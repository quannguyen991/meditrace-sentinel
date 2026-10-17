# -*- coding: utf-8 -*-
"""Test suite cho Trụ cột 3: Động cơ Đa bệnh lý trong tests/test_da_benh_ly.py."""
import random
import pytest
from src.da_benh_ly import MultimorbidityEngine, BENH_NEN_MAN_TINH


def test_tao_ca_da_benh_ly_nguoi_lon_co_benh_nen():
    benh_chinh = {
        "ten": "cơn đau thắt ngực không ổn định",
        "nhom": "người lớn",
        "dien_tien": "cấp"
    }
    rng = random.Random(42)
    ca = MultimorbidityEngine.tao_ca_da_benh_ly(benh_chinh, rng=rng, ty_le_co_benh_nen=1.0)
    
    assert ca.benh_chinh["ten"] == "cơn đau thắt ngực không ổn định"
    assert len(ca.benh_nen) >= 1
    # Bệnh nền không được trùng với bệnh chính
    assert not any(b["ten"] == ca.benh_chinh["ten"] for b in ca.benh_nen)
    assert len(ca.thuoc_nen_dang_dung) >= 1
    assert len(ca.luot_hoi_thoai_bo_sung) == 2
    assert "Bác sĩ" in ca.luot_hoi_thoai_bo_sung[0][0]
    assert "Bệnh nhân" in ca.luot_hoi_thoai_bo_sung[1][0]


def test_ghep_luot_thoai_benh_nen_vao_hoi_thoai_goc():
    ht_goc = (
        "Bác sĩ: Chào bác, hôm nay bác đi khám vì sao?\n"
        "Bệnh nhân: Tôi bị đau tức ngực dữ dội từ sáng nay.\n"
        "Bác sĩ: Để tôi nghe tim phổi cho bác xem thế nào.\n"
        "Bác sĩ: Nhịp tim nhanh, huyết áp 150/90 mmHg."
    )
    benh_chinh = {"ten": "sốt xuất huyết", "nhom": "người lớn"}
    rng = random.Random(10)
    ca = MultimorbidityEngine.tao_ca_da_benh_ly(benh_chinh, rng=rng, ty_le_co_benh_nen=1.0)
    
    ht_moi = MultimorbidityEngine.ghep_vao_hoi_thoai_goc(ht_goc, ca)
    assert "bệnh lý nền" in ht_moi or "thuốc" in ht_moi
    assert len(ht_moi.split("\n")) > len(ht_goc.split("\n"))
