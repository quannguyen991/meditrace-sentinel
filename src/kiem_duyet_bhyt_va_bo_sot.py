# -*- coding: utf-8 -*-
"""Tầng 4.5 & Cổng Tiền kiểm Lâm sàng - BHYT Việt Nam:
1. ActiveOmissionRecoveryEngine (Tầng 4.5): Quét các đoạn hội thoại chưa được LLM trích xuất
   (`doan_chua_ghi`) bằng từ điển y khoa & Aho-Corasick để chủ động khôi phục các thông tin
   nguy cấp bị bỏ sót (Dị ứng, Thuốc, Triệu chứng âm tính quan trọng / Pertinent Negatives, Sinh hiệu).
2. BHYTXmlPreChecker (Quyết định 130/QĐ-BYT & 4750/QĐ-BYT + Thông tư 54/2017/TT-BYT Mức 6–7):
   Gợi ý mã bệnh ICD-10, kiểm tra chéo chỉ định Thuốc (XML2) với Chẩn đoán (XML1) & Diễn biến (XML5)
   để cảnh báo nguy cơ xuất toán BHYT, đồng thời kiểm tra liều Nhi khoa (mg/kg) và đa thuốc Đông-Tây y.
3. ClinicalHarmWeightedEvaluator (CHWER & Multi-Loop Backward Error Attribution):
   Đo lường sai số có trọng số sinh mạng lâm sàng (CHWER) và quy kết ngược tầng gây lỗi (Tầng 0..4)
   khi bác sĩ chỉnh sửa hoặc bác bỏ mệnh đề trên giao diện.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from html import escape as _xml_escape
import re
from typing import Any, Dict, List, Optional, Tuple

from src import cong_rui_ro, khoa_bang_chung
from src.phat_bieu import PhatBieu


# ---------------------------------------------------------------------------
# 1. DANH MỤC ÁNH XẠ CHẨN ĐOÁN / TRIỆU CHỨNG -> MÃ ICD-10 BỘ Y TẾ
# ---------------------------------------------------------------------------
DANH_MUC_ICD10_BYT: List[Tuple[str, str, str, Tuple[str, ...]]] = [
    # (Mã ICD-10, Tên chuẩn BYT, Nhóm chuyên khoa, Các từ khóa nhận diện)
    ("I10", "Tăng huyết áp vô căn (nguyên phát)", "Tim mạch",
     ("tăng huyết áp", "cao huyết áp", "huyết áp cao")),
    ("E11.2", "Đái tháo đường típ 2 có biến chứng thận", "Nội tiết",
     ("đái tháo đường biến chứng thận", "tiểu đường suy thận", "albumin niệu đái tháo đường")),
    ("E11.3", "Đái tháo đường típ 2 có biến chứng mắt", "Nội tiết",
     ("bệnh võng mạc đái tháo đường", "tiểu đường mờ mắt", "biến chứng mắt tiểu đường")),
    ("E11.4", "Đái tháo đường típ 2 có biến chứng thần kinh", "Nội tiết",
     ("tê bì chân tay tiểu đường", "biến chứng thần kinh đái tháo đường")),
    ("E11.9", "Đái tháo đường típ 2", "Nội tiết",
     ("đái tháo đường", "tiểu đường", "đường huyết cao")),
    ("I11.0", "Bệnh tim do tăng huyết áp có suy tim", "Tim mạch",
     ("tăng huyết áp suy tim", "suy tim do tăng huyết áp", "phì đại thất trái tăng huyết áp")),
    ("K25.9", "Loét dạ dày", "Tiêu hóa",
     ("loét dạ dày", "ổ loét dạ dày")),
    ("N18.3", "Bệnh thận mạn giai đoạn 3", "Thận - Tiết niệu",
     ("bệnh thận mạn giai đoạn 3", "suy thận độ 2", "suy thận giai đoạn 3")),
    ("E78.5", "Rối loạn chuyển hóa lipoprotein (Mỡ máu cao)", "Nội tiết",
     ("rối loạn mỡ máu", "mỡ máu cao", "tăng cholesterol", "tăng triglycerid")),
    ("I48", "Rung nhĩ và cuồng nhĩ", "Tim mạch",
     ("rung nhĩ", "loạn nhịp hoàn toàn")),
    ("I20.9", "Cơn đau thắt ngực / Bệnh tim thiếu máu cục bộ", "Tim mạch",
     ("đau thắt ngực", "thiếu máu cơ tim", "bệnh mạch vành")),
    ("I50.9", "Suy tim", "Tim mạch",
     ("suy tim", "khó thở khi nằm", "phù hai chân do tim")),
    ("J02.9", "Viêm họng cấp", "Hô hấp",
     ("viêm họng", "đau rát họng", "họng đỏ", "viêm amidan")),
    ("J01.9", "Viêm xoang cấp", "Tai Mũi Họng",
     ("viêm xoang", "đau nhức hốc mũi", "nghẹt mũi chảy dịch đặc")),
    ("J20.9", "Viêm phế quản cấp", "Hô hấp",
     ("viêm phế quản", "ho đờm", "ran rít", "ran ngáy")),
    ("J18.9", "Viêm phổi", "Hô hấp",
     ("viêm phổi", "đông đặc phổi", "ran ẩm", "ran nổ")),
    ("J45.9", "Hen phế quản", "Hô hấp",
     ("hen phế quản", "hen suyễn", "cơn hen", "khò khè tái diễn")),
    ("J44.9", "Bệnh phổi tắc nghẽn mạn tính (COPD)", "Hô hấp",
     ("copd", "phổi tắc nghẽn mạn tính")),
    ("J30.4", "Viêm mũi dị ứng", "Tai Mũi Họng",
     ("viêm mũi dị ứng", "hắt hơi sổ mũi dị ứng")),
    ("K29.7", "Viêm dạ dày - tá tràng", "Tiêu hóa",
     ("viêm dạ dày", "viêm loét dạ dày", "đau thượng vị", "đau bao tử", "xót ruột")),
    ("K21.9", "Bệnh trào ngược dạ dày - thực quản (GERD)", "Tiêu hóa",
     ("trào ngược dạ dày", "ợ hơi ợ chua", "gerd", "nóng rát sau xương ức")),
    ("A09", "Tiêu chảy và viêm dạ dày-ruột nhiễm khuẩn", "Tiêu hóa",
     ("tiêu chảy cấp", "viêm ruột", "đi ngoài phân lỏng")),
    ("N39.0", "Nhiễm khuẩn đường tiết niệu", "Thận - Tiết niệu",
     ("nhiễm khuẩn tiết niệu", "viêm đường tiết niệu", "tiểu buốt", "tiểu rắt")),
    ("N18.9", "Bệnh thận mạn", "Thận - Tiết niệu",
     ("suy thận", "bệnh thận mạn", "ckd")),
    ("M54.5", "Đau thắt lưng / Thoái hóa cột sống", "Cơ xương khớp",
     ("đau thắt lưng", "thoái hóa cột sống", "đau lưng cấp")),
    ("M17.9", "Thoái hóa khớp gối / Viêm khớp", "Cơ xương khớp",
     ("thoái hóa khớp", "đau khớp gối", "sưng đau khớp", "viêm khớp")),
    ("M10.9", "Bệnh Gút (Gout)", "Cơ xương khớp",
     ("bệnh gút", "gout", "tăng acid uric", "sưng ngón chân cái")),
    ("G43.9", "Đau nửa đầu (Migraine) / Đau đầu vận mạch", "Thần kinh",
     ("đau nửa đầu", "migraine", "đau đầu vận mạch")),
    ("H81.1", "Chóng mặt tư thế kịch phát lành tính / Rối loạn tiền đình", "Thần kinh",
     ("rối loạn tiền đình", "chóng mặt xoay tròn")),
    ("L20.9", "Viêm da cơ địa / Dị ứng da", "Da liễu",
     ("viêm da cơ địa", "nổi mề đay", "viêm da dị ứng", "chàm")),
    ("H10.9", "Viêm kết mạc", "Mắt",
     ("viêm kết mạc", "đau mắt đỏ")),
]

# Quy tắc đối chiếu Thuốc (XML2) -> Nhóm Mã ICD-10 hợp lệ (XML1) theo phác đồ BHYT
QUY_TAC_THUOC_ICD10_BHYT: Dict[str, Tuple[Tuple[str, ...], str]] = {
    "omeprazol": (("K29.7", "K21.9", "M54.5", "M17.9", "M10.9"),
                  "Thuốc ức chế bơm proton (PPI) cần mã ICD-10 bệnh lý dạ dày-trào ngược (K21/K29) hoặc dự phòng loét do NSAID."),
    "esomeprazol": (("K29.7", "K21.9", "M54.5", "M17.9"),
                    "Esomeprazol cần mã ICD-10 viêm loét dạ dày - tá tràng hoặc trào ngược (K21/K29)."),
    "pantoprazol": (("K29.7", "K21.9"),
                    "Pantoprazol cần mã ICD-10 bệnh lý dạ dày - thực quản (K21/K29)."),
    "metformin": (("E11.9", "E11.2", "E11.3", "E11.4"),
                  "Metformin bắt buộc phải có mã ICD-10 Đái tháo đường (E11.x) ở mục Chẩn đoán chính hoặc bệnh kèm theo."),
    "insulin": (("E11.9", "E11.2", "E11.3", "E11.4"),
                "Insulin bắt buộc phải có mã ICD-10 Đái tháo đường (E10-E14) để tránh xuất toán BHYT."),
    "amlodipin": (("I10", "I11.0", "I20.9"),
                  "Amlodipin cần mã ICD-10 Tăng huyết áp (I10/I11) hoặc Bệnh mạch vành (I20)."),
    "losartan": (("I10", "I11.0", "I50.9", "N18.9", "N18.3", "E11.2"),
                 "Losartan cần mã ICD-10 Tăng huyết áp (I10/I11), Suy tim (I50) hoặc Bệnh thận mạn/đái tháo đường."),
    "atorvastatin": (("E78.5", "I20.9", "I10"),
                     "Statin hạ mỡ máu cần mã ICD-10 Rối loạn chuyển hóa lipid (E78.x) hoặc bệnh lý tim mạch nguy cơ cao."),
    "rosuvastatin": (("E78.5", "I20.9"),
                     "Rosuvastatin cần mã ICD-10 Rối loạn lipid máu (E78.x) hoặc bệnh mạch vành."),
    "salbutamol": (("J45.9", "J44.9", "J20.9"),
                   "Thuốc giãn phế quản Salbutamol cần mã ICD-10 Hen phế quản (J45), COPD (J44) hoặc co thắt phế quản."),
    "ventolin": (("J45.9", "J44.9", "J20.9"),
                 "Ventolin cần mã ICD-10 Hen phế quản (J45) hoặc COPD (J44)."),
    "amoxicillin": (("J02.9", "J01.9", "J20.9", "J18.9", "N39.0"),
                    "Kháng sinh Amoxicillin cần mã ICD-10 bệnh lý nhiễm khuẩn (J01, J02, J18, J20, N39...)."),
    "augmentin": (("J02.9", "J01.9", "J20.9", "J18.9", "N39.0"),
                  "Kháng sinh Augmentin cần mã ICD-10 nhiễm khuẩn hô hấp, tiết niệu hoặc mô mềm."),
    "cefixim": (("J02.9", "J01.9", "J20.9", "J18.9", "N39.0", "A09"),
                "Kháng sinh Cefixim cần mã ICD-10 nhiễm khuẩn tương ứng trong mục Chẩn đoán."),
    "azithromycin": (("J02.9", "J01.9", "J20.9", "J18.9"),
                     "Kháng sinh Azithromycin cần mã ICD-10 nhiễm khuẩn đường hô hấp hoặc mô mềm."),
    "warfarin": (("I48",),
                 "Chống đông kháng Vitamin K (Warfarin) cần mã ICD-10 Rung nhĩ (I48) hoặc Huyết khối tĩnh mạch/Van tim cơ học."),
    "coumadin": (("I48",),
                 "Coumadin (Warfarin) cần mã ICD-10 Rung nhĩ (I48) hoặc Huyết khối tĩnh mạch/Van tim cơ học."),
    "acenocoumarol": (("I48",),
                      "Chống đông kháng Vitamin K (Acenocoumarol) cần mã ICD-10 Rung nhĩ (I48) hoặc Huyết khối tĩnh mạch/Van tim cơ học."),
    "sintrom": (("I48",),
                "Sintrom (Acenocoumarol) cần mã ICD-10 Rung nhĩ (I48) hoặc Huyết khối tĩnh mạch/Van tim cơ học."),
    "losec": (("K29.7", "K21.9", "M54.5", "M17.9", "M10.9"),
              "Losec (Omeprazole) cần mã ICD-10 bệnh lý dạ dày-trào ngược (K21/K29) hoặc dự phòng loét do NSAID."),
    "colchicin": (("M10.9",),
                  "Colchicin cần mã ICD-10 Bệnh Gút (M10.x)."),
    "glucophage": (("E11.9", "E11.2", "E11.3", "E11.4"),
                   "Glucophage (Metformin) bắt buộc phải có mã ICD-10 Đái tháo đường (E11.x)."),
    "crestor": (("E78.5", "I20.9"),
                "Crestor (Rosuvastatin) cần mã ICD-10 Rối loạn lipid máu (E78.x) hoặc bệnh mạch vành."),
    "lipitor": (("E78.5", "I20.9", "I10"),
                "Lipitor (Atorvastatin) cần mã ICD-10 Rối loạn lipid máu (E78.x) hoặc tim mạch nguy cơ cao."),
    "nexium": (("K29.7", "K21.9", "M54.5", "M17.9"),
               "Nexium (Esomeprazol) cần mã ICD-10 viêm loét dạ dày - tá tràng hoặc trào ngược (K21/K29)."),
    "cozaar": (("I10", "I11.0", "I50.9", "N18.9", "N18.3", "E11.2"),
               "Cozaar (Losartan) cần mã ICD-10 Tăng huyết áp (I10/I11), Suy tim (I50) hoặc Bệnh thận mạn."),
}

# Quy tắc liều Nhi khoa theo cân nặng (mg/kg/ngày tối đa an toàn)
# 25/11/2026: doc tu MOT nguon (data/tri_thuc_thuoc.json, chua duyet).
from src import tri_thuc_thuoc as _ttt
LIEU_TRAN_NHI_KHOA_MG_KG_NGAY: Dict[str, Tuple[float, float, str]] = _ttt.bang_lieu_tre_em()

# Nhận diện Đa thuốc ngầm / Thuốc Đông y - Thuốc không rõ nhãn mác dễ trộn Corticoid hoặc Paracetamol
RE_THUOC_DONG_Y_NGAM = re.compile(
    r"(?i)\b(thuốc\s+tễ|thuốc\s+cam|thuốc\s+hoàn|thuốc\s+tán|thuốc\s+nam|thuốc\s+bắc|"
    r"cao\s+lá|gói\s+bột\s+(?:cam|giảm\s+đau)|thuốc\s+tàu|viên\s+hoàn\s+trị\s+khớp)\b"
)
BIET_DUOC_CHUA_PARACETAMOL = tuple(_ttt.ten_cua("paracetamol"))

# Boost 5: Quy tắc đối chiếu Chỉ định Cận lâm sàng / DVKT chi phí cao (XML3/XML4) <-> Diễn biến lâm sàng (XML5)
QUY_TAC_CHI_DINH_CLS_BHYT: Dict[str, Dict[str, Any]] = {
    "chụp mri": {
        "ma_dvkt": "17.0001",
        "ten_dich_vu": "Chụp cộng hưởng từ (MRI)",
        "mau_nhan_dien": r"(?i)\b(?:chụp\s+)?mri\b",
        "trieu_chung_bat_buoc": (
            "đau đầu kéo dài", "đau đầu dữ dội", "yếu liệt", "tê bì", "thoát vị đĩa đệm",
            "đau cột sống", "đau thắt lưng lan", "co giật", "chóng mặt", "thần kinh khu trú",
            "đứt dây chằng", "đau khớp gối", "chấn thương", "u não", "đột quỵ",
        ),
    },
    "cộng hưởng từ": {
        "ma_dvkt": "17.0001",
        "ten_dich_vu": "Chụp cộng hưởng từ (MRI)",
        "mau_nhan_dien": r"(?i)\bcộng\s+hưởng\s+từ\b",
        "trieu_chung_bat_buoc": (
            "đau đầu kéo dài", "đau đầu dữ dội", "yếu liệt", "tê bì", "thoát vị đĩa đệm",
            "đau cột sống", "đau thắt lưng lan", "co giật", "chóng mặt", "thần kinh khu trú",
            "đứt dây chằng", "đau khớp gối", "chấn thương", "u não", "đột quỵ",
        ),
    },
    "ct-scan": {
        "ma_dvkt": "17.0002",
        "ten_dich_vu": "Chụp cắt lớp vi tính (CT-Scan)",
        "mau_nhan_dien": r"(?i)\b(?:ct[\-\s]*scan|chụp\s+ct)\b",
        "trieu_chung_bat_buoc": (
            "chấn thương", "đột quỵ", "tai biến", "đau đầu dữ dội", "yếu nửa người", "hôn mê",
            "ho ra máu", "đau bụng cấp", "khó thở", "viêm xoang", "u phổi", "sỏi thận", "sỏi niệu quản",
        ),
    },
    "cắt lớp vi tính": {
        "ma_dvkt": "17.0002",
        "ten_dich_vu": "Chụp cắt lớp vi tính (CT-Scan)",
        "mau_nhan_dien": r"(?i)\bcắt\s+lớp\s+vi\s+tính\b",
        "trieu_chung_bat_buoc": (
            "chấn thương", "đột quỵ", "tai biến", "đau đầu dữ dội", "yếu nửa người", "hôn mê",
            "ho ra máu", "đau bụng cấp", "khó thở", "viêm xoang", "u phổi", "sỏi thận", "sỏi niệu quản",
        ),
    },
    "nội soi dạ dày": {
        "ma_dvkt": "03.0001",
        "ten_dich_vu": "Nội soi thực quản - dạ dày - tá tràng",
        "mau_nhan_dien": r"(?i)\bnội\s+soi\s+(?:thực\s+quản\s*[-–]?\s*)?dạ\s+dày\b",
        "trieu_chung_bat_buoc": (
            "đau thượng vị", "đau dạ dày", "đau bao tử", "ợ hơi", "ợ chua", "trào ngược",
            "nóng rát", "nôn ra máu", "phân đen", "nuốt nghẹn", "buồn nôn", "xót ruột",
            "viêm dạ dày", "loét dạ dày",
        ),
    },
    "nội soi đại tràng": {
        "ma_dvkt": "03.0002",
        "ten_dich_vu": "Nội soi đại trực tràng",
        "mau_nhan_dien": r"(?i)\bnội\s+soi\s+đại\s+(?:trực\s+)?tràng\b",
        "trieu_chung_bat_buoc": (
            "đi ngoài ra máu", "đi cầu ra máu", "phân nhầy máu", "rối loạn đại tiện",
            "tiêu chảy kéo dài", "táo bón kéo dài", "đau bụng dưới", "đau dọc khung đại tràng",
            "sụt cân", "viêm đại tràng", "polyp",
        ),
    },
    "troponin": {
        "ma_dvkt": "23.0105",
        "ten_dich_vu": "Định lượng Troponin T/I máu",
        "mau_nhan_dien": r"(?i)\b(?:hs[\-\s]*)?troponin(?:\s*[ti])?\b",
        "trieu_chung_bat_buoc": (
            "đau ngực", "tức ngực", "đau thắt ngực", "nặng ngực", "khó thở",
            "vã mồ hôi", "nhồi máu cơ tim", "hội chứng vành cấp", "thiếu máu cơ tim", "hồi hộp",
        ),
    },
    "siêu âm doppler mạch": {
        "ma_dvkt": "18.0020",
        "ten_dich_vu": "Siêu âm Doppler mạch máu",
        "mau_nhan_dien": r"(?i)\bsiêu\s+âm\s+doppler\s+mạch\b",
        "trieu_chung_bat_buoc": (
            "tê chân", "tê bì", "đau cách hồi", "phù chân", "suy giãn tĩnh mạch",
            "huyết khối", "chóng mặt", "tăng huyết áp", "cao huyết áp", "đái tháo đường",
            "tiểu đường", "xơ vữa", "lạnh đầu chi",
        ),
    },
    "hba1c": {
        "ma_dvkt": "23.0042",
        "ten_dich_vu": "Định lượng HbA1c máu",
        "mau_nhan_dien": r"(?i)\bhba1c\b",
        "trieu_chung_bat_buoc": (
            "đái tháo đường", "tiểu đường", "đường huyết cao", "tăng đường huyết",
            "khát nước nhiều", "tiểu nhiều", "sụt cân", "rối loạn dung nạp đường",
        ),
    },
    "x-quang ngực": {
        "ma_dvkt": "16.0001",
        "ten_dich_vu": "Chụp X-quang ngực thẳng",
        "mau_nhan_dien": r"(?i)\bx[\-\s]*quang\s+(?:ngực|tim\s+phổi|phổi)\b",
        "trieu_chung_bat_buoc": (
            "ho", "khó thở", "đau ngực", "tức ngực", "sốt", "viêm phổi", "viêm phế quản",
            "hen", "copd", "ran ẩm", "ran nổ", "ran rít", "ho đờm", "ho ra máu",
        ),
    },
    "điện tâm đồ": {
        "ma_dvkt": "02.0001",
        "ten_dich_vu": "Ghi điện tâm đồ (ECG)",
        "mau_nhan_dien": r"(?i)\b(?:điện\s+tâm\s+đồ|điện\s+tim|ecg)\b",
        "trieu_chung_bat_buoc": (
            "đau ngực", "tức ngực", "khó thở", "hồi hộp", "đánh trống ngực", "loạn nhịp",
            "rung nhĩ", "tăng huyết áp", "cao huyết áp", "suy tim", "ngất", "chóng mặt",
            "mạch nhanh", "mạch chậm",
        ),
    },
    "crp": {
        "ma_dvkt": "23.0088",
        "ten_dich_vu": "Định lượng CRP (C-Reactive Protein)",
        "mau_nhan_dien": r"(?i)\b(?:hs[\-\s]*)?crp\b",
        "trieu_chung_bat_buoc": (
            "sốt", "viêm", "nhiễm trùng", "nhiễm khuẩn", "ho đờm", "đau họng",
            "tiểu buốt", "sưng đau", "áp xe",
        ),
    },
    "d-dimer": {
        "ma_dvkt": "22.0055",
        "ten_dich_vu": "Định lượng D-Dimer",
        "mau_nhan_dien": r"(?i)\bd[\-\s]*dimer\b",
        "trieu_chung_bat_buoc": (
            "khó thở", "đau ngực", "sưng phù", "phù một chân", "huyết khối",
            "tắc mạch phổi", "thuyên tắc", "rung nhĩ", "rối loạn đông máu",
        ),
    },
}


# ---------------------------------------------------------------------------
# 2. TẦNG 4.5: ĐỘNG CƠ KHÔI PHỤC BỎ SÓT CHỦ ĐỘNG (ACTIVE OMISSION RECOVERY)
# ---------------------------------------------------------------------------
@dataclass
class MenhDeKhoiPhuc:
    luot: int
    nguoi_noi: str
    loai_thong_tin: str           # "di_ung" | "thuoc" | "trieu_chung_am_tinh" | "sinh_hieu" | "thuoc_dong_y_ngam"
    noi_dung_goi_y: str
    trich_dan_nguyen_van: str
    muc_do_nghiem_trong: float
    ly_do_khoi_phuc: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ActiveOmissionRecoveryEngine:
    """Quét các đoạn thoại chưa được LLM trích xuất (`doan_chua_ghi`) để chủ động
    khôi phục các thực thể lâm sàng quan trọng bị bỏ sót (Giải quyết Câu hỏi số 1 của BGK).
    """

    RE_DI_UNG_BO_SOT = re.compile(
        r"(?i)\b(dị\s+ứng|mẫn\s+cảm|nổi\s+mề\s+đay|sốc\s+phản\s+vệ|phát\s+ban\s+khi\s+(?:uống|dùng))\b"
    )
    RE_AM_TINH_QUAN_TRONG = re.compile(
        r"(?i)\b(không\s+(?:sốt|đau\s+ngực|khó\s+thở|nôn|ho\s+ra\s+máu|co\s+giật|phù|dị\s+ứng)|"
        r"chưa\s+(?:từng|thấy)\s+(?:bị\s+)?dị\s+ứng)\b"
    )
    RE_SINH_HIEU_BO_SOT = re.compile(
        r"(?i)\b(huyết\s+áp\s+\d{2,3}(?:/\d{2,3})?|mạch\s+\d{2,3}|spo2\s+\d{2,3}\s*%?|"
        r"nhiệt\s+độ\s+\d{2}(?:[.,]\d)?|sốt\s+\d{2}(?:[.,]\d)\s*độ|nặng\s+\d{1,3}\s*(?:kg|cân))\b"
    )
    RE_THUOC_PHO_BIEN = re.compile(
        r"(?i)\b(penicillin|amoxicillin|augmentin|paracetamol|hapacol|efferalgan|panadol|"
        r"ibuprofen|cefixim|cephalexin|azithromycin|prednisolon|medrol|salbutamol|ventolin|"
        r"aspirin|clopidogrel|warfarin|sintrom|digoxin|insulin|metformin|amlodipin|losartan|"
        r"atorvastatin|rosuvastatin|omeprazol|esomeprazol|colchicin|allopurinol)\b"
    )

    # Loai canh bao -> (loai_thong_tin, muc nghiem trong) cua tang 4.5. Ma khac (dinh chinh,
    # khong chac, ke hoach, thoi gian, chung chung) chi hien o lop canh bao, khong goi y.
    LOAI_KHOI_PHUC = {
        "OMITTED_ALLERGY": ("di_ung", 1.0),
        "OMITTED_MEDICATION": ("thuoc", 0.9),
        "OMITTED_NEGATION": ("trieu_chung_am_tinh", 0.75),
        "OMITTED_NUMERIC_VALUE": ("sinh_hieu", 0.7),
    }

    @classmethod
    def quet_khoi_phuc(cls, ps: List[PhatBieu], hoi_thoai: str,
                       kk: Optional[Dict[str, Any]] = None) -> List[MenhDeKhoiPhuc]:
        """Tu 25/11/2026 la lop boc cua `canh_bao.bo_sot` — mot bo bo sot cho ca he
        thong. Ban cu (giu o git) co hai loi: bo qua MOI di ung bi sot khi mot menh de
        bat ky chua chu "dị ứng" (ke ca "không dị ứng"), va moi doan chi mot loai."""
        if not hoi_thoai or not hoi_thoai.strip():
            return []
        from src.canh_bao import bo_sot
        from src.canh_bao.phat_hien import NguCanh
        if kk is None:
            kk = khoa_bang_chung.khoa_ca(ps, hoi_thoai, bat_buoc_trich_dan=False)
        ket_qua: List[MenhDeKhoiPhuc] = []
        for d, ma, cum in bo_sot.quet_chi_tiet(NguCanh(hoi_thoai), ps, kk.get("doan_chua_ghi") or []):
            if ma not in cls.LOAI_KHOI_PHUC:
                continue
            loai, nt = cls.LOAI_KHOI_PHUC[ma]
            luot, vai, doan = int(d.get("luot", 0)), str(d.get("vai") or "bệnh nhân"), str(d.get("doan") or "").strip()
            if loai == "thuoc":
                if bo_sot.THUOC_DONG_Y.search(cum):
                    loai, nt = "thuoc_dong_y_ngam", 0.95
                elif any(t in cong_rui_ro.THUOC_KHOANG_DIEU_TRI_HEP for t in bo_sot._ten_thuoc(cum)):
                    nt = 1.0
            ket_qua.append(MenhDeKhoiPhuc(
                luot=luot, nguoi_noi=vai, loai_thong_tin=loai,
                noi_dung_goi_y=f"{loai} tại lượt {luot}: {cum}",
                trich_dan_nguyen_van=doan, muc_do_nghiem_trong=nt,
                ly_do_khoi_phuc=f"Tầng 4.5 ({ma}): “{cum}” chưa có dòng nào trong bản ghi dẫn tới."))
        return ket_qua


# ---------------------------------------------------------------------------
# 3. CỔNG TIỀN KIỂM BHYT (QĐ 130/QĐ-BYT & 4750/QĐ-BYT) & AN TOÀN NHI KHOA/ĐÔNG-TÂY Y
# ---------------------------------------------------------------------------
@dataclass
class KetQuaTienKiemBHYT:
    ma_icd10_chinh: Optional[Dict[str, str]]
    ma_icd10_kem_theo: List[Dict[str, str]]
    canh_bao_xuat_toan_bhyt: List[str]
    canh_bao_lieu_nhi_khoa: List[str]
    canh_bao_da_thuoc_dong_tay_y: List[str]
    bang_xml_130_4750: Dict[str, Any]
    dat_chuan_cdss_muc_6_7_tt54: bool
    bien_luan_chi_dinh_cls: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BHYTXmlPreChecker:
    """Tiền kiểm hồ sơ bệnh án điện tử theo Quyết định 130/QĐ-BYT & 4750/QĐ-BYT
    và Bộ tiêu chí Bệnh viện thông minh Mức 6–7 (Thông tư 54/2017/TT-BYT).
    """

    @classmethod
    def goi_y_icd10(cls, ps: List[PhatBieu], hoi_thoai: str = "") -> List[Dict[str, str]]:
        """Gợi ý danh sách mã ICD-10 từ các mệnh đề còn hiệu lực của bệnh nhân."""
        van_ban_bn = " ".join(
            (p.noi_dung or "").lower()
            for p in ps
            if getattr(p, "chu_the_id", 0) == 0
            and getattr(p, "trang_thai", "còn hiệu lực") == "còn hiệu lực"
            and not getattr(p, "phu_dinh", False)
            and getattr(p, "tinh_huong", "thực tế") != "giả định"
        )
        # Ưu tiên mệnh đề do bác sĩ nhận định trước (loại bỏ mệnh đề phủ định và giả định!)
        van_ban_chan_doan = " ".join(
            (p.noi_dung or "").lower()
            for p in ps
            if getattr(p, "chu_the_id", 0) == 0
            and getattr(p, "trang_thai", "còn hiệu lực") == "còn hiệu lực"
            and not getattr(p, "phu_dinh", False)
            and getattr(p, "tinh_huong", "thực tế") != "giả định"
            and (getattr(p, "hanh_vi", "") == "nhận định" or getattr(p, "nguoi_noi", "") == "bác sĩ")
        )

        da_chon: List[Dict[str, str]] = []
        ma_da_co = set()

        for nguon_vb, loai_khop in ((van_ban_chan_doan, "Chẩn đoán bác sĩ"), (van_ban_bn, "Triệu chứng/Bệnh sử")):
            for ma, ten_chuan, chuyen_khoa, tu_khoa_list in DANH_MUC_ICD10_BYT:
                if ma in ma_da_co:
                    continue
                for tk in tu_khoa_list:
                    if tk in nguon_vb:
                        da_chon.append({
                            "ma_icd10": ma,
                            "ten_benh_byt": ten_chuan,
                            "chuyen_khoa": chuyen_khoa,
                            "can_cu_khop": f"{loai_khop} ('{tk}')"
                        })
                        ma_da_co.add(ma)
                        break
        return da_chon

    @staticmethod
    def _la_thuoc_da_ngung(p: Any) -> bool:
        t_dict = getattr(p, "thuoc", None)
        if isinstance(t_dict, dict) and t_dict.get("trang_thai_dung") == "đã ngừng":
            return True
        nd_low = (getattr(p, "noi_dung", "") or "").lower()
        return any(kw in nd_low for kw in ("đã ngừng", "ngừng dùng", "ngưng dùng", "đã ngưng"))

    @classmethod
    def _tim_can_nang_kg(cls, ps: List[PhatBieu], hoi_thoai: str,
                         thong_tin_bn: Optional[Dict[str, Any]]) -> Optional[float]:
        if isinstance(thong_tin_bn, dict):
            cn_raw = thong_tin_bn.get("can_nang_kg") if thong_tin_bn.get("can_nang_kg") is not None else thong_tin_bn.get("can_nang")
            if cn_raw is not None:
                try:
                    val = float(cn_raw)
                    if val > 0:
                        return val
                except (ValueError, TypeError):
                    pass
        vb = " ".join([p.noi_dung for p in ps if getattr(p, "chu_the_id", 0) == 0] + [hoi_thoai or ""])
        m = re.search(r"(?i)\b(?:nặng|cân\s+nặng)\s*(\d{1,3}(?:[.,]\d)?)\s*(?:kg|cân|ký)\b", vb)
        if m:
            return float(m.group(1).replace(",", "."))
        return None

    @classmethod
    def kiem_tra_chi_dinh_cls(
        cls, ps: List[PhatBieu], hoi_thoai: str = ""
    ) -> List[Dict[str, Any]]:
        """Boost 5: Đối chiếu chỉ định Cận lâm sàng / DVKT (XML3/XML4) với Diễn biến lâm sàng (XML5)."""
        # Tập mệnh đề lâm sàng dương tính còn hiệu lực của bệnh nhân (chu_the_id == 0)
        ps_bang_chung_ls = [
            p for p in ps
            if getattr(p, "chu_the_id", 0) == 0
            and getattr(p, "trang_thai", "còn hiệu lực") == "còn hiệu lực"
            and not getattr(p, "phu_dinh", False)
            and getattr(p, "tinh_huong", "thực tế") != "giả định"
        ]

        # Thu thập các nguồn chỉ định CLS của bác sĩ (từ mệnh đề kế hoạch/bác sĩ + các lượt bác sĩ nói trong hội thoại)
        nguon_chi_dinh: List[Tuple[str, List[int]]] = []
        re_dong_tu_chi_dinh = re.compile(
            r"(?i)\b(chỉ\s+định|cho\s+làm|cho\s+chụp|cần\s+chụp|đi\s+chụp|xét\s+nghiệm|làm\s+thêm|kiểm\s+tra|đo\s+điện|nội\s+soi|siêu\s+âm)\b"
        )
        re_ket_qua_cu = re.compile(r"(?i)\b(năm\s+ngoái|trước\s+đây|phiếu\s+cũ|kết\s+quả\s+cũ|đã\s+chụp\s+từ)\b")
        re_phu_dinh_cd = re.compile(r"(?i)\b(không\s+cần|chưa\s+cần|không\s+chỉ\s+định|không\s+chụp|không\s+làm)\b")

        for p in ps:
            if getattr(p, "trang_thai", "còn hiệu lực") != "còn hiệu lực" or getattr(p, "phu_dinh", False):
                continue
            if getattr(p, "tinh_huong", "thực tế") == "giả định" or getattr(p, "thoi_gian_su_kien", "") == "quá khứ":
                continue
            nd = p.noi_dung or ""
            if re_ket_qua_cu.search(nd) or re_phu_dinh_cd.search(nd):
                continue
            la_chi_dinh = (
                getattr(p, "tinh_huong", "") == "kế hoạch"
                or getattr(p, "hanh_vi", "") == "kế hoạch"
                or getattr(p, "nguoi_noi", "") == "bác sĩ"
                or bool(re_dong_tu_chi_dinh.search(nd))
            )
            if la_chi_dinh:
                nguon_chi_dinh.append((nd, list(p.bang_chung or [])))

        if hoi_thoai:
            for idx_dong, dong in enumerate([d.strip() for d in hoi_thoai.splitlines() if d.strip()], start=1):
                sach = re.sub(r"^\s*\d+[.)]\s*", "", dong)
                if re.match(r"(?i)^(?:bác\s+s[ĩỹ]|bs|doctor|bac_si)\s*:", sach):
                    if not re_phu_dinh_cd.search(sach) and not re_ket_qua_cu.search(sach) and "?" not in sach:
                        nguon_chi_dinh.append((sach, [idx_dong]))

        da_xet_ma_dvkt = set()
        ket_qua_cls: List[Dict[str, Any]] = []

        for tu_khoa_cls, quy_tac in QUY_TAC_CHI_DINH_CLS_BHYT.items():
            ma_dvkt = quy_tac["ma_dvkt"]
            if ma_dvkt in da_xet_ma_dvkt:
                continue
            mau_re = re.compile(quy_tac["mau_nhan_dien"])
            luot_order: List[int] = []
            for vb_cd, bc_cd in nguon_chi_dinh:
                if mau_re.search(vb_cd):
                    for b in bc_cd:
                        if int(b) not in luot_order:
                            luot_order.append(int(b))
            if not luot_order:
                continue

            da_xet_ma_dvkt.add(ma_dvkt)
            ten_dv = quy_tac["ten_dich_vu"]
            ds_tc_yeu_cau: Tuple[str, ...] = quy_tac["trieu_chung_bat_buoc"]

            # Đối chiếu với tập mệnh đề dương tính còn hiệu lực của bệnh nhân
            khop_ps: List[PhatBieu] = []
            tu_khoa_da_khop: List[str] = []
            for p_ev in ps_bang_chung_ls:
                nd_low = (p_ev.noi_dung or "").lower()
                for tc in ds_tc_yeu_cau:
                    if tc in nd_low:
                        if p_ev not in khop_ps:
                            khop_ps.append(p_ev)
                        if tc not in tu_khoa_da_khop:
                            tu_khoa_da_khop.append(tc)

            if khop_ps:
                luot_can_cu = sorted({int(t) for p_ev in khop_ps for t in (p_ev.bang_chung or [])})
                tag_str = " ".join(f"[T{t}]" for t in luot_can_cu) if luot_can_cu else f"[T{luot_order[0]}]"
                trich_ls = "; ".join(dict.fromkeys((p_ev.noi_dung or "").strip() for p_ev in khop_ps if p_ev.noi_dung))
                ket_qua_cls.append({
                    "dich_vu": ten_dv,
                    "tu_khoa_lenh": tu_khoa_cls,
                    "ma_dvkt": ma_dvkt,
                    "hop_le": True,
                    "cau_bien_luan": f"Chỉ định {ten_dv} hợp lệ dựa trên triệu chứng/dấu hiệu lâm sàng: {trich_ls} {tag_str}",
                    "luot_can_cu": luot_can_cu,
                    "ma_xml": "XML3",
                })
            else:
                canh_bao_msg = (
                    f"[CẢNH BÁO XUẤT TOÁN CLS - XML3/XML5]: Chỉ định '{ten_dv}' (Lượt {luot_order}) "
                    f"chưa có triệu chứng/dấu hiệu lâm sàng tương ứng trong Diễn biến bệnh (XML5) "
                    f"(cần có ít nhất một dấu hiệu chỉ điểm như: {', '.join(ds_tc_yeu_cau[:5])})."
                )
                ket_qua_cls.append({
                    "dich_vu": ten_dv,
                    "tu_khoa_lenh": tu_khoa_cls,
                    "ma_dvkt": ma_dvkt,
                    "hop_le": False,
                    "canh_bao": canh_bao_msg,
                    "goi_y_bo_sung": (
                        f"Hỏi bổ sung và ghi nhận triệu chứng lâm sàng chỉ điểm ({', '.join(ds_tc_yeu_cau[:4])}...) "
                        f"vào Diễn biến bệnh (XML5) trước khi ký chỉ định {ten_dv}."
                    ),
                    "luot_can_cu": luot_order,
                    "ma_xml": "XML3",
                })

        return ket_qua_cls

    @classmethod
    def kiem_duyet_ho_so(cls, ma_ca: str, ps: List[PhatBieu], hoi_thoai: str = "",
                         thong_tin_benh_nhan: Optional[Dict[str, Any]] = None) -> KetQuaTienKiemBHYT:
        ds_icd10 = cls.goi_y_icd10(ps, hoi_thoai)
        icd_chinh = ds_icd10[0] if ds_icd10 else None
        icd_kem_theo = ds_icd10[1:] if len(ds_icd10) > 1 else []
        tap_ma_icd = {x["ma_icd10"] for x in ds_icd10}

        canh_bao_bhyt: List[str] = []
        canh_bao_nhi: List[str] = []
        canh_bao_dong_tay: List[str] = []

        # Lấy danh sách mệnh đề thuốc còn đang dùng / kê đơn của bệnh nhân (loại bỏ thuốc đã ngừng & giả định)
        ps_thuoc = [
            p for p in ps
            if getattr(p, "chu_the_id", 0) == 0
            and getattr(p, "trang_thai", "còn hiệu lực") == "còn hiệu lực"
            and getattr(p, "tinh_huong", "thực tế") != "giả định"
            and not getattr(p, "phu_dinh", False)
            and not cls._la_thuoc_da_ngung(p)
            and (
                getattr(p, "thuoc", None)
                or any(t in (p.noi_dung or "").lower() for t in QUY_TAC_THUOC_ICD10_BHYT)
                or (_ttt.hoat_chat(p.noi_dung or "") is not None and "dị ứng" not in (p.noi_dung or "").lower())
            )
        ]

        # 1. Kiểm tra chéo chỉ định Thuốc (XML2) với Mã ICD-10 (XML1)
        for p in ps_thuoc:
            nd_thap = (p.noi_dung or "").lower()
            if "dị ứng" in nd_thap or "mẫn cảm" in nd_thap:
                continue
            ten_th = ((p.thuoc or {}).get("ten") or "").lower() if isinstance(getattr(p, "thuoc", None), dict) else ""
            chuoi_kiem = f"{ten_th} {nd_thap}"
            for hoat_chat, (ma_hop_le, giai_thich) in QUY_TAC_THUOC_ICD10_BHYT.items():
                if re.search(rf"(?i)(?<!\w){re.escape(hoat_chat)}e?(?!\w)", chuoi_kiem):
                    if not (tap_ma_icd & set(ma_hop_le)):
                        canh_bao_bhyt.append(
                            f"[CẢNH BÁO XUẤT TOÁN BHYT - QĐ 4750/QĐ-BYT]: Thuốc '{hoat_chat.capitalize()}' "
                            f"(Lượt {p.bang_chung}) chưa có mã ICD-10 tương ứng trong mục Chẩn đoán "
                            f"(Yêu cầu một trong các mã: {', '.join(ma_hop_le)}). {giai_thich}"
                        )

        # 1b. Boost 5: Kiểm tra chéo chỉ định Cận lâm sàng / DVKT (XML3/XML4) với Diễn biến lâm sàng (XML5)
        bien_luan_cls = cls.kiem_tra_chi_dinh_cls(ps, hoi_thoai)
        for muc_cls in bien_luan_cls:
            if not muc_cls.get("hop_le") and muc_cls.get("canh_bao"):
                canh_bao_bhyt.append(str(muc_cls["canh_bao"]))

        # 2. Kiểm tra thiếu diễn biến lâm sàng hoặc sinh hiệu bắt buộc trong XML1 / XML5
        if not ds_icd10:
            canh_bao_bhyt.append(
                "[CẢNH BÁO BHYT - BẢNG XML1]: Hồ sơ chưa xác định được mã bệnh ICD-10 chính (`MA_BENH`). "
                "Cần bổ sung nhận định chẩn đoán trước khi đẩy cổng giám định BHXH."
            )

        # 3. Kiểm tra liều Nhi khoa theo cân nặng (mg/kg/ngày) & Thông tư 26/2025/TT-BYT (< 72 tháng tuổi)
        can_nang = cls._tim_can_nang_kg(ps, hoi_thoai, thong_tin_benh_nhan)
        tuoi_bn: Optional[float] = None
        thang_tuoi: Optional[int] = None
        if isinstance(thong_tin_benh_nhan, dict):
            if thong_tin_benh_nhan.get("tuoi") is not None:
                try:
                    tuoi_bn = float(thong_tin_benh_nhan["tuoi"])
                except (ValueError, TypeError):
                    tuoi_bn = None
            thang_raw = (
                thong_tin_benh_nhan.get("thang_tuoi")
                if thong_tin_benh_nhan.get("thang_tuoi") is not None
                else thong_tin_benh_nhan.get("so_thang_tuoi")
            )
            if thang_raw is not None:
                try:
                    thang_tuoi = int(float(thang_raw))
                except (ValueError, TypeError):
                    thang_tuoi = None

        vb_tuoi = " ".join([p.noi_dung or "" for p in ps if getattr(p, "chu_the_id", 0) == 0] + [hoi_thoai or ""])
        if thang_tuoi is None:
            m_thang = re.search(r"(?i)\b(\d{1,2})\s*tháng(?:\s+tuổi)?\b", vb_tuoi)
            if m_thang and re.search(r"(?i)\b(tháng\s+tuổi|bé|cháu|con|trẻ|bệnh\s+nhi)\b", vb_tuoi):
                thang_tuoi = int(m_thang.group(1))
        if tuoi_bn is None:
            m_tuoi_tre = re.search(r"(?i)\b(?:bé|cháu|con|bệnh\s+nhi)(?:\s+nhà\s+(?:em|tôi))?\s+(\d{1,2})\s*tuổi\b", vb_tuoi)
            if m_tuoi_tre:
                tuoi_bn = float(m_tuoi_tre.group(1))

        tre_duoi_72_thang = (
            (tuoi_bn is not None and tuoi_bn < 6)
            or (thang_tuoi is not None and thang_tuoi < 72)
        )
        if tre_duoi_72_thang and can_nang is None and len(ps_thuoc) > 0:
            canh_bao_nhi.append(
                "[CẢNH BÁO BẮT BUỘC TT 26/2025/TT-BYT]: Trẻ dưới 72 tháng tuổi bắt buộc ghi Cân nặng (kg) "
                "trên đơn thuốc điện tử và hồ sơ khám để kiểm soát liều an toàn [cần bổ sung cân nặng]."
            )
        la_tre_em = (
            (can_nang is not None and can_nang < 40.0)
            or (tuoi_bn is not None and tuoi_bn < 15)
            or bool(re.search(r"(?i)\b(cháu\s+bé|bé\s+nhà|bệnh\s+nhi|\d+\s+tháng\s+tuổi)\b", hoi_thoai or ""))
        )
        if la_tre_em and can_nang and can_nang > 0:
            for p in ps:
                if (
                    getattr(p, "chu_the_id", 0) != 0
                    or getattr(p, "trang_thai", "còn hiệu lực") != "còn hiệu lực"
                    or getattr(p, "tinh_huong", "thực tế") == "giả định"
                    or getattr(p, "phu_dinh", False)
                    or cls._la_thuoc_da_ngung(p)
                ):
                    continue
                nd_thap = (p.noi_dung or "").lower()
                if "dị ứng" in nd_thap or "mẫn cảm" in nd_thap:
                    continue
                lieu_str = ((p.thuoc or {}).get("lieu") or "") if isinstance(getattr(p, "thuoc", None), dict) else ""
                chuoi_th = f"{nd_thap} {lieu_str}".lower()
                for ten_th, (max_lan, max_ngay, ghi_chu) in LIEU_TRAN_NHI_KHOA_MG_KG_NGAY.items():
                    if ten_th in chuoi_th:
                        m_mg = re.search(r"(\d+(?:[.,]\d+)?)\s*mg\b", chuoi_th)
                        if m_mg:
                            so_mg = float(m_mg.group(1).replace(",", "."))
                            mg_kg = round(so_mg / can_nang, 1)
                            if mg_kg > max_ngay:
                                canh_bao_nhi.append(
                                    f"[CẢNH BÁO QUÁ LIỀU NHI KHOA]: {ten_th.capitalize()} liều {so_mg:g}mg cho trẻ {can_nang:g}kg "
                                    f"tương đương {mg_kg} mg/kg (Vượt trần tối đa trong ngày {max_ngay} mg/kg/ngày!). {ghi_chu}"
                                )
                            elif mg_kg > max_lan:
                                canh_bao_nhi.append(
                                    f"[LƯU Ý LIỀU NHI KHOA THEO CÂN NẶNG]: {ten_th.capitalize()} {so_mg:g}mg trên trẻ {can_nang:g}kg "
                                    f"= {mg_kg} mg/kg/lần (Trần 1 lần uống là {max_lan} mg/kg). {ghi_chu}"
                                )

        # 4. Kiểm tra Đa thuốc Đông-Tây y & Trùng lặp hoạt chất Paracetamol
        toan_bo_vb = (hoi_thoai or "") + " " + " ".join(p.noi_dung or "" for p in ps)
        for m_dy in RE_THUOC_DONG_Y_NGAM.finditer(toan_bo_vb):
            cum = m_dy.group(0)
            msg = (
                f"[CẢNH BÁO ĐÔNG-TÂY Y KẾT HỢP]: Ghi nhận người bệnh dùng '{cum}'. "
                f"Cần cảnh giác nguy cơ chứa Corticoid trộn ngầm (gây suy thượng thận/loét dạ dày khi phối hợp NSAID) "
                f"hoặc kim loại nặng/Paracetamol không rõ hàm lượng."
            )
            if msg not in canh_bao_dong_tay:
                canh_bao_dong_tay.append(msg)

        cac_thuoc_para = {
            bd for bd in BIET_DUOC_CHUA_PARACETAMOL
            if re.search(rf"(?i)\b{re.escape(bd)}\b", toan_bo_vb)
        }
        if len(cac_thuoc_para) >= 2:
            canh_bao_dong_tay.append(
                f"[CẢNH BÁO TRÙNG LẶP HOẠT CHẤT PARACETAMOL]: Phát hiện đồng thời {len(cac_thuoc_para)} biệt dược "
                f"cùng chứa Paracetamol ({', '.join(sorted(cac_thuoc_para))}). Nguy cơ quá liều >4000mg/ngày gây độc tính gan cấp!"
            )

        # 5. Đóng gói cấu trúc dữ liệu chuẩn Quyết định 130/QĐ-BYT & 4750/QĐ-BYT (XML1, XML2, XML5)
        xml1 = {
            "MA_LK": ma_ca,
            "MA_BENH_CHINH": icd_chinh["ma_icd10"] if icd_chinh else "",
            "TEN_BENH_CHINH": icd_chinh["ten_benh_byt"] if icd_chinh else "",
            "MA_BENH_KT": ";".join(x["ma_icd10"] for x in icd_kem_theo),
            "CAN_NANG": can_nang,
        }
        xml2 = [
            {
                "MA_LK": ma_ca,
                "STT": idx + 1,
                "TEN_THUOC": (p.thuoc or {}).get("ten") if isinstance(getattr(p, "thuoc", None), dict) else p.noi_dung,
                "LIEU_DUNG": (p.thuoc or {}).get("lieu") if isinstance(getattr(p, "thuoc", None), dict) else None,
                "DUONG_DUNG": (p.thuoc or {}).get("duong_dung") if isinstance(getattr(p, "thuoc", None), dict) else None,
                "LUOT_BANG_CHUNG": p.bang_chung,
            }
            for idx, p in enumerate(ps_thuoc)
        ]
        ps_dien_bien = [
            p for p in ps
            if getattr(p, "chu_the_id", 0) == 0
            and getattr(p, "trang_thai", "còn hiệu lực") == "còn hiệu lực"
            and getattr(p, "tinh_huong", "thực tế") != "giả định"
        ]
        xml5 = [
            {
                "MA_LK": ma_ca,
                "STT": idx + 1,
                "DIEN_BIEN_LS": p.noi_dung,
                "MOC_THOI_GIAN": p.moc_thoi_gian,
                "LUOT_THOAI_GOC": p.bang_chung,
                "TRICH_DAN_NGUYEN_VAN": p.trich_dan,
            }
            for idx, p in enumerate(ps_dien_bien)
        ]

        return KetQuaTienKiemBHYT(
            ma_icd10_chinh=icd_chinh,
            ma_icd10_kem_theo=icd_kem_theo,
            canh_bao_xuat_toan_bhyt=canh_bao_bhyt,
            canh_bao_lieu_nhi_khoa=canh_bao_nhi,
            canh_bao_da_thuoc_dong_tay_y=canh_bao_dong_tay,
            bang_xml_130_4750={"XML1_TONG_HOP": xml1, "XML2_THUOC": xml2, "XML5_DIEN_BIEN_LS": xml5},
            dat_chuan_cdss_muc_6_7_tt54=True,
            bien_luan_chi_dinh_cls=bien_luan_cls,
        )


# ---------------------------------------------------------------------------
# 4. THƯỚC ĐO CHWER & TRUY NGƯỢC LỖI ĐA VÒNG (MULTI-LOOP ERROR ATTRIBUTION)
# ---------------------------------------------------------------------------
class ClinicalHarmWeightedEvaluator:
    """Đo lường sai số có trọng số rủi ro sinh mạng lâm sàng (CHWER) và
    quy kết ngược nguồn lỗi theo từng tầng của kiến trúc 5 tầng.
    """

    @staticmethod
    def tinh_chwer(danh_sach_du_doan: List[PhatBieu],
                   danh_sach_dap_an: List[PhatBieu]) -> Dict[str, Any]:
        """Tính Clinical Harm-Weighted Error Rate (CHWER).
        - Mệnh đề Dị ứng / Thuốc NTI có trọng số w = 1.0.
        - Thuốc thường w = 0.9; Chẩn đoán w = 0.8; Thời gian w = 0.6; Khác w = 0.3.
        """
        if not danh_sach_dap_an:
            return {"chwer": 0.0, "ser_khong_trong_so": 0.0, "tong_trong_so_dap_an": 0.0}

        tap_du_doan = {
            (getattr(p, "chu_the_id", 0), (p.noi_dung or "").strip().lower(), bool(getattr(p, "phu_dinh", False)))
            for p in danh_sach_du_doan
            if getattr(p, "trang_thai", "còn hiệu lực") == "còn hiệu lực"
        }

        tong_w = 0.0
        loi_w = 0.0
        so_loi = 0

        for g in danh_sach_dap_an:
            if getattr(g, "trang_thai", "còn hiệu lực") != "còn hiệu lực":
                continue
            loai = cong_rui_ro.loai_thong_tin(g)
            w = cong_rui_ro.MUC_NGHIEM_TRONG.get(loai, 0.3)
            tong_w += w
            khoa = (getattr(g, "chu_the_id", 0), (g.noi_dung or "").strip().lower(), bool(getattr(g, "phu_dinh", False)))
            if khoa not in tap_du_doan:
                loi_w += w
                so_loi += 1

        n_gold = max(1, sum(1 for g in danh_sach_dap_an if getattr(g, "trang_thai", "còn hiệu lực") == "còn hiệu lực"))
        return {
            "chwer": round(loi_w / max(1e-9, tong_w), 4),
            "ser_khong_trong_so": round(so_loi / n_gold, 4),
            "tong_trong_so_dap_an": round(tong_w, 2),
            "trong_so_loi": round(loi_w, 2),
        }

    @staticmethod
    def quy_ket_nguoc_tang_loi(thao_tac_bac_si: str,
                               menh_de_goc: Optional[Dict[str, Any]] = None,
                               menh_de_sua: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Quy kết ngược thao tác chỉnh sửa của bác sĩ về đúng Tầng gây lỗi (Tầng 0..4)
        để kiểm soát lỗi giữa các bước AI (Câu hỏi số 2 của Ban Giám khảo).
        """
        goc = menh_de_goc or {}
        sua = menh_de_sua or {}

        if thao_tac_bac_si == "sua_loi_thoai_asr":
            return {
                "tang_gay_loi": "Tầng 0: Nhận dạng tiếng nói & Tách người nói (ASR / Diarization)",
                "ma_tang": "STAGE_0_ASR",
                "mo_ta": "Bác sĩ sửa văn bản gỡ băng hoặc vai người nói của lượt thoại gốc."
            }
        if thao_tac_bac_si == "them_menh_de_bo_sot":
            return {
                "tang_gay_loi": "Tầng 1: Mô hình Trích xuất Mệnh đề Nguyên tử (SLM Extraction Omission)",
                "ma_tang": "STAGE_1_EXTRACTION_OMISSION",
                "mo_ta": "Bác sĩ xác nhận bổ sung mệnh đề bị mô hình Tầng 1 bỏ sót (được Tầng 4.5 phát hiện)."
            }
        if thao_tac_bac_si == "doi_chu_the" or (
            goc.get("subject") != sua.get("subject") and sua.get("subject") is not None
        ):
            return {
                "tang_gay_loi": "Tầng 2: Liên kết Thực thể & Phân giải Đại từ Xưng hô (Entity Attribution)",
                "ma_tang": "STAGE_2_ENTITY_ATTRIBUTION",
                "mo_ta": f"Bác sĩ đổi chủ thể từ '{goc.get('subject')}' sang '{sua.get('subject')}'."
            }
        if thao_tac_bac_si == "khoi_phuc_dinh_chinh":
            return {
                "tang_gay_loi": "Tầng 3: Máy trạng thái Cập nhật Đính chính & Diễn biến (FSM State Update)",
                "ma_tang": "STAGE_3_FSM_STATE",
                "mo_ta": "Bác sĩ thay đổi trạng thái hiệu lực/thay thế của chuỗi đính chính."
            }
        if thao_tac_bac_si == "duyet_menh_de_bi_chan":
            return {
                "tang_gay_loi": "Tầng 4: Khóa Bằng chứng K1–K7 & Cổng Rủi ro (Evidence Gate False Positive)",
                "ma_tang": "STAGE_4_GATE_FALSE_POSITIVE",
                "mo_ta": "Mệnh đề đúng nhưng bị Cổng K1–K7 giữ ở khay Cần xác nhận; bác sĩ đã xác nhận đưa vào thân hồ sơ."
            }
        return {
            "tang_gay_loi": "Tầng 1: Trích xuất Nội dung Chi tiết Lâm sàng (SLM Span Refinement)",
            "ma_tang": "STAGE_1_CONTENT_EDIT",
            "mo_ta": "Bác sĩ tinh chỉnh câu chữ hoặc chi tiết lâm sàng của mệnh đề."
        }


