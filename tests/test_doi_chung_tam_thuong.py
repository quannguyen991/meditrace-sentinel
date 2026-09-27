# -*- coding: utf-8 -*-
"""Hai duong tat khong dung mo hinh, va mot san duoi day du.

VI SAO CAN. Tai lieu cua du an da viet nhieu lan rang "mot he thong chi gan
trieu chung cho nguoi vua noi van dat do chinh xac cao". Cau do LAP LUAN chu
khong DO — khong co cau hinh nao chay duong tat do, nen khong co so de tra loi
nguoi cham.

DIEU HAI DUONG TAT PHAI THE HIEN: chung sai o HAI TANG DOI NHAU.

    tang 3  nguoi nha ke HO benh nhan    -> `nguoi_noi` sai,  `benh_nhan` dung
    tang 4  nguoi nha ke VE CHINH MINH   -> `nguoi_noi` dung, `benh_nhan` sai

Do duoc tren 60 ca bo 3.000: tang 4 thi `benh_nhan` dat 14,29%, tang 3 thi
`benh_nhan` dat 99,31%. Day la bang chung rang hai tang do thuc su doi nhau,
khong phai hai cach goi cua mot thu.
"""
import pytest

from src import doi_chung_tam_thuong as dc

HOI_THOAI = "\n".join([
    "Bác sĩ: Cháu bị sao ạ?",
    "Người nhà: Dạ cháu sốt hai hôm rồi ạ.",
    "Người nhà: Tôi thì dị ứng penicillin, còn cháu chưa thấy bị.",
    "Bác sĩ: Họng hơi đỏ, không có ban.",
])


def test_tach_luot_dem_tu_1():
    luot = dc.tach_luot(HOI_THOAI)
    assert luot[0] == (1, "Bác sĩ", "Cháu bị sao ạ?")
    assert luot[1][0] == 2 and luot[1][1] == "Người nhà"


def test_bo_tieu_tu_LAP_cho_den_het():
    """"Vang a, toi sot" bo mot lan con "a, toi sot" — phai lap."""
    assert dc._gon("Vâng ạ, tôi sốt ba hôm rồi") == "tôi sốt ba hôm"
    assert dc._gon("Dạ thì cháu đau họng ạ") == "cháu đau họng"


def test_bo_cau_giao_tiep():
    """San duoi co cau "toi cam on bac si" la san YEU GIA."""
    md = dc.menh_de_bang_luat("Bệnh nhân: Tôi cảm ơn bác sĩ nhiều.")
    assert md == []


def test_tach_o_cum_chuyen_y():
    """"Toi thi X, CON chau thi Y" la hai chu the — phai tach."""
    md = dc.menh_de_bang_luat("Người nhà: Tôi thì dị ứng penicillin, "
                              "còn cháu chưa thấy bị.")
    assert len(md) == 2


def test_mac_dinh_BO_luot_bac_si():
    md = dc.menh_de_bang_luat(HOI_THOAI)
    assert all(v != "Bác sĩ" for _s, v, _n in md)


def test_lay_bac_si_thi_lay_KET_QUA_KHAM_khong_lay_CAU_HOI():
    md = dc.menh_de_bang_luat(HOI_THOAI, lay_bac_si=True)
    cua_bs = [n for _s, v, n in md if v == "Bác sĩ"]
    assert any("họng" in n.lower() for n in cua_bs)
    assert not any("bị sao" in n.lower() for n in cua_bs)


# ------------------------------------------- hai duong tat doi nhau

def test_duong_NGUOI_NOI_gan_nguoi_nha_cho_cau_tu_ke_ve_minh():
    van, _gc, _n = dc.sinh_ban_nhap(HOI_THOAI, "nguoi_noi")
    assert "người nhà" in van.lower()


def test_duong_BENH_NHAN_gan_het_cho_benh_nhan():
    """Duong nay PHAI sai o tang 4 — do la ly do no ton tai."""
    van, ghi_chu, _n = dc.sinh_ban_nhap(HOI_THOAI, "benh_nhan")
    assert "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI" not in van


