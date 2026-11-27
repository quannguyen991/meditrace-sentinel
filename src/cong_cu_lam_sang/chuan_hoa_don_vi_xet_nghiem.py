# -*- coding: utf-8 -*-
"""[Công cụ lâm sàng hỗ trợ bác sĩ › Xét nghiệm]
Làm gì   : Đổi creatinin, glucose, urea giữa các đơn vị khác nhau về một đơn vị chung để các
           công cụ khác so được.
Vào → Ra : giá trị xét nghiệm + đơn vị (hoặc cả dict xét nghiệm) → giá trị quy đổi ở các đơn
           vị chuẩn
Đọc từ   : chuan_hoa_du_lieu_xet_nghiem() quy đổi cả dict; chuan_hoa_creatinine() ví dụ cho
           một chỉ số
Mục lục (các hàm/lớp chính):
  chuan_hoa_du_lieu_xet_nghiem()  Chuẩn hoá toàn bộ từ điển xét nghiệm
  chuan_hoa_creatinine()          Quy đổi creatinin sang mg/dL và µmol/L
  chuan_hoa_glucose()             Quy đổi glucose máu sang mmol/L và mg/dL
  chuan_hoa_urea()                Quy đổi urea hoặc BUN sang mmol/L và mg/dL
Dùng bởi : cong_cu_lam_sang/doc_phieu_xet_nghiem, cong_cu_lam_sang/doi_soat_can_lam_sang,
           cong_cu_lam_sang/hieu_chinh_lieu, cong_cu_lam_sang/nap_ket_qua_lis_hl7,
           cong_cu_lam_sang/quy_dao_nhieu_lan_kham, cong_cu_lam_sang/xuat_fhir_r4,
           he_thong/dieu_phoi_cac_chot_an_toan
Tên cũ   : chuan_hoa_don_vi_xet_nghiem.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Canonical Lab Unit Normalizer — Chuẩn hóa đơn vị xét nghiệm nội bộ.

Thống nhất đơn vị xét nghiệm giữa:
  - `src/cong_cu_lam_sang/doi_soat_can_lam_sang.py` (ParaclinicalCorrelator)
  - `src/cong_cu_lam_sang/hieu_chinh_lieu.py` (CKD-EPI 2021 / Cockcroft-Gault / Schwartz)
  - `src/cong_cu_lam_sang/doc_phieu_xet_nghiem.py` (boc_tach_phieu_cu)
  - `src/cong_cu_lam_sang/xuat_fhir_r4.py` (HL7 FHIR R4 Observation LOINC)
  - `src/cong_cu_lam_sang/thang_diem_nguy_co.py` (CURB-65, Glasgow-Blatchford)
"""
from __future__ import annotations

from typing import Any, Dict, Optional


# ─── _to_float() — Đổi giá trị bất kỳ sang số thực không âm ───────────────────────────
# Trả về None nếu rỗng, sai định dạng hoặc âm; chấp nhận dấu phẩy thập phân.
def _to_float(val: Any) -> Optional[float]:
    if val is None or isinstance(val, bool):
        return None
    try:
        if isinstance(val, str):
            val = val.strip().replace(",", ".")
            if not val:
                return None
        f = float(val)
        return f if f >= 0 else None
    except (ValueError, TypeError):
        return None


# ═══ chuan_hoa_creatinine() — Quy đổi creatinin sang mg/dL và µmol/L ══════════════════
# Hệ số 88.4. Không có đơn vị thì từ 15 trở lên coi là µmol/L, nhỏ hơn coi là mg/dL.
def chuan_hoa_creatinine(val: Any, don_vi: Optional[str] = None) -> Optional[Dict[str, float]]:
    """Chuẩn hóa Creatinine về cả `mg_dl` và `umol_l`.

    Quy ước: 1 mg/dL = 88.4 µmol/L.
    Nếu không truyền `don_vi`: giá trị >= 15.0 được hiểu là µmol/L, < 15.0 là mg/dL.
    """
    f = _to_float(val)
    if f is None or f <= 0:
        return None
    dv = (don_vi or "").strip().lower().replace("μ", "µ")
    if "mol" in dv:
        umol = f
        mg = round(f / 88.4, 2)
    elif "mg" in dv:
        mg = round(f, 2)
        umol = round(f * 88.4, 1)
    else:
        if f >= 15.0:
            umol = round(f, 1)
            mg = round(f / 88.4, 2)
        else:
            mg = round(f, 2)
            umol = round(f * 88.4, 1)
    return {"mg_dl": mg, "umol_l": umol}


# ═══ chuan_hoa_glucose() — Quy đổi glucose máu sang mmol/L và mg/dL ═══════════════════
# Hệ số 18.018. Không có đơn vị thì từ 30 trở lên coi là mg/dL, nhỏ hơn coi là mmol/L.
def chuan_hoa_glucose(val: Any, don_vi: Optional[str] = None) -> Optional[Dict[str, float]]:
    """Chuẩn hóa Glucose máu về cả `mmol_l` và `mg_dl`.

    Quy ước: 1 mmol/L = 18.018 mg/dL.
    Nếu không truyền `don_vi`: giá trị >= 30.0 được hiểu là mg/dL, < 30.0 là mmol/L.
    """
    f = _to_float(val)
    if f is None or f <= 0:
        return None
    dv = (don_vi or "").strip().lower()
    if "mg" in dv:
        mg = round(f, 1)
        mmol = round(f / 18.018, 2)
    elif "mmol" in dv:
        mmol = round(f, 2)
        mg = round(f * 18.018, 1)
    else:
        if f >= 30.0:
            mg = round(f, 1)
            mmol = round(f / 18.018, 2)
        else:
            mmol = round(f, 2)
            mg = round(f * 18.018, 1)
    return {"mmol_l": mmol, "mg_dl": mg}