_CHU_THE_BENH_NHAN_CHUAN = {
    "bệnh nhân", "người bệnh", "tôi", "tui", "mình", "bản thân", "patient", "self",
    "trẻ", "bé", "em bé", "trẻ nhỏ", "bệnh nhi", "cháu", "cháu bé",
    "bé nhà em", "bé nhà tôi", "cháu nhà tôi", "cháu nhà em",
}


def _suy_chu_the_id(m: Dict[str, Any]) -> Tuple[int, str]:
    from src.phat_bieu import la_vai_nhan_vien

    ten_subj = str(m.get("subject") or m.get("ten_chu_the") or m.get("chu_the") or "").strip()
    if m.get("chu_the_id") is not None:
        try:
            return int(m["chu_the_id"]), ten_subj
        except (ValueError, TypeError):
            pass
    sec_low = str(m.get("section") or m.get("muc") or "").strip().upper()
    if "GIA ĐÌNH" in sec_low:
        return 1, ten_subj or "gia đình"
    if ten_subj:
        if la_vai_nhan_vien(ten_subj):
            return 0, ten_subj
        if ten_subj.lower() not in _CHU_THE_BENH_NHAN_CHUAN:
            return 1, ten_subj
    return 0, ten_subj


def _suy_tinh_huong(m: Dict[str, Any]) -> str:
    raw = str(m.get("tinh_huong") or m.get("situation") or "").strip().lower()
    if raw in ("giả định", "gia_dinh", "hypothetical", "conditional"):
        return "giả định"
    if raw in ("kế hoạch", "ke_hoach", "plan", "planned"):
        return "kế hoạch"
    return "thực tế"


