# -*- coding: utf-8 -*-
"""[Công cụ lâm sàng hỗ trợ bác sĩ › Liên thông]
Làm gì   : Chuyển bản nháp hồ sơ khám thành gói FHIR R4 để chuyển sang hệ thống khác.
Vào → Ra : mã ca + bản nháp (+ thông tin bệnh nhân, bác sĩ, mệnh đề, xét nghiệm) → gói FHIR
           Bundle dạng dict hoặc chuỗi JSON
Đọc từ   : class FHIRExporter dựng gói FHIR Bundle từ bản nháp và xuất ra chuỗi JSON
Mục lục (các hàm/lớp chính):
  class FHIRExporter  Chuyển bản nháp sang gói HL7 FHIR R4 gồm 8 tài nguyên
Gọi tới  : cong_cu_lam_sang/chuan_hoa_don_vi_xet_nghiem,
           cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot
Dùng bởi : he_thong/dieu_phoi_cac_chot_an_toan
Tên cũ   : fhir_exporter.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Trụ cột 2: Chuẩn hóa Xuất bản Bệnh án Quốc tế HL7 FHIR R4 (Fast Healthcare Interoperability Resources).

Cho phép đóng gói toàn bộ bản nháp lâm sàng và các thực thể đã qua kiểm chứng
thành một FHIR Document Bundle chuẩn mực quốc tế, sẵn sàng tích hợp với hệ thống
bệnh viện (HIS / EMR / LIS) và các chuẩn giao dịch y tế số.
"""

import base64
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import re
from html import escape
from typing import Any, Dict, List, Optional
import uuid

from src.cong_cu_lam_sang.chuan_hoa_don_vi_xet_nghiem import chuan_hoa_du_lieu_xet_nghiem
from src.cong_cu_lam_sang.tien_kiem_bhyt_va_khoi_phuc_bo_sot import DANH_MUC_ICD10_BYT


