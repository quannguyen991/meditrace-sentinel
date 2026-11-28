# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Đo các mảnh từ liên tiếp trùng giữa bản thảo và hội thoại.
Vào → Ra : bản thảo + văn bản nguồn → độ phủ và mật độ mảnh trích.
Đọc từ   : manh_trich() tìm mảnh tham lam; do_phu_va_mat_do() tính hai chỉ số.
"""
import re
import unicodedata


def _tu(van):
    return re.findall(r"\w+", unicodedata.normalize("NFC", van.lower()))


def _manh(tom_tat, goc):
    vi_tri = {}
    for j, tu in enumerate(goc):
        vi_tri.setdefault(tu, []).append(j)
    i = 0
    while i < len(tom_tat):
        dai_nhat = 0
        for j in vi_tri.get(tom_tat[i], []):
            dai = 0
            while (i + dai < len(tom_tat) and j + dai < len(goc)
                   and tom_tat[i + dai] == goc[j + dai]):
                dai += 1
            dai_nhat = max(dai_nhat, dai)
        if dai_nhat:
            yield tom_tat[i:i + dai_nhat]
            i += dai_nhat
        else:
            i += 1


def manh_trich(van_tom_tat: str, van_goc: str) -> list[str]:
    """Tìm mảnh dài nhất tại từng vị trí bản thảo, rồi tiến qua mảnh đó."""
    return [" ".join(m) for m in _manh(_tu(van_tom_tat), _tu(van_goc))]


def do_phu_va_mat_do(van_tom_tat: str, van_goc: str) -> dict:
    """Tính độ phủ và mật độ theo Grusky, Naaman & Artzi (2018)."""
    tom_tat = _tu(van_tom_tat)
    do_dai = [len(m) for m in _manh(tom_tat, _tu(van_goc))]
    n = len(tom_tat)
    return {"coverage": sum(do_dai) / n if n else 0.0,
            "density": sum(x * x for x in do_dai) / n if n else 0.0,
            "so_tu": n}
