# -*- coding: utf-8 -*-
import importlib.util
from pathlib import Path

import pytest

_P = Path(__file__).resolve().parent.parent / "tools" / "run_capped.py"
_spec = importlib.util.spec_from_file_location("run_capped", _P)
run_capped = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run_capped)


def test_mac_dinh_074_va_doi_so_sau_gach_gach_di_nguyen():
    phan, mo_dun, doi = run_capped.tach_doi_so(["--", "--model", "Qwen/Qwen3-4B", "--do-dai", "4096"])
    assert phan == 0.74 and mo_dun == "src.huan_luyen.huan_luyen_sft"
    assert doi == ["--model", "Qwen/Qwen3-4B", "--do-dai", "4096"]


def test_doc_phan_vram():
    phan, _mo_dun, doi = run_capped.tach_doi_so(["--phan-vram", "0.6", "--", "--buoc", "5"])
    assert phan == 0.6 and doi == ["--buoc", "5"]


def test_chon_mo_dun():
    _p, mo_dun, doi = run_capped.tach_doi_so(["--mo-dun", "src.duong_ong.chay_duong_ong", "--", "--nhanh", "B"])
    assert mo_dun == "src.duong_ong.chay_duong_ong" and doi == ["--nhanh", "B"]


@pytest.mark.parametrize("v", ["0", "1.5", "-0.1"])
def test_tu_choi_phan_vram_ngoai_khoang(v):
    with pytest.raises(SystemExit):
        run_capped.tach_doi_so(["--phan-vram", v, "--"])


def test_tu_choi_doi_so_la_truoc_gach_gach():
    with pytest.raises(SystemExit):
        run_capped.tach_doi_so(["--model", "x", "--"])
