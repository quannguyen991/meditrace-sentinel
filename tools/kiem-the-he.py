# -*- coding: utf-8 -*-
"""Dung chuoi GPU neu du lieu tren may KHONG phai the he mong doi.

    python tools/kiem-the-he.py <the_he> <tap> [<tap> ...]

VI SAO CO TEP NAY (15/09/2026). Tu the he 7 tro di, bo moi va bo cu TRUNG id va
trung so ca o ca bon bo thach thuc (80/80/60/80). `don-dem-trich.py` doi chieu
bang id nen khong phan biet duoc — chinh no da ghi ro gioi han do. Neu quen dong bo
du lieu len may, chuoi se huan luyen 1,5 ngay GPU tren the he cu ma khong co gi bao.
Phep kiem o day doc van tay (`van_tay_bo`): dung the he VA bam noi dung khop ban ghi.
"""
import json
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

from src import van_tay_bo  # noqa: E402


def main() -> int:
    if len(sys.argv) < 3:
        raise SystemExit("Dung: python tools/kiem-the-he.py <the_he> <tap> [<tap> ...]")
    mong, cac_tap = sys.argv[1], sys.argv[2:]
    hong = 0
    for tap in cac_tap:
        dp = GOC / "data" / f"{tap}.jsonl"
        if not dp.exists():
            print(f"  {tap}: KHONG CO tep bo du lieu")
            hong += 1
            continue
        ban_ghi = [json.loads(x) for x in open(dp, encoding="utf-8") if x.strip()]
        vt = van_tay_bo.doc(dp)
        if not vt:
            print(f"  {tap}: KHONG CO van tay")
            hong += 1
            continue
        khop, loi = van_tay_bo.khop(dp, ban_ghi)
        if str(vt["the_he"]) != mong or not khop:
            print(f"  {tap}: the he {vt['the_he']} (mong {mong}), khop={khop}")
            hong += 1
            continue
        print(f"  {tap}: the he {mong}, {len(ban_ghi)} ca, khop van tay")
    return 1 if hong else 0


if __name__ == "__main__":
    sys.exit(main())
