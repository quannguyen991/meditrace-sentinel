# -*- coding: utf-8 -*-
"""Test phep do van xuoi tren bo chan doan.

Phep do nay khong dung thuoc do nao — dap an biet truoc. Nhung chinh vi the
no phai duoc test hai chieu: bao DAT khi ban dung, bao HONG khi ban sai. Mot
phep kiem khong bao gio bao sai thi vo dung.
"""
from src import do_van_xuoi as dvx
from src import sinh_bo_chan_doan as sb

BO = sb.sinh_bo(3, seed=1)


def lay(bay):
    return [m for m in BO if m["bay"] == bay][0]


# ------------------------------------------------------------- chu_the

def test_chu_the_DAT_khi_gan_cho_nguoi_nha():
    m = lay("chu_the")
    van = f"TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI\n\nMẹ bệnh nhi dị ứng {m['thuoc']}."
    assert dvx.kiem_chu_the(m, van)[0] is True


def test_chu_the_HONG_khi_gan_cho_tre():
    m = lay("chu_the")
    van = f"DỊ ỨNG\n\nTrẻ dị ứng {m['thuoc']}."
    dat, ly_do = dvx.kiem_chu_the(m, van)
    assert dat is False and m["thuoc"] in ly_do


def test_chu_the_KHONG_KET_LUAN_khi_khong_nhac_toi_thuoc():
    """Bo sot khac gan sai. Gop lam mot la che mat mot trong hai."""
    m = lay("chu_the")
    assert dvx.kiem_chu_the(m, "BỆNH SỬ HIỆN TẠI\n\nTrẻ ho.")[0] is None


def test_chu_the_DAT_khi_cau_neu_ca_hai_nguoi():
    """"Me di ung X, chau chua thay bi" — cau co ca hai, khong duoc bao sai."""
    m = lay("chu_the")
    van = f"Mẹ dị ứng {m['thuoc']}, cháu chưa thấy bị bao giờ."
    assert dvx.kiem_chu_the(m, van)[0] is True


# ------------------------------------------------------------ dien_bien

def test_dien_bien_DAT_khi_giu_ca_hai_moc():
    m = lay("dien_bien")
    van = f"BỆNH SỬ HIỆN TẠI\n\n{m['moc_cu']} trẻ {m['trieu_chung']}, {m['moc_moi']} đã hết."
    assert dvx.kiem_dien_bien(m, van)[0] is True


def test_dien_bien_HONG_khi_vut_moc_dau():
    m = lay("dien_bien")
    van = f"BỆNH SỬ HIỆN TẠI\n\n{m['moc_moi']} trẻ đã hết {m['trieu_chung']}."
    dat, ly_do = dvx.kiem_dien_bien(m, van)
    assert dat is False and "vut moc dau" in ly_do


# -------------------------------------------------------------- moi_bia

def test_moi_bia_DAT_khi_khong_nhac_toi():
    m = lay("moi_bia")
    assert dvx.kiem_moi_bia(m, f"Trẻ {m['trieu_chung_that']}.")[0] is True


def test_moi_bia_HONG_khi_khang_dinh_trieu_chung_khong_ai_tra_loi():
    m = lay("moi_bia")
    dat, _ = dvx.kiem_moi_bia(m, f"Trẻ có {m['moi_khong_duoc_tra_loi']}.")
    assert dat is False


def test_moi_bia_DAT_khi_ghi_ro_la_chua_ghi_nhan():
    m = lay("moi_bia")
    van = f"Chưa ghi nhận {m['moi_khong_duoc_tra_loi']}."
    assert dvx.kiem_moi_bia(m, van)[0] is True


# ------------------------------------------------------------- gia_dinh

def test_gia_dinh_HONG_khi_ghi_thanh_trieu_chung_that():
    m = lay("gia_dinh")
    dat, _ = dvx.kiem_gia_dinh(m, f"Trẻ {m['dieu_kien']}.")
    assert dat is False


def test_gia_dinh_DAT_khi_giu_dau_hieu_dieu_kien():
    m = lay("gia_dinh")
    van = f"Nếu trẻ {m['dieu_kien']} thì tái khám."
    assert dvx.kiem_gia_dinh(m, van)[0] is True


