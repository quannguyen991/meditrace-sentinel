"""Hoi quy K6: khop lieu thuoc phai theo ranh gioi so.

Truoc day phep kiem chuoi con tho chay truoc nhanh ranh gioi so nen
"5 mg" khop nham vao "2.5 mg", "25 mg"; "1 viên" khop vao "11 viên".
"""
import pytest

from src.khoa_bang_chung import _chuan_trich, _khop_chi_tiet_thuoc


def _khop(ct, van):
    return _khop_chi_tiet_thuoc(ct, _chuan_trich(van))


@pytest.mark.parametrize("ct,van", [
    ("5 mg", "bác cho uống amlodipin 2.5 mg mỗi sáng"),
    ("5 mg", "bác cho uống amlodipin 2,5 mg mỗi sáng"),
    ("5 mg", "uống 25 mg mỗi ngày"),
    ("5 mg", "uống 5.5 mg mỗi ngày"),
    ("1 viên", "mỗi lần 11 viên"),
    ("2 lần", "ngày 12 lần"),
    ("50 mg", "500 mg"),
    ("500 mg", "1500 mg"),
])
def test_khong_khop_nham_so(ct, van):
    assert _khop(ct, van) is False


@pytest.mark.parametrize("ct,van", [
    ("5 mg", "uống amlodipin 5 mg buổi sáng"),
    ("5mg", "uống amlodipin 5 mg buổi sáng"),
    ("5 mg", "uống amlodipin 5mg buổi sáng"),
    ("2.5 mg", "uống 2,5 mg"),
    ("2,5 mg", "uống 2.5 mg"),
    ("1 viên", "mỗi lần 1 viên sau ăn"),
    ("2 lần", "ngày 2 lần sáng chiều"),
    ("hai lần", "ngày 2 lần"),
    ("500 mg", "paracetamol 500 mg khi sốt"),
    ("nửa viên", "uống 0,5 viên"),
])
def test_van_khop_dung(ct, van):
    assert _khop(ct, van) is True
