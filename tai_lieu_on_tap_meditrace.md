# Bộ câu hỏi và trả lời kỹ thuật MediTrace Sentinel

Tài liệu luyện bảo vệ dự án dành cho thành viên thuyết trình. Nội dung tổng hợp từ mã nguồn và tài liệu dự án được đọc ngày 28/11/2026. Các đoạn “Trả lời gợi ý” có thể điều chỉnh theo cách nói của bạn. Số liệu luôn đi cùng tập đo và điều kiện; các phiên bản dữ liệu, mô hình và tài liệu không được gộp thành một phép thử.

## Cách sử dụng trước buổi bảo vệ

Học chắc câu 1–12, các câu về tính năng thực tế và câu phản biện cuối. Khi trả lời, đi theo bốn ý: vấn đề, cách xử lý, bằng chứng, giới hạn. Không nói đã triển khai lâm sàng, tiết kiệm thời gian, loại bỏ mọi lỗi hoặc bảo vệ dữ liệu tuyệt đối nếu chưa có phép đo tương ứng. Các tính năng liên quan tri thức thuốc, ICD và gợi ý lâm sàng là công cụ hỗ trợ đối chiếu; dữ liệu tri thức được README ghi chưa được chuyên gia duyệt.

## I. Tổng quan và kiến trúc

### 1. MediTrace là gì và giải quyết vấn đề nào?
Trả lời gợi ý: MediTrace Sentinel hỗ trợ tạo bản nháp ghi chép lâm sàng từ hội thoại khám bệnh tiếng Việt. Nhóm quan tâm đến những lỗi đổi nghĩa nhưng câu văn vẫn trôi chảy: gán triệu chứng của người nhà cho bệnh nhân, giữ lại lời đã đính chính, biến kế hoạch thành việc đã làm hoặc thêm liều thuốc không có trong lời nói. Hệ thống đề xuất từng thông tin và liên kết với lượt hội thoại để bác sĩ kiểm tra. Sản phẩm chưa phải bệnh án chính thức, không thay bác sĩ chẩn đoán hoặc kê đơn.

### 2. Trình bày toàn bộ luồng xử lý?
Trả lời gợi ý: Nếu đầu vào là âm thanh, PhoWhisper chuyển âm thanh thành chữ; tùy cấu hình có thể tách các giọng và để người dùng gán vai. Hội thoại được chia theo lượt. Qwen3-4B đề xuất các mệnh đề có cấu trúc; các bước sau dùng luật để gom người, xử lý đính chính và mâu thuẫn, kiểm căn cứ, phân loại rủi ro. Hệ thống ghép bản nháp theo mẫu và đưa các mục không chắc vào “Cần xác nhận”. Bác sĩ xem câu gốc, nghe lại khi có âm thanh và quyết định giữ, sửa hoặc bỏ.

### 3. Điều gì do AI làm và điều gì do luật làm?
Trả lời gợi ý: Trong luồng từ văn bản tới bản nháp, AI chủ yếu đề xuất mệnh đề; những bước gom chủ thể, cập nhật trạng thái, kiểm căn cứ, xếp chỗ và nhiều cảnh báo dùng quy tắc có thể đọc trong mã. Nếu tính đầu vào âm thanh thì PhoWhisper cũng là mô hình AI và pyannote có thể được dùng để tách giọng. Một số tính năng phụ có thể gọi mô hình ngoài khi được bật. Cách chia này giúp truy nguyên lỗi tốt hơn nhưng không bảo đảm tìm được nguyên nhân trong mọi tình huống.

### 4. Điểm mới và đóng góp của nhóm là gì?
Trả lời gợi ý: Nhóm không tuyên bố tự tạo Qwen hay PhoWhisper. Đóng góp nằm ở việc thiết kế bài toán và kết hợp mô hình có sẵn với bộ dữ liệu mô phỏng, adapter, quy trình biểu diễn mệnh đề, quy tắc xử lý tiếng Việt, kiểm căn cứ, cảnh báo và giao diện duyệt. Sự khác biệt cần được chứng minh theo từng tiêu chí; dự án chưa chứng minh chính xác hơn mọi cách viết trực tiếp. Khi hỏi về quyền tác giả mã, nhóm đối chiếu bảng kê khai và phân biệt mã tự viết, có AI hỗ trợ và thư viện bên ngoài.

### 5. Vì sao không để một mô hình viết thẳng toàn bộ hồ sơ?
Trả lời gợi ý: Viết thẳng có thể cho văn bản tự nhiên và trong một số phép thử của nhóm còn đạt điểm gán chủ thể cao hơn. Tuy nhiên, một đoạn văn trôi chảy không tự cho thấy từng câu dựa vào lượt nào và việc đối chiếu sai người hay lời đính chính khó hơn. MediTrace chọn biểu diễn từng thông tin để dễ truy vết và xem xét. Đổi lại, hệ thống có nhiều bước, có thể bỏ sót ngay khi tách và không tự động chính xác hơn.

### 6. Mệnh đề là gì? Cho ví dụ cụ thể.
Trả lời gợi ý: Mệnh đề là một đơn vị thông tin để xử lý và kiểm tra. Với câu “Tôi ho một tuần… à không, mười ngày rồi”, hệ thống cần nhận nội dung ho, chủ thể bệnh nhân, người nói, thời gian, quan hệ đính chính, trạng thái của giá trị cũ và lượt nói làm căn cứ. Trường phủ định, mức chắc chắn và tình huống cũng quan trọng ở những câu khác. Một câu có thể cần nhiều mệnh đề; tách không đúng vẫn gây mất hoặc sai ý.

### 7. Người nói và chủ thể khác nhau như thế nào?
Trả lời gợi ý: Người nói là người phát ngôn; chủ thể là người mà thông tin đề cập. Người con nói “Bố em bị hen” thì con là người nói, bố là chủ thể. Hai trường được lưu riêng và được kiểm tra bằng các quy tắc, nhưng đại từ tiếng Việt như “con”, “cháu”, “em” phụ thuộc quan hệ và ngữ cảnh. Khi không đủ chắc, cần để bác sĩ xác nhận; không khẳng định thuật toán giải quyết triệt để đồng tham chiếu.

