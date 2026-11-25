# Thiết kế: Trợ lý nhiều tác tử trong ngăn chat của MediTrace

Ngày 23/11/2026. Trạng thái: bản nháp chờ người dùng duyệt. Những chỗ ghi **(quyết định của người soạn)** là lựa chọn của người soạn, chưa được người dùng đồng ý.

## 1. Ý định và lý do

Bác sĩ dùng ngăn chat bên phải của MediTrace (và trang "Tra cứu") để hỏi về ca khám và tra cứu y văn. Hôm nay họ gõ một câu, chờ, rồi nhận một câu trả lời kèm thẻ nguồn; không thấy hệ thống đang làm gì. Người dùng muốn biến ô hỏi đó thành nơi **nhiều tác tử (agent) cùng làm việc**: bác sĩ hỏi, hệ thống lập kế hoạch, từng tác tử chạy các bước nhìn thấy được (có dấu tích khi xong), rồi ra câu trả lời có nguồn. Mẫu tham khảo là bảng "Agents" bật tắt được và thẻ tiến độ có dấu tích của Suki, và bảng "Discussion topics" (gạch chủ đề đã bàn).

Mục đích: hỗ trợ bác sĩ **tra cứu và trả lời câu hỏi**. Người dùng đã nói rõ các tác tử này không phải để làm hành chính bảo hiểm.

## 2. Mục tiêu, không phải mục tiêu, mục tiêu cần tránh

Mục tiêu:
1. Một bảng "Tác tử" cho bật hoặc tắt từng tác tử, nằm trong ngăn chat có sẵn.
2. Mỗi câu hỏi tạo ra một **kế hoạch** (các tác tử và bước sẽ chạy), rồi **tiến độ thật**: bước nào code đã chạy xong mới hiện dấu tích.
3. Câu trả lời cuối luôn kèm nguồn và nhãn mô hình ngoài, dùng lại `TraLoiCoNguon`.
4. Hỏi và tra cứu dùng **mô hình thương mại** (người dùng chốt 23/11/2026), qua cổng ngoài có sẵn.

Không phải mục tiêu (giai đoạn này):
- Theo dõi trực tiếp trong lúc ghi âm (cần chép lời theo thời gian thực; hiện MediTrace chép lời sau khi ghi âm xong). Để giai đoạn sau.
- Tác tử bảo hiểm và thanh toán kiểu Mỹ (xin duyệt thuốc trước, khiếu nại, điều chỉnh rủi ro): không có ở Việt Nam.
- Tác tử tự ghi vào hồ sơ, tự kê đơn hay tự ra y lệnh.
- Dùng mô hình thương mại cho khâu trích mệnh đề hoặc tạo bản nháp chính.

Mục tiêu cần tránh (thất bại dù chạy được):
- **Tiến độ giả**: hiện dấu tích cho bước chưa chạy, hoặc để mô hình tự kể mình đã làm gì.
- Gửi dữ liệu ca khám ra ngoài khi bác sĩ chưa bật công tắc.
- Câu trả lời nghe như chẩn đoán hay chỉ định điều trị.
- Kế hoạch do mô hình đề xuất bị trình bày như tiến độ đã làm.
- Điều phối nhận nội dung ca khám khi không cần.

## 3. Ràng buộc (đã có trong dự án)

