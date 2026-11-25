# -*- coding: utf-8 -*-
"""Loi KHO cay vao dap an (cho du lieu huan luyen va de do do kho cua luat)."""
import copy
import json
import random

import pytest

from tools import cay_loi_kho as k

HOI = "\n".join([
    "Bác sĩ: Chị khó chịu ở đâu?",                                               # 1
    "Bệnh nhân: Tôi đau âm ỉ hố chậu phải 3 ngày nay, sốt 38,5 độ.",               # 2
    "Bác sĩ: Chị có ho, có khó thở không?",                                       # 3
    "Bệnh nhân: Không ho, nhưng hơi khó thở.",                                    # 4
    "Người nhà: Mẹ tôi bị tiểu đường.",                                           # 5
    "Bệnh nhân: Tôi uống amlodipin 5 mg ngày một lần buổi sáng.",                 # 6
    "Bệnh nhân: À không, 4 ngày chứ không phải 3 ngày.",                          # 7
    "Bác sĩ: Có thể là viêm ruột thừa. Nếu đau tăng thì chị vào viện ngay nhé.",  # 8
])


def _d(nd, luot, **kw):
    d = dict(chu_the="bệnh nhân", noi_dung=nd, muc="BỆNH SỬ HIỆN TẠI", moc_thoi_gian=None, phu_dinh=False,
             tinh_huong="thực tế", luot=luot, thoi_gian_su_kien="hiện tại", quan_he=None, quan_he_voi=None,
             trang_thai="còn hiệu lực", do_chac_chan="chắc chắn", hanh_vi="tự kể", thuoc=None,
             trich_dan=["x"] * len(luot))
    d.update(kw)
    return d


CA = {"id": "kho_1", "input": HOI, "dap_an": [
    _d("đau âm ỉ hố chậu phải", [2, 7], moc_thoi_gian="4 ngày"),                                   # 0
    _d("đau âm ỉ hố chậu phải", [2], moc_thoi_gian="3 ngày", trang_thai="bị thay thế"),            # 1
    _d("sốt 38,5 độ", [2]),                                                                       # 2
    _d("ho", [3, 4], phu_dinh=True),                                                              # 3
    _d("khó thở nhẹ", [3, 4]),                                                                    # 4
    _d("tiểu đường", [5], chu_the="mẹ", muc="TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", thoi_gian_su_kien="quá khứ"),  # 5
    _d("đang dùng amlodipin 5 mg ngày một lần buổi sáng", [6], muc="THUỐC ĐANG DÙNG",
       thuoc={"ten": "amlodipin", "lieu": "5 mg", "so_lan": "ngày một lần", "duong_dung": "uống",
              "bat_dau": None, "ngung": None, "trang_thai_dung": "đang dùng"}),                   # 6
    _d("có thể viêm ruột thừa", [8], muc="CHẨN ĐOÁN", do_chac_chan="nghi ngờ", hanh_vi="nhận định"),  # 7
    _d("vào viện ngay nếu đau tăng", [8], muc="KẾ HOẠCH ĐIỀU TRỊ", tinh_huong="giả định",
       hanh_vi="kế hoạch"),                                                                       # 8
]}


def _cay(loai, hat=0):
    return k.cay_kho(CA, loai, random.Random(hat))


def test_danh_muc():
    assert len(k.LOAI_KHO) >= 12 and set(k.NHOM_KHO) == set(k.LOAI_KHO)


@pytest.mark.parametrize("loai", k.LOAI_KHO)
def test_moi_loai_ap_dung_duoc_khong_sua_goc_tat_dinh(loai):
    goc = copy.deepcopy(CA)
    a, b = _cay(loai, 3), _cay(loai, 3)
    assert CA == goc
    assert a is not None, loai
    assert a[0]["dap_an"] != CA["dap_an"]
    assert json.dumps(a[0], ensure_ascii=False) == json.dumps(b[0], ensure_ascii=False)
    assert [c.loai for c in a[1]] == [loai]


def test_so_lech_nho_chi_lech_1():
    moi, (c,) = _cay("so_lech_nho")
    d = moi["dap_an"][c.chi_so]
    assert d["noi_dung"] in ("sốt 37,5 độ", "sốt 39,5 độ") or c.chi_so in (0, 6)


def test_doi_ben_va_muc_do():
    moi, (c,) = _cay("doi_ben")
    assert "hố chậu trái" in moi["dap_an"][c.chi_so]["noi_dung"]
    moi, (c,) = _cay("doi_muc_do")
    assert moi["dap_an"][c.chi_so]["noi_dung"] != CA["dap_an"][c.chi_so]["noi_dung"]


def test_nguoi_nha_thanh_benh_nhan():
    moi, (c,) = _cay("nguoi_nha_thanh_benh_nhan")
    assert c.chi_so == 5 and moi["dap_an"][5]["chu_the"] == "bệnh nhân"


def test_bo_tu_nghi():
    moi, (c,) = _cay("bo_tu_nghi")
    d = moi["dap_an"][7]
    assert c.chi_so == 7 and d["do_chac_chan"] == "chắc chắn" and "có thể" not in d["noi_dung"]


def test_dinh_chinh_nguoc_giu_ban_cu():
    moi, (c,) = _cay("dinh_chinh_nguoc")
    assert moi["dap_an"][0]["trang_thai"] == "bị thay thế" and moi["dap_an"][1]["trang_thai"] == "còn hiệu lực"


def test_phu_dinh_trong_chuoi_chon_luot_co_ca_hai():
    for hat in range(6):
        moi, (c,) = _cay("phu_dinh_trong_chuoi", hat)
        assert c.chi_so in (3, 4)
        assert moi["dap_an"][c.chi_so]["phu_dinh"] != CA["dap_an"][c.chi_so]["phu_dinh"]


def test_bia_phu_dinh_them_dong_khong_co_trong_hoi_thoai():
    moi, (c,) = _cay("bia_phu_dinh")
    d = moi["dap_an"][c.chi_so]
    assert c.chi_so == len(CA["dap_an"]) and d["phu_dinh"] and d["noi_dung"] not in HOI.lower()


def test_cay_nhieu_loi_khac_dong():
    moi, cs = k.cay_nhieu(CA, random.Random(1), so_loi=3)
    assert len(cs) == 3 and len({c.chi_so for c in cs}) == 3


def test_xuat_cap_dung_dinh_dang_train():
    cap = k.xuat_cap(CA, random.Random(0), so_loi=2)
    tot, xau = json.loads(cap["chosen"]), json.loads(cap["rejected"])
    assert cap["id"] == "kho_1" and tot != xau and "phat_bieu" in xau and len(cap["loi"]) == 2
    assert all({"loai", "chi_so", "mo_ta"} <= set(x) for x in cap["loi"])


def test_moi_nhan_loi_tro_dung_dong_trong_dau_ra():
    for hat in range(15):
        cap = k.xuat_cap(CA, random.Random(hat), so_loi=hat % 3 + 1)
        if cap is None:
            continue
        xau = json.loads(cap["rejected"])["phat_bieu"]
        assert all(x["chi_so_ra"] is not None and x["chi_so_ra"] < len(xau) for x in cap["loi"])