def test_duong_day_du_CO_loi_bac_si():
    """Hai duong thuan bo han luot bac si nen bao phu tang bac si chi 4,17% —
    san yeu gia. `day_du` phai co ket qua kham."""
    van, _gc, n = dc.sinh_ban_nhap(HOI_THOAI, "day_du")
    assert "họng" in van.lower()
    assert n > dc.sinh_ban_nhap(HOI_THOAI, "nguoi_noi")[2]


def test_day_du_gan_loi_bac_si_cho_BENH_NHAN():
    """Chinh cho nay `sua_cuc_bo` hieu sai 104 lan: cau bac si noi la thong tin
    VE benh nhan, khong phai thong tin cua bac si."""
    van, ghi_chu, _n = dc.sinh_ban_nhap(HOI_THOAI, "day_du")
    muc_hong = [g["muc"] for g in ghi_chu if "họng" in g["noi_dung"].lower()]
    assert muc_hong and "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI" not in muc_hong


def test_duong_khong_hop_le_thi_dung_han():
    with pytest.raises(SystemExit):
        dc.sinh_ban_nhap(HOI_THOAI, "khong_co_duong_nay")


def test_ba_duong_deu_sinh_duoc_va_dinh_dang_khop_nhanh():
    mau = [{"id": "x1", "input": HOI_THOAI, "output": "BỆNH SỬ HIỆN TẠI\n\nSốt."}]
    for duong in dc.DUONG:
        kq = dc.chay(mau, duong)
        assert len(kq) == 1
        # Phai co du khoa de `sai_so` va `do_dac` cham duoc.
        for khoa in ("id", "input", "tham_chieu", "du_doan", "ghi_chu",
                     "so_phat_bieu", "so_can_xac_nhan", "so_luot_goi"):
            assert khoa in kq[0], (duong, khoa)
        assert kq[0]["so_luot_goi"] == 0, "doi chung nay KHONG duoc goi mo hinh"


# --------------------------- bang tu xung do TU NGU LIEU (10/09/2026)

def test_TU_XUNG_MINH_khong_chua_tu_chi_BENH_NHAN():
    """Loi that, do duoc tren 681 ca. Trong hoi thoai kham benh Viet Nam, nguoi
    nha goi BENH NHAN la "chau"/"con", va benh nhan cao tuoi duoc goi "ba"/"ong":

        chau   ve benh nhan 438   ve chinh minh 5
        con    ve benh nhan 235   ve chinh minh 0
        ba     ve benh nhan  98   ve chinh minh 9
        ong    ve benh nhan  78   ve chinh minh 9

    Giu bon tu nay trong bang lam doi chung sai o dung tang 3 — tang dong nhat
    trong ba tang kho (34% so menh de).
    """
    for tu in ("cháu", "con", "bà", "ông", "em"):
        assert tu not in dc.TU_XUNG_MINH, tu
    for tu in ("tôi", "mẹ", "bố"):
        assert tu in dc.TU_XUNG_MINH, tu


def test_cau_mo_dau_bang_chau_duoc_gan_cho_BENH_NHAN():
    """"chau chua thay bi bao gio" do me noi la ve BENH NHAN, khong ve me."""
    assert not dc._noi_ve_chinh_minh("cháu chưa thấy bị bao giờ")
    assert dc._noi_ve_chinh_minh("tôi thì dị ứng penicillin")


def test_tach_dung_hai_chu_the_trong_MOT_luot():
    """Cau bay kinh dien cua du an: mot luot, hai chu the doi nhau."""
    van = "Người nhà: Tôi thì dị ứng penicillin, còn cháu chưa thấy bị."
    _van, ghi_chu, _n = dc.sinh_ban_nhap(van, "nguoi_noi")
    muc = {g["noi_dung"]: g["muc"] for g in ghi_chu}
    gia_dinh = [n for n, m in muc.items() if "GIA ĐÌNH" in m]
    assert any("penicillin" in n for n in gia_dinh)
    assert not any("chưa thấy bị" in n for n in gia_dinh)
