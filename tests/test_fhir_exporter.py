# -*- coding: utf-8 -*-
"""Test suite cho Trụ cột 2: Chuẩn hóa Xuất bản Bệnh án Quốc tế HL7 FHIR trong tests/test_fhir_exporter.py."""
import json
import pytest
from src.fhir_exporter import FHIRExporter


def test_tao_fhir_bundle_day_du_resources():
    ban_nhap = {
        "CHẨN ĐOÁN": "Viêm phế quản cấp.",
        "TIỀN SỬ BỆNH": "Tăng huyết áp độ 2 (ba năm nay).",
        "DỊ ỨNG": "Dị ứng amoxicillin nổi mẩn ngứa toàn thân.",
        "THUỐC ĐANG DÙNG": "Amlodipin 5 mg uống mỗi sáng.",
        "SINH HIỆU": "Huyết áp 135/85 mmHg, Mạch 80 lần/phút.",
        "BỆNH SỬ HIỆN TẠI": "Ho có đờm sốt nhẹ 3 ngày nay.",
        "KHÁM LÂM SÀNG": "Phổi nghe có ran ngáy hai bên.",
        "KẾ HOẠCH ĐIỀU TRỊ": "Uống nhiều nước, hạ sốt bằng paracetamol khi cần.",
        "CẦN XÁC NHẬN": "Cần xác nhận liều dùng thuốc huyết áp."
    }
    thong_tin_bn = {
        "id": "BN_09281",
        "gioi_tinh": "nam",
        "tuoi": 58
    }

    bundle = FHIRExporter.xuat_fhir_bundle("ca_001", ban_nhap, thong_tin_bn)

    # 1. Kiểm tra cấu trúc Bundle cấp cao
    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "document"
    assert "timestamp" in bundle
    assert len(bundle["entry"]) >= 6  # Composition, Patient, Condition, History, Allergy, Medication, Observation

    # 2. Kiểm tra Resource: Composition
    comp = bundle["entry"][0]["resource"]
    assert comp["resourceType"] == "Composition"
    assert comp["status"] == "preliminary"
    assert len(comp["section"]) == 4

    # 3. Kiểm tra Resource: Patient
    patient = [e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Patient"][0]
    assert patient["gender"] == "male"
    assert patient["extension"][0]["valueInteger"] == 58

    # 4. Kiểm tra Resource: Condition & Allergy
    condition = [e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Condition"][0]
    assert "Viêm phế quản cấp" in condition["code"]["text"]

    allergy = [e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "AllergyIntolerance"][0]
    assert "amoxicillin" in allergy["code"]["text"]
    assert allergy["criticality"] == "high"


def test_xuat_chuoi_json_hop_le():
    ban_nhap = {"CHẨN ĐOÁN": "Cúm mùa."}
    bundle = FHIRExporter.xuat_fhir_bundle("ca_002", ban_nhap)
    json_str = FHIRExporter.xuat_chuoi_json(bundle)
    
    # Đảm bảo JSON parse được hoàn hảo
    parsed = json.loads(json_str)
    assert parsed["resourceType"] == "Bundle"
    assert parsed["id"] == "bundle-ca_002"
