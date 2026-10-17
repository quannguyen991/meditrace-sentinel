# -*- coding: utf-8 -*-
"""Trụ cột 2: Chuẩn hóa Xuất bản Bệnh án Quốc tế HL7 FHIR R4 (Fast Healthcare Interoperability Resources).

Cho phép đóng gói toàn bộ bản nháp lâm sàng và các thực thể đã qua kiểm chứng
thành một FHIR Document Bundle chuẩn mực quốc tế, sẵn sàng tích hợp với hệ thống
bệnh viện (HIS / EMR / LIS) và các chuẩn giao dịch y tế số.
"""

from dataclasses import asdict
from datetime import datetime, timezone
import json
import re
from typing import Any, Dict, List, Optional
import uuid


class FHIRExporter:
    """Bộ chuyển đổi bản nháp MediTrace sang HL7 FHIR R4 Bundle Resource."""

    @staticmethod
    def _tao_id(prefix: str = "res") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    @classmethod
    def xuat_fhir_bundle(cls, ma_ca: str, ban_nhap: Dict[str, Any],
                         thong_tin_benh_nhan: Optional[Dict[str, Any]] = None,
                         danh_sach_phat_bieu: Optional[List[Any]] = None) -> Dict[str, Any]:
        """Tạo HL7 FHIR R4 Document Bundle từ kết quả xử lý của MediTrace Sentinel."""
        now_iso = datetime.now(timezone.utc).isoformat()
        bundle_id = f"bundle-{ma_ca}"
        patient_id = cls._tao_id("patient")
        
        # 1. Tạo Resource: Patient
        gioi = "unknown"
        if thong_tin_benh_nhan:
            g = str(thong_tin_benh_nhan.get("gioi_tinh", "")).lower()
            if "nam" in g:
                gioi = "male"
            elif "nữ" in g or "nu" in g:
                gioi = "female"

        patient_resource = {
            "resourceType": "Patient",
            "id": patient_id,
            "identifier": [{
                "system": "urn:oid:meditrace:patient:id",
                "value": str(thong_tin_benh_nhan.get("id", ma_ca) if thong_tin_benh_nhan else ma_ca)
            }],
            "active": True,
            "gender": gioi,
            "meta": {
                "profile": ["http://hl7.org/fhir/StructureDefinition/Patient"]
            }
        }
        if thong_tin_benh_nhan and thong_tin_benh_nhan.get("tuoi"):
            patient_resource["extension"] = [{
                "url": "http://hl7.org/fhir/StructureDefinition/patient-age",
                "valueInteger": int(thong_tin_benh_nhan["tuoi"])
            }]

        entries = [{"fullUrl": f"urn:uuid:{patient_id}", "resource": patient_resource}]

        # 2. Tạo Resource: Condition (Chẩn đoán & Tiền sử bệnh)
        chan_doan_text = ban_nhap.get("CHẨN ĐOÁN", "") or ban_nhap.get("chan_doan", "")
        if chan_doan_text:
            cond_id = cls._tao_id("condition")
            cond_res = {
                "resourceType": "Condition",
                "id": cond_id,
                "clinicalStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active",
                        "display": "Active"
                    }]
                },
                "verificationStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "provisional",
                        "display": "Provisional"
                    }]
                },
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": "encounter-diagnosis",
                        "display": "Encounter Diagnosis"
                    }]
                }],
                "code": {
                    "text": str(chan_doan_text).strip(),
                    "coding": [{
                        "system": "http://hl7.org/fhir/sid/icd-10",
                        "display": str(chan_doan_text).strip()
                    }]
                },
                "subject": {"reference": f"urn:uuid:{patient_id}"},
                "recordedDate": now_iso
            }
            entries.append({"fullUrl": f"urn:uuid:{cond_id}", "resource": cond_res})

        # Tiền sử bệnh
        tien_su = ban_nhap.get("TIỀN SỬ BỆNH", "") or ban_nhap.get("tien_su_benh", "")
        if tien_su:
            ts_id = cls._tao_id("condition-history")
            ts_res = {
                "resourceType": "Condition",
                "id": ts_id,
                "clinicalStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "resolved",
                        "display": "Resolved / In Remission"
                    }]
                },
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": "problem-list-item",
                        "display": "Problem List Item"
                    }]
                }],
                "code": {"text": str(tien_su).strip()},
                "subject": {"reference": f"urn:uuid:{patient_id}"}
            }
            entries.append({"fullUrl": f"urn:uuid:{ts_id}", "resource": ts_res})

        # 3. Tạo Resource: AllergyIntolerance (Dị ứng thuốc/thức ăn)
        di_ung = ban_nhap.get("DỊ ỨNG", "") or ban_nhap.get("di_ung", "")
        if di_ung:
            al_id = cls._tao_id("allergy")
            al_res = {
                "resourceType": "AllergyIntolerance",
                "id": al_id,
                "clinicalStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                        "code": "active",
                        "display": "Active"
                    }]
                },
                "verificationStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                        "code": "confirmed",
                        "display": "Confirmed"
                    }]
                },
                "type": "allergy",
                "criticality": "high",
                "code": {"text": str(di_ung).strip()},
                "patient": {"reference": f"urn:uuid:{patient_id}"},
                "recordedDate": now_iso
            }
            entries.append({"fullUrl": f"urn:uuid:{al_id}", "resource": al_res})

        # 4. Tạo Resource: MedicationStatement (Thuốc đang dùng)
        thuoc = ban_nhap.get("THUỐC ĐANG DÙNG", "") or ban_nhap.get("thuoc_dang_dung", "")
        if thuoc:
            med_id = cls._tao_id("medication")
            med_res = {
                "resourceType": "MedicationStatement",
                "id": med_id,
                "status": "active",
                "medicationCodeableConcept": {"text": str(thuoc).strip()},
                "subject": {"reference": f"urn:uuid:{patient_id}"},
                "effectiveDateTime": now_iso
            }
            entries.append({"fullUrl": f"urn:uuid:{med_id}", "resource": med_res})

        # 5. Tạo Resource: Observation (Dấu hiệu sinh tồn / Sinh hiệu nếu có)
        sinh_hieu = ban_nhap.get("SINH HIỆU", "") or ban_nhap.get("sinh_hieu", "")
        if sinh_hieu:
            obs_id = cls._tao_id("observation-vitals")
            obs_res = {
                "resourceType": "Observation",
                "id": obs_id,
                "status": "final",
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                        "display": "Vital Signs"
                    }]
                }],
                "code": {"text": "Sinh hiệu lâm sàng"},
                "subject": {"reference": f"urn:uuid:{patient_id}"},
                "valueString": str(sinh_hieu).strip(),
                "effectiveDateTime": now_iso
            }
            entries.append({"fullUrl": f"urn:uuid:{obs_id}", "resource": obs_res})

        # 6. Tạo Resource: Composition (Bản tóm tắt bệnh án gốc gắn kết toàn bộ các tài nguyên)
        comp_id = cls._tao_id("composition")
        comp_res = {
            "resourceType": "Composition",
            "id": comp_id,
            "status": "preliminary",
            "type": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "11488-4",
                    "display": "Consultation note"
                }],
                "text": "Bản nháp hồ sơ khám bệnh MediTrace Sentinel"
            },
            "subject": {"reference": f"urn:uuid:{patient_id}"},
            "date": now_iso,
            "title": f"Bệnh án ngoại trú ca {ma_ca}",
            "section": [
                {
                    "title": "Bệnh sử hiện tại",
                    "text": {"status": "generated", "div": f"<div>{ban_nhap.get('BỆNH SỬ HIỆN TẠI', '')}</div>"}
                },
                {
                    "title": "Khám lâm sàng",
                    "text": {"status": "generated", "div": f"<div>{ban_nhap.get('KHÁM LÂM SÀNG', '')}</div>"}
                },
                {
                    "title": "Kế hoạch điều trị",
                    "text": {"status": "generated", "div": f"<div>{ban_nhap.get('KẾ HOẠCH ĐIỀU TRỊ', '')}</div>"}
                },
                {
                    "title": "Mục cần bác sĩ xác nhận",
                    "text": {"status": "generated", "div": f"<div>{ban_nhap.get('CẦN XÁC NHẬN', '')}</div>"}
                }
            ]
        }
        entries.insert(0, {"fullUrl": f"urn:uuid:{comp_id}", "resource": comp_res})

        # Đóng gói Document Bundle chuẩn HL7 FHIR
        fhir_bundle = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "type": "document",
            "timestamp": now_iso,
            "meta": {
                "lastUpdated": now_iso,
                "profile": ["http://hl7.org/fhir/StructureDefinition/Bundle"]
            },
            "entry": entries
        }

        return fhir_bundle

    @classmethod
    def xuat_chuoi_json(cls, fhir_bundle: Dict[str, Any], indent: int = 2) -> str:
        """Xuất FHIR Bundle thành chuỗi JSON chuẩn có format đẹp."""
        return json.dumps(fhir_bundle, ensure_ascii=False, indent=indent)