- Bản nháp hồ sơ và khâu trích luôn do Qwen3-4B tại chỗ làm; mô hình ngoài chỉ cho việc phụ, mặc định tắt, chỉ chạy khi yêu cầu có `allowExternal: true` (công tắc "Cho phép gửi ra mô hình ngoài"), nếu không trả 403 `chua_cho_phep_ngoai` (`web/server.ts`, hàm `chanNeuChuaChoPhep`). **Ngoại lệ (người dùng chốt 23/11/2026):** đường *tra cứu ẩn danh* (mục 5.1) **luôn mở**, không cần công tắc, vì mô hình ngoài chỉ nhận dữ liệu đã qua bộ luật ẩn danh. Các việc ngoài khác (`edit-note`, `generate-note-external`...) vẫn cần công tắc như cũ.
- Mọi nội dung gửi ra phải đi qua `goiNgoai`, vốn che thông tin nhận dạng (`anDanhVanBanNgoai`) rồi trả lại sau khi nhận. Khoá và địa chỉ cổng nằm ngoài mã (`D:/Claude/.secrets/`).
- Đáp án từ mô hình ngoài mang `source: "mo_hinh_ngoai"` và tên mô hình, và không bao giờ được đưa vào phép đo của đề tài.
- Không chẩn đoán, không kê đơn; bản nháp mặc định chưa duyệt; bác sĩ quyết định.
- Đường hầm Cloudflare cắt yêu cầu chờ quá khoảng 100 giây: việc dài phải theo mô hình "trả 202 và hỏi lại" (`generate-note` đã làm vậy).
- Tên người dùng, nội dung ca khám không được ghi vào nhật ký (nhật ký chỉ ghi tên tác tử, bước, thời lượng, mã lỗi).
- Chạy tiếp mô hình ngoài tốn tiền: kiểm số dư, ước tính chi phí và giới hạn trước khi bật cho người dùng.

## 4. Các cách làm đã cân nhắc

- **A. Bộ điều phối trên máy chủ, tác tử có bước cố định** (đã chọn, người dùng đồng ý). Mỗi tác tử là một mô-đun có danh sách bước thật. Hỏi tạo một việc nền; giao diện hỏi lại theo mã việc. Tiến độ trung thực vì code tự báo bước.
- **B. Mô hình tự lập kế hoạch và tự báo tiến độ.** Linh hoạt, nhưng tiến độ do mô hình tự tả, khó kiểm, và mô hình tại chỗ quá chậm. Không chọn nguyên dạng. **Lấy một phần:** từ 23/11/2026 người dùng muốn một tác tử điều phối giao việc, nên việc *lập kế hoạch* do mô hình thương mại làm (có kiểm bằng danh sách trắng và trần), còn *thực hiện và báo tiến độ* vẫn do code (cách A). Đây là cách lai, không phải B.
- **C. Chỉ vẽ tiến độ ở giao diện.** Nhanh nhưng tiến độ giả, trái nguyên tắc dự án (các màn minh hoạ hiện đã phải ghi rõ "không phải nhật ký thật"). Không chọn.

## 5. Thiết kế đã chốt

**Cách làm việc (người dùng chốt 23/11/2026):** bác sĩ gõ yêu cầu; một **tác tử điều phối** (mô hình thương mại `qwen3.8-flash` qua cổng ai-box hiện có) đọc yêu cầu, **lập kế hoạch và giao việc** cho các tác tử chuyên trách (tìm kiếm, trả lời, đối chiếu...), rồi gộp kết quả. Giao diện hiện **kế hoạch** (do điều phối đề xuất) và **tiến độ** (do code ghi). Hai thứ này luôn được tách và dán nhãn khác nhau: kế hoạch là "mô hình đề xuất sẽ làm", dấu tích tiến độ chỉ xuất hiện khi hàm của bước đó đã chạy xong. Điều phối không bao giờ tự báo "đã xong".

**Luồng một câu hỏi:**
1. *Điều phối* nhận câu hỏi và **chỉ biết hình dạng của ca** (có hội thoại không, có bản nháp không, có mệnh đề đã trích không), **không nhận nội dung ca khám**. Trả về kế hoạch dạng JSON: danh sách `{tac_tu, nhiem_vu, phu_thuoc}`.
2. Máy chủ **kiểm kế hoạch** trước khi chạy: chỉ nhận tác tử trong danh sách trắng, tối đa 6 bước, phụ thuộc không vòng. Kế hoạch sai khuôn thì dùng kế hoạch dự phòng bằng luật (mục dưới).
3. Chạy các tác tử theo thứ tự phụ thuộc, song song khi độc lập. Mỗi bước ghi trạng thái (chờ, đang chạy, xong, bỏ qua, lỗi) vào việc nền.
4. Tác tử *Đối chiếu* kiểm câu trả lời; nếu phát hiện ý không có căn cứ thì được **sửa lại đúng một lần** (tác tử Trả lời viết lại), rồi trả kết quả kèm cảnh báo nếu vẫn còn ý thiếu căn cứ.
5. Giao diện hỏi lại mỗi 1 đến 2 giây (đường hầm không hợp luồng sự kiện kéo dài), vẽ kế hoạch, tiến độ và câu trả lời.

