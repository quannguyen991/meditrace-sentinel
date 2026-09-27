# -*- coding: utf-8 -*-
"""Phep do chat luong phat hien quan he.

VI SAO PHEP DO NAY PHAI DEM BON CON SO, khong phai mot.

Tren bo tu sinh, mo hinh nen du doan 20 quan he trong khi dap an co 17, va
phan bo loai gan khop (dinh chinh 10/10, dien bien 8/7). Neu chi dem tong so
thi ket luan se la "co che chay tot".

Thuc te: **1 tren 17 cap la dung**. Mo hinh danh dau dung SO LUONG va dung
LOAI nhung sai CAP — no bat trung muc tieu o muc thong ke tong the va truot
gan het o muc tung truong hop.

Nen phep do phai tach: dung / thieu / thua / nham loai. Gop lai thanh mot ty
le la giau mat dung cai can thay.
"""
import pytest

from src import do_quan_he as dq


def _ca(dap_an):
    return {"id": "t1", "dap_an": dap_an}


def _md(noi_dung, chu_the="bệnh nhân", **kw):
    return {"chu_the": chu_the, "noi_dung": noi_dung, "muc": "BỆNH SỬ HIỆN TẠI",
            "quan_he": None, "quan_he_voi": None, "tinh_huong": "thực tế", **kw}


def _pb(noi_dung, chu_the="bệnh nhân", **kw):
    return {"chu_the": chu_the, "noi_dung": noi_dung, "tinh_huong": "thực tế", **kw}


# ------------------------------------------------------- bon nhom dem rieng

def test_cap_dung_thi_tinh_dung():
    ca = _ca([_md("sốt", moc_thoi_gian="4 ngày"),
              _md("sốt", moc_thoi_gian="2 ngày",
                  quan_he="đính chính", quan_he_voi=0)])
    tho = [{"id": "t1", "phat_bieu": [
        _pb("sốt"), _pb("sốt", quan_he="đính chính", quan_he_voi=0)]}]
    tk = dq.do({"t1": ca}, tho)
    assert (tk["dung"], tk["thieu"] if "thieu" in tk else tk["sot"],
            tk["thua"], tk["nham_loai"]) == (1, 0, 0, 0)


def test_dung_cap_sai_loai_tinh_rieng_khong_gop_vao_thua():
    """Bat dung hai menh de co lien quan nhung goi sai ten quan he la mot loai
    loi KHAC voi bat nham hai menh de khong lien quan. Gop lai thi khong biet
    phai sua cho nao."""
    ca = _ca([_md("nôn"), _md("nôn", quan_he="diễn biến", quan_he_voi=0)])
    tho = [{"id": "t1", "phat_bieu": [
        _pb("nôn"), _pb("nôn", quan_he="đính chính", quan_he_voi=0)]}]
    tk = dq.do({"t1": ca}, tho)
    assert tk["nham_loai"] == 1
    assert tk["dung"] == 0 and tk["thua"] == 0 and tk["sot"] == 0


def test_bat_ra_cap_khong_co_that_la_thua():
    ca = _ca([_md("ho"), _md("sốt")])
    tho = [{"id": "t1", "phat_bieu": [
        _pb("ho"), _pb("sốt", quan_he="diễn biến", quan_he_voi=0)]}]
    tk = dq.do({"t1": ca}, tho)
    assert tk["thua"] == 1 and tk["dung"] == 0


def test_khong_bat_duoc_cap_co_that_la_thieu():
    ca = _ca([_md("nôn"), _md("nôn", quan_he="diễn biến", quan_he_voi=0)])
    tho = [{"id": "t1", "phat_bieu": [_pb("nôn"), _pb("nôn")]}]
    tk = dq.do({"t1": ca}, tho)
    assert tk["sot"] == 1 and tk["dung"] == 0