def _suy_trang_thai(m: Dict[str, Any]) -> str:
    raw = str(m.get("trang_thai") or m.get("status") or "").strip().lower()
    if raw in ("bị thay thế", "bi_thay_the", "superseded", "replaced", "bo", "rejected", "cancelled"):
        return "bị thay thế"
    if raw in ("chưa giải quyết", "chua_giai_quyet", "unresolved", "conflict", "can_xac_nhan", "quarantine", "pending"):
        return "chưa giải quyết"
    # "than" = trang thai "thang" (qua thang, khong can xac nhan) cua giao dien web (api-contract.ts)
    if not raw or raw in ("còn hiệu lực", "con_hieu_luc", "than", "active", "current", "confirmed", "kept", "giu"):
        return "còn hiệu lực"
    # Gia tri la: KHONG ngam dinh la con hieu luc (fail-open) -> danh dau chua giai quyet
    return "chưa giải quyết"


def _suy_nguoi_noi(m: Dict[str, Any]) -> str:
    raw = str(m.get("nguoi_noi") or m.get("speaker") or "").strip().lower()
    if raw in ("bác sĩ", "bác sỹ", "bs", "doctor", "bac_si"):
        return "bác sĩ"
    if raw in ("điều dưỡng", "nurse", "dieu_duong", "y tá", "y sĩ"):
        return "điều dưỡng"
    if raw in ("người nhà", "family_member", "family", "nguoi_nha"):
        return "người nhà"
    if raw in ("bệnh nhân", "benh_nhan", "patient", "bn", "người bệnh"):
        return "bệnh nhân"
    sec_up = str(m.get("section") or m.get("muc") or "").strip().upper()
    if sec_up == "CHẨN ĐOÁN" and not raw:
        return "bác sĩ"
    if not raw:
        # Khong khai bao nguoi noi: giu mac dinh cu (benh nhan) cho tuong thich dau vao web
        return "bệnh nhân"
    # Gia tri la ("người khác", "other" hay rac): ghi ro la nguoi khac, khong ngam dinh benh nhan
    return "người khác"


