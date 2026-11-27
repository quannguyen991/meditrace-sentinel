# -*- coding: utf-8 -*-
"""[Công cụ lâm sàng hỗ trợ bác sĩ › Giấy tờ]
Làm gì   : Kiểm xem trước thủ thuật bác sĩ đã giải thích đủ các ý pháp lý cho người bệnh
           chưa, có căn cứ ở câu nào trong hội thoại.
Vào → Ra : hội thoại + danh sách mệnh đề (+ dấu thời gian âm thanh, tên thủ thuật) → kết quả
           kiểm từng ý giải thích, ý nào thiếu hoặc chưa rõ
Đọc từ   : kiem_chung_cam_doan_thu_thuat() kiểm các ý giải thích; co_dau_hieu_thu_thuat()
           nhận biết ca có thủ thuật
Mục lục (các hàm/lớp chính):
  co_dau_hieu_thu_thuat()          Phát hiện hội thoại có nhắc tới thủ thuật
  kiem_chung_cam_doan_thu_thuat()  Kiểm 6 mục giải thích trước thủ thuật, lập phiếu nháp
  _tach_luot_hoi_thoai()           Tách hội thoại thành các lượt đánh số
  _suy_ten_thu_thuat()             Suy ra tên thủ thuật từ đầu vào hoặc hội thoại
Gọi tới  : duong_ong/b1_cau_truc_menh_de
Dùng bởi : he_thong/dich_vu_http
Tên cũ   : cam_doan_thu_thuat.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Kiểm chứng Cam đoan Thủ thuật / Phẫu thuật có Căn cứ (Grounded Informed Consent Verifier).

Căn cứ pháp lý:
- Điều 10 & Điều 63 Luật Khám bệnh, chữa bệnh số 15/2023/QH15 (có hiệu lực từ 01/01/2024):
  Trước khi thực hiện phẫu thuật, thủ thuật hoặc can thiệp có nguy cơ tai biến, người hành nghề
  phải giải thích đầy đủ cho người bệnh hoặc người đại diện hợp pháp về 6 trụ cột bắt buộc:
    1. chan_doan_tinh_trang: Tình trạng bệnh / chẩn đoán cần can thiệp
    2. phuong_phap_thu_thuat: Phương pháp phẫu thuật, thủ thuật / can thiệp dự kiến
    3. nguy_co_tai_bien: Nguy cơ, tai biến, phản vệ, biến chứng có thể xảy ra
    4. phuong_an_thay_the: Phương án điều trị thay thế (nếu có)
    5. hau_qua_tu_choi: Hậu quả / tiên lượng nếu từ chối hoặc chậm trễ can thiệp
    6. xac_nhan_dong_y: Lời xác nhận đã hiểu và đồng ý của người bệnh hoặc người đại diện hợp pháp

Bất biến an toàn lâm sàng MediTrace:
- 100% quy tắc tất định (deterministic), KHÔNG dùng mô hình ngôn ngữ tự suy diễn.
- Truy vết hai chiều `[T1..Tn]` + `audio_spans` cho từng mục.
- KHÔNG chấp nhận bác sĩ / điều dưỡng tự nói đồng ý thay người bệnh.
- Mục nào chưa được giải thích trên hội thoại thì giữ nguyên `[Cần bác sĩ giải thích bổ sung]`.
"""
from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

from src.duong_ong.b1_cau_truc_menh_de import la_vai_nhan_vien

RE_TU_KHOA_THU_THUAT = re.compile(
    r"(?i)\b("
    r"thủ\s+thuật|phẫu\s+thuật|nội\s+soi|chọc\s+dò|cản\s+quang|"
    r"gây\s+mê|gây\s+tê|đặt\s+stent|truyền\s+máu|sinh\s+thiết|cam\s+đoan"
    r")\b"
)

RE_TEN_THU_THUAT_CU_THE = re.compile(
    r"(?i)\b("
    r"nội\s+soi\s+(?:thực\s+quản\s*[-–]?\s*)?(?:dạ\s+dày|đại\s+tràng|trực\s+tràng|phế\s+quản|tai\s+mũi\s+họng)(?:\s+gây\s+mê)?|"
    r"chụp\s+(?:ct|cắt\s+lớp\s+vi\s+tính|mri|cộng\s+hưởng\s+từ|mạch\s+vành)\s+(?:có\s+)?(?:tiêm\s+)?(?:thuốc\s+)?cản\s+quang|"
    r"tiêm\s+thuốc\s+cản\s+quang|"
    r"chọc\s+dò\s+(?:dịch\s+não\s+tủy|màng\s+phổi|màng\s+bụng|tủy\s+xương)|"
    r"đặt\s+stent\s*(?:mạch\s+vành|động\s+mạch|niệu\s+quản)?|"
    r"sinh\s+thiết\s*(?:gan|thận|phổi|dạ\s+dày|hạch|vú|tuyến\s+giáp)?|"
    r"truyền\s+(?:máu|khối\s+hồng\s+cầu|tiểu\s+cầu|huyết\s+tương)|"
    r"phẫu\s+thuật\s+[^\.,;!\?\n]{2,40}|"
    r"thủ\s+thuật\s+[^\.,;!\?\n]{2,40}"
    r")"
)

