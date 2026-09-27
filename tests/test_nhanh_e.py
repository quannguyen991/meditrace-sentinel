# -*- coding: utf-8 -*-
"""Test nhanh E — ghep ban nhap cua A voi bang phat bieu.

Cai phai giu: E khong duoc AM THAM lam hong ban nhap tot. `ty_le_giu` la con
so chan viec do, va no phai dem dung.
"""
from src import nhanh_e


def a(ma, van):
    return {"id": ma, "input": "1. Bác sĩ: Cháu sao ạ?\n2. Người nhà: Cháu ho.",
            "tham_chieu": "LÝ DO KHÁM BỆNH\n\nHo.", "du_doan": van,
            "so_luot_goi": 1, "token_vao": 10, "token_ra": 5}


def tho(ma, ps):
    return {"id": ma, "so_luot": 2, "json_hop_le": True, "ly_do": "",
            "phat_bieu": ps, "tho": ""}


PS = [{"chu_the": "trẻ", "noi_dung": "ho", "do_chac_chan": "chắc chắn",
       "phu_dinh": False, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại",
       "moc_thoi_gian": None, "quan_he": "không", "quan_he_voi": None,
       "luot_thoai": [1, 2]}]

VAN_A = "LÝ DO KHÁM BỆNH\n\nHo.\n\nBỆNH SỬ HIỆN TẠI\n\nTrẻ ho từ hôm qua."


def test_khong_goi_mo_hinh():
    """E chay tu hai tep da sinh san. Neu no can GPU thi no khong the la buoc
    lap nhanh."""
    ra = nhanh_e.chay_E([a("m1", VAN_A)], [tho("m1", PS)])
    assert len(ra) == 1 and ra[0]["ban_nhap_A"] == VAN_A


def test_giu_lai_ban_nhap_A_de_doi_chieu():
    ra = nhanh_e.chay_E([a("m1", VAN_A)], [tho("m1", PS)])
    assert ra[0]["ban_nhap_A"] == VAN_A
    assert "du_doan" in ra[0] and "du_doan_khong_muc_phu" in ra[0]


def test_ty_le_giu_dem_dung():
    ra = nhanh_e.chay_E([a("m1", VAN_A)], [tho("m1", PS)])
    t = nhanh_e.ty_le_giu(ra)
    assert t["ky_tu_goc"] == len(VAN_A)
    assert t["so_ban"] == 1


def test_tat_ca_hai_co_che_thi_khong_sua_gi():
    ra = nhanh_e.chay_E([a("m1", VAN_A)], [tho("m1", PS)],
                        bo_sung=False, sua=False)
    assert ra[0]["du_doan"] == VAN_A
    assert ra[0]["da_sua"] == [] and ra[0]["da_bo_sung"] == []


def test_mau_khong_co_trong_tep_trich_van_chay_duoc():
    """Thieu ban trich thi giu nguyen ban cua A, khong duoc nem."""
    ra = nhanh_e.chay_E([a("m1", VAN_A)], [])
    assert len(ra) == 1 and ra[0]["so_phat_bieu"] == 0


def test_sua_cuc_bo_PHA_van_xuoi_cua_A_khi_menh_de_khong_khop_nguyen_van():
    """Ghi lai gioi han that thanh test.

    `sua_cuc_bo` doi menh de xuat hien NGUYEN VAN trong cau. A viet van xuoi
    nen phan lon khong khop, va bi xep la "khong co nguon". Tren tap phat
    trien: 240/282 cau bi day xuong muc phu, diem tut 0.6216 -> 0.3502.
    """
    van = "BỆNH SỬ HIỆN TẠI\n\nBé được mẹ đưa tới khám vì tình trạng hô hấp."
    ps = [dict(PS[0], noi_dung="viêm phổi")]
    ra = nhanh_e.chay_E([a("m1", van)], [tho("m1", ps)])
    assert any(s["loi"] == "khong_co_nguon" for s in ra[0]["da_sua"])
