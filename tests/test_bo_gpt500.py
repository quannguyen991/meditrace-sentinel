# -*- coding: utf-8 -*-
"""Bo 500 GPT: chuyen doi dung, cham dung — va CHI de do (xem test_chan_du_lieu_gpt)."""
import pytest

from src import bo_gpt500 as g
from src import thuc_the


@pytest.fixture(scope="module")
def ds():
    if not g.NGUON.exists():
        pytest.skip("can data/ngoai/phuong_ngu_500.jsonl (khong co trong ban ma nguon day len GitHub)")
    return [g.chuyen(b) for b in g.nap(g.NGUON)]


def test_chuyen_du_500_ca_id_khong_trung_moi_ca_4_luot_vai_hop_le(ds):
    assert len(ds) == 500 and len({d["id"] for d in ds}) == 500
    for d in ds:
        luot = thuc_the.tach_luot(d["input"])
        assert len(luot) == 4
        assert all(vai in ("bác sĩ", "bệnh nhân", "người nhà", "điều dưỡng")
                   for _s, vai, _v in luot), d["input"]


def test_MOI_khuon_deu_co_trong_bang_benh_nhan(ds):
    assert {d["scenario_id"] for d in ds} == set(g.BENH_NHAN)
    assert g.BENH_NHAN_MO_HO <= set(g.BENH_NHAN)


def test_ME_la_nguoi_nha_o_khuon_di_ung_nhung_la_benh_nhan_o_khuon_nguoi_cao_tuoi(ds):
    a = next(d for d in ds if d["scenario_id"] == "allergy_relative")
    b = next(d for d in ds if d["scenario_id"] == "daughter_elderly_dizzy")
    assert a["benh_nhan"] == "trẻ" and b["benh_nhan"] == "mẹ"


def _hoan_hao(ca):
    """Du doan HOAN HAO dung tu dap an."""
    ps = []
    for k, c in enumerate(ca["gold_claims"]):
        lop = g.ANH_XA[c["status"]]
        p = {"id": k, "noi_dung": c["concept"], "moc_thoi_gian": c["time"],
             "chu_the_id": 0 if c["subject"] == ca["benh_nhan"] else 1}
        if lop == g.PHU_DINH:
            p["phu_dinh"] = True
        elif lop in (g.CHUA_GHI_NHAN, g.NGHI_NGO):
            p["do_chac_chan"] = lop
        elif lop == g.KHONG_LA_SU_THAT:
            p["tinh_huong"] = "giả định"
        ps.append(p)
    return ps


def test_du_doan_HOAN_HAO_thi_dung_het_va_khong_ro_ri(ds):
    b = g.tong_hop(ds, {ca["id"]: (_hoan_hao(ca), set()) for ca in ds})["bang"]
    assert b["tim_thay"]["trung_binh"] == 1.0
    assert b["dung_chu_the"]["trung_binh"] == 1.0
    assert b["dung_lop"]["trung_binh"] == 1.0
    assert b["ro_ri"]["trung_binh"] == 0.0
    assert b["nguoi_khac_thanh_benh_nhan"]["trung_binh"] == 0.0


def test_di_ung_cua_ME_ghi_thanh_cua_TRE_bi_bat(ds):
    ca = next(d for d in ds if d["scenario_id"] == "allergy_relative")
    ps = _hoan_hao(ca)
    for p, c in zip(ps, ca["gold_claims"]):
        if c["subject"] == "mẹ":
            p["chu_the_id"] = 0
    assert any(k.get("nguoi_khac_thanh_benh_nhan") for k in g.cham_ca(ca, ps))


def test_cau_hoi_CHUA_TRA_LOI_ghi_thanh_phu_dinh_la_RO_RI_tru_khi_bi_khoa_chan(ds):
    ca = next(d for d in ds if d["scenario_id"] == "unanswered_question")
    ps = _hoan_hao(ca)
    moc = set()
    for p, c in zip(ps, ca["gold_claims"]):
        if g.ANH_XA[c["status"]] == g.KHONG_LA_SU_THAT:
            p.pop("tinh_huong", None)
            p["phu_dinh"] = True
            moc.add(p["id"])
    assert any(k.get("ro_ri") for k in g.cham_ca(ca, ps))
    assert not any(k.get("ro_ri") for k in g.cham_ca(ca, ps, bi_chan=moc))


def test_ca_KHONG_co_du_doan_tinh_la_khong_tim_thay_chu_khong_bo_di(ds):
    tk = g.tong_hop(ds[:50], {})
    assert tk["bang"]["tim_thay"]["trung_binh"] == 0.0
    assert tk["so_ca"] == 50 and tk["so_ca_co_du_doan"] == 0
