# -*- coding: utf-8 -*-
"""Động cơ Phân tích Quỹ đạo Lâm sàng Dọc theo Nhiều Lần Khám (Longitudinal Lab & Medication Trajectory Engine).

Bao gồm:
1. Phân tầng Tổn thương Thận cấp (KDIGO AKI Staging: 48h & 7 ngày, chuẩn hóa mg/dL và µmol/L).
2. Phân tích xu hướng xét nghiệm dọc: eGFR (CKD-EPI 2021), HbA1c, INR, Hemoglobin, Kali (K+), AST/ALT.
3. Phát hiện chuỗi nguy cơ thuốc liên hoàn qua nhiều lần khám (Triple Whammy, thuốc độc thận khi AKI/giảm eGFR,
   thuốc độc gan khi men gan tăng vọt, thuốc chống đông khi tăng INR/tụt Hb).
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from src.chuan_hoa_don_vi_xet_nghiem import chuan_hoa_du_lieu_xet_nghiem
from src.di_ung_cheo import _phan_giai_thanh_phan
from src.ep_kieu_dau_vao import so_an_toan
from src.hieu_chinh_lieu import tinh_egfr_ckd_epi_2021

_ACEI_ARB: Set[str] = {
    "enalapril", "captopril", "lisinopril", "perindopril", "ramipril",
    "imidapril", "benazepril", "quinapril", "fosinopril",
    "losartan", "valsartan", "telmisartan", "irbesartan", "candesartan", "olmesartan",
}
_DIURETICS: Set[str] = {
    "furosemide", "torsemide", "bumetanide",
    "hydrochlorothiazide", "indapamide", "chlorthalidone", "metolazone",
    "spironolactone", "amiloride", "triamterene", "acetazolamide",
}
_NSAIDS: Set[str] = {
    "ibuprofen", "diclofenac", "meloxicam", "naproxen", "piroxicam",
    "ketoprofen", "indomethacin", "ketorolac", "celecoxib", "etoricoxib",
    "mefenamic acid", "tenoxicam", "aceclofenac", "dexketoprofen", "nsaid",
}
_NEPHROTOXIC_OR_AKI_UNSAFE: Set[str] = _NSAIDS | {
    "metformin", "gentamicin", "amikacin", "tobramycin", "streptomycin",
    "vancomycin", "spironolactone", "thuoc_can_quang",
}
_HEPATOTOXIC: Set[str] = {
    "paracetamol", "atorvastatin", "rosuvastatin", "simvastatin", "pravastatin",
    "lovastatin", "fluvastatin", "methotrexate", "valproat", "valproate",
    "isoniazid", "rifampicin", "pyrazinamide", "amiodarone", "ketoconazole",
}
_ANTICOAG_ANTIPLATELET: Set[str] = {
    "warfarin", "acenocoumarol", "dabigatran", "rivaroxaban", "apixaban",
    "edoxaban", "enoxaparin", "heparin", "clopidogrel", "ticagrelor", "prasugrel", "aspirin",
}


def _la_nu_tu_bn(tt: Dict[str, Any]) -> bool:
    if isinstance(tt.get("la_nu"), bool):
        return tt["la_nu"]
    gt = str(tt.get("gioi_tinh") or "").strip().lower()
    return gt in ("nữ", "nu", "female", "f")


def _phan_tich_thoi_gian(
    visit: Dict[str, Any],
    moc_hien_tai: datetime,
) -> Optional[datetime]:
    """Chuẩn hóa mốc thời gian của một lần khám về datetime UTC naive; trả None nếu không đọc được."""
    gio_truoc = so_an_toan(visit.get("gio_truoc"))
    if gio_truoc is not None and gio_truoc >= 0:
        return moc_hien_tai - timedelta(hours=gio_truoc)
    ngay_truoc = so_an_toan(visit.get("ngay_truoc"))
    if ngay_truoc is not None and ngay_truoc >= 0:
        return moc_hien_tai - timedelta(days=ngay_truoc)

    raw = None
    for k in ("ngay_kham", "thoi_gian", "timestamp", "date", "created_at", "ngay"):
        if visit.get(k) is not None:
            raw = visit.get(k)
            break
    if raw is None:
        return None
    if isinstance(raw, datetime):
        if raw.tzinfo is not None:
            return raw.astimezone(timezone.utc).replace(tzinfo=None)
        return raw
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        ts = float(raw)
        if ts > 1e12:
            ts /= 1000.0
        try:
            return datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None)
        except (OSError, OverflowError, ValueError):
            return None

    s = str(raw).strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is not None:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)
        return dt
    except ValueError:
        pass

    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y", "%d-%m-%Y %H:%M", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _trich_xet_nghiem_lan_kham(
    visit: Dict[str, Any],
    tuoi_mac_dinh: Optional[int],
    la_nu_mac_dinh: bool,
) -> Dict[str, Any]:
    """Gộp và chuẩn hóa toàn bộ chỉ số xét nghiệm từ một lần khám."""
    gop: Dict[str, Any] = {}
    for k in ("xet_nghiem", "du_lieu_xet_nghiem", "labs"):
        sub = visit.get(k)
        if isinstance(sub, dict):
            for sk, sv in sub.items():
                if sv is not None:
                    gop[sk] = sv

    cac_khoa_xn = {
        "creatinine", "creatinine_mg_dl", "creatinine_umol_l", "creatinine_unit", "creatinine_don_vi",
        "egfr", "hba1c", "inr", "hb", "hemoglobin", "k", "kali", "ast", "got", "alt", "gpt",
        "urea", "ure", "urea_mmol_l", "urea_unit", "bun", "bun_unit", "glucose", "glucose_mmol_l",
        "glucose_mg_dl", "glucose_unit", "bilirubin", "albumin",
    }
    for k in cac_khoa_xn:
        if visit.get(k) is not None and k not in gop:
            gop[k] = visit[k]

    # Lưu đánh dấu đơn vị gốc của creatinine để tính tỷ lệ AKI chính xác
    don_vi_creat = str(gop.get("creatinine_unit") or gop.get("creatinine_don_vi") or "").lower()
    raw_creat_mg = so_an_toan(gop.get("creatinine_mg_dl"))
    raw_creat_umol = so_an_toan(gop.get("creatinine_umol_l"))
    raw_creat = so_an_toan(gop.get("creatinine"))
    la_umol_goc = (
        "mol" in don_vi_creat
        or (raw_creat_umol is not None and raw_creat_mg is None)
        or (raw_creat is not None and "mg" not in don_vi_creat and raw_creat >= 15.0)
    )

    norm = chuan_hoa_du_lieu_xet_nghiem(gop)
    ra: Dict[str, Any] = dict(norm)
    ra["_creat_la_umol_goc"] = la_umol_goc

    def _so(*keys: str) -> Optional[float]:
        for key in keys:
            v = so_an_toan(norm.get(key))
            if v is not None:
                return v
        return None

    ra["creatinine_mg_dl"] = _so("creatinine_mg_dl")
    ra["creatinine_umol_l"] = _so("creatinine_umol_l")
    ra["hba1c"] = _so("hba1c")
    ra["inr"] = _so("inr")
    ra["hb"] = _so("hb", "hemoglobin")
    ra["k"] = _so("k", "kali")
    ra["ast"] = _so("ast", "got")
    ra["alt"] = _so("alt", "gpt")

    egfr = _so("egfr")
    if egfr is None and ra["creatinine_mg_dl"] is not None:
        tuoi_v = so_an_toan(visit.get("tuoi"))
        tuoi_use = int(tuoi_v) if tuoi_v is not None and tuoi_v >= 18 else (
            tuoi_mac_dinh if tuoi_mac_dinh is not None and tuoi_mac_dinh >= 18 else None
        )
        la_nu_use = _la_nu_tu_bn(visit) if ("gioi_tinh" in visit or "la_nu" in visit) else la_nu_mac_dinh
        if tuoi_use is not None:
            egfr_calc = tinh_egfr_ckd_epi_2021(ra["creatinine_mg_dl"], tuoi_use, la_nu_use)
            if egfr_calc > 0:
                egfr = egfr_calc
    ra["egfr"] = egfr
    return ra


def _trich_thuoc_lan_kham(visit: Dict[str, Any]) -> List[Tuple[str, str]]:
    """Trả về danh sách (hoat_chat_chuan, ten_hien_thi) từ một lần khám."""
    ten_tho: List[str] = []
    for k in ("danh_sach_thuoc", "thuoc", "medications"):
        val = visit.get(k)
        if not val:
            continue
        if isinstance(val, str):
            ten_tho.extend([x.strip() for x in re.split(r"[,;\n]+", val) if x.strip()])
        elif isinstance(val, (list, tuple, set)):
            for item in val:
                if isinstance(item, dict):
                    if item.get("trang_thai_dung") == "đã ngừng":
                        continue
                    t = item.get("ten") or item.get("hoat_chat") or item.get("ten_thuoc") or item.get("name") or ""
                    if str(t).strip():
                        ten_tho.append(str(t).strip())
                elif item is not None and str(item).strip():
                    ten_tho.append(str(item).strip())

    for k in ("phat_bieu", "propositions"):
        pbs = visit.get(k)
        if not isinstance(pbs, list):
            continue
        for pb in pbs:
            if isinstance(pb, dict):
                if pb.get("phu_dinh") or pb.get("chu_the_id", 0) != 0:
                    continue
                if pb.get("trang_thai", "còn hiệu lực") != "còn hiệu lực":
                    continue
                th = pb.get("thuoc")
                if isinstance(th, dict) and th.get("ten") and th.get("trang_thai_dung") != "đã ngừng":
                    ten_tho.append(str(th["ten"]).strip())

    ra: List[Tuple[str, str]] = []
    da_co: Set[str] = set()
    for t in ten_tho:
        for hc in _phan_giai_thanh_phan(t):
            if hc and hc not in da_co:
                da_co.add(hc)
                ra.append((hc, t))
    return ra


def _danh_gia_kdigo_aki(
    lich_su_chuan: List[Dict[str, Any]],
    hien_tai_chuan: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Áp dụng tiêu chuẩn KDIGO AKI (48h và 7 ngày)."""
    xn_now = hien_tai_chuan["xn"]
    scr_now_mg = xn_now.get("creatinine_mg_dl")
    scr_now_umol = xn_now.get("creatinine_umol_l")
    t_now = hien_tai_chuan["dt"]
    if scr_now_mg is None or scr_now_umol is None or t_now is None:
        return None

    diem_48h: List[Dict[str, Any]] = []
    diem_7d: List[Dict[str, Any]] = []
    for h in lich_su_chuan:
        t_h = h["dt"]
        xn_h = h["xn"]
        if t_h is None or xn_h.get("creatinine_mg_dl") is None or xn_h.get("creatinine_umol_l") is None:
            continue
        delta_sec = (t_now - t_h).total_seconds()
        if delta_sec < 0:
            continue
        if delta_sec <= 48 * 3600:
            diem_48h.append(h)
        if delta_sec <= 7 * 86400:
            diem_7d.append(h)

    if not diem_48h and not diem_7d:
        return None

    tieu_chi: List[str] = []
    stage = 0

    delta_48h_mg = 0.0
    delta_48h_umol = 0.0
    tang_48h_dat = False
    base_48h = None
    if diem_48h:
        base_48h = min(diem_48h, key=lambda x: x["xn"]["creatinine_mg_dl"])
        delta_48h_mg = round(scr_now_mg - base_48h["xn"]["creatinine_mg_dl"], 3)
        delta_48h_umol = round(scr_now_umol - base_48h["xn"]["creatinine_umol_l"], 2)
        if delta_48h_mg >= 0.3 or delta_48h_umol >= 26.5:
            tang_48h_dat = True
            stage = max(stage, 1)
            tieu_chi.append(
                f"Creatinine tăng cấp trong <= 48 giờ: +{delta_48h_mg:.2f} mg/dL (+{delta_48h_umol:.1f} µmol/L) so với đáy {base_48h['xn']['creatinine_mg_dl']:.2f} mg/dL."
            )

    ratio_7d = 1.0
    base_7d = None
    delta_7d_mg = 0.0
    delta_7d_umol = 0.0
    if diem_7d:
        base_7d = min(diem_7d, key=lambda x: x["xn"]["creatinine_mg_dl"])
        base_mg = base_7d["xn"]["creatinine_mg_dl"]
        base_umol = base_7d["xn"]["creatinine_umol_l"]
        delta_7d_mg = round(scr_now_mg - base_mg, 3)
        delta_7d_umol = round(scr_now_umol - base_umol, 2)
        if xn_now.get("_creat_la_umol_goc") and base_7d["xn"].get("_creat_la_umol_goc") and base_umol > 0:
            ratio_7d = round(scr_now_umol / base_umol, 3)
        elif base_mg > 0:
            ratio_7d = round(scr_now_mg / base_mg, 3)

        tang_cap_tren_4 = (scr_now_mg >= 4.0 or scr_now_umol >= 353.6) and (
            tang_48h_dat or delta_7d_mg >= 0.3 or delta_7d_umol >= 26.5
        )
        if ratio_7d >= 3.0 or tang_cap_tren_4:
            stage = max(stage, 3)
            tieu_chi.append(
                f"Creatinine tăng gấp {ratio_7d:.2f}x nền 7 ngày ({base_mg:.2f} -> {scr_now_mg:.2f} mg/dL)"
                + (" hoặc >= 4.0 mg/dL kèm tăng cấp." if tang_cap_tren_4 else " (>= 3.0x).")
            )
        elif ratio_7d >= 2.0:
            stage = max(stage, 2)
            tieu_chi.append(
                f"Creatinine tăng gấp {ratio_7d:.2f}x nền 7 ngày ({base_mg:.2f} -> {scr_now_mg:.2f} mg/dL, 2.0-2.99x)."
            )
        elif ratio_7d >= 1.5:
            stage = max(stage, 1)
            tieu_chi.append(
                f"Creatinine tăng gấp {ratio_7d:.2f}x nền 7 ngày ({base_mg:.2f} -> {scr_now_mg:.2f} mg/dL, 1.5-1.99x)."
            )

    if stage == 0:
        return None

    base_ref = base_7d or base_48h
    base_mg_ref = base_ref["xn"]["creatinine_mg_dl"] if base_ref else scr_now_mg
    base_umol_ref = base_ref["xn"]["creatinine_umol_l"] if base_ref else scr_now_umol
    muc_do = "NGUY_KICH" if stage == 3 else ("CAO" if stage == 2 else "CANH_BAO")
    khuyen_cao_map = {
        1: "KDIGO AKI Giai đoạn 1: Ngừng ngay NSAID/thuốc độc thận, đánh giá thể tích tuần hoàn và theo dõi SCr/nước tiểu mỗi 24h.",
        2: "KDIGO AKI Giai đoạn 2: Ngừng mọi thuốc độc thận/Metformin, hội chẩn Thận học, kiểm tra điện giải (K+) và cân bằng dịch chặt chẽ.",
        3: "KDIGO AKI Giai đoạn 3 (NGUY KỊCH): Hội chẩn Thận học khẩn cấp đánh giá chỉ định lọc máu cấp cứu, ngừng toàn bộ thuốc thải qua thận/độc thận.",
    }
    return {
        "giai_doan": stage,
        "ten_giai_doan": f"KDIGO AKI Stage {stage}",
        "muc_do": muc_do,
        "creatinine_nen_mg_dl": base_mg_ref,
        "creatinine_nen_umol_l": base_umol_ref,
        "creatinine_hien_tai_mg_dl": scr_now_mg,
        "creatinine_hien_tai_umol_l": scr_now_umol,
        "tang_tuyet_doi_mg_dl": round(scr_now_mg - base_mg_ref, 2),
        "tang_tuyet_doi_umol_l": round(scr_now_umol - base_umol_ref, 1),
        "ti_le_tang": round(ratio_7d, 2),
        "tieu_chi_dat": tieu_chi,
        "khuyen_cao": khuyen_cao_map[stage],
    }


