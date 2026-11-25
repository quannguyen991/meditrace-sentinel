# -*- coding: utf-8 -*-
"""
tests/test_kiem_dinh_trich_dan_v2.py — Kiểm thử tự động bảo toàn 100% trích dẫn nguyên văn (Exact Substring)
trên bộ dữ liệu MediTrace V2 Mở rộng 5.000 ca (Bất biến số 4 MediTrace).
"""

from pathlib import Path
import pytest
from tools.kiem_tra_trich_dan_v2 import kiem_dinh_tap_du_lieu, GOC_DU_AN


TEP_V2 = GOC_DU_AN / "data" / "hoi_thoai_viet_v2_mo_rong.jsonl"


def test_tep_v2_ton_tai_va_du_5000_ca():
    """Kiểm tra tệp dữ liệu V2 mở rộng tồn tại trên đĩa và có đúng 5.000 ca lâm sàng."""
    assert TEP_V2.exists(), f"Tệp {TEP_V2} không tồn tại!"
    assert TEP_V2.stat().st_size > 30_000_000, "Dung lượng tệp V2 quá nhỏ!"
    with open(TEP_V2, "r", encoding="utf-8") as f:
        tong_so_ca = sum(1 for line in f if line.strip())
    assert tong_so_ca == 5000, f"Số ca thực tế là {tong_so_ca}, kỳ vọng đúng 5.000 ca!"


def test_100_phan_tram_trich_dan_la_chuoi_con_nguyen_van_v2():
    """Bất biến số 4: 100.0000% trích dẫn là chuỗi con nguyên văn của đúng lượt thoại."""
    kq = kiem_dinh_tap_du_lieu(TEP_V2, so_ca_kiem_trie=50)

    assert kq["tong_so_ca"] == 5000
    assert kq["tong_so_menh_de"] >= 40000
    assert kq["tong_so_trich_dan"] >= 40000

    # Tuyệt đối 0 lỗi
    assert kq["tong_loi"] == 0, f"Phát hiện lỗi trích dẫn: {kq['chi_tiet_loi']}"
    assert kq["ty_le_khop_tuyet_doi_pct"] == 100.0, "Tỷ lệ khớp không đạt 100.0000%!"
    assert kq["so_khop_tuyet_doi"] == kq["tong_so_trich_dan"]

    # Khớp Substring Trie trên tập mẫu
    assert kq["so_khop_trie"] == kq["so_trich_dan_kiem_trie"]
    assert kq["ty_le_khop_trie_pct"] == 100.0


def test_khong_co_trich_dan_rong_hoac_ngoai_khoang():
    """Không có trích dẫn rỗng và không có chỉ số lượt vượt ngoài hội thoại."""
    kq = kiem_dinh_tap_du_lieu(TEP_V2, so_ca_kiem_trie=10)
    assert len(kq["chi_tiet_loi"]["do_dai_khong_khop"]) == 0
    assert len(kq["chi_tiet_loi"]["luot_ngoai_khoang"]) == 0
    assert len(kq["chi_tiet_loi"]["trich_dan_rong"]) == 0
    assert len(kq["chi_tiet_loi"]["khong_phai_chuoi_con"]) == 0
    assert len(kq["chi_tiet_loi"]["khong_khop_trie"]) == 0


def test_phan_bo_muc_va_he_co_quan_hop_le():
    """Kiểm tra phân bố đầy đủ các mục lâm sàng và hệ cơ quan trong bộ dữ liệu V2."""
    kq = kiem_dinh_tap_du_lieu(TEP_V2, so_ca_kiem_trie=0)
    muc_dict = kq["phan_bo"]["muc"]
    # Các mục lâm sàng thực tế trong V2 (theo đặt tên trong mô hình)
    muc_chuan = {
        "LÝ DO KHÁM BỆNH",
        "BỆNH SỬ HIỆN TẠI",
        "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI",
        "THUỐC ĐANG DÙNG",
        "KHÁM LÂM SÀNG",
    }
    for muc in muc_chuan:
        assert muc in muc_dict, f"Thiếu mục lâm sàng chuẩn: {muc}. Có: {list(muc_dict.keys())}"
        assert muc_dict[muc] > 0
