# -*- coding: utf-8 -*-
"""Nap ViMQ (cau hoi y te cua benh nhan, co nhan thuc the) thanh mau cho khau trich.

ViMQ (https://github.com/tadeephuy/ViMQ, phat hanh hoc thuat, phi thuong mai) la cac cau
hoi DON LE da tach tu (noi tu bang dau gach duoi: `dong_mach`), kem `seq_label` la cac doan
thuc the `[bat_dau, ket_thuc, loai]` theo CHI SO TU (ket_thuc tinh ca). Khong co hoi thoai,
khong co chu the, phu dinh, thoi gian.

De cho khau trich cua du an doc duoc, moi cau duoc bo gach duoi roi boc thanh mot luot
`Benh nhan: <cau>` (gia dinh: nguoi hoi la benh nhan; ghi ro trong bao cao). Thuc the goc
duoc giu lai de DO phu (khong dung de huan luyen truc tiep).
"""
from __future__ import annotations

import json
from pathlib import Path


def bo_gach_duoi(s: str) -> str:
    return " ".join(str(s or "").replace("_", " ").split())


def doc_vimq(duong_dan: str | Path, tap: str = "train") -> list[dict]:
    """-> [{"id", "input", "cau", "thuc_the": [{"text", "loai"}], "y_dinh"}].

    Dong co chi so thuc the ngoai pham vi cau bi bo qua rieng (khong lam hong ca tep).
    """
    du_lieu = json.loads(Path(duong_dan).read_text(encoding="utf-8"))
    if not isinstance(du_lieu, list):
        raise ValueError(f"{duong_dan}: can mot danh sach")
    ra = []
    for i, d in enumerate(du_lieu):
        cau = d.get("sentence")
        if not isinstance(cau, str) or not cau.strip():
            continue
        tu = cau.split()
        the = []
        for nhan in d.get("seq_label") or []:
            try:
                b, k, loai = int(nhan[0]), int(nhan[1]), str(nhan[2])
            except (TypeError, ValueError, IndexError):
                continue
            if 0 <= b <= k < len(tu):
                the.append({"text": bo_gach_duoi(" ".join(tu[b:k + 1])), "loai": loai})
        sach = bo_gach_duoi(cau)
        ra.append({"id": f"vimq_{tap}_{i:05d}", "input": f"Bệnh nhân: {sach}", "cau": sach,
                   "thuc_the": the, "y_dinh": d.get("sent_label")})
    return ra