def _phan_tich_xu_huong_xn(
    tat_ca_lan_kham: List[Dict[str, Any]],
    hien_tai: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Phát hiện biến động lâm sàng đáng chú ý theo chuỗi thời gian xét nghiệm."""
    xu_huong: List[Dict[str, Any]] = []
    xn_now = hien_tai["xn"]
    t_now = hien_tai["dt"]

    def _chuoi_co_gia_tri(khoa: str) -> List[Dict[str, Any]]:
        return [v for v in tat_ca_lan_kham if v["xn"].get(khoa) is not None]

    # 1. eGFR trajectory slope
    ds_egfr = _chuoi_co_gia_tri("egfr")
    if len(ds_egfr) >= 2 and xn_now.get("egfr") is not None:
        v0 = ds_egfr[0]["xn"]["egfr"]
        v_prev = ds_egfr[-2]["xn"]["egfr"]
        v_now = xn_now["egfr"]
        dt0 = ds_egfr[0]["dt"]
        delta_so_voi_dau = round(v_now - v0, 1)
        delta_so_voi_truoc = round(v_now - v_prev, 1)
        giam_phan_tram = ((v_prev - v_now) / v_prev * 100.0) if v_prev > 0 else 0.0
        giam_nam = None
        if dt0 is not None and t_now is not None:
            so_ngay = (t_now - dt0).total_seconds() / 86400.0
            if so_ngay >= 30.0:
                giam_nam = round((v0 - v_now) / (so_ngay / 365.25), 1)
        if giam_phan_tram >= 15.0 or delta_so_voi_truoc <= -10.0 or (giam_nam is not None and giam_nam > 5.0):
            muc = "NGUY_KICH" if v_now < 30.0 else ("CAO" if giam_phan_tram >= 25.0 or v_now < 45.0 else "CANH_BAO")
            mo_ta_slope = f" (tốc độ suy giảm ~{giam_nam} mL/phút/năm)" if giam_nam is not None else ""
            xu_huong.append({
                "chi_so": "eGFR",
                "gia_tri_truoc": v_prev,
                "gia_tri_hien_tai": v_now,
                "thay_doi": delta_so_voi_truoc,
                "don_vi": "mL/min/1.73m2",
                "xu_huong": "GIAM_MANH",
                "muc_do": muc,
                "toc_do_giam_nam": giam_nam,
                "y_nghia": f"eGFR giảm từ {v_prev} xuống {v_now} mL/min/1.73m2{mo_ta_slope}: cần rà soát lại toàn bộ thuốc thải qua thận.",
            })

    # 2. HbA1c drift
    ds_hba1c = _chuoi_co_gia_tri("hba1c")
    if len(ds_hba1c) >= 2 and xn_now.get("hba1c") is not None:
        v_prev = ds_hba1c[-2]["xn"]["hba1c"]
        v_now = xn_now["hba1c"]
        delta = round(v_now - v_prev, 2)
        if delta >= 0.5 or (v_now > 7.0 and delta > 0.2):
            xu_huong.append({
                "chi_so": "HbA1c",
                "gia_tri_truoc": v_prev,
                "gia_tri_hien_tai": v_now,
                "thay_doi": delta,
                "don_vi": "%",
                "xu_huong": "TANG_XAU_DI",
                "muc_do": "CAO" if v_now >= 9.0 or delta >= 1.5 else "CANH_BAO",
                "y_nghia": f"HbA1c tăng từ {v_prev}% lên {v_now}% (+{delta}%): kiểm soát đường huyết kém dần, cần đánh giá tuân thủ và điều chỉnh phác đồ.",
            })

    # 3. INR drift
    ds_inr = _chuoi_co_gia_tri("inr")
    if len(ds_inr) >= 2 and xn_now.get("inr") is not None:
        v_prev = ds_inr[-2]["xn"]["inr"]
        v_now = xn_now["inr"]
        delta = round(v_now - v_prev, 2)
        if v_now > 3.5 or delta >= 1.0:
            xu_huong.append({
                "chi_so": "INR",
                "gia_tri_truoc": v_prev,
                "gia_tri_hien_tai": v_now,
                "thay_doi": delta,
                "don_vi": "",
                "xu_huong": "TANG_MANH",
                "muc_do": "NGUY_KICH" if v_now >= 4.5 else "CAO",
                "y_nghia": f"INR tăng vọt từ {v_prev} lên {v_now} (+{delta}): nguy cơ xuất huyết nghiêm trọng do quá liều kháng vitamin K hoặc tương tác thuốc.",
            })
        elif v_prev >= 2.0 and (v_now < 2.0 or delta <= -0.8):
            xu_huong.append({
                "chi_so": "INR",
                "gia_tri_truoc": v_prev,
                "gia_tri_hien_tai": v_now,
                "thay_doi": delta,
                "don_vi": "",
                "xu_huong": "GIAM_DUOI_NGUONG",
                "muc_do": "CANH_BAO",
                "y_nghia": f"INR tụt từ {v_prev} xuống {v_now} ({delta}): mất hiệu lực chống đông, nguy cơ huyết khối tắc mạch.",
            })

    # 4. Hemoglobin (Hb) drop
    ds_hb = _chuoi_co_gia_tri("hb")
    if len(ds_hb) >= 2 and xn_now.get("hb") is not None:
        v_prev = ds_hb[-2]["xn"]["hb"]
        v_now = xn_now["hb"]
        delta = round(v_now - v_prev, 2)
        if delta <= -2.0 or (v_prev > 0 and (v_prev - v_now) / v_prev >= 0.15 and v_now < 11.0):
            xu_huong.append({
                "chi_so": "Hb",
                "gia_tri_truoc": v_prev,
                "gia_tri_hien_tai": v_now,
                "thay_doi": delta,
                "don_vi": "g/dL",
                "xu_huong": "GIAM_MANH",
                "muc_do": "NGUY_KICH" if v_now < 8.0 or delta <= -3.0 else "CAO",
                "y_nghia": f"Hemoglobin giảm mạnh từ {v_prev} xuống {v_now} g/dL ({delta} g/dL): nghi ngờ xuất huyết tiến triển hoặc tán huyết.",
            })

    # 5. Kali máu (K+) rise
    ds_k = _chuoi_co_gia_tri("k")
    if len(ds_k) >= 2 and xn_now.get("k") is not None:
        v_prev = ds_k[-2]["xn"]["k"]
        v_now = xn_now["k"]
        delta = round(v_now - v_prev, 2)
        if (delta >= 0.8 and v_now > 5.0) or (v_now >= 5.5 and delta > 0.3):
            xu_huong.append({
                "chi_so": "Kali (K+)",
                "gia_tri_truoc": v_prev,
                "gia_tri_hien_tai": v_now,
                "thay_doi": delta,
                "don_vi": "mmol/L",
                "xu_huong": "TANG_MANH",
                "muc_do": "NGUY_KICH" if v_now >= 6.0 else "CAO",
                "y_nghia": f"Kali máu tăng từ {v_prev} lên {v_now} mmol/L (+{delta}): nguy cơ rối loạn nhịp tim nặng nếu tiếp tục thuốc giữ kali.",
            })

    # 6. AST / ALT spike
    for ten_men, khoa in (("AST", "ast"), ("ALT", "alt")):
        ds_men = _chuoi_co_gia_tri(khoa)
        if len(ds_men) >= 2 and xn_now.get(khoa) is not None:
            v_prev = ds_men[-2]["xn"][khoa]
            v_now = xn_now[khoa]
            delta = round(v_now - v_prev, 1)
            if (v_prev > 0 and v_now >= 2.0 * v_prev and v_now > 100.0) or (v_now > 120.0 and delta >= 60.0):
                xu_huong.append({
                    "chi_so": ten_men,
                    "gia_tri_truoc": v_prev,
                    "gia_tri_hien_tai": v_now,
                    "thay_doi": delta,
                    "don_vi": "U/L",
                    "xu_huong": "TANG_VOT",
                    "muc_do": "NGUY_KICH" if v_now >= 300.0 else "CAO",
                    "y_nghia": f"{ten_men} tăng vọt từ {v_prev} lên {v_now} U/L (+{delta}): dấu hiệu tổn thương tế bào gan cấp (DILI/viêm gan).",
                })

    return xu_huong


def _phan_tich_chuoi_thuoc_doc(
    lich_su_chuan: List[Dict[str, Any]],
    hien_tai_chuan: Dict[str, Any],
    kdigo_aki: Optional[Dict[str, Any]],
    xu_huong_xn: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Phát hiện chuỗi phối hợp thuốc độc hại liên lần khám."""
    canh_bao: List[Dict[str, Any]] = []
    t_now = hien_tai_chuan["dt"]

    # Gộp thuốc lần khám hiện tại + các lần khám gần đây (<= 30 ngày hoặc không có timestamp)
    thuoc_hien_tai: Dict[str, str] = {hc: ten for hc, ten in hien_tai_chuan["thuoc"]}
    thuoc_gan_day: Dict[str, str] = dict(thuoc_hien_tai)
    for h in lich_su_chuan:
        if t_now is not None and h["dt"] is not None:
            if (t_now - h["dt"]).total_seconds() > 30 * 86400:
                continue
        for hc, ten in h["thuoc"]:
            thuoc_gan_day.setdefault(hc, ten)

    tap_gan_day = set(thuoc_gan_day)
    tap_hien_tai = set(thuoc_hien_tai)

    # 1. Triple Whammy (ACEi/ARB + Lợi tiểu + NSAID) qua các lần khám
    acei_arb = sorted(tap_gan_day & _ACEI_ARB)
    diur = sorted(tap_gan_day & _DIURETICS)
    nsaid = sorted(tap_gan_day & _NSAIDS)
    if acei_arb and diur and nsaid and (tap_hien_tai & (_ACEI_ARB | _DIURETICS | _NSAIDS)):
        ds_lien_quan = [thuoc_gan_day[x] for x in (acei_arb + diur + nsaid)]
        canh_bao.append({
            "loai_canh_bao": "TRIPLE_WHAMMY",
            "muc_do": "NGUY_KICH",
            "thuoc_lien_quan": ds_lien_quan,
            "mo_ta": (
                f"Phối hợp 'Triple Whammy' xuyên lần khám: ACEi/ARB ({', '.join(acei_arb)}) + "
                f"Lợi tiểu ({', '.join(diur)}) + NSAID ({', '.join(nsaid)}), làm co tiểu động mạch đến và giãn tiểu động mạch đi gây suy thận cấp."
            ),
            "khuyen_cao": "Ngừng ngay NSAID (thay bằng Paracetamol nếu gan ổn), kiểm tra Creatinine/eGFR và Kali máu.",
        })

    # 2. Thuốc độc thận / chống chỉ định khi có KDIGO AKI hoặc eGFR giảm nhanh / < 30
    egfr_now = hien_tai_chuan["xn"].get("egfr")
    egfr_giam_manh = any(x["chi_so"] == "eGFR" for x in xu_huong_xn)
    if kdigo_aki is not None or (egfr_now is not None and egfr_now < 30.0) or egfr_giam_manh:
        thuoc_nguy_hiem = sorted(tap_hien_tai & _NEPHROTOXIC_OR_AKI_UNSAFE)
        if thuoc_nguy_hiem:
            ly_do_than = (
                kdigo_aki["ten_giai_doan"]
                if kdigo_aki
                else (f"eGFR={egfr_now} (<30)" if egfr_now is not None and egfr_now < 30.0 else "eGFR giảm nhanh")
            )
            canh_bao.append({
                "loai_canh_bao": "NEPHROTOXIC_AKI_CASCADE",
                "muc_do": "NGUY_KICH" if (kdigo_aki or (egfr_now is not None and egfr_now < 30.0)) else "CAO",
                "thuoc_lien_quan": [thuoc_hien_tai[x] for x in thuoc_nguy_hiem],
                "mo_ta": (
                    f"Tiếp tục/kê thuốc nguy cơ cao trên nền {ly_do_than}: "
                    f"{', '.join(thuoc_nguy_hiem)} (nguy cơ nặng thêm AKI, toan lactic do Metformin, tăng K+)."
                ),
                "khuyen_cao": "Ngừng NSAID/Metformin/Spironolactone và hiệu chỉnh liều hoặc thay thế kháng sinh độc thận ngay.",
            })

    # 3. Tiếp tục thuốc độc gan khi AST/ALT tăng vọt
    men_gan_tang = any(x["chi_so"] in ("AST", "ALT") for x in xu_huong_xn)
    if men_gan_tang:
        thuoc_gan = sorted(tap_hien_tai & _HEPATOTOXIC)
        if thuoc_gan:
            canh_bao.append({
                "loai_canh_bao": "HEPATOTOXIC_CASCADE",
                "muc_do": "CAO",
                "thuoc_lien_quan": [thuoc_hien_tai[x] for x in thuoc_gan],
                "mo_ta": (
                    f"AST/ALT tăng vọt nhưng đơn hiện tại vẫn có thuốc chuyển hóa/độc gan: {', '.join(thuoc_gan)}."
                ),
                "khuyen_cao": "Tạm ngừng các thuốc nghi ngờ gây tổn thương gan do thuốc (DILI) và đánh giá lại chức năng gan.",
            })

    # 4. Chống đông / kháng kết tập khi INR tăng vọt (>3.5) hoặc Hb tụt mạnh
    inr_now = hien_tai_chuan["xn"].get("inr")
    inr_tang = any(x["chi_so"] == "INR" and x["xu_huong"] == "TANG_MANH" for x in xu_huong_xn)
    hb_giam = any(x["chi_so"] == "Hb" for x in xu_huong_xn)
    if inr_tang or (inr_now is not None and inr_now > 3.5) or hb_giam:
        thuoc_dong_mau = sorted(tap_hien_tai & _ANTICOAG_ANTIPLATELET)
        if thuoc_dong_mau:
            chi_tiet = []
            if inr_tang or (inr_now is not None and inr_now > 3.5):
                chi_tiet.append(f"INR={inr_now}")
            if hb_giam:
                chi_tiet.append("Hb giảm mạnh")
            canh_bao.append({
                "loai_canh_bao": "ANTICOAGULANT_BLEEDING_CASCADE",
                "muc_do": "NGUY_KICH",
                "thuoc_lien_quan": [thuoc_hien_tai[x] for x in thuoc_dong_mau],
                "mo_ta": (
                    f"Nguy cơ xuất huyết nghiêm trọng ({', '.join(chi_tiet)}) khi đang dùng thuốc chống đông/kháng tiểu cầu: "
                    f"{', '.join(thuoc_dong_mau)}."
                ),
                "khuyen_cao": "Tạm ngừng chống đông/NSAID, tầm soát nguồn chảy máu, cân nhắc Vitamin K hoặc đảo ngược đông máu nếu có xuất huyết.",
            })

    return canh_bao


def phan_tich_quy_dao_lam_sang(
    lich_su_lan_kham: Optional[List[Dict[str, Any]]],
    lan_kham_hien_tai: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Phân tích quỹ đạo xét nghiệm và dùng thuốc qua nhiều lần khám.

    Trả về dict với đúng các khóa:
    {kdigo_aki: dict|None, xu_huong_xn: list[dict], canh_bao_thuoc_doc: list[dict], tom_tat_nguy_co: str}.
    """
    hien_tai_raw = lan_kham_hien_tai if isinstance(lan_kham_hien_tai, dict) else {}
    lich_su_raw = [v for v in (lich_su_lan_kham or []) if isinstance(v, dict)]

    tuoi_f = so_an_toan(hien_tai_raw.get("tuoi"))
    tuoi_mac_dinh = int(tuoi_f) if tuoi_f is not None and tuoi_f > 0 else None
    la_nu_mac_dinh = _la_nu_tu_bn(hien_tai_raw)

    moc_mac_dinh = datetime.now(timezone.utc).replace(tzinfo=None)
    t_now = _phan_tich_thoi_gian(hien_tai_raw, moc_mac_dinh) or moc_mac_dinh

    hien_tai_chuan = {
        "dt": t_now,
        "xn": _trich_xet_nghiem_lan_kham(hien_tai_raw, tuoi_mac_dinh, la_nu_mac_dinh),
        "thuoc": _trich_thuoc_lan_kham(hien_tai_raw),
    }

    lich_su_chuan: List[Dict[str, Any]] = []
    for item in lich_su_raw:
        dt_item = _phan_tich_thoi_gian(item, t_now)
        lich_su_chuan.append({
            "dt": dt_item,
            "xn": _trich_xet_nghiem_lan_kham(item, tuoi_mac_dinh, la_nu_mac_dinh),
            "thuoc": _trich_thuoc_lan_kham(item),
        })

    # Sắp xếp lịch sử tăng dần theo thời gian (bản ghi không có thời gian xếp trước bản ghi có thời gian hoặc theo thứ tự)
    lich_su_co_dt = sorted([v for v in lich_su_chuan if v["dt"] is not None], key=lambda x: x["dt"])
    lich_su_khong_dt = [v for v in lich_su_chuan if v["dt"] is None]
    tat_ca_lan_kham = lich_su_khong_dt + lich_su_co_dt + [hien_tai_chuan]

    kdigo_aki = _danh_gia_kdigo_aki(lich_su_co_dt, hien_tai_chuan)
    xu_huong_xn = _phan_tich_xu_huong_xn(tat_ca_lan_kham, hien_tai_chuan)
    canh_bao_thuoc_doc = _phan_tich_chuoi_thuoc_doc(lich_su_chuan, hien_tai_chuan, kdigo_aki, xu_huong_xn)

    diem_nhan: List[str] = []
    if kdigo_aki is not None:
        diem_nhan.append(f"{kdigo_aki['ten_giai_doan']} ({kdigo_aki['muc_do']})")
    for xh in xu_huong_xn:
        diem_nhan.append(f"{xh['chi_so']} {xh['xu_huong']} ({xh['gia_tri_truoc']} -> {xh['gia_tri_hien_tai']} {xh['don_vi']}".strip() + ")")
    for cb in canh_bao_thuoc_doc:
        diem_nhan.append(f"{cb['loai_canh_bao']}: {', '.join(cb['thuoc_lien_quan'])}")

    tom_tat = "; ".join(diem_nhan) if diem_nhan else "Không phát hiện bất thường quỹ đạo lâm sàng."

    return {
        "kdigo_aki": kdigo_aki,
        "xu_huong_xn": xu_huong_xn,
        "canh_bao_thuoc_doc": canh_bao_thuoc_doc,
        "tom_tat_nguy_co": tom_tat,
    }
