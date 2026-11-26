# -*- coding: utf-8 -*-
"""Kien truc Guardrails da tang cho duong ong MediTrace Sentinel.

Dap ung truc tiep yeu cau cua Ban Giam khao:
"Giua cac buoc, vi du nhu boc tach thong tin tu am thanh, gom chu the, hoi thoai,
can co cac quy trinh de kiem tra / guardrails nham han che rui ro trong viec nhan dien sai."

Kien truc gom 5 Guardrail doc lap:
  1. ASRQualityGuardrail: Kiem tra chat luong nhan dang giong noi va doi soat am vi duoc thu.
  2. SpeakerConsistencyGuardrail: Kiem tra nhat quan giua vai nguoi noi va dai tu xung ho tieng Viet.
  3. DialogueActGuardrail: Kiem tra hanh vi thoai (tu sua loi, phu dinh phuc tap, cau gia dinh/tuong lai).
  4. EvidenceIntegrityGuardrail: Kiem tra chong bia dat thong tin (Hallucination Zero-Tolerance).
  5. ClinicalSafetyGuardrail: Thuc thi triet ly "Bat nham con hon bo sot" (Fail-safe Asymmetric Routing).
"""

from dataclasses import dataclass, field
import difflib
import re
import unicodedata
from typing import Any, Dict, List, Optional, Set, Tuple

# Danh muc hoat chat & thuoc thuong gap theo Duoc thu Quoc gia Viet Nam
DUOC_THU_QUOC_GIA: Set[str] = {
    "paracetamol", "panadol", "hapacol", "efferalgan",
    "amoxicillin", "clavulanic", "augmentin", "ibuprofen",
    "aspirin", "clopidogrel", "plavix", "atorvastatin", "lipitor", "rosuvastatin", "crestor",
    "amlodipin", "amlodipine", "losartan", "cozaar", "enalapril", "captopril",
    "metformin", "glucophage", "gliclazide", "insulin",
    "omeprazol", "omeprazole", "losec", "esomeprazol", "esomeprazole", "pantoprazol", "pantoprazole",
    "ranitidine", "berberin", "spironolacton", "spironolactone", "amiodaron", "amiodarone", "cordarone",
    "ceftriaxone", "cefuroxime", "ciprofloxacin", "levofloxacin", "azithromycin",
    "erythromycin", "clarithromycin", "gentamicin", "vancomycin", "warfarin", "coumadin",
    "acenocoumarol", "sintrom", "heparin", "enoxaparin", "digoxin", "theophylline", "salbutamol",
    "budesonide", "prednisolone", "methylprednisolone", "dexamethasone",
    "cetirizine", "loratadine", "fexofenadine", "carbamazepine", "valproat",
    "phenytoin", "diazepam", "sertraline", "fluoxetine"
}

# Bang am vi Viet hoa hay gap khi nguoi benh doc ten thuoc / ASR nghe nham
AM_VI_THUOC = {
    "a mô xi lin": "amoxicillin", "a móc": "amoxicillin", "amox": "amoxicillin",
    "pha ra xê ta mon": "paracetamol", "pa na đôn": "paracetamol", "ha pa côn": "paracetamol",
    "óp me pra zôn": "omeprazole", "ô mê": "omeprazole",
    "am lô đi pin": "amlodipin", "am lo": "amlodipin",
    "met pho min": "metformin",
    "o re xon": "oresol", "ô rê son": "oresol",
    "xút bô": "salbutamol", "xan bu ta mon": "salbutamol",
    "oát pha rin": "warfarin", "oa pharin": "warfarin",
}


@dataclass
class GuardrailResult:
    hop_le: bool
    canh_bao: List[str] = field(default_factory=list)
    goi_y: Dict[str, Any] = field(default_factory=dict)
    chi_tiet: str = ""
    goi_y_thuoc: Dict[str, str] = field(default_factory=dict)
    goi_y_phuong_ngu: Dict[str, str] = field(default_factory=dict)


