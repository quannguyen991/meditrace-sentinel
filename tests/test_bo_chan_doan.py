# -*- coding: utf-8 -*-
"""Moi tinh huong mot test. Cac test nay kiem BENH AN DUNG do chinh ma sinh ra,
tuc la kiem xem dap an cua bo kiem tra co dung khong — neu dap an sai thi moi
phep do ve sau deu sai theo.
"""
import re

import pytest

from src import sinh_bo_chan_doan as sb

BO = sb.sinh_bo(5, seed=1)


def _lay(bay):
    return [m for m in BO if m["bay"] == bay]


def test_sinh_du_bay_tinh_huong():
    # Buoc so tinh huong theo `sb.BAY` chu khong go cung so 7: them mot nhom
    # bay moi thi test nay phai van kiem dung viec "moi nhom deu sinh du n mau",
    # khong phai do lai vi mot con so dem.
    assert {m["bay"] for m in BO} == set(sb.BAY)
    assert len(BO) == len(sb.BAY) * 5
    for ten in sb.BAY:
        assert len(_lay(ten)) == 5, ten


def test_id_duy_nhat():
    assert len({m["id"] for m in BO}) == len(BO)


def test_bay_chu_the_di_ung_thuoc_ve_me():
    for m in _lay("chu_the"):
        assert "TIỀN SỬ GIA ĐÌNH" in m["output"], "di ung cua me thuoc muc gia dinh"
        gd = m["output"].split("TIỀN SỬ GIA ĐÌNH")[1]
        assert m["thuoc"] in gd, "ten thuoc phai nam trong muc gia dinh"
        di_ung = m["output"].split("TIỀN SỬ DỊ ỨNG")[1].split("TIỀN SỬ GIA ĐÌNH")[0]
        assert m["thuoc"] not in di_ung, "KHONG duoc gan di ung cua me cho tre"


def test_bay_chac_chan_giu_chua_ghi_nhan():
    for m in _lay("chac_chan"):
        assert m["cum_dung"] in m["output"]
        assert m["cum_sai"] not in m["output"], "khong duoc nang thanh phu dinh chac chan"


def test_bay_dinh_chinh_giu_moc_moi_bo_moc_cu():
    for m in _lay("dinh_chinh"):
        assert m["moc_moi"] in m["output"]
        # Moc cu chi duoc xuat hien trong cau ghi chu ve viec da dinh chinh
        assert "đính chính" in m["output"], "phai ghi lai rang da co dinh chinh"
        truoc_ghi_chu = m["output"].split("Người nhà nêu ban đầu")[0]
        assert m["moc_cu"] not in truoc_ghi_chu, "moc cu khong duoc dung lam so lieu"


def test_bay_dien_bien_GIU_CA_HAI_MOC():
    """Loi de mac nhat: coi dien bien la dinh chinh roi vut mat cau dau."""
    for m in _lay("dien_bien"):
        assert m["moc_cu"] in m["output"], "moc cu PHAI con — day khong phai dinh chinh"
        assert m["moc_moi"] in m["output"], "moc moi cung phai con"


def _co_cum_rieng(cum, van_ban):
    """So theo ranh gioi tu, khong theo chuoi con.

    "ho" la tien to cua "ho khan": kiem bang chuoi con se bao dong gia.
    """
    return re.search(rf"{re.escape(cum)}(?![\wÀ-ỹ])", van_ban) is not None


def test_bay_gia_dinh_khong_thanh_trieu_chung():
    for m in _lay("gia_dinh"):
        assert m["trieu_chung_that"] in m["output"]
        assert not _co_cum_rieng(f"Trẻ {m['dieu_kien']}", m["output"]), \
            "cau gia dinh khong duoc ghi thanh trieu chung da xay ra"


def test_dieu_kien_gia_dinh_khong_trung_voi_trieu_chung_that():
    """Neu hai cum long nhau thi khong con kiem duoc gi."""
    for m in _lay("gia_dinh") + _lay("moi_bia"):
        a = m.get("dieu_kien") or m["moi_khong_duoc_tra_loi"]
        b = m["trieu_chung_that"]
        assert a not in b and b not in a, f"{a!r} va {b!r} long nhau"


def test_bay_moi_bia_khong_tra_loi_thi_khong_ghi():
    for m in _lay("moi_bia"):
        assert m["moi_khong_duoc_tra_loi"] not in m["output"], \
            "cau hoi khong ai tra loi thi benh an khong duoc nhac toi"


def test_nhom_sach_khong_co_bay():
    """Khong co nhom sach thi khong phan biet duoc 'bat duoc bay' voi
    'canh giac qua muc, gan co moi thu'."""
    sach = _lay("sach")
    assert len(sach) == 5
    for m in sach:
        assert "đính chính" not in m["output"]
        assert "chưa ghi nhận" not in m["output"]


def test_sinh_lai_cung_seed_ra_cung_ket_qua():
    assert sb.sinh_bo(10, seed=7) == sb.sinh_bo(10, seed=7)


def test_doi_n_khong_lam_doi_mau_cu():
    """Sinh 10 mau thi 5 mau dau phai giong het khi sinh 5 mau."""
    a = sb.sinh_bo(5, seed=3)
    b = sb.sinh_bo(10, seed=3)
    for bay in sb.BAY:
        ta = [m for m in a if m["bay"] == bay]
        tb = [m for m in b if m["bay"] == bay][:5]
        assert ta == tb


def test_moi_mau_deu_co_luot_nguoi_nha():
    for m in BO:
        assert "Người nhà:" in m["input"]
