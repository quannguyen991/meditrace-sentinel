# -*- coding: utf-8 -*-
"""Test cho buoc cham lai cac nhanh bang diem quy gan."""
from src import cham_lai_bang_quy_gan as cl

THAM_CHIEU = "TIỀN SỬ GIA ĐÌNH\n\nMẹ dị ứng penicillin.\n\nDỊ ỨNG\n\nTrẻ chưa ghi nhận dị ứng."


def mau(du_doan, khong_muc_phu=None):
    m = {"id": "x", "tham_chieu": THAM_CHIEU, "du_doan": du_doan}
    if khong_muc_phu is not None:
        m["du_doan_khong_muc_phu"] = khong_muc_phu
    return m


def test_cham_tra_ve_ca_hai_bo_chi_so():
    """Bao cao phai co ca thuoc do moi lan diem cuoc thi — bo diem cuoc thi di
    la mat kha nang doi chieu voi ket qua Cua 4 cu."""
    d = cl.cham([mau(THAM_CHIEU)])
    assert d["f1_quy_gan"] == 1.0
    assert "final_cuoc_thi" in d and "section_f1" in d


def test_ban_hoan_doi_chu_the_bi_tru_diem_quy_gan():
    hoan_doi = THAM_CHIEU.replace("Mẹ dị ứng", "Trẻ dị ứng").replace(
        "Trẻ chưa ghi nhận", "Mẹ chưa ghi nhận")
    d = cl.cham([mau(hoan_doi)])
    assert d["f1_quy_gan"] < 0.5
    assert d["so_sai_chu_the"] == 2


def test_trung_binh_tren_nhieu_mau():
    d = cl.cham([mau(THAM_CHIEU), mau("")])
    assert 0.0 < d["f1_quy_gan"] < 1.0


def test_dung_ban_khong_muc_phu_khi_duoc_yeu_cau():
    """Muc CAN XAC NHAN khong co trong ban tham chieu. Hai cach doc phai ra hai
    con so khac nhau, khong duoc am tham dung mot ban cho ca hai."""
    co_muc_phu = THAM_CHIEU + "\n\nCẦN XÁC NHẬN\n\nTrẻ có thể sốt cao về đêm."
    ds = [mau(co_muc_phu, khong_muc_phu=THAM_CHIEU)]
    assert cl.cham(ds, dung_ban_khong_muc_phu=True)["so_thua"] < \
        cl.cham(ds, dung_ban_khong_muc_phu=False)["so_thua"]


def test_thieu_ban_khong_muc_phu_thi_lui_ve_ban_thuong():
    """Nhanh A khong co truong do. Phai lui ve `du_doan` chu khong duoc cham
    tren chuoi rong roi bao diem 0 — do la mot so 0 gia."""
    d = cl.cham([mau(THAM_CHIEU)], dung_ban_khong_muc_phu=True)
    assert d["f1_quy_gan"] == 1.0


def test_tap_rong_khong_lam_vo_phep_tinh():
    assert cl.cham([]) == {}
