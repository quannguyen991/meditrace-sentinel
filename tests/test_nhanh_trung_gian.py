# -*- coding: utf-8 -*-
"""Test ba nhanh B / C / C_ghi_de khac nhau DUNG o cho dinh noi.

Neu ba nhanh khac nhau o nhung cho lat vat khac nua thi chenh lech do duoc se
lan lon nguyen nhan, va ca thiet ke doi chung mat gia tri. Nen test o day
kiem tung khac biet mot, tren cung mot dau ra mo hinh gia.
"""
import pytest

from src import bakeoff, nhanh
from src.sinh_benh_an import MUC_NGUOI_KHAC

HT_DIEN_BIEN = ("Bác sĩ: Cháu còn nôn không chị?\n"
                "Người nhà: Hôm qua cháu nôn, hôm nay thì hết rồi ạ.")

PS_DIEN_BIEN = [
    {"chu_the": "trẻ", "noi_dung": "nôn", "do_chac_chan": "chắc chắn",
     "phu_dinh": False, "tinh_huong": "thực tế", "thoi_gian_su_kien": "quá khứ",
     "moc_thoi_gian": "hôm qua", "quan_he": "không", "quan_he_voi": None,
     "luot_thoai": [1, 2]},
    {"chu_the": "trẻ", "noi_dung": "nôn", "do_chac_chan": "chắc chắn",
     "phu_dinh": True, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại",
     "moc_thoi_gian": "hôm nay", "quan_he": "diễn biến", "quan_he_voi": 0,
     "luot_thoai": [2]},
]

HT_CHU_THE = ("Bác sĩ: Nhà mình có ai dị ứng thuốc không ạ?\n"
              "Người nhà: Tôi dị ứng penicillin, còn cháu chưa thấy bị bao giờ.")

PS_CHU_THE = [
    {"chu_the": "người nhà", "noi_dung": "dị ứng penicillin",
     "do_chac_chan": "chắc chắn", "phu_dinh": False, "tinh_huong": "thực tế",
     "thoi_gian_su_kien": "quá khứ", "moc_thoi_gian": None,
     "quan_he": "không", "quan_he_voi": None, "luot_thoai": [1, 2]},
    {"chu_the": "trẻ", "noi_dung": "dị ứng thuốc", "do_chac_chan": "chưa ghi nhận",
     "phu_dinh": False, "tinh_huong": "thực tế", "thoi_gian_su_kien": "quá khứ",
     "moc_thoi_gian": None, "quan_he": "không", "quan_he_voi": None,
     "luot_thoai": [1, 2]},
]


@pytest.fixture
def mo_hinh_gia(monkeypatch):
    """Thay `bakeoff.trich` bang mot ham tra ve JSON dinh san."""
    def dat(ps):
        def _gia(tok, model, prefix_fn, mau_list, max_token=1536, vi_du=True):
            return [{"id": m["id"], "so_luot": 2, "json_hop_le": True,
                     "ly_do": "", "phat_bieu": ps, "tho": ""} for m in mau_list]
        monkeypatch.setattr(bakeoff, "trich", _gia)
    return dat


def mau(ht, ma="m1"):
    return [{"id": ma, "input": ht, "output": ""}]


# --------------------------------------- khac biet 1: luat quan he (C vs C_ghi_de)

def test_C_giu_CA_HAI_moc_cua_dien_bien(mo_hinh_gia, capsys):
    mo_hinh_gia(PS_DIEN_BIEN)
    ra = nhanh.chay_trung_gian(mau(HT_DIEN_BIEN), None, None, None, "C")
    van = ra[0]["du_doan"]
    assert "hôm qua" in van and "hôm nay" in van


