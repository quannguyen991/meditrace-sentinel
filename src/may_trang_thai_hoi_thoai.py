# -*- coding: utf-8 -*-
"""Máy trạng thái hội thoại (Conversational FSM) & Giải quyết ngữ pháp tỉnh lược chủ ngữ (Pro-Drop Syntax).

Trục 2 của MediTrace:
- Xử lý hiện tượng tỉnh lược chủ ngữ (Pro-Drop / Zero Anaphora) đặc thù của tiếng Việt lâm sàng.
- Phân biệt chính xác Người trải nghiệm (Experiencer Detection): Bệnh nhân vs Người nhà kể hộ vs Bác sĩ.
- Máy trạng thái hữu hạn (FSM) quản lý tự sửa lỗi (Self-Correction / Conversational Repair):
  + Đính chính (Correction / Supersession): Chuyển bản ghi cũ sang 'bị thay thế' (giữ vết kiểm toán,
    không vào thân bệnh án, loại trừ K7).
  + Diễn biến (Evolution): Giữ cả hai trạng thái lâm sàng theo mốc thời gian.
  + Mâu thuẫn (Contradiction): Giữ lại chuyển sang 'cần xác nhận', tuyệt đối không âm thầm xóa dữ liệu.
- Hoàn toàn tương thích và mở rộng `src.cap_nhat` và `src.khoa_bang_chung`.
"""
from dataclasses import asdict, dataclass, field
import enum
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from src import cap_nhat, chuan_hoa, thuc_the
from src.phat_bieu import PhatBieu, QUAN_HE, TRANG_THAI


# ==============================================================================
# 1. TRẠNG THÁI FSM VÀ MỐI QUAN HỆ HỘI THOẠI
# ==============================================================================

class TrangThaiFSM(str, enum.Enum):
    CON_HIEU_LUC = "còn hiệu lực"
    BI_THAY_THE = "bị thay thế"
    CHUA_GIAI_QUYET = "chưa giải quyết"
    GIA_DINH = "giả định"


class QuanHeHoiThoai(str, enum.Enum):
    BO_SUNG = "bổ sung"
    DINH_CHINH = "đính chính"
    DIEN_BIEN = "diễn biến"
    MAU_THUAN = "mâu thuẫn"


# ==============================================================================
# 2. XỬ LÝ TỈNH LƯỢC CHỦ NGỮ (VIETNAMESE PRO-DROP / EXPERIENCER RESOLVER)
# ==============================================================================

