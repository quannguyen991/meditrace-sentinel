# -*- coding: utf-8 -*-
"""Cap nhat trang thai THEO TUNG LUOT, va hai chi so co don vi la luot.

Them 16/09/2026 sau khi doc arXiv 2603.17425 (Pan, Liu, You): ho chay vong cap nhat
o moi luot va do `T_goal`; du an nay truoc do chi cap nhat MOT lan cho ca ca, nen
khong tra loi duoc "o luot thu may ban nhap bat dau sai".

Hai hang rao trong tep nay:
  1. Anh chup o luot CUOI phai trung khit `ap_luat` tren ca danh sach — hai duong
     khong duoc troi nhau.
  2. Tren ca co dinh chinh, `luot_sai_dau_tien` phai la luot TRUOC khi cau dinh chinh
     xuat hien, khong phai luot cuoi.
"""
from src import cap_nhat, cham_he_thong as cht
from src.phat_bieu import PhatBieu


def _pb(id, noi_dung, bang_chung, quan_he=None, quan_he_voi=None, nguoi_noi="bệnh nhân"):
    return PhatBieu(id=id, nguoi_noi=nguoi_noi, chu_the_id=0, noi_dung=noi_dung,
                    bang_chung=bang_chung, quan_he=quan_he, quan_he_voi=quan_he_voi,
                    trich_dan=[noi_dung])


def _bo_dinh_chinh():
    """Luot 2 noi "sot bon ngay", luot 5 tu dinh chinh thanh "sot hai ngay"."""
    return [_pb(0, "sốt bốn ngày", [2]),
            _pb(1, "ho", [3]),
            _pb(2, "sốt hai ngày", [5], quan_he="đính chính", quan_he_voi=0)]


def test_anh_chup_cuoi_cung_trung_khit_ap_luat_ca_danh_sach():
    ds = _bo_dinh_chinh()
    theo_luot = cap_nhat.ap_luat_theo_luot(ds)
    cuoi = theo_luot[-1][1]
    mot_lan = cap_nhat.ap_luat(ds)
    assert [p.to_dict() for p in cuoi] == [p.to_dict() for p in mot_lan]


def test_moc_luot_dung_bang_luot_bang_chung_muon_nhat():
    ds = _bo_dinh_chinh()
    assert [t for t, _ in cap_nhat.ap_luat_theo_luot(ds)] == [2, 3, 5]


def test_truoc_khi_dinh_chinh_ban_cu_van_con_hieu_luc():
    theo_luot = dict(cap_nhat.ap_luat_theo_luot(_bo_dinh_chinh()))
    tai_3 = {p.id: p.trang_thai for p in theo_luot[3]}
    tai_5 = {p.id: p.trang_thai for p in theo_luot[5]}
    assert tai_3[0] == "còn hiệu lực", "luot 3 chua ai dinh chinh"
    assert tai_5[0] == "bị thay thế" and tai_5[2] == "còn hiệu lực"


def test_cap_hoi_dap_tinh_theo_luot_tra_loi():
    """Bang chung [3, 4] la mot cap hoi–dap: thong tin chi du nghia o luot 4."""
    ds = [_pb(0, "dị ứng thuốc", [3, 4])]
    assert [t for t, _ in cap_nhat.ap_luat_theo_luot(ds)] == [4]


# ------------------------------------------------- hai chi so co don vi la luot

def _ca_va_ket_qua(du_doan_sai_o_luot_2=True):
    """Mot ca dap an hai menh de, va mot ban ghi ket qua cua duong ong."""
    ca = {"id": "t1", "input": "Bác sĩ: Sao ạ?\nBệnh nhân: Sốt hai ngày.\nBác sĩ: Ho không?\nBệnh nhân: Có ho.",
          "dap_an": [
              {"chu_the": "bệnh nhân", "noi_dung": "sốt", "muc": "BỆNH SỬ HIỆN TẠI",
               "moc_thoi_gian": "hai ngày", "luot": [2], "trang_thai": "còn hiệu lực",
               "tinh_huong": "thực tế", "do_chac_chan": "chắc chắn", "phu_dinh": False},
              {"chu_the": "bệnh nhân", "noi_dung": "ho", "muc": "BỆNH SỬ HIỆN TẠI",
               "moc_thoi_gian": None, "luot": [4], "trang_thai": "còn hiệu lực",
               "tinh_huong": "thực tế", "do_chac_chan": "chắc chắn", "phu_dinh": False}]}
    p0 = {"id": 0, "chu_the_id": 0 if not du_doan_sai_o_luot_2 else 1,
          "ten_chu_the": "bệnh nhân" if not du_doan_sai_o_luot_2 else "mẹ",
          "noi_dung": "sốt", "moc_thoi_gian": "hai ngày", "bang_chung": [2],
          "do_chac_chan": "chắc chắn", "phu_dinh": False, "tinh_huong": "thực tế"}
    p1 = {"id": 1, "chu_the_id": 0, "ten_chu_the": "bệnh nhân", "noi_dung": "ho",
          "moc_thoi_gian": None, "bang_chung": [4], "do_chac_chan": "chắc chắn",
          "phu_dinh": False, "tinh_huong": "thực tế"}
    r = {"phat_bieu": [p0, p1],
         "ghi_chu": [{"id": 0, "muc": "BỆNH SỬ HIỆN TẠI"},
                     {"id": 1, "muc": "BỆNH SỬ HIỆN TẠI"}]}
    return ca, r


def test_luot_sai_dau_tien_chi_dung_luot_co_loi():
    ca, r = _ca_va_ket_qua(du_doan_sai_o_luot_2=True)
    k = cht.cham_theo_luot(ca, r)
    assert k["luot_sai_dau_tien"] == 2, k
    assert k["T_dung"] is None, "ban nhap sai chu the thi khong bao gio dung"


def test_ban_nhap_dung_thi_khong_co_luot_sai_va_T_dung_la_luot_cuoi():
    ca, r = _ca_va_ket_qua(du_doan_sai_o_luot_2=False)
    k = cht.cham_theo_luot(ca, r)
    assert k["luot_sai_dau_tien"] is None, k
    assert k["T_dung"] == 4, k
    assert k["so_menh_de_than_dap_an"] == 2


def test_bo_sot_cung_tinh_la_luot_sai():
    """Thieu mot menh de dap an tinh toi luot do cung la sai, khong chi ghi sai."""
    ca, r = _ca_va_ket_qua(du_doan_sai_o_luot_2=False)
    r = {"phat_bieu": [r["phat_bieu"][1]], "ghi_chu": [r["ghi_chu"][1]]}
    k = cht.cham_theo_luot(ca, r)
    assert k["luot_sai_dau_tien"] == 2, k
