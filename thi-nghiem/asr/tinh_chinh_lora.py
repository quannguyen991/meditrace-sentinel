# -*- coding: utf-8 -*-
"""Tinh chinh PhoWhisper bang LoRA tren tap huan luyen VietMed (tach theo nguoi noi).

Dau vao (ngoai kho, khong commit):
  --train-dir  thu muc co train_audio.zip va train_transcript.txt cua VietMed
  --dev-dir    thu muc co dev_audio.zip va dev_transcript.txt (chon moc dung, khong dung de bao cao)

Dau ra: thu muc mo hinh da gop LoRA (de danh_gia_asr.py nap bang --mo-hinh).
Tap kiem thu (test) KHONG dung trong script nay.
"""
import argparse
import ast
import random
import zipfile
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from peft import LoraConfig, get_peft_model
from scipy.signal import resample_poly
from transformers import WhisperForConditionalGeneration, WhisperProcessor

from danh_gia_asr import MODEL, REVISION, TAN_SO, doc_am_thanh


def tap(thu_muc: Path, ten: str):
    """-> danh sach (am thanh bytes, tham chieu) cho tap ten ('train' | 'dev')."""
    dong = ast.literal_eval((thu_muc / f"{ten}_transcript.txt").read_text(encoding="utf-8"))
    out = []
    with zipfile.ZipFile(thu_muc / f"{ten}_audio.zip") as z:
        goc = f"{ten}_audio/"
        ds = {n[len(goc):]: n for n in z.namelist() if n.lower().endswith((".ogg", ".wav", ".flac", ".mp3")) and n.startswith(goc)}
        for d in dong:
            if d["file"] in ds:
                out.append((z.read(ds[d["file"]]), d["text"]))
    return out


def tao_batch(proc, mau, thiet_bi):
    mang = [doc_am_thanh(a) for a, _ in mau]
    feats = proc.feature_extractor(mang, sampling_rate=TAN_SO, return_tensors="pt").input_features
    proc.tokenizer.set_prefix_tokens(language="vi", task="transcribe", predict_timestamps=False)
    nhan = [proc.tokenizer(t).input_ids for _, t in mau]
    dai = max(len(x) for x in nhan)
    pad = proc.tokenizer.pad_token_id
    labels = torch.full((len(nhan), dai), -100, dtype=torch.long)
    for i, x in enumerate(nhan):
        labels[i, : len(x)] = torch.tensor(x)
    # Bo token bat dau (sot) o dau nhan: mo hinh tu them decoder_start_token khi tinh loss.
    if (labels[:, 0] == proc.tokenizer.convert_tokens_to_ids("<|startoftranscript|>")).all():
        labels = labels[:, 1:]
    return feats.to(thiet_bi, dtype=torch.float16), labels.to(thiet_bi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-dir", type=Path, required=True)
    ap.add_argument("--dev-dir", type=Path, required=True)
    ap.add_argument("--ra", type=Path, required=True)
    ap.add_argument("--so-epoch", type=int, default=2)
    ap.add_argument("--batch", type=int, default=2)
    ap.add_argument("--tich-luy", type=int, default=4, help="so buoc tich luy gradient")
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--hat", type=int, default=42)
    a = ap.parse_args()
    random.seed(a.hat)
    torch.manual_seed(a.hat)

    thiet_bi = "cuda"
    proc = WhisperProcessor.from_pretrained(MODEL, revision=REVISION)
    mo_hinh = WhisperForConditionalGeneration.from_pretrained(
        MODEL, revision=REVISION, dtype=torch.float16).to(thiet_bi)
    mo_hinh.config.forced_decoder_ids = None
    mo_hinh.gradient_checkpointing_enable()
    mo_hinh.enable_input_require_grads()
    cau_hinh = LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
                          target_modules=["q_proj", "v_proj", "k_proj", "out_proj"], bias="none")
    mo_hinh = get_peft_model(mo_hinh, cau_hinh)
    for p in mo_hinh.parameters():
        if p.requires_grad:
            p.data = p.data.float()
    mo_hinh.print_trainable_parameters()

    train = tap(a.train_dir, "train")
    print("so cau huan luyen:", len(train))
    toi_uu = torch.optim.AdamW([p for p in mo_hinh.parameters() if p.requires_grad], lr=a.lr)
    scaler = torch.amp.GradScaler("cuda")
    tong_buoc = (len(train) // a.batch) * a.so_epoch // a.tich_luy
    lich = torch.optim.lr_scheduler.LambdaLR(toi_uu, lambda s: min(1.0, (s + 1) / 20) * max(0.0, 1 - s / max(1, tong_buoc)))

    mo_hinh.train()
    buoc = 0
    for ep in range(a.so_epoch):
        random.shuffle(train)
        tong_loss, n = 0.0, 0
        for i in range(0, len(train) - a.batch + 1, a.batch):
            feats, labels = tao_batch(proc, train[i:i + a.batch], thiet_bi)
            with torch.autocast("cuda", dtype=torch.float16):
                loss = mo_hinh(input_features=feats, labels=labels).loss / a.tich_luy
            scaler.scale(loss).backward()
            tong_loss += loss.item() * a.tich_luy
            n += 1
            if n % a.tich_luy == 0:
                scaler.unscale_(toi_uu)
                torch.nn.utils.clip_grad_norm_([p for p in mo_hinh.parameters() if p.requires_grad], 1.0)
                scaler.step(toi_uu)
                scaler.update()
                toi_uu.zero_grad()
                lich.step()
                buoc += 1
                if buoc % 50 == 0:
                    print(f"epoch {ep} buoc {buoc} loss {tong_loss / n:.4f}", flush=True)
        print(f"ket thuc epoch {ep}: loss trung binh {tong_loss / max(n, 1):.4f}", flush=True)

    # Gop LoRA vao trong so de danh_gia_asr.py nap nhu mo hinh thuong.
    mo_hinh = mo_hinh.merge_and_unload()
    mo_hinh = mo_hinh.half()
    dau_ra = a.ra / "phowhisper-medium-vietmed-lora"
    dau_ra.mkdir(parents=True, exist_ok=True)
    mo_hinh.save_pretrained(dau_ra)
    proc.save_pretrained(dau_ra)
    print("da luu", dau_ra)


if __name__ == "__main__":
    main()