class BoGiaiQuyetProDrop:
    """Bộ giải quyết tỉnh lược chủ ngữ và xác định người trải nghiệm triệu chứng."""

    # Từ chỉ bệnh nhân rõ ràng (bao gồm phương ngữ 3 miền)
    TU_BENH_NHAN = (
        "bé nhà em", "con nhà em", "cháu nó", "nhà em", "em bé", "bé",
        "ông ấy", "bà ấy", "anh ấy", "chị ấy", "bệnh nhân", "trẻ",
        "bé nhà tôi", "con nhà tôi", "cháu nhà em", "cháu nhà tôi",
        "cháu tôi", "con tôi", "con em", "nhà tôi", "ông nhà tôi",
        "bà nhà tôi", "cô ấy", "chú ấy", "bác ấy", "em ấy",
        "thằng nhỏ", "mấy nhỏ", "con bé", "bé út", "ổng", "bả", "bác trai", "bác gái", "cụ nhà em"
    )

    # Từ tự xưng rõ của người nói (3 miền Bắc, Trung, Nam)
    TU_TU_XUNG = ("tôi", "tui", "mình", "tớ", "qua", "mềnh")

    # Mối quan hệ họ hàng
    TU_HO_HANG = (
        "con trai", "con gái", "anh trai", "chị gái", "em trai", "em gái",
        "ông nội", "bà nội", "ông ngoại", "bà ngoại", "mẹ", "bố", "cha",
        "chồng", "vợ", "bà"
    )

    # Từ ghép có chữ 'mình' nhưng KHÔNG PHẢI đại từ tự xưng
    MINH_KHONG_PHAI_TU_XUNG = (
        "trở mình", "giật mình", "rùng mình", "cựa mình", "mình mẩy",
        "nóng mình", "một mình", "khắp mình"
    )

    # Dấu hiệu đính chính tức thì trong câu
    DAU_HIEU_DINH_CHINH = re.compile(
        r"(?<!\w)("
        r"à không|nhầm|nói nhầm|nhớ nhầm|nhầm rồi|à quên|"
        r"đúng ra là|chính xác là|ý tôi là|không phải|"
        r"nhớ lại rồi|nói lại cho đúng"
        r")(?!\w)",
        re.I
    )

    # Dấu hiệu diễn biến theo thời gian
    DAU_HIEU_DIEN_BIEN = re.compile(
        r"(?<!\w)("
        r"hôm qua.*?hôm nay|"
        r"ban đầu.*?sau đó|"
        r"lúc đầu.*?bây giờ|"
        r"mấy hôm trước.*?đến nay|"
        r"sau khi uống.*?thì đỡ|"
        r"đỡ hơn|thuyên giảm|nặng hơn|tăng dần"
        r")(?!\w)",
        re.I
    )

    def __init__(self):
        self.chu_the_hien_tai: int = 0
        self.nguoi_noi_truoc: Optional[str] = None
        self.nguoi_nha_ke_ho: bool = False

    def phan_tich_luot(
        self,
        vai: str,
        van_ban: str,
        chu_the_id_de_xuat: Optional[int] = None
    ) -> Tuple[int, str]:
        """Xác định chủ thể đích thực (chu_the_id) khi gặp câu khuyết chủ ngữ.
        
        Trả về: (chu_the_id, giai_thich)
        - 0: Bệnh nhân chính
        - >0: Người khác (người nhà, người đi cùng)
        """
        thap = van_ban.lower().strip()
        vai_chuan = (vai or "").lower().strip()

        # 1. Trường hợp người nói là Bác sĩ: Khuyết chủ ngữ luôn mặc định nói về Bệnh nhân
        if vai_chuan == "bác sĩ":
            self.nguoi_noi_truoc = "bác sĩ"
            return 0, "bác sĩ hỏi/nhận định về bệnh nhân"

        # 2. Trường hợp người nói là Bệnh nhân: Khuyết chủ ngữ mặc định là chính họ
        if vai_chuan in ("bệnh nhân", "người bệnh"):
            self.nguoi_noi_truoc = "bệnh nhân"
            # Kiểm tra xem có nhắc người nhà không
            for hh in self.TU_HO_HANG:
                if re.search(rf"\b{hh}\s+(tôi|tui|mình|em)\b", thap):
                    return 1, f"bệnh nhân nhắc đến người thân ({hh})"
            return 0, "bệnh nhân tự mô tả triệu chứng của mình"

        # 3. Trường hợp người nói là Người nhà
        if vai_chuan == "người nhà":
            self.nguoi_noi_truoc = "người nhà"

            # Kiểm tra cụm từ ghép có 'mình' nhưng không phải đại từ tự xưng
            co_minh_khong_tu_xung = any(mk in thap for mk in self.MINH_KHONG_PHAI_TU_XUNG)

            # Kiểm tra cụm chỉ họ hàng xa/người thân khác (anh trai, chị gái, ông bà...)
            if re.search(r"\b(anh trai|chị gái|em trai|em gái|ông nội|bà nội|ông ngoại|bà ngoại)\b", thap):
                return 1, "người nhà nhắc đến người thân khác trong gia đình"

            # Ưu tiên kiểm tra người nhà tự xưng làm vị ngữ/chủ ngữ ("tôi thì", "tôi cũng", "tôi bị", "tui...")
            # Chú ý: Trừ trường hợp sở hữu như "ông nhà tôi bị", "cháu nhà tôi bị", "con tôi bị"...
            mau_tu_xung_chu_ngu = re.compile(
                r"(?<!nhà\s)(?<!con\s)(?<!cháu\s)(?<!bé\s)(?<!ông\s)(?<!bà\s)(?<!em\s)(?<!của\s)(tôi|tui|mình|tớ|qua|mềnh)\s+(thì|cũng|bị|đang|đã|uống|đau|sốt|khám|điều trị|thấy)\b",
                re.I
            )
            if mau_tu_xung_chu_ngu.search(thap) and not (co_minh_khong_tu_xung and "mình" in thap and not any(t in thap for t in ("tôi", "tui", "tớ", "qua", "mềnh"))):
                return 1, "người nhà tự xưng kể về bản thân họ"

            # Kiểm tra cụm chỉ rõ bệnh nhân
            for bn in self.TU_BENH_NHAN:
                if re.search(rf"(?<!\w){re.escape(bn)}(?!\w)", thap):
                    self.nguoi_nha_ke_ho = True
                    return 0, f"người nhà dùng danh từ chỉ rõ bệnh nhân ({bn})"

            # Kiểm tra từ tự xưng rõ thông thường
            co_tu_xung = False
            for tx in self.TU_TU_XUNG:
                if re.search(rf"(?<!\w){re.escape(tx)}(?!\w)", thap):
                    if not co_minh_khong_tu_xung or tx != "mình":
                        co_tu_xung = True
                        break

            # Nếu người nhà dùng từ tự xưng ("Tôi thì bị...") -> Chủ thể là Người nhà (1)
            if co_tu_xung:
                return 1, "người nhà tự xưng kể về bản thân họ"

            # Nếu câu khuyết chủ ngữ ("Sốt từ tối qua, nôn 2 lần"):
            # Nếu trước đó người nhà đã xác lập ngữ cảnh kể hộ bệnh nhân -> Thuộc về Bệnh nhân
            if self.nguoi_nha_ke_ho:
                return 0, "kế thừa ngữ cảnh người nhà kể hộ cho bệnh nhân"

            # Mặc định an toàn cho khuyết chủ ngữ
            return 0, "mặc định lâm sàng cho bệnh nhân"

        return chu_the_id_de_xuat if chu_the_id_de_xuat is not None else 0, "mặc định"


