# -*- coding: utf-8 -*-
"""Gia tri "khong ro" phai thanh trang thai tuong minh, khong ngam dinh thanh gia tri an toan."""
import pytest

from src.cong_cu_lam_sang.xuat_fhir_r4 import FHIRExporter
from src.cong_cu_lam_sang.tien_kiem_bhyt_va_khoi_phuc_bo_sot import _suy_nguoi_noi, _suy_trang_thai


def _di_ung(b):
    return [e["resource"] for e in b["entry"] if e["resource"]["resourceType"] == "AllergyIntolerance"]


@pytest.mark.parametrize("cau", ["không rõ", "Không rõ", "chưa rõ", "Dị ứng: không rõ",
                                 "chưa rõ tiền sử dị ứng", "không rõ có dị ứng không"])
def test_di_ung_khong_ro_la_chua_xac_nhan(cau):
    al = _di_ung(FHIRExporter.xuat_fhir_bundle("ca", {"CHẨN ĐOÁN": "Viêm phổi", "DỊ ỨNG": cau}))
    assert len(al) == 1
    assert al[0]["verificationStatus"]["coding"][0]["code"] == "unconfirmed"
    assert al[0]["criticality"] == "unable-to-assess"


@pytest.mark.parametrize("cau", ["không", "không dị ứng", "chưa ghi nhận dị ứng", "NKDA"])
def test_di_ung_phu_dinh_ro_van_bo(cau):
    assert _di_ung(FHIRExporter.xuat_fhir_bundle("ca", {"CHẨN ĐOÁN": "Viêm phổi", "DỊ ỨNG": cau})) == []


def test_di_ung_duong_tinh_van_xac_nhan():
    al = _di_ung(FHIRExporter.xuat_fhir_bundle("ca", {"CHẨN ĐOÁN": "Viêm phổi", "DỊ ỨNG": "Penicillin"}))
    assert al and al[0]["verificationStatus"]["coding"][0]["code"] == "confirmed"


def test_trang_thai_la_khong_mac_dinh_con_hieu_luc():
    assert _suy_trang_thai({"trang_thai": "abc_la"}) == "chưa giải quyết"
    assert _suy_trang_thai({}) == "còn hiệu lực"
    assert _suy_trang_thai({"status": "active"}) == "còn hiệu lực"
    assert _suy_trang_thai({"status": "than"}) == "còn hiệu lực"      # trang thai web
    assert _suy_trang_thai({"status": "superseded"}) == "bị thay thế"


def test_nguoi_noi_la_khong_mac_dinh_benh_nhan():
    assert _suy_nguoi_noi({"speaker": "xyz"}) == "người khác"
    assert _suy_nguoi_noi({"speaker": "patient"}) == "bệnh nhân"
    assert _suy_nguoi_noi({"nguoi_noi": "bệnh nhân"}) == "bệnh nhân"
    assert _suy_nguoi_noi({"section": "CHẨN ĐOÁN"}) == "bác sĩ"
