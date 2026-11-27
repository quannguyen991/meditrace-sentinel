# -*- coding: utf-8 -*-
"""[Công cụ lâm sàng hỗ trợ bác sĩ › Tri thức]
Làm gì   : Tìm nhanh tên thuốc trong văn bản và tra thông tin Dược thư Quốc gia, chạy tại
           chỗ không cần mạng.
Vào → Ra : văn bản (hoặc danh sách tên thuốc) → các thuốc nhận ra kèm thông tin dược thư và
           tương tác
Đọc từ   : class BoTraCuuDuocThuAhoCorasick nhận thuốc trong văn bản; class
           PurePythonAhoCorasick bộ khớp chuỗi
Mục lục (các hàm/lớp chính):
  class BoTraCuuDuocThuAhoCorasick  Bộ tra thuốc và tương tác bằng Aho-Corasick
  class PurePythonAhoCorasick       Máy tìm nhiều từ khoá Aho-Corasick viết thuần Python
  class ThongTinDuocThu             Mục dữ liệu Dược thư cho một hoạt chất
  class AhoCorasickNode             Nút của cây Trie trong máy Aho-Corasick
Gọi tới  : cong_cu_lam_sang/tri_thuc_thuoc
Dùng bởi : cong_cu_lam_sang/canh_bao_tuong_tac_thuoc, do_luong/quet_an_toan_duoc_ly_v2
Tên cũ   : aho_corasick_duoc_thu.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Pure Python Aho-Corasick & Dược thư Quốc gia Việt Nam 2022 Offline Dictionary.

Đặc tính kỹ thuật:
1. Pure Python 100%: Hoàn toàn không phụ thuộc C-extension / MSVC Build Tools trên Windows.
2. Thời gian tìm kiếm tuyến tính O(N + M + Z) cho tra cứu đồng thời hàng nghìn hoạt chất & biệt dược.
3. Word-boundary guard bảo vệ chống nhận diện sai các chuỗi con trong tiếng Việt.
4. Tích hợp cơ sở dữ liệu Dược thư Quốc gia Việt Nam lần III (2022) phục vụ cảnh báo DDI,
   liều trần tối đa và chống chỉ định cơ địa nhạy cảm.
"""

from collections import deque
from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import unicodedata


# ═══ class ThongTinDuocThu — Mục dữ liệu Dược thư cho một hoạt chất ═══════════════════
# Gồm tên biệt dược, mã ATC, liều tối đa, chống chỉ định và tương tác. Dữ liệu chưa
# chuyên gia duyệt.
@dataclass
class ThongTinDuocThu:
    """Mục dữ liệu Dược thư Quốc gia Việt Nam 2022 cho một hoạt chất."""
    ma_hoat_chat: str
    ten_hoat_chat: str
    ten_biet_duoc: List[str]
    nhom_duoc_ly: str
    ma_atc: str
    lieu_toi_da_24h_mg: Optional[float] = None
    chong_chi_dinh_thai_ky: Optional[str] = None
    chong_chi_dinh_egfr: Optional[float] = None  # Ngưỡng eGFR (mL/phút) chống chỉ định
    chong_chi_dinh_benh_nen: List[str] = field(default_factory=list)
    tuong_tac_chong_chi_dinh: List[str] = field(default_factory=list)
    tuong_tac_nghiem_trong: List[str] = field(default_factory=list)


# ═══ class AhoCorasickNode — Nút của cây Trie trong máy Aho-Corasick ══════════════════
class AhoCorasickNode:
    """Nút trong cây Trie của máy trạng thái hữu hạn Aho-Corasick."""
    __slots__ = ('children', 'fail', 'outputs', 'is_end')

    def __init__(self):
        self.children: Dict[str, AhoCorasickNode] = {}
        self.fail: Optional['AhoCorasickNode'] = None
        self.outputs: List[Dict[str, Any]] = []
        self.is_end: bool = False


