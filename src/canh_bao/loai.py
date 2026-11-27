# -*- coding: utf-8 -*-
"""[Lớp cảnh báo]
Làm gì   : Định nghĩa chung của lớp cảnh báo: các loại lỗi, cấu trúc một cảnh báo và mức
           nghiêm trọng.
Đọc từ   : class Loai các loại lỗi; class CanhBao một cảnh báo; muc_do() mức nghiêm trọng
Mục lục (các hàm/lớp chính):
  class Loai     Mô tả một mã cảnh báo: nhóm, tiêu đề, mức gốc
  class CanhBao  Một cảnh báo: mã, lượt, câu trích, lý do, kết luận
  muc_do()       Tính mức nghiêm trọng theo loại thông tin
Dùng bởi : canh_bao/asr, canh_bao/bo_sot, canh_bao/gop, canh_bao/lam_sang, canh_bao/nhat_ky,
           canh_bao/phat_hien, canh_bao/toan_ca, do_luong/do_canh_bao
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Tầng 6 — LỚP CẢNH BÁO: phân loại lỗi, lược đồ một cảnh báo, mức nghiêm trọng.

VÌ SAO TÁCH KHỎI `khoa_bang_chung` VÀ `cong_rui_ro`.
Khoá trả lời "phát biểu này có được vào thân không" bằng BỐN câu hỏi (nguồn, nội
dung, chủ thể, mức khẳng định). Lớp này trả lời một câu khác: "nếu phát biểu này
sai thì SAI KIỂU GÌ, và bác sĩ cần nhìn vào đâu". Một phát biểu có thể qua khoá mà
vẫn mang cảnh báo (liều "5 mg" trong khi lượt dẫn nói "50 mg" — khoá K6 chỉ so
nguyên chuỗi với trường `lieu`, không đọc số trong `noi_dung`).

CẢNH BÁO KHÔNG PHẢI TRẠNG THÁI. Trạng thái đầu ra vẫn là ba:
    đã kiểm chứng          vao than ban nhap
    cần xác nhận           chi vao muc CẦN XÁC NHẬN
    bị phủ định/thay thế   không vào thân, giữ dấu vết
Cảnh báo là LÝ DO một phát biểu cần được chú ý. Chính sách D (`gop.trang_thai_D`)
quyết định cảnh báo nào đủ nặng để đổi trạng thái; chính sách C (đang dùng để đo)
KHÔNG đổi.

HAI TRỤC TÁCH RIÊNG — không nhân với nhau thành một điểm:
    muc_do    NẾU thông tin này sai thì hậu quả lớn đến đâu (theo LOẠI thông tin:
              dị ứng, thuốc > chẩn đoán > thời gian > khác)
    bat_dinh  căn cứ của CẢNH BÁO NÀY yếu hay mờ đến đâu: "thấp" = có bằng chứng
              rõ ràng cho thấy lỗi (số trong lượt dẫn khác số trong bản ghi);
              "cao" = chỉ là dấu hiệu gián tiếp
Dị ứng có căn cứ tốt vẫn nghiêm trọng nếu sai: mức độ cao, bất định thấp.

BA LOẠI KẾT LUẬN — một cảnh báo không chứng minh output sai:
    loi_phat_hien      có bằng chứng đối nghịch rõ (detected_error)
    nghi_rui_ro        thiếu bằng chứng khẳng định, hoặc dấu hiệu gián tiếp
    can_xem            chất lượng/ghi chú cho bác sĩ, không đổi trạng thái
"""
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

# 24/09/2026 (tôi): thêm AMBIGUOUS_LAY_TERM (cách nói dân gian nhiều nghĩa).
PHIEN_BAN = "canh-bao-2026-09-24b"

