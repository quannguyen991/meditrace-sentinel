# -*- coding: utf-8 -*-
"""Test sua cuc bo.

Hai test dau lay tu ke hoach (Task 17 buoc 1). Cai quan trong nhat la
`test_sua_khong_lam_hong_cau_dung`: mot co che sua tu dong lam hong cau von
dung thi te hon la khong sua gi.
"""
from src import sua_cuc_bo
from src.sinh_benh_an import MUC_NGUOI_KHAC


def pb(noi_dung, chu_the_id=0, **kw):
    d = {"id": kw.pop("id", 1), "chu_the_id": chu_the_id, "noi_dung": noi_dung,
         "bang_chung": [1], "do_chac_chan": "chắc chắn", "phu_dinh": False,
         "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại",
         "trang_thai": "còn hiệu lực", "moc_thoi_gian": None}
    d.update(kw)
    return d


def cac_cau(van_ban):
    return {c.strip() for k in (van_ban or "").split("\n\n")
            for c in k.split(".") if c.strip() and not c.strip().isupper()}


# --------------------------------------------------- hai test trong ke hoach

def test_sua_khong_lam_hong_cau_dung():
    """Cau co nguon dung phai con nguyen sau khi sua cau khac."""
    bang = [pb("ho khan", id=1), pb("sốt", id=2)]
    nhap = "BỆNH SỬ HIỆN TẠI\n\nho khan. sốt. đã dùng paracetamol."
    ket = sua_cuc_bo.sua(nhap, bang)
    con = cac_cau(ket.van_ban)
    assert "ho khan" in con and "sốt" in con
    assert "đã dùng paracetamol" not in con


def test_gioi_han_so_vong():
    bang = [pb("ho khan")]
    nhap = "BỆNH SỬ HIỆN TẠI\n\nx. y. z. t. u."
    assert sua_cuc_bo.sua(nhap, bang, max_vong=3).so_vong <= 3


# ------------------------------------------------------ bon phep kiem

def test_cau_khong_co_nguon_bi_CHUYEN_chu_khong_bi_XOA():
    """Xoa la mat thong tin ma khong ai biet. Chuyen thi bac si con doc duoc."""
    ket = sua_cuc_bo.sua("BỆNH SỬ HIỆN TẠI\n\nđã dùng paracetamol.",
                         [pb("ho khan")])
    assert "paracetamol" in ket.van_ban
    assert "CẦN XÁC NHẬN" in ket.van_ban
    assert ket.da_sua[0]["loi"] == "khong_co_nguon"


def test_vi_du_trong_ke_hoach_ten_thuoc_chua_xac_dinh():
    """Hoi thoai: "chua nho ro ten thuoc". Ban nhap: "da dung paracetamol"."""
    bang = [pb("đã dùng thuốc", do_chac_chan="chắc chắn")]
    ket = sua_cuc_bo.sua("BỆNH SỬ HIỆN TẠI\n\nđã dùng paracetamol.", bang)
    than = ket.van_ban.split("CẦN XÁC NHẬN")[0]
    assert "paracetamol" not in than, "giu mot ten thuoc khong co trong hoi thoai"


def test_cau_dung_ban_bi_thay_the_bi_BO():
    """Chuyen xuong muc phu la noi lai mot thong tin da bi dinh chinh."""
    bang = [pb("sốt 4 ngày", id=1, trang_thai="bị thay thế"),
            pb("sốt 2 ngày", id=2)]
    ket = sua_cuc_bo.sua("BỆNH SỬ HIỆN TẠI\n\nsốt 4 ngày. sốt 2 ngày.", bang)
    assert "4 ngày" not in ket.van_ban
    assert "sốt 2 ngày" in ket.van_ban
    assert any(s["loi"] == "dung_ban_bi_thay_the" for s in ket.da_sua)


def test_them_muc_chac_chan_bi_ha_lai():
    bang = [pb("dị ứng thuốc", do_chac_chan="chưa ghi nhận")]
    ket = sua_cuc_bo.sua("DỊ ỨNG\n\ndị ứng thuốc.", bang)
    assert "chưa ghi nhận dị ứng thuốc" in ket.van_ban


def test_cau_da_co_hedge_thi_khong_sua_nua():
    """Neu khong dung thi moi vong lai them mot lan "chua ghi nhan"."""
    bang = [pb("dị ứng thuốc", do_chac_chan="chưa ghi nhận")]
    ket = sua_cuc_bo.sua("DỊ ỨNG\n\nchưa ghi nhận dị ứng thuốc.", bang)
    assert ket.van_ban.count("chưa ghi nhận") == 1
    assert ket.da_sua == []


