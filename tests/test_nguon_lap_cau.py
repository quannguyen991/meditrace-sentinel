# -*- coding: utf-8 -*-
from src.bo_du_lieu import ngu_lieu_viet as nl
from src.do_luong import nguon_lap_cau as nlc
from src.do_luong import do_lap_cau as dl


def test_cau_trong_nhom_duoc_gan_ten_nhom():
    nhom, co_dinh = nlc._cac_nhom_cau(), nlc._cau_co_dinh()
    cau = nl.MO_DAU[0]
    assert nlc.phan_loai_nguon(cau, nhom, co_dinh).startswith("nhom:")


def test_cau_bia_la_ghep():
    assert nlc.phan_loai_nguon("xin chào cái gì đó không thuộc nhóm nào cả 12345",
                               nlc._cac_nhom_cau(), nlc._cau_co_dinh()) == "ghep"


def test_phan_loai_chiu_duoc_hoa_thuong_va_nfd():
    import unicodedata
    cau = unicodedata.normalize("NFD", nl.MO_DAU[0].upper())
    assert nlc.phan_loai_nguon(cau).startswith("nhom:")


def test_bang_nguon_lap_tong_khop_so_cau_lap():
    ca = [{"input": "Bác sĩ: a b c.\nBệnh nhân: d e f."},
          {"input": "Bác sĩ: a b c.\nBệnh nhân: g h i."}]
    r = nlc.bang_nguon_lap(ca)
    th = dl.do_lap_cau(ca)
    assert r["tong_cau_lap"] == th["so_cau"] - th["so_cau_duy_nhat"] == 1
    assert sum(r["theo_nguon"].values()) == 1
