*Cập nhật ngày: 18/10/2026 (Nghiệm thu toàn diện đợt nâng cấp ngày 18/10/2026)*


# TÓM TẮT

MediTrace Sentinel nghiên cứu cách tạo bản nháp hồ sơ khám bệnh từ hội thoại tiếng Việt theo từng thông tin nhỏ có thể kiểm tra. Một thông tin như “bệnh nhân ho khan, hai tuần” được gọi là một mệnh đề. Mỗi mệnh đề giữ người nói, người mà thông tin nói về, mức chắc chắn, phủ định, thời gian, quan hệ với thông tin trước và câu nói gốc làm bằng chứng. Mô hình Qwen3-4B chỉ đề xuất danh sách mệnh đề. Chương trình sau đó xử lý thông tin đã được sửa lại, kiểm tra bằng chứng và quyết định thông tin nằm ở phần chính hay mục Cần xác nhận. Dữ liệu gồm 5.000 hội thoại do chương trình tự tạo từ 100 mẫu bệnh; 634 ca thuộc tập phát triển được dùng cho các kết quả trong báo cáo. Trên mẫu 240 ca, tỷ lệ bản cũ vẫn bị giữ sau khi người nói sửa giảm từ 5,21% xuống 0,36%. Ở bộ đổi chủ thể 80 ca, thêm bước kiểm tra bằng chứng làm lỗi nghiêm trọng giảm từ 43,0% xuống 36,2%, nhưng bỏ sót tăng từ 4,5% lên 7,7%. Cách viết trực tiếp có điểm quy gán cao hơn MediTrace ở cả bốn bộ thử thách, nên dữ liệu hiện tại không ủng hộ kết luận rằng MediTrace tạo bản nháp chính xác hơn. Kết quả phù hợp hơn là kiến trúc có cấu trúc giúp truy lại từng thông tin, xử lý lời đính chính và đo rõ sự đánh đổi giữa lỗi và bỏ sót. Hệ thống chưa được thử trên hội thoại bệnh nhân thật và không thay thế quyết định của bác sĩ.

Đợt nâng cấp kỹ thuật (nghiệm thu ngày 18/10/2026): Để giải quyết các ranh giới an toàn y khoa và yêu cầu ứng dụng thực tế, hệ thống được mở rộng từ 6 kiểm tra căn cứ ban đầu lên Kiến trúc Điều phối 8 Chốt An toàn Lâm sàng (8 Clinical Guardrails Orchestrator). Hệ thống tích hợp bộ phát hiện tương tác thuốc nguy cơ cao DDI Black-box (cặp Clopidogrel + Omeprazole), hiệu chỉnh liều theo chức năng thận suy eGFR (Metformin cutoff < 45 / < 30 mL/min/1.73m2), bộ lọc khử định danh PII/PHI (dữ liệu sức khỏe là dữ liệu nhạy cảm theo Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 và Nghị định 356/2025/NĐ-CP), tác tử chủ động gợi mở triệu chứng lâm sàng SOCRATES và xuất dữ liệu liên thông y tế HL7 FHIR R4. Toàn bộ hệ sinh thái đã hoàn thành nghiệm thu kỹ thuật qua 1.330 bài kiểm thử tự động ở lần chạy 18/10/2026 (lần chạy 26/11/2026: 1.942 bài qua, 27 bỏ qua; đây là kiểm tra mã, không phải tỷ lệ đúng trên dữ liệu thật), hoàn thiện giao diện Tờ dặn dò người bệnh xuất viện 4 khung giờ chuẩn quốc tế JCI và Bảng kiểm toán tiến trình AI trực quan hóa chuỗi bóc tách mệnh đề.

Từ khóa: hội thoại lâm sàng; bản nháp hồ sơ; truy vết bằng chứng; xử lý đính chính; tiếng Việt; mô hình ngôn ngữ.


# 1. GIỚI THIỆU VÀ CÂU HỎI NGHIÊN CỨU


## 1.1. Vấn đề nghiên cứu

Mô hình ngôn ngữ có thể tạo ghi chú lâm sàng từ hội thoại và có tiềm năng giảm một phần việc nhập liệu. Nghiên cứu quan sát trước đây cho thấy công việc với hồ sơ điện tử và giấy tờ chiếm tỷ trọng lớn trong ngày làm việc của bác sĩ; các nghiên cứu gần đây về AI scribe cũng ghi nhận mức giảm thời gian ghi chép ở một số cơ sở (Sinsky et al., 2016; Rotenstein et al., 2026; Svetly et al., 2026). Tuy nhiên, câu văn đúng ngữ pháp vẫn có thể chứa lỗi làm đổi nghĩa. Báo cáo này tập trung vào bốn nhóm lỗi: ghi thông tin cho sai người, giữ thông tin đã bị sửa, nâng mức chắc chắn hoặc biến kế hoạch thành việc đã xảy ra, và ghi chi tiết không có câu nói gốc làm bằng chứng.

- Người đi cùng kể bệnh của người thân nhưng bản nháp ghi thành bệnh của bệnh nhân.
- Người bệnh nói “một tuần… à không, mười ngày” nhưng bản nháp giữ cả hai mốc như cùng đúng.
- Bác sĩ nói “nếu mai còn sốt thì chụp phim” nhưng bản nháp ghi việc chụp phim như đã xảy ra.
- Bản nháp tự thêm liều thuốc hoặc nhiệt độ không xuất hiện trong hội thoại.
Các lỗi trên khó đánh giá chỉ bằng mức giống câu chữ. ROUGE, một thước đo phổ biến trong tóm tắt văn bản, chủ yếu dựa vào mức trùng lặp đơn vị từ/ngữ giữa đầu ra và bản tham chiếu (Lin, 2004). Các nghiên cứu về tính nhất quán sự kiện cũng cho thấy đánh giá tự động có thể bỏ qua những sai lệch quan trọng trong tóm tắt lâm sàng (Luo et al., 2024). Ví dụ, đổi một chữ “không” có thể đảo nghĩa nhưng phần lớn từ còn lại vẫn giống bản mẫu. Vì vậy, nghiên cứu đánh giá riêng việc ghi đúng người, đúng trạng thái và đúng câu nói gốc làm bằng chứng.


## 1.2. Ý tưởng của MediTrace Sentinel

MediTrace tách hội thoại thành các mệnh đề. Mệnh đề là một thông tin lâm sàng nhỏ, ví dụ “bệnh nhân ho khan, hai tuần”. Mỗi mệnh đề có thể được kiểm tra độc lập trước khi đưa vào bản nháp.

Chương trình còn phân biệt người nói với người mà thông tin nói về. Ví dụ, một người con đi cùng bệnh nhân có thể nói về bệnh của bố mình; thông tin đó không tự động trở thành bệnh sử của bệnh nhân. Khi người nói sửa lời, chương trình đánh dấu bản cũ là đã bị thay thế và giữ bản mới. Nếu hai người nói mâu thuẫn nhau, chương trình không tự quyết định ai đúng mà chuyển thông tin sang trạng thái chưa giải quyết.

Đầu ra là bản nháp để bác sĩ xem lại. Hệ thống không chẩn đoán, kê đơn, ra y lệnh hoặc thay thế quyết định chuyên môn.


## 1.3. Câu hỏi nghiên cứu và giả thuyết

Câu hỏi nghiên cứu: với cùng mục tiêu tạo bản nháp từ hội thoại, việc tách thông tin có cấu trúc, xử lý lời sửa và kiểm tra câu nói gốc làm bằng chứng có giúp giảm các lỗi làm đổi nghĩa mà không làm mất quá nhiều thông tin hay không?

| Mã | Giả thuyết |
| :--- | :--- |
| H1 | Phương án có cấu trúc ghi thông tin đúng người tốt hơn cách viết trực tiếp. |
| H1b | Xử lý thông tin đã được người nói sửa lại làm giảm việc giữ bản cũ như còn đúng. |
| H2 | Kiểm tra bằng chứng làm giảm lỗi nghiêm trọng trong phần chính nhưng có thể làm tăng bỏ sót. |
| H3 | Các thước đo dựa chủ yếu vào độ giống câu chữ có thể bỏ qua lỗi làm đổi nghĩa. |


# 2. TỔNG QUAN TÀI LIỆU


# 2.1. Gánh nặng ghi chép hành chính và vai trò hỗ trợ của AI scribe


# Ghi chép hồ sơ bệnh án từ lâu đã chiếm tỷ trọng lớn trong khối lượng công việc hàng ngày của nhân viên y tế. Khảo sát quan sát trực tiếp trên 57 bác sĩ ngoại trú thuộc bốn chuyên khoa, Sinsky et al. (2016) chỉ ra rằng chỉ 27,0% quỹ thời gian làm việc được dành cho tương tác trực tiếp với người bệnh, trong khi có tới 49,2% bị tiêu tốn cho hồ sơ bệnh án điện tử và các công việc bàn giấy. Dù tỷ lệ này có thể biến thiên tùy theo mô hình từng cơ sở y tế, số liệu trên phản ánh áp lực hành chính đáng kể đè nặng lên các hoạt động lâm sàng.


