# -*- coding: utf-8 -*-
from src.audio.asr.bench_metrics import chuan_hoa_do, sai_tu_khoa, tong_hop, wer


def test_so_doc_bang_chu_va_chu_so_do_bang_nhau():
    assert chuan_hoa_do("năm trăm mi li gam") == chuan_hoa_do("500 mg") == ["500", "mg"]
    assert wer(["Uống năm mươi mi li gam."], ["uống 50 mg"]) == 0


def test_sai_lieu_la_sai_khong_phai_them():
    s = sai_tu_khoa("uống 5 mg", "uống 50 mg")
    assert s["lieu"] == "sai" and s["thuoc"] is None


def test_them_phu_dinh_duoc_dem_rieng():
    assert sai_tu_khoa("có dị ứng", "không dị ứng")["phu_dinh"] == "them"


def test_cap_toi_thieu_truot_khi_mot_cau_sai():
    muc = [{"id": "a", "cap": "p", "van_ban": "ho một ngày"}, {"id": "b", "cap": "p", "van_ban": "ho mười ngày"}]
    r = tong_hop(muc, {"a": "ho một ngày", "b": "ho một ngày"})
    assert r["cap_toi_thieu"] == {"tong": 1, "phan_biet_dung": 0, "truot": ["p"]}
    assert r["theo_loai"]["thoi_gian"]["ty_le_sai"] == 0.5


def test_cap_khong_truot_vi_loi_o_loai_khac():
    muc = [{"id": "a", "cap": "p", "van_ban": "uống metformin 5 mg"},
           {"id": "b", "cap": "p", "van_ban": "uống metformin 50 mg"}]
    r = tong_hop(muc, {"a": "uống mét pho min 5 mg", "b": "uống mét pho min 50 mg"})
    assert r["cap_toi_thieu"]["phan_biet_dung"] == 1
    assert r["theo_loai"]["thuoc"]["ty_le_sai"] == 1.0


def test_cap_phu_dinh_truot_khi_them_chu_khong():
    muc = [{"id": "a", "cap": "p", "van_ban": "có dị ứng"}, {"id": "b", "cap": "p", "van_ban": "không dị ứng"}]
    assert tong_hop(muc, {"a": "không dị ứng", "b": "không dị ứng"})["cap_toi_thieu"]["phan_biet_dung"] == 0


def test_miligram_la_mg():
    assert chuan_hoa_do("bốn trăm miligram") == chuan_hoa_do("400 mg") == chuan_hoa_do("bốn trăm mi li gam")
