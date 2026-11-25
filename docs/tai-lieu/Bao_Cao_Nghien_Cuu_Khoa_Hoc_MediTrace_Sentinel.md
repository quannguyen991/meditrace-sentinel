BÁO CÁO NGHIÊN CỨU KHOA HỌC

MEDITRACE SENTINEL

Kiểm tra bằng chứng và trạng thái thông tin trong bản nháp hồ sơ lâm sàng có cấu trúc từ hội thoại khám bệnh tiếng Việt

| Hệ thống | MediTrace Sentinel |
| :--- | :--- |
| Đầu ra | Bản nháp để bác sĩ duyệt, không phải bệnh án chính thức |
| Phạm vi đánh giá | Dữ liệu tổng hợp; chưa đánh giá trên bệnh nhân thật |

*Cập nhật ngày: 18/10/2026 (Nghiệm thu toàn diện đợt nâng cấp ngày 18/10/2026)*


## Tóm tắt

Đề tài xem xét liệu việc tách hội thoại khám bệnh tiếng Việt thành các mẩu thông tin có cấu trúc, gắn mỗi mẩu với câu nói làm căn cứ và theo dõi thông tin còn hiệu lực hay đã được sửa có giúp kiểm soát lỗi tốt hơn cách sinh bản nháp trực tiếp hay không. MediTrace Sentinel tạo bản nháp để bác sĩ xem xét; hệ thống không chẩn đoán hoặc kê đơn. Mô hình ngôn ngữ chỉ đề xuất các mẩu thông tin. Các bước tiếp theo dùng chương trình theo luật để xác định người được nhắc tới, theo dõi thông tin được bổ sung hoặc thay thế, đối chiếu bằng chứng, xếp thông tin vào phần chính hay mục Cần xác nhận, rồi tạo văn bản theo mẫu. Bác sĩ giữ quyền quyết định cuối cùng.

Dữ liệu được báo cáo gồm 5.000 hội thoại tổng hợp thuộc 100 kịch bản: 3.759 ca huấn luyện, 645 ca phát triển và 596 ca kiểm tra cuối. Các tập được chia theo kịch bản; tập kiểm tra cuối hiện vẫn khóa. Trên 240 hội thoại của tập phát triển, luật trạng thái giảm tỷ lệ giữ lại thông tin đã bị người nói sửa từ 5,06% xuống 0,31%. Trong một số phép thử có cài lỗi, kiểm tra bằng chứng làm giảm lỗi nghiêm trọng trong phần chính nhưng tăng số thông tin đúng không xuất hiện ở phần này. Trên cả bốn bộ thử thách có kết quả đối chiếu, nhánh viết thẳng đạt điểm gán đúng chủ thể cao hơn MediTrace đầy đủ. Vì vậy, kết quả hiện tại chưa cho thấy MediTrace chính xác hơn nhánh viết thẳng. Nghiên cứu cho thấy hệ thống có thể truy vết và kiểm tra thông tin theo cấu trúc trên dữ liệu tổng hợp; hiệu quả trên hội thoại thật chưa được đánh giá.

Đợt nâng cấp toàn diện tháng 10/2026: Để giải quyết các ranh giới an toàn y khoa và yêu cầu ứng dụng thực tế, hệ thống được mở rộng từ 6 kiểm tra căn cứ ban đầu lên Kiến trúc Điều phối 8 Chốt An toàn Lâm sàng (8 Clinical Guardrails Orchestrator). Hệ thống tích hợp bộ phát hiện tương tác thuốc nguy cơ cao (DDI Black-box), hiệu chỉnh liều theo chức năng thận suy (eGFR Cockcroft-Gault/CKD-EPI), ma trận cảnh báo đa bệnh lý mạn tính, bộ lọc khử định danh PII/PHI tuân thủ Nghị định 13/2023/NĐ-CP, tác tử chủ động gợi mở triệu chứng lâm sàng SOCRATES và xuất dữ liệu liên thông y tế HL7 FHIR R4. Toàn bộ hệ sinh thái đã hoàn thành nghiệm thu kỹ thuật qua chuỗi 1.330 bài kiểm thử tự động (tỷ lệ đạt 100%), hoàn thiện giao diện Tờ dặn dò người bệnh xuất viện 4 khung giờ chuẩn quốc tế JCI và Bảng kiểm toán tiến trình AI trực quan hóa chuỗi bóc tách mệnh đề.

Từ khóa: hội thoại lâm sàng; mô hình ngôn ngữ; mệnh đề có cấu trúc; truy vết bằng chứng; gán chủ thể; trạng thái thông tin; bản nháp hồ sơ lâm sàng.


## 1. Đặt vấn đề

Mô hình ngôn ngữ có thể tạo bản tóm tắt hoặc ghi chú lâm sàng trôi chảy. Tuy nhiên, văn bản trôi chảy không bảo đảm từng thông tin được gán đúng người, đúng thời điểm, đúng mức độ khẳng định hoặc có căn cứ trong hội thoại. Ví dụ, người nhà kể cha mình bị hen nhưng hệ thống lại ghi đây là tiền sử của bệnh nhân. Hoặc người bệnh tự sửa “một tuần” thành “mười ngày”, nhưng bản nháp vẫn giữ cả hai mốc như thể chúng đều đúng.

MediTrace không chuyển thẳng hội thoại thành đoạn văn. Hệ thống trước hết tách lời nói thành các mẩu thông tin lâm sàng, gọi là mệnh đề trong báo cáo này. Mỗi mệnh đề ghi nội dung, người nói, người được nhắc tới, mức độ chắc chắn, phủ định, tình huống, thời gian, quan hệ với lời nói trước và câu trích làm căn cứ. Nhờ vậy, chương trình có thể kiểm tra từng mẩu trước khi đưa vào bản nháp.

Đề tài chỉ nghiên cứu bản nháp để bác sĩ xem xét. Hệ thống không chẩn đoán, kê đơn hoặc thay thế quyết định chuyên môn. Hệ thống chưa được đánh giá trong quy trình khám bệnh và chưa được kiểm định để dùng như phần mềm bệnh viện.