### 8. Phân biệt đính chính, diễn biến và mâu thuẫn?
Trả lời gợi ý: “Một tuần, à không, mười ngày” là một giá trị được người nói sửa lại; giá trị cũ nên được đánh dấu thay thế và vẫn giữ dấu vết. “Hôm qua đau, hôm nay hết” là hai trạng thái ở hai thời điểm nên có thể giữ cả hai. Hai người cung cấp hai thông tin trái nhau chưa chắc là đính chính; cần lưu nguồn và đưa ra xác nhận. Dấu hiệu ngôn ngữ và luật giúp phân biệt nhưng có thể nhầm khi ngữ cảnh phức tạp.

### 9. Tại sao phải giữ dấu vết thông tin cũ?
Trả lời gợi ý: Giữ trạng thái cũ giúp bác sĩ xem hệ thống đã hiểu đúng lời sửa hay chưa và kiểm tra lịch sử biến đổi. Thông tin đã thay thế không nên xuất hiện như giá trị đang có hiệu lực trong phần chính. Lưu vết không đồng nghĩa toàn bộ lịch sử đã được bảo vệ khỏi mọi sửa đổi; bảo vệ nhật ký là bài toán riêng.

### 10. Bảy phép kiểm căn cứ gồm những gì?
Trả lời gợi ý: Theo README, các phép kiểm xem câu trích có trong lượt dẫn, nội dung có phù hợp, chủ thể có khớp, mức chắc chắn có bị nâng lên, thời gian và liều có căn cứ, và thông tin có bị cập nhật hoặc thay thế. Một số tài liệu gom cách trình bày thành sáu nhóm; đây là khác biệt phân nhóm, cần đối chiếu đúng phiên bản khi trình bày. Các phép kiểm có giới hạn: câu trích có thật chưa đủ bảo đảm diễn giải đúng; một số điều kiện chỉ cảnh báo, không chặn mọi lỗi.

### 11. Vì sao dùng mẫu câu cố định để tạo bản nháp?
Trả lời gợi ý: Mẫu câu giảm nhu cầu cho một mô hình sinh tự viết lại toàn bộ và làm quan hệ giữa mệnh đề với bản nháp dễ kiểm tra. Tuy nhiên, nó có thể tạo câu kém tự nhiên hoặc diễn đạt thiếu linh hoạt. Quan trọng hơn, nếu mệnh đề ban đầu sai hoặc thiếu thì mẫu câu không tự sửa được nội dung đó.

### 12. Hệ thống chặn hoàn tất như thế nào và có ý nghĩa gì?
Trả lời gợi ý: Theo README, hệ thống chặn ký duyệt hoàn tất khi chưa có mệnh đề có căn cứ hoặc còn mục “Cần xác nhận” chưa xử lý. Bác sĩ phải xác nhận, sửa hoặc bỏ các mục tương ứng. Đây là chốt chặn quy trình đối với rủi ro đã được hệ thống nêu ra; nó không chứng minh rằng hệ thống đã phát hiện mọi thông tin bị bỏ sót.

## II. Mô hình ngôn ngữ và huấn luyện

### 13. Vì sao chọn Qwen3-4B?
Trả lời gợi ý: Nhóm chọn mô hình cỡ 4B theo mục tiêu chạy tại chỗ với tài nguyên vừa phải. So với dùng mô hình lớn qua mạng, cách này hỗ trợ kiểm soát nơi xử lý, song mô hình nhỏ vẫn có thể bỏ sót, nhầm chủ thể và xử lý chậm. Đây là lựa chọn kỹ thuật theo điều kiện dự án, không phải bằng chứng mô hình này tốt nhất. Muốn kết luận phải so sánh các mô hình theo cùng tập và cấu hình.

### 14. Adapter và tinh chỉnh là gì?
Trả lời gợi ý: Mô hình nền đã được huấn luyện trước trên lượng dữ liệu lớn. Adapter là các tham số bổ sung được huấn luyện để mô hình thích ứng với nhiệm vụ và định dạng của MediTrace, thay vì cập nhật toàn bộ tham số nền. Cách này giảm tài nguyên huấn luyện nhưng vẫn phụ thuộc dữ liệu, cấu hình và đánh giá. Nếu BGK hỏi số tham số, hạng LoRA, learning rate hay số epoch, cần mở cấu hình của đúng lần chạy; không đoán.

### 15. Tinh chỉnh giúp được bao nhiêu?
Trả lời gợi ý: Trên 30 ca phát triển với 304 mệnh đề, bộ chấm tự động của dự án ghi tỷ lệ bỏ sót 43,1% với Qwen3-4B chưa tinh chỉnh và 11,5% với adapter trong một phép đo. Đây là chênh lệch 31,6 điểm phần trăm trên mẫu và điều kiện cụ thể, không phải cải thiện đã chứng minh trên bệnh nhân thật. Khoảng tin cậy trong README lần lượt khoảng 37,6–48,7% và 8,4–15,6%. Tập nhỏ, nhãn mô phỏng và cách chấm tự động đều giới hạn kết luận.

### 16. Phiên bản adapter mới hơn có luôn tốt hơn?
Trả lời gợi ý: Không. Lần đo 26/11 trên cùng dạng phép thử được README ghi v1 bỏ sót 11,8%, v3 14,1%; khoảng tin cậy chồng lấp và mẫu nhỏ. Không nên gọi v3 tốt hơn chỉ vì tên phiên bản mới. Chọn mô hình phải dựa vào nhiều chỉ số, nhóm lỗi, tính ổn định và đúng cấu hình sẽ triển khai.

### 17. Mô hình có thể bịa JSON hay thiếu trường không?
Trả lời gợi ý: Có thể. Định dạng có cấu trúc giúp kiểm tra nhưng không buộc mọi đầu ra của mô hình đều đúng. Hệ thống cần kiểm tra khả năng đọc và các trường trước khi xử lý tiếp, báo lỗi hoặc đưa tình huống không rõ để người dùng xử lý. Nhóm chỉ nên mô tả cơ chế phục hồi đã thực sự kiểm thử; tỷ lệ 0 ca JSON lỗi trong một phép thử nhỏ không có nghĩa sẽ không bao giờ gặp lỗi.

