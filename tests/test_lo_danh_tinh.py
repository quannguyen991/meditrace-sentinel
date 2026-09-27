# -*- coding: utf-8 -*-
"""Bo sinh khong duoc ro danh tinh nguoi nha vao dap an.

Bat bien: quan he GHI DICH DANH trong dap an <=> quan he CO trong loi thoai.
Truoc 15/09/2026 bo sinh ghi thang quan he that tu trang thai an — 18,1% menh de
gan cho nguoi ke tren tap train khong co manh moi nao trong hoi thoai.
"""
import random

import pytest

from src import sinh_hoi_thoai_viet as sh

KHONG_DICH_DANH = {"bệnh nhân", "người nhà"}


@pytest.fixture(scope="module")
def bo():
    return sh.sinh_bo(400, seed=11)


def test_moi_quan_he_ghi_dich_danh_deu_co_trong_loi_thoai(bo):
    """Mot ten nguoi trong dap an ma khong co trong hoi thoai la thong tin bia."""
    vi_pham = []
    for c in bo:
        hoi = c["input"].lower()
        for d in c["dap_an"]:
            ten = d["chu_the"].lower()
            if ten not in KHONG_DICH_DANH and ten not in hoi:
                vi_pham.append((c["id"], ten))
    assert not vi_pham, vi_pham[:5]


def test_khong_lo_danh_tinh_thi_ghi_nguoi_nha(bo):
    co = [c for c in bo if c["nguoi_ke"] and not c["lo_danh_tinh"]
          and any(d["chu_the"] == "người nhà" for d in c["dap_an"])]
    assert co, "phai co ca khong lo danh tinh ma van co thong tin cua nguoi ke"


def test_lo_danh_tinh_thi_loi_thoai_noi_ro_quan_he(bo):
    co = [c for c in bo if c["nguoi_ke"] and c["lo_danh_tinh"]]
    assert co
    for c in co:
        assert f"là {c['nguoi_ke']} của" in c["input"], c["id"]


def test_ty_le_lo_danh_tinh_gan_hang_so(bo):
    co_nn = [c for c in bo if c["nguoi_ke"]]
    ty_le = sum(c["lo_danh_tinh"] for c in co_nn) / len(co_nn)
    assert abs(ty_le - sh.TY_LE_LO_DANH_TINH) < 0.12, ty_le


def test_ca_khong_co_nguoi_nha_thi_khong_lo_gi(bo):
    assert all(not c["lo_danh_tinh"] for c in bo if not c["nguoi_ke"])
