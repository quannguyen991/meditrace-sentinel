"""Critical clinical tokens in a Vietnamese transcript.

Used ONLY to compare two transcripts (ASR disagreement, benchmark scoring). It never
rewrites the transcript: the text MediTrace receives stays what the recogniser heard.

Categories:
    thuoc        drug names (from a small lexicon)
    lieu         (value, unit) pairs: 5 mg, 50 mg, 500 mg, 10 ml ...
    tan_suat     doses per day: "ngày 2 lần" -> 2
    thoi_gian    durations and anchors: (1, "ngày"), (10, "ngày"), "hôm qua" ...
    phu_dinh     negation words: không, chưa, chưa từng, chẳng
    trang_thai   medication state: đang dùng, đã ngừng, mới bắt đầu
    nguoi        who: bệnh nhân, bố, mẹ, ông, bà, vợ, chồng, con, cháu ...

Number words are parsed to integers so that "năm trăm mi li gam" and "500 mg" compare
equal, while "5 mg" and "50 mg" do not.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Optional

# Ten thuoc hay gap trong bo du lieu va trong yeu cau kiem thu. Moi thuoc mot ten
# chuan kem cac cach viet chap nhan duoc (khong tinh phien am kieu "a mốc xi lin").
THUOC = {
    "amoxicillin": ("amoxicillin", "amoxicilin", "amoxicilline", "amoxycillin"),
    "penicillin": ("penicillin", "penicilin", "penicilline"),
    "metformin": ("metformin", "metformine"),
    "paracetamol": ("paracetamol", "paracetamon"),
    "ibuprofen": ("ibuprofen", "ibuprofene"),
    "omeprazole": ("omeprazole", "omeprazol"),
    "salbutamol": ("salbutamol",),
    "cefuroxime": ("cefuroxime", "cefuroxim"),
    "azithromycin": ("azithromycin", "azithromycine"),
    "amlodipine": ("amlodipine", "amlodipin"),
    "aspirin": ("aspirin", "aspirine"),
    "prednisolone": ("prednisolone", "prednisolon"),
}
_BIEN_THE = {v: k for k, vs in THUOC.items() for v in vs}

_SO = {"không": 0, "một": 1, "mốt": 1, "hai": 2, "ba": 3, "bốn": 4, "tư": 4, "năm": 5,
       "lăm": 5, "sáu": 6, "bảy": 7, "tám": 8, "chín": 9}
_DON_VI_LIEU = {"mg": "mg", "ml": "ml", "gam": "g", "g": "g", "viên": "viên", "mcg": "mcg"}
_DON_VI_THOI_GIAN = {"ngày", "tuần", "tháng", "năm", "giờ", "hôm"}
_MOC = ("hôm qua", "hôm nay", "hôm kia", "tuần trước", "tháng trước", "năm ngoái",
        "năm trước", "sáng nay", "tối qua")
_PHU_DINH = ("chưa từng", "chưa bao giờ", "không có", "không", "chưa", "chẳng")
_TRANG_THAI = {"đang dùng": "dang_dung", "đang uống": "dang_dung",
               "đã ngừng": "da_ngung", "đã dừng": "da_ngung", "ngừng": "da_ngung",
               "mới bắt đầu": "moi_bat_dau", "mới dùng": "moi_bat_dau", "mới uống": "moi_bat_dau"}
_NGUOI = ("bệnh nhân", "bố", "mẹ", "ông", "bà", "vợ", "chồng", "con", "cháu", "anh", "chị",
          "em", "nhà tôi", "ổng", "bả")


def chuan_hoa(text: str) -> str:
    """Chu thuong, NFC, bo dau cau, gop don vi lieu viet roi ("mi li gam" -> "mg")."""
    t = unicodedata.normalize("NFC", (text or "").lower())
    t = re.sub(r"(\d)\s*(mg|ml|mcg|g)\b", r"\1 \2", t)
    t = re.sub(r"\bmi[\s-]*li[\s-]*gr?am\b|\bmilli[\s-]*grams?\b", "mg", t)
    t = re.sub(r"\bmi[\s-]*li[\s-]*lít\b|\bmililít\b", "ml", t)
    t = re.sub(r"\bmi[\s-]*crô[\s-]*gam\b", "mcg", t)
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _doc_so(w: list[str], i: int) -> Optional[tuple[int, int]]:
    """Doc mot so bat dau tai w[i] -> (gia tri, vi tri sau so) hoac None."""
    if i >= len(w):
        return None
    if w[i].isdigit():
        return int(w[i]), i + 1
    tong, j = 0, i
    # hang tram: <so> tram [linh/le <so> | chuc]
    if j + 1 < len(w) and w[j] in _SO and w[j + 1] == "trăm":
        tong, j = _SO[w[j]] * 100, j + 2
        if j + 1 < len(w) and w[j] in ("linh", "lẻ") and w[j + 1] in _SO:
            return tong + _SO[w[j + 1]], j + 2
    # hang chuc
    if j < len(w) and w[j] == "mười":
        tong += 10
        j += 1
        if j < len(w) and w[j] in _SO and w[j] not in ("không",) and not (j + 1 < len(w) and w[j + 1] in ("trăm", "mươi")):
            tong += _SO[w[j]]
            j += 1
        return tong, j
    if j + 1 < len(w) and w[j] in _SO and w[j + 1] == "mươi":
        tong += _SO[w[j]] * 10
        j += 2
        if j < len(w) and w[j] in _SO and w[j] != "không":
            tong += _SO[w[j]]
            j += 1
        return tong, j
    if j < len(w) and w[j] in _SO and w[j] != "không":
        return tong + _SO[w[j]], j + 1
    return (tong, j) if j > i else None


def trich(text: str) -> dict[str, Any]:
    """-> cac tap tu khoa quan trong trong mot doan chu."""
    t = chuan_hoa(text)
    w = t.split()
    ra = {"thuoc": set(), "lieu": set(), "tan_suat": set(), "thoi_gian": set(),
          "phu_dinh": [], "trang_thai": set(), "nguoi": []}
    for x in w:
        if x in _BIEN_THE:
            ra["thuoc"].add(_BIEN_THE[x])
    i = 0
    while i < len(w):
        # tan suat: "ngay <so> lan"
        if w[i] == "ngày" and (s := _doc_so(w, i + 1)) and s[1] < len(w) and w[s[1]] == "lần":
            ra["tan_suat"].add(s[0])
            i = s[1] + 1
            continue
        s = _doc_so(w, i)
        if s and s[1] < len(w):
            gia, j = s
            dv = w[j]
            if dv in _DON_VI_LIEU:
                ra["lieu"].add((gia, _DON_VI_LIEU[dv]))
                i = j + 1
                continue
            if dv in _DON_VI_THOI_GIAN and not (dv == "năm" and w[i] == "năm"):
                ra["thoi_gian"].add((gia, dv))
                i = j + 1
                continue
            if dv == "lần" and j + 1 < len(w) and w[j + 1] in ("một", "mỗi") and j + 2 < len(w) and w[j + 2] == "ngày":
                ra["tan_suat"].add(gia)
                i = j + 3
                continue
        i += 1
    for m in _MOC:
        if re.search(rf"(?<!\w){m}(?!\w)", t):
            ra["thoi_gian"].add(m)
    for p in _PHU_DINH:                       # dai truoc ngan: "chưa từng" truoc "chưa"
        for _ in re.finditer(rf"(?<!\w){p}(?!\w)", t):
            ra["phu_dinh"].append(p)
    # dem moi tu phu dinh mot lan theo vi tri: bo lan trung do "chưa từng" chua "chưa"
    ra["phu_dinh"] = sorted(ra["phu_dinh"])
    for k, v in _TRANG_THAI.items():
        if re.search(rf"(?<!\w){k}(?!\w)", t):
            ra["trang_thai"].add(v)
    for n in _NGUOI:
        for _ in re.finditer(rf"(?<!\w){n}(?!\w)", t):
            ra["nguoi"].append(n)
    ra["nguoi"] = sorted(ra["nguoi"])
    return ra


# Loai -> ma ly do khi hai ban chep khac nhau
LY_DO = {"thuoc": "drug_name_disagreement", "lieu": "dosage_disagreement",
         "tan_suat": "dosage_disagreement", "thoi_gian": "time_disagreement",
         "phu_dinh": "negation_disagreement", "trang_thai": "medication_state_disagreement",
         "nguoi": "subject_disagreement"}


def khac_nhau(a: dict[str, Any], b: dict[str, Any]) -> list[str]:
    """-> danh sach loai tu khoa quan trong ma hai ban trich KHAC nhau."""
    return [k for k in LY_DO if a[k] != b[k]]
