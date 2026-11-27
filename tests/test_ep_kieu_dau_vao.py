# -*- coding: utf-8 -*-
"""Hoi quy: gia tri JSON dang chuoi ("25", "82") hoac rac khong lam sap cong rui ro
(truoc day TypeError trong nhanh.chay_trung_gian -> /api/ho-so 500)."""
import pytest

from src.duong_ong import b5_xep_cho_cong_rui_ro as cong_rui_ro
from src.he_thong.ep_kieu_dau_vao import (chuan_hoa_du_lieu_xet_nghiem_dau_vao,
                                 chuan_hoa_thong_tin_benh_nhan, so_an_toan)


@pytest.mark.parametrize("x,mong", [
    ("25", 25.0), (" 82 ", 82.0), ("2,5", 2.5), (10, 10.0), (3.5, 3.5),
    ("abc", None), ("", None), (None, None), (True, None), ([], None), ({}, None),
    ("nan", None), ("inf", None),
])
def test_so_an_toan(x, mong):
    assert so_an_toan(x) == mong


def test_chuan_hoa_thong_tin_benh_nhan_chuoi_so_va_rac():
    tt = chuan_hoa_thong_tin_benh_nhan({"tuoi": "82", "egfr": "25", "tuan_thai": "10",
                                        "thang_tuoi": "abc", "ten": "A", "thai_ky": True})
    assert tt["tuoi"] == 82 and isinstance(tt["tuoi"], int)
    assert tt["egfr"] == 25.0
    assert tt["tuan_thai"] == 10
    assert "thang_tuoi" not in tt            # rac -> coi nhu thieu
    assert tt["ten"] == "A" and tt["thai_ky"] is True


def test_chuan_hoa_thong_tin_khong_phai_dict():
    assert chuan_hoa_thong_tin_benh_nhan(None) is None
    assert chuan_hoa_thong_tin_benh_nhan("x") is None


def test_chuan_hoa_xet_nghiem_giu_don_vi():
    xn = chuan_hoa_du_lieu_xet_nghiem_dau_vao({"creatinine": "1,4", "creatinine_unit": "mg/dL",
                                               "egfr": "??", "ast": 40})
    assert xn == {"creatinine": 1.4, "creatinine_unit": "mg/dL", "ast": 40.0}


@pytest.mark.parametrize("bn", [
    {"egfr": "25"}, {"tuoi": "82"}, {"thai_ky": True, "tuan_thai": "10"},
    {"egfr": "rac"}, {"tuoi": "tám mươi"}, {"thang_tuoi": "3"}, {"so_thuoc_dang_dung": "6"},
    {"egfr": None, "tuoi": [], "so_thuoc_dang_dung": {}},
])
def test_cong_rui_ro_khong_sap_voi_chuoi(bn):
    kq = cong_rui_ro.phan_tich_co_dia_benh_nhan(bn)
    assert kq.he_so_tong >= 1.0


def test_cong_rui_ro_chuoi_so_van_duoc_tinh():
    assert cong_rui_ro.phan_tich_co_dia_benh_nhan({"egfr": "25"}).he_so_tong > 1.0
    assert cong_rui_ro.phan_tich_co_dia_benh_nhan({"tuoi": "82"}).he_so_tong > 1.0
    kq = cong_rui_ro.phan_tich_co_dia_benh_nhan({"thai_ky": True, "tuan_thai": "10"})
    assert any("3 tháng đầu" in y for y in kq.cac_yeu_to)
