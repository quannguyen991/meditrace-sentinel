# -*- coding: utf-8 -*-
"""Don tep dem trich CHI KHI no thuoc bo du lieu khac.

    python tools/don-dem-trich.py <tap> [<tap> ...]

VI SAO CO TEP NAY (14/09/2026).

Ban dau chuoi don tep dem bang cach doi ten TAT CA tep `trich_<tap>*` moi lan
khoi dong. Cach do chan duoc lo~i "dem cua bo nay dung cho bo khac" — lo~i im lang
thu ba cua du an — nhung no bien chuoi thanh thu KHONG KHOI DONG LAI DUOC: dang
chay do dang ma phai dung lai (het dien, sua mot buoc, doi thu tu) thi moi tep
dem da tinh deu bi vut, va o nhip 5 phut/ca thi 240 ca la 20 gio GPU.

Cho nay can mot phep kiem CHINH XAC chu khong phai mot cai choi quet sach:

    tep dem hop le  <=>  moi ban ghi trong no co `id` thuoc bo du lieu hien tai

Neu hop le thi GIU — chay tiep dung cho do. Neu co du mot ban ghi la thi doi ten
ca tep, vi khong biet con ban ghi nao khac cung la.

KHONG so sanh noi dung: tep dem chi luu ket qua trich, khong luu lai hoi thoai
goc, nen `id` la thu duy nhat doi chieu duoc. Hai bo du lieu khac the he ma trung
id VA trung so ca thi phep kiem nay khong bat duoc — do la ly do van tay bo du
lieu (`van_tay_bo`) van phai ton tai ben canh.
"""
import json
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
DU_LIEU = GOC / "data"


def _ids(duong: Path) -> set:
    ra = set()
    with open(duong, encoding="utf-8") as f:
        for dong in f:
            dong = dong.strip()
            if dong:
                ra.add(json.loads(dong).get("id"))
    return ra


def don_mot_tap(tap: str) -> None:
    bo = DU_LIEU / f"{tap}.jsonl"
    if not bo.exists():
        print(f"  {tap}: khong co tep bo du lieu, bo qua")
        return

    dem = sorted(DU_LIEU.glob(f"trich_{tap}_*.jsonl"))
    if not dem:
        print(f"  {tap}: chua co tep dem")
        return

    hop_le = _ids(bo)
    for d in dem:
        try:
            co = _ids(d)
        except Exception as loi:  # tep hong thi cung phai don
            print(f"  {d.name}: doc khong duoc ({loi}) -> doi ten")
            co = {None}
        la = {x for x in co if x not in hop_le}
        if not la:
            print(f"  {d.name}: {len(co)} ban ghi, tat ca thuoc bo hien tai -> GIU")
            continue
        moi = d.with_suffix(d.suffix + ".khac-bo")
        n = 1
        while moi.exists():
            n += 1
            moi = d.with_suffix(d.suffix + f".khac-bo{n}")
        d.rename(moi)
        print(f"  {d.name}: {len(la)}/{len(co)} ban ghi KHONG thuoc bo hien tai "
              f"-> doi ten thanh {moi.name}")


def main() -> None:
    cac_tap = sys.argv[1:]
    if not cac_tap:
        raise SystemExit("Dung: python tools/don-dem-trich.py <tap> [<tap> ...]")
    print("Don tep dem trich:")
    for tap in cac_tap:
        don_mot_tap(tap)


if __name__ == "__main__":
    main()