# ----------------------------------------------------------------- nhóm lớn
NHOM = {
    "UNSUPPORTED": "Thông tin không có căn cứ",
    "OMISSION": "Có thể bỏ sót",
    "SUBJECT_ATTRIBUTION": "Gán sai người",
    "NEGATION_ASSERTION": "Sai khẳng định / phủ định / mức chắc chắn",
    "TEMPORAL": "Sai thời gian",
    "STATE_UPDATE": "Sai cập nhật thông tin",
    "ENTITY_VALUE": "Sai tên thuốc, số liệu, vị trí",
    "RELATION_CAUSALITY": "Sai liên hệ, nguyên nhân",
    "PLAN_FACT_CONDITIONAL": "Nhầm kế hoạch, điều kiện với sự việc",
    "EVIDENCE_PROVENANCE": "Căn cứ hoặc nguồn chưa đủ",
    "QUALITY": "Chất lượng bản ghi",
    # Lỗi TRƯỚC khâu AI (chép âm). Tách riêng: không tính là lỗi của mô hình sinh.
    "ASR_UPSTREAM": "Bản chép âm chưa chắc",
    # Thêm 25/11/2026: kiểm tra dựa trên tri thức thuốc (liều, tương tác, dị ứng). Không phải lỗi
    # của bản ghi mà là điều bác sĩ cần xem; đọc số từ `tri_thuc_thuoc` (chưa duyệt -> cần xem).
    "CLINICAL_KNOWLEDGE": "Kiến thức lâm sàng (liều, tương tác, dị ứng)",
}

LOI_PHAT_HIEN = "loi_phat_hien"
NGHI_RUI_RO = "nghi_rui_ro"
CAN_XEM = "can_xem"

CAO, TRUNG, THAP = "cao", "trung", "thap"
_HANG = {THAP: 0, TRUNG: 1, CAO: 2}

# Độ tin cậy của CHÍNH bộ phát hiện — không phải của cảnh báo.
ON_DINH = "on_dinh"                  # có phép kiểm dương/âm/âm khó; dùng cho chính sách D
THU_NGHIEM = "thu_nghiem"            # experimental: chỉ hiện, không đổi trạng thái
CHUA_TIN_CAY = "chua_tin_cay"        # not_reliably_detectable_yet: không có bộ phát hiện


# ═══ class Loai — Mô tả một mã cảnh báo: nhóm, tiêu đề, mức gốc ═══════════════════════
# Gồm nhóm, tiêu đề cho bác sĩ, giải thích, mức gốc, thứ tự ưu tiên, độ tin cậy.
@dataclass(frozen=True)
class Loai:
    nhom: str
    tieu_de: str            # câu ngắn hiện cho bác sĩ
    giai_thich: str         # một câu, lời thường
    muc_goc: str            # mức nghiêm trọng trước khi xét loại thông tin
    uu_tien: int            # nhỏ = xem trước (mục 37 của đặc tả)
    tin_cay: str = ON_DINH


# ─── _l() — Tạo một dòng mô tả mã cảnh báo ────────────────────────────────────────────
def _l(nhom, tieu_de, giai_thich, muc_goc, uu_tien, tin_cay=ON_DINH):
    return Loai(nhom, tieu_de, giai_thich, muc_goc, uu_tien, tin_cay)


