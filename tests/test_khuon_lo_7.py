# -*- coding: utf-8 -*-
"""Kiểm thử chuyên biệt cho src/bo_du_lieu/khuon_lo_7.py (Lô 7: 50 khuôn bệnh, candidate 501-550)."""
import json
import unicodedata
import pytest

from src.bo_du_lieu.khuon_lo_7 import BENH_LO_7, GIOI_TINH_LO_7
from src.bo_du_lieu.khuon_mo_rong import DANH_SACH_UNG_VIEN_CON_LAI, BENH_MO_RONG
from src.bo_du_lieu import ngu_lieu_viet as nl
from src.bo_du_lieu import kiem_khuon as kk


def test_lo_7_so_luong_va_khop_ung_vien():
    """Kiểm tra Lô 7 đủ 50 khuôn và khớp 100% DANH_SACH_UNG_VIEN_CON_LAI[200:250]."""
    assert len(BENH_LO_7) == 50
    candidates = DANH_SACH_UNG_VIEN_CON_LAI[200:250]
    for b, c in zip(BENH_LO_7, candidates):
        assert b["ten"] == c[0]
        assert b["nhom"] == c[1]
        assert b["dien_tien"] == c[2]
        assert b["he_co_quan"] == c[3]
        assert b["da_duyet"] is False


def test_lo_7_tuyet_doi_khong_chua_om():
    """Kiểm tra tuyệt đối không chứa chuỗi con 'ốm' trong bất kỳ trường nào."""
    for b in BENH_LO_7:
        text = unicodedata.normalize("NFC", json.dumps(b, ensure_ascii=False).lower())
        assert "ốm" not in text, f"Khuôn '{b['ten']}' chứa chuỗi con 'ốm'!"


def test_lo_7_du_truong_va_bien_the_6():
    """Kiểm tra đủ các trường bắt buộc và mỗi biến thể có 6 lựa chọn không trùng."""
    for b in BENH_LO_7:
        assert len(b["chinh"]) >= 3
        assert len(b["phu"]) >= 3
        for f_var, f_main in [
            ("bien_the_kham", "kham"),
            ("bien_the_chan_doan", "chan_doan"),
            ("bien_the_ke_hoach", "ke_hoach")
        ]:
            assert f_var in b
            var_list = b[f_var]
            assert isinstance(var_list, list) and len(var_list) == 6
            assert len(set(var_list)) == 6, f"Khuôn '{b['ten']}' có biến thể '{f_var}' trùng lặp!"
            assert b[f_main] == var_list[0]


def test_lo_7_kiem_tat_ca_va_gioi_tinh():
    """Kiểm tra chạy kiem_tat_ca trên Lô 7 không có lỗi LOI và không trùng >= 20%."""
    chi_nu = {k for k, v in GIOI_TINH_LO_7.items() if v == "nữ"}
    chi_nam = {k for k, v in GIOI_TINH_LO_7.items() if v == "nam"}

    ket = kk.kiem_tat_ca(
        BENH_LO_7,
        chi_nu=chi_nu,
        chi_nam=chi_nam,
        nhan_gioi=GIOI_TINH_LO_7,
        nguong_trung=0.20
    )
    loi = [v for v in ket.van_de if v.muc == "LOI"]
    assert not loi, f"Lô 7 có lỗi kiem_khuon: {loi}"
    assert len(ket.cap_trung) == 0, f"Lô 7 có cặp trùng lặp nội bộ >= 20%: {ket.cap_trung}"


def test_lo_7_khong_trung_lap_cheo_300_khuon_hien_co():
    """Kiểm tra 50 khuôn Lô 7 không có cặp trùng >= 20% với 300 khuôn hiện có (200 gốc + 100 mở rộng)."""
    goc = getattr(nl, "BENH_GOC", nl.BENH[:200])
    hien_co = [b for b in goc + BENH_MO_RONG if b["ten"] not in {x["ten"] for x in BENH_LO_7}]
    tu_hien_co = {kk._chuan(b["ten"]): kk._tu_khoa([*b.get("chinh", []), *b.get("phu", [])]) for b in hien_co}
    tu_lo_7 = {kk._chuan(b["ten"]): kk._tu_khoa([*b.get("chinh", []), *b.get("phu", [])]) for b in BENH_LO_7}

    cap_trung = []
    for t7, tok7 in tu_lo_7.items():
        for t_cu, tok_cu in tu_hien_co.items():
            j = kk._jaccard(tok7, tok_cu)
            if j >= 0.20:
                cap_trung.append((t7, t_cu, round(j, 3)))

    assert not cap_trung, f"Có cặp trùng lặp chéo >= 20%: {cap_trung}"
