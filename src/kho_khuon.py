# -*- coding: utf-8 -*-
"""KHO KHUON dung chung: bo sinh, buoc chia tap va loc gioi tinh phai nhin CUNG MOT danh sach.

VI SAO CAN (23/11/2026). Truoc do `mo_rong=True` co ba cho dung ba danh sach khac nhau:
  - `sinh_ca` chon khuon tu `nl.BENH` (270 khuon);
  - `bang_tap_khuon` dung `BENH_GOC` + `khuon_mo_rong.BENH_MO_RONG` (600 khuon);
  - `tach_tap_viet.phan_khuon` danh chi so theo `nl.BENH`.
Khuon ngoai `nl.BENH` khong co chi so nen roi vao nhom cua khuon 101-200 va lam 12 khuon
cu doi tap (ro ri), con khuon trong `nl.BENH` ma khong co trong `BENH_MO_RONG` thi tra cuu
bang tap that bai. Kho nay la nguon duy nhat.

THU TU (quan trong, vi `phan_khuon` chia dot theo CHI SO):
  1. 200 khuon goc (`nl.BENH_GOC`), khong doi;
  2. 70 khuon moi cua `nl.BENH` (chi so 200-269), da duoc bo sinh dung;
  3. cac khuon cua `khuon_mo_rong.BENH_MO_RONG` chua co o buoc 1, 2 (giu thu tu do).
Khuon co o ca `nl.BENH` va `BENH_MO_RONG` (13 khuon trung ten) giu NOI DUNG cua `nl.BENH` (da
dung trong bo sinh) va lay them cac truong `bien_the_*` cua ban mo rong. Chi them, khong
doi ma chu cu.

`mo_rong=False` tra dung 200 khuon goc: hanh vi cu giu nguyen tung bit.
"""
from __future__ import annotations

from functools import lru_cache

from src import ngu_lieu_viet as nl


def _goc() -> list:
    return list(getattr(nl, "BENH_GOC", nl.BENH[:200]))


@lru_cache(maxsize=2)
def ds_khuon(mo_rong: bool = False) -> tuple:
    """-> tuple cac dict khuon. Khong sua cac dict tra ve."""
    goc = _goc()
    if not mo_rong:
        return tuple(goc)
    ten_goc = {b["ten"] for b in goc}
    try:
        from src import khuon_mo_rong as kmr
    except ImportError:
        return tuple(nl.BENH)
    theo_ten = {b["ten"]: b for b in kmr.BENH_MO_RONG}
    ra, da = [], set()
    for b in nl.BENH:
        ten = b["ten"]
        if ten in da:
            continue
        da.add(ten)
        mr = theo_ten.get(ten)
        if mr is not None and ten not in ten_goc:
            b = {**b, **{k: v for k, v in mr.items() if k.startswith("bien_the_")}}
        ra.append(b)
    for b in kmr.BENH_MO_RONG:
        if b["ten"] not in da:
            da.add(b["ten"])
            ra.append(b)
    return tuple(ra)


@lru_cache(maxsize=1)
def chi_nu() -> frozenset:
    """Khuon chi o nu: tap goc + tap cua khuon mo rong (ten khong trung khuon goc)."""
    try:
        from src import khuon_mo_rong as kmr
        return frozenset(nl.CHI_NU) | frozenset(kmr.CHI_NU_MO_RONG)
    except ImportError:
        return frozenset(nl.CHI_NU)


@lru_cache(maxsize=1)
def chi_nam() -> frozenset:
    try:
        from src import khuon_mo_rong as kmr
        return frozenset(nl.CHI_NAM) | frozenset(kmr.CHI_NAM_MO_RONG)
    except ImportError:
        return frozenset(nl.CHI_NAM)


@lru_cache(maxsize=1)
def dot_cua_khuon() -> dict:
    """{ten khuon: so dot} cho MOI khuon ngoai 200 khuon goc.

    Dot 1 va 2 la hai dot 200 khuon cua `khuon_mo_rong.TEN_THEO_DOT`; dot 0 la phan con lai
    (cac khuon cua `nl.BENH` o vi tri 200-269 chua nam trong dot nao). Khuon goc khong co
    trong bang nay.
    """
    ten_goc = {b["ten"] for b in _goc()}
    try:
        from src import khuon_mo_rong as kmr
        theo_dot = dict(getattr(kmr, "TEN_THEO_DOT", {}))
    except ImportError:
        theo_dot = {}
    ra = {}
    for b in ds_khuon(True):
        t = b["ten"]
        if t in ten_goc:
            continue
        ra[t] = next((d for d, tap_ten in theo_dot.items() if t in tap_ten), 0)
    return ra


@lru_cache(maxsize=1)
def thanh_vien_dot() -> dict:
    """{so dot: tuple ten khuon da sap xep} cua kho day du."""
    nhom: dict = {}
    for t, d in dot_cua_khuon().items():
        nhom.setdefault(d, []).append(t)
    return {d: tuple(sorted(v)) for d, v in nhom.items()}
