# -*- coding: utf-8 -*-
"""Phep thu kiem tra bien the cau khong lam doi nhan va trich dan.

Task B3 cua Kế hoạch Nâng cấp Toàn diện Meditrace.
Bao dam rang khi mo rong bien the cau:
  1. Trich dan trong moi menh de dap an luon la chuoi con nguyen van cua input.
  2. Moi menh de co day du cac truong nhan theo dung luoc do chuan.
  3. Kiem tra ca tren bo sinh goc (mo_rong=False) va bo sinh mo rong (mo_rong=True).
"""
import pytest
from src.bo_du_lieu import sinh_hoi_thoai_viet as sh

CAC_KHOA_CHUAN = [
    "chu_the", "noi_dung", "muc", "moc_thoi_gian", "phu_dinh", "tinh_huong",
    "luot", "thoi_gian_su_kien", "quan_he", "quan_he_voi", "trang_thai",
    "do_chac_chan", "hanh_vi", "thuoc", "trich_dan"
]


def test_trich_dan_la_chuoi_con_cua_input():
    bo = sh.sinh_bo(500, seed=7)
    for ca in bo:
        hoi_thoai = ca["input"]
        for md in ca["dap_an"]:
            assert "trich_dan" in md
            for doan in md["trich_dan"]:
                assert doan in hoi_thoai, (
                    f"Ca {ca['id']}, menh de {md['noi_dung']}: "
                    f"trich dan {doan!r} khong phai chuoi con cua input"
                )


def test_moi_menh_de_co_du_truong_nhan():
    bo = sh.sinh_bo(500, seed=7)
    for ca in bo:
        for md in ca["dap_an"]:
            for k in CAC_KHOA_CHUAN:
                assert k in md, f"Ca {ca['id']} thieu khoa {k!r} trong dap an"


def test_mo_rong_trich_dan_la_chuoi_con_cua_input():
    bo = sh.sinh_bo(500, seed=7, mo_rong=True)
    for ca in bo:
        hoi_thoai = ca["input"]
        for md in ca["dap_an"]:
            assert "trich_dan" in md
            for doan in md["trich_dan"]:
                assert doan in hoi_thoai, (
                    f"Ca mo rong {ca['id']}, menh de {md['noi_dung']}: "
                    f"trich dan {doan!r} khong phai chuoi con cua input"
                )


def test_mo_rong_moi_menh_de_co_du_truong_nhan():
    bo = sh.sinh_bo(500, seed=7, mo_rong=True)
    for ca in bo:
        for md in ca["dap_an"]:
            for k in CAC_KHOA_CHUAN:
                assert k in md, f"Ca mo rong {ca['id']} thieu khoa {k!r} trong dap an"
