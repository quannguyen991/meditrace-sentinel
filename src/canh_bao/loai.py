# -*- coding: utf-8 -*-
"""Tang 6 — LOP CANH BAO: phan loai loi, luoc do mot canh bao, muc nghiem trong.

VI SAO TACH KHOI `khoa_bang_chung` VA `cong_rui_ro`.
Khoa tra loi "phat bieu nay co duoc vao than khong" bang BON cau hoi (nguon, noi
dung, chu the, muc khang dinh). Lop nay tra loi mot cau khac: "neu phat bieu nay
sai thi SAI KIEU GI, va bac si can nhin vao dau". Mot phat bieu co the qua khoa ma
van mang canh bao (lieu "5 mg" trong khi luot dan noi "50 mg" — khoa K6 chi so
nguyen chuoi voi truong `lieu`, khong doc so trong `noi_dung`).

CANH BAO KHONG PHAI TRANG THAI. Trang thai dau ra van la ba:
    đã kiểm chứng          vao than ban nhap
    cần xác nhận           chi vao muc CẦN XÁC NHẬN
    bị phủ định/thay thế   khong vao than, giu dau vet
Canh bao la LY DO mot phat bieu can duoc chu y. Chinh sach D (`gop.trang_thai_D`)
quyet dinh canh bao nao du nang de doi trang thai; chinh sach C (dang dung de do)
KHONG doi.

HAI TRUC TACH RIENG — khong nhan voi nhau thanh mot diem:
    muc_do    NEU thong tin nay sai thi hau qua lon den dau (theo LOAI thong tin:
              di ung, thuoc > chan doan > thoi gian > khac)
    bat_dinh  can cu cua CANH BAO NAY yeu hay mo den dau: "thap" = co bang chung
              ro rang cho thay loi (so trong luot dan khac so trong ban ghi);
              "cao" = chi la dau hieu gian tiep
Di ung co can cu tot van nghiem trong neu sai: muc do cao, bat dinh thap.

BA LOAI KET LUAN — mot canh bao khong chung minh output sai:
    loi_phat_hien      co bang chung doi nghich ro (detected_error)
    nghi_rui_ro        thieu bang chung khang dinh, hoac dau hieu gian tiep
    can_xem            chat luong/ghi chu cho bac si, khong doi trang thai
"""
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

# 24/09/2026 (toi): them AMBIGUOUS_LAY_TERM (cach noi dan gian nhieu nghia).
PHIEN_BAN = "canh-bao-2026-09-24b"

# ----------------------------------------------------------------- nhom lon
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
    # Loi TRUOC khau AI (chep am). Tach rieng: khong tinh la loi cua mo hinh sinh.
    "ASR_UPSTREAM": "Bản chép âm chưa chắc",
}

LOI_PHAT_HIEN = "loi_phat_hien"
NGHI_RUI_RO = "nghi_rui_ro"
CAN_XEM = "can_xem"

CAO, TRUNG, THAP = "cao", "trung", "thap"
_HANG = {THAP: 0, TRUNG: 1, CAO: 2}

# Do tin cay cua CHINH bo phat hien — khong phai cua canh bao.
ON_DINH = "on_dinh"                  # co phep kiem duong/am/am kho; dung cho chinh sach D
THU_NGHIEM = "thu_nghiem"            # experimental: chi hien, khong doi trang thai
CHUA_TIN_CAY = "chua_tin_cay"        # not_reliably_detectable_yet: khong co bo phat hien


@dataclass(frozen=True)
class Loai:
    nhom: str
    tieu_de: str            # cau ngan hien cho bac si
    giai_thich: str         # mot cau, loi thuong
    muc_goc: str            # muc nghiem trong truoc khi xet loai thong tin
    uu_tien: int            # nho = xem truoc (muc 37 cua dac ta)
    tin_cay: str = ON_DINH


