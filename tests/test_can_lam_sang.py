# -*- coding: utf-8 -*-
"""Kiểm thử unit test cho Module Đối soát Cận lâm sàng & Xét nghiệm."""

from src.can_lam_sang import ParaclinicalCorrelator


def test_bao_dong_do_nhoi_mau_co_tim():
    # Lâm sàng đau ngực + Troponin 0.18 + ECG ST chênh lên
    xet_nghiem = {
        "troponin": 0.18,
        "ecg": "ST chênh lên ở đạo trình DII, DIII, aVF",
        "wbc": 9.2
    }
    hoi_thoai = "Bệnh nhân: Tôi bị đau thắt ngực dữ dội như đá đè từ 2 tiếng trước, vã mồ hôi hột."

    kq = ParaclinicalCorrelator.phan_tich_xet_nghiem(xet_nghiem, hoi_thoai, chan_doan_so_bo="Theo dõi Hội chứng mạch vành cấp")

    assert kq.co_gia_tri_nguy_kich is True
    assert any("NHỒI MÁU CƠ TIM" in b for b in kq.bao_dong_do_khan_cap)
    assert any("Aspirin" in k for k in kq.khuyen_cao_dieu_tri)
    assert len(kq.chan_doan_duoc_xac_nhan) >= 1


def test_xac_nhan_viem_phoi_thong_qua_wbc_va_xquang():
    # Lâm sàng ho sốt + Bạch cầu 14.5 + X-quang đông đặc nhu mô
    xet_nghiem = {
        "wbc": 14.5,
        "xquang_phoi": "Đám mờ đông đặc thùy dưới phổi phải",
        "hb": 13.5
    }
    hoi_thoai = "Bệnh nhân: Tôi bị sốt 39 độ, ho có đờm vàng đục và đau tức ngực bên phải ba hôm nay."

    kq = ParaclinicalCorrelator.phan_tich_xet_nghiem(xet_nghiem, hoi_thoai, chan_doan_so_bo="Viêm phổi mắc phải cộng đồng")

    assert any("nhiễm trùng" in x.lower() or "viêm phổi" in x.lower() for x in kq.chan_doan_duoc_xac_nhan)
    assert any("x-quang" in x.lower() for x in kq.chan_doan_duoc_xac_nhan)


def test_canh_bao_kali_va_thieu_mau_nguy_kich():
    # K+ = 6.4 (tăng kali nguy kịch), Hb = 6.2 (thiếu máu nặng)
    xet_nghiem = {
        "k": 6.4,
        "hb": 6.2,
        "creatinine": 180,
        "egfr": 25
    }
    kq = ParaclinicalCorrelator.phan_tich_xet_nghiem(xet_nghiem)

    assert kq.co_gia_tri_nguy_kich is True
    assert any("Kali" in b for b in kq.bao_dong_do_khan_cap)
    assert any("Hemoglobin" in b for b in kq.bao_dong_do_khan_cap)
    assert any("truyền máu" in k.lower() for k in kq.khuyen_cao_dieu_tri)
    assert any("calci" in k.lower() or "glucose" in k.lower() for k in kq.khuyen_cao_dieu_tri)


def test_phat_hien_bat_tuong_dong_wbc_tang_khong_sot():
    # WBC tăng 16.0 nhưng không có triệu chứng viêm trong hội thoại
    xet_nghiem = {"wbc": 16.0}
    hoi_thoai = "Bệnh nhân: Tôi đi kiểm tra sức khỏe tổng quát, người hoàn toàn bình thường không sốt không ho."

    kq = ParaclinicalCorrelator.phan_tich_xet_nghiem(xet_nghiem, hoi_thoai)

    assert len(kq.canh_bao_bat_tuong_dong) >= 1
    assert any("tiềm ẩn" in c.lower() for c in kq.canh_bao_bat_tuong_dong)
