# -*- coding: utf-8 -*-
"""[Dịch vụ, an toàn và minh bạch › An toàn]
Làm gì   : Ép dữ liệu thô từ JSON/HTTP về kiểu đúng để lỗi nhập liệu không làm hỏng các bước
           sau.
Vào → Ra : giá trị thô (số, cờ, thông tin bệnh nhân, xét nghiệm) → giá trị đúng kiểu, thiếu
           hoặc sai thì về mặc định an toàn
Đọc từ   : so_an_toan() ép về số hoặc None; chuan_hoa_thong_tin_benh_nhan() chuẩn hoá hồ sơ
           vào
Mục lục (các hàm/lớp chính):
  so_an_toan()                            Đọc một giá trị thành số hữu hạn an toàn
  ep_bool_an_toan()                       Ép giá trị về đúng/sai hoặc None
  chuan_hoa_thong_tin_benh_nhan()         Chuẩn hoá thông tin bệnh nhân về đúng kiểu
  chuan_hoa_du_lieu_xet_nghiem_dau_vao()  Ép chỉ số xét nghiệm đầu vào về số
Dùng bởi : cong_cu_lam_sang/canh_bao_tuong_tac_thuoc,
           cong_cu_lam_sang/quy_dao_nhieu_lan_kham, duong_ong/b5_xep_cho_cong_rui_ro,
           he_thong/dich_vu_http, he_thong/dieu_phoi_cac_chot_an_toan
Tên cũ   : ep_kieu_dau_vao.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Ép kiểu an toàn cho dữ liệu bệnh nhân / xét nghiệm đi vào từ JSON (giao diện, HTTP).

VÌ SAO. JSON từ giao diện hay gửi số dưới dạng chuỗi ({"egfr": "25", "tuoi": "82"}).
Trước đây cong_rui_ro so sánh thẳng `"25" < 15` -> TypeError trong nhanh.chay_trung_gian
-> /api/ho-so trả 500. Mọi giá trị số đi qua `so_an_toan`: đọc được thì thành số, không đọc
được (rác, NaN, vô cùng, bool, list...) thì coi như THIẾU (None) chứ không sập.
"""
from __future__ import annotations

import math
from typing import Any, Dict, Optional

# Các khoá thông tin bệnh nhân mang giá trị số (số nguyên thì ép về int)
KHOA_SO_NGUYEN_BN = ("tuoi", "thang_tuoi", "tuan_thai", "so_thuoc_dang_dung")
KHOA_SO_THUC_BN = ("egfr", "crcl", "can_nang", "can_nang_kg", "chieu_cao", "chieu_cao_cm", "creatinine")

# Các khoá xét nghiệm vẫn là chuỗi (đơn vị, ghi chú) - không ép số
_DUOI_KHOA_CHUOI_XN = ("_unit", "_don_vi", "don_vi", "unit", "ghi_chu", "ngay", "thoi_gian")


# ═══ so_an_toan() — Đọc một giá trị thành số hữu hạn an toàn ══════════════════════════
# Nhận dấu phẩy thập phân như 2,5; không đọc được thì trả None.
def so_an_toan(x: Any) -> Optional[float]:
    """-> float nếu đọc được một số hữu hạn, ngược lại None. Nhận dấu phẩy thập phân "2,5"."""
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


# ─── _ep_nguyen() — Đổi số nguyên dạng float về int ───────────────────────────────────
# Giữ nguyên nếu không phải số nguyên.
def _ep_nguyen(v: float) -> Any:
    return int(v) if float(v).is_integer() else v


_CHUOI_DUNG = {"true", "1", "có", "co", "yes", "y", "đúng", "dung", "mang thai", "có thai", "co thai"}
_CHUOI_SAI = {"false", "0", "không", "khong", "no", "n", "sai", "không có", "khong co", "chưa", "chua"}


# ═══ ep_bool_an_toan() — Ép giá trị về đúng/sai hoặc None ═════════════════════════════
# Nhận bool, số 0-1 và chuỗi tiếng Việt hay Anh; không rõ thì None.
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


# ═══ chuan_hoa_thong_tin_benh_nhan() — Chuẩn hoá thông tin bệnh nhân về đúng kiểu ═════
# Trả bản sao đã ép trường số; khoá số không đọc được bị bỏ.
def chuan_hoa_thong_tin_benh_nhan(tt: Any) -> Optional[Dict[str, Any]]:
    """Bản sao dict thông tin bệnh nhân với các trường số đã ép kiểu; khoá số không đọc được bị bỏ."""
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


# ═══ chuan_hoa_du_lieu_xet_nghiem_dau_vao() — Ép chỉ số xét nghiệm đầu vào về số ══════
# Giữ trường đơn vị và ghi chú; chỉ số rác bị bỏ.
def chuan_hoa_du_lieu_xet_nghiem_dau_vao(xn: Any) -> Optional[Dict[str, Any]]:
    """Ép mọi chỉ số xét nghiệm về số; giữ nguyên trường đơn vị/ghi chú; chỉ số rác bị bỏ."""
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
