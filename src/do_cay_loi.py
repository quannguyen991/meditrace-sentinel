# -*- coding: utf-8 -*-
"""Do lop canh bao bang LOI CAY NHAN TAO — khong nhan nguoi, khong mo hinh (25/11/2026).

Ban ghi sach = dap an (`danh_gia_khoa.phat_bieu_tu_dap_an`). Moi canh bao tren ban sach la
BAO NHAM (dap an coi la dung; gioi han: dap an co the thieu cau am tinh chung). Moi ca, moi loai
loi: cay DUNG MOT loi (`tools.cay_loi`) roi xem lop canh bao co bat dung cho, dung nhom khong.

    python -m src.do_cay_loi --tap dieu_chinh --ra-json docs/ket-qua/cay-loi-moc.json
    python -m src.do_cay_loi --tap giu_kin --toi-da-khoa-luat --ra-json ...   # MOT lan

Moi so ghi "tren loi cay nhan tao". Dang ky truoc: docs/dang-ky-truoc-bo-luat.md (sua doi 25/11).
"""
import argparse
import hashlib
import io
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from src.canh_bao import gop
from src.danh_gia_khoa import phat_bieu_tu_dap_an, vao_than
from tools import cay_loi


def _ps(ca):
    return phat_bieu_tu_dap_an(ca)


def _rng(seed, ca_id, loai):
    return random.Random(int(hashlib.sha256(f"{seed}:{ca_id}:{loai}".encode()).hexdigest()[:12], 16))


def wilson(k, n, z=1.96):
    if n == 0:
        return [0.0, 1.0]
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(max(0.0, c - h), 3), round(min(1.0, c + h), 3)]


def _r(x):
    return round(x, 3)


def _moi_canh_bao(kq):
    """-> [(phat_bieu_id hoac None neu toan ca, canh bao)]"""
    ra = [(int(i), c) for i, v in kq["theo_phat_bieu"].items() for c in v["tat_ca"]]
    return ra + [(None, c) for c in kq["toan_ca"]]


def _cay_kho(ps, ca, l, rng):
    """Bo chuyen: loi kho cay vao dap an -> (PhatBieu moi, Cay). id PhatBieu = chi so dap an."""
    from tools import cay_loi_kho
    r = cay_loi_kho.cay_kho(ca, l, rng)
    if r is None:
        return None
    moi, (c,) = r
    ps2 = phat_bieu_tu_dap_an(moi)
    if c.chi_so not in {p.id for p in ps2}:
        return None
    return ps2, cay_loi.Cay(l, c.chi_so, moi["dap_an"][c.chi_so].get("luot") or [], c.mo_ta)