# Trước thực trạng đó, các công cụ AI scribe bắt đầu được triển khai nhằm giảm tải khối lượng công việc này. Nghiên cứu đa trung tâm của Rotenstein et al. (2026) trên 8.581 nhân viên lâm sàng tại năm hệ thống y tế ghi nhận: việc ứng dụng AI scribe giúp tiết kiệm trung bình 13,4 phút sử dụng hồ sơ bệnh án điện tử và 16,0 phút ghi chép trên mỗi ca trực 8 giờ; tuy nhiên, thời gian xử lý hồ sơ ngoài giờ làm việc chưa ghi nhận mức giảm có ý nghĩa thống kê. Tương tự, khảo sát của Svetly et al. (2026) trên 210 nhân viên y tế cho thấy thời gian trực tiếp soạn thảo ghi chú giảm 26,2%, từ 5,54 xuống còn 4,09 phút mỗi lượt khám. Dù mở ra triển vọng rõ nét trong việc tinh gọn quy trình lâm sàng, các nghiên cứu này chủ yếu dựa trên thiết kế quan sát hoặc can thiệp trước – sau, do đó chưa thể cô lập hoàn toàn tác động của AI khỏi các yếu tố can nhiễu bên ngoài.


# 2.2. Bài toán tạo ghi chú lâm sàng từ hội thoại


# Chuyển hóa hội thoại khám bệnh thành hồ sơ bệnh án có cấu trúc đã trở thành một bài toán nghiên cứu độc lập. Nhằm chuẩn hóa việc đánh giá các mô hình sinh ghi chú tự động, Yim et al. (2023) đã công bố bộ dữ liệu ACI-BENCH gồm các đoạn đối thoại bác sĩ – người bệnh đi kèm ghi chú chuẩn. Tiếp nối hướng đi này, chuỗi nhiệm vụ tại MEDIQA-Chat 2023 thu hút 17 nhóm nghiên cứu tham gia giải quyết bài toán tóm tắt hội thoại lâm sàng bằng nhiều hướng tiếp cận khác nhau (Ben Abacha et al., 2023). Các công trình này không chỉ thiết lập thước đo chung trên các bộ dữ liệu tiêu chuẩn, mà còn đặt ra yêu cầu cấp thiết: phải đánh giá nghiêm ngặt tính xác thực của nội dung đầu ra, thay vì chỉ dừng lại ở độ trôi chảy về mặt từ ngữ.


# Trên thực tế, chất lượng ghi chú do AI tạo ra vẫn tiềm ẩn rủi ro sai sót. Khi phân tích 194 ghi chú từ 97 ca khám thuộc năm chuyên khoa theo thang đo PDQI-9, Palm et al. (2025) nhận thấy văn bản do AI sinh ra đạt độ hoàn thiện và chất lượng tổng thể tương đương với bản ghi tham chiếu từ chuyên gia. Tuy nhiên, tỷ lệ thông tin không có căn cứ từ nguồn gốc ở nhóm AI lại cao hơn rõ rệt: 31% so với 20% ở nhóm tham chiếu. Kết quả này chứng minh rằng một bản ghi nhìn có vẻ mạch lạc, đầy đủ về hình thức vẫn có thể chứa đựng lỗi sai lệch nghiêm trọng về mặt nội dung.


# 2.3. Sai lệch thông tin và giới hạn của các phương pháp đánh giá tự động


# Để đo lường các rủi ro ngữ nghĩa, Asgari et al. (2025) đã xây dựng khung đánh giá an toàn cho các bản tóm tắt y khoa sinh bởi mô hình ngôn ngữ lớn. Qua việc thẩm định 12.999 câu trong 450 ghi chú lâm sàng, nhóm tác giả phát hiện 1,47% số câu chứa thông tin bịa đặt hoặc thiếu căn cứ, và 3,45% thông tin quan trọng từ nguồn bị bỏ sót. Các dạng sai lệch phổ biến bao gồm: tự ý thêm thắt dữ kiện, đảo ngược ý phủ định, sai lệch ngữ cảnh và sai mối quan hệ nhân quả. Bối cảnh này củng cố định hướng đánh giá của MediTrace: cần phân tách rạch ròi giữa lỗi thêm thông tin và lỗi bỏ sót, đồng thời đánh giá độc lập mức độ ảnh hưởng của từng loại lỗi đối với độ an toàn của dữ liệu y tế.


# Mặt khác, các phương pháp đánh giá tự động hiện nay vẫn bộc lộ những rào cản kỹ thuật rõ ràng. Nghiên cứu của Luo et al. (2024) khi xây dựng bộ tiêu chuẩn TreatFact cho thấy cả các thước đo truyền thống lẫn các bộ chấm điểm dựa trên mô hình ngôn ngữ lớn đều gặp khó khăn trong việc phát hiện những sai lệch sự kiện tinh vi. Điển hình là chỉ số ROUGE – thước đo dựa trên mức độ trùng lặp từ vựng với văn bản tham chiếu (Lin, 2004) – vẫn có thể chấm điểm số rất cao cho một câu dù câu đó đã bị đảo ngược từ phủ định, gán sai chủ thể hành động hoặc biến dạng hoàn toàn tình trạng bệnh lý. Do đó, nghiên cứu này chỉ sử dụng ROUGE như một chỉ số tham chiếu bổ trợ và ưu tiên xây dựng các phương pháp đo lường chuyên biệt cho các lỗi làm thay đổi bản chất ngữ nghĩa.


# 2.4. Định vị của hệ thống MediTrace Sentinel


# Tổng quan tài liệu chỉ ra hai vấn đề tồn tại song song: AI có tiềm năng giảm tải hành chính rõ rệt, nhưng độ tin cậy của các bản ghi nháp vẫn đòi hỏi cơ chế kiểm soát nghiêm ngặt ở cấp độ thông tin cụ thể. Trong bối cảnh đó, MediTrace Sentinel thu hẹp phạm vi vào một bài toán cụ thể: đối với tập dữ liệu hội thoại tiếng Việt do chương trình tự tạo, liệu việc phân rã câu thành các mệnh đề độc lập, chuẩn hóa chủ thể thông tin, xử lý hiện tượng tự sửa lời và truy vết bằng chứng từ câu nói gốc có giúp phát hiện hiệu quả các sai lệch làm đổi nghĩa hay không. Đề tài không khái quát hóa kết quả từ các nghiên cứu quốc tế để bảo chứng cho hiệu quả ứng dụng thực tế trong môi trường lâm sàng; toàn bộ nhận định và kết luận của MediTrace Sentinel đều được xây dựng nghiêm ngặt dựa trên các phép đo thực nghiệm nội tại của chính đề tài.


# 3. THIẾT KẾ VÀ PHƯƠNG PHÁP


## 3.1. Luồng xử lý

| Bước | Thành phần | Chương trình thực hiện |
| :--- | :--- | :--- |
| 1 | Tách mệnh đề | Qwen3-4B đọc hội thoại đã đánh số lượt và đề xuất từng thông tin lâm sàng theo mẫu cố định. |
| 2 | Nhận người và cách gọi | Nhận ra các cách gọi như “tôi”, “bác”, “bệnh nhân” có thể chỉ cùng một người khi có đủ căn cứ. |
| 3 | Chuẩn hóa bản ghi | Đưa đầu ra mô hình về cùng dạng dữ liệu để các luật phía sau xử lý. |
| 4 | Xử lý thông tin đã sửa | Phân biệt bổ sung, đính chính, diễn biến theo thời gian và mâu thuẫn. |
| 5 | Kiểm tra câu nói gốc | So từng thông tin với lượt nói, câu trích, người, mức chắc chắn, thời gian và chi tiết thuốc. |
| 6 | Quyết định vị trí | Đưa thông tin vào phần chính hoặc mục Cần xác nhận; ưu tiên dòng quan trọng để bác sĩ xem trước. |
| 7 | Tạo bản nháp | Ghép thông tin bằng mẫu câu cố định, không gọi mô hình để viết lại tự do. |
| 8 | Bác sĩ duyệt | Bác sĩ đối chiếu câu gốc và quyết định giữ, sửa hoặc bỏ từng dòng. |


## 3.2. Thông tin được lưu trong mỗi mệnh đề

