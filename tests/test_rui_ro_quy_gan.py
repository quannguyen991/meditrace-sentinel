# -*- coding: utf-8 -*-
"""Test cho tang cham rui ro quy gan."""
from src import rui_ro_quy_gan as rr
from src.phat_bieu import PhatBieu

LUOT = [
    (1, "Bác sĩ", "Cháu có tiền sử dị ứng thuốc gì không ạ?"),
    (2, "Người nhà", "Tôi thì dị ứng penicillin, còn cháu chưa thấy bị bao giờ."),
    (3, "Bệnh nhân", "Con đau bụng ạ."),
]
NC = rr.NguCanh.tu_hoi_thoai(LUOT)


def pb(chu_the_id=0, bang_chung=(1, 2), chac="chắc chắn", noi_dung="dị ứng"):
    return PhatBieu(id=0, nguoi_noi="người nhà", chu_the_id=chu_the_id,
                    noi_dung=noi_dung, bang_chung=list(bang_chung),
                    do_chac_chan=chac)


# --------------------------------------------------------------- ngu canh

def test_dem_dung_so_nguoi_ke_khong_tinh_bac_si():
    assert NC.so_nguoi_ke == 2       # người nhà + bệnh nhân


def test_hoi_thoai_hai_ben_chi_co_mot_nguoi_ke():
    nc = rr.NguCanh.tu_hoi_thoai([(1, "Bác sĩ", "Chị thấy sao?"),
                                  (2, "Bệnh nhân", "Tôi đau đầu.")])
    assert nc.so_nguoi_ke == 1


# ------------------------------------------------------------- dau hieu

def test_bat_duoc_chu_the_KHONG_doc_duoc_tu_noi_dung():
    """Dau hieu manh nhat. Luot 3 khong co tu nao goi ten nguoi nha, nen mot
    phat bieu gan cho nguoi nha tu luot do la suy tu nhan vai."""
    d = rr.dac_trung(pb(chu_the_id=1, bang_chung=(3,)), NC)
    assert d["chủ thể suy từ người nói"] is True


def test_KHONG_bao_dong_khi_noi_dung_co_goi_ten_chu_the():
    """Luot 2 co chu 'cháu' — chu the benh nhan doc duoc thang tu noi dung."""
    d = rr.dac_trung(pb(chu_the_id=0, bang_chung=(1, 2)), NC)
    assert d["chủ thể suy từ người nói"] is False


def test_bang_chung_mot_luot_bi_danh_dau():
    assert rr.dac_trung(pb(bang_chung=(2,)), NC)["bằng chứng một lượt"] is True
    assert rr.dac_trung(pb(bang_chung=(1, 2)), NC)["bằng chứng một lượt"] is False


def test_khong_chac_chan_bi_danh_dau():
    assert rr.dac_trung(pb(chac="chưa ghi nhận"), NC)["không chắc chắn"] is True


# ---------------------------------------------------------------- diem

def test_diem_nam_trong_khoang_0_1():
    for p in (pb(), pb(chu_the_id=1, bang_chung=(3,), chac="nghi ngờ")):
        assert 0.0 <= rr.diem_rui_ro(p, NC) <= 1.0


def test_phat_bieu_cang_nhieu_dau_hieu_diem_cang_cao():
    it = pb(chu_the_id=0, bang_chung=(1, 2))
    nhieu = pb(chu_the_id=1, bang_chung=(3,), chac="nghi ngờ")
    assert rr.diem_rui_ro(nhieu, NC) > rr.diem_rui_ro(it, NC)


# -------------------------------------------------------------- sang loc

def test_sang_loc_danh_dau_chu_khong_XOA_phat_bieu():
    """Xoa la bo sot am tham. Danh dau thi no van con, chi doi cho sang muc
    can xac nhan — va van dem duoc."""
    ds = [pb(chu_the_id=1, bang_chung=(3,), chac="nghi ngờ"), pb()]
    ra = rr.sang_loc(ds, 0.5, NC)
    assert len(ra) == len(ds)
    assert ra[0].trang_thai == "chưa giải quyết"


def test_nguong_qua_1_thi_khong_danh_dau_gi():
    """Moc doi chung cua duong danh doi. Thieu no thi khong biet duong bat dau
    tu dau."""
    ds = [pb(chu_the_id=1, bang_chung=(3,), chac="nghi ngờ")]
    assert rr.sang_loc(ds, 1.01, NC)[0].trang_thai == "còn hiệu lực"


def test_nguong_bang_0_thi_danh_dau_het():
    ds = [pb(), pb(chu_the_id=1, bang_chung=(3,))]
    assert all(p.trang_thai == "chưa giải quyết" for p in rr.sang_loc(ds, 0.0, NC))


def test_sang_loc_khong_sua_ban_goc():
    ds = [pb(chu_the_id=1, bang_chung=(3,), chac="nghi ngờ")]
    rr.sang_loc(ds, 0.0, NC)
    assert ds[0].trang_thai == "còn hiệu lực"


def test_so_phat_bieu_bi_danh_dau_GIAM_don_dieu_khi_nguong_tang():
    """Tinh chat bat buoc cua mot nut van: van cang chat thi cang it bi danh
    dau. Hong tinh chat nay thi duong danh doi khong con y nghia."""
    ds = [pb(), pb(chu_the_id=1, bang_chung=(3,)), pb(chac="nghi ngờ"),
          pb(chu_the_id=1, bang_chung=(3,), chac="nghi ngờ")]
    truoc = None
    for nguong in (0.0, 0.25, 0.5, 0.75, 1.0, 1.01):
        n = sum(1 for p in rr.sang_loc(ds, nguong, NC)
                if p.trang_thai == "chưa giải quyết")
        if truoc is not None:
            assert n <= truoc, f"nguong {nguong} danh dau nhieu hon nguong truoc"
        truoc = n