**Các tác tử bản đầu (quyết định của người soạn: tên và ranh giới; người dùng đã chốt ba vai tìm kiếm, trả lời, đối chiếu):**
| Tác tử | Làm gì | Dùng mô hình thương mại không |
|---|---|---|
| Điều phối | Lập kế hoạch, giao việc, gộp kết quả | Có (chỉ nhận *ca ẩn danh* theo mục 5.1) |
| Tìm kiếm | Mô hình chỉ đặt từ khoá; **mã tìm thật** trong kcb.vn, MSD, PubMed..., trả các đoạn trích có mã nguồn | Có (chỉ đặt từ khoá) |
| Trả lời | Viết câu trả lời từ các đoạn trích và ca khám, mỗi ý ghi nguồn hoặc lượt hội thoại | Có |
| Đối chiếu | Kiểm bằng code (đoạn trích và đường dẫn có thật, số liệu khớp máy tính, có đủ nguồn) rồi nhờ mô hình xét từng ý có được đoạn trích ủng hộ không; đánh dấu ý thiếu căn cứ | Có (phần xét ý); phần code không |
| Chủ đề cần bàn | So mệnh đề đã trích với danh sách chủ đề (triệu chứng, dị ứng, thuốc đang dùng, tiền sử...), gạch chủ đề đã nói | Không (luật tại chỗ) |
| Đối chiếu thuốc và dị ứng | Gom thuốc, dị ứng đã trích, báo mâu thuẫn và chỗ thiếu; không kê đơn | Không (luật tại chỗ) |

**Kế hoạch dự phòng bằng luật** (khi công tắc mô hình ngoài tắt, hoặc điều phối trả sai khuôn, hoặc cổng ngoài lỗi): có ca khám thì chạy "Chủ đề cần bàn" và "Đối chiếu thuốc và dị ứng"; mô hình ngoài tắt thì các tác tử cần nó hiện "bỏ qua: chưa bật mô hình ngoài".

**Bảng tác tử.** Công tắc từng tác tử lưu theo người dùng (bảng `cai_dat` đã có). Tác tử dùng mô hình ngoài chỉ chạy khi công tắc "Cho phép gửi ra mô hình ngoài" đang bật; nếu tắt thì hiện lý do và không chạy.

**Việc nền.** Mở rộng bảng `viec_nen` (hàng đợi bền vững, `web/may-chu/hang-doi.ts`) để mang thêm loại việc và bước đang chạy. Việc trợ lý **không xếp sau hàng GPU**: chỉ tác tử tại chỗ nặng mới dùng chung, các tác tử gọi mô hình ngoài chạy song song, tối đa hai việc cùng lúc (quyết định của người soạn). Khởi động lại máy chủ thì việc dở được chạy lại như `generate-note`.

**Bước thật.** Mỗi bước có tên, trạng thái (chờ, đang chạy, xong, bỏ qua, lỗi), ghi chú ngắn. Bước chỉ chuyển "xong" sau khi hàm của nó trả về. Một bước hay một tác tử lỗi không làm hỏng cả việc: trả câu trả lời một phần và ghi rõ phần nào lỗi.

**An toàn.** Câu trả lời của tác tử nào cũng kèm nguồn hoặc nêu "không đủ căn cứ"; cùng nhắc "chỉ để tham khảo, không phải chẩn đoán" như hiện nay. Tác tử chỉ đề xuất; việc thêm gì vào ngữ cảnh hay bản nháp do bác sĩ bấm.

