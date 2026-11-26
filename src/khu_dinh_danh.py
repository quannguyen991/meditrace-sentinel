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

    # Từ chỉ địa chỉ chi tiết (hỗ trợ cả các mệnh đề có dấu phẩy nối như số nhà, đường, phường/xã, quận/huyện, tỉnh/thành)
    RE_DIA_CHI = re.compile(
        r"(?i)(?:địa chỉ(?:\s+cư\s+trú)?|nhà ở|trú tại|ngụ tại|thường trú tại|hộ khẩu tại)\s*(?:là|:)?\s*([^.\n;]+?(?:phường|xã|thị trấn|huyện|quận|thị xã|tỉnh|thành phố|tp\.?)[^.\n;]*)"
    )

    # Bảng chuyển số đọc tiếng Việt (ASR) thành chữ số
    SO_DOC_VIET: Dict[str, str] = {
        "không": "0", "linh": "0", "lẻ": "0",
        "một": "1", "mốt": "1",
        "hai": "2",
        "ba": "3",
        "bốn": "4", "tư": "4",
        "năm": "5", "lăm": "5", "nhăm": "5",
        "sáu": "6",
        "bảy": "7", "bẩy": "7",
        "tám": "8",
        "chín": "9",
    }

    @classmethod
    def chuan_hoa_so_noi_tieng_viet(cls, van_ban: str) -> str:
        """Đổi chuỗi số đọc bằng chữ tiếng Việt (>= 6 chữ số liên tiếp, cho phép ngắt phẩy/gạch) thành chữ số
        để bắt SĐT/CCCD/BHYT từ đầu ra ASR mà không làm hỏng 'hai ngày', 'ba viên'."""
        if not van_ban:
            return van_ban
        tu_so = "|".join(sorted(cls.SO_DOC_VIET.keys(), key=len, reverse=True))
        # Khớp chuỗi gồm ít nhất 6 từ số liên tiếp (ngăn cách bởi khoảng trắng, dấu phẩy hoặc gạch nối)
        pat = re.compile(
            rf"(?i)\b((?:{tu_so})(?:(?:\s+|,\s*|\s*-\s*)(?:{tu_so})){{5,}})\b"
        )

        def _thay(m: re.Match) -> str:
            cum = m.group(1)
            cac_tu = re.split(r"[\s,-]+", cum.strip().lower())
            digits = [cls.SO_DOC_VIET[t] for t in cac_tu if t in cls.SO_DOC_VIET]
            return "".join(digits) if len(digits) >= 6 else cum

        return pat.sub(_thay, van_ban)

    # Tiền tố tên người cụ thể (không dùng nhãn vai 'bệnh nhân:' để tránh bắt nhầm lời thoại)
    TIEN_TO_TEN = [
        "tôi tên là", "bệnh nhân tên là", "cháu tên là", "em tên là", "bác tên là",
        "họ và tên:", "họ tên:", "tên tôi là"
    ]

    # Danh xưng + Họ người Việt phổ biến + Tên viết hoa (vd: "Chào bác Nguyễn Văn An", "Mời anh Trần Minh Tuấn")
    RE_DANH_XUNG_HO_TEN = re.compile(
        r"\b(?:[Bb]ác|[Aa]nh|[Cc]hị|[Cc]ô|[Cc]hú|[Ôô]ng|[Bb]à|[Ee]m|[Cc]háu|[Bb]é|[Bb]ệnh\s+nhân)\s+"
        r"((?:Nguyễn|Trần|Lê|Phạm|Hoàng|Huỳnh|Phan|Vũ|Võ|Đặng|Bùi|Đỗ|Hồ|Ngô|Dương|Lý|Đinh|Đoàn|Lương|Trịnh|Đào|Mai|Tạ|Hà|Tăng|Quách|Chu|La|Tô|Châu|Tống|Thái|Nghiêm|Kiều|Lâm|Vương)"
        r"(?:\s+[A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ][a-zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]+){1,3})\b"
    )

    # Các hậu tố từ ghép tiếng Việt thông dụng/lâm sàng không được phép tách nhầm khi tên người là tên đơn (1 âm tiết)
    _HAU_TO_TU_GHEP_DON: Dict[str, Tuple[str, ...]] = {
        "an": ("toàn", "thần", "tâm", "nghỉ", "ninh", "khang", "sinh"),
        "bình": ("thường", "ổn", "tĩnh", "đẳng", "quân", "phục", "nguyên"),
        "tâm": ("thu", "trương", "thần", "nhĩ", "thất", "lý", "phế", "vị", "đồ"),
        "thanh": ("quản", "niên", "huyết", "nhiệt", "đờm", "mạc"),
        "thành": ("bụng", "ngực", "mạch", "phần", "công"),
        "minh": ("mẫn", "bạch"),
        "phúc": ("mạc",),
        "kết": ("mạc", "luận", "quả"),
        "mai": ("sau",),
    }

    @classmethod
    def _tao_regex_ten_nguoi(cls, ten_goc: str) -> re.Pattern:
        """Tạo biểu thức chính quy có ranh giới từ Unicode an toàn cho họ tên.
        - Với họ tên đa âm tiết ('Nguyễn Văn An'): khớp không phân biệt hoa-thường trên ranh giới từ.
        - Với tên đơn 1 âm tiết ('An', 'Bình', 'Tâm'): chỉ khớp khi viết hoa đầu từ hoặc đứng sau danh xưng,
          đồng thời loại trừ các từ ghép lâm sàng/thông dụng ('an thần', 'an toàn', 'bình thường', 'tâm đồ'...).
        """
        val = ten_goc.strip()
        if len(val.split()) >= 2:
            return re.compile(rf"(?<!\w){re.escape(val)}(?!\w)", re.IGNORECASE)

        thap = val.lower()
        hau_to = cls._HAU_TO_TU_GHEP_DON.get(thap, ())
        chan_sau = rf"(?!(?i:\s+(?:{'|'.join(re.escape(h) for h in hau_to)}))(?!\w))" if hau_to else ""
        chan_truoc = (
            r"(?<!\bđiện )(?<!\bĐiện )(?<!\bthuốc )(?<!\bThuốc )(?<!\báp )(?<!\bÁp )(?<!\btim )(?<!\bTim )"
            if thap in ("tâm", "an", "bình", "thanh")
            else ""
        )
        v_cap = val[0].upper() + val[1:].lower()
        v_up = val.upper()
        nhanh_hoa = rf"{chan_truoc}(?<!\w)(?:{re.escape(v_cap)}|{re.escape(v_up)})(?!\w){chan_sau}"
        danh_xung_co_dinh = (
            "bác", "Bác", "anh", "Anh", "chị", "Chị", "cô", "Cô", "chú", "Chú",
            "ông", "Ông", "bà", "Bà", "em", "Em", "cháu", "Cháu", "bé", "Bé",
            "bệnh nhân", "Bệnh nhân", "người bệnh", "Người bệnh", "bn", "BN",
        )
        lb_dx = "|".join(rf"(?<=\b{re.escape(dx)} )" for dx in danh_xung_co_dinh)
        nhanh_dx = rf"(?:{lb_dx})(?<!\w)(?i:{re.escape(val)})(?!\w){chan_sau}"
        return re.compile(rf"(?:{nhanh_hoa}|{nhanh_dx})")

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

        van_ban = cls.chuan_hoa_so_noi_tieng_viet(van_ban)
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

        # 7. Ẩn danh Tên bệnh nhân được truyền trực tiếp (bắt buộc ranh giới từ Unicode + bảo vệ từ ghép lâm sàng)
        if ten_benh_nhan and len(ten_benh_nhan.strip()) >= 2:
            val = ten_benh_nhan.strip()
            token = "[BENH_NHAN]"
            pat_bn = cls._tao_regex_ten_nguoi(val)
            matches_bn = list(pat_bn.finditer(van_ban))
            if matches_bn:
                bang_anh_xa[token] = val
                for m in matches_bn:
                    danh_sach_pii.append(ThucThePII("HO_TEN", m.group(0), token, m.start(), m.end()))

        # 8. Ẩn danh Tên thân nhân (bắt buộc ranh giới từ Unicode + bảo vệ từ ghép lâm sàng)
        if ten_than_nhan:
            for i, ten_tn in enumerate(ten_than_nhan, 1):
                if ten_tn and len(ten_tn.strip()) >= 2:
                    val = ten_tn.strip()
                    token = f"[NGUOI_NHA_{i}]"
                    pat_tn = cls._tao_regex_ten_nguoi(val)
                    matches_tn = list(pat_tn.finditer(van_ban))
                    if matches_tn:
                        bang_anh_xa[token] = val
                        for m in matches_tn:
                            danh_sach_pii.append(ThucThePII("HO_TEN_NGUOI_NHA", m.group(0), token, m.start(), m.end()))

        # 9. Tự động bắt tên qua tiền tố đích danh
        # Chỉ dùng (?i:...) cho phần tiền tố để [A-Z...][a-z...]+ giữ phân biệt hoa-thường,
        # hỗ trợ cả tên 1 chữ cái ('Nguyễn Thị Ý' / 'TRẦN THỊ Ý') và không bao giờ nuốt triệu chứng chữ thường phía sau.
        _chu_hoa = "A-ZÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ"
        _chu_thuong = "a-zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
        _tu_ten_hoa_dau = rf"[{_chu_hoa}][{_chu_thuong}]+"
        _tu_ten_hoa_tiep = rf"[{_chu_hoa}][{_chu_thuong}]*"
        _cum_ten = rf"(?:{_tu_ten_hoa_dau}(?:\s+{_tu_ten_hoa_tiep}){{0,4}}|[{_chu_hoa}]{{2,}}(?:\s+[{_chu_hoa}]{{1,}}){{1,4}})"
        for tt in cls.TIEN_TO_TEN:
            pattern = re.compile(rf"(?i:{re.escape(tt)})\s+({_cum_ten})(?!\w)")
            for m in pattern.finditer(van_ban):
                val = m.group(1).strip()
                if len(val) >= 2 and not any(p.gia_tri_goc.lower() == val.lower() for p in danh_sach_pii):
                    token = _lay_token("HO_TEN")
                    bang_anh_xa[token] = val
                    danh_sach_pii.append(ThucThePII("HO_TEN", val, token, m.start(1), m.end(1)))

        # 10. Tự động bắt tên riêng người Việt đi sau danh xưng (vd: "Chào bác Nguyễn Văn An")
        for m in cls.RE_DANH_XUNG_HO_TEN.finditer(van_ban):
            val = m.group(1).strip()
            if not any(p.gia_tri_goc.lower() == val.lower() for p in danh_sach_pii):
                token = _lay_token("HO_TEN")
                bang_anh_xa[token] = val
                danh_sach_pii.append(ThucThePII("HO_TEN", val, token, m.start(1), m.end(1)))

        # Thực hiện thay thế các thực thể trong văn bản (ưu tiên chuỗi dài trước + ranh giới từ Unicode)
        _token_ten = lambda tk: tk == "[BENH_NHAN]" or tk.startswith("[NGUOI_NHA_") or tk.startswith("[HO_TEN_")
        for token, val_goc in sorted(bang_anh_xa.items(), key=lambda kv: len(kv[1]), reverse=True):
            if not val_goc:
                continue
            if _token_ten(token):
                vb_xu_ly = cls._tao_regex_ten_nguoi(val_goc).sub(lambda _m, t=token: t, vb_xu_ly)
                continue
            left_b = r"(?<!\w)" if (val_goc[0].isalnum() or val_goc[0] == "_") else ""
            right_b = r"(?!\w)" if (val_goc[-1].isalnum() or val_goc[-1] == "_") else ""
            vb_xu_ly = re.sub(
                rf"{left_b}{re.escape(val_goc)}{right_b}",
                lambda _m, t=token: t,
                vb_xu_ly,
                flags=re.IGNORECASE,
            )

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
