# -*- coding: utf-8 -*-
"""Loc tu dong cac menh de do MAY gan truoc (Task E4 cua ke hoach nang cap).

Nhan do may gan co the sai va khong ai kiem lai, nen chi giu menh de qua cac phep kiem co
the kiem BANG LUAT. Phep kiem nay chi bat duoc nhan sai ro rang; KHONG chung minh duoc
chu the, phu dinh hay thoi gian dung. Khong thay duoc nguoi doc.
"""
from __future__ import annotations

import unicodedata

from src.do_trich import do_giong

CAC_TRUONG_BAT_BUOC = ("chu_the", "noi_dung", "do_chac_chan", "luot_thoai")
DO_CHAC_CHAN = {"chắc chắn", "nghi ngờ", "chưa ghi nhận"}


def chuan(s) -> str:
    return " ".join(unicodedata.normalize("NFC", str(s or "")).lower().split())


def loc_menh_de_may(menh_de: list[dict], van_ban: str) -> tuple[list[dict], list[dict]]:
    """-> (giu, bo); moi phan tu cua `bo` co them khoa `ly_do`.

    Giu khi: du truong bat buoc, `chu_the` va `noi_dung` khong rong, `do_chac_chan` hop le,
    `trich_dan` KHONG rong va moi chuoi la chuoi con nguyen van cua `van_ban` (sau NFC), va
    khong trung (chu_the, noi_dung) voi mot menh de da giu.
    """
    giu, bo, da_co = [], [], set()
    goc = chuan(van_ban)
    for m in menh_de or []:
        ly_do = None
        if not isinstance(m, dict):
            bo.append({"menh_de": m, "ly_do": "khong phai tu dien"})
            continue
        thieu = [k for k in CAC_TRUONG_BAT_BUOC if k not in m]
        if thieu:
            ly_do = f"thieu truong {thieu}"
        elif not chuan(m["chu_the"]) or not chuan(m["noi_dung"]):
            ly_do = "chu_the hoac noi_dung rong"
        elif m["do_chac_chan"] not in DO_CHAC_CHAN:
            ly_do = "do_chac_chan khong hop le"
        else:
            td = m.get("trich_dan")
            if not isinstance(td, list) or not td or not all(isinstance(x, str) and x.strip() for x in td):
                ly_do = "khong co trich_dan"
            elif any(chuan(x) not in goc for x in td):
                ly_do = "trich_dan khong phai chuoi con cua van ban"
            else:
                khoa = (chuan(m["chu_the"]), chuan(m["noi_dung"]))
                if khoa in da_co:
                    ly_do = "trung menh de"
                else:
                    da_co.add(khoa)
        if ly_do:
            bo.append({**m, "ly_do": ly_do})
        else:
            giu.append(m)
    return giu, bo


def phu_thuc_the(menh_de: list[dict], thuc_the: list[dict], nguong: float = 0.6) -> dict:
    """Ti le thuc the goc (cua bo NER) duoc mot menh de PHU: chuoi thuc the nam trong
    `noi_dung`, hoac `do_giong` >= nguong. -> {"so_thuc_the", "so_phu", "ti_le_phu"}."""
    noi = [chuan(m.get("noi_dung")) for m in menh_de or []]
    phu = 0
    for t in thuc_the or []:
        x = chuan(t.get("text"))
        if x and any(x in n or do_giong(x, n) >= nguong for n in noi):
            phu += 1
    tong = len(thuc_the or [])
    return {"so_thuc_the": tong, "so_phu": phu, "ti_le_phu": (phu / tong) if tong else 0.0}
