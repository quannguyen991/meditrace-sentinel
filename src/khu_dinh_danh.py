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
    # Bo `ti_le_an_toan_bao_mat` (tra 1.0/0.95 co dinh, khong do gi ca). Thay bang ket qua
    # kiem tra con sot THAT tren van ban da che: rong = khong con dau vet PII nao bo do bat duoc.
    con_sot: List[Dict[str, object]] = field(default_factory=list)


# Ho nguoi Viet pho bien (viet thuong) - dung de nhan ten viet thuong tu ASR
HO_VIET = (
    "nguyễn", "trần", "lê", "phạm", "hoàng", "huỳnh", "phan", "vũ", "võ", "đặng", "bùi", "đỗ",
    "hồ", "ngô", "dương", "lý", "đinh", "đoàn", "lương", "trịnh", "đào", "mai", "tạ", "hà",
    "tăng", "quách", "chu", "la", "tô", "châu", "tống", "thái", "nghiêm", "kiều", "lâm", "vương",
    "cao", "lưu", "trương", "từ", "khúc", "âu", "giang", "triệu", "doãn", "phùng", "văn", "tôn",
)

# Tu thuong dung / dau cau / trieu chung: gap la DUNG bat ten (tranh "Trần Thị Mai Sau đó")
TU_DUNG_TEN = frozenset((
    "sau", "đó", "rồi", "hôm", "nay", "qua", "năm", "tuổi", "tháng", "ngày", "tuần",
    "ạ", "dạ", "vâng", "nhé", "nha", "à", "ơi", "ạh", "đây", "đấy", "kia", "này", "nè",
    "và", "với", "thì", "mà", "là", "có", "không", "chưa", "đã", "đang", "sẽ", "vừa", "mới",
    "cũng", "còn", "nữa", "được", "bị", "cho", "vì", "nên", "nhưng", "hay", "hoặc", "ở", "tại",
    "đến", "tới", "từ", "khám", "đi", "về", "làm", "sinh", "quê", "nhà", "hiện", "giờ", "lúc",
    "tôi", "em", "cháu", "con", "bác", "anh", "chị", "cô", "chú", "ông", "bà", "mẹ", "bố", "vợ",
    "chồng", "sĩ", "bệnh", "nhân", "người", "thuốc", "đau", "sốt", "ho", "mệt", "khó", "thở",
    "chóng", "mặt", "buồn", "nôn", "tiêu", "chảy", "ngứa", "sưng", "uống", "tiêm", "xin", "muốn",
    "thấy", "cảm", "biết", "nói", "hỏi", "khi", "trước", "nghề", "giáo", "viên", "học", "sinh",
    "hôm", "tối", "sáng", "chiều", "trưa", "đêm", "vào", "ra", "lên", "xuống", "ạ.",
))

# Tien to dan ten (khong phan biet hoa-thuong). "tôi là" yeu cau ten bat dau bang ho/chu hoa.
TIEN_TO_TEN_MANH = (
    "tên của tôi là", "tôi tên là", "tên tôi là", "bệnh nhân tên là", "cháu tên là", "em tên là",
    "bác tên là", "con tên là", "anh tên là", "chị tên là", "tên là", "cháu tên", "em tên",
    "con tên", "họ và tên", "họ tên",
)
TIEN_TO_TEN_YEU = ("tôi là", "em là", "cháu là")

_RE_TU = re.compile(r"[^\W\d_]+")
_RE_CHUOI_SO = re.compile(r"(?<![\w+])(\+\s?)?\d+(?:[ .\-]\d+)*(?!\w)")


def _la_hoa(tu: str) -> bool:
    return tu[:1].isupper()


