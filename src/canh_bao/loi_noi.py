# -*- coding: utf-8 -*-
"""[Lớp cảnh báo]
Làm gì   : Chuẩn hoá lời nói tiếng Việt cho các luật: tách ý, nhận câu hỏi, bỏ từ đệm.
Vào → Ra : chuỗi lời nói → danh sách ý đã tách, cờ câu hỏi, chuỗi đã bỏ từ đệm
Đọc từ   : tach_y() tách câu thành ý; nhan_cau_hoi() nhận câu hỏi
Mục lục (các hàm/lớp chính):
  tach_y()        Tách lượt nói thành từng ý theo dấu câu hoặc từ nối
  nhan_cau_hoi()  Nhận biết một câu có phải câu hỏi
  bo_tu_dem()     Bỏ từ đệm và từ lặp liền nhau
  co_dau_cau()    Kiểm tra lượt nói có dấu câu kết thúc hay không
Dùng bởi : canh_bao/phat_hien, duong_ong/b4_kiem_can_cu
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chuẩn hoá LỜI NÓI cho các luật: tách ý, nhận câu hỏi, bỏ từ đệm.

VÌ SAO (25/11/2026). Các luật cũ dựa vào DẤU CÂU: `phat_hien.cac_cau` tách theo
".!?;", `khoa_bang_chung.doan_chua_ghi` bỏ qua đoạn kết thúc bằng "?", `LA_CAU_HOI`
ưu tiên dấu "?". Văn bản chép từ âm thanh thường KHÔNG có dấu câu và viết thường,
nên trên lời nói thật các luật yếu đi mà không báo lỗi gì. Tệp này gồm ba hàm chịu
được cả hai kiểu đầu vào; các luật gọi sang đây thay vì tự đọc dấu câu.
"""
import re
import unicodedata
from typing import List, Tuple

TOI_DA_TU = 25
_DAU = re.compile(r"[.!?;…]+|,")
# Từ nối bắt đầu một ý mới khi không có dấu câu. "mà"/"thì" quá nhiều nghĩa -> không dùng.
_TU_NOI = re.compile(r"(?<!\w)(còn|nhưng|rồi|với lại|thêm nữa|ngoài ra|xong)(?!\w)")
# Từ hỏi phải ở CUỐI câu (chỉ còn tiểu từ sau nó): "ăn gì cũng nôn", "mấy hôm nay cháu ho",
# "chưa bao giờ dị ứng" là câu kể (rà soát 25/11).
_DUOI = r"(\s+(rồi|vậy|ạ|thế|nhỉ|nhé|nha|chưa|hả|chị|anh|em|bác|cô|chú|cháu|bé))*\s*$"
_TU_HOI = re.compile(r"(?<!\w)(gì|nào|sao|đâu|ai|bao lâu|bao giờ|thế nào|ra sao|mấy \w+|bao nhiêu( \w+)?)"
                     + _DUOI)
_CO_KHONG = re.compile(r"(?<!\w)có(?!\w).*(?<!\w)(không|chưa)" + _DUOI)
_TIEU_TU_CUOI = re.compile(r"(?<!\w)(không|chưa|à|hả|chứ|nhỉ|phải không|đúng không|có phải không)"
                           r"(\s+(ạ|vậy|nhỉ|nhé|nha|thế|vậy ạ|thế ạ))?\s*[?.!]*\s*$")
_TRA_LOI_NGAN = re.compile(r"^(dạ|vâng|ờ|ừ|thưa bác sĩ|[ ,])*(không|chưa|có|chẳng|chả)(\s+(ạ|đâu|ạ bác sĩ|nha|nhé))?"
                           r"\s*[.!]*$")
_DEM = re.compile(r"(?<!\w)(ờ|ừm|ừ|ơ|à)(?!\w)\s*")


# ═══ co_dau_cau() — Kiểm tra lượt nói có dấu câu kết thúc hay không ═══════════════════
# Chỉ lượt không dấu mới đi qua luồng chuẩn hoá lời nói.
def co_dau_cau(van: str) -> bool:
    """Lượt có dấu kết câu không. Các luật cũ giữ nguyên hành vi trên lượt CÓ dấu; chỉ lượt
    không dấu mới đi qua `tach_y` / `nhan_cau_hoi` — để số liệu cũ không đổi."""
    return bool(re.search(r"[.?!;…]", van or ""))


# ─── _nfc() — Chuẩn hoá chuỗi Unicode về dạng NFC ─────────────────────────────────────
def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", str(s or ""))


