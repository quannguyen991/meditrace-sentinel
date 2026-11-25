# -*- coding: utf-8 -*-
"""Cau lap trong bo hoi thoai den tu dau? (Task B2 cua ke hoach nang cap)

Dem moi cau lap cua bo, roi phan loai theo NGUON trong ma:
  - "nhom:<TEN>"   cau bang dung mot phan tu cua nhom <TEN> trong `ngu_lieu_viet`
                   (ke ca nhom long nhau, vi du `MIEN.bac.chao_cuoi`)
  - "mau-f-string:dongN"  cau khop mot f-string o dong N cua `sinh_hoi_thoai_viet.py`
  - "cau-co-dinh"  cau bang dung mot chuoi van ban co dinh viet thang trong
                   `sinh_hoi_thoai_viet.py` (khong thuoc nhom nao)
  - "ghep"         con lai: cau duoc ghep tu nhieu manh (f-string) hoac dung dong tu
                   trung tinh; muon sua phai sua cho ghep, khong them cau vao nhom

Chay: python -m src.nguon_lap_cau data/hoi_thoai_viet_5000.jsonl [--ra docs/do-lap-cau-nguon.md]
"""
from __future__ import annotations

import ast
import collections
import re
import sys
from pathlib import Path

from src import do_lap_cau as dl
from src import ngu_lieu_viet as nl

_GOC = Path(__file__).resolve().parent


def _lam_phang(v, duong: str, ra: dict[str, set[str]]) -> None:
    """Duyet de quy hang cua `nl` (list/tuple/dict long nhau), gom chuoi theo DUONG DAN
    (vi du `MIEN.bac.chao_cuoi`, `XA_GIAO`)."""
    if isinstance(v, str):
        ra.setdefault(duong, set()).add(dl._chuan_hoa(v))
    elif isinstance(v, dict):
        for k, x in v.items():
            _lam_phang(x, f"{duong}.{k}", ra)
    elif isinstance(v, (list, tuple)):
        for x in v:
            _lam_phang(x, duong, ra)


def _cac_nhom_cau() -> dict[str, set[str]]:
    """{DUONG_DAN_NHOM: tap cau da chuan hoa} cho moi hang HOA cua `nl` (ke ca long nhau)."""
    ra: dict[str, set[str]] = {}
    for ten in dir(nl):
        if ten.isupper():
            _lam_phang(getattr(nl, ten), ten, ra)
    # Chuoi qua ngan hoac chi la mot tu (ten benh, thuoc...) khong phai cau hoi thoai.
    return {k: {c for c in v if len(c) >= 6} for k, v in ra.items()}


def _mau_f_string() -> list[tuple[str, "re.Pattern[str]"]]:
    """[(ten, regex)] cho moi f-string trong sinh_hoi_thoai_viet.py: phan van ban giu
    nguyen, phan {..} thanh `.+?`. Cau lap nhu "<goi> di kham cho minh phai khong a?"
    khong nam trong nhom nao ma den tu mot f-string."""
    nguon = (_GOC / "sinh_hoi_thoai_viet.py").read_text(encoding="utf-8")
    ra = []
    for n in ast.walk(ast.parse(nguon)):
        if isinstance(n, ast.JoinedStr):
            manh = []
            for x in n.values:
                if isinstance(x, ast.Constant):
                    manh.append(re.escape(dl._chuan_hoa(str(x.value))))
                else:
                    manh.append(".+?")
            mau = "".join(manh)
            if len(re.sub(r"\.|\.\+\?", "", mau)) >= 6:
                ra.append((f"mau-f-string:dong{n.lineno}", re.compile(mau)))
    return ra


def _cau_co_dinh() -> set[str]:
    """Moi hang chuoi >= 6 ky tu viet thang trong sinh_hoi_thoai_viet.py (khong phai f-string)."""
    cay = ast.parse((_GOC / "sinh_hoi_thoai_viet.py").read_text(encoding="utf-8"))
    ra = set()
    for n in ast.walk(cay):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) >= 6:
            ra.add(dl._chuan_hoa(n.value))
    return ra


def phan_loai_nguon(cau: str, nhom: dict[str, set[str]] | None = None,
                    co_dinh: set[str] | None = None,
                    mau: list | None = None) -> str:
    """-> "nhom:<DUONG_DAN>" | "cau-co-dinh" | "mau-f-string:dong<N>" | "ghep".

    `cau` da qua `do_lap_cau.tach_cau`. Thu tu: nhom cua `ngu_lieu_viet`, chuoi co dinh
    trong `sinh_hoi_thoai_viet.py`, f-string, roi "ghep" (con lai).
    """
    nhom = _cac_nhom_cau() if nhom is None else nhom
    co_dinh = _cau_co_dinh() if co_dinh is None else co_dinh
    mau = _mau_f_string() if mau is None else mau
    c = dl._chuan_hoa(cau)
    for ten, tap in nhom.items():
        if c in tap:
            return f"nhom:{ten}"
    if c in co_dinh:
        return "cau-co-dinh"
    for ten, rx in mau:
        if rx.fullmatch(c):
            return ten
    return "ghep"


def bang_nguon_lap(cac_ca: list[dict]) -> dict:
    """-> {"tong_cau_lap": int, "theo_nguon": {nguon: so_cau_lap}, "top": [(cau, n, nguon)]}.

    "So cau lap" = so lan xuat hien TRU lan dau cua moi cau (tong = so_cau - so_cau_duy_nhat).
    """
    dem = collections.Counter()
    for ca in cac_ca:
        if isinstance(ca, dict) and "input" in ca:
            dem.update(dl.tach_cau(ca["input"]))
    nhom, co_dinh, mau = _cac_nhom_cau(), _cau_co_dinh(), _mau_f_string()
    theo = collections.Counter()
    for cau, n in dem.items():
        if n > 1:
            theo[phan_loai_nguon(cau, nhom, co_dinh, mau)] += n - 1
    top = [(c, n, phan_loai_nguon(c, nhom, co_dinh, mau))
           for c, n in dem.most_common(40) if n > 1]
    return {"tong_cau_lap": sum(theo.values()), "theo_nguon": dict(theo.most_common()),
            "top": top}


def _in_bang(r: dict, tep: str) -> str:
    tong = r["tong_cau_lap"] or 1
    d = [f"# Nguon cua cau lap — {tep}", "",
         f"Tong so lan lap (tru lan dau cua tung cau): {r['tong_cau_lap']:,}", "",
         "| Nguon | So lan lap | Ty trong |", "|---|---:|---:|"]
    for nguon, n in r["theo_nguon"].items():
        d.append(f"| {nguon} | {n:,} | {100 * n / tong:.1f}% |")
    d += ["", "## 40 cau lap nhieu nhat", "", "| So lan | Nguon | Cau |", "|---:|---|---|"]
    for c, n, nguon in r["top"]:
        d.append(f"| {n:,} | {nguon} | {c[:100]} |")
    return "\n".join(d) + "\n"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        raise SystemExit("dung: python -m src.nguon_lap_cau <tep.jsonl> [--ra tep.md]")
    tep = sys.argv[1]
    ca, _ = dl.doc_jsonl(tep)
    van_ban = _in_bang(bang_nguon_lap(ca), tep)
    if "--ra" in sys.argv:
        Path(sys.argv[sys.argv.index("--ra") + 1]).write_text(van_ban, encoding="utf-8")
    print(van_ban)


if __name__ == "__main__":
    main()
