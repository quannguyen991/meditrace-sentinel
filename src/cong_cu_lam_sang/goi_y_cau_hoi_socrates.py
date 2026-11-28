# -*- coding: utf-8 -*-
"""[Công cụ lâm sàng hỗ trợ bác sĩ › Trong lúc khám]
Làm gì   : Tìm điểm còn thiếu trong phần hỏi bệnh theo khung SOCRATES và gợi ý bác sĩ hỏi
           thêm câu nào.
Vào → Ra : mệnh đề đã trích + hội thoại → danh sách khoảng trống thông tin và câu hỏi gợi ý
Đọc từ   : class ActiveClinicalClarificationAgent tìm khoảng trống thông tin; class
           GoiYLamSang một gợi ý
Mục lục (các hàm/lớp chính):
  class ActiveClinicalClarificationAgent  Tìm thông tin còn thiếu và gợi ý câu hỏi cho bác sĩ
  class GoiYLamSang                       Một câu hỏi gợi ý cho bác sĩ để lấp khoảng trống
  class KetQuaTroLyLamSang                Tập gợi ý và mức đầy đủ của bệnh án
Dùng bởi : he_thong/dieu_phoi_cac_chot_an_toan
Tên cũ   : tro_ly_lam_sang.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Trợ lý Gợi ý Câu hỏi Lâm sàng (Active Clinical Clarification Agent).

Phát hiện:
1. Đau: vị trí, tính chất, hướng lan (đau ngực).
2. Sốt: nhiệt độ đo được, rét run.
3. Ho: ho khan hay có đờm, màu đờm.
4. Thuốc thường gặp chưa rõ hàm lượng/liều.
5. Nữ tuổi sinh sản chưa hỏi thai kỳ/cho con bú (căn cứ hồ sơ).

Bám lời thoại (28/11/2026): gợi ý chỉ bật khi CHÍNH LỜI bệnh nhân/người nhà của ca khám nhắc
tới triệu chứng hoặc thuốc: khớp nguyên từ ("ho" không khớp "cho", "thoải"), bỏ câu phủ định
("không sốt"), bỏ câu hỏi của bác sĩ, bỏ lời của "người khác". Mỗi gợi ý mang `luot_dan` và
`trich_dan` là lượt nói làm căn cứ để bác sĩ thấy vì sao hệ thống hỏi. Gợi ý thai kỳ dựa trên
hồ sơ (giới, tuổi) và ghi nguồn "hồ sơ".
"""

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional, Tuple


# ═══ class GoiYLamSang — Một câu hỏi gợi ý cho bác sĩ để lấp khoảng trống ═════════════
# Có chủ đề, mức ưu tiên, khoảng trống, câu hỏi, lựa chọn nhanh, lý do và căn cứ (lượt nói).
@dataclass
class GoiYLamSang:
    ma_goi_y: str
    chu_de: str              # ĐAU, SỐT, HÔ_HẤP, THUỐC, THAI_KỲ, TIỀN_SỬ
    muc_do_uu_tien: str      # CAO, TRUNG_BINH, KHUYEN_NGHI
    khoang_trong: str        # Mô tả thông tin đang bị khuyết thiếu
    cau_hoi_goi_y: str       # Câu hỏi đề xuất cho bác sĩ (ngắn)
    cac_lua_chon: List[str]  # Các nhãn gợi ý nhanh cho UI
    ly_do_y_khoa: str        # Giải thích tại sao cần hỏi thông tin này
    luot_dan: List[int] = field(default_factory=list)  # Số lượt nói làm căn cứ (đếm từ 1)
    trich_dan: str = ""      # Đoạn lời thoại hoặc hồ sơ làm căn cứ
    nguon: str = ""          # "lời bệnh nhân", "lời người nhà", "lời người bệnh", "hồ sơ"


# ═══ class KetQuaTroLyLamSang — Tập gợi ý và mức đầy đủ của bệnh án ═══════════════════
@dataclass
class KetQuaTroLyLamSang:
    danh_sach_goi_y: List[GoiYLamSang] = field(default_factory=list)
    tong_so_khoang_trong: int = 0
    muc_do_day_du_benh_an: float = 1.0  # Từ 0.0 đến 1.0


_VAI_KHAI = {"bệnh nhân": "lời bệnh nhân", "người bệnh": "lời bệnh nhân",
             "người nhà": "lời người nhà"}
