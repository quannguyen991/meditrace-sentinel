# TÀI LIỆU BÀN GIAO DỰ ÁN MEDITRACE SENTINEL (HANDOVER SPECIFICATION)

> **Dành cho AI (Gemini / Claude / Antigravity) và Kỹ sư tiếp nhận dự án:**  
> Đọc tệp này để hiểu toàn bộ bối cảnh, kiến trúc hệ thống 5 tầng, cấu trúc mã nguồn, quy trình luồng dữ liệu, 14 module nâng cấp an toàn lâm sàng, bộ kiểm thử tự động, và các nguyên tắc thiết kế bất khả xâm phạm của dự án **MediTrace Sentinel**.

---

## 1. TỔNG QUAN DỰ ÁN & VẤN ĐỀ CỐT LÕI

### 1.1 MediTrace Sentinel là gì?
**MediTrace Sentinel** là một hệ sinh thái **Trợ lý Ghi chép Lâm sàng Xung quanh (Ambient Clinical Intelligence / AI Medical Scribe)** chuyên dụng cho phòng khám và bệnh viện tại Việt Nam.  
Hệ thống lắng nghe cuộc hội thoại khám bệnh giữa Bác sĩ – Bệnh nhân – Thân nhân bằng tiếng Việt đời thường, tự động gỡ băng và dựng thành **bản nháp hồ sơ bệnh án chuẩn SOAP** (Subjective – Objective – Assessment – Plan).

### 1.2 Triết lý thiết kế cốt lõi: "Neuro-symbolic & Verifiable"
Khác với các ứng dụng AI đàm thoại thông thường (như ChatGPT, Gemini) vốn để cho mô hình ngôn ngữ lớn (LLM) tự do sinh văn bản từ đầu đến cuối dẫn đến rủi ro **ảo giác lâm sàng (Clinical Hallucination)** và **nhầm lẫn chủ thể (Misattribution)**:
* **Mô hình AI chỉ được làm một việc duy nhất:** Nhận diện âm thanh (PhoWhisper) và bóc tách các mẩu tin nguyên tử (Qwen3-4B QLoRA) kèm câu trích nguyên văn và lượt thoại `[T_i]`.
* **Tuyệt đối cấm AI tự do viết văn xuôi bệnh án:** Các khâu gom chủ thể, xử lý đính chính, đối soát bằng chứng K1–K7, kiểm tra tương tác thuốc Dược thư Quốc gia, và sinh văn bản SOAP hoàn chỉnh **100% là thuật toán luật toán học xác định (Deterministic Rule-Based / FSM / Template Engine)**.
* **Mọi dòng trong bệnh án đều phải kiểm chứng được trong 1 giây (Click-to-Verify):** Bác sĩ nhấp chuột vào bất kỳ mệnh đề nào, hệ thống lập tức hiển thị đường nối trỏ thẳng về đúng câu nói và đúng giây âm thanh gốc.

### 1.3 Bối cảnh cấp thiết tại Việt Nam
* **Quá tải phòng khám:** Bác sĩ ngoại trú khám 50–80 ca/ngày, mỗi ca chỉ có 3–5 phút. Hơn 50% thời gian bị "trói tay vào bàn phím" để gõ phần mềm EMR.
* **Quy định pháp lý bắt buộc:** Thông tư 46/2018/TT-BYT (bắt buộc số hóa bệnh án điện tử) và Nghị định 13/2023/NĐ-CP (bảo vệ dữ liệu cá nhân cực kỳ nghiêm ngặt, cấm gửi dữ liệu bệnh tật lên máy chủ nước ngoài).
* **Mô hình triển khai:** Chạy **100% On-premise (cục bộ)** trên máy tính phòng khám/bệnh viện. Không gửi bất kỳ dữ liệu nào ra ngoài internet.

---

## 2. KIẾN TRÚC ĐƯỜNG ỐNG 5 TẦNG (PIPELINE ARCHITECTURE)

