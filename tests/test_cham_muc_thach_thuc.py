# -*- coding: utf-8 -*-
"""Cham thach thuc tren van ban: cung mot ham cho moi nhanh, ke ca nhanh A.

Hai dieu phai giu, va ca hai deu co ca that dung sau:
  1. DUNG cho that sai phai bi bat (di ung sai nguoi, giu moc da bi dinh chinh)
  2. SAI LECH KHONG LIEN QUAN khong duoc keo ca xuong ("met" vs "met moi") —
     neu khong phep do nay chi do "viet giong khuon".
"""
from src import cham_muc_thach_thuc as cm


THAM_CHIEU_BAN_A = """LÝ DO KHÁM BỆNH

Mệt.

TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI

Bố rối loạn lo âu; Bố dị ứng nọc ong.

DỊ ỨNG

Chưa ghi nhận dị ứng thuốc."""


def _ca_dct(output):
    return {"id": "x", "output": output, "dap_an": []}


def test_tach_muc_bo_hai_muc_phu():
    van = "BỆNH SỬ HIỆN TẠI\n\nSốt.\n\nCẦN XÁC NHẬN\n\n- ho (chưa rõ)\n\nCÂU HỎI LÀM RÕ\n\n1. Ho mấy ngày?"
    m = cm.tach_muc(van)
    assert "BỆNH SỬ HIỆN TẠI" in m
    assert "CẦN XÁC NHẬN" not in m and "CÂU HỎI LÀM RÕ" not in m


def test_tach_muc_hieu_tieu_de_markdown():
    """Nhanh A tung viet tieu de kieu Markdown — `chuan_dinh_dang` phai quy ve chuan."""
    m = cm.tach_muc("**Dị ứng:**\n\nDị ứng nọc ong.")
    assert m.get("DỊ ỨNG") == ["Dị ứng nọc ong."]


def test_cac_y_tach_theo_cham_phay_va_bo_thu_tu():
    assert cm.cac_y(["Bố rối loạn lo âu; Bố dị ứng nọc ong."]) == \
           cm.cac_y(["Bố dị ứng nọc ong; bố rối loạn lo âu"])


def test_cac_y_khong_cat_so_thap_phan():
    assert cm.cac_y(["Sốt 38,5 độ."]) == {"sốt 38,5 độ"}


def test_doi_chu_the_dung_khi_di_ung_dung_cho():
    assert cm.dung_doi_chu_the(_ca_dct(THAM_CHIEU_BAN_A), THAM_CHIEU_BAN_A)


def test_doi_chu_the_SAI_khi_di_ung_nguoi_nha_bi_gan_cho_benh_nhan():
    sai = THAM_CHIEU_BAN_A.replace("Bố rối loạn lo âu; Bố dị ứng nọc ong.", "Bố rối loạn lo âu.") \
                          .replace("Chưa ghi nhận dị ứng thuốc.", "Dị ứng nọc ong.")
    assert not cm.dung_doi_chu_the(_ca_dct(THAM_CHIEU_BAN_A), sai)


def test_doi_chu_the_KHONG_phat_sai_lech_khong_lien_quan():
    lech = THAM_CHIEU_BAN_A.replace("Bố rối loạn lo âu", "Bố bị rối loạn lo âu")
    assert cm.dung_doi_chu_the(_ca_dct(THAM_CHIEU_BAN_A), lech)


def _ca_dch():
    return {
        "id": "dch", "bay_chinh": "dinh_chinh",
        "output": "BỆNH SỬ HIỆN TẠI\n\nBệnh nhân đau thượng vị (hai tháng nay); mệt.",
        "dap_an": [
            {"noi_dung": "đau thượng vị", "quan_he": "đính chính", "quan_he_voi": 1},
            {"noi_dung": "đau thượng vị", "quan_he": None},
            {"noi_dung": "mệt", "quan_he": None},
        ],
    }


def test_dinh_chinh_SAI_khi_giu_moc_da_bi_sua():
    sai = "BỆNH SỬ HIỆN TẠI\n\nBệnh nhân đau thượng vị (nửa năm rồi); mệt."
    assert cm.dung_dinh_chinh(_ca_dch(), sai) is False


def test_dinh_chinh_KHONG_phat_met_thanh_met_moi():
    """Ca that `dch_001`: xu ly moc dung, chi viet mot y khac lech chu."""
    dung_ma_lech = "BỆNH SỬ HIỆN TẠI\n\nBệnh nhân đau thượng vị (hai tháng nay); mệt mỏi."
    assert cm.dung_dinh_chinh(_ca_dch(), dung_ma_lech) is True


def test_dinh_chinh_ca_khong_co_quan_he_thi_bo_qua():
    ca = _ca_dch()
    for d in ca["dap_an"]:
        d["quan_he"] = None
    assert cm.dung_dinh_chinh(ca, ca["output"]) is None