_VAI_BIET = {"bác sĩ", "điều dưỡng", "người khác", "bệnh nhân", "người bệnh", "người nhà"}
_PHU_DINH_TRUOC = re.compile(r"(?:^|\W)(?:không|chưa|hết|chẳng|ko)(?:\s+\w+){0,2}\s*$", re.I)


def _tach_luot(hoi_thoai: str) -> List[Tuple[int, str, str]]:
    """-> [(so_luot, vai_viet_thuong, noi_dung)]. Dòng không có vai -> vai ''."""
    ra = []
    for i, dong in enumerate(d for d in (hoi_thoai or "").split("\n") if d.strip()):
        m = re.match(r"^\s*([^:\n]{1,20}):\s*(.*)$", dong)
        if m and m.group(1).strip().lower() in _VAI_BIET:
            ra.append((i + 1, m.group(1).strip().lower(), m.group(2).strip()))
        else:
            ra.append((i + 1, "", dong.strip()))
    return ra


def _mau_tu(tu: str) -> "re.Pattern[str]":
    return re.compile(r"(?<!\w)" + re.escape(tu) + r"(?!\w)", re.I)


def _co_tu(van_ban: str, cac_tu) -> bool:
    return any(_mau_tu(t).search(van_ban) for t in cac_tu)


def _trich_quanh(noi_dung: str, vi_tri: int, do_dai: int = 70) -> str:
    """Lấy vế câu chứa vị trí khớp, cắt ngắn."""
    dau = max(noi_dung.rfind(c, 0, vi_tri) for c in ".,;!?") + 1
    cuoi = min([c for c in (noi_dung.find(x, vi_tri) for x in ".;!?") if c != -1] or [len(noi_dung)])
    doan = noi_dung[dau:cuoi].strip()
    return doan if len(doan) <= do_dai else doan[:do_dai].rstrip() + "…"


# Người nhà kể về CHÍNH MÌNH ("còn tôi thì bị…", "tôi cũng đang uống…") — không phải bệnh nhân.
_NGUOI_NHA_TU_KE = re.compile(r"(?:^|\W)(?:còn\s+)?(?:tôi|em|mình|tui)\s+(?:thì\s+|cũng\s+)?"
                              r"(?:bị|có|đang|hay|từng)(?!\w)", re.I)


def _ve_cau(noi_dung: str, vi_tri: int) -> str:
    dau = max(noi_dung.rfind(c, 0, vi_tri) for c in ".;!?") + 1
    cuoi = min([c for c in (noi_dung.find(x, vi_tri) for x in ".;!?") if c != -1] or [len(noi_dung)])
    return noi_dung[dau:cuoi]


def _tim_can_cu(luot, cac_tu, bo_neu_cau_co=()) -> Optional[Tuple[int, str, str]]:
    """Lượt ĐẦU TIÊN của bệnh nhân/người nhà nhắc một từ trong `cac_tu` ở dạng khẳng định.

    Bỏ qua: câu phủ định ngay trước từ khoá; câu người nhà kể về chính mình; câu chứa một
    cụm trong `bo_neu_cau_co` (vd "dị ứng" khi tìm tên thuốc đang dùng).
    -> (so_luot, trich_dan, nguon) hoặc None. Khi hội thoại không ghi vai (một khối văn bản),
    mọi dòng được xét như lời người bệnh.
    """
    co_vai = any(v for _, v, _ in luot)
    for so, vai, nd in luot:
        if co_vai and vai not in _VAI_KHAI:
            continue
        for t in cac_tu:
            for m in _mau_tu(t).finditer(nd):
                if _PHU_DINH_TRUOC.search(nd[:m.start()]):
                    continue
                cau = _ve_cau(nd, m.start())
                if vai == "người nhà" and _NGUOI_NHA_TU_KE.search(cau):
                    continue
                if bo_neu_cau_co and _co_tu(cau, bo_neu_cau_co):
                    continue
                return so, _trich_quanh(nd, m.start()), _VAI_KHAI.get(vai, "lời người bệnh")
    return None


def _noi_dung_phat_bieu(p: Any) -> str:
    if isinstance(p, dict):
        return str(p.get("noi_dung", ""))
    return str(getattr(p, "noi_dung", p))


