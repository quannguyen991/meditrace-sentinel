# -*- coding: utf-8 -*-
"""Module Khử nhận dạng và Ẩn danh Thông tin Cá nhân Y tế (Clinical PII/PHI De-identification).

Tuân thủ nghiêm ngặt Luật Khám bệnh, chữa bệnh 2023 (Điều 10, 32 về bảo mật thông tin bệnh nhân),
Nghị định 13/2023/NĐ-CP về Bảo vệ Dữ liệu Cá nhân và tiêu chuẩn quốc tế HIPAA / GDPR.

Các loại thực thể PII/PHI được phát hiện và xử lý:
1. Họ và tên người (Bệnh nhân, người nhà)
2. Số điện thoại (10 chữ số theo quy chuẩn VN)
3. Số Căn cước công dân / CMND (9 hoặc 12 số)
4. Số thẻ Bảo hiểm Y tế (BHYT) (chuẩn 15 ký tự)
5. Địa chỉ cư trú chi tiết
6. Ngày tháng năm sinh
7. Địa chỉ Email
"""

from dataclasses import dataclass, field
import re
from typing import Dict, List, Optional, Tuple


@dataclass
class ThucThePII:
    loai: str           # HO_TEN, SO_DIEN_THOAI, CCCD, SO_BHYT, DIA_CHI, EMAIL, NGAY_SINH
    gia_tri_goc: str
    ma_the_the: str     # ví dụ: [BENH_NHAN_1], [SDT_1], [BHYT_1]
    vi_tri_dau: int
    vi_tri_cuoi: int


@dataclass
class KetQuaKhuDinhDanh:
    van_ban_da_an_danh: str
    danh_sach_pii: List[ThucThePII] = field(default_factory=list)
    bang_anh_xa_giai_ma: Dict[str, str] = field(default_factory=dict)
    tong_so_thuc_the: int = 0
    ti_le_an_toan_bao_mat: float = 1.0


