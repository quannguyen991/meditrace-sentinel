# -*- coding: utf-8 -*-
"""Tu phuong ngu trong loi thoai, nghia chuan trong dap an.

VI SAO CO TEP NAY (10/09/2026).

Bo sinh truoc do co ba vung nhung khac nhau chi o TIEU TU ("a", "nghen", "hi").
Tu vung giong het nhau: moi vung deu noi "sot", "met". Nguoi that khong noi
vay — o mien Nam mot nguoi me se noi "chau nong ham hap".

Day la mot dang cua chinh van de du an di do, o tang tu vung: he thong phai
hieu "nong ham hap" va "sot" la MOT THU.

HAI RANG BUOC PHAI GIU, va ca hai deu de vi pham im lang:
  1. chi thay trong loi BENH NHAN / NGUOI NHA, khong thay loi BAC SI
  2. DAP AN giu nghia chuan — neu dap an cung doi theo thi khong con phep thu

TRU cum KHONG dong nghia (`pn.GIU_NGUYEN`, 24/09/2026): "nong ham hap" chua
phai "sot" khi chua do nhiet do — chinh `chuan_hoa` ghi vay tu 11/09 — nen dap
an ghi dung loi nguoi noi. Doan tren tung lay "nong ham hap / sot" lam vi du cho
"MOT THU"; vi du do sai.
"""
import random

import pytest

from src import phuong_ngu as pn
from src import sinh_hoi_thoai_viet as sh


def _rng():
    return random.Random(0)


# ------------------------------------------------------------- tu dien

def test_nap_duoc_tu_dien():
    if not pn.TEP_TU_DIEN.exists():
        pytest.skip("can data/ngoai/tu_dien_phuong_ngu.csv (khong co trong ban ma nguon day len GitHub)")
    td = pn.nap()
    assert td["trung"] and td["nam"]
    assert all(len(x) == 2 for cac in td.values() for x in cac)


def test_khong_co_tep_thi_tra_rong_khong_nem_loi():
    """Bo sinh phai chay duoc ca khi chua co tu dien."""
    td = pn.nap("khong/co/tep/nao.csv")
    assert td == {"trung": [], "nam": []}


def test_bang_quy_chuan_co_ca_hai_chieu_nguon():
    if not pn.TEP_TU_DIEN.exists():
        pytest.skip("can data/ngoai/tu_dien_phuong_ngu.csv (khong co trong ban ma nguon day len GitHub)")
    b = pn.bang_quy_chuan()
    assert b["nóng hầm hập"] == "sốt"
    assert b["lừ đừ"] == "mệt"
    assert b["nỏ"] == "không"


# ---------------------------------------------------------- phep thay tu

def test_thay_duoc_tu_o_giua_cau():
    cau, doi = pn.doi_sang_phuong_ngu("Cháu sốt hai ngày.", "nam", _rng(), 1.0)
    assert "nóng hầm hập" in cau
    assert ("sốt", "nóng hầm hập") in doi


def test_thay_duoc_tu_o_DAU_CAU_va_giu_chu_hoa():
    """Ban dau khop phan biet hoa thuong, nen moi tu dung o DAU CAU deu khong
    bao gio duoc doi — dung nhung cho de nhin nhat."""
    cau, _ = pn.doi_sang_phuong_ngu("Hôm kia cháu mệt.", "trung", _rng(), 1.0)
    assert cau.startswith("Hôm tê"), cau


@pytest.mark.parametrize("cau", ["Cháu mệt mỏi lắm.", "Cháu sốt cao ba ngày.",
                                 "Trẻ sốt xuất huyết.", "Bệnh nhân ngất xỉu."])
def test_khong_pha_TU_GHEP(cau):
    """Ranh gioi TU khong phai ranh gioi TU GHEP.

    "met" trong "met moi" dung la mot tu tach bang dau cach, nhung thay rieng
    no ra "lu du moi" thi khong phai tieng Viet. Loi nay lam hong du lieu ma
    nhin bang so khong thay.
    """
    moi, doi = pn.doi_sang_phuong_ngu(cau, "nam", _rng(), 1.0)
    assert moi == cau, f"da pha tu ghep: {moi}"
    assert doi == []


