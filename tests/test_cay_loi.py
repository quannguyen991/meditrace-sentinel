# -*- coding: utf-8 -*-
"""Bo cay loi (plan 2026-11-25-cay-loi-do-canh-bao, Task 2)."""
import random

import pytest

from src.do_luong.danh_gia_khoa import phat_bieu_tu_dap_an
from tools import cay_loi

HOI = "\n".join([
    "Bác sĩ: Chào chị, chị khó chịu ở đâu?",                     # 1
    "Bệnh nhân: Tôi sốt 39 độ ba ngày nay rồi bác sĩ ạ.",          # 2
    "Bác sĩ: Chị có ho không?",                                    # 3
    "Bệnh nhân: Dạ không ho ạ.",                                   # 4
    "Bác sĩ: Chị có dị ứng thuốc gì không?",                       # 5
    "Bệnh nhân: Tôi dị ứng penicillin ạ.",                         # 6
    "Bác sĩ: Chị đang uống thuốc gì?",                             # 7
    "Bệnh nhân: Tôi uống amlodipin 5 mg mỗi sáng.",                # 8
    "Bệnh nhân: À không, ba ngày chứ không phải hai ngày.",        # 9
    "Bác sĩ: Nếu còn sốt thì chị quay lại nhé, có thể là sốt virus.",  # 10
])


def _d(noi_dung, luot, trich, **kw):
    d = dict(chu_the="bệnh nhân", noi_dung=noi_dung, muc="BỆNH SỬ HIỆN TẠI", moc_thoi_gian=None,
             phu_dinh=False, tinh_huong="thực tế", luot=luot, thoi_gian_su_kien="hiện tại", quan_he=None,
             quan_he_voi=None, trang_thai="còn hiệu lực", do_chac_chan="chắc chắn", hanh_vi="trả lời",
             thuoc=None, trich_dan=trich)
    d.update(kw)
    return d


CA = {"id": "ca_thu", "input": HOI, "dap_an": [
    _d("sốt 39 độ", [2, 9], ["Tôi sốt 39 độ ba ngày nay rồi"], moc_thoi_gian="ba ngày nay"),
    _d("sốt 39 độ", [2], ["Tôi sốt 39 độ ba ngày nay rồi"], moc_thoi_gian="hai ngày", trang_thai="bị thay thế"),
    _d("không ho", [3, 4], ["Dạ không ho ạ"], phu_dinh=True),
    _d("dị ứng penicillin", [5, 6], ["Tôi dị ứng penicillin ạ"], muc="DỊ ỨNG"),
    _d("đang dùng amlodipin 5 mg mỗi sáng", [8], ["Tôi uống amlodipin 5 mg mỗi sáng"], muc="THUỐC ĐANG DÙNG",
       thuoc={"ten": "amlodipin", "lieu": "5 mg", "so_lan": "mỗi sáng", "duong_dung": "uống", "bat_dau": None,
              "ngung": None, "trang_thai_dung": "đang dùng"}),
    _d("sốt virus", [10], ["có thể là sốt virus"], muc="CHẨN ĐOÁN", do_chac_chan="nghi ngờ",
       chu_the="bệnh nhân"),
    _d("quay lại khám nếu còn sốt", [10], ["Nếu còn sốt thì chị quay lại nhé"], muc="KẾ HOẠCH ĐIỀU TRỊ",
       tinh_huong="giả định"),
]}


def _ps():
    return phat_bieu_tu_dap_an(CA)


def _cay(loai, hat=1):
    return cay_loi.cay(_ps(), CA, loai, random.Random(hat))


def _theo_id(ps):
    return {p.id: p for p in ps}


def test_danh_muc_du_16_loai_va_co_nhom_dung():
    assert len(cay_loi.LOAI_CAY) == 16
    assert set(cay_loi.NHOM_DUNG) == set(cay_loi.LOAI_CAY)
    assert cay_loi.NHOM_DUNG["xoa_di_ung"] == {"OMISSION"}


@pytest.mark.parametrize("loai", cay_loi.LOAI_CAY)
def test_khong_sua_ban_goc_va_cung_hat_cung_ket_qua(loai):
    ps = _ps()
    truoc = [p.to_dict() for p in ps]
    a = cay_loi.cay(ps, CA, loai, random.Random(7))
    b = cay_loi.cay(_ps(), CA, loai, random.Random(7))
    assert [p.to_dict() for p in ps] == truoc
    assert a is not None, loai
    assert [p.to_dict() for p in a[0]] == [p.to_dict() for p in b[0]]
    assert a[1] == b[1] and a[1].loai == loai


def test_doi_chu_the():
    moi, c = _cay("doi_chu_the")
    goc = _theo_id(_ps())[c.phat_bieu_id]
    assert _theo_id(moi)[c.phat_bieu_id].chu_the_id != goc.chu_the_id


