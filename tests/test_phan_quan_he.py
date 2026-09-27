# -*- coding: utf-8 -*-
"""Buoc phan quan he theo tung cap.

Test o day KHONG dung mo hinh. Ba thu duoc kiem:
  1. cau hoi dung du can cu (co nguyen van luot thoai)
  2. doc dap an khong bao gio doan bua
  3. duong "luat" khoi phuc duoc quan he tren dung nhung ca no phai bat duoc,
     va KHONG bat bua tren ca sach
"""
import pytest

from src import phan_quan_he as pq
from src import ung_vien_quan_he as uv
from src.phat_bieu import PhatBieu


def _pb(id, noi_dung, bang_chung, moc=None, chu_the_id=1, **kw):
    return PhatBieu(id=id, nguoi_noi="bệnh nhân", chu_the_id=chu_the_id,
                    noi_dung=noi_dung, bang_chung=bang_chung,
                    moc_thoi_gian=moc, **kw)


# ------------------------------------------------------------------ cau hoi

def test_cau_hoi_co_nguyen_van_luot_thoai():
    """Dau hieu dinh chinh nam trong LOI NOI. Bo luot thoai di la cat mat can
    cu chinh — cau hoi con lai chi la hai ban ghi kho."""
    ps = [_pb(1, "sốt", [2], moc="4 ngày"), _pb(2, "sốt", [4], moc="2 ngày")]
    luot = {2: "Cháu sốt 4 ngày rồi.", 4: "À không, 2 ngày thôi ạ."}
    cap = uv.CapUngVien(a=1, b=2, ly_do=("khác mốc",), diem=1.0)

    ch = pq.cau_hoi(cap, ps, luot)
    assert "À không, 2 ngày thôi ạ." in ch
    assert "Cháu sốt 4 ngày rồi." in ch
    assert "2. " in ch and "4. " in ch          # co so thu tu luot


def test_cau_hoi_khong_in_truong_rong():
    """Truong rong in ra lam mo hinh tuong la co thong tin o do."""
    ps = [_pb(1, "ho", [1]), _pb(2, "ho", [2])]
    ch = pq.cau_hoi(uv.CapUngVien(a=1, b=2, ly_do=(), diem=0.0), ps, {1: "a", 2: "b"})
    assert "mốc thời gian" not in ch
    assert "phủ định" not in ch
    assert "mức chắc chắn" not in ch


def test_cau_hoi_bao_loi_khi_cap_tro_sai():
    ps = [_pb(1, "ho", [1])]
    with pytest.raises(KeyError):
        pq.cau_hoi(uv.CapUngVien(a=1, b=99, ly_do=(), diem=0.0), ps, {})


def test_cau_hoi_liet_ke_du_nam_dap_an():
    ps = [_pb(1, "ho", [1]), _pb(2, "ho", [2])]
    ch = pq.cau_hoi(uv.CapUngVien(a=1, b=2, ly_do=(), diem=0.0), ps, {1: "a", 2: "b"})
    for d in pq.DAP_AN:
        assert f'"{d}"' in ch


# --------------------------------------------------------------- doc dap an

@pytest.mark.parametrize("van,mong", [
    ('{"quan_he": "đính chính"}', "đính chính"),
    ('{"quan_he": "diễn biến"}', "diễn biến"),
    ('  {"quan_he":"bổ sung"}  ', "bổ sung"),
    ('Trả lời: {"quan_he": "mâu thuẫn"}', "mâu thuẫn"),
])
def test_doc_dap_an_json(van, mong):
    assert pq.doc_dap_an(van) == mong


@pytest.mark.parametrize("van", [
    '{"quan_he": "không"}',        # dap an thu nam -> None
    '{"quan_he": "linh tinh"}',    # rac
    '{"quan_he": ""}',
    "",
    None,
    "Tôi không chắc.",
    "{hong json",
])
def test_doc_dap_an_khong_doan_bua(van):
    """Quan he gia nguy hiem hon khong co quan he: `cap_nhat.ap_luat` se danh
    dau mot ban ghi DUNG thanh 'bi thay the' va vut no khoi benh an."""
    assert pq.doc_dap_an(van) is None