def test_van_thay_khi_tu_dung_MOT_MINH():
    """Doi chung cho test tren: chan tu ghep khong duoc chan luon ca truong
    hop dung."""
    moi, doi = pn.doi_sang_phuong_ngu("Cháu sốt ba ngày.", "nam", _rng(), 1.0)
    assert "nóng hầm hập" in moi


def test_hai_tu_da_bo_duoc_ghi_lai_ly_do():
    """Bo mot tu khoi bang thay ma khong ghi ly do thi nguoi sau se them lai."""
    assert "không" in pn.DA_BO and "làm" in pn.DA_BO
    tu_thay = {c for cac in pn.THAY_DUOC.values() for c, _d in cac}
    assert not (set(pn.DA_BO) & tu_thay), "tu da bo ma van nam trong bang thay"


def test_mien_bac_khong_doi_gi():
    cau = "Cháu sốt hai ngày."
    moi, doi = pn.doi_sang_phuong_ngu(cau, "bac", _rng(), 1.0)
    assert moi == cau and doi == []


def test_ty_le_0_thi_khong_doi_gi():
    cau = "Cháu sốt hai ngày."
    moi, _ = pn.doi_sang_phuong_ngu(cau, "nam", _rng(), 0.0)
    assert moi == cau


# ------------------------------------------- rang buoc trong bo sinh

@pytest.fixture(scope="module")
def bo():
    return sh.sinh_bo(300, seed=42)


def test_co_ca_mang_tu_phuong_ngu(bo):
    """Tu 11/09/2026 chi khuon DANH GIA mang tu phuong ngu — bang thay lay tu tu
    dien do GPT sinh (`sinh_hoi_thoai_viet.PHUONG_NGU_TRONG_TRAIN`). Nen ty le do
    tren khuon ngoai train, va khuon train phai la 0."""
    tap = sh.bang_tap_khuon()
    danh_gia = [c for c in bo if tap[c["benh"]] != "train"]
    co = [c for c in danh_gia if c["tu_phuong_ngu"]]
    assert co, "khong ca nao co tu phuong ngu"
    assert len(co) / len(danh_gia) > 0.05
    assert not any(c["tu_phuong_ngu"] for c in bo if tap[c["benh"]] == "train")


def test_LOI_BAC_SI_khong_bao_gio_co_tu_phuong_ngu(bo):
    """Bac si duoc dao tao noi chuan. Tron lai thi mat mot dau hieu that."""
    tu = {d for cac in pn.THAY_DUOC.values() for _c, d in cac}
    for c in bo:
        for dong in c["input"].split("\n"):
            if not dong.startswith("Bác sĩ:"):
                continue
            for t in tu:
                assert t not in dong.lower(), f"{c['id']}: bac si noi {t!r}"


def test_DAP_AN_giu_nghia_chuan(bo):
    """Neu dap an cung doi sang phuong ngu thi khong con phep thu nao ca. Tru cum
    khong dong nghia — `test_GIU_NGUYEN_*` ben duoi."""
    tu = {d for cac in pn.THAY_DUOC.values() for _c, d in cac} - pn.GIU_NGUYEN
    for c in bo:
        for m in c["dap_an"]:
            noi = str(m["noi_dung"]).lower()
            for t in tu:
                assert t not in noi, f"{c['id']}: dap an chua tu phuong ngu {t!r}"


# ------------------------------------ cum khong dong nghia (24/09/2026)

