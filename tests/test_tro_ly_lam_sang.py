# -*- coding: utf-8 -*-
"""Kiểm thử unit test cho Trợ lý Gợi ý Câu hỏi Lâm sàng Thông minh."""

from src.tro_ly_lam_sang import ActiveClinicalClarificationAgent


def test_phat_hien_khoang_trong_dau_bung():
    # Bệnh nhân chỉ nói "đau bụng" mà không nói ở đâu, tính chất thế nào
    hoi_thoai = (
        "Bác sĩ: Bác thấy khó chịu trong người thế nào?\n"
        "Bệnh nhân: Tôi bị đau bụng từ tối qua bác sĩ ạ."
    )

    kq = ActiveClinicalClarificationAgent.phan_tich_khoang_trong(hoi_thoai)
    ma_goi_y = [g.ma_goi_y for g in kq.danh_sach_goi_y]

    assert "GAP_DAU_VI_TRI_BUNG" in ma_goi_y
    assert "GAP_DAU_TINH_CHAT" in ma_goi_y
    assert kq.tong_so_khoang_trong >= 2


def test_phat_hien_khoang_trong_sot_va_ho():
    # Khai sốt và ho nhưng không có nhiệt độ, không rõ đờm
    hoi_thoai = (
        "Bác sĩ: Bác sốt mấy hôm rồi?\n"
        "Bệnh nhân: Dạ tôi sốt và ho hai hôm nay."
    )

    kq = ActiveClinicalClarificationAgent.phan_tich_khoang_trong(hoi_thoai)
    ma_goi_y = [g.ma_goi_y for g in kq.danh_sach_goi_y]

    assert "GAP_SOT_NHIET_DO" in ma_goi_y
    assert "GAP_HO_TINH_CHAT_DOM" in ma_goi_y


def test_phat_hien_thieu_lieu_thuoc_va_thai_ky():
    # Nữ 28 tuổi, khai uống amlodipin nhưng không rõ hàm lượng và chưa hỏi thai kỳ
    hoi_thoai = (
        "Bệnh nhân: Tôi đang uống amlodipin điều trị huyết áp."
    )
    thong_tin_bn = {
        "gioi_tinh": "nữ",
        "tuoi": 28
    }

    kq = ActiveClinicalClarificationAgent.phan_tich_khoang_trong(
        hoi_thoai,
        thong_tin_benh_nhan=thong_tin_bn
    )
    ma_goi_y = [g.ma_goi_y for g in kq.danh_sach_goi_y]

    assert "GAP_THUOC_HAM_LUONG_AMLODIPIN" in ma_goi_y
    assert "GAP_NU_THAI_KY" in ma_goi_y
