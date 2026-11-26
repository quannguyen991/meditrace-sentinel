# -*- coding: utf-8 -*-
"""Hoi quy hieu_chinh_lieu: CrCl cho quy tac dinh nghia theo CrCl, thieu tuoi,
gioi tinh theo tu nguyen ven, doxycycline, benh gan nen khong bia so lieu."""
import pytest

from src.hieu_chinh_lieu import QUY_TAC_THAN, _tap_goc_thuoc_tu_danh_sach, kiem_tra_hieu_chinh_lieu
from src.ocr_lam_sang import boc_tach_phieu_cu


# ---------------------------------------------------------------- CrCl vs eGFR
def test_moi_quy_tac_than_khai_bao_chi_so():
    for qt in QUY_TAC_THAN:
        assert qt.get("chi_so") in ("crcl", "egfr"), qt["thuoc"]


def test_dabigatran_dung_crcl_khong_dung_egfr():
    # Nam 85 tuoi, 50 kg, creatinine 1.4 mg/dL: CrCl ~27 (eGFR CKD-EPI ~48)
    kq = kiem_tra_hieu_chinh_lieu(
        ["Dabigatran 110mg"], {"creatinine": 1.4},
        {"tuoi": 85, "can_nang_kg": 50, "la_nu": False})
    assert 26 <= kq["chuc_nang_than"]["crcl_cockcroft_gault"] <= 28
    assert kq["chuc_nang_than"]["egfr_ckd_epi"] > 30
    cb = [c for c in kq["canh_bao_hieu_chinh_than"] if "Dabigatran" in c["thuoc"]]
    assert cb and cb[0]["muc_do"] == "CRITICAL"
    assert cb[0]["chi_so_dung"] == "crcl"
    assert kq["co_canh_bao_critical"] is True


def test_enoxaparin_dung_crcl():
    kq = kiem_tra_hieu_chinh_lieu(
        ["Enoxaparin 40mg"], {"creatinine": 1.4},
        {"tuoi": 85, "can_nang_kg": 50, "la_nu": False})
    assert any("Enoxaparin" in c["thuoc"] for c in kq["canh_bao_hieu_chinh_than"])


def test_quy_tac_crcl_thieu_can_nang_thi_dung_chi_so_thay_the_co_co():
    kq = kiem_tra_hieu_chinh_lieu(["Dabigatran 110mg"], {"egfr": 22.0}, {"tuoi": 70})
    cb = [c for c in kq["canh_bao_hieu_chinh_than"] if "Dabigatran" in c["thuoc"]]
    assert cb and cb[0]["chi_so_thay_the"] is True


def test_metformin_van_dung_egfr():
    kq = kiem_tra_hieu_chinh_lieu(
        ["Metformin 500mg"], {"creatinine": 1.4},
        {"tuoi": 85, "can_nang_kg": 50, "la_nu": False})
    # eGFR ~48 -> khong co canh bao CRITICAL metformin du CrCl ~27
    assert not any(c["muc_do"] == "CRITICAL" for c in kq["canh_bao_hieu_chinh_than"])


# ---------------------------------------------------------------- thieu tuoi
def test_thieu_tuoi_khong_uoc_tinh():
    kq = kiem_tra_hieu_chinh_lieu(["Metformin 500mg"], {"creatinine": 2.5}, {"can_nang_kg": 60})
    ct = kq["chuc_nang_than"]
    assert ct["phuong_phap_uoc_tinh"] == "thieu_tuoi"
    assert ct["egfr_ckd_epi"] is None and ct["crcl_cockcroft_gault"] is None
    assert ct.get("canh_bao_uoc_tinh")


def test_thieu_tuoi_nhung_co_egfr_xet_nghiem_van_dung():
    kq = kiem_tra_hieu_chinh_lieu(["Metformin 500mg"], {"egfr": 20.0}, {})
    assert kq["chuc_nang_than"]["phuong_phap_uoc_tinh"] == "Ket_qua_phong_xet_nghiem"
    assert kq["co_canh_bao_critical"] is True


def test_ocr_thieu_tuoi_khong_mac_dinh_50():
    kq = boc_tach_phieu_cu("Creatinin: 2.5 mg/dL, Glucophage 850mg", tuoi=None)
    assert "egfr" not in kq["chi_so"]
    assert kq["hieu_chinh_lieu"]["chuc_nang_than"]["phuong_phap_uoc_tinh"] == "thieu_tuoi"


def test_ocr_mac_dinh_khong_co_tuoi():
    kq = boc_tach_phieu_cu("Creatinin: 2.5 mg/dL")
    assert "egfr" not in kq["chi_so"]


def test_ocr_tuoi_chuoi_va_rac_khong_sap():
    assert "egfr" in boc_tach_phieu_cu("Creatinin: 2.5 mg/dL", tuoi="70")["chi_so"]
    assert "egfr" not in boc_tach_phieu_cu("Creatinin: 2.5 mg/dL", tuoi="abc")["chi_so"]


# ---------------------------------------------------------------- gioi tinh
@pytest.mark.parametrize("gt,nu", [
    ("false", False), ("nam", False), ("male", False), ("M", False), ("không rõ", False),
    ("nữ", True), ("Nu", True), ("female", True), ("F", True), ("Nữ giới", True),
])
def test_gioi_tinh_theo_tu(gt, nu):
    kq = kiem_tra_hieu_chinh_lieu([], {"creatinine": 1.0}, {"tuoi": 60, "gioi_tinh": gt})
    egfr_nu = kiem_tra_hieu_chinh_lieu([], {"creatinine": 1.0}, {"tuoi": 60, "la_nu": True})
    egfr_nam = kiem_tra_hieu_chinh_lieu([], {"creatinine": 1.0}, {"tuoi": 60, "la_nu": False})
    mong = egfr_nu if nu else egfr_nam
    assert kq["chuc_nang_than"]["egfr_ckd_epi"] == mong["chuc_nang_than"]["egfr_ckd_epi"]


# ---------------------------------------------------------------- doxycycline
def test_doxycycline_khong_thanh_tetracycline():
    tap = _tap_goc_thuoc_tu_danh_sach(["doxycycline 100mg", "vibramycin"])
    assert "tetracyclin" not in tap


def test_doxycycline_khong_co_canh_bao_than():
    kq = kiem_tra_hieu_chinh_lieu(["Doxycycline 100mg"], {"egfr": 10.0}, {"tuoi": 60})
    assert kq["canh_bao_hieu_chinh_than"] == []


# ---------------------------------------------------------------- benh gan nen
def test_benh_gan_nen_khong_bia_men_gan():
    kq = kiem_tra_hieu_chinh_lieu(["Paracetamol 500mg"], {}, {"tuoi": 60, "benh_nen": ["xơ gan"]})
    gan = kq["chuc_nang_gan"]
    assert gan["benh_gan_nen"] is True
    assert gan["ast"] is None and gan["alt"] is None
    assert gan["bat_thuong"] is True
    cb = kq["canh_bao_hieu_chinh_gan"]
    assert cb and "210" not in cb[0]["chi_so_danh_gia"]


@pytest.mark.parametrize("bn", ["không suy gan", "không có bệnh gan", "chưa từng xơ gan",
                                "phủ nhận suy gan"])
def test_phu_dinh_benh_gan(bn):
    kq = kiem_tra_hieu_chinh_lieu(["Ibuprofen 400mg"], {}, {"tuoi": 60, "benh_nen": bn})
    assert kq["chuc_nang_gan"]["benh_gan_nen"] is False
    assert kq["canh_bao_hieu_chinh_gan"] == []
    assert kq["chuc_nang_gan"]["bat_thuong"] is False
