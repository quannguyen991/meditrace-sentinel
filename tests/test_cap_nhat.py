# -*- coding: utf-8 -*-
import pytest

from src import cap_nhat
from src.phat_bieu import PhatBieu

ME, TRE = 1, 2


def pb(id, noi_dung, **kw):
    kw.setdefault("nguoi_noi", "người nhà")
    kw.setdefault("chu_the_id", TRE)
    kw.setdefault("bang_chung", [id])
    return PhatBieu(id=id, noi_dung=noi_dung, **kw)


# ------------------------------------------------------------ luoc do hop le

def test_do_chac_chan_la_tap_dong():
    with pytest.raises(ValueError):
        pb(1, "sốt", do_chac_chan="không đủ căn cứ")


def test_tinh_huong_la_tap_dong():
    with pytest.raises(ValueError):
        pb(1, "sốt", tinh_huong="có thể")


def test_bang_chung_khong_duoc_rong():
    """Moi phat bieu phai truy vet duoc ve mot luot thoai co that."""
    with pytest.raises(ValueError):
        PhatBieu(id=1, nguoi_noi="người nhà", chu_the_id=TRE,
                 noi_dung="sốt", bang_chung=[])


def test_quan_he_phai_kem_id_lien_quan():
    with pytest.raises(ValueError):
        pb(2, "sốt 2 ngày", quan_he="đính chính")


def test_bang_chung_nhieu_luot():
    """Cap "Anh co di ung thuoc khong?" / "Co." can ca hai luot."""
    p = pb(1, "dị ứng thuốc", bang_chung=[7, 8])
    assert len(p.bang_chung) == 2


# ------------------------------------------------------------- luat cap nhat

def test_bo_sung_giu_ca_hai():
    ds = cap_nhat.ap_luat([pb(1, "sốt"), pb(2, "sốt cao", quan_he="bổ sung", quan_he_voi=1)])
    assert all(p.trang_thai == "còn hiệu lực" for p in ds)


def test_dinh_chinh_thay_the_ban_cu():
    ds = cap_nhat.ap_luat([
        pb(1, "sốt", moc_thoi_gian="3 ngày"),
        pb(2, "sốt", moc_thoi_gian="2 ngày", quan_he="đính chính", quan_he_voi=1),
    ])
    assert ds[0].trang_thai == "bị thay thế"
    assert ds[1].trang_thai == "còn hiệu lực"
    assert len(cap_nhat.con_hieu_luc(ds)) == 1


def test_dinh_chinh_KHONG_XOA_ban_cu():
    """Giu ban cu de truy lai duoc rang da co dinh chinh."""
    ds = cap_nhat.ap_luat([
        pb(1, "sốt", moc_thoi_gian="3 ngày"),
        pb(2, "sốt", moc_thoi_gian="2 ngày", quan_he="đính chính", quan_he_voi=1),
    ])
    assert len(ds) == 2
    assert cap_nhat.da_bi_thay_the(ds)[0].moc_thoi_gian == "3 ngày"


def test_dien_bien_GIU_CA_HAI():
    """Loi de mac nhat: coi dien bien la dinh chinh roi vut mat cau dau.

    "Hom qua dau, hom nay het dau" — ca hai deu dung.
    """
    ds = cap_nhat.ap_luat([
        pb(1, "đau", moc_thoi_gian="hôm qua"),
        pb(2, "hết đau", moc_thoi_gian="hôm nay", quan_he="diễn biến", quan_he_voi=1),
    ])
    assert all(p.trang_thai == "còn hiệu lực" for p in ds)
    assert len(cap_nhat.con_hieu_luc(ds)) == 2


def test_mau_thuan_khong_tu_chon_ben_nao():
    ds = cap_nhat.ap_luat([
        pb(1, "sốt", moc_thoi_gian="2 ngày"),
        pb(2, "sốt", moc_thoi_gian="4 ngày", quan_he="mâu thuẫn", quan_he_voi=1),
    ])
    assert all(p.trang_thai == "chưa giải quyết" for p in ds)
    assert not cap_nhat.con_hieu_luc(ds)
    assert len(cap_nhat.can_xac_nhan(ds)) == 2


def test_tham_chieu_hong_thi_gan_co_chu_khong_doan():
    ds = cap_nhat.ap_luat([pb(2, "sốt", quan_he="đính chính", quan_he_voi=99)])
    assert ds[0].trang_thai == "chưa giải quyết"


def test_ap_luat_khong_sua_ban_goc():
    goc = [pb(1, "sốt"), pb(2, "sốt", quan_he="đính chính", quan_he_voi=1)]
    cap_nhat.ap_luat(goc)
    assert goc[0].trang_thai == "còn hiệu lực", "ap_luat khong duoc sua danh sach goc"


# ---------------------------------------------------- gia dinh va ke hoach

def test_gia_dinh_khong_vao_benh_an():
    p = pb(1, "đau", tinh_huong="giả định")
    assert p.du_dieu_kien_vao_benh_an() is False
    assert p in cap_nhat.can_xac_nhan([p])


def test_ke_hoach_khong_vao_benh_su():
    p = pb(1, "kê amoxicillin", tinh_huong="kế hoạch")
    assert p.du_dieu_kien_vao_benh_an() is False


def test_thuc_te_con_hieu_luc_thi_vao_benh_an():
    assert pb(1, "sốt").du_dieu_kien_vao_benh_an() is True


# --------------------------------------------------------- doi chung don gian

def test_doi_chung_ghi_de_xu_ly_dung_dinh_chinh():
    ds = cap_nhat.ghi_de_phat_bieu_truoc([
        pb(1, "sốt", moc_thoi_gian="3 ngày"),
        pb(2, "sốt", moc_thoi_gian="2 ngày"),
    ])
    assert len(cap_nhat.con_hieu_luc(ds)) == 1


def test_doi_chung_ghi_de_LAM_HONG_dien_bien():
    """Cho thay quy tac don gian khong du: no vut mat cau dau cua dien bien.

    Day chinh la ly do can co quan he `dien_bien` rieng.
    """
    ds = cap_nhat.ghi_de_phat_bieu_truoc([
        pb(1, "đau", moc_thoi_gian="hôm qua"),
        pb(2, "đau", moc_thoi_gian="hôm nay"),
    ])
    assert len(cap_nhat.con_hieu_luc(ds)) == 1, "quy tac ghi de vut mat moc hom qua"
