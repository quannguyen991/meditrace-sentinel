# -*- coding: utf-8 -*-
"""Tri thuc thuoc — MOT nguon cho ca he thong (25/11/2026).

Truoc ngay nay lieu toi da paracetamol 4000 mg nam o it nhat 3 noi (`guardrails`,
`duoc_ly_lam_sang`, `aho_corasick_duoc_thu`), lieu tre em o `kiem_duyet_bhyt_va_bo_sot`,
danh sach thuoc khoang dieu tri hep o `cong_rui_ro`, tu dien ten thuoc o `thuc_the` — moi
noi mot danh sach, co cho trai nhau (omeprazole 40 hay 80 mg/ngay), va hau het khong ghi
nguon. Gio tat ca doc tu `data/tri_thuc_thuoc.json`.

MOI MUC co `nguon` (chep tu dau, co so trang hay khong) va `da_duyet`. Muc `da_duyet=false`
chi duoc sinh canh bao muc "can xem", khong bao gio chan. KHONG ai tu dat `da_duyet=true`
tru nguoi co chuyen mon da tra lai nguon — xem docs/tri-thuc-thuoc-can-duyet.md.
"""
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple

TEP = Path(__file__).resolve().parents[1] / "data" / "tri_thuc_thuoc.json"


@dataclass(frozen=True)
class LieuToiDa:
    gia_tri: float
    don_vi: str
    nguon: str
    da_duyet: bool
    moi_lan: Optional[float] = None
    ghi_chu: str = ""


def _khoa(ten: str) -> str:
    """Khoa so khop: viet thuong, bo 'e' cuoi (omeprazol = omeprazole, cefixim = cefixime)."""
    t = re.sub(r"\s+", " ", (ten or "").strip().lower())
    return t[:-1] if len(t) > 5 and t.endswith("e") else t


@lru_cache(maxsize=1)
def _du_lieu() -> dict:
    return json.loads(TEP.read_text(encoding="utf-8"))


def tat_ca() -> List[dict]:
    return list(_du_lieu()["muc"])


@lru_cache(maxsize=1)
def _bang_ten() -> Dict[str, str]:
    """{khoa ten: hoat chat} cho hoat chat, ten khac va biet duoc."""
    ra = {}
    for m in tat_ca():
        for t in [m["hoat_chat"], *m.get("ten_khac", []), *m.get("biet_duoc", [])]:
            ra.setdefault(_khoa(t), m["hoat_chat"])
    return ra


@lru_cache(maxsize=1)
def _theo_hoat_chat() -> Dict[str, dict]:
    return {m["hoat_chat"]: m for m in tat_ca()}


def tat_ca_ten() -> List[str]:
    """Moi ten (hoat chat, ten khac, biet duoc), viet thuong, dai truoc."""
    ten = {t.lower() for m in tat_ca() for t in [m["hoat_chat"], *m.get("ten_khac", []), *m.get("biet_duoc", [])]}
    return sorted(ten, key=lambda t: (-len(t), t))


def ten_cua(hc: str) -> List[str]:
    m = _theo_hoat_chat().get(hoat_chat(hc) or "")
    return [] if m is None else [t.lower() for t in [m["hoat_chat"], *m.get("ten_khac", []), *m.get("biet_duoc", [])]]


@lru_cache(maxsize=1)
def regex_ten_thuoc() -> "re.Pattern":
    # Mau cho moi ten (co hoac khong 'e' cuoi), ranh gioi chu chiu duoc chu co dau.
    phan = sorted({re.escape(t[:-1]) + "e?" if len(t) > 5 and t.endswith("e") else re.escape(t) + "e?"
                   for t in tat_ca_ten()}, key=lambda s: -len(s))
    return re.compile(r"(?i)(?<![\w-])(" + "|".join(phan) + r")(?![\w-])")


def hoat_chat(ten: str) -> Optional[str]:
    """Biet duoc / ten khac / hoat chat -> hoat chat. Chuoi dai ("panadol extra") -> ten dai
    nhat tim thay trong chuoi. None khi khong biet."""
    k = _khoa(ten)
    if k in _bang_ten():
        return _bang_ten()[k]
    tim = [m.group(1) for m in regex_ten_thuoc().finditer(ten or "")]
    if not tim:
        return None
    return _bang_ten().get(_khoa(max(tim, key=len)))


def la_nti(hc: str) -> bool:
    m = _theo_hoat_chat().get(hoat_chat(hc) or "")
    return bool(m and m.get("nti"))


def lieu_toi_da(hc: str, doi_tuong: Literal["nguoi_lon", "tre_em"]) -> Optional[LieuToiDa]:
    m = _theo_hoat_chat().get(hoat_chat(hc) or "")
    l = ((m or {}).get("lieu_toi_da") or {}).get(doi_tuong)
    if not l:
        return None
    return LieuToiDa(gia_tri=float(l["gia_tri"]), don_vi=l["don_vi"], nguon=m["nguon"], da_duyet=m["da_duyet"],
                     moi_lan=l.get("moi_lan"), ghi_chu=l.get("ghi_chu", ""))


# ---- bang dan xuat cho cac mo-dun cu (giu giao dien cu, doc tu cung mot nguon) ----

def bang_lieu_nguoi_lon() -> Dict[str, float]:
    """{moi ten: mg/ngay} — thay `guardrails.LIEU_TRAN`, `duoc_ly_lam_sang.LIEU_TOI_DA_NGAY`."""
    ra = {}
    for m in tat_ca():
        l = (m.get("lieu_toi_da") or {}).get("nguoi_lon")
        if l:
            for t in ten_cua(m["hoat_chat"]):
                ra[t] = float(l["gia_tri"])
    return ra


def bang_lieu_tre_em() -> Dict[str, Tuple[float, float, str]]:
    """{moi ten: (mg/kg/lan, mg/kg/ngay, ghi chu)} — thay `LIEU_TRAN_NHI_KHOA_MG_KG_NGAY`."""
    ra = {}
    for m in tat_ca():
        l = (m.get("lieu_toi_da") or {}).get("tre_em")
        if l:
            for t in ten_cua(m["hoat_chat"]):
                ra[t] = (float(l.get("moi_lan") or l["gia_tri"]), float(l["gia_tri"]), l.get("ghi_chu", ""))
    return ra


def ten_nti() -> set:
    """Ten HOAT CHAT cua thuoc khoang dieu tri hep — thay `cong_rui_ro.THUOC_KHOANG_DIEU_TRI_HEP`.
    Chi hoat chat (cong "sintrom", co san trong bang cu): mo rong sang biet duoc (coumadin,
    tegretol...) doi muc nguy co cua chinh sach C tu du lieu chua duyet (ra soat 25/11)."""
    return {m["hoat_chat"] for m in tat_ca() if m.get("nti")} | {"sintrom"}
