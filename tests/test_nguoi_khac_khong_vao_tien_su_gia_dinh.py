# -*- coding: utf-8 -*-
"""Nguoi khong phai benh nhan va khong phai nguoi nha (vd benh nhan khac cung phong)
khong duoc ghi vao TIEN SU GIA DINH cua benh nhan; phai sang CAN XAC NHAN."""
from src.duong_ong import b5_viet_ban_nhap as sba
from src.he_thong import dich_vu_http as dich_vu


def _p(**k):
    p = {"id": 1, "chu_the_id": 2, "bang_chung": [3], "trang_thai": "còn hiệu lực",
         "tinh_huong": "thực tế", "noi_dung": "đái tháo đường"}
    p.update(k)
    return p


def test_nguoi_noi_la_nguoi_khac_sang_can_xac_nhan():
    muc, ly_do = sba._muc_cho(_p(nguoi_noi="người khác", ten_chu_the="người khác"), 0)
    assert muc == "CẦN XÁC NHẬN"
    assert "người khác" in ly_do


def test_nguoi_nha_ke_benh_cua_me_van_vao_tien_su_gia_dinh():
    muc, _ = sba._muc_cho(_p(nguoi_noi="người nhà", ten_chu_the="mẹ tôi"), 0)
    assert muc == sba.MUC_NGUOI_KHAC


def test_ca_mau_hai_benh_nhan_khong_ghi_benh_nguoi_thu_hai_vao_ho_so():
    r = dich_vu.doc_ca("demo_hai_benh_nhan", "C_khoa_hoi")
    sach = r["du_doan_khong_muc_phu"].lower()
    assert "metformin" not in sach and "đái tháo đường" not in sach
    assert "vợ" not in r["du_doan"].lower()
    assert "cefuroxim" not in sach
