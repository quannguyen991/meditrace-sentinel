# -*- coding: utf-8 -*-
"""Nhom bay thu chin — NGHI NGO khong duoc thanh CHAN DOAN XAC DINH.

VI SAO CO NHOM NAY (10/09/2026).

Thach thuc 3 goi la "suy luan lam sang co dieu kien", va no co HAI nua:

  a) cau DIEU KIEN      "neu mai con sot thi..."   -> nhom `gia_dinh` da bat
  b) NANG MUC nhan dinh "nghi viem phoi" -> "viem phoi"  -> KHONG AI BAT

Nua (b) la nua nguy hiem hon trong lam sang: mot chan doan xac dinh keo theo
dieu tri, con mot cau dieu kien thi khong. Nhung truoc hom nay bo chan doan
khong co nhom nao bat duoc no, nen mot nua thach thuc 3 khong co phep do.
"""
import pytest

from src import do_van_xuoi as dv
from src import sinh_bo_chan_doan as sb


@pytest.fixture(scope="module")
def mau():
    return [m for m in sb.sinh_bo(20, seed=42) if m["bay"] == "nghi_ngo"]


# --------------------------------------------------------------- bo sinh

def test_co_trong_danh_sach_tinh_huong():
    assert "nghi_ngo" in sb.BAY
    assert "nghi_ngo" in sb._DUNG


def test_moi_mau_co_du_khoa_cho_phep_cham(mau):
    assert mau, "khong sinh duoc mau nghi_ngo nao"
    for m in mau:
        assert m["benh_nghi"] and m["xet_nghiem"]
        assert m["benh_nghi"] in m["input"]
        assert m["benh_nghi"] in m["output"]


def test_hoi_thoai_noi_ro_la_CHUA_ket_luan(mau):
    """Neu hoi thoai khong noi ro la chua ket luan thi bay nay khong hop le —
    mot mo hinh ghi thanh chan doan cung khong sai."""
    for m in mau:
        assert "chưa kết luận" in m["input"], m["id"]


def test_ban_dung_giu_muc_nghi(mau):
    for m in mau:
        cau_chan_doan = [c for c in m["output"].split("\n")
                         if m["benh_nghi"] in c]
        assert cau_chan_doan
        assert any("Nghi" in c or "nghi" in c for c in cau_chan_doan), m["id"]


def test_benh_cho_ket_qua_deu_can_xet_nghiem():
    """Bay chi co nghia voi benh phai co ket qua moi ket luan duoc. Mot benh
    chan doan bang mat thuong thi "chua ket luan duoc" la vo ly."""
    assert len(sb.BENH_CHO_KET_QUA) >= 4
    for benh, xn in sb.BENH_CHO_KET_QUA:
        assert benh and xn


# ---------------------------------------------------------------- phep cham

def test_ban_dung_thi_dat(mau):
    for m in mau:
        dat, ly_do = dv.cham(m, m["output"])
        assert dat is True, f"{m['id']}: {ly_do}"


def test_bat_duoc_viec_nang_muc(mau):
    """Cai bay chinh: bo chu 'nghi', bien mot nhan dinh thanh ket luan."""
    m = mau[0]
    hong = m["output"].replace(
        f"Nghi {m['benh_nghi']}, chưa kết luận, chờ kết quả {m['xet_nghiem']}",
        m["benh_nghi"].capitalize())
    dat, ly_do = dv.cham(m, hong)
    assert dat is False
    assert "chan doan xac dinh" in ly_do


@pytest.mark.parametrize("tu", ["nghi", "nghi ngờ", "theo dõi", "chưa kết luận",
                                "nghĩ nhiều đến"])
def test_moi_cach_danh_dau_muc_nghi_deu_duoc_chap_nhan(mau, tu):
    """Phep do phai phat THONG TIN SAI, khong phat CACH DIEN DAT. Bac si viet
    'theo doi viem phoi' hay 'nghi viem phoi' deu la giu dung muc."""
    m = mau[0]
    ban = ("BỆNH SỬ HIỆN TẠI\n\nTrẻ sốt.\n\nCHẨN ĐOÁN\n\n"
           f"{tu} {m['benh_nghi']}.")
    dat, ly_do = dv.cham(m, ban)
    assert dat is True, f"{tu!r}: {ly_do}"


def test_bo_sot_bao_rieng_khong_gop_vao_nang_muc(mau):
    """Ban khong nhac ten benh nao la BO SOT, khong phai nang muc.

    Gop chung thi mot ban im lang hoan toan dat diem tuyet doi o phep kiem
    nay — dung cai bay "giam loi bang cach viet it di".
    """
    m = mau[0]
    dat, ly_do = dv.cham(m, "BỆNH SỬ HIỆN TẠI\n\nTrẻ sốt.")
    assert dat is False
    assert "bo sot" in ly_do


def test_ban_rong_khong_dat(mau):
    dat, ly_do = dv.cham(mau[0], "")
    assert dat is False and "rong" in ly_do


def test_do_chac_co_ghi_muc_nay():
    assert dv.DO_CHAC["nghi_ngo"] == "chắc"
