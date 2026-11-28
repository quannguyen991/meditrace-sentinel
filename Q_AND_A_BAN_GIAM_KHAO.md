# BỘ CÂU HỎI & TRẢ LỜI PHẢN BIỆN DÀNH CHO BAN GIÁM KHẢO (Q&A DEFENSE SPECIFICATION)
## DỰ ÁN: MEDITRACE SENTINEL — AMBIENT CLINICAL INTELLIGENCE

> **Hướng dẫn sử dụng:**  
> Bộ tài liệu này tổng hợp **Bản đồ cấu trúc dự án** cùng toàn bộ các câu hỏi phản biện từ **dễ đến khó**, phân chia rành mạch giữa **Cấu trúc kiến trúc**, **Lý thuyết y tế/sản phẩm**, **Kỹ thuật/thuật toán chuyên sâu** và **Stress-Test thực chiến**.  
> Mỗi câu trả lời được thiết kế theo công thức: **(1) Trực diện khẳng định $\rightarrow$ (2) Bản chất kỹ thuật/lâm sàng gắn đúng tên mô-đun thật $\rightarrow$ (3) Số liệu thực nghiệm đã kiểm chứng (nêu rõ cả giới hạn còn lại)**.

---

# PHẦN 0: CẤU TRÚC DỰ ÁN & BẢN ĐỒ KIẾN TRÚC TỔNG THỂ

Khi Ban Giám khảo hỏi về **tổ chức mã nguồn, luồng dữ liệu và cách các thành phần phối hợp với nhau**, có thể trình bày theo mô hình **3 khối – 6 gói lõi – 5 tầng xử lý**:

### 1. Sơ đồ luồng dữ liệu đầu – cuối (End-to-End Pipeline)

```text
Âm thanh phòng khám (Mic / File WAV)
  │
  ▼  [Tầng 0 - ASR & Diarization]  (src/audio/)
     PhoWhisper + PyAnnote tách người nói + Trie 65+ G2P tên thuốc (gợi ý, không tự sửa ngầm)
  │
  ▼  [B0 - Chuẩn hóa phương ngữ]   (src/duong_ong/b0_chuan_hoa_phuong_ngu.py)
     Ánh xạ từ vùng miền kèm khóa bảo vệ ngữ cảnh ("tứ chi", "mô mềm", "cấy ghép", "vô kinh", "bờ mi")
  │
  ▼  [B1 - Rút mệnh đề bằng AI]    (src/duong_ong/b1_cau_truc_menh_de.py)  <-- BƯỚC DUY NHẤT DÙNG LLM
     Qwen3-4B QLoRA 4-bit bóc từng mệnh đề PhatBieu gắn bang_chung [T_i] + trich_dan nguyên văn
  │
  ▼  [B2 & B3 - Chủ thể & Trạng thái] (src/duong_ong/b2_*, b3_*)
     Gom nhóm người nói/bù chủ ngữ tỉnh lược -> Máy trạng thái FSM đánh dấu đính chính DA_THAY_THE
  │
  ▼  [B4 - Khóa căn cứ K1–K7]       (src/duong_ong/b4_kiem_can_cu.py)
     7 cổng xác định kiểm tra nguyên văn, chủ thể, phủ định/giả định, thời gian, liều lượng, đính chính
  │
  ▼  [B5 & B6 + Cảnh báo + Lâm sàng] (src/duong_ong/b5_*, b6_*, src/canh_bao/, src/cong_cu_lam_sang/)
     Định tuyến rủi ro (Chính sách C/D) + 13 nhóm/56 mã cảnh báo + 158 hoạt chất Dược thư + DDI + TT 26/2025
  │
  ▼  [BFF + WORM + React UI]       (web/may-chu/ + web/src/)
     Hàng đợi nền SQLite (202 Accepted) -> Bác sĩ rà Cần xác nhận + Click-to-Verify -> WORM SHA-256 (.anchor.json)
```

### 2. Bản đồ tổ chức mã nguồn (`src/`, `web/`, `tools/`, `tests/`, `data/`, `docs/`)

