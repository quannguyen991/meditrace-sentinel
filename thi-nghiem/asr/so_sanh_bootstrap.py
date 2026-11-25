# -*- coding: utf-8 -*-
"""So sanh hai he thong ASR tren cung tap bang paired bootstrap theo cau.

Dau vao: hai tep *.chi-tiet.json (dau ra cua danh_gia_asr.py) cung tap, cung thu tu.
Dau ra: WER moi he thong, hieu WER (B - A) va khoang tin cay 95% theo bootstrap cap cau.

Chi doc du lieu da tinh, khong chay mo hinh. Khong chon nguong tren tap test.
"""
import argparse
import json
import random
from pathlib import Path

import jiwer


def doc_cau(duong_dan: Path, gioi_han=None):
    cac = [k for k in json.loads(duong_dan.read_text(encoding="utf-8")) if "ref" in k]
    if gioi_han:
        cac = cac[:gioi_han]
    out = []
    for k in cac:
        ref = k["ref"]
        hyp = k["hyp"] or "_"
        o = jiwer.process_words(ref, hyp)
        loi = o.substitutions + o.deletions + o.insertions
        n = o.hits + o.substitutions + o.deletions
        out.append((k["id"], loi, max(n, 1)))
    return out


def wer_tong(cac):
    return sum(l for _, l, _ in cac) / sum(n for _, _, n in cac)


def bootstrap(a, b, B=2000, hat=42):
    ids = [x[0] for x in a]
    bd = {x[0]: x for x in b}
    a = [x for x in a if x[0] in bd]
    b = [bd[x[0]] for x in a]
    rnd = random.Random(hat)
    n = len(a)
    hieu = []
    for _ in range(B):
        idx = [rnd.randrange(n) for _ in range(n)]
        la = sum(a[i][1] for i in idx) / sum(a[i][2] for i in idx)
        lb = sum(b[i][1] for i in idx) / sum(b[i][2] for i in idx)
        hieu.append(lb - la)
    hieu.sort()
    return {
        "so_cau": n,
        "wer_A": round(wer_tong(a), 4),
        "wer_B": round(wer_tong(b), 4),
        "hieu_B_minus_A": round(wer_tong(b) - wer_tong(a), 4),
        "khoang_tin_cay_95": [round(hieu[int(0.025 * B)], 4), round(hieu[int(0.975 * B)], 4)],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", type=Path, required=True, help="he thong goc (A)")
    ap.add_argument("--b", type=Path, required=True, help="he thong so sanh (B)")
    ap.add_argument("--gioi-han", type=int, default=None)
    ap.add_argument("--B", type=int, default=2000)
    a = ap.parse_args()
    ket = bootstrap(doc_cau(a.a, a.gioi_han), doc_cau(a.b, a.gioi_han), a.B)
    print(json.dumps(ket, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