def _bat_ten_sau_tien_to(van_ban: str, vi_tri: int, yeu: bool) -> Optional[Tuple[int, int]]:
    """Bat cum ten ngay sau vi_tri (cuoi tien to). -> (dau, cuoi) hoac None.

    Chu hoa dau: lay cac tu viet hoa lien tiep (toi da 5), dung o tu dung.
    Viet thuong (ASR): tu dau la ho -> toi da 4 tu; khong phai ho -> toi da 2 tu; dung o tu dung.
    Tien to yeu ("tôi là"): chi nhan khi tu dau la ho hoac viet hoa.
    """
    m0 = re.match(r"\s*:?\s*", van_ban[vi_tri:])
    k = vi_tri + m0.end()
    tu_list: List[Tuple[int, int, str]] = []
    while k < len(van_ban):
        m = _RE_TU.match(van_ban, k)
        if not m:
            break
        tu_list.append((m.start(), m.end(), m.group(0)))
        if len(tu_list) >= 6:
            break
        nxt = m.end()
        if nxt < len(van_ban) and van_ban[nxt] == " " and nxt + 1 < len(van_ban) and _RE_TU.match(van_ban, nxt + 1):
            k = nxt + 1
        else:
            break
    if not tu_list:
        return None
    dau = tu_list[0][2]
    if dau.lower() in TU_DUNG_TEN and not (dau.lower() in HO_VIET):
        return None
    hoa = _la_hoa(dau)
    la_ho = dau.lower() in HO_VIET
    if yeu and not (hoa or la_ho):
        return None
    if hoa:
        toi_da = 5
    else:
        toi_da = 4 if la_ho else 2
    lay: List[Tuple[int, int, str]] = []
    for i, (a, b, w) in enumerate(tu_list):
        if len(lay) >= toi_da:
            break
        if i > 0 and w.lower() in TU_DUNG_TEN:
            break
        if hoa and not _la_hoa(w):
            break
        lay.append((a, b, w))
    if not lay:
        return None
    return lay[0][0], lay[-1][1]


def tim_ten_theo_tien_to(van_ban: str) -> List[Tuple[int, int]]:
    """Moi cum ten dung sau tien to dan ten (khong phan biet hoa-thuong) -> danh sach (dau, cuoi)."""
    ra: List[Tuple[int, int]] = []
    if not van_ban:
        return ra
    for ds, yeu in ((TIEN_TO_TEN_MANH, False), (TIEN_TO_TEN_YEU, True)):
        for tt in sorted(ds, key=len, reverse=True):
            for m in re.finditer(rf"(?<!\w){re.escape(tt)}(?!\w)", van_ban, re.IGNORECASE):
                kq = _bat_ten_sau_tien_to(van_ban, m.end(), yeu)
                if kq and not any(a < kq[1] and kq[0] < b for a, b in ra):
                    ra.append(kq)
    return sorted(ra)


