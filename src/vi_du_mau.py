# -*- coding: utf-8 -*-
"""Vi du mau cho loi nhac trich phat bieu.

Tach ra tep rieng vi no dai va se con sua nhieu.

Lich su:
  Vong 1 zero-shot          -> 0/13 gan dung chu the (nham chu_the voi nguoi_noi)
  Vong 2 them vi du 1-2     -> loi chu the 100% -> 89%; 8B sau do dat 98%
  Vong 4 them vi du 3-4     -> vi luoc do CHUA CO truong thoi gian va quan he,
                               mo hinh khong co cho nao ghi "2 ngay" hay "hom qua"
                               nen bo luon. Ket qua 0/15 o ca dinh_chinh va
                               dien_bien LA LOI CUA LUOC DO, khong phai cua mo hinh.
  Vong 5 them vi du 5       -> phep kiem CHEO tim ra 17/289 ban ghi (6%) ghi
                               "chau ba tuoi" ma chu_the la "nguoi nha". Bang
                               tinh huong khong cham toi vi no khong phai bay
                               cua tinh huong nao. Vi du 5 day dung ca do.
  Vong 6 (11/09/2026)       -> them `trich_dan` va `hanh_vi` vao moi ban ghi, va
                               KEO VI DU VE DUNG QUY UOC CUA BO SINH, vi truoc do
                               hai ben day hai dieu khac nhau:
                                 - `luot_thoai` chi gom luot CHUA thong tin; cau
                                   tra loi tat moi kem luot cau hoi (vi du 3)
                                 - cau dieu kien GHI LAI voi tinh_huong "gia
                                   dinh" (vi du 2). Ban cu khong ghi gi ca va ghi
                                   mot ke hoach "uong thuoc ha sot" — quy uoc ma
                                   bo sinh bo tu 09/09/2026 (Task 24).
                                 - `thoi_gian_su_kien` theo MUC, nhu bo sinh dat.
"""

