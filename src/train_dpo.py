# -*- coding: utf-8 -*-
"""Huan luyen DPO tren CAP LOI KHO, bat dau tu adapter trich v3.

Du lieu: `data/cay_loi/cap_loi_kho_train.jsonl` (sinh bang `python -m tools.cay_loi_kho`).
Moi cap = (dau ra dung, dau ra bi cay MOT loi kho: doi ben, doi muc do, qua khu/hien
tai, dinh chinh nguoc...). Hai chuoi giong nhau gan het, nen tin hieu DPO don vao
dung may token khac nhau — chinh cho SFT khong day duoc vi SFT chi thay ban dung.

Loss = -log sigmoid(beta * [(lp_tot - ref_tot) - (lp_xau - ref_xau)]) + alpha * NLL_tot
  - mo hinh tham chieu = v3 (khong phai mo hinh goc): ref log-prob TINH TRUOC mot lan
    (`--pha ref`), ghi ra tep, chay tiep duoc neu dut giua chung.
  - NLL tren ban dung (kieu RPO) giu mo hinh khong troi khoi dinh dang JSON.

Ba pha, chay lan luot tren HoaiDuc (qua `tools/run_capped.py --phan-vram 0.70`):
    python -m src.train_dpo --pha ref
    python -m src.train_dpo --pha train
    python -m src.train_dpo --pha danh-gia --adapter <thu muc>   # do chinh xac chon cap

Phan khong can torch (chon cap, dung mat na) chay duoc tren laptop de test truoc.
"""
import argparse
import io
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

from src import duong_dan
from src.train_baseline import dung_chuoi

BETA = 0.1
ALPHA = 1.0
TEP_CAP_TRAIN = "cay_loi/cap_loi_kho_train.jsonl"
TEP_CAP_VAL = "cay_loi/cap_loi_kho_val.jsonl"
TEP_NHAC_TRAIN = "trich_train_v2.jsonl"
TEP_NHAC_VAL = "trich_giu_lai_v2.jsonl"


def loai_cap(cap: dict) -> str:
    """Loai loi chinh cua cap (loi dau tien)."""
    return cap["loi"][0]["loai"]


def chon_cap(ds: list, so_cap: int, seed: int = 42) -> list:
    """Chon `so_cap` cap CHIA DEU theo loai loi (vong tron qua cac loai), tat dinh.

    Tap goc lech: so_lech_nho nhieu gap chuc lan dinh_chinh_nguoc. Lay ngau nhien
    thi loai hiem gan nhu khong vao tap train."""
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


def dung_mau(tok, nhac: str, tra_loi: str, do_dai: int):
    """-> (input_ids, labels) voi labels = -100 tren phan nhac; None neu qua `do_dai`."""
    chuoi_nhac = dung_chuoi(tok, nhac, nhiem_vu="trich")
    chuoi_du = dung_chuoi(tok, nhac, tra_loi, "trich") + tok.eos_token
    id_nhac = tok.encode(chuoi_nhac, add_special_tokens=False)
    id_du = tok.encode(chuoi_du, add_special_tokens=False)
    if len(id_du) > do_dai:
        return None
    if id_du[:len(id_nhac)] != id_nhac:
        raise ValueError("chuoi nhac khong phai tien to cua chuoi day du — mat na se lech")
    return id_du, [-100] * len(id_nhac) + id_du[len(id_nhac):]


def nap_cap(tep_cap: Path, tep_nhac: Path, tok, do_dai: int, so_cap: int, seed: int = 42):
    """-> (danh sach mau, so bi loai). Mau = {khoa, loai, tot: (ids, nhan), xau: (ids, nhan)}."""
    nhac = {}
    for l in tep_nhac.read_text(encoding="utf-8").splitlines():
        if l.strip():
            m = json.loads(l)
            nhac[m["id"]] = m["input"]
    ds = [json.loads(l) for l in tep_cap.read_text(encoding="utf-8").splitlines() if l.strip()]
    ds = [c for c in ds if c["id"] in nhac]
    mau, loai_bo = [], 0
    # lay du phong gap doi de con du sau khi loai mau qua dai
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


def loss_dpo(lp_tot, lp_xau, ref_tot, ref_xau, nll_tot, beta=BETA, alpha=ALPHA):
    """-> (loss, le) — `le` = phan thuong ngam dinh chenh lech (de ghi nhat ky)."""
    import torch.nn.functional as F
    le = beta * ((lp_tot - ref_tot) - (lp_xau - ref_xau))
    return -F.logsigmoid(le) + alpha * nll_tot, le