```
                       [Âm thanh cuộc khám / Lời thoại tiếng Việt]
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ TẦNG 0: GỠ BĂNG ÂM THANH & TÁCH NGƯỜI NÓI (PhoWhisper + PyAnnote)                       │
│ - Tệp: src/audio/pipeline.py, src/audio/storage.py                                      │
│ - Chuyển audio -> chuỗi lượt thoại: {segment_id, text, speaker_id, start_time, end_time} │
│ - Bác sĩ duyệt gán vai (bác sĩ, bệnh nhân, người nhà)                                   │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ TẦNG 1: BÓC TÁCH MỆNH ĐỀ NGUYÊN TỬ (Qwen3-4B + QLoRA Adapter)                          │
│ - Tệp: src/nhanh.py, src/phat_bieu.py, src/bakeoff.py                                   │
│ - Đọc hội thoại thô -> Xuất danh sách mẩu tin nguyên tử có cấu trúc:                    │
│   PhatBieu: {chu_the, thuc_the, trang_thai, thoi_gian, luot_thoai, trich_dan}           │
│   BẮT BUỘC có trích dẫn nguyên văn chuỗi ký tự trong lượt thoại [T_i]                   │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ TẦNG 2: LIÊN KẾT THỰC THỂ & GOM NHÓM NGƯỜI NÓI (Deterministic Rule-Based)                │
│ - Tệp: src/thuc_the.py, src/phan_quan_he.py                                             │
│ - Phân tách rõ ràng: Bác sĩ, Người bệnh (id=0), Người nhà (id=1, 2...)                   │
│ - Đại từ họ hàng tiếng Việt ("bố tôi", "mẹ em", "bé nhà tôi", "ông nhà")                │
│ - Ngăn chặn lỗi nhầm lẫn tiền sử gia đình thành tiền sử bản thân bệnh nhân              │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ TẦNG 3: CẬP NHẬT TRẠNG THÁI & DÒNG THỜI GIAN ĐÍNH CHÍNH (Finite State Machine - FSM)    │
│ - Tệp: src/cap_nhat.py                                                                  │
│ - Tự động nhận diện bệnh nhân tự sửa lời nói: "1 tuần... à không, 10 ngày rồi"          │
│   -> Đánh dấu mẩu tin cũ là "bị thay thế" (K7 Superseded), chỉ giữ lại mẩu tin mới       │
│ - Xử lý thông tin song hành, mâu thuẫn giữa 2 người nói chưa được xác nhận             │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ TẦNG 4: KHÓA BẰNG CHỨNG (K1-K7) & ĐỊNH TUYẾN CỔNG RỦI RO (Fail-Safe Asymmetric Routing) │
│ - Tệp: src/khoa_bang_chung.py, src/cong_rui_ro.py, src/guardrails.py                    │
│ - K1: So khớp ký tự trích dẫn trực tiếp vào lượt thoại gốc [T_i] (Chặn Hallucination)   │
│ - K2: So khớp đại từ nhân xưng và vai người nói                                         │
│ - K3: So khớp thực thể y học                                                            │
│ - K4: Phát hiện câu giả định, kế hoạch, phòng ngừa ("Nếu sốt thì...")                   │
│ - K5: So khớp mốc thời gian                                                             │
│ - K6: So khớp số liệu liều lượng, đơn vị thuốc                                          │
│ - K7: Kiểm tra thông tin đã bị đính chính / loại trừ                                    │
│ - Triết lý: "Bắt nhầm còn hơn bỏ sót" -> Đẩy thông tin nghi ngờ xuống CẦN XÁC NHẬN      │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ TẦNG 5: SINH HỒ SƠ BỆNH ÁN SOAP THEO KHUÔN MẪU (Template Engine - Không dùng LLM)      │
│ - Tệp: src/sinh_benh_an.py, src/fhir_exporter.py, src/dan_do_benh_nhan.py               │
│ - Ghép các mệnh đề đã kiểm duyệt vào đúng các mục chuẩn SOAP:                           │
│   + LÝ DO KHÁM BỆNH, BỆNH SỬ HIỆN TẠI, SINH HIỆU, TIỀN SỬ BỆNH, TIỀN SỬ GIA ĐÌNH        │
│   + KHÁM LÂM SÀNG, ĐƠN THUỐC, CẦN BÁC SĨ XÁC NHẬN                                       │
│ - Xuất bản dặn dò bình dân cho người bệnh & Chuẩn quốc tế HL7 FHIR R4                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. CẤU TRÚC THƯ MỤC DỰ ÁN & VAI TRÒ TỪNG TỆP TIN

```
d:\Claude\meditrace-ma-nguon\
├── HANDOVER.md                                # TÀI LIỆU NÀY (Bàn giao dự án cho Gemini/AI/Dev)
├── README.md                                  # Hướng dẫn tổng quan ngắn gọn của dự án
├── GIAI_THICH_DU_AN_MEDITRACE_SENTINEL.md     # Bản giải thích toàn diện bối cảnh, lý do, sự khác biệt
├── package.json                               # Cấu hình workspace
├── data/                                      # Dữ liệu mẫu, cache trích xuất (trich_*_hl.jsonl)
├── models/                                    # Thư mục lưu checkpoint QLoRA adapter
│
├── src/                                       # TOÀN BỘ MÃ NGUỒN XỬ LÝ LÕI (PYTHON)
│   ├── audio/                                 # Module gỡ băng âm thanh & ASR
│   │   ├── pipeline.py                        # Pipeline gỡ băng PhoWhisper + Pyannote diarization
│   │   └── storage.py                         # Quản lý lưu trữ phiên âm thanh cục bộ
│   │
│   ├── nhanh.py                               # ĐIỀU PHỐI ĐƯỜNG ỐNG: So sánh nhánh A (AI thuần) và C (MediTrace)
│   ├── phat_bieu.py                           # Định nghĩa cấu trúc mẩu tin lâm sàng nguyên tử (PhatBieu)
│   ├── thuc_the.py                            # Tầng 2: Gom nhóm đại từ nhân xưng & liên kết thực thể
│   ├── cap_nhat.py                            # Tầng 3: Máy trạng thái FSM xử lý đính chính và mâu thuẫn
│   ├── khoa_bang_chung.py                     # Tầng 4: Bộ 7 cổng khóa bằng chứng K1-K7 đối soát thoại gốc
│   ├── cong_rui_ro.py                         # Tầng 4: Phân loại rủi ro lâm sàng & cổng cách ly an toàn
│   ├── sinh_benh_an.py                        # Tầng 5: Bộ mẫu sinh bệnh án SOAP từ bảng mệnh đề đã duyệt
│   ├── dich_vu.py                             # Máy chủ HTTP API cục bộ (cổng 8765) cho Frontend Web
│   │
│   ├── [14 MODULE NÂNG CẤP LÂM SÀNG MỚI]:
│   ├── guardrails.py                          # Hệ thống 5 chốt kiểm tra tự động Guardrails đa tầng
│   ├── duoc_ly_lam_sang.py                    # Cảnh báo tương tác thuốc DDI & Dược thư Quốc gia
│   ├── hieu_chinh_lieu.py                     # Hiệu chỉnh liều thuốc suy thận (Cockcroft-Gault) & suy gan
│   ├── thang_diem_lam_sang.py                 # Tự động tính 9 thang điểm lâm sàng (NEWS2, GCS, qSOFA...)
│   ├── can_lam_sang.py                        # Báo động giá trị cận lâm sàng nguy kịch & soi mâu thuẫn
│   ├── tro_ly_lam_sang.py                     # Trợ lý nhắc bác sĩ hỏi triệu chứng SOCRATES
│   ├── khu_dinh_danh.py                       # Khử định danh thông tin cá nhân (HIPAA / NĐ 13)
│   ├── fhir_exporter.py                       # Xuất bệnh án chuẩn quốc tế HL7 FHIR R4 JSON
│   ├── dan_do_benh_nhan.py                    # Tự động sinh bản dặn dò uống thuốc & dấu hiệu đỏ cấp cứu
│   ├── phuong_ngu_lam_sang.py                 # Bộ từ điển phương ngữ 3 miền & âm vị tên thuốc dân gian
│   ├── da_benh_ly.py                          # Ma trận đa bệnh lý kết hợp (cấp tính + mạn tính)
│   ├── dieu_phoi_ha_tang.py                   # Quản lý tài nguyên phần cứng, chống tràn RAM & chữ ký SHA-256
│   ├── canh_bao/                              # Gói chính sách phân loại cờ đỏ lâm sàng
│   └── sinh_hoi_thoai_viet.py                 # Bộ sinh 200 khuôn ca bệnh đa chuyên khoa
│
├── tests/                                     # BỘ KIỂM THỬ TỰ ĐỘNG (1.320+ TESTS)
│   ├── test_guardrails.py                     # Test 5 tầng Guardrails, chống ảo giác số liệu & liều trần
│   ├── test_khoa_bang_chung.py                # Test 26 kịch bản khóa bằng chứng K1-K7
│   ├── test_cong_rui_ro.py                    # Test cổng cách ly an toàn & phân nhóm rủi ro
│   ├── test_thang_diem_lam_sang.py            # Test tính điểm 9 thang điểm lâm sàng
│   ├── test_duoc_ly_lam_sang.py               # Test phát hiện tương tác thuốc kỵ nhau DDI
│   ├── test_hieu_chinh_lieu.py                # Test chỉnh liều theo chức năng thận Cockcroft-Gault
│   ├── test_can_lam_sang.py                   # Test cảnh báo cận lâm sàng nguy kịch
│   └── test_kiem_khuon.py                     # Test bộ dữ liệu 200 khuôn ca bệnh
│
├── tools/                                     # CÔNG CỤ HỖ TRỢ & XUẤT BÁO CÁO
│   ├── tao_bao_cao_nang_cap_word.py           # Script tự động xuất file Word báo cáo thẩm mỹ cao
│   └── ve_slide_problem_evidence_meditrace.py # Script vẽ đồ thị trực quan hóa dữ liệu thực nghiệm
│
├── web/                                       # GIAO DIỆN NGƯỜI DÙNG WEB (REACT + TYPESCRIPT)
│   ├── src/components/EvidenceView.tsx        # Màn hình duyệt từng mệnh đề, nối đường bằng chứng
│   └── src/components/SoapNote.tsx            # Màn hình hiển thị bệnh án chuẩn SOAP
│
└── docs/                                      # TÀI LIỆU, SLIDE & HÌNH ẢNH DỰ THI
    └── tai-lieu/                              # Chứa file Word, Markdown giải thích chi tiết
