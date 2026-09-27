# -*- coding: utf-8 -*-
"""Cham he thong. Trich HOAN HAO (dap an bo tu sinh, khuon train) cho qua DUNG
duong ong (`nhanh.chay_trung_gian`) thi gan nhu khong loi — moi loi con lai la
loi cua duong ong, khong phai cua mo hinh. Cay loi co chu dinh thi phai dem ra."""
import json
import random

import pytest

from src import cham_he_thong as ch
from src import du_lieu_trich, nhanh, thach_thuc
from src import sinh_hoi_thoai_viet as sh


def _chay(cases, sua=None, ten="C_khoa_hoi"):
    kq_tho = []
    for ca in cases:
        _ds, js = du_lieu_trich.doi_mot_ca(ca)
        ps = json.loads(js)["phat_bieu"]
        if sua:
            sua(ca, ps)
        kq_tho.append({"id": ca["id"], "phat_bieu": ps})
    return {r["id"]: r for r in
            nhanh.chay_trung_gian(cases, None, None, None, ten, kq_tho=kq_tho)}


@pytest.fixture(scope="module")
def bo():
    return [sh.sinh_mot_ca(f"c{i:03d}", random.Random(4200 + i),
                           sh.TuyChon(chi_tap="train")) for i in range(60)]


def test_trich_HOAN_HAO_qua_duong_ong_thi_gan_nhu_khong_loi(bo):
    b = ch.tong_hop(bo, _chay(bo))["bang"]
    for ten in ("sai_chu_the", "sai_muc", "ban_cu", "khong_can_cu"):
        assert b[ten]["gia_tri"] <= 0.01, (ten, b[ten])
    # Chinh sach cach C (22/09/2026): di ung / thuoc CO CANH BAO sang CAN XAC NHAN, ke
    # ca khi dung. Do tren 60 ca nay: bo sot trong than tu <= 3% len 4,9% — do la GIA
    # cua chinh sach, da bao cao, khong phai loi. Nguong 6% de van bat duoc hoi quy.
    assert b["bo_sot"]["gia_tri"] <= 0.06, b["bo_sot"]


def test_cay_DOI_CHU_THE_thi_danh_dau_bat_hon_ngau_nhien(bo):
    def sua(ca, ps):
        for p in ps:
            if p["chu_the"] != "bệnh nhân":
                p["chu_the"] = "bệnh nhân"
                return
    t = ch.tong_hop(bo, _chay(bo, sua))["tong"]
    assert t["dd_loi"] >= 5, t
    assert t["dd_trung"] > t["dd_ngau_nhien"], t


def test_thieu_ket_qua_cho_mot_ca_thi_DUNG_HAN(bo):
    with pytest.raises(SystemExit):
        ch.tong_hop(bo[:3], {})


def test_dong_TRUNG_LAP_tach_khoi_khong_can_cu():
    ca = {"id": "x", "dap_an": [{"chu_the": "bệnh nhân", "noi_dung": "sốt cao",
                                 "luot": [2], "muc": "BỆNH SỬ HIỆN TẠI"}]}
    ps = [{"id": 0, "noi_dung": "sốt cao", "chu_the_id": 0, "bang_chung": [2]},
          {"id": 1, "noi_dung": "sốt cao", "chu_the_id": 0, "bang_chung": [2]},
          {"id": 2, "noi_dung": "đau bụng", "chu_the_id": 0, "bang_chung": [2]}]
    loi, bo_sot = ch.loi_phat_bieu(ca, ps)
    assert loi[0][0] == [] and loi[1][0] == ["trung_lap"], loi
    assert loi[2][0] == ["khong_can_cu"] and not bo_sot


