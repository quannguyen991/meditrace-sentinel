"""Kiem tra moi tai lieu minh bach chi tro toi duong dan co that trong repo.

Quy tac:
1. Link Markdown [text](target) (khong phai http/https/mailto/#...) phai tro toi tep
   ton tai, tinh tu thu muc chua file .md. Bo phan #anchor va :dong.
2. Ma inline `...` co dang duong dan repo (bat dau bang src/, web/, tools/, docs/,
   tests/, data/, .githooks/; khong khoang trang, *, <, {) phai ton tai, tinh tu
   goc repo. Bo hau to :dong hoac :a-b. Bo qua duong dan chua viet_kiem_tra_cuoi
   (bo de niem phong, khong mo).
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs" / "minh-bach"

PHONG_LUU = "viet_kiem_tra_cuoi"
TIEN_TO_REPO = ("src/", "web/", "tools/", "docs/", "tests/", "data/", ".githooks/")

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
CODE_RE = re.compile(r"`([^`\n]+)`")
HAU_TO_DONG_RE = re.compile(r":\d+(?:-\d+)?$")
NGOAI_RE = re.compile(r"^(?:https?:|mailto:)", re.IGNORECASE)
KHONG_PHAI_DUONG_DAN_RE = re.compile(r"[\s*<{]")


def _bo_hau_to(duong_dan: str) -> str:
    duong_dan = duong_dan.split("#", 1)[0]
    return HAU_TO_DONG_RE.sub("", duong_dan)


def _thu_thap_lien_ket(noi_dung: str):
    """Tra ve cac duong dan tuong doi tu link Markdown."""
    ket_qua = []
    for m in LINK_RE.finditer(noi_dung):
        dich = m.group(1)
        if NGOAI_RE.match(dich) or dich.startswith("#"):
            continue
        duong = _bo_hau_to(dich)
        if duong:
            ket_qua.append(duong)
    return ket_qua


def _thu_thap_ma_duong_dan(noi_dung: str):
    """Tra ve cac ma inline trong backtick trông giong duong dan repo."""
    ket_qua = []
    for m in CODE_RE.finditer(noi_dung):
        ma = m.group(1).strip()
        if not ma.startswith(TIEN_TO_REPO):
            continue
        if KHONG_PHAI_DUONG_DAN_RE.search(ma):
            continue
        duong = _bo_hau_to(ma)
        if not duong or PHONG_LUU in duong:
            continue
        ket_qua.append(duong)
    return ket_qua


def test_moi_duong_dan_trong_minh_bach_ton_tai():
    thieu = set()
    for tep in sorted(DOCS.glob("*.md")):
        noi_dung = tep.read_text(encoding="utf-8")

        for duong in _thu_thap_lien_ket(noi_dung):
            if PHONG_LUU in duong:
                continue
            if not (tep.parent / duong).exists():
                thieu.add((tep.name, duong))

        for duong in _thu_thap_ma_duong_dan(noi_dung):
            if not (REPO / duong).exists():
                thieu.add((tep.name, duong))

    assert not thieu, (
        f"{len(thieu)} duong dan trong docs/minh-bach khong ton tai:\n"
        + "\n".join(f"{ten} -> {duong}" for ten, duong in sorted(thieu))
    )
