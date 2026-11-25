# -*- coding: utf-8 -*-
"""Phep thu cho cac loi ra soat doc lap tim ra (25/11/2026), moi loi mot phep thu."""
from src import cong_rui_ro, khoa_bang_chung as kbc
from src.canh_bao import bo_sot, gop, lam_sang
from src.canh_bao.loai import CAN_XEM
from src.canh_bao.loi_noi import nhan_cau_hoi
from src.canh_bao.phat_hien import NguCanh
from src.duoc_ly_lam_sang import ClinicalPharmacovigilanceEngine as Dl
from src.guardrails import EvidenceIntegrityGuardrail as MedicalGuardrails
from src.phat_bieu import PhatBieu


def _doan(so, doan, vai="bệnh nhân"):
    return {"luot": so, "vai": vai, "doan": doan, "bat_dau": 0, "ket_thuc": len(doan)}


def _pb(id, nd, luot, **kw):
    return PhatBieu(id=id, nguoi_noi=kw.pop("nguoi_noi", "bệnh nhân"), chu_the_id=kw.pop("chu_the_id", 0),
                    noi_dung=nd, bang_chung=luot, **kw)


def _ma(cbs):
    return [c.ma for c in cbs]


# --- C1: di ung dang khac ("sốc phản vệ", "mẫn cảm") khong bi che boi mot di ung bat ky da ghi
def test_soc_phan_ve_khong_bi_che_boi_di_ung_khac():
    ps = [_pb(0, "dị ứng tôm", [1])]
    for doan in ("em bị sốc phản vệ với penicillin", "em mẫn cảm với aspirin", "uống amoxicillin là nổi mề đay"):
        assert "OMITTED_ALLERGY" in _ma(bo_sot.quet(NguCanh(""), ps, [_doan(2, doan)])), doan


# --- C2: "nhưng" tach ve; "khong di ung" chung khong che di ung khang dinh
def test_nhung_tach_ve_di_ung():
    ps = [_pb(0, "dị ứng", [1], phu_dinh=True)]
    cbs = bo_sot.quet(NguCanh(""), ps, [_doan(2, "em không bị dị ứng penicillin nhưng dị ứng aspirin")])
    assert "OMITTED_ALLERGY" in _ma(cbs)


# --- C3: van CO dau cau giu hanh vi cu (PLAN_AS_FACT)
def test_van_co_dau_giu_plan_as_fact():
    ht = "Bác sĩ: Bé bị viêm họng. Có gì bất thường thì tuần sau tái khám."
    ps = [_pb(0, "bé đã tái khám tuần sau", [1], nguoi_noi="bác sĩ")]
    kq = gop.chay(ps, ht)
    assert "PLAN_AS_FACT" in [c.ma for c in kq["theo_phat_bieu"][0]["tat_ca"]]


# --- I4: loi ke cua nguoi benh khong dau khong bi coi la cau hoi
def test_loi_ke_khong_phai_cau_hoi():
    for cau in ("mấy hôm nay cháu ho", "em chưa bao giờ dị ứng thuốc", "em có uống thuốc nhưng không đỡ",
                "ăn gì cũng nôn"):
        assert not nhan_cau_hoi(cau), cau


def test_luot_nguoi_benh_khong_dau_van_duoc_quet():
    ht = "Bác sĩ: chị kể đi\nBệnh nhân: em có uống thuốc nhưng không đỡ"
    ra = kbc.khoa_ca([], ht, bat_buoc_trich_dan=False)["doan_chua_ghi"]
    assert [d for d in ra if d["luot"] == 2]


# --- I5: di ung cua nguoi nha khong che di ung cua benh nhan; doan noi ve nguoi nha duoc ghi ro
def test_di_ung_cua_me_khong_che_cua_chau():
    ps = [_pb(0, "mẹ dị ứng penicillin", [1], chu_the_id=1, nguoi_noi="người nhà")]
    cbs = bo_sot.quet(NguCanh(""), ps, [_doan(2, "cháu cũng dị ứng penicillin", "người nhà")])
    assert "OMITTED_ALLERGY" in _ma(cbs)