### 18. Tại sao không dùng LLM lớn hơn hoặc chỉ cải thiện prompt?
Trả lời gợi ý: Mô hình lớn hoặc prompt tốt hơn là phương án đáng so sánh. Lựa chọn phụ thuộc chi phí, phần cứng, độ trễ, quyền riêng tư và chất lượng. Tinh chỉnh mô hình nhỏ hướng tới cấu hình có thể chạy tại chỗ; nó không tự chứng minh vượt hơn các lựa chọn khác. Cần so sánh cùng tập kiểm tra và đo cả độ đầy đủ, sai chủ thể và tốc độ.

## III. Âm thanh và truy vết

### 19. PhoWhisper và pyannote làm gì?
Trả lời gợi ý: PhoWhisper chuyển tiếng nói thành văn bản. Pyannote khi được bật hỗ trợ phân đoạn theo người nói, tức nhóm những đoạn có thể cùng giọng; nó không tự biết chắc ai là bác sĩ hay bệnh nhân. Người dùng gán vai cho từng nhãn giọng. Lỗi ở cả hai bước có thể truyền sang bản nháp.

### 20. Nếu hai người nói cùng lúc hoặc phòng khám ồn?
Trả lời gợi ý: Tín hiệu chồng lấn, tiếng ồn, khoảng cách micro, giọng địa phương hay tiếng nói nhỏ có thể khiến mất từ, nhận sai từ và tách nhầm giọng. Đặc biệt, mất từ “không”, nhầm tên thuốc hoặc con số có thể đổi nghĩa. Nhóm cần đo theo môi trường và nhóm người nói, cung cấp khả năng nghe lại và không xem bản chép là nguồn đúng tuyệt đối.

### 21. WER là gì? Vì sao không đủ để đánh giá an toàn?
Trả lời gợi ý: WER là tỷ lệ lỗi từ so với bản chép tham chiếu, tính theo số từ thay thế, xóa và thêm chia cho số từ tham chiếu. Ví dụ thay sai một từ trong mười từ tạo WER 10% nếu không có lỗi khác. Nhưng WER không tự thể hiện mức độ nguy hiểm: sai “không”, liều hoặc tên thuốc có thể quan trọng hơn sai từ đệm. Cần thêm chỉ số cho phủ định, tên thuốc, số và ảnh hưởng đến bản nháp.

### 22. Các kết quả âm thanh của dự án được hiểu thế nào?
Trả lời gợi ý: Bộ slide FINAL nêu một phép thử nhỏ trên 38 câu giọng máy, WER khoảng 42,4–47,7%, không thể suy ra hiệu năng trên hội thoại thật. Một báo cáo ASR riêng ngày 18/11 ghi PhoWhisper-medium gốc và LoRA trên VietMed-test 3.437 câu có WER 23,69% và 20,41%; trên ViMedCSS shard 323 câu là 33,36% và 26,06%. Đó là những phép đo khác tập và cấu hình; báo cáo cũng ghi LoRA chưa triển khai trong demo tại thời điểm đó. Không ghép chúng thành một kết quả chung.

### 23. “Nghe lại” có gì khác nút “Nghe” ở ca mẫu?
Trả lời gợi ý: Với ca có bản ghi âm và mốc thời gian, “Nghe lại” mở đoạn âm thanh liên quan; README nói thêm khoảng 0,5 giây mỗi đầu. Với ca mẫu chỉ có chữ, nút “Nghe” có thể dùng giọng đọc của trình duyệt để đọc văn bản; đó không phải ghi âm gốc. Khi demo phải nói rõ khác biệt này và lưu ý mốc thời gian có thể lệch.

### 24. Nếu ASR chép sai thì kiểm căn cứ có cứu được không?
Trả lời gợi ý: Không chắc. Nếu hệ thống lấy bản chép sai làm nguồn thì một thông tin có thể phù hợp văn bản nhưng vẫn trái âm thanh. Ví dụ “không dị ứng” bị mất chữ “không” có thể đổi hoàn toàn ý nghĩa. Vì vậy bác sĩ cần nghe lại, nhất là các dòng thuốc, số, phủ định; đánh giá phải bao gồm cả chuỗi âm thanh đến bản nháp.

## IV. Tính năng duyệt, nhật ký và hỗ trợ bác sĩ

### 25. Bác sĩ duyệt từng mệnh đề ra sao?
Trả lời gợi ý: Giao diện hiển thị lời thoại, mệnh đề, chủ thể và liên kết căn cứ cạnh nhau; người duyệt có thể giữ, sửa hoặc bỏ. Các mục có rủi ro được đưa vào vùng cần xác nhận với lý do. Mục tiêu là giảm chi phí tìm nguồn và làm rõ thông tin cần chú ý, nhưng dự án chưa chứng minh bằng nghiên cứu người dùng rằng thời gian duyệt giảm.

### 26. Ký duyệt và nhật ký chuỗi băm hoạt động như thế nào?
Trả lời gợi ý: Theo README, khi ký, bản ghi được thêm vào nhật ký có chuỗi băm SHA-256 và điểm neo; sửa sau khi ký sẽ hiển thị trạng thái cần ký lại. Băm giúp kiểm tra tính nhất quán và phát hiện một số thay đổi trong chuỗi. Nó không đồng nghĩa chữ ký số pháp lý, không ngăn mọi sửa đổi và hiệu quả phụ thuộc việc bảo vệ điểm neo, quyền truy cập và quy trình vận hành.

### 27. SHA-256 có mã hóa dữ liệu không?
Trả lời gợi ý: Không. SHA-256 là hàm băm, tạo giá trị tóm tắt để kiểm tra tính toàn vẹn; đây không phải cơ chế mã hóa để người không có khóa không thể đọc dữ liệu. Bảo mật nội dung cần cơ chế lưu trữ, truyền dữ liệu và quản lý khóa phù hợp. Khi thuyết trình cần tránh câu “dữ liệu được mã hóa bằng SHA-256”.

### 28. SBAR và sao chép sang HIS có chức năng gì?
Trả lời gợi ý: SBAR là cách tổ chức thông tin bàn giao theo tình huống, bối cảnh, đánh giá và đề xuất. MediTrace có chức năng tạo phiếu từ bản nháp có xét các dòng đã giữ, sửa hoặc bỏ, và hỗ trợ sao chép sang các ô ở hệ thống bệnh viện. Sao chép thủ công hoặc hỗ trợ thao tác không đồng nghĩa đã tích hợp hai chiều với HIS/EMR. Người dùng vẫn kiểm tra nội dung trước khi chuyển.