# 1. Giải thích tình trạng bệnh / chẩn đoán
RE_CHAN_DOAN_TINH_TRANG = re.compile(
    r"(?i)\b("
    r"chẩn\s+đoán|tình\s+trạng\s+(?:bệnh|hiện\s+tại|của\s+(?:bác|anh|chị|em|cháu|cụ|ông|bà))|"
    r"nghi\s+ngờ\s+(?:bị|viêm|loét|u|hẹp|tắc|xuất\s+huyết|nhồi\s+máu|tràn\s+dịch)|"
    r"(?:đang\s+bị|do|vì)\s+(?:viêm|loét|xuất\s+huyết|hẹp|tắc|thiếu\s+máu|sỏi|tràn\s+dịch|áp\s+xe|nhồi\s+máu)|"
    r"viêm\s+loét\s+(?:dạ\s+dày|đại\s+tràng|tá\s+tràng)|"
    r"bệnh\s+lý|tổn\s+thương\s+(?:ở|vùng|dạ\s+dày|đại\s+tràng|phổi|mạch\s+vành|não)|"
    r"cần\s+phải\s+kiểm\s+tra\s+nguyên\s+nhân|xác\s+định\s+ổ\s+(?:loét|chảy\s+máu|viêm|u)"
    r")\b"
)

# 2. Phương pháp thủ thuật / phẫu thuật dự kiến
RE_PHUONG_PHAP_THU_THUAT = re.compile(
    r"(?i)\b("
    r"phương\s+pháp|tiến\s+hành\s+(?:làm|nội\s+soi|phẫu\s+thuật|thủ\s+thuật|chọc\s+dò|tiêm|truyền|đặt|sinh\s+thiết)|"
    r"chỉ\s+định\s+(?:làm|nội\s+soi|phẫu\s+thuật|thủ\s+thuật|chụp|chọc\s+dò|tiêm|truyền\s+máu|đặt\s+stent|sinh\s+thiết)|"
    r"nội\s+soi|phẫu\s+thuật|thủ\s+thuật|chọc\s+dò|sinh\s+thiết|đặt\s+stent|truyền\s+máu|"
    r"tiêm\s+thuốc\s+cản\s+quang|gây\s+mê|gây\s+tê\s+(?:tại\s+chỗ|tủy\s+sống)|"
    r"đưa\s+ống\s+soi|luồn\s+ống\s+thông"
    r")\b"
)

# 3. Nguy cơ, tai biến, phản vệ, biến chứng
RE_NGUY_CO_TAI_BIEN = re.compile(
    r"(?i)\b("
    r"nguy\s+cơ|tai\s+biến|biến\s+chứng|rủi\s+ro|tác\s+dụng\s+phụ|"
    r"sốc\s+phản\s+vệ|phản\s+vệ|phản\s+ứng\s+dị\s+ứng|"
    r"chảy\s+máu|xuất\s+huyết|thủng\s+(?:dạ\s+dày|ruột|đại\s+tràng|tạng)|"
    r"nhiễm\s+trùng|nhiễm\s+khuẩn|suy\s+hô\s+hấp|tụt\s+huyết\s+áp|loạn\s+nhịp|"
    r"tổn\s+thương\s+thận\s+do\s+thuốc\s+cản\s+quang|suy\s+thận\s+cấp|"
    r"đau\s+rát\s+họng|chướng\s+bụng\s+sau\s+soi"
    r")\b"
)

