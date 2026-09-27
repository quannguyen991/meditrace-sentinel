# -*- coding: utf-8 -*-
"""Moi tep .ps1 chi duoc chua ky tu ASCII.

VI SAO. PowerShell 5.1 doc tep UTF-8 KHONG co BOM theo bang ma ANSI. Mot dau
gach dai hay mot chu co dau trong CHU THICH cung thanh ky tu la, va neu ky tu
la do chua dau nhay thi kich ban vo cu phap giua chung — thuong la o mot dong
hoan toan khac cho co ky tu do, nen rat kho lan ra.

Da xay ra that mot lan: mot dau gach dai lam ca chuoi chay dem dung o buoc dau.

Va quy tac nay de vi pham lai: 10/09/2026 mot lan sua chu thich them dung mot
dau gach dai vao `chay-bo-5000.ps1`. Kiem bang mat khong chan duoc — dau gach
dai va dau gach ngang trong nhu nhau.
"""
import pathlib

import pytest

PS1 = sorted(pathlib.Path("tools").glob("*.ps1"))


def test_co_tep_ps1_de_kiem():
    """Neu glob khong khop gi thi cac test duoi deu xanh ma khong kiem gi ca."""
    assert PS1, "khong tim thay tep .ps1 nao trong tools/"


@pytest.mark.parametrize("p", PS1, ids=lambda p: p.name)
def test_chi_chua_ascii(p):
    b = p.read_bytes()
    xau = [(i, b[i]) for i in range(len(b)) if b[i] > 127]
    if xau:
        i = xau[0][0]
        quanh = b[max(0, i - 40):i + 20].decode("utf-8", "replace")
        pytest.fail(f"{p.name}: {len(xau)} byte ngoai ASCII, "
                    f"cho dau tien o vi tri {i}: ...{quanh}...")


@pytest.mark.parametrize("p", PS1, ids=lambda p: p.name)
def test_khong_chua_ky_tu_tab(p):
    """Tab trong .ps1 gan nhu luon la dau vet cua mot `\\t` bi nuot khi sinh
    tep bang heredoc — da xay ra bon lan trong du an nay."""
    b = p.read_bytes()
    assert 9 not in b, (
        f"{p.name}: co ky tu tab. Rat co the mot duong dan Windows da bi nuot "
        f"dau gach nguoc (`\\tools\\` -> tab).")