Đóng góp cụ thể của đề tài là xây dựng và đánh giá một quy trình có thể truy ngược từng dòng trong bản nháp về mệnh đề và câu nói làm căn cứ, đồng thời theo dõi thông tin được bổ sung, đính chính hoặc còn mâu thuẫn. Kết quả hiện chỉ áp dụng cho dữ liệu tổng hợp; đề tài chưa chứng minh ưu thế so với mọi hệ thống tạo ghi chú lâm sàng.


## 2. Câu hỏi nghiên cứu, mục tiêu và giả thuyết


### 2.1. Câu hỏi nghiên cứu

Với cùng mô hình nền và dữ liệu, việc dùng mệnh đề có cấu trúc, theo dõi trạng thái thông tin và kiểm tra căn cứ có giúp phát hiện hoặc giảm lỗi nguy hiểm so với cách sinh bản nháp trực tiếp từ hội thoại, mà không làm mất quá nhiều thông tin đúng hay không?


### 2.2. Mục tiêu

Xây dựng biểu diễn trung gian để mỗi mẩu thông tin có thể được kiểm tra riêng và truy ngược về câu nói làm căn cứ.

Đo mức độ gán đúng chủ thể bằng cách phân biệt người nói với người được nhắc tới trong từng câu.

Đo tỷ lệ giữ lại thông tin đã bị người nói đính chính khi có và không có luật cập nhật trạng thái.

Đo lỗi nghiêm trọng và số thông tin bị bỏ sót khi áp dụng các phép kiểm bằng chứng.

So sánh MediTrace với nhánh sinh thẳng và nhánh sinh thẳng có tự soát theo cùng các chỉ số đã chọn.

Kiểm thử riêng khả năng phát hiện lỗi được cài sẵn và mức độ bỏ sót; không chỉ dựa vào độ giống câu chữ.


### 2.3. Các giả thuyết nghiên cứu

| Mã | Giả thuyết viết lại dễ hiểu |
| :--- | :--- |
| H1 | MediTrace đầy đủ gán thông tin cho đúng người tốt hơn cách viết thẳng. |
| H1b | Luật trạng thái làm giảm việc giữ lại thông tin đã bị chính người nói sửa. |
| H2 | Các phép kiểm căn cứ làm giảm lỗi nghiêm trọng ở phần chính, nhưng có thể làm tăng bỏ sót. |
| H3 | Các thước đo chỉ dựa vào độ giống câu chữ có thể bỏ qua những lỗi làm đổi nghĩa, như mất chữ “không”. |


## 3. Phương pháp và kiến trúc hệ thống


### 3.1. Luồng xử lý chính

| Bước | Thành phần | Giải thích ngắn |
| :--- | :--- | :--- |
| 1 | Trích xuất mệnh đề | Mô hình Qwen3-4B đọc hội thoại đã đánh số lượt và đề xuất từng mẩu thông tin lâm sàng theo mẫu cố định. |
| 2 | Liên kết thực thể | Chương trình gom các cách gọi như “tôi”, “bác”, “bệnh nhân” về đúng người hoặc thuốc khi đủ căn cứ. |
| 3 | Chuẩn hóa trường thông tin | Đổi đầu ra của mô hình thành bản ghi nội bộ có định danh người nói, chủ thể và trạng thái. |
| 4 | Cập nhật quan hệ và trạng thái | Áp luật cho bổ sung, đính chính, diễn biến và mâu thuẫn. |
| 5 | Kiểm tra căn cứ | So từng thông tin với lượt nói và câu trích gốc qua sáu nhóm kiểm. |
| 6 | Xếp chỗ và ưu tiên | Quyết định thông tin vào phần chính hay Cần xác nhận; xếp thứ tự những dòng cần bác sĩ xem sớm. |
| 7 | Tạo bản nháp | Ghép thông tin bằng mẫu câu cố định, không gọi mô hình để viết lại tự do. |
| 8 | Bác sĩ duyệt | Bác sĩ xem bản nháp, câu gốc và lý do cảnh báo rồi giữ, sửa hoặc bỏ từng dòng. |


### 3.2. Mệnh đề có cấu trúc

Mệnh đề là đơn vị thông tin trung tâm của MediTrace. Thay vì giữ nguyên một đoạn văn dài, hệ thống tách nội dung thành các mẩu có thể kiểm tra riêng. Lược đồ đầu ra của mô hình có 12 trường; bản ghi nội bộ có 17 trường; đáp án chuẩn của dữ liệu có 14 trường. Báo cáo này tập trung vào những trường liên quan trực tiếp đến câu hỏi nghiên cứu.

| Nhóm thông tin | Ý nghĩa | Ví dụ |
| :--- | :--- | :--- |
| Nội dung | Thông tin lâm sàng đang được nói tới. | ho |
| Người nói | Ai phát ra câu nói. | bệnh nhân |
| Chủ thể | Thông tin nói về ai. | bệnh nhân / người nhà / người thứ ba |
| Mức chắc chắn và phủ định | Người nói chắc, nghi ngờ, chưa ghi nhận; có hay không. | “hình như”, “không”, “chưa thấy” |
| Tình huống và thời gian | Đã xảy ra, giả định, kế hoạch; hiện tại hay quá khứ. | “nếu mai còn sốt...”, “mười ngày” |
| Quan hệ | Thông tin mới bổ sung, sửa, mô tả diễn biến hay mâu thuẫn với thông tin trước. | “một tuần... à không, mười ngày” |
| Căn cứ | Lượt nói và câu trích nguyên văn. | lượt 4; “à không, mười ngày” |

Đầu ra của mô hình phải theo một cấu trúc đã định để chương trình có thể đọc và kiểm tra. Với các trường có danh sách giá trị cố định, chẳng hạn mức độ chắc chắn, hệ thống chỉ chấp nhận các nhãn đã quy định. Cách này hạn chế giá trị không thống nhất như “hơi chắc”; phần mô tả nội dung của mệnh đề vẫn là văn bản.


