# -*- coding: utf-8 -*-
import importlib.util
import json
from pathlib import Path

_P = Path(__file__).resolve().parent.parent / "tools" / "do_bo_sot_tren_tap.py"
_spec = importlib.util.spec_from_file_location("do_bo_sot_tren_tap", _P)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def _ghi(p, dong):
    p.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in dong), encoding="utf-8")


def test_chi_tinh_tren_ca_co_trong_moi_tep_dem(tmp_path):
    _ghi(tmp_path / "da.jsonl", [
        {"id": "a", "dap_an": [{"noi_dung": "ho ba ngày"}, {"noi_dung": "sốt nhẹ"}]},
        {"id": "b", "dap_an": [{"noi_dung": "đau đầu"}]},
        {"id": "c", "dap_an": [{"noi_dung": "mệt mỏi"}]}])
    _ghi(tmp_path / "x.jsonl", [{"id": "a", "ly_do": "", "phat_bieu": [{"noi_dung": "ho ba ngày"}]},
                                {"id": "b", "ly_do": "", "phat_bieu": [{"noi_dung": "đau đầu"}]}])
    _ghi(tmp_path / "y.jsonl", [{"id": "a", "ly_do": "", "phat_bieu": []}])
    kq = m.do(tmp_path / "da.jsonl", {"X": tmp_path / "x.jsonl", "Y": tmp_path / "y.jsonl"})
    assert kq["so_ca"] == 1  # chi ca "a" co o ca hai tep
    assert kq["ket_qua"]["X"]["so_bo_sot"] == 1 and kq["ket_qua"]["X"]["so_menh_de_dap_an"] == 2
    assert kq["ket_qua"]["Y"]["so_bo_sot"] == 2


def test_dem_ca_json_loi(tmp_path):
    _ghi(tmp_path / "da.jsonl", [{"id": "a", "dap_an": [{"noi_dung": "ho"}]}])
    _ghi(tmp_path / "x.jsonl", [{"id": "a", "ly_do": "thieu truong", "phat_bieu": None}])
    kq = m.do(tmp_path / "da.jsonl", {"X": tmp_path / "x.jsonl"})
    assert kq["ket_qua"]["X"]["so_ca_json_loi"] == 1 and kq["ket_qua"]["X"]["so_bo_sot"] == 1


def test_khoang_tin_cay():
    lo, hi = m.khoang_tin_cay_95(0, 0)
    assert (lo, hi) == (0.0, 0.0)
    lo, hi = m.khoang_tin_cay_95(50, 100)
    assert 0.39 < lo < 0.41 and 0.59 < hi < 0.61
    assert m.khoang_tin_cay_95(0, 100)[0] == 0.0
    assert m.khoang_tin_cay_95(100, 100)[1] > 0.999


def test_in_bang_co_cot_khoang(tmp_path):
    kq = {"so_ca": 2, "ket_qua": {"X": {"so_menh_de_dap_an": 10, "so_bo_sot": 1, "ti_le_bo_sot": 0.1,
                                          "khoang": (0.02, 0.4), "so_ca_json_loi": 0}}}
    s = m.in_bang(kq)
    assert "| X | 10 | 1 | 10.0% | 2.0%–40.0% | 0 |" in s
