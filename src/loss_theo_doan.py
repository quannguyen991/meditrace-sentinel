# -*- coding: utf-8 -*-
"""Loss cross-entropy tinh THEO DOAN de giam dinh bo nho khi huan luyen chuoi dai.

VI SAO CAN. Voi tu vung Qwen V = 151.936 va chuoi T = 4.096, ma tran logits
[1, 4096, 151936] o FP32 chiem khoang 2,5 GB, chua ke buffer softmax va gradient.
Buoc dau tien khi tiep tuc huan luyen o 4.096 token can khoang 10,5 GiB tren RTX
3060, trong khi gioi han cua du an la 90% (10,8 GiB) va bge-m3 cung phan hien thi
da chiem khoang 1,9 GiB: ket qua la het bo nho (OOM).

CACH LAM. Khong tinh logits cho ca chuoi mot lan. Chia chieu T thanh cac doan
`kich_thuoc_doan` token; moi doan chi tinh logits cua doan do, cong tong loss, roi
(nho `torch.utils.checkpoint`) bo logits ngay va tinh lai khi lan truyen nguoc.
Ket qua BANG loss tinh mot lan tren toan bo logits (phep thu canh dieu nay), nen
checkpoint cu van dung duoc.
"""
from __future__ import annotations

import torch
import torch.nn.functional as F
from torch import Tensor
from torch.utils.checkpoint import checkpoint


def _tong_loss_doan(hidden: Tensor, lm_head: torch.nn.Module, nhan: Tensor,
                    bo_qua: int) -> Tensor:
    logits = lm_head(hidden).float()
    return F.cross_entropy(logits.reshape(-1, logits.size(-1)), nhan.reshape(-1),
                           ignore_index=bo_qua, reduction="sum")


def cross_entropy_theo_doan(hidden: Tensor, lm_head: torch.nn.Module, nhan: Tensor,
                            kich_thuoc_doan: int = 512, bo_qua: int = -100) -> Tensor:
    """Loss trung binh tren cac token khac `bo_qua`.

    `hidden` [B, T, H] va `nhan` [B, T] da duoc dich mot vi tri (ham goi tu dich).
    Neu moi nhan deu bi bo qua thi tra 0,0 (huu han, van lan truyen nguoc duoc).
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


def bo_mat_na_day_du(attention_mask):
    """Mat na toan 1 (khong co dem) -> None, de transformers dung duong `is_causal`
    cua SDPA (nho bo nho O(n)) thay vi dung mat na 4 chieu day [B, 1, T, T].

    Voi `per_device_train_batch_size=1` khong bao gio co dem, nen mat na luon toan 1.
    Co dem thi giu nguyen mat na (ket qua phai dung)."""
    if attention_mask is not None and bool(attention_mask.all()):
        return None
    return attention_mask


def tao_trainer_loss_theo_doan(Trainer: type, kich_thuoc_doan: int = 512) -> type:
    """Lop con cua `Trainer` ghi de `compute_loss` bang loss theo doan.

    Lay hidden states tu than mo hinh va `lm_head` rieng, nen KHONG bao gio tao ra
    logits cho ca chuoi. Chi dung duoc voi mo hinh bao boi PEFT
    (`model.base_model.model.model` va `.lm_head`).
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
            # `prediction_step` cua Trainer doc `outputs` nhu dict (hoac cat lat
            # `outputs[1:]`): tra `None` thi buoc eval se vo. Dict rong la du, vi
            # eval chi can loss (`prediction_loss_only`).
            return (loss, {}) if return_outputs else loss

    return TrainerLossTheoDoan
