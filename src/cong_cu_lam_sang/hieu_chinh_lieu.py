# -*- coding: utf-8 -*-
"""[Công cụ lâm sàng hỗ trợ bác sĩ › Thuốc]
Làm gì   : Gợi ý chỉnh liều thuốc theo chức năng thận (CrCl, eGFR) và bệnh gan nền của người
           bệnh.
Vào → Ra : đơn thuốc + hồ sơ người bệnh (tuổi, cân nặng, creatinin, bệnh nền) → mức suy thận
           và khuyến cáo chỉnh liều từng thuốc
Đọc từ   : kiem_tra_hieu_chinh_lieu() hàm chính; tinh_crcl() và tinh_egfr_ckd_epi_2021()
           tính chức năng thận
Mục lục (các hàm/lớp chính):
  kiem_tra_hieu_chinh_lieu()             Gợi ý chỉnh liều theo chức năng thận và gan
  tinh_crcl()                            Tính độ thanh thải creatinin theo Cockcroft-Gault
  tinh_egfr_ckd_epi_2021()               Tính eGFR người lớn theo CKD-EPI 2021
  tinh_egfr_bedside_schwartz_nhi_khoa()  Tính eGFR trẻ em theo Bedside Schwartz
  phan_do_suy_than()                     Xếp giai đoạn suy thận G1 đến G5 theo KDIGO
  chuyen_umol_sang_mg_dl()               Đổi creatinin từ µmol/L sang mg/dL
Gọi tới  : cong_cu_lam_sang/chuan_hoa_don_vi_xet_nghiem, cong_cu_lam_sang/tri_thuc_thuoc
Dùng bởi : cong_cu_lam_sang/doc_phieu_xet_nghiem, cong_cu_lam_sang/quy_dao_nhieu_lan_kham,
           he_thong/dieu_phoi_cac_chot_an_toan
Tên cũ   : hieu_chinh_lieu.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Động cơ Tự động Hiệu chỉnh Liều Thuốc theo Chức năng Thận & Gan (CDSS Pharmacokinetics).

Tích hợp công thức Cockcroft-Gault / CKD-EPI và ma trận điều chỉnh liều lâm sàng:
- Tính toán độ thanh thải Creatinine (CrCl) và phân tầng suy thận KDIGO.
- Tự động phát hiện các thuốc bài xuất qua thận cần giảm liều hoặc chống chỉ định
  (Metformin, Ciprofloxacin, Levofloxacin, Enoxaparin, DOACs, Allopurinol...).
- Rà soát chức năng gan (AST, ALT, Bilirubin) và hiệu chỉnh thuốc chuyển hóa qua gan (Paracetamol, NSAIDs, Statin).
- Tích hợp hướng dẫn tương tác Thuốc - Thực phẩm (Drug-Food Interactions).
"""

from typing import Dict, List, Optional, Any
import re

from src.cong_cu_lam_sang.chuan_hoa_don_vi_xet_nghiem import chuan_hoa_creatinine, chuan_hoa_du_lieu_xet_nghiem


# ═══ tinh_crcl() — Tính độ thanh thải creatinin theo Cockcroft-Gault ══════════════════
# Cần tuổi, cân nặng, creatinin mg/dL; thiếu dữ liệu trả 0.0; nhân 0.85 với nữ.
def tinh_crcl(
    tuoi: Optional[int],
    can_nang_kg: Optional[float],
    creatinine_mg_dl: Optional[float],
    la_nu: bool = False
) -> float:
    """Tính độ thanh thải Creatinine ước tính theo công thức Cockcroft-Gault (mL/phút).
    
    CrCl = ((140 - Tuổi) * Cân nặng) / (72 * Creatinine mg/dL) * (0.85 nếu Nữ)
    Bổ sung NoneType guards toàn diện để ngăn chặn ngoại lệ thời gian chạy khi thiếu dữ liệu.
    """
    if creatinine_mg_dl is None or can_nang_kg is None or tuoi is None:
        return 0.0
    try:
        creat_f = float(creatinine_mg_dl)
        weight_f = float(can_nang_kg)
        age_i = int(tuoi)
    except (ValueError, TypeError):
        return 0.0

    if creat_f <= 0 or weight_f <= 0 or age_i <= 0:
        return 0.0
    
    crcl = ((140 - age_i) * weight_f) / (72.0 * creat_f)
    if la_nu:
        crcl *= 0.85
    return round(crcl, 1)


# ═══ tinh_egfr_ckd_epi_2021() — Tính eGFR người lớn theo CKD-EPI 2021 ═════════════════
# Công thức không dùng yếu tố chủng tộc, cần creatinin mg/dL, tuổi, giới.
def tinh_egfr_ckd_epi_2021(
    creatinine_mg_dl: Optional[float],
    tuoi: Optional[int],
    la_nu: bool = False
) -> float:
    """Tính mức lọc cầu thận ước tính (eGFR) theo công thức KDIGO CKD-EPI 2021 (Race-Free).
    
    Khuyến cáo chính thức của KDIGO 2021 / NKF-ASN task force loại bỏ biến chủng tộc:
    eGFR = 142 * min(Scr/kappa, 1)^alpha * max(Scr/kappa, 1)^(-1.200) * 0.9938^tuoi * (1.012 nếu Nữ)
    
    Hệ số:
    - Nữ: kappa = 0.7, alpha = -0.241, hệ số giới tính = 1.012
    - Nam: kappa = 0.9, alpha = -0.302, hệ số giới tính = 1.000
    - Scr: creatinine huyết thanh (mg/dL)
    - tuoi: Tuổi bệnh nhân (năm)
    
    Ưu điểm lâm sàng: Hoàn toàn không cần Cân nặng, Chiều cao hay Chủng tộc;
    cung cấp cơ chế fallback an toàn tuyệt đối khi hồ sơ ngoại trú thiếu cân nặng/chiều cao.
    """
    if creatinine_mg_dl is None:
        return 0.0
    try:
        scr = float(creatinine_mg_dl)
        # thiếu tuổi -> không ước tính (trước đây mặc định 50 tuổi)
        if tuoi is None:
            return 0.0
        age = int(tuoi)
    except (ValueError, TypeError):
        return 0.0

    if scr <= 0 or age <= 0:
        return 0.0

    if age < 18:
        # Chốt chặn an toàn: KDIGO quy định CKD-EPI chỉ áp dụng cho người >= 18 tuổi
        return 0.0

    kappa = 0.7 if la_nu else 0.9
    alpha = -0.241 if la_nu else -0.302
    he_so_nu = 1.012 if la_nu else 1.0

    ti_le = scr / kappa
    min_val = min(ti_le, 1.0)
    max_val = max(ti_le, 1.0)

    egfr = 142.0 * (min_val ** alpha) * (max_val ** -1.200) * (0.9938 ** age) * he_so_nu
    return round(egfr, 1)


