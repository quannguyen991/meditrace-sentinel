# -*- coding: utf-8 -*-
"""[Huấn luyện mô hình › Huấn luyện]
Làm gì   : Kiểm nhanh GPU và mô hình có sẵn sàng huấn luyện không: nạp 4-bit, tắt thinking,
           mặt nạ nhãn, sinh tiếng Việt.
Vào → Ra : tên mô hình (--model) → in kết quả bốn phép kiểm ra màn hình
Đọc từ   : main() chạy cả bốn phép kiểm
Mục lục (các hàm/lớp chính):
  main()  Điểm vào: kiểm nhanh môi trường trước huấn luyện
Tên cũ   : kiem_mo_hinh.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Kiểm nhanh môi trường mô hình trước khi huấn luyện.

Bốn điều phải đúng, nếu sai thì mọi bước sau đều vô nghĩa:

  1. Nạp được mô hình 4-bit trên GPU
  2. `enable_thinking=False` thật sự tắt chế độ thinking — đầu ra KHÔNG được
     lẫn khối <think>...</think>. Đây là bẫy riêng của Qwen3.
  3. Mặt nạ nhãn che đúng phần prompt, không lệch token nào
  4. Sinh được tiếng Việt có dấu

    python -m src.huan_luyen.kiem_moi_truong --model Qwen/Qwen3-1.7B
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


# ═══ main() — Điểm vào: kiểm nhanh môi trường trước huấn luyện ════════════════════════
# Nạp 4-bit, tắt thinking, kiểm mặt nạ nhãn và sinh tiếng Việt có dấu.
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
        bnb_4bit_compute_dtype=torch.bfloat16,   # KHÔNG để mặc định float32
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
