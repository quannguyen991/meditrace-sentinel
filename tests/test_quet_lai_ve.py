# -*- coding: utf-8 -*-
"""Task 1 (kế hoạch 27/11): quét lại các vế chưa được trích.

86% mệnh đề bị sót nằm trong một lượt đã có mệnh đề khác (canh-bao-moc-0.md). Đơn vị
xét phải là VẾ, không phải lượt: lượt đã có một câu trích vẫn có thể còn vế chưa ai ghi.
"""
import json
import unicodedata

import pytest

from src.duong_ong import chay_duong_ong as nhanh
from src.duong_ong.b1_quet_lai_ve import (gop_ket_qua_quet_lai, loc_trong_van,
                                          loi_nhac_quet_lai, ve_chua_phu)
from src.huan_luyen import chon_mo_hinh_bakeoff as bakeoff

HT = "[1] Bác sĩ: Cô dùng thuốc gì?\n[2] Bệnh nhân: Tôi uống amlodipin 5mg, còn dị ứng tôm."


# ---------------------------------------------------------------- ba test của kế hoạch

def test_ve_chua_phu_tim_ve_thu_hai_cung_luot():
    ps = [{"trich_dan": "Tôi uống amlodipin 5mg", "bang_chung": [2]}]
    ve = ve_chua_phu(HT, ps)
    assert [v["van"] for v in ve] == ["còn dị ứng tôm"]
    assert "di_ung" in ve[0]["tin_hieu"]


def test_ve_xa_giao_khong_quet():
    assert ve_chua_phu("[1] Bệnh nhân: Vâng ạ.", []) == []


def test_gop_bo_trung_trich_va_gan_nguon():
    cu = [{"trich_dan": "dị ứng tôm", "bang_chung": [2]}]
    moi = [{"trich_dan": "dị ứng tôm", "bang_chung": [2]}, {"trich_dan": "5mg", "bang_chung": [2]}]
    ra = gop_ket_qua_quet_lai(cu, moi)
    assert len(ra) == 2 and ra[1]["nguon"] == "quet_lai"


# ---------------------------------------------------------------- thêm

def test_ve_chua_phu_tra_vi_tri_tren_luot():
    ps = [{"trich_dan": ["Tôi uống amlodipin 5mg"], "luot_thoai": [2]}]
    v = ve_chua_phu(HT, ps)[0]
    luot2 = HT.split("\n")[1].split(": ", 1)[1]
    assert v["luot"] == 2 and luot2[v["dau"]:v["cuoi"]] == "còn dị ứng tôm"


def test_ve_co_trich_nhung_con_thuoc_khac_van_chua_phu():
    """Câu trích chỉ chạm một phần vế: vế còn tên thuốc chưa nằm trong câu trích nào thì
    vẫn là chưa phủ (Review Focus 1)."""
    ht = "[1] Bệnh nhân: Tôi uống amlodipin 5mg với metformin 500mg."
    ps = [{"trich_dan": "amlodipin 5mg", "luot_thoai": [1]}]
    ve = ve_chua_phu(ht, ps)
    assert len(ve) == 1 and "thuoc" in ve[0]["tin_hieu"]


def test_ve_da_phu_du_thi_khong_quet():
    ps = [{"trich_dan": "Tôi uống amlodipin 5mg", "luot_thoai": [2]},
          {"trich_dan": "dị ứng tôm", "luot_thoai": [2]}]
    assert ve_chua_phu(HT, ps) == []


def test_loi_nhac_neu_dung_ve_va_danh_so_luot():
    ve = ve_chua_phu(HT, [{"trich_dan": "Tôi uống amlodipin 5mg", "bang_chung": [2]}])
    nhac = loi_nhac_quet_lai(HT, ve)
    assert "còn dị ứng tôm" in nhac and "Lượt 2" in nhac
    assert "2. [2] Bệnh nhân" in nhac and "trich_dan" in nhac


def _luot(ht, so):
    dong = [d for d in ht.split("\n") if d.strip()][so - 1]
    return unicodedata.normalize("NFC", dong.split(": ", 1)[1]).lower()


