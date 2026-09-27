# -*- coding: utf-8 -*-
# CHAY NHANH A VA A+ THE HE 8 tren 4 bo thu thach, Kaggle 2xT4 (22/09/2026).
#
# VI SAO. Bang ket qua the he 8 moi co B, C, C_khoa, C_khoa_hoi. Nhanh A (viet thang
# ho so) va A+ (A roi tu soat) la hai moc so quan trong nhat cua du an: neu A+ ngang
# C thi toan bo bieu dien trung gian la thua. Chua chay tren the he 8.
#
# ADAPTER NHANH A lay tu DAU RA cua kernel `meditrace-th8-nhanh-a` (kernel_sources), khong
# tai len dataset lai. Adapter do HUAN LUYEN BANG fp16 tren T4 — khac may nha dung
# bf16. Khi so A voi C phai ghi ro cho nay.
#
# CHIA CARD: card 0 chay doi_chu_the + dinh_chinh (140 ca), card 1 chay nhieu_asr +
# phuong_ngu (160 ca). Moi card chay A het hai bo roi moi chay A+ (A+ can ket qua A).
#
# max_token: nhanh A dung mac dinh 512 cua `chay_A`. Da kiem 22/09: ho so mau the he 8
# dai nhat ~270 token, lan chay A cu dai nhat 226 token, khong ca nao cham tran.
#
# CHAM: A viet van xuoi nen KHONG cham bang bo cham muc menh de. Cham bang
# `src.cham_lai_bang_quy_gan`, cung thuoc do quy gan ap cho phan van ban cua moi nhanh.
#
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

VAO = Path("/kaggle/input")
LAM = Path("/kaggle/working")
GOC = LAM / "meditrace"
THE_HE = "8"
MO_HINH = "Qwen/Qwen3-4B"
PHAN = {
    0: ["thach_thuc_doi_chu_the_phat_trien", "thach_thuc_dinh_chinh_phat_trien"],
    1: ["thach_thuc_nhieu_asr_phat_trien", "thach_thuc_phuong_ngu_phat_trien"],
}


def goi_du_lieu() -> Path:
    for src in sorted(VAO.glob("**/src")):
        if (src / "nhanh.py").is_file() and (src.parent / "data").is_dir():
            return src.parent
    raise SystemExit(f"khong thay dataset co src/nhanh.py trong {VAO}")


def tim_adapter() -> Path:
    """Adapter nhanh A trong dau ra cua kernel huan luyen, o BAT KY do sau nao."""
    for ung in sorted(VAO.glob("**/models/nen-qwen3-4b/best_checkpoint")):
        if (ung / "adapter_model.safetensors").is_file() and "trich" not in str(ung):
            return ung
    raise SystemExit("khong thay adapter nhanh A (models/nen-qwen3-4b/best_checkpoint)")


def chuan_bi() -> Path:
    goi = goi_du_lieu()
    print("dataset:", goi, flush=True)
    if GOC.exists():
        shutil.rmtree(GOC)
    shutil.copytree(goi, GOC)
    (GOC / "data").mkdir(exist_ok=True)
    cu = sorted((GOC / "data").glob("ra_A*.jsonl"))
    if cu:
        raise SystemExit(f"dataset co ket qua A cu {[t.name for t in cu]} - khong chay")
    return GOC


def thu_hoach(goc: Path) -> None:
    for tep in (goc / "data").glob("ra_A*.jsonl"):
        shutil.copy2(tep, LAM / tep.name)


def chuoi_lenh(tap_list, adapter):
    """Mot card: A cho moi bo, roi A+ cho moi bo."""
    lenh = []
    for tap in tap_list:
        lenh.append([sys.executable, "-m", "src.nhanh", "--nhanh", "A",
                     "--model", MO_HINH, "--adapter", adapter, "--tap", tap])
    for tap in tap_list:
        lenh.append([sys.executable, "-m", "src.nhanh", "--nhanh", "A+",
                     "--model", MO_HINH, "--adapter", adapter, "--tap", tap,
                     "--tu", f"ra_A_{tap}.jsonl"])
    return lenh


def main() -> None:
    subprocess.run(["nvidia-smi", "--query-gpu=index,name,memory.total",
                    "--format=csv,noheader"], check=False)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "transformers==4.57.6", "peft==0.20.0", "bitsandbytes==0.50.2",
                    "accelerate==1.14.0", "lm-format-enforcer==0.11.3"], check=True)
    goc = chuan_bi()
    adapter = tim_adapter()
    print("adapter nhanh A:", adapter, flush=True)

    tat_ca = [t for ds in PHAN.values() for t in ds]
    ma = subprocess.call([sys.executable, str(goc / "tools" / "kiem-the-he.py"),
                          THE_HE, *tat_ca], cwd=goc)
    if ma != 0:
        sys.exit("du lieu tren may khong phai the he " + THE_HE)

    # Moi card mot tien trinh nen, chay tuan tu chuoi lenh cua no.
    kich_ban = LAM / "chuoi_card.py"
    kich_ban.write_text(
        "import json, os, subprocess, sys\n"
        "lenh = json.loads(sys.argv[1])\n"
        "for l in lenh:\n"
        "    print('[chay]', ' '.join(l), flush=True)\n"
        "    ma = subprocess.call(l)\n"
        "    print('[ma thoat]', ma, flush=True)\n"
        "    if ma != 0:\n"
        "        sys.exit(ma)\n", encoding="utf-8")
    tien_trinh = []
    for card, taps in PHAN.items():
        log = open(LAM / f"log_card{card}.txt", "a", encoding="utf-8")
        env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(card), PYTHONIOENCODING="utf-8")
        p = subprocess.Popen([sys.executable, str(kich_ban),
                              json.dumps(chuoi_lenh(taps, str(adapter)))],
                             cwd=goc, env=env, stdout=log, stderr=subprocess.STDOUT)
        tien_trinh.append((card, p, log))
        time.sleep(20)

    bat_dau = time.time()
    while any(p.poll() is None for _c, p, _l in tien_trinh):
        time.sleep(300)
        thu_hoach(goc)
        dem = {t.name: sum(1 for _ in open(t, encoding="utf-8"))
               for t in sorted(LAM.glob("ra_A*.jsonl"))}
        print(f"[{(time.time() - bat_dau) / 60:.0f} phut] {dem}", flush=True)

    for card, p, log in tien_trinh:
        log.close()
        print(f"card {card}: ma thoat {p.returncode}", flush=True)
        print((LAM / f"log_card{card}.txt").read_text(encoding="utf-8",
                                                      errors="replace")[-2000:], flush=True)
    thu_hoach(goc)
    (LAM / "ghi_chu_may.json").write_text(json.dumps(
        {"may_chay": "kaggle-2xT4", "viec": "nhanh A va A+ tren 4 bo thu thach",
         "the_he": THE_HE, "mo_hinh": MO_HINH, "adapter": str(adapter),
         "kieu_so_adapter": "fp16 (T4 khong co bf16)", "max_token_A": 512,
         "cac_tap": tat_ca}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("ket qua o /kaggle/working:", sorted(os.listdir(LAM)), flush=True)


if __name__ == "__main__":
    main()