### 29. Câu hỏi cờ đỏ được tạo thế nào?
Trả lời gợi ý: Theo README, chức năng dùng luật chạy tại chỗ để gợi ý tối đa hai câu hỏi an toàn chưa hỏi, có xét một số thông tin như tuổi và giới, và đánh dấu khi đã hỏi. Đó là danh sách gợi ý giới hạn, không phải công cụ khẳng định bệnh nhân có hoặc không có nguy cơ. Cần người có chuyên môn duyệt nội dung và quyết định sử dụng.

### 30. Tờ dặn dò và mã QR có ý nghĩa gì?
Trả lời gợi ý: Hệ thống có tờ dặn dò có thể in và hỗ trợ đọc bằng giọng trình duyệt; README cũng nêu cổng QR cho người bệnh. Mục tiêu là giúp truyền đạt thông tin sau buổi khám, nhưng nội dung phải do bác sĩ kiểm tra. Cần xác minh bản demo tạo QR dẫn tới đâu, thời hạn và kiểm soát truy cập thế nào trước khi mô tả chi tiết về bảo mật.

### 31. Đối chiếu lần khám trước hoạt động ra sao?
Trả lời gợi ý: Chức năng so sánh thông tin giữa các lần khám của cùng người bệnh và nêu khả năng khác nhau ở dị ứng, bệnh nền hoặc thuốc mạn. Theo README, các dòng bác sĩ đã bỏ hoặc đã đính chính được bỏ qua. Khác biệt có thể phản ánh thay đổi thực sự theo thời gian chứ không nhất thiết là lỗi, vì vậy kết quả là lời nhắc để bác sĩ xem lại.

### 32. Các tính năng này có tự thay đổi bản nháp chính không?
Trả lời gợi ý: README phân biệt đường ống dựng bản nháp chính với các công cụ hỗ trợ xung quanh. Tuy nhiên một số thao tác cho phép người dùng chỉnh sửa hoặc chọn nội dung; khi demo cần nói rõ nguồn và trạng thái của kết quả. Không mặc định mọi nội dung từ công cụ phụ đã đi qua cùng lớp kiểm căn cứ như bản nháp chính.

## V. Công cụ lâm sàng và giới hạn

### 33. Tiền kiểm BHYT và gợi ý ICD-10 có phải quyết định thanh toán không?
Trả lời gợi ý: Không. Theo README, công cụ gợi ý mã ICD-10 và cảnh báo một số điểm có thể cần đối chiếu; nó không thay quy trình mã hóa, giám định hay quyết định thanh toán. Tài liệu cho biết có xét thông tin bị phủ định để tránh gợi ý mã cho bệnh đã phủ định. Các bảng tri thức liên quan chưa được bác sĩ hoặc dược sĩ duyệt, vì vậy cần kiểm tra với nguồn chính thức và chuyên gia.

### 34. Đối soát đơn thuốc và cảnh báo tương tác có thay dược sĩ?
Trả lời gợi ý: Không. Chức năng nhằm hỗ trợ tìm thông tin cần kiểm tra như thuốc đang dùng, dị ứng hoặc kết hợp có nguy cơ theo bảng quy tắc. Cảnh báo đúng phụ thuộc dữ liệu nhập, tên thuốc, liều, bảng tri thức và ngữ cảnh người bệnh. Không có cảnh báo không chứng minh đơn thuốc an toàn, đặc biệt khi dữ liệu tri thức dự án chưa được chuyên gia duyệt.

### 35. Đọc phiếu xét nghiệm và quy đổi đơn vị xử lý được gì?
Trả lời gợi ý: README mô tả bóc chỉ số từ phiếu cũ, quy đổi creatinin giữa µmol/L và mg/dL, và một số công cụ tính hỗ trợ đối chiếu. Sai sót có thể đến từ đọc nhầm chỉ số, dấu thập phân, đơn vị, thời điểm hoặc dữ liệu cần cho công thức. Bác sĩ phải xem phiếu gốc và xác nhận điều kiện áp dụng; không xem đầu ra như chỉ định chỉnh liều đã được kiểm chứng.

### 36. Có thể quảng bá công cụ đạt 100% độ chính xác không?
Trả lời gợi ý: Không nên. Một số tỷ lệ rất cao trong tài liệu cũ xuất phát từ ca kiểm thử đơn vị tự viết, không phải đánh giá độc lập trên dân số lâm sàng. Nên nói cụ thể công cụ đã vượt qua những trường hợp kiểm thử nào, còn độ chính xác trên dữ liệu thực tế chưa được xác định. Kiểm thử đơn vị kiểm tra hành vi dự kiến ở một số đầu vào, không chứng minh hiệu năng tổng thể.

### 37. Nhập LIS/HL7, xuất FHIR hoặc XML nghĩa là đã tích hợp bệnh viện?
Trả lời gợi ý: Chưa. README liệt kê nhập kết quả và xuất gói theo định dạng như HL7 FHIR R4 hoặc BHYT XML 130 trong phần công cụ mở rộng. Có chức năng đọc hoặc tạo tệp theo định dạng không chứng minh tương thích đầy đủ với một hệ thống cụ thể hoặc được cơ sở tiếp nhận. Tích hợp cần kiểm thử schema, ánh xạ dữ liệu, xác thực, bảo mật, phiên bản và quy trình vận hành với hệ thống đích.

### 38. Cam đoan thủ thuật, đi buồng và bàn giao ca có thể sử dụng ngay không?
Trả lời gợi ý: Chúng là các tiện ích hỗ trợ tổ chức biểu mẫu và thông tin quanh quy trình khám. Việc một giao diện hoặc mẫu đã được lập trình không chứng minh biểu mẫu phù hợp mọi cơ sở hoặc có hiệu lực pháp lý. Cần đối chiếu quy trình của cơ sở, bảo đảm người có trách nhiệm kiểm tra nội dung và xác nhận trước khi sử dụng thực tế.

## VI. Trợ lý nhiều tác tử và bảo mật

### 39. Trợ lý nhiều tác tử là gì?
Trả lời gợi ý: Theo README, trợ lý có bộ điều phối tạo kế hoạch tối đa sáu bước và giao các nhiệm vụ như tìm tài liệu, trả lời, đối chiếu, thuốc và dị ứng cho các tác tử chuyên trách. Đây là một cách phân chia công việc phần mềm; không có nghĩa mỗi tác tử độc lập đúng hoặc kết quả được chuyên gia duyệt. Cần phân biệt trợ lý phụ với đường ống chính được đo trong nghiên cứu.

