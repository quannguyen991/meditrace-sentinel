# -*- coding: utf-8 -*-
"""Soi hai cho la cua the he 8: loi thuoc khong giam qua cac nhanh, va so cap dung.

VI SAO CAN (19/09/2026). Bang the he 8 co hai cho chua giai thich duoc:
  - `sai_thuoc` gan nhu khong doi qua B, C, C_khoa (3,52 / 3,73 / 3,90 o bo doi chu
    the), trong khi nhom phep kiem K6 co luat CHAN khi lieu khong thay trong luot dan;
  - so cap dung ca hai ban o bo doi chu the chi 10/40.

Tep nay khong sinh so moi cho bao cao. No tra loi hai cau: loi thuoc SAI O TRUONG
NAO, va cap HONG VI LY DO GI.

    python tools/soi-sai-thuoc.py --thu-muc kaggle-ra/the-he-8 \
        --tap thach_thuc_doi_chu_the_phat_trien --nhanh B C C_khoa
"""
import argparse
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC))

from src import cham_he_thong, du_lieu, khoa_bang_chung  # noqa: E402
from src.cham_he_thong import CHI_TIET_THUOC_CHAM, _nd, dap_an, ghep_menh_de  # noqa: E402


def nap(thu_muc, tap, nhanh):
    d = Path(thu_muc)
    goc = {c["id"]: c for c in du_lieu.nap_mau(d / f"{tap}.jsonl")}
    kq = {n: {r["id"]: r for r in du_lieu.nap_mau(d / f"ra_{n}_{tap}.jsonl")}
          for n in nhanh}
    for n, k in kq.items():
        lech = [i for i, r in k.items() if r.get("input") != goc[i].get("input")]
        if lech:
            raise SystemExit(f"ra_{n}: {len(lech)} ca lech the he — dung lai")
    return goc, kq


def soi_thuoc(goc, kq):
    """-> {nhanh: Counter truong sai}, va vai vi du."""
    bang, vi_du = {}, defaultdict(list)
    for nhanh, k in kq.items():
        dem = Counter()
        for i, r in k.items():
            ca = goc[i]
            loi, _bs = cham_he_thong.loi_phat_bieu(ca, r["phat_bieu"])
            da = dap_an(ca)
            g = ghep_menh_de(da, r["phat_bieu"])
            nguoc = {j: da[x] for x, j in g.items()}
            for idx, (ds, _x) in loi.items():
                if not ds or ds[0] != "sai_thuoc":
                    continue
                p = r["phat_bieu"][idx]
                d = nguoc.get(idx)
                if d is None:
                    dem["khong ghep duoc"] += 1
                    continue
                va, du = d.get("thuoc") or {}, p.get("thuoc") or {}
                for truong in CHI_TIET_THUOC_CHAM:
                    a, b = _nd(va.get(truong)), _nd(du.get(truong))
                    if a == b:
                        continue
                    if a and not b:
                        dem[f"{truong}: bỏ trống"] += 1
                    elif b and not a:
                        dem[f"{truong}: thêm vào"] += 1
                    else:
                        dem[f"{truong}: khác giá trị"] += 1
                    if len(vi_du[nhanh]) < 6:
                        vi_du[nhanh].append(
                            {"ca": i, "truong": truong, "dap_an": va.get(truong),
                             "he_thong": du.get(truong),
                             "noi_dung": p.get("noi_dung"),
                             "luot_dan": p.get("bang_chung"),
                             "trich_dan": p.get("trich_dan")})
        bang[nhanh] = dem
    return bang, vi_du


def thieu_hay_sai(bang):
    """Tach loi thuoc lam ba nhom: bo trong, khac gia tri, them vao."""
    ra = {}
    for nhanh, dem in bang.items():
        ra[nhanh] = {
            "bỏ trống": sum(v for k, v in dem.items() if k.endswith("bỏ trống")),
            "khác giá trị": sum(v for k, v in dem.items() if k.endswith("khác giá trị")),
            "thêm vào": sum(v for k, v in dem.items() if k.endswith("thêm vào")),
        }
    return ra


def soi_cap(goc, kq, nhanh):
    """Cap hong vi ly do gi (bo doi chu the)."""
    cap = defaultdict(dict)
    for i, ca in goc.items():
        if ca.get("thach_thuc") != "doi_chu_the":
            return None
        cap[ca["cap"]][ca["bien_the"]] = ca
    ra = Counter()
    chi_tiet = []
    for ma, v in cap.items():
        if len(v) != 2:
            continue
        hong = {}
        for ban, ca in v.items():
            r = kq[nhanh].get(ca["id"])
            hong[ban] = ly_do_hong(ca, r)
        if hong["A"] is None and hong["B"] is None:
            ra["đúng cả cặp"] += 1
        else:
            for ban, ly in hong.items():
                if ly:
                    ra[f"bản {ban}: {ly}"] += 1
            chi_tiet.append({"cap": ma, **{f"ban_{b}": (hong[b] or "đúng") for b in hong}})
    return ra, chi_tiet