# ----------------------------------------------------------------- bảng mã
# Chỉ khai những mã CÓ bộ phát hiện (hoặc ánh xạ từ khoá). Mã trong đặc tả mà
# chưa phát hiện được nằm ở CHUA_PHAT_HIEN bên dưới, kèm lý do — không giả vờ.
LOAI: Dict[str, Loai] = {
    # --- chủ thể (ưu tiên 1)
    "WRONG_SUBJECT": _l("SUBJECT_ATTRIBUTION", "Có thể gán sai người",
                        "Câu gốc nói về một người khác, nhưng bản ghi gán cho người này.", CAO, 1),
    "FAMILY_PATIENT_MIXUP": _l("SUBJECT_ATTRIBUTION", "Có thể lẫn người nhà với bệnh nhân",
                               "Câu gốc có nhắc người nhà; thông tin có thể không phải của bệnh nhân.", CAO, 1),
    "SPEAKER_SUBJECT_MISMATCH": _l("SUBJECT_ATTRIBUTION", "Người nói không phải người bệnh",
                                   "Máy gán chủ thể theo người nói; câu gốc không nói rõ là của ai.", TRUNG, 3),
    "SUBJECT_AMBIGUOUS": _l("SUBJECT_ATTRIBUTION", "Chưa rõ thông tin của ai",
                            "Câu gốc không đủ để biết thông tin thuộc về ai.", TRUNG, 3),
    # --- phủ định, mức chắc chắn (ưu tiên 2, 9)
    "NEGATION_FLIP": _l("NEGATION_ASSERTION", "Có thể đảo ngược có/không",
                        "Câu trả lời trong hội thoại ngược với bản ghi.", CAO, 2),
    "UNKNOWN_AS_NEGATIVE": _l("NEGATION_ASSERTION", "“Không nhớ” bị ghi thành “không có”",
                              "Người nói chỉ nói không nhớ hoặc không rõ; bản ghi lại ghi là không có.", CAO, 2),
    "NOT_YET_AS_NEGATIVE": _l("NEGATION_ASSERTION", "“Chưa ghi nhận” bị ghi thành “không có”",
                              "Câu gốc là chưa thấy, chưa làm; bản ghi ghi thành phủ định chắc chắn.", CAO, 2),
    "NEGATION_SCOPE_ERROR": _l("NEGATION_ASSERTION", "Chữ “không” bác lời người khác, không phủ định triệu chứng",
                               "Câu gốc “không đúng đâu…” là cãi lại câu trước; phần sau vẫn là khẳng định.", CAO, 2),
    "POSSIBLE_NEGATION_ERROR": _l("NEGATION_ASSERTION", "Câu gốc có từ phủ định",
                                  "Đoạn làm căn cứ có từ phủ định nhưng bản ghi là khẳng định.", TRUNG, 4),
    "CERTAINTY_INCREASED": _l("NEGATION_ASSERTION", "Nghi ngờ bị ghi thành chắc chắn",
                              "Câu gốc chỉ nghi ngờ hoặc chưa chắc; bản ghi khẳng định.", CAO, 9),
    "APPROXIMATION_LOST": _l("NEGATION_ASSERTION", "Mất chữ “khoảng”",
                             "Câu gốc nói con số ước chừng; bản ghi ghi như số chính xác.", THAP, 20),
    # --- thuốc, dị ứng, bịa (ưu tiên 3-6)
    "FABRICATED_MEDICATION": _l("UNSUPPORTED", "Tên thuốc không có trong hội thoại",
                                "Không lượt nào trong hội thoại nhắc tên thuốc này.", CAO, 3),
    "FABRICATED_ALLERGY": _l("UNSUPPORTED", "Chất gây dị ứng không có trong hội thoại",
                             "Không lượt nào trong hội thoại nhắc chất này.", CAO, 4),
    "MEDICATION_ENTITY_MISMATCH": _l("ENTITY_VALUE", "Tên thuốc không có ở lượt được dẫn",
                                     "Tên thuốc có trong hội thoại nhưng không ở lượt làm căn cứ.", CAO, 5),
    "ALLERGEN_MISMATCH": _l("ENTITY_VALUE", "Chất gây dị ứng không có ở lượt được dẫn",
                            "Chất gây dị ứng có trong hội thoại nhưng không ở lượt làm căn cứ.", CAO, 5),
    "DOSE_MISMATCH": _l("ENTITY_VALUE", "Liều thuốc không khớp", "Liều trong bản ghi khác liều trong hội thoại.", CAO, 6),
    "FREQUENCY_MISMATCH": _l("ENTITY_VALUE", "Số lần dùng không khớp",
                             "Số lần trong bản ghi khác số lần trong hội thoại.", CAO, 6),
    "ROUTE_MISMATCH": _l("ENTITY_VALUE", "Đường dùng thuốc không khớp",
                         "Đường dùng (uống, xịt, bôi…) không có ở lượt được dẫn.", CAO, 6),
    "UNIT_MISMATCH": _l("ENTITY_VALUE", "Sai đơn vị", "Cùng con số nhưng đơn vị khác với hội thoại.", CAO, 6),
    "DECIMAL_MISMATCH": _l("ENTITY_VALUE", "Lệch dấu thập phân", "Con số lệch gấp 10 lần so với hội thoại.", CAO, 6),
    "DURATION_MISMATCH": _l("ENTITY_VALUE", "Khoảng thời gian không khớp",
                            "Số ngày, tuần, tháng trong bản ghi khác hội thoại.", TRUNG, 10),
    "NUMERIC_MISMATCH": _l("ENTITY_VALUE", "Con số không khớp", "Con số trong bản ghi không có trong lượt được dẫn.", TRUNG, 12),
    "RANGE_COLLAPSED": _l("ENTITY_VALUE", "Khoảng số bị rút thành một số",
                          "Câu gốc nói một khoảng (ví dụ 3–4 ngày); bản ghi chỉ giữ một số.", THAP, 20),
    "LATERALITY_CHANGED": _l("ENTITY_VALUE", "Sai bên trái/phải", "Bên trong bản ghi ngược với câu gốc.", CAO, 6),
    "SEVERITY_CHANGED": _l("ENTITY_VALUE", "Sai mức độ", "Mức độ (nhẹ/nặng) trong bản ghi khác câu gốc.", TRUNG, 14),
    "FREQUENCY_WORD_CHANGED": _l("ENTITY_VALUE", "Sai tần suất", "“Thỉnh thoảng” và “thường xuyên” bị đổi cho nhau.", TRUNG, 14),
    # --- thời gian, trạng thái dùng thuốc (ưu tiên 7, 10)
    "DISCONTINUED_AS_CURRENT": _l("TEMPORAL", "Thuốc đã ngừng bị ghi là đang dùng",
                                  "Câu gốc nói đã ngừng hoặc bỏ thuốc; bản ghi ghi đang dùng.", CAO, 7),
    "PAST_CURRENT_CONFUSION": _l("TEMPORAL", "Nhầm trước đây với hiện tại",
                                 "Câu gốc nói chuyện trước đây; bản ghi ghi như hiện tại, hoặc ngược lại.", TRUNG, 10),
    "TEMPORAL_MISMATCH": _l("TEMPORAL", "Mốc thời gian không thấy trong câu gốc",
                            "Mốc thời gian trong bản ghi không có ở lượt được dẫn.", TRUNG, 10),
    # --- kế hoạch, điều kiện (ưu tiên 8)
    "CONDITION_AS_FACT": _l("PLAN_FACT_CONDITIONAL", "Câu điều kiện bị ghi thành sự việc",
                            "Câu gốc có “nếu…”; bản ghi ghi như đã xảy ra.", CAO, 8),
    "CONDITION_AS_CONFIRMED_PLAN": _l("PLAN_FACT_CONDITIONAL", "Kế hoạch có điều kiện bị ghi thành chắc chắn",
                                      "Câu gốc là “nếu… thì…”; bản ghi bỏ mất điều kiện.", CAO, 8),
    "PLAN_AS_FACT": _l("PLAN_FACT_CONDITIONAL", "Kế hoạch bị ghi thành việc đã làm",
                       "Câu gốc nói sẽ làm; bản ghi ghi như đã làm hoặc đang có.", CAO, 8),
    "PLANNED_TEST_AS_RESULT": _l("PLAN_FACT_CONDITIONAL", "Xét nghiệm chưa làm bị ghi thành có kết quả",
                                 "Câu gốc nói sẽ làm hoặc chưa làm xét nghiệm; bản ghi có kết quả.", CAO, 8),
    "RECOMMENDATION_AS_FACT": _l("PLAN_FACT_CONDITIONAL", "Lời dặn bị ghi thành việc bệnh nhân đã làm",
                                 "Câu gốc là bác sĩ khuyên hoặc dặn; bản ghi ghi như sự việc.", TRUNG, 8),
    "QUESTION_AS_FACT": _l("PLAN_FACT_CONDITIONAL", "Câu hỏi bị ghi thành sự việc",
                           "Căn cứ chỉ là câu hỏi của bác sĩ, không có câu trả lời xác nhận.", CAO, 8),
    "FAMILY_STATEMENT_AS_CLINICIAN_PLAN": _l("PLAN_FACT_CONDITIONAL", "Ý của người nhà bị ghi thành kế hoạch của bác sĩ",
                                             "Căn cứ chỉ là lời người bệnh hoặc người nhà, không phải bác sĩ.", TRUNG, 8),
    # --- cập nhật trạng thái (ưu tiên 11)
    "CORRECTION_NOT_APPLIED": _l("STATE_UPDATE", "Giữ giá trị đã được đính chính",
                                 "Người nói đã sửa lại con số; bản ghi còn giữ số cũ.", CAO, 11),
    "OLD_AND_NEW_VALUE_DUPLICATED": _l("STATE_UPDATE", "Giữ cả số cũ lẫn số đã sửa",
                                       "Bản ghi có cả giá trị trước và sau khi đính chính.", TRUNG, 11),
    "CONTRADICTION_UNRESOLVED": _l("STATE_UPDATE", "Hai nguồn nói khác nhau",
                                   "Hai người nói hai thông tin trái nhau; hệ thống không tự chọn bên.", CAO, 11),
    "INTERNAL_CONTRADICTION": _l("STATE_UPDATE", "Bản ghi tự mâu thuẫn",
                                 "Hai dòng trong bản ghi trái nhau (ví dụ “không dị ứng” và “dị ứng X”).", CAO, 11),
    "CONTRADICTORY_MEDICATION_STATUS": _l("STATE_UPDATE", "Thuốc vừa đang dùng vừa đã ngừng",
                                          "Cùng một thuốc có hai trạng thái trái nhau trong bản ghi.", CAO, 11),
    "CONTRADICTORY_INFORMATION": _l("STATE_UPDATE", "Hai dòng có/không trái nhau",
                                    "Cùng một nội dung, một dòng khẳng định, một dòng phủ định.", TRUNG, 11),
    # --- không căn cứ (ưu tiên 12)
    "FABRICATED_QUOTE": _l("UNSUPPORTED", "Câu trích dẫn không có trong hội thoại",
                           "Máy dẫn một câu mà hội thoại không có.", CAO, 12),
    "UNSUPPORTED_INFORMATION": _l("UNSUPPORTED", "Nội dung không khớp câu gốc",
                                  "Nội dung bản ghi không trùng từ nào với đoạn được dẫn.", TRUNG, 12),
    "UNSUPPORTED_BOILERPLATE": _l("UNSUPPORTED", "Câu mẫu không có căn cứ",
                                  "Câu kiểu “không dị ứng”, “khám bình thường” mà hội thoại không nói.", CAO, 12),
    "OVER_NORMALIZATION": _l("UNSUPPORTED", "Diễn đạt thường bị đổi thành thuật ngữ",
                             "Chỉ khớp qua một từ địa phương hoặc khẩu ngữ có nhiều nghĩa.", TRUNG, 15),
    # Thêm 24/09/2026. Khác OVER_NORMALIZATION: cảnh báo cả khi bản ghi chép NGUYÊN VĂN,
    # vì chép nguyên văn "ốm" thì người đọc miền Bắc vẫn hiểu là "bị bệnh". Cụm và câu
    # hỏi lấy từ `dan_gian.BANG` (mục MO_HO).
    "AMBIGUOUS_LAY_TERM": _l("UNSUPPORTED", "Cách nói có nhiều nghĩa, cần hỏi lại",
                             "Người bệnh dùng một cách nói dân gian có hơn một nghĩa hợp lý; "
                             "chưa hỏi lại thì chưa chọn được nghĩa nào.", TRUNG, 15),
    # --- căn cứ, nguồn
    "WRONG_EVIDENCE": _l("EVIDENCE_PROVENANCE", "Dẫn sai lượt", "Lượt được dẫn không tồn tại hoặc không chứa câu trích.", TRUNG, 16),
    "EVIDENCE_MISSING": _l("EVIDENCE_PROVENANCE", "Không có câu trích nguyên văn",
                           "Bản ghi không kèm câu nguyên văn làm căn cứ.", TRUNG, 16),
    "EVIDENCE_CONTEXT_MISSING": _l("EVIDENCE_PROVENANCE", "Thiếu câu hỏi đi kèm",
                                   "Căn cứ là một câu trả lời ngắn; câu hỏi của bác sĩ không được dẫn.", THAP, 21),
    # --- bỏ sót (ưu tiên 13) — ở mức TOÀN CA, không gắn vào phát biểu nào
    "OMITTED_ALLERGY": _l("OMISSION", "Có thể bỏ sót dị ứng", "Hội thoại nhắc dị ứng nhưng bản ghi không có dòng nào dẫn tới.", CAO, 13),
    "OMITTED_MEDICATION": _l("OMISSION", "Có thể bỏ sót thuốc", "Hội thoại nhắc thuốc nhưng bản ghi không có dòng nào dẫn tới.", CAO, 13),
    "OMITTED_NEGATION": _l("OMISSION", "Có thể bỏ sót một câu phủ định", "Người bệnh nói không có một điều gì đó; bản ghi không ghi.", TRUNG, 13),
    "OMITTED_CORRECTION": _l("OMISSION", "Có thể bỏ sót một lần đính chính", "Người nói sửa lại thông tin; bản ghi không dẫn tới.", TRUNG, 13),
    "OMITTED_UNCERTAINTY": _l("OMISSION", "Có thể bỏ sót điều chưa chắc", "Người nói nói chưa chắc; bản ghi không ghi.", THAP, 13),
    "OMITTED_PLAN": _l("OMISSION", "Có thể bỏ sót kế hoạch", "Bác sĩ dặn hoặc chỉ định; bản ghi không ghi.", TRUNG, 13),
    "OMITTED_NUMERIC_VALUE": _l("OMISSION", "Có thể bỏ sót một con số", "Hội thoại có con số (liều, thời gian, chỉ số) không được ghi.", TRUNG, 13),
    "OMITTED_DURATION": _l("OMISSION", "Có thể bỏ sót thời gian bệnh", "Hội thoại nói thời gian bệnh; bản ghi không dẫn tới.", TRUNG, 13),
    # --- kiến thức lâm sàng (25/11/2026) — `canh_bao.lam_sang`, thử nghiệm: chỉ hiện
    "DOSE_OVER_MAX": _l("CLINICAL_KNOWLEDGE", "Liều vượt mức tối đa",
                        "Tổng liều một ngày vượt mức tối đa người lớn trong bảng tri thức thuốc.", CAO, 12, THU_NGHIEM),
    "DRUG_INTERACTION": _l("CLINICAL_KNOWLEDGE", "Có thể có tương tác thuốc",
                           "Hai thuốc người bệnh đang dùng hoặc được kê nằm trong bảng tương tác.", CAO, 12, THU_NGHIEM),
    "CONTRAINDICATION": _l("CLINICAL_KNOWLEDGE", "Kê thuốc người bệnh đang dị ứng",
                           "Thuốc được kê hoặc đang dùng chứa chất mà bản ghi nói người bệnh dị ứng.", CAO, 12, THU_NGHIEM),
    "CROSS_ALLERGY": _l("CLINICAL_KNOWLEDGE", "Nguy cơ dị ứng chéo thuốc",
                        "Thuốc đang dùng hoặc được kê có nguy cơ dị ứng chéo với chất người bệnh dị ứng.",
                        CAO, 12, THU_NGHIEM),
    # Thêm 25/11/2026: cặp "Bác sĩ hỏi — người bệnh đáp ngắn" mà không dòng nào dẫn tới câu đáp.
    # `doan_chua_ghi` không thấy cặp này (bỏ câu hỏi; câu đáp không có từ nội dung).
    "OMITTED_ANSWER": _l("OMISSION", "Có thể bỏ sót một câu trả lời",
                         "Bác sĩ hỏi và người bệnh đã trả lời, nhưng bản ghi không có dòng nào dẫn tới câu trả lời.",
                         CAO, 13, THU_NGHIEM),
    "POSSIBLE_IMPORTANT_OMISSION": _l("OMISSION", "Có đoạn hội thoại chưa được ghi",
                                      "Đoạn có nội dung lâm sàng nhưng không dòng nào dẫn tới.", THAP, 22),
    # --- chất lượng: không đổi trạng thái
    "DUPLICATE_INFORMATION": _l("QUALITY", "Ghi lặp", "Cùng một thông tin xuất hiện hai lần.", THAP, 30),
    "SEMANTIC_DUPLICATE": _l("QUALITY", "Có thể ghi lặp", "Hai dòng gần như cùng nội dung.", THAP, 30),
    # --- thử nghiệm: CHỈ HIỆN, không đổi trạng thái
    "UNSUPPORTED_CAUSALITY": _l("RELATION_CAUSALITY", "Có thể tự suy ra nguyên nhân",
                                "Bản ghi nói “do…” nhưng câu gốc không nói nguyên nhân.", TRUNG, 17, THU_NGHIEM),
    "UNSUPPORTED_FACT_COMBINATION": _l("RELATION_CAUSALITY", "Có thể ghép thông tin của hai người",
                                       "Căn cứ lấy từ lời của hai người khác nhau.", TRUNG, 17, THU_NGHIEM),
    "IMPORTANT_MODIFIER_DROPPED": _l("QUALITY", "Có thể mất chi tiết khi tóm tắt",
                                     "Câu gốc có chi tiết (thỉnh thoảng, về đêm, sau ăn…) không có trong bản ghi.", THAP, 25, THU_NGHIEM),
    "DOCTOR_STATEMENT_AS_PATIENT_FACT": _l("SUBJECT_ATTRIBUTION", "Căn cứ chỉ là lời bác sĩ",
                                           "Bản ghi là lời kể của bệnh nhân nhưng căn cứ chỉ có lời bác sĩ.", THAP, 24, THU_NGHIEM),
    "CLINICALLY_IRRELEVANT": _l("QUALITY", "Có thể không phải thông tin lâm sàng",
                                "Câu gốc là chuyện ngoài lề (đến muộn, gửi xe…).", THAP, 30, THU_NGHIEM),
    # --- chép âm: lỗi TRƯỚC mô hình
    "ASR_LOW_CONFIDENCE": _l("ASR_UPSTREAM", "Đoạn chép âm chưa chắc", "Máy chép âm không chắc đoạn này.", TRUNG, 18),
    "POSSIBLE_MEDICATION_TRANSCRIPTION_ERROR": _l("ASR_UPSTREAM", "Tên thuốc có thể bị chép sai",
                                                  "Tên thuốc nằm trong đoạn chép âm chưa chắc.", CAO, 18),
    "POSSIBLE_NUMERIC_TRANSCRIPTION_ERROR": _l("ASR_UPSTREAM", "Con số có thể bị chép sai",
                                               "Con số nằm trong đoạn chép âm chưa chắc.", CAO, 18),
    "POSSIBLE_NEGATION_TRANSCRIPTION_ERROR": _l("ASR_UPSTREAM", "Từ phủ định có thể bị chép sai",
                                                "Từ “không/chưa” nằm trong đoạn chép âm chưa chắc.", CAO, 18),
    "SPEAKER_DIARIZATION_UNCERTAIN": _l("ASR_UPSTREAM", "Chưa chắc ai nói lượt này",
                                        "Máy chưa chắc người nói; vai do bác sĩ gán tay.", TRUNG, 18),
}