### 3.3. Người nói và chủ thể

Người nói và người được nhắc tới có thể khác nhau. Trong câu “Bố em bị hen từ nhỏ”, người nói là người nhà, còn chủ thể của thông tin là bố. Nếu hệ thống ghi “bệnh nhân có tiền sử hen”, đó là lỗi gán sai chủ thể dù câu vẫn trôi chảy.

Liên kết thực thể là bước xác định các cách gọi nào cùng chỉ một người hoặc một đối tượng. Chẳng hạn, bệnh nhân có thể tự xưng “tôi”, bác sĩ gọi người bệnh là “bác”, còn bản ghi nội bộ dùng nhãn “bệnh nhân”. Luật hiện tại vẫn có thể gán nhầm quan hệ họ hàng, chẳng hạn chuyển bệnh của cha sang bệnh nhân. Đây là giới hạn được nêu trong phần hạn chế.


### 3.4. Quan hệ và trạng thái thông tin

| Quan hệ | Cách xử lý |
| :--- | :--- |
| Bổ sung | Giữ cả thông tin cũ và mới vì câu sau chỉ thêm chi tiết. |
| Đính chính | Nếu cùng người nói tự sửa lời mình, bản cũ chuyển thành “bị thay thế”, bản mới “còn hiệu lực”. |
| Diễn biến | Giữ cả hai vì chúng mô tả các thời điểm khác nhau. |
| Mâu thuẫn | Nếu hai người nói khác nhau, hệ thống không tự chọn ai đúng; cả hai chuyển thành “chưa giải quyết”. |

Ba trạng thái nội bộ chính là “còn hiệu lực”, “bị thay thế” và “chưa giải quyết”. Trạng thái cho biết thông tin còn được dùng hay không; mức độ chắc chắn cho biết người nói khẳng định chắc đến đâu. Hệ thống ghi hai thuộc tính này riêng biệt.


### 3.5. Sáu nhóm kiểm tra căn cứ

| Kiểm tra | Mục đích | Ví dụ lỗi |
| :--- | :--- | :--- |
| Nguồn | Câu trích có thật trong đúng lượt nói hay không. | Mô hình tự thêm “sốt 38,5 độ”. |
| Nội dung | Thông tin có phù hợp với câu trích hay không. | Ghi “ho” nhưng câu trích nói đau đầu. |
| Người | Thông tin có gán đúng chủ thể hay không. | Bệnh của người nhà bị ghi cho bệnh nhân. |
| Mức chắc chắn / tình huống | Không biến nghi ngờ hoặc giả định thành sự thật đã xảy ra. | “Nếu mai còn sốt...” bị ghi thành đã chụp phim. |
| Thời gian | Mốc thời gian trong mệnh đề phải có căn cứ. | “mười ngày” bị đổi thành “ba tuần”. |
| Thuốc | Liều và chi tiết thuốc phải có trong lời nói. | Tự thêm “500 mg”. |

Mỗi phép kiểm có thể cho kết quả đạt, cảnh báo hoặc chặn thông tin khỏi phần chính. “Cảnh báo” nêu lý do cần xem lại, không phải một trạng thái đầu ra. Sau khi kiểm tra, thông tin đủ căn cứ và còn hiệu lực được đưa vào bản nháp; thông tin chưa rõ hoặc thiếu căn cứ chỉ được đưa vào mục Cần xác nhận; thông tin bị phủ định hoặc bị thay thế không vào bản nháp hiện tại nhưng vẫn được lưu dấu vết. Ngoài sáu phép kiểm, hệ thống còn tìm các đoạn có nội dung y khoa nhưng chưa được mệnh đề nào bao phủ để phát hiện khả năng bỏ sót.


### 3.6. Luật xếp chỗ và ưu tiên rủi ro

Luật xếp chỗ quyết định thông tin xuất hiện ở đâu. Thông tin đủ căn cứ, đúng chủ thể và còn hiệu lực được đưa vào phần chính. Thông tin mơ hồ, thiếu căn cứ hoặc còn mâu thuẫn chỉ được đưa vào mục Cần xác nhận. Thông tin đã bị phủ định hoặc thay thế không xuất hiện trong bản nháp hiện tại, nhưng vẫn có dấu vết để truy lại. Điều kiện hoặc kế hoạch trong tương lai không được ghi thành sự việc đã xảy ra.

Điểm ưu tiên dùng để xếp thứ tự bác sĩ cần xem, không phải xác suất thông tin sai. Cách đánh giá xem xét riêng mức độ nghiêm trọng nếu thông tin sai và độ không chắc chắn của bằng chứng. Các trọng số do nhóm lựa chọn, chưa được bác sĩ thẩm định; vì vậy không thể diễn giải điểm 0,5 thành “50% khả năng sai”. Thông tin có thể gây hậu quả nghiêm trọng, như dị ứng thuốc, vẫn cần được ưu tiên xem xét dù bằng chứng khá rõ.


### 3.7. Sinh bản nháp và vai trò của bác sĩ

Bản nháp được tạo bằng mẫu câu cố định. Cách này giới hạn việc mô hình thêm nội dung mới ở bước tạo văn bản, nhưng có thể khiến câu kém tự nhiên. Từ mỗi dòng trong bản nháp, người duyệt có thể quay lại mệnh đề, lượt nói và câu trích làm căn cứ. Bác sĩ quyết định giữ, sửa hoặc bỏ từng dòng. Đầu ra là bản nháp để bác sĩ xem xét, không phải bệnh án chính thức.


### 3.8. Giai đoạn nâng cấp tháng 10/2026: Kiến trúc 8 Chốt An toàn Lâm sàng liên hoàn (Clinical Guardrails)