def he_so_dpo(z: float, beta: float, alpha: float, n_tot: int):
    """dL/dlp_tot va dL/dlp_xau cua L = -log sigmoid(z) + alpha * (-lp_tot / n_tot),
    z = beta * ((lp_tot - ref_tot) - (lp_xau - ref_xau)).

    Dung de lan truyen nguoc TUNG CHUOI MOT (moi luc chi giu mot do thi): backward
    `he_tot * lp_tot` roi `he_xau * lp_xau` cho cung gradient nhu backward L."""
    s = 1.0 / (1.0 + math.exp(z)) if z > -50 else 1.0  # sigmoid(-z)
    return -beta * s - alpha / max(n_tot, 1), beta * s


def logp_chuoi(model, ids, nhan, kich_thuoc_doan=512):
    """-> (tong log-prob cua cac token co nhan, so token). Khong tao logits ca chuoi."""
    import torch
    from src.loss_theo_doan import bo_mat_na_day_du, cross_entropy_theo_doan
    dev = next(model.parameters()).device
    x = torch.tensor([ids], device=dev)
    y = torch.tensor([nhan], device=dev)
    goc = model.base_model.model
    hidden = goc.model(input_ids=x, attention_mask=bo_mat_na_day_du(torch.ones_like(x))).last_hidden_state
    n = int((y[:, 1:] != -100).sum().item())
    ce = cross_entropy_theo_doan(hidden[:, :-1], goc.lm_head, y[:, 1:], kich_thuoc_doan)
    return -ce * n, n


def ghep_lo(cac_mau, ma_dem):
    """[(ids, nhan), ...] -> (ids [B,T], nhan [B,T], mat_na [B,T]) dem PHAI; nhan dem = -100.
    Thuan Python (danh sach), de test khong can torch."""
    T = max(len(i) for i, _ in cac_mau)
    ids = [list(i) + [ma_dem] * (T - len(i)) for i, _ in cac_mau]
    nhan = [list(n) + [-100] * (T - len(n)) for _, n in cac_mau]
    mat = [[1] * len(i) + [0] * (T - len(i)) for i, _ in cac_mau]
    return ids, nhan, mat


def _logp_doan(h, lm_head, y):
    import torch.nn.functional as F
    logits = lm_head(h).float()
    ce = F.cross_entropy(logits.reshape(-1, logits.size(-1)), y.reshape(-1),
                         ignore_index=-100, reduction="none").view(y.shape)
    return -ce.sum(dim=1)


def logp_lo(model, cac_mau, ma_dem, kich_thuoc_doan=512):
    """MOT luot qua mo hinh cho ca lo (ban dung + ban sai) -> (logp [B], so token [B]).
    Nhanh hon hai luot rieng vi GPU chay day hon; ket qua bang `logp_chuoi` tung chuoi."""
    import torch
    from torch.utils.checkpoint import checkpoint
    from src.loss_theo_doan import bo_mat_na_day_du
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


def _logp_cap(model, m, ma_dem, ghep):
    """-> (lp_tot, lp_xau, n_tot). Ghep lo neu duoc; tran bo nho thi chay lan luot."""
    import torch
    if ghep:
        tran = False
        try:
            lp, n = logp_lo(model, [m["tot"], m["xau"]], ma_dem)
            return lp[0], lp[1], int(n[0].item())
        except torch.cuda.OutOfMemoryError:
            tran = True
        # chay lai NGOAI khoi except: trong khoi, traceback con giu tensor cua lan hong
        if tran:
            torch.cuda.empty_cache()
            print(f"[tran bo nho] {m['khoa']} - chay lan luot", flush=True)
    lt, nt = logp_chuoi(model, *m["tot"])
    lx, _ = logp_chuoi(model, *m["xau"])
    return lt, lx, nt


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
    else:
        m.eval()
    return m


def _doc_jsonl(p: Path) -> dict:
    ra = {}
    if p.exists():
        for l in p.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                ra[r["khoa"]] = r
    return ra