def test_dung_so_luong_nhung_sai_cap_KHONG_duoc_tinh_la_dat():
    """Day la truong hop that da gap tren bo tu sinh, va la ly do tep nay ton
    tai. Du doan 2 quan he, dap an co 2 quan he, dung loai — nhung sai cap."""
    ca = _ca([_md("sốt"), _md("ho"),
              _md("sốt", quan_he="đính chính", quan_he_voi=0)])
    tho = [{"id": "t1", "phat_bieu": [
        _pb("sốt"), _pb("ho"),
        _pb("ho", quan_he="đính chính", quan_he_voi=1)]}]
    tk = dq.do({"t1": ca}, tho)
    assert tk["theo_loai_that"] == {"đính chính": 1}
    assert tk["theo_loai_du_doan"] == {"đính chính": 1}
    assert tk["dung"] == 0, "so luong khop nhung cap sai — khong duoc tinh dung"
    assert tk["thua"] == 1 and tk["sot"] == 1


# ------------------------------------------------------------ truong hop bien

def test_bo_qua_quan_he_tro_ra_ngoai_bang():
    tho = [{"id": "t1", "phat_bieu": [
        _pb("sốt", quan_he="đính chính", quan_he_voi=99)]}]
    tk = dq.do({"t1": _ca([_md("sốt")])}, tho)
    assert tk["thua"] == 0


def test_bo_qua_quan_he_tro_vao_chinh_no():
    tho = [{"id": "t1", "phat_bieu": [
        _pb("sốt", quan_he="đính chính", quan_he_voi=0)]}]
    tk = dq.do({"t1": _ca([_md("sốt")])}, tho)
    assert tk["thua"] == 0


def test_quan_he_bang_khong_khong_tinh_la_du_doan():
    tho = [{"id": "t1", "phat_bieu": [
        _pb("sốt"), _pb("sốt", quan_he="không", quan_he_voi=0)]}]
    tk = dq.do({"t1": _ca([_md("sốt"), _md("sốt")])}, tho)
    assert tk["thua"] == 0 and tk["ca_co_du_doan"] == 0


def test_khac_chu_the_thi_khac_khoa():
    """Hai menh de cung noi dung nhung khac chu the KHONG duoc ghep voi nhau —
    do dung la loi nguy hiem nhat ma du an di chan."""
    ca = _ca([_md("dị ứng", chu_the="mẹ"),
              _md("dị ứng", chu_the="trẻ", quan_he="đính chính", quan_he_voi=0)])
    tho = [{"id": "t1", "phat_bieu": [
        _pb("dị ứng", chu_the="trẻ"),
        _pb("dị ứng", chu_the="mẹ", quan_he="đính chính", quan_he_voi=0)]}]
    tk = dq.do({"t1": ca}, tho)
    assert tk["dung"] == 0, "ghep nham hai chu the ma van tinh dung"


# ----------------------------------------------------------- tinh huong

def test_do_tinh_huong_dem_ba_nhom():
    ca = _ca([_md("sốt", tinh_huong="giả định"), _md("ho")])
    tho = [{"id": "t1", "phat_bieu": [
        _pb("sốt"), _pb("ho", tinh_huong="giả định")]}]
    tk = dq.do_tinh_huong({"t1": ca}, tho)
    assert (tk["dung"], tk["sot"], tk["thua"]) == (0, 1, 1)


def test_do_tinh_huong_khop_thi_dung():
    ca = _ca([_md("sốt", tinh_huong="giả định")])
    tho = [{"id": "t1", "phat_bieu": [_pb("sốt", tinh_huong="giả định")]}]
    tk = dq.do_tinh_huong({"t1": ca}, tho)
    assert tk["dung"] == 1 and tk["do_chuan"] == 1.0


def test_bo_qua_ca_khong_co_trong_dap_an():
    tk = dq.do({}, [{"id": "la", "phat_bieu": [_pb("sốt")]}])
    assert tk["dung"] == 0 and tk["thua"] == 0