def do(ds, loai=cay_loi.LOAI_CAY, seed=42, vi_du=3, kho=False):
    """`kho=True`: dung loi KHO (`tools.cay_loi_kho`) thay cho bo co ban."""
    if kho:
        from tools import cay_loi_kho
        loai = cay_loi_kho.LOAI_KHO if loai is cay_loi.LOAI_CAY else loai
        ham_cay, nhom_dung_cua = _cay_kho, cay_loi_kho.NHOM_KHO
    else:
        ham_cay, nhom_dung_cua = cay_loi.cay, cay_loi.NHOM_DUNG
    sach_ma, so_ca, than, chan = Counter(), 0, 0, 0
    tl = {l: Counter() for l in loai}
    ma_tong, ma_dung = Counter(), Counter()
    lot = defaultdict(list)
    for ca in ds:
        ps = _ps(ca)
        kq = gop.chay(ps, ca["input"])
        so_ca += 1
        sach_ma.update(c.ma for _, c in _moi_canh_bao(kq))
        for p in ps:
            if vao_than(p):
                than += 1
                chan += kq["trang_thai_D"].get(p.id, {}).get("trang_thai") == gop.CAN_XAC_NHAN
        for l in loai:
            r = ham_cay(ps, ca, l, _rng(seed, ca["id"], l))
            t = tl[l]
            if r is None:
                t["khong_ap_dung"] += 1
                continue
            moi, c = r
            k2 = gop.chay(moi, ca["input"])
            dung_nhom = nhom_dung_cua[l]
            xoa = l.startswith("xoa_")

            def trung(pid, cb):
                if xoa:
                    return pid is None and bool(set(cb.luot) & set(c.luot))
                return pid == c.phat_bieu_id

            cbs = _moi_canh_bao(k2)
            tren = [cb for pid, cb in cbs if trung(pid, cb)]
            dung = any(cb.nhom in dung_nhom for cb in tren)
            t["so_lan"] += 1
            t["bat_dung_loai"] += dung
            t["bat_bat_ky"] += bool(tren)
            if xoa:
                t["luot_con_duoc_dan"] += any(set(p.bang_chung) & set(c.luot) for p in moi)
            else:
                t["d_can_xac_nhan"] += (k2["trang_thai_D"].get(c.phat_bieu_id, {}).get("trang_thai")
                                        == gop.CAN_XAC_NHAN)
            for pid, cb in cbs:
                ma_tong[cb.ma] += 1
                ma_dung[cb.ma] += trung(pid, cb) and cb.nhom in dung_nhom
            if not dung and len(lot[l]) < vi_du:
                lot[l].append({"ca": ca["id"], "phat_bieu_id": c.phat_bieu_id, "mo_ta": c.mo_ta,
                               "canh_bao_tren_dong": sorted({cb.ma for cb in tren})})
    theo_loai = {}
    for l, t in tl.items():
        n = t["so_lan"]
        theo_loai[l] = {"so_lan": n, "bat_dung_loai": t["bat_dung_loai"], "bat_bat_ky": t["bat_bat_ky"],
                        "khong_ap_dung": t["khong_ap_dung"], "luot_con_duoc_dan": t["luot_con_duoc_dan"],
                        "d_can_xac_nhan": t["d_can_xac_nhan"],
                        "do_nhay": _r(t["bat_dung_loai"] / n) if n else None,
                        "do_nhay_bat_ky": _r(t["bat_bat_ky"] / n) if n else None,
                        "wilson": wilson(t["bat_dung_loai"], n)}
    co = [v["do_nhay"] for v in theo_loai.values() if v["do_nhay"] is not None]
    return {
        "ghi_chu": "Tren loi cay nhan tao, ban sach = dap an. Khong phai do chinh xac thuc te.",
        "seed": seed, "so_ca": so_ca,
        "sach": {"so_ca": so_ca, "bao_nham_moi_ca": _r(sum(sach_ma.values()) / max(so_ca, 1)),
                 "theo_ma": dict(sorted(sach_ma.items(), key=lambda x: (-x[1], x[0]))),
                 "chan_thua_D": _r(chan / max(than, 1))},
        "theo_loai": theo_loai,
        "do_nhay_trung_binh": _r(sum(co) / len(co)) if co else None,
        "theo_ma_trong_cay": {m: {"so_lan_bao": n, "dung": ma_dung[m], "chinh_xac": _r(ma_dung[m] / n),
                                  "bao_nham_moi_ca_sach": _r(sach_ma[m] / max(so_ca, 1))}
                              for m, n in sorted(ma_tong.items(), key=lambda x: (-x[1], x[0]))},
        "vi_du_lot": dict(lot),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--tap", choices=("dieu_chinh", "giu_kin"), required=True)
    ap.add_argument("--toi-da-khoa-luat", action="store_true",
                    help="bat buoc voi --tap giu_kin: xac nhan luat da khoa (chi chay mot lan)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--gioi-han", type=int, default=None, help="chi chay N ca dau (thu nhanh)")
    ap.add_argument("--ra-json", required=True)
    ap.add_argument("--kho", action="store_true", help="dung loi KHO (tools.cay_loi_kho)")
    a = ap.parse_args(argv)
    if a.tap == "giu_kin" and not a.toi_da_khoa_luat:
        ap.error("tap giu kin chi chay mot lan sau khi khoa luat: them --toi-da-khoa-luat")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    from src import du_lieu
    du_lieu.chan_tap_khoa(a.tap)   # hai tap nay khong phai tap kiem tra cuoi; chot van goi (test_chan_tap_khoa)
    ds = cay_loi.tap_dieu_chinh() if a.tap == "dieu_chinh" else cay_loi.tap_giu_kin()
    ds = ds[:a.gioi_han] if a.gioi_han else ds
    ra = do(ds, seed=a.seed, kho=a.kho)
    ra["kho"] = a.kho
    ra["tap"] = a.tap
    Path(a.ra_json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.ra_json).write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"so ca {ra['so_ca']}  bao nham/ca sach {ra['sach']['bao_nham_moi_ca']}  chan thua D "
          f"{ra['sach']['chan_thua_D']}  do nhay TB {ra['do_nhay_trung_binh']}")
    for l, v in ra["theo_loai"].items():
        print(f"{l:22} n={v['so_lan']:4d} dung_loai={v['do_nhay']} bat_ky={v['do_nhay_bat_ky']} "
              f"D_cxn={v['d_can_xac_nhan']} {v['wilson']}")
    print("bao nham ban sach:", list(ra["sach"]["theo_ma"].items())[:12])


if __name__ == "__main__":
    main()
