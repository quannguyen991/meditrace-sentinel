# -*- coding: utf-8 -*-
"""Do CHAT LUONG phat hien quan he, doi chieu voi dap an cau truc.

VI SAO CO TEP NAY (10/09/2026).

Con so `quan_he` = "khong" o 282/282 tren bo tham chieu ngoai da bi giai thich
SAI HAI LAN, va lan nao cung nghe hop ly:

  lan 1  "khau trich khong nhan ra quan he tren hoi thoai dai"
         -> bac bo boi: buoc phan tung cap chi sinh 2 cap ung vien

  lan 2  "bo nhan huan luyen khong co vi du duong nen mo hinh hoc sai"
         -> bac bo boi: chinh MO HINH NEN, khong adapter, khong hoc gi ca,
            van danh dau 20 quan he tren bo tu sinh

Cai chung cua hai lan: dem MOT con so roi rut mot nguyen nhan. Tep nay dem BON
con so — dung, thua, sot, va nham loai — de lan sau khong lam the nua.

    python -m src.do_quan_he --tap viet_phat_trien
"""
import argparse
import io
import json
import sys
from collections import Counter

from src import duong_dan


def _khoa(m):
    """Khoa ghep mot menh de: chu the + noi dung da chuan hoa tho."""
    return (str(m.get("chu_the", "")).strip().lower(),
            " ".join(str(m.get("noi_dung", "")).lower().split()))


def _cap_dung(ca):
    """Tap cap quan he DUNG cua mot ca -> {(khoa_nguon, khoa_dich): loai}."""
    dap_an = ca["dap_an"]
    ra = {}
    for m in dap_an:
        if not m.get("quan_he"):
            continue
        j = m.get("quan_he_voi")
        if j is None or not (0 <= j < len(dap_an)):
            continue
        ra[(_khoa(m), _khoa(dap_an[j]))] = m["quan_he"]
    return ra


def _cap_du_doan(k):
    """Tap cap quan he DU DOAN tu dau ra trich -> {(khoa_nguon, khoa_dich): loai}."""
    ps = k.get("phat_bieu") or []
    ra = {}
    for i, p in enumerate(ps):
        qh = p.get("quan_he")
        if not qh or qh == "không":
            continue
        j = p.get("quan_he_voi")
        if j is None or not isinstance(j, int) or not (0 <= j < len(ps)) or j == i:
            continue
        ra[(_khoa(p), _khoa(ps[j]))] = qh
    return ra


def do(mau_theo_id, tho):
    """-> thong ke. Dem BON nhom, khong gop lai thanh mot ty le."""
    dung = thua = sot = nham_loai = 0
    theo_loai_dung = Counter()
    theo_loai_du_doan = Counter()
    theo_loai_that = Counter()
    ca_co_quan_he_that = ca_co_du_doan = 0

    for k in tho:
        ca = mau_theo_id.get(k["id"])
        if ca is None:
            continue
        that = _cap_dung(ca)
        du = _cap_du_doan(k)
        ca_co_quan_he_that += bool(that)
        ca_co_du_doan += bool(du)
        for loai in that.values():
            theo_loai_that[loai] += 1
        for loai in du.values():
            theo_loai_du_doan[loai] += 1

        for cap, loai_that in that.items():
            if cap not in du:
                sot += 1
            elif du[cap] == loai_that:
                dung += 1
                theo_loai_dung[loai_that] += 1
            else:
                nham_loai += 1
        for cap in du:
            if cap not in that:
                thua += 1

    tong_that = dung + sot + nham_loai
    tong_du = dung + thua + nham_loai
    return {
        "so_ca": len(tho),
        "ca_co_quan_he_that": ca_co_quan_he_that,
        "ca_co_du_doan": ca_co_du_doan,
        "dung": dung, "thua": thua, "sot": sot, "nham_loai": nham_loai,
        "do_phu": dung / tong_that if tong_that else None,
        "do_chuan": dung / tong_du if tong_du else None,
        "theo_loai_that": dict(theo_loai_that),
        "theo_loai_du_doan": dict(theo_loai_du_doan),
        "theo_loai_dung": dict(theo_loai_dung),
    }


