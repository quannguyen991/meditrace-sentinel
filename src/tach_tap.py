# -*- coding: utf-8 -*-
"""Chia bo du lieu thanh BON tap tach roi.

Vi sao bon tap chu khong phai mot:

  train           huan luyen mo hinh
  phat_trien      DUOC xem loi, sua phuong phap, chon nguong
  kiem_tra_cuoi   KHONG duoc mo truoc Cua 5 — moi con so trong bao cao cuoi lay tu day
  kiem_tra_chung  lay ngau nhien, de bao cao chat luong CHUNG

Ban ke hoach dau tien dung CUNG MOT tap cho ca viec tham do loi lan danh gia cuoi.
Nhu vay tap do da thanh tap phat trien va khong con danh gia duoc nua.

`phat_trien` va `kiem_tra_cuoi` deu chon tu nhom co luot "Nguoi nha", nen chung la
tap kiem tra CHUYEN BIET cho tinh huong nhieu nguoi noi, KHONG dai dien cho toan bo
hoi thoai. Do la ly do co them `kiem_tra_chung`.

    python -m src.tach_tap
"""
import io
import random
import sys

from src import du_lieu, duong_dan

SEED = 42
SO_PHAT_TRIEN = 35
SO_KIEM_TRA_CUOI = 40
SO_KIEM_TRA_CHUNG = 60


def chia(mau_list, seed=SEED):
    rnd = random.Random(seed)

    co_nn = du_lieu.loc_mau_co_nguoi_nha(mau_list)
    rnd.shuffle(co_nn)

    phat_trien = co_nn[:SO_PHAT_TRIEN]
    kiem_tra_cuoi = co_nn[SO_PHAT_TRIEN:SO_PHAT_TRIEN + SO_KIEM_TRA_CUOI]
    # co_nn[SO_PHAT_TRIEN + SO_KIEM_TRA_CUOI:] van o lai huan luyen — co y.
    # Bo het mau nguoi nha khoi train thi mo hinh khong hoc duoc tinh huong
    # nhieu nguoi noi, va baseline yeu gia theo chieu nguoc lai.

    id_giu = {m["id"] for m in phat_trien + kiem_tra_cuoi}
    con_lai = [m for m in mau_list if m["id"] not in id_giu]
    rnd.shuffle(con_lai)

    kiem_tra_chung = con_lai[:SO_KIEM_TRA_CHUNG]
    train = con_lai[SO_KIEM_TRA_CHUNG:]

    return {
        "train": train,
        "phat_trien": phat_trien,
        "kiem_tra_cuoi": kiem_tra_cuoi,
        "kiem_tra_chung": kiem_tra_chung,
    }


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    mau = du_lieu.nap_mau(duong_dan.TRAIN_JSONL)
    tap = chia(mau)
    for ten, ds in tap.items():
        dp = duong_dan.THU_MUC_DU_LIEU / f"{ten}.jsonl"
        du_lieu.ghi_mau(dp, ds)
        so_nn = len(du_lieu.loc_mau_co_nguoi_nha(ds))
        print(f"{ten:16} {len(ds):5d} mau  ({so_nn} co nguoi nha)")
    print(f"{'TONG':16} {sum(len(d) for d in tap.values()):5d}")


if __name__ == "__main__":
    main()
