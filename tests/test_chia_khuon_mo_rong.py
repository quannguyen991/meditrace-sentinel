# -*- coding: utf-8 -*-
"""Kiem thu chia tap khuon mo rong doc lap (Task F2)."""
from src.bo_du_lieu import ngu_lieu_viet as nl
from src.bo_du_lieu import sinh_hoi_thoai_viet as sh
from src.bo_du_lieu import chia_tap_theo_khuon as tt
from src.bo_du_lieu import khuon_mo_rong as kmr


def _goc():
    return [b["ten"] for b in getattr(nl, "BENH_GOC", nl.BENH[:200])]


def test_200_khuon_cu_khong_doi_khi_them_50():
    """200 khuon cu phai giu dung tap tuyet doi khi them 50 khuon moi."""
    goc = _goc()
    t0 = {t: k for k, v in tt.phan_khuon(goc).items() for t in v}
    tat = goc + [b["ten"] for b in kmr.DOT[1]]
    t1 = {t: k for k, v in tt.phan_khuon(tat).items() for t in v}
    doi = sorted(t for t in goc if t0[t] != t1[t])
    assert not doi, f"{len(doi)} khuon cu bi doi tap: {doi}"


def test_dot_mo_rong_chia_doc_lap():
    """200 khuon dot 1 (Lo 1-4) phai duoc chia doc lap theo ty le 80/10/10."""
    goc = _goc()
    tat = goc + [b["ten"] for b in kmr.DOT[1]]
    p = tt.phan_khuon(tat)
    moi_ten = set(b["ten"] for b in kmr.DOT[1])

    moi_tr = p["train"] & moi_ten
    moi_pt = p["phat_trien"] & moi_ten
    moi_kt = p["kiem_tra_cuoi"] & moi_ten

    assert len(moi_tr) + len(moi_pt) + len(moi_kt) == len(kmr.DOT[1])
    # Voi 200 khuon: 10% moi tap dev/test = 20 khuon, train = 160 khuon
    assert len(moi_pt) == round(len(kmr.DOT[1]) * 0.1)
    assert len(moi_kt) == round(len(kmr.DOT[1]) * 0.1)
    assert len(moi_tr) == len(kmr.DOT[1]) - len(moi_pt) - len(moi_kt)


def test_khong_khuon_nao_o_hai_tap():
    tat = _goc() + [b["ten"] for b in kmr.DOT[1]]
    p = tt.phan_khuon(tat)
    assert not (p["train"] & p["phat_trien"])
    assert not (p["train"] & p["kiem_tra_cuoi"])
    assert not (p["phat_trien"] & p["kiem_tra_cuoi"])


def test_bang_tap_khuon_mo_rong_giu_200_cu():
    goc = _goc()
    b0 = sh.bang_tap_khuon(mo_rong=False)
    b1 = sh.bang_tap_khuon(mo_rong=True)
    doi = sorted(t for t in goc if b0[t] != b1[t])
    assert not doi, f"Khuon cu doi tap o bang_tap_khuon(mo_rong=True): {doi}"
    for b in kmr.BENH_MO_RONG:
        assert b["ten"] in b1, f"Khuon moi '{b['ten']}' khong co trong bang_tap_khuon"


def test_toan_bo_600_khuon_chia_hai_dot_doc_lap_va_khong_doi_200_cu():
    """Dot 1 (Lo 1-4) va Dot 2 (Lo 5-8) moi dot chia doc lap 160/20/20; 200 khuon cu khong doi tap."""
    goc = _goc()
    t0 = {t: k for k, v in tt.phan_khuon(goc).items() for t in v}
    tat = goc + [b["ten"] for b in kmr.BENH_MO_RONG]
    assert len(set(tat)) == 600
    p = tt.phan_khuon(tat)
    assert not (p["train"] & p["phat_trien"])
    assert not (p["train"] & p["kiem_tra_cuoi"])
    assert not (p["phat_trien"] & p["kiem_tra_cuoi"])
    assert len(p["train"] | p["phat_trien"] | p["kiem_tra_cuoi"]) == 600
    t1 = {t: k for k, v in p.items() for t in v}
    assert not [t for t in goc if t0[t] != t1[t]], "Khuon cu doi tap"
    for dot_id in (1, 2):
        ten = set(b["ten"] for b in kmr.DOT[dot_id])
        assert len(p["train"] & ten) == 160
        assert len(p["phat_trien"] & ten) == 20
        assert len(p["kiem_tra_cuoi"] & ten) == 20
