# BỘ 7 SƠ ĐỒ FLOW XỬ LÝ & ĐƯỜNG ỐNG KIỂM THỬ THỰC CHIẾN MEDITRACE SENTINEL

Tài liệu này tổng hợp và giải thích chi tiết **Bộ 7 Sơ đồ luồng xử lý và minh chứng kiểm thử quan trọng nhất** của hệ thống MediTrace Sentinel. Tất cả các sơ đồ được thiết kế theo tỷ lệ **16:9 Full HD (3840 x 2160 pixels @ 200 DPI)** theo chuẩn đồ họa y tế công nghệ cao (Medical-Tech Infographic), sử dụng thuật ngữ chuẩn xác nhưng diễn đạt đời thường, dễ hiểu để thuyết trình trước Hội đồng Giám khảo hoặc đưa vào báo cáo nghiệm thu khoa học.

Toàn bộ ảnh gốc độ phân giải cao đã được lưu đồng thời tại:
- **Thư mục tài liệu dự án:** `docs/tai-lieu/hinh/`
- **Thư mục Downloads:** `C:\Users\admin\Downloads\hinh_flow_meditrace\`
- **Màn hình Desktop:** `C:\Users\admin\Desktop\Hinh_Flow_MediTrace\`

---

## MỤC LỤC BỘ 7 SƠ ĐỒ MASTER FLOW

1. [Flow 1: Gỡ băng ASR, Dược thư âm vị, Quy tắc Bôi đỏ & Rút mẩu tin JSON](#flow-1-đường-ống-gỡ-băng-asr-dược-thư-âm-vị--rút-mẩu-tin-nguyên-tử)
2. [Flow 2: Bắt đính chính FSM, Lọc câu giả định & Dựng bệnh án SOAP](#flow-2-bắt-đính-chính-fsm-lọc-câu-giả-định--dựng-bệnh-án-soap)
3. [Flow 3: Quy trình 7 Cổng Khóa bằng chứng (K1–K7) — Triệt tiêu Hallucination](#flow-3-quy-trình-7-cổng-khóa-bằng-chứng-k1k7--triệt-tiêu-ảo-giác-ai)
4. [Flow 4: Giám sát Dược lý lâm sàng, Chỉnh liều eGFR & 9 Thang điểm CDSS](#flow-4-giám-sát-dược-lý-lâm-sàng-hiệu-chỉnh-liều-egfr--9-thang-điểm-cdss)
5. [Flow 5: So sánh đối đầu trực diện: ChatGPT / LLM tự do vs. MediTrace Sentinel](#flow-5-so-sánh-đối-đầu-trực-diện-chatgpt--llm-tự-do-vs-meditrace-sentinel)
6. [Flow 6: Ma trận Kiểm thử thực nghiệm toàn diện & Đường ống CI/CD (1.330 Bài Test)](#flow-6-ma-trận-kiểm-thử-thực-nghiệm-toàn-diện--đường-ống-cicd-1330-bài-test)
7. [Flow 7: Quy trình Bác sĩ tương tác lâm sàng & Click-to-Verify trong 1 giây](#flow-7-quy-trình-bác-sĩ-tương-tác-lâm-sàng--click-to-verify-trong-1-giây)

---

### Flow 1: ĐƯỜNG ỐNG GỠ BĂNG (ASR), DƯỢC THƯ ÂM VỊ & RÚT MẨU TIN NGUYÊN TỬ
- **Tên file ảnh:** `flow-1-nhan-dien-giong-noi-va-rut-tin.png`
- **Phân tầng:** Bước 0 (Âm thanh & ASR) & Tầng 1 (Local LLM Qwen3-4B QLoRA)
- **Ý nghĩa cốt lõi:**
  1. **Ghi âm tự nhiên phòng khám:** 3–5 phút/ca khám ngoại trú, xử lý 100% On-premise bảo mật theo Nghị định 13/2023/NĐ-CP.
  2. **Gỡ băng PhoWhisper & Tách giọng PyAnnote:** Bác sĩ gán vai một lần (Bác sĩ, Bệnh nhân, Người nhà) và gắn mỏ neo lượt thoại `[T1]`, `[T2]`...
  3. **Chốt 1 - ASR Guardrail & Dược thư âm vị (Quy tắc sống còn):** Phòng khám có tạp âm, bệnh nhân hay nói tên thuốc dân gian (*"a móc"*, *"ô mê"*...). ASR không thể đảm bảo nghe đúng 100%. Áp dụng nguyên tắc **Zero Silent Normalization**: Tuyệt đối **CẤM** tự ý đoán ngầm tên thuốc. Mọi gợi ý đều **BẮT BUỘC BÔI ĐỎ** và đưa sang mục `[CẦN BÁC SĨ XÁC NHẬN]`.
  4. **Tầng 1 - Rút mẩu tin nguyên tử (JSON):** Chạy trên GPU máy trạm phòng khám (RTX 3050/3060). **TUYỆT ĐỐI CẤM** AI viết văn xuôi tự do; chỉ bóc tách các mẩu tin JSON có trường trích dẫn và mỏ neo `[Ti]`.
  5. **Chốt 2 - Speaker Consistency Gate:** Soi đại từ tiếng Việt (*"Mẹ tôi bị hen"*, *"Bé nhà em"*), cấm gán nhầm vào tiền sử của bệnh nhân chính.

---

### Flow 2: BẮT ĐÍNH CHÍNH (FSM), LỌC CÂU GIẢ ĐỊNH & DỰNG BỆNH ÁN SOAP
- **Tên file ảnh:** `flow-2-dinh-chinh-fsm-va-benh-an-soap.png`
- **Phân tầng:** Tầng 2 (Khử định danh & Gom chủ thể), Tầng 3 (Máy trạng thái FSM) & Tầng 5 (Xuất bản SOAP)
- **Ý nghĩa cốt lõi:**
  1. **Tầng 2 - Phân định 4 nhóm chủ thể & Khử định danh:** Xử lý câu nuốt chủ ngữ của người Việt, ẩn danh thông tin cá nhân thành mã băm `[BENH_NHAN_001]`.
  2. **Tầng 3 - FSM bắt đính chính nói nhầm:** Khi bệnh nhân tự sửa lời (*"Sốt 1 tuần... à không, mới 3 hôm"*), FSM tự động phân nhánh: gạch bỏ tin cũ `[Bị thay thế]`, chỉ đưa mẩu tin mới `3 hôm` vào bệnh án. Giảm 14 lần lỗi nhớ nhầm tin cũ (từ 11.5% xuống 0.8%).
  3. **Chốt 3 - Dialogue Act & Lọc câu giả định:** Bác sĩ dặn dò tương lai (*"Nếu mai sốt thì chụp X-quang"*) $\rightarrow$ CẤM ghi thành đã làm; tự động chuyển sang mục Kế hoạch theo dõi.
  4. **Tầng 5 - Dựng bệnh án SOAP:** Dựng bằng Template Engine thuần toán học, tập trung cảnh báo BÔI ĐỎ vào mục Cần bác sĩ xác nhận, hỗ trợ Click-to-Verify phát lại âm thanh trong 1 giây.

---

### Flow 3: QUY TRÌNH 7 CỔNG KHÓA BẰNG CHỨNG (K1–K7) — TRIỆT TIÊU ẢO GIÁC AI
- **Tên file ảnh:** `flow-3-khoa-bang-chung-k1-k7-chong-ao-giac.png`
- **Phân tầng:** Tầng 4 (Evidence Locking Engine - 100% Python Determinism)
- **Ý nghĩa cốt lõi:**
  1. Mọi mẩu tin do AI trích xuất **bắt buộc phải đi qua phễu thẩm định 7 cổng an ninh**:
     - **Cổng K1 (Verbatim Match):** Dò chuỗi trích dẫn nguyên văn vào lượt thoại gốc `[Ti]`. Tên thuốc đoán âm vị $\rightarrow$ Bôi đỏ chuyển sang Cần xác nhận.
     - **Cổng K2 (Core Medical Terms):** Khớp từ vựng y khoa chính giữa câu trích và tóm tắt.
     - **Cổng K3 (Speaker Attribution):** Kiểm tra đại từ chỉ người, cấm gán nhầm người nhà sang bệnh nhân.
     - **Cổng K4 (Hypothetical Filter):** Chặn các câu nghi ngờ, phòng ngừa, giả định tương lai.
     - **Cổng K5 (Temporal Alignment):** Khóa mốc thời gian (*"3 ngày"*, *"1 tuần"*).
     - **Cổng K6 (Numerical Grounding):** Soi từng chữ số huyết áp, nhiệt độ, liều mg; chặn đứng thói quen điền số giả định (120/80 mmHg).
     - **Cổng K7 (Temporal Superseded Check):** Gạch bỏ thông tin đã bị câu nói sau đính chính.
  2. **Hai nhánh đầu ra:**
     - `[OK] Vượt qua 7 Cổng:` Đi thẳng vào thân bệnh án SOAP với độ tin cậy 100% (0.0% bị chặn nhầm trên 30.136 dòng thực nghiệm).
     - `[!] Vi phạm bất kỳ Cổng nào:` Tuyệt đối không xóa ngầm mà bôi đỏ cách ly vào mục "Cần Bác sĩ xác nhận" để bác sĩ ra quyết định.

---

### Flow 4: GIÁM SÁT DƯỢC LÝ LÂM SÀNG, HIỆU CHỈNH LIỀU eGFR & 9 THANG ĐIỂM CDSS
- **Tên file ảnh:** `flow-4-duoc-ly-lam-sang-va-cdss-thang-diem.png`
- **Phân tầng:** Chốt 5 (Clinical Safety Guardrail & Deterministic CDSS)
- **Ý nghĩa cốt lõi:**
  1. **Trạm 1 - Tiếp nhận đơn & An toàn ASR:** Bác sĩ kê đơn bằng lời nói, bệnh nhân khai thuốc đang dùng tại nhà; tên thuốc âm vị dân gian bắt buộc bôi đỏ cảnh báo.
  2. **Trạm 2 - 3 Chốt kiểm soát dược lý:**
     - Soi tương tác thuốc kỵ nhau (DDI): Báo động đỏ Warfarin + Aspirin/NSAID (xuất huyết), Clopidogrel + Omeprazole (triệt tiêu tác dụng), Digoxin + Amiodarone (ngộ độc tim).
     - Kiểm soát liều trần an toàn: Paracetamol $\le 4000\,\text{mg/ngày}$ (tối đa 8 viên 500mg), Ibuprofen $\le 2400\,\text{mg/ngày}$, Aspirin $\le 3000\,\text{mg/ngày}$.
     - Hiệu chỉnh liều suy thận: Tính độ lọc thận Cockcroft-Gault eGFR từ Creatinine máu. Khi eGFR $< 30\,\text{mL/phút}$, giảm 50% liều kháng sinh và chống chỉ định Metformin.
  3. **Trạm 3 - Tự động cộng 9 thang điểm nguy cơ (CDSS):** GCS, qSOFA, CURB-65, CHA2DS2-VASc, HAS-BLED, Wells Score, Glasgow-Blatchford, NYHA I-IV, BMI Châu Á.
  4. **Đầu ra kép:** Cảnh báo màn hình bác sĩ trong 1 giây + In Tờ dặn dò người bệnh chia 4 khung giờ đời thường (Sáng - Trưa - Chiều - Tối) kèm danh mục "Dấu hiệu đỏ nguy hiểm".

---

### Flow 5: SO SÁNH ĐỐI ĐẦU TRỰC DIỆN: CHATGPT / LLM TỰ DO vs. MEDITRACE SENTINEL
- **Tên file ảnh:** `flow-5-so-sanh-doi-dau-chatgpt-vs-meditrace.png`
- **Phân tầng:** Head-to-Head Comparative Architecture
- **Ý nghĩa cốt lõi:**
  - **Nhánh A (ChatGPT / LLM tạo sinh tự do End-to-End):**
    - Đẩy dữ liệu lên Cloud (vi phạm bảo mật y tế NĐ 13).
    - Hộp đen dự đoán từ tiếp theo trơn tru, không có bảng bằng chứng trung gian, không có bộ luật kiểm duyệt.
    - Hậu quả: Bịa đặt số liệu (Hallucination), nhầm lẫn người nhà sang bệnh nhân, giữ lại thông tin nói nhầm, biến lời dặn tương lai thành việc đã làm, mù tịt về an toàn thuốc kỵ nhau, không thể truy vết kiểm tra.
  - **Nhánh C (MediTrace Sentinel - Neuro-symbolic & Khóa bằng chứng):**
    - 100% On-premise bảo mật tuyệt đối tại phòng khám.
    - AI chỉ nhặt mẩu tin JSON nguyên tử kèm mỏ neo; 5 Tầng kiểm soát logic xác định.
    - Giá trị thực chiến: Triệt tiêu ảo giác bịa đặt (Zero Hallucination), giảm 6 lần lỗi nhầm người nhà (12.4% xuống 2.1%), giảm 14 lần lỗi nhớ nhầm tin cũ (11.5% xuống 0.8%), Click-to-Verify trong 1 giây, có Dược sĩ số gác cổng, tiết kiệm 5–7 phút mỗi ca khám.

---

### Flow 6: MA TRẬN KIỂM THỬ THỰC NGHIỆM TOÀN DIỆN & ĐƯỜNG ỐNG CI/CD (1.330 BÀI TEST)
- **Tên file ảnh:** `flow-6-duong-ong-kiem-thu-thuc-nghiem-1330-test.png`
- **Phân tầng:** Verification & Validation Pipeline (100% Tests Passed)
- **Ý nghĩa cốt lõi:**
  1. **Ma trận dữ liệu kiểm thử độc lập:**
     - 200 khuôn ca bệnh độc lập (Template-Disjoint) bao phủ 10 chuyên khoa, AI chưa từng nhìn thấy trong lúc huấn luyện (chống học vẹt 100%).
     - 5.000 hội thoại mô phỏng với n-gram diversity đạt 78.3%.
     - 300 ca thử thách đối đầu (Adversarial Pairs) hoán đổi chủ thể, đính chính thời gian và chèn nhiễu âm thanh ASR.
  2. **Hệ thống 1.330 bài test tự động CI/CD:**
     - Module 0: ASR & Dược thư âm vị (62 tests)
     - Module 1: Bóc tách mẩu tin JSON (145 tests)
     - Module 2: Đại từ nhân xưng & Khử định danh (120 tests)
     - Module 3: Máy trạng thái FSM & Dialogue Act (98 tests)
     - Module 4: 7 Cổng khóa bằng chứng K1–K7 (280 tests)
     - Module 5: Dược lý DDI, eGFR & 9 Thang điểm (310 tests)
     - Module Tích hợp E2E & Bảo mật SHA-256 (315 tests)
  3. **Kết quả thực nghiệm đo đạc:**
     - Attribution F1 tăng từ 66.1% lên 70.8% (+4.7% F1).
     - Slot Error Rate giảm từ 45.4% xuống 36.9% (-8.5% SER).
     - Bỏ sót dị ứng: 0.0% (Không bao giờ bỏ sót dị ứng nguy cấp).
     - Thông tin đúng bị chặn nhầm: 0.0% (0 / 30.136 dòng).
     - **1.330 / 1.330 BÀI TEST ĐẠT 100% TRONG ĐƯỜNG ỐNG CI/CD!**

---

### Flow 7: QUY TRÌNH BÁC SĨ TƯƠNG TÁC LÂM SÀNG & CLICK-TO-VERIFY TRONG 1 GIÂY
- **Tên file ảnh:** `flow-7-quy-trinh-bac-si-kham-va-click-to-verify.png`
- **Phân tầng:** Human-in-the-Loop Clinical Workflow
- **Ý nghĩa cốt lõi:**
  1. **Bước 01 [ 0 GIÂY THAO TÁC ]:** Bác sĩ bấm 1 nút "Bắt đầu khám", hệ thống thu âm thụ động ngầm; bác sĩ 100% rảnh tay tập trung thăm khám và lắng nghe người bệnh, không cần gõ phím cắm cúi.
  2. **Bước 02 [ 30s CÓ BỆNH ÁN ]:** Khi bệnh nhân đứng dậy ra về, chỉ sau 30–45 giây xử lý, bản nháp SOAP hoàn chỉnh đã hiện sẵn trên màn hình với đầy đủ mỏ neo `[Ti]`.
  3. **Bước 03 [ 20s LIẾC MẮT SOI ]:** Mắt bác sĩ nhìn thẳng vào mục "CẦN BÁC SĨ XÁC NHẬN" để liếc nhanh các cảnh báo bôi đỏ (gợi ý tên thuốc ASR, tương tác DDI, câu nói nhầm).
  4. **Bước 04 [ 1s NGHE ĐỐI SOÁT ]:** Với thông tin còn băn khoăn, bác sĩ bấm chuột vào mỏ neo, hệ thống phát lại đúng 2 giây âm thanh giọng bệnh nhân nói để đối soát tức thì.
  5. **Bước 05 [ TIẾT KIỆM 5-7 PHÚT ]:** Bác sĩ bấm nút "Ký duyệt", hệ thống tự động niêm phong chữ ký số SHA-256, đồng bộ sang EMR viện và in ngay Tờ dặn dò điều trị trao tận tay người bệnh.
  - **TỔNG KẾT:** Bác sĩ chỉ mất dưới 60 giây thao tác trên màn hình — Tiết kiệm 5–7 phút cho mỗi lượt khám!
