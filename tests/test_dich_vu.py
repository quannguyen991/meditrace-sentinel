# -*- coding: utf-8 -*-
"""Dich vu HTTP cho giao dien.

VI SAO CAN TEST. Giao dien la thu ban nguoi danh gia nhin thay. Hai dieu de sai ma khong ai
biet: (1) dich vu lang le goi mo hinh khac voi ban bao cao, (2) mot ban ghi CU duoc tra
ve ma khong co nhan, nguoi xem tuong may vua chay. Hai dieu do duoc canh o day.
"""
import json

import pytest

from src import dich_vu


@pytest.fixture(scope="module")
def loi():
    return dich_vu.Loi(cho_nap_mo_hinh=False)


def _mot_ca_co_dem(loi):
    loi.dem
    if not loi._dem_theo_chu:
        pytest.skip("may nay khong co tep dem khau trich")
    return next(iter(loi._dem_theo_chu))


def test_mo_hinh_mac_dinh_la_4b_khong_phai_8b():
    """Adapter khau trich cua du an huan luyen tren Qwen3-4B. Nap 8B la do sai mo hinh."""
    assert dich_vu.Loi().ten_mo_hinh == "Qwen/Qwen3-4B"


def test_tat_mo_hinh_thi_bao_loi_ro_chu_khong_im_lang(loi):
    with pytest.raises(dich_vu.LoiDichVu) as e:
        loi.ho_so("ca_la", "Bác sĩ: xin chào\nBệnh nhân: chào bác sĩ", "C_khoa")
    assert e.value.code == 503 and e.value.ma == "mo_hinh_bi_tat"


def test_nhanh_ngoai_danh_sach_bi_tu_choi(loi):
    with pytest.raises(dich_vu.LoiDichVu) as e:
        loi.ho_so("x", "Bác sĩ: a", "A+")
    assert e.value.ma == "nhanh_khong_hop_le"


def test_chay_lai_tu_bo_dem_co_nhan_nguon_va_du_menh_de(loi):
    """Loi thoai co trong tep dem: dung lai duoc trong vai giay, KHONG can mo hinh."""
    chu = _mot_ca_co_dem(loi)
    r = loi.ho_so("bat_ky", chu, "C_khoa")
    assert r["nguon"] == "bo_dem"           # khong duoc ghi la "mo_hinh"
    assert r["id"] != "bat_ky"              # lay dung ma ca cua ban dem
    assert r["so_phat_bieu"] > 0 and r["du_doan"].strip()
    assert all("id" in g and "muc" in g for g in r["ghi_chu"])


def test_tra_theo_chu_bo_qua_khac_biet_khoang_trang(loi):
    chu = _mot_ca_co_dem(loi)
    assert loi.dem_theo_chu(chu.replace("\n", "\n ")) is not None
    assert loi.dem_theo_chu("Bác sĩ: câu này không có trong bộ đệm") is None


def test_ca_mau_co_nhan_bo_va_dem_menh_de():
    if not dich_vu.THU_MUC_CHAY_TRUOC.exists():
        pytest.skip("chua co thu muc ket qua chay truoc")
    ds = dich_vu.ca_mau()
    assert ds and all({"id", "bo", "so_menh_de"} <= set(x) for x in ds)
    assert all("C_khoa_hoi" not in x["bo"] for x in ds)


def test_ca_mau_nhanh_hoi_giu_nguyen_phat_bieu_them_cau_hoi():
    if not dich_vu.THU_MUC_CHAY_TRUOC.exists():
        pytest.skip("chua co thu muc ket qua chay truoc")
    ds = dich_vu.ca_mau()
    co_hoi = 0
    for x in ds[:40]:
        a = dich_vu.doc_ca(x["id"])
        b = dich_vu.doc_ca(x["id"], "C_khoa_hoi")
        assert a["phat_bieu"] == b["phat_bieu"]
        assert b["nhanh"] == "C_khoa_hoi"
        co_hoi += bool(b.get("cau_hoi"))
    assert co_hoi > 0


def test_ca_mau_khong_co_thi_bao_404():
    with pytest.raises(dich_vu.LoiDichVu) as e:
        dich_vu.doc_ca("khong_ton_tai_999")
    assert e.value.code == 404


def test_doan_chep_ra_json_giu_du_truong_nguon_asr():
    t = {"segment_id": "seg_001", "text_original": "ho ba hôm", "speaker_role": "unknown",
         "asr_provider": "phowhisper", "asr_model": "vinai/PhoWhisper-small", "thua": 1}
    ra = dich_vu._doan_ra_json(t)
    assert ra["asr_provider"] == "phowhisper" and ra["speaker_role"] == "unknown"
    assert "thua" not in ra                 # chi tra cac truong da khai bao


def test_loi_dich_vu_ra_json_duoc():
    e = dich_vu.LoiDichVu("ma", "thông điệp", 409)
    assert json.dumps({"loi": e.ma, "thong_diep": e.thong_diep}, ensure_ascii=False)