# 4. Phương án điều trị thay thế
RE_PHUONG_AN_THAY_THE = re.compile(
    r"(?i)\b("
    r"phương\s+(?:án|pháp)\s+thay\s+thế|lựa\s+chọn\s+(?:thay\s+thế|khác)|"
    r"thay\s+thế\s+bằng|thay\s+vì\s+(?:nội\s+soi|mổ|tiêm\s+cản\s+quang|gây\s+mê)|"
    r"điều\s+trị\s+(?:nội\s+khoa|bảo\s+tồn)|uống\s+thuốc\s+theo\s+dõi\s+trước|"
    r"nội\s+soi\s+tỉnh\s+không\s+gây\s+mê|chụp\s+không\s+tiêm\s+thuốc|"
    r"siêu\s+âm\s+hoặc\s+xét\s+nghiệm\s+phân|test\s+hơi\s+thở|"
    r"ngoài\s+(?:cách|phương\s+pháp)\s+này|có\s+thể\s+chọn\s+cách\s+khác|"
    r"không\s+có\s+phương\s+pháp\s+thay\s+thế\s+tương\s+đương"
    r")\b"
)

# 5. Hậu quả nếu từ chối hoặc chậm trễ can thiệp
RE_HAU_QUA_TU_CHOI = re.compile(
    r"(?i)("
    r"\bnếu\s+(?:không|chưa|từ\s+chối|trì\s+hoãn|chậm\s+trễ|để\s+muộn)\b|"
    r"\bhậu\s+quả\s+(?:nếu|khi)\b|"
    r"\bchậm\s+trễ\s+(?:sẽ|có\s+thể|dẫn\s+đến|làm)\b|"
    r"\bbỏ\s+(?:sót|lỡ)\s+(?:tổn\s+thương|thời\s+gian\s+vàng|ung\s+thư\s+sớm|chẩn\s+đoán)\b|"
    r"\bbệnh\s+(?:sẽ\s+)?(?:tiến\s+triển\s+nặng|nặng\s+lên|nguy\s+hiểm\s+tính\s+mạng|vỡ|hoại\s+tử)\b"
    r")"
)

# 6. Lời xác nhận đồng ý của người bệnh / đại diện hợp pháp
RE_TU_CHOI_DONG_Y = re.compile(
    r"(?i)\b("
    r"không\s+đồng\s+ý|chưa\s+đồng\s+ý|từ\s+chối|không\s+làm\s+đâu|"
    r"chưa\s+muốn\s+làm|xin\s+(?:hoãn|về\s+suy\s+nghĩ|hỏi\s+ý\s+kiến)|"
    r"sợ\s+lắm\s+không\s+(?:làm|mổ|soi)"
    r")\b"
)

RE_XAC_NHAN_DONG_Y = re.compile(
    r"(?i)\b("
    r"đồng\s+ý|chấp\s+thuận|nhất\s+trí|xin\s+cam\s+đoan|ký\s+(?:giấy\s+)?cam\s+đoan|"
    r"(?:hiểu\s+rồi|đã\s+hiểu|nắm\s+rõ).{0,30}(?:đồng\s+ý|nhờ\s+bác\s+sĩ|cứ\s+làm|tiến\s+hành)|"
    r"(?:bác\s+sĩ|bệnh\s+viện)\s+cứ\s+(?:tiến\s+hành|làm\s+cho)|"
    r"nhờ\s+bác\s+sĩ\s+(?:làm|mổ|soi|tiến\s+hành)"
    r")\b"
)

RE_DAP_NGAN_DONG_Y = re.compile(
    r"(?i)^\s*(?:dạ\s+)?(?:vâng(?:\s+ạ)?|dạ\s+được\s+ạ|vâng\s+thưa\s+bác\s+sĩ|nhất\s+trí\s+ạ|ok\s+bác\s+sĩ)\s*[.!]*\s*$"
)

RE_BAC_SI_HOI_DONG_Y = re.compile(
    r"(?i)\b(đồng\s+ý|cam\s+đoan|chấp\s+thuận|tiến\s+hành\s+nhé|làm\s+nhé)\b"
)


# ═══ co_dau_hieu_thu_thuat() — Phát hiện hội thoại có nhắc tới thủ thuật ══════════════
# Tìm từ khoá thủ thuật/can thiệp xâm lấn trong hội thoại hoặc các mệnh đề; trả về đúng
# hoặc sai.
def co_dau_hieu_thu_thuat(hoi_thoai: str, phat_bieu: Optional[list] = None) -> bool:
    """Kiểm tra hội thoại hoặc danh sách phát biểu có đề cập thủ thuật / can thiệp xâm lấn không."""
    if RE_TU_KHOA_THU_THUAT.search(hoi_thoai or ""):
        return True
    for p in phat_bieu or []:
        nd = (
            (p.get("noi_dung") or p.get("text") or "")
            if isinstance(p, dict)
            else (getattr(p, "noi_dung", "") or "")
        )
        if RE_TU_KHOA_THU_THUAT.search(str(nd)):
            return True
    return False