def do_tinh_huong(mau_theo_id, tho, gia_tri="giả định"):
    """Cung cach dem, cho truong `tinh_huong`. Mot truong don, khong phai cap."""
    dung = thua = sot = 0
    for k in tho:
        ca = mau_theo_id.get(k["id"])
        if ca is None:
            continue
        that = {_khoa(m) for m in ca["dap_an"] if m.get("tinh_huong") == gia_tri}
        du = {_khoa(p) for p in (k.get("phat_bieu") or [])
              if p.get("tinh_huong") == gia_tri}
        dung += len(that & du)
        sot += len(that - du)
        thua += len(du - that)
    return {"gia_tri": gia_tri, "dung": dung, "thua": thua, "sot": sot,
            "do_phu": dung / (dung + sot) if (dung + sot) else None,
            "do_chuan": dung / (dung + thua) if (dung + thua) else None}


def _in(tk, ten):
    print(f"\n=== {ten} ===")
    print(f"  ca co quan he that : {tk['ca_co_quan_he_that']}/{tk['so_ca']}")
    print(f"  ca co du doan      : {tk['ca_co_du_doan']}/{tk['so_ca']}")
    print(f"  dung      {tk['dung']:4d}")
    print(f"  thieu     {tk['sot']:4d}   (co that ma khong bat duoc)")
    print(f"  thua      {tk['thua']:4d}   (bat ra ma khong co that)")
    print(f"  nham loai {tk['nham_loai']:4d}   (dung cap, sai loai quan he)")
    dp, dc = tk["do_phu"], tk["do_chuan"]
    print(f"  do phu    {dp:.3f}" if dp is not None else "  do phu    —")
    print(f"  do chuan  {dc:.3f}" if dc is not None else "  do chuan  —")
    print(f"  that     : {tk['theo_loai_that']}")
    print(f"  du doan  : {tk['theo_loai_du_doan']}")
    print(f"  dung theo loai: {tk['theo_loai_dung']}")


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--max-token", type=int, default=3072)
    ap.add_argument("--adapter-trich", action="store_true",
                    help="doc tep dem cua ban da huan luyen (hau to _hl)")
    a = ap.parse_args()

    from src import du_lieu as _dl
    _dl.chan_tap_ngoai(a.tap)
    _dl.chan_tap_khoa(a.tap)

    d = duong_dan.THU_MUC_DU_LIEU
    mau = {json.loads(x)["id"]: json.loads(x)
           for x in open(d / f"{a.tap}.jsonl", encoding="utf-8") if x.strip()}
    hau = "_hl" if a.adapter_trich else ""
    dem = d / f"trich_{a.tap}_{a.max_token}{hau}.jsonl"
    if not dem.exists():
        raise SystemExit(f"chua co {dem}")
    tho = [json.loads(x) for x in open(dem, encoding="utf-8") if x.strip()]

    # Tep dem co dung la cua bo du lieu nay khong. Xem bakeoff.kiem_khop —
    # khong co phep kiem nay thi mot lan sinh lai du lieu la du de moi con so
    # sau do vo nghia ma khong co gi bao.
    from src import bakeoff as _bk
    _bk.kiem_khop(mau, tho, dem.name)

    tk = do(mau, tho)
    _in(tk, f"QUAN HE — {a.tap}{hau}")
    tk_gd = do_tinh_huong(mau, tho)
    print(f"\n=== TINH HUONG 'gia dinh' — {a.tap}{hau} ===")
    print(f"  dung {tk_gd['dung']}   thieu {tk_gd['sot']}   thua {tk_gd['thua']}")
    dp, dc = tk_gd["do_phu"], tk_gd["do_chuan"]
    print(f"  do phu {dp:.3f}" if dp is not None else "  do phu —",
          f"  do chuan {dc:.3f}" if dc is not None else "  do chuan —")

    ra = {"tap": a.tap, "adapter_trich": a.adapter_trich,
          "quan_he": tk, "tinh_huong_gia_dinh": tk_gd}
    dp2 = duong_dan.THU_MUC_KET_QUA / f"quan-he-{a.tap}{hau}.json"
    dp2.write_text(json.dumps(ra, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nda ghi {dp2}")


if __name__ == "__main__":
    main()