### 40. Khi trợ lý dùng mô hình ngoài, dữ liệu được bảo vệ thế nào?
Trả lời gợi ý: README mô tả công tắc bật mô hình ngoài, cảnh báo, danh sách trường cho phép và chặn một số câu hỏi có danh tính; quản trị có thể tắt toàn hệ thống. Tuy nhiên, loại tên, điện thoại và địa chỉ không bảo đảm ẩn danh tuyệt đối vì nội dung còn lại vẫn có thể nhận diện gián tiếp. Trước khi dùng dữ liệu thật cần kiểm tra từng luồng, nhà cung cấp, cấu hình, quản lý khóa và chính sách lưu trữ thực tế.

### 41. Có thể nói dữ liệu không bao giờ rời máy không?
Trả lời gợi ý: Không nên nói tuyệt đối. Theo thiết kế, các thành phần chính có thể chạy tại chỗ, nhưng một số tính năng phụ có thể gửi dữ liệu ra ngoài khi người dùng bật. Ngoài ra, địa điểm lưu trữ và xử lý phụ thuộc cấu hình triển khai. Phải chỉ rõ chức năng, nơi chạy và dữ liệu có thể gửi đi thay vì đưa ra một cam kết chung.

### 42. SQLite và đăng nhập đã đủ bảo mật cho bệnh án thật chưa?
Trả lời gợi ý: SQLite là cơ sở dữ liệu lưu trữ, không tự bảo đảm bảo mật toàn diện. Đăng nhập và tách dữ liệu theo người dùng là một phần; còn cần xác minh phân quyền phía máy chủ, mã hóa phù hợp khi lưu và truyền, quản lý khóa, sao lưu, xóa dữ liệu, nhật ký và kiểm thử tấn công. Nếu chưa đo và kiểm định, phải trình bày là việc cần hoàn thiện trước thử nghiệm với dữ liệu sức khỏe thật.

### 43. Nếu bị hỏi về tuân thủ pháp luật và bảo vệ dữ liệu?
Trả lời gợi ý: Nhóm cần phân biệt các biện pháp kỹ thuật đã làm với việc đã đáp ứng đầy đủ yêu cầu pháp lý. Trước triển khai thật phải làm việc với cơ sở y tế và người phụ trách pháp lý để xác định căn cứ xử lý, trách nhiệm các bên, quy trình đồng ý khi cần, lưu trữ, truy cập và ứng phó sự cố theo quy định áp dụng. Không khẳng định đã tuân thủ toàn bộ chỉ dựa trên việc có đăng nhập hoặc chuỗi băm.

## VII. Dữ liệu và đánh giá

### 44. Bộ dữ liệu 5.000 ca là gì?
Trả lời gợi ý: Đây là dữ liệu hội thoại mô phỏng được tạo theo khuôn, không phải 5.000 bệnh nhân thật hoặc 5.000 ca kiểm thử độc lập. Các tài liệu mô tả nhiều phiên bản: bộ dùng trong slide FINAL và bộ v2 mở rộng. Không được trộn số khuôn hoặc cách chia tập của hai phiên bản. Khi trình bày một phép đo, phải chỉ đúng bộ và phiên bản gắn với phép đo đó.

### 45. Bộ dùng trong slide FINAL được chia thế nào?
Trả lời gợi ý: Tài liệu nội dung slide nêu phiên bản 5.000 hội thoại, 100 mẫu bệnh và 47.825 mệnh đề đáp án; chia 3.776 ca huấn luyện, 634 ca phát triển và 590 ca kiểm tra cuối, theo mẫu bệnh. Slide ghi tập cuối chưa dùng trong kết quả trình bày. Đây là số của phiên bản báo cáo 8b được tài liệu đó viện dẫn, không áp cho mọi bộ dữ liệu khác trong kho.

### 46. Bộ v2 657 khuôn có liên quan thế nào?
Trả lời gợi ý: README mô tả bộ v2 mở rộng có 5.000 ca, 657 khuôn thuộc 21 hệ cơ quan và tỷ lệ lặp câu 47,37% theo cách đo được nêu. Đây là bộ và mốc nâng cấp riêng; không được ghép 657 khuôn với phân chia 75/13/12 mẫu bệnh của bộ slide FINAL rồi coi là cùng phép thử. Số khuôn lớn không tự chứng minh dữ liệu tự nhiên hay độc lập tuyệt đối.

### 47. Tỷ lệ lặp câu có ý nghĩa gì?
Trả lời gợi ý: README ghi tỷ lệ lặp của bộ v2 là 47,37%, giảm so với mốc 76,92% của bộ cũ theo báo cáo dự án. Cần hiểu đúng định nghĩa chuẩn hóa và phiên bản dữ liệu trước khi so sánh. Lặp có thể do câu ngắn tự nhiên nhưng cũng có thể làm mô hình gặp lại cách nói quen; giảm lặp không tự chứng minh khả năng tổng quát hóa.

### 48. Chia theo khuôn có ngăn hết rò rỉ?
Trả lời gợi ý: Chia theo khuôn tránh ca cùng khuôn nằm ở nhiều tập, giúp phép đánh giá khó hơn chia ngẫu nhiên theo ca. Nhưng câu hoặc cụm từ vẫn có thể trùng giữa các khuôn. Cần đo trùng nguyên văn và gần đúng, kiểm tra nguồn sinh, người nói hoặc phiên đối với âm thanh, và giữ tập cuối không dùng để điều chỉnh.

### 49. 300 ca thử thách là gì?
Trả lời gợi ý: Bộ slide mô tả bốn nhóm thử thách tổng cộng 300 ca: đổi chủ thể 80, đính chính 60, nhiễu giọng nói 80, vùng miền 80. Chúng được tạo để xem hành vi ở các tình huống mục tiêu và so sánh phương án. Đây là ca mô phỏng, không phải 300 cuộc khám bệnh nhân thật, và không đại diện đầy đủ cho tần suất lỗi trong bệnh viện.

