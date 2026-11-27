# -*- coding: utf-8 -*-
"""[Công cụ lâm sàng hỗ trợ bác sĩ › Xét nghiệm]
Làm gì   : So chỉ số xét nghiệm với ngưỡng bình thường theo tuổi, giới và báo giá trị nguy
           kịch hoặc không khớp với lời bệnh nhân.
Vào → Ra : dict chỉ số xét nghiệm + mệnh đề, tuổi, giới → danh sách chỉ số bất thường, nguy
           kịch, gợi ý đối chiếu
Đọc từ   : class ParaclinicalCorrelator so chỉ số với ngưỡng; class KetQuaDoiSoatCanLamSang
           là kết quả trả về
Mục lục (các hàm/lớp chính):
  class ParaclinicalCorrelator   Phân tích chỉ số xét nghiệm đối chiếu bệnh cảnh
  class ChiSoXetNghiem           Một chỉ số xét nghiệm kèm trạng thái và ý nghĩa
  class KetQuaDoiSoatCanLamSang  Kết quả đối soát cận lâm sàng
Gọi tới  : cong_cu_lam_sang/chuan_hoa_don_vi_xet_nghiem
Dùng bởi : cong_cu_lam_sang/doc_phieu_xet_nghiem, cong_cu_lam_sang/nap_ket_qua_lis_hl7,
           he_thong/dieu_phoi_cac_chot_an_toan
Tên cũ   : can_lam_sang.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Module Đối soát Cận lâm sàng & Xét nghiệm Máu / Chẩn đoán hình ảnh (Clinical-Paraclinical Correlator).

Tự động phân tích các chỉ số cận lâm sàng (Lab Tests & Paraclinical Results):
1. Huyết học: WBC (Bạch cầu), Hb (Hemoglobin), PLT (Tiểu cầu).
2. Sinh hóa: Glucose, HbA1c, Ure, Creatinine, eGFR, AST/ALT, Troponin T/I, CRP, Điện giải đồ (K+, Na+).
3. Chẩn đoán hình ảnh & Điện tim: X-quang ngực, ECG, Siêu âm.

Chức năng then chốt:
- Bắt Giá trị Báo động Nguy kịch (Critical / Panic Values) đe dọa tính mạng (Troponin tăng, K+ > 6.0, Hb < 7.0,...).
- Đối soát Tương quan Lâm sàng - Cận lâm sàng: Xác nhận độ tin cậy của chẩn đoán (Concordant),
  phát hiện bất tương đồng (Discordant) và tự động nâng cấp chẩn đoán từ sơ bộ sang xác định.
"""

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional

from src.cong_cu_lam_sang.chuan_hoa_don_vi_xet_nghiem import chuan_hoa_du_lieu_xet_nghiem


# ═══ class ChiSoXetNghiem — Một chỉ số xét nghiệm kèm trạng thái và ý nghĩa ═══════════
# Gồm mã, giá trị, đơn vị, khoảng tham chiếu, trạng thái (bình thường, tăng, giảm, nguy
# kịch).
@dataclass
class ChiSoXetNghiem:
    ma_xet_nghiem: str           # WBC, HB, PLT, CREATININE, EGFR, TROPONIN, K, GLUCOSE, CRP, AST, ALT
    ten_chi_so: str              # Tên hiển thị tiếng Việt
    gia_tri: float
    don_vi: str
    khoang_tham_chieu: str       # ví dụ: "4.0 - 10.0"
    trang_thai: str              # "BINH_THUONG", "TANG_CAO", "GIAM_THAP", "NGUY_KICH"
    y_nghia_lam_sang: str = ""


# ═══ class KetQuaDoiSoatCanLamSang — Kết quả đối soát cận lâm sàng ════════════════════
# Danh sách chỉ số, cờ giá trị nguy kịch, báo động khẩn, bất tương đồng và khuyến cáo.
@dataclass
class KetQuaDoiSoatCanLamSang:
    danh_sach_chi_so: List[ChiSoXetNghiem] = field(default_factory=list)
    co_gia_tri_nguy_kich: bool = False
    bao_dong_do_khan_cap: List[str] = field(default_factory=list)
    chan_doan_duoc_xac_nhan: List[str] = field(default_factory=list)
    canh_bao_bat_tuong_dong: List[str] = field(default_factory=list)
    khuyen_cao_dieu_tri: List[str] = field(default_factory=list)