# Mã trong đặc tả CHƯA có bộ phát hiện — ghi rõ lý do, không giả vờ đã giải quyết.
CHUA_PHAT_HIEN = {
    "PRONOUN_COREFERENCE_ERROR / COREFERENCE_AMBIGUOUS (ngoài phần khoá đã làm)":
        "Cần hiểu ai là “ông ấy”, “cháu” qua nhiều lượt; khoá chỉ xử lý từ chỉ người trong một câu.",
    "RELATION_MISMATCH, MEDICATION_INDICATION_MISMATCH, TEST_RESULT_MISMATCH":
        "Cần hiểu quan hệ giữa hai thực thể; luật từ khoá cho quá nhiều báo động giả.",
    "UNSUPPORTED_CONTEXTUAL_INFERENCE, INTENT/RESPONSE_INFERRED":
        "Suy luận ngữ nghĩa; không có dấu hiệu bề mặt đáng tin.",
    "OVERGENERALIZATION, CATEGORY_EXPANSION":
        "Cần biết “amoxicillin” thuộc nhóm nào; không dùng kiến thức y khoa thay bằng chứng.",
    "CROSS_PROBLEM_RELATION_ERROR, CROSS_VISIT_CONTAMINATION":
        "Bộ dữ liệu mỗi ca là một lần khám; chưa có cấu trúc nhiều lần khám để kiểm.",
    "WRONG_SECTION":
        "Mục do chính `sinh_benh_an` xếp từ trường có cấu trúc; lỗi mục là lỗi trường, đã có mã ở nhóm khác.",
    "COMPRESSION (CONDITION_DROPPED, CERTAINTY_DROPPED)":
        "Chỉ có bản thử nghiệm IMPORTANT_MODIFIER_DROPPED; chưa đo độ chính xác.",
}


