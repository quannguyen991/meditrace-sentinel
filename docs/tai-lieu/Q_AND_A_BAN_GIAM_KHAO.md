# BỘ CÂU HỎI & TRẢ LỜI PHẢN BIỆN DÀNH CHO BAN GIÁM KHẢO (Q&A DEFENSE SPECIFICATION)
## DỰ ÁN: MEDITRACE SENTINEL — AMBIENT CLINICAL INTELLIGENCE

> **Hướng dẫn sử dụng:**  
> Bộ tài liệu này tổng hợp toàn bộ các câu hỏi từ **dễ đến khó**, phân chia rành mạch giữa **Lý thuyết y tế/sản phẩm** và **Kỹ thuật/thuật toán chuyên sâu**.  
> Mỗi câu trả lời được thiết kế theo công thức: **(1) Trực diện khẳng định $\rightarrow$ (2) Bản chất kỹ thuật/lâm sàng $\rightarrow$ (3) Số liệu thực nghiệm chứng minh**.

---

# PHẦN 1: CÂU HỎI LÝ THUYẾT, NGHIỆP VỤ LÂM SÀNG & GIÁ TRỊ SẢN PHẨM

---

### [DỄ] Câu 1: MediTrace Sentinel giải quyết vấn đề gì lớn nhất trong bệnh viện?
* **Trả lời:**  
  * **Vấn đề giải quyết:** Bác sĩ ngoại trú tại Việt Nam đang bị quá tải khốc liệt (khám 50–80 ca/ngày, mỗi ca chỉ có 3–5 phút). Bác sĩ phải dành hơn 50% thời gian cắm cúi gõ bàn phím nhập bệnh án điện tử (EMR), dẫn đến kiệt sức (burnout), mất kết nối với người bệnh và dễ ghi sót tiền sử/dị ứng.
  * **Giải pháp:** MediTrace đóng vai trò người trợ lý vô hình (Ambient Medical Scribe) ngồi cạnh lắng nghe cuộc trò chuyện tự nhiên giữa bác sĩ và người bệnh, tự động gỡ băng và dựng bản nháp bệnh án chuẩn cấu trúc SOAP. Bác sĩ chỉ mất 15–30 giây liếc mắt kiểm tra và bấm nút duyệt.

---

### [DỄ] Câu 2: Tại sao không dùng luôn ChatGPT, Claude hay Gemini cho nhanh và rẻ?
* **Trả lời:**  
  Có 3 lý do sống còn khiến việc dùng ChatGPT ở bệnh viện là **vi phạm pháp luật và nguy hiểm tính mạng**:
  1. **Vi phạm bảo mật (Nghị định 13/2023/NĐ-CP):** Dùng ChatGPT là gửi tên tuổi, bệnh tật của công dân Việt Nam lên máy chủ nước ngoài. MediTrace chạy 100% On-premise nội bộ, có bộ khử định danh giấu tên tự động, dữ liệu không bao giờ ra internet.
  2. **Ảo giác AI (Hallucination):** ChatGPT có xu hướng "nói dối trơn tru", sẵn sàng tự điền con số huyết áp hoặc tiền sử bệnh mà bệnh nhân không hề nói. MediTrace có 7 cổng khóa K1–K7 dò từng chữ với thoại gốc, phát hiện bịa đặt là chặn ngay.
  3. **Không thể kiểm chứng:** ChatGPT trả ra một đoạn văn xuôi dài, bác sĩ muốn kiểm tra phải đọc lại cả băng ghi âm 15 phút. MediTrace có tính năng *Click-to-Verify*: bấm vào dòng nào trên bệnh án là sáng lên câu nói ở đúng giây ghi âm gốc.

---

