"""Critical clinical tokens in a Vietnamese transcript.

Used ONLY to compare two transcripts (ASR disagreement, benchmark scoring). It never
rewrites the transcript: the text MediTrace receives stays what the recogniser heard.

Categories:
    thuoc        drug names (expanded Vietnamese clinical lexicon)
    lieu         (value, unit) pairs: 5 mg, 500 mg, 10 ml, 2 nhát, 1 ống, 10 ui ...
    tan_suat     doses per day: "ngày 2 lần" -> 2
    thoi_gian    durations and anchors: (1, "ngày"), (10, "ngày"), "hôm qua" ...
    phu_dinh     negation words: không, chưa, chưa từng, chẳng
    trang_thai   medication state: đang dùng, đã ngừng, mới bắt đầu
    nguoi        who: bệnh nhân, bố, mẹ, ông, bà, vợ, chồng, con, cháu ...
    muc_do_dau   pain descriptors: dữ dội, âm ỉ, quặn thắt, nhói buốt, nóng rát ...

Number words are parsed to integers so that "năm trăm mi li gam" and "500 mg" compare
equal, while "5 mg" and "50 mg" do not.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Optional

# Danh mục thuốc phổ biến tại phòng khám & bệnh viện Việt Nam
# Khóa: tên hoạt chất/chuẩn hóa; Giá trị: các biến thể viết và biệt dược hay gặp
THUOC = {
    # Kháng sinh
    "amoxicillin": ("amoxicillin", "amoxicilin", "amoxicilline", "amoxycillin", "clamoxyl"),
    "augmentin": ("augmentin", "augmentine", "klamentin"),
    "penicillin": ("penicillin", "penicilin", "penicilline"),
    "cefixime": ("cefixime", "cefixim", "meiact", "zifi"),
    "ciprofloxacin": ("ciprofloxacin", "ciprofloxacine", "ciprobay"),
    "cefuroxime": ("cefuroxime", "cefuroxim", "zinnat"),
    "azithromycin": ("azithromycin", "azithromycine", "zithromax"),
    "levofloxacin": ("levofloxacin", "levofloxacine", "tavanic"),
    "clarithromycin": ("clarithromycin", "klacid"),
    "ceftriaxone": ("ceftriaxone", "rocephin"),
    "doxycycline": ("doxycycline", "doxycyclin"),
    "metronidazole": ("metronidazole", "flagyl", "klion"),

    # Hạ sốt, giảm đau, kháng viêm & Corticoid
    "paracetamol": ("paracetamol", "paracetamon", "para"),
    "efferalgan": ("efferalgan", "eferalgan"),
    "hapacol": ("hapacol",),
    "panadol": ("panadol",),
    "ibuprofen": ("ibuprofen", "ibuprofene", "brufen"),
    "aspirin": ("aspirin", "aspirine", "aspilet"),
    "meloxicam": ("meloxicam", "mobic"),
    "celecoxib": ("celecoxib", "celebrex"),
    "diclofenac": ("diclofenac", "voltaren"),
    "prednisolone": ("prednisolone", "prednisolon"),
    "methylprednisolone": ("methylprednisolone", "medrol"),
    "dexamethasone": ("dexamethasone", "dexa"),

    # Tim mạch, huyết áp, mỡ máu
    "amlodipine": ("amlodipine", "amlodipin", "amlor"),
    "losartan": ("losartan", "cozaar"),
    "telmisartan": ("telmisartan", "micardis"),
    "atorvastatin": ("atorvastatin", "lipitor"),
    "rosuvastatin": ("rosuvastatin", "crestor"),
    "bisoprolol": ("bisoprolol", "concor"),
    "captopril": ("captopril",),
    "enalapril": ("enalapril", "renitec"),
    "clopidogrel": ("clopidogrel", "plavix"),

    # Dạ dày, tiêu hóa
    "omeprazole": ("omeprazole", "omeprazol"),
    "esomeprazole": ("esomeprazole", "nexium"),
    "pantoprazole": ("pantoprazole", "pantoloc"),
    "phosphalugel": ("phosphalugel", "photphalugel"),
    "gaviscon": ("gaviscon",),

    # Đái tháo đường
    "metformin": ("metformin", "metformine", "glucophage"),
    "gliclazide": ("gliclazide", "diamicron"),
    "glimepiride": ("glimepiride", "amaryl"),
    "insulin": ("insulin",),

    # Hô hấp, chống dị ứng
    "salbutamol": ("salbutamol",),
    "ventolin": ("ventolin",),
    "seretide": ("seretide",),
    "symbicort": ("symbicort",),
    "cetirizine": ("cetirizine", "zyrtec"),
    "loratadine": ("loratadine", "claritin"),
    "fexofenadine": ("fexofenadine", "telfast"),
}
_BIEN_THE = {v: k for k, vs in THUOC.items() for v in vs}

_SO = {
    "không": 0, "một": 1, "mốt": 1, "hai": 2, "ba": 3, "bốn": 4, "tư": 4, "năm": 5,
    "lăm": 5, "sáu": 6, "bảy": 7, "tám": 8, "chín": 9,
}

# Đơn vị liều dùng thực tế
_DON_VI_LIEU = {
    "mg": "mg", "ml": "ml", "gam": "g", "g": "g", "mcg": "mcg",
    "viên": "viên", "ống": "ống", "gói": "gói", "giọt": "giọt",
    "nhát": "nhát", "xịt": "nhát", "ui": "ui",
    "chai": "chai", "lọ": "lọ", "thìa": "thìa", "muỗng": "thìa",
    "vỉ": "vỉ", "tép": "tép", "miếng": "miếng",
}

_DON_VI_THOI_GIAN = {"ngày", "tuần", "tháng", "năm", "giờ", "hôm"}
_MOC = (
    "hôm qua", "hôm nay", "hôm kia", "tuần trước", "tháng trước", "năm ngoái",
    "năm trước", "sáng nay", "tối qua",
)
_PHU_DINH = ("chưa từng", "chưa bao giờ", "không có", "không", "chưa", "chẳng")
_TRANG_THAI = {
    "đang dùng": "dang_dung", "đang uống": "dang_dung",
    "đã ngừng": "da_ngung", "đã dừng": "da_ngung", "ngừng": "da_ngung",
    "mới bắt đầu": "moi_bat_dau", "mới dùng": "moi_bat_dau", "mới uống": "moi_bat_dau",
}
_NGUOI = (
    "bệnh nhân", "bố", "mẹ", "ông", "bà", "vợ", "chồng", "con", "cháu", "anh", "chị",
    "em", "nhà tôi", "ổng", "bả",
)

# Từ điển mô tả tính chất, mức độ & diễn tiến đau lâm sàng
_MUC_DO_DAU = {
    # Mức độ / Cường độ
    "dữ dội": "du_doi", "kinh khủng": "du_doi", "quằn quại": "du_doi", "khốc liệt": "du_doi",
    "không chịu nổi": "du_doi",
    "âm ỉ": "am_i", "râm ran": "am_i", "ê ẩm": "am_i", "ngầm ngầm": "am_i",
    "đau nhẹ": "nhe", "hơi đau": "nhe", "hơi nhức": "nhe", "thoáng qua": "nhe",

    # Tính chất cảm giác đau
    "đau nhói": "nhoi", "nhói": "nhoi", "nhói buốt": "nhoi", "chói buốt": "nhoi", "nhói lên": "nhoi",
    "đau quặn": "quan", "quặn": "quan", "quặn thắt": "quan", "quặn bụng": "quan",
    "quặn ruột": "quan", "xoắn vặn": "quan",
    "thắt ngực": "that_nguc", "bóp nghẹt": "that_nguc", "đè nặng": "that_nguc",
    "tức ngực": "that_nguc", "nghẹt thở": "that_nguc",
    "rát bỏng": "rat_bong", "nóng rát": "rat_bong", "bỏng rát": "rat_bong", "cháy rát": "rat_bong",
    "nhức buốt": "nhuc_buot", "buốt": "nhuc_buot", "nhức nhối": "nhuc_buot", "buốt óc": "nhuc_buot",
    "căng tức": "tuc", "tưng tức": "tuc", "tức bụng": "tuc", "tức hông": "tuc",
    "châm chích": "cham_chich", "như kim châm": "cham_chich", "kiến cắn": "cham_chich", "kiến bò": "cham_chich",

    # Nhịp điệu / Diễn tiến
    "từng cơn": "tung_con", "cơn đau": "tung_con", "ngắt quãng": "tung_con",
    "liên tục": "lien_tuc", "kéo dài": "lien_tuc", "triền miên": "lien_tuc", "không dứt": "lien_tuc",
    "đột ngột": "dot_ngot", "bất thình lình": "dot_ngot", "sét đánh": "dot_ngot",
}


def chuan_hoa(text: str) -> str:
    """Chu thuong, NFC, quy chuan don vi ghep, don vi dac thu, tach so va bo dau cau."""
    t = unicodedata.normalize("NFC", (text or "").lower())

    # Quy chuẩn đơn vị phức và tiếng Việt viết rời
    t = re.sub(r"\bmi[\s-]*li[\s-]*gr?am\b|\bmilli[\s-]*grams?\b", "mg", t)
    t = re.sub(r"\bmi[\s-]*li[\s-]*lít\b|\bmililít\b", "ml", t)
    t = re.sub(r"\bmi[\s-]*crô[\s-]*gam\b", "mcg", t)
    t = re.sub(r"\bnhát\s+xịt\b", "nhát", t)
    t = re.sub(r"\b(đơn\s+vị|u[\.\s]*i\.?|iu)\b", "ui", t)
    t = re.sub(r"\b(thìa|muỗng)\s+(cà\s+phê|cafe|canh)\b", "thìa", t)

    # Tách số dính liền với đơn vị đo lường (vi du: 500mg -> 500 mg, 2viên -> 2 viên)
    t = re.sub(
        r"(\d)\s*(mg|ml|mcg|g|viên|ống|gói|giọt|nhát|xịt|ui|chai|lọ|thìa|muỗng|vỉ|tép|miếng)\b",
        r"\1 \2",
        t,
    )
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
    ra: dict[str, Any] = {
        "thuoc": set(),
        "lieu": set(),
        "tan_suat": set(),
        "thoi_gian": set(),
        "phu_dinh": [],
        "trang_thai": set(),
        "nguoi": [],
        "muc_do_dau": set(),
    }

    # Bắt tên thuốc
    for x in w:
        if x in _BIEN_THE:
            ra["thuoc"].add(_BIEN_THE[x])

    # Bắt liều dùng và tần suất
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

    # Bắt mốc thời gian
    for m in _MOC:
        if re.search(rf"(?<!\w){m}(?!\w)", t):
            ra["thoi_gian"].add(m)

    # Bắt phủ định
    for p in _PHU_DINH:
        for _ in re.finditer(rf"(?<!\w){p}(?!\w)", t):
            ra["phu_dinh"].append(p)
    ra["phu_dinh"] = sorted(ra["phu_dinh"])

    # Bắt trạng thái dùng thuốc
    for k, v in _TRANG_THAI.items():
        if re.search(rf"(?<!\w){k}(?!\w)", t):
            ra["trang_thai"].add(v)

    # Bắt đối tượng người
    for n in _NGUOI:
        for _ in re.finditer(rf"(?<!\w){n}(?!\w)", t):
            ra["nguoi"].append(n)
    ra["nguoi"] = sorted(ra["nguoi"])

    # Bắt mức độ, tính chất & diễn tiến đau
    for k, v in _MUC_DO_DAU.items():
        if re.search(rf"(?<!\w){k}(?!\w)", t):
            ra["muc_do_dau"].add(v)

    return ra


# Loai -> ma ly do khi hai ban chep khac nhau
LY_DO = {
    "thuoc": "drug_name_disagreement",
    "lieu": "dosage_disagreement",
    "tan_suat": "dosage_disagreement",
    "thoi_gian": "time_disagreement",
    "phu_dinh": "negation_disagreement",
    "trang_thai": "medication_state_disagreement",
    "nguoi": "subject_disagreement",
    "muc_do_dau": "pain_descriptor_disagreement",
}


def khac_nhau(a: dict[str, Any], b: dict[str, Any]) -> list[str]:
    """-> danh sach loai tu khoa quan trong ma hai ban trich KHAC nhau."""
    return [k for k in LY_DO if a[k] != b[k]]