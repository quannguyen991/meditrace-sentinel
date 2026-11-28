# -*- coding: utf-8 -*-
"""Kiểm `noi_dung` so với câu trích của chính nó (nguyên mẫu, chưa nối vào đường ống)."""
from src.duong_ong.b4_kiem_noi_dung_trich import kiem_noi_dung_theo_trich as kiem


def test_chep_loi_asr():
    # Chép nguyên chữ không dấu của ASR: có trong câu trích nhưng không phải chữ viết đúng.
    ra = kiem("the trang beo", ["the trang beo phi do mot"])
    assert "chep_loi_asr" in ra


def test_doi_chu():
    ra = kiem("ngột mũi", ["con bị nghẹt mũi mấy hôm nay"])
    assert "tu_khong_co_trong_trich" in ra


def test_nhan_sai_tren_dung_trich():
    ra = kiem("đau bụng", ["bé đi ngoài toàn nước"])
    assert "nhan_khac_trich" in ra
    assert "tu_khong_co_trong_trich" in ra


def test_bo_mat_bo_nghia():
    ra = kiem("đau cơ", ["tôi đau cơ nặng hơn sau khi ăn"])
    assert "bo_mat_bo_nghia" in ra


def test_bo_nghia_ve_dem():
    assert "bo_mat_bo_nghia" in kiem("ho", ["con ho về đêm"])


def test_du_nghia_thi_sach():
    assert kiem("đau cơ nặng hơn sau khi ăn", ["tôi đau cơ nặng hơn sau khi ăn"]) == []


def test_so_bang_chu():
    assert kiem("ho 3 ngày", ["con ho ba ngày nay"]) == []


def test_bo_chu_chi_nguoi():
    assert kiem("dị ứng penicillin", ["tôi dị ứng penicillin"]) == []


def test_khoi_phuc_dau_tu_trich_khong_dau_khong_bi_phat():
    # Trích ASR không dấu, nội dung đã khôi phục dấu: được trích hỗ trợ, không báo.
    assert kiem("đau bụng", ["be dau bung tu sang"]) == []


def test_chu_latin_va_don_vi_khong_bi_coi_la_loi_asr():
    assert kiem("uống paracetamol 500 mg", ["uống paracetamol năm trăm mg"]) == []


def test_nhieu_trich_gop_lai():
    # Hai câu trích: vế bổ nghĩa ở câu thứ hai vẫn bị tính.
    assert "bo_mat_bo_nghia" in kiem("sốt cao", ["bé sốt", "sốt cao về chiều"])


def test_rong_khong_loi():
    assert kiem("", ["abc"]) == []
    assert kiem("sốt", []) == []