# ─── _chuan_vai() — Quy nhãn người nói về năm vai chuẩn ───────────────────────────────
# Trả về bác sĩ, điều dưỡng, bệnh nhân, người nhà hoặc người khác; nhãn lạ thành người
# khác.
def _chuan_vai(vai_tho: str) -> str:
    """Chuẩn hóa nhãn người nói về: 'bác sĩ' | 'điều dưỡng' | 'bệnh nhân' | 'người nhà' | 'người khác'."""
    v = re.sub(r"\s+", " ", str(vai_tho or "")).strip().lower()
    if not v:
        return "người khác"
    if v in ("doctor", "bac_si", "bs", "bác sĩ", "bác sỹ") or la_vai_nhan_vien(v):
        if "điều dưỡng" in v or "y tá" in v or v in ("nurse", "dieu_duong"):
            return "điều dưỡng"
        return "bác sĩ"
    if v in ("patient", "benh_nhan", "bn", "bệnh nhân", "người bệnh"):
        return "bệnh nhân"
    tu_nguoi_nha = (
        "người nhà", "nguoi_nha", "family_member", "family", "gia đình",
        "người đại diện", "đại diện", "mẹ", "bố", "ba", "má", "con", "con gái",
        "con trai", "vợ", "chồng", "anh", "chị", "ông", "bà", "cô", "chú", "bác",
    )
    if v in tu_nguoi_nha or any(v.startswith(k + " ") for k in ("mẹ", "bố", "con", "vợ", "chồng", "người nhà")):
        return "người nhà"
    return "người khác"


# ─── _tach_luot_hoi_thoai() — Tách hội thoại thành các lượt đánh số ───────────────────
# Mỗi dòng thành một lượt (số thứ tự từ 1) kèm vai chuẩn và nội dung.
def _tach_luot_hoi_thoai(hoi_thoai: str) -> List[Dict[str, Any]]:
    """Tách hội thoại thành danh sách lượt có số thứ tự 1-based, vai chuẩn và nội dung."""
    dong_list = [d.strip() for d in (hoi_thoai or "").splitlines() if d.strip()]
    luot_ra: List[Dict[str, Any]] = []
    for idx, dong in enumerate(dong_list, start=1):
        # Bỏ tiền tố đánh số lượt kiểu "1. " hoặc "[T1] "
        sach = re.sub(r"^\s*(?:\[?T?\d+\]?[.)]?)\s*", "", dong)
        m = re.match(r"^([^:]{1,40}):\s*(.+)$", sach)
        if m:
            vai_goc = m.group(1).strip()
            noi_dung = m.group(2).strip()
            vai_chuan = _chuan_vai(vai_goc)
        else:
            vai_goc = ""
            noi_dung = sach
            vai_chuan = "người khác"
        luot_ra.append({
            "luot": idx,
            "vai_goc": vai_goc,
            "vai_chuan": vai_chuan,
            "noi_dung": noi_dung,
        })
    return luot_ra


# ─── _tao_ban_do_audio() — Lập bảng số lượt tới đoạn âm thanh ─────────────────────────
# Gom mốc thời gian (ms) và câu trích từ metadata âm thanh hoặc từ mệnh đề theo từng
# lượt.
def _tao_ban_do_audio(metadata_am_thanh: Optional[list], phat_bieu: Optional[list]) -> Dict[int, List[Dict[str, Any]]]:
    """Ánh xạ số lượt -> danh sách audio_spans từ metadata âm thanh hoặc từ mệnh đề."""
    theo_luot: Dict[int, List[Dict[str, Any]]] = {}
    for m in metadata_am_thanh or []:
        if not isinstance(m, dict) or m.get("luot") is None:
            continue
        luot_so = int(m["luot"])
        a_start = m.get("audio_start")
        a_end = m.get("audio_end")
        if a_start is None and a_end is None and m.get("start_ms") is None:
            continue
        start_ms = int(m["start_ms"]) if m.get("start_ms") is not None else int(round(float(a_start or 0.0) * 1000))
        end_ms = int(m["end_ms"]) if m.get("end_ms") is not None else int(round(float(a_end or 0.0) * 1000))
        theo_luot.setdefault(luot_so, []).append({
            "start_ms": start_ms,
            "end_ms": end_ms,
            "speaker_id": str(m.get("speaker_id") or m.get("speaker_role") or ""),
            "exact_quote": str(m.get("exact_quote") or ""),
        })

    for p in phat_bieu or []:
        d = p.to_dict() if hasattr(p, "to_dict") else (p if isinstance(p, dict) else {})
        bc = d.get("bang_chung") or d.get("evidenceTurns") or []
        spans = d.get("audio_spans") or []
        if len(bc) == 1 and spans and int(bc[0]) not in theo_luot:
            theo_luot[int(bc[0])] = list(spans)
    return theo_luot


