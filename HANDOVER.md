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
* **Quy định pháp lý bắt buộc:** Thông tư 46/2018/TT-BYT (bắt buộc số hóa bệnh án điện tử) và Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 cùng Nghị định 356/2025/NĐ-CP (hiệu lực 01/01/2026, thay Nghị định 13/2023/NĐ-CP; dữ liệu sức khỏe là dữ liệu cá nhân nhạy cảm). Dự án chạy tại chỗ nên dữ liệu người bệnh không cần rời phòng khám.
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
│ - Tệp: src/duong_ong/chay_duong_ong.py, src/duong_ong/b1_cau_truc_menh_de.py, src/huan_luyen/chon_mo_hinh_bakeoff.py                                   │
│ - Đọc hội thoại thô -> Xuất danh sách mẩu tin nguyên tử có cấu trúc:                    │
│   PhatBieu: {chu_the, thuc_the, trang_thai, thoi_gian, luot_thoai, trich_dan}           │
│   BẮT BUỘC có trích dẫn nguyên văn chuỗi ký tự trong lượt thoại [T_i]                   │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ TẦNG 2: LIÊN KẾT THỰC THỂ & GOM NHÓM NGƯỜI NÓI (Deterministic Rule-Based)                │
│ - Tệp: src/duong_ong/b2_gom_nguoi_thuc_the.py, src/duong_ong/b3_phan_xu_quan_he.py                                             │
│ - Phân tách rõ ràng: Bác sĩ, Người bệnh (id=0), Người nhà (id=1, 2...)                   │
│ - Đại từ họ hàng tiếng Việt ("bố tôi", "mẹ em", "bé nhà tôi", "ông nhà")                │
│ - Ngăn chặn lỗi nhầm lẫn tiền sử gia đình thành tiền sử bản thân bệnh nhân              │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ TẦNG 3: CẬP NHẬT TRẠNG THÁI & DÒNG THỜI GIAN ĐÍNH CHÍNH (Finite State Machine - FSM)    │
│ - Tệp: src/duong_ong/b3_cap_nhat_trang_thai.py                                                                  │
│ - Tự động nhận diện bệnh nhân tự sửa lời nói: "1 tuần... à không, 10 ngày rồi"          │
│   -> Đánh dấu mẩu tin cũ là "bị thay thế" (K7 Superseded), chỉ giữ lại mẩu tin mới       │
│ - Xử lý thông tin song hành, mâu thuẫn giữa 2 người nói chưa được xác nhận             │
└──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ TẦNG 4: KHÓA BẰNG CHỨNG (K1-K7) & ĐỊNH TUYẾN CỔNG RỦI RO (Fail-Safe Asymmetric Routing) │
│ - Tệp: src/duong_ong/b4_kiem_can_cu.py, src/duong_ong/b5_xep_cho_cong_rui_ro.py, src/he_thong/rao_chan_an_toan.py                    │
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
│ - Tệp: src/duong_ong/b5_viet_ban_nhap.py, src/cong_cu_lam_sang/xuat_fhir_r4.py, src/cong_cu_lam_sang/to_dan_do_benh_nhan.py               │
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
├── BAO_CAO_CAI_TIEN_CHANG_1.md                # Báo cáo cải tiến Chặng 1 (AI 2026) đối chiếu 3 yêu cầu BGK
├── HANDOVER.md                                # TÀI LIỆU NÀY (Bàn giao dự án cho Gemini/AI/Dev)
├── README.md                                  # Hướng dẫn tổng quan ngắn gọn của dự án
├── GIAI_THICH_DU_AN_MEDITRACE_SENTINEL.md     # Bản giải thích toàn diện bối cảnh, lý do, sự khác biệt
├── package.json                               # Cấu hình workspace
├── data/                                      # Dữ liệu mẫu, cache trích xuất (trich_*_hl.jsonl)
├── models/                                    # Thư mục lưu checkpoint QLoRA adapter
│
├── src/                                       # MÃ NGUỒN XỬ LÝ LÕI PYTHON (6 GÓI NGHIỆP VỤ + AUDIO/TRAIN)
│   ├── audio/                                 # Gỡ băng PhoWhisper, tách vai Pyannote & Trie G2P 600 thuốc
│   │   ├── pipeline.py                        # Pipeline gỡ băng & gợi ý vai người nói
│   │   ├── storage.py                         # Quản lý lưu trữ phiên âm thanh cục bộ
│   │   └── asr/                               # schemas.py, disagreement.py, contextual_trie_600.py, phowhisper_provider.py
│   │
│   ├── duong_ong/                             # ĐƯỜNG ỐNG 5 TẦNG (Bước 0 -> Bước 6)
│   │   ├── b0_chuan_hoa_phuong_ngu.py         # Bước 0: Chuẩn hoá phương ngữ 3 miền kèm khiên bảo vệ y khoa
│   │   ├── b1_cau_truc_menh_de.py             # Bước 1: Định nghĩa cấu trúc mệnh đề nguyên tử `PhatBieu`
│   │   ├── b2_gom_nguoi_thuc_the.py           # Bước 2: Gom chủ thể, đại từ nhân xưng & pro-drop (`b2_bu_chu_ngu_tinh_luoc.py`)
│   │   ├── b3_cap_nhat_trang_thai.py          # Bước 3: Máy trạng thái FSM xử lý đính chính & mâu thuẫn
│   │   ├── b4_kiem_can_cu.py                  # Bước 4: Bộ 7 cổng khóa bằng chứng K1–K7 đối soát thoại gốc
│   │   ├── b5_xep_cho_cong_rui_ro.py          # Bước 5a: Phân loại rủi ro (gồm `thuoc_nti`) & cổng cách ly an toàn
│   │   ├── b5_viet_ban_nhap.py                # Bước 5b: Sinh bệnh án SOAP từ mẫu cố định
│   │   └── chay_duong_ong.py                  # Điều phối thực thi & so sánh các nhánh A / C / C_khoa
│   │
│   ├── canh_bao/                              # LỚP CẢNH BÁO 13 NHÓM · 56 MÃ (Chính sách D)
│   │   ├── loai.py, gop.py                    # Phân bậc `LOAI_NANG`, hợp nhất & triage 3 tầng chống mệt mỏi cảnh báo
│   │   └── phat_hien.py, toan_ca.py, lam_sang.py # Bộ phát hiện rơi liều, mất dấu ASR, nhầm chủ thể, thiếu sót & DDI
│   │
│   ├── cong_cu_lam_sang/                      # CÁC MÔ-ĐUN HỖ TRỢ LÂM SÀNG, BHYT & FHIR
│   │   ├── tra_duoc_thu_aho_corasick.py       # Aho-Corasick nạp 158 hoạt chất từ `tri_thuc_thuoc.py`
│   │   ├── canh_bao_tuong_tac_thuoc.py        # Cảnh báo tương tác thuốc DDI & liều trần 24h
│   │   ├── hieu_chinh_lieu.py                 # Hiệu chỉnh liều suy thận (Cockcroft-Gault / CKD-EPI)
│   │   ├── thang_diem_nguy_co.py              # 9 thang điểm (GCS, qSOFA, CURB-65, CHA2DS2-VASc, Wells...)
│   │   ├── doi_soat_can_lam_sang.py           # Báo động đỏ cận lâm sàng & `nap_ket_qua_lis_hl7.py`
│   │   ├── goi_y_cau_hoi_socrates.py          # Nhắc hỏi bù triệu chứng SOCRATES
│   │   ├── xuat_fhir_r4.py                    # Xuất HL7 FHIR R4 Bundle
│   │   ├── tien_kiem_bhyt_va_khoi_phuc_bo_sot.py # Tiền kiểm BHYT XML1–XML5 (TT 26/2025) & `kiem_toan_xml_bhyt.py`
│   │   ├── to_dan_do_benh_nhan.py             # Bản dặn dò đời thường & `ho_so_benh_nhan_qr.py`
│   │   └── cam_doan_thu_thuat.py, di_buong_noi_tru.py # Cam đoan PTTT WORM & Đi buồng nội trú TT 32/2023
│   │
│   ├── he_thong/                              # DỊCH VỤ HTTP, AN TOÀN & BẢO MẬT
│   │   ├── dich_vu_http.py                    # Máy chủ HTTP API nội bộ (cổng 8765) & `hop_dong_api.py`
│   │   ├── khu_dinh_danh.py                   # Khử định danh PHI/PII theo mẫu cấu trúc
│   │   ├── rao_chan_an_toan.py                # Hàng rào đa tầng & `dieu_phoi_cac_chot_an_toan.py`
│   │   └── nhat_ky_ky_duyet_worm.py           # Nhật ký băm WORM SHA-256
│   │
│   ├── bo_du_lieu/ & do_luong/ & huan_luyen/  # KHO 657 KHUÔN BỆNH, ĐO LƯỜNG & HUẤN LUYỆN
│   │   └── kho_khuon.py, sinh_ca_da_benh_ly.py, sinh_hoi_thoai_viet.py, do_canh_bao.py, do_vidia2std.py
│
├── tests/                                     # BỘ KIỂM THỬ TỰ ĐỘNG (1.960+ pytest + 96 TypeScript tests)
│   ├── test_guardrails.py                     # Test hàng rào đa tầng & liều trần
│   ├── test_khoa_bang_chung.py                # Test kịch bản khóa bằng chứng K1–K7
│   ├── test_cong_rui_ro.py                    # Test cổng cách ly an toàn & `thuoc_nti`
│   ├── test_da_nguon_doc_lap.py               # Test phương ngữ 3 miền, G2P ngữ cảnh, 158 hoạt chất & Chính sách D
│   ├── test_thang_diem_lam_sang.py, test_duoc_ly_lam_sang.py, test_hieu_chinh_lieu.py, test_can_lam_sang.py
│   └── test_bo_sinh_goc_khong_doi.py          # Phép thử vàng giữ nguyên 200 khuôn gốc (BAM_VANG SHA-256)
│
├── tools/                                     # CÔNG CỤ ĐO ĐẠC & XUẤT TÀI LIỆU
│   ├── do_da_nguon_doc_lap.py                 # Đánh giá chéo 5 bộ công khai (ViDia2Std, ViHealthQA, ViMedAQA, ViMQ, PhoNER)
│   ├── do_truyen_lan_loi_tung_tang.py         # Đo tỷ lệ chặn lỗi từng tầng đường ống
│   └── tao_cam_nang_giai_thich_va_qna_word.py # Xuất Cẩm nang Word (.docx) & Markdown phản biện BGK
│
├── web/                                       # GIAO DIỆN REACT + BFF NODE/EXPRESS + SQLITE WORM
│   ├── src/components/EvidenceView.tsx        # Màn hình duyệt từng mệnh đề, nối dây đường bằng chứng
│   ├── src/components/DuyetBenCanh.tsx        # Ngăn duyệt nhanh & phát lại âm thanh từng lượt
│   ├── src/components/NoteEditorView.tsx      # Màn hình soạn, sửa, chép HIS, BHYT & ký duyệt WORM
│   └── may-chu/worm.ts                        # Chuỗi băm WORM SHA-256 + tệp neo `.anchor.json`
│
└── docs/                                      # TÀI LIỆU, KẾT QUẢ THỰC NGHIỆM & HÌNH ẢNH DỰ THI
    └── tai-lieu/                              # Cẩm nang Word, Markdown giải thích, Q&A chi tiết