def _l(nhom, tieu_de, giai_thich, muc_goc, uu_tien, tin_cay=ON_DINH):
    return Loai(nhom, tieu_de, giai_thich, muc_goc, uu_tien, tin_cay)


# ----------------------------------------------------------------- bang ma
# Chi khai nhung ma CO bo phat hien (hoac anh xa tu khoa). Ma trong dac ta ma
# chua phat hien duoc nam o CHUA_PHAT_HIEN ben duoi, kem ly do — khong gia vo.
LOAI: Dict[str, Loai] = {
    # --- chu the (uu tien 1)
    "WRONG_SUBJECT": _l("SUBJECT_ATTRIBUTION", "Có thể gán sai người",
                        "Câu gốc nói về một người khác, nhưng bản ghi gán cho người này.", CAO, 1),
    "FAMILY_PATIENT_MIXUP": _l("SUBJECT_ATTRIBUTION", "Có thể lẫn người nhà với bệnh nhân",
                               "Câu gốc có nhắc người nhà; thông tin có thể không phải của bệnh nhân.", CAO, 1),
    "SPEAKER_SUBJECT_MISMATCH": _l("SUBJECT_ATTRIBUTION", "Người nói không phải người bệnh",
                                   "Máy gán chủ thể theo người nói; câu gốc không nói rõ là của ai.", TRUNG, 3),
    "SUBJECT_AMBIGUOUS": _l("SUBJECT_ATTRIBUTION", "Chưa rõ thông tin của ai",
                            "Câu gốc không đủ để biết thông tin thuộc về ai.", TRUNG, 3),
    # --- phu dinh, muc chac chan (uu tien 2, 9)
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
    # --- thuoc, di ung, bia (uu tien 3-6)
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
                         "Đường dùng (uống, xịt, bôi…) không có ở lượt được dẫn.", TRUNG, 6),
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
    # --- thoi gian, trang thai dung thuoc (uu tien 7, 10)
    "DISCONTINUED_AS_CURRENT": _l("TEMPORAL", "Thuốc đã ngừng bị ghi là đang dùng",
                                  "Câu gốc nói đã ngừng hoặc bỏ thuốc; bản ghi ghi đang dùng.", CAO, 7),
    "PAST_CURRENT_CONFUSION": _l("TEMPORAL", "Nhầm trước đây với hiện tại",
                                 "Câu gốc nói chuyện trước đây; bản ghi ghi như hiện tại, hoặc ngược lại.", TRUNG, 10),
    "TEMPORAL_MISMATCH": _l("TEMPORAL", "Mốc thời gian không thấy trong câu gốc",
                            "Mốc thời gian trong bản ghi không có ở lượt được dẫn.", TRUNG, 10),
    # --- ke hoach, dieu kien (uu tien 8)
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
    # --- cap nhat trang thai (uu tien 11)
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
    # --- khong can cu (uu tien 12)
    "FABRICATED_QUOTE": _l("UNSUPPORTED", "Câu trích dẫn không có trong hội thoại",
                           "Máy dẫn một câu mà hội thoại không có.", CAO, 12),
    "UNSUPPORTED_INFORMATION": _l("UNSUPPORTED", "Nội dung không khớp câu gốc",
                                  "Nội dung bản ghi không trùng từ nào với đoạn được dẫn.", TRUNG, 12),
    "UNSUPPORTED_BOILERPLATE": _l("UNSUPPORTED", "Câu mẫu không có căn cứ",
                                  "Câu kiểu “không dị ứng”, “khám bình thường” mà hội thoại không nói.", CAO, 12),
    "OVER_NORMALIZATION": _l("UNSUPPORTED", "Diễn đạt thường bị đổi thành thuật ngữ",
                             "Chỉ khớp qua một từ địa phương hoặc khẩu ngữ có nhiều nghĩa.", TRUNG, 15),
    # Them 24/09/2026. Khac OVER_NORMALIZATION: canh bao ca khi ban ghi chep NGUYEN VAN,
    # vi chep nguyen van "om" thi nguoi doc mien Bac van hieu la "bi benh". Cum va cau
    # hoi lay tu `dan_gian.BANG` (muc MO_HO).
    "AMBIGUOUS_LAY_TERM": _l("UNSUPPORTED", "Cách nói có nhiều nghĩa, cần hỏi lại",
                             "Người bệnh dùng một cách nói dân gian có hơn một nghĩa hợp lý; "
                             "chưa hỏi lại thì chưa chọn được nghĩa nào.", TRUNG, 15),
    # --- can cu, nguon
    "WRONG_EVIDENCE": _l("EVIDENCE_PROVENANCE", "Dẫn sai lượt", "Lượt được dẫn không tồn tại hoặc không chứa câu trích.", TRUNG, 16),
    "EVIDENCE_MISSING": _l("EVIDENCE_PROVENANCE", "Không có câu trích nguyên văn",
                           "Bản ghi không kèm câu nguyên văn làm căn cứ.", TRUNG, 16),
    "EVIDENCE_CONTEXT_MISSING": _l("EVIDENCE_PROVENANCE", "Thiếu câu hỏi đi kèm",
                                   "Căn cứ là một câu trả lời ngắn; câu hỏi của bác sĩ không được dẫn.", THAP, 21),
    # --- bo sot (uu tien 13) — o muc TOAN CA, khong gan vao phat bieu nao
    "OMITTED_ALLERGY": _l("OMISSION", "Có thể bỏ sót dị ứng", "Hội thoại nhắc dị ứng nhưng bản ghi không có dòng nào dẫn tới.", CAO, 13),
    "OMITTED_MEDICATION": _l("OMISSION", "Có thể bỏ sót thuốc", "Hội thoại nhắc thuốc nhưng bản ghi không có dòng nào dẫn tới.", CAO, 13),
    "OMITTED_NEGATION": _l("OMISSION", "Có thể bỏ sót một câu phủ định", "Người bệnh nói không có một điều gì đó; bản ghi không ghi.", TRUNG, 13),
    "OMITTED_CORRECTION": _l("OMISSION", "Có thể bỏ sót một lần đính chính", "Người nói sửa lại thông tin; bản ghi không dẫn tới.", TRUNG, 13),
    "OMITTED_UNCERTAINTY": _l("OMISSION", "Có thể bỏ sót điều chưa chắc", "Người nói nói chưa chắc; bản ghi không ghi.", THAP, 13),
    "OMITTED_PLAN": _l("OMISSION", "Có thể bỏ sót kế hoạch", "Bác sĩ dặn hoặc chỉ định; bản ghi không ghi.", TRUNG, 13),
    "OMITTED_NUMERIC_VALUE": _l("OMISSION", "Có thể bỏ sót một con số", "Hội thoại có con số (liều, thời gian, chỉ số) không được ghi.", TRUNG, 13),
    "OMITTED_DURATION": _l("OMISSION", "Có thể bỏ sót thời gian bệnh", "Hội thoại nói thời gian bệnh; bản ghi không dẫn tới.", TRUNG, 13),
    "POSSIBLE_IMPORTANT_OMISSION": _l("OMISSION", "Có đoạn hội thoại chưa được ghi",
                                      "Đoạn có nội dung lâm sàng nhưng không dòng nào dẫn tới.", THAP, 22),
    # --- chat luong: khong doi trang thai
    "DUPLICATE_INFORMATION": _l("QUALITY", "Ghi lặp", "Cùng một thông tin xuất hiện hai lần.", THAP, 30),
    "SEMANTIC_DUPLICATE": _l("QUALITY", "Có thể ghi lặp", "Hai dòng gần như cùng nội dung.", THAP, 30),
    # --- thu nghiem: CHI HIEN, khong doi trang thai
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
    # --- chep am: loi TRUOC mo hinh
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

