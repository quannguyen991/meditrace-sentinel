# -*- coding: utf-8 -*-
"""Canh phien ban bo cham 2026-09-22: ma loi thoi gian, ba ma con cua sai_muc,
phu dinh o dau cau, va loi ghep cheo hai ban cung noi dung khac phu dinh."""
from src import cham_he_thong as ch


def _d(noi_dung, **kw):
    x = {"chu_the": "bệnh nhân", "noi_dung": noi_dung, "luot": [2],
         "muc": "BỆNH SỬ HIỆN TẠI", "do_chac_chan": "chắc chắn", "phu_dinh": False,
         "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại",
         "moc_thoi_gian": None, "trang_thai": "còn hiệu lực"}
    x.update(kw)
    return x


def _p(i, noi_dung, **kw):
    x = {"id": i, "noi_dung": noi_dung, "chu_the_id": 0, "bang_chung": [2],
         "do_chac_chan": "chắc chắn", "phu_dinh": False, "tinh_huong": "thực tế",
         "thoi_gian_su_kien": "hiện tại", "moc_thoi_gian": None}
    x.update(kw)
    return x


def _loi(da, ps):
    ra, _bo = ch.loi_phat_bieu({"id": "x", "dap_an": da}, ps)
    return {i: set(ds) for i, (ds, _l) in ra.items()}


def test_hai_ban_giong_het_chi_khac_phu_dinh_ghep_dung_cap():
    """Hai ban giong het ca noi dung, moc va luot, chi khac phu dinh; he thong viet
    dung ca hai theo thu tu nguoc. Pha the hoa bang phu dinh -> 0 loi.
    (Ca dct_030_A tung bi nghi la truong hop nay; kiem lai thi hai ban khac MOC
    thoi gian va mo hinh dao phu dinh THAT — xem phep thu ngay duoi.)"""
    da = [_d("da xanh", phu_dinh=False), _d("da xanh", phu_dinh=True)]
    ps = [_p(0, "da xanh", phu_dinh=True), _p(1, "da xanh", phu_dinh=False)]
    loi = _loi(da, ps)
    assert loi[0] == set() and loi[1] == set(), loi


def test_khong_o_dau_cau_bang_co_phu_dinh():
    """'không sốt' khong co co phu dinh = 'sốt' co co phu dinh. Khong phai loi."""
    loi = _loi([_d("sốt", phu_dinh=True)], [_p(0, "không sốt", phu_dinh=False)])
    assert "sai_muc" not in loi[0], loi


def test_dao_phu_dinh_that_la_loi_va_co_ma_con():
    loi = _loi([_d("ho", phu_dinh=True)], [_p(0, "ho", phu_dinh=False)])
    assert {"sai_muc", "sai_muc_phu_dinh"} <= loi[0]
    assert "sai_muc_chac_chan" not in loi[0]


def test_nghi_ngo_ghi_thanh_chac_chan_co_ma_con_chac_chan():
    loi = _loi([_d("viêm phổi", do_chac_chan="nghi ngờ")],
               [_p(0, "viêm phổi", do_chac_chan="chắc chắn")])
    assert {"sai_muc", "sai_muc_chac_chan"} <= loi[0]


def test_ke_hoach_ghi_thanh_thuc_te_co_ma_con_tinh_huong():
    loi = _loi([_d("chụp X-quang", tinh_huong="kế hoạch")],
               [_p(0, "chụp X-quang", tinh_huong="thực tế")])
    assert {"sai_muc", "sai_muc_tinh_huong"} <= loi[0]


def test_ma_con_KHONG_nam_trong_LOI_nen_khong_dem_hai_lan():
    assert not set(ch.MA_CON_MUC) & set(ch.LOI)
    assert ch._co_loi(["sai_muc_chac_chan"]) is False


def test_qua_khu_ghi_thanh_hien_tai_la_loi_thoi_gian():
    loi = _loi([_d("viêm khớp", thoi_gian_su_kien="quá khứ")],
               [_p(0, "viêm khớp", thoi_gian_su_kien="hiện tại")])
    assert "sai_thoi_gian" in loi[0]


def test_chua_ro_o_mot_ben_KHONG_la_loi_thoi_gian():
    loi = _loi([_d("táo bón", thoi_gian_su_kien="chưa rõ")],
               [_p(0, "táo bón", thoi_gian_su_kien="hiện tại")])
    assert "sai_thoi_gian" not in loi[0]


def test_hai_moc_thoi_gian_mau_thuan_la_loi():
    loi = _loi([_d("ợ nóng", moc_thoi_gian="từ năm ngoái")],
               [_p(0, "ợ nóng", moc_thoi_gian="hai tháng nay")])
    assert "sai_thoi_gian" in loi[0]


def test_thieu_moc_o_mot_ben_KHONG_la_loi():
    loi = _loi([_d("ợ nóng", moc_thoi_gian="hai tháng nay")], [_p(0, "ợ nóng")])
    assert "sai_thoi_gian" not in loi[0]


def test_sai_thoi_gian_la_loi_that_tinh_vao_so_dung():
    assert "sai_thoi_gian" in ch.LOI
    assert ch._co_loi(["sai_thoi_gian"]) is True


def test_phien_ban_bo_cham_duoc_ghi():
    assert ch.PHIEN_BAN == "2026-09-22"
    ten = {t for t, _tu, _mau in ch.BANG}
    assert {"sai_thoi_gian_tren_ghep", "sai_muc_phu_dinh_tren_ghep"} <= ten


def test_dao_phu_dinh_theo_hai_moc_cua_mot_dien_bien_la_hai_loi_that():
    """dct_030_A: 'da xanh tu tuan truoc' (co) va 'hom kia' (het). Mo hinh viet nguoc
    ca hai. Ghep theo moc thoi gian la dung, nen hai loi phu dinh la loi THAT."""
    da = [_d("da xanh", phu_dinh=False, moc_thoi_gian="từ tuần trước"),
          _d("da xanh", phu_dinh=True, moc_thoi_gian="hôm kia")]
    ps = [_p(0, "da xanh", phu_dinh=True, moc_thoi_gian="từ tuần trước"),
          _p(1, "da xanh", phu_dinh=False, moc_thoi_gian="hôm kia")]
    loi = _loi(da, ps)
    assert "sai_muc_phu_dinh" in loi[0] and "sai_muc_phu_dinh" in loi[1], loi
