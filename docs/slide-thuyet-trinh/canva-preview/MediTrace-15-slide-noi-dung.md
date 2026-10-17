# MediTrace Sentinel

Nội dung 15 slide để hoàn thiện trên Canva.

Nguồn chính: Báo cáo FINAL và PDF 15 slide FINAL. Mã nguồn dùng đối chiếu mô hình, quy trình và phạm vi chức năng.

## 01. MediTrace Sentinel

✱ Bản nháp lâm sàng
có thể truy lại lời nói gốc
 Kiểm tra căn cứ và trạng thái của từng thông tin
trong hội thoại khám bệnh tiếng Việt

 Nhóm MediTrace · THPT Cầu Giấy
Giáo viên hướng dẫn: Nguyễn Ngọc Lý

Ghi chú và nguồn: Giới thiệu mục tiêu: tạo bản nháp mà bác sĩ có thể kiểm tra từng dòng. Tên trường và giáo viên hướng dẫn lấy từ PDF 15 slide FINAL. Năm trình bày 2026 theo báo cáo FINAL.

## 02. Bối cảnh ghi chép lâm sàng

🩺
 Bác sĩ vừa trao đổi,
vừa tổng hợp hồ sơ
 Hội thoại có nhiều người nói, lời đính chính và những thông tin chưa chắc chắn.
 Câu văn trôi chảy vẫn có thể ghi sai người hoặc sai trạng thái.

 ✱ Thông tin này
nói về ai?
 Còn đúng
ở thời điểm nào?
 Câu nói nào
làm căn cứ?

Ghi chú và nguồn: Báo cáo FINAL mục 1.1 và README. Dự án chưa đo mức tiết kiệm thời gian cho bác sĩ, vì vậy không hứa hiệu quả tiết kiệm thời gian. Chỉ nêu vấn đề cần đối chiếu bản nháp với nguồn.

## 03. Bốn lỗi làm đổi nghĩa

👥 Nhầm chủ thể
 “Bố em bị hen từ nhỏ.”
 Ghi sai: bệnh nhân bị hen.
 Thông tin thuộc về người bố.

 ↩️ Giữ lời đã sửa
 “Một tuần… à không, mười ngày.”
 Ghi sai: ho một tuần.
 Mốc hiện dùng là mười ngày.

 ⏳ Sai trạng thái
 “Nếu mai còn sốt thì chụp phim.”
 Ghi sai: đã chụp phim.
 Đây là kế hoạch có điều kiện.

 💊 Thêm chi tiết
 Hội thoại không nhắc liều dùng.
 Ghi sai: tự thêm “500 mg”.
 Chi tiết cần có câu gốc hỗ trợ.

Ghi chú và nguồn: Các tình huống minh họa theo báo cáo FINAL mục 1.1, 3.4 và README. Đây là ví dụ lỗi, không phải lời khuyên dùng thuốc. Phải phân biệt người nói với chủ thể được nhắc tới.

## 04. Câu hỏi và phạm vi nghiên cứu

Tách từng thông tin, theo dõi lời sửa và kiểm căn cứ có giảm lỗi mà vẫn giữ đủ nội dung?

 H1 Ghi đúng người hơn cách viết trực tiếp.

 H1b Giảm giữ thông tin đã bị người nói sửa.

 H2 Giảm lỗi nghiêm trọng, có thể tăng bỏ sót.

 H3 Độ giống câu chữ chưa đủ để đo đúng nghĩa.

 🔬 Dữ liệu mô phỏng. Đầu ra là bản nháp chờ bác sĩ duyệt. Hệ thống không chẩn đoán hay kê đơn.

Ghi chú và nguồn: Các giả thuyết theo bảng trong báo cáo FINAL. Câu hỏi đặt ra sự đánh đổi độ đúng và độ đủ. H1 chưa được ủng hộ, H1b được ủng hộ trên dữ liệu tổng hợp, H2 được ủng hộ một phần, H3 được ủng hộ cùng giới hạn bộ chấm.

## 05. Quy trình xử lý từng thông tin

