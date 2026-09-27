# Do DO TRE cua khau trich tren Kaggle 2xT4: cung 5 ca, bon cau hinh, roi thu vLLM.
#
# CAU HOI: 4 phut/ca di dau — do nen 4 bit (bitsandbytes), do adapter chua gop, hay
# do ep luoc do JSON (lm-format-enforcer chay Python o MOI token)?
#
#   card 0   (1) nf4 + adapter + ep JSON      = dieu kien HoaiDuc (da cham)
#            (2) nf4 + adapter, KHONG ep      = dieu kien lan chay Kaggle 16/09 (thieu thu vien)
#   card 1   (3) fp16 da gop adapter + ep JSON
#            (4) fp16 da gop adapter, KHONG ep
#   sau do   (5) vLLM fp16 da gop, KHONG ep   (thu; loi thi ghi loi, khong dung)
#
# Moi cau hinh ghi: giay, token ra, token/giay, JSON hop le, so phat bieu, va do KHOP
# voi cau hinh (1) — tang toc ma doi dau ra thi khong dung duoc cho ket qua da cham.
import json
import os
import subprocess
import sys
import time
from pathlib import Path

# Lan 1 (17/09): peft moi nhat goi torchao 0.10 co san tren Kaggle va vo o PeftModel
# tren mo hinh KHONG nen (cau hinh 3, 4, 5). Ghim phien ban HoaiDuc va go torchao.
subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "-q", "torchao"], check=False)
subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                "transformers==4.57.6", "peft==0.20.0", "bitsandbytes==0.50.2",
                "accelerate==1.14.0", "lm-format-enforcer==0.11.3"], check=False)

VAO = Path("/kaggle/input")
LAM = Path("/kaggle/working")
MO_HINH = "Qwen/Qwen3-4B"
SO_CA = 5
MAX_TOKEN = 3072


def goi():
    for src in sorted(VAO.glob("**/src")):
        if (src / "bakeoff.py").is_file():
            return src.parent
    sys.exit("khong thay dataset")


GOC = goi()
sys.path.insert(0, str(GOC))
ADAPTER = str(GOC / "models" / "nen-qwen3-4b-trich" / "best_checkpoint")
CA = [json.loads(x) for x in open(GOC / "data" / "thach_thuc_phuong_ngu_phat_trien.jsonl",
                                  encoding="utf-8") if x.strip()][:SO_CA]


def prompt_cua(tok, m):
    # Giong het bakeoff._vong_trich voi vi_du=True (nhanh.py goi mac dinh).
    from src.bakeoff import HUONG_DAN, VI_DU, danh_so_luot
    danh_so, _ = danh_so_luot(m["input"])
    loi_nhac = HUONG_DAN + f"\n\n{VI_DU}\n\nBây giờ đến lượt bạn."
    msgs = [{"role": "user", "content": f"{loi_nhac}\n\nHội thoại:\n{danh_so}"}]
    return tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                   enable_thinking=False)


def phat_bieu(van):
    try:
        i, j = van.index("{"), van.rindex("}") + 1
        return json.loads(van[i:j]).get("phat_bieu") or [], True
    except Exception:
        return [], False


def khoa(p):
    return (str(p.get("chu_the")), str(p.get("noi_dung")), str(p.get("do_chac_chan")),
            bool(p.get("phu_dinh")), str(p.get("tinh_huong")))


def chay_hf(ten, card, nf4, ep):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel
    thiet_bi = f"cuda:{card}"
    tok = AutoTokenizer.from_pretrained(MO_HINH)
    t0 = time.time()
    if nf4:
        bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True,
                                 bnb_4bit_quant_type="nf4",
                                 bnb_4bit_compute_dtype=torch.float16)
        m = AutoModelForCausalLM.from_pretrained(MO_HINH, quantization_config=bnb,
                                                 device_map={"": thiet_bi})
        m = PeftModel.from_pretrained(m, ADAPTER)
    else:
        m = AutoModelForCausalLM.from_pretrained(MO_HINH, torch_dtype=torch.float16,
                                                 device_map={"": thiet_bi})
        m = PeftModel.from_pretrained(m, ADAPTER).merge_and_unload()
    m.eval()
    nap = time.time() - t0
    prefix_fn = None
    if ep:
        from src.bakeoff import _ep_json
        prefix_fn = _ep_json(tok)
        if prefix_fn is None:
            return {"cau_hinh": ten, "loi": "khong nap duoc lm-format-enforcer"}
    kq = []
    for c in CA:
        inp = tok(prompt_cua(tok, c), return_tensors="pt").to(thiet_bi)
        torch.cuda.synchronize(card)
        t = time.time()
        with torch.no_grad():
            out = m.generate(**inp, max_new_tokens=MAX_TOKEN, do_sample=False,
                             pad_token_id=tok.eos_token_id, prefix_allowed_tokens_fn=prefix_fn)
        torch.cuda.synchronize(card)
        giay = time.time() - t
        vao = inp["input_ids"].shape[1]
        ra = out[0].shape[0] - vao
        van = tok.decode(out[0][vao:], skip_special_tokens=True)
        ps, ok = phat_bieu(van)
        kq.append({"id": c["id"], "giay": round(giay, 1), "token_vao": vao, "token_ra": ra,
                   "token_giay": round(ra / giay, 2), "json_ok": ok, "so_pb": len(ps),
                   "van": van})
        print(f"[{ten}] {c['id']}: {giay:.0f}s, {ra} token, {ra / giay:.1f} tok/s, json {ok}",
              flush=True)
    del m
    torch.cuda.empty_cache()
    return {"cau_hinh": ten, "nap_giay": round(nap, 1), "ca": kq}


