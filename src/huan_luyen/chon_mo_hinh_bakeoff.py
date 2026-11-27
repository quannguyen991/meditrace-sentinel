# -*- coding: utf-8 -*-
"""[Huấn luyện mô hình › Chọn mô hình]
Làm gì   : So các mô hình ở bước rút mệnh đề bằng số đo trên tập phát triển thay vì chọn
           theo cảm tính.
Vào → Ra : tên mô hình, các ca hội thoại phát triển → tỷ lệ JSON hợp lệ và kết quả trích để
           chấm chủ thể
Đọc từ   : chay() nạp mô hình rồi trích trên ca mẫu; trich() chạy bước rút mệnh đề
Mục lục (các hàm/lớp chính):
  main()        Điểm vào: chạy bake-off trên tập phát triển
  chay()        Nạp mô hình rồi trích trên các ca mẫu
  nap()         Nạp mô hình một lần để dùng lại nhiều lượt
  trich()       Chạy bước rút mệnh đề trên danh sách ca mẫu
  kiem_khop()   Kiểm tệp đệm trích đúng bộ dữ liệu hiện tại
  _phan_tich()  Phân tích đầu ra thành danh sách mệnh đề
Gọi tới  : bo_du_lieu/nap_du_lieu, duong_ong/b1_cau_truc_menh_de,
           duong_ong/b1_vi_du_mau_loi_nhac, he_thong/duong_dan, huan_luyen/huan_luyen_sft
Dùng bởi : do_luong/do_bit_nhan, do_luong/do_bo_chan_doan, do_luong/do_quan_he,
           bo_du_lieu/du_lieu_huan_luyen_trich, bo_du_lieu/gan_nhan_truoc,
           duong_ong/chay_duong_ong, he_thong/dich_vu_http
Tên cũ   : bakeoff.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Bake-off chọn mô hình bằng số, không bằng phán đoán.

Qwen3-8B được chọn theo benchmark chung — KHÔNG phải theo bài toán trích phát
biểu lâm sàng tiếng Việt. Hai thứ đó tương quan chứ không đồng nhất. 30 phút thử
rẻ hơn 3 giờ train nhầm.

Đo HAI con số trên 20 hội thoại của tập PHÁT TRIỂN:

    tỷ lệ JSON hợp lệ      máy bằng, đếm tự động
    tỷ lệ gần đúng chủ thể  QUAN TRỌNG HƠN, phải chấm tay

Một mô hình sinh JSON đẹp mà gán nhầm chủ thể thì vô dụng cho dự án này.

    python -m src.huan_luyen.chon_mo_hinh_bakeoff --model Qwen/Qwen3-4B --n 20
"""
import argparse
import io
import json
import os
import sys
from pathlib import Path

from src.duong_ong.b1_cau_truc_menh_de import DUONG_DUNG, HANH_VI, TRANG_THAI_DUNG

