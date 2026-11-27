# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu]
Làm gì   : Sinh hội thoại khám bệnh mô phỏng và bộ thử thách, nạp dữ liệu ngoài, chia train
           / phát triển / kiểm tra theo khuôn bệnh.
Bản đồ   : BAN_DO_MA_NGUON.md

Các tệp:
    bien_the_cau              Cho bộ sinh nhiều cách nói khác nhau cho cùng một ý (câu hỏi
                              bác sĩ, lời chào, câu đáp phủ định) để hội thoại bớt lặp câu.
    ca_mau_bgk                Dựng sẵn ba ca khám nhiều người nói để nút Xem thử với ca mẫu
                              chạy được khi chưa có kết quả chạy thật.
    chia_bon_tap              Chia bộ hội thoại thành bốn tập tách rời (huấn luyện, phát
                              triển, kiểm tra cuối, kiểm tra chung) để không lộ đề.
    chia_tap_theo_khuon       Chia bộ tự sinh thành huấn luyện, phát triển, kiểm tra cuối
                              THEO KHUÔN BỆNH, để một khuôn chỉ nằm ở một tập, không lộ đề.
    dan_gian                  Đổi câu bệnh nhân sang cách nói dân gian, địa phương, ẩn dụ để
                              tạo bộ thử thách, giữ nguyên đáp án lâm sàng.
    du_lieu_huan_luyen_trich  Dựng dữ liệu huấn luyện cho bước rút mệnh đề từ các ca tự
                              sinh: lời thoại vào, mệnh đề đáp án ra.
    gan_nhan_truoc            Cho mô hình của dự án gán trước mệnh đề lên câu ViMQ, rồi lọc
                              bằng luật, ra nhãn máy chưa kiểm.
    kho_khuon                 Giữ một danh sách khuôn bệnh duy nhất để bộ sinh, bước chia
                              tập và bộ lọc giới tính cùng nhìn, không lệch nhau.
    khuon_lo_3                Chứa lô khuôn bệnh 301–350 (cơ xương khớp, thần kinh cơ, chấn
                              thương chỉnh hình) cho bộ sinh.
    khuon_lo_4                Chứa lô 50 khuôn bệnh đánh số 351–400 cho bộ sinh, mỗi khuôn
                              có đủ trường bắt buộc và biến thể.
    khuon_lo_5                Chứa lô khuôn bệnh 401–450 (truyền nhiễm nhiệt đới, ký sinh
                              trùng, lao ngoài phổi, tiêu hoá) cho bộ sinh.
    khuon_lo_6                Chứa lô khuôn bệnh 451–500 (mắt, tai mũi họng, răng hàm mặt)
                              cho bộ sinh.
    khuon_lo_7                Chứa lô 50 khuôn bệnh đánh số 501–550 cho bộ sinh, trải nhiều
                              hệ cơ quan.
    khuon_lo_8                Chứa lô 50 khuôn bệnh đánh số 551–600 cho bộ sinh.
    khuon_mo_rong             Gộp các lô khuôn bệnh mở rộng thành một danh sách chung (657
                              khuôn, 21 hệ cơ quan) cùng bảng giới tính theo khuôn.
    kiem_khuon                Kiểm khuôn bệnh có hợp lệ không (đủ trường, đúng giới, không
                              trùng nhau quá) trước khi cho vào bộ sinh.
    loc_nhan_may              Giữ lại mệnh đề do máy gán trước chỉ khi qua các phép kiểm
                              bằng luật, như có câu trích thật trong lời thoại.
    loi_dan_thuong            Đổi thuật ngữ y khoa trong lời bệnh nhân sang lời dân thường,
                              nhưng đáp án vẫn giữ thuật ngữ lâm sàng.
    nap_bo_gpt500             Chuyển bộ 500 hội thoại phương ngữ do GPT sinh sang định dạng
                              ca của dự án và chấm điểm, chỉ để đo, không để huấn luyện.
    nap_bo_nguoi_that         Đọc bộ hội thoại người thật ghi tay, kiểm lỗi định dạng rồi
                              đổi sang định dạng của bộ sinh để đo.
    nap_du_lieu               Đọc, tách lượt thoại và thống kê bộ hội thoại, đồng thời chặn
                              bằng mã việc chạm tập kiểm tra cuối hay dữ liệu GPT.
    nap_vietmed               Đọc bản chép lời VietMed và ghép các dòng liền nhau thành đoạn
                              hội thoại đủ dài cho bước rút.
    nap_vimq                  Đọc ViMQ (câu hỏi y tế có nhãn thực thể) và bỏ dấu gạch dưới
                              để thành mẫu cho bước rút.
    ngu_lieu_viet             Chứa kho ngữ liệu thô cho bộ sinh: cách xưng hô, người nhà,
                              câu mẫu, triệu chứng và danh sách khuôn bệnh gốc.
    nhieu_asr                 Làm nhiễu lời thoại giống lỗi máy nhận dạng giọng nói (bỏ dấu,
                              sai từ) để thử độ bền, chỉ dùng để đo.
    phuong_ngu                Đổi từ chuẩn sang phương ngữ miền Trung, Nam trong lời thoại
                              và quy ngược về từ chuẩn bằng từ điển.
    sinh_bo_chan_doan         Sinh bộ kiểm tra chẩn đoán lỗi bằng luật, mỗi mẫu cài một bẫy
                              (chủ thể, chắc chắn, đính chính, diễn biến...).
    sinh_bo_thach_thuc        Sinh bốn bộ thử thách theo cặp (đổi người, tự sửa, lỗi chép
                              giọng nói, phương ngữ) bằng luật, từ tập ca sẵn có.
    sinh_ca_da_benh_ly        Sinh ca khám có bệnh chính cộng 1–2 bệnh nền và thuốc nền để
                              tạo hội thoại huấn luyện đa bệnh; không dùng trong luồng khám.
    sinh_hoi_thoai_viet       Sinh hội thoại khám bệnh tiếng Việt mô phỏng từ khuôn bệnh,
                              kèm bệnh án và đáp án có cấu trúc.
    tang_cuong                Tăng thêm mẫu có người nhà bằng cách biến đổi hội thoại sẵn
                              có, không dùng mô hình ngôn ngữ sinh mới.
    van_tay_bo                Ghi vân tay bộ dữ liệu (thế hệ, hạt giống, commit, băm nội
                              dung) để biết bộ nào sinh ra từ mã nào và bắt nhầm bộ.
"""
