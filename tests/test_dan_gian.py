# -*- coding: utf-8 -*-
"""Bat bien cua bo thu thach dan gian (src/dan_gian.py, thach_thuc.cap_dan_gian)."""
import json
import re

import pytest

from src import chuan_hoa, dan_gian, duong_dan, thach_thuc


@pytest.fixture(scope="module")
def cap():
    return thach_thuc.cap_dan_gian("phat_trien", 6, seed=7)


def _luot(input_):
    return [d for d in input_.split("\n") if d.strip()]


def test_hai_ban_chi_khac_trich_dan(cap):
    for a, b in zip(cap[::2], cap[1::2]):
        assert thach_thuc.bo_trich_dan(a["dap_an"]) == thach_thuc.bo_trich_dan(b["dap_an"])
        assert a["output"] == b["output"]
        assert len(_luot(a["input"])) == len(_luot(b["input"]))


def test_trich_dan_ban_B_nam_nguyen_van_trong_hoi_thoai(cap):
    for b in cap[1::2]:
        luot = _luot(b["input"])
        for d in b["dap_an"]:
            for t in d.get("trich_dan") or []:
                assert any(t in l for l in luot), (b["id"], t)


def test_khong_doi_loi_bac_si(cap):
    for a, b in zip(cap[::2], cap[1::2]):
        for x, y in zip(_luot(a["input"]), _luot(b["input"])):
            if x.split(":", 1)[0].strip().lower().split(" ", 1)[-1].startswith("bác sĩ") \
                    or re.match(r"\s*(\d+\s+)?bác sĩ", x.lower()):
                assert x == y


def test_moi_cap_co_it_nhat_hai_cho_doi_va_dung_phan_bo(cap):
    for i, b in enumerate(cap[1::2]):
        cho = b["cho_dan_gian"]
        assert len(cho) >= 2
        if i % 3 == 0:
            assert any(c["loai"] == dan_gian.MO_HO for c in cho)
        if i % 3 == 2:
            assert any(c["loai"] == "chen" for c in cho)


def test_giu_tu_ghep():
    assert dan_gian.doi_cau("nôn nao")[0] == "nôn nao"
    assert dan_gian.doi_cau("mệt mỏi")[0] == "mệt mỏi"
    assert dan_gian.doi_cau("ho khan")[0] == "ho khan"
    assert dan_gian.doi_cau("cho cháu")[0] == "cho cháu"


def test_trich_dan_theo_ngu_canh_luot():
    # "nôn" cuoi doan trich, ngay sau la "nao" trong luot: luot KHONG doi, trich dan
    # cung khong duoc doi.
    input_ = "1 Bác sĩ: Sao em?\n2 Bệnh nhân: Em buồn nôn nao cả người."
    moi, _ = dan_gian.doi_hoi_thoai(input_)
    da = dan_gian.doi_trich_dan([{"trich_dan": ["Em buồn nôn"]}], input_)
    assert da[0]["trich_dan"][0] in moi


def test_duong_ong_khong_biet_cum_giu_lai():
    for dg, chuan in dan_gian.muc_chuan_hoa(True):
        m = next(x for x in dan_gian.BANG if x.dan_gian == dg)
        if m.trong_bang:
            assert chuan_hoa.chuan_hoa(dg) == chuan.lower()
        else:
            assert chuan_hoa.chuan_hoa(dg) == dg.lower()
            assert chuan_hoa.chuan_hoa(dg, gom_giu_lai=True) == chuan.lower()


def test_cum_mo_ho_khong_vao_bang_chuan_hoa():
    mo_ho = {m.dan_gian for m in dan_gian.BANG if m.loai == dan_gian.MO_HO}
    assert not mo_ho & {dg for dg, _ in dan_gian.muc_chuan_hoa(True)}


def test_cum_dan_gian_khong_co_trong_du_lieu_the_he_8():
    """Them cum vao bang chuan hoa khong duoc doi so da bao cao: khong cum nao duoc
    xuat hien trong hoi thoai, dap an hay dau ra cua the he 8."""
    tep = [duong_dan.THU_MUC_DU_LIEU / "hoi_thoai_viet_5000_th8.jsonl"]
    tep += sorted(duong_dan.THU_MUC_DU_LIEU.glob("thach_thuc_*_phat_trien.jsonl"))
    tep += sorted((duong_dan.GOC_DU_AN / "kaggle-ra" / "the-he-8").glob("ra_*.jsonl"))
    tep = [t for t in tep if t.exists() and "dan_gian" not in t.name]
    if not tep:
        pytest.skip("khong co du lieu the he 8 tren may nay")
    mau = re.compile("|".join(rf"(?<![\wÀ-ỹ]){re.escape(dg)}(?![\wÀ-ỹ])"
                              for dg, _ in dan_gian.muc_chuan_hoa(True)), re.I)
    for t in tep:
        van = t.read_text(encoding="utf-8")
        assert not mau.search(van), (t.name, mau.search(van).group(0))
