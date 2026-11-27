# -*- coding: utf-8 -*-
"""Cay DUNG MOT loi da biet vao ban ghi hoan hao (dap an -> PhatBieu) de do lop canh bao ma
khong can nhan nguoi (plan docs/superpowers/plans/2026-11-25-cay-loi-do-canh-bao.md).

    moi, c = cay(ps, ca, "doi_lieu", random.Random(42))   # None khi khong ap dung

`ps` khong bi sua; `c` ghi loai, id menh de bi cay (hoac bi xoa / moi them) va luot cua no.
Moi so do bang bo nay la "tren loi cay nhan tao": loi cay sach hon loi mo hinh mac that.
"""
import json
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from src.duong_ong import b5_xep_cho_cong_rui_ro as cong_rui_ro
from src.cong_cu_lam_sang import tri_thuc_thuoc as tri_thuc_thuoc
from src.do_luong.danh_gia_khoa import vao_than
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu

GOC = Path(__file__).resolve().parents[1]
TEP_IDS = GOC / "data" / "cay_loi" / "tap_dieu_chinh_ids.json"

LOAI_CAY = ("doi_chu_the", "dao_phu_dinh", "nang_chac_chan", "gia_dinh_thanh_that", "ban_cu_con_hieu_luc",
            "doi_lieu", "doi_so", "doi_thuoc", "doi_thoi_gian", "bia_menh_de", "bia_trich_dan", "doi_bang_chung",
            "xoa_di_ung", "xoa_thuoc", "xoa_phu_dinh", "xoa_so_lieu")

NHOM_DUNG = {
    "doi_chu_the": {"SUBJECT_ATTRIBUTION"},
    "dao_phu_dinh": {"NEGATION_ASSERTION"},
    "nang_chac_chan": {"NEGATION_ASSERTION"},
    "gia_dinh_thanh_that": {"PLAN_FACT_CONDITIONAL"},
    "ban_cu_con_hieu_luc": {"STATE_UPDATE"},
    "doi_lieu": {"ENTITY_VALUE"},
    "doi_so": {"ENTITY_VALUE", "TEMPORAL"},
    "doi_thuoc": {"ENTITY_VALUE", "UNSUPPORTED"},
    "doi_thoi_gian": {"TEMPORAL", "ENTITY_VALUE"},
    "bia_menh_de": {"UNSUPPORTED", "ENTITY_VALUE", "EVIDENCE_PROVENANCE"},
    "bia_trich_dan": {"EVIDENCE_PROVENANCE", "UNSUPPORTED"},
    "doi_bang_chung": {"EVIDENCE_PROVENANCE"},
    "xoa_di_ung": {"OMISSION"},
    "xoa_thuoc": {"OMISSION"},
    "xoa_phu_dinh": {"OMISSION"},
    "xoa_so_lieu": {"OMISSION"},
}

_DON_VI_LIEU = r"(?:mg|g|gam|mcg|µg|ml|ui|iu)"
_LIEU = re.compile(r"(?<![\w.,])(\d+(?:[.,]\d+)?)(\s*" + _DON_VI_LIEU + r")(?!\w)", re.I)
_SO = re.compile(r"(?<![\w.,])(\d+(?:[.,]\d+)?)(?![\w.,]*\s*" + _DON_VI_LIEU + r"(?!\w))(?![.,]?\d)")
_PHU = re.compile(r"^\s*(không|chưa|chẳng)\s+", re.I)
MOC_THAY = ("ba năm trước", "hôm qua", "mười năm nay", "từ tuần trước", "hai tháng nay", "từ sáng nay")


@dataclass(frozen=True)
class Cay:
    loai: str
    phat_bieu_id: Optional[int]
    luot: Tuple[int, ...] = field(default_factory=tuple)
    mo_ta: str = ""

    def __post_init__(self):
        object.__setattr__(self, "luot", tuple(self.luot))


def _sao(ps):
    return [PhatBieu(**p.to_dict()) for p in ps]


def _con(p):
    return p.trang_thai != "bị thay thế"


def _so_ra_chuoi(x: float, mau: str) -> str:
    s = f"{x:g}"
    return s.replace(".", ",") if "," in mau else s


def _vai(ca):
    dong = [d for d in str(ca.get("input") or "").split("\n") if d.strip()]
    return {i: d.split(":", 1)[0].strip().lower() for i, d in enumerate(dong, 1)}


