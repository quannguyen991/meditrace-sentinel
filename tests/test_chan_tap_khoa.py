# -*- coding: utf-8 -*-
"""Chot chan tap kiem tra cuoi phai chan DUNG TEN tap dang dung.

LO~ DA TON TAI den 11/09/2026: chot so NGUYEN TEN voi "kiem_tra_cuoi" — ten tap
cua bo du lieu cuoc thi cu — nen `viet_kiem_tra_cuoi` di qua. Va 8/13 script
nhan `--tap`, trong do co `nhanh.py`, khong goi chot nao ca. Tuc la suot tu khi
doi sang bo tu sinh, tap kiem tra cuoi chi duoc bao ve bang tri nho.
"""
import pathlib

import pytest

from src import du_lieu


@pytest.mark.parametrize("ten", [
    "kiem_tra_cuoi", "viet_kiem_tra_cuoi", "viet3k_kiem_tra_cuoi",
    "viet_kiem_tra_cuoi_th4", "thach_thuc_phuong_ngu_kiem_tra_cuoi"])
def test_chan_MOI_ten_chua_kiem_tra_cuoi(ten, monkeypatch):
    monkeypatch.delenv(du_lieu.MO_TAP_KHOA, raising=False)
    with pytest.raises(SystemExit):
        du_lieu.chan_tap_khoa(ten)


def test_chan_ca_khi_nam_trong_danh_sach(monkeypatch):
    monkeypatch.delenv(du_lieu.MO_TAP_KHOA, raising=False)
    with pytest.raises(SystemExit):
        du_lieu.chan_tap_khoa(["viet_phat_trien", "viet_kiem_tra_cuoi"])


@pytest.mark.parametrize("ten", [
    "viet_phat_trien", "viet_train", "kiem_tra_chung",
    "thach_thuc_phuong_ngu_phat_trien"])
def test_KHONG_chan_tap_khac(ten, monkeypatch):
    monkeypatch.delenv(du_lieu.MO_TAP_KHOA, raising=False)
    du_lieu.chan_tap_khoa(ten)


def test_mo_chot_chi_bang_bien_moi_truong_co_chu_dinh(monkeypatch):
    monkeypatch.setenv(du_lieu.MO_TAP_KHOA, "1")
    du_lieu.chan_tap_khoa("viet_kiem_tra_cuoi")


def test_MOI_script_nhan_tap_deu_goi_chot():
    """Them mot script nhan `--tap` ma quen goi chot la mo mot duong vao tap
    kiem tra cuoi. Quet ma nguon thay vi tin vao viec nho — viec nho da hong
    mot lan roi."""
    goc = pathlib.Path(__file__).resolve().parent.parent / "src"
    thieu = []
    for p in sorted(goc.glob("*.py")):
        van = p.read_text(encoding="utf-8")
        if 'add_argument("--tap"' in van and "chan_tap_khoa(" not in van:
            thieu.append(p.name)
    assert not thieu, f"nhan --tap ma khong goi chan_tap_khoa: {thieu}"
