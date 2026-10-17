# -*- coding: utf-8 -*-
"""Kiểm thử tự động cho Động cơ Hiệu chỉnh Liều Thuốc theo Chức năng Thận & Gan (src/hieu_chinh_lieu.py)."""

import pytest
from src.hieu_chinh_lieu import (
    tinh_crcl,
    chuyen_umol_sang_mg_dl,
    phan_do_suy_than,
    kiem_tra_hieu_chinh_lieu
)


def test_tinh_crcl_va_chuyen_doi_don_vi():
    """Kiểm tra công thức Cockcroft-Gault tính CrCl và chuyển đổi micromol/L sang mg/dL."""
    # Nam 60 tuổi, 70kg, Creatinine 1.0 mg/dL: CrCl = (80 * 70) / 72 = 77.8 mL/phút
    crcl_nam = tinh_crcl(tuoi=60, can_nang_kg=70.0, creatinine_mg_dl=1.0, la_nu=False)
    assert crcl_nam == 77.8
    
    # Nữ 75 tuổi, 50kg, Creatinine 1.5 mg/dL: CrCl = (65 * 50) / 108 * 0.85 = 25.6 mL/phút
    crcl_nu = tinh_crcl(tuoi=75, can_nang_kg=50.0, creatinine_mg_dl=1.5, la_nu=True)
    assert crcl_nu == 25.6
    
    # Chuyển đổi 88.4 umol/L -> 1.0 mg/dL
    assert chuyen_umol_sang_mg_dl(88.4) == 1.0
    
    # Phân độ KDIGO
    assert phan_do_suy_than(77.8)["giai_doan"] == "G2"
    assert phan_do_suy_than(25.6)["giai_doan"] == "G4"
    assert phan_do_suy_than(10.0)["giai_doan"] == "G5"


def test_metformin_chong_chi_dinh_khi_suy_than_nang():
    """Metformin bắt buộc phải có cảnh báo CRITICAL chống chỉ định khi eGFR < 30 mL/phút."""
    kq = kiem_tra_hieu_chinh_lieu(
        danh_sach_thuoc=["Metformin 850mg ngày 2 viên", "Amlodipine 5mg"],
        ket_qua_xet_nghiem={"egfr": 22.0, "creatinine": 2.3},
        thong_tin_benh_nhan={"tuoi": 68, "can_nang_kg": 60, "la_nu": False}
    )
    
    assert kq["co_canh_bao_critical"] is True
    assert len(kq["canh_bao_hieu_chinh_than"]) == 1
    
    cb = kq["canh_bao_hieu_chinh_than"][0]
    assert cb["thuoc"] == "Metformin"
    assert cb["muc_do"] == "CRITICAL"
    assert "CHỐNG CHỈ ĐỊNH" in cb["khuyen_cao"]
    assert "toan chuyển hóa acid lactic" in cb["ly_do_lam_sang"]


def test_metformin_giam_lieu_khi_suy_than_vua():
    """Metformin phải cảnh báo giảm tối đa 1000mg/ngày khi eGFR trong khoảng 30-44 mL/phút."""
    kq = kiem_tra_hieu_chinh_lieu(
        danh_sach_thuoc=["Metformin 500mg"],
        ket_qua_xet_nghiem={"egfr": 38.0},
        thong_tin_benh_nhan={"tuoi": 62, "can_nang_kg": 65, "la_nu": True}
    )
    
    assert kq["co_canh_bao_critical"] is False
    assert len(kq["canh_bao_hieu_chinh_than"]) == 1
    cb = kq["canh_bao_hieu_chinh_than"][0]
    assert cb["muc_do"] == "WARNING"
    assert "1000 mg/ngày" in cb["khuyen_cao"]


def test_hieu_chinh_ciprofloxacin_va_tuong_tac_thuc_pham():
    """Ciprofloxacin khi suy thận nặng cần giảm liều 50% và cảnh báo kiêng sữa/canxi."""
    kq = kiem_tra_hieu_chinh_lieu(
        danh_sach_thuoc=["Ciprofloxacin 500mg viên uống", "Paracetamol 500mg"],
        ket_qua_xet_nghiem={"egfr": 25.0},
        thong_tin_benh_nhan={"tuoi": 55, "can_nang_kg": 55}
    )
    
    # Cảnh báo giảm liều thận
    cb_than = [c for c in kq["canh_bao_hieu_chinh_than"] if "Ciprofloxacin" in c["thuoc"]]
    assert len(cb_than) == 1
    assert "Giảm 50% liều" in cb_than[0]["khuyen_cao"]
    
    # Cảnh báo tương tác thức ăn (sữa/canxi và rượu bia với Paracetamol)
    cb_tp = kq["huong_dan_tuong_tac_thuc_pham"]
    assert any("Sữa" in c["thuc_pham_kieng_cu"] for c in cb_tp)
    assert any("Rượu" in c["thuc_pham_kieng_cu"] for c in cb_tp)


def test_canh_bao_suy_gan_paracetamol_va_nsaid():
    """Khi men gan tăng cao (AST/ALT > 200), Paracetamol phải giảm trần liều và NSAID bị chống chỉ định."""
    kq = kiem_tra_hieu_chinh_lieu(
        danh_sach_thuoc=["Ibuprofen 400mg", "Paracetamol 500mg"],
        ket_qua_xet_nghiem={"ast": 240.0, "alt": 280.0, "bilirubin": 42.0},
        thong_tin_benh_nhan={"tuoi": 48, "can_nang_kg": 62}
    )
    
    assert kq["chuc_nang_gan"]["bat_thuong"] is True
    assert kq["co_canh_bao_critical"] is True  # NSAID là CRITICAL
    
    cb_gan = kq["canh_bao_hieu_chinh_gan"]
    thuoc_gan = [c["thuoc"] for c in cb_gan]
    assert any("Paracetamol" in t for t in thuoc_gan)
    assert any("NSAID" in t for t in thuoc_gan)
    
    nsaid_cb = [c for c in cb_gan if "NSAID" in c["thuoc"]][0]
    assert nsaid_cb["muc_do"] == "CRITICAL"
    assert "CHỐNG CHỈ ĐỊNH" in nsaid_cb["khuyen_cao"]