# ==============================================================================
# 3. MÁY TRẠNG THÁI HỮU HẠN QUẢN LÝ TỰ SỬA LỖI & ĐÍNH CHÍNH (REPAIR FSM)
# ==============================================================================

@dataclass
class SuKienChuyenTrangThai:
    id_moi: int
    id_cu: Optional[int]
    quan_he: str
    trang_thai_truoc: Optional[str]
    trang_thai_sau: str
    ly_do: str


class MayTrangThaiHoiThoai:
    """FSM quản lý vòng đời và tính nhất quán của tập mệnh đề lâm sàng."""

    def __init__(self):
        self.danh_sach: List[PhatBieu] = []
        self.lich_su_chuyen: List[SuKienChuyenTrangThai] = []

    def them_phat_bieu(self, pb: PhatBieu) -> PhatBieu:
        """Thêm một phát biểu mới vào FSM và cập nhật lại trạng thái mạng lưới."""
        ban_sao = PhatBieu(**pb.to_dict())
        self.danh_sach.append(ban_sao)
        self._cap_nhat_trang_thai_cho_moi_nhat()
        return ban_sao

    def _cung_nguoi_noi(self, p1: PhatBieu, p2: PhatBieu) -> bool:
        """Kiểm tra hai phát biểu có xuất phát từ cùng một người nói hay không."""
        return (p1.nguoi_noi or "").lower().strip() == (p2.nguoi_noi or "").lower().strip()

    def _cap_nhat_trang_thai_cho_moi_nhat(self):
        """Thực thi luật chuyển trạng thái xác định MediTrace."""
        theo_id = {p.id: p for p in self.danh_sach}

        for p in self.danh_sach:
            if not p.quan_he:
                continue

            truoc = theo_id.get(p.quan_he_voi)
            if truoc is None:
                p.trang_thai = TrangThaiFSM.CHUA_GIAI_QUYET.value
                self.lich_su_chuyen.append(
                    SuKienChuyenTrangThai(
                        id_moi=p.id,
                        id_cu=None,
                        quan_he=p.quan_he,
                        trang_thai_truoc=None,
                        trang_thai_sau=p.trang_thai,
                        ly_do="quan_he_voi_khong_ton_tai"
                    )
                )
                continue

            # 1. Bổ sung: Cả hai cùng còn hiệu lực
            if p.quan_he == QuanHeHoiThoai.BO_SUNG.value:
                p.trang_thai = TrangThaiFSM.CON_HIEU_LUC.value
                truoc.trang_thai = TrangThaiFSM.CON_HIEU_LUC.value

            # 2. Đính chính (Self-repair vs Cross-speaker conflict)
            elif p.quan_he == QuanHeHoiThoai.DINH_CHINH.value:
                # Nếu cùng một người nói đính chính lại lời của chính mình (Tự sửa lỗi)
                if self._cung_nguoi_noi(p, truoc):
                    tt_truoc = truoc.trang_thai
                    truoc.trang_thai = TrangThaiFSM.BI_THAY_THE.value
                    p.trang_thai = TrangThaiFSM.CON_HIEU_LUC.value
                    self.lich_su_chuyen.append(
                        SuKienChuyenTrangThai(
                            id_moi=p.id,
                            id_cu=truoc.id,
                            quan_he="đính chính",
                            trang_thai_truoc=tt_truoc,
                            trang_thai_sau=truoc.trang_thai,
                            ly_do="nguoi_noi_tu_dinh_chinh"
                        )
                    )
                else:
                    # Khác người nói: Biến thành mâu thuẫn nguồn, không tự ý ghi đè
                    p.quan_he = QuanHeHoiThoai.MAU_THUAN.value
                    truoc.trang_thai = TrangThaiFSM.CHUA_GIAI_QUYET.value
                    p.trang_thai = TrangThaiFSM.CHUA_GIAI_QUYET.value
                    self.lich_su_chuyen.append(
                        SuKienChuyenTrangThai(
                            id_moi=p.id,
                            id_cu=truoc.id,
                            quan_he="mâu thuẫn nguồn",
                            trang_thai_truoc=truoc.trang_thai,
                            trang_thai_sau=TrangThaiFSM.CHUA_GIAI_QUYET.value,
                            ly_do="hai_nguon_mau_thuan_chuyen_can_xac_nhan"
                        )
                    )

            # 3. Diễn biến: Cả hai cùng còn hiệu lực nhưng khác mốc thời gian
            elif p.quan_he == QuanHeHoiThoai.DIEN_BIEN.value:
                truoc.trang_thai = TrangThaiFSM.CON_HIEU_LUC.value
                p.trang_thai = TrangThaiFSM.CON_HIEU_LUC.value

            # 4. Mâu thuẫn: Cả hai hạ xuống chưa giải quyết
            elif p.quan_he == QuanHeHoiThoai.MAU_THUAN.value:
                truoc.trang_thai = TrangThaiFSM.CHUA_GIAI_QUYET.value
                p.trang_thai = TrangThaiFSM.CHUA_GIAI_QUYET.value

    def lay_danh_sach_hieu_luc(self) -> List[PhatBieu]:
        """Chỉ trả về các mệnh đề hợp lệ để sinh bệnh án chính thức (Layer 5)."""
        return [p for p in self.danh_sach if p.trang_thai == TrangThaiFSM.CON_HIEU_LUC.value]

    def lay_danh_sach_can_xac_nhan(self) -> List[PhatBieu]:
        """Các mệnh đề cần bác sĩ xem xét: Mâu thuẫn hoặc Giả định."""
        return [
            p for p in self.danh_sach
            if p.trang_thai == TrangThaiFSM.CHUA_GIAI_QUYET.value
            or p.tinh_huong != "thực tế"
        ]

    def lay_danh_sach_bi_thay_the(self) -> List[PhatBieu]:
        """Các mệnh đề đã bị đính chính: Lưu trữ cho chuỗi kiểm toán WORM."""
        return [p for p in self.danh_sach if p.trang_thai == TrangThaiFSM.BI_THAY_THE.value]

    def lay_lich_su_dinh_chinh_kem_am_thanh(self) -> List[Dict[str, Any]]:
        """Lấy danh sách các cặp đính chính (Bản cũ bị thay thế + Bản mới)
        kèm đầy đủ audio_spans phục vụ Click-to-Verify trên giao diện bác sĩ.
        """
        theo_id = {p.id: p for p in self.danh_sach}
        ket_qua = []
        for p in self.danh_sach:
            if p.quan_he == QuanHeHoiThoai.DINH_CHINH.value and p.quan_he_voi in theo_id:
                truoc = theo_id[p.quan_he_voi]
                ket_qua.append({
                    "id_moi": p.id,
                    "id_cu": truoc.id,
                    "noi_dung_moi": p.noi_dung,
                    "noi_dung_cu": truoc.noi_dung,
                    "trang_thai_moi": p.trang_thai,
                    "trang_thai_cu": truoc.trang_thai,
                    "nguoi_noi": p.nguoi_noi,
                    "audio_spans_moi": getattr(p, "audio_spans", []),
                    "audio_spans_cu": getattr(truoc, "audio_spans", []),
                })
        return ket_qua

    def lay_danh_sach_mau_thuan_kem_am_thanh(self) -> List[Dict[str, Any]]:
        """Lấy danh sách các mâu thuẫn giữa các người nói (Cross-speaker conflicts)
        chuyển sang 'CẦN XÁC NHẬN', không xóa dữ liệu nào.
        """
        theo_id = {p.id: p for p in self.danh_sach}
        ket_qua = []
        for p in self.danh_sach:
            if p.trang_thai == TrangThaiFSM.CHUA_GIAI_QUYET.value:
                doi_lap = theo_id.get(p.quan_he_voi) if p.quan_he_voi is not None else None
                ket_qua.append({
                    "id": p.id,
                    "noi_dung": p.noi_dung,
                    "nguoi_noi": p.nguoi_noi,
                    "chu_the_id": p.chu_the_id,
                    "audio_spans": getattr(p, "audio_spans", []),
                    "doi_lap_id": doi_lap.id if doi_lap else None,
                    "doi_lap_noi_dung": doi_lap.noi_dung if doi_lap else None,
                    "doi_lap_audio_spans": getattr(doi_lap, "audio_spans", []) if doi_lap else [],
                })
        return ket_qua


