# -*- coding: utf-8 -*-
"""Test phep do va dieu kien cong bang.

Dieu kien cong bang la cai chan viec "cai thien" bang cach viet it di. Neu no
khong bao thang duoc thi no vo dung — nen o day co test cho ca hai chieu.
"""
from src import do_dac


def kq(du_doan, tham_chieu, **kw):
    d = {"id": "m1", "du_doan": du_doan, "tham_chieu": tham_chieu,
         "du_doan_khong_muc_phu": du_doan.split("CẦN XÁC NHẬN")[0].strip(),
         "so_luot_goi": 1, "token_vao": 100, "token_ra": 50,
         "so_phat_bieu": 2, "so_can_xac_nhan": 0, "loi_ban_ghi": []}
    d.update(kw)
    return d


BENH_AN = "LÝ DO KHÁM BỆNH\n\nHo khan 2 ngày."


# ------------------------------------------------------------- do mot nhanh

def test_diem_giong_het_khi_du_doan_trung_tham_chieu():
    d = do_dac.do_mot_nhanh([kq(BENH_AN, BENH_AN)])
    assert d["section_f1"] == 1.0
    assert d["final"] > 0.99


def test_cong_don_chi_phi():
    d = do_dac.do_mot_nhanh([kq(BENH_AN, BENH_AN), kq(BENH_AN, BENH_AN)])
    assert d["so_luot_goi"] == 2 and d["token_vao"] == 200


def test_bo_muc_phu_lam_section_f1_TANG():
    """Ly do phai do ca hai ban: muc CAN XAC NHAN la mot muc du doan thua."""
    van = BENH_AN + "\n\nCẦN XÁC NHẬN\n\nkhó thở — câu giả định, chưa xảy ra."
    co = do_dac.do_mot_nhanh([kq(van, BENH_AN)], dung_muc_phu=True)
    khong = do_dac.do_mot_nhanh([kq(van, BENH_AN)], dung_muc_phu=False)
    assert khong["section_f1"] > co["section_f1"]
    assert co["section_f1"] < 1.0 and khong["section_f1"] == 1.0


def test_mau_khong_co_tham_chieu_khong_lam_lech_trung_binh():
    d = do_dac.do_mot_nhanh([kq(BENH_AN, BENH_AN), kq(BENH_AN, "")])
    assert d["so_mau"] == 2 and d["so_mau_co_tham_chieu"] == 1
    assert d["section_f1"] == 1.0


# ------------------------------------------------------------------ bo sot

def test_bo_sot_tra_None_cho_nhanh_khong_co_bang_phat_bieu():
    """A va A+ sinh van xuoi. Khong duoc lay ROUGE recall thay the roi goi
    la cung mot dai luong."""
    assert do_dac.do_bo_sot([kq(BENH_AN, BENH_AN)]) is None


def test_bo_sot_dem_dung_ty_le():
    gc = [{"id": 1, "muc": "BỆNH SỬ HIỆN TẠI"},
          {"id": 2, "muc": "CẦN XÁC NHẬN"},
          {"id": 3, "muc": "CẦN XÁC NHẬN"},
          {"id": 4, "muc": "DỊ ỨNG"}]
    b = do_dac.do_bo_sot([kq(BENH_AN, BENH_AN, ghi_chu=gc)])
    assert b["tong_phat_bieu"] == 4 and b["sang_muc_phu"] == 2
    assert abs(b["ty_le_muc_phu"] - 0.5) < 1e-9


# ------------------------------------------------------ dieu kien cong bang

def test_dieu_kien_DAT_khi_bo_sot_khong_tang():
    dat, tin = do_dac.kiem_dieu_kien_cong_bang(
        {"ty_le_muc_phu": 0.10}, {"ty_le_muc_phu": 0.10})
    assert dat is True


def test_dieu_kien_DAT_o_dung_nguong_20_phan_tram():
    dat, _ = do_dac.kiem_dieu_kien_cong_bang(
        {"ty_le_muc_phu": 0.10}, {"ty_le_muc_phu": 0.12})
    assert dat is True


def test_dieu_kien_THANG_khi_bo_sot_tang_qua_nguong():
    """Chieu quan trong: mot dieu kien khong bao gio thang thi vo dung."""
    dat, tin = do_dac.kiem_dieu_kien_cong_bang(
        {"ty_le_muc_phu": 0.10}, {"ty_le_muc_phu": 0.30})
    assert dat is False
    assert "viet it di" in tin


def test_dieu_kien_thang_khi_tu_khong_bo_sot_thanh_co():
    dat, tin = do_dac.kiem_dieu_kien_cong_bang(
        {"ty_le_muc_phu": 0.0}, {"ty_le_muc_phu": 0.05})
    assert dat is False
    assert "0% -> 5%" in tin, "phai neu tri tuyet doi, khong chi 'tang inf%'"
    assert "inf" not in tin


def test_thong_diep_luon_neu_tri_tuyet_doi():
    """"Tang 20%" khong doc duoc neu khong biet 20% cua bao nhieu."""
    for cu, moi in [(0.10, 0.10), (0.10, 0.12), (0.10, 0.30), (0.0, 0.0)]:
        _, tin = do_dac.kiem_dieu_kien_cong_bang(
            {"ty_le_muc_phu": cu}, {"ty_le_muc_phu": moi})
        assert f"{cu:.0%} -> {moi:.0%}" in tin, tin


def test_dieu_kien_tra_None_khi_thieu_du_lieu():
    dat, tin = do_dac.kiem_dieu_kien_cong_bang(None, {"ty_le_muc_phu": 0.1})
    assert dat is None and "khong du du lieu" in tin


# ------------------------------------------------------------------- bang

def test_bang_so_sanh_in_du_moi_nhanh():
    b = do_dac.bang_so_sanh({"A": do_dac.do_mot_nhanh([kq(BENH_AN, BENH_AN)]),
                             "C": do_dac.do_mot_nhanh([kq(BENH_AN, BENH_AN)])})
    assert "| A |" in b and "| C |" in b and "final" in b


def test_bang_khong_nem_khi_thieu_so():
    b = do_dac.bang_so_sanh({"A": {"final": None, "so_phat_bieu": 0}})
    assert "—" in b
