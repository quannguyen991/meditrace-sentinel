# -*- coding: utf-8 -*-
"""Trụ cột 1: Tầng kiểm duyệt Dược lý Lâm sàng Nâng cao (Clinical Pharmacovigilance Engine).

Tích hợp:
1. Động cơ tra cứu tương tác thuốc nguy hiểm (Drug-Drug Interaction - DDI).
2. Kiểm soát liều trần tối đa hàng ngày (Maximum Daily Dose Guardrail).
3. Kiểm tra chống chỉ định kép theo cơ địa nhạy cảm (Patient Vulnerability Contraindication).
"""

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional, Set, Tuple

# Tích hợp Pure Python Aho-Corasick & Dược thư Quốc gia Việt Nam 2022 (zero MSVC dependency)
from src.aho_corasick_duoc_thu import (
    PurePythonAhoCorasick,
    BoTraCuuDuocThuAhoCorasick,
    ThongTinDuocThu,
    CO_SO_DU_LIEU_DUOC_THU_2022
)

# Mức độ nghiêm trọng của tương tác thuốc
DDI_CHONG_CHI_DINH = "chống chỉ định tuyệt đối"     # Nguy cơ tử vong / biến cố đe dọa tính mạng
DDI_NGHIEM_TRONG = "nguy cơ cao"                    # Xuất huyết, độc tính tim/thận nặng
DDI_CAN_THEO_DOI = "cần theo dõi sát"               # Thay đổi sinh khả dụng, cần chỉnh liều

@dataclass
class TuongTacThuoc:
    thuoc_1: str
    thuoc_2: str
    muc_do: str
    co_che: str
    hau_qua: str
    khuyen_cao: str


@dataclass
class KetQuaKiemDuyetDuocLy:
    hop_le: bool
    canh_bao_ddi: List[TuongTacThuoc] = field(default_factory=list)
    chong_chi_dinh_co_dia: List[str] = field(default_factory=list)
    vuot_lieu_tran: List[str] = field(default_factory=list)
    giai_trinh_duoc_ly: List[str] = field(default_factory=list)
    trung_nhom_atc: List[str] = field(default_factory=list)
    ganh_nang_da_thuoc: Dict[str, Any] = field(default_factory=dict)


# Nhóm ATC có nguy cơ trùng lặp điều trị (Therapeutic / ATC Duplication)
NHOM_ATC_TRUNG_LAP: Dict[str, Tuple[str, Tuple[str, ...]]] = {
    "NSAID (M01A)": (
        "Trùng nhóm thuốc kháng viêm không steroid (NSAID): tăng gấp bội nguy cơ xuất huyết tiêu hóa, loét dạ dày và suy thận cấp.",
        ("ibuprofen", "diclofenac", "meloxicam", "celecoxib", "naproxen", "piroxicam", "ketoprofen", "indomethacin", "etoricoxib"),
    ),
    "Statin (C10AA)": (
        "Trùng nhóm Statin hạ mỡ máu: không tăng hiệu quả bảo vệ tim mạch nhưng tăng mạnh nguy cơ tiêu cơ vân và độc tính gan.",
        ("atorvastatin", "rosuvastatin", "simvastatin", "pravastatin", "lovastatin", "fluvastatin", "pitavastatin"),
    ),
    "PPI (A02BC)": (
        "Trùng nhóm ức chế bơm proton (PPI): lãng phí thuốc và tăng nguy cơ hạ magie máu, loãng xương, nhiễm C. difficile.",
        ("omeprazol", "esomeprazol", "pantoprazol", "lansoprazol", "rabeprazol"),
    ),
    "ACEi/ARB (C09A/C09C)": (
        "Phối hợp kép ức chế hệ RAA (ACEi + ARB hoặc trùng nhóm): chống chỉ định theo ESC/KDIGO vì tăng nguy cơ tụt huyết áp, suy thận cấp và tăng kali máu.",
        ("enalapril", "captopril", "lisinopril", "perindopril", "ramipril", "losartan", "valsartan", "telmisartan", "irbesartan", "candesartan", "olmesartan"),
    ),
}

THUOC_TANG_KALI: Tuple[str, ...] = (
    "spironolacton", "amilorid", "triamteren",
    "enalapril", "captopril", "lisinopril", "perindopril", "ramipril",
    "losartan", "valsartan", "telmisartan", "irbesartan", "candesartan",
    "trimethoprim", "ibuprofen", "diclofenac", "meloxicam",
)

THUOC_KEO_DAI_QT: Tuple[str, ...] = (
    "amiodaron", "clarithromycin", "azithromycin", "erythromycin",
    "ciprofloxacin", "levofloxacin", "moxifloxacin",
    "haloperidol", "ondansetron", "domperidon", "fluconazol", "sotalol",
)