def test_C_ghi_de_VUT_MAT_moc_dau_cua_dien_bien(mo_hinh_gia):
    """Day la ly do ton tai cua bang quan he.

    Quy tac "phat bieu sau ghi de phat bieu truoc" khong phan biet duoc
    dinh chinh voi dien bien, nen no vut mat "hom qua co non" — mot su that
    van con dung.
    """
    mo_hinh_gia(PS_DIEN_BIEN)
    ra = nhanh.chay_trung_gian(mau(HT_DIEN_BIEN), None, None, None, "C_ghi_de")
    van = ra[0]["du_doan"]
    assert "hôm nay" in van
    assert "hôm qua" not in van.split("CẦN XÁC NHẬN")[0], \
        "doi chung ghi de le ra phai vut mat moc dau"


def test_C_va_C_ghi_de_khac_nhau_that_su(mo_hinh_gia):
    """Doi chung ma cho ra ket qua y het thi khong doi chung duoc gi."""
    mo_hinh_gia(PS_DIEN_BIEN)
    c = nhanh.chay_trung_gian(mau(HT_DIEN_BIEN), None, None, None, "C")
    mo_hinh_gia(PS_DIEN_BIEN)
    g = nhanh.chay_trung_gian(mau(HT_DIEN_BIEN), None, None, None, "C_ghi_de")
    assert c[0]["du_doan"] != g[0]["du_doan"]


# ----------------------------------------- khac biet 2: lien ket thuc the (B vs C)

def test_C_dua_di_ung_cua_nguoi_nha_vao_muc_gia_dinh(mo_hinh_gia):
    mo_hinh_gia(PS_CHU_THE)
    ra = nhanh.chay_trung_gian(mau(HT_CHU_THE), None, None, None, "C")
    van = ra[0]["du_doan"]
    assert MUC_NGUOI_KHAC in van
    assert "penicillin" in van.split(MUC_NGUOI_KHAC)[1]
    assert "penicillin" not in van.split(MUC_NGUOI_KHAC)[0]


def test_B_khong_ap_luat_nen_ban_bi_thay_the_van_vao_benh_an(mo_hinh_gia):
    """B co bang phat bieu nhung khong co luat cap nhat — do dung la thu B
    duoc thiet ke de KHONG co. Test nay giu cho B khong bi lam manh len."""
    ps = [
        {"chu_the": "trẻ", "noi_dung": "sốt", "do_chac_chan": "chắc chắn",
         "phu_dinh": False, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại",
         "moc_thoi_gian": "4 ngày", "quan_he": "không", "quan_he_voi": None,
         "luot_thoai": [1]},
        {"chu_the": "trẻ", "noi_dung": "sốt", "do_chac_chan": "chắc chắn",
         "phu_dinh": False, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại",
         "moc_thoi_gian": "2 ngày", "quan_he": "đính chính", "quan_he_voi": 0,
         "luot_thoai": [2]},
    ]
    mo_hinh_gia(ps)
    b = nhanh.chay_trung_gian(mau("Bác sĩ: Sốt mấy hôm?\nNgười nhà: 4 ngày, à 2 ngày."),
                              None, None, None, "B")
    mo_hinh_gia(ps)
    c = nhanh.chay_trung_gian(mau("Bác sĩ: Sốt mấy hôm?\nNgười nhà: 4 ngày, à 2 ngày."),
                              None, None, None, "C")
    assert "4 ngày" in b[0]["du_doan"], "B le ra khong ap luat cap nhat"
    hien_tai_C = c[0]["du_doan"].split("CẦN XÁC NHẬN")[0]
    assert "4 ngày" not in hien_tai_C, "C phai danh dau ban cu la bi thay the"


# --------------------------------------------------------------- ghi nhan

def test_ghi_lai_so_phat_bieu_va_ban_ghi_hong(mo_hinh_gia):
    mo_hinh_gia(PS_DIEN_BIEN + [{"chu_the": "trẻ", "noi_dung": "x",
                                 "luot_thoai": []}])
    ra = nhanh.chay_trung_gian(mau(HT_DIEN_BIEN), None, None, None, "C")
    assert ra[0]["so_phat_bieu"] == 2
    assert len(ra[0]["loi_ban_ghi"]) == 1


def test_ghi_chu_truy_nguoc_duoc(mo_hinh_gia):
    mo_hinh_gia(PS_CHU_THE)
    ra = nhanh.chay_trung_gian(mau(HT_CHU_THE), None, None, None, "C")
    assert len(ra[0]["ghi_chu"]) == 2
    assert all(g["bang_chung"] for g in ra[0]["ghi_chu"])


def test_nhanh_khong_hop_le_thi_nem(mo_hinh_gia):
    """"D" tung la ten khong hop le, gio da la mot nhanh that. Dung "E"."""
    mo_hinh_gia(PS_CHU_THE)
    with pytest.raises(AssertionError):
        nhanh.chay_trung_gian(mau(HT_CHU_THE), None, None, None, "E")


def test_luu_ca_ban_co_va_khong_co_muc_phu(mo_hinh_gia):
    """Phai co du hai ban de bao cao ca hai so Section F1."""
    ps = [dict(PS_CHU_THE[0]), dict(PS_CHU_THE[1], tinh_huong="giả định")]
    mo_hinh_gia(ps)
    ra = nhanh.chay_trung_gian(mau(HT_CHU_THE), None, None, None, "C")[0]
    assert "CẦN XÁC NHẬN" in ra["du_doan"]
    assert "CẦN XÁC NHẬN" not in ra["du_doan_khong_muc_phu"]
    assert ra["so_can_xac_nhan"] == 1


def test_khong_giau_duoc_phat_bieu_trong_muc_phu(mo_hinh_gia):
    """Neu day het xuong CAN XAC NHAN thi diem tang gia. So dem nay chan viec do."""
    ps = [dict(p, tinh_huong="giả định") for p in PS_CHU_THE]
    mo_hinh_gia(ps)
    ra = nhanh.chay_trung_gian(mau(HT_CHU_THE), None, None, None, "C")[0]
    assert ra["so_can_xac_nhan"] == 2
    assert ra["du_doan_khong_muc_phu"].strip() == "", "than benh an le ra phai rong"


# ------------------------------------------------------------------ nhanh D

PS_THIEU = [
    {"chu_the": "trẻ", "noi_dung": "ho khan", "do_chac_chan": "chắc chắn",
     "phu_dinh": False, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại",
     "moc_thoi_gian": None, "quan_he": "không", "quan_he_voi": None,
     "luot_thoai": [2]},
    {"chu_the": "trẻ", "noi_dung": "dị ứng thuốc", "do_chac_chan": "chưa ghi nhận",
     "phu_dinh": False, "tinh_huong": "thực tế", "thoi_gian_su_kien": "quá khứ",
     "moc_thoi_gian": None, "quan_he": "không", "quan_he_voi": None,
     "luot_thoai": [2]},
]


def test_D_chay_duoc_va_giu_nguyen_muc_do_chac_chan(mo_hinh_gia):
    mo_hinh_gia(PS_THIEU)
    ra = nhanh.chay_trung_gian(mau(HT_CHU_THE), None, None, None, "D")[0]
    assert "chưa ghi nhận dị ứng thuốc" in ra["du_doan"]
    assert "không dị ứng" not in ra["du_doan"]


def test_D_khong_khac_C_tren_dau_ra_da_dung_luat(mo_hinh_gia):
    """Gioi han da biet, viet thanh test.

    Task 16 va 17 di tim dung nhung luat ma khau sinh da ap dung. Tren dau ra
    cua C chung khong tim thay gi, nen D = C. Neu bao cao trinh bay D hon C
    thi phai chi ra chenh lech den TU DAU — khong the tu hai co che nay.
    """
    mo_hinh_gia(PS_THIEU)
    c = nhanh.chay_trung_gian(mau(HT_CHU_THE), None, None, None, "C")[0]
    mo_hinh_gia(PS_THIEU)
    d = nhanh.chay_trung_gian(mau(HT_CHU_THE), None, None, None, "D")[0]
    assert d["du_doan"] == c["du_doan"]
    assert d["da_bo_sung"] == [] and d["da_sua"] == []


def test_D_ghi_lai_da_bo_sung_va_da_sua(mo_hinh_gia):
    mo_hinh_gia(PS_THIEU)
    ra = nhanh.chay_trung_gian(mau(HT_CHU_THE), None, None, None, "D")[0]
    assert "da_bo_sung" in ra and "da_sua" in ra


# ------------------------------------------------------- boc co che (2x2)

def test_bon_o_cua_bang_boc_co_che_khac_nhau_dung_cho_can_khac(mo_hinh_gia):
    """B / C_khong_luat / C_khong_lien_ket / C la bon o cua 2x2.

    PHAI chon dung ca thu. Ban dau test nay dung `chu_the="người nhà"`, va no
    hong — vi luat chuoi tho cua nhanh B DA xu ly dung ca do ("nguoi nha"
    khong nam trong TEN_BENH_NHAN nen thanh chu the khac). Do la mot phat
    hien that, khong phai loi: LIEN KET THUC THE chi hon luat chuoi khi chu
    the la DAI TU, luc do chuoi khong tu noi len duoc no chi ai.

    Nen ca thu o day la benh nhan nguoi lon tu noi "Tôi dị ứng penicillin",
    va mo hinh ghi `chu_the="tôi"`:
        B  "tôi" khong nam trong TEN_BENH_NHAN -> coi la nguoi khac -> di ung
           cua CHINH benh nhan bi day sang TIEN SU GIA DINH. SAI.
        C  bang thuc the biet "tôi" do BENH NHAN noi -> id 0 -> muc DI UNG.
    """
    ht = "Bác sĩ: Anh có dị ứng thuốc gì không ạ?\nBệnh nhân: Tôi dị ứng penicillin."
    ps = [
        {"chu_the": "tôi", "noi_dung": "dị ứng penicillin",
         "do_chac_chan": "chắc chắn", "phu_dinh": False, "tinh_huong": "thực tế",
         "thoi_gian_su_kien": "quá khứ", "moc_thoi_gian": None,
         "quan_he": "không", "quan_he_voi": None, "luot_thoai": [1, 2]},
        {"chu_the": "tôi", "noi_dung": "sốt", "do_chac_chan": "chắc chắn",
         "phu_dinh": False, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại",
         "moc_thoi_gian": "4 ngày", "quan_he": "không", "quan_he_voi": None,
         "luot_thoai": [2]},
        {"chu_the": "tôi", "noi_dung": "sốt", "do_chac_chan": "chắc chắn",
         "phu_dinh": False, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại",
         "moc_thoi_gian": "2 ngày", "quan_he": "đính chính", "quan_he_voi": 1,
         "luot_thoai": [2]},
    ]
    ra = {}
    for ten in ("B", "C_khong_luat", "C_khong_lien_ket", "C"):
        mo_hinh_gia(ps)
        ra[ten] = nhanh.chay_trung_gian(mau(ht), None, None, None, ten)[0]["du_doan"]

    def co_lien_ket(v):
        """Dung: di ung cua chinh benh nhan nam o muc DI UNG."""
        return "DỊ ỨNG" in v.split("CẦN XÁC NHẬN")[0]             and MUC_NGUOI_KHAC not in v

    def co_luat(v):
        """Dung: moc da bi dinh chinh khong con o than benh an."""
        return "4 ngày" not in v.split("CẦN XÁC NHẬN")[0]

    assert not co_lien_ket(ra["B"]) and not co_luat(ra["B"]), "o (khong, khong)"
    assert co_lien_ket(ra["C_khong_luat"]) and not co_luat(ra["C_khong_luat"]),         "o (lien ket, khong luat)"
    assert not co_lien_ket(ra["C_khong_lien_ket"]) and co_luat(ra["C_khong_lien_ket"]),         "o (khong lien ket, luat)"
    assert co_lien_ket(ra["C"]) and co_luat(ra["C"]), "o (lien ket, luat)"


