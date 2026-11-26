# -*- coding: utf-8 -*-
"""Kiểm thử Động cơ Phân tích Quỹ đạo Lâm sàng Dọc (`src/quy_dao_lam_sang.py`)
và tích hợp vào `src/dieu_phoi_ha_tang.py`."""
from src.dieu_phoi_ha_tang import MediTracePipelineOrchestrator
from src.phat_bieu import PhatBieu
from src.quy_dao_lam_sang import phan_tich_quy_dao_lam_sang


def test_quy_dao_rong_hoac_thieu_du_lieu_khong_bao_gia():
    kq = phan_tich_quy_dao_lam_sang([], {})
    assert set(kq.keys()) == {"kdigo_aki", "xu_huong_xn", "canh_bao_thuoc_doc", "tom_tat_nguy_co"}
    assert kq["kdigo_aki"] is None
    assert kq["xu_huong_xn"] == []
    assert kq["canh_bao_thuoc_doc"] == []
    assert "Không phát hiện" in kq["tom_tat_nguy_co"]

    # Có creatinine nhưng lần khám cũ thiếu mốc thời gian -> không suy diễn KDIGO AKI
    kq_no_ts = phan_tich_quy_dao_lam_sang(
        [{"xet_nghiem": {"creatinine": 0.9}}],
        {"ngay_kham": "2026-11-26T10:00:00", "xet_nghiem": {"creatinine": 1.6}},
    )
    assert kq_no_ts["kdigo_aki"] is None


def test_kdigo_aki_stage_1_48h_va_don_vi_umol_mg():
    # Tăng +0.3 mg/dL trong 36h -> Stage 1
    kq_mg = phan_tich_quy_dao_lam_sang(
        [{"ngay_kham": "2026-11-25T00:00:00", "xet_nghiem": {"creatinine_mg_dl": 1.0}}],
        {"ngay_kham": "2026-11-26T12:00:00", "xet_nghiem": {"creatinine_mg_dl": 1.3}},
    )
    assert kq_mg["kdigo_aki"] is not None
    assert kq_mg["kdigo_aki"]["giai_doan"] == 1

    # Tăng +30 umol/L (>= 26.5 umol/L) trong 24h theo gio_truoc -> Stage 1
    kq_umol = phan_tich_quy_dao_lam_sang(
        [{"gio_truoc": 24, "xet_nghiem": {"creatinine": 80, "creatinine_unit": "umol/L"}}],
        {"xet_nghiem": {"creatinine": 110, "creatinine_unit": "umol/L"}},
    )
    assert kq_umol["kdigo_aki"] is not None
    assert kq_umol["kdigo_aki"]["giai_doan"] == 1


def test_kdigo_aki_stage_2_va_stage_3():
    # 2.2x trong 5 ngày -> Stage 2
    kq_s2 = phan_tich_quy_dao_lam_sang(
        [{"ngay_truoc": 5, "xet_nghiem": {"creatinine": 1.0}}],
        {"xet_nghiem": {"creatinine": 2.2}},
    )
    assert kq_s2["kdigo_aki"]["giai_doan"] == 2
    assert kq_s2["kdigo_aki"]["muc_do"] == "CAO"

    # 3.1x trong 6 ngày (dùng umol/L) -> Stage 3
    kq_s3 = phan_tich_quy_dao_lam_sang(
        [{"ngay_kham": "2026-11-20", "xet_nghiem": {"creatinine": 90}}],
        {"ngay_kham": "2026-11-26", "xet_nghiem": {"creatinine": 285}},
    )
    assert kq_s3["kdigo_aki"]["giai_doan"] == 3
    assert kq_s3["kdigo_aki"]["muc_do"] == "NGUY_KICH"

    # SCr >= 4.0 mg/dL (4.2) với mức tăng cấp >= 0.3 mg/dL (từ 3.5 -> 4.2, tỉ lệ chỉ 1.2x) -> Stage 3
    kq_s3_abs = phan_tich_quy_dao_lam_sang(
        [{"gio_truoc": 36, "xet_nghiem": {"creatinine_mg_dl": 3.5}}],
        {"xet_nghiem": {"creatinine_mg_dl": 4.2}},
    )
    assert kq_s3_abs["kdigo_aki"]["giai_doan"] == 3