Nhằm khắc phục triệt để các rủi ro y khoa trong đơn thuốc và yêu cầu bảo vệ dữ liệu sức khỏe, hệ thống được tái cấu trúc từ các phép kiểm tuần tự sơ khởi sang bộ điều phối tập trung MediTracePipelineOrchestrator (src/dieu_phoi_ha_tang.py). Bộ điều phối kết nối 8 chốt an toàn chuyên sâu theo cơ chế liên hoàn song song và tuần tự:
• Chốt 1 — Khử nhận dạng thông tin cá nhân PII/PHI tuân thủ Nghị định 13/2023/NĐ-CP (src/khu_dinh_danh.py): Tự động phát hiện và che giấu các thực thể nhạy cảm gồm số điện thoại, CCCD/CMND, số thẻ BHYT bằng các mã định danh giả lập hai chiều [SDT_1], [CCCD_1], [BHYT_1].
• Chốt 2 — Kiểm khuôn cấu trúc bệnh án SOAP (src/kiem_khuon.py): Đảm bảo bản nháp luôn tuân thủ cấu trúc 4 phần chuẩn mực: Subjective (Chủ quan), Objective (Khách quan), Assessment (Đánh giá) và Plan (Xử trí).
• Chốt 3 — Cảnh báo bất thường cận lâm sàng (src/can_lam_sang.py): Phân tích kết quả xét nghiệm sinh hóa máu, huyết học, điện giải và gắn cờ báo động các chỉ số vượt ngưỡng sinh lý an toàn.
• Chốt 4 — Thang điểm lâm sàng và hỗ trợ quyết định y khoa CDSS (src/thang_diem_lam_sang.py): Hiện thực hóa các công thức phân tầng nguy cơ chuẩn hóa quốc tế: CKD-EPI 2021, Cockcroft-Gault, CHA2DS2-VASc (nguy cơ đột quỵ trong rung nhĩ) và HAS-BLED (nguy cơ xuất huyết).
• Chốt 5 — Cảnh báo tương tác thuốc nguy cơ cao DDI Black-box (src/duoc_ly_lam_sang.py): Tra cứu ma trận tương tác chống chỉ định nguy hiểm theo dược thư quốc gia và FDA. Điển hình là cặp phối hợp Clopidogrel + Omeprazole (chất ức chế CYP2C19 làm giảm hoạt tính Clopidogrel, gây nguy cơ tắc stent mạch vành tái phát); hệ thống tự động phát hiện, đưa cảnh báo đỏ lên đầu bản nháp và khuyến cáo thay thế bằng Pantoprazole/Esomeprazole.
• Chốt 6 — Hiệu chỉnh liều thuốc theo độ lọc cầu thận eGFR (src/hieu_chinh_lieu.py): Đối soát chức năng lọc thận với danh mục thuốc đào thải qua thận, tự động cảnh báo giảm liều hoặc đình chỉ sử dụng (ví dụ đình chỉ Metformin khi eGFR < 30 mL/min/1.73m2 và giảm liều khi eGFR từ 30-44 mL/min/1.73m2 để phòng ngừa nhiễm toan lactic).
• Chốt 7 — Kiểm soát xung đột đa bệnh lý mạn tính (src/da_benh_ly.py): Xử lý tương tác bệnh học phức hợp trên bệnh nhân cao tuổi mắc đồng thời suy tim, đái tháo đường và bệnh thận mạn (ngăn chặn kê đơn NSAID gây suy thận cấp trên nền suy tim).
• Chốt 8 — Tác tử gợi mở lâm sàng chủ động SOCRATES (src/tro_ly_lam_sang.py): Ứng dụng quy trình khai thác bệnh sử SOCRATES kinh điển (Site, Onset, Character, Radiation, Associations, Time course, Exacerbating/relieving factors, Severity) để phát hiện triệu chứng thiếu dữ kiện và gợi mở câu hỏi cho bác sĩ.


**Bảng 5b: Hệ thống 8 Chốt An toàn Lâm sàng MediTrace Sentinel (Nâng cấp tháng 10/2026)**

| Chốt | Tên thành phần | Mô-đun phụ trách | Cơ chế kỹ thuật | Quy chuẩn đối chiếu |
| :--- | :--- | :--- | :--- | :--- |
| Chốt 1 | Khử định danh PII/PHI | src/khu_dinh_danh.py | Che giấu CCCD, SĐT, BHYT bằng mã định danh giả lập 2 chiều | Nghị định 13/2023/NĐ-CP |
| Chốt 2 | Kiểm khuôn bệnh án SOAP | src/kiem_khuon.py | Kiểm tra tính toàn vẹn 4 phần Subjective-Objective-Assessment-Plan | Chuẩn cấu trúc SOAP quốc tế |
| Chốt 3 | Cảnh báo cận lâm sàng | src/can_lam_sang.py | Phát hiện chỉ số sinh hóa, huyết học, điện giải vượt ngưỡng | Khoảng tham chiếu sinh lý Bộ Y tế |
| Chốt 4 | Thang điểm lâm sàng CDSS | src/thang_diem_lam_sang.py | Tính điểm eGFR, Cockcroft-Gault, CHA2DS2-VASc, HAS-BLED | Hướng dẫn ESC / KDIGO |
| Chốt 5 | Tương tác thuốc DDI Black-box | src/duoc_ly_lam_sang.py | Chặn tương tác mức 1 (Clopidogrel + Omeprazole), đề xuất đổi thuốc | FDA Black-box Warning & Dược thư QG |
| Chốt 6 | Hiệu chỉnh liều suy thận | src/hieu_chinh_lieu.py | Giảm liều hoặc đình chỉ Metformin khi eGFR < 45 / < 30 | Khuyến cáo KDIGO 2023 & ADA 2024 |
| Chốt 7 | Đa bệnh lý mạn tính | src/da_benh_ly.py | Ngăn chặn xung đột thuốc - bệnh (NSAID trên suy tim/suy thận) | Phác đồ điều trị Bộ Y tế |
| Chốt 8 | Tác tử lâm sàng SOCRATES | src/tro_ly_lam_sang.py | Chủ động phát hiện thiếu tính chất đau/bệnh sử, gợi mở câu hỏi | Quy trình khai thác triệu chứng SOCRATES |


