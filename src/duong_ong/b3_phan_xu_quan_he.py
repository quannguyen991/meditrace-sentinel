# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 3 – Cập nhật trạng thái]
Làm gì   : Quyết định quan hệ (bổ sung, đính chính, diễn biến, mâu thuẫn) cho từng cặp mệnh
           đề ứng viên, bằng luật hoặc bằng một lượt hỏi mô hình.
Vào → Ra : danh sách mệnh đề + lời thoại theo lượt → danh sách mệnh đề đã gán quan hệ cho
           các cặp đáng ngờ
Đọc từ   : phan() sinh cặp, phân xử, áp phán quyết; phan_bang_luat() là cách bằng luật không
           cần GPU
Mục lục (các hàm/lớp chính):
  phan()               Sinh cặp, phân xử, áp phán quyết cho danh sách mệnh đề
  cau_hoi()            Dựng câu hỏi quan hệ cho một cặp mệnh đề
  doc_dap_an()         Đọc đáp án quan hệ từ câu trả lời của mô hình
  phan_bang_luat()     Phân xử mọi cặp bằng luật bề mặt, không cần GPU
  phan_bang_mo_hinh()  Phân xử mọi cặp bằng một lượt gọi mô hình
  ep_json_phan()       Ép đầu ra theo lược đồ phân xử quan hệ
Gọi tới  : duong_ong/b1_cau_truc_menh_de, duong_ong/b3_sinh_cap_ung_vien_quan_he
Dùng bởi : duong_ong/chay_duong_ong
Tên cũ   : phan_quan_he.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Phân xử quan hệ cho TỪNG CẶP ứng viên — bước còn thiếu của lớp 2.

VÌ SAO CÓ TỆP NÀY.

`bakeoff.trich` bắt mô hình vừa liệt kê phát biểu VỪA tự đánh dấu `quan_he`
trong cùng một lượt sinh. Đó là bài toán **khởi phát**: mô hình phải tự nhớ
rằng mình vừa ghi một bản ghi tương tự ở đâu đó phía trước, tự quay lại đối
chiếu, rồi tự quyết định ghi thêm một trường không ai hỏi.

Trên hội thoại 4 lượt tự sinh thì làm được. Trên hội thoại 10-28 lượt của người
thật thì không: `quan_he` bằng "không" ở **282/282** phát biểu, trong khi
21/35 hội thoại có mốc kiểu "hôm qua... hôm nay..." — đúng dạng `dien bien`.

`ung_vien_quan_he.sinh_cap` đã giải nửa đầu: chương trình liệt kê cặp đáng ngờ,
vét cạn theo cấu trúc. Tệp này giải nửa sau: **hỏi mô hình một câu bốn lựa chọn
trên một cặp**, thay vì bắt nó tự tìm quan hệ trong toàn bộ danh sách.

    trước:  mô hình đọc 28 lượt, tự nhớ, tự đối chiếu, tự ghi thêm trường
    này:    chương trình đưa ra 2 phát biểu + các lượt thoại làm bằng chứng
            mô hình chỉ trả lời: bổ sung / đính chính / diễn biến /
                                 mâu thuẫn / không

BA ĐƯỜNG PHÂN, xếp theo chi phí tăng dần. Cả ba đều trả về cùng một kiểu dữ
liệu nên thay nhau được, và đều là đối chứng của nhau:

    luat      goi_y_bang_luat, không GPU. Đường lùi khi không có máy, VÀ là
              đối chứng: mô hình không hơn luật này thì bước phân bằng mô
              hình không đáng chi phí.
    mo_hinh   một lượt gọi mô hình cho mỗi cặp.
    ca_hai    luật quyết trước; cặp nào luật trả None thì mới hỏi mô hình.
              Rẻ nhất trong ba, vì phần lớn cặp có dấu hiệu bề mặt.

