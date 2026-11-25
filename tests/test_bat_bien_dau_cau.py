# -*- coding: utf-8 -*-
"""Lop canh bao phai gan nhu khong doi khi hoi thoai mat dau cau va viet thuong."""
from tools.do_bat_bien_dau_cau import bo_dau_hoi_thoai, do


def _pb(id, nd, luot, trich, **kw):
    d = dict(id=id, nguoi_noi=kw.pop("nguoi_noi", "bệnh nhân"), chu_the_id=kw.pop("chu_the_id", 0),
             noi_dung=nd, bang_chung=luot, trich_dan=trich)
    d.update(kw)
    return d


CA = [
    {"input": "Bác sĩ: Chị có dị ứng thuốc gì không?\nBệnh nhân: Dạ không ạ.\n"
              "Bác sĩ: Chị có đang uống thuốc gì không?\nBệnh nhân: Dạ, em đang uống amlodipin 5mg mỗi sáng.",
     "phat_bieu": [_pb(0, "dị ứng thuốc", [1, 2], ["Chị có dị ứng thuốc gì không", "Dạ không ạ"], phu_dinh=True),
                   _pb(1, "amlodipin 5mg mỗi sáng", [4], ["em đang uống amlodipin 5mg mỗi sáng"],
                       thuoc={"ten": "amlodipin", "lieu": "5mg", "so_lan": "mỗi sáng"})]},
    {"input": "Bác sĩ: Ho mấy ngày rồi?\nBệnh nhân: Em ho năm ngày rồi.\nBệnh nhân: À không, ba ngày thôi ạ.\n"
              "Bác sĩ: Có sốt không?\nBệnh nhân: Có, sốt về chiều ạ.",
     "phat_bieu": [_pb(0, "ho ba ngày", [2, 3], ["ba ngày thôi ạ"]),
                   _pb(1, "sốt về chiều", [4, 5], ["Có sốt không", "sốt về chiều ạ"])]},
    {"input": "Bác sĩ: Trong nhà có ai bị bệnh gì không?\nNgười nhà: Mẹ cháu bị tăng huyết áp ạ.\n"
              "Bác sĩ: Bé có bị dị ứng gì không?\nNgười nhà: Dạ, bé dị ứng tôm.",
     "phat_bieu": [_pb(0, "mẹ bị tăng huyết áp", [2], ["Mẹ cháu bị tăng huyết áp ạ"], nguoi_noi="người nhà",
                       chu_the_id=1),
                   _pb(1, "dị ứng tôm", [4], ["bé dị ứng tôm"], nguoi_noi="người nhà")]},
]


def test_bo_dau_hoi_thoai_giu_nhan_vai():
    assert bo_dau_hoi_thoai("Bác sĩ: Có sốt không?\nBệnh nhân: Có, 38,5 độ.") == \
        "Bác sĩ: có sốt không\nBệnh nhân: có 38,5 độ"


def test_ca_mau_bat_bien():
    kq = do([], CA)
    assert kq["ty_le_ma_giu_nguyen"] >= 0.9, kq
    assert kq["jaccard"] >= 0.9, kq
