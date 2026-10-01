# -*- coding: utf-8 -*-
"""Bang khai ma nguon.

Phu luc AI cho phep "AI viet ma nguon ban dau" voi hai dieu kien: ghi ro ma nao
do AI sinh, va co nhat ky loi nhac. Tep nay lam dieu thu nhat.

Test o day cot loi kiem MOT thu: bang khong duoc noi gi manh hon su that. Cu
the la khong duoc de trong khi khong truy duoc loi nhac cho mot tep — im lang
o cho do la khai bao thieu.
"""
import pytest

from src import khai_ma_nguon as km


@pytest.fixture(scope="module")
def lich_su():
    return km.lich_su_tep()


def test_doc_duoc_lich_su_git(lich_su):
    assert lich_su, "khong doc duoc lich su git"
    assert all(m["so_lan_sua"] >= 1 for m in lich_su.values())


def test_chi_gom_thu_muc_ma_nguon(lich_su):
    for t in lich_su:
        assert t.split("/")[0] in km.THU_MUC_MA, t


def test_khong_gom_tai_lieu(lich_su):
    assert not [t for t in lich_su if t.startswith("docs/")]


def test_ngay_dau_khong_sau_ngay_cuoi(lich_su):
    for t, m in lich_su.items():
        assert m["ngay_dau"] <= m["ngay_cuoi"], t


# ------------------------------------------------------- noi dung bang

def _gon(van):
    """Bo cho ngat dong truoc khi kiem.

    Kiem chuoi co xuong dong o giua la kiem gion: doi cho ngat dong mot chut
    la test do, du noi dung khong doi. Da hong that o
    `test_tep_khong_truy_duoc_van_duoc_khai_la_AI_viet`.
    """
    import re
    return re.sub(r"\s+", " ", van)


def _bang():
    ls = {"src/a.py": {"so_lan_sua": 3, "ngay": [], "commit": [],
                       "ngay_dau": "2026-09-05", "ngay_cuoi": "2026-09-07"},
          "src/b.py": {"so_lan_sua": 1, "ngay": [], "commit": [],
                       "ngay_dau": "2026-09-06", "ngay_cuoi": "2026-09-06"}}
    return km.dung_bang(ls, {"src/a.py": ["viết bộ sinh"]})


def test_khai_ro_toan_bo_do_AI_viet():
    """Cau khai phai o dau, khong duoc giau trong bang."""
    t = _gon(_bang())
    assert "do AI viết" in t
    assert "Không có tệp nào được viết tay hoàn toàn" in t


def test_NOI_RO_tep_khong_truy_duoc_loi_nhac():
    """Im lang o cho khong truy duoc la khai bao thieu."""
    t = _gon(_bang())
    assert "không truy được lời nhắc riêng" in t
    assert "`src/b.py`" in t


def test_tep_khong_truy_duoc_van_duoc_khai_la_AI_viet():
    """Khong truy duoc loi nhac KHONG co nghia la khong ro nguon goc."""
    t = _gon(_bang())
    assert "thiếu *đường truy ngược tới lời nhắc*" in t


def test_phan_biet_go_ma_voi_quyet_dinh_thiet_ke():
    """Bang noi ve viec GO MA. Quyet dinh thiet ke la cua hoc sinh, va phai
    duoc noi ro — neu khong thi bang nay doc thanh 'AI lam het'."""
    t = _gon(_bang())
    assert "quyết định thiết kế" in t.lower()
    assert "không câu nào là một dòng mã" in t


def test_co_du_cac_thu_muc_ma():
    # ba thư mục của phần xử lý + `web` (giao diện, kho riêng, ghi là web/...)
    assert set(km.THU_MUC_MA) == {"src", "tests", "tools", "web"}


def test_bang_co_so_lan_sua_va_ngay():
    t = _gon(_bang())
    assert "Lần sửa" in t and "Từ ngày" in t and "Đến ngày" in t