**Chi phí.** Người dùng nói chưa tính chuyện tiền (23/11/2026): **chưa đặt giới hạn chi tiêu theo ngày**. Vẫn ghi số token và thời gian của mỗi việc để tính sau. Giữ các **trần kỹ thuật** để một việc không chạy lan: tối đa 6 bước, một vòng sửa, trần token mỗi lời gọi, thời gian chờ mỗi bước. Số liệu đo trước đây (24/09): một câu tra cứu khoảng 2 lời gọi, 5,5 đến 8 nghìn token vào, 13 đến 25 giây; nay có thêm lời gọi của điều phối và đối chiếu nên cao hơn, cần đo lại.

### 5.1 Bộ luật ẩn danh cho tra cứu (người dùng yêu cầu 23/11/2026)

Yêu cầu của người dùng: phần tra cứu luôn để mở mô hình thương mại, nhưng có **bộ luật** quy định cái gì được gửi ra: **không lấy tên người dùng hay dữ liệu cá nhân; chỉ lấy dấu hiệu bệnh, tình trạng gặp phải; ẩn danh toàn bộ; mô hình thương mại không được động vào dữ liệu thật của ca khám.**

**Nguyên tắc: xây câu gửi đi từ danh sách cho phép, không "lau sạch" văn bản.** Lau sạch (che tên, số điện thoại bằng mẫu) bỏ sót được; danh sách cho phép thì cái gì không được liệt kê sẽ không đi ra.

1. **Từ ca khám chỉ lấy các mệnh đề đã trích có loại thuộc danh sách cho phép:** triệu chứng, dấu hiệu, kết quả khám, bệnh hoặc tình trạng đã biết, **và thuốc kèm liều** (người dùng xác nhận 23/11/2026 là không ảnh hưởng). Lấy `noi_dung` và trường `thuoc` đã chuẩn hoá, **không lấy `trich_dan`, không lấy chữ trong hội thoại, không lấy chủ thể cụ thể** (chỉ ghi "người bệnh" hoặc "người nhà"). Không lấy tên, ngày cụ thể, địa chỉ, nơi làm việc, số liên lạc, mã hồ sơ, tên cơ sở, tên bác sĩ.
2. **Ngữ cảnh lâm sàng thô được gửi** (người dùng xác nhận 23/11/2026 là không ảnh hưởng): **nhóm tuổi** (sơ sinh, trẻ em, người lớn, cao tuổi), **giới**, **có thai hay không** và các tình trạng tương tự. **Không** gửi tuổi chính xác hay ngày sinh (người soạn giữ lại mức thô này; người dùng chưa nói về tuổi chính xác).
3. **Câu hỏi của bác sĩ** là chuỗi tự do duy nhất. Qua **máy phát hiện** trước khi gửi: chuỗi số dài, email, số điện thoại, dạng ngày, tên riêng đi sau từ xưng hô (ông, bà, anh, chị, bé, bệnh nhân) hay từ chỉ nơi. Phát hiện mà không che chắc chắn được thì **chặn và báo bác sĩ viết lại**, không đoán.
4. **Xem trước:** mọi việc tra cứu hiện đúng chuỗi sẽ gửi ra (có thể thu gọn) trong thẻ kế hoạch, để bác sĩ thấy chính xác cái gì đi ra.
5. **Điều phối, Tìm kiếm, Trả lời và phần xét ý của Đối chiếu chỉ nhận chuỗi này** (gọi là *ca ẩn danh*). Chúng **không bao giờ** nhận hội thoại, bản nháp, mệnh đề nguyên bản hay trích dẫn. Phần của Đối chiếu so ý trả lời với **các đoạn y văn công khai**, không so với ca khám.
6. **Mô hình ngoài không ghi được gì:** chỉ trả văn bản; không có công cụ ghi vào hồ sơ, ca khám hay cài đặt.
7. **Việc cần chính nội dung ca khám** ("bệnh nhân nói gì ở lượt 7", "bản nháp đã ghi thuốc nào") do **code tại chỗ** làm (tìm lượt, đọc mệnh đề), không gửi ra ngoài.

