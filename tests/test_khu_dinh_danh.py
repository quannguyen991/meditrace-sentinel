# -*- coding: utf-8 -*-
"""Kiểm thử tự động cho Module Khử nhận dạng thông tin cá nhân y tế PII/PHI."""

from src.khu_dinh_danh import ClinicalDeidentifier


def test_an_danh_thong_tin_co_ban():
    hoi_thoai = (
        "Bác sĩ: Chào bác, tôi xin số điện thoại để liên hệ tái khám nhé.\n"
        "Bệnh nhân: Dạ, số điện thoại của tôi là 0912345678, email là nguyenvana@gmail.com.\n"
        "Bác sĩ: Bác cho tôi xin số căn cước công dân và bảo hiểm y tế luôn ạ.\n"
        "Bệnh nhân: Căn cước công dân của tôi là 001090012345, thẻ bảo hiểm y tế số GD4010123456789."
    )

    kq = ClinicalDeidentifier.an_danh_van_ban(hoi_thoai)
    
    # Không còn số điện thoại, email, CCCD, BHYT gốc trong văn bản đã ẩn danh
    assert "0912345678" not in kq.van_ban_da_an_danh
    assert "nguyenvana@gmail.com" not in kq.van_ban_da_an_danh
    assert "001090012345" not in kq.van_ban_da_an_danh
    assert "GD4010123456789" not in kq.van_ban_da_an_danh

    # Có token thay thế
    assert "[SDT_1]" in kq.van_ban_da_an_danh
    assert "[EMAIL_1]" in kq.van_ban_da_an_danh
    assert "[CCCD_1]" in kq.van_ban_da_an_danh
    assert "[BHYT_1]" in kq.van_ban_da_an_danh

    # Giải mã 2 chiều phục hồi chính xác
    vb_khoi_phuc = ClinicalDeidentifier.giai_ma_van_ban(kq.van_ban_da_an_danh, kq.bang_anh_xa_giai_ma)
    assert "0912345678" in vb_khoi_phuc
    assert "nguyenvana@gmail.com" in vb_khoi_phuc
    assert "001090012345" in vb_khoi_phuc
    assert "GD4010123456789" in vb_khoi_phuc


def test_an_danh_ten_benh_nhan_va_nguoi_nha():
    hoi_thoai = (
        "Bác sĩ: Chào bác Trần Văn Minh, hôm nay ai đi cùng bác?\n"
        "Bệnh nhân: Tôi đi cùng con gái là Trần Thị Lan bác sĩ ạ.\n"
        "Bác sĩ: Bác Minh dạo này uống thuốc huyết áp đều không?"
    )

    kq = ClinicalDeidentifier.an_danh_van_ban(
        hoi_thoai,
        ten_benh_nhan="Trần Văn Minh",
        ten_than_nhan=["Trần Thị Lan"]
    )

    assert "Trần Văn Minh" not in kq.van_ban_da_an_danh
    assert "Trần Thị Lan" not in kq.van_ban_da_an_danh
    assert "[BENH_NHAN]" in kq.van_ban_da_an_danh
    assert "[NGUOI_NHA_1]" in kq.van_ban_da_an_danh

    # Giải mã lại
    phuc_hoi = ClinicalDeidentifier.giai_ma_van_ban(kq.van_ban_da_an_danh, kq.bang_anh_xa_giai_ma)
    assert "Trần Văn Minh" in phuc_hoi
    assert "Trần Thị Lan" in phuc_hoi


def test_an_danh_ngay_sinh_va_dia_chi():
    hoi_thoai = (
        "Bệnh nhân: Tôi sinh ngày 15/08/1965, địa chỉ trú tại số 15 đường Giải Phóng, quận Đống Đa, Hà Nội."
    )

    kq = ClinicalDeidentifier.an_danh_van_ban(hoi_thoai)
    assert "15/08/1965" not in kq.van_ban_da_an_danh
    assert "[NGAY_SINH_1]" in kq.van_ban_da_an_danh
    assert "[DIA_CHI_1]" in kq.van_ban_da_an_danh

    phuc_hoi = ClinicalDeidentifier.giai_ma_van_ban(kq.van_ban_da_an_danh, kq.bang_anh_xa_giai_ma)
    assert "15/08/1965" in phuc_hoi
    assert "quận Đống Đa" in phuc_hoi
