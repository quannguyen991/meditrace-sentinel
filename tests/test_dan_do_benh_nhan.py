# -*- coding: utf-8 -*-
"""Kiểm thử tự động cho Trình Sinh Bản Hướng Dẫn & Dặn Dò Người Bệnh (src/dan_do_benh_nhan.py)."""

import pytest
from src.dan_do_benh_nhan import (
    phan_loai_lich_uong_thuoc,
    sinh_ban_dan_do_benh_nhan,
    dinh_dang_van_ban_dan_do
)


def test_phan_loai_lich_uong_thuoc_chinh_xac():
    """Kiểm tra việc tách các buổi uống thuốc sáng, trưa, chiều/tối và trước ngủ."""
    danh_sach = [
        "Amlodipine 5mg uống 1 viên buổi sáng sau ăn",
        "Paracetamol 500mg ngày 3 lần mỗi lần 1 viên",
        "Metformin 850mg ngày 2 lần uống trong bữa ăn",
        "Seduxen 5mg 1 viên uống trước khi đi ngủ",
        "Nexium 40mg 1 viên trước khi ăn 30 phút"
    ]
    
    lich = phan_loai_lich_uong_thuoc(danh_sach)
    
    # Sáng phải có: Amlodipine, Paracetamol (liều 1), Metformin (liều 1), Nexium
    ten_thuoc_sang = [t["ten_thuoc"] for t in lich["sang"]]
    assert any("Amlodipine" in t for t in ten_thuoc_sang)
    assert any("Nexium" in t for t in ten_thuoc_sang)
    assert any("Paracetamol" in t for t in ten_thuoc_sang)
    assert any("Metformin" in t for t in ten_thuoc_sang)
    
    # Nexium phải có cách dùng trước ăn
    nexium_entry = [t for t in lich["sang"] if "Nexium" in t["ten_thuoc"]][0]
    assert "TRƯỚC khi ăn" in nexium_entry["cach_dung"]
    
    # Trưa phải có: Paracetamol (liều 2)
    ten_thuoc_trua = [t["ten_thuoc"] for t in lich["trua"]]
    assert any("Paracetamol" in t for t in ten_thuoc_trua)
    
    # Tối phải có: Metformin (liều 2), Paracetamol (liều 3)
    ten_thuoc_toi = [t["ten_thuoc"] for t in lich["toi"]]
    assert any("Metformin" in t for t in ten_thuoc_toi)
    
    # Trước ngủ phải có Seduxen
    assert len(lich["truoc_ngu"]) == 1
    assert "Seduxen" in lich["truoc_ngu"][0]["ten_thuoc"]


def test_sinh_ban_dan_do_benh_tang_huyet_ap():
    """Kiểm tra sinh bản dặn dò cho bệnh nhân Tăng huyết áp."""
    ban_dan_do = sinh_ban_dan_do_benh_nhan(
        ten_benh_nhan="Nguyễn Văn A",
        chan_doan="Tăng huyết áp nguyên phát độ 2",
        danh_sach_thuoc=["Amlodipine 5mg sáng 1 viên sau ăn", "Losartan 50mg sáng 1 viên"],
        ngay_tai_kham="Sau 14 ngày"
    )
    
    assert ban_dan_do["nguoi_benh"] == "Nguyễn Văn A"
    assert "Áp lực máu trong lòng mạch" in ban_dan_do["giai_thich_benh_don_gian"]
    
    # Chế độ ăn phải kiêng mặn
    kieng_cu = ban_dan_do["che_do_an_uong"]["kieng_cu"]
    assert any("Ăn mặn" in k or "mắm tôm" in k for k in kieng_cu)
    
    # Phải có dấu hiệu đỏ cấp cứu
    assert len(ban_dan_do["dau_hieu_do_can_cap_cuu"]) >= 5
    assert any("tức nặng ngực" in d for d in ban_dan_do["dau_hieu_do_can_cap_cuu"])


def test_sinh_ban_dan_do_benh_dai_thao_duong():
    """Kiểm tra sinh bản dặn dò cho bệnh nhân Đái tháo đường."""
    ban_dan_do = sinh_ban_dan_do_benh_nhan(
        ten_benh_nhan="Trần Thị B",
        chan_doan="Đái tháo đường típ 2",
        danh_sach_thuoc=["Metformin 500mg ngày 2 lần sau ăn"]
    )
    
    assert "Lượng đường trong máu" in ban_dan_do["giai_thich_benh_don_gian"]
    kieng_cu = ban_dan_do["che_do_an_uong"]["kieng_cu"]
    assert any("Bánh kẹo ngọt" in k for k in kieng_cu)


def test_dinh_dang_van_ban_in_an():
    """Kiểm tra chuyển đổi cấu trúc bản dặn dò sang định dạng văn bản in hoàn chỉnh."""
    ban_dan_do = sinh_ban_dan_do_benh_nhan(
        ten_benh_nhan="Lê Hoàng C",
        chan_doan="Viêm phế quản cấp",
        danh_sach_thuoc=["Augmentin 1g ngày 2 lần sau ăn", "Paracetamol 500mg khi sốt"],
        ngay_tai_kham="Sau 5 ngày"
    )
    
    van_ban = dinh_dang_van_ban_dan_do(ban_dan_do)
    assert "BẢN HƯỚNG DẪN ĐIỀU TRỊ & DẶN DÒ NGƯỜI BỆNH" in van_ban
    assert "Kính gửi: Lê Hoàng C" in van_ban
    assert "Chẩn đoán: Viêm phế quản cấp" in van_ban
    assert "1. HIỂU VỀ TÌNH TRẠNG SỨC KHỎE CỦA BÁC:" in van_ban
    assert "2. LỊCH UỐNG THUỐC HÀNG NGÀY:" in van_ban
    assert "3. CHẾ ĐỘ ĂN UỐNG & SINH HOẠT HỢP LÝ:" in van_ban
    assert "5. 🚨 DẤU HIỆU CẦN ĐẾN BỆNH VIỆN CẤP CỨU NGAY LẬP TỨC:" in van_ban
    assert "LỊCH TÁI KHÁM: Sau 5 ngày" in van_ban
