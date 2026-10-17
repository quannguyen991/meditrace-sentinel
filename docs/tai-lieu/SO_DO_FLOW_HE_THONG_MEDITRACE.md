# BỘ 7 SƠ ĐỒ LƯU ĐỒ XỬ LÝ & QUY TRÌNH KIỂM THỬ HỆ THỐNG MEDITRACE SENTINEL

Tài liệu này tổng hợp và giải thích chi tiết **Bộ 7 Sơ đồ lưu đồ quy trình xử lý và minh chứng kiểm thử** của hệ thống MediTrace Sentinel. Tất cả các sơ đồ được thiết kế theo tỷ lệ **16:9 Full HD (3840 x 2160 pixels @ 200 DPI)** theo chuẩn đồ họa kỹ thuật y tế công nghệ cao (Medical-Tech Infographic), sử dụng thuật ngữ khoa học, kỹ thuật và y tế chuẩn xác, diễn đạt trực tiếp, dễ hiểu, không dùng từ ngữ ẩn dụ, hoán dụ hay giật gân, phù hợp để trình bày trước Hội đồng Giám khảo hoặc đưa vào hồ sơ nghiệm thu khoa học.

Toàn bộ ảnh gốc độ phân giải cao đã được lưu đồng thời tại:
- **Thư mục tài liệu dự án:** `docs/tai-lieu/hinh/`
- **Thư mục Downloads:** `C:\Users\admin\Downloads\hinh_flow_meditrace\`
- **Màn hình Desktop:** `C:\Users\admin\Desktop\Hinh_Flow_MediTrace\`

---

## MỤC LỤC BỘ 7 SƠ ĐỒ MASTER FLOW

1. [Flow 1: Thu âm, phiên âm tiếng nói (ASR) & Trích xuất thông tin cấu trúc (JSON)](#flow-1-thu-âm-phiên-âm-tiếng-nói-asr--trích-xuất-thông-tin-cấu-trúc-json)
2. [Flow 2: Xử lý đính chính lời nói, lọc câu giả định & Dựng bệnh án SOAP](#flow-2-xử-lý-đính-chính-lời-nói-lọc-câu-giả-định--dựng-bệnh-án-soap)
3. [Flow 3: Quy trình kiểm tra tự động 7 bước (K1–K7) — Loại bỏ thông tin sai lệch](#flow-3-quy-trình-kiểm-tra-tự-động-7-bước-k1k7--loại-bỏ-thông-tin-sai-lệch)
4. [Flow 4: Kiểm soát an toàn đơn thuốc, hiệu chỉnh liều và tính điểm lâm sàng (CDSS)](#flow-4-kiểm-soát-an-toàn-đơn-thuốc-hiệu-chỉnh-liều-và-tính-điểm-lâm-sàng-cdss)
5. [Flow 5: So sánh phương pháp xử lý: Mô hình ngôn ngữ tự do (ChatGPT) vs. Hệ thống MediTrace Sentinel](#flow-5-so-sánh-phương-pháp-xử-lý-mô-hình-ngôn-ngữ-tự-do-chatgpt-vs-hệ-thống-meditrace-sentinel)
6. [Flow 6: Dữ liệu thực nghiệm và quy trình kiểm thử tự động (1.330 trường hợp kiểm thử)](#flow-6-dữ-liệu-thực-nghiệm-và-quy-trình-kiểm-thử-tự-động-1330-trường-hợp-kiểm-thử)
7. [Flow 7: Quy trình bác sĩ sử dụng hệ thống trong ca khám bệnh (< 60 giây thao tác)](#flow-7-quy-trình-bác-sĩ-sử-dụng-hệ-thống-trong-ca-khám-bệnh--60-giây-thao-tác)

---

### Flow 1: THU ÂM, PHIÊN ÂM TIẾNG NÓI (ASR) & TRÍCH XUẤT THÔNG TIN CẤU TRÚC (JSON)
- **Tên file ảnh:** `flow-1-nhan-dien-giong-noi-va-rut-tin.png`
- **Phân tầng:** Bước 0 (Thu âm & ASR) & Tầng 1 (Local LLM Qwen3-4B QLoRA)
- **Ý nghĩa kỹ thuật và lâm sàng:**
  1. **Thu âm tại phòng khám:** Thời lượng 3–5 phút cho mỗi ca khám ngoại trú, xử lý hoàn toàn tại chỗ (On-premise) trên máy tính phòng khám, tuân thủ bảo mật thông tin y tế theo Nghị định 13/2023/NĐ-CP.
  2. **Chuyển tiếng nói thành văn bản (PhoWhisper) & Phân tách người nói (PyAnnote):** Phân biệt giọng nói người 1, người 2, người 3 (Bác sĩ, Bệnh nhân, Người nhà đi cùng) và đánh số thứ tự câu thoại `[T1]`, `[T2]`... làm căn cứ lưu vết nguồn gốc thông tin.
  3. **Nhận diện tên thuốc & Cơ chế Bôi đỏ cảnh báo:** Phòng khám có tiếng ồn; người bệnh có thể phát âm chưa chuẩn hoặc dùng tên gọi dân gian (*"a móc"*, *"ô mê"*, viên nhộng đỏ vàng...). Nhận dạng giọng nói (ASR) không thể đảm bảo chính xác 100% tên thuốc. Hệ thống áp dụng quy tắc: **Không tự ý suy đoán sửa tên thuốc**. Mọi gợi ý nhận diện tên thuốc đều **BẮT BUỘC BÔI ĐỎ** và chuyển vào mục `[CẦN BÁC SĨ XÁC NHẬN]`.
  4. **Trích xuất thông tin có cấu trúc (JSON):** Mô hình AI chạy cục bộ (Qwen3-4B) chỉ được phép trích xuất các trường dữ liệu theo định dạng JSON xác định, không cho phép viết văn tự do (để tránh sai lệch nội dung). Mỗi mẩu tin trích xuất bắt buộc phải gắn với mã số câu thoại gốc `[Ti]`.
  5. **Phân biệt vai trò người nói:** Tự động nhận diện các đại từ nhân xưng tiếng Việt (*"mẹ tôi"*, *"bố tôi"*, *"bé nhà em"*...), phân luồng thông tin bệnh của người nhà sang mục Tiền sử gia đình, tránh ghi nhầm vào bệnh sử của bệnh nhân chính.

---

### Flow 2: XỬ LÝ ĐÍNH CHÍNH LỜI NÓI, LỌC CÂU GIẢ ĐỊNH & DỰNG BỆNH ÁN SOAP
- **Tên file ảnh:** `flow-2-dinh-chinh-fsm-va-benh-an-soap.png`
- **Phân tầng:** Tầng 2 (Ẩn danh hóa & Phân nhóm chủ thể), Tầng 3 (Xử lý đính chính) & Tầng 5 (Thiết lập bệnh án SOAP)
- **Ý nghĩa kỹ thuật và lâm sàng:**
  1. **Phân nhóm chủ thể & Ẩn danh hóa:** Xử lý các câu nói thiếu chủ ngữ trong giao tiếp tiếng Việt, tự động che thông tin cá nhân (họ tên, CCCD, số điện thoại, địa chỉ) thành mã ẩn danh `[BENH_NHAN_001]`.
  2. **Xử lý khi người nói đính chính câu từ:** Khi bệnh nhân nói nhầm rồi tự sửa lại (*"Sốt 1 tuần... à không, mới 3 hôm thôi"*), hệ thống tự động phân loại: gạch bỏ thông tin cũ `[Bị thay thế]`, chỉ đưa thông tin mới `3 hôm` vào hồ sơ bệnh án. Giúp giảm 14 lần lỗi do lưu giữ thông tin cũ đã bị sửa (từ 11.5% xuống còn 0.8%).
  3. **Lọc câu dặn dò tương lai và giả định:** Khi bác sĩ dặn dò (*"Nếu ngày mai còn sốt thì chụp X-quang"*), hệ thống nhận diện đây là câu điều kiện tương lai, không ghi vào mục Khám lâm sàng hay Chẩn đoán, mà chuyển chính xác vào mục Kế hoạch theo dõi.
  4. **Thiết lập bệnh án theo mẫu chuẩn SOAP:** Bệnh án được sắp xếp tự động thành 4 phần chuẩn y khoa: S (Subjective - Bệnh sử, Tiền sử), O (Objective - Khám thực thể, Dấu hiệu sinh tồn), A (Assessment - Chẩn đoán), P (Plan - Kế hoạch điều trị, Đơn thuốc). Toàn bộ nội dung nghi ngờ đều được gom vào mục riêng để bác sĩ kiểm tra, đồng thời có thể bấm vào từng câu để nghe lại đoạn âm thanh gốc tương ứng.

---

### Flow 3: QUY TRÌNH KIỂM TRA TỰ ĐỘNG 7 BƯỚC (K1–K7) — LOẠI BỎ THÔNG TIN SAI LỆCH
- **Tên file ảnh:** `flow-3-khoa-bang-chung-k1-k7-chong-ao-giac.png`
- **Phân tầng:** Tầng 4 (Quy trình kiểm định logic xác định 100% bằng thuật toán)
- **Ý nghĩa kỹ thuật và lâm sàng:**
  1. Mọi thông tin do mô hình AI trích xuất **bắt buộc phải đi qua quy trình kiểm tra 7 bước**:
     - **Bước K1 (Kiểm tra trong lời thoại gốc):** Dò chuỗi trích dẫn nguyên văn trong câu thoại nguồn `[Ti]`. Tên thuốc nhận diện chưa chắc chắn $\rightarrow$ Bôi đỏ chuyển sang mục Chờ bác sĩ xác nhận.
     - **Bước K2 (Kiểm tra thuật ngữ y khoa):** So khớp từ ngữ y tế chính giữa đoạn trích dẫn và nội dung tóm tắt để tránh tóm tắt sai lệch.
     - **Bước K3 (Xác minh người nói):** Kiểm tra đại từ chỉ người, ngăn chặn việc gán triệu chứng của người nhà vào bệnh sử bệnh nhân.
     - **Bước K4 (Lọc câu giả định tương lai):** Ngăn chặn việc ghi nhận các câu dặn dò, phòng ngừa thành việc đã thực hiện.
     - **Bước K5 (Đối chiếu mốc thời gian):** Kiểm tra mốc thời gian (*"3 ngày"*, *"1 tuần"*) có xuất hiện chính xác trong lượt thoại được dẫn chứng hay không.
     - **Bước K6 (Kiểm tra chữ số lâm sàng và liều lượng):** Đối chiếu từng con số huyết áp, nhiệt độ, liều thuốc mg. Chặn ngay việc mô hình AI tự ý điền các con số thói quen (ví dụ tự điền 120/80 mmHg).
     - **Bước K7 (Cập nhật thông tin đính chính):** Loại bỏ thông tin cũ đã bị câu nói sau thay thế.
  2. **Hai nhánh kết quả rõ ràng:**
     - `[OK] Vượt qua 7 Bước:` Đưa trực tiếp vào thân bệnh án SOAP với độ chính xác cao (kết quả đo đạc: 0.0% thông tin đúng bị chặn nhầm trên 30.136 dòng kiểm thử).
     - `[!] Có điểm nghi ngờ:` Không tự ý xóa bỏ mà BÔI ĐỎ cách ly vào mục "Cần Bác sĩ xác nhận" để bác sĩ xem xét và đưa ra quyết định.

---

### Flow 4: KIỂM SOÁT AN TOÀN ĐƠN THUỐC, HIỆU CHỈNH LIỀU VÀ TÍNH ĐIỂM LÂM SÀNG (CDSS)
- **Tên file ảnh:** `flow-4-duoc-ly-lam-sang-va-cdss-thang-diem.png`
- **Phân tầng:** Bước 5 (Kiểm tra an toàn đơn thuốc & Hệ thống hỗ trợ ra quyết định lâm sàng CDSS)
- **Ý nghĩa kỹ thuật và lâm sàng:**
  1. **Bước 1 - Tiếp nhận đơn & Dữ liệu đầu vào:** Bác sĩ kê đơn qua lời nói, bệnh nhân thông báo thuốc đang dùng tại nhà, kết quả xét nghiệm (Creatinine máu, tuổi, cân nặng). Mọi tên thuốc do bệnh nhân gọi theo thói quen dân gian đều được bôi đỏ cảnh báo.
  2. **Bước 2 - 3 Bước kiểm tra an toàn đơn thuốc:**
     - Kiểm tra tương tác thuốc bất lợi (DDI): Tra cứu Dược thư Quốc gia, phát hiện các cặp thuốc tương tác cần lưu ý (ví dụ: Warfarin + Aspirin gây tăng nguy cơ xuất huyết, Clopidogrel + Omeprazole làm giảm hiệu quả chống đông).
     - Kiểm soát liều tối đa trong ngày: Paracetamol $\le 4000\,\text{mg/ngày}$ (tối đa 8 viên 500mg), Ibuprofen $\le 2400\,\text{mg/ngày}$, Aspirin $\le 3000\,\text{mg/ngày}$. Hệ thống tự cộng dồn hoạt chất từ nhiều nguồn và cảnh báo nếu vượt ngưỡng.
     - Hiệu chỉnh liều theo chức năng thận: Tự động tính mức lọc cầu thận Cockcroft-Gault (eGFR) từ nồng độ Creatinine máu. Khi eGFR $< 30\,\text{mL/phút}$, đưa ra khuyến cáo giảm liều kháng sinh và cảnh báo thuốc cần thận trọng.
  3. **Bước 3 - Tự động tính 9 thang điểm lâm sàng (CDSS):** Hỗ trợ tính tự động các thang điểm: GCS, qSOFA, CURB-65, CHA2DS2-VASc, HAS-BLED, Wells Score, Glasgow-Blatchford, NYHA I-IV, BMI Châu Á.
  4. **Kết quả đầu ra:** Bảng cảnh báo hiển thị rõ ràng trên màn hình bác sĩ trong 1 giây + Phiếu hướng dẫn dùng thuốc cho bệnh nhân chia theo 4 khung giờ trong ngày (Sáng - Trưa - Chiều - Tối) kèm các dấu hiệu cảnh báo cần quay lại viện ngay.

---

### Flow 5: SO SÁNH PHƯƠNG PHÁP XỬ LÝ: MÔ HÌNH NGÔN NGỮ TỰ DO (CHATGPT) vs. HỆ THỐNG MEDITRACE SENTINEL
- **Tên file ảnh:** `flow-5-so-sanh-doi-dau-chatgpt-vs-meditrace.png`
- **Phân tầng:** So sánh kiến trúc kỹ thuật và mức độ an toàn y tế
- **Ý nghĩa kỹ thuật và lâm sàng:**
  - **Phương pháp A (Mô hình AI đám mây tạo sinh tự do - End-to-End):**
    - Chuyển dữ liệu bệnh nhân lên máy chủ đám mây bên ngoài (cần lưu ý tuân thủ quy định bảo vệ dữ liệu y tế).
    - Tạo sinh câu chữ dựa trên xác suất thống kê, không có bước trung gian kiểm tra nguồn gốc từng câu trích dẫn, không có bộ quy tắc kiểm tra tương tác thuốc.
    - Hạn chế: Dễ sinh ra thông tin không có trong thực tế (tự điền số huyết áp, tiền sử bệnh), nhầm lẫn giữa lời kể của người nhà và bệnh nhân, giữ lại thông tin bệnh nhân đã đính chính, nhầm câu dặn dò tương lai thành việc đã làm, khó truy cứu lại nguồn gốc câu nói.
  - **Phương pháp B (Hệ thống MediTrace Sentinel - Kết hợp AI và kiểm tra logic đa tầng):**
    - Vận hành 100% tại chỗ (On-premise) trên máy tính phòng khám, bảo mật thông tin nội bộ.
    - AI chỉ trích xuất dữ liệu có cấu trúc JSON kèm mã số câu thoại gốc; toàn bộ nội dung đều đi qua 5 tầng kiểm tra logic độc lập.
    - Kết quả đạt được: Loại bỏ thông tin suy diễn không có trong lời thoại, giảm 6 lần tỷ lệ nhầm triệu chứng người nhà (từ 12.4% xuống 2.1%), giảm 14 lần lỗi nhớ nhầm thông tin cũ (từ 11.5% xuống 0.8%), hỗ trợ bấm xem lại âm thanh gốc tức thì, tự động kiểm tra tương tác thuốc và liều lượng, tiết kiệm 5–7 phút ghi chép cho mỗi ca khám.

---

### Flow 6: DỮ LIỆU THỰC NGHIỆM VÀ QUY TRÌNH KIỂM THỬ TỰ ĐỘNG (1.330 TRƯỜNG HỢP KIỂM THỬ)
- **Tên file ảnh:** `flow-6-duong-ong-kiem-thu-thuc-nghiem-1330-test.png`
- **Phân tầng:** Quy trình thẩm định chất lượng và kiểm thử hồi quy CI/CD
- **Ý nghĩa kỹ thuật và lâm sàng:**
  1. **Tập dữ liệu đánh giá độc lập:**
     - 200 khuôn ca bệnh độc lập (Template-Disjoint) bao phủ 10 chuyên khoa; toàn bộ là các ca bệnh mà mô hình AI chưa từng gặp trong quá trình huấn luyện (đảm bảo tính khách quan).
     - 5.000 đoạn hội thoại mô phỏng với độ phong phú từ vựng đạt 78.3%.
     - 300 ca thử nghiệm bẫy sai sót (Adversarial Testing) hoán đổi người nói, đính chính thời gian và chèn tiếng ồn môi trường.
  2. **Hệ thống 1.330 bài kiểm thử tự động (CI/CD Pipeline):**
     - Nhóm 0: Nhận dạng âm thanh và từ điển tên thuốc (62 tests)
     - Nhóm 1: Trích xuất thông tin JSON có cấu trúc (145 tests)
     - Nhóm 2: Phân biệt người nói và bảo mật thông tin theo NĐ 13 (120 tests)
     - Nhóm 3: Xử lý đính chính và lọc câu giả định (98 tests)
     - Nhóm 4: Quy trình kiểm tra logic 7 bước K1–K7 (280 tests)
     - Nhóm 5: Kiểm tra an toàn thuốc và 9 thang điểm lâm sàng (310 tests)
     - Nhóm Tích hợp hệ thống và bảo mật (315 tests)
  3. **Kết quả đo đạc thực nghiệm:**
     - Độ chính xác trích xuất đúng nguồn (Attribution F1) tăng từ 66.1% lên 70.8% (+4.7%).
     - Tỷ lệ lỗi gán thuộc tính (Slot Error Rate) giảm từ 45.4% xuống 36.9% (-8.5%).
     - Tỷ lệ bỏ sót dị ứng thuốc: 0.0% (toàn bộ cảnh báo dị ứng đều được ghi nhận).
     - Tỷ lệ thông tin đúng bị chặn nhầm: 0.0% (0 / 30.136 dòng kiểm thử).
     - **1.330 / 1.330 TRƯỜNG HỢP KIỂM THỬ ĐẠT KẾT QUẢ THÀNH CÔNG (100%) TRONG ĐƯỜNG ỐNG CI/CD.**

---

### Flow 7: QUY TRÌNH BÁC SĨ SỬ DỤNG HỆ THỐNG TRONG CA KHÁM BỆNH (< 60 GIÂY THAO TÁC)
- **Tên file ảnh:** `flow-7-quy-trinh-bac-si-kham-va-click-to-verify.png`
- **Phân tầng:** Quy trình tương tác thực tế của bác sĩ tại phòng khám (Human-in-the-Loop)
- **Ý nghĩa kỹ thuật và lâm sàng:**
  1. **Bước 01 [ 0 GIÂY THAO TÁC ]:** Bác sĩ bấm 1 nút "Bắt đầu khám" trên màn hình, hệ thống bắt đầu tiếp nhận âm thanh; bác sĩ tập trung hoàn toàn vào việc giao tiếp, hỏi bệnh và thăm khám cho người bệnh mà không cần vừa khám vừa gõ phím.
  2. **Bước 02 [ 30s CÓ BẢN NHÁP ]:** Khi kết thúc lượt khám, chỉ sau khoảng 30–45 giây xử lý tự động, bản nháp bệnh án chuẩn SOAP hoàn chỉnh đã được chuẩn bị sẵn trên màn hình kèm số thứ tự câu thoại `[Ti]` trong đoạn ghi âm.
  3. **Bước 03 [ 20s RÀ SOÁT CẢNH BÁO ]:** Bác sĩ xem nhanh mục "CẦN BÁC SĨ XÁC NHẬN" để kiểm tra các nội dung được bôi đỏ (gợi ý tên thuốc nhận diện chưa chắc chắn, cảnh báo tương tác thuốc, thông tin bệnh nhân đã tự sửa lại).
  4. **Bước 04 [ 1s NGHE ĐỐI SOÁT ]:** Đối với thông tin cần nghe lại để đối chứng, bác sĩ bấm vào số thứ tự câu thoại, hệ thống phát lại ngay đoạn âm thanh 2 giây bệnh nhân nói để đối soát và xác nhận trực tiếp trong 1 giây.
  5. **Bước 05 [ TIẾT KIỆM 5-7 PHÚT ]:** Bác sĩ bấm nút "Ký duyệt", hệ thống niêm phong dữ liệu (mã hóa SHA-256), chuyển vào phần mềm bệnh viện (EMR) và in ngay Phiếu hướng dẫn dùng thuốc trao tận tay người bệnh.
  - **TỔNG KẾT:** Bác sĩ chỉ mất dưới 60 giây thao tác trên màn hình — Tiết kiệm 5–7 phút ghi chép cho mỗi lượt khám!
