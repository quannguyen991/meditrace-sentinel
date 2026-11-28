"""Minh chứng 1b: mọi dòng bảng trong sổ quyết định và bảng "AI hỗ trợ / đội tự sửa"
phải có ít nhất một bằng chứng kiểm được.

Bằng chứng hợp lệ (nằm trong dấu backtick):
- mã commit 7 ký tự hex, phải qua `git cat-file -e <ma>^{commit}`;
- đường dẫn bắt đầu bằng src/, web/, tools/, docs/, tests/, data/ và phải tồn tại.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[1]
TEP = [
    GOC / "docs" / "minh-bach" / "so-quyet-dinh-thiet-ke.md",
    GOC / "docs" / "minh-bach" / "ai-ho-tro-va-doi-tu-sua.md",
]
TIEN_TO = ("src/", "web/", "tools/", "docs/", "tests/", "data/")
RE_BACKTICK = re.compile(r"`([^`]+)`")
RE_COMMIT = re.compile(r"^[0-9a-f]{7}$")
RE_PHAN_CACH = re.compile(r"^\|[\s:\-|]+\|\s*$")


def _dong_than_bang(van_ban: str) -> list[str]:
    """Trả về các dòng thân bảng (bỏ dòng tiêu đề và dòng ---)."""
    ket_qua: list[str] = []
    dong = van_ban.splitlines()
    for i, d in enumerate(dong):
        if not d.startswith("| "):
            continue
        if RE_PHAN_CACH.match(d):
            continue
        # Dòng tiêu đề: dòng ngay sau nó là dòng phân cách.
        if i + 1 < len(dong) and RE_PHAN_CACH.match(dong[i + 1]):
            continue
        ket_qua.append(d)
    return ket_qua


def _commit_ton_tai(ma: str) -> bool:
    r = subprocess.run(
        ["git", "cat-file", "-e", f"{ma}^{{commit}}"],
        cwd=GOC,
        capture_output=True,
    )
    return r.returncode == 0


def _bang_chung(dong: str) -> tuple[list[str], list[str]]:
    """Trả về (bằng chứng hợp lệ, bằng chứng hỏng) trong một dòng."""
    hop_le: list[str] = []
    hong: list[str] = []
    for m in RE_BACKTICK.findall(dong):
        s = m.strip()
        if RE_COMMIT.match(s):
            (hop_le if _commit_ton_tai(s) else hong).append(s)
        elif s.startswith(TIEN_TO):
            duong = s.split("#", 1)[0].split("::", 1)[0]
            (hop_le if (GOC / duong).exists() else hong).append(s)
    return hop_le, hong


@pytest.mark.skipif(shutil.which("git") is None, reason="cần git")
@pytest.mark.parametrize("tep", TEP, ids=lambda p: p.name)
def test_moi_dong_co_bang_chung_that(tep: Path) -> None:
    assert tep.exists(), f"chưa có tệp {tep.relative_to(GOC)}"
    dong = _dong_than_bang(tep.read_text(encoding="utf-8"))
    assert len(dong) >= 5, f"{tep.name}: quá ít dòng bảng ({len(dong)})"
    loi: list[str] = []
    for d in dong:
        hop_le, hong = _bang_chung(d)
        if hong:
            loi.append(f"bằng chứng không kiểm được {hong}: {d[:90]}")
        if not hop_le:
            loi.append(f"không có bằng chứng: {d[:90]}")
    assert not loi, "\n".join(loi)
