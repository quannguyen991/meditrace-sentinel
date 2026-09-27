# -*- coding: utf-8 -*-
"""Test bo sinh benh an.

Hai luat duoi day la LY DO buoc nay viet bang ma chu khong bang mo hinh.
Neu chung khong duoc test thi khong co gi giu chung.
"""
from src import sinh_benh_an as sba


def pb(noi_dung, chu_the_id=0, **kw):
    d = {"id": kw.pop("id", 1), "chu_the_id": chu_the_id, "noi_dung": noi_dung,
         "bang_chung": [1], "do_chac_chan": "chắc chắn", "phu_dinh": False,
         "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại",
         "trang_thai": "còn hiệu lực", "moc_thoi_gian": None}
    d.update(kw)
    return d


# ------------------------------------------------- LUAT 1: chu the khong tron

def test_di_ung_cua_me_vao_muc_gia_dinh():
    """Test nay o trong ke hoach. No la cot loi cua du an."""
    ra, _ = sba.sinh([pb("dị ứng penicillin", chu_the_id=1),
                      pb("dị ứng thuốc", do_chac_chan="chưa ghi nhận")],
                     ten_chu_the={1: "mẹ"})
    assert sba.MUC_NGUOI_KHAC in ra
    muc_gia_dinh = ra.split(sba.MUC_NGUOI_KHAC)[1]
    assert "penicillin" in muc_gia_dinh


def test_di_ung_cua_me_KHONG_vao_muc_di_ung_cua_benh_nhan():
    """Chieu nguoc lai — cai that su phai chan."""
    ra, _ = sba.sinh([pb("dị ứng penicillin", chu_the_id=1)], ten_chu_the={1: "mẹ"})
    assert "penicillin" not in ra.split(sba.MUC_NGUOI_KHAC)[0]


def test_muc_gia_dinh_noi_ro_la_cua_ai():
    ra, _ = sba.sinh([pb("dị ứng penicillin", chu_the_id=1)], ten_chu_the={1: "mẹ"})
    assert "mẹ:" in ra


def test_di_ung_cua_chinh_benh_nhan_van_vao_muc_di_ung():
    ra, _ = sba.sinh([pb("dị ứng amoxicillin", chu_the_id=0)])
    assert "DỊ ỨNG" in ra and "amoxicillin" in ra.split("DỊ ỨNG")[1]


# --------------------------------------- LUAT 2: chua ghi nhan khong thanh khong

def test_khong_bien_chua_ghi_nhan_thanh_khong_co():
    """Test nay o trong ke hoach.

    "Chua thay bi bao gio" la mot cho TRONG. "Khong di ung" la mot khang dinh AM.
    Doi cai thu nhat thanh cai thu hai la bia ra mot ket luan lam sang.
    """
    ra, _ = sba.sinh([pb("dị ứng thuốc", do_chac_chan="chưa ghi nhận")])
    thap = ra.lower()
    assert "chưa ghi nhận" in thap
    assert "không dị ứng" not in thap


def test_ba_muc_do_chac_chan_ra_ba_cach_dien_dat_khac_nhau():
    chac = sba.dien_dat(pb("sốt"))
    chac_phu_dinh = sba.dien_dat(pb("sốt", phu_dinh=True))
    nghi = sba.dien_dat(pb("sốt", do_chac_chan="nghi ngờ"))
    chua = sba.dien_dat(pb("sốt", do_chac_chan="chưa ghi nhận"))
    assert chac == "sốt"
    assert chac_phu_dinh == "không sốt"
    assert nghi == "nghi ngờ sốt"
    assert chua == "chưa ghi nhận sốt"
    assert len({chac, chac_phu_dinh, nghi, chua}) == 4


def test_chua_ghi_nhan_bo_qua_phu_dinh():
    """"Chua thay bi bao gio" da la cho trong roi, khong phai phu dinh chong len."""
    assert sba.dien_dat(pb("sốt", do_chac_chan="chưa ghi nhận", phu_dinh=True)) \
        == "chưa ghi nhận sốt"


# ------------------------------------------------------------ chuyen huong

def test_gia_dinh_xuong_muc_can_xac_nhan_chu_khong_bi_vut():
    ra, gc = sba.sinh([pb("uống hạ sốt", tinh_huong="giả định")])
    assert "CẦN XÁC NHẬN" in ra and "hạ sốt" in ra
    assert gc[0]["ly_do"] == "câu giả định, chưa xảy ra"


def test_gia_dinh_khong_vao_benh_su_hien_tai():
    ra, _ = sba.sinh([pb("khó thở", tinh_huong="giả định")])
    assert "BỆNH SỬ HIỆN TẠI" not in ra


def test_ban_bi_thay_the_khong_vao_benh_an():
    ra, gc = sba.sinh([pb("sốt", moc_thoi_gian="4 ngày", trang_thai="bị thay thế"),
                       pb("sốt", moc_thoi_gian="2 ngày", id=2)])
    hien_tai = ra.split("BỆNH SỬ HIỆN TẠI")[1].split("CẦN XÁC NHẬN")[0]
    assert "2 ngày" in hien_tai and "4 ngày" not in hien_tai


def test_thieu_bang_chung_xuong_can_xac_nhan():
    ra, gc = sba.sinh([pb("sốt", bang_chung=[])])
    assert gc[0]["muc"] == "CẦN XÁC NHẬN"
    assert gc[0]["ly_do"] == "không có bằng chứng lượt thoại"


def test_ke_hoach_vao_muc_ke_hoach_dieu_tri():
    ra, _ = sba.sinh([pb("uống kháng sinh 5 ngày", tinh_huong="kế hoạch")])
    assert "KẾ HOẠCH ĐIỀU TRỊ" in ra and "kháng sinh" in ra


