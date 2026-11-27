# -*- coding: utf-8 -*-
"""Bo do cay loi (plan 2026-11-25-cay-loi-do-canh-bao, Task 3). gop.chay duoc thay bang ban gia
de kiem cach dem, khong kiem luat."""
import json
from types import SimpleNamespace as NS

import pytest

from src.do_luong import do_cay_loi as do_cay_loi
from src.canh_bao import gop
from src.canh_bao.loai import LOAI
from tests.test_cay_loi import CA
from tools import cay_loi


def _cb(ma, luot=()):
    return NS(ma=ma, nhom=LOAI[ma].nhom, luot=list(luot))


def _gia(ps, hoi_thoai, *a, **k):
    """Bao NEGATION_FLIP cho moi dong phu dinh; bao OMITTED_ALLERGY o luot 6 khi khong dong nao
    nhac penicillin; dong phu dinh -> can xac nhan."""
    theo = {p.id: {"tat_ca": [_cb("NEGATION_FLIP", p.bang_chung)] if p.phu_dinh else []} for p in ps}
    toan = [] if any("penicillin" in p.noi_dung for p in ps) else [_cb("OMITTED_ALLERGY", [6])]
    tt = {p.id: {"trang_thai": gop.CAN_XAC_NHAN if p.phu_dinh else gop.DA_KIEM_CHUNG} for p in ps}
    return {"theo_phat_bieu": theo, "toan_ca": toan, "trang_thai_D": tt}


@pytest.fixture
def ket(monkeypatch):
    monkeypatch.setattr(gop, "chay", _gia)
    return do_cay_loi.do([CA], seed=3)


def test_ban_sach_moi_canh_bao_la_bao_nham(ket):
    s = ket["sach"]
    assert s["so_ca"] == 1 and s["bao_nham_moi_ca"] == 1.0 and s["theo_ma"] == {"NEGATION_FLIP": 1}
    # dong phu dinh "không ho" vao than va bi dua sang can xac nhan
    assert s["chan_thua_D"] == pytest.approx(1 / 5, abs=1e-3)


def test_dao_phu_dinh_dem_theo_dong_bi_cay(ket):
    r = cay_loi.cay(do_cay_loi._ps(CA), CA, "dao_phu_dinh", do_cay_loi._rng(3, CA["id"], "dao_phu_dinh"))
    moi, c = r
    bat = next(p for p in moi if p.id == c.phat_bieu_id).phu_dinh
    t = ket["theo_loai"]["dao_phu_dinh"]
    assert t["so_lan"] == 1 and t["bat_dung_loai"] == int(bat) and t["d_can_xac_nhan"] == int(bat)


def test_bo_sot_dem_theo_giao_luot(ket):
    assert ket["theo_loai"]["xoa_di_ung"]["bat_dung_loai"] == 1
    assert ket["theo_loai"]["xoa_thuoc"]["bat_dung_loai"] == 0
    assert ket["theo_loai"]["xoa_thuoc"]["bat_bat_ky"] == 0
    # luot 8 cua dong thuoc khong con ai dan; luot [2,9] cua "sốt 39 độ" van con dong bi thay the dan
    assert ket["theo_loai"]["xoa_thuoc"]["luot_con_duoc_dan"] == 0


def test_khong_ap_dung_va_wilson(ket):
    t = ket["theo_loai"]["xoa_di_ung"]
    assert t["khong_ap_dung"] == 0 and t["wilson"][0] < 1 <= t["wilson"][1] + 1e-9


def test_precision_trong_luot_cay(ket):
    # NEGATION_FLIP ban o moi luot cay co dong phu dinh; chi dung khi nam tren dong bi cay
    # va loai cay nhan NEGATION_ASSERTION
    m = ket["theo_ma_trong_cay"]["NEGATION_FLIP"]
    assert 0 < m["so_lan_bao"] and 0 <= m["chinh_xac"] < 1


def test_cung_hat_cung_ket_qua(monkeypatch):
    monkeypatch.setattr(gop, "chay", _gia)
    a = json.dumps(do_cay_loi.do([CA], seed=5), sort_keys=True)
    b = json.dumps(do_cay_loi.do([CA], seed=5), sort_keys=True)
    assert a == b


def test_giu_kin_doi_co_khoa_luat():
    with pytest.raises(SystemExit):
        do_cay_loi.main(["--tap", "giu_kin", "--ra-json", "x.json"])


def test_do_loi_kho_dung_bang_nhom_kho(monkeypatch):
    from tests.test_cay_loi_kho import CA as CA_KHO
    from tools import cay_loi_kho
    monkeypatch.setattr(gop, "chay", _gia)
    r = do_cay_loi.do([CA_KHO], seed=1, kho=True)
    assert set(r["theo_loai"]) == set(cay_loi_kho.LOAI_KHO)
    # _gia chi bao NEGATION_FLIP tren dong phu dinh: bia_phu_dinh (dong moi phu dinh) bi "bat" nhung sai nhom
    t = r["theo_loai"]["bia_phu_dinh"]
    assert t["so_lan"] == 1 and t["bat_bat_ky"] == 1 and t["bat_dung_loai"] == 0
