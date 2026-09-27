# -*- coding: utf-8 -*-
"""Test chinh PHEP CHAM, khong test mo hinh.

Neu phep cham sai thi ca phep do sai theo. Moi phep kiem phai chung minh duoc
ca hai chieu: bao DAT khi dung, va bao HONG khi sai. Mot phep kiem khong bao gio
bao sai thi vo dung.
"""
from src import do_bo_chan_doan as dbc
from src import sinh_bo_chan_doan as sb

BO = sb.sinh_bo(3, seed=1)


def lay(bay):
    return [m for m in BO if m["bay"] == bay][0]


def pb(noi_dung, chu_the="trẻ", **kw):
    d = {"chu_the": chu_the, "noi_dung": noi_dung,
         "do_chac_chan": "chắc chắn", "tinh_huong": "thực tế", "luot_thoai": [1]}
    d.update(kw)
    return d


# ------------------------------------------------------------------ chu_the

def test_chu_the_dat_khi_gan_cho_me():
    m = lay("chu_the")
    dat, _ = dbc.kiem_chu_the(m, [pb(f"dị ứng {m['thuoc']}", chu_the="mẹ")])
    assert dat is True


def test_chu_the_hong_khi_gan_cho_tre():
    m = lay("chu_the")
    dat, ly_do = dbc.kiem_chu_the(m, [pb(f"dị ứng {m['thuoc']}", chu_the="trẻ")])
    # Kiem HANH VI, va kiem rang ly do NEU TEN chu the sai — khong khop nguyen
    # van thong bao, vi mot phep kiem gion se do khi doi cach dien dat.
    assert dat is False
    assert "trẻ" in ly_do


def test_chu_the_hong_khi_gan_cho_BENH_NHAN():
    """LO~ HONG da co that, bit ngay 10/09/2026.

    Ban truoc kiem the PHU DINH: "chu the khong khop (tre|be|chau|em be)". Mot
    he thong ghi `chu_the = "benh nhan"` cho di ung cua me thi LOT QUA, vi
    "benh nhan" khong nam trong bang tu do.

    Do duoc: doi chung tam thuong `benh_nhan` — gan MOI menh de cho benh nhan —
    dat 60/60 = 100% o nhom nay trong khi no sai toan bo.
    """
    m = lay("chu_the")
    dat, ly_do = dbc.kiem_chu_the(
        m, [pb(f"dị ứng {m['thuoc']}", chu_the="bệnh nhân")])
    assert dat is False
    assert "bệnh nhân" in ly_do


def test_chu_the_dat_khi_gan_cho_nguoi_nha():
    """"nguoi nha" va "toi" cung la nguoi ke, khong chi "me"."""
    m = lay("chu_the")
    for ten in ("người nhà", "tôi", "Mẹ"):
        dat, _ = dbc.kiem_chu_the(m, [pb(f"dị ứng {m['thuoc']}", chu_the=ten)])
        assert dat is True, ten


def test_chu_the_hong_khi_khong_trich_duoc_gi():
    assert dbc.kiem_chu_the(lay("chu_the"), [pb("sốt")])[0] is False


# --------------------------------------------------------------- chac_chan

def test_chac_chan_dat_khi_giu_chua_ghi_nhan():
    m = lay("chac_chan")
    dat, _ = dbc.kiem_chac_chan(m, [pb(m["trieu_chung"], do_chac_chan="chưa ghi nhận")])
    assert dat is True


def test_chac_chan_hong_khi_nang_thanh_phu_dinh_chac_chan():
    m = lay("chac_chan")
    dat, _ = dbc.kiem_chac_chan(
        m, [pb(m["trieu_chung"], do_chac_chan="chắc chắn", phu_dinh=True)])
    assert dat is False


# -------------------------------------------------------------- dinh_chinh

def test_dinh_chinh_dat_khi_giu_moc_moi():
    m = lay("dinh_chinh")
    dat, _ = dbc.kiem_dinh_chinh(m, [pb(f"sốt {m['moc_moi']}")])
    assert dat is True


def test_dinh_chinh_DAT_khi_giu_ca_hai_va_danh_dau():
    """Thiet ke doi GIU ban cu de truy lai duoc rang da co dinh chinh.

    Ban 1 cua phep kiem bao hong o day — sai, va cho 0/15 trong khi mo hinh
    lam dung. Xem docstring cua kiem_dinh_chinh.
    """
    m = lay("dinh_chinh")
    dat, _ = dbc.kiem_dinh_chinh(m, [
        pb(f"sốt {m['moc_cu']}", quan_he="không"),
        pb(f"sốt {m['moc_moi']}", quan_he="đính chính", quan_he_voi=0)])
    assert dat is True


def test_dinh_chinh_hong_khi_giu_ca_hai_ma_khong_danh_dau():
    """Hai moc ngang hang nhau thi khong biet dung cai nao."""
    m = lay("dinh_chinh")
    dat, ly_do = dbc.kiem_dinh_chinh(
        m, [pb(f"sốt {m['moc_moi']}"), pb(f"sốt {m['moc_cu']}")])
    assert dat is False and "khong danh dau" in ly_do


