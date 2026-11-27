# -*- coding: utf-8 -*-
"""Kiểm thử khớp Schema Contract giữa Python (`src/he_thong/hop_dong_api.py`) và TypeScript (`web/src/types/api-contract.ts`)."""
import re
from pathlib import Path

from src.he_thong.hop_dong_api import CONTRACT_SCHEMA, validate_contract_keys
from src.cong_cu_lam_sang.tien_kiem_bhyt_va_khoi_phuc_bo_sot import (
    ClinicalHarmWeightedEvaluator,
    tien_kiem_bhyt_tu_du_lieu,
)
from src.cong_cu_lam_sang.doc_phieu_xet_nghiem import boc_tach_phieu_cu

ROOT = Path(__file__).resolve().parent.parent
TS_CONTRACT_PATH = ROOT / "web" / "src" / "types" / "api-contract.ts"


def test_ts_contract_file_ton_tai_va_khop_tat_ca_interface():
    assert TS_CONTRACT_PATH.exists(), f"Thiếu {TS_CONTRACT_PATH}"
    ts_src = TS_CONTRACT_PATH.read_text(encoding="utf-8")

    for iface_name, spec in CONTRACT_SCHEMA.items():
        pattern = rf"export\s+interface\s+{re.escape(iface_name)}\s*\{{([\s\S]*?)\n\}}"
        m = re.search(pattern, ts_src)
        assert m is not None, f"Thiếu interface `{iface_name}` trong {TS_CONTRACT_PATH.name}"
        body = m.group(1)
        for field in spec["required"]:
            field_pat = rf"\b{re.escape(field)}\s*\??:"
            assert re.search(field_pat, body) is not None, (
                f"Trường `{field}` trong `{iface_name}` có ở Python nhưng thiếu ở TypeScript"
            )


def test_validate_contract_keys_phat_hien_thieu_truong():
    missing = validate_contract_keys({"ok": True}, "PyHealthResponse")
    assert "mo_hinh" in missing
    assert "ok" not in missing


def test_bhyt_precheck_output_khop_contract():
    kq = tien_kiem_bhyt_tu_du_lieu(
        [{"id": 1, "text": "Bệnh nhân tăng huyết áp độ 2", "section": "CHẨN ĐOÁN", "status": "than"}],
        "Bác sĩ: Tăng huyết áp độ 2.",
    )
    assert validate_contract_keys(kq, "PyBhytPrecheckResponse") == []


def test_ocr_phieu_cu_output_khop_contract():
    kq = boc_tach_phieu_cu(
        van_ban="Creatinin 180 umol/L, Metformin 500mg ngày 2 lần",
        tuoi=65,
        la_nu=False,
    )
    assert validate_contract_keys(kq, "PyOcrPhieuCuResponse") == []


def test_error_attribution_output_khop_contract():
    quy_ket = ClinicalHarmWeightedEvaluator.quy_ket_nguoc_tang_loi(
        thao_tac_bac_si="sua",
        menh_de_goc={"text": "Đau ngực", "section": "BỆNH SỬ"},
        menh_de_sua={"text": "Không đau ngực", "section": "BỆNH SỬ"},
    )
    payload = {"ok": True, "quy_ket": quy_ket}
    assert validate_contract_keys(payload, "PyErrorAttributionResponse") == []
