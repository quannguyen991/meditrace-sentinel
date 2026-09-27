# -*- coding: utf-8 -*-
"""Test phep do chat luong khau trich.

Phep do nay quyet dinh ket luan cua ca thi nghiem huan luyen, nen no phai
duoc test hai chieu: bao dung khi trich dung, bao sai khi trich sai.
"""
from src import do_trich as dt


def md(noi_dung, chu_the="bệnh nhân"):
    return {"noi_dung": noi_dung, "chu_the": chu_the}


# ------------------------------------------------------------ do giong

def test_giong_nhau_hoan_toan():
    assert dt.do_giong("ho có đờm", "ho có đờm") == 1.0


def test_giong_mot_phan_van_ghep_duoc():
    assert dt.do_giong("ho có đờm nhiều", "ho có đờm") >= dt.NGUONG_GHEP


def test_khac_han_thi_khong_ghep():
    assert dt.do_giong("ho có đờm", "đau đầu") < dt.NGUONG_GHEP


def test_rong_thi_khong_ghep():
    assert dt.do_giong("", "ho") == 0.0


# --------------------------------------------------------------- ghep

def test_moi_ben_chi_dung_MOT_lan():
    """Mot ban trich dung khong duoc che nhieu ban dap an."""
    dap_an = [md("ho có đờm"), md("ho có đờm nhiều")]
    trich = [md("ho có đờm")]
    cap, thieu, thua = dt.ghep(dap_an, trich)
    assert len(cap) == 1 and len(thieu) == 1 and thua == []


def test_ghep_theo_diem_cao_nhat_truoc():
    dap_an = [md("sốt cao"), md("ho có đờm")]
    trich = [md("ho có đờm"), md("sốt cao")]
    cap, thieu, thua = dt.ghep(dap_an, trich)
    assert len(cap) == 2 and not thieu and not thua
    for d, t, _ in cap:
        assert d["noi_dung"] == t["noi_dung"]


def test_trich_thua_duoc_dem_rieng():
    cap, thieu, thua = dt.ghep([md("ho")], [md("ho"), md("đau bụng dữ dội")])
    assert len(cap) == 1 and len(thua) == 1


# ------------------------------------------------------------ cung nguoi

def test_cac_cach_goi_benh_nhan_deu_la_MOT_nguoi():
    for a in ("bệnh nhân", "trẻ", "bé", "cháu"):
        for b in ("bệnh nhân", "trẻ", "bé", "cháu"):
            assert dt.cung_nguoi(a, b), f"{a} vs {b}"


def test_nguoi_nha_KHONG_phai_benh_nhan():
    assert not dt.cung_nguoi("bệnh nhân", "mẹ")
    assert not dt.cung_nguoi("mẹ", "trẻ")


def test_hai_nguoi_nha_khac_nhau_van_phai_khop_dung_ten():
    assert dt.cung_nguoi("mẹ", "mẹ")
    assert not dt.cung_nguoi("mẹ", "bà nội")


# ---------------------------------------------------------------- cham

def test_trich_dung_het_thi_100_phan_tram():
    dap_an = [md("ho có đờm"), md("dị ứng penicillin", "mẹ")]
    k = dt.cham([(dap_an, list(dap_an))])
    assert k["ty_le_tim_thay"] == 1.0
    assert k["ty_le_dung_chu_the"] == 1.0
    assert k["khac_bn_ty_le_dung"] == 1.0


def test_gan_sai_chu_the_bi_bat():
    """Chieu quan trong nhat: dung noi dung nhung sai nguoi."""
    dap_an = [md("dị ứng penicillin", "mẹ")]
    trich = [md("dị ứng penicillin", "bệnh nhân")]
    k = dt.cham([(dap_an, trich)])
    assert k["ty_le_tim_thay"] == 1.0, "noi dung dung thi van phai ghep duoc"
    assert k["ty_le_dung_chu_the"] == 0.0
    assert k["khac_bn_dung"] == 0
    assert k["loi"][0]["khac_benh_nhan"] is True


def test_menh_de_KHAC_BENH_NHAN_duoc_dem_RIENG():
    """2,8% menh de khac benh nhan la toan bo phan do quy gan. Gop chung thi
    97% menh de de gan se che mat no."""
    dap_an = [md("ho"), md("sốt"), md("dị ứng", "mẹ")]
    trich = [md("ho"), md("sốt"), md("dị ứng", "bệnh nhân")]
    k = dt.cham([(dap_an, trich)])
    assert k["ty_le_dung_chu_the"] > 0.6, "gop chung thi trong nhu van tot"
    assert k["khac_bn_ty_le_dung"] == 0.0, "tach ra moi thay hong hoan toan"


def test_bo_sot_khong_bi_tinh_la_gan_sai():
    """Bo sot khac gan sai. Gop lam mot la che mat mot trong hai."""
    dap_an = [md("ho"), md("sốt")]
    k = dt.cham([(dap_an, [md("ho")])])
    assert k["ty_le_tim_thay"] == 0.5
    assert k["ty_le_dung_chu_the"] == 1.0


def test_khong_trich_duoc_gi_thi_khong_chia_cho_khong():
    k = dt.cham([([md("ho")], [])])
    assert k["ty_le_tim_thay"] == 0.0
    assert k["ty_le_dung_chu_the"] == 0.0
