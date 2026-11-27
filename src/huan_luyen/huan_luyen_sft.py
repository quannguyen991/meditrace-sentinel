# -*- coding: utf-8 -*-
"""[Huấn luyện mô hình › Huấn luyện]
Làm gì   : Huấn luyện có giám sát adapter LoRA cho Qwen3 ở bước rút mệnh đề, và giữ lời nhắc
           hệ thống dùng chung.
Vào → Ra : tập huấn luyện jsonl hội thoại và nhãn → adapter LoRA và nhật ký huấn luyện trong
           thư mục kết quả
Đọc từ   : main() chạy huấn luyện SFT; class TapLamSang dựng mẫu và loại mẫu quá dài
Mục lục (các hàm/lớp chính):
  main()            Điểm vào: huấn luyện SFT adapter Qwen3
  dung_chuoi()      Dựng văn bản theo mẫu chat Qwen3
  class TapLamSang  Tập dữ liệu SFT, loại mẫu quá dài thay vì cắt
  gom_lo()          Gom các mẫu thành lô có đệm phải
  kiem_mat_na()     Kiểm mặt nạ nhãn trước khi huấn luyện
Gọi tới  : bo_du_lieu/nap_du_lieu, he_thong/duong_dan, huan_luyen/loss_theo_doan
Dùng bởi : duong_ong/chay_duong_ong, huan_luyen/chon_mo_hinh_bakeoff,
           huan_luyen/huan_luyen_dpo
Tên cũ   : train_baseline.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Huấn luyện mô hình NỀN (nhánh A): hội thoại -> bệnh án, một bước.

Đây là mốc để so sánh. Mỗi nhánh sau (A+, B, C, D) phải hơn được nó thì
biểu diễn trung gian mới có lý do tồn tại.

BỐN SỬA ĐỔI so với `train.py` gốc — mỗi cái có lý do, không phải chỉnh cho đẹp:

  số bước   50 -> 200      50 x grad_accum 16 = 800 mẫu, chưa tới 0,65 epoch
  kiểu số   fp16 -> bf16   RTX 3060 là Ampere; bf16 không cần loss scaling
  độ dài    cắt -> LOẠI    cắt từ đuôi là cắt mất bệnh án, tức cắt mất NHÃN
  nguồn     train_split -> train_tang_cuong.jsonl  (tập cũ chứa mẫu giữ riêng)

    python -m src.huan_luyen.huan_luyen_sft --model Qwen/Qwen3-8B --kiem-mat-na
    python -m src.huan_luyen.huan_luyen_sft --model Qwen/Qwen3-8B
"""
import argparse
import io
import json
import sys

from src.he_thong import duong_dan as duong_dan

# torch nạp TRỄ, trong từng hàm. Lý do: bộ test phải chạy được trên máy
# không có GPU (laptop) để bắt lỗi mặt nạ nhãn TRƯỚC khi đẩy lên HoaiDuc.
# Import ở đầu tệp thì cả tệp không nạp được ở đó, và test không chạy.

# Nguyên văn từ train.py gốc. KHÔNG sửa — đổi lời nhắc là đổi baseline,
# lúc đó số của nhánh A không so được với kết quả cũ nữa.
LOI_NHAC_HE_THONG = (
    "Bạn đọc một cuộc hội thoại khám bệnh bằng tiếng Việt và viết lại thành hồ sơ bệnh án.\n\n"
    "Nguyên tắc:\n"
    "- Chỉ ghi những gì hội thoại nói ra. Không suy diễn, không thêm thông tin.\n"
    "- Ghi thông tin về ĐÚNG NGƯỜI mà nó nói tới. Người nhà kể hộ thì chủ thể "
    "là bệnh nhân; người nhà kể bệnh của chính họ thì chủ thể là người nhà.\n"
    "- Giữ nguyên tên thuốc, tên xét nghiệm và thuật ngữ y khoa như trong hội thoại.\n"
    "- Điều chưa được xác nhận thì ghi là chưa ghi nhận, không ghi thành phủ định.\n"
    "- Chỉ tạo những mục có thông tin thật. Không tạo mục trống.\n"
    "- Đề mục viết hoa toàn bộ, mỗi mục cách nhau một dòng trống. Văn phong "
    "bệnh án, ngắn gọn."
)

