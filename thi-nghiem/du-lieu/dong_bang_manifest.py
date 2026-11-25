# -*- coding: utf-8 -*-
"""Dong bang manifest: gan moi ca sinh boi sinh_bo(so_ca, seed) vao tap train/phat_trien/kiem_tra_cuoi
theo ten khuon (tach_tap_viet.phan_khuon), roi ghi ID, khuon, tap va ma bam SHA-256.

Muc dich: bo kiem tra cuoi duoc khoa TRUOC khi sinh bo huan luyen moi. Chay lai voi cung seed
phai cho ra cung ma bam; neu khac, bo sinh da thay doi va phai tao manifest moi, ghi ro ly do.

Chi ghi ID, ten khuon va ma bam. Khong ghi noi dung hoi thoai ra file manifest.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.stdout.reconfigure(encoding="utf-8")

from src import ngu_lieu_viet as nl, sinh_hoi_thoai_viet as sh, tach_tap_viet as tv  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--so-ca", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--ra", type=Path, required=True)
    a = ap.parse_args()

    names = [b["ten"] for b in nl.BENH]
    p = tv.phan_khuon(names)
    tap_cua = {}
    for t, ds in p.items():
        for k in ds:
            tap_cua[k] = t

    bo = sh.sinh_bo(a.so_ca, a.seed)
    dong = []
    for m in bo:
        dong.append({"id": m["id"], "khuon": m["benh"], "tap": tap_cua[m["benh"]]})

    chuoi = "\n".join(f'{d["id"]}|{d["khuon"]}|{d["tap"]}' for d in dong).encode("utf-8")
    ket = {
        "so_ca": len(dong),
        "seed": a.seed,
        "so_khuon": len(names),
        "khuon_theo_tap": {t: sorted(v) for t, v in p.items()},
        "so_ca_theo_tap": {t: sum(1 for d in dong if d["tap"] == t) for t in p},
        "ma_bam_danh_sach_ca": hashlib.sha256(chuoi).hexdigest(),
        "ghi_chu": "Bo kiem tra cuoi = tap kiem_tra_cuoi. Khoa truoc khi sinh bo huan luyen moi.",
    }
    a.ra.parent.mkdir(parents=True, exist_ok=True)
    a.ra.write_text(json.dumps(ket, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in ket.items() if k != "khuon_theo_tap"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