KHÔNG đoán bừa. Cả ba đường đều được phép trả `None` (= không có quan hệ).
Quan hệ giả nguy hiểm hơn là không có quan hệ: `cap_nhat.ap_luat` sẽ đánh dấu
một bản ghi ĐÚNG thành "bị thay thế" và vứt nó khỏi bệnh án.
"""
import json
import re
from typing import Dict, List, Optional, Tuple

from src.duong_ong import b3_sinh_cap_ung_vien_quan_he as uv
from src.duong_ong.b1_cau_truc_menh_de import QUAN_HE, PhatBieu

# "không" không nằm trong QUAN_HE (đó là bộ bốn giá trị quan hệ THẬT). Nó là
# đáp án thứ năm của câu hỏi, và được dịch thành None trước khi trả ra.
KHONG = "không"
DAP_AN = tuple(QUAN_HE) + (KHONG,)

# Ép đầu ra về đúng một trường. Càng ít trường càng ít chỗ hỏng: ở đây chỉ cần
# một nhãn, không cần lời giải thích — lời giải thích của mô hình 4B không
# dùng để kiểm tra được, chỉ làm tốn token và tăng cơ hội lệch định dạng.
LUOC_DO_PHAN = {
    "type": "object",
    "properties": {"quan_he": {"type": "string", "enum": list(DAP_AN)}},
    "required": ["quan_he"],
}

HUONG_DAN = """Bạn được cho HAI phát biểu lấy từ cùng một cuộc hội thoại khám bệnh, kèm những lượt thoại mà chúng dựa vào.

Hãy xác định quan hệ giữa phát biểu B với phát biểu A. Chỉ chọn MỘT trong năm đáp án:

- "bổ sung": B thêm thông tin cho A. Cả hai cùng đúng.
- "đính chính": người nói đã nói sai ở A và sửa lại thành B. A không còn đúng nữa.
- "diễn biến": A và B nói về HAI THỜI ĐIỂM khác nhau. Cả hai đều đúng, không cái nào thay thế cái nào.
- "mâu thuẫn": A và B trái nhau, và trong hội thoại không ai xác nhận lại cái nào đúng.
- "không": A và B không liên quan tới nhau, hoặc chỉ tình cờ giống chữ.

Phân biệt quan trọng nhất:
- "đính chính" là MỘT sự thật bị nói nhầm rồi sửa ("sốt 4 ngày... à không, 2 ngày").
- "diễn biến" là HAI sự thật ở hai thời điểm ("hôm qua nôn, hôm nay hết nôn").

Nếu không có căn cứ rõ trong lượt thoại, hãy chọn "không".