def test_quet_lai_khong_tao_menh_de_ngoai_van():
    """Mọi mệnh đề quét lại được giữ đều có câu trích nằm trong chính lượt nó dẫn."""
    moi = [{"chu_the": "bệnh nhân", "noi_dung": "dị ứng tôm", "luot_thoai": [2],
            "trich_dan": ["dị ứng tôm"]},
           {"chu_the": "bệnh nhân", "noi_dung": "dị ứng cua", "luot_thoai": [2],
            "trich_dan": ["dị ứng cua"]},                       # bịa: không có trong lượt
           {"chu_the": "bệnh nhân", "noi_dung": "dị ứng tôm", "luot_thoai": [1],
            "trich_dan": ["dị ứng tôm"]},                       # dẫn sai lượt
           {"chu_the": "bệnh nhân", "noi_dung": "tăng huyết áp", "luot_thoai": [9],
            "trich_dan": ["huyết áp"]},                         # lượt không tồn tại
           {"chu_the": "bệnh nhân", "noi_dung": "sốt", "luot_thoai": [2]}]  # không trích
    giu, bo = loc_trong_van(HT, moi)
    assert [p["noi_dung"] for p in giu] == ["dị ứng tôm"] and len(bo) == 4
    ra = gop_ket_qua_quet_lai([{"trich_dan": ["Tôi uống amlodipin 5mg"], "luot_thoai": [2]}], giu)
    for p in ra:
        if p.get("nguon") == "quet_lai":
            for so in p["luot_thoai"]:
                assert all(t.lower() in _luot(HT, so) for t in p["trich_dan"])


def test_loc_bo_menh_de_trich_ve_khac_cung_luot():
    """Lần quét lại chỉ được hỏi về vế đã chọn. Mệnh đề trích một vế KHÁC của cùng lượt
    (dù câu trích có thật trong lượt) bị bỏ và được đếm."""
    ve = ve_chua_phu(HT, [{"trich_dan": "Tôi uống amlodipin 5mg", "bang_chung": [2]}])
    assert [v["van"] for v in ve] == ["còn dị ứng tôm"]
    moi = [{"noi_dung": "dị ứng tôm", "luot_thoai": [2], "trich_dan": ["dị ứng tôm"]},
           {"noi_dung": "uống amlodipin", "luot_thoai": [2], "trich_dan": ["uống amlodipin 5mg"]},
           {"noi_dung": "dùng thuốc", "luot_thoai": [1], "trich_dan": ["dùng thuốc"]}]
    giu, bo = loc_trong_van(HT, moi, ve=ve)
    assert [p["noi_dung"] for p in giu] == ["dị ứng tôm"]
    assert [p["noi_dung"] for p in bo] == ["uống amlodipin", "dùng thuốc"]
    # Không truyền vế: chỉ kiểm câu trích nằm trong lượt dẫn, như trước.
    assert len(loc_trong_van(HT, moi)[0]) == 3


def test_loc_giu_cau_trich_tran_qua_ranh_gioi_ve():
    ve = ve_chua_phu(HT, [{"trich_dan": "Tôi uống amlodipin 5mg", "bang_chung": [2]}])
    moi = [{"noi_dung": "dị ứng tôm", "luot_thoai": [2], "trich_dan": ["5mg, còn dị ứng tôm"]}]
    assert len(loc_trong_van(HT, moi, ve=ve)[0]) == 1


def test_gop_doi_lai_quan_he_voi_theo_vi_tri_moi():
    cu = [{"trich_dan": ["a"], "luot_thoai": [1]}]
    moi = [{"trich_dan": ["a"], "luot_thoai": [1]},                    # trùng -> bỏ
           {"trich_dan": ["b"], "luot_thoai": [1]},
           {"trich_dan": ["c"], "luot_thoai": [1], "quan_he": "đính chính", "quan_he_voi": 1},
           {"trich_dan": ["d"], "luot_thoai": [1], "quan_he": "bổ sung", "quan_he_voi": 0}]
    ra = gop_ket_qua_quet_lai(cu, moi)
    assert [p["trich_dan"][0] for p in ra] == ["a", "b", "c", "d"]
    assert ra[2]["quan_he_voi"] == 1                 # trỏ "b", nay ở vị trí 1
    assert ra[3]["quan_he"] == "không" and ra[3]["quan_he_voi"] is None  # trỏ bản bị bỏ


# ---------------------------------------------------------------- tích hợp chay_trung_gian

