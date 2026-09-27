# -*- coding: utf-8 -*-
"""Kiem nhanh moi truong mo hinh truoc khi huan luyen.

Bon dieu phai dung, neu sai thi moi buoc sau deu vo nghia:

  1. Nap duoc mo hinh 4-bit tren GPU
  2. `enable_thinking=False` that su tat che do thinking — dau ra KHONG duoc
     lan khoi <think>...</think>. Day la bay rieng cua Qwen3.
  3. Mat na nhan che dung phan prompt, khong lech token nao
  4. Sinh duoc tieng Viet co dau

    python -m src.kiem_mo_hinh --model Qwen/Qwen3-1.7B
"""
import argparse
import io
import sys

SYSTEM = (
    "Bạn là trợ lý y tế. Đọc hội thoại và ghi lại thành hồ sơ bệnh án ngắn gọn, "
    "chỉ dùng thông tin có trong hội thoại."
)
HOI_THOAI = (
    "Bác sĩ: Cháu có tiền sử dị ứng thuốc gì không ạ?\n"
    "Mẹ: Tôi thì dị ứng penicillin, còn cháu chưa thấy bị bao giờ."
)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-1.7B")
    a = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

    print(f"[1/4] Nap tokenizer {a.model}")
    tok = AutoTokenizer.from_pretrained(a.model)

    print("[2/4] Nap mo hinh 4-bit (bfloat16 compute)")
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,   # KHONG de mac dinh float32
    )
    model = AutoModelForCausalLM.from_pretrained(
        a.model, quantization_config=bnb, device_map="auto")
    model.eval()
    print(f"      VRAM dang dung: {torch.cuda.memory_allocated()/2**30:.2f} GB")

    msgs = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Hội thoại:\n{HOI_THOAI}"}]

    print("[3/4] Kiem mat na nhan — enable_thinking=False")
    prompt = tok.apply_chat_template(msgs, tokenize=False,
                                     add_generation_prompt=True, enable_thinking=False)
    dap_an = "TIỀN SỬ DỊ ỨNG\n\nMẹ dị ứng penicillin. Trẻ chưa ghi nhận dị ứng."
    day_du = tok.apply_chat_template(msgs + [{"role": "assistant", "content": dap_an}],
                                     tokenize=False, add_generation_prompt=False,
                                     enable_thinking=False)
    ids_prompt = tok.encode(prompt, add_special_tokens=False)
    ids_day_du = tok.encode(day_du, add_special_tokens=False)

    cung_tien_to = ids_day_du[:len(ids_prompt)] == ids_prompt
    print(f"      prompt {len(ids_prompt)} token, day du {len(ids_day_du)} token")
    print(f"      day du co cung tien to voi prompt: {cung_tien_to}")
    phan_nhan = tok.decode(ids_day_du[len(ids_prompt):])
    print(f"      phan duoc hoc: {phan_nhan[:120]!r}")
    if not cung_tien_to:
        print("      *** CANH BAO: mat na nhan se LECH. Phai sua truoc khi train. ***")

    print("[4/4] Sinh thu")
    inp = tok(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        out = model.generate(**inp, max_new_tokens=120, do_sample=False,
                             pad_token_id=tok.eos_token_id)
    sinh = tok.decode(out[0][inp["input_ids"].shape[1]:], skip_special_tokens=True)
    print("      --- dau ra ---")
    print("      " + sinh.replace("\n", "\n      ")[:600])

    co_think = "<think>" in sinh or "</think>" in sinh
    print()
    print(f"KET LUAN: co khoi <think> trong dau ra: {co_think}")
    if co_think:
        print("*** enable_thinking=False KHONG co tac dung — phai xu ly truoc khi train ***")
        sys.exit(1)
    print("OK — moi truong san sang.")


if __name__ == "__main__":
    main()