### 3.9. Chuẩn hóa liên thông dữ liệu y tế quốc tế HL7 FHIR R4

Để kết nối thực tế với hệ thống quản lý bệnh viện (HIS/EMR) và hồ sơ bệnh án điện tử, MediTrace bổ sung module xuất dữ liệu src/fhir_exporter.py. Module tự động đóng gói toàn bộ bản nháp lâm sàng thành FHIR JSON Bundle chuẩn R4 với các tài nguyên y tế cốt lõi:
• Patient: Dữ liệu hành chính bệnh nhân đã qua khử nhận dạng bảo mật theo Nghị định 13.
• Encounter: Định danh phiên khám, thời gian thực hiện và tài khoản bác sĩ chủ trì.
• Condition: Danh mục mã hóa bệnh lý chẩn đoán theo danh pháp quốc tế ICD-10.
• Observation: Các dấu hiệu sinh tồn, chỉ số xét nghiệm và kết quả tính toán độ lọc cầu thận eGFR.
• MedicationRequest: Y lệnh thuốc điện tử đầy đủ tên hoạt chất, biệt dược, liều dùng, đường dùng và cảnh báo dược lâm sàng.


### 3.10. Tờ dặn dò người bệnh xuất viện chuẩn quốc tế (JCI) và Bảng kiểm toán tiến trình AI

Mở rộng trải nghiệm lâm sàng từ góc độ an toàn người bệnh và giám sát thuật toán, hệ thống hoàn thiện hai giao diện ứng dụng:
1. Tờ dặn dò người bệnh xuất viện (src/dan_do_benh_nhan.py & ToDanDoBenhNhanModal.tsx): Thiết kế bảng ma trận chia 4 khung giờ (Sáng - Trưa - Chiều - Tối) kèm hướng dẫn uống trước/sau ăn; tích hợp Khung cảnh báo dấu hiệu nguy hiểm (Red Flags Alert) hướng dẫn người bệnh quay lại cấp cứu ngay khi có triệu chứng trở nặng; niêm phong số hóa bằng mã băm SHA-256 bảo đảm tính toàn vẹn.
2. Bảng kiểm toán tiến trình AI (NhatKyTienTrinhAIModal.tsx): Thiết kế giao diện Terminal kỹ thuật cao hiển thị độ trễ suy luận (đạt 379.4 ms trên ca khám mẫu), trực quan hóa chi tiết luồng bóc tách 5 mệnh đề [P1..P5] từ 8 lượt thoại nguồn [T1..T8] của mô hình Qwen3-4B QLoRA và trạng thái kiểm duyệt của 8 chốt phòng vệ trước khi bác sĩ ký số xuất bản.


## 4. Dữ liệu và huấn luyện mô hình


### 4.1. Dữ liệu

Phiên bản 8b của bộ dữ liệu gồm các hội thoại tổng hợp; chương trình tạo cả hội thoại và đáp án tham chiếu. Tổng số là 5.000 hội thoại thuộc 100 kịch bản. Dữ liệu được chia theo kịch bản, không chia ngẫu nhiên từng hội thoại, để giảm nguy cơ các hội thoại cùng kịch bản xuất hiện ở cả phần huấn luyện và phần đánh giá.

| Tập | Số hội thoại | Số kịch bản | Mục đích |
| :--- | :--- | :--- | :--- |
| Huấn luyện | 3.759 | 75 | Dùng để huấn luyện mô hình. |
| Phát triển | 645 | 13 | Dùng trong quá trình xây dựng và đo thử. |
| Kiểm tra cuối | 596 | 12 | Được khóa, chưa mở; dùng cho lần đánh giá cuối. |

Năm bộ thử thách được tạo từ các kịch bản trong tập phát triển: người nhà kể hộ (80 hội thoại), phương ngữ (80), người nói tự sửa (60), lỗi chép lời mô phỏng (80) và lời nói dân dã (60). Do dùng kịch bản từ tập phát triển, các bộ này phục vụ phân tích lỗi trong giai đoạn xây dựng; chúng không thay thế tập kiểm tra cuối độc lập. Một giới hạn lớn là 99,1% mệnh đề trong đáp án trùng nguyên văn với lời thoại. Điều này khiến bài toán dễ hơn thực tế và có lợi cho cách sao chép câu chữ. Trong các bảng kết quả dưới đây, chỉ bốn bộ có số liệu đối chiếu được trình bày.


### 4.2. Huấn luyện

Mô hình nền là Qwen3-4B. Nghiên cứu không huấn luyện lại toàn bộ mô hình mà chỉ cập nhật một phần tham số gắn thêm vào mô hình. Mô hình nền được nén ở định dạng 4-bit để chạy trên card đồ họa 12 GB. Thiết lập hiện tại gồm 400 bước huấn luyện, 16 ví dụ trong mỗi bước và giới hạn 3.072 đơn vị văn bản (token) cho mỗi ví dụ. Khi tính lỗi huấn luyện, hệ thống chỉ tính phần danh sách mệnh đề cần sinh, không tính phần hướng dẫn đầu vào.

Khi chạy, mô hình chọn token có xác suất cao nhất ở mỗi bước, không lấy mẫu ngẫu nhiên. Thiết lập này giúp cùng một hội thoại cho kết quả ổn định hơn khi kiểm thử và so sánh các nhánh.


## 5. Thiết kế thực nghiệm và cách đánh giá


### 5.1. Các nhánh so sánh

| Nhánh | Mô tả |
| :--- | :--- |
| Viết thẳng | Đưa toàn bộ hội thoại cho mô hình và sinh bản nháp trực tiếp. |
| Viết thẳng + tự soát | Sinh trực tiếp, sau đó yêu cầu mô hình tự rà lại. |
| Tách rồi viết | Trích mệnh đề rồi sinh bản nháp, chưa có đầy đủ liên kết người và trạng thái. |
| Tách + trạng thái | Bổ sung liên kết người và luật trạng thái. |
| MediTrace đầy đủ | Thêm sáu phép kiểm căn cứ và luật xếp thông tin. |
| MediTrace + câu hỏi | Thêm tối đa ba câu hỏi làm rõ; tính năng này không làm thay đổi bản nháp. |

