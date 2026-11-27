# -*- coding: utf-8 -*-
"""Bộ kiểm thử cho Nhiệm vụ VẤN ĐỀ 2 (Axis 1): Phân chia độc lập & Kiểm nghiệm Ngoài khuôn."""
import pytest

from src.bo_du_lieu import ngu_lieu_viet as nl
from src.bo_du_lieu.chia_tap_theo_khuon import phan_khuon
from src.do_luong.kiem_nghiem_ngoai_khuon import (
    tinh_ma_tran_trung_lap_train_test,
    chay_kiem_nghiem_ngoai_khuon,
    KICH_BAN_NGOAI_KHUON,
)


def test_phan_chia_doc_lap_tuyet_doi():
    """Kiểm tra tính rời rạc tuyệt đối giữa Train, Dev và Test."""
    cac_ten = [b["ten"] for b in nl.BENH]
    phan_tap = phan_khuon(cac_ten)

    train = phan_tap["train"]
    dev = phan_tap["phat_trien"]
    test = phan_tap["kiem_tra_cuoi"]

    # Đảm bảo không có bất kỳ khuôn nào trùng nhau giữa các tập
    assert len(train & test) == 0, f"Trùng Train và Test: {train & test}"
    assert len(train & dev) == 0, f"Trùng Train và Dev: {train & dev}"
    assert len(dev & test) == 0, f"Trùng Dev và Test: {dev & test}"
    assert len(train) + len(dev) + len(test) == len(set(cac_ten))


def test_ma_tran_trung_lap_duoi_20_phan_tram():
    """Kiểm tra ma trận trùng lặp ngữ nghĩa giữa Train và Test bảo đảm < 20%."""
    cac_ten = [b["ten"] for b in nl.BENH]
    phan_tap = phan_khuon(cac_ten)

    thong_ke = tinh_ma_tran_trung_lap_train_test(
        danh_sach_benh=nl.BENH,
        tap_train_ten=phan_tap["train"],
        tap_test_ten=phan_tap["kiem_tra_cuoi"]
    )

    assert thong_ke.hoan_toan_doc_lap is True
    # Jaccard trung bình triệu chứng phải < 0.20 (thực tế ~0.054)
    assert thong_ke.jaccard_trung_binh < 0.20, f"Jaccard trung bình quá cao: {thong_ke.jaccard_trung_binh}"
    # P95 Jaccard phải < 0.20
    assert thong_ke.jaccard_p95 < 0.20, f"P95 Jaccard vượt ngưỡng: {thong_ke.jaccard_p95}"
    # Tỷ lệ các cặp vượt ngưỡng 20% phải rất thấp (< 5%)
    assert thong_ke.ty_le_cap_vuot_20 < 0.05, f"Quá nhiều cặp vượt ngưỡng 20%: {thong_ke.ty_le_cap_vuot_20}"
    # 2-gram và 3-gram overlap phải < 0.20
    assert thong_ke.ngram_2_jaccard < 0.20, f"2-gram overlap vượt ngưỡng: {thong_ke.ngram_2_jaccard}"
    assert thong_ke.ngram_3_jaccard < 0.20, f"3-gram overlap vượt ngưỡng: {thong_ke.ngram_3_jaccard}"


def test_kich_ban_ngoai_khuon_that_su_khong_trung_khuon_goc():
    """Xác nhận 10 kịch bản ngoài khuôn hoàn toàn KHÔNG tồn tại trong danh mục khuôn gốc."""
    ten_khuon_goc = set(b["ten"].strip().lower() for b in nl.BENH)
    for kb in KICH_BAN_NGOAI_KHUON:
        ten_benh = kb["benh"].strip().lower()
        assert ten_benh not in ten_khuon_goc, f"Bệnh {ten_benh} đã tồn tại trong khuôn gốc!"


def test_danh_gia_dinh_luong_oot():
    """Chạy toàn bộ kiểm nghiệm ngoài khuôn và xác minh các chỉ số lâm sàng."""
    ket_qua = chay_kiem_nghiem_ngoai_khuon()

    assert ket_qua.so_kich_ban == 10
    assert ket_qua.tong_so_phat_bieu > 0

    # 1. Tỷ lệ gán đúng chủ thể >= 98% (thực tế 100%)
    assert ket_qua.ty_le_dung_chu_the >= 0.98, (
        f"Tỷ lệ gán đúng chủ thể không đạt: {ket_qua.ty_le_dung_chu_the} "
        f"({ket_qua.dung_chu_the_count}/{ket_qua.tong_so_phat_bieu})"
    )

    # 2. Tỷ lệ CHỐNG GÁN NHẦM tiền sử người nhà cho bệnh nhân: 100% tuyệt đối!
    assert ket_qua.ty_le_chong_gan_nham_nguoi_nha == 1.0, (
        f"Bị gán nhầm tiền sử người nhà cho bệnh nhân! "
        f"Chỉ đạt {ket_qua.chong_gan_nham_count}/{ket_qua.tong_menh_de_nguoi_nha}"
    )

    # 3. Tỷ lệ trích dẫn khớp nguyên văn hai chiều: 100% tuyệt đối!
    assert ket_qua.ty_le_dung_trich_dan == 1.0, (
        f"Trích dẫn không khớp nguyên văn! "
        f"Chỉ đạt {ket_qua.dung_trich_dan_count}/{ket_qua.tong_so_phat_bieu}"
    )

    # 4. Tỷ lệ FSM nhận diện và xử lý đính chính: 100% tuyệt đối!
    assert ket_qua.ty_le_bat_dinh_chinh == 1.0, (
        f"FSM không đính chính được phát biểu cũ! "
        f"Chỉ đạt {ket_qua.bat_dinh_chinh_count}/{ket_qua.tong_so_dinh_chinh}"
    )