# ------------------------------------------------------------ chac_chan

def test_chac_chan_HONG_khi_nang_thanh_phu_dinh():
    m = lay("chac_chan")
    assert dvx.kiem_chac_chan(m, f"Trẻ {m['cum_sai']}.")[0] is False


def test_chac_chan_DAT_khi_giu_hedge():
    m = lay("chac_chan")
    assert dvx.kiem_chac_chan(m, f"Chưa ghi nhận {m['trieu_chung']}.")[0] is True


# ----------------------------------------------------------- dinh_chinh

def test_dinh_chinh_DAT_khi_chi_giu_moc_moi():
    m = lay("dinh_chinh")
    assert dvx.kiem_dinh_chinh(m, f"Sốt {m['moc_moi']}.")[0] is True


def test_dinh_chinh_HONG_khi_mat_moc_moi():
    m = lay("dinh_chinh")
    assert dvx.kiem_dinh_chinh(m, f"Sốt {m['moc_cu']}.")[0] is False


def test_dinh_chinh_HONG_khi_giu_ca_hai_khong_danh_dau():
    m = lay("dinh_chinh")
    van = f"Sốt {m['moc_cu']}. Sốt {m['moc_moi']}."
    assert dvx.kiem_dinh_chinh(m, van)[0] is False


# ----------------------------------------------------------------- sach

def test_sach_HONG_khi_ban_rong():
    assert dvx.kiem_sach(lay("sach"), "")[0] is False


def test_sach_DAT_khi_ban_binh_thuong():
    assert dvx.kiem_sach(lay("sach"), "BỆNH SỬ HIỆN TẠI\n\nTrẻ ho khan.")[0] is True


# ------------------------------------------------------------ do chac

def test_moi_tinh_huong_deu_khai_bao_do_chac():
    """Tron phep kiem chac voi phep kiem xap xi la bao cao sai do tin cay."""
    for bay in sb.BAY:
        assert bay in dvx.DO_CHAC
        assert dvx.DO_CHAC[bay] in ("chắc", "vừa")


# ------------------------------------- trung lap voi CACH DIEN DAT

def test_dien_bien_DAT_khi_dung_tu_tuong_duong():
    """A viet "khoi phat hom qua, HIEN TAI da het" — giu ca hai moc bang tu
    khac. Phat cach dien dat thay vi phat thong tin sai la lam hong ca phep
    so giua van xuoi va cum ghep."""
    m = lay("dien_bien")
    van = "BỆNH SỬ HIỆN TẠI\n\nTrẻ khó thở khởi phát hôm qua, hiện tại đã hết."
    assert dvx.kiem_dien_bien(m, van)[0] is True


def test_dinh_chinh_DAT_khi_danh_dau_bang_TRANG_THAI_BI_THAY_THE():
    """C ghi moc cu o muc CAN XAC NHAN kem "trang thai bi thay the". Do dung
    la danh dau, chi khac chu."""
    m = lay("dinh_chinh")
    van = (f"BỆNH SỬ HIỆN TẠI\n\nđau bụng ({m['moc_moi']}).\n\n"
           f"CẦN XÁC NHẬN\n\nđau bụng ({m['moc_cu']}) — trạng thái bị thay thế.")
    assert dvx.kiem_dinh_chinh(m, van)[0] is True


def test_dinh_chinh_VAN_HONG_khi_giu_ca_hai_ma_khong_danh_dau_gi():
    """Chieu nguoc lai phai con bao sai duoc, khong thi noi long thanh vo dung."""
    m = lay("dinh_chinh")
    van = f"BỆNH SỬ HIỆN TẠI\n\nđau bụng {m['moc_cu']}. đau bụng {m['moc_moi']}."
    assert dvx.kiem_dinh_chinh(m, van)[0] is False


def test_dien_bien_VAN_HONG_khi_that_su_vut_mot_moc():
    m = lay("dien_bien")
    assert dvx.kiem_dien_bien(m, "Trẻ hiện tại đã hết khó thở.")[0] is False
