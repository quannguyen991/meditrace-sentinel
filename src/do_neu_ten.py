# -*- coding: utf-8 -*-
"""Ban nhap co NEU TEN NGUOI cho menh de khong phai cua benh nhan khong.

VI SAO CAN MOT THUOC DO RIENG CHO VIEC NAY — do duoc 11/09/2026, va no la bang
chung manh nhat cua ca du an ve chuyen thuoc do do thu khac voi thu no khai.

Muc TIEN SU GIA DINH VA XA HOI cua ban nhap, tren tap phat trien the he 2:

    ban tham chieu      22 cau, 22 neu ten nguoi   (100%)
    nhanh B, C, D       50, 50, 53 cau, **0 neu ten nguoi**   (0%)

Mot bac si doc `TIEN SU GIA DINH VA XA HOI / roi loan mo mau` khong biet AI bi roi
loan mo mau. Ban nhap do khong dung duoc.

VA `f1_quy_gan` KHONG THAY GI. Sau khi sua de ban nhap neu ten (0% -> 100%):

    B truoc sua   0,8032
    B sau sua     0,8032      hieu 0,0000, KTC [0,0000; 0,0000]

Doi dung bang khong. Ly do: `thuoc_do_quy_gan._chu_the_cua_cau` suy chu the tu TEN
MUC khi cau khong co tu chi nguoi (`MUC_NGUOI_NHA = ("GIA DINH",)`). Nen mot cau
KHONG neu ten nam trong muc gia dinh van duoc cham la "nguoi nha" — dung 100% o
tang 4.

    Con so 100% o tang 4 la diem cua viec XEP DUNG MUC, khong phai diem cua viec
    GAN DUNG NGUOI.

DAY LA LAN THU BA trong hai ngay:

    ROUGE         mu truoc lo~i doi chu the      0,9799 so voi 0,9661
    f1_quy_gan    bi tang de chi phoi            xep regex tren duong ong
    f1_quy_gan    mu truoc viec NEU TEN NGUOI    0% -> 100% lam diem doi 0,0000

Hai lan dau la chuyen do lon. Lan nay la chuyen do KHONG HE do.

GIOI HAN CUA CHINH THUOC DO NAY: no kiem su CO MAT cua mot tu chi nguoi o dau cau,
khong kiem tu do co DUNG NGUOI khong. Mot ban nhap ghi "bo roi loan mo mau" trong
khi dap an la "me" se dat o day. Nen doc no cung `do_tang_quy_gan`, khong thay the.

    python -m src.do_neu_ten --tep B=data/ra_B_viet_phat_trien_th2.jsonl
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

from src import sinh_benh_an

# Tu chi nguoi dung o DAU cau trong muc tien su gia dinh. Lay tu chinh bo sinh
# de khong troi: `nl.NGUOI_NHA` la danh sach vai nguoi nha that.
VAI_NGUOI = ("mẹ", "bố", "ba", "bà", "ông", "chị", "anh", "cô", "dì", "chú",
             "bác", "vợ", "chồng", "con", "em", "cháu", "người nhà", "gia đình")

MUC_NGUOI_KHAC = sinh_benh_an.MUC_NGUOI_KHAC


def _la_tieu_de(dong):
    d = dong.strip()
    return bool(d) and d == d.upper() and len(d) > 3


def cau_trong_muc(van_ban, muc=MUC_NGUOI_KHAC):
    """-> danh sach cau nam trong `muc`.

    Tach theo dau cau chu khong theo dong: `sinh_benh_an` noi nhieu menh de vao
    mot dong bang dau cham.
    """
    ra = []
    trong = False
    for dong in str(van_ban or "").split("\n"):
        d = dong.strip()
        if d == muc:
            trong = True
            continue
        if _la_tieu_de(d):
            trong = False
            continue
        if trong and d:
            for cau in re.split(r"(?<=[.;])\s+", d):
                cau = cau.strip().lstrip("- ").strip()
                if cau:
                    ra.append(cau)
    return ra


def co_neu_ten(cau):
    """Cau co bat dau bang mot tu chi nguoi khong.

    Chi xet DAU cau: `sinh_benh_an.dien_dat` dat ten o dau theo dang "<ten>: ",
    va mot tu chi nguoi nam giua cau thuong la mot phan noi dung
    ("di ung thuoc cua me cho") chu khong phai nhan chu the.
    """
    dau = str(cau or "").strip().lower().lstrip("- ").strip()
    return any(dau.startswith(v) for v in VAI_NGUOI)


def cham(ket_qua, khoa="du_doan", muc=MUC_NGUOI_KHAC):
    """-> {so_cau, so_neu_ten, ty_le}."""
    co = tong = 0
    for x in ket_qua:
        for cau in cau_trong_muc(x.get(khoa), muc):
            tong += 1
            co += 1 if co_neu_ten(cau) else 0
    return {"so_cau": tong, "so_neu_ten": co,
            "ty_le": co / tong if tong else float("nan")}


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tep", nargs="+", required=True, metavar="TEN=DUONG_DAN")
    ap.add_argument("--muc", default=MUC_NGUOI_KHAC)
    a = ap.parse_args()

    print(f"Muc `{a.muc}` — cau co neu ten nguoi hay khong\n")
    print(f"| Nhánh | Số câu | Nêu tên | Tỷ lệ |")
    print(f"|---|---|---|---|")
    dau = True
    for x in a.tep:
        ten, _, duong = x.partition("=")
        p = Path(duong)
        if not p.exists():
            print(f"| `{ten}` | — | — | không có tệp |")
            continue
        kq = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
        if dau:
            t = cham(kq, "tham_chieu", a.muc)
            print(f"| *tham chiếu* | {t['so_cau']} | {t['so_neu_ten']} | "
                  f"{t['ty_le']:.0%} |")
            dau = False
        d = cham(kq, "du_doan", a.muc)
        ty = "—" if d["so_cau"] == 0 else f"{d['ty_le']:.0%}"
        print(f"| `{ten}` | {d['so_cau']} | {d['so_neu_ten']} | {ty} |")


if __name__ == "__main__":
    main()
