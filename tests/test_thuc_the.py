# -*- coding: utf-8 -*-
"""Test lien ket thuc the — ca hai chieu loi.

Ba test dau lay nguyen van tu ke hoach (Task 11 buoc 1).
"""
from src import thuc_the

HT = ("Bệnh nhân: Tôi uống thuốc A.\n"
      "Người nhà: Thuốc đó chồng tôi ngừng từ tuần trước rồi.\n"
      "Bệnh nhân: Đúng, giờ tôi không uống nữa.")


# ------------------------------------------------- ba test trong ke hoach

def test_ba_luot_cung_mot_thuoc():
    thuoc = [t for t in thuc_the.lien_ket(HT) if t.loai == "thuốc"]
    assert len(thuoc) == 1, "'thuoc A' va 'thuoc do' phai la MOT thuc the"


def test_ba_luot_cung_mot_nguoi():
    nguoi = [t for t in thuc_the.lien_ket(HT) if t.loai == "người"]
    bn = [t for t in nguoi if "tôi" in t.cach_goi or "chồng tôi" in t.cach_goi]
    assert len(bn) == 1, "'toi' va 'chong toi' deu tro toi BENH NHAN"


def test_khong_gop_nham_hai_thuoc_khac_nhau():
    """Loi nguoc lai: gop nham cung nguy hiem."""
    ht = "Bệnh nhân: Tôi uống thuốc A và thuốc B."
    assert len([t for t in thuc_the.lien_ket(ht) if t.loai == "thuốc"]) == 2


# ----------------------------------------- chieu gop nham (nguy hiem hon)

def test_toi_cua_nguoi_nha_KHONG_gop_vao_benh_nhan():
    """Cot loi cua du an: "toi" cua nguoi nha la NGUOI NHA, khong phai benh nhan."""
    ht = ("Bác sĩ: Nhà mình có ai dị ứng thuốc không ạ?\n"
          "Người nhà: Tôi dị ứng penicillin, còn cháu thì chưa thấy bị bao giờ.")
    nguoi = [t for t in thuc_the.lien_ket(ht) if t.loai == "người"]
    co_toi = [t for t in nguoi if "tôi" in t.cach_goi]
    assert len(co_toi) == 1
    assert co_toi[0].ten_chuan == "người nhà", "gan 'toi' cua nguoi nha cho benh nhan"


def test_hai_cum_quan_he_khac_nhau_thi_KHONG_gop():
    """Khong the ca "chong toi" lan "con toi" cung la benh nhan.

    Gop nham hai nguoi nguy hiem hon bo sot mot lien ket, nen luc khong chac
    thi de rieng.
    """
    ht = ("Người nhà: Chồng tôi bị tiểu đường.\n"
          "Người nhà: Con tôi thì hay ho về đêm.")
    nguoi = thuc_the.lien_ket(ht)
    bn = [t for t in nguoi if t.ten_chuan == "bệnh nhân"][0]
    assert "chồng tôi" not in bn.cach_goi and "con tôi" not in bn.cach_goi
    rieng = [t for t in nguoi if t.ten_chuan in ("chồng tôi", "con tôi")]
    assert len(rieng) == 2


def test_TUI_Nam_Bo_nhu_TOI():
    """"tui" la cach tu xung Nam Bo (them 24/09/2026). Truoc do "Me tui bi tieu duong"
    khong sinh thuc the "me tui": tien su gia dinh roi vao chinh nguoi noi."""
    ht = ("Bệnh nhân: Mẹ tui bị tiểu đường.\n"
          "Bệnh nhân: Tui thì hay nhức đầu.")
    nguoi = thuc_the.lien_ket(ht)
    assert [t for t in nguoi if t.ten_chuan == "mẹ tui"], "khong sinh thuc the 'me tui'"
    bn = [t for t in nguoi if t.ten_chuan == "bệnh nhân"][0]
    assert "tui" in bn.cach_goi and "mẹ tui" not in bn.cach_goi