def tien_kiem_bhyt_tu_du_lieu(
    menh_de_raw: List[Dict[str, Any]],
    hoi_thoai: str = "",
    thong_tin_benh_nhan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Hàm cầu nối gọn cho Node/API: nhận danh sách mệnh đề dict + hội thoại, trả về kết quả BHYTXmlPreChecker."""
    from src.phat_bieu import _doc_hanh_vi, _doc_thuoc

    ds_pb: List[PhatBieu] = []
    for idx, m in enumerate(menh_de_raw or [], start=1):
        if not isinstance(m, dict):
            continue
        td_raw = m.get("trich_dan") or m.get("quotes") or []
        if isinstance(td_raw, str):
            td_list = [td_raw] if td_raw else []
        else:
            td_list = [str(x) for x in td_raw if x]
        noi_dung_str = str(m.get("text") or m.get("noi_dung") or "")
        drug_str = str(m.get("drug") or "").strip()
        if drug_str and drug_str.lower() not in noi_dung_str.lower():
            noi_dung_str = f"{noi_dung_str} ({drug_str})".strip()

        chu_the_id, ten_chu_the = _suy_chu_the_id(m)
        tinh_huong = _suy_tinh_huong(m)
        trang_thai = _suy_trang_thai(m)
        nguoi_noi = _suy_nguoi_noi(m)
        thuoc_obj = _doc_thuoc(m)
        if thuoc_obj is None and drug_str:
            drug_status_raw = str(m.get("drugStatus") or m.get("trang_thai_dung") or "").strip().lower()
            tt_dung = "đã ngừng" if drug_status_raw in ("đã ngừng", "stopped", "discontinued") else None
            thuoc_obj = {
                "ten": drug_str, "lieu": None, "so_lan": None,
                "duong_dung": None, "bat_dau": None, "ngung": None,
                "trang_thai_dung": tt_dung,
            }

        ds_pb.append(
            PhatBieu(
                id=int(m.get("id") or idx),
                nguoi_noi=nguoi_noi,
                chu_the_id=chu_the_id,
                ten_chu_the=ten_chu_the,
                noi_dung=noi_dung_str,
                bang_chung=[int(x) for x in (m.get("evidenceTurns") or m.get("bang_chung") or [1])],
                phu_dinh=bool(m.get("negated", m.get("phu_dinh", False))),
                tinh_huong=tinh_huong,
                trang_thai=trang_thai,
                trich_dan=td_list,
                hanh_vi=_doc_hanh_vi(m),
                thuoc=thuoc_obj,
            )
        )
    kq_obj = BHYTXmlPreChecker.kiem_duyet_ho_so("web", ds_pb, hoi_thoai, thong_tin_benh_nhan=thong_tin_benh_nhan)
    kq = kq_obj.to_dict()
    ds_icd = []
    if kq.get("ma_icd10_chinh"):
        ds_icd.append(kq["ma_icd10_chinh"])
    ds_icd.extend(kq.get("ma_icd10_kem_theo") or [])

    goi_y = []
    for item in ds_icd:
        ma_icd = item.get("ma_icd10") or item.get("ma") or ""
        ten_icd = item.get("ten_benh_byt") or item.get("ten_benh") or item.get("ten") or ""
        khoa = item.get("chuyen_khoa") or item.get("khoa") or ""
        trich_dan_khop = ""
        for pb in ds_pb:
            if (
                getattr(pb, "chu_the_id", 0) == 0
                and getattr(pb, "trang_thai", "còn hiệu lực") == "còn hiệu lực"
                and getattr(pb, "tinh_huong", "thực tế") != "giả định"
                and not pb.phu_dinh
                and pb.noi_dung
                and any(kw in pb.noi_dung.lower() for m_code, _, _, kws in DANH_MUC_ICD10_BYT if m_code == ma_icd for kw in kws)
            ):
                trich_dan_khop = (pb.trich_dan[0] if pb.trich_dan else "") or pb.noi_dung
                break
        goi_y.append({"ma": ma_icd, "ten": ten_icd, "khoa": khoa, "trich_dan": trich_dan_khop})
    kq["icd10_chi_tiet"] = goi_y
    kq["canh_bao_xuat_toan"] = [
        {"thuoc": "BHYT", "ly_do": msg} for msg in (kq.get("canh_bao_xuat_toan_bhyt") or [])
    ]
    kq["goi_xml_1_5"] = xuat_goi_xml_1_5_qd130(
        ma_lk="web",
        ket_qua_bhyt=kq_obj,
        danh_sach_phat_bieu=ds_pb,
        thong_tin_benh_nhan=thong_tin_benh_nhan,
        hoi_thoai=hoi_thoai,
    )
    kq["doi_soat_thuoc_tt26"] = doi_soat_da_don_va_don_quoc_gia(
        ds_pb,
        hoi_thoai=hoi_thoai,
        thong_tin_benh_nhan=thong_tin_benh_nhan,
    )
    return kq


_SO_TU_CHU_VIET: Dict[str, float] = {
    "nửa": 0.5,
    "rưỡi": 1.5,
    "một": 1.0,
    "hai": 2.0,
    "ba": 3.0,
    "bốn": 4.0,
    "tư": 4.0,
    "năm": 5.0,
    "sáu": 6.0,
    "bảy": 7.0,
    "tám": 8.0,
    "chín": 9.0,
    "mười": 10.0,
    "mười bốn": 14.0,
    "mười lăm": 15.0,
}


def _doi_chu_hoac_so_sang_float(chuoi: str) -> Optional[float]:
    s = (chuoi or "").strip().lower()
    if not s:
        return None
    if s in _SO_TU_CHU_VIET:
        return _SO_TU_CHU_VIET[s]
    if "/" in s:
        phan = s.split("/", 1)
        try:
            mau = float(phan[1].strip().replace(",", "."))
            if mau > 0:
                return float(phan[0].strip().replace(",", ".")) / mau
        except (ValueError, TypeError):
            return None
    try:
        return float(s.replace(",", "."))
    except (ValueError, TypeError):
        return None


def _fmt_so_lieu(v: Optional[float]) -> Any:
    if v is None:
        return None
    return int(v) if float(v).is_integer() else round(float(v), 2)


def _phan_tich_dong_don_tt26(
    ten_thuoc: str,
    hoat_chat_chuan: Optional[str],
    thuoc_dict: Dict[str, Any],
    noi_dung: str,
    trich_dan_list: List[str],
    bang_chung: List[int],
) -> Dict[str, Any]:
    """Cấu trúc hóa 1 dòng đơn thuốc theo chuẩn Đơn thuốc điện tử quốc gia (Thông tư 26/2025/TT-BYT).
    Bất biến an toàn: KHÔNG bao giờ tự suy đoán hàm lượng, buổi uống hoặc tổng số lượng khi thiếu dữ kiện.
    """
    vb_gop = " | ".join(
        x for x in [
            noi_dung,
            str(thuoc_dict.get("lieu") or ""),
            str(thuoc_dict.get("so_lan") or ""),
            str(thuoc_dict.get("duong_dung") or ""),
            *trich_dan_list,
        ]
        if x
    )
    vb_low = vb_gop.lower()

    # 1. Hàm lượng (ví dụ: 500mg, 20 mg, 850mg, 100IU/ml)
    m_hl = re.search(
        r"(?i)\b(\d+(?:[.,]\d+)?\s*(?:mg|mcg|g|iu|ui|%)(?:\s*/\s*\d*(?:[.,]\d+)?\s*(?:mg|mcg|g|ml))?)\b",
        vb_gop,
    )
    ham_luong = re.sub(r"\s+", "", m_hl.group(1)) if m_hl else "[cần bổ sung]"

    # 2. Chia liều Sáng / Trưa / Chiều / Tối (chỉ điền khi văn bản nêu tường minh buổi dùng)
    mau_so = r"(\d+(?:[.,/]\d+)?|nửa|một|hai|ba|bốn)"
    mau_don_vi = r"(?:\s*(?:viên|gói|ống|nhát|giọt|ml|lọ|liều))?"

    def _tim_lieu_buoi(mau_buoi: str) -> Optional[float]:
        m_b = re.search(rf"(?i)\b(?:buổi\s+|mỗi\s+)?(?:{mau_buoi})\s+(?:uống\s+|dùng\s+|xịt\s+|tiêm\s+)?{mau_so}{mau_don_vi}\b", vb_gop)
        if m_b:
            return _doi_chu_hoac_so_sang_float(m_b.group(1))
        m_nguoc = re.search(rf"(?i)\b{mau_so}\s*(?:viên|gói|ống|nhát|giọt|ml)\s+(?:vào\s+)?(?:buổi\s+)?(?:{mau_buoi})\b", vb_gop)
        if m_nguoc:
            return _doi_chu_hoac_so_sang_float(m_nguoc.group(1))
        return None

    sang_v = _tim_lieu_buoi("sáng")
    trua_v = _tim_lieu_buoi("trưa")
    chieu_v = _tim_lieu_buoi("chiều")
    toi_v = _tim_lieu_buoi("tối|đêm|trước khi đi ngủ|trước ngủ")

    co_buoi_tuong_minh = any(v is not None for v in (sang_v, trua_v, chieu_v, toi_v))
    if co_buoi_tuong_minh:
        sang = _fmt_so_lieu(sang_v or 0.0)
        trua = _fmt_so_lieu(trua_v or 0.0)
        chieu = _fmt_so_lieu(chieu_v or 0.0)
        toi = _fmt_so_lieu(toi_v or 0.0)
        tong_don_vi_moi_ngay: Optional[float] = float((sang_v or 0.0) + (trua_v or 0.0) + (chieu_v or 0.0) + (toi_v or 0.0))
    else:
        sang = trua = chieu = toi = None
        tong_don_vi_moi_ngay = None
        # Kiểm tra xem có đủ cả số đơn vị mỗi lần VÀ số lần/ngày tường minh không ("1 viên x 2 lần/ngày", "ngày 2 lần mỗi lần 1 viên", "ngày uống 2 viên")
        m_nhan = re.search(
            rf"(?i)\b{mau_so}\s*(?:viên|gói|ống|nhát)\s*(?:x|×|\*)\s*{mau_so}\s*lần\s*(?:/|\s*một\s*|\s*trong\s*)?ngày\b",
            vb_gop,
        )
        m_moi_lan = re.search(rf"(?i)\bmỗi\s+lần\s+{mau_so}\s*(?:viên|gói|ống|nhát)\b", vb_gop)
        m_so_lan_ngay = re.search(
            rf"(?i)\b(?:ngày\s+(?:uống\s+|dùng\s+)?{mau_so}\s*lần|{mau_so}\s*lần\s*/\s*ngày)\b",
            vb_gop,
        )
        m_ngay_vien = re.search(rf"(?i)\bngày\s+(?:uống\s+|dùng\s+)?{mau_so}\s*(?:viên|gói|ống)\b", vb_gop)
        if m_nhan:
            a_v = _doi_chu_hoac_so_sang_float(m_nhan.group(1))
            b_v = _doi_chu_hoac_so_sang_float(m_nhan.group(2))
            if a_v is not None and b_v is not None:
                tong_don_vi_moi_ngay = a_v * b_v
        elif m_moi_lan and m_so_lan_ngay:
            a_v = _doi_chu_hoac_so_sang_float(m_moi_lan.group(1))
            b_str = m_so_lan_ngay.group(1) or m_so_lan_ngay.group(2)
            b_v = _doi_chu_hoac_so_sang_float(b_str)
            if a_v is not None and b_v is not None:
                tong_don_vi_moi_ngay = a_v * b_v
        elif m_ngay_vien:
            tong_don_vi_moi_ngay = _doi_chu_hoac_so_sang_float(m_ngay_vien.group(1))

    la_khi_can = bool(re.search(r"(?i)\bkhi\s+(?:cần|đau|sốt|khó\s+thở|ho)\b", vb_low))

    # 3. Số ngày dùng thuốc ("trong 5 ngày", "uống 7 ngày", "1 tuần" -> 7, "2 tuần" -> 14)
    so_ngay: Optional[int] = None
    m_ngay = re.search(
        r"(?i)(?:trong|uống|dùng|kéo\s+dài|đợt|x|×|,)\s*(\d+|mười\s+bốn|mười\s+lăm|mười|một|hai|ba|bốn|năm|sáu|bảy|tám|chín)\s*ngày\b",
        vb_gop,
    )
    if not m_ngay:
        m_ngay = re.search(
            r"(?i)\b(\d+|mười\s+bốn|mười\s+lăm|mười|một|hai|ba|bốn|năm|sáu|bảy|tám|chín)\s*ngày\b(?!\s*(?:một\s+lần|hai\s+lần|ba\s+lần|\d+\s*lần|uống|dùng|nay|trước|qua))",
            vb_gop,
        )
    m_tuan = re.search(r"(?i)(?<!ngừng\s)(?<!ngưng\s)\b(\d+|một|hai|ba|bốn)\s*tuần\b(?!\s*(?:nay|trước|qua))", vb_gop)
    m_thang_dt = re.search(r"(?i)(?:trong|uống|dùng)\s*(\d+|một|hai|ba)\s*tháng\b", vb_gop)

    if m_ngay:
        v_n = _doi_chu_hoac_so_sang_float(m_ngay.group(1))
        if v_n is not None and v_n > 0:
            so_ngay = int(round(v_n))
    elif m_tuan:
        v_t = _doi_chu_hoac_so_sang_float(m_tuan.group(1))
        if v_t is not None and v_t > 0:
            so_ngay = int(round(v_t * 7))
    elif m_thang_dt:
        v_th = _doi_chu_hoac_so_sang_float(m_thang_dt.group(1))
        if v_th is not None and v_th > 0:
            so_ngay = int(round(v_th * 30))

    # 4. Tổng số lượng: CHỈ tự tính khi cả tổng đơn vị mỗi ngày VÀ số ngày đều tường minh, không phải thuốc "khi cần"
    if (
        tong_don_vi_moi_ngay is not None
        and tong_don_vi_moi_ngay > 0
        and so_ngay is not None
        and so_ngay > 0
        and not la_khi_can
    ):
        tong_so_luong = _fmt_so_lieu(tong_don_vi_moi_ngay * so_ngay)
    else:
        tong_so_luong = None

    # 5. Đường dùng & Lời dặn ăn uống
    duong_dung = str(thuoc_dict.get("duong_dung") or "").strip()
    if not duong_dung:
        m_dd = re.search(r"(?i)\b(uống|xịt|bôi|nhỏ\s+mắt|nhỏ\s+mũi|nhỏ|tiêm|ngậm|hít|đặt)\b", vb_gop)
        duong_dung = m_dd.group(1).lower() if m_dd else "[cần bổ sung]"

    m_an = re.search(
        r"(?i)\b(trước\s+(?:bữa\s+)?ăn\s*\d*\s*(?:phút)?|sau\s+(?:bữa\s+)?ăn(?:\s+no)?|trong\s+bữa\s+ăn|lúc\s+đói|ngay\s+sau\s+ăn|trước\s+khi\s+(?:đi\s+)?ngủ)\b",
        vb_gop,
    )
    loi_dan_an_uong = m_an.group(1).strip() if m_an else "[cần bổ sung]"

    thieu: List[str] = []
    if ham_luong == "[cần bổ sung]":
        thieu.append("ham_luong")
    if not co_buoi_tuong_minh and tong_don_vi_moi_ngay is None:
        thieu.append("lieu_dung_trong_ngay")
    if so_ngay is None:
        thieu.append("so_ngay")
    if tong_so_luong is None:
        thieu.append("tong_so_luong")
    if duong_dung == "[cần bổ sung]":
        thieu.append("duong_dung")
    if loi_dan_an_uong == "[cần bổ sung]":
        thieu.append("loi_dan_an_uong")

    tags_bc = [f"[T{int(t)}]" for t in sorted({int(x) for x in (bang_chung or []) if int(x) > 0})]

    return {
        "ten_thuoc": ten_thuoc,
        "hoat_chat": hoat_chat_chuan or "[cần bổ sung]",
        "ham_luong": ham_luong,
        "sang": sang,
        "trua": trua,
        "chieu": chieu,
        "toi": toi,
        "so_ngay": so_ngay,
        "tong_so_luong": tong_so_luong,
        "duong_dung": duong_dung,
        "loi_dan_an_uong": loi_dan_an_uong,
        "bang_chung": tags_bc,
        "thieu_thong_tin": thieu,
    }


def doi_soat_da_don_va_don_quoc_gia(
    ps: List[PhatBieu],
    hoi_thoai: str = "",
    thong_tin_benh_nhan: Optional[Dict[str, Any]] = None,
    duoc_ly_ddi: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Boost 6: Đối soát đa đơn thuốc (Thuốc đang dùng ở nhà vs Đơn mới kê) & Cấu trúc hóa Đơn thuốc quốc gia TT 26/2025/TT-BYT."""
    thuoc_dang_dung_o_nha: List[Dict[str, Any]] = []
    don_thuoc_moi_tt26: List[Dict[str, Any]] = []
    tat_ca_muc_hoat_dong: List[Dict[str, Any]] = []

    for idx_p, raw_p in enumerate(ps or [], start=1):
        if isinstance(raw_p, dict):
            chu_the_id, ten_ct = _suy_chu_the_id(raw_p)
            trang_thai = _suy_trang_thai(raw_p)
            tinh_huong = _suy_tinh_huong(raw_p)
            nguoi_noi = _suy_nguoi_noi(raw_p)
            phu_dinh = bool(raw_p.get("phu_dinh", raw_p.get("negated", False)))
            noi_dung = str(raw_p.get("noi_dung") or raw_p.get("text") or "").strip()
            hanh_vi = str(raw_p.get("hanh_vi") or "")
            muc = str(raw_p.get("muc") or raw_p.get("section") or "").upper()
            thuoc_obj = raw_p.get("thuoc") if isinstance(raw_p.get("thuoc"), dict) else {}
            if not thuoc_obj and raw_p.get("drug"):
                thuoc_obj = {"ten": str(raw_p["drug"]).strip()}
            bc = [int(x) for x in (raw_p.get("bang_chung") or raw_p.get("luot_thoai") or raw_p.get("evidenceTurns") or [idx_p])]
            td_raw = raw_p.get("trich_dan") or raw_p.get("quotes") or []
            td_list = [td_raw] if isinstance(td_raw, str) else [str(x) for x in td_raw if x]
            da_ngung = (
                thuoc_obj.get("trang_thai_dung") == "đã ngừng"
                or any(kw in noi_dung.lower() for kw in ("đã ngừng", "ngừng dùng", "ngưng dùng", "đã ngưng"))
            )
        else:
            chu_the_id = getattr(raw_p, "chu_the_id", 0)
            trang_thai = getattr(raw_p, "trang_thai", "còn hiệu lực")
            tinh_huong = getattr(raw_p, "tinh_huong", "thực tế")
            nguoi_noi = getattr(raw_p, "nguoi_noi", "bệnh nhân")
            phu_dinh = bool(getattr(raw_p, "phu_dinh", False))
            noi_dung = str(getattr(raw_p, "noi_dung", "") or "").strip()
            hanh_vi = str(getattr(raw_p, "hanh_vi", "") or "")
            muc = str(getattr(raw_p, "muc", "") or "").upper()
            thuoc_obj = getattr(raw_p, "thuoc", None) or {}
            bc = list(getattr(raw_p, "bang_chung", None) or [])
            td_list = list(getattr(raw_p, "trich_dan", None) or [])
            da_ngung = BHYTXmlPreChecker._la_thuoc_da_ngung(raw_p)

        if chu_the_id != 0 or trang_thai != "còn hiệu lực" or phu_dinh or tinh_huong == "giả định" or da_ngung:
            continue
        nd_low = noi_dung.lower()
        if "dị ứng" in nd_low or "mẫn cảm" in nd_low:
            continue

        ten_th = str(thuoc_obj.get("ten") or "").strip()
        if not ten_th:
            m_rx = _ttt.regex_ten_thuoc().search(noi_dung)
            if m_rx:
                ten_th = m_rx.group(1).strip()
        if not ten_th:
            continue

        hc = _ttt.hoat_chat(ten_th) or _ttt.hoat_chat(noi_dung)
        tags_bc = [f"[T{int(t)}]" for t in sorted({int(x) for x in bc if int(x) > 0})]

        la_don_moi = (
            tinh_huong == "kế hoạch"
            or hanh_vi == "kế hoạch"
            or muc == "KẾ HOẠCH ĐIỀU TRỊ"
            or thuoc_obj.get("trang_thai_dung") == "được kê, chưa dùng"
            or (nguoi_noi == "bác sĩ" and muc != "THUỐC ĐANG DÙNG" and thuoc_obj.get("trang_thai_dung") != "đang dùng")
        )

        if la_don_moi:
            dong_tt26 = _phan_tich_dong_don_tt26(
                ten_thuoc=ten_th,
                hoat_chat_chuan=hc,
                thuoc_dict=thuoc_obj,
                noi_dung=noi_dung,
                trich_dan_list=td_list,
                bang_chung=bc,
            )
            don_thuoc_moi_tt26.append(dong_tt26)
            tat_ca_muc_hoat_dong.append({
                "nguon_don": "don_moi",
                "ten_thuoc": ten_th,
                "hoat_chat": hc,
                "bang_chung": tags_bc,
            })
        else:
            thuoc_dang_dung_o_nha.append({
                "ten_thuoc": ten_th,
                "hoat_chat": hc or "[cần bổ sung]",
                "lieu": thuoc_obj.get("lieu"),
                "so_lan": thuoc_obj.get("so_lan"),
                "duong_dung": thuoc_obj.get("duong_dung"),
                "trang_thai_dung": thuoc_obj.get("trang_thai_dung") or "đang dùng",
                "noi_dung_goc": noi_dung,
                "bang_chung": tags_bc,
            })
            tat_ca_muc_hoat_dong.append({
                "nguon_don": "thuoc_nha",
                "ten_thuoc": ten_th,
                "hoat_chat": hc,
                "bang_chung": tags_bc,
            })

    # Phát hiện trùng lặp hoạt chất giữa các biệt dược (thuốc nhà <-> đơn mới, hoặc nội bộ từng nhóm)
    theo_hc: Dict[str, List[Dict[str, Any]]] = {}
    for m_act in tat_ca_muc_hoat_dong:
        hc_key = m_act.get("hoat_chat")
        if hc_key:
            theo_hc.setdefault(hc_key.lower(), []).append(m_act)

    canh_bao_trung_hoat_chat: List[Dict[str, Any]] = []
    for hc_low, ds_trung in theo_hc.items():
        if len(ds_trung) < 2:
            continue
        tap_nguon = {x["nguon_don"] for x in ds_trung}
        if tap_nguon == {"thuoc_nha", "don_moi"}:
            pham_vi = "giua_thuoc_nha_va_don_moi"
        elif tap_nguon == {"thuoc_nha"}:
            pham_vi = "trong_thuoc_nha"
        else:
            pham_vi = "trong_don_moi"
        ds_ten = [x["ten_thuoc"] for x in ds_trung]
        ds_bc = sorted({b for x in ds_trung for b in x["bang_chung"]})
        canh_bao_trung_hoat_chat.append({
            "hoat_chat": hc_low,
            "cac_thuoc": ds_ten,
            "pham_vi": pham_vi,
            "bang_chung": ds_bc,
            "canh_bao": (
                f"[CẢNH BÁO TRÙNG HOẠT CHẤT ĐA ĐƠN]: Hoạt chất '{hc_low}' bị trùng lặp giữa "
                f"{', '.join(ds_ten)} ({', '.join(ds_bc) if ds_bc else 'cần rà soát'}) — nguy cơ quá liều tích lũy!"
            ),
        })

    return {
        "chuan_don_thuoc": "Thông tư 26/2025/TT-BYT",
        "thuoc_dang_dung_o_nha": thuoc_dang_dung_o_nha,
        "don_thuoc_moi_tt26": don_thuoc_moi_tt26,
        "canh_bao_trung_hoat_chat": canh_bao_trung_hoat_chat,
        "co_trung_hoat_chat": len(canh_bao_trung_hoat_chat) > 0,
        "tuong_tac_ddi_kem_theo": (duoc_ly_ddi or {}).get("canh_bao_tuong_tac", []) if isinstance(duoc_ly_ddi, dict) else [],
    }


def xuat_goi_xml_1_5_qd130(
    ma_lk: str,
    ket_qua_bhyt: Any,
    danh_sach_phat_bieu: List[PhatBieu],
    thong_tin_benh_nhan: Optional[Dict[str, Any]] = None,
    hoi_thoai: str = "",
) -> Dict[str, str]:
    """Xuất gói hồ sơ XML1–XML5 chuẩn Quyết định 130/QĐ-BYT & 4750/QĐ-BYT song song FHIR R4."""
    bn = thong_tin_benh_nhan or {}
    now_str = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    ma_lk_esc = _xml_escape(str(ma_lk or "LK_001"))
    ma_bn = _xml_escape(str(bn.get("id") or ma_lk or "BN_001"))
    ho_ten = _xml_escape(str(bn.get("ten") or bn.get("ho_ten") or "BENH_NHAN_AN_DANH"))
    gioi = "2" if "nữ" in str(bn.get("gioi_tinh", "")).lower() or bn.get("la_nu") else "1"

    def _lay_icd(item: Any, key: str, default: str = "") -> str:
        if isinstance(item, dict):
            return str(item.get(key) or default)
        return str(getattr(item, key, None) or default)

    chinh = getattr(ket_qua_bhyt, "ma_icd10_chinh", None)
    kem_theo = getattr(ket_qua_bhyt, "ma_icd10_kem_theo", None) or []
    ma_chinh = _xml_escape(_lay_icd(chinh, "ma_icd10", "R69") if chinh else "R69")
    ten_chinh = _xml_escape(_lay_icd(chinh, "ten_benh_byt", "Khám bệnh chưa rõ nguyên nhân") if chinh else "Khám bệnh chưa rõ nguyên nhân")
    ma_kem = _xml_escape(";".join(_lay_icd(x, "ma_icd10") for x in kem_theo if _lay_icd(x, "ma_icd10")))

    xml1 = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        "<TONG_HOP>\n"
        f"  <MA_LK>{ma_lk_esc}</MA_LK>\n"
        f"  <MA_BN>{ma_bn}</MA_BN>\n"
        f"  <HO_TEN>{ho_ten}</HO_TEN>\n"
        f"  <GIOI_TINH>{gioi}</GIOI_TINH>\n"
        f"  <MA_BENH>{ma_chinh}</MA_BENH>\n"
        f"  <MA_BENHKHAC>{ma_kem}</MA_BENHKHAC>\n"
        f"  <TEN_BENH>{ten_chinh}</TEN_BENH>\n"
        f"  <NGAY_VAO>{now_str}</NGAY_VAO>\n"
        f"  <NGAY_RA>{now_str}</NGAY_RA>\n"
        "  <KET_QUA_DTRI>1</KET_QUA_DTRI>\n"
        "  <TINH_TRANG_RV>1</TINH_TRANG_RV>\n"
        "</TONG_HOP>"
    )

    # XML2: Chi tiết thuốc (lọc bỏ thuốc đã ngừng, phủ định, giả định hoặc khác chủ thể)
    thuoc_items: List[str] = []
    stt_t = 0
    for pb in danh_sach_phat_bieu:
        if getattr(pb, "chu_the_id", 0) != 0 or getattr(pb, "phu_dinh", False):
            continue
        if getattr(pb, "trang_thai", "còn hiệu lực") != "còn hiệu lực":
            continue
        if getattr(pb, "tinh_huong", "thực tế") == "giả định":
            continue
        if BHYTXmlPreChecker._la_thuoc_da_ngung(pb):
            continue
        t_dict = getattr(pb, "thuoc", None)
        muc = getattr(pb, "muc", "") or ""
        if isinstance(t_dict, dict) or muc in ("THUỐC ĐANG DÙNG", "KẾ HOẠCH ĐIỀU TRỊ"):
            stt_t += 1
            ten_t = _xml_escape(str((t_dict.get("ten") if isinstance(t_dict, dict) else None) or pb.noi_dung or ""))
            lieu_t = _xml_escape(str((t_dict.get("lieu") if isinstance(t_dict, dict) else None) or ""))
            duong_t = _xml_escape(str((t_dict.get("duong_dung") if isinstance(t_dict, dict) else None) or "1.01"))
            thuoc_items.append(
                "  <CHI_TIET_THUOC>\n"
                f"    <MA_LK>{ma_lk_esc}</MA_LK>\n"
                f"    <STT>{stt_t}</STT>\n"
                f"    <TEN_THUOC>{ten_t}</TEN_THUOC>\n"
                f"    <HAM_LUONG>{lieu_t}</HAM_LUONG>\n"
                f"    <DUONG_DUNG>{duong_t}</DUONG_DUNG>\n"
                f"    <LIEU_DUNG>{lieu_t}</LIEU_DUNG>\n"
                f"    <NGAY_YL>{now_str}</NGAY_YL>\n"
                "  </CHI_TIET_THUOC>"
            )
    xml2 = (
        '<?xml version="1.0" encoding="utf-8"?>\n<CHITIEU_CHITIET_THUOC>\n<DSACH_CHI_TIET_THUOC>\n'
        + ("\n".join(thuoc_items) + "\n" if thuoc_items else "")
        + "</DSACH_CHI_TIET_THUOC>\n</CHITIEU_CHITIET_THUOC>"
    )

    # XML3: Dịch vụ kỹ thuật (Khám bệnh ngoại trú + toàn bộ chỉ định Cận lâm sàng / DVKT phát hiện được)
    dvkt_items: List[str] = [
        "  <CHI_TIET_DVKT>\n"
        f"    <MA_LK>{ma_lk_esc}</MA_LK>\n"
        "    <STT>1</STT>\n"
        "    <MA_DICH_VU>01.0001</MA_DICH_VU>\n"
        "    <TEN_DICH_VU>Khám bệnh ngoại trú</TEN_DICH_VU>\n"
        "    <SO_LUONG>1</SO_LUONG>\n"
        f"    <NGAY_YL>{now_str}</NGAY_YL>\n"
        "  </CHI_TIET_DVKT>"
    ]
    ds_cls_bhyt = (
        ket_qua_bhyt.get("bien_luan_chi_dinh_cls")
        if isinstance(ket_qua_bhyt, dict)
        else getattr(ket_qua_bhyt, "bien_luan_chi_dinh_cls", None)
    )
    if ds_cls_bhyt is None:
        ds_cls_bhyt = BHYTXmlPreChecker.kiem_tra_chi_dinh_cls(danh_sach_phat_bieu, hoi_thoai)
    for idx_dv, muc_dv in enumerate(ds_cls_bhyt or [], start=2):
        ma_dv = _xml_escape(str(muc_dv.get("ma_dvkt") or f"99.{idx_dv:04d}"))
        ten_dv = _xml_escape(str(muc_dv.get("dich_vu") or "Dịch vụ cận lâm sàng"))
        dvkt_items.append(
            "  <CHI_TIET_DVKT>\n"
            f"    <MA_LK>{ma_lk_esc}</MA_LK>\n"
            f"    <STT>{idx_dv}</STT>\n"
            f"    <MA_DICH_VU>{ma_dv}</MA_DICH_VU>\n"
            f"    <TEN_DICH_VU>{ten_dv}</TEN_DICH_VU>\n"
            "    <SO_LUONG>1</SO_LUONG>\n"
            f"    <NGAY_YL>{now_str}</NGAY_YL>\n"
            "  </CHI_TIET_DVKT>"
        )
    xml3 = (
        '<?xml version="1.0" encoding="utf-8"?>\n<CHITIEU_CHITIET_DVKT_VTYT>\n<DSACH_CHI_TIET_DVKT>\n'
        + "\n".join(dvkt_items) + "\n"
        + "</DSACH_CHI_TIET_DVKT>\n</CHITIEU_CHITIET_DVKT_VTYT>"
    )

    # XML4: Cận lâm sàng
    cls_items: List[str] = []
    xn_dict = bn.get("xet_nghiem") if isinstance(bn.get("xet_nghiem"), dict) else (
        bn.get("du_lieu_xet_nghiem") if isinstance(bn.get("du_lieu_xet_nghiem"), dict) else {}
    )
    for idx_cls, (k_xn, v_xn) in enumerate(xn_dict.items(), start=1):
        cls_items.append(
            "  <CHI_TIET_CLS>\n"
            f"    <MA_LK>{ma_lk_esc}</MA_LK>\n"
            f"    <STT>{idx_cls}</STT>\n"
            f"    <MA_CHI_SO>{_xml_escape(str(k_xn).upper())}</MA_CHI_SO>\n"
            f"    <TEN_CHI_SO>{_xml_escape(str(k_xn))}</TEN_CHI_SO>\n"
            f"    <GIA_TRI>{_xml_escape(str(v_xn))}</GIA_TRI>\n"
            f"    <NGAY_KQ>{now_str}</NGAY_KQ>\n"
            "  </CHI_TIET_CLS>"
        )
    xml4 = (
        '<?xml version="1.0" encoding="utf-8"?>\n<CHITIEU_CHITIET_CLS>\n<DSACH_CHI_TIET_CLS>\n'
        + ("\n".join(cls_items) + "\n" if cls_items else "")
        + "</DSACH_CHI_TIET_CLS>\n</CHITIEU_CHITIET_CLS>"
    )

    # XML5: Diễn biến lâm sàng (chỉ lấy mệnh đề còn hiệu lực, thực tế của chính bệnh nhân chu_the_id == 0)
    dien_bien_text = "; ".join(
        pb.noi_dung for pb in danh_sach_phat_bieu
        if getattr(pb, "chu_the_id", 0) == 0
        and getattr(pb, "trang_thai", "còn hiệu lực") == "còn hiệu lực"
        and getattr(pb, "tinh_huong", "thực tế") != "giả định"
        and pb.noi_dung
    ) or (hoi_thoai[:500] if hoi_thoai else "Khám ngoại trú")
    xml5 = (
        '<?xml version="1.0" encoding="utf-8"?>\n<CHITIEU_CHITIET_DIEN_BIEN_BENH>\n<DSACH_CHI_TIET_DIEN_BIEN_BENH>\n'
        "  <CHI_TIET_DIEN_BIEN_BENH>\n"
        f"    <MA_LK>{ma_lk_esc}</MA_LK>\n"
        "    <STT>1</STT>\n"
        f"    <DIEN_BIEN>{_xml_escape(dien_bien_text)}</DIEN_BIEN>\n"
        f"    <NGAY_YL>{now_str}</NGAY_YL>\n"
        "  </CHI_TIET_DIEN_BIEN_BENH>\n"
        "</DSACH_CHI_TIET_DIEN_BIEN_BENH>\n</CHITIEU_CHITIET_DIEN_BIEN_BENH>"
    )

    return {
        "chuan": "QD_130_4750_QD_BYT",
        "XML1": xml1,
        "XML2": xml2,
        "XML3": xml3,
        "XML4": xml4,
        "XML5": xml5,
    }


if __name__ == "__main__":
    import json
    import sys

    if "--precheck" in sys.argv:
        raw = sys.stdin.read().lstrip("\ufeff")
        data = json.loads(raw) if raw.strip() else {}
        tt_bn = data.get("thong_tin_benh_nhan") or data.get("patientInfo")
        out = tien_kiem_bhyt_tu_du_lieu(
            data.get("propositions") or [],
            data.get("transcript") or "",
            thong_tin_benh_nhan=tt_bn if isinstance(tt_bn, dict) else None,
        )
        print(json.dumps(out, ensure_ascii=False))