**Công tắc quản trị:** vì ẩn danh bằng luật không bảo đảm tuyệt đối (tổ hợp hiếm của dấu hiệu có thể gợi ra một người), cần một công tắc **tắt toàn hệ thống** cho người quản trị, mặc định bật theo yêu cầu của người dùng.

**Nhật ký:** mỗi lần gửi ghi tên tác tử, số ký tự, loại mệnh đề đã gửi và kết quả máy phát hiện; **không ghi chính chuỗi đã gửi** vào nhật ký dùng chung.

**Phép thử bắt buộc:** (a) ca có tên, số điện thoại, ngày sinh, địa chỉ trong hội thoại thì chuỗi gửi ra không chứa chúng (kiểm bằng chuỗi cụ thể); (b) mệnh đề loại ngoài danh sách (`trich_dan`, `chu_the` cụ thể, ngày, địa điểm) không đi ra, còn thuốc, liều, nhóm tuổi, giới và thai đi ra đúng khuôn; (c) câu hỏi chứa tên hoặc số dài bị chặn; (d) mô hình ngoài giả (kiểm thử) không nhận được trường nào ngoài danh sách cho phép; (e) công tắc quản trị tắt thì không có lời gọi ngoài nào.


## 6. Việc để người xây quyết

- Tên bước và chữ hiển thị của từng tác tử.
- Luật chọn tác tử cho câu hỏi tự do (bản đầu dùng luật, không gọi mô hình để phân loại, để tiết kiệm tiền).
- Cách tách `lookup-official` (đang là một khối lớn trong route) thành hàm nhận một hàm báo bước.
- Giá trị giới hạn hỏi mỗi ngày, thời gian chờ mỗi bước, và hình dạng chính xác của phản hồi trạng thái việc.
- Cách hiển thị bảng tác tử và thẻ tiến độ trong ngăn phải và trang Tra cứu.

## 7. Bổ sung sau khi người đọc thử hỏi

**Đã có câu trả lời trong dự án:**
- *Dữ liệu ca khám từ đâu:* **giao diện gửi kèm trong yêu cầu**, như `lookup-official` và `clinical-qa` đang làm (`transcript`, `draft`, thêm danh sách mệnh đề đã trích `propositions` cho hai tác tử luật tại chỗ). Trang "Tra cứu" không có ca khám thì các tác tử về ca khám bị bỏ qua và ghi rõ lý do. Hai tác tử luật tại chỗ làm trên mệnh đề đã trích (có cấu trúc), không đọc văn bản tự do.

**Quyết định của người soạn (người dùng chưa duyệt; sửa được):**
- *Bảng việc riêng:* việc trợ lý dùng **bảng và bộ chạy riêng** (`viec_tro_ly`), không dùng chung `viec_nen`, để không đụng hàng GPU và các phép thử của `generate-note`. Hàng này lưu cột `tien_trinh` (JSON các bước) và `ket_qua`.
- *Khởi động lại giữa chừng:* bước đã xong được **giữ và bỏ qua** khi chạy lại; lời gọi mô hình ngoài đã trả kết quả không gọi lại (không tốn tiền hai lần). Số lần chạy lại tối đa là 1 cho bước có gọi mô hình ngoài, 2 cho bước tại chỗ.
- *Công tắc mô hình ngoài tắt:* kiểm **theo từng tác tử**. Tác tử luật tại chỗ vẫn chạy; tác tử cần mô hình ngoài hiện "bỏ qua: chưa bật mô hình ngoài"; câu trả lời là câu trả lời một phần, không trả 403 cho cả câu hỏi.
- *Thiếu khoá cổng ngoài:* tác tử cần mô hình ngoài báo lỗi mềm (như mã 503 hiện tại), các tác tử còn lại vẫn chạy.
- *Điểm cuối:* thêm điểm cuối mới (`POST` và `GET /api/tro-ly`) **bên cạnh** các điểm cuối hiện có; các điểm cuối cũ giữ nguyên chữ ký. Khi tách `lookup-official` thành hàm thì route cũ gọi lại hàm đó.
- *Gộp câu trả lời:* mỗi tác tử trả một phần theo kiểu `TraLoiHoiDap` hiện có, kèm tên tác tử; giao diện hiện từng phần, nguồn không trộn lẫn giữa các tác tử.
- *Công tắc tác tử:* theo từng người dùng (không theo trang). Mặc định bật cả bốn; tác tử cần mô hình ngoài vẫn bị công tắc "Cho phép gửi ra mô hình ngoài" chặn.
- *Chọn tác tử cho câu hỏi tự do:* luật; nếu không luật nào khớp thì chạy "Tra cứu nguồn", và nếu có ca khám thì chạy thêm "Hỏi đáp về ca khám". Các tác tử chạy song song được.
- *Giới hạn mỗi ngày:* chưa đặt (người dùng chưa tính chi phí); chỉ ghi số token.