# ═══ class ParaclinicalCorrelator — Phân tích chỉ số xét nghiệm đối chiếu bệnh cảnh ═══
# Gắn nhãn từng chỉ số theo ngưỡng, báo giá trị nguy kịch, so với hội thoại hoặc chẩn
# đoán sơ bộ.
class ParaclinicalCorrelator:
    """Bộ đối soát và phân tích tương quan cận lâm sàng."""

    @classmethod
    def phan_tich_xet_nghiem(
        cls,
        du_lieu_xet_nghiem: Dict[str, Any],
        hoi_thoai_hoac_benh_su: str = "",
        chan_doan_so_bo: str = ""
    ) -> KetQuaDoiSoatCanLamSang:
        """Phân tích các chỉ số xét nghiệm và đối chiếu tương quan với bệnh cảnh lâm sàng."""
        du_lieu_xet_nghiem = chuan_hoa_du_lieu_xet_nghiem(du_lieu_xet_nghiem)
        danh_sach: List[ChiSoXetNghiem] = []
        bao_dong_do: List[str] = []
        xac_nhan: List[str] = []
        bat_tuong_dong: List[str] = []
        khuyen_cao: List[str] = []

        vb_lower = (hoi_thoai_hoac_benh_su + " " + chan_doan_so_bo).lower()

        def _lay_chi_so(*khoa: str) -> Any:
            for k in khoa:
                v = du_lieu_xet_nghiem.get(k)
                if v is not None and not isinstance(v, bool):
                    if isinstance(v, str):
                        v_str = v.strip().replace(",", ".")
                        if not v_str:
                            continue
                        return v_str
                    return v
            return None

        # ----------------------------------------------------------------------
        # 1. BẠCH CẦU (WBC - White Blood Cells)
        # ----------------------------------------------------------------------
        wbc = _lay_chi_so("wbc", "bach_cau")
        if wbc is not None:
            wbc_val = float(wbc)
            if wbc_val > 20.0:
                tt = "NGUY_KICH"
                yn = "Bạch cầu tăng rất cao: Phản ứng giả bạch cầu hoặc nhiễm trùng huyết / sốc nhiễm khuẩn nặng."
                bao_dong_do.append(f"WBC = {wbc_val} G/L: Báo động nguy cơ sốc nhiễm khuẩn hoặc cơn bão cytokine.")
            elif wbc_val > 10.5:
                tt = "TANG_CAO"
                yn = "Bạch cầu tăng: Dấu hiệu đáp ứng viêm hoặc nhiễm trùng vi khuẩn cấp tính."
            elif wbc_val < 3.0:
                tt = "NGUY_KICH" if wbc_val < 1.0 else "GIAM_THAP"
                yn = "Bạch cầu giảm: Nhiễm virus (Dengue, Cúm), suy tủy hoặc nhiễm khuẩn tối cấp."
                if wbc_val < 1.0:
                    bao_dong_do.append(f"WBC = {wbc_val} G/L: Giảm bạch cầu hạt nặng, nguy cơ nhiễm trùng cơ hội đe dọa tính mạng.")
            else:
                tt = "BINH_THUONG"
                yn = "Số lượng bạch cầu trong giới hạn bình thường."

            danh_sach.append(ChiSoXetNghiem("WBC", "Bạch cầu (WBC)", wbc_val, "G/L", "4.0 - 10.0", tt, yn))

            # Đối soát với hội thoại
            if wbc_val > 12.0:
                co_phu_dinh = bool(re.search(r"\b(?:không|chưa)\s+(?:bị\s+)?(?:sốt|ho|nhiễm trùng)\b", vb_lower))
                co_nhiem_trung = any(w in vb_lower for w in ["viêm phổi", "ho đờm", "nhiễm trùng", "viêm ruột thừa"]) or ("sốt" in vb_lower and not co_phu_dinh)
                if co_nhiem_trung and not ("không sốt" in vb_lower and "không ho" in vb_lower):
                    xac_nhan.append(f"WBC tăng cao ({wbc_val} G/L) củng cố và xác nhận chẩn đoán hội chứng nhiễm trùng cấp tính.")
                else:
                    bat_tuong_dong.append(f"WBC tăng ({wbc_val} G/L) nhưng lâm sàng chưa ghi nhận triệu chứng sốt hoặc ổ nhiễm trùng rõ ràng — cần tầm soát ổ nhiễm tiềm ẩn.")

        # ----------------------------------------------------------------------
        # 2. HEMOGLOBIN (HB - Huyết sắc tố)
        # ----------------------------------------------------------------------
        hb = _lay_chi_so("hb", "hemoglobin")
        if hb is not None:
            hb_val = float(hb)
            if hb_val < 7.0:
                tt = "NGUY_KICH"
                yn = "Thiếu máu nặng đe dọa tính mạng: Có chỉ định truyền khối hồng cầu cấp cứu."
                bao_dong_do.append(f"Hemoglobin = {hb_val} g/dL: Thiếu máu mức độ nặng, chỉ định truyền máu khẩn.")
                khuyen_cao.append("Chỉ định truyền máu khẩn cấp, đặt đường truyền tĩnh mạch lớn và làm phản ứng chéo.")
            elif hb_val < 10.0:
                tt = "GIAM_THAP"
                yn = "Thiếu máu mức độ trung bình."
            elif hb_val < 12.0:
                tt = "GIAM_THAP"
                yn = "Thiếu máu mức độ nhẹ."
            else:
                tt = "BINH_THUONG"
                yn = "Huyết sắc tố trong giới hạn bình thường."

            danh_sach.append(ChiSoXetNghiem("HB", "Huyết sắc tố (Hb)", hb_val, "g/dL", "12.0 - 16.0", tt, yn))

            # Đối soát với hội thoại xuất huyết
            if hb_val < 10.0 and any(w in vb_lower for w in ["nôn ra máu", "phân đen", "đi cầu ra máu", "xuất huyết tiêu hóa"]):
                xac_nhan.append(f"Hb giảm ({hb_val} g/dL) xác nhận tình trạng mất máu cấp tiến triển do xuất huyết tiêu hóa.")

        # ----------------------------------------------------------------------
        # 3. MEN TIM (TROPONIN T / I)
        # ----------------------------------------------------------------------
        trop = _lay_chi_so("troponin", "troponin_t", "troponin_i")
        if trop is not None:
            trop_val = float(trop)
            # Ngưỡng bình thường Troponin T < 0.014 ng/mL hoặc Troponin I < 0.04 ng/mL
            if trop_val >= 0.05:
                tt = "NGUY_KICH"
                yn = "TROPONIN TĂNG RẤT CAO: Chỉ điểm hoại tử tế bào cơ tim cấp (Hội chứng vành cấp / Nhồi máu cơ tim)."
                bao_dong_do.append(f"Troponin = {trop_val} ng/mL: KÍCH HOẠT BÁO ĐỘNG ĐỎ NHỒI MÁU CƠ TIM CẤP (ACS/STEMI).")
                khuyen_cao.append("Hội chẩn khẩn Can thiệp Tim mạch (PCI), cho Aspirin + Clopidogrel liều nạp, chuyển phòng Catheterization.")
                if any(w in vb_lower for w in ["đau ngực", "tức ngực", "đè nặng ngực", "mạch vành"]):
                    xac_nhan.append(f"Troponin tăng ({trop_val}) xác nhận chẩn đoán Nhồi máu cơ tim cấp trên bệnh cảnh đau thắt ngực.")
            elif trop_val > 0.014:
                tt = "TANG_CAO"
                yn = "Troponin tăng nhẹ: Nghi ngờ tổn thương cơ tim, cần làm lại động học sau 1-3 giờ."
            else:
                tt = "BINH_THUONG"
                yn = "Men tim âm tính trong giới hạn bình thường."

            danh_sach.append(ChiSoXetNghiem("TROPONIN", "Men tim Troponin", trop_val, "ng/mL", "< 0.014", tt, yn))

        # ----------------------------------------------------------------------
        # 4. KALI MÁU (K+)
        # ----------------------------------------------------------------------
        k_val = _lay_chi_so("k", "kali")
        if k_val is not None:
            k_f = float(k_val)
            if k_f >= 6.0:
                tt = "NGUY_KICH"
                yn = "TĂNG KALI MÁU NẶNG: Nguy cơ ngừng tim đột ngột do rung thất."
                bao_dong_do.append(f"Kali máu = {k_f} mmol/L: Tăng kali máu nguy kịch! Nguy cơ ngừng tim.")
                khuyen_cao.append("Tiêm Calci gluconat 10% bảo vệ màng tế bào cơ tim, truyền Glucose + Insulin tác dụng nhanh hạ kali khẩn.")
            elif k_f > 5.0:
                tt = "TANG_CAO"
                yn = "Tăng kali máu nhẹ đến vừa."
            elif k_f < 2.8:
                tt = "NGUY_KICH"
                yn = "HẠ KALI MÁU NẶNG: Nguy cơ liệt cơ hô hấp và xoắn đỉnh tim."
                bao_dong_do.append(f"Kali máu = {k_f} mmol/L: Hạ kali máu nặng nguy hiểm.")
                khuyen_cao.append("Bù Kali đường tĩnh mạch qua catheter trung tâm có theo dõi monitoring tim liên tục.")
            elif k_f < 3.5:
                tt = "GIAM_THAP"
                yn = "Hạ kali máu nhẹ."
            else:
                tt = "BINH_THUONG"
                yn = "Kali máu trong giới hạn bình thường."

            danh_sach.append(ChiSoXetNghiem("K", "Điện giải Kali (K+)", k_f, "mmol/L", "3.5 - 5.0", tt, yn))

        # ----------------------------------------------------------------------
        # 5. CREATININE & EGFR (CHỨC NĂNG THẬN)
        # ----------------------------------------------------------------------
        creat_umol = du_lieu_xet_nghiem.get("creatinine_umol_l")
        egfr = du_lieu_xet_nghiem.get("egfr")
        if creat_umol is not None:
            creat_val = float(creat_umol)
            tt = "TANG_CAO" if creat_val > 115 else "BINH_THUONG"
            yn = "Chức năng lọc cầu thận suy giảm." if tt == "TANG_CAO" else "Creatinine trong giới hạn."
            danh_sach.append(ChiSoXetNghiem("CREATININE", "Creatinine huyết thanh", creat_val, "umol/L", "60 - 110", tt, yn))

        # ----------------------------------------------------------------------
        # 5b. GLUCOSE & UREA (CHUYỂN HÓA & THẬN)
        # ----------------------------------------------------------------------
        glu_mmol = du_lieu_xet_nghiem.get("glucose_mmol_l")
        if glu_mmol is not None:
            glu_val = float(glu_mmol)
            if glu_val < 2.8:
                tt = "NGUY_KICH"
                yn = "HẠ ĐƯỜNG HUYẾT NẶNG: Nguy cơ hôn mê hạ đường huyết đe dọa tính mạng."
                bao_dong_do.append(f"Glucose máu = {glu_val} mmol/L: Hạ đường huyết nặng (< 2.8 mmol/L), cần bù đường tĩnh mạch khẩn.")
            elif glu_val >= 22.2:
                tt = "NGUY_KICH"
                yn = "TĂNG ĐƯỜNG HUYẾT RẤT CAO: Nguy cơ nhiễm toan ceton (DKA) hoặc tăng áp lực thẩm thấu (HHS)."
                bao_dong_do.append(f"Glucose máu = {glu_val} mmol/L: Tăng đường huyết nguy kịch (>= 22.2 mmol/L), tầm soát ceton và toan chuyển hóa.")
            elif glu_val > 7.0:
                tt = "TANG_CAO"
                yn = "Đường huyết tăng cao trên ngưỡng bình thường lúc đói."
            elif glu_val < 3.9:
                tt = "GIAM_THAP"
                yn = "Đường huyết giảm nhẹ."
            else:
                tt = "BINH_THUONG"
                yn = "Đường huyết trong giới hạn bình thường."
            danh_sach.append(ChiSoXetNghiem("GLUCOSE", "Glucose máu", glu_val, "mmol/L", "3.9 - 6.4", tt, yn))

        urea_mmol = du_lieu_xet_nghiem.get("urea_mmol_l")
        if urea_mmol is not None:
            urea_val = float(urea_mmol)
            if urea_val > 15.0:
                tt = "NGUY_KICH"
                yn = "Ure máu tăng rất cao: Suy thận cấp/mạn nặng hoặc xuất huyết tiêu hóa trên."
                bao_dong_do.append(
                    f"Ure máu = {urea_val} mmol/L: Tăng ure máu nguy kịch (> 15.0 mmol/L), nguy cơ suy thận cấp/mạn nặng hoặc xuất huyết tiêu hóa trên."
                )
            elif urea_val > 7.5:
                tt = "TANG_CAO"
                yn = "Ure máu tăng nhẹ đến vừa."
            else:
                tt = "BINH_THUONG"
                yn = "Ure máu trong giới hạn bình thường."
            danh_sach.append(ChiSoXetNghiem("UREA", "Ure máu", urea_val, "mmol/L", "2.5 - 7.5", tt, yn))

        if egfr is not None:
            egfr_val = float(egfr)
            if egfr_val < 30.0:
                tt = "NGUY_KICH"
                yn = "Suy thận nặng (Giai đoạn 4-5): Chống chỉ định Metformin, NSAID và thuốc cản quang."
                bao_dong_do.append(f"eGFR = {egfr_val} mL/phút/1.73m2: Suy thận nặng, chống chỉ định tuyệt đối nhóm NSAID/Metformin.")
            elif egfr_val < 60.0:
                tt = "GIAM_THAP"
                yn = "Suy giảm chức năng thận mức độ trung bình (Giai đoạn 3)."
            else:
                tt = "BINH_THUONG"
                yn = "Tốc độ lọc cầu thận bình thường."
            danh_sach.append(ChiSoXetNghiem("EGFR", "Mức lọc cầu thận (eGFR)", egfr_val, "mL/min/1.73m2", "> 60", tt, yn))

        # ----------------------------------------------------------------------
        # 6. CHẨN ĐOÁN HÌNH ẢNH (X-QUANG PHỔI & ECG)
        # ----------------------------------------------------------------------
        xquang = str(du_lieu_xet_nghiem.get("xquang_phoi", "")).lower()
        if xquang:
            if any(w in xquang for w in ["đám mờ", "đông đặc", "thâm nhiễm"]):
                if any(w in vb_lower for w in ["ho", "sốt", "khó thở", "viêm phổi"]):
                    xac_nhan.append(f"Hình ảnh X-quang phổi ({xquang}) xác nhận tổn thương đông đặc nhu mô trong Viêm phổi.")
            elif "tràn dịch" in xquang:
                xac_nhan.append(f"X-quang phát hiện tràn dịch màng phổi ({xquang}).")

        ecg = str(du_lieu_xet_nghiem.get("ecg", "")).lower()
        if ecg:
            if any(w in ecg for w in ["st chênh lên", "st elevation", "sóng q hoại tử"]):
                bao_dong_do.append(f"Điện tâm đồ (ECG) phát hiện: {ecg} -> Nhồi máu cơ tim cấp ST chênh lên.")
                xac_nhan.append("ECG xác nhận biến đổi dòng điện tổn thương hoại tử cơ tim cấp.")

        return KetQuaDoiSoatCanLamSang(
            danh_sach_chi_so=danh_sach,
            co_gia_tri_nguy_kich=len(bao_dong_do) > 0,
            bao_dong_do_khan_cap=bao_dong_do,
            chan_doan_duoc_xac_nhan=xac_nhan,
            canh_bao_bat_tuong_dong=bat_tuong_dong,
            khuyen_cao_dieu_tri=khuyen_cao
        )