def test_doc_dap_an_van_xuoi_uu_tien_nhan_dai_hon():
    """'khong' la con cua nhieu cau; khong duoc de no nuot mat nhan that."""
    assert pq.doc_dap_an("Quan hệ ở đây là đính chính.") == "đính chính"


# ------------------------------------------------------------- duong "luat"

def test_luat_bat_duoc_dinh_chinh():
    ps = [_pb(1, "sốt", [2], moc="4 ngày"), _pb(2, "sốt", [4], moc="2 ngày")]
    luot = {2: "Cháu sốt 4 ngày rồi.", 4: "À không, 2 ngày thôi ạ."}
    moi, tk = pq.phan(ps, luot, duong="luat")
    assert tk["so_phan"] == 1
    assert [p.quan_he for p in moi if p.quan_he] == ["đính chính"]


def test_luat_bat_duoc_dien_bien():
    ps = [_pb(1, "nôn", [2], moc="hôm qua"),
          _pb(2, "nôn", [4], moc="hôm nay", phu_dinh=True)]
    luot = {2: "Hôm qua cháu nôn.", 4: "Hôm nay thì hết rồi ạ."}
    moi, tk = pq.phan(ps, luot, duong="luat")
    assert tk["theo_nhan"].get("diễn biến") == 1


def test_luat_khong_bat_bua_tren_ca_sach():
    """Doi chung. Mot buoc phan gan quan he cho moi cap se dat diem cao gia
    tren cac tinh huong co bay, va pha benh an tren ca khong co bay."""
    ps = [_pb(1, "ho", [2]), _pb(2, "sốt", [4])]
    luot = {2: "Cháu bị ho ạ.", 4: "Cháu có sốt nữa."}
    moi, tk = pq.phan(ps, luot, duong="luat")
    assert tk["so_phan"] == 0
    assert all(p.quan_he is None for p in moi)


def test_phan_khong_sua_ban_goc():
    ps = [_pb(1, "sốt", [2], moc="4 ngày"), _pb(2, "sốt", [4], moc="2 ngày")]
    luot = {2: "Cháu sốt 4 ngày.", 4: "À nhầm, 2 ngày."}
    pq.phan(ps, luot, duong="luat")
    assert all(p.quan_he is None for p in ps), "phan() da sua ban goc"


def test_phan_tra_thong_ke_rong_khi_khong_co_cap():
    ps = [_pb(1, "ho", [1])]
    moi, tk = pq.phan(ps, {1: "ho ạ"}, duong="luat")
    assert tk == {"so_cap": 0, "so_phan": 0, "bi_cat": False,
                  "theo_nhan": {}, "duong": "luat"}
    assert moi is ps


def test_duong_khong_hop_le_bao_loi():
    with pytest.raises(AssertionError):
        pq.phan([], {}, duong="linh_tinh")


# ------------------------------------------------- duong "ca_hai" tiet kiem

class _ModelGia:
    """Dem so lan bi hoi. Khong nap mo hinh that."""

    def __init__(self):
        self.so_lan = 0


def test_ca_hai_khong_hoi_lai_cap_da_co_dap_an(monkeypatch):
    """Cap nao luat da quyet thi khong ton mot luot goi mo hinh."""
    dem = _ModelGia()

    def _gia(caps, danh_sach, luot_thoai, tok, model, prefix_fn=None,
             max_token=24, bo_qua=None):
        bo_qua = bo_qua or {}
        ra = {}
        for c in caps:
            if bo_qua.get(c.khoa()) is not None:
                ra[c.khoa()] = bo_qua[c.khoa()]
                continue
            dem.so_lan += 1
            ra[c.khoa()] = None
        return ra

    monkeypatch.setattr(pq, "phan_bang_mo_hinh", _gia)
    ps = [_pb(1, "sốt", [2], moc="4 ngày"), _pb(2, "sốt", [4], moc="2 ngày")]
    luot = {2: "Cháu sốt 4 ngày.", 4: "À không, 2 ngày."}
    _, tk = pq.phan(ps, luot, duong="ca_hai", tok=None, model=object())
    assert dem.so_lan == 0, "cap da co dap an tu luat ma van hoi mo hinh"
    assert tk["so_phan"] == 1
