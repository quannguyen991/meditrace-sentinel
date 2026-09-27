# -*- coding: utf-8 -*-
"""Do do trung nguyen van giua dap an va hoi thoai (20/09/2026).

VI SAO CAN. Du an da biet mot con so: 99,1% menh de dap an trung nguyen van voi
chu trong hoi thoai. Nhung do la con so tu dat ra, khong co chuan de doi chieu.

Hien tuong nay co ten goi va cach do chuan trong khoa hoc tom tat van ban:
Extractive Fragment Coverage va Extractive Fragment Density (Grusky, Naaman,
Artzi — NAACL 2018, "Newsroom: A Dataset of 1.3 Million Summaries with Diverse
Extractive Strategies").

    F(A, S)   tap doan trich lon nhat: duyet tham lam qua S, moi vi tri lay doan
              dai nhat con xuat hien nguyen van trong A
    Coverage  = (1/|S|) * tong |f|        ty le tu trong S den tu cac doan sao chep
    Density   = (1/|S|) * tong |f|^2      do dam dac cua cac doan sao chep lien tuc

Doc so: Coverage gan 1 nghia la gan nhu moi tu trong dap an deu lay tu hoi thoai.
Density cao nghia la chung duoc sao theo tung KHOI DAI chu khong phai tung tu le —
day moi la dau hieu cua bai toan giai duoc bang sao chep.

Cong bo hai chi so nay bien "mot diem yeu tu phat hien" thanh "mot chi so da co
chuan, trich dan duoc".

    python tools/do-trung-nguyen-van.py --tap viet_phat_trien thach_thuc_doi_chu_the_phat_trien
"""
import argparse
import io
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import du_lieu, duong_dan  # noqa: E402


def tu(s: str):
    s = unicodedata.normalize("NFC", (s or "").lower())
    return re.sub(r"[^\w\s]", " ", s).split()


def doan_trich(A, S):
    """Thuat toan tham lam cua Grusky va cong su. A, S la danh sach tu.

    -> danh sach do dai cac doan trich. Doan do dai 0 (tu khong co trong A) khong
    duoc ghi, dung nhu trong bai goc: chung khong dong gop vao ca hai chi so.
    """
    F = []
    i = j = 0
    # chi muc nguoc: tu -> cac vi tri trong A, de khong phai quet lai A moi lan
    vi_tri = {}
    for k, t in enumerate(A):
        vi_tri.setdefault(t, []).append(k)
    while i < len(S):
        dai_nhat = 0
        for k in vi_tri.get(S[i], ()):
            n = 0
            while (i + n < len(S) and k + n < len(A) and S[i + n] == A[k + n]):
                n += 1
            dai_nhat = max(dai_nhat, n)
        if dai_nhat:
            F.append(dai_nhat)
            i += dai_nhat
        else:
            i += 1
        j += 1
    return F


def do_mot_ca(ca):
    A = tu(ca["input"])
    # "Ban tom tat" cua bai toan nay la toan bo noi dung cac menh de dap an.
    S = []
    for p in ca["dap_an"]:
        S += tu(p.get("noi_dung"))
    if not S:
        return None
    F = doan_trich(A, S)
    return (sum(F) / len(S), sum(x * x for x in F) / len(S), len(S))


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace", line_buffering=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", nargs="+", required=True)
    ap.add_argument("--thu-muc", default=None)
    ap.add_argument("--ra", default=None, help="tep JSON de ghi ket qua")
    a = ap.parse_args()
    d = Path(a.thu_muc) if a.thu_muc else duong_dan.THU_MUC_DU_LIEU

    ra = {}
    print("| Tập | Số ca | Coverage | Density | Số từ đáp án |")
    print("|---|---|---|---|---|")
    for tap in a.tap:
        cac = du_lieu.nap_mau(d / f"{tap}.jsonl")
        do = [x for x in (do_mot_ca(c) for c in cac) if x]
        if not do:
            print(f"| {tap} | 0 | — | — | — |")
            continue
        cov = sum(x[0] for x in do) / len(do)
        den = sum(x[1] for x in do) / len(do)
        n_tu = sum(x[2] for x in do)
        ra[tap] = {"so_ca": len(do), "coverage": cov, "density": den, "so_tu_dap_an": n_tu}
        print(f"| {tap} | {len(do)} | **{cov:.3f}** | **{den:.1f}** | {n_tu} |")

    if a.ra:
        Path(a.ra).write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\nGhi {a.ra}")


if __name__ == "__main__":
    main()
