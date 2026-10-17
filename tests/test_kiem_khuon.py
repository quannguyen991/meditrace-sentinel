# -*- coding: utf-8 -*-
"""Test bo kiem khuon benh (src/kiem_khuon.py). Moi luat co mot ca loi co y."""
from src import kiem_khuon as kk
from src import ngu_lieu_viet as nl


def _khuon(**sua):
    b = dict(
        ten="viêm họng cấp", nhom="cả hai", dien_tien="cấp",
        chinh=["đau họng", "sốt nhẹ", "ho"],
        phu=["khàn tiếng", "nuốt vướng", "mệt mỏi"],
        kham="Họng đỏ, amidan sưng nhẹ.",
        chan_doan="Viêm họng cấp.",
        ke_hoach="Súc họng nước muối.",
    )
    b.update(sua)
    return b


def _muc(ds, muc):
    return [v for v in ds if v.muc == muc]


def test_khuon_dat_chuan_khong_loi():
    assert kk.kiem_mot(_khuon(), set(), set(), {}) == [] or all(
        v.muc == "INFO" for v in kk.kiem_mot(_khuon(), set(), set(), {})
    )


def test_thieu_truong_la_loi():
    b = _khuon()
    del b["kham"]
    assert _muc(kk.kiem_mot(b, set(), set(), {}), "LOI")


def test_nhom_va_dien_tien_sai_la_loi():
    ds = kk.kiem_mot(_khuon(nhom="trẻ sơ sinh", dien_tien="vừa"), set(), set(), {})
    assert len(_muc(ds, "LOI")) == 2


def test_chan_doan_khong_nhac_ten_benh_la_loi():
    ds = kk.kiem_mot(_khuon(chan_doan="Cần theo dõi thêm."), set(), set(), {})
    assert _muc(ds, "LOI")


def test_chan_doan_lech_dien_tien_la_canh():
    ds = kk.kiem_mot(_khuon(dien_tien="mạn", chan_doan="Viêm họng cấp."), set(), set(), {})
    assert _muc(ds, "CANH")


def test_nhan_gioi_mau_thuan_noi_dung_la_loi():
    b = _khuon(ten="u xơ tử cung", chan_doan="U xơ tử cung.", chinh=["đau bụng dưới", "ra máu âm đạo", "táo bón"])
    ds = kk.kiem_mot(b, set(), set(), {"u xơ tử cung": "nam"})
    assert _muc(ds, "LOI")


def test_tu_chi_mot_gioi_khong_co_nhan_la_canh_khong_phai_loi():
    b = _khuon(ten="u xơ tử cung", chan_doan="U xơ tử cung.", chinh=["đau bụng dưới", "ra máu âm đạo", "táo bón"])
    ds = kk.kiem_mot(b, set(), set(), {})
    assert not _muc(ds, "LOI")
    assert _muc(ds, "CANH")


def test_nhan_gioi_khong_hop_le_la_loi():
    ds = kk.kiem_mot(_khuon(ten="viêm họng cấp"), set(), set(), {"viêm họng cấp": "không rõ"})
    assert _muc(ds, "LOI")


def test_nhom_nguoi_lon_co_tu_tre_em_la_canh():
    b = _khuon(nhom="người lớn", phu=["quấy khóc", "mệt mỏi", "ho"])
    assert _muc(kk.kiem_mot(b, set(), set(), {}), "CANH")


def test_tu_khop_nguyen_khong_bao_gio_bat_nham():
    # "trẻ" nam trong "trẻ tuổi" thi van la tu tre em, nhung "bú" khong duoc khop trong "búp" hay "bụng"
    b = _khuon(nhom="người lớn", kham="Bụng mềm, không đau.")
    assert not _muc(kk.kiem_mot(b, set(), set(), {}), "CANH")


def test_trung_ten_la_loi():
    benh = [_khuon(), _khuon()]
    ket = kk.kiem_tat_ca(benh, set(), set(), {})
    assert any("ten trung" in v.noi_dung for v in _muc(ket.van_de, "LOI"))


def test_trung_trieu_chung_giua_khuon_la_canh():
    a = _khuon(ten="khuon a")
    b = _khuon(ten="khuon b")
    ket = kk.kiem_tat_ca([a, b], set(), set(), {})
    assert ket.cap_trung and ket.cap_trung[0][2] == 1.0
    assert _muc(ket.van_de, "CANH")


def test_nhan_gioi_cho_khuon_khong_ton_tai_la_loi():
    ket = kk.kiem_tat_ca([_khuon()], set(), set(), {"khong co that": "nữ"})
    assert _muc(ket.van_de, "LOI")


def test_danh_sach_gioi_cu_bi_bao_canh():
    ket = kk.kiem_tat_ca([_khuon()], {"ten khong ton tai"}, set(), {})
    assert any("khong khop khuon nao" in v.noi_dung for v in _muc(ket.van_de, "CANH"))


def test_200_khuon_hien_co_khong_co_loi_cau_truc():
    """Bo khuon that phai qua tang cau truc. Canh bao thi duoc, loi thi khong."""
    ket = kk.kiem_tat_ca(nl.BENH, nl.CHI_NU, nl.CHI_NAM, nl.GIOI_THEO_KHUON)
    assert ket.so_khuon == 200
    assert ket.dat, kk.bao_cao(ket)
