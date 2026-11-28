# -*- coding: utf-8 -*-
"""Mã sản phẩm Python chỉ có một lối ra mạng: gọi máy xa của đội (mặc định tắt, bật bằng --mo-hinh-xa)."""
import re
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
MAU = re.compile(r"urlopen\(|\brequests\.|\bhttpx\.|http\.client")
DUOC_PHEP = {"src/he_thong/dich_vu_http.py": 1}


def test_chi_mot_loi_ra_mang_python():
    dem = {}
    for tep in (GOC / "src").rglob("*.py"):
        n = len(MAU.findall(tep.read_text(encoding="utf-8", errors="ignore")))
        if n:
            dem[tep.relative_to(GOC).as_posix()] = n
    assert dem == DUOC_PHEP