LOI_NHAC_NGUOI_DUNG = "Hãy viết hồ sơ bệnh án cho cuộc hội thoại sau:\n{hoi_thoai}"

# Nhiệm vụ thứ hai: TRÍCH bảng phát biểu, không viết bệnh án. Lời nhắc đầy
# đủ đã nằm sẵn trong trường `input` của tệp dữ liệu (do `du_lieu_trich`
# dựng), giống hệt lúc suy luận — khác một chữ là lệch phân phối.
LOI_NHAC_HE_THONG_TRICH = (
    "Bạn là một trợ lý AI chuyên khoa y tế bằng tiếng Việt. "
    "Nhiệm vụ của bạn là đọc cuộc hội thoại lâm sàng và trích ra các bản ghi "
    "thông tin có cấu trúc dưới dạng JSON, theo đúng hướng dẫn được cung cấp."
)


# ═══ dung_chuoi() — Dựng văn bản theo mẫu chat Qwen3 ══════════════════════════════════
# Tắt thinking ở cả huấn luyện và suy luận để mặt nạ nhãn không lệch.
def dung_chuoi(tok, hoi_thoai, benh_an=None, nhiem_vu="benh_an"):
    """Dựng văn bản theo template chat.

    `enable_thinking=False` ở CẢ hai chỗ — train và suy luận — vì Qwen3 chèn
    cặp <think></think> rỗng nếu để mặc định. Lệch một token thì mặt nạ nhãn
    lệch theo, và mô hình học nhầm chỗ suốt 200 bước.
    """
    if nhiem_vu == "trich":
        # `hoi_thoai` ở đây ĐÃ là lời nhắc đầy đủ, dùng nguyên văn.
        msgs = [{"role": "system", "content": LOI_NHAC_HE_THONG_TRICH},
                {"role": "user", "content": hoi_thoai}]
    else:
        msgs = [{"role": "system", "content": LOI_NHAC_HE_THONG},
                {"role": "user",
                 "content": LOI_NHAC_NGUOI_DUNG.format(hoi_thoai=hoi_thoai)}]
    if benh_an is None:
        return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                       enable_thinking=False)
    msgs = msgs + [{"role": "assistant", "content": benh_an}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False,
                                   enable_thinking=False)


# ═══ class TapLamSang — Tập dữ liệu SFT, loại mẫu quá dài thay vì cắt ═════════════════
# Cắt đuôi sẽ mất bệnh án ở cuối chuỗi nên mẫu dài bị loại.
class TapLamSang:
    """LOẠI mẫu quá dài thay vì cắt đuôi.

    Bản gốc cắt `full_ids[:max_length]`. Vì bệnh án nằm ở CUỐI chuỗi, cắt đuôi
    là cắt mất chính phần cần học — mô hình học một bệnh án cụt đuôi.
    Ở 1024 token chỉ khoảng 1,4% mẫu vượt, nên loại đi rẻ hơn nhiều.

    Không kế thừa `torch.utils.data.Dataset`: Trainer chỉ cần __len__ và
    __getitem__, còn bộ test thì chạy được ở máy không có torch.
    """

    def __init__(self, duong_dan_jsonl, tok, do_dai_toi_da=1024,
                 nhiem_vu="benh_an"):
        self.tok, self.do_dai_toi_da = tok, do_dai_toi_da
        self.nhiem_vu = nhiem_vu
        self.mau, self.bi_loai = [], []
        with open(duong_dan_jsonl, encoding="utf-8") as f:
            for dong in f:
                if not dong.strip():
                    continue
                m = json.loads(dong)
                chuoi = dung_chuoi(tok, m["input"], m["output"],
                                   nhiem_vu) + tok.eos_token
                if len(tok.encode(chuoi, add_special_tokens=False)) > do_dai_toi_da:
                    self.bi_loai.append(m["id"])
                else:
                    self.mau.append(m)

    def __len__(self):
        return len(self.mau)

    def __getitem__(self, i):
        """Trả DANH SÁCH thuần, không phải tensor — dùng tensor ở khâu gom lô.

        Nhờ vậy phép kiểm mặt nạ nhãn (cái dễ sai nhất) chạy được trên máy
        không có torch, tức bắt lỗi trước khi đẩy lên GPU.
        """
        m = self.mau[i]
        chuoi_nhac = dung_chuoi(self.tok, m["input"], nhiem_vu=self.nhiem_vu)
        chuoi_du = dung_chuoi(self.tok, m["input"], m["output"],
                              self.nhiem_vu) + self.tok.eos_token
        id_nhac = self.tok.encode(chuoi_nhac, add_special_tokens=False)
        id_du = self.tok.encode(chuoi_du, add_special_tokens=False)
        nhan = [-100] * len(id_nhac) + id_du[len(id_nhac):]
        return {"input_ids": id_du, "labels": nhan[:len(id_du)]}


