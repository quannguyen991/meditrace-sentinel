# -*- coding: utf-8 -*-
"""Bo sot tach theo: luot dan cua menh de dap an CO / KHONG trung nguyen van mot cau
trong tap huan luyen cua mo hinh. Tra loi cau hoi cua giam khao ve trung lap ngu nghia:
neu mo hinh chi "nho cau", bo sot o nhom khong trung se cao hon han.

Chay: python tools/do_bo_sot_theo_trung_lap.py --dap-an data/viet_phat_trien.jsonl \
        "v1=<trich v1>:data/viet_train.jsonl" "v3=<trich v3>:data/viet_train_v2.jsonl"
"""
from __future__ import annotations

import argparse
import copy
import sys

from src.do_luong.do_bo_sot import ti_le_bo_sot
from src.do_luong.do_lap_cau import doc_jsonl, tach_cau
from tools.do_bo_sot_tren_tap import doc_jsonl_theo_id, khoang_tin_cay_95


def tap_cau(tep):
    ca, _ = doc_jsonl(tep)
    return {c for x in ca for c in tach_cau(x.get("input", ""))}


def gan_nhom(dap_an_ca, input_ca, cau_train):
    luot = tach_cau(input_ca)
    ra = []
    for d in dap_an_ca:
        d = copy.copy(d)
        so = [i for i in (d.get("luot") or d.get("luot_thoai") or d.get("bang_chung") or []) if isinstance(i, int)]
        cau = [luot[i - 1] for i in so if 1 <= i <= len(luot)]
        d["nhom_loi"] = "trung" if cau and all(c in cau_train for c in cau) else "khong_trung"
        ra.append(d)
    return ra


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--dap-an", required=True)
    ap.add_argument("cap", nargs="+", help="ten=tep_trich:tep_train")
    a = ap.parse_args()
    dap = doc_jsonl_theo_id(a.dap_an)
    print("| Mô hình | Nhóm lượt dẫn | Mệnh đề | Bỏ sót | Tỷ lệ | Khoảng 95% |")
    print("|---|---|---:|---:|---:|---|")
    for c in a.cap:
        ten, rest = c.split("=", 1)
        tep_trich, tep_train = rest.rsplit(":", 1)
        trich = doc_jsonl_theo_id(tep_trich)
        cau_train = tap_cau(tep_train)
        chung = sorted(set(dap) & set(trich))
        cap = [(gan_nhom(dap[i].get("dap_an") or [], dap[i].get("input", ""), cau_train),
                trich[i].get("phat_bieu") or []) for i in chung]
        r = ti_le_bo_sot(cap)
        for nhom in ("trung", "khong_trung"):
            n = r["theo_nhom"].get(nhom, {"so_menh_de": 0, "so_bo_sot": 0, "ti_le": 0.0})
            lo, hi = khoang_tin_cay_95(n["so_bo_sot"], n["so_menh_de"]) if n["so_menh_de"] else (0, 0)
            print(f"| {ten} | {nhom} | {n['so_menh_de']} | {n['so_bo_sot']} | "
                  f"{100 * n['ti_le']:.1f}% | {100 * lo:.1f}–{100 * hi:.1f}% |")


if __name__ == "__main__":
    main()
