# -*- coding: utf-8 -*-
"""Động cơ Kiểm tra Dị ứng Chéo Thuốc theo Nhóm ATC & Chuỗi nhánh Hóa học (Cross-Reactivity Engine).

Hỗ trợ:
1. Khớp trực tiếp hoạt chất & thành phần thuốc phối hợp (VD: Augmentin -> amoxicillin + clavulanate, Bactrim -> co-trimoxazole).
2. Nhóm Beta-lactam theo chuỗi nhánh R1 & phân nhóm cấu trúc:
   - Penicillin <-> Aminopenicillin (CHONG_CHI_DINH)
   - Penicillin / Aminopenicillin <-> Cephalosporin thế hệ 1 / chung chuỗi nhánh R1 (CHONG_CHI_DINH)
   - Penicillin / Aminopenicillin <-> Cephalosporin thế hệ 2/3/4 khác chuỗi nhánh R1 (THAN_TRONG)
   - Cephalosporin <-> Cephalosporin cùng chuỗi nhánh R1 (CHONG_CHI_DINH) vs khác R1 (THAN_TRONG)
   - Ceftazidime <-> Aztreonam (cùng chuỗi nhánh R1 -> CHONG_CHI_DINH; Penicillin <-> Aztreonam an toàn)
   - Penicillin / Cephalosporin <-> Carbapenem (THAN_TRONG)
3. Nhóm Sulfonamide: kháng sinh sulfonamide <-> nhau (CHONG_CHI_DINH) vs sulfonamide không kháng khuẩn (THAN_TRONG).
4. Nhóm NSAID: ức chế COX-1 không chọn lọc <-> nhau (CHONG_CHI_DINH) vs ức chế chọn lọc COX-2 (THAN_TRONG).
5. Nhóm Macrolide, Fluoroquinolone (THAN_TRONG nội nhóm, CHONG_CHI_DINH khi khớp trực tiếp) & ACEi (CHONG_CHI_DINH phù mạch).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set, Tuple

from src import tri_thuc_thuoc as _ttt

CHONG_CHI_DINH = "CHONG_CHI_DINH"
THAN_TRONG = "THAN_TRONG"

_MUC_DO_UU_TIEN = {CHONG_CHI_DINH: 2, THAN_TRONG: 1}

# Biệt dược / tên phối hợp / chính tả phổ biến tại Việt Nam -> danh sách hoạt chất chuẩn
_BIET_DUOC_VA_PHOI_HOP: Dict[str, Tuple[str, ...]] = {
    # Beta-lactam Penicillins & combos
    "augmentin": ("amoxicillin", "clavulanate"),
    "co-amoxiclav": ("amoxicillin", "clavulanate"),
    "co amoxiclav": ("amoxicillin", "clavulanate"),
    "amoxiclav": ("amoxicillin", "clavulanate"),
    "amoxicillin/clavulanate": ("amoxicillin", "clavulanate"),
    "amoxicillin-clavulanate": ("amoxicillin", "clavulanate"),
    "amoxicillin/clavulanic": ("amoxicillin", "clavulanate"),
    "klamentin": ("amoxicillin", "clavulanate"),
    "curam": ("amoxicillin", "clavulanate"),
    "clamoxyl": ("amoxicillin",),
    "osa": ("amoxicillin",),
    "unasyn": ("ampicillin", "sulbactam"),
    "sultamicillin": ("ampicillin", "sulbactam"),
    "tazocin": ("piperacillin", "tazobactam"),
    "zosyn": ("piperacillin", "tazobactam"),
    "penicilin": ("penicillin",),
    "penicillin g": ("benzylpenicillin",),
    "penicillin v": ("phenoxymethylpenicillin",),
    # Cephalosporins
    "keflex": ("cephalexin",),
    "cefalexin": ("cephalexin",),
    "cephalexin": ("cephalexin",),
    "duricef": ("cefadroxil",),
    "kefzol": ("cefazolin",),
    "ancef": ("cefazolin",),
    "ceclor": ("cefaclor",),
    "zinnat": ("cefuroxime",),
    "zinacef": ("cefuroxime",),
    "suprax": ("cefixime",),
    "cefixim": ("cefixime",),
    "omnicef": ("cefdinir",),
    "claforan": ("cefotaxime",),
    "rocephin": ("ceftriaxone",),
    "fortum": ("ceftazidime",),
    "maxipime": ("cefepime",),
    "cefobid": ("cefoperazone",),
    "sulperazon": ("cefoperazone", "sulbactam"),
    # Monobactam & Carbapenems
    "azactam": ("aztreonam",),
    "meronem": ("meropenem",),
    "tienam": ("imipenem",),
    "imipenem/cilastatin": ("imipenem",),
    "invanz": ("ertapenem",),
    # Sulfonamides
    "bactrim": ("sulfamethoxazole", "trimethoprim"),
    "biseptol": ("sulfamethoxazole", "trimethoprim"),
    "septrin": ("sulfamethoxazole", "trimethoprim"),
    "co-trimoxazole": ("sulfamethoxazole", "trimethoprim"),
    "cotrimoxazole": ("sulfamethoxazole", "trimethoprim"),
    "cotrimoxazol": ("sulfamethoxazole", "trimethoprim"),
    "trimethoprim-sulfamethoxazole": ("sulfamethoxazole", "trimethoprim"),
    "trimethoprim/sulfamethoxazole": ("sulfamethoxazole", "trimethoprim"),
    "sulfamid": ("sulfonamide",),
    "sulfa": ("sulfonamide",),
    "lasix": ("furosemide",),
    "furosemid": ("furosemide",),
    "hypothiazid": ("hydrochlorothiazide",),
    "natrilix": ("indapamide",),
    "celebrex": ("celecoxib",),
    "amaryl": ("glimepiride",),
    "diamicron": ("gliclazide",),
    "diamox": ("acetazolamide",),
    # NSAIDs
    "advil": ("ibuprofen",),
    "brufen": ("ibuprofen",),
    "voltaren": ("diclofenac",),
    "cataflam": ("diclofenac",),
    "mobic": ("meloxicam",),
    "feldene": ("piroxicam",),
    "naprosyn": ("naproxen",),
    "aleve": ("naproxen",),
    "arcoxia": ("etoricoxib",),
    "toradol": ("ketorolac",),
    "ponstan": ("mefenamic acid",),
    "aspegic": ("aspirin",),
    # Macrolides
    "zithromax": ("azithromycin",),
    "klacid": ("clarithromycin",),
    "rovamycine": ("spiramycin",),
    "rulid": ("roxithromycin",),
    "erythrocin": ("erythromycin",),
    # Fluoroquinolones
    "ciprobay": ("ciprofloxacin",),
    "tavanic": ("levofloxacin",),
    "avelox": ("moxifloxacin",),
    "oflocet": ("ofloxacin",),
    "noroxin": ("norfloxacin",),
    # ACE inhibitors
    "renitec": ("enalapril",),
    "capoten": ("captopril",),
    "lopril": ("captopril",),
    "zestril": ("lisinopril",),
    "coversyl": ("perindopril",),
    "tritace": ("ramipril",),
    # Other common Vietnamese aliases
    "zyloric": ("allopurinol",),
    "panadol": ("paracetamol",),
    "hapacol": ("paracetamol",),
    "efferalgan": ("paracetamol",),
    "acetaminophen": ("paracetamol",),
    "glucophage": ("metformin",),
    "panfor": ("metformin",),
    "sintrom": ("acenocoumarol",),
    "coumadin": ("warfarin",),
    "plavix": ("clopidogrel",),
    "losec": ("omeprazole",),
    "nexium": ("esomeprazole",),
    "lipitor": ("atorvastatin",),
    "crestor": ("rosuvastatin",),
    "norvasc": ("amlodipine",),
    "cozaar": ("losartan",),
    "aldactone": ("spironolactone",),
}

# Phân nhóm dược lý cho ma trận dị ứng chéo
_PENICILLINS: Set[str] = {
    "penicillin", "benzylpenicillin", "phenoxymethylpenicillin",
    "ampicillin", "amoxicillin", "cloxacillin", "oxacillin",
    "dicloxacillin", "flucloxacillin", "piperacillin", "ticarcillin",
    "aminopenicillin",
}
_AMINOPENICILLINS: Set[str] = {"amoxicillin", "ampicillin", "aminopenicillin"}

# Cephalosporin thế hệ 1 / cùng chuỗi nhánh R1 với aminopenicillin
_CEPH_GEN1_SHARED_R1: Set[str] = {
    "cephalexin", "cefadroxil", "cefazolin", "cefradine", "cephalothin", "cefaclor",
}
# Cephalosporin thế hệ 2/3/4 khác chuỗi nhánh R1 với aminopenicillin
_CEPH_DISTINCT_R1: Set[str] = {
    "cefuroxime", "cefixime", "cefdinir", "cefotaxime",
    "ceftriaxone", "ceftazidime", "cefepime", "cefpodoxime", "cefoperazone", "cefoxitin",
}
_CEPH_ALL: Set[str] = _CEPH_GEN1_SHARED_R1 | _CEPH_DISTINCT_R1 | {"cephalosporin"}

# Cụm Cephalosporin có chuỗi nhánh R1 tương đồng lẫn nhau
_CEPH_R1_CLUSTERS: Tuple[Set[str], ...] = (
    {"cephalexin", "cefadroxil", "cefaclor", "cefradine"},
    {"cefotaxime", "ceftriaxone", "cefepime"},
    {"ceftazidime", "aztreonam"},  # Chung chuỗi nhánh R1 giữa Ceftazidime và Aztreonam
)

_CARBAPENEMS: Set[str] = {"meropenem", "imipenem", "ertapenem", "doripenem", "carbapenem"}

_SULFA_ANTIBIOTIC: Set[str] = {
    "sulfamethoxazole", "co-trimoxazole", "sulfadiazine", "sulfacetamide",
    "sulfasalazine", "sulfonamide",
}
_SULFA_NON_ANTIBIOTIC: Set[str] = {
    "furosemide", "hydrochlorothiazide", "indapamide", "celecoxib",
    "glimepiride", "gliclazide", "acetazolamide", "torsemide", "bumetanide",
    "chlorthalidone", "metolazone", "glibenclamide", "glipizide", "dapsone",
}

_NSAID_COX1: Set[str] = {
    "aspirin", "ibuprofen", "diclofenac", "naproxen", "meloxicam",
    "piroxicam", "ketoprofen", "indomethacin", "ketorolac",
    "mefenamic acid", "tenoxicam", "aceclofenac", "dexketoprofen", "nsaid",
}
_NSAID_COX2_SELECTIVE: Set[str] = {"celecoxib", "etoricoxib", "parecoxib"}

_MACROLIDES: Set[str] = {
    "erythromycin", "clarithromycin", "azithromycin", "spiramycin", "roxithromycin", "josamycin", "macrolide",
}

_FLUOROQUINOLONES: Set[str] = {
    "ciprofloxacin", "levofloxacin", "moxifloxacin", "ofloxacin", "norfloxacin", "pefloxacin", "fluoroquinolone", "quinolone",
}

_ACEI: Set[str] = {
    "enalapril", "captopril", "lisinopril", "perindopril", "ramipril",
    "imidapril", "benazepril", "quinapril", "fosinopril", "acei",
}
_ARB: Set[str] = {
    "losartan", "valsartan", "telmisartan", "irbesartan", "candesartan", "olmesartan", "arb",
}

_CHUAN_TEN_KHONG_E: Dict[str, str] = {
    "cefixim": "cefixime",
    "cefuroxim": "cefuroxime",
    "cefotaxim": "cefotaxime",
    "ceftriaxon": "ceftriaxone",
    "ceftazidim": "ceftazidime",
    "cefepim": "cefepime",
    "cefpodoxim": "cefpodoxime",
    "furosemid": "furosemide",
    "glimepirid": "glimepiride",
    "gliclazid": "gliclazide",
    "acetazolamid": "acetazolamide",
    "indapamid": "indapamide",
    "hydrochlorothiazid": "hydrochlorothiazide",
    "amlodipin": "amlodipine",
    "omeprazol": "omeprazole",
    "esomeprazol": "esomeprazole",
    "pantoprazol": "pantoprazole",
    "lansoprazol": "lansoprazole",
    "spironolacton": "spironolactone",
    "theophyllin": "theophylline",
    "azathioprin": "azathioprine",
    "carbamazepin": "carbamazepine",
    "amiodaron": "amiodarone",
    "fluoroquinolon": "fluoroquinolone",
    "macrolid": "macrolide",
    "sulfonamid": "sulfonamide",
    "betalactam": "beta-lactam",
}


def _chuan_ten_don(tok: str) -> str:
    s = re.sub(r"\s+", " ", (tok or "").strip().lower())
    s = re.sub(r"^(thuốc|viên|gói|ống|chai|tiêm|uống)\s+", "", s)
    s = re.sub(r"\s+\d+(?:[.,]\d+)?\s*(mg|g|gam|mcg|µg|ml|ui|iu|%)\b.*$", "", s).strip()
    if s in _CHUAN_TEN_KHONG_E:
        return _CHUAN_TEN_KHONG_E[s]
    if len(s) > 5 and s.endswith("e") and s[:-1] in _CHUAN_TEN_KHONG_E:
        return _CHUAN_TEN_KHONG_E[s[:-1]]
    return s


def _phan_giai_thanh_phan(raw: str) -> List[str]:
    """Phân giải một chuỗi tên thuốc/chất dị ứng thành tập hoạt chất/nhóm chuẩn."""
    s = re.sub(r"\s+", " ", (raw or "").strip().lower())
    if not s:
        return []
    # Bỏ tiền tố kiểu "dị ứng với ..."
    s_clean = re.sub(r"^(?:bị\s+)?(?:dị\s+ứng|mẫn\s+cảm|phản\s+vệ|sốc\s+phản\s+vệ)\s*(?:với|do|khi\s+dùng)?\s*", "", s).strip()
    if not s_clean:
        return []

    if "kháng viêm không steroid" in s_clean or "nhóm nsaid" in s_clean:
        return ["nsaid"]
    if "beta-lactam" in s_clean or "beta lactam" in s_clean or "betalactam" in s_clean:
        return ["beta-lactam"]
    if "ức chế men chuyển" in s_clean:
        return ["acei"]

    ket_qua: List[str] = []
    da_co: Set[str] = set()

    def _them(ten: Optional[str]) -> None:
        if not ten:
            return
        t = _chuan_ten_don(ten)
        if t and t not in da_co:
            da_co.add(t)
            ket_qua.append(t)

    # 1. Khớp nguyên chuỗi hoặc tách dấu "/" trong từ điển biệt dược & phối hợp
    s_norm = _chuan_ten_don(s_clean)
    for khoa in (s_clean, s_norm):
        if khoa in _BIET_DUOC_VA_PHOI_HOP:
            for tp in _BIET_DUOC_VA_PHOI_HOP[khoa]:
                _them(tp)

    # 2. Tìm theo token / từ khóa dài trong chuỗi (VD: "augmentin 625 mg", "penicillin g")
    for bd, tps in sorted(_BIET_DUOC_VA_PHOI_HOP.items(), key=lambda kv: -len(kv[0])):
        if re.search(rf"(?<!\w){re.escape(bd)}(?!\w)", s_clean):
            for tp in tps:
                _them(tp)

    # 3. Tra `tri_thuc_thuoc` (hoạt chất + biệt dược nội bộ)
    hc_ttt = _ttt.hoat_chat(s_clean) or _ttt.hoat_chat(s_norm)
    if hc_ttt:
        # Một số mục trong tri_thuc_thuoc là combo như "amoxicillin/clavulanat" nếu có
        for phan in re.split(r"[/+]", hc_ttt):
            _them(phan)
    for m_rx in _ttt.regex_ten_thuoc().finditer(s_clean):
        hc_m = _ttt.hoat_chat(m_rx.group(1))
        if hc_m:
            for phan in re.split(r"[/+]", hc_m):
                _them(phan)

    # 4. Tách dấu "/" hoặc "+" nếu chưa khớp đủ
    if "/" in s_norm or "+" in s_norm:
        for phan in re.split(r"[/+]", s_norm):
            phan_c = _chuan_ten_don(phan)
            if phan_c in _BIET_DUOC_VA_PHOI_HOP:
                for tp in _BIET_DUOC_VA_PHOI_HOP[phan_c]:
                    _them(tp)
            elif phan_c:
                _them(_ttt.hoat_chat(phan_c) or phan_c)

    if not ket_qua and s_norm:
        _them(s_norm)
    return ket_qua


def _trich_danh_sach_chuoi(du_lieu: Any, la_di_ung: bool = False) -> List[str]:
    """Chuẩn hóa đầu vào linh hoạt (str, list, tuple, set, list[dict]) thành danh sách tên giữ nguyên hiển thị."""
    if not du_lieu:
        return []
    muc_tho: List[Any]
    if isinstance(du_lieu, str):
        muc_tho = [x.strip() for x in re.split(r"[,;\n]+", du_lieu) if x.strip()]
    elif isinstance(du_lieu, dict):
        muc_tho = [du_lieu]
    elif isinstance(du_lieu, (list, tuple, set)):
        muc_tho = list(du_lieu)
    else:
        return []

    ra: List[str] = []
    for item in muc_tho:
        if item is None:
            continue
        if isinstance(item, dict):
            ten = (
                item.get("ten")
                or item.get("hoat_chat")
                or item.get("ten_thuoc")
                or item.get("chat_di_ung")
                or item.get("name")
                or item.get("noi_dung")
                or ""
            )
            ten_s = str(ten).strip()
        else:
            ten_s = str(item).strip()
        if not ten_s:
            continue
        if la_di_ung and ("," in ten_s or ";" in ten_s):
            for sub in re.split(r"[,;\n]+", ten_s):
                sub_s = sub.strip()
                if sub_s:
                    ra.append(sub_s)
        else:
            ra.append(ten_s)
    return ra


def _danh_gia_cap(hc_du: str, hc_th: str) -> Optional[Tuple[str, str, str, str]]:
    """Trả về (nhom_cheo, muc_do, co_che, khuyen_cao_thay_the) cho cặp (chất dị ứng, thành phần thuốc) hoặc None."""
    # 1. Khớp trực tiếp hoạt chất
    if hc_du == hc_th:
        return (
            "Khớp trực tiếp hoạt chất / thành phần thuốc",
            CHONG_CHI_DINH,
            f"Thuốc chứa chính hoạt chất '{hc_th}' mà người bệnh có tiền sử dị ứng.",
            f"Ngừng/không kê '{hc_th}', chuyển sang hoạt chất khác nhóm cấu trúc an toàn.",
        )

    # 2. Beta-lactam: nhóm chung "beta-lactam"
    if hc_du == "beta-lactam":
        if hc_th in _PENICILLINS or hc_th in _CEPH_ALL:
            return (
                "Beta-lactam (Nhóm dị ứng rộng)",
                CHONG_CHI_DINH,
                "Dị ứng nhóm Beta-lactam: nguy cơ phản ứng chéo nghiêm trọng với Penicillin và Cephalosporin.",
                "Tránh toàn bộ Penicillin/Cephalosporin; cân nhắc Macrolide, Fluoroquinolone hoặc Aztreonam tùy kháng sinh đồ.",
            )
        if hc_th in _CARBAPENEMS:
            return (
                "Beta-lactam (Nguy cơ chéo thấp với Carbapenem)",
                THAN_TRONG,
                "Carbapenem có tỷ lệ dị ứng chéo thấp (~1%) với nhóm Beta-lactam.",
                "Chỉ dùng khi thật cần thiết, thử test/theo dõi sát dấu hiệu phản vệ trong giờ đầu.",
            )

    # 3. Beta-lactam: Penicillin <-> Penicillin / Cephalosporin / Carbapenem / Aztreonam
    if hc_du in _PENICILLINS and hc_th in _PENICILLINS:
        return (
            "Beta-lactam (Penicillin / Aminopenicillin)",
            CHONG_CHI_DINH,
            f"Cùng cấu trúc nhân Penam/vòng beta-lactam giữa '{hc_du}' và '{hc_th}' (nguy cơ phản vệ chéo rất cao).",
            "Tránh mọi kháng sinh nhóm Penicillin; thay thế bằng Macrolide, Doxycycline, hoặc Cephalosporin khác chuỗi R1 nếu nhẹ.",
        )

    # Aminopenicillin/Penicillin <-> Cephalosporin thế hệ 1 / cùng chuỗi nhánh R1
    if (hc_du in _PENICILLINS and hc_th in _CEPH_GEN1_SHARED_R1) or (
        hc_du in _CEPH_GEN1_SHARED_R1 and hc_th in _PENICILLINS
    ):
        return (
            "Beta-lactam (Penicillin - Cephalosporin thế hệ 1 / chung chuỗi nhánh R1)",
            CHONG_CHI_DINH,
            f"'{hc_du}' và '{hc_th}' có tương đồng chuỗi nhánh R1 aminopenicillin/thế hệ 1 (nguy cơ dị ứng chéo ~10-15%).",
            "Tránh phối hợp/thay thế chéo; ưu tiên Cephalosporin thế hệ 2-3 khác chuỗi nhánh R1 (Cefuroxime, Ceftriaxone) hoặc nhóm Macrolide/Fluoroquinolone.",
        )

    # Penicillin <-> Cephalosporin thế hệ 2/3/4 khác chuỗi R1
    if (hc_du in _PENICILLINS and hc_th in _CEPH_DISTINCT_R1) or (
        hc_du in _CEPH_DISTINCT_R1 and hc_th in _PENICILLINS
    ):
        return (
            "Beta-lactam (Penicillin - Cephalosporin khác chuỗi nhánh R1)",
            THAN_TRONG,
            f"'{hc_th}' là Cephalosporin khác chuỗi nhánh R1 với '{hc_du}' (nguy cơ dị ứng chéo thấp ~1-2%).",
            "Thận trọng: khai thác tiền sử phản vệ nặng; nếu không có sốc phản vệ/SJS-TEN có thể cân nhắc dùng có giám sát hoặc thay bằng Aztreonam/Macrolide.",
        )

    # Class "cephalosporin"
    if hc_du == "cephalosporin" and hc_th in _CEPH_ALL:
        return (
            "Beta-lactam (Nhóm Cephalosporin)",
            CHONG_CHI_DINH,
            f"Người bệnh dị ứng nhóm Cephalosporin, chống chỉ định với '{hc_th}'.",
            "Tránh dùng Cephalosporin; cân nhắc Aztreonam (trừ Ceftazidime), Macrolide hoặc Fluoroquinolone.",
        )

    # Ceftazidime <-> Aztreonam (chia sẻ chuỗi nhánh R1 giống hệt nhau)
    if {hc_du, hc_th} == {"ceftazidime", "aztreonam"}:
        return (
            "Beta-lactam (Chuỗi nhánh R1 Ceftazidime - Aztreonam)",
            CHONG_CHI_DINH,
            "Ceftazidime và Aztreonam chia sẻ chuỗi nhánh R1 giống hệt nhau nên có nguy cơ dị ứng chéo cao.",
            "Không thay thế giữa Ceftazidime và Aztreonam; chọn Carbapenem (thận trọng) hoặc kháng sinh khác nhóm.",
        )

    # Penicillin <-> Aztreonam: an toàn miễn dịch (không cảnh báo chéo)
    if (hc_du in _PENICILLINS and hc_th == "aztreonam") or (hc_du == "aztreonam" and hc_th in _PENICILLINS):
        return None

    # Cephalosporin <-> Cephalosporin
    if hc_du in _CEPH_ALL and hc_th in _CEPH_ALL:
        chung_r1 = any(hc_du in cum and hc_th in cum for cum in _CEPH_R1_CLUSTERS)
        if chung_r1:
            return (
                "Beta-lactam (Cephalosporin cùng chuỗi nhánh R1)",
                CHONG_CHI_DINH,
                f"'{hc_du}' và '{hc_th}' dùng chung chuỗi nhánh R1 đặc hiệu, nguy cơ dị ứng chéo cao.",
                "Chọn Cephalosporin có chuỗi nhánh R1 hoàn toàn khác hoặc chuyển sang nhóm kháng sinh khác.",
            )
        return (
            "Beta-lactam (Cephalosporin khác chuỗi nhánh R1)",
            THAN_TRONG,
            f"'{hc_du}' và '{hc_th}' cùng nhóm Cephalosporin nhưng khác chuỗi nhánh R1.",
            "Theo dõi phản ứng quá mẫn khi sử dụng; tránh nếu tiền sử SJS/TEN hoặc sốc phản vệ nặng.",
        )

    # Penicillin / Cephalosporin <-> Carbapenem
    if ((hc_du in _PENICILLINS or hc_du in _CEPH_ALL) and hc_th in _CARBAPENEMS) or (
        hc_du in _CARBAPENEMS and (hc_th in _PENICILLINS or hc_th in _CEPH_ALL)
    ):
        return (
            "Beta-lactam (Nguy cơ chéo thấp với Carbapenem)",
            THAN_TRONG,
            f"Nguy cơ dị ứng chéo giữa '{hc_du}' và '{hc_th}' thấp (~1%), cần theo dõi khi dùng.",
            "Theo dõi sát sinh hiệu trong 30-60 phút đầu sau tiêm hoặc dùng liều thử có giám sát.",
        )

    if hc_du in _CARBAPENEMS and hc_th in _CARBAPENEMS:
        return (
            "Beta-lactam (Nhóm Carbapenem)",
            THAN_TRONG,
            f"Cùng cấu trúc nhân Carbapenem giữa '{hc_du}' và '{hc_th}'.",
            "Thận trọng tối đa; cân nhắc Aztreonam hoặc kháng sinh ngoài nhóm Beta-lactam.",
        )

    # 4. Sulfonamides
    if hc_du in _SULFA_ANTIBIOTIC and hc_th in _SULFA_ANTIBIOTIC:
        return (
            "Sulfonamide kháng khuẩn (Arylamine N4)",
            CHONG_CHI_DINH,
            f"'{hc_du}' và '{hc_th}' cùng mang nhóm arylamine N4 gây phản ứng chéo nặng (SJS/TEN, phát ban thuốc).",
            "Ngừng/tránh mọi kháng sinh Sulfonamide; chuyển sang kháng sinh nhóm khác (VD: Nitrofurantoin, Beta-lactam, Fluoroquinolone tùy chỉ định).",
        )

    if (hc_du in _SULFA_ANTIBIOTIC and hc_th in _SULFA_NON_ANTIBIOTIC) or (
        hc_du in _SULFA_NON_ANTIBIOTIC and hc_th in _SULFA_ANTIBIOTIC
    ):
        return (
            "Sulfonamide không kháng khuẩn (Chéo cấu trúc thấp)",
            THAN_TRONG,
            f"'{hc_th}' mang gốc sulfonamide không phải arylamine; nguy cơ chéo với '{hc_du}' thấp nhưng cần cảnh giác nếu từng SJS/TEN.",
            "Có thể cân nhắc nếu phản ứng trước đây nhẹ và theo dõi sát; tránh nếu tiền sử SJS/TEN/DRESS hoặc thay bằng nhóm không chứa gốc sulfa (Acid ethacrynic, Ibuprofen, Metformin).",
        )

    if hc_du in _SULFA_NON_ANTIBIOTIC and hc_th in _SULFA_NON_ANTIBIOTIC:
        return (
            "Sulfonamide không kháng khuẩn",
            THAN_TRONG,
            f"Cùng mang nhóm sulfonamide giữa '{hc_du}' và '{hc_th}' (nguy cơ chéo thấp).",
            "Theo dõi dấu hiệu mẫn cảm da niêm hoặc chọn thuốc thay thế ngoài nhóm sulfonamide.",
        )

    # 5. NSAIDs (COX-1 cross-sensitivity vs selective COX-2)
    if hc_du in _NSAID_COX1 and hc_th in _NSAID_COX1:
        return (
            "NSAID (Ức chế COX-1 không chọn lọc)",
            CHONG_CHI_DINH,
            f"Phản ứng chéo qua cơ chế ức chế COX-1 và tăng leukotriene giữa '{hc_du}' và '{hc_th}' (co thắt phế quản, phù mạch, mày đay).",
            "Chống chỉ định mọi NSAID ức chế COX-1; thay bằng Paracetamol (liều phù hợp) hoặc cân nhắc thuốc ức chế chọn lọc COX-2 (Celecoxib/Etoricoxib) có theo dõi.",
        )

    if (hc_du in _NSAID_COX1 and hc_th in _NSAID_COX2_SELECTIVE) or (
        hc_du in _NSAID_COX2_SELECTIVE and hc_th in _NSAID_COX1
    ):
        return (
            "NSAID (Chọn lọc COX-2 trên nền dị ứng COX-1)",
            THAN_TRONG,
            f"Thuốc ức chế chọn lọc COX-2 ('{hc_th}') ít gây phản ứng chéo với '{hc_du}' hơn NSAID cổ điển nhưng vẫn có nguy cơ phản ứng ở bệnh nhân mẫn cảm nặng.",
            "Thận trọng, theo dõi sát sau liều đầu hoặc ưu tiên Paracetamol nếu kiểm soát được đau/sốt.",
        )

    if hc_du in _NSAID_COX2_SELECTIVE and hc_th in _NSAID_COX2_SELECTIVE:
        return (
            "NSAID (Nhóm ức chế chọn lọc COX-2)",
            THAN_TRONG,
            f"Cùng nhóm Coxib giữa '{hc_du}' và '{hc_th}'.",
            "Thận trọng hoặc chuyển sang Paracetamol / giảm đau không thuộc nhóm NSAID.",
        )

    # 6. Macrolides
    if hc_du in _MACROLIDES and hc_th in _MACROLIDES:
        return (
            "Kháng sinh Macrolide",
            THAN_TRONG,
            f"Cùng vòng lactone nhóm Macrolide giữa '{hc_du}' và '{hc_th}', có nguy cơ dị ứng chéo nội nhóm.",
            "Theo dõi sát phản ứng quá mẫn hoặc thay bằng nhóm khác (Beta-lactam, Doxycycline) nếu phù hợp lâm sàng.",
        )

    # 7. Fluoroquinolones
    if hc_du in _FLUOROQUINOLONES and hc_th in _FLUOROQUINOLONES:
        return (
            "Kháng sinh Fluoroquinolone",
            THAN_TRONG,
            f"Dị ứng chéo nội nhóm Fluoroquinolone giữa '{hc_du}' và '{hc_th}' (~5-10% qua trung gian IgE hoặc MRGPRX2).",
            "Thận trọng cao độ hoặc chuyển sang kháng sinh ngoài nhóm Fluoroquinolone nếu không bắt buộc.",
        )

    # 8. ACEi angioedema class effect
    if hc_du in _ACEI and hc_th in _ACEI:
        return (
            "Ức chế men chuyển (ACEi - Nguy cơ phù mạch tái phát)",
            CHONG_CHI_DINH,
            f"Hiệu ứng nhóm ức chế tích lũy bradykinin giữa '{hc_du}' và '{hc_th}' gây phù mạch đường thở đe dọa tính mạng.",
            "Ngừng toàn bộ nhóm ACEi; cân nhắc đổi sang nhóm chẹn thụ thể Angiotensin II (ARB) hoặc chẹn kênh calci (Amlodipine) với theo dõi.",
        )

    if (hc_du in _ACEI and hc_th in _ARB) or (hc_du in _ARB and hc_th in _ACEI):
        return (
            "Hệ RAA (ACEi - ARB nguy cơ phù mạch chéo thấp)",
            THAN_TRONG,
            f"Có tỷ lệ nhỏ (~2-10%) tái phát phù mạch khi chuyển từ '{hc_du}' sang '{hc_th}'.",
            "Theo dõi sát dấu hiệu sưng môi/lưỡi/khó thở trong những tuần đầu hoặc chọn Amlodipine.",
        )

    return None


def kiem_tra_di_ung_cheo(danh_sach_di_ung: Any, danh_sach_thuoc: Any) -> List[Dict[str, Any]]:
    """Kiểm tra dị ứng chéo thuốc dựa trên danh sách dị ứng và danh sách thuốc đang dùng / được kê.

    Trả về danh sách dict có đúng 6 khóa:
    {thuoc, di_ung_goc, nhom_cheo, muc_do: "CHONG_CHI_DINH"|"THAN_TRONG", co_che, khuyen_cao_thay_the}.
    """
    ds_di_ung = _trich_danh_sach_chuoi(danh_sach_di_ung, la_di_ung=True)
    ds_thuoc = _trich_danh_sach_chuoi(danh_sach_thuoc, la_di_ung=False)
    if not ds_di_ung or not ds_thuoc:
        return []

    di_ung_phan_giai = [(du, _phan_giai_thanh_phan(du)) for du in ds_di_ung]
    thuoc_phan_giai = [(th, _phan_giai_thanh_phan(th)) for th in ds_thuoc]

    theo_cap: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for ten_thuoc, hcs_thuoc in thuoc_phan_giai:
        for ten_du, hcs_du in di_ung_phan_giai:
            tot_nhat: Optional[Dict[str, Any]] = None
            for hc_du in hcs_du:
                for hc_th in hcs_thuoc:
                    danh_gia = _danh_gia_cap(hc_du, hc_th)
                    if not danh_gia:
                        continue
                    nhom_cheo, muc_do, co_che, khuyen_cao = danh_gia
                    ung_vien = {
                        "thuoc": ten_thuoc,
                        "di_ung_goc": ten_du,
                        "nhom_cheo": nhom_cheo,
                        "muc_do": muc_do,
                        "co_che": co_che,
                        "khuyen_cao_thay_the": khuyen_cao,
                    }
                    if tot_nhat is None or _MUC_DO_UU_TIEN[muc_do] > _MUC_DO_UU_TIEN[tot_nhat["muc_do"]]:
                        tot_nhat = ung_vien
            if tot_nhat is not None:
                khoa = (ten_thuoc.lower(), ten_du.lower())
                if khoa not in theo_cap or _MUC_DO_UU_TIEN[tot_nhat["muc_do"]] > _MUC_DO_UU_TIEN[theo_cap[khoa]["muc_do"]]:
                    theo_cap[khoa] = tot_nhat

    return sorted(
        theo_cap.values(),
        key=lambda x: (-_MUC_DO_UU_TIEN[x["muc_do"]], x["thuoc"].lower(), x["di_ung_goc"].lower()),
    )
