# -*- coding: utf-8 -*-
"""Canh bao lam sang (lieu, tuong tac, chong chi dinh) di qua lop canh bao, co ma, co muc tin
cay — thay cho he song song `lam_sang_nang_cao` khong ma, khong muc tin cay."""
from src import tri_thuc_thuoc
from src.canh_bao import gop, lam_sang
from src.canh_bao.loai import CAN_XEM, LOAI, NHOM, THU_NGHIEM
from src.canh_bao.phat_hien import NguCanh
from src.phat_bieu import PhatBieu

HT = ("Bác sĩ: Anh đang dùng thuốc gì?\n"
      "Bệnh nhân: Tôi uống paracetamol 1000 mg ngày 6 lần, với lại đang uống warfarin.\n"
      "Bác sĩ: Tôi kê thêm aspirin 81 mg mỗi sáng.")


def _ps():
    return [
        PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="paracetamol 1000 mg ngày 6 lần",
                 bang_chung=[2], trich_dan=["Tôi uống paracetamol 1000 mg ngày 6 lần"],
                 thuoc={"ten": "paracetamol", "lieu": "1000 mg", "so_lan": "ngày 6 lần"}),
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="warfarin", bang_chung=[2],
                 trich_dan=["đang uống warfarin"], thuoc={"ten": "warfarin"}),
        PhatBieu(id=2, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="aspirin 81 mg mỗi sáng", bang_chung=[3],
                 trich_dan=["Tôi kê thêm aspirin 81 mg mỗi sáng"], tinh_huong="kế hoạch",
                 thuoc={"ten": "aspirin", "lieu": "81 mg", "so_lan": "mỗi sáng"}),
    ]


def _tat_ca(kq):
    return [c for v in kq["theo_phat_bieu"].values() for c in v["tat_ca"]] + list(kq["toan_ca"])


def test_ma_moi_thu_nghiem_nhom_moi():
    assert "CLINICAL_KNOWLEDGE" in NHOM
    for ma in ("DOSE_OVER_MAX", "DRUG_INTERACTION", "CONTRAINDICATION"):
        assert LOAI[ma].nhom == "CLINICAL_KNOWLEDGE" and LOAI[ma].tin_cay == THU_NGHIEM


def test_lieu_vuot_qua_thanh_canh_bao():
    cbs = [c for c in _tat_ca(gop.chay(_ps(), HT)) if c.ma == "DOSE_OVER_MAX"]
    assert len(cbs) == 1 and cbs[0].phat_bieu_id == 0
    assert cbs[0].anh_huong_trang_thai is False
    assert "6000" in cbs[0].ly_do and "4000" in cbs[0].ly_do


def test_muc_chua_duyet_chi_can_xem():
    assert tri_thuc_thuoc.lieu_toi_da("paracetamol", "nguoi_lon").da_duyet is False
    cbs = [c for c in lam_sang.quet(NguCanh(HT), _ps()) if c.ma == "DOSE_OVER_MAX"]
    assert cbs and all(c.ket_luan == CAN_XEM for c in cbs)


def test_lieu_trong_nguong_thi_im():
    ps = [PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="paracetamol 500 mg ngày 3 lần",
                   bang_chung=[2], thuoc={"ten": "paracetamol", "lieu": "500 mg", "so_lan": "ngày 3 lần"})]
    assert not [c for c in lam_sang.quet(NguCanh(HT), ps) if c.ma == "DOSE_OVER_MAX"]


def test_lieu_gam_va_so_lan_dang_khac():
    assert lam_sang.lieu_ngay_mg({"lieu": "1g", "so_lan": "4 lần/ngày"}, "") == 4000.0
    assert lam_sang.lieu_ngay_mg({"lieu": "500mg", "so_lan": "mỗi 4 giờ"}, "") == 3000.0
    assert lam_sang.lieu_ngay_mg({"lieu": "hai nhát", "so_lan": "khi cần"}, "") is None


def test_tuong_tac_warfarin_aspirin():
    cbs = [c for c in lam_sang.quet(NguCanh(HT), _ps()) if c.ma == "DRUG_INTERACTION"]
    assert cbs and cbs[0].ket_luan == CAN_XEM
    assert "warfarin" in cbs[0].ly_do and "aspirin" in cbs[0].ly_do


def test_chong_chi_dinh_ke_thuoc_dang_di_ung():
    ht = "Bệnh nhân: Tôi dị ứng amoxicillin.\nBác sĩ: Tôi kê augmentin 625 mg ngày 2 lần."
    ps = [PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng amoxicillin", bang_chung=[1]),
          PhatBieu(id=1, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="augmentin 625 mg ngày 2 lần", bang_chung=[2],
                   tinh_huong="kế hoạch", thuoc={"ten": "augmentin", "lieu": "625 mg", "so_lan": "ngày 2 lần"})]
    cbs = [c for c in lam_sang.quet(NguCanh(ht), ps) if c.ma == "CONTRAINDICATION"]
    assert cbs and cbs[0].phat_bieu_id == 1


def test_khong_di_ung_thi_khong_chong_chi_dinh():
    ht = "Bệnh nhân: Tôi không dị ứng amoxicillin.\nBác sĩ: Tôi kê amoxicillin 500 mg ngày 3 lần."
    ps = [PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng amoxicillin", phu_dinh=True,
                   bang_chung=[1]),
          PhatBieu(id=1, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="amoxicillin 500 mg ngày 3 lần", bang_chung=[2],
                   tinh_huong="kế hoạch", thuoc={"ten": "amoxicillin", "lieu": "500 mg", "so_lan": "ngày 3 lần"})]
    assert not [c for c in lam_sang.quet(NguCanh(ht), ps) if c.ma == "CONTRAINDICATION"]