LUOC_DO = {
    "type": "object",
    "properties": {
        "phat_bieu": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "chu_the": {"type": "string"},
                    "noi_dung": {"type": "string"},
                    "do_chac_chan": {"enum": ["chắc chắn", "nghi ngờ", "chưa ghi nhận"]},
                    "phu_dinh": {"type": "boolean"},
                    "tinh_huong": {"enum": ["thực tế", "giả định", "kế hoạch"]},
                    "thoi_gian_su_kien": {"enum": ["hiện tại", "quá khứ", "chưa rõ"]},
                    "moc_thoi_gian": {"type": ["string", "null"]},
                    "quan_he": {"enum": ["bổ sung", "đính chính", "diễn biến", "mâu thuẫn", "không"]},
                    "quan_he_voi": {"type": ["integer", "null"]},
                    "luot_thoai": {"type": "array", "items": {"type": "integer"}},
                    # Thêm 11/09/2026 — xem `phat_bieu.PhatBieu.trich_dan`. KHÔNG
                    # đưa vào "required": đầu ra cũ và mô hình nền không có hai
                    # trường này, và `_phan_tich` dùng danh sách bắt buộc của riêng
                    # nó. Thiếu trích dẫn thì `khoa_bang_chung` coi là bằng chứng
                    # yếu hơn, không coi là bản ghi hỏng.
                    "trich_dan": {"type": "array", "items": {"type": "string"}},
                    "hanh_vi": {"enum": list(HANH_VI)},
                    # Thêm 15/09/2026 — xem `phat_bieu.THUOC_KHOA`. Chỉ phát biểu về
                    # thuốc mang trường này; KHÔNG vào "required", cùng lý do với
                    # `trich_dan`. Hai danh sách đóng lấy từ `phat_bieu`, không gõ
                    # lại ở đây: hai bản gõ tay là hai bản sẽ trôi nhau.
                    "thuoc": {
                        "type": ["object", "null"],
                        "properties": {
                            "ten": {"type": "string"},
                            "lieu": {"type": ["string", "null"]},
                            "so_lan": {"type": ["string", "null"]},
                            "duong_dung": {"enum": list(DUONG_DUNG) + [None]},
                            "bat_dau": {"type": ["string", "null"]},
                            "ngung": {"type": ["string", "null"]},
                            "trang_thai_dung": {"enum": list(TRANG_THAI_DUNG) + [None]},
                        },
                        "required": ["ten"],
                    },
                },
                "required": ["chu_the", "noi_dung", "do_chac_chan", "luot_thoai"],
            },
        }
    },
    "required": ["phat_bieu"],
}

HUONG_DAN = """Đọc hội thoại khám bệnh dưới đây. Với MỖI thông tin lâm sàng, ghi một bản ghi gồm:

- chu_the: thông tin này nói VỀ AI. Người nhà thường kể hộ bệnh nhân — khi đó chủ thể là bệnh nhân, không phải người kể. Nhưng nếu người nhà kể bệnh CỦA CHÍNH HỌ thì chủ thể là người nhà.
  Tuổi, cân nặng, giới tính của bệnh nhân là thông tin VỀ BỆNH NHÂN, kể cả khi người nhà là người nói ra.
- noi_dung: triệu chứng, bệnh, thuốc hoặc kết quả
- thuoc: CHỈ ghi khi bản ghi là thông tin về thuốc; bản ghi khác thì bỏ trường này. Gồm ten; lieu (ví dụ "5 mg", "hai nhát"); so_lan (ví dụ "ngày hai lần", "khi cần"); duong_dung: "uống" | "xịt" | "bôi" | "nhỏ"; bat_dau (ví dụ "hai tuần nay"); ngung (ví dụ "2 tuần"); trang_thai_dung: "đang dùng" | "đã ngừng" | "được kê, chưa dùng" (bác sĩ vừa kê trong buổi khám, người bệnh chưa dùng viên nào). Chi tiết nào hội thoại KHÔNG nói thì để null — không đoán liều, không đoán số lần dùng. GIỮ NGUYÊN chữ trong hội thoại. Liều bị người nói sửa lại ("5 mg, à nhầm, 10 mg") thì ghi CẢ HAI bản, bản sau "đính chính" bản trước.
- do_chac_chan: "chắc chắn" | "nghi ngờ" | "chưa ghi nhận". "Chưa thấy bị bao giờ" là "chưa ghi nhận", KHÔNG phải phủ định chắc chắn.
- phu_dinh: true nếu là phủ định
- tinh_huong: "thực tế" | "giả định" | "kế hoạch". "Nếu mai vẫn đau thì..." là "giả định".
- thoi_gian_su_kien: "hiện tại" | "quá khứ" | "chưa rõ"
- moc_thoi_gian: mốc CỤ THỂ nếu hội thoại nêu, ví dụ "2 ngày", "hôm qua", "hôm nay". Để null nếu không có. GIỮ NGUYÊN chữ trong hội thoại.
- quan_he: quan hệ với một bản ghi TRƯỚC ĐÓ, kèm quan_he_voi là số thứ tự bản ghi đó (đếm từ 0):
    "đính chính" — người nói tự sửa lại chính thông tin vừa nêu ("4 ngày... à không, 2 ngày"). Ghi CẢ HAI bản, bản sau đính chính bản trước.
    "diễn biến"  — hai mốc thời gian khác nhau, CẢ HAI đều đúng ("hôm qua đau, hôm nay hết"). Ghi CẢ HAI bản.
    "bổ sung"    — thêm chi tiết cho thông tin đã nêu
    "mâu thuẫn"  — hai nguồn nói trái nhau, chưa ai xác nhận lại
    "không"      — không liên quan bản ghi nào trước đó
- luot_thoai: danh sách SỐ THỨ TỰ các lượt làm bằng chứng — lượt CHỨA thông tin đó. Câu trả lời tắt như "Dạ, không ạ" thì thêm cả lượt câu hỏi ngay trước.
- trich_dan: với MỖI lượt trong luot_thoai, chép NGUYÊN VĂN đoạn ngắn nhất trong lượt đó nói ra thông tin — đúng từng chữ, kể cả cách nói dân dã hay phương ngữ. Không sửa, không tóm tắt, không chuẩn hóa.
- hanh_vi: "trả lời" | "tự kể" | "quan sát" | "nhận định" | "kế hoạch". Bệnh nhân hoặc người nhà nói ngay sau lượt của bác sĩ là "trả lời"; tự nói ra khi không ai hỏi là "tự kể". Kết quả khám là "quan sát", chẩn đoán là "nhận định", chỉ định và dặn dò là "kế hoạch".

Câu hỏi mà không ai trả lời thì KHÔNG tạo bản ghi.
Chỉ trả về JSON, không giải thích."""