def test_dinh_chinh_dat_khi_chi_giu_moc_moi():
    m = lay("dinh_chinh")
    assert dbc.kiem_dinh_chinh(m, [pb(f"sốt {m['moc_moi']}")])[0] is True


def test_dinh_chinh_hong_khi_mat_moc_moi():
    m = lay("dinh_chinh")
    assert dbc.kiem_dinh_chinh(m, [pb(f"sốt {m['moc_cu']}")])[0] is False


# --------------------------------------------------------------- dien_bien

def test_dien_bien_dat_khi_giu_ca_hai_moc():
    m = lay("dien_bien")
    dat, _ = dbc.kiem_dien_bien(m, [
        pb(f"{m['trieu_chung']}", moc_thoi_gian=m["moc_cu"]),
        pb(f"hết {m['trieu_chung']}", moc_thoi_gian=m["moc_moi"])])
    assert dat is True


def test_dien_bien_hong_khi_vut_mat_moc_dau():
    """Loi de mac nhat: coi dien bien la dinh chinh."""
    m = lay("dien_bien")
    dat, ly_do = dbc.kiem_dien_bien(
        m, [pb(f"hết {m['trieu_chung']}", moc_thoi_gian=m["moc_moi"])])
    assert dat is False and "vut mat moc dau" in ly_do


# ---------------------------------------------------------------- gia_dinh

def test_gia_dinh_dat_khi_khong_ghi_thanh_thuc_te():
    m = lay("gia_dinh")
    dat, _ = dbc.kiem_gia_dinh(m, [pb(m["trieu_chung_that"])])
    assert dat is True


def test_gia_dinh_dat_khi_danh_dau_la_gia_dinh():
    m = lay("gia_dinh")
    dat, _ = dbc.kiem_gia_dinh(m, [pb(m["dieu_kien"], tinh_huong="giả định")])
    assert dat is True


def test_gia_dinh_hong_khi_ghi_thanh_trieu_chung_thuc_te():
    m = lay("gia_dinh")
    dat, ly_do = dbc.kiem_gia_dinh(m, [pb(m["dieu_kien"], tinh_huong="thực tế")])
    assert dat is False and "thuc te" in ly_do


# ----------------------------------------------------------------- moi_bia

def test_moi_bia_dat_khi_khong_nhac_toi():
    m = lay("moi_bia")
    dat, _ = dbc.kiem_moi_bia(m, [pb(m["trieu_chung_that"])])
    assert dat is True


def test_moi_bia_hong_khi_tu_dien():
    m = lay("moi_bia")
    dat, ly_do = dbc.kiem_moi_bia(m, [pb(m["moi_khong_duoc_tra_loi"])])
    assert dat is False and "tu dien" in ly_do


# -------------------------------------------------------------------- sach

def test_sach_dat_khi_khong_bao_dong_gia():
    dat, _ = dbc.kiem_sach(lay("sach"), [pb("ho khan"), pb("sốt")])
    assert dat is True


def test_sach_hong_khi_canh_giac_qua_muc():
    dat, ly_do = dbc.kiem_sach(
        lay("sach"), [pb("ho khan", do_chac_chan="chưa ghi nhận")])
    assert dat is False and "bao dong gia" in ly_do


# ------------------------------------------------------------- so khop tu

def test_so_theo_ranh_gioi_TU_khong_phai_ranh_gioi_CUM():
    """`_co` chan khop trong long MOT TU, khong chan khop tien to cua mot CUM.

    "ho" KHONG khop trong "hoac" (cung mot tu) nhung CO khop trong "ho khan"
    (hai tu). Do la hanh vi dung: neu chan ca truong hop sau thi "2 ngay" se
    khong khop trong "sot 2 ngay nay" — pha vo phep kiem dinh_chinh.

    Viec `moi` va `trieu_chung_that` khong long nhau duoc bao dam o khau SINH
    du lieu (`sinh_bo_chan_doan._chon_khong_trung`), khong phai o khau so khop.
    Xem test_bo_chan_doan.test_dieu_kien_gia_dinh_khong_trung_voi_trieu_chung_that.
    """
    assert dbc._co("ho khan", "trẻ ho khan") is True
    assert dbc._co("ho", "trẻ ho nhiều") is True
    assert dbc._co("ho", "trẻ hoặc mẹ") is False, "khong duoc khop trong long mot tu"
    assert dbc._co("2 ngày", "sốt 2 ngày nay") is True, "phep kiem dinh_chinh dua vao day"


def test_khong_co_phat_bieu_nao_thi_hong():
    for bay in sb.BAY:
        m = [x for x in BO if x["bay"] == bay][0]
        assert dbc.cham(m, [])[0] is False, bay


