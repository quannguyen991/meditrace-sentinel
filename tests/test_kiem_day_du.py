# -*- coding: utf-8 -*-
"""Test do do day du.

Trong tam theo ke hoach (Task 16 buoc 1): bo sung KHI CO bang chung, va
KHONG bo sung khi khong co. Cai thu hai quan trong hon — mot co che "bo sung"
khong co chan se tu bia ra muc kham.
"""
from src import kiem_day_du as kdd
from src import sinh_benh_an as sba


def pb(noi_dung, id=1, chu_the_id=0, **kw):
    d = {"id": id, "chu_the_id": chu_the_id, "noi_dung": noi_dung,
         "bang_chung": [1], "do_chac_chan": "chắc chắn", "phu_dinh": False,
         "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại",
         "trang_thai": "còn hiệu lực", "moc_thoi_gian": None}
    d.update(kw)
    return d


# --------------------------------------------------------------- doi chieu

def test_nhan_ra_noi_dung_da_the_hien():
    ps = [pb("ho khan")]
    van, _ = sba.sinh(ps)
    k = kdd.doi_chieu(ps, van)
    assert k["da_the_hien"] == [1] and k["bo_sot"] == []


def test_nhan_ra_noi_dung_bi_bo_sot():
    ps = [pb("ho khan", id=1), pb("sốt", id=2)]
    van, _ = sba.sinh([ps[0]])          # sinh THIEU ban ghi 2
    k = kdd.doi_chieu(ps, van)
    assert k["bo_sot"] == [2]


def test_ban_bi_thay_the_khong_duoc_dem_vao_BAT_KY_nhom_nao():
    """Ban cu bi thay the KHONG duoc vao benh an — vang mat la dung.

    Phai kiem CA BON nhom, khong chi hai. Ban dau test nay chi kiem `bo_sot`
    va `da_the_hien`, va no van xanh khi bo han phep loc trang thai: ban cu
    roi vao `can_xac_nhan` nen hai o kia van rong. Test khong bat duoc gi.
    """
    ps = [pb("sốt", id=1, moc_thoi_gian="4 ngày", trang_thai="bị thay thế"),
          pb("sốt", id=2, moc_thoi_gian="2 ngày")]
    van, _ = sba.sinh(ps)
    k = kdd.doi_chieu(ps, van)
    for nhom in ("bo_sot", "da_the_hien", "can_xac_nhan", "lap"):
        assert 1 not in k[nhom], f"ban bi thay the bi dem vao {nhom}"
    assert k["da_the_hien"] == [2]


def test_phat_bieu_o_muc_can_xac_nhan_duoc_tinh_rieng():
    ps = [pb("khó thở", tinh_huong="giả định")]
    van, _ = sba.sinh(ps)
    k = kdd.doi_chieu(ps, van)
    assert k["can_xac_nhan"] == [1] and k["bo_sot"] == []


def test_so_khop_chan_ca_hai_ranh_gioi_tu():
    """Cung cai bay da lam hong phep cham chan doan: "ho" khop vao duoi "cho"."""
    assert kdd._co_trong("ho", "cho uống hạ sốt") is False
    assert kdd._co_trong("ho", "trẻ ho nhiều") is True


def test_khong_bao_da_the_hien_nham_vi_khop_trong_long_tu():
    ps = [pb("ho")]
    k = kdd.doi_chieu(ps, "BỆNH SỬ HIỆN TẠI\n\ncho uống hạ sốt.")
    assert k["bo_sot"] == [1], "bao 'da the hien' cho noi dung chua he xuat hien"


# ----------------------------------------------------------------- bo sung

def test_bo_sung_KHI_CO_bang_chung_trong_bang():
    ps = [pb("ho khan", id=1), pb("sốt", id=2)]
    van, _ = sba.sinh([ps[0]])
    moi, da_them = kdd.bo_sung(ps, van)
    assert da_them == [2]
    assert "sốt" in moi and "ho khan" in moi


def test_KHONG_bo_sung_thu_khong_co_trong_bang():
    """Chan quan trong nhat: co che bo sung khong duoc tu them muc kham
    hay ket qua ma hoi thoai chua cung cap."""
    ps = [pb("ho khan")]
    van, _ = sba.sinh(ps)
    moi, da_them = kdd.bo_sung(ps, van)
    assert da_them == []
    assert moi == van, "da sua ban nhap du khong thieu gi"
    for tu in ("xét nghiệm", "X-quang", "khám phổi", "công thức máu"):
        assert tu not in moi


def test_bo_sung_giu_nguyen_muc_do_chac_chan():
    ps = [pb("ho khan", id=1),
          pb("dị ứng thuốc", id=2, do_chac_chan="chưa ghi nhận")]
    van, _ = sba.sinh([ps[0]])
    moi, _ = kdd.bo_sung(ps, van)
    assert "chưa ghi nhận dị ứng thuốc" in moi
    assert "không dị ứng" not in moi


def test_bo_sung_dat_dung_muc():
    ps = [pb("ho khan", id=1), pb("dị ứng amoxicillin", id=2)]
    van, _ = sba.sinh([ps[0]])
    moi, _ = kdd.bo_sung(ps, van)
    assert "DỊ ỨNG" in moi and "amoxicillin" in moi.split("DỊ ỨNG")[1]


def test_bo_sung_khong_dua_di_ung_cua_nguoi_nha_vao_muc_benh_nhan():
    ps = [pb("ho khan", id=1), pb("dị ứng penicillin", id=2, chu_the_id=1)]
    van, _ = sba.sinh([ps[0]])
    moi, _ = kdd.bo_sung(ps, van, ten_chu_the={1: "mẹ"})
    assert sba.MUC_NGUOI_KHAC in moi
    assert "penicillin" not in moi.split(sba.MUC_NGUOI_KHAC)[0]


def test_bo_sung_roi_thi_khong_con_bo_sot():
    ps = [pb("ho khan", id=1), pb("sốt", id=2), pb("nôn", id=3)]
    van, _ = sba.sinh([ps[0]])
    moi, _ = kdd.bo_sung(ps, van)
    assert kdd.doi_chieu(ps, moi)["bo_sot"] == []


# ------------------------------------------------------------------ ty le

def test_bo_sung_KHONG_them_lai_thu_da_co():
    """Neu bo sung khong loc theo `bo_sot` thi moi noi dung bi ghi hai lan."""
    ps = [pb("ho khan", id=1), pb("sốt", id=2)]
    van, _ = sba.sinh(ps)                       # sinh DU ca hai
    moi, da_them = kdd.bo_sung(ps, van)
    assert da_them == [] and moi == van
    # "ho khan" xuat hien HAI lan la dung: LY DO KHAM BENH nhac lai trieu
    # chung chinh. Cai phai giu la ban nhap KHONG DOI sau khi bo sung.
    assert moi.count("ho khan") == van.count("ho khan")
    assert kdd.doi_chieu(ps, moi)["lap"] == [], "bao lap oan cho trieu chung chinh"


def test_ty_le_day_du_dem_dung_mau_so():
    ps = [pb("ho khan", id=1), pb("sốt", id=2)]
    van, _ = sba.sinh([ps[0]])
    t = kdd.ty_le(ps, van)
    assert t["con_hieu_luc"] == 2 and t["bo_sot"] == 1
    assert abs(t["ty_le_day_du"] - 0.5) < 1e-9


def test_ty_le_tra_None_khi_khong_co_phat_bieu_nao():
    assert kdd.ty_le([], "") is None