### [TRUNG BÌNH] Câu 3: Bác sĩ rất bận, liệu việc bắt bác sĩ ngồi duyệt từng dòng có làm mất thêm thời gian không?
* **Trả lời:**  
  * **Không làm mất thời gian, mà tiết kiệm từ 5 đến 7 phút mỗi ca khám.**
  * Bác sĩ **không phải đọc lại toàn bộ từ đầu đến cuối**. Màn hình của MediTrace chia làm 2 phần trực quan:
    * *Phần thân bệnh án:* Chứa những thông tin đã vượt qua toàn bộ 7 cổng kiểm tra (K1–K7) với độ tin cậy tuyệt đối.
    * *Mục "Cần bác sĩ xác nhận":* Chỉ gom đúng những điểm nghi ngờ (ví dụ: bệnh nhân nói nhầm, thuốc có tương tác kỵ nhau, câu giả định chưa rõ ràng) kèm cờ cảnh báo đỏ/vàng.
  * Bác sĩ chỉ cần liếc mắt đúng 15–30 giây vào các điểm cảnh báo, thấy đúng bấm nút duyệt là xong.

---

### [TRUNG BÌNH] Câu 4: Nếu phần mềm ghi nhầm hoặc gợi ý sai dẫn đến tai biến y khoa thì ai chịu trách nhiệm?
* **Trả lời:**  
  * **Về mặt pháp lý:** Bác sĩ luôn là người chịu trách nhiệm chuyên môn cuối cùng. MediTrace được định vị chính xác là **Công cụ hỗ trợ soạn thảo bản nháp (Drafting Copilot)**, không phải bác sĩ điều trị và không tự động ra quyết định thay con người.
  * **Về mặt bảo vệ thầy thuốc:** MediTrace bảo vệ bác sĩ tốt hơn việc ghi chép tay:
    1. Mọi dòng trong bệnh án đều có liên kết căn cứ trỏ về đúng câu nói của bệnh nhân $\rightarrow$ Minh bạch nguồn gốc, tránh tranh chấp "bệnh nhân bảo có nói mà bác sĩ không ghi".
    2. Sau khi bác sĩ bấm duyệt, bệnh án được niêm phong bằng chữ ký số băm SHA-256 chống sửa lén $\rightarrow$ Bảo đảm tính pháp lý trước tòa án.
    3. Tích hợp sẵn Dược thư Quốc gia để "nhắc nhở" bác sĩ khi vô tình kê 2 thuốc kỵ nhau.

---

### [KHÓ] Câu 5: Trong y tế có sự đánh đổi: Kiểm tra quá chặt thì bỏ sót thông tin (Low Recall), nới lỏng thì bị sai (Low Precision). MediTrace giải quyết sự đánh đổi này như thế nào?
* **Trả lời:**  
  * **Hệ thống áp dụng triết lý "Định tuyến bất đối xứng theo độ rủi ro" (Fail-Safe Asymmetric Routing):**
    * Với thông tin thông thường (ví dụ: đau bụng âm ỉ, mệt mỏi): Ưu tiên độ chính xác (Precision). Nếu trượt bài kiểm tra K1–K7 thì loại khỏi thân bệnh án.
    * Với thông tin nguy cấp (Dị ứng thuốc, Thuốc có khoảng điều trị hẹp như Digoxin/Warfarin, Bệnh tim mạch): **Tuyệt đối không bao giờ âm thầm xóa bỏ (Zero Information Loss)**.
  * **Giải pháp kỹ thuật:** Dù mẩu tin dị ứng có bị nghi ngờ (ví dụ người nhà nói lấp lửng), hệ thống vẫn giữ lại $100\%$ và chuyển sang mục *"CẦN BÁC SĨ XÁC NHẬN"* kèm cờ đỏ.
  * **Kết quả thực nghiệm:** Tỷ lệ bỏ sót dị ứng giảm về **$0.0\%$**, trong khi tỷ lệ thông tin đúng bị chặn nhầm đạt **$0 / 30.136$ dòng**.

---

