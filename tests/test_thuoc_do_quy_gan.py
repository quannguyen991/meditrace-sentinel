# -*- coding: utf-8 -*-
"""Test cho thuoc do quy gan.

Vi sao can thuoc do nay. Cua 4 do nam nhanh bang ROUGE + Section F1 va thu duoc
0,3643 / 0,3582 / 0,3514 — chenh nhau 0,006. Nhung chinh du an da chung minh
bo cham do MU truoc loi quy gan: hoan doi "me di ung penicillin" thanh "tre di
ung penicillin" cho Section F1 = 1,0000 o 271/271 cap.

Tuc la Cua 4 khong truot vi nhanh C kem. No truot vi CAI THUOC DO khong nhin
thay thu dang duoc do. Dung mot cai thuoc mu de ket luan ve mot co che chuyen
tri diem mu cua no la mot loi thiet ke, khong phai mot ket qua.

Thuoc do nay do dung MOT thu: menh de co duoc gan cho DUNG NGUOI khong.
"""
from src import thuoc_do_quy_gan as tdq

DUNG = """TIỀN SỬ GIA ĐÌNH

Mẹ dị ứng penicillin.

DỊ ỨNG

Trẻ chưa ghi nhận dị ứng thuốc."""

HOAN_DOI = """TIỀN SỬ GIA ĐÌNH

Trẻ dị ứng penicillin.

DỊ ỨNG

Mẹ chưa ghi nhận dị ứng thuốc."""


# ------------------------------------------------------------ tach menh de

def test_tach_duoc_menh_de_kem_chu_the():
    ds = tdq.tach_menh_de(DUNG)
    assert len(ds) == 2
    assert {m.chu_the for m in ds} == {"người nhà", "bệnh nhân"}


def test_chu_the_lay_tu_TU_TRONG_CAU_truoc_khi_lay_tu_muc():
    """'Be di hoc mau giao' nam duoi muc GIA DINH van la chuyen cua BE."""
    ds = tdq.tach_menh_de("TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI\n\nBé đi học mẫu giáo.")
    assert ds[0].chu_the == "bệnh nhân"


def test_muc_gia_dinh_la_mac_dinh_khi_cau_khong_neu_ai():
    ds = tdq.tach_menh_de("TIỀN SỬ GIA ĐÌNH\n\nCó người bị hen phế quản.")
    assert ds[0].chu_the == "người nhà"


def test_muc_khac_mac_dinh_la_benh_nhan():
    ds = tdq.tach_menh_de("LÝ DO KHÁM BỆNH\n\nHo và sốt ba ngày.")
    assert ds[0].chu_the == "bệnh nhân"


# ------------------------------------- GIU tu phu dinh, day la cho de sai chet nguoi

def test_phu_dinh_KHONG_bi_coi_la_tu_dem():
    """'khong di ung' va 'di ung' KHONG duoc coi la cung mot menh de.

    Cac bang tu dem tieng Viet san co deu liet 'khong' vao tu dem. Neu bo no
    thi mot benh an ghi nguoc han van dat diem tuyet doi — dung cai loi ma
    thuoc do nay sinh ra de chan.
    """
    a = tdq.tach_menh_de("DỊ ỨNG\n\nTrẻ dị ứng penicillin.")
    b = tdq.tach_menh_de("DỊ ỨNG\n\nTrẻ không dị ứng penicillin.")
    assert not tdq.cung_noi_dung(a[0], b[0])


def test_chua_ghi_nhan_khac_voi_khong_co():
    a = tdq.tach_menh_de("DỊ ỨNG\n\nTrẻ chưa ghi nhận dị ứng.")
    b = tdq.tach_menh_de("DỊ ỨNG\n\nTrẻ không có dị ứng.")
    assert not tdq.cung_noi_dung(a[0], b[0])


# ------------------------------------------------------ tinh chat quyet dinh

def test_HOAN_DOI_CHU_THE_LAM_DIEM_SUP():
    """Tinh chat song con cua thuoc do. ROUGE cho cap nay 1,00; cai nay phai khong."""
    d = tdq.diem(HOAN_DOI, DUNG)
    assert d["f1_quy_gan"] < 0.5, f"do duoc {d['f1_quy_gan']}"
    assert d["dung_quy_gan"] == 0.0
    assert d["so_sai_chu_the"] == 2


def test_ban_giong_het_thi_diem_tuyet_doi():
    d = tdq.diem(DUNG, DUNG)
    assert d["f1_quy_gan"] == 1.0 and d["dung_quy_gan"] == 1.0
    assert d["so_sai_chu_the"] == 0