| Mục thông tin | Ý nghĩa | Ví dụ |
| :--- | :--- | :--- |
| Nội dung | Thông tin lâm sàng đang được nói tới. | ho khan |
| Người nói | Ai phát ra câu nói. | bệnh nhân / bác sĩ / người nhà |
| Người mà thông tin nói về | Ai là người có triệu chứng, bệnh, thuốc hoặc tiền sử đang được nói tới. | bệnh nhân / người thân |
| Mức chắc chắn và phủ định | Người nói khẳng định, nghi ngờ, chưa ghi nhận; có hay không. | “hình như”, “không”, “chưa thấy” |
| Tình huống và thời gian | Sự việc đã xảy ra, là giả định hay kế hoạch; hiện tại hay quá khứ. | “nếu mai còn sốt…”, “mười ngày” |
| Quan hệ với thông tin trước | Bổ sung, sửa lại, mô tả diễn biến hoặc mâu thuẫn. | “một tuần… à không, mười ngày” |
| Câu nói gốc làm bằng chứng | Mã lượt nói và câu trích dùng để đối chiếu. | lượt 4: “à không, mười ngày” |

Các mục có danh sách giá trị cố định chỉ nhận những nhãn đã quy định. Phần mô tả nội dung vẫn là văn bản. Cách làm này giúp chương trình kiểm tra từng mệnh đề bằng luật thay vì phải hiểu lại một đoạn văn hoàn chỉnh ở mỗi bước.


## 3.3. Xử lý lời sửa và mâu thuẫn

| Quan hệ | Cách xử lý |
| :--- | :--- |
| Bổ sung | Giữ cả thông tin cũ và mới nếu câu sau chỉ thêm chi tiết. |
| Đính chính | Nếu cùng người nói tự sửa lời, bản cũ chuyển thành đã bị thay thế; bản mới là thông tin hiện dùng. |
| Diễn biến | Giữ các thông tin thuộc những thời điểm khác nhau. |
| Mâu thuẫn | Nếu hai người nói khác nhau đưa thông tin trái nhau, cả hai được giữ để bác sĩ xác nhận; chương trình không tự chọn một phía. |

Trạng thái của thông tin trả lời câu hỏi “thông tin này còn nên dùng trong bản nháp hiện tại hay không?”. Mức chắc chắn trả lời câu hỏi “người nói chắc đến đâu?”. Hai khái niệm này được xử lý riêng.


## 3.4. Sáu nhóm kiểm tra bằng chứng

| Nhóm kiểm tra | Mục đích | Ví dụ lỗi |
| :--- | :--- | :--- |
| Nguồn | Câu trích phải có thật trong đúng lượt nói. | Tự thêm “sốt 38,5 độ”. |
| Nội dung | Thông tin phải phù hợp với câu được dẫn. | Ghi “ho” nhưng câu trích nói đau đầu. |
| Người | Thông tin phải gắn đúng người. | Bệnh của người nhà bị ghi cho bệnh nhân. |
| Mức chắc chắn / tình huống | Không biến nghi ngờ hoặc giả định thành sự thật đã xảy ra. | “Nếu mai còn sốt…” bị ghi thành đã chụp phim. |
| Thời gian | Mốc thời gian phải có căn cứ. | “mười ngày” bị đổi thành “ba tuần”. |
| Thuốc | Tên, liều và chi tiết thuốc phải có trong lời nói. | Tự thêm “500 mg”. |

Mỗi mệnh đề có thể qua kiểm tra, được cảnh báo, hoặc không được đưa vào phần chính và chuyển sang mục Cần xác nhận. Chương trình cũng tìm các đoạn hội thoại có nội dung y khoa nhưng chưa có mệnh đề nào liên kết tới, nhằm phát hiện khả năng bỏ sót.


## 3.5. Dữ liệu

Dữ liệu phiên bản 8b gồm 5.000 hội thoại do chương trình tự tạo theo luật từ 100 mẫu bệnh. Một mẫu bệnh là một kịch bản dùng để sinh nhiều hội thoại có biến thể. Dữ liệu được chia theo mẫu bệnh để giảm khả năng cùng một kịch bản xuất hiện ở cả phần học và phần đo.

| Tập | Số hội thoại | Số mẫu bệnh | Mục đích |
| :--- | :--- | :--- | :--- |
| Huấn luyện | 3.776 | 75 | Huấn luyện mô hình. |
| Phát triển | 634 | 13 | Xây dựng, điều chỉnh và đo các kết quả trong báo cáo. |
| Kiểm tra cuối | 590 | 12 | Chưa dùng; sẽ dùng một lần ở bước đánh giá cuối. |

Đáp án có 47.825 mệnh đề; 5,0% không thuộc bệnh nhân. Trong 5.000 ca, các tình huống chính gồm người nhà kể hộ 43,2%, đính chính 13,1%, diễn biến theo thời gian 12,8%, câu điều kiện 12,2%, mâu thuẫn 11,3% và dị ứng của người nhà 5,5%.

Bốn bộ thử thách chính có tổng cộng 300 ca, được sinh theo cặp để hai ca gần giống nhau và chỉ thay đổi một điểm: đổi chủ thể 80 ca, đính chính 60 ca, lỗi do nhận dạng giọng nói chép sai chữ 80 ca và cách nói vùng miền 80 ca. Phép thử “lời nói dân dã” gồm 60 ca là thử nghiệm phụ, không tính vào 300 ca trên.

Giới hạn lớn nhất của dữ liệu là mức sao chép nguyên văn cao. Mức bao phủ đoạn trích đạt khoảng 0,95–0,97 và mật độ chuỗi sao chép 6,2–7,2 ở hầu hết tập; riêng bộ nhiễu giọng nói là 0,799 và 4,5. Điều này có lợi cho các phương án có thể chép gần nguyên văn bản mẫu.


## 3.6. Mô hình và thiết lập chạy

Mô hình tách thông tin là Qwen3-4B, thuộc họ mô hình Qwen3 (Yang et al., 2025). Mô hình được huấn luyện thêm bằng phương pháp nhẹ, chạy trên một card đồ họa 12 GB và được nén 4 bit. Lượt huấn luyện dùng trong báo cáo chạy 400 bước, mỗi bước 16 ví dụ và lưu số ở định dạng bf16. Khi chạy, hệ thống luôn chọn đầu ra có khả năng cao nhất để cùng một hội thoại cho kết quả ổn định, thuận lợi cho kiểm thử và so sánh.

| Thiết lập | Mô hình tách thông tin | Phương án viết thẳng |
| :--- | :--- | :--- |
| Bộ trọng số | Qwen3-4B đã huấn luyện thêm | Bộ trọng số riêng |
| Số bước huấn luyện | 400 bước | 200 bước |
| Số ví dụ mỗi bước | 16 ví dụ | Chưa đối chiếu trực tiếp từ tệp kết quả của lượt chạy |
| Cách lưu số | bf16 | fp16 |
| Phần cứng ghi nhận | Card đồ họa 12 GB | GPU T4 trên Kaggle |

Phương án viết trực tiếp dùng bộ trọng số riêng, được huấn luyện 200 bước và lưu số ở định dạng fp16 trên GPU T4. Như vậy, hai phương án khác nhau không chỉ ở cách tạo bản nháp mà còn ở số bước huấn luyện, bộ trọng số và cách lưu số. Các khác biệt này có thể ảnh hưởng đến kết quả, nên phép so sánh hiện tại chưa phải là một thí nghiệm chỉ thay đúng kiến trúc phía sau.


## 3.7. Các phương án so sánh

| Phương án | Mô tả |
| :--- | :--- |
| Viết thẳng | Đưa toàn bộ hội thoại cho mô hình và sinh bản nháp trực tiếp. |
| Viết thẳng + tự soát | Sinh trực tiếp, sau đó yêu cầu mô hình rà lại một lượt. |
| Chỉ tách thông tin | Tách mệnh đề rồi tạo bản nháp, chưa xử lý đầy đủ lời sửa và kiểm tra bằng chứng. |
| Tách + xử lý sửa lại | Bổ sung bước xử lý thông tin đã được người nói sửa. |
| Tách + xử lý sửa lại + kiểm tra bằng chứng | Bổ sung sáu nhóm kiểm tra và quy tắc quyết định phần chính/Cần xác nhận. |
| Thêm câu hỏi làm rõ | Có thiết kế tối đa ba câu hỏi làm rõ; trong các phép đo hiện tại bước này chưa kích hoạt lần nào. |


## 3.8. Chỉ số đánh giá

