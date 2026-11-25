# -*- coding: utf-8 -*-
"""Chuan hoa LOI NOI cho cac luat: tach y, nhan cau hoi, bo tu dem.

VI SAO (25/11/2026). Cac luat cu dua vao DAU CAU: `phat_hien.cac_cau` tach theo
".!?;", `khoa_bang_chung.doan_chua_ghi` bo qua doan ket thuc bang "?", `LA_CAU_HOI`
uu tien dau "?". Van ban chep tu am thanh thuong KHONG co dau cau va viet thuong,
nen tren loi noi that cac luat yeu di ma khong bao loi gi. Tep nay gom ba ham chiu
duoc ca hai kieu dau vao; cac luat goi sang day thay vi tu doc dau cau.
"""
import re
import unicodedata
from typing import List, Tuple

TOI_DA_TU = 25
_DAU = re.compile(r"[.!?;…]+|,")
# Tu noi bat dau mot y moi khi khong co dau cau. "mà"/"thì" qua nhieu nghia -> khong dung.
_TU_NOI = re.compile(r"(?<!\w)(còn|nhưng|rồi|với lại|thêm nữa|ngoài ra|xong)(?!\w)")
# Tu hoi phai o CUOI cau (chi con tieu tu sau no): "ăn gì cũng nôn", "mấy hôm nay cháu ho",
# "chưa bao giờ dị ứng" la cau ke (ra soat 25/11).
_DUOI = r"(\s+(rồi|vậy|ạ|thế|nhỉ|nhé|nha|chưa|hả|chị|anh|em|bác|cô|chú|cháu|bé))*\s*$"
_TU_HOI = re.compile(r"(?<!\w)(gì|nào|sao|đâu|ai|bao lâu|bao giờ|thế nào|ra sao|mấy \w+|bao nhiêu( \w+)?)"
                     + _DUOI)
_CO_KHONG = re.compile(r"(?<!\w)có(?!\w).*(?<!\w)(không|chưa)" + _DUOI)
_TIEU_TU_CUOI = re.compile(r"(?<!\w)(không|chưa|à|hả|chứ|nhỉ|phải không|đúng không|có phải không)"
                           r"(\s+(ạ|vậy|nhỉ|nhé|nha|thế|vậy ạ|thế ạ))?\s*[?.!]*\s*$")
_TRA_LOI_NGAN = re.compile(r"^(dạ|vâng|ờ|ừ|thưa bác sĩ|[ ,])*(không|chưa|có|chẳng|chả)(\s+(ạ|đâu|ạ bác sĩ|nha|nhé))?"
                           r"\s*[.!]*$")
_DEM = re.compile(r"(?<!\w)(ờ|ừm|ừ|ơ|à)(?!\w)\s*")


def co_dau_cau(van: str) -> bool:
    """Luot co dau ket cau khong. Cac luat cu giu nguyen hanh vi tren luot CO dau; chi luot
    khong dau moi di qua `tach_y` / `nhan_cau_hoi` — de so lieu cu khong doi."""
    return bool(re.search(r"[.?!;…]", van or ""))


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", str(s or ""))


def _cat_dai(van: str, a: int, b: int) -> List[Tuple[int, int]]:
    """Cat [a, b) thanh cac khuc <= TOI_DA_TU tu, giu vi tri trong van goc."""
    tu = [(m.start() + a, m.end() + a) for m in re.finditer(r"\S+", van[a:b])]
    return [(tu[i][0], tu[min(i + TOI_DA_TU, len(tu)) - 1][1]) for i in range(0, len(tu), TOI_DA_TU)]


def _thu_gon(van: str, a: int, b: int) -> Tuple[int, int]:
    while a < b and van[a] in " ,\t":
        a += 1
    while b > a and van[b - 1] in " ,\t":
        b -= 1
    return a, b


def tach_y(van: str) -> List[Tuple[int, int]]:
    """-> cac khoang [a, b) cua tung y trong `van`. Co dau cau thi tach theo dau; khuc
    nao van dai va khong co dau thi tach tiep theo tu noi; cuoi cung cat khuc > 25 tu."""
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


def nhan_cau_hoi(van: str) -> bool:
    """Cau hoi khi: co "?"; hoac tieu tu hoi cuoi cau ("không", "chưa ạ", "à", "hả"...);
    hoac mau "có ... không"; hoac tu hoi ("gì", "đâu", "mấy"...). Cau tra loi ngan
    ("dạ không", "có ạ") KHONG phai cau hoi du ket thuc bang "không"."""
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
        # "em không ho" khong phai cau hoi: "không" phai dung CUOI (chi con tieu tu sau no).
        return True
    return bool(_TU_HOI.search(t.rstrip(".! "))) and not re.search(r"(?<!\w)(không|chưa) (biết|nhớ|rõ)(?!\w)", t)


def bo_tu_dem(van: str) -> str:
    """Bo tu dem dung rieng ("ờ", "ừm", "à" dau/giua cau) va tu lap lien ("không không"),
    giu "à" cuoi cau hoi ("bé sốt à")."""
    t = _nfc(van).strip()
    cuoi_a = bool(re.search(r"(?<!\w)à\s*[?]?\s*$", t)) and len(t.split()) > 1
    than = re.sub(r"(?<!\w)à\s*[?]?\s*$", "", t) if cuoi_a else t
    than = _DEM.sub("", than)
    than = re.sub(r"(?<!\w)(\w+)(\s+\1)+(?!\w)", r"\1", than)
    than = re.sub(r"\s{2,}", " ", than).strip()
    return f"{than} à" if cuoi_a else than
