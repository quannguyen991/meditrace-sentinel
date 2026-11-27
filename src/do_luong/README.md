# Đo lường và chấm điểm — `src/do_luong/`

Sinh mọi con số trong báo cáo: cham_* là bộ chấm, do_* là các phép đo.

| Tệp | Thuộc | Làm gì | Tên cũ |
|---|---|---|---|
| [bit_nhan.py](bit_nhan.py) | Phép đo | Kiểm mô hình gán chủ thể là hiểu thật hay chỉ đoán theo người vừa nói, bằng cách bịt nhãn người nói rồi so với bản gốc. | `src/bit_nhan.py` |
| [cham_chu_the.py](cham_chu_the.py) | Bộ chấm | In ra từng phát biểu cùng nguyên văn lượt dẫn chứng để người chấm tay trường chủ thể, vì bộ đếm tự động sẽ chấm nhầm người nhà. | `src/cham_chu_the.py` |
| [cham_diem.py](cham_diem.py) | Bộ chấm | Chấm độ giống giữa bản nháp và bản tham chiếu bằng ROUGE và Section F1, tách từ theo âm tiết tiếng Việt. | `src/cham_diem.py` |
| [cham_he_thong.py](cham_he_thong.py) | Bộ chấm | Chấm từng mệnh đề đường ống rút ra so với đáp án có cấu trúc: sai người, sai mức, bịa, bỏ sót, và lượt sai đầu tiên. | `src/cham_he_thong.py` |
| [cham_lai_bang_quy_gan.py](cham_lai_bang_quy_gan.py) | Bộ chấm | Chấm lại các nhánh bằng điểm quy gán trên đúng đầu ra đã sinh, để xem kết luận C không hơn B có do thước đo mù không. | `src/cham_lai_bang_quy_gan.py` |
| [cham_muc_thach_thuc.py](cham_muc_thach_thuc.py) | Bộ chấm | Chấm bốn bộ thử thách trực tiếp trên văn bản bản nháp, để nhánh A (văn xuôi, không có bảng mệnh đề) cũng được so công bằng. | `src/cham_muc_thach_thuc.py` |
| [chuan_dinh_dang.py](chuan_dinh_dang.py) | Bộ chấm | Đổi các kiểu viết tiêu đề mục khác nhau về tên mục chuẩn trước khi chấm, để cách trình bày không làm sai điểm Section F1. | `src/chuan_dinh_dang.py` |
| [chung_chi_thuoc_do.py](chung_chi_thuoc_do.py) | Thước đo | Kiểm điểm quy gán có đủ nhạy với lỗi đổi chủ thể mà không quá nhạy với đổi từ đồng nghĩa, trên bệnh án thật. | `src/chung_chi_thuoc_do.py` |
| [danh_gia_khoa.py](danh_gia_khoa.py) | Thước đo | Đo tầng khoá bằng chứng chặn oan bao nhiêu trên đáp án hoàn hảo và bắt được bao nhiêu lỗi cấy có chủ định. | `src/danh_gia_khoa.py` |
| [dau_vet_nguon.py](dau_vet_nguon.py) | Chất lượng dữ liệu | Đếm các dấu vết nguồn gốc trong bộ hội thoại để biết nó có phải bản dịch từ tiếng Anh không, bằng số chứ không bằng phỏng đoán. | `src/dau_vet_nguon.py` |
| [do_bit_nhan.py](do_bit_nhan.py) | Phép đo | Chạy phép thử bịt nhãn người nói với mô hình trên GPU để đo tỉ lệ chủ thể chỉ đúng nhờ đoán theo người nói. | `src/do_bit_nhan.py` |
| [do_bo_chan_doan.py](do_bo_chan_doan.py) | Phép đo | Đo mô hình có sa vào từng bẫy của bộ chẩn đoán không (gán dị ứng sai người, nâng bệnh nghi thành chắc...), chấm tự động. | `src/do_bo_chan_doan.py` |
| [do_bo_sot.py](do_bo_sot.py) | Phép đo | Đo tỉ lệ mệnh đề của đáp án mà bước rút không rút ra được, để trả lời câu giảm bỏ sót thông tin quan trọng bằng số. | `src/do_bo_sot.py` |
| [do_canh_bao.py](do_canh_bao.py) | Phép đo | Đo lớp cảnh báo báo đúng bao nhiêu và bắt được bao nhiêu lỗi so với bộ chấm tự động, so chính sách C với D trên tập phát triển. | `src/do_canh_bao.py` |
| [do_cay_loi.py](do_cay_loi.py) | Phép đo | Đo lớp cảnh báo có bắt đúng chỗ, đúng nhóm một lỗi cấy nhân tạo vào đáp án không, và báo nhầm bao nhiêu trên bản sạch. | `src/do_cay_loi.py` |
| [do_dac.py](do_dac.py) | Phép đo | So các nhánh trên năm mặt chất lượng (điểm cuối, Section F1, bỏ sót, cần xác nhận, chi phí) và kiểm nhánh mới không giảm lỗi nhờ viết ít. | `src/do_dac.py` |
| [do_dan_gian.py](do_dan_gian.py) | Phép đo | Đo bộ thử thách dân gian theo cặp A và B: nói chữ khác mà nghĩa không đổi thì hệ thống có chặn, cảnh báo hay tự chọn nghĩa không. | `src/do_dan_gian.py` |
| [do_lap_cau.py](do_lap_cau.py) | Chất lượng dữ liệu | Đo độ lặp câu và độ đa dạng từ vựng của bộ hội thoại bằng một định nghĩa cố định, để so bộ cũ với bộ mới cùng một thước. | `src/do_lap_cau.py` |
| [do_neu_ten.py](do_neu_ten.py) | Phép đo | Đo bản nháp có nêu tên người (mẹ, bố...) cho các câu thuộc mục không phải của bệnh nhân hay chỉ xếp đúng mục mà quên nêu người. | `src/do_neu_ten.py` |
| [do_quan_he.py](do_quan_he.py) | Phép đo | Đo phát hiện quan hệ bằng bốn số đúng, thừa, sót, nhầm loại thay vì một số, so với đáp án cấu trúc. | `src/do_quan_he.py` |
| [do_tang_quan_he.py](do_tang_quan_he.py) | Phép đo | Đếm cặp quan hệ ứng viên mà chương trình liệt kê trên dữ liệu thật và bộ chẩn đoán, để xem cơ chế quan hệ có khai hoa không. | `src/do_tang_quan_he.py` |
| [do_tang_quy_gan.py](do_tang_quy_gan.py) | Phép đo | Chấm quy gán riêng từng tầng độ khó (bác sĩ, bệnh nhân, kể hộ, kể về mình), vì số gộp không thấy được tầng người nhà. | `src/do_tang_quy_gan.py` |
| [do_trich.py](do_trich.py) | Phép đo | Đo trực tiếp bước rút mệnh đề: tìm thấy bao nhiêu mệnh đề đáp án, gán đúng người bao nhiêu, riêng mệnh đề ngoài bệnh nhân. | `src/do_trich.py` |
| [do_van_xuoi.py](do_van_xuoi.py) | Phép đo | Đo một bệnh án văn xuôi trên bộ chẩn đoán có mắc đúng lỗi bẫy không, không dùng thước đo nào, để so nhánh A với nhánh C. | `src/do_van_xuoi.py` |
| [do_vidia2std.py](do_vidia2std.py) | Phép đo | Đo bảng chuẩn hoá phương ngữ đổi đúng bao nhiêu chỗ khác biệt trên câu thật ViDia2Std, không phải đo hiểu lời bệnh nhân. | `src/do_vidia2std.py` |
| [doi_chung_context_vi.py](doi_chung_context_vi.py) | Đối chứng | Gán chủ thể (bệnh nhân hay người khác) bằng luật kiểu ConText: từ kích hoạt, kích hoạt giả, hết phạm vi, không dùng mô hình. | `src/context_vi.py` |
| [doi_chung_tam_thuong.py](doi_chung_tam_thuong.py) | Đối chứng | Dựng hai đường tắt không dùng mô hình (chủ thể là người nói, chủ thể luôn là bệnh nhân) để xem hệ thống thật có hơn cả hai. | `src/doi_chung_tam_thuong.py` |
| [duong_danh_doi.py](duong_danh_doi.py) | Thống kê | Vẽ đường đánh đổi giữa lỗi và bỏ sót khi vặn ngưỡng rủi ro quy gán, chấm trên thân bài mà bác sĩ đọc như sự thật. | `src/duong_danh_doi.py` |
| [khoang_tin_cay.py](khoang_tin_cay.py) | Thống kê | Tính khoảng tin cậy bootstrap theo ca và theo khuôn bệnh, và so cặp các nhánh, để biết chênh lệch có vượt nhiễu không. | `src/sai_so.py` |
| [kiem_nghiem_ngoai_khuon.py](kiem_nghiem_ngoai_khuon.py) | Chất lượng dữ liệu | Kiểm hai điều: tập train và test không trùng khuôn, và hệ thống còn đúng trên 10 kịch bản lâm sàng hoàn toàn ngoài khuôn. | `src/kiem_nghiem_ngoai_khuon.py` |
| [kiem_thu_dot_bien.py](kiem_thu_dot_bien.py) | Kiểm thử | Cấy 5 họ lỗi lâm sàng nguy hiểm vào ca hợp lệ rồi đếm các cổng chặn (khoá K1–K7, cổng rủi ro) bắt được bao nhiêu. | `src/kiem_thu_dot_bien.py` |
| [nguon_lap_cau.py](nguon_lap_cau.py) | Chất lượng dữ liệu | Truy mỗi câu lặp của bộ hội thoại về chỗ sinh ra nó trong bộ sinh: nhóm câu, mẫu f-string, câu cố định hay ghép. | `src/nguon_lap_cau.py` |
| [quet_an_toan_duoc_ly_v2.py](quet_an_toan_duoc_ly_v2.py) | Chất lượng dữ liệu | Quét bộ dữ liệu v2 tìm tương tác thuốc nguy hiểm, dị ứng người nhà bị gán cho bệnh nhân, đính chính hỏng và trích dẫn sai. | `src/quet_an_toan_duoc_ly_v2.py` |
| [thuoc_do_quy_gan.py](thuoc_do_quy_gan.py) | Thước đo | Đo mệnh đề có được gán đúng người không: ghép theo nội dung trước, rồi đếm cặp khớp luôn chủ thể, thứ ROUGE không thấy. | `src/thuoc_do_quy_gan.py` |

Bản đồ toàn dự án: [../../BAN_DO_MA_NGUON.md](../../BAN_DO_MA_NGUON.md)
