# -*- coding: utf-8 -*-
# DOI CHUNG MO HINH NEN — KHONG adapter (19/09/2026).
#
# MUC DICH. Tra loi cau hoi manh nhat chong lai du an: "mo hinh to hon la het loi
# chu gi, dau can co che cua em". Bake-off 06/09 co cham vao cau nay nhung chi 8 hoi
# thoai, tren bo VAIC da bo, va cham bang mat. Lan nay: 300 ca, 4 bo thach thuc the
# he 8, cham bang src/cham_he_thong.py — dung bo cham nhu cac nhanh khac.
#
# CACH GIU CHO CONG BANG. Moi khau giong het kernel-th8-a/b:
#   cung 4 bo thach thuc, cung luoc do JSON, cung ep JSON bang lm-format-enforcer,
#   cung 5 vi du mau trong loi nhac, cung max_token 3072, cung giai ma tham lam.
# CHI KHAC MOT CHO: khong nap adapter da huan luyen, va doi co mo hinh.
#
# CANH BAO KHI DOC KET QUA. Ten tep ket qua `ra_<nhanh>_<tap>.jsonl` KHONG kem ten
# mo hinh. Tai ve phai de rieng thu muc, neu khong se de len ket qua cua mo hinh da
# huan luyen ma khong ai biet. Xem docs/ket-qua/doi-chung-luat-4-bo-th8.md.
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
MO_HINH = "Qwen/Qwen3-8B"
NHANH = ["B", "C", "C_khoa", "C_khoa_hoi"]
MAX_TOKEN = "3072"
CAC_TAP = ["thach_thuc_phuong_ngu_phat_trien", "thach_thuc_nhieu_asr_phat_trien"]
SO_CA = ""      # chay het 80 ca moi bo


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


def main() -> None:
    subprocess.run(["nvidia-smi", "--query-gpu=index,name,memory.total",
                    "--format=csv,noheader"], check=False)
    # Phien ban giong venv HoaiDuc (D:/meditrace-venv, kiem 17/09/2026).
    subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                    "transformers==4.57.6", "peft==0.20.0", "bitsandbytes==0.50.2",
                    "accelerate==1.14.0", "lm-format-enforcer==0.11.3"], check=True)
    thu = subprocess.run([sys.executable, "-c",
                          "from lmformatenforcer import JsonSchemaParser;"
                          "from lmformatenforcer.integrations.transformers import "
                          "build_transformers_prefix_allowed_tokens_fn;"
                          "import transformers;"
                          "print('ep JSON san sang, transformers', transformers.__version__)"])
    if thu.returncode != 0:
        sys.exit("khong nap duoc lm-format-enforcer - dung, khong chay tu do")
    goc = chuan_bi()

    ma = subprocess.call([sys.executable, str(goc / "tools" / "kiem-the-he.py"),
                          THE_HE, *CAC_TAP], cwd=goc)
    if ma != 0:
        sys.exit("du lieu tren may khong phai the he " + THE_HE)

    def khoi_dong(card, tap):
        lenh = [sys.executable, "-m", "src.nhanh", "--nhanh", *NHANH,
                "--model", MO_HINH, "--tap", tap, "--max-token", MAX_TOKEN]
        if SO_CA:
            lenh += ["--n", SO_CA]
        log = open(LAM / f"log_{tap}.txt", "a", encoding="utf-8")
        moi_truong = dict(os.environ, CUDA_VISIBLE_DEVICES=str(card),
                          PYTHONIOENCODING="utf-8")
        print(f"[card {card}] {' '.join(lenh)}", flush=True)
        return subprocess.Popen(lenh, cwd=goc, env=moi_truong, stdout=log,
                                stderr=subprocess.STDOUT), log

    def dem_ca(tap):
        d = goc / "data" / f"trich_{tap}_3072.jsonl"
        return sum(1 for _ in open(d, encoding="utf-8")) if d.exists() else 0

    CANH_TREO = 40 * 60
    tien_trinh = []
    theo_doi = {}
    for card, tap in enumerate(CAC_TAP):
        p, log = khoi_dong(card, tap)
        tien_trinh.append([tap, p, log])
        theo_doi[tap] = {"card": card, "dem": dem_ca(tap), "luc": time.time(), "lan": 0}
        time.sleep(20)

    bat_dau = time.time()
    while any(p.poll() is None for _t, p, _l in tien_trinh):
        time.sleep(120)
        dem = {}
        for muc in tien_trinh:
            t, p, log = muc
            n = dem_ca(t)
            dem[t] = n
            td = theo_doi[t]
            if n != td["dem"]:
                td["dem"], td["luc"] = n, time.time()
            elif p.poll() is None and time.time() - td["luc"] > CANH_TREO and td["lan"] < 4:
                td["lan"] += 1
                print(f"!!! {t}: {CANH_TREO // 60} phut khong them ca (dung o {n}) - "
                      f"giet va chay lai, lan {td['lan']}", flush=True)
                p.kill()
                p.wait()
                log.close()
                muc[1], muc[2] = khoi_dong(td["card"], t)
                td["luc"] = time.time()
        print(f"[{(time.time() - bat_dau) / 60:.1f} phut] da trich: {dem}", flush=True)
        thu_hoach(goc)

    for tap, p, log in tien_trinh:
        log.close()
        print(f"{tap}: ma thoat {p.returncode}", flush=True)
        duoi = (LAM / f"log_{tap}.txt").read_text(encoding="utf-8",
                                                  errors="replace")[-1500:]
        print(f"--- duoi log {tap}:\n{duoi}", flush=True)
        toan_log = (LAM / f"log_{tap}.txt").read_text(encoding="utf-8", errors="replace")
        if "khong ep duoc JSON" in toan_log:
            print(f"!!! {tap}: VAN CHAY TU DO - ket qua nay KHONG dung duoc", flush=True)
    thu_hoach(goc)
    (LAM / "ghi_chu_may.json").write_text(json.dumps(
        {"may_chay": "kaggle-2xT4", "ep_json": "lm-format-enforcer 0.11.3",
         "the_he": THE_HE, "cac_tap": CAC_TAP,
         "mo_hinh": MO_HINH, "adapter": None, "vai_tro": "doi chung mo hinh nen", "nhanh": NHANH, "so_ca": SO_CA or "het"},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print("ket qua o /kaggle/working:", sorted(os.listdir(LAM)), flush=True)


if __name__ == "__main__":
    main()
