# Huấn luyện mô hình — `src/huan_luyen/`

Huấn luyện adapter Qwen3 cho bước rút mệnh đề (b1) và chọn mô hình bằng số đo.

| Tệp | Thuộc | Làm gì | Tên cũ |
|---|---|---|---|
| [chon_mo_hinh_bakeoff.py](chon_mo_hinh_bakeoff.py) | Chọn mô hình | So các mô hình ở bước rút mệnh đề bằng số đo trên tập phát triển thay vì chọn theo cảm tính. | `src/bakeoff.py` |
| [ham_thuong_rlvr.py](ham_thuong_rlvr.py) | Học tăng cường | Chấm điểm thưởng kiểm chứng được cho một lần trích mệnh đề để dùng trong học tăng cường GRPO. | `src/bo_kiem_tra.py` |
| [huan_luyen_dpo.py](huan_luyen_dpo.py) | Huấn luyện | Tinh chỉnh adapter trích v3 bằng DPO trên các cặp đầu ra đúng và sai khó (thử nghiệm, chưa dùng trong hệ thống). | `src/train_dpo.py` |
| [huan_luyen_sft.py](huan_luyen_sft.py) | Huấn luyện | Huấn luyện có giám sát adapter LoRA cho Qwen3 ở bước rút mệnh đề, và giữ lời nhắc hệ thống dùng chung. | `src/train_baseline.py` |
| [kiem_moi_truong.py](kiem_moi_truong.py) | Huấn luyện | Kiểm nhanh GPU và mô hình có sẵn sàng huấn luyện không: nạp 4-bit, tắt thinking, mặt nạ nhãn, sinh tiếng Việt. | `src/kiem_mo_hinh.py` |
| [loss_theo_doan.py](loss_theo_doan.py) | Huấn luyện | Tính loss cross-entropy theo từng đoạn chuỗi để hạ đỉnh VRAM khi huấn luyện chuỗi dài. | `src/loss_theo_doan.py` |

Bản đồ toàn dự án: [../../BAN_DO_MA_NGUON.md](../../BAN_DO_MA_NGUON.md)
