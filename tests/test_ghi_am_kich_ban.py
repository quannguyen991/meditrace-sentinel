# -*- coding: utf-8 -*-
from tools.ghi_am_kich_ban import tao_kich_ban

CA = {"id": "c1", "input": "Bác sĩ: Chị bị gì?\nNgười nhà: Cháu sốt ba hôm.\nBệnh nhân: Con mệt lắm."}


def test_kich_ban_tach_vai_va_danh_so_luot():
    kb = tao_kich_ban(CA)
    assert kb["vai"] == ["Bác sĩ", "Người nhà", "Bệnh nhân"]
    assert "[1] Bác sĩ: Chị bị gì?" in kb["van"]
    assert "[3] Bệnh nhân: Con mệt lắm." in kb["van"]


def test_kich_ban_co_nhac_dong_y_va_khong_dung_ten_that():
    kb = tao_kich_ban(CA)
    assert "đồng ý" in kb["van"] and "không nói tên thật" in kb["van"]
