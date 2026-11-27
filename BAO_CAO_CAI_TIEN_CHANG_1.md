# BÁO CÁO CẢI TIẾN CHẶNG 1 — CUỘC THI AI 2026 (`ai.tainangviet.vn`)

**Dự án:** MediTrace Sentinel — Phần mềm dựng bản nháp hồ sơ khám bệnh từ lời nói buổi khám tiếng Việt có truy vết căn cứ hai chiều  
**Kho mã nguồn (HTTPS):** https://github.com/quannguyen991/meditrace-sentinel  
**Sản phẩm chạy thử (HTTPS):** https://meditrace-sentinel.meditrace.workers.dev  
**Ngày cập nhật:** 26/11/2026  

> **Nguyên tắc liêm chính khoa học của báo cáo này:**  
> 1. MediTrace chỉ tạo **bản nháp để bác sĩ xem lại**, không chẩn đoán, không kê đơn, không tự hoàn tất hồ sơ thay bác sĩ.  
> 2. Mọi con số dưới đây đều do mã nguồn trong kho in ra và có tệp kết quả hoặc lệnh chạy đối chứng. Những gì là dữ liệu mô phỏng, lỗi cấy nhân tạo hoặc giới hạn chưa giải quyết được đều được ghi rõ ngay cạnh con số.

---

## TÓM TẮT ĐỐI CHIẾU NHANH VỚI 3 YÊU CẦU CẢI TIẾN CỦA BAN GIÁM KHẢO

| Yêu cầu của Ban Giám khảo | Nâng cấp đã triển khai trong mã nguồn | Minh chứng định lượng & Đường dẫn kiểm chứng |
| :--- | :--- | :--- |
| **1. Giảm bỏ sót thông tin lâm sàng quan trọng**<br>*(Định nghĩa rõ loại lỗi & mức nghiêm trọng; giữ thông tin chưa chắc ở mục cần bác sĩ xác nhận thay vì âm thầm loại bỏ; tuyệt đối không tự hoàn tất hồ sơ khi thiếu căn cứ)* | - Xây dựng **Lớp cảnh báo (`src/canh_bao/`)** gồm **13 nhóm lỗi lớn, 56 mã lỗi** có bộ phát hiện (kèm 7 nhóm công khai chưa phát hiện được), tách riêng 2 trục: **mức nghiêm trọng lâm sàng (`muc_do`)** và **độ bất định căn cứ (`bat_dinh`)**.<br>- Định tuyến bảo toàn: thông tin chưa chắc (dị ứng, thuốc, chủ thể mơ hồ, câu điều kiện, giá trị bị đính chính) luôn chuyển vào mục **`CẦN XÁC NHẬN`** kèm lý do, **không xoá ngầm** (`src/duong_ong/b5_viet_ban_nhap.py`, `src/duong_ong/b5_xep_cho_cong_rui_ro.py`).<br>- **Chốt chặn cứng 2 tầng trước khi hoàn tất hồ sơ** (`kiemTraDieuKienKyDuyet` tại `web/src/lib/compileEffectiveNote.ts` + `khoWorm.ghiSignOff` tại `web/may-chu/worm.ts`): chặn ký duyệt khi `0` mệnh đề, khi còn bất kỳ mục `Cần xác nhận` nào chưa được bác sĩ `Xác nhận / Sửa / Bỏ`, hoặc khi thiếu căn cứ lượt thoại. | - **Tỷ lệ bỏ sót (30 ca phát triển độc lập, 304 mệnh đề):** giảm từ **43,1%** (Qwen3-4B chưa train) xuống **11,5%** (Qwen3-4B + adapter QLoRA, khoảng tin cậy 95%: `8,4%–15,6%`, `0` ca JSON lỗi) — `docs/ket-qua/bo-sot-qwen3-4b.md`.<br>- **Độ nhạy bắt lỗi theo nhóm (đăng ký trước):** 16 loại lỗi cơ bản đạt **0,871** trên 400 ca điều chỉnh và giữ nguyên **0,871** trên 240 ca giữ kín (`thach_thuc_v2`); 14 loại lỗi khó tăng từ `0,682` lên **0,889** (vòng 6) — `docs/ket-qua/cay-loi.md`.<br>- **Luồng bác sĩ kiểm tra/sửa bản nháp:** `DuyetBenCanh.tsx`, `VerificationView.tsx`, `compileEffectiveNote.ts`, nhật ký bất biến WORM SHA-256 (`worm.ts`). |
| **2. Kiểm soát lỗi giữa các bước AI**<br>*(Kiểm tra chủ thể, nguồn phát ngôn, trạng thái đính chính ở từng bước; đường dẫn về âm thanh/văn bản gốc; demo hai bệnh nhân hoặc bác sĩ–người nhà trao đổi)* | - **Bước 0 (Âm thanh & Vai nói):** tách vai `doctor / patient / caregiver / nurse / other` (`src/audio/schemas.py`); chặn cứng tạo bản nháp (`HTTP 409 asr_review_pending` + kiểm tra giao diện) nếu còn lượt chưa gán vai; tô sáng vùng mờ ASR (`asrHighlight.ts`).<br>- **Bước 2–3 (Chủ thể & Đính chính):** gom thực thể người nói ≠ chủ thể (`src/duong_ong/b2_gom_nguoi_thuc_the.py`), máy trạng thái đính chính (`src/duong_ong/b3_cap_nhat_trang_thai.py`, `src/duong_ong/b2_bu_chu_ngu_tinh_luoc.py`), luật `dinh_chinh_nguoc` (`src/canh_bao/toan_ca.py`).<br>- **Bước 4 (Khóa căn cứ & Truy vết 2 chiều):** 6 phép kiểm căn cứ (`src/duong_ong/b4_kiem_can_cu.py`), mỏ neo `[T1]..[Tn]`, dây nối SVG hai cột (`VerificationView.tsx`) và phát lại đúng đoạn âm thanh gốc `±0,5s` (`useTurnAudioPlayer.ts`). | - Giảm thông tin cũ đã bị đính chính còn sót lại trên bộ "tự sửa" từ **11,48%** xuống **0,80%**; F₁ bộ "đổi người" tăng từ `66,1%` lên **70,8%** (SER giảm `45,4% → 36,9%`).<br>- **3 ca demo đa người nói dựng sẵn** (bấm **"Xem thử với ca mẫu"**, không cần GPU, `src/bo_du_lieu/ca_mau_bgk.py`):<br>  1. *Bác sĩ – Mẹ – Bệnh nhi 6 tuổi* (`demo_bs_nguoi_nha_nhi`)<br>  2. *Hai người bệnh cùng phòng trao đổi* (`demo_hai_benh_nhan`)<br>  3. *Bác sĩ – Cụ ông 74 tuổi – Con gái* (`demo_lao_khoa_con_gai`)<br>- Kiểm thử tự động: `tests/test_demo_bac_si_nguoi_nha.py`, `tests/test_dich_vu.py`. |
| **3. Kiểm tra tính độc lập của bộ dữ liệu**<br>*(Chia dữ liệu theo khuôn/kịch bản và nguồn, thử hội thoại mới, phân tích lỗi; công khai cách tạo và kiểm soát mẫu tổng hợp)* | - Mở rộng kho khuôn từ 200 khuôn (v1) lên **657 khuôn ca bệnh trên 21 hệ cơ quan** (`src/bo_du_lieu/kho_khuon.py`, `src/bo_du_lieu/khuon_mo_rong.py`), ngữ cảnh hóa câu hỏi bác sĩ (`src/bo_du_lieu/bien_the_cau.py`).<br>- Chia tập độc lập tuyệt đối theo khuôn bệnh và theo đợt (`src/bo_du_lieu/chia_tap_theo_khuon.py`): **0 khuôn giao nhau** giữa Train / Dev / Test, bảo toàn mã băm vàng 200 khuôn gốc.<br>- Kiểm định tự động 6 quy tắc chất lượng câu (`tools/kiem_chat_luong_cau.py`) và 100% trích dẫn chuỗi con (`tools/kiem_tra_trich_dan_v2.py`). | - **Giảm lặp câu trên 5.000 ca v2:** lặp mọi câu giảm từ `76,92%` xuống **47,37%** (câu $\ge 8$ từ: **42,19%**), câu duy nhất tăng **+127%** (`20.190 → 45.835`), MTLD `93,0 → 145,4`, Distinct-2 `0,0188 → 0,0468`.<br>- **Độc lập Train–Test (`515` khuôn Train / `72` Dev / `70` Test):** giao tên khuôn `= 0`; Jaccard từ khóa triệu chứng trung bình **0,0587** (`p95 = 0,1172`), bigram Jaccard **0,0891**, trigram Jaccard **0,0287**; danh sách đầy đủ tại `data/manifest_v2_mo_rong_5000.json`.<br>- **Thử ngoài khuôn & ngoài nguồn:** 30 ca phát triển ngoài khuôn (`11,5%` bỏ sót), 240 ca giữ kín `thach_thuc_v2` (độ nhạy `0,871`), 10 kịch bản bệnh hiếm ngoài kho 657 khuôn (`src/do_luong/kiem_nghiem_ngoai_khuon.py`: `52/52` đúng chủ thể & trích dẫn, `10/10` bắt đính chính), và 200 câu thực tế ngoài nguồn **ViMQ** (phủ thực thể **88,2%**, kèm phân tích lỗi). |

