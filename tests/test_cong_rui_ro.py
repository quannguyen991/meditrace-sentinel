# -*- coding: utf-8 -*-
"""Cong rui ro: DANH DAU va XEP THU TU, khong tu chan."""
from src import cong_rui_ro as cr
from src import khoa_bang_chung as kbc
from src.phat_bieu import PhatBieu

HT = ("Bác sĩ: Cháu có dị ứng thuốc gì không?\n"
      "Người nhà: Dạ, dị ứng penicillin ạ.\n"
      "Bác sĩ: Cháu có ho không?\n"
      "Người nhà: Dạ, có ho ạ.\n"
      "Người nhà: Tôi thì bị tăng huyết áp.")


def pb(id_, noi_dung, luot, trich, chu_the_id=0, **kw):
    return PhatBieu(id=id_, nguoi_noi="người nhà", chu_the_id=chu_the_id,
                    noi_dung=noi_dung, bang_chung=luot, trich_dan=trich, **kw)


def _cham(ps):
    return cr.cham(ps, kbc.khoa_ca(ps, HT)["ket_qua"])


def test_di_ung_THIEU_can_cu_la_NGUY_CO_CAO():
    """"Da, di ung penicillin a" khong co tu chi nguoi — chu the chi suy tu nguoi
    noi. Voi di ung, chung ay la du de bac si duyet truoc."""
    dg = _cham([pb(0, "dị ứng penicillin", [2], ["dị ứng penicillin ạ"])])
    assert dg[0].loai == "di_ung" and dg[0].nhom == cr.NGUY_CO_CAO


def test_trieu_chung_it_quan_trong_cung_canh_bao_do_KHONG_cao():
    dg = _cham([pb(0, "ho", [4], ["có ho ạ"])])
    # 22/09/2026: co canh bao ma diem thap la "rủi ro thấp", khong con la "đã kiểm chứng"
    assert dg[0].nhom == cr.RUI_RO_THAP and dg[0].ly_do


def test_bi_chan_chi_den_tu_KHOA():
    """Tang rui ro khong tu chan: phat bieu qua khoa khong bao gio vao nhom bi
    chan, du diem cao den dau."""
    ps = [pb(0, "dị ứng penicillin", [2], ["dị ứng penicillin ạ"])]
    kq = kbc.khoa_ca(ps, HT)["ket_qua"]
    assert kq[0].qua and cr.cham(ps, kq)[0].nhom != cr.BI_CHAN


def test_thu_tu_duyet_BI_CHAN_truoc_roi_NGUY_CO_CAO():
    ps = [pb(0, "ho", [4], ["có ho ạ"]),
          pb(1, "dị ứng penicillin", [2], ["dị ứng penicillin ạ"]),
          # doi chu the bang "toi" -> khoa chan
          pb(2, "tăng huyết áp", [5], ["Tôi thì bị tăng huyết áp"])]
    thu_tu = [d.id for d in cr.thu_tu_duyet(_cham(ps))]
    assert thu_tu == [2, 1, 0]


def test_cach_C_di_ung_co_canh_bao_sang_can_xac_nhan():
    """Cach C (22/09/2026): di ung co canh bao -> CẦN XÁC NHẬN, kem ly do."""
    dg = _cham([pb(0, "dị ứng penicillin", [2], ["dị ứng penicillin ạ"])])
    ra = cr.dua_sang_xac_nhan(dg)
    assert 0 in ra and ra[0].startswith("cảnh báo ở thông tin dị ứng")


def test_cach_C_trieu_chung_co_canh_bao_o_lai_than():
    dg = _cham([pb(0, "ho", [4], ["có ho ạ"])])
    assert cr.dua_sang_xac_nhan(dg) == {}


def test_khong_canh_bao_thi_van_la_da_kiem_chung():
    dg = [cr.DanhGia(0, "khac", 0.3, 0.0, 0.0, cr.DA_KIEM_CHUNG, [])]
    assert cr.dua_sang_xac_nhan(dg) == {}
