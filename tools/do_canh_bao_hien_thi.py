# -*- coding: utf-8 -*-
"""Đo MT5 (ngân sách cảnh báo) trên 400 ca cấy lỗi tập điều chỉnh, chỉ CPU.

Ba cách đếm "cảnh báo hiển thị", cùng một lần chạy `gop.chay`:
  tat_ca     mọi cảnh báo (cách đếm của docs/ket-qua/cay-loi.md: 7,11/ca sạch)
  ui_cu      giao diện cũ: cảnh báo chính + tối đa 2 cảnh báo khác nhóm mỗi dòng,
             cộng cảnh báo toàn ca có kết luận khác `can_xem`
  ngan_sach  `gop.hien_thi_ca(kq)` — chỉ phần `hien` (có khi chạy trên mã đã có Task 5)

Độ nhạy hiển thị = lần cấy có cảnh báo ĐÚNG NHÓM, đúng dòng (lỗi xoá: cảnh báo toàn ca chạm lượt
bị xoá) NẰM TRONG phần hiển thị. Cùng định nghĩa với `src/do_luong/do_cay_loi.py`.

    PYTHONUTF8=1 python -m tools.do_canh_bao_hien_thi --ra-json docs/ket-qua/canh-bao-ngan-sach-cay-loi.json

Không đụng tập kín `viet_kiem_tra_cuoi*`, không đụng tập giữ kín.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.canh_bao import gop  # noqa: E402
from src.do_luong.do_cay_loi import _moi_canh_bao, _ps, _rng, wilson  # noqa: E402
from src.do_luong.danh_gia_khoa import vao_than  # noqa: E402
from tools import cay_loi  # noqa: E402


def _ui_cu(kq):
    ra = []
    for i, v in kq["theo_phat_bieu"].items():
        if v["chinh"] is not None:
            ra.append((int(i), v["chinh"]))
        ra += [(int(i), c) for c in v["khac"]]
    return ra + [(None, c) for c in kq["toan_ca"] if c.ket_luan != "can_xem"]


def _ngan_sach(kq):
    hs = gop.hien_thi_ca(kq)
    ra = [(int(i), c) for i, (hien, _gap) in hs["theo_phat_bieu"].items() for c in hien]
    return ra + [(None, c) for c in hs["toan_ca"][0]]


def do(ds, seed=42):
    cach = {"tat_ca": _moi_canh_bao, "ui_cu": _ui_cu}
    if hasattr(gop, "hien_thi_ca"):
        cach["ngan_sach"] = _ngan_sach
    sach = {k: Counter() for k in cach}
    sach_ma = {k: Counter() for k in cach}
    tl = {l: Counter() for l in cay_loi.LOAI_CAY}
    than = chan = so_ca = 0
    for ca in ds:
        ps = _ps(ca)
        kq = gop.chay(ps, ca["input"])
        so_ca += 1
        for k, f in cach.items():
            cbs = f(kq)
            sach[k]["tong"] += len(cbs)
            sach_ma[k].update(c.ma for _, c in cbs)
        for p in ps:
            if vao_than(p):
                than += 1
                chan += kq["trang_thai_D"].get(p.id, {}).get("trang_thai") == gop.CAN_XAC_NHAN
        for l in cay_loi.LOAI_CAY:
            r = cay_loi.cay(ps, ca, l, _rng(seed, ca["id"], l))
            if r is None:
                continue
            moi, c = r
            k2 = gop.chay(moi, ca["input"])
            nhom = cay_loi.NHOM_DUNG[l]
            xoa = l.startswith("xoa_")

            def trung(pid, cb):
                if xoa:
                    return pid is None and bool(set(cb.luot) & set(c.luot))
                return pid == c.phat_bieu_id

            t = tl[l]
            t["n"] += 1
            for k, f in cach.items():
                t[k] += any(trung(pid, cb) and cb.nhom in nhom for pid, cb in f(k2))
            if not xoa:
                t["d_cxn"] += k2["trang_thai_D"].get(c.phat_bieu_id, {}).get("trang_thai") == gop.CAN_XAC_NHAN
    theo_loai = {}
    for l, t in tl.items():
        n = t["n"]
        theo_loai[l] = {"n": n, "d_can_xac_nhan": t["d_cxn"],
                        **{f"do_nhay_{k}": round(t[k] / n, 3) if n else None for k in cach},
                        **{f"wilson_{k}": wilson(t[k], n) for k in cach}}
    tb = {k: round(sum(v[f"do_nhay_{k}"] for v in theo_loai.values() if v["n"]) /
                   sum(1 for v in theo_loai.values() if v["n"]), 3) for k in cach}
    return {
        "ghi_chu": "Tren loi cay nhan tao, ban sach = dap an. Khong phai do chinh xac thuc te.",
        "seed": seed, "so_ca": so_ca,
        "canh_bao_moi_ca_sach": {k: round(sach[k]["tong"] / max(so_ca, 1), 3) for k in cach},
        "theo_ma_ca_sach": {k: dict(sach_ma[k].most_common()) for k in cach},
        "chan_thua_D_ban_sach": round(chan / max(than, 1), 3),
        "do_nhay_trung_binh": tb,
        "theo_loai": theo_loai,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--ra-json", required=True)
    ap.add_argument("--gioi-han", type=int, default=None)
    a = ap.parse_args(argv)
    from src.bo_du_lieu import nap_du_lieu as du_lieu
    du_lieu.chan_tap_khoa("dieu_chinh")
    ds = cay_loi.tap_dieu_chinh()
    ds = ds[:a.gioi_han] if a.gioi_han else ds
    ra = do(ds)
    Path(a.ra_json).write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: ra[k] for k in ("so_ca", "canh_bao_moi_ca_sach", "chan_thua_D_ban_sach",
                                         "do_nhay_trung_binh")}, ensure_ascii=False))
    for l, v in ra["theo_loai"].items():
        print(l, {k: v[k] for k in v if not k.startswith("wilson")})


if __name__ == "__main__":
    main()
