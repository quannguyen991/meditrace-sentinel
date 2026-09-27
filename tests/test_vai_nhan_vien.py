# -*- coding: utf-8 -*-
"""Vai nhan vien y te khong phai `chu_the` cua thong tin lam sang.

LOI DA XAY RA, va no la luan diem cua du an xay ra ben trong du an.

Khau trich ghi `chu_the = "bac si"` cho 160/537 phat bieu tren tap phat trien —
moi cau bac si NOI: ket qua kham, chan doan, ke hoach dieu tri. Nhung "hong hoi
do" la thong tin VE BENH NHAN do bac si noi. `chu_the` la thong tin ve ai,
`nguoi_noi` la ai noi; gop hai truong do lai chinh la lo~i quy gan.

VI SAO KHONG THUOC DO NAO THAY. Thuoc do dau-cuoi suy chu the tu VAN BAN sinh
ra va ten muc, khong tu `chu_the_id`. Nhanh B va C giu cau dung muc nen thuoc
do doc ra "benh nhan" va cho diem dung — 98,6% o tang bac si — du bieu dien ben
trong sai. Chi nhanh D phoi no ra, vi D la nhanh duy nhat HANH DONG theo
`chu_the_id`: `sua_cuc_bo` doi cau sang muc TIEN SU GIA DINH VA XA HOI. 104
lan. Gia: tang bac si 98,6% -> 52,8%, diem gop -13,7.
"""
import pytest

from src import phat_bieu, sua_cuc_bo


def _ps(chu_the, noi_dung="họng hơi đỏ", luot=2):
    return [{"chu_the": chu_the, "noi_dung": noi_dung, "luot_thoai": [luot],
             "do_chac_chan": "chắc chắn"}]


# --------------------------------------------------- nhan dang vai

@pytest.mark.parametrize("ten", ["bác sĩ", "Bác Sĩ", " bác sỹ ", "điều dưỡng",
                                 "y tá", "BS"])
def test_nhan_dang_vai_nhan_vien(ten):
    assert phat_bieu.la_vai_nhan_vien(ten)


@pytest.mark.parametrize("ten", ["bệnh nhân", "mẹ", "bà ngoại", "trẻ", "",
                                 None, "bác"])
def test_khong_bat_nham_vai_khac(ten):
    """"bac" khong phai "bac si" — mot chu khac nhau va la hai nguoi khac."""
    assert not phat_bieu.la_vai_nhan_vien(ten)


# ------------------------------------- quy ve benh nhan trong tu_json

def test_chu_the_bac_si_duoc_quy_ve_BENH_NHAN():
    """Loi that. Truoc khi sua, cho nay ra id_khac va keo theo ca chuoi."""
    ps, loi = phat_bieu.tu_json(_ps("bác sĩ"))
    assert not loi
    assert ps[0].chu_the_id == 0


def test_quy_ve_benh_nhan_CA_KHI_co_bang_lien_ket():
    """Nhanh C co `id_theo_ten`. Bang do khong co "bac si" nen truoc day roi
    vao `id_khac` — dung duong nao cung phai chan."""
    ps, _ = phat_bieu.tu_json(_ps("bác sĩ"), id_theo_ten={"trẻ": 0, "mẹ": 2},
                              id_khac=7)
    assert ps[0].chu_the_id == 0


def test_nguoi_nha_that_VAN_la_nguoi_khac():
    """Doi chung: hang rao khong duoc lam mat kha nang phan biet nguoi nha."""
    ps, _ = phat_bieu.tu_json(_ps("mẹ", "dị ứng penicillin"),
                              id_theo_ten={"trẻ": 0, "mẹ": 2}, id_khac=7)
    assert ps[0].chu_the_id == 2


def test_dem_vai_nhan_vien_de_bao_cao_duoc_ty_le():
    """Chuan hoa am tham thi khong ai biet khau trich sai bao nhieu."""
    assert phat_bieu.dem_vai_nhan_vien(
        _ps("bác sĩ") + _ps("mẹ") + _ps("điều dưỡng")) == 2


# ------------------------------------- `ten_chu_the` phai duoc gan that

def test_ten_chu_the_duoc_gan_trong_tu_json():
    """Truoc 10/09/2026 `tu_json` de trong truong nay, va `nhanh` gan lai sau.

    Goi `tu_json` truc tiep — nhu `do_tang_quan_he` va `duong_danh_doi` dang
    lam — thi nhan chuoi rong, va moi hang rao doc truong do thanh MA CHET:
    khong bao gio bao loi, chi khong bao gio bat duoc gi.
    """
    ps, _ = phat_bieu.tu_json(_ps("bác sĩ"))
    assert ps[0].ten_chu_the == "bác sĩ"
    assert ps[0].to_dict()["ten_chu_the"] == "bác sĩ"


def test_ten_chu_the_KHONG_lech_hang_khi_co_ban_ghi_khong_hop_le():
    """Loi that cua cach gan cu.

    `nhanh` gan lai bang `zip(ps, [x for x in tho if x.get("luot_thoai")])`.
    Ban ghi thu hai duoi day co `luot_thoai` nhung thieu `quan_he_voi`, nen no
    bi loai khoi `ps` ma van con o danh sach ben phai — phep zip lech mot nhip
    va phat bieu cuoi nhan ten chu the cua ban ghi khac.

    Gan tai cho trong `tu_json` thi khong co cho nao de lech.
    """
    tho = [
        {"chu_the": "bệnh nhân", "noi_dung": "sốt", "luot_thoai": [2]},
        {"chu_the": "mẹ", "noi_dung": "ho", "luot_thoai": [3],
         "quan_he": "đính chính"},                      # thieu quan_he_voi
        {"chu_the": "bác sĩ", "noi_dung": "họng đỏ", "luot_thoai": [4]},
    ]
    ps, loi = phat_bieu.tu_json(tho)
    assert len(loi) == 1 and len(ps) == 2
    assert [p.ten_chu_the for p in ps] == ["bệnh nhân", "bác sĩ"]
    # Va hang rao van bat dung phat bieu cuoi.
    assert ps[1].chu_the_id == 0


# ------------------------------- hang rao thu hai: sua_cuc_bo tu chan

def _pb(chu_the_id, ten_chu_the, noi_dung):
    return {"chu_the_id": chu_the_id, "ten_chu_the": ten_chu_the,
            "noi_dung": noi_dung, "trang_thai": "còn hiệu lực",
            "do_chac_chan": "chắc chắn"}


def test_cau_bac_si_KHONG_bi_doi_sang_muc_gia_dinh():
    """Loi that, 104 lan tren tap phat trien.

    Ban nhap ngoai va ban ghi cu khong di qua `tu_json`, nen `sua_cuc_bo` phai
    tu chan chu khong duoc dua het vao hang rao o tren.
    """
    cau = "bác sĩ: hạ sốt, uống nhiều nước"
    loi, _ = sua_cuc_bo.kiem_mot_cau(
        cau, "KHÁM LÂM SÀNG",
        [_pb(1, "bác sĩ", "hạ sốt, uống nhiều nước")], id_benh_nhan=0)
    assert loi != "sai_nguoi"


def test_thong_tin_cua_NGUOI_NHA_van_bi_doi_sang_muc_gia_dinh():
    """Doi chung, va day moi la viec co ich cua phep kiem `sai_nguoi`."""
    loi, _ = sua_cuc_bo.kiem_mot_cau(
        "dị ứng penicillin", "TIỀN SỬ DỊ ỨNG",
        [_pb(2, "mẹ", "dị ứng penicillin")], id_benh_nhan=0)
    assert loi == "sai_nguoi"
