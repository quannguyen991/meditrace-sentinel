# -*- coding: utf-8 -*-
from tools.kiem_ke_luat import kiem_ke


def _tao(thu_muc, ten, noi_dung):
    p = thu_muc / ten
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(noi_dung, encoding="utf-8")


def test_mo_dun_khong_ai_nhap(tmp_path):
    src, tests = tmp_path / "src", tmp_path / "tests"
    _tao(src, "dich_vu.py", "from src import a\n")
    _tao(src, "a.py", "import src.b as b\n# Nguon: Duoc thu QG 2018, tr. 12\n")
    _tao(src, "b.py", "x = 1\n")
    _tao(src, "c.py", "y = 2\n")
    _tao(tests, "test_a.py", "from src import a\n")
    kq = {d["mo_dun"]: d for d in kiem_ke(src, tests)}
    assert kq["c"]["duoc_nhap_boi"] == []
    assert kq["b"]["duoc_nhap_boi"] == ["a"]
    assert kq["a"]["co_phep_thu"] and not kq["b"]["co_phep_thu"]
    assert kq["a"]["so_cho_ghi_nguon"] == 1
    assert kq["b"]["nam_tren_luong_chinh"] and not kq["c"]["nam_tren_luong_chinh"]


def test_goi_con_va_nhap_tuong_doi(tmp_path):
    src, tests = tmp_path / "src", tmp_path / "tests"
    _tao(src, "dich_vu.py", "from src.canh_bao import gop\n")
    _tao(src, "canh_bao/__init__.py", "")
    _tao(src, "canh_bao/gop.py", "from . import loai\nfrom .phat_hien import f\n")
    _tao(src, "canh_bao/loai.py", "")
    _tao(src, "canh_bao/phat_hien.py", "def f(): pass\n")
    kq = {d["mo_dun"]: d for d in kiem_ke(src, tests)}
    assert kq["canh_bao.loai"]["duoc_nhap_boi"] == ["canh_bao.gop"]
    assert kq["canh_bao.phat_hien"]["nam_tren_luong_chinh"]