def _ung_vien(ps, ca, loai):
    if loai == "doi_chu_the":
        return [p for p in ps if vao_than(p)]
    if loai == "dao_phu_dinh":
        return [p for p in ps if vao_than(p)]
    if loai == "nang_chac_chan":
        return [p for p in ps if _con(p) and p.do_chac_chan != "chắc chắn"]
    if loai == "gia_dinh_thanh_that":
        return [p for p in ps if _con(p) and p.tinh_huong != "thực tế"]
    if loai == "ban_cu_con_hieu_luc":
        return [p for p in ps if p.trang_thai == "bị thay thế"]
    if loai == "doi_lieu":
        return [p for p in ps if vao_than(p) and _LIEU.search(p.noi_dung)]
    if loai in ("doi_so", "xoa_so_lieu"):
        return [p for p in ps if vao_than(p) and _SO.search(p.noi_dung)]
    if loai == "doi_thuoc":
        return [p for p in ps if vao_than(p) and tri_thuc_thuoc.regex_ten_thuoc().search(p.noi_dung)]
    if loai == "doi_thoi_gian":
        return [p for p in ps if vao_than(p) and p.moc_thoi_gian]
    if loai in ("bia_trich_dan",):
        return [p for p in ps if vao_than(p) and p.trich_dan]
    if loai == "doi_bang_chung":
        bs = {i for i, v in _vai(ca).items() if v.startswith("bác sĩ")}
        return [p for p in ps if vao_than(p) and p.bang_chung and bs - set(p.bang_chung)]
    if loai == "xoa_di_ung":
        return [p for p in ps if vao_than(p) and not p.phu_dinh and cong_rui_ro.loai_thong_tin(p) == "di_ung"]
    if loai == "xoa_thuoc":
        return [p for p in ps if vao_than(p) and not p.phu_dinh
                and cong_rui_ro.loai_thong_tin(p) in ("thuoc", "thuoc_nti")]
    if loai == "xoa_phu_dinh":
        return [p for p in ps if vao_than(p) and p.phu_dinh]
    raise ValueError(loai)


def _bia(ps, ca, rng):
    hoi = str(ca.get("input") or "").lower()
    ten = [t for t in tri_thuc_thuoc.tat_ca_ten() if " " not in t and t not in hoi and len(t) > 4]
    bn = [i for i, v in _vai(ca).items() if not v.startswith(("bác sĩ", "điều dưỡng"))]
    if not ten or not bn:
        return None
    t = rng.choice(sorted(ten))
    luot = rng.choice(bn)
    dong = [d for d in str(ca["input"]).split("\n") if d.strip()][luot - 1].split(":", 1)[-1].strip()
    la_di_ung = rng.random() < 0.5
    p = PhatBieu(id=max([q.id for q in ps] + [-1]) + 1, nguoi_noi="bệnh nhân", chu_the_id=0,
                 noi_dung=("dị ứng " if la_di_ung else "đang dùng ") + t, bang_chung=[luot], trich_dan=[dong],
                 ten_chu_the="bệnh nhân", hanh_vi="trả lời",
                 thuoc=None if la_di_ung else {"ten": t, "lieu": None, "so_lan": None, "duong_dung": None,
                                               "bat_dau": None, "ngung": None, "trang_thai_dung": "đang dùng"})
    return _sao(ps) + [p], Cay("bia_menh_de", p.id, [luot], p.noi_dung)