def ly_do_hong(ca, r):
    """None neu ban nay dung. Nguoc lai tra chuoi ly do."""
    from src.cham_he_thong import (_con_hieu_luc, _la_bn_gold, _muc, _than_khang_dinh_di_ung_bn,
                                   dung_nguoi, do_giong, NGUONG_GHEP)
    if r is None:
        return "khong co ket qua"
    gold = [d for d in dap_an(ca) if "dị ứng" in d["noi_dung"].lower()
            and _muc(d) == ("chắc chắn", False, "thực tế") and _con_hieu_luc(d)]
    if not gold:
        return "đáp án không có mệnh đề dị ứng khẳng định"
    g = ghep_menh_de(gold, r["phat_bieu"])
    for i, d in enumerate(gold):
        if i not in g:
            return "không ghép được mệnh đề dị ứng (bỏ sót hoặc viết khác)"
        if not dung_nguoi(d, r["phat_bieu"][g[i]]):
            p = r["phat_bieu"][g[i]]
            return (f"sai người: đáp án {d.get('chu_the')!r}, hệ thống "
                    f"{(p.get('ten_chu_the') or ('bệnh nhân' if p.get('chu_the_id') == 0 else '?'))!r}")
    if not any(_la_bn_gold(d) for d in gold):
        chat = {_nd(d["noi_dung"]) for d in gold}
        if any(do_giong(_nd(p["noi_dung"]), c) >= NGUONG_GHEP
               for p in _than_khang_dinh_di_ung_bn(r) for c in chat):
            return "thân bản nháp còn một câu gán dị ứng đó cho bệnh nhân"
    return None


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--thu-muc", required=True)
    ap.add_argument("--tap", required=True)
    ap.add_argument("--nhanh", nargs="+", default=["B", "C", "C_khoa"])
    ap.add_argument("--ra", default=None, help="tep json ghi ket qua")
    a = ap.parse_args()

    goc, kq = nap(a.thu_muc, a.tap, a.nhanh)
    print(f"{a.tap}: {len(goc)} ca, nhanh {', '.join(a.nhanh)}\n")

    bang, vi_du = soi_thuoc(goc, kq)
    print("=== LOI THUOC SAI O TRUONG NAO ===")
    truong = sorted({t for d in bang.values() for t in d})
    print(f"{'':38s}" + "".join(f"{n:>10s}" for n in a.nhanh))
    for t in truong:
        print(f"{t:38s}" + "".join(f"{bang[n][t]:10d}" for n in a.nhanh))
    print(f"{'TONG':38s}" + "".join(f"{sum(bang[n].values()):10d}" for n in a.nhanh))

    print("\n=== TACH NHOM ===")
    for nhanh, d in thieu_hay_sai(bang).items():
        print(f"  {nhanh:8s} bỏ trống {d['bỏ trống']:3d} · khác giá trị "
              f"{d['khác giá trị']:3d} · thêm vào {d['thêm vào']:3d}")
    print("  Cong kiem chung K6 chi kiem truong CO GHI (`if t.get(...)`). Truong bi bo"
          " trong khong co gi de kiem, nen khong ma ly do nao chay — do la ly do"
          " sai_thuoc khong giam tu B sang C_khoa.")

    print("\n=== VAI VI DU (nhanh C_khoa) ===")
    for v in vi_du.get("C_khoa", [])[:6]:
        print(f"  ca {v['ca']} · {v['truong']}: đáp án {v['dap_an']!r} → hệ thống "
              f"{v['he_thong']!r}\n      «{v['noi_dung']}» lượt {v['luot_dan']}")

    kq_cap = soi_cap(goc, kq, "C_khoa")
    if kq_cap:
        ra_cap, chi_tiet = kq_cap
        print("\n=== CAP HONG VI LY DO GI (C_khoa) ===")
        for k, v in ra_cap.most_common():
            print(f"  {v:3d}  {k}")

    if a.ra:
        Path(a.ra).write_text(json.dumps(
            {"tap": a.tap, "loi_thuoc": {n: dict(bang[n]) for n in a.nhanh},
             "vi_du": {k: v for k, v in vi_du.items()},
             "cap": dict(kq_cap[0]) if kq_cap else None,
             "cap_chi_tiet": kq_cap[1] if kq_cap else None},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print("\nGhi", a.ra)


if __name__ == "__main__":
    main()
