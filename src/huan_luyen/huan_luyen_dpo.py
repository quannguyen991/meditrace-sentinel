# -*- coding: utf-8 -*-
"""[Huấn luyện mô hình › Huấn luyện]
Làm gì   : Tinh chỉnh adapter trích v3 bằng DPO trên các cặp đầu ra đúng và sai khó (thử
           nghiệm, chưa dùng trong hệ thống).
Vào → Ra : cặp lỗi khó jsonl + adapter v3 → log-prob tham chiếu, adapter DPO, độ chính xác
           chọn đúng bản
Đọc từ   : loss_dpo() là hàm loss; pha_train() huấn luyện từng cặp; main() chọn pha ref,
           train, đánh giá
Mục lục (các hàm/lớp chính):
  main()          Điểm vào: chạy pha ref, train hoặc đánh giá
  pha_ref()       Pha tính log-prob tham chiếu của adapter v3
  pha_train()     Pha huấn luyện DPO từng cặp
  pha_danh_gia()  Pha đo độ chính xác chọn đúng bản
  loss_dpo()      Tính loss DPO có thêm NLL trên bản đúng
  nap_cap()       Nạp cặp DPO và dựng mẫu token
  chon_cap()      Chọn cặp chia đều theo loại lỗi
  logp_lo()       Tính log-prob cả lô trong một lượt qua mô hình
Gọi tới  : bo_du_lieu/nap_du_lieu, he_thong/duong_dan, huan_luyen/huan_luyen_sft,
           huan_luyen/loss_theo_doan
Tên cũ   : train_dpo.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Huấn luyện DPO trên CẶP LỖI KHÓ, bắt đầu từ adapter trích v3.

Dữ liệu: `data/cay_loi/cap_loi_kho_train.jsonl` (sinh bằng `python -m tools.cay_loi_kho`).
Mỗi cặp = (đầu ra đúng, đầu ra bị cấy MỘT lỗi khó: đổi bên, đổi mức độ, quá khứ/hiện
tại, đính chính ngược...). Hai chuỗi giống nhau gần hết, nên tín hiệu DPO dồn vào
đúng mấy token khác nhau — chính chỗ SFT không dạy được vì SFT chỉ thấy bản đúng.

Loss = -log sigmoid(beta * [(lp_tot - ref_tot) - (lp_xau - ref_xau)]) + alpha * NLL_tot
  - mô hình tham chiếu = v3 (không phải mô hình gốc): ref log-prob TÍNH TRƯỚC một lần
    (`--pha ref`), ghi ra tệp, chạy tiếp được nếu đứt giữa chừng.
  - NLL trên bản đúng (kiểu RPO) giữ mô hình không trôi khỏi định dạng JSON.

Ba pha, chạy lần lượt trên HoaiDuc (qua `tools/run_capped.py --phan-vram 0.70`):
    python -m src.huan_luyen.huan_luyen_dpo --pha ref
    python -m src.huan_luyen.huan_luyen_dpo --pha train
    python -m src.huan_luyen.huan_luyen_dpo --pha danh-gia --adapter <thư mục>   # đo chính xác chọn cặp

Phần không cần torch (chọn cặp, dựng mặt nạ) chạy được trên laptop để test trước.
"""
import argparse
import io
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

from src.he_thong import duong_dan as duong_dan
from src.huan_luyen.huan_luyen_sft import dung_chuoi

BETA = 0.1
ALPHA = 1.0
TEP_CAP_TRAIN = "cay_loi/cap_loi_kho_train.jsonl"
TEP_CAP_VAL = "cay_loi/cap_loi_kho_val.jsonl"
TEP_NHAC_TRAIN = "trich_train_v2.jsonl"
TEP_NHAC_VAL = "trich_giu_lai_v2.jsonl"


# ═══ gan_bang() — So hai số có chấp nhận sai số bf16 ══════════════════════════════════
# Dùng so lô ghép với tính tuần tự.
def gan_bang(a: float, b: float) -> bool:
    """Sai số bf16 giữa lô và lần lượt: đo 26/11 thấy chênh 0,4% (-23,77 vs -23,68)."""
    return abs(a - b) <= max(0.5, 0.02 * abs(b))