def test_TUI_trong_cum_so_huu_khong_tinh_la_nguoi_noi():
    ht = "Người nhà: Chồng tui ngừng thuốc rồi."
    nha = [t for t in thuc_the.lien_ket(ht) if t.ten_chuan == "người nhà"]
    assert not any("tui" in t.cach_goi for t in nha), "dem 'tui' trong 'chong tui'"


def test_toi_trong_cum_so_huu_khong_tinh_la_nguoi_noi():
    """"chong toi" chi mot nguoi; chu "toi" ben trong khong duoc dem rieng."""
    ht = "Người nhà: Chồng tôi ngừng thuốc rồi."
    nguoi = thuc_the.lien_ket(ht)
    nha = [t for t in nguoi if t.ten_chuan == "người nhà"]
    assert not any("tôi" in t.cach_goi for t in nha), "dem 'toi' trong 'chong toi'"


# ------------------------------------------------------- tro nguoc cho thuoc

def test_thuoc_do_tro_ve_thuoc_GAN_NHAT_khong_phai_thuoc_dau():
    ht = ("Bệnh nhân: Tôi uống thuốc A.\n"
          "Bệnh nhân: Sau đó chuyển sang thuốc B.\n"
          "Người nhà: Thuốc đó uống buổi tối ạ.")
    thuoc = [t for t in thuc_the.lien_ket(ht) if t.loai == "thuốc"]
    assert len(thuoc) == 2
    b = [t for t in thuoc if t.ten_chuan == "B"][0]
    a = [t for t in thuoc if t.ten_chuan == "A"][0]
    assert "thuốc đó" in b.cach_goi
    assert "thuốc đó" not in a.cach_goi


def test_tro_nguoc_khi_chua_co_thuoc_nao_thi_bo_qua():
    """Khong duoc tao thuc the ma. Khong co gi de tro ve thi thoi."""
    ht = "Bệnh nhân: Thuốc đó tôi không nhớ tên."
    assert [t for t in thuc_the.lien_ket(ht) if t.loai == "thuốc"] == []


def test_ten_thuoc_trong_tu_dien_duoc_nhan_du_khong_co_chu_thuoc():
    ht = "Người nhà: Cháu dị ứng amoxicillin ạ."
    thuoc = [t for t in thuc_the.lien_ket(ht) if t.loai == "thuốc"]
    assert len(thuoc) == 1 and thuoc[0].ten_chuan.lower() == "amoxicillin"


def test_cung_ten_nhac_hai_lan_van_la_mot_thuc_the():
    ht = ("Bệnh nhân: Tôi uống penicillin.\n"
          "Bác sĩ: Penicillin liều bao nhiêu ạ?")
    thuoc = [t for t in thuc_the.lien_ket(ht) if t.loai == "thuốc"]
    assert len(thuoc) == 1
    assert thuoc[0].luot_thoai == [1, 2]


# ------------------------------------------------------------- tach luot

def test_tach_luot_bo_so_thu_tu_dau_dong():
    luot = thuc_the.tach_luot("1. Bác sĩ: Chào chị.\n2. Người nhà: Vâng ạ.")
    assert luot[0][1] == "bác sĩ" and luot[0][2] == "Chào chị."
    assert luot[1][0] == 2


def test_moi_thuc_the_ghi_lai_luot_lam_bang_chung():
    """Khong co luot thoai thi khong truy vet duoc — ca du an dua vao day."""
    for t in thuc_the.lien_ket(HT):
        if t.cach_goi:
            assert t.luot_thoai, f"{t.ten_chuan} khong co luot thoai"


def test_chua_lien_ket_xet_nghiem_va_benh():
    """Ghi lai gioi han that thay vi de nguoi doc tuong da lam.

    Neu sau nay lam, test nay phai doi — va do la luc can doi.
    """
    ht = "Bác sĩ: Chị đi xét nghiệm máu rồi chứ? Cháu bị viêm phổi."
    loai = {t.loai for t in thuc_the.lien_ket(ht)}
    assert "xét nghiệm" not in loai and "bệnh" not in loai
