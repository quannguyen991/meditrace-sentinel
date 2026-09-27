# -*- coding: utf-8 -*-
"""Nhom bay thu tam — tinh nhat quan giua HAI MUC trong cung mot benh an.

VI SAO CO NHOM NAY. Truoc 09/09/2026 khong phep do nao cua du an bat duoc loi
mau thuan noi bo:

  - ROUGE dem tu, nen "da ngung" va "dang dung" deu khop tu nhu nhau
  - diem quy gan chi xet chu the
  - bay nhom cu deu chi xet MOT cau mot

Nen thach thuc 5 (day du va nhat quan) khong co so nao trong bang ket qua. Mot
thach thuc khong do duoc thi khong duoc bao cao nhu da giai.
"""
import pytest

from src import do_van_xuoi as dv
from src import sinh_bo_chan_doan as sb


@pytest.fixture(scope="module")
def mau():
    return [m for m in sb.sinh_bo(20, seed=42) if m["bay"] == "nhat_quan"]


# --------------------------------------------------------------- bo sinh

def test_co_trong_danh_sach_tinh_huong():
    assert "nhat_quan" in sb.BAY
    assert "nhat_quan" in sb._DUNG


def test_moi_mau_co_du_khoa_cho_phep_cham(mau):
    for m in mau:
        assert m["thuoc_da_ngung"], m["id"]
        assert m["thuoc_da_ngung"] in m["input"]
        assert m["thuoc_da_ngung"] in m["output"]


def test_thuoc_da_ngung_roi_han_voi_thuoc_di_ung():
    """Tron hai kho thuoc thi mot mau co the vua la bay nay vua la bay kia, va
    khong con biet phep kiem dang bat cai gi."""
    assert not (set(sb.THUOC) & set(sb.THUOC_DA_NGUNG))


def test_ban_dung_khong_co_muc_thuoc_dang_dung(mau):
    for m in mau:
        assert dv.MUC_DANG_DUNG not in m["output"], m["id"]


def test_sinh_lai_cung_seed_ra_cung_ket_qua():
    assert sb.sinh_bo(5, seed=42) == sb.sinh_bo(5, seed=42)


# ---------------------------------------------------------------- phep cham

def test_ban_dung_thi_dat(mau):
    for m in mau:
        dat, ly_do = dv.cham(m, m["output"])
        assert dat is True, f"{m['id']}: {ly_do}"


def test_bat_duoc_thuoc_nam_o_muc_dang_dung(mau):
    """Cach hong 1: sai VI TRI. Cau doc rieng van dung, chi sai vi no nam duoi
    tieu de THUOC DANG DUNG."""
    m = mau[0]
    hong = (m["output"] + "\n\n" + dv.MUC_DANG_DUNG + "\n\n"
            + m["thuoc_da_ngung"].capitalize() + ".")
    dat, ly_do = dv.cham(m, hong)
    assert dat is False
    assert dv.MUC_DANG_DUNG in ly_do


def test_bat_duoc_cau_noi_dang_dung(mau):
    """Cach hong 2: sai DIEN DAT. Dung muc, nhung cau noi thuoc dang dung."""
    m = mau[0]
    hong = m["output"].replace("đã ngừng", "hiện đang dùng")
    dat, ly_do = dv.cham(m, hong)
    assert dat is False
    assert "dang dung" in ly_do


def test_bo_sot_bao_rieng_khong_gop_vao_mau_thuan(mau):
    """Ban khong nhac toi thuoc nao la BO SOT, khong phai mau thuan.

    Gop chung thi mot ban rong se dat diem tuyet doi o phep kiem nay — dung
    cai bay "giam loi bang cach viet it di" ma ca du an di chan.
    """
    m = mau[0]
    dat, ly_do = dv.cham(m, "BỆNH SỬ HIỆN TẠI\n\nTrẻ mệt mỏi.")
    assert dat is False
    assert "bo sot" in ly_do


def test_ban_rong_khong_dat(mau):
    dat, ly_do = dv.cham(mau[0], "")
    assert dat is False and "rong" in ly_do


def test_noi_da_ngung_trong_cung_cau_thi_van_dat(mau):
    """Khong duoc bat nham: mot cau co ca "dang dung" lan "da ngung" —
    vi du "truoc dang dung X, nay da ngung" — la ghi dung."""
    m = mau[0]
    t = m["thuoc_da_ngung"]
    ban = ("BỆNH SỬ HIỆN TẠI\n\nTrẻ mệt mỏi.\n\nTIỀN SỬ BỆNH\n\n"
           f"Trước đang dùng {t}, nay đã ngừng.")
    dat, ly_do = dv.cham(m, ban)
    assert dat is True, ly_do


def test_do_chac_co_ghi_muc_nay():
    """Moi phep kiem phai khai minh chac hay chi xap xi."""
    assert dv.DO_CHAC["nhat_quan"] == "chắc"