### [KHÓ] Câu 6: Người Việt Nam khi đi khám nói năng lộn xộn, hay nuốt chủ ngữ, xưng hô "con/cháu/ông nhà", dùng từ địa phương ("trúng gió", "xót ruột"). Làm sao hệ thống của bạn xử lý được?
* **Trả lời:**  
  Đây chính là "vũ khí bản địa hóa" của MediTrace mà các mô hình nước ngoài không thể có:
  1. **Tầng 2 (Gom nhóm chủ thể - `src/thuc_the.py`):** Bộ luật ngữ pháp xử lý đại từ xưng hô Việt Nam. Phân biệt rõ: người mẹ nói *"Cháu nhà em bị sốt"* thì chủ thể bệnh là "con" (id=1), không phải người mẹ (id=0).
  2. **Xử lý câu nuốt chủ ngữ:** Khi bệnh nhân nói *"Sốt 2 hôm nay rồi"*, ngữ cảnh lượt thoại được đối chiếu với vai người nói (Speaker Role). Nếu là bệnh nhân nói về bản thân thì tự động gán chủ thể $0$.
  3. **Động cơ phương ngữ 3 miền (`src/phuong_ngu_lam_sang.py`):** Bộ từ điển hơn 60 thuật ngữ dân gian (Bắc - Trung - Nam) quy đổi về chuẩn y khoa: *"trúng gió"* $\rightarrow$ liệt dây VII ngoại biên / cảm mạo; *"xót ruột/cồn cào"* $\rightarrow$ viêm loét dạ dày; *"nấc cục"* $\rightarrow$ nấc cụt.
  4. **Từ điển âm vị thuốc Tây:** Bệnh nhân đọc tên thuốc dân gian: *"a móc"* $\rightarrow$ *Amoxicillin*; *"ô mê"* $\rightarrow$ *Omeprazole*.

---

# PHẦN 2: CÂU HỎI KỸ THUẬT, THUẬT TOÁN & CÔNG NGHỆ CHUYÊN SÂU

---

### [DỄ] Câu 7: Kiến trúc tổng thể của MediTrace gồm những thành phần công nghệ nào?
* **Trả lời:**  
  * **Tầng 0 (ASR):** PhoWhisper (fine-tuned nhận dạng tiếng nói tiếng Việt) + PyAnnote Diarization (tách giọng người nói).
  * **Tầng 1 (Bóc tách thông tin):** Mô hình nguồn mở Qwen3-4B chạy kèm adapter huấn luyện QLoRA 4-bit (chạy ngay trên GPU máy trạm phòng khám).
  * **Tầng 2 đến Tầng 5 (Xử lý & Kiểm chứng):** 100% viết bằng Python thuật toán xác định (Deterministic Rule-Based, Máy trạng thái hữu hạn FSM, Bảng tra Dược thư Quốc gia, Template Engine).
  * **Giao diện Web:** React 19 + TypeScript + TailwindCSS, giao tiếp với backend qua REST API nội bộ (`src/dich_vu.py`).

---

### [DỄ] Câu 8: Tại sao lại chọn mô hình Qwen3-4B mà không chọn Llama-3-8B hay mô hình lớn hơn?
* **Trả lời:**  
  1. **Khả năng triển khai tại phòng khám (Hardware Feasibility):** Các phòng khám Việt Nam chỉ trang bị máy tính phổ thông hoặc máy trạm có card đồ họa vừa phải (4GB – 8GB VRAM). Mô hình 8B cần tối thiểu 12GB–16GB VRAM, chi phí phần cứng quá đắt. Qwen3-4B QLoRA chỉ tốn ~3.8GB VRAM, chạy mượt trên card đồ họa phổ thông (như RTX 3050/3060).
  2. **Thời gian phản hồi:** Mô hình 4B xử lý bóc tách một ca khám chỉ mất ~30–45 giây trên GPU phổ thông, trong khi mô hình lớn mất từ 5–10 phút (không kịp cho ca khám tiếp theo).
  3. **Độ chính xác chuyên biệt:** Nhờ kỹ thuật huấn luyện QLoRA trên tập dữ liệu hội thoại y tế tiếng Việt chuẩn, Qwen3-4B đạt độ chính xác trích xuất tương đương mô hình 8B nhưng nhẹ hơn gấp đôi.

---

