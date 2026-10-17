# -*- coding: utf-8 -*-
"""Test suite cho he thong Guardrails da tang trong src/guardrails.py."""
import pytest
from src import guardrails as gr


def test_guardrail_asr_phat_hien_am_vi_thuoc():
    g1 = gr.ASRQualityGuardrail()
    res = g1.kiem_tra_phien_am("Bệnh nhân bảo uống a mô xi lin một tuần nay")
    assert any("amoxicillin" in c for c in res.canh_bao)
    assert res.goi_y.get("a mô xi lin") == "amoxicillin"


def test_guardrail_asr_chan_chuoi_rong():
    g1 = gr.ASRQualityGuardrail()
    res = g1.kiem_tra_phien_am("  ")
    assert not res.hop_le
    assert res.chi_tiet == "ASR_EMPTY"


def test_guardrail_chu_the_phat_hien_mau_thuan_nguoi_nha():
    g2 = gr.SpeakerConsistencyGuardrail()
    # Người nhà nói "mẹ tôi bị hen" nhưng gán chủ thể cho bệnh nhân (chu_the_id = 0)
    res = g2.kiem_tra_xung_ho(
        nguoi_noi="người nhà",
        chu_the_id=0,
        cau_noi="Mẹ tôi thì bị hen suyễn từ thời trẻ"
    )
    assert not res.hop_le
    assert any("Mâu thuẫn chủ thể" in c for c in res.canh_bao)


def test_guardrail_chu_the_hop_le_khi_dung_chu_the():
    g2 = gr.SpeakerConsistencyGuardrail()
    res = g2.kiem_tra_xung_ho(
        nguoi_noi="người nhà",
        chu_the_id=1,  # Đã gán cho người nhà (khác 0)
        cau_noi="Mẹ tôi thì bị hen suyễn từ thời trẻ"
    )
    assert res.hop_le


def test_guardrail_hanh_vi_thoai_dinh_chinh():
    g3 = gr.DialogueActGuardrail()
    cau = "Tôi đau bụng khoảng 3 ngày... à không, đúng ra là 5 ngày rồi"
    dinh_chinh = g3.phat_hien_dinh_chinh(cau)
    assert dinh_chinh is not None
    cu, moi = dinh_chinh
    assert "3 ngày" in cu
    assert "5 ngày" in moi


def test_guardrail_hanh_vi_thoai_gia_dinh():
    g3 = gr.DialogueActGuardrail()
    assert g3.la_cau_gia_dinh_hoac_tuong_lai("Nếu mai còn sốt thì quay lại chụp phim")
    assert g3.la_cau_gia_dinh_hoac_tuong_lai("Hẹn bác hai tuần nữa tái khám nhé")
    assert not g3.la_cau_gia_dinh_hoac_tuong_lai("Tôi bị sốt và ho liên tục hai hôm nay")


def test_guardrail_can_cu_chong_hallucination():
    g4 = gr.EvidenceIntegrityGuardrail()
    goc = "Bệnh nhân: Tôi bị dị ứng với thuốc kháng sinh amoxicillin nổi mẩn ngứa khắp người"
    
    # Đúng nguyên văn
    res_dung = g4.kiem_tra_can_cu("dị ứng với thuốc kháng sinh amoxicillin", goc)
    assert res_dung.hop_le
    assert res_dung.chi_tiet == "EXACT_MATCH"

    # Bịa đặt thông tin (không có trong câu gốc)
    res_sai = g4.kiem_tra_can_cu("bệnh nhân từng bị sốc phản vệ ngừng tim", goc)
    assert not res_sai.hop_le
    assert res_sai.chi_tiet == "HALLUCINATION_DETECTED"


