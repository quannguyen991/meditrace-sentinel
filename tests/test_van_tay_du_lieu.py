# -*- coding: utf-8 -*-
"""Khong duoc chay tiep tu checkpoint khi DU LIEU da doi.

VI SAO CO TEP NAY (10/09/2026).

`train_baseline` tu dong chay tiep neu thay bat ky `checkpoint-*` nao trong thu
muc dich. Dieu do dung khi mot lan chay bi ngat giua chung. Nhung khi BO DU
LIEU doi ma checkpoint cu van con, no chay tiep tu mo hinh cu:

    huan luyen 300 buoc tren bo 3.000 ca
    roi 100 buoc tren bo 5.000 ca
    -> mot adapter lai giua hai bo, khong noi len duoc gi

Khong co gi bao loi. Chi phat hien duoc vi `eval_loss` o cac buoc dau TRUNG
TUNG CHU SO voi lan chay truoc — mot dau hieu chi thay neu tinh co con nho so
cu. Va vi no TANG len o hai buoc cuoi (0,0003 -> 0,0016), dau hieu phan phoi
du lieu doi duoi chan mo hinh.

Day la loi im lang thu SAU cung ho trong du an nay.
"""
import json

from src import train_baseline as tb


def _mau(i):
    return {"input": f"hội thoại {i}", "output": f"bệnh án {i}"}


def test_cung_du_lieu_ra_cung_van_tay():
    a = [_mau(i) for i in range(50)]
    b = [_mau(i) for i in range(50)]
    assert tb._van_tay_du_lieu(a) == tb._van_tay_du_lieu(b)


def test_khac_so_mau_ra_van_tay_khac():
    a = [_mau(i) for i in range(50)]
    b = [_mau(i) for i in range(60)]
    assert tb._van_tay_du_lieu(a) != tb._van_tay_du_lieu(b)


def test_CUNG_so_mau_nhung_khac_noi_dung_van_bat_duoc():
    """Truong hop nguy hiem nhat: sinh lai voi seed khac, hoac doi bo sinh.
    So mau khong doi nen dem so khong bat duoc."""
    a = [_mau(i) for i in range(50)]
    b = [_mau(i + 1000) for i in range(50)]
    assert tb._van_tay_du_lieu(a) != tb._van_tay_du_lieu(b)


def test_doi_mau_o_GIUA_thi_khong_bat_duoc__gioi_han_da_biet():
    """Ghi lai gioi han that: van tay chi xet mau DAU va CUOI.

    Doi mot mau o giua ma giu nguyen so mau, mau dau va mau cuoi thi van tay
    khong doi. Chap nhan gioi han nay vi bam toan bo tap se chay o dau moi lan
    train tren vai chuc nghin mau.

    Test nay ton tai de nguoi doc sau khong tuong van tay la bam toan bo.
    """
    a = [_mau(i) for i in range(50)]
    b = list(a)
    b[25] = _mau(9999)
    assert tb._van_tay_du_lieu(a) == tb._van_tay_du_lieu(b)


def test_tap_rong_khong_no():
    assert tb._van_tay_du_lieu([])["so_mau"] == 0


def test_van_tay_ghi_duoc_ra_json():
    """Van tay duoc ghi ra tep canh checkpoint, nen phai tuan tu hoa duoc."""
    vt = tb._van_tay_du_lieu([_mau(1), _mau(2)])
    assert json.loads(json.dumps(vt, ensure_ascii=False)) == vt


def test_ma_co_chot_tu_choi_khi_lech():
    """Chot phai NEM LOI chu khong phai in canh bao roi chay tiep."""
    import pathlib
    t = (pathlib.Path("src") / "train_baseline.py").read_text(encoding="utf-8")
    assert "TU CHOI chay tiep" in t
    assert "raise SystemExit" in t
    # va phai chi ra cach sua, khong chi noi "khong duoc"
    assert "Xoa cac thu muc checkpoint-*" in t