def test_xu_huong_xn_egfr_hba1c_inr_hb_kali_men_gan():
    lich_su = [
        {
            "ngay_kham": "2026-08-01",
            "xet_nghiem": {
                "creatinine_mg_dl": 1.0,
                "hba1c": 6.8,
                "inr": 2.3,
                "hb": 13.0,
                "k": 4.1,
                "ast": 32,
                "alt": 28,
            },
        }
    ]
    hien_tai = {
        "ngay_kham": "2026-11-26",
        "tuoi": 65,
        "gioi_tinh": "nam",
        "xet_nghiem": {
            "creatinine_mg_dl": 2.1,
            "hba1c": 8.4,
            "inr": 4.2,
            "hb": 9.8,
            "k": 5.6,
            "ast": 240,
            "alt": 210,
        },
        "danh_sach_thuoc": ["warfarin", "atorvastatin", "metformin"],
    }
    kq = phan_tich_quy_dao_lam_sang(lich_su, hien_tai)
    chi_so_phat_hien = {x["chi_so"] for x in kq["xu_huong_xn"]}
    assert {"eGFR", "HbA1c", "INR", "Hb", "Kali (K+)", "AST", "ALT"} <= chi_so_phat_hien

    loai_cb = {c["loai_canh_bao"] for c in kq["canh_bao_thuoc_doc"]}
    assert "NEPHROTOXIC_AKI_CASCADE" in loai_cb
    assert "HEPATOTOXIC_CASCADE" in loai_cb
    assert "ANTICOAGULANT_BLEEDING_CASCADE" in loai_cb


def test_triple_whammy_xuyen_lan_kham():
    lich_su = [
        {"ngay_truoc": 14, "danh_sach_thuoc": ["enalapril 10 mg"]},
        {"ngay_truoc": 7, "danh_sach_thuoc": ["furosemide 40 mg"]},
    ]
    hien_tai = {
        "danh_sach_thuoc": ["ibuprofen 400 mg"],
    }
    kq = phan_tich_quy_dao_lam_sang(lich_su, hien_tai)
    loai_cb = {c["loai_canh_bao"] for c in kq["canh_bao_thuoc_doc"]}
    assert "TRIPLE_WHAMMY" in loai_cb
    tw = [c for c in kq["canh_bao_thuoc_doc"] if c["loai_canh_bao"] == "TRIPLE_WHAMMY"][0]
    assert tw["muc_do"] == "NGUY_KICH"


def test_tich_hop_dieu_phoi_ha_tang_quy_dao_lam_sang():
    ht = "Bệnh nhân: Tôi đang uống metformin và ibuprofen.\nBác sĩ: Kiểm tra lại thận."
    ps = [
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="uống metformin", bang_chung=[1], thuoc={"ten": "metformin"}),
        PhatBieu(id=2, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="uống ibuprofen", bang_chung=[1], thuoc={"ten": "ibuprofen"}),
    ]
    kq = MediTracePipelineOrchestrator.xu_ly_ca_kham(
        ma_ca="ca_quy_dao_01",
        hoi_thoai=ht,
        danh_sach_phat_bieu=ps,
        thong_tin_benh_nhan={"tuoi": 68, "gioi_tinh": "nam"},
        du_lieu_xet_nghiem={"creatinine_mg_dl": 2.4},
        lich_su_lan_kham=[
            {"gio_truoc": 36, "xet_nghiem": {"creatinine_mg_dl": 1.0}, "danh_sach_thuoc": ["enalapril", "hydrochlorothiazide"]},
        ],
    )
    assert kq.quy_dao_lam_sang is not None
    assert kq.quy_dao_lam_sang["kdigo_aki"]["giai_doan"] == 2
    assert len(kq.audit_trail.cac_chot_kiem_soat) == 8
    assert kq.audit_trail.an_toan_lam_sang is False
