# -*- coding: utf-8 -*-
from pathlib import Path

import pytest

from src import nap_vietmed as nv


def _d(text, spk="VietMed_007_a", f="VietMed_007/1.ogg"):
    return {"text": text, "speaker_name": spk, "file": f, "duration": 5.0}


def test_doc_chep_loi_nhay_don(tmp_path):
    p = tmp_path / "t.txt"
    p.write_text("[\n{'text': 'ho ba ngày', 'speaker_name': 'VietMed_007_a', "
                 "'file': 'VietMed_007/1.ogg', 'duration': 5.0},\n]", encoding="utf-8")
    r = nv.doc_chep_loi(p)
    assert len(r) == 1 and r[0]["text"] == "ho ba ngày"


@pytest.mark.parametrize("noi_dung", ["khong phai danh sach", "[1, 2]", "__import__('os')",
                                      "[{'a': 1},"])
def test_tep_hong_nem_ValueError(tmp_path, noi_dung):
    p = tmp_path / "t.txt"
    p.write_text(noi_dung, encoding="utf-8")
    with pytest.raises(ValueError):
        nv.doc_chep_loi(p)


def test_ghep_cung_ban_ghi_thanh_mot_doan_va_giu_nguoi_noi():
    r = nv.ghep_doan([_d("một", "VietMed_007_a"), _d("hai", "VietMed_007_b"), _d("ba")])
    assert len(r) == 1
    assert r[0]["so_dong"] == 3 and r[0]["van_ban"] == "một hai ba"
    assert [x["nguoi_noi"] for x in r[0]["luot"]] == ["VietMed_007_a", "VietMed_007_b", "VietMed_007_a"]


def test_khac_ban_ghi_tach_doan_va_dem_so_thu_tu():
    r = nv.ghep_doan([_d("a"), _d("b", f="VietMed_008/1.ogg"), _d("c")])
    assert [x["id"] for x in r] == ["VietMed_007#1", "VietMed_008#1", "VietMed_007#2"]


def test_cat_khi_qua_dai():
    dong = [_d("x" * 100) for _ in range(10)]
    r = nv.ghep_doan(dong, toi_da_ky_tu=250)
    assert len(r) >= 4
    assert all(len(x["van_ban"]) <= 250 for x in r)
    assert sum(x["so_dong"] for x in r) == 10


def test_dong_don_le_dai_hon_gioi_han_van_duoc_giu():
    r = nv.ghep_doan([_d("y" * 500)], toi_da_ky_tu=100)
    assert len(r) == 1 and r[0]["so_dong"] == 1


def test_bo_dong_rong_va_thieu_text():
    r = nv.ghep_doan([_d("  "), {"speaker_name": "x"}, _d("co chu")])
    assert len(r) == 1 and r[0]["so_dong"] == 1


def test_ma_ghi_am_thieu_file_lay_tu_nguoi_noi():
    assert nv.ma_ghi_am({"speaker_name": "VietMed_009_b"}) == "VietMed_009"


_TRAIN = Path(r"D:\Claude\data-rieng-tu\du-lieu-ngoai\VietMed\labeled_medical_data\train_transcript.txt")


@pytest.mark.skipif(not _TRAIN.exists(), reason="thieu du lieu VietMed tren may nay")
def test_chay_tren_tap_train_that():
    dong = nv.doc_chep_loi(_TRAIN)
    r = nv.ghep_doan(dong)
    assert len(dong) == 2773  # wc -l ra 2775 vi tinh them hai dong "[" va "]"
    assert sum(x["so_dong"] for x in r) == sum(1 for d in dong if str(d.get("text") or "").strip())