def test_cap_nhieu_asr_nhan_dung_ban_nao_bi_lam_kho():
    """Hai bo sinh dat nhan NGUOC nhau; nham la dao dau ket luan."""
    assert cm.BAN_BI_LAM_KHO == {"phuong_ngu": "A", "nhieu_asr": "B"}


def test_cham_tap_nhieu_asr_dem_ban_bi_lam_kho_rieng():
    tc = "BỆNH SỬ HIỆN TẠI\n\nSốt."
    cac_ca = [
        {"id": "s", "thach_thuc": "nhieu_asr", "cap": 0, "bien_the": "A", "output": tc},
        {"id": "k", "thach_thuc": "nhieu_asr", "cap": 0, "bien_the": "B", "output": tc},
    ]
    kq = {"s": {"du_doan": tc}, "k": {"du_doan": "BỆNH SỬ HIỆN TẠI\n\nHo."}}
    ra = cm.cham_tap(cac_ca, kq)
    assert ra["hai_ban_giong_het"] == 0
    assert "ban_sach_trung_tham_chieu" not in ra, "truong so voi cach viet bo sinh da bo"


# ------------------------------------------------ cach viet cua KHAU DUNG BAN NHAP
# Bo test ban dau chi dung cau theo khuon cua bo sinh, nen xanh trong khi bo cham
# phat oan duong ong 0/40. Cac test duoi day dung DUNG cach viet that cua duong ong.

def test_duong_ong_viet_nguoi_hai_cham_van_dung():
    duong_ong = THAM_CHIEU_BAN_A.replace("Bố rối loạn lo âu; Bố dị ứng nọc ong.",
                                         "bố: rối loạn lo âu. bố: dị ứng nọc ong.")
    assert cm.dung_doi_chu_the(_ca_dct(THAM_CHIEU_BAN_A), duong_ong)


def test_duong_ong_viet_SAI_NGUOI_van_bi_bat_sau_chuan_hoa():
    sai = THAM_CHIEU_BAN_A.replace("Bố rối loạn lo âu; Bố dị ứng nọc ong.",
                                   "bà ngoại: rối loạn lo âu. bà ngoại: dị ứng nọc ong.")
    assert not cm.dung_doi_chu_the(_ca_dct(THAM_CHIEU_BAN_A), sai)


def test_dinh_chinh_bo_tien_to_benh_nhan_va_y_tron_lap():
    duong_ong = "BỆNH SỬ HIỆN TẠI\n\nđau thượng vị (hai tháng nay). đau thượng vị. mệt."
    assert cm.dung_dinh_chinh(_ca_dch(), duong_ong) is True


def test_dinh_chinh_hai_moc_mau_thuan_lam_su_that_van_SAI():
    ca = _ca_dch()
    ca["output"] = "BỆNH SỬ HIỆN TẠI\n\nBệnh nhân đau thượng vị (chưa rõ hai tháng nay hay nửa năm rồi)."
    duong_ong = "BỆNH SỬ HIỆN TẠI\n\nđau thượng vị (hai tháng nay). đau thượng vị (nửa năm rồi)."
    assert cm.dung_dinh_chinh(ca, duong_ong) is False


def _ca_mau_thuan():
    return {"id": "m", "bay_chinh": "mau_thuan",
            "output": "BỆNH SỬ HIỆN TẠI\n\nBệnh nhân sốt (chưa rõ ba hôm hay mấy hôm nay).",
            "dap_an": [
                {"noi_dung": "sốt", "moc_thoi_gian": "ba hôm", "trang_thai": "chưa giải quyết", "quan_he": None},
                {"noi_dung": "sốt", "moc_thoi_gian": "mấy hôm nay", "trang_thai": "chưa giải quyết",
                 "quan_he": "mâu thuẫn", "quan_he_voi": 0}]}


def test_mau_thuan_viet_chua_ro_trong_than_la_dung():
    assert cm.dung_dinh_chinh(_ca_mau_thuan(), "BỆNH SỬ HIỆN TẠI\n\nsốt (chưa rõ ba hôm hay mấy hôm nay).")


def test_mau_thuan_dua_xuong_can_xac_nhan_cung_la_dung():
    """Chinh sach cua duong ong — khong duoc phat vi khac cach viet cua bo sinh."""
    van = ("BỆNH SỬ HIỆN TẠI\n\nmệt.\n\nCẦN XÁC NHẬN\n\n"
           "sốt (ba hôm) — trạng thái chưa giải quyết.\nsốt (mấy hôm nay) — trạng thái chưa giải quyết.")
    assert cm.dung_dinh_chinh(_ca_mau_thuan(), van)


def test_mau_thuan_ghi_ca_hai_moc_lam_su_that_la_SAI():
    assert not cm.dung_dinh_chinh(_ca_mau_thuan(), "BỆNH SỬ HIỆN TẠI\n\nsốt (ba hôm). sốt (mấy hôm nay).")


def test_mau_thuan_bien_mat_khong_dau_vet_la_SAI():
    assert not cm.dung_dinh_chinh(_ca_mau_thuan(), "BỆNH SỬ HIỆN TẠI\n\nsốt (ba hôm).")
