# -*- coding: utf-8 -*-
"""Ep kieu an toan cho du lieu benh nhan / xet nghiem di vao tu JSON (giao dien, HTTP).

VI SAO. JSON tu giao dien hay gui so duoi dang chuoi ({"egfr": "25", "tuoi": "82"}).
Truoc day cong_rui_ro so sanh thang `"25" < 15` -> TypeError trong nhanh.chay_trung_gian
-> /api/ho-so tra 500. Moi gia tri so di qua `so_an_toan`: doc duoc thi thanh so, khong doc
duoc (rac, NaN, vo cung, bool, list...) thi coi nhu THIEU (None) chu khong sap.
"""
from __future__ import annotations

import math
from typing import Any, Dict, Optional

# Cac khoa thong tin benh nhan mang gia tri so (so nguyen thi ep ve int)
KHOA_SO_NGUYEN_BN = ("tuoi", "thang_tuoi", "tuan_thai", "so_thuoc_dang_dung")
KHOA_SO_THUC_BN = ("egfr", "crcl", "can_nang", "can_nang_kg", "chieu_cao", "chieu_cao_cm", "creatinine")

# Cac khoa xet nghiem van la chuoi (don vi, ghi chu) - khong ep so
_DUOI_KHOA_CHUOI_XN = ("_unit", "_don_vi", "don_vi", "unit", "ghi_chu", "ngay", "thoi_gian")


def so_an_toan(x: Any) -> Optional[float]:
    """-> float neu doc duoc mot so huu han, nguoc lai None. Nhan dau phay thap phan "2,5"."""
    if x is None or isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        v = float(x)
    elif isinstance(x, str):
        s = x.strip().replace(",", ".")
        if not s:
            return None
        try:
            v = float(s)
        except ValueError:
            return None
    else:
        return None
    return v if math.isfinite(v) else None


def _ep_nguyen(v: float) -> Any:
    return int(v) if float(v).is_integer() else v


_CHUOI_DUNG = {"true", "1", "có", "co", "yes", "y", "đúng", "dung", "mang thai", "có thai", "co thai"}
_CHUOI_SAI = {"false", "0", "không", "khong", "no", "n", "sai", "không có", "khong co", "chưa", "chua"}


def ep_bool_an_toan(x: Any) -> Optional[bool]:
    """Chuyển bool / số 0-1 / chuỗi tiếng Việt-Anh thành bool hoặc None nếu không rõ."""
    if x is None:
        return None
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, float)):
        if x == 1:
            return True
        if x == 0:
            return False
        return None
    if isinstance(x, str):
        s = x.strip().lower()
        if s in _CHUOI_DUNG:
            return True
        if s in _CHUOI_SAI:
            return False
    return None


def chuan_hoa_thong_tin_benh_nhan(tt: Any) -> Optional[Dict[str, Any]]:
    """Ban sao dict thong tin benh nhan voi cac truong so da ep kieu; khoa so khong doc duoc bi bo."""
    if not isinstance(tt, dict):
        return None
    ra = dict(tt)
    for k in KHOA_SO_NGUYEN_BN + KHOA_SO_THUC_BN:
        if k not in ra or ra[k] is None:
            continue
        v = so_an_toan(ra[k])
        if v is None:
            ra.pop(k)
        else:
            ra[k] = _ep_nguyen(v) if k in KHOA_SO_NGUYEN_BN else v

    # Chuẩn hóa đồng bộ cờ thai kỳ (`co_thai`, `thai_ky`, `mang_thai`)
    cac_co_thai = {k: ep_bool_an_toan(ra.get(k)) for k in ("co_thai", "thai_ky", "mang_thai") if k in ra}
    if any(v is True for v in cac_co_thai.values()):
        ra["thai_ky"] = True
        ra["mang_thai"] = True
        if "co_thai" in ra:
            ra["co_thai"] = True
    elif any(v is False for v in cac_co_thai.values()):
        for k, v in cac_co_thai.items():
            if v is not None:
                ra[k] = v
        if cac_co_thai.get("co_thai") is False:
            ra.setdefault("thai_ky", False)
            ra.setdefault("mang_thai", False)

    xn = ra.get("xet_nghiem")
    if isinstance(xn, dict):
        ra["xet_nghiem"] = chuan_hoa_du_lieu_xet_nghiem_dau_vao(xn)
    return ra


def chuan_hoa_du_lieu_xet_nghiem_dau_vao(xn: Any) -> Optional[Dict[str, Any]]:
    """Ep moi chi so xet nghiem ve so; giu nguyen truong don vi/ghi chu; chi so rac bi bo."""
    if not isinstance(xn, dict):
        return None
    ra: Dict[str, Any] = {}
    for k, val in xn.items():
        ks = str(k).lower()
        if val is None:
            continue
        if any(ks.endswith(d) for d in _DUOI_KHOA_CHUOI_XN) or isinstance(val, (dict, list)):
            ra[k] = val
            continue
        v = so_an_toan(val)
        if v is not None:
            ra[k] = v
    return ra