def test_doi_tu_dong_nghia_KHONG_bi_phat_nhu_hoan_doi_chu_the():
    """Doi chung: loi vo hai phai bi tru it hon han loi nguy hiem.

    Day la phep so lam nen ca luan diem. Neu thuoc do phat hai thu nhu nhau
    thi no cung mu y het ROUGE, chi mu theo kieu khac.
    """
    vo_hai = DUNG.replace("dị ứng penicillin", "dị ứng thuốc penicillin")
    d_vo_hai = tdq.diem(vo_hai, DUNG)
    d_nguy_hiem = tdq.diem(HOAN_DOI, DUNG)
    assert d_vo_hai["f1_quy_gan"] > d_nguy_hiem["f1_quy_gan"] + 0.4


# ------------------------------------------------------------- bo sot va thua

def test_bo_sot_duoc_dem():
    thieu = "TIỀN SỬ GIA ĐÌNH\n\nMẹ dị ứng penicillin."
    d = tdq.diem(thieu, DUNG)
    assert d["so_thieu"] == 1 and d["bo_sot"] == 0.5


def test_viet_it_di_KHONG_lam_tang_diem():
    """Bay lon nhat cua ca du an: giam loi bang cach viet it di.

    Ban chi giu mot menh de dung phai co f1 THAP hon ban giu ca hai.
    """
    thieu = "TIỀN SỬ GIA ĐÌNH\n\nMẹ dị ứng penicillin."
    assert tdq.diem(thieu, DUNG)["f1_quy_gan"] < tdq.diem(DUNG, DUNG)["f1_quy_gan"]


def test_them_menh_de_khong_co_trong_tham_chieu_bi_dem_la_thua():
    thua = DUNG + "\n\nCHẨN ĐOÁN\n\nViêm phổi thùy dưới phải."
    d = tdq.diem(thua, DUNG)
    assert d["so_thua"] == 1


# ---------------------------------------------------------------- ben le

def test_ban_rong_khong_lam_vo_phep_tinh():
    d = tdq.diem("", DUNG)
    assert d["f1_quy_gan"] == 0.0 and d["bo_sot"] == 1.0


def test_bo_qua_dong_tieu_de_khong_tinh_la_menh_de():
    ds = tdq.tach_menh_de("LÝ DO KHÁM BỆNH\n\nHo.")
    assert len(ds) == 1 and "khám" not in ds[0].tu


def test_con_so_KHONG_bi_coi_la_tu_dem():
    """'dau bung 3 ngay' va 'dau bung 5 ngay' phai la hai menh de khac nhau."""
    a = tdq.tach_menh_de("BỆNH SỬ HIỆN TẠI\n\nTrẻ đau bụng 3 ngày.")
    b = tdq.tach_menh_de("BỆNH SỬ HIỆN TẠI\n\nTrẻ đau bụng 5 ngày.")
    assert not tdq.cung_noi_dung(a[0], b[0])


# ------------------------------------------------- gioi han, ghi lai bang test

def test_GHI_LAI_GIOI_HAN_tu_chi_nguoi_nha_mo_ho_khong_duoc_nhan_dien():
    """Day KHONG phai test cho tinh nang — no ghi lai mot cho da BIET la sai.

    'ba', 'bac', 'ma', 'co' deu co nghia thu hai rat thuong gap trong benh an
    ('ba ngay', 'bac si', 'sung ma', 'co be'). Nhan dien chung se gan nham
    menh de cho nguoi nha nhieu hon la gan dung. Da chon do BO SOT thay vi
    GOP NHAM — cung lua chon da chot o Task 11.

    Test hong nghia la ai do vua them chung vao danh sach: hay do lai ty le
    gan nham truoc khi giu thay doi do.
    """
    ds = tdq.tach_menh_de("TIỀN SỬ GIA ĐÌNH\n\nBà ngoại của bé bị tiểu đường.")
    assert ds[0].chu_the == "người nhà", "cum ro nghia thi VAN phai nhan ra"

    mo_ho = tdq.tach_menh_de("BỆNH SỬ HIỆN TẠI\n\nBác của cháu bị lao phổi.")
    assert mo_ho[0].chu_the == "bệnh nhân", (
        "'bac' co bi doc nham thanh nguoi nha khong — hien tai la KHONG doc, "
        "nen cau nay bi gan cho benh nhan. Do la cho bo sot da biet.")


def test_khong_doc_nham_bac_si_thanh_nguoi_nha():
    ds = tdq.tach_menh_de("KHÁM LÂM SÀNG\n\nBác sĩ khám thấy họng đỏ.")
    assert ds[0].chu_the == "bệnh nhân"
