# -*- coding: utf-8 -*-
"""Test suite cho Trụ cột 4: Hạ tầng Điều phối Luồng Toàn diện trong tests/test_dieu_phoi_ha_tang.py."""
import pytest
from src.dieu_phoi_ha_tang import MediTracePipelineOrchestrator
from src.phat_bieu import PhatBieu


def test_dieu_phoi_luong_toan_dien_end_to_end():
    hoi_thoai = (
        "Bác sĩ: Chào bác, hôm nay bác đi khám vì sao ạ?\n"
        "Bệnh nhân: Dạ, tôi bị ho có đờm và sốt nhẹ ba hôm nay.\n"
        "Bác sĩ: Bác có tiền sử dị ứng thuốc gì không?\n"
        "Bệnh nhân: Tôi bị dị ứng kháng sinh penicillin uống vào là nổi mề đay.\n"
        "Bác sĩ: Hiện tại bác có đang uống thuốc gì ở nhà không?\n"
        "Bệnh nhân: Tôi đang uống viên amlodipin 5 mg mỗi sáng để hạ huyết áp.\n"
        "Bác sĩ: Nếu mai còn sốt cao thì quay lại chụp phim phổi nhé."
    )
    
    ps = [
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="ho có đờm", bang_chung=[2], trich_dan=["ho có đờm"]),
        PhatBieu(id=2, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng penicillin", bang_chung=[4], trich_dan=["dị ứng kháng sinh penicillin"]),
        PhatBieu(id=3, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="đang uống thuốc amlodipin", bang_chung=[6], trich_dan=["uống viên amlodipin"]),
        PhatBieu(id=4, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="nếu mai còn sốt cao thì quay lại chụp phim phổi nhé", bang_chung=[7], trich_dan=["quay lại chụp phim phổi"])
    ]
    
    thong_tin_bn = {
        "id": "BN_7718",
        "gioi_tinh": "nam",
        "tuoi": 62,
        "egfr": 75
    }

    ket_qua = MediTracePipelineOrchestrator.xu_ly_ca_kham(
        ma_ca="test_e2e_001",
        hoi_thoai=hoi_thoai,
        danh_sach_phat_bieu=ps,
        thong_tin_benh_nhan=thong_tin_bn
    )

    # 1. Kiểm tra kết quả tổng thể
    assert ket_qua.ma_ca == "test_e2e_001"
    assert ket_qua.audit_trail is not None
    assert ket_qua.audit_trail.chu_ky_bam_sha256
    assert len(ket_qua.audit_trail.cac_chot_kiem_soat) == 6
    assert ket_qua.hieu_chinh_lieu is not None
    assert ket_qua.ban_dan_do_benh_nhan is not None

    # 2. Kiểm tra các chốt kiểm soát
    ten_chot = [c.ten_chot for c in ket_qua.audit_trail.cac_chot_kiem_soat]
    assert any("Guardrail 1" in t for t in ten_chot)
    assert any("Guardrail 2" in t for t in ten_chot)
    assert any("Guardrail 3" in t for t in ten_chot)
    assert any("Khóa căn cứ" in t for t in ten_chot)
    assert any("Guardrail 5" in t for t in ten_chot)
    assert any("Chốt 7" in t for t in ten_chot)

    # 3. Kiểm tra xuất bản HL7 FHIR
    assert ket_qua.fhir_bundle["resourceType"] == "Bundle"
    assert ket_qua.fhir_bundle["type"] == "document"
    assert len(ket_qua.fhir_bundle["entry"]) >= 3

    # 4. Kiểm tra phân vùng bệnh án
    assert "CẦN XÁC NHẬN" in ket_qua.ban_nhap_3_phan_vung