01 🎙️ Chuẩn bị lời thoại Đánh số lượt nói.
Âm thanh là đầu vào tùy chọn.

 02 🧠 Tách mệnh đề Qwen3-4B đề xuất từng thông tin có cấu trúc.

 03 👥 Nhận người Lưu riêng người nói và người được nhắc tới.

 04 ↩️ Cập nhật trạng thái Phân biệt đính chính, diễn biến, mâu thuẫn.

 05 🔎 Kiểm căn cứ Đối chiếu với câu nói gốc bằng sáu nhóm kiểm tra.

 06 ⚠️ Xếp vị trí Phần chính hoặc Cần xác nhận, kèm lý do.

 07 📄 Tạo bản nháp Ghép bằng mẫu câu cố định.

 08 🩺 Bác sĩ duyệt Đối chiếu nguồn.
Giữ, sửa hoặc bỏ.

 Trong luồng tạo bản nháp từ văn bản, mô hình chỉ đề xuất mệnh đề. Các bước kiểm tra dùng luật có thể đọc được.

Ghi chú và nguồn: Luồng tổng hợp từ báo cáo FINAL mục 3.1 và README. Báo cáo có riêng bước chuẩn hóa bản ghi, ở đây gộp trong phần nhận đầu ra trước khi cập nhật trạng thái. Phiên âm dùng PhoWhisper nên không khẳng định toàn bộ hệ thống chỉ có một mô hình AI. Gợi ý hỏi lại có thiết kế nhưng chưa kích hoạt trong các phép đo.

## 06. Một mệnh đề có những gì?

💬 Lượt U04 · Bệnh nhân “Tôi ho một tuần…
à không,
 mười ngày rồi. ”
 Mỗi mệnh đề chỉ giữ một thông tin lâm sàng để kiểm tra riêng.

 Nội dung Ho 
 Người nói / chủ thể Bệnh nhân / bệnh nhân 
 Mức chắc chắn Khẳng định, không phủ định 
 Thời gian Mười ngày 
 Quan hệ Đính chính cho “một tuần” 
 Căn cứ U04 và câu trích nguyên văn

Ghi chú và nguồn: Theo báo cáo FINAL mục 3.2. Mã U04 là ví dụ minh họa. Tách riêng nội dung, người, mức chắc chắn, phủ định, tình huống, thời gian, quan hệ và bằng chứng giúp kiểm tra từng trường.

## 07. Lời sửa và mâu thuẫn

LỜI BAN ĐẦU “Ho một tuần”
 U03 · Bệnh nhân
 Đã bị thay thế

 ↩
 LỜI ĐÍNH CHÍNH “À không, mười ngày”
 U04 · Cùng bệnh nhân
 Thông tin hiện dùng

 Diễn biến theo thời gian
 “Hôm qua đau, hôm nay hết.”
Giữ cả hai mốc để thể hiện diễn biến.

 Hai người nói trái nhau
 Giữ nguồn và đánh dấu chưa giải quyết để bác sĩ xác nhận.

 Thông tin cũ không nằm trong phần chính nhưng vẫn có dấu vết để đối chiếu.

Ghi chú và nguồn: Báo cáo FINAL mục 3.3, src/cap_nhat.py và src/sinh_benh_an.py. Cùng người nói tự sửa được xử lý khác với mâu thuẫn giữa hai người. Trạng thái hiện dùng không đồng nghĩa chắc chắn đúng về lâm sàng.

## 08. Sáu nhóm kiểm tra căn cứ

K1 🔗 Nguồn
 Câu trích có thật trong lượt nói?

 K2 📝 Nội dung
 Thông tin có khớp câu được dẫn?

 K3 👥 Chủ thể
 Thông tin thuộc đúng người?

 K4 ❓ Mức khẳng định
 Có biến nghi ngờ hoặc điều kiện thành sự thật?

 K5 🕒 Thời gian
 Mốc thời gian có trong nguồn?

 K6 💊 Thuốc
 Liều và chi tiết thuốc có căn cứ?

 Qua kiểm tra Phần chính Cần làm rõ Cần xác nhận + lý do Đã bị thay thế Lưu vết 

 Máy kiểm tra qua chưa có nghĩa bác sĩ đã duyệt. Mức xử lý phụ thuộc loại lỗi và độ rõ của bằng chứng.