| Thư mục / Gói | Vai trò kiến trúc | Các mô-đun tiêu biểu & quy mô kiểm chứng |
| :--- | :--- | :--- |
| **`src/audio/`** | Thu nhận, chuẩn hóa âm thanh, nhận dạng tiếng nói & tách lượt người nói | `pipeline.py`, `asr/phowhisper_provider.py`, `asr/disagreement.py`, `asr/contextual_trie_600.py` (`65+` ánh xạ G2P tên thuốc chỉ ở mức gợi ý) |
| **`src/bo_du_lieu/`** | Sinh dữ liệu hội thoại mô phỏng, kiểm rò rỉ khuôn & nạp nguồn chuẩn | `kho_khuon.py` (**657 khuôn**, **21 hệ cơ quan**), `chia_tap_theo_khuon.py` (**515 Train / 72 Dev / 70 Test** không trùng khuôn), `phuong_ngu.py`, `sinh_hoi_thoai_viet.py`, `ca_mau_bgk.py` (3 ca trình diễn) |
| **`src/duong_ong/`** | Lõi Neuro-Symbolic (`B0`–`B6`), nơi ghép AI với chuỗi thuật toán xác định | `chay_duong_ong.py` (ghép toàn trình), `b0_chuan_hoa_phuong_ngu.py`, `b1_cau_truc_menh_de.py` (`PhatBieu`), `b2_gom_nguoi_thuc_the.py`, `b2_bu_chu_ngu_tinh_luoc.py`, `b3_cap_nhat_trang_thai.py`, `b4_kiem_can_cu.py` (K1–K7), `b5_xep_cho_cong_rui_ro.py`, `b5_viet_ban_nhap.py`, `b6_goi_y_hoi_lai.py` |
| **`src/canh_bao/`** | Phát hiện & phân tầng rủi ro 3 mức (`Nặng / Cần hỏi / Thông tin`) | `loai.py` (**13 nhóm, 56 mã lỗi**, gồm `thuoc_nti`, thiếu liều, lẫn người nhà, ASR không dấu), `phat_hien.py`, `toan_ca.py`, `bo_sot.py`, `gop.py` |
| **`src/cong_cu_lam_sang/`** | Kiểm tra an toàn dược lý, thang điểm, BHYT & liên thông bệnh viện | `tra_duoc_thu_aho_corasick.py` (**158 hoạt chất**), `canh_bao_tuong_tac_thuoc.py` (DDI), `hieu_chinh_lieu.py`, `thang_diem_nguy_co.py` (**9 thang điểm**), `tien_kiem_bhyt_va_khoi_phuc_bo_sot.py` (13 quy tắc CLS + cân nặng trẻ em TT 26/2025), `xuat_fhir_r4.py`, `nap_ket_qua_lis_hl7.py`, `ho_so_benh_nhan_qr.py`, `goi_y_cau_hoi_socrates.py`, `tu_dien_phuong_ngu_lam_sang.py` |
| **`src/do_luong/`** | Đánh giá định lượng SER, Attribution F1, độ lặp câu & ngoài khuôn | `cham_he_thong.py`, `do_canh_bao.py`, `do_lap_cau.py`, `do_vidia2std.py`, `kiem_nghiem_ngoai_khuon.py` |
| **`src/he_thong/`** | API dịch vụ Python, khử định danh PII, điều phối 5 chốt an toàn & WORM | `dich_vu_http.py` (HTTP `:8765`, cấu hình socket ổn định trên Windows), `hop_dong_api.py`, `khu_dinh_danh.py`, `dieu_phoi_cac_chot_an_toan.py`, `nhat_ky_ky_duyet_worm.py` |
| **`src/huan_luyen/`** | Huấn luyện & so sánh mô hình SFT / DPO / RLVR trên Qwen3-4B QLoRA | `chon_mo_hinh_bakeoff.py`, `huan_luyen_sft.py`, `huan_luyen_dpo.py`, `loss_theo_doan.py` |
| **`web/may-chu/`** | Backend BFF (Node.js/Express + TypeScript + SQLite WAL) | `csdl.ts`, `hang-doi.ts` (xử lý nền `202 Accepted`), `worm.ts` (chuỗi băm SHA-256 + `.anchor.json`), `routes/ca-kham.ts`, `routes/sign-off.ts`, `tro-ly/an-danh.ts` (allowlist khi bật trợ lý ngoài), `tra-cuu/kiem-dinh-so.ts` |
| **`web/src/`** | Giao diện bác sĩ, điều hành bệnh viện & cổng bệnh nhân (React 19 + TS) | `TranscriptView.tsx`, `VerificationView.tsx` (phím tắt `J/K/Enter/Space`, `Giữ nhanh`), `DuyetBenCanh.tsx`, `NoteEditorView.tsx`, `HisSmartCopyPopover.tsx`, `BhytPrecheckModal.tsx`, `HospitalCommandCenterView.tsx`, `PatientPortalView.tsx`, `hooks/useTurnAudioPlayer.ts` |
| **`tools/`, `tests/`, `docs/`** | Kịch bản đo đạc, sinh tài liệu & bộ kiểm thử hồi quy | `tools/do_da_nguon_doc_lap.py` (5 bộ dữ liệu độc lập), `tools/tao_word_qna_giam_khao.py`, `tests/` (**1.974 pytest pass, 25 skip** + **96/96 TS tests**), `docs/ket-qua/` |

---

# PHẦN 1: CÂU HỎI LÝ THUYẾT, NGHIỆP VỤ LÂM SÀNG & GIÁ TRỊ SẢN PHẨM

---

### [DỄ] Câu 1: MediTrace Sentinel giải quyết vấn đề gì lớn nhất trong bệnh viện?
* **Trả lời:**  
  * **Vấn đề giải quyết:** Bác sĩ ngoại trú tại bệnh viện đông bệnh nhân đang chịu áp lực quá tải nặng (nhiều phòng khám tiếp nhận hàng chục ca mỗi ngày), vừa khám hỏi vừa phải nhập bệnh án điện tử (EMR/HIS), dễ mệt mỏi (burnout), giảm giao tiếp mắt với người bệnh và có nguy cơ ghi sót tiền sử hoặc dị ứng.
  * **Giải pháp:** MediTrace đóng vai trò **trợ lý dựng bản nháp bệnh án theo nguồn thoại (Evidence-Linked Ambient Clinical Scribe)**: lắng nghe cuộc hội thoại tự nhiên, tự động gỡ băng, bóc tách thành cấu trúc SOAP kèm bằng chứng nguyên văn và phân loại sẵn các mục rủi ro vào hàng đợi *"Cần xác nhận"*. Bác sĩ không phải gõ lại từ đầu, chỉ tập trung kiểm tra các điểm có cờ cảnh báo, dùng phím tắt (`J/K/Enter/Space`, `Giữ nhanh`) và copy nhanh sang HIS qua `HisSmartCopyPopover`.

---