# ═══ gom_lo() — Gom các mẫu thành lô có đệm phải ══════════════════════════════════════
# Nhãn đệm là -100 để không tính loss ở chỗ đệm.
def gom_lo(lo, ma_dem):
    """Đệm phải. Nhãn đệm bằng -100 chứ không bằng ma_dem — đệm bằng ma_dem
    thì mô hình bị tính loss trên chỗ đệm."""
    import torch
    n = max(len(x["input_ids"]) for x in lo)
    ids = torch.tensor([list(x["input_ids"]) + [ma_dem] * (n - len(x["input_ids"]))
                        for x in lo], dtype=torch.long)
    nhan = torch.tensor([list(x["labels"]) + [-100] * (n - len(x["labels"]))
                         for x in lo], dtype=torch.long)
    return {"input_ids": ids, "attention_mask": ids.ne(ma_dem).long(), "labels": nhan}


# ═══ kiem_mat_na() — Kiểm mặt nạ nhãn trước khi huấn luyện ════════════════════════════
# Giải mã phần có nhãn và đối chiếu bệnh án gốc; lệch thì dừng.
def kiem_mat_na(tap, tok, so_mau=3):
    """Bước 1 của Task 6 — chạy TRƯỚC khi train.

    Giải mã phần nhãn (bỏ -100) và đối chiếu với bệnh án gốc. Nếu lệch thì
    dừng hẳn: train 200 bước với mặt nạ sai là ném đi 2 giờ GPU.
    """
    for i in range(min(so_mau, len(tap))):
        x = tap[i]
        nhan = [t for t in x["labels"] if t != -100]
        van = tok.decode(nhan)
        goc = tap.mau[i]["output"]
        print("")
        print(f"--- mau {i} ({tap.mau[i]['id']}) ---")
        print(f"nhan: {van[:100]!r}")
        print(f"goc : {goc[:100]!r}")
        khop = van.strip().startswith(goc[:40].strip())
        print(f"nhan bat dau dung benh an goc: {'OK' if khop else 'LECH'}")
        if not khop:
            raise SystemExit("Mat na nhan lech. Khong train.")
    print("")
    print(f"Mat na nhan dung o {min(so_mau, len(tap))} mau.")


