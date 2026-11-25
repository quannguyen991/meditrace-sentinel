# Nâng cấp toàn diện MediTrace Sentinel — Kế hoạch triển khai

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mở chặn huấn luyện khâu trích Qwen3-4B, đo được tỷ lệ bỏ sót, sinh bộ dữ liệu v2 ít lặp câu và có thêm khuôn bệnh, tình huống, kịch bản mới, huấn luyện thêm bằng dữ liệu ngoài có kiểm soát, và thay hàng đợi tạo bản nháp trong RAM bằng hàng đợi bền vững.

**Architecture:** Sáu luồng, thứ tự ưu tiên A → B → F → E → C → D. Luồng A (Python) sửa lỗi hết bộ nhớ bằng cách tính loss theo đoạn rồi đo. Luồng B thêm thước đo lặp câu và mở rộng nhóm câu của bộ sinh luật. Luồng F thêm 50 khuôn bệnh, ba tình huống (bối cảnh) và ba kịch bản (bẫy) mới, tất cả sau một cờ `mo_rong` để bộ cũ không đổi một bit nào. Luồng E đưa dữ liệu ngoài vào huấn luyện: dùng hội thoại thật của VietMed, gán nhãn trước bằng chính mô hình của dự án, lọc tự động, trộn tối đa 20%, và đo trên đoạn thật không cần nhãn. Luồng C (TypeScript) thêm hàng đợi bền vững. Luồng D cập nhật tài liệu bằng số liệu in từ chương trình.

**Tech Stack:** Python (pytest, torch, transformers, peft), TypeScript (`node:sqlite`, `tsx`), SQLite WAL.

**Spec:** `KE_HOACH_NANG_CAP_TOAN_DIEN_MEDITRACE.md` (bản 1.4, mục 0 và 4.3E, Giai đoạn 1B và 5) và `docs/BAN-GIAO-CONG-VIEC-DANG-DO.md` (21/11/2026).

**Phạm vi chưa có trong kế hoạch này (cần kế hoạch riêng):** nghe lại đúng đoạn trên giao diện, Sherpa-ONNX, RLVR/GRPO, FHIR, thử nghiệm lâm sàng, và gán nhãn dữ liệu thật bằng mô hình thương mại (cổng quyết định G1 ở Luồng E). Lý do: chưa có số liệu nền, hoặc cần bạn quyết định trước.