# Biến âm vùng miền 3 miền phổ biến trong hội thoại y khoa (l/n, tr/ch, s/x, hỏi/ngã)
BIEN_AM_VUNG_MIEN: Dict[str, str] = {
    "xốt": "sốt",
    "xưng": "sưng",
    "xuyễn": "suyễn",
    "xỏi": "sỏi",
    "chĩ": "trĩ",
    "chàn dịch": "tràn dịch",
    "tróng mặt": "chóng mặt",
    "tỉnh mạch": "tĩnh mạch",
    "lên cơn": "lên cơn",
    "nên cơn": "lên cơn",
    "lôn": "nôn",
    "lôn mửa": "nôn mửa",
    "lặng ngực": "nặng ngực",
    "khó thỡ": "khó thở",
    "mệt mõi": "mệt mỏi",
    "đau nhứt": "đau nhức",
    "tê bĩ": "tê bì",
}


def tao_khoa_am_vi_vung_mien(van_ban: str) -> str:
    """Chuẩn hóa biến âm vùng miền 3 miền (l/n -> n, tr/ch -> ch, s/x -> s, thanh ngã -> thanh hỏi)."""
    s = unicodedata.normalize("NFD", (van_ban or "").lower().strip())
    # Đồng nhất thanh ngã (\u0303) và thanh hỏi (\u0309)
    s = s.replace("\u0303", "\u0309")
    s = unicodedata.normalize("NFC", s)
    # Đồng nhất phụ âm đầu theo từ: l/n -> n, tr/ch -> ch, s/x -> s
    tu_moi: List[str] = []
    for w in s.split():
        if w.startswith("tr"):
            w = "ch" + w[2:]
        elif w.startswith("l"):
            w = "n" + w[1:]
        elif w.startswith("x"):
            w = "s" + w[1:]
        tu_moi.append(w)
    return " ".join(tu_moi)


# ==============================================================================
# GUARDRAIL 1: ASR & Duoc thu am vi
# ==============================================================================
class ASRQualityGuardrail:
    """Kiem soat chat luong am thanh & phien am tu ASR truoc khi dua vao rut thong tin."""

    @staticmethod
    def chuan_hoa_bien_am_vung_mien(van_ban: str) -> Dict[str, Any]:
        """Phát hiện và chuẩn hóa các lỗi biến âm vùng miền 3 miền (l/n, tr/ch, s/x, hỏi/ngã)."""
        thap = (van_ban or "").lower()
        thay_the: Dict[str, str] = {}
        vb_chuan = van_ban or ""
        for bien_am, chuan in BIEN_AM_VUNG_MIEN.items():
            if bien_am == chuan:
                continue
            pat = re.compile(rf"(?<!\w){re.escape(bien_am)}(?!\w)", re.IGNORECASE)
            if pat.search(thap):
                thay_the[bien_am] = chuan
                vb_chuan = pat.sub(chuan, vb_chuan)
        return {
            "van_ban_chuan": vb_chuan,
            "thay_the": thay_the,
            "khoa_am_vi": tao_khoa_am_vi_vung_mien(vb_chuan),
        }

    @staticmethod
    def kiem_tra_phien_am(van_ban_phien_am: str) -> GuardrailResult:
        canh_bao: List[str] = []
        loi_asr: List[str] = []
        goi_y_thuoc: Dict[str, str] = {}
        goi_y_phuong_ngu: Dict[str, str] = {}
        thap = (van_ban_phien_am or "").lower().strip()

        # 1. Kiem tra do dai toi thieu va ky tu la
        if len(thap) < 3:
            return GuardrailResult(False, ["Âm thanh quá ngắn hoặc không nhận dạng được tiếng nói"], {}, "ASR_EMPTY")

        # 2. Phat hien phat am am vi dan gian cua ten thuoc de chuan hoa (tach rieng voi phuong ngu trieu chung)
        for am_vi, chuan in AM_VI_THUOC.items():
            if re.search(rf"(?<!\w){re.escape(am_vi)}(?!\w)", thap):
                msg = f"Phát hiện phát âm tên thuốc dạng âm vị dân gian: '{am_vi}' -> gợi ý '{chuan}'"
                canh_bao.append(msg)
                loi_asr.append(msg)
                goi_y_thuoc[am_vi] = chuan

        # 3. Phat hien cac chuoi nghi ngo la ASR bi lap tu hoac ao giac (hallucination loop)
        tu_lap = re.findall(r"(?<!\w)(\w+(?:\s+\w+)?)(?:[\s.,;!]+\1){3,}(?!\w)", thap)
        if tu_lap:
            msg_lap = f"Phát hiện vòng lặp âm thanh ASR bất thường: lặp từ '{tu_lap[0]}'"
            canh_bao.append(msg_lap)
            loi_asr.append(msg_lap)

        # 4. Rà soát phương ngữ & khẩu ngữ dân gian lâm sàng 3 miền + biến âm (l/n, tr/ch, s/x, hỏi/ngã)
        bien_am = ASRQualityGuardrail.chuan_hoa_bien_am_vung_mien(van_ban_phien_am)
        for tu_bien, tu_chuan in bien_am["thay_the"].items():
            if tu_bien not in goi_y_thuoc:
                goi_y_phuong_ngu[tu_bien] = tu_chuan
                canh_bao.append(f"Chuẩn hóa biến âm vùng miền: '{tu_bien}' -> '{tu_chuan}'")

        try:
            from src.phuong_ngu_lam_sang import ClinicalDialectEngine
            kq_pn = ClinicalDialectEngine.phan_tich_va_chuan_hoa(van_ban_phien_am, doi_thuat_ngu_y_khoa=False)
            for th in kq_pn.danh_sach_phat_hien:
                k_low = th.tu_goc.lower()
                if k_low not in goi_y_thuoc and k_low not in goi_y_phuong_ngu:
                    goi_y_phuong_ngu[th.tu_goc] = th.thuat_ngu_chuan
            if kq_pn.canh_bao_lam_sang:
                canh_bao.extend(kq_pn.canh_bao_lam_sang)
                loi_asr.extend(kq_pn.canh_bao_lam_sang)
        except Exception:
            pass

        goi_y = {**goi_y_thuoc, **goi_y_phuong_ngu}
        return GuardrailResult(
            hop_le=len(loi_asr) == 0,
            canh_bao=canh_bao,
            goi_y=goi_y,
            chi_tiet=f"Đã rà soát {len(thap.split())} từ.",
            goi_y_thuoc=goi_y_thuoc,
            goi_y_phuong_ngu=goi_y_phuong_ngu,
        )


