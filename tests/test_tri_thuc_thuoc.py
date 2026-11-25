# -*- coding: utf-8 -*-
"""Tri thuc thuoc: MOT nguon (data/tri_thuc_thuoc.json), moi muc co nguon va da_duyet."""
import json
import re
from pathlib import Path

from src import kho_khuon, tri_thuc_thuoc as ttt

GOC = Path(__file__).resolve().parents[1]
TEN_NHOM_KHONG_PHAI_THUOC = {"statin", "cephalosporin", "fluoroquinolone", "thiazide", "triptan",
                             "aminopenicillin", "disease", "orabase", "ceramide", "bromide", "kinase",
                             "methicillin"}  # MRSA, khong phai thuoc dieu tri
_HAU_TO = re.compile(r"(cillin|mycin|micin|cyclin|floxacin|pril|sartan|statin|olol|prazol|prazole|dipin|dipine|azol"
                     r"|azole|mab|tinib|parin|xaban|semide|lukast|setron|zepam|zolam|ofen|fenac|coxib|sone|solon|olone"
                     r"|formin|flozin|triptan|vir|cycline|nidazol|cef\w+|ceph\w+)$")


def test_moi_muc_co_nguon_va_da_duyet():
    for m in ttt.tat_ca():
        assert m["nguon"].strip(), m["hoat_chat"]
        assert isinstance(m["da_duyet"], bool), m["hoat_chat"]


def test_khong_tu_dat_da_duyet():
    assert not [m["hoat_chat"] for m in ttt.tat_ca() if m["da_duyet"]]


def test_hoat_chat_tu_biet_duoc():
    assert ttt.hoat_chat("Hapacol") == "paracetamol"
    assert ttt.hoat_chat("panadol extra") == "paracetamol"
    assert ttt.hoat_chat("omeprazol") == ttt.hoat_chat("omeprazole") == "omeprazole"
    assert ttt.hoat_chat("nước lọc") is None


def test_sintrom_khong_phai_warfarin():
    # Sintrom la acenocoumarol. Bang cu ghi la biet duoc cua warfarin.
    assert ttt.hoat_chat("sintrom") == "acenocoumarol"


def test_nti():
    assert ttt.la_nti("warfarin") and ttt.la_nti("digoxin") and not ttt.la_nti("paracetamol")


def test_lieu_toi_da():
    l = ttt.lieu_toi_da("paracetamol", "nguoi_lon")
    assert l.gia_tri == 4000.0 and l.don_vi == "mg/ngày" and l.nguon and l.da_duyet is False
    tre = ttt.lieu_toi_da("paracetamol", "tre_em")
    assert tre.gia_tri == 60.0 and tre.don_vi == "mg/kg/ngày"
    assert ttt.lieu_toi_da("ceftriaxone", "nguoi_lon") is None


def test_regex_ten_thuoc():
    bt = ttt.regex_ten_thuoc()
    assert bt.search("bé uống Hapacol 250") and bt.search("tiêm ceftriaxone 1g")
    assert not bt.search("bé uống nước cam")


def test_khong_con_lieu_viet_cung():
    """Khong con bang lieu viet cung canh ten thuoc ngoai tri_thuc_thuoc."""
    bt = re.compile(r"""["'](paracetamol|panadol|hapacol|ibuprofen|aspirin|metformin)["']\s*:\s*\(?\s*\d""")
    vi_pham = []
    for p in (GOC / "src").rglob("*.py"):
        if p.name in ("tri_thuc_thuoc.py", "ngu_lieu_viet.py") or p.name.startswith("khuon_"):
            continue
        for i, d in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if bt.search(d) or re.search(r"lieu_toi_da_24h_mg\s*=\s*\d", d):
                vi_pham.append(f"{p.name}:{i}")
    assert not vi_pham, vi_pham


def test_phu_thuoc_trong_khuon():
    thieu = set()
    for b in kho_khuon.ds_khuon(True):
        van = " ".join([b.get("ke_hoach", "")] + list(b.get("bien_the_ke_hoach") or []))
        for w in re.findall(r"[A-Za-z][\w\-]+", van):
            w = w.lower()
            if len(w) >= 5 and w.isascii() and _HAU_TO.search(w) and w not in TEN_NHOM_KHONG_PHAI_THUOC:
                if ttt.hoat_chat(w) is None:
                    thieu.add(w)
    assert not thieu, sorted(thieu)


def test_json_hop_le():
    d = json.loads((GOC / "data" / "tri_thuc_thuoc.json").read_text(encoding="utf-8"))
    assert d["phien_ban"] and len(d["muc"]) >= 100