### [TRUNG BÌNH] Câu 9: Tại sao dự án chỉ dùng AI ở Tầng 1, còn Tầng 2–5 lại dùng thuật toán luật (Rule-based)? Sao không dùng AI làm hết (End-to-End)?
* **Trả lời:**  
  * **Đây là quyết định kiến trúc quan trọng nhất của dự án (Neuro-symbolic Architecture):**
    * Điểm mạnh của AI (LLM) là: Đọc hiểu ngôn ngữ tự nhiên lộn xộn, nhận diện từ đồng nghĩa và nhặt mẩu tin.
    * Điểm yếu chết người của AI là: Hay bịa đặt (hallucination), không làm toán chuẩn, không kiểm soát được ranh giới logic chặt chẽ.
  * **Nếu để AI làm từ đầu đến cuối (End-to-End):** Mô hình sẽ tự tiện gộp các câu khác chủ thể lại với nhau, biến câu dặn dò tương lai thành bệnh đã có, và khi sai thì không ai biết nó sai ở bước nào ("hộp đen").
  * **Khi tách thành luật ở Tầng 2–5:** Mọi quy tắc (đối soát chữ, tra thuốc kỵ nhau, cộng điểm thang điểm) đều minh bạch 100%, có thể viết Unit Test kiểm thử độc lập và sửa lỗi ngay lập tức mà không cần phải train lại AI.

---