Ghi chú và nguồn: Báo cáo FINAL mục 3.4 và src/khoa_bang_chung.py. K2 và K5 phần lớn là cảnh báo, không nói rằng mọi sai lệch đều bị chặn. K6 chặn liều không thấy trong nguồn và cảnh báo các chi tiết như đường dùng, số lần, thời điểm bắt đầu/ngừng. Không khẳng định chặn mọi nội dung bịa.

## 09. Bác sĩ duyệt cùng bằng chứng

[Ảnh giao diện từ tài liệu dự án] Ảnh giao diện từ tài liệu dự án, sử dụng ca mô phỏng ✱ Từng dòng
có câu gốc
để đối chiếu
 Xem người nói, chủ thể và lý do cảnh báo ngay bên cạnh mệnh đề.
 ✓ Giữ
✎ Sửa
× Bỏ
 Bác sĩ quyết định nội dung cuối.

Ghi chú và nguồn: Ảnh gốc lấy từ trang 12 của PDF chi tiết do người dùng cung cấp. Chỉ dùng ảnh giao diện, không lấy các khẳng định cũ như tự động vào hồ sơ chính thức. Chức năng giữ/sửa/bỏ và liên kết lượt nói đối chiếu web/README.md và mã nguồn giao diện.

## 10. Dữ liệu và cách đánh giá

5.000 hội thoại mô phỏng 
 100 mẫu bệnh 
 47.825 mệnh đề đáp án 

 Huấn luyện Dev Cuối 
 Tập Ca Mẫu bệnh 
 Huấn luyện 3.776 75 
 Phát triển 634 13 
 Kiểm tra cuối 590 12 
 Chia theo mẫu bệnh. Tập cuối chưa dùng trong kết quả hiện tại.

 300 ca thử thách theo cặp
 Đổi chủ thể: 80 ca
Đính chính: 60 ca
Nhiễu giọng nói: 80 ca
Vùng miền: 80 ca
 5 phương án so sánh
 Viết trực tiếp, viết + tự soát,
và ba biến thể có cấu trúc.

Ghi chú và nguồn: Báo cáo FINAL mục 3.5, 3.7 và PDF 15 slide trang 9. Con số 3.776/634/590 lấy phiên bản 8b. Không dùng số 3.759/645/596 trong PDF chi tiết. Các bộ thử thách được tạo theo cặp gần giống nhau, không khẳng định chúng là hội thoại bệnh nhân thật.

## 11. Xử lý lời sửa giảm giữ bản cũ

Tỷ lệ giữ thông tin đã bị sửa
 Chỉ tách
thông tin 
 5,21% 
 Thêm xử lý
lời sửa 
 0,36% 
 0% 3% 6%
 Mẫu 240 ca từ tập phát triển. So sánh hai biến thể nội bộ.

 93,1 % Mức giảm tương đối
 Giảm 4,85 điểm phần trăm trên mẫu tổng hợp.
 Ở bộ đính chính 60 ca:
 11,48% xuống 0,80%. 

 ✓ H1b được ủng hộ trong phạm vi dữ liệu mô phỏng.

Ghi chú và nguồn: Báo cáo FINAL mục 4.2. Mức giảm tương đối tính (5.21-0.36)/5.21 = 93.09%, làm tròn 93,1%. Không gọi 93,1% là giảm điểm phần trăm. Bộ 60 ca và mẫu 240 ca là hai phép đo khác nhau. Không dùng số 5,06%/0,31% của PDF cũ.

## 12. Giảm lỗi đi kèm tăng bỏ sót

🔎 Lỗi nghiêm trọng
 Trước kiểm tra 43,0% 

 Sau kiểm tra 36,2% 

 Giảm 6,8 điểm phần trăm

 ⚠️ Bỏ sót
 Trước kiểm tra 4,5% 

 Sau kiểm tra 7,7% 

 Tăng 3,2 điểm phần trăm

 Bộ đổi chủ thể, 80 ca. Mỗi biểu đồ dùng thang riêng.

 H2 được ủng hộ một phần. Chuyển sang Cần xác nhận có thể đưa cả thông tin đúng ra khỏi phần chính.