# ==============================================================================
# GUARDRAIL 2: Nhat quan Nguoi noi & Chu the
# ==============================================================================
class SpeakerConsistencyGuardrail:
    """Kiem tra mâu thuan giua vai nguoi noi va dai tu xung ho tieng Viet.
    
    Ngan chan loi nghiem trong: Nhan nguoi nha lai ghi nhan thanh benh nhan va nguoc lai.
    Luu y nhi khoa: Cac cum chi benh nhi ('bé nhà em', 'con tôi', 'cháu nhà tôi'...) la hop le khi chu_the_id == 0.
    """

    TU_KHOA_NGUOI_NHA = (
        r"\bmẹ tôi\b", r"\bbố tôi\b", r"\bba tôi\b", r"\bmá tôi\b",
        r"\bchồng tôi\b", r"\bvợ tôi\b", r"\bbà tôi\b", r"\bông tôi\b",
        r"\bông nội tôi\b", r"\bbà nội tôi\b", r"\bông ngoại tôi\b", r"\bbà ngoại tôi\b",
        r"\banh trai tôi\b", r"\bchị gái tôi\b", r"\bem trai tôi\b", r"\bem gái tôi\b",
    )

    @staticmethod
    def kiem_tra_xung_ho(nguoi_noi: str, chu_the_id: int, cau_noi: str) -> GuardrailResult:
        canh_bao = []
        thap = cau_noi.lower()

        # Neu nguoi noi tu xung ke ve nguoi khac trong gia dinh ma chu_the_id van la 0 (benh nhan)
        for pat in SpeakerConsistencyGuardrail.TU_KHOA_NGUOI_NHA:
            if re.search(pat, thap):
                if chu_the_id == 0 and nguoi_noi in ("người nhà", "người bệnh", "bệnh nhân"):
                    canh_bao.append(f"Mâu thuẫn chủ thể: Câu nói chứa '{re.search(pat, thap).group()}' nhưng thông tin đang gán cho bệnh nhân chính")

        # Neu bac si dang noi ma lai duoc gan la nguoi benh phat bieu
        if nguoi_noi == "bác sĩ" and any(w in thap for w in ("tôi bị đau", "tôi uống thuốc", "tôi sốt")):
            canh_bao.append("Bác sĩ nói câu mô tả bệnh nhưng cần kiểm tra xem có phải đang nhắc lại lời bệnh nhân không")

        return GuardrailResult(
            hop_le=len(canh_bao) == 0,
            canh_bao=canh_bao,
            chi_tiet="Kiểm tra đối soát đại từ nhân xưng hoàn tất."
        )