def test_luat_chuoi_tho_cua_B_da_du_khi_chu_the_ghi_ro_vai():
    """Ghi lai phat hien tren thanh test rieng.

    Khi mo hinh ghi `chu_the="người nhà"` thi B da phan loai dung ma khong
    can lien ket thuc the. Nghia la dong gop cua lien ket thuc the chi do
    duoc tren cac mau co chu the la DAI TU. Neu bao cao noi lien ket lam nen
    chenh lech C - B thi phai kem ty le mau thuoc loai do.
    """
    from src import phat_bieu
    ra, _ = phat_bieu.tu_json([{"chu_the": "người nhà", "noi_dung": "dị ứng",
                                "luot_thoai": [1]}])
    assert ra[0].chu_the_id != 0
    ra2, _ = phat_bieu.tu_json([{"chu_the": "trẻ", "noi_dung": "sốt",
                                 "luot_thoai": [1]}])
    assert ra2[0].chu_the_id == 0


def test_trich_mot_lan_dung_duoc_cho_nhieu_nhanh(monkeypatch):
    """Sau nhanh dung chung buoc trich. Chay rieng la sinh lai sau lan.

    Test nay giu hai dieu: truyen `kq_tho` vao thi KHONG goi mo hinh nua,
    va ket qua giong het nhu khi de no tu trich.
    """
    dem = {"lan": 0}

    def _gia(tok, model, prefix_fn, mau_list, max_token=1536, vi_du=True):
        dem["lan"] += 1
        return [{"id": m["id"], "so_luot": 2, "json_hop_le": True,
                 "ly_do": "", "phat_bieu": PS_CHU_THE, "tho": ""} for m in mau_list]
    monkeypatch.setattr(bakeoff, "trich", _gia)

    m = mau(HT_CHU_THE)
    tho = bakeoff.trich(None, None, None, m)
    assert dem["lan"] == 1
    a = nhanh.chay_trung_gian(m, None, None, None, "C", kq_tho=tho)
    b = nhanh.chay_trung_gian(m, None, None, None, "B", kq_tho=tho)
    assert dem["lan"] == 1, "van goi lai mo hinh du da co ket qua trich"

    tu_trich = nhanh.chay_trung_gian(m, None, None, None, "C")
    assert dem["lan"] == 2
    assert a[0]["du_doan"] == tu_trich[0]["du_doan"]

    # KHONG con doi hoi B khac C tren mau nay.
    #
    # Truoc 11/09/2026 dong nay la `assert b[0]["du_doan"] != a[0]["du_doan"]`,
    # va no xanh vi mot LO~I: nhanh B roi mat ten nguoi. `ten_chu_the` cua B la
    # `{}` (B khong lien ket thuc the), nen `sinh_benh_an` khong tra duoc ten va
    # viet cau KHONG CO TEN AI. C tra duoc, nen hai ban khac nhau — va test lay
    # dung chenh lech do lam bang chung rang hai nhanh khac nhau.
    #
    # Gia cua lo~i do, do tren tap phat trien the he 2: muc TIEN SU GIA DINH VA
    # XA HOI cua B/C/D co 50/50/53 cau va **0 cau neu ten nguoi**, trong khi ban
    # tham chieu co 22 cau va 22 cau neu ten.
    #
    # Sau khi `sinh_benh_an` biet lui ve chuoi khau trich da viet, B cung neu ten
    # — va tren mau nay `chu_the` la "nguoi nha", dung bang ten chuan cua thuc
    # the, nen hai ban trung nhau. Do KHONG phai mat phep boc tach:
    # `test_luat_chuoi_tho_cua_B_da_du_khi_chu_the_ghi_ro_vai` ngay phia tren da
    # ghi rang dong gop cua lien ket thuc the chi do duoc tren mau co chu the la
    # DAI TU, va mau nay khong phai loai do.
    #
    # Test nay gio chi giu dieu no noi trong docstring: truyen `kq_tho` thi khong
    # goi lai mo hinh, va ket qua giong het khi de no tu trich.
    assert b[0]["du_doan"], "nhanh B phai sinh ra ban nhap"