### 50. Kết quả xử lý đính chính là bao nhiêu?
Trả lời gợi ý: Trên mẫu 240 ca phát triển được nêu trong slide, tỷ lệ giữ thông tin đã bị sửa giảm từ 5,21% xuống 0,36% khi thêm xử lý lời sửa so với biến thể chỉ tách thông tin. Chênh lệch là 4,85 điểm phần trăm, tương đương giảm tương đối khoảng 93,1%. Một phép đo riêng trên bộ đính chính 60 ca là 11,48% xuống 0,80%. Không gộp hai mẫu hoặc gọi mức giảm tương đối là giảm điểm phần trăm.

### 51. Kiểm căn cứ cải thiện gì và đánh đổi gì?
Trả lời gợi ý: Slide báo cáo trên bộ đổi chủ thể 80 ca, tỷ lệ lỗi nghiêm trọng trong phần chính theo định nghĩa phép đo giảm từ 43,0% xuống 36,2%; tỷ lệ thông tin đáp án không có trong phần chính tăng từ 4,5% lên 7,7%. Đây là so sánh hai biến thể có và không thêm bước kiểm căn cứ, không phải kết luận chung so với mọi mô hình viết trực tiếp. Một số thông tin đúng có thể chuyển sang “Cần xác nhận”; không đồng nghĩa tất cả bị mất khỏi hệ thống.

### 52. So với viết trực tiếp, MediTrace thắng hay thua?
Trả lời gợi ý: Về điểm quy gán trên bốn bộ trong slide, viết trực tiếp cao hơn: đổi chủ thể 0,9388 so với 0,7476; đính chính 0,9885 so với 0,8299; nhiễu 0,8033 so với 0,7009; vùng miền 0,9735 so với 0,8950. Do đó giả thuyết ghi đúng người hơn không được ủng hộ trong phép thử. Thiết lập các phương án khác nhau nên chưa thể quy toàn bộ chênh lệch cho kiến trúc; giá trị truy vết cần đánh giá riêng.

### 53. F1, precision, recall và SER là gì?
Trả lời gợi ý: Precision là tỷ lệ thông tin được hệ thống đưa ra mà đúng theo tiêu chí chấm; recall là tỷ lệ thông tin cần có được tìm thấy; F1 là trung bình điều hòa giữa precision và recall. SER là tỷ lệ lỗi theo định nghĩa bộ chấm, có thể gồm sai, thiếu và thừa. Mỗi chỉ số phụ thuộc đơn vị tính và cách ghép mệnh đề; điểm trung bình không phản ánh đầy đủ lỗi nguy hiểm hiếm gặp.

### 54. Vì sao ROUGE không đủ?
Trả lời gợi ý: ROUGE đếm sự trùng lặp từ hoặc cụm từ. Trong thử nghiệm của dự án trên 400 bản ghi, khi đổi chỗ bệnh nhân và người nhà mà không đổi tập từ, ROUGE-1 vẫn 1,0000. Câu có thể giống về từ nhưng sai quan hệ chủ thể. Cần đo thêm đúng người, phủ định, thời gian và trạng thái cùng với kiểm tra thủ công.

### 55. Đo lớp cảnh báo bằng cấy lỗi như thế nào?
Trả lời gợi ý: Nhóm lấy bản đáp án làm bản ghi sạch trong thiết kế thử, cấy một lỗi biết trước rồi đo cảnh báo đúng nhóm tại vị trí lỗi; bản sạch được dùng để đếm cảnh báo phát ra. Trên tập giữ kín 240 ca sau khi khóa luật, báo cáo ghi độ nhạy trung bình 0,871 và trung bình 8,00 cảnh báo trên mỗi ca sạch. Đây không phải xác suất an toàn và không phải kết quả trực tiếp trên lỗi tự nhiên của bệnh án thật.

### 56. Tại sao trung bình 0,871 có thể gây hiểu nhầm?
Trả lời gợi ý: Các loại lỗi có kết quả rất khác nhau và số mẫu khác nhau. Trên tập giữ kín của thí nghiệm cấy lỗi, phát hiện “giả định thành sự thật” là 0,417 trên 240 lần cấy, còn “bản cũ còn hiệu lực” là 0,311 trên 45 lần cấy. Những số này có bất định và chỉ thuộc cách cấy cụ thể, nhưng cho thấy một trung bình tốt có thể che điểm yếu quan trọng.

### 57. Tại sao báo nhầm là vấn đề?
Trả lời gợi ý: Cảnh báo trên ca sạch có thể làm bác sĩ phải xem thêm và khó ưu tiên cảnh báo quan trọng. Báo cáo cấy lỗi nêu trung bình 8,00 cảnh báo mỗi ca sạch ở tập giữ kín; phần lớn là cảnh báo bỏ sót chung và báo cáo ghi chúng chỉ lưu hậu trường. Vì vậy không được tự nói cả tám cảnh báo đều hiện cho bác sĩ. Cần đo giao diện thực tế và thời gian, mức bỏ qua khi có người dùng.

### 58. Vì sao có tài liệu ghi 0% chặn nhầm?
Trả lời gợi ý: Báo cáo đối chiếu số liệu giải thích 0/30.136 được tính trên một điều kiện đáp án gần nguyên văn hội thoại, không đại diện trực tiếp cho đầu ra mô hình. Cùng báo cáo nêu các phép đo chặn thừa khác trên đầu ra mô hình với điều kiện và phiên bản cụ thể. Không nói “chặn nhầm 0% trong thực tế”; phải nêu mẫu và nguồn, đồng thời rà lại file nộp.

### 59. Dữ liệu và kết quả có thể tái lập không?
Trả lời gợi ý: Muốn tái lập cần dữ liệu hoặc quyền truy cập, manifest và cách chia, mã hoặc commit, cấu hình mô hình, phiên bản thư viện, lệnh chạy, phần cứng và tệp kết quả. Một số dữ liệu ASR và kết quả được tài liệu ghi nằm ngoài repo nên không thể giả định người ngoài tự truy cập được. Trước bảo vệ nên chọn các số chính và chứng minh đường đi từ slide về báo cáo, tệp kết quả và cách chạy.

### 60. Có thể suy từ dữ liệu mô phỏng ra bệnh nhân thật?
Trả lời gợi ý: Chưa thể. Các bộ sinh có thể lặp câu, thiếu nói chen, tiếng ồn và cách diễn đạt tự nhiên. Kết quả mô phỏng là bằng chứng bước đầu về các tình huống đã thiết kế. Cần dữ liệu đại diện được phép sử dụng, nhãn chuyên môn, đánh giá độc lập và nghiên cứu với người dùng trước khi kết luận về hiệu quả lâm sàng.

