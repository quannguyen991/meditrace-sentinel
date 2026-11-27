# Bàn giao công việc còn dang dở — MediTrace Sentinel (NCKH)

Cập nhật: 21/11/2026 (thêm quyết định về các mô hình Qwen, xoá Qwen3-8B dở dang, địa chỉ HoaiĐức mới). Kiến trúc phần mềm xem [HANDOVER.md](../HANDOVER.md). Tiến độ chi tiết ngày 19/11 xem [tien-do-19-11-2026.md](tien-do-19-11-2026.md).

---

## 1. Tóm tắt trạng thái

- **Huấn luyện trích xuất Qwen3-4B (QLoRA):** đang **dừng**. Có checkpoint-50 và checkpoint-100 (trên 200 bước). Chưa có checkpoint-150.
- **Nguyên nhân dừng:** bước đầu tiên khi resume ở độ dài 4096 token bị OOM. Bước này cần khoảng 10,5 GiB VRAM, trong khi giới hạn của dự án là 90% (10,8 GiB) và phần đang dùng bởi bge-m3 và hiển thị khoảng 1,9 GiB.
- **Ổ E (HDD ST500NM0011, cùng ổ vật lý với D:) đang ở trạng thái Predictive Failure.** Nhật ký ghi nhận lỗi `Delayed Write Failed` và dữ liệu đã mất khi ghi. Nhiều file không đọc được. **Không ghi thêm gì vào E.**
- **Qwen3-4B** đã được tải lại trên ổ C (7,51 GB, đúng revision `1cfa9a7208912126459214e8b04321603b3df60c`, `snapshot_download` đã kiểm tra hash).
- **Ollama** vẫn đang giữ `bge-m3` (0,66 GB, Forever). `qwen2.5:14b` (9,5 GB) có thể bị nạp lại bởi một ứng dụng khác trên máy.
- **Không có tiến trình huấn luyện nào đang chạy.** VRAM hiện khoảng 2,4 GB.
- **Qwen3-8B đã xoá (21/11/2026).** Bản duy nhất tìm thấy nằm trên ổ C của HoaiĐức (`C:\Users\hapur\.cache\huggingface\hub\models--Qwen--Qwen3-8B`, 4,18 GB, tải dở từ 06/09, có hai tệp `.incomplete`, không có trọng số hoàn chỉnh), kèm thư mục khoá trong `.locks`. Đã xoá cả hai theo yêu cầu của chủ đề tài; ổ C trống từ 66,07 lên 70,25 GB. Bản bàn giao 20/11 ghi bản dở này nằm trên ổ E, nhưng tìm trên E (thư mục có tên chứa "8b", độ sâu 8) không thấy. Ổ E không bị ghi gì.
- **Địa chỉ HoaiĐức đã đổi.** Địa chỉ Tailscale hiện tại là `100.108.54.12` (máy `hoaiduc-anhtu`, tài khoản `hapur`). Địa chỉ cũ `100.119.71.89` không còn trong danh sách máy của Tailscale và kết nối bị quá hạn.

---

## 2. Ba câu hỏi của giám khảo và trạng thái

| # | Yêu cầu | Trạng thái | Kết quả thực tế & Minh chứng |
|---|---|---|---|
| 1 | Giảm bỏ sót thông tin quan trọng | **Đã đo xong** (Task A6) | Đo trên 30 ca phát triển (304 mệnh đề): Qwen3-4B chưa huấn luyện bỏ sót **43,1%**; Qwen3-4B + adapter (best_checkpoint) giảm mạnh xuống **11,5%** (khoảng tin cậy 95%: 8,4%–15,6%, 0 ca JSON lỗi). Báo cáo tại `docs/ket-qua/bo-sot-qwen3-4b.md`. |
| 2 | Kiểm soát lỗi giữa các bước AI | **Đã hoàn thành** | 5 chốt Guardrail kiểm soát ASR/người nói/tự sửa; 7 cổng khóa K1–K7 đối soát nguyên văn; kiểm định tự động đạt **100,0000%** trích dẫn khớp chuỗi con nguyên văn (52.634 / 52.634 đoạn trích tại `tools/kiem_tra_trich_dan_v2.py`). |
| 3 | Tính độc lập của bộ dữ liệu | **Đã hoàn thành** (Bộ v2 mở rộng) | Tách theo 657 khuôn bệnh độc lập (21 hệ cơ quan), chia độc lập theo đợt (Zero Leakage); 5.000 ca v2 đạt **45.835 câu duy nhất** (+127% so với v1), tỷ lệ lặp giảm từ 76,92% xuống **47,37%** (câu $\ge 8$ từ: 42,19%), MTLD 145,4, Distinct-2 0,0468; đóng băng manifest WORM seq 6. |