# ------------------------------------------------------------- bang tra muc

def test_qua_khu_vao_tien_su_benh_hien_tai_vao_benh_su():
    ra, _ = sba.sinh([pb("viêm phổi", thoi_gian_su_kien="quá khứ"),
                      pb("ho khan", thoi_gian_su_kien="hiện tại", id=2)])
    assert "viêm phổi" in ra.split("TIỀN SỬ BỆNH")[1]
    assert "ho khan" in ra.split("BỆNH SỬ HIỆN TẠI")[1].split("TIỀN SỬ BỆNH")[0]


def test_tiem_chung_va_phau_thuat_tach_muc():
    ra, _ = sba.sinh([pb("đã tiêm chủng đủ mũi"),
                      pb("mổ ruột thừa năm ngoái", thoi_gian_su_kien="quá khứ", id=2)])
    assert "TIÊM CHỦNG" in ra and "TIỀN SỬ PHẪU THUẬT" in ra


def test_khong_sinh_muc_rong():
    """Quy tac 3 cua loi nhac goc: khong tao muc trong."""
    ra, _ = sba.sinh([pb("ho khan")])
    for muc in ("DỊ ỨNG", "TIÊM CHỦNG", sba.MUC_NGUOI_KHAC, "CẦN XÁC NHẬN"):
        assert muc not in ra


def test_thu_tu_muc_theo_benh_an_khong_theo_thu_tu_phat_bieu():
    ra, _ = sba.sinh([pb("dị ứng amoxicillin"),
                      pb("ho khan", id=2)])
    assert ra.index("BỆNH SỬ HIỆN TẠI") < ra.index("DỊ ỨNG")


# ------------------------------------------------------------------ ghi chu

def test_ghi_chu_truy_nguoc_duoc_tung_phat_bieu():
    """Task 16 do do day du bang ghi chu nay — no phai co bang chung."""
    _, gc = sba.sinh([pb("ho khan", bang_chung=[3, 4])])
    assert gc[0]["bang_chung"] == [3, 4]
    assert gc[0]["muc"] == "BỆNH SỬ HIỆN TẠI"


def test_moc_thoi_gian_duoc_giu_nguyen_van():
    ra, _ = sba.sinh([pb("sốt", moc_thoi_gian="2 ngày")])
    assert "2 ngày" in ra


def test_khong_gop_hai_phat_bieu_khac_chu_the_thanh_mot_cum():
    """Cho thong tin troi tu nguoi nay sang nguoi kia. Moi phat bieu mot cum."""
    _, gc = sba.sinh([pb("dị ứng penicillin", chu_the_id=1),
                      pb("sốt", chu_the_id=0, id=2)], ten_chu_the={1: "mẹ"})
    assert len(gc) == 2
    assert {g["muc"] for g in gc} == {sba.MUC_NGUOI_KHAC, "BỆNH SỬ HIỆN TẠI"}


# ------------------------------------------------------------- muc phu

def test_tach_muc_phu_ra_khoi_benh_an():
    ra, _ = sba.sinh([pb("ho khan", id=1),
                      pb("khó thở", id=2, tinh_huong="giả định")])
    than, phu = sba.tach_muc_phu(ra)
    assert "CẦN XÁC NHẬN" not in than
    assert "khó thở" in phu and "khó thở" not in than
    assert "ho khan" in than


def test_muc_phu_lam_bo_cham_dem_them_mot_muc_KHONG_co_trong_tham_chieu():
    """Ly do `tach_muc_phu` ton tai — kiem bang chinh bo cham goc."""
    from src import cham_diem

    ra, _ = sba.sinh([pb("ho khan", id=1),
                      pb("khó thở", id=2, tinh_huong="giả định")])
    than, _ = sba.tach_muc_phu(ra)
    assert "CẦN XÁC NHẬN" in cham_diem.cac_muc(ra)
    assert "CẦN XÁC NHẬN" not in cham_diem.cac_muc(than)


def test_khong_co_muc_phu_thi_tra_nguyen_van():
    ra, _ = sba.sinh([pb("ho khan")])
    than, phu = sba.tach_muc_phu(ra)
    assert than == ra and phu == ""


def test_cac_muc_con_lai_deu_duoc_bo_cham_nhan_ra():
    """Neu bo cham khong nhan ra muc nao thi Section F1 bang 0 vi mot ly do
    hinh thuc, khong phai vi noi dung."""
    from src import cham_diem
    for muc in sba.THU_TU_MUC:
        assert muc in cham_diem.cac_muc(muc + "\n\nnội dung."), muc


def test_phat_bieu_co_chu_the_la_BAC_SI_khong_thanh_tien_su_gia_dinh():
    """Bac si khong phai chu the lam sang. "Bac si: kho khai thac them thong
    tin benh su" khong phai tien su cua bac si.

    Da xay ra that tren tap phat trien: 16 phat bieu co chu the la bac si bi
    day vao muc tien su gia dinh, vua sai nghia vua sinh ra muc thua."""
    ra, gc = sba.sinh([pb("khó khai thác thêm thông tin", chu_the_id=2,
                          ten_chu_the="bác sĩ")], ten_chu_the={2: "bác sĩ"})
    assert sba.MUC_NGUOI_KHAC not in ra
    assert gc[0]["muc"] == "CẦN XÁC NHẬN"
    assert "nhân viên y tế" in gc[0]["ly_do"]


def test_nguoi_nha_VAN_vao_tien_su_gia_dinh():
    """Chieu nguoc lai — khong duoc chan nham nguoi nha."""
    ra, _ = sba.sinh([pb("dị ứng penicillin", chu_the_id=1,
                         ten_chu_the="người nhà")], ten_chu_the={1: "mẹ"})
    assert sba.MUC_NGUOI_KHAC in ra and "penicillin" in ra