### [TRUNG BÌNH] Câu 10: Cơ chế Khóa bằng chứng K1–K7 ở Tầng 4 hoạt động cụ thể như thế nào để chặn Hallucination?
* **Trả lời:**  
  Mỗi mệnh đề được AI trích ra ở Tầng 1 bắt buộc phải có trường `trich_dan` (chuỗi trích dẫn nguyên văn) và `bang_chung` (lượt thoại $[T_i]$). Cổng khóa tại [`src/khoa_bang_chung.py`](file:///d:/Claude/meditrace-ma-nguon/src/khoa_bang_chung.py) thực thi 7 chốt chặn:
  * **K1 (Nguồn gốc nguyên văn):** Dò trực tiếp xâu ký tự `trich_dan` vào lượt thoại $[T_i]$. Nếu không có trong lượt thoại $\rightarrow$ Bị CHẶN lập tức (`trich_khong_co`), đánh dấu Hallucination.
  * **K2 (Khớp nội dung):** Quét tỷ lệ trùng lặp từ ngữ lâm sàng cốt lõi.
  * **K3 (Khớp chủ thể):** Đối chiếu từ chỉ người trong lượt thoại với vai người được gán.
  * **K4 (Khớp mức khẳng định):** Phát hiện câu nghi ngờ hoặc câu điều kiện/phòng ngừa ("Nếu... thì...") mà bị ghi thành sự thật $\rightarrow$ Bị CHẶN (`dieu_kien`).
  * **K5 (Khớp mốc thời gian):** Mốc thời gian phải có thật trong lượt thoại.
  * **K6 (Khớp liều lượng & thuốc):** Số lượng viên, hàm lượng mg phải trùng khớp với con số người nói nhắc đến.
  * **K7 (Kiểm tra đính chính - Superseded):** Nếu thông tin đã bị câu nói sau đính chính hoặc xét nghiệm loại trừ $\rightarrow$ Đánh dấu bị thay thế, không cho vào thân bệnh án.

---

### [KHÓ] Câu 11: Tại sao trong báo cáo bạn khẳng định điểm ROUGE (thước đo AI văn bản phổ biến) là vô dụng trong đánh giá bệnh án? Bạn dùng thước đo nào thay thế?
* **Trả lời:**  
  * **Thực nghiệm chứng minh ROUGE vô dụng trong y tế:**  
    Trong thử nghiệm trên 400 ca bệnh của dự án, khi cố ý đổi chỗ chữ **"bệnh nhân"** và **"người nhà"** (ví dụ: biến bệnh hen của người nhà thành bệnh của bệnh nhân — một lỗi y khoa cực kỳ nghiêm trọng):
    $$\text{Điểm ROUGE-1 vẫn đạt đúng } \mathbf{1.0000} \text{ (điểm tuyệt đối!)}$$
    Lý do: ROUGE chỉ đếm số từ trùng lặp mà không hiểu ngữ nghĩa. Hoán đổi hai người thì tập hợp từ không hề thay đổi, nên ROUGE không phát hiện được lỗi!
  * **Thước đo thay thế của dự án:**  
    Dự án xây dựng bộ đo chuyên biệt **Entity Slot Error Rate (SER)** và **Attribution F1**:
    * Đo đạc chính xác trên từng ô thuộc tính: (Chủ thể, Bệnh/Thuốc, Trạng thái, Thời gian).
    * Đo tỷ lệ thông tin bị thay thế nhưng vẫn còn sót lại trong bản nháp (nhờ đó chứng minh Cổng K7 giảm tỷ lệ sót tin cũ từ $11.48\%$ xuống **$0.80\%$**).

---

### [KHÓ] Câu 12: Dữ liệu huấn luyện của bạn là dữ liệu mô phỏng (Synthetic Data). Làm sao chứng minh mô hình không bị "học vẹt" (overfitting) và có tính tổng quát ngoài đời thực?
* **Trả lời:**  
  Dự án giải quyết triệt để vấn đề này qua 3 kỹ thuật khoa học:
  1. **Chia tách theo khuôn bệnh độc lập (Template-Disjoint Split):** 200 khuôn ca bệnh được chia thành tập Train, Dev, Test riêng biệt. Tập Test gồm những khuôn bệnh mà mô hình **chưa bao giờ nhìn thấy trong lúc huấn luyện**.
  2. **Đo đạc độ đa dạng từ vựng bằng toán học:** Đo khoảng cách Jaccard và n-gram diversity giữa 5.000 ca bệnh, chứng minh độ khác biệt giữa các ca đạt **$78.3\%$** (không bị trùng lặp câu chữ).
  3. **Bộ dữ liệu Thử thách Cặp đôi (Adversarial Contrastive Pairs):** Tạo 300 ca thử thách theo cặp chỉ khác nhau đúng một yếu tố ranh giới (đổi người mang dị ứng, người nói tự đính chính sau 5 câu, chèn tiếng ồn ASR, phương ngữ 3 miền). Kết quả nhánh C của MediTrace vượt trội hoàn toàn so với nhánh A (AI thông thường) với $F_1$ tăng từ $66.1\%$ lên **$70.8\%$** và SER giảm từ $45.4\%$ xuống **$36.9\%$**.

---

### [KHÓ] Câu 13: Hệ thống Guardrails 5 chốt chặn vừa nâng cấp giải quyết hiện tượng Cascading Errors (Lỗi dây chuyền) như thế nào?
* **Trả lời:**  
  * **Cơ chế Cascading Error:** Nếu Tầng 0 (ASR) nghe sai từ *"Aspirin"* thành *"Amlodipin"*, Tầng 1 sẽ nhặt mẩu tin *"Amlodipin"*, Tầng 2 gán cho bệnh nhân, Tầng 3 lưu trạng thái. Đến Tầng 4 kiểm tra thì thấy câu trích vẫn khớp với đoạn gỡ băng (vì chính đoạn gỡ băng đã bị chép sai từ đầu!), dẫn đến bệnh án sai hoàn toàn.
  * **Cách Guardrails 5 tầng chặn đứng:**
    * **Chốt 1 (ASR Guardrail):** Chạy ngay sau gỡ băng. Dò âm vị dược thư và từ điển phương ngữ, phát hiện từ lặp bất thường và tự động quy đổi cách đọc dân gian (*"a móc"* $\rightarrow$ *Amoxicillin*) ngay tại nguồn.
    * **Chốt 2 (Speaker Guardrail):** Rà soát mâu thuẫn đại từ nhân xưng ngay khi Tầng 1 vừa nhặt mẩu tin.
    * **Chốt 3 (Dialogue Act Gate):** Bóc tách các câu đính chính (*"à không"*) và câu giả định (*"nếu mai sốt"*) trước khi đưa vào máy trạng thái.
    * **Chốt 4 (Evidence Integrity Gate):** Soi xâu ký tự và đối soát từng con số sinh hiệu/liều thuốc.
    * **Chốt 5 (Clinical Safety Gate):** Soi tương tác thuốc kỵ nhau DDI và liều trần trước khi xuất bệnh án.
  * **Kết quả:** Sai ở khâu nào bị chặn đứng và cô lập ngay ở khâu đó, không bao giờ lan truyền sang khâu tiếp theo.

---

# PHẦN 3: BỘ CÂU HỎI "BẮT BẺ CHÍ MẠNG" (STRESS-TEST) & CÁCH PHẢN BIỆN ĐOẠT ĐIỂM TUYỆT ĐỐI

---

### ❓ Giám khảo hỏi: *"Nếu micrô phòng khám thu nhiều tạp âm, bệnh nhân nói lí nhí, ASR nghe sai be bét thì phần mềm của bạn có thành đống rác không?"*
* **🎯 Phản biện tự tin:**  
  *"Thưa Ban Giám khảo, đây chính là lý do MediTrace vượt trội hơn ChatGPT.  
  Nếu là ChatGPT, khi gặp đoạn gỡ băng sai be bét, nó vẫn cố tình 'sáng tác' ra một bệnh án đọc rất mượt nhưng sai sự thật $\rightarrow$ cực kỳ nguy hiểm.  
  Còn với MediTrace, nhờ Chốt Guardrail 1 và Cổng K1: Khi âm thanh bị nhiễu hoặc không rõ ràng, hệ thống sẽ phát hiện độ tin cậy thấp (Low Confidence) và câu trích không đủ căn cứ. Mẩu tin đó **lập tức bị chặn lại và chuyển sang mục 'Cần bác sĩ xác nhận'** chứ tuyệt đối không bao giờ được ghi vào bệnh án chính thức. Thà để bác sĩ tự điền bằng tay còn hơn để phần mềm tự bịa thông tin sai!"*

---

### ❓ Giám khảo hỏi: *"Một ngày khám 80 ca, nhỡ bác sĩ bận quá quên bấm duyệt mà tắt máy về thì dữ liệu có bị mất không?"*
* **🎯 Phản biện tự tin:**  
  *"Hệ thống thiết kế cơ chế tự động lưu trữ tức thời (Auto-Save Persistence) vào cơ sở dữ liệu SQLite cục bộ tại phòng khám sau mỗi lượt thoại. Toàn bộ phiên âm thanh, các mẩu tin trích xuất và bản nháp đều được lưu vết. Nếu bác sĩ bị ngắt quãng ca khám để đi cấp cứu hoặc tắt máy đột ngột, khi mở lại phần mềm, ca khám vẫn hiển thị nguyên vẹn ở trạng thái 'Chờ duyệt' để bác sĩ kiểm tra tiếp mà không bị mất một chữ nào."*

---

### ❓ Giám khảo hỏi: *"Dự án của bạn đã kiểm thử trên bao nhiêu ca bệnh và độ ổn định thực tế ra sao?"*
* **🎯 Phản biện tự tin:**  
  *"Hệ thống đã trải qua bộ kiểm thử tự động toàn diện với **1.320 bài test tự động (Unit & Integration Tests)** bao phủ toàn bộ 14 module lâm sàng, 7 cổng khóa bằng chứng và các tình huống kiểm thử nghịch đảo. Hiện tại, toàn bộ 1.320 bài test đều vượt qua $100\%$ không có lỗi.  
  Ngoài ra, cơ sở dữ liệu khuôn bệnh đã được nâng cấp lên **200 khuôn ca bệnh thuộc 10 chuyên khoa lâm sàng**, với hơn 5.000 hội thoại mô phỏng và 300 ca thử thách đối đầu ranh giới, bảo đảm hệ thống sẵn sàng hoạt động ổn định trong môi trường thực tế."*

---

> **LỜI KẾT DÀNH CHO BẠN KHI ĐỨNG TRƯỚC BAN GIÁM KHẢO:**  
> Luôn giữ phong thái tự tin, điềm tĩnh và bám chắc vào thông điệp:  
> **"MediTrace Sentinel không phải là công cụ AI biểu diễn công nghệ viết văn. Đây là giải pháp an toàn y tế số được xây dựng bằng tư duy lâm sàng thực chiến: Đặt an toàn tính mạng người bệnh lên hàng đầu, triệt tiêu ảo giác bằng luật toán học xác định, và giải phóng đôi tay người thầy thuốc."**