def cay(ps: List[PhatBieu], ca: dict, loai: str, rng: random.Random):
    """-> (danh sach MOI, Cay) hoac None khi ca khong co menh de du dieu kien cho `loai`."""
    if loai == "bia_menh_de":
        return _bia(ps, ca, rng)
    ung = sorted(_ung_vien(ps, ca, loai), key=lambda p: p.id)
    if not ung:
        return None
    dich = rng.choice(ung)
    if loai.startswith("xoa_"):
        return [p for p in _sao(ps) if p.id != dich.id], Cay(loai, dich.id, dich.bang_chung, dich.noi_dung)
    moi = _sao(ps)
    q = next(p for p in moi if p.id == dich.id)
    mo_ta = ""
    if loai == "doi_chu_the":
        q.chu_the_id = 1 if q.chu_the_id == 0 else 0
        q.ten_chu_the = "người nhà" if q.chu_the_id else "bệnh nhân"
    elif loai == "dao_phu_dinh":
        # Phu dinh co hieu luc = phu_dinh XOR "không" dau cau (cham_he_thong._phu_dinh_that). Chi dao
        # co, giu noi dung — them "không" ma dong thoi bat co thi hai lan dao triet tieu (do moc 25/11).
        q.phu_dinh = not q.phu_dinh
    elif loai == "nang_chac_chan":
        q.do_chac_chan = "chắc chắn"
    elif loai == "gia_dinh_thanh_that":
        q.tinh_huong = "thực tế"
    elif loai == "ban_cu_con_hieu_luc":
        q.trang_thai = "còn hiệu lực"
    elif loai == "doi_lieu":
        m = _LIEU.search(q.noi_dung)
        cu = m.group(1) + m.group(2)
        moi_lieu = _so_ra_chuoi(float(m.group(1).replace(",", ".")) * 10, m.group(1)) + m.group(2)
        q.noi_dung = q.noi_dung[:m.start()] + moi_lieu + q.noi_dung[m.end():]
        if q.thuoc and q.thuoc.get("lieu"):
            q.thuoc = dict(q.thuoc, lieu=_LIEU.sub(lambda k: _so_ra_chuoi(
                float(k.group(1).replace(",", ".")) * 10, k.group(1)) + k.group(2), q.thuoc["lieu"], count=1))
        mo_ta = f"{cu} -> {moi_lieu}"
    elif loai == "doi_so":
        m = _SO.search(q.noi_dung)
        so = _so_ra_chuoi(float(m.group(1).replace(",", ".")) + 2, m.group(1))
        q.noi_dung = q.noi_dung[:m.start()] + so + q.noi_dung[m.end():]
        mo_ta = f"{m.group(1)} -> {so}"
    elif loai == "doi_thuoc":
        m = tri_thuc_thuoc.regex_ten_thuoc().search(q.noi_dung)
        hc = tri_thuc_thuoc.hoat_chat(m.group(1))
        khac = sorted(m2["hoat_chat"].lower() for m2 in tri_thuc_thuoc.tat_ca()
                      if m2["hoat_chat"] != hc and " " not in m2["hoat_chat"])
        t = rng.choice(khac)
        q.noi_dung = q.noi_dung[:m.start()] + t + q.noi_dung[m.end():]
        if q.thuoc:
            q.thuoc = dict(q.thuoc, ten=t)
        mo_ta = f"{m.group(1)} -> {t}"
    elif loai == "doi_thoi_gian":
        t = rng.choice([x for x in MOC_THAY if x != q.moc_thoi_gian])
        if q.moc_thoi_gian in q.noi_dung:
            q.noi_dung = q.noi_dung.replace(q.moc_thoi_gian, t)
        q.moc_thoi_gian = t
    elif loai == "bia_trich_dan":
        q.trich_dan = [f"{q.noi_dung} từ tuần trước"] + list(q.trich_dan[1:])
    elif loai == "doi_bang_chung":
        bs = sorted(i for i, v in _vai(ca).items() if v.startswith("bác sĩ") and i not in q.bang_chung)
        q.bang_chung = [rng.choice(bs)]
        q.trich_dan = list(q.trich_dan[:1])
    return moi, Cay(loai, dich.id, dich.bang_chung, mo_ta or dich.noi_dung)


def tap_dieu_chinh() -> List[dict]:
    """400 ca dieu chinh theo `data/cay_loi/tap_dieu_chinh_ids.json` (dang ky truoc 25/11/2026)."""
    meta = json.loads(TEP_IDS.read_text(encoding="utf-8"))
    can = set(meta["ids"])
    ds = [json.loads(l) for l in (GOC / meta["nguon"]).read_text(encoding="utf-8").splitlines() if l.strip()]
    ra = [d for d in ds if d["id"] in can]
    assert len(ra) == meta["so_ca"], "tep nguon da doi so voi dang ky truoc"
    return ra


def tap_giu_kin() -> List[dict]:
    """Dap an 240 ca cua data/thach_thuc_v2 — CHI chay mot lan sau khi khoa luat."""
    ra = []
    for f in sorted((GOC / "data" / "thach_thuc_v2").glob("thach_thuc_*.jsonl")):
        ra += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    return ra
