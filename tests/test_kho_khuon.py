# -*- coding: utf-8 -*-
"""Kho khuon dung chung: bo sinh, chia tap va loc gioi tinh nhin cung mot danh sach."""
import collections

from src.bo_du_lieu import kho_khuon as kk
from src.bo_du_lieu import ngu_lieu_viet as nl
from src.bo_du_lieu import sinh_hoi_thoai_viet as sh
from src.bo_du_lieu import chia_tap_theo_khuon as tt

KHOA_BAT_BUOC = ("ten", "nhom", "dien_tien", "chinh", "phu", "kham", "chan_doan", "ke_hoach")


def test_mo_rong_tat_tra_dung_200_khuon_goc():
    assert [b["ten"] for b in kk.ds_khuon(False)] == [b["ten"] for b in nl.BENH_GOC]
    assert len(kk.ds_khuon(False)) == 200


def test_mo_rong_bat_co_200_goc_dau_roi_70_cua_nl_roi_khuon_mo_rong():
    ds = kk.ds_khuon(True)
    ten = [b["ten"] for b in ds]
    assert ten[:200] == [b["ten"] for b in nl.BENH_GOC]
    assert ten[200:270] == [b["ten"] for b in nl.BENH[200:270]]
    from src.bo_du_lieu import khuon_mo_rong as kmr
    assert set(b["ten"] for b in kmr.BENH_MO_RONG) <= set(ten)
    assert len(ten) == len(set(ten)), "co ten khuon trung"


def test_moi_khuon_du_truong_bat_buoc():
    for b in kk.ds_khuon(True):
        for k in KHOA_BAT_BUOC:
            assert b.get(k), (b["ten"], k)


def test_khuon_trung_ten_giu_noi_dung_nl_va_them_bien_the():
    from src.bo_du_lieu import khuon_mo_rong as kmr
    nl_theo_ten = {b["ten"]: b for b in nl.BENH[200:270]}
    chung = [b for b in kmr.BENH_MO_RONG if b["ten"] in nl_theo_ten]
    assert chung, "khong con khuon trung ten de kiem"
    theo = {b["ten"]: b for b in kk.ds_khuon(True)}
    for mr in chung:
        gop = theo[mr["ten"]]
        assert gop["kham"] == nl_theo_ten[mr["ten"]]["kham"]
        assert gop["bien_the_kham"] == mr["bien_the_kham"]


def test_chia_tap_200_khuon_goc_khong_doi_khi_mo_rong():
    goc = [b["ten"] for b in kk.ds_khuon(False)]
    t0 = {t: k for k, v in tt.phan_khuon(goc).items() for t in v}
    t1 = {t: k for k, v in tt.phan_khuon([b["ten"] for b in kk.ds_khuon(True)]).items() for t in v}
    assert [t for t in goc if t0[t] != t1[t]] == []


def test_bang_tap_khuon_phu_moi_khuon_cua_kho():
    bang = sh.bang_tap_khuon(mo_rong=True)
    assert all(b["ten"] in bang for b in kk.ds_khuon(True))
    assert set(bang.values()) == {"train", "phat_trien", "kiem_tra_cuoi"}


def test_moi_dot_chia_10_phan_tram_phat_trien_va_kiem_tra():
    ten = [b["ten"] for b in kk.ds_khuon(True)]
    tap = {t: k for k, v in tt.phan_khuon(ten).items() for t in v}
    tv = kk.thanh_vien_dot()
    assert set(tv) == {0, 1, 2}
    assert len(tv[1]) == 200 and len(tv[2]) == 200
    for d, ten_dot in tv.items():
        dem = collections.Counter(tap[t] for t in ten_dot)
        mong = max(1, round(0.10 * len(ten_dot)))
        assert dem["phat_trien"] == mong and dem["kiem_tra_cuoi"] == mong, (d, dem)


def test_tap_cua_khuon_khong_phu_thuoc_bo_ten_truyen_vao():
    """Truyen 200, 270, 400, 500, 600 hay 657 ten thi tap cua mot khuon van nhu nhau; neu khong
    bang tap cua bo sinh va buoc `chia` (chi truyen khuon CO MAT trong ca) se lech nhau."""
    ten = [b["ten"] for b in kk.ds_khuon(True)]
    day_du = {t: k for k, v in tt.phan_khuon(ten).items() for t in v}
    for n in (200, 270, 400, 500, 600):
        con = {t: k for k, v in tt.phan_khuon(ten[:n]).items() for t in v}
        assert [t for t in ten[:n] if con[t] != day_du[t]] == [], n


def test_loc_gioi_khuon_mo_rong_chi_nu_khong_ra_cho_nam():
    from src.bo_du_lieu import khuon_mo_rong as kmr
    assert kmr.CHI_NU_MO_RONG, "kho mo rong khong co khuon chi nu"
    ten_nu = next(iter(kmr.CHI_NU_MO_RONG))
    assert sh._hop_gioi(ten_nu, "mẹ") is True
    assert sh._hop_gioi(ten_nu, "bố") is False
    ten_nam = next(iter(kmr.CHI_NAM_MO_RONG))
    assert sh._hop_gioi(ten_nam, "bố") is True
    assert sh._hop_gioi(ten_nam, "mẹ") is False


def test_sinh_bo_mo_rong_dung_khuon_ngoai_nl_va_khong_loi_tra_bang_tap():
    bo = sh.sinh_bo(400, seed=7, mo_rong=True)
    ten_nl = {b["ten"] for b in nl.BENH}
    ngoai_nl = [c for c in bo if c["benh"] not in ten_nl]
    assert len(ngoai_nl) > 50, "bo sinh khong dung khuon cua khuon_mo_rong"
