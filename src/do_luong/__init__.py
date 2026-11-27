# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm]
Làm gì   : Sinh mọi con số trong báo cáo: cham_* là bộ chấm, do_* là các phép đo.
Bản đồ   : BAN_DO_MA_NGUON.md

Các tệp:
    bit_nhan                 Kiểm mô hình gán chủ thể là hiểu thật hay chỉ đoán theo người
                             vừa nói, bằng cách bịt nhãn người nói rồi so với bản gốc.
    cham_chu_the             In ra từng phát biểu cùng nguyên văn lượt dẫn chứng để người
                             chấm tay trường chủ thể, vì bộ đếm tự động sẽ chấm nhầm người
                             nhà.
    cham_diem                Chấm độ giống giữa bản nháp và bản tham chiếu bằng ROUGE và
                             Section F1, tách từ theo âm tiết tiếng Việt.
    cham_he_thong            Chấm từng mệnh đề đường ống rút ra so với đáp án có cấu trúc:
                             sai người, sai mức, bịa, bỏ sót, và lượt sai đầu tiên.
    cham_lai_bang_quy_gan    Chấm lại các nhánh bằng điểm quy gán trên đúng đầu ra đã sinh,
                             để xem kết luận C không hơn B có do thước đo mù không.
    cham_muc_thach_thuc      Chấm bốn bộ thử thách trực tiếp trên văn bản bản nháp, để nhánh
                             A (văn xuôi, không có bảng mệnh đề) cũng được so công bằng.
    chuan_dinh_dang          Đổi các kiểu viết tiêu đề mục khác nhau về tên mục chuẩn trước
                             khi chấm, để cách trình bày không làm sai điểm Section F1.
    chung_chi_thuoc_do       Kiểm điểm quy gán có đủ nhạy với lỗi đổi chủ thể mà không quá
                             nhạy với đổi từ đồng nghĩa, trên bệnh án thật.
    danh_gia_khoa            Đo tầng khoá bằng chứng chặn oan bao nhiêu trên đáp án hoàn hảo
                             và bắt được bao nhiêu lỗi cấy có chủ định.
    dau_vet_nguon            Đếm các dấu vết nguồn gốc trong bộ hội thoại để biết nó có phải
                             bản dịch từ tiếng Anh không, bằng số chứ không bằng phỏng đoán.
    do_bit_nhan              Chạy phép thử bịt nhãn người nói với mô hình trên GPU để đo tỉ
                             lệ chủ thể chỉ đúng nhờ đoán theo người nói.
    do_bo_chan_doan          Đo mô hình có sa vào từng bẫy của bộ chẩn đoán không (gán dị
                             ứng sai người, nâng bệnh nghi thành chắc...), chấm tự động.
    do_bo_sot                Đo tỉ lệ mệnh đề của đáp án mà bước rút không rút ra được, để
                             trả lời câu giảm bỏ sót thông tin quan trọng bằng số.
    do_canh_bao              Đo lớp cảnh báo báo đúng bao nhiêu và bắt được bao nhiêu lỗi so
                             với bộ chấm tự động, so chính sách C với D trên tập phát triển.
    do_cay_loi               Đo lớp cảnh báo có bắt đúng chỗ, đúng nhóm một lỗi cấy nhân tạo
                             vào đáp án không, và báo nhầm bao nhiêu trên bản sạch.
    do_dac                   So các nhánh trên năm mặt chất lượng (điểm cuối, Section F1, bỏ
                             sót, cần xác nhận, chi phí) và kiểm nhánh mới không giảm lỗi
                             nhờ viết ít.
    do_dan_gian              Đo bộ thử thách dân gian theo cặp A và B: nói chữ khác mà nghĩa
                             không đổi thì hệ thống có chặn, cảnh báo hay tự chọn nghĩa
                             không.
    do_lap_cau               Đo độ lặp câu và độ đa dạng từ vựng của bộ hội thoại bằng một
                             định nghĩa cố định, để so bộ cũ với bộ mới cùng một thước.
    do_neu_ten               Đo bản nháp có nêu tên người (mẹ, bố...) cho các câu thuộc mục
                             không phải của bệnh nhân hay chỉ xếp đúng mục mà quên nêu
                             người.
    do_quan_he               Đo phát hiện quan hệ bằng bốn số đúng, thừa, sót, nhầm loại
                             thay vì một số, so với đáp án cấu trúc.
    do_tang_quan_he          Đếm cặp quan hệ ứng viên mà chương trình liệt kê trên dữ liệu
                             thật và bộ chẩn đoán, để xem cơ chế quan hệ có khai hoa không.
    do_tang_quy_gan          Chấm quy gán riêng từng tầng độ khó (bác sĩ, bệnh nhân, kể hộ,
                             kể về mình), vì số gộp không thấy được tầng người nhà.
    do_trich                 Đo trực tiếp bước rút mệnh đề: tìm thấy bao nhiêu mệnh đề đáp
                             án, gán đúng người bao nhiêu, riêng mệnh đề ngoài bệnh nhân.
    do_van_xuoi              Đo một bệnh án văn xuôi trên bộ chẩn đoán có mắc đúng lỗi bẫy
                             không, không dùng thước đo nào, để so nhánh A với nhánh C.
    do_vidia2std             Đo bảng chuẩn hoá phương ngữ đổi đúng bao nhiêu chỗ khác biệt
                             trên câu thật ViDia2Std, không phải đo hiểu lời bệnh nhân.
    doi_chung_context_vi     Gán chủ thể (bệnh nhân hay người khác) bằng luật kiểu ConText:
                             từ kích hoạt, kích hoạt giả, hết phạm vi, không dùng mô hình.
    doi_chung_tam_thuong     Dựng hai đường tắt không dùng mô hình (chủ thể là người nói,
                             chủ thể luôn là bệnh nhân) để xem hệ thống thật có hơn cả hai.
    duong_danh_doi           Vẽ đường đánh đổi giữa lỗi và bỏ sót khi vặn ngưỡng rủi ro quy
                             gán, chấm trên thân bài mà bác sĩ đọc như sự thật.
    khoang_tin_cay           Tính khoảng tin cậy bootstrap theo ca và theo khuôn bệnh, và so
                             cặp các nhánh, để biết chênh lệch có vượt nhiễu không.
    kiem_nghiem_ngoai_khuon  Kiểm hai điều: tập train và test không trùng khuôn, và hệ thống
                             còn đúng trên 10 kịch bản lâm sàng hoàn toàn ngoài khuôn.
    kiem_thu_dot_bien        Cấy 5 họ lỗi lâm sàng nguy hiểm vào ca hợp lệ rồi đếm các cổng
                             chặn (khoá K1–K7, cổng rủi ro) bắt được bao nhiêu.
    nguon_lap_cau            Truy mỗi câu lặp của bộ hội thoại về chỗ sinh ra nó trong bộ
                             sinh: nhóm câu, mẫu f-string, câu cố định hay ghép.
    quet_an_toan_duoc_ly_v2  Quét bộ dữ liệu v2 tìm tương tác thuốc nguy hiểm, dị ứng người
                             nhà bị gán cho bệnh nhân, đính chính hỏng và trích dẫn sai.
    thuoc_do_quy_gan         Đo mệnh đề có được gán đúng người không: ghép theo nội dung
                             trước, rồi đếm cặp khớp luôn chủ thể, thứ ROUGE không thấy.
"""