---

## YÊU CẦU 1: GIẢM BỎ SÓT THÔNG TIN LÂM SÀNG QUAN TRỌNG & CHỐT CHẶN HOÀN TẤT HỒ SƠ

### 1.1. Định nghĩa rõ từng loại lỗi và mức nghiêm trọng (Tách 2 trục độc lập)

Trong [`src/canh_bao/loai.py`](src/canh_bao/loai.py) và [`src/duong_ong/b5_xep_cho_cong_rui_ro.py`](src/duong_ong/b5_xep_cho_cong_rui_ro.py), hệ thống không gộp chung mọi cảnh báo thành một điểm mờ mà tách thành **hai trục độc lập** và **ba mức kết luận**:

1. **Trục 1 — Mức nghiêm trọng lâm sàng nếu sai (`muc_do`: `cao` / `trung` / `thap`):** phụ thuộc vào **loại thông tin lâm sàng** (`MUC_NGHIEM_TRONG` trong `src/duong_ong/b5_xep_cho_cong_rui_ro.py`):
   - `di_ung` (`1,0`) và `thuoc_nti` — thuốc khoảng điều trị hẹp như warfarin, acenocoumarol, digoxin, phenytoin, carbamazepine, valproat, colchicine, lithium (`1,0`): sai sót có nguy cơ sốc phản vệ hoặc ngộ độc cấp → tự động nâng mức nghiêm trọng lên `cao`.
   - `thuoc` thông thường (`0,9`), `chan_doan` (`0,8`), `thoi_gian` (`0,6`), `khac` (`0,3`).
   - Nhóm mã `LUON_CAO` (`NEGATION_FLIP`, `UNKNOWN_AS_NEGATIVE`, `FABRICATED_MEDICATION`, `FABRICATED_ALLERGY`, `DOSE_MISMATCH`, `DECIMAL_MISMATCH`, `UNIT_MISMATCH`, `DISCONTINUED_AS_CURRENT`, `PLANNED_TEST_AS_RESULT`, `LATERALITY_CHANGED`, `INTERNAL_CONTRADICTION`) luôn giữ mức `cao` dù rơi vào mục nào.
2. **Trục 2 — Độ bất định của bằng chứng (`bat_dinh`: `thap` / `trung` / `cao`):** `thap` khi có bằng chứng đối nghịch trực tiếp trên chữ/số của lượt dẫn; `cao` khi chỉ là dấu hiệu gián tiếp.
3. **Ba loại kết luận (`ket_luan`):** `loi_phat_hien` (có bằng chứng trái ngược rõ), `nghi_rui_ro` (thiếu bằng chứng khẳng định đầy đủ), `can_xem` (ghi chú chất lượng hoặc tri thức thuốc chưa qua hội đồng duyệt).

#### Bảng phân nhóm 13 nhóm lỗi lâm sàng (`src/canh_bao/loai.py`, 56 mã có bộ phát hiện)

| Mã nhóm | Tên nhóm tiếng Việt | Số mã | Các mã tiêu biểu | Mức gốc chính | Vai trò định tuyến |
| :--- | :--- | :---: | :--- | :---: | :--- |
| `SUBJECT_ATTRIBUTION` | Gán sai người | 5 | `WRONG_SUBJECT`, `FAMILY_PATIENT_MIXUP`, `SPEAKER_SUBJECT_MISMATCH`, `SUBJECT_AMBIGUOUS` | `cao` / `trung` | Đưa sang `CẦN XÁC NHẬN`, ngăn ghi bệnh/dị ứng người nhà cho bệnh nhân |
| `NEGATION_ASSERTION` | Sai khẳng định / phủ định / mức chắc chắn | 7 | `NEGATION_FLIP`, `UNKNOWN_AS_NEGATIVE`, `NOT_YET_AS_NEGATIVE`, `CERTAINTY_INCREASED` | `cao` | Chặn biến *"chưa rõ / không nhớ"* thành *"không có"* |
| `ENTITY_VALUE` | Sai tên thuốc, số liệu, vị trí, mức độ | 14 | `DOSE_MISMATCH`, `UNIT_MISMATCH`, `DECIMAL_MISMATCH`, `LATERALITY_CHANGED`, `SEVERITY_CHANGED` | `cao` / `trung` | Bắt lệch liều, lệch dấu thập phân 10×, đổi trái/phải, đổi nhẹ/nặng |
| `TEMPORAL` | Sai thời gian / trạng thái dùng thuốc | 3 | `DISCONTINUED_AS_CURRENT`, `PAST_CURRENT_CONFUSION`, `TEMPORAL_MISMATCH` | `cao` / `trung` | Chặn ghi thuốc đã ngừng thành đang dùng; phân biệt tiền sử vs hiện tại |
| `PLAN_FACT_CONDITIONAL` | Nhầm kế hoạch, điều kiện với sự việc | 7 | `CONDITION_AS_FACT`, `PLAN_AS_FACT`, `PLANNED_TEST_AS_RESULT`, `QUESTION_AS_FACT` | `cao` | Chặn biến lời dặn *"nếu mai còn sốt…"* hoặc câu hỏi bác sĩ thành sự thật |
| `STATE_UPDATE` | Sai cập nhật / đính chính / mâu thuẫn | 6 | `CORRECTION_NOT_APPLIED`, `CONTRADICTION_UNRESOLVED`, `INTERNAL_CONTRADICTION` | `cao` | Bắt giữ số cũ đã đính chính hoặc hai nguồn nói trái nhau |
| `UNSUPPORTED` | Thông tin không có căn cứ | 6 | `FABRICATED_MEDICATION`, `FABRICATED_ALLERGY`, `FABRICATED_QUOTE`, `AMBIGUOUS_LAY_TERM` | `cao` / `trung` | Chặn câu trích/thuốc/dị ứng bịa hoặc từ dân gian đa nghĩa |
| `EVIDENCE_PROVENANCE` | Căn cứ hoặc nguồn chưa đủ | 3 | `WRONG_EVIDENCE`, `EVIDENCE_MISSING`, `EVIDENCE_CONTEXT_MISSING` | `trung` / `thap` | Đánh dấu mệnh đề dẫn sai lượt hoặc thiếu câu hỏi ngữ cảnh |
| `OMISSION` | Có thể bỏ sót (cảnh báo mức toàn ca) | 10 | `OMITTED_ALLERGY`, `OMITTED_MEDICATION`, `OMITTED_NEGATION`, `OMITTED_NUMERIC_VALUE`, `OMITTED_ANSWER` | `cao` / `trung` | Tô sáng ngay trên cột lời thoại những lượt nghi chưa được trích |
| `ASR_UPSTREAM` | Bản chép âm chưa chắc (trước khâu AI rút tin) | 5 | `ASR_LOW_CONFIDENCE`, `POSSIBLE_MEDICATION_TRANSCRIPTION_ERROR`, `SPEAKER_DIARIZATION_UNCERTAIN` | `cao` / `trung` | Tách riêng lỗi ASR/tách giọng khỏi lỗi mô hình trích xuất; gắn nút nghe lại |
| `CLINICAL_KNOWLEDGE` | Kiến thức lâm sàng (liều, tương tác, dị ứng) | 3 | `DOSE_OVER_MAX`, `DRUG_INTERACTION`, `CONTRAINDICATION` | `cao` (`thu_nghiem`) | Đối chiếu `data/tri_thuc_thuoc.json` (gắn nhãn thử nghiệm, chỉ nhắc bác sĩ) |
| `RELATION_CAUSALITY` | Sai liên hệ, nguyên nhân | 2 | `UNSUPPORTED_CAUSALITY`, `UNSUPPORTED_FACT_COMBINATION` | `trung` (`thu_nghiem`) | Cảnh báo tự suy diễn quan hệ nhân quả *"do…"* không có trong lời nói |
| `QUALITY` | Chất lượng bản ghi | 4 | `DUPLICATE_INFORMATION`, `SEMANTIC_DUPLICATE`, `IMPORTANT_MODIFIER_DROPPED` | `thap` | Nhắc trùng lặp hoặc rơi trạng từ bổ nghĩa, không tự đổi trạng thái |