# Cơ sở dữ liệu tương tác thuốc lâm sàng thường gặp tại Việt Nam (DDI Knowledge Base)
BANG_TUONG_TAC_THUOC: List[TuongTacThuoc] = [
    TuongTacThuoc(
        thuoc_1="warfarin", thuoc_2="aspirin",
        muc_do=DDI_CHONG_CHI_DINH,
        co_che="Hiệp đồng ức chế đông máu và kết tập tiểu cầu, tổn thương niêm mạc dạ dày",
        hau_qua="Nguy cơ xuất huyết tiêu hóa ồ ạt và đột quỵ xuất huyết não",
        khuyen_cao="Tránh phối hợp trừ khi có chỉ định van tim cơ học đặc biệt và theo dõi sát INR"
    ),
    TuongTacThuoc(
        thuoc_1="warfarin", thuoc_2="ibuprofen",
        muc_do=DDI_CHONG_CHI_DINH,
        co_che="NSAID ức chế COX-1 làm loét niêm mạc đường tiêu hóa và đẩy warfarin khỏi liên kết protein",
        hau_qua="Nguy cơ chảy máu nội tạng nghiêm trọng",
        khuyen_cao="Chống chỉ định phối hợp. Thay bằng Paracetamol để giảm đau hạ sốt"
    ),
    TuongTacThuoc(
        thuoc_1="clopidogrel", thuoc_2="omeprazole",
        muc_do=DDI_NGHIEM_TRONG,
        co_che="Omeprazole ức chế mạnh CYP2C19, ngăn chuyển hóa clopidogrel thành dạng có hoạt tính",
        hau_qua="Giảm hiệu lực chống kết tập tiểu cầu, tăng nguy cơ tái phát nhồi máu cơ tim/huyết khối stent",
        khuyen_cao="Thay thế Omeprazole bằng Pantoprazole (ít ức chế CYP2C19 hơn) hoặc thuốc kháng H2"
    ),
    TuongTacThuoc(
        thuoc_1="enalapril", thuoc_2="spironolactone",
        muc_do=DDI_NGHIEM_TRONG,
        co_che="Cùng ức chế trục renin-angiotensin-aldosterone và giữ kali tại ống thận",
        hau_qua="Tăng kali máu ác tính gây rối loạn nhịp tim ngừng tim",
        khuyen_cao="Theo dõi điện giải đồ và chức năng thận định kỳ mỗi 1-2 tuần"
    ),
    TuongTacThuoc(
        thuoc_1="captopril", thuoc_2="spironolactone",
        muc_do=DDI_NGHIEM_TRONG,
        co_che="Phối hợp ức chế men chuyển và lợi tiểu giữ kali",
        hau_qua="Nguy cơ tăng kali máu nghiêm trọng",
        khuyen_cao="Kiểm tra kali máu trước và trong quá trình điều trị"
    ),
    TuongTacThuoc(
        thuoc_1="metformin", thuoc_2="thuoc_can_quang",
        muc_do=DDI_CHONG_CHI_DINH,
        co_che="Thuốc cản quang gây suy giảm chức năng thận cấp, làm tích lũy metformin",
        hau_qua="Nhiễm toan lactic đe dọa tính mạng (tỷ lệ tử vong lên tới 50%)",
        khuyen_cao="Tạm ngừng Metformin ít nhất 48 giờ trước và sau khi chụp cản quang có tiêm tĩnh mạch"
    ),
    TuongTacThuoc(
        thuoc_1="clarithromycin", thuoc_2="atorvastatin",
        muc_do=DDI_NGHIEM_TRONG,
        co_che="Clarithromycin ức chế mạnh men gan CYP3A4 làm tăng nồng độ Statin trong máu lên 4-10 lần",
        hau_qua="Tiêu cơ vân cấp tính, myoglobin niệu gây suy thận cấp",
        khuyen_cao="Tạm dừng Atorvastatin trong thời gian dùng kháng sinh Clarithromycin"
    ),
    TuongTacThuoc(
        thuoc_1="digoxin", thuoc_2="amiodarone",
        muc_do=DDI_NGHIEM_TRONG,
        co_che="Amiodarone ức chế P-glycoprotein làm tăng gấp đôi nồng độ Digoxin trong huyết thanh",
        hau_qua="Ngộ độc Digoxin: loạn nhịp thất, block nhĩ thất, nhìn mờ",
        khuyen_cao="Giảm 50% liều Digoxin khi bắt đầu phối hợp Amiodarone và đo nồng độ Digoxin máu"
    ),
    TuongTacThuoc(
        thuoc_1="ciprofloxacin", thuoc_2="theophylline",
        muc_do=DDI_NGHIEM_TRONG,
        co_che="Ciprofloxacin ức chế CYP1A2 làm giảm độ thanh thải của Theophylline",
        hau_qua="Ngộ độc Theophylline: co giật, loạn nhịp nhanh nguy hiểm",
        khuyen_cao="Tránh dùng chung hoặc giảm 1/2 liều Theophylline và theo dõi nồng độ thuốc"
    ),
    TuongTacThuoc(
        thuoc_1="allopurinol", thuoc_2="azathioprine",
        muc_do=DDI_CHONG_CHI_DINH,
        co_che="Allopurinol ức chế xanthine oxidase, làm ngưng trệ thoái giáng 6-mercaptopurine/azathioprine",
        hau_qua="Độc tính ức chế tủy xương nghiêm trọng: mất bạch cầu hạt, giảm tiểu cầu tử vong",
        khuyen_cao="CHỐNG CHỈ ĐỊNH PHỐI HỢP. Nếu bắt buộc, phải giảm liều Azathioprine xuống còn 1/4 - 1/3 liều thông thường và theo dõi huyết đồ hàng tuần"
    ),
    TuongTacThuoc(
        thuoc_1="colchicine", thuoc_2="clarithromycin",
        muc_do=DDI_CHONG_CHI_DINH,
        co_che="Clarithromycin ức chế mạnh mẽ cả CYP3A4 và P-glycoprotein, làm tăng vọt nồng độ Colchicine huyết tương",
        hau_qua="Ngộ độc Colchicine cấp tính: suy đa tạng, ức chế tủy, tiêu cơ vân và tử vong",
        khuyen_cao="CHỐNG CHỈ ĐỊNH PHỐI HỢP ở bệnh nhân suy thận hoặc suy gan. Tránh dùng chung ở mọi đối tượng"
    ),
    TuongTacThuoc(
        thuoc_1="methotrexate", thuoc_2="ibuprofen",
        muc_do=DDI_CHONG_CHI_DINH,
        co_che="NSAID làm giảm độ lọc cầu thận và cạnh tranh bài tiết chủ động tại ống thận của Methotrexate",
        hau_qua="Tăng nồng độ Methotrexate huyết thanh tự do gây suy tủy cấp, viêm loét đường tiêu hóa nặng",
        khuyen_cao="Tránh phối hợp NSAID với Methotrexate liều cao; với liều thấp bệnh khớp cần theo dõi sát chức năng thận và công thức máu"
    ),
    TuongTacThuoc(
        thuoc_1="methotrexate", thuoc_2="aspirin",
        muc_do=DDI_CHONG_CHI_DINH,
        co_che="Aspirin đẩy Methotrexate ra khỏi protein huyết tương và giảm thanh thải thận",
        hau_qua="Độc tính tủy xương và gan nghiêm trọng",
        khuyen_cao="Không tự ý dùng kèm Aspirin khi đang điều trị Methotrexate"
    ),
    TuongTacThuoc(
        thuoc_1="valproat", thuoc_2="carbamazepine",
        muc_do=DDI_NGHIEM_TRONG,
        co_che="Carbamazepine cảm ứng CYP làm tăng chuyển hóa valproat thành chất độc gan; Valproat ức chế epoxide hydrolase làm tăng chất chuyển hóa độc của carbamazepine",
        hau_qua="Nguy cơ ngộ độc thần kinh (chóng mặt, nhìn đôi) và tổn thương tế bào gan",
        khuyen_cao="Theo dõi nồng độ thuốc trong máu và điều chỉnh liều từng thuốc thận trọng"
    ),
    TuongTacThuoc(
        thuoc_1="rifampicin", thuoc_2="warfarin",
        muc_do=DDI_NGHIEM_TRONG,
        co_che="Rifampicin là chất cảm ứng enzym CYP2C9 và CYP3A4 cực mạnh làm tăng thanh thải Warfarin",
        hau_qua="Giảm mạnh hiệu lực kháng đông của Warfarin, nguy cơ hình thành huyết khối tái phát",
        khuyen_cao="Theo dõi chỉ số INR sát sao và thường phải tăng liều Warfarin lên gấp 2-3 lần khi dùng chung Rifampicin"
    ),
    TuongTacThuoc(
        thuoc_1="acenocoumarol", thuoc_2="aspirin",
        muc_do=DDI_CHONG_CHI_DINH,
        co_che="Hiệp đồng ức chế đông máu (kháng Vitamin K) và kết tập tiểu cầu, tổn thương niêm mạc dạ dày",
        hau_qua="Nguy cơ xuất huyết tiêu hóa ồ ạt và xuất huyết nội sọ nghiêm trọng",
        khuyen_cao="Tránh phối hợp Sintrom (Acenocoumarol) với Aspirin trừ chỉ định van tim cơ học đặc biệt có theo dõi sát INR"
    ),
    TuongTacThuoc(
        thuoc_1="acenocoumarol", thuoc_2="ibuprofen",
        muc_do=DDI_CHONG_CHI_DINH,
        co_che="NSAID ức chế COX-1 làm loét niêm mạc tiêu hóa và tăng nguy cơ chảy máu trên nền kháng Vitamin K",
        hau_qua="Nguy cơ chảy máu nội tạng nghiêm trọng",
        khuyen_cao="Chống chỉ định phối hợp Sintrom (Acenocoumarol) với NSAID. Thay bằng Paracetamol để giảm đau hạ sốt"
    ),
    TuongTacThuoc(
        thuoc_1="acenocoumarol", thuoc_2="amiodarone",
        muc_do=DDI_NGHIEM_TRONG,
        co_che="Amiodarone ức chế mạnh CYP2C9 làm giảm chuyển hóa Acenocoumarol",
        hau_qua="Tăng vọt chỉ số INR và nguy cơ xuất huyết nặng",
        khuyen_cao="Giảm 30-50% liều Acenocoumarol (Sintrom) và kiểm tra INR chặt chẽ khi phối hợp Amiodarone (Cordarone)"
    ),
    TuongTacThuoc(
        thuoc_1="warfarin", thuoc_2="amiodarone",
        muc_do=DDI_NGHIEM_TRONG,
        co_che="Amiodarone ức chế mạnh CYP2C9 làm tăng nồng độ Warfarin huyết tương",
        hau_qua="Tăng vọt chỉ số INR và nguy cơ xuất huyết nặng",
        khuyen_cao="Giảm 30-50% liều Warfarin (Coumadin) và theo dõi INR sát sao khi dùng kèm Amiodarone (Cordarone)"
    ),
    TuongTacThuoc(
        thuoc_1="rifampicin", thuoc_2="acenocoumarol",
        muc_do=DDI_NGHIEM_TRONG,
        co_che="Rifampicin cảm ứng mạnh CYP2C9 làm tăng chuyển hóa Acenocoumarol",
        hau_qua="Giảm hiệu lực chống đông của Sintrom (Acenocoumarol), nguy cơ huyết khối tắc mạch",
        khuyen_cao="Theo dõi sát INR và hiệu chỉnh liều Acenocoumarol khi bắt đầu hoặc ngừng Rifampicin"
    ),
]

