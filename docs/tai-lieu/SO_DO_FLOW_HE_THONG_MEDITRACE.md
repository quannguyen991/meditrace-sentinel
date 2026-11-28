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
6. [Flow 6: Dữ liệu thực nghiệm và quy trình kiểm thử tự động](#flow-6-dữ-liệu-thực-nghiệm-và-quy-trình-kiểm-thử-tự-động)
7. [Flow 7: Quy trình bác sĩ sử dụng hệ thống trong ca khám bệnh](#flow-7-quy-trình-bác-sĩ-sử-dụng-hệ-thống-trong-ca-khám-bệnh)

---

### Flow 1: THU ÂM, PHIÊN ÂM TIẾNG NÓI (ASR) & TRÍCH XUẤT THÔNG TIN CẤU TRÚC (JSON)
- **Tên file ảnh:** `flow-1-nhan-dien-giong-noi-va-rut-tin.png`
- **Phân tầng:** Bước 0 (Thu âm & ASR) & Tầng 1 (Local LLM Qwen3-4B QLoRA)
- **Ý nghĩa kỹ thuật và lâm sàng:**
  1. **Thu âm tại phòng khám:** Thời lượng 3–5 phút cho mỗi ca khám ngoại trú, xử lý hoàn toàn tại chỗ (On-premise) trên máy tính phòng khám, nên dữ liệu người bệnh không cần rời phòng khám (khung pháp lý hiện hành: Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 và Nghị định 356/2025/NĐ-CP, hiệu lực 01/01/2026).
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
  2. **Xử lý khi người nói đính chính câu từ:** Khi bệnh nhân nói nhầm rồi tự sửa lại (*"Sốt 1 tuần... à không, mới 3 hôm thôi"*), hệ thống tự động phân loại: gạch bỏ thông tin cũ `[Bị thay thế]`, chỉ đưa thông tin mới `3 hôm` vào hồ sơ bệnh án. Đo trên bộ đính chính 60 ca: tỷ lệ thông tin cũ đã bị sửa nhưng vẫn còn trong bản nháp giảm từ 11,48% xuống 0,80% (mẫu 240 ca tập phát triển: 5,21% xuống 0,36%; nguồn `README.md`, `docs/final/Báo cáo dự án.md` mục 4.2).
  3. **Lọc câu dặn dò tương lai và giả định:** Khi bác sĩ dặn dò (*"Nếu ngày mai còn sốt thì chụp X-quang"*), hệ thống nhận diện đây là câu điều kiện tương lai, không ghi vào mục Khám lâm sàng hay Chẩn đoán, mà chuyển chính xác vào mục Kế hoạch theo dõi.
  4. **Thiết lập bệnh án theo mẫu chuẩn SOAP:** Bệnh án được sắp xếp tự động thành 4 phần chuẩn y khoa: S (Subjective - Bệnh sử, Tiền sử), O (Objective - Khám thực thể, Dấu hiệu sinh tồn), A (Assessment - Chẩn đoán), P (Plan - Kế hoạch điều trị, Đơn thuốc). Toàn bộ nội dung nghi ngờ đều được gom vào mục riêng để bác sĩ kiểm tra, đồng thời có thể bấm vào từng câu để nghe lại đoạn âm thanh gốc tương ứng.

---

### Flow 3: QUY TRÌNH KIỂM TRA TỰ ĐỘNG 7 BƯỚC (K1–K7) — LOẠI BỎ THÔNG TIN SAI LỆCH
- **Tên file ảnh:** `flow-3-khoa-bang-chung-k1-k7-chong-ao-giac.png`
- **Phân tầng:** Tầng 4 (Quy trình kiểm định logic xác định bằng thuật toán)
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
     - `[OK] Vượt qua 7 Bước:` Đưa vào thân bệnh án SOAP. Trên đáp án mô phỏng, 0/30.136 dòng đúng bị chặn nhầm, nhưng số này chỉ đúng vì đáp án chép gần nguyên văn hội thoại (độ phủ 0,95). Trên đầu ra mô hình thật, chặn thừa là 8,0% (chính sách C) / 10,0% (chính sách D), và lỗi nguy hiểm vẫn lọt vào thân 11,8% với chính sách D, đo trên các tập phát triển đã dùng để chỉnh luật (`docs/ket-qua/canh-bao.json`).
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
  4. **Kết quả đầu ra:** Bảng cảnh báo hiển thị trên màn hình bác sĩ (các bước theo luật chạy dưới một giây, `README.md`) + Phiếu hướng dẫn dùng thuốc cho bệnh nhân chia theo 4 khung giờ trong ngày (Sáng - Trưa - Chiều - Tối) kèm các dấu hiệu cảnh báo cần quay lại viện ngay.

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
    - Kết quả đo được (so với nhánh chỉ tách thông tin, cùng mô hình nhỏ): ghi nhầm người giảm từ 22,0% xuống 17,9% và F1 tăng từ 66,1 lên 70,8 ở bộ đổi chủ thể 80 ca; thông tin cũ đã bị sửa còn trong bản nháp giảm từ 11,48% xuống 0,80% ở bộ đính chính 60 ca. Thời gian tiết kiệm cho bác sĩ: **chưa đo**.
  - **Kết quả không có lợi, phải nói cùng:**
    - Dự án **chưa chạy so sánh đầy đủ** với mô hình thương mại. Phép đo duy nhất (173/300 ca): mô hình thương mại ghi nhầm người **ít hơn** mô hình của dự án, 1,4% so với 7,6% ở bộ đính chính. Kế hoạch đo: `docs/superpowers/plans/2026-11-27-nang-cap-toan-dien-bgk.md` Task 6.
    - Cách để mô hình nhỏ viết thẳng bản nháp ghi đúng người **cao hơn** đường ống (0,939 so với 0,748 ở bộ đổi chủ thể). Điểm mạnh của MediTrace là kiểm tra được từng dòng, không phải chính xác hơn.

---

### Flow 6: DỮ LIỆU THỰC NGHIỆM VÀ QUY TRÌNH KIỂM THỬ TỰ ĐỘNG
- **Tên file ảnh:** `flow-6-duong-ong-kiem-thu-thuc-nghiem-1330-test.png`
- **Phân tầng:** Quy trình thẩm định chất lượng và kiểm thử hồi quy CI/CD
- **Ý nghĩa kỹ thuật và lâm sàng:**
  1. **Tập dữ liệu đánh giá độc lập:**
     - 657 khuôn ca bệnh bao phủ 21 hệ cơ quan, chia theo khuôn 515 Train / 72 Dev / 70 Test để mô hình không nhìn thấy bài kiểm tra trước lúc đánh giá.
     - 5.000 đoạn hội thoại mô phỏng thế hệ v2 đạt 45.835 câu duy nhất (+127% so với v1), tỷ lệ lặp giảm từ 76,92% xuống 47,37% (câu $\ge 8$ từ: 42,19%), MTLD đạt 145,4, Distinct-2 đạt 0,0468, 100% trích dẫn trong dữ liệu tự sinh là chuỗi con nguyên văn (52.634/52.634; đây là kiểm dữ liệu huấn luyện, không phải đầu ra mô hình) và 0 lỗi theo 6 quy tắc câu.
     - 300 ca thử nghiệm bẫy sai sót (Adversarial Testing) hoán đổi người nói, đính chính thời gian và chèn tiếng ồn môi trường.
  2. **Bộ kiểm thử tự động (lần chạy 26/11/2026, `README.md`):** 1.942 bài `pytest` qua, 27 bỏ qua theo môi trường phần cứng; 96 bài kiểm thử TypeScript (`web/`) qua. Các bài này kiểm tra mã chạy đúng trên ca do nhóm tự viết, không phải độ chính xác trên dữ liệu thật.
  3. **Kết quả đo đạc thực nghiệm:**
     - F1 tăng từ 66,1% lên 70,8%, tỷ lệ lỗi theo ô (SER) giảm từ 45,4% xuống 36,9%, ghi nhầm người giảm từ 22,0% xuống 17,9% (bộ đổi chủ thể 80 ca).
     - Tỷ lệ bỏ sót mệnh đề: 43,1% (chưa huấn luyện) xuống 11,5% (có adapter), 30 ca tập phát triển, so với bộ chấm tự động.
     - Tỷ lệ bỏ sót dị ứng: **chưa đo riêng**. Lớp cảnh báo bỏ sót chung chỉ phủ 12% mệnh đề bị sót (`docs/ket-qua/canh-bao.json`).
     - Chặn nhầm 0/30.136 dòng trên đáp án mô phỏng (chỉ đúng vì đáp án chép gần nguyên văn hội thoại, độ phủ 0,95); trên đầu ra mô hình thật chặn thừa 8,0–10,0%.

---

### Flow 7: QUY TRÌNH BÁC SĨ SỬ DỤNG HỆ THỐNG TRONG CA KHÁM BỆNH
- **Tên file ảnh:** `flow-7-quy-trinh-bac-si-kham-va-click-to-verify.png`
- **Phân tầng:** Quy trình tương tác thực tế của bác sĩ tại phòng khám (Human-in-the-Loop)
- **Ý nghĩa kỹ thuật và lâm sàng:**
  1. **Bước 01 [ BẮT ĐẦU KHÁM ]:** Bác sĩ bấm 1 nút "Bắt đầu khám" trên màn hình, hệ thống bắt đầu tiếp nhận âm thanh; bác sĩ tập trung hoàn toàn vào việc giao tiếp, hỏi bệnh và thăm khám cho người bệnh mà không cần vừa khám vừa gõ phím.
  2. **Bước 02 [ CÓ BẢN NHÁP ]:** Khi kết thúc lượt khám, sau khoảng 3,5 phút xử lý trên một card RTX 3060 (`README.md`; chạy nền nên bác sĩ khám ca tiếp theo trong lúc chờ), bản nháp bệnh án chuẩn SOAP hoàn chỉnh đã được chuẩn bị sẵn trên màn hình kèm số thứ tự câu thoại `[Ti]` trong đoạn ghi âm.
  3. **Bước 03 [ RÀ SOÁT CẢNH BÁO ]:** Bác sĩ xem nhanh mục "CẦN BÁC SĨ XÁC NHẬN" để kiểm tra các nội dung được bôi đỏ (gợi ý tên thuốc nhận diện chưa chắc chắn, cảnh báo tương tác thuốc, thông tin bệnh nhân đã tự sửa lại).
  4. **Bước 04 [ NGHE ĐỐI SOÁT ]:** Đối với thông tin cần nghe lại để đối chứng, bác sĩ bấm vào số thứ tự câu thoại, hệ thống phát lại đúng đoạn âm thanh bệnh nhân nói để đối soát và xác nhận.
  5. **Bước 05 [ KÝ DUYỆT ]:** Bác sĩ bấm nút "Ký duyệt", hệ thống niêm phong dữ liệu (mã hóa SHA-256), chuyển vào phần mềm bệnh viện (EMR) và in ngay Phiếu hướng dẫn dùng thuốc trao tận tay người bệnh.
  - **Lưu ý:** Thời gian thao tác và thời gian tiết kiệm của bác sĩ **chưa đo**; dự án chưa thử với bác sĩ thật. Kế hoạch đo: `docs/superpowers/plans/2026-11-27-nang-cap-toan-dien-bgk.md` Task 9.