# ─── _lay_spans_cho_luot() — Lấy các đoạn âm thanh của những lượt căn cứ ──────────────
def _lay_spans_cho_luot(
    luot_can_cu: List[int],
    trich_dan: List[str],
    ban_do_audio: Dict[int, List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    spans_ra: List[Dict[str, Any]] = []
    for idx, luot_so in enumerate(luot_can_cu):
        quote = trich_dan[idx] if idx < len(trich_dan) else (trich_dan[0] if trich_dan else "")
        for sp in ban_do_audio.get(int(luot_so), []):
            item = dict(sp)
            if not item.get("exact_quote") and quote:
                item["exact_quote"] = quote
            spans_ra.append(item)
    return spans_ra


# ─── _suy_ten_thu_thuat() — Suy ra tên thủ thuật từ đầu vào hoặc hội thoại ────────────
# Ưu tiên tên được truyền vào; không tìm được thì ghi nhãn cần bác sĩ xác nhận.
def _suy_ten_thu_thuat(
    ten_thu_thuat: Optional[str],
    hoi_thoai: str,
    phat_bieu: list,
) -> str:
    if ten_thu_thuat and str(ten_thu_thuat).strip():
        return str(ten_thu_thuat).strip()
    m = RE_TEN_THU_THUAT_CU_THE.search(hoi_thoai or "")
    if m:
        return re.sub(r"\s+", " ", m.group(1)).strip()
    for p in phat_bieu or []:
        d = p.to_dict() if hasattr(p, "to_dict") else (p if isinstance(p, dict) else {})
        nd = str(d.get("noi_dung") or d.get("text") or "")
        m_pb = RE_TEN_THU_THUAT_CU_THE.search(nd)
        if m_pb:
            return re.sub(r"\s+", " ", m_pb.group(1)).strip()
    m_chung = RE_TU_KHOA_THU_THUAT.search(hoi_thoai or "")
    if m_chung:
        return m_chung.group(0).strip()
    return "[Cần bác sĩ xác nhận tên thủ thuật]"


# ═══ kiem_chung_cam_doan_thu_thuat() — Kiểm 6 mục giải thích trước thủ thuật, lập phiếu nháp ═══
# Đối chiếu Điều 10 và 63 Luật KBCB 2023, trả số mục đạt, cảnh báo thiếu, bản nháp
# phiếu. Phải ký tay.
def kiem_chung_cam_doan_thu_thuat(
    hoi_thoai: str,
    phat_bieu: list,
    metadata_am_thanh: list | None = None,
    ten_thu_thuat: str | None = None,
) -> dict:
    """Kiểm chứng 6 trụ cột giải thích pháp lý trước thủ thuật theo Điều 10 & 63 Luật KBCB 2023."""
    cac_luot = _tach_luot_hoi_thoai(hoi_thoai or "")
    ban_do_audio = _tao_ban_do_audio(metadata_am_thanh, phat_bieu)
    ten_tt = _suy_ten_thu_thuat(ten_thu_thuat, hoi_thoai or "", phat_bieu or [])

    # Chuẩn hóa danh sách phát biểu để hỗ trợ đối chiếu bổ sung cho các trụ cột 1..5
    ds_pb_dict: List[Dict[str, Any]] = []
    for p in phat_bieu or []:
        if hasattr(p, "to_dict"):
            ds_pb_dict.append(p.to_dict())
        elif isinstance(p, dict):
            ds_pb_dict.append(p)

    def _quet_tru_cot_nhan_vien(
        ma: str,
        tieu_de: str,
        mau_regex: re.Pattern,
        goi_y_thieu: str,
        chap_nhan_chan_doan_pb: bool = False,
    ) -> Dict[str, Any]:
        luot_khop: List[int] = []
        trich_dan_khop: List[str] = []

        # 1. Quét trên các lượt nói của bác sĩ / điều dưỡng (không lấy câu hỏi của bệnh nhân)
        for luot_item in cac_luot:
            if luot_item["vai_chuan"] not in ("bác sĩ", "điều dưỡng"):
                continue
            nd = luot_item["noi_dung"]
            if mau_regex.search(nd):
                luot_khop.append(int(luot_item["luot"]))
                trich_dan_khop.append(nd)

        # 2. Quét bổ sung từ mệnh đề còn hiệu lực của nhân viên y tế (nếu lượt thoại thiếu nhãn vai)
        if not luot_khop:
            for pb in ds_pb_dict:
                if pb.get("phu_dinh") or pb.get("negated"):
                    continue
                if str(pb.get("trang_thai") or "còn hiệu lực") == "bị thay thế":
                    continue
                vai_pb = _chuan_vai(pb.get("nguoi_noi") or pb.get("speaker") or "")
                sec_pb = str(pb.get("section") or pb.get("muc") or "").upper()
                hanh_vi_pb = str(pb.get("hanh_vi") or "")
                nd_pb = str(pb.get("noi_dung") or pb.get("text") or "").strip()
                la_nv = vai_pb in ("bác sĩ", "điều dưỡng") or hanh_vi_pb in ("nhận định", "kế hoạch") or sec_pb in ("CHẨN ĐOÁN", "KẾ HOẠCH ĐIỀU TRỊ")
                if not la_nv:
                    continue
                if mau_regex.search(nd_pb) or (chap_nhan_chan_doan_pb and (hanh_vi_pb == "nhận định" or sec_pb == "CHẨN ĐOÁN") and nd_pb):
                    bc = [int(x) for x in (pb.get("bang_chung") or pb.get("evidenceTurns") or [])]
                    for b in bc:
                        if b not in luot_khop:
                            luot_khop.append(b)
                    td_list = pb.get("trich_dan") or pb.get("quotes") or []
                    if isinstance(td_list, str):
                        td_list = [td_list]
                    trich = td_list[0] if td_list else nd_pb
                    if trich and trich not in trich_dan_khop:
                        trich_dan_khop.append(str(trich))

        da_co = len(luot_khop) > 0
        spans = _lay_spans_cho_luot(luot_khop, trich_dan_khop, ban_do_audio) if da_co else []
        return {
            "ma": ma,
            "tieu_de": tieu_de,
            "da_giai_thich": da_co,
            "luot_can_cu": luot_khop,
            "trich_dan": trich_dan_khop,
            "audio_spans": spans,
            "canh_bao_thieu": None if da_co else goi_y_thieu,
        }

    muc_1 = _quet_tru_cot_nhan_vien(
        ma="chan_doan_tinh_trang",
        tieu_de="Giải thích tình trạng bệnh / chẩn đoán cần can thiệp",
        mau_regex=RE_CHAN_DOAN_TINH_TRANG,
        goi_y_thieu="Chưa ghi nhận bác sĩ giải thích rõ tình trạng bệnh / chẩn đoán dẫn tới chỉ định thủ thuật (Điều 63 Luật KBCB 2023).",
        chap_nhan_chan_doan_pb=True,
    )
    muc_2 = _quet_tru_cot_nhan_vien(
        ma="phuong_phap_thu_thuat",
        tieu_de="Phương pháp thủ thuật / phẫu thuật dự kiến",
        mau_regex=RE_PHUONG_PHAP_THU_THUAT,
        goi_y_thieu="Chưa ghi nhận giải thích về phương pháp thủ thuật / phẫu thuật / can thiệp dự kiến thực hiện.",
    )
    muc_3 = _quet_tru_cot_nhan_vien(
        ma="nguy_co_tai_bien",
        tieu_de="Nguy cơ, tai biến, phản vệ, biến chứng có thể xảy ra",
        mau_regex=RE_NGUY_CO_TAI_BIEN,
        goi_y_thieu="Chưa ghi nhận bác sĩ giải thích các nguy cơ, tai biến, phản vệ hoặc biến chứng có thể xảy ra trong và sau thủ thuật.",
    )
    muc_4 = _quet_tru_cot_nhan_vien(
        ma="phuong_an_thay_the",
        tieu_de="Phương án điều trị thay thế (nếu có)",
        mau_regex=RE_PHUONG_AN_THAY_THE,
        goi_y_thieu="Chưa ghi nhận giải thích về các phương án điều trị / chẩn đoán thay thế (hoặc nêu rõ lý do không có phương án thay thế).",
    )
    muc_5 = _quet_tru_cot_nhan_vien(
        ma="hau_qua_tu_choi",
        tieu_de="Hậu quả / tiên lượng nếu từ chối hoặc chậm trễ can thiệp",
        mau_regex=RE_HAU_QUA_TU_CHOI,
        goi_y_thieu="Chưa ghi nhận giải thích về hậu quả / nguy cơ tiến triển bệnh nếu người bệnh từ chối hoặc trì hoãn can thiệp.",
    )

    # 6. Kiểm chứng lời xác nhận đồng ý — BẮT BUỘC từ 'bệnh nhân' hoặc 'người nhà'
    luot_dong_y: List[int] = []
    trich_dong_y: List[str] = []
    bac_si_tu_noi_dong_y = False
    nguoi_benh_tu_choi = False

    for idx_l, luot_item in enumerate(cac_luot):
        vai = luot_item["vai_chuan"]
        nd = luot_item["noi_dung"]

        if vai in ("bác sĩ", "điều dưỡng"):
            # Phát hiện trường hợp bác sĩ tự kết luận đồng ý mà chưa có lời đáp của bệnh nhân/người nhà
            if RE_XAC_NHAN_DONG_Y.search(nd) and "?" not in nd and not re.search(r"(?i)\b(không|chưa|nhé|hả|ạ\?)\b", nd):
                bac_si_tu_noi_dong_y = True
            continue

        if vai in ("bệnh nhân", "người nhà"):
            if RE_TU_CHOI_DONG_Y.search(nd):
                nguoi_benh_tu_choi = True
                continue
            if RE_XAC_NHAN_DONG_Y.search(nd):
                luot_dong_y.append(int(luot_item["luot"]))
                trich_dong_y.append(nd)
            elif idx_l > 0 and RE_DAP_NGAN_DONG_Y.match(nd):
                luot_truoc = cac_luot[idx_l - 1]
                if luot_truoc["vai_chuan"] in ("bác sĩ", "điều dưỡng") and RE_BAC_SI_HOI_DONG_Y.search(luot_truoc["noi_dung"]):
                    luot_dong_y.extend([int(luot_truoc["luot"]), int(luot_item["luot"])])
                    trich_dong_y.extend([luot_truoc["noi_dung"], nd])

    # Nếu người bệnh từ chối ở lượt cuối cùng thì hủy trạng thái đồng ý trước đó
    if nguoi_benh_tu_choi and cac_luot:
        luot_cuoi_tu_choi = max(
            (int(x["luot"]) for x in cac_luot if x["vai_chuan"] in ("bệnh nhân", "người nhà") and RE_TU_CHOI_DONG_Y.search(x["noi_dung"])),
            default=0,
        )
        if not luot_dong_y or luot_cuoi_tu_choi >= max(luot_dong_y):
            luot_dong_y = []
            trich_dong_y = []

    da_dong_y = len(luot_dong_y) > 0
    if da_dong_y:
        canh_bao_6 = None
    elif nguoi_benh_tu_choi:
        canh_bao_6 = "Người bệnh / người nhà đang bày tỏ ý kiến TỪ CHỐI hoặc XIN TRÌ HOÃN thủ thuật — tuyệt đối không tự động xuất trạng thái đồng ý."
    elif bac_si_tu_noi_dong_y:
        canh_bao_6 = (
            "CHẶN AN TOÀN PHÁP LÝ: Chỉ có lượt lời của nhân viên y tế nêu từ khóa đồng ý, "
            "CHƯA có lời xác nhận trực tiếp từ 'bệnh nhân' hoặc 'người nhà'!"
        )
    else:
        canh_bao_6 = "Chưa ghi nhận lời xác nhận đã hiểu và đồng ý thực hiện thủ thuật từ chính người bệnh hoặc người đại diện hợp pháp."

    muc_6 = {
        "ma": "xac_nhan_dong_y",
        "tieu_de": "Xác nhận đã hiểu và đồng ý của người bệnh / đại diện hợp pháp",
        "da_giai_thich": da_dong_y,
        "luot_can_cu": sorted(set(luot_dong_y)),
        "trich_dan": trich_dong_y,
        "audio_spans": _lay_spans_cho_luot(sorted(set(luot_dong_y)), trich_dong_y, ban_do_audio) if da_dong_y else [],
        "canh_bao_thieu": canh_bao_6,
    }

    cac_muc = [muc_1, muc_2, muc_3, muc_4, muc_5, muc_6]
    so_muc_dat = sum(1 for m in cac_muc if m["da_giai_thich"])
    du_6_muc = so_muc_dat == 6
    ty_le = round(so_muc_dat / 6.0, 4)

    canh_bao_phap_ly: List[str] = [
        m["canh_bao_thieu"] for m in cac_muc if m.get("canh_bao_thieu")
    ]
    canh_bao_phap_ly.append(
        "LƯU Ý PHÁP LÝ: Bản dự thảo chỉ trích xuất lời giải thích có căn cứ từ hội thoại; "
        "bác sĩ và người bệnh/người đại diện hợp pháp bắt buộc kiểm tra và ký tay/ký số xác nhận trước khi thực hiện thủ thuật."
    )

    def _dong_phieu(muc: Dict[str, Any], nhan_thieu: str = "[Cần bác sĩ giải thích bổ sung]") -> str:
        if not muc["da_giai_thich"]:
            return nhan_thieu
        tag_luot = ", ".join(f"T{x}" for x in muc["luot_can_cu"])
        trich = " | ".join(f"“{q}”" for q in muc["trich_dan"][:2])
        return f"{trich} [{tag_luot}]"

    van_ban_phieu = (
        "GIẤY CAM ĐOAN CHẤP THUẬN PHẪU THUẬT, THỦ THUẬT VÀ CAN THIỆP XÂM LẤN\n"
        "(Đối chiếu tự động theo Điều 10 & Điều 63 Luật Khám bệnh, chữa bệnh số 15/2023/QH15)\n"
        "========================================================================\n"
        f"Tên thủ thuật / can thiệp dự kiến: {ten_tt}\n"
        f"Mức độ hoàn thành giải thích pháp lý: {so_muc_dat}/6 mục ({round(ty_le * 100, 1)}%)\n\n"
        f"1. Chẩn đoán / Tình trạng bệnh cần can thiệp:\n   {_dong_phieu(muc_1)}\n\n"
        f"2. Phương pháp phẫu thuật, thủ thuật dự kiến:\n   {_dong_phieu(muc_2)}\n\n"
        f"3. Nguy cơ, tai biến, phản vệ và biến chứng có thể xảy ra:\n   {_dong_phieu(muc_3)}\n\n"
        f"4. Phương án điều trị thay thế:\n   {_dong_phieu(muc_4)}\n\n"
        f"5. Hậu quả nếu từ chối hoặc chậm trễ can thiệp:\n   {_dong_phieu(muc_5)}\n\n"
        "6. Ý kiến xác nhận của người bệnh / người đại diện hợp pháp:\n"
        f"   {_dong_phieu(muc_6, '[Cần bác sĩ giải thích bổ sung / Chờ người bệnh hoặc đại diện hợp pháp xác nhận đồng ý]')}\n\n"
        "XÁC NHẬN TRƯỚC THỦ THUẬT (BẮT BUỘC KÝ TRỰC TIẾP — HỆ THỐNG KHÔNG TỰ ĐỘNG KÝ THAY):\n"
        "- Bác sĩ giải thích (Ký & ghi rõ họ tên): ........................................\n"
        "- Người bệnh / Đại diện hợp pháp (Ký & ghi rõ họ tên): ............................"
    )

    return {
        "can_cu_phap_ly": "Điều 10 & Điều 63 Luật Khám bệnh, chữa bệnh số 15/2023/QH15",
        "ten_thu_thuat": ten_tt,
        "du_6_muc_phap_ly": du_6_muc,
        "so_muc_dat": so_muc_dat,
        "tong_so_muc": 6,
        "ty_le_hoan_thanh": ty_le,
        "phan_tram_hoan_thanh": round(ty_le * 100.0, 1),
        "nguoi_benh_tu_choi_hoac_hoan": nguoi_benh_tu_choi,
        "chan_bac_si_tu_xac_nhan": bac_si_tu_noi_dong_y and not da_dong_y,
        "cac_muc_kiem_chung": cac_muc,
        "chi_tiet_theo_ma": {m["ma"]: m for m in cac_muc},
        "canh_bao_phap_ly": canh_bao_phap_ly,
        "van_ban_phieu_cam_doan": van_ban_phieu,
    }


if __name__ == "__main__":
    if "--check" in sys.argv:
        raw = sys.stdin.read().lstrip("\ufeff")
        payload = json.loads(raw) if raw.strip() else {}
        kq = kiem_chung_cam_doan_thu_thuat(
            hoi_thoai=str(payload.get("hoi_thoai") or payload.get("transcript") or payload.get("input") or ""),
            phat_bieu=payload.get("phat_bieu") or payload.get("propositions") or [],
            metadata_am_thanh=payload.get("metadata_am_thanh") or payload.get("metadata"),
            ten_thu_thuat=payload.get("ten_thu_thuat") or payload.get("procedureName"),
        )
        print(json.dumps(kq, ensure_ascii=False))
