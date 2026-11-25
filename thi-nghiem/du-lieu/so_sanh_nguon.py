# -*- coding: utf-8 -*-
"""So sanh do da dang tu vung va do phu n-gram giua ba nguon:
  - mo phong: src/sinh_hoi_thoai_viet.sinh_bo (5.000 ca)
  - that (VietMed-train, loi noi that tu video y te): tep transcript ngoai kho
  - that (ViMedCSS-train, doan video y te): metadata CSV ngoai kho

Khong nap tep am thanh. Dau vao ngoai kho khong commit:
  --vietmed-dir  thu muc co train_transcript.txt
  --vimedcss-train  duong dan ViMedCSS-Metadata/train_set.csv
"""
import argparse
import ast
import json
import re
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.stdout.reconfigure(encoding="utf-8")


def token(s: str):
    return re.findall(r"\w+", s.lower())


def thong_ke(cau_list):
    tu = [w for c in cau_list for w in token(c)]
    n = len(tu)
    v = len(set(tu))
    return {
        "so_cau": len(cau_list),
        "so_tu": n,
        "tu_vung_duy_nhat": v,
        "ttr": round(v / max(1, n), 4),
        "cau_trung_nguyen_van": len(cau_list) - len(set(cau_list)),
        "do_dai_cau_tb": round(n / max(1, len(cau_list)), 2),
    }


def ngram(cau_list, k=3):
    s = set()
    for c in cau_list:
        t = token(c)
        s.update(tuple(t[i:i + k]) for i in range(max(0, len(t) - k + 1)))
    return s


def phu(tap_a, tap_b, k=3):
    """ty le n-gram cua A co trong B"""
    if not tap_a:
        return 0.0
    return round(len(tap_a & tap_b) / len(tap_a), 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vietmed-dir", type=Path, required=True)
    ap.add_argument("--vimedcss-train", type=Path, required=True)
    ap.add_argument("--so-ca", type=int, default=5000)
    ap.add_argument("--ra", type=Path, default=None)
    a = ap.parse_args()

    from src import sinh_hoi_thoai_viet as sh
    bo = sh.sinh_bo(a.so_ca, 42)
    mo_phong = []
    for m in bo:
        mo_phong.extend(c.strip() for c in re.split(r"[\n]+", m["input"]) if c.strip())

    vm = [d["text"] for d in ast.literal_eval((a.vietmed_dir / "train_transcript.txt").read_text(encoding="utf-8"))]
    vc = pd.read_csv(a.vimedcss_train)["segment_text"].astype(str).tolist()

    ng_mp, ng_vm, ng_vc = ngram(mo_phong), ngram(vm), ngram(vc)
    ket = {
        "mo_phong_5000": thong_ke(mo_phong),
        "that_vietmed_train": thong_ke(vm),
        "that_vimedcss_train": thong_ke(vc),
        "do_phu_3gram": {
            "that_vietmed_ma_mo_phong_bao_phu": phu(ng_vm, ng_mp),
            "that_vimedcss_ma_mo_phong_bao_phu": phu(ng_vc, ng_mp),
            "that_vietmed_ma_vimedcss_bao_phu": phu(ng_vm, ng_vc),
            "mo_phong_ma_that_vietmed_bao_phu": phu(ng_mp, ng_vm),
        },
        "ghi_chu": "bao_phu = ty le 3-gram cua nguon A xuat hien trong nguon B. Thap nghia la B khac biet nhieu voi A.",
    }
    txt = json.dumps(ket, ensure_ascii=False, indent=2)
    print(txt)
    if a.ra:
        a.ra.parent.mkdir(parents=True, exist_ok=True)
        a.ra.write_text(txt, encoding="utf-8")


if __name__ == "__main__":
    main()