> **Công khai giới hạn (`CHUA_PHAT_HIEN` trong `src/canh_bao/loai.py`):** 7 nhóm lỗi ngữ nghĩa sâu (đồng tham chiếu đại từ qua nhiều lượt ngoài phạm vi khóa câu, suy luận ngụ ý, mở rộng nhóm kháng sinh khi chưa duyệt bảng tri thức…) được liệt kê thẳng trong mã nguồn là *chưa phát hiện đáng tin cậy bằng luật*, không giả vờ đã giải quyết hết.

---

### 1.2. Ưu tiên giữ thông tin chưa chắc ở mục "Cần xác nhận" & Tuyệt đối không hoàn tất hồ sơ khi thiếu căn cứ

1. **Không âm thầm loại bỏ thông tin nghi ngờ (`src/duong_ong/b5_viet_ban_nhap.py`, `src/duong_ong/b5_xep_cho_cong_rui_ro.py`, `src/duong_ong/chay_duong_ong.py`):**
   - Trong `sinh_benh_an._muc_cho`, mọi phát biểu thiếu bằng chứng lượt thoại, mang trạng thái `bị thay thế` / `mâu thuẫn`, mang tình huống `giả định`, hoặc bị khóa căn cứ K1–K6 (`ly_do_chan`) và cổng rủi ro (`cong_rui_ro.dua_sang_xac_nhan`) đánh dấu đều **không bị xoá khỏi đầu ra**, mà được chuyển nguyên vẹn xuống mục **`CẦN XÁC NHẬN`** kèm lý do cụ thể bằng tiếng Việt đời thường (ví dụ: *"đoạn dẫn nói về chính người kể"*, *"tên hoặc chi tiết thuốc không thấy ở đoạn dẫn"*, *"câu giả định, chưa xảy ra"*).
   - Hệ thống khuếch đại rủi ro theo cơ địa nhạy cảm (`phan_tich_co_dia_benh_nhan`: thai kỳ quý 1, trẻ $\le 6$ tháng, người cao tuổi $\ge 65$/$\ge 80$, suy thận eGFR $< 60$/$< 30$/$< 15$, suy gan, đa thuốc $\ge 5$ thuốc) để tự động đẩy các mệnh đề thuốc/dị ứng có cảnh báo nhỏ sang mục **`CẦN XÁC NHẬN`**.
2. **Chốt chặn cứng hai tầng: Tuyệt đối không hoàn tất / ký duyệt hồ sơ khi thiếu căn cứ:**
   - **Tầng Giao diện (`kiemTraDieuKienKyDuyet` trong [`web/src/lib/compileEffectiveNote.ts`](web/src/lib/compileEffectiveNote.ts), [`NoteEditorView.tsx`](web/src/components/NoteEditorView.tsx), [`App.tsx`](web/src/App.tsx)):**
     - Nếu hồ sơ chưa có mệnh đề trích xuất từ hội thoại (`propositions.length === 0`) → nút chuyển sang trạng thái cảnh báo **`Chưa đủ căn cứ`**, chặn hoàn tất hồ sơ.
     - Nếu còn bất kỳ mệnh đề nào trong mục **`Cần xác nhận`** chưa được bác sĩ quyết định rõ (`Xác nhận` / `Sửa` có nội dung / `Bỏ`) → nút hiện **`Cần xác nhận (N)`**; nếu bác sĩ bấm ký, hệ thống từ chối ký duyệt, tự mở ngăn duyệt bên phải và cuộn thẳng tới đúng mệnh đề chưa xác nhận đầu tiên.
     - Nếu còn mệnh đề thiếu lượt thoại căn cứ (`evidenceTurns.length === 0`) chưa được bác sĩ sửa/bỏ, hoặc tất cả mệnh đề đều bị bỏ (`0` mệnh đề còn hiệu lực) → chặn hoàn tất hồ sơ.
   - **Tầng Máy chủ & Chuỗi băm WORM ([`web/may-chu/worm.ts`](web/may-chu/worm.ts), [`web/may-chu/routes/sign-off.ts`](web/may-chu/routes/sign-off.ts)):**
     - Kiểm định bất biến ở API `POST /api/sessions/:id/sign-off`: từ chối với mã `HTTP 400` nếu `tongMenhDe < 1`, `soBo >= tongMenhDe`, `tyLeCoNguon <= 0`, hoặc `soChuaXacNhan > 0`.

---

### 1.3. Minh chứng định lượng: Bảng lỗi theo nhóm, Tỷ lệ bỏ sót & Ví dụ bác sĩ sửa bản nháp

#### A. Bảng tỷ lệ bỏ sót mệnh đề lâm sàng (`docs/ket-qua/bo-sot-qwen3-4b.md`)
Đo bằng `tools/do_bo_sot_tren_tap.py` trên **30 ca đầu của tập phát triển** (gồm các khuôn bệnh không xuất hiện trong tập huấn luyện, tổng cộng **304 mệnh đề đáp án**, ngưỡng khớp từ $\ge 0,6$):