# ═══ bam_mau() — Băm token của cả hai chuỗi trong cặp ═════════════════════════════════
# Để biết cặp đã bị sinh lại thì ref cũ không còn đúng.
def bam_mau(m: dict) -> str:
    """Băm token id của cả hai chuỗi — ref lưu kèm để biết cặp có bị sinh lại không."""
    import hashlib
    h = hashlib.sha256()
    for ids, _ in (m["tot"], m["xau"]):
        h.update((",".join(map(str, ids)) + ";").encode())
    return h.hexdigest()[:16]


# ═══ loai_cap() — Lấy loại lỗi chính của một cặp ══════════════════════════════════════
# Là lỗi đầu tiên trong cặp.
def loai_cap(cap: dict) -> str:
    """Loại lỗi chính của cặp (lỗi đầu tiên)."""
    return cap["loi"][0]["loai"]


# ═══ chon_cap() — Chọn cặp chia đều theo loại lỗi ═════════════════════════════════════
# Xoay vòng các loại, tất định theo seed; tránh loại hiếm bị bỏ.
def chon_cap(ds: list, so_cap: int, seed: int = 42) -> list:
    """Chọn `so_cap` cặp CHIA ĐỀU theo loại lỗi (vòng tròn qua các loại), tất định.

    Tập gốc lệch: so_lech_nho nhiều gấp chục lần dinh_chinh_nguoc. Lấy ngẫu nhiên
    thì loại hiếm gần như không vào tập train."""
    theo = defaultdict(list)
    for c in ds:
        theo[loai_cap(c)].append(c)
    rng = random.Random(seed)
    hang = []
    for l in sorted(theo):
        rng.shuffle(theo[l])
        hang.append(theo[l])
    ra, i = [], 0
    while len(ra) < so_cap and any(hang):
        h = hang[i % len(hang)]
        if h:
            ra.append(h.pop())
        i += 1
    rng.shuffle(ra)
    return ra


# ═══ dung_mau() — Dựng token và nhãn cho một chuỗi ════════════════════════════════════
# Nhãn -100 trên phần lời nhắc; quá độ dài thì trả None.
def dung_mau(tok, nhac: str, tra_loi: str, do_dai: int):
    """-> (input_ids, labels) với labels = -100 trên phần nhắc; None nếu quá `do_dai`."""
    chuoi_nhac = dung_chuoi(tok, nhac, nhiem_vu="trich")
    chuoi_du = dung_chuoi(tok, nhac, tra_loi, "trich") + tok.eos_token
    id_nhac = tok.encode(chuoi_nhac, add_special_tokens=False)
    id_du = tok.encode(chuoi_du, add_special_tokens=False)
    if len(id_du) > do_dai:
        return None
    if id_du[:len(id_nhac)] != id_nhac:
        raise ValueError("chuoi nhac khong phai tien to cua chuoi day du — mat na se lech")
    return id_du, [-100] * len(id_nhac) + id_du[len(id_nhac):]


# ═══ nap_cap() — Nạp cặp DPO và dựng mẫu token ════════════════════════════════════════
# Trả danh sách mẫu và số cặp bị loại vì quá dài.
def nap_cap(tep_cap: Path, tep_nhac: Path, tok, do_dai: int, so_cap: int, seed: int = 42):
    """-> (danh sách mẫu, số bị loại). Mẫu = {khoa, loai, tot: (ids, nhan), xau: (ids, nhan)}."""
    nhac = {}
    for l in tep_nhac.read_text(encoding="utf-8").splitlines():
        if l.strip():
            m = json.loads(l)
            nhac[m["id"]] = m["input"]
    ds = [json.loads(l) for l in tep_cap.read_text(encoding="utf-8").splitlines() if l.strip()]
    ds = [c for c in ds if c["id"] in nhac]
    mau, loai_bo = [], 0
    # lấy dự phòng gấp đôi để còn đủ sau khi loại mẫu quá dài
    for c in chon_cap(ds, so_cap * 2, seed):
        if len(mau) >= so_cap:
            break
        tot = dung_mau(tok, nhac[c["id"]], c["chosen"], do_dai)
        xau = dung_mau(tok, nhac[c["id"]], c["rejected"], do_dai)
        if tot is None or xau is None:
            loai_bo += 1
            continue
        mau.append({"khoa": f"{c['id']}#{c.get('bien_the', 0)}", "loai": loai_cap(c),
                    "tot": tot, "xau": xau})
    return mau, loai_bo


