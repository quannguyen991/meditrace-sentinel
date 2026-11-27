# Sinh, nạp và chia dữ liệu — `src/bo_du_lieu/`

Sinh hội thoại khám bệnh mô phỏng và bộ thử thách, nạp dữ liệu ngoài, chia train / phát triển / kiểm tra theo khuôn bệnh.

| Tệp | Thuộc | Làm gì | Tên cũ |
|---|---|---|---|
| [bien_the_cau.py](bien_the_cau.py) | Bộ sinh | Cho bộ sinh nhiều cách nói khác nhau cho cùng một ý (câu hỏi bác sĩ, lời chào, câu đáp phủ định) để hội thoại bớt lặp câu. | `src/bien_the_cau.py` |
| [ca_mau_bgk.py](ca_mau_bgk.py) | Ca mẫu | Dựng sẵn ba ca khám nhiều người nói để nút Xem thử với ca mẫu chạy được khi chưa có kết quả chạy thật. | `src/ca_mau_bgk.py` |
| [chia_bon_tap.py](chia_bon_tap.py) | Nạp và chia | Chia bộ hội thoại thành bốn tập tách rời (huấn luyện, phát triển, kiểm tra cuối, kiểm tra chung) để không lộ đề. | `src/tach_tap.py` |
| [chia_tap_theo_khuon.py](chia_tap_theo_khuon.py) | Nạp và chia | Chia bộ tự sinh thành huấn luyện, phát triển, kiểm tra cuối THEO KHUÔN BỆNH, để một khuôn chỉ nằm ở một tập, không lộ đề. | `src/tach_tap_viet.py` |
| [dan_gian.py](dan_gian.py) | Bộ thử thách | Đổi câu bệnh nhân sang cách nói dân gian, địa phương, ẩn dụ để tạo bộ thử thách, giữ nguyên đáp án lâm sàng. | `src/dan_gian.py` |
| [du_lieu_huan_luyen_trich.py](du_lieu_huan_luyen_trich.py) | Nạp và chia | Dựng dữ liệu huấn luyện cho bước rút mệnh đề từ các ca tự sinh: lời thoại vào, mệnh đề đáp án ra. | `src/du_lieu_trich.py` |
| [gan_nhan_truoc.py](gan_nhan_truoc.py) | Dữ liệu ngoài | Cho mô hình của dự án gán trước mệnh đề lên câu ViMQ, rồi lọc bằng luật, ra nhãn máy chưa kiểm. | `src/gan_nhan_truoc.py` |
| [kho_khuon.py](kho_khuon.py) | Khuôn bệnh | Giữ một danh sách khuôn bệnh duy nhất để bộ sinh, bước chia tập và bộ lọc giới tính cùng nhìn, không lệch nhau. | `src/kho_khuon.py` |
| [khuon_lo_3.py](khuon_lo_3.py) | Khuôn bệnh | Chứa lô khuôn bệnh 301–350 (cơ xương khớp, thần kinh cơ, chấn thương chỉnh hình) cho bộ sinh. | `src/khuon_lo_3.py` |
| [khuon_lo_4.py](khuon_lo_4.py) | Khuôn bệnh | Chứa lô 50 khuôn bệnh đánh số 351–400 cho bộ sinh, mỗi khuôn có đủ trường bắt buộc và biến thể. | `src/khuon_lo_4.py` |
| [khuon_lo_5.py](khuon_lo_5.py) | Khuôn bệnh | Chứa lô khuôn bệnh 401–450 (truyền nhiễm nhiệt đới, ký sinh trùng, lao ngoài phổi, tiêu hoá) cho bộ sinh. | `src/khuon_lo_5.py` |
| [khuon_lo_6.py](khuon_lo_6.py) | Khuôn bệnh | Chứa lô khuôn bệnh 451–500 (mắt, tai mũi họng, răng hàm mặt) cho bộ sinh. | `src/khuon_lo_6.py` |
| [khuon_lo_7.py](khuon_lo_7.py) | Khuôn bệnh | Chứa lô 50 khuôn bệnh đánh số 501–550 cho bộ sinh, trải nhiều hệ cơ quan. | `src/khuon_lo_7.py` |
| [khuon_lo_8.py](khuon_lo_8.py) | Khuôn bệnh | Chứa lô 50 khuôn bệnh đánh số 551–600 cho bộ sinh. | `src/khuon_lo_8.py` |
| [khuon_mo_rong.py](khuon_mo_rong.py) | Khuôn bệnh | Gộp các lô khuôn bệnh mở rộng thành một danh sách chung (657 khuôn, 21 hệ cơ quan) cùng bảng giới tính theo khuôn. | `src/khuon_mo_rong.py` |
| [kiem_khuon.py](kiem_khuon.py) | Khuôn bệnh | Kiểm khuôn bệnh có hợp lệ không (đủ trường, đúng giới, không trùng nhau quá) trước khi cho vào bộ sinh. | `src/kiem_khuon.py` |
| [loc_nhan_may.py](loc_nhan_may.py) | Dữ liệu ngoài | Giữ lại mệnh đề do máy gán trước chỉ khi qua các phép kiểm bằng luật, như có câu trích thật trong lời thoại. | `src/loc_nhan_may.py` |
| [loi_dan_thuong.py](loi_dan_thuong.py) | Bộ sinh | Đổi thuật ngữ y khoa trong lời bệnh nhân sang lời dân thường, nhưng đáp án vẫn giữ thuật ngữ lâm sàng. | `src/loi_dan_thuong.py` |
| [nap_bo_gpt500.py](nap_bo_gpt500.py) | Dữ liệu ngoài | Chuyển bộ 500 hội thoại phương ngữ do GPT sinh sang định dạng ca của dự án và chấm điểm, chỉ để đo, không để huấn luyện. | `src/bo_gpt500.py` |
| [nap_bo_nguoi_that.py](nap_bo_nguoi_that.py) | Dữ liệu ngoài | Đọc bộ hội thoại người thật ghi tay, kiểm lỗi định dạng rồi đổi sang định dạng của bộ sinh để đo. | `src/bo_nguoi_that.py` |
| [nap_du_lieu.py](nap_du_lieu.py) | Nạp và chia | Đọc, tách lượt thoại và thống kê bộ hội thoại, đồng thời chặn bằng mã việc chạm tập kiểm tra cuối hay dữ liệu GPT. | `src/du_lieu.py` |
| [nap_vietmed.py](nap_vietmed.py) | Dữ liệu ngoài | Đọc bản chép lời VietMed và ghép các dòng liền nhau thành đoạn hội thoại đủ dài cho bước rút. | `src/nap_vietmed.py` |
| [nap_vimq.py](nap_vimq.py) | Dữ liệu ngoài | Đọc ViMQ (câu hỏi y tế có nhãn thực thể) và bỏ dấu gạch dưới để thành mẫu cho bước rút. | `src/nap_vimq.py` |
| [ngu_lieu_viet.py](ngu_lieu_viet.py) | Bộ sinh | Chứa kho ngữ liệu thô cho bộ sinh: cách xưng hô, người nhà, câu mẫu, triệu chứng và danh sách khuôn bệnh gốc. | `src/ngu_lieu_viet.py` |
| [nhieu_asr.py](nhieu_asr.py) | Bộ thử thách | Làm nhiễu lời thoại giống lỗi máy nhận dạng giọng nói (bỏ dấu, sai từ) để thử độ bền, chỉ dùng để đo. | `src/nhieu_asr.py` |
| [phuong_ngu.py](phuong_ngu.py) | Bộ sinh | Đổi từ chuẩn sang phương ngữ miền Trung, Nam trong lời thoại và quy ngược về từ chuẩn bằng từ điển. | `src/phuong_ngu.py` |
| [sinh_bo_chan_doan.py](sinh_bo_chan_doan.py) | Bộ thử thách | Sinh bộ kiểm tra chẩn đoán lỗi bằng luật, mỗi mẫu cài một bẫy (chủ thể, chắc chắn, đính chính, diễn biến...). | `src/sinh_bo_chan_doan.py` |
| [sinh_bo_thach_thuc.py](sinh_bo_thach_thuc.py) | Bộ thử thách | Sinh bốn bộ thử thách theo cặp (đổi người, tự sửa, lỗi chép giọng nói, phương ngữ) bằng luật, từ tập ca sẵn có. | `src/thach_thuc.py` |
| [sinh_ca_da_benh_ly.py](sinh_ca_da_benh_ly.py) | Bộ sinh | Sinh ca khám có bệnh chính cộng 1–2 bệnh nền và thuốc nền để tạo hội thoại huấn luyện đa bệnh; không dùng trong luồng khám. | `src/da_benh_ly.py` |
| [sinh_hoi_thoai_viet.py](sinh_hoi_thoai_viet.py) | Bộ sinh | Sinh hội thoại khám bệnh tiếng Việt mô phỏng từ khuôn bệnh, kèm bệnh án và đáp án có cấu trúc. | `src/sinh_hoi_thoai_viet.py` |
| [tang_cuong.py](tang_cuong.py) | Bộ sinh | Tăng thêm mẫu có người nhà bằng cách biến đổi hội thoại sẵn có, không dùng mô hình ngôn ngữ sinh mới. | `src/tang_cuong.py` |
| [van_tay_bo.py](van_tay_bo.py) | Nạp và chia | Ghi vân tay bộ dữ liệu (thế hệ, hạt giống, commit, băm nội dung) để biết bộ nào sinh ra từ mã nào và bắt nhầm bộ. | `src/van_tay_bo.py` |

Bản đồ toàn dự án: [../../BAN_DO_MA_NGUON.md](../../BAN_DO_MA_NGUON.md)