```

---

## 4. CHI TIẾT 14 MODULE NÂNG CẤP MỚI & CÁCH GIẢI QUYẾT BÀI TOÁN

| STT | Tên module & File mã nguồn | Vấn đề thực tế trước đây | Giải pháp công nghệ trong mã nguồn |
| :---: | :--- | :--- | :--- |
| **1** | **Guardrails Đa tầng**<br>[`src/guardrails.py`](file:///d:/Claude/meditrace-ma-nguon/src/guardrails.py) | Lỗi nghe nhầm ở bước trước sẽ bị các bước sau chép theo dây chuyền. | 5 Guardrail độc lập: Kiểm tra âm vị thuốc ASR; Kiểm tra xung đột đại từ xưng hô; Kiểm tra tự sửa lời nói; Khóa đối soát xâu ký tự; Định tuyến bảo toàn thông tin nguy cấp. |
| **2** | **Dược lý Lâm sàng & DDI**<br>[`src/duoc_ly_lam_sang.py`](file:///d:/Claude/meditrace-ma-nguon/src/duoc_ly_lam_sang.py) | AI thông thường không biết 2 thuốc kê cùng nhau có gây xuất huyết hoặc tử vong không. | Bảng tra cứu tương tác thuốc DDI theo Dược thư Quốc gia Việt Nam; Kiểm soát liều trần tối đa trong ngày (Paracetamol $\le 4000\text{mg}$, Ibuprofen $\le 2400\text{mg}$...). |
| **3** | **Hiệu chỉnh liều Thận/Gan**<br>[`src/hieu_chinh_lieu.py`](file:///d:/Claude/meditrace-ma-nguon/src/hieu_chinh_lieu.py) | Người suy thận uống liều người bình thường sẽ bị ngộ độc; bác sĩ bận không kịp bấm máy tính tính độ lọc thận. | Áp dụng công thức Cockcroft-Gault tính độ thanh thải Creatinine ($eGFR$), tự động đưa ra khuyến cáo giảm $50\%$ liều hoặc chống chỉ định dùng thuốc. |
| **4** | **9 Thang điểm Lâm sàng**<br>[`src/thang_diem_lam_sang.py`](file:///d:/Claude/meditrace-ma-nguon/src/thang_diem_lam_sang.py) | Trong lúc khám đông, bác sĩ khó nhớ hết các bảng cộng điểm nguy cơ phức tạp. | Tự động tính 9 thang điểm chuẩn y khoa: **NEWS2**, **CURB-65**, **CHA2DS2-VASc**, **HAS-BLED**, **GCS**, **qSOFA**, **NYHA**, **Child-Pugh**, **BMI**. |
| **5** | **Giám sát Cận lâm sàng**<br>[`src/can_lam_sang.py`](file:///d:/Claude/meditrace-ma-nguon/src/can_lam_sang.py) | Giấy xét nghiệm kẹp lẫn trong hồ sơ, bác sĩ chưa kịp xem làm trễ giờ vàng cấp cứu. | Quét dải tham chiếu bình thường; Bật báo động đỏ giá trị nguy kịch (Troponin tăng, Kali máu vọt); Phát hiện mâu thuẫn giữa lời nói và kết quả xét nghiệm. |
| **6** | **Trợ lý Hỏi bù Triệu chứng**<br>[`src/tro_ly_lam_sang.py`](file:///d:/Claude/meditrace-ma-nguon/src/tro_ly_lam_sang.py) | Ca khám 3 phút bác sĩ rất dễ quên hỏi kỹ tính chất cơn đau (vị trí, hướng lan, mức độ). | Phân tích khoảng trống bệnh sử theo chuẩn SOCRATES; Hiện sẵn các nút gợi ý câu hỏi để bác sĩ bấm hỏi bổ sung trước khi kết thúc ca khám. |
| **7** | **Khử định danh Bảo mật**<br>[`src/khu_dinh_danh.py`](file:///d:/Claude/meditrace-ma-nguon/src/khu_dinh_danh.py) | Rò rỉ thông tin cá nhân bệnh nhân vi phạm pháp luật (NĐ 13/2023/NĐ-CP). | Tự động tìm và mã hóa tên, SĐT, số CCCD, số thẻ BHYT thành `[BENH_NHAN_1]`, `[SDT_1]`. Chỉ bác sĩ tại phòng khám mới có chìa khóa giải mã. |
| **8** | **Xuất chuẩn HL7 FHIR R4**<br>[`src/fhir_exporter.py`](file:///d:/Claude/meditrace-ma-nguon/src/fhir_exporter.py) | Dữ liệu các bệnh viện bị phân mảnh, xuất ra chữ Word bác sĩ lại phải gõ tay vào máy. | Đóng gói bệnh án thành cấu trúc chuẩn quốc tế HL7 FHIR Bundle (Patient, Encounter, Condition, Observation, MedicationRequest) cắm thẳng vào EMR bệnh viện. |
| **9** | **Bản dặn dò Đời thường**<br>[`src/dan_do_benh_nhan.py`](file:///d:/Claude/meditrace-ma-nguon/src/dan_do_benh_nhan.py) | Đơn thuốc viết tắt thuật ngữ chuyên ngành bệnh nhân về nhà không hiểu, uống sai giờ. | Tự động dịch thành bản dặn dò bình dị, chia lịch uống thuốc 4 buổi (Sáng - Trưa - Chiều - Tối, trước/sau ăn), chế độ ăn kiêng và danh mục Dấu hiệu đỏ cấp cứu. |
| **10** | **Phương ngữ & Âm vị thuốc**<br>[`src/phuong_ngu_lam_sang.py`](file:///d:/Claude/meditrace-ma-nguon/src/phuong_ngu_lam_sang.py) | Người bệnh dùng từ địa phương ("trúng gió", "xót ruột") hoặc đọc tên thuốc kiểu dân gian ("a móc", "ô mê"). | Bộ từ điển 60+ thuật ngữ dân gian 3 miền và bảng âm vị thuốc Tây, tự động chuẩn hóa về thuật ngữ y khoa chính tắc. |
| **11** | **Điều phối Phần cứng & SHA-256**<br>[`src/dieu_phoi_ha_tang.py`](file:///d:/Claude/meditrace-ma-nguon/src/dieu_phoi_ha_tang.py) | Máy tính phòng khám yếu dễ bị treo RAM; hồ sơ bệnh án điện tử sợ bị sửa lén. | Tự động giải phóng bộ nhớ VRAM/RAM; Tự động đóng dấu băm SHA-256 niêm phong bệnh án sau khi bác sĩ duyệt để bảo đảm giá trị pháp lý trước tòa án. |
| **12** | **Ma trận Đa bệnh lý**<br>[`src/da_benh_ly.py`](file:///d:/Claude/meditrace-ma-nguon/src/da_benh_ly.py) | Bệnh nhân thực tế thường mắc nhiều bệnh kết hợp (cấp tính trên nền mạn tính). | Ma trận kết hợp bệnh lý phức tạp (viêm phổi + đái tháo đường + tăng huyết áp), bảo đảm dữ liệu mô phỏng sát 100% thực tế. |
| **13** | **An toàn Bắt nhầm hơn bỏ sót**<br>[`src/canh_bao/`](file:///d:/Claude/meditrace-ma-nguon/src/canh_bao/) | Kiểm tra quá gắt sẽ làm mất các thông tin nguy hiểm (dị ứng, thuốc tim). | Không bao giờ âm thầm xóa bỏ thông tin nghi ngờ; chuyển toàn bộ vào mục "Cần bác sĩ xác nhận" kèm cờ đỏ để bác sĩ tự quyết định. |
| **14** | **200 Khuôn ca bệnh Lâm sàng**<br>[`src/sinh_hoi_thoai_viet.py`](file:///d:/Claude/meditrace-ma-nguon/src/sinh_hoi_thoai_viet.py) | Số lượng bài mẫu ít dễ bị học vẹt, thiếu tính khái quát. | Mở rộng gấp đôi lên 200 khuôn bệnh thuộc 10 chuyên khoa; chứng minh bằng toán học độ đa dạng khác biệt đạt 78.3%. |

---

## 5. CÁC CẤU TRÚC DỮ LIỆU CỐT LÕI (CORE SCHEMAS)

### 5.1 Cấu trúc mệnh đề nguyên tử (`PhatBieu` trong `src/phat_bieu.py`)
```python
@dataclass
class PhatBieu:
    id: int                       # Mã định danh mẩu tin
    chu_the_id: int               # 0: Bệnh nhân, 1..n: Người nhà / Người khác
    ten_chu_the: str              # "bệnh nhân", "mẹ bệnh nhân", "con trai"...
    thuc_the: str                 # Tên bệnh, thuốc, triệu chứng
    noi_dung: str                 # Diễn giải lâm sàng ngắn gọn
    chac_chan: str                # "chắc chắn" | "nghi ngờ" | "chưa ghi nhận"
    phu_dinh: bool                # True nếu là phủ định ("không sốt", "không khó thở")
    tinh_chat: str                # "sự thật" | "giả định" | "kế hoạch" | "thay thế"
    thoi_gian: Optional[str]      # Mốc thời gian ("3 ngày nay", "hôm rằm")
    bang_chung: List[int]         # Danh sách số thứ tự lượt thoại [T_i]
    trich_dan: List[str]          # Chuỗi trích dẫn nguyên văn từ lời nói
    quan_he: List[Tuple]          # Quan hệ với các phát biểu khác (thay thế, mâu thuẫn)
