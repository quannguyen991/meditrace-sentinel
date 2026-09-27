# -*- coding: utf-8 -*-
"""Tu phuong ngu tu bang GPT KHONG vao khuon train (quyet dinh 11/09/2026).

Bang thay cua bo sinh lay tu tu dien do GPT sinh; du an khong dung mo hinh ngon
ngu thuong mai o bat ky khau nao, ke ca sinh du lieu huan luyen. Xem
`sinh_hoi_thoai_viet.PHUONG_NGU_TRONG_TRAIN` va docs/nguon-du-lieu.md.
"""
import random

from src import sinh_hoi_thoai_viet as sh


def _ca(ma, seed, tap, mien):
    return sh.sinh_mot_ca(ma, random.Random(seed),
                          sh.TuyChon(chi_tap=tap, ep_mien=mien))


def test_khuon_TRAIN_khong_co_tu_phuong_ngu_tu_bang_GPT():
    assert not sh.PHUONG_NGU_TRONG_TRAIN
    for i in range(40):
        for mien in ("nam", "trung"):
            ca = _ca(f"t{i}", 500 + i, "train", mien)
            assert not ca["tu_phuong_ngu"], (ca["id"], ca["tu_phuong_ngu"])


def test_khuon_PHAT_TRIEN_van_co_phuong_ngu():
    co = sum(bool(_ca(f"d{i}", 700 + i, "phat_trien", "nam")["tu_phuong_ngu"])
             for i in range(40))
    assert co > 0