# ─── _cat_dai() — Cắt khúc dài thành các khúc tối đa 25 từ ────────────────────────────
# Giữ vị trí trong văn bản gốc.
def _cat_dai(van: str, a: int, b: int) -> List[Tuple[int, int]]:
    """Cắt [a, b) thành các khúc <= TOI_DA_TU từ, giữ vị trí trong văn gốc."""
    tu = [(m.start() + a, m.end() + a) for m in re.finditer(r"\S+", van[a:b])]
    return [(tu[i][0], tu[min(i + TOI_DA_TU, len(tu)) - 1][1]) for i in range(0, len(tu), TOI_DA_TU)]


# ─── _thu_gon() — Bỏ khoảng trắng và dấu phẩy ở hai đầu khúc ──────────────────────────
# Trả về vị trí đầu cuối mới.
def _thu_gon(van: str, a: int, b: int) -> Tuple[int, int]:
    while a < b and van[a] in " ,\t":
        a += 1
    while b > a and van[b - 1] in " ,\t":
        b -= 1
    return a, b


# ═══ tach_y() — Tách lượt nói thành từng ý theo dấu câu hoặc từ nối ═══════════════════
# Trả về các khoảng [a, b); văn bản chép âm không dấu vẫn tách được.
def tach_y(van: str) -> List[Tuple[int, int]]:
    """-> các khoảng [a, b) của từng ý trong `van`. Có dấu câu thì tách theo dấu; khúc
    nào vẫn dài và không có dấu thì tách tiếp theo từ nối; cuối cùng cắt khúc > 25 từ."""
    van = van or ""
    khuc, dau = [], 0
    for m in _DAU.finditer(van):
        khuc.append((dau, m.start()))
        dau = m.end()
    khuc.append((dau, len(van)))
    ra = []
    for a, b in khuc:
        a, b = _thu_gon(van, a, b)
        if a >= b:
            continue
        diem = [a] + [m.start() + a for m in _TU_NOI.finditer(van[a:b]) if m.start() > 0] + [b]
        for x, y in zip(diem, diem[1:]):
            x, y = _thu_gon(van, x, y)
            if x < y:
                ra += _cat_dai(van, x, y)
    return ra


# ═══ nhan_cau_hoi() — Nhận biết một câu có phải câu hỏi ═══════════════════════════════
# Câu trả lời ngắn như dạ không, có ạ thì không tính là câu hỏi.
def nhan_cau_hoi(van: str) -> bool:
    """Cau hoi khi: co "?"; hoac tieu tu hoi cuoi cau ("không", "chưa ạ", "à", "hả"...);
    hoac mau "có ... không"; hoac tu hoi ("gì", "đâu", "mấy"...). Cau tra loi ngan
    ("dạ không", "có ạ") KHÔNG phải câu hỏi dù kết thúc bằng "không"."""
    t = re.sub(r"\s+", " ", _nfc(van).lower()).strip()
    if not t:
        return False
    if "?" in t:
        return True
    if _TRA_LOI_NGAN.match(t):
        return False
    if _CO_KHONG.search(t.rstrip(".! ")):
        return True
    if _TIEU_TU_CUOI.search(t):
        # "em không ho" không phải câu hỏi: "không" phải đứng CUỐI (chỉ còn tiểu từ sau nó).
        return True
    return bool(_TU_HOI.search(t.rstrip(".! "))) and not re.search(r"(?<!\w)(không|chưa) (biết|nhớ|rõ)(?!\w)", t)


# ═══ bo_tu_dem() — Bỏ từ đệm và từ lặp liền nhau ══════════════════════════════════════
# Giữ chữ à ở cuối câu hỏi.
def bo_tu_dem(van: str) -> str:
    """Bo tu dem dung rieng ("ờ", "ừm", "à" dau/giua cau) va tu lap lien ("không không"),
    giữ "à" cuối câu hỏi ("bé sốt à")."""
    t = _nfc(van).strip()
    cuoi_a = bool(re.search(r"(?<!\w)à\s*[?]?\s*$", t)) and len(t.split()) > 1
    than = re.sub(r"(?<!\w)à\s*[?]?\s*$", "", t) if cuoi_a else t
    than = _DEM.sub("", than)
    than = re.sub(r"(?<!\w)(\w+)(\s+\1)+(?!\w)", r"\1", than)
    than = re.sub(r"\s{2,}", " ", than).strip()
    return f"{than} à" if cuoi_a else than