## VIII. Demo, hiệu năng và kế hoạch tiếp theo

### 61. Tạo một bản nháp mất bao lâu?
Trả lời gợi ý: README nêu khoảng 3,5 phút trên RTX 3060; slide nêu khoảng 213 giây cho phép đo được dẫn. Đây là thời gian tham chiếu của cấu hình và đầu vào cụ thể, không bảo đảm mọi ca đều bằng nhau. Bản mẫu đã chạy sẵn xuất hiện nhanh không chứng minh mô hình vừa suy luận trong vài giây. Cần đo thêm theo độ dài, phần cứng và đồng thời nhiều người dùng.

### 62. Làm sao trình diễn minh bạch khi thời gian ngắn?
Trả lời gợi ý: Dùng ca mẫu để minh họa luồng và nói rõ bản nháp đã được chuẩn bị trước; chỉ nhãn mô hình vừa chạy, bộ đệm hoặc bản ghi chạy trước nếu giao diện có. Sau đó mở mệnh đề, chỉ người nói và chủ thể, câu gốc, mục cần xác nhận, thao tác giữ/sửa/bỏ và thử chốt chặn. Nếu muốn chứng minh suy luận thật, khởi chạy trước một ca mới và công bố thời gian dự kiến, không giả vờ ca mẫu là kết quả mới.

### 63. Ca mẫu đa người nói có gì để khai thác?
Trả lời gợi ý: README mô tả ba ca dựng sẵn: bác sĩ–mẹ–bệnh nhi; hai người bệnh cùng phòng; và bác sĩ–cụ ông–con gái. Mỗi ca giúp chỉ rõ sự khác nhau giữa người phát ngôn và người được nhắc đến, cũng như lý do cần đối chiếu thông tin. Khi demo hãy chọn một mệnh đề cụ thể đã kiểm tra trước, tránh tuyên bố hệ thống xử lý hoàn hảo mọi quan hệ gia đình.

### 64. Nếu mô hình hoặc mạng không hoạt động khi demo?
Trả lời gợi ý: Chuẩn bị ảnh chụp, ca đã chạy và sơ đồ, ghi rõ đó là kết quả dự phòng. Phần chạy tại chỗ cần xác minh dịch vụ và phần cứng trước; tính năng cần mạng hoặc mô hình ngoài phải có phương án giải thích không dùng mạng. Nên nói rõ tình trạng thực tế thay vì tạo ấn tượng kết quả dự phòng được xử lý trực tiếp.

### 65. Hướng phát triển ưu tiên là gì?
Trả lời gợi ý: Ưu tiên kiểm chứng trước khi mở rộng tuyên bố: hoàn thiện đánh giá độc lập và khóa tập cuối; giảm bỏ sót và cảnh báo sai; đo chuỗi âm thanh đến bản nháp với giọng và môi trường đa dạng; nhờ bác sĩ, dược sĩ thẩm định tri thức; kiểm thử bảo mật và thử nghiệm quy trình với người dùng. Mỗi thay đổi phải có chỉ số và dữ liệu kiểm tra riêng, không chỉ thêm chức năng.

## IX. Câu phản biện chuyên sâu

### 66. “Nếu AI bỏ sót dị ứng, các em chặn ký để làm gì?”
Trả lời gợi ý: Chặn ký giúp bảo đảm các mục đã được đánh dấu cần xác nhận không bị bỏ qua, nhưng không bảo đảm phát hiện mọi thông tin vắng mặt. Nếu dị ứng không được tách và lớp phát hiện bỏ sót không báo, bác sĩ vẫn phải đối chiếu hội thoại. Đây là giới hạn của kiến trúc hiện tại. Hướng cải thiện là đo recall cho dị ứng trên tập được chuyên gia gán nhãn, cải thiện phát hiện bỏ sót và thiết kế luồng duyệt toàn bộ nguồn.

### 67. “Trích dẫn nguyên văn 100% nghĩa là hết ảo giác?”
Trả lời gợi ý: Không. Con số 52.634/52.634 được báo cáo là kiểm tra trích dẫn trong bộ dữ liệu huấn luyện do chương trình sinh, không phải chứng minh mọi đầu ra mô hình đều đúng. Một trích dẫn có thật vẫn có thể bị diễn giải sai người hay phủ định. Cần đánh giá riêng trích dẫn và nội dung trên đầu ra mô hình.

### 68. “Sao các em nói 0,8% mà tài liệu khác nói không có phép đo?”
Trả lời gợi ý: Cần hỏi rõ mẫu số và định nghĩa. Slide báo cáo 0,80% là tỷ lệ giữ thông tin đã bị sửa trong phép so sánh trên bộ đính chính 60 ca; tài liệu đối chiếu cảnh báo không được dùng con số đó làm tỷ lệ tổng quát cho một phép đo khác như khả năng lớp cảnh báo bắt mọi lỗi đính chính. Cùng một con số không thể chuyển sang chỉ số khác nếu mẫu và cách đếm không giống nhau.

### 69. “Tính năng thuốc chưa chuyên gia duyệt, có gây hại không?”
Trả lời gợi ý: Rủi ro là người dùng nhầm gợi ý sơ bộ thành kết luận lâm sàng và tin rằng không có cảnh báo nghĩa là an toàn. Nhóm phải công bố rõ trạng thái chưa thẩm định, không sử dụng làm căn cứ quyết định độc lập, kiểm soát phạm vi demo và ưu tiên chuyên gia thẩm định dữ liệu, quy tắc và phép thử. Trước khi sử dụng thực tế phải đánh giá toàn bộ quy trình với cơ sở chuyên môn.

### 70. “Hệ thống có phải thiết bị y tế hoặc đã đủ điều kiện triển khai?”
Trả lời gợi ý: Nhóm mô tả mục đích hiện tại là hỗ trợ tạo bản nháp và không đưa ra kết luận pháp lý về phân loại sản phẩm. Việc phân loại và điều kiện triển khai phụ thuộc mục đích sử dụng, chức năng thực tế và quy định áp dụng; cần chuyên gia pháp lý và cơ quan/cơ sở có thẩm quyền xem xét. Dự án chưa có bằng chứng để khẳng định sẵn sàng triển khai lâm sàng.