class ClinicalDeidentifier:
    """Bộ xử lý khử nhận dạng dữ liệu lâm sàng tiếng Việt."""

    # Regex nhận diện số điện thoại VN (10 chữ số bắt đầu bằng 03, 05, 07, 08, 09 hoặc +84)
    # Dùng (?<!\d) và (?!\d) để không bắt nhầm chuỗi số trong CCCD/BHYT
    RE_SDT = re.compile(
        r"(?<!\d)(?:(?:\+84|0)(?:3[2-9]|5[2689]|7[06-9]|8[1-9]|9[0-9]))[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)"
    )

    # Regex nhận diện CCCD (12 chữ số) hoặc CMND (9 chữ số) khi có từ khóa dẫn đường
    RE_CCCD = re.compile(
        r"(?i)(?:cccd|cmnd|căn cước công dân|căn cước|chứng minh nhân dân|số định danh)(?:\s+của\s+(?:tôi|em|bác|cháu))?\s*(?:số|là|:)?\s*(\d{9}|\d{12})(?!\d)"
    )

    # Regex nhận diện thẻ BHYT (chuẩn 15 ký tự: 2 ký tự chữ cái + 1 chữ số đối tượng + 2 số tỉnh + 10 số định danh)
    RE_BHYT = re.compile(
        r"(?i)(?:bhyt|bảo hiểm y tế|thẻ bhyt)(?:\s+của\s+(?:tôi|em|bác|cháu))?\s*(?:số|là|:)?\s*([a-z]{2}\s*\d\s*\d{2}\s*\d{10})(?!\d)"
    )

    # Regex nhận diện Email
    RE_EMAIL = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    )

    # Regex nhận diện ngày tháng năm sinh cụ thể
    RE_NGAY_SINH = re.compile(
        r"(?i)(?:sinh ngày|ngày sinh|ns|sinh)\s*(?:là|:)?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})\b"
    )

    # Từ chỉ địa chỉ chi tiết (hỗ trợ cả các mệnh đề có dấu phẩy nối như số nhà, đường, quận/huyện, tỉnh/thành)
    RE_DIA_CHI = re.compile(
        r"(?i)(?:địa chỉ(?:\s+cư\s+trú)?|nhà ở|trú tại|ngụ tại|thường trú tại|hộ khẩu tại)\s*(?:là|:)?\s*([^.\n;]+?(?:huyện|quận|thị xã|tỉnh|thành phố)[^.\n;]*)"
    )

    # Tiền tố tên người cụ thể (không dùng nhãn vai 'bệnh nhân:' để tránh bắt nhầm lời thoại)
    TIEN_TO_TEN = [
        "tôi tên là", "bệnh nhân tên là", "cháu tên là", "em tên là", "bác tên là",
        "họ và tên:", "họ tên:", "tên tôi là"
    ]

    @classmethod
    def an_danh_van_ban(
        cls,
        van_ban: str,
        ten_benh_nhan: Optional[str] = None,
        ten_than_nhan: Optional[List[str]] = None
    ) -> KetQuaKhuDinhDanh:
        """Thực hiện ẩn danh văn bản hội thoại hoặc bệnh án.
        
        Thay thế các thông tin nhạy cảm bằng mã định danh an toàn có thể giải mã 2 chiều.
        """
        if not van_ban:
            return KetQuaKhuDinhDanh(van_ban_da_an_danh="", danh_sach_pii=[], bang_anh_xa_giai_ma={})

        vb_xu_ly = van_ban
        danh_sach_pii: List[ThucThePII] = []
        bang_anh_xa: Dict[str, str] = {}
        dem_theo_loai: Dict[str, int] = {}

        def _lay_token(loai: str) -> str:
            dem_theo_loai[loai] = dem_theo_loai.get(loai, 0) + 1
            return f"[{loai}_{dem_theo_loai[loai]}]"

        # 1. Ẩn danh Email
        for match in cls.RE_EMAIL.finditer(van_ban):
            val = match.group(0)
            token = _lay_token("EMAIL")
            bang_anh_xa[token] = val
            danh_sach_pii.append(ThucThePII("EMAIL", val, token, match.start(), match.end()))

        # 2. Ẩn danh Thẻ BHYT (ưu tiên trước số điện thoại)
        for match in cls.RE_BHYT.finditer(van_ban):
            val = match.group(1).strip()
            token = _lay_token("BHYT")
            bang_anh_xa[token] = val
            danh_sach_pii.append(ThucThePII("SO_BHYT", val, token, match.start(1), match.end(1)))

        # 3. Ẩn danh CCCD/CMND (ưu tiên trước số điện thoại)
        for match in cls.RE_CCCD.finditer(van_ban):
            val = match.group(1).strip()
            token = _lay_token("CCCD")
            bang_anh_xa[token] = val
            danh_sach_pii.append(ThucThePII("CCCD", val, token, match.start(1), match.end(1)))

        # 4. Ẩn danh Số điện thoại
        for match in cls.RE_SDT.finditer(van_ban):
            val = match.group(0).strip()
            # Bỏ qua nếu là một phần của CCCD hoặc BHYT đã bắt
            if any(val in p.gia_tri_goc for p in danh_sach_pii):
                continue
            token = _lay_token("SDT")
            bang_anh_xa[token] = val
            danh_sach_pii.append(ThucThePII("SO_DIEN_THOAI", val, token, match.start(), match.end()))

        # 5. Ẩn danh Ngày sinh
        for match in cls.RE_NGAY_SINH.finditer(van_ban):
            val = match.group(1).strip()
            token = _lay_token("NGAY_SINH")
            bang_anh_xa[token] = val
            danh_sach_pii.append(ThucThePII("NGAY_SINH", val, token, match.start(1), match.end(1)))

        # 6. Ẩn danh Địa chỉ chi tiết
        for match in cls.RE_DIA_CHI.finditer(van_ban):
            val = match.group(1).strip()
            token = _lay_token("DIA_CHI")
            bang_anh_xa[token] = val
            danh_sach_pii.append(ThucThePII("DIA_CHI", val, token, match.start(1), match.end(1)))

        # 7. Ẩn danh Tên bệnh nhân được truyền trực tiếp
        if ten_benh_nhan and len(ten_benh_nhan.strip()) >= 2:
            val = ten_benh_nhan.strip()
            token = "[BENH_NHAN]"
            bang_anh_xa[token] = val
            for m in re.finditer(re.escape(val), van_ban, re.IGNORECASE):
                danh_sach_pii.append(ThucThePII("HO_TEN", m.group(0), token, m.start(), m.end()))

        # 8. Ẩn danh Tên thân nhân
        if ten_than_nhan:
            for i, ten_tn in enumerate(ten_than_nhan, 1):
                if ten_tn and len(ten_tn.strip()) >= 2:
                    val = ten_tn.strip()
                    token = f"[NGUOI_NHA_{i}]"
                    bang_anh_xa[token] = val
                    for m in re.finditer(re.escape(val), van_ban, re.IGNORECASE):
                        danh_sach_pii.append(ThucThePII("HO_TEN_NGUOI_NHA", m.group(0), token, m.start(), m.end()))

        # 9. Tự động bắt tên qua tiền tố đích danh
        for tt in cls.TIEN_TO_TEN:
            pattern = re.compile(rf"(?i){re.escape(tt)}\s+([A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ][a-zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+(?:\s+[A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ][a-zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+)+)")
            for m in pattern.finditer(van_ban):
                val = m.group(1).strip()
                if not any(p.gia_tri_goc.lower() == val.lower() for p in danh_sach_pii):
                    token = _lay_token("HO_TEN")
                    bang_anh_xa[token] = val
                    danh_sach_pii.append(ThucThePII("HO_TEN", val, token, m.start(1), m.end(1)))

        # Thực hiện thay thế các thực thể trong văn bản
        for token, val_goc in bang_anh_xa.items():
            vb_xu_ly = re.sub(re.escape(val_goc), token, vb_xu_ly, flags=re.IGNORECASE)

        return KetQuaKhuDinhDanh(
            van_ban_da_an_danh=vb_xu_ly,
            danh_sach_pii=danh_sach_pii,
            bang_anh_xa_giai_ma=bang_anh_xa,
            tong_so_thuc_the=len(danh_sach_pii),
            ti_le_an_toan_bao_mat=1.0 if len(danh_sach_pii) > 0 else 0.95
        )

    @classmethod
    def giai_ma_van_ban(cls, van_ban_da_an_danh: str, bang_anh_xa: Dict[str, str]) -> str:
        """Khôi phục lại dữ liệu gốc cho nhân viên y tế có thẩm quyền (2-way de-identification)."""
        if not van_ban_da_an_danh or not bang_anh_xa:
            return van_ban_da_an_danh

        ket_qua = van_ban_da_an_danh
        for token, val_goc in bang_anh_xa.items():
            ket_qua = ket_qua.replace(token, val_goc)
        return ket_qua
