# -*- coding: utf-8 -*-
"""Độ đồng thuận giữa hai người gán nhãn (Cohen κ) và phiếu gán nhãn mù (kế hoạch 27/11, Task 7)."""
import csv

import pytest

from src.do_luong.dong_thuan_nhan import NHAN_HOP_LE, cohen_kappa, dong_thuan, nap_nhan
from tools.phieu_gan_nhan_nguoi import xuat_phieu


def test_kappa_dong_y_hoan_toan_bang_1():
    assert cohen_kappa(["dung", "sai_nguoi", "dung"], ["dung", "sai_nguoi", "dung"]) == pytest.approx(1.0)


def test_kappa_vi_du_biet_truoc():
    # Ví dụ kinh điển: po = 0,7; pe = 0,5 → κ = 0,4
    a = ["c"] * 5 + ["k"] * 5
    b = ["c"] * 4 + ["k"] * 1 + ["c"] * 2 + ["k"] * 3
    assert cohen_kappa(a, b) == pytest.approx(0.4)


def test_kappa_mot_nhan_duy_nhat_khong_chia_cho_0():
    assert cohen_kappa(["dung"] * 4, ["dung"] * 4) == pytest.approx(1.0)


def test_kappa_do_dai_lech_thi_bao_loi():
    with pytest.raises(ValueError):
        cohen_kappa(["dung"], ["dung", "dung"])


def test_dong_thuan_chi_tinh_muc_ca_hai_cung_gan():
    ra = dong_thuan({"a#1": "dung", "a#2": "bia"}, {"a#1": "dung", "a#3": "dung"})
    assert ra["so_muc"] == 1 and ra["kappa"] == pytest.approx(1.0)


def test_nap_nhan_bo_dong_trong_va_bao_nhan_la(tmp_path):
    p = tmp_path / "phieu_A.csv"
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["ma_muc", "nhan"])
        w.writeheader()
        w.writerows([{"ma_muc": "x#0", "nhan": "dung"}, {"ma_muc": "x#1", "nhan": ""}])
    assert nap_nhan(p) == {"x#0": "dung"}
    with open(p, "a", encoding="utf-8", newline="") as f:
        f.write("x#2,lung_tung\n")
    with pytest.raises(ValueError):
        nap_nhan(p)


def test_xuat_phieu_mu_khong_lo_dau_ra_bo_cham_va_on_dinh():
    ca = [{"id": f"c{i}", "input": "Bác sĩ: Ho không?\nBệnh nhân: Ho ba ngày.",
           "phat_bieu": [{"id": 0, "noi_dung": "ho ba ngày", "bang_chung": [2], "trich_dan": ["Ho ba ngày"],
                          "ten_chu_the": "bệnh nhân", "loi": "khong_can_cu"}]} for i in range(60)]
    p1 = xuat_phieu(ca, so_ca=40, seed=2711)
    p2 = xuat_phieu(ca, so_ca=40, seed=2711)
    assert p1 == p2 and len({r["ma_ca"] for r in p1}) == 40
    assert all(r["nhan"] == "" for r in p1)
    assert all("loi" not in r for r in p1), "phiếu phải mù với kết quả bộ chấm"
    assert set(NHAN_HOP_LE) >= {"dung", "sai_nguoi", "sai_noi_dung", "bia", "sai_muc"}
