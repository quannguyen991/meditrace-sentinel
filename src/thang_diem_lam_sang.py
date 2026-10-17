# -*- coding: utf-8 -*-
"""Động cơ Tính Thang điểm Nguy cơ Lâm sàng Quốc tế (Clinical Risk Scoring Engine).

Hỗ trợ tự động bóc tách thông tin từ hội thoại, bệnh sử, sinh hiệu và chỉ số sinh hóa
để tính toán 4 thang điểm phân tầng nguy cơ lâm sàng quan trọng nhất trong nội khoa:
1. CURB-65: Đánh giá mức độ nặng Viêm phổi mắc phải cộng đồng (CAP) -> Chỉ định nhập viện / ICU.
2. CHA2DS2-VASc: Đánh giá nguy cơ đột quỵ thiếu máu não ở bệnh nhân Rung nhĩ -> Chỉ định thuốc chống đông (OAC).
3. Wells Score for PE: Đánh giá xác suất tiền nghiệm Thuyên tắc mạch phổi -> Chỉ định D-dimer / CTPA.
4. Glasgow-Blatchford Score (GBS): Phân tầng nguy cơ Xuất huyết tiêu hóa trên cấp tính -> Chỉ định nội soi can thiệp.
"""

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional


@dataclass
class KetQuaThangDiem:
    ten_thang_diem: str
    diem_so: int
    phan_tang_nguy_co: str      # THAP, TRUNG_BINH, CAO, NGUY_KICH
    khuyen_cao_lam_sang: str     # Khuyến cáo xử trí / điều trị cụ thể cho bác sĩ
    chi_tiet_tieu_chi: List[str] = field(default_factory=list)


@dataclass
class BoThangDiemToanDien:
    curb65: Optional[KetQuaThangDiem] = None
    cha2ds2_vasc: Optional[KetQuaThangDiem] = None
    wells_pe: Optional[KetQuaThangDiem] = None
    glasgow_blatchford: Optional[KetQuaThangDiem] = None
    gcs: Optional[KetQuaThangDiem] = None
    qsofa: Optional[KetQuaThangDiem] = None
    nyha: Optional[KetQuaThangDiem] = None
    child_pugh: Optional[KetQuaThangDiem] = None
    bmi: Optional[KetQuaThangDiem] = None
    canh_bao_nguy_co_cao: List[str] = field(default_factory=list)


