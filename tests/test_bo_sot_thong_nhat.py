# -*- coding: utf-8 -*-
"""Mot bo bo sot duy nhat (src/canh_bao/bo_sot.py), thay hai bo cu chay song song."""
from src import khoa_bang_chung
from src.canh_bao import bo_sot
from src.canh_bao.phat_hien import NguCanh
from src.kiem_duyet_bhyt_va_bo_sot import ActiveOmissionRecoveryEngine
from src.phat_bieu import PhatBieu

HT = ("Bác sĩ: Chị có dị ứng gì không?\n"
      "Bệnh nhân: Em không dị ứng thức ăn.\n"
      "Bác sĩ: Còn thuốc thì sao?\n"
      "Bệnh nhân: Em dị ứng penicillin, đang uống warfarin mỗi tối.")


def _doan(so, doan, vai="bệnh nhân"):
    return {"luot": so, "vai": vai, "doan": doan, "bat_dau": 0, "ket_thuc": len(doan)}


def _ma(cbs, luot=None):
    return {c.ma for c in cbs if luot is None or luot in c.luot}


def test_khong_di_ung_thuc_an_khong_che_di_ung_thuoc():
    ps = [PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng thức ăn",
                   phu_dinh=True, bang_chung=[2])]
    cbs = bo_sot.quet(NguCanh(HT), ps, [_doan(4, "Em dị ứng penicillin")])
    assert "OMITTED_ALLERGY" in _ma(cbs)


def test_di_ung_khang_dinh_cung_chat_thi_im():
    ps = [PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng penicillin",
                   phu_dinh=False, bang_chung=[2])]
    cbs = bo_sot.quet(NguCanh(HT), ps, [_doan(4, "Em dị ứng penicillin")])
    assert "OMITTED_ALLERGY" not in _ma(cbs)


def test_di_ung_khang_dinh_khac_chat_van_bao():
    ps = [PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng tôm",
                   phu_dinh=False, bang_chung=[2])]
    cbs = bo_sot.quet(NguCanh(HT), ps, [_doan(4, "Em dị ứng penicillin")])
    assert "OMITTED_ALLERGY" in _ma(cbs)


def test_mot_doan_nhieu_loai():
    cbs = bo_sot.quet(NguCanh(HT), [], [_doan(4, "Em dị ứng penicillin, đang uống warfarin mỗi tối")])
    assert {"OMITTED_ALLERGY", "OMITTED_MEDICATION"} <= _ma(cbs)


def test_thuoc_da_ghi_thi_im():
    ps = [PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="warfarin", bang_chung=[3],
                   thuoc={"ten": "warfarin"})]
    cbs = bo_sot.quet(NguCanh(HT), ps, [_doan(4, "đang uống warfarin mỗi tối")])
    assert "OMITTED_MEDICATION" not in _ma(cbs)


def test_doan_khong_loai_nao_la_chung_chung():
    cbs = bo_sot.quet(NguCanh(HT), [], [_doan(4, "nhà em ở gần chợ")])
    assert _ma(cbs) == {"POSSIBLE_IMPORTANT_OMISSION"}


def test_hai_dau_ra_cung_ket_qua():
    ps = [PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng thức ăn",
                   phu_dinh=True, bang_chung=[2], trich_dan=["Em không dị ứng thức ăn"])]
    kk = khoa_bang_chung.khoa_ca(ps, HT, bat_buoc_trich_dan=False)
    luot_dong_co = {x.luot for x in ActiveOmissionRecoveryEngine.quet_khoi_phuc(ps, HT, kk)}
    luot_bo_sot = {s for c in bo_sot.quet(NguCanh(HT), ps, kk["doan_chua_ghi"]) for s in c.luot}
    assert luot_dong_co and luot_dong_co <= luot_bo_sot
    loai = {x.loai_thong_tin for x in ActiveOmissionRecoveryEngine.quet_khoi_phuc(ps, HT, kk)}
    assert {"di_ung", "thuoc"} <= loai
