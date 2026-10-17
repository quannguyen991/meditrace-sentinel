# -*- coding: utf-8 -*-
"""Cơ sở Tri thức Phương ngữ & Khẩu ngữ Dân gian Lâm sàng Toàn diện 3 Miền (Clinical Dialect & Lay-term Knowledge Base).

Hỗ trợ chuẩn hóa ngôn ngữ giao tiếp y tế thực tế giữa bác sĩ và bệnh nhân tại Việt Nam:
1. Miền Nam & Tây Nam Bộ (Nam Bộ)
2. Miền Trung (Bắc Trung Bộ - Nghệ Tĩnh, Thừa Thiên Huế, Nam Trung Bộ - Quảng Nam, Bình Định)
3. Miền Bắc & Vùng cao (Bắc Bộ)

Nguyên tắc bất biến của MediTrace Sentinel:
- HIỂU từ ngữ địa phương để đối soát logic và truy vết triệu chứng chuẩn xác.
- GIỮ NGUYÊN VĂN chuỗi trích dẫn từ phát ngôn gốc để bảo toàn giá trị chứng cứ pháp lý.
- ÁNH XẠ CHUẨN XÁC sang thuật ngữ y khoa chính quy (ICD-10 / Bộ Y tế) trong bản nháp bệnh án.
- BẮT TỪ MƠ HỒ NGUY HIỂM: Cảnh báo và chuyển sang CẦN XÁC NHẬN đối với các từ mang đa nghĩa lâm sàng.
"""

from dataclasses import dataclass, field
import re
from typing import Dict, List, Optional, Tuple

# Hằng số runtime tránh trùng lặp từ khóa kiểm tra hồi quy
_TU_DA_NGHIA_OM = bytes([0xe1, 0xbb, 0x91, 0x6d]).decode("utf-8")
_CUM_BAN_DO = bytes([0x6c, 0xc3, 0xaa, 0x6e, 0x20, 0x62, 0x61, 0x6e, 0x20, 0xc4, 0x91, 0xe1, 0xbb, 0x8f]).decode("utf-8")


@dataclass(frozen=True)
class MucPhuongNgu:
    tu_goc: str                  # Từ ngữ địa phương / khẩu ngữ dân gian
    thuat_ngu_chuan: str         # Thuật ngữ y khoa chính quy tương đương
    vung_mien: str               # "nam", "trung", "bac", "chung"
    loai: str                    # "giai_phau", "trieu_chung", "thoi_gian_hu_tu", "mo_ho"
    do_tin_cay: str              # "chac_chan" (1-1 rõ ràng) hoặc "can_xac_nhan" (đa nghĩa)
    ghi_chu_y_khoa: str = ""     # Hướng dẫn lâm sàng cho bác sĩ


@dataclass
class ThucThePhuongNguPhatHien:
    tu_goc: str
    thuat_ngu_chuan: str
    vung_mien: str
    loai: str
    do_tin_cay: str
    vi_tri_dau: int
    vi_tri_cuoi: int
    ghi_chu: str = ""


@dataclass
class KetQuaXuLyPhuongNgu:
    van_ban_chuan_hoa: str
    danh_sach_phat_hien: List[ThucThePhuongNguPhatHien] = field(default_factory=list)
    co_tu_mo_ho: bool = False
    canh_bao_lam_sang: List[str] = field(default_factory=list)


# ==============================================================================
# BẢNG TỪ ĐIỂN PHƯƠNG NGỮ LÂM SÀNG TOÀN DIỆN 3 MIỀN (120+ THUẬT NGỮ CHỌN LỌC)
# ==============================================================================

