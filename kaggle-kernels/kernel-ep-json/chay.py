# CHAY LAI hai bo thach thuc the he 7 CO EP JSON (17/09/2026).
#
# Lan chay 16/09 (kernel meditrace-chay-dai-t4) thieu lm-format-enforcer nen bakeoff._ep_json
# lui ve chay tu do, trong khi ba bo con lai tren HoaiDuc chay co ep. Hai dieu kien khac
# nhau thi khong so thang duoc. Ban nay:
#   - ghim DUNG phien ban thu vien cua venv HoaiDuc;
#   - thu nap lm-format-enforcer TRUOC khi dung GPU, khong nap duoc thi dung han;
#   - KHONG nap tep dem trich cu (tep dem do la dau ra khong ep) va khong gan kernel cu;
#   - quet log, thay "khong ep duoc JSON" la bao hong.
#
# Chay tren Kaggle: hai bo thach thuc, moi bo ghim mot card T4, chay song song.
#
# TOAN BO dieu khien nam TRONG NOTEBOOK nay, khong nam trong dataset. Ly do: dataset
# nang 164 MB, moi lan sua mot dong ma dieu khien ma phai tai lai ca goi thi khong
# lam viec duoc. Dataset chi giu thu khong doi: ma nguon, du lieu, adapter.
#
# TEP DEM la thu duy nhat cho phep phien sau chay tiep phien truoc (phien Kaggle toi
# da 12 gio). Cu 5 phut chep tep dem ra /kaggle/working mot lan, nen het gio dot ngot
# cung khong mat phan da lam.
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
    # KHONG nap tep dem nao: moi tep dem the he 7 tren Kaggle deu la dau ra khong ep.
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

    adapter = str(goc / "models" / "nen-qwen3-4b-trich" / "best_checkpoint")
    if not Path(adapter).is_dir():
        sys.exit("khong thay adapter trich o " + adapter)

    tien_trinh = []
    for card, tap in enumerate(CAC_TAP):
        lenh = [sys.executable, "-m", "src.nhanh", "--nhanh", *NHANH,
                "--model", MO_HINH, "--tap", tap, "--max-token", MAX_TOKEN,
                "--adapter-trich", adapter]
        if SO_CA:
            lenh += ["--n", SO_CA]
        log = open(LAM / f"log_{tap}.txt", "w", encoding="utf-8")
        moi_truong = dict(os.environ, CUDA_VISIBLE_DEVICES=str(card),
                          PYTHONIOENCODING="utf-8")
        print(f"[card {card}] {' '.join(lenh)}", flush=True)
        tien_trinh.append((tap, subprocess.Popen(lenh, cwd=goc, env=moi_truong,
                                                 stdout=log,
                                                 stderr=subprocess.STDOUT), log))
        time.sleep(20)

    bat_dau = time.time()
    while any(p.poll() is None for _t, p, _l in tien_trinh):
        time.sleep(120)
        dem = {}
        for t, _p, _l in tien_trinh:
            d = goc / "data" / f"trich_{t}_3072_hl.jsonl"
            dem[t] = sum(1 for _ in open(d, encoding="utf-8")) if d.exists() else 0
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
        {"may_chay": "kaggle-2xT4", "ep_json": "lm-format-enforcer 0.11.3", "the_he": THE_HE, "cac_tap": CAC_TAP,
         "mo_hinh": MO_HINH, "nhanh": NHANH, "so_ca": SO_CA or "het"},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print("ket qua o /kaggle/working:", sorted(os.listdir(LAM)), flush=True)


if __name__ == "__main__":
    main()
