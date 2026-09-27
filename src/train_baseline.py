# -*- coding: utf-8 -*-
"""Huan luyen mo hinh NEN (nhanh A): hoi thoai -> benh an, mot buoc.

Day la moc de so sanh. Moi nhanh sau (A+, B, C, D) phai hon duoc no thi
bieu dien trung gian moi co ly do ton tai.

BON SUA DOI so voi `train.py` goc — moi cai co ly do, khong phai chinh cho dep:

  so buoc   50 -> 200      50 x grad_accum 16 = 800 mau, chua toi 0,65 epoch
  kieu so   fp16 -> bf16   RTX 3060 la Ampere; bf16 khong can loss scaling
  do dai    cat -> LOAI    cat tu duoi la cat mat benh an, tuc cat mat NHAN
  nguon     train_split -> train_tang_cuong.jsonl  (tap cu chua mau giu rieng)

    python -m src.train_baseline --model Qwen/Qwen3-8B --kiem-mat-na
    python -m src.train_baseline --model Qwen/Qwen3-8B
"""
import argparse
import io
import json
import sys

from src import duong_dan

# torch nap TRE, trong tung ham. Ly do: bo test phai chay duoc tren may
# khong co GPU (laptop) de bat loi mat na nhan TRUOC khi day len HoaiDuc.
# Import o dau tep thi ca tep khong nap duoc o do, va test khong chay.

# Nguyen van tu train.py goc. KHONG sua — doi loi nhac la doi baseline,
# luc do so cua nhanh A khong so duoc voi ket qua cu nua.
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

# Nhiem vu thu hai: TRICH bang phat bieu, khong viet benh an. Loi nhac day
# du da nam san trong truong `input` cua tep du lieu (do `du_lieu_trich`
# dung), giong het luc suy luan — khac mot chu la lech phan phoi.
LOI_NHAC_HE_THONG_TRICH = (
    "Bạn là một trợ lý AI chuyên khoa y tế bằng tiếng Việt. "
    "Nhiệm vụ của bạn là đọc cuộc hội thoại lâm sàng và trích ra các bản ghi "
    "thông tin có cấu trúc dưới dạng JSON, theo đúng hướng dẫn được cung cấp."
)


def dung_chuoi(tok, hoi_thoai, benh_an=None, nhiem_vu="benh_an"):
    """Dung van ban theo template chat.

    `enable_thinking=False` o CA hai cho — train va suy luan — vi Qwen3 chen
    cap <think></think> rong neu de mac dinh. Lech mot token thi mat na nhan
    lech theo, va mo hinh hoc nham cho suot 200 buoc.
    """
    if nhiem_vu == "trich":
        # `hoi_thoai` o day DA la loi nhac day du, dung nguyen van.
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


class TapLamSang:
    """LOAI mau qua dai thay vi cat duoi.

    Ban goc cat `full_ids[:max_length]`. Vi benh an nam o CUOI chuoi, cat duoi
    la cat mat chinh phan can hoc — mo hinh hoc mot benh an cut duoi.
    O 1024 token chi khoang 1,4% mau vuot, nen loai di re hon nhieu.

    Khong ke thua `torch.utils.data.Dataset`: Trainer chi can __len__ va
    __getitem__, con bo test thi chay duoc o may khong co torch.
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
        """Tra DANH SACH thuan, khong phai tensor — dung tensor o khau gom lo.

        Nho vay phep kiem mat na nhan (cai de sai nhat) chay duoc tren may
        khong co torch, tuc bat loi truoc khi day len GPU.
        """
        m = self.mau[i]
        chuoi_nhac = dung_chuoi(self.tok, m["input"], nhiem_vu=self.nhiem_vu)
        chuoi_du = dung_chuoi(self.tok, m["input"], m["output"],
                              self.nhiem_vu) + self.tok.eos_token
        id_nhac = self.tok.encode(chuoi_nhac, add_special_tokens=False)
        id_du = self.tok.encode(chuoi_du, add_special_tokens=False)
        nhan = [-100] * len(id_nhac) + id_du[len(id_nhac):]
        return {"input_ids": id_du, "labels": nhan[:len(id_du)]}


def gom_lo(lo, ma_dem):
    """Dem phai. Nhan dem bang -100 chu khong bang ma_dem — dem bang ma_dem
    thi mo hinh bi tinh loss tren cho dem."""
    import torch
    n = max(len(x["input_ids"]) for x in lo)
    ids = torch.tensor([list(x["input_ids"]) + [ma_dem] * (n - len(x["input_ids"]))
                        for x in lo], dtype=torch.long)
    nhan = torch.tensor([list(x["labels"]) + [-100] * (n - len(x["labels"]))
                         for x in lo], dtype=torch.long)
    return {"input_ids": ids, "attention_mask": ids.ne(ma_dem).long(), "labels": nhan}


def kiem_mat_na(tap, tok, so_mau=3):
    """Buoc 1 cua Task 6 — chay TRUOC khi train.

    Giai ma phan nhan (bo -100) va doi chieu voi benh an goc. Neu lech thi
    dung han: train 200 buoc voi mat na sai la nem di 2 gio GPU.
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


