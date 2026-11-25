# -*- coding: utf-8 -*-
"""Do do lap cau va do da dang tu vung cua mot bo hoi thoai.

Bo 5.000 ca hien tai co ti le lap cau rat cao (ban ban giao 20/11/2026: 87.265 cau,
20.652 cau duy nhat, lap 76,3%) va tu vung ngheo (TTR 0,0020 so voi 0,0181-0,0253
cua du lieu that). Cong cu nay do lai cac con so do bang MOT dinh nghia co dinh, de
so bo v1 voi bo v2 cung mot thuoc.

Dinh nghia:
  - mot "cau" la mot LUOT noi sau khi bo phan ghi nguoi noi (`Bac si:`...), chuan hoa
    NFC, ha chu thuong, gop khoang trang;
  - ti_le_lap = 1 - so_cau_duy_nhat / so_cau;
  - TTR = so tu duy nhat / tong so tu tren toan bo bo;
  - MTLD (McCarthy & Jarvis 2010, nguong 0,72) it phu thuoc do dai van ban hon TTR;
  - distinct-2 = so cap tu lien tiep duy nhat / tong so cap (tinh trong tung cau).

Chay: python -m src.do_lap_cau data/hoi_thoai_viet_5000.jsonl
"""
from __future__ import annotations

import collections
import json
import re
import sys
import unicodedata
from typing import Iterable

from src import duong_dan

_TIEN_TO_NGUOI_NOI = re.compile(r"^\s*[^:\n]{1,30}:\s*")
_TU = re.compile(r"[^\W_]+", re.UNICODE)


def _chuan_hoa(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "").lower()
    return re.sub(r"\s+", " ", s).strip()


def tach_cau(input_hoi_thoai: str) -> list[str]:
    """Tach `input` cua mot ca (moi dong mot luot) thanh cac cau, bo phan ghi nguoi noi."""
    ra = []
    for dong in (input_hoi_thoai or "").split("\n"):
        dong = _TIEN_TO_NGUOI_NOI.sub("", dong, count=1)
        dong = _chuan_hoa(dong)
        if dong:
            ra.append(dong)
    return ra


def _tu(cau: str) -> list[str]:
    return _TU.findall(cau)


def _mtld_mot_chieu(tokens: list[str], nguong: float = 0.72) -> float:
    so_nhan_to, loai, tong = 0.0, set(), 0
    for t in tokens:
        tong += 1
        loai.add(t)
        if len(loai) / tong <= nguong:
            so_nhan_to += 1
            loai, tong = set(), 0
    if tong:
        ttr = len(loai) / tong
        so_nhan_to += (1 - ttr) / (1 - nguong)
    return len(tokens) / so_nhan_to if so_nhan_to else float(len(tokens))


def mtld(tokens: list[str], nguong: float = 0.72) -> float:
    """Trung binh MTLD xuoi va nguoc. Chuoi rong -> 0,0."""
    if not tokens:
        return 0.0
    return (_mtld_mot_chieu(tokens, nguong) + _mtld_mot_chieu(tokens[::-1], nguong)) / 2


def do_lap_cau(cac_ca: Iterable[dict], do_dai_tu_toi_thieu: int = 1) -> dict:
    """-> {"so_ca", "so_cau", "so_cau_duy_nhat", "ty_le_lap", "ttr", "mtld",
    "distinct2", "top_lap"}. Ca khong co khoa `input` bi bo qua.
    Neu `do_dai_tu_toi_thieu > 1`, chi tinh cac cau co it nhat tung do tu."""
    dem = collections.Counter()
    tu_tat_ca, loai_tu = [], set()
    cap_duy_nhat, tong_cap = set(), 0
    so_ca = 0
    for ca in cac_ca:
        if not isinstance(ca, dict) or "input" not in ca:
            continue
        so_ca += 1
        for cau in tach_cau(ca["input"]):
            tu = _tu(cau)
            if len(tu) < do_dai_tu_toi_thieu:
                continue
            dem[cau] += 1
            tu_tat_ca.extend(tu)
            loai_tu.update(tu)
            for i in range(len(tu) - 1):
                cap_duy_nhat.add((tu[i], tu[i + 1]))
                tong_cap += 1
    so_cau = sum(dem.values())
    duy_nhat = len(dem)
    return {
        "so_ca": so_ca,
        "so_cau": so_cau,
        "so_cau_duy_nhat": duy_nhat,
        "ty_le_lap": (1 - duy_nhat / so_cau) if so_cau else 0.0,
        "ttr": (len(loai_tu) / len(tu_tat_ca)) if tu_tat_ca else 0.0,
        "mtld": mtld(tu_tat_ca),
        "distinct2": (len(cap_duy_nhat) / tong_cap) if tong_cap else 0.0,
        "top_lap": [(c, n) for c, n in dem.most_common(20) if n > 1],
    }


def doc_jsonl(duong_dan_tep: str) -> tuple[list[dict], int]:
    """-> (cac_ca_hop_le, so_dong_bo). Dong trong hoac JSON hong duoc bo qua va dem."""
    ca, bo = [], 0
    with open(duong_dan_tep, encoding="utf-8") as f:
        for dong in f:
            if not dong.strip():
                bo += 1
                continue
            try:
                x = json.loads(dong)
            except json.JSONDecodeError:
                bo += 1
                continue
            if isinstance(x, dict):
                ca.append(x)
            else:
                bo += 1
    return ca, bo


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser(description="Do do lap lai cau va chi so ngon ngu.")
    ap.add_argument("tep", help="duong dan tep jsonl")
    ap.add_argument("--do-dai-tu", type=int, default=1, help="do dai tu toi thieu cua cau (vi du: 8)")
    a = ap.parse_args()

    ca, bo = doc_jsonl(a.tep)
    r = do_lap_cau(ca, do_dai_tu_toi_thieu=a.do_dai_tu)
    print(f"tep: {a.tep}  (bo {bo} dong trong/hong)" + (f" (cau >= {a.do_dai_tu} tu)" if a.do_dai_tu > 1 else ""))
    for k in ("so_ca", "so_cau", "so_cau_duy_nhat"):
        print(f"{k:18s} {r[k]:,}")
    print(f"{'ty_le_lap':18s} {100 * r['ty_le_lap']:.2f}%")
    print(f"{'ttr':18s} {r['ttr']:.4f}")
    print(f"{'mtld':18s} {r['mtld']:.1f}")
    print(f"{'distinct2':18s} {r['distinct2']:.4f}")
    print("20 cau lap nhieu nhat:")
    for c, n in r["top_lap"]:
        print(f"  {n:6d}  {c[:90]}")


if __name__ == "__main__":
    main()