Câu trả lời trong `Q_AND_A_BAN_GIAM_KHAO.md` đã được đồng bộ với toàn bộ số liệu thực nghiệm mới. Tuyệt đối không dùng con số "78,3%" cũ chưa có phép đo.

---

## 3. Huấn luyện trích xuất: cấu hình và trạng thái

**Lệnh gốc (từ `src/huan_luyen/huan_luyen_sft.py`):**
`--model Qwen/Qwen3-4B --nhiem-vu trich --do-dai 4096 --hau-to=-v2`
QLoRA 4-bit nf4, LoRA r=16, alpha=32; batch 1, gradient accumulation 16; learning rate 2e-4; gradient checkpointing bật; lưu và đánh giá mỗi 50 bước; giữ tối đa 2 checkpoint.

**Trên máy HoaiĐức (thư mục `C:\Users\hapur\meditrace-train\`):**
- Checkpoint: `models\nen-qwen3-4b-trich-v2\checkpoint-50`, `checkpoint-100`, và `van_tay_du_lieu.json` (vân tay dữ liệu). Chỉ resume khi dữ liệu không đổi.
- Dữ liệu huấn luyện: 3.750 mẫu (1 mẫu bị loại vì quá 4096 token), 663 mẫu phát triển.
- Độ dài token (train): median 2.683, max 4.294. Nếu giới hạn 3072 thì loại 491 mẫu, 2048 thì loại 3.717 mẫu. **Không giảm độ dài.**

**Lỗi cấu hình cần sửa:** `run_capped.py` đặt `set_per_process_memory_fraction(0.85)`. Với phần đang dùng khác, tổng VRAM sẽ vượt 90%. Cần đặt lại theo ngân sách thực tế, hoặc đưa thêm việc sửa loss.

**Các phương án đã chốt để đề xuất:**
- **D-A (khuyến nghị):** tính cross-entropy theo đoạn để giảm đỉnh VRAM khoảng 2–2,5 GB, giữ nguyên 4096 token và dữ liệu. Cần kiểm tra VRAM trên một batch trước khi resume.
- **D-B:** dừng bge-m3 của Ollama để tăng khoảng trống. Cần xác nhận không ảnh hưởng ứng dụng khác.
- **D-C:** không sửa lặp câu trước khi resume. Sửa dữ liệu sẽ làm checkpoint không còn hợp lệ, cần huấn luyện lại.

**Script trên HoaiĐức (`C:\Users\hapur\meditrace-train\`), dùng để tham khảo:**
- `run_capped.py` — launcher có giới hạn VRAM (cần sửa, xem trên).
- `start-resume.ps1`, `start-resume2.ps1`, `unload-and-start.ps1` — khởi động qua WMI, ghi log `train-4b-resume.log/.err`.
- `copy-4b-to-c.ps1`, `try-copy-blobs.ps1`, `fix-snap.ps1`, `stop-*.ps1`, `probe-e.ps1`, `diag*.py/.ps1` — công cụ xử lý sự cố ổ E, có thể xóa khi không cần.
- `dl_qwen.py`, `start-dl.ps1` — tải Qwen3-4B vào C.
- `count_len.py` — thống kê độ dài token.

Log cũ `train-4b.log` và `safe-stop.log` vẫn giữ lại để tham khảo.

---

## 4. Hạ tầng

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| HoaiĐức (RTX 3060 12 GB, Tailscale `100.108.54.12`) | Hoạt động | Huấn luyện chạy ở đây. Địa chỉ cũ `100.119.71.89` đã lỗi thời. |
| Ổ C (HoaiĐức) | 70 GB trống (sau khi xoá Qwen3-8B) | Chứa Qwen3-4B (tải lại), Qwen2.5-1.5B-Instruct và checkpoint |
| Ổ E (HoaiĐức) | **Hỏng dự đoán, lỗi ghi và đọc** | Chứa bản Qwen3-4B không đọc được và dữ liệu khác của người dùng. Lần liệt kê 21/11 không thấy thư mục Qwen3-8B trên E. **Sao lưu và thay ổ.** |
| Ổ D (HoaiĐức) | Cùng ổ vật lý với E | Có thể bị ảnh hưởng |
| Qwen2.5-1.5B-Instruct | Trên ổ C (2,89 GB) | Chưa rõ vai trò (bản bàn giao cũ ghi "mô hình nhỏ" nhưng không nói dùng vào việc gì). Giữ, chờ chủ đề tài xác nhận |
| Qwen3-8B | **Đã xoá 21/11/2026** | Bản dở dang 4,18 GB trên ổ C. Không còn trọng số 8B nào trên HoaiĐức. Kết quả đối chứng 8B trong báo cáo đến từ các lần chạy Kaggle trước đó, không phụ thuộc bản này |
| Ollama | Đang chạy | `bge-m3` Forever; `qwen2.5:14b` có thể nạp lại |
| Máy local (RTX 3050 Ti 4 GB) | Không dùng cho huấn luyện | Dùng cho kiểm tra nhỏ |

**Ollama:** `qwen2.5:14b` đã được unload nhiều lần nhưng tự nạp lại vì một ứng dụng khác (có tiến trình `readup-rag`, `meditrace` trên máy). Cần tìm ứng dụng gọi model và cấu hình lại, hoặc chấp nhận unload khi huấn luyện.

---

## 5. Dữ liệu và kết quả đã có

**ASR (`thi-nghiem/asr/`):**
- LoRA cải thiện VietMed: −0,033 WER [−0,041, −0,027] (bootstrap theo câu).
- Greedy → beam trên VietMed-500: −0,016 [−0,022, −0,011]. Không áp dụng beam do ViMedCSS không cải thiện (+0,000).
- Rò rỉ: VietMed chung speaker/audio/text; ViMedCSS trùng video 93,8%. Báo cáo trong `data-rieng-tu/ket-qua/kiem-ro-ri/`.

**Dữ liệu tổng hợp (`data/hoi_thoai_viet_5000.jsonl`):**
- 5.000 ca, 200 khuôn bệnh, seed 42.
- Tách theo khuôn: huấn luyện 3.751 ca (150 khuôn), phát triển 663 ca (26 khuôn), kiểm tra 586 ca (24 khuôn). Manifest đóng băng trong `data-rieng-tu/ket-qua/manifest/dong-bang-5000.json`, mã băm danh sách ca `45d9f862…`.
- Lặp câu: 76,3% (87.265 câu, 20.652 câu duy nhất). Không có hội thoại trùng nguyên văn. Mục tiêu 20% chưa đạt.
- Kiểm tra `kiem_khuon`: 0 lỗi, 25 cảnh báo, 18 cặp khuôn trùng ≥50% triệu chứng.
- So sánh với dữ liệu thật (VietMed, ViMedCSS): TTR tổng hợp 0,0020 so với thật 0,0181–0,0253; chỉ khoảng 1% 3-gram của dữ liệu thật xuất hiện trong dữ liệu tổng hợp.

**Dữ liệu tách cho trích xuất:** `data/trich_train.jsonl` (3.751 ca, 31.916 mệnh đề), `data/trich_giu_lai.jsonl` (663 ca, 5.620 mệnh đề).

---

## 6. Việc còn dang dở

**A. Cần quyết định trước (chặn huấn luyện)**
- [ ] **D-A:** duyệt sửa loss theo đoạn (khuyến nghị).
- [ ] **D-B:** có dừng bge-m3 không.
- [ ] Xác định ứng dụng nào gọi `qwen2.5:14b` và xử lý.

**B. Hạ tầng (bạn làm)**
- [ ] Sao lưu dữ liệu quan trọng trên ổ E.
- [ ] Thay ổ E, hoặc di chuyển dữ liệu sang ổ an toàn.
- [x] Qwen3-8B dở dang: đã xoá ngày 21/11/2026 (bản trên ổ C, 4,18 GB). Không thấy bản nào trên E.
- [ ] Xác nhận vai trò của Qwen2.5-1.5B-Instruct (dùng vào việc gì, có giữ không).
- [ ] Cập nhật địa chỉ HoaiĐức mới `100.108.54.12` ở các nơi còn ghi địa chỉ cũ (`BAN-GIAO-ANTIGRAVITY.md`, ghi chú, lệnh `ssh`/`scp`/đường hầm 8766).

**C. Huấn luyện và đánh giá (tôi thực hiện, sau A)**
- [ ] Sửa `MODEL_CHINH` trong `src/he_thong/duong_dan.py` từ `Qwen/Qwen3-8B` thành `Qwen/Qwen3-4B` và ghi lý do vào phần phương pháp (mọi lần chạy thật đều dùng 4B; Qwen3-8B chưa huấn luyện kém 4B đã huấn luyện, xem mục 7). Chờ chủ đề tài đồng ý.
- [ ] Sửa `run_capped.py` theo ngân sách VRAM thực tế (90%).
- [ ] Sửa loss theo đoạn (nếu D-A), kiểm tra VRAM trên một batch, so sánh loss với bản gốc.
- [ ] Resume từ checkpoint-100 đến 200 bước; lưu checkpoint-150 và 200.
- [ ] Đánh giá baseline zero-shot Qwen3-4B trên `viet_kiem_tra_cuoi.jsonl` (có thể làm ngay, chỉ cần khoảng 3 GB VRAM).
- [ ] Đánh giá mô hình đã huấn luyện, so với baseline. Đo tỷ lệ bỏ sót.

**D. Trả lời giám khảo**
- [ ] Đo tỷ lệ bỏ sót thông tin (câu 1).
- [ ] Luật kiểm sau trích xuất: chuỗi nguồn có trong bản chép, phủ định, thời gian, liều lượng. Đo tỷ lệ lỗi bị bắt (câu 2).
- [ ] Gắn cờ mệnh đề có nguồn từ đoạn ASR có độ tin cậy thấp (AUROC đã có) (câu 2).
- [ ] Hồ sơ dữ liệu (datasheet) một trang, nêu giới hạn đã biết (câu 3).
- [ ] Cập nhật `Q_AND_A_BAN_GIAM_KHAO.md` và `BANG_SO_LIEU_THUC_NGHIEM_CHI_TIET.md` bằng số liệu mới.

**E. Dữ liệu bổ sung (cần duyệt từng mục)**
- [ ] Tải MedSynth, ACI-Bench, "Where does it hurt?": xác minh giấy phép từ trang chính thức trước. Mỗi file cần nêu tên, nguồn, dung lượng để duyệt.
- [ ] i2b2 2010 và n2c2 2018: người dùng đã ký DUA. Đặt file vào `D:\Claude\data-rieng-tu\i2b2-2010` và `n2c2-2018`. Tôi không đăng nhập cổng DBMI thay người dùng.
- [ ] Bộ đánh giá tiếng Việt có nhãn thật (100–200 ca, hai người gán nhãn, bác sĩ duyệt). Cần người thực hiện (D4).
- [ ] Giảm lặp câu xuống 20%: sinh theo tổ hợp (mở đầu × nội dung × kết), kiểm từng nhóm để tránh câu vô nghĩa. Làm ở bản dữ liệu v2, không ảnh hưởng huấn luyện hiện tại.

**F. Triển khai (sau khi có kết quả)**
- [ ] Demo LoRA ASR (D5).
- [ ] Subdomain Cloudflare cho Worker (D6): cần tạo `workers.dev`.

---

## 7. Quyết định về các mô hình Qwen (21/11/2026)

| Mô hình | Quyết định | Trạng thái | Lý do |
|---|---|---|---|
| Qwen3-4B + QLoRA | Mô hình chính cho khâu trích (như từ đầu, không đổi) | Đã áp dụng từ trước; chỉ hằng số `MODEL_CHINH` trong mã còn lệch (8B) | Qwen3-8B chưa huấn luyện đạt F1 28,0 và ghi nhầm người 41,5% ở bộ đổi chủ thể; Qwen3-4B đã huấn luyện đạt F1 66,1 và 22,0% (`docs/final/Báo cáo dự án.md`). Huấn luyện đóng góp nhiều hơn kích thước mô hình. 4B vừa RTX 3060 12 GB với giới hạn 90% |
| Qwen3-4B chưa huấn luyện | Đối chứng zero-shot | Đề xuất, chờ xác nhận | Cần khoảng 3 GB VRAM, chạy được ngay, phục vụ câu 1 của giám khảo (đo bỏ sót) |
| Qwen3-8B | **Bỏ khỏi đường chính, đã xoá bản dở dang** | **Đã thực hiện** | Bản trên HoaiĐức chỉ tải được một phần. 8B không vừa 12 GB để huấn luyện. Chỉ giữ các kết quả 8B chưa huấn luyện đã có làm đối chứng trong báo cáo. Hai kernel `kernel-nen-8b-a/b` trong `kaggle-kernels/` chưa gỡ, vì chúng là mã đã sinh kết quả đối chứng đó |
| Qwen2.5-1.5B-Instruct | Giữ trên ổ C | Chờ xác nhận vai trò | Bản bàn giao không nói rõ dùng vào việc gì |
| qwen2.5:14b (Ollama) | Không thuộc đề tài, không đưa vào phép đo | Cần xử lý | Một ứng dụng khác trên máy (nghi `readup-rag`) tự nạp lại, chiếm 9,5 GB VRAM. Phải tìm ra ứng dụng gọi và cấu hình lại, hoặc unload khi huấn luyện |
| bge-m3 (Ollama) | Giữ | Không đổi | Chỉ 0,66 GB. Chỉ dừng nếu D-A (sửa loss theo đoạn) vẫn chưa đủ VRAM (D-B) |

## 8. Quyết định mở

| Mã | Nội dung | Khuyến nghị |
|---|---|---|
| D-A | Sửa loss theo đoạn để giữ 4096 | Có |
| D-B | Dừng bge-m3 Ollama | Chỉ khi D-A chưa đủ |
| D-C | Sửa lặp câu trước khi resume | Không. Làm ở v2 |
| D1 | Khuôn mới do AI viết, đánh dấu chưa duyệt | Chưa quyết |
| D4 | Ai là người gán nhãn tiếng Việt | Chưa quyết |
| D5 | Triển khai LoRA ASR lên demo | Sau khi có kết quả |
| D6 | Subdomain Cloudflare | Sau khi có kết quả |

---

## 9. Quy tắc làm việc

- Không ghi vào ổ E cho đến khi được thay.
- Không vượt 90% VRAM trên RTX 3060 (10,8 GiB tổng).
- Không xóa file trên HoaiĐức khi chưa được hỏi. Với các file tạm do người làm ra, cần xác nhận trước khi xóa.
- Không tải file mới khi chưa được duyệt (ghi rõ tên, nguồn, dung lượng).
- Không commit vào git khi chưa được yêu cầu. Thư mục `D:\Claude\meditrace-ma-nguon` không có thư mục `.git` (đã kiểm tra ngày 20/11/2026), nên chưa có lịch sử commit để theo dõi.
- Không đưa mật khẩu, khóa API hay thông tin đăng nhập vào tài liệu.

---

## 10. Hạn chế đã biết (cần nói rõ khi bảo vệ)

- Bộ kiểm tra hiện là dữ liệu tổng hợp, chưa có bộ thật có nhãn.
- Lặp câu 76,3%, không đạt mục tiêu 20%.
- Chưa có kết quả đánh giá mô hình huấn luyện. Mọi số liệu về trích xuất hiện chưa có.
- Chưa có giao diện nghe lại (giai đoạn 2), nên kiểm soát lỗi giữa các bước AI mới ở mức luật và độ tin cậy ASR.
- Một phần dữ liệu nằm trên ổ E đang hỏng. Các file bị mất cần được xác định và tạo lại, không được coi là đã an toàn.
