# -*- coding: utf-8 -*-
"""Chay mot lenh huan luyen voi tran VRAM cua tien trinh.

Ban goc tren HoaiDuc (C:\\Users\\hapur\\meditrace-train\\run_capped.py) dat cung
`set_per_process_memory_fraction(0.85)` va cung dong lenh. 0,85 x 12 GB = 10,2 GiB
cho RIENG tien trinh nay, trong khi bge-m3 va hien thi da chiem ~1,9 GiB: tong vuot
gioi han 90% (10,8 GiB) cua du an. Ban nay doc tran tu `--phan-vram` (mac dinh 0.74
= 8,9/12, tuc 10,8 tru 1,9) va chuyen moi doi so con lai cho `src.huan_luyen.huan_luyen_sft`.

Dung:
  python tools/run_capped.py --phan-vram 0.74 -- --model Qwen/Qwen3-4B \\
      --nhiem-vu trich --do-dai 4096 --hau-to=-v2 --loss-theo-doan
"""
import argparse
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def tach_doi_so(argv: list[str]) -> tuple[float, str, list[str]]:
    """-> (phan_vram, mo_dun, doi_so_cho_mo_dun). Doi so sau `--` di nguyen.

    `--mo-dun` mac dinh `src.huan_luyen.huan_luyen_sft`; dung `src.duong_ong.chay_duong_ong` de chay khau trich co tran VRAM
    (21/11/2026: khong co tran thi suy luan 3.072 token da vuot 11,4 GiB, qua gioi han 90%).
    """
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--phan-vram", type=float, default=0.74)
    ap.add_argument("--mo-dun", default="src.huan_luyen.huan_luyen_sft")
    if "--" in argv:
        i = argv.index("--")
        truoc, sau = argv[:i], argv[i + 1:]
    else:
        truoc, sau = argv, []
    a, thua = ap.parse_known_args(truoc)
    if thua:
        raise SystemExit(f"doi so la truoc '--': {thua}")
    if not 0.0 < a.phan_vram <= 1.0:
        raise SystemExit("--phan-vram phai trong (0, 1]")
    return a.phan_vram, a.mo_dun, sau


def main():
    phan, mo_dun, doi_so = tach_doi_so(sys.argv[1:])
    import torch
    torch.cuda.set_per_process_memory_fraction(phan, 0)
    print(f"[run_capped] tran VRAM tien trinh = {phan:.2f} cua GPU 0", flush=True)
    sys.argv = [mo_dun] + doi_so
    runpy.run_module(mo_dun, run_name="__main__", alter_sys=True)


if __name__ == "__main__":
    main()
