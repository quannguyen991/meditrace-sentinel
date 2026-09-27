# -*- coding: utf-8 -*-
# HUAN LUYEN NHANH A THE HE 8 tren Kaggle T4 (19/09/2026).
#
# Nhanh A = hoi thoai vao, ban nhap ra, mot lan goi mo hinh. Adapter nhanh A cua the
# he 8 chua co o dau: adapter cu nam tren may HoaiDuc, ma du an da chot chi dung may
# nay voi Kaggle. Nen phai huan luyen lai.
#
# MOT KHAC BIET PHAI GHI RO KHI BAO CAO: card T4 KHONG co bf16. May nha (RTX 3060)
# huan luyen bang bf16; o day `train_baseline` tu chuyen sang fp16 kem loss scaling.
# Hai adapter vi the khong phai cung mot thu ve so hoc. Khi so nhanh A voi nhanh C
# phai noi ro cho nay.
#
# Phien Kaggle toi da 12 gio. Trainer luu checkpoint moi 50 buoc; cu 10 phut chep
# thu muc models ra /kaggle/working mot lan, nen het gio dot ngot cung con checkpoint.
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
TEP_TRAIN = "viet_train.jsonl"
TEP_VAL = "viet_phat_trien.jsonl"
SO_BUOC = "200"


def goi_du_lieu() -> Path:
    """Thu muc dataset — tim theo `src/`, o BAT KY do sau nao.

    Kaggle gan dataset o /kaggle/input/datasets/<tai khoan>/<ten>, khong phai
    /kaggle/input/<ten> nhu tai lieu cu. Tim de quy thi khong phu thuoc cach gan.
    """
    for src in sorted(VAO.glob("**/src")):
        if (src / "nhanh.py").is_file():
            return src.parent
    raise SystemExit(f"khong thay dataset co src/nhanh.py trong {VAO}")


def chuan_bi() -> Path:
    goi = goi_du_lieu()
    print("dataset:", goi, flush=True)
    if GOC.exists():
        shutil.rmtree(GOC)
    shutil.copytree(goi, GOC)
    (GOC / "data").mkdir(exist_ok=True)
    # Dataset khong duoc co tep dem: tep dem the he 7 trong dataset (neu co) la khong ep.
    cu = sorted((GOC / "data").glob("trich_*.jsonl"))
    if cu:
        raise SystemExit(f"dataset co tep dem cu {[t.name for t in cu]} - khong chay")
    return GOC


def thu_hoach(goc: Path) -> None:
    for mau in ("ra_*.jsonl", "trich_*.jsonl"):
        for tep in (goc / "data").glob(mau):
            shutil.copy2(tep, LAM / tep.name)



def chep_mo_hinh(goc: Path) -> None:
    """Chep thu muc adapter ra /kaggle/working. Chi chep tep nho, bo tokenizer thua."""
    nguon = goc / "models"
    if not nguon.is_dir():
        return
    dich = LAM / "models"
    if dich.exists():
        shutil.rmtree(dich, ignore_errors=True)
    shutil.copytree(nguon, dich, ignore=shutil.ignore_patterns("*.pt", "optimizer*"))


def main() -> None:
    subprocess.run(["nvidia-smi", "--query-gpu=index,name,memory.total",
                    "--format=csv,noheader"], check=False)
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "transformers==4.57.6", "peft==0.20.0", "bitsandbytes==0.50.2",
                    "accelerate==1.14.0", "lm-format-enforcer==0.11.3"], check=True)
    goc = chuan_bi()

    ma = subprocess.call([sys.executable, str(goc / "tools" / "kiem-the-he.py"),
                          THE_HE, "viet_train", "viet_phat_trien"], cwd=goc)
    if ma != 0:
        sys.exit("du lieu tren may khong phai the he " + THE_HE)

    lenh = [sys.executable, "-m", "src.train_baseline", "--model", MO_HINH,
            "--nhiem-vu", "benh_an", "--buoc", SO_BUOC,
            "--tep-train", TEP_TRAIN, "--tep-val", TEP_VAL]
    log = open(LAM / "log_train_nhanh_a.txt", "a", encoding="utf-8")
    moi_truong = dict(os.environ, CUDA_VISIBLE_DEVICES="0", PYTHONIOENCODING="utf-8")
    print("[train]", " ".join(lenh), flush=True)
    p = subprocess.Popen(lenh, cwd=goc, env=moi_truong, stdout=log,
                         stderr=subprocess.STDOUT)

    bat_dau = time.time()
    while p.poll() is None:
        time.sleep(600)
        chep_mo_hinh(goc)
        duoi = (LAM / "log_train_nhanh_a.txt").read_text(encoding="utf-8",
                                                         errors="replace")[-400:]
        print(f"[{(time.time() - bat_dau) / 60:.0f} phut]\n{duoi}", flush=True)

    log.close()
    chep_mo_hinh(goc)
    print("ma thoat:", p.returncode, flush=True)
    toan = (LAM / "log_train_nhanh_a.txt").read_text(encoding="utf-8", errors="replace")
    print("--- duoi log:\n" + toan[-3000:], flush=True)
    (LAM / "ghi_chu_may.json").write_text(json.dumps(
        {"may_chay": "kaggle-T4", "viec": "huan luyen nhanh A", "the_he": THE_HE,
         "mo_hinh": MO_HINH, "so_buoc": SO_BUOC, "tep_train": TEP_TRAIN,
         "tep_val": TEP_VAL,
         "kieu_so": "fp16 (T4 khong co bf16) - KHAC may nha dung bf16"},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print("ket qua o /kaggle/working:", sorted(os.listdir(LAM)), flush=True)


if __name__ == "__main__":
    main()