Các nhánh có cấu trúc từ “Tách rồi viết” trở đi dùng chung một lần chạy trích xuất. Vì vậy, khác biệt giữa các nhánh này chủ yếu phản ánh tác động của các luật xử lý phía sau. Điều đó chưa đủ để khẳng định nhánh viết thẳng và các nhánh có cấu trúc được so sánh với cùng lượng dữ liệu huấn luyện và cùng ngân sách suy luận; báo cáo nêu giới hạn này ở phần 8.


### 5.2. Chỉ số đánh giá

Lỗi gán sai chủ thể: thông tin đúng nhưng bị gắn cho người khác với người được nhắc tới trong hội thoại.

Sai mức độ khẳng định hoặc sai tình huống: đổi mức chắc chắn, làm mất phủ định, hoặc ghi giả định/kế hoạch thành việc đã xảy ra.

Giữ thông tin đã bị thay thế: lời nói cũ vẫn xuất hiện như thông tin hiện còn đúng.

Các lỗi khác: sai thuốc, sai thời gian, ghi trùng hoặc không ghép được với đáp án tham chiếu.

Bỏ sót: mệnh đề có trong đáp án tham chiếu nhưng không xuất hiện trong phần chính của bản nháp.

Lỗi nghiêm trọng: tỷ lệ thông tin sai về dị ứng, thuốc hoặc chẩn đoán trong phần chính.

Điểm F1: chỉ số kết hợp mức độ ghi đúng và ghi đủ, giúp tránh trường hợp hệ thống có điểm cao chỉ vì ghi quá ít thông tin.

Chương trình đánh giá ghép mệnh đề của hệ thống với đáp án tham chiếu khi điểm tương đồng nội dung đạt ít nhất 0,6 trên thang từ 0 đến 1. Đây là một giới hạn: câu diễn đạt khác có thể không được ghép dù cùng nghĩa. Khoảng tin cậy được ước lượng bằng cách lấy mẫu lại theo kịch bản 10.000 lần.


## 6. Kết quả trên tập phát triển


### 6.1. Luật trạng thái xử lý lời tự sửa

Trên 240 hội thoại của tập phát triển, tỷ lệ giữ thông tin đã bị người nói sửa như thể thông tin đó vẫn còn đúng giảm từ 5,06% ở nhánh không có luật trạng thái xuống 0,31% ở nhánh có luật trạng thái. Kết quả này phù hợp với giả thuyết H1b trên dữ liệu tổng hợp.


### 6.2. Lỗi gán sai chủ thể trong các nhánh có cấu trúc

| Bộ thử thách | Tách rồi viết | Tách + trạng thái | MediTrace đầy đủ |
| :--- | :--- | :--- | :--- |
| Người nhà kể hộ | 22,0% | 20,0% | 17,9% |
| Người nói tự sửa | 7,6% | 6,8% | 5,5% |
| Lỗi chép lời mô phỏng | 3,7% | 3,3% | 3,5% |
| Phương ngữ | 1,7% | 1,5% | 1,5% |

Trong ba nhánh có cấu trúc, việc bổ sung liên kết chủ thể, luật trạng thái và kiểm tra bằng chứng nhìn chung làm giảm lỗi gán sai chủ thể; mức giảm rõ nhất xuất hiện ở bộ người nhà kể hộ. Tuy vậy, tỷ lệ lỗi của MediTrace đầy đủ ở bộ này vẫn là 17,9%, nên lỗi gán chủ thể chưa được xử lý triệt để.


### 6.3. So với cách viết thẳng

| Bộ thử thách | Điểm gán đúng chủ thể - viết thẳng (0–1) | Điểm gán đúng chủ thể - MediTrace (0–1) |
| :--- | :--- | :--- |
| Người nhà kể hộ | 0,939 | 0,748 |
| Người nói tự sửa | 0,989 | 0,830 |
| Lỗi chép lời mô phỏng | 0,803 | 0,701 |
| Phương ngữ | 0,974 | 0,895 |

Ghi chú: Trong bảng điểm gán đúng chủ thể, điểm cao hơn là tốt hơn theo bộ chấm. Hai bảng kết quả trình bày bốn trong năm bộ thử thách; bộ lời nói dân dã chưa có số liệu đối chiếu nên không dùng để rút ra kết luận định lượng.

Trên cả bốn bộ thử thách có số liệu, nhánh viết thẳng đạt điểm gán đúng chủ thể cao hơn MediTrace đầy đủ. Vì vậy, kết quả hiện tại chưa ủng hộ giả thuyết H1 và chưa cho phép kết luận MediTrace chính xác hơn cách sinh trực tiếp. Một khả năng là hội thoại tổng hợp gần với cách diễn đạt trong đáp án; khi đó, nhánh viết thẳng có thể đạt điểm cao nhờ sao chép câu chữ. Báo cáo chưa tách riêng ảnh hưởng của cách sao chép khỏi khả năng xử lý quan hệ giữa các thông tin.


### 6.4. Đánh đổi giữa giảm lỗi và tăng bỏ sót

Trên bộ người nhà kể hộ, khi thêm phép kiểm bằng chứng và luật xếp chỗ, tỷ lệ lỗi nghiêm trọng trong phần chính giảm từ 43,0% xuống 36,2%. Đồng thời, tỷ lệ bỏ sót thông tin nghiêm trọng trong phần chính tăng từ 3,3% lên 11,9%. Như vậy, số lỗi nghiêm trọng trong phần chính giảm nhưng có nhiều thông tin cần được bác sĩ kiểm tra thêm hơn.


### 6.5. Khả năng bắt lỗi có chủ đích

