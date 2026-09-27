# -*- coding: utf-8 -*-
"""Tu khoa lam sang quan trong va cac CAP TOI THIEU (yeu cau XII, XIII).

Mot bo nhan dang giong noi lam mat khac biet trong cac cap duoi day la loi nguy
hiem. Phep thu nay canh BO TRICH TU KHOA: no phai phan biet duoc tung cap, de
benchmark va bo phat hien bat dong dung duoc no.
"""
import pytest

from src.audio.asr import critical_tokens as ct


@pytest.mark.parametrize("a,b,loai", [
    ("uống 5 mg mỗi ngày", "uống 50 mg mỗi ngày", "lieu"),
    ("uống năm mi li gam", "uống năm mươi mi li gam", "lieu"),
    ("ho một ngày rồi", "ho mười ngày rồi", "thoi_gian"),
    ("sốt một tuần", "sốt mười tuần", "thoi_gian"),
    ("có dị ứng penicillin", "không dị ứng penicillin", "phu_dinh"),
    ("đang dùng thuốc", "đã ngừng thuốc", "trang_thai"),
    ("bệnh nhân bị hen", "bố bệnh nhân bị hen", "nguoi"),
    ("ngày 1 lần", "ngày 2 lần", "tan_suat"),
    ("uống amoxicillin", "uống metformin", "thuoc"),
])
def test_cap_toi_thieu_phan_biet_duoc(a, b, loai):
    assert loai in ct.khac_nhau(ct.trich(a), ct.trich(b)), (ct.trich(a), ct.trich(b))


@pytest.mark.parametrize("a,b", [
    ("uống 500 mg", "uống năm trăm mi li gam"),
    ("uống 5 mg", "uống năm miligam"),
    ("ngày hai lần", "ngày 2 lần"),
    ("ho mười ngày", "ho 10 ngày"),
    ("uống Amoxicillin.", "uống amoxicilin"),
])
def test_cung_nghia_khac_cach_viet_khong_bao_khac(a, b):
    assert ct.khac_nhau(ct.trich(a), ct.trich(b)) == []


def test_so_tu_doc_dung():
    assert ct.trich("năm trăm mi li gam")["lieu"] == {(500, "mg")}
    assert ct.trich("năm mươi mi li gam")["lieu"] == {(50, "mg")}
    assert ct.trich("mười lăm ngày")["thoi_gian"] == {(15, "ngày")}
    assert ct.trich("hôm qua đau nhiều")["thoi_gian"] == {"hôm qua"}


def test_trich_khong_sua_chu():
    """Trich chi de SO SANH; khong tra ve chu da sua."""
    r = ct.trich("Người nóng hầm hập.")
    assert r["thuoc"] == set() and r["lieu"] == set()
