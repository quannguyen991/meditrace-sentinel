# -*- coding: utf-8 -*-
"""Nhat ky canh bao cho nghien cuu (dac ta muc 49).

Moi dong mot canh bao: ca, phat bieu, ma, bang chung, bo phat hien, phien ban,
muc do, bat dinh, trang thai cuoi. Hai cot de trong (None) cho sau nay dien:
    bac_si_xac_nhan    bac si co dong y canh bao dung khong (tu giao dien duyet)
    dung_theo_bo_cham  canh bao co trung loi ma bo cham tu dong tim ra khong
                       (`src.do_canh_bao` dien khi chay tren tap co dap an)
"""
import json
from pathlib import Path
from typing import Iterable, List, Optional

from src.canh_bao.loai import PHIEN_BAN


def dong(ca_id: str, kq: dict, nhan_bo_cham: Optional[dict] = None) -> List[dict]:
    """kq = `gop.chay(...)`. nhan_bo_cham = {phat_bieu_id: dung/sai} neu co."""
    ra = []
    for pid, v in kq["theo_phat_bieu"].items():
        tt = kq["trang_thai_D"][pid]["trang_thai"]
        for c in v["tat_ca"]:
            ra.append(_dong(ca_id, c, tt, None if nhan_bo_cham is None else nhan_bo_cham.get((pid, c.ma))))
    for c in kq["toan_ca"]:
        ra.append(_dong(ca_id, c, None, None))
    return ra


def _dong(ca_id, c, trang_thai_cuoi, dung):
    return {"ca": ca_id, "phat_bieu": c.phat_bieu_id, "ma": c.ma, "nhom": c.nhom, "luot": c.luot,
            "trich": c.trich, "ly_do": c.ly_do, "bo_phat_hien": c.bo_phat_hien, "phien_ban": PHIEN_BAN,
            "tin_cay_bo_phat_hien": c.tin_cay, "ket_luan": c.ket_luan, "muc_do": c.muc_do,
            "bat_dinh": c.bat_dinh, "anh_huong_trang_thai": c.anh_huong_trang_thai,
            "trang_thai_cuoi": trang_thai_cuoi, "bac_si_xac_nhan": None, "dung_theo_bo_cham": dung}


def ghi(duong: Path, cac_dong: Iterable[dict]):
    duong.parent.mkdir(parents=True, exist_ok=True)
    with open(duong, "a", encoding="utf-8") as f:
        for d in cac_dong:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