class ClinicalRiskScoringEngine:
    """Động cơ tính toán thang điểm nguy cơ lâm sàng dựa trên bằng chứng hội thoại và cận lâm sàng."""

    # --------------------------------------------------------------------------
    # 1. THANG ĐIỂM CURB-65 (VIÊM PHỔI CỘNG ĐỒNG)
    # --------------------------------------------------------------------------
    @classmethod
    def tinh_curb65(
        cls,
        tuoi: int = 0,
        y_thuc_lu_lan: bool = False,
        urea_mmol_l: Optional[float] = None,
        bun_mg_dl: Optional[float] = None,
        nhip_tho: Optional[int] = None,
        huyet_ap_tam_thu: Optional[int] = None,
        huyet_ap_tam_truong: Optional[int] = None,
        van_ban_kham: str = ""
    ) -> KetQuaThangDiem:
        """Tính điểm CURB-65 phân tầng nguy cơ viêm phổi cộng đồng."""
        diem = 0
        tieu_chi = []
        vb_lower = van_ban_kham.lower()

        # C - Confusion (Lú lẫn / Rối loạn ý thức)
        co_lu_lan = y_thuc_lu_lan or any(w in vb_lower for w in ["lú lẫn", "lơ mơ", "chậm chạp", "mê sảng", "tiếp xúc chậm"])
        if co_lu_lan:
            diem += 1
            tieu_chi.append("[+1] C: Rối loạn ý thức / lú lẫn (Confusion)")

        # U - Urea máu > 7 mmol/L hoặc BUN > 19 mg/dL
        co_urea_cao = (urea_mmol_l is not None and urea_mmol_l > 7.0) or (bun_mg_dl is not None and bun_mg_dl > 19.0)
        if co_urea_cao:
            diem += 1
            tieu_chi.append(f"[+1] U: Urea máu tăng cao ({urea_mmol_l or bun_mg_dl})")

        # R - Respiratory rate (Nhịp thở >= 30 lần/phút)
        if nhip_tho is not None and nhip_tho >= 30:
            diem += 1
            tieu_chi.append(f"[+1] R: Nhịp thở nhanh >= 30 l/p ({nhip_tho} l/p)")
        elif re.search(r"\bnhịp thở\s*(?:là|:)?\s*([3-9]\d)\b", vb_lower):
            diem += 1
            tieu_chi.append("[+1] R: Nhịp thở nhanh >= 30 l/p")

        # B - Blood pressure (Huyết áp tâm thu < 90 hoặc tâm trương <= 60 mmHg)
        tuot_ha = False
        if huyet_ap_tam_thu is not None and huyet_ap_tam_thu < 90:
            tuot_ha = True
        if huyet_ap_tam_truong is not None and huyet_ap_tam_truong <= 60:
            tuot_ha = True
        if not tuot_ha and any(w in vb_lower for w in ["tụt huyết áp", "huyết áp tụt", "huyết áp thấp"]):
            tuot_ha = True
        if tuot_ha:
            diem += 1
            tieu_chi.append("[+1] B: Tụt huyết áp (HATT < 90 hoặc HATTr <= 60 mmHg)")

        # 65 - Tuổi >= 65
        if tuoi >= 65 or re.search(r"\b(?:6[5-9]|[7-9]\d)\s*tuổi\b", vb_lower):
            diem += 1
            tieu_chi.append(f"[+1] 65: Người cao tuổi >= 65 tuổi ({tuoi} tuổi)")

        # Phân tầng nguy cơ theo tiêu chuẩn BTS (British Thoracic Society)
        if diem <= 1:
            nguy_co = "THAP"
            khuyen_cao = "Nguy cơ tử vong thấp (< 1.5%). Khuyến cáo điều trị ngoại trú an toàn tại nhà với kháng sinh đường uống."
        elif diem == 2:
            nguy_co = "TRUNG_BINH"
            khuyen_cao = "Nguy cơ tử vong trung bình (~9.2%). Khuyến cáo nhập viện điều trị nội trú ngắn hạn hoặc theo dõi sát tại khoa Cấp cứu."
        else:
            nguy_co = "CAO"
            khuyen_cao = "Nguy cơ tử vong cao (15 - 40%). Viêm phổi nặng: Bắt buộc nhập viện điều trị nội trú, đánh giá chuyển khoa Hồi sức tích cực (ICU)."

        return KetQuaThangDiem("CURB-65", diem, nguy_co, khuyen_cao, tieu_chi)

    # --------------------------------------------------------------------------
    # 2. THANG ĐIỂM CHA2DS2-VASc (NGUY CƠ ĐỘT QUỴ TRONG RUNG NHĨ)
    # --------------------------------------------------------------------------
    @classmethod
    def tinh_cha2ds2_vasc(
        cls,
        tuoi: int = 0,
        gioi_tinh: str = "nam",
        tien_su_suy_tim: bool = False,
        tien_su_tang_huyet_ap: bool = False,
        tien_su_dai_thao_duong: bool = False,
        tien_su_dot_quy_tia: bool = False,
        tien_su_benh_mach_mau: bool = False,
        van_ban_kham: str = ""
    ) -> KetQuaThangDiem:
        """Tính điểm CHA2DS2-VASc đánh giá nguy cơ thuyên tắc não trong rung nhĩ."""
        diem = 0
        tieu_chi = []
        vb_lower = van_ban_kham.lower()

        # C - Congestive Heart Failure (+1)
        if tien_su_suy_tim or "suy tim" in vb_lower:
            diem += 1
            tieu_chi.append("[+1] C: Suy tim sung huyết / giảm EF")

        # H - Hypertension (+1)
        if tien_su_tang_huyet_ap or any(w in vb_lower for w in ["tăng huyết áp", "cao huyết áp"]):
            diem += 1
            tieu_chi.append("[+1] H: Tiền sử tăng huyết áp")

        # A2 - Age >= 75 (+2)
        if tuoi >= 75:
            diem += 2
            tieu_chi.append(f"[+2] A2: Tuổi >= 75 ({tuoi} tuổi)")
        elif tuoi >= 65:
            diem += 1
            tieu_chi.append(f"[+1] A: Tuổi từ 65 đến 74 ({tuoi} tuổi)")

        # D - Diabetes mellitus (+1)
        if tien_su_dai_thao_duong or any(w in vb_lower for w in ["đái tháo đường", "tiểu đường"]):
            diem += 1
            tieu_chi.append("[+1] D: Đái tháo đường")

        # S2 - Stroke / TIA / Thromboembolism (+2)
        if tien_su_dot_quy_tia or any(w in vb_lower for w in ["đột quỵ", "tai biến", "nhồi máu não", "thiếu máu não thoáng qua", "tia"]):
            diem += 2
            tieu_chi.append("[+2] S2: Tiền sử đột quỵ / TIA / tắc mạch")

        # V - Vascular disease (+1)
        if tien_su_benh_mach_mau or any(w in vb_lower for w in ["nhồi máu cơ tim", "bệnh mạch vành", "xơ vữa động mạch", "bệnh mạch máu ngoại biên"]):
            diem += 1
            tieu_chi.append("[+1] V: Bệnh lý mạch máu (NMCT cũ, mảng xơ vữa)")

        # Sc - Sex category (Nữ giới +1)
        la_nu = "nữ" in gioi_tinh.lower() or "nu" in gioi_tinh.lower()
        if la_nu:
            diem += 1
            tieu_chi.append("[+1] Sc: Giới tính nữ")

        # Phân tầng nguy cơ theo ESC (European Society of Cardiology)
        nguong_chi_dinh = 2 if la_nu else 1
        if diem == 0 or (la_nu and diem == 1):
            nguy_co = "THAP"
            khuyen_cao = "Nguy cơ đột quỵ thấp. Không chỉ định thuốc chống đông (OAC) hoặc thuốc chống ngưng tập tiểu cầu."
        elif diem == nguong_chi_dinh:
            nguy_co = "TRUNG_BINH"
            khuyen_cao = "Nguy cơ đột quỵ trung bình. Khuyến cáo cân nhắc chỉ định thuốc chống đông đường uống thế hệ mới (NOAC/DOAC)."
        else:
            nguy_co = "CAO"
            khuyen_cao = "Nguy cơ đột quỵ CAO. CHỈ ĐỊNH BẮT BUỘC thuốc chống đông đường uống (NOAC: Rivaroxaban, Apixaban, Dabigatran hoặc Kháng vitamin K)."

        return KetQuaThangDiem("CHA2DS2-VASc", diem, nguy_co, khuyen_cao, tieu_chi)

    # --------------------------------------------------------------------------
    # 3. THANG ĐIỂM WELLS SCORE FOR PE (THUYÊN TẮC PHỔI)
    # --------------------------------------------------------------------------
    @classmethod
    def tinh_wells_pe(
        cls,
        dau_hieu_dvt: bool = False,
        pe_la_chan_doan_hang_dau: bool = True,
        nhip_tim_tren_100: bool = False,
        bat_dong_hoac_phau_thuat_gan_day: bool = False,
        tien_su_dvt_pe: bool = False,
        ho_ra_mau: bool = False,
        ung_thu_dang_dieu_tri: bool = False,
        van_ban_kham: str = ""
    ) -> KetQuaThangDiem:
        """Tính điểm Wells phân tầng xác suất thuyên tắc động mạch phổi."""
        diem = 0.0
        tieu_chi = []
        vb_lower = van_ban_kham.lower()

        if dau_hieu_dvt or any(w in vb_lower for w in ["sưng một bên chân", "sưng cẳng chân một bên", "đau bắp chân một bên", "dvt"]):
            diem += 3.0
            tieu_chi.append("[+3.0] Có triệu chứng lâm sàng của huyết khối tĩnh mạch sâu (DVT)")

        if pe_la_chan_doan_hang_dau or "thuyên tắc phổi" in vb_lower:
            diem += 3.0
            tieu_chi.append("[+3.0] Thuyên tắc phổi là chẩn đoán số 1 hoặc khả thi nhất")

        if nhip_tim_tren_100 or any(w in vb_lower for w in ["nhịp tim nhanh > 100", "mạch nhanh", "mạch > 100", "tim nhanh"]):
            diem += 1.5
            tieu_chi.append("[+1.5] Nhịp tim nhanh > 100 chu kỳ/phút")

        if bat_dong_hoac_phau_thuat_gan_day or any(w in vb_lower for w in ["bất động", "nằm liệt", "mới mổ", "phẫu thuật gần đây"]):
            diem += 1.5
            tieu_chi.append("[+1.5] Bất động >= 3 ngày hoặc phẫu thuật trong vòng 4 tuần")

        if tien_su_dvt_pe or "tiền sử thuyên tắc" in vb_lower:
            diem += 1.5
            tieu_chi.append("[+1.5] Tiền sử đã từng bị DVT hoặc thuyên tắc phổi")

        if ho_ra_mau or "ho ra máu" in vb_lower:
            diem += 1.0
            tieu_chi.append("[+1.0] Triệu chứng ho ra máu")

        if ung_thu_dang_dieu_tri or any(w in vb_lower for w in ["ung thư", "k giai đoạn", "hóa trị", "xạ trị"]):
            diem += 1.0
            tieu_chi.append("[+1.0] Bệnh lý ác tính (ung thư đang tiến triển/điều trị)")

        diem_int = round(diem, 1)
        if diem <= 4.0:
            nguy_co = "THAP"
            khuyen_cao = "Ít khả năng thuyên tắc phổi (Xác suất < 15%). Khuyến cáo làm xét nghiệm D-dimer độ nhạy cao để loại trừ, tránh chụp CT không cần thiết."
        else:
            nguy_co = "CAO"
            khuyen_cao = "XÁC SUẤT NGUY CƠ CAO (Xác suất > 40%). Chỉ định khẩn cấp chụp cắt lớp vi tính động mạch phổi có cản quang (CTPA) và cân nhắc chống đông sớm."

        return KetQuaThangDiem("Wells PE", int(diem), nguy_co, khuyen_cao, tieu_chi)

    # --------------------------------------------------------------------------
    # 4. THANG ĐIỂM GLASGOW-BLATCHFORD (XUẤT HUYẾT TIÊU HÓA TRÊN)
    # --------------------------------------------------------------------------
    @classmethod
    def tinh_glasgow_blatchford(
        cls,
        urea_mmol_l: Optional[float] = None,
        hb_g_dl: Optional[float] = None,
        gioi_tinh: str = "nam",
        huyet_ap_tam_thu: Optional[int] = None,
        nhip_tim: Optional[int] = None,
        di_ngoai_phan_den: bool = False,
        co_con_ngat: bool = False,
        tien_su_benh_gan: bool = False,
        tien_su_suy_tim: bool = False,
        van_ban_kham: str = ""
    ) -> KetQuaThangDiem:
        """Tính điểm Glasgow-Blatchford Score (GBS) cho xuất huyết tiêu hóa."""
        diem = 0
        tieu_chi = []
        vb_lower = van_ban_kham.lower()
        la_nam = not ("nữ" in gioi_tinh.lower() or "nu" in gioi_tinh.lower())

        # Urea máu
        if urea_mmol_l is not None:
            if urea_mmol_l >= 25.0:
                diem += 6
                tieu_chi.append(f"[+6] Urea máu rất cao >= 25 mmol/L ({urea_mmol_l})")
            elif urea_mmol_l >= 10.0:
                diem += 4
                tieu_chi.append(f"[+4] Urea máu cao 10 - 24.9 mmol/L ({urea_mmol_l})")
            elif urea_mmol_l >= 8.0:
                diem += 3
                tieu_chi.append(f"[+3] Urea máu 8 - 9.9 mmol/L ({urea_mmol_l})")
            elif urea_mmol_l >= 6.5:
                diem += 2
                tieu_chi.append(f"[+2] Urea máu 6.5 - 7.9 mmol/L ({urea_mmol_l})")

        # Hemoglobin
        if hb_g_dl is not None:
            if la_nam:
                if hb_g_dl < 10.0:
                    diem += 6
                    tieu_chi.append(f"[+6] Hb nam < 10.0 g/dL ({hb_g_dl})")
                elif hb_g_dl < 12.0:
                    diem += 3
                    tieu_chi.append(f"[+3] Hb nam 10 - 11.9 g/dL ({hb_g_dl})")
                elif hb_g_dl < 13.0:
                    diem += 1
                    tieu_chi.append(f"[+1] Hb nam 12 - 12.9 g/dL ({hb_g_dl})")
            else:
                if hb_g_dl < 10.0:
                    diem += 6
                    tieu_chi.append(f"[+6] Hb nữ < 10.0 g/dL ({hb_g_dl})")
                elif hb_g_dl < 12.0:
                    diem += 1
                    tieu_chi.append(f"[+1] Hb nữ 10 - 11.9 g/dL ({hb_g_dl})")

        # Huyết áp tâm thu
        if huyet_ap_tam_thu is not None:
            if huyet_ap_tam_thu < 90:
                diem += 3
                tieu_chi.append(f"[+3] Huyết áp tâm thu tụt < 90 mmHg ({huyet_ap_tam_thu})")
            elif huyet_ap_tam_thu < 100:
                diem += 2
                tieu_chi.append(f"[+2] Huyết áp tâm thu 90 - 99 mmHg ({huyet_ap_tam_thu})")
            elif huyet_ap_tam_thu < 110:
                diem += 1
                tieu_chi.append(f"[+1] Huyết áp tâm thu 100 - 109 mmHg ({huyet_ap_tam_thu})")

        # Nhịp tim
        if nhip_tim is not None and nhip_tim >= 100:
            diem += 1
            tieu_chi.append(f"[+1] Nhịp tim nhanh >= 100 l/p ({nhip_tim})")

        # Triệu chứng khác
        if di_ngoai_phan_den or any(w in vb_lower for w in ["phân đen", "đi cầu phân đen", "tiêu phân đen"]):
            diem += 1
            tieu_chi.append("[+1] Đi ngoài phân đen mùi khẳm")

        if co_con_ngat or any(w in vb_lower for w in ["ngất", "xỉu", "choáng ngất"]):
            diem += 2
            tieu_chi.append("[+2] Cơn ngất thoáng qua (Syncope)")

        if tien_su_benh_gan or any(w in vb_lower for w in ["xơ gan", "viêm gan mạn", "bệnh gan"]):
            diem += 2
            tieu_chi.append("[+2] Tiền sử bệnh gan mạn tính / xơ gan")

        if tien_su_suy_tim or "suy tim" in vb_lower:
            diem += 2
            tieu_chi.append("[+2] Tiền sử suy tim")

        if diem == 0:
            nguy_co = "THAP"
            khuyen_cao = "Nguy cơ rất thấp (tỷ lệ can thiệp nội soi < 1%). An toàn để xuất viện và điều trị theo dõi ngoại trú."
        elif diem <= 5:
            nguy_co = "TRUNG_BINH"
            khuyen_cao = "Nguy cơ trung bình. Nhập viện theo dõi, chỉ định nội soi dạ dày thực quản trong vòng 24 giờ."
        else:
            nguy_co = "CAO"
            khuyen_cao = "NGUY CƠ CAO / XUẤT HUYẾT NẶNG. Bắt buộc nhập viện khẩn cấp, thiết lập 2 đường truyền tĩnh mạch lớn, nội soi can thiệp cầm máu sớm."

        return KetQuaThangDiem("Glasgow-Blatchford", diem, nguy_co, khuyen_cao, tieu_chi)

    # --------------------------------------------------------------------------
    # 5. THANG ĐIỂM HÔN MÊ GLASGOW (GCS - GLASGOW COMA SCALE)
    # --------------------------------------------------------------------------
    @classmethod
    def tinh_gcs(
        cls,
        mat: int = 4,
        loi_noi: int = 5,
        van_dong: int = 6,
        van_ban_kham: str = ""
    ) -> KetQuaThangDiem:
        """Đo lường mức độ tri giác, hôn mê trong chấn thương sọ não và đột quỵ cấp (3 - 15 điểm)."""
        vb_lower = van_ban_kham.lower()
        tieu_chi = []

        # Tự động phát hiện từ văn bản nếu không truyền trực tiếp
        if "hôn mê sâu" in vb_lower or "mê sâu" in vb_lower:
            mat, loi_noi, van_dong = 1, 1, 1
        elif "gọi không mở mắt" in vb_lower or "kích thích đau không mở" in vb_lower:
            mat = 1
        elif "gọi mở mắt" in vb_lower:
            mat = 3
        elif "kích thích đau mở mắt" in vb_lower:
            mat = 2

        if "không nói được" in vb_lower or "không phát âm" in vb_lower:
            loi_noi = 1
        elif "úp ớ" in vb_lower or "kêu rên" in vb_lower:
            loi_noi = 2
        elif "nói lẫn lộn" in vb_lower or "lú lẫn" in vb_lower:
            loi_noi = 4

        if "mất não" in vb_lower or "duỗi cứng" in vb_lower:
            van_dong = 2
        elif "mất vỏ" in vb_lower or "co cứng" in vb_lower:
            van_dong = 3
        elif "co tay tránh đau" in vb_lower:
            van_dong = 4

        # Giới hạn giá trị chuẩn y khoa
        mat = max(1, min(4, mat))
        loi_noi = max(1, min(5, loi_noi))
        van_dong = max(1, min(6, van_dong))

        tong_diem = mat + loi_noi + van_dong
        tieu_chi.append(f"Mở mắt (E): {mat}/4 điểm")
        tieu_chi.append(f"Đáp ứng lời nói (V): {loi_noi}/5 điểm")
        tieu_chi.append(f"Đáp ứng vận động (M): {van_dong}/6 điểm")

        if tong_diem <= 8:
            nguy_co = "NGUY_KICH"
            khuyen_cao = "HÔN MÊ NẶNG (GCS <= 8 điểm). Nguy cơ tụt lưỡi và hít sặc cao. CHỈ ĐỊNH ĐẶT NỘI KHÍ QUẢN BẢO VỆ ĐƯỜNG THỞ KHẨN CẤP."
        elif tong_diem <= 12:
            nguy_co = "CAO"
            khuyen_cao = "Rối loạn tri giác mức độ vừa (GCS 9 - 12 điểm). Cần theo dõi sát tri giác mỗi 15-30 phút, chụp CT sọ não khẩn."
        else:
            nguy_co = "THAP"
            khuyen_cao = "Tri giác tỉnh táo hoặc chấn thương nhẹ (GCS 13 - 15 điểm). Tiếp tục theo dõi lâm sàng."

        return KetQuaThangDiem("Glasgow Coma Scale (GCS)", tong_diem, nguy_co, khuyen_cao, tieu_chi)

    # --------------------------------------------------------------------------
    # 6. THANG ĐIỂM qSOFA (QUICK SOFA - NHẬN DIỆN NHIỄM TRÙNG HUYẾT NẶNG)
    # --------------------------------------------------------------------------
    @classmethod
    def tinh_qsofa(
        cls,
        nhip_tho: Optional[int] = None,
        huyet_ap_tam_thu: Optional[int] = None,
        y_thuc_thay_doi: bool = False,
        van_ban_kham: str = ""
    ) -> KetQuaThangDiem:
        """Đánh giá nhanh nguy cơ nhiễm trùng huyết (Sepsis) ngoài phòng ICU (0 - 3 điểm)."""
        vb_lower = van_ban_kham.lower()
        diem = 0
        tieu_chi = []

        # 1. Nhịp thở >= 22 lần/phút
        tho_nhanh = (nhip_tho is not None and nhip_tho >= 22) or any(w in vb_lower for w in ["thở nhanh", "khó thở", "thở gấp"])
        if tho_nhanh:
            diem += 1
            tieu_chi.append(f"[+1] Nhịp thở nhanh >= 22 lần/phút ({nhip_tho or 'ghi nhận nhanh'})")

        # 2. Huyết áp tâm thu <= 100 mmHg
        ha_tut = (huyet_ap_tam_thu is not None and huyet_ap_tam_thu <= 100) or any(w in vb_lower for w in ["tụt huyết áp", "huyết áp thấp"])
        if ha_tut:
            diem += 1
            tieu_chi.append(f"[+1] Huyết áp tâm thu tụt <= 100 mmHg ({huyet_ap_tam_thu or 'tụt'})")

        # 3. Rối loạn ý thức / thay đổi tri giác (GCS < 15)
        co_roi_loan_tri_giac = y_thuc_thay_doi or any(w in vb_lower for w in ["lú lẫn", "lơ mơ", "kém tiếp xúc", "mê sảng", "ngủ gà"])
        if co_roi_loan_tri_giac:
            diem += 1
            tieu_chi.append("[+1] Thay đổi trạng thái tâm thần / tri giác (GCS < 15)")

        if diem >= 2:
            nguy_co = "NGUY_KICH"
            khuyen_cao = "NGUY CƠ SỐC NHIỄM KHUẨN HUYẾT CAO (qSOFA >= 2). Nguy cơ tử vong nội viện tăng gấp nhiều lần. Cần cấy máu, đo Lactate máu, hồi sức dịch tĩnh mạch và dùng kháng sinh phổ rộng trong vòng 1 giờ đầu (Golden Hour)."
        elif diem == 1:
            nguy_co = "TRUNG_BINH"
            khuyen_cao = "Nguy cơ nhiễm trùng mức độ vừa (qSOFA = 1). Cần theo dõi sát dấu hiệu sinh tồn và tìm ổ nhiễm trùng."
        else:
            nguy_co = "THAP"
            khuyen_cao = "Nguy cơ sốc nhiễm khuẩn thấp (qSOFA = 0). Điều trị theo phác đồ thông thường."

        return KetQuaThangDiem("qSOFA (Sepsis)", diem, nguy_co, khuyen_cao, tieu_chi)

    # --------------------------------------------------------------------------
    # 7. PHÂN ĐỘ SUY TIM THEO NYHA (NEW YORK HEART ASSOCIATION)
    # --------------------------------------------------------------------------
    @classmethod
    def tinh_nyha(
        cls,
        van_ban_kham: str = "",
        kho_tho_khi_nghi: bool = False,
        kho_tho_khi_gang_suc_nhe: bool = False,
        kho_tho_khi_gang_suc_nang: bool = False
    ) -> KetQuaThangDiem:
        """Phân độ suy tim theo mức độ gắng sức của người bệnh (Độ I - IV)."""
        vb_lower = van_ban_kham.lower()
        tieu_chi = []

        if kho_tho_khi_nghi or any(w in vb_lower for w in ["khó thở khi nằm", "khó thở khi nghỉ ngơi", "ngồi thở", "khó thở kịch phát"]):
            do = 4
            nguy_co = "NGUY_KICH"
            tieu_chi.append("Khó thở ngay cả khi nghỉ ngơi tại giường, triệu chứng tăng khi vận động nhẹ.")
            khuyen_cao = "SUY TIM NYHA ĐỘ IV (RẤT NẶNG). Bệnh nhân mất hoàn toàn khả năng gắng sức. Cần nhập viện điều trị nội trú, dùng thuốc lợi tiểu, giãn mạch và theo dõi tim mạch chặt chẽ."
        elif kho_tho_khi_gang_suc_nhe or any(w in vb_lower for w in ["đi bộ vài mét", "làm việc nhà nhẹ", "quét nhà khó thở", "tự tắm khó thở"]):
            do = 3
            nguy_co = "CAO"
            tieu_chi.append("Hạn chế đáng kể hoạt động thể lực; khó thở ngay cả khi làm việc nhẹ hàng ngày.")
            khuyen_cao = "SUY TIM NYHA ĐỘ III. Hạn chế nhiều hoạt động sinh hoạt thông thường. Cần tối ưu hóa phác đồ điều trị suy tim theo hướng dẫn ESC."
        elif kho_tho_khi_gang_suc_nang or any(w in vb_lower for w in ["leo cầu thang", "chạy bộ", "bê vác nặng", "làm việc nặng"]):
            do = 2
            nguy_co = "TRUNG_BINH"
            tieu_chi.append("Hạn chế nhẹ hoạt động thể lực; mệt và khó thở khi vận động gắng sức nhiều.")
            khuyen_cao = "SUY TIM NYHA ĐỘ II. Điều trị ngoại trú ổn định, hướng dẫn chế độ ăn giảm muối và theo dõi cân nặng hàng ngày."
        else:
            do = 1
            nguy_co = "THAP"
            tieu_chi.append("Không bị hạn chế hoạt động thể lực thông thường.")
            khuyen_cao = "SUY TIM NYHA ĐỘ I. Không hạn chế vận động. Tiếp tục duy trì phác đồ phòng ngừa biến cố tim mạch."

        return KetQuaThangDiem(f"Phân độ Suy tim NYHA (Độ {do})", do, nguy_co, khuyen_cao, tieu_chi)

    # --------------------------------------------------------------------------
    # 8. THANG ĐIỂM XƠ GAN CHILD-PUGH
    # --------------------------------------------------------------------------
    @classmethod
    def tinh_child_pugh(
        cls,
        bilirubin_umol_l: Optional[float] = None,
        albumin_g_l: Optional[float] = None,
        inr: Optional[float] = None,
        co_truong: str = "KHONG",
        benh_nao_gan: str = "KHONG"
    ) -> KetQuaThangDiem:
        """Đánh giá mức độ xơ gan và suy giảm chức năng gan (Class A, B, C - 5 đến 15 điểm)."""
        diem = 0
        tieu_chi = []

        # 1. Bilirubin (µmol/L): < 34: 1d, 34-50: 2d, > 50: 3d
        if bilirubin_umol_l is not None:
            if bilirubin_umol_l < 34:
                diem += 1
                tieu_chi.append(f"[+1] Bilirubin bình thường < 34 µmol/L ({bilirubin_umol_l})")
            elif bilirubin_umol_l <= 50:
                diem += 2
                tieu_chi.append(f"[+2] Bilirubin tăng vừa 34 - 50 µmol/L ({bilirubin_umol_l})")
            else:
                diem += 3
                tieu_chi.append(f"[+3] Bilirubin tăng nặng > 50 µmol/L ({bilirubin_umol_l})")
        else:
            diem += 1

        # 2. Albumin (g/L): > 35: 1d, 28-35: 2d, < 28: 3d
        if albumin_g_l is not None:
            if albumin_g_l > 35:
                diem += 1
                tieu_chi.append(f"[+1] Albumin máu tốt > 35 g/L ({albumin_g_l})")
            elif albumin_g_l >= 28:
                diem += 2
                tieu_chi.append(f"[+2] Albumin giảm nhẹ 28 - 35 g/L ({albumin_g_l})")
            else:
                diem += 3
                tieu_chi.append(f"[+3] Albumin giảm nặng < 28 g/L ({albumin_g_l})")
        else:
            diem += 1

        # 3. INR: < 1.7: 1d, 1.7-2.3: 2d, > 2.3: 3d
        if inr is not None:
            if inr < 1.7:
                diem += 1
                tieu_chi.append(f"[+1] INR < 1.7 ({inr})")
            elif inr <= 2.3:
                diem += 2
                tieu_chi.append(f"[+2] INR 1.7 - 2.3 ({inr})")
            else:
                diem += 3
                tieu_chi.append(f"[+3] INR > 2.3 ({inr})")
        else:
            diem += 1

        # 4. Cổ trướng (Báng bụng)
        co_truong_upper = co_truong.upper()
        if co_truong_upper in ["NHIEU", "NANG"]:
            diem += 3
            tieu_chi.append("[+3] Cổ trướng mức độ nhiều (căng)")
        elif co_truong_upper in ["IT", "VUA"]:
            diem += 2
            tieu_chi.append("[+2] Cổ trướng lượng ít/vừa")
        else:
            diem += 1
            tieu_chi.append("[+1] Không có cổ trướng")

        # 5. Bệnh não gan (Hôn mê gan)
        benh_nao_upper = benh_nao_gan.upper()
        if benh_nao_upper in ["DO_3", "DO_4", "NANG"]:
            diem += 3
            tieu_chi.append("[+3] Bệnh não gan độ 3 - 4 (tiền hôn mê / hôn mê gan)")
        elif benh_nao_upper in ["DO_1", "DO_2", "NHE"]:
            diem += 2
            tieu_chi.append("[+2] Bệnh não gan độ 1 - 2 (lú lẫn, run vỗ cánh)")
        else:
            diem += 1
            tieu_chi.append("[+1] Không có bệnh não gan")

        if diem <= 6:
            phan_hang = "Class A"
            nguy_co = "THAP"
            khuyen_cao = "XƠ GAN CHILD-PUGH CLASS A (5 - 6 điểm). Chức năng gan còn bù tốt. Tiên lượng sống sau 1 năm đạt 100%. Theo dõi ngoại trú định kỳ."
        elif diem <= 9:
            phan_hang = "Class B"
            nguy_co = "TRUNG_BINH"
            khuyen_cao = "XƠ GAN CHILD-PUGH CLASS B (7 - 9 điểm). Chức năng gan tổn thương mất bù mức độ vừa. Cần cân nhắc chỉ định ghép gan."
        else:
            phan_hang = "Class C"
            nguy_co = "CAO"
            khuyen_cao = "XƠ GAN CHILD-PUGH CLASS C (10 - 15 điểm). Gan suy giảm chức năng nghiêm trọng. Tiên lượng nặng, nguy cơ biến chứng xuất huyết vỡ giãn tĩnh mạch và hôn mê gan cao."

        return KetQuaThangDiem(f"Child-Pugh ({phan_hang})", diem, nguy_co, khuyen_cao, tieu_chi)

    # --------------------------------------------------------------------------
    # 9. CHỈ SỐ KHỐI CƠ THỂ BMI (CHUẨN CHÂU Á - WPRO)
    # --------------------------------------------------------------------------
    @classmethod
    def tinh_bmi(
        cls,
        can_nang_kg: float,
        chieu_cao_cm: float
    ) -> KetQuaThangDiem:
        """Tính chỉ số khối cơ thể (BMI) theo chuẩn dành cho người Châu Á (WPRO)."""
        if chieu_cao_cm <= 0 or can_nang_kg <= 0:
            return KetQuaThangDiem("BMI (Châu Á)", 0, "KHONG_XAC_DINH", "Thiếu chiều cao hoặc cân nặng", [])

        chieu_cao_m = chieu_cao_cm / 100.0
        bmi = round(can_nang_kg / (chieu_cao_m * chieu_cao_m), 1)
        tieu_chi = [f"Cân nặng: {can_nang_kg} kg", f"Chiều cao: {chieu_cao_cm} cm", f"Chỉ số BMI: {bmi} kg/m²"]

        if bmi < 18.5:
            phan_loai = "GẦY (Thiếu năng lượng trường diễn)"
            nguy_co = "THAP"
            khuyen_cao = f"BMI = {bmi} kg/m² (< 18.5). Thể trạng gầy, cần bổ sung dinh dưỡng, tầm soát suy mòn hoặc bệnh mạn tính."
        elif bmi <= 22.9:
            phan_loai = "BÌNH THƯỜNG"
            nguy_co = "THAP"
            khuyen_cao = f"BMI = {bmi} kg/m² (18.5 - 22.9). Thể trạng cân đối lý tưởng theo chuẩn người Châu Á."
        elif bmi <= 24.9:
            phan_loai = "TIỀN BÉO PHÌ (Thừa cân)"
            nguy_co = "TRUNG_BINH"
            khuyen_cao = f"BMI = {bmi} kg/m² (23.0 - 24.9). Thừa cân, có nguy cơ tim mạch và rối loạn chuyển hóa. Cần điều chỉnh chế độ ăn và tập luyện thể dục."
        elif bmi <= 29.9:
            phan_loai = "BÉO PHÌ ĐỘ I"
            nguy_co = "CAO"
            khuyen_cao = f"BMI = {bmi} kg/m² (25.0 - 29.9). Béo phì độ I. Nguy cơ cao mắc đái tháo đường, tăng huyết áp, gan nhiễm mỡ. Cần can thiệp giảm cân tích cực."
        else:
            phan_loai = "BÉO PHÌ ĐỘ II (Béo phì nặng)"
            nguy_co = "NGUY_KICH"
            khuyen_cao = f"BMI = {bmi} kg/m² (>= 30.0). Béo phì mức độ nặng. Nguy cơ rất cao xảy ra biến cố tim mạch và hội chứng ngưng thở khi ngủ."

        return KetQuaThangDiem(f"Chỉ số thể trạng BMI ({phan_loai})", int(bmi), nguy_co, khuyen_cao, tieu_chi)
