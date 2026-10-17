# -*- coding: utf-8 -*-
"""Test suite cho Trụ cột 1: Động cơ Dược lý Lâm sàng trong src/duoc_ly_lam_sang.py."""
import pytest
from src.duoc_ly_lam_sang import (
    ClinicalPharmacovigilanceEngine as CPE,
    DDI_CHONG_CHI_DINH,
    DDI_NGHIEM_TRONG
)


def test_phat_hien_tuong_tac_nguy_hiem_warfarin_aspirin():
    thuoc = ["viên warfarin 2mg", "aspirin 81mg"]
    ddi = CPE.kiem_tra_tuong_tac(thuoc)
    assert len(ddi) >= 1
    assert any(d.thuoc_1 == "warfarin" and d.thuoc_2 == "aspirin" for d in ddi)
    assert ddi[0].muc_do == DDI_CHONG_CHI_DINH


def test_phat_hien_tuong_tac_clopidogrel_omeprazole():
    thuoc = ["clopidogrel 75mg", "omeprazole 20mg"]
    ddi = CPE.kiem_tra_tuong_tac(thuoc)
    assert any("clopidogrel" in d.thuoc_1 or "clopidogrel" in d.thuoc_2 for d in ddi)
    assert any("CYP2C19" in d.co_che for d in ddi)


def test_chong_chi_dinh_nsaid_khi_suy_than_nang():
    co_dia = {"egfr": 22, "tuoi": 72}
    thuoc = ["ibuprofen 400mg", "paracetamol 500mg"]
    cd = CPE.kiem_tra_co_dia_chong_chi_dinh(thuoc, co_dia)
    assert any("ibuprofen" in c and "suy thận" in c for c in cd)


def test_chong_chi_dinh_acei_trong_thai_ky():
    co_dia = {"mang_thai": True, "tuan_thai": 14}
    thuoc = ["captopril 25mg", "vitamin C"]
    cd = CPE.kiem_tra_co_dia_chong_chi_dinh(thuoc, co_dia)
    assert any("captopril" in c and "quái thai" in c for c in cd)


def test_chong_chi_dinh_propranolol_o_benh_nhan_hen():
    co_dia = {"tien_su_benh": ["hen phế quản", "viêm mũi dị ứng"]}
    thuoc = ["propranolol 40mg", "salbutamol xịt"]
    cd = CPE.kiem_tra_co_dia_chong_chi_dinh(thuoc, co_dia)
    assert any("propranolol" in c and "co thắt phế quản" in c for c in cd)


def test_phat_hien_vuot_lieu_tran_paracetamol():
    # Paracetamol liều trần là 4000mg/ngày
    err = CPE.kiem_tra_lieu_tran("panadol extra", 5000.0)
    assert err is not None
    assert "VƯỢT LIỀU TRẦN" in err

    # Liều an toàn 2000mg/ngày
    assert CPE.kiem_tra_lieu_tran("paracetamol", 2000.0) is None


def test_kiem_duyet_toan_dien_tong_hop():
    co_dia = {"mang_thai": True, "egfr": 50}
    thuoc = ["warfarin 5mg", "aspirin 81mg"]
    chi_tiet_lieu = {"paracetamol": 6000.0}

    ket_qua = CPE.kiem_duyet_toan_dien(thuoc, co_dia, chi_tiet_lieu)
    assert not ket_qua.hop_le
    assert len(ket_qua.canh_bao_ddi) > 0
    assert len(ket_qua.chong_chi_dinh_co_dia) > 0
    assert len(ket_qua.vuot_lieu_tran) > 0
    assert len(ket_qua.giai_trinh_duoc_ly) >= 3
