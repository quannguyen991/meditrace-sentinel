# -*- coding: utf-8 -*-
"""[Huấn luyện mô hình]
Làm gì   : Huấn luyện adapter Qwen3 cho bước rút mệnh đề (b1) và chọn mô hình bằng số đo.
Bản đồ   : BAN_DO_MA_NGUON.md

Các tệp:
    chon_mo_hinh_bakeoff  So các mô hình ở bước rút mệnh đề bằng số đo trên tập phát triển
                          thay vì chọn theo cảm tính.
    ham_thuong_rlvr       Chấm điểm thưởng kiểm chứng được cho một lần trích mệnh đề để dùng
                          trong học tăng cường GRPO.
    huan_luyen_dpo        Tinh chỉnh adapter trích v3 bằng DPO trên các cặp đầu ra đúng và
                          sai khó (thử nghiệm, chưa dùng trong hệ thống).
    huan_luyen_sft        Huấn luyện có giám sát adapter LoRA cho Qwen3 ở bước rút mệnh đề,
                          và giữ lời nhắc hệ thống dùng chung.
    kiem_moi_truong       Kiểm nhanh GPU và mô hình có sẵn sàng huấn luyện không: nạp 4-bit,
                          tắt thinking, mặt nạ nhãn, sinh tiếng Việt.
    loss_theo_doan        Tính loss cross-entropy theo từng đoạn chuỗi để hạ đỉnh VRAM khi
                          huấn luyện chuỗi dài.
"""
