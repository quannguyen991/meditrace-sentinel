# -*- coding: utf-8 -*-
"""Bóc tách chỉ số xét nghiệm & đơn thuốc cũ (Clinical Vision/OCR Parser) chạy 100% cục bộ.

Kết nối trực tiếp với động cơ `src.hieu_chinh_lieu` để tự động tính eGFR / CrCl
và cảnh báo hiệu chỉnh liều thuốc ngay khi bác sĩ nhập hoặc quét phiếu xét nghiệm cũ.
"""
from __future__ import annotations

from dataclasses import asdict
import json
import re
import sys
from typing import Any, Dict, List, Optional

from src.can_lam_sang import ParaclinicalCorrelator
from src.chuan_hoa_don_vi_xet_nghiem import (
    chuan_hoa_creatinine,
    chuan_hoa_glucose,
    chuan_hoa_urea,
)
from src.hieu_chinh_lieu import (
    chuyen_umol_sang_mg_dl,
    kiem_tra_hieu_chinh_lieu,
    tinh_egfr_ckd_epi_2021,
)

# Từ điển hoạt chất & biệt dược phổ biến dễ gặp trên đơn thuốc cũ ngoại trú
TU_DIEN_THUOC_CU: Dict[str, str] = {
    "metformin": "Metformin",
    "glucophage": "Metformin",
    "glumeform": "Metformin",
    "allopurinol": "Allopurinol",
    "zyloric": "Allopurinol",
    "ciprofloxacin": "Ciprofloxacin",
    "levofloxacin": "Levofloxacin",
    "tavanic": "Levofloxacin",
    "amoxicillin": "Amoxicillin",
    "augmentin": "Amoxicillin/Clavulanat",
    "enoxaparin": "Enoxaparin",
    "lovenox": "Enoxaparin",
    "spironolacton": "Spironolacton",
    "losartan": "Losartan",
    "cozaar": "Losartan",
    "amlodipin": "Amlodipin",
    "atorvastatin": "Atorvastatin",
    "lipitor": "Atorvastatin",
    "rosuvastatin": "Rosuvastatin",
    "crestor": "Rosuvastatin",
    "paracetamol": "Paracetamol",
    "panadol": "Paracetamol",
    "hapacol": "Paracetamol",
    "ibuprofen": "Ibuprofen",
    "diclofenac": "Diclofenac",
    "meloxicam": "Meloxicam",
    "omeprazol": "Omeprazol",
    "esomeprazol": "Esomeprazol",
    "nexium": "Esomeprazol",
    "warfarin": "Warfarin",
    "rivaroxaban": "Rivaroxaban",
    "xarelto": "Rivaroxaban",
}


def _lay_so_float(pattern: str, text: str) -> Optional[float]:
    m = re.search(pattern, text, flags=re.IGNORECASE)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", "."))
    except (ValueError, TypeError):
        return None


