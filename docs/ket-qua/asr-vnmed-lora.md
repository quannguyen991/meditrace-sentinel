# ASR: LoRA trên VNMed_Speech cho PhoWhisper-small

Ngày chạy: 28/11/2026. Số liệu thô: [asr-vnmed-lora.json](asr-vnmed-lora.json). Mô hình sản xuất (vinai/PhoWhisper-small) **không bị đổi**; adapter chỉ nằm trên máy huấn luyện và chưa được triển khai.

## 1. Dữ liệu

- VNMed_Speech `reviewed-merged.parquet`: 2.887 đoạn, 107 phiên, 8,36 giờ, 8 kHz, CC BY 4.0, lời đã được người duyệt. Nâng lên 16 kHz bằng `resample_poly` khi nạp.
- Bỏ đoạn dài hơn 29,5 giây. Tách 5 phiên (155 đoạn) để theo dõi loss; còn **2.732 đoạn huấn luyện**.
- Không dùng tập kiểm thử nào để huấn luyện hay chọn siêu tham số.

## 2. Kiểm rò rỉ (văn bản, đã chuẩn hóa chữ thường, bỏ dấu câu)

Khớp tuyệt đối và gần trùng (độ giống ≥ 0,9, câu từ 6 từ trở lên, tìm ứng viên bằng 6-gram):

| Tập so | Trùng tuyệt đối | Gần trùng |
|---|---|---|
| ViMedCSS-test-shard0 (323 câu) | 0 | 0 |
| VietMed-test | 0 | 0 |
| VietMed-train | 0 | 0 |
| VietMed-dev | 0 | 0 |

Không có dòng nào bị loại. Có 3 câu trùng nhau trong chính VNMed (giữ nguyên). Kiểm tra này chỉ dựa vào văn bản; chưa so âm thanh hay video nguồn (VNMed lấy từ VietMed_unlabeled, nhóm khác với VietMed có nhãn).

## 3. Huấn luyện

LoRA r=16, alpha=32, dropout 0,05 trên q/k/v/out_proj (3,54 triệu tham số, 1,44%), lr 1e-4 giảm tuyến tính, batch 4 × tích lũy 4 = 16, fp16, trần VRAM 70% (đỉnh dùng 3,5 GB), seed 42.

| | Giá trị |
|---|---|
| Số bước | 510 (3 epoch) |
| Thời gian | 1.961 giây (khoảng 33 phút) |
| Loss huấn luyện trung bình | 0,282 → 0,138 → 0,108 |
| Loss theo dõi (5 phiên giữ lại) | 0,543 (trước) → 0,143 → 0,125 → 0,124 |

Loss theo dõi cùng nguồn video với tập huấn luyện nên giảm mạnh một phần do làm quen cách ghi lời của bộ dữ liệu; không dùng nó làm bằng chứng cải thiện.

## 4. Kết quả (giải mã greedy, cùng `danh_gia_asr.py`)

Số của PhoWhisper-small. Bảng ở `docs/tien-do-asr-va-kiem-ro-ri.md` là của PhoWhisper-medium, không so trực tiếp.

| Tập | Chỉ số | Gốc | LoRA 1 epoch | LoRA 3 epoch (bản cuối) |
|---|---|---|---|---|
| ViMedCSS-test-shard0 (323) | WER | 0,3165 | 0,3381 | **0,2610** |
| | Thuật ngữ Anh nhận đúng | 0,1053 | 0,1718 | **0,1904** |
| | AUROC độ tin cậy (WER≥0,2) | 0,808 | 0,788 | 0,789 |
| VietMed-test, 500 câu đầu | WER | 0,3550 | 0,3295 | **0,3201** |
| | AUROC độ tin cậy (WER≥0,2) | 0,855 | 0,759 | 0,770 |

Hiệu (LoRA 3 epoch − gốc), paired bootstrap theo câu, 2.000 lần, khoảng tin cậy 95%:

| Phép đo | Hiệu | CI 95% |
|---|---|---|
| WER ViMedCSS | −0,056 | [−0,069; −0,043] |
| WER VietMed-500 | −0,035 | [−0,045; −0,025] |
| Thuật ngữ Anh ViMedCSS | +0,085 | [+0,056; +0,116] |

LoRA 1 epoch so với gốc: WER ViMedCSS +0,022 [−0,042; +0,140] (không khác biệt rõ), thuật ngữ +0,067 [+0,040; +0,094], WER VietMed −0,026 [−0,037; −0,014].

Trên ViMedCSS, 30 câu có tỷ lệ thuật ngữ tăng và 1 câu giảm. Ví dụ: `methionin` (gốc ghi "mê thi ô nin"), `lipid` (gốc ghi "libya") được nhận đúng sau tinh chỉnh; nhiều thuật ngữ khác vẫn sai (`levodopa` → "lê vô độp").

## 5. Giới hạn

- Một lần chạy, một seed. Không có lặp lại nên chưa biết độ dao động giữa các lần huấn luyện.
- Epoch 1 cho WER ViMedCSS xấu hơn gốc: kết quả phụ thuộc số bước và lịch lr; số epoch 3 chưa được tối ưu (không quét siêu tham số, không chọn epoch theo tập kiểm thử).
- Bootstrap theo câu bỏ qua việc nhiều câu cùng video, nên CI có thể hẹp hơn thực tế, nhất là ViMedCSS.
- AUROC độ tin cậy của VietMed giảm (0,855 → 0,770): mô hình tinh chỉnh tự tin hơn khi sai, cần hiệu chuẩn lại trước khi dùng ngưỡng độ tin cậy.
- Nguồn âm thanh 8 kHz; VietMed-test chỉ 500 câu đầu (không phải toàn bộ 3.437 câu).
- Kiểm rò rỉ chỉ qua văn bản. Chưa đo trên âm thanh thật của MediTrace.
- Chưa triển khai; mô hình và dịch vụ sản xuất giữ nguyên. Giấy phép dữ liệu CC BY 4.0 (cần ghi nguồn nếu phát hành adapter).

## 6. Tệp

Trên máy huấn luyện `C:\Users\hapur\meditrace-train\vnmed\`: `reviewed-merged.parquet`, `eval\` (bản sao tập kiểm thử), `lora-pho-small-vnmed\` (adapter cuối + `epoch1\`, `epoch2\`, `epoch3\`, 57 MB), `ket-qua\{goc,epoch1,epoch3}\`, `train.log`, `eval.log`, `pylib\` (jiwer, pyarrow, soundfile cài riêng, không đụng venv chung). Trong kho: `thi-nghiem/asr/tinh_chinh_lora_vnmed.py`, `thi-nghiem/asr/danh_gia_adapter.py`.