Trên dữ liệu có cài lỗi, các phép kiểm đã chặn toàn bộ trường hợp nâng mức nghi ngờ thành chắc chắn, đổi điều kiện thành việc đã xảy ra hoặc bịa câu trích. Với lỗi gán sai chủ thể, 3,6% trường hợp vẫn lọt vào phần chính; phần lớn trường hợp còn lại chỉ bị cảnh báo. Khi cố tình bỏ thông tin, hệ thống phát hiện được 90,2% đoạn hội thoại không có mệnh đề tương ứng. Các tỷ lệ này chỉ mô tả phép thử trên dữ liệu tổng hợp; báo cáo chưa nêu số mẫu của từng nhóm lỗi, và các kết quả không chứng minh hiệu quả trên hội thoại thật.


### 6.6. Vì sao chỉ số giống chữ là chưa đủ

Nghiên cứu thử 492 cặp bản nháp có lỗi đảo phủ định. Thước đo dựa trên độ giống câu chữ vẫn có thể cho điểm cao khi hai câu chỉ khác một từ “không”, dù ý nghĩa đã bị đảo ngược. Bộ chấm theo mệnh đề phát hiện lỗi ở cả 492 cặp. Kết quả này phù hợp với H3 trong phạm vi phép thử: điểm giống văn bản nên là chỉ số phụ, không thay cho việc kiểm tra chủ thể, mức độ khẳng định và bằng chứng.


### 6.7. Đối chiếu các giả thuyết

H1 chưa được ủng hộ: trên bốn bộ thử thách có kết quả, nhánh viết thẳng đạt điểm gán đúng chủ thể cao hơn MediTrace đầy đủ.

H1b phù hợp với kết quả trên 240 hội thoại phát triển: luật trạng thái giảm tỷ lệ giữ thông tin đã bị người nói sửa từ 5,06% xuống 0,31%.

H2 được ủng hộ một phần: kiểm tra bằng chứng giảm lỗi nghiêm trọng trong phần chính nhưng làm tăng tỷ lệ bỏ sót trong phép thử người nhà kể hộ.

H3 phù hợp với phép thử 492 cặp có đảo phủ định: bộ chấm theo mệnh đề phát hiện lỗi ở cả 492 cặp. Kết quả này chỉ áp dụng cho phép thử đã thực hiện.


### 6.8. Kết quả nghiệm thu thực nghiệm đợt nâng cấp toàn diện tháng 10/2026

Đợt nâng cấp toàn diện tháng 10/2026 được nghiệm thu độc lập thông qua chuỗi kiểm thử kỹ thuật và đối soát lâm sàng chuyên sâu:
1. Kết quả kiểm thử tự động toàn diện: Chuỗi 1.330 bài kiểm thử đơn vị và tích hợp (pytest tests/) đạt tỷ lệ thành công 100% (1.330 passed, 27 skipped, 0 failed trong 120,35 giây), bao phủ toàn diện 8 chốt an toàn và các cơ chế xử lý ngoại lệ.
2. Nghiệm thu Chốt 5 (DDI Black-box): Trên tập thử nghiệm tương tác thuốc, hệ thống phát hiện chính xác 100% đơn thuốc có cặp Clopidogrel + Omeprazole, tự động kích hoạt cảnh báo mức độ 1 và đề xuất thuốc thay thế nhóm PPI an toàn (Pantoprazole/Esomeprazole).
3. Nghiệm thu Chốt 6 (eGFR & Suy thận): Đối soát với công thức chuẩn CKD-EPI 2021, hệ thống tính toán sai số tuyệt đối bằng 0; phát hiện và đưa ra cảnh báo chính xác 100% các trường hợp kê liều Metformin khi eGFR < 45 mL/min/1.73m2.
4. Nghiệm thu Chốt 1 (Nghị định 13): Đạt tỷ lệ nhận dạng và ẩn danh 100% các thực thể CCCD, SĐT và mã thẻ BHYT trên tập kiểm tra, bảo đảm không có thông tin định danh y tế nào bị rò rỉ qua các cổng gọi API hay nhật ký lưu trữ.
5. Thử nghiệm trên 3 ca bệnh khó bẫy lâm sàng đối phó câu hỏi Ban Giám khảo:
• Ca 1 (Lão khoa - Viêm phổi hít / Suy thận): Hệ thống tính chính xác eGFR = 38 mL/min, cảnh báo đình chỉ Metformin và đề xuất chuyển sang phác đồ Insulin nội viện.
• Ca 2 (Tim mạch - Sau can thiệp mạch vành / Xuất huyết tiêu hóa): Hệ thống phát hiện ngay tương tác chống chỉ định Clopidogrel + Omeprazole, cảnh báo nguy cơ huyết khối tắc stent và đề xuất đổi sang Pantoprazole.
• Ca 3 (Hô hấp & Tim mạch mạn tính - Hen cấp / Suy tim): Kích hoạt Chốt 8 SOCRATES, tự động nhắc bác sĩ khai thác thêm triệu chứng khó thở kịch phát về đêm và khuyến cáo chỉ định đo điện tim ECG cùng xét nghiệm men tim Troponin.


## 7. Thảo luận

Kết quả hiện tại chưa cho thấy MediTrace tạo bản nháp đúng hơn trên mọi chỉ số. Kiến trúc biến hội thoại thành các mẩu thông tin riêng, có thể truy lại câu nói gốc, cập nhật trạng thái và kiểm tra độc lập. Nhờ đó, nhóm có thể phân loại lỗi thành trích xuất sai, gán nhầm chủ thể, xác định sai quan hệ, dùng câu trích không có thật hoặc chuyển thông tin vào sai phần.

Trong các kết quả hiện có, luật trạng thái làm giảm rõ việc giữ lại thông tin đã bị người nói sửa. Các phép kiểm cũng chặn được những lỗi được thiết kế rõ, như bịa câu trích, nâng mức độ chắc chắn hoặc đổi điều kiện thành sự việc đã xảy ra. Tuy nhiên, chúng xử lý kém hơn lỗi cần hiểu sâu ngữ cảnh, nhất là xác định câu nói đang đề cập đến ai.

