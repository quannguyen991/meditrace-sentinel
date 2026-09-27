# -*- coding: utf-8 -*-
"""Test cho PHEP PHAN XU cua duong danh doi.

Vi sao phan bao cao lai can test rieng. Hai lan o Task 10, mot phep cham tu bia
ra loi roi bao cao chinh cai loi do. O day rui ro nguoc lai va nang hon: mot
phep phan xu tu rut ra KET LUAN SAI tu so lieu dung.

Ca hai lan hong duoi day deu la loi that, da xay ra trong ban dau:

  1. Phan xu chi kiem `if not co_ich`, nen voi ket qua "thang 1, thua 2" no van
     in "bon dau hieu co mang thong tin" — nguoc han voi bang so ngay ben tren.
  2. Chon "diem tot nhat" bang `min(so_sai_chu_the)` nen no chon nguong 0,00,
     noi 100% phat bieu bi day xuong va than bai gan nhu trong. Bao cao viet
     "giam 100% loi" — dung cai bay ke hoach ghi la bay lon nhat cua du an:
     GIAM LOI BANG CACH VIET IT DI.
"""
from src.duong_danh_doi import _bao_cao


def diem(nguong, ty_le, sai, sai_nn, bo_sot, bo_sot_nn=None):
    return {"nguong": nguong, "ty_le_day_xuong": ty_le, "so_sai_chu_the": sai,
            "ngau_nhien_sai_chu_the": sai_nn, "bo_sot": bo_sot,
            "ngau_nhien_bo_sot": bo_sot_nn if bo_sot_nn is not None else bo_sot,
            "do_bao_phu": 1 - bo_sot, "f1_quy_gan": 0.2}


GOC = diem(1.01, 0.0, 0.60, 0.60, 0.50)


# ------------------------------------------------- phan xu ve nhom doi chung

def test_thang_it_hon_thua_thi_KHONG_duoc_ket_luan_la_co_thong_tin():
    bang = [diem(0.25, 0.8, 0.10, 0.13, 0.90),      # thang
            diem(0.50, 0.6, 0.30, 0.27, 0.80),      # thua
            diem(0.75, 0.2, 0.52, 0.50, 0.55),      # thua
            GOC]
    ra = _bao_cao(bang, "phat_trien")
    assert "Chưa chứng minh được bốn dấu hiệu mang thông tin" in ra
    assert "có mang thông tin." not in ra


def test_thang_da_so_thi_moi_duoc_ket_luan_la_co_thong_tin():
    bang = [diem(0.25, 0.8, 0.08, 0.13, 0.55),
            diem(0.50, 0.6, 0.20, 0.27, 0.54),
            diem(0.75, 0.2, 0.45, 0.50, 0.52),
            GOC]
    ra = _bao_cao(bang, "phat_trien")
    assert "có mang thông tin" in ra
    assert "Chưa chứng minh được" not in ra


def test_thang_thua_ngang_nhau_van_la_CHUA_chung_minh_duoc():
    """Hoa khong phai thang. Nguong phai nghieng ve phia than trong."""
    bang = [diem(0.25, 0.8, 0.10, 0.13, 0.90),
            diem(0.50, 0.6, 0.30, 0.27, 0.80),
            GOC]
    assert "Chưa chứng minh được" in _bao_cao(bang, "phat_trien")


# ------------------------------------------------------ chon diem hoat dong

def test_KHONG_chon_diem_day_xuong_toan_bo():
    """Bay lon nhat cua du an. Nguong 0,00 co loi bang 0 vi than bai trong —
    no khong duoc phep duoc goi la 'nguong tot nhat'."""
    bang = [diem(0.00, 1.0, 0.00, 0.00, 1.00),
            diem(0.75, 0.2, 0.52, 0.55, 0.55),
            GOC]
    ra = _bao_cao(bang, "phat_trien")
    assert "ngưỡng tốt nhất là **0.75**" in ra
    assert "**0.00**" not in ra


def test_loai_nguong_lam_bo_sot_tang_qua_20_phan_tram():
    bang = [diem(0.50, 0.6, 0.20, 0.25, 0.80),   # bo sot 0,50 -> 0,80 = +60%
            diem(0.75, 0.2, 0.52, 0.55, 0.55),   # +10%, dat
            GOC]
    ra = _bao_cao(bang, "phat_trien")
    assert "ngưỡng tốt nhất là **0.75**" in ra


def test_khong_nguong_nao_dat_thi_noi_thang_la_khong_dat():
    bang = [diem(0.50, 0.6, 0.20, 0.25, 0.90), GOC]
    ra = _bao_cao(bang, "phat_trien")
    assert "Không ngưỡng nào thoả điều kiện công bằng" in ra
    assert "không phải chỗ để hạ ngưỡng cho vừa" in ra


def test_bao_cao_luon_neu_cot_ngau_nhien_o_diem_duoc_chon():
    """Chon xong ma khong doi chieu voi chon bua thi ban doc se tuong la thang."""
    bang = [diem(0.75, 0.2, 0.52, 0.49, 0.55), GOC]
    ra = _bao_cao(bang, "phat_trien")
    assert "chọn bừa cùng tỷ lệ để lại" in ra
    assert "không đóng góp gì" in ra