def boc_tach_phieu_cu(
    van_ban: str,
    tuoi: Optional[int] = None,
    la_nu: bool = False,
    can_nang_kg: Optional[float] = None,
) -> Dict[str, Any]:
    """Bóc tách chỉ số sinh hóa & danh sách thuốc từ văn bản phiếu XN/đơn thuốc cũ, nối `hieu_chinh_lieu`."""
    chu = (van_ban or "").strip()
    chi_so: Dict[str, Any] = {}

    # 1. Creatinine: hỗ trợ cả µmol/L (tự quy đổi sang mg/dL) và mg/dL
    m_creat = re.search(
        r"(?:creatinin[e]?|scr)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(µmol/l|umol/l|mg/dl)?",
        chu,
        flags=re.IGNORECASE,
    )
    if m_creat:
        val = float(m_creat.group(1).replace(",", "."))
        don_vi = (m_creat.group(2) or "").lower()
        c_norm = chuan_hoa_creatinine(val, don_vi or None)
        if c_norm:
            chi_so["creatinine_umol_l"] = c_norm["umol_l"]
            chi_so["creatinine"] = c_norm["mg_dl"]
            chi_so["creatinine_mg_dl"] = c_norm["mg_dl"]

    egfr_in = _lay_so_float(r"(?:egfr|mlct)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)", chu)
    # Thieu tuoi (hoac tuoi khong doc duoc) -> KHONG mac dinh 50, khong uoc tinh eGFR;
    # hieu_chinh_lieu se danh dau phuong_phap_uoc_tinh="thieu_tuoi"
    try:
        tuoi_chuan: Optional[int] = int(float(str(tuoi).strip().replace(",", "."))) if tuoi is not None else None
    except (ValueError, TypeError):
        tuoi_chuan = None
    if tuoi_chuan is not None and tuoi_chuan <= 0:
        tuoi_chuan = None
    if egfr_in is not None:
        chi_so["egfr"] = egfr_in
    elif "creatinine" in chi_so and tuoi_chuan is not None and tuoi_chuan >= 18:
        chi_so["egfr"] = tinh_egfr_ckd_epi_2021(chi_so["creatinine"], tuoi_chuan, la_nu)

    hba1c = _lay_so_float(r"hba1c\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)", chu)
    if hba1c is not None:
        chi_so["hba1c"] = hba1c

    m_glu = re.search(
        r"(?:glucose|đường\s*huyết)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(mmol/l|mg/dl)?",
        chu,
        flags=re.IGNORECASE,
    )
    if m_glu:
        g_val = float(m_glu.group(1).replace(",", "."))
        g_dv = (m_glu.group(2) or "").lower() or None
        g_norm = chuan_hoa_glucose(g_val, g_dv)
        if g_norm:
            chi_so["glucose"] = g_norm["mmol_l"]
            chi_so["glucose_mmol_l"] = g_norm["mmol_l"]
            chi_so["glucose_mg_dl"] = g_norm["mg_dl"]

    m_urea = re.search(
        r"\b(urea|ure|bun)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(mmol/l|mg/dl)?",
        chu,
        flags=re.IGNORECASE,
    )
    if m_urea:
        u_name = m_urea.group(1).lower()
        u_val = float(m_urea.group(2).replace(",", "."))
        u_dv = (m_urea.group(3) or "").lower() or None
        u_norm = chuan_hoa_urea(u_val, u_dv, la_bun=(u_name == "bun"))
        if u_norm:
            chi_so["urea"] = u_norm["mmol_l"]
            chi_so["urea_mmol_l"] = u_norm["mmol_l"]
            chi_so["urea_mg_dl"] = u_norm["mg_dl"]

    ast = _lay_so_float(r"\b(?:ast|got)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)", chu)
    if ast is not None:
        chi_so["ast"] = ast

    alt = _lay_so_float(r"\b(?:alt|gpt)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)", chu)
    if alt is not None:
        chi_so["alt"] = alt

    kali = _lay_so_float(r"\b(?:kali|k\+)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)", chu)
    if kali is not None:
        chi_so["kali"] = kali

    # Boost 9: Mở rộng trích xuất cận lâm sàng huyết học - đông máu - tim mạch - viêm - gan mật
    wbc = _lay_so_float(r"\b(?:wbc|bạch\s*cầu)\b\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)", chu)
    if wbc is not None:
        chi_so["wbc"] = wbc

    m_hb = re.search(
        r"\b(?:hb|hgb|hemoglobin|huyết\s*sắc\s*tố)\b\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)\s*(g/dl|g/l)?",
        chu,
        flags=re.IGNORECASE,
    )
    if m_hb:
        hb_raw = float(m_hb.group(1).replace(",", "."))
        hb_dv = (m_hb.group(2) or "").strip().lower()
        if hb_dv == "g/l" or (not hb_dv and hb_raw > 35.0):
            chi_so["hb_g_l"] = hb_raw
            chi_so["hb"] = round(hb_raw / 10.0, 2)
        else:
            chi_so["hb"] = hb_raw

    plt = _lay_so_float(r"\b(?:plt|tiểu\s*cầu)\b\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)", chu)
    if plt is not None:
        chi_so["plt"] = plt

    troponin = _lay_so_float(
        r"\b(?:hs[\-\s]*)?troponin(?:\s*[ti])?\b\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)",
        chu,
    )
    if troponin is not None:
        chi_so["troponin"] = troponin

    crp = _lay_so_float(r"\b(?:hs[\-\s]*)?crp\b\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)", chu)
    if crp is not None:
        chi_so["crp"] = crp

    na = _lay_so_float(r"(?<!\w)(?:na\s*\+|na|natri)(?!\w)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)", chu)
    if na is not None:
        chi_so["na"] = na

    inr = _lay_so_float(r"\binr\b\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)", chu)
    if inr is not None:
        chi_so["inr"] = inr

    bilirubin = _lay_so_float(
        r"\bbilirubin(?:\s*(?:tp|toàn\s*phần|tt|trực\s*tiếp))?\b\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)",
        chu,
    )
    if bilirubin is not None:
        chi_so["bilirubin"] = bilirubin

    albumin = _lay_so_float(r"\balbumin\b(?!\s*niệu)\s*[:=\-]?\s*(\d+(?:[.,]\d+)?)", chu)
    if albumin is not None:
        chi_so["albumin"] = albumin

    # 2. Thuốc trong đơn cũ (chuẩn hóa biệt dược -> hoạt chất)
    chu_thuong = chu.lower()
    thuoc_tim_duoc: List[str] = []
    seen = set()
    for tu_khoa, hoat_chat in TU_DIEN_THUOC_CU.items():
        if re.search(rf"\b{re.escape(tu_khoa)}\b", chu_thuong) and hoat_chat not in seen:
            seen.add(hoat_chat)
            thuoc_tim_duoc.append(hoat_chat)

    # 3. Nối trực tiếp động cơ hiệu chỉnh liều (src/hieu_chinh_lieu.py)
    thong_tin_bn: Dict[str, Any] = {"tuoi": tuoi_chuan, "la_nu": bool(la_nu)}
    if can_nang_kg is not None:
        thong_tin_bn["can_nang_kg"] = can_nang_kg

    hieu_chinh = kiem_tra_hieu_chinh_lieu(
        danh_sach_thuoc=thuoc_tim_duoc,
        ket_qua_xet_nghiem=chi_so,
        thong_tin_benh_nhan=thong_tin_bn,
    )

    # Cảnh báo Kali máu cao (>= 5.0 mmol/L) kết hợp Spironolacton (nguy cơ tăng kali máu đe dọa tính mạng)
    if "kali" in chi_so and chi_so["kali"] >= 5.0 and any("spironolacton" in t.lower() for t in thuoc_tim_duoc):
        hieu_chinh.setdefault("canh_bao_hieu_chinh_than", []).append({
            "thuoc": "Spironolacton",
            "muc_do": "CRITICAL",
            "chi_so_danh_gia": f"Kali máu = {chi_so['kali']} mmol/L (>= 5.0)",
            "khuyen_cao": "NGỪNG NGAY Spironolacton và kiểm tra điện tâm đồ (ECG)",
            "lieu_de_xuat": "Chống chỉ định tuyệt đối khi Kali >= 5.0 mmol/L.",
            "ly_do_lam_sang": "Lợi tiểu giữ kali gây tăng kali máu nặng, nguy cơ loạn nhịp thất / ngừng tim.",
        })
        hieu_chinh["tong_so_canh_bao"] = len(hieu_chinh.get("canh_bao_hieu_chinh_than", [])) + len(
            hieu_chinh.get("canh_bao_hieu_chinh_gan", [])
        ) + len(hieu_chinh.get("huong_dan_tuong_tac_thuc_pham", []))
        hieu_chinh["co_canh_bao_critical"] = True

    kq_cls = ParaclinicalCorrelator.phan_tich_xet_nghiem(chi_so, chu)

    return {
        "chi_so": chi_so,
        "thuoc_nhan_dien": thuoc_tim_duoc,
        "hieu_chinh_lieu": hieu_chinh,
        "doi_soat_can_lam_sang": asdict(kq_cls),
    }


if __name__ == "__main__":
    if "--parse" in sys.argv:
        raw = sys.stdin.read().lstrip("\ufeff")
        data = json.loads(raw) if raw.strip() else {}
        kq = boc_tach_phieu_cu(
            van_ban=str(data.get("text") or ""),
            tuoi=data.get("tuoi"),
            la_nu=bool(data.get("laNu", False)),
            can_nang_kg=data.get("canNangKg"),
        )
        print(json.dumps(kq, ensure_ascii=False))
