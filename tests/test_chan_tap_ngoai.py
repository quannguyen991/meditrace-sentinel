# -*- coding: utf-8 -*-
"""Chot chan du lieu cua cuoc thi cu.

VI SAO CO TEP NAY. Bon tap `train` / `phat_trien` / `kiem_tra_cuoi` /
`kiem_tra_chung` la BAN SAO du lieu cua mot cuoc thi NLP, khong phai du lieu
cua du an. Ban to chuc khuyen khong dung tai san cua ho, va do dau vet cho
thay bo do rat nhieu kha nang la ban dich tu tieng Anh.

Cai bay o day rat kin va DA TON TAI mot thoi gian dai: `nhanh.py` de `--tap`
mac dinh la "phat_trien", nen chay lenh mac dinh la doc phai du lieu cuoc thi
ma khong ai dinh lam the. Moi ket qua sinh ra kieu do trong y het ket qua tren
du lieu cua du an.

Nen chot nay phai duoc chan bang MA, va phai co test ca hai chieu: chieu chan
va chieu cho qua.
"""
import os

import pytest

from src import du_lieu


@pytest.mark.parametrize("ten", du_lieu.TAP_NGOAI)
def test_chan_moi_tap_cua_cuoc_thi(ten, monkeypatch):
    monkeypatch.delenv(du_lieu.CHO_PHEP_TAP_NGOAI, raising=False)
    with pytest.raises(SystemExit) as e:
        du_lieu.chan_tap_ngoai(ten)
    assert ten in str(e.value)


@pytest.mark.parametrize("ten", ["viet_train", "viet_phat_trien",
                                 "viet_kiem_tra_cuoi", "bo_chan_doan"])
def test_cho_qua_tap_cua_de_tai(ten, monkeypatch):
    monkeypatch.delenv(du_lieu.CHO_PHEP_TAP_NGOAI, raising=False)
    du_lieu.chan_tap_ngoai(ten)          # khong duoc nem loi


def test_chan_ca_khi_nam_trong_danh_sach(monkeypatch):
    monkeypatch.delenv(du_lieu.CHO_PHEP_TAP_NGOAI, raising=False)
    with pytest.raises(SystemExit):
        du_lieu.chan_tap_ngoai(["viet_phat_trien", "phat_trien"])


def test_duong_thoat_co_chu_dinh(monkeypatch):
    """Phep do dau vet nguon goc la mot ket qua that cua du an va can chay lai
    duoc. Nhung no phai la viec CO CHU DINH, khong phai thu xay ra vi mot gia
    tri mac dinh."""
    monkeypatch.setenv(du_lieu.CHO_PHEP_TAP_NGOAI, "1")
    du_lieu.chan_tap_ngoai("phat_trien")     # khong duoc nem loi


def test_thong_bao_chi_ra_tap_thay_the(monkeypatch):
    """Mot chot chi noi 'khong duoc' ma khong noi 'dung cai nao' thi nguoi gap
    no se tim cach go chot."""
    monkeypatch.delenv(du_lieu.CHO_PHEP_TAP_NGOAI, raising=False)
    with pytest.raises(SystemExit) as e:
        du_lieu.chan_tap_ngoai("phat_trien")
    tin = str(e.value)
    assert "viet_phat_trien" in tin
    assert du_lieu.CHO_PHEP_TAP_NGOAI in tin


def test_khong_con_mac_dinh_nao_tro_vao_du_lieu_cuoc_thi():
    """Chan o mot cho khong du neu mot cho khac van mac dinh doc vao do."""
    import pathlib
    import re
    xau = []
    for p in pathlib.Path("src").glob("*.py"):
        for so, dong in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            m = re.search(r'--tap".*default="([^"]+)"', dong)
            if m and m.group(1) in du_lieu.TAP_NGOAI:
                xau.append(f"{p.name}:{so} -> {m.group(1)}")
    assert not xau, "mac dinh con tro vao du lieu cuoc thi:\n" + "\n".join(xau)