def test_ban_CU_cua_he_thong_ghep_ban_cu_cua_dap_an_du_khong_duoc_xet():
    """Ban cu nam o CAN XAC NHAN (ngoai phan xet), ban moi o than: ban moi phai
    ghep ban moi cua dap an — truoc 11/09/2026 no ghep nham ban cu (loi gia)."""
    ca = {"id": "x", "dap_an": [
        {"chu_the": "bệnh nhân", "noi_dung": "sụt cân", "luot": [3],
         "muc": "BỆNH SỬ HIỆN TẠI", "trang_thai": "bị thay thế"},
        {"chu_the": "bệnh nhân", "noi_dung": "sụt cân", "luot": [5],
         "muc": "BỆNH SỬ HIỆN TẠI", "quan_he": "đính chính", "quan_he_voi": 0}]}
    ps = [{"id": 0, "noi_dung": "sụt cân", "chu_the_id": 0, "bang_chung": [3],
           "trang_thai": "bị thay thế"},
          {"id": 1, "noi_dung": "sụt cân", "chu_the_id": 0, "bang_chung": [5]}]
    loi, bo_sot = ch.loi_phat_bieu(ca, ps, xet={1})
    assert loi == {1: ([], "khac")} and not bo_sot, (loi, bo_sot)


def test_ghep_dung_BAN_theo_moc_thoi_gian():
    da = [{"noi_dung": "sốt", "moc_thoi_gian": "bốn ngày"},
          {"noi_dung": "sốt", "moc_thoi_gian": "hai ngày"}]
    ps = [{"id": 7, "noi_dung": "sốt", "moc_thoi_gian": "hai ngày"},
          {"id": 8, "noi_dung": "sốt", "moc_thoi_gian": "bốn ngày"}]
    assert ch.ghep_menh_de(da, ps) == {0: 1, 1: 0}


def test_thach_thuc_DOI_CHU_THE_trich_hoan_hao_dung_ca_cap():
    ds = thach_thuc.cap_doi_chu_the("train", 4, seed=3)
    tt = ch.cham_thach_thuc(ds, _chay(ds))
    assert tt["so_cap"] == 4 and tt["dung_ca_cap"] == 4, tt


def test_thach_thuc_DINH_CHINH_trich_hoan_hao_dung_trang_thai_cuoi():
    ds = thach_thuc.bo_dinh_chinh("train", 10, seed=3)
    tt = ch.cham_thach_thuc(ds, _chay(ds))
    assert tt["dung"] == tt["so_ca"] == 10, tt


def test_thach_thuc_PHUONG_NGU_trich_hoan_hao_thi_hai_ban_giong_het():
    """Khuon phat trien: khuon train khong con tu phuong ngu nao (11/09/2026)."""
    ds = thach_thuc.cap_phuong_ngu("phat_trien", 2, seed=3)
    tt = ch.cham_thach_thuc(ds, _chay(ds))
    assert tt["giong_het"] == tt["so_cap"] == 2, tt


# ------------------------------------------------ DUNG NGUOI, khong chi "benh nhan hay khong"
def _d(chu_the):
    return {"chu_the": chu_the, "noi_dung": "dị ứng nọc ong"}


def _p(chu_the_id, ten):
    return {"chu_the_id": chu_the_id, "ten_chu_the": ten}


def test_ghi_bo_thanh_ba_ngoai_la_SAI_NGUOI():
    """Ca that the he 6: dung muc tien su gia dinh, sai nguoi. Ban cu cham DUNG."""
    assert not ch.dung_nguoi(_d("bố"), _p(3, "bà ngoại"))


def test_dung_quan_he_la_dung_nguoi():
    assert ch.dung_nguoi(_d("bố"), _p(3, "bố"))
    assert ch.dung_nguoi(_d("bà ngoại"), _p(2, "bà ngoại của bé"))


def test_dap_an_nguoi_nha_thi_ghi_dich_danh_la_BIA():
    assert not ch.dung_nguoi(_d("người nhà"), _p(3, "bố"))
    assert ch.dung_nguoi(_d("người nhà"), _p(3, "người nhà"))
    assert ch.dung_nguoi(_d("người nhà"), _p(3, "tôi"))


def test_benh_nhan_van_chi_kiem_id():
    assert ch.dung_nguoi(_d("bệnh nhân"), _p(0, "bé"))
    assert not ch.dung_nguoi(_d("bệnh nhân"), _p(3, "bé"))
    assert not ch.dung_nguoi(_d("bố"), _p(0, "bố"))
