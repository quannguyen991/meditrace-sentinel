# -*- coding: utf-8 -*-
"""Hoi quy ro ri PHI truoc khi gui may xa (GPU HoaiDuc).

Moi ca la mot cau tieng Viet; van ban sau khu dinh danh KHONG duoc con chuoi nhay cam
va kiem_tra_con_sot phai rong. Them cac ca chong bat nham (so lieu lam sang, tu thuong).
"""
import re

import pytest

from src.khu_dinh_danh import ClinicalDeidentifier as CD


def _chu_so(s):
    return re.sub(r"\D", "", s)


# ----------------------------------------------------------------- so dien thoai / dinh danh
@pytest.mark.parametrize("cau,so", [
    ("Số của tôi là 0912345678 nhé", "0912345678"),
    ("Số của tôi là 0912 345 678 nhé", "0912345678"),
    ("Số của tôi là 0912.345.678 nhé", "0912345678"),
    ("Số của tôi là 0912-345-678 nhé", "0912345678"),
    ("Gọi cho con tôi số +84 912345678", "84912345678"),
    ("Gọi cho con tôi số +84912345678", "84912345678"),
    ("Gọi số 84 912 345 678 giúp tôi", "84912345678"),
    ("số máy là 0 9 1 2 3 4 5 6 7 8 ạ", "0912345678"),
    ("số máy là không chín một hai ba bốn năm sáu bảy tám ạ", "0912345678"),
    ("Điện thoại bàn nhà tôi 024 3825 1234", "02438251234"),
    ("Số 098 765 4321 là của vợ tôi", "0987654321"),
    ("Căn cước của tôi 001090012345 ạ", "001090012345"),
    ("cccd 001 090 012 345", "001090012345"),
    ("mã hồ sơ 123456789012 ở viện cũ", "123456789012"),
])
def test_so_dai_bi_che(cau, so):
    kq = CD.an_danh_van_ban(cau)
    assert so not in _chu_so(kq.van_ban_da_an_danh), kq.van_ban_da_an_danh
    assert CD.kiem_tra_con_sot(kq.van_ban_da_an_danh) == []
    # giai ma 2 chieu khoi phuc dung cau goc
    assert CD.giai_ma_van_ban(kq.van_ban_da_an_danh, kq.bang_anh_xa_giai_ma) == CD.chuan_hoa_so_noi_tieng_viet(cau)


# ----------------------------------------------------------------- ten viet thuong (ASR)
@pytest.mark.parametrize("cau,ten", [
    ("tôi tên là nguyễn văn an năm nay sáu mươi tuổi", "nguyễn văn an"),
    ("tên tôi là trần thị bình, tôi bị đau bụng", "trần thị bình"),
    ("dạ cháu tên hoàng minh đức ạ", "hoàng minh đức"),
    ("bác sĩ ơi tôi là phạm văn hùng đây", "phạm văn hùng"),
    ("họ tên lê thị hoa", "lê thị hoa"),
    ("Tôi tên là Trần Thị Mai.", "Trần Thị Mai"),
])
def test_ten_viet_thuong_bi_che(cau, ten):
    kq = CD.an_danh_van_ban(cau)
    assert ten.lower() not in kq.van_ban_da_an_danh.lower(), kq.van_ban_da_an_danh
    assert CD.kiem_tra_con_sot(kq.van_ban_da_an_danh) == []


# ----------------------------------------------------------------- ten rieng khi biet ho ten day du
@pytest.mark.parametrize("cau,lo", [
    ("Anh An đau bụng từ hôm qua", "An đau"),
    ("anh an đau bụng từ hôm qua", " an "),
    ("Bác Minh uống thuốc đều không?", "Minh"),
    ("Hôm nay An thấy đỡ hơn", "An"),
    ("Chào ông Nguyễn Văn An", "Nguyễn Văn An"),
])
def test_ten_rieng_va_danh_xung_bi_che(cau, lo):
    ten = "Bác Minh" in cau and "Trần Văn Minh" or "Nguyễn Văn An"
    kq = CD.an_danh_van_ban(cau, ten_benh_nhan=ten)
    assert lo not in kq.van_ban_da_an_danh, kq.van_ban_da_an_danh
    # giai ma phuc hoi nguyen van (khong bien "Anh An" thanh "Anh Nguyễn Văn An");
    # chu hoa/thuong cua ten co the theo ban goc trong bang anh xa
    assert CD.giai_ma_van_ban(kq.van_ban_da_an_danh, kq.bang_anh_xa_giai_ma).lower() == cau.lower()


# ----------------------------------------------------------------- chong bat nham
def test_khong_nuot_tu_dau_cau_sau_ten():
    kq = CD.an_danh_van_ban("Tôi tên là Trần Thị Mai Sau đó tôi bị sốt")
    assert "Sau đó tôi bị sốt" in kq.van_ban_da_an_danh
    assert "Mai" not in kq.van_ban_da_an_danh


@pytest.mark.parametrize("cau", [
    "Huyết áp 120/80, mạch 84 lần/phút, nhiệt độ 38,5 độ",
    "Uống paracetamol 500 mg ngày 3 lần, mỗi lần 1 viên",
    "Đường huyết 7.8 mmol/L, HbA1c 8.1%",
    "Huyết áp đo ba lần: 140 90, 135 85, 130 80",
    "Bệnh nhân an toàn, tâm thu bình thường",
    "tôi là người nhà bệnh nhân",
])
def test_khong_che_so_lieu_lam_sang(cau):
    kq = CD.an_danh_van_ban(cau, ten_benh_nhan="Nguyễn Văn An")
    assert kq.van_ban_da_an_danh == cau
    assert CD.kiem_tra_con_sot(cau) == []


def test_khong_con_ti_le_an_toan_gia():
    kq = CD.an_danh_van_ban("không có gì")
    assert not hasattr(kq, "ti_le_an_toan_bao_mat")


# ----------------------------------------------------------------- kiem tra con sot (fail-closed)
@pytest.mark.parametrize("cau", [
    "gọi 0912 345 678",
    "tôi tên là nguyễn văn an",
    "+84 912 345 678",
])
def test_kiem_tra_con_sot_bat_duoc_van_ban_tho(cau):
    assert CD.kiem_tra_con_sot(cau) != []
