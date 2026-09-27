# -*- coding: utf-8 -*-
"""Do thi trang thai: dinh chinh chi thang khi CHINH nguoi noi tu sua.

Truoc 11/09/2026 `cap_nhat.ap_luat` cho ban sau thang moi luc, bat ke ai noi.
Nguoi nha noi "4 ngay" roi benh nhan noi "2 ngay" — hay bac si noi "vay la 2
ngay" — la HAI nguon, khong co can cu chon ben. Ke ca loi bac si cung khong tu
dong dung hon loi nguoi benh.
"""
from src import cap_nhat
from src.phat_bieu import PhatBieu


def pb(id_, nguoi_noi, moc, **kw):
    return PhatBieu(id=id_, nguoi_noi=nguoi_noi, chu_the_id=0, noi_dung="sốt",
                    bang_chung=[id_ + 1], moc_thoi_gian=moc, **kw)


def test_TU_dinh_chinh_thi_ban_sau_thang():
    ra = cap_nhat.ap_luat([pb(0, "người nhà", "3 ngày"),
                           pb(1, "người nhà", "2 ngày", quan_he="đính chính",
                              quan_he_voi=0)])
    assert [p.trang_thai for p in ra] == ["bị thay thế", "còn hiệu lực"]


def test_NGUOI_KHAC_dinh_chinh_thi_ha_ve_mau_thuan():
    ra = cap_nhat.ap_luat([pb(0, "người nhà", "4 ngày"),
                           pb(1, "bệnh nhân", "2 ngày", quan_he="đính chính",
                              quan_he_voi=0)])
    assert [p.trang_thai for p in ra] == ["chưa giải quyết", "chưa giải quyết"]
    assert ra[1].quan_he == "mâu thuẫn"


def test_BAC_SI_cung_KHONG_tu_thang():
    ra = cap_nhat.ap_luat([pb(0, "bệnh nhân", "4 ngày"),
                           pb(1, "bác sĩ", "2 ngày", quan_he="đính chính",
                              quan_he_voi=0)])
    assert all(p.trang_thai == "chưa giải quyết" for p in ra)


def test_KHONG_sua_ban_goc():
    goc = [pb(0, "người nhà", "4 ngày"),
           pb(1, "bệnh nhân", "2 ngày", quan_he="đính chính", quan_he_voi=0)]
    cap_nhat.ap_luat(goc)
    assert goc[1].quan_he == "đính chính" and goc[0].trang_thai == "còn hiệu lực"


def test_lich_su_giu_ban_bi_thay_the_KEM_ly_do():
    ra = cap_nhat.ap_luat([pb(0, "người nhà", "4 ngày"),
                           pb(1, "người nhà", "2 ngày", quan_he="đính chính",
                              quan_he_voi=0)])
    ls = cap_nhat.lich_su(ra)
    assert len(ls) == 1 and ls[0]["id"] == 0
    assert "đính chính" in ls[0]["ly_do"] and ls[0]["moc_thoi_gian"] == "4 ngày"


def test_lich_su_mau_thuan_ghi_CA_HAI_ban():
    ra = cap_nhat.ap_luat([pb(0, "người nhà", "4 ngày"),
                           pb(1, "bệnh nhân", "2 ngày", quan_he="mâu thuẫn",
                              quan_he_voi=0)])
    assert {x["id"] for x in cap_nhat.lich_su(ra)} == {0, 1}
