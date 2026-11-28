# -*- coding: utf-8 -*-
"""Kiểm thử unit test cho Trợ lý Gợi ý Câu hỏi Lâm sàng Thông minh."""

from src.cong_cu_lam_sang.goi_y_cau_hoi_socrates import ActiveClinicalClarificationAgent


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


# ── Bám lời thoại (28/11/2026) ─────────────────────────────────────────────

def _ma(hoi_thoai, **k):
    kq = ActiveClinicalClarificationAgent.phan_tich_khoang_trong(hoi_thoai, **k)
    return [g.ma_goi_y for g in kq.danh_sach_goi_y]


def test_tu_ho_nam_trong_tu_khac_khong_bat_goi_y_ho():
    hoi_thoai = ("Bác sĩ: Chị cho tôi hỏi, dạo này thế nào?\n"
                 "Bệnh nhân: Dạ tôi thấy khó thở, mệt, không thoải mái ạ.")
    assert "GAP_HO_TINH_CHAT_DOM" not in _ma(hoi_thoai)


def test_cau_hoi_cua_bac_si_va_cau_phu_dinh_khong_bat_goi_y():
    hoi_thoai = ("Bác sĩ: Anh có ho hay sốt không?\n"
                 "Bệnh nhân: Dạ không ho, không sốt gì cả.")
    ma = _ma(hoi_thoai)
    assert "GAP_HO_TINH_CHAT_DOM" not in ma and "GAP_SOT_NHIET_DO" not in ma


def test_loi_nguoi_khac_khong_bat_goi_y():
    hoi_thoai = ("Bệnh nhân: Tôi đau thượng vị âm ỉ.\n"
                 "Người khác: Còn tôi thì sốt với ho mấy hôm nay.")
    ma = _ma(hoi_thoai)
    assert "GAP_SOT_NHIET_DO" not in ma and "GAP_HO_TINH_CHAT_DOM" not in ma


def test_goi_y_mang_luot_dan_va_trich_dan():
    hoi_thoai = ("Bác sĩ: Chị bị sao?\n"
                 "Người nhà: Dạ cháu nhà tôi ho ba hôm nay, đêm ho nhiều.")
    kq = ActiveClinicalClarificationAgent.phan_tich_khoang_trong(hoi_thoai)
    g = next(g for g in kq.danh_sach_goi_y if g.ma_goi_y == "GAP_HO_TINH_CHAT_DOM")
    assert g.luot_dan == [2]
    assert "ho ba hôm nay" in g.trich_dan
    assert g.nguon == "lời người nhà"


def test_thuoc_trong_cau_di_ung_khong_hoi_ham_luong():
    hoi_thoai = "Bệnh nhân: Tôi bị dị ứng aspirin, nổi mề đay."
    assert "GAP_THUOC_HAM_LUONG_ASPIRIN" not in _ma(hoi_thoai)


def test_nguoi_nha_ke_ve_chinh_minh_khong_bat_goi_y():
    hoi_thoai = ("Bệnh nhân: Tôi đau thượng vị âm ỉ.\n"
                 "Người nhà: Còn tôi thì bị ho mấy hôm, đang uống paracetamol.")
    ma = _ma(hoi_thoai)
    assert "GAP_HO_TINH_CHAT_DOM" not in ma


def test_da_noi_ho_dom_thi_khong_hoi_lai():
    assert "GAP_HO_TINH_CHAT_DOM" not in _ma("Bệnh nhân: Tôi ho có đờm vàng ba ngày nay.")


def test_thai_ky_ghi_nguon_ho_so():
    kq = ActiveClinicalClarificationAgent.phan_tich_khoang_trong(
        "Bệnh nhân: Tôi đau đầu.", thong_tin_benh_nhan={"gioi_tinh": "nữ", "tuoi": 30})
    g = next(g for g in kq.danh_sach_goi_y if g.ma_goi_y == "GAP_NU_THAI_KY")
    assert g.nguon == "hồ sơ" and "30 tuổi" in g.trich_dan