Ghi chú và nguồn: Báo cáo FINAL mục 4.3 và bảng lỗi nghiêm trọng/bỏ sót. So sánh biến thể có xử lý lời sửa với biến thể thêm kiểm căn cứ, không phải viết trực tiếp với MediTrace. Lỗi nghiêm trọng gồm dị ứng, thuốc hoặc chẩn đoán trong phần chính. Bỏ sót là thông tin đáp án không có trong phần chính.

## 13. So sánh với viết trực tiếp

Bộ thử thách Viết trực tiếp MediTrace 
 Đổi chủ thể 0,9388 0,7476 
 Đính chính 0,9885 0,8299 
 Nhiễu giọng nói 0,8033 0,7009 
 Vùng miền 0,9735 0,8950 
 Điểm quy gán. Cao hơn là tốt hơn.

 ✱ H1 chưa
được ủng hộ
 Viết trực tiếp đạt điểm cao hơn ở cả bốn bộ thử thách.
 Dữ liệu dễ sao chép và thiết lập huấn luyện khác nhau, nên chưa tách riêng tác động của kiến trúc.

 Giá trị hiện tại của MediTrace nằm ở khả năng truy vết và xử lý lời sửa. Độ chính xác còn cần cải thiện.

Ghi chú và nguồn: Báo cáo FINAL mục 4.6 và PDF 15 slide trang 12. Không khẳng định hệ thống chính xác hơn viết trực tiếp. Hai phương án khác bộ trọng số, số bước và định dạng số học. Không quy toàn bộ chênh lệch cho dữ liệu dễ sao chép. H3: ROUGE-1 có thể không phát hiện đổi người, theo phép thử 400 hồ sơ.

## 14. Giới hạn và hướng phát triển

01 Hội thoại khó hơn
 Thêm nói chen, phương ngữ và tên thuốc. Giảm lợi thế sao chép bản mẫu.

 02 Đánh giá độc lập
 Hoàn thành chấm tay hai người. Khóa thiết lập rồi mở 590 ca cuối.

 03 Thử với bác sĩ
 Dùng hội thoại mô phỏng do người nói. Đo thời gian duyệt và số dòng cần sửa.

 Giới hạn hiện tại
 Chưa thử tại cơ sở khám bệnh.
Chưa chứng minh tiết kiệm thời gian.
 Âm thanh mới thử bằng 38 câu giọng máy.
WER khoảng 42,4–47,7%.
 Khoảng 213 giây/bản nháp
trên RTX 3060.

 Chép lời và tạo bản nháp chạy tại chỗ. Chức năng mô hình ngoài mặc định tắt, cần người dùng cho phép.

Ghi chú và nguồn: Báo cáo FINAL mục 4.7, 6 và 7, README và web/README. WER là tỷ lệ lỗi từ, chỉ thử 38 câu với giọng máy, không suy ra trên âm thanh thật. Trạng thái chấm tay mâu thuẫn giữa hai bản FINAL: báo cáo DOCX nói chưa chấm, PDF 15 slide nói 16/36. Không nêu số phiếu đã chấm, chỉ nói cần hoàn thành đánh giá. Chưa tích hợp HIS/EMR. Mô hình ngoài có thể truyền dữ liệu khi bật, vì vậy không nói dữ liệu không bao giờ rời máy.

## 15. Kết luận nghiên cứu

Mỗi dòng bản nháp
có căn cứ
để bác sĩ xem lại
 Xử lý lời sửa cho kết quả rõ trên dữ liệu mô phỏng.
Kiểm căn cứ làm hiện rõ sự đánh đổi lỗi và bỏ sót.
 Độ chính xác và hiệu quả trong quy trình khám
cần tiếp tục kiểm chứng.

 📄 + 🔎 + 🩺 

 Cảm ơn quý thầy cô và Ban Giám khảo
 Nhóm MediTrace · THPT Cầu Giấy

Ghi chú và nguồn: Tóm tắt báo cáo FINAL mục 5 và 6. Đóng góp hiện tại là truy vết, xử lý lời sửa và phân tích đánh đổi. Không có bằng chứng để khẳng định hiệu quả lâm sàng hay khả năng loại hết lỗi. Nguồn chính: MediTrace_BaoCao_FINAL.docx, MediTrace_15_slide_Times_New_Roman_Final.pdf, README và các mô-đun xử lý. PDF chi tiết cung cấp ảnh giao diện và ngữ cảnh sản phẩm.
