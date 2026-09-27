"""Thuoc do cho benchmark ASR: WER va ty le sai tu khoa lam sang.

Ca ban chep chuan va ban nhan dang deu qua cung mot buoc chuan hoa truoc khi do:
chu thuong, bo dau cau, "mi li gam" -> "mg", so doc bang chu -> chu so. Buoc nay chi
dung de DO; no khong bao gio sua ban chep dua vao MediTrace.
"""
from __future__ import annotations

from typing import Any

from . import critical_tokens as ct

LOAI = ("thuoc", "lieu", "tan_suat", "thoi_gian", "phu_dinh", "trang_thai", "nguoi")


def chuan_hoa_do(text: str) -> list[str]:
    w = ct.chuan_hoa(text).split()
    ra, i = [], 0
    while i < len(w):
        s = ct._doc_so(w, i)
        if s and s[1] > i:
            ra.append(str(s[0]))
            i = s[1]
        else:
            ra.append(w[i])
            i += 1
    return ra


def khoang_cach_tu(a: list[str], b: list[str]) -> int:
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[len(b)]


def wer(refs: list[str], hyps: list[str]) -> float:
    loi = tong = 0
    for r, h in zip(refs, hyps):
        rr = chuan_hoa_do(r)
        loi += khoang_cach_tu(rr, chuan_hoa_do(h))
        tong += len(rr)
    return loi / max(tong, 1)


def sai_tu_khoa(ref: str, hyp: str) -> dict[str, Any]:
    """-> {loai: 'dung'|'sai'|'them'|None}. None = ca hai deu khong co loai do."""
    a, b = ct.trich(ref), ct.trich(hyp)
    ra = {}
    for k in LOAI:
        if not a[k] and not b[k]:
            ra[k] = None
        elif not a[k]:
            ra[k] = "them"
        else:
            ra[k] = "dung" if a[k] == b[k] else "sai"
    return ra


def tong_hop(muc: list[dict], hyps: dict[str, str]) -> dict[str, Any]:
    """muc: [{id, van_ban, cap?}], hyps: {id: chu nhan dang}."""
    refs = [m["van_ban"] for m in muc]
    hs = [hyps.get(m["id"], "") for m in muc]
    theo_loai = {k: {"co": 0, "sai": 0, "them": 0} for k in LOAI}
    cau_sai = 0
    chi_tiet = {}
    for m, h in zip(muc, hs):
        s = sai_tu_khoa(m["van_ban"], h)
        chi_tiet[m["id"]] = s
        if any(v in ("sai", "them") for v in s.values()):
            cau_sai += 1
        for k, v in s.items():
            if v in ("dung", "sai"):
                theo_loai[k]["co"] += 1
            if v in ("sai", "them"):
                theo_loai[k][v] += 1
    cap: dict[str, list[str]] = {}
    for m in muc:
        if m.get("cap"):
            cap.setdefault(m["cap"], []).append(m["id"])
    # Mot cap dat khi LOAI THONG TIN PHAN BIET hai cau (vd lieu 5 mg / 50 mg) dung o ca hai
    # cau. Loi o loai khac (vd ten thuoc) khong lam truot cap; no da duoc dem o theo_loai.
    van = {m["id"]: m["van_ban"] for m in muc}
    cap_dat = []
    for c, ids in cap.items():
        phan_biet = ct.khac_nhau(ct.trich(van[ids[0]]), ct.trich(van[ids[1]]))
        if all(chi_tiet[i][k] in ("dung", None) for i in ids for k in phan_biet):
            cap_dat.append(c)
    return {
        "so_cau": len(muc),
        "wer": wer(refs, hs),
        "ty_le_cau_sai_tu_khoa": cau_sai / max(len(muc), 1),
        "theo_loai": {k: {**v, "ty_le_sai": (v["sai"] / v["co"]) if v["co"] else None}
                      for k, v in theo_loai.items()},
        "cap_toi_thieu": {"tong": len(cap), "phan_biet_dung": len(cap_dat),
                          "truot": sorted(set(cap) - set(cap_dat))},
        "chi_tiet": chi_tiet,
    }