VI_DU = """Ví dụ 1 — người nhà kể hộ bệnh nhân.

Hội thoại:
1. Bác sĩ: Cháu có tiền sử dị ứng thuốc gì không ạ?
2. Người nhà: Tôi thì dị ứng penicillin, còn cháu chưa thấy bị bao giờ.

JSON:
{"phat_bieu": [
 {"chu_the": "mẹ", "noi_dung": "dị ứng penicillin", "do_chac_chan": "chắc chắn", "phu_dinh": false, "tinh_huong": "thực tế", "thoi_gian_su_kien": "chưa rõ", "moc_thoi_gian": null, "quan_he": "không", "quan_he_voi": null, "luot_thoai": [2], "trich_dan": ["Tôi thì dị ứng penicillin"], "hanh_vi": "trả lời"},
 {"chu_the": "trẻ", "noi_dung": "dị ứng thuốc", "do_chac_chan": "chưa ghi nhận", "phu_dinh": false, "tinh_huong": "thực tế", "thoi_gian_su_kien": "chưa rõ", "moc_thoi_gian": null, "quan_he": "không", "quan_he_voi": null, "luot_thoai": [2], "trich_dan": ["còn cháu chưa thấy bị bao giờ"], "hanh_vi": "trả lời"}
]}

Chú ý: người nói là NGƯỜI NHÀ ở cả hai bản ghi, nhưng chủ thể khác nhau. Mỗi bản ghi trích đúng đoạn nói về nó, và "chưa thấy bị bao giờ" là "chưa ghi nhận", không phải phủ định.

Ví dụ 2 — câu giả định.

Hội thoại:
1. Bác sĩ: Cháu sốt mấy hôm rồi chị?
2. Người nhà: Bé ho nhiều lắm ạ. Nếu mai bé còn sốt thì tôi cho uống hạ sốt.

JSON:
{"phat_bieu": [
 {"chu_the": "trẻ", "noi_dung": "ho nhiều", "do_chac_chan": "chắc chắn", "phu_dinh": false, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại", "moc_thoi_gian": null, "quan_he": "không", "quan_he_voi": null, "luot_thoai": [2], "trich_dan": ["Bé ho nhiều lắm ạ"], "hanh_vi": "trả lời"},
 {"chu_the": "trẻ", "noi_dung": "sốt", "do_chac_chan": "chắc chắn", "phu_dinh": false, "tinh_huong": "giả định", "thoi_gian_su_kien": "hiện tại", "moc_thoi_gian": null, "quan_he": "không", "quan_he_voi": null, "luot_thoai": [2], "trich_dan": ["Nếu mai bé còn sốt thì tôi cho uống hạ sốt"], "hanh_vi": "trả lời"}
]}

Chú ý: câu "nếu mai bé còn sốt" là điều kiện — ghi với tinh_huong "giả định", KHÔNG phải triệu chứng đang có.

Ví dụ 3 — ĐÍNH CHÍNH. Người nói tự sửa lại chính thông tin vừa nêu. Ghi CẢ HAI bản.

Hội thoại:
1. Bác sĩ: Cháu đau bụng mấy hôm rồi chị?
2. Người nhà: 5 ngày ạ… À không, hôm kia mới bắt đầu, vậy là 3 ngày.

JSON:
{"phat_bieu": [
 {"chu_the": "trẻ", "noi_dung": "đau bụng", "do_chac_chan": "chắc chắn", "phu_dinh": false, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại", "moc_thoi_gian": "5 ngày", "quan_he": "không", "quan_he_voi": null, "luot_thoai": [1, 2], "trich_dan": ["Cháu đau bụng mấy hôm rồi chị", "5 ngày ạ"], "hanh_vi": "trả lời"},
 {"chu_the": "trẻ", "noi_dung": "đau bụng", "do_chac_chan": "chắc chắn", "phu_dinh": false, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại", "moc_thoi_gian": "3 ngày", "quan_he": "đính chính", "quan_he_voi": 0, "luot_thoai": [1, 2], "trich_dan": ["Cháu đau bụng mấy hôm rồi chị", "vậy là 3 ngày"], "hanh_vi": "trả lời"}
]}

Chú ý: lượt 2 chỉ nói số ngày — "đau bụng" nằm ở câu hỏi, nên bằng chứng gồm cả lượt 1. Mốc "5 ngày" vẫn được ghi lại, nhưng bản ghi sau đính chính nó. Số liệu đúng để dùng là "3 ngày".

Ví dụ 4 — DIỄN BIẾN. Hai mốc thời gian khác nhau, CẢ HAI đều đúng. Đây KHÔNG phải đính chính.

Hội thoại:
1. Bác sĩ: Cháu còn nôn không chị?
2. Người nhà: Hôm qua cháu nôn, hôm nay thì hết rồi ạ.

JSON:
{"phat_bieu": [
 {"chu_the": "trẻ", "noi_dung": "nôn", "do_chac_chan": "chắc chắn", "phu_dinh": false, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại", "moc_thoi_gian": "hôm qua", "quan_he": "không", "quan_he_voi": null, "luot_thoai": [2], "trich_dan": ["Hôm qua cháu nôn"], "hanh_vi": "trả lời"},
 {"chu_the": "trẻ", "noi_dung": "nôn", "do_chac_chan": "chắc chắn", "phu_dinh": true, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại", "moc_thoi_gian": "hôm nay", "quan_he": "diễn biến", "quan_he_voi": 0, "luot_thoai": [2], "trich_dan": ["hôm nay thì hết rồi ạ"], "hanh_vi": "trả lời"}
]}

Chú ý: khác ví dụ 3 ở chỗ CẢ HAI bản ghi đều còn hiệu lực. Hôm qua có nôn là đúng, hôm nay hết nôn cũng đúng. Không được vứt mốc đầu.

Ví dụ 5 — TUỔI của bệnh nhân, do người nhà nói ra.

Hội thoại:
1. Bác sĩ: Cháu mấy tuổi rồi chị?
2. Người nhà: Cháu ba tuổi ạ. Mấy hôm nay quấy khóc nhiều.

JSON:
{"phat_bieu": [
 {"chu_the": "trẻ", "noi_dung": "ba tuổi", "do_chac_chan": "chắc chắn", "phu_dinh": false, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại", "moc_thoi_gian": null, "quan_he": "không", "quan_he_voi": null, "luot_thoai": [2], "trich_dan": ["Cháu ba tuổi ạ"], "hanh_vi": "trả lời"},
 {"chu_the": "trẻ", "noi_dung": "quấy khóc", "do_chac_chan": "chắc chắn", "phu_dinh": false, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại", "moc_thoi_gian": "mấy hôm nay", "quan_he": "không", "quan_he_voi": null, "luot_thoai": [2], "trich_dan": ["Mấy hôm nay quấy khóc nhiều"], "hanh_vi": "trả lời"}
]}

Chú ý: người nói là NGƯỜI NHÀ nhưng cả hai bản ghi đều nói VỀ TRẺ. Tuổi là đặc điểm của bệnh nhân, không phải của người kể."""