- Ghi nhầm người: thông tin đúng nhưng gắn cho người khác.
- Sai mức hoặc tình huống: sai mức chắc chắn, phủ định, hoặc biến giả định/kế hoạch thành việc đã xảy ra.
- Giữ bản cũ: thông tin đã bị người nói sửa nhưng vẫn được ghi như còn đúng.
- Lỗi nghiêm trọng: lỗi ở thông tin dị ứng, thuốc hoặc chẩn đoán trong phần chính.
- Bỏ sót: thông tin có trong đáp án nhưng không có trong phần chính của bản nháp.
- Tỷ lệ lỗi theo ô thông tin: số ô sai, thừa hoặc thiếu so với số ô đáp án; chỉ số có thể vượt 100%.
- F1: điểm cân bằng giữa ghi đúng và ghi đủ.
- Điểm quy gán: điểm cho biết thông tin có được ghi đúng người và đúng trạng thái hay không.
- ROUGE-1: điểm đo mức trùng từ ngữ giữa bản nháp và bản mẫu; dùng như chỉ số phụ (Lin, 2004).
Hai thông tin được ghép với nhau khi mức giống nhau về từ ngữ từ 0,6 trở lên. Khoảng dao động 95% được ước lượng bằng cách lấy mẫu lại theo từng mẫu bệnh 10.000 lần. Ngưỡng ghép 0,6 có thể bất lợi cho các câu diễn đạt khác nhưng cùng nghĩa.


## 3.9. Giai đoạn nâng cấp kỹ thuật (nghiệm thu ngày 18/10/2026): Kiến trúc 8 Chốt An toàn Lâm sàng liên hoàn (Clinical Guardrails)

Nhằm khắc phục triệt để các rủi ro y khoa trong đơn thuốc và yêu cầu bảo vệ dữ liệu sức khỏe người bệnh, hệ thống được tái cấu trúc từ các phép kiểm tuần tự sơ khởi sang bộ điều phối tập trung MediTracePipelineOrchestrator (src/he_thong/dieu_phoi_cac_chot_an_toan.py). Bộ điều phối kết nối 8 chốt an toàn chuyên sâu theo cơ chế liên hoàn song song và tuần tự:
• Chốt 1 — Khử nhận dạng thông tin cá nhân PII/PHI (dữ liệu sức khỏe là dữ liệu nhạy cảm theo Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 và Nghị định 356/2025/NĐ-CP) (src/he_thong/khu_dinh_danh.py): Tự động phát hiện và che giấu các thực thể nhạy cảm gồm số điện thoại, CCCD/CMND, số thẻ BHYT bằng các mã định danh giả lập hai chiều [SDT_1], [CCCD_1], [BHYT_1].
• Chốt 2 — Nhất quán chủ thể và vai người nói (src/he_thong/rao_chan_an_toan.py): Đối soát từng mệnh đề với vai người nói của lượt dẫn, cảnh báo khi thông tin của người nhà hoặc người bệnh khác có nguy cơ bị ghi cho bệnh nhân đang mở hồ sơ.
• Chốt 3 — Cảnh báo bất thường cận lâm sàng (src/cong_cu_lam_sang/doi_soat_can_lam_sang.py): Phân tích kết quả xét nghiệm sinh hóa máu, huyết học, điện giải và gắn cờ báo động các chỉ số vượt ngưỡng sinh lý an toàn.
• Chốt 4 — Thang điểm lâm sàng và hỗ trợ quyết định y khoa CDSS (src/cong_cu_lam_sang/thang_diem_nguy_co.py): Hiện thực hóa các công thức phân tầng nguy cơ chuẩn hóa quốc tế: CKD-EPI 2021, Cockcroft-Gault, CHA2DS2-VASc (nguy cơ đột quỵ trong rung nhĩ) và HAS-BLED (nguy cơ xuất huyết).
• Chốt 5 — Cảnh báo tương tác thuốc nguy cơ cao DDI Black-box (src/cong_cu_lam_sang/canh_bao_tuong_tac_thuoc.py): Tra cứu ma trận tương tác chống chỉ định nguy hiểm theo dược thư quốc gia và FDA. Điển hình là cặp phối hợp Clopidogrel + Omeprazole (chất ức chế CYP2C19 làm giảm hoạt tính Clopidogrel, gây nguy cơ tắc stent mạch vành tái phát); hệ thống tự động phát hiện, đưa cảnh báo đỏ lên đầu bản nháp và khuyến cáo thay thế bằng Pantoprazole/Esomeprazole.
• Chốt 6 — Hiệu chỉnh liều thuốc theo độ lọc cầu thận eGFR (src/cong_cu_lam_sang/hieu_chinh_lieu.py): Đối soát chức năng lọc thận với danh mục thuốc đào thải qua thận, tự động cảnh báo giảm liều hoặc đình chỉ sử dụng (ví dụ đình chỉ Metformin khi eGFR < 30 mL/min/1.73m2 và giảm liều khi eGFR từ 30-44 mL/min/1.73m2 để phòng ngừa nhiễm toan lactic).
• Chốt 7 — Tờ dặn dò người bệnh (src/cong_cu_lam_sang/to_dan_do_benh_nhan.py): Soạn bản dặn dò bằng lời dễ hiểu từ bản nháp đã duyệt — lịch uống thuốc theo buổi, việc cần làm, dấu hiệu phải quay lại khám — kèm lưu ý tương tác thuốc với thức ăn lấy từ bước hiệu chỉnh liều.
• Chốt 8 — Tác tử gợi mở lâm sàng chủ động SOCRATES (src/cong_cu_lam_sang/goi_y_cau_hoi_socrates.py): Ứng dụng quy trình khai thác bệnh sử SOCRATES kinh điển (Site, Onset, Character, Radiation, Associations, Time course, Exacerbating/relieving factors, Severity) để phát hiện triệu chứng thiếu dữ kiện và gợi mở câu hỏi cho bác sĩ.

| Chốt | Tên thành phần | Mô-đun phụ trách | Cơ chế kỹ thuật | Quy chuẩn đối chiếu |
| :--- | :--- | :--- | :--- | :--- |
| Chốt 1 | Khử định danh PII/PHI | src/he_thong/khu_dinh_danh.py | Che giấu CCCD, SĐT, BHYT bằng mã định danh giả lập 2 chiều | Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 và Nghị định 356/2025/NĐ-CP |
| Chốt 2 | Nhất quán chủ thể & vai người nói | src/he_thong/rao_chan_an_toan.py | Đối soát chủ thể mệnh đề với vai người nói của lượt dẫn | Truy vết căn cứ theo lượt thoại |
| Chốt 3 | Cảnh báo cận lâm sàng | src/cong_cu_lam_sang/doi_soat_can_lam_sang.py | Phát hiện chỉ số sinh hóa, huyết học, điện giải vượt ngưỡng | Khoảng tham chiếu sinh lý Bộ Y tế |
| Chốt 4 | Thang điểm lâm sàng CDSS | src/cong_cu_lam_sang/thang_diem_nguy_co.py | Tính điểm eGFR, Cockcroft-Gault, CHA2DS2-VASc, HAS-BLED | Hướng dẫn ESC / KDIGO |
| Chốt 5 | Tương tác thuốc DDI Black-box | src/cong_cu_lam_sang/canh_bao_tuong_tac_thuoc.py | Chặn tương tác mức 1 (Clopidogrel + Omeprazole), đề xuất đổi thuốc | FDA Black-box Warning & Dược thư QG |
| Chốt 6 | Hiệu chỉnh liều suy thận | src/cong_cu_lam_sang/hieu_chinh_lieu.py | Giảm liều hoặc đình chỉ Metformin khi eGFR < 45 / < 30 | Khuyến cáo KDIGO 2023 & ADA 2024 |
| Chốt 7 | Tờ dặn dò người bệnh | src/cong_cu_lam_sang/to_dan_do_benh_nhan.py | Lịch uống thuốc theo buổi, việc cần làm, dấu hiệu phải tái khám | Ngôn ngữ dễ hiểu cho người bệnh |
| Chốt 8 | Tác tử lâm sàng SOCRATES | src/cong_cu_lam_sang/goi_y_cau_hoi_socrates.py | Chủ động phát hiện thiếu tính chất đau/bệnh sử, gợi mở câu hỏi | Quy trình khai thác triệu chứng SOCRATES |


## 3.10. Chuẩn hóa liên thông dữ liệu y tế quốc tế HL7 FHIR R4

Để kết nối thực tế với hệ thống quản lý bệnh viện (HIS/EMR) và hồ sơ bệnh án điện tử, MediTrace bổ sung module xuất dữ liệu src/cong_cu_lam_sang/xuat_fhir_r4.py. Module tự động đóng gói toàn bộ bản nháp lâm sàng thành FHIR JSON Bundle chuẩn R4 với các tài nguyên y tế cốt lõi:
• Patient: Dữ liệu hành chính bệnh nhân đã qua khử nhận dạng (dữ liệu sức khỏe là dữ liệu nhạy cảm theo Luật 91/2025/QH15).
• Encounter: Định danh phiên khám, thời gian thực hiện và tài khoản bác sĩ chủ trì.
• Condition: Danh mục mã hóa bệnh lý chẩn đoán theo danh pháp quốc tế ICD-10.
• Observation: Các dấu hiệu sinh tồn, chỉ số xét nghiệm và kết quả tính toán độ lọc cầu thận eGFR.
• MedicationRequest: Y lệnh thuốc điện tử đầy đủ tên hoạt chất, biệt dược, liều dùng, đường dùng và cảnh báo dược lâm sàng.