# Ma trong dac ta CHUA co bo phat hien — ghi ro ly do, khong gia vo da giai quyet.
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


# ----------------------------------------------------------------- muc do
# Loai thong tin — MOT dinh nghia voi `cong_rui_ro.loai_thong_tin`.
LOAI_NANG = ("di_ung", "thuoc")
# Ma ma sai o BAT KY loai thong tin nao cung nguy hiem — khong ha xuong.
LUON_CAO = {"NEGATION_FLIP", "NEGATION_SCOPE_ERROR", "UNKNOWN_AS_NEGATIVE", "FABRICATED_MEDICATION", "FABRICATED_ALLERGY",
            "DOSE_MISMATCH", "DECIMAL_MISMATCH", "UNIT_MISMATCH", "DISCONTINUED_AS_CURRENT",
            "PLANNED_TEST_AS_RESULT", "LATERALITY_CHANGED", "INTERNAL_CONTRADICTION"}


def muc_do(ma: str, loai_thong_tin: str) -> str:
    """Muc nghiem trong = muc goc cua ma, dieu chinh theo LOAI thong tin.
    Di ung / thuoc: nang len mot bac. Thong tin 'khac' (trieu chung phu...): ha
    mot bac, tru nhung ma LUON_CAO. Khong gan 'cao' dong loat."""
    goc = LOAI[ma].muc_goc
    h = _HANG[goc]
    if loai_thong_tin in LOAI_NANG:
        h = min(h + 1, 2)
    elif loai_thong_tin == "khac" and ma not in LUON_CAO:
        h = max(h - 1, 0)
    return [THAP, TRUNG, CAO][h]


