# -*- coding: utf-8 -*-
"""Test cau noi tu dau ra mo hinh sang PhatBieu.

Cau noi nay de sai am tham: no nam giua hai phan da co test, nen loi o day
khong lam do test nao khac ma van lam hong ket qua cuoi.
"""
from src import phat_bieu as pb
from src import thuc_the
from src.sinh_benh_an import MUC_NGUOI_KHAC


def js(noi_dung, chu_the="trẻ", luot=None, **kw):
    d = {"chu_the": chu_the, "noi_dung": noi_dung,
         "luot_thoai": luot if luot is not None else [1],
         "do_chac_chan": "chắc chắn", "phu_dinh": False,
         "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại",
         "moc_thoi_gian": None, "quan_he": "không", "quan_he_voi": None}
    d.update(kw)
    return d


# ------------------------------------------------------------ nguoi noi

def test_nguoi_noi_lay_tu_luot_bang_chung_CUOI():
    """Cap hoi-dap [1,2]: luot 2 la cau tra loi, nguoi tra loi moi phat ngon."""
    ra, loi = pb.tu_json([js("sốt", luot=[1, 2])],
                         nguoi_noi_theo_luot={1: "bác sĩ", 2: "người nhà"})
    assert loi == []
    assert ra[0].nguoi_noi == "người nhà"


def test_ban_ghi_khong_co_luot_thoai_bi_BO_chu_khong_doan_bu():
    ra, loi = pb.tu_json([js("sốt", luot=[])])
    assert ra == []
    assert len(loi) == 1 and "bang chung" in loi[0]["ly_do"]


def test_mot_ban_ghi_hong_khong_lam_mat_cac_ban_con_lai():
    ra, loi = pb.tu_json([js("sốt", luot=[]), js("ho khan", luot=[2])])
    assert len(ra) == 1 and ra[0].noi_dung == "ho khan"
    assert len(loi) == 1


# --------------------------------------------------------------- chu the

def test_nhanh_B_gan_id_0_cho_cac_cach_goi_benh_nhan():
    for ten in ("trẻ", "bé", "cháu", "bệnh nhân"):
        ra, _ = pb.tu_json([js("sốt", chu_the=ten)])
        assert ra[0].chu_the_id == 0, ten


def test_nhanh_B_gan_id_khac_cho_nguoi_khong_phai_benh_nhan():
    ra, _ = pb.tu_json([js("dị ứng penicillin", chu_the="mẹ")])
    assert ra[0].chu_the_id != 0


def test_nhanh_C_dung_bang_thuc_the_that():
    ht = ("Bác sĩ: Nhà mình có ai dị ứng thuốc không ạ?\n"
          "Người nhà: Tôi dị ứng penicillin, còn cháu chưa thấy bị bao giờ.")
    tt = thuc_the.lien_ket(ht)
    bang = pb.bang_ten_tu_thuc_the(tt)
    ra_me, _ = pb.tu_json([js("dị ứng penicillin", chu_the="người nhà", luot=[2])],
                          id_theo_ten=bang)
    ra_tre, _ = pb.tu_json([js("dị ứng thuốc", chu_the="trẻ", luot=[2])],
                           id_theo_ten=bang)
    assert ra_tre[0].chu_the_id == 0
    assert ra_me[0].chu_the_id != 0, "di ung cua nguoi nha bi gan cho benh nhan"


def test_bang_ten_luon_co_cac_cach_goi_benh_nhan():
    """Mo hinh viet chu_the la "tre"; bang thuc the goi no la "benh nhan"."""
    bang = pb.bang_ten_tu_thuc_the(thuc_the.lien_ket("Bệnh nhân: Tôi sốt."))
    for ten in pb.TEN_BENH_NHAN:
        assert bang[ten] == 0


def test_ten_la_khong_co_trong_bang_thi_KHONG_gan_cho_benh_nhan():
    """Doan bu ve phia benh nhan la dung kieu loi du an muon chan."""
    bang = pb.bang_ten_tu_thuc_the(thuc_the.lien_ket("Bệnh nhân: Tôi sốt."))
    ra, _ = pb.tu_json([js("đau lưng", chu_the="ông hàng xóm")], id_theo_ten=bang)
    assert ra[0].chu_the_id != 0


# --------------------------------------------------------------- quan he

def test_quan_he_khong_thanh_None():
    ra, _ = pb.tu_json([js("sốt", quan_he="không")])
    assert ra[0].quan_he is None and ra[0].quan_he_voi is None


def test_quan_he_thieu_quan_he_voi_thi_BO_ban_ghi():
    ra, loi = pb.tu_json([js("sốt", quan_he="đính chính", quan_he_voi=None)])
    assert ra == [] and "quan_he_voi" in loi[0]["ly_do"]


def test_quan_he_giu_nguyen_khi_du_doi():
    ra, _ = pb.tu_json([js("sốt", moc_thoi_gian="4 ngày"),
                        js("sốt", moc_thoi_gian="2 ngày", quan_he="đính chính",
                           quan_he_voi=0, luot=[2])])
    assert ra[1].quan_he == "đính chính" and ra[1].quan_he_voi == 0
    assert ra[0].id == 0 and ra[1].id == 1, "id phai khop chi so ma mo hinh tro toi"


def test_id_lien_tuc_theo_chi_so_goc_ke_ca_khi_co_ban_hong():
    """quan_he_voi tro toi CHI SO trong danh sach cua mo hinh. Neu doi so lai
    khi bo ban hong thi moi quan he tro nham ban ghi khac."""
    ra, loi = pb.tu_json([js("sốt", luot=[]),          # hong, bi bo
                          js("ho khan", luot=[2]),
                          js("hết ho", luot=[3], quan_he="diễn biến", quan_he_voi=1)])
    assert len(loi) == 1
    ids = [p.id for p in ra]
    assert ids == [1, 2], f"id phai giu chi so goc, dang la {ids}"
    assert ra[1].quan_he_voi == 1 and ra[0].id == 1


# ----------------------------------------------------------- chay het duong

def test_chay_het_duong_tu_JSON_den_benh_an():
    from src import cap_nhat, sinh_benh_an
    ht = ("Bác sĩ: Nhà mình có ai dị ứng thuốc không ạ?\n"
          "Người nhà: Tôi dị ứng penicillin, còn cháu chưa thấy bị bao giờ.")
    bang = pb.bang_ten_tu_thuc_the(thuc_the.lien_ket(ht))
    ps, loi = pb.tu_json([
        js("dị ứng penicillin", chu_the="người nhà", luot=[1, 2]),
        js("dị ứng thuốc", chu_the="trẻ", luot=[1, 2], do_chac_chan="chưa ghi nhận"),
    ], nguoi_noi_theo_luot={1: "bác sĩ", 2: "người nhà"}, id_theo_ten=bang)
    assert loi == []
    van, _ = sinh_benh_an.sinh(cap_nhat.ap_luat(ps),
                              ten_chu_the={bang["người nhà"]: "người nhà"})
    assert MUC_NGUOI_KHAC in van and "penicillin" in van.split(MUC_NGUOI_KHAC)[1]
    assert "chưa ghi nhận" in van
    assert "penicillin" not in van.split(MUC_NGUOI_KHAC)[0]
