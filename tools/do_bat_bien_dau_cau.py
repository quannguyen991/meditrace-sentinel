# -*- coding: utf-8 -*-
"""Do do BAT BIEN DAU CAU cua lop canh bao.

Chay `canh_bao.gop.chay` hai lan tren cung dau ra mo hinh: (a) hoi thoai goc, (b) hoi
thoai bo dau cau + viet thuong (nhu van chep tu am thanh); menh de va trich dan cua
mo hinh duoc chuan hoa theo CUNG cach. So tap canh bao (ma, phat bieu) va canh bao toan
ca (ma, luot). Luat tot thi gan nhu khong doi: dau cau khong mang thong tin lam sang.

    python -m tools.do_bat_bien_dau_cau [--thu-muc data/thach_thuc] [--nhanh C_khoa]
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

from src import du_lieu, nhieu_asr
from src.canh_bao import gop
from src.phat_bieu import PhatBieu


def bo_dau(van: str) -> str:
    return re.sub(r"\s{2,}", " ", nhieu_asr.bo_dau_cau(van or "")).strip().lower()


def bo_dau_hoi_thoai(hoi_thoai: str) -> str:
    """Giu nhan vai ("Bác sĩ: ") — do la thu bo sinh / may tach nguoi noi dat ra."""
    ra = []
    for d in hoi_thoai.split("\n"):
        vai, ngan, than = d.partition(": ")
        ra.append(f"{vai}{ngan}{bo_dau(than)}" if ngan else bo_dau(d))
    return "\n".join(ra)


def bo_dau_phat_bieu(d: dict) -> dict:
    d = dict(d)
    d["noi_dung"] = bo_dau(d.get("noi_dung"))
    if d.get("trich_dan"):
        d["trich_dan"] = [bo_dau(t) for t in d["trich_dan"]]
    return d


def _tap(kq) -> set:
    ra = {("pb", c.ma, pid) for pid, v in kq["theo_phat_bieu"].items() for c in v["tat_ca"]}
    ra |= {("ca", c.ma, tuple(c.luot)) for c in kq["toan_ca"]}
    return ra


def do(ca_list, ra_list) -> dict:
    """`ra_list`: cac ban ghi dau ra mo hinh ({"input", "phat_bieu"}); `ca_list` chi de
    cung giao dien voi cac bo do khac (khong dung). -> ty le canh bao goc con giu."""
    giu, tong, hop, mat, them = 0, 0, 0, Counter(), Counter()
    for r in ra_list:
        a = _tap(gop.chay([PhatBieu(**d) for d in r["phat_bieu"]], r["input"]))
        b = _tap(gop.chay([PhatBieu(**bo_dau_phat_bieu(d)) for d in r["phat_bieu"]], bo_dau_hoi_thoai(r["input"])))
        tong += len(a)
        giu += len(a & b)
        hop += len(a | b)
        mat.update(x[1] for x in a - b)
        them.update(x[1] for x in b - a)
    # ty_le_ma_giu_nguyen chi dem canh bao MAT; jaccard dem ca canh bao THEM (25/11: bo dau cau
    # lam sinh them 1.042 canh bao bo sot gia ma ty le giu van 0,973 — so mot chieu che mat).
    return {"ty_le_ma_giu_nguyen": round(giu / tong, 3) if tong else 1.0,
            "jaccard": round(giu / hop, 3) if hop else 1.0, "so_canh_bao_goc": tong,
            "ma_mat": mat, "ma_them": them}


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--thu-muc", default="data/thach_thuc")
    ap.add_argument("--nhanh", default="C_khoa")
    ap.add_argument("--ra-json", default=None)
    a = ap.parse_args(argv)
    from src.do_canh_bao import cac_tap
    T = Path(a.thu_muc)
    ra_list = [r for tap in cac_tap(T, a.nhanh) for r in du_lieu.nap_mau(T / f"ra_{a.nhanh}_{tap}.jsonl")]
    kq = do([], ra_list)
    kq = {**kq, "ma_mat": dict(kq["ma_mat"].most_common()), "ma_them": dict(kq["ma_them"].most_common()),
          "thu_muc": str(T), "so_ca": len(ra_list)}
    print(json.dumps(kq, ensure_ascii=False, indent=1))
    if a.ra_json:
        Path(a.ra_json).write_text(json.dumps(kq, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