### 71. “Nếu mô hình lớn viết trực tiếp tốt hơn, tại sao phải dùng MediTrace?”
Trả lời gợi ý: Với chỉ số quy gán trong phép thử của nhóm, phương án viết trực tiếp thực sự cao hơn và cần công bố rõ. Lý do nghiên cứu MediTrace là xem liệu biểu diễn có cấu trúc và truy vết giúp con người kiểm tra lời sửa, căn cứ và trạng thái tốt hơn hay không. Hiện chưa có nghiên cứu người dùng đủ để khẳng định quy trình đó nhanh hơn hoặc an toàn hơn; đây là giả thuyết cần kiểm chứng tiếp.

### 72. “Điểm mới có phải chỉ là ghép nhiều thư viện?”
Trả lời gợi ý: Nhiều hệ thống ứng dụng sử dụng mô hình nền và thư viện có sẵn; giá trị cần xét ở bài toán, cách tổ chức dữ liệu, thuật toán bổ sung, thiết kế đánh giá và kết quả thực nghiệm. MediTrace xây dựng đường ống, luật, dữ liệu mô phỏng và quy trình truy vết để xử lý đặc thù hội thoại. Nhóm không nhận công lao tạo ra mô hình hoặc thư viện gốc và sẵn sàng chỉ phần mã, dữ liệu cùng nguồn của từng thành phần.

### 73. “Nếu bác sĩ phải xem lại hết thì có tiết kiệm thời gian không?”
Trả lời gợi ý: Chưa biết. Truy vết có thể giúp tìm căn cứ nhưng cảnh báo sai và việc đối chiếu có thể tăng công việc. Để trả lời cần nghiên cứu so sánh với quy trình hiện tại: cùng loại ca, người tham gia phù hợp, đo thời gian, lỗi còn lại, số lần sửa và trải nghiệm. Nhóm hiện chưa có cơ sở công bố tỷ lệ tiết kiệm thời gian.

### 74. “Những gì nhóm có thể tự tin nhất?”
Trả lời gợi ý: Nhóm có thể trình bày kiến trúc, chỉ ra mã và demo những chức năng hiện hoạt động; trình bày kết quả trong từng phép thử mô phỏng cùng hạn chế. Trên các phép đo được nêu, xử lý lời sửa làm giảm tỷ lệ giữ bản cũ; đồng thời kiểm căn cứ thể hiện đánh đổi giữa lỗi trong phần chính và thông tin không vào phần chính. Nhóm không biến kết quả đó thành tuyên bố hiệu quả lâm sàng hoặc an toàn tuyệt đối.

## X. Bảng số liệu nhanh để ôn tập

Mỗi con số dưới đây phải đọc kèm điều kiện trong cùng dòng; không thay thế hoặc kết hợp các hàng như thể chung tập thử.

• Bộ slide FINAL: 5.000 hội thoại mô phỏng; 100 mẫu bệnh; 47.825 mệnh đề; chia 3.776/634/590 ca train/dev/test cuối; test cuối được slide ghi chưa dùng cho kết quả hiện tại.
• Bộ v2 riêng: README ghi 5.000 ca, 657 khuôn, 21 hệ cơ quan; tỷ lệ lặp câu 47,37%. Không ghép với cách chia của bộ slide.
• Tinh chỉnh: 43,1% xuống 11,5% bỏ sót, 30 ca phát triển/304 mệnh đề, bộ chấm tự động; không suy ra hiệu quả trên bệnh nhân thật.
• Lời sửa: 5,21% xuống 0,36%, mẫu 240 ca phát triển; giảm 4,85 điểm phần trăm hoặc 93,1% tương đối. Bộ riêng 60 ca: 11,48% xuống 0,80%.
• Đổi chủ thể 80 ca: lỗi nghiêm trọng ở phần chính 43,0% xuống 36,2%; thiếu khỏi phần chính 4,5% lên 7,7% khi thêm kiểm căn cứ trong phép so sánh nội bộ.
• Cấy lỗi: tập giữ kín 240 ca, trung bình đúng loại 0,871, trung bình 8,00 cảnh báo/ca sạch theo định nghĩa báo cáo; không phải độ an toàn thực tế.
• Âm thanh: phép thử slide gồm 38 câu giọng máy, WER 42,4–47,7%; thí nghiệm ASR khác trên VietMed và ViMedCSS có tập và cấu hình khác.
• Độ trễ: khoảng 213 giây hoặc 3,5 phút/bản nháp theo báo cáo trên RTX 3060; phụ thuộc cấu hình và đầu vào.
• ROUGE-1: 1,0000 ngay cả khi đổi người trong phép thử 400 bản ghi; chứng minh giới hạn của chỉ số từ vựng trong tình huống thử, không chứng minh mọi chỉ số ngữ nghĩa đều tốt.

## XI. Nguồn đối chiếu trước khi trình bày

1. README.md — mô tả kiến trúc, tính năng, điều kiện demo, kết quả và giới hạn.
2. docs/slide-thuyet-trinh/canva-preview/MediTrace-15-slide-noi-dung.md — số liệu theo bộ slide FINAL, định nghĩa so sánh và các lưu ý.
3. docs/doi-chieu-so-lieu-bao-cao.md — cảnh báo số liệu cũ không có nguồn hoặc dễ bị hiểu sai; kiểm tra cả file Word sinh từ tài liệu cũ.
4. docs/ket-qua/cay-loi.md — thiết kế và kết quả cấy lỗi; bảng từng loại, mẫu và cảnh báo trên ca sạch.
5. docs/tien-do-asr-va-kiem-ro-ri.md — kết quả ASR riêng, rò rỉ dữ liệu và trạng thái triển khai tại thời điểm ghi báo cáo.
6. BAN_DO_MA_NGUON.md — bản đồ mã nguồn, tên tệp và đường dẫn để mở khi BGK hỏi chi tiết.
7. BAO_CAO_CAI_TIEN_CHANG_1.md và docs/final/Báo cáo dự án.md — phạm vi cải tiến, thực nghiệm và hồ sơ báo cáo.

Ghi chú: Đây là tài liệu hỗ trợ luyện bảo vệ được tổng hợp từ nguồn nội bộ, không phải báo cáo kiểm định độc lập. Trước khi nộp, kiểm tra lại đúng phiên bản demo, số liệu và trạng thái đánh giá của dự án.