| Mô hình trích xuất (Tầng 1) | Số mệnh đề đáp án | Số mệnh đề bỏ sót | Tỷ lệ bỏ sót | Khoảng tin cậy Wilson 95% | Số ca lỗi cú pháp JSON |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Qwen3-4B chưa huấn luyện (Zero-shot)** | 304 | 131 | **43,1%** | 37,6% – 48,7% | 0 / 30 |
| **Qwen3-4B + QLoRA Adapter (`best_checkpoint`)** | 304 | 35 | **11,5%** | **8,4% – 15,6%** | 0 / 30 |

*Ghi nhận trung thực về sự đánh đổi và giới hạn:*
- Khi bật thêm khóa kiểm căn cứ (`C_khoa`) trên các bộ thử thách, tỷ lệ lỗi nghiêm trọng ở thân bệnh án giảm nhưng tỷ lệ thông tin không vào được thân bệnh án tăng (ví dụ từ `4,5%` lên `7,7%` ở bộ *đổi người*). Điểm cải tiến cốt lõi là các mệnh đề bị khóa chặn **không bị xoá mất** mà nằm ở mục **`CẦN XÁC NHẬN`** để bác sĩ duyệt lại trong vài giây.
- Với các mệnh đề mà ngay từ Tầng 1 mô hình Qwen3-4B không trích ra, bộ cảnh báo bỏ sót toàn ca dựa trên luật từ khóa (`doan_chua_ghi`) hiện mới chạm đúng lượt của **25/200 mệnh đề bị sót (độ phủ 12,5%, precision 2,8%)** trên 4 bộ thử thách (`docs/ket-qua/canh-bao-moc-0.md`), do 86% mệnh đề bị sót nằm chung lượt với một mệnh đề khác đã được trích. Mô hình trích xuất bản v3 (huấn luyện trên bộ v2 657 khuôn) và nhánh DPO trên cặp lỗi khó (`src/huan_luyen/huan_luyen_dpo.py`) đã được triển khai để tiếp tục kéo giảm tỷ lệ này.

#### B. Bảng độ nhạy lớp cảnh báo theo nhóm lỗi (`docs/ket-qua/cay-loi.md` — tiêu chí đăng ký trước tại `docs/dang-ky-truoc-bo-luat.md`)
*Lưu ý: Phép đo dưới đây cấy nhân tạo đúng 1 lỗi đã biết vào bản đáp án chuẩn để đo khả năng phát hiện của bộ luật, không phải tần suất lỗi trên bệnh nhân thật.*

1. **16 loại lỗi cơ bản** (đo trên **400 ca tập điều chỉnh** từ `viet_train_v2`, và kiểm chứng một lần duy nhất trên **240 ca tập giữ kín `thach_thuc_v2`** sau khi khóa luật):

| Nhóm / Loại lỗi cấy | Tập điều chỉnh ($n=400$ ca) Trước → Sau | Tập giữ kín ($n=240$ ca, chạy 1 lần) [Wilson 95%] |
| :--- | :---: | :---: |
| `doi_chu_the` (Gán sai người) | 0,945 → **0,945** | **0,946** [0,910–0,968] |
| `dao_phu_dinh` (Đảo có ↔ không) | 0,052 → **0,695** | **0,617** [0,554–0,676] |
| `nang_chac_chan` (Nghi ngờ → chắc chắn) | 0,881 → **0,881** | **0,896** [0,824–0,941] |
| `gia_dinh_thanh_that` (Điều kiện/kế hoạch → sự việc) | 0,355 → **0,445** | **0,417** [0,356–0,480] |
| `ban_cu_con_hieu_luc` (Giữ thông tin cũ) | 0,482 → **0,482** | **0,311** [0,195–0,457] *(cảnh báo rơi sang nhóm trùng/thời gian)* |
| `doi_lieu` / `doi_so` / `doi_thuoc` / `doi_thoi_gian` | 0,789 / **0,900** / 0,996 / 0,916 | **1,000** / **0,908** / **1,000** / **0,953** |
| `bia_menh_de` / `bia_trich_dan` / `doi_bang_chung` | **1,000** / **1,000** / **1,000** | **1,000** / **1,000** / **1,000** |
| `xoa_di_ung` / `xoa_thuoc` / `xoa_phu_dinh` / `xoa_so_lieu` | **0,983** / 0,962 / 1,000 / 0,948 | **0,972** / **0,972** / **0,989** / **0,954** |
| **Trung bình 16 loại lỗi cơ bản** | **0,801 → 0,871** | **0,871** *(không suy giảm khi sang tập giữ kín)* |
| **Số cảnh báo trên bản sạch (trung bình/ca)** | **8,98 → 7,11** | **8,00** *(chủ yếu cảnh báo bỏ sót nhẹ lưu hậu trường)* |

2. **14 loại lỗi khó** (`tools/cay_loi_kho.py` — câu trích dẫn giữ nguyên, chỉ đổi tinh vi 1 chi tiết; đo trên 400 ca tập điều chỉnh, số vòng 6 chưa chạy lại tập giữ kín nên là cận lạc quan):
   - Trước vòng 6: trung bình **0,682** (phát hiện 4 điểm mù: `qua_khu_hien_tai` `0,012`, `dinh_chinh_nguoc` `0,000`, `doi_ben` `0,250`, `doi_muc_do` `0,500`).
   - Sau vòng 6 (bổ sung 4 luật mới, báo nhầm bản sạch chỉ tăng `+0,002`/ca): `doi_ben` → **0,950**, `doi_muc_do` → **0,970**, `qua_khu_hien_tai` → **0,730**, `dinh_chinh_nguoc` → **1,000**; trung bình 14 loại lỗi khó đạt **0,889**.

3. **Đối chiếu trên lỗi thật của mô hình ở 4 bộ thử thách (`docs/ket-qua/canh-bao-moc-0.md`, 2.789 phát biểu):**
   - Tỷ lệ lỗi nguy hiểm (dị ứng, thuốc, chẩn đoán) lọt vào thân: giảm từ **45,2%** (chính sách C: 98/217) xuống **42,9%** (chính sách D sau vòng 6: 93/217); tỷ lệ chặn thừa trên mệnh đề đúng giảm từ `8,0%` xuống **6,1%**.

#### C. Ví dụ thực tế bác sĩ kiểm tra, sửa bản nháp và ký duyệt trên giao diện
Khi mở **Ca mẫu 3 (`demo_lao_khoa_con_gai`)** trên giao diện soạn bệnh án:
1. **Phát hiện & Cách ly:** Con gái nói *"hôm qua bố hơi đau họng nên tự ra hiệu thuốc mua vỉ a móc uống"* (lượt 5). Giả sử mô hình trích `amoxicillin` — khóa căn cứ K6 phát hiện chữ `"amoxicillin"` không có mặt nguyên văn trong lượt 5 nên **không cho vào mục `THUỐC ĐANG DÙNG`**, mà đẩy xuống **`CẦN XÁC NHẬN`** kèm lý do *"tên hoặc chi tiết thuốc không thấy ở đoạn dẫn"*. Đồng thời thanh công cụ hiện nút vàng **`Cần xác nhận (2)`** và khóa cứng chưa cho ký duyệt.
2. **Đối chiếu căn cứ 1 chạm:** Bác sĩ bấm vào dòng cảnh báo hoặc mở ngăn **Duyệt từng mệnh đề** (`DuyetBenCanh.tsx`) / màn **Bằng chứng hội thoại** (`VerificationView.tsx`) → dây nối đỏ trỏ thẳng về **lượt 5** (kèm nút **Nghe lại** đoạn âm thanh `25,1s – 35,0s`).
3. **Sửa hoặc Bỏ có lưu vết:** Bác sĩ kiểm tra vỉ thuốc bệnh nhân mang theo, bấm **`Sửa`** thành *"Bệnh nhân tự mua uống 2 viên Amoxicillin 500mg từ hôm qua (đã đối chiếu vỉ thuốc)"*, và bấm **`Bỏ`** trên mệnh đề cũ *"quên uống thuốc huyết áp cả tuần nay"* (do bệnh nhân đã đính chính ở lượt 3).
4. **Biên dịch văn bản hiệu lực & Ký duyệt WORM:** Hàm `compileEffectiveNote` lập tức cập nhật văn bản xuất (Sao chép, `.txt`, `.md`, In PDF A4, SBAR, Chép HIS) theo đúng nội dung bác sĩ vừa sửa/bỏ, ẩn tiêu đề `CẦN XÁC NHẬN` khi đã xử lý hết, và mở khóa nút **`Ký duyệt`**. Khi bác sĩ bấm ký, hệ thống băm chuẩn FIPS `SHA-256` trên cả nội dung bệnh án lẫn bảng quyết định duyệt, nối vào chuỗi SQLite WORM + tệp neo `.anchor.json` (`Đã ký #seq`). Nếu sau đó ai sửa dù 1 ký tự, nút lập tức đổi sang **`Đã sửa · Ký lại`**.

