# -*- coding: utf-8 -*-
"""Tang 1: hieu phuong ngu nhung giu nguyen van, va KHONG chon ho nghia khi mo ho."""
from src import chuan_hoa as ch
from src import doan_van


def test_doi_nghia_nhung_giu_duoc_vi_tri_nguyen_van():
    assert ch.chuan_hoa("hổm rày ổng xỉu hoài") == "dạo gần đây ông ấy ngất hoài"
    c = ch.phan_tich("Hổm rày ổng xỉu hoài")
    assert [x.goc for x in c] == ["Hổm rày", "ổng", "xỉu"]


def test_TE_la_trieu_chung_KHONG_bi_doi():
    """"te" = kia o mien Trung, nhung "te chan" la trieu chung — doi la bia."""
    assert ch.chuan_hoa("tê chân mấy bữa nay") == "tê chân mấy bữa nay"
    assert ch.chuan_hoa("hôm tê cháu sốt") == "hôm kia cháu sốt"


def test_RANG_la_cai_rang_KHONG_bi_doi():
    assert "răng" in ch.chuan_hoa("lâu rồi chưa thấy mọc răng")
    assert ch.chuan_hoa("làm răng mà sốt rứa") == "làm sao mà sốt vậy"


def test_CHI_duoi_KHONG_bi_doi():
    assert ch.chuan_hoa("suy tĩnh mạch chi dưới") == "suy tĩnh mạch chi dưới"
    assert ch.chuan_hoa("có chi mô") == "không có gì"


def test_BA_vai_KHONG_bi_doi():
    assert ch.chuan_hoa("đau bả vai") == "đau bả vai"
    assert ch.chuan_hoa("bả sốt hai bữa") == "bà ấy sốt hai bữa"


def test_HONG_het_cau_la_khong_con_sau_tu_bo_phan_la_MO_HO():
    assert ch.chuan_hoa("có đau hông?") == "có đau không?"
    c = ch.can_hoi("đau hông bên phải")
    assert c and c[0].goc == "hông"
    # mo ho that thi KHONG ghi nghia nao — khong chon ho nguoi noi
    assert ch.chuan_hoa("đau hông bên phải") == "đau hông bên phải"


def test_nong_ham_hap_la_CAN_HOI_khong_tu_thanh_sot():
    c = ch.can_hoi("cháu nóng hầm hập")
    assert c and c[0].muc_tin == ch.CAN_HOI
    assert "sốt" in ch.chuan_hoa("cháu nóng hầm hập")
    assert "sốt" not in ch.chuan_hoa("cháu nóng hầm hập", gom_can_hoi=False)


def test_ME_la_CAN_HOI():
    """Nham ba voi me la dung loi quy gan cua du an — khong tu chon."""
    assert ch.can_hoi("mệ bị tai biến")


def test_biet_MOI_tu_phuong_ngu_bo_sinh_dung():
    """Vong tron phai noi ro (xem docstring `chuan_hoa`): tang nay biet truoc moi
    tu ma bo sinh thay, nen phep thu cap phuong ngu khong do duoc tu LA."""
    from src import phuong_ngu
    for vung, cap in phuong_ngu.THAY_DUOC.items():
        for _chuan, dia_phuong in cap:
            assert ch.phan_tich(dia_phuong), (vung, dia_phuong)


# ------------------------------------------------------------- doan van

def test_cat_doan_khong_cat_so_thap_phan():
    van = "Nhiệt độ 38,5 độ, mạch 110. Họng đỏ"
    assert [van[a:b] for a, b in doan_van.cac_doan(van)] == \
        ["Nhiệt độ 38,5 độ", "mạch 110", "Họng đỏ"]


def test_dau_ket_nhan_ra_cau_hoi():
    van = "Cháu sốt mấy hôm? Dạ ba hôm."
    d = doan_van.cac_doan(van)
    assert doan_van.dau_ket(van, d[0]) == "?"
    assert doan_van.dau_ket(van, d[1]) == "."
