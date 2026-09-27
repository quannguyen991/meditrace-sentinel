# -*- coding: utf-8 -*-
"""Canh bon chi so mau-so-khong-phu-thuoc-he-thong them ngay 20/09/2026.

Cai chung vá: moi ty le loi cu deu chia cho mot mau so do CHINH he thong quyet
dinh, nen he thong viet it thi ty le dep. Do duoc 19/09: duong tat bang luat dat
13,1% sai chu the — thap hon moi nhanh co mo hinh — nhung bo sot 51,3% thong tin.
"""
from collections import Counter

import pytest

from src import cham_he_thong as ch


def _dem(so_than, so_dap_an, so_dung, so_ghep, chen, bo_sot):
    """Dung lai dung cac phep tinh cuoi `cham_ca`, khong goi lai ca ham."""
    k = Counter(so_than=so_than, so_dap_an_than=so_dap_an, so_dung=so_dung,
                so_ghep=so_ghep, chen=chen, bo_sot=bo_sot)
    k["f1_tu"] = 2 * k["so_dung"]
    k["f1_mau"] = k["so_than"] + k["so_dap_an_than"]
    k["ser_tu"] = (k["so_ghep"] - k["so_dung"]) + k["bo_sot"] + k["chen"]
    return k


def test_he_thong_hoan_hao():
    """Viet dung het, khong thua khong thieu -> P = R = F1 = 1, SER = 0."""
    k = _dem(so_than=10, so_dap_an=10, so_dung=10, so_ghep=10, chen=0, bo_sot=0)
    assert k["so_dung"] / k["so_than"] == 1.0
    assert k["so_dung"] / k["so_dap_an_than"] == 1.0
    assert k["f1_tu"] / k["f1_mau"] == 1.0
    assert k["ser_tu"] / k["so_dap_an_than"] == 0.0


def test_he_thong_viet_it_khong_con_duoc_diem_dep():
    """Day la chinh cai bay ma bon chi so nay de vá.

    He thong A viet 2 menh de, ca 2 dung. Ty le loi cu cua no = 0%.
    He thong B viet 10 menh de, 8 dung. Ty le loi cu = 20%, trong TE hon.
    Nhung dap an co 10 o: A bo sot 8, B bo sot 2.
    """
    a = _dem(so_than=2, so_dap_an=10, so_dung=2, so_ghep=2, chen=0, bo_sot=8)
    b = _dem(so_than=10, so_dap_an=10, so_dung=8, so_ghep=10, chen=0, bo_sot=2)

    # Theo do chinh xac don thuan thi A "hon" B
    assert a["so_dung"] / a["so_than"] > b["so_dung"] / b["so_than"]
    # Nhung F1 va SER phai xep B tren A
    assert a["f1_tu"] / a["f1_mau"] < b["f1_tu"] / b["f1_mau"]
    assert a["ser_tu"] / a["so_dap_an_than"] > b["ser_tu"] / b["so_dap_an_than"]


def test_ser_vuot_mot_khi_chen_qua_nhieu():
    """SER > 1 la hop le: he thong chen them nhieu hon so o co that."""
    k = _dem(so_than=30, so_dap_an=10, so_dung=5, so_ghep=6, chen=24, bo_sot=5)
    assert k["ser_tu"] / k["so_dap_an_than"] > 1.0


def test_f1_khop_trung_binh_dieu_hoa():
    """F1 viet duoi dang mot ty so duy nhat phai bang 2PR/(P+R)."""
    k = _dem(so_than=13, so_dap_an=17, so_dung=9, so_ghep=11, chen=2, bo_sot=8)
    p = k["so_dung"] / k["so_than"]
    r = k["so_dung"] / k["so_dap_an_than"]
    assert k["f1_tu"] / k["f1_mau"] == pytest.approx(2 * p * r / (p + r))


def test_bang_co_du_bon_chi_so():
    ten = {t for t, _tu, _mau in ch.BANG}
    assert {"do_chinh_xac", "do_phu", "f1", "ser", "sai_chu_the_tren_gold"} <= ten


def test_mau_so_khong_phu_thuoc_he_thong():
    """`do_phu`, `ser`, `sai_chu_the_tren_gold` PHAI chia cho so o dap an.

    Neu ai do doi sang `so_than` thi ca ba lai tro thanh diem dep cho he thong
    viet it — dung cai bay dang vá."""
    mau = {t: m for t, _tu, m in ch.BANG}
    assert mau["do_phu"] == "so_dap_an_than"
    assert mau["ser"] == "so_dap_an_than"
    assert mau["sai_chu_the_tren_gold"] == "so_dap_an_than"
