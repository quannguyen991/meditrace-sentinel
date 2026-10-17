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


def tinh_crcl(tuoi: int, can_nang_kg: float, creatinine_mg_dl: float, la_nu: bool = False) -> float:
    """Tính độ thanh thải Creatinine ước tính theo công thức Cockcroft-Gault (mL/phút).
    
    CrCl = ((140 - Tuổi) * Cân nặng) / (72 * Creatinine mg/dL) * (0.85 nếu Nữ)
    """
    if creatinine_mg_dl <= 0 or can_nang_kg <= 0 or tuoi <= 0:
        return 0.0
    
    crcl = ((140 - tuoi) * can_nang_kg) / (72 * creatinine_mg_dl)
    if la_nu:
        crcl *= 0.85
    return round(crcl, 1)


def chuyen_umol_sang_mg_dl(creatinine_umol_l: float) -> float:
    """Chuyển đơn vị Creatinine từ umol/L sang mg/dL."""
    return round(creatinine_umol_l / 88.4, 2)


def phan_do_suy_than(crcl_hoac_egfr: float) -> Dict[str, str]:
    """Phân độ suy thận theo hướng dẫn KDIGO."""
    if crcl_hoac_egfr >= 90:
        return {"giai_doan": "G1", "mo_ta": "Chức năng thận bình thường hoặc tăng", "muc_do": "BINH_THUONG"}
    elif crcl_hoac_egfr >= 60:
        return {"giai_doan": "G2", "mo_ta": "Suy giảm chức năng thận nhẹ", "muc_do": "GIAM_NHE"}
    elif crcl_hoac_egfr >= 45:
        return {"giai_doan": "G3a", "mo_ta": "Suy giảm chức năng thận nhẹ đến trung bình", "muc_do": "GIAM_TRUNG_BINH"}
    elif crcl_hoac_egfr >= 30:
        return {"giai_doan": "G3b", "mo_ta": "Suy giảm chức năng thận trung bình đến nặng", "muc_do": "GIAM_VUA_NANG"}
    elif crcl_hoac_egfr >= 15:
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
    }
]

# Cơ sở tri thức theo chức năng gan
QUY_TAC_GAN = [
    {
        "thuoc": "paracetamol",
        "ten_chuan": "Paracetamol (Acetaminophen)",
        "dieu_kien": lambda ast, alt, bili: ast > 150 or alt > 150 or bili > 35,
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
        "dieu_kien": lambda ast, alt, bili: ast > 150 or alt > 150,
        "muc_do": "WARNING",
        "khuyen_cao": "Tạm ngừng Statin hoặc giảm liều tối thiểu, theo dõi lại men gan sau 2-4 tuần",
        "lieu_de_xuat": "Tạm ngừng dùng statin cho đến khi ALT/AST hồi phục về mức < 3 lần giới hạn bình thường.",
        "ly_do": "Statin chuyển hóa chủ yếu qua gan, tổn thương tế bào gan đang tiến triển làm tăng nguy cơ hủy hoại cơ và độc tính gan."
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
    danh_sach_thuoc: List[str],
    ket_qua_xet_nghiem: Optional[Dict[str, Any]] = None,
    thong_tin_benh_nhan: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Phân tích và đưa ra khuyến cáo hiệu chỉnh liều theo chức năng Thận & Gan.
    
    Args:
        danh_sach_thuoc: Danh sách tên thuốc (chuỗi văn bản hoặc tên biệt dược)
        ket_qua_xet_nghiem: Dict chứa các chỉ số xét nghiệm (creatinine, egfr, ast, alt, bilirubin...)
        thong_tin_benh_nhan: Dict chứa tuổi, cân nặng, giới tính (nu: bool)
    """
    ket_qua_xet_nghiem = ket_qua_xet_nghiem or {}
    thong_tin_benh_nhan = thong_tin_benh_nhan or {}
    
    # 1. Đánh giá chức năng thận
    crcl_val: Optional[float] = None
    egfr_val: Optional[float] = ket_qua_xet_nghiem.get("egfr")
    creat_val = ket_qua_xet_nghiem.get("creatinine")
    
    tuoi = thong_tin_benh_nhan.get("tuoi", 50)
    can_nang = thong_tin_benh_nhan.get("can_nang_kg", 60.0)
    la_nu = thong_tin_benh_nhan.get("la_nu", False)
    
    if creat_val is not None and creat_val > 0:
        # Nếu creat > 30 thường là umol/L, nếu < 10 là mg/dL
        creat_mg_dl = creat_val if creat_val < 15.0 else chuyen_umol_sang_mg_dl(creat_val)
        crcl_val = tinh_crcl(tuoi, can_nang, creat_mg_dl, la_nu)
    
    # Ưu tiên eGFR nếu có, hoặc dùng CrCl
    chi_so_than_chinh = egfr_val if egfr_val is not None else crcl_val
    phan_do_than = phan_do_suy_than(chi_so_than_chinh) if chi_so_than_chinh is not None else None
    
    # 2. Đánh giá chức năng gan
    ast_val = ket_qua_xet_nghiem.get("ast", ket_qua_xet_nghiem.get("got", 25.0))
    alt_val = ket_qua_xet_nghiem.get("alt", ket_qua_xet_nghiem.get("gpt", 25.0))
    bili_val = ket_qua_xet_nghiem.get("bilirubin", 15.0)
    
    gan_bat_thuong = (ast_val > 100 or alt_val > 100 or bili_val > 30)
    
    canh_bao_than: List[Dict[str, Any]] = []
    canh_bao_gan: List[Dict[str, Any]] = []
    canh_bao_thuc_pham: List[Dict[str, Any]] = []
    
    # Chuẩn hóa tên các thuốc đang dùng
    thuoc_lower = [t.lower().strip() for t in danh_sach_thuoc]
    chuoi_thuoc_gop = " ".join(thuoc_lower)
    
    # Kiểm tra hiệu chỉnh thận
    if chi_so_than_chinh is not None:
        for qt in QUY_TAC_THAN:
            if qt["thuoc"] in chuoi_thuoc_gop or any(re.search(r'\b' + re.escape(qt["thuoc"]) + r'\b', t) for t in thuoc_lower):
                if qt["dieu_kien"](chi_so_than_chinh):
                    canh_bao_than.append({
                        "thuoc": qt["ten_chuan"],
                        "muc_do": qt["muc_do"],
                        "chi_so_danh_gia": f"CrCl/eGFR = {chi_so_than_chinh} mL/phút ({phan_do_than['giai_doan'] if phan_do_than else ''})",
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
