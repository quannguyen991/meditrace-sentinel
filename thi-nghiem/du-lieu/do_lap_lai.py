# -*- coding: utf-8 -*-
"""Do muc lap lai cua bo hoi thoai mo phong (sinh boi src/sinh_hoi_thoai_viet.sinh_bo).

Muc dich: tra loi cau hoi 'bo 200 khuon / 5.000 ca co bi lap lai khong?' bang so do duoc.
Khong sua du lieu. Ket qua ghi ra JSON de dua vao tai lieu.

Chi so:
  - so hoi thoai trung nguyen van
  - ti le cap ca (cung khuon, khac khuon) co Jaccard n-gram >= nguong (mau ngau nhien, co hat giong)
  - ti le cau thoai (cau co nghia) xuat hien o nhieu ca
  - so cau thoai duy nhat / tong so cau
  - phan bo so ca moi khuon
"""
import argparse
import json
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.stdout.reconfigure(encoding="utf-8")

from src.bo_du_lieu import sinh_hoi_thoai_viet as sh  # noqa: E402


def ngram(s: str, n: int = 3):
    t = re.findall(r"\w+", s.lower())
    return set(tuple(t[i:i + n]) for i in range(max(0, len(t) - n + 1)))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def do(so_ca: int, seed: int, mau_cap: int, nguong: float):
    bo = sh.sinh_bo(so_ca, seed)
    rnd = random.Random(seed)
    ket = {"so_ca": len(bo), "seed": seed}

    cac = [m["input"] for m in bo]
    ket["hoi_thoai_trung_nguyen_van"] = len(cac) - len(set(cac))

    # cau thoai: tach theo dong xuong dong hoac dau cham; dem cau o nhieu ca
    dem_cau = Counter()
    tong_cau = 0
    for txt in cac:
        cau = set(c.strip() for c in re.split(r"[\n.?!]+", txt) if len(c.strip().split()) >= 4)
        tong_cau += len(cau)
        dem_cau.update(cau)
    ket["cau_thoai_duy_nhat"] = len(dem_cau)
    ket["cau_thoai_tong"] = tong_cau
    ket["ti_le_cau_xuat_hien_o_nhieu_hon_1_ca"] = round(sum(1 for c, n in dem_cau.items() if n > 1) / max(1, len(dem_cau)), 4)

    # phan bo ca theo khuon
    theo_khuon = Counter(m["benh"] for m in bo)  # khuon = ten benh (ca.benh["ten"])
    ket["so_khuon_co_ca"] = len(theo_khuon)
    ket["ca_moi_khuon_min_max"] = [min(theo_khuon.values()), max(theo_khuon.values())] if theo_khuon else None

    # Jaccard n-gram: cap cung khuon vs cap khac khuon (mau ngau nhien)
    nhom = defaultdict(list)
    for i, m in enumerate(bo):
        nhom[m["benh"]].append(i)
    cung, khac = [], []
    cac_ng = [ngram(t) for t in cac]
    chi_so_khuon = list(nhom.keys())
    for _ in range(mau_cap):
        k = rnd.choice(chi_so_khuon)
        if len(nhom[k]) >= 2:
            i, j = rnd.sample(nhom[k], 2)
            cung.append(jaccard(cac_ng[i], cac_ng[j]))
        i, j = rnd.randrange(len(bo)), rnd.randrange(len(bo))
        if i != j and bo[i]["benh"] != bo[j]["benh"]:
            khac.append(jaccard(cac_ng[i], cac_ng[j]))
    if cung:
        ket["jaccard_3gram_cung_khuon_tb"] = round(sum(cung) / len(cung), 4)
        ket[f"ti_le_cap_cung_khuon_>={nguong}"] = round(sum(1 for x in cung if x >= nguong) / len(cung), 4)
    if khac:
        ket["jaccard_3gram_khac_khuon_tb"] = round(sum(khac) / len(khac), 4)
        ket[f"ti_le_cap_khac_khuon_>={nguong}"] = round(sum(1 for x in khac if x >= nguong) / len(khac), 4)
    return ket


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--so-ca", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--mau-cap", type=int, default=4000)
    ap.add_argument("--nguong", type=float, default=0.5)
    ap.add_argument("--ra", type=Path, default=None)
    a = ap.parse_args()
    ket = do(a.so_ca, a.seed, a.mau_cap, a.nguong)
    txt = json.dumps(ket, ensure_ascii=False, indent=2)
    print(txt)
    if a.ra:
        a.ra.parent.mkdir(parents=True, exist_ok=True)
        a.ra.write_text(txt, encoding="utf-8")


if __name__ == "__main__":
    main()
