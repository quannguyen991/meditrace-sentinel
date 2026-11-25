# Kế hoạch nâng cấp toàn diện MediTrace Sentinel

**Phiên bản:** 1.4  
**Ngày lập:** 17/11/2026 (cập nhật tiến độ 21/11/2026)  
**Căn cứ:** rà soát mã nguồn, ảnh “Đề cải tiến – Phiên bản 1”, các ứng dụng AI scribe, Devpost, mã nguồn mở và HL7 FHIR.

## 0. Cập nhật tiến độ 21/11/2026 (so với bản 1.3 ngày 17/11)

Nguồn: `docs/BAN-GIAO-CONG-VIEC-DANG-DO.md` (20–21/11). Các con số dưới đây lấy từ tài liệu đó, chưa được kiểm lại bằng cách chạy mã hay đối chiếu với `docs/tien-do-19-11-2026.md`.

**Đã có thêm:**

| Hạng mục | Trạng thái | Liên quan mục |
|---|---|---|
| Bộ dữ liệu tổng hợp | 5.000 ca, 200 khuôn bệnh, seed 42. Chia theo khuôn: huấn luyện 3.751 ca (150 khuôn), phát triển 663 ca (26 khuôn), kiểm tra 586 ca (24 khuôn). Danh sách ca đã đóng băng trong `data-rieng-tu/ket-qua/manifest/dong-bang-5000.json` (mã băm `45d9f862…`). Kiểm `kiem_khuon`: 0 lỗi, 25 cảnh báo, 18 cặp khuôn trùng từ 50% triệu chứng | 2.1, GĐ 1, GĐ 1B (Đợt A) |
| Dữ liệu cho khâu trích xuất | `data/trich_train.jsonl` (3.751 ca, 31.916 mệnh đề), `data/trich_giu_lai.jsonl` (663 ca, 5.620 mệnh đề) | 4.3B |
| Kiểm rò rỉ ASR | VietMed dùng chung người nói, âm thanh và văn bản giữa các tập; ViMedCSS trùng video 93,8%. Báo cáo ở `data-rieng-tu/ket-qua/kiem-ro-ri/` | GĐ 1, GĐ 5 |
| Thí nghiệm ASR | LoRA giảm lỗi từ (WER) trên VietMed 0,033 (khoảng tin cậy 0,027–0,041). Giải mã beam so với greedy giảm 0,016 trên VietMed-500 nhưng không cải thiện trên ViMedCSS, nên chưa áp dụng beam | GĐ 5 |
| Mô hình Qwen | Đã quyết định lại (xem mục 4.3E). Qwen3-8B đã xoá; Qwen3-4B tải lại vào ổ C, kiểm hash | 4.3E |

**Tiến độ cập nhật đến 24/11/2026:**

- **Mở chặn huấn luyện & Loss theo đoạn (Luồng A hoàn thành):** `src/loss_theo_doan.py` hạ đỉnh VRAM trên RTX 3060 xuống 6,4 GiB (ngưỡng an toàn 8,9 GiB). Hoàn thành huấn luyện checkpoint-100 lên checkpoint-200 (`best_checkpoint`) với `eval_loss` đạt 0,00088.
- **Đo tỷ lệ bỏ sót thực nghiệm (Task A6 hoàn thành):** Đo trên 30 ca phát triển (304 mệnh đề): Qwen3-4B chưa huấn luyện bỏ sót **43,1%** (khoảng 37,6%–48,7%), trong khi Qwen3-4B + adapter giảm tỷ lệ bỏ sót xuống **11,5%** (khoảng 8,4%–15,6%) với 0 ca JSON lỗi (báo cáo tại `docs/ket-qua/bo-sot-qwen3-4b.md`).
- **Nâng cấp toàn diện bộ dữ liệu v2 (Luồng B & F hoàn thành, người dùng đã duyệt chốt Phương án A):**
  - Mở rộng kho lên **657 khuôn bệnh** thuộc 21 hệ cơ quan (`src/kho_khuon.py`).
  - Sinh đủ 5.000 ca mở rộng (`data/hoi_thoai_viet_v2_mo_rong.jsonl`, seed=2611).
  - Tỷ lệ lặp câu giảm mạnh từ 76,92% xuống **47,37%** (với câu $\ge 8$ từ: **42,19%**); số câu duy nhất tăng 127% lên **45.835 câu**; MTLD đạt **145,4** (+56,3%); Distinct-2 đạt **0,0468** (+148,9%).
  - Kiểm định chất lượng 6 quy tắc: **0 lỗi** ngữ pháp/hạt thừa/hai dấu cách.
  - Kiểm định trích dẫn nguyên văn Axis 2: **100,0000%** trích dẫn khớp chuỗi con nguyên văn (52.634 / 52.634 đoạn trích).
  - Đóng băng WORM audit log seq 6 tại `data/manifest_v2_mo_rong_5000.json`.
  - Phân chia độc lập cho huấn luyện: `viet_train_v2.jsonl` (3.925 ca), `viet_phat_trien_v2.jsonl` (551 ca), `viet_kiem_tra_cuoi_v2.jsonl` (524 ca) và bộ trích `trich_train_v2.jsonl`, `trich_giu_lai_v2.jsonl` (Zero Template Leakage).
- **Hàng đợi bền vững SQLite (Luồng C hoàn thành):** `web/may-chu/hang-doi.ts` lưu việc nền bền vững, chịu crash recovery; 11 nhóm kiểm thử TypeScript passed 100%.
- **Đồng bộ tài liệu (Luồng D1 hoàn thành):** Cập nhật toàn diện README, Q&A ban giám khảo, Bảng số liệu thực nghiệm chi tiết; rút bỏ hoàn toàn con số "78,3%" chưa có phép đo.
- **Trạng thái kiểm thử hệ thống:** 1.540 bài kiểm thử Pytest passed 100% (26 skipped, 0 failed trong 164.83s).

## 1. Mục tiêu sản phẩm

Phát triển MediTrace thành trợ lý tạo **bản nháp ghi chép khám bệnh tiếng Việt có thể truy vết**, để bác sĩ kiểm tra, sửa và xác nhận từng thông tin. Trọng tâm là giảm lỗi khó nhận ra: sai người, mất lời đính chính, nhầm dự định với việc đã làm, bỏ sót thông tin quan trọng hoặc thêm nội dung không được nói.

Ba yêu cầu trong ảnh là tiêu chí xuyên suốt:

1. **Giảm bỏ sót:** định nghĩa loại lỗi/mức nghiêm trọng; khi thiếu căn cứ thì giữ ở mục cần xác nhận, không âm thầm loại hoặc tự điền.
2. **Kiểm soát lỗi qua các bước AI:** giữ liên kết audio, transcript, người nói, chủ thể, trạng thái lời nói, mệnh đề và quyết định duyệt; cho phép mở nguồn để xác nhận.
3. **Kiểm tra tính độc lập của dữ liệu:** chia theo khuôn/kịch bản/nguồn, thử hội thoại mới và báo cáo rò rỉ ngữ nghĩa, không chỉ tìm ID trùng.

Định vị: MediTrace tạo bản nháp có nguồn để bác sĩ duyệt. Chưa mở rộng sang chẩn đoán, kê đơn hoặc tự thực thi hành động lâm sàng nếu chưa thẩm định riêng.

## 2. Hiện trạng kho mã đã rà soát

Phân loại dưới đây phản ánh mã và tài liệu, không xác nhận mọi tính năng đã chạy với mô hình thật.

| Năng lực | Đã thấy trong kho | Khoảng trống |
|---|---|---|
| Ghi âm/tải audio, chép âm tiếng Việt | Có giao diện, API và pipeline PhoWhisper; có tùy chọn tách người nói. | Cần kiểm thử trên mô hình/máy triển khai; gắn nguồn và cấu hình vào kết quả. |
| Timestamp và dẫn nguồn | Audio có segment ID, mốc thời gian, metadata; có giao diện thử nghe đoạn riêng. | Giao diện chính chưa nối mệnh đề với audio; audioUrl tạm bị loại khi lưu nên mở lại ca chưa đảm bảo nghe được. |
| Trích xuất và kiểm căn cứ | Có pipeline nhiều bước; luật về trích dẫn, chủ thể, phủ định, thời gian, liều và rủi ro. | Cần đo bỏ sót/cảnh báo nhầm theo nhóm, phân biệt lỗi từ ASR, trích xuất và luật. |
| AI hỗ trợ tìm kiếm y khoa | Đã có `EvidenceView`, lựa chọn nguồn; API `/api/lookup-official` truy vấn nhiều kho/website; `TraLoiCoNguon` hiển thị nguồn đã tra, nguồn được trích, lưu ý an toàn và tra nguồn khác; API gợi ý câu hỏi theo nhóm. | Cần nghiệm thu truy vấn thực tế, thêm nguồn chính thống Việt Nam hiện hành, gắn trích dẫn riêng cho từng câu hỏi gợi ý, hiển thị ngày/phạm vi/tính cập nhật nguồn và thiết kế panel theo nhóm lâm sàng. Code có sẵn không đồng nghĩa mọi nguồn/API đã hoạt động ổn định khi triển khai. |
| Đính chính/mâu thuẫn | Có mã cập nhật thông tin tự sửa, thay thế, diễn biến và mâu thuẫn. | Cần kiểm tra nhất quán từ transcript đến bản nháp, duyệt, lưu và xuất. |
| Duyệt mệnh đề | Có giữ/sửa/bỏ, trạng thái cần xem và lưu quyết định. | Cần lịch sử phiên bản; sửa bản nháp phải làm trạng thái duyệt cũ hết hiệu lực. |
| Mẫu/dữ liệu ứng dụng | Có trang mẫu với tìm kiếm và tạo mẫu tùy chỉnh; dữ liệu mặc định/demo và trạng thái mẫu đang giữ trong state giao diện. | Xây thư viện mẫu có lưu bền, phân loại/quyền sở hữu, lọc/sắp xếp, mẫu theo phiên và đặt mẫu mặc định; xác minh đường sinh tài liệu có nguồn. |
| Tờ dặn dò | Có module Python và giao diện in; hiện có hồ sơ/thuốc mẫu, nhãn minh họa. | Chưa xác nhận nối đầu cuối từ nội dung bác sĩ duyệt; ngăn nhầm nội dung mẫu thành chỉ định. |
| FHIR, dược lý, thang điểm | Có module và kiểm thử riêng; nhật ký “8 chốt” ghi rõ minh họa. | Chưa xác nhận giao diện web gọi xuyên suốt; tài liệu ghi chưa kết nối HIS/EMR. |
| Đánh giá | Bộ sinh hiện có 200 khuôn bệnh; test trong kho kiểm tra đủ 200 khuôn và có logic chia theo khuôn. | README còn ghi mốc cũ 100 khuôn/5.000 ca. Đồng bộ tài liệu và xác minh manifest/dataset/checkpoint của từng lần train. 200 khuôn giảm rủi ro nhưng không tự chứng minh test độc lập hay đại diện lâm sàng. |

### 2.1. Rà soát sâu mã nguồn và các cổng cần xử lý

Đây là kết quả đọc tĩnh mã nguồn/tài liệu trong kho; chưa xác nhận chất lượng lâm sàng, cấu hình production hay hành vi trên dữ liệu thật.