### [DỄ] Câu 2: Tại sao không dùng luôn ChatGPT, Claude hay Gemini cho nhanh và rẻ?
* **Trả lời:**  
  Có 3 lý do sống còn khiến việc dùng chatbot đám mây trực tiếp tại bệnh viện tiềm ẩn rủi ro pháp lý và an toàn lâm sàng:
  1. **Bảo vệ dữ liệu nhạy cảm (Nghị định 13/2023/NĐ-CP):** Gửi nguyên văn lời thoại có họ tên, địa chỉ, số điện thoại, số CCCD, mã bệnh nhân ra máy chủ bên ngoài vi phạm nguyên tắc kiểm soát dữ liệu y tế. MediTrace mặc định chạy **100% On-premise nội bộ** (`PhoWhisper` + `Qwen3-4B` + `SQLite`). Chế độ trợ lý bên ngoài mặc định **TẮT** (`MEDITRACE_TRO_LY_NGOAI=tat`), và ngay cả khi cơ sở y tế chủ động bật, bộ lọc allowlist tại [`web/may-chu/tro-ly/an-danh.ts`](file:///d:/Claude/meditrace-ma-nguon/web/may-chu/tro-ly/an-danh.ts) kết hợp [`src/he_thong/khu_dinh_danh.py`](file:///d:/Claude/meditrace-ma-nguon/src/he_thong/khu_dinh_danh.py) vẫn bắt buộc khử định danh trước khi rời máy chủ nội bộ.
  2. **Rủi ro ảo giác AI (Hallucination):** Chatbot tổng quát có thể viết trơn tru những thông tin bệnh nhân không nói hoặc trộn bệnh của người nhà thành của bệnh nhân. MediTrace áp dụng 7 cổng khóa căn cứ **K1–K7** tại [`src/duong_ong/b4_kiem_can_cu.py`](file:///d:/Claude/meditrace-ma-nguon/src/duong_ong/b4_kiem_can_cu.py) để chặn và gắn cờ các mệnh đề không có trích dẫn nguyên văn hoặc sai chủ thể/liều/thời gian.
  3. **Khả năng kiểm chứng tức thì:** Chatbot trả ra một khối văn xuôi khó đối chiếu. MediTrace liên kết từng dòng bệnh án ngược về đúng lượt thoại `[T_i]` và đoạn âm thanh gốc qua [`web/src/hooks/useTurnAudioPlayer.ts`](file:///d:/Claude/meditrace-ma-nguon/web/src/hooks/useTurnAudioPlayer.ts) (*Click-to-Verify*).

---

### [TRUNG BÌNH] Câu 3: Bác sĩ rất bận, liệu việc bắt bác sĩ ngồi duyệt từng dòng có làm mất thêm thời gian không?
* **Trả lời:**  
  * **Thiết kế giao diện hướng tới giảm thao tác đọc dư thừa, không bắt bác sĩ đọc lại toàn bộ từ đầu đến cuối** (lưu ý: đội ngũ chưa công bố con số *"tiết kiệm X phút/ca"* ngoài đời thực khi chưa hoàn tất thử nghiệm đo thời gian bấm giờ trực tiếp trên bác sĩ lâm sàng).
  * Về mặt luồng thao tác, màn hình duyệt của MediTrace tách thành 2 lớp rõ ràng trong [`web/src/components/VerificationView.tsx`](file:///d:/Claude/meditrace-ma-nguon/web/src/components/VerificationView.tsx) và [`web/src/components/DuyetBenCanh.tsx`](file:///d:/Claude/meditrace-ma-nguon/web/src/components/DuyetBenCanh.tsx):
    * **Phần thân bản nháp (đã qua K1–K7 và không thuộc nhóm cờ rủi ro):** Gom các mệnh đề đạt căn cứ, hỗ trợ thao tác *Giữ nhanh* thay vì bắt sửa tay từng câu.
    * **Mục *"Cần bác sĩ xác nhận"*:** Gom riêng những điểm có cờ đỏ/vàng (lời đính chính, mệnh đề nghi ngờ/giả định, thuốc có khoảng điều trị hẹp, tên thuốc dân gian gợi ý từ ASR, tương tác thuốc) để bác sĩ tập trung xử lý bằng phím tắt `J / K / Enter / Space`.
  * Ngoài ra, khâu chạy mô hình nặng được đẩy qua hàng đợi nền `202 Accepted` ([`web/may-chu/hang-doi.ts`](file:///d:/Claude/meditrace-ma-nguon/web/may-chu/hang-doi.ts)), giúp bác sĩ chuyển sang ca khám tiếp theo mà không phải ngồi nhìn thanh chờ.

---

### [TRUNG BÌNH] Câu 4: Nếu phần mềm ghi nhầm hoặc gợi ý sai dẫn đến tai biến y khoa thì ai chịu trách nhiệm?
* **Trả lời:**  
  * **Về mặt pháp lý:** Bác sĩ khám chữa bệnh luôn là người chịu trách nhiệm chuyên môn cuối cùng. MediTrace được định vị là **công cụ hỗ trợ soạn thảo bản nháp có căn cứ (Source-Grounded Drafting Copilot)**, không tự động ký y lệnh hay thay thế quyết định lâm sàng.
  * **Về mặt kỹ thuật bảo vệ thầy thuốc và kiểm toán nội bộ:**
    1. **Truy vết hai chiều:** Mọi mệnh đề trong bản nháp đều liên kết tới `bang_chung` `[T_i]`, `trich_dan` nguyên văn và đoạn âm thanh gốc, giảm tranh chấp *"bệnh nhân có nói nhưng không được ghi nhận"*.
    2. **Cổng khóa trước khi ký duyệt + Sổ kiểm toán WORM:** Chốt kiểm tra phía trình duyệt/BFF (`web/may-chu/routes/sign-off.ts`) chặn hoàn tất ký duyệt nếu vẫn còn mục *"Cần xác nhận"* chưa xử lý. Sau khi bác sĩ bấm duyệt, [`web/may-chu/worm.ts`](file:///d:/Claude/meditrace-ma-nguon/web/may-chu/worm.ts) và [`src/he_thong/nhat_ky_ky_duyet_worm.py`](file:///d:/Claude/meditrace-ma-nguon/src/he_thong/nhat_ky_ky_duyet_worm.py) ghi bản ghi WORM nối chuỗi băm **SHA-256** (`prev_hash` $\rightarrow$ `entry_hash`) kèm tệp neo ngoại biên **`.anchor.json`** để phát hiện mọi hành vi sửa/xoá lén dưới SQLite. Đây là **sổ kiểm toán kỹ thuật chống chối bỏ nội bộ**, chưa thay thế chữ ký số CA theo Luật Giao dịch điện tử.
    3. **Cảnh báo dược lý:** Bộ tra **158 hoạt chất** (`tra_duoc_thu_aho_corasick.py`) và bộ kiểm tra DDI (`canh_bao_tuong_tac_thuoc.py`) đóng vai trò nhắc cảnh báo khi có cặp thuốc kỵ nhau hoặc thiếu cân nặng trẻ em theo TT 26/2025.

---

### [KHÓ] Câu 5: Trong y tế có sự đánh đổi: Kiểm tra quá chặt thì bỏ sót thông tin (Low Recall), nới lỏng thì bị sai (Low Precision). MediTrace giải quyết sự đánh đổi này như thế nào?
* **Trả lời:**  
  * **Hệ thống áp dụng triết lý "Định tuyến bất đối xứng theo độ rủi ro" (Fail-Safe Asymmetric Routing)** tại [`src/duong_ong/b5_xep_cho_cong_rui_ro.py`](file:///d:/Claude/meditrace-ma-nguon/src/duong_ong/b5_xep_cho_cong_rui_ro.py) và [`src/canh_bao/`](file:///d:/Claude/meditrace-ma-nguon/src/canh_bao/):
    * Với thông tin nhẹ, ít rủi ro sinh mạng: Ưu tiên độ chính xác (Precision); nếu trượt K1–K7 thì không đưa vào thân bệnh án sạch.
    * Với nhóm nguy cấp (Dị ứng, Thuốc có khoảng điều trị hẹp `thuoc_nti` như Digoxin/Warfarin, Đe dọa tính mạng, Lẫn người nhà, Bất đồng liều): Áp dụng nguyên tắc **không âm thầm xoá bỏ**, định tuyến giữ lại trong mục *"CẦN BÁC SĨ XÁC NHẬN"* kèm cờ đỏ/vàng. Chốt chặn ký duyệt khóa không cho hoàn tất hồ sơ khi còn mục chưa được bác sĩ xử lý (`Xác nhận / Sửa / Bỏ`).
  * **Kết quả thực nghiệm đã đo và minh bạch phạm vi:**
    * Trên phép đo cấy lỗi có đăng ký trước ([`docs/ket-qua/cay-loi.md`](file:///d:/Claude/meditrace-ma-nguon/docs/ket-qua/cay-loi.md)), độ nhạy bắt lỗi xoá dị ứng (`xoa_di_ung`) đạt **98,3%** trên tập điều chỉnh (400 ca) và **97,2%** trên tập giữ kín (240 ca).
    * Ở bước khóa căn cứ K1–K7 trên đáp án chuẩn, tỷ lệ chặn nhầm là **$0 / 30.136$ dòng**.
    * Trên **4 bộ thử thách phát triển** (`300 ca`, `2.789 phát biểu` đối chiếu bộ chấm tự động dùng để tinh chỉnh luật), khi nâng cấp từ **Chính sách C** lên **Chính sách D** (bổ sung phát hiện `thuoc_nti`, thiếu liều, lẫn họ thuốc, ASR mất dấu), tỷ lệ **lọt lỗi nguy hiểm vào thân bệnh án (`lot_nguy_hiem`) giảm từ 45,9% (101/220) xuống còn 11,8% (26/220)** — tương ứng **chặn được 88,2% (194/220)** các trường hợp lỗi nguy hiểm mà bộ chấm gắn nhãn, trong khi tỷ lệ chặn thừa tăng nhẹ từ **8,0%** (C) lên **10,0%** (D). Trên tập giữ kín `thach_thuc_v2` (240 ca), độ nhạy phát hiện đạt **0,871**, độ nhạy đổi chủ thể đạt **0,946**.

---

### [KHÓ] Câu 6: Người Việt Nam khi đi khám nói năng lộn xộn, hay nuốt chủ ngữ, xưng hô "con/cháu/ông nhà", dùng từ địa phương ("trúng gió", "xót ruột"). Làm sao hệ thống của bạn xử lý được?
* **Trả lời:**  
  Đây là điểm bản địa hóa chuyên sâu cho tiếng Việt lâm sàng, gồm 4 lớp xử lý phối hợp:
  1. **Gom nhóm chủ thể xưng hô tiếng Việt (`src/duong_ong/b2_gom_nguoi_thuc_the.py`):** Phân biệt rạch ròi vai người nói (`nguoi_noi`) với người mang triệu chứng/bệnh (`chu_the_id`), ví dụ mẹ nói *"Cháu nhà em sốt từ tối qua"* $\rightarrow$ gán chủ thể là người bệnh (`con/cháu`), không lẫn sang người mẹ.
  2. **Bù chủ ngữ tỉnh lược (`src/duong_ong/b2_bu_chu_ngu_tinh_luoc.py`):** Với câu cụt không chủ ngữ (*"Ho cả đêm qua, không sốt"*), mô-đun đối chiếu bối cảnh lượt thoại liền kề và vai `nguoi_noi` để bù đúng chủ thể thay vì bỏ trống.
  3. **Chuẩn hóa phương ngữ 3 miền kèm khóa bảo vệ ngữ cảnh (`src/duong_ong/b0_chuan_hoa_phuong_ngu.py` & `src/cong_cu_lam_sang/tu_dien_phuong_ngu_lam_sang.py`):** Quy đổi từ địa phương Bắc–Trung–Nam (như *"trúng gió"*, *"xót ruột"*, *"mắc ói"*, *"nhức đầu"*, *"đi cầu"*) và tích hợp **guard ngữ cảnh y khoa** (ví dụ không thay nhầm *"chi"* trong *"tứ chi"*, *"mô"* trong *"mô mềm"*, *"cấy"* trong *"cấy ghép"*, *"kinh"* trong *"vô kinh"*, *"mi"* trong *"bờ mi"*). Trên `ViDia2Std/test.csv` (1.603 câu), mô-đun đạt **28,0%** đúng chuẩn xác từng cụm và **37,1%** tổng độ phủ quy đổi cụm phương ngữ, kéo WER giảm từ **30,1% xuống 21,9%**.
  4. **Gợi ý âm vị G2P tên thuốc (`src/audio/asr/contextual_trie_600.py`) & Dược thư (`tra_duoc_thu_aho_corasick.py`):** Hỗ trợ hơn **65 ánh xạ phiên âm dân gian** (*"a móc"*, *"ô mê"*, *"pa ra"*) kèm điều kiện ngữ cảnh thuốc (*uống/viên/mg/liều*) để giảm khớp nhầm từ thông thường; kết hợp đối chiếu danh mục **158 hoạt chất** chuẩn, luôn ở dạng gợi ý chờ bác sĩ xác nhận.

---

# PHẦN 2: CÂU HỎI KỸ THUẬT, THUẬT TOÁN & CÔNG NGHỆ CHUYÊN SÂU

---

### [DỄ] Câu 7: Kiến trúc tổng thể của MediTrace gồm những thành phần công nghệ nào?
* **Trả lời:**  
  Hệ thống được tổ chức sạch theo **kiến trúc Neuro-Symbolic 5 tầng** kết hợp nền tảng Web Full-Stack nội bộ:
  * **Tầng Âm thanh & Tiền xử lý (`src/audio/` + `B0`):** `PhoWhisper` + `PyAnnote` tách giọng người nói, bộ đo bất đồng ASR (`disagreement.py`), trie gợi ý **65+** âm vị thuốc G2P (`contextual_trie_600.py`) và chuẩn hóa phương ngữ 3 miền (`b0_chuan_hoa_phuong_ngu.py`).
  * **Tầng 1 — Rút mệnh đề bằng AI (`b1_cau_truc_menh_de.py`):** Mô hình nguồn mở **Qwen3-4B** gắn adapter **QLoRA 4-bit** là **khâu duy nhất dùng LLM**, trả về JSON có cấu trúc `PhatBieu` kèm lượt thoại căn cứ và chuỗi trích nguyên văn.
  * **Tầng 2 đến Tầng 5 — Chuỗi thuật toán xác định (`src/duong_ong/`, `src/canh_bao/`, `src/cong_cu_lam_sang/`):** 100% Python xác định (không phụ thuộc xác suất sinh văn bản của LLM): gom chủ thể & bù tỉnh lược (`B2`), máy trạng thái hữu hạn FSM cập nhật đính chính (`B3`), 7 cổng khóa căn cứ **K1–K7** (`B4`), định tuyến rủi ro Chính sách C/D & dựng bản nháp SOAP (`B5`), gợi ý hỏi lại (`B6`), cảnh báo 13 nhóm/56 mã lỗi, Dược thư 158 hoạt chất, DDI, 9 thang điểm nguy cơ, tiền kiểm BHYT TT 26/2025 và xuất FHIR R4.
  * **Tầng Ứng dụng Web & Lưu trữ (`web/may-chu/` + `web/src/` + `src/he_thong/`):** Node.js/Express BFF + SQLite WAL + hàng đợi nền `202 Accepted` + sổ kiểm toán WORM SHA-256 (`.anchor.json`), giao tiếp qua REST API nội bộ với React 19 + TypeScript + TailwindCSS và dịch vụ suy luận Python (`dich_vu_http.py` cổng `8765`).

---

### [DỄ] Câu 8: Tại sao lại chọn mô hình Qwen3-4B mà không chọn Llama-3-8B hay mô hình lớn hơn?
* **Trả lời:**  
  1. **Khả năng triển khai tại phòng khám (Hardware Feasibility):** Máy trạm phòng khám phổ thông thường chỉ có **6GB–8GB VRAM** (như RTX 3050/3060). Mô hình 8B trở lên yêu cầu VRAM và RAM lớn hơn đáng kể khi nạp trọng số lẫn KV cache, làm đội chi phí đầu tư phòng khám. **Qwen3-4B QLoRA 4-bit** gọn nhẹ đủ để chạy cục bộ trên GPU 8GB VRAM tại phòng khám.
  2. **Kiến trúc bất đồng bộ cho bài toán thời gian suy luận:** Nhóm trình bày trung thực thực tế đo đạc: khi chạy bằng PyTorch (`transformers`) mặc định chưa tăng tốc trên RTX 3060 8GB, thời gian suy luận một ca đầy đủ khoảng **~3,5 phút/ca** (chưa phải *30–45 giây*). Thay vì phóng đại con số, MediTrace giải quyết trực tiếp trên luồng làm việc qua **hàng đợi nền `202 Accepted`** trong SQLite ([`web/may-chu/hang-doi.ts`](file:///d:/Claude/meditrace-ma-nguon/web/may-chu/hang-doi.ts)): bác sĩ bấm kết thúc ghi âm là quay sang khám bệnh nhân tiếp theo ngay với **0 giây đứng chờ UI**, bản nháp được xử lý ngầm và báo sẵn khi hoàn tất; hướng tối ưu phần mềm tiếp theo là chuyển engine suy luận sang `vLLM` / `llama.cpp` + `XGrammar` để kéo độ trễ xuống mục tiêu **15–25 giây/ca**.
  3. **Chất lượng trích xuất chuyên biệt qua QLoRA:** Sau tinh chỉnh QLoRA trên dữ liệu hội thoại tiếng Việt lâm sàng, trên 30 ca phát triển độc lập (304 mệnh đề), adapter Qwen3-4B kéo tỷ lệ bỏ sót xuống **11,5%** (khoảng tin cậy 95%: 8,4%–15,6%) với **0 ca lỗi cấu trúc JSON** (so với **43,1%** bỏ sót trước huấn luyện).

---

### [TRUNG BÌNH] Câu 9: Tại sao dự án chỉ dùng AI ở Bước B1 để chia câu nói thành từng mệnh đề (`PhatBieu`), còn Bước B2–B5 lại dùng thuật toán luật? Sao không để AI viết thẳng bệnh án End-to-End?
* **Trả lời:**  
  * **Bản chất tại sao B1 phải tách câu nói thành từng mệnh đề nguyên tử (`PhatBieu`):**
    1. Trong hội thoại tự nhiên tiếng Việt, một lượt nói thường **trộn nhiều chủ thể, nhiều mốc thời gian và cả lời tự đính chính** (ví dụ: *"Bác sĩ ơi hôm qua tôi tưởng đau dạ dày, mà sáng nay siêu âm lại ra sỏi mật; còn mẹ tôi thì dị ứng penicillin"*).
    2. Nếu không tách ra từng mệnh đề `PhatBieu` (`noi_dung`, `nguoi_noi`, `chu_the_id`, `phu_dinh`, `do_chac_chan`, `tinh_huong`, `moc_thoi_gian`, `bang_chung`, `trich_dan`, `quan_he`, `thuoc`, `audio_spans`), việc kiểm tra căn cứ sẽ mất chính xác: một đoạn dài có thể chứa 1 ý đúng và 1 ý bịa hoặc lẫn chủ thể.
    3. Nhờ chuẩn hóa đầu ra B1 thành danh sách các `PhatBieu` nguyên tử, máy trạng thái B3 mới đánh dấu chính xác riêng ý *"đau dạ dày"* thành `DA_THAY_THE` khi có câu siêu âm đính chính, các cổng K1–K7 ở B4 mới kiểm tra từng câu trích nguyên văn, và B5 mới chỉ tách riêng mệnh đề nghi ngờ sang *"Cần xác nhận"* mà vẫn giữ nguyên các thông tin sạch khác.
  * **Lý do kiến trúc Lai Neuro-Symbolic (AI ở B1 + Rule ở B2–B5):**
    * AI (LLM) giỏi hiểu ngữ nghĩa tự do, từ đồng nghĩa và bóc tách mệnh đề; nhưng yếu ở tính nhất quán logic, đếm liều và kiểm soát ranh giới.
    * Tách phần B2–B5 thành thuật toán Python xác định giúp mọi quy tắc (gom chủ thể, máy trạng thái đính chính, tra 158 hoạt chất, đối soát K1–K7) **minh bạch 100%**, truy vết được lỗi sai ở đúng mô-đun và kiểm thử được bằng **1.974 unit/integration tests** mà không cần huấn luyện lại mô hình.

---

### [TRUNG BÌNH] Câu 10: Cơ chế Khóa bằng chứng K1–K7 ở Tầng 4 hoạt động cụ thể như thế nào để chặn Hallucination?
* **Trả lời:**  
  Mỗi `PhatBieu` do B1 trích xuất bắt buộc mang `bang_chung` (chỉ số lượt thoại `[T_i]`) và `trich_dan` (chuỗi trích dẫn nguyên văn). Mô-đun [`src/duong_ong/b4_kiem_can_cu.py`](file:///d:/Claude/meditrace-ma-nguon/src/duong_ong/b4_kiem_can_cu.py) chạy 7 chốt chặn xác định:
  * **K1 (Nguồn gốc nguyên văn):** Dò trực tiếp xâu `trich_dan` trong lượt thoại `[T_i]`. Không khớp $\rightarrow$ chặn ngay (`trich_khong_co`).
  * **K2 (Khớp nội dung):** Kiểm tra độ phủ từ khóa lâm sàng cốt lõi giữa `noi_dung` và `trich_dan`.
  * **K3 (Khớp chủ thể):** Đối chiếu đại từ/tên gọi trong lượt thoại với `chu_the_id` được gán.
  * **K4 (Khớp mức khẳng định & điều kiện):** Chặn trường hợp bệnh nhân chỉ nói nghi ngờ hoặc câu điều kiện phòng ngừa (*"Nếu tối nay sốt lại thì uống..."*) nhưng bị ghi thành sự thật khẳng định (`dieu_kien`).
  * **K5 (Khớp mốc thời gian):** Thời gian được gán (`moc_thoi_gian` / `thoi_gian_su_kien`) phải có căn cứ trong lượt thoại.
  * **K6 (Khớp liều lượng & thuốc):** Kiểm tra số lượng/đơn vị liều (mg, g, ml, mcg, UI, viên...) khi phát biểu thuộc họ liều (`s.ho == "lieu"`) để tránh lệch liều hay khớp nhầm đơn vị thường.
  * **K7 (Kiểm tra đính chính — Superseded):** Các phát biểu đã bị câu sau phủ định hoặc xét nghiệm loại trừ (FSM ở B3 đánh dấu `DA_THAY_THE`) bị loại khỏi phần thân bệnh án khẳng định.

---

### [KHÓ] Câu 11: Tại sao trong báo cáo khẳng định điểm ROUGE (thước đo AI văn bản phổ biến) là vô dụng trong đánh giá bệnh án? Dự án dùng thước đo nào thay thế?
* **Trả lời:**  
  * **Thực nghiệm chứng minh ROUGE không đo được an toàn y khoa:**  
    Trong phép thử trên 400 ca bệnh của dự án, khi cố ý hoán đổi vai trò **"bệnh nhân"** và **"người nhà"** (lỗi lâm sàng nghiêm trọng: biến bệnh của người nhà thành bệnh của người bệnh):
    $$\text{Điểm ROUGE-1 vẫn đạt } \mathbf{1.0000}$$
    Nguyên nhân: ROUGE chỉ đếm trùng lặp túi từ (bag-of-words), không phân biệt chủ thể gắn với từng triệu chứng.
  * **Thước đo thay thế của dự án (`src/do_luong/cham_he_thong.py`):**  
    1. **Entity Slot Error Rate (SER)** và **Attribution F1:** Chấm trực tiếp trên từng bộ giá trị `(Chủ thể, Nội dung/Thuốc, Trạng thái, Mốc thời gian)`.
    2. **Tỷ lệ sót thông tin bị thay thế (Superseded Retention):** Nhờ Cổng K7 và máy trạng thái B3, tỷ lệ sót thông tin cũ đã bị người nói tự đính chính giảm từ **11,48% xuống 0,80%** (giảm hơn **14 lần**).

---

### [KHÓ] Câu 12: Dữ liệu huấn luyện của bạn là dữ liệu mô phỏng (Synthetic Data). Làm sao chứng minh mô hình không bị "học vẹt" (overfitting) và có tính tổng quát?
* **Trả lời:**  
  Dự án kiểm soát rủi ro rò rỉ dữ liệu qua 4 lớp độc lập:
  1. **Chia tách không trùng khuôn (Template-Disjoint Split):** **657 khuôn ca bệnh** thuộc **21 hệ cơ quan lâm sàng** (`src/bo_du_lieu/kho_khuon.py`) được tách độc lập thành **515 khuôn Train / 72 khuôn Dev / 70 khuôn Test** (`chia_tap_theo_khuon.py`). Độ tương đồng Jaccard từ khóa triệu chứng trung bình giữa Train và Test chỉ **5,87%**, bảo đảm tập Test kiểm tra trên các mẫu ca chưa từng xuất hiện khi huấn luyện.
  2. **Kiểm chứng đa dạng ngôn ngữ (`src/do_luong/do_lap_cau.py`):** Kho hội thoại mô phỏng v2 (**5.000 hội thoại**) đạt **45.835 câu duy nhất** (+127% so với v1), giảm tỷ lệ lặp câu từ 76,92% xuống **47,37%** (với câu $\ge 8$ từ còn **42,19%**), MTLD đạt **145,4** (+56,3%), Distinct-2 đạt **0,0468** (+148,9%) và **52.634/52.634 (100%)** trích dẫn đều là chuỗi con nguyên văn.
  3. **Tập thách thức đối lập (Adversarial Contrastive Pairs):** Trên các cặp ca bệnh đổi duy nhất một yếu tố ranh giới (đổi người mang dị ứng, tự đính chính, nhiễu ASR, phương ngữ 3 miền), nhánh C cải thiện $F_1$ từ **66,1% lên 70,8%** và giảm SER từ **45,4% xuống 36,9%**.
  4. **Kiểm nghiệm ngoài khuôn & dữ liệu công khai bên thứ ba:** Bổ sung **10 kịch bản bệnh hiếm ngoài khuôn** (`src/do_luong/kiem_nghiem_ngoai_khuon.py`) và đối chiếu độc lập trên **5 bộ dữ liệu tiếng Việt bên ngoài** (`tools/do_da_nguon_doc_lap.py` — xem chi tiết ở Câu 18).

---

### [KHÓ] Câu 13: Hệ thống Guardrails 5 chốt chặn giải quyết hiện tượng Cascading Errors (Lỗi dây chuyền) như thế nào?
* **Trả lời:**  
  * **Cơ chế Cascading Error:** Nếu đầu vào ASR nghe sai tên thuốc hoặc mất dấu tiếng Việt, lỗi ở tầng đầu có thể được AI chép lại nguyên văn vào `trich_dan` ở B1 và đi qua phép khớp xâu của B4 nếu không có chốt kiểm tra độc lập ở từng tầng.
  * **5 chốt điều phối tại [`src/he_thong/dieu_phoi_cac_chot_an_toan.py`](file:///d:/Claude/meditrace-ma-nguon/src/he_thong/dieu_phoi_cac_chot_an_toan.py):**
    * **Chốt 1 (ASR & Chuẩn hóa đầu vào):** Gắn trie gợi ý G2P **65+** thuốc dân gian có khóa ngữ cảnh, phát hiện bất thường ASR/không dấu và chuẩn hóa phương ngữ 3 miền kèm guard bảo vệ cụm từ y khoa (`B0`).
    * **Chốt 2 (Speaker Guardrail):** Kiểm tra nhất quán vai `nguoi_noi` với `chu_the_id` và bù chủ ngữ tỉnh lược (`B2`).
    * **Chốt 3 (Dialogue Act & FSM Gate):** Tách câu nghi vấn, câu giả định điều kiện và cập nhật trạng thái đính chính `DA_THAY_THE` (`B3`).
    * **Chốt 4 (Evidence Integrity Gate K1–K7):** Kiểm tra nguyên văn trích dẫn, khẳng định, thời gian và hàm lượng/đơn vị liều (`B4`).
    * **Chốt 5 (Clinical Safety & WORM Gate):** Kiểm tra **158 hoạt chất**, tương tác DDI, liều trần, quy tắc BHYT/TT 26/2025, đẩy nhóm nguy hiểm sang *"Cần xác nhận"* và khóa ký duyệt cho tới khi bác sĩ quyết định, sau đó niêm vết WORM SHA-256.

---

# PHẦN 3: BỘ CÂU HỎI "BẮT BẺ CHÍ MẠNG" (STRESS-TEST) & PHẢN BIỆN THỰC TẾ

---

### [KHÓ] Câu 14: *"Lúc ghi âm thực tế tên thuốc bệnh nhân đọc sai hoặc ASR nghe nhầm ('a móc', 'ô mê'). Phần mềm có tự sửa thành tên thuốc vào đơn không? Nhỡ AI đoán sai thì sao?"*
* **🎯 Phản biện tự tin:**  
  *"Thưa Ban Giám khảo, đây là nguyên tắc an toàn **không tự ý chuẩn hóa ngầm vào đơn chính thức (Zero Silent Normalization)** của MediTrace Sentinel:*
  1. **Không tự động điền đơn chính thức từ âm vị mơ hồ:** Chỉ một nhầm lẫn giữa hai hoạt chất gần âm (ví dụ Amoxicillin đơn chất và chế phẩm phối hợp Clavulanate) có thể dẫn đến tai biến dị ứng hoặc sai phác đồ. Do đó `contextual_trie_600.py` chỉ trả về **gợi ý** khi xuất hiện trong ngữ cảnh thuốc (`uống`, `viên`, `mg`, `đơn`) và luôn tách khỏi khẳng định sạch.
  2. **Cách ly sang hàng đợi *"Cần bác sĩ xác nhận"*:** Mọi ca nghi ngờ sai tên thuốc/họ thuốc hoặc thiếu liều (theo Chính sách D) đều mang cờ cảnh báo nổi bật để bác sĩ kiểm tra.
  3. **Đối soát bằng 1 cú bấm (*Click-to-Verify*):** Bác sĩ bấm thẳng vào thẻ cảnh báo để `useTurnAudioPlayer.ts` phát lại đúng đoạn âm thanh gốc tại lượt thoại đó, xác nhận hoặc sửa lại tên thuốc chuẩn.
  4. **Kiểm tra hậu kiểm & lưu vết WORM:** Chỉ sau khi bác sĩ xác nhận và không còn mục treo, đơn mới qua được cổng `sign-off.ts` để kiểm DDI/BHYT và ghi vào sổ WORM SHA-256 kèm tệp neo `.anchor.json`."*

---

### [KHÓ] Câu 15: *"Nếu micrô phòng khám thu nhiều tạp âm, bệnh nhân nói lí nhí, ASR nghe sai be bét thì phần mềm có tạo ra bệnh án rác không?"*
* **🎯 Phản biện tự tin:**  
  *"Đây chính là điểm khác biệt cốt lõi giữa Neuro-Symbolic có cổng khóa căn cứ và chatbot sinh văn bản tự do:*
  * Chatbot thông thường có xu hướng suy đoán phần bị mất để viết thành một bản tóm tắt trôi chảy nhưng sai lệch.
  * Với MediTrace, khi ASR vỡ chữ hoặc không có ngữ cảnh rõ, mô-đun phát hiện bất thường ASR/không dấu trong `src/canh_bao/` cùng Cổng K1–K2 tại `b4_kiem_can_cu.py` sẽ chặn mệnh đề thiếu căn cứ, đồng thời báo trạng thái cần bác sĩ xem lại thay vì tự bịa thông số lâm sàng vào thân bệnh án sạch."*

---

### [TRUNG BÌNH] Câu 16: *"Một ngày khám đông ca, nhỡ bác sĩ đang dở tay hoặc tắt máy đột ngột thì dữ liệu có bị mất không?"*
* **🎯 Phản biện tự tin:**  
  *"Backend BFF (`web/may-chu/csdl.ts`) lưu phiên khám liên tục trên cơ sở dữ liệu **SQLite WAL cục bộ** kèm hàng đợi nền `hang-doi.ts`. Phiên ghi âm, bản gỡ băng, danh sách mệnh đề, các mục đã xác nhận hoặc đang chờ duyệt đều được lưu theo trạng thái phiên; khi mở lại phần mềm, bác sĩ tiếp tục đúng phiên ở trạng thái `Chờ duyệt` mà không mất dữ liệu đang xử lý."*

---

### [KHÓ] Câu 17: *"Dự án đã kiểm thử tự động trên bao nhiêu ca bệnh, bộ test chạy thực tế thế nào?"*
* **🎯 Phản biện tự tin:**  
  *"Toàn hệ thống hiện được bảo vệ bởi bộ kiểm thử hồi quy hai tầng chạy sau các đợt tinh chỉnh cuối cùng:*
  1. **Kiểm thử tự động phần mềm:** **1.974 bài test Python passed, 25 skipped** (trong tổng số 1.999 tests thu thập qua `pytest`, các bài bỏ qua phụ thuộc phần cứng/sidecar GPU ngoài môi trường CI CPU) và **96/96 bài kiểm thử TypeScript/BFF passed** (`web/`).
  2. **Kiểm thử dữ liệu và an toàn lâm sàng:** **657 khuôn ca bệnh** (21 hệ cơ quan) chia độc lập 515/72/70, **5.000 hội thoại mô phỏng v2** (100% trích dẫn chuỗi con nguyên văn), **4 bộ thử thách phát triển** (300 ca: Chính sách D giảm `lot_nguy_hiem` từ 45,9% xuống **11,8%**, chặn **88,2%** lỗi nguy hiểm với chặn thừa **10,0%**), **240 ca giữ kín `thach_thuc_v2`** (nhạy **0,871**, đổi chủ thể **0,946**, bắt xoá dị ứng **97,2%**), và **10 ca bệnh hiếm ngoài khuôn** (`kiem_nghiem_ngoai_khuon.py`)."*

---

### [KHÓ] Câu 18: *"Làm sao chứng minh phương ngữ và từ điển thuốc của dự án không chỉ chạy tốt trên dữ liệu tự sinh? Đã đo trên dữ liệu công khai độc lập nào và có giới hạn gì chưa đạt?"*
* **🎯 Phản biện tự tin:**  
  *"Đội ngũ đã viết kịch bản [`tools/do_da_nguon_doc_lap.py`](file:///d:/Claude/meditrace-ma-nguon/tools/do_da_nguon_doc_lap.py) để chạy kiểm nghiệm trên **5 bộ dữ liệu tiếng Việt công khai bên ngoài** (kết quả lưu tại `docs/ket-qua/da-nguon-doc-lap.json`) và báo cáo thẳng cả điểm mạnh lẫn giới hạn:*
  1. **`ViDia2Std/test.csv`** (1.603 câu có nhãn chuẩn hóa phương ngữ người thật): Chặn giữ ngữ cảnh chuẩn, chuẩn hóa đúng hoàn toàn **28,0%** (1.192/4.264 cặp thay thế), đạt tổng độ phủ **37,1%**, giúp kéo tỷ lệ lỗi từ (WER) trên bộ phương ngữ giảm từ **30,1% xuống 21,9%**.
  2. **`ViHealthQA`** (2.013 mẫu hỏi đáp sức khỏe): Ghi nhận 14/42 câu hỏi/đáp xuất hiện hoạt chất nằm trong Dược thư **158 hoạt chất** hiện tại.
  3. **`ViMedAQA`** (500 mẫu hỏi đáp y khoa): Bắt khớp **87** lượt nhắc hoạt chất chuẩn trên mẫu văn bản thực tế.
  4. **`ViMQ`** (1.000 câu hỏi ý định y khoa): Khớp 10 lượt thuốc (9/334 thực thể `MED` có nhãn), cho thấy phần lớn câu hỏi của bệnh nhân đại chúng dùng triệu chứng/tên bệnh hơn là tên hoạt chất Tây y chuẩn.
  5. **`PhoNER_COVID19`** (1.000 câu tin tức dịch tễ — **điểm giới hạn minh bạch**): So với nhãn vàng `NAME` và `PATIENT_ID`, bộ `khu_dinh_danh.py` chỉ đạt **10/847 (1,2%)** vì bộ khử định danh được thiết kế theo cấu trúc hội thoại y tế (*"tên tôi là...", "bác sĩ...", mã hồ sơ phòng khám*) chứ chưa mang mô hình NER tin tức để bắt tên riêng tiếng Việt xuất hiện tự do không tiền tố (*"Bệnh nhân 45 tuổi ở Hải Dương..."*). Đây là giới hạn rõ ràng được đội ngũ đưa vào lộ trình bổ sung NER tiếng Việt cho văn bản tự do."*

---

### [TRUNG BÌNH] Câu 19: *"Ngoài phần bóc tách bệnh án SOAP, dự án có gì phục vụ vận hành thực tế tại bệnh viện Việt Nam (BHYT, trả kết quả, bệnh nhân)?"*
* **🎯 Phản biện tự tin:**  
  *"Ngoài lõi Neuro-Symbolic 5 tầng, dự án tích hợp **bộ tiện ích lâm sàng & vận hành bệnh viện** nằm gọn trong `src/cong_cu_lam_sang/` và `web/` giúp giải quyết đúng các điểm nghẽn hành chính của bác sĩ Việt Nam:*
  * **Tiền kiểm BHYT & TT 26/2025 (`tien_kiem_bhyt_va_khoi_phuc_bo_sot.py` + `BhytPrecheckModal.tsx`):** Rà **13 quy tắc cận lâm sàng (CLS)** dễ bị xuất toán BHYT và bắt buộc kiểm tra **cân nặng trẻ em** khi kê đơn nhi khoa theo quy định mới.
  * **Sao chép thông minh sang HIS (`HisSmartCopyPopover.tsx`):** Cho phép bác sĩ copy đúng từng khối (Lý do khám, Bệnh sử, Tiền sử/Dị ứng, Chẩn đoán, Điều trị) sang phần mềm HIS cũ của bệnh viện mà không cần chờ tích hợp API phức tạp ngay ngày đầu.
  * **Chuẩn liên thông & ngoại viện:** Hỗ trợ xuất **FHIR R4** (`xuat_fhir_r4.py`), nạp **LIS/HL7** (`nap_ket_qua_lis_hl7.py`), thang điểm nguy cơ (**9 thang điểm** tại `thang_diem_nguy_co.py`), đi buồng nội trú (`di_buong_noi_tru.py`), **Cổng bệnh nhân & QR tóm tắt đơn/dặn dò** (`ho_so_benh_nhan_qr.py`, `PatientPortalView.tsx`), và **Trung tâm điều hành bệnh viện** (`HospitalCommandCenterView.tsx`)."*

---

> **LỜI KẾT DÀNH CHO BẠN KHI ĐỨNG TRƯỚC BAN GIÁM KHẢO:**  
> Luôn giữ phong thái điềm tĩnh, trung thực khoa học và bám chắc thông điệp:  
> **"MediTrace Sentinel không trình diễn một chatbot viết văn y khoa trơn tru. Đây là kiến trúc Neuro-Symbolic đặt an toàn người bệnh lên trước: dùng AI đúng một chỗ để tách từng mệnh đề có căn cứ nguyên văn, kiểm soát rủi ro ảo giác bằng 7 cổng khóa K1–K7 và 5 chốt an toàn xác định, minh bạch cả kết quả đo được lẫn giới hạn còn lại để người thầy thuốc luôn giữ quyền quyết định cuối cùng."**