**Người dùng đã chốt (23/11/2026):** dùng cổng ai-box hiện có với `qwen3.8-flash`; chưa tính chuyện tiền; muốn có **điều phối** giao việc cho các tác tử tìm kiếm, trả lời, đối chiếu.

**Rủi ro cần người xây chú ý:** (1) điều phối do mô hình quyết nên có thể bịa tác tử hoặc kế hoạch quá dài, vì thế phải kiểm bằng danh sách trắng và trần; (2) qwen3.8-flash có bước suy nghĩ ẩn mà token suy nghĩ không bị `max_tokens` giới hạn (đo 23/09/2026), nên tắt suy nghĩ (`enable_thinking: false`, mặc định hiện nay) cho điều phối và đối chiếu; (3) câu trả lời cuối vẫn là của mô hình ngoài: nhãn `mo_hinh_ngoai` bắt buộc và không đưa vào bất kỳ phép đo nào của đề tài.


## 8. Ghi nhận sau khi xây (24/11/2026)

Các chỗ bản xây khác hoặc cụ thể hơn thiết kế (chi tiết và lý do ở sổ `docs/superpowers/plans/2026-11-23-tro-ly-nhieu-tac-tu.ledger.md`):
- Người nhận chuỗi ngoài: ngoài Điều phối, Tìm kiếm, Trả lời, phần xét ý của Đối chiếu, bước **soạn lại** của Đối chiếu cũng chỉ nhận ca ẩn danh. Lời nhắc soạn câu trả lời khi ca đã ẩn danh không đòi số lượt hội thoại (không có để ghi).
- Điều phối **không** được tự xếp chính nó vào kế phác (`dieu_phoi` bị `kiemKePhach` từ chối như tác tử lạ).
- Kế phác dự phòng luôn có chuỗi tìm kiếm → trả lời → đối chiếu (nếu các tác tử đó đang bật); khi mô hình ngoài đóng, các bước hiện "bỏ qua: chưa bật mô hình ngoài" đúng như mục 5, thay vì vắng mặt.
- Hàng đợi `viec_tro_ly` giữ cả `tien_trinh` lẫn `dau` (kết quả trung gian) của từng bước; khởi động lại thì bước đã xong không gọi lại. Ngưỡng chạy lại: 1 với việc đã có bước gọi mô hình ngoài, 2 với việc chỉ tại chỗ.
- Mệnh đề vào `POST /api/tro-ly` được lọc còn `text, section, subject, negated, certainty, drug` trước khi lưu: trích dẫn và lượt thoại không bao giờ vào hàng đợi.
- Chờ trực tiếp của `POST /api/tro-ly` là 1,5 giây (đổi bằng `MEDITRACE_TRO_LY_CHO_MS`).
- Trang "Hỏi ca khám" đầy đủ (EvidenceView) chưa chuyển sang trợ lý; chỉ ngăn phải của màn soạn.
- Giao diện chưa gửi tuổi, giới, có thai (chưa có trường có cấu trúc); máy chủ đã nhận `nguCanh` và đổi tuổi thành nhóm tuổi tại chỗ.
