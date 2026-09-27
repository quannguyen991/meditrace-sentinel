# -*- coding: utf-8 -*-
"""Nua thu hai cua thach thuc 4 — DAN DUNG luot thoai nguon.

VI SAO CO TEP NAY (10/09/2026).

Thach thuc 4 ten day du la "lien ket chu the va can cu bang chung", va no gom
HAI viec khac nhau:

    gan dung nguoi   thong tin nay thuoc ve ai
    dan dung nguon   thong tin nay dua vao cau nao

Truoc hom nay `do_trich` chi do viec dau. Mot he thong co the gan DUNG nguoi
ma DAN SAI luot thoai, va khong phep do nao cua du an bat duoc — trong khi
"truy vet bang chung" la chinh dieu du an dat ten.
"""
import pytest

from src import do_trich as dt


def _cap(luot_that, luot_doan, noi_dung="sốt"):
    """Mot cap (dap an, ban trich, diem giong) nhu `ghep` tra ve."""
    return ({"chu_the": "bệnh nhân", "noi_dung": noi_dung, "luot": luot_that},
            {"chu_the": "bệnh nhân", "noi_dung": noi_dung,
             "luot_thoai": luot_doan},
            1.0)


def test_dan_dung_het_thi_hoan_hao():
    k = dt.cham_can_cu([_cap([1, 2], [1, 2])])
    assert k["do_phu"] == 1.0 and k["do_chuan"] == 1.0
    assert k["ty_le_khop_hoan_toan"] == 1.0


def test_dan_thieu_mot_luot():
    """Cap hoi-dap can CA HAI luot moi du nghia. Dan mot luot la mat can cu."""
    k = dt.cham_can_cu([_cap([1, 2], [2])])
    assert k["luot_dung"] == 1 and k["luot_sot"] == 1
    assert k["do_phu"] == 0.5
    assert k["do_chuan"] == 1.0          # khong dan thua
    assert k["khop_hoan_toan"] == 0


def test_dan_thua_mot_luot():
    k = dt.cham_can_cu([_cap([1], [1, 5])])
    assert k["luot_thua"] == 1
    assert k["do_phu"] == 1.0
    assert k["do_chuan"] == 0.5


def test_dan_sai_hoan_toan():
    k = dt.cham_can_cu([_cap([1, 2], [7, 8])])
    assert k["luot_dung"] == 0
    assert k["do_phu"] == 0.0 and k["do_chuan"] == 0.0


def test_gan_dung_nguoi_nhung_dan_sai_nguon_van_bi_bat():
    """Day la truong hop chinh ma phep do nay ton tai de bat: chu the dung,
    can cu sai. Phep do cu cho diem tuyet doi."""
    cap = [_cap([3, 4], [1, 2])]
    assert dt.cham_can_cu(cap)["do_phu"] == 0.0
    # nhung chu the thi van dung
    d, t, _ = cap[0]
    assert dt.cung_nguoi(d["chu_the"], t["chu_the"])


def test_tinh_theo_TUNG_menh_de_khong_gop_chung():
    """Mot menh de dan dung 2/2 va mot menh de dan sai 2/2 phai thay duoc ca
    hai, khong bi mot ty le gop lam mo mat."""
    k = dt.cham_can_cu([_cap([1, 2], [1, 2]), _cap([3, 4], [8, 9], "ho")])
    assert k["so_menh_de_xet"] == 2
    assert k["khop_hoan_toan"] == 1
    assert k["ty_le_khop_hoan_toan"] == 0.5
    assert k["do_phu"] == 0.5


def test_dap_an_khong_co_luot_thi_bo_qua():
    """Khong do duoc thi khong dem, chu khong tinh la sai — dem la sai se phat
    oan mot he thong dung tren mot dap an thieu."""
    k = dt.cham_can_cu([({"chu_the": "bệnh nhân", "noi_dung": "sốt"},
                         {"chu_the": "bệnh nhân", "noi_dung": "sốt",
                          "luot_thoai": [1]}, 1.0)])
    assert k["so_menh_de_xet"] == 0


def test_ban_trich_khong_dan_gi_thi_tinh_la_sot_het():
    k = dt.cham_can_cu([_cap([1, 2], [])])
    assert k["luot_sot"] == 2 and k["luot_dung"] == 0
    assert k["do_phu"] == 0.0


def test_nhan_ca_hai_ten_khoa():
    """Dap an dung khoa `luot`, ban trich dung `luot_thoai`. Doc nham mot ben
    se cho ra 0 ma khong bao gi."""
    a = ({"chu_the": "bệnh nhân", "noi_dung": "sốt", "luot": [1, 2]},
         {"chu_the": "bệnh nhân", "noi_dung": "sốt", "luot_thoai": [1, 2]}, 1.0)
    assert dt.cham_can_cu([a])["do_phu"] == 1.0


def test_cham_gan_ket_qua_can_cu_vao_bang_chinh():
    """`cham` phai tra ve luon so can cu, khong de nguoi goi tu ghep."""
    dap_an = [{"chu_the": "bệnh nhân", "noi_dung": "sốt", "luot": [1, 2]}]
    trich = [{"chu_the": "bệnh nhân", "noi_dung": "sốt", "luot_thoai": [1, 2]}]
    k = dt.cham([(dap_an, trich)])
    assert "can_cu" in k
    assert k["can_cu"]["do_phu"] == 1.0


def test_khong_co_cap_nao_thi_khong_chia_cho_khong():
    k = dt.cham_can_cu([])
    assert k["so_menh_de_xet"] == 0
    assert k["do_phu"] == 0.0 and k["do_chuan"] == 0.0