# ==============================================================================
# GUARDRAIL 3: Hanh vi thoai & Dinh chinh (Dialogue Act Gate)
# ==============================================================================
class DialogueActGuardrail:
    """Kiem tra hanh vi dinh chinh (self-repair), phu dinh va cau gia dinh."""

    MAU_DINH_CHINH = (
        r"(?P<cu>.+?)\s+(?:à không|nhầm|nhầm rồi|à quên|đúng ra là|chính xác là)\s+(?P<moi>.+)",
        r"(?P<cu>.+?)\s+(?:không phải|ý tôi là)\s+(?P<moi>.+)"
    )

    MAU_GIA_DINH = (
        r"\bnếu\b.+?\bthì\b",
        r"\bkhi nào\b.+?\bmới\b",
        r"\bhẹn\b.+?\btái khám\b",
        r"\btrong trường hợp\b",
        r"\bgiả sử\b"
    )

    @staticmethod
    def phat_hien_dinh_chinh(cau_noi: str) -> Optional[Tuple[str, str]]:
        """Tra ve (thong_tin_cu_bi_thay_the, thong_tin_moi) neu phat hien tu sua loi."""
        thap = cau_noi.lower().strip()
        for pat in DialogueActGuardrail.MAU_DINH_CHINH:
            m = re.search(pat, thap)
            if m:
                return m.group("cu").strip(), m.group("moi").strip()
        return None

    @staticmethod
    def la_cau_gia_dinh_hoac_tuong_lai(cau_noi: str) -> bool:
        """Phat hien cau la loi dan do hoac gia dinh tuong lai, khong phai su that lam sang."""
        thap = cau_noi.lower()
        return any(re.search(pat, thap) for pat in DialogueActGuardrail.MAU_GIA_DINH)


