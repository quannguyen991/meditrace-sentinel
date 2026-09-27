# -*- coding: utf-8 -*-
"""Test cho bo sinh nhieu dung trong chung chi thuoc do.

Phep thu nay so hai thuoc do bang cach co y lam hong benh an theo hai kieu.
Neu bo sinh nhieu sai thi ca ket luan sai theo — nen no phai co test rieng,
GIONG NHU phep cham da phai co test rieng o Task 10 (hai lan phep cham tu bia
ra loi roi bao cao chinh cai loi do).
"""
from src import chung_chi_thuoc_do as cc

# Ban thu phai du GIAU de tao duoc nhom doi chung. Ban dau chi co
# "Tre ho ba ngay." / "Me bi hen phe quan." — trong ca ban chi co dung MOT tu
# thay dong nghia duoc, nen khong bao gio dat duoc "doi dung 2 tu" va bon test
# hong. Do khong phai loi cua ma, ma la mau thu khong dai dien.
BAN = """LÝ DO KHÁM BỆNH

Trẻ ho ba ngày, nôn nhiều.

TIỀN SỬ GIA ĐÌNH

Mẹ bị hen phế quản."""


# ------------------------------------------------------------- dem tu khac

def test_dem_tu_khac_khi_hai_ve_khac_so_am_tiet():
    """Phep dem theo VI TRI bao 6 tu khac; can le dung phai bao 2."""
    a = "Trẻ ho ba ngày rồi ạ."
    b = "Bà ngoại ho ba ngày rồi ạ."
    assert cc.so_tu_khac(a, b) == 2


def test_dem_tu_khac_ban_giong_het_thi_bang_khong():
    assert cc.so_tu_khac(BAN, BAN) == 0


# ------------------------------------------------------------ hoan doi

def test_hoan_doi_giu_nguyen_do_dai_va_doi_dung_hai_tu():
    ra = cc.hoan_doi_chu_the(BAN)
    assert ra is not None
    assert "Mẹ ho ba ngày, nôn nhiều." in ra
    assert "Trẻ bị hen phế quản." in ra
    assert cc.so_tu_khac(ra, BAN) == 2


def test_KHONG_dung_toi_dong_tieu_de():
    """'TIEN SU GIA DINH' co chua chu 'gia dinh'. Neu phep hoan doi cham vao
    tieu de thi Section F1 tut vi CAU TRUC vo, va phep thu bi nhiem: bo cham
    cuoc thi se trong nhu the co nhin thay loi quy gan."""
    ra = cc.hoan_doi_chu_the(BAN)
    assert "TIỀN SỬ GIA ĐÌNH" in ra
    assert "LÝ DO KHÁM BỆNH" in ra


def test_khong_hoan_doi_khi_hai_tu_o_CUNG_mot_cau():
    """Doi cho trong cung mot cau ra cau vo nghia, khong phai loi quy gan."""
    mot_cau = "DỊ ỨNG\n\nMẹ dị ứng penicillin còn trẻ thì chưa."
    assert cc.hoan_doi_chu_the(mot_cau) is None


def test_khong_hoan_doi_duoc_khi_ban_khong_nhac_toi_nguoi_nha():
    assert cc.hoan_doi_chu_the("LÝ DO KHÁM BỆNH\n\nTrẻ ho ba ngày.") is None


# --------------------------------------------------------- doi chung vo hai

def test_doi_chung_dat_DUNG_so_tu_yeu_cau():
    ra = cc.doi_dong_nghia(BAN, 2)
    assert ra is not None and cc.so_tu_khac(ra, BAN) == 2


def test_doi_chung_khong_dung_toi_tieu_de():
    ra = cc.doi_dong_nghia(BAN, 2)
    assert "LÝ DO KHÁM BỆNH" in ra and "TIỀN SỬ GIA ĐÌNH" in ra


def test_doi_chung_khong_doi_chu_the():
    """Doi chung phai VO HAI. Neu no cham vao tu chi nguoi thi no khong con la
    nhom doi chung nua — no thanh mot loi quy gan thu hai."""
    ra = cc.doi_dong_nghia(BAN, 2)
    assert "Trẻ" in ra and "Mẹ" in ra


def test_tra_None_khi_khong_dat_dung_con_so():
    """Tha loai mau con hon so hai nhom co so tu bi doi khac nhau — dung bai
    hoc cua Task 3, noi ket luan suyt bi rut nguoc vi le do."""
    ngan = "LÝ DO KHÁM BỆNH\n\nHo."
    assert cc.doi_dong_nghia(ngan, 9) is None


def test_khong_doi_ngay_khi_dung_truoc_moc_thoi_gian():
    """'ngay hom qua' -> 'hom hom qua' la cau hong, khong phai dong nghia."""
    ban = "BỆNH SỬ HIỆN TẠI\n\nSốt cao vào ngày hôm qua."
    ra = cc.doi_dong_nghia(ban, 1)
    assert ra is None or "hôm hôm qua" not in ra


# ------------------------------------------------------------ tinh chat chung

def test_hai_phep_doi_cho_cung_mot_so_tu_bi_doi():
    """Dieu kien cot loi cua ca phep so. Hong test nay la moi ket luan ve
    khoang cach giua hai thuoc do deu mat gia tri."""
    sai = cc.hoan_doi_chu_the(BAN)
    n = cc.so_tu_khac(sai, BAN)
    vo_hai = cc.doi_dong_nghia(BAN, n)
    assert vo_hai is not None
    assert cc.so_tu_khac(vo_hai, BAN) == cc.so_tu_khac(sai, BAN)