# ═══ tinh_egfr_bedside_schwartz_nhi_khoa() — Tính eGFR trẻ em theo Bedside Schwartz ═══
# Dùng 0.413 nhân chiều cao chia creatinin; thiếu chiều cao thì trả None.
def tinh_egfr_bedside_schwartz_nhi_khoa(
    creatinine_mg_dl: Optional[float],
    chieu_cao_cm: Optional[float]
) -> Optional[float]:
    """Tính mức lọc cầu thận eGFR cho trẻ em (< 18 tuổi) theo công thức Bedside Schwartz (KDIGO 2012/2021).
    
    Công thức chuẩn quốc tế nhi khoa:
    eGFR = (0.413 * chieu_cao_cm) / creatinine_mg_dl (mL/phút/1.73 m2)
    
    Quy tắc an toàn lâm sàng:
    Tuyệt đối không áp dụng công thức CKD-EPI của người lớn cho bệnh nhân dưới 18 tuổi.
    Nếu thiếu chiều cao ở trẻ em, bắt buộc trả về None kèm cảnh báo yêu cầu đo chiều cao.
    """
    if creatinine_mg_dl is None or chieu_cao_cm is None:
        return None
    try:
        scr = float(creatinine_mg_dl)
        height = float(chieu_cao_cm)
    except (ValueError, TypeError):
        return None

    if scr <= 0 or height <= 0:
        return None

    egfr = (0.413 * height) / scr
    return round(egfr, 1)


# ═══ chuyen_umol_sang_mg_dl() — Đổi creatinin từ µmol/L sang mg/dL ════════════════════
# Chia cho 88.4, làm tròn 2 số; giá trị rỗng hoặc không dương trả 0.0.
def chuyen_umol_sang_mg_dl(creatinine_umol_l: Optional[float]) -> float:
    """Chuyển đơn vị Creatinine từ umol/L sang mg/dL."""
    if creatinine_umol_l is None:
        return 0.0
    try:
        val = float(creatinine_umol_l)
        if val <= 0:
            return 0.0
        return round(val / 88.4, 2)
    except (ValueError, TypeError):
        return 0.0


# ═══ phan_do_suy_than() — Xếp giai đoạn suy thận G1 đến G5 theo KDIGO ═════════════════
# Nhận CrCl hoặc eGFR; thiếu dữ liệu trả giai đoạn chưa xác định.
def phan_do_suy_than(crcl_hoac_egfr: Optional[float]) -> Dict[str, str]:
    """Phân độ suy thận theo hướng dẫn KDIGO."""
    if crcl_hoac_egfr is None:
        return {"giai_doan": "CHUA_XAC_DINH", "mo_ta": "Chưa có dữ liệu chức năng thận", "muc_do": "KHONG_RO"}
    try:
        val = float(crcl_hoac_egfr)
    except (ValueError, TypeError):
        return {"giai_doan": "CHUA_XAC_DINH", "mo_ta": "Dữ liệu chức năng thận không hợp lệ", "muc_do": "KHONG_RO"}

    if val >= 90:
        return {"giai_doan": "G1", "mo_ta": "Chức năng thận bình thường hoặc tăng", "muc_do": "BINH_THUONG"}
    elif val >= 60:
        return {"giai_doan": "G2", "mo_ta": "Suy giảm chức năng thận nhẹ", "muc_do": "GIAM_NHE"}
    elif val >= 45:
        return {"giai_doan": "G3a", "mo_ta": "Suy giảm chức năng thận nhẹ đến trung bình", "muc_do": "GIAM_TRUNG_BINH"}
    elif val >= 30:
        return {"giai_doan": "G3b", "mo_ta": "Suy giảm chức năng thận trung bình đến nặng", "muc_do": "GIAM_VUA_NANG"}
    elif val >= 15:
        return {"giai_doan": "G4", "mo_ta": "Suy giảm chức năng thận nặng", "muc_do": "GIAM_NANG"}
    else:
        return {"giai_doan": "G5", "mo_ta": "Suy thận giai đoạn cuối (ESRD)", "muc_do": "NGUY_KICH"}