PS_DAU = [{"chu_the": "bệnh nhân", "noi_dung": "uống amlodipin 5mg", "do_chac_chan": "chắc chắn",
           "phu_dinh": False, "tinh_huong": "thực tế", "thoi_gian_su_kien": "hiện tại",
           "moc_thoi_gian": None, "quan_he": "không", "quan_he_voi": None,
           "luot_thoai": [2], "trich_dan": ["Tôi uống amlodipin 5mg"], "hanh_vi": "trả lời"}]
PS_DI_UNG = {"chu_the": "bệnh nhân", "noi_dung": "dị ứng tôm", "do_chac_chan": "chắc chắn",
             "phu_dinh": False, "tinh_huong": "thực tế", "thoi_gian_su_kien": "quá khứ",
             "moc_thoi_gian": None, "quan_he": "không", "quan_he_voi": None,
             "luot_thoai": [2], "trich_dan": ["dị ứng tôm"], "hanh_vi": "trả lời"}
PS_BIA = dict(PS_DI_UNG, noi_dung="dị ứng cua", trich_dan=["dị ứng cua"])


@pytest.fixture
def gia(monkeypatch):
    """Thay bước trích đầu và `_sinh` bằng hàm giả; đếm số lần sinh thêm."""
    goi = []

    def dat(ps_dau, ps_quet_lai=()):
        def _trich(tok, model, prefix_fn, mau_list, max_token=1536, vi_du=True):
            return [{"id": m["id"], "so_luot": 2, "json_hop_le": True, "ly_do": "",
                     "phat_bieu": [dict(p) for p in ps_dau], "tho": ""} for m in mau_list]

        def _sinh(tok, model, noi_dung, max_token=512, **kw):
            goi.append(noi_dung)
            return json.dumps({"phat_bieu": list(ps_quet_lai)}, ensure_ascii=False), 10, 5

        monkeypatch.setattr(bakeoff, "trich", _trich)
        monkeypatch.setattr(nhanh, "_sinh", _sinh)
    dat.goi = goi
    return dat


def _chay(quet_lai):
    return nhanh.chay_trung_gian([{"id": "m1", "input": HT, "output": ""}], None, object(), None,
                                 "C_khoa", quet_lai=quet_lai)[0]


def test_chay_trung_gian_quet_lai_sinh_dung_mot_lan_khi_co_ve(gia):
    gia(PS_DAU, [PS_DI_UNG, PS_BIA])
    ra = _chay(True)
    assert len(gia.goi) == 1 and "còn dị ứng tôm" in gia.goi[0]
    nd = [p["noi_dung"] for p in ra["phat_bieu"]]
    assert "dị ứng tôm" in nd and "dị ứng cua" not in nd
    # Mệnh đề quét lại cũng đi qua khoá K1–K6: có một kết quả khoá cho mỗi mệnh đề.
    assert len(ra["khoa"]) == len(ra["phat_bieu"]) == 2
    assert ra["so_luot_goi"] == 2
    assert ra["quet_lai"] == {"so_ve": 1, "so_moi": 1, "so_bo_ngoai_van": 1, "so_bo_trung": 0}


def test_chay_trung_gian_quet_lai_khong_sinh_khi_khong_con_ve(gia):
    gia(PS_DAU + [PS_DI_UNG])
    ra = _chay(True)
    assert gia.goi == [] and ra["so_luot_goi"] == 1 and ra["quet_lai"]["so_ve"] == 0


def test_chay_trung_gian_mac_dinh_khong_quet_lai(gia):
    gia(PS_DAU, [PS_DI_UNG])
    ra = nhanh.chay_trung_gian([{"id": "m1", "input": HT, "output": ""}], None, object(), None,
                               "C_khoa")[0]
    assert gia.goi == [] and "quet_lai" not in ra and len(ra["phat_bieu"]) == 1


def test_quet_lai_chi_cho_nhanh_co_khoa(gia):
    """Nhánh không có K1–K6 thì mệnh đề quét lại sẽ vào thân mà không qua khoá: cấm."""
    gia(PS_DAU, [PS_DI_UNG])
    with pytest.raises(ValueError):
        nhanh.chay_trung_gian([{"id": "m1", "input": HT, "output": ""}], None, object(), None,
                              "C", quet_lai=True)


def test_quet_lai_can_mo_hinh(gia):
    gia(PS_DAU, [PS_DI_UNG])
    with pytest.raises(SystemExit):
        nhanh.chay_trung_gian([{"id": "m1", "input": HT, "output": ""}], None, None, None,
                              "C_khoa", quet_lai=True)