# ═══ class FHIRExporter — Chuyển bản nháp sang gói HL7 FHIR R4 gồm 8 tài nguyên ═══════
# Gồm Patient, Encounter, Condition, MedicationRequest, Observation (LOINC),
# AllergyIntolerance, DocumentReference, Provenance.
class FHIRExporter:
    """Bộ chuyển đổi bản nháp MediTrace sang HL7 FHIR R4 8-Resource Bundle.
    
    Hỗ trợ xuất bản đầy đủ 8 loại tài nguyên cốt lõi theo chuẩn HL7 FHIR R4:
    1. Patient: Thông tin nhân khẩu học bệnh nhân
    2. Encounter: Lượt khám ngoại trú (Ambulatory Encounter)
    3. Condition: Chẩn đoán ICD-10 và tiền sử bệnh lý
    4. MedicationRequest: Y lệnh kê đơn thuốc điều trị
    5. Observation: Sinh hiệu & chỉ số cận lâm sàng mã hóa chuẩn LOINC
    6. AllergyIntolerance: Tiền sử dị ứng thuốc và thức ăn
    7. DocumentReference: Tài liệu bệnh án lâm sàng điện tử
    8. Provenance: Nguồn gốc chứng thực, chữ ký số và vết kiểm toán WORM
    Kèm theo Composition (Document Bundle Root) và phần mở rộng Trích dẫn hai chiều (Bidirectional Citation).
    """

    URI_CITATION_EXTENSION = "https://meditrace.vn/fhir/StructureDefinition/bidirectional-citation"

    # Danh mục mã LOINC chuẩn quốc tế cho Sinh hiệu & Cận lâm sàng phổ biến
    BANG_MA_LOINC: Dict[str, Dict[str, str]] = {
        "creatinine": {"code": "2160-0", "display": "Creatinine [Mass/volume] in Serum or Plasma", "unit": "mg/dL"},
        "egfr": {"code": "98979-8", "display": "Glomerular filtration rate/1.73 sq M.predicted by CKD-EPI 2021 race-free equation", "unit": "mL/min/1.73m2"},
        "ast": {"code": "1920-8", "display": "Aspartate aminotransferase [Enzymatic activity/volume] in Serum or Plasma", "unit": "U/L"},
        "alt": {"code": "1742-6", "display": "Alanine aminotransferase [Enzymatic activity/volume] in Serum or Plasma", "unit": "U/L"},
        "axit_uric": {"code": "2857-1", "display": "Urate [Mass/volume] in Serum or Plasma", "unit": "mg/dL"},
        "glucose": {"code": "1558-6", "display": "Fasting glucose [Mass/volume] in Serum or Plasma", "unit": "mg/dL"},
        "urea": {"code": "3091-6", "display": "Urea [Moles/volume] in Serum or Plasma", "unit": "mmol/L"},
        "hba1c": {"code": "4548-4", "display": "Hemoglobin A1c/Hemoglobin.total in Blood", "unit": "%"},
        "inr": {"code": "6301-6", "display": "INR in Platelet poor plasma by Coagulation assay", "unit": "{INR}"},
        "digoxin": {"code": "2198-0", "display": "Digoxin [Mass/volume] in Serum or Plasma", "unit": "ng/mL"},
        "huyet_ap": {"code": "85354-9", "display": "Blood pressure panel with all children optional", "unit": "mmHg"},
        "nhip_tim": {"code": "8867-4", "display": "Heart rate", "unit": "/min"},
        "than_nhiet": {"code": "8310-5", "display": "Body temperature", "unit": "Cel"},
        "spo2": {"code": "59408-5", "display": "Oxygen saturation in Arterial blood by Pulse oximetry", "unit": "%"},
        "wbc": {"code": "6690-2", "display": "Leukocytes [#/volume] in Blood by Automated count", "unit": "10*9/L"},
        "hb": {"code": "718-7", "display": "Hemoglobin [Mass/volume] in Blood", "unit": "g/dL"},
        "kali": {"code": "2823-3", "display": "Potassium [Moles/volume] in Serum or Plasma", "unit": "mmol/L"},
        "troponin": {"code": "6598-7", "display": "Troponin T.cardiac [Mass/volume] in Serum or Plasma", "unit": "ng/mL"},
    }

    _RE_DI_UNG_PHU_DINH = re.compile(
        r"^\s*(?:[-*•]\s*)?(?:bệnh\s+nhân\s+|bn\s+|người\s+bệnh\s+)?"
        r"(?:"
        r"(?:không|ko|chẳng|chả)\s+(?:(?:có|bị|thấy|ghi\s+nhận|phát\s+hiện|rõ)\s+)*(?:tiền\s+sử\s+)?(?:dị\s+ứng|mẫn\s+cảm)"
        r"|(?:chưa(?:\s+(?:ghi\s+nhận|từng|thấy|có|bị|phát\s+hiện|rõ|bao\s+giờ))+)\s*(?:tiền\s+sử\s+)?(?:dị\s+ứng|mẫn\s+cảm)?"
        r"|(?:dị\s+ứng|tiền\s+sử\s+dị\s+ứng)\s*[:=-]\s*(?:không(?:\s+có|\s+rõ)?|chưa(?:\s+ghi\s+nhận|\s+rõ)?|âm\s+tính)"
        r"|không\s+có\s+tiền\s+sử\s+dị\s+ứng"
        r"|(?:không(?:\s+có|\s+rõ)?|âm\s+tính|nkda|nka)\s*$"
        r")",
        re.IGNORECASE,
    )

    _RE_TACH_VE_DI_UNG = re.compile(
        r"[.;\n]+"
        r"|,\s*(?=(?:có\s+|bị\s+|dị\s+ứng|mẫn\s+cảm|không|ko|chưa|chẳng|còn|nhưng|chỉ|trừ|ngoài|"
        r"nổi\s+mề\s+đay|mề\s+đay|mẩn\s+ngứa|phát\s+ban|sốc|phản\s+vệ|phù\s+|khó\s+thở|khi\s+(?:uống|dùng|tiêm|ăn))\b)"
        r"|\b(?:nhưng|song|tuy\s+nhiên|ngoại\s+trừ)\b"
        r"|\b(?:chỉ|trừ|ngoài|mà)\s+(?=(?:có|bị|dị\s+ứng|mẫn\s+cảm|nổi|mề\s+đay|mẩn|ngứa|phát\s+ban|sốc|phản\s+vệ|phù|với|khi|[a-zA-Z]{4,})\b)",
        re.IGNORECASE,
    )

    _RE_DAU_HIEU_DUONG_TINH_DI_UNG = re.compile(
        r"\b(?:nổi\s+mề\s+đay|mẩn\s+ngứa|sốc\s+phản\s+vệ|phản\s+vệ|phát\s+ban|phù\s+(?:mạch|mi|mắt|môi|thanh\s+quản))\b",
        re.IGNORECASE,
    )

    # "không rõ" / "chưa rõ" KHÔNG phải là "không dị ứng": là trạng thái CHƯA BIẾT, phải giữ lại
    _RE_DI_UNG_KHONG_RO = re.compile(
        r"^\s*(?:[-*•]\s*)?(?:(?:tiền\s+sử\s+)?dị\s+ứng\s*[:=-]?\s*)?(?:không|chưa|ko)\s+rõ"
        r"(?:\s+(?:có\s+)?(?:tiền\s+sử\s+)?(?:dị\s+ứng|mẫn\s+cảm)(?:\s+(?:gì|không))?)?\s*[.!]?\s*$",
        re.IGNORECASE,
    )

    @classmethod
    def _la_di_ung_khong_ro(cls, van_ban: Any) -> bool:
        return bool(cls._RE_DI_UNG_KHONG_RO.match(str(van_ban or "")))

    @classmethod
    def _la_di_ung_phu_dinh(cls, van_ban: Any) -> bool:
        """Trả về True nếu toàn bộ nội dung mục DỊ ỨNG mang nghĩa phủ định / chưa ghi nhận."""
        txt = str(van_ban or "").strip()
        if not txt:
            return True
        if cls._la_di_ung_khong_ro(txt):
            return False          # chưa biết != không dị ứng
        cac_ve = [v.strip() for v in cls._RE_TACH_VE_DI_UNG.split(txt) if v and v.strip()]
        if not cac_ve:
            return True
        for ve in cac_ve:
            m = cls._RE_DI_UNG_PHU_DINH.search(ve)
            if not m:
                return False
            phan_du = ve[m.end():]
            if cls._RE_DAU_HIEU_DUONG_TINH_DI_UNG.search(phan_du) and not re.search(r"\b(?:không|chưa|ko)\b", phan_du, re.I):
                return False
        return True

    @staticmethod
    def _tao_id(prefix: str = "res") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    @staticmethod
    def _xhtml(text: Any) -> str:
        """Tạo narrative XHTML hợp lệ về cấu trúc và escape nội dung không tin cậy."""
        return f'<div xmlns="http://www.w3.org/1999/xhtml">{escape(str(text or ""))}</div>'

    @classmethod
    def _tao_citation_extension(cls, citation: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Tạo cấu trúc extension chuẩn FHIR R4 lưu vết trích dẫn hai chiều (Bidirectional Citation)."""
        if not citation or not isinstance(citation, dict):
            return None

        sub_exts = []
        if "utterance_id" in citation:
            sub_exts.append({"url": "utterance-id", "valueString": str(citation["utterance_id"])})
        if "speaker" in citation or "nguoi_noi" in citation:
            spk = citation.get("speaker") or citation.get("nguoi_noi")
            sub_exts.append({"url": "speaker-role", "valueCode": str(spk).upper()})
        if "start_ms" in citation or "bat_dau_ms" in citation:
            s_ms = citation.get("start_ms", citation.get("bat_dau_ms", 0))
            sub_exts.append({"url": "audio-timestamp-start-ms", "valueInteger": int(s_ms)})
        if "end_ms" in citation or "ket_thuc_ms" in citation:
            e_ms = citation.get("end_ms", citation.get("ket_thuc_ms", 0))
            sub_exts.append({"url": "audio-timestamp-end-ms", "valueInteger": int(e_ms)})
        if "quote" in citation or "trich_dan" in citation:
            q = citation.get("quote") or citation.get("trich_dan")
            sub_exts.append({"url": "verbatim-quote", "valueString": str(q)})
        if "confidence" in citation or "do_tin_cay" in citation:
            conf = citation.get("confidence", citation.get("do_tin_cay", 1.0))
            sub_exts.append({"url": "confidence-score", "valueDecimal": float(conf)})
        if "section" in citation or "phan_benh_an" in citation:
            sec = citation.get("section") or citation.get("phan_benh_an")
            sub_exts.append({"url": "document-section", "valueString": str(sec)})

        if not sub_exts:
            return None

        return {
            "url": cls.URI_CITATION_EXTENSION,
            "extension": sub_exts
        }

    @classmethod
    def _trich_xuat_ma_icd10(cls, text: str) -> str:
        """Trích xuất mã ICD-10 từ chuỗi chẩn đoán/tiền sử; fallback 'R69' nếu chưa nhận diện được."""
        chuoi = str(text or "").strip()
        if not chuoi:
            return "R69"

        m_icd = re.search(r"ICD-?10\s*[:：]?\s*([A-Z]\d{2}(?:\.\d{1,2})?)", chuoi, re.IGNORECASE)
        if m_icd:
            return m_icd.group(1).upper()

        m_ngoac = re.search(r"[\[(]\s*([A-Z]\d{2}(?:\.\d{1,2})?)\s*[\])]", chuoi)
        if m_ngoac:
            return m_ngoac.group(1).upper()

        chuoi_thuong = chuoi.lower()
        for ma_icd, _ten_byt, _khoa, tu_khoa_tuple in DANH_MUC_ICD10_BYT:
            if any(kw in chuoi_thuong for kw in tu_khoa_tuple):
                return ma_icd

        return "R69"

    @classmethod
    def xuat_fhir_bundle(
        cls,
        ma_ca: str,
        ban_nhap: Dict[str, Any],
        thong_tin_benh_nhan: Optional[Dict[str, Any]] = None,
        danh_sach_phat_bieu: Optional[List[Any]] = None,
        trich_dan_chung_cu: Optional[Dict[str, Any]] = None,
        thong_tin_bac_si: Optional[Dict[str, Any]] = None,
        du_lieu_xet_nghiem: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Tạo HL7 FHIR R4 Document Bundle từ kết quả xử lý của MediTrace Sentinel.
        
        Bao gồm đầy đủ 8 Resource cốt lõi theo quy định:
        Encounter, Condition, MedicationRequest, Observation (LOINC),
        AllergyIntolerance, Provenance, DocumentReference, Patient.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        bundle_id = f"bundle-{ma_ca}"
        comp_id = cls._tao_id("composition")
        patient_id = cls._tao_id("patient")
        encounter_id = cls._tao_id("encounter")
        trich_dan = dict(trich_dan_chung_cu) if isinstance(trich_dan_chung_cu, dict) else {}
        bs_info = thong_tin_bac_si or {}
        
        # Tự động trích xuất metadata trích dẫn hai chiều từ danh_sach_phat_bieu nếu có
        if danh_sach_phat_bieu:
            for p in danh_sach_phat_bieu:
                spans = getattr(p, "audio_spans", None) or []
                spk = getattr(p, "nguoi_noi", "PATIENT")
                muc = getattr(p, "muc", "")
                t_dan = getattr(p, "trich_dan", [])
                quote = spans[0].get("exact_quote") if spans else (t_dan[0] if t_dan else getattr(p, "noi_dung", ""))
                s_ms = spans[0].get("start_ms", 0) if spans else 0
                e_ms = spans[0].get("end_ms", 0) if spans else 0
                
                cite_obj = {
                    "utterance_id": f"utt_{getattr(p, 'id', 1):04d}",
                    "speaker": str(spk).upper(),
                    "start_ms": s_ms,
                    "end_ms": e_ms,
                    "quote": quote,
                    "confidence": 0.98,
                    "section": muc or "LÂM SÀNG"
                }
                
                nd_low = str(getattr(p, "noi_dung", "")).lower()
                if "chan_doan" not in trich_dan and ("chẩn đoán" in muc.lower() or "viêm" in nd_low or "tăng huyết áp" in nd_low):
                    trich_dan["chan_doan"] = cite_obj
                elif "di_ung" not in trich_dan and ("dị ứng" in muc.lower() or "dị ứng" in nd_low) and getattr(p, "chu_the_id", 0) == 0:
                    trich_dan["di_ung"] = cite_obj
                elif "tien_su_gia_dinh" not in trich_dan and ("gia đình" in muc.lower() or getattr(p, "chu_the_id", 0) != 0):
                    trich_dan["tien_su_gia_dinh"] = cite_obj
                elif "sinh_hieu" not in trich_dan and ("sinh hiệu" in muc.lower() or "huyết áp" in nd_low or "mạch" in nd_low):
                    trich_dan["sinh_hieu"] = cite_obj
                elif "ke_hoach_dieu_tri" not in trich_dan and ("kế hoạch" in muc.lower() or "uống" in nd_low or "kê" in nd_low):
                    trich_dan["ke_hoach_dieu_tri"] = cite_obj
        
        # Danh sách ID toàn bộ tài nguyên để bảo đảm tính toàn vẹn tham chiếu chéo trong Provenance
        all_res_ids: List[str] = [comp_id, patient_id, encounter_id]

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
                "system": "https://meditrace.example/fhir/NamingSystem/patient-id",
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

        # 2. Tạo Resource: Encounter (Lượt khám ngoại trú)
        ly_do = ban_nhap.get("LÝ DO KHÁM", "") or ban_nhap.get("ly_do_kham", "Khám nội tổng quát ngoại trú")
        encounter_resource = {
            "resourceType": "Encounter",
            "id": encounter_id,
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory"
            },
            "subject": {"reference": f"urn:uuid:{patient_id}"},
            "period": {
                "start": now_iso,
                "end": now_iso
            },
            "reasonCode": [{
                "text": str(ly_do).strip()
            }],
            "serviceType": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/service-type",
                    "code": "general-practice",
                    "display": "Khám Bệnh Đa Khoa / Ngoại Trú"
                }]
            }
        }
        cite_enc = cls._tao_citation_extension(trich_dan.get("ly_do_kham") or trich_dan.get("encounter"))
        if cite_enc:
            encounter_resource["extension"] = [cite_enc]
        entries.append({"fullUrl": f"urn:uuid:{encounter_id}", "resource": encounter_resource})

        # 3. Tạo Resource: Condition (Chẩn đoán & Tiền sử bệnh)
        chan_doan_text = ban_nhap.get("CHẨN ĐOÁN", "") or ban_nhap.get("chan_doan", "")
        if chan_doan_text:
            cond_id = cls._tao_id("condition")
            all_res_ids.append(cond_id)
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
                        "code": cls._trich_xuat_ma_icd10(str(chan_doan_text)),
                        "display": str(chan_doan_text).strip()
                    }]
                },
                "subject": {"reference": f"urn:uuid:{patient_id}"},
                "encounter": {"reference": f"urn:uuid:{encounter_id}"},
                "recordedDate": now_iso
            }
            cite_cd = cls._tao_citation_extension(trich_dan.get("chan_doan"))
            if cite_cd:
                cond_res["extension"] = [cite_cd]
            entries.append({"fullUrl": f"urn:uuid:{cond_id}", "resource": cond_res})

        # Tiền sử bệnh
        tien_su = ban_nhap.get("TIỀN SỬ BỆNH", "") or ban_nhap.get("tien_su_benh", "")
        if tien_su:
            ts_id = cls._tao_id("condition-history")
            all_res_ids.append(ts_id)
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
                "code": {
                    "text": str(tien_su).strip(),
                    "coding": [{
                        "system": "http://hl7.org/fhir/sid/icd-10",
                        "code": cls._trich_xuat_ma_icd10(str(tien_su)),
                        "display": str(tien_su).strip()
                    }]
                },
                "subject": {"reference": f"urn:uuid:{patient_id}"},
                "encounter": {"reference": f"urn:uuid:{encounter_id}"}
            }
            cite_ts = cls._tao_citation_extension(trich_dan.get("tien_su_benh"))
            if cite_ts:
                ts_res["extension"] = [cite_ts]
            entries.append({"fullUrl": f"urn:uuid:{ts_id}", "resource": ts_res})

        # Tiền sử gia đình (FamilyMemberHistory) nếu có
        tien_su_gd = ban_nhap.get("TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", "") or ban_nhap.get("tien_su_gia_dinh", "")
        if tien_su_gd:
            fmh_id = cls._tao_id("family-history")
            all_res_ids.append(fmh_id)
            fmh_res = {
                "resourceType": "FamilyMemberHistory",
                "id": fmh_id,
                "status": "completed",
                "patient": {"reference": f"urn:uuid:{patient_id}"},
                "relationship": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                        "code": "FAMMEMB",
                        "display": "Family Member"
                    }],
                    "text": "Người nhà / Thân nhân"
                },
                "note": [{"text": str(tien_su_gd).strip()}]
            }
            cite_fmh = cls._tao_citation_extension(trich_dan.get("tien_su_gia_dinh"))
            if cite_fmh:
                fmh_res["extension"] = [cite_fmh]
            entries.append({"fullUrl": f"urn:uuid:{fmh_id}", "resource": fmh_res})

        # 4. Tạo Resource: AllergyIntolerance (Dị ứng thuốc/thức ăn — bỏ qua khi mang nghĩa phủ định/chưa ghi nhận)
        di_ung = ban_nhap.get("DỊ ỨNG", "") or ban_nhap.get("di_ung", "")
        if di_ung and not cls._la_di_ung_phu_dinh(di_ung):
            di_ung_khong_ro = cls._la_di_ung_khong_ro(di_ung)
            al_id = cls._tao_id("allergy")
            all_res_ids.append(al_id)
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
                        # tiền sử dị ứng chưa rõ -> unconfirmed, không ngầm định là không dị ứng
                        "code": "unconfirmed" if di_ung_khong_ro else "confirmed",
                        "display": "Unconfirmed" if di_ung_khong_ro else "Confirmed"
                    }]
                },
                "type": "allergy",
                "criticality": "unable-to-assess" if di_ung_khong_ro else "high",
                "code": {"text": ("Chưa rõ tiền sử dị ứng: " if di_ung_khong_ro else "") + str(di_ung).strip()},
                "patient": {"reference": f"urn:uuid:{patient_id}"},
                "recordedDate": now_iso
            }
            cite_al = cls._tao_citation_extension(trich_dan.get("di_ung"))
            if cite_al:
                al_res["extension"] = [cite_al]
            entries.append({"fullUrl": f"urn:uuid:{al_id}", "resource": al_res})

        # 5. Tạo Resource: MedicationRequest (CHỈ tạo y lệnh order khi có thuoc_ke_don thực sự;
        # tuyệt đối không lấy thuoc_hien_tai gán thành y lệnh mới intent="order")
        thuoc_ke_don = str(ban_nhap.get("KẾ HOẠCH ĐIỀU TRỊ", "") or ban_nhap.get("ke_hoach_dieu_tri", "") or "").strip()
        thuoc_hien_tai = str(ban_nhap.get("THUỐC ĐANG DÙNG", "") or ban_nhap.get("thuoc_dang_dung", "") or "").strip()

        if thuoc_ke_don:
            med_req_id = cls._tao_id("medication-request")
            all_res_ids.append(med_req_id)
            med_req_res = {
                "resourceType": "MedicationRequest",
                "id": med_req_id,
                "status": "active",
                "intent": "order",
                "subject": {"reference": f"urn:uuid:{patient_id}"},
                "encounter": {"reference": f"urn:uuid:{encounter_id}"},
                "authoredOn": now_iso,
                "medicationCodeableConcept": {
                    "text": thuoc_ke_don,
                    "coding": [{
                        "system": "https://dav.gov.vn/drug-codes",
                        "display": thuoc_ke_don
                    }]
                },
                "dosageInstruction": [{
                    "text": thuoc_ke_don
                }]
            }
            cite_med = cls._tao_citation_extension(trich_dan.get("ke_hoach_dieu_tri") or trich_dan.get("thuoc"))
            if cite_med:
                med_req_res["extension"] = [cite_med]
            entries.append({"fullUrl": f"urn:uuid:{med_req_id}", "resource": med_req_res})

        # MedicationStatement cho thuốc đang dùng (không mang intent="order")
        if thuoc_hien_tai:
            med_id = cls._tao_id("medication")
            all_res_ids.append(med_id)
            med_res = {
                "resourceType": "MedicationStatement",
                "id": med_id,
                "status": "active",
                "medicationCodeableConcept": {"text": thuoc_hien_tai},
                "subject": {"reference": f"urn:uuid:{patient_id}"},
                "effectiveDateTime": now_iso
            }
            entries.append({"fullUrl": f"urn:uuid:{med_id}", "resource": med_res})

        # 6. Tạo Resource: Observation (Dấu hiệu sinh tồn & Xét nghiệm mã hóa LOINC)
        sinh_hieu = ban_nhap.get("SINH HIỆU", "") or ban_nhap.get("sinh_hieu", "")
        if sinh_hieu:
            obs_id = cls._tao_id("observation-vitals")
            all_res_ids.append(obs_id)
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
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "85354-9",
                        "display": "Blood pressure panel with all children optional"
                    }],
                    "text": "Sinh hiệu lâm sàng"
                },
                "subject": {"reference": f"urn:uuid:{patient_id}"},
                "encounter": {"reference": f"urn:uuid:{encounter_id}"},
                "valueString": str(sinh_hieu).strip(),
                "effectiveDateTime": now_iso
            }
            cite_obs = cls._tao_citation_extension(trich_dan.get("sinh_hieu"))
            if cite_obs:
                obs_res["extension"] = [cite_obs]
            entries.append({"fullUrl": f"urn:uuid:{obs_id}", "resource": obs_res})

        # Tạo thêm các Resource: Observation cho kết quả xét nghiệm cận lâm sàng (mã hóa LOINC chuẩn)
        # Hỗ trợ đồng thời cả `du_lieu_xet_nghiem` độc lập lẫn `thong_tin_benh_nhan["xet_nghiem"]`
        lab_src: Dict[str, Any] = {}
        if isinstance(thong_tin_benh_nhan, dict):
            for k_bn, v_bn in thong_tin_benh_nhan.items():
                if k_bn not in ("id", "ten", "ho_ten", "gioi_tinh", "tuoi", "la_nu", "xet_nghiem", "du_lieu_xet_nghiem", "thang_diem", "benh_nen", "tien_su_benh"):
                    lab_src[k_bn] = v_bn
            for nested_key in ("xet_nghiem", "du_lieu_xet_nghiem"):
                if isinstance(thong_tin_benh_nhan.get(nested_key), dict):
                    for k_xn, v_xn in thong_tin_benh_nhan[nested_key].items():
                        if v_xn is not None:
                            lab_src.setdefault(k_xn, v_xn)
        if isinstance(du_lieu_xet_nghiem, dict):
            for k_xn, v_xn in du_lieu_xet_nghiem.items():
                if v_xn is not None:
                    lab_src[k_xn] = v_xn

        if lab_src:
            lab_norm = chuan_hoa_du_lieu_xet_nghiem(lab_src)
            if "creatinine_mg_dl" in lab_norm:
                lab_norm["creatinine"] = lab_norm["creatinine_mg_dl"]
            if "glucose_mg_dl" in lab_norm:
                lab_norm["glucose"] = lab_norm["glucose_mg_dl"]
            if "urea_mmol_l" in lab_norm:
                lab_norm["urea"] = lab_norm["urea_mmol_l"]
            if "kali" not in lab_norm and lab_norm.get("k") is not None:
                lab_norm["kali"] = lab_norm["k"]
            if "wbc" not in lab_norm and lab_norm.get("bach_cau") is not None:
                lab_norm["wbc"] = lab_norm["bach_cau"]
            if "hb" not in lab_norm and lab_norm.get("hemoglobin") is not None:
                lab_norm["hb"] = lab_norm["hemoglobin"]
            if "troponin" not in lab_norm:
                for k_tr in ("troponin_t", "troponin_i"):
                    if lab_norm.get(k_tr) is not None:
                        lab_norm["troponin"] = lab_norm[k_tr]
                        break
            for lab_key, lab_meta in cls.BANG_MA_LOINC.items():
                if lab_key in lab_norm and lab_norm[lab_key] is not None:
                    val = lab_norm[lab_key]
                    lab_obs_id = cls._tao_id(f"obs-{lab_key}")
                    all_res_ids.append(lab_obs_id)
                    lab_obs_res = {
                        "resourceType": "Observation",
                        "id": lab_obs_id,
                        "status": "final",
                        "category": [{
                            "coding": [{
                                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                                "code": "laboratory",
                                "display": "Laboratory"
                            }]
                        }],
                        "code": {
                            "coding": [{
                                "system": "http://loinc.org",
                                "code": lab_meta["code"],
                                "display": lab_meta["display"]
                            }],
                            "text": lab_meta["display"]
                        },
                        "subject": {"reference": f"urn:uuid:{patient_id}"},
                        "encounter": {"reference": f"urn:uuid:{encounter_id}"},
                        "effectiveDateTime": now_iso
                    }
                    if isinstance(val, (int, float)) and not isinstance(val, bool):
                        lab_obs_res["valueQuantity"] = {
                            "value": float(val),
                            "unit": lab_meta["unit"],
                            "system": "http://unitsofmeasure.org",
                            "code": lab_meta["unit"]
                        }
                    else:
                        lab_obs_res["valueString"] = str(val)
                    entries.append({"fullUrl": f"urn:uuid:{lab_obs_id}", "resource": lab_obs_res})

        # 7. Tạo Resource: DocumentReference (Tài liệu hồ sơ bệnh án chuẩn EMR)
        doc_ref_id = cls._tao_id("docref")
        all_res_ids.append(doc_ref_id)
        raw_markdown = json.dumps(ban_nhap, ensure_ascii=False, indent=2)
        b64_content = base64.b64encode(raw_markdown.encode("utf-8")).decode("ascii")
        doc_ref_res = {
            "resourceType": "DocumentReference",
            "id": doc_ref_id,
            "status": "current",
            "docStatus": "preliminary",
            "type": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "11488-4",
                    "display": "Consultation note"
                }],
                "text": "Bản nháp hồ sơ khám bệnh điện tử MediTrace Sentinel"
            },
            "category": [{
                "coding": [{
                    "system": "http://hl7.org/fhir/us/core/CodeSystem/us-core-documentreference-category",
                    "code": "clinical-note",
                    "display": "Clinical Note"
                }]
            }],
            "subject": {"reference": f"urn:uuid:{patient_id}"},
            "date": now_iso,
            "context": {
                "encounter": [{"reference": f"urn:uuid:{encounter_id}"}]
            },
            "content": [{
                "attachment": {
                    "contentType": "text/markdown; charset=utf-8",
                    "title": f"Bệnh án ngoại trú ca {ma_ca}",
                    "data": b64_content
                }
            }]
        }
        entries.append({"fullUrl": f"urn:uuid:{doc_ref_id}", "resource": doc_ref_res})

        # 8. Tạo Resource: Provenance (Nguồn gốc chứng thực, chữ ký số và vết kiểm toán)
        prov_id = cls._tao_id("provenance")
        all_res_ids.append(prov_id)
        # Băm SHA-256 nội dung bản nháp để bảo toàn tính toàn vẹn (Integrity Hash)
        digest = hashlib.sha256(raw_markdown.encode("utf-8")).hexdigest()
        cchn_bac_si = str(bs_info.get("cchn", "CCHN-PENDING-APPROVAL"))
        ten_bac_si = str(bs_info.get("ho_ten", "Bác sĩ lâm sàng phụ trách"))

        prov_res = {
            "resourceType": "Provenance",
            "id": prov_id,
            "target": [{"reference": f"urn:uuid:{rid}"} for rid in all_res_ids if rid != prov_id],
            "recorded": now_iso,
            "reason": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActReason",
                    "code": "CLINNOTEE",
                    "display": "clinical note entry"
                }]
            }],
            "agent": [
                {
                    "type": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
                            "code": "author",
                            "display": "Author"
                        }]
                    },
                    "who": {
                        "display": "MediTrace AI Sentinel v2.4 (Clinical Documentation Assistant)"
                    }
                },
                {
                    "type": {
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/provenance-participant-type",
                            "code": "verifier",
                            "display": "Verifier"
                        }]
                    },
                    "who": {
                        "identifier": {
                            "system": "https://moh.gov.vn/cchn",
                            "value": cchn_bac_si
                        },
                        "display": ten_bac_si
                    }
                }
            ],
            "entity": [{
                "role": "source",
                "what": {
                    "identifier": {
                        "system": "https://meditrace.vn/audio-recordings",
                        "value": f"audio-{ma_ca}.wav"
                    },
                    "display": "Bản ghi âm hội thoại khám bệnh gốc"
                }
            }],
            "signature": [{
                "type": [{
                    "system": "urn:iso-astm:E1762-95:2013",
                    "code": "1.2.840.10065.1.12.1.1",
                    "display": "Author's Signature"
                }],
                "when": now_iso,
                "who": {"display": "MediTrace Sentinel Engine"},
                "data": digest
            }]
        }
        entries.append({"fullUrl": f"urn:uuid:{prov_id}", "resource": prov_res})

        # 9. Tạo Resource: Composition (Bản tóm tắt bệnh án gốc gắn kết toàn bộ các tài nguyên)
        comp_sections = [
            {
                "title": "Bệnh sử hiện tại",
                "text": {"status": "generated", "div": cls._xhtml(ban_nhap.get("BỆNH SỬ HIỆN TẠI", ""))}
            },
            {
                "title": "Khám lâm sàng",
                "text": {"status": "generated", "div": cls._xhtml(ban_nhap.get("KHÁM LÂM SÀNG", ""))}
            },
            {
                "title": "Kế hoạch điều trị",
                "text": {"status": "generated", "div": cls._xhtml(ban_nhap.get("KẾ HOẠCH ĐIỀU TRỊ", ""))}
            },
            {
                "title": "Mục cần bác sĩ xác nhận",
                "text": {"status": "generated", "div": cls._xhtml(ban_nhap.get("CẦN XÁC NHẬN", ""))}
            }
        ]
        if tien_su_gd:
            comp_sections.append({
                "title": "Tiền sử gia đình và xã hội",
                "text": {"status": "generated", "div": cls._xhtml(tien_su_gd)}
            })

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
            "encounter": {"reference": f"urn:uuid:{encounter_id}"},
            "date": now_iso,
            "title": f"Bệnh án ngoại trú ca {ma_ca}",
            "section": comp_sections
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
