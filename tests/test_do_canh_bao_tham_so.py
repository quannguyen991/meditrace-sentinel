# -*- coding: utf-8 -*-
"""do_canh_bao.chay nhan thu muc va nhanh, tu tim cac tap co tep dau ra tuong ung."""
import json
from pathlib import Path

import pytest

from src import do_canh_bao

GOC = Path(__file__).resolve().parents[1] / "data" / "thach_thuc"
TAP = "thach_thuc_dinh_chinh_phat_trien"


@pytest.mark.skipif(not (GOC / f"{TAP}.jsonl").exists(), reason="thieu data/thach_thuc")
def test_chay_tren_thu_muc_tam(tmp_path):
    ra_dong = (GOC / f"ra_C_khoa_{TAP}.jsonl").read_text(encoding="utf-8").splitlines()[0]
    r = json.loads(ra_dong)
    ca = next(json.loads(d) for d in (GOC / f"{TAP}.jsonl").read_text(encoding="utf-8").splitlines()
              if d.strip() and json.loads(d)["id"] == r["id"])
    (tmp_path / f"{TAP}.jsonl").write_text(json.dumps(ca, ensure_ascii=False) + "\n", encoding="utf-8")
    (tmp_path / f"ra_C_khoa_{TAP}.jsonl").write_text(ra_dong + "\n", encoding="utf-8")
    con_hieu_luc = sum(1 for p in r["phat_bieu"] if p.get("trang_thai") != "bị thay thế")

    kq, _ = do_canh_bao.chay(tmp_path, "C_khoa")

    assert kq["so_menh_de"] == con_hieu_luc > 0
    assert set(kq["chinh_sach"]) == {"C", "D"}
    assert kq["cac_tap"] == [TAP]


def test_thu_muc_khong_co_tap_bao_loi(tmp_path):
    with pytest.raises(FileNotFoundError):
        do_canh_bao.chay(tmp_path, "C_khoa")
