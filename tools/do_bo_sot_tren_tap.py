# -*- coding: utf-8 -*-
"""Do ti le bo sot tu tep dem khau trich (Task A6 cua ke hoach nang cap).

Doc `data/trich_<tap>_<max_token>[_hl].jsonl` do `src.duong_ong.chay_duong_ong` ghi (moi dong: id, ly_do,
phat_bieu, tho), ghep voi dap an cua `data/<tap>.jsonl`, roi tinh ti le bo sot bang
`src.do_luong.do_bo_sot.ti_le_bo_sot`. Chi tinh tren cac ca CO TRONG TAT CA cac tep dem duoc
dua vao, de so cac mo hinh tren cung mot tap ca.

  python tools/do_bo_sot_tren_tap.py --ra docs/ket-qua/bo-sot-qwen3-4b.md \\
      "Qwen3-4B chua huan luyen=data/trich_viet_phat_trien_3072.jsonl" \\
      "Qwen3-4B + adapter=data/trich_viet_phat_trien_3072_hl.jsonl"
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.he_thong import duong_dan as duong_dan  # noqa: E402
from src.do_luong.do_bo_sot import ti_le_bo_sot  # noqa: E402


def doc_jsonl_theo_id(duong_dan_tep) -> dict:
    ra = {}
    for dong in Path(duong_dan_tep).read_text(encoding="utf-8").splitlines():
        if dong.strip():
            x = json.loads(dong)
            ra[x["id"]] = x
    return ra


def khoang_tin_cay_95(so_bo_sot: int, tong: int) -> tuple[float, float]:
    """Khoang Wilson 95% cho ti le. Cac menh de cua cung mot ca khong doc lap, nen day la
    khoang HEP HON thuc te; chi dung de cho thay cho lech lon khi it ca."""
    if tong == 0:
        return 0.0, 0.0
    z, p = 1.96, so_bo_sot / tong
    mau = 1 + z * z / tong
    tam = (p + z * z / (2 * tong)) / mau
    nua = z * math.sqrt(p * (1 - p) / tong + z * z / (4 * tong * tong)) / mau
    return max(0.0, tam - nua), min(1.0, tam + nua)


def do(tep_dap_an, cac_tep_dem: dict) -> dict:
    """-> {"so_ca", "ket_qua": {ten: {ti_le_bo_sot, ..., "khoang", "so_ca_json_loi"}}}."""
    dap_an = doc_jsonl_theo_id(tep_dap_an)
    dem = {ten: doc_jsonl_theo_id(tep) for ten, tep in cac_tep_dem.items()}
    chung = set(dap_an)
    for d in dem.values():
        chung &= set(d)
    chung = sorted(chung)
    ra = {}
    for ten, d in dem.items():
        cap = [(dap_an[i].get("dap_an") or [], d[i].get("phat_bieu") or []) for i in chung]
        r = ti_le_bo_sot(cap)
        r["khoang"] = khoang_tin_cay_95(r["so_bo_sot"], r["so_menh_de_dap_an"])
        r["so_ca_json_loi"] = sum(1 for i in chung if (d[i].get("ly_do") or "").strip())
        ra[ten] = r
    return {"so_ca": len(chung), "ket_qua": ra}


def in_bang(kq: dict) -> str:
    d = [f"# Ty le bo sot — {kq['so_ca']} ca cua tap phat trien", "",
         "Chi so: ti le menh de cua dap an KHONG ghep duoc voi ban trich nao (do giong tu >= 0,6).",
         "Khoang tin cay Wilson 95% coi moi menh de la doc lap, nen hep hon thuc te.", "",
         "| Mo hinh | So menh de dap an | Bo sot | Ti le | Khoang 95% | Ca JSON loi |",
         "|---|---:|---:|---:|---|---:|"]
    for ten, r in kq["ket_qua"].items():
        lo, hi = r["khoang"]
        d.append(f"| {ten} | {r['so_menh_de_dap_an']} | {r['so_bo_sot']} | "
                 f"{100 * r['ti_le_bo_sot']:.1f}% | {100 * lo:.1f}%–{100 * hi:.1f}% | {r['so_ca_json_loi']} |")
    return "\n".join(d) + "\n"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--ra", default=None)
    ap.add_argument("cap", nargs="+", help="ten=duong_dan_tep_dem")
    a = ap.parse_args()
    cac = {}
    for c in a.cap:
        ten, _, tep = c.partition("=")
        if not tep:
            raise SystemExit(f"can dang ten=duong_dan: {c}")
        cac[ten] = tep
    kq = do(duong_dan.THU_MUC_DU_LIEU / f"{a.tap}.jsonl", cac)
    van_ban = in_bang(kq)
    if a.ra:
        Path(a.ra).write_text(van_ban, encoding="utf-8")
    print(van_ban)


if __name__ == "__main__":
    main()