def test_khong_khop_vao_DUOI_mot_tu_khac():
    """Loi that: "ho" khop vao duoi chu "cho" vi chi chan ranh gioi phai.

    "Cho uong ha sot" bi tinh la da nhac toi trieu chung "ho" -> phep kiem
    moi_bia bao hong oan 3/4 truong hop.
    """
    assert dbc._co("ho", "cho uống hạ sốt") is False, "khop vao duoi chu 'cho'"
    assert dbc._co("ho", "bác sĩ cho thuốc") is False
    assert dbc._co("ho", "trẻ ho nhiều") is True, "van phai khop khi dung la tu 'ho'"
    assert dbc._co("ho khan", "trẻ ho khan") is True
    assert dbc._co("2 ngày", "sốt 2 ngày nay") is True


def test_moi_bia_dat_khi_chi_co_tu_chua_cum_do():
    m = lay("moi_bia")
    m = dict(m, moi_khong_duoc_tra_loi="ho")
    assert dbc.kiem_moi_bia(m, [pb("cho uống thuốc hạ sốt")])[0] is True


# ------------------------------------------------------------- kiem CHEO

def test_kiem_cheo_bat_duoc_tuoi_cua_tre_gan_cho_nguoi_nha():
    """Loi THAT tim thay khi doc du lieu tho cua lan do 4B: 17 ban ghi ghi
    "cháu ba tuổi" ma chu the la "nguoi nha". Khong phep kiem tinh huong nao
    cham toi, vi no khong phai bay cua tinh huong nao."""
    loi = dbc.kiem_cheo({}, [pb("cháu ba tuổi", chu_the="người nhà")])
    assert len(loi) == 1 and loi[0]["loai"] == "chu_the_cua_dac_diem_tre"


def test_kiem_cheo_khong_bao_khi_chu_the_dung():
    assert dbc.kiem_cheo({}, [pb("cháu ba tuổi", chu_the="trẻ")]) == []
    assert dbc.kiem_cheo({}, [pb("cháu bốn tuổi", chu_the="bé")]) == []


def test_kiem_cheo_khong_dung_toi_ban_ghi_cua_nguoi_nha_that():
    """Di ung CUA nguoi nha thi chu the la nguoi nha — dung, khong duoc bao."""
    assert dbc.kiem_cheo({}, [pb("dị ứng penicillin", chu_the="mẹ")]) == []
    assert dbc.kiem_cheo({}, [pb("tiểu đường", chu_the="người nhà")]) == []


def test_kiem_cheo_chay_tren_moi_tinh_huong():
    """Khong duoc phu thuoc truong `bay` — no la lop kiem doc lap."""
    for bay in sb.BAY:
        m = [x for x in BO if x["bay"] == bay][0]
        assert dbc.kiem_cheo(m, [pb("cháu ba tuổi", chu_the="người nhà")])


# ------------------------- bo cham phai phu DU tinh huong bo sinh co

def test_PHEP_KIEM_phu_du_moi_tinh_huong_cua_bo_sinh():
    """Loi that. Bo sinh co 9 tinh huong, bo cham chi co 7: `nghi_ngo` va
    `nhat_quan` duoc them vao bo sinh ma khong them phep kiem.

    Hau qua: `cham()` nem `KeyError` khi gap hai nhom do, tuc la chung CHUA BAO
    GIO duoc cham — va khong ai biet, vi khong ai chay toi do.
    """
    from src import sinh_bo_chan_doan
    thieu = [b for b in sinh_bo_chan_doan.BAY if b not in dbc.PHEP_KIEM]
    assert not thieu, f"khong co phep kiem cho: {thieu}"


def test_nghi_ngo_hong_khi_NANG_MUC():
    m = lay("nghi_ngo")
    dat, ly_do = dbc.kiem_nghi_ngo(
        m, [pb(m["benh_nghi"], do_chac_chan="chắc chắn")])
    assert dat is False and "chac chan" in ly_do


def test_nghi_ngo_dat_khi_GIU_muc_nghi():
    m = lay("nghi_ngo")
    dat, _ = dbc.kiem_nghi_ngo(m, [pb(m["benh_nghi"], do_chac_chan="nghi ngờ")])
    assert dat is True


def test_nghi_ngo_hong_khi_BO_HAN_thong_tin():
    """Bay nay co hai ve. Im lang khong nhac gi cung la sai."""
    m = lay("nghi_ngo")
    dat, ly_do = dbc.kiem_nghi_ngo(m, [pb("sốt")])
    assert dat is False and "bo han" in ly_do


def test_nhat_quan_hong_khi_thuoc_da_ngung_van_o_dang_dang_dung():
    m = lay("nhat_quan")
    dat, ly_do = dbc.kiem_nhat_quan(m, [pb(m["thuoc_da_ngung"])])
    assert dat is False and "DA NGUNG" in ly_do


def test_nhat_quan_dat_khi_co_dau_vet_da_ngung():
    m = lay("nhat_quan")
    dat, _ = dbc.kiem_nhat_quan(
        m, [pb(f"{m['thuoc_da_ngung']}, đã ngừng hai tuần")])
    assert dat is True
    dat2, _ = dbc.kiem_nhat_quan(
        m, [pb(m["thuoc_da_ngung"], trang_thai="bị thay thế")])
    assert dat2 is True