# ==============================================================================
# GUARDRAIL 4: Khóa căn cứ & Chong bia dat (Hallucination Zero-Tolerance)
# ==============================================================================
class EvidenceIntegrityGuardrail:
    """Kiem tra doi chieu nguyen van va chong ao giac lieu/thuoc."""

    @staticmethod
    def kiem_tra_can_cu(cau_trich: str, luot_thoai_goc: str) -> GuardrailResult:
        if not cau_trich or not luot_thoai_goc:
            return GuardrailResult(False, ["Thiếu câu trích dẫn hoặc lượt thoại gốc"], {}, "EMPTY_EVIDENCE")

        trich = cau_trich.strip().lower()
        goc = luot_thoai_goc.strip().lower()

        # Exact match
        if trich in goc:
            return GuardrailResult(True, [], {}, "EXACT_MATCH")

        # Fuzzy matching nếu ASR ngắt câu hơi lệch dấu cách
        sm = difflib.SequenceMatcher(None, trich, goc)
        match = sm.find_longest_match(0, len(trich), 0, len(goc))
        ty_le = match.size / max(len(trich), 1)

        if ty_le >= 0.85:
            return GuardrailResult(True, [f"Trích dẫn khớp tương đối ({round(ty_le*100)}%)"], {}, "FUZZY_MATCH")

        return GuardrailResult(
            False,
            [f"Câu trích dẫn không tồn tại trong lượt thoại làm căn cứ: '{cau_trich}'"],
            {},
            "HALLUCINATION_DETECTED"
        )

    @staticmethod
    def kiem_tra_ao_giac_so_lieu(chuoi_trich_xuat: str, luot_thoai_goc: str) -> GuardrailResult:
        """Kiểm tra đối soát số liệu lâm sàng (Huyết áp, nhịp tim, sốt, liều dùng).
        
        Ngăn chặn lỗi nguy hiểm: AI tự bịa ra con số lâm sàng (Clinical Numerical Hallucination)
        mà người bệnh hoặc bác sĩ không hề nhắc đến trong lượt thoại.
        """
        if not chuoi_trich_xuat or not luot_thoai_goc:
            return GuardrailResult(True, [], {}, "NO_NUMBERS")

        goc = luot_thoai_goc.lower()
        # Chuẩn hóa cách nói thân nhiệt dân gian: "37 độ 5" -> "37.5"
        goc_chuan = re.sub(r"(\d+)\s*độ\s*(\d+)", r"\1.\2", goc)

        # Tìm các con số trong chuỗi kết quả (ví dụ: 140, 90, 500, 38.5, 500mg)
        cac_so = re.findall(r"\b\d+(?:[\.,]\d+)?", chuoi_trich_xuat)
        if not cac_so:
            return GuardrailResult(True, [], {}, "NO_NUMBERS")

        # Bảng từ số học tiếng Việt tương ứng
        TU_SO_TIENG_VIET = {
            "1": "một", "2": "hai", "3": "ba", "4": "bốn", "5": "năm",
            "6": "sáu", "7": "bảy", "8": "tám", "9": "chín", "10": "mười",
            "0.5": "nửa", "1.5": "rưỡi"
        }

        so_ao_giac = []
        for s in cac_so:
            s_chuan = s.replace(",", ".")
            # Kiểm tra nếu số xuất hiện trực tiếp dưới dạng ký tự số trong thoại
            if s in goc or s_chuan in goc_chuan:
                continue
            # Kiểm tra dạng từ nói (ví dụ 2 viên -> 'hai viên')
            tu_so = TU_SO_TIENG_VIET.get(s)
            if tu_so and re.search(rf"\b{tu_so}\b", goc):
                continue
            so_ao_giac.append(s)

        if so_ao_giac:
            return GuardrailResult(
                hop_le=False,
                canh_bao=[f"Phát hiện số liệu lâm sàng '{', '.join(so_ao_giac)}' không có căn cứ trong lời thoại gốc"],
                goi_y={"so_ao_giac": so_ao_giac},
                chi_tiet="HALLUCINATION_NUMERICAL_DETECTED"
            )

        return GuardrailResult(True, [], {}, "NUMBERS_VERIFIED")

    @staticmethod
    def kiem_tra_duoc_thu_quoc_gia(ten_thuoc: str) -> GuardrailResult:
        """Đối soát tên thuốc với Dược thư Quốc gia Việt Nam và bảng âm vị chuẩn hóa."""
        t_low = (ten_thuoc or "").strip().lower()
        if not t_low:
            return GuardrailResult(False, ["Tên thuốc rỗng"], {}, "EMPTY_DRUG")

        # 1. Ưu tiên kiểm tra trực tiếp trong Dược thư Quốc gia
        for dt in DUOC_THU_QUOC_GIA:
            if dt in t_low:
                return GuardrailResult(
                    hop_le=True,
                    canh_bao=[],
                    goi_y={"hoat_chat": dt},
                    chi_tiet="PHARMACOPOEIA_VERIFIED"
                )

        # 2. Chuẩn hóa nếu là phát âm âm vị dân gian (bắt theo ranh giới từ nguyên vẹn)
        for am_vi, chuan in AM_VI_THUOC.items():
            if re.search(rf"(?<!\w){re.escape(am_vi)}(?!\w)", t_low):
                return GuardrailResult(
                    hop_le=True,
                    canh_bao=[f"Đã đối soát âm vị: '{ten_thuoc}' tương ứng hoạt chất chuẩn '{chuan}'"],
                    goi_y={"hoat_chat": chuan},
                    chi_tiet="PHARMACOPOEIA_MATCHED_ALIASED"
                )

        return GuardrailResult(
            hop_le=False,
            canh_bao=[f"Tên thuốc hoặc hoạt chất '{ten_thuoc}' chưa nằm trong Dược thư Quốc gia thường gặp - Cần bác sĩ ký duyệt"],
            goi_y={},
            chi_tiet="THUOC_NGOAI_DANH_MUC"
        )

    @staticmethod
    def kiem_tra_nguong_lieu_an_toan(hoat_chat: str, lieu_dung_mg: float) -> GuardrailResult:
        """Kiểm soát liều trần tối đa hàng ngày đối chiếu theo Dược thư Quốc gia."""
        h_low = (hoat_chat or "").strip().lower()
        
        # Bảng liều trần tối đa tham chiếu Dược thư
        # 25/11/2026: doc tu MOT nguon (data/tri_thuc_thuoc.json, chua duyet), tra theo HOAT CHAT
        # (ra soat: do chuoi con tren 114 ten khien "kháng sinh" khop "inh" -> isoniazid 300 mg).
        from src import tri_thuc_thuoc
        hc = tri_thuc_thuoc.hoat_chat(h_low)
        l = tri_thuc_thuoc.lieu_toi_da(hc, "nguoi_lon") if hc else None
        if l is not None:
            max_mg = l.gia_tri
            if lieu_dung_mg > max_mg:
                return GuardrailResult(
                    hop_le=False,
                    canh_bao=[f"CẢNH BÁO QUÁ LIỀU NGUY HIỂM: Liều {lieu_dung_mg}mg vượt liều trần an toàn "
                              f"{max_mg}mg/ngày cho {hc}" + ("" if l.da_duyet else " (ngưỡng chưa được duyệt)")],
                    goi_y={"lieu_tran_mg": max_mg, "hoat_chat": hc},
                    chi_tiet="OVERDOSE_HAZARD"
                )
            return GuardrailResult(True, [], {"lieu_tran_mg": max_mg}, "SAFE_DOSE")

        return GuardrailResult(True, [], {}, "UNKNOWN_CEILING")


