import pytest

from src.do_luong.do_sao_chep import do_phu_va_mat_do, manh_trich


def test_giong_het():
    assert do_phu_va_mat_do("Một hai ba", "Một hai ba") == {
        "coverage": 1.0, "density": 3.0, "so_tu": 3}


def test_khong_trung_va_rong():
    assert do_phu_va_mat_do("một hai", "ba bốn") == {
        "coverage": 0.0, "density": 0.0, "so_tu": 2}
    assert do_phu_va_mat_do("", "ba") == {
        "coverage": 0.0, "density": 0.0, "so_tu": 0}


def test_hai_manh_tham_lam():
    assert manh_trich("a b x c d e", "a b q c d e") == ["a b", "c d e"]
    kq = do_phu_va_mat_do("a b x c d e", "a b q c d e")
    assert kq["coverage"] == pytest.approx(5 / 6)
    assert kq["density"] == pytest.approx(13 / 6)


def test_tieng_viet_va_chuan_hoa_unicode():
    assert manh_trich("Đau ngực", "đau ngu\u031b\u0323c") == ["đau ngực"]
    assert do_phu_va_mat_do("Đau ngực", "đau ngực")["coverage"] == 1.0
