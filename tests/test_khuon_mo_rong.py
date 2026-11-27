# -*- coding: utf-8 -*-
"""Kiem thu khuon mo rong (Task F1, Axis: 600 Clinical Templates & Organ Diversity)."""
from collections import Counter
import pytest

from src.bo_du_lieu import kiem_khuon as kk
from src.bo_du_lieu import ngu_lieu_viet as nl
from src.bo_du_lieu import khuon_mo_rong as kmr


def test_lo_1_den_lo_8_du_400_khuon():
    for i in range(1, 9):
        assert len(kmr.LO[i]) == 50, f"Lo {i} khong du 50 khuon"
    assert len(kmr.DOT[1]) == 200
    assert len(kmr.DOT[2]) == 200
    assert len(kmr.BENH_MO_RONG) == 400
    assert kmr.DOT[1] == kmr.LO[1] + kmr.LO[2] + kmr.LO[3] + kmr.LO[4]
    assert kmr.DOT[2] == kmr.LO[5] + kmr.LO[6] + kmr.LO[7] + kmr.LO[8]


def test_du_truong_bat_buoc_moi_khuon():
    truong_yeu_cau = ("ten", "nhom", "dien_tien", "chinh", "phu", "kham",
                      "chan_doan", "ke_hoach", "he_co_quan", "da_duyet")
    for b in kmr.BENH_MO_RONG:
        for k in truong_yeu_cau:
            assert k in b, f"Khuon '{b.get('ten')}' thieu truong '{k}'"
            if k != "da_duyet":
                assert b[k], f"Khuon '{b['ten']}' co truong '{k}' rong"
        assert isinstance(b["chinh"], list) and len(b["chinh"]) >= 3
        assert isinstance(b["phu"], list) and len(b["phu"]) >= 3


def test_bien_the_it_nhat_6_cach_mo_ta():
    """Moi khuon mo rong phai co it nhat 6 bien the kham, chan doan, ke hoach."""
    for b in kmr.BENH_MO_RONG:
        for k in ("bien_the_kham", "bien_the_chan_doan", "bien_the_ke_hoach"):
            assert k in b, f"Khuon '{b['ten']}' thieu '{k}'"
            ds = b[k]
            assert isinstance(ds, list), f"'{k}' cua '{b['ten']}' khong phai list"
            assert len(ds) >= 6, f"'{k}' cua '{b['ten']}' chi co {len(ds)} bien the (< 6)"
            assert len(set(ds)) == len(ds), f"'{k}' cua '{b['ten']}' co bien the trung lap"


def test_tat_ca_chua_duyet():
    for b in kmr.BENH_MO_RONG:
        assert b["da_duyet"] is False, f"Khuon '{b['ten']}' da_duyet khong phai False"


def test_ten_khong_trung_nhau_va_khong_trung_200_cu():
    ten_moi = [b["ten"] for b in kmr.BENH_MO_RONG]
    assert len(set(ten_moi)) == len(ten_moi), "Co ten khuon mo rong trung lap"
    goc = set(b["ten"] for b in getattr(nl, "BENH_GOC", nl.BENH[:200]))
    trung = goc & set(ten_moi)
    assert not trung, f"Khuon mo rong trung voi khuon goc: {trung}"


def test_nhi_khoa_it_nhat_15_phan_tram():
    so_nhi = sum(1 for b in kmr.BENH_MO_RONG if b["nhom"] == "nhi")
    ty_le = so_nhi / len(kmr.BENH_MO_RONG)
    assert ty_le >= 0.15, f"Ty le nhi {ty_le:.1%} < 15%"


def test_kiem_khuon_khong_co_loi():
    ket = kk.kiem_tat_ca(
        kmr.BENH_MO_RONG,
        kmr.CHI_NU_MO_RONG,
        kmr.CHI_NAM_MO_RONG,
        kmr.GIOI_THEO_KHUON_MO_RONG
    )
    loi = [v for v in ket.van_de if v.muc == "LOI"]
    assert not loi, f"Co loi trong kiem_khuon: {loi}"
    assert len(ket.cap_trung) == 0, f"Co cap trung lap >= 20%: {ket.cap_trung}"
    assert ket.dat is True


def test_da_dang_he_co_quan_600_khuon():
    """200 khuon goc + 400 khuon moi: it nhat 18 he, khong he nao vuot 12%."""
    hop_nhat = dict(kmr.HE_CO_QUAN_200_CU)
    for b in kmr.BENH_MO_RONG:
        hop_nhat[b["ten"]] = b["he_co_quan"]
    assert len(hop_nhat) == 600
    cnt = Counter(hop_nhat.values())
    assert len(cnt) >= 18, f"So he co quan {len(cnt)} < 18"
    for he, so_luong in cnt.items():
        ty_le = so_luong / len(hop_nhat)
        assert ty_le <= 0.12, f"He '{he}' chiem {ty_le:.2%} > 12% ({so_luong}/600)"


def test_ung_vien_con_lai_khop_300_khuon_lo_3_den_8():
    """300 ung vien con lai khong trung va khop 100% (ten, nhom, dien_tien chuan hoa, he_co_quan)
    voi 300 khuon da hien thuc hoa o Lo 3-8; toan bo 600 khuon co >= 18 he, he lon nhat <= 12%."""
    assert len(kmr.DANH_SACH_UNG_VIEN_CON_LAI) == 300
    ten_ung_vien = [c[0] for c in kmr.DANH_SACH_UNG_VIEN_CON_LAI]
    assert len(set(ten_ung_vien)) == 300, "Co ten ung vien con lai trung lap"

    goc = set(b["ten"] for b in getattr(nl, "BENH_GOC", nl.BENH[:200]))
    assert not (goc & set(ten_ung_vien)), "Ung vien trung voi 200 khuon goc"

    lo_3_8 = []
    for i in range(3, 9):
        lo_3_8.extend(kmr.LO[i])
    assert [b["ten"] for b in lo_3_8] == ten_ung_vien, "Lo 3-8 khong khop thu tu ung vien"
    for b, c in zip(lo_3_8, kmr.DANH_SACH_UNG_VIEN_CON_LAI):
        assert b["nhom"] == c[1] and b["he_co_quan"] == c[3], f"Lech ung vien: {b['ten']}"

    toan_bo = dict(kmr.HE_CO_QUAN_200_CU)
    for b in kmr.BENH_MO_RONG:
        toan_bo[b["ten"]] = b["he_co_quan"]

    assert len(toan_bo) == 600
    cnt = Counter(toan_bo.values())
    assert len(cnt) >= 18
    for he, so_luong in cnt.items():
        ty_le = so_luong / 600
        assert ty_le <= 0.12, f"He '{he}' chiem {ty_le:.2%} > 12% tren 600 khuon ({so_luong}/600)"
