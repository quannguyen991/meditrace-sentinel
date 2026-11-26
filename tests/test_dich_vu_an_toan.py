# -*- coding: utf-8 -*-
"""Hoi quy an toan cho src/dich_vu.py: ep kieu bien vao, duong may xa, xac thuc HTTP."""
import types

from src import dich_vu


# ------------------------------------------------------------ ep kieu bien vao (muc 4)
def test_ho_so_ep_kieu_thong_tin_benh_nhan_o_bien_vao(monkeypatch):
    da_nhan = {}

    def ho_so_tho(than):
        da_nhan["than"] = than
        return {"id": "ca", "nhanh": "C_khoa", "nguon": "bo_dem", "phat_bieu": []}

    def them_canh_bao(r, thong_tin_benh_nhan=None, du_lieu_xet_nghiem=None):
        da_nhan["tt"], da_nhan["xn"] = thong_tin_benh_nhan, du_lieu_xet_nghiem
        return r

    monkeypatch.setattr(dich_vu, "_them_canh_bao", them_canh_bao)
    monkeypatch.setattr(dich_vu, "lay_worm_logger", lambda: types.SimpleNamespace(
        append_event=lambda **k: {"seq": 1, "curr_hash": "h"}))
    gia = types.SimpleNamespace(_ho_so_tho=ho_so_tho, headers={})
    than = {"input": "x", "thong_tin_benh_nhan": {"tuoi": "82", "egfr": "rac", "tuan_thai": "10"},
            "du_lieu_xet_nghiem": {"egfr": "25", "creatinine_unit": "mg/dL"}}
    dich_vu.May._ho_so(gia, than)
    assert da_nhan["than"]["thong_tin_benh_nhan"] == {"tuoi": 82, "tuan_thai": 10}
    assert da_nhan["tt"] == {"tuoi": 82, "tuan_thai": 10}
    assert da_nhan["xn"] == {"egfr": 25.0, "creatinine_unit": "mg/dL"}