def pha_ref(a, tok, mau):
    """Log-prob cua v3 tren tung cap; ghi noi tiep, bo qua khoa da co."""
    import torch
    da = _doc_jsonl(a.tep_ref)
    can = [m for m in mau if m["khoa"] not in da]
    print(f"[ref] {len(da)} da co, con {len(can)}", flush=True)
    if not can:
        return
    model = _nap_mo_hinh(a.model, a.adapter_goc, huan_luyen=False)
    with open(a.tep_ref, "a", encoding="utf-8") as f, torch.no_grad():
        for i, m in enumerate(can, 1):
            lt, lx, nt = _logp_cap(model, m, tok.pad_token_id, a.ghep_lo)
            if i == 1 and a.ghep_lo:
                # tu kiem: lo 2 chuoi phai cho cung log-prob voi chay lan luot
                st, _ = logp_chuoi(model, *m["tot"])
                sx, _ = logp_chuoi(model, *m["xau"])
                print(f"[kiem ghep lo] tot {lt.item():.3f} vs {st.item():.3f}, "
                      f"xau {lx.item():.3f} vs {sx.item():.3f}", flush=True)
            f.write(json.dumps({"khoa": m["khoa"], "tot": lt.item(), "xau": lx.item(),
                                "n_tot": nt}) + "\n")
            f.flush()
            if i % 25 == 0:
                print(f"[ref] {i}/{len(can)}", flush=True)


def pha_train(a, tok, mau):
    import torch
    ref = _doc_jsonl(a.tep_ref)
    thieu = [m["khoa"] for m in mau if m["khoa"] not in ref]
    if thieu:
        raise SystemExit(f"Thieu ref cho {len(thieu)} cap — chay --pha ref truoc.")
    model = _nap_mo_hinh(a.model, a.adapter_goc, huan_luyen=True)
    model.print_trainable_parameters()
    import bitsandbytes as bnb
    tham_so = [p for p in model.parameters() if p.requires_grad]
    opt = bnb.optim.PagedAdamW8bit(tham_so, lr=a.lr, weight_decay=0.0)
    so_buoc = (len(mau) + a.tich_luy - 1) // a.tich_luy
    khoi = max(1, so_buoc // 20)

    def lr_tai(b):  # khoi dong tuyen tinh roi giam tuyen tinh ve 0
        return a.lr * (b + 1) / khoi if b < khoi else a.lr * max(0.0, (so_buoc - b) / (so_buoc - khoi))

    a.thu_muc_ra.mkdir(parents=True, exist_ok=True)
    nk = open(a.thu_muc_ra / "nhat_ky.jsonl", "a", encoding="utf-8")
    model.train()
    buoc, tong = 0, defaultdict(float)
    import time
    t0 = time.time()

    def mot_cap(m):
        """Moi luc chi giu MOT do thi (giu ca hai thi tran bo nho o 0,70 — chay thu 26/11).
        1) ban dung co gradient; 2) ban sai khong gradient -> z; 3) backward ban dung
        theo he so; 4) ban sai co gradient, backward theo he so. Gradient bang backward L."""
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


def pha_danh_gia(a, tok, mau):
    """Ti le cap ma mo hinh cho ban DUNG log-prob cao hon ban bi cay loi, theo loai."""
    import torch
    model = _nap_mo_hinh(a.model, a.adapter, huan_luyen=False)
    theo = defaultdict(lambda: [0, 0])
    with torch.no_grad():
        for i, m in enumerate(mau, 1):
            lt, lx, _ = _logp_cap(model, m, tok.pad_token_id, a.ghep_lo)
            theo[m["loai"]][0] += int(lt.item() > lx.item())
            theo[m["loai"]][1] += 1
            if i % 25 == 0:
                print(f"[danh-gia] {i}/{len(mau)}", flush=True)
    dung = sum(v[0] for v in theo.values())
    ket = {"adapter": str(a.adapter), "so_cap": len(mau), "ti_le_dung": dung / max(len(mau), 1),
           "theo_loai": {k: {"dung": v[0], "tong": v[1]} for k, v in sorted(theo.items())}}
    print(json.dumps(ket, ensure_ascii=False, indent=1), flush=True)
    a.tep_ket_qua.parent.mkdir(parents=True, exist_ok=True)
    a.tep_ket_qua.write_text(json.dumps(ket, ensure_ascii=False, indent=1), encoding="utf-8")


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
    ap.add_argument("--khong-ghep-lo", dest="ghep_lo", action="store_false",
                    help="chay ban dung va ban sai lan luot thay vi mot lo 2 chuoi")
    a = ap.parse_args(argv)
    a.tep_ref = a.thu_muc_ra / "ref_logp.jsonl"

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.model)
    tok.pad_token = tok.eos_token
    d = duong_dan.THU_MUC_DU_LIEU
    from src import du_lieu as _dl
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