```

### 5.2 Kết quả khóa bằng chứng (`KetQua` trong `src/khoa_bang_chung.py`)
```python
@dataclass
class KetQua:
    id: int                       # Khớp với id của PhatBieu
    chan: List[str]               # Danh sách mã lý do BỊ CHẶN (xuống CẦN XÁC NHẬN)
    canh_bao: List[str]           # Danh sách mã lý do CẢNH BÁO (vẫn vào thân, xếp cờ)
    doan: List[Tuple[int, int, int]] # (lượt_thoại, vị_trí_đầu, vị_trí_cuối)

    @property
    def qua(self) -> bool:
        return not self.chan     # True nếu vượt qua toàn bộ 7 bài kiểm tra K1-K7
```

### 5.3 Kết quả kiểm duyệt Guardrails (`GuardrailResult` trong `src/guardrails.py`)
```python
@dataclass
class GuardrailResult:
    hop_le: bool                  # Hợp lệ hay vi phạm
    canh_bao: List[str]           # Thông điệp cảnh báo lâm sàng
    goi_y: Dict[str, Any]         # Gợi ý chuẩn hóa (ví dụ: amox -> amoxicillin)
    chi_tiet: str                 # Mã trạng thái (EXACT_MATCH, HALLUCINATION_DETECTED...)