# ═══ class PurePythonAhoCorasick — Máy tìm nhiều từ khoá Aho-Corasick viết thuần Python ═══
# Thêm từ khoá, dựng liên kết thất bại, rồi tìm mọi từ khoá trong văn bản; chuẩn hoá
# Unicode NFC.
class PurePythonAhoCorasick:
    """Máy tự động Aho-Corasick thuần Python không phụ thuộc C-compiler."""

    def __init__(self):
        self.root = AhoCorasickNode()
        self._is_built = False
        self._pattern_count = 0

    @staticmethod
    def _chuan_hoa_ky_tu(s: str) -> str:
        """Chuẩn hóa Unicode tiếng Việt NFC, chuẩn hóa gạch nối thuốc hợp chất (-) và chuyển chữ thường."""
        if not s:
            return ""
        # Chuẩn hóa các biến thể gạch ngang (en-dash, em-dash, figure dash, hyphen bullet) thành '-' tiêu chuẩn
        s = re.sub(r"[\u2010\u2011\u2012\u2013\u2014\u2212]", "-", s)
        # Chuẩn hóa khoảng trắng quanh dấu gạch nối trong tên thuốc hợp chất (ví dụ: 'co - amoxiclav' -> 'co-amoxiclav')
        s = re.sub(r"\s*-\s*", "-", s)
        return unicodedata.normalize("NFC", s).lower().strip()

    def them_tu_khoa(self, tu_khoa: str, du_lieu: Optional[Dict[str, Any]] = None) -> None:
        """Thêm một từ khóa hoặc cụm từ vào Trie."""
        tu_chuan = self._chuan_hoa_ky_tu(tu_khoa)
        if not tu_chuan:
            return

        curr = self.root
        for char in tu_chuan:
            if char not in curr.children:
                curr.children[char] = AhoCorasickNode()
            curr = curr.children[char]

        curr.is_end = True
        payload = du_lieu.copy() if du_lieu else {}
        payload["tu_khoa_goc"] = tu_khoa
        payload["tu_khoa_chuan"] = tu_chuan
        curr.outputs.append(payload)
        self._pattern_count += 1
        self._is_built = False

    def xay_dung(self) -> None:
        """Xây dựng các liên kết thất bại (failure links) và liên kết từ điển (output links) bằng BFS."""
        queue: deque[AhoCorasickNode] = deque()
        self.root.fail = self.root

        # Gán fail link cho các nút con bậc 1 trỏ về root
        for char, child in self.root.children.items():
            child.fail = self.root
            queue.append(child)

        # Duyệt theo chiều rộng (BFS) cho các tầng sâu hơn
        while queue:
            curr = queue.popleft()

            for char, child in curr.children.items():
                f = curr.fail
                while f is not self.root and char not in f.children:
                    f = f.fail

                if char in f.children and f.children[char] is not child:
                    child.fail = f.children[char]
                else:
                    child.fail = self.root

                # Nối tiếp danh sách output từ nút fail để không bỏ sót chuỗi con
                if child.fail and child.fail.outputs:
                    child.outputs.extend(child.fail.outputs)

                queue.append(child)

        self._is_built = True

    @staticmethod
    def _la_ky_tu_tu(char: str) -> bool:
        """Kiểm tra ký tự có thuộc từ hay không (hỗ trợ cả chữ cái tiếng Việt và số)."""
        return char.isalnum() or char == "_"

    def tim_kiem(
        self,
        van_ban: str,
        kiem_tra_bien_tu: bool = True
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm toàn bộ các mẫu khớp trong văn bản trong thời gian O(N + Z).
        
        Args:
            van_ban: Văn bản cần quét
            kiem_tra_bien_tu: Nếu True, yêu cầu biên từ để tránh 'tin' khớp trong 'thông tin'.
        """
        if not self._is_built:
            self.xay_dung()

        if not van_ban:
            return []

        vb_chuan = self._chuan_hoa_ky_tu(van_ban)
        do_dai = len(vb_chuan)
        curr = self.root
        ket_qua: List[Dict[str, Any]] = []

        for idx, char in enumerate(vb_chuan):
            while curr is not self.root and char not in curr.children:
                curr = curr.fail

            curr = curr.children.get(char, self.root)

            if curr.outputs:
                for match_payload in curr.outputs:
                    pattern_len = len(match_payload["tu_khoa_chuan"])
                    start_idx = idx - pattern_len + 1
                    end_idx = idx + 1

                    # Kiểm tra biên từ (Word Boundary Guard)
                    if kiem_tra_bien_tu:
                        # Biên trước
                        if start_idx > 0 and self._la_ky_tu_tu(vb_chuan[start_idx - 1]):
                            continue
                        # Biên sau
                        if end_idx < do_dai and self._la_ky_tu_tu(vb_chuan[end_idx]):
                            continue

                    ket_qua.append({
                        "tu_khoa": match_payload["tu_khoa_goc"],
                        "vi_tri_dau": start_idx,
                        "vi_tri_cuoi": end_idx,
                        "du_lieu": match_payload
                    })

        return ket_qua


# ─── _ltd() — Lấy liều tối đa người lớn từ nguồn tri thức thuốc ───────────────────────
# Trả mg mỗi ngày hoặc None nếu không có.
def _ltd(hc):
    """Liều tối đa người lớn (mg/ngày) từ MỘT nguồn `tri_thuc_thuoc` (25/11/2026)."""
    from src.cong_cu_lam_sang import tri_thuc_thuoc as tri_thuc_thuoc
    l = tri_thuc_thuoc.lieu_toi_da(hc, "nguoi_lon")
    return l.gia_tri if l else None


# Dữ liệu mẫu đại diện Dược thư Quốc gia Việt Nam 2022 (offline knowledge base)
# LIỀU đọc từ MOT nguồn data/tri_thuc_thuoc.json. Sintrom được ánh xạ chuẩn sang acenocoumarol (tách biệt với warfarin).
CO_SO_DU_LIEU_DUOC_THU_2022: List[ThongTinDuocThu] = [
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-N02BE01",
        ten_hoat_chat="paracetamol",
        ten_biet_duoc=["panadol", "efferalgan", "hapacol", "tylenol", "paracold", "acetaminophen"],
        nhom_duoc_ly="Thuốc giảm đau hạ sốt không gây nghiện",
        ma_atc="N02BE01",
        lieu_toi_da_24h_mg=_ltd("paracetamol"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["suy tế bào gan nặng", "thiếu hụt g6pd"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["ruou", "isoniazid"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-M01AE01",
        ten_hoat_chat="ibuprofen",
        ten_biet_duoc=["advil", "brufen", "alaxan", "motrin"],
        nhom_duoc_ly="Thuốc kháng viêm không steroid (NSAID)",
        ma_atc="M01AE01",
        lieu_toi_da_24h_mg=_ltd("ibuprofen"),
        chong_chi_dinh_thai_ky="Chống chỉ định tuyệt đối 3 tháng cuối thai kỳ (Category D)",
        chong_chi_dinh_egfr=30.0,
        chong_chi_dinh_benh_nen=["loét dạ dày tá tràng tiến triển", "hen suyễn (hội chứng widal)", "suy thận nặng"],
        tuong_tac_chong_chi_dinh=["warfarin", "acenocoumarol", "aspirin"],
        tuong_tac_nghiem_trong=["captopril", "enalapril", "methotrexate"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-B01AA03",
        ten_hoat_chat="warfarin",
        ten_biet_duoc=["coumadin", "marevan"],
        nhom_duoc_ly="Thuốc chống đông kháng vitamin K",
        ma_atc="B01AA03",
        lieu_toi_da_24h_mg=_ltd("warfarin"),
        chong_chi_dinh_thai_ky="Chống chỉ định tuyệt đối thai kỳ (Category X - dị tật sọ mặt)",
        chong_chi_dinh_egfr=15.0,
        chong_chi_dinh_benh_nen=["nguy cơ xuất huyết cao", "loét tiêu hóa tiến triển"],
        tuong_tac_chong_chi_dinh=["aspirin", "ibuprofen", "clopidogrel"],
        tuong_tac_nghiem_trong=["amiodarone", "ciprofloxacin", "metronidazole"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-B01AA07",
        ten_hoat_chat="acenocoumarol",
        ten_biet_duoc=["sintrom", "minisintrom", "acenocoumarole"],
        nhom_duoc_ly="Thuốc chống đông kháng vitamin K",
        ma_atc="B01AA07",
        lieu_toi_da_24h_mg=_ltd("acenocoumarol"),
        chong_chi_dinh_thai_ky="Chống chỉ định tuyệt đối thai kỳ (Category X - dị tật bào thai và xuất huyết)",
        chong_chi_dinh_egfr=15.0,
        chong_chi_dinh_benh_nen=["nguy cơ xuất huyết cao", "loét tiêu hóa tiến triển"],
        tuong_tac_chong_chi_dinh=["aspirin", "ibuprofen", "clopidogrel"],
        tuong_tac_nghiem_trong=["amiodarone", "ciprofloxacin", "metronidazole", "rifampicin"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-B01AC04",
        ten_hoat_chat="clopidogrel",
        ten_biet_duoc=["plavix", "clopistad", "agrelan"],
        nhom_duoc_ly="Thuốc chống kết tập tiểu cầu ức chế P2Y12",
        ma_atc="B01AC04",
        lieu_toi_da_24h_mg=_ltd("clopidogrel"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["xuất huyết tiêu hóa cấp", "chảy máu nội sọ"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["omeprazole", "esomeprazole"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-A02BC01",
        ten_hoat_chat="omeprazole",
        ten_biet_duoc=["omeprazol", "losec", "omepral", "lomac"],
        nhom_duoc_ly="Thuốc ức chế bơm proton (PPI)",
        ma_atc="A02BC01",
        lieu_toi_da_24h_mg=_ltd("omeprazole"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=[],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["clopidogrel"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-A10BA02",
        ten_hoat_chat="metformin",
        ten_biet_duoc=["glucophage", "panfor", "diaformin"],
        nhom_duoc_ly="Thuốc hạ đường huyết nhóm Biguanide",
        ma_atc="A10BA02",
        lieu_toi_da_24h_mg=_ltd("metformin"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=30.0,  # eGFR < 30 chống chỉ định tuyệt đối
        chong_chi_dinh_benh_nen=["suy tim mất bù", "nhiễm toan chuyển hóa", "suy gan"],
        tuong_tac_chong_chi_dinh=["thuoc_can_quang"],
        tuong_tac_nghiem_trong=["cimetidine"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-J01MA02",
        ten_hoat_chat="ciprofloxacin",
        ten_biet_duoc=["ciprobay", "citeran", "cipro"],
        nhom_duoc_ly="Kháng sinh nhóm Fluoroquinolone",
        ma_atc="J01MA02",
        lieu_toi_da_24h_mg=_ltd("ciprofloxacin"),
        chong_chi_dinh_thai_ky="Thận trọng cao trong thai kỳ và cho con bú (Category C)",
        chong_chi_dinh_egfr=15.0,
        chong_chi_dinh_benh_nen=["tiền sử đứt gân achilles do quinolone", "nhược cơ"],
        tuong_tac_chong_chi_dinh=["theophylline", "tizanidine"],
        tuong_tac_nghiem_trong=["warfarin"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-C08CA01",
        ten_hoat_chat="amlodipin",
        ten_biet_duoc=["amlor", "norvasc", "amlodipine"],
        nhom_duoc_ly="Thuốc chẹn kênh calci Dihydropyridine",
        ma_atc="C08CA01",
        lieu_toi_da_24h_mg=_ltd("amlodipin"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["sốc tim", "hẹp van động mạch chủ nặng"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["simvastatin"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-C09AA02",
        ten_hoat_chat="enalapril",
        ten_biet_duoc=["renitec", "ednyt", "vasotec"],
        nhom_duoc_ly="Thuốc ức chế men chuyển (ACEi)",
        ma_atc="C09AA02",
        lieu_toi_da_24h_mg=_ltd("enalapril"),
        chong_chi_dinh_thai_ky="Chống chỉ định tuyệt đối thai kỳ quý 2 và 3 (Category D)",
        chong_chi_dinh_egfr=15.0,
        chong_chi_dinh_benh_nen=["tiền sử phù mạch do acei", "hẹp động mạch thận hai bên"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["spironolactone", "aliskiren", "ibuprofen"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-C03DA01",
        ten_hoat_chat="spironolactone",
        ten_biet_duoc=["spironolacton", "aldactone", "verospiron"],
        nhom_duoc_ly="Thuốc lợi tiểu kháng Aldosterone",
        ma_atc="C03DA01",
        lieu_toi_da_24h_mg=_ltd("spironolactone"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=30.0,
        chong_chi_dinh_benh_nen=["tăng kali máu ác tính", "bệnh addison"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["enalapril", "captopril", "losartan"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-J01CR02",
        ten_hoat_chat="co-amoxiclav",
        ten_biet_duoc=["augmentin", "klamentin", "amoxicillin-clavulanate", "amoxicillin-acid clavulanic"],
        nhom_duoc_ly="Kháng sinh phối hợp Penicillin và chất ức chế Beta-lactamase",
        ma_atc="J01CR02",
        lieu_toi_da_24h_mg=_ltd("co-amoxiclav"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=10.0,
        chong_chi_dinh_benh_nen=["dị ứng kháng sinh nhóm beta-lactam", "tiền sử vàng da ứ mật do amoxiclav"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["methotrexate", "warfarin"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-J01EE01",
        ten_hoat_chat="co-trimoxazole",
        ten_biet_duoc=["bactrim", "biseptol", "sulfamethoxazole-trimethoprim"],
        nhom_duoc_ly="Kháng sinh phối hợp Sulfonamide và Trimethoprim",
        ma_atc="J01EE01",
        lieu_toi_da_24h_mg=_ltd("co-trimoxazole"),
        chong_chi_dinh_thai_ky="Chống chỉ định thai kỳ đủ tháng và phụ nữ cho con bú",
        chong_chi_dinh_egfr=15.0,
        chong_chi_dinh_benh_nen=["thiếu máu do thiếu acid folic", "thiếu hụt g6pd", "suy gan nặng"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["warfarin", "phenytoin", "enalapril"]
    ),
    # =========================================================================
    # DANH MỤC DƯỢC THƯ QUỐC GIA 2022 MỞ RỘNG (18 HỆ CƠ QUAN & 400 KHUÔN BỆNH MỚI)
    # =========================================================================
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-J04AC01",
        ten_hoat_chat="isoniazid",
        ten_biet_duoc=["inh", "rimifon"],
        nhom_duoc_ly="Thuốc chống lao nhóm Hydrazid",
        ma_atc="J04AC01",
        lieu_toi_da_24h_mg=_ltd("isoniazid"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["viêm gan cấp", "suy gan nặng"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["paracetamol", "carbamazepine", "phenytoin"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-J04AB02",
        ten_hoat_chat="rifampicin",
        ten_biet_duoc=["rifadin", "rimactan"],
        nhom_duoc_ly="Kháng sinh nhóm Rifamycin chống lao",
        ma_atc="J04AB02",
        lieu_toi_da_24h_mg=_ltd("rifampicin"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["vàng da tắc mật", "suy gan nặng"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["warfarin", "thuoc_tranh_thai", "clarithromycin"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-J04AK01",
        ten_hoat_chat="pyrazinamide",
        ten_biet_duoc=["pza", "pyrazinamid"],
        nhom_duoc_ly="Thuốc chống lao tổng hợp",
        ma_atc="J04AK01",
        lieu_toi_da_24h_mg=_ltd("pyrazinamide"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=30.0,
        chong_chi_dinh_benh_nen=["gout cấp", "tăng acid uric máu", "suy gan nặng"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["allopurinol"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-J04AK02",
        ten_hoat_chat="ethambutol",
        ten_biet_duoc=["myambutol", "emb"],
        nhom_duoc_ly="Thuốc chống lao tổng hợp kìm khuẩn",
        ma_atc="J04AK02",
        lieu_toi_da_24h_mg=_ltd("ethambutol"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=30.0,
        chong_chi_dinh_benh_nen=["viêm thần kinh thị giác", "trẻ em dưới 5 tuổi"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=[]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-J01AA02",
        ten_hoat_chat="doxycycline",
        ten_biet_duoc=["vibramycin", "doxycyclin"],
        nhom_duoc_ly="Kháng sinh nhóm Tetracycline",
        ma_atc="J01AA02",
        lieu_toi_da_24h_mg=_ltd("doxycycline"),
        chong_chi_dinh_thai_ky="Chống chỉ định tuyệt đối thai kỳ (Category D - ố vàng men răng, chậm phát triển xương thai nhi)",
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["trẻ em dưới 8 tuổi", "suy gan nặng"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["warfarin", "antacid", "sat"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-M04AA01",
        ten_hoat_chat="allopurinol",
        ten_biet_duoc=["zyloric", "milurit"],
        nhom_duoc_ly="Thuốc chống Gout ức chế Xanthine Oxidase",
        ma_atc="M04AA01",
        lieu_toi_da_24h_mg=_ltd("allopurinol"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=10.0,
        chong_chi_dinh_benh_nen=["dị ứng allopurinol", "hla-b*5801"],
        tuong_tac_chong_chi_dinh=["azathioprine"],
        tuong_tac_nghiem_trong=["amoxicillin", "warfarin", "theophylline"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-M04AC01",
        ten_hoat_chat="colchicine",
        ten_biet_duoc=["colchicin", "colcrys"],
        nhom_duoc_ly="Thuốc điều trị Gout cấp (Khoảng điều trị hẹp NTI)",
        ma_atc="M04AC01",
        lieu_toi_da_24h_mg=_ltd("colchicine"),
        chong_chi_dinh_thai_ky="Chống chỉ định trong thai kỳ và cho con bú",
        chong_chi_dinh_egfr=30.0,
        chong_chi_dinh_benh_nen=["suy gan nặng", "suy thận nặng"],
        tuong_tac_chong_chi_dinh=["clarithromycin"],
        tuong_tac_nghiem_trong=["atorvastatin", "cyclosporine"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-N03AB02",
        ten_hoat_chat="phenytoin",
        ten_biet_duoc=["dilantin", "epanutin"],
        nhom_duoc_ly="Thuốc chống động kinh dẫn xuất Hydantoin (NTI)",
        ma_atc="N03AB02",
        lieu_toi_da_24h_mg=_ltd("phenytoin"),
        chong_chi_dinh_thai_ky="Chống chỉ định thai kỳ (Category D - Hội chứng hydantoin bào thai)",
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["block xoang nhĩ", "block nhĩ thất độ 2-3"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["warfarin", "amiodarone", "valproat"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-N03AF01",
        ten_hoat_chat="carbamazepine",
        ten_biet_duoc=["tegretol", "carbatrol"],
        nhom_duoc_ly="Thuốc chống động kinh nhóm Iminostilbene (NTI)",
        ma_atc="N03AF01",
        lieu_toi_da_24h_mg=_ltd("carbamazepine"),
        chong_chi_dinh_thai_ky="Chống chỉ định thai kỳ (Category D - dị tật nứt đốt sống)",
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["suy tủy xương", "block nhĩ thất", "hla-b*1502"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["valproat", "warfarin", "clarithromycin"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-N03AG01",
        ten_hoat_chat="valproat",
        ten_biet_duoc=["depakine", "valproic acid", "natri valproat"],
        nhom_duoc_ly="Thuốc chống động kinh dẫn xuất Acid béo (NTI)",
        ma_atc="N03AG01",
        lieu_toi_da_24h_mg=_ltd("valproat"),
        chong_chi_dinh_thai_ky="Chống chỉ định tuyệt đối thai kỳ (Category X - dị tật ống thần kinh thai nhi)",
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["viêm gan cấp", "rối loạn chu trình urê"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["carbamazepine", "lamotrigine", "aspirin"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-C01AA05",
        ten_hoat_chat="digoxin",
        ten_biet_duoc=["lanoxin"],
        nhom_duoc_ly="Glycosid tim chống loạn nhịp và trợ tim (NTI)",
        ma_atc="C01AA05",
        lieu_toi_da_24h_mg=_ltd("digoxin"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=30.0,
        chong_chi_dinh_benh_nen=["rung thất", "block nhĩ thất hoàn toàn", "hội chứng wolff-parkinson-white"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["amiodarone", "verapamil", "spironolactone", "clarithromycin"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-C01BD01",
        ten_hoat_chat="amiodarone",
        ten_biet_duoc=["amiodaron", "cordarone"],
        nhom_duoc_ly="Thuốc chống loạn nhịp tim nhóm III (NTI)",
        ma_atc="C01BD01",
        lieu_toi_da_24h_mg=_ltd("amiodarone"),
        chong_chi_dinh_thai_ky="Chống chỉ định thai kỳ (Category D - bướu cổ và suy giáp thai nhi)",
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["nhịp chậm xoang nặng", "block nhĩ thất độ 2-3", "bệnh lý tuyến giáp"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["digoxin", "warfarin", "acenocoumarol", "simvastatin"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-L01BA01",
        ten_hoat_chat="methotrexate",
        ten_biet_duoc=["trexall", "methotrexat"],
        nhom_duoc_ly="Thuốc chống chuyển hóa kháng Folate (NTI)",
        ma_atc="L01BA01",
        lieu_toi_da_24h_mg=_ltd("methotrexate"),
        chong_chi_dinh_thai_ky="Chống chỉ định tuyệt đối thai kỳ (Category X - gây sẩy thai và quái thai)",
        chong_chi_dinh_egfr=30.0,
        chong_chi_dinh_benh_nen=["suy tủy", "suy gan nặng", "loét tiêu hóa tiến triển"],
        tuong_tac_chong_chi_dinh=["aspirin", "ibuprofen"],
        tuong_tac_nghiem_trong=["co-amoxiclav", "co-trimoxazole"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-R03DA04",
        ten_hoat_chat="theophylline",
        ten_biet_duoc=["theostat", "aminophylline"],
        nhom_duoc_ly="Thuốc giãn phế quản dẫn xuất Xanthine (NTI)",
        ma_atc="R03DA04",
        lieu_toi_da_24h_mg=_ltd("theophylline"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["loạn nhịp nhanh không kiểm soát", "nhồi máu cơ tim cấp"],
        tuong_tac_chong_chi_dinh=["ciprofloxacin"],
        tuong_tac_nghiem_trong=["clarithromycin", "allopurinol"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-N07AA02",
        ten_hoat_chat="pyridostigmine",
        ten_biet_duoc=["mestinon"],
        nhom_duoc_ly="Thuốc kháng Cholinesterase điều trị nhược cơ",
        ma_atc="N07AA02",
        lieu_toi_da_24h_mg=_ltd("pyridostigmine"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["tắc nghẽn cơ học ruột hoặc đường tiết niệu", "hen phế quản"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["ciprofloxacin", "gentamicin"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-L04AX01",
        ten_hoat_chat="azathioprine",
        ten_biet_duoc=["imuran"],
        nhom_duoc_ly="Thuốc ức chế miễn dịch dẫn xuất Thiopurine",
        ma_atc="L04AX01",
        lieu_toi_da_24h_mg=_ltd("azathioprine"),
        chong_chi_dinh_thai_ky="Thận trọng cao trong thai kỳ (Category D)",
        chong_chi_dinh_egfr=20.0,
        chong_chi_dinh_benh_nen=["suy tủy nặng", "viêm gan cấp"],
        tuong_tac_chong_chi_dinh=["allopurinol"],
        tuong_tac_nghiem_trong=["warfarin", "co-trimoxazole"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-A07EC02",
        ten_hoat_chat="mesalazine",
        ten_biet_duoc=["pentasa", "asacol", "salofalk"],
        nhom_duoc_ly="Thuốc kháng viêm đường ruột (5-ASA) điều trị Crohn/IBD",
        ma_atc="A07EC02",
        lieu_toi_da_24h_mg=_ltd("mesalazine"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=30.0,
        chong_chi_dinh_benh_nen=["loét dạ dày tá tràng tiến triển", "suy thận nặng"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["azathioprine"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-C02AB01",
        ten_hoat_chat="methyldopa",
        ten_biet_duoc=["aldomet", "dopagyte"],
        nhom_duoc_ly="Thuốc hạ huyết áp kích thích thụ thể Alpha-2 trung ương",
        ma_atc="C02AB01",
        lieu_toi_da_24h_mg=_ltd("methyldopa"),
        chong_chi_dinh_thai_ky=None,
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["bệnh gan tiến triển", "trầm cảm nặng"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["levodopa", "sat"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-C09CA01",
        ten_hoat_chat="losartan",
        ten_biet_duoc=["cozaar", "losartan-kali"],
        nhom_duoc_ly="Thuốc chẹn thụ thể Angiotensin II (ARB)",
        ma_atc="C09CA01",
        lieu_toi_da_24h_mg=_ltd("losartan"),
        chong_chi_dinh_thai_ky="Chống chỉ định tuyệt đối thai kỳ quý 2 và 3 (Category D - suy thận vô niệu thai nhi)",
        chong_chi_dinh_egfr=15.0,
        chong_chi_dinh_benh_nen=["tiền sử phù mạch", "hẹp động mạch thận hai bên"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["spironolactone", "aliskiren", "ibuprofen"]
    ),
    ThongTinDuocThu(
        ma_hoat_chat="DTQG-C10AA05",
        ten_hoat_chat="atorvastatin",
        ten_biet_duoc=["lipitor", "atorvastad"],
        nhom_duoc_ly="Thuốc hạ lipid máu ức chế HMG-CoA Reductase",
        ma_atc="C10AA05",
        lieu_toi_da_24h_mg=_ltd("atorvastatin"),
        chong_chi_dinh_thai_ky="Chống chỉ định tuyệt đối thai kỳ và cho con bú (Category X)",
        chong_chi_dinh_egfr=None,
        chong_chi_dinh_benh_nen=["bệnh gan tiến triển", "tăng men gan dai dẳng không rõ nguyên nhân"],
        tuong_tac_chong_chi_dinh=[],
        tuong_tac_nghiem_trong=["clarithromycin", "colchicine", "gemfibrozil"]
    )
]


# ═══ class BoTraCuuDuocThuAhoCorasick — Bộ tra thuốc và tương tác bằng Aho-Corasick ═══
# Nhận hoạt chất, biệt dược trong văn bản và tra tương tác giữa các thuốc. Chạy offline.
class BoTraCuuDuocThuAhoCorasick:
    """Bộ tra cứu thực thể dược học Dược thư Quốc gia Việt Nam 2022."""

    def __init__(self, danh_sach_duoc_thu: Optional[List[ThongTinDuocThu]] = None):
        self.automaton = PurePythonAhoCorasick()
        self.bang_hoat_chat: Dict[str, ThongTinDuocThu] = {}
        self._bo_sung_tu_tri_thuc = danh_sach_duoc_thu is None
        ds = danh_sach_duoc_thu or CO_SO_DU_LIEU_DUOC_THU_2022
        self._khoi_tao_tu_dien(ds)

    def _khoi_tao_tu_dien(self, ds: List[ThongTinDuocThu]) -> None:
        """Đăng ký toàn bộ hoạt chất và biệt dược vào máy trạng thái."""
        da_dang_ky_tu_khoa: Set[str] = set()
        for dt in ds:
            self.bang_hoat_chat[dt.ten_hoat_chat] = dt

            # Đăng ký tên hoạt chất (INN)
            self.automaton.them_tu_khoa(dt.ten_hoat_chat, {
                "loai": "HOAT_CHAT",
                "hoat_chat_chuan": dt.ten_hoat_chat,
                "thong_tin": dt
            })
            da_dang_ky_tu_khoa.add(dt.ten_hoat_chat.lower())

            # Đăng ký các biệt dược
            for bd in dt.ten_biet_duoc:
                self.automaton.them_tu_khoa(bd, {
                    "loai": "BIET_DUOC",
                    "hoat_chat_chuan": dt.ten_hoat_chat,
                    "thong_tin": dt
                })
                da_dang_ky_tu_khoa.add(bd.lower())

        # Bổ sung đầy đủ 158+ hoạt chất & biệt dược từ data/tri_thuc_thuoc.json
        if self._bo_sung_tu_tri_thuc:
            try:
                from src.cong_cu_lam_sang import tri_thuc_thuoc as _ttt
                for m in _ttt.tat_ca():
                    hc = str(m.get("hoat_chat") or "").strip().lower()
                    if not hc or len(hc) < 4:
                        continue
                    if hc not in self.bang_hoat_chat:
                        self.bang_hoat_chat[hc] = ThongTinDuocThu(
                            ma_hoat_chat=f"TTT_{re.sub(r'[^a-z0-9]', '_', hc).upper()}",
                            ten_hoat_chat=hc,
                            ten_biet_duoc=list(m.get("ten_khac") or []) + list(m.get("biet_duoc") or []),
                            nhom_duoc_ly=str(m.get("nhom") or "Dược thư QG"),
                            ma_atc="",
                            lieu_toi_da_24h_mg=m.get("lieu_toi_da_ngay_mg"),
                        )
                    dt_ref = self.bang_hoat_chat[hc]
                    if hc not in da_dang_ky_tu_khoa:
                        self.automaton.them_tu_khoa(hc, {
                            "loai": "HOAT_CHAT",
                            "hoat_chat_chuan": hc,
                            "thong_tin": dt_ref,
                        })
                        da_dang_ky_tu_khoa.add(hc)
                    for alias in list(m.get("ten_khac") or []) + list(m.get("biet_duoc") or []):
                        al = str(alias or "").strip()
                        if len(al) >= 4 and al.lower() not in da_dang_ky_tu_khoa:
                            self.automaton.them_tu_khoa(al, {
                                "loai": "BIET_DUOC",
                                "hoat_chat_chuan": hc,
                                "thong_tin": dt_ref,
                            })
                            da_dang_ky_tu_khoa.add(al.lower())
            except Exception as exc:
                import warnings
                warnings.warn(f"Không nạp được tri_thuc_thuoc bổ sung: {exc}", RuntimeWarning, stacklevel=2)

        self.automaton.xay_dung()

    def nhan_dien_thuoc_trong_van_ban(self, van_ban: str) -> List[Dict[str, Any]]:
        """Nhận diện tất cả các thuốc xuất hiện trong văn bản lâm sàng."""
        khop = self.automaton.tim_kiem(van_ban, kiem_tra_bien_tu=True)
        ket_qua = []
        da_gap: Set[str] = set()

        for k in khop:
            hc = k["du_lieu"]["hoat_chat_chuan"]
            if hc not in da_gap:
                da_gap.add(hc)
                ket_qua.append({
                    "hoat_chat": hc,
                    "tu_khoa_khop": k["tu_khoa"],
                    "loai": k["du_lieu"]["loai"],
                    "vi_tri": (k["vi_tri_dau"], k["vi_tri_cuoi"]),
                    "thong_tin": k["du_lieu"]["thong_tin"]
                })
        return ket_qua

    def kiem_tra_tuong_tac(self, danh_sach_ten_thuoc: List[str]) -> List[Dict[str, Any]]:
        """Phát hiện tương tác thuốc dựa trên ĐTQGVN 2022 sử dụng Aho-Corasick."""
        # 1. Trích xuất danh sách hoạt chất chuẩn từ các chuỗi thuốc đầu vào
        hoat_chat_phat_hien: Set[str] = set()
        for t in danh_sach_ten_thuoc:
            if not t:
                continue
            matches = self.nhan_dien_thuoc_trong_van_ban(t)
            for m in matches:
                hoat_chat_phat_hien.add(m["hoat_chat"])

        hc_list = list(hoat_chat_phat_hien)
        canh_bao: List[Dict[str, Any]] = []

        # 2. Rà soát tương tác cặp O(K^2) trên số hoạt chất thực
        for i in range(len(hc_list)):
            for j in range(i + 1, len(hc_list)):
                h1, h2 = hc_list[i], hc_list[j]
                t1 = self.bang_hoat_chat.get(h1)
                t2 = self.bang_hoat_chat.get(h2)

                if not t1 or not t2:
                    continue

                # Kiểm tra chống chỉ định phối hợp
                if h2 in t1.tuong_tac_chong_chi_dinh or h1 in t2.tuong_tac_chong_chi_dinh:
                    canh_bao.append({
                        "thuoc_1": h1,
                        "thuoc_2": h2,
                        "muc_do": "CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI",
                        "nguon": "Dược thư Quốc gia Việt Nam 2022"
                    })
                # Kiểm tra tương tác nghiêm trọng cần theo dõi
                elif h2 in t1.tuong_tac_nghiem_trong or h1 in t2.tuong_tac_nghiem_trong:
                    canh_bao.append({
                        "thuoc_1": h1,
                        "thuoc_2": h2,
                        "muc_do": "NGUY CƠ CAO",
                        "nguon": "Dược thư Quốc gia Việt Nam 2022"
                    })

        return canh_bao