# ═══ loss_dpo() — Tính loss DPO có thêm NLL trên bản đúng ═════════════════════════════
# Trả loss và phần thưởng ngầm định chênh lệch để ghi nhật ký.
def loss_dpo(lp_tot, lp_xau, ref_tot, ref_xau, nll_tot, beta=BETA, alpha=ALPHA):
    """-> (loss, le) — `le` = phần thưởng ngầm định chênh lệch (để ghi nhật ký)."""
    import torch.nn.functional as F
    le = beta * ((lp_tot - ref_tot) - (lp_xau - ref_xau))
    return -F.logsigmoid(le) + alpha * nll_tot, le


# ═══ he_so_dpo() — Tính hệ số đạo hàm của loss theo log-prob ══════════════════════════
# Cho phép lan truyền ngược từng chuỗi một để tiết kiệm bộ nhớ.
def he_so_dpo(z: float, beta: float, alpha: float, n_tot: int):
    """dL/dlp_tot và dL/dlp_xau của L = -log sigmoid(z) + alpha * (-lp_tot / n_tot),
    z = beta * ((lp_tot - ref_tot) - (lp_xau - ref_xau)).

    Dùng để lan truyền ngược TỪNG CHUỖI MỘT (mỗi lúc chỉ giữ một đồ thị): backward
    `he_tot * lp_tot` rồi `he_xau * lp_xau` cho cùng gradient như backward L."""
    s = 1.0 / (1.0 + math.exp(z)) if z > -50 else 1.0  # sigmoid(-z)
    return -beta * s - alpha / max(n_tot, 1), beta * s


# ═══ logp_chuoi() — Tính tổng log-prob các token có nhãn của một chuỗi ════════════════
# Tính theo đoạn nên không tạo logits cả chuỗi.
def logp_chuoi(model, ids, nhan, kich_thuoc_doan=512):
    """-> (tổng log-prob của các token có nhãn, số token). Không tạo logits cả chuỗi."""
    import torch
    from src.huan_luyen.loss_theo_doan import bo_mat_na_day_du, cross_entropy_theo_doan
    dev = next(model.parameters()).device
    x = torch.tensor([ids], device=dev)
    y = torch.tensor([nhan], device=dev)
    goc = model.base_model.model
    hidden = goc.model(input_ids=x, attention_mask=bo_mat_na_day_du(torch.ones_like(x))).last_hidden_state
    n = int((y[:, 1:] != -100).sum().item())
    ce = cross_entropy_theo_doan(hidden[:, :-1], goc.lm_head, y[:, 1:], kich_thuoc_doan)
    return -ce * n, n


# ═══ ghep_lo() — Ghép nhiều chuỗi thành lô có đệm phải ════════════════════════════════
# Nhãn đệm là -100; thuần Python để test không cần torch.
def ghep_lo(cac_mau, ma_dem):
    """[(ids, nhan), ...] -> (ids [B,T], nhan [B,T], mat_na [B,T]) đệm PHẢI; nhãn đệm = -100.
    Thuần Python (danh sách), để test không cần torch."""
    T = max(len(i) for i, _ in cac_mau)
    ids = [list(i) + [ma_dem] * (T - len(i)) for i, _ in cac_mau]
    nhan = [list(n) + [-100] * (T - len(n)) for _, n in cac_mau]
    mat = [[1] * len(i) + [0] * (T - len(i)) for i, _ in cac_mau]
    return ids, nhan, mat


# ─── _logp_doan() — Tính log-prob cho một đoạn ẩn ─────────────────────────────────────
# Dùng lm_head trên đoạn rồi lấy log-prob nhãn.
def _logp_doan(h, lm_head, y):
    import torch.nn.functional as F
    logits = lm_head(h).float()
    ce = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1),
                         ignore_index=-100, reduction="none").view(y.shape)
    return -ce.sum(dim=1)