```

---

## 6. HƯỚNG DẪN VẬN HÀNH, CHẠY THỬ VÀ KIỂM THỬ

### 6.1 Môi trường yêu cầu
* Hệ điều hành: Windows / Linux / macOS.
* Python: `>= 3.10` (khuyên dùng Python 3.11).
* Node.js: `>= 18.x` (cho giao diện web).
* Card đồ họa: Tùy chọn (Hỗ trợ GPU CUDA hoặc CPU thuần).

### 6.2 Lệnh chạy toàn bộ kiểm thử tự động (Unit Test Suite)
Dự án có bộ kiểm thử tự động toàn diện với hơn **1.320 bài test** (hiện tại tất cả đều đạt 100%):
```powershell
# Chạy toàn bộ test suite an toàn lâm sàng cốt lõi
pytest tests/test_guardrails.py tests/test_khoa_bang_chung.py tests/test_cong_rui_ro.py tests/test_thang_diem_lam_sang.py

# Kết quả mong đợi: 58 passed in ~25-30s
```

### 6.3 Lệnh khởi động dịch vụ Backend API
Backend chạy dịch vụ HTTP nội bộ tại cổng `8765`:
```powershell
# Khởi động dịch vụ (chế độ nạp nhẹ / ca mẫu đệm)
python -m src.dich_vu --cong 8765

