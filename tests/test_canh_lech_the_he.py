# -*- coding: utf-8 -*-
"""Canh cham ket qua cua the he nay bang dap an cua the he khac.

VI SAO CAN TEST. Loi da xay ra that ngay 16/09/2026 va khong ai thay: id cua hai the
he trung nhau (cung danh sach kich ban), chi noi dung loi thoai khac. Bo cham chay
binh thuong, in ra mot bang so dep, va bang so do sai. Xem `canh_bo_lech_the_he`.
"""
import pytest

from src import cham_he_thong


def _ca(i, van):
    return {"id": i, "input": van}


def test_cung_hoi_thoai_thi_khong_bao_gi():
    goc = {"a": _ca("a", "1. Cháu sốt ba hôm rồi ạ.")}
    kq = {"a": {"id": "a", "input": "1. Cháu sốt ba hôm rồi ạ."}}
    cham_he_thong.canh_bo_lech_the_he("ra_C_x.jsonl", goc, kq)


def test_hoi_thoai_khac_thi_dung_han():
    goc = {"a": _ca("a", "1. Cháu sốt ba hôm rồi ạ.")}
    kq = {"a": {"id": "a", "input": "1. Cháu sốt bốn hôm rồi ạ."}}
    with pytest.raises(SystemExit) as e:
        cham_he_thong.canh_bo_lech_the_he("ra_C_x.jsonl", goc, kq)
    assert "the he du lieu khac" in str(e.value)


def test_chi_mot_ca_lech_cung_dung():
    """Khong co nguong 'lech it thi bo qua': mot ca lech la mot bo du lieu khac."""
    goc = {"a": _ca("a", "x"), "b": _ca("b", "y")}
    kq = {"a": {"id": "a", "input": "x"}, "b": {"id": "b", "input": "z"}}
    with pytest.raises(SystemExit):
        cham_he_thong.canh_bo_lech_the_he("ra_C_x.jsonl", goc, kq)


def test_ban_ghi_khong_co_input_thi_bo_qua():
    """Tep ket qua cu khong luu `input`. Khong the kiem, nhung khong duoc chan."""
    goc = {"a": _ca("a", "x")}
    kq = {"a": {"id": "a"}}
    cham_he_thong.canh_bo_lech_the_he("ra_C_x.jsonl", goc, kq)


def test_bao_loi_neu_bo_du_lieu_thieu_truong_input():
    goc = {"a": {"id": "a"}}
    kq = {"a": {"id": "a", "input": "x"}}
    with pytest.raises(SystemExit):
        cham_he_thong.canh_bo_lech_the_he("ra_C_x.jsonl", goc, kq)
