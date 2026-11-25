# -*- coding: utf-8 -*-
"""Động cơ Tự động Hiệu chỉnh Liều Thuốc theo Chức năng Thận & Gan (CDSS Pharmacokinetics).

Tích hợp công thức Cockcroft-Gault / CKD-EPI và ma trận điều chỉnh liều lâm sàng:
- Tính toán độ thanh thải Creatinine (CrCl) và phân tầng suy thận KDIGO.
- Tự động phát hiện các thuốc bài xuất qua thận cần giảm liều hoặc chống chỉ định
  (Metformin, Ciprofloxacin, Levofloxacin, Enoxaparin, DOACs, Allopurinol...).
- Rà soát chức năng gan (AST, ALT, Bilirubin) và hiệu chỉnh thuốc chuyển hóa qua gan (Paracetamol, NSAIDs, Statin).
- Tích hợp hướng dẫn tương tác Thuốc - Thực phẩm (Drug-Food Interactions).
"""

from typing import Dict, List, Optional, Any
import re

from src.chuan_hoa_don_vi_xet_nghiem import chuan_hoa_creatinine, chuan_hoa_du_lieu_xet_nghiem


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
    - Scr: Serum Creatinine (mg/dL)
    - tuoi: Tuổi bệnh nhân (năm)
    
    Ưu điểm lâm sàng: Hoàn toàn không cần Cân nặng, Chiều cao hay Chủng tộc;
    cung cấp cơ chế fallback an toàn tuyệt đối khi hồ sơ ngoại trú thiếu cân nặng/chiều cao.
    """
    if creatinine_mg_dl is None:
        return 0.0
    try:
        scr = float(creatinine_mg_dl)
        age = int(tuoi) if tuoi is not None else 50
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
        "ten_chuan": "Metformin",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "CRITICAL",
        "khuyen_cao": "CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI khi CrCl/eGFR < 30 mL/phút",
        "lieu_de_xuat": "Ngừng Metformin, chuyển sang Insulin hoặc thuốc hạ đường huyết an toàn cho thận.",
        "ly_do": "Nguy cơ tích lũy thuốc gây toan chuyển hóa acid lactic đe dọa tính mạng (tỷ lệ tử vong tới 50%)."
    },
    {
        "thuoc": "metformin",
        "ten_chuan": "Metformin",
        "dieu_kien": lambda cr: 30 <= cr < 45,
        "muc_do": "WARNING",
        "khuyen_cao": "Giảm 50% liều dùng thông thường (Tối đa 1000 mg/ngày)",
        "lieu_de_xuat": "500 mg x 1-2 lần/ngày (tối đa 1000 mg/ngày), theo dõi eGFR mỗi 3 tháng.",
        "ly_do": "Giảm độ lọc cầu thận làm chậm bài tiết Metformin qua ống thận."
    },
    {
        "thuoc": "ciprofloxacin",
        "ten_chuan": "Ciprofloxacin",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "WARNING",
        "khuyen_cao": "Giảm 50% liều hoặc giãn khoảng cách dùng mỗi 18-24 giờ",
        "lieu_de_xuat": "250-500 mg mỗi 18-24 giờ (hoặc 50% liều thông thường).",
        "ly_do": "Thuốc thải trừ chủ yếu qua thận, tích lũy làm tăng nguy cơ co giật và độc tính gân cơ."
    },
    {
        "thuoc": "levofloxacin",
        "ten_chuan": "Levofloxacin",
        "dieu_kien": lambda cr: 20 <= cr < 50,
        "muc_do": "WARNING",
        "khuyen_cao": "Khởi đầu 500 mg, sau đó duy trì 250 mg mỗi 24 giờ",
        "lieu_de_xuat": "Khởi đầu 500 mg, sau đó 250 mg mỗi 24 giờ (thay vì 500-750 mg mỗi 24h).",
        "ly_do": "Hơn 80% Levofloxacin đào thải nguyên dạng qua nước tiểu."
    },
    {
        "thuoc": "levofloxacin",
        "ten_chuan": "Levofloxacin",
        "dieu_kien": lambda cr: cr < 20,
        "muc_do": "CRITICAL",
        "khuyen_cao": "Khởi đầu 500 mg, sau đó 250 mg mỗi 48 giờ",
        "lieu_de_xuat": "Khởi đầu 500 mg, sau đó 250 mg mỗi 48 giờ.",
        "ly_do": "Tích lũy kéo dài gây độc tính thần kinh trung ương và kéo dài khoảng QT."
    },
    {
        "thuoc": "enoxaparin",
        "ten_chuan": "Enoxaparin (Lovenox)",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "CRITICAL",
        "khuyen_cao": "Giảm liều điều trị xuống 1 mg/kg mỗi 24 giờ (thay vì mỗi 12 giờ)",
        "lieu_de_xuat": "1 mg/kg tiêm dưới da mỗi 24 giờ. Liều dự phòng: 20 mg mỗi 24 giờ.",
        "ly_do": "Nguy cơ tích tụ kháng đông dẫn tới xuất huyết nội sọ hoặc xuất huyết tiêu hóa ồ ạt."
    },
    {
        "thuoc": "allopurinol",
        "ten_chuan": "Allopurinol",
        "dieu_kien": lambda cr: 10 <= cr < 30,
        "muc_do": "WARNING",
        "khuyen_cao": "Giảm liều khởi đầu xuống 100 mg/ngày (tối đa 200 mg/ngày)",
        "lieu_de_xuat": "100 mg mỗi ngày hoặc 100 mg cách ngày.",
        "ly_do": "Chất chuyển hóa Oxypurinol tích lũy làm tăng vọt nguy cơ phản ứng da nặng (Hội chứng DRESS, Stevens-Johnson)."
    },
    {
        "thuoc": "allopurinol",
        "ten_chuan": "Allopurinol",
        "dieu_kien": lambda cr: cr < 10,
        "muc_do": "CRITICAL",
        "khuyen_cao": "Tối đa 100 mg cách ngày hoặc chuyển sang Febuxostat",
        "lieu_de_xuat": "100 mg dùng cách ngày hoặc cân nhắc Febuxostat chuyển hóa qua gan.",
        "ly_do": "Đào thải thận gần như ngưng trệ, độc tính da và gan rất cao."
    },
    {
        "thuoc": "dabigatran",
        "ten_chuan": "Dabigatran (Pradaxa)",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "CRITICAL",
        "khuyen_cao": "CHỐNG CHỈ ĐỊNH khi CrCl < 30 mL/phút",
        "lieu_de_xuat": "Chống chỉ định tuyệt đối. Cân nhắc chuyển sang Warfarin có chỉnh liều theo INR.",
        "ly_do": "80% Dabigatran thải qua thận. Suy thận nặng gây tăng nồng độ gấp 6 lần, nguy cơ tử vong do chảy máu."
    },
    {
        "thuoc": "rivaroxaban",
        "ten_chuan": "Rivaroxaban (Xarelto)",
        "dieu_kien": lambda cr: 15 <= cr < 50,
        "muc_do": "WARNING",
        "khuyen_cao": "Giảm liều xuống 15 mg x 1 lần/ngày (thay vì 20 mg/ngày)",
        "lieu_de_xuat": "15 mg uống cùng bữa ăn 1 lần mỗi ngày.",
        "ly_do": "Thanh thải thận giảm 35-50%, làm tăng AUC của thuốc kháng đông."
    },
    {
        "thuoc": "spironolactone",
        "ten_chuan": "Spironolactone",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "CRITICAL",
        "khuyen_cao": "CHỐNG CHỈ ĐỊNH hoặc THẬN TRỌNG TỐI ĐA",
        "lieu_de_xuat": "Tránh dùng nếu eGFR < 30 mL/phút hoặc Kali máu > 5.0 mmol/L.",
        "ly_do": "Nguy cơ tăng Kali máu ác tính gây block nhĩ thất và ngừng tim đột ngột."
    },
    {
        "thuoc": "methotrexate",
        "ten_chuan": "Methotrexate",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "CRITICAL",
        "khuyen_cao": "CHỐNG CHỈ ĐỊNH TUYỆT ĐỐI khi CrCl/eGFR < 30 mL/phút",
        "lieu_de_xuat": "Chống chỉ định. Chuyển sang liệu pháp an toàn cho thận.",
        "ly_do": "Methotrexate bài xuất 80-90% qua thận; suy thận nặng gây tích lũy nồng độ cực độc dẫn tới suy tủy toàn bộ và tử vong."
    },
    {
        "thuoc": "methotrexate",
        "ten_chuan": "Methotrexate",
        "dieu_kien": lambda cr: 30 <= cr < 50,
        "muc_do": "WARNING",
        "khuyen_cao": "Giảm 50% liều Methotrexate tuần",
        "lieu_de_xuat": "Giảm 50% liều dùng mỗi tuần, bổ sung acid folic 5mg/tuần và theo dõi công thức máu mỗi 2 tuần.",
        "ly_do": "Giảm độ lọc cầu thận làm chậm thanh thải Methotrexate, tăng độc tính tế bào máu và gan."
    },
    {
        "thuoc": "colchicine",
        "ten_chuan": "Colchicine",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "CRITICAL",
        "khuyen_cao": "CHỐNG CHỈ ĐỊNH khi dùng kèm thuốc ức chế CYP3A4/P-gp; giảm liều tối đa 0.5 mg/ngày",
        "lieu_de_xuat": "Tối đa 0.5 mg/ngày cho đợt Gout cấp và không lặp lại liệu trình trong vòng 14 ngày.",
        "ly_do": "Nguy cơ ngộ độc Colchicine cấp tính gây tiêu cơ vân, suy tủy và liệt thần kinh cơ đe dọa tính mạng."
    },
    {
        "thuoc": "ethambutol",
        "ten_chuan": "Ethambutol",
        "dieu_kien": lambda cr: cr < 30,
        "muc_do": "WARNING",
        "khuyen_cao": "Giãn khoảng cách dùng 15-25 mg/kg 3 lần mỗi tuần (thay vì dùng hàng ngày)",
        "lieu_de_xuat": "15-25 mg/kg uống 3 lần/tuần (thứ 2 - 4 - 6).",
        "ly_do": "Ethambutol thải trừ chủ yếu qua thận; tích lũy kéo dài gây độc tính viêm dây thần kinh thị giác giảm thị lực không hồi phục."
    },
    {
        "thuoc": "digoxin",
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
        "ten_chuan": "Tetracycline / Doxycycline",
        "thuc_pham": "Sữa, viên uống Sắt/Canxi",
        "khuyen_cao": "Tránh uống cùng sữa hoặc thuốc bổ máu chứa sắt. Cách nhau tối thiểu 2-3 giờ.",
        "ly_do": "Tạo phức chelate không hấp thu qua niêm mạc ruột non."
    },
    {
        "thuoc": "warfarin",
        "ten_chuan": "Warfarin (Sintrom / Coumadin)",
        "thuc_pham": "Rau xanh đậm màu (rau muống, bông cải xanh, cải xoăn, rau chân vịt)",
        "khuyen_cao": "Duy trì chế độ ăn rau xanh ổn định hàng ngày, không ăn tăng vọt đột ngột.",
        "ly_do": "Vitamin K tự nhiên trong rau xanh đậm là chất đối kháng trực tiếp cơ chế chống đông của Warfarin."
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
    tuoi_raw = thong_tin_benh_nhan.get("tuoi")
    try:
        tuoi: int = int(tuoi_raw) if tuoi_raw is not None else 50
    except (ValueError, TypeError):
        tuoi = 50

    can_nang_raw = thong_tin_benh_nhan.get("can_nang_kg")
    can_nang: Optional[float] = None
    if can_nang_raw is not None:
        try:
            can_nang_float = float(can_nang_raw)
            if can_nang_float > 0:
                can_nang = can_nang_float
        except (ValueError, TypeError):
            can_nang = None

    la_nu_raw = thong_tin_benh_nhan.get("la_nu", False)
    la_nu = False
    if isinstance(la_nu_raw, bool):
        la_nu = la_nu_raw
    elif isinstance(la_nu_raw, str):
        la_nu = any(x in la_nu_raw.lower() for x in ("nữ", "nu", "female", "f"))
    elif la_nu_raw is not None:
        la_nu = bool(la_nu_raw)

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
    if creat_mg_dl is not None and can_nang is not None and tuoi >= 18:
        crcl_val = tinh_crcl(tuoi, can_nang, creat_mg_dl, la_nu)

    # Đánh giá eGFR (KDIGO CKD-EPI 2021 race-free fallback cho người lớn, Bedside Schwartz cho nhi khoa)
    egfr_val: Optional[float] = None
    phuong_phap_uoc_tinh: str = "Chua_co_du_lieu"

    if egfr_lab_val is not None:
        try:
            egfr_val = float(egfr_lab_val)
            phuong_phap_uoc_tinh = "Ket_qua_phong_xet_nghiem"
        except (ValueError, TypeError):
            egfr_val = None

    if egfr_val is None and creat_mg_dl is not None:
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
    ast_raw = ket_qua_xet_nghiem.get("ast")
    if ast_raw is None:
        ast_raw = ket_qua_xet_nghiem.get("got")
    try:
        ast_val = float(ast_raw) if ast_raw is not None else 25.0
    except (ValueError, TypeError):
        ast_val = 25.0

    alt_raw = ket_qua_xet_nghiem.get("alt")
    if alt_raw is None:
        alt_raw = ket_qua_xet_nghiem.get("gpt")
    try:
        alt_val = float(alt_raw) if alt_raw is not None else 25.0
    except (ValueError, TypeError):
        alt_val = 25.0

    bili_raw = ket_qua_xet_nghiem.get("bilirubin")
    try:
        bili_val = float(bili_raw) if bili_raw is not None else 15.0
    except (ValueError, TypeError):
        bili_val = 15.0
    
    gan_bat_thuong = (ast_val > 100 or alt_val > 100 or bili_val > 30)
    
    canh_bao_than: List[Dict[str, Any]] = []
    canh_bao_gan: List[Dict[str, Any]] = []
    canh_bao_thuc_pham: List[Dict[str, Any]] = []
    
    # Chuẩn hóa an toàn danh sách thuốc
    danh_sach_thuoc_an_toan = danh_sach_thuoc if isinstance(danh_sach_thuoc, list) else []
    thuoc_lower = [str(t).lower().strip() for t in danh_sach_thuoc_an_toan if t is not None and str(t).strip()]
    chuoi_thuoc_gop = " ".join(thuoc_lower)
    
    # Kiểm tra hiệu chỉnh thận
    if chi_so_than_chinh is not None:
        for qt in QUY_TAC_THAN:
            if qt["thuoc"] in chuoi_thuoc_gop or any(re.search(r'\b' + re.escape(qt["thuoc"]) + r'\b', t) for t in thuoc_lower):
                if qt["dieu_kien"](chi_so_than_chinh):
                    canh_bao_than.append({
                        "thuoc": qt["ten_chuan"],
                        "muc_do": qt["muc_do"],
                        "chi_so_danh_gia": f"CrCl/eGFR = {round(chi_so_than_chinh, 1)} mL/phút ({phan_do_than['giai_doan'] if phan_do_than else ''})",
                        "khuyen_cao": qt["khuyen_cao"],
                        "lieu_de_xuat": qt["lieu_de_xuat"],
                        "ly_do_lam_sang": qt["ly_do"]
                    })
    
    # Kiểm tra hiệu chỉnh gan
    for qt in QUY_TAC_GAN:
        if qt["thuoc"] in chuoi_thuoc_gop or any(re.search(r'\b' + re.escape(qt["thuoc"]) + r'\b', t) for t in thuoc_lower):
            if qt["dieu_kien"](ast_val, alt_val, bili_val):
                canh_bao_gan.append({
                    "thuoc": qt["ten_chuan"],
                    "muc_do": qt["muc_do"],
                    "chi_so_danh_gia": f"AST={ast_val} U/L, ALT={alt_val} U/L, Bilirubin={bili_val} µmol/L",
                    "khuyen_cao": qt["khuyen_cao"],
                    "lieu_de_xuat": qt["lieu_de_xuat"],
                    "ly_do_lam_sang": qt["ly_do"]
                })
                
    # Kiểm tra tương tác thuốc - thức ăn
    for tt in TUONG_TAC_THUC_PHAM:
        if tt["thuoc"] in chuoi_thuoc_gop or any(re.search(r'\b' + re.escape(tt["thuoc"]) + r'\b', t) for t in thuoc_lower):
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
            "phan_do": phan_do_than
        },
        "chuc_nang_gan": {
            "ast": ast_val,
            "alt": alt_val,
            "bilirubin": bili_val,
            "bat_thuong": gan_bat_thuong
        },
        "tong_so_canh_bao": len(canh_bao_than) + len(canh_bao_gan) + len(canh_bao_thuc_pham),
        "co_canh_bao_critical": co_canh_bao_critical,
        "canh_bao_hieu_chinh_than": canh_bao_than,
        "canh_bao_hieu_chinh_gan": canh_bao_gan,
        "huong_dan_tuong_tac_thuc_pham": canh_bao_thuc_pham
    }
