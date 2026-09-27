# -*- coding: utf-8 -*-
"""Dua dap an the he 8b (sua "nong ham hap", 24/09/2026) vao MOI ban sao bo du lieu
nam trong cac thu muc ket qua.

VI SAO CAN. Bo sinh da sua (`phuong_ngu.GIU_NGUYEN`): menh de ma can cu duy nhat la
"nong ham hap" thi dap an ghi dung cum do, khong ghi "sot, chac chan". Bo sinh lai
nam o `data/`. Nhung moi thu muc ket qua (`kaggle-ra/...`, `data-gpt/`...) mang BAN
SAO bo du lieu luc chay, de bo cham doi chieu dung the he (`--thu-muc`). Cham lai voi
dap an moi thi phai thay dap an trong ban sao do.

CHI THAY KHI BAN SAO DUNG LA THE HE 8: `input` giong het ban 8b VA (`dap_an`,
`output`) giong het ban 8 cu. Chi so `input` la chua du — lan chay thu dau tien bat
duoc `kaggle-ra/meditrace/data` va `klog/meditrace/data`: bo the he cu, 18–20 ca trung loi
thoai nhung dap an khac vi ly do khac; so `input` thoi thi da ghi de dap an 8b len
mot bo the he khac. Chi thay hai truong `dap_an` va `output`; bo sinh lai da chung
minh day la hai truong duy nhat khac nhau (42 menh de / 19 ca tap phat trien).

    python tools/va-dap-an-giu-loi.py --cu data/the-he-8 --nguon data         # chi xem
    python tools/va-dap-an-giu-loi.py --cu data/the-he-8 --nguon data --ghi   # ghi that

Van tay di kem (`*.van_tay.json`) duoc sua theo: `the_he` -> 8b, bam noi dung tinh
lai, them truong `sua_dap_an`. Cac truong khac (commit sinh, hat) giu nguyen.
"""
import argparse
import json
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC))
from src import van_tay_bo  # noqa: E402

BO = ["viet_phat_trien", "thach_thuc_doi_chu_the_phat_trien",
      "thach_thuc_phuong_ngu_phat_trien", "thach_thuc_dinh_chinh_phat_trien",
      "thach_thuc_nhieu_asr_phat_trien", "thach_thuc_dan_gian_phat_trien"]
THU_MUC = ["data-gpt", "data-may", "data-thu-may", "goi-kaggle", "kaggle-ra", "klog"]
GHI_CHU = ("2026-09-24: noi_dung 'sốt' -> 'nóng hầm hập' khi trich dan chi co cum do "
           "(phuong_ngu.GIU_NGUYEN); input khong doi. Xem docs/dang-ky-truoc.md, "
           "muc Thay doi sau dang ky.")


def _nap(p):
    van = p.read_text(encoding="utf-8")
    return [json.loads(x) for x in van.split("\n") if x.strip()], van.endswith("\n")


def la_bo_du_lieu(p):
    if p.name.startswith(("ra_", "trich_", "log_")) or p.name.endswith(".van_tay.json"):
        return False
    try:
        with open(p, encoding="utf-8") as f:
            dau = json.loads(f.readline())
    except (ValueError, UnicodeDecodeError):
        return False
    return isinstance(dau, dict) and {"id", "input", "dap_an"} <= set(dau)


def va_tep(p, cu, moi, ghi):
    ds, xuong_dong = _nap(p)
    dem = {"doi": 0, "giu": 0, "khac_the_he": 0, "khac_dap_an": 0, "khong_co": 0}
    for ca in ds:
        m, c = moi.get(ca["id"]), cu.get(ca["id"])
        hien = (ca["dap_an"], ca["output"])
        if m is None or c is None:
            dem["khong_co"] += 1
        elif m["input"] != ca["input"] or c["input"] != ca["input"]:
            dem["khac_the_he"] += 1
        elif hien == (m["dap_an"], m["output"]):
            dem["giu"] += 1
        elif hien == (c["dap_an"], c["output"]):
            ca["dap_an"], ca["output"] = m["dap_an"], m["output"]
            dem["doi"] += 1
        else:
            dem["khac_dap_an"] += 1
    if ghi and dem["doi"]:
        p.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in ds)
                     + ("\n" if xuong_dong else ""), encoding="utf-8")
        vt_p = van_tay_bo.duong_dan_van_tay(p)
        if vt_p.exists():
            vt = json.loads(vt_p.read_text(encoding="utf-8"))
            vt.update(the_he="8b", bam_noi_dung=van_tay_bo.bam_noi_dung(ds),
                      sua_dap_an=GHI_CHU)
            vt_p.write_text(json.dumps(vt, ensure_ascii=False, indent=2),
                            encoding="utf-8")
    return dem


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--cu", required=True, help="thu muc chua bo the he 8 (truoc khi sua)")
    ap.add_argument("--nguon", required=True, help="thu muc chua bo the he 8b")
    ap.add_argument("--ghi", action="store_true")
    a = ap.parse_args()

    def nap_bo(thu_muc):
        ra = {}
        for ten in BO:
            for ca in _nap(Path(thu_muc) / f"{ten}.jsonl")[0]:
                assert ca["id"] not in ra, ca["id"]
                ra[ca["id"]] = ca
        return ra
    cu, moi = nap_bo(a.cu), nap_bo(a.nguon)
    assert cu.keys() == moi.keys()
    tong = 0
    for tm in THU_MUC:
        for p in sorted((GOC / tm).rglob("*.jsonl")):
            if not la_bo_du_lieu(p):
                continue
            dem = va_tep(p, cu, moi, a.ghi)
            if dem["doi"] or dem["giu"] or dem["khac_dap_an"]:
                tong += dem["doi"]
                print(f"{str(p.relative_to(GOC)):72} doi {dem['doi']:3d}  giu {dem['giu']:4d}"
                      f"  khac dap an {dem['khac_dap_an']:3d}  khac the he {dem['khac_the_he']:4d}"
                      f"  khong co {dem['khong_co']:4d}")
    print(f"\nTong so ca doi dap an: {tong}" + ("" if a.ghi else "  (CHUA GHI — them --ghi)"))


if __name__ == "__main__":
    main()
