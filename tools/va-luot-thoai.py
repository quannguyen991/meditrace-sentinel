# -*- coding: utf-8 -*-
"""KHONG DUNG — tao ra theo mot chan doan SAI (20/09/2026), giu lai chi de co dau vet.

Chan doan sai: tuong truong `luot_thoai` bi bo trong. Thuc te `khong_can_cu` nghia la
"khong ghep duoc voi menh de dap an nao", va truong bang chung trong ban ghi da ghep
ten la `bang_chung`. Cong cu nay tim thay 0 cho can va. Doc
docs/ket-qua/doi-chung-thuong-mai-gpt.md de biet nguyen nhan that.

Mo ta ban dau (SAI):
Va truong `luot_thoai` bi bo trong cho dau ra cua mo hinh thuong mai (20/09/2026).

VI SAO CAN. Lan chay doi chung gpt-6-astra co 45–49% menh de bi bo cham danh dau
`khong_can_cu`. Kiem lai thi 100% so do THIEU truong `luot_thoai`, va 100% trong
so do co `trich_dan` xuat hien NGUYEN VAN trong hoi thoai. Nghia la noi dung CO
can cu, chi thieu so hieu luot. Bao cao 45–49% "khong can cu" la sai su that.

VI SAO HAI BEN KHAC NHAU. Mo hinh chay tai cho bi `lm-format-enforcer` ep theo
luoc do nen khong bao gio bo sot truong. Mo hinh thuong mai goi qua API voi
`strict: false`, nen luoc do khong duoc cuong che. Day la mot khac biet THAT ve
tuan thu dinh dang, va phai bao cao rieng — nhung no khong duoc tron lan vao chi
so do do chinh xac noi dung.

CACH VA. Voi moi menh de thieu `luot_thoai`: tim cac luot co chua nguyen van
trich dan (sau khi chuan hoa dau cau va khoang trang). Chi dien khi tim duoc;
khong doan.

    python tools/va-luot-thoai.py data-gpt
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import du_lieu  # noqa: E402


def chuan(s: str) -> str:
    s = unicodedata.normalize("NFC", (s or "").lower())
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", s)).strip()


def tach_luot(vao: str):
    """-> danh sach (so_luot, van_ban_da_chuan_hoa), so luot bat dau tu 1."""
    ra = []
    for n, dong in enumerate([x for x in vao.split("\n") if x.strip()], 1):
        # Bo nhan vai o dau dong ("Bac si:", "Nguoi nha:") — trich dan khong co no.
        ra.append((n, chuan(re.sub(r"^[^:]{1,20}:\s*", "", dong))))
    return ra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("thu_muc")
    ap.add_argument("--max-token", default="3072")
    a = ap.parse_args()
    d = Path(a.thu_muc)

    for dem in sorted(d.glob(f"trich_*_{a.max_token}.jsonl")):
        tap = dem.name[len("trich_"):-len(f"_{a.max_token}.jsonl")]
        bo = d / f"{tap}.jsonl"
        if not bo.is_file():
            print(f"{dem.name}: khong thay {bo.name}, bo qua")
            continue
        goc = {c["id"]: c for c in du_lieu.nap_mau(bo)}

        ra, thieu, va_duoc = [], 0, 0
        for dong in dem.read_text(encoding="utf-8").splitlines():
            if not dong.strip():
                continue
            r = json.loads(dong)
            luot = tach_luot(goc[r["id"]]["input"]) if r["id"] in goc else []
            for p in (r.get("phat_bieu") or []):
                if p.get("luot_thoai"):
                    continue
                thieu += 1
                tim = []
                for x in (p.get("trich_dan") or []):
                    cx = chuan(x)
                    if len(cx) < 4:
                        continue
                    for n, vb in luot:
                        if cx in vb and n not in tim:
                            tim.append(n)
                if tim:
                    p["luot_thoai"] = sorted(tim)
                    va_duoc += 1
            ra.append(json.dumps(r, ensure_ascii=False))

        (d / f"{dem.stem}.truoc-va.jsonl").write_text(
            dem.read_text(encoding="utf-8"), encoding="utf-8")
        dem.write_text("\n".join(ra) + "\n", encoding="utf-8")
        print(f"{tap:36} thieu luot {thieu:4d} | va duoc {va_duoc:4d} "
              f"| khong tim thay {thieu - va_duoc:3d}")


if __name__ == "__main__":
    main()
