# -*- coding: utf-8 -*-
"""doan_chua_ghi voi nguong_phu: mot doan chi coi la da ghi khi du nhieu tu noi dung cua no
co trong menh de dan toi luot do — khong phai chi chung mot tu."""
from src import khoa_bang_chung as kbc
from src.phat_bieu import PhatBieu

HT = "Bác sĩ: Chị kể đi.\nNgười nhà: Cháu ho ba ngày nay, mẹ em bị tiểu đường lâu năm."


def _ps():
    # Menh de chi ghi y "ho", nhung co chu "lâu" (lam gia doan sau la da ghi theo tieu chi cu)
    return [PhatBieu(id=0, nguoi_noi="người nhà", chu_the_id=0, noi_dung="ho ba ngày nay, lâu rồi",
                     bang_chung=[2], trich_dan=["Cháu ho ba ngày nay"])]


def _chua_ghi(nguong):
    ps = _ps()
    cl = kbc._luot(HT)
    kq = [kbc.khoa_mot(p, cl, False) for p in ps]
    return kbc.doan_chua_ghi(kq, ps, cl, nguong_phu=nguong)


def test_luot_dai_hai_y_nguong_0_5():
    ra = _chua_ghi(0.5)
    doan = [d for d in ra if "tiểu đường" in d["doan"]]
    assert doan and doan[0]["vai"] == "người nhà" and doan[0]["luot"] == 2


def test_hanh_vi_cu_khi_none():
    assert not [d for d in _chua_ghi(None) if "tiểu đường" in d["doan"]]


def test_doan_da_ghi_du_tu_thi_im():
    ps = [PhatBieu(id=0, nguoi_noi="người nhà", chu_the_id=1, noi_dung="mẹ bị tiểu đường lâu năm",
                   bang_chung=[2], trich_dan=["mẹ em bị tiểu đường lâu năm"]),
          PhatBieu(id=1, nguoi_noi="người nhà", chu_the_id=0, noi_dung="ho ba ngày",
                   bang_chung=[2], trich_dan=["Cháu ho ba ngày nay"])]
    cl = kbc._luot(HT)
    kq = [kbc.khoa_mot(p, cl, False) for p in ps]
    assert [d for d in kbc.doan_chua_ghi(kq, ps, cl, nguong_phu=0.5) if d["luot"] == 2] == []


def test_mac_dinh_mo_dun_duoc_dung():
    cu = kbc.NGUONG_PHU_MAC_DINH
    try:
        kbc.NGUONG_PHU_MAC_DINH = 0.5
        ra = kbc.khoa_ca(_ps(), HT, bat_buoc_trich_dan=False)["doan_chua_ghi"]
        assert [d for d in ra if "tiểu đường" in d["doan"]]
    finally:
        kbc.NGUONG_PHU_MAC_DINH = cu