---

## YÊU CẦU 2: KIỂM SOÁT LỖI GIỮA CÁC BƯỚC AI & TRUY VẾT ÂM THANH / VĂN BẢN GỐC

### 2.1. Chốt kiểm soát chủ thể, nguồn phát ngôn và đính chính qua từng bước đường ống

| Bước đường ống | Nguy cơ lan truyền lỗi (Cascading Error) | Cơ chế kiểm soát đã triển khai trong mã nguồn | Trạng thái lưu vết & Đường dẫn gốc |
| :--- | :--- | :--- | :--- |
| **Bước 0: Chép lời & Tách giọng** (`src/audio/`, `asr.ts`, `App.tsx`) | ASR nghe nhầm tên thuốc/số/từ phủ định; tách giọng gán nhầm người nhà thành bệnh nhân | - Mặc định gán `speaker_role = "unknown"` và `asr_review_required = True` sau tách giọng; hỗ trợ đủ vai `doctor`, `patient`, `caregiver`, `nurse`, `other` (`src/audio/schemas.py`).<br>- **Chặn cứng hai đầu:** Giao diện (`App.tsx:225`) và Backend (`dich_vu.py:660`, mã `409 asr_review_pending`) từ chối dựng bản nháp nếu còn bất kỳ lượt nào chưa gán vai.<br>- Phân tích bất đồng ASR & gắn cờ `ASR_LOW_CONFIDENCE`, `POSSIBLE_MEDICATION_TRANSCRIPTION_ERROR`. | Lưu mốc `start_time`, `end_time` (giây) và `audio_spans` (`start_ms..end_ms`) cho từng lượt thoại; lưu ghi âm vào IndexedDB theo từng tài khoản bác sĩ (`realAudioService.ts`). |
| **Bước 1: Trích mệnh đề nguyên tử** (`src/huan_luyen/chon_mo_hinh_bakeoff.py`, `src/duong_ong/b1_cau_truc_menh_de.py`) | Mô hình viết văn xuôi tự gộp câu của hai người hoặc bịa chi tiết không có trong hội thoại | - Cấm sinh văn xuôi; ép lược đồ JSON cho từng `PhatBieu` gồm `nguoi_noi`, `chu_the`, `do_chac_chan`, `phu_dinh`, `tinh_huong`, `hanh_vi`, `luot_thoai`, `trich_dan`.<br>- Chuẩn hóa vai nhân viên y tế (`la_vai_nhan_vien`) ngay từ lúc đọc JSON để lời bác sĩ không biến thành tiền sử gia đình. | Mỗi mệnh đề bắt buộc mang danh sách chỉ số lượt `bang_chung` và chuỗi `trich_dan`. |
| **Bước 2: Liên kết thực thể & Chủ thể** (`src/duong_ong/b2_gom_nguoi_thuc_the.py`) | Tiếng Việt lược chủ ngữ (*"Đêm qua nôn hai lần"*) hoặc đại từ họ hàng đa nghĩa (*"cháu"*, *"con"*, *"ông nhà"*) | - Tách biệt rạch ròi `nguoi_noi` (ai phát ngôn) và `chu_the_id` (`0` = người bệnh chính, `1..n` = người nhà / bệnh nhân khác cùng phòng).<br>- Khi chủ thể không phải người bệnh (`chu_the_id != 0`), mệnh đề chỉ được phép vào `TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI` hoặc `CẦN XÁC NHẬN`, **tuyệt đối không vào `DỊ ỨNG`, `BỆNH SỬ` hay `ĐƠN THUỐC` của người bệnh** (kể cả trong gói xuất HL7 FHIR R4 `fhir_exporter.py` và tiền kiểm BHYT `kiem_duyet_bhyt_va_bo_sot.py`). | Thẻ mệnh đề trên giao diện gắn nhãn xanh `nói về: <chủ thể>` và truyền `chu_the_id` xuyên suốt sang BFF TypeScript (`asr.ts`). |
| **Bước 3: Máy trạng thái Đính chính & Mâu thuẫn** (`src/duong_ong/b3_cap_nhat_trang_thai.py`, `src/duong_ong/b2_bu_chu_ngu_tinh_luoc.py`) | Người bệnh nói nhầm rồi sửa lại (*"4 ngày… à không, chiều hôm qua"*), hoặc người nhà và người bệnh nói ngược nhau | - Phát hiện quan hệ `đính chính` → chuyển phát biểu cũ sang `trang_thai = "bị thay thế"` (**không xoá khỏi CSDL**, chuyển xuống `CẦN XÁC NHẬN` để giữ vết kiểm toán), giữ phát biểu mới ở `còn hiệu lực`.<br>- Phát hiện quan hệ `diễn biến` (hai thời điểm đều đúng → giữ cả hai) và `mâu thuẫn` (hai người nói trái nhau → đánh dấu mâu thuẫn để bác sĩ hỏi lại).<br>- Luật `toan_ca.dinh_chinh_nguoc` bắt trường hợp mô hình giữ nhầm số cũ trước chữ *"à nhầm / không phải"*. | Giảm tỷ lệ sót thông tin cũ trên bộ thử thách *tự sửa* từ **11,48%** xuống **0,80%**; lưu đầy đủ `lich_su` chuyển trạng thái. |
| **Bước 4–5: Khóa căn cứ K1–K6 & Truy vết hai chiều** (`src/duong_ong/b4_kiem_can_cu.py`, `VerificationView.tsx`, `DuyetBenCanh.tsx`) | Mô hình trích câu không có thật, gán lời *"bản thân tôi bị dị ứng"* của người nhà cho `chu_the_id = 0`, hoặc lệch liều thuốc | - Đối chiếu trực tiếp từng mệnh đề với lượt dẫn: khớp chuỗi con nguyên văn (K1), khớp từ nội dung (K2), chặn đại từ tự xưng của người kể `chu_the_nguoi_ke` (K3), chặn nâng mức chắc chắn/điều kiện (K4), khớp mốc thời gian (K5), khớp tên/liều thuốc (K6).<br>- Giao diện hiển thị mỏ neo `[T1]..[Tn]` bấm được ở mọi dòng bản nháp, vẽ dây nối Bezier từ lượt thoại sang mệnh đề, và nút **Nghe lại** phát đúng đoạn ghi âm gốc (`±0,5s` đệm hai đầu). | `0 / 30.136` dòng đáp án chuẩn bị chặn oan; trên đầu ra mô hình thật ở 4 bộ thử thách, tỷ lệ chặn thừa là `8,0%` (C) / `6,1%` (D). |

