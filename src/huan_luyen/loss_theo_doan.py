# -*- coding: utf-8 -*-
"""[Huấn luyện mô hình › Huấn luyện]
Làm gì   : Tính loss cross-entropy theo từng đoạn chuỗi để hạ đỉnh VRAM khi huấn luyện chuỗi
           dài.
Vào → Ra : logit ẩn và nhãn token → giá trị loss như cách tính thường nhưng ít bộ nhớ hơn
Đọc từ   : cross_entropy_theo_doan() tính loss từng đoạn; tao_trainer_loss_theo_doan() gắn
           vào trainer
Mục lục (các hàm/lớp chính):
  cross_entropy_theo_doan()     Loss cross-entropy tính theo từng đoạn token
  tao_trainer_loss_theo_doan()  Tạo lớp Trainer dùng loss theo đoạn
  bo_mat_na_day_du()            Bỏ mặt nạ chú ý khi toàn là 1
  _tong_loss_doan()             Cộng loss cross-entropy của một đoạn
Dùng bởi : huan_luyen/huan_luyen_dpo, huan_luyen/huan_luyen_sft
Tên cũ   : loss_theo_doan.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Loss cross-entropy tính THEO ĐOẠN để giảm đỉnh bộ nhớ khi huấn luyện chuỗi dài.

VÌ SAO CẦN. Với từ vựng Qwen V = 151.936 và chuỗi T = 4.096, ma trận logits
[1, 4096, 151936] ở FP32 chiếm khoảng 2,5 GB, chưa kể buffer softmax và gradient.
Bước đầu tiên khi tiếp tục huấn luyện ở 4.096 token cần khoảng 10,5 GiB trên RTX
3060, trong khi giới hạn của dự án là 90% (10,8 GiB) và bge-m3 cùng phần hiển thị
đã chiếm khoảng 1,9 GiB: kết quả là hết bộ nhớ (OOM).

CÁCH LÀM. Không tính logits cho cả chuỗi một lần. Chia chiều T thành các đoạn
`kich_thuoc_doan` token; mỗi đoạn chỉ tính logits của đoạn đó, cộng tổng loss, rồi
(nhờ `torch.utils.checkpoint`) bỏ logits ngay và tính lại khi lan truyền ngược.
Kết quả BẰNG loss tính một lần trên toàn bộ logits (phép thử canh điều này), nên
checkpoint cũ vẫn dùng được.
"""
from __future__ import annotations

import torch
import torch.nn.functional as F
from torch import Tensor
from torch.utils.checkpoint import checkpoint


# ─── _tong_loss_doan() — Cộng loss cross-entropy của một đoạn ─────────────────────────
# Được bọc checkpoint để bỏ logits và tính lại khi lan truyền ngược.
def _tong_loss_doan(hidden: Tensor, lm_head: torch.nn.Module, nhan: Tensor,
                    bo_qua: int) -> Tensor:
    logits = lm_head(hidden).float()
    return F.cross_entropy(logits.reshape(-1, logits.size(-1)), nhan.reshape(-1),
                           ignore_index=bo_qua, reduction="sum")


# ═══ cross_entropy_theo_doan() — Loss cross-entropy tính theo từng đoạn token ═════════
# Chỉ tính logits từng đoạn; mọi nhãn bị bỏ qua thì trả 0,0.
def cross_entropy_theo_doan(hidden: Tensor, lm_head: torch.nn.Module, nhan: Tensor,
                            kich_thuoc_doan: int = 512, bo_qua: int = -100) -> Tensor:
    """Loss trung bình trên các token khác `bo_qua`.

    `hidden` [B, T, H] và `nhan` [B, T] đã được dịch một vị trí (hàm gọi tự dịch).
    Nếu mọi nhãn đều bị bỏ qua thì trả 0,0 (hữu hạn, vẫn lan truyền ngược được).
    """
    if kich_thuoc_doan <= 0:
        raise ValueError("kich_thuoc_doan phai duong")
    so_token = int((nhan != bo_qua).sum().item())
    if so_token == 0:
        return hidden.sum() * 0.0
    tong = hidden.new_zeros((), dtype=torch.float32)
    T = hidden.size(1)
    for i in range(0, T, kich_thuoc_doan):
        h = hidden[:, i:i + kich_thuoc_doan]
        n = nhan[:, i:i + kich_thuoc_doan]
        if bool((n != bo_qua).any()):
            if h.requires_grad:
                tong = tong + checkpoint(_tong_loss_doan, h, lm_head, n, bo_qua,
                                         use_reentrant=False)
            else:
                tong = tong + _tong_loss_doan(h, lm_head, n, bo_qua)
    return tong / so_token


# ═══ bo_mat_na_day_du() — Bỏ mặt nạ chú ý khi toàn là 1 ═══════════════════════════════
# Cho phép SDPA dùng đường causal tiết kiệm bộ nhớ.
def bo_mat_na_day_du(attention_mask):
    """Mặt nạ toàn 1 (không có đệm) -> None, để transformers dùng đường `is_causal`
    của SDPA (nhỏ bộ nhớ O(n)) thay vì dùng mặt nạ 4 chiều dày [B, 1, T, T].

    Với `per_device_train_batch_size=1` không bao giờ có đệm, nên mặt nạ luôn toàn 1.
    Có đệm thì giữ nguyên mặt nạ (kết quả phải đúng)."""
    if attention_mask is not None and bool(attention_mask.all()):
        return None
    return attention_mask


# ═══ tao_trainer_loss_theo_doan() — Tạo lớp Trainer dùng loss theo đoạn ═══════════════
# Ghi đè compute_loss, lấy hidden state và lm_head; chỉ dùng với mô hình PEFT.
def tao_trainer_loss_theo_doan(Trainer: type, kich_thuoc_doan: int = 512) -> type:
    """Lớp con của `Trainer` ghi đè `compute_loss` bằng loss theo đoạn.

    Lấy hidden states từ thân mô hình và `lm_head` riêng, nên KHÔNG bao giờ tạo ra
    logits cho cả chuỗi. Chỉ dùng được với mô hình bao bởi PEFT
    (`model.base_model.model.model` và `.lm_head`).
    """
    class TrainerLossTheoDoan(Trainer):
        def compute_loss(self, model, inputs, return_outputs=False,
                         num_items_in_batch=None):
            goc = model.base_model.model
            hidden = goc.model(input_ids=inputs["input_ids"],
                               attention_mask=bo_mat_na_day_du(
                                   inputs.get("attention_mask"))).last_hidden_state
            loss = cross_entropy_theo_doan(hidden[:, :-1], goc.lm_head,
                                           inputs["labels"][:, 1:], kich_thuoc_doan)
            # `prediction_step` của Trainer đọc `outputs` như dict (hoặc cắt lát
            # `outputs[1:]`): trả `None` thì bước eval sẽ vỡ. Dict rỗng là đủ, vì
            # eval chỉ cần loss (`prediction_loss_only`).
            return (loss, {}) if return_outputs else loss

    return TrainerLossTheoDoan
