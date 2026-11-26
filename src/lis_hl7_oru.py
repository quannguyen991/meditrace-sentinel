# -*- coding: utf-8 -*-
"""HL7 v2 ORU^R01, JSON & CSV LIS Ingest (Deterministically Parsed).

Phân tích dữ liệu xét nghiệm từ hệ thống LIS (HL7 v2 ORU^R01, CSV, hoặc JSON),
chuẩn hóa mã LOINC / tên xét nghiệm và đơn vị nội bộ qua
`src.chuan_hoa_don_vi_xet_nghiem.chuan_hoa_du_lieu_xet_nghiem`,
và tự động chạy `ParaclinicalCorrelator.phan_tich_xet_nghiem` để phát hiện
cảnh báo giá trị nguy kịch (panic flags).

Hoàn toàn xác định 100% (0 LLM). Hỗ trợ CLI `--parse` đọc stdin JSON `{"text": ...}`.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import unicodedata
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Tuple

from src.can_lam_sang import ParaclinicalCorrelator
from src.chuan_hoa_don_vi_xet_nghiem import chuan_hoa_du_lieu_xet_nghiem


def _bo_dau_va_chuan_hoa(text: str) -> str:
    s = unicodedata.normalize("NFD", str(text or ""))
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = s.replace("đ", "d").replace("Đ", "D")
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


# Ánh xạ mã LOINC & tên tiếng Việt/Anh về khóa chuẩn nội bộ
_LOINC_VA_TEN_CHUAN: Dict[str, str] = {
    # Creatinine
    "2160-0": "creatinine",
    "creatinine": "creatinine",
    "creatinin": "creatinine",
    "creat": "creatinine",
    "scr": "creatinine",
    # eGFR
    "98979-8": "egfr",
    "33914-3": "egfr",
    "48642-3": "egfr",
    "egfr": "egfr",
    "gfr": "egfr",
    "mlct": "egfr",
    # Kali (K+)
    "2823-3": "kali",
    "6298-4": "kali",
    "kali": "kali",
    "k+": "kali",
    "k": "kali",
    "potassium": "kali",
    # Troponin
    "6598-7": "troponin",
    "10839-9": "troponin",
    "89579-7": "troponin",
    "troponin": "troponin",
    "troponin t": "troponin",
    "troponin i": "troponin",
    "hs-troponin": "troponin",
    "hs troponin": "troponin",
    "trop": "troponin",
    # WBC
    "6690-2": "wbc",
    "26464-8": "wbc",
    "wbc": "wbc",
    "bach cau": "wbc",
    "leukocytes": "wbc",
    "white blood cells": "wbc",
    # Hemoglobin
    "718-7": "hb",
    "hb": "hb",
    "hgb": "hb",
    "hemoglobin": "hb",
    "huyet sac to": "hb",
    # Platelets
    "777-3": "plt",
    "26515-7": "plt",
    "plt": "plt",
    "tieu cau": "plt",
    "platelets": "plt",
    # Urea / BUN
    "3091-6": "urea",
    "3094-0": "bun",
    "urea": "urea",
    "ure": "urea",
    "bun": "bun",
    # AST / ALT
    "1920-8": "ast",
    "ast": "ast",
    "sgot": "ast",
    "got": "ast",
    "1742-6": "alt",
    "alt": "alt",
    "sgpt": "alt",
    "gpt": "alt",
    # HbA1c
    "4548-4": "hba1c",
    "hba1c": "hba1c",
    "a1c": "hba1c",
    # Glucose
    "1558-6": "glucose",
    "2345-7": "glucose",
    "2339-0": "glucose",
    "glucose": "glucose",
    "duong huyet": "glucose",
    "glu": "glucose",
    # CRP
    "1988-5": "crp",
    "30522-7": "crp",
    "crp": "crp",
    "hs-crp": "crp",
    # INR
    "6301-6": "inr",
    "34714-6": "inr",
    "inr": "inr",
    # Natri (Na+)
    "2951-2": "na",
    "2947-0": "na",
    "na": "na",
    "na+": "na",
    "natri": "na",
    "sodium": "na",
}

_KHOA_CO_DON_VI = {"creatinine", "glucose", "urea", "bun"}


def chuan_hoa_ma_chi_so(ma_hoac_ten: str) -> str:
    """Chuẩn hóa mã LOINC hoặc tên xét nghiệm về khóa nội bộ thống nhất."""
    raw = str(ma_hoac_ten or "").strip()
    if not raw:
        return ""
    norm = _bo_dau_va_chuan_hoa(raw)
    if norm in _LOINC_VA_TEN_CHUAN:
        return _LOINC_VA_TEN_CHUAN[norm]
    # Khớp tiền tố/từ khóa nếu tên có chú thích thêm (vd "Troponin T hs", "Glucose máu")
    for k, v in _LOINC_VA_TEN_CHUAN.items():
        if len(k) >= 3 and re.search(rf"(?:^|\b){re.escape(k)}(?:$|\b)", norm):
            return v
    return re.sub(r"[^a-z0-9_]+", "_", norm).strip("_")


def _ep_gia_tri(val: Any) -> Any:
    if val is None or isinstance(val, bool):
        return None
    if isinstance(val, (int, float)):
        return val
    s = str(val).strip()
    if not s:
        return None
    # Xử lý dấu thập phân phẩy nếu là số
    s_num = s.replace(",", ".")
    try:
        f = float(s_num)
        return int(f) if f.is_integer() and "." not in s_num else f
    except ValueError:
        return s


def _ghi_chi_so_vao_dict(
    chi_so: Dict[str, Any],
    ma_chuan: str,
    gia_tri: Any,
    don_vi: str = "",
) -> None:
    if not ma_chuan or gia_tri is None:
        return
    chi_so[ma_chuan] = gia_tri
    if don_vi and ma_chuan in _KHOA_CO_DON_VI:
        chi_so[f"{ma_chuan}_unit"] = don_vi


def _phan_tich_hl7_oru(noi_dung: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    chi_so: Dict[str, Any] = {}
    ban_ghi_obx: List[Dict[str, Any]] = []
    lines = [ln.strip() for ln in re.split(r"[\r\n]+", noi_dung) if ln.strip()]

    for ln in lines:
        fields = ln.split("|")
        seg = fields[0].strip().upper()
        if seg != "OBX":
            continue
        stt = fields[1].strip() if len(fields) > 1 else ""
        loai_gt = fields[2].strip() if len(fields) > 2 else ""
        obs_id = fields[3].strip() if len(fields) > 3 else ""
        val_raw = fields[5].strip() if len(fields) > 5 else ""
        unit_raw = fields[6].strip() if len(fields) > 6 else ""
        ref_range = fields[7].strip() if len(fields) > 7 else ""
        flag = fields[8].strip() if len(fields) > 8 else ""
        status = fields[11].strip() if len(fields) > 11 else ""

        obs_parts = obs_id.split("^")
        ma_loinc = obs_parts[0].strip() if len(obs_parts) >= 1 else ""
        ten_goc = obs_parts[1].strip() if len(obs_parts) >= 2 and obs_parts[1].strip() else ma_loinc
        don_vi = unit_raw.split("^")[0].strip() if unit_raw else ""

        ma_chuan = chuan_hoa_ma_chi_so(ma_loinc)
        if ma_chuan == _bo_dau_va_chuan_hoa(ma_loinc).replace("-", "_") and ten_goc:
            ma_tu_ten = chuan_hoa_ma_chi_so(ten_goc)
            if ma_tu_ten:
                ma_chuan = ma_tu_ten

        val_clean = val_raw.split("^")[0].strip() if "^" in val_raw else val_raw
        gia_tri = _ep_gia_tri(val_clean)

        _ghi_chi_so_vao_dict(chi_so, ma_chuan, gia_tri, don_vi)
        ban_ghi_obx.append({
            "stt": stt,
            "loai_gia_tri": loai_gt,
            "ma_loinc": ma_loinc,
            "ten_goc": ten_goc,
            "ma_chuan": ma_chuan,
            "gia_tri": gia_tri,
            "don_vi": don_vi,
            "khoang_tham_chieu": ref_range,
            "co_bat_thuong": flag,
            "trang_thai": status,
        })

    return chi_so, ban_ghi_obx


def _phan_tich_json_lis(obj: Any) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    chi_so: Dict[str, Any] = {}
    ban_ghi_obx: List[Dict[str, Any]] = []

    items: List[Dict[str, Any]] = []
    if isinstance(obj, dict):
        for key in ("ban_ghi_obx", "obx", "results", "ket_qua", "tests", "items", "danh_sach"):
            if isinstance(obj.get(key), list):
                items = [x for x in obj[key] if isinstance(x, dict)]
                break
        if not items:
            src_dict = obj.get("chi_so") if isinstance(obj.get("chi_so"), dict) else (
                obj.get("labs") if isinstance(obj.get("labs"), dict) else (
                    obj.get("xet_nghiem") if isinstance(obj.get("xet_nghiem"), dict) else obj
                )
            )
            for idx, (k, v) in enumerate(src_dict.items(), start=1):
                if isinstance(v, dict):
                    val = v.get("gia_tri") if v.get("gia_tri") is not None else v.get("value")
                    dv = str(v.get("don_vi") or v.get("unit") or "")
                    ref = str(v.get("khoang_tham_chieu") or v.get("reference_range") or "")
                    flag = str(v.get("co_bat_thuong") or v.get("flag") or "")
                    items.append({
                        "stt": str(idx),
                        "code": k,
                        "name": v.get("ten") or k,
                        "value": val,
                        "unit": dv,
                        "reference_range": ref,
                        "flag": flag,
                    })
                else:
                    ma_chuan = chuan_hoa_ma_chi_so(str(k))
                    gia_tri = _ep_gia_tri(v)
                    if str(k).endswith("_unit") or str(k).endswith("_don_vi"):
                        chi_so[str(k)] = v
                        continue
                    _ghi_chi_so_vao_dict(chi_so, ma_chuan, gia_tri, "")
                    ban_ghi_obx.append({
                        "stt": str(idx),
                        "loai_gia_tri": "NM" if isinstance(gia_tri, (int, float)) else "ST",
                        "ma_loinc": str(k),
                        "ten_goc": str(k),
                        "ma_chuan": ma_chuan,
                        "gia_tri": gia_tri,
                        "don_vi": "",
                        "khoang_tham_chieu": "",
                        "co_bat_thuong": "",
                        "trang_thai": "F",
                    })
            if not items:
                return chi_so, ban_ghi_obx
    elif isinstance(obj, list):
        items = [x for x in obj if isinstance(x, dict)]

    for idx, it in enumerate(items, start=1):
        ma_raw = str(it.get("ma_loinc") or it.get("code") or it.get("chi_so") or it.get("name") or it.get("ten") or "")
        ten_goc = str(it.get("ten_goc") or it.get("name") or it.get("ten") or ma_raw)
        ma_chuan = chuan_hoa_ma_chi_so(ma_raw) or chuan_hoa_ma_chi_so(ten_goc)
        val_raw = it.get("gia_tri") if it.get("gia_tri") is not None else it.get("value")
        gia_tri = _ep_gia_tri(val_raw)
        don_vi = str(it.get("don_vi") or it.get("unit") or "").strip()
        ref = str(it.get("khoang_tham_chieu") or it.get("reference_range") or "").strip()
        flag = str(it.get("co_bat_thuong") or it.get("flag") or "").strip()

        _ghi_chi_so_vao_dict(chi_so, ma_chuan, gia_tri, don_vi)
        ban_ghi_obx.append({
            "stt": str(it.get("stt") or idx),
            "loai_gia_tri": "NM" if isinstance(gia_tri, (int, float)) else "ST",
            "ma_loinc": ma_raw,
            "ten_goc": ten_goc,
            "ma_chuan": ma_chuan,
            "gia_tri": gia_tri,
            "don_vi": don_vi,
            "khoang_tham_chieu": ref,
            "co_bat_thuong": flag,
            "trang_thai": str(it.get("trang_thai") or "F"),
        })

    return chi_so, ban_ghi_obx


def _phan_tich_csv_lis(noi_dung: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    chi_so: Dict[str, Any] = {}
    ban_ghi_obx: List[Dict[str, Any]] = []
    van_ban = noi_dung.lstrip("\ufeff").strip()
    lines = [ln for ln in van_ban.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    if not lines:
        return chi_so, ban_ghi_obx

    delim = "\t" if "\t" in lines[0] else (";" if ";" in lines[0] and "," not in lines[0] else ",")
    reader = csv.reader(io.StringIO("\n".join(lines)), delimiter=delim)

    header_tokens = {"chi_so", "ma_chi_so", "ten_chi_so", "loinc", "code", "name", "test"}
    idx_code, idx_val, idx_unit, idx_ref, idx_flag = 0, 1, 2, 3, 4

    for idx_row, cols in enumerate(reader):
        c_clean = [str(c or "").strip() for c in cols]
        if not any(c_clean):
            continue
        if idx_row == 0 and any(_bo_dau_va_chuan_hoa(c).replace(" ", "_") in header_tokens for c in c_clean[:2]):
            for j, h in enumerate(c_clean):
                hn = _bo_dau_va_chuan_hoa(h).replace(" ", "_")
                if hn in header_tokens:
                    idx_code = j
                elif hn in {"gia_tri", "value", "ket_qua", "result"}:
                    idx_val = j
                elif hn in {"don_vi", "unit"}:
                    idx_unit = j
                elif hn in {"khoang_tham_chieu", "tham_chieu", "reference_range", "ref_range"}:
                    idx_ref = j
                elif hn in {"co_bat_thuong", "flag", "bat_thuong"}:
                    idx_flag = j
            continue

        ma_raw = c_clean[idx_code] if idx_code < len(c_clean) else ""
        val_raw = c_clean[idx_val] if idx_val < len(c_clean) else ""
        don_vi = c_clean[idx_unit] if idx_unit < len(c_clean) else ""
        ref = c_clean[idx_ref] if idx_ref < len(c_clean) else ""
        flag = c_clean[idx_flag] if idx_flag < len(c_clean) else ""

        ma_chuan = chuan_hoa_ma_chi_so(ma_raw)
        gia_tri = _ep_gia_tri(val_raw)
        if not ma_chuan or gia_tri is None:
            continue

        _ghi_chi_so_vao_dict(chi_so, ma_chuan, gia_tri, don_vi)
        ban_ghi_obx.append({
            "stt": str(len(ban_ghi_obx) + 1),
            "loai_gia_tri": "NM" if isinstance(gia_tri, (int, float)) else "ST",
            "ma_loinc": ma_raw,
            "ten_goc": ma_raw,
            "ma_chuan": ma_chuan,
            "gia_tri": gia_tri,
            "don_vi": don_vi,
            "khoang_tham_chieu": ref,
            "co_bat_thuong": flag,
            "trang_thai": "F",
        })

    return chi_so, ban_ghi_obx


def phan_tich_lis_dau_vao(noi_dung: str) -> Dict[str, Any]:
    """Phân tích thông điệp LIS đầu vào (HL7 v2 ORU^R01, JSON hoặc CSV) và đối soát cận lâm sàng."""
    text = str(noi_dung or "").strip()
    if not text:
        kq_cls = ParaclinicalCorrelator.phan_tich_xet_nghiem({}, "")
        return {
            "dinh_dang": "CSV",
            "chi_so": {},
            "ban_ghi_obx": [],
            "doi_soat_can_lam_sang": asdict(kq_cls),
        }

    # 1. Nhận diện HL7 v2 ORU^R01
    if re.search(r"(?:^|[\r\n])(?:MSH|PID|OBR|OBX)\|", text):
        dinh_dang = "HL7_ORU_R01"
        chi_so, ban_ghi_obx = _phan_tich_hl7_oru(text)
    elif text[0] in ("{", "["):
        try:
            obj = json.loads(text)
            dinh_dang = "JSON"
            chi_so, ban_ghi_obx = _phan_tich_json_lis(obj)
        except json.JSONDecodeError:
            dinh_dang = "CSV"
            chi_so, ban_ghi_obx = _phan_tich_csv_lis(text)
    else:
        dinh_dang = "CSV"
        chi_so, ban_ghi_obx = _phan_tich_csv_lis(text)

    chi_so_chuan = chuan_hoa_du_lieu_xet_nghiem(chi_so)
    doi_soat = ParaclinicalCorrelator.phan_tich_xet_nghiem(chi_so_chuan, "")

    return {
        "dinh_dang": dinh_dang,
        "chi_so": chi_so_chuan,
        "ban_ghi_obx": ban_ghi_obx,
        "doi_soat_can_lam_sang": asdict(doi_soat),
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="MediTrace LIS HL7 ORU^R01 / JSON / CSV Parser")
    parser.add_argument("--parse", action="store_true", help="Đọc stdin JSON {'text': ...} và xuất kết quả JSON")
    args = parser.parse_args(argv)
    if args.parse:
        raw_stdin = sys.stdin.read()
        try:
            payload = json.loads(raw_stdin) if raw_stdin.strip() else {}
            text = payload.get("text") or payload.get("noi_dung") or "" if isinstance(payload, dict) else str(raw_stdin)
        except json.JSONDecodeError:
            text = raw_stdin
        res = phan_tich_lis_dau_vao(str(text))
        print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