def kiem_tra_l2_sang_l3(pb: PhatBieu) -> Tuple[bool, List[str]]:
    """Kiểm tra cửa ngõ giữa Layer 2 (Trích xuất) và Layer 3 (Máy trạng thái FSM).
    
    Phát hiện và ngăn chặn ngay lập tức:
    1. Gán nhầm chủ thể: Người nhà tự kể về bản thân nhưng gán chu_the_id = 0.
    2. Nguồn phát ngôn mơ hồ: vai người nói unknown hoặc không xác định.
    3. Trạng thái đính chính không có căn cứ.
    """
    loi = []
    
    # 1. Kiểm tra vai người nói
    role = (pb.nguoi_noi or "").strip().lower()
    if role in ("unknown", "chưa rõ", ""):
        loi.append("nguoi_noi_khong_xac_dinh")

    # 2. Kiểm tra chủ thể và đại từ tự xưng
    if role == "người nhà" and pb.chu_the_id == 0:
        van_trich = " ".join(pb.trich_dan).lower()
        if re.search(r"(?<!\w)(tôi|tui|mình|tớ|qua|mềnh)\s+(thì|cũng|bị|đang|đã|uống|đau|sốt)\b", van_trich):
            loi.append("chu_the_nguoi_ke: Người nhà tự kể về bản thân không được gán cho bệnh nhân (chu_the_id=0)")

    # 3. Kiểm tra tính toàn vẹn của quan_he
    if pb.quan_he in (QuanHeHoiThoai.DINH_CHINH.value, QuanHeHoiThoai.MAU_THUAN.value, QuanHeHoiThoai.DIEN_BIEN.value):
        if pb.quan_he_voi is None:
            loi.append(f"quan_he '{pb.quan_he}' thiếu trường tham chiếu 'quan_he_voi'")

    return len(loi) == 0, loi


# ==============================================================================
# 4. HÀM WRAPPER XỬ LÝ TOÀN DIỆN CHO DUONG ONG
# ==============================================================================

def ap_dung_may_trang_thai(danh_sach: List[PhatBieu]) -> List[PhatBieu]:
    """Áp dụng FSM lên toàn bộ danh sách mệnh đề, trả về danh sách đã cập nhật trạng thái."""
    fsm = MayTrangThaiHoiThoai()
    for p in danh_sach:
        fsm.them_phat_bieu(p)
    return fsm.danh_sach