from src.duong_ong.b1_vi_du_mau_loi_nhac import VI_DU  # noqa: E402  (4 ví dụ, xem tệp đó)


# ═══ danh_so_luot() — Đánh số từng lượt thoại ═════════════════════════════════════════
# Trả hội thoại đã đánh số và số lượt.
def danh_so_luot(hoi_thoai):
    dong = [d for d in hoi_thoai.split("\n") if d.strip()]
    return "\n".join(f"{i+1}. {d}" for i, d in enumerate(dong)), len(dong)


# ═══ kiem_khop() — Kiểm tệp đệm trích đúng bộ dữ liệu hiện tại ════════════════════════
# Lệch thì dừng ngay, tránh số đo sai do đệm của bộ cũ.
def kiem_khop(mau_theo_id, tho, ten_dem=""):
    """Tệp đệm trích có PHẢI của bộ dữ liệu này không. Sai thì ném lỗi ngay.

    VÌ SAO CẦN (10/09/2026). Bộ dữ liệu được sinh lại từ 3.000 ca lên 5.000 ca,
    và `viet_phat_trien.jsonl` bị ghi đè bằng tập phát triển MỚI. Tệp đệm trích
    vẫn là của bộ cũ. Mã của ca là `hv_xxxx` ở CẢ HAI bộ — nên id khớp hết, và
    phép đo chạy trơn tru, cho ra một bảng số hoàn toàn vô nghĩa:

        đo trên bộ cũ   ca có quan hệ thật: 16/60
        đo sau khi đổi  ca có quan hệ thật:  1/60   <- số của bộ khác

    Không có gì báo lỗi. Không JSON hỏng, không ngoại lệ, không dòng cảnh báo.
    Nếu không đối chiếu tay với lần đo trước thì đã báo cáo con số đó.

    Phép kiểm: `so_luot` trong tệp đệm phải bằng số lượt của hội thoại trong
    đáp án. Rẻ, và đủ để bắt mọi trường hợp hai bộ khác nhau — hai hội thoại
    khác nhau gần như không bao giờ cùng số lượt ở TẤT CẢ các ca.
    """
    lech = []
    for k in tho:
        ca = mau_theo_id.get(k["id"])
        if ca is None:
            lech.append(f"{k['id']}: khong co trong dap an")
            continue
        that = len([d for d in ca["input"].split("\n") if d.strip()])
        if k.get("so_luot") != that:
            lech.append(f"{k['id']}: dem ghi {k.get('so_luot')} luot, "
                        f"dap an co {that}")
    if lech:
        raise SystemExit(
            f"TU CHOI: tep dem trich {ten_dem} KHONG phai cua bo du lieu nay.\n"
            + "\n".join("  " + x for x in lech[:5])
            + (f"\n  ... va {len(lech) - 5} cho nua" if len(lech) > 5 else "")
            + "\nSinh lai tep dem, hoac tro toi dung bo du lieu da dung de trich.")