def test_thong_tin_cua_nguoi_khac_duoc_chuyen_sang_muc_gia_dinh():
    bang = [pb("dị ứng penicillin", chu_the_id=1)]
    ket = sua_cuc_bo.sua("DỊ ỨNG\n\ndị ứng penicillin.", bang,
                         ten_chu_the={1: "mẹ"})
    assert MUC_NGUOI_KHAC in ket.van_ban
    assert "penicillin" not in ket.van_ban.split(MUC_NGUOI_KHAC)[0]
    assert "mẹ:" in ket.van_ban


def test_thong_tin_cua_benh_nhan_KHONG_bi_chuyen_di():
    """Chieu nguoc lai — chuyen nham cung la lam hong."""
    bang = [pb("dị ứng amoxicillin", chu_the_id=0)]
    ket = sua_cuc_bo.sua("DỊ ỨNG\n\ndị ứng amoxicillin.", bang)
    assert MUC_NGUOI_KHAC not in ket.van_ban
    assert ket.da_sua == []


# ------------------------------------------------------------ tinh on dinh

def test_ban_nhap_dung_hoan_toan_thi_khong_sua_gi():
    bang = [pb("ho khan", id=1), pb("sốt", id=2)]
    nhap = "BỆNH SỬ HIỆN TẠI\n\nho khan. sốt."
    ket = sua_cuc_bo.sua(nhap, bang)
    assert ket.da_sua == [] and ket.so_vong == 1
    assert cac_cau(ket.van_ban) == cac_cau(nhap)


def test_chay_hai_lan_ra_cung_ket_qua():
    """Khong on dinh thi so do duoc phu thuoc vao so vong, khong phai vao du lieu."""
    bang = [pb("ho khan", id=1), pb("dị ứng thuốc", id=2,
                                    do_chac_chan="chưa ghi nhận")]
    nhap = "BỆNH SỬ HIỆN TẠI\n\nho khan.\n\nDỊ ỨNG\n\ndị ứng thuốc."
    mot = sua_cuc_bo.sua(nhap, bang).van_ban
    hai = sua_cuc_bo.sua(mot, bang).van_ban
    assert mot == hai


def test_con_ngo_ghi_lai_cho_chua_xac_minh_duoc():
    ket = sua_cuc_bo.sua("BỆNH SỬ HIỆN TẠI\n\nđã chụp X-quang phổi.",
                         [pb("ho khan")])
    assert ket.con_ngo and "X-quang" in ket.con_ngo[0]


def test_tren_ban_nhap_do_sinh_benh_an_sinh_ra_thi_gan_nhu_khong_sua_gi():
    """Gioi han da biet cua co che nay — ghi lai bang test, khong giau.

    Khau sinh da ap dung dung nhung luat ma khau sua di tim, nen sua cuc bo
    tren dau ra cua C khong tao ra chenh lech. Gia tri cua no nam o ban nhap
    do MO HINH viet.
    """
    from src import sinh_benh_an
    bang = [pb("ho khan", id=1), pb("dị ứng penicillin", id=2, chu_the_id=1)]
    van, _ = sinh_benh_an.sinh(bang, ten_chu_the={1: "mẹ"})
    ket = sua_cuc_bo.sua(van, bang, ten_chu_the={1: "mẹ"})
    assert ket.da_sua == [], f"le ra khong co gi de sua, nhung: {ket.da_sua}"


def test_khong_dan_tien_to_ten_hai_lan():
    """Cau tu `sinh_benh_an` da co san "<ten>: ". Da xay ra that tren tap phat
    trien: "bác sĩ: bác sĩ: khó khai thác thêm..."."""
    bang = [pb("khó khai thác thêm thông tin", chu_the_id=2)]
    ket = sua_cuc_bo.sua("KẾ HOẠCH ĐIỀU TRỊ\n\nbác sĩ: khó khai thác thêm thông tin.",
                         bang, ten_chu_the={2: "bác sĩ"})
    assert "bác sĩ: bác sĩ:" not in ket.van_ban
    assert ket.van_ban.count("bác sĩ:") == 1


def test_van_dan_tien_to_khi_cau_chua_co():
    bang = [pb("dị ứng penicillin", chu_the_id=1)]
    ket = sua_cuc_bo.sua("DỊ ỨNG\n\ndị ứng penicillin.", bang,
                         ten_chu_the={1: "mẹ"})
    assert "mẹ: dị ứng penicillin" in ket.van_ban
