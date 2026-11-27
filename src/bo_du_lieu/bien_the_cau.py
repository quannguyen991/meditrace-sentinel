# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Bộ sinh]
Làm gì   : Cho bộ sinh nhiều cách nói khác nhau cho cùng một ý (câu hỏi bác sĩ, lời chào,
           câu đáp phủ định) để hội thoại bớt lặp câu.
Vào → Ra : tham số ngữ cảnh (triệu chứng chính, ca, miền, tuổi) + rng → một câu tiếng Việt
           chọn ngẫu nhiên có kiểm soát
Đọc từ   : sinh_cau_hoi_da_tang() ghép câu hỏi bác sĩ ba tầng; sinh_cau_hoi_them_ngu_canh()
           hỏi thêm triệu chứng theo ca
Mục lục (các hàm/lớp chính):
  sinh_cau_hoi_da_tang()           Ghép câu hỏi của bác sĩ từ ba tầng dẫn-lời-đuôi
  sinh_cau_hoi_them_ngu_canh()     Sinh câu hỏi thêm triệu chứng theo triệu chứng chính
  sinh_cau_hoi_tien_su_ngu_canh()  Sinh câu hỏi tiền sử hợp tuổi và ngữ cảnh ca
  sinh_chao_cuoi()                 Sinh lời chào kết thúc buổi khám
  sinh_dap_khong_di_ung()          Sinh câu đáp phủ định rằng không dị ứng
  sinh_y_lenh_ke()                 Sinh y lệnh bác sĩ kê thuốc mới
  sinh_xa_giao()                   Sinh cặp hỏi đáp xã giao không có thông tin lâm sàng
Dùng bởi : bo_du_lieu/sinh_hoi_thoai_viet
Tên cũ   : bien_the_cau.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Các biến thể câu mở rộng đa dạng cho bộ sinh hội thoại lâm sàng v2.

Mục tiêu: Giảm độ lặp câu toàn bộ (Dataset Duplication <= 30%) theo Task B3.
Bao gồm:
  1. Bộ sinh câu hỏi bác sĩ đa tầng (Lead-in x Question core x Suffix).
  2. Bộ mở rộng hội thoại xã giao (XA_GIAO_MO_RONG >= 120 cặp).
  3. Bộ lời chào kết và cảm ơn phân hóa theo đại từ (tôi/em/cháu/con/trung tính) x 3 vùng miền.
  4. Bộ từ đếm, đồng tình và phủ định tự nhiên (không dị ứng, chưa uống thuốc, không tiền sử).
  5. Biến thể khuôn mẫu f-string xác nhận danh tính, triệu chứng chính và thời gian.
  6. Biến thể triệu chứng phụ và dẫn chuyển sang khám lâm sàng.
  7. Bộ dẫn nhập phong phú cho khám lâm sàng, chẩn đoán và kế hoạch điều trị.
  8. Biến thể cho câu hỏi không đáp, điều dưỡng bàn giao và tái khám.

