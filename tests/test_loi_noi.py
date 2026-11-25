# -*- coding: utf-8 -*-
from src.canh_bao.loi_noi import bo_tu_dem, nhan_cau_hoi, tach_y


def _cat(van):
    return [van[a:b] for a, b in tach_y(van)]


def test_tach_y_khong_dau_theo_tu_noi():
    assert len(tach_y("ho ba ngày nay còn sốt thì hôm qua mới bị")) == 2


def test_tach_y_co_dau_theo_dau():
    assert _cat("Em ho ba ngày. Sốt từ hôm qua, có đau họng.") == [
        "Em ho ba ngày", "Sốt từ hôm qua", "có đau họng"]


def test_tach_y_khoang_la_vi_tri_trong_van_goc():
    van = "ờ em ho ba ngày nay rồi sốt nữa"
    for a, b in tach_y(van):
        assert van[a:b] == van[a:b].strip() and van[a:b]


def test_tach_y_cau_dai_khong_dau_bi_cat():
    van = " ".join(["ho"] * 60)
    assert all(len(van[a:b].split()) <= 25 for a, b in tach_y(van))


def test_tach_y_rong():
    assert tach_y("") == [] and tach_y("  ") == []


def test_nhan_cau_hoi_co_khong():
    assert nhan_cau_hoi("chị có ho không")


def test_nhan_cau_hoi_cau_ke_phu_dinh():
    assert not nhan_cau_hoi("em không ho")


def test_nhan_cau_hoi_chua_a():
    assert nhan_cau_hoi("uống thuốc chưa ạ")


def test_nhan_cau_hoi_dau_hoi():
    assert nhan_cau_hoi("Ho mấy ngày rồi?")


def test_nhan_cau_hoi_tu_hoi():
    assert nhan_cau_hoi("bé bị sốt từ hôm nào") and nhan_cau_hoi("đau ở đâu")


def test_nhan_cau_hoi_tra_loi_ngan_khong_phai_hoi():
    assert not nhan_cau_hoi("dạ không") and not nhan_cau_hoi("dạ có ạ") and not nhan_cau_hoi("không ạ")


def test_bo_tu_dem():
    assert bo_tu_dem("ờ thì em không không có sốt") == "thì em không có sốt"


def test_bo_tu_dem_giu_a_cuoi_cau_hoi():
    assert bo_tu_dem("bé sốt à") == "bé sốt à"
    assert bo_tu_dem("à bé sốt từ hôm qua") == "bé sốt từ hôm qua"
