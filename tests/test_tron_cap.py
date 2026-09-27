# -*- coding: utf-8 -*-
"""Test tron cap cham mu.

Cai phai giu: phieu KHONG duoc lo nhanh nao la nhanh nao. Mot phep cham mu
bi lo thi te hon khong cham, vi no cho ket qua trong nhu co can cu.
"""
from src import tron_cap


def kq(ma, van):
    return {"id": ma, "input": f"hội thoại {ma}", "du_doan": van}


A = [kq(f"m{i}", f"BẢN CỦA A số {i}") for i in range(20)]
C = [kq(f"m{i}", f"BẢN CỦA C số {i}") for i in range(20)]


# ------------------------------------------------------------ khong lo nhanh

def test_phieu_khong_chua_ten_nhanh():
    phieu, _, _ = tron_cap.tron(A, C, "A", "C")
    van = tron_cap.in_phieu(phieu)
    for tu in ("nhánh A", "nhánh C", "nhanh A", "nhanh C", "ra_A_", "ra_C_"):
        assert tu not in van, f"phieu lo nguon goc: {tu!r}"


def test_khong_phai_nhanh_nao_cung_luon_o_ben_trai():
    """Neu mot nhanh luon la "ban A" thi bac si hoc duoc quy luat sau vai cap."""
    phieu, khoa, _ = tron_cap.tron(A, C, "A", "C")
    ben_trai = [k["ban_A"] for k in khoa]
    assert "A" in ben_trai and "C" in ben_trai
    # khong lech qua 80/20 tren 20 cap
    ty_le = ben_trai.count("A") / len(ben_trai)
    assert 0.2 <= ty_le <= 0.8, f"lech {ty_le:.0%}"


def test_moi_cap_co_dong_xu_RIENG_chu_khong_dung_chung_mot_lan_lat():
    phieu, khoa, _ = tron_cap.tron(A, C, "A", "C")
    assert len({k["ban_A"] for k in khoa}) == 2


# ----------------------------------------------------------------- tai lap

def test_cung_seed_ra_cung_nhan():
    _, k1, _ = tron_cap.tron(A, C, "A", "C", seed=7)
    _, k2, _ = tron_cap.tron(A, C, "A", "C", seed=7)
    assert k1 == k2


def test_doi_seed_thi_doi_nhan():
    _, k1, _ = tron_cap.tron(A, C, "A", "C", seed=7)
    _, k2, _ = tron_cap.tron(A, C, "A", "C", seed=8)
    assert k1 != k2


def test_them_mau_khong_lam_doi_nhan_cua_mau_cu():
    """Dung bam theo ma mau chu khong phai mot chuoi ngau nhien tuan tu:
    them bot mau khong duoc lam xao tron ket qua da cham."""
    _, k_it, _ = tron_cap.tron(A[:5], C[:5], "A", "C")
    _, k_nhieu, _ = tron_cap.tron(A, C, "A", "C")
    theo_ma = {k["ma"]: k for k in k_nhieu}
    for k in k_it:
        assert theo_ma[k["ma"]] == k


# ------------------------------------------------------------ cap trung nhau

def test_hai_ban_giong_het_nhau_thi_LOAI_va_bao_cao():
    """Cap do khong do duoc gi. Bo am tham thi so cap trong bao cao sai."""
    giong = [kq("m0", "GIỐNG NHAU"), kq("m1", "khác 1")]
    giong2 = [kq("m0", "GIỐNG NHAU"), kq("m1", "khác 2")]
    phieu, khoa, trung = tron_cap.tron(giong, giong2, "A", "C")
    assert trung == ["m0"]
    assert len(phieu) == 1 and phieu[0]["ma"] == "m1"


def test_mau_chi_co_o_mot_nhanh_thi_bo_qua():
    phieu, _, _ = tron_cap.tron(A, C[:3], "A", "C")
    assert len(phieu) == 3


# ------------------------------------------------------------------ giai ma

def test_giai_ma_dem_dung_ve_dung_nhanh():
    phieu, khoa, _ = tron_cap.tron(A, C, "A", "C")
    # tra loi: luon chon ban nao chua chu "C"
    tra_loi = []
    for p in phieu:
        chon = "A" if "CỦA C" in p["ban_A"] else "B"
        tra_loi.append({"ma": p["ma"], "cau": tron_cap.CAU_HOI[0], "chon": chon})
    dem = tron_cap.giai_ma(khoa, tra_loi)
    assert dem[tron_cap.CAU_HOI[0]]["C"] == len(phieu)
    assert dem[tron_cap.CAU_HOI[0]].get("A", 0) == 0


def test_giai_ma_dem_rieng_lua_chon_nhu_nhau():
    phieu, khoa, _ = tron_cap.tron(A[:4], C[:4], "A", "C")
    tra_loi = [{"ma": p["ma"], "cau": tron_cap.CAU_HOI[1], "chon": "nhu nhau"}
               for p in phieu]
    dem = tron_cap.giai_ma(khoa, tra_loi)
    assert dem[tron_cap.CAU_HOI[1]]["nhu nhau"] == 4


def test_giai_ma_bo_qua_ma_khong_co_trong_khoa():
    _, khoa, _ = tron_cap.tron(A[:2], C[:2], "A", "C")
    dem = tron_cap.giai_ma(khoa, [{"ma": "khong-ton-tai", "cau": "x", "chon": "A"}])
    assert dem == {}, "ma la khong duoc tao ra mot o cau hoi trong bang dem"


# -------------------------------------------------------------------- phieu

def test_phieu_co_du_ba_cau_hoi_moi_cap():
    phieu, _, _ = tron_cap.tron(A[:2], C[:2], "A", "C")
    van = tron_cap.in_phieu(phieu)
    for c in tron_cap.CAU_HOI:
        assert van.count(c) == 2


def test_phieu_co_o_nhu_nhau():
    """Ep chon mot trong hai khi ca hai cung sai la ep ra du lieu rac."""
    phieu, _, _ = tron_cap.tron(A[:1], C[:1], "A", "C")
    assert "như nhau" in tron_cap.in_phieu(phieu)


def test_phieu_co_hoi_thoai_goc():
    """Khong co hoi thoai thi bac si khong kiem duoc ban nao dung."""
    phieu, _, _ = tron_cap.tron(A[:1], C[:1], "A", "C")
    assert "hội thoại m0" in tron_cap.in_phieu(phieu)
