# -*- coding: utf-8 -*-
"""Xung ho trong hoi thoai tu sinh.

Nguoi dung doc mot ca minh hoa ngay 11/09/2026: "sao lai nha em cai gi day, khong
ai noi nhu nay ca". Va dung: "nha em" — cach vo chong goi nhau — roi vao mieng ong
ba, bo me, ca bac si; nguoi xung "toi" goi con la "be nha em"; ba noi goi chau
trai la "anh"; benh nhan vang mat van duoc "kham qua mot chut".
"""
import random
import re

import pytest

from src import ngu_lieu_viet as nl
from src import sinh_hoi_thoai_viet as sh

# Cach NGUOI NHA goi benh nhan, tu goc nhin cua ho — bac si khong bao gio noi.
SO_HUU_NGUOI_NHA = re.compile(
    r"(?<!\w)((bé|cháu|con) nhà (em|tôi)|nhà (em|tôi)|cháu tôi|con (em|tôi)"
    r"|(chồng|vợ|bố|mẹ) (em|tôi|cháu))(?!\w)")


@pytest.fixture(scope="module")
def bo():
    return sh.sinh_bo(600, seed=7)


def _luot(ca):
    for d in ca["input"].split("\n"):
        vai, _, noi = d.partition(": ")
        yield vai, noi


def _cac_ca(n=3000, **kw):
    for i in range(n):
        yield sh.sinh_ca(f"x{i}", random.Random(i), **kw)


def test_BAC_SI_khong_bao_gio_dung_cach_goi_cua_nguoi_nha(bo):
    for ca in bo:
        for vai, noi in _luot(ca):
            if vai == "Bác sĩ":
                assert not SO_HUU_NGUOI_NHA.search(noi.lower()), (ca["id"], noi)


def test_nguoi_nha_HOP_lua_tuoi_va_gioi_cua_benh_nhan():
    for ca in _cac_ca(ep_nguoi_ke=True):
        qh = ca.nguoi_ke[3]
        if ca.la_tre_em:
            assert qh in ("mẹ", "bố", "bà nội", "bà ngoại"), qh
            continue
        tuoi = nl.LUA_TUOI_THEO_GOI[ca.goi_bn]
        assert qh not in ("bà nội", "bà ngoại", "ông nội", "ông ngoại"), (ca.goi_bn, qh)
        if qh in ("mẹ", "bố"):
            assert tuoi == "trẻ", (ca.goi_bn, qh)
        if qh in ("con gái", "con trai"):
            assert tuoi != "trẻ", (ca.goi_bn, qh)
        if qh == "vợ":
            assert ca.gioi_bn == "nam", ca.goi_bn
        if qh == "chồng":
            assert ca.gioi_bn == "nữ", ca.goi_bn


def test_khuon_MOT_GIOI_chi_nhan_cach_goi_hop_gioi():
    gap = 0
    for ca in _cac_ca():
        cho = nl.XUNG_HO_THEO_KHUON.get(ca.benh["ten"])
        if cho and not ca.la_tre_em:
            gap += 1
            assert ca.goi_bn in cho, (ca.benh["ten"], ca.goi_bn)
            assert ca.gioi_bn == nl.GIOI_THEO_KHUON[ca.benh["ten"]]
    assert gap > 0


def test_cach_goi_benh_nhan_KHOP_tu_xung_va_quan_he_cua_nguoi_nha():
    """Da xung "toi" thi "chau nha toi", "con toi" — khong bao gio "be nha em".
    "nha em"/"nha toi" tran la cach vo chong goi nhau."""
    for ca in _cac_ca(ep_nguoi_ke=True):
        tx, qh = ca.nguoi_ke[2], ca.nguoi_ke[3]
        for k in range(5):
            ref = sh._cach_goi_bn_trong_loi_nguoi_ke(ca, random.Random(k))
            tu = ref.split()
            if len(tu) >= 2 and tu[-1] in ("em", "tôi", "cháu"):
                assert tu[-1] == tx, (ca.nguoi_ke, ref)
            if re.fullmatch(r"((ông|bà) )?nhà (em|tôi)", ref):
                assert qh in ("vợ", "chồng"), (ca.nguoi_ke, ref)


def test_mot_nguoi_nha_KHONG_xung_hai_kieu(bo):
    """"be nha em ... nen toi di thay" — mot nguoi, hai tu xung."""
    so_huu = re.compile(r"(?<!\w)(?:nhà|con|bố|mẹ|chồng|vợ) (em|tôi|cháu)(?!\w)")
    for ca in bo:
        if not ca["nguoi_ke"]:
            continue
        chu = set()
        for vai, noi in _luot(ca):
            if vai == "Người nhà":
                chu |= set(so_huu.findall(noi.lower()))
        assert len(chu) <= 1, (ca["id"], chu)


def test_benh_nhan_VANG_MAT_thi_khong_kham_va_chan_doan_chi_la_nghi_ngo(bo):
    gap = 0
    for ca in bo:
        if ca["boi_canh"] != "nguoi_nha_thay_mat":
            continue
        gap += 1
        assert not any(d["muc"] == "KHÁM LÂM SÀNG" for d in ca["dap_an"]), ca["id"]
        cd = [d for d in ca["dap_an"] if d["muc"] == "CHẨN ĐOÁN"]
        assert cd and all(d["do_chac_chan"] == "nghi ngờ" for d in cd), ca["id"]
        for vai, noi in _luot(ca):
            if vai == "Bác sĩ":
                assert not re.search(r"khám qua|nằm lên bàn|nghe phổi|để tôi khám cho",
                                     noi), (ca["id"], noi)
    assert gap > 0


def test_KHONG_mo_dau_bang_Da_Vang_khi_noi_tiep_luot_cua_minh(bo):
    for ca in bo:
        truoc = None
        for vai, noi in _luot(ca):
            if vai not in ("Bác sĩ", "Điều dưỡng") and \
                    truoc not in (None, "Bác sĩ", "Điều dưỡng"):
                assert not re.match(r"(Dạ|Vâng)\b", noi), (ca["id"], noi)
            truoc = vai


def test_loi_chao_cuoi_dung_TU_XUNG_cua_chinh_nguoi_noi():
    for i in range(400):
        rng = random.Random(i)
        ca = sh.sinh_ca(f"x{i}", rng)
        s = sh.sinh_hoi_thoai(ca, rng)
        tx = ca.nguoi_ke[2] if ca.nguoi_ke else ca.tu_xung_bn
        cuoi = s.luot[-1][1].lower()
        assert set(re.findall(r"(?<!\w)(tôi|em|cháu|con)(?!\w)", cuoi)) <= {tx}, (tx, cuoi)
