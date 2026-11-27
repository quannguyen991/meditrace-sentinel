# -*- coding: utf-8 -*-
"""Do dinh VRAM cua MOT buoc tien + lui khi huan luyen khau trich.

Dung de kiem loss theo doan (src/huan_luyen/loss_theo_doan.py) truoc khi huan luyen that:
  - o do dai ngan, loss theo doan phai BANG loss goc (lech duoi 0,1%);
  - o 4.096 token, dinh VRAM cua tien trinh phai <= 8,9 GiB (= 10,8 GiB gioi han
    90% tru 1,9 GiB ma bge-m3 va hien thi dang chiem).

Chay tren may co GPU (HoaiDuc):
  python tools/do_vram_mot_batch.py --do-dai 2048                 # loss goc
  python tools/do_vram_mot_batch.py --do-dai 2048 --kich-thuoc-doan 512
  python tools/do_vram_mot_batch.py --do-dai 4096 --kich-thuoc-doan 512
(O 1.024 token tep trich khong con mau nao: trung vi do dai la ~2.683 token.)
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.he_thong import duong_dan as duong_dan  # noqa: E402


def do_vram(model_ten: str, do_dai: int, kich_thuoc_doan: int | None,
            tep: str | None = None, phan_vram: float | None = None) -> dict:
    """-> {"peak_gib", "peak_reserved_gib", "loss", "do_dai_thuc", "kich_thuoc_doan"}.

    Lay mau DAI NHAT khong qua `do_dai` token cua tep huan luyen khau trich, chay
    mot buoc tien va lui giong `train_baseline` (nf4, LoRA r=16, bf16, gradient
    checkpointing). `kich_thuoc_doan=None` dung loss goc cua mo hinh.
    """
    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    from src.huan_luyen.loss_theo_doan import bo_mat_na_day_du, cross_entropy_theo_doan
    from src.huan_luyen.huan_luyen_sft import TapLamSang, gom_lo

    if phan_vram:
        torch.cuda.set_per_process_memory_fraction(phan_vram, 0)
    tok = AutoTokenizer.from_pretrained(model_ten)
    tep = tep or str(duong_dan.THU_MUC_DU_LIEU / "trich_train.jsonl")
    tap = TapLamSang(tep, tok, do_dai, "trich")
    if len(tap) == 0:
        # Do dai token cua tep trich: trung vi ~2.683, toi da ~4.294. O 1.024 khong con
        # mau nao; muon so loss goc voi loss theo doan, dung >= 2.048.
        raise SystemExit(f"khong co mau nao <= {do_dai} token trong {tep} "
                         f"({len(tap.bi_loai)} mau bi loai)")
    chi_so = max(range(len(tap)), key=lambda i: len(tap[i]["input_ids"]))
    lo = gom_lo([tap[chi_so]], tok.pad_token_id)
    lo = {k: v.cuda() for k, v in lo.items()}

    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True,
                             bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(model_ten, quantization_config=bnb,
                                                 device_map="auto")
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"]))
    model.gradient_checkpointing_enable()
    model.train()

    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    with torch.autocast("cuda", dtype=torch.bfloat16):
        if kich_thuoc_doan:
            goc = model.base_model.model
            hidden = goc.model(input_ids=lo["input_ids"],
                               attention_mask=bo_mat_na_day_du(
                                   lo["attention_mask"])).last_hidden_state
            loss = cross_entropy_theo_doan(hidden[:, :-1], goc.lm_head,
                                           lo["labels"][:, 1:], kich_thuoc_doan)
        else:
            loss = model(**lo).loss
    loss.backward()
    torch.cuda.synchronize()
    gib = 1024 ** 3
    return {"peak_gib": round(torch.cuda.max_memory_allocated() / gib, 3),
            "peak_reserved_gib": round(torch.cuda.max_memory_reserved() / gib, 3),
            "loss": float(loss.detach()),
            "do_dai_thuc": int(lo["input_ids"].size(1)),
            "kich_thuoc_doan": kich_thuoc_doan}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=duong_dan.MODEL_CHINH)
    ap.add_argument("--do-dai", type=int, default=1024)
    ap.add_argument("--kich-thuoc-doan", type=int, default=None,
                    help="bo trong = loss goc cua mo hinh")
    ap.add_argument("--tep", default=None)
    ap.add_argument("--phan-vram", type=float, default=None,
                    help="tran VRAM cua tien trinh (0-1), vi du 0.74")
    a = ap.parse_args()
    print(json.dumps(do_vram(a.model, a.do_dai, a.kich_thuoc_doan, a.tep, a.phan_vram),
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