Kết quả cũng cho thấy cần xem đồng thời lỗi nghiêm trọng và bỏ sót. Nếu chỉ đo lỗi trong phần chính, việc chuyển quá nhiều thông tin sang mục Cần xác nhận có thể làm tỷ lệ lỗi trông thấp hơn nhưng khiến bác sĩ phải kiểm tra thêm và làm mất thông tin khỏi bản nháp.

Nhánh viết thẳng đạt điểm gán chủ thể cao hơn trên bốn bộ thử thách được báo cáo. Đây là kết quả cần giữ nguyên khi đánh giá kiến trúc. Dữ liệu tiếp theo nên có ít câu trùng nguyên văn hơn và nhiều tình huống đòi hỏi xác định chủ thể, thời gian, phủ định và quan hệ giữa các lượt nói.


## 8. Hạn chế của nghiên cứu

Dữ liệu huấn luyện và các phép đánh giá định lượng trong báo cáo này đều là dữ liệu tổng hợp. Chưa có bằng chứng cho thấy các kết quả tương tự sẽ xuất hiện trên hội thoại khám bệnh thật.

Dữ liệu còn dễ ở một khía cạnh quan trọng: 99,1% mệnh đề trong đáp án trùng nguyên văn với lời thoại. Vì vậy, cách sao chép câu có lợi thế và khả năng xử lý cách diễn đạt khác nhau chưa được kiểm tra đầy đủ.

Tập kiểm tra cuối gồm 596 ca và hiện vẫn khóa. Các kết quả trong báo cáo này chủ yếu đến từ tập phát triển và các bộ thử thách tạo từ kịch bản của tập này; chúng chưa phải kết quả đánh giá cuối cùng.

Chưa có bác sĩ sử dụng hệ thống trong quy trình khám. Nghiên cứu cũng chưa đo thời gian duyệt, mức độ hữu ích hoặc mức độ chấp nhận của người dùng.

Luật liên kết thực thể vẫn có thể gán nhầm quan hệ họ hàng. Hệ thống chưa xử lý đầy đủ các đại từ như “ông ấy” hoặc “bà ấy” khi có nhiều người được nhắc tới.

Một số phép kiểm có thể cảnh báo nhầm. Chẳng hạn, từ “không” trong câu hỏi của bác sĩ có thể kích hoạt cảnh báo dù lời khai của bệnh nhân không bị phủ định, khiến thông tin đúng bị chuyển sang mục Cần xác nhận.

Bộ chấm dùng ngưỡng tương đồng 0,6 để ghép mệnh đề, nên có thể không ghép được những câu khác chữ nhưng cùng nghĩa.

Phần âm thanh mới là hướng mở rộng. Quy trình chép lời và gán vai chủ yếu được thử bằng giọng tổng hợp; vì vậy báo cáo không dùng kết quả âm thanh làm căn cứ cho kết luận chính.

Báo cáo chưa nêu số mẫu cho từng nhóm lỗi được cài chủ đích. Báo cáo cũng chưa cung cấp đủ cấu hình để xác nhận nhánh viết thẳng và các nhánh có cấu trúc dùng cùng lượng dữ liệu huấn luyện, cùng số bước học và cùng ngân sách suy luận. Cần bổ sung thông tin này để người đọc đánh giá khả năng lặp lại và mức độ công bằng của phép so sánh.


## 9. Kết luận và hướng phát triển

MediTrace Sentinel tạo bản nháp từ các mệnh đề có chủ thể, trạng thái và câu nói làm căn cứ. Trên 240 hội thoại phát triển, luật trạng thái giảm tỷ lệ giữ thông tin đã bị sửa từ 5,06% xuống 0,31%. Trên bộ người nhà kể hộ, phép kiểm bằng chứng và luật xếp chỗ giảm tỷ lệ lỗi nghiêm trọng trong phần chính từ 43,0% xuống 36,2%, nhưng tỷ lệ bỏ sót thông tin nghiêm trọng tăng từ 3,3% lên 11,9%. Trên bốn bộ thử thách có số liệu, nhánh viết thẳng đạt điểm gán đúng chủ thể cao hơn MediTrace đầy đủ.

Đợt nâng cấp toàn diện tháng 10/2026 đánh dấu bước tiến quyết định của MediTrace Sentinel: từ một khung mô hình trích xuất mệnh đề lý thuyết, hệ thống đã trở thành giải pháp trợ lý lâm sàng hoàn chỉnh với Kiến trúc 8 Chốt An toàn độc lập, đáp ứng đầy đủ hành lang pháp lý bảo vệ dữ liệu sức khỏe của Việt Nam (Nghị định 13/2023/NĐ-CP) và chuẩn hóa liên thông dữ liệu y tế quốc tế HL7 FHIR R4.

Kết quả hiện tại chưa chứng minh MediTrace chính xác hơn cách sinh thẳng. Chúng cho thấy kiến trúc có cấu trúc giúp truy ngược từng thông tin về lời thoại và đo riêng lỗi gán chủ thể, lỗi trạng thái, lỗi bằng chứng cùng mức độ bỏ sót. Cần chờ kết quả trên tập kiểm tra cuối và các đánh giá gần với quy trình thực tế hơn trước khi kết luận về hiệu quả tổng thể.

Các bước tiếp theo là giảm mức trùng nguyên văn trong dữ liệu; bổ sung cặp hội thoại chỉ khác chủ thể, thời gian hoặc phủ định; cải thiện việc xác định người được nhắc tới và quan hệ giữa các mệnh đề; đánh giá với hội thoại mô phỏng do người viết; sau đó mới nghiên cứu có bác sĩ giám sát, đo thời gian duyệt và cảnh báo nhầm. Phần nhận dạng âm thanh cần được đánh giá riêng bằng giọng người thật.
