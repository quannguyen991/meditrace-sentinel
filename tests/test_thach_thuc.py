# -*- coding: utf-8 -*-
"""Bo thach thuc: hai ban cua mot cap chi khac DUNG dieu dang do.

Neu hai ban khac nhau o nhieu cho hon the, mot he thong co the dung o ca hai
vi mot ly do khong lien quan — va con so "doi dung ca hai" mat nghia.
"""
import pytest

from src import sinh_hoi_thoai_viet as sh
from src import thach_thuc as tt


@pytest.fixture(scope="module")
def dct():
    return tt.cap_doi_chu_the("phat_trien", 6, seed=3)


@pytest.fixture(scope="module")
def png():
    return tt.cap_phuong_ngu("phat_trien", 6, seed=3)


def _cap(ds):
    theo = {}
    for x in ds:
        theo.setdefault(x["cap"], {})[x["bien_the"]] = x
    return theo


def test_doi_chu_the_hai_ban_chi_khac_MOT_luot(dct):
    for c in _cap(dct).values():
        la = c["A"]["input"].split("\n")
        lb = c["B"]["input"].split("\n")
        assert len(la) == len(lb)
        assert sum(x != y for x, y in zip(la, lb)) == 1


def test_doi_chu_the_dap_an_DAO_nguoi_mang_di_ung(dct):
    """Ban A: nguoi nha di ung X, benh nhan chua ghi nhan. Ban B: benh nhan di
    ung X, chac chan. Cung mot X."""
    for c in _cap(dct).values():
        a, b = c["A"], c["B"]
        cua_nguoi_nha = [d for d in a["dap_an"]
                         if d["noi_dung"].startswith("dị ứng ")
                         and d["chu_the"] != "bệnh nhân"]
        assert len(cua_nguoi_nha) == 1, a["id"]
        x = cua_nguoi_nha[0]["noi_dung"]
        cua_bn = [d for d in b["dap_an"] if d["noi_dung"] == x]
        assert len(cua_bn) == 1, b["id"]
        assert cua_bn[0]["chu_the"] == "bệnh nhân"
        assert cua_bn[0]["do_chac_chan"] == "chắc chắn"
        assert not cua_bn[0]["phu_dinh"]


def test_doi_chu_the_chi_rut_khuon_cua_tap(dct):
    bang = sh.bang_tap_khuon()
    assert all(bang[x["benh"]] == "phat_trien" for x in dct)


def test_phuong_ngu_hai_ban_CUNG_dap_an_tru_trich_dan(png):
    for c in _cap(png).values():
        assert c["A"]["tu_phuong_ngu"] and not c["B"]["tu_phuong_ngu"]
        assert tt._so_cap_phuong_ngu(c["A"]["dap_an"]) == \
            tt._so_cap_phuong_ngu(c["B"]["dap_an"])
        assert c["A"]["input"] != c["B"]["input"]


def test_phuong_ngu_hai_ban_chi_khac_noi_dung_o_cum_GIU_NGUYEN():
    """Tu 24/09/2026 ban A noi "nong ham hap" thi dap an A ghi dung cum do, ban B
    ghi "sot". Cho khac duy nhat phai la DUNG truong noi_dung, DUNG cum do — neu
    khong thi `_so_cap_phuong_ngu` dang che mot khac biet khac.

    Cap 0 cua hat 42 (mien Nam) la cap that trong bo phat trien co cum nay."""
    from src import phuong_ngu as pn
    a, b = tt.cap_phuong_ngu("phat_trien", 1, seed=42)
    khac = [(x["noi_dung"], y["noi_dung"])
            for x, y in zip(tt.bo_trich_dan(a["dap_an"]), tt.bo_trich_dan(b["dap_an"]))
            if x != y]
    assert khac, "cap 0 khong con cum giu nguyen — chon cap khac cho test nay"
    for x, y in khac:
        assert any(g in x for g in pn.GIU_NGUYEN) and pn.ve_tu_chuan(x) == y


def test_dinh_chinh_moi_ca_mang_DUNG_bay_cua_no():
    ds = tt.bo_dinh_chinh("phat_trien", 10, seed=3)
    so = len(tt.BAY_CAP_NHAT)
    assert [x["bay_chinh"] for x in ds] == \
        [tt.BAY_CAP_NHAT[i % so] for i in range(10)]
    assert all(x["bay_chinh"] in x["bay"] for x in ds)


def test_sinh_lai_ra_DUNG_bo_cu():
    assert tt.cap_doi_chu_the("phat_trien", 2, seed=9) == \
        tt.cap_doi_chu_the("phat_trien", 2, seed=9)
