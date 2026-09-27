# -*- coding: utf-8 -*-
"""Dinh tuyen muc (`sinh_benh_an._muc_cho`): hanh vi, dong tu dung thuoc trong
trich dan, sinh hieu phai kem so. Hieu chinh tren dap an khuon TRAIN."""
import random

import pytest

from src import sinh_benh_an as sba
from src import sinh_hoi_thoai_viet as sh
from src.danh_gia_khoa import phat_bieu_tu_dap_an, vao_than


def _muc(**kw):
    p = {"id": 0, "chu_the_id": 0, "bang_chung": [2], "trang_thai": "còn hiệu lực",
         "tinh_huong": "thực tế", "noi_dung": "sốt", "nguoi_noi": "người nhà"}
    p.update(kw)
    return sba._muc_cho(p, 0)[0]


def test_TEN_THUOC_tran_vao_THUOC_DANG_DUNG_nho_dong_tu_trong_trich_dan():
    """Dap an ghi noi dung la TEN THUOC; bang tra tren noi dung khong bat duoc."""
    assert _muc(noi_dung="salbutamol",
                trich_dan=["tôi có uống salbutamol"]) == "THUỐC ĐANG DÙNG"
    assert _muc(noi_dung="salbutamol") == "BỆNH SỬ HIỆN TẠI", "khong trich dan: luat cu"


def test_uong_SUA_khong_phai_thuoc():
    assert _muc(noi_dung="bú kém",
                trich_dan=["cháu có uống sữa nhưng ít"]) != "THUỐC ĐANG DÙNG"


def test_TANG_HUYET_AP_la_tien_su_khong_phai_sinh_hieu():
    assert _muc(noi_dung="tăng huyết áp", thoi_gian_su_kien="quá khứ") == "TIỀN SỬ BỆNH"
    assert _muc(noi_dung="huyết áp 150/90") == "SINH HIỆU"


def test_bac_si_NHAC_LAI_benh_su_theo_hanh_vi():
    """Cau bac si noi nhung la loi nhac lai benh su -> benh su, khong phai chan
    doan. Khong co hanh_vi (dau ra the he 4) thi giu luat cu."""
    kw = dict(nguoi_noi="bác sĩ", noi_dung="sốt ba ngày")
    assert _muc(**kw) == "CHẨN ĐOÁN"
    assert _muc(hanh_vi="trả lời", **kw) == "BỆNH SỬ HIỆN TẠI"


def test_QUAN_SAT_cua_NGUOI_NHA_khong_thanh_kham_lam_sang():
    """Nguoi nha khong kham: hanh vi "quan sat" chi tin khi nguoi noi la nhan vien."""
    assert _muc(hanh_vi="quan sát", noi_dung="nổi ban đỏ") != "KHÁM LÂM SÀNG"
    assert _muc(hanh_vi="quan sát", nguoi_noi="bác sĩ",
                noi_dung="họng đỏ") == "KHÁM LÂM SÀNG"


def test_hanh_vi_KE_HOACH_vao_ke_hoach_ke_ca_khi_tinh_huong_ghi_thuc_te():
    assert _muc(hanh_vi="kế hoạch", nguoi_noi="bác sĩ",
                noi_dung="uống nhiều nước") == "KẾ HOẠCH ĐIỀU TRỊ"


def test_NHAN_DINH_cua_bac_si_vao_chan_doan():
    assert _muc(hanh_vi="nhận định", nguoi_noi="bác sĩ",
                noi_dung="viêm họng cấp") == "CHẨN ĐOÁN"


def test_chu_the_KHAC_benh_nhan_THANG_hanh_vi():
    """Luat 1 dung truoc moi thu: di ung cua me khong vao DI UNG, du hanh vi la gi."""
    assert _muc(chu_the_id=1, hanh_vi="trả lời",
                noi_dung="dị ứng penicillin") == sba.MUC_NGUOI_KHAC


@pytest.fixture(scope="module")
def bo_train():
    return [sh.sinh_mot_ca(f"t{i:03d}", random.Random(9000 + i),
                           sh.TuyChon(chi_tap="train")) for i in range(300)]


def test_tren_dap_an_TRAIN_dinh_tuyen_dung_it_nhat_99_phan_tram(bo_train):
    """Truoc 11/09/2026: 95,4% tren tap train — 1.195 phat bieu thuoc roi xuong
    benh su, 80 "tang huyet ap" roi vao sinh hieu."""
    dung = tong = 0
    for ca in bo_train:
        for p in phat_bieu_tu_dap_an(ca):
            g = ca["dap_an"][p.id]["muc"]
            if g == "LÝ DO KHÁM BỆNH" or not vao_than(p):
                continue
            tong += 1
            dung += sba._muc_cho(p.to_dict(), 0)[0] == g
    assert dung / tong >= 0.99, f"{dung}/{tong}"


def test_cau_hoi_lam_ro_la_PHAN_PHU_ke_ca_khi_khong_co_muc_can_xac_nhan():
    van = ("BỆNH SỬ HIỆN TẠI\n\nSốt.\n\n" + sba.MUC_HOI_LAI +
           "\n\n1. Sốt từ khi nào ạ?")
    than, phu = sba.tach_muc_phu(van)
    assert sba.MUC_HOI_LAI not in than and sba.MUC_HOI_LAI in phu