# ─── _van_tay_du_lieu() — Tạo dấu vân tay của tập huấn luyện ──────────────────────────
# Số mẫu cộng băm mẫu đầu và mẫu cuối, đủ nhận ra tập đã đổi.
def _van_tay_du_lieu(tap):
    """Dấu vân tay của tập huấn luyện, đủ để biết nó có đổi không.

    Không băm toàn bộ tập: nó có thể vài chục nghìn mẫu và việc này chạy ở đầu
    mỗi lần train. Ba con số dưới đây đã đủ — hai bộ dữ liệu khác nhau gần như
    không bao giờ trùng cả ba:

        số mẫu  +  băm của mẫu ĐẦU  +  băm của mẫu CUỐI

    Cách này bắt được cả trường hợp nguy hiểm nhất: cùng số mẫu nhưng nội dung
    khác (sinh lại với seed khác, hoặc đổi bộ sinh).
    """
    import hashlib

    def _bam(m):
        s = json.dumps(m, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

    n = len(tap)
    return {"so_mau": n,
            "bam_dau": _bam(tap[0]) if n else "",
            "bam_cuoi": _bam(tap[n - 1]) if n else ""}


# ═══ main() — Điểm vào: huấn luyện SFT adapter Qwen3 ══════════════════════════════════
# Kiểm mặt nạ nếu được yêu cầu, rồi huấn luyện LoRA 4-bit và lưu adapter.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=duong_dan.MODEL_CHINH)
    ap.add_argument("--buoc", type=int, default=200)
    ap.add_argument("--do-dai", type=int, default=1024)
    ap.add_argument("--nhiem-vu", choices=["benh_an", "trich"], default="benh_an")
    # Tệp dữ liệu và hậu tố thư mục adapter. Mặc định giữ nguyên hành vi cũ.
    # Thêm 11/09/2026 để huấn luyện nhánh A trên BỘ TỰ SINH (`viet_train.jsonl`,
    # bản tham chiếu nằm ở `output`): adapter A cũ học trên dữ liệu cuộc thi — thứ
    # ban tổ chức khuyên không dùng — và so A với đường ống chỉ công bằng khi hai
    # bên học trên CÙNG một bộ.
    ap.add_argument("--tep-train", default=None)
    ap.add_argument("--tep-val", default=None)
    ap.add_argument("--hau-to", default="",
                    help="them vao ten thu muc adapter, vi du -viet5")
    ap.add_argument("--kiem-mat-na", action="store_true",
                    help="chi kiem mat na nhan roi thoat, khong train")
    # Thêm 21/11/2026: tính loss THEO ĐOẠN để không tạo logits cho cả chuỗi 4.096
    # token (đỉnh bộ nhớ ~10,5 GiB -> OOM trên RTX 3060). Loss bằng loss gốc (xem
    # `src/huan_luyen/loss_theo_doan.py`), nên checkpoint cũ vẫn chạy tiếp được. Mặc định TẮT:
    # không có cờ thì hành vi y hệt trước đây.
    ap.add_argument("--loss-theo-doan", action="store_true",
                    help="tinh cross-entropy theo doan de giam dinh VRAM")
    ap.add_argument("--kich-thuoc-doan", type=int, default=512)
    a = ap.parse_args()

    # Chỉ nạp AutoTokenizer trước. `Trainer` kéo theo `datasets` -> `pandas`,
    # và trên HoaiDuc `pandas._libs` bị chính sách Application Control của
    # Windows chặn. Phép kiểm mặt nạ không cần Trainer, nên dùng nó chặn.
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(a.model)
    tok.pad_token = tok.eos_token

    d = duong_dan.THU_MUC_DU_LIEU
    if a.nhiem_vu == "trich":
        ten_train, ten_val = "trich_train.jsonl", "trich_giu_lai.jsonl"
    else:
        ten_train, ten_val = "train_tang_cuong.jsonl", "phat_trien.jsonl"
    ten_train, ten_val = a.tep_train or ten_train, a.tep_val or ten_val
    # Dữ liệu do GPT sinh chỉ để đo, kể cả tệp val (nó chọn checkpoint).
    from src.bo_du_lieu import nap_du_lieu as _dl
    _dl.chan_du_lieu_gpt([ten_train, ten_val])
    tap_train = TapLamSang(d / ten_train, tok, a.do_dai, a.nhiem_vu)
    tap_val = TapLamSang(d / ten_val, tok, a.do_dai, a.nhiem_vu)
    print(f"train {len(tap_train)} mau (loai {len(tap_train.bi_loai)} qua {a.do_dai} token)")
    print(f"val   {len(tap_val)} mau (loai {len(tap_val.bi_loai)})")

    if a.kiem_mat_na:
        kiem_mat_na(tap_train, tok)
        return
    kiem_mat_na(tap_train, tok, so_mau=1)

    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import (AutoModelForCausalLM, BitsAndBytesConfig,
                              Trainer, TrainingArguments)

    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True,
                             bnb_4bit_quant_type="nf4",
                             bnb_4bit_compute_dtype=torch.bfloat16)
    model = AutoModelForCausalLM.from_pretrained(a.model, quantization_config=bnb,
                                                 device_map="auto")
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, LoraConfig(
        r=16, lora_alpha=32, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"]))
    model.print_trainable_parameters()
    model.gradient_checkpointing_enable()

    import torch as _torch
    CO_BF16 = _torch.cuda.is_available() and _torch.cuda.is_bf16_supported()
    print(f"[kieu so] bf16={CO_BF16} fp16={not CO_BF16} "
          f"({_torch.cuda.get_device_name(0) if _torch.cuda.is_available() else 'khong co GPU'})",
          flush=True)

    ten = a.model.split("/")[-1].replace(".", "_").lower()
    hau_to = "" if a.nhiem_vu == "benh_an" else "-trich"
    thu_muc = duong_dan.THU_MUC_MO_HINH / f"nen-{ten}{hau_to}{a.hau_to}"
    tham_so = TrainingArguments(
        output_dir=str(thu_muc), learning_rate=2e-4,
        per_device_train_batch_size=1, per_device_eval_batch_size=1,
        gradient_accumulation_steps=16, max_steps=a.buoc,
        weight_decay=0.01, lr_scheduler_type="cosine", warmup_ratio=0.03,
        logging_steps=5, eval_strategy="steps", eval_steps=50,
        save_strategy="steps", save_steps=50, save_total_limit=2,
        load_best_model_at_end=True, metric_for_best_model="loss",
        greater_is_better=False,
        # Card của máy nhà (RTX 3060, Ampere) có bf16. Card T4 của Kaggle KHÔNG có,
        # nên ở đó phải fp16 kèm loss scaling. Đây là một KHÁC BIỆT VỀ SỐ HỌC giữa
        # hai máy: adapter huấn luyện ở T4 không phải cùng một thứ với adapter huấn
        # luyện ở máy nhà, và phải ghi rõ điều đó mỗi lần báo cáo.
        bf16=CO_BF16, fp16=not CO_BF16,
        optim="paged_adamw_8bit", remove_unused_columns=False, report_to="none")

    if a.loss_theo_doan:
        from src.huan_luyen.loss_theo_doan import tao_trainer_loss_theo_doan
        Trainer = tao_trainer_loss_theo_doan(Trainer, a.kich_thuoc_doan)
        print(f"[loss] theo doan, moi doan {a.kich_thuoc_doan} token", flush=True)
    trainer = Trainer(model=model, args=tham_so, train_dataset=tap_train,
                      eval_dataset=tap_val,
                      data_collator=lambda b: gom_lo(b, tok.pad_token_id))
    # Chạy tiếp từ checkpoint gần nhất nếu có. Một lần train mất vài giờ, và
    # máy này đã một lần báo `CUDA error: unspecified launch failure` giữa
    # chừng — mất 50 bước thì chấp nhận được, mất cả lần chạy thì không.
    #
    # NHƯNG chỉ được chạy tiếp khi DỮ LIỆU KHÔNG ĐỔI. Đã hỏng thật 10/09/2026:
    # bộ dữ liệu đổi từ 3.000 sang 5.000 ca, checkpoint cũ của bộ 3.000 vẫn nằm
    # trong thư mục, và lần chạy mới TỰ ĐỘNG chạy tiếp từ đó — huấn luyện 300
    # bước trên bộ cũ rồi 100 bước trên bộ mới, ra một adapter lai giữa hai bộ.
    #
    # Không có gì báo. Chỉ phát hiện vì `eval_loss` ở các bước đầu TRÙNG TỪNG
    # CHỮ SỐ với lần chạy trước, và vì nó TĂNG lên ở hai bước cuối (0,0003 ->
    # 0,0016) — dấu hiệu phân phối dữ liệu đổi dưới chân mô hình.
    van_tay = _van_tay_du_lieu(tap_train)
    tep_van_tay = thu_muc / "van_tay_du_lieu.json"
    co_ckpt = any(thu_muc.glob("checkpoint-*")) if thu_muc.exists() else False
    if co_ckpt:
        cu = None
        if tep_van_tay.exists():
            cu = json.loads(tep_van_tay.read_text(encoding="utf-8"))
        if cu != van_tay:
            raise SystemExit(
                f"TU CHOI chay tiep: du lieu huan luyen DA DOI.\n"
                f"  checkpoint trong {thu_muc} thuoc ve: {cu}\n"
                f"  du lieu dang dung        : {van_tay}\n"
                f"Chay tiep se cho ra mot adapter lai giua hai bo du lieu.\n"
                f"Xoa cac thu muc checkpoint-* roi chay lai tu dau.")
        print(f"Tim thay checkpoint trong {thu_muc}, du lieu khop, chay tiep.",
              flush=True)
    thu_muc.mkdir(parents=True, exist_ok=True)
    tep_van_tay.write_text(json.dumps(van_tay, ensure_ascii=False),
                           encoding="utf-8")
    trainer.train(resume_from_checkpoint=co_ckpt or None)
    dich = thu_muc / "best_checkpoint"
    trainer.save_model(str(dich))
    tok.save_pretrained(str(dich))
    print(f"Xong. Adapter: {dich}")


if __name__ == "__main__":
    main()