# Liều tối đa hàng ngày (Maximum Daily Dose) cho người lớn
# 25/11/2026: doc tu MOT nguon (data/tri_thuc_thuoc.json, chua duyet).
from src import tri_thuc_thuoc as _ttt
LIEU_TOI_DA_NGAY: Dict[str, Tuple[float, str]] = {t: (v, "mg") for t, v in _ttt.bang_lieu_nguoi_lon().items()}


_BIET_DUOC_PHO_BIEN: Dict[str, str] = {
    "losec": "omeprazole",
    "omepral": "omeprazole",
    "lomac": "omeprazole",
    "nexium": "esomeprazole",
    "plavix": "clopidogrel",
    "clopistad": "clopidogrel",
    "sintrom": "acenocoumarol",
    "minisintrom": "acenocoumarol",
    "coumadin": "warfarin",
    "marevan": "warfarin",
    "cordarone": "amiodarone",
    "glucophage": "metformin",
    "panfor": "metformin",
    "crestor": "rosuvastatin",
    "lipitor": "atorvastatin",
    "cozaar": "losartan",
    "aldactone": "spironolactone",
    "verospiron": "spironolactone",
    "norvasc": "amlodipin",
    "amlor": "amlodipin",
    "panadol": "paracetamol",
    "hapacol": "paracetamol",
    "efferalgan": "paracetamol",
    "advil": "ibuprofen",
    "brufen": "ibuprofen",
    "renitec": "enalapril",
    "lanoxin": "digoxin",
    "zyloric": "allopurinol",
    "ciprobay": "ciprofloxacin",
    "theostat": "theophylline",
    "imuran": "azathioprine",
    "tegretol": "carbamazepine",
    "depakine": "valproat",
}