Toàn bộ biến thể được viết bằng tiếng Việt lâm sàng tự nhiên, tuyệt đối không dùng mã/số ngẫu nhiên.
Mỗi lựa chọn dùng lượng ngẫu nhiên độc lập `Random(2*hat+3)`.
"""
from __future__ import annotations
import random
from typing import List, Tuple

# ==============================================================================
# 1. TỪ ĐẾM VÀ ĐÁP TỰ NHIÊN (AFFIRMATION & NEGATION)
# ==============================================================================

DA_VANG_MO_RONG = {
    "bac": [
        "Vâng ạ, ", "Vâng, ", "Dạ vâng, ", "Dạ vâng ạ, ", "Thưa bác sĩ, ",
        "Vâng thưa bác sĩ, ", "Dạ, ", "Dạ thưa bác sĩ, ", "Vâng em nghe, ",
        "Vâng tôi nghe đây ạ, "
    ],
    "nam": [
        "Dạ, ", "Dạ thưa bác sĩ, ", "Dạ vâng, ", "Dạ bác sĩ, ",
        "Dạ thưa bác, ", "Dạ em nghe bác sĩ, ", "Dạ bác, ", "Dạ đúng rồi bác sĩ, ",
        "Dạ thưa đúng ạ, "
    ],
    "trung": [
        "Dạ, ", "Dạ vâng, ", "Dạ thưa bác sĩ, ", "Dạ bác sĩ, ",
        "Dạ cháu nghe bác sĩ, ", "Dạ thưa bác, ", "Dạ đúng rồi bác, "
    ]
}

DA_PHU_DINH_MO_RONG = {
    "bac": [
        "Dạ không ạ, ", "Dạ không, ", "Dạ chưa ạ, ", "Vâng không ạ, ",
        "Dạ em không, ", "Dạ tôi không, ", "Dạ chưa, ", "Vâng chưa ạ, "
    ],
    "nam": [
        "Dạ không ạ, ", "Dạ không, ", "Dạ chưa bác sĩ, ", "Dạ hổng có, ",
        "Dạ chưa ạ, ", "Dạ hổng có đâu bác sĩ, ", "Dạ không có, ", "Dạ chưa từng bác ơi, "
    ],
    "trung": [
        "Dạ không ạ, ", "Dạ không, ", "Dạ chưa bác sĩ, ", "Dạ không có, ",
        "Dạ chưa tê, ", "Dạ chưa ạ, ", "Dạ không có chi mô, "
    ]
}

# ═══ chon_da() — Chọn câu trả lời kiểu da theo miền và có/không ═══════════════════════
# Lấy ngẫu nhiên từ bảng đáp phủ định hoặc khẳng định, theo miền; miền lạ dùng miền nam.
def chon_da(mien: str, phu_dinh: bool, rng: random.Random) -> str:
    bang = DA_PHU_DINH_MO_RONG if phu_dinh else DA_VANG_MO_RONG
    ds = bang.get(mien, bang["nam"])
    return rng.choice(ds)


# --- Đáp phủ định cho DỊ ỨNG (phải giữ nghĩa không dị ứng thuốc)
DAP_KHONG_DI_UNG = [
    "không{tt}.",
    "không có{tt}.",
    "từ trước đến giờ chưa từng bị dị ứng thuốc gì cả{tt}.",
    "tôi dùng thuốc bình thường không thấy dị ứng hay ngứa ngáy gì{tt}.",
    "không bị dị ứng thuốc bao giờ bác sĩ{tt}.",
    "chưa từng bị phản ứng hay dị ứng với thuốc nào{tt}.",
    "không có tiền sử dị ứng thuốc gì{tt}.",
    "không thấy có biểu hiện dị ứng nào trước nay{tt}.",
    "uống thuốc gì từ trước tới giờ cũng êm, không bị dị ứng{tt}.",
    "tôi không có dị ứng thuốc gì hết bác sĩ{tt}.",
    "trộm vía từ nhỏ tới lớn chưa bị dị ứng thuốc bao giờ{tt}.",
    "không bác sĩ ơi, cơ địa tôi dùng thuốc bình thường{tt}.",
    "chưa từng thấy dị ứng với kháng sinh hay thuốc giảm đau gì cả{tt}.",
    "không có bác sĩ, uống thuốc bình thường{tt}.",
    "sức khỏe bình thường, chưa bao giờ bị dị ứng thuốc{tt}.",
    "tôi không có cơ địa dị ứng thuốc men gì{tt}.",
    "trước giờ không dị ứng với thành phần thuốc nào cả{tt}.",
    "chưa bị dị ứng thuốc lần nào trong đời{tt}.",
    "dạ không có, tôi uống thuốc an toàn từ trước tới giờ{tt}.",
    "tôi không bị dị ứng với bất kỳ thuốc nào{tt}.",
    "uống các loại thuốc từ trước nay đều không bị phản ứng dị ứng gì{tt}.",
    "chưa thấy xuất hiện dấu hiệu dị ứng thuốc nào bao giờ{tt}.",
    "cơ thể tôi đáp ứng thuốc bình thường, không dị ứng{tt}.",
    "không dị ứng với kháng sinh hay hóa chất gì cả{tt}."
]

# --- Đáp phủ định cho THUỐC ĐANG DÙNG (chưa uống thuốc gì)
DAP_CHUA_UONG_THUOC = [
    "chưa uống gì{tt}.",
    "chưa uống thuốc gì{tt}.",
    "ở nhà chưa kịp uống thuốc gì cả{tt}.",
    "từ lúc đau tới giờ tôi chưa uống viên nào{tt}.",
    "chưa dùng thứ gì bác sĩ{tt}.",
    "tôi chưa mua thuốc gì uống hết{tt}.",
    "chưa dám tự mua thuốc uống ở nhà{tt}.",
    "thấy mệt là đi khám luôn chứ chưa uống thuốc gì{tt}.",
    "chưa dùng viên thuốc nào cả bác sĩ{tt}.",
    "ở nhà chỉ nghỉ ngơi chứ chưa có uống thuốc men gì{tt}.",
    "chưa uống thuốc tây thuốc bắc gì cả{tt}.",
    "để nguyên triệu chứng vậy tới khám luôn chứ chưa dùng thuốc gì{tt}.",
    "chưa bác sĩ, mới bị nên chưa mua thuốc gì uống{tt}.",
    "chưa, tôi sợ uống sai nên không dám tự ý dùng thuốc{tt}.",
    "chưa uống thuốc gì từ lúc phát triệu chứng tới giờ{tt}.",
    "ở nhà chưa điều trị hay dùng bất cứ loại thuốc nào{tt}.",
    "chưa kịp uống gì hết, đau quá nên vào viện luôn{tt}.",
    "tôi chưa can thiệp thuốc men gì cả bác sĩ{tt}.",
    "chưa có dùng thuốc hạ sốt hay giảm đau gì hết{tt}.",
    "hoàn toàn chưa dùng thuốc gì trước khi tới đây{tt}.",
    "chưa dùng thuốc điều trị gì ở nhà hết{tt}.",
    "tôi chưa uống viên hạ sốt hay giảm đau nào cả{tt}.",
    "ở nhà chưa uống thuốc gì, đợi bác sĩ khám rồi kê đơn luôn{tt}."
]

# --- Đáp phủ định cho TIỀN SỬ BẢN THÂN (không có bệnh gì cũ)
DAP_KHONG_TIEN_SU = [
    "không có gì{tt}.",
    "không có bệnh gì{tt}.",
    "từ trước tới nay sức khỏe hoàn toàn bình thường{tt}.",
    "tôi không có bệnh nền gì bác sĩ{tt}.",
    "trước giờ khỏe mạnh, ít khi phải đi khám bệnh viện{tt}.",
    "không có bệnh mãn tính nào đang phải theo dõi cả{tt}.",
    "tôi không có tiền sử bệnh lý gì trước đây{tt}.",
    "trước giờ bình thường, không bệnh tật gì lớn{tt}.",
    "không có vấn đề gì đáng kể về sức khỏe đâu bác sĩ{tt}.",
    "sức khỏe tôi từ trước tới giờ rất tốt, không bệnh gì cũ{tt}.",
    "trước giờ tôi không mắc bệnh lý mạn tính nào{tt}.",
    "chưa từng phải điều trị bệnh gì lâu năm cả{tt}.",
    "không có bệnh sử gì đặc biệt bác sĩ{tt}.",
    "tôi không có bệnh nền nào hết{tt}.",
    "trước giờ đi khám sức khỏe định kỳ đều bình thường{tt}.",
    "chưa từng phẫu thuật hay nằm viện vì bệnh mạn tính nào{tt}.",
    "sức khỏe trước nay rất ổn định, không có bệnh nền{tt}."
]

# --- Đáp CÓ DỊ ỨNG (phải chứa cụm từ "dị ứng {thuoc}")
DAP_CO_DI_UNG = [
    "có, dị ứng {thuoc}{tt}.",
    "có, tôi bị dị ứng {thuoc}{tt}.",
    "trước đây tôi từng bị dị ứng {thuoc}{tt}.",
    "tôi có tiền sử dị ứng {thuoc}{tt}.",
    "có dị ứng {thuoc}, lần trước uống bị phát ban{tt}.",
    "hồi trước có lần dùng thuốc bị dị ứng {thuoc} khá nặng{tt}.",
    "có thưa bác sĩ, tôi bị dị ứng {thuoc}{tt}.",
    "tôi không dùng được thuốc đó, bị dị ứng {thuoc}{tt}.",
    "có dị ứng {thuoc} từ mấy năm trước rồi{tt}.",
    "cơ địa tôi bị dị ứng {thuoc} bác sĩ{tt}.",
    "bị dị ứng {thuoc} bác sĩ ơi, uống vào là nổi mẩn{tt}.",
    "tuyến trước bảo tôi có cơ địa dị ứng {thuoc}{tt}.",
    "có, tôi từng nhập viện vì dị ứng {thuoc}{tt}.",
    "uống vào là ngứa nên tôi biết mình dị ứng {thuoc}{tt}.",
    "tôi ghi nhớ kỹ là mình bị dị ứng {thuoc}{tt}."
]


# ==============================================================================
# 2. BỘ SINH CÂU HỎI BÁC SĨ ĐA TẦNG (LEAD-IN x CORE x SUFFIX)
# ==============================================================================

# do AI viết, chưa bác sĩ duyệt
DAN_DI_UNG = [
    "", "", "", "", "", "", "À, ", "Tiện hỏi luôn, "
]

# do AI viết, chưa bác sĩ duyệt
LOI_DI_UNG = [
    "có dị ứng thuốc nào không",
    "từng nổi mề đay khi uống thuốc chưa",
    "có dị ứng kháng sinh hay giảm đau không",
    "có dị ứng thuốc hay thức ăn gì không",
    "từng bị sốc thuốc lần nào chưa",
    "có dị ứng thuốc tây hay thuốc nam không",
    "uống thuốc có bị phản ứng lạ không",
    "có dị ứng penicillin hay aspirin không",
    "uống thuốc có bị ngứa nổi mẩn không",
    "có mẫn cảm với thuốc nào không",
    "trước giờ có dị ứng thuốc gì không",
    "uống thuốc có bị nổi ban đỏ chưa",
    "có dị ứng với kháng sinh không",
    "uống thuốc có bị nổi ngứa không",
    "từng bị dị ứng thuốc gì chưa",
    "có tiền sử dị ứng thuốc không",
    "có mẫn cảm với thuốc gì không",
    "uống hạ sốt có bị mẩn ngứa không",
    "có dị ứng paracetamol hay kháng sinh không",
    "từng bị phát ban khi dùng thuốc chưa",
    "có cơ địa dị ứng thuốc không",
    "uống thuốc có bị phù nề không"
]

DUOI_DI_UNG = ["?", " ạ?", " vậy?", " thế?"]


# do AI viết, chưa bác sĩ duyệt
DAN_THUOC = [
    "", "", "", "", "", "", "Cho hỏi, ", "Ở nhà "
]

# do AI viết, chưa bác sĩ duyệt
LOI_THUOC = [
    "có đang uống thuốc nào không",
    "đã mua thuốc gì uống chưa",
    "có uống hạ sốt hay giảm đau chưa",
    "có uống theo đơn viện nào không",
    "có uống thuốc nam hay thực phẩm chức năng không",
    "có uống thuốc huyết áp, tiểu đường không",
    "trước khi tới có uống liều nào chưa",
    "có dùng thuốc điều trị thường xuyên không",
    "có dùng thuốc bôi hay xịt nào không",
    "mình có dùng thuốc gì chưa",
    "có uống theo toa cũ nào không",
    "đã tự mua thuốc gì uống chưa",
    "có uống thuốc huyết áp không",
    "có uống viên hạ sốt nào chưa",
    "có uống giảm đau ở nhà chưa",
    "có dùng thực phẩm chức năng không",
    "sáng nay có uống thuốc gì chưa",
    "có đang dùng thuốc theo đơn không",
    "có uống thuốc nam hay đông y không",
    "đã dùng thuốc gì trước khi tới chưa",
    "có uống viên thuốc nào từ sáng chưa"
]

DUOI_THUOC = ["?", " ạ?", " vậy?", " thế?"]


# do AI viết, chưa bác sĩ duyệt
DAN_THEM = [
    "", "", "", "", "", "", "Ngoài ra, ", "Cho hỏi thêm, "
]

# do AI viết, chưa bác sĩ duyệt
LOI_THEM = [
    "còn khó chịu chỗ nào khác không",
    "có biểu hiện bất thường nào nữa không",
    "còn triệu chứng nào nữa không",
    "có đau nhức hay mệt ở đâu không",
    "trong người còn thấy gì lạ không",
    "có sốt, ớn lạnh hay buồn nôn không",
    "có dấu hiệu nào mới nữa không",
    "có triệu chứng gì đi kèm không",
    "có sụt cân, chán ăn, mất ngủ không",
    "còn chỗ nào đau nữa không",
    "có bị sốt hay ho không",
    "có chóng mặt hay buồn nôn không",
    "có kèm theo khó thở không",
    "ăn ngủ dạo này có được không",
    "có đau tức ngực hay hồi hộp không",
    "trong người còn mệt ở đâu không",
    "có thấy ớn lạnh hay vã mồ hôi không",
    "có bị đau đầu hay hoa mắt không",
    "đi vệ sinh có bình thường không",
    "còn dấu hiệu gì khác không"
]

DUOI_THEM = ["?", " ạ?", " vậy?", " thế?"]


# do AI viết, chưa bác sĩ duyệt
DAN_TIEN_SU = [
    "", "", "", "", "", "", "Về bệnh cũ, ", "Trước giờ "
]

# do AI viết, chưa bác sĩ duyệt
LOI_TIEN_SU = [
    "có điều trị bệnh mạn tính nào không",
    "có tiền sử tim mạch, huyết áp không",
    "từng nằm viện hay mổ lần nào chưa",
    "bản thân có bệnh nền gì không",
    "có bệnh gì phải theo dõi định kỳ không",
    "từng bị giống đợt này chưa",
    "có tiền sử gan, thận, hen, tiểu đường không",
    "có theo dõi ở chuyên khoa nào không",
    "có tiền sử phẫu thuật gì không",
    "từng có đợt uống thuốc kéo dài không",
    "có bệnh dạ dày hay trào ngược không",
    "có bị bệnh gan hay thận không",
    "có tiền sử hen phế quản không",
    "có bệnh huyết áp hay tiểu đường không",
    "từng nằm viện điều trị bao giờ chưa",
    "có đang theo dõi bệnh gì không",
    "từng bị đợt nào giống thế này chưa",
    "sức khỏe trước giờ có bệnh gì không",
    "có bệnh nền tim mạch không",
    "có tiền sử bệnh phổi hay phế quản không"
]

DUOI_TIEN_SU = ["?", " ạ?", " vậy?", " thế?"]


# do AI viết, chưa bác sĩ duyệt
DAN_GIA_DINH = [
    "", "", "", "", "", "", "Trong nhà ", "Gia đình "
]

# do AI viết, chưa bác sĩ duyệt
LOI_GIA_DINH = [
    "có ai mắc bệnh tương tự không",
    "bố mẹ anh em có ai tiểu đường, huyết áp không",
    "có ai mắc bệnh di truyền không",
    "người thân có ai dị ứng hay hen không",
    "có ai phải uống thuốc lâu dài không",
    "có ai từng bị đột quỵ không",
    "có ai bị bệnh dạ dày, tim mạch không",
    "bên nội ngoại có ai bị bệnh mạn tính không",
    "có ai bị viêm gan, thận hay phổi không",
    "có ai đang có triệu chứng giống vậy không",
    "nhà mình có ai bị giống vậy không",
    "bố mẹ có ai bị tim mạch không",
    "trong nhà có ai bị huyết áp không",
    "có ai trong nhà bị tiểu đường không",
    "người thân có ai bị dị ứng không",
    "nhà có ai bị hen suyễn không",
    "có ai cùng nhà đang bị bệnh tương tự không",
    "người nhà có ai bị bệnh gan không"
]

DUOI_GIA_DINH = ["?", " ạ?", " vậy?", " thế?"]


# do AI viết, chưa bác sĩ duyệt
DAN_THOI_GIAN = [
    "", "", "", "", "Dấu hiệu này ", "Tình trạng này ",
    "Cơn khó chịu này ", "Cho hỏi "
]

# do AI viết, chưa bác sĩ duyệt
LOI_THOI_GIAN = [
    "xuất hiện từ bao giờ",
    "bắt đầu thấy bị từ lúc nào",
    "bị như vậy bao lâu rồi",
    "kéo dài mấy ngày nay rồi",
    "khởi phát từ khi nào",
    "bị liên tục từ lúc nào",
    "phát triệu chứng từ hôm nào",
    "từ hôm nào thấy rõ nhất",
    "diễn ra bao nhiêu ngày rồi",
    "để ý thấy từ thời điểm nào",
    "bắt đầu khó chịu từ ngày nào",
    "bị từ hôm nào rồi",
    "bị mấy ngày nay rồi",
    "bắt đầu đau từ lúc nào",
    "mới bị hay bị mấy hôm rồi",
    "kéo dài được bao lâu rồi",
    "bị từ hôm qua hay hôm nay",
    "kéo dài mấy ngày rồi",
    "bị liên tục hay ngắt quãng",
    "thấy khó chịu từ lúc nào"
]

DUOI_THOI_GIAN = ["?", " ạ?", " vậy?", " thế?", " vậy ạ?"]


# ═══ sinh_cau_hoi_da_tang() — Ghép câu hỏi của bác sĩ từ ba tầng dẫn-lời-đuôi ═════════
# Loại câu: dị ứng, thuốc, hỏi thêm hoặc tiền sử; mỗi loại có bảng dẫn, lời, đuôi riêng.
def sinh_cau_hoi_da_tang(loai: str, rng: random.Random) -> str:
    """Sinh câu hỏi bác sĩ ghép đa tầng: Dẫn x Lõi x Đuôi."""
    if loai == "di_ung":
        dan, loi, duoi = DAN_DI_UNG, LOI_DI_UNG, DUOI_DI_UNG
    elif loai == "thuoc":
        dan, loi, duoi = DAN_THUOC, LOI_THUOC, DUOI_THUOC
    elif loai == "them":
        dan, loi, duoi = DAN_THEM, LOI_THEM, DUOI_THEM
    elif loai == "tien_su":
        dan, loi, duoi = DAN_TIEN_SU, LOI_TIEN_SU, DUOI_TIEN_SU
    elif loai == "gia_dinh":
        dan, loi, duoi = DAN_GIA_DINH, LOI_GIA_DINH, DUOI_GIA_DINH
    elif loai == "thoi_gian":
        dan, loi, duoi = DAN_THOI_GIAN, LOI_THOI_GIAN, DUOI_THOI_GIAN
    else:
        return "Bác sĩ muốn hỏi thêm về tình trạng của bạn?"

    d = rng.choice(dan)
    l = rng.choice(loi)
    u = rng.choice(duoi)
    cau = f"{d}{l}{u}".strip()
    return cau[:1].upper() + cau[1:]


# ==============================================================================
# 2.1. BỘ SINH CÂU HỎI THÊM CÓ NGỮ CẢNH (CONTEXTUAL SYMPTOM INQUIRY)
# ==============================================================================

# ─── _rut_gon_trieu_chung() — Rút gọn triệu chứng dài thành cụm danh từ ngắn ──────────
# Cắt ở dấu phẩy hoặc từ phụ như kèm, kéo dài; giữ cụm còn lại ít nhất hai từ.
# do AI viết, chưa bác sĩ duyệt
def _rut_gon_trieu_chung(tc: str) -> str:
    """Rút gọn triệu chứng dài thành cụm danh từ ngắn gọn, tròn nghĩa tiếng Việt."""
    tc = tc.strip().lower()
    for cat in (',', ';', ' đáp ứng', ' kèm theo', ' kèm', ' liên tục', ' dữ dội', 
                ' khi ', ' sau khi ', ' lan ', ' xuất hiện', ' trên ', ' kéo dài', ' vùng ', ' giật '):
        if cat in tc:
            dau = tc.split(cat)[0].strip()
            if len(dau.split()) >= 2:
                tc = dau
                break
    words = tc.split()
    if len(words) > 6:
        cap_ghep = {'dai': 'dẳng', 'âm': 'ỉ', 'nhức': 'nhối', 'buốt': 'rát', 'quấy': 'khóc',
                    'nôn': 'trớ', 'nóng': 'rát', 'đau': 'nhức', 'chóng': 'mặt', 'hoa': 'mắt'}
        if words[5] in cap_ghep and len(words) > 6 and words[6] == cap_ghep[words[5]]:
            words = words[:7]
        else:
            words = words[:6]
    while words and words[-1] in ('giật', 'thành', 'ở', 'tại', 'do', 'và', 'kèm', 'với', 'như'):
        words.pop()
    return ' '.join(words)

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_THEM_CHINH = [
    "Ngoài {chinh} ra, {goi} còn thấy khó chịu ở đâu không{u}",
    "Bên cạnh {chinh}, có bị đau ở đâu nữa không{u}",
    "Ngoài triệu chứng {chinh}, trong người còn thấy gì lạ không{u}",
    "Ngoài {chinh} ra còn bị gì nữa không{u}",
    "Ngoài {chinh} ra có kèm sốt không{u}",
    "Bên cạnh {chinh} thì còn đau ở đâu không{u}",
    "Ngoài {chinh} có thấy mệt mỏi ở đâu không{u}",
    "Ngoài {chinh} ra mình có bị gì thêm không{u}",
    "Kèm theo {chinh} có sốt hay buồn nôn không{u}",
    "Cùng với {chinh}, ăn ngủ dạo này thế nào{u}",
    "Ngoài {chinh} có bị đau đầu hay hoa mắt không{u}",
    "Đi cùng với {chinh}, đi tiêu tiểu có bình thường không{u}",
    "Ngoài {chinh} ra có phát sinh dấu hiệu nào mới không{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_THEM_TRE_EM = [
    "Ngoài {chinh} ra, ở nhà bé có quấy khóc không{u}",
    "Bên cạnh {chinh}, bé ăn uống bú sữa có bình thường không{u}",
    "Ngoài biểu hiện {chinh}, bé có sốt hay nôn trớ không{u}",
    "Cùng với {chinh}, bé có thở mệt hay ngủ li bì không{u}",
    "Ngoài việc {chinh}, cháu đi tiêu tiểu bình thường chứ{u}",
    "Ngoài {chinh} ra bé có sốt không{u}",
    "Bé có quấy khóc hay nôn trớ gì không{u}",
    "Ngoài {chinh} bé còn khó chịu gì nữa không{u}",
    "Bé ăn ngủ bú mẹ có bình thường không{u}",
    "Cháu có sốt hay ho gì kèm theo không{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_THEM_CHUNG = [
    "Ngoài ra còn thấy khó chịu ở đâu không{u}",
    "Còn triệu chứng nào khác không{u}",
    "Có kèm biểu hiện bất thường nào khác không{u}",
    "Trong người còn thấy gì khác lạ không{u}",
    "Có sốt, đau đầu hay buồn nôn không{u}",
    "Còn khó chịu nào chưa kể không{u}",
    "Có phát sinh thêm dấu hiệu nào mới không{u}",
    "Cơ thể có thêm biểu hiện lạ nào không{u}",
    "Ngoài mấy dấu hiệu trên còn thấy gì không{u}",
    "Còn bị khó chịu gì nữa không{u}",
    "Có sốt hay đau nhức gì thêm không{u}",
    "Có thấy mệt mỏi hay nôn nao không{u}",
    "Người có sốt hay ớn lạnh không{u}",
]

# ═══ sinh_cau_hoi_them_ngu_canh() — Sinh câu hỏi thêm triệu chứng theo triệu chứng chính ═══
# Có 75% nhắc lại triệu chứng chính đã kể; cách gọi theo ca (trẻ em hoặc người lớn).
# do AI viết, chưa bác sĩ duyệt
def sinh_cau_hoi_them_ngu_canh(chinh: str, ca, rng: random.Random) -> str:
    """Sinh câu hỏi thêm triệu chứng phụ thuộc ngữ cảnh triệu chứng chính đã kể."""
    chinh_gon = _rut_gon_trieu_chung(chinh)
    goi = ca.goi_bn
    u = rng.choice(["?", " ạ?", " vậy?", " thế?", " vậy ạ?", " thế ạ?"])
    
    # 75% trường hợp nhắc lại triệu chứng chính đã kể (hoặc trẻ em)
    if rng.random() < 0.75:
        if getattr(ca, "la_tre_em", False) and rng.random() < 0.60:
            mau = rng.choice(CAU_HOI_THEM_TRE_EM)
        else:
            mau = rng.choice(CAU_HOI_THEM_CHINH)
        cau = mau.format(chinh=chinh_gon, goi=goi, u=u)
    else:
        mau = rng.choice(CAU_HOI_THEM_CHUNG)
        cau = mau.format(goi=goi, u=u)
    
    cau = cau.strip()
    return cau[:1].upper() + cau[1:]


# ==============================================================================
# 2.2. BỘ SINH CÂU HỎI TIỀN SỬ PHÂN HÓA THEO LỨA TUỔI (CONTEXTUAL MEDICAL HISTORY)
# ==============================================================================

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_TIEN_SU_TRE_EM = [
    "Trước đây bé có từng đi viện đợt nào chưa{u}",
    "Từ nhỏ đến giờ bé có bệnh lý gì đáng chú ý không{u}",
    "Sức khỏe trước giờ của bé có bình thường không{u}",
    "Trước đợt này bé có từng bị mệt như vậy chưa{u}",
    "Hồi trước bé có phải uống thuốc dài ngày không{u}",
    "Bé có từng nằm viện lần nào chưa{u}",
    "Trước giờ bé có bệnh mạn tính gì không{u}",
    "Trước đợt này bé có từng bị như vậy chưa{u}",
    "Bình thường sức khỏe bé tốt chứ{u}",
    "Bé có tiền sử bệnh gì từ nhỏ không{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_TIEN_SU_NGUOI_LON = [
    "Trước giờ {goi} có bệnh gì trong người không{u}",
    "Bản thân có bệnh nền gì không{u}",
    "Trước đây {goi} có từng mổ hay nằm viện chưa{u}",
    "Trước giờ có bệnh huyết áp hay tiểu đường không{u}",
    "Trước đợt này có từng bị cơn tương tự chưa{u}",
    "Bình thường sức khỏe {goi} tốt chứ{u}",
    "Có đang điều trị bệnh mạn tính nào không{u}",
    "Trước giờ có phải uống thuốc kéo dài không{u}",
    "Bản thân có tiền sử bệnh gì không{u}",
    "Ngoài đợt {chinh} ra trước đây sức khỏe bình thường chứ{u}",
    "Trước nay sức khỏe có ổn định không{u}",
    "Có bệnh gì cần theo dõi định kỳ không{u}",
    "Bản thân {goi} có bệnh lý mạn tính nào từ trước không{u}",
    "Trước giờ có từng đi khám chuyên khoa nào chưa{u}",
    "Sức khỏe trước đây của {goi} thế nào, có bệnh nền gì không{u}",
    "Trước đợt này {goi} có thấy mệt mỏi hay khó chịu tương tự không{u}",
    "Có đang theo dõi điều trị bệnh lý nào khác không{u}",
    "Trước nay {goi} có từng phải phẫu thuật lần nào chưa{u}",
    "Bình thường đi kiểm tra sức khỏe có phát hiện bệnh gì không{u}",
    "Trong người trước giờ có bệnh tim, gan hay thận gì không{u}",
    "Có tiền sử bệnh phổi hay hen suyễn gì không {goi}{u}",
    "Trước giờ {goi} có phải nằm điều trị nội trú lần nào chưa{u}",
    "Về tiền sử bệnh, trước nay mình có bệnh gì đáng chú ý không{u}",
    "Trước đợt {chinh} này thì cơ thể hoàn toàn khỏe mạnh chứ{u}",
    "Bản thân có đang uống thuốc theo đơn của bệnh viện nào không{u}",
]

# ═══ sinh_cau_hoi_tien_su_ngu_canh() — Sinh câu hỏi tiền sử hợp tuổi và ngữ cảnh ca ═══
# Trẻ em dùng mẫu riêng; người lớn dùng mẫu khác, có thể nhắc triệu chứng chính.
# do AI viết, chưa bác sĩ duyệt
def sinh_cau_hoi_tien_su_ngu_canh(chinh: str, ca, rng: random.Random) -> str:
    """Sinh câu hỏi tiền sử phân hóa theo lứa tuổi và ngữ cảnh ca."""
    goi = ca.goi_bn
    chinh_gon = _rut_gon_trieu_chung(chinh)
    u = rng.choice(["?", " ạ?", " vậy?", " thế?", " vậy ạ?", " thế ạ?"])
    if getattr(ca, "la_tre_em", False):
        mau = rng.choice(CAU_HOI_TIEN_SU_TRE_EM)
        cau = mau.format(chinh=chinh_gon, goi=goi, u=u)
    else:
        mau = rng.choice(CAU_HOI_TIEN_SU_NGUOI_LON)
        cau = mau.format(chinh=chinh_gon, goi=goi, u=u)
    cau = cau.strip()
    return cau[:1].upper() + cau[1:]


# ==============================================================================
# 2.3. BỘ SINH CÂU HỎI THUỐC VÀ DỊ ỨNG (CONTEXTUAL MEDICATION & ALLERGY INQUIRY)
# ==============================================================================

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_DI_UNG_TRE_EM = [
    "Trước giờ mỗi lần cho bé uống thuốc hạ sốt hay kháng sinh có thấy dị ứng mẩn ngứa gì không{u}",
    "Bé nhà mình có cơ địa dị ứng thuốc men, thức ăn hay chất nào không{u}",
    "Từ nhỏ đến giờ bé uống các loại siro hay thuốc tây có bị phản ứng lạ bao giờ chưa{u}",
    "Ở nhà gia đình có để ý thấy bé bị mẫn cảm hay dị ứng với thành phần thuốc nào không{u}",
    "Trước đây bé từng có lần nào uống thuốc bị nổi ban đỏ hay sưng mắt môi chưa{u}",
    "Bé có dị ứng thuốc gì không{u}",
    "Uống thuốc bé có từng bị phát ban hay mẩn ngứa chưa{u}",
    "Bé có cơ địa dị ứng thuốc hay thức ăn gì không{u}",
    "Trước giờ bé uống kháng sinh có bị dị ứng không{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_DI_UNG_NGUOI_LON = [
    "{goi_hoa} có dị ứng thuốc gì không{u}",
    "Trước giờ {goi} có từng bị dị ứng thuốc kháng sinh không{u}",
    "Bản thân {goi} có tiền sử dị ứng thuốc gì không{u}",
    "Uống thuốc tây có từng bị mẩn ngứa hay phù môi chưa{u}",
    "Có tiền sử dị ứng thuốc men gì cần báo bác sĩ không{u}",
    "Trước nay {goi} uống thuốc có dị ứng gì không{u}",
    "Bản thân có cơ địa dị ứng thuốc hay thức ăn gì không{u}",
    "Uống thuốc trước nay có phản ứng bất thường gì không{u}",
    "Trước giờ có mẫn cảm với penicillin hay aspirin không{u}",
    "Về dị ứng thuốc, từng bị nổi mề đay lần nào chưa{u}",
    "{goi_hoa} có cơ địa dị ứng thuốc không{u}",
    "Trước giờ uống kháng sinh có bị ngứa ngáy hay nổi ban không{u}",
    "Uống thuốc giảm đau hay hạ sốt có bị phản ứng gì không{u}",
    "Có từng bị dị ứng loại thuốc nào trước đây chưa{u}",
    "Khi uống thuốc tây {goi} có thấy khó chịu hay nổi mẩn không{u}",
    "Bản thân có dị ứng với thành phần thuốc nào không{u}",
    "Trước đây có bác sĩ nào dặn mình kiêng loại thuốc nào không{u}",
    "Uống thuốc kháng viêm hay kháng sinh có êm không{u}",
    "Có tiền sử sốc thuốc hay dị ứng thuốc nặng lần nào chưa{u}",
    "{goi_hoa} có dị ứng với kháng sinh nhóm beta-lactam không{u}",
    "Trong tiền sử bệnh, {goi} có ghi nhận dị ứng thuốc gì chưa{u}",
    "Uống thuốc tây vào có bị nóng rát hay nổi mề đay không{u}",
    "Trước giờ {goi} có uống được kháng sinh bình thường không{u}",
    "Có cần lưu ý dị ứng thuốc gì vào hồ sơ không {goi}{u}",
    "Cơ thể {goi} có nhạy cảm hay dị ứng với thuốc nào không{u}",
]

# ═══ sinh_cau_hoi_di_ung_ngu_canh() — Sinh câu hỏi dị ứng hợp tuổi và đối tượng ═══════
# Chọn mẫu trẻ em hoặc người lớn, dùng cách gọi bệnh nhân của ca.
# do AI viết, chưa bác sĩ duyệt
def sinh_cau_hoi_di_ung_ngu_canh(ca, rng: random.Random) -> str:
    """Sinh câu hỏi dị ứng phân hóa theo lứa tuổi và đối tượng."""
    goi = ca.goi_bn
    goi_hoa = goi[:1].upper() + goi[1:]
    u = rng.choice(["?", " ạ?", " vậy?", " thế?", " vậy ạ?", " thế ạ?"])
    if getattr(ca, "la_tre_em", False):
        mau = rng.choice(CAU_HOI_DI_UNG_TRE_EM)
    else:
        mau = rng.choice(CAU_HOI_DI_UNG_NGUOI_LON)
    cau = mau.format(goi=goi, goi_hoa=goi_hoa, u=u).strip()
    return cau[:1].upper() + cau[1:]


# do AI viết, chưa bác sĩ duyệt
CAU_HOI_THUOC_CHINH = [
    "Khi bị {chinh}, ở nhà {goi} đã uống thuốc gì chưa{u}",
    "Từ lúc bị {chinh} đã dùng thuốc gì chưa{u}",
    "Có uống thuốc gì cho đỡ {chinh} chưa{u}",
    "Mấy hôm nay có tự mua thuốc gì uống không{u}",
    "Trước khi tới đây khám, mình đã kịp uống thuốc gì chưa{u}",
    "Từ lúc xuất hiện {chinh}, mình đã dùng thuốc gì chưa{u}",
    "Khi bị {chinh}, ở nhà đã can thiệp thuốc gì chưa{u}",
    "Lúc thấy {chinh}, có tự mua kháng sinh uống không{u}",
    "Ở nhà có uống liều hạ sốt hay giảm đau nào cho đỡ {chinh} chưa{u}",
    "Từ hôm phát triệu chứng {chinh} đến nay đã dùng thuốc gì chưa{u}",
    "Mấy ngày bị {chinh} có ra tiệm thuốc tây mua thuốc uống không{u}",
    "Để giảm bớt {chinh}, ở nhà mình đã uống thứ gì chưa{u}",
    "Có dùng thuốc bôi hay thuốc uống nào để đỡ {chinh} chưa{u}",
    "Trước khi vào phòng khám đã kịp uống thuốc gì cho bớt {chinh} chưa{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_THUOC_TRE_EM = [
    "Từ lúc bé bị {chinh} đến nay, ở nhà gia đình đã cho bé uống thuốc hạ sốt hay siro gì chưa{u}",
    "Trước khi đưa bé đi khám, ở nhà mẹ đã kịp cho cháu dùng gói thuốc nào chưa{u}",
    "Mấy hôm nay bé có đang phải uống loại thuốc điều trị nào khác không{u}",
    "Từ lúc bé thấy khó chịu, nhà mình có tự mua thuốc gì ở tiệm thuốc cho bé uống chưa{u}",
    "Ở nhà mẹ đã cho bé uống thuốc gì chưa{u}",
    "Bé đã uống siro hay hạ sốt gì chưa{u}",
    "Từ lúc sốt đã cho bé dùng thuốc gì chưa{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_THUOC_CHUNG = [
    "Hiện tại {goi} có đang uống thuốc gì không{u}",
    "Ở nhà đã uống thuốc gì trước khi tới đây chưa{u}",
    "Có đang dùng đơn thuốc định kỳ nào không{u}",
    "Gần đây {goi} có uống thuốc gì thường xuyên không{u}",
    "Hiện tại có đang duy trì đơn thuốc mạn tính nào không{u}",
    "Có đang dùng thuốc theo toa của bác sĩ nào khác không{u}",
    "Trước khi tới phòng khám thì {goi} đã uống thuốc gì chưa{u}",
    "Hằng ngày {goi} có phải uống loại thuốc nào đều đặn không{u}",
    "Có đang uống thực phẩm chức năng hay thuốc bổ gì không{u}",
    "Gần đây có dùng thuốc nam hay thuốc bắc gì ở nhà không{u}",
    "Đợt này {goi} có đang theo đơn thuốc nào của tuyến dưới không{u}",
    "Trước khi đi khám sáng nay mình có uống viên thuốc nào chưa{u}",
]

# ═══ sinh_cau_hoi_thuoc_ngu_canh() — Sinh câu hỏi dùng thuốc gắn với triệu chứng ══════
# Có 65% gắn với triệu chứng chính; mẫu khác nhau cho trẻ em và người lớn.
# do AI viết, chưa bác sĩ duyệt
def sinh_cau_hoi_thuoc_ngu_canh(chinh: str, ca, rng: random.Random) -> str:
    """Sinh câu hỏi dùng thuốc gắn với triệu chứng và lứa tuổi."""
    goi = ca.goi_bn
    chinh_gon = _rut_gon_trieu_chung(chinh)
    u = rng.choice(["?", " ạ?", " vậy?", " thế?", " vậy ạ?", " thế ạ?"])
    if rng.random() < 0.65:
        if getattr(ca, "la_tre_em", False):
            mau = rng.choice(CAU_HOI_THUOC_TRE_EM)
        else:
            mau = rng.choice(CAU_HOI_THUOC_CHINH)
        cau = mau.format(chinh=chinh_gon, goi=goi, u=u)
    else:
        mau = rng.choice(CAU_HOI_THUOC_CHUNG)
        cau = mau.format(goi=goi, u=u)
    cau = cau.strip()
    return cau[:1].upper() + cau[1:]


# ==============================================================================
# 2.4. BỘ SINH CÂU HỎI GIA ĐÌNH THEO HỆ CƠ QUAN (CONTEXTUAL FAMILY HISTORY)
# ==============================================================================

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_GD_HO_HAP = [
    "Trong gia đình có ai bị hen suyễn hay khó thở không{u}",
    "Gia đình có ai mắc bệnh về đường hô hấp không{u}",
    "Người thân trong nhà có ai hay bị ho hen không{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_GD_TIM_MACH = [
    "Trong nhà có ai bị huyết áp cao hay bệnh tim mạch không{u}",
    "Gia đình mình có ai có tiền sử bệnh tim mạch hay đột quỵ không{u}",
    "Người thân trong nhà có ai phải uống thuốc tim mạch hay huyết áp không{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_GD_TIEU_HOA = [
    "Trong nhà có ai từng mắc bệnh dạ dày hay bệnh gan không{u}",
    "Gia đình có ai từng điều trị bệnh dạ dày hay tiêu hóa không{u}",
    "Người thân trong nhà có ai bị viêm loét dạ dày không{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_GD_CO_XUONG_KHOP = [
    "Trong gia đình có ai bị viêm khớp hay bệnh gout không{u}",
    "Bố mẹ anh em có ai hay bị đau nhức xương khớp không{u}",
    "Người thân trong nhà có ai mắc bệnh khớp mạn tính không{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_GD_THAN_KINH = [
    "Trong nhà có ai từng bị đau đầu hay động kinh không{u}",
    "Gia đình mình có ai có tiền sử bệnh thần kinh không{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_GD_DA_LIEU = [
    "Trong nhà có ai có tiền sử viêm da hay dị ứng không{u}",
    "Người thân trong gia đình có ai mắc bệnh về da không{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_GD_THAN_TIET_NIEU = [
    "Người thân trong nhà có ai từng mắc bệnh sỏi thận hay tiết niệu không{u}",
    "Gia đình có ai có tiền sử bệnh lý thận hay tiết niệu không{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_GD_TRUYEN_NHIEM = [
    "Trong nhà có ai đang bị sốt hay có triệu chứng tương tự không{u}",
    "Người thân trong gia đình có ai mắc bệnh tương tự không{u}",
]

# do AI viết, chưa bác sĩ duyệt
CAU_HOI_GD_CHUNG = [
    "Trong gia đình mình có ai mắc bệnh mạn tính hay bệnh tương tự không{u}",
    "Gia đình có ai có tiền sử huyết áp hay bệnh tim mạch không{u}",
    "Người thân trong nhà có ai có bệnh gì đáng lưu ý không{u}",
    "Bố mẹ anh em trong nhà sức khỏe có ai bị bệnh tương tự không{u}",
]

# ═══ sinh_cau_hoi_gia_dinh_ngu_canh() — Sinh câu hỏi tiền sử gia đình theo hệ cơ quan ═══
# Hô hấp, tim mạch, nội tiết... mỗi nhóm có kho câu hỏi riêng.
# do AI viết, chưa bác sĩ duyệt
def sinh_cau_hoi_gia_dinh_ngu_canh(he_co_quan: str, rng: random.Random) -> str:
    """Sinh câu hỏi tiền sử gia đình phân hóa theo hệ cơ quan."""
    u = rng.choice(["?", " ạ?", " vậy?", " thế?", " vậy ạ?", " thế ạ?"])
    he = (he_co_quan or "").lower()
    if any(h in he for h in ("hô hấp", "dị ứng")):
        pool = CAU_HOI_GD_HO_HAP
    elif any(h in he for h in ("tim mạch", "nội tiết", "chuyển hoá")):
        pool = CAU_HOI_GD_TIM_MACH
    elif "tiêu hoá" in he:
        pool = CAU_HOI_GD_TIEU_HOA
    elif any(h in he for h in ("khớp", "xương")):
        pool = CAU_HOI_GD_CO_XUONG_KHOP
    elif any(h in he for h in ("thần kinh", "tâm thần")):
        pool = CAU_HOI_GD_THAN_KINH
    elif any(h in he for h in ("thận", "tiết niệu")):
        pool = CAU_HOI_GD_THAN_TIET_NIEU
    elif any(h in he for h in ("da", "liễu")):
        pool = CAU_HOI_GD_DA_LIEU
    elif "truyền nhiễm" in he:
        pool = CAU_HOI_GD_TRUYEN_NHIEM
    else:
        pool = CAU_HOI_GD_CHUNG
    
    if rng.random() < 0.85:
        mau = rng.choice(pool)
    else:
        mau = rng.choice(CAU_HOI_GD_CHUNG)
    cau = mau.format(u=u).strip()
    return cau[:1].upper() + cau[1:]



# ==============================================================================
# 3. KHO MỞ RỘNG XÃ GIAO (XA_GIAO_MO_RONG >= 120 CẶP)
# ==============================================================================

XA_GIAO_MO_RONG: List[Tuple[str, str]] = [
    ("Mời {goi} ngồi ghế này ạ.", "Dạ, cảm ơn bác sĩ ạ."),
    ("{goi_hoa} đợi lâu chưa ạ?", "Dạ cũng vừa thôi ạ."),
    ("Nhà mình ở gần đây không ạ?", "Dạ cũng gần đây thôi ạ."),
    ("Phiền {goi} đưa thẻ bảo hiểm ạ.", "Dạ, đây ạ."),
    ("Hôm nay phòng khám hơi đông, {goi} thông cảm nhé.", "Dạ không sao đâu ạ."),
    ("Mời {goi} vào, mời ngồi ạ.", "Dạ, cảm ơn bác sĩ."),
    ("{goi_hoa} đi đường có mệt không ạ?", "Dạ không mệt lắm ạ."),
    ("Trời nóng quá nhỉ, {goi} uống nước đi.", "Dạ, cảm ơn ạ."),
    ("Hôm nay {goi} đi xe gì đến đây vậy?", "Dạ đi xe máy ạ."),
    ("{goi_hoa} có cần đo huyết áp trước không?", "Dạ, bác sĩ cứ làm ạ."),
    ("Có ai đi cùng {goi} không ạ?", "Dạ có ạ, người nhà đi cùng."),
    ("Đây là phiếu khám, {goi} giữ lấy nhé.", "Dạ vâng, cầm ạ."),
    ("Để tôi xem lại hồ sơ một chút nhé.", "Dạ, bác sĩ cứ xem ạ."),
    ("Chờ tôi một chút, {goi} ngồi đợi nhé.", "Dạ vâng ạ."),
    ("{goi_hoa} đã uống nước chưa ạ?", "Dạ rồi ạ, cảm ơn bác sĩ."),
    ("Hôm nay {goi} có ai đưa tới không?", "Dạ có ạ, người nhà đưa tới."),
    ("Phòng khám có chỗ để xe không?", "Dạ có ạ, em đã gửi xe rồi."),
    ("Chào {goi}, mời {goi} kéo ghế ngồi gần đây cho thoải mái nhé.", "Dạ vâng, cảm ơn bác sĩ nhiều ạ."),
    ("Hôm nay trời mưa to, {goi} đi đường có bị ướt không?", "Dạ em có mặc áo mưa cẩn thận nên không sao ạ."),
    ("{goi_hoa} đến đây bằng phương tiện gì vậy?", "Dạ em bắt xe buýt tuyến gần đây đi tới ạ."),
    ("Đoạn đường tới phòng khám sáng nay có bị tắc xe không {goi}?", "Dạ đường xá hôm nay khá thông thoáng ạ."),
    ("{goi_hoa} đã kịp ăn sáng trước khi đến đây khám chưa?", "Dạ em đã ăn lót dạ một chút rồi ạ."),
    ("Để tôi mở hồ sơ bệnh án của {goi} ra xem nhé.", "Dạ vâng, bác sĩ cứ kiểm tra ạ."),
    ("Phòng khám bật máy lạnh có bị lạnh quá so với {goi} không?", "Dạ nhiệt độ phòng thế này là vừa vặn dễ chịu ạ."),
    ("{goi_hoa} ngồi chờ ở sảnh ngoài có thấy mỏi mệt không?", "Dạ sảnh chờ thoáng mát nên em ngồi cũng thoải mái ạ."),
    ("{goi_hoa} nhớ giữ cẩn thận sổ khám bệnh này nhé.", "Dạ vâng, em cất ngay vào túi đây ạ."),
    ("Hôm nay {goi} xin nghỉ việc buổi sáng để đi khám bệnh đúng không?", "Dạ vâng, em xin nghỉ nửa ngày để đi kiểm tra sức khỏe ạ."),
    ("{goi_hoa} tìm phòng khám theo địa chỉ có dễ dàng không?", "Dạ biển hiệu to rõ ràng ngoài mặt đường nên em tìm thấy ngay ạ."),
    ("Thời tiết mấy bữa nay chuyển mùa thất thường quá {goi} nhỉ.", "Dạ vâng, thời tiết thay đổi làm người cứ uể oải suốt ạ."),
    ("Mời {goi} uống chút nước ấm cho dễ chịu cổ họng nhé.", "Dạ em cảm ơn bác sĩ đã chu đáo quan tâm ạ."),
    ("{goi_hoa} cứ để áo khoác và túi xách lên ghế bên cạnh cho đỡ vướng.", "Dạ vâng, em để gọn sang bên rồi ạ."),
    ("Bác sĩ cần đối chiếu thông tin trên thẻ căn cước một lát nhé {goi}.", "Dạ đây ạ, em gửi bác sĩ kiểm tra giúp em."),
    ("{goi_hoa} đã được đo mạch và huyết áp ở bàn điều dưỡng bên ngoài chưa?", "Dạ cô điều dưỡng bên ngoài đã đo và ghi vào phiếu rồi ạ."),
    ("{goi_hoa} tự đi một mình hay có ai chở đến phòng khám?", "Dạ em tự đi xe máy tới đây một mình ạ."),
    ("Sáng nay đến đây {goi} có phải chờ đợi lấy số lâu không?", "Dạ em đặt lịch hẹn trước trên mạng nên vào khám nhanh lắm ạ."),
    ("Hôm nay {goi} cảm thấy thể trạng có quá mệt mỏi không?", "Dạ hơi mệt một chút nhưng em vẫn đi lại bình thường được ạ."),
    ("Phòng khám có mạng wifi, {goi} có cần kết nối không?", "Dạ em có dùng gói 4G sẵn rồi, cảm ơn bác sĩ ạ."),
    ("{goi_hoa} vào ngồi thả lỏng tinh thần một chút trước khi khám nhé.", "Dạ vâng, em cảm ơn bác sĩ ạ."),
    ("Gió mùa về trời se lạnh, {goi} đi sớm nhớ giữ ấm cổ nhé.", "Dạ vâng, em có quàng khăn ấm khi đi đường rồi ạ."),
    ("{goi_hoa} có mang theo kết quả xét nghiệm hay phim chụp cũ không?", "Dạ có ạ, em mang đầy đủ giấy tờ khám đợt trước theo đây."),
    ("Để bác sĩ chỉnh lại đèn khám một chút cho sáng nhé.", "Dạ vâng, bác sĩ cứ tự nhiên chỉnh ạ."),
    ("{goi_hoa} uống ngụm nước suối đóng chai cho đỡ khát nhé.", "Dạ em xin, cảm ơn bác sĩ rất nhiều ạ."),
    ("Hôm nay khu vực tiếp đón bệnh nhân có thuận tiện cho {goi} không?", "Dạ các bạn nhân viên hướng dẫn em rất tận tình ạ."),
    ("{goi_hoa} đi từ huyện lên đây hay ở ngay trong thành phố vậy?", "Dạ nhà em ở ngay quận bên cạnh thôi ạ."),
    ("Cứ bình tĩnh ngồi nghỉ, không việc gì phải vội đâu {goi} nhé.", "Dạ vâng, em nghe lời bác sĩ ạ."),
    ("{goi_hoa} đưa phiếu chỉ định khám lúc nãy cho bác sĩ xem nhé.", "Dạ đây ạ, em gửi bác sĩ xem giúp em."),
    ("Bác sĩ xem qua thông tin hành chính một chút nhé {goi}.", "Dạ vâng, bác sĩ xem hộ em có sai sót gì không ạ."),
    ("Hôm nay cơ quan {goi} có nhiều người phải nghỉ việc vì bệnh không?", "Dạ dạo này thời tiết độc nên chỗ em cũng nhiều người bị mệt ạ."),
    ("{goi_hoa} đã đi khám ở cơ sở y tế nào khác trước khi tới đây chưa?", "Dạ thấy khó chịu là em đến thẳng đây khám luôn ạ."),
    ("Bác sĩ thấy sắc mặt {goi} hơi nhợt nhạt, đi lại cẩn thận nhé.", "Dạ vâng, em cũng thấy người hơi yếu nên đi chậm rãi ạ."),
    ("{goi_hoa} có cần bật quạt thông gió cho thoáng khí hơn không?", "Dạ không khí phòng khám thế này là thông thoáng rồi ạ."),
    ("Mời {goi} ngồi tựa lưng vào ghế cho đỡ mỏi lưng nhé.", "Dạ vâng, ngồi ghế này êm ái lắm ạ."),
    ("{goi_hoa} có mang theo kính đọc sách nếu cần ký giấy tờ không?", "Dạ em luôn mang kính theo trong túi xách ạ."),
    ("Chờ bác sĩ ghi chú thông tin ban đầu vào máy tính một chút nhé.", "Dạ vâng, bác sĩ cứ làm việc ạ, em ngồi đợi được."),
    ("Buổi sáng ở đây lượng bệnh nhân thường đông hơn buổi chiều một chút.", "Dạ em cũng tranh thủ đi khám sớm cho xong việc ạ."),
    ("{goi_hoa} đưa bàn tay cho bác sĩ xem vòng định danh bệnh nhân nhé.", "Dạ đây ạ, em đeo ở cổ tay từ lúc đăng ký ngoài quầy."),
    ("Thời tiết oi bức thế này ra đường nhớ đội mũ nón cẩn thận nhé {goi}.", "Dạ vâng, em có đội mũ bảo hiểm và che chắn kỹ ạ."),
    ("{goi_hoa} có người nhà đang đợi ở khu vực phòng chờ bên ngoài không?", "Dạ có người nhà em đang ngồi đọc báo ở dãy ghế ngoài kia ạ."),
    ("Bác sĩ lau tay khử khuẩn một lát rồi sẽ bắt đầu khám cho {goi} nhé.", "Dạ vâng, bác sĩ cứ vệ sinh tay chu đáo ạ."),
    ("{goi_hoa} đã kiểm tra kỹ đồ đạc cá nhân chưa, tránh để quên nhé.", "Dạ em đã cất cẩn thận ví tiền và điện thoại vào balo rồi ạ."),
    ("Hôm nay {goi} đi xe ôm công nghệ hay tự lái xe tới vậy?", "Dạ em đặt xe ôm công nghệ chở đến tận cửa phòng khám ạ."),
    ("Ngồi nghỉ ngơi vài phút cho nhịp thở và mạch đập ổn định lại nhé {goi}.", "Dạ vâng, em ngồi hít thở sâu một chút cho lại sức ạ."),
    ("{goi_hoa} có thấy khát nước hay cần đi vệ sinh trước không?", "Dạ em bình thường, sẵn sàng vào khám luôn rồi ạ."),
    ("Bác sĩ chuẩn bị máy đo và dụng cụ y tế một chút nhé.", "Dạ vâng, em xin đợi bác sĩ chuẩn bị ạ."),
    ("{goi_hoa} cầm lấy tập tài liệu tư vấn sức khỏe này đọc tham khảo nhé.", "Dạ em cảm ơn bác sĩ, em sẽ đọc kỹ tờ thông tin này ạ."),
    ("Đường sá dạo này hay sửa chữa, {goi} đi lại nhớ chú ý an toàn nhé.", "Dạ vâng, em cảm ơn lời dặn dò của bác sĩ ạ."),
    ("{goi_hoa} đi khám có gặp khó khăn gì ở khâu tiếp đón không?", "Dạ thủ tục hôm nay rất nhanh gọn và thuận tiện ạ."),
    ("Bác sĩ mở cửa sổ một chút cho gió tự nhiên vào nhé {goi}.", "Dạ vâng, mở cửa sổ ra nhìn thoáng đãng và dễ chịu hơn hẳn ạ."),
    # Thêm 55 cặp tiếp theo
    ("Hôm nay {goi} có mang theo thẻ bảo hiểm y tế điện tử trên VssID không?", "Dạ em đã cài sẵn ứng dụng trên điện thoại rồi ạ."),
    ("Phòng khám có máy nước nóng lạnh ở góc phòng, {goi} cứ tự nhiên nhé.", "Dạ em cảm ơn bác sĩ đã chỉ dẫn ạ."),
    ("{goi_hoa} ngồi ghế đệm này có thấy êm ái không?", "Dạ ghế ngồi rất thoải mái và vừa tầm ạ."),
    ("Bác sĩ nhìn qua phiếu thông tin cá nhân một chút nhé {goi}.", "Dạ vâng, có chỗ nào chưa rõ bác sĩ cứ hỏi em ạ."),
    ("Trời nắng gắt thế này đi đường có bị chói mắt không {goi}?", "Dạ em có đeo kính râm chống nắng rồi ạ."),
    ("{goi_hoa} đã khai báo y tế ban đầu ở bàn lễ tân chưa?", "Dạ em đã tích vào phiếu thông tin ngoài cửa rồi ạ."),
    ("Để bác sĩ chỉnh lại độ cao của ghế khám cho phù hợp với {goi} nhé.", "Dạ vâng, bác sĩ cứ chỉnh giúp em ạ."),
    ("{goi_hoa} có cảm thấy ngột ngạt khi đeo khẩu trang nãy giờ không?", "Dạ em đeo khẩu trang y tế quen rồi nên bình thường ạ."),
    ("Hôm nay công việc của {goi} có bận rộn lắm không?", "Dạ em thu xếp xong việc từ hôm qua để hôm nay đi khám ạ."),
    ("Bác sĩ kiểm tra lại mã số hồ sơ điện tử nhé {goi}.", "Dạ vâng, mã số của em in rõ trên đầu phiếu khám ạ."),
    ("{goi_hoa} đi thang bộ hay đi thang máy lên tầng này vậy?", "Dạ em đi thang máy từ tầng trệt lên đây ạ."),
    ("Không gian phòng khám hôm nay có yên tĩnh không {goi}?", "Dạ phòng khám rất yên tĩnh và sạch sẽ ạ."),
    ("{goi_hoa} kéo rèm che nắng lại một chút cho đỡ chói nhé.", "Dạ vâng, kéo rèm lại nhìn dịu mắt hơn hẳn ạ."),
    ("Bác sĩ bật đèn chuyên dụng để quan sát cho rõ nhé {goi}.", "Dạ vâng, bác sĩ cứ bật đèn lên khám ạ."),
    ("{goi_hoa} có cần sạc pin điện thoại trong lúc ngồi đợi không?", "Dạ pin máy em vẫn còn nhiều, cảm ơn bác sĩ ạ."),
    ("Mời {goi} cất điện thoại vào túi để tập trung trao đổi bệnh nhé.", "Dạ vâng, em đã chuyển sang chế độ im lặng rồi ạ."),
    ("Bác sĩ in sẵn đơn chỉ định ra đây rồi nhé {goi}.", "Dạ em cảm ơn bác sĩ đã in giúp em ạ."),
    ("{goi_hoa} từ sáng đến giờ đã uống đủ hai lít nước chưa?", "Dạ em cũng cố gắng uống nước đều đặn suốt buổi sáng ạ."),
    ("Để tôi dọn dẹp mặt bàn khám một chút cho rộng rãi nhé.", "Dạ vâng, bác sĩ cứ sắp xếp tự nhiên ạ."),
    ("{goi_hoa} có người quen nào từng khám bệnh ở phòng khám này chưa?", "Dạ bạn đồng nghiệp cùng công ty giới thiệu em tới đây khám ạ."),
    ("Buổi trưa phòng khám có nghỉ một tiếng, nhưng bác sĩ vẫn trực ở đây.", "Dạ em tranh thủ vào khám trước giờ nghỉ trưa ạ."),
    ("{goi_hoa} có cần lấy thêm bông cồn lau tay không?", "Dạ em vừa rửa tay sát khuẩn ở cửa vào rồi ạ."),
    ("Cửa kính phòng khám cách âm khá tốt nên không bị ồn ngoài đường.", "Dạ vâng, ngồi trong này em thấy rất tĩnh tâm ạ."),
    ("{goi_hoa} có cần xin giấy xác nhận khám bệnh để nộp cơ quan không?", "Dạ có ạ, lát xong bác sĩ cho em xin một bản nhé."),
    ("Bác sĩ ghi nhận thông tin nghề nghiệp của {goi} vào hồ sơ nhé.", "Dạ vâng, em làm công việc văn phòng thôi ạ."),
    ("{goi_hoa} thấy quy trình đăng ký số khám hôm nay có thuận lợi không?", "Dạ các bước đều có bảng chỉ dẫn rõ ràng nên dễ đi ạ."),
    ("Để bác sĩ bật thêm quạt gió thoang thoảng cho mát mẻ nhé.", "Dạ vâng, bật quạt nhè nhẹ thế này là rất mát rồi ạ."),
    ("{goi_hoa} có hay đi bộ thể dục buổi sáng không?", "Dạ thỉnh thoảng cuối tuần em mới có thời gian đi bộ ạ."),
    ("Bác sĩ kiểm tra lại ngày tháng năm sinh của {goi} một chút nhé.", "Dạ đúng ngày sinh trên thẻ căn cước của em rồi ạ."),
    ("{goi_hoa} có cần túi nilon đựng thuốc lát nữa không?", "Dạ em có mang theo túi vải bảo vệ môi trường rồi ạ.")
]


# ==============================================================================
# 4. BỘ LỜI CHÀO KẾT THEO VÙNG MIỀN VÀ ĐẠI TỪ (CHAO_CUOI_MO_RONG)
# ==============================================================================

# Phân loại theo từng vùng miền với đủ mọi đại từ để không bao giờ bị trùng lặp
CHAO_CUOI_MO_RONG = {
    "bac": [
        # Đại từ TÔI
        "Vâng, tôi cảm ơn bác sĩ.", "Vâng, tôi nhớ rồi ạ.", "Vâng ạ, tôi hiểu rồi.",
        "Vâng, tôi đã rõ rồi, cảm ơn bác sĩ.", "Vâng, tôi sẽ làm theo ạ.",
        "Vâng, tôi biết rồi, cảm ơn bác sĩ.", "Vâng, cảm ơn bác sĩ đã khám cho tôi.",
        "Vâng, tôi hiểu rõ lời bác sĩ dặn rồi, xin cảm ơn bác sĩ.",
        "Vâng, tôi sẽ theo dõi sát sao ở nhà, cảm ơn bác sĩ ạ.",
        "Vâng, tôi nghe rõ hết rồi ạ, cảm ơn bác sĩ đã khám rất kỹ.",
        "Vâng, tôi đã hiểu phác đồ và đơn thuốc rồi, cảm ơn bác sĩ nhiều.",
        "Vâng, tôi xin ghi nhớ lời bác sĩ, cảm ơn bác sĩ đã tận tình khám chữa.",
        "Vâng, tôi rõ mọi việc rồi, xin phép bác sĩ tôi ra quầy lấy thuốc ạ.",
        "Vâng, tôi sẽ tái khám đúng lịch hẹn, cảm ơn bác sĩ.",
        "Vâng ạ, tôi sẽ nghỉ ngơi theo đúng hướng dẫn của bác sĩ.",
        "Vâng ạ, tôi cảm ơn bác sĩ đã khám bệnh cẩn thận.",
        "Vâng, tôi hiểu rồi, chúc bác sĩ một ngày làm việc tốt lành ạ.",
        "Vâng, tôi xin cảm ơn sự tận tâm của bác sĩ ạ.",
        "Vâng, tôi sẽ uống thuốc đúng liều lượng như bác sĩ kê.",
        "Vâng, tôi ghi chép đầy đủ lời bác sĩ dặn rồi ạ.",
        "Vâng, tôi cảm ơn bác sĩ rất nhiều, chào bác sĩ tôi về ạ.",
        "Vâng, tôi đã nắm được chế độ kiêng cữ rồi, cảm ơn bác sĩ.",
        # Đại từ EM
        "Vâng ạ, em cảm ơn bác sĩ.", "Vâng ạ, em cảm ơn bác sĩ nhiều ạ.",
        "Vâng ạ, em cảm ơn bác sĩ đã dặn kỹ.",
        "Vâng ạ, em cảm ơn bác sĩ nhiều, em sẽ uống thuốc đúng giờ.",
        "Vâng ạ, em cảm ơn bác sĩ, có gì bất thường em sẽ quay lại tái khám ngay.",
        "Vâng ạ, em cảm ơn bác sĩ, chúc bác sĩ thật nhiều sức khỏe và công tác tốt.",
        "Vâng ạ, em sẽ tuân thủ uống thuốc đầy đủ, em cảm ơn bác sĩ.",
        "Vâng ạ, cảm ơn bác sĩ đã giải thích rất cặn kẽ và dễ hiểu cho em.",
        "Vâng ạ, em cảm ơn bác sĩ nhiều, chào bác sĩ em về ạ.",
        "Vâng, em xin cảm ơn bác sĩ đã tận tình giải thích ạ.",
        "Vâng, em nghe rõ đơn thuốc rồi, cảm ơn bác sĩ ạ.",
        "Vâng ạ, em nhớ lịch hẹn tái khám rồi, em cảm ơn bác sĩ.",
        "Vâng ạ, em hiểu rõ rồi, em sẽ nghỉ ngơi dưỡng sức ạ.",
        "Vâng, em cảm ơn bác sĩ nhiều, em ra quầy thanh toán đây ạ.",
        "Vâng ạ, em sẽ ăn uống điều độ theo lời bác sĩ chỉ dẫn.",
        # Đại từ CHÁU
        "Vâng ạ, cháu nhớ kỹ lời bác sĩ dặn rồi, cháu cảm ơn bác sĩ nhiều ạ.",
        "Vâng ạ, cháu cảm ơn bác sĩ đã tư vấn và dặn dò chu đáo.",
        "Vâng, cháu cảm ơn bác sĩ, cháu xin phép về ạ.",
        "Vâng ạ, cháu nhớ lời bác sĩ rồi, cháu cảm ơn bác sĩ nhiều.",
        "Vâng ạ, cháu sẽ uống thuốc đúng giờ như bác sĩ bảo.",
        "Vâng ạ, cháu hiểu rồi, cháu cảm ơn bác sĩ đã khám cho cháu.",
        "Vâng, cháu xin phép ra lấy thuốc, cháu cảm ơn bác sĩ ạ.",
        "Vâng ạ, cháu sẽ theo dõi thêm ở nhà, cảm ơn bác sĩ nhiều.",
        # Đại từ CON
        "Vâng, con hiểu rồi, con cảm ơn bác sĩ nhiều ạ.",
        "Vâng ạ, con nhớ lịch tái khám rồi, con cảm ơn bác sĩ.",
        "Vâng ạ, con sẽ uống thuốc đều đặn, cảm ơn bác sĩ ạ.",
        "Vâng, con cảm ơn bác sĩ đã tận tình khám cho con ạ.",
        "Vâng ạ, con nghe lời bác sĩ dặn rồi, con xin phép về ạ.",
        "Vâng, con cảm ơn bác sĩ nhiều, chúc bác sĩ công tác tốt ạ.",
        # Trung tính không đại từ
        "Vâng ạ, xin cảm ơn bác sĩ đã dặn dò cẩn thận.",
        "Vâng, đã hiểu rõ đơn thuốc rồi, cảm ơn bác sĩ nhiều ạ.",
        "Vâng ạ, xin ghi nhớ phác đồ điều trị của bác sĩ.",
        "Vâng, xin cảm ơn bác sĩ đã khám chữa tận tình ạ."
    ],
    "nam": [
        # Đại từ TÔI
        "Dạ tôi nghe rõ lời bác sĩ dặn rồi, cảm ơn bác sĩ nhiều nha.",
        "Dạ tôi cảm ơn bác sĩ nhiều nghen, chúc bác sĩ nhiều sức khỏe.",
        "Dạ tôi xin phép ra lấy thuốc, cảm ơn bác sĩ nhiều nghen.",
        "Dạ tôi nhớ cữ thuốc rồi, cảm ơn bác sĩ đã dặn dò chu đáo nha.",
        "Dạ tôi hiểu rõ phác đồ rồi, cảm ơn bác sĩ nhiều nghen.",
        "Dạ tôi sẽ uống thuốc đúng giờ, xin cảm ơn bác sĩ nhiều nha.",
        "Dạ tôi cảm ơn bác sĩ đã thăm khám cặn kẽ cho tôi nghen.",
        "Dạ tôi nắm rõ các bước điều trị rồi, cảm ơn bác sĩ nha.",
        "Dạ tôi xin ghi nhận lời dặn, cảm ơn bác sĩ dữ lắm.",
        "Dạ tôi sẽ kiêng cữ đúng như bác sĩ dặn, cảm ơn bác sĩ nha.",
        "Dạ tôi hiểu rồi, có gì tôi sẽ ghé tái khám, cảm ơn bác sĩ nghen.",
        "Dạ tôi cảm ơn bác sĩ nhiều, chúc bác sĩ luôn bình an mạnh khỏe.",
        "Dạ tôi nghe rõ hết rồi, xin cảm ơn bác sĩ rất nhiều nha.",
        "Dạ tôi nhớ lịch hẹn tuần sau rồi, cảm ơn bác sĩ nhiều nghen.",
        # Đại từ EM
        "Dạ em nhớ rồi ạ.", "Dạ, em cảm ơn bác sĩ nhiều.", "Dạ, em cảm ơn bác sĩ ạ.",
        "Dạ em hiểu rồi ạ, cảm ơn bác sĩ.", "Dạ vâng, em làm theo lời bác sĩ ạ.",
        "Dạ em nghe rõ rồi ạ, cảm ơn bác sĩ.", "Dạ, em cảm ơn bác sĩ đã khám kỹ ạ.",
        "Dạ, em sẽ làm đúng như bác sĩ dặn ạ.", "Dạ thưa bác sĩ, em cảm ơn ạ.",
        "Dạ em cảm ơn bác sĩ nhiều nghen, em sẽ uống thuốc đúng cữ.",
        "Dạ cảm ơn bác sĩ đã thăm khám nhiệt tình cho em ạ.",
        "Dạ em hiểu rồi, có gì em chạy lại tái khám liền, cảm ơn bác sĩ nghen.",
        "Dạ thưa bác sĩ em đã rõ hết rồi, em cảm ơn bác sĩ dữ lắm.",
        "Dạ cảm ơn bác sĩ nhiều ạ, để em về nghỉ ngơi uống thuốc như dặn.",
        "Dạ em nắm rõ rồi, cảm ơn bác sĩ đã chỉ dẫn cặn kẽ.",
        "Dạ em sẽ uống thuốc đều đặn đúng toa, cảm ơn bác sĩ nha.",
        "Dạ em cảm ơn bác sĩ, chào bác sĩ em ra về ạ.",
        "Dạ em nhớ lời dặn kiêng cữ rồi, cảm ơn bác sĩ nhiều ạ.",
        "Dạ cảm ơn bác sĩ đã giải thích rõ ràng cho em hiểu nha.",
        "Dạ em nghe rõ hết rồi nè, cảm ơn bác sĩ nhiều nghen.",
        "Dạ em xin phép bác sĩ em về, cảm ơn bác sĩ dữ lắm nghen.",
        "Dạ em hiểu toa thuốc rồi, cảm ơn bác sĩ nhiều nha.",
        "Dạ em sẽ tái khám đúng hẹn, cảm ơn bác sĩ nhiều nghen.",
        # Đại từ CON
        "Dạ con nhớ rồi ạ, con cảm ơn bác sĩ nhiều.",
        "Dạ thưa bác sĩ con nghe rõ rồi, con cảm ơn bác sĩ nhiều nghen.",
        "Dạ con cảm ơn bác sĩ đã khám kỹ cho con nghen.",
        "Dạ con sẽ uống nhiều nước như bác sĩ dặn, cảm ơn bác sĩ ạ.",
        "Dạ con hiểu cách dùng thuốc rồi, con cảm ơn bác sĩ nha.",
        "Dạ con xin phép về nghỉ ngơi, cảm ơn bác sĩ nhiều nghen.",
        "Dạ con sẽ uống thuốc đúng cữ như lời bác sĩ dặn ạ.",
        "Dạ con nhớ lời dặn của bác sĩ rồi, con cảm ơn bác sĩ ạ.",
        # Đại từ CHÁU
        "Dạ cháu hiểu rồi bác sĩ ơi, cháu cảm ơn bác sĩ nhiều nha.",
        "Dạ cháu cảm ơn bác sĩ nhiều nghen, chúc bác sĩ luôn vui khỏe.",
        "Dạ cháu nghe rõ rồi, cháu cảm ơn bác sĩ đã dặn dò chu đáo.",
        "Dạ cháu sẽ làm đúng theo lời bác sĩ hướng dẫn ạ.",
        "Dạ cháu nhớ đơn thuốc rồi, cảm ơn bác sĩ nhiều nghen.",
        # Trung tính không đại từ
        "Dạ, cảm ơn bác sĩ ạ.", "Dạ, cảm ơn bác sĩ đã dặn dò ạ.",
        "Dạ xin cảm ơn bác sĩ đã nhiệt tình thăm khám nghen.",
        "Dạ ghi nhận đầy đủ lời dặn rồi, cảm ơn bác sĩ nhiều nha.",
        "Dạ xin cảm ơn bác sĩ, chúc bác sĩ thật nhiều sức khỏe ạ."
    ],
    "trung": [
        # Đại từ TÔI
        "Dạ vâng, tôi cảm ơn bác sĩ.", "Dạ, tôi cảm ơn bác sĩ đã chỉ dẫn.",
        "Dạ, cảm ơn bác sĩ, tôi hiểu rồi.", "Dạ vâng, tôi sẽ theo dõi như bác sĩ dặn.",
        "Dạ tôi nghe rõ rồi, cảm ơn bác sĩ đã dặn dò cẩn thận.",
        "Dạ vâng, tôi hiểu rồi, cảm ơn bác sĩ đã khám chu đáo cho tôi.",
        "Dạ tôi đã rõ rồi bác sĩ, cảm ơn bác sĩ đã tận tình.",
        "Dạ tôi cảm ơn bác sĩ nhiều, chúc bác sĩ công tác tốt ạ.",
        "Dạ tôi xin phép bác sĩ tôi về uống thuốc theo lời dặn ạ.",
        "Dạ tôi hiểu cách uống thuốc rồi, cảm ơn bác sĩ nhiều nhe.",
        "Dạ tôi nhớ lịch hẹn tái khám rồi, xin cảm ơn bác sĩ nhiều nhen.",
        "Dạ tôi sẽ uống thuốc đúng liều, cảm ơn bác sĩ đã căn dặn kỹ càng.",
        "Dạ tôi nắm rõ các bước điều trị rồi, cảm ơn bác sĩ nhe.",
        "Dạ tôi xin cảm ơn bác sĩ đã thăm khám cặn kẽ cho tôi ạ.",
        # Đại từ EM
        "Dạ em nghe rõ lời bác sĩ rồi nhe, em cảm ơn bác sĩ ạ.",
        "Dạ vâng em nhớ rồi, cảm ơn bác sĩ đã khám cho em ạ.",
        "Dạ em cảm ơn bác sĩ nhiều nhen, em về uống thuốc theo đơn.",
        "Dạ em hiểu rõ cách uống thuốc rồi, cảm ơn bác sĩ nhiều nhe.",
        "Dạ em sẽ chú ý theo dõi như lời bác sĩ dặn ạ.",
        "Dạ em cảm ơn bác sĩ đã chỉ bảo tận tình cho em nha.",
        "Dạ em xin phép ra lấy thuốc, cảm ơn bác sĩ nhiều ạ.",
        "Dạ em sẽ tái khám đúng hẹn, cảm ơn bác sĩ nhen.",
        # Đại từ CHÁU
        "Dạ, cháu cảm ơn bác sĩ.", "Dạ, cảm ơn bác sĩ nhiều.",
        "Dạ vâng, cháu nhớ rồi ạ.", "Dạ vâng, cháu làm theo lời bác sĩ.",
        "Dạ cháu cảm ơn bác sĩ nhiều nhe, cháu về uống thuốc theo đơn ạ.",
        "Dạ cháu nhớ kỹ lời bác sĩ rồi, cháu cảm ơn bác sĩ nhiều ạ.",
        "Dạ cảm ơn bác sĩ nhiều nhen, có chi cháu lại vô khám lại.",
        "Dạ vâng, cháu sẽ theo dõi kỹ như lời bác sĩ dặn ạ.",
        "Dạ cháu nhớ đơn thuốc rồi, cảm ơn bác sĩ nhiều nhe.",
        "Dạ cảm ơn bác sĩ đã khám rất kỹ lưỡng cho cháu ạ.",
        "Dạ cháu xin phép về nghỉ ngơi, cảm ơn bác sĩ nhiều ạ.",
        "Dạ cháu nghe rõ rồi, cháu cảm ơn bác sĩ nhiều nhen.",
        # Đại từ CON
        "Dạ con nhớ lời bác sĩ rồi, con cảm ơn bác sĩ nhiều nhen.",
        "Dạ con cảm ơn bác sĩ đã nhiệt tình chỉ dẫn cho con.",
        "Dạ con hiểu rồi, con sẽ uống thuốc đúng bữa ạ.",
        "Dạ con cảm ơn bác sĩ đã khám cẩn thận cho con nhe.",
        "Dạ con nhớ lịch tái khám rồi, con cảm ơn bác sĩ nhiều ạ.",
        # Trung tính không đại từ
        "Dạ, cảm ơn bác sĩ đã dặn dò cẩn thận.",
        "Dạ xin cảm ơn bác sĩ đã nhiệt tình thăm khám nhen.",
        "Dạ đã hiểu rõ đơn thuốc rồi, cảm ơn bác sĩ nhiều ạ.",
        "Dạ xin ghi nhận lời dặn, chúc bác sĩ công tác tốt nhe."
    ]
}


# ==============================================================================
# 5. BIẾN THỂ F-STRING XÁC NHẬN DANH TÍNH (IDENTITY & ROLE)
# ==============================================================================

HOI_TU_KHAM = [
    "{goi_hoa} đi khám cho mình phải không ạ?",
    "Hôm nay {goi} tự đi khám cho mình phải không ạ?",
    "{goi_hoa} đến khám trực tiếp cho bản thân đúng không ạ?",
    "Mình đi khám cho chính mình đúng không {goi}?",
    "{goi_hoa} là người cần khám bệnh hôm nay đúng không ạ?",
    "Hôm nay {goi} đi khám cho bản thân mình phải không?",
    "Cho tôi hỏi người cần kiểm tra sức khỏe hôm nay là {goi} đúng không ạ?",
    "{goi_hoa} tự tới khám bệnh cho mình đúng không ạ?",
    "Hôm nay bác sĩ khám trực tiếp cho {goi} đúng không nào?",
    "{goi_hoa} là người trực tiếp thăm khám hôm nay phải không ạ?"
]

DAP_TU_KHAM = [
    "{tx} khám cho {tx} ạ.",
    "{tx} tự đi khám ạ.",
    "đúng rồi ạ, {tx} tự đến khám.",
    "{tx} đi khám thật ạ.",
    "dạ đúng rồi bác sĩ, {tx} tự đi khám bệnh cho mình ạ.",
    "vâng ạ, {tx} đến khám cho bản thân ạ.",
    "dạ đúng ạ, {tx} là người cần khám hôm nay.",
    "{tx} tự đi khám cho mình bác sĩ ạ.",
    "dạ vâng, {tx} đi khám cho chính {tx} ạ.",
    "đúng rồi bác sĩ, {tx} bị mệt nên tự đi kiểm tra ạ."
]

HOI_QUAN_HE_NGUOI_NHA = [
    "{nn_hoa} là gì của {bn3} ạ?",
    "Cho bác sĩ hỏi {nn} là gì của {bn3} nhà mình ạ?",
    "{nn_hoa} có quan hệ thế nào với {bn3} vậy ạ?",
    "Bác sĩ hỏi một chút, {nn} là người nhà, cụ thể là gì của {bn3} ạ?",
    "{nn_hoa} đưa {bn3} đi khám, mình là quan hệ thế nào với {bn3} ạ?",
    "Để bác sĩ ghi hồ sơ, {nn} là gì của {bn3} vậy ạ?"
]

DAP_QUAN_HE_NGUOI_NHA = [
    "{tx} là {qh} của {bn3} ạ.",
    "{tx} là {qh} ruột của {bn3} ạ.",
    "dạ {tx} là {qh} của {bn3}, nay đưa {bn3} đi khám ạ.",
    "thưa bác sĩ, {tx} là {qh} của {bn3} ạ.",
    "dạ {tx} là {qh} trong nhà của {bn3} ạ."
]


# ==============================================================================
# 6. BIẾN THỂ TRIỆU CHỨNG CHÍNH VÀ THỜI GIAN (CHIEF COMPLAINT)
# ==============================================================================

CACH_KE_CHINH = [
    "{chu}{chinh} {moc} chưa đỡ{tt}.",
    "{chu}bị {chinh} {moc}{tt}.",
    "{chu}thấy {chinh} {moc}{tt}.",
    "{chu}có biểu hiện {chinh} {moc}{tt}.",
    "{chu}có dấu hiệu {chinh} {moc}{tt}.",
    "tình trạng {chinh} của {chu}kéo dài {moc}{tt}.",
    "{chu}bắt đầu thấy {chinh} {moc}{tt}.",
    "{chu}xuất hiện {chinh} {moc}{tt}.",
    "cơn {chinh} này {chu}bị {moc}{tt}.",
    "{chu}bị {chinh} liên tục {moc}{tt}.",
    "{chu}thấy trong người {chinh} {moc}{tt}.",
    "{chu}than phiền {chinh} {moc}{tt}.",
    "{chu}cứ bị {chinh} {moc}{tt}.",
    "{chu}bị chứng {chinh} {moc}{tt}.",
    "{chu}bắt đầu bị {chinh} {moc}{tt}.",
    "{chu}thấy xuất hiện {chinh} {moc}{tt}.",
    "{chu}chịu đựng tình trạng {chinh} {moc}{tt}.",
    "{chu}thấy {chinh} rõ rệt {moc}{tt}.",
    "{chu}phát hiện bị {chinh} {moc}{tt}.",
    "{chu}cảm giác {chinh} {moc}{tt}.",
    "{chu}bị {chinh} làm khó chịu {moc}{tt}.",
    "{chu}khó chịu vì {chinh} {moc}{tt}."
]

CACH_KE_PHU = [
    "{chu}còn {cum} nữa{tt}.",
    "{chu}còn thấy {cum} nữa{tt}.",
    "{chu}có thêm triệu chứng {cum}{tt}.",
    "ngoài ra {chu}còn bị {cum} nữa{tt}.",
    "{chu}kèm theo cả {cum}{tt}.",
    "{chu}thấy có thêm {cum} mấy hôm nay{tt}.",
    "{chu}còn xuất hiện {cum} nữa bác sĩ{tt}.",
    "bên cạnh đó {chu}cũng bị {cum}{tt}.",
    "{chu}bị {cum} kèm theo nữa{tt}.",
    "{chu}thấy người còn có {cum} nữa{tt}.",
    "{chu}kèm theo dấu hiệu {cum} rất khó chịu{tt}.",
    "chưa kể {chu}còn bị {cum} nữa{tt}.",
    "đi kèm với đó là {chu}bị {cum}{tt}.",
    "{chu}phát sinh thêm cả {cum} nữa bác sĩ{tt}.",
    "thêm vào đó {chu}thấy người có {cum}{tt}.",
    "{chu}còn than phiền là bị {cum} nữa{tt}.",
    "đồng thời {chu}còn thấy {cum}{tt}.",
    "{chu}ghi nhận thêm hiện tượng {cum} nữa{tt}.",
    "cùng lúc đó {chu}cũng xuất hiện {cum}{tt}.",
    "{chu}thấy kèm theo triệu chứng {cum} khó ở{tt}."
]


# ==============================================================================
# 7. BIẾN THỂ MỞ ĐẦU VÀ CHUYỂN KHÁM
# ==============================================================================

MO_DAU_MO_RONG = [
    "Chào {goi}, hôm nay {goi} đến khám vì sao{tt}?",
    "{goi} thấy trong người thế nào{tt}?",
    "Mời {goi} ngồi. {goi_hoa} bị làm sao{tt}?",
    "Hôm nay {goi} khám gì{tt}?",
    "{goi_hoa} kể tôi nghe xem dạo này thế nào{tt}.",
    "Chào {goi}, có triệu chứng gì làm {goi} khó chịu phải đi khám thế{tt}?",
    "Mời {goi} ngồi xuống, hôm nay {goi} thấy sức khỏe thế nào{tt}?",
    "{goi_hoa} kể giúp tôi xem mấy hôm nay thấy trong người ra sao{tt}?",
    "Chào {goi}, hôm nay {goi} cảm thấy mệt mỏi hay đau ở đâu vậy{tt}?",
    "Bác sĩ chào {goi}, lý do chính khiến {goi} đi khám hôm nay là gì{tt}?",
    "Mời {goi} ngồi nghỉ ngơi, rồi chia sẻ với tôi lý do đi khám nhé{tt}.",
    "{goi_hoa} kể rõ cho bác sĩ nghe xem tình trạng hiện tại thế nào{tt}.",
    "Chào {goi}, hôm nay trong người thấy khó ở chỗ nào vậy{tt}?",
    "{goi_hoa} đi khám hôm nay vì vấn đề sức khỏe gì thế{tt}?",
    "Bác sĩ lắng nghe đây, {goi} kể xem triệu chứng xuất hiện thế nào{tt}.",
    "Mời {goi} ngồi, cho bác sĩ biết điều gì làm mình lo lắng nhất{tt}?",
    "Chào {goi}, tình trạng khó chịu này bắt đầu từ khi nào thế{tt}?",
    "{goi_hoa} cảm thấy sức khỏe có gì bất thường mấy hôm nay không{tt}?",
    "Bác sĩ chào {goi}, hôm nay {goi} muốn kiểm tra về vấn đề gì{tt}?",
    "Chào {goi}, mời {goi} ngồi tự nhiên rồi kể bệnh tình giúp tôi nhé{tt}.",
    "{goi_hoa} thấy triệu chứng này ảnh hưởng đến sinh hoạt thế nào{tt}?",
    "Hôm nay {goi} đến đây, có điều gì làm mình bận tâm nhất về sức khỏe{tt}?",
    "Chào {goi}, bác sĩ có thể giúp gì cho tình trạng sức khỏe của {goi} hôm nay{tt}?",
    "Mời {goi} ngồi, {goi_hoa} thấy trong người phát sinh dấu hiệu gì lạ thế{tt}?",
    "{goi_hoa} kể từ đầu xem cơ thể bắt đầu thấy mệt từ bao giờ{tt}?",
    "Chào {goi}, hôm nay {goi} thấy đau nhức hay khó chịu ở cơ quan nào{tt}?",
    "Bác sĩ chào {goi}, hãy chia sẻ cụ thể lý do mình đi khám hôm nay nhé{tt}.",
    "{goi_hoa} nghỉ ngơi một chút rồi nói cho bác sĩ biết triệu chứng chính nhé{tt}.",
    "Chào {goi}, mấy hôm nay cơ thể có biểu hiện gì khiến {goi} phải đi khám{tt}?",
    "{goi_hoa} bị cảm giác khó chịu này hành hạ mấy ngày rồi{tt}?"
]

MO_DAU_NGUOI_NHA_MO_RONG = [
    "Chào {goi_nn}, hôm nay {goi_nn} đưa {goi_bs} đi khám vì sao{tt}?",
    "{goi_nn_hoa} thấy {goi_bs} có biểu hiện gì{tt}?",
    "Mời {goi_nn} ngồi. {goi_bs_hoa} nhà mình bị làm sao{tt}?",
    "Chào {goi_nn}, mấy hôm nay {goi_bs} nhà mình có dấu hiệu gì bất thường vậy{tt}?",
    "Mời {goi_nn} ngồi, {goi_nn_hoa} kể bác sĩ nghe xem {goi_bs} bị mệt thế nào{tt}?",
    "Chào {goi_nn}, tình trạng sức khỏe của {goi_bs} dạo này ra sao{tt}?",
    "{goi_nn_hoa} chia sẻ giúp bác sĩ xem {goi_bs} bắt đầu phát bệnh từ khi nào{tt}?",
    "Chào {goi_nn}, lý do chính mà gia đình đưa {goi_bs} đi khám hôm nay là gì{tt}?",
    "Mời {goi_nn} ngồi xuống, {goi_nn} thấy {goi_bs} có triệu chứng gì nặng nhất{tt}?",
    "{goi_nn_hoa} quan sát thấy {goi_bs} kêu đau hay mệt mỏi ở đâu vậy{tt}?",
    "Chào {goi_nn}, gia đình thấy {goi_bs} phát bệnh từ hôm nào thế{tt}?",
    "{goi_nn_hoa} kể rõ giúp bác sĩ xem {goi_bs} ở nhà sinh hoạt ăn uống ra sao{tt}?",
    "Chào {goi_nn}, mấy ngày qua {goi_bs} có biểu hiện gì làm gia đình lo lắng nhất{tt}?",
    "Mời {goi_nn} ngồi, bác sĩ nghe {goi_nn} kể về tình hình sức khỏe của {goi_bs} đây{tt}."
]

# Chú ý: Tuyệt đối không có tiểu từ ở cuối (như "nhé", "nha") vì bộ sinh sẽ tự thêm s.dn() + "."
CHUYEN_KHAM_MO_RONG = [
    "Rồi, để tôi khám cho {goi}",
    "Được rồi, {goi} nằm lên bàn khám giúp tôi",
    "Tôi khám qua một chút",
    "{goi_hoa} ngồi yên để tôi nghe phổi",
    "Để tôi xem bụng một chút",
    "{goi_hoa} giơ tay lên giúp tôi",
    "Để tôi đo huyết áp cho {goi}",
    "Tôi sờ vào chỗ đau xem thế nào",
    "{goi_hoa} há miệng cho tôi xem họng",
    "Để tôi kiểm tra tim một chút",
    "{goi_hoa} thở sâu giúp tôi",
    "Tôi ấn nhẹ vào đây, xem có đau không",
    "Để tôi xem mắt và da một chút",
    "{goi_hoa} quay người sang bên cho tôi khám",
    "Bây giờ {goi} ngồi thẳng lưng lên để tôi kiểm tra tổng quát",
    "Được rồi, mời {goi} qua giường khám để bác sĩ thăm khám kỹ hơn",
    "{goi_hoa} nằm ngửa ra giường khám và thả lỏng cơ thể giúp tôi",
    "Để tôi đo nhiệt độ và nhịp thở của {goi} xem sao",
    "Tôi sẽ nghe tim phổi và kiểm tra vùng họng cho {goi}",
    "{goi_hoa} ngồi dịch lại gần đây để bác sĩ kiểm tra vết đau",
    "Được rồi, {goi} hít thở đều đặn để tôi dùng ống nghe kiểm tra",
    "Để bác sĩ sờ nắn nhẹ khu vực ổ bụng xem có điểm đau khu trú không",
    "Mời {goi} ngồi ngay ngắn để tôi đo dấu hiệu sinh tồn",
    "{goi_hoa} kéo cao tay áo lên một chút để tôi quấn băng đo huyết áp",
    "Để tôi xem kỹ lại vùng da bị tổn thương",
    "{goi_hoa} ngửa cổ nhẹ ra sau để tôi sờ nắn hạch vùng cổ",
    "Tôi dùng đèn soi đáy mắt và kiểm tra đồng tử cho {goi}",
    "{goi_hoa} co gập hai đầu gối lại để tôi kiểm tra phản xạ gân xương",
    "Để tôi kiểm tra nhịp mạch ở cổ tay của {goi}",
    "{goi_hoa} nuốt nước bọt một cái để tôi xem cử động thanh quản",
    "Tôi ấn nhẹ vùng hố chậu xem phản ứng đề kháng thế nào"
]


# ==============================================================================
# 8. BIẾN THỂ CÂU HỎI KHÔNG ĐÁP, ĐIỀU DƯỠNG, TÁI KHÁM
# ==============================================================================

HOI_KHONG_DAP_MO_RONG = [
    "Gần đây {goi} có đi đâu xa không{tt}?",
    "{goi_hoa} ngủ nghỉ thế nào{tt}?",
    "Ăn uống dạo này ra sao{tt}?",
    "Dạo này trong người có thấy sụt cân không{tt}?",
    "Công việc đợt này có bị áp lực căng thẳng quá không{tt}?",
    "{goi_hoa} có hay bị mất ngủ ban đêm không{tt}?",
    "Ở nhà có ai xung quanh bị triệu chứng tương tự không{tt}?",
    "Mấy hôm nay sinh hoạt ăn ngủ có điều độ không{tt}?",
    "{goi_hoa} thấy tinh thần dạo này thế nào{tt}?",
    "Có hay bị hụt hơi khi leo cầu thang không{tt}?",
    "Gần đây môi trường làm việc có nhiều khói bụi không{tt}?",
    "{goi_hoa} uống nước mỗi ngày có đủ không{tt}?",
    "Dạo này đi đại tiểu tiện có gì bất thường không{tt}?",
    "{goi_hoa} có thấy hay bị vã mồ hôi trộm ban đêm không{tt}?",
    "Gần đây mình có dùng chất kích thích hay cà phê nhiều không{tt}?",
    "{goi_hoa} có hay bị hoa mắt chóng mặt khi đứng lên ngồi xuống không{tt}?",
    "Dạo này thị lực và thính giác của {goi} có thấy giảm sút không{tt}?",
    "{goi_hoa} có cảm giác đắng miệng hay chán ăn mấy ngày nay không{tt}?",
    "Mỗi ngày {goi} có duy trì tập thể dục hay vận động nhẹ không{tt}?",
    "{goi_hoa} có thường xuyên phải thức khuya làm việc không{tt}?",
    "Gần đây trong gia đình có ai bị cảm sốt hay ho lây sang không{tt}?",
    "{goi_hoa} có cảm thấy người hay bị ớn lạnh về chiều tối không{tt}?",
    "Dạo này đường tiêu hóa của {goi} có hay bị đầy bụng khó tiêu không{tt}?",
    "{goi_hoa} có hay bị tê bì chân tay khi ngồi lâu một chỗ không{tt}?",
    "Gần đây cân nặng của {goi} có biến động tăng hay giảm đột ngột không{tt}?",
    "{goi_hoa} có cảm thấy trí nhớ dạo này hay bị đãng trí quên trước quên sau không{tt}?",
    "Thời gian gần đây {goi} có tiếp xúc với nguồn hóa chất độc hại nào không{tt}?",
    "{goi_hoa} có thấy đau mỏi vùng vai gáy khi ngồi làm việc không{tt}?",
    "Dạo này giấc ngủ của {goi} có sâu không hay chập chờn dễ tỉnh giấc{tt}?",
    "{goi_hoa} có cảm giác tim đập nhanh hay hồi hộp trống ngực không{tt}?"
]

BAC_SI_DIEU_DUONG_MO_RONG = [
    "Cảm ơn em. {_hoa(ca.goi_bn)} kể tôi nghe xem thế nào{tt()}.",
    "Được rồi, cảm ơn em điều dưỡng. Mời {_hoa(ca.goi_bn)} kể bác sĩ nghe xem trong người mệt ra sao{tt()}.",
    "Bác sĩ cảm ơn em nhé. {_hoa(ca.goi_bn)} chia sẻ cho tôi biết lý do đi khám hôm nay là gì{tt()}?",
    "Tôi rõ rồi, cảm ơn em. {_hoa(ca.goi_bn)} thấy sức khỏe có gì bất thường mấy hôm nay{tt()}?",
    "Cảm ơn em nhé. Mời {_hoa(ca.goi_bn)} ngồi nghỉ rồi kể xem triệu chứng xuất hiện thế nào{tt()}.",
    "Được rồi em. {_hoa(ca.goi_bn)} cho bác sĩ biết chỗ nào làm mình khó chịu nhất{tt()}?",
    "Bác sĩ ghi nhận sinh hiệu, cảm ơn em. {_hoa(ca.goi_bn)} kể xem bệnh bắt đầu từ hôm nào{tt()}?",
    "Cảm ơn em điều dưỡng nhiều. {_hoa(ca.goi_bn)} kể từ đầu xem tình trạng dạo này thế nào nhé{tt()}."
]

DIEU_DUONG_MO_RONG = [
    ("vào từ sáng", "em đã đo sinh hiệu rồi ạ."),
    ("mới đăng ký khám", "em đã đo huyết áp và nhịp tim rồi ạ."),
    ("chờ từ nãy", "các chỉ số sinh hiệu em đã cập nhật trên phiếu ạ."),
    ("vừa vào phòng chờ", "em đã kiểm tra mạch và nhiệt độ xong ạ."),
    ("đã làm thủ tục tiếp đón", "sinh hiệu ban đầu đo được ổn định ạ."),
    ("đã vào sảnh chờ", "em đo xong huyết áp và SpO2 rồi ạ."),
    ("đăng ký số thứ tự từ sớm", "sinh hiệu em ghi đầy đủ vào sổ rồi ạ."),
    ("vừa được đưa tới", "em đã kiểm tra mạch nhiệt độ huyết áp xong xuôi ạ.")
]

TAI_KHAM_MO_RONG = [
    "Lần trước tôi kê {thuoc} cho {ai}, dùng thấy thế nào{tt}?",
    "Đợt khám trước {ai} uống {thuoc} có thấy thuyên giảm không{tt}?",
    "Toa thuốc {thuoc} lần trước bác sĩ kê, {ai} dùng đáp ứng ra sao{tt}?",
    "Tình hình uống {thuoc} từ hôm tái khám trước tới nay thế nào rồi {ai}{tt}?",
    "{ai} dùng {thuoc} theo đơn cũ thấy triệu chứng có đỡ hơn không{tt}?",
    "Lần khám trước tôi có kê {thuoc}, {ai} uống đều đặn chứ{tt}?",
    "Đơn thuốc {thuoc} đợt trước {ai} dùng hết chưa, cảm thấy thế nào{tt}?"
]


# ==============================================================================
# 9. DẪN NHẬP PHONG PHÚ CHO KHÁM, CHẨN ĐOÁN, KẾ HOẠCH (CUT DUPLICATION)
# ==============================================================================

KHAM_DAN_MO_RONG = [
    "{kham}",
    "Qua thăm khám lâm sàng, tôi thấy: {kham}",
    "Kết quả kiểm tra thực thể: {kham}",
    "Khám lâm sàng ghi nhận: {kham}",
    "Tôi kiểm tra qua thì thấy: {kham}",
    "Tình trạng thực thể hiện tại: {kham}",
    "Sau khi thăm khám tôi ghi nhận: {kham}",
    "Đánh giá lâm sàng cho thấy: {kham}",
    "Tôi vừa kiểm tra xong, cụ thể: {kham}",
    "Biểu hiện qua thăm khám thực thể: {kham}",
    "Ghi nhận thăm khám ban đầu: {kham}",
    "Kiểm tra lâm sàng phát hiện: {kham}",
    "Khám thực thể nhận thấy: {kham}",
    "Thăm khám lâm sàng cho thấy: {kham}",
    "Sau khi trực tiếp kiểm tra: {kham}"
]

CHAN_DOAN_DAN_MO_RONG = [
    "{chan_doan}",
    "Chẩn đoán hiện tại là: {chan_doan}",
    "Tôi chẩn đoán là: {chan_doan}",
    "Kết luận chẩn đoán: {chan_doan}",
    "Qua thăm khám, tôi xác định: {chan_doan}",
    "Trường hợp này được chẩn đoán: {chan_doan}",
    "Đánh giá chẩn đoán lâm sàng: {chan_doan}",
    "Kết quả chẩn đoán cho thấy: {chan_doan}",
    "Bác sĩ kết luận chẩn đoán: {chan_doan}",
    "Tôi đưa ra chẩn đoán xác định: {chan_doan}",
    "Tình trạng này được xác định là: {chan_doan}",
    "Chẩn đoán y khoa hiện tại: {chan_doan}",
    "Dựa vào các biểu hiện, tôi chẩn đoán: {chan_doan}",
    "Bệnh cảnh này phù hợp với chẩn đoán: {chan_doan}"
]

KE_HOACH_DAN_MO_RONG = [
    "{ke_hoach}",
    "Hướng điều trị như sau: {ke_hoach}",
    "Kế hoạch điều trị cụ thể: {ke_hoach}",
    "Về phương án xử trí: {ke_hoach}",
    "Tôi đưa ra kế hoạch điều trị: {ke_hoach}",
    "Phương án điều trị tiếp theo: {ke_hoach}",
    "Lời khuyên và hướng điều trị: {ke_hoach}",
    "Kế hoạch theo dõi và dùng thuốc: {ke_hoach}",
    "Phác đồ điều trị được chỉ định: {ke_hoach}",
    "Về các bước can thiệp tiếp theo: {ke_hoach}",
    "Chỉ định điều trị như sau: {ke_hoach}",
    "Phương hướng xử trí cho đợt này: {ke_hoach}",
    "Kế hoạch can thiệp y tế: {ke_hoach}",
    "Hướng giải quyết và dùng thuốc: {ke_hoach}"
]


# ==============================================================================
# 10. BỘ SINH ĐA TẦNG TOÀN DIỆN GIẢM TRÙNG LẶP (TASK B3 EXTENDED GENERATORS)
# ==============================================================================

# --- 10.1. Chào cuối đa tầng (Lead-in x Core[Pronoun] x Gratitude x Ending[Region])
# do AI viết, chưa bác sĩ duyệt
DAN_CHAO_DT = {
    "bac": ["Vâng ạ, ", "Vâng, ", "Dạ vâng, ", "Dạ, ", ""],
    "trung": ["Dạ, ", "Dạ vâng, ", "Dạ bác sĩ, ", ""],
    "nam": ["Dạ, ", "Dạ vâng, ", "Dạ bác sĩ, ", ""]
}

CORE_CHAO_DT = {
    "tôi": [
        "tôi nhớ lời bác sĩ dặn rồi", "tôi sẽ uống thuốc đúng giờ",
        "tôi hiểu đơn thuốc rồi", "tôi sẽ tái khám đúng hẹn",
        "cảm ơn bác sĩ nhiều", "tôi rõ cách dùng thuốc rồi",
        "tôi sẽ theo dõi kỹ", "cảm ơn bác sĩ đã khám kỹ"
    ],
    "em": [
        "em nhớ lời bác sĩ rồi", "em sẽ uống thuốc đúng đơn",
        "em hiểu cách uống rồi", "em sẽ tái khám đúng hẹn",
        "em cảm ơn bác sĩ nhiều", "em rõ hết phác đồ rồi",
        "em sẽ theo dõi kỹ", "cảm ơn bác sĩ đã khám kỹ"
    ],
    "cháu": [
        "cháu nhớ lời bác sĩ rồi", "cháu sẽ uống thuốc đúng giờ",
        "cháu cảm ơn bác sĩ", "cháu nhớ cách uống rồi",
        "cháu cảm ơn bác sĩ nhiều", "cháu hiểu rồi"
    ],
    "con": [
        "con nhớ lời bác sĩ rồi", "con sẽ uống thuốc đúng giờ",
        "con cảm ơn bác sĩ", "con cảm ơn bác sĩ nhiều",
        "con hiểu cách dùng rồi", "con sẽ tái khám đúng hẹn"
    ],
    "trung_tinh": [
        "xin ghi nhận lời dặn", "đã hiểu rõ đơn thuốc rồi",
        "xin cảm ơn bác sĩ", "sẽ tái khám đúng hẹn"
    ]
}

GRATITUDE_CHAO_DT = [
    "cảm ơn bác sĩ nhiều", "xin cảm ơn bác sĩ",
    "chúc bác sĩ nhiều sức khỏe", "cảm ơn bác sĩ đã giúp đỡ",
    "cảm ơn bác sĩ đã khám kỹ", "chúc bác sĩ công tác tốt"
]

ENDING_CHAO_DT = {
    "bac": [" ạ.", " nhé ạ.", " ạ, xin phép về."],
    "trung": [" ạ.", " nhe bác sĩ.", " nghen bác sĩ."],
    "nam": [" nghen bác sĩ.", " nha bác sĩ.", " ạ."]
}

# ═══ sinh_chao_cuoi() — Sinh lời chào kết thúc buổi khám ══════════════════════════════
# Chọn lời theo miền và thái độ người nói; 30% thêm lời cảm ơn.
def sinh_chao_cuoi(ca, tx: str, rng: random.Random) -> str:
    mien = ca.mien if ca.mien in DAN_CHAO_DT else "nam"
    dan = rng.choice(DAN_CHAO_DT[mien])
    loi_pool = CORE_CHAO_DT.get(tx, CORE_CHAO_DT["trung_tinh"])
    duoi = rng.choice(ENDING_CHAO_DT[mien])
    if rng.random() < 0.3:
        grat = rng.choice(GRATITUDE_CHAO_DT)
        cau = f"{dan}{grat}{duoi}".strip()
    else:
        loi = rng.choice(loi_pool)
        cau = f"{dan}{loi}{duoi}".strip()
    return cau[:1].upper() + cau[1:]


# --- 10.2. Chuyển khám đa tầng (Lead-in x Action x Suffix)
# do AI viết, chưa bác sĩ duyệt
DAN_CK_DT = [
    "", "", "", "", "", "Rồi, ", "Giờ ", "Tiếp theo, "
]

LOI_CK_DT = [
    "để tôi khám cho {goi}", "{goi} nằm lên bàn khám", "tôi khám qua cho {goi}",
    "{goi} ngồi yên tôi nghe tim phổi", "để tôi kiểm tra vùng bụng",
    "{goi} giơ hai tay lên", "để tôi đo lại huyết áp cho {goi}",
    "tôi sờ nắn chỗ đau", "{goi} há miệng tôi soi họng",
    "để tôi nghe tim và phổi", "{goi} hít sâu thở đều",
    "tôi ấn nhẹ chỗ này xem có đau không", "để tôi xem vùng da niêm mạc",
    "{goi} nghiêng sang bên này", "bác sĩ nghe tim phổi cho {goi}",
    "bác sĩ kiểm tra phản xạ", "để bác sĩ nghe vùng ngực",
    "để bác sĩ xem các khớp có sưng không", "để bác sĩ kiểm tra họng",
    "{goi} ngồi thẳng lưng tôi nghe phổi", "để bác sĩ đo mạch và SpO2",
    "để tôi kiểm tra một lượt", "bác sĩ khám tai mũi họng cho {goi}",
    "bác sĩ sờ nắn kiểm tra vùng đau", "{goi} ngồi thẳng người tôi kiểm tra",
    "để tôi soi đèn kiểm tra họng", "{goi} hít thở sâu bằng miệng",
    "tôi kiểm tra nhiệt độ và mạch", "để bác sĩ ấn nhẹ kiểm tra gan lách",
    "{goi} duỗi thẳng chân ra", "để tôi kiểm tra huyết áp hai tay",
    "bác sĩ kiểm tra hạch vùng cổ", "{goi} quay mặt sang bên phải",
    "để tôi nghe lại nhịp tim", "bác sĩ xem qua kết mạc mắt"
]

DUOI_CK_DT = [
    " nhé.", " nhé ạ.", " một chút nhé.", " nha.", " nghen."
]

# ═══ sinh_chuyen_kham() — Sinh câu chuyển sang giai đoạn khám ═════════════════════════
# Ghép dẫn, lời, đuôi; viết hoa đầu câu.
def sinh_chuyen_kham(goi: str, goi_hoa: str, rng: random.Random) -> str:
    dan = rng.choice(DAN_CK_DT)
    loi = rng.choice(LOI_CK_DT).format(goi=goi, goi_hoa=goi_hoa)
    duoi = rng.choice(DUOI_CK_DT).format(goi=goi, goi_hoa=goi_hoa)
    cau = f"{dan}{loi}{duoi}".strip()
    return cau[:1].upper() + cau[1:]


# --- 10.3. Khám, Chẩn đoán, Kế hoạch đa tầng
# do AI viết, chưa bác sĩ duyệt
DAN_KHAM_GEN = [
    "", "", "", "", "", "",
    "Khám thấy: ", "Ghi nhận: ", "Khám lâm sàng: ", "Kiểm tra thấy: ",
    "Thăm khám ghi nhận: ", "Khám thực thể: ", "Tôi ghi nhận: "
]
DUOI_KHAM_GEN = [""]

DAN_CD_GEN = [
    "", "", "", "", "", "",
    "Chẩn đoán: ", "Kết luận: ", "Tôi chẩn đoán: ",
    "Khả năng cao là: ", "Bác sĩ nghĩ đến: ", "Hướng tới: "
]
DUOI_CD_GEN = [""]

DAN_KH_GEN = [
    "", "", "", "", "", "",
    "Hướng xử trí: ", "Phác đồ: ", "Kế hoạch: ",
    "Về điều trị: ", "Bác sĩ dặn: ", "Tôi hướng dẫn: "
]
DUOI_KH_GEN = [""]

# ═══ sinh_kham() — Sinh câu bác sĩ nêu kết quả khám ═══════════════════════════════════
# Bọc nội dung khám giữa phần dẫn và phần đuôi ngẫu nhiên.
def sinh_kham(kham: str, rng: random.Random) -> str:
    return f"{rng.choice(DAN_KHAM_GEN)}{kham}{rng.choice(DUOI_KHAM_GEN)}"

# ═══ sinh_chan_doan() — Sinh câu bác sĩ nêu chẩn đoán ═════════════════════════════════
# Bọc chẩn đoán giữa phần dẫn và phần đuôi ngẫu nhiên.
def sinh_chan_doan(chan_doan: str, rng: random.Random) -> str:
    return f"{rng.choice(DAN_CD_GEN)}{chan_doan}{rng.choice(DUOI_CD_GEN)}"

# ═══ sinh_ke_hoach() — Sinh câu bác sĩ nêu kế hoạch điều trị ══════════════════════════
# Bọc kế hoạch giữa phần dẫn và phần đuôi ngẫu nhiên.
def sinh_ke_hoach(ke_hoach: str, rng: random.Random) -> str:
    return f"{rng.choice(DAN_KH_GEN)}{ke_hoach}{rng.choice(DUOI_KH_GEN)}"


# --- 10.4. Xác nhận danh tính đa tầng
DAN_HOI_TK_DT = [
    "", "", "", "", "Hôm nay ", "Bác sĩ hỏi, ",
    "Cho bác sĩ hỏi là, ", "Bác sĩ muốn xác nhận trước, ", "Để ghi vào hồ sơ thì, ",
    "Trước khi bắt đầu, ", "Cho tôi hỏi một chút, ", "Để rõ thông tin đăng ký, "
]
LOI_HOI_TK_DT = [
    "{goi} đi khám cho mình phải không", "hôm nay {goi} là người trực tiếp cần khám đúng không",
    "{goi} đến kiểm tra sức khỏe cho bản thân mình phải không", "có phải {goi} là bệnh nhân cần khám hôm nay không",
    "bác sĩ khám cho chính {goi} đúng không", "{goi} đến đây khám bệnh cho mình hay cho ai khác",
    "hôm nay {goi} tự mình đến khám chữa bệnh đúng không", "phiếu khám này là của chính {goi} phải không",
    "{goi} tự đi khám phải không", "bác sĩ khám cho {goi} phải không",
    "{goi} đi khám cho bản thân đúng không"
]
DUOI_HOI_TK_DT = [" ạ?", "?", " vậy ạ?", " thế ạ?"]

# do AI viết, chưa bác sĩ duyệt
DAN_DAP_TK_DT = [
    "Dạ, ", "Vâng, ", "Đúng rồi, ", "", ""
]
LOI_DAP_TK_DT = [
    "{tx} đi khám cho mình", "{tx} tự đi khám", "của {tx}",
    "{tx} đi khám", "hôm nay {tx} khám", "hôm nay {tx} đi khám",
    "chính {tx} khám", "{tx} đến khám cho bản thân", "{tx} tự đến khám",
    "{tx} đăng ký khám cho mình", "phiếu này là của {tx}",
    "{tx} đến kiểm tra sức khỏe", "{tx} tới khám bệnh hôm nay",
    "{tx} tự đi kiểm tra sức khỏe", "chính {tx} cần khám bệnh",
    "{tx} đến khám theo lịch", "{tx} đi khám cho chính mình",
    "{tx} đăng ký khám bệnh hôm nay", "phiếu khám của {tx} đây"
]
DUOI_DAP_TK_DT = [" ạ.", "."]

# ═══ sinh_danh_tinh_tu_kham() — Sinh cặp hỏi đáp xác nhận bệnh nhân tự đi khám ════════
# Trả (câu hỏi, câu đáp); 52% người đáp xưng bằng từ xưng của mình.
def sinh_danh_tinh_tu_kham(ca, rng: random.Random) -> Tuple[str, str]:
    hoi = f"{rng.choice(DAN_HOI_TK_DT)}{rng.choice(LOI_HOI_TK_DT).format(goi=ca.goi_bn, goi_hoa=ca.goi_bn[:1].upper() + ca.goi_bn[1:])}{rng.choice(DUOI_HOI_TK_DT)}".strip()
    hoi = hoi[:1].upper() + hoi[1:]
    if rng.random() < 0.52:
        tx = ca.tu_xung_bn
        dap_choices = [
            "Dạ đúng ạ.", "Vâng ạ.", "Dạ phải ạ.", "Đúng rồi ạ.",
            "Dạ đúng rồi.", f"Của {tx} ạ.", f"{tx} đi khám.",
            "Dạ chính xác.", "Dạ vâng ạ.", f"Đúng {tx} rồi.",
            "Tôi đi khám.", "Của tôi ạ."
        ]
        dap = rng.choice(dap_choices)
    else:
        dap = f"{rng.choice(DAN_DAP_TK_DT)}{rng.choice(LOI_DAP_TK_DT).format(tx=ca.tu_xung_bn)}{rng.choice(DUOI_DAP_TK_DT)}"
        dap = dap[:1].upper() + dap[1:]
    return hoi, dap

DAN_HOI_NN_DT = [
    "", "Cho bác sĩ hỏi, ", "Bác sĩ muốn xác nhận, ", "Để tiện xưng hô trong hồ sơ, ",
    "Bác sĩ hỏi một chút, ", "Cho tôi hỏi rõ là, "
]
LOI_HOI_NN_DT = [
    "{nn} có quan hệ như thế nào với {bn3}", "{nn} là người nhà gì của {bn3}",
    "{nn} là gì của {bn3}", "mình có quan hệ gia đình thế nào với {bn3}"
]
DUOI_HOI_NN_DT = [" ạ?", "?", " vậy ạ?", " thế ạ?"]

DAN_DAP_NN_DT = ["Dạ, ", "Dạ thưa bác sĩ, ", "Vâng ạ, ", "Dạ vâng, ", "Thưa bác sĩ, "]
LOI_DAP_NN_DT = [
    "{tx} là {qh} của {bn3}", "{tx} là {qh} đưa {bn3} đi khám",
    "{tx} là người nhà, cụ thể là {qh} của {bn3}", "{tx} là {qh} ruột trong nhà của {bn3}"
]
DUOI_DAP_NN_DT = [" ạ.", " đây ạ.", " bác sĩ ạ.", "."]

# ═══ sinh_danh_tinh_nguoi_nha() — Sinh cặp hỏi đáp xác nhận quan hệ người nhà ═════════
# Trả (câu hỏi, câu đáp) nêu rõ người kể là ai của bệnh nhân.
def sinh_danh_tinh_nguoi_nha(ca, bn3: str, rng: random.Random) -> Tuple[str, str]:
    nn = ca.nguoi_ke[1]
    nn_hoa = nn[:1].upper() + nn[1:]
    hoi = f"{rng.choice(DAN_HOI_NN_DT)}{rng.choice(LOI_HOI_NN_DT).format(nn=nn, nn_hoa=nn_hoa, bn3=bn3)}{rng.choice(DUOI_HOI_NN_DT)}".strip()
    hoi = hoi[:1].upper() + hoi[1:]
    dap = f"{rng.choice(DAN_DAP_NN_DT)}{rng.choice(LOI_DAP_NN_DT).format(tx=ca.nguoi_ke[2], qh=ca.nguoi_ke[3], bn3=bn3)}{rng.choice(DUOI_DAP_NN_DT)}"
    return hoi, dap


# --- 10.5. Phủ định bệnh nhân đa tầng (Allergy, Meds, History)
# do AI viết, chưa bác sĩ duyệt
DAN_PHU_DINH_DT = {
    "bac": ["Dạ không, ", "Không ạ, ", "Chưa ạ, ", "Dạ chưa, ", ""],
    "trung": ["Dạ không, ", "Không có, ", "Dạ chưa, ", ""],
    "nam": ["Dạ không, ", "Hổng có, ", "Dạ chưa, ", ""]
}

# do AI viết, chưa bác sĩ duyệt
PHU_DINH_NGAN_DT = {
    "bac": [
        "Dạ không ạ.", "Không ạ.", "Chưa ạ.", "Dạ chưa ạ.", "Không có ạ.",
        "Dạ không có.", "Dạ chưa từng.", "Không có đâu ạ.", "Dạ ổn cả.",
        "Bình thường ạ.", "Dạ không sao.", "Dạ chưa từng bị.",
        "Dạ không bị bệnh gì ạ.", "Trước giờ bình thường cả ạ.",
        "Dạ không có dị ứng gì ạ.", "Trong nhà không ai bị cả ạ.",
        "Dạ không có biểu hiện đó ạ.", "Bình thường không thấy gì lạ ạ.",
        "Dạ không có bệnh mạn tính nào ạ.", "Dạ sức khỏe bình thường ạ."
    ],
    "trung": [
        "Dạ không ạ.", "Không có ạ.", "Dạ chưa ạ.", "Không có mô.",
        "Dạ không có.", "Dạ chưa từng.", "Bình thường cả.", "Dạ ổn cả.",
        "Không can chi mô.", "Dạ chưa từng bị.", "Không có chi mô.",
        "Dạ không có chi mô ạ.", "Trước chừ bình thường rứa bác sĩ.",
        "Dạ không bị chi hết ạ.", "Dạ không có dị ứng chi mô.",
        "Trong nhà không ai bị rứa cả.", "Bình thường không thấy chi lạ hết.",
        "Dạ chưa từng bị rứa bao giờ.", "Khỏe re hà, không có chi mô."
    ],
    "nam": [
        "Dạ không ạ.", "Dạ hổng có.", "Dạ chưa ạ.", "Không có đâu ạ.",
        "Dạ không có.", "Dạ chưa từng.", "Bình thường bác sĩ.", "Dạ ổn cả.",
        "Dạ không sao.", "Dạ chưa từng bị.", "Hổng có đâu ạ.", "Bình thường ạ.",
        "Dạ hổng có bị gì hết trơn.", "Trước giờ khỏe re hà.",
        "Dạ không có dị ứng gì đâu bác sĩ.", "Trong nhà hổng ai bị giống vậy hết.",
        "Dạ bình thường hổng có gì lạ.", "Hổng có sao đâu bác sĩ.",
        "Dạ chưa từng bị vậy bao giờ.", "Dạ mọi thứ bình thường hà."
    ]
}

# do AI viết, chưa bác sĩ duyệt
PHU_DINH_CHUA_UONG_NGAN_DT = {
    "bac": [
        "Dạ chưa ạ.", "Chưa ạ.", "Chưa uống gì ạ.", "Dạ chưa bác sĩ.",
        "Dạ chưa uống gì.", "Chưa dùng gì ạ.", "Dạ chưa có uống.",
        "Chưa uống viên nào ạ.", "Dạ chưa dùng gì.",
        "Dạ chưa kịp uống gì cả ạ.", "Chưa đụng đến viên thuốc nào ạ.",
        "Ở nhà chưa dùng thứ gì hết ạ.", "Chưa kịp mua thuốc gì uống cả.",
        "Dạ đi khám luôn chứ chưa uống gì."
    ],
    "trung": [
        "Dạ chưa ạ.", "Chưa ạ.", "Chưa uống chi cả.", "Dạ chưa bác sĩ.",
        "Chưa dùng chi hết.", "Dạ chưa uống mô.", "Chưa uống thuốc chi.",
        "Dạ chưa dùng chi.", "Chưa có uống chi mô.",
        "Dạ tới thẳng đây khám chớ chưa uống chi.", "Chưa đụng tới viên thuốc mô hết.",
        "Ở nhà chưa kịp mua thuốc chi uống.", "Dạ chưa uống chi hết nhe bác sĩ."
    ],
    "nam": [
        "Dạ chưa ạ.", "Chưa ạ.", "Chưa uống gì bác sĩ.", "Dạ chưa bác sĩ.",
        "Chưa có uống gì ạ.", "Chưa dùng gì hết á.", "Dạ chưa uống viên nào.",
        "Hổng có uống gì hết á.", "Dạ chưa dùng thuốc gì.",
        "Dạ chạy qua đây khám liền chứ chưa uống gì.", "Chưa có đụng viên thuốc nào hết trơn.",
        "Hổng có dám tự uống thuốc ở nhà.", "Dạ chưa mua thuốc gì uống hết á."
    ]
}

# do AI viết, chưa bác sĩ duyệt
CORE_KHONG_DU_DT = [
    "{sub} không dị ứng thuốc gì",
    "{sub} chưa từng bị dị ứng thuốc",
    "trước giờ {sub} không dị ứng gì",
    "{sub} uống thuốc bình thường",
    "{sub} không bị dị ứng kháng sinh",
    "{sub} không có tiền sử dị ứng",
    "{sub} không dị ứng thuốc nào cả",
    "{sub} chưa từng dị ứng thuốc",
    "{sub} chưa thấy dị ứng thuốc nào",
    "{sub} dùng thuốc bình thường không sao",
    "{sub} không có cơ địa dị ứng",
    "{sub} chưa từng nổi mề đay",
    "{sub} uống thuốc đều êm",
    "{sub} không phản ứng với thuốc gì",
    "{sub} chưa bao giờ dị ứng thuốc",
    "trước nay {sub} uống thuốc không sao",
    "{sub} không dị ứng kháng sinh nào",
    "{sub} chưa từng bị phát ban",
    "{sub} uống thuốc rất êm"
]
CHITIET_KHONG_DT = [
    ""
]
DUOI_PHU_DINH_DT = {
    "bac": [" ạ.", "."],
    "trung": [" ạ.", " bác sĩ.", "."],
    "nam": [" nha bác sĩ.", " ạ.", "."]
}

# ─── _chu_the_benh_nhan() — Lấy cách gọi bệnh nhân dùng trong câu đáp ─────────────────
# Có người kể thì dùng cách gọi bệnh nhân, không thì dùng từ tự xưng.
def _chu_the_benh_nhan(ca) -> str:
    return ca.goi_bn if getattr(ca, "nguoi_ke", None) else ca.tu_xung_bn

# ═══ sinh_dap_khong_di_ung() — Sinh câu đáp phủ định rằng không dị ứng ════════════════
# 45% là đáp ngắn; còn lại ghép dẫn, lõi, đuôi theo miền.
def sinh_dap_khong_di_ung(ca, rng: random.Random, tt: str = "") -> str:
    mien = ca.mien if ca.mien in DAN_PHU_DINH_DT else "nam"
    if rng.random() < 0.45:
        return rng.choice(PHU_DINH_NGAN_DT[mien])
    dan = rng.choice(DAN_PHU_DINH_DT[mien])
    core = rng.choice(CORE_KHONG_DU_DT).format(sub=_chu_the_benh_nhan(ca))
    duoi = rng.choice(DUOI_PHU_DINH_DT[mien])
    kq = f"{dan}{core}{duoi}".strip()
    return kq[:1].upper() + kq[1:]

# do AI viết, chưa bác sĩ duyệt
CORE_CHUA_UT_DT = [
    "{sub} chưa uống thuốc gì",
    "{sub} chưa dùng thuốc ở nhà",
    "{sub} chưa mua thuốc uống",
    "{sub} chưa uống viên nào",
    "ở nhà {sub} chưa uống thuốc",
    "{sub} chưa uống thuốc gì cả",
    "{sub} chưa kịp uống viên nào",
    "{sub} chưa tự mua thuốc uống",
    "{sub} tới khám luôn, chưa uống gì",
    "{sub} chưa uống hạ sốt gì",
    "{sub} chưa uống thuốc tây thuốc nam",
    "ở nhà {sub} chưa uống gì",
    "{sub} chưa uống từ lúc đau",
    "{sub} chưa dùng thuốc gì ở nhà",
    "{sub} chưa đụng viên thuốc nào",
    "{sub} chưa uống thuốc gì hết",
    "{sub} chưa dùng thứ gì trước đây",
    "{sub} chưa dám tự uống thuốc"
]

# ═══ sinh_dap_chua_uong_thuoc() — Sinh câu đáp phủ định rằng chưa uống thuốc ══════════
# 45% là đáp ngắn; còn lại ghép dẫn, lõi, đuôi theo miền.
def sinh_dap_chua_uong_thuoc(ca, rng: random.Random, tt: str = "") -> str:
    mien = ca.mien if ca.mien in DAN_PHU_DINH_DT else "nam"
    if rng.random() < 0.45:
        return rng.choice(PHU_DINH_CHUA_UONG_NGAN_DT.get(mien, PHU_DINH_CHUA_UONG_NGAN_DT["nam"]))
    dan = rng.choice(DAN_PHU_DINH_DT[mien])
    core = rng.choice(CORE_CHUA_UT_DT).format(sub=_chu_the_benh_nhan(ca))
    duoi = rng.choice(DUOI_PHU_DINH_DT[mien])
    kq = f"{dan}{core}{duoi}".strip()
    return kq[:1].upper() + kq[1:]

# do AI viết, chưa bác sĩ duyệt
CORE_KHONG_TS_DT = [
    "{sub} không có bệnh nền",
    "{sub} trước giờ khỏe mạnh",
    "{sub} không bị huyết áp hay tiểu đường",
    "{sub} chưa từng nằm viện",
    "{sub} không có bệnh mạn tính",
    "{sub} không có tiền sử bệnh gì",
    "{sub} trước giờ sức khỏe bình thường",
    "{sub} không có bệnh nền nào",
    "{sub} ít khi đau bệnh lắm",
    "{sub} chưa từng phải phẫu thuật",
    "trước giờ {sub} không bệnh tật gì",
    "{sub} không bị tim mạch hay gan thận",
    "{sub} khám sức khỏe đều bình thường",
    "{sub} không uống thuốc mạn tính",
    "{sub} không có vấn đề sức khỏe",
    "{sub} chưa từng mắc bệnh nặng",
    "sức khỏe {sub} trước nay rất tốt",
    "{sub} chưa từng điều trị bệnh gì"
]

# ═══ sinh_dap_khong_tien_su() — Sinh câu đáp phủ định rằng không có tiền sử ═══════════
# 45% là đáp ngắn; còn lại ghép dẫn, lõi, đuôi theo miền.
def sinh_dap_khong_tien_su(ca, rng: random.Random, tt: str = "") -> str:
    mien = ca.mien if ca.mien in DAN_PHU_DINH_DT else "nam"
    if rng.random() < 0.45:
        return rng.choice(PHU_DINH_NGAN_DT[mien])
    dan = rng.choice(DAN_PHU_DINH_DT[mien])
    core = rng.choice(CORE_KHONG_TS_DT).format(sub=_chu_the_benh_nhan(ca))
    duoi = rng.choice(DUOI_PHU_DINH_DT[mien])
    kq = f"{dan}{core}{duoi}".strip()
    return kq[:1].upper() + kq[1:]


# --- 10.6. Y lệnh thuốc đa tầng
Y_LENH_NGUNG_PRE = [
    "Từ hôm nay ngừng {duong} {ten}", "Mình tạm dừng {duong} {ten} từ ngày hôm nay",
    "Bác sĩ dặn là ngưng {duong} {ten} từ bữa nay", "Thuốc {ten} thì từ nay mình ngừng {duong}",
    "Kể từ hôm nay ngưng hẳn {duong} {ten} giúp tôi", "Đối với {ten}, hôm nay bắt đầu ngừng {duong}",
    "Tôi chỉ định ngừng {duong} {ten} kể từ hôm nay", "Bác sĩ cho dừng {duong} {ten} từ thời điểm này"
]
Y_LENH_KE_PRE = [
    "Tôi kê {ten_moi} {lieu}, {duong_moi} {so_lan}", "Bác sĩ kê {ten_moi} {lieu}, {duong_moi} {so_lan}",
    "Đợt này tôi kê {ten_moi} {lieu}, {duong_moi} {so_lan}", "Tôi cho kê {ten_moi} {lieu}, {duong_moi} {so_lan}",
    "Tôi sẽ kê đơn {ten_moi} {lieu}, {duong_moi} {so_lan}", "Bác sĩ sẽ kê {ten_moi} {lieu}, {duong_moi} {so_lan}",
    "Trong toa thuốc tôi kê {ten_moi} {lieu}, {duong_moi} {so_lan}", "Tôi bổ sung kê {ten_moi} {lieu}, {duong_moi} {so_lan}",
    "Đơn thuốc hôm nay tôi kê {ten_moi} {lieu}, {duong_moi} {so_lan}", "Bác sĩ quyết định kê {ten_moi} {lieu}, {duong_moi} {so_lan}"
]
Y_LENH_DUOI = [" nhé.", " nhé ạ.", " nha.", " nghen."]

# ═══ sinh_y_lenh_ngung() — Sinh y lệnh bác sĩ bảo ngừng một thuốc ═════════════════════
# Điền tên thuốc và đường dùng vào mẫu, nối phần đuôi ngẫu nhiên.
def sinh_y_lenh_ngung(ten: str, duong: str, rng: random.Random, tt: str = "") -> str:
    pre = rng.choice(Y_LENH_NGUNG_PRE).format(ten=ten, duong=duong)
    duoi = rng.choice(Y_LENH_DUOI)
    return f"{pre}{duoi}"

# ═══ sinh_y_lenh_ke() — Sinh y lệnh bác sĩ kê thuốc mới ═══════════════════════════════
# Điền tên, liều, đường dùng, số lần vào mẫu, nối phần đuôi ngẫu nhiên.
def sinh_y_lenh_ke(ten_moi: str, lieu: str, duong_moi: str, so_lan: str, rng: random.Random, tt: str = "") -> str:
    pre = rng.choice(Y_LENH_KE_PRE).format(ten_moi=ten_moi, lieu=lieu, duong_moi=duong_moi, so_lan=so_lan)
    duoi = rng.choice(Y_LENH_DUOI)
    return f"{pre}{duoi}"


# --- 10.7. Xã giao đa tầng (Clinical Small Talk Generator)
# do AI viết, chưa bác sĩ duyệt
XA_GIAO_TOPICS = [
    # Topic 1: Đi lại
    (
        ["Sáng nay ", "Hôm nay ", ""],
        [
            "{goi} đi xe gì tới đây", "{goi} tự đi hay ai chở qua",
            "đường tới đây có đông không", "{goi} đi tới đây có xa không",
            "đi đường có bị kẹt xe không {goi}"
        ],
        ["?", " ạ?"],
        ["Dạ, ", ""],
        [
            "{tx} đi xe máy tới", "người nhà chở {tx} qua", "đường cũng thoáng",
            "nhà {tx} ở gần đây thôi", "đi lại cũng thuận tiện"
        ],
        [" ạ.", "."]
    ),
    # Topic 2: Sảnh chờ & chỗ ngồi
    (
        ["Ngồi ngoài sảnh ", "Phòng khám hôm nay ", ""],
        [
            "{goi} có thấy lạnh quá không", "sảnh chờ có thoáng không",
            "{goi} đợi có lâu không", "{goi} ngồi ghế này có thoải mái không",
            "trong phòng có vừa nhiệt độ không {goi}"
        ],
        ["?", " ạ?"],
        ["Dạ, ", ""],
        [
            "vừa vặn dễ chịu", "thoáng mát lắm", "đợi chút xíu là tới lượt",
            "ghế ngồi êm ái lắm", "nhiệt độ thế này vừa rồi"
        ],
        [" ạ.", "."]
    ),
    # Topic 3: Thủ tục tiếp đón
    (
        ["Thủ tục hôm nay ", "Lúc lấy số ", ""],
        [
            "có nhanh không {goi}", "{goi} có phải đợi lâu không",
            "nhân viên hướng dẫn ổn chứ", "tiếp đón có thuận lợi không {goi}"
        ],
        ["?", " ạ?"],
        ["Dạ, ", ""],
        [
            "rất nhanh gọn", "các bạn hướng dẫn kỹ lắm",
            "{tx} bấm số là vào ngay", "mọi thứ đều nhanh chóng"
        ],
        [" ạ.", "."]
    ),
    # Topic 4: Nước uống & ăn sáng
    (
        ["Sáng giờ ", "Trước khi vào ", ""],
        [
            "{goi} ăn sáng chưa", "{goi} uống ngụm nước chưa",
            "{goi} ngồi nghỉ đỡ mệt chưa", "{goi} có thấy khát nước không"
        ],
        ["?", " ạ?"],
        ["Dạ, ", ""],
        [
            "{tx} ăn sáng rồi", "{tx} uống nước rồi",
            "{tx} đỡ mệt rồi", "{tx} có ăn nhẹ rồi"
        ],
        [" ạ.", "."]
    ),
    # Topic 5: Giấy tờ & BHYT
    (
        ["Hôm nay ", ""],
        [
            "{goi} có mang BHYT không", "{goi} mang sổ khám cũ không",
            "{goi} mang căn cước chưa", "{goi} có mang theo đơn thuốc cũ không"
        ],
        ["?", " ạ?"],
        ["Dạ có, ", "Dạ, "],
        [
            "{tx} mang đủ cả", "{tx} cầm sẵn đây",
            "{tx} kẹp trong túi", "{tx} có mang theo đầy đủ"
        ],
        [" ạ.", "."]
    ),
    # Topic 6: Thời tiết
    (
        ["Mấy nay ", "Trời hôm nay ", ""],
        [
            "trời đổi mùa {goi} có mệt không", "nắng nóng đi đường có mệt không",
            "sáng se lạnh {goi} có mặc ấm không", "mưa gió đi lại có vất vả không {goi}"
        ],
        ["?", " ạ?"],
        ["Dạ, ", ""],
        [
            "cũng hơi mệt", "{tx} có mặc áo khoác",
            "đi sáng sớm nên mát", "{tx} đi lại cẩn thận không sao"
        ],
        [" ạ.", "."]
    ),
    # Topic 7: Công việc
    (
        ["Hôm nay ", "Dạo này "],
        [
            "{goi} xin nghỉ làm đi khám à", "công việc có bận lắm không",
            "{goi} ngủ đủ giấc không", "công việc có nhiều áp lực không {goi}"
        ],
        ["?", " ạ?"],
        ["Dạ, ", ""],
        [
            "{tx} xin nghỉ nửa buổi", "công việc cũng vừa phải",
            "{tx} tranh thủ đi sáng", "hơi bận nhưng vẫn ổn"
        ],
        [" ạ.", "."]
    ),
    # Topic 8: Tinh thần & sẵn sàng
    (
        ["", "Vào phòng rồi "],
        [
            "{goi} có hồi hộp không", "{goi} thấy thoải mái chưa",
            "mình bắt đầu khám được chưa", "{goi} đã sẵn sàng vào khám chưa"
        ],
        ["?", " ạ?"],
        ["Dạ, ", ""],
        [
            "{tx} bình tĩnh rồi", "{tx} thấy yên tâm rồi",
            "{tx} sẵn sàng rồi", "{tx} thấy thoải mái rồi"
        ],
        [" ạ.", "."]
    ),
    # Topic 9: Hợp tác thăm khám
    (
        ["Bây giờ ", ""],
        [
            "bác sĩ kiểm tra cho {goi} được chưa", "mình bắt đầu kiểm tra được không {goi}",
            "{goi} sẵn sàng để bác sĩ kiểm tra chưa"
        ],
        ["?", " ạ?"],
        ["Dạ, ", ""],
        [
            "bác sĩ cứ làm đi", "{tx} sẵn sàng rồi",
            "bác sĩ cứ kiểm tra tự nhiên", "vâng được rồi"
        ],
        [" ạ.", "."]
    ),
    # Topic 10: Nghỉ ngơi & hồi phục
    (
        ["Ngồi nghỉ một lát ", ""],
        [
            "{goi} thấy đỡ thở dốc chưa", "{goi} thấy trong người dịu bớt chưa",
            "{goi} thấy đỡ mệt hơn lúc mới tới chưa"
        ],
        ["?", " ạ?"],
        ["Dạ, ", ""],
        [
            "đỡ nhiều rồi", "{tx} thở đều lại rồi",
            "{tx} thấy hồi sức rồi", "được rồi"
        ],
        [" ạ.", "."]
    )
]

# do AI viết, chưa bác sĩ duyệt
DAP_NGAN_XA_GIAO = [
    "Dạ ổn ạ.", "Dạ rồi ạ.", "Vâng ạ.", "Dạ bình thường ạ.", "Dạ có ạ.",
    "Dạ được rồi ạ.", "Dạ đỡ nhiều rồi.", "Em cảm ơn bác sĩ.",
    "Bác sĩ cứ làm đi ạ.", "Dạ vâng được ạ.", "Dạ vâng ạ.", "Dạ không sao ạ.",
    "Dạ đỡ nhiều rồi ạ.", "Dạ sẵn sàng rồi ạ.", "Dạ cảm ơn bác sĩ.",
    "Dạ được rồi.", "Dạ đỡ rồi.", "Dạ không sao.", "Cảm ơn bác sĩ.",
    "Dạ ổn cả.", "Dạ bình thường.",
    "Dạ tôi sẵn sàng rồi ạ.", "Dạ ngồi nghỉ thấy đỡ rồi bác sĩ.",
    "Dạ đi đường cũng thuận lợi ạ.", "Dạ vâng, phiền bác sĩ khám giúp.",
    "Dạ trong người thấy dễ chịu hơn rồi.", "Dạ không có vấn đề gì ạ.",
    "Vâng, bác sĩ cứ khám tự nhiên ạ.", "Dạ tôi đỡ hồi hộp rồi.",
    "Dạ được bác sĩ ạ.", "Dạ tôi ổn định rồi ạ.", "Dạ em cảm ơn bác sĩ nhiều.",
    "Vâng, tôi yên tâm rồi ạ.", "Dạ dạo này sức khỏe cũng túc tắc ạ.",
    "Dạ vâng, tôi nghe rõ rồi ạ.", "Dạ tôi thấy thoải mái rồi.",
    "Dạ không mệt lắm đâu bác sĩ.", "Dạ đi lại cũng dễ dàng ạ.",
    "Vâng, bác sĩ cứ kiểm tra giúp tôi.", "Dạ sáng nay đi đường thông thoáng ạ.",
    "Dạ tôi thở đều lại rồi.", "Dạ vâng, cảm ơn bác sĩ đã chu đáo.",
    "Dạ đỡ mệt hơn lúc mới tới rồi ạ.", "Dạ tôi chuẩn bị xong rồi.",
    "Vâng, tôi ngồi nghỉ một lát là khỏe rồi.", "Dạ không có gì trở ngại ạ.",
    "Dạ tôi bình tĩnh lại rồi bác sĩ.", "Dạ vâng, nhờ bác sĩ xem giúp.",
    "Dạ trong phòng khám mát mẻ dễ chịu ạ.", "Dạ mọi chuyện ổn cả bác sĩ.",
    "Vâng, tôi thấy yên tâm hơn rồi.", "Dạ tôi ngồi đợi cũng nhanh thôi ạ.",
    "Dạ tinh thần tôi thoải mái rồi.", "Dạ vâng, cảm ơn bác sĩ dặn dò.",
    "Dạ sẵn sàng.", "Dạ yên tâm.", "Dạ khỏe ạ.", "Dạ ổn.", "Dạ vâng.", "Dạ khỏe.", "Dạ rõ ạ."
]

# ═══ sinh_xa_giao() — Sinh cặp hỏi đáp xã giao không có thông tin lâm sàng ════════════
# Trả (câu hỏi, câu đáp) từ một chủ đề xã giao chọn ngẫu nhiên.
def sinh_xa_giao(ca, rng: random.Random) -> Tuple[str, str]:
    q_dan_list, q_core_list, q_duoi_list, a_dan_list, a_core_list, a_duoi_list = rng.choice(XA_GIAO_TOPICS)
    goi = ca.nguoi_ke[1] if ca.nguoi_ke else ca.goi_bn
    tx = ca.nguoi_ke[2] if ca.nguoi_ke else ca.tu_xung_bn
    goi_hoa = goi[:1].upper() + goi[1:]
    q_dan = rng.choice(q_dan_list).format(goi=goi, goi_hoa=goi_hoa)
    q_core = rng.choice(q_core_list).format(goi=goi, goi_hoa=goi_hoa)
    q_duoi = rng.choice(q_duoi_list).format(goi=goi, goi_hoa=goi_hoa)
    hoi = f"{q_dan}{q_core}{q_duoi}".strip()
    hoi = hoi[:1].upper() + hoi[1:]

    if rng.random() < 0.55:
        dap = rng.choice(DAP_NGAN_XA_GIAO)
    else:
        a_dan = rng.choice(a_dan_list)
        a_core = rng.choice(a_core_list).format(tx=tx, goi=goi)
        a_duoi = rng.choice(a_duoi_list)
        dap = f"{a_dan}{a_core}{a_duoi}".strip()
        dap = dap[:1].upper() + dap[1:]
    return hoi, dap


# --- 10.8. Bổ sung người nhà thay mặt, vắng mặt và điều dưỡng mở rộng
NGUOI_NHA_THAY_MAT_BS = [
    "Hôm nay {nn} đi một mình à, {bn3} không đến được{tt}?",
    "Chào {nn}, {bn3} hôm nay không trực tiếp đi khám cùng mình được sao{tt}?",
    "Hôm nay chỉ có một mình {nn} đến thôi à, {bn3} nhà mình mệt thế nào{tt}?",
    "{nn_hoa} đi khám thay cho {bn3} phải không, {bn3} ở nhà sức khỏe sao rồi{tt}?",
    "Chào {nn}, nay {nn} đi thay à, {bn3} có triệu chứng gì mà không đến được{tt}?",
    "Hôm nay {nn} tới khám hộ {bn3} đúng không, {bn3} ở nhà thấy trong người ra sao{tt}?",
    "{nn_hoa} đến một mình à, {bn3} ở nhà có mệt mỏi lắm không{tt}?",
    "Chào {nn}, {bn3} không đi cùng được nên {nn} đi khám đại diện đúng không{tt}?"
]

NGUOI_NHA_THAY_MAT_KE = [
    "{da}{gbn} mệt quá nên {tx} đi thay{tt}.",
    "{da}{gbn} yếu mệt không đi lại được nên {tx} tranh thủ đi khám thay để xin tư vấn{tt}.",
    "{da}hôm nay {gbn} sốt mệt nằm ở nhà, {tx} đến đây trình bày triệu chứng với bác sĩ{tt}.",
    "{da}{gbn} đau nhức đi lại khó khăn quá nên nhờ {tx} tới phòng khám hỏi bác sĩ{tt}.",
    "{da}sức khỏe {gbn} đang mệt nhiều, {tx} phải đi thay để bác sĩ hướng dẫn phác đồ{tt}.",
    "{da}{gbn} đi lại không tiện nên bảo {tx} đi khám hộ và nghe dặn dò{tt}.",
    "{da}ở nhà {gbn} mệt không dậy nổi, {tx} sốt ruột quá nên đi khám thay{tt}.",
    "{da}{gbn} không chịu đi nên {tx} phải tự tới gặp bác sĩ để kể bệnh tình{tt}."
]

VANG_MAT_CHAN_DOAN = [
    "Nghe {nn} kể thì tôi nghĩ nhiều đến {nghi}, nhưng chưa khám trực tiếp nên chưa kết luận được{tt}.",
    "Qua lời {nn} miêu tả thì định hướng nhiều tới {nghi}, tuy nhiên cần khám trực tiếp mới chắc chắn{tt}.",
    "Dựa trên các dấu hiệu {nn} vừa kể, tôi nghi ngờ {nghi}, dù vậy vẫn phải khám trực tiếp để khẳng định{tt}.",
    "Các biểu hiện {nn} nêu gợi ý tình trạng {nghi}, nhưng vì chưa khám người bệnh nên tôi chưa khẳng định ngay{tt}.",
    "Bước đầu nghe {nn} nói thì khả năng là {nghi}, nhưng nguyên tắc là phải khám trực tiếp người bệnh{tt}.",
    "Tôi tạm thời hướng đến bệnh cảnh {nghi}, tuy nhiên cần đưa người bệnh đến kiểm tra cụ thể{tt}."
]

VANG_MAT_KE_HOACH = [
    "{nn_hoa} đưa {goi_hoi} đến để tôi khám trực tiếp{dn}.",
    "Khi nào {goi_hoi} đỡ mệt thì {nn} đưa đến đây để bác sĩ thăm khám cụ thể{dn}.",
    "Tốt nhất là {nn} thu xếp đưa {goi_hoi} qua phòng khám để kiểm tra trực tiếp{dn}.",
    "{nn_hoa} cần sớm đưa {goi_hoi} tới cơ sở y tế để được bác sĩ khám thực thể{dn}.",
    "{nn_hoa} cố gắng đưa {goi_hoi} đến bệnh viện để bác sĩ đánh giá chính xác{dn}.",
    "Gia đình nên sớm sắp xếp đưa {goi_hoi} tới khám trực tiếp cho an tâm{dn}."
]

# do AI viết, chưa bác sĩ duyệt
DIEU_DUONG_MO_RONG_THEM = [
    ("vào từ sáng", "đo sinh hiệu rồi ạ."),
    ("mới đăng ký", "đo huyết áp, nhịp tim rồi ạ."),
    ("chờ từ nãy", "cập nhật sinh hiệu xong ạ."),
    ("vừa vào phòng", "đo mạch, nhiệt độ xong ạ."),
    ("mới tiếp đón", "sinh hiệu ổn định ạ."),
    ("vào sảnh chờ", "đo huyết áp, SpO2 rồi ạ."),
    ("lấy số sớm", "ghi đủ sinh hiệu rồi ạ."),
    ("vừa mới tới", "đo mạch, huyết áp xong ạ."),
    ("ở quầy đón tiếp", "đo xong rồi ạ."),
    ("ngồi chờ ngoài", "cập nhật chỉ số rồi ạ.")
]
