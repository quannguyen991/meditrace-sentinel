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


def test_fhir_8_resource_bundle_va_trich_dan_hai_chieu():
    """Kiểm tra xuất bản toàn diện đủ 8 loại Resource HL7 FHIR R4 và metadata trích dẫn hai chiều."""
    ban_nhap = {
        "CHẨN ĐOÁN": "Tăng huyết áp vô căn (I10)",
        "TIỀN SỬ BỆNH": "Đái tháo đường type 2 (5 năm)",
        "DỊ ỨNG": "Dị ứng Aspirin nổi mẩn ngứa và phù mi mắt",
        "SINH HIỆU": "Huyết áp 140/90 mmHg, Mạch 82 lần/phút",
        "KẾ HOẠCH ĐIỀU TRỊ": "Amlodipin 5mg 1 viên uống mỗi sáng sau ăn",
        "LÝ DO KHÁM": "Khám định kỳ huyết áp"
    }
    thong_tin_bn = {"id": "BN_TEST_007", "gioi_tinh": "nu", "tuoi": 62}
    thong_tin_bs = {"ho_ten": "BS. Nguyễn Văn A", "cchn": "001234/BYT-CCHN"}

    # Dữ liệu trích dẫn hai chiều (Bidirectional Citation Grounding)
    trich_dan = {
        "chan_doan": {
            "utterance_id": "utt_0012",
            "speaker": "DOCTOR",
            "start_ms": 14200,
            "end_ms": 18500,
            "quote": "Bác bị tăng huyết áp vô căn rồi nhé",
            "confidence": 0.98,
            "section": "CHẨN ĐOÁN"
        },
        "di_ung": {
            "utterance_id": "utt_0008",
            "speaker": "PATIENT",
            "start_ms": 8100,
            "end_ms": 11300,
            "quote": "Tôi uống Aspirin là bị nổi mẩn ngứa phù hết mắt",
            "confidence": 0.99,
            "section": "DỊ ỨNG"
        },
        "sinh_hieu": {
            "utterance_id": "utt_0005",
            "speaker": "DOCTOR",
            "start_ms": 5000,
            "end_ms": 7800,
            "quote": "Huyết áp hôm nay đo là 140 trên 90, mạch 82",
            "confidence": 0.97,
            "section": "SINH HIỆU"
        }
    }

    bundle = FHIRExporter.xuat_fhir_bundle(
        ma_ca="ca_test_8_res",
        ban_nhap=ban_nhap,
        thong_tin_benh_nhan=thong_tin_bn,
        trich_dan_chung_cu=trich_dan,
        thong_tin_bac_si=thong_tin_bs
    )

    resources = {e["resource"]["resourceType"]: e["resource"] for e in bundle["entry"]}
    
    # 1. Kiểm tra sự hiện diện của đủ 8 Resource cốt lõi theo quy định:
    tap_hop_loai_resource = set(e["resource"]["resourceType"] for e in bundle["entry"])
    cac_resource_bat_buoc = {
        "Patient", "Encounter", "Condition", "MedicationRequest",
        "Observation", "AllergyIntolerance", "DocumentReference", "Provenance"
    }
    assert cac_resource_bat_buoc.issubset(tap_hop_loai_resource), f"Thiếu resource: {cac_resource_bat_buoc - tap_hop_loai_resource}"

    # 2. Kiểm tra Resource Encounter
    encounter = resources["Encounter"]
    assert encounter["status"] == "finished"
    assert encounter["class"]["code"] == "AMB"

    # 3. Kiểm tra Resource MedicationRequest
    med_req = resources["MedicationRequest"]
    assert med_req["status"] == "active"
    assert med_req["intent"] == "order"
    assert "Amlodipin" in med_req["medicationCodeableConcept"]["text"]

    # 4. Kiểm tra Resource Observation với mã LOINC chuẩn
    obs = resources["Observation"]
    assert obs["code"]["coding"][0]["system"] == "http://loinc.org"
    assert obs["code"]["coding"][0]["code"] == "85354-9"  # Blood pressure panel

    # 5. Kiểm tra Resource DocumentReference
    docref = resources["DocumentReference"]
    assert docref["type"]["coding"][0]["code"] == "11488-4"  # Consultation note
    assert len(docref["content"][0]["attachment"]["data"]) > 0  # Chứa base64 content

    # 6. Kiểm tra Resource Provenance & Chữ ký số
    prov = resources["Provenance"]
    assert len(prov["agent"]) == 2
    assert any(a["who"].get("display", "").startswith("MediTrace AI Sentinel") for a in prov["agent"])
    assert any(a["who"].get("identifier", {}).get("value") == "001234/BYT-CCHN" for a in prov["agent"])
    assert "data" in prov["signature"][0]  # SHA-256 Digest

    # 7. Kiểm tra phần mở rộng Trích dẫn hai chiều (Bidirectional Citation Extension)
    cond = [e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Condition" and "Tăng huyết áp" in e["resource"]["code"]["text"]][0]
    assert "extension" in cond
    cite_ext = cond["extension"][0]
    assert cite_ext["url"] == FHIRExporter.URI_CITATION_EXTENSION
    
    # Kiểm tra các trường con trong extension
    sub_map = {item["url"]: item for item in cite_ext["extension"]}
    assert sub_map["utterance-id"]["valueString"] == "utt_0012"
    assert sub_map["speaker-role"]["valueCode"] == "DOCTOR"
    assert sub_map["audio-timestamp-start-ms"]["valueInteger"] == 14200
    assert sub_map["audio-timestamp-end-ms"]["valueInteger"] == 18500
    assert "tăng huyết áp" in sub_map["verbatim-quote"]["valueString"]
    assert sub_map["confidence-score"]["valueDecimal"] == 0.98

    # 8. Kiểm tra toàn vẹn tham chiếu chéo (Cross-Reference Integrity) của Provenance
    all_entry_urls = set(e["fullUrl"] for e in bundle["entry"])
    prov_targets = [t["reference"] for t in prov["target"]]
    
    # Mọi resource trong target của Provenance đều phải tồn tại thực tế trong Bundle
    for ref in prov_targets:
        assert ref in all_entry_urls, f"Dangling reference: {ref} không có trong entries của Bundle"
    
    # Composition (Document Root) bắt buộc phải nằm trong target được Provenance chứng thực
    comp_url = bundle["entry"][0]["fullUrl"]
    assert comp_url in prov_targets, "Provenance chưa chứng thực Composition root"


def test_fhir_loinc_observations_va_can_lam_sang():
    """Kiểm tra xuất bản các chỉ số xét nghiệm cận lâm sàng sang Observation chuẩn LOINC."""
    ban_nhap = {
        "CHẨN ĐOÁN": "Gout mạn kèm suy thận mạn giai đoạn 3",
        "KẾ HOẠCH ĐIỀU TRỊ": "Febuxostat 40mg uống mỗi sáng"
    }
    thong_tin_bn = {
        "id": "BN_LAB_001",
        "tuoi": 65,
        "creatinine": 1.9,
        "egfr": 36.5,
        "ast": 42.0,
        "alt": 48.0,
        "axit_uric": 9.2,
        "hba1c": 6.5,
        "inr": 1.1
    }

    bundle = FHIRExporter.xuat_fhir_bundle("ca_lab_001", ban_nhap, thong_tin_bn)
    obs_entries = [e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Observation"]

    loinc_codes = set()
    for obs in obs_entries:
        for coding in obs.get("code", {}).get("coding", []):
            if coding.get("system") == "http://loinc.org":
                loinc_codes.add(coding["code"])

    # Kiểm tra sự hiện diện của các mã LOINC xét nghiệm cốt lõi
    assert "2160-0" in loinc_codes    # Creatinine
    assert "98979-8" in loinc_codes   # eGFR CKD-EPI 2021
    assert "1920-8" in loinc_codes    # AST
    assert "1742-6" in loinc_codes    # ALT
    assert "2857-1" in loinc_codes    # Axit Uric
    assert "4548-4" in loinc_codes    # HbA1c
    assert "6301-6" in loinc_codes    # INR