---

### 2.2. Minh chứng Demo: Ba tình huống đa người nói chạy ngay không cần GPU

Người chấm có thể bấm nút **"Xem thử với ca mẫu"** ngay tại **Trang chủ** hoặc tab **Lời thoại** (hoặc gọi `GET /api/sample-cases?bo=demo_bgk`). Mỗi lần bấm hệ thống xoay vòng qua **3 ca mẫu đa người nói** trong [`src/bo_du_lieu/ca_mau_bgk.py`](src/bo_du_lieu/ca_mau_bgk.py), chạy thật qua đường ống luật `nhanh.chay_trung_gian(..., nhanh="C_khoa_hoi")`:

1. **Ca mẫu 1 (`demo_bs_nguoi_nha_nhi`) — Bác sĩ, Mẹ (Người nhà) và Bệnh nhi 6 tuổi:**
   - Mẹ kể hộ *"cháu sốt cao với ho đờm từ 4 ngày nay"* `[T2]`; bé đính chính *"không phải 4 ngày đâu ạ, con mới bị sốt nóng từ chiều hôm qua thôi"* `[T3]` → bản nháp chỉ giữ **sốt nóng từ chiều hôm qua** ở `BỆNH SỬ HIỆN TẠI`, còn *"sốt cao 4 ngày nay"* mang trạng thái `bị thay thế` nằm ở **`CẦN XÁC NHẬN`**.
   - Mẹ nói *"bản thân tôi thì bị dị ứng penicillin… còn cháu chưa thấy bị dị ứng thuốc gì"* `[T5]` → dị ứng Penicillin được ghi riêng cho **mẹ** ở `TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI`, mục `DỊ ỨNG` của bé ghi đúng **chưa ghi nhận dị ứng thuốc**.
   - Lời dặn điều kiện của bác sĩ *"nếu đêm nay cháu sốt cao trên 39 độ…"* `[T7]` được giữ ở **`CẦN XÁC NHẬN`** kèm lý do *"câu giả định, chưa xảy ra"*.
2. **Ca mẫu 2 (`demo_hai_benh_nhan`) — Hai bệnh nhân cùng phòng khám trao đổi với bác sĩ:**
   - Anh Minh (bệnh nhân đang mở hồ sơ) khai đau thượng vị 5 hôm nay, không dị ứng thuốc `[T2, T5]`.
   - Người bệnh sổ kế tiếp ngồi cạnh xen vào hỏi chuyện đái tháo đường dùng Metformin `[T3]` và khai *"còn tôi thì bị dị ứng cefuroxim… với lại đêm qua còn nôn hai lần nữa"* `[T6]`.
   - Ngay cả khi mô hình trích nhầm dị ứng Cefuroxim cho anh Minh (`chu_the = "bệnh nhân"`), **Khóa K3 (`chu_the_nguoi_ke`) chặn đứng** không cho lọt vào mục `DỊ ỨNG` của anh Minh mà đẩy sang **`CẦN XÁC NHẬN`** kèm cảnh báo đỏ; câu lược chủ ngữ *"đêm qua nôn hai lần"* cũng bị giữ ở **`CẦN XÁC NHẬN`** để bác sĩ xác nhận là của ai trước khi ký.
3. **Ca mẫu 3 (`demo_lao_khoa_con_gai`) — Bác sĩ, Cụ ông 74 tuổi và Con gái:**
   - Con gái nói bố quên thuốc cả tuần `[T2]`, cụ ông đính chính vẫn uống đều `Amlodipin 5mg` mỗi sáng, chỉ quên hôm kia `[T3]` → thông tin cũ bị thay thế; dị ứng Aspirin của con gái `[T5]` tách sang tiền sử gia đình; thuốc kháng sinh gọi theo tên dân gian *"vỉ a móc"* `[T5]` bị khóa K6 giữ lại ở **`CẦN XÁC NHẬN`** chờ bác sĩ kiểm tra vỉ thuốc thật.

Toàn bộ các kịch bản này được kiểm thử tự động trong [`tests/test_demo_bac_si_nguoi_nha.py`](tests/test_demo_bac_si_nguoi_nha.py) và [`tests/test_dich_vu.py`](tests/test_dich_vu.py).

---

## YÊU CẦU 3: KIỂM TRA TÍNH ĐỘC LẬP CỦA BỘ DỮ LIỆU & THỬ NGHIỆM NGOÀI KHUÔN

### 3.1. Công khai cách tạo, mở rộng lên 657 khuôn và kiểm soát chất lượng mẫu tổng hợp

1. **Vì sao sinh bằng luật xác định thay vì dùng LLM viết hội thoại (`src/bo_du_lieu/sinh_hoi_thoai_viet.py`, `src/bo_du_lieu/bien_the_cau.py`, `docs/HO_SO_DU_LIEU_DATASHEET.md`):**
   - Hội thoại do LLM tự viết thường đầy đủ chủ ngữ và sạch bất thường, làm biến mất hai hiện tượng gây lỗi quy gán nặng nhất trong tiếng Việt: **lược chủ ngữ** và **đại từ họ hàng đa nghĩa** (*con, cháu, em, ông nhà*).
   - Bộ sinh của dự án ghép kịch bản bằng luật xác định có hạt giống cố định (`seed=42` cho v1; `seed=2611` cho v2 mở rộng), gán nhãn đáp án có cấu trúc `dap_an` ngay lúc sinh (chủ thể thật, trạng thái đính chính thật, lượt bằng chứng thật) và kiểm soát 4 bẫy lộ đáp án (chỉ chèn thêm không xoá lượt gốc; giữ cả hai mốc ở `diễn biến`; độ dài hội thoại độc lập với bẫy; vị trí bẫy rải đều).
2. **Mở rộng từ 200 khuôn lên 657 khuôn ca bệnh trên 21 hệ cơ quan (`src/bo_du_lieu/kho_khuon.py`, `src/bo_du_lieu/khuon_mo_rong.py`):**
   - Hợp nhất một nguồn khuôn duy nhất gồm **200 khuôn gốc** (`da_duyet = True`) + **457 khuôn mở rộng** (`da_duyet = False`, gắn nhãn minh bạch chưa qua bác sĩ chuyên khoa duyệt), phủ **21 hệ cơ quan**, hệ lớn nhất không vượt quá `10,83%`.
   - Triển khai bộ biến thể câu ngữ cảnh hóa (`src/bo_du_lieu/bien_the_cau.py`): câu hỏi bác sĩ bám theo triệu chứng/thuốc vừa nêu mà không lộ chẩn đoán tương lai (*Zero Information Leak*).
3. **Kiểm soát chất lượng tự động trên toàn bộ 5.000 ca v2 (`87.097` lượt thoại):**
   - `tools/kiem_chat_luong_cau.py` (6 quy tắc): lỗi lặp từ ghép câu `0,000%`, hạt đề nghị thừa sau dấu chấm `0,000%`, cụm nhận xét cụt sau dấu chấm `0,000%`, kết thúc bằng dấu phẩy/hai chấm `0,000%`, hai dấu cách liên tiếp `0,000%`. Đọc kiểm tra thủ công 50 ca ngẫu nhiên lưu tại `docs/ket-qua/doc-mau-v2-sau-khi-sua.md`.
   - `tools/kiem_tra_trich_dan_v2.py`: **52.634 / 52.634 đoạn `trich_dan` (100,0000%)** là chuỗi con nguyên văn của đúng lượt thoại được dẫn.