# ═══ class ActiveClinicalClarificationAgent — Tìm thông tin còn thiếu và gợi ý câu hỏi cho bác sĩ ═══
# Chỉ gợi ý khi lời bệnh nhân/người nhà thật sự nhắc tới vấn đề. Chỉ là gợi ý.
class ActiveClinicalClarificationAgent:
    """Phát hiện khoảng trống bệnh sử từ lời thoại của chính ca khám."""

    @classmethod
    def phan_tich_khoang_trong(
        cls,
        hoi_thoai: str,
        danh_sach_phat_bieu: Optional[List[Any]] = None,
        thong_tin_benh_nhan: Optional[Dict[str, Any]] = None
    ) -> KetQuaTroLyLamSang:
        luot = _tach_luot(hoi_thoai)
        # "Đã có chưa" xét trên toàn bộ hội thoại (mọi vai) và mệnh đề đã trích.
        da_co = " \n".join([nd for _, _, nd in luot] +
                           [_noi_dung_phat_bieu(p) for p in (danh_sach_phat_bieu or [])])

        goi_y_list: List[GoiYLamSang] = []

        def them(can_cu, **k):
            so, trich, nguon = can_cu
            goi_y_list.append(GoiYLamSang(luot_dan=[so], trich_dan=trich, nguon=nguon, **k))

        # 1. ĐAU
        cc_dau = _tim_can_cu(luot, ["đau bụng", "đau ngực", "đau đầu", "đau lưng", "đau khớp"])
        if cc_dau:
            cc_bung = _tim_can_cu(luot, ["đau bụng"])
            if cc_bung and not _co_tu(da_co, ["thượng vị", "hạ sườn", "quanh rốn", "hố chậu", "hạ vị",
                                              "mỏ ác", "trên rốn", "dưới rốn"]):
                them(cc_bung, ma_goi_y="GAP_DAU_VI_TRI_BUNG", chu_de="ĐAU", muc_do_uu_tien="CAO",
                     khoang_trong="Có đau bụng nhưng chưa rõ vị trí.",
                     cau_hoi_goi_y="Đau chỗ nào nhất trong bụng?",
                     cac_lua_chon=["Thượng vị", "Hố chậu phải", "Quanh rốn", "Hạ vị", "Khắp bụng"],
                     ly_do_y_khoa="Vị trí đau giúp phân biệt bệnh ngoại khoa cấp với nội khoa.")
            if not _co_tu(da_co, ["quặn", "âm ỉ", "nhói", "như dao đâm", "từng cơn", "bỏng rát",
                                  "căng tức", "rát", "thắt"]):
                them(cc_dau, ma_goi_y="GAP_DAU_TINH_CHAT", chu_de="ĐAU", muc_do_uu_tien="TRUNG_BINH",
                     khoang_trong="Chưa rõ tính chất cơn đau.",
                     cau_hoi_goi_y="Đau quặn từng cơn hay âm ỉ liên tục?",
                     cac_lua_chon=["Quặn từng cơn", "Âm ỉ liên tục", "Nhói", "Rát bỏng"],
                     ly_do_y_khoa="Tính chất đau định hướng cơ chế gây đau.")
            cc_nguc = _tim_can_cu(luot, ["đau ngực"])
            if cc_nguc and not _co_tu(da_co, ["lan lên", "lan ra", "lan xuống", "lan sang", "không lan"]):
                them(cc_nguc, ma_goi_y="GAP_DAU_NGUC_HUONG_LAN", chu_de="ĐAU", muc_do_uu_tien="CAO",
                     khoang_trong="Đau ngực chưa rõ hướng lan.",
                     cau_hoi_goi_y="Đau ngực có lan lên cằm, xuống tay trái hay ra sau lưng không?",
                     cac_lua_chon=["Lan tay trái", "Lan sau lưng", "Lan cằm/cổ", "Không lan"],
                     ly_do_y_khoa="Sàng lọc hội chứng mạch vành cấp và lóc tách động mạch chủ.")

        # 2. SỐT
        cc_sot = _tim_can_cu(luot, ["sốt"])
        if cc_sot:
            if not re.search(r"(?<!\d)(?:3[6-9]|4[0-2])(?:[.,]\d)?\s*(?:độ|°c|°)", da_co, re.I):
                them(cc_sot, ma_goi_y="GAP_SOT_NHIET_DO", chu_de="SỐT", muc_do_uu_tien="TRUNG_BINH",
                     khoang_trong="Có sốt nhưng chưa có nhiệt độ đo được.",
                     cau_hoi_goi_y="Đo được cao nhất bao nhiêu độ?",
                     cac_lua_chon=["37,5–38°C", "38,5–39°C", "Trên 39°C", "Chưa đo"],
                     ly_do_y_khoa="Mức sốt giúp phân tầng nguy cơ nhiễm trùng.")
            if not _co_tu(da_co, ["rét run", "ớn lạnh", "lạnh run", "rét"]):
                them(cc_sot, ma_goi_y="GAP_SOT_RET_RUN", chu_de="SỐT", muc_do_uu_tien="TRUNG_BINH",
                     khoang_trong="Chưa hỏi rét run kèm sốt.",
                     cau_hoi_goi_y="Sốt có kèm rét run không?",
                     cac_lua_chon=["Rét run", "Chỉ ớn lạnh", "Không rét run"],
                     ly_do_y_khoa="Rét run gợi ý nhiễm khuẩn huyết hoặc nhiễm khuẩn đường mật.")

        # 3. HO
        cc_ho = _tim_can_cu(luot, ["ho"])
        if cc_ho and not _co_tu(da_co, ["ho khan", "ho đờm", "có đờm", "khạc đờm", "đờm", "ho ra máu"]):
            them(cc_ho, ma_goi_y="GAP_HO_TINH_CHAT_DOM", chu_de="HÔ_HẤP", muc_do_uu_tien="TRUNG_BINH",
                 khoang_trong="Chưa rõ ho khan hay có đờm.",
                 cau_hoi_goi_y="Ho khan hay có đờm? Đờm màu gì?",
                 cac_lua_chon=["Ho khan", "Đờm trắng trong", "Đờm vàng/xanh", "Đờm lẫn máu"],
                 ly_do_y_khoa="Phân biệt nhiễm virus với bội nhiễm vi khuẩn.")

        # 4. THUỐC chưa rõ hàm lượng
        for thuoc in ["amlodipin", "losartan", "metformin", "gliclazide", "atorvastatin", "paracetamol", "aspirin"]:
            cc_thuoc = _tim_can_cu(luot, [thuoc], bo_neu_cau_co=["dị ứng"])
            if not cc_thuoc:
                continue
            if re.search(r"(?<!\w)" + thuoc + r"\w*[^\n.]{0,25}?\d+(?:[.,]\d+)?\s*(?:mg|g|viên)", da_co, re.I):
                continue
            ten = thuoc.capitalize()
            them(cc_thuoc, ma_goi_y=f"GAP_THUOC_HAM_LUONG_{thuoc.upper()}", chu_de="THUỐC",
                 muc_do_uu_tien="CAO",
                 khoang_trong=f"Có dùng {ten} nhưng chưa rõ hàm lượng và liều.",
                 cau_hoi_goi_y=f"{ten} viên bao nhiêu mg, ngày uống mấy viên?",
                 cac_lua_chon=[f"{ten} 1 viên/ngày", f"{ten} 2 viên/ngày", "Không nhớ, có mang vỏ thuốc"],
                 ly_do_y_khoa=f"Cần liều {ten} chính xác để đánh giá điều trị và tránh quá liều.")

        # 5. THAI KỲ — căn cứ là HỒ SƠ (giới, tuổi), không phải lời thoại
        ttbn = thong_tin_benh_nhan or {}
        gioi_tinh = str(ttbn.get("gioi_tinh", "")).lower()
        try:
            tuoi = int(ttbn.get("tuoi") or 0)
        except (TypeError, ValueError):
            tuoi = 0
        la_nu = "nữ" in gioi_tinh or gioi_tinh in ("nu", "f", "female")
        if la_nu and 15 <= tuoi <= 49 and not _co_tu(
                da_co, ["mang thai", "có bầu", "có thai", "thai kỳ", "kinh nguyệt", "trễ kinh", "cho con bú"]):
            goi_y_list.append(GoiYLamSang(
                ma_goi_y="GAP_NU_THAI_KY", chu_de="THAI_KỲ", muc_do_uu_tien="CAO",
                khoang_trong="Nữ tuổi sinh sản, chưa hỏi thai kỳ/cho con bú.",
                cau_hoi_goi_y="Có đang mang thai, trễ kinh hay cho con bú không?",
                cac_lua_chon=["Không", "Đang mang thai", "Đang cho con bú", "Trễ kinh, chưa thử"],
                ly_do_y_khoa="Ảnh hưởng chỉ định thuốc và chụp X-quang/CT.",
                trich_dan=f"Hồ sơ: nữ, {tuoi} tuổi", nguon="hồ sơ"))

        so_khoang_trong = len(goi_y_list)
        do_day_du = max(0.0, round(1.0 - (so_khoang_trong * 0.15), 2))
        return KetQuaTroLyLamSang(
            danh_sach_goi_y=goi_y_list,
            tong_so_khoang_trong=so_khoang_trong,
            muc_do_day_du_benh_an=do_day_du,
        )