def test_guardrail_an_toan_bat_nham_con_hon_bo_sot():
    g5 = gr.ClinicalSafetyGuardrail()

    class GiaDanhGia:
        def __init__(self, loai, nhom, ly_do):
            self.loai = loai
            self.nhom = nhom
            self.ly_do = ly_do

    # Dị ứng dù có cảnh báo nhỏ cũng phải chuyển CẦN XÁC NHẬN, không bỏ sót
    dg_di_ung = GiaDanhGia(loai="di_ung", nhom="nguy cơ cao", ly_do=["chủ thể suy từ người nói"])
    muc = g5.dinh_tuyen_an_toan({}, dg_di_ung)
    assert muc == "CAN_XAC_NHAN"

    # Thuốc NTI bị chặn căn cứ -> Đưa vào CẦN XÁC NHẬN để bác sĩ duyệt thay vì xóa mất tích
    dg_nti_bi_chan = GiaDanhGia(loai="thuoc_nti", nhom="bị chặn", ly_do=["không có trích dẫn"])
    muc_nti = g5.dinh_tuyen_an_toan({}, dg_nti_bi_chan)
    assert muc_nti == "CAN_XAC_NHAN"


def test_guardrail_chong_ao_giac_so_lieu():
    g4 = gr.EvidenceIntegrityGuardrail()
    goc = "Bác sĩ: Huyết áp của bác đo được là 130 trên 85, nhiệt độ 37 độ 5 nhé."

    # Hợp lệ: Con số xuất hiện trong lời thoại gốc
    res_ok = g4.kiem_tra_ao_giac_so_lieu("Huyết áp 130/85, thân nhiệt 37.5", goc)
    assert res_ok.hop_le
    assert res_ok.chi_tiet == "NUMBERS_VERIFIED"

    # Ảo giác: AI tự bịa ra huyết áp 180 và liều thuốc 500mg không có trong thoại
    res_hallucinated = g4.kiem_tra_ao_giac_so_lieu("Huyết áp 180/100, cho uống paracetamol 500mg", goc)
    assert not res_hallucinated.hop_le
    assert res_hallucinated.chi_tiet == "HALLUCINATION_NUMERICAL_DETECTED"
    assert "180" in res_hallucinated.goi_y["so_ao_giac"]
    assert "500" in res_hallucinated.goi_y["so_ao_giac"]


def test_guardrail_doi_soat_duoc_thu_quoc_gia():
    g4 = gr.EvidenceIntegrityGuardrail()

    # Thuốc chuẩn trong Dược thư Quốc gia
    res_dt = g4.kiem_tra_duoc_thu_quoc_gia("amoxicillin 500mg")
    assert res_dt.hop_le
    assert res_dt.chi_tiet == "PHARMACOPOEIA_VERIFIED"

    # Tên âm vị tiếng Việt dân gian
    res_av = g4.kiem_tra_duoc_thu_quoc_gia("uống viên a móc")
    assert res_av.hop_le
    assert res_av.chi_tiet == "PHARMACOPOEIA_MATCHED_ALIASED"
    assert res_av.goi_y["hoat_chat"] == "amoxicillin"

    # Tên thuốc lạ hoắc AI bịa ra
    res_la = g4.kiem_tra_duoc_thu_quoc_gia("thuoc_than_ky_xyz 1000mg")
    assert not res_la.hop_le
    assert res_la.chi_tiet == "THUOC_NGOAI_DANH_MUC"


def test_guardrail_nguong_an_toan_lieu_tran():
    g4 = gr.EvidenceIntegrityGuardrail()

    # Liều an toàn: Paracetamol 2000mg/ngày (dưới trần 4000mg)
    res_safe = g4.kiem_tra_nguong_lieu_an_toan("paracetamol", 2000.0)
    assert res_safe.hop_le
    assert res_safe.chi_tiet == "SAFE_DOSE"

    # Quá liều nguy hiểm: Paracetamol 5000mg/ngày (vượt trần 4000mg)
    res_over = g4.kiem_tra_nguong_lieu_an_toan("paracetamol", 5000.0)
    assert not res_over.hop_le
    assert res_over.chi_tiet == "OVERDOSE_HAZARD"
    assert any("CẢNH BÁO QUÁ LIỀU NGUY HIỂM" in c for c in res_over.canh_bao)

