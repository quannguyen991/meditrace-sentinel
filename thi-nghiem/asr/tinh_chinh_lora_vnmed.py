# -*- coding: utf-8 -*-
"""LoRA tren PhoWhisper-small voi VNMed_Speech (8 kHz -> 16 kHz).

Chay tren may huan luyen. Gioi han VRAM 70%. Luu adapter (khong gop) sau moi epoch.
Tach 5% phien (seq_name) lam tap theo doi loss; khong dung tap kiem thu.
"""
import argparse, io, json, random, sys, time, re
from pathlib import Path
sys.path.insert(0, r"C:\Users\hapur\meditrace-train\vnmed\pylib")
import numpy as np, pyarrow.parquet as pq, torch
from peft import LoraConfig, get_peft_model
from transformers import WhisperForConditionalGeneration, WhisperProcessor
from danh_gia_asr import doc_am_thanh, TAN_SO

MODEL = "vinai/PhoWhisper-small"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parquet", type=Path, required=True)
    ap.add_argument("--bo-qua", type=Path, default=None, help="json {drop_idx:[...]} hang bi loai vi trung kiem thu")
    ap.add_argument("--ra", type=Path, required=True)
    ap.add_argument("--so-epoch", type=int, default=1)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--tich-luy", type=int, default=4)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--han-gio", type=str, default=None, help="HH:MM dung tu dong khi qua gio nay")
    ap.add_argument("--hat", type=int, default=42)
    a = ap.parse_args()
    random.seed(a.hat); torch.manual_seed(a.hat)
    torch.cuda.set_per_process_memory_fraction(0.70)
    dev = "cuda"
    t0 = time.time()
    bang = pq.read_table(a.parquet, columns=["audio", "text", "seq_name", "duration"]).to_pylist()
    drop = set(json.loads(a.bo_qua.read_text())["drop_idx"]) if a.bo_qua else set()
    seqs = sorted({r["seq_name"] for r in bang})
    rnd = random.Random(a.hat); rnd.shuffle(seqs)
    val_seq = set(seqs[: max(1, len(seqs) // 20)])
    train, val = [], []
    for i, r in enumerate(bang):
        if i in drop or not r["text"].strip() or r["duration"] > 29.5:
            continue
        x = doc_am_thanh(r["audio"]["bytes"])
        (val if r["seq_name"] in val_seq else train).append((x, r["text"].strip()))
    del bang
    print(f"train {len(train)} val {len(val)} (phien val {len(val_seq)}) nap {time.time()-t0:.0f}s", flush=True)

    proc = WhisperProcessor.from_pretrained(MODEL)
    proc.tokenizer.set_prefix_tokens(language="vi", task="transcribe", predict_timestamps=False)
    m = WhisperForConditionalGeneration.from_pretrained(MODEL, dtype=torch.float16).to(dev)
    m.config.forced_decoder_ids = None
    m.enable_input_require_grads()
    m = get_peft_model(m, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05,
                                     target_modules=["q_proj", "v_proj", "k_proj", "out_proj"], bias="none"))
    for p in m.parameters():
        if p.requires_grad:
            p.data = p.data.float()
    m.print_trainable_parameters()
    sot = proc.tokenizer.convert_tokens_to_ids("<|startoftranscript|>")

    def batch(mau):
        f = proc.feature_extractor([x for x, _ in mau], sampling_rate=TAN_SO, return_tensors="pt").input_features
        nh = [proc.tokenizer(t).input_ids[:440] for _, t in mau]
        L = max(len(n) for n in nh)
        lab = torch.full((len(nh), L), -100, dtype=torch.long)
        for i, n in enumerate(nh):
            lab[i, :len(n)] = torch.tensor(n)
        if (lab[:, 0] == sot).all():
            lab = lab[:, 1:]
        return f.to(dev, dtype=torch.float16), lab.to(dev)

    @torch.no_grad()
    def val_loss():
        m.eval(); tot = n = 0
        for i in range(0, len(val), 8):
            f, l = batch(val[i:i+8])
            with torch.autocast("cuda", dtype=torch.float16):
                tot += m(input_features=f, labels=l).loss.item(); n += 1
        m.train(); return tot / max(n, 1)

    params = [p for p in m.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=a.lr)
    scaler = torch.amp.GradScaler("cuda")
    tong = (len(train) // a.batch) * a.so_epoch // a.tich_luy
    sch = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / 20) * max(0.0, 1 - s / max(1, tong)))
    log = {"train": len(train), "val": len(val), "tong_buoc_ke_hoach": tong, "val_loss_truoc": val_loss(), "epochs": []}
    print("val loss truoc", log["val_loss_truoc"], flush=True)
    m.train(); buoc = 0; tl = n = 0; t1 = time.time(); stop = False
    for ep in range(a.so_epoch):
        random.shuffle(train)
        for i in range(0, len(train) - a.batch + 1, a.batch):
            f, l = batch(train[i:i + a.batch])
            with torch.autocast("cuda", dtype=torch.float16):
                loss = m(input_features=f, labels=l).loss / a.tich_luy
            scaler.scale(loss).backward(); tl += loss.item() * a.tich_luy; n += 1
            if n % a.tich_luy == 0:
                scaler.unscale_(opt); torch.nn.utils.clip_grad_norm_(params, 1.0)
                scaler.step(opt); scaler.update(); opt.zero_grad(); sch.step(); buoc += 1
                if buoc % 20 == 0:
                    print(f"ep {ep} buoc {buoc}/{tong} loss {tl/n:.4f} {time.time()-t1:.0f}s vram_max {torch.cuda.max_memory_allocated()/2**30:.1f}GB", flush=True)
                if a.han_gio and time.strftime("%H:%M") >= a.han_gio:
                    print("het gio, dung som", flush=True); stop = True; break
        vl = val_loss()
        d = a.ra / f"epoch{ep+1}"; d.mkdir(parents=True, exist_ok=True); m.save_pretrained(d)
        log["epochs"].append({"epoch": ep + 1, "buoc": buoc, "loss_train_tb": tl / max(n, 1), "val_loss": vl, "giay": time.time() - t1, "dung_som": stop})
        print("epoch", ep + 1, log["epochs"][-1], flush=True)
        tl = n = 0
        if stop: break
    m.save_pretrained(a.ra)
    log["buoc_da_chay"] = buoc; log["tong_giay"] = time.time() - t1
    (a.ra / "nhat-ky-huan-luyen.json").write_text(json.dumps(log, indent=1), encoding="utf-8")
    print("xong", flush=True)

if __name__ == "__main__":
    main()
