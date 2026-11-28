# -*- coding: utf-8 -*-
"""Do PhoWhisper-small goc hoac goc+LoRA (greedy, cung cach giai ma danh_gia_asr.py)."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, r"C:\Users\hapur\meditrace-train\vnmed\pylib")
import torch
from danh_gia_asr import danh_gia, tap_vimedcss, tap_vietmed, nap_mo_hinh

ap = argparse.ArgumentParser()
ap.add_argument("--adapter", type=Path, default=None)
ap.add_argument("--eval-dir", type=Path, required=True)
ap.add_argument("--ra", type=Path, required=True)
ap.add_argument("--vietmed-gioi-han", type=int, default=500)
a = ap.parse_args()
torch.cuda.set_per_process_memory_fraction(0.70)
proc, m = nap_mo_hinh("cuda", "vinai/PhoWhisper-small", None)
if a.adapter:
    from peft import PeftModel
    m = PeftModel.from_pretrained(m, str(a.adapter)).merge_and_unload().half().eval()
a.ra.mkdir(parents=True, exist_ok=True)
kq = {"adapter": str(a.adapter), "ket_qua": []}
for ten, nguon, gh in [("ViMedCSS-test-shard0", tap_vimedcss(a.eval_dir / "test-00000.parquet"), None),
                       ("VietMed-test-500", tap_vietmed(a.eval_dir), a.vietmed_gioi_han)]:
    tong, ct = danh_gia(ten, nguon, proc, m, "cuda", gh, 1)
    kq["ket_qua"].append(tong)
    (a.ra / f"{ten}.chi-tiet.json").write_text(json.dumps(ct, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(tong, ensure_ascii=False), flush=True)
(a.ra / "tong-hop.json").write_text(json.dumps(kq, ensure_ascii=False, indent=1), encoding="utf-8")