# ----------------------------------------------------------------- mức độ
# Loại thông tin — MỘT định nghĩa với `cong_rui_ro.loai_thong_tin`.
LOAI_NANG = ("di_ung", "thuoc", "chan_doan")
# Mã mà sai ở BẤT KỲ loại thông tin nào cũng nguy hiểm — không hạ xuống.
LUON_CAO = {"NEGATION_FLIP", "NEGATION_SCOPE_ERROR", "UNKNOWN_AS_NEGATIVE", "FABRICATED_MEDICATION", "FABRICATED_ALLERGY",
            "DOSE_MISMATCH", "DECIMAL_MISMATCH", "UNIT_MISMATCH", "DISCONTINUED_AS_CURRENT",
            "PLANNED_TEST_AS_RESULT", "LATERALITY_CHANGED", "INTERNAL_CONTRADICTION"}


# ═══ muc_do() — Tính mức nghiêm trọng theo loại thông tin ═════════════════════════════
# Dị ứng, thuốc nâng một bậc; thông tin khác hạ một bậc, trừ các mã luôn cao.
def muc_do(ma: str, loai_thong_tin: str) -> str:
    """Mức nghiêm trọng = mức gốc của mã, điều chỉnh theo LOẠI thông tin.
    Dị ứng / thuốc: nâng lên một bậc. Thông tin 'khác' (triệu chứng phụ...): hạ
    một bậc, trừ những mã LUON_CAO. Không gán 'cao' đồng loạt."""
    goc = LOAI[ma].muc_goc
    h = _HANG[goc]
    if loai_thong_tin in LOAI_NANG:
        h = min(h + 1, 2)
    elif loai_thong_tin == "khac" and ma not in LUON_CAO:
        h = max(h - 1, 0)
    return [THAP, TRUNG, CAO][h]


