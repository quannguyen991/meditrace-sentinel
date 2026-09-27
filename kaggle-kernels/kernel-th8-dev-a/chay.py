# -*- coding: utf-8 -*-
# CHAY TAP PHAT TRIEN THE HE 8 tren Kaggle 2xT4 (19/09/2026).
#
# Tap phat trien co 634 ca. Chay het mat khoang 37 gio mot card, khong vua mot phien
# Kaggle. Nen rut MOT MAU 240 ca (hat 2026), chia 4 phan bang nhau, moi phan mot card:
# kernel nay chay hai phan, kernel kia chay hai phan con lai.
#
# Viec chia lam NGAY TREN MAY KAGGLE tu tep viet_phat_trien.jsonl co san trong
# dataset, nen khong phai tai lai goi 164 MB. Truoc khi chia, van kiem van tay cua
# tep goc de chac la the he 8.
#
# Moi phan la mot "tap" rieng, nen tep dem va tep ket qua cua bon card khong dam nhau.
# Ghep lai khi cham: xem tools/gop-phan-tap.py.
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
NHANH = ["B", "C", "C_khoa", "C_khoa_hoi"]
MAX_TOKEN = "3072"
TAP_GOC = "viet_phat_trien"
SO_MAU = 240
SO_PHAN = 4
HAT = 2026
CAC_TAP = ["viet_phat_trien_p1", "viet_phat_trien_p2"]
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


def chia_tap(goc: Path) -> None:
    """Rut mau SO_MAU ca tu TAP_GOC, chia SO_PHAN phan, moi phan mot tep + van tay.

    Rut xong SAP THEO id roi moi chia, nen phan nao chua ca nao la co dinh: chay lai
    kernel cho ra dung cac phan cu, va tep dem cua phien truoc con dung.
    """
    import random
    sys.path.insert(0, str(goc))
    from src import van_tay_bo

    nguon = goc / "data" / f"{TAP_GOC}.jsonl"
    ban = [json.loads(x) for x in open(nguon, encoding="utf-8") if x.strip()]
    ban.sort(key=lambda r: r["id"])
    if len(ban) < SO_MAU:
        sys.exit(f"{TAP_GOC} chi co {len(ban)} ca, khong rut duoc {SO_MAU}")
    mau = random.Random(HAT).sample(ban, SO_MAU)
    mau.sort(key=lambda r: r["id"])
    moi = SO_MAU // SO_PHAN
    for k in range(SO_PHAN):
        phan = mau[k * moi:(k + 1) * moi]
        dp = goc / "data" / f"{TAP_GOC}_p{k + 1}.jsonl"
        dp.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in phan) + "\n",
                      encoding="utf-8")
        van_tay_bo.ghi(dp, phan, THE_HE, hat=HAT,
                       ghi_chu=f"phan {k + 1}/{SO_PHAN} cua mau {SO_MAU} ca {TAP_GOC}")
        shutil.copy2(dp, LAM / dp.name)
        shutil.copy2(van_tay_bo.duong_dan_van_tay(dp),
                     LAM / van_tay_bo.duong_dan_van_tay(dp).name)
        print(f"  {dp.name}: {len(phan)} ca", flush=True)


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
                          THE_HE, TAP_GOC], cwd=goc)
    if ma != 0:
        sys.exit("du lieu tren may khong phai the he " + THE_HE)
    chia_tap(goc)

    adapter = str(goc / "models" / "nen-qwen3-4b-trich" / "best_checkpoint")
    if not Path(adapter).is_dir():
        sys.exit("khong thay adapter trich o " + adapter)

    def khoi_dong(card, tap):
        lenh = [sys.executable, "-m", "src.nhanh", "--nhanh", *NHANH,
                "--model", MO_HINH, "--tap", tap, "--max-token", MAX_TOKEN,
                "--adapter-trich", adapter]
        if SO_CA:
            lenh += ["--n", SO_CA]
        log = open(LAM / f"log_{tap}.txt", "a", encoding="utf-8")
        moi_truong = dict(os.environ, CUDA_VISIBLE_DEVICES=str(card),
                          PYTHONIOENCODING="utf-8")
        print(f"[card {card}] {' '.join(lenh)}", flush=True)
        return subprocess.Popen(lenh, cwd=goc, env=moi_truong, stdout=log,
                                stderr=subprocess.STDOUT), log

    def dem_ca(tap):
        d = goc / "data" / f"trich_{tap}_3072_hl.jsonl"
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
         "mo_hinh": MO_HINH, "nhanh": NHANH, "so_ca": SO_CA or "het"},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print("ket qua o /kaggle/working:", sorted(os.listdir(LAM)), flush=True)


if __name__ == "__main__":
    main()