**Ba bộ dữ liệu ngoài đã tải (`D:\Claude\data-rieng-tu\du-lieu-ngoai\`) và vai trò thật của từng bộ:**

| Bộ | Dùng vào việc gì trong kế hoạch | Ghi chú |
|---|---|---|
| VietMed (chép lời) | Nguồn hội thoại thật cho Luồng E (gán nhãn trước, lọc, trộn tối đa 20%) | Giấy phép ba nguồn không khớp (MIT, CC BY 4.0, CC BY-NC 4.0). Coi như phi thương mại cho tới khi xác nhận |
| hungnm/vietnamese-medical-qa | Kho cách nói triệu chứng cho bộ sinh (Task E2), không làm mẫu huấn luyện trực tiếp | Apache 2.0 |
| VietMed-Sum | **Không dùng để huấn luyện.** Chỉ xem cấu trúc (Task E1) | `docs/nguon-va-giay-phep.md` ghi tóm tắt tập SYN do GPT-3.5 tạo và thẻ không có giấy phép. Quy tắc dự án: dữ liệu do mô hình thương mại sinh chỉ để đo |

## Global Constraints

- Không ghi vào ổ E của HoaiĐức. Không vượt 90% VRAM của RTX 3060 (10,8 GiB tổng).
- Không xoá tệp trên HoaiĐức khi chưa hỏi. Không tải tệp mới khi chưa được duyệt (nêu tên, nguồn, dung lượng). Hỏi trước khi khởi động lại dịch vụ trên HoaiĐức. Địa chỉ HoaiĐức hiện tại: `100.108.54.12` (tài khoản `hapur`).
- Không commit vào git khi chưa được yêu cầu. Kho `D:\Claude\meditrace-ma-nguon` hiện không có `.git`, nên mỗi tác vụ kết thúc bằng bước "Ghi nhận" thay cho commit.
- Không đưa mật khẩu, khoá API hay thông tin đăng nhập vào mã hoặc tài liệu.
- Không sửa tệp tiếng Việt bằng PowerShell `Get-Content`/`Set-Content` (hỏng dấu). Dùng công cụ sửa tệp hoặc Python có `encoding="utf-8"`.
- Dữ liệu do GPT hoặc mô hình thương mại sinh chỉ để đo, không vào huấn luyện.
- Không sửa bộ 5.000 ca cũ (`data/hoi_thoai_viet_5000.jsonl`), manifest đóng băng `data-rieng-tu/ket-qua/manifest/dong-bang-5000.json` (mã băm `45d9f862…`), và `van_tay_du_lieu.json` của checkpoint-50/100. Đổi dữ liệu thì phải huấn luyện lại từ đầu với hậu tố mới (`--hau-to=-v3`).
- Mọi số trong báo cáo in từ chương trình, không gõ tay. Kết quả bất lợi ghi ngang hàng với kết quả có lợi.
- Tài liệu viết không ẩn dụ, giải thích mọi thuật ngữ ở lần đầu.
- Chạy kiểm thử: `D:\khkt-venv-lap\Scripts\python -m pytest tests/ -q` trong `D:\Claude\meditrace-ma-nguon`. Không cài thêm gói vào môi trường Python đã khoá.
- Bộ sinh cũ phải giữ nguyên từng bit: mọi tính năng mới (khuôn, tình huống, kịch bản, kho cách nói ngoài) nằm sau cờ `mo_rong`, mặc định tắt. Phép thử vàng ở Task F0 (băm SHA-256 của `sinh_bo(200, seed=42)` và danh sách khuôn từng tập) phải PASS trước và sau mọi sửa đổi ở Luồng B và F.
- Chia tập: 200 khuôn cũ giữ nguyên tập (150 train, 26 phát triển, 24 kiểm tra). Khuôn mới chỉ được vào nhóm riêng, không được làm xáo trộn cách chia của 200 khuôn cũ (vì `tach_tap_viet.phan_khuon` hiện xếp mọi khuôn ngoài 100 khuôn đầu vào cùng một nhóm và xếp hạng bằng băm).
- Dữ liệu ngoài: không bao giờ vào tập phát triển hay kiểm tra đã đóng băng; nhãn do máy gán phải mang thẻ `nguon` và `nhan = "may-chua-kiem"`, không báo cáo như nhãn thật; khuôn do AI viết mang `da_duyet = False` cho tới khi bác sĩ duyệt.
- Đo bộ nhớ: tiến trình huấn luyện được dùng tối đa 8,9 GiB (= 10,8 GiB trừ 1,9 GiB mà bge-m3 và hiển thị đang chiếm).
- Đánh giá trên tập phát triển (`data/viet_phat_trien.jsonl`). Tập kiểm tra cuối (`data/viet_kiem_tra_cuoi.jsonl`) chỉ mở một lần ở báo cáo cuối, không dùng để chọn mô hình hay chỉnh luật. (Bản bàn giao 20/11 ghi baseline zero-shot trên tập kiểm tra cuối; kế hoạch này chọn tập phát triển cho an toàn, cần bạn xác nhận.)

## Review Focus

Các đầu vào dễ làm hỏng mà đặc tả không nêu, xếp theo khả năng gặp:

1. **Nhãn toàn `-100` trong một đoạn** (đoạn chỉ có lời bác sĩ, không có mệnh đề): loss theo đoạn không được ra NaN hoặc chia cho 0. Kiểm ở Task A2.
2. **Độ dài không chia hết cho kích thước đoạn** (đoạn cuối ngắn, hoặc chỉ 1 token): kết quả phải bằng loss tính một lần. Kiểm ở Task A2.
3. **Tệp `.jsonl` có dòng trống hoặc dòng hỏng**: đo lặp câu phải bỏ qua và báo số dòng bỏ, không dừng giữa chừng. Kiểm ở Task B1.
4. **Cùng một câu tiếng Việt viết bằng dạng Unicode NFC và NFD**: phải tính là một câu. Kiểm ở Task B1.
5. **Job đang `dang_chay` khi máy chủ khởi động lại, và cùng một yêu cầu gửi hai lần**: job dở phải được chạy lại (tối đa 2 lần), yêu cầu trùng phải trả về cùng một job. Kiểm ở Task C1.

---

## Luồng A — Mở chặn huấn luyện và đo kết quả

### Task A1: Sửa `MODEL_CHINH` thành Qwen3-4B

**Files:**
- Modify: `src/duong_dan.py:42`
- Test: `tests/test_model_chinh.py` (tệp mới; `tests/test_duong_dan.py` có `pytestmark` bỏ qua cả tệp khi thiếu thư mục `D:/VAIC DE @`, nên không đặt phép thử ở đó)

**Interfaces:**
- Produces: `duong_dan.MODEL_CHINH == "Qwen/Qwen3-4B"`, được `src/train_baseline.py:187` và `src/nhanh.py:352` dùng làm mặc định của `--model`.

- [ ] **Step 1: Viết phép thử `test_model_chinh_la_qwen3_4b` trong `tests/test_model_chinh.py`.** Assertion: `from src import duong_dan; assert duong_dan.MODEL_CHINH == "Qwen/Qwen3-4B"`.
- [ ] **Step 2: Chạy và xác nhận thất bại.** `pytest tests/test_model_chinh.py -v` → FAIL (`Qwen/Qwen3-8B`).
- [ ] **Step 3: Đổi `MODEL_CHINH` ở `src/duong_dan.py` thành `"Qwen/Qwen3-4B"`.** Ghi một dòng chú thích: mọi lần chạy thật đều dùng 4B, 8B chưa huấn luyện kém 4B đã huấn luyện (xem `docs/final/Báo cáo dự án.md`).
- [ ] **Step 4: Chạy lại cả `tests/test_duong_dan.py` và `tests/test_bakeoff.py`.** Mong đợi PASS (phép thử `test_ho_mo_hinh_deu_la_qwen3` vẫn qua).
- [ ] **Step 5: Ghi nhận** vào `docs/tien-do-21-11-2026.md` một dòng: "MODEL_CHINH đổi 8B → 4B".

### Task A2: Hàm loss theo đoạn

**Files:**
- Create: `src/loss_theo_doan.py`
- Test: `tests/test_loss_theo_doan.py`

**Interfaces:**
- Produces: `cross_entropy_theo_doan(hidden: Tensor, lm_head: Module, nhan: Tensor, kich_thuoc_doan: int = 512, bo_qua: int = -100) -> Tensor`. `hidden` có dạng `[B, T, H]`, `nhan` dạng `[B, T]`, cả hai đã được dịch một vị trí (hàm gọi tự dịch). Trả về loss trung bình trên các token không phải `bo_qua`, bằng với `F.cross_entropy` trên toàn bộ logits.

- [ ] **Step 1: Viết bốn phép thử** (đầu tệp `pytest.importorskip("torch")`):
  - `test_bang_loss_day_du`: `torch.manual_seed(0)`, `hidden = randn(1, 1000, 16)`, `lm_head = Linear(16, 50, bias=False)`, `nhan = randint(0, 50, (1, 1000))` với `nhan[0, :100] = -100`; `assert torch.allclose(cross_entropy_theo_doan(hidden, lm_head, nhan, 512), F.cross_entropy(lm_head(hidden).view(-1, 50), nhan.view(-1), ignore_index=-100), atol=1e-6)`.
  - `test_gradient_bang_nhau`: gradient của `lm_head.weight` và `hidden` khớp hai cách tính, `atol=1e-6`.
  - `test_toan_bo_nhan_bo_qua`: `nhan` toàn `-100` → kết quả `== 0.0`, hữu hạn, và `.backward()` chạy được. (Review Focus 1.)
  - `test_do_dai_khong_chia_het`: `T = 513` và `T = 1`, `kich_thuoc_doan = 512` → vẫn bằng loss đầy đủ. (Review Focus 2.)
- [ ] **Step 2: Chạy và xác nhận thất bại.** `pytest tests/test_loss_theo_doan.py -v` → FAIL (chưa có mô-đun).
- [ ] **Step 3: Cài `cross_entropy_theo_doan` trong `src/loss_theo_doan.py`.** Chia theo chiều `T`; mỗi đoạn gọi `torch.utils.checkpoint.checkpoint` bọc phép `lm_head` + tổng cross-entropy (`reduction="sum"`) để logits được tính lại khi lan truyền ngược; cộng các tổng rồi chia cho số token khác `bo_qua`; nếu số token đó bằng 0 thì trả `hidden.sum() * 0.0`.
- [ ] **Step 4: Chạy lại, mong đợi PASS cả 4 phép thử.**
- [ ] **Step 5: Ghi nhận** vào `docs/tien-do-21-11-2026.md`.

### Task A3: Gắn loss theo đoạn vào huấn luyện và tham số hoá giới hạn VRAM

**Files:**
- Modify: `src/loss_theo_doan.py` (thêm `tao_trainer_loss_theo_doan`)
- Modify: `src/train_baseline.py:184-276` (thêm cờ, dùng lớp mới khi bật)
- Create: `tools/run_capped.py` (đọc bản trên HoaiĐức rồi đưa vào kho)
- Create: `tools/do_vram_mot_batch.py`
- Test: `tests/test_loss_theo_doan.py`

**Interfaces:**
- Consumes: `cross_entropy_theo_doan` (Task A2).
- Produces: `tao_trainer_loss_theo_doan(Trainer: type, kich_thuoc_doan: int = 512) -> type` trả về lớp con của `Trainer` ghi đè `compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None)`. Cờ mới của `train_baseline`: `--loss-theo-doan` (cờ bật/tắt, mặc định tắt) và `--kich-thuoc-doan` (int, mặc định 512). `tools/run_capped.py` nhận `--phan-vram` (float, mặc định 0.74, tức 8,9/12).

- [ ] **Step 1: Viết `test_trainer_loss_theo_doan_bang_loss_goc`.** Dựng đối tượng giả có `base_model.model.model(input_ids=, attention_mask=)` trả `SimpleNamespace(last_hidden_state=…)` và `base_model.model.lm_head`; gọi `compute_loss` của lớp con (lớp cha giả `class Trainer: pass`); `assert` bằng `F.cross_entropy` trên toàn logits với nhãn đã dịch một vị trí, `atol=1e-6`.
- [ ] **Step 2: Chạy, xác nhận thất bại** (chưa có `tao_trainer_loss_theo_doan`).
- [ ] **Step 3: Cài `tao_trainer_loss_theo_doan`.** Lấy `hidden` từ `model.base_model.model.model`, `lm_head` từ `model.base_model.model.lm_head`; dịch `hidden[:, :-1]` và `nhan[:, 1:]`; gọi `cross_entropy_theo_doan`. Trong `train_baseline.main`, nếu có `--loss-theo-doan` thì dùng `tao_trainer_loss_theo_doan(Trainer, a.kich_thuoc_doan)` thay cho `Trainer` ở dòng 274. Cờ tắt thì hành vi y hệt cũ.
- [ ] **Step 4: Chạy lại, PASS.** Chạy thêm `pytest tests/ -q -k "train_baseline or loss"` để chắc chắn không hỏng phép thử khác.
- [ ] **Step 5: Đọc `C:\Users\hapur\meditrace-train\run_capped.py` trên HoaiĐức (chỉ đọc, qua `ssh hapur@100.108.54.12`)** rồi chép vào `tools/run_capped.py`; đổi hằng `set_per_process_memory_fraction(0.85)` thành đối số `--phan-vram` mặc định 0.74. Không sửa tệp trên HoaiĐức ở bước này.
- [ ] **Step 6: Viết `tools/do_vram_mot_batch.py`** với hàm `do_vram(model_ten: str, do_dai: int, kich_thuoc_doan: int | None) -> dict` trả `{"peak_gib": float, "loss": float}`: nạp mô hình như `train_baseline`, chạy một bước tiến và lùi trên mẫu dài nhất không quá `do_dai`, đọc `torch.cuda.max_memory_allocated()`.
- [ ] **Step 7 (cần bạn duyệt chạm HoaiĐức): chạy đo.** Chạy `do_vram` ở `do_dai=1024` với và không `kich_thuoc_doan`, mong đợi hai giá trị loss lệch nhau dưới 0,1% (tương đương). Sau đó chạy `do_dai=4096` với `kich_thuoc_doan=512`. Mong đợi `peak_gib <= 8.9`. Nếu lớn hơn, dừng và báo (phương án dự phòng là D-B: dừng bge-m3).
- [ ] **Step 8: Ghi nhận** số đo thật vào `docs/tien-do-21-11-2026.md`.

### Task A4: Tiếp tục huấn luyện từ checkpoint-100 đến 200

**Files:**
- Không tạo hay sửa mã. Dùng `tools/run_capped.py`, `src/train_baseline.py`.

**Interfaces:**
- Consumes: Task A3 (cờ `--loss-theo-doan`, `run_capped.py`), `C:\Users\hapur\meditrace-train\models\nen-qwen3-4b-trich-v2\` (checkpoint-50, checkpoint-100, `van_tay_du_lieu.json`).

- [ ] **Step 1: Xác nhận dữ liệu không đổi.** So `van_tay_du_lieu.json` hiện có với vân tay do `train_baseline._van_tay_du_lieu` tính lại trên `data/trich_train.jsonl` (3.751 ca). Phải khớp, nếu không dừng (chạy tiếp sẽ ra adapter lai hai bộ).
- [ ] **Step 2 (cần bạn đồng ý): dừng bge-m3 chỉ khi Task A3 Step 7 vượt 8,9 GiB.** Không tự dừng.
- [ ] **Step 3 (cần bạn đồng ý chạy trên HoaiĐức): chạy lệnh qua trình giới hạn RAM và VRAM:** `python tools/run_capped.py --phan-vram 0.74 -- python -m src.train_baseline --model Qwen/Qwen3-4B --nhiem-vu trich --do-dai 4096 --hau-to=-v2 --loss-theo-doan`. Chạy thử đúng dòng lệnh này trên laptop với `--kiem-mat-na` trước khi chạy thật.
- [ ] **Step 4: Kiểm tra kết quả.** Có `checkpoint-150` và `checkpoint-200`, `eval_loss` ghi trong log, không có `OutOfMemoryError`. Mong đợi `eval_loss` bước 150 không tăng bất thường so với bước 100.
- [ ] **Step 5: Ghi nhận** đường dẫn checkpoint, loss từng 50 bước, VRAM đỉnh.

### Task A5: Chỉ số tỷ lệ bỏ sót

**Files:**
- Create: `src/do_bo_sot.py`
- Test: `tests/test_do_bo_sot.py`

**Interfaces:**
- Consumes: `src.do_trich.ghep(dap_an, trich, nguong=NGUONG_GHEP) -> (cap, thieu, thua)` (đã có) và hằng `NGUONG_GHEP = 0.6`.
- Produces: `ti_le_bo_sot(cac_ca: list[tuple[list[dict], list[dict]]], nguong: float = NGUONG_GHEP) -> dict` với khoá `"so_menh_de_dap_an"`, `"so_bo_sot"`, `"ti_le_bo_sot"`, `"theo_nhom"`. Mỗi phần tử của `cac_ca` là `(dap_an, trich)`. Mệnh đề đáp án có khoá `nhom_loi` (hoặc `"khac"` nếu thiếu) thì tính riêng theo nhóm.

- [ ] **Step 1: Viết phép thử.**
  - `test_khong_bo_sot`: đáp án và trích giống hệt → `ti_le_bo_sot == 0.0`.
  - `test_bo_sot_mot_nua`: 2 mệnh đề đáp án, trích chỉ 1 → `ti_le_bo_sot == 0.5`, `so_bo_sot == 1`.
  - `test_nguong_ghep_anh_huong`: cùng cặp, `nguong=0.9` cho tỷ lệ cao hơn `nguong=0.3`.
  - `test_ca_rong`: danh sách rỗng → tỷ lệ `0.0`, không chia cho 0.
- [ ] **Step 2: Chạy, xác nhận thất bại.**
- [ ] **Step 3: Cài `ti_le_bo_sot`** gọi `ghep` cho từng ca, cộng dồn số mệnh đề trong `thieu`.
- [ ] **Step 4: Chạy lại, PASS.**
- [ ] **Step 5: Ghi nhận.**

### Task A6: Đo baseline zero-shot và mô hình đã huấn luyện

**Files:**
- Create: `tools/do_bo_sot_tren_tap.py`
- Output: `docs/ket-qua/bo-sot-qwen3-4b.md` (do chương trình sinh)

**Interfaces:**
- Consumes: `ti_le_bo_sot` (Task A5); đầu ra trích của `python -m src.nhanh` (xác nhận ở Step 1 cờ nào chạy khâu trích và `--adapter` có thể bỏ trống để chạy mô hình chưa huấn luyện).
- Produces: bảng Markdown gồm hai dòng "Qwen3-4B chưa huấn luyện" và "Qwen3-4B + adapter (checkpoint-N)" với số mệnh đề đáp án, số bỏ sót, tỷ lệ bỏ sót.

- [ ] **Step 1: Đọc `src/nhanh.py` (phần `argparse`, quanh dòng 352) và ghi vào ghi chú tiến độ** cờ nào chạy khâu trích, `--adapter` bắt buộc hay tuỳ chọn, tệp đầu ra nằm đâu.
- [ ] **Step 2: Viết `tools/do_bo_sot_tren_tap.py`** nhận `--tap-dap-an`, `--tep-trich-zero-shot`, `--tep-trich-adapter`, `--ra`; đọc hai tệp trích, gọi `ti_le_bo_sot`, ghi bảng.
- [ ] **Step 3 (cần bạn đồng ý chạy trên HoaiĐức): chạy khâu trích trên `data/viet_phat_trien.jsonl`** cho (a) mô hình chưa huấn luyện, chỉ cần khoảng 3 GB VRAM, (b) mô hình với adapter mới nhất. Tập phát triển có 663 ca; nếu thời gian quá dài (khoảng 213 giây mỗi bản nháp của luồng đầy đủ, khâu trích riêng nhanh hơn) thì chạy trước 100 ca đầu và ghi rõ số ca.
- [ ] **Step 4: Chạy script đo, mong đợi** có hai dòng số; mở tệp kết quả kiểm tra con số lớn hơn 0 và nhỏ hơn hoặc bằng 1.
- [ ] **Step 5: Ghi nhận** và đưa số này vào Q&A giám khảo ở Task D1 (không gõ tay).

---

## Luồng B — Bộ dữ liệu v2 ít lặp câu

### Task B1: Thước đo lặp câu và độ đa dạng

**Files:**
- Create: `tools/do_lap_cau.py`
- Test: `tests/test_do_lap_cau.py`

**Interfaces:**
- Produces:
  - `tach_cau(input_hoi_thoai: str) -> list[str]`: tách `input` của một ca (mỗi dòng một lượt, đầu dòng ghi người nói như `Bác sĩ:`) thành các câu, bỏ phần ghi người nói, chuẩn hoá NFC, hạ chữ thường, bỏ dấu cách thừa.
  - `do_lap_cau(cac_ca: list[dict]) -> dict` với khoá `"so_cau"`, `"so_cau_duy_nhat"`, `"ty_le_lap"` (= `1 - so_cau_duy_nhat / so_cau`), `"ttr"`, `"mtld"`, `"distinct2"`, `"top_lap"` (20 cặp `(cau, so_lan)` lặp nhiều nhất).
  - `doc_jsonl(duong_dan: str) -> tuple[list[dict], int]` trả các ca hợp lệ và số dòng bị bỏ.

- [ ] **Step 1: Viết phép thử:**
  - `test_ty_le_lap_tay`: ba ca nhỏ dựng tay có 6 câu, 3 câu duy nhất → `ty_le_lap == 0.5`.
  - `test_nfc_nfd_la_mot_cau`: cùng câu tiếng Việt dạng NFC và NFD → đếm là một câu. (Review Focus 4.)
  - `test_doc_jsonl_bo_dong_hong`: tệp có một dòng trống và một dòng JSON hỏng → trả đúng số ca hợp lệ và `so_dong_bo == 2`. (Review Focus 3.)
  - `test_ca_khong_co_input`: ca thiếu khoá `input` → bỏ qua, không lỗi.
  - `test_bo_cu_ty_le_lap_khoang_0_763`: đánh dấu `skipif` khi thiếu `data/hoi_thoai_viet_5000.jsonl`; `assert abs(ty_le_lap - 0.763) < 0.01` (bản bàn giao ghi 87.265 câu, 20.652 câu duy nhất).
- [ ] **Step 2: Chạy, xác nhận thất bại.**
- [ ] **Step 3: Cài ba hàm.** MTLD theo McCarthy & Jarvis 2010 với ngưỡng 0,72; `distinct2` là số cặp từ duy nhất trên tổng số cặp từ.
- [ ] **Step 4: Chạy lại, PASS.** Nếu phép thử bộ cũ lệch quá 1 điểm phần trăm thì **dừng và báo**: định nghĩa "câu" đang khác bản bàn giao.
- [ ] **Step 5: Ghi nhận** ba số của bộ cũ (lặp câu, MTLD, distinct-2) vào `docs/tien-do-21-11-2026.md` làm mốc so sánh.

### Task B2: Tìm nguồn của câu lặp

**Files:**
- Create: `tools/nguon_lap_cau.py`
- Output: `docs/do-lap-cau-nguon.md` (do chương trình sinh)

**Interfaces:**
- Consumes: `do_lap_cau` (Task B1) và các nhóm câu trong `src/ngu_lieu_viet.py` (`MO_DAU`, `MO_DAU_NGUOI_NHA`, `HOI_THOI_GIAN`, `HOI_THEM`, `HOI_TIEN_SU`, `HOI_GIA_DINH`, `HOI_DI_UNG`, `HOI_THUOC`, `XA_GIAO`, `CHUYEN_KHAM`, `DAN_DO`, `BAC_SI_TIEP_LOI`).
- Produces: `phan_loai_nguon(cau: str) -> str` trả tên nhóm câu mà `cau` khớp (hoặc `"khac"`), và bảng tỷ trọng câu lặp theo nhóm.

- [ ] **Step 1: Viết phép thử `test_phan_loai_nguon`:** một câu lấy từ `ngu_lieu_viet.MO_DAU[0]` (sau khi chuẩn hoá giống `tach_cau`) → `"MO_DAU"`; câu bịa không thuộc nhóm nào → `"khac"`.
- [ ] **Step 2: Chạy, xác nhận thất bại.**
- [ ] **Step 3: Cài `phan_loai_nguon` và phần in bảng.** Với mỗi câu lặp trong 5.000 ca, tính phần trăm tổng số câu lặp theo nhóm.
- [ ] **Step 4: Chạy trên bộ cũ.** Mong đợi bảng có tổng phần trăm 100% và các nhóm đứng đầu. Quyết định nhóm nào cần mở rộng ở Task B3 dựa trên bảng này, không đoán.
- [ ] **Step 5: Ghi nhận.**

### Task B3: Mở rộng các nhóm câu theo tổ hợp

**Files:**
- Modify: `src/ngu_lieu_viet.py` (các nhóm đứng đầu bảng ở Task B2)
- Modify: `src/sinh_hoi_thoai_viet.py` (chỗ chọn câu từ nhóm, trong `sinh_hoi_thoai` quanh dòng 787–1263)
- Test: `tests/test_mo_rong_bo_du_lieu.py`, `tests/test_bien_the_khong_doi_nhan.py` (mới)

**Interfaces:**
- Consumes: bảng nguồn lặp (Task B2).
- Produces: mỗi nhóm đứng đầu có thêm biến thể; việc chọn biến thể độc lập với việc chọn mệnh đề, nên cùng một khuôn bệnh ra nhiều cách nói. Hàm sinh giữ nguyên chữ ký `sinh_bo(so_ca: int, seed: int = 42) -> List[dict]`.

- [ ] **Step 1: Viết hai phép thử trong `tests/test_bien_the_khong_doi_nhan.py`**, sinh 500 ca bằng `sinh_bo(500, seed=7)`:
  - `test_trich_dan_la_chuoi_con_cua_input`: với mọi ca, mọi chuỗi trong `dap_an[i]["trich_dan"]` là chuỗi con nguyên văn của `ca["input"]`.
  - `test_moi_menh_de_co_du_truong_nhan`: mọi phần tử `dap_an` có đủ các khoá mà `_dap_an` trong `src/sinh_hoi_thoai_viet.py:1568` hiện sinh ra (lấy danh sách khoá từ một ca sinh bằng mã hiện tại trước khi sửa, ghi vào phép thử).
  Hai phép thử này phải PASS **trước** khi sửa (đường cơ sở) và **sau** khi sửa.
- [ ] **Step 2: Chạy trước khi sửa mã, mong đợi PASS (đường cơ sở).** Nếu không PASS thì bộ sinh hiện tại đã lệch, **dừng và báo**. Nếu thấy việc thêm biến thể buộc phải đổi lược đồ đáp án, **dừng và hỏi**.
- [ ] **Step 3: Thêm biến thể vào các nhóm đứng đầu** (khẩu ngữ, cách nói vùng miền, người nhà kể hộ, thứ tự lượt) và đổi chỗ chọn câu để lấy tổ hợp. Mỗi nhóm đứng đầu có thêm tối thiểu 8 biến thể mới, viết tay, không do mô hình sinh.
- [ ] **Step 4: Chạy `pytest tests/test_mo_rong_bo_du_lieu.py tests/test_bien_the_khong_doi_nhan.py -q`.** Mong đợi PASS, kể cả `test_du_200_khuon`.
- [ ] **Step 5: Đo.** Sinh 1.000 ca bằng seed mới vào tệp tạm trong thư mục scratchpad, chạy `do_lap_cau`. Ghi `ty_le_lap`. Lặp tối đa **hai vòng** B2 → B3. Nếu `ty_le_lap > 0.40` sau hai vòng, **dừng và báo**, không tự tiếp tục.
- [ ] **Step 6: Ghi nhận** số trước và sau.

### Task B4: Sinh bộ v2, manifest v2, kiểm không trùng bộ cũ

**Files:**
- Create: `tools/xuat_manifest_v2.py`
- Output: `data/hoi_thoai_viet_v2.jsonl`, `data-rieng-tu/ket-qua/manifest/dong-bang-v2.json`, `data/v2_mau_duyet.md`
- Test: `tests/test_manifest_v2.py`

**Interfaces:**
- Consumes: `python -m src.sinh_hoi_thoai_viet --so-ca 5000 --seed <số mới> --ra hoi_thoai_viet_v2.jsonl` (tham số `--ra` là tên tệp trong `data/`), `src.ngu_lieu_viet.be_theo_tap` hoặc `tap_cua_ca` để chia theo khuôn.
- Produces: dòng lệnh `python tools/xuat_manifest_v2.py --tep <tên tệp trong data/> --ten <tên manifest>` (dùng lại ở Task F5 với `--ten dong-bang-v2-mo-rong`); và `tao_manifest(cac_ca: list[dict], ma_bo_cu: set[str], van_ban_bo_cu: set[str]) -> dict` với khoá `"so_ca"`, `"tap"` (số ca theo train/phát triển/kiểm tra), `"ma_bam"` (SHA-256 của danh sách mã ca), `"trung_ma_bo_cu"`, `"trung_van_ban_bo_cu"`.

- [ ] **Step 1: Viết phép thử:**
  - `test_khong_trung_ma_va_van_ban_bo_cu`: manifest v2 có `trung_ma_bo_cu == 0` và `trung_van_ban_bo_cu == 0`.
  - `test_manifest_ma_bam_on_dinh`: gọi hai lần cho cùng đầu vào ra cùng `ma_bam`.
  - `test_khuon_khong_nam_hai_tap`: không khuôn bệnh nào xuất hiện ở hai tập.
- [ ] **Step 2: Chạy, xác nhận thất bại.**
- [ ] **Step 3: Cài `tao_manifest` và phần ghi tệp.** Tệp manifest bộ cũ chỉ đọc, không ghi.
- [ ] **Step 4: Sinh `data/hoi_thoai_viet_v2.jsonl`** (5.000 ca, seed khác 42). Chạy `do_lap_cau`: mong đợi `ty_le_lap <= 0.30` (mục tiêu người dùng đặt lại ngày 21/11/2026, trước đó 0,20). Nếu cao hơn, ghi số thật, không chỉnh ngưỡng.
- [ ] **Step 5: Xuất `data/v2_mau_duyet.md`:** 50 ca ngẫu nhiên, mỗi khuôn tối đa 3 ca, để bạn đọc kiểm câu vô nghĩa.
- [ ] **Step 6: Chạy toàn bộ `pytest tests/ -q`.** Mong đợi không phép thử cũ nào hỏng.
- [ ] **Step 7: Ghi nhận.** Nhắc rõ: huấn luyện trên v2 là lần chạy mới (`--hau-to=-v3`), không tiếp tục từ checkpoint-100.

### Task B5: Ghép đoạn hội thoại VietMed

**Files:**
- Create: `src/nap_vietmed.py`
- Test: `tests/test_nap_vietmed.py`

**Interfaces:**
- Produces:
  - `doc_chep_loi(duong_dan: str) -> list[dict]`: tệp `*_transcript.txt` của VietMed là danh sách kiểu từ điển Python (nháy đơn, **không phải JSON**), nên đọc bằng `ast.literal_eval`. Mỗi phần tử có `text`, `speaker_name`, `file`, `duration`.
  - `ghep_doan(dong: list[dict], toi_da_ky_tu: int = 6000) -> list[dict]`: gom các dòng liên tiếp cùng `speaker_name` gốc (bỏ hậu tố `_a`, `_b`) thành đoạn, mỗi đoạn `{"id": str, "van_ban": str, "so_dong": int}`, cắt khi vượt `toi_da_ky_tu`.

- [ ] **Step 1: Viết phép thử:**
  - `test_doc_chep_loi_nhay_don`: chuỗi `"[\n{'text': 'ho ba ngày', 'speaker_name': 'VietMed_007_a', 'file': 'VietMed_007/1.ogg', 'duration': 5.0},\n]"` → trả một phần tử có `text == "ho ba ngày"`.
  - `test_ghep_cung_nguoi_noi`: ba dòng cùng `VietMed_007_a` → một đoạn `so_dong == 3`.
  - `test_cat_khi_qua_dai`: nhiều dòng tổng vượt `toi_da_ky_tu` → ít nhất hai đoạn, không đoạn nào vượt giới hạn.
  - `test_tep_hong_khong_dung_gia_tri_la`: nội dung không phải danh sách hợp lệ → ném `ValueError` rõ ràng, không thực thi mã.
- [ ] **Step 2: Chạy, xác nhận thất bại.**
- [ ] **Step 3: Cài hai hàm** dùng `ast.literal_eval` (không dùng `eval`).
- [ ] **Step 4: Chạy lại, PASS.** Chạy thử trên `D:\Claude\data-rieng-tu\du-lieu-ngoai\VietMed\labeled_medical_data\train_transcript.txt` (2.775 dòng), in số đoạn. Chỉ đọc, không ghi vào thư mục dữ liệu ngoài.
- [ ] **Step 5: Ghi nhận** số đoạn và ghi chú: đoạn này chưa có nhãn mệnh đề; dùng làm bộ đánh giá hoặc gán nhãn sau (chờ quyết định về người hoặc máy gán nhãn).

---

## Luồng F — Thêm khuôn bệnh, tình huống và kịch bản mới

Thuật ngữ dùng trong luồng này (theo mã hiện có): **khuôn** là một bệnh trong `ngu_lieu_viet.BENH` (hiện 200). **Tình huống** là bối cảnh buổi khám trong `BOI_CANH` (hiện 5: khám lần đầu, tái khám, chờ kết quả, người nhà thay mặt, điều dưỡng bàn giao). **Kịch bản** là "bẫy" trong `BAY` (hiện 14, ví dụ đính chính, mâu thuẫn, người nhà kể hộ).

### Task F0: Phép thử vàng cho bộ sinh cũ

**Files:**
- Test: `tests/test_bo_sinh_goc_khong_doi.py`

**Interfaces:**
- Produces: hai phép thử mà mọi tác vụ F và B3 phải giữ PASS.

- [ ] **Step 1: Chạy hai lần liên tiếp** `sinh_bo(200, seed=42)`, tính `hashlib.sha256(json.dumps(bo, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()`. Hai lần phải ra cùng giá trị (nếu không thì bộ sinh không tất định, **dừng và báo**). In giá trị ra rồi dán nguyên văn vào phép thử.
- [ ] **Step 2: Viết `test_sinh_bo_seed_42_khong_doi`** (so băm với giá trị đã dán) và **`test_chia_khuon_200_khong_doi`** (`tach_tap_viet.phan_khuon([b["ten"] for b in nl.BENH])` có đúng 150/26/24 khuôn, và danh sách đã sắp xếp của hai tập phát triển và kiểm tra khớp danh sách đã dán, 50 tên).
- [ ] **Step 3: Chạy, mong đợi PASS** (đường cơ sở, chưa sửa gì). Chạy cả `pytest tests/test_mo_rong_bo_du_lieu.py -q`.
- [ ] **Step 4: Ghi nhận** hai giá trị vàng và ngày chụp vào `docs/tien-do-21-11-2026.md`.

### Task F1: Khuôn bệnh mở rộng, hai đợt 200 khuôn mới, tới 600 khuôn cả thảy, chưa duyệt

**Mục tiêu người dùng (21/11/2026): tổng 600 khuôn (200 khuôn cũ + 400 khuôn mới), làm trong ba đợt 200 khuôn, và mục tiêu đi kèm là ĐA DẠNG LOẠI BỆNH hơn, giảm lặp, tỷ lệ lặp mọi câu ≤ 30%.** Đợt 1 là 200 khuôn đã có (`nl.BENH`, không đổi). **Đợt 2 và đợt 3 là hai đợt viết mới, mỗi đợt 200 khuôn** (khuôn 201–400 và 401–600). *Cách hiểu này suy từ "mỗi đợt 200 khuôn, tổng 3 đợt 600 khuôn" và "tăng lên 500–600 khuôn" trước đó; nếu ý là 3 đợt mới (thêm 600, tổng 800) thì đổi lại.* Mỗi đợt có cổng riêng: người dùng duyệt danh sách tên cả đợt, rồi viết nội dung **theo lô 50 khuôn**, người dùng đọc mẫu sau mỗi lô 50 (để một đợt 200 khuôn không dồn cả công duyệt vào một lần), cuối đợt người dùng chốt rồi mới sang đợt sau. Đã có 50 tên đề xuất (`docs/khuon-mo-rong-danh-sach.md`) làm lô đầu của đợt 2; **150 tên còn lại của đợt 2 và 200 tên của đợt 3 chưa có**, người nhận việc đề xuất từng lô sau khi lô trước được duyệt. Không viết trước cả 400 khuôn vì nội dung y khoa AI viết chưa có người duyệt.

**Files:**
- Create: `src/khuon_mo_rong.py`, `docs/khuon-mo-rong-danh-sach.md`, `docs/khuon-mo-rong-mau-duyet.md`
- Test: `tests/test_khuon_mo_rong.py`

**Interfaces:**
- Produces: `khuon_mo_rong.DOT: dict[int, list[dict]]` (khoá là số đợt mới, 1 và 2, mỗi đợt đúng 200 phần tử; "đợt 1" ở đây là khuôn 201–400, "đợt 2" là khuôn 401–600); `khuon_mo_rong.BENH_MO_RONG: list[dict]` (nối các đợt đã có, cùng khoá với `ngu_lieu_viet.BENH`: `ten`, `nhom`, `dien_tien`, `chinh`, `phu`, `kham`, `chan_doan`, `ke_hoach`, thêm `da_duyet: bool` và `he_co_quan: str`, tên hệ cơ quan hoặc nhóm bệnh, ví dụ "hô hấp", "tiêu hoá", "da liễu", "chấn thương", "nhiễm trùng", "sản phụ khoa"); `khuon_mo_rong.TEN: frozenset[str]`; `khuon_mo_rong.TEN_THEO_DOT: dict[int, frozenset[str]]`. Không thêm vào `nl.BENH`, để `test_du_200_khuon` còn đúng.

- [ ] **Step 1: Lập bảng khoảng trống.** In tên, nhóm (`nhi`/`người lớn`/`cả hai`), diễn tiến của 200 khuôn hiện có; nhóm theo hệ cơ quan; ghi vào `docs/khuon-mo-rong-danh-sach.md` danh sách **tên khuôn đề xuất cho lô 50 đang làm** nhằm lấp khoảng trống (hệ cơ quan ít đại diện, nhi khoa, bệnh mạn tính cần dùng nhiều thuốc, bệnh cần chờ kết quả xét nghiệm). **Dừng tại đây để bạn duyệt danh sách tên** trước khi viết nội dung.
- [ ] **Step 2: Viết `tests/test_khuon_mo_rong.py`:** `test_moi_dot_du_200_khuon`; `test_tong_khuon_bang_200_nhan_so_dot`; `test_ten_khong_trung_nhau_va_khong_trung_200_cu`; `test_du_truong` (mọi khoá bắt buộc không rỗng); `test_nhi_it_nhat_15_phan_tram_moi_dot` (tối thiểu 30 khuôn nhi mỗi đợt 200, theo tỷ lệ 15,5% của 200 khuôn cũ); `test_da_dang_he_co_quan` (xem dưới); `test_tat_ca_chua_duyet` (`da_duyet is False` ở mọi khuôn, trừ khi người dùng đổi sau khi bác sĩ duyệt).
  `test_da_dang_he_co_quan`: trên toàn bộ khuôn đã viết (200 cũ + các đợt mới, gán `he_co_quan` cho 200 cũ bằng một bảng ánh xạ viết trong `khuon_mo_rong.py`), **không hệ nào chiếm quá 12% tổng số khuôn**, và có ít nhất 18 hệ khác nhau. Mỗi đợt mới phải làm giảm hoặc giữ nguyên chỉ số "hệ lớn nhất chiếm bao nhiêu phần trăm", không làm tăng. Báo cáo bảng số khuôn theo hệ sau mỗi đợt vào `docs/khuon-mo-rong-phan-bo.md` (do chương trình in).
- [ ] **Step 3: Chạy, xác nhận thất bại.**
- [ ] **Step 4: Viết nội dung khuôn của lô 50 đang làm theo từng lô nhỏ 10**, đúng mẫu của `BENH` (3 triệu chứng chính, 3 phụ, một câu khám, một câu chẩn đoán, một câu kế hoạch). Sau mỗi lô cập nhật `docs/khuon-mo-rong-mau-duyet.md` để bạn hoặc bác sĩ đọc. Nội dung do AI viết, ghi rõ "chưa được bác sĩ duyệt" ở đầu tệp (quyết định D1 còn mở).
- [ ] **Step 5: Chạy lại, PASS.** Chạy cả `pytest tests/ -q -k "khuon or benh"`.
- [ ] **Step 6: Ghi nhận.**

### Task F2: Chia tập không làm đổi 200 khuôn cũ

**Files:**
- Modify: `src/tach_tap_viet.py:50-85` (`phan_khuon`), `src/sinh_hoi_thoai_viet.py:1289-1305` (`bang_tap_khuon`, `tap_cua_ca`)
- Test: `tests/test_chia_khuon_mo_rong.py`

**Interfaces:**
- Consumes: `khuon_mo_rong.TEN` (Task F1), phép thử vàng (Task F0).
- Produces: hằng `tach_tap_viet.TY_LE_MO_RONG_PHAT_TRIEN = 0.10`, `TY_LE_MO_RONG_KIEM_TRA = 0.10`. `phan_khuon` giữ nguyên chữ ký; **mỗi đợt 200 khuôn là một nhóm riêng, chia độc lập** (160/20/20), để thêm đợt sau không làm đổi tập của các đợt trước (nếu gộp mọi đợt thành một nhóm và xếp hạng bằng băm thì thêm đợt sẽ làm khuôn đã vào tập huấn luyện nhảy sang kiểm tra). Nhóm `k_moi` (hiện là mọi khuôn ngoài 100 khuôn đầu) loại các tên này. `bang_tap_khuon(mo_rong: bool = False) -> dict[str, str]`.

- [ ] **Step 1: Viết phép thử:**
  - `test_200_khuon_cu_khong_doi_khi_them_50`: `phan_khuon(200 tên + 200 tên đợt 1)` cho 200 khuôn cũ **đúng tập** như `phan_khuon(200 tên)` (so từng khuôn).
  - `test_dot_truoc_khong_doi_khi_them_dot_sau`: tập của 200 khuôn đợt 1 giống hệt dù đầu vào có thêm đợt 2.
  - `test_nhom_mo_rong_chia_160_20_20`.
  - `test_khong_khuon_nao_o_hai_tap`.
  - `test_mac_dinh_khong_doi`: `bang_tap_khuon()` (không cờ) bằng giá trị vàng ở F0.
- [ ] **Step 2: Chạy, xác nhận thất bại** (hiện các tên mới sẽ xáo lại nhóm `k_moi`).
- [ ] **Step 3: Sửa `phan_khuon` thêm nhóm thứ ba và `bang_tap_khuon(mo_rong)`.** Khi không có tên mở rộng trong đầu vào, mã chạy đúng nhánh cũ.
- [ ] **Step 4: Chạy lại cùng `tests/test_bo_sinh_goc_khong_doi.py` và `tests/test_mo_rong_bo_du_lieu.py`.** Mong đợi PASS cả ba.
- [ ] **Step 5: Ghi nhận.**

### Task F3: Ba tình huống (bối cảnh) mới

**Files:**
- Modify: `src/ngu_lieu_viet.py` (thêm `BOI_CANH_MO_RONG`, trọng số), `src/sinh_hoi_thoai_viet.py` (`TuyChon`, `sinh_ca`, `sinh_hoi_thoai`, `sinh_bo`)
- Test: `tests/test_boi_canh_mo_rong.py`

**Interfaces:**
- Produces: `ngu_lieu_viet.BOI_CANH_MO_RONG = ("tu_van_qua_dien_thoai", "chuyen_tuyen", "kham_dinh_ky")`; `TuyChon.boi_canh_mo_rong: bool = False`; `sinh_bo(so_ca: int, seed: int = 42, mo_rong: bool = False) -> List[dict]`. Tắt cờ thì đường rút số của `rng` phải y hệt cũ (xem lời nhắc ở đầu `TuyChon`).

- [ ] **Step 1: Đọc cách `cho_ket_qua` (bỏ mục chẩn đoán) và `nguoi_nha_thay_mat` được cài trong `sinh_hoi_thoai`; ghi vào ghi chú tiến độ nơi cần chèn. Rồi chốt nghĩa nhãn với bạn trước khi viết mã:**
  - `tu_van_qua_dien_thoai`: không có mục khám thực thể; bác sĩ dặn đến khám trực tiếp khi có dấu hiệu nặng.
  - `chuyen_tuyen`: bệnh nhân mang giấy chuyển và kết quả của nơi khác; thông tin đó có `thoi_gian_su_kien = "quá khứ"` và nguồn là giấy, không phải lời bệnh nhân.
  - `kham_dinh_ky`: không có triệu chứng chính; bệnh nhân nói không có gì bất thường (`phu_dinh = True`, `do_chac_chan = "chắc chắn"`); tiền sử nhiều hơn bình thường.
  **Không tự đặt nghĩa nhãn nếu bạn chưa xác nhận.**
- [ ] **Step 2: Viết phép thử:**
  - `test_tat_co_thi_bo_cu_khong_doi` (băm vàng F0).
  - `test_ba_boi_canh_xuat_hien`: `sinh_bo(1000, seed=7, mo_rong=True)` có mỗi bối cảnh mới từ 30 ca trở lên.
  - `test_nhan_dung_nghia_tung_boi_canh` (theo ba dòng nghĩa ở Step 1, kiểm trên `dap_an`).
  - `test_trich_dan_la_chuoi_con_cua_input` cho các ca mới.
  - `test_ca_moi_van_dung_luoc_do`: khoá `dap_an` của ca mới bằng khoá của ca cũ.
- [ ] **Step 3: Chạy, xác nhận thất bại.**
- [ ] **Step 4: Cài** bối cảnh mới bám theo mẫu của `cho_ket_qua`; tỷ lệ bối cảnh mới hằng `TY_LE_BOI_CANH_MO_RONG = 0.25` trên các ca khi `mo_rong=True`.
- [ ] **Step 5: Chạy lại cùng `tests/test_bo_sinh_goc_khong_doi.py`, PASS.**
- [ ] **Step 6: Ghi nhận.**

### Task F4: Ba kịch bản (bẫy) mới

**Files:**
- Modify: `src/ngu_lieu_viet.py` (thêm `CODE_SWITCH`), `src/sinh_hoi_thoai_viet.py` (thêm `BAY_MO_RONG`, tách khỏi `BAY` và `BAY_RUT`)
- Test: `tests/test_bay_mo_rong.py`

**Interfaces:**
- Produces: `BAY_MO_RONG = ("dieu_kien_prn", "khong_nho_khong_biet", "code_switch")`, bật bằng `TuyChon.bay_mo_rong: bool = False` và `sinh_bo(..., mo_rong=True)`; `ngu_lieu_viet.CODE_SWITCH: list[tuple[str, str]]` (ít nhất 30 cặp: cách nói thuần Việt, cách nói pha Anh–Việt, ví dụ "xét nghiệm nhanh" ↔ "test nhanh").

- [ ] **Step 1: Đọc cách `hoi_khong_dap` và `lieu_dinh_chinh` được cài (cái sau ghi vào `ca.bay` ngay chỗ xảy ra, trong `_ke_thuoc`). Chốt nghĩa nhãn với bạn:**
  - `dieu_kien_prn`: bác sĩ dặn "nếu sốt trên 38,5 độ thì uống paracetamol" thì mệnh đề thuốc có `tinh_huong = "giả định"` (không bao giờ `"thực tế"`). Cần bạn xác nhận chọn `"giả định"` hay `"kế hoạch"` cho câu điều kiện.
  - `khong_nho_khong_biet`: người nói "không nhớ" hoặc "không rõ" có dị ứng hay không thì `do_chac_chan = "chưa ghi nhận"` và `phu_dinh = False` (khác "không dị ứng").
  - `code_switch`: chỉ đổi chữ (thuật ngữ pha Anh–Việt), mọi nhãn giữ nguyên.
- [ ] **Step 2: Viết phép thử** với `sinh_bo(5000, seed=7, mo_rong=True)`:
  - `test_tat_co_thi_bo_cu_khong_doi` (băm vàng F0).
  - `test_moi_bay_co_it_nhat_300_menh_de`.
  - `test_dieu_kien_prn_khong_bao_gio_thuc_te`.
  - `test_khong_nho_la_chua_ghi_nhan_khong_phai_phu_dinh`.
  - `test_code_switch_giu_nguyen_nhan`: ca có `code_switch` có `dap_an` (trừ `noi_dung` và `trich_dan`) giống ca cùng khuôn không có bẫy.
  - `test_trich_dan_la_chuoi_con_cua_input`.
- [ ] **Step 3: Chạy, xác nhận thất bại.**
- [ ] **Step 4: Cài ba bẫy**, mỗi bẫy bật riêng với tỷ lệ hằng số riêng (như `TY_LE_LIEU_DINH_CHINH`), không đưa vào `BAY_RUT` để không làm loãng tỷ lệ các bẫy cũ.
- [ ] **Step 5: Chạy lại cùng `tests/test_bo_sinh_goc_khong_doi.py` và `tests/test_mo_rong_bo_du_lieu.py`.** Mong đợi PASS.
- [ ] **Step 6: Ghi nhận.**

### Task F5: Sinh bộ v2 mở rộng

**Files:**
- Modify: `src/sinh_hoi_thoai_viet.py` (`main`: thêm cờ `--mo-rong`)
- Output: `data/hoi_thoai_viet_v2_mo_rong.jsonl`, `data-rieng-tu/ket-qua/manifest/dong-bang-v2-mo-rong.json`, `data/v2_mo_rong_mau_duyet.md`
- Test: `tests/test_manifest_v2.py` (mở rộng, dùng chung với Task B4)

**Interfaces:**
- Consumes: Task B3 (nhóm câu đa dạng), F1–F4, `tools/xuat_manifest_v2.py` (Task B4, thêm đối số `--ten`), kho cách nói ngoài `data/cum_trieu_chung_ngoai.json` nếu đã có (Task E2).
- Produces: lệnh `python -m src.sinh_hoi_thoai_viet --so-ca 5000 --seed 2611 --mo-rong --ra hoi_thoai_viet_v2_mo_rong.jsonl`.

- [ ] **Step 1: Viết `test_phan_bo_v2_mo_rong`:** trên tệp đã sinh, mỗi bối cảnh mới ≥ 150 ca, mỗi bẫy mới ≥ 300 mệnh đề, mỗi khuôn mở rộng ≥ 4 ca (5.000 ca chia 600 khuôn, trung bình 8,3 ca mỗi khuôn), và không ca nào thuộc khuôn mở rộng nằm ở tập cũ (kiểm bằng `bang_tap_khuon(mo_rong=True)`). Đánh dấu `skipif` khi chưa có tệp.
- [ ] **Step 2: Thêm cờ `--mo-rong` vào `main`.** Cờ bật thì truyền `mo_rong=True` cho `sinh_bo` và dùng `bang_tap_khuon(mo_rong=True)`.
- [ ] **Step 3 (cần bạn duyệt danh sách khuôn ở F1 và nghĩa nhãn ở F3, F4): sinh 5.000 ca**, chạy `do_lap_cau` (Task B1) và `tao_manifest`. Ghi `ty_le_lap` thật (mục tiêu 0,30, không chỉnh ngưỡng nếu chưa đạt).
- [ ] **Step 4: Xuất `data/v2_mo_rong_mau_duyet.md`:** 50 ca, thêm 10 ca cho mỗi tình huống và kịch bản mới, để bạn đọc.
- [ ] **Step 5: Chạy toàn bộ `pytest tests/ -q`, PASS.**
- [ ] **Step 6: Ghi nhận.** Huấn luyện trên bộ này là lần chạy mới (`--hau-to=-v3`), không tiếp tục từ checkpoint-100.

---

## Luồng E — Huấn luyện thêm bằng dữ liệu ngoài (có kiểm soát)

Vì sao cần các bước lọc: ba bộ ngoài không có nhãn mệnh đề kiểu của dự án (nội dung, chủ thể, phủ định, thời gian, thuốc, trích dẫn). Nhãn phải do máy gán trước. Nhãn máy có thể sai và không ai kiểm lại, nên luồng này (1) chỉ lấy mệnh đề qua được các phép kiểm tự động, (2) giới hạn bộ ngoại ở 20% dữ liệu trộn, (3) đo trên đoạn thật bằng các chỉ số không cần nhãn, và (4) giữ bộ ngoại ngoài mọi tập đã đóng băng.

### Task E0: Môi trường đọc parquet và xlsx

**Files:**
- Không có mã. Ghi kết quả vào `docs/tien-do-21-11-2026.md`.

**Interfaces:**
- Produces: một môi trường Python có `pyarrow` (đọc `.parquet`) và `openpyxl` (đọc `.xlsx`), không phải hai môi trường đã khoá.

- [ ] **Step 1: Kiểm tra có sẵn không.** Trên laptop, `D:\khkt-venv-lap` đã biết **thiếu** `pyarrow` và `pandas`. Chạy `python -c "import pyarrow, openpyxl"` trên môi trường của HoaiĐức (`C:\Users\hapur\khkt-venv`) chỉ để đọc; không cài.
- [ ] **Step 2 (cần bạn duyệt tải): nếu cả hai nơi đều thiếu, tạo môi trường riêng `D:\venv-doc-du-lieu`** chỉ gồm `pyarrow` và `openpyxl` từ PyPI. Báo tên gói, phiên bản, dung lượng thực tế trước khi tải. Ổ D của laptop chỉ còn khoảng 1,3 GB trống, nên nếu không đủ thì tạo trên HoaiĐức ở ổ C.
- [ ] **Step 3: Kiểm tra:** `python -c "import pyarrow.parquet as pq; print(pq.ParquetFile(r'D:\Claude\data-rieng-tu\du-lieu-ngoai\vietnamese-medical-qa\data\train-00000-of-00001.parquet').schema_arrow)"` in ra danh sách cột.

### Task E1: Xem cấu trúc ba bộ ngoài

**Files:**
- Create: `tools/xem_cau_truc_du_lieu_ngoai.py`
- Output: `docs/du-lieu-ngoai-cau-truc.md`
- Test: `tests/test_xem_cau_truc_du_lieu_ngoai.py`

**Interfaces:**
- Consumes: môi trường Task E0.
- Produces: `mo_ta(duong_dan: str, so_mau: int = 3, toi_da_ky_tu: int = 200) -> dict` với khoá `"dinh_dang"`, `"so_dong"`, `"cot"`, `"mau"`. Hỗ trợ `.parquet`, `.xlsx`, và `*_transcript.txt` của VietMed (danh sách kiểu từ điển Python, nháy đơn, không phải JSON).

- [ ] **Step 1: Viết phép thử** trên tệp tạm: `test_mo_ta_transcript_vietmed` (dùng `ast.literal_eval`; hai dòng mẫu trả `so_dong == 2` và `cot` chứa `text`, `speaker_name`, `file`, `duration`); `test_mo_ta_cat_mau_dai` (mẫu dài hơn `toi_da_ky_tu` bị cắt); `test_tep_hong_nem_ValueError`. Phép thử parquet và xlsx dùng `pytest.importorskip("pyarrow")` và `importorskip("openpyxl")`.
- [ ] **Step 2: Chạy, xác nhận thất bại.**
- [ ] **Step 3: Cài `mo_ta`** (không dùng `eval`) và phần ghi `docs/du-lieu-ngoai-cau-truc.md`.
- [ ] **Step 4: Chạy trên cả ba bộ.** Đọc kết quả và ghi vào cuối tài liệu ba câu trả lời: (a) `Metadata_labeled_medical.xlsx` có cột vai người nói (bác sĩ, bệnh nhân…) không; (b) các tập `*_full_dialogue` của VietMed-Sum có phải chép lời gốc của VietMed không; (c) cột nào của `vietnamese-medical-qa` là câu hỏi của bệnh nhân. **Nếu (a) không có vai thì dừng và hỏi** (Task E3 cần vai).
- [ ] **Step 5: Ghi nhận.**

### Task E2: Kho cách nói triệu chứng từ hỏi đáp (chỉ làm vốn từ cho bộ sinh)

**Files:**
- Create: `src/cum_tu_ngoai.py`
- Output: `data/cum_trieu_chung_ngoai.json`, `docs/cum-mau-duyet.md`
- Test: `tests/test_cum_tu_ngoai.py`

**Interfaces:**
- Produces: `trich_cum_trieu_chung(cac_cau_hoi: list[str], tu_khoa: set[str], toi_da_tu: int = 12) -> list[str]`. Trả các câu ngắn (không quá `toi_da_tu` từ) chứa ít nhất một từ khoá triệu chứng, đã chuẩn hoá NFC, hạ chữ thường, bỏ trùng, và **bỏ mọi câu chứa số điện thoại, email, địa chỉ, tên riêng đi kèm "tôi tên"**.
- Đầu vào `tu_khoa`: gộp mọi chuỗi trong `chinh` và `phu` của `nl.BENH` và `khuon_mo_rong.BENH_MO_RONG`.

- [ ] **Step 1: Viết phép thử:**
  - `test_chi_giu_cau_ngan_co_tu_khoa`.
  - `test_bo_cau_co_so_dien_thoai_va_email`: câu có chuỗi 10 chữ số liền hoặc có `@` bị loại.
  - `test_nfc_nfd_la_mot_cau`.
  - `test_bo_trung`.
- [ ] **Step 2: Chạy, xác nhận thất bại.**
- [ ] **Step 3: Cài hàm; chạy trên cột câu hỏi (cột xác định ở E1);** ghi `data/cum_trieu_chung_ngoai.json` và `docs/cum-mau-duyet.md` (100 câu ngẫu nhiên để bạn đọc kiểm).
- [ ] **Step 4: Nối vào bộ sinh sau cờ `mo_rong`:** nhóm `CACH_NOI_NGOAI` chỉ được nạp khi `mo_rong=True` và tệp JSON tồn tại; thêm `test_tat_co_thi_bo_cu_khong_doi` (băm vàng F0).
- [ ] **Step 5: Ghi nhận.** Kho này chỉ làm vốn từ cho bộ sinh luật, không phải mẫu huấn luyện trực tiếp.

### Task E3: Chọn đoạn hội thoại thật của VietMed

**Files:**
- Create: `src/nap_vietmed.py` (bổ sung cho Task B5), `tools/chon_doan_vietmed.py`
- Test: `tests/test_chon_doan_vietmed.py`
- Output: `data/vietmed_doan_da_chon.jsonl`

**Interfaces:**
- Consumes: `doc_chep_loi`, `ghep_doan` (Task B5), bảng vai người nói từ `Metadata_labeled_medical.xlsx` (Task E1).
- Produces: `chon_doan_hoi_thoai(doan: list[dict], vai_theo_nguoi_noi: dict[str, str], toi_thieu_ky_tu: int = 400, toi_da_ky_tu: int = 6000) -> list[dict]`. Giữ đoạn có ít nhất một lời của bệnh nhân và ít nhất một của bác sĩ, độ dài trong khoảng cho phép, và dựng `input` dạng mỗi dòng một lượt với tiền tố `Bác sĩ:` hoặc `Bệnh nhân:` như bộ sinh.

- [ ] **Step 1: Viết phép thử:** `test_bo_doc_thoai_mot_nguoi_noi` (một vai → loại); `test_giu_doan_co_bac_si_va_benh_nhan`; `test_input_co_tien_to_vai`; `test_doan_qua_ngan_hoac_qua_dai_bi_loai`; `test_khong_co_vai_trong_bang_thi_bo` (người nói không có trong bảng vai → loại, không đoán).
- [ ] **Step 2: Chạy, xác nhận thất bại.**
- [ ] **Step 3: Cài `chon_doan_hoi_thoai`** và công cụ dòng lệnh (chỉ đọc thư mục dữ liệu ngoài, chỉ ghi `data/vietmed_doan_da_chon.jsonl`).
- [ ] **Step 4: Chạy trên tập `train` của VietMed.** In số đoạn trước và sau khi chọn. **Nếu sau khi chọn còn dưới 100 đoạn thì dừng và báo**: luồng E không đủ dữ liệu để có ý nghĩa.
- [ ] **Step 5: Loại các đoạn đã dùng cho thí nghiệm ASR** (theo báo cáo rò rỉ ở `data-rieng-tu/ket-qua/kiem-ro-ri/`), ghi số đoạn bị loại.
- [ ] **Step 6: Ghi nhận.**

### Task E4: Gán nhãn trước bằng chính mô hình của dự án và lọc tự động

**Files:**
- Create: `tools/gan_nhan_truoc.py`
- Test: `tests/test_gan_nhan_truoc.py`
- Output: `data/trich_ngoai_nhan_may.jsonl`

**Interfaces:**
- Consumes: `data/vietmed_doan_da_chon.jsonl` (Task E3), hai checkpoint adapter từ Task A4 (checkpoint-100 và mới nhất), `src.do_trich.ghep(dap_an, trich, nguong)`, các phép kiểm trong `src/khoa_bang_chung.py` (đọc chữ ký ở Step 1).
- Produces:
  - `loc_menh_de_may(menh_de: list[dict], van_ban: str) -> tuple[list[dict], list[dict]]` trả `(giu, bo)`, mỗi phần tử của `bo` thêm khoá `"ly_do"`. Giữ khi: có đủ khoá của `PhatBieu`; mọi chuỗi trong `trich_dan` là chuỗi con nguyên văn của `van_ban` (sau chuẩn hoá NFC); `chu_the` thuộc giá trị hợp lệ; không trùng mệnh đề khác trong cùng đoạn.
  - `dong_thuan_giua_hai_checkpoint(a: list[dict], b: list[dict], nguong: float = 0.8) -> list[dict]`: chỉ giữ mệnh đề của `a` ghép được (qua `ghep`) với một mệnh đề của `b` ở mức giống ≥ `nguong` **và cùng `chu_the`**.
  - Mỗi bản ghi đầu ra: `{"input", "dap_an", "nguon": "vietmed", "nhan": "may-chua-kiem"}`.

- [ ] **Step 1: Đọc chữ ký các phép kiểm trong `src/khoa_bang_chung.py`;** ghi vào ghi chú tiến độ phép kiểm nào dùng được trực tiếp cho `loc_menh_de_may`.
- [ ] **Step 2: Viết phép thử:**
  - `test_giu_menh_de_co_trich_dan_that` và `test_bo_menh_de_trich_dan_khong_co_trong_van_ban` (ghi `ly_do`).
  - `test_nfc_nfd_trich_dan_van_khop`.
  - `test_bo_chu_the_la`.
  - `test_dong_thuan_chi_giu_cap_cung_chu_the`: hai mệnh đề cùng nội dung nhưng khác chủ thể → không được giữ.
  - `test_ban_ghi_dau_ra_co_the_nguon_va_nhan`.
- [ ] **Step 3: Chạy, xác nhận thất bại.**
- [ ] **Step 4: Cài hai hàm và công cụ dòng lệnh.**
- [ ] **Step 5 (cần bạn duyệt chạy trên HoaiĐức): chạy khâu trích** trên các đoạn đã chọn bằng hai checkpoint, rồi lọc. In: số đoạn, số mệnh đề máy tạo, số bị loại theo từng `ly_do`, số còn lại. Chọn 30 đoạn ngẫu nhiên để bạn đọc nhanh (không gán nhãn, chỉ đọc có hợp lý không) và ghi nhận xét vào `docs/tien-do-21-11-2026.md`.
- [ ] **Step 6: Ghi nhận.**

**Cổng quyết định G1 (không có tác vụ):** dùng mô hình thương mại để gán nhãn thay cho mô hình của dự án chỉ khi bạn đồng ý. Khi đó phải làm trước: sửa quy tắc "dữ liệu do GPT sinh chỉ để đo", ghi vào kê khai AI, kiểm số dư, ước tính chi phí, chọn mô hình rẻ nhất đủ dùng, và báo riêng bộ này trong mọi kết quả. Không chạy trước khi có đồng ý này.

### Task E5: Trộn dữ liệu và huấn luyện ba lần chạy so sánh

**Files:**
- Create: `tools/tron_du_lieu_huan_luyen.py`
- Test: `tests/test_tron_du_lieu_huan_luyen.py`

**Interfaces:**
- Consumes: `data/hoi_thoai_viet_v2_mo_rong.jsonl` (Task F5), `data/trich_ngoai_nhan_may.jsonl` (Task E4), cờ `--tep-train`, `--tep-val`, `--hau-to` của `src/train_baseline.py`.
- Produces: `tron(ca_luat: list[dict], ca_ngoai: list[dict], ty_le_ngoai_toi_da: float = 0.20, seed: int = 2611) -> list[dict]`. Giữ **toàn bộ** `ca_luat`; thêm không quá `ty_le_ngoai_toi_da` của **tổng số sau khi trộn** từ `ca_ngoai`; kết quả tất định theo `seed`.

- [ ] **Step 1: Viết phép thử:** `test_giu_het_ca_luat`; `test_ty_le_ngoai_khong_vuot_20_phan_tram` (ví dụ 800 ca luật, 1000 ca ngoại → số ca ngoại ≤ 200); `test_tat_dinh_theo_seed`; `test_tu_choi_ca_ngoai_thieu_nguon_hoac_nhan` (ném `ValueError`); `test_khong_trung_input_voi_tap_da_dong_bang`: nếu `input` của một ca ngoại trùng văn bản của `data/viet_phat_trien.jsonl` hoặc `data/viet_kiem_tra_cuoi.jsonl` thì bị loại.
- [ ] **Step 2: Chạy, xác nhận thất bại.**
- [ ] **Step 3: Cài `tron`.**
- [ ] **Step 4: Chạy `pytest tests/test_tron_du_lieu_huan_luyen.py -q`, PASS.**
- [ ] **Step 5 (cần bạn duyệt GPU, và duyệt ước tính thời gian lấy từ lần chạy Task A4): ba lần chạy huấn luyện, mỗi lần với hậu tố riêng và dữ liệu có vân tay riêng** (`train_baseline` sẽ từ chối chạy tiếp từ checkpoint cũ):
  - **R0:** bộ v1 (checkpoint-200 của Task A4, không chạy lại).
  - **R1:** `--hau-to=-v3-luat` chỉ với `hoi_thoai_viet_v2_mo_rong` (phần train).
  - **R2:** `--hau-to=-v3-luat-ngoai` với bộ trộn (luật + ngoại, ngoại ≤ 20%).
  Chạy qua `tools/run_capped.py` với `--loss-theo-doan`, trên HoaiĐức.
- [ ] **Step 6: Ghi nhận** đường dẫn checkpoint và loss.

### Task E6: Đo trên đoạn thật không cần nhãn, quyết định có giữ bộ ngoại không

**Files:**
- Create: `tools/do_tren_doan_that.py`
- Test: `tests/test_do_tren_doan_that.py`
- Output: `docs/ket-qua/doan-that-ba-lan-chay.md`

**Interfaces:**
- Consumes: kết quả trích của R0, R1, R2 trên **100 đoạn VietMed giữ riêng, không dùng ở Task E4 và E5**, và `ti_le_bo_sot` (Task A5) trên tập phát triển.
- Produces: `do_tren_doan_that(trich_theo_doan: list[list[dict]], van_ban: list[str]) -> dict` với khoá `"ti_le_json_hop_le"`, `"ti_le_trich_dan_co_that"`, `"ti_le_qua_phep_kiem_can_cu"`, `"so_menh_de_trung_binh"`. Chỉ số không cần nhãn thật.

- [ ] **Step 1: Viết phép thử:** `test_json_hop_le_dem_dung` (một đoạn trả `None` hoặc không phải danh sách → không hợp lệ); `test_trich_dan_co_that_dem_theo_menh_de`; `test_doan_rong_khong_chia_cho_0`; `test_nfc_nfd_trich_dan`.
- [ ] **Step 2: Chạy, xác nhận thất bại.**
- [ ] **Step 3: Cài hàm và bảng so ba lần chạy.**
- [ ] **Step 4 (cần bạn duyệt chạy trên HoaiĐức): chạy khâu trích R0, R1, R2** trên 100 đoạn giữ riêng và trên tập phát triển, in bảng. Quy tắc quyết định (viết trước khi có số, không đổi sau): **bộ ngoại chỉ được giữ nếu R2 không kém R1 ở `ti_le_bo_sot` trên tập phát triển và `ti_le_trich_dan_co_that` trên đoạn thật không giảm.** Ngược lại, loại bộ ngoại và ghi kết quả bất lợi ngang hàng.
- [ ] **Step 5: Ghi nhận.** Báo cáo ghi rõ: nhãn của bộ ngoại do máy gán, chưa ai kiểm; mọi chỉ số trên đoạn thật là chỉ số không cần nhãn, không thay được đo bỏ sót bằng nhãn thật.

### Task E7: Giấy phép và kê khai

**Files:**
- Modify: `docs/nguon-va-giay-phep.md`

- [ ] **Step 1: Thêm ba dòng cho ba bộ đã tải** (bảng mục 1): `hungnm/vietnamese-medical-qa` (Apache 2.0, theo thẻ Hugging Face, kiểm ngày 21/11/2026, dùng làm kho cách nói), VietMed (bản sao chép lời, ba nguồn giấy phép chưa thống nhất, dùng như phi thương mại), VietMed-Sum (loại khỏi huấn luyện, lý do ở bảng).
- [ ] **Step 2: Thêm vào mục 3 ("Chú thích về tính hợp lệ")** một câu: nhãn mệnh đề của dữ liệu ngoài do mô hình của dự án gán, chưa ai kiểm; chỉ chiếm tối đa 20% dữ liệu huấn luyện của lần chạy R2.
- [ ] **Step 3: Kiểm:** `grep -n "vietnamese-medical-qa\|nhãn máy\|may-chua-kiem" docs/nguon-va-giay-phep.md` có kết quả.

---

## Luồng C — Hàng đợi tạo bản nháp bền vững (web)

### Task C1: Mô-đun hàng đợi trên SQLite

**Files:**
- Modify: `web/db/schema.sql` (thêm bảng `viec_nen`)
- Create: `web/may-chu/hang-doi.ts`
- Test: `web/may-chu/hang-doi.test.ts` (chạy bằng `npx tsx web/may-chu/hang-doi.test.ts`, giống `src/lib/*.test.ts`)

**Interfaces:**
- Produces (`hang-doi.ts`), nhận `db: DatabaseSync` để thử bằng `":memory:"`:
  - `taoHangDoi(db: DatabaseSync): HangDoi`
  - `HangDoi.them(nguoiDungId: number, khoaTrung: string, taiTrong: string): number` trả `id`; nếu `khoaTrung` đã có việc chưa kết thúc thì trả `id` đã có.
  - `HangDoi.layViecTiepTheo(): { id: number; taiTrong: string } | null` đánh dấu `dang_chay` trong một giao dịch nguyên tử.
  - `HangDoi.xong(id: number, ketQua: string): void`, `HangDoi.loi(id: number, ma: string): void`.
  - `HangDoi.khoiPhucSauKhoiDong(toiDaLanThu = 2): { chayLai: number; thatBai: number }`.
  - `HangDoi.trangThai(id: number, nguoiDungId: number): { trangThai: string; ketQua?: string; ma?: string } | null` (chỉ trả khi đúng chủ).
- Bảng `viec_nen`: `id INTEGER PRIMARY KEY`, `nguoi_dung_id`, `khoa_trung TEXT`, `tai_trong TEXT`, `trang_thai TEXT` (`cho_chay`, `dang_chay`, `xong`, `that_bai`), `so_lan_thu INTEGER DEFAULT 0`, `ket_qua TEXT`, `ma_loi TEXT`, `tao_luc`, `bat_dau_luc`.

- [ ] **Step 1: Viết phép thử** (dùng `:memory:`):
  - `them_hai_lan_cung_khoa_tra_cung_id`. (Review Focus 5.)
  - `lay_viec_theo_thu_tu_va_chi_mot_nguoi_lay_duoc`: hai lần gọi `layViecTiepTheo` liên tiếp trên một việc → lần hai ra `null`.
  - `khoi_phuc_chay_lai_toi_da_2_lan`: đặt việc `dang_chay` với `so_lan_thu = 1` → thành `cho_chay`, `chayLai == 1`; với `so_lan_thu = 2` → `that_bai` mã `crash_recovery_exhausted`, `thatBai == 1`. (Review Focus 5.)
  - `khong_doc_duoc_viec_cua_nguoi_khac`: `trangThai(id, nguoiDungKhac)` → `null`.
  - `loi_va_xong_doi_trang_thai`.
- [ ] **Step 2: Chạy, xác nhận thất bại** (`npx tsx web/may-chu/hang-doi.test.ts`).
- [ ] **Step 3: Thêm bảng vào `web/db/schema.sql` (`CREATE TABLE IF NOT EXISTS`) và cài `hang-doi.ts`.** Việc lấy tiếp theo dùng `BEGIN IMMEDIATE` + `UPDATE ... WHERE id = (SELECT ... ORDER BY tao_luc LIMIT 1) RETURNING`, cùng kiểu `giaoDich` trong `web/may-chu/csdl.ts:24`.
- [ ] **Step 4: Chạy lại, PASS.** Chạy `npm run lint` trong `web/`, mong đợi không lỗi kiểu.
- [ ] **Step 5: Ghi nhận.**

### Task C2: Nối hàng đợi vào máy chủ

**Files:**
- Modify: `web/server.ts:264-315` (thay `VIEC_NHAP: Map` và `hangDoiNhap: Promise` bằng `HangDoi`)
- Test: `web/may-chu/hang-doi.test.ts` (thêm trường hợp), thử bằng tay trên `npm run dev`

**Interfaces:**
- Consumes: `taoHangDoi`, `HangDoi` (Task C1), `db` từ `web/may-chu/csdl.ts`, hàm `taoBanNhap({ transcript, sessionId, sampleCaseId, branch })` đã có.
- Produces: các điểm cuối hiện có giữ nguyên hình dạng phản hồi (cùng khoá JSON). Khi máy chủ khởi động, gọi `khoiPhucSauKhoiDong()`. Thông báo 404 "máy chủ có thể đã khởi động lại" ở dòng 315 chỉ còn dùng cho `id` không tồn tại.

- [ ] **Step 1: Viết phép thử `moi_viec_con_sau_khi_mo_lai_db`:** tạo hàng đợi trên tệp DB tạm, thêm việc, đóng và mở lại `DatabaseSync` cùng tệp → `trangThai` vẫn trả `cho_chay`.
- [ ] **Step 2: Chạy, xác nhận thất bại hoặc chưa có** (nếu phép thử dùng tệp tạm thì sẽ qua ngay; khi đó ghi rõ phép thử này đã được Task C1 che và bỏ qua bước này).
- [ ] **Step 3: Thay mã ở `web/server.ts`.** Một vòng lặp nền gọi `layViecTiepTheo()` rồi chạy `taoBanNhap`, ghi `xong` hoặc `loi`. Chỉ chạy một việc tại một thời điểm (như `hangDoiNhap` hiện tại, vì GPU chỉ có một).
- [ ] **Step 4: Chạy `npm run lint` và `npx tsx` các phép thử `*.test.ts` trong `web/`.** Mong đợi PASS.
- [ ] **Step 5 (cần bạn đồng ý, chỉ trên laptop, không đụng HoaiĐức): thử bằng tay.** Đặt `MEDITRACE_DB` trỏ tới DB tạm, `PORT=3100 npm run dev`, tạo một bản nháp, tắt máy chủ khi việc còn `dang_chay`, mở lại và kiểm trạng thái chuyển về chạy lại hoặc thất bại có mã.
- [ ] **Step 6: Ghi nhận.** Việc đưa bản web mới lên HoaiĐức theo quy trình trong `BAN-GIAO-ANTIGRAVITY.md` mục 4 (build, chạy thử `node dist/server.cjs`, bật trang bảo trì, hỏi bạn trước khi khởi động lại dịch vụ).

---

## Luồng D — Đồng bộ tài liệu

### Task D1: Cập nhật tài liệu bằng số do chương trình in

**Files:**
- Modify: `Q_AND_A_BAN_GIAM_KHAO.md`, `BANG_SO_LIEU_THUC_NGHIEM_CHI_TIET.md`, `README.md` (đang ghi 100 khuôn/5.000 ca)
- Modify: `docs/BAN-GIAO-CONG-VIEC-DANG-DO.md`, `KE_HOACH_NANG_CAP_TOAN_DIEN_MEDITRACE.md` (đánh dấu việc đã xong)

**Interfaces:**
- Consumes: `docs/ket-qua/bo-sot-qwen3-4b.md` (Task A6), số đo lặp câu (Task B1, B4).

- [ ] **Step 1: Kiểm chuỗi bị loại.** Chạy `grep -rn "78,3" Q_AND_A_BAN_GIAM_KHAO.md BANG_SO_LIEU_THUC_NGHIEM_CHI_TIET.md README.md docs/`. Mong đợi: không còn chỗ nào dùng "78,3%" như kết quả (chỉ được xuất hiện trong câu nói rõ con số đã bị loại).
- [ ] **Step 2: Chép số từ tệp kết quả của Task A6 và B1/B4 vào tài liệu** bằng công cụ sửa tệp. Không gõ số khác. Kết quả bất lợi (nếu có) ghi ngang hàng.
- [ ] **Step 3: Sửa `README.md`** thành số khuôn và số ca đúng với manifest hiện hành (200 khuôn, 5.000 ca cho v1; ghi v2 riêng khi có).
- [ ] **Step 4: Đánh dấu việc xong** trong bản bàn giao và kế hoạch nâng cấp (mục 0).
- [ ] **Step 5: Ghi nhận** ngày cập nhật.

---

## Thứ tự và phụ thuộc

| Thứ tự | Tác vụ | Chờ |
|---|---|---|
| 1 | A1 | không |
| 2 | A2 → A3 | A1 không bắt buộc; A3 Step 5, 7 cần bạn duyệt chạm HoaiĐức |
| 3 | A4 | A3 pass VRAM ≤ 8,9 GiB và bạn đồng ý |
| 4 | A5 → A6 | A4 cho adapter mới; baseline zero-shot chạy được ngay sau A5 |
| song song | B1 → B2 → B3 → B4 → B5 | không phụ thuộc luồng A |
| sau B1 | F0 → F1 → F2 → F3 → F4 | F1 chờ bạn duyệt danh sách tên từng lô 50; F3 và F4 chờ bạn chốt nghĩa nhãn |
| sau B3, F4 | F5 (sinh bộ v2 mở rộng) | cần B4 (công cụ manifest), E2 nếu muốn dùng kho cách nói ngoài |
| song song | E0 → E1 → E2 | E0 cần bạn duyệt tải nếu phải tạo môi trường riêng |
| sau A4, B5, E1 | E3 → E4 | E4 cần hai checkpoint và bạn duyệt chạy HoaiĐức |
| sau F5, E4 | E5 → E6 | cần bạn duyệt GPU; quy tắc giữ hay bỏ bộ ngoại đã viết trước ở E6 |
| bất kỳ lúc nào | E7 | không |
| song song | C1 → C2 | không phụ thuộc các luồng khác |
| cuối | D1 | A6, B4, F5, E6 |

Tối thiểu để có kết quả huấn luyện đầu tiên: A1 → A2 → A3 → A4 → A5 → A6 (không cần F hay E). Luồng F và E nhằm vòng huấn luyện thứ hai, sau khi bạn đã có số bỏ sót ở A6.