# Cơ sở tri thức hiệu chỉnh liều theo chức năng thận
QUY_TAC_THAN = [
    {
        "thuoc": "metformin",
        "chi_so": "egfr",
        "ten_chuan": "Metformin",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "CRITICAL",
        "khuyen_cao": "CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI khi CrCl/eGFR < 30 mL/phút",
        "lieu_de_xuat": "Ngừng Metformin, chuyển sang Insulin hoặc thuốc hạ đường huyết an toàn cho thận.",
        "ly_do": "Nguy cơ tích lũy thuốc gây toan chuyển hóa acid lactic đe dọa tính mạng (tỷ lệ tử vong tới 50%)."
    },
    {
        "thuoc": "metformin",
        "chi_so": "egfr",
        "ten_chuan": "Metformin",
        "dieu_kien": lambda cr: 30 <= cr < 45,
        "muc_do": "WARNING",
        "khuyen_cao": "Giảm 50% liều dùng thông thường (Tối đa 1000 mg/ngày)",
        "lieu_de_xuat": "500 mg x 1-2 lần/ngày (tối đa 1000 mg/ngày), theo dõi eGFR mỗi 3 tháng.",
        "ly_do": "Giảm độ lọc cầu thận làm chậm bài tiết Metformin qua ống thận."
    },
    {
        "thuoc": "ciprofloxacin",
        "chi_so": "crcl",
        "ten_chuan": "Ciprofloxacin",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "WARNING",
        "khuyen_cao": "Giảm 50% liều hoặc giãn khoảng cách dùng mỗi 18-24 giờ",
        "lieu_de_xuat": "250-500 mg mỗi 18-24 giờ (hoặc 50% liều thông thường).",
        "ly_do": "Thuốc thải trừ chủ yếu qua thận, tích lũy làm tăng nguy cơ co giật và độc tính gân cơ."
    },
    {
        "thuoc": "levofloxacin",
        "chi_so": "crcl",
        "ten_chuan": "Levofloxacin",
        "dieu_kien": lambda cr: 20 <= cr < 50,
        "muc_do": "WARNING",
        "khuyen_cao": "Khởi đầu 500 mg, sau đó duy trì 250 mg mỗi 24 giờ",
        "lieu_de_xuat": "Khởi đầu 500 mg, sau đó 250 mg mỗi 24 giờ (thay vì 500-750 mg mỗi 24h).",
        "ly_do": "Hơn 80% Levofloxacin đào thải nguyên dạng qua nước tiểu."
    },
    {
        "thuoc": "levofloxacin",
        "chi_so": "crcl",
        "ten_chuan": "Levofloxacin",
        "dieu_kien": lambda cr: cr < 20,
        "muc_do": "CRITICAL",
        "khuyen_cao": "Khởi đầu 500 mg, sau đó 250 mg mỗi 48 giờ",
        "lieu_de_xuat": "Khởi đầu 500 mg, sau đó 250 mg mỗi 48 giờ.",
        "ly_do": "Tích lũy kéo dài gây độc tính thần kinh trung ương và kéo dài khoảng QT."
    },
    {
        "thuoc": "enoxaparin",
        "chi_so": "crcl",
        "ten_chuan": "Enoxaparin (Lovenox)",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "CRITICAL",
        "khuyen_cao": "Giảm liều điều trị xuống 1 mg/kg mỗi 24 giờ (thay vì mỗi 12 giờ)",
        "lieu_de_xuat": "1 mg/kg tiêm dưới da mỗi 24 giờ. Liều dự phòng: 20 mg mỗi 24 giờ.",
        "ly_do": "Nguy cơ tích tụ kháng đông dẫn tới xuất huyết nội sọ hoặc xuất huyết tiêu hóa ồ ạt."
    },
    {
        "thuoc": "allopurinol",
        "chi_so": "crcl",
        "ten_chuan": "Allopurinol",
        "dieu_kien": lambda cr: 10 <= cr < 30,
        "muc_do": "WARNING",
        "khuyen_cao": "Giảm liều khởi đầu xuống 100 mg/ngày (tối đa 200 mg/ngày)",
        "lieu_de_xuat": "100 mg mỗi ngày hoặc 100 mg cách ngày.",
        "ly_do": "Chất chuyển hóa Oxypurinol tích lũy làm tăng vọt nguy cơ phản ứng da nặng (Hội chứng DRESS, Stevens-Johnson)."
    },
    {
        "thuoc": "allopurinol",
        "chi_so": "crcl",
        "ten_chuan": "Allopurinol",
        "dieu_kien": lambda cr: cr < 10,
        "muc_do": "CRITICAL",
        "khuyen_cao": "Tối đa 100 mg cách ngày hoặc chuyển sang Febuxostat",
        "lieu_de_xuat": "100 mg dùng cách ngày hoặc cân nhắc Febuxostat chuyển hóa qua gan.",
        "ly_do": "Đào thải thận gần như ngưng trệ, độc tính da và gan rất cao."
    },
    {
        "thuoc": "dabigatran",
        "chi_so": "crcl",
        "ten_chuan": "Dabigatran (Pradaxa)",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "CRITICAL",
        "khuyen_cao": "CHỐNG CHỈ ĐỊNH khi CrCl < 30 mL/phút",
        "lieu_de_xuat": "Chống chỉ định tuyệt đối. Cân nhắc chuyển sang Warfarin có chỉnh liều theo INR.",
        "ly_do": "80% Dabigatran thải qua thận. Suy thận nặng gây tăng nồng độ gấp 6 lần, nguy cơ tử vong do chảy máu."
    },
    {
        "thuoc": "rivaroxaban",
        "chi_so": "crcl",
        "ten_chuan": "Rivaroxaban (Xarelto)",
        "dieu_kien": lambda cr: 15 <= cr < 50,
        "muc_do": "WARNING",
        "khuyen_cao": "Giảm liều xuống 15 mg x 1 lần/ngày (thay vì 20 mg/ngày)",
        "lieu_de_xuat": "15 mg uống cùng bữa ăn 1 lần mỗi ngày.",
        "ly_do": "Thanh thải thận giảm 35-50%, làm tăng AUC của thuốc kháng đông."
    },
    {
        "thuoc": "spironolactone",
        "chi_so": "egfr",
        "ten_chuan": "Spironolactone",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "CRITICAL",
        "khuyen_cao": "CHỐNG CHỈ ĐỊNH hoặc THẬN TRỌNG TỐI ĐA",
        "lieu_de_xuat": "Tránh dùng nếu eGFR < 30 mL/phút hoặc Kali máu > 5.0 mmol/L.",
        "ly_do": "Nguy cơ tăng Kali máu ác tính gây block nhĩ thất và ngừng tim đột ngột."
    },
    {
        "thuoc": "methotrexate",
        "chi_so": "crcl",
        "ten_chuan": "Methotrexate",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "CRITICAL",
        "khuyen_cao": "CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI khi CrCl/eGFR < 30 mL/phút",
        "lieu_de_xuat": "Chống chỉ định. Chuyển sang liệu pháp an toàn cho thận.",
        "ly_do": "Methotrexate bài xuất 80-90% qua thận; suy thận nặng gây tích lũy nồng độ cực độc dẫn tới suy tủy toàn bộ và tử vong."
    },
    {
        "thuoc": "methotrexate",
        "chi_so": "crcl",
        "ten_chuan": "Methotrexate",
        "dieu_kien": lambda cr: 30 <= cr < 50,
        "muc_do": "WARNING",
        "khuyen_cao": "Giảm 50% liều Methotrexate tuần",
        "lieu_de_xuat": "Giảm 50% liều dùng mỗi tuần, bổ sung acid folic 5mg/tuần và theo dõi công thức máu mỗi 2 tuần.",
        "ly_do": "Giảm độ lọc cầu thận làm chậm thanh thải Methotrexate, tăng độc tính tế bào máu và gan."
    },
    {
        "thuoc": "colchicine",
        "chi_so": "crcl",
        "ten_chuan": "Colchicine",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "CRITICAL",
        "khuyen_cao": "CHỐNG CHỈ ĐỊNH khi dùng kèm thuốc ức chế CYP3A4/P-gp; giảm liều tối đa 0.5 mg/ngày",
        "lieu_de_xuat": "Tối đa 0.5 mg/ngày cho đợt Gout cấp và không lặp lại liệu trình trong vòng 14 ngày.",
        "ly_do": "Nguy cơ ngộ độc Colchicine cấp tính gây tiêu cơ vân, suy tủy và liệt thần kinh cơ đe dọa tính mạng."
    },
    {
        "thuoc": "ethambutol",
        "chi_so": "crcl",
        "ten_chuan": "Ethambutol",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "WARNING",
        "khuyen_cao": "Giãn khoảng cách dùng 15-25 mg/kg 3 lần mỗi tuần (thay vì dùng hàng ngày)",
        "lieu_de_xuat": "15-25 mg/kg uống 3 lần/tuần (thứ 2 - 4 - 6).",
        "ly_do": "Ethambutol thải trừ chủ yếu qua thận; tích lũy kéo dài gây độc tính viêm dây thần kinh thị giác giảm thị lực không hồi phục."
    },
    {
        "thuoc": "digoxin",
        "chi_so": "crcl",
        "ten_chuan": "Digoxin",
        "dieu_kien": lambda cr: cr < 50,
        "muc_do": "WARNING",
        "khuyen_cao": "Giảm 50% liều hoặc dùng cách ngày (ví dụ 0.125 mg cách ngày)",
        "lieu_de_xuat": "0.0625 - 0.125 mg mỗi ngày hoặc 0.125 mg cách ngày; theo dõi nồng độ thuốc máu định kỳ.",
        "ly_do": "Độ thanh thải Digoxin tỷ lệ thuận với CrCl; suy thận làm giảm bài tiết dẫn tới ngộ độc Digoxin gây loạn nhịp tim nguy hiểm."
    }
]