def tim_so_dai(van_ban: str) -> List[Tuple[int, int, str]]:
    """Tim chuoi so giong so dien thoai / so dinh danh (9-15 chu so) ke ca khi bi tach nhom.

    -> [(dau, cuoi, loai)], loai "SDT" (bat dau 0 / 84 / +84) hoac "SO_DINH_DANH".
    Nhom so cach nhau dung mot dau cach/cham/gach: "0912 345 678", "0912.345.678",
    "+84 912345678", "0 9 1 2 3 4 5 6 7 8". Chuoi nhieu nhom KHONG bat dau bang 0/84 (vd huyet
    ap "140 90, 135 85") khong bi coi la so dien thoai, tru khi moi nhom chi mot chu so.
    """
    ra: List[Tuple[int, int, str]] = []
    if not van_ban:
        return ra
    for m in _RE_CHUOI_SO.finditer(van_ban):
        cong = bool(m.group(1))
        nhom = [(g.start(), g.end()) for g in re.finditer(r"\d+", van_ban[m.start():m.end()])]
        nhom = [(m.start() + a, m.start() + b) for a, b in nhom]
        i = 0
        while i < len(nhom):
            chu_i = van_ban[nhom[i][0]:nhom[i][1]]
            dau_span = m.start() if (i == 0 and cong) else nhom[i][0]
            loai = "SDT" if (chu_i.startswith("0") or chu_i.startswith("84") or (i == 0 and cong)) else "SO_DINH_DANH"
            # (a) mot nhom lien 9-15 chu so
            if 9 <= len(chu_i) <= 15:
                ra.append((dau_span, nhom[i][1], loai))
                i += 1
                continue
            # (b) nhieu nhom bat dau 0 / 84 / +84: lay so nhom it nhat dat >= 10 chu so
            if loai == "SDT":
                d, j = len(chu_i), i
                while d < 10 and j + 1 < len(nhom):
                    j += 1
                    d += nhom[j][1] - nhom[j][0]
                if j > i and 9 <= d <= 15 and d >= 10:
                    ra.append((dau_span, nhom[j][1], "SDT"))
                    i = j + 1
                    continue
            # (c) doc tung chu so: "1 2 3 4 5 6 7 8 9"
            if len(chu_i) == 1:
                j = i
                while j + 1 < len(nhom) and nhom[j + 1][1] - nhom[j + 1][0] == 1:
                    j += 1
                if 9 <= j - i + 1 <= 15:
                    ra.append((dau_span, nhom[j][1], loai))
                    i = j + 1
                    continue
            i += 1
    return ra


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

        def _chong(a: int, b: int) -> bool:
            return any(p.vi_tri_dau < b and a < p.vi_tri_cuoi for p in danh_sach_pii)

        # 4. Ẩn danh Số điện thoại / chuỗi số định danh 9-15 chữ số (kể cả tách nhóm "0912 345 678",
        #    "0912.345.678", "+84 912345678", đọc từng số "0 9 1 2 ...")
        for a, b, loai_so in tim_so_dai(van_ban):
            if _chong(a, b):
                continue  # đã nằm trong CCCD / BHYT
            val = van_ban[a:b]
            token = _lay_token("SDT" if loai_so == "SDT" else "SO_DINH_DANH")
            bang_anh_xa[token] = val
            danh_sach_pii.append(ThucThePII(
                "SO_DIEN_THOAI" if loai_so == "SDT" else "SO_DINH_DANH", val, token, a, b))

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

        def _them_ten_biet_truoc(ten: str, token: str, loai: str) -> None:
            """Ho ten day du + bien the TEN RIENG (tu cuoi) + "danh xung + ten rieng"."""
            val = ten.strip()
            bien_the = [(val, token)]
            cac_tu = val.split()
            if len(cac_tu) >= 2 and len(cac_tu[-1]) >= 2:
                # "Nguyễn Văn An" -> "An" ("Anh An đau", "anh an đau") dung token rieng de
                # giai ma tra lai dung chu da noi (khong bien "Anh An" thanh "Anh Nguyễn Văn An")
                bien_the.append((cac_tu[-1], token[:-1] + "_TEN]"))
            for gia_tri, tk in bien_the:
                matches = [m for m in cls._tao_regex_ten_nguoi(gia_tri).finditer(van_ban)
                           if not _chong(m.start(), m.end())]
                if matches:
                    bang_anh_xa[tk] = gia_tri
                    for m in matches:
                        danh_sach_pii.append(ThucThePII(loai, m.group(0), tk, m.start(), m.end()))

        # 7. Ẩn danh Tên bệnh nhân được truyền trực tiếp (bắt buộc ranh giới từ Unicode + bảo vệ từ ghép lâm sàng)
        if ten_benh_nhan and len(ten_benh_nhan.strip()) >= 2:
            _them_ten_biet_truoc(ten_benh_nhan, "[BENH_NHAN]", "HO_TEN")

        # 8. Ẩn danh Tên thân nhân (bắt buộc ranh giới từ Unicode + bảo vệ từ ghép lâm sàng)
        if ten_than_nhan:
            for i, ten_tn in enumerate(ten_than_nhan, 1):
                if ten_tn and len(ten_tn.strip()) >= 2:
                    _them_ten_biet_truoc(ten_tn, f"[NGUOI_NHA_{i}]", "HO_TEN_NGUOI_NHA")

        # 9. Tự động bắt tên qua tiền tố đích danh, KHÔNG phân biệt hoa-thường (ASR hay ra chữ thường:
        #    "tôi tên là nguyễn văn an"); dừng ở từ dừng ("Trần Thị Mai Sau đó" -> chỉ "Trần Thị Mai").
        for a, b in tim_ten_theo_tien_to(van_ban):
            if _chong(a, b):
                continue
            val = van_ban[a:b]
            token = _lay_token("HO_TEN")
            bang_anh_xa[token] = val
            danh_sach_pii.append(ThucThePII("HO_TEN", val, token, a, b))

        # 10. Tự động bắt tên riêng người Việt đi sau danh xưng (vd: "Chào bác Nguyễn Văn An")
        for m in cls.RE_DANH_XUNG_HO_TEN.finditer(van_ban):
            a, b = m.start(1), m.end(1)
            # cat cac tu dung o duoi ("bác Trần Thị Mai Sau đó" -> "Trần Thị Mai")
            tu = list(_RE_TU.finditer(van_ban, a, b))
            while len(tu) > 2 and tu[-1].group(0).lower() in TU_DUNG_TEN:
                tu.pop()
            b = tu[-1].end()
            val = van_ban[a:b]
            if _chong(a, b) or any(p.gia_tri_goc.lower() == val.lower() for p in danh_sach_pii):
                continue
            token = _lay_token("HO_TEN")
            bang_anh_xa[token] = val
            danh_sach_pii.append(ThucThePII("HO_TEN", val, token, a, b))

        # Thay thế: (1) đúng VỊ TRÍ đã phát hiện (kể cả tên viết thường / tên đơn sau tiền tố),
        # (2) rồi quét toàn văn theo GIÁ TRỊ để che các lần nhắc lại (ưu tiên chuỗi dài trước).
        da_lay: List[Tuple[int, int, str]] = []
        for p in sorted(danh_sach_pii, key=lambda p: (p.vi_tri_dau, -(p.vi_tri_cuoi - p.vi_tri_dau))):
            if any(a < p.vi_tri_cuoi and p.vi_tri_dau < b for a, b, _ in da_lay):
                continue
            da_lay.append((p.vi_tri_dau, p.vi_tri_cuoi, p.ma_the_the))
        for a, b, tk in sorted(da_lay, reverse=True):
            vb_xu_ly = vb_xu_ly[:a] + tk + vb_xu_ly[b:]

        _token_ten = lambda tk: tk.startswith("[BENH_NHAN") or tk.startswith("[NGUOI_NHA_") or tk.startswith("[HO_TEN_")
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
            con_sot=cls.kiem_tra_con_sot(vb_xu_ly),
        )

    @classmethod
    def kiem_tra_con_sot(cls, van_ban: str) -> List[Dict[str, object]]:
        """Quet lai van ban DA CHE: con chuoi so giong SDT/dinh danh, hay ten sau tien to dan ten,
        thi tra danh sach (loai, vi tri) - KHONG tra gia tri goc de khoi lo qua log.

        Dung lam chot fail-closed truoc khi gui ra may xa: danh sach khac rong -> khong gui.
        """
        ra: List[Dict[str, object]] = []
        if not van_ban:
            return ra
        for a, b, loai in tim_so_dai(van_ban):
            ra.append({"loai": loai, "vi_tri": [a, b]})
        for a, b in tim_ten_theo_tien_to(van_ban):
            ra.append({"loai": "HO_TEN", "vi_tri": [a, b]})
        return ra

    @classmethod
    def giai_ma_van_ban(cls, van_ban_da_an_danh: str, bang_anh_xa: Dict[str, str]) -> str:
        """Khôi phục lại dữ liệu gốc cho nhân viên y tế có thẩm quyền (2-way de-identification)."""
        if not van_ban_da_an_danh or not bang_anh_xa:
            return van_ban_da_an_danh

        ket_qua = van_ban_da_an_danh
        for token, val_goc in bang_anh_xa.items():
            ket_qua = ket_qua.replace(token, val_goc)
        return ket_qua