Chỉ trả về JSON dạng {"quan_he": "..."}."""


# ------------------------------------------------------------------ câu hỏi

# ─── _mo_ta() — Mô tả một mệnh đề trong một dòng ──────────────────────────────────────
# Chỉ in trường có giá trị, để mô hình không tưởng có thông tin ở trường rỗng.
def _mo_ta(p: PhatBieu) -> str:
    """Một dòng mô tả một phát biểu. Chỉ in trường CÓ giá trị — trường rỗng in
    ra chỉ làm nhiễu, và làm mô hình tưởng là có thông tin ở đó."""
    phan = [f"nội dung: {p.noi_dung}"]
    if p.ten_chu_the:
        phan.append(f"chủ thể: {p.ten_chu_the}")
    if p.moc_thoi_gian:
        phan.append(f"mốc thời gian: {p.moc_thoi_gian}")
    if p.do_chac_chan != "chắc chắn":
        phan.append(f"mức chắc chắn: {p.do_chac_chan}")
    if p.phu_dinh:
        phan.append("phủ định: có")
    if p.tinh_huong != "thực tế":
        phan.append(f"tình huống: {p.tinh_huong}")
    return "; ".join(phan)


# ═══ cau_hoi() — Dựng câu hỏi quan hệ cho một cặp mệnh đề ═════════════════════════════
# Lượt nói được in nguyên văn kèm số thứ tự vì dấu hiệu đính chính nằm trong lời nói.
def cau_hoi(cap: uv.CapUngVien, danh_sach: List[PhatBieu],
            luot_thoai: Optional[Dict[int, str]] = None) -> str:
    """Dựng câu hỏi cho MỘT cặp. Hàm thuần túy — test được không cần GPU.

    Lượt thoại được in NGUYÊN VĂN kèm số thứ tự, vì dấu hiệu đính chính
    ("à không", "nhầm rồi") nằm trong lời nói chứ không nằm trong trường nào
    của bản ghi. Bỏ lượt thoại đi là cắt mất căn cứ chính của câu hỏi.
    """
    theo_id = {p.id: p for p in danh_sach}
    a, b = theo_id.get(cap.a), theo_id.get(cap.b)
    if a is None or b is None:
        raise KeyError(f"cap tro toi ban ghi khong co: {cap.a}, {cap.b}")

    luot_thoai = luot_thoai or {}
    so_luot = sorted(set(a.bang_chung) | set(b.bang_chung))
    trich = "\n".join(f"{s}. {luot_thoai.get(s, '(không có lượt này)')}"
                      for s in so_luot) or "(không có lượt thoại kèm theo)"

    return (f"{HUONG_DAN}\n\n"
            f"Phát biểu A: {_mo_ta(a)}\n"
            f"Phát biểu B: {_mo_ta(b)}\n\n"
            f"Các lượt thoại liên quan:\n{trich}")


# --------------------------------------------------------------- đọc đáp án

# ═══ doc_dap_an() — Đọc đáp án quan hệ từ câu trả lời của mô hình ═════════════════════
# Nhận cả JSON lẫn văn xuôi; trả về một giá trị quan hệ hoặc None, không bao giờ đoán.
def doc_dap_an(van_ban: str) -> Optional[str]:
    """-> một giá trị trong QUAN_HE, hoặc None.

    Chấp nhận cả JSON lẫn văn xuôi: khi không ép được lm-format-enforcer thì
    mô hình vẫn trả lời được, chỉ là lộn xộn hơn. Không ép được mà vẫn đọc
    được thì cả cơ chế chạy tiếp trên máy không cài được thư viện đó.

    "không" -> None. Rác -> None. Không bao giờ đoán.
    """
    van = (van_ban or "").strip()
    try:
        d = json.loads(re.search(r"\{.*?\}", van, re.S).group(0))
        gia_tri = str(d.get("quan_he", "")).strip().lower()
    except Exception:                                       # noqa: BLE001
        gia_tri = ""
    if not gia_tri:
        # Văn xuôi: tìm nhãn dài nhất xuất hiện trong câu. Xét "đính chính"
        # trước "bổ sung" vì một câu có thể chứa cả hai từ; ưu tiên nhãn
        # NÀO DÀI HƠN để "không" không nuốt mất "không rõ ràng".
        thap = van.lower()
        ung = [d for d in DAP_AN if d in thap]
        if not ung:
            return None
        gia_tri = max(ung, key=len)
    return gia_tri if gia_tri in QUAN_HE else None


# ------------------------------------------------------------- ba đường phân

# ═══ phan_bang_luat() — Phân xử mọi cặp bằng luật bề mặt, không cần GPU ═══════════════
# Chỉ trả lời khi có dấu hiệu rõ, còn lại None.
def phan_bang_luat(caps: List[uv.CapUngVien], danh_sach: List[PhatBieu],
                   luot_thoai: Dict[int, str]) -> Dict[Tuple[int, int], Optional[str]]:
    """Đối chứng không GPU. Chỉ trả lời khi có dấu hiệu bề mặt, còn lại None."""
    return {c.khoa(): uv.goi_y_bang_luat(c, danh_sach, luot_thoai) for c in caps}


# ═══ phan_bang_mo_hinh() — Phân xử mọi cặp bằng một lượt gọi mô hình ══════════════════
# Giới hạn 24 token để mô hình không giải thích dài.
def phan_bang_mo_hinh(caps: List[uv.CapUngVien], danh_sach: List[PhatBieu],
                      luot_thoai: Dict[int, str], tok, model,
                      prefix_fn=None, max_token=24,
                      bo_qua=None) -> Dict[Tuple[int, int], Optional[str]]:
    """Một lượt gọi mô hình cho mỗi cặp.

    `max_token=24` đủ cho `{"quan_he": "đính chính"}` và không đủ cho mô hình
    bắt đầu giải thích dài dòng — đặt thật thấp là một cách chặn rẻ.

    `bo_qua`: các cặp đã có đáp án từ đường khác, không hỏi lại. Đây là chỗ
    đường `ca_hai` tiết kiệm: cặp nào luật đã quyết thì không tốn một lượt gọi.
    """
    import torch

    bo_qua = bo_qua or {}
    ra: Dict[Tuple[int, int], Optional[str]] = {}
    for c in caps:
        if c.khoa() in bo_qua and bo_qua[c.khoa()] is not None:
            ra[c.khoa()] = bo_qua[c.khoa()]
            continue
        msgs = [{"role": "user", "content": cau_hoi(c, danh_sach, luot_thoai)}]
        prompt = tok.apply_chat_template(msgs, tokenize=False,
                                         add_generation_prompt=True,
                                         enable_thinking=False)
        inp = tok(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            out = model.generate(**inp, max_new_tokens=max_token, do_sample=False,
                                 pad_token_id=tok.eos_token_id,
                                 prefix_allowed_tokens_fn=prefix_fn)
        sinh = tok.decode(out[0][inp["input_ids"].shape[1]:],
                          skip_special_tokens=True)
        ra[c.khoa()] = doc_dap_an(sinh)
    return ra


# ═══ ep_json_phan() — Ép đầu ra theo lược đồ phân xử quan hệ ══════════════════════════
# Không cài được thư viện thì trả None và báo rõ, không im lặng.
def ep_json_phan(tok):
    """Ép đầu ra theo LUOC_DO_PHAN. Giống `bakeoff._ep_json` nhưng lược đồ khác.

    Không cài được thì trả None và NÓI RÕ — im lặng ở đây sẽ thành một phép so
    sánh không còn điều kiện giống nhau giữa các lần chạy.
    """
    try:
        from lmformatenforcer import JsonSchemaParser
        from lmformatenforcer.integrations.transformers import (
            build_transformers_prefix_allowed_tokens_fn)
        return build_transformers_prefix_allowed_tokens_fn(
            tok, JsonSchemaParser(LUOC_DO_PHAN))
    except Exception as e:                                  # noqa: BLE001
        print(f"  (khong ep duoc JSON o buoc phan quan he: {e}; chay tu do)")
        return None


# --------------------------------------------------------------- cửa duy nhất

# ═══ phan() — Sinh cặp, phân xử, áp phán quyết cho danh sách mệnh đề ══════════════════
# Cửa duy nhất mà nhánh gọi; ba đường (luật, mô hình, kết hợp) cùng đếm thống kê. Trả về
# (danh sách mới, thống kê).
def phan(danh_sach: List[PhatBieu], luot_thoai: Dict[int, str],
         duong: str = "luat", tok=None, model=None, prefix_fn=None,
         toi_da: int = uv.TOI_DA_MAC_DINH) -> Tuple[List[PhatBieu], dict]:
    """Sinh cặp, phân xử, áp phán quyết. -> (danh sách MỚI, thống kê).

    Đây là cửa duy nhất mà `nhanh.py` gọi. Ba đường đều đi qua đây để thống kê
    được đếm giống nhau — nếu mỗi đường tự đếm một kiểu thì bảng so sánh giữa
    chúng không còn đọc được.
    """
    assert duong in ("luat", "mo_hinh", "ca_hai"), duong
    caps = uv.sinh_cap(danh_sach, luot_thoai, toi_da=toi_da)
    if not caps:
        return danh_sach, {"so_cap": 0, "so_phan": 0, "bi_cat": False,
                           "theo_nhan": {}, "duong": duong}

    if duong == "luat":
        phan_quyet = phan_bang_luat(caps, danh_sach, luot_thoai)
    elif duong == "mo_hinh":
        phan_quyet = phan_bang_mo_hinh(caps, danh_sach, luot_thoai, tok, model,
                                       prefix_fn)
    else:
        theo_luat = phan_bang_luat(caps, danh_sach, luot_thoai)
        phan_quyet = phan_bang_mo_hinh(caps, danh_sach, luot_thoai, tok, model,
                                       prefix_fn, bo_qua=theo_luat)

    moi = uv.ap_phan_quyet(danh_sach, phan_quyet)
    theo_nhan: Dict[str, int] = {}
    for v in phan_quyet.values():
        if v:
            theo_nhan[v] = theo_nhan.get(v, 0) + 1
    # `so_phan` đếm sau khi ÁP, không đếm phán quyết: `ap_phan_quyet` bỏ bớt
    # các cạnh tạo vòng hoặc trùng đích, nên hai số này khác nhau và số ĐÚNG
    # để báo cáo là số cạnh thực sự được gán.
    return moi, {
        "so_cap": len(caps),
        "so_phan": sum(1 for p in moi if p.quan_he),
        "so_phan_quyet": sum(1 for v in phan_quyet.values() if v),
        "bi_cat": uv.da_bi_cat(danh_sach, toi_da),
        "theo_nhan": theo_nhan,
        "duong": duong,
    }
