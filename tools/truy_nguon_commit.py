"""Truy nguồn lịch sử commit theo công cụ AI.

Chạy: python -m tools.truy_nguon_commit > docs/minh-bach/truy-nguon-commit.md
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
TEP_GHI_DE = GOC / "docs" / "minh-bach" / "truy-nguon-ghi-de.json"

_TRAILER = re.compile(r"^Cong-cu-AI:\s*(\S+)\s*$", re.MULTILINE)
_CLAUDE = re.compile(r"^Co-Authored-By:\s*Claude\b", re.MULTILINE | re.IGNORECASE)
_DOI_TEN_NGOAC = re.compile(r"\{[^{}]*? => ([^{}]*)\}")

DINH_DANG = "%x1e%H%x1f%ad%x1f%s%x1f%B%x1e"


def phan_loai_commit(thong_diep: str, ghi_de: dict[str, str], ma: str) -> str:
    if ma in ghi_de:
        return ghi_de[ma]
    m = _TRAILER.search(thong_diep)
    if m:
        return m.group(1)
    if _CLAUDE.search(thong_diep):
        return "claude_code"
    return "chua_xac_dinh"


def cham_test(tep: list[str]) -> bool:
    return any(t.startswith("tests/") or "/tests/" in t or t.endswith(".test.ts") for t in tep)


def _duong_dan_moi(p: str) -> str:
    """Numstat ghi đổi tên dạng `a/{x => y}/b` hoặc `x => y`; lấy đường dẫn mới."""
    p = _DOI_TEN_NGOAC.sub(r"\1", p)
    if " => " in p:
        p = p.split(" => ", 1)[1]
    return p.replace("//", "/")


def tach_log(tho: str) -> list[dict]:
    manh = tho.split("\x1e")
    ds = []
    # manh: ["", đầu_1, numstat_1, đầu_2, numstat_2, ...]
    for i in range(1, len(manh) - 1, 2):
        dau = manh[i].lstrip("\n")
        if not dau:
            continue
        ma, ngay, tom_tat, than = dau.split("\x1f", 3)
        tep = []
        for d in manh[i + 1].splitlines():
            cot = d.split("\t", 2)
            if len(cot) == 3:
                tep.append(_duong_dan_moi(cot[2]))
        ds.append({"ma": ma, "ngay": ngay, "tom_tat": tom_tat, "thong_diep": than, "tep": tep})
    return ds


def doc_git_log() -> str:
    kq = subprocess.run(
        ["git", "-c", "core.quotepath=false", "log", f"--format={DINH_DANG}", "--date=short", "--numstat"],
        cwd=GOC,
        capture_output=True,
        check=True,
    )
    return kq.stdout.decode("utf-8", errors="replace")


def doc_ghi_de() -> dict[str, str]:
    if not TEP_GHI_DE.exists():
        return {}
    du_lieu = json.loads(TEP_GHI_DE.read_text(encoding="utf-8") or "{}")
    # Cho phép ghi mã đầy đủ hoặc mã rút gọn.
    return {str(k): str(v) for k, v in du_lieu.items()}


def _tim_ghi_de(ghi_de: dict[str, str], ma: str) -> dict[str, str]:
    for k, v in ghi_de.items():
        if len(k) >= 7 and ma.startswith(k):
            return {ma: v}
    return {}


def _o(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def sinh_markdown(ds: list[dict], ghi_de: dict[str, str]) -> str:
    dong_bang = []
    dem: Counter[str] = Counter()
    for c in ds:
        cong_cu = phan_loai_commit(c["thong_diep"], _tim_ghi_de(ghi_de, c["ma"]), c["ma"])
        dem[cong_cu] += 1
        dong_bang.append(
            f"| {c['ngay']} | `{c['ma'][:7]}` | {_o(c['tom_tat'])} | {cong_cu} | "
            f"{len(c['tep'])} | {'có' if cham_test(c['tep']) else 'không'} |"
        )
    ra = [
        "# Truy nguồn commit theo công cụ AI",
        "",
        "Commit `chua_xac_dinh` là commit không ghi công cụ; không đoán. "
        "Tác giả xác nhận dần vào `docs/minh-bach/truy-nguon-ghi-de.json`.",
        "",
        "Sinh bằng `python -m tools.truy_nguon_commit`. Thứ tự xác định công cụ: tệp ghi đè → "
        "trailer `Cong-cu-AI:` → dòng `Co-Authored-By: Claude` → `chua_xac_dinh`.",
        "",
        "## Đếm theo công cụ",
        "",
        "| Công cụ | Số commit |",
        "|---|---|",
    ]
    for cong_cu, so in sorted(dem.items(), key=lambda x: (-x[1], x[0])):
        ra.append(f"| {cong_cu} | {so} |")
    ra.append(f"| **Tổng** | **{sum(dem.values())}** |")
    ra += [
        "",
        "## Từng commit",
        "",
        "| Ngày | Commit | Tóm tắt | Công cụ | Số tệp | Chạm test |",
        "|---|---|---|---|---|---|",
        *dong_bang,
        "",
    ]
    return "\n".join(ra)


def main() -> None:
    md = sinh_markdown(tach_log(doc_git_log()), doc_ghi_de())
    sys.stdout.buffer.write(md.encode("utf-8"))


if __name__ == "__main__":
    main()
