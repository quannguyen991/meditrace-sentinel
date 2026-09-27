# -*- coding: utf-8 -*-
from pathlib import Path

from src import duong_dan
import pytest

pytestmark = pytest.mark.skipif(
    not duong_dan.GOC_VAIC.exists(),
    reason="can thu muc du lieu goc 'D:/VAIC DE @' — chi co tren laptop, khong co tren HoaiDuc")


def test_moi_duong_dan_deu_ton_tai():
    for ten in ("GOC_VAIC", "TRAIN_JSONL"):
        p = Path(getattr(duong_dan, ten))
        assert p.exists(), f"{ten} tro toi cho khong ton tai: {p}"


def test_thu_muc_ra_duoc_tao():
    for ten in ("THU_MUC_KET_QUA", "THU_MUC_DU_LIEU", "THU_MUC_MO_HINH"):
        assert Path(getattr(duong_dan, ten)).is_dir(), f"{ten} chua duoc tao"


def test_ho_mo_hinh_deu_la_qwen3():
    for ten in ("MODEL_NHO", "MODEL_GO_LOI", "MODEL_CHINH"):
        assert getattr(duong_dan, ten).startswith("Qwen/Qwen3-")
