# -*- coding: utf-8 -*-
"""Nhieu ASR: lam xau CHU, khong duoc dong toi DAP AN.

Ba bat bien duoc canh o day, theo dung thu tu quan trong:
  1. giu nguyen so tu — neu khong, trich dan khong anh xa lai duoc
  2. khong dung toi tu chi nguoi / tu so / tu phu dinh — neu khong, dap an sai
  3. khong vao duong huan luyen
"""
import random

import pytest

from src import nhieu_asr as na


def test_bo_dau_bo_ca_chu_d():
    assert na.bo_dau("sốt") == "sot"
    assert na.bo_dau("đau") == "dau"
    assert na.bo_dau("Đau bụng") == "Dau bung"


def test_giu_nguyen_so_tu():
    dong = "Bệnh nhân: Cháu sốt cao từ hôm qua, đau bụng quặn từng cơn ạ."
    ra = na.nhieu_dong(dong, random.Random(1), ti_le=1.0)
    _, _, than_goc = dong.partition(": ")
    _, _, than_ra = ra.partition(": ")
    assert len(than_ra.split(" ")) == len(than_goc.split(" "))


def test_giu_nhan_vai_o_dau_dong():
    """Nhan vai la cong cu danh so luot cua bo sinh, khong phai loi ai noi."""
    ra = na.nhieu_dong("Bác sĩ: Cháu đau ở đâu?", random.Random(2), ti_le=1.0)
    assert ra.startswith("Bác sĩ: ")


@pytest.mark.parametrize("tu", ["bà", "bố", "mẹ", "cô", "chú", "dì", "cháu",
                                "năm", "bốn", "ba", "không", "chưa", "hôm"])
def test_khong_bo_dau_tu_nguy_hiem(tu):
    """"bà" -> "ba" la doi nguoi, "năm" -> "nam" la doi so. Ca hai deu la doi
    DAP AN chu khong phai lam nhieu."""
    assert na.cam_dung(tu), f"{tu} phai nam trong nhom cam"
    assert na.nhieu_tu(tu, random.Random(3), ti_le=1.0) == tu


def test_khong_dung_toi_con_so():
    ra = na.nhieu_dong("Người nhà: Bà sốt 38,5 độ từ 3 hôm nay.",
                       random.Random(4), ti_le=1.0)
    assert "38,5" in ra and " 3 " in ra


def test_ti_le_0_thi_chi_mat_dau_cau():
    dong = "Bệnh nhân: Cháu mệt lắm, chóng mặt."
    ra = na.nhieu_dong(dong, random.Random(5), ti_le=0.0)
    assert ra == "Bệnh nhân: cháu mệt lắm chóng mặt"


def test_anh_xa_trich_dan_theo_chi_so_tu():
    goc = "Người nhà: Cháu nôn ba lần từ tối qua ạ."
    nhieu = na.nhieu_dong(goc, random.Random(6), ti_le=1.0)
    ra = na.nhieu_trich("nôn ba lần từ tối qua", goc, nhieu)
    assert ra in nhieu
    assert len(ra.split(" ")) == 6


def test_nhieu_ca_giu_dap_an_tru_trich_dan():
    ca = {
        "id": "x",
        "input": "Bác sĩ: Cháu bị sao?\nBệnh nhân: Cháu sốt cao từ tối qua ạ.",
        "dap_an": [
            {"chu_the": "bệnh nhân", "noi_dung": "sốt cao", "muc": "BỆNH SỬ",
             "luot": [2], "trich_dan": ["sốt cao từ tối qua"]},
        ],
    }
    ra = na.nhieu_ca(ca, random.Random(7), ti_le=1.0)

    # dap an khong doi, tru trich dan
    goc_m, ra_m = ca["dap_an"][0], ra["dap_an"][0]
    assert {k: v for k, v in ra_m.items() if k != "trich_dan"} == \
           {k: v for k, v in goc_m.items() if k != "trich_dan"}

    # trich dan moi phai NAM TRONG hoi thoai da lam nhieu — dieu kien de K1 chay
    assert ra_m["trich_dan"][0] in ra["input"]
    assert ca["input"] != ra["input"]


def test_khong_sua_ca_goc():
    ca = {"id": "x", "input": "Bệnh nhân: Cháu sốt.",
          "dap_an": [{"noi_dung": "sốt", "luot": [1], "trich_dan": ["Cháu sốt"]}]}
    goc = ca["input"]
    na.nhieu_ca(ca, random.Random(8), ti_le=1.0)
    assert ca["input"] == goc, "phai tra ban moi, khong sua ca goc"


def test_khong_khau_huan_luyen_nao_goi_nhieu_asr():
    """Cung mot le voi bang phuong ngu: bo lam nhieu CHI de do.

    Neu mot ngay nao do duong huan luyen nhap khau tep nay, test do se hong o
    day chu khong hong am tham o so lieu."""
    import ast
    import pathlib

    for ten in ("du_lieu_trich.py", "sinh_hoi_thoai_viet.py", "train_baseline.py",
                "du_lieu.py", "tang_cuong.py"):
        cay = ast.parse(pathlib.Path("src", ten).read_text(encoding="utf-8"))
        for nut in ast.walk(cay):
            if isinstance(nut, ast.ImportFrom) and (nut.module or "").endswith("nhieu_asr"):
                pytest.fail(f"{ten} nhap khau nhieu_asr — bo lam nhieu chi de do")
            if isinstance(nut, ast.Import):
                for a in nut.names:
                    assert not a.name.endswith("nhieu_asr"), \
                        f"{ten} nhap khau nhieu_asr — bo lam nhieu chi de do"


def test_trich_dan_ket_thuc_o_tu_dinh_dau_cau():
    """Bay da vap that: dap an trich "... roi roi", loi thoai ghi "... roi roi."

    Dinh mot dau cham o tu cuoi lam ca doan truot, va hau qua khong lo ra ngay:
    trich dan cu duoc giu nguyen, roi `khoa_bang_chung` chan oan ca menh de dung.
    """
    goc = "Bệnh nhân: Dạ, con đi ngoài khó nửa năm rồi rồi."
    nhieu = na.nhieu_dong(goc, random.Random(11), ti_le=1.0)
    ra = na.nhieu_trich("con đi ngoài khó nửa năm rồi rồi", goc, nhieu)
    assert ra is not None
    assert ra in nhieu


def test_khong_tim_thay_thi_tra_none():
    goc = "Bệnh nhân: Cháu sốt."
    nhieu = na.nhieu_dong(goc, random.Random(12), ti_le=1.0)
    assert na.nhieu_trich("chuyện không có trong câu này", goc, nhieu) is None
