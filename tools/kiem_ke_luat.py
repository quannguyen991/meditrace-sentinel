# -*- coding: utf-8 -*-
"""Kiem ke cac mo-dun luat trong src/: ai nhap, co phep thu khong, ghi nguon may cho,
co nam tren luong chinh (bao dong nhap tu src/dich_vu.py) khong.

Doc bang `ast`, khong regex. Chi liet ke ung vien ma chet; KHONG xoa gi.

    python -m tools.kiem_ke_luat            # ghi docs/kiem-ke-luat.md
"""
import ast
import re
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
# Dong ghi nguon: "Nguon:", "nguon=", "Theo <van ban>", "QD-BYT", "TT-BYT", "Duoc thu"
_NGUON = re.compile(r"(ngu[oồ]n\s*[:=]|\bnguon\b\s*[:=]|QĐ-BYT|QD-BYT|TT-BYT|D[uư][oợ]c th[uư]|\bBNF\b|\bWHO\b|\bdoi\s*:)",
                    re.IGNORECASE)


def _ten_mo_dun(src: Path, p: Path) -> str:
    phan = list(p.relative_to(src).with_suffix("").parts)
    if phan[-1] == "__init__":
        phan = phan[:-1]
    return ".".join(phan)


def _nhap(cay: ast.AST, ten: str, la_goi: bool, cac_ten: set) -> set:
    """Tap ten mo-dun (khong tien to 'src.') ma `ten` nhap, chi giu cac ten co trong src."""
    goi = ten if la_goi else ten.rpartition(".")[0]
    ra = set()

    def them(dich):
        if dich in cac_ten and dich != ten:
            ra.add(dich)

    for nut in ast.walk(cay):
        if isinstance(nut, ast.Import):
            for a in nut.names:
                if a.name.startswith("src."):
                    them(a.name[4:])
        elif isinstance(nut, ast.ImportFrom):
            if nut.level:
                co_so = goi.split(".") if goi else []
                co_so = co_so[: len(co_so) - (nut.level - 1)] if nut.level > 1 else co_so
                goc = ".".join(co_so + ([nut.module] if nut.module else []))
            elif nut.module and (nut.module == "src" or nut.module.startswith("src.")):
                goc = nut.module[4:] if nut.module != "src" else ""
            else:
                continue
            if goc:
                them(goc)
            for a in nut.names:
                them(f"{goc}.{a.name}" if goc else a.name)
    return ra


def kiem_ke(thu_muc_src: Path, thu_muc_tests: Path) -> list:
    src, tests = Path(thu_muc_src), Path(thu_muc_tests)
    tep = {_ten_mo_dun(src, p): p for p in sorted(src.rglob("*.py"))}
    cac_ten = set(tep)
    nhap = {}
    for ten, p in tep.items():
        cay = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        nhap[ten] = _nhap(cay, ten, p.name == "__init__.py", cac_ten)
    # tests nhap gi
    duoc_thu = set()
    for p in sorted(tests.rglob("*.py")) if tests.exists() else []:
        cay = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        duoc_thu |= _nhap(cay, "__tests__." + p.stem, False, cac_ten)
    # luong chinh: bao dong tu dich_vu
    chinh, hang = set(), ["dich_vu"] if "dich_vu" in tep else []
    while hang:
        m = hang.pop()
        if m in chinh:
            continue
        chinh.add(m)
        hang.extend(nhap[m] - chinh)
    ra = []
    for ten, p in tep.items():
        noi_dung = p.read_text(encoding="utf-8", errors="replace")
        ra.append({
            "mo_dun": ten,
            "duoc_nhap_boi": sorted(k for k, v in nhap.items() if ten in v),
            "co_phep_thu": ten in duoc_thu,
            "so_cho_ghi_nguon": sum(1 for d in noi_dung.splitlines() if _NGUON.search(d)),
            "nam_tren_luong_chinh": ten in chinh,
            "so_dong": noi_dung.count("\n"),
        })
    return ra


def bang_md(ds: list) -> str:
    chet = [d for d in ds if not d["duoc_nhap_boi"] and not d["nam_tren_luong_chinh"] and d["mo_dun"]]
    khong_thu = [d for d in ds if d["nam_tren_luong_chinh"] and not d["co_phep_thu"] and d["so_dong"] > 30]
    dong = ["# Kiểm kê mô-đun src/ (sinh bằng `python -m tools.kiem_ke_luat`)", "",
            f"Tổng {len(ds)} mô-đun; {sum(d['nam_tren_luong_chinh'] for d in ds)} nằm trên luồng chính "
            "(bao đóng nhập từ `src/dich_vu.py`).", "",
            "Danh sách dưới đây chỉ để người dùng quyết; **không xoá gì tự động**. Một mô-đun không ai nhập "
            "vẫn có thể là lệnh chạy độc lập (`python -m src.x`).", "",
            f"## Ứng viên mã chết: không ai nhập, không trên luồng chính ({len(chet)})", "",
            "| Mô-đun | Dòng | Có phép thử | Chỗ ghi nguồn |", "|---|---|---|---|"]
    dong += [f"| `{d['mo_dun']}` | {d['so_dong']} | {'có' if d['co_phep_thu'] else 'không'} | {d['so_cho_ghi_nguon']} |"
             for d in sorted(chet, key=lambda d: -d["so_dong"])]
    dong += ["", f"## Trên luồng chính nhưng không có phép thử nào nhập trực tiếp ({len(khong_thu)})", "",
             "| Mô-đun | Dòng | Chỗ ghi nguồn |", "|---|---|---|"]
    dong += [f"| `{d['mo_dun']}` | {d['so_dong']} | {d['so_cho_ghi_nguon']} |"
             for d in sorted(khong_thu, key=lambda d: -d["so_dong"])]
    dong += ["", "## Toàn bộ", "", "| Mô-đun | Dòng | Luồng chính | Phép thử | Nguồn | Được nhập bởi |",
             "|---|---|---|---|---|---|"]
    dong += [f"| `{d['mo_dun'] or '(src)'}` | {d['so_dong']} | {'✓' if d['nam_tren_luong_chinh'] else ''} | "
             f"{'✓' if d['co_phep_thu'] else ''} | {d['so_cho_ghi_nguon']} | {', '.join(d['duoc_nhap_boi'][:4])}"
             f"{' …' if len(d['duoc_nhap_boi']) > 4 else ''} |" for d in ds]
    return "\n".join(dong) + "\n"


def main():
    ds = kiem_ke(GOC / "src", GOC / "tests")
    dich = GOC / "docs" / "kiem-ke-luat.md"
    dich.write_text(bang_md(ds), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Ghi {dich}: {len(ds)} mo-dun")


if __name__ == "__main__":
    main()