def test_dao_phu_dinh_doi_phu_dinh_co_hieu_luc():
    from src.do_luong.cham_he_thong import _phu_dinh_that
    for hat in range(20):
        moi, c = _cay("dao_phu_dinh", hat)
        p, goc = _theo_id(moi)[c.phat_bieu_id], _theo_id(_ps())[c.phat_bieu_id]
        assert _phu_dinh_that(p.to_dict()) != _phu_dinh_that(goc.to_dict())
        assert p.noi_dung == goc.noi_dung


def test_nang_chac_chan_va_gia_dinh_thanh_that():
    moi, c = _cay("nang_chac_chan")
    assert _theo_id(moi)[c.phat_bieu_id].do_chac_chan == "chắc chắn" and c.phat_bieu_id == 5
    moi, c = _cay("gia_dinh_thanh_that")
    assert _theo_id(moi)[c.phat_bieu_id].tinh_huong == "thực tế" and c.phat_bieu_id == 6


def test_ban_cu_con_hieu_luc():
    moi, c = _cay("ban_cu_con_hieu_luc")
    assert c.phat_bieu_id == 1 and _theo_id(moi)[1].trang_thai == "còn hiệu lực"


def test_doi_lieu_nhan_10_ca_noi_dung_lan_thuoc():
    moi, c = _cay("doi_lieu")
    p = _theo_id(moi)[4]
    assert c.phat_bieu_id == 4 and "50 mg" in p.noi_dung and p.thuoc["lieu"] == "50 mg"
    assert p.trich_dan == ["Tôi uống amlodipin 5 mg mỗi sáng"]


def test_doi_so_cong_2_khong_dung_lieu():
    moi, c = _cay("doi_so")
    p = _theo_id(moi)[c.phat_bieu_id]
    assert c.phat_bieu_id in (0,) and "41 độ" in p.noi_dung


def test_doi_thuoc_sang_hoat_chat_khac():
    gap = set()
    for hat in range(12):
        moi, c = _cay("doi_thuoc", hat)
        p, goc = _theo_id(moi)[c.phat_bieu_id], _theo_id(_ps())[c.phat_bieu_id]
        gap.add(c.phat_bieu_id)
        cu = "amlodipin" if c.phat_bieu_id == 4 else "penicillin"
        assert cu not in p.noi_dung and p.noi_dung != goc.noi_dung
        if goc.thuoc:
            assert p.thuoc["ten"] != cu and p.thuoc["ten"] in p.noi_dung
    assert gap == {3, 4}


def test_doi_thoi_gian():
    moi, c = _cay("doi_thoi_gian")
    p = _theo_id(moi)[c.phat_bieu_id]
    assert p.moc_thoi_gian and p.moc_thoi_gian != _theo_id(_ps())[c.phat_bieu_id].moc_thoi_gian


def test_bia_menh_de_thuoc_khong_co_trong_hoi_thoai():
    for hat in range(10):
        moi, c = _cay("bia_menh_de", hat)
        cu = {p.id for p in _ps()}
        assert c.phat_bieu_id not in cu and len(moi) == len(cu) + 1
        p = _theo_id(moi)[c.phat_bieu_id]
        ten = p.noi_dung.split()[-1]
        assert ten.lower() not in HOI.lower()
        assert p.chu_the_id == 0 and list(c.luot) == p.bang_chung


def test_bia_trich_dan_va_doi_bang_chung():
    moi, c = _cay("bia_trich_dan")
    p = _theo_id(moi)[c.phat_bieu_id]
    assert p.trich_dan[0] not in HOI
    moi, c = _cay("doi_bang_chung")
    p, goc = _theo_id(moi)[c.phat_bieu_id], _theo_id(_ps())[c.phat_bieu_id]
    assert not set(p.bang_chung) & set(goc.bang_chung)
    assert all(HOI.split("\n")[s - 1].startswith("Bác sĩ") for s in p.bang_chung)


@pytest.mark.parametrize("loai,id_", [("xoa_di_ung", 3), ("xoa_thuoc", 4), ("xoa_phu_dinh", 2), ("xoa_so_lieu", None)])
def test_xoa_tra_id_va_luot(loai, id_):
    moi, c = _cay(loai)
    goc = _theo_id(_ps())
    assert c.phat_bieu_id not in _theo_id(moi) and len(moi) == len(goc) - 1
    if id_ is not None:
        assert c.phat_bieu_id == id_
    assert list(c.luot) == goc[c.phat_bieu_id].bang_chung


def test_khong_ap_dung_tra_none():
    ca = dict(CA, dap_an=[CA["dap_an"][2]])
    assert cay_loi.cay(phat_bieu_tu_dap_an(ca), ca, "xoa_thuoc", random.Random(0)) is None
    assert cay_loi.cay(phat_bieu_tu_dap_an(ca), ca, "ban_cu_con_hieu_luc", random.Random(0)) is None


def test_tap_dieu_chinh_khop_tep_id():
    ds = cay_loi.tap_dieu_chinh()
    assert len(ds) == 400 and ds[0]["id"] == "v2mr_0003"