def test_dieu_phoi_kem_can_lam_sang_va_thang_diem():
    hoi_thoai = (
        "Bác sĩ: Bác sốt và ho mấy hôm rồi?\n"
        "Bệnh nhân: Dạ sốt cao 39 độ và ho khạc đờm vàng ba hôm nay.\n"
        "Bác sĩ: Nghe phổi có rale ẩm rải rác bên phải."
    )
    ps = [
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="sốt cao 39 độ", bang_chung=[2], trich_dan=["sốt cao 39 độ"]),
        PhatBieu(id=2, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="rale ẩm rải rác bên phải", bang_chung=[3], trich_dan=["rale ẩm rải rác"])
    ]
    thong_tin_bn = {
        "id": "BN_9981",
        "tuoi": 70,
        "gioi_tinh": "nam"
    }
    xet_nghiem = {
        "wbc": 15.2,
        "urea": 8.1,
        "xquang_phoi": "Đám mờ đông đặc thùy dưới phổi phải"
    }

    ket_qua = MediTracePipelineOrchestrator.xu_ly_ca_kham(
        ma_ca="test_e2e_cls_002",
        hoi_thoai=hoi_thoai,
        danh_sach_phat_bieu=ps,
        thong_tin_benh_nhan=thong_tin_bn,
        du_lieu_xet_nghiem=xet_nghiem
    )

    assert ket_qua.doi_soat_can_lam_sang is not None
    assert len(ket_qua.doi_soat_can_lam_sang.chan_doan_duoc_xac_nhan) >= 1
    assert "CURB-65" in ket_qua.thang_diem_nguy_co
    assert ket_qua.thang_diem_nguy_co["CURB-65"]["diem_so"] >= 2
    assert len(ket_qua.audit_trail.cac_chot_kiem_soat) == 7


def test_asr_goi_y_thuoc_phai_chuyen_sang_can_xac_nhan_va_boi_do():
    """Kiểm tra nguyên tắc cốt tử: Gợi ý tên thuốc do ASR nhận diện âm vị dân gian (như 'a móc')
    TUYỆT ĐỐI không tự động chấp thuận mà BẮT BUỘC BÔI ĐỎ và ĐƯA SANG MỤC CẦN XÁC NHẬN.
    """
    hoi_thoai = (
        "Bác sĩ: Bác ở nhà có tự uống thuốc gì chưa?\n"
        "Bệnh nhân: Dạ tôi có ra tiệm mua mấy viên a móc với viên ô mê uống đỡ rát họng.\n"
        "Bác sĩ: Để tôi kiểm tra lại nhé."
    )
    ps = [
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="uống a móc với ô mê", bang_chung=[2], trich_dan=["uống đỡ rát họng"])
    ]
    thong_tin_bn = {"id": "BN_ASR_TEST", "tuoi": 45, "gioi_tinh": "nu"}

    ket_qua = MediTracePipelineOrchestrator.xu_ly_ca_kham(
        ma_ca="test_asr_drug_quarantine",
        hoi_thoai=hoi_thoai,
        danh_sach_phat_bieu=ps,
        thong_tin_benh_nhan=thong_tin_bn
    )

    # 1. Mục CẦN XÁC NHẬN bắt buộc phải có nội dung cảnh báo bôi đỏ
    can_xac_nhan = ket_qua.ban_nhap_3_phan_vung.get("CẦN XÁC NHẬN", "")
    assert "[BÔI ĐỎ - CẦN BÁC SĨ XÁC NHẬN TÊN THUỐC]" in can_xac_nhan
    assert "a móc" in can_xac_nhan
    assert "Amoxicillin" in can_xac_nhan
    assert "ô mê" in can_xac_nhan
    assert "Omeprazole" in can_xac_nhan

    # 2. Kiểm tra trong Audit Trail có ghi nhận cảnh báo ASR Guardrail
    chot_asr = [c for c in ket_qua.audit_trail.cac_chot_kiem_soat if "Guardrail 1" in c.ten_chot][0]
    assert chot_asr.trang_thai in ("DAT", "CANH_BAO")
    assert any("a móc" in cb for cb in chot_asr.canh_bao)



