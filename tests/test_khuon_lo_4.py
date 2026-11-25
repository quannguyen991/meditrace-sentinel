# -*- coding: utf-8 -*-
"""Kiem thu khuon benh Lo 4 (50 khuon: 351-400 tu DANH_SACH_UNG_VIEN_CON_LAI[50:100])."""
import re
import pytest

from src import kiem_khuon as kk
from src import ngu_lieu_viet as nl
from src import khuon_mo_rong as kmr
from src import khuon_lo_4 as kl4
from src import dan_gian


def test_lo_4_du_50_khuon():
    assert len(kl4.BENH_LO_4) == 50


def test_lo_4_khop_ung_vien_50_den_100():
    cands = kmr.DANH_SACH_UNG_VIEN_CON_LAI[50:100]
    assert len(cands) == 50
    for b, c in zip(kl4.BENH_LO_4, cands):
        assert b["ten"] == c[0]
        assert b["nhom"] == c[1]
        assert b["dien_tien"] == c[2]
        assert b["he_co_quan"] == c[3]


def test_du_truong_bat_buoc_moi_khuon_lo_4():
    truong_yeu_cau = (
        "ten", "nhom", "dien_tien", "chinh", "phu", "kham",
        "chan_doan", "ke_hoach", "he_co_quan", "da_duyet",
        "bien_the_kham", "bien_the_chan_doan", "bien_the_ke_hoach"
    )
    for b in kl4.BENH_LO_4:
        for k in truong_yeu_cau:
            assert k in b, f"Khuon '{b.get('ten')}' thieu truong '{k}'"
            if k != "da_duyet":
                assert b[k], f"Khuon '{b['ten']}' co truong '{k}' rong"
        assert isinstance(b["chinh"], list) and len(b["chinh"]) >= 3
        assert isinstance(b["phu"], list) and len(b["phu"]) >= 3
        assert b["da_duyet"] is False


def test_bien_the_it_nhat_6_cach_mo_ta_lo_4():
    for b in kl4.BENH_LO_4:
        for k in ("bien_the_kham", "bien_the_chan_doan", "bien_the_ke_hoach"):
            ds = b[k]
            assert isinstance(ds, list), f"'{k}' cua '{b['ten']}' khong phai list"
            assert len(ds) >= 6, f"'{k}' cua '{b['ten']}' chi co {len(ds)} bien the (< 6)"
            assert len(set(ds)) == len(ds), f"'{k}' cua '{b['ten']}' co bien the trung lap"
        assert b["kham"] == b["bien_the_kham"][0]
        assert b["chan_doan"] == b["bien_the_chan_doan"][0]
        assert b["ke_hoach"] == b["bien_the_ke_hoach"][0]


def test_kiem_khuon_lo_4_khong_loi_khong_trung():
    ket = kk.kiem_tat_ca(
        kl4.BENH_LO_4,
        kl4.CHI_NU_LO_4,
        kl4.CHI_NAM_LO_4,
        kl4.GIOI_TINH_LO_4
    )
    loi = [v for v in ket.van_de if v.muc == "LOI"]
    assert not loi, f"Co loi trong kiem_khuon Lo 4: {loi}"
    assert len(ket.cap_trung) == 0, f"Co cap trung lap >= 20% trong Lo 4: {ket.cap_trung}"
    assert ket.dat is True


def test_khong_trung_lap_voi_300_khuon_cu():
    cac_khuon_hien_tai = [b for b in list(getattr(nl, "BENH_GOC", nl.BENH[:200])) + list(kmr.BENH_MO_RONG)
                          if b["ten"] not in {x["ten"] for x in kl4.BENH_LO_4}]
    tu_cu = {kk._chuan(b["ten"]): kk._tu_khoa([*b.get("chinh", []), *b.get("phu", [])]) for b in cac_khuon_hien_tai}
    tu_moi = {kk._chuan(b["ten"]): kk._tu_khoa([*b.get("chinh", []), *b.get("phu", [])]) for b in kl4.BENH_LO_4}

    trung_cu = []
    for ten_moi, s_moi in tu_moi.items():
        for ten_cu, s_cu in tu_cu.items():
            j = kk._jaccard(s_moi, s_cu)
            if j >= 0.20:
                trung_cu.append((ten_moi, ten_cu, round(j, 3)))
    assert len(trung_cu) == 0, f"Co cap trung lap >= 20% voi 300 khuon cu: {trung_cu}"


def test_tuyet_doi_khong_chua_tu_cam_va_om_lo_4():
    import inspect
    raw_code = inspect.getsource(kl4)
    assert "ốm" not in raw_code.lower(), "Tep src/khuon_lo_4.py chua chuoi con 'om'"
    mau = re.compile("|".join(re.escape(m.dan_gian) for m in dan_gian.BANG if m.loai == dan_gian.MO_HO), re.I)
    assert not mau.search(raw_code), f"Tep src/khuon_lo_4.py chua cum mo ho: {mau.search(raw_code).group(0)}"
