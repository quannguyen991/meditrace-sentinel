# -*- coding: utf-8 -*-
"""Do TI LE BO SOT thong tin cua khau trich menh de.

Mot menh de cua dap an la BO SOT neu khong co ban trich nao ghep duoc voi no.
Dung chinh phep ghep cua `src.do_trich.ghep` (ghep tham lam theo do giong tu,
nguong 0,6), nen so lieu nay cung he voi cac so khac cua du an.

Cau 1 cua giam khao: "giam bo sot thong tin quan trong". Chi so nay tra loi cau do
bang SO, thay cho cau chung chung.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Optional

from src.do_trich import NGUONG_GHEP, ghep


def ti_le_bo_sot(cac_ca: list[tuple[list[dict], Optional[list[dict]]]],
                 nguong: float = NGUONG_GHEP) -> dict:
    """`cac_ca`: moi phan tu la `(dap_an, trich)`; `trich` co the la None (coi nhu rong).

    -> {"so_menh_de_dap_an", "so_bo_sot", "ti_le_bo_sot", "theo_nhom"}. Menh de dap an
    co khoa `nhom_loi` thi tinh rieng theo nhom; thieu khoa thi vao nhom "khac".
    """
    tong = bo_sot = 0
    nhom = defaultdict(lambda: [0, 0])
    for dap_an, trich in cac_ca:
        dap_an = dap_an or []
        _cap, thieu, _thua = ghep(dap_an, trich or [], nguong)
        ma_thieu = {id(d) for d in thieu}
        for d in dap_an:
            ten = d.get("nhom_loi") or "khac"
            nhom[ten][0] += 1
            tong += 1
            if id(d) in ma_thieu:
                nhom[ten][1] += 1
                bo_sot += 1
    return {
        "so_menh_de_dap_an": tong,
        "so_bo_sot": bo_sot,
        "ti_le_bo_sot": (bo_sot / tong) if tong else 0.0,
        "theo_nhom": {k: {"so_menh_de": v[0], "so_bo_sot": v[1],
                          "ti_le": (v[1] / v[0]) if v[0] else 0.0}
                      for k, v in sorted(nhom.items())},
    }