---

### 3.2. Minh chứng: Thống kê trùng lặp, Danh sách tập Train/Dev/Test & Kết quả ngoài khuôn

#### A. Thống kê độ lặp câu và độ đa dạng từ vựng (`src/do_luong/do_lap_cau.py` trên 5.000 ca)

| Chỉ số đo lường | Bộ v1 cũ (200 khuôn) | Bộ v2 mở rộng (657 khuôn) | Biến động thực tế |
| :--- | :---: | :---: | :--- |
| Tổng số ca / Mã định danh | 5.000 (`hv_0001..5000`) | 5.000 (`v2mr_0001..5000`) | `0` ca trùng ID hoặc trùng `input` với bộ cũ |
| Khuôn bệnh thực tế xuất hiện | 200 / 200 | **656 / 657** | Trung vị 7 ca/khuôn (tối đa 17 ca/khuôn) |
| Tổng số lượt thoại | 87.473 | **87.097** | Trung vị 13 từ/lượt |
| Số câu duy nhất (khác nhau) | 20.190 | **45.835** | **+25.645 câu (+127,0%)** |
| **Tỷ lệ lặp (mọi câu)** | 76,92% | **47,37%** | **Giảm 29,55 điểm %** |
| **Tỷ lệ lặp (câu dài $\ge 8$ từ)** | 69,60% | **42,19%** | **Giảm 27,41 điểm %** |
| Độ phong phú từ vựng **MTLD** | 93,0 | **145,4** | **+56,3%** |
| Độ đa dạng Bigram **Distinct-2** | 0,0188 | **0,0468** | **+148,9%** |

*Giải trình minh bạch về con số 47,37%:* Sau khi ngữ cảnh hóa câu hỏi bác sĩ, 100% câu hỏi khai thác của bác sĩ đã biến mất khỏi nhóm câu lặp cao nhất; phần lặp còn lại chủ yếu là phản xạ đáp ngắn tự nhiên của người Việt khi đi khám (*"của tôi ạ."*, *"vâng ạ."*, *"tôi đi khám."*). Dự án chủ động dừng tại đây và báo số thật, không chèn từ đệm giả tạo để ép chỉ số.

#### B. Phân chia độc lập theo khuôn bệnh & Ma trận trùng lặp ngữ nghĩa Train – Test
Đơn vị chia tách trong [`src/bo_du_lieu/chia_tap_theo_khuon.py`](src/bo_du_lieu/chia_tap_theo_khuon.py) là **khuôn bệnh (`benh`) chia độc lập theo từng đợt**, tuyệt đối không chia ngẫu nhiên theo dòng hội thoại:

| Tập dữ liệu (v2 mở rộng) | Số khuôn phân bổ (`bang_tap_khuon`) | Số khuôn xuất hiện trong 5.000 ca | Số ca khám | Số mệnh đề đáp án | Tệp vân tay SHA-256 công khai trong kho mã |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Huấn luyện (`viet_train_v2`)** | 515 | 514 | 3.925 | 37.232 | [`data/viet_train_v2.van_tay.json`](data/viet_train_v2.van_tay.json) |
| **Phát triển (`viet_phat_trien_v2`)** | 72 | 72 | 551 | 5.345 | [`data/viet_phat_trien_v2.van_tay.json`](data/viet_phat_trien_v2.van_tay.json) |
| **Kiểm tra cuối (`viet_kiem_tra_cuoi_v2`)** | 70 | 70 | 524 | 4.953 | [`data/viet_kiem_tra_cuoi_v2.van_tay.json`](data/viet_kiem_tra_cuoi_v2.van_tay.json) |
| **Tổng cộng** | **657 khuôn** | **656 khuôn** | **5.000 ca** | **47.530** | Danh sách tên từng khuôn: [`data/manifest_v2_mo_rong_5000.json`](data/manifest_v2_mo_rong_5000.json) |

Đo ma trận trùng lặp từ khóa triệu chứng lâm sàng giữa `515` khuôn Train và `70` khuôn Test (`36.050` cặp khuôn) bằng `tinh_ma_tran_trung_lap_train_test` trong [`src/do_luong/kiem_nghiem_ngoai_khuon.py`](src/do_luong/kiem_nghiem_ngoai_khuon.py):
- **Giao tập tên khuôn Train $\cap$ Dev $\cap$ Test:** **`0` khuôn** (`hoan_toan_doc_lap = True`); `0` khuôn trong 200 khuôn gốc bị dịch chuyển tập khi mở rộng (`tests/test_chia_khuon_mo_rong_khong_doi.py`).
- **Jaccard từ khóa triệu chứng trung bình giữa mọi cặp khuôn Train – Test:** **`0,0587`** (`5,87%`); phân vị thứ 95 (`p95`): **`0,1172`** (`11,72%`); tỷ lệ cặp khuôn có Jaccard $\ge 0,20$: chỉ **`0,0017` (`0,17%`)** (giảm mạnh so với `2,11%` ở bộ v1 200 khuôn).
- **Trùng lặp N-gram trên toàn tập mô tả triệu chứng Train vs Test:** Bigram Jaccard = **`0,0891`** (`8,91%`), Trigram Jaccard = **`0,0287`** (`2,87%`).

#### C. Kết quả thử nghiệm trên kịch bản ngoài khuôn & dữ liệu ngoài nguồn + Phân tích lỗi

1. **Đánh giá mô hình trích xuất trên khuôn bệnh chưa từng gặp (Template-Disjoint Dev):**
   - Trên 30 ca phát triển (thuộc các khuôn bệnh tách rời hoàn toàn khỏi tập Train): Qwen3-4B + adapter QLoRA giảm tỷ lệ bỏ sót từ `43,1%` xuống **`11,5%`** (`0/30` ca JSON lỗi).
   - Trên bộ thử thách *đổi chủ thể* (các cặp hội thoại đối kháng thuộc khuôn giữ lại): đường ống `C_khoa` nâng F₁ từ `66,1%` lên **`70,8%`**, giảm SER từ `45,4%` xuống **`36,9%`**.
   - Trên **240 ca giữ kín `thach_thuc_v2`** (chạy đúng 1 lần sau khi khóa luật): độ nhạy trung bình của lớp cảnh báo đạt **`0,871`**, bằng đúng mức `0,871` trên tập điều chỉnh — chứng minh bộ luật không học vẹt theo mẫu câu tập Train.
2. **Đánh giá các tầng luật trên 10 kịch bản bệnh hiếm hoàn toàn ngoài kho 657 khuôn (`OOT_01..OOT_10` trong `src/do_luong/kiem_nghiem_ngoai_khuon.py`):**
   - Gồm 10 bệnh lý chuyên sâu không nằm trong kho sinh dữ liệu (*Guillain-Barré, suy thượng thận Addison, u tủy thượng thận Pheochromocytoma, nhược cơ Myasthenia Gravis, bệnh Wilson, hội chứng Brugada, viêm đa cơ tự miễn, viêm động mạch Takayasu, hội chứng Churg-Strauss, Amyloidosis tim–thận* — tổng **52 mệnh đề**, mỗi ca đều cài bẫy người nhà kể bệnh riêng + bệnh nhân tự đính chính).
   - Kết quả chạy `chay_kiem_nghiem_ngoai_khuon()`: gán đúng chủ thể **`52/52` (`100%`)**, chống gán nhầm bệnh/dị ứng của người nhà sang bệnh nhân **`11/11` (`100%`)**, bảo toàn trích dẫn nguyên văn **`52/52` (`100%`)**, xử lý đính chính chuyển sang `bị thay thế` **`10/10` (`100%`)**. *(Lưu ý minh bạch: phép thử này đo tính tổng quát của các tầng luật Pro-drop + Khóa K1 + FSM trên mệnh đề chuẩn của kịch bản mới, không đo khâu LLM trích xuất).*
