# -*- coding: utf-8 -*-
"""Du lieu do GPT sinh CHI DE DO: moi duong huan luyen phai chan no."""
from pathlib import Path

import pytest

from src import du_lieu

GOC = Path(__file__).resolve().parents[1]


def test_chan_tep_co_chu_gpt_ke_ca_tep_val():
    with pytest.raises(SystemExit):
        du_lieu.chan_du_lieu_gpt(["viet_train.jsonl", "gpt500_phuong_ngu.jsonl"])
    with pytest.raises(SystemExit):
        du_lieu.chan_du_lieu_gpt("data/GPT500.jsonl")


def test_khong_chan_tep_cua_de_tai():
    du_lieu.chan_du_lieu_gpt(["viet_train.jsonl", "viet_phat_trien.jsonl", None])


def test_train_baseline_GOI_chot_chan():
    """Chot khong ai goi la chot chet — dung ho loi `chan_tap_khoa` (11/09/2026)."""
    van = (GOC / "src" / "train_baseline.py").read_text(encoding="utf-8")
    assert "chan_du_lieu_gpt(" in van


def test_ten_tep_chuyen_doi_MANG_chu_gpt():
    from src import bo_gpt500
    assert du_lieu.DAU_DU_LIEU_GPT in bo_gpt500.TEP_RA.name.lower()
    assert du_lieu.DAU_DU_LIEU_GPT in bo_gpt500.TEN_TAP.lower()
