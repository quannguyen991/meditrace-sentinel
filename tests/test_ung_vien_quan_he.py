# -*- coding: utf-8 -*-
"""Test cho tang sinh cap ung vien quan he.

Ly do tang nay ton tai: tren 35 hoi thoai that, mo hinh danh dau `quan_he` o
0/282 phat bieu. Khong phai vi hoi thoai khong co quan he — 21/35 hoi thoai co
moc kieu "hom qua... hom nay...". Mo hinh don gian la khong tu khoi phat.

Nen doi vai: CHUONG TRINH liet ke cap dang ngo, mo hinh (hoac luat) chi phai
tra loi mot cau hoi bon lua chon tren mot cap ngan.
"""
import pytest

from src import ung_vien_quan_he as uv
from src.phat_bieu import PhatBieu


def pb(id, noi_dung, chu_the_id=0, moc=None, phu_dinh=False,
       chac="chắc chắn", thoi_diem="hiện tại", luot=None):
    return PhatBieu(id=id, nguoi_noi="người nhà", chu_the_id=chu_the_id,
                    noi_dung=noi_dung, bang_chung=luot or [1],
                    moc_thoi_gian=moc, phu_dinh=phu_dinh,
                    do_chac_chan=chac, thoi_gian_su_kien=thoi_diem)


# --------------------------------------------------------------- bat duoc cap

def test_dinh_chinh_cung_noi_dung_khac_moc_thi_thanh_cap():
    """'dau bung 5 ngay' roi '... a khong, 3 ngay' — phai ra mot cap."""
    ds = [pb(0, "đau bụng", moc="5 ngày"), pb(1, "đau bụng", moc="3 ngày")]
    cap = uv.sinh_cap(ds)
    assert len(cap) == 1
    assert (cap[0].a, cap[0].b) == (0, 1)
    assert "khác mốc" in cap[0].ly_do


def test_dien_bien_khac_phu_dinh_thi_thanh_cap():
    """'hom qua non' / 'hom nay het non' — khac ca moc lan phu dinh."""
    ds = [pb(0, "nôn", moc="hôm qua"), pb(1, "nôn", moc="hôm nay", phu_dinh=True)]
    cap = uv.sinh_cap(ds)
    assert len(cap) == 1
    assert "khác phủ định" in cap[0].ly_do


def test_khac_do_chac_chan_thi_thanh_cap():
    ds = [pb(0, "dị ứng thuốc", chac="chưa ghi nhận"),
          pb(1, "dị ứng thuốc", chac="chắc chắn")]
    assert len(uv.sinh_cap(ds)) == 1


# ------------------------------------------------------- KHONG bat nham cai gi

def test_khac_chu_the_thi_khong_thanh_cap():
    """Loi nguy hiem nhat cua du an la tron chu the. Tang nay khong duoc tao ra no."""
    ds = [pb(0, "dị ứng penicillin", chu_the_id=1, moc="lâu rồi"),
          pb(1, "dị ứng penicillin", chu_the_id=0, moc="chưa rõ")]
    assert uv.sinh_cap(ds) == []


def test_danh_sach_song_song_khong_no_ra_thanh_cap():
    """Bay that gap o train_1299: sau muc 'nguy co ...' liet ke song song.

    Chung deu cung chu the va deu chia chu 'nguy co' — phep do tho se sinh
    ra 15 cap rac. Nguong giao phai du cao de loai het.
    """
    ten = ["nguy cơ nhiễm trùng", "nguy cơ chảy máu", "nguy cơ hỏng dụng cụ",
           "nguy cơ bó bột bị chật", "nguy cơ phải tháo dụng cụ"]
    ds = [pb(i, t, moc=f"lần {i}") for i, t in enumerate(ten)]
    assert uv.sinh_cap(ds) == []


def test_trung_lap_hoan_toan_khong_phai_quan_he():
    """Hai ban ghi giong het, khong truong nao khac — do la trung lap khi trich,
    khong phai quan he. Phai tra ve o danh sach RIENG."""
    ds = [pb(0, "phẫu thuật"), pb(1, "phẫu thuật")]
    assert uv.sinh_cap(ds) == []
    assert len(uv.sinh_cap_trung_lap(ds)) == 1


def test_hai_noi_dung_khac_han_khong_thanh_cap():
    ds = [pb(0, "sốt cao", moc="hôm qua"), pb(1, "đau bụng", moc="hôm nay")]
    assert uv.sinh_cap(ds) == []


# ---------------------------------------------------- goi y quan he bang luat

def test_luat_doc_ra_dinh_chinh_tu_dau_hieu_trong_loi_thoai():
    """'a khong' la dau hieu dinh chinh — nam trong VAN BAN, khong nam trong truong."""
    ds = [pb(0, "đau bụng", moc="5 ngày", luot=[2]),
          pb(1, "đau bụng", moc="3 ngày", luot=[2])]
    luot = {2: "5 ngày ạ… à không, hôm kia mới bắt đầu, vậy là 3 ngày."}
    cap = uv.sinh_cap(ds, luot_thoai=luot)
    assert uv.goi_y_bang_luat(cap[0], ds, luot) == "đính chính"