# Cơ sở tri thức theo chức năng gan
QUY_TAC_GAN = [
    {
        "thuoc": "paracetamol",
        "ten_chuan": "Paracetamol (Acetaminophen)",
        "dieu_kien": lambda ast, alt, bili: ast > 120 or alt > 120 or bili > 35,
        "muc_do": "WARNING",
        "khuyen_cao": "Giảm liều tối đa không quá 2.000 mg/ngày (tối đa 500mg mỗi 6-8 giờ)",
        "lieu_de_xuat": "500 mg mỗi 8 giờ khi sốt cao, tổng liều không quá 2.000 mg/24 giờ.",
        "ly_do": "Tế bào gan suy giảm dự trữ Glutathione, dễ chuyển hóa thành NAPQI gây hoại tử tế bào gan cấp."
    },
    {
        "thuoc": "ibuprofen",
        "ten_chuan": "NSAIDs (Ibuprofen / Diclofenac / Meloxicam)",
        "dieu_kien": lambda ast, alt, bili: ast > 200 or alt > 200 or bili > 35,
        "muc_do": "CRITICAL",
        "khuyen_cao": "CHỐNG CHỈ ĐỊNH trong suy giảm chức năng gan tiến triển hoặc xơ gan",
        "lieu_de_xuat": "Tránh toàn bộ nhóm NSAIDs. Cân nhắc Paracetamol liều thấp hoặc giảm đau bậc khác.",
        "ly_do": "Tăng nguy cơ xuất huyết tiêu hóa do giảm prothrombin và nguy cơ khởi phát Hội chứng Gan-Thận (HRS)."
    },
    {
        "thuoc": "atorvastatin",
        "ten_chuan": "Statin (Atorvastatin / Rosuvastatin)",
        "dieu_kien": lambda ast, alt, bili: ast > 120 or alt > 120,
        "muc_do": "WARNING",
        "khuyen_cao": "Tạm ngừng Statin hoặc giảm liều tối thiểu, theo dõi lại men gan sau 2-4 tuần (AST/ALT > 3x ULN)",
        "lieu_de_xuat": "Tạm ngừng dùng statin cho đến khi ALT/AST hồi phục về mức < 3 lần giới hạn bình thường.",
        "ly_do": "Statin chuyển hóa chủ yếu qua gan, tổn thương tế bào gan đang tiến triển làm tăng nguy cơ hủy hoại cơ và độc tính gan."
    },
    {
        "thuoc": "rosuvastatin",
        "ten_chuan": "Rosuvastatin (Crestor)",
        "dieu_kien": lambda ast, alt, bili: ast > 120 or alt > 120,
        "muc_do": "WARNING",
        "khuyen_cao": "Tạm ngừng Rosuvastatin hoặc giảm liều tối thiểu, theo dõi lại men gan sau 2-4 tuần (AST/ALT > 3x ULN)",
        "lieu_de_xuat": "Tạm ngừng dùng statin cho đến khi ALT/AST hồi phục về mức < 3 lần giới hạn bình thường.",
        "ly_do": "Statin làm tăng nguy cơ hủy hoại cơ và độc tính gan khi men gan vượt quá 3 lần giới hạn trên."
    }
]

