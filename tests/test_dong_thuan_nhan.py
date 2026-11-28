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


def test_kappa_suy_bien_tra_none_khong_xac_dinh():
    # Cả hai chỉ dùng một nhãn: mẫu số bằng 0, κ không xác định (rà soát độc lập 28/11)
    assert cohen_kappa(["dung"] * 4, ["dung"] * 4) is None


def test_kappa_do_dai_lech_thi_bao_loi():
    with pytest.raises(ValueError):
        cohen_kappa(["dung"], ["dung", "dung"])


def test_dong_thuan_bao_muc_thieu_moi_ben():
    ra = dong_thuan({"a#1": "dung", "a#2": "bia", "a#4": "sai_nguoi"}, {"a#1": "dung", "a#3": "dung", "a#4": "dung"})
    assert ra["so_muc"] == 2
    assert ra["thieu_o_b"] == ["a#2"] and ra["thieu_o_a"] == ["a#3"]


def test_dong_thuan_khong_co_muc_chung_thi_kappa_none():
    assert dong_thuan({"a#1": "dung"}, {"b#1": "dung"})["kappa"] is None


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


def test_nap_nhan_tu_choi_ma_trung(tmp_path):
    p = tmp_path / "phieu.csv"
    p.write_text("ma_muc,nhan\nx#0,dung\nx#0,bia\n", encoding="utf-8")
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
    assert all(r["muc_may_xep"] for r in p1), "phải có mục bệnh án để gán được nhãn sai_muc"
    assert all("toan_bo_hoi_thoai" in r for r in p1)
    assert set(NHAN_HOP_LE) >= {"dung", "sai_nguoi", "sai_noi_dung", "bia", "sai_muc"}