| Phát hiện trong repo | Ý nghĩa | Việc cần làm |
|---|---|---|
| `src/ngu_lieu_viet.py` có 200 khuôn; `tests/test_mo_rong_bo_du_lieu.py` sinh 5.000 ca trong fixture. Chưa thấy dataset JSONL/checkpoint/manifest huấn luyện trong `data/` (hiện thấy DB ứng dụng). **Cập nhật 21/11/2026:** bản bàn giao 20/11 ghi đã có bộ 5.000 ca với manifest đóng băng và checkpoint-50/100 trên máy HoaiĐức (xem mục 0); hàng này giữ lại để ghi nhận tình trạng lúc rà soát 17/11. | 5.000 là quy mô bộ sinh trong test, chưa chứng minh có bộ train 5.000 mẫu đã lưu hoặc đã dùng để huấn luyện. | Tách trạng thái bộ sinh, dataset và checkpoint; kiểm tra artifact ngoài repo/đường dẫn ignore; xuất manifest/fingerprint thực tế trước khi công bố baseline. |
| `src/tach_tap_viet.py` chia riêng nhóm 100 khuôn gốc và nhóm khuôn mới. Với 200 khuôn, logic hiện tại tạo khoảng 150/26/24 khuôn train/dev/test; ở 300 khuôn dự kiến 250/26/24. | Dev/test không tăng tương ứng với tổng dữ liệu ở mốc 300; tỷ lệ nhóm cũ/mới không cân xứng. | Trước khi sinh thêm dữ liệu, thiết kế split manifest theo đích đánh giá và phân tầng theo nguồn/kịch bản; khóa test độc lập; không lấy số ước tính thay manifest. |
| `src/train_baseline.py` kiểm tra tương thích dữ liệu bằng số mẫu và hash một phần (mẫu đầu/cuối), trong khi `src/van_tay_bo.py` có fingerprint đầy đủ cho luồng khác. | Chỉnh sửa ở phần giữa dữ liệu có thể không bị phát hiện trong một số lần tiếp tục huấn luyện. | Dùng hash chuẩn hóa toàn bộ bản ghi/nhãn; lưu split-manifest ID, phiên bản tokenizer/model/adapter, cấu hình train và mã nguồn sinh trong checkpoint metadata. |
| `PatientsView`/`TasksView` dùng dữ liệu mẫu; `TemplatesView` dùng `defaultTemplates` và state giao diện dù backend có kho `mau-van-ban`. | UI demo có thể bị hiểu là dữ liệu thật; thư viện Heidi-like chưa bền vững ở luồng lưu/quyền. | Gắn nhãn demo; nối kho thật có phân quyền, phiên bản và audit; xử lý trạng thái rỗng/lỗi/offline và xung đột cập nhật. |
| `web/src/lib/taiKhoan.ts` giữ bản sao `localStorage` và đồng bộ snapshot qua API; backend lưu SQLite; JSON body giới hạn 60 MB. | PHI có nhiều bản sao; snapshot có thể ghi đè giữa tab/thiết bị; cần xác nhận DB bền vững theo topology triển khai. | Rà soát data-flow/threat model; giới hạn theo endpoint, rate limit AI/audio, origin allowlist chặt, mã hóa/retention/khôi phục và optimistic concurrency; không dùng filesystem serverless tạm cho DB. |
| Gọi model ngoài cần `allowExternal`, có che một số mẫu PII; tùy chọn ở giao diện lưu toàn cục. API audio Python mặc định bind loopback nhưng chưa có auth riêng. | Che chuỗi nhận dạng không đồng nghĩa ẩn danh; gửi dữ liệu y tế và mở audio service ra mạng cần kiểm soát phiên/quyền. | Đồng ý theo phiên khám, hiển thị provider/mục đích/dữ liệu trước khi gửi; mặc định local/off; giữ audio API localhost cho tới khi có auth, TLS, quota và kiểm soát quyền. |
| Tra cứu y khoa và panel nguồn đã có; `/api/questions-external` chưa gắn citation riêng từng câu gợi ý; metadata ngày/phạm vi nguồn chưa được quản trị tập trung. | Khó kiểm chứng gợi ý lâm sàng và độ mới/phạm vi của nguồn. | Source registry allowlist có quốc gia, loại tài liệu, hiệu lực/ngày rà soát; citation cho từng gợi ý; kiểm URL/trích đoạn, prompt injection, cache, giới hạn tần suất và quyền sử dụng. |

**Cổng P0 trước khi tăng quy mô hoặc pilot:** (1) baseline tái lập từ manifest/model thực tế; (2) test khóa và báo cáo rò rỉ; (3) dữ liệu demo nhận diện rõ; (4) data-flow/đồng ý/provider ngoài và lưu trữ được rà soát; (5) lỗi nghiêm trọng có taxonomy và đường đưa về bác sĩ xác nhận.

## 3. Học hỏi từ nền tảng và dự án