# Cơ sở tri thức tương tác Thuốc - Thực phẩm (Drug-Food Interactions)
TUONG_TAC_THUC_PHAM = [
    {
        "thuoc": "ciprofloxacin",
        "ten_chuan": "Ciprofloxacin / Quinolone",
        "thuc_pham": "Sữa, phô mai, sữa chua, chế phẩm bổ sung Canxi/Sắt",
        "khuyen_cao": "Uống thuốc cách xa sữa và sản phẩm từ sữa ít nhất 2 giờ trước hoặc 4 giờ sau.",
        "ly_do": "Các ion đa hóa trị (Ca2+, Fe2+, Mg2+) tạo phức Chelate không tan, làm giảm 70-90% lượng thuốc hấp thu."
    },
    {
        "thuoc": "tetracycline",
        "ten_chuan": "Tetracycline",
        "thuc_pham": "Sữa, viên uống Sắt/Canxi",
        "khuyen_cao": "Tránh uống cùng sữa hoặc thuốc bổ máu chứa sắt. Cách nhau tối thiểu 2-3 giờ.",
        "ly_do": "Tạo phức chelate không hấp thu qua niêm mạc ruột non."
    },
    {
        # doxycycline tách riêng khỏi tetracycline (chỉ tương tác hấp thu, không hiệu chỉnh thận)
        "thuoc": "doxycycline",
        "ten_chuan": "Doxycycline",
        "thuc_pham": "Viên uống Sắt/Canxi/Magie, thuốc kháng acid",
        "khuyen_cao": "Uống cách xa chế phẩm sắt, canxi, thuốc kháng acid tối thiểu 2-3 giờ.",
        "ly_do": "Ion đa hóa trị tạo phức chelate làm giảm hấp thu doxycycline."
    },
    {
        "thuoc": "warfarin",
        "ten_chuan": "Warfarin (Coumadin)",
        "thuc_pham": "Rau xanh đậm màu (rau muống, bông cải xanh, cải xoăn, rau chân vịt)",
        "khuyen_cao": "Duy trì chế độ ăn rau xanh ổn định hàng ngày, không ăn tăng vọt đột ngột.",
        "ly_do": "Vitamin K tự nhiên trong rau xanh đậm là chất đối kháng trực tiếp cơ chế chống đông của Warfarin."
    },
    {
        "thuoc": "acenocoumarol",
        "ten_chuan": "Acenocoumarol (Sintrom)",
        "thuc_pham": "Rau xanh đậm màu giàu Vitamin K (rau muống, bông cải xanh, cải bó xôi)",
        "khuyen_cao": "Duy trì chế độ ăn rau xanh ổn định hàng ngày, không ăn tăng giảm đột ngột và tránh rượu bia.",
        "ly_do": "Vitamin K tự nhiên đối kháng trực tiếp cơ chế kháng Vitamin K của Sintrom (Acenocoumarol), làm biến động INR."
    },
    {
        "thuoc": "paracetamol",
        "ten_chuan": "Paracetamol",
        "thuc_pham": "Rượu, bia, đồ uống có cồn",
        "khuyen_cao": "Tuyệt đối không uống rượu bia trong thời gian điều trị thuốc.",
        "ly_do": "Cồn kích hoạt enzym CYP2E1 làm tăng tạo độc chất NAPQI gây suy tế bào gan cấp hoại tử."
    },
    {
        "thuoc": "metronidazole",
        "ten_chuan": "Metronidazole (Flagyl)",
        "thuc_pham": "Rượu, bia, nước uống có cồn",
        "khuyen_cao": "Kiêng tuyệt đối đồ uống có cồn trong khi uống thuốc và ít nhất 48 giờ sau liều cuối cùng.",
        "ly_do": "Gây phản ứng giống Disulfiram (Antabuse): đỏ bừng mặt, tim đập nhanh, hạ huyết áp, buồn nôn dữ dội."
    },
    {
        "thuoc": "amlodipine",
        "ten_chuan": "Amlodipine / Thuốc chẹn kênh Canxi / Statin",
        "thuc_pham": "Nước ép bưởi chùm (Grapefruit juice)",
        "khuyen_cao": "Tránh uống nước ép bưởi chùm khi đang dùng Amlodipine hoặc Simvastatin/Atorvastatin.",
        "ly_do": "Chất Furanocoumarin trong bưởi chùm ức chế enzym ruột CYP3A4, làm tăng vọt nồng độ thuốc gây tụt huyết áp nghiêm trọng."
    }
]


_BIET_DUOC_HIEU_CHINH: Dict[str, str] = {
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
    "norvasc": "amlodipine",
    "amlor": "amlodipine",
    "panadol": "paracetamol",
    "hapacol": "paracetamol",
    "efferalgan": "paracetamol",
    "advil": "ibuprofen",
    "brufen": "ibuprofen",
    "ciprobay": "ciprofloxacin",
    "lanoxin": "digoxin",
    "zyloric": "allopurinol",
    "pradaxa": "dabigatran",
    "xarelto": "rivaroxaban",
    "lovenox": "enoxaparin",
    "flagyl": "metronidazole",
    # Doxycycline KHÔNG quy về tetracycline: doxycycline thải chủ yếu qua mật/ruột,
    # không cần hiệu chỉnh theo thận, không được kế thừa cảnh báo của tetracycline.
    "vibramycin": "doxycycline",
}


# ─── _goc_thuoc() — Rút gọn tên hoạt chất bỏ chữ e cuối ───────────────────────────────
def _goc_thuoc(ten: str) -> str:
    s = (ten or "").strip().lower()
    return s[:-1] if len(s) > 5 and s.endswith("e") else s


# ─── _tap_goc_thuoc_tu_danh_sach() — Quy danh sách thuốc về tập hoạt chất gốc ─────────
# Nhận biệt dược và tên hoạt chất, trả tập tên đã rút gọn để tra bảng chỉnh liều.
def _tap_goc_thuoc_tu_danh_sach(danh_sach_thuoc: List[str]) -> set:
    from src.cong_cu_lam_sang import tri_thuc_thuoc as _ttt

    tap_goc = set()
    for raw in danh_sach_thuoc:
        s = (raw or "").strip().lower()
        if not s:
            continue
        for bd, hc_bd in _BIET_DUOC_HIEU_CHINH.items():
            if re.search(rf"(?<!\w){re.escape(bd)}(?!\w)", s):
                tap_goc.add(_goc_thuoc(hc_bd))
        hc_direct = _ttt.hoat_chat(s)
        if hc_direct:
            tap_goc.add(_goc_thuoc(hc_direct))
        for m_rx in _ttt.regex_ten_thuoc().finditer(s):
            hc_m = _ttt.hoat_chat(m_rx.group(1)) or m_rx.group(1).lower()
            tap_goc.add(_goc_thuoc(hc_m))
        for tok in re.findall(r"[a-zA-Z][\w\-]{2,}", s):
            tap_goc.add(_goc_thuoc(tok))
    return tap_goc


