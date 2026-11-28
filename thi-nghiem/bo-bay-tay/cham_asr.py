# -*- coding: utf-8 -*-
"""So bản chép âm (ra/loi_thoai_asr.jsonl) với lời thoại gốc: từ then chốt còn hay mất.

Phủ định, trái/phải, tên thuốc: đếm từ. Số: so GIÁ TRỊ bằng src.canh_bao.so_lieu.tach
(hiểu cả "một trăm bảy mươi"), nên "170" chép thành chữ không bị tính là mất.

    D:/khkt-venv-lap/Scripts/python -X utf8 thi-nghiem/bo-bay-tay/cham_asr.py
"""
import json
import sys
from collections import Counter
from pathlib import Path

DAY = Path(__file__).resolve().parent
sys.path.insert(0, str(DAY.parents[1]))
sys.path.insert(0, str(DAY))
from nghe import BEN, PHU_DINH, THUOC, tu  # noqa: E402
from src.canh_bao import so_lieu  # noqa: E402


def gia_tri(s):
    return Counter(round(x.gia_tri, 3) for x in so_lieu.tach(s))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    goc = {c["id"]: c for c in map(json.loads, open(DAY / "ra" / "ca_bay.jsonl", encoding="utf-8"))}
    tong, mat = {}, []
    for r in map(json.loads, open(DAY / "ra" / "loi_thoai_asr.jsonl", encoding="utf-8")):
        ca = goc[r["id"]]
        vung = ca["phuong_ngu"]
        for i, (a, b) in enumerate(zip(ca["input"].split("\n"), r["input"].split("\n")), 1):
            a, b = a.split(":", 1)[1], b.split(":", 1)[1]
            ta, tb = tu(a), tu(b)
            nhom = {"phu_dinh": PHU_DINH, "ben": BEN, "thuoc": THUOC}
            for g, bo in nhom.items():
                for t in {x for x in ta if x in bo}:
                    n, k = ta.count(t), min(ta.count(t), tb.count(t))
                    c = tong.setdefault(vung, {}).setdefault(g, [0, 0])
                    c[0] += n; c[1] += k
                    if k < n:
                        mat.append((r["id"], vung, i, g, t, b.strip()))
            va, vb = gia_tri(a), gia_tri(b)
            n, k = sum(va.values()), sum((va & vb).values())
            c = tong.setdefault(vung, {}).setdefault("so", [0, 0])
            c[0] += n; c[1] += k
            for v in (va - vb):
                mat.append((r["id"], vung, i, "so", str(v), b.strip()))
    print("Từ then chốt còn giữ sau chép âm (PhoWhisper, giả định tách người nói hoàn hảo):")
    for v, d in tong.items():
        print(f"  {v:<10} " + "  ".join(f"{g} {k}/{n}" for g, (n, k) in sorted(d.items())))
    print("\nMất:")
    for x in mat:
        print(f"  {x[0]} [{x[1]}] lượt {x[2]} {x[3]} '{x[4]}': {x[5]}")
    (DAY / "ra" / "asr_tu_then_chot.json").write_text(json.dumps(
        {"giu_lai": {v: {g: {"goc": n, "con": k} for g, (n, k) in d.items()} for v, d in tong.items()},
         "mat": [dict(zip(("ca", "vung", "luot", "nhom", "tu", "ban_chep"), x)) for x in mat]},
        ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
