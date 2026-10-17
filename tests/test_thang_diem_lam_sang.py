# -*- coding: utf-8 -*-
"""Kiểm thử unit test cho Động cơ Tính Thang điểm Nguy cơ Lâm sàng Quốc tế."""

from src.thang_diem_lam_sang import ClinicalRiskScoringEngine


def test_tinh_curb65_nguy_co_cao():
    # Bệnh nhân 72 tuổi (>=65), có lú lẫn, nhịp thở 32 l/p, huyết áp 85/50 -> 4 điểm (CAO)
    kq = ClinicalRiskScoringEngine.tinh_curb65(
        tuoi=72,
        y_thuc_lu_lan=True,
        urea_mmol_l=8.5,
        nhip_tho=32,
        huyet_ap_tam_thu=85,
        huyet_ap_tam_truong=50
    )
    assert kq.diem_so >= 4
    assert kq.phan_tang_nguy_co == "CAO"
    assert "ICU" in kq.khuyen_cao_lam_sang or "nhập viện" in kq.khuyen_cao_lam_sang


def test_tinh_curb65_nguy_co_thap():
    # Bệnh nhân 35 tuổi, tỉnh táo, thở 18 l/p, HA 120/80, urea bình thường -> 0 điểm (THAP)
    kq = ClinicalRiskScoringEngine.tinh_curb65(
        tuoi=35,
        y_thuc_lu_lan=False,
        urea_mmol_l=4.2,
        nhip_tho=18,
        huyet_ap_tam_thu=120,
        huyet_ap_tam_truong=80
    )
    assert kq.diem_so == 0
    assert kq.phan_tang_nguy_co == "THAP"
    assert "ngoại trú" in kq.khuyen_cao_lam_sang


def test_tinh_cha2ds2_vasc_rung_nhi():
    # Nữ 76 tuổi (+2 tuổi, +1 nữ), tiền sử THA (+1) và Tăng huyết áp, ĐTĐ (+1) -> 5 điểm (CAO)
    kq = ClinicalRiskScoringEngine.tinh_cha2ds2_vasc(
        tuoi=76,
        gioi_tinh="nữ",
        tien_su_tang_huyet_ap=True,
        tien_su_dai_thao_duong=True
    )
    assert kq.diem_so == 5
    assert kq.phan_tang_nguy_co == "CAO"
    assert "chống đông" in kq.khuyen_cao_lam_sang


def test_tinh_wells_pe():
    # Nghi thuyên tắc phổi (+3), nhịp tim nhanh 115 (+1.5), bất động sau mổ (+1.5) -> 6.0 điểm (CAO)
    kq = ClinicalRiskScoringEngine.tinh_wells_pe(
        pe_la_chan_doan_hang_dau=True,
        nhip_tim_tren_100=True,
        bat_dong_hoac_phau_thuat_gan_day=True
    )
    assert kq.diem_so >= 5
    assert kq.phan_tang_nguy_co == "CAO"
    assert "CTPA" in kq.khuyen_cao_lam_sang


def test_tinh_glasgow_blatchford():
    # Xuất huyết tiêu hóa: Urea 12 mmol/L (+4), Hb 9.5 g/dL (+6 nam), đi cầu phân đen (+1), HA tụt 95 (+2) -> 13 điểm (CAO)
    kq = ClinicalRiskScoringEngine.tinh_glasgow_blatchford(
        urea_mmol_l=12.0,
        hb_g_dl=9.5,
        gioi_tinh="nam",
        huyet_ap_tam_thu=95,
        di_ngoai_phan_den=True
    )
    assert kq.diem_so >= 10
    assert kq.phan_tang_nguy_co == "CAO"
    assert "nội soi" in kq.khuyen_cao_lam_sang


def test_tinh_gcs_hon_me_nang():
    # Hôn mê nặng: Mắt 1, Lời nói 2, Vận động 3 -> GCS = 6 điểm (NGUY_KICH, đặt nội khí quản)
    kq = ClinicalRiskScoringEngine.tinh_gcs(mat=1, loi_noi=2, van_dong=3)
    assert kq.diem_so == 6
    assert kq.phan_tang_nguy_co == "NGUY_KICH"
    assert "NỘI KHÍ QUẢN" in kq.khuyen_cao_lam_sang


def test_tinh_gcs_tinh_tao():
    # Tỉnh táo: 4-5-6 -> GCS = 15 điểm (THAP)
    kq = ClinicalRiskScoringEngine.tinh_gcs(mat=4, loi_noi=5, van_dong=6)
    assert kq.diem_so == 15
    assert kq.phan_tang_nguy_co == "THAP"


def test_tinh_qsofa_soc_nhiem_khuan():
    # Thở 26 l/p, HA 85 mmHg, tri giác thay đổi -> qSOFA = 3 điểm (NGUY_KICH)
    kq = ClinicalRiskScoringEngine.tinh_qsofa(nhip_tho=26, huyet_ap_tam_thu=85, y_thuc_thay_doi=True)
    assert kq.diem_so == 3
    assert kq.phan_tang_nguy_co == "NGUY_KICH"
    assert "SỐC NHIỄM KHUẨN" in kq.khuyen_cao_lam_sang


def test_tinh_nyha_suy_tim():
    # Khó thở khi nằm, ngồi thở -> NYHA Độ 4
    kq4 = ClinicalRiskScoringEngine.tinh_nyha(kho_tho_khi_nghi=True)
    assert kq4.diem_so == 4
    assert kq4.phan_tang_nguy_co == "NGUY_KICH"

    # Hạn chế gắng sức nặng -> NYHA Độ 2
    kq2 = ClinicalRiskScoringEngine.tinh_nyha(kho_tho_khi_gang_suc_nang=True)
    assert kq2.diem_so == 2
    assert kq2.phan_tang_nguy_co == "TRUNG_BINH"


def test_tinh_child_pugh_xo_gan():
    # Bilirubin 60 (>50: +3), Albumin 25 (<28: +3), INR 2.5 (>2.3: +3), Cổ trướng nhiều (+3), Não gan độ 3 (+3) -> 15d (Class C)
    kq = ClinicalRiskScoringEngine.tinh_child_pugh(
        bilirubin_umol_l=60.0,
        albumin_g_l=25.0,
        inr=2.5,
        co_truong="NHIEU",
        benh_nao_gan="DO_3"
    )
    assert kq.diem_so == 15
    assert "Class C" in kq.ten_thang_diem
    assert kq.phan_tang_nguy_co == "CAO"


def test_tinh_bmi_chau_a():
    # 75 kg, 165 cm -> BMI = 27.5 (Béo phì độ I theo chuẩn WPRO)
    kq = ClinicalRiskScoringEngine.tinh_bmi(can_nang_kg=75.0, chieu_cao_cm=165.0)
    assert kq.diem_so == 27
    assert "BÉO PHÌ ĐỘ I" in kq.ten_thang_diem
    assert kq.phan_tang_nguy_co == "CAO"