# Kiểm tra sức khỏe hệ thống:
# Mở trình duyệt: http://localhost:8765/api/suc-khoe
```

### 6.4 Lệnh khởi động giao diện Frontend Web
```powershell
cd web
npm install
npm run dev
# Mở trình duyệt tại: http://localhost:5173
```

### 6.5 Lệnh tự động xuất báo cáo thẩm mỹ cao (Word .docx)
```powershell
python tools/tao_bao_cao_nang_cap_word.py
# File xuất ra tại: docs/tai-lieu/Bao_Cao_Nang_Cap_Toan_Dien_MediTrace_Sentinel.docx
```

---

## 7. NHỮNG NGUYÊN TẮC BẤT KHẢ XÂM PHẠM KHI LẬP TRÌNH (CRITICAL INVARIANTS)

Bất kỳ AI hoặc lập trình viên nào tiếp tục phát triển dự án này **BẮT BUỘC** phải tuân thủ nghiêm ngặt 5 nguyên tắc sau:

1. **Tuyệt đối không dùng LLM để viết lại hồ sơ bệnh án dạng văn xuôi:**  
   LLM chỉ được dùng ở Tầng 1 để trích xuất mệnh đề dạng bảng có trích dẫn `[T_i]`. Khâu sinh văn bản ở Tầng 5 bắt buộc phải dùng khuôn mẫu code (`src/sinh_benh_an.py`) để chống gộp nhầm người và chống bịa đặt.
2. **Không bao giờ xóa mất thông tin nguy cấp (Zero Information Loss):**  
   Mọi phát biểu liên quan đến Dị ứng (`di_ung`), Thuốc có khoảng điều trị hẹp (`thuoc_nti`) dù có vi phạm căn cứ K1–K7 cũng **không được xóa bỏ**, mà bắt buộc phải chuyển sang mục `"CẦN BÁC SĨ XÁC NHẬN"` kèm cờ cảnh báo đỏ.
3. **Phân biệt rõ ràng giữa "Chưa ghi nhận" và "Không có":**  
   Nếu trong cuộc khám chưa ai hỏi đến dị ứng, hồ sơ phải ghi là *"Chưa ghi nhận"*, tuyệt đối không được tự ý biến thành khẳng định âm tính *"Không dị ứng"*.
4. **Bắt buộc trích dẫn 2 chiều:**  
   Mọi mệnh đề xuất hiện trong thân bệnh án đều phải có vị trí trỏ ngược về lượt thoại gốc. Không có câu trích $\rightarrow$ Không được phép vào thân hồ sơ.
5. **Bảo mật cục bộ 100%:**  
   Không được thêm bất kỳ thư viện hoặc API nào âm thầm gửi dữ liệu thoại hoặc thông tin bệnh nhân ra các dịch vụ đám mây công cộng bên ngoài.

---

> **LIÊN HỆ & BẢO TRÌ:**  
> Hệ thống MediTrace Sentinel được phát triển với sự cẩn trọng cao nhất cho môi trường y tế. Khi cần mở rộng thêm các thang điểm lâm sàng hoặc bổ sung danh mục tương tác thuốc, hãy chỉnh sửa trực tiếp tại các tệp module độc lập tương ứng trong thư mục `src/` và luôn chạy lại `pytest` để xác nhận không gây xung đột hồi quy.
