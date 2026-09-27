# -*- coding: utf-8 -*-
"""Doi chung theo luat kieu ConText cho truc chu the.

Ba viec tep nay chot:
  1. Tu chi nguoi nha lam doi chu the sang nguoi do.
  2. KICH HOAT GIA: cung tu do trong vai nguoi dua di kham hay nguoi ke thi KHONG
     doi chu the — "mẹ đưa cháu đi khám" van la thong tin cua benh nhan. Thieu bo
     phan nay thi moi cau nguoi nha ke ho deu bi gan sai.
  3. Bang tu chon tu VAI NGUOI NHA cua bo sinh, khong chon bang cach nhin tap danh
     gia. Mot bang tu chon tu chinh tap danh gia cho ra con so cao gia.
"""
from src import context_vi as cv
from src import doi_chung_tam_thuong as dc
from src import ngu_lieu_viet as nl


def test_tu_chi_nguoi_nha_doi_chu_the():
    assert cv.chu_the_cua("mẹ em bị tiểu đường") == 1
    assert cv.chu_the_cua("bà ngoại dị ứng penicillin") == 1


def test_khong_co_tu_chi_nguoi_nha_thi_la_benh_nhan():
    assert cv.chu_the_cua("cháu sốt hai ngày nay") == 0
    assert cv.chu_the_cua("ho nhiều về đêm") == 0


def test_kich_hoat_gia_nguoi_dua_di_kham_va_nguoi_ke():
    assert cv.chu_the_cua("mẹ đưa cháu đi khám") == 0
    assert cv.chu_the_cua("bà kể là cháu ho từ hôm qua") == 0
    assert cv.chu_the_cua("bố cho cháu uống hạ sốt rồi") == 0


def test_lien_tu_doi_lap_ket_thuc_pham_vi():
    """Doi chu the giua chung cau — dung cho bo thach thuc doi chu the nham vao."""
    cau = "bà ngoại thì dị ứng penicillin, còn cháu chưa bị bao giờ"
    assert cv.chu_the_cua(cau) == 1
    assert [pv for pv, _tu, _gia in cv.giai_thich(cau)] == [
        "bà ngoại thì dị ứng penicillin", "cháu chưa bị bao giờ"]


def test_giai_thich_chi_ro_tu_kich_hoat_va_kich_hoat_gia():
    assert cv.giai_thich("mẹ đưa cháu đi khám")[0][1:] == ("mẹ", True)
    assert cv.giai_thich("mẹ bị tiểu đường")[0][1:] == ("mẹ", False)


def test_bang_tu_lay_tu_vai_nguoi_nha_cua_bo_sinh():
    """Moi vai nguoi nha ma bo sinh dung deu phai co trong bang — thieu mot vai la
    doi chung yeu gia, va doi chung yeu gia lam duong ong trong tot hon thuc te."""
    vai = set(nl.VAI_NU) | set(nl.VAI_NAM)
    thieu = [v for v in vai if v not in cv.TU_NGUOI_NHA]
    assert not thieu, thieu


def test_duong_context_co_trong_danh_sach_doi_chung():
    assert "context" in dc.DUONG


def test_duong_context_gan_dung_nguoi_tren_mot_hoi_thoai_ngan():
    hoi_thoai = ("Bác sĩ: Cháu sao ạ?\n"
                 "Người nhà: Dạ cháu sốt hai ngày nay ạ.\n"
                 "Bác sĩ: Nhà mình có ai bị hen không ạ?\n"
                 "Người nhà: Dạ bố cháu bị hen ạ.")
    van, ghi_chu, so = dc.sinh_ban_nhap(hoi_thoai, duong="context")
    assert so >= 2
    assert "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI" in van, van
    # Menh de "bo chau bi hen" phai mang ten nguoi, khong duoc nam tron trong muc
    # cua benh nhan.
    assert "hen" in van and "bố" in van.lower()