# ═══ logp_lo() — Tính log-prob cả lô trong một lượt qua mô hình ═══════════════════════
# Nhanh hơn hai lượt riêng, kết quả bằng logp_chuoi.
def logp_lo(model, cac_mau, ma_dem, kich_thuoc_doan=512):
    """MỘT lượt qua mô hình cho cả lô (bản đúng + bản sai) -> (logp [B], số token [B]).
    Nhanh hơn hai lượt riêng vì GPU chạy đầy hơn; kết quả bằng `logp_chuoi` từng chuỗi."""
    import torch
    from torch.utils.checkpoint import checkpoint
    from src.huan_luyen.loss_theo_doan import bo_mat_na_day_du
    dev = next(model.parameters()).device
    ids, nhan, mat = (torch.tensor(x, device=dev) for x in ghep_lo(cac_mau, ma_dem))
    goc = model.base_model.model
    hidden = goc.model(input_ids=ids, attention_mask=bo_mat_na_day_du(mat)).last_hidden_state
    h, y = hidden[:, :-1], nhan[:, 1:]
    tong = hidden.new_zeros(ids.size(0), dtype=torch.float32)
    for i in range(0, h.size(1), kich_thuoc_doan):
        yy = y[:, i:i + kich_thuoc_doan]
        if not bool((yy != -100).any()):
            continue
        hh = h[:, i:i + kich_thuoc_doan]
        if hh.requires_grad:
            tong = tong + checkpoint(_logp_doan, hh, goc.lm_head, yy, use_reentrant=False)
        else:
            tong = tong + _logp_doan(hh, goc.lm_head, yy)
    return tong, (y != -100).sum(dim=1)


# ═══ do_dai_cap() — Đo độ dài của một cặp ═════════════════════════════════════════════
def do_dai_cap(m) -> int:
    return max(len(m["tot"][0]), len(m["xau"][0]))


# ═══ nen_ghep() — Quyết định có ghép lô cho cặp này không ═════════════════════════════
# Chỉ ghép khi cặp ngắn hơn ngưỡng.
def nen_ghep(ghep, m) -> bool:
    """`ghep` = None (tắt) hoặc {"nguong": số token}: chỉ ghép khi cặp ngắn hơn ngưỡng."""
    return ghep is not None and do_dai_cap(m) <= ghep["nguong"]


# ═══ ha_nguong() — Hạ ngưỡng ghép sau khi cặp tràn bộ nhớ ═════════════════════════════
# Cặp dài bằng nó trở lên sẽ chạy tuần tự ngay từ đầu.
def ha_nguong(ghep, m):
    """Cặp này tràn bộ nhớ -> mọi cặp dài bằng nó trở lên sẽ chạy lần lượt ngay từ đầu
    (chạy thử 26/11: 60% cặp tràn ở trần 0,70, mỗi lần tràn phí một lượt chạy)."""
    ghep["nguong"] = min(ghep["nguong"], do_dai_cap(m) - 1)


# ─── _logp_cap() — Tính log-prob bản đúng và bản sai của một cặp ──────────────────────
# Ghép lô nếu đủ ngắn; tràn bộ nhớ thì hạ ngưỡng và chạy tuần tự.
def _logp_cap(model, m, ma_dem, ghep):
    """-> (lp_tot, lp_xau, n_tot). Ghép lô nếu cặp đủ ngắn; tràn bộ nhớ thì hạ ngưỡng
    và chạy lần lượt."""
    import torch
    if nen_ghep(ghep, m):
        tran = False
        try:
            lp, n = logp_lo(model, [m["tot"], m["xau"]], ma_dem)
            return lp[0], lp[1], int(n[0].item())
        except torch.cuda.OutOfMemoryError:
            tran = True
        # chạy lại NGOÀI khối except: trong khối, traceback còn giữ tensor của lần hỏng
        if tran:
            torch.cuda.empty_cache()
            ha_nguong(ghep, m)
            print(f"[tran bo nho] {m['khoa']} - chay lan luot, nguong ghep {ghep['nguong']}", flush=True)
    lt, nt = logp_chuoi(model, *m["tot"])
    lx, _ = logp_chuoi(model, *m["xau"])
    return lt, lx, nt


# ─── _nap_mo_hinh() — Nạp mô hình gốc 4-bit kèm adapter v3 ────────────────────────────
# Chế độ huấn luyện bật checkpoint và tắt dropout; chế độ đánh giá dùng eval.
def _nap_mo_hinh(model_goc, adapter, huan_luyen):
    import torch
    from peft import PeftModel, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, BitsAndBytesConfig
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True,
                             bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
    m = AutoModelForCausalLM.from_pretrained(model_goc, quantization_config=bnb, device_map="auto")
    if huan_luyen:
        m = prepare_model_for_kbit_training(m)
    m = PeftModel.from_pretrained(m, str(adapter), is_trainable=huan_luyen)
    if huan_luyen:
        m.gradient_checkpointing_enable()
        m.enable_input_require_grads()
        # Tắt dropout (LoRA dropout 0,05 của adapter v3): ref tính ở chế độ eval, và
        # lượt `lx0` (tính z) với lượt `lx` (lan truyền ngược) phải là CÙNG một hàm —
        # để dropout thì z lúc đầu khác 0 và hệ số lệch nhẹ (review 26/11).
        import torch.nn as nn
        for mod in m.modules():
            if isinstance(mod, nn.Dropout):
                mod.p = 0.0
    else:
        m.eval()
    return m


