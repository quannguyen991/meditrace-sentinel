# -*- coding: utf-8 -*-
"""Kiểm thử tự động cho Cơ sở Tri thức Phương ngữ Lâm sàng 3 Miền Toàn diện."""

from src.phuong_ngu_lam_sang import ClinicalDialectEngine


def test_chuan_hoa_phuong_ngu_nam_bo():
    cau_noi = (
        "Dạ tôi bị đau bao tử với sưng hai cái giò từ bữa hổm, người cứ lừ đừ, có bữa bị xỉu luôn."
    )
    kq = ClinicalDialectEngine.phan_tich_va_chuan_hoa(cau_noi)

    # Đã phát hiện đúng các thực thể phương ngữ Nam Bộ
    tu_phat_hien = [p.tu_goc.lower() for p in kq.danh_sach_phat_hien]
    assert "bao tử" in tu_phat_hien
    assert "hai cái giò" in tu_phat_hien or "giò" in tu_phat_hien
    assert "lừ đừ" in tu_phat_hien
    assert "xỉu" in tu_phat_hien
    assert "bữa hổm" in tu_phat_hien

    # Văn bản chuẩn hóa được quy về thuật ngữ y khoa chính quy
    vb_chuan = kq.van_ban_chuan_hoa.lower()
    assert "dạ dày" in vb_chuan
    assert "chi dưới" in vb_chuan
    assert "mệt mỏi li bì" in vb_chuan
    assert "ngất" in vb_chuan


def test_chuan_hoa_phuong_ngu_trung_bo():
    cau_noi = (
        "Bụng dưới nó cứ trằn xuống, đi tiểu thấy thốn dữ dội, đầu nhức bưng óc từ hôm tê đến chừ."
    )
    kq = ClinicalDialectEngine.phan_tich_va_chuan_hoa(cau_noi)

    tu_phat_hien = [p.tu_goc.lower() for p in kq.danh_sach_phat_hien]
    assert "trằn xuống" in tu_phat_hien or "trằn" in tu_phat_hien
    assert "thốn" in tu_phat_hien
    assert "nhức bưng óc" in tu_phat_hien
    assert "hôm tê" in tu_phat_hien
    assert "chừ" in tu_phat_hien

    vb_chuan = kq.van_ban_chuan_hoa.lower()
    assert "nặng tức" in vb_chuan
    assert "đau nhói buốt" in vb_chuan
    assert "đau đầu dữ dội" in vb_chuan
    assert "hôm kia" in vb_chuan
    assert "bây giờ" in vb_chuan


def test_chuan_hoa_phuong_ngu_bac_bo():
    cau_noi = (
        "Mấy hôm nay người cứ ngầy ngật, hâm hấp sốt, đầu váng đầu và bụng dạ đầy ách khó chịu."
    )
    kq = ClinicalDialectEngine.phan_tich_va_chuan_hoa(cau_noi)

    tu_phat_hien = [p.tu_goc.lower() for p in kq.danh_sach_phat_hien]
    assert "ngầy ngật" in tu_phat_hien
    assert "hâm hấp sốt" in tu_phat_hien or "hâm hấp" in tu_phat_hien
    assert "váng đầu" in tu_phat_hien
    assert "đầy ách" in tu_phat_hien

    vb_chuan = kq.van_ban_chuan_hoa.lower()
    assert "mệt mỏi sốt nhẹ" in vb_chuan
    assert "sốt nhẹ" in vb_chuan
    assert "nặng đầu" in vb_chuan
    assert "chướng bụng khó tiêu" in vb_chuan


def test_phan_giai_tu_mo_ho_om():
    # 1. 'ốm' trong ngữ cảnh miền Bắc (bị ốm, đau ốm)
    cau_bac = "Tôi bị ốm liệt giường ba ngày nay rồi bác sĩ."
    kq_bac = ClinicalDialectEngine.phan_tich_va_chuan_hoa(cau_bac)
    assert any(p.thuat_ngu_chuan == "bị bệnh" for p in kq_bac.danh_sach_phat_hien)

    # 2. 'ốm' trong ngữ cảnh miền Nam (ốm nhom, gầy ốm)
    cau_nam = "Dạo này ăn không ngon nên người ốm nhom ốm teo."
    kq_nam = ClinicalDialectEngine.phan_tich_va_chuan_hoa(cau_nam)
    assert any(p.thuat_ngu_chuan == "gầy sụt cân" for p in kq_nam.danh_sach_phat_hien)


def test_phan_giai_tu_mo_ho_mo_ac():
    # 1. Trẻ sơ sinh -> Thóp trước
    cau_nhi = "Bé hai tháng tuổi vùng mỏ ác thấy hơi phồng."
    kq_nhi = ClinicalDialectEngine.phan_tich_va_chuan_hoa(cau_nhi)
    assert any("thóp trước" in p.thuat_ngu_chuan for p in kq_nhi.danh_sach_phat_hien)

    # 2. Người lớn -> Thượng vị
    cau_lon = "Bác bị đau thắt chỗ mỏ ác sau khi ăn đồ cay."
    kq_lon = ClinicalDialectEngine.phan_tich_va_chuan_hoa(cau_lon)
    assert any("thượng vị" in p.thuat_ngu_chuan for p in kq_lon.danh_sach_phat_hien)


def test_phan_giai_tu_mo_ho_hong():
    # 1. Vị trí giải phẫu: đau hông
    cau_gp = "Tôi bị đau hông bên phải lan ra sau lưng."
    kq_gp = ClinicalDialectEngine.phan_tich_va_chuan_hoa(cau_gp)
    assert any(p.thuat_ngu_chuan == "vùng hông" for p in kq_gp.danh_sach_phat_hien)

    # 2. Phủ định: hông có sốt
    cau_pd = "Tôi hông có bị sốt đâu bác sĩ."
    kq_pd = ClinicalDialectEngine.phan_tich_va_chuan_hoa(cau_pd)
    assert any(p.thuat_ngu_chuan == "không" for p in kq_pd.danh_sach_phat_hien)
