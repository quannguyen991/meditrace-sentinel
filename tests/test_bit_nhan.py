# -*- coding: utf-8 -*-
"""Test cho phep thu bit nhan nguoi noi."""
from src import bit_nhan

HT = ("Bác sĩ: Cháu có tiền sử dị ứng thuốc gì không ạ?\n"
      "Người nhà: Tôi thì dị ứng penicillin, còn cháu chưa thấy bị bao giờ.\n"
      "Bác sĩ: Cháu sốt mấy hôm rồi chị?")


def test_xoa_het_ten_vai_o_dau_luot():
    ra, _ = bit_nhan.bit(HT)
    assert "Bác sĩ:" not in ra and "Người nhà:" not in ra


def test_cung_mot_vai_thi_cung_mot_nhan():
    """Neu moi luot mot nhan khac thi chinh phep bit da xoa mat thong tin
    'hai luot nay cung mot nguoi' — do la thong tin that, khong phai duong tat."""
    ra, bang = bit_nhan.bit(HT)
    assert len(bang) == 2
    assert ra.count(bang["Bác sĩ"] + ":") == 2


def test_GIU_NGUYEN_noi_dung_tung_chu():
    """Dap an dung phai khong doi. Doi mot chu trong noi dung la phep thu hong."""
    ra, _ = bit_nhan.bit(HT)
    for cau in ("Tôi thì dị ứng penicillin, còn cháu chưa thấy bị bao giờ.",
                "Cháu sốt mấy hôm rồi chị?"):
        assert cau in ra


def test_khong_dung_toi_dau_hai_cham_giua_cau():
    ht = "Bác sĩ: Kết quả thế này: bạch cầu tăng nhẹ."
    ra, bang = bit_nhan.bit(ht)
    assert "bạch cầu tăng nhẹ" in ra and len(bang) == 1


def test_bit_mau_giu_nguyen_dap_an():
    m = {"id": "x", "input": HT, "output": "DỊ ỨNG\n\nMẹ dị ứng penicillin."}
    ra = bit_nhan.bit_mau(m)
    assert ra["output"] == m["output"]
    assert ra["input"] != m["input"]


# ----------------------------------------------------------- nhan trung tinh

def test_nhan_ra_chu_the_chi_la_cai_nhan_chep_lai():
    assert bit_nhan.la_nhan_trung_tinh("Người 2")
    assert bit_nhan.la_nhan_trung_tinh("người 10")


def test_khong_nham_nguoi_nha_la_nhan_trung_tinh():
    assert not bit_nhan.la_nhan_trung_tinh("người nhà")
    assert not bit_nhan.la_nhan_trung_tinh("mẹ")
    assert not bit_nhan.la_nhan_trung_tinh("trẻ")


# --------------------------------------------------------------- doi chieu

def test_dem_dung_so_doi_y():
    goc = [{"noi_dung": "dị ứng penicillin", "chu_the": "mẹ"},
           {"noi_dung": "sốt", "chu_the": "trẻ"}]
    bit = [{"noi_dung": "dị ứng penicillin", "chu_the": "Người 2"},
           {"noi_dung": "sốt", "chu_the": "trẻ"}]
    kq = bit_nhan.doi_chieu(goc, bit)
    assert kq["so_khop_noi_dung"] == 2
    assert kq["so_doi_y"] == 1
    assert kq["so_chu_the_la_nhan"] == 1


def test_ghep_theo_NOI_DUNG_chu_khong_theo_thu_tu():
    """Hai lan chay co the trich ra so phat bieu khac nhau. Ghep theo thu tu
    se bao 'doi y' o nhung cho that ra chi la lech mot o."""
    goc = [{"noi_dung": "sốt", "chu_the": "trẻ"},
           {"noi_dung": "ho", "chu_the": "trẻ"}]
    bit = [{"noi_dung": "quấy khóc", "chu_the": "trẻ"},
           {"noi_dung": "sốt", "chu_the": "trẻ"},
           {"noi_dung": "ho", "chu_the": "trẻ"}]
    kq = bit_nhan.doi_chieu(goc, bit)
    assert kq["so_khop_noi_dung"] == 2 and kq["so_doi_y"] == 0


def test_phat_bieu_khong_khop_noi_dung_thi_khong_dem():
    goc = [{"noi_dung": "sốt", "chu_the": "trẻ"}]
    bit = [{"noi_dung": "ho", "chu_the": "mẹ"}]
    kq = bit_nhan.doi_chieu(goc, bit)
    assert kq["so_khop_noi_dung"] == 0 and kq["so_doi_y"] == 0
