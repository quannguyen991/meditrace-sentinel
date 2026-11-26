# -*- coding: utf-8 -*-
"""Unit tests for M4 Python integration: LIS HL7 ORU^R01 parser, Trie Biasing, and API endpoints."""
import json
import pytest

from src.lis_hl7_oru import phan_tich_lis_dau_vao
from src.audio.asr.contextual_trie_600 import ContextualPrefixTrie600, tao_trie_logits_processor
from src.dieu_phoi_ha_tang import tai_kiem_tra_nhanh


def test_lis_hl7_oru_r01_parsing():
    hl7_msg = (
        "MSH|^~\\&|LIS|BV_DA_KHOA|MEDITRACE|MEDITRACE|20261126120000||ORU^R01|MSG0001|P|2.3\r\n"
        "PID|1||BN123456||NGUYEN VAN A||19650101|M\r\n"
        "OBR|1|ORD001|LAB001|LAB_PANEL^Sinh Hoa Mau|||20261126110000\r\n"
        "OBX|1|NM|2160-0^Creatinine^LN||165|umol/L|62-106|H|||F\r\n"
        "OBX|2|NM|2823-3^Potassium^LN||6.5|mmol/L|3.5-5.0|HH|||F\r\n"
        "OBX|3|NM|6598-7^Troponin T^LN||0.08|ng/mL|0-0.014|H|||F\r\n"
    )
    res = phan_tich_lis_dau_vao(hl7_msg)
    assert res["dinh_dang"] == "HL7_ORU_R01"
    assert len(res["ban_ghi_obx"]) == 3
    assert res["chi_so"]["creatinine"] == 165
    assert res["chi_so"]["kali"] == 6.5
    assert res["chi_so"]["troponin"] == 0.08
    # Troponin & Kali HH should trigger critical panic flags in doi_soat_can_lam_sang
    cls = res["doi_soat_can_lam_sang"]
    assert cls["co_gia_tri_nguy_kich"] is True
    assert any("kali" in str(cb).lower() or "troponin" in str(cb).lower() for cb in cls.get("bao_dong_do_khan_cap", []))


def test_lis_csv_and_json_parsing():
    csv_msg = (
        "Chi so,Gia tri,Don vi\n"
        "Creatinine,120,umol/L\n"
        "Kali,4.2,mmol/L\n"
        "eGFR,55,mL/min/1.73m2\n"
    )
    res_csv = phan_tich_lis_dau_vao(csv_msg)
    assert res_csv["dinh_dang"] == "CSV"
    assert res_csv["chi_so"]["creatinine"] == 120
    assert res_csv["chi_so"]["kali"] == 4.2
    assert res_csv["chi_so"]["egfr"] == 55

    json_msg = json.dumps({
        "ket_qua": [
            {"ma": "2160-0", "ten": "Creatinine", "gia_tri": 130, "don_vi": "umol/L"},
            {"ma": "2823-3", "ten": "Kali", "gia_tri": 4.5, "don_vi": "mmol/L"}
        ]
    })
    res_json = phan_tich_lis_dau_vao(json_msg)
    assert res_json["dinh_dang"] == "JSON"
    assert res_json["chi_so"]["creatinine"] == 130
    assert res_json["chi_so"]["kali"] == 4.5


def test_tao_trie_logits_processor_graceful():
    trie = ContextualPrefixTrie600()
    trie.nap_khuon_benh([
        {"ma": "I10", "ten": "Tăng huyết áp vô căn", "he_co_quan": "tim_mach", "trieu_chung": ["chóng mặt", "đau đầu"]}
    ])
    # With dummy tokenizer or None
    assert tao_trie_logits_processor(None, None) is None
    assert tao_trie_logits_processor(trie, None) is None


def test_tai_kiem_tra_nhanh_deterministic():
    propositions = [
        {"id": 1, "text": "Bệnh nhân có tiền sử dị ứng penicillin", "certainty": "khang_dinh"},
        {"id": 2, "text": "Chỉ định Amoxicillin 500mg 2 viên/ngày", "drug": {"ten": "Amoxicillin", "hoat_chat": "amoxicillin"}},
    ]
    res = tai_kiem_tra_nhanh(
        propositions=propositions,
        danh_sach_di_ung=["penicillin"],
        danh_sach_thuoc=["amoxicillin"],
        transcript="Bệnh nhân dị ứng penicillin",
    )
    assert res["thoi_gian_ms"] < 200
    # Allergen cross-reaction should be detected deterministically
    assert len(res["di_ung_cheo"]) > 0
    assert any("amoxicillin" in str(x).lower() and "penicillin" in str(x).lower() for x in res["di_ung_cheo"])
    assert res["hop_le_lam_sang"] is False