# ==============================================================================
# GUARDRAIL 5: An toan lam sang "Bat nham con hon bo sot" (Fail-Safe Routing)
# ==============================================================================
class ClinicalSafetyGuardrail:
    """Thuc thi triet ly High-Recall cho cac thong tin nguy cap:
    Bat ky nghi ngo nao ve Di ung, Thuoc NTI, Chan doan deu phai giu lai va chuyen
    sang 'CAN XAC NHAN' kem co do, tuyet doi khong am tham vut bo (Zero Information Loss).
    """

    NHOM_NGUY_CAP = {"di_ung", "thuoc_nti", "thuoc", "chan_doan"}

    @staticmethod
    def dinh_tuyen_an_toan(menh_de: Dict[str, Any], danh_gia_rui_ro: Any) -> str:
        """-> "THAN_BENH_AN" | "CAN_XAC_NHAN" | "BI_CHAN_LUU_VET"
        
        Triet ly: Bat nham con hon bo sot.
        """
        loai = getattr(danh_gia_rui_ro, "loai", "khac")
        nhom = getattr(danh_gia_rui_ro, "nhom", "")
        co_canh_bao = bool(getattr(danh_gia_rui_ro, "ly_do", []))

        # 1. Thong tin nguy cap co bat ky canh bao nao -> Dua vao CAN XAC NHAN
        if loai in ClinicalSafetyGuardrail.NHOM_NGUY_CAP and co_canh_bao:
            return "CAN_XAC_NHAN"

        # 2. Bi chan tu khoa bang chung nhung la thong tin nguy cap:
        # Thay vi xoa mat tich, dua sang CAN XAC NHAN kem nhan canh bao do
        if nhom == "bị chặn":
            if loai in ClinicalSafetyGuardrail.NHOM_NGUY_CAP:
                return "CAN_XAC_NHAN"
            return "BI_CHAN_LUU_VET"

        # 3. Neu la thong tin binh thuong da kiem chung
        if not co_canh_bao:
            return "THAN_BENH_AN"

        return "CAN_XAC_NHAN" if loai in ClinicalSafetyGuardrail.NHOM_NGUY_CAP else "THAN_BENH_AN"