# ─── _lay_benh_nen_bn() — Lấy danh sách bệnh nền của người bệnh ───────────────────────
# Đọc khoá benh_nen và tien_su_benh, tách theo dấu phẩy hoặc chấm phẩy.
def _lay_benh_nen_bn(thong_tin_bn: Dict[str, Any]) -> List[str]:
    ra: List[str] = []
    for k in ("benh_nen", "tien_su_benh"):
        raw = thong_tin_bn.get(k)
        if not raw:
            continue
        if isinstance(raw, str):
            ra.extend([x.strip().lower() for x in re.split(r"[,;\n]+", raw) if x.strip()])
        elif isinstance(raw, (list, tuple, set)):
            ra.extend([str(x).strip().lower() for x in raw if x is not None and str(x).strip()])
    return ra


_TU_NU = {"nữ", "nu", "female", "f", "woman", "nữ giới", "nu gioi", "gái", "gai"}
_TU_NAM = {"nam", "male", "m", "man", "nam giới", "nam gioi", "trai"}


# ─── _doc_la_nu() — Đọc giới tính nữ từ nhiều kiểu giá trị ────────────────────────────
# So khớp nguyên từ, các giá trị mơ hồ như true hoặc 1 không suy ra là nữ.
def _doc_la_nu(gia_tri: Any) -> bool:
    """Đọc giới tính nữ theo TỪ NGUYÊN VẸN (không dùng chuỗi con: "false" không phải nữ)."""
    if isinstance(gia_tri, bool):
        return gia_tri
    if gia_tri is None:
        return False
    if isinstance(gia_tri, (int, float)):
        return bool(gia_tri)
    s = re.sub(r"\s+", " ", str(gia_tri).strip().lower())
    if s in _TU_NU:
        return True
    if s in _TU_NAM or s in {"false", "0", "true", "1", "không rõ", "khong ro", ""}:
        # "true"/"1" ở khoá gioi_tinh không nói lên giới nào -> không suy diễn là nữ
        return False
    tu = re.findall(r"\w+", s)
    return bool(tu) and tu[0] in {"nữ", "nu", "female", "f"}


_MAU_BENH_GAN = re.compile(r"(suy gan|xơ gan|bệnh gan)")
_MAU_PHU_DINH_GAN = re.compile(
    r"(?<!\w)(không|chưa|ko|k|phủ nhận|loại trừ|chưa từng|không có|không bị)(?!\w)[^,;.]*$")


# ─── _co_benh_gan_nen() — Kiểm tra có bệnh gan nền không bị phủ định ──────────────────
# Tìm suy gan, xơ gan, bệnh gan trong danh sách; bỏ qua nếu phía trước có từ phủ định.
def _co_benh_gan_nen(benh_nen_list: List[str]) -> bool:
    """Có báo cáo bệnh gan nền (suy gan/xơ gan/bệnh gan) và KHÔNG bị phủ định trong cùng mệnh đề."""
    for b in benh_nen_list:
        for m in _MAU_BENH_GAN.finditer(b):
            if not _MAU_PHU_DINH_GAN.search(b[:m.start()]):
                return True
    return False


# ─── _so_hoac_none() — Đổi giá trị sang số thực, lỗi thì trả None ─────────────────────
# Loại cả giá trị bool và NaN.
def _so_hoac_none(x: Any) -> Optional[float]:
    if x is None or isinstance(x, bool):
        return None
    try:
        v = float(str(x).strip().replace(",", ".")) if isinstance(x, str) else float(x)
    except (ValueError, TypeError):
        return None
    return v if v == v else None  # loại NaN