```

---

## 4. CHI TIẾT 14 MODULE NÂNG CẤP MỚI & CÁCH GIẢI QUYẾT BÀI TOÁN

| STT | Tên module & File mã nguồn | Vấn đề thực tế trước đây | Giải pháp công nghệ trong mã nguồn |
| :---: | :--- | :--- | :--- |
| **1** | **Guardrails Đa tầng**<br>[`src/he_thong/rao_chan_an_toan.py`](file:///d:/Claude/meditrace-ma-nguon/src/he_thong/rao_chan_an_toan.py) | Lỗi nghe nhầm ở bước trước sẽ bị các bước sau chép theo dây chuyền. | 5 Guardrail độc lập: Kiểm tra âm vị thuốc ASR; Kiểm tra xung đột đại từ xưng hô; Kiểm tra tự sửa lời nói; Khóa đối soát xâu ký tự; Định tuyến bảo toàn thông tin nguy cấp. |
| **2** | **Dược lý Lâm sàng & DDI**<br>[`src/cong_cu_lam_sang/canh_bao_tuong_tac_thuoc.py`](file:///d:/Claude/meditrace-ma-nguon/src/cong_cu_lam_sang/canh_bao_tuong_tac_thuoc.py) | AI thông thường không biết 2 thuốc kê cùng nhau có gây xuất huyết hoặc tử vong không. | Bảng tra cứu tương tác thuốc DDI theo Dược thư Quốc gia Việt Nam; Kiểm soát liều trần tối đa trong ngày (Paracetamol $\le 4000\text{mg}$, Ibuprofen $\le 2400\text{mg}$...). |
| **3** | **Hiệu chỉnh liều Thận/Gan**<br>[`src/cong_cu_lam_sang/hieu_chinh_lieu.py`](file:///d:/Claude/meditrace-ma-nguon/src/cong_cu_lam_sang/hieu_chinh_lieu.py) | Người suy thận uống liều người bình thường sẽ bị ngộ độc; bác sĩ bận không kịp bấm máy tính tính độ lọc thận. | Áp dụng công thức Cockcroft-Gault tính độ thanh thải Creatinine ($eGFR$), tự động đưa ra khuyến cáo giảm $50\%$ liều hoặc chống chỉ định dùng thuốc. |
| **4** | **9 Thang điểm Lâm sàng**<br>[`src/cong_cu_lam_sang/thang_diem_nguy_co.py`](file:///d:/Claude/meditrace-ma-nguon/src/cong_cu_lam_sang/thang_diem_nguy_co.py) | Trong lúc khám đông, bác sĩ khó nhớ hết các bảng cộng điểm nguy cơ phức tạp. | Tự động tính 9 thang điểm chuẩn y khoa: **NEWS2**, **CURB-65**, **CHA2DS2-VASc**, **HAS-BLED**, **GCS**, **qSOFA**, **NYHA**, **Child-Pugh**, **BMI**. |
| **5** | **Giám sát Cận lâm sàng**<br>[`src/cong_cu_lam_sang/doi_soat_can_lam_sang.py`](file:///d:/Claude/meditrace-ma-nguon/src/cong_cu_lam_sang/doi_soat_can_lam_sang.py) | Giấy xét nghiệm kẹp lẫn trong hồ sơ, bác sĩ chưa kịp xem làm trễ giờ vàng cấp cứu. | Quét dải tham chiếu bình thường; Bật báo động đỏ giá trị nguy kịch (Troponin tăng, Kali máu vọt); Phát hiện mâu thuẫn giữa lời nói và kết quả xét nghiệm. |
| **6** | **Trợ lý Hỏi bù Triệu chứng**<br>[`src/cong_cu_lam_sang/goi_y_cau_hoi_socrates.py`](file:///d:/Claude/meditrace-ma-nguon/src/cong_cu_lam_sang/goi_y_cau_hoi_socrates.py) | Ca khám 3 phút bác sĩ rất dễ quên hỏi kỹ tính chất cơn đau (vị trí, hướng lan, mức độ). | Phân tích khoảng trống bệnh sử theo chuẩn SOCRATES; Hiện sẵn các nút gợi ý câu hỏi để bác sĩ bấm hỏi bổ sung trước khi kết thúc ca khám. |
| **7** | **Khử định danh Bảo mật**<br>[`src/he_thong/khu_dinh_danh.py`](file:///d:/Claude/meditrace-ma-nguon/src/he_thong/khu_dinh_danh.py) | Rò rỉ thông tin cá nhân bệnh nhân (dữ liệu nhạy cảm theo Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15). | Tự động tìm và mã hóa tên, SĐT, số CCCD, số thẻ BHYT thành `[BENH_NHAN_1]`, `[SDT_1]`. Chỉ bác sĩ tại phòng khám mới có chìa khóa giải mã. |
| **8** | **Xuất chuẩn HL7 FHIR R4**<br>[`src/cong_cu_lam_sang/xuat_fhir_r4.py`](file:///d:/Claude/meditrace-ma-nguon/src/cong_cu_lam_sang/xuat_fhir_r4.py) | Dữ liệu các bệnh viện bị phân mảnh, xuất ra chữ Word bác sĩ lại phải gõ tay vào máy. | Đóng gói bệnh án thành cấu trúc chuẩn quốc tế HL7 FHIR Bundle (Patient, Encounter, Condition, Observation, MedicationRequest) cắm thẳng vào EMR bệnh viện. |
| **9** | **Bản dặn dò Đời thường**<br>[`src/cong_cu_lam_sang/to_dan_do_benh_nhan.py`](file:///d:/Claude/meditrace-ma-nguon/src/cong_cu_lam_sang/to_dan_do_benh_nhan.py) | Đơn thuốc viết tắt thuật ngữ chuyên ngành bệnh nhân về nhà không hiểu, uống sai giờ. | Tự động dịch thành bản dặn dò bình dị, chia lịch uống thuốc 4 buổi (Sáng - Trưa - Chiều - Tối, trước/sau ăn), chế độ ăn kiêng và danh mục Dấu hiệu đỏ cấp cứu. |
| **10** | **Phương ngữ & Âm vị thuốc**<br>[`src/cong_cu_lam_sang/tu_dien_phuong_ngu_lam_sang.py`](file:///d:/Claude/meditrace-ma-nguon/src/cong_cu_lam_sang/tu_dien_phuong_ngu_lam_sang.py) | Người bệnh dùng từ địa phương ("trúng gió", "xót ruột") hoặc đọc tên thuốc kiểu dân gian ("a móc", "ô mê"). | Bộ từ điển 60+ thuật ngữ dân gian 3 miền và bảng âm vị thuốc Tây, tự động chuẩn hóa về thuật ngữ y khoa chính tắc. |
| **11** | **Điều phối Phần cứng & SHA-256**<br>[`src/he_thong/dieu_phoi_cac_chot_an_toan.py`](file:///d:/Claude/meditrace-ma-nguon/src/he_thong/dieu_phoi_cac_chot_an_toan.py) | Máy tính phòng khám yếu dễ bị treo RAM; hồ sơ bệnh án điện tử sợ bị sửa lén. | Tự động giải phóng bộ nhớ VRAM/RAM; Tự động đóng dấu băm SHA-256 niêm phong bệnh án sau khi bác sĩ duyệt để bảo đảm giá trị pháp lý trước tòa án. |
| **12** | **Ma trận Đa bệnh lý**<br>[`src/bo_du_lieu/sinh_ca_da_benh_ly.py`](file:///d:/Claude/meditrace-ma-nguon/src/bo_du_lieu/sinh_ca_da_benh_ly.py) | Bệnh nhân thực tế thường mắc nhiều bệnh kết hợp (cấp tính trên nền mạn tính). | Ma trận kết hợp bệnh lý phức tạp (viêm phổi + đái tháo đường + tăng huyết áp), bảo đảm dữ liệu mô phỏng sát thực tế. |
| **13** | **An toàn Bắt nhầm hơn bỏ sót**<br>[`src/canh_bao/`](file:///d:/Claude/meditrace-ma-nguon/src/canh_bao/) | Kiểm tra quá gắt sẽ làm mất các thông tin nguy hiểm (dị ứng, thuốc tim). | Không bao giờ âm thầm xóa bỏ thông tin nghi ngờ; chuyển toàn bộ vào mục "Cần bác sĩ xác nhận" kèm cờ đỏ để bác sĩ tự quyết định. |
| **14** | **657 Khuôn ca bệnh Lâm sàng**<br>[`src/bo_du_lieu/kho_khuon.py`](file:///d:/Claude/meditrace-ma-nguon/src/bo_du_lieu/kho_khuon.py) | Số lượng bài mẫu ít dễ bị học vẹt, thiếu tính khái quát. | 657 khuôn bệnh thuộc 21 hệ cơ quan (200 khuôn gốc + 457 khuôn mở rộng, đếm ngày 24/11/2026). Toàn bộ khuôn mở rộng mang cờ `da_duyet = False`. Sinh 5.000 ca v2 mở rộng đạt 45.835 câu duy nhất (+127% so với v1), tỷ lệ lặp giảm từ 76,92% xuống 47,37% (câu $\ge 8$ từ lặp 42,19%), MTLD đạt 145,4, Distinct-2 đạt 0,0468, 52.634/52.634 trích dẫn khớp nguyên văn 100,0000% và 0 lỗi quy tắc câu. Đóng băng WORM tại `data/manifest_v2_mo_rong_5000.json`. |

---

## 5. CÁC CẤU TRÚC DỮ LIỆU CỐT LÕI (CORE SCHEMAS)

### 5.1 Cấu trúc mệnh đề nguyên tử (`PhatBieu` trong `src/duong_ong/b1_cau_truc_menh_de.py`)
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

### 5.2 Kết quả khóa bằng chứng (`KetQua` trong `src/duong_ong/b4_kiem_can_cu.py`)
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

### 5.3 Kết quả kiểm duyệt Guardrails (`GuardrailResult` trong `src/he_thong/rao_chan_an_toan.py`)
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
Dự án có bộ kiểm thử tự động gồm **1.960+ bài test `pytest`** (25–27 test bỏ qua có điều kiện theo môi trường) và **96 bài test TypeScript & BFF** trong `web/` (cập nhật 27/11/2026):
```powershell
# Chạy toàn bộ kiểm thử Python
$env:PYTHONUTF8="1"; python -m pytest tests/ --basetemp=D:\temp\pytest -q

# Chạy kiểm tra kiểu, test và đóng gói TypeScript (Frontend + Backend BFF)
cd web
npm run lint
npm test
npm run build
```

### 6.3 Lệnh khởi động dịch vụ Backend API
Backend chạy dịch vụ HTTP nội bộ tại cổng `8765`:
```powershell
# Khởi động dịch vụ (chế độ nạp nhẹ / ca mẫu đệm)
python -m src.he_thong.dich_vu_http --cong 8765

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
   LLM chỉ được dùng ở Tầng 1 để trích xuất mệnh đề dạng bảng có trích dẫn `[T_i]`. Khâu sinh văn bản ở Tầng 5 bắt buộc phải dùng khuôn mẫu code (`src/duong_ong/b5_viet_ban_nhap.py`) để chống gộp nhầm người và chống bịa đặt.
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