# ═══ class CanhBao — Một cảnh báo: mã, lượt, câu trích, lý do, kết luận ═══════════════
# Tự xác định có đủ nặng để đổi trạng thái (chính sách D) và xuất ra dạng JSON.
# ----------------------------------------------------------------- lược đồ
@dataclass
class CanhBao:
    ma: str                              # ví dụ WRONG_SUBJECT
    phat_bieu_id: Optional[int]          # None = cảnh báo mức toàn ca
    luot: List[int]                      # lượt hội thoại liên quan
    trich: List[str]                     # câu gốc làm lý do cảnh báo
    ly_do: str                           # vì sao cảnh báo, nói rõ câu nào
    ket_luan: str                        # LOI_PHAT_HIEN | NGHI_RUI_RO | CAN_XEM
    bat_dinh: str                        # THAP | TRUNG | CAO
    bo_phat_hien: str                    # tên hàm / mã khoá gốc
    muc_do: str = TRUNG
    loai_tt: str = "khac"                # loại thông tin (cong_rui_ro.loai_thong_tin)
    phu: List[str] = field(default_factory=list)   # mã phụ đã gộp vào (mục 38-39)
    phien_ban: str = PHIEN_BAN

    @property
    def nhom(self) -> str:
        return LOAI[self.ma].nhom

    @property
    def tin_cay(self) -> str:
        return LOAI[self.ma].tin_cay

    @property
    def anh_huong_trang_thai(self) -> bool:
        """Cảnh báo này có đủ để đưa phát biểu sang CẦN XÁC NHẬN (chính sách D)?
        Bộ phát hiện thử nghiệm và nhóm chất lượng/chép âm: không bao giờ."""
        if self.tin_cay != ON_DINH or self.nhom in ("QUALITY", "ASR_UPSTREAM", "OMISSION"):
            return False
        if self.ket_luan == LOI_PHAT_HIEN:
            return self.muc_do in (CAO, TRUNG)
        if self.ket_luan == NGHI_RUI_RO:
            # Nghi ngờ mà căn cứ của chính cảnh báo còn mờ (bất định cao) thì chỉ hiện.
            # Đo 24/09/2026: SPEAKER_SUBJECT_MISMATCH (bất định cao) chỉ đúng loại 5,8%
            # mà đổi trạng thái 89 lần — đó là chặn thừa.
            # NGOẠI TRỪ dị ứng / thuốc: trên hai loại này, cảnh báo nghi ngờ dù yếu vẫn đi
            # kèm lỗi thật 44% số lần (cùng phép đo) — bỏ đi thì lỗi nguy hiểm lọt tăng từ
            # 44,7% lên 55,3%. An toàn đặt trước ít chặn thừa.
            return self.muc_do == CAO and (self.bat_dinh != CAO or self.loai_tt in LOAI_NANG)
        return False

    def hanh_dong(self) -> str:
        return "xem_lai" if self.anh_huong_trang_thai else "luu_y"

    def to_dict(self):
        d = asdict(self)
        loai = LOAI[self.ma]
        d.update(nhom=self.nhom, nhom_ten=NHOM[self.nhom], tieu_de=loai.tieu_de,
                 giai_thich=loai.giai_thich, uu_tien=loai.uu_tien, tin_cay=self.tin_cay,
                 anh_huong_trang_thai=self.anh_huong_trang_thai, hanh_dong_goi_y=self.hanh_dong(),
                 phu_tieu_de=[LOAI[m].tieu_de for m in self.phu if m in LOAI])
        return d
