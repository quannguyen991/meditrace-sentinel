# -*- coding: utf-8 -*-
import pytest

from src.do_bo_sot import ti_le_bo_sot


def _md(noi_dung, nhom=None):
    d = {"noi_dung": noi_dung}
    if nhom:
        d["nhom_loi"] = nhom
    return d


def test_khong_bo_sot():
    da = [_md("ho ba ngày"), _md("sốt nhẹ")]
    r = ti_le_bo_sot([(da, [dict(x) for x in da])])
    assert r["ti_le_bo_sot"] == 0.0
    assert r["so_menh_de_dap_an"] == 2 and r["so_bo_sot"] == 0


def test_bo_sot_mot_nua():
    da = [_md("ho ba ngày"), _md("dị ứng penicillin")]
    r = ti_le_bo_sot([(da, [_md("ho ba ngày")])])
    assert r["so_bo_sot"] == 1
    assert r["ti_le_bo_sot"] == 0.5


def test_nguong_ghep_anh_huong():
    da = [_md("ho kéo dài ba ngày nay")]
    trich = [_md("ho ba ngày")]
    chat = ti_le_bo_sot([(da, trich)], nguong=0.9)["ti_le_bo_sot"]
    long_ = ti_le_bo_sot([(da, trich)], nguong=0.3)["ti_le_bo_sot"]
    assert chat > long_


def test_ca_rong_khong_chia_cho_0():
    r = ti_le_bo_sot([])
    assert r["ti_le_bo_sot"] == 0.0 and r["so_menh_de_dap_an"] == 0


def test_ca_khong_co_dap_an():
    r = ti_le_bo_sot([([], [_md("ho")])])
    assert r["so_menh_de_dap_an"] == 0 and r["ti_le_bo_sot"] == 0.0


def test_theo_nhom():
    da = [_md("dị ứng penicillin", "chu_the"), _md("ho ba ngày", "chu_the"),
          _md("sốt nhẹ")]
    trich = [_md("ho ba ngày")]
    r = ti_le_bo_sot([(da, trich)])
    assert r["theo_nhom"]["chu_the"] == {"so_menh_de": 2, "so_bo_sot": 1, "ti_le": 0.5}
    assert r["theo_nhom"]["khac"] == {"so_menh_de": 1, "so_bo_sot": 1, "ti_le": 1.0}


def test_trich_none_coi_nhu_rong():
    da = [_md("ho")]
    r = ti_le_bo_sot([(da, None)])
    assert r["so_bo_sot"] == 1