# ═══ nap() — Nạp mô hình một lần để dùng lại nhiều lượt ═══════════════════════════════
# Nạp được kèm adapter và ép JSON tuỳ chọn.
def nap(ten_mo_hinh, ep_json=True, adapter=None):
    """Nạp mô hình một lần, dùng lại cho nhiều lượt chạy.

    Tách khỏi `chay` để nhánh B và C không phải nạp lại 8B mỗi lần — nạp mất
    vài phút và chiếm hết VRAM, không thể nạp hai bản cùng lúc.
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    tok = AutoTokenizer.from_pretrained(ten_mo_hinh)
    bnb = BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)

    # Boost 2: Nếu GPU còn >= 3.5 GB VRAM trống, ghim toàn bộ mô hình 4-bit lên GPU 0
    # (`device_map={"": 0}`) để tránh `device_map="auto"` âm thầm offload layer sang CPU RAM
    # qua PCIe làm chậm 5-10x; nếu thiếu VRAM hoặc OOM thì tự động lùi về `device_map="auto"`.
    cuda_mod = getattr(torch, "cuda", None)
    co_cuda = bool(cuda_mod is not None and callable(getattr(cuda_mod, "is_available", None)) and cuda_mod.is_available())
    vram_trong_gb = 0.0
    if co_cuda and callable(getattr(cuda_mod, "mem_get_info", None)):
        try:
            vram_trong_gb = float(cuda_mod.mem_get_info()[0]) / (1024 ** 3)
        except Exception:
            vram_trong_gb = 0.0

    oom_cls = getattr(cuda_mod, "OutOfMemoryError", RuntimeError) if cuda_mod is not None else RuntimeError
    if co_cuda and vram_trong_gb >= 3.5:
        try:
            model = AutoModelForCausalLM.from_pretrained(
                ten_mo_hinh, quantization_config=bnb, torch_dtype=torch.bfloat16,
                device_map={"": 0})
        except (oom_cls, RuntimeError, MemoryError):
            if callable(getattr(cuda_mod, "empty_cache", None)):
                cuda_mod.empty_cache()
            model = AutoModelForCausalLM.from_pretrained(
                ten_mo_hinh, quantization_config=bnb, torch_dtype=torch.bfloat16,
                device_map="auto")
    else:
        model = AutoModelForCausalLM.from_pretrained(
            ten_mo_hinh, quantization_config=bnb, torch_dtype=torch.bfloat16,
            device_map="auto")
    if adapter:
        # Adapter huấn luyện RIÊNG cho khâu trích (`--nhiem-vu trich`).
        # Khác hẳn adapter của nhánh A, vốn học viết bệnh án.
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
        model._co_adapter_trich = True
        print(f"  (da nap adapter trich: {adapter})", flush=True)
    else:
        model._co_adapter_trich = False
    model.eval()

    prefix_fn = _ep_json(tok) if ep_json else None
    return tok, model, prefix_fn


# ─── _ep_json() — Dựng ràng buộc ép đầu ra theo lược đồ ───────────────────────────────
# Không có thư viện thì chạy tự do và nói rõ.
def _ep_json(tok):
    """Ép đầu ra theo LUOC_DO. Không cài được lm-format-enforcer thì chạy tự do
    và NÓI RÕ — im lặng ở đây sẽ thành một phép so sánh không còn điều kiện
    giống nhau giữa các lần chạy."""
    try:
        from lmformatenforcer import JsonSchemaParser
        from lmformatenforcer.integrations.transformers import (
            build_transformers_prefix_allowed_tokens_fn)
        return build_transformers_prefix_allowed_tokens_fn(
            tok, JsonSchemaParser(LUOC_DO))
    except Exception as e:                           # noqa: BLE001
        print(f"  (khong ep duoc JSON: {e}; chay tu do)")
        return None


# ═══ trich() — Chạy bước rút mệnh đề trên danh sách ca mẫu ════════════════════════════
# Chọn lời nhắc và ví dụ theo mô hình; giới hạn token tránh cắt cụt JSON.
def trich(tok, model, prefix_fn, mau_list, max_token=1536, vi_du=None,
          luu_dan=None, prompt_lookup_num_tokens=None):
    """max_token=1536: ở 768 thì 4B bị CẮT CỤT giữa JSON (2/8 mẫu), vì nó trích
    được nhiều phát biểu hơn 1.7B. Đó là lỗi cơ học, không phải lỗi năng lực.

    `vi_du=None`: tự động theo mô hình. Nếu đã nạp `adapter_trich` (huấn luyện
    với `du_lieu_trich.dung(..., vi_du=False)` và `LOI_NHAC_HE_THONG_TRICH`),
    mặc định `vi_du=False` và kèm system prompt để KHỚP 100% phân phối lúc train
    và giảm 2.000 token prompt (tránh tràn VRAM). Nếu zero-shot (không adapter),
    mặc định `vi_du=True` (5 ví dụ mẫu).
    """
    co_adapter = bool(getattr(model, "_co_adapter_trich", False))
    if vi_du is None:
        vi_du = not co_adapter
    if prompt_lookup_num_tokens is None:
        env_plt = os.environ.get("MEDITRACE_PROMPT_LOOKUP_TOKENS", "").strip()
        if env_plt != "":
            try:
                prompt_lookup_num_tokens = max(0, int(env_plt))
            except ValueError:
                prompt_lookup_num_tokens = 5 if co_adapter else None
        elif co_adapter:
            prompt_lookup_num_tokens = 5
    # Chạy tiếp bỏ qua mẫu THEO ID. Nhưng id là `hv_xxxx` ở MỌI bộ tự sinh,
    # nên một tệp đệm của bộ 3.000 sẽ được dùng lại nguyên cho bộ 5.000 —
    # và đó là một phép đo trên dữ liệu trộn lẫn, im lặng hoàn toàn.
    #
    # Nên mỗi bản ghi trong tệp đệm phải chứng minh nó là của ĐÚNG hội thoại
    # đang xét: `so_luot` phải khớp. Bản nào không khớp thì BỎ và trích lại,
    # chứ không dùng lại. Báo ra số bản bị bỏ — im lặng ở đây cũng nguy hiểm
    # ngang im lặng khi dùng lại bản sai.
    da_co = {}
    if luu_dan is not None:
        dp = Path(luu_dan)
        if dp.exists():
            so_luot_that = {}
            for m in mau_list:
                so_luot_that[m["id"]] = len(
                    [d for d in m["input"].split("\n") if d.strip()])
            bo = 0
            for dong in dp.read_text(encoding="utf-8").splitlines():
                if not dong.strip():
                    continue
                k = json.loads(dong)
                mong = so_luot_that.get(k["id"])
                if mong is not None and k.get("so_luot") != mong:
                    bo += 1
                    continue
                da_co[k["id"]] = k
            print(f"  (da co {len(da_co)} mau trong {dp.name}, chay tiep)",
                  flush=True)
            if bo:
                print(f"  (BO {bo} mau trong tep dem: so luot khong khop "
                      f"hoi thoai dang xet — tep dem cua bo du lieu khac)",
                      flush=True)

    ket_qua = []
    tep = open(luu_dan, "a", encoding="utf-8") if luu_dan is not None else None
    try:
        return _vong_trich(tok, model, prefix_fn, mau_list, max_token, vi_du,
                           da_co, tep, ket_qua,
                           co_adapter=co_adapter,
                           prompt_lookup_num_tokens=prompt_lookup_num_tokens)
    finally:
        if tep is not None:
            tep.close()


_CACHE_LOI_NHAC_TINH = {}


# ─── _sinh_mot_mau() — Sinh đầu ra cho một ca ─────────────────────────────────────────
# Giải mã tất định, có thể ép theo tiền tố.
def _sinh_mot_mau(tok, model, inp, max_token, prefix_fn=None,
                  prompt_lookup_num_tokens=None):
    import torch
    kw = dict(max_new_tokens=max_token, do_sample=False,
              use_cache=True, pad_token_id=tok.eos_token_id)
    if prefix_fn is not None:
        kw["prefix_allowed_tokens_fn"] = prefix_fn
    elif prompt_lookup_num_tokens:
        kw["prompt_lookup_num_tokens"] = prompt_lookup_num_tokens
    with torch.no_grad():
        try:
            out = model.generate(**inp, **kw)
        except TypeError:
            # Mô hình giả trong test hoặc phiên bản transformers cũ không nhận tham số phụ
            kw.pop("prompt_lookup_num_tokens", None)
            try:
                out = model.generate(**inp, **kw)
            except TypeError:
                kw.pop("use_cache", None)
                out = model.generate(**inp, **kw)
    vao_len = inp["input_ids"].shape[1]
    van_ban = tok.decode(out[0][vao_len:], skip_special_tokens=True)
    del out
    return van_ban


# ─── _vong_trich() — Vòng lặp trích lần lượt các ca ───────────────────────────────────
# Chạy từng ca, phân tích JSON và ghi kết quả.
def _vong_trich(tok, model, prefix_fn, mau_list, max_token, vi_du,
                da_co, tep, ket_qua, co_adapter=False,
                prompt_lookup_num_tokens=None):
    from src.huan_luyen.huan_luyen_sft import LOI_NHAC_HE_THONG_TRICH
    khoa_nhac = bool(vi_du)
    if khoa_nhac not in _CACHE_LOI_NHAC_TINH:
        _CACHE_LOI_NHAC_TINH[khoa_nhac] = HUONG_DAN + (
            f"\n\n{VI_DU}\n\nBây giờ đến lượt bạn." if khoa_nhac else ""
        )
    loi_nhac = _CACHE_LOI_NHAC_TINH[khoa_nhac]
    for i, m in enumerate(mau_list, 1):
        if m["id"] in da_co:
            ket_qua.append(da_co[m["id"]])
            print(f"  [{i:2d}/{len(mau_list)}] {m['id']:14} (da co, bo qua)",
                  flush=True)
            continue
        danh_so, so_luot = danh_so_luot(m["input"])
        noi_dung_user = f"{loi_nhac}\n\nHội thoại:\n{danh_so}"
        if co_adapter:
            msgs = [{"role": "system", "content": LOI_NHAC_HE_THONG_TRICH},
                    {"role": "user", "content": noi_dung_user}]
        else:
            msgs = [{"role": "user", "content": noi_dung_user}]
        prompt = tok.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        # torch nạp ở đây chứ không ở đầu hàm: mẫu lấy từ tệp đệm không cần
        # đến nó, nên chạy tiếp được cả trên máy không có GPU.
        import torch
        inp = tok(prompt, return_tensors="pt").to(model.device)
        # Giải mã 2 tầng (Two-Tier Lazy Enforcement): khi đã có adapter fine-tune,
        # chạy giải mã nhanh trước (không tốn CPU quét 151.936 token mỗi bước);
        # chỉ khi JSON hỏng mới fallback sang prefix_fn.
        if co_adapter and prefix_fn is not None:
            sinh = _sinh_mot_mau(tok, model, inp, max_token, prefix_fn=None,
                                 prompt_lookup_num_tokens=prompt_lookup_num_tokens)
            hop_le, du_lieu, ly_do = _phan_tich(sinh, so_luot)
            if not hop_le:
                sinh = _sinh_mot_mau(tok, model, inp, max_token, prefix_fn=prefix_fn)
                hop_le, du_lieu, ly_do = _phan_tich(sinh, so_luot)
        else:
            sinh = _sinh_mot_mau(tok, model, inp, max_token, prefix_fn=prefix_fn,
                                 prompt_lookup_num_tokens=prompt_lookup_num_tokens)
            hop_le, du_lieu, ly_do = _phan_tich(sinh, so_luot)
        del inp
        if hasattr(torch, "cuda") and torch.cuda.is_available():
            torch.cuda.empty_cache()
        ban_ghi = {"id": m["id"], "so_luot": so_luot, "json_hop_le": hop_le,
                   "ly_do": ly_do, "phat_bieu": du_lieu, "tho": sinh[:400]}
        ket_qua.append(ban_ghi)
        if tep is not None:
            # flush ngay: treo máy hay mất điện thì mẫu vừa xong vẫn còn.
            tep.write(json.dumps(ban_ghi, ensure_ascii=False) + "\n")
            tep.flush()
        # flush=True: khi chuyển hướng ra tệp, Python đệm stdout theo khối 8 KB
        # nên không theo dõi được tiến độ của một lần chạy 40 phút.
        print(f"  [{i:2d}/{len(mau_list)}] {m['id']:14} "
              f"{'JSON OK' if hop_le else 'JSON HONG'} "
              f"{len(du_lieu) if du_lieu else 0} phat bieu", flush=True)
    return ket_qua


# ═══ chay() — Nạp mô hình rồi trích trên các ca mẫu ═══════════════════════════════════
# Giữ chữ ký cũ cho các chỗ gọi sẵn.
def chay(ten_mo_hinh, mau_list, ep_json=True, max_token=1536, vi_du=True):
    """Nạp rồi trích. Giữ chữ ký cũ để các chỗ gọi sẵn không phải sửa."""
    tok, model, prefix_fn = nap(ten_mo_hinh, ep_json)
    return trich(tok, model, prefix_fn, mau_list, max_token, vi_du)


# ─── _phan_tich() — Phân tích đầu ra thành danh sách mệnh đề ──────────────────────────
# Trả (hợp lệ, danh sách mệnh đề, lý do hỏng).
def _phan_tich(van_ban, so_luot):
    """Trả về (hop_le, danh_sach_phat_bieu, ly_do_hong)."""
    try:
        d = json.loads(van_ban)
    except json.JSONDecodeError as e:
        return False, None, f"json hong: {e}"
    if "phat_bieu" not in d or not isinstance(d["phat_bieu"], list):
        return False, None, "thieu khoa 'phat_bieu'"
    for p in d["phat_bieu"]:
        thieu = [k for k in ("chu_the", "noi_dung", "do_chac_chan", "luot_thoai")
                 if k not in p]
        if thieu:
            return False, d["phat_bieu"], f"thieu truong {thieu}"
        # Bằng chứng phải trỏ tới lượt thoại CÓ THẬT — đây là kiểm bằng luật,
        # không phải kiểm cú pháp
        xau = [n for n in p["luot_thoai"] if not (1 <= n <= so_luot)]
        if xau:
            return False, d["phat_bieu"], f"luot thoai khong ton tai: {xau}"
    return True, d["phat_bieu"], ""


# ═══ main() — Điểm vào: chạy bake-off trên tập phát triển ═════════════════════════════
# Đo tỉ lệ JSON hợp lệ; độ đúng chủ thể phải chấm tay.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--khong-ep-json", action="store_true")
    ap.add_argument("--khong-vi-du", action="store_true")
    a = ap.parse_args()

    from src.bo_du_lieu import nap_du_lieu as du_lieu
    from src.he_thong import duong_dan as duong_dan

    mau = du_lieu.nap_mau(duong_dan.THU_MUC_DU_LIEU / "phat_trien.jsonl")[:a.n]
    print(f"Bake-off: {a.model} tren {len(mau)} hoi thoai tap phat trien")
    kq = chay(a.model, mau, ep_json=not a.khong_ep_json, vi_du=not a.khong_vi_du)

    hop_le = sum(1 for k in kq if k["json_hop_le"])
    ten_tep = a.model.split("/")[-1].replace(".", "_")
    hau_to = "" if not a.khong_vi_du else "-khong-vi-du"
    dp = duong_dan.THU_MUC_KET_QUA / f"bakeoff-{ten_tep}{hau_to}.json"
    dp.write_text(json.dumps(kq, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"Ty le JSON hop le: {hop_le}/{len(kq)} = {100*hop_le/len(kq):.0f}%")
    print(f"Ket qua tho: {dp}")
    print("Ty le gan dung chu the PHAI CHAM TAY — mo tep tren va doc tung phat bieu.")


if __name__ == "__main__":
    main()