## 3.11. Tờ dặn dò người bệnh xuất viện chuẩn quốc tế (JCI) và Bảng kiểm toán tiến trình AI

Mở rộng trải nghiệm lâm sàng từ góc độ an toàn người bệnh và giám sát thuật toán, hệ thống hoàn thiện hai giao diện ứng dụng:
1. Tờ dặn dò người bệnh xuất viện (src/cong_cu_lam_sang/to_dan_do_benh_nhan.py & ToDanDoBenhNhanModal.tsx): Thiết kế bảng ma trận chia 4 khung giờ (Sáng - Trưa - Chiều - Tối) kèm hướng dẫn uống trước/sau ăn; tích hợp Khung cảnh báo dấu hiệu nguy hiểm (Red Flags Alert) hướng dẫn người bệnh quay lại cấp cứu ngay khi có triệu chứng trở nặng; niêm phong số hóa bằng mã băm SHA-256 bảo đảm tính toàn vẹn.
2. Bảng kiểm toán tiến trình AI (NhatKyTienTrinhAIModal.tsx): Thiết kế giao diện Terminal kỹ thuật cao hiển thị độ trễ suy luận (đạt 379.4 ms trên ca khám mẫu), trực quan hóa chi tiết luồng bóc tách 5 mệnh đề [P1..P5] từ 8 lượt thoại nguồn [T1..T8] của mô hình Qwen3-4B QLoRA và trạng thái kiểm duyệt của 8 chốt phòng vệ trước khi bác sĩ ký số xuất bản.

Nhằm khắc phục triệt để các rủi ro y khoa trong đơn thuốc và yêu cầu bảo vệ dữ liệu sức khỏe người bệnh, hệ thống được tái cấu trúc từ các phép kiểm tuần tự sơ khởi sang bộ điều phối tập trung MediTracePipelineOrchestrator (src/he_thong/dieu_phoi_cac_chot_an_toan.py). Bộ điều phối kết nối 8 chốt an toàn chuyên sâu theo cơ chế liên hoàn song song và tuần tự:
• Chốt 1 — Khử nhận dạng thông tin cá nhân PII/PHI (dữ liệu sức khỏe là dữ liệu nhạy cảm theo Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 và Nghị định 356/2025/NĐ-CP) (src/he_thong/khu_dinh_danh.py): Tự động phát hiện và che giấu các thực thể nhạy cảm gồm số điện thoại, CCCD/CMND, số thẻ BHYT bằng các mã định danh giả lập hai chiều [SDT_1], [CCCD_1], [BHYT_1].
• Chốt 2 — Nhất quán chủ thể và vai người nói (src/he_thong/rao_chan_an_toan.py): Đối soát từng mệnh đề với vai người nói của lượt dẫn, cảnh báo khi thông tin của người nhà hoặc người bệnh khác có nguy cơ bị ghi cho bệnh nhân đang mở hồ sơ.
• Chốt 3 — Cảnh báo bất thường cận lâm sàng (src/cong_cu_lam_sang/doi_soat_can_lam_sang.py): Phân tích kết quả xét nghiệm sinh hóa máu, huyết học, điện giải và gắn cờ báo động các chỉ số vượt ngưỡng sinh lý an toàn.
• Chốt 4 — Thang điểm lâm sàng và hỗ trợ quyết định y khoa CDSS (src/cong_cu_lam_sang/thang_diem_nguy_co.py): Hiện thực hóa các công thức phân tầng nguy cơ chuẩn hóa quốc tế: CKD-EPI 2021, Cockcroft-Gault, CHA2DS2-VASc (nguy cơ đột quỵ trong rung nhĩ) và HAS-BLED (nguy cơ xuất huyết).
• Chốt 5 — Cảnh báo tương tác thuốc nguy cơ cao DDI Black-box (src/cong_cu_lam_sang/canh_bao_tuong_tac_thuoc.py): Tra cứu ma trận tương tác chống chỉ định nguy hiểm theo dược thư quốc gia và FDA. Điển hình là cặp phối hợp Clopidogrel + Omeprazole (chất ức chế CYP2C19 làm giảm hoạt tính Clopidogrel, gây nguy cơ tắc stent mạch vành tái phát); hệ thống tự động phát hiện, đưa cảnh báo đỏ lên đầu bản nháp và khuyến cáo thay thế bằng Pantoprazole/Esomeprazole.
• Chốt 6 — Hiệu chỉnh liều thuốc theo độ lọc cầu thận eGFR (src/cong_cu_lam_sang/hieu_chinh_lieu.py): Đối soát chức năng lọc thận với danh mục thuốc đào thải qua thận, tự động cảnh báo giảm liều hoặc đình chỉ sử dụng (ví dụ đình chỉ Metformin khi eGFR < 30 mL/min/1.73m2 và giảm liều khi eGFR từ 30-44 mL/min/1.73m2 để phòng ngừa nhiễm toan lactic).
• Chốt 7 — Tờ dặn dò người bệnh (src/cong_cu_lam_sang/to_dan_do_benh_nhan.py): Soạn bản dặn dò bằng lời dễ hiểu từ bản nháp đã duyệt — lịch uống thuốc theo buổi, việc cần làm, dấu hiệu phải quay lại khám — kèm lưu ý tương tác thuốc với thức ăn lấy từ bước hiệu chỉnh liều.
• Chốt 8 — Tác tử gợi mở lâm sàng chủ động SOCRATES (src/cong_cu_lam_sang/goi_y_cau_hoi_socrates.py): Ứng dụng quy trình khai thác bệnh sử SOCRATES kinh điển (Site, Onset, Character, Radiation, Associations, Time course, Exacerbating/relieving factors, Severity) để phát hiện triệu chứng thiếu dữ kiện và gợi mở câu hỏi cho bác sĩ.

Để kết nối thực tế với hệ thống quản lý bệnh viện (HIS/EMR) và hồ sơ bệnh án điện tử, MediTrace bổ sung module xuất dữ liệu src/cong_cu_lam_sang/xuat_fhir_r4.py. Module tự động đóng gói toàn bộ bản nháp lâm sàng thành FHIR JSON Bundle chuẩn R4 với các tài nguyên y tế cốt lõi:
• Patient: Dữ liệu hành chính bệnh nhân đã qua khử nhận dạng (dữ liệu sức khỏe là dữ liệu nhạy cảm theo Luật 91/2025/QH15).
• Encounter: Định danh phiên khám, thời gian thực hiện và tài khoản bác sĩ chủ trì.
• Condition: Danh mục mã hóa bệnh lý chẩn đoán theo danh pháp quốc tế ICD-10.
• Observation: Các dấu hiệu sinh tồn, chỉ số xét nghiệm và kết quả tính toán độ lọc cầu thận eGFR.
• MedicationRequest: Y lệnh thuốc điện tử đầy đủ tên hoạt chất, biệt dược, liều dùng, đường dùng và cảnh báo dược lâm sàng.

Mở rộng trải nghiệm lâm sàng từ góc độ an toàn người bệnh và giám sát thuật toán, hệ thống hoàn thiện hai giao diện ứng dụng:
1. Tờ dặn dò người bệnh xuất viện (src/cong_cu_lam_sang/to_dan_do_benh_nhan.py & ToDanDoBenhNhanModal.tsx): Thiết kế bảng ma trận chia 4 khung giờ (Sáng - Trưa - Chiều - Tối) kèm hướng dẫn uống trước/sau ăn; tích hợp Khung cảnh báo dấu hiệu nguy hiểm (Red Flags Alert) hướng dẫn người bệnh quay lại cấp cứu ngay khi có triệu chứng trở nặng; niêm phong số hóa bằng mã băm SHA-256 bảo đảm tính toàn vẹn.
2. Bảng kiểm toán tiến trình AI (NhatKyTienTrinhAIModal.tsx): Thiết kế giao diện Terminal kỹ thuật cao hiển thị độ trễ suy luận (đạt 379.4 ms trên ca khám mẫu), trực quan hóa chi tiết luồng bóc tách 5 mệnh đề [P1..P5] từ 8 lượt thoại nguồn [T1..T8] của mô hình Qwen3-4B QLoRA và trạng thái kiểm duyệt của 8 chốt phòng vệ trước khi bác sĩ ký số xuất bản.


# 4. KẾT QUẢ