# ─── _doc_jsonl() — Đọc tệp JSONL thành từ điển theo khoá ─────────────────────────────
def _doc_jsonl(p: Path) -> dict:
    ra = {}
    if p.exists():
        for l in p.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                ra[r["khoa"]] = r
    return ra


# ═══ pha_ref() — Pha tính log-prob tham chiếu của adapter v3 ══════════════════════════
# Ghi nối tiếp ra tệp, bỏ qua cặp đã có nên chạy tiếp được.
def pha_ref(a, tok, mau):
    """Log-prob của v3 trên từng cặp; ghi nối tiếp, bỏ qua khoá đã có."""
    import torch
    da = _doc_jsonl(a.tep_ref)
    can = [m for m in mau if m["khoa"] not in da]
    print(f"[ref] {len(da)} da co, con {len(can)}", flush=True)
    if not can:
        return
    model = _nap_mo_hinh(a.model, a.adapter_goc, huan_luyen=False)
    with open(a.tep_ref, "a", encoding="utf-8") as f, torch.no_grad():
        for i, m in enumerate(can, 1):
            lt, lx, nt = _logp_cap(model, m, tok.pad_token_id, a.ghep)
            if i == 1 and nen_ghep(a.ghep, m):
                # tự kiểm: lô 2 chuỗi phải cho cùng log-prob với chạy lần lượt
                st, _ = logp_chuoi(model, *m["tot"])
                sx, _ = logp_chuoi(model, *m["xau"])
                print(f"[kiem ghep lo] tot {lt.item():.3f} vs {st.item():.3f}, "
                      f"xau {lx.item():.3f} vs {sx.item():.3f}", flush=True)
                if not (gan_bang(lt.item(), st.item()) and gan_bang(lx.item(), sx.item())):
                    raise SystemExit("Ghep lo cho log-prob khac chay lan luot — dung, chay lai voi --khong-ghep-lo.")
            f.write(json.dumps({"khoa": m["khoa"], "tot": lt.item(), "xau": lx.item(),
                                "n_tot": nt, "bam": bam_mau(m)}) + "\n")
            f.flush()
            if i % 25 == 0:
                print(f"[ref] {i}/{len(can)}", flush=True)