def test_luat_doc_ra_dien_bien_khi_hai_moc_deu_dung():
    ds = [pb(0, "nôn", moc="hôm qua", luot=[2]),
          pb(1, "nôn", moc="hôm nay", phu_dinh=True, luot=[2])]
    luot = {2: "Hôm qua cháu nôn, hôm nay thì hết rồi ạ."}
    cap = uv.sinh_cap(ds, luot_thoai=luot)
    assert uv.goi_y_bang_luat(cap[0], ds, luot) == "diễn biến"


def test_luat_KHONG_goi_dien_bien_la_dinh_chinh():
    """Loi de mac nhat cua ca du an. Co test rieng vi no dat den the."""
    ds = [pb(0, "sốt", moc="hôm qua", luot=[4]),
          pb(1, "sốt", moc="hôm nay", phu_dinh=True, luot=[4])]
    luot = {4: "Hôm qua cháu sốt, hôm nay đỡ rồi ạ."}
    cap = uv.sinh_cap(ds, luot_thoai=luot)
    assert uv.goi_y_bang_luat(cap[0], ds, luot) != "đính chính"


def test_khong_co_dau_hieu_gi_thi_luat_tra_ve_None_chu_khong_doan():
    """Luat khong duoc doan bua. Khong biet thi noi khong biet, de mo hinh phan."""
    ds = [pb(0, "ho", chac="nghi ngờ"), pb(1, "ho", chac="chắc chắn")]
    cap = uv.sinh_cap(ds)
    assert uv.goi_y_bang_luat(cap[0], ds, {}) is None


# ------------------------------------------------------------- ap ket qua phan

def test_ap_phan_quyet_gan_dung_truong_quan_he():
    ds = [pb(0, "đau bụng", moc="5 ngày"), pb(1, "đau bụng", moc="3 ngày")]
    cap = uv.sinh_cap(ds)
    moi = uv.ap_phan_quyet(ds, {(0, 1): "đính chính"})
    assert moi[1].quan_he == "đính chính" and moi[1].quan_he_voi == 0
    assert moi[0].quan_he is None, "ban ghi truoc khong duoc gan quan he"


def test_ap_phan_quyet_bo_qua_gia_tri_khong_hop_le():
    """Mo hinh tra ve rac thi bo, khong duoc lam vo ca danh sach."""
    ds = [pb(0, "đau bụng", moc="5 ngày"), pb(1, "đau bụng", moc="3 ngày")]
    moi = uv.ap_phan_quyet(ds, {(0, 1): "linh tinh"})
    assert moi[1].quan_he is None


def test_ap_phan_quyet_khong_sua_ban_goc():
    ds = [pb(0, "đau bụng", moc="5 ngày"), pb(1, "đau bụng", moc="3 ngày")]
    uv.ap_phan_quyet(ds, {(0, 1): "đính chính"})
    assert ds[1].quan_he is None


def test_khong_gan_quan_he_thanh_vong():
    """a->b va b->a cung luc se lam luat cap nhat quanh mai. Phai chan."""
    ds = [pb(0, "đau bụng", moc="5 ngày"), pb(1, "đau bụng", moc="3 ngày")]
    moi = uv.ap_phan_quyet(ds, {(0, 1): "đính chính", (1, 0): "đính chính"})
    co_quan_he = [p for p in moi if p.quan_he is not None]
    assert len(co_quan_he) == 1


# ------------------------------------------------------------------ gioi han

def test_gioi_han_so_cap_moi_hoi_thoai():
    """Hoi thoai 28 luot co the sinh ra rat nhieu cap. Phai cat, va phai BAO
    la da cat chu khong im lang."""
    ds = [pb(i, "đau bụng", moc=f"{i} ngày") for i in range(12)]
    cap = uv.sinh_cap(ds, toi_da=10)
    assert len(cap) == 10
    assert uv.da_bi_cat(ds, toi_da=10) is True


def test_cap_co_dau_hieu_dinh_chinh_duoc_GIU_khi_phai_cat():
    """Bo sot mot cap dinh chinh gay hai nhat: benh an se giu lai con so ma
    chinh nguoi noi da tu nhan la sai. Nen khi phai cat, no phai song."""
    ds = [pb(i, "đau bụng", moc=f"{i} ngày", luot=[1]) for i in range(6)]
    ds.append(pb(6, "đau bụng", moc="2 ngày", luot=[9]))
    luot = {9: "5 ngày ạ… à không, 2 ngày thôi."}

    cap = uv.sinh_cap(ds, luot_thoai=luot, toi_da=3)
    assert any(6 in (c.a, c.b) for c in cap), "cap co dinh chinh bi cat mat"
    assert "có dấu hiệu đính chính" in cap[0].ly_do


def test_luot_thoai_khong_lam_doi_TAP_cap_ung_vien():
    """No chi doi thu tu uu tien. Do vet cua buoc liet ke phai la tinh chat
    cau truc, khong phu thuoc vao viec co truyen loi thoai vao hay khong."""
    ds = [pb(0, "đau bụng", moc="5 ngày", luot=[2]),
          pb(1, "đau bụng", moc="3 ngày", luot=[2])]
    luot = {2: "5 ngày ạ… à không, 3 ngày."}
    assert {c.khoa() for c in uv.sinh_cap(ds)} == \
        {c.khoa() for c in uv.sinh_cap(ds, luot_thoai=luot)}