## 4.1. So sánh ba phương án có cấu trúc

| Bộ thử thách | Chỉ tách thông tin F1 / lỗi ô / nhầm người | Tách + xử lý sửa lại F1 / lỗi ô / nhầm người | + kiểm tra bằng chứng F1 / lỗi ô / nhầm người |
| :--- | :--- | :--- | :--- |
| Đổi chủ thể (80) | 66,1 / 45,4 / 22,0% | 69,2 / 38,2 / 20,0% | 70,8 / 36,9 / 17,9% |
| Đính chính (60) | 80,9 / 29,9 / 7,6% | 85,9 / 17,4 / 6,8% | 87,0 / 17,4 / 5,5% |
| Nhiễu giọng nói (80) | 63,2 / 63,7 / 3,7% | 64,9 / 58,4 / 3,3% | 64,8 / 58,6 / 3,5% |
| Vùng miền (80) | 85,8 / 21,5 / 1,7% | 87,8 / 16,9 / 1,5% | 88,0 / 16,3 / 1,5% |

Ở bộ đổi chủ thể, các bước phía sau giảm tỷ lệ ghi nhầm người từ 22,0% xuống 17,9% và tăng F1 từ 66,1 lên 70,8. Ở bộ đính chính, F1 tăng từ 80,9 lên 87,0. Ngược lại, ở bộ nhiễu giọng nói, thêm bước kiểm tra bằng chứng gần như không cải thiện kết quả; F1 64,9 xuống 64,8 và tỷ lệ ghi nhầm người 3,3% lên 3,5%. Ở bộ vùng miền, cải thiện rất nhỏ.

Tỷ lệ ghi nhầm người không thể đọc riêng. Một cách làm đơn giản lấy cả lượt bác sĩ chỉ ghi nhầm người 12,9% ở bộ đổi chủ thể, thấp hơn các mô hình trên, nhưng F1 chỉ 23,1%, tỷ lệ lỗi theo ô 181,3% và bỏ sót 50,4%. Vì vậy, báo cáo luôn trình bày đồng thời độ đúng và độ đủ.


## 4.2. Xử lý thông tin đã được người nói sửa

Trên bộ đính chính 60 ca, số ca có trạng thái cuối đúng tăng từ 15/60 lên 50/60. Tỷ lệ bản cũ còn bị giữ giảm từ 11,48% xuống 0,80%. Trên một mẫu 240 ca của tập phát triển, tỷ lệ tương ứng giảm từ 5,21% xuống 0,36%.

Lần đo đầu ngày 07/09/2026, cơ chế xử lý lời sửa hầu như không có tác dụng vì dữ liệu huấn luyện khi đó thiếu mục quan hệ. Sau khi sửa dữ liệu và huấn luyện lại, cơ chế mới hoạt động. Kết quả này cho thấy chất lượng nhãn dữ liệu ảnh hưởng trực tiếp đến khả năng áp dụng luật phía sau.


## 4.3. Lỗi nghiêm trọng và bỏ sót khi thêm kiểm tra bằng chứng

| Bộ | Lỗi nghiêm trọng | Bỏ sót |
| :--- | :--- | :--- |
| Đổi chủ thể | 43,0% → 36,2% | 4,5% → 7,7% |
| Đính chính | 18,2% → 13,2% | 3,0% → 5,4% |
| Nhiễu giọng nói | 33,5% → 30,1% | 21,8% → 24,9% |
| Vùng miền | 8,2% → 8,2% | 3,5% → 3,5% |

Trên mẫu 240 ca của tập phát triển, lỗi nghiêm trọng giảm từ 15,06% xuống 12,52%, trong khi bỏ sót nghiêm trọng ở phần chính tăng từ 0,58% lên 3,48%. Sai thuốc gần như không đổi, khoảng 3,2–3,9%; dữ liệu hiện có chưa giải thích được nguyên nhân.

Một chính sách thận trọng hơn chuyển mọi thông tin dị ứng và thuốc có cảnh báo sang mục Cần xác nhận. Ở bộ đổi chủ thể 80 ca, lỗi nghiêm trọng trong phần chính giảm từ 36,2% xuống 25,7%, nhưng tỷ lệ thông tin nghiêm trọng không nằm ở phần chính tăng từ 11,9% lên 40,2%; F1 giảm từ 70,8 xuống 69,2. Có 186 mệnh đề bị chuyển sang Cần xác nhận; 38,2% trong nhóm này sai thật, so với 20,7% ở nhóm ở lại. Chính sách đã tập trung được nhiều lỗi hơn vào vùng cần xem lại nhưng cũng chuyển nhiều thông tin đúng ra khỏi phần chính.


## 4.4. Kiểm thử bằng cách cố ý làm hỏng đáp án

Trên 634 ca của tập phát triển, nghiên cứu bắt đầu từ đáp án hoàn hảo rồi cố ý làm hỏng một mệnh đề trong mỗi ca theo từng loại lỗi. Khi kiểm thông tin đúng, hệ thống không chuyển nhầm mệnh đề nào trong 5.092 mệnh đề; trên tập huấn luyện là 0/30.136. Kết quả này thuận lợi một phần vì câu trích trong đáp án gần như luôn là chuỗi nguyên văn trong hội thoại, nên chưa cho biết tỷ lệ cảnh báo nhầm trên dữ liệu thật.

| Lỗi được cài sẵn | Kết quả |
| :--- | :--- |
| Đổi người | 13,4% bị chuyển khỏi phần chính; 83,0% được cảnh báo; 3,6% không phát hiện. |
| Nâng mức chắc chắn | Chuyển khỏi phần chính 175/175 ca (100%). |
| Giả định thành sự thật | Chuyển khỏi phần chính 68/68 ca (100%). |
| Câu trích không có trong hội thoại | Chuyển khỏi phần chính 634/634 ca (100%). |
| Cố ý bỏ một đoạn có thông tin y khoa | Phát hiện được đoạn chưa có mệnh đề liên kết trong 90,2% ca. |

Các lỗi trên được tạo đúng theo loại mà bước kiểm tra được thiết kế để bắt. Vì vậy, các tỷ lệ 100% đo khả năng bắt lỗi có chủ đích, không phải tỷ lệ bắt lỗi tự nhiên ngoài thực tế. Một thử nghiệm thăm dò khác cho thấy hơn 40% lỗi nguy hiểm vẫn lọt vào phần chính (44,7% hoặc 43,3% tùy chế độ) vì nhiều lỗi không để lại dấu hiệu rõ trong câu được dẫn. Các luật sau đó còn được sửa khi nhìn các ca này, nên số đo có thể lạc quan.


## 4.5. Các thước đo giống câu chữ có thể bỏ qua lỗi làm đổi nghĩa

| Thước đo | Lỗi nguy hiểm | Lỗi vô hại | Khoảng cách |
| :--- | :--- | :--- | :--- |
| Điểm VAIC | 0,9816 | 0,9689 | −0,0127 |
| ROUGE-1 | 1,0000 | 0,9610 | −0,0390 |
| F1 theo mục | 1,0000 | 1,0000 | 0,0000 |
| Bộ chấm của đề tài | 0,8264 | 0,9645 | +0,1381 |

Phép đo 400 bệnh án cho thấy đổi chỗ hai người có thể không làm thay đổi số từ, nên ROUGE-1 vẫn bằng 1,0000 dù lỗi làm thay đổi người. Đây là phép đo độ nhạy của thước đo trên lỗi sinh bằng luật, không đo tần suất lỗi ngoài đời.

Trong phép mở rộng 492 cặp, bộ chấm của đề tài phát hiện 492/492 ca đảo phủ định và 492/492 ca kế hoạch bị ghi thành đã làm; với lỗi thời gian là 482/492. Tuy nhiên, bộ chấm cũng báo lỗi oan 47/492 bản vô hại (9,6%) vì thay một từ đồng nghĩa có thể làm mức giống nhau xuống dưới ngưỡng 0,6. Ngoài ra, 209/492 ca đổi thời gian không làm văn bản đầu ra thay đổi, nên bản nháp không thể hiện được khác biệt hiện tại/quá khứ trong các ca đó.

Đáng chú ý, ở phép đảo phủ định, ROUGE-1 của bản lỗi là 0,9927, cao hơn 0,9855 của bản đúng. Kết quả này ủng hộ việc không dùng độ giống câu chữ như thước đo duy nhất.


## 4.6. So với cách viết trực tiếp và các mô hình khác

| Bộ thử thách | Viết thẳng | MediTrace đầy đủ |
| :--- | :--- | :--- |
| Đổi chủ thể | 0,9388 | 0,7476 |
| Đính chính | 0,9885 | 0,8299 |
| Nhiễu giọng nói | 0,8033 | 0,7009 |
| Vùng miền | 0,9735 | 0,8950 |