def _goc_khong_e(ten: str) -> str:
    """Chuẩn hóa gốc tên hoạt chất không phân biệt chữ 'e' cuối (omeprazol == omeprazole, spironolacton == spironolactone)."""
    s = (ten or "").strip().lower()
    return s[:-1] if len(s) > 5 and s.endswith("e") else s


def _trich_danh_sach_benh_nen(co_dia: Optional[Dict[str, Any]]) -> List[str]:
    """Hỗ trợ đồng thời cả khóa `benh_nen` lẫn `tien_su_benh` (dạng list hoặc chuỗi)."""
    if not isinstance(co_dia, dict):
        return []
    ket_qua: List[str] = []
    for khoa in ("tien_su_benh", "benh_nen"):
        raw = co_dia.get(khoa)
        if not raw:
            continue
        if isinstance(raw, str):
            ket_qua.extend([x.strip().lower() for x in re.split(r"[,;\n]+", raw) if x.strip()])
        elif isinstance(raw, (list, tuple, set)):
            ket_qua.extend([str(x).strip().lower() for x in raw if x is not None and str(x).strip()])
    return ket_qua


class ClinicalPharmacovigilanceEngine:
    """Động cơ Dược lý Lâm sàng kiểm soát an toàn dùng thuốc toàn diện."""

    _bo_tra_cuu_aho: Optional[BoTraCuuDuocThuAhoCorasick] = None

    @classmethod
    def lay_bo_tra_cuu_aho(cls) -> BoTraCuuDuocThuAhoCorasick:
        """Khởi tạo và lấy singleton máy tra cứu Aho-Corasick Dược thư Quốc gia Việt Nam 2022."""
        if cls._bo_tra_cuu_aho is None:
            cls._bo_tra_cuu_aho = BoTraCuuDuocThuAhoCorasick()
        return cls._bo_tra_cuu_aho

    @classmethod
    def nhan_dien_thuoc_aho_corasick(cls, van_ban: str) -> List[Dict[str, Any]]:
        """Nhận diện thực thể dược học (hoạt chất/biệt dược) trong văn bản bằng Aho-Corasick thuần Python."""
        return cls.lay_bo_tra_cuu_aho().nhan_dien_thuoc_trong_van_ban(van_ban)

    @staticmethod
    def chuan_hoa_ten_thuoc(ten: str) -> str:
        t = (ten or "").strip().lower()
        t = re.sub(r"\b(thuốc|viên|gói|uống|tiêm)\b", "", t).strip()
        return re.sub(r"\s+", " ", t)

    @classmethod
    def phan_giai_hoat_chat(cls, chuoi_thuoc: str) -> List[str]:
        """Phân giải chuỗi tên thuốc / biệt dược / hàm lượng thành danh sách hoạt chất chuẩn."""
        norm = cls.chuan_hoa_ten_thuoc(chuoi_thuoc)
        if not norm:
            return []
        ket_qua: List[str] = []
        da_co: Set[str] = set()

        def _them(hc_raw: Optional[str]) -> None:
            if not hc_raw:
                return
            g = _goc_khong_e(hc_raw)
            if g and g not in da_co:
                da_co.add(g)
                ket_qua.append(hc_raw.strip().lower())

        if "thuoc_can_quang" in norm or "cản quang" in norm:
            _them("thuoc_can_quang")

        for bd, hc_bd in _BIET_DUOC_PHO_BIEN.items():
            if re.search(rf"(?<!\w){re.escape(bd)}(?!\w)", norm):
                _them(hc_bd)

        hc_direct = _ttt.hoat_chat(norm)
        if hc_direct:
            _them(hc_direct)

        for m_rx in _ttt.regex_ten_thuoc().finditer(norm):
            _them(_ttt.hoat_chat(m_rx.group(1)) or m_rx.group(1))

        for m_aho in cls.nhan_dien_thuoc_aho_corasick(norm):
            _them(m_aho["hoat_chat"])

        if not ket_qua:
            for tok in re.findall(r"[a-zA-ZÀ-ỹ][\w\-]{3,}", norm):
                tok_l = tok.lower()
                if not re.match(r"^\d", tok_l) and tok_l not in {"ngay", "ngày", "sáng", "trưa", "chiều", "tối", "tuần"}:
                    _them(tok_l)
        return ket_qua

    @classmethod
    def kiem_tra_tuong_tac(cls, danh_sach_thuoc: List[str]) -> List[TuongTacThuoc]:
        """Phát hiện tương tác thuốc đa hoạt chất (DDI), hỗ trợ biệt dược & biến thể chữ 'e' cuối."""
        ra: List[TuongTacThuoc] = []
        tap_goc_moi_muc: List[Set[str]] = []
        for raw in danh_sach_thuoc or []:
            if not raw or not str(raw).strip():
                continue
            hcs = cls.phan_giai_hoat_chat(str(raw))
            gocs = {_goc_khong_e(h) for h in hcs}
            norm = cls.chuan_hoa_ten_thuoc(str(raw))
            for tok in re.findall(r"[a-z0-9_]+", norm):
                gocs.add(_goc_khong_e(tok))
            tap_goc_moi_muc.append(gocs)

        # Gộp cả trường hợp nhiều thuốc nằm trong cùng 1 chuỗi hoặc giữa các phần tử khác nhau
        tat_ca_goc: Set[str] = set().union(*tap_goc_moi_muc) if tap_goc_moi_muc else set()
        for tt in BANG_TUONG_TAC_THUOC:
            g1 = _goc_khong_e(tt.thuoc_1)
            g2 = _goc_khong_e(tt.thuoc_2)
            if g1 in tat_ca_goc and g2 in tat_ca_goc and g1 != g2:
                if tt not in ra:
                    ra.append(tt)
        return ra

    @classmethod
    def kiem_tra_co_dia_chong_chi_dinh(cls, danh_sach_thuoc: List[str], co_dia: Optional[Dict[str, Any]]) -> List[str]:
        """Kiểm tra chống chỉ định tuyệt đối theo cơ địa lâm sàng (hỗ trợ cả `benh_nen` & `tien_su_benh`)."""
        if not co_dia:
            return []

        canh_bao: List[str] = []
        muc_thuoc: List[Tuple[str, Set[str]]] = []
        for raw in danh_sach_thuoc or []:
            if not raw or not str(raw).strip():
                continue
            t_norm = cls.chuan_hoa_ten_thuoc(str(raw))
            gocs = {_goc_khong_e(h) for h in cls.phan_giai_hoat_chat(str(raw))}
            for tok in re.findall(r"[a-z0-9_]+", t_norm):
                gocs.add(_goc_khong_e(tok))
            muc_thuoc.append((t_norm, gocs))

        def _khop_nhom(gocs: Set[str], t_norm: str, danh_sach_ten: Tuple[str, ...]) -> Optional[str]:
            for x in danh_sach_ten:
                gx = _goc_khong_e(x)
                if gx in gocs or x in t_norm:
                    return x
            return None

        def _nhan_thuoc(t_norm: str, hc_khop: str) -> str:
            return t_norm if hc_khop in t_norm else f"{t_norm} ({hc_khop})"

        # 1. Suy thận nặng (eGFR < 30 ml/phút hoặc CKD stage 4-5)
        egfr = co_dia.get("egfr")
        if egfr is None and isinstance(co_dia.get("xet_nghiem"), dict):
            egfr = co_dia["xet_nghiem"].get("egfr")
        ckd = co_dia.get("ckd_stage")
        suy_than_nang = (egfr is not None and float(egfr) < 30) or ckd in (4, 5, "4", "5")

        if suy_than_nang:
            for t_norm, gocs in muc_thuoc:
                m_nsaid = _khop_nhom(gocs, t_norm, ("ibuprofen", "meloxicam", "diclofenac", "celecoxib", "naproxen", "piroxicam", "etoricoxib", "nsaid"))
                if m_nsaid:
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH: Thuốc NSAID '{_nhan_thuoc(t_norm, m_nsaid)}' bị cấm khi suy thận nặng (eGFR < 30) do nguy cơ suy thận cấp vô niệu")
                m_met = _khop_nhom(gocs, t_norm, ("metformin",))
                if m_met:
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH: Thuốc hạ đường huyết '{_nhan_thuoc(t_norm, m_met)}' bị cấm khi eGFR < 30 do nguy cơ nhiễm toan lactic tử vong")
                m_spi = _khop_nhom(gocs, t_norm, ("spironolactone",))
                if m_spi:
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH: Lợi tiểu kháng Aldosterone '{_nhan_thuoc(t_norm, m_spi)}' chống chỉ định khi eGFR < 30 do nguy cơ tăng kali máu ngừng tim")
                m_neph = _khop_nhom(gocs, t_norm, ("gentamicin", "vancomycin"))
                if m_neph:
                    canh_bao.append(f"CẢNH BÁO CAO: Kháng sinh độc thận '{_nhan_thuoc(t_norm, m_neph)}' cần giảm liều triệt để và định lượng nồng độ đáy")

        # 2. Phụ nữ mang thai (Thai kỳ Category X/D)
        mang_thai = co_dia.get("mang_thai") or co_dia.get("thai_ky")
        if mang_thai:
            for t_norm, gocs in muc_thuoc:
                m_raa = _khop_nhom(gocs, t_norm, ("captopril", "enalapril", "lisinopril", "perindopril", "ramipril", "losartan", "valsartan", "telmisartan", "irbesartan", "candesartan"))
                if m_raa:
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI: Nhóm hạ áp '{_nhan_thuoc(t_norm, m_raa)}' (ACEi/ARB) gây quái thai, suy thận và vô sọ ở thai nhi (Category D)")
                m_statin = _khop_nhom(gocs, t_norm, ("atorvastatin", "rosuvastatin", "simvastatin", "pravastatin", "lovastatin"))
                if m_statin:
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI: Statin '{_nhan_thuoc(t_norm, m_statin)}' chống chỉ định trong thai kỳ do nguy cơ dị tật xương (Category X)")
                m_vka = _khop_nhom(gocs, t_norm, ("warfarin", "acenocoumarol"))
                if m_vka:
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI: Thuốc chống đông kháng Vitamin K '{_nhan_thuoc(t_norm, m_vka)}' gây dị tật bào thai và xuất huyết thai (Category X)")
                m_mtx = _khop_nhom(gocs, t_norm, ("methotrexate",))
                if m_mtx:
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI: '{_nhan_thuoc(t_norm, m_mtx)}' là thuốc độc tế bào gây sảy thai và dị tật nặng")

        # 3. Tiền sử bệnh nền đặc thù (đọc cả `tien_su_benh` và `benh_nen`)
        benh_nen = _trich_danh_sach_benh_nen(co_dia)
        if any("hen" in b for b in benh_nen):
            for t_norm, gocs in muc_thuoc:
                m_bb = _khop_nhom(gocs, t_norm, ("propranolol", "timolol", "carvedilol", "nadolol", "sotalol"))
                if m_bb:
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH: Thuốc chẹn beta '{_nhan_thuoc(t_norm, m_bb)}' gây co thắt phế quản cấp nguy hiểm ở bệnh nhân hen suyễn")
                m_widal = _khop_nhom(gocs, t_norm, ("aspirin", "ibuprofen", "diclofenac", "meloxicam", "naproxen"))
                if m_widal:
                    canh_bao.append("CẢNH BÁO: Bệnh nhân hen phế quản có nguy cơ co thắt phế quản nặng do NSAID/Aspirin (Hội chứng Widal)")

        if any("loét dạ dày" in b or "loét tá tràng" in b or "xuất huyết tiêu hóa" in b for b in benh_nen):
            for t_norm, gocs in muc_thuoc:
                m_ulcer = _khop_nhom(gocs, t_norm, ("aspirin", "ibuprofen", "diclofenac", "meloxicam", "naproxen", "prednisolone", "methylprednisolone"))
                if m_ulcer:
                    canh_bao.append(f"CẢNH BÁO CAO: Thuốc '{_nhan_thuoc(t_norm, m_ulcer)}' gây kích ứng và tái phát loét/xuất huyết tiêu hóa nặng trên bệnh nhân có tiền sử bệnh dạ dày")

        return canh_bao

    @classmethod
    def kiem_tra_lieu_tran(cls, ten_thuoc: str, lieu_mg: float) -> Optional[str]:
        """Kiểm tra nếu liều thuốc vượt quá liều trần cho phép trong ngày."""
        norm = cls.chuan_hoa_ten_thuoc(ten_thuoc)
        hc = _ttt.hoat_chat(norm)
        if not hc:
            for bd, hc_bd in _BIET_DUOC_PHO_BIEN.items():
                if re.search(rf"(?<!\w){re.escape(bd)}(?!\w)", norm):
                    hc = hc_bd
                    break
        l = _ttt.lieu_toi_da(hc, "nguoi_lon") if hc else None
        if l is not None and lieu_mg > l.gia_tri:
            return (f"VƯỢT LIỀU TRẦN: Liều dùng {lieu_mg} mg vượt quá liều tối đa hàng ngày cho phép "
                    f"({l.gia_tri} mg) của '{hc}'" + ("" if l.da_duyet else " (ngưỡng chưa được duyệt)"))
        return None

    @classmethod
    def kiem_tra_da_thuoc_va_trung_nhom_atc(cls, danh_sach_thuoc: List[str]) -> Dict[str, Any]:
        """Phát hiện trùng nhóm ATC (NSAID, Statin, PPI, ACEi/ARB), đa thuốc (>= 5) và cộng dồn nguy cơ Kali/QT."""
        thuoc_chuan: List[str] = []
        seen_goc: Set[str] = set()
        for raw in danh_sach_thuoc or []:
            if not raw or not str(raw).strip():
                continue
            hcs = cls.phan_giai_hoat_chat(str(raw))
            for hc in hcs:
                g = _goc_khong_e(hc)
                if g and g not in seen_goc:
                    seen_goc.add(g)
                    thuoc_chuan.append(hc)

        trung_nhom: List[str] = []
        chi_tiet_atc: Dict[str, List[str]] = {}
        for ten_nhom, (mo_ta, ds_goc) in NHOM_ATC_TRUNG_LAP.items():
            tap_goc_atc = {_goc_khong_e(g) for g in ds_goc}
            khop = [t for t in thuoc_chuan if _goc_khong_e(t) in tap_goc_atc]
            if len(khop) >= 2:
                chi_tiet_atc[ten_nhom] = khop
                trung_nhom.append(
                    f"[TRÙNG NHÓM ATC - {ten_nhom}] Phát hiện {len(khop)} thuốc cùng nhóm ({', '.join(khop)}): {mo_ta}"
                )

        tap_goc_kali = {_goc_khong_e(k) for k in THUOC_TANG_KALI}
        tap_goc_qt = {_goc_khong_e(q) for q in THUOC_KEO_DAI_QT}
        kali_drugs = [t for t in thuoc_chuan if _goc_khong_e(t) in tap_goc_kali]
        qt_drugs = [t for t in thuoc_chuan if _goc_khong_e(t) in tap_goc_qt]
        cong_don_rui_ro: List[str] = []
        if len(kali_drugs) >= 2:
            cong_don_rui_ro.append(
                f"[CỘNG DỒN TĂNG KALI MÁU] Phối hợp {len(kali_drugs)} thuốc có nguy cơ giữ kali ({', '.join(kali_drugs)}): cần theo dõi điện giải đồ (K+) và chức năng thận."
            )
        if len(qt_drugs) >= 2:
            cong_don_rui_ro.append(
                f"[CỘNG DỒN KÉO DÀI KHOẢNG QT] Phối hợp {len(qt_drugs)} thuốc kéo dài QTc ({', '.join(qt_drugs)}): nguy cơ xoắn đỉnh (Torsades de pointes), cần đo ECG kiểm tra QTc."
            )

        polypharmacy = len(thuoc_chuan) >= 5
        if polypharmacy:
            cong_don_rui_ro.append(
                f"[ĐA THUỐC (POLYPHARMACY)] Bệnh nhân dùng đồng thời {len(thuoc_chuan)} hoạt chất (>= 5): cần rà soát lược bỏ thuốc không thiết yếu."
            )

        return {
            "so_thuoc_phan_biet": len(thuoc_chuan),
            "polypharmacy": polypharmacy,
            "trung_nhom_atc": chi_tiet_atc,
            "thuoc_tang_kali": kali_drugs,
            "thuoc_keo_dai_qt": qt_drugs,
            "canh_bao_atc_va_cong_don": trung_nhom + cong_don_rui_ro,
        }

    @classmethod
    def kiem_duyet_toan_dien(cls, danh_sach_thuoc: List[str], co_dia: Optional[Dict[str, Any]] = None,
                             chi_tiet_lieu: Optional[Dict[str, float]] = None) -> KetQuaKiemDuyetDuocLy:
        """Thực thi toàn bộ quy trình kiểm duyệt dược lý lâm sàng."""
        canh_bao_ddi = cls.kiem_tra_tuong_tac(danh_sach_thuoc)
        chong_chi_dinh = cls.kiem_tra_co_dia_chong_chi_dinh(danh_sach_thuoc, co_dia)
        vuot_lieu = []
        
        if chi_tiet_lieu:
            for t, l in chi_tiet_lieu.items():
                err = cls.kiem_tra_lieu_tran(t, l)
                if err:
                    vuot_lieu.append(err)

        ganh_nang = cls.kiem_tra_da_thuoc_va_trung_nhom_atc(danh_sach_thuoc)
        trung_nhom_atc = ganh_nang.get("canh_bao_atc_va_cong_don", [])

        giai_trinh = []
        for ddi in canh_bao_ddi:
            giai_trinh.append(f"[{ddi.muc_do.upper()}] Tương tác giữa {ddi.thuoc_1} và {ddi.thuoc_2}: {ddi.hau_qua}. Khuyến cáo: {ddi.khuyen_cao}")
        for cd in chong_chi_dinh:
            giai_trinh.append(f"[CHỐNG CHỈ ĐỊNH] {cd}")
        for can_bao_lieu in vuot_lieu:
            giai_trinh.append(f"[QUÁ LIỀU] {can_bao_lieu}")
        for cb_atc in trung_nhom_atc:
            giai_trinh.append(cb_atc)

        co_trung_hoac_cong_don_nguy_hiem = (
            bool(ganh_nang.get("trung_nhom_atc"))
            or len(ganh_nang.get("thuoc_tang_kali", [])) >= 2
            or len(ganh_nang.get("thuoc_keo_dai_qt", [])) >= 2
        )
        hop_le = (
            len(canh_bao_ddi) == 0
            and len(chong_chi_dinh) == 0
            and len(vuot_lieu) == 0
            and not co_trung_hoac_cong_don_nguy_hiem
        )

        return KetQuaKiemDuyetDuocLy(
            hop_le=hop_le,
            canh_bao_ddi=canh_bao_ddi,
            chong_chi_dinh_co_dia=chong_chi_dinh,
            vuot_lieu_tran=vuot_lieu,
            giai_trinh_duoc_ly=giai_trinh,
            trung_nhom_atc=trung_nhom_atc,
            ganh_nang_da_thuoc=ganh_nang,
        )