def _van_tay_du_lieu(tap):
    """Dau van tay cua tap huan luyen, du de biet no co doi khong.

    Khong bam toan bo tap: no co the vai chuc nghin mau va viec nay chay o dau
    moi lan train. Ba con so duoi day da du — hai bo du lieu khac nhau gan nhu
    khong bao gio trung ca ba:

        so mau  +  bam cua mau DAU  +  bam cua mau CUOI

    Cach nay bat duoc ca truong hop nguy hiem nhat: cung so mau nhung noi dung
    khac (sinh lai voi seed khac, hoac doi bo sinh).
    """
    import hashlib

    def _bam(m):
        s = json.dumps(m, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

    n = len(tap)
    return {"so_mau": n,
            "bam_dau": _bam(tap[0]) if n else "",
            "bam_cuoi": _bam(tap[n - 1]) if n else ""}


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=duong_dan.MODEL_CHINH)
    ap.add_argument("--buoc", type=int, default=200)
    ap.add_argument("--do-dai", type=int, default=1024)
    ap.add_argument("--nhiem-vu", choices=["benh_an", "trich"], default="benh_an")
    # Tep du lieu va hau to thu muc adapter. Mac dinh giu nguyen hanh vi cu.
    # Them 11/09/2026 de huan luyen nhanh A tren BO TU SINH (`viet_train.jsonl`,
    # ban tham chieu nam o `output`): adapter A cu hoc tren du lieu cuoc thi — thu
    # ban to chuc khuyen khong dung — va so A voi duong ong chi cong bang khi hai
    # ben hoc tren CUNG mot bo.
    ap.add_argument("--tep-train", default=None)
    ap.add_argument("--tep-val", default=None)
    ap.add_argument("--hau-to", default="",
                    help="them vao ten thu muc adapter, vi du -viet5")
    ap.add_argument("--kiem-mat-na", action="store_true",
                    help="chi kiem mat na nhan roi thoat, khong train")
    a = ap.parse_args()

    # Chi nap AutoTokenizer truoc. `Trainer` keo theo `datasets` -> `pandas`,
    # va tren HoaiDuc `pandas._libs` bi chinh sach Application Control cua
    # Windows chan. Phep kiem mat na khong can Trainer, nen dung no chan.
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(a.model)
    tok.pad_token = tok.eos_token

    d = duong_dan.THU_MUC_DU_LIEU
    if a.nhiem_vu == "trich":
        ten_train, ten_val = "trich_train.jsonl", "trich_giu_lai.jsonl"
    else:
        ten_train, ten_val = "train_tang_cuong.jsonl", "phat_trien.jsonl"
    ten_train, ten_val = a.tep_train or ten_train, a.tep_val or ten_val
    # Du lieu do GPT sinh chi de do, ke ca tep val (no chon checkpoint).
    from src import du_lieu as _dl
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
        # Card cua may nha (RTX 3060, Ampere) co bf16. Card T4 cua Kaggle KHONG co,
        # nen o do phai fp16 kem loss scaling. Day la mot KHAC BIET VE SO HOC giua
        # hai may: adapter huan luyen o T4 khong phai cung mot thu voi adapter huan
        # luyen o may nha, va phai ghi ro dieu do moi lan bao cao.
        bf16=CO_BF16, fp16=not CO_BF16,
        optim="paged_adamw_8bit", remove_unused_columns=False, report_to="none")

    trainer = Trainer(model=model, args=tham_so, train_dataset=tap_train,
                      eval_dataset=tap_val,
                      data_collator=lambda b: gom_lo(b, tok.pad_token_id))
    # Chay tiep tu checkpoint gan nhat neu co. Mot lan train mat vai gio, va
    # may nay da mot lan bao `CUDA error: unspecified launch failure` giua
    # chung — mat 50 buoc thi chap nhan duoc, mat ca lan chay thi khong.
    #
    # NHUNG chi duoc chay tiep khi DU LIEU KHONG DOI. Da hong that 10/09/2026:
    # bo du lieu doi tu 3.000 sang 5.000 ca, checkpoint cu cua bo 3.000 van nam
    # trong thu muc, va lan chay moi TU DONG chay tiep tu do — huan luyen 300
    # buoc tren bo cu roi 100 buoc tren bo moi, ra mot adapter lai giua hai bo.
    #
    # Khong co gi bao. Chi phat hien vi `eval_loss` o cac buoc dau TRUNG TUNG
    # CHU SO voi lan chay truoc, va vi no TANG len o hai buoc cuoi (0,0003 ->
    # 0,0016) — dau hieu phan phoi du lieu doi duoi chan mo hinh.
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