# ═══ chuan_hoa_urea() — Quy đổi urea hoặc BUN sang mmol/L và mg/dL ════════════════════
# Hệ số 6.006 cho urea, 2.801 cho BUN; đoán đơn vị theo ngưỡng khi thiếu đơn vị.
def chuan_hoa_urea(
    val: Any,
    don_vi: Optional[str] = None,
    la_bun: bool = False,
) -> Optional[Dict[str, float]]:
    """Chuẩn hóa Urea / BUN về `mmol_l` (chuẩn CURB-65 & Glasgow-Blatchford) và `mg_dl`.

    Quy ước:
      - Urea: 1 mmol/L = 6.006 mg/dL
      - BUN:  1 mmol/L urea = 2.801 mg/dL BUN
    Nếu không truyền `don_vi`:
      - Nếu `la_bun=True` và val >= 15.0 -> mg/dL BUN
      - Nếu `la_bun=False` và val > 35.0 -> mg/dL Urea
    """
    f = _to_float(val)
    if f is None or f <= 0:
        return None
    dv = (don_vi or "").strip().lower()
    he_so = 2.801 if la_bun else 6.006

    if "mmol" in dv:
        mmol = round(f, 2)
        mg = round(f * he_so, 1)
    elif "mg" in dv:
        mg = round(f, 1)
        mmol = round(f / he_so, 2)
    else:
        nguong = 15.0 if la_bun else 35.0
        if f > nguong:
            mg = round(f, 1)
            mmol = round(f / he_so, 2)
        else:
            mmol = round(f, 2)
            mg = round(f * he_so, 1)
    return {"mmol_l": mmol, "mg_dl": mg}


# ═══ chuan_hoa_du_lieu_xet_nghiem() — Chuẩn hoá toàn bộ từ điển xét nghiệm ════════════
# Bổ sung các trường đã quy đổi đơn vị (creatinin, glucose, urea...) vào bản sao dữ
# liệu.
def chuan_hoa_du_lieu_xet_nghiem(du_lieu: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Chuẩn hóa toàn bộ dictionary xét nghiệm, bổ sung các trường chuẩn hóa nội bộ."""
    if not isinstance(du_lieu, dict):
        return {}
    kq = dict(du_lieu)

    # Creatinine: ưu tiên creatinine_umol_l hoặc creatinine + don_vi
    creat_dv = du_lieu.get("creatinine_unit") or du_lieu.get("creatinine_don_vi")
    if du_lieu.get("creatinine_mg_dl") is not None:
        c = chuan_hoa_creatinine(du_lieu.get("creatinine_mg_dl"), "mg/dL")
    elif du_lieu.get("creatinine") is not None:
        c = chuan_hoa_creatinine(du_lieu.get("creatinine"), creat_dv)
    elif du_lieu.get("creatinine_umol_l") is not None:
        c = chuan_hoa_creatinine(du_lieu.get("creatinine_umol_l"), "umol/L")
    else:
        c = None
    if c:
        kq["creatinine_mg_dl"] = c["mg_dl"]
        kq["creatinine_umol_l"] = c["umol_l"]

    # Glucose
    glu_dv = du_lieu.get("glucose_unit") or du_lieu.get("glucose_don_vi")
    if du_lieu.get("glucose_mmol_l") is not None:
        g = chuan_hoa_glucose(du_lieu.get("glucose_mmol_l"), "mmol/L")
    elif du_lieu.get("glucose_mg_dl") is not None:
        g = chuan_hoa_glucose(du_lieu.get("glucose_mg_dl"), "mg/dL")
    elif du_lieu.get("glucose") is not None:
        g = chuan_hoa_glucose(du_lieu.get("glucose"), glu_dv)
    else:
        g = None
    if g:
        kq["glucose_mmol_l"] = g["mmol_l"]
        kq["glucose_mg_dl"] = g["mg_dl"]

    # Urea / BUN
    urea_dv = du_lieu.get("urea_unit") or du_lieu.get("ure_unit") or du_lieu.get("bun_unit")
    if du_lieu.get("urea_mmol_l") is not None:
        u = chuan_hoa_urea(du_lieu.get("urea_mmol_l"), "mmol/L")
    elif du_lieu.get("urea") is not None or du_lieu.get("ure") is not None:
        raw_u = du_lieu.get("urea") if du_lieu.get("urea") is not None else du_lieu.get("ure")
        u = chuan_hoa_urea(raw_u, urea_dv, la_bun=False)
    elif du_lieu.get("bun") is not None:
        u = chuan_hoa_urea(du_lieu.get("bun"), urea_dv, la_bun=True)
    else:
        u = None
    if u:
        kq["urea_mmol_l"] = u["mmol_l"]
        kq["urea_mg_dl"] = u["mg_dl"]

    return kq