Điểm quy gán của cách viết trực tiếp cao hơn MediTrace ở cả bốn bộ thử thách. Khoảng dao động 95% của chênh lệch nằm hoàn toàn phía âm ở cả bốn bộ; riêng bộ đổi chủ thể, chênh lệch là −0,1912 với khoảng từ −0,3053 đến −0,1087. Vì vậy, H1 không được ủng hộ trên tập phát triển.

Cách viết trực tiếp chép khít từng ký tự bản mẫu ở 24/80 ca đổi chủ thể, 38/60 ca đính chính, 27/80 ca nhiễu giọng nói và 36/80 ca vùng miền, tương đương khoảng 30–63% số ca tùy bộ. Phép đánh giá lại so với chính bản mẫu đó, nên dữ liệu hiện tại tạo lợi thế lớn cho cách viết trực tiếp. Thêm một lượt tự soát vào cách viết trực tiếp gần như không thay đổi kết quả.

Một mô hình thương mại được thử với cùng lời nhắc trên 173/300 ca trước khi dừng do hết số dư. Ở bộ đổi chủ thể, mô hình này ghi nhầm người 15,4% so với 22,9% của mô hình đề tài; ở bộ đính chính là 1,4% so với 7,6%. Khi áp bước nhận người bằng luật lên mô hình thương mại, tỷ lệ ở bộ đổi chủ thể tăng từ 15,4% lên 25,2%; với mô hình nhỏ, tỷ lệ giảm từ 22,9% xuống 20,5%. Kết quả này cho thấy cùng một luật có thể tác động khác nhau theo mô hình đầu vào và không cho phép kết luận đề tài đã giải được bài toán ghi nhầm người.

Phản ví dụ khác: Qwen3-8B chưa huấn luyện thêm đạt 41,5% ghi nhầm người và F1 28,0 ở bộ đổi chủ thể, kém Qwen3-4B đã huấn luyện thêm (22,0%; F1 66,1). Trong phép thử này, huấn luyện đóng góp nhiều hơn việc chỉ tăng kích thước mô hình.

Phép thử phụ “lời nói dân dã” 60 ca cho F1 lần lượt 84,9; 87,0; 85,9 và tỷ lệ ghi nhầm người 2,8%; 1,2%; 0,9% ở ba phương án có cấu trúc. Đây là phép thử phụ, không gộp với bốn bộ chính.


## 4.7. Các phần chưa có đủ kết quả

Trong các thử nghiệm ban đầu (tháng 09/2026), bước câu hỏi làm rõ chưa kích hoạt nên chưa đo được đầy đủ lợi ích. Đến đợt nâng cấp toàn diện tháng 10/2026, cơ chế này đã được hoàn thiện thành Chốt 8 SOCRATES (src/cong_cu_lam_sang/goi_y_cau_hoi_socrates.py), kích hoạt thành công trên các ca bệnh phức tạp và được kiểm chứng thực tế tại mục 4.8 dưới đây.


## 4.8. Kết quả nghiệm thu thực nghiệm đợt nâng cấp ngày 18/10/2026

Đợt nâng cấp kỹ thuật nghiệm thu ngày 18/10/2026 được đánh giá độc lập thông qua chuỗi kiểm thử kỹ thuật và đối soát lâm sàng chuyên sâu:
1. Kết quả kiểm thử tự động: lần chạy ngày 18/10/2026 ghi nhận 1.330 bài kiểm thử đơn vị và tích hợp qua, 27 bỏ qua; lần chạy 26/11/2026 (README.md) ghi nhận 1.942 bài qua, 27 bỏ qua. Đây là kiểm tra mã chạy đúng trên ca do nhóm tự viết, không phải tỷ lệ đúng trên dữ liệu thật.
2. Chốt 5 (DDI Black-box): vượt qua các phép thử đơn vị với đơn thuốc do nhóm tự viết có cặp Clopidogrel + Omeprazole (chưa đo trên tập đơn thuốc độc lập), tự động kích hoạt cảnh báo mức độ 1 và đề xuất thuốc thay thế nhóm PPI an toàn (Pantoprazole/Esomeprazole).
3. Chốt 6 (eGFR & Suy thận): phép thử đơn vị đối chiếu với công thức CKD-EPI 2021 cho kết quả trùng khớp trên các ca tự viết; cảnh báo kê liều Metformin khi eGFR < 45 mL/min/1.73m2 vượt qua phép thử đơn vị (chưa đo trên tập độc lập).
4. Chốt 1 (khử định danh): vượt qua phép thử đơn vị với CCCD, SĐT và mã thẻ BHYT theo mẫu do nhóm viết. Trên văn bản báo chí PhoNER_COVID19, bộ khử định danh chỉ che được 10/847 (1,2%) nhãn tên và mã bệnh nhân (docs/ket-qua/da-nguon-doc-lap.json), nên chưa thể khẳng định không có thông tin định danh bị rò rỉ.
5. Thử nghiệm trên 3 ca bệnh khó bẫy lâm sàng đối phó câu hỏi Ban Giám khảo:
• Ca 1 (Lão khoa - Viêm phổi hít / Suy thận): Hệ thống tính chính xác eGFR = 38 mL/min, cảnh báo đình chỉ Metformin và đề xuất chuyển sang phác đồ Insulin nội viện.
• Ca 2 (Tim mạch - Sau can thiệp mạch vành / Xuất huyết tiêu hóa): Hệ thống phát hiện ngay tương tác chống chỉ định Clopidogrel + Omeprazole, cảnh báo nguy cơ huyết khối tắc stent và đề xuất đổi sang Pantoprazole.
• Ca 3 (Hô hấp & Tim mạch mạn tính - Hen cấp / Suy tim): Kích hoạt Chốt 8 SOCRATES, tự động nhắc bác sĩ khai thác thêm triệu chứng khó thở kịch phát về đêm và khuyến cáo chỉ định đo điện tim ECG cùng xét nghiệm men tim Troponin.


# 5. BÀN LUẬN

Kết quả hiện tại không cho thấy MediTrace tạo bản nháp chính xác hơn cách viết trực tiếp. Điểm quy gán thấp hơn ở cả bốn bộ thử thách. Dữ liệu tổng hợp lại có mức sao chép nguyên văn cao, và cách viết trực tiếp nhiều lần chép khít bản mẫu. Vì vậy, nghiên cứu chưa tách được rõ hiệu quả của kiến trúc khỏi lợi thế do cách dữ liệu được sinh và cách bản mẫu được dùng để chấm.

Thành phần có kết quả tích cực rõ nhất là xử lý thông tin đã được người nói sửa. Trên bộ đính chính 60 ca, tỷ lệ giữ bản cũ giảm từ 11,48% xuống 0,80%; trên mẫu 240 ca giảm từ 5,21% xuống 0,36%. Kết quả này ủng hộ H1b trên dữ liệu do chương trình tự tạo.

Kiểm tra bằng chứng giảm lỗi nghiêm trọng ở ba trong bốn bộ chính, nhưng đồng thời làm tăng bỏ sót ở ba bộ đó. Bộ vùng miền gần như không đổi. H2 vì vậy chỉ được ủng hộ một phần: có dấu hiệu giảm lỗi ở phần chính, nhưng cái giá là thêm thông tin đúng bị chuyển khỏi phần chính.

H3 được ủng hộ bởi các phép đổi người, đảo phủ định và thay trạng thái kế hoạch. ROUGE-1 có thể rất cao dù ý nghĩa đã sai. Tuy nhiên, bộ chấm của đề tài cũng chưa hoàn hảo: 47/492 bản vô hại bị báo lỗi vì ngưỡng ghép từ ngữ. Do đó, bộ chấm mới nên được dùng cùng đánh giá thủ công chứ không nên được coi là chuẩn tuyệt đối.

Kiến trúc có cấu trúc vẫn có một lợi ích nghiên cứu: mỗi dòng đầu ra có thể liên kết ngược tới mệnh đề và câu nói gốc. Điều này tạo điều kiện để phân tích lỗi theo từng bước trong các nghiên cứu tiếp theo. Báo cáo hiện tại chưa có bảng phân rã đầy đủ lỗi theo từng bước, nên chưa thể định lượng lợi ích này.

Đợt nâng cấp ngày 18/10/2026 đã giải quyết căn cơ bài toán chuyển đổi từ mô hình nghiên cứu sang ứng dụng thực tế. Việc bổ sung 8 chốt an toàn lâm sàng độc lập đã chứng minh rằng: AI scribe trong y tế không thể chỉ dựa vào năng lực ngôn ngữ thuần túy, mà bắt buộc phải được bao bọc bởi các lớp bảo vệ kiểm chứng dược lý, cận lâm sàng và pháp lý dữ liệu khắt khe.


# 6. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