| Nguồn | Ý tưởng tham khảo | Hướng áp dụng |
|---|---|---|
| [AWS HealthScribe](https://docs.aws.amazon.com/transcribe/latest/dg/health-scribe.html) | Transcript theo lượt, vai, thuật ngữ, ghi chú sơ bộ và dẫn chứng; đầu ra có tính xác suất, cần chuyên gia rà soát. | Giữ nguồn và quy trình duyệt con người xuyên suốt. |
| [Heidi](https://www.heidihealth.com/solutions/medical-scribe-software) | Mẫu chuyên khoa, tài liệu chuyển tuyến, chỉnh sửa trước khi ký. | Mẫu chỉ điền dữ kiện có nguồn và trạng thái duyệt. |
| [Abridge](https://www.abridge.com/press-release/abridge-inside-emory) | Liên kết nội dung với bằng chứng hội thoại. | Bấm mệnh đề để xem transcript và nghe đoạn tương ứng. |
| [Nabla Connect](https://nabla.com/connect) | Tích hợp scribe như một lớp trong sản phẩm/EHR. | Tích hợp sau khi bản nháp, phiên bản và quyền truy cập ổn định. |
| [Ambience Patient Summary](https://www.ambiencehealthcare.com/blog/ambience-healthcare-s-patient-recap-offers-clinicians-the-first-chart-summarization-technology-from-an-ambient-ai-platform) | Tóm tắt hồ sơ trước khám. | Để sau vì cần nguồn hồ sơ, quyền truy cập và dẫn nguồn riêng. |
| Devpost: [Clinical Note Guard](https://devpost.com/software/clinical-note-guard), [CarryOver](https://devpost.com/software/carryover-tcrfw3), [Resona](https://devpost.com/software/resona-x4fwds), [CareScribe](https://devpost.com/software/carescribe) | Bằng chứng theo mệnh đề, nghe lại theo mốc, checklist trước duyệt, provenance và timeline hành động. | Dùng làm gợi ý thiết kế/demo; mô tả hackathon không chứng minh hiệu quả lâm sàng. |
| Mã mở: [NoteTrace](https://github.com/pisong314/notetrace), [Berta](https://github.com/phairlab/berta-ai-scribe), [Open Medical Scribe](https://github.com/BirgerMoell/open-medical-scribe), [OpenScribe](https://github.com/sammargolis/OpenScribe) | Kiểm tra nội dung theo nguồn, mẫu theo quy trình, provider linh hoạt. | Học thiết kế; kiểm tra license/bảo mật trước khi dùng lại mã. |
| [FHIR DocumentReference](https://hl7.org/fhir/R4/documentreference.html), [FHIR Provenance](https://hl7.org/fhir/R4/provenance.html) | Tham chiếu tài liệu, phiên bản, tác nhân và hoạt động tạo/sửa/ký. | Chuẩn bị trao đổi tài liệu; FHIR không tự bảo đảm tính đúng hay tích hợp. |
| [WHO AI governance guidance](https://www.who.int/news/item/18-01-2024-who-releases-ai-ethics-and-governance-guidance-for-large-multi-modal-models) | Rủi ro nội dung sai/thiếu, thiên lệch và automation bias; cần người dùng tham gia. | Thử nghiệm có bác sĩ, nhiệm vụ hẹp, theo dõi lỗi sau phát hành. |

## 4. Kiến trúc đích

Audio/lời thoại → transcript có timestamp, người nói, nguồn ASR và lịch sử sửa → mệnh đề có chủ thể, thời gian, phủ định, tình thái và trích dẫn → kiểm căn cứ/thiếu/mâu thuẫn → bác sĩ nghe/xem nguồn, sửa/giữ/bỏ → bản đã duyệt → mẫu/tài liệu → FHIR thử nghiệm → tích hợp có kiểm soát.

Mỗi dữ kiện cần cho biết: lấy từ đâu, ai nói, nói về ai, khi nào, mô hình nào xử lý, ai sửa, quyết định duyệt nào và trên phiên bản nào. Thiếu nguồn phải hiện “chưa ghi nhận/không rõ/cần xác nhận”, không suy thành phủ định.

### 4.1. Hạ tầng và cấu trúc triển khai

**Hiện trạng đọc được trong repo:** frontend React/Vite; Express/Node làm API và định tuyến sang dịch vụ Python; lưu ứng dụng dùng SQLite `node:sqlite` với WAL/giao dịch; luồng audio có session JSON/audio trên filesystem; tạo ghi chú dài dùng hàng đợi `Promise` và `Map` trong bộ nhớ tiến trình. Đây là nền phù hợp cho demo/pilot ít người dùng, nhưng job mất khi tiến trình khởi động lại và DB/filesystem phải được kiểm chứng theo môi trường deployment (`vercel.json` rewrite sang `api.meditrace.vn`).

| Lớp | Hướng nâng cấp | Điều kiện chuyển bước |
|---|---|---|
| Giao diện | Giữ SPA; chia theo domain, tách demo fixtures khỏi dữ liệu thật; API client theo schema/version; trạng thái loading/failed/retry/conflict rõ. | Trước khi trang bệnh nhân, task, template dùng ngoài demo. |
| API nghiệp vụ | Giữ **modular monolith** Express; nhóm module auth/encounter/audio/note/evidence/template/task/FHIR; schema request/response, idempotency key và lỗi chuẩn. Chưa cần microservices. | Tách dịch vụ khi tải, ownership hoặc yêu cầu cô lập tài nguyên đo được. |
| Suy luận | Worker Python/model riêng vì phụ thuộc GPU và thời gian chạy; API điều phối tạo job, trả job ID và đọc trạng thái; không để request web giữ vòng đời GPU. | Worker có health/readiness, giới hạn queue, timeout/cancel/retry và model version. |
| Job dài | Thay `Map`/Promise trong RAM bằng queue bền vững: ban đầu bảng job PostgreSQL + worker có lease; chỉ thêm broker riêng khi cần throughput. Trạng thái queued/running/succeeded/failed/cancelled; idempotency, retry policy, dead-letter. | Kiểm soát được restart, duplicate job, timeout và quyền đọc theo user/encounter. |
| CSDL | SQLite tiếp tục cho local/dev và demo một tiến trình. Khi cần nhiều tiến trình/ghi đồng thời/HA, chuyển dữ liệu nghiệp vụ sang PostgreSQL managed, migration có version/rollback; dùng transaction và optimistic concurrency. Không lưu blob audio trong JSON/CSDL. | Benchmark và rehearsal migration/rollback trước cutover. PostgreSQL hỗ trợ kiểm soát concurrency/transaction isolation; chọn isolation theo invariant thực tế, không mặc định cấu hình nặng nhất. ([PostgreSQL concurrency](https://www.postgresql.org/docs/current/mvcc.html)) |
| Audio/object | Đưa audio/artifact lớn sang object storage riêng có mã hóa, retention, xóa theo session, MIME/size/hash; DB chỉ lưu metadata/object key; download bằng quyền ngắn hạn. | Có threat model, quyền truy cập, đồng thuận, retention/delete và recovery. |
| Đồng bộ UI | Thay gửi nguyên snapshot bằng endpoint theo resource/event; dùng `version`/ETag hoặc compare-and-swap; conflict trả 409 để người dùng chọn/ghép. Bản local chỉ là cache có hạn, không là nguồn sự thật. | Trước khi hỗ trợ nhiều tab/thiết bị hoặc dùng dữ liệu thật. |
| Quan sát/vận hành | Instrument OpenTelemetry traces/metrics/logs; nối trace ID web→API→job→Python/model→DB/provider. Log cấu trúc, không ghi transcript/audio/PHI; dashboard p50/p95, queue, GPU/model latency, ASR, citations, DB contention, job failure và cost. | Có SLO/alert, health/readiness, runbook, backup restore drill và rollback. OpenTelemetry chuẩn hóa traces, metrics, logs cho quan sát xuyên dịch vụ.  |
| Mạng/an toàn API | TLS, origin allowlist, authn/authz theo resource, object-level authorization, giới hạn body/audio theo route, quota/rate limit, timeout, SSRF allowlist cho tra cứu, secret manager và egress control. | Rà soát theo OWASP API Security (BOLA, resource consumption, misconfiguration, unsafe API consumption).  |

**Đích triển khai:** browser/CDN → API nghiệp vụ bền vững → PostgreSQL + object storage; API tạo job bền vững → worker Python CPU/GPU → artifact có version → API trả trạng thái để UI duyệt. Giai đoạn đầu có thể dùng PostgreSQL làm job table, chưa cần Kafka/Redis nếu tải chưa chứng minh nhu cầu.

### 4.2. Cấu trúc module và hợp đồng dữ liệu

- Tổ chức monorepo theo miền: `encounters`, `audio`, `transcript`, `claims`, `review`, `documents/templates`, `evidence/search`, `tasks`, `identity/access`, `audit`, `integrations/fhir`. Mỗi miền có schema, service, persistence adapter và handler; tránh import vòng và gọi DB trực tiếp từ UI.
- Chuẩn hóa entity có ID bất biến: `Encounter`, `AudioAsset`, `TranscriptVersion`, `Utterance`, `Claim`, `EvidenceLink`, `ReviewDecision`, `DocumentVersion`, `TemplateVersion`, `SourceRecord`, `ConsentRecord`, `Job`, `AuditEvent`. Không dùng tên hiển thị làm khóa.
- Giữ “sự thật gốc” và “đầu ra dẫn xuất” riêng: audio/transcript gốc bất biến; sửa transcript tạo version; mệnh đề liên kết span; ghi chú lưu input/model/prompt/schema version; quyết định bác sĩ là record độc lập, không ghi đè kết quả AI.
- Có contract JSON Schema/Pydantic/Zod dùng chung hoặc sinh client; validate ở ranh giới API; migration DB có version; tương thích ngược khi deploy frontend/API/worker lệch thời điểm.
- Tách provenance dataset/model khỏi provenance encounter. Trong FHIR R4, Provenance mô tả nguồn/tạo/sửa resource; AuditEvent ghi nhận hoạt động truy cập/thao tác theo sự kiện. 

### 4.3. Nâng cấp thuật toán theo từng lớp

**A. Audio → transcript**

- Repo đã có preprocessing/VAD, adapter ASR, diarization, alignment, so sánh hai bản ASR cho token trọng yếu và cờ `asr_review_required`. Giữ nguyên nguyên tắc không tự chọn transcript khi thuốc, số/liều, phủ định, thời gian hoặc chủ thể bất đồng.
- Bổ sung N-best theo span, giữ raw text song song chuẩn hóa từ thuốc, word timestamp khi provider có, audio quality và nguồn ASR/model. Đánh giá clinical token error, speaker attribution, timestamp overlap và precision/recall của cờ nghe lại; confidence chỉ xếp hàng review sau calibration.
- Tách `speaker_id` khỏi `speaker_role`; nếu diarization fallback/không chắc thì vai trò và chủ thể về chưa rõ, không suy từ lời nói. Cho bác sĩ nghe vùng sai khác theo timeline.

**B. Transcript → mệnh đề có cấu trúc**

- Chuẩn đầu ra typed claim: `subject`, `predicate/value`, polarity, temporality, modality, experiencer, dosage/unit, source span(s), confidence components, review status. Không làm phẳng thành văn xuôi trước khi kiểm chủ thể/phủ định/thời điểm.
- `src/do_trich.py` hiện dùng F1 từ vựng ngưỡng 0,6 và ghép tham lam một-một để chấm trích xuất. Giữ làm baseline; bổ sung chuẩn hóa bảo toàn đơn vị/phủ định và ghép toàn cục (bipartite matching) theo nhiều tín hiệu: exact/normalized, lexical overlap, entity/unit, time/polarity/subject. Embedding chỉ tạo ứng viên; không để điểm ngữ nghĩa tự quyết định mệnh đề y khoa.
- Sau extraction, chạy invariant: chủ thể phải có evidence; không đổi phủ định; dose/unit không tự điền; past/current/planned phân biệt; correction thay giá trị cũ nhưng giữ lịch sử; mâu thuẫn hiển thị song song cho bác sĩ.
- Đo precision/recall/F1 span và claim; exact match medication/dose/negation/subject; calibration theo lớp; ablation model-only/rule-only/hybrid. Không chọn threshold từ test khóa.

**C. Ưu tiên soát rủi ro**

- `src/rui_ro_quy_gan.py` chấm bốn tín hiệu với trọng số bằng nhau; tài liệu module ghi rõ chưa có nhãn tay để hiệu chuẩn. Dùng làm xếp hàng review, không gọi là xác suất. Hiệu chuẩn trọng số/ngưỡng trên dev bác sĩ gán nhãn; đối chứng random-review ở cùng tỷ lệ chuyển duyệt và phân tích subgroup.
- Đo đường đánh đổi số lỗi chủ thể/thuốc/phủ định còn sót tại từng tỷ lệ cảnh báo, false-positive burden và thời gian bác sĩ. Khi thiếu căn cứ, giữ cần xác nhận; không “tăng recall” bằng cách đánh dấu mọi thứ mà không đo workload.

**D. Tra cứu y khoa có dẫn nguồn**

- Pipeline: xác định intent/bối cảnh tối thiểu → Việt/Anh/synonym query expansion → lọc allowlist theo quốc gia/loại tài liệu/đối tượng/hiệu lực → hybrid retrieval (BM25 + vector) → rerank theo phù hợp/độ mới/thẩm quyền → trích đoạn có định vị → sinh từng câu hỏi/nhận định gắn evidence ID → kiểm claim-to-span và link → phát hiện xung đột/thiếu → abstain hoặc hỏi thêm.
- Citation gắn sát từng câu/ý, không chỉ ở cuối đoạn. Kiểm URL/title/tổ chức/ngày/jurisdiction/phiên bản và đoạn nguồn thực sự hỗ trợ claim; phân biệt “nguồn tìm thấy” với “nguồn đã dùng”. PubMed là chỉ mục nghiên cứu, không mặc định là guideline.
- Khởi đầu bằng registry metadata + lexical/hybrid retrieval nhỏ. Chỉ xây knowledge graph/GraphRAG khi benchmark chứng minh cần quan hệ nhiều thực thể hoặc timeline hồ sơ. Đo recall@k/nDCG riêng với factuality, entailment và citation correctness; bài SourceCheckup cho thấy URL hợp lệ vẫn có thể không hỗ trợ các claim trong câu trả lời. 
- Với NCBI E-utilities, thêm thông số `tool`/`email`, tôn trọng giới hạn request và cache; chỉ dùng API key nếu tốc độ truy vấn cần vượt giới hạn chính sách. 

**E. Chính sách chọn mô hình**

- Không mặc định tăng từ Qwen3-4B lên model lớn. Benchmark adapter hiện tại với baseline không adapter, model nhỏ/lớn và rules-only trên cùng split; đo lỗi nghiêm trọng, schema adherence, calibration, latency/VRAM/throughput và chi phí.
- **Quyết định ngày 21/11/2026:**
  - **Qwen3-4B + QLoRA vẫn là mô hình chính cho khâu trích xuất, như từ đầu** (mọi lần huấn luyện và chạy thật đều dùng 4B; không có thay đổi ở điểm này). Lý do giữ: Qwen3-8B chưa huấn luyện đạt F1 28,0 và ghi nhầm người 41,5% ở bộ đổi chủ thể, còn Qwen3-4B đã huấn luyện đạt F1 66,1 và 22,0% (`docs/final/Báo cáo dự án.md`); huấn luyện đóng góp nhiều hơn kích thước mô hình. Bản 4B vừa card RTX 3060 12 GB với giới hạn 90%.
  - **Qwen3-4B chưa huấn luyện** là đối chứng zero-shot (đề xuất, chờ xác nhận), cần khoảng 3 GB bộ nhớ card, đo được tỷ lệ bỏ sót.
  - **Qwen3-8B bỏ khỏi đường chính; bản tải dở trên HoaiĐức đã xoá** (4,18 GB, không dùng được). Chỉ giữ các kết quả 8B chưa huấn luyện đã có làm đối chứng. Hai kernel `kaggle-kernels/kernel-nen-8b-a` và `kernel-nen-8b-b` chưa gỡ vì là mã sinh ra kết quả đối chứng đó.
  - **Qwen2.5-1.5B-Instruct** giữ trên ổ C; vai trò chưa được ghi rõ, chờ xác nhận.
  - **qwen2.5:14b (Ollama)** không thuộc đề tài, không đưa vào phép đo; một ứng dụng khác trên máy tự nạp lại và chiếm 9,5 GB bộ nhớ card, cần tìm và cấu hình lại.
  - Thay đổi thật sự duy nhất: hằng số `MODEL_CHINH` trong `src/duong_dan.py` vẫn mặc định Qwen3-8B, lệch với thực tế chạy; cần sửa thành Qwen3-4B và ghi vào phần phương pháp (chưa làm).
- Chọn theo yêu cầu nội bộ/dữ liệu, độ ổn định JSON và hiệu quả review; model/prompt regression phải kiểm trên dev trước phát hành. Khi thiếu căn cứ, abstain/chuyển bác sĩ duyệt.

### 4.4. Thiết kế thuật toán thành các cổng kiểm tra có thể kiểm chứng

**Nguyên tắc thiết kế:** không gom mọi tín hiệu thành một điểm “độ tin cậy AI” khó diễn giải. Lưu riêng chất lượng âm thanh, bất đồng ASR, speaker/role, độ chắc từng trường, căn cứ nguồn, mâu thuẫn, mức độ nghiêm trọng và trạng thái bác sĩ duyệt. Bộ điều phối chỉ dùng các tín hiệu đã được đánh giá để chọn một trong ba hành động: đưa vào bản nháp, yêu cầu xác nhận, hoặc không đưa vào bản nháp và nêu rõ lý do.

1. **Giữ lại nhiều giả thuyết ở các điểm dễ sai:** với các đoạn có phủ định, số/liều/đơn vị, tên thuốc, người nói, sửa lời hoặc thời gian, lưu N-best/alternatives từ ASR nếu có; không ép hợp nhất khi các ứng viên bất đồng. Cho phép nghe lại đoạn gốc trước khi chấp nhận claim.
2. **Trích xuất claim có kiểu dữ liệu:** biểu diễn claim thành các trường subject/experiencer, predicate/value, polarity, time, modality, dose/unit, span nguồn, transcript version, model version và review state. Trường vắng mặt là `not_mentioned`; lời nói mơ hồ là `uncertain`; không ánh xạ hai trạng thái này thành phủ định.
3. **Xác minh hai tầng:** kiểm tra cấu trúc và invariant bằng luật xác định (đơn vị, phủ định, chủ thể, thời gian, sửa lời), sau đó kiểm mức hỗ trợ ngữ nghĩa giữa claim và span. Embedding hoặc LLM verifier chỉ được đề xuất/đánh dấu để con người xem; không tự quyết định tính đúng lâm sàng.
4. **Theo dõi sai số xuyên tầng:** tạo error ledger gắn lỗi chuẩn tham chiếu với từng tầng `audio → ASR → speaker/role → claim → note`. Báo riêng lỗi có từ transcript gốc, lỗi giới hạn bởi âm thanh/ASR, lỗi trích xuất và lỗi dựng ghi chú. Một claim có trích dẫn đúng transcript vẫn có thể sai nếu transcript đã sai; vì vậy provenance văn bản phải có đường trở lại audio ở những điểm trọng yếu.
5. **Chuyển duyệt theo ngân sách và rủi ro:** trên dev, hiệu chuẩn tín hiệu theo từng nhóm lỗi; dựng risk-coverage curve và so sánh random review, ngưỡng WER/ASR, self-confidence của LLM, bộ quy tắc hiện có và mô hình kết hợp ở cùng tỷ lệ chuyển duyệt. Mục tiêu là bắt được nhiều lỗi nghiêm trọng hơn trong cùng khối lượng review, không phải tối đa hóa một điểm trung bình.
6. **Đánh giá độc lập:** giữ challenge set theo template family, người nói/phiên thu và nguồn; thay đổi hoặc bổ sung mô hình phải chạy lại toàn bộ benchmark phiên bản đã khóa. Không dùng test cuối để chỉnh prompt, ngưỡng hoặc luật.

Đây là hướng nghiên cứu có thể kiểm chứng, không phải tuyên bố mới tuyệt đối: nghiên cứu 2026 đã khảo sát lỗi thông dịch lan sang ghi chú trong tình huống mô phỏng và nêu giới hạn mẫu nhỏ, chỉ chấm ghi chú cuối nên khó định vị lỗi ở transcript hay xử lý ngôn ngữ. Phần đề xuất cho MediTrace là thí nghiệm tiếng Việt có kiểm soát, giữ quan sát trung gian từng tầng và đo lỗi nặng/khối lượng bác sĩ duyệt. ([JMIR 2026](https://doi.org/10.2196/88734))

### 4.5. Mô hình dữ liệu và hợp đồng giữa dịch vụ

**Luồng dữ liệu tối thiểu:** `Encounter → AudioAsset → TranscriptVersion → Utterance/WordSpan → Claim → EvidenceLink → ReviewDecision → NoteVersion → Export`. Mỗi đối tượng dùng ID bất biến; bản đã duyệt tham chiếu chính xác phiên bản transcript, claim, mẫu và model/prompt/schema đã tạo ra nó.

- API nhận dữ liệu phải kiểm tra schema, quyền truy cập theo encounter, kích thước/type audio và idempotency. Mọi sửa đổi tạo phiên bản mới hoặc sự kiện audit; không ghi đè âm thầm transcript/ghi chú đã duyệt.
- Dùng PostgreSQL làm nguồn dữ liệu bền vững khi cần nhiều instance/ghi đồng thời; SQLite chỉ tiếp tục cho local/demo một tiến trình. Queue ban đầu có thể là bảng job với lease, retry có giới hạn và khóa chống chạy trùng; thiết kế outbox nếu cần bảo đảm thay đổi DB và phát job không lệch nhau. Chỉ thêm Redis/Kafka khi đo tải chứng minh cần.
- Tách metadata và file lớn: DB lưu quyền, hash, thời hạn, phiên bản và object key; audio/artifact nằm ở object storage riêng có mã hóa, retention/xóa và URL ngắn hạn. Không đặt PHI trong telemetry; chỉ ghi ID giả danh/trace ID, trạng thái, thời lượng và mã lỗi đã lọc.
- AuditEvent ghi nhận truy cập/thao tác; Provenance mô tả tác nhân/hoạt động/tài liệu đầu vào đã tạo nên phiên bản đầu ra. Đây là hai nhu cầu khác nhau trong FHIR, không nên dùng chung một bảng log tùy tiện. ([FHIR AuditEvent](https://hl7.org/fhir/auditevent.html), [FHIR Provenance](https://hl7.org/fhir/provenance.html))
- Chia code theo miền nghiệp vụ và hợp đồng API có phiên bản trước khi tách service. Worker Python nhận job theo hợp đồng đã kiểm tra, giới hạn CPU/GPU/thời gian, ghi trạng thái idempotent và trả artifact có phiên bản. Frontend không gọi DB trực tiếp và không dùng `localStorage` làm nguồn chuẩn cho hồ sơ.
- Bổ sung trace ID nối browser/API/job/worker/model/DB/provider, dashboard latency/error/queue/cost và kiểm tra khôi phục backup. OpenTelemetry chuẩn hóa traces, metrics và logs; telemetry không được chứa audio, transcript hoặc dữ liệu định danh. ([OpenTelemetry signals](https://opentelemetry.io/docs/concepts/signals/))

**Các lựa chọn nên hoãn:** microservices toàn hệ thống, event sourcing đầy đủ, knowledge graph/GraphRAG, vector database riêng, fine-tune model lớn và tự triển khai cụm GPU. Chỉ mở các nhánh này sau khi có benchmark, tải thực hoặc yêu cầu tích hợp cụ thể chứng minh giá trị; trước đó chúng tăng vận hành và bề mặt lỗi nhiều hơn lợi ích đo được.

### 4.6. Trục nghiên cứu ưu tiên và thí nghiệm đầu tiên

**Tên làm việc:** *Độ toàn vẹn bằng chứng khi lỗi đầu vào lan qua pipeline ghi chép lâm sàng tiếng Việt.* Đây là tên mô tả dự án, chưa phải tuyên bố tính mới. Nghiên cứu JMIR 2026 đã ghi nhận lỗi thông dịch trong encounter mô phỏng có thể đi vào ghi chú AI; SCRIBE cũng đề xuất đánh giá nhiều lớp. Khoảng trống hẹp hơn để kiểm tra là: đo riêng từng lớp trên tiếng Việt, đặc biệt phủ định, người được nói tới, sửa lời, thời gian và thuốc/liều/đơn vị; xác định lỗi nào được gate hiện tại cho qua và liệu cơ chế chuyển duyệt theo rủi ro có bắt được nhiều lỗi nặng hơn trong cùng thời gian bác sĩ.

**Câu hỏi nghiên cứu:** Ở cùng tỷ lệ chuyển ca sang duyệt, liệu kiểm tra kết hợp bất đồng ASR, kiểu claim và liên kết audio/span làm giảm tỷ lệ chấp nhận sai các lỗi nghiêm trọng so với chỉ dùng WER/độ tin cậy ASR, tự đánh giá của LLM, gate hiện tại hoặc chọn ngẫu nhiên?

**Thiết kế pilot khả thi:**

- Bắt đầu bằng một tập thí điểm nhỏ lấy từ các họ khuôn hiện có, chọn có chủ đích cho các loại lỗi chính; ghi rõ cỡ mẫu là thí điểm, không suy rộng thành đại diện lâm sàng. Sau đó mở rộng lên mục tiêu 300 khuôn theo các cổng dữ liệu ở Giai đoạn 1B.
- Tạo cặp đối chứng sạch/lỗi có kiểm soát: bỏ hoặc đảo phủ định; đổi người nói/chủ thể; sửa thời gian/thông tin trước đó; xáo trộn số/liều/đơn vị; bỏ câu hỏi khiến câu trả lời bị hiểu thành phủ định; thêm code-switch thuật ngữ. Giữ audio gốc, transcript chuẩn, transcript nhiễu và lineage riêng.
- Chia tập theo họ kịch bản, người viết/diễn viên, session thu và nguồn; không để paraphrase/counterfactual của cùng một ca lọt sang split khác. Bổ sung challenge set mới do người khác tạo sau khi đóng băng baseline.
- Hai người gán nhãn độc lập cho claim và mức nghiêm trọng; bất đồng được phân xử. Có bác sĩ cố vấn để duyệt định nghĩa/ca nặng; nếu chưa có xác nhận chuyên môn, gọi kết quả là benchmark kỹ thuật, không là bằng chứng an toàn lâm sàng.
- So sánh: không gate; ngưỡng ASR/WER; confidence tự báo của LLM; gate luật hiện tại; kết hợp typed claim + evidence/audio + ưu tiên review; random review ở cùng khối lượng. Thực hiện ablation từng thành phần.

**Kết quả cần báo cáo:** false acceptance của claim nghiêm trọng; độ chính xác exact cho chủ thể/phủ định/thời gian/thuốc-liều-đơn vị; omission rate; unsupported claim rate; recall lỗi nghiêm trọng tại các mức review burden cố định; tỷ lệ chuyển duyệt, cảnh báo sai và thời gian xem trung vị. WER/CER chỉ là chỉ số ASR phụ, không đại diện chất lượng ghi chú. Không gọi raw LLM confidence là xác suất đã hiệu chuẩn.

**Giả thuyết có thể bị bác bỏ:** claim có span trích dẫn vẫn có thể sai vì transcript/diễn giải đầu vào sai; gate kết hợp có thể giảm lỗi nghiêm trọng được chấp nhận ở cùng review burden, nhưng có thể tăng bỏ sót hoặc số cảnh báo. Nếu kết quả không cải thiện qua baseline hoặc không tái lập trên challenge set, không đưa gate thành mặc định; quay lại sửa dữ liệu/schema/luật.

## 5. Lộ trình triển khai

### Giai đoạn 0 — Đường cơ sở và bản đồ tính năng (1–2 tuần)

- Lập danh mục trạng thái: UI, API nối, unit/integration test, mô hình thật, minh họa.
- Chạy luồng mẫu và audio ở dev; ghi phiên bản, thời gian, nguồn kết quả, lỗi.
- Đóng băng baseline: commit, model, adapter, prompt, cấu hình và dữ liệu.
- Gắn nhãn/tắt nhật ký “8 chốt” và tờ dặn dò khi chưa có kết quả backend tương ứng.
- Kiểm kê API, lưu audio/transcript, quyền tài khoản và cờ gọi model ngoài.

**Hoàn tất khi:** có bảng tính năng/đường gọi/trạng thái/minh chứng/giới hạn; phân biệt mẫu, cache, model vừa chạy và kết quả có sẵn.

### Giai đoạn 1 — Đánh giá độc lập và taxonomy lỗi (2–4 tuần)

Taxonomy tối thiểu:

| Nhóm | Ví dụ | Mức gợi ý |
|---|---|---|
| Sai chủ thể | Dị ứng của mẹ ghi cho bệnh nhân | Nghiêm trọng |
| Sai thuốc/liều/đơn vị | 1 viên thành 2; mg thành ml | Nghiêm trọng |
| Đảo phủ định | “Không dị ứng” thành “dị ứng” | Nghiêm trọng |
| Mất đính chính | Giữ “một tuần” sau khi sửa thành “mười ngày” | Cao |
| Sai thời gian/tình thái | Dự định thành việc đã làm | Cao |
| Bỏ sót dữ kiện nói rõ | Bỏ dị ứng/dấu hiệu quan trọng | Cao/Trung bình |
| Bịa/khẳng định quá mức | Thêm triệu chứng không được nói | Nghiêm trọng |
| Sai transcript | ASR nhầm thuốc, số, người nói | Theo hậu quả |

Thiết kế dữ liệu:

- Nền hiện có là 200 khuôn bệnh theo test trong kho, thay cho mốc 100 khuôn trong README cũ. Kế hoạch mở rộng lên 300 khuôn/kịch bản duy nhất; trước khi công bố, xuất danh sách ID/tên khuôn và manifest của lần train/đánh giá cụ thể.
- Tách theo khuôn bệnh, kịch bản lỗi và nguồn tạo; không chia biến thể cùng khuôn sang train/test. Khóa tập kiểm tra cuối, không dùng nó để sinh dữ liệu hoặc chọn mô hình.
- Có tập phát triển, test kín và test ngoại khuôn tạo sau khi khóa baseline.
- Audio người thật chỉ theo quy trình đồng thuận/phê duyệt; trước đó dùng hội thoại mới do người khác soạn.
- Gắn nhãn kép lỗi trọng yếu; giải quyết bất đồng bởi thẩm định viên thứ ba; lưu định nghĩa và phiên bản.
- Kiểm tra trùng chính xác, chuẩn hóa, n-gram/embedding và cấu trúc sự kiện.

Đo bỏ sót/recall, cảnh báo nhầm/precision, nguồn đúng lượt/chủ thể/timestamp, sửa transcript/ghi chú và kết quả theo nguồn/kịch bản/giọng/ồn. Không gộp thành một điểm duy nhất.

**Hoàn tất khi:** tài liệu thống nhất mục tiêu 300 khuôn; có manifest train/dev/test gắn phiên bản, seed và model; có báo cáo rò rỉ, ca ngoại khuôn và confusion matrix theo taxonomy. Số mẫu từng tập lấy từ manifest thật, không suy ra từ số khuôn.


### Giai đoạn 1B — Mở rộng bộ dữ liệu huấn luyện (3–6 tuần, song song sau khi khóa test)

**Mục tiêu:** tăng danh mục từ 200 lên 300 khuôn/kịch bản thực sự khác nhau; mở rộng dataset có provenance theo từng đợt. 10.000–12.000 bản ghi QC là mục tiêu dài hạn để lập kế hoạch, không phải số hiện có, không phải tiêu chuẩn chung và không tự chứng minh chất lượng. Trước khi chốt mốc, xác minh dữ liệu/checkpoint hiện có; manifest phải báo riêng từng split, nguồn, loại dữ liệu và số bản ghi dùng thật trong từng lần train.

**Triển khai theo cổng thay vì nhân bản dữ liệu một lần:**

1. **Đợt A — audit/đóng baseline:** xuất inventory 200 khuôn, dữ liệu đã lưu, dữ liệu sinh trong test, checkpoint và split. Khóa test hiện tại trước chỉnh sửa; cập nhật README đang ghi 100 khuôn/5.000 ca theo bằng chứng kiểm kê. **Trạng thái 21/11/2026:** phần kiểm kê và khoá danh sách đã làm (manifest đóng băng 200 khuôn, 5.000 ca, xem mục 0); chưa làm: cập nhật README, sửa độ lặp câu (76,3%) và dữ liệu v2.
2. **Đợt B — 200 → 250 khuôn:** thêm 50 khuôn mới đã duyệt và khoảng 1.500–2.000 bản ghi mới đa nguồn, đa dạng thực sự (mục tiêu dự kiến, không cố đạt số bằng paraphrase). Dùng làm pilot taxonomy, chất lượng nhãn, cân bằng và chi phí duyệt.
3. **Đợt C — 250 → 300 khuôn:** chỉ thêm 50 khuôn kế tiếp và tăng dần về 10.000–12.000 bản ghi QC nếu pilot cải thiện dev/challenge mà không tăng lỗi nghiêm trọng hay làm suy giảm nhóm yếu thế. Nếu không đạt, sửa schema/split/nhãn trước khi sinh tiếp.

“Khuôn” là họ kịch bản có cấu trúc thông tin và bẫy lỗi khác nhau; đổi tên, triệu chứng bề mặt, đại từ hoặc thứ tự câu không được tính là khuôn mới. Chỉ tính bản ghi có ID ổn định, nhãn và lineage đầy đủ vào số mẫu QC.

**Nhóm dữ liệu cần mở rộng**

- **Bộ lõi:** rà soát 200 khuôn hiện có; bổ sung theo hai đợt 50+50 khuôn để đạt 300 sau khi qua cổng pilot. Khuôn mới phải mở rộng chuyên khoa, tuổi, giới, diễn tiến, số người nói và loại thông tin lâm sàng, không chỉ đổi tên/đổi từ.
- **Ca ngoài khuôn:** tạo tình huống mới từ quy trình khám khác, cách hỏi khác và quan hệ thông tin khác; ưu tiên người viết không tham gia xây bộ sinh hiện tại.
- **Ca đối kháng:** sai chủ thể, người nhà kể bệnh, lời đính chính, mâu thuẫn theo thời gian, câu hỏi chưa trả lời, phủ định, dự định có điều kiện, thuốc/liều/đơn vị và nhiều người nói.
- **Biến thể ngôn ngữ:** phương ngữ Bắc–Trung–Nam, đại từ vùng miền, lược chủ ngữ, ngập ngừng, nói chồng, sửa giữa câu, pha thuật ngữ Anh–Việt.
- **Đa bệnh lý/bối cảnh:** chỉ thêm khi đáp án mô tả rõ bệnh, thuốc, chủ thể và thời điểm; tránh ghép bệnh cơ học khiến hội thoại thiếu tự nhiên.
- **Audio có transcript chuẩn:** tập riêng do người nghe/hiệu đính; lưu nguồn, điều kiện thu, chất lượng, quyền sử dụng và người gán nhãn.
- **Phương ngữ và code-switch:** thêm thiết kế có kiểm soát cho thuật ngữ thuốc/thủ thuật tiếng Anh xen trong tiếng Việt, tên thuốc gần âm, số và đơn vị. Dùng VietMed/VietMedCSS và VietMed-NER để định vị benchmark, lỗi thường gặp và baseline; không mặc định được phép sao chép/tái phân phối dữ liệu hoặc mô hình, cần kiểm tra điều khoản và phạm vi license trước khi dùng.
- **Ca do bác sĩ viết hoặc hiệu đính:** dùng làm đánh giá chuyên gia; chỉ nhập vào train khi đã có quyết định rõ và không thuộc tập test đã khóa.

**Thiết kế thành phần dữ liệu và nhãn**

- Dùng nhiều nguồn có lineage: ca tổng hợp do bác sĩ/biên tập viên lâm sàng viết hoặc duyệt; hội thoại mới do người độc lập soạn; audio thu riêng có đồng thuận và transcript chuẩn; ca thực tế chỉ khi có căn cứ pháp lý, phê duyệt, giảm thiểu dữ liệu và quy trình gỡ định danh phù hợp. Không lấy nội dung PubMed/web công khai làm dữ liệu train chỉ vì truy cập được; phải kiểm tra license, quyền tái sử dụng và mục đích.
- Phân tầng theo nhu cầu thực tế thay vì chia đều 300 khuôn: chuyên khoa, tuổi/nhóm đặc biệt, phương ngữ, số người nói, thời lượng, modality, độ khó, lỗi nghiêm trọng, nguồn và mức xác nhận của chuyên gia. Báo rõ ô thiếu dữ liệu; không tạo số cân bằng giả.
- Gán nhãn nhiều tầng: transcript/span; speaker/chủ thể; mệnh đề; khẳng định/phủ định/chưa rõ; thời điểm và tình thái; thuốc/liều/đơn vị; mức nghiêm trọng; nguồn bằng chứng; quyết định giữ/sửa/bỏ của bác sĩ. Có hướng dẫn gán nhãn, double-label cho nhóm trọng yếu, adjudication và agreement.
- Tạo cặp đối chứng tối thiểu cho lỗi an toàn (đổi người dị ứng, phủ định, liều/đơn vị, quá khứ so với dự định, người nhà so với bệnh nhân, tự sửa). Cặp giúp đo độ nhạy đúng điểm thay đổi; không để hai vế lọt sang hai split.
- Phân bổ số biến thể theo độ khó và khoảng trống lỗi quan sát được; đặt min/max mỗi họ kịch bản để tránh mẫu phổ biến lấn át. Trung bình 10–12 nghìn chia cho 300 khuôn chỉ là phép tính quy mô, không phải quota; manifest mới là con số chuẩn.
- Ưu tiên cải thiện dữ liệu/nhãn/split trước khi tăng kích thước model. So sánh base, adapter và các ablation trên cùng dev; chọn checkpoint bằng dev, đánh giá test khóa một lần theo protocol.

**Bảo vệ test cuối**

- Đóng băng danh sách khuôn, ca, đáp án và mã băm trước khi sinh thêm dữ liệu huấn luyện.
- Không dùng biến thể gần của test cuối làm train. Nếu ca test được dùng để sửa luật, prompt hoặc mô hình, ghi nhận đã tiêu thụ và thay test mới trước khi tuyên bố kết quả độc lập.
- Tách rõ train để học, dev để chọn phiên bản, test kín để báo cáo; challenge set mới do người khác soạn và giữ kín. Dùng nhiều trục test độc lập: khuôn/kịch bản ngoài train; nguồn/cơ sở khác; người nói/phiên thu âm khác; hội thoại thật được duyệt tiến cứu nếu được phép. Báo cáo từng trục riêng, không gộp thành một điểm.
- Không tự động chuyển ca khó từ test sang train rồi tiếp tục báo cáo trên chính test đó.

**Manifest và công khai cách tạo**

Mỗi mẫu nên có: case_id, template_id, scenario_id, source_type/source_id, generator_version, seed, ngày tạo, split/lý do chọn split, nhãn lỗi/kỹ năng, người tạo/duyệt, phiên bản đáp án, quan hệ biến thể, phương ngữ, speaker/session ID giả danh, modality, quyền sử dụng và trạng thái kiểm tra trùng. Bản công khai nêu số khuôn/ca từng tập, cách chia/sinh biến thể, nguồn, quy trình rà soát, bộ bị loại, tiêu chí trùng, license và giới hạn dữ liệu tổng hợp; chỉ công bố tổng hợp đã rà soát disclosure risk.

**Cổng kiểm soát trước khi nhập train**

- Kiểm schema, ID, nhãn, lượt thoại, trích dẫn nguyên văn và đáp án không thêm thông tin ngoài hội thoại.
- Kiểm trùng chính xác, chuẩn hóa, n-gram/embedding và đồ thị sự kiện lâm sàng (chủ thể–mệnh đề–thời điểm–trạng thái); gom near-duplicate để người duyệt phân xử. Đối chiếu chéo dev/test trước và sau chuẩn hóa.
- Duyệt thủ công mẫu theo nhóm nguồn/lỗi; nhóm nghiêm trọng phải có ca âm, ca dương và trường hợp dễ nhầm.
- Theo dõi phân bố theo chuyên khoa, độ dài, số người nói, thuốc/liều, phủ định, đính chính và độ khó.
- Chạy baseline trước/sau trên cùng dev và test đã khóa; lưu cả kết quả cải thiện và suy giảm.

**Vòng lặp mở rộng:** chạy trên dev/challenge → gom lỗi theo taxonomy và bước phát sinh → viết mẫu mới cùng phản ví dụ → duyệt → đưa đúng split → đánh giá lại → phát hành dataset version và changelog. Không dùng điểm test cuối để lặp tinh chỉnh.

**Tiêu chí theo đợt:** Đợt B có 250 khuôn được duyệt, manifest bất biến, báo cáo trùng/rò rỉ và so sánh baseline trên dev/challenge. Đợt C mới được chấp nhận khi đạt 300 khuôn và tiến dần tới 10.000–12.000 bản ghi QC theo manifest. Mọi số liệu tách theo split/khuôn/kịch bản/nguồn/modality; dataset có provenance, không rò rỉ test khóa; báo cáo nhóm lỗi cải thiện, không đổi hoặc suy giảm. Số bản ghi không phải tiêu chí nghiệm thu duy nhất.

### Giai đoạn 2 — Provenance và nghe lại đúng đoạn (2–4 tuần)

- Chuẩn hóa ID cho phiên audio, đoạn, lượt nói, mệnh đề, nguồn và phiên bản.
- Bảo toàn timestamp, speaker/role, ASR provider/model, confidence nếu có, người và thời điểm sửa.
- Bấm mệnh đề mở lượt nguồn; phát audio từ start_time đến end_time rồi tự dừng.
- Mệnh đề có nhiều nguồn thì hiện từng nguồn; thiếu timestamp thì báo rõ.
- Lưu audio theo session có phân quyền; thay audioUrl tạm bằng endpoint tham chiếu hoặc báo audio không còn.
- Giữ transcript gốc và bản sửa có liên kết.

**Hoàn tất khi:** demo hai người nói, câu đính chính, nhiều nguồn và tải lại trang; phát đúng đoạn hoặc giải thích vì sao không phát được.

### Giai đoạn 2B — AI hỗ trợ tra cứu y khoa có dẫn nguồn (3–5 tuần)

**Trải nghiệm trình bày theo ảnh tham chiếu**

- Khung bên cạnh hồ sơ có tiêu đề phiên khám/tóm tắt lượt khám, nút tạo cuộc tra cứu mới, thu gọn/mở rộng và chọn phạm vi dữ kiện được dùng. Không mang dữ kiện từ bệnh nhân/phiên khác sang.
- Sau khi bác sĩ chọn vấn đề hoặc đặt câu hỏi, hiển thị trạng thái tìm kiếm và số nguồn đã tìm thấy; tách rõ “nguồn đã tìm” với “nguồn thực sự được trích dẫn”. Không lấy số lượng nguồn làm bằng chứng về chất lượng.
- Trình bày câu hỏi gợi ý theo nhóm phù hợp với bệnh cảnh: đặc điểm triệu chứng, phơi nhiễm/dịch tễ, mức độ nặng/dấu hiệu cảnh báo, yếu tố nguy cơ, ảnh hưởng chức năng. Có thể bật/tắt từng nhóm.
- Mỗi câu hỏi/ý lâm sàng gắn nhãn nguồn ngay cạnh nội dung. Mở nhãn để xem tên tài liệu, tổ chức, loại nguồn, ngày xuất bản/cập nhật, đoạn trích, URL và phần/trang liên quan.
- Hộp “Điểm an toàn cần lưu ý” tách riêng dấu hiệu cấp cứu/tái đánh giá; nêu nguồn, không suy diễn mức khẩn cấp ngoài quy tắc được duyệt.
- Cuối kết quả có danh sách tài liệu tham khảo dạng thu gọn, số nguồn đã trích dẫn, thao tác mở nguồn, kiểm tra nguồn khác, sao chép/chia sẻ nội bộ và phản hồi hữu ích/không hữu ích.
- Ô hỏi tiếp giữ đúng bệnh cảnh đang mở, cho phép thêm dữ kiện hoặc yêu cầu tìm lại. Có thể thêm giọng nói, đính kèm dữ liệu được phép và xóa ngữ cảnh trước khi tạo cuộc mới.
- Chỉ hiển thị phần giải thích ngắn về cách tìm/chọn nguồn và giới hạn; không hiển thị chuỗi suy luận nội bộ. Luôn có chú thích: hỗ trợ tra cứu, không thay quyết định chuyên môn.

**Cách vận hành AI tìm kiếm**

1. Chuẩn hóa câu hỏi và ngữ cảnh tối thiểu: vấn đề, tuổi/nhóm đặc biệt nếu có, địa bàn áp dụng, thời gian và chuyên khoa; hỏi lại nếu thiếu thông tin làm thay đổi ý nghĩa.
2. Tạo truy vấn tiếng Việt và thuật ngữ tiếng Anh/synonym; tách câu hỏi thành các mục cần tra cứu và phát hiện dấu hiệu cảnh báo bằng quy tắc đã được duyệt.
3. Tìm trong danh mục nguồn được quản trị; ưu tiên hướng dẫn hiện hành của Việt Nam cho thực hành trong nước, sau đó đối chiếu hướng dẫn quốc tế phù hợp. Không đồng nhất dữ liệu quảng bá, tin phổ thông, nghiên cứu đơn lẻ và hướng dẫn điều trị.
4. Lọc theo đối tượng, bối cảnh, ngày cập nhật, trạng thái còn hiệu lực, thẩm quyền và loại tài liệu; xếp hạng theo mức phù hợp chứ không chỉ độ tương đồng từ khóa.
5. Trích đoạn có định vị; tạo câu hỏi gợi ý/tóm tắt chỉ từ nội dung truy hồi. Mỗi khẳng định có liên quan phải trỏ được tới đoạn nguồn; nếu nguồn xung đột hoặc không đủ thì nêu rõ và không tự hợp nhất thành kết luận.
6. Kiểm tra sau sinh: URL mở được, trích dẫn thực sự hỗ trợ câu cạnh nó, không gán hướng dẫn cho nghiên cứu, ngày cập nhật còn hợp lý và không có chỉ định/chẩn đoán tự tạo.
7. Ghi truy vấn, phiên bản chỉ mục/mô hình, nguồn được lấy và nguồn được dùng; không ghi PHI thừa vào log. Có kiểm soát truy cập, chống prompt injection từ trang web và kiểm tra quyền sử dụng.

**Danh mục nguồn đề xuất:** xem mục 12; khởi động bằng danh sách cho phép nhỏ, phân nhóm theo thẩm quyền/chủ đề/ngôn ngữ. Nguồn bệnh viện dùng cho quy trình tại cơ sở và tài liệu người bệnh; không thay thế hướng dẫn quốc gia. PubMed là công cụ tìm tài liệu nghiên cứu, không phải cơ quan ban hành khuyến cáo. Tài liệu quốc tế phải ghi rõ quốc gia/phạm vi áp dụng và không ghi đè hướng dẫn Việt Nam mà không cảnh báo.

**Nghiệm thu:** truy xuất được từ mỗi gợi ý tới URL/đoạn nguồn; thử các ca không có nguồn, nguồn cũ, hướng dẫn xung đột và red flags; bác sĩ đánh giá độ đúng của trích dẫn, tính hữu ích của câu hỏi, bỏ sót câu hỏi an toàn, độ mới và thời gian phản hồi. Không công bố như công cụ chẩn đoán tự động.

### Giai đoạn 3 — Giảm bỏ sót có kiểm soát (3–5 tuần)

- Thông tin chưa chắc chuyển sang “cần xác nhận”; không âm thầm loại hoặc tự điền.
- Tách “được nói rõ”, “không được nói đến”, “được phủ định rõ”.
- Cảnh báo có lý do, trích đoạn, bước phát sinh và mức ưu tiên; bác sĩ giữ/sửa/bỏ.
- Checklist mẫu chỉ báo thiếu đề cập, không tự lấp.
- Đánh giá từng luật; không nhận điểm tổng tốt hơn nếu lỗi nghiêm trọng tăng.
- Đặt ngưỡng nội bộ cho nhóm lỗi trọng yếu cùng bác sĩ cố vấn.

**Hoàn tất khi:** lỗi trọng yếu có mục tiêu recall, giới hạn cảnh báo nhầm và ca hồi quy; thiếu căn cứ không được chuyển thành nội dung chắc chắn.

### Giai đoạn 4 — Giao diện duyệt và phiên bản (2–4 tuần)

- Hàng đợi ưu tiên thuốc/liều, dị ứng, phủ định, chủ thể, đính chính, hành động chưa hoàn tất.
- So transcript gốc/đã sửa, bản nháp AI và bản bác sĩ chốt.
- Lịch sử phiên bản: ai sửa, lúc nào, trường nào và quyết định gì.
- Nếu nguồn hoặc bản nháp đổi, trạng thái duyệt cũ chuyển “cần duyệt lại”.
- Checklist chuyên khoa cấu hình được; mục vắng mặt ghi “chưa đề cập”.
- Chỉ thao tác hàng loạt cho nội dung không rủi ro.

**Hoàn tất khi:** bác sĩ thấy mục cần xem, truy nguồn và nhận biết phiên bản đã xác nhận.

### Giai đoạn 5 — ASR và người nói (3–6 tuần)

- Tạo audio ground truth với giọng vùng miền, tốc độ, chồng tiếng, tiếng ồn, thuốc, số, đơn vị, phủ định.
- Đo WER/CER và clinical token error rate.
- Đo diarization riêng; vai lâm sàng vẫn cần người dùng xác nhận khi cần.
- Confidence là tín hiệu nghe lại; xác minh calibration trước khi dùng ngưỡng.
- So sánh provider trên cùng test, đo độ trễ, VRAM, lỗi và luồng dữ liệu.
- Thêm câu đổi chủ thể như “bố em”, “con tôi”, lời gián tiếp và lược chủ ngữ.
- Có đường sửa transcript thủ công.

**Hoàn tất khi:** báo cáo cấu hình/dữ liệu/điều kiện/lỗi và có fallback rõ.

**Trạng thái 21/11/2026:** đã có kết quả LoRA và beam trên VietMed/ViMedCSS và báo cáo rò rỉ (xem mục 0). Bản bàn giao không nhắc đến các việc sau, nên chưa xác nhận được là đã làm: đo lỗi từ y khoa, đo tách người nói riêng, sửa transcript thủ công, so provider trên cùng tập kiểm tra.

### Giai đoạn 6 — Thư viện tạo tài liệu và hoàn thiện module mở rộng (4–8 tuần)

**Thư viện tạo tài liệu theo ý tưởng tham chiếu Heidi**

- Một ô tìm kiếm “Tìm hoặc tạo tài liệu” nhận tên mẫu hoặc yêu cầu tự nhiên; đề xuất thao tác phù hợp với phiên khám đang mở.
- Bộ lọc/sắp xếp theo loại tài liệu, chuyên khoa, người tạo, mức quyền truy cập và gần đây/yêu thích. Có thể ẩn mẫu ngoài quyền/gói nếu MediTrace triển khai phân tầng gói.
- Chia thư viện thành “Dành cho phiên này” (tác vụ tạo theo dữ liệu phiên đang mở) và “Mẫu của MediTrace / Mẫu của tôi / Mẫu của cơ sở”; luôn phân biệt tác vụ sinh tạm với mẫu đã lưu.
- Tác vụ nhanh ban đầu: ghi chú tiến triển; SOAP; H&P kèm vấn đề; đánh giá và kế hoạch; tóm tắt buổi khám; thư giải thích cho người bệnh; giấy dặn dò sau khám; tóm tắt/chuyển tuyến; biên bản họp nhóm chăm sóc liên chuyên khoa. Mẫu hành chính như biên bản điều hành để ngoài luồng bệnh án và chỉ triển khai khi có phân quyền, kiểm soát PHI.
- Cho tạo, sửa, sao chép và xem trước mẫu; lưu mẫu cá nhân/cơ sở, đặt mặc định theo bác sĩ hoặc chuyên khoa, quản lý phiên bản và quay lại mẫu trước.
- Mọi trường được sinh phải truy được về transcript/hồ sơ nguồn, đánh dấu chưa có căn cứ khi thiếu, và vào bản nháp chờ bác sĩ duyệt. Không tự xác nhận chẩn đoán, kê đơn hay hoàn tất hồ sơ. “Tạo đánh giá cúm/COVID” chỉ là cấu trúc tài liệu từ dữ kiện có sẵn, không tự kết luận bệnh.
- Có trạng thái sử dụng/gói hoặc hạn mức thao tác nếu sản phẩm cần; không để thông báo quota ảnh hưởng quy trình cấp cứu hay lưu bản nháp.

**Hiện trạng và phần cần xây:** `TemplatesView` hiện có tìm kiếm theo tiêu đề, mẫu mặc định và thao tác tạo mẫu giữ trong state React; chưa thấy lưu bền, lọc/sắp xếp theo loại/người tạo, đặt mẫu mặc định, chia “phiên này” với thư viện chuẩn, hoặc quản lý phiên bản/quyền ở màn hình này. Cần nối API/kho dữ liệu, quyền cá nhân-cơ sở, audit log và pipeline nguồn → bản nháp → duyệt.

**Nghiệm thu:** mẫu mới còn sau khi tải lại và đăng nhập lại; lọc/tìm trả đúng kết quả; đặt mặc định đúng phạm vi; nội dung sinh chỉ lấy từ phiên được chọn, có nguồn và trạng thái thiếu; bác sĩ sửa/duyệt trước khi ký, in hoặc xuất.

1. **Mẫu chuyên khoa:** lưu theo tài khoản/đơn vị; phân biệt trường bắt buộc, tùy chọn, chưa đề cập; thử một chuyên khoa.
2. **Tờ dặn dò:** lấy từ bản bác sĩ duyệt; mặc định trắng khi thiếu; bỏ dữ liệu mẫu; bác sĩ xác nhận trước in.
3. **FHIR:** validate exporter; bắt đầu DocumentReference, Provenance và tài liệu nháp/đã duyệt; sandbox trước khi tuyên bố tích hợp.
4. **Nhật ký xử lý:** event backend thật; trạng thái “đã chạy/bỏ qua/thất bại/minh họa”; model/version/config và người duyệt, tránh ghi PHI thừa.
5. **Dược lý/thang điểm/CDSS:** giữ prototype cho tới khi bác sĩ/dược sĩ thẩm định nguồn, phạm vi, phiên bản hướng dẫn và quy trình cảnh báo.
6. **Tóm tắt trước khám:** chỉ khi có hồ sơ, phân quyền, thời điểm và dẫn nguồn riêng.

### Giai đoạn 7 — Bảo mật, vận hành và pilot

- Lập data-flow map audio/transcript/ghi chú/log/provider; nơi lưu, thời hạn, xóa và sao lưu.
- Kiểm tra quyền tài khoản/đơn vị, phiên đăng nhập, endpoint audio và đồng bộ localStorage/SQLite.
- Hiển thị dữ liệu nào đi ra ngoài; cấu hình mặc định an toàn phù hợp triển khai.
- Hạn chế PHI trong log; mã hóa lưu/truyền theo môi trường.
- Bắt đầu bằng ca giả lập; ca người bệnh cần quy trình đồng thuận/phê duyệt phù hợp.
- Có thể quay lui model/rule/prompt/schema sau phát hành.

**Bổ sung vào Giai đoạn 0/7 — kiểm soát nền tảng trước pilot:** rà soát origin/CORS, giới hạn request và rate limit theo endpoint, đồng bộ nhiều tab/thiết bị, vị trí DB trong deployment, log có PHI, quyền xuất/xóa; kiểm kê artifact huấn luyện ngoài repo; giữ audio service ở localhost tới khi có auth/TLS/quota/phân quyền; có retention/delete và backup-restore drill. Rà soát pháp lý theo Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 và Nghị định 356/2025/NĐ-CP (hiệu lực 01/01/2026) là đầu vào cho chuyên gia, không phải tuyên bố MediTrace đã tuân thủ.

## 6. Tính năng mới và ưu tiên

| Tính năng | Giá trị | Ưu tiên | Điều kiện |
|---|---|---:|---|
| Phát audio theo mệnh đề | Xác minh nguồn nhanh | P0 | Provenance xuyên pipeline |
| Hàng đợi cần xác nhận | Tập trung lỗi rủi ro | P0 | Taxonomy/lý do cảnh báo |
| Trạng thái chưa hỏi/chưa đề cập | Không biến thiếu thành phủ định | P0 | Schema trạng thái tách riêng |
| Phiên bản và lịch sử sửa | Truy dấu và phục hồi | P1 | ID ổn định/audit schema |
| AI hỗ trợ tìm kiếm y khoa | Câu hỏi gợi ý theo chủ đề, nguồn cạnh từng ý, điểm an toàn, hỏi tiếp | P1 | Danh mục allowlist, dẫn nguồn chính xác, kiểm duyệt lâm sàng, ghi rõ phạm vi quốc gia |
| Thư viện mẫu và tạo tài liệu | Tìm/gọi nhanh mẫu theo phiên khám, chuyên khoa và người tạo | P1 | Lưu bền, phân quyền, provenance, bác sĩ duyệt |
| Kiểm tra nhất quán xuyên bước | So transcript, mệnh đề, bản nháp, duyệt | P1 | Provenance thống nhất |
| Tờ dặn dò | Hỗ trợ sau khám | P2 | Chỉ từ nội dung đã duyệt |
| FHIR | Chuẩn bị trao đổi tài liệu | P2 | Validator và hệ thống đích |
| Đa ngôn ngữ | Mở rộng tình huống | P3 | Baseline tiếng Việt đạt |
| Tóm tắt trước khám | Chuẩn bị buổi khám | P3 | Hồ sơ phân quyền, dẫn nguồn |

### 6.1. Brainstorm tính năng bổ sung theo giá trị và rủi ro

| Gói tính năng | Hướng triển khai | Ưu tiên/gate |
|---|---|---|
| **Command palette “Tìm hoặc tạo”** | Tìm mẫu, tài liệu, thao tác và câu lệnh trong một ô; lọc theo loại/chuyên khoa/người tạo; phân nhóm “phiên này”, “của tôi”, “cơ sở”, “MediTrace”; mở nhanh nhưng luôn preview trước khi áp dụng. | P1 sau khi kho template có phân quyền và lưu bền vững. |
| **Tóm tắt lần khám và diễn tiến** | Timeline các lần khám với nguồn/phiên bản; so sánh thay đổi triệu chứng, thuốc, dị ứng và kế hoạch; chỉ lấy dữ liệu bệnh án được cấp quyền, nêu ngày nguồn và cảnh báo thiếu dữ liệu. | P2; cần patient identity matching, phân quyền và provenance ổn định. |
| **Bản giải thích cho người bệnh** | Tạo bản ngôn ngữ dễ hiểu, hướng dẫn đã được bác sĩ duyệt, dấu hiệu cần liên hệ lại và câu hỏi còn chưa giải quyết; không tự thêm liều dùng hay lời khuyên ngoài hồ sơ. | P2; dựa trên tài liệu đã duyệt, bác sĩ xác nhận trước khi in/gửi. |
| **Theo dõi việc cần làm sau khám** | Nhắc việc xét nghiệm/tái khám/chuyển tuyến, người phụ trách, hạn, trạng thái hoàn thành và lý do bỏ qua; tạo task từ kế hoạch đã xác nhận, không tự phát lệnh chăm sóc. | P2; cần nối TasksView với backend và audit. |
| **Hòa giải thuốc/dị ứng** | So danh sách trong hồ sơ với phát ngôn và tài liệu nguồn; phân biệt đang dùng/ngừng/dự kiến/không rõ; phát hiện mâu thuẫn để người duyệt xác nhận, không tự ghi đè. | P1/P2; chỉ bật khi có nhãn và test lỗi thuốc/chủ thể. |
| **Bộ kiểm tra chất lượng trước ký** | Checklist có thể cấu hình theo chuyên khoa: chủ thể, dị ứng, thuốc/liều, phủ định, thời gian, kế hoạch, trường chưa đề cập, nguồn và trạng thái duyệt. | P1; không ép hoàn tất trường không có căn cứ; không chặn cấp cứu. |
| **Phản hồi có cấu trúc và vòng học** | Cho bác sĩ đánh dấu lỗi loại nào, sửa gì, mức nghiêm trọng và nguyên nhân; phân tích xu hướng theo model/prompt/source; chỉ đưa vào train sau duyệt và kiểm tra quyền. | P1; không tự huấn luyện từ hồ sơ lâm sàng đang dùng. |
| **Kiểm soát phiên làm việc** | Tạm dừng/tiếp tục ghi âm, mute, hiển thị trạng thái ghi, xóa audio, khóa màn hình và xác nhận đúng phiên/người bệnh trước khi tạo ghi chú. | P0/P1 tùy bối cảnh triển khai; cần kiểm thử nhầm phiên và quyền audio. |
| **Tra cứu tích hợp vào tài liệu** | Từ một câu hỏi hoặc mục thiếu, mở kết quả nguồn ở panel; thêm trích dẫn vào vùng tham khảo của bản nháp; citation không được hiểu là bằng chứng câu ghi trong bệnh án đã được nói ra. | P1; tách nguồn hội thoại khỏi nguồn tri thức y khoa. |

### 6.2. Đích kiến trúc dữ liệu để tránh mở rộng chắp vá

- Định danh ổn định và tách miền: tài khoản/cơ sở, người bệnh, encounter, audio asset, transcript version, claim/evidence link, review decision, document/template, source record, consent và audit event.
- Mọi thao tác sửa là phiên bản mới hoặc event có tác giả/thời điểm; không cập nhật âm thầm. API dùng version/ETag hoặc cơ chế tương đương để phát hiện xung đột đồng bộ.
- Mã hóa dữ liệu nhạy cảm khi lưu và truyền; quản lý khóa/secret ngoài mã nguồn; quyền tối thiểu theo cơ sở-vai trò-encounter; audit truy cập và xuất/xóa; quy trình backup và khôi phục có kiểm chứng.
- Giữ ranh giới giữa (a) nội dung được nói trong encounter, (b) thông tin nhập từ chart, (c) tri thức từ nguồn ngoài và (d) nội dung AI suy ra. Chúng có thể cùng hỗ trợ soạn thảo nhưng không được gộp nguồn.
- FHIR là adapter trao đổi theo profile được chọn, không phải bản thân CSDL hay chứng nhận tích hợp. Lưu Provenance cho nguồn gốc/tạo/sửa; AuditEvent cho truy cập/thao tác khi profile và hệ thống đích yêu cầu.

## 7. Chỉ số và cổng phát hành

Không chọn ngưỡng số trước khi đo baseline. Xác lập cùng bác sĩ rồi khóa trước test kín.

| Nhóm | Đo lường |
|---|---|
| An toàn | Recall/bỏ sót theo lỗi; bịa; sai thuốc/liều/phủ định/chủ thể |
| Nguồn | Trích dẫn đúng lượt; timestamp đúng; provenance đầy đủ |
| Tra cứu AI | Tỷ lệ ý có trích dẫn hỗ trợ; độ đúng citation; độ phủ nguồn liên quan; độ mới; tỷ lệ từ chối khi không có căn cứ; đánh giá hữu ích của bác sĩ |
| Dữ liệu/train | Exact/near duplicate theo split; đồng thuận người gán nhãn; tỷ lệ mẫu bị loại; kết quả theo template/source/speaker/modality; hash toàn bộ dataset; leakage audit |
| Duyệt | Thời gian đến bản chốt; số sửa; cảnh báo xác nhận/bỏ qua |
| Audio | WER/CER và lỗi token lâm sàng; speaker error; tỷ lệ sửa transcript |
| Vận hành | Luồng hoàn thành; lỗi API; thời gian; khôi phục ca/audio; xung đột đồng bộ; độ trễ/lỗi nguồn tra cứu |
| Bảo mật | Quyền truy cập; data flow; đồng ý/provider ngoài; xóa/retention; mã hóa; backup/restore; sự cố; endpoint bị lạm dụng |

Không phát hành nếu lỗi nặng chưa có cách kiểm soát, test bị rò rỉ, demo bị hiểu là kết quả ca thật, hoặc bỏ sót nặng tăng vượt ngưỡng thống nhất. Pilot cần protocol, người giám sát lâm sàng, tiêu chí dừng, xử lý sự cố và ghi nhận phiên bản model/prompt/dataset; kết quả pilot không tự khái quát thành bằng chứng hiệu quả ở cơ sở khác.

## 8. Phân công và phụ thuộc

| Nhóm việc | Chủ trì gợi ý | Phụ thuộc |
|---|---|---|
| Bản đồ tính năng/telemetry | Backend + frontend | Giai đoạn 0 |
| Dataset/taxonomy/đánh giá | ML/data + bác sĩ | Quy trình dữ liệu |
| Provenance/phát lại | Backend audio + frontend | Schema ID |
| Kiểm căn cứ/giảm bỏ sót | Rules/ML + reviewer | Taxonomy/test kín |
| UX duyệt/phiên bản | Product/frontend + bác sĩ | Provenance |
| FHIR/tích hợp | Backend + đối tác | Hệ thống đích |
| Bảo mật/pilot | DevOps/security + chủ dữ liệu | Data-flow map |

## 9. Kế hoạch 30 ngày đầu

Trong 30 ngày đầu, đầu ra dữ liệu là inventory, split policy, test khóa và thiết kế pilot 200→250 khuôn; không đặt KPI phải hoàn tất 300 khuôn hay 10.000–12.000 mẫu trong tháng đầu. Chỉ lên đợt C khi kết quả dev/challenge và chất lượng gán nhãn đạt cổng đã thống nhất.

- **Tuần 1:** khóa baseline, lập ma trận tính năng, chạy luồng audio và mẫu trên dev, gắn nhãn demo.
- **Tuần 2:** chốt taxonomy và manifest; xác minh mốc 200 khuôn hiện tại, lập danh sách bổ sung 100 khuôn để đạt mục tiêu 300; tách test theo khuôn/kịch bản/nguồn, lập báo cáo trùng lặp và khóa test ngoài khuôn.
- **Tuần 3:** chuẩn hóa provenance audio → transcript → mệnh đề; lập allowlist nguồn y tế và prototype tìm kiếm truy hồi có dẫn nguồn.
- **Tuần 4:** nối nghe lại audio, demo panel AI tìm kiếm có nhóm câu hỏi/nguồn/điểm an toàn, chạy ca ngoài khuôn, báo cáo lỗi và rà soát với bác sĩ cố vấn.

**Đầu ra:** ma trận hiện trạng; manifest xác nhận 200 khuôn hiện có và số mẫu thực tế; kế hoạch mở rộng lên 300 khuôn/10.000–12.000 mẫu đã QC; test set độc lập; báo cáo baseline và trùng lặp; demo nghe lại và tìm kiếm có dẫn nguồn; allowlist nguồn v1; backlog P0/P1/P2 cùng danh sách module chưa nối luồng thật.

## 10. Rủi ro

| Rủi ro | Cách giảm |
|---|---|
| Điểm tổng tốt lên nhưng lỗi nặng tăng | Chỉ số riêng và cổng phát hành cho lỗi trọng yếu |
| Test tổng hợp giống train | Tách theo nguồn/khuôn, test ngoại khuôn, kiểm tra tương đồng |
| Transcript sai nhưng ghi chú hợp lý | Đo lỗi ASR lâm sàng, nghe audio, đánh dấu bất định |
| Cảnh báo bị bỏ qua | Giải thích nguồn, phân mức, đo hành vi duyệt |
| Demo bị hiểu là thật | Event backend và nhãn minh họa |
| FHIR bị hiểu là tích hợp bệnh viện | Báo đúng mức: JSON, sandbox hay production |
| PHI lộ qua log/lưu trữ | Data-flow, phân quyền, log tối thiểu, thời hạn xóa |

## 11. Nguồn tham khảo

### Quản trị AI, đánh giá và dữ liệu

- WHO, framework for training, validation and evaluation of AI medical devices: https://www.who.int/publications/i/item/9789240038462
- NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework
- DECIDE-AI, reporting guideline for early-stage clinical evaluation: https://www.nature.com/articles/s41591-022-01772-9
- SCRIBE, framework đánh giá transcription, diarization, note quality và robustness của ambient scribe: https://www.nature.com/articles/s41746-025-01622-1
- Rabotin et al., error propagation từ thông dịch sang ghi chú AI trong encounters mô phỏng, JMIR Medical Informatics 2026; nghiên cứu mô tả quy mô nhỏ, hỗ trợ đo lỗi xuyên tầng nhưng không thể ngoại suy trực tiếp sang MediTrace/tiếng Việt: https://doi.org/10.2196/88734
- SourceCheckup, đánh giá mức độ nguồn y tế hỗ trợ từng mệnh đề được trích dẫn, Nature Communications 2025: https://www.nature.com/articles/s41467-025-58551-6
- VietMed, benchmark ASR tiếng Việt miền y khoa, LREC-COLING 2024: https://aclanthology.org/2024.lrec-main.1509/
- ViMedCSS, benchmark tiếng Việt y khoa có code-switch, LREC 2026: https://aclanthology.org/2026.lrec-1.445/
- VietMed-NER, spoken medical NER tiếng Việt, NAACL 2025 Industry Track: https://aclanthology.org/2025.naacl-industry.59/
- CONSORT-AI extension: https://www.nature.com/articles/s41591-020-1034-x
- SPIRIT-AI extension: https://www.nature.com/articles/s41591-020-1037-7
- Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15, Cổng văn bản Chính phủ (hiệu lực 01/01/2026): https://vanban.chinhphu.vn/?classid=1&docid=214590&pageid=27160&typegroupid=
- Nghị định 356/2025/NĐ-CP, Cổng văn bản Chính phủ (hiệu lực 01/01/2026): https://vanban.chinhphu.vn/?docid=216387&pageid=27160
- NCBI E-utilities policy: https://www.ncbi.nlm.nih.gov/books/NBK25497/

### Hạ tầng, API và truy xuất bằng chứng

- PostgreSQL concurrency control and transaction isolation: https://www.postgresql.org/docs/current/mvcc.html
- OpenTelemetry signals: https://opentelemetry.io/docs/concepts/signals/
- OWASP API Security Top 10 2023: https://api-security.owasp.org/editions/2023/en/0x00-header/
- SourceCheckup, medical reference relevance/citation evaluation: https://www.nature.com/articles/s41467-025-58551-6

- WHO, AI for health governance: https://www.who.int/publications/i/item/9789240084759
- AWS HealthScribe: https://docs.aws.amazon.com/transcribe/latest/dg/health-scribe.html
- HL7 FHIR R4 DocumentReference: https://hl7.org/fhir/R4/documentreference.html
- HL7 FHIR R4 Provenance: https://hl7.org/fhir/R4/provenance.html
- Heidi: https://www.heidihealth.com/solutions/medical-scribe-software
- Abridge: https://www.abridge.com/press-release/abridge-inside-emory
- Nabla Connect: https://nabla.com/connect
- Ambience Patient Summary: https://www.ambiencehealthcare.com/blog/ambience-healthcare-s-patient-recap-offers-clinicians-the-first-chart-summarization-technology-from-an-ambient-ai-platform
- Devpost: https://devpost.com/software/clinical-note-guard ; https://devpost.com/software/carryover-tcrfw3 ; https://devpost.com/software/resona-x4fwds ; https://devpost.com/software/carescribe
- GitHub: https://github.com/pisong314/notetrace ; https://github.com/phairlab/berta-ai-scribe ; https://github.com/BirgerMoell/open-medical-scribe ; https://github.com/sammargolis/OpenScribe

## 12. Danh mục nguồn y tế đề xuất cho AI tìm kiếm

Danh sách khởi đầu để xây allowlist, không phải xếp hạng tuyệt đối. Phải kiểm tra từng tài liệu, ngày hiệu lực, đối tượng và quyền truy cập trước khi lập chỉ mục; ưu tiên phiên bản chính thức, tránh lấy bài viết không rõ tác giả làm căn cứ lâm sàng.

| Nhóm | Nguồn/website | Vai trò phù hợp trong MediTrace |
|---|---|---|
| Việt Nam — cơ quan quản lý | [Bộ Y tế](https://moh.gov.vn/) | Văn bản, hướng dẫn, quyết định và chính sách hiện hành; ưu tiên cho bối cảnh Việt Nam. |
| Việt Nam — khám chữa bệnh | [Cục Quản lý Khám, chữa bệnh](https://kcb.vn/) | Hướng dẫn chuyên môn, quy trình kỹ thuật/lâm sàng và chất lượng khám chữa bệnh. |
| Việt Nam — dược | [Cục Quản lý Dược](https://dav.gov.vn/) và [cổng dịch vụ/tra cứu thuốc](https://dichvucong.dav.gov.vn/) | Đăng ký, cảnh báo, thông tin quản lý và tra cứu thuốc tại Việt Nam; cần kiểm tra tên hoạt chất, hàm lượng, dạng dùng và thị trường. |
| Việt Nam — dịch tễ | [Cục Phòng bệnh](https://vadp.gov.vn/) | Dịch bệnh, giám sát, vaccine và khuyến cáo phòng bệnh thuộc Bộ Y tế. |
| Việt Nam — y tế công cộng | [Viện Vệ sinh Dịch tễ Trung ương](https://nihe.org.vn/) | Dịch tễ, vaccine, xét nghiệm, y tế công cộng và nghiên cứu thuộc phạm vi chuyên môn của Viện. |
| Việt Nam — cơ sở chuyên môn | [Bệnh viện Bạch Mai](https://bachmai.gov.vn/) | Hướng dẫn người bệnh, quy trình bệnh viện và nội dung chuyên khoa; dùng như nguồn cơ sở, không thay hướng dẫn Bộ Y tế. |
| Quốc tế — hướng dẫn/tổ chức | [WHO](https://www.who.int/health-topics) và [WHO Guidelines](https://www.who.int/publications/who-guidelines) | Khuyến cáo/hướng dẫn quốc tế, thông tin bệnh và y tế công cộng; gắn rõ phạm vi toàn cầu/khu vực. |
| Quốc tế — y tế công cộng | [CDC Hoa Kỳ](https://www.cdc.gov/) | Dịch tễ, phòng bệnh, vaccine và hướng dẫn lâm sàng thuộc phạm vi Hoa Kỳ; ghi rõ bối cảnh Mỹ. |
| Quốc tế — hướng dẫn thực hành | [NICE](https://www.nice.org.uk/guidance) | Clinical guidelines, technology appraisal và khuyến nghị trong hệ thống Anh; luôn hiển thị quốc gia và ngày cập nhật. |
| Quốc tế — thông tin sức khỏe | [NHS](https://www.nhs.uk/conditions/) và [MedlinePlus](https://medlineplus.gov/) | Giải thích bệnh/triệu chứng/thuốc dễ hiểu cho người bệnh; không dùng thay hướng dẫn điều trị chuyên môn. |
| Quốc tế — thuốc/quản lý | [FDA Drug Safety](https://www.fda.gov/drugs/drug-safety-and-availability/drug-safety-communications), [FDA Labels](https://labels.fda.gov/), [DailyMed](https://dailymed.nlm.nih.gov/dailymed/) và [EMA Medicines](https://www.ema.europa.eu/en/medicines) | Nhãn, thông tin an toàn và tình trạng thuốc theo từng khu vực pháp lý; không suy ra thuốc được phép lưu hành tại Việt Nam từ phê duyệt nước ngoài. |
| Quốc tế — tổng hợp bằng chứng | [Cochrane Evidence](https://www.cochrane.org/evidence) | Tổng quan hệ thống và tổng hợp bằng chứng; kiểm tra ngày cập nhật và câu hỏi/phạm vi tổng quan. |
| Quốc tế — tìm nghiên cứu | [PubMed](https://pubmed.ncbi.nlm.nih.gov/), [PubMed Central](https://pmc.ncbi.nlm.nih.gov/) | Tìm bài nghiên cứu và toàn văn lưu trữ; PubMed là cơ sở dữ liệu thư mục, bài được lập chỉ mục không tự động đồng nghĩa là hướng dẫn hay bằng chứng chất lượng cao. |
| Quốc tế — thử nghiệm | [ClinicalTrials.gov](https://clinicaltrials.gov/) | Tra cứu đăng ký/kết quả nghiên cứu; chỉ mô tả thử nghiệm, không trình bày thuốc/thủ thuật thử nghiệm như điều trị chuẩn. |

**Thứ tự ưu tiên truy hồi:** (1) hướng dẫn Bộ Y tế/cơ quan Việt Nam đúng thẩm quyền và còn hiệu lực; (2) hướng dẫn chuyên môn của cơ sở cho quy trình tại chính cơ sở; (3) hướng dẫn WHO/NICE/CDC và cơ quan tương đương với địa bàn được gắn nhãn; (4) tổng quan hệ thống; (5) nghiên cứu gốc để bổ sung khi cần. Thông tin thuốc lấy từ cơ quan quản lý/nhãn chính thức theo đúng thị trường, không lấy bài SEO hoặc nội dung quảng bá làm bằng chứng.

**Metadata bắt buộc cho mỗi nguồn:** tổ chức phát hành, loại tài liệu, chủ đề/chuyên khoa, quốc gia/phạm vi, ngày xuất bản/cập nhật, trạng thái hiệu lực nếu xác định được, URL chính tắc, thời điểm truy cập, quyền sử dụng, ngày kiểm tra gần nhất và người/tiến trình duyệt nguồn.

## 13. Định hướng chốt

MediTrace đã có lõi đáng giữ: pipeline nhiều bước, kiểm căn cứ, thể hiện nội dung cần bác sĩ xem, cùng màn hình mẫu có tìm kiếm/tạo mẫu ở mức giao diện. Thứ tự nâng cấp: **đánh giá độc lập → mở rộng dữ liệu lên 300 khuôn có kiểm soát → provenance/nghe lại → giảm bỏ sót theo taxonomy → AI tra cứu có nguồn → duyệt có phiên bản → thư viện tạo tài liệu → FHIR → pilot có kiểm soát**. Ba yêu cầu về an toàn dữ liệu trong ảnh đầu và thiết kế AI tìm kiếm trong ảnh sau là đầu vào cho nghiệm thu.

