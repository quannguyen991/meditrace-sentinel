# -*- coding: utf-8 -*-
"""Khi bat `mo_rong` (kho 270 khuon), 200 khuon GOC khong duoc doi tap.

VI SAO. `tach_tap_viet.phan_khuon` xep MOI khuon ngoai 100 khuon dau vao cung mot nhom
`k_moi` roi xep hang bang bam. Them khuon vao nhom do doi hang cua ca khuon cu 101-200,
nen mot so khuon cu nhay tap: do ngay 22/11/2026, 12 trong 200 khuon cu doi tap khi bat
`mo_rong` (7 khuon tu phat trien sang train, 5 khuon tu kiem tra cuoi sang phat trien).

HAU QUA. Bo sinh voi `mo_rong=True` dua khuon thuoc tap phat trien/kiem tra cuoi DA DONG
BANG vao tap train. Mo hinh huan luyen tren bo do roi danh gia tren `viet_phat_trien` /
`viet_kiem_tra_cuoi` cu se thay lai khuon da hoc: ro ri, lam dep so lieu.

Cach sua (xem Task F2 trong ke hoach): khuon moi di vao nhom RIENG, khong chung nhom
voi khuon 101-200. Phep thu nay phai PASS truoc khi sinh bo v2 hay huan luyen tren no.
"""
from src import ngu_lieu_viet as nl
from src import sinh_hoi_thoai_viet as sh
from src import tach_tap_viet as tt


def _goc():
    return [b["ten"] for b in getattr(nl, "BENH_GOC", nl.BENH[:200])]


def _tat():
    """Kho day du (200 goc + khuon mo rong), cung nguon voi bo sinh va buoc chia."""
    from src import kho_khuon
    return [b["ten"] for b in kho_khuon.ds_khuon(True)]


def test_phan_khuon_200_cu_khong_doi_khi_them_khuon_moi():
    goc = _goc()
    tat = _tat()
    if len(tat) == len(goc):
        return  # chua co khuon mo rong
    t0 = {t: k for k, v in tt.phan_khuon(goc).items() for t in v}
    t1 = {t: k for k, v in tt.phan_khuon(tat).items() for t in v}
    doi = sorted(t for t in goc if t0[t] != t1[t])
    assert not doi, f"{len(doi)} khuon cu doi tap khi them khuon moi: {doi}"


def test_bang_tap_khuon_mo_rong_giu_tap_cua_200_cu():
    goc = _goc()
    if len(nl.BENH) == len(goc):
        return
    b0, b1 = sh.bang_tap_khuon(mo_rong=False), sh.bang_tap_khuon(mo_rong=True)
    doi = sorted(t for t in goc if b0[t] != b1[t])
    assert not doi, f"{len(doi)} khuon cu doi tap o bang_tap_khuon(mo_rong=True): {doi}"


def test_khuon_moi_chia_10_phan_tram_phat_trien_va_kiem_tra():
    from src import kho_khuon
    p = tt.phan_khuon(_tat())
    for d, ten_dot in kho_khuon.thanh_vien_dot().items():
        n = len(ten_dot)
        dem = {k: sum(1 for t in ten_dot if t in p[k]) for k in p}
        assert dem["phat_trien"] == max(1, round(0.10 * n)), (d, dem)
        assert dem["kiem_tra_cuoi"] == max(1, round(0.10 * n)), (d, dem)
        assert sum(dem.values()) == n


def test_khong_khuon_nao_o_hai_tap_khi_mo_rong():
    p = tt.phan_khuon(_tat())
    assert not (p["train"] & p["phat_trien"])
    assert not (p["train"] & p["kiem_tra_cuoi"])
    assert not (p["phat_trien"] & p["kiem_tra_cuoi"])
