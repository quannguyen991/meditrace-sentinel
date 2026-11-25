# -*- coding: utf-8 -*-
"""Bộ kiểm thử cho Phân tích Audio Segments và Phân bố Độ dài V2."""
import pytest

from src.audio.phan_tich_am_thanh_v2 import (
    dem_am_tiet_tieng_viet,
    mo_hinh_hoa_moc_thoi_gian_ca,
    phan_tich_tap_ca_v2,
)


def test_dem_am_tiet_tieng_viet():
    """Kiểm tra đếm âm tiết tiếng Việt chuẩn xác."""
    assert dem_am_tiet_tieng_viet("Tôi bị đau bụng quanh rốn từ chiều qua") == 9
    assert dem_am_tiet_tieng_viet("Dạ, không.") == 2
    assert dem_am_tiet_tieng_viet("") == 1


def test_mo_hinh_hoa_moc_thoi_gian_ca():
    """Kiểm tra tính đơn điệu và không chồng lấn của mốc thời gian."""
    cac_luot = [
        {"nguoi_noi": "Bác sĩ", "noi_dung": "Chào anh, hôm nay anh thấy khó chịu ở đâu?"},
        {"nguoi_noi": "Bệnh nhân", "noi_dung": "Dạ tôi bị sốt và ho đờm từ tối qua."},
        {"nguoi_noi": "Bác sĩ", "noi_dung": "Anh có đo nhiệt độ chưa?"},
        {"nguoi_noi": "Bệnh nhân", "noi_dung": "Dạ đo nhiệt kế là 38 độ 5 ạ."}
    ]
    timeline, tong_thoi_luong_s = mo_hinh_hoa_moc_thoi_gian_ca(cac_luot, toc_do_am_tiet_s=4.2)

    assert len(timeline) == 4
    assert tong_thoi_luong_s > 0

    # Kiểm tra tính đơn điệu thời gian (start_ms < end_ms và end_ms < start_ms tiếp theo)
    for i in range(len(timeline)):
        item = timeline[i]
        assert item["start_ms"] < item["end_ms"]
        assert item["duration_s"] > 0
        if i > 0:
            assert item["start_ms"] >= timeline[i - 1]["end_ms"]  # Phải có khoảng lặng chuyển lượt


def test_phan_tich_tap_ca_v2():
    """Kiểm tra tổng hợp thống kê phân bố trên danh sách ca."""
    cac_ca = [
        {
            "id": 1,
            "turns": [
                {"nguoi_noi": "Bác sĩ", "noi_dung": "Chào chị, cháu bé bị làm sao?"},
                {"nguoi_noi": "Người nhà", "noi_dung": "Dạ cháu nó bị nôn trớ 3 lần từ sáng nay."},
                {"nguoi_noi": "Bác sĩ", "noi_dung": "Bé có sốt không chị?"},
                {"nguoi_noi": "Người nhà", "noi_dung": "Dạ không thấy sốt ạ."}
            ],
            "dap_an": [
                {"luot": 2, "noi_dung": "nôn trớ 3 lần", "trich_dan": ["nôn trớ 3 lần"]}
            ]
        }
    ]

    bc = phan_tich_tap_ca_v2(cac_ca)
    assert bc.tong_so_ca == 1
    assert bc.tong_so_luot == 4
    assert bc.luot_trung_binh_tren_ca == 4.0
    assert bc.thoi_luong_ca_trung_binh_s > 0
    assert bc.tong_so_audio_spans == 1
    assert bc.ty_le_span_hop_le_100 == 1.0
