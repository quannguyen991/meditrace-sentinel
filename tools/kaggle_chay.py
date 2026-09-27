# -*- coding: utf-8 -*-
"""Kich ban chay TREN KAGGLE — hai the he thuc thi song song tren hai card T4.

Kaggle cap 2 card T4 trong mot phien, va quota tinh theo GIO PHIEN chu khong theo
so card. Nen chay hai tien trinh, moi tien trinh ghim mot card, la mot gio quota
doi duoc hai gio card.

Cach dung (dat trong kernel-metadata.json, xem tools/kaggle_goi.py):

    python kaggle_chay.py thach_thuc_phuong_ngu_phat_trien thach_thuc_nhieu_asr_phat_trien

BA DIEU PHAI GIU:

  1. TEP DEM. Buoc sinh ghi `data/trich_<tap>_3072_hl.jsonl` theo tung ca. Phien
     Kaggle toi da 12 gio, nen tep dem la thu duy nhat cho phep phien sau chay tiep
     phien truoc. Cuoi phien phai chep no ra /kaggle/working du an ve, va dau phien
     sau phai nap lai. Khong lam vay la moi phien deu bat dau tu ca so 1.
  2. VAN TAY BO DU LIEU. `tools/kiem-the-he.py` chay truoc, dung ngay neu du lieu
     tren may khong phai the he mong doi. Tren Kaggle de quen dong bo du lieu con de
     hon o may nha.
  3. GHI RO MAY. Ket qua chay tren T4 khong dam bao trung khit ket qua chay tren
     RTX 3060 cua HoaiDuc. Tep ra mang them truong `may_chay` de bao cao noi duoc
     bo nao chay o dau.
"""
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
THE_HE = "7"
MO_HINH = "Qwen/Qwen3-4B"
NHANH = ["B", "C", "C_khoa", "C_khoa_hoi"]
MAX_TOKEN = "3072"


def _goi_du_lieu() -> Path:
    """Thu muc dataset da gan vao phien — tim thu muc co `src/`."""
    for d in sorted(VAO.glob("*")):
        if (d / "src").is_dir():
            return d
    raise SystemExit(f"khong thay dataset co thu muc src/ trong {VAO}")


def chuan_bi() -> Path:
    goi = _goi_du_lieu()
    if GOC.exists():
        shutil.rmtree(GOC)
    shutil.copytree(goi, GOC, dirs_exist_ok=True)
    (GOC / "data").mkdir(exist_ok=True)
    # Tep dem cua phien TRUOC, neu co, nam o mot dataset rieng. Chep vao truoc khi
    # chay de buoc sinh noi tiep dung cho do.
    for d in sorted(VAO.glob("*")):
        for tep in d.glob("trich_*.jsonl"):
            dich = GOC / "data" / tep.name
            if not dich.exists():
                shutil.copy2(tep, dich)
                print(f"nap lai tep dem phien truoc: {tep.name} "
                      f"({sum(1 for _ in open(dich, encoding='utf-8'))} ban ghi)")
    return GOC


def kiem_the_he(goc: Path, cac_tap) -> None:
    ma = subprocess.call([sys.executable, str(goc / "tools" / "kiem-the-he.py"),
                          THE_HE, *cac_tap], cwd=goc)
    if ma != 0:
        raise SystemExit("du lieu khong phai the he " + THE_HE + " — dung")


def chay_mot_tap(goc: Path, tap: str, card: int, adapter: str):
    moi_truong = dict(os.environ, CUDA_VISIBLE_DEVICES=str(card),
                      PYTHONIOENCODING="utf-8", HF_HUB_ENABLE_HF_TRANSFER="1")
    log = open(LAM / f"log_{tap}_card{card}.txt", "w", encoding="utf-8")
    lenh = [sys.executable, "-m", "src.nhanh", "--nhanh", *NHANH,
            "--model", MO_HINH, "--tap", tap, "--max-token", MAX_TOKEN,
            "--adapter-trich", adapter]
    # SO_CA: chay thu vai ca de do nhip truoc khi chay dai. Khong dat thi chay het.
    so_ca = os.environ.get("SO_CA")
    if so_ca:
        lenh += ["--n", so_ca]
    print(f"[card {card}] {' '.join(lenh)}")
    return subprocess.Popen(lenh, cwd=goc, env=moi_truong, stdout=log,
                            stderr=subprocess.STDOUT), log


def thu_hoach(goc: Path) -> None:
    """Chep ket qua VA tep dem ra /kaggle/working du an ve."""
    for mau in ("ra_*.jsonl", "trich_*.jsonl"):
        for tep in (goc / "data").glob(mau):
            shutil.copy2(tep, LAM / tep.name)
            print(f"thu hoach {tep.name}: "
                  f"{sum(1 for _ in open(tep, encoding='utf-8'))} ban ghi")


def main() -> None:
    cac_tap = sys.argv[1:]
    if not cac_tap or len(cac_tap) > 2:
        raise SystemExit("dung: python kaggle_chay.py <tap1> [<tap2>]")
    goc = chuan_bi()
    kiem_the_he(goc, cac_tap)
    adapter = str(goc / "models" / "nen-qwen3-4b-trich" / "best_checkpoint")
    if not Path(adapter).is_dir():
        raise SystemExit(f"khong thay adapter trich o {adapter}")

    tien_trinh = []
    for card, tap in enumerate(cac_tap):
        tien_trinh.append((tap, *chay_mot_tap(goc, tap, card, adapter)))
        time.sleep(20)          # lech nhau de hai tien trinh khong cung tai model

    bat_dau = time.time()
    while any(p.poll() is None for _tap, p, _log in tien_trinh):
        time.sleep(300)
        gio = (time.time() - bat_dau) / 3600
        dem = {t: sum(1 for _ in open(goc / "data" / f"trich_{t}_3072_hl.jsonl",
                                      encoding="utf-8"))
               if (goc / "data" / f"trich_{t}_3072_hl.jsonl").exists() else 0
               for t, _p, _l in tien_trinh}
        print(f"[{gio:.2f} gio] da trich: {dem}", flush=True)
        thu_hoach(goc)          # thu hoach lien tuc: het gio phien van con tep dem

    for tap, p, log in tien_trinh:
        log.close()
        print(f"{tap}: ma thoat {p.returncode}")
    thu_hoach(goc)
    (LAM / "ghi_chu_may.json").write_text(json.dumps(
        {"may_chay": "kaggle-2xT4", "the_he": THE_HE, "cac_tap": cac_tap,
         "mo_hinh": MO_HINH, "nhanh": NHANH}, ensure_ascii=False, indent=2),
        encoding="utf-8")


if __name__ == "__main__":
    main()