def test_doan_ve_nguoi_nha_ghi_ro_chu_the():
    cbs = bo_sot.quet(NguCanh(""), [], [_doan(2, "mẹ em bị tiểu đường đang uống metformin", "người nhà")])
    thuoc = [c for c in cbs if c.ma == "OMITTED_MEDICATION"]
    assert thuoc and "có thể là của người nhà" in thuoc[0].ly_do


# --- I6: danh sach chat di ung khong thanh thuoc bi sot
def test_danh_sach_chat_di_ung_khong_thanh_thuoc():
    ps = [_pb(0, "dị ứng penicillin", [1])]
    for doan in ("dị ứng với penicillin và aspirin", "dị ứng penicillin còn amoxicillin thì không"):
        assert "OMITTED_MEDICATION" not in _ma(bo_sot.quet(NguCanh(""), ps, [_doan(2, doan)])), doan


# --- I7: Focus 3 qua ca doan_chua_ghi: thuc the moi trong doan thi doan la chua ghi
def test_focus_3_qua_doan_chua_ghi():
    ht = "Bác sĩ: Em có dị ứng gì không?\nBệnh nhân: Em không dị ứng thức ăn, dị ứng penicillin."
    ps = [_pb(0, "dị ứng thức ăn", [2], phu_dinh=True, trich_dan=["Em không dị ứng thức ăn"])]
    kk = kbc.khoa_ca(ps, ht, bat_buoc_trich_dan=False)
    assert any("penicillin" in d["doan"] for d in kk["doan_chua_ghi"])
    cbs = bo_sot.quet(NguCanh(ht), ps, kk["doan_chua_ghi"])
    assert "OMITTED_ALLERGY" in _ma(cbs)


# --- I8: tra lieu theo hoat chat, khong theo chuoi con; NTI khong mo rong sang biet duoc
def test_lieu_khong_khop_chuoi_con():
    for ten in ("kháng sinh", "men vi sinh", "kinh giới"):
        assert Dl.kiem_tra_lieu_tran(ten, 500) is None, ten
        assert MedicalGuardrails.kiem_tra_nguong_lieu_an_toan(ten, 500).hop_le, ten
    assert Dl.kiem_tra_lieu_tran("Panadol", 5000)
    assert not MedicalGuardrails.kiem_tra_nguong_lieu_an_toan("hapacol", 5000).hop_le


def test_nti_chi_them_acenocoumarol():
    cu = {"warfarin", "sintrom", "heparin", "enoxaparin", "digoxin", "theophylline", "aminophylline",
          "phenytoin", "carbamazepine", "valproat", "lithium", "insulin", "methotrexate", "cyclosporine",
          "tacrolimus", "amiodarone", "gentamicin", "vancomycin"}
    assert set(cong_rui_ro.THUOC_KHOANG_DIEU_TRI_HEP) - cu <= {"acenocoumarol"}
    assert cu <= set(cong_rui_ro.THUOC_KHOANG_DIEU_TRI_HEP)


# --- I9: chong chi dinh dua tren anh xa chua duyet -> CAN_XEM; chat di ung chi lay trong ve dau
def test_chong_chi_dinh_chua_duyet_can_xem():
    ht = "Bệnh nhân: Tôi dị ứng amoxicillin.\nBác sĩ: Tôi kê augmentin 625 mg ngày 2 lần."
    ps = [_pb(0, "dị ứng amoxicillin", [1]),
          _pb(1, "augmentin 625 mg ngày 2 lần", [2], nguoi_noi="bác sĩ", tinh_huong="kế hoạch",
              thuoc={"ten": "augmentin", "lieu": "625 mg", "so_lan": "ngày 2 lần"})]
    cbs = [c for c in lam_sang.quet(NguCanh(ht), ps) if c.ma == "CONTRAINDICATION"]
    assert cbs and all(c.ket_luan == CAN_XEM for c in cbs)


def test_chat_di_ung_chi_trong_ve_dau():
    ht = "Bệnh nhân: Dị ứng penicillin, đang dùng augmentin."
    ps = [_pb(0, "dị ứng penicillin, đang dùng augmentin", [1]),
          _pb(1, "augmentin", [1], thuoc={"ten": "augmentin"})]
    cbs = [c for c in lam_sang.quet(NguCanh(ht), ps) if c.ma == "CONTRAINDICATION"]
    assert not cbs  # penicillin khong phai thanh phan ghi trong ten augmentin; khong tu suy di ung cheo