def chay_nhom(cac, card, tep):
    kq = [chay_hf(ten, card, nf4, ep) for ten, nf4, ep in cac]
    Path(tep).write_text(json.dumps(kq, ensure_ascii=False), encoding="utf-8")


if len(sys.argv) > 1 and sys.argv[1] == "nhom":
    card = int(sys.argv[2])
    if card == 0:
        # (2) da do o lan 1: 199 s/ca, 5,98 tok/s. Lan nay chi chay lai (1) lam moc so khop.
        chay_nhom([("1-nf4-ep", True, True)], 0, LAM / "nhom0.json")
    else:
        chay_nhom([("3-fp16-gop-ep", False, True), ("4-fp16-gop-khong-ep", False, False)], 1, LAM / "nhom1.json")
    sys.exit(0)

# Hai nhom song song, moi nhom mot card.
p0 = subprocess.Popen([sys.executable, __file__, "nhom", "0"])
time.sleep(30)
p1 = subprocess.Popen([sys.executable, __file__, "nhom", "1"])
p0.wait()
p1.wait()

tat_ca = []
for tep in ("nhom0.json", "nhom1.json"):
    if (LAM / tep).exists():
        tat_ca += json.loads((LAM / tep).read_text(encoding="utf-8"))

# (5) vLLM: gop adapter ra dia roi phuc vu bang vLLM. Loi o bat ky buoc nao thi ghi lai.
try:
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "vllm"], check=True, timeout=1500)
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    gop = LAM / "gop-fp16"
    tok = AutoTokenizer.from_pretrained(MO_HINH)
    m = AutoModelForCausalLM.from_pretrained(MO_HINH, torch_dtype=torch.float16, device_map={"": "cpu"})
    PeftModel.from_pretrained(m, ADAPTER).merge_and_unload().save_pretrained(gop)
    tok.save_pretrained(gop)
    del m
    from vllm import LLM, SamplingParams
    llm = LLM(model=str(gop), dtype="float16", max_model_len=8192, gpu_memory_utilization=0.9)
    sp = SamplingParams(temperature=0, max_tokens=MAX_TOKEN)
    kq = []
    for c in CA:
        t = time.time()
        o = llm.generate([prompt_cua(tok, c)], sp)[0]
        giay = time.time() - t
        ra = len(o.outputs[0].token_ids)
        van = o.outputs[0].text
        ps, ok = phat_bieu(van)
        kq.append({"id": c["id"], "giay": round(giay, 1), "token_ra": ra,
                   "token_giay": round(ra / giay, 2), "json_ok": ok, "so_pb": len(ps), "van": van})
        print(f"[5-vllm] {c['id']}: {giay:.0f}s, {ra} token, {ra / giay:.1f} tok/s", flush=True)
    tat_ca.append({"cau_hinh": "5-vllm-fp16-gop-khong-ep", "ca": kq})
except Exception as e:                                           # noqa: BLE001
    tat_ca.append({"cau_hinh": "5-vllm-fp16-gop-khong-ep", "loi": repr(e)[:500]})
    print("vLLM loi:", repr(e)[:300], flush=True)

# Tong hop va do KHOP voi cau hinh (1).
goc = next((x for x in tat_ca if x["cau_hinh"] == "1-nf4-ep" and "ca" in x), None)
bang = []
for x in tat_ca:
    if "ca" not in x:
        bang.append({"cau_hinh": x["cau_hinh"], "loi": x.get("loi")})
        continue
    tong_giay = sum(c["giay"] for c in x["ca"])
    tong_token = sum(c["token_ra"] for c in x["ca"])
    dong = {"cau_hinh": x["cau_hinh"], "giay_moi_ca": round(tong_giay / len(x["ca"]), 1),
            "token_giay": round(tong_token / tong_giay, 2),
            "json_ok": sum(c["json_ok"] for c in x["ca"]), "so_ca": len(x["ca"])}
    if goc:
        trung_khit = trung_pb = tong_pb = 0
        for a, b in zip(goc["ca"], x["ca"]):
            trung_khit += a["van"].strip() == b["van"].strip()
            pa = {khoa(p) for p in phat_bieu(a["van"])[0]}
            pb = {khoa(p) for p in phat_bieu(b["van"])[0]}
            trung_pb += len(pa & pb)
            tong_pb += len(pa | pb)
        dong["trung_khit_voi_1"] = f"{trung_khit}/{len(x['ca'])}"
        dong["phat_bieu_trung_voi_1"] = round(trung_pb / tong_pb, 3) if tong_pb else None
    bang.append(dong)
(LAM / "ket_qua_do.json").write_text(json.dumps({"bang": bang, "chi_tiet": tat_ca},
                                                ensure_ascii=False, indent=1), encoding="utf-8")
print("\n==== BANG ====")
for d in bang:
    print(json.dumps(d, ensure_ascii=False), flush=True)