# ═══ kiem_tra_hieu_chinh_lieu() — Gợi ý chỉnh liều theo chức năng thận và gan ═════════
# Tính CrCl/eGFR, đối chiếu bảng thuốc; trả cảnh báo thận, gan, kali (có mức CRITICAL).
# Bảng chưa duyệt, bác sĩ quyết.
def kiem_tra_hieu_chinh_lieu(
    danh_sach_thuoc: Optional[List[str]],
    ket_qua_xet_nghiem: Optional[Dict[str, Any]] = None,
    thong_tin_benh_nhan: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Phân tích và đưa ra khuyến cáo hiệu chỉnh liều theo chức năng Thận & Gan.
    
    Tích hợp cơ chế KDIGO CKD-EPI 2021 Race-Free fallback và bảo vệ NoneType toàn diện:
    - Khi khuyết thiếu Cân nặng/Chiều cao/Chủng tộc: Tự động dùng công thức KDIGO CKD-EPI 2021
      ước tính eGFR từ Creatinine, Tuổi và Giới tính.
    - Khi có đầy đủ Cân nặng: Tính toán song song cả CrCl (Cockcroft-Gault) và eGFR (CKD-EPI 2021).
    - Bảo vệ chống mọi lỗi NoneType / TypeError khi các trường xét nghiệm hoặc thông tin bệnh nhân bị None.
    
    Args:
        danh_sach_thuoc: Danh sách tên thuốc (chuỗi văn bản hoặc tên biệt dược)
        ket_qua_xet_nghiem: Dict chứa các chỉ số xét nghiệm (creatinine, egfr, ast, alt, bilirubin...)
        thong_tin_benh_nhan: Dict chứa tuổi, cân nặng, giới tính (nu: bool)
    """
    ket_qua_xet_nghiem = chuan_hoa_du_lieu_xet_nghiem(ket_qua_xet_nghiem)
    thong_tin_benh_nhan = thong_tin_benh_nhan if isinstance(thong_tin_benh_nhan, dict) else {}
    
    # 1. Đánh giá chức năng thận
    crcl_val: Optional[float] = None
    egfr_lab_val = ket_qua_xet_nghiem.get("egfr")
    creat_val = ket_qua_xet_nghiem.get("creatinine")
    
    # Chuẩn hóa thông tin bệnh nhân an toàn trước NoneType
    # Thiếu tuổi -> KHÔNG mặc định 50: không ước tính CrCl/eGFR (đánh dấu "thieu_tuoi")
    _tuoi_f = _so_hoac_none(thong_tin_benh_nhan.get("tuoi"))
    tuoi: Optional[int] = int(_tuoi_f) if _tuoi_f is not None and _tuoi_f > 0 else None

    # Hỗ trợ đồng thời cả `can_nang_kg` lẫn `can_nang`
    can_nang_raw = (
        thong_tin_benh_nhan.get("can_nang_kg")
        if thong_tin_benh_nhan.get("can_nang_kg") is not None
        else thong_tin_benh_nhan.get("can_nang")
    )
    can_nang: Optional[float] = None
    if can_nang_raw is not None:
        try:
            can_nang_float = float(can_nang_raw)
            if can_nang_float > 0:
                can_nang = can_nang_float
        except (ValueError, TypeError):
            can_nang = None

    la_nu_raw = thong_tin_benh_nhan.get("la_nu")
    if la_nu_raw is None:
        la_nu_raw = thong_tin_benh_nhan.get("gioi_tinh", False)
    la_nu = _doc_la_nu(la_nu_raw)

    # Chuyển đổi Creatinine sang mg/dL nếu có
    creat_mg_dl: Optional[float] = ket_qua_xet_nghiem.get("creatinine_mg_dl")
    if creat_mg_dl is None and creat_val is not None:
        c_norm = chuan_hoa_creatinine(creat_val, ket_qua_xet_nghiem.get("creatinine_unit"))
        creat_mg_dl = c_norm["mg_dl"] if c_norm else None

    # Chuẩn hóa Chiều cao cho nhi khoa nếu có
    chieu_cao_raw = thong_tin_benh_nhan.get("chieu_cao_cm", thong_tin_benh_nhan.get("chieu_cao"))
    chieu_cao: Optional[float] = None
    if chieu_cao_raw is not None:
        try:
            chieu_cao_float = float(chieu_cao_raw)
            if chieu_cao_float > 0:
                chieu_cao = chieu_cao_float
        except (ValueError, TypeError):
            chieu_cao = None

    # Tính Cockcroft-Gault CrCl nếu có cân nặng (chỉ áp dụng người lớn)
    creat_mg_dl = _so_hoac_none(creat_mg_dl)
    if creat_mg_dl is not None and creat_mg_dl <= 0:
        creat_mg_dl = None
    if creat_mg_dl is not None and can_nang is not None and tuoi is not None and tuoi >= 18:
        crcl_val = tinh_crcl(tuoi, can_nang, creat_mg_dl, la_nu) or None

    # Đánh giá eGFR (KDIGO CKD-EPI 2021 race-free fallback cho người lớn, Bedside Schwartz cho nhi khoa)
    egfr_val: Optional[float] = None
    phuong_phap_uoc_tinh: str = "Chua_co_du_lieu"
    canh_bao_uoc_tinh: Optional[str] = None

    egfr_val = _so_hoac_none(egfr_lab_val)
    if egfr_val is not None:
        phuong_phap_uoc_tinh = "Ket_qua_phong_xet_nghiem"

    if egfr_val is None and creat_mg_dl is not None and tuoi is None:
        phuong_phap_uoc_tinh = "thieu_tuoi"
        canh_bao_uoc_tinh = ("Thiếu tuổi bệnh nhân: không ước tính được CrCl/eGFR từ creatinine; "
                             "cần bổ sung tuổi trước khi đánh giá hiệu chỉnh liều theo thận.")
    elif egfr_val is None and creat_mg_dl is not None:
        if tuoi < 18:
            # Chốt chặn nhi khoa (< 18 tuổi): Bắt buộc dùng Bedside Schwartz, không dùng CKD-EPI người lớn
            if chieu_cao is not None:
                egfr_val = tinh_egfr_bedside_schwartz_nhi_khoa(creat_mg_dl, chieu_cao)
                phuong_phap_uoc_tinh = "KDIGO_Bedside_Schwartz_Nhi_Khoa"
            else:
                egfr_val = None
                phuong_phap_uoc_tinh = "Nhi_Khoa_Thieu_Chieu_Cao_Bedside_Schwartz"
        else:
            # Người lớn >= 18 tuổi: Áp dụng KDIGO CKD-EPI 2021 Race-Free
            egfr_val = tinh_egfr_ckd_epi_2021(creat_mg_dl, tuoi, la_nu)
            phuong_phap_uoc_tinh = "KDIGO_CKD_EPI_2021_Race_Free"

    # Chỉ số thận chính: Ưu tiên eGFR (lab hoặc CKD-EPI 2021), kế đến CrCl
    chi_so_than_chinh = egfr_val if egfr_val is not None else crcl_val
    phan_do_than = phan_do_suy_than(chi_so_than_chinh) if chi_so_than_chinh is not None else None
    
    # 2. Đánh giá chức năng gan (NoneType safe)
    # Chỉ số chưa đo -> None (không bịa giá trị "bình thường" hay "bất thường")
    ast_raw = ket_qua_xet_nghiem.get("ast")
    if ast_raw is None:
        ast_raw = ket_qua_xet_nghiem.get("got")
    ast_val = _so_hoac_none(ast_raw)

    alt_raw = ket_qua_xet_nghiem.get("alt")
    if alt_raw is None:
        alt_raw = ket_qua_xet_nghiem.get("gpt")
    alt_val = _so_hoac_none(alt_raw)

    bili_val = _so_hoac_none(ket_qua_xet_nghiem.get("bilirubin"))

    # Giá trị để so sánh ngưỡng (chỉ số thiếu = không vượt ngưỡng)
    ast_ss = ast_val if ast_val is not None else 0.0
    alt_ss = alt_val if alt_val is not None else 0.0
    bili_ss = bili_val if bili_val is not None else 0.0

    benh_nen_list = _lay_benh_nen_bn(thong_tin_benh_nhan)
    # Có rõ ràng: bệnh gan nên ĐƯỢC BÁO CÁO (có xử lý phủ định "không suy gan")
    co_benh_gan_nen = _co_benh_gan_nen(benh_nen_list)
    gan_bat_thuong = (ast_ss > 100 or alt_ss > 100 or bili_ss > 30 or co_benh_gan_nen)

    canh_bao_than: List[Dict[str, Any]] = []
    canh_bao_gan: List[Dict[str, Any]] = []
    canh_bao_thuc_pham: List[Dict[str, Any]] = []

    # Chuẩn hóa an toàn danh sách thuốc (không phân biệt 'e' cuối & nhận diện biệt dược phổ biến)
    danh_sach_thuoc_an_toan = danh_sach_thuoc if isinstance(danh_sach_thuoc, list) else []
    thuoc_lower = [str(t).lower().strip() for t in danh_sach_thuoc_an_toan if t is not None and str(t).strip()]
    tap_goc_thuoc = _tap_goc_thuoc_tu_danh_sach(thuoc_lower)

    # Kiểm tra hiệu chỉnh thận: mỗi quy tắc dùng ĐÚNG chỉ số nó được định nghĩa
    # (CrCl Cockcroft-Gault cho dabigatran/enoxaparin/...; eGFR cho metformin/spironolactone).
    # Thiếu chỉ số đúng -> dùng chỉ số còn lại (lấy min nếu có nhiều) và gán cờ chi_so_thay_the.
    co_san = {"crcl": crcl_val or None, "egfr": egfr_val or None}
    for qt in QUY_TAC_THAN:
        if _goc_thuoc(qt["thuoc"]) not in tap_goc_thuoc:
            continue
        loai = qt.get("chi_so", "crcl")
        gia_tri = co_san.get(loai)
        thay_the = False
        if gia_tri is None:
            con_lai = [v for v in co_san.values() if v is not None]
            if not con_lai:
                continue
            gia_tri = min(con_lai)
            thay_the = True
        if qt["dieu_kien"](gia_tri):
            ten_cs = "CrCl" if loai == "crcl" else "eGFR"
            if thay_the:
                ten_cs = f"{'eGFR' if loai == 'crcl' else 'CrCl'} (thay cho {ten_cs} - chưa tính được)"
            pd = phan_do_suy_than(gia_tri)
            canh_bao_than.append({
                "thuoc": qt["ten_chuan"],
                "muc_do": qt["muc_do"],
                "chi_so_danh_gia": f"{ten_cs} = {round(gia_tri, 1)} mL/phút ({pd['giai_doan']})",
                "chi_so_dung": loai,
                "chi_so_thay_the": thay_the,
                "khuyen_cao": qt["khuyen_cao"],
                "lieu_de_xuat": qt["lieu_de_xuat"],
                "ly_do_lam_sang": qt["ly_do"]
            })

    # Kiểm tra thêm Spironolacton/Spironolactone khi Kali máu > 5.0 mmol/L
    kali_raw = ket_qua_xet_nghiem.get("kali") if ket_qua_xet_nghiem.get("kali") is not None else ket_qua_xet_nghiem.get("k")
    if kali_raw is not None and _goc_thuoc("spironolactone") in tap_goc_thuoc:
        try:
            kali_f = float(kali_raw)
            if kali_f > 5.0 and not any("Spironolacton" in c["thuoc"] for c in canh_bao_than):
                canh_bao_than.append({
                    "thuoc": "Spironolactone (Spironolacton)",
                    "muc_do": "CRITICAL" if kali_f >= 5.5 else "WARNING",
                    "chi_so_danh_gia": f"Kali máu = {kali_f} mmol/L",
                    "khuyen_cao": "CHỐNG CHỈ ĐỊNH Spironolacton khi tăng Kali máu (> 5.0 mmol/L)",
                    "lieu_de_xuat": "Ngừng Spironolacton ngay lập tức và theo dõi điện tâm đồ / điện giải đồ.",
                    "ly_do_lam_sang": "Nguy cơ tăng Kali máu ác tính gây loạn nhịp thất và ngừng tim.",
                })
        except (ValueError, TypeError):
            pass

    # Kiểm tra hiệu chỉnh gan: kích hoạt khi men gan THẬT vượt ngưỡng HOẶC có cờ
    # bệnh gan nền được báo cáo (không còn bịa AST/ALT = 210)
    def _hien(v, dv):
        return f"{v} {dv}" if v is not None else "chưa có"

    for qt in QUY_TAC_GAN:
        if _goc_thuoc(qt["thuoc"]) in tap_goc_thuoc:
            vuot_nguong = qt["dieu_kien"](ast_ss, alt_ss, bili_ss)
            if vuot_nguong or co_benh_gan_nen:
                chi_so_gan_str = (
                    f"AST={_hien(ast_val, 'U/L')}, ALT={_hien(alt_val, 'U/L')}, "
                    f"Bilirubin={_hien(bili_val, 'µmol/L')}"
                )
                if co_benh_gan_nen and not vuot_nguong:
                    chi_so_gan_str = f"Bệnh nền suy gan/xơ gan được báo cáo ({chi_so_gan_str})"
                canh_bao_gan.append({
                    "thuoc": qt["ten_chuan"],
                    "muc_do": qt["muc_do"],
                    "chi_so_danh_gia": chi_so_gan_str,
                    "khuyen_cao": qt["khuyen_cao"],
                    "lieu_de_xuat": qt["lieu_de_xuat"],
                    "ly_do_lam_sang": qt["ly_do"]
                })

    # Kiểm tra tương tác thuốc - thức ăn
    for tt in TUONG_TAC_THUC_PHAM:
        if _goc_thuoc(tt["thuoc"]) in tap_goc_thuoc:
            canh_bao_thuc_pham.append({
                "thuoc": tt["ten_chuan"],
                "thuc_pham_kieng_cu": tt["thuc_pham"],
                "huong_dan_dung": tt["khuyen_cao"],
                "co_che_duoc_ly": tt["ly_do"]
            })
            
    co_canh_bao_critical = any(c["muc_do"] == "CRITICAL" for c in canh_bao_than + canh_bao_gan)
    
    return {
        "chuc_nang_than": {
            "crcl_cockcroft_gault": crcl_val,
            "egfr_ckd_epi": egfr_val,
            "phuong_phap_uoc_tinh": phuong_phap_uoc_tinh,
            "canh_bao_uoc_tinh": canh_bao_uoc_tinh,
            "phan_do": phan_do_than
        },
        "chuc_nang_gan": {
            "ast": ast_val,
            "alt": alt_val,
            "bilirubin": bili_val,
            "benh_gan_nen": co_benh_gan_nen,
            "bat_thuong": gan_bat_thuong
        },
        "tong_so_canh_bao": len(canh_bao_than) + len(canh_bao_gan) + len(canh_bao_thuc_pham),
        "co_canh_bao_critical": co_canh_bao_critical,
        "canh_bao_hieu_chinh_than": canh_bao_than,
        "canh_bao_hieu_chinh_gan": canh_bao_gan,
        "huong_dan_tuong_tac_thuc_pham": canh_bao_thuc_pham
    }
