# -*- coding: utf-8 -*-
"""Cat mot loi thoai thanh DOAN theo dau cau — MOT dinh nghia dung chung.

Dung o hai noi, va hai noi PHAI cat giong nhau:

  sinh_hoi_thoai_viet  tim doan bang chung cho `trich_dan` cua dap an
  khoa_bang_chung      tim doan hoi thoai CHUA duoc phat bieu nao dan toi

Hai cach cat khac nhau thi "doan" cua dap an va "doan" ma khoa kiem khong khop
nhau, va khong co gi bao loi — ho loi "hai khau dung hai don vi van ban" da gap
o `sua_cuc_bo._co`.

Dau phay va dau cham GIUA HAI CHU SO khong tach: "38,5 do", "37.8". Dau hai cham
khong tach: "Sinh hieu em do duoc: ..." la mot y.
"""
from typing import List, Tuple

DAU_DOAN = ";!?…"


def cac_doan(van: str) -> List[Tuple[int, int]]:
    """-> [(bat_dau, ket_thuc)] tren chinh chuoi `van`, da bo khoang trang hai
    dau moi doan. Doan rong bi bo."""
    ra, dau, n = [], 0, len(van)
    for i, c in enumerate(van):
        tach = c in DAU_DOAN or (
            c in ",." and not (0 < i < n - 1 and van[i - 1].isdigit()
                               and van[i + 1].isdigit()))
        if tach:
            _them(ra, van, dau, i)
            dau = i + 1
    _them(ra, van, dau, n)
    return ra


def dau_ket(van: str, doan: Tuple[int, int]) -> str:
    """Dau cau NGAY SAU doan ("" neu het chuoi) — de biet doan co la cau hoi."""
    j = doan[1]
    while j < len(van) and van[j].isspace():
        j += 1
    return van[j] if j < len(van) else ""


def _them(ra, van, a, b):
    while a < b and van[a].isspace():
        a += 1
    while b > a and van[b - 1].isspace():
        b -= 1
    if b > a:
        ra.append((a, b))