3. **Thử nghiệm khâu AI trích xuất trên văn bản y tế thực tế ngoài nguồn (`ViMQ` — 200 câu hỏi người bệnh Việt Nam, ghi nhận tại `docs/tien-do-21-11-2026.md`):**
   - Chạy `Qwen3-4B + best_checkpoint` trên 200 mẫu của bộ dữ liệu công khai `ViMQ` (nguồn độc lập hoàn toàn với bộ sinh của dự án):
     - Tỷ lệ xuất JSON hợp lệ: **`192/200` (`96,0%`, `8` mẫu lỗi JSON = `4,0%`)**.
     - Trích dẫn là chuỗi con nguyên văn: **`272/276` mệnh đề (`98,6%`)**; `4` mệnh đề bị khóa K1 lọc bỏ do lệch chuỗi con.
     - Độ phủ thực thể y khoa gốc của `ViMQ`: **`284/322 = 88,2%`**.
   - **Phân tích lỗi thẳng thắn trên dữ liệu ngoài nguồn:** Khi đọc kiểm tra 25 mẫu đầu ra trên `ViMQ`, nhóm phát hiện mô hình biến một số **câu hỏi chưa có câu trả lời** (ví dụ *"Mổ cột sống sau bao lâu có thể mang thai?"*) thành mệnh đề `"tinh_huong": "thực tế"`. Nguyên nhân là trong dữ liệu hội thoại khám bệnh, người bệnh thường trả lời/kể triệu chứng còn bác sĩ mới là người đặt câu hỏi, nên khi gặp câu hỏi đơn lẻ của người bệnh trên diễn đàn `ViMQ`, mô hình bị lệch phân phối. Nhờ phát hiện này, dự án **quyết định không đưa nhãn máy ViMQ vào huấn luyện** để bảo vệ bất biến *"không biến câu hỏi chưa trả lời thành sự thật"*, đồng thời có luật `QUESTION_AS_FACT` ở lớp cảnh báo để chặn khi câu dẫn có dấu hỏi.

---

## PHỤ LỤC: TỔNG HỢP NÂNG CẤP KIẾN TRÚC, BẢO MẬT & KIỂM THỬ TOÀN HỆ THỐNG (ĐỢT 11/2026)

Bên cạnh 3 yêu cầu trọng tâm của Ban Giám khảo, toàn bộ mã nguồn triển khai (`src/`, `web/may-chu/`, `web/src/`) đã được rà soát kiểm toán kiến trúc toàn diện và nâng cấp đồng bộ:

1. **Tầng Python Core (`src/`):**
   - Khử định danh (`src/he_thong/khu_dinh_danh.py`): vá lỗi biểu thức chính quy nuốt triệu chứng sau họ người và lỗi tên 1 âm tiết làm hỏng từ y khoa (*an thần, bình thường, losartan*).
   - Xuất HL7 FHIR R4 (`src/cong_cu_lam_sang/xuat_fhir_r4.py`) & Tiền kiểm BHYT (`src/cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot.py`): tách vế câu dị ứng hỗn hợp (*"không dị ứng thức ăn, chỉ nổi mề đay với ceftriaxone"*), tách thuốc đang dùng ở nhà khỏi y lệnh mới kê, loại trừ bệnh nền của người nhà (`subject != bệnh nhân`) và bệnh đã phủ định khỏi gợi ý mã ICD-10.
   - Dược lý & Biệt dược (`src/cong_cu_lam_sang/tra_duoc_thu_aho_corasick.py`, `src/he_thong/rao_chan_an_toan.py`, `src/he_thong/dieu_phoi_cac_chot_an_toan.py`): ánh xạ chuẩn `Sintrom → acenocoumarol` (tách khỏi `warfarin`), loại câu dị ứng/lối sống khỏi danh sách thuốc đang dùng để không báo tương tác giả, bảo toàn số lẻ `.5` cho thang điểm Wells PE (`src/cong_cu_lam_sang/thang_diem_nguy_co.py`).
   - Tối ưu `GET /api/suc-khoe` (`src/he_thong/dich_vu_http.py`): khởi động lạnh giảm xuống `< 1 giây` mà không kéo `torch`/`scipy` lên RAM khi chưa cần; bổ sung khóa suy luận GPU (`_khoa_suy_luan`) và huấn luyện DPO theo lô 2 chuỗi có tự kiểm sai số (`src/huan_luyen/huan_luyen_dpo.py`).
2. **Tầng Máy chủ Node/Express BFF (`web/server.ts`, `web/may-chu/`):**
   - Tách mô-đun sạch sẽ (`routes/*`, `tra-cuu/*`, `tro-ly/*`) kèm hợp đồng kiểu 2 chiều (`src/he_thong/hop_dong_api.py` ↔ `web/src/types/api-contract.ts`).
   - Trợ lý nhiều tác tử ẩn danh (`web/may-chu/tro-ly/`): dựng dữ liệu gửi mô hình ngoài từ danh sách cho phép (allowlist), giữ nguyên nhãn `[DỊ ỨNG]` để không bao giờ biến dị ứng Penicillin thành *"thuốc đang dùng"*, quy đổi chuẩn đơn vị liều (`mg/µg/g`, `/phút` ↔ `/giờ`, số thập phân `0.125 mg` và phân cách hàng nghìn tiếng Việt `1.500 mg` trong `kiem-dinh-so.ts`), hỗ trợ SSE stream và hủy tác vụ (`DELETE /api/tro-ly/:id`).
   - An ninh & Toàn vẹn dữ liệu: gỡ bỏ hoàn toàn wildcard CSRF (`.vercel.app` / `.trycloudflare.com`), chỉ cho phép danh sách nguồn cấu hình tường minh qua HTTPS; thêm khóa đồng bộ lạc quan `409 Conflict` cho `PUT /api/ca-kham/:id`; chống IDOR chéo bác sĩ và phát hiện cắt chuỗi/xoá trắng nhật ký ký duyệt bằng tệp neo `.anchor.json` (`web/may-chu/worm.ts`).
3. **Tầng Giao diện React (`web/src/`):**
   - Cô lập tuyệt đối dữ liệu giữa các ca khám và người dùng (`key={currentSession.id}`, IndexedDB ghi âm tách theo `userId`, hủy luồng thu âm cũ khi đăng xuất/chuyển ca, không rò rỉ dữ liệu mẫu sang tờ dặn dò của ca thật).
   - Bổ sung 3 lớp `ErrorBoundary.tsx`, chia 6 gói `React.lazy`, sửa cắt trang khi in bệnh án A4 (`@media print`), đồng bộ đa tab qua `BroadcastChannel`, và khóa cứng điều kiện ký duyệt WORM khi chưa xác nhận hết thông tin nghi ngờ.
4. **Quy mô kiểm thử tự động hiện tại (chạy xác nhận ngày 26/11/2026):**
   - **Python (`pytest tests/`):** **1.779 phép thử vượt qua**, `0` thất bại (25 phép thử bỏ qua có chủ đích khi môi trường không gắn phần cứng/mô hình nặng).
   - **TypeScript Backend & Frontend (`cd web && npm run lint && tsx --test ...`):** `0` lỗi kiểu `tsc --noEmit`, **43/43 phép thử đơn vị & tích hợp vượt qua 100%**, đóng gói sản xuất sạch (`npm run build`).
