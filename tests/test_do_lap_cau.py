# -*- coding: utf-8 -*-
import unicodedata
from pathlib import Path

import pytest

from src.do_luong import do_lap_cau as dl
from src.he_thong import duong_dan as duong_dan


def _ca(*dong):
    return {"input": "\n".join(dong)}


def test_tach_cau_bo_tien_to_nguoi_noi_va_hoa_thuong():
    assert dl.tach_cau("Bác sĩ: Chị kể tôi nghe ạ.\nBệnh nhân:   Dạ,  ho ba ngày.") == [
        "chị kể tôi nghe ạ.", "dạ, ho ba ngày."]


def test_ty_le_lap_tay():
    # 6 cau, 3 cau duy nhat -> lap 0,5
    ca = [_ca("Bác sĩ: a b.", "Bệnh nhân: c d."),
          _ca("Bác sĩ: a b.", "Bệnh nhân: c d."),
          _ca("Bác sĩ: a b.", "Bệnh nhân: e f.")]
    r = dl.do_lap_cau(ca)
    assert r["so_cau"] == 6 and r["so_cau_duy_nhat"] == 3
    assert r["ty_le_lap"] == 0.5
    assert r["top_lap"][0] == ("a b.", 3)


def test_nfc_nfd_la_mot_cau():
    nfc = unicodedata.normalize("NFC", "Dạ, không ạ.")
    nfd = unicodedata.normalize("NFD", "Dạ, không ạ.")
    assert nfc != nfd
    r = dl.do_lap_cau([_ca("Bệnh nhân: " + nfc), _ca("Bệnh nhân: " + nfd)])
    assert r["so_cau"] == 2 and r["so_cau_duy_nhat"] == 1


def test_doc_jsonl_bo_dong_hong_va_dong_trong(tmp_path):
    p = tmp_path / "a.jsonl"
    p.write_text('{"input": "Bác sĩ: một."}\n\n{hong\n[1, 2]\n{"input": "Bác sĩ: hai."}\n',
                 encoding="utf-8")
    ca, bo = dl.doc_jsonl(str(p))
    assert len(ca) == 2 and bo == 3


def test_ca_khong_co_input_bi_bo_qua():
    r = dl.do_lap_cau([{"khong_co": 1}, _ca("Bác sĩ: xin chào.")])
    assert r["so_ca"] == 1 and r["so_cau"] == 1


def test_rong_khong_chia_cho_0():
    r = dl.do_lap_cau([])
    assert r["ty_le_lap"] == 0.0 and r["ttr"] == 0.0 and r["mtld"] == 0.0
    assert r["distinct2"] == 0.0 and r["top_lap"] == []


def test_do_dai_tu_toi_thieu():
    # 2 cau dai, 2 cau ngan (1 tu)
    ca = [_ca("Bác sĩ: một hai ba bốn.", "Bệnh nhân: có."),
          _ca("Bác sĩ: một hai ba bốn.", "Bệnh nhân: không.")]
    # Do dai >= 4: chi tinh 2 cau "một hai ba bốn" (lap 1/2 = 0.5)
    r = dl.do_lap_cau(ca, do_dai_tu_toi_thieu=4)
    assert r["so_cau"] == 2 and r["so_cau_duy_nhat"] == 1
    assert r["ty_le_lap"] == 0.5


def test_mtld_cao_hon_khi_tu_vung_phong_phu():
    lap = ["a", "b"] * 50
    phong_phu = [f"t{i}" for i in range(100)]
    assert dl.mtld(phong_phu) > dl.mtld(lap)


_BO_CU = Path(duong_dan.THU_MUC_DU_LIEU) / "hoi_thoai_viet_5000.jsonl"


@pytest.mark.skipif(not _BO_CU.exists(), reason="thieu data/hoi_thoai_viet_5000.jsonl")
def test_bo_cu_ty_le_lap_khoang_0_763():
    """Ban ban giao 20/11/2026 ghi 87.265 cau, 20.652 duy nhat, lap 76,3%. Do lai bang
    dinh nghia nay ra 76,9% (87.473 / 20.190): lech 0,6 diem phan tram, trong dung sai 1."""
    ca, _ = dl.doc_jsonl(str(_BO_CU))
    r = dl.do_lap_cau(ca)
    assert abs(r["ty_le_lap"] - 0.763) < 0.01
