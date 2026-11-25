# -*- coding: utf-8 -*-
"""Doc va ghep chep loi VietMed thanh doan hoi thoai (Task B5 cua ke hoach).

Tep `labeled_medical_data/*_transcript.txt` cua VietMed la mot DANH SACH KIEU TU DIEN
PYTHON (nhay don), KHONG phai JSON, nen doc bang `ast.literal_eval` (khong dung `eval`).
Moi phan tu: {'text', 'speaker_name', 'file', 'duration'}. Moi phan tu la mot lat cat
khoang 5 giay cua ghi am dai, nen phai ghep lai theo ban ghi (thu muc cua `file`) moi
co doan hoi thoai.

Chua co nhan menh de: doan nay dung lam bo danh gia hoac gan nhan sau (Task E3, E4).
"""
from __future__ import annotations

import ast
import re
from pathlib import Path


def doc_chep_loi(duong_dan: str | Path) -> list[dict]:
    """Doc mot tep `*_transcript.txt`. Noi dung khong phai danh sach tu dien hop le
    -> `ValueError` ro rang, khong thuc thi ma."""
    van_ban = Path(duong_dan).read_text(encoding="utf-8")
    try:
        x = ast.literal_eval(van_ban)
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"{duong_dan}: khong phai danh sach tu dien Python hop le ({e})") from e
    if not isinstance(x, list) or not all(isinstance(d, dict) for d in x):
        raise ValueError(f"{duong_dan}: can mot danh sach cac tu dien")
    return x


def ma_ghi_am(dong: dict) -> str:
    """Ma ban ghi: thu muc dau cua `file` (vi du `VietMed_007/1465.0_1470.0.ogg` ->
    `VietMed_007`). Thieu `file` thi lay `speaker_name` bo hau to `_a`/`_b`."""
    f = str(dong.get("file") or "")
    if "/" in f:
        return f.split("/", 1)[0]
    ten = str(dong.get("speaker_name") or "")
    return re.sub(r"_[a-z]$", "", ten) or "khong-ro"


def ghep_doan(dong: list[dict], toi_da_ky_tu: int = 6000) -> list[dict]:
    """Gom cac dong LIEN TIEP cung ban ghi thanh doan; cat khi qua `toi_da_ky_tu`.

    -> [{"id", "luot": [{"nguoi_noi", "van_ban"}], "van_ban", "so_dong"}]. Nguoi noi
    (`speaker_name`, vi du `VietMed_007_a`) duoc giu nguyen tung luot de buoc sau gan vai.
    Dong khong co `text` hoac rong bi bo qua. Mot dong don le dai hon gioi han van duoc
    giu thanh mot doan rieng (khong cat giua cau).
    """
    ra: list[dict] = []
    hien, ma_hien, dai = None, None, 0
    stt: dict[str, int] = {}

    def dong_doan():
        nonlocal hien, dai
        if hien and hien["luot"]:
            hien["van_ban"] = " ".join(x["van_ban"] for x in hien["luot"])
            hien["so_dong"] = len(hien["luot"])
            ra.append(hien)
        hien, dai = None, 0

    for d in dong:
        text = str(d.get("text") or "").strip()
        if not text:
            continue
        ma = ma_ghi_am(d)
        if hien is None or ma != ma_hien or (dai + len(text) + 1 > toi_da_ky_tu and hien["luot"]):
            dong_doan()
            stt[ma] = stt.get(ma, 0) + 1
            hien = {"id": f"{ma}#{stt[ma]}", "luot": []}
            ma_hien = ma
        hien["luot"].append({"nguoi_noi": str(d.get("speaker_name") or ""), "van_ban": text})
        dai += len(text) + 1
    dong_doan()
    return ra