# ----------------------------------------------------------------- luoc do
@dataclass
class CanhBao:
    ma: str                              # vd WRONG_SUBJECT
    phat_bieu_id: Optional[int]          # None = canh bao muc toan ca
    luot: List[int]                      # luot hoi thoai lien quan
    trich: List[str]                     # cau goc lam ly do canh bao
    ly_do: str                           # vi sao canh bao, noi ro cau nao
    ket_luan: str                        # LOI_PHAT_HIEN | NGHI_RUI_RO | CAN_XEM
    bat_dinh: str                        # THAP | TRUNG | CAO
    bo_phat_hien: str                    # ten ham / ma khoa goc
    muc_do: str = TRUNG
    loai_tt: str = "khac"                # loai thong tin (cong_rui_ro.loai_thong_tin)
    phu: List[str] = field(default_factory=list)   # ma phu da gop vao (muc 38-39)
    phien_ban: str = PHIEN_BAN

    @property
    def nhom(self) -> str:
        return LOAI[self.ma].nhom

    @property
    def tin_cay(self) -> str:
        return LOAI[self.ma].tin_cay

    @property
    def anh_huong_trang_thai(self) -> bool:
        """Canh bao nay co du de dua phat bieu sang CAN XAC NHAN (chinh sach D)?
        Bo phat hien thu nghiem va nhom chat luong/chep am: khong bao gio."""
        if self.tin_cay != ON_DINH or self.nhom in ("QUALITY", "ASR_UPSTREAM", "OMISSION"):
            return False
        if self.ket_luan == LOI_PHAT_HIEN:
            return self.muc_do in (CAO, TRUNG)
        if self.ket_luan == NGHI_RUI_RO:
            # Nghi ngo ma can cu cua chinh canh bao con mo (bat dinh cao) thi chi hien.
            # Do 24/09/2026: SPEAKER_SUBJECT_MISMATCH (bat dinh cao) chi dung loai 5,8%
            # ma doi trang thai 89 lan — do la chan thua.
            # NGOAI TRU di ung / thuoc: tren hai loai nay, canh bao nghi ngo du yeu van di
            # kem loi that 44% so lan (cung phep do) — bo di thi loi nguy hiem lot tang tu
            # 44,7% len 55,3%. An toan dat truoc it chan thua.
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
