# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Nhãn người]
Làm gì   : Đọc phiếu gán nhãn của người thật và tính độ đồng thuận giữa hai người (Cohen κ),
           để biết nhãn người có nhất quán không (kế hoạch 27/11, Task 7; mục tiêu κ ≥ 0,6). κ KHÔNG đo độ đúng của
           bộ chấm tự động: muốn vậy phải phân xử nhãn hai người rồi mới so với bộ chấm.
Vào → Ra : hai tệp phiếu CSV (cột ma_muc, nhan) → κ, tỷ lệ đồng ý, ma trận nhầm
Mục lục:
  NHAN_HOP_LE     Các nhãn người gán được dùng
  nap_nhan()      Đọc một phiếu, bỏ dòng chưa gán, báo lỗi nhãn lạ
  cohen_kappa()   κ của hai dãy nhãn cùng thứ tự
  dong_thuan()    So hai phiếu theo mã mục chung
Máy KHÔNG BAO GIỜ điền nhãn thay người: tệp này chỉ đọc và tính.
"""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional

NHAN_HOP_LE = (
    "dung",          # đúng nội dung, đúng người, đúng mục
    "sai_nguoi",     # nội dung có thật nhưng gán nhầm người (bệnh nhân ↔ người nhà)
    "sai_noi_dung",  # sai số liệu / phủ định / thời gian / trạng thái
    "bia",           # hội thoại không nói điều này
    "sai_muc",       # đúng nội dung nhưng xếp nhầm mục bệnh án
    "khong_ro",      # người gán không quyết được
)


def nap_nhan(duong: str | Path) -> Dict[str, str]:
    ra: Dict[str, str] = {}
    with open(duong, encoding="utf-8-sig", newline="") as f:
        for dong in csv.DictReader(f):
            ma = (dong.get("ma_muc") or "").strip()
            nhan = (dong.get("nhan") or "").strip()
            if not ma or not nhan:
                continue
            if nhan not in NHAN_HOP_LE:
                raise ValueError(f"Nhãn lạ '{nhan}' ở mục {ma}; chỉ dùng: {', '.join(NHAN_HOP_LE)}")
            if ma in ra:
                raise ValueError(f"Mã mục {ma} bị gán hai lần trong cùng một phiếu")
            ra[ma] = nhan
    return ra


def cohen_kappa(a: List[str], b: List[str]) -> Optional[float]:
    """κ của hai dãy nhãn. Trả None khi không xác định (cả hai chỉ dùng một nhãn giống nhau: mẫu số 0)."""
    if len(a) != len(b):
        raise ValueError("Hai dãy nhãn phải cùng độ dài")
    n = len(a)
    if n == 0:
        raise ValueError("Không có mục nào để so")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    if pe >= 1.0:  # cả hai chỉ dùng đúng một nhãn giống nhau: κ không xác định
        return None
    return (po - pe) / (1 - pe)


def dong_thuan(nhan_a: Dict[str, str], nhan_b: Dict[str, str]) -> dict:
    chung = sorted(set(nhan_a) & set(nhan_b))
    a = [nhan_a[k] for k in chung]
    b = [nhan_b[k] for k in chung]
    return {
        "so_muc": len(chung),
        "thieu_o_a": sorted(set(nhan_b) - set(nhan_a)),
        "thieu_o_b": sorted(set(nhan_a) - set(nhan_b)),
        "ty_le_dong_y": (sum(x == y for x, y in zip(a, b)) / len(chung)) if chung else None,
        "kappa": cohen_kappa(a, b) if chung else None,
        "ma_tran": {f"{x}|{y}": n for (x, y), n in Counter(zip(a, b)).items()},
    }