def test_giu_nguyen_khop_chuan_hoa():
    """GIU_NGUYEN phai la DUNG cac cum trong bang thay ma `chuan_hoa` xep CAN HOI.

    Loi da xay ra: tu 11/09 `chuan_hoa` ghi "nong ham hap" la can hoi ("nguoi noi
    chua do nhiet do — khong tu doi thanh sot"), trong khi bo sinh van ghi dap an
    "sot, chac chan". Hai bang lech nhau ma khong gi bao, va phep cham tinh dau ra
    chep nguyen van la sai. Them mot cum can hoi vao THAY_DUOC ma quen GIU_NGUYEN
    (hay nguoc lai) thi test nay do."""
    from src import chuan_hoa as ch
    for cac in pn.THAY_DUOC.values():
        for _chuan, dia_phuong in cac:
            muc = {c.muc_tin for c in ch.phan_tich(dia_phuong)}
            assert muc, f"{dia_phuong!r} khong co trong chuan_hoa"
            can_hoi = ch.CAN_HOI in muc
            assert can_hoi == (dia_phuong in pn.GIU_NGUYEN), dia_phuong


@pytest.mark.parametrize("noi_dung, trich, mong", [
    ("sốt", ["Nóng hầm hập ba hôm rồi ạ"], "nóng hầm hập"),
    ("Sốt", ["Tôi nóng hầm hập"], "Nóng hầm hập"),
    # bac si goi ten "sot", nguoi benh xac nhan: "sot" co can cu nguyen van
    ("sốt", ["Cháu có sốt không?", "Dạ, nóng hầm hập luôn"], "sốt"),
    # "sot cao" bi CHAN_SAU giu lai trong loi thoai
    ("sốt cao", ["Sốt cao lắm, nóng hầm hập"], "sốt cao"),
    ("ho", ["Nóng hầm hập, ho nhiều"], "ho"),
    ("sốt", ["Đau đầu"], "sốt"),
])
def test_giu_loi_nguoi_noi(noi_dung, trich, mong):
    assert pn.giu_loi_nguoi_noi(noi_dung, trich) == mong


def test_ve_tu_chuan_la_nguoc_cua_giu_loi():
    assert pn.ve_tu_chuan("nóng hầm hập") == "sốt"
    assert pn.ve_tu_chuan("lừ đừ") == "lừ đừ"      # khong thuoc GIU_NGUYEN


def test_GIU_NGUYEN_chi_khi_trich_dan_khong_con_tu_chuan(bo):
    """Hai chieu: (1) menh de ghi "nong ham hap" thi khong trich dan nao con chu
    "sot"; (2) khong con menh de "sot" nao ma can cu duy nhat la "nong ham hap"
    — dung loi da sua. Va phai co it nhat mot menh de di qua duong nay, khong thi
    test (1) dung vi khong co gi de xet."""
    import re
    sot = re.compile(r"(?<!\w)sốt(?!\w)", re.I)
    nhh = re.compile(r"(?<!\w)nóng hầm hập(?!\w)", re.I)
    so_giu = 0
    for c in bo:
        for m in c["dap_an"]:
            trich = m["trich_dan"]
            if nhh.search(m["noi_dung"]):
                so_giu += 1
                assert not any(sot.search(t) for t in trich), c["id"]
                assert any(nhh.search(t) for t in trich), c["id"]
            if sot.search(m["noi_dung"]):
                assert (any(sot.search(t) for t in trich)
                        or not any(nhh.search(t) for t in trich)), \
                    f"{c['id']}: dap an 'sot' ma trich dan chi co 'nong ham hap'"
    assert so_giu > 0


def test_ca_mien_bac_khong_co_tu_phuong_ngu(bo):
    for c in bo:
        if c.get("mien") == "bac":
            assert not c["tu_phuong_ngu"]


def test_benh_an_tham_chieu_khong_co_tu_phuong_ngu(bo):
    """Benh an la van ban chuyen mon, viet bang tu chuan. Tru cum khong dong nghia
    (`pn.GIU_NGUYEN`): doi thanh "sot" la ghi mot dieu nguoi noi chua noi."""
    tu = {d for cac in pn.THAY_DUOC.values() for _c, d in cac} - pn.GIU_NGUYEN
    for c in bo:
        for t in tu:
            assert t not in c["output"].lower(), f"{c['id']}: benh an co {t!r}"
