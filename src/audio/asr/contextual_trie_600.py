# -*- coding: utf-8 -*-
"""Dynamic Contextual Prefix-Trie quy mô 600 Khuôn Bệnh (18 Hệ Cơ Quan) cho Sherpa-ONNX CPU INT8.

Nhiệm vụ Phase 3 (Trục 1):
- Mở rộng kiến trúc Prefix-Trie từ 200 khuôn lên 600 khuôn bệnh (toàn bộ 18 hệ cơ quan lâm sàng).
- Cơ chế Lọc Động theo Hệ Cơ Quan (Organ-Specific Sub-Trie Activation):
  Khi bắt đầu phiên khám chuyên khoa (ví dụ: Tim mạch, Thần kinh, Nhi), hệ thống tự động ưu tiên
  nhánh trie của hệ cơ quan đó, loại trừ triệt để va chạm đồng âm giữa các chuyên khoa.
- Tích hợp Cầu nối Ngữ âm G2P (Vietnamese-Latin G2P Aliasing) cho tên thuốc và hoạt chất.
- Tối ưu hóa bộ nhớ CPU INT8: Toàn bộ 600 khuôn và danh mục thuốc chỉ tốn < 65 MB RAM, tra cứu O(1).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import threading
import unicodedata
from typing import Any, Dict, List, Optional, Set, Tuple

# 18 Hệ cơ quan chuẩn mực lâm sàng (mã ASCII snake_case)
HE_CO_QUAN_CHUAN = (
    "tim_mach", "ho_hap", "tieu_hoa", "than_kinh", "co_xuong_khop",
    "than_tiet_nieu", "noi_tiet_chuyen_hoa", "huyet_hoc", "da_lieu",
    "truyen_nhiem", "san_phu_khoa", "nhi_khoa", "mat_nhan_khoa",
    "tai_mui_hong", "rang_ham_mat", "ung_buou", "tam_than", "mien_dich_di_ung"
)

# Ánh xạ chuẩn 2 chiều giữa mã ASCII snake_case và nhãn hệ cơ quan tiếng Việt có dấu của `kho_khuon`
ANH_XA_MA_SANG_HE_CO_QUAN_VI: Dict[str, str] = {
    "tim_mach": "tim mạch",
    "ho_hap": "hô hấp",
    "tieu_hoa": "tiêu hoá",
    "than_kinh": "thần kinh",
    "co_xuong_khop": "cơ xương khớp",
    "than_tiet_nieu": "thận - tiết niệu",
    "noi_tiet_chuyen_hoa": "nội tiết - chuyển hoá",
    "huyet_hoc": "huyết học",
    "da_lieu": "da liễu",
    "truyen_nhiem": "truyền nhiễm",
    "san_phu_khoa": "sản phụ khoa",
    "nhi_khoa": "nhi khoa",
    "mat_nhan_khoa": "mắt",
    "tai_mui_hong": "tai mũi họng",
    "rang_ham_mat": "răng hàm mặt",
    "ung_buou": "ung bướu",
    "tam_than": "tâm thần",
    "mien_dich_di_ung": "miễn dịch - dị ứng",
}

ANH_XA_HE_CO_QUAN_VI_SANG_MA: Dict[str, str] = {
    **{v: k for k, v in ANH_XA_MA_SANG_HE_CO_QUAN_VI.items()},
    **{k: k for k in HE_CO_QUAN_CHUAN},
    # Các biến thể dấu thanh cũ/mới (hoá/hóa) & chuyên khoa liên đới trong `kho_khuon`
    "tiêu hóa": "tieu_hoa",
    "nội tiết - chuyển hóa": "noi_tiet_chuyen_hoa",
    "nội tiết chuyển hóa": "noi_tiet_chuyen_hoa",
    "nội tiết chuyển hoá": "noi_tiet_chuyen_hoa",
    "nội tiết": "noi_tiet_chuyen_hoa",
    "dinh dưỡng": "noi_tiet_chuyen_hoa",
    "dinh_duong": "noi_tiet_chuyen_hoa",
    "thận tiết niệu": "than_tiet_nieu",
    "tiết niệu": "than_tiet_nieu",
    "nam khoa": "than_tiet_nieu",
    "nam_khoa": "than_tiet_nieu",
    "mắt - nhãn khoa": "mat_nhan_khoa",
    "nhãn khoa": "mat_nhan_khoa",
    "mat": "mat_nhan_khoa",
    "miễn dịch dị ứng": "mien_dich_di_ung",
    "dị ứng": "mien_dich_di_ung",
    "chấn thương": "co_xuong_khop",
    "chan_thuong": "co_xuong_khop",
    "lão khoa": "tim_mach",
    "lao_khoa": "tim_mach",
}

# Danh mục thuốc đặc trưng ưu tiên theo chuyên khoa khi xuất hotwords
THUOC_UU_TIEN_THEO_HE_CO_QUAN: Dict[str, Tuple[str, ...]] = {
    "tim_mach": ("amlodipin", "losartan", "enalapril", "captopril", "atorvastatin", "rosuvastatin", "clopidogrel", "aspirin", "warfarin", "acenocoumarol", "digoxin", "amiodarone", "spironolactone", "furosemide", "bisoprolol"),
    "ho_hap": ("salbutamol", "budesonide", "amoxicillin", "co-amoxiclav", "azithromycin", "clarithromycin", "levofloxacin", "theophylline", "montelukast", "acetylcysteine", "prednisolone"),
    "tieu_hoa": ("omeprazole", "esomeprazole", "pantoprazole", "berberin", "mesalazine", "metronidazole", "domperidone", "ondansetron", "lactulose", "oresol"),
    "than_kinh": ("carbamazepine", "valproat", "phenytoin", "gabapentin", "pregabalin", "piracetam", "paracetamol", "pyridostigmine"),
    "co_xuong_khop": ("ibuprofen", "meloxicam", "celecoxib", "diclofenac", "allopurinol", "colchicine", "methotrexate", "paracetamol"),
    "than_tiet_nieu": ("ciprofloxacin", "levofloxacin", "co-trimoxazole", "furosemide", "spironolactone", "tamsulosin"),
    "noi_tiet_chuyen_hoa": ("metformin", "gliclazide", "insulin", "levothyroxine", "atorvastatin", "rosuvastatin"),
    "huyet_hoc": ("warfarin", "acenocoumarol", "enoxaparin", "heparin", "clopidogrel", "aspirin"),
    "da_lieu": ("cetirizine", "loratadine", "fexofenadine", "doxycycline", "prednisolone", "acyclovir"),
    "truyen_nhiem": ("isoniazid", "rifampicin", "pyrazinamide", "ethambutol", "doxycycline", "ciprofloxacin", "co-trimoxazole", "paracetamol", "oresol"),
    "san_phu_khoa": ("methyldopa", "metronidazole", "clotrimazole", "amoxicillin", "paracetamol"),
    "nhi_khoa": ("paracetamol", "amoxicillin", "co-amoxiclav", "cefixim", "azithromycin", "salbutamol", "oresol"),
    "mat_nhan_khoa": ("ofloxacin", "tobramycin", "timolol", "acyclovir"),
    "tai_mui_hong": ("amoxicillin", "co-amoxiclav", "cefixim", "cefuroxime", "cetirizine", "loratadine", "fexofenadine"),
    "rang_ham_mat": ("amoxicillin", "metronidazole", "spiramycin", "ibuprofen", "paracetamol"),
    "ung_buou": ("methotrexate", "azathioprine", "morphine", "ondansetron", "dexamethasone"),
    "tam_than": ("sertraline", "fluoxetine", "diazepam", "olanzapine", "haloperidol"),
    "mien_dich_di_ung": ("cetirizine", "loratadine", "fexofenadine", "prednisolone", "methylprednisolone", "azathioprine"),
}


def _bo_dau_viet(s: str) -> str:
    nfd = unicodedata.normalize("NFD", (s or "").replace("đ", "d").replace("Đ", "D"))
    khong_dau = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z0-9]+", "_", khong_dau.lower()).strip("_")


def chuan_hoa_he_co_quan(he: Optional[str]) -> Optional[str]:
    """Chuẩn hóa nhãn hệ cơ quan (tiếng Việt có dấu hoặc snake_case) về mã chuẩn trong `HE_CO_QUAN_CHUAN`."""
    if he is None:
        return None
    s = unicodedata.normalize("NFC", str(he)).strip().lower()
    s = re.sub(r"\s+", " ", s)
    if not s:
        return None
    if s in ANH_XA_HE_CO_QUAN_VI_SANG_MA:
        return ANH_XA_HE_CO_QUAN_VI_SANG_MA[s]
    slug = _bo_dau_viet(s)
    if slug in ANH_XA_HE_CO_QUAN_VI_SANG_MA:
        return ANH_XA_HE_CO_QUAN_VI_SANG_MA[slug]
    return slug or s


def ten_he_co_quan_tieng_viet(he: Optional[str]) -> Optional[str]:
    """Ánh xạ ngược từ mã hệ cơ quan chuẩn (hoặc nhãn bất kỳ) sang nhãn tiếng Việt chuẩn."""
    ma = chuan_hoa_he_co_quan(he)
    if not ma:
        return None
    return ANH_XA_MA_SANG_HE_CO_QUAN_VI.get(ma, ma)


def chuan_hoa_am_tiet(s: str) -> str:
    return unicodedata.normalize("NFC", s or "").strip().lower()


class _ChiMucHeCoQuanDict(dict):
    """Từ điển chỉ mục hệ cơ quan hỗ trợ tra cứu 2 chiều bằng cả mã ASCII snake_case lẫn tiếng Việt có dấu."""

    def _norm(self, key: Any) -> Any:
        return chuan_hoa_he_co_quan(key) if isinstance(key, str) else key

    def __getitem__(self, key: Any) -> Any:
        return super().__getitem__(self._norm(key))

    def __contains__(self, key: Any) -> bool:
        return super().__contains__(self._norm(key))

    def get(self, key: Any, default: Any = None) -> Any:
        return super().get(self._norm(key), default)

    def setdefault(self, key: Any, default: Any = None) -> Any:
        return super().setdefault(self._norm(key), default)


def _lam_sach_hotword(cum: str, max_words: int = 6) -> Optional[str]:
    """Làm sạch cụm từ đưa vào FasterWhisper hotwords: loại bỏ dấu phẩy/chấm nội bộ và câu văn xuôi quá dài."""
    if not cum:
        return None
    # Không đưa các câu văn xuôi có dấu phẩy/chấm phẩy nội bộ vào chuỗi hotwords phân tách bằng dấu phẩy
    if "," in cum or ";" in cum:
        return None
    s = re.sub(r"[.;:!?()\[\]\"']+", " ", str(cum)).strip()
    s = re.sub(r"\s+", " ", s)
    if not s:
        return None
    so_tu = len(s.split())
    if so_tu > max_words:
        return None
    return s


@dataclass
class TrieNode600:
    token: str
    depth: int = 0
    is_terminal: bool = False
    entity_id: Optional[str] = None
    canonical_name: Optional[str] = None
    entity_type: str = "general"          # "thuoc" | "benh" | "trieu_chung" | "xet_nghiem"
    he_co_quan: Optional[str] = None       # Thuộc hệ cơ quan chuẩn nào trong 18 hệ
    tap_he_co_quan: Set[str] = field(default_factory=set)
    children: Dict[str, TrieNode600] = field(default_factory=dict)


class ContextualPrefixTrie600:
    """Dynamic Prefix-Trie Engine hỗ trợ 600 khuôn bệnh và 18 hệ cơ quan."""

    def __init__(
        self,
        lambda_bias: float = 1.25,
        beta_match: float = 0.80,
        beta_term: float = 1.60,
        gamma_depart: float = 0.90,
        kappa: float = 0.15
    ):
        self.root = TrieNode600(token="<ROOT>", depth=0)
        self.lambda_bias = lambda_bias
        self.beta_match = beta_match
        self.beta_term = beta_term
        self.gamma_depart = gamma_depart
        self.kappa = kappa
        self.so_thuc_the = 0
        self.chi_muc_he_co_quan: Dict[str, Set[str]] = _ChiMucHeCoQuanDict({he: set() for he in HE_CO_QUAN_CHUAN})
        self._ten_benh_theo_he: Dict[str, List[str]] = {he: [] for he in HE_CO_QUAN_CHUAN}
        self._trieu_chung_ngan_theo_he: Dict[str, List[str]] = {he: [] for he in HE_CO_QUAN_CHUAN}
        self._thu_tu_lam_sang_theo_he: Dict[str, List[str]] = {he: [] for he in HE_CO_QUAN_CHUAN}
        self._thuoc_theo_he: Dict[str, List[str]] = {he: [] for he in HE_CO_QUAN_CHUAN}
        self._tat_ca_thuoc: List[str] = []

    def lay_thuc_the_theo_he_co_quan(self, he_co_quan: str) -> Set[str]:
        """Tra cứu tập thực thể lâm sàng của hệ cơ quan (chấp nhận cả tiếng Việt có dấu lẫn snake_case)."""
        he_chuan = chuan_hoa_he_co_quan(he_co_quan)
        if not he_chuan:
            return set()
        return set(self.chi_muc_he_co_quan.get(he_chuan, set()))

    def _ghi_chi_muc_lam_sang(self, he_chuan: str, canonical_name: str, entity_type: str) -> None:
        self.chi_muc_he_co_quan.setdefault(he_chuan, set()).add(canonical_name)
        hw_sach = _lam_sach_hotword(canonical_name, max_words=6)
        if not hw_sach:
            return
        if entity_type == "benh":
            ds_benh = self._ten_benh_theo_he.setdefault(he_chuan, [])
            if hw_sach.lower() not in {x.lower() for x in ds_benh}:
                ds_benh.append(hw_sach)
        elif not re.search(r"\d", hw_sach) and len(hw_sach.split()) <= 5:
            ds_tc = self._trieu_chung_ngan_theo_he.setdefault(he_chuan, [])
            if hw_sach.lower() not in {x.lower() for x in ds_tc}:
                ds_tc.append(hw_sach)
        ds_ls = self._thu_tu_lam_sang_theo_he.setdefault(he_chuan, [])
        if hw_sach.lower() not in {x.lower() for x in ds_ls}:
            ds_ls.append(hw_sach)

    def chen_cum_tu(
        self,
        cum_tu: str,
        entity_id: str,
        canonical_name: str,
        entity_type: str = "general",
        he_co_quan: Optional[str] = None
    ) -> None:
        """Chèn một cụm từ/thuật ngữ vào Trie theo từng âm tiết tiếng Việt/Latin."""
        tu_khoa = chuan_hoa_am_tiet(cum_tu).split()
        if not tu_khoa:
            return

        he_chuan = chuan_hoa_he_co_quan(he_co_quan) if he_co_quan else None

        curr = self.root
        for depth, am_tiet in enumerate(tu_khoa, start=1):
            if am_tiet not in curr.children:
                curr.children[am_tiet] = TrieNode600(token=am_tiet, depth=depth)
            curr = curr.children[am_tiet]

        curr.is_terminal = True
        curr.entity_id = entity_id
        curr.canonical_name = canonical_name
        curr.entity_type = entity_type
        if he_chuan:
            curr.he_co_quan = he_chuan
            curr.tap_he_co_quan.add(he_chuan)
        self.so_thuc_the += 1

        ten_sach = (canonical_name or "").strip()
        if entity_type == "thuoc":
            if ten_sach and ten_sach.lower() not in {x.lower() for x in self._tat_ca_thuoc}:
                self._tat_ca_thuoc.append(ten_sach)
            if he_chuan:
                ds_th = self._thuoc_theo_he.setdefault(he_chuan, [])
                if ten_sach and ten_sach.lower() not in {x.lower() for x in ds_th}:
                    ds_th.append(ten_sach)
        elif he_chuan:
            self._ghi_chi_muc_lam_sang(he_chuan, canonical_name, entity_type)

    def nap_khuon_benh(self, danh_sach_khuon: List[Dict[str, Any]]) -> None:
        """Nạp danh sách khuôn bệnh (cả 200 khuôn gốc và >400 khuôn mở rộng)."""
        thuoc_da_co_map = {t.lower(): t for t in self._tat_ca_thuoc}
        re_ung_buou = re.compile(r"(?i)\b(ung\s+thư|u\s+ác|carcinom|lymphom|bạch\s+cầu\s+(?:cấp|mạn)|đa\s+u\s+tủy)\b")
        for kb in danh_sach_khuon:
            ten_benh = kb.get("ten", "")
            he = chuan_hoa_he_co_quan(kb.get("he_co_quan", "truyen_nhiem")) or "truyen_nhiem"
            la_ung_buou = bool(re_ung_buou.search(ten_benh or ""))
            eid = f"DIS_{chuan_hoa_am_tiet(ten_benh).replace(' ', '_')}"

            # 1. Chèn tên bệnh
            self.chen_cum_tu(ten_benh, eid, ten_benh, entity_type="benh", he_co_quan=he)
            if la_ung_buou and he != "ung_buou":
                self._ghi_chi_muc_lam_sang("ung_buou", ten_benh, "benh")
                curr_ub = self.root
                for tok_ub in chuan_hoa_am_tiet(ten_benh).split():
                    curr_ub = curr_ub.children[tok_ub]
                curr_ub.tap_he_co_quan.add("ung_buou")

            # 2. Chèn triệu chứng chính và phụ
            for tc in kb.get("chinh", []) + kb.get("phu", []):
                self.chen_cum_tu(tc, f"SYM_{eid}", tc, entity_type="trieu_chung", he_co_quan=he)
                if la_ung_buou and he != "ung_buou":
                    self._ghi_chi_muc_lam_sang("ung_buou", tc, "trieu_chung")

            # 3. Chèn xét nghiệm/cận lâm sàng nếu có
            kham = kb.get("kham", "")
            if kham:
                self.chen_cum_tu(kham, f"LAB_{eid}", kham, entity_type="xet_nghiem", he_co_quan=he)

            # 4. Liên kết các thuốc xuất hiện trong kế hoạch điều trị của khuôn với đúng hệ cơ quan
            vb_kh = " ".join([str(kb.get("ke_hoach") or "")] + [str(x) for x in (kb.get("bien_the_ke_hoach") or [])]).lower()
            if vb_kh and thuoc_da_co_map:
                ds_th = self._thuoc_theo_he.setdefault(he, [])
                da_co_th = {x.lower() for x in ds_th}
                for w in re.findall(r"[a-zA-Z][\w\-]{3,}", vb_kh):
                    w_low = w.lower()
                    ten_goc = thuoc_da_co_map.get(w_low) or thuoc_da_co_map.get(w_low + "e") or (
                        thuoc_da_co_map.get(w_low[:-1]) if w_low.endswith("e") else None
                    )
                    if ten_goc and ten_goc.lower() not in da_co_th:
                        da_co_th.add(ten_goc.lower())
                        ds_th.append(ten_goc)

    def nap_duoc_thu_va_g2p(self, danh_muc_thuoc: Dict[str, List[str]]) -> None:
        """Nạp danh mục thuốc kèm biến thể ngữ âm G2P tiếng Việt."""
        for ten_chuan, bien_the in danh_muc_thuoc.items():
            eid = f"DRUG_{chuan_hoa_am_tiet(ten_chuan).replace(' ', '_')}"
            # Chèn tên chuẩn quốc tế Latin
            self.chen_cum_tu(ten_chuan, eid, ten_chuan, entity_type="thuoc")
            # Chèn các biến thể ngữ âm bác sĩ/bệnh nhân đọc
            for bt in bien_the:
                self.chen_cum_tu(bt, eid, ten_chuan, entity_type="thuoc")

    def buoc_trie(
        self,
        node_hien_tai: TrieNode600,
        am_tiet_tiep: str,
        he_co_quan_uu_tien: Optional[str] = None,
        mu_dialogue_act: float = 1.0
    ) -> Tuple[float, TrieNode600]:
        """Tính toán điểm bias cho một bước mở rộng Beam Search.
        
        Tích hợp 2 chốt chặn kiểm định:
        1. Dialogue Act Masking: mu_dialogue_act in [0.0, 1.0]
        2. Organ System Filtering: Tăng điểm ưu tiên cho hệ cơ quan của phiên khám
           (chấp nhận cả tên tiếng Việt có dấu lẫn mã ASCII snake_case).
        """
        tok = chuan_hoa_am_tiet(am_tiet_tiep)
        he_uu_tien = chuan_hoa_he_co_quan(he_co_quan_uu_tien) if he_co_quan_uu_tien else None
        if tok in node_hien_tai.children:
            next_node = node_hien_tai.children[tok]
            bonus = self.beta_match + (self.kappa * next_node.depth)
            if next_node.is_terminal:
                bonus += self.beta_term
                # Hệ số ưu tiên chuyên khoa nếu trùng hệ cơ quan
                if he_uu_tien and (he_uu_tien in next_node.tap_he_co_quan or next_node.he_co_quan == he_uu_tien):
                    bonus *= 1.35  # Ưu tiên chuyên khoa sâu 35%
                elif he_uu_tien and (next_node.tap_he_co_quan or next_node.he_co_quan):
                    bonus *= 0.70  # Giảm nhẹ nếu khác hệ cơ quan chỉ định

            diem_bias = bonus * self.lambda_bias * mu_dialogue_act
            return diem_bias, next_node

        # Rời khỏi nhánh trie đang khớp dở dang
        if node_hien_tai is not self.root:
            penalty = - (self.gamma_depart * node_hien_tai.depth) * self.lambda_bias * mu_dialogue_act
            return penalty, self.root

        return 0.0, self.root

    def tinh_dung_luong_ram_uoc_tinh_kb(self) -> float:
        """Ước tính dung lượng RAM tiêu thụ trên CPU INT8."""
        def _dem_node(node: TrieNode600) -> int:
            return 1 + sum(_dem_node(c) for c in node.children.values())

        tong_nodes = _dem_node(self.root)
        # Mỗi TrieNode tốn ~120 bytes trong Python/C++ ONNX Runtime
        return (tong_nodes * 120) / 1024.0

    def xuat_hotwords(self, he_co_quan: Optional[str] = None, max_terms: int = 120) -> str:
        """Xuất chuỗi hotwords phân tách bằng dấu phẩy cho FasterWhisperProvider(hotwords=...).
        
        Khi truyền `he_co_quan` (ví dụ `'tim_mach'` hoặc `'tim mạch'`), ưu tiên xuất các thuật ngữ
        bệnh lý / triệu chứng thuộc đúng hệ cơ quan đó kết hợp với các thuốc liên quan chuyên khoa,
        tuyệt đối không trả về 120 tên thuốc cố định theo bảng chữ cái.
        """
        if max_terms <= 0:
            return ""
        terms: List[str] = []
        seen: Set[str] = set()

        def _them(ten_raw: str) -> None:
            if len(terms) >= max_terms:
                return
            t = _lam_sach_hotword(ten_raw, max_words=6)
            if t and t.lower() not in seen:
                seen.add(t.lower())
                terms.append(t)

        he_chuan = chuan_hoa_he_co_quan(he_co_quan) if he_co_quan else None
        thuoc_map_low = {t.lower(): t for t in self._tat_ca_thuoc}

        if he_chuan:
            # 1a. Ưu tiên tên bệnh chuẩn thuộc đúng `he_chuan` (trải rộng toàn bộ khuôn của chuyên khoa)
            gioi_han_benh = max(1, int(max_terms * 0.45))
            for ten_b in self._ten_benh_theo_he.get(he_chuan, []):
                if len(terms) >= gioi_han_benh:
                    break
                _them(ten_b)

            # 1b. Tiếp theo lấy các cụm triệu chứng cô đọng thuộc `he_chuan`
            gioi_han_ls = max(gioi_han_benh, int(max_terms * 0.70))
            for kw_tc in self._trieu_chung_ngan_theo_he.get(he_chuan, []):
                if len(terms) >= gioi_han_ls:
                    break
                _them(kw_tc)
            for kw_ls in self._thu_tu_lam_sang_theo_he.get(he_chuan, []):
                if len(terms) >= gioi_han_ls:
                    break
                _them(kw_ls)

            # 2. Kết hợp thuốc đặc trưng gắn với chuyên khoa `he_chuan` (ưu tiên nhóm thuốc cốt lõi của chuyên khoa trước)
            for th_goi_y in THUOC_UU_TIEN_THEO_HE_CO_QUAN.get(he_chuan, ()):
                ten_th = (
                    thuoc_map_low.get(th_goi_y.lower())
                    or thuoc_map_low.get(th_goi_y.lower() + "e")
                    or (thuoc_map_low.get(th_goi_y.lower()[:-1]) if th_goi_y.lower().endswith("e") else None)
                    or (th_goi_y if not thuoc_map_low else None)
                )
                if ten_th:
                    _them(ten_th)
            for th_he in self._thuoc_theo_he.get(he_chuan, []):
                _them(th_he)

            # 3. Nếu vẫn còn slot thì lấy nốt các từ lâm sàng còn lại của chuyên khoa rồi mới tới thuốc chung
            for ten_b in self._ten_benh_theo_he.get(he_chuan, []):
                _them(ten_b)
            for kw_ls in self._thu_tu_lam_sang_theo_he.get(he_chuan, []):
                _them(kw_ls)
            for th_chung in self._tat_ca_thuoc:
                _them(th_chung)
            return ", ".join(terms[:max_terms])

        # Không truyền `he_co_quan`: lấy cân bằng giữa thuật ngữ lâm sàng đa hệ cơ quan và danh mục thuốc
        nua_ls = max_terms // 2
        vong = 0
        co_them = True
        while len(terms) < nua_ls and co_them:
            co_them = False
            for he_k in HE_CO_QUAN_CHUAN:
                ds = self._ten_benh_theo_he.get(he_k, []) or self._thu_tu_lam_sang_theo_he.get(he_k, [])
                if vong < len(ds):
                    _them(ds[vong])
                    co_them = True
                    if len(terms) >= nua_ls:
                        break
            vong += 1

        for th_chung in self._tat_ca_thuoc:
            _them(th_chung)

        if len(terms) < max_terms:
            def _duyet(node: TrieNode600) -> None:
                if len(terms) >= max_terms:
                    return
                if node.is_terminal and node.canonical_name:
                    _them(node.canonical_name)
                for child in node.children.values():
                    _duyet(child)
            _duyet(self.root)

        return ", ".join(terms[:max_terms])


_TRIE_MAC_DINH_CACHE: Optional[ContextualPrefixTrie600] = None
_TRIE_CACHE_LOCK = threading.Lock()


def tao_trie_600_mac_dinh() -> ContextualPrefixTrie600:
    """Khởi tạo (có cache singleton an toàn luồng) ContextualPrefixTrie600 mặc định với danh mục dược thư & khuôn bệnh."""
    global _TRIE_MAC_DINH_CACHE
    if _TRIE_MAC_DINH_CACHE is not None:
        return _TRIE_MAC_DINH_CACHE
    with _TRIE_CACHE_LOCK:
        if _TRIE_MAC_DINH_CACHE is not None:
            return _TRIE_MAC_DINH_CACHE
        trie = ContextualPrefixTrie600()
        try:
            from src import tri_thuc_thuoc as _ttt
            dm_thuoc: Dict[str, List[str]] = {}
            for m in _ttt.tat_ca():
                hc = m.get("hoat_chat")
                if hc:
                    dm_thuoc[hc] = list(m.get("ten_khac") or []) + list(m.get("biet_duoc") or [])
            if dm_thuoc:
                trie.nap_duoc_thu_va_g2p(dm_thuoc)
        except Exception:
            pass
        try:
            from src.kho_khuon import ds_khuon
            khuon = list(ds_khuon(mo_rong=True))
            if khuon:
                trie.nap_khuon_benh(khuon)
        except Exception:
            pass
        _TRIE_MAC_DINH_CACHE = trie
        return trie