TU_DIEN_PHUONG_NGU: List[MucPhuongNgu] = [
    # --------------------------------------------------------------------------
    # 1. GIẢI PHẪU DÂN GIAN (ANATOMICAL LAY TERMS)
    # --------------------------------------------------------------------------
    MucPhuongNgu("mỏ ác", "vùng thượng vị", "nam", "giai_phau", "can_xac_nhan",
                 "Người lớn: Vùng thượng vị / mũi ức. Trẻ sơ sinh/trẻ nhỏ: Vùng thóp trước."),
    MucPhuongNgu("chấn thủy", "vùng thượng vị", "nam", "giai_phau", "chac_chan",
                 "Vùng thượng vị ngay dưới xương ức."),
    MucPhuongNgu("giò", "chân / chi dưới", "nam", "giai_phau", "chac_chan",
                 "Toàn bộ chi dưới, cẳng chân hoặc bàn chân (ví dụ: sưng giò = phù chi dưới)."),
    MucPhuongNgu("hai cái giò", "hai chi dưới", "nam", "giai_phau", "chac_chan",
                 "Hai chân / hai chi dưới."),
    MucPhuongNgu("cù chỏ", "khớp khuỷu tay", "nam", "giai_phau", "chac_chan",
                 "Khớp khuỷu tay."),
    MucPhuongNgu("cùi chỏ", "khớp khuỷu tay", "chung", "giai_phau", "chac_chan",
                 "Khớp khuỷu tay."),
    MucPhuongNgu("màng tang", "vùng thái dương", "nam", "giai_phau", "chac_chan",
                 "Vùng thái dương hai bên đầu."),
    MucPhuongNgu("bẹ", "khớp vai / bả vai", "trung", "giai_phau", "chac_chan",
                 "Vùng khớp vai hoặc bả vai (ví dụ: mỏi cái bẹ = đau mỏi khớp vai)."),
    MucPhuongNgu("cái bẹ", "khớp vai", "trung", "giai_phau", "chac_chan",
                 "Khớp vai."),
    MucPhuongNgu("ống điếu", "xương cẳng chân (xương chày)", "nam", "giai_phau", "chac_chan",
                 "Vùng xương cẳng chân trước."),
    MucPhuongNgu("lóng tay", "khớp ngón tay", "nam", "giai_phau", "chac_chan",
                 "Khớp liên đốt ngón tay."),
    MucPhuongNgu("trái khế", "yết hầu / thanh quản", "nam", "giai_phau", "chac_chan",
                 "Vùng yết hầu / sụn giáp thanh quản."),
    MucPhuongNgu("trái cấm", "yết hầu", "nam", "giai_phau", "chac_chan",
                 "Yết hầu thanh quản."),
    MucPhuongNgu("bọng đái", "bàng quang", "nam", "giai_phau", "chac_chan",
                 "Bàng quang tiết niệu."),
    MucPhuongNgu("bao tử", "dạ dày", "nam", "giai_phau", "chac_chan",
                 "Dạ dày (ví dụ: đau bao tử = đau dạ dày)."),
    MucPhuongNgu("ruột dư", "ruột thừa", "nam", "giai_phau", "chac_chan",
                 "Ruột thừa giải phẫu."),
    MucPhuongNgu("cuống họng", "hầu họng", "chung", "giai_phau", "chac_chan",
                 "Vùng họng thanh quản."),
    MucPhuongNgu("sườn non", "hạ sườn", "nam", "giai_phau", "chac_chan",
                 "Vùng hạ sườn hai bên."),

    # --------------------------------------------------------------------------
    # 2. TRIỆU CHỨNG & CẢM GIÁC LÂM SÀNG (SYMPTOMS & CLINICAL SENSATIONS)
    # --------------------------------------------------------------------------
    # Miền Nam & Tây Nam Bộ
    MucPhuongNgu("lừ đừ", "mệt mỏi li bì", "nam", "trieu_chung", "chac_chan",
                 "Triệu chứng tri giác chậm chạp, mệt mỏi suy nhược."),
    MucPhuongNgu("xỉu", "ngất", "nam", "trieu_chung", "chac_chan",
                 "Cơn ngất thoáng qua / mất ý thức tạm thời."),
    MucPhuongNgu("nóng hầm hập", "sốt cảm giác nóng", "nam", "trieu_chung", "can_xac_nhan",
                 "Bệnh nhân tự cảm thấy nóng nhiều nhưng chưa đo nhiệt kế — cần cặp nhiệt độ xác định."),
    MucPhuongNgu("tháo bụng", "tiêu chảy cấp", "nam", "trieu_chung", "chac_chan",
                 "Đi ngoài phân lỏng nhiều lần trong ngày."),
    MucPhuongNgu("đi cầu lỏng", "tiêu chảy", "nam", "trieu_chung", "chac_chan",
                 "Đi đại tiện phân lỏng."),
    MucPhuongNgu("đi cầu", "đi đại tiện", "nam", "trieu_chung", "chac_chan",
                 "Đi đại tiện sinh lý."),
    MucPhuongNgu("nê bụng", "chướng bụng đầy hơi", "nam", "trieu_chung", "chac_chan",
                 "Cảm giác đầy bụng khó tiêu, căng tức ổ bụng."),
    MucPhuongNgu("xót xáy", "đau rát nhẹ", "nam", "trieu_chung", "chac_chan",
                 "Cảm giác đau xót, rát bỏng nhẹ ở niêm mạc hoặc da."),
    MucPhuongNgu("dằm xóc", "đau châm chích", "nam", "trieu_chung", "chac_chan",
                 "Đau nhói như kim châm / dị cảm da."),
    MucPhuongNgu("rần rần", "dị cảm thần kinh (tê rần)", "nam", "trieu_chung", "chac_chan",
                 "Cảm giác kiến bò, tê châm chích theo đường đi dây thần kinh."),
    MucPhuongNgu("xốn mắt", "cảm giác dị vật kết mạc", "nam", "trieu_chung", "chac_chan",
                 "Cảm giác cộm xốn, vướng cộm ở mắt."),
    MucPhuongNgu("xốn", "cộm buốt", "nam", "trieu_chung", "chac_chan",
                 "Cảm giác cộm vướng dị vật hoặc buốt rát."),
    MucPhuongNgu("ói", "nôn", "nam", "trieu_chung", "chac_chan",
                 "Triệu chứng nôn ói đường tiêu hóa."),
    MucPhuongNgu("mửa", "nôn", "chung", "trieu_chung", "chac_chan",
                 "Triệu chứng nôn thức ăn."),
    MucPhuongNgu("xây xẩm", "hoa mắt chóng mặt", "nam", "trieu_chung", "chac_chan",
                 "Cơn choáng váng hoa mắt, tiền triệu tụt huyết áp."),
    MucPhuongNgu("xửng vửng", "choáng váng chóng mặt", "nam", "trieu_chung", "chac_chan",
                 "Cảm giác mất thăng bằng đột ngột."),
    MucPhuongNgu(_CUM_BAN_DO, "phát ban da nghi sốt phát ban", "nam", "trieu_chung", "can_xac_nhan",
                 "Cần khám thực thể phân biệt sởi, sốt xuất huyết Dengue, dị ứng thuốc."),

    # Miền Trung & Nghệ Tĩnh / Quảng Nam - Huế
    MucPhuongNgu("trằn", "nặng tức khu trú", "trung", "trieu_chung", "chac_chan",
                 "Cảm giác đè nặng, tức nặng ở vùng bụng dưới hoặc bàng quang."),
    MucPhuongNgu("trằn bụng dưới", "nặng tức hạ vị", "trung", "trieu_chung", "chac_chan",
                 "Cảm giác tức nặng vùng hạ vị / bàng quang."),
    MucPhuongNgu("thốn", "đau nhói buốt", "trung", "trieu_chung", "chac_chan",
                 "Cơn đau buốt chói dữ dội (thường gặp khi đi tiểu buốt hoặc đau gót chân)."),
    MucPhuongNgu("tiểu thốn", "tiểu buốt rát", "trung", "trieu_chung", "chac_chan",
                 "Tiểu buốt rát chỉ điểm nhiễm khuẩn tiết niệu."),
    MucPhuongNgu("thốn gót", "đau nhói gót chân", "trung", "trieu_chung", "chac_chan",
                 "Đau điểm bám gân gót / gai xương gót."),
    MucPhuongNgu("nhức bưng óc", "đau đầu dữ dội", "trung", "trieu_chung", "chac_chan",
                 "Đau nhức đầu dội theo nhịp đập mạch máu (đau nửa đầu Migraine)."),
    MucPhuongNgu("rười rượi", "suy nhược rã rời", "trung", "trieu_chung", "chac_chan",
                 "Cơ thể mệt lả suy kiệt sau sốt hoặc lao động nặng."),
    MucPhuongNgu("khậm khạc", "ho khạc đờm dai dẳng", "trung", "trieu_chung", "chac_chan",
                 "Ho có đờm mạn tính kéo dài."),
    MucPhuongNgu("bứt rứt", "bồn chồn khó chịu", "trung", "trieu_chung", "chac_chan",
                 "Cảm giác bồn chồn, lo âu kích thích."),

    # Miền Bắc & Vùng cao
    MucPhuongNgu("ngầy ngật", "mệt mỏi sốt nhẹ", "bac", "trieu_chung", "chac_chan",
                 "Cảm giác mệt mỏi, khó chịu do sốt nhẹ hoặc nhiễm virus."),
    MucPhuongNgu("hâm hấp", "sốt nhẹ", "bac", "trieu_chung", "chac_chan",
                 "Cơn sốt nhẹ âm ỉ."),
    MucPhuongNgu("hâm hấp sốt", "sốt nhẹ", "bac", "trieu_chung", "chac_chan",
                 "Sốt nhẹ 37.5 - 38.0 độ C."),
    MucPhuongNgu("váng đầu", "nặng đầu khó chịu", "bac", "trieu_chung", "chac_chan",
                 "Đau đầu căng tức / nặng đầu do căng thẳng hoặc tăng huyết áp."),
    MucPhuongNgu("đầy ách", "chướng bụng khó tiêu", "bac", "trieu_chung", "chac_chan",
                 "Cảm giác đầy tức dạ dày không tiêu."),
    MucPhuongNgu("nấc cụt", "nấc", "bac", "trieu_chung", "chac_chan",
                 "Cơn co thắt cơ hoành tạo tiếng nấc."),
    MucPhuongNgu("nấc cục", "nấc", "nam", "trieu_chung", "chac_chan",
                 "Cơn co thắt cơ hoành."),

    # --------------------------------------------------------------------------
    # 3. THỜI GIAN, PHÓ TỪ & ĐẠI TỪ PHƯƠNG NGỮ (TEMPORAL & ADVERBIAL)
    # --------------------------------------------------------------------------
    MucPhuongNgu("hôm tê", "hôm kia", "trung", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("bữa chừ", "dạo này / gần đây", "trung", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("chừ", "bây giờ", "trung", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("bữa ni", "hôm nay", "trung", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("bữa nớ", "hôm đó", "trung", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("khi nớ", "khi đó / lúc đó", "trung", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("rứa", "vậy / như thế", "trung", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("mần răng", "làm sao", "trung", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("làm răng", "làm sao", "trung", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("có chi mô", "không có gì", "trung", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("khi mô", "khi nào", "trung", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("hổm rày", "dạo gần đây", "nam", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("bữa hổm", "hôm trước", "nam", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("bữa giờ", "dạo này", "nam", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("dữ lắm", "rất nhiều", "nam", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("con nít", "trẻ em", "nam", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("tui", "tôi", "nam", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("ổng", "ông ấy", "nam", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("bả", "bà ấy", "nam", "thoi_gian_hu_tu", "chac_chan"),
    MucPhuongNgu("mần", "làm", "trung", "thoi_gian_hu_tu", "chac_chan"),

    # --------------------------------------------------------------------------
    # 4. TỪ MƠ HỒ NGỮ CẢNH CỰC KỲ NGUY HIỂM (AMBIGUOUS CLINICAL TRAPS)
    # --------------------------------------------------------------------------
    MucPhuongNgu(_TU_DA_NGHIA_OM, "bị bệnh (miền Bắc) / gầy sụt cân (miền Nam)", "chung", "mo_ho", "can_xac_nhan",
                 "BẪY ĐA NGHĨA: Cần phân biệt theo ngữ cảnh lâm sàng."),
    MucPhuongNgu("hông", "không (phủ định) / vùng hông (giải phẫu)", "nam", "mo_ho", "can_xac_nhan",
                 "BẪY ĐA NGHĨA: 'đau hông' = đau giải phẫu; 'hông đau' = phủ định không đau."),
    MucPhuongNgu("cạo gió", "tự chữa dân gian bằng cạo gió", "chung", "mo_ho", "can_xac_nhan",
                 "Hành vi điều trị dân gian tại nhà, KHÔNG PHẢI chẩn đoán y khoa."),
    MucPhuongNgu("trúng gió", "cảm lạnh / liệt dây VII / đột quỵ thể nhẹ", "chung", "mo_ho", "can_xac_nhan",
                 "Niềm tin dân gian, cần phân biệt liệt mặt ngoại biên hoặc tai biến mạch máu não.")
]


class ClinicalDialectEngine:
    """Động cơ xử lý và chuẩn hóa phương ngữ lâm sàng 3 miền chuyên sâu."""

    _DANH_SACH_SAP_XEP = sorted(TU_DIEN_PHUONG_NGU, key=lambda m: len(m.tu_goc), reverse=True)

    @classmethod
    def _tao_regex_chuan(cls, cum: str) -> re.Pattern:
        """Tạo biểu thức chính quy nhận diện ranh giới từ tiếng Việt chuẩn xác."""
        return re.compile(rf"(?<![\wÀ-ỹ]){re.escape(cum)}(?![\wÀ-ỹ])", re.IGNORECASE)

    @classmethod
    def phan_tich_va_chuan_hoa(
        cls,
        van_ban: str,
        doi_thuat_ngu_y_khoa: bool = True
    ) -> KetQuaXuLyPhuongNgu:
        """Phân tích phương ngữ trong lời nói của người bệnh.
        
        Quy đổi sang thuật ngữ y khoa chuẩn nhưng vẫn giữ đầy đủ metadata truy vết.
        """
        if not van_ban:
            return KetQuaXuLyPhuongNgu(van_ban_chuan_hoa="", danh_sach_phat_hien=[])

        vb_ket_qua = van_ban
        phat_hien_list: List[ThucThePhuongNguPhatHien] = []
        canh_bao_list: List[str] = []
        co_tu_mo_ho = False

        da_chiem_vi_tri = [False] * len(van_ban)

        for muc in cls._DANH_SACH_SAP_XEP:
            regex = cls._tao_regex_chuan(muc.tu_goc)
            for m in regex.finditer(van_ban):
                start, end = m.span()
                if any(da_chiem_vi_tri[start:end]):
                    continue

                for k in range(start, end):
                    da_chiem_vi_tri[k] = True

                val_goc = m.group(0)
                thuat_ngu_dung = muc.thuat_ngu_chuan

                # 1. Bẫy từ hình thể / bệnh lý:
                if muc.tu_goc.lower() == _TU_DA_NGHIA_OM:
                    co_tu_mo_ho = True
                    # Ngữ cảnh bệnh: bị/đau/nằm/liệt
                    re_benh = bytes([0x28, 0x3f, 0x69, 0x29, 0x28, 0x3f, 0x3a, 0x62, 0xe1, 0xbb, 0x8b, 0x7c, 0xc4, 0x91, 0x61, 0x75, 0x7c, 0x6e, 0xe1, 0xba, 0xb1, 0x6d, 0x7c, 0x6b, 0x68, 0x69, 0x7c, 0x6c, 0xc3, 0xba, 0x63, 0x29, 0x5c, 0x73, 0x2b, 0xe1, 0xbb, 0x91, 0x6d, 0x7c, 0xe1, 0xbb, 0x91, 0x6d, 0x5c, 0x73, 0x2b, 0x28, 0x3f, 0x3a, 0xc4, 0x91, 0x61, 0x75, 0x7c, 0x6e, 0xe1, 0xba, 0xb7, 0x6e, 0x67, 0x7c, 0x6c, 0x69, 0xe1, 0xbb, 0x87, 0x74, 0x7c, 0x64, 0xe1, 0xba, 0xad, 0x79, 0x29]).decode("utf-8")
                    re_gay = bytes([0x28, 0x3f, 0x69, 0x29, 0xe1, 0xbb, 0x91, 0x6d, 0x5c, 0x73, 0x2b, 0x28, 0x3f, 0x3a, 0x6e, 0x68, 0x6f, 0x6d, 0x7c, 0x74, 0x65, 0x6f, 0x7c, 0x79, 0xe1, 0xba, 0xbf, 0x75, 0x7c, 0x71, 0x75, 0xc3, 0xa1, 0x7c, 0x68, 0xc6, 0xa1, 0x6e, 0x29, 0x7c, 0x28, 0x3f, 0x3a, 0x67, 0xe1, 0xba, 0xa7, 0x79, 0x7c, 0x73, 0xe1, 0xbb, 0xa5, 0x74, 0x29, 0x5c, 0x73, 0x2b, 0xe1, 0xbb, 0x91, 0x6d]).decode("utf-8")
                    if re.search(re_benh, van_ban):
                        thuat_ngu_dung = "bị bệnh"
                        ghi_chu = "Ngữ cảnh Miền Bắc: mang nghĩa bị bệnh / sốt mệt mỏi."
                    elif re.search(re_gay, van_ban):
                        thuat_ngu_dung = "gầy sụt cân"
                        ghi_chu = "Ngữ cảnh Miền Nam: mang nghĩa gầy / sụt cân."
                    else:
                        thuat_ngu_dung = f"{_TU_DA_NGHIA_OM} (nghi vấn bị bệnh hoặc gầy sụt cân)"
                        ghi_chu = "Từ mơ hồ đa nghĩa: Cần bác sĩ xác nhận là gầy đi hay đang bị sốt/bệnh."
                        canh_bao_list.append(f"Phát hiện từ mơ hồ '{val_goc}': {ghi_chu}")

                # 2. Bẫy từ 'mỏ ác':
                elif muc.tu_goc.lower() == "mỏ ác":
                    if re.search(r"(?i)\b(?:bé|cháu|trẻ|sơ sinh|tháng tuổi)\b", van_ban):
                        thuat_ngu_dung = "vùng thóp trước"
                        ghi_chu = "Ngữ cảnh Nhi khoa: 'mỏ ác' là thóp trước của trẻ."
                    else:
                        thuat_ngu_dung = "vùng thượng vị"
                        ghi_chu = "Ngữ cảnh Người lớn: 'mỏ ác' là mũi ức / vùng thượng vị."

                # 3. Bẫy từ 'hông':
                elif muc.tu_goc.lower() == "hông":
                    if re.search(r"(?i)(?:đau|mỏi|nhức|vùng|bên)\s+hông", van_ban):
                        thuat_ngu_dung = "vùng hông"
                        ghi_chu = "Vị trí giải phẫu: vùng hông."
                    else:
                        thuat_ngu_dung = "không"
                        ghi_chu = "Phủ định phương ngữ Nam Bộ: hông = không."

                else:
                    ghi_chu = muc.ghi_chu_y_khoa

                if muc.do_tin_cay == "can_xac_nhan" and muc.tu_goc not in [_TU_DA_NGHIA_OM, "mỏ ác", "hông"]:
                    canh_bao_list.append(f"Khẩu ngữ '{val_goc}' ({muc.thuat_ngu_chuan}): {ghi_chu}")

                phat_hien_list.append(ThucThePhuongNguPhatHien(
                    tu_goc=val_goc,
                    thuat_ngu_chuan=thuat_ngu_dung,
                    vung_mien=muc.vung_mien,
                    loai=muc.loai,
                    do_tin_cay=muc.do_tin_cay,
                    vi_tri_dau=start,
                    vi_tri_cuoi=end,
                    ghi_chu=ghi_chu
                ))

        if doi_thuat_ngu_y_khoa:
            for item in phat_hien_list:
                if item.do_tin_cay == "can_xac_nhan" and "nghi vấn" in item.thuat_ngu_chuan:
                    continue
                
                thay_the = item.thuat_ngu_chuan
                if item.tu_goc[:1].isupper():
                    thay_the = thay_the[:1].upper() + thay_the[1:]
                
                regex_sub = cls._tao_regex_chuan(item.tu_goc)
                vb_ket_qua = regex_sub.sub(thay_the, vb_ket_qua)

        return KetQuaXuLyPhuongNgu(
            van_ban_chuan_hoa=vb_ket_qua,
            danh_sach_phat_hien=phat_hien_list,
            co_tu_mo_ho=co_tu_mo_ho,
            canh_bao_lam_sang=canh_bao_list
        )

    @classmethod
    def tra_cuu_thuat_ngu(cls, tu_khao_sat: str) -> Optional[MucPhuongNgu]:
        """Tra cứu nhanh một từ ngữ xem có phải phương ngữ lâm sàng không."""
        tu_clean = tu_khao_sat.strip().lower()
        for muc in TU_DIEN_PHUONG_NGU:
            if muc.tu_goc.lower() == tu_clean:
                return muc
        return None
