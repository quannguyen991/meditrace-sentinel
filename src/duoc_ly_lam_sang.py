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
    )
]

# Liều tối đa hàng ngày (Maximum Daily Dose) cho người lớn
LIEU_TOI_DA_NGAY: Dict[str, Tuple[float, str]] = {
    "paracetamol": (4000.0, "mg"),
    "panadol": (4000.0, "mg"),
    "hapacol": (4000.0, "mg"),
    "efferalgan": (4000.0, "mg"),
    "ibuprofen": (2400.0, "mg"),
    "aspirin": (3000.0, "mg"),
    "metformin": (2550.0, "mg"),
    "amlodipin": (10.0, "mg"),
    "omeprazole": (40.0, "mg"),
    "salbutamol": (16.0, "mg")
}


class ClinicalPharmacovigilanceEngine:
    """Động cơ Dược lý Lâm sàng kiểm soát an toàn dùng thuốc toàn diện."""

    @staticmethod
    def chuan_hoa_ten_thuoc(ten: str) -> str:
        t = (ten or "").strip().lower()
        t = re.sub(r"\b(thuốc|viên|gói|uống|tiêm)\b", "", t).strip()
        return t

    @classmethod
    def kiem_tra_tuong_tac(cls, danh_sach_thuoc: List[str]) -> List[TuongTacThuoc]:
        """Phát hiện tương tác thuốc đa hoạt chất (DDI)."""
        ra: List[TuongTacThuoc] = []
        cac_thuoc = [cls.chuan_hoa_ten_thuoc(t) for t in danh_sach_thuoc if t]
        
        for i in range(len(cac_thuoc)):
            for j in range(i + 1, len(cac_thuoc)):
                t1, t2 = cac_thuoc[i], cac_thuoc[j]
                for tt in BANG_TUONG_TAC_THUOC:
                    if (tt.thuoc_1 in t1 and tt.thuoc_2 in t2) or (tt.thuoc_1 in t2 and tt.thuoc_2 in t1):
                        if tt not in ra:
                            ra.append(tt)
        return ra

    @classmethod
    def kiem_tra_co_dia_chong_chi_dinh(cls, danh_sach_thuoc: List[str], co_dia: Optional[Dict[str, Any]]) -> List[str]:
        """Kiểm tra chống chỉ định tuyệt đối theo cơ địa lâm sàng."""
        if not co_dia:
            return []
        
        canh_bao = []
        cac_thuoc = [cls.chuan_hoa_ten_thuoc(t) for t in danh_sach_thuoc if t]
        
        # 1. Suy thận nặng (eGFR < 30 ml/phút hoặc CKD stage 4-5)
        egfr = co_dia.get("egfr")
        ckd = co_dia.get("ckd_stage")
        suy_than_nang = (egfr is not None and egfr < 30) or ckd in (4, 5, "4", "5")
        
        if suy_than_nang:
            for t in cac_thuoc:
                if any(x in t for x in ("ibuprofen", "meloxicam", "diclofenac", "celecoxib", "nsaid")):
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH: Thuốc NSAID '{t}' bị cấm khi suy thận nặng (eGFR < 30) do nguy cơ suy thận cấp vô niệu")
                if "metformin" in t:
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH: Thuốc hạ đường huyết '{t}' bị cấm khi eGFR < 30 do nguy cơ nhiễm toan lactic tử vong")
                if any(x in t for x in ("gentamicin", "vancomycin")):
                    canh_bao.append(f"CẢNH BÁO CAO: Kháng sinh độc thận '{t}' cần giảm liều triệt để và định lượng nồng độ đáy")

        # 2. Phụ nữ mang thai (Thai kỳ Category X/D)
        mang_thai = co_dia.get("mang_thai") or co_dia.get("thai_ky")
        if mang_thai:
            for t in cac_thuoc:
                if any(x in t for x in ("captopril", "enalapril", "losartan", "valsartan")):
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI: Nhóm hạ áp '{t}' (ACEi/ARB) gây quái thai, suy thận và vô sọ ở thai nhi (Category D)")
                if any(x in t for x in ("atorvastatin", "rosuvastatin", "simvastatin")):
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI: Statin '{t}' chống chỉ định trong thai kỳ do nguy cơ dị tật xương (Category X)")
                if "warfarin" in t:
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI: Thuốc chống đông '{t}' gây hội chứng thai nhi Warfarin dị tật sọ mặt và xuất huyết thai")
                if "methotrexate" in t:
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI: '{t}' là thuốc độc tế bào gây sảy thai và dị tật nặng")

        # 3. Tiền sử bệnh nền đặc thù
        benh_nen = [str(b).lower() for b in co_dia.get("tien_su_benh", [])]
        if any("hen" in b for b in benh_nen):
            for t in cac_thuoc:
                if any(x in t for x in ("propranolol", "timolol", "carvedilol")):
                    canh_bao.append(f"CHỐNG CHỈ ĐỊNH: Thuốc chẹn beta '{t}' gây co thắt phế quản cấp nguy hiểm ở bệnh nhân hen suyễn")
                if any(x in t for x in ("aspirin", "ibuprofen")):
                    canh_bao.append(f"CẢNH BÁO: Bệnh nhân hen phế quản có nguy cơ co thắt phế quản nặng do NSAID/Aspirin (Hội chứng Widal)")

        if any("loét dạ dày" in b or "loét tá tràng" in b or "xuất huyết tiêu hóa" in b for b in benh_nen):
            for t in cac_thuoc:
                if any(x in t for x in ("aspirin", "ibuprofen", "diclofenac", "prednisolone")):
                    canh_bao.append(f"CẢNH BÁO CAO: Thuốc '{t}' gây kích ứng và tái phát loét/xuất huyết tiêu hóa nặng trên bệnh nhân có tiền sử bệnh dạ dày")

        return canh_bao

    @classmethod
    def kiem_tra_lieu_tran(cls, ten_thuoc: str, lieu_mg: float) -> Optional[str]:
        """Kiểm tra nếu liều thuốc vượt quá liều trần cho phép trong ngày."""
        ten = cls.chuan_hoa_ten_thuoc(ten_thuoc)
        for goc, (max_mg, don_vi) in LIEU_TOI_DA_NGAY.items():
            if goc in ten:
                if lieu_mg > max_mg:
                    return f"VƯỢT LIỀU TRẦN: Liều dùng {lieu_mg} {don_vi} vượt quá liều tối đa hàng ngày cho phép ({max_mg} {don_vi}) của '{goc}'"
        return None

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

        giai_trinh = []
        for ddi in canh_bao_ddi:
            giai_trinh.append(f"[{ddi.muc_do.upper()}] Tương tác giữa {ddi.thuoc_1} và {ddi.thuoc_2}: {ddi.hau_qua}. Khuyến cáo: {ddi.khuyen_cao}")
        for cd in chong_chi_dinh:
            giai_trinh.append(f"[CHỐNG CHỈ ĐỊNH] {cd}")
        for vl in vuot_lieu:
            giai_trinh.append(f"[QUÁ LIỀU] {vl}")

        hop_le = (len(canh_bao_ddi) == 0 and len(chong_chi_dinh) == 0 and len(vuot_lieu) == 0)

        return KetQuaKiemDuyetDuocLy(
            hop_le=hop_le,
            canh_bao_ddi=canh_bao_ddi,
            chong_chi_dinh_co_dia=chong_chi_dinh,
            vuot_lieu_tran=vuot_lieu,
            giai_trinh_duoc_ly=giai_trinh
        )
