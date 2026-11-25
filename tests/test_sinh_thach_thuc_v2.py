# -*- coding: utf-8 -*-
"""Bo thu thach v2: chi khuon CHUA NHIN (ngoai 200 khuon goc), chi tap phat trien."""
import re

import pytest

from src import kho_khuon
from src import sinh_hoi_thoai_viet as sh
from tools import sinh_thach_thuc_v2 as v2

SO = 4  # so ca moi bo trong phep thu (nho cho nhanh)


@pytest.fixture(scope="module")
def bo():
    return v2.sinh_tat_ca(so_ca=SO, seed=7)


def _luot(ca):
    return [d for d in ca["input"].split("\n") if d.strip()]


def test_du_sau_bo_dung_so_ca(bo):
    assert set(bo) == set(v2.CAC_BO)
    assert all(len(ds) == SO for ds in bo.values())


def test_khong_dung_khuon_train_hay_khuon_goc(bo):
    goc = {b["ten"] for b in kho_khuon._goc()}
    bang = sh.bang_tap_khuon(mo_rong=True)
    for ds in bo.values():
        for ca in ds:
            assert bang[ca["benh"]] == "phat_trien", ca["id"]
            assert ca["benh"] not in goc, ca["id"]


def test_tra_loi_ngan_co_cap(bo):
    for ca in bo["tra_loi_ngan"]:
        L = _luot(ca)
        duoc_dan = {x for m in ca["dap_an"] for x in (m.get("luot") or [])}
        cap = 0
        for i in range(1, len(L)):
            v0, _, t0 = L[i - 1].partition(": ")
            v1, _, t1 = L[i].partition(": ")
            if (v0 == "Bác sĩ" and t0.rstrip().endswith("?") and v1 != "Bác sĩ"
                    and len(t1.split()) <= 3 and (i + 1) in duoc_dan):
                cap += 1
        assert cap >= 3, ca["id"]


def test_tra_loi_ngan_trich_dan_van_la_chuoi_con(bo):
    for ca in bo["tra_loi_ngan"]:
        L = _luot(ca)
        for m in ca["dap_an"]:
            than = " ".join(L[j - 1] for j in m.get("luot") or [])
            for t in m.get("trich_dan") or []:
                assert t.rstrip(".") in than, (ca["id"], t)


def test_khong_dau_cau(bo):
    b = [ca for ca in bo["khong_dau_cau"] if ca["bien_the"] == "B"]
    assert b
    for ca in b:
        than = "\n".join(d.partition(": ")[2] for d in _luot(ca))
        than = re.sub(r"\d[.,]\d", "", than)  # 38,5 giu dau phay
        assert not re.search(r"[.,?!]", than), ca["id"]
        assert than == than.lower(), ca["id"]


def test_khong_dau_cau_giu_dap_an(bo):
    ds = bo["khong_dau_cau"]
    for a, b in zip(ds[::2], ds[1::2]):
        assert v2.bo_trich_dan(a["dap_an"]) == v2.bo_trich_dan(b["dap_an"])
        L = _luot(b)
        for m in b["dap_an"]:
            than = " ".join(L[j - 1] for j in m.get("luot") or [])
            for t in m.get("trich_dan") or []:
                assert t in than, (b["id"], t)


def test_tat_dinh(bo):
    lai = v2.sinh_tat_ca(so_ca=SO, seed=7)
    assert [c["input"] for c in lai["tra_loi_ngan"]] == [c["input"] for c in bo["tra_loi_ngan"]]