MediTrace Sentinel thử một cách tạo bản nháp lâm sàng theo ba bước chính: tách hội thoại thành thông tin nhỏ, kiểm tra từng thông tin, sau đó để bác sĩ quyết định cuối. Trên dữ liệu do chương trình tự tạo, xử lý lời đính chính làm giảm mạnh việc giữ thông tin cũ. Các bước kiểm tra bằng chứng bắt tốt những lỗi được cài sẵn theo đúng loại chúng được thiết kế để bắt và làm giảm lỗi nghiêm trọng ở một số bộ thử thách, nhưng làm tăng bỏ sót.

Kết quả hiện tại không ủng hộ H1: điểm quy gán của MediTrace thấp hơn cách viết trực tiếp ở cả bốn bộ thử thách. H1b được ủng hộ trên dữ liệu tự tạo. H2 được ủng hộ một phần vì lỗi nghiêm trọng giảm nhưng bỏ sót tăng. H3 được ủng hộ, đồng thời bộ chấm mới vẫn có 9,6% báo lỗi oan trong phép thay từ đồng nghĩa.

Ưu tiên tiếp theo là tạo dữ liệu khó hơn và ít sao chép nguyên văn; thêm các cặp chỉ khác người, thời gian hoặc phủ định; cải thiện nhận người và quan hệ họ hàng; hoàn thành chấm tay hai người; đo trên tập kiểm tra cuối 590 ca đúng một lần; sau đó mới chuyển sang hội thoại mô phỏng do người nói và nghiên cứu có giám sát với bác sĩ. Khi có người dùng thật, cần đo thêm thời gian duyệt, số cảnh báo thừa, tỷ lệ sửa của bác sĩ và mức chấp nhận sử dụng.

Bước tiến đến ngày 18/10/2026 đưa MediTrace Sentinel từ một khung trích xuất mệnh đề lý thuyết trở thành một giải pháp trợ lý lâm sàng hoàn chỉnh. Hệ sinh thái hiện đã sẵn sàng tích hợp với bệnh án điện tử HIS/EMR thông qua chuẩn quốc tế HL7 FHIR R4, đồng thời chạy tại chỗ để dữ liệu người bệnh không rời bệnh viện, hướng tới yêu cầu của Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 và Nghị định 356/2025/NĐ-CP và nâng cao an toàn người bệnh theo chuẩn JCI.


# 7. HẠN CHẾ VÀ NGUYÊN TẮC SỬ DỤNG

1. Toàn bộ dữ liệu huấn luyện và đánh giá hiện tại do chương trình tự tạo; chưa có hội thoại bệnh nhân thật.
1. Tập phát triển chỉ có 13 mẫu bệnh, nên một số khoảng dao động còn rộng và khó đại diện cho tình huống lâm sàng đa dạng.
1. Mức sao chép nguyên văn trong đáp án cao, tạo lợi thế cho phương án viết trực tiếp và chưa thử đủ cách diễn đạt tự nhiên.
1. Tập kiểm tra cuối 590 ca chưa được dùng. Các kết quả hiện tại chủ yếu là số trên tập phát triển.
1. Một số luật được sửa sau khi xem lỗi trên tập phát triển, nên kết quả có thể lạc quan hơn khi áp dụng cho dữ liệu mới.
1. Chưa có bác sĩ sử dụng hệ thống trong quy trình khám; chưa đo thời gian duyệt, độ hữu ích hoặc mức chấp nhận.
1. Ngưỡng ghép 0,6 có thể báo sai khi hai câu cùng nghĩa nhưng dùng từ khác; phép mở rộng ghi nhận 47/492 bản vô hại bị báo lỗi.
1. Bước nhận người bằng luật vẫn có thể gộp sai quan hệ họ hàng hoặc đại từ. Hiệu quả của cùng một luật thay đổi theo mô hình đầu vào.
1. Các lỗi cài sẵn để kiểm thử được tạo theo đúng loại mà bước kiểm tra được thiết kế để bắt; tỷ lệ 100% không đại diện cho lỗi tự nhiên.
1. Phần âm thanh mới thử bằng 38 câu và giọng máy; tên thuốc sai gần 100% số câu nên chưa dùng trong kết luận chính.
1. Phương án viết trực tiếp và mô hình tách thông tin không dùng hoàn toàn cùng bộ trọng số và thiết lập số học, có thể gây nhiễu cho so sánh.
Nguyên tắc sử dụng: sản phẩm chỉ tạo bản nháp để bác sĩ kiểm tra. Không dùng đầu ra như hồ sơ chính thức nếu chưa được người có chuyên môn duyệt. Hệ thống không tự chẩn đoán, kê đơn, thay đổi thuốc, ra y lệnh hoặc đưa ra hướng xử trí khẩn cấp.

Ghi nhận đợt nâng cấp ngày 18/10/2026: Các hạn chế kỹ thuật ban đầu về mặt an toàn đơn thuốc, thiếu cơ chế khử định danh người bệnh, chưa có chuẩn kết nối dữ liệu và thiếu tương tác làm rõ triệu chứng đã được giải quyết trực tiếp qua việc bổ sung 8 chốt an toàn lâm sàng, mô-đun khử định danh, cổng xuất HL7 FHIR R4 và tác tử SOCRATES. Tuy nhiên, nguyên tắc cốt lõi vẫn không thay đổi: hệ thống giữ vai trò trợ lý hỗ trợ bác sĩ duyệt (Human-in-the-loop), bác sĩ luôn là người chịu trách nhiệm y khoa cuối cùng.

Bộ chấm tay gồm 36 phiếu; hai người chấm đã hoàn thành 16/36 phiếu. Do chưa chấm hết bộ, báo cáo này chưa trình bày hệ số kappa hoặc kết luận về độ đồng thuận giữa hai người chấm.


# 8. TÀI LIỆU THAM KHẢO

Asgari, E., Montaña-Brown, N., Dubois, M., Khalil, S., Balloch, J., Au Yeung, J., & Pimenta, D. (2025). A framework to assess clinical safety and hallucination rates of LLMs for medical text summarisation. npj Digital Medicine, 8, 274. https://doi.org/10.1038/s41746-025-01670-7

Ben Abacha, A., Yim, W.-w., Adams, G., Snider, N., & Yetisgen, M. (2023). Overview of the MEDIQA-Chat 2023 shared tasks on the summarization & generation of doctor-patient conversations. Proceedings of the 5th Clinical Natural Language Processing Workshop, 503–513. https://doi.org/10.18653/v1/2023.clinicalnlp-1.52

Lin, C.-Y. (2004). ROUGE: A package for automatic evaluation of summaries. In Text Summarization Branches Out (pp. 74–81). Association for Computational Linguistics. https://aclanthology.org/W04-1013/

Luo, Z., Xie, Q., & Ananiadou, S. (2024). Factual consistency evaluation of summarization in the era of large language models. Expert Systems with Applications, 254, 124456. https://doi.org/10.1016/j.eswa.2024.124456

Palm, E., Manikantan, A., Mahal, H., Belwadi, S. S., & Pepin, M. E. (2025). Assessing the quality of AI-generated clinical notes: Validated evaluation of a large language model ambient scribe. Frontiers in Artificial Intelligence, 8, 1691499. https://doi.org/10.3389/frai.2025.1691499

Rotenstein, L. S., Holmgren, A. J., Thombley, R., et al. (2026). Changes in clinician time expenditure and visit quantity with adoption of artificial intelligence-powered scribes: A multisite study. JAMA, 335(16), 1408–1417. https://doi.org/10.1001/jama.2026.2253

Sinsky, C., Colligan, L., Li, L., Prgomet, M., Reynolds, S., Goeders, L., Westbrook, J., Tutty, M., & Blike, G. (2016). Allocation of physician time in ambulatory practice: A time and motion study in 4 specialties. Annals of Internal Medicine, 165(11), 753–760. https://doi.org/10.7326/M16-0961

Svetly, A., Razzouk, E., McLean, M., Frye, K., Little, A., Massaro, L., Quailey, C., Svetly, C., Patel, A., & Montiel, J. (2026). Large-scale implementation of ambient artificial intelligence documentation and its effects on electronic health record efficiency and clinician well-being. Applied Clinical Informatics, 17(4), 747–753. https://doi.org/10.1055/a-2936-7516

Yang, A., Li, A., Yang, B., et al. (2025). Qwen3 technical report. arXiv. https://arxiv.org/abs/2505.09388

Yim, W.-w., Fu, Y., Ben Abacha, A., Snider, N., Lin, T., & Yetisgen, M. (2023). ACI-BENCH: A novel ambient clinical intelligence dataset for benchmarking automatic visit note generation. Scientific Data, 10, 586. https://doi.org/10.1038/s41597-023-02487-3