# ═══ pha_train() — Pha huấn luyện DPO từng cặp ════════════════════════════════════════
# Kiểm ref đủ và khớp, tối ưu 8-bit, tích luỹ gradient, ghi nhật ký và lưu adapter.
def pha_train(a, tok, mau):
    import torch
    ref = _doc_jsonl(a.tep_ref)
    if a.chi_cap_co_ref:
        # rút gọn khi gặp hạn (26/11): chỉ train trên các cặp ĐÃ tính ref, giữ thứ tự đã trộn
        mau = [m for m in mau if m["khoa"] in ref]
        print(f"[train] chi cap co ref: {len(mau)} cap", flush=True)
    thieu = [m["khoa"] for m in mau if m["khoa"] not in ref]
    if thieu:
        raise SystemExit(f"Thieu ref cho {len(thieu)} cap — chay --pha ref truoc.")
    lech = [m["khoa"] for m in mau if ref[m["khoa"]].get("bam", bam_mau(m)) != bam_mau(m)]
    if lech:
        raise SystemExit(f"Ref cua {len(lech)} cap tinh tren token KHAC (cap da sinh lai?) — "
                         f"xoa ref_logp.jsonl va chay lai --pha ref. Vi du: {lech[:3]}")
    model = _nap_mo_hinh(a.model, a.adapter_goc, huan_luyen=True)
    model.print_trainable_parameters()
    import bitsandbytes as bnb
    tham_so = [p for p in model.parameters() if p.requires_grad]
    opt = bnb.optim.PagedAdamW8bit(tham_so, lr=a.lr, weight_decay=0.0)
    so_buoc = (len(mau) + a.tich_luy - 1) // a.tich_luy
    khoi = max(1, so_buoc // 20)

    def lr_tai(b):  # khởi động tuyến tính rồi giảm tuyến tính về 0
        return a.lr * (b + 1) / khoi if b < khoi else a.lr * max(0.0, (so_buoc - b) / (so_buoc - khoi))

    a.thu_muc_ra.mkdir(parents=True, exist_ok=True)
    nk = open(a.thu_muc_ra / "nhat_ky.jsonl", "a", encoding="utf-8")
    model.train()
    buoc, tong = 0, defaultdict(float)
    import time
    t0 = time.time()

    def mot_cap(m):
        """Mỗi lúc chỉ giữ MỘT đồ thị (giữ cả hai thì tràn bộ nhớ ở 0,70 — chạy thử 26/11).
        1) bản đúng có gradient; 2) bản sai không gradient -> z; 3) backward bản đúng
        theo hệ số; 4) bản sai có gradient, backward theo hệ số. Gradient bằng backward L."""
        r = ref[m["khoa"]]
        lt, nt = logp_chuoi(model, *m["tot"])
        with torch.no_grad():
            lx0, _ = logp_chuoi(model, *m["xau"])
        z = a.beta * ((lt.item() - r["tot"]) - (lx0.item() - r["xau"]))
        he_tot, he_xau = he_so_dpo(z, a.beta, a.alpha, nt)
        loss = -math.log(max(1e-12, 1.0 / (1.0 + math.exp(-z)))) + a.alpha * (-lt.item() / max(nt, 1))
        (he_tot * lt / a.tich_luy).backward()
        del lt
        lx, _ = logp_chuoi(model, *m["xau"])
        (he_xau * lx / a.tich_luy).backward()
        return loss, z

    for i, m in enumerate(mau):
        loss, le = mot_cap(m)
        tong["loss"] += loss
        tong["le"] += le
        tong["dung"] += float(le > 0)
        tong["n"] += 1
        if (i + 1) % a.tich_luy == 0 or i + 1 == len(mau):
            for g in opt.param_groups:
                g["lr"] = lr_tai(buoc)
            torch.nn.utils.clip_grad_norm_(tham_so, 1.0)
            opt.step()
            opt.zero_grad(set_to_none=True)
            buoc += 1
            if buoc % 5 == 0 or i + 1 == len(mau):
                n = tong["n"]
                dong = {"buoc": buoc, "tren": so_buoc, "cap": i + 1, "loss": tong["loss"] / n,
                        "le_tb": tong["le"] / n, "ti_le_dung": tong["dung"] / n, "lr": lr_tai(buoc - 1),
                        "giay_moi_cap": round((time.time() - t0) / (i + 1), 1)}
                print(json.dumps(dong), flush=True)
                nk.write(json.dumps(dong) + "\n")
                nk.flush()
                tong = defaultdict(float)
            if buoc % a.luu_moi == 0:
                model.save_pretrained(str(a.thu_muc_ra / f"buoc-{buoc}"))
    dich = a.thu_muc_ra / "best_checkpoint"
    model.save_pretrained(str(dich))
    tok.save_pretrained(str(dich))
    print(f"Xong. Adapter: {dich}", flush=True)


# ═══ pha_danh_gia() — Pha đo độ chính xác chọn đúng bản ═══════════════════════════════
# Tỉ lệ cặp mà log-prob bản đúng cao hơn bản bị cấy lỗi, theo loại lỗi.
def pha_danh_gia(a, tok, mau):
    """Tỉ lệ cặp mà mô hình cho bản ĐÚNG log-prob cao hơn bản bị cấy lỗi, theo loại."""
    import torch
    model = _nap_mo_hinh(a.model, a.adapter, huan_luyen=False)
    theo = defaultdict(lambda: [0, 0])
    chenh = defaultdict(list)   # lp_tot - lp_xau: v3 đã đúng 280/280 (26/11) -> tỉ lệ đúng
    tung_cap = []               # kịch trần, so sánh bằng độ CHÊNH và log-prob bản đúng
    with torch.no_grad():
        for i, m in enumerate(mau, 1):
            lt, lx, _ = _logp_cap(model, m, tok.pad_token_id, a.ghep)
            theo[m["loai"]][0] += int(lt.item() > lx.item())
            theo[m["loai"]][1] += 1
            chenh[m["loai"]].append(lt.item() - lx.item())
            tung_cap.append({"khoa": m["khoa"], "loai": m["loai"], "tot": lt.item(), "xau": lx.item()})
            if i % 25 == 0:
                print(f"[danh-gia] {i}/{len(mau)}", flush=True)
    dung = sum(v[0] for v in theo.values())
    tat_ca = [x for v in chenh.values() for x in v]
    ket = {"adapter": str(a.adapter), "so_cap": len(mau), "ti_le_dung": dung / max(len(mau), 1),
           "chenh_tb": sum(tat_ca) / max(len(tat_ca), 1),
           "logp_tot_tb": sum(x["tot"] for x in tung_cap) / max(len(tung_cap), 1),
           "theo_loai": {k: {"dung": v[0], "tong": v[1],
                             "chenh_tb": sum(chenh[k]) / len(chenh[k])} for k, v in sorted(theo.items())},
           "tung_cap": tung_cap}
    print(json.dumps(ket, ensure_ascii=False, indent=1), flush=True)
    a.tep_ket_qua.parent.mkdir(parents=True, exist_ok=True)
    a.tep_ket_qua.write_text(json.dumps(ket, ensure_ascii=False, indent=1), encoding="utf-8")


# ═══ main() — Điểm vào: chạy pha ref, train hoặc đánh giá ═════════════════════════════
# Đọc tham số, nạp cặp và gọi pha tương ứng.
def main(argv=None):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--pha", choices=["ref", "train", "danh-gia"], required=True)
    ap.add_argument("--model", default=duong_dan.MODEL_CHINH)
    ap.add_argument("--adapter-goc", type=Path,
                    default=duong_dan.THU_MUC_MO_HINH / "nen-qwen3-4b-trich-v3" / "best_checkpoint")
    ap.add_argument("--adapter", type=Path, default=None, help="adapter can danh gia")
    ap.add_argument("--thu-muc-ra", type=Path,
                    default=duong_dan.THU_MUC_MO_HINH / "nen-qwen3-4b-trich-v3-dpo")
    ap.add_argument("--so-cap", type=int, default=1200)
    ap.add_argument("--so-cap-val", type=int, default=280)
    ap.add_argument("--do-dai", type=int, default=4096)
    ap.add_argument("--tich-luy", type=int, default=8)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--beta", type=float, default=BETA)
    ap.add_argument("--alpha", type=float, default=ALPHA)
    ap.add_argument("--luu-moi", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--tep-ket-qua", type=Path, default=None)
    ap.add_argument("--chi-cap-co-ref", action="store_true",
                    help="train chi tren cac cap da co trong ref_logp.jsonl")
    ap.add_argument("--khong-ghep-lo", dest="ghep_lo", action="store_false",
                    help="chay ban dung va ban sai lan luot thay vi mot lo 2 chuoi")
    a = ap.parse_args(argv)
    a.tep_ref = a.thu_muc_ra / "ref_logp.jsonl"
    a.ghep = {"nguong": a.do_dai} if a.ghep_lo else None

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.model)
    tok.pad_token = tok.eos_token
    d = duong_dan.THU_MUC_DU_LIEU
    from src.bo_du_lieu import nap_du_lieu as _dl
    _dl.chan_du_lieu_gpt([TEP_NHAC_TRAIN, TEP_NHAC_VAL])

    if a.pha == "danh-gia":
        a.adapter = a.adapter or a.adapter_goc
        a.tep_ket_qua = a.tep_ket_qua or (a.thu_muc_ra / f"danh_gia_{a.adapter.parent.name}_{a.adapter.name}.json")
        mau, bo = nap_cap(d / TEP_CAP_VAL, d / TEP_NHAC_VAL, tok, a.do_dai, a.so_cap_val, a.seed)
        print(f"val {len(mau)} cap (loai {bo} qua {a.do_dai} token)", flush=True)
        return pha_danh_gia(a, tok, mau)
    mau, bo = nap_cap(d / TEP_CAP_TRAIN, d / TEP_NHAC_TRAIN, tok, a.do_dai, a.so_cap, a.seed)
    print(f"train {len(mau)} cap (loai {bo} qua {a.do_dai} token)", flush=True)
    a.thu_muc_ra.mkdir(parents=True, exist_ok=True)
    if a.pha == "ref":
        return pha_ref(a, tok, mau)
    return pha_train(a, tok, mau)


if __name__ == "__main__":
    main()
