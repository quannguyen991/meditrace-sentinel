# -*- coding: utf-8 -*-
"""Bộ kiểm thử toàn diện kiểm toán tầng Python (P0 Fixes + Cấu trúc Pha 1–3).

Bao phủ:
1. Khử định danh PII/PHI (`src/he_thong/khu_dinh_danh.py`): không nuốt triệu chứng sau tên người, ranh giới từ Unicode cho tên ngắn ("An").
2. Tiền kiểm BHYT, HL7 FHIR R4, Cận lâm sàng & Thang điểm (`kiem_duyet_bhyt_va_bo_sot`, `fhir_exporter`, `can_lam_sang`, `thang_diem_lam_sang`).
3. Điều phối hạ tầng, Guardrails, Luồng âm thanh (`SpeakerRole.NURSE` / `OTHER`), `hoi_lai`, `nhanh` (`C_khoa_v2`).
4. Tối ưu khởi động `GET /api/suc-khoe` (< 100ms, không nạp `scipy`/`cham_he_thong`/`torch`, không quét đĩa `dem`, không làm bẩn `_pipe`),
   Lock đa luồng, socket timeout = 60, `vao.get("metadata")`, `ContextualPrefixTrie600` 2 chiều & hotwords theo hệ cơ quan,
   và thống nhất danh mục thuốc (`sintrom` -> `acenocoumarol`, chữ `'e'` cuối, biệt dược, `benh_nen`/`tien_su_benh`, `can_nang`/`can_nang_kg`).
5. HTTP integration tests gọi thật `May` cho `/api/suc-khoe`, `/api/ho-so`, `/api/bhyt/precheck`, `/api/ocr/phieu-cu`.
"""
from __future__ import annotations

import http.client
import json
import subprocess
import sys
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path

from src.duong_ong import b3_cap_nhat_trang_thai as cap_nhat
from src.he_thong import dich_vu_http as dich_vu
from src.duong_ong import b6_goi_y_hoi_lai as hoi_lai
from src.duong_ong import chay_duong_ong as nhanh
from src.duong_ong import b1_cau_truc_menh_de as phat_bieu
from src.duong_ong import b2_gom_nguoi_thuc_the as thuc_the
from src.cong_cu_lam_sang.tra_duoc_thu_aho_corasick import BoTraCuuDuocThuAhoCorasick
from src.he_thong.hop_dong_api import validate_contract_keys
from src.audio.adapter import to_meditrace
from src.audio.asr import faster_whisper_provider, phowhisper_provider
from src.audio.asr.contextual_trie_600 import (
    ContextualPrefixTrie600,
    chuan_hoa_he_co_quan,
    tao_trie_600_mac_dinh,
    ten_he_co_quan_tieng_viet,
)
from src.audio.models import SpeakerRole
from src.audio.pipeline import AudioPipeline
from src.audio.storage import SessionStore
from src.cong_cu_lam_sang.doi_soat_can_lam_sang import ParaclinicalCorrelator
from src.he_thong.dieu_phoi_cac_chot_an_toan import MediTracePipelineOrchestrator, _trich_danh_sach_thuoc_hop_le
from src.cong_cu_lam_sang.canh_bao_tuong_tac_thuoc import ClinicalPharmacovigilanceEngine
from src.cong_cu_lam_sang.xuat_fhir_r4 import FHIRExporter
from src.he_thong.rao_chan_an_toan import ASRQualityGuardrail, SpeakerConsistencyGuardrail
from src.cong_cu_lam_sang.hieu_chinh_lieu import kiem_tra_hieu_chinh_lieu
from src.he_thong.khu_dinh_danh import ClinicalDeidentifier
from src.cong_cu_lam_sang.tien_kiem_bhyt_va_khoi_phuc_bo_sot import (
    BHYTXmlPreChecker,
    tien_kiem_bhyt_tu_du_lieu,
    xuat_goi_xml_1_5_qd130,
)
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu
from src.cong_cu_lam_sang.thang_diem_nguy_co import ClinicalRiskScoringEngine


# ==============================================================================
# 1. KHỬ ĐỊNH DANH (`src/he_thong/khu_dinh_danh.py`)
# ==============================================================================
def test_p0_khu_dinh_danh_khong_nuot_trieu_chung_sau_ho_ten():
    cau = "Tôi tên là Nguyễn Văn An năm nay bốn mươi tuổi bị đau ngực khó thở"
    kq = ClinicalDeidentifier.an_danh_van_ban(cau)
    assert "Nguyễn Văn An" not in kq.van_ban_da_an_danh
    assert "[HO_TEN_1]" in kq.van_ban_da_an_danh
    assert "năm nay bốn mươi tuổi bị đau ngực khó thở" in kq.van_ban_da_an_danh
    assert ClinicalDeidentifier.giai_ma_van_ban(kq.van_ban_da_an_danh, kq.bang_anh_xa_giai_ma) == cau

    # Kiểm tra cả trường hợp viết hoa toàn bộ họ tên trong phiếu hành chính
    cau_hoa = "Họ tên: TRẦN VĂN BÌNH năm nay sáu mươi tuổi bị sốt cao ho đờm"
    kq_hoa = ClinicalDeidentifier.an_danh_van_ban(cau_hoa)
    assert "TRẦN VĂN BÌNH" not in kq_hoa.van_ban_da_an_danh
    assert "năm nay sáu mươi tuổi bị sốt cao ho đờm" in kq_hoa.van_ban_da_an_danh


def test_p0_khu_dinh_danh_ranh_gioi_tu_unicode_cho_ten_ngan():
    vb = "Bệnh nhân An có tiền sử suy gan, hiện đang dùng losartan 50mg và truyền vancomycin."
    kq = ClinicalDeidentifier.an_danh_van_ban(vb, ten_benh_nhan="An")
    assert "Bệnh nhân [BENH_NHAN] có" in kq.van_ban_da_an_danh
    for tu_y_khoa in ("suy gan", "đang", "losartan", "vancomycin"):
        assert tu_y_khoa in kq.van_ban_da_an_danh

    # Khi tên ngắn không xuất hiện độc lập trong câu -> không được khớp nhầm chuỗi con
    vb_khong_ten = "Người bệnh suy gan, đang uống losartan và tiêm vancomycin."
    kq_khong = ClinicalDeidentifier.an_danh_van_ban(vb_khong_ten, ten_benh_nhan="An")
    assert kq_khong.van_ban_da_an_danh == vb_khong_ten
    assert kq_khong.tong_so_thuc_the == 0


# ==============================================================================
# 2. BHYT, FHIR R4, CẬN LÂM SÀNG & THANG ĐIỂM
# ==============================================================================
def test_p0_bhyt_bao_toan_chu_the_tinh_huong_trang_thai_va_loc_xml2_xml5():
    props = [
        {
            "id": 1,
            "text": "Mẹ bị đái tháo đường típ 2 lâu năm",
            "subject": "mẹ",
            "section": "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI",
            "status": "còn hiệu lực",
        },
        {
            "id": 2,
            "text": "Bố bị tăng huyết áp",
            "subject": "bố",
            "status": "còn hiệu lực",
        },
        {
            "id": 3,
            "text": "Nếu đau ngực dữ dội thì nghi thiếu máu cơ tim",
            "subject": "bệnh nhân",
            "situation": "giả định",
            "status": "còn hiệu lực",
        },
        {
            "id": 4,
            "text": "Hen phế quản",
            "subject": "bệnh nhân",
            "status": "bị thay thế",
        },
        {
            "id": 5,
            "text": "Viêm họng cấp",
            "subject": "bệnh nhân",
            "nguoi_noi": "bác sĩ",
            "status": "than",
        },
        {
            "id": 6,
            "text": "Đã ngừng Metformin 500mg từ tháng trước",
            "subject": "bệnh nhân",
            "drug": "Metformin",
            "drugStatus": "đã ngừng",
            "status": "còn hiệu lực",
        },
        {
            "id": 7,
            "text": "Amoxicillin 500mg ngày 2 lần",
            "subject": "bệnh nhân",
            "drug": "Amoxicillin",
            "status": "còn hiệu lực",
        },
    ]
    kq = tien_kiem_bhyt_tu_du_lieu(props, "Khám viêm họng cấp, mẹ tiểu đường, bố tăng huyết áp.")
    # Bệnh sử của mẹ (E11.9), bố (I10), câu giả định (I20.9) và câu bị thay thế (J45.9) KHÔNG ĐƯỢC thành ICD-10 của BN!
    assert kq["ma_icd10_chinh"]["ma_icd10"] == "J02.9"
    ma_tat_ca = [x["ma"] for x in kq["icd10_chi_tiet"]]
    assert ma_tat_ca == ["J02.9"]

    # XML2 không chứa thuốc đã ngừng (Metformin), nhưng giữ thuốc đang kê (Amoxicillin)
    xml2 = kq["goi_xml_1_5"]["XML2"]
    assert "Metformin" not in xml2
    assert "Amoxicillin" in xml2

    # XML5 chỉ chứa diễn biến của chính bệnh nhân (chu_the_id == 0), không chứa bệnh sử của mẹ/bố
    xml5 = kq["goi_xml_1_5"]["XML5"]
    assert "Viêm họng cấp" in xml5
    assert "Mẹ bị đái tháo đường" not in xml5
    assert "Bố bị tăng huyết áp" not in xml5


def test_p0_dich_vu_truyen_thong_tin_benh_nhan_vao_bhyt_kiem_duyet():
    ban_ghi = {
        "id": "ca_nhi_bhyt",
        "input": "Bác sĩ: Viêm họng cấp, kê Paracetamol 800mg.",
        "phat_bieu": [
            {"id": 1, "nguoi_noi": "bác sĩ", "chu_the_id": 0, "noi_dung": "viêm họng cấp", "hanh_vi": "nhận định", "bang_chung": [1]},
            {
                "id": 2,
                "nguoi_noi": "bác sĩ",
                "chu_the_id": 0,
                "noi_dung": "uống Paracetamol 800mg",
                "tinh_huong": "kế hoạch",
                "thuoc": {"ten": "paracetamol", "lieu": "800mg", "duong_dung": "uống"},
                "bang_chung": [1],
            },
        ],
    }
    # Cân nặng 10kg chỉ nằm trong thong_tin_benh_nhan (không xuất hiện trong hội thoại)
    kq = dich_vu._them_canh_bao(ban_ghi, thong_tin_benh_nhan={"tuoi": 3, "can_nang": 10.0})
    cb_nhi = kq["lam_sang_nang_cao"]["bhyt_icd10"]["canh_bao_lieu_nhi_khoa"]
    assert len(cb_nhi) >= 1
    assert any("80" in c for c in cb_nhi)


def test_p0_fhir_phu_dinh_di_ung_thuoc_dang_dung_va_xet_nghiem_hai_nguon():
    for cau_phu_dinh in ("Không dị ứng thuốc", "Chưa ghi nhận dị ứng thuốc và thức ăn", "Dị ứng: không có", "NKDA"):
        bundle = FHIRExporter.xuat_fhir_bundle(
            ma_ca="ca_fhir_neg",
            ban_nhap={
                "CHẨN ĐOÁN": "Tăng huyết áp",
                "DỊ ỨNG": cau_phu_dinh,
                "THUỐC ĐANG DÙNG": "Amlodipin 5mg mỗi sáng",
                "KẾ HOẠCH ĐIỀU TRỊ": "",
            },
            thong_tin_benh_nhan={"id": "BN1", "xet_nghiem": {"hba1c": 7.2}},
            du_lieu_xet_nghiem={"creatinine": 1.4, "urea": 8.5},
        )
        entries = [e["resource"] for e in bundle["entry"]]
        allergies = [r for r in entries if r["resourceType"] == "AllergyIntolerance"]
        assert not any(
            a.get("clinicalStatus", {}).get("coding", [{}])[0].get("code") == "active"
            and a.get("criticality") == "high"
            for a in allergies
        ), cau_phu_dinh

        # Khi thuoc_ke_don rỗng: KHÔNG tạo MedicationRequest (intent="order"), chỉ giữ MedicationStatement
        med_reqs = [r for r in entries if r["resourceType"] == "MedicationRequest"]
        med_stmts = [r for r in entries if r["resourceType"] == "MedicationStatement"]
        assert med_reqs == []
        assert len(med_stmts) == 1 and "Amlodipin" in med_stmts[0]["medicationCodeableConcept"]["text"]

        # Đọc xét nghiệm đồng thời từ cả `du_lieu_xet_nghiem` lẫn `thong_tin_benh_nhan["xet_nghiem"]`
        obs_codes = {
            c["code"]
            for r in entries
            if r["resourceType"] == "Observation"
            for c in r.get("code", {}).get("coding", [])
        }
        assert {"4548-4", "2160-0", "3091-6"}.issubset(obs_codes)


def test_p0_can_lam_sang_giu_troponin_0_va_bao_dong_do_urea():
    kq = ParaclinicalCorrelator.phan_tich_xet_nghiem({"troponin": 0.0, "urea": 18.4})
    by_code = {c.ma_xet_nghiem: c for c in kq.danh_sach_chi_so}
    assert "TROPONIN" in by_code
    assert by_code["TROPONIN"].gia_tri == 0.0
    assert by_code["TROPONIN"].trang_thai == "BINH_THUONG"

    assert "UREA" in by_code
    assert by_code["UREA"].trang_thai == "NGUY_KICH"
    assert kq.co_gia_tri_nguy_kich is True
    assert any("Ure" in b for b in kq.bao_dong_do_khan_cap)


def test_p0_thang_diem_giu_float_cho_wells_pe_va_bmi():
    wells = ClinicalRiskScoringEngine.tinh_wells_pe(
        pe_la_chan_doan_hang_dau=True,   # +3.0
        nhip_tim_tren_100=True,          # +1.5 -> 4.5 (> 4.0 -> CAO)
    )
    assert isinstance(wells.diem_so, float)
    assert wells.diem_so == 4.5
    assert wells.phan_tang_nguy_co == "CAO"

    bmi = ClinicalRiskScoringEngine.tinh_bmi(can_nang_kg=75.0, chieu_cao_cm=165.0)
    assert isinstance(bmi.diem_so, float)
    assert bmi.diem_so == 27.5


# ==============================================================================
# 3. ĐIỀU PHỐI HẠ TẦNG, GUARDRAILS, LUỒNG ÂM THANH, HỎI LẠI & NHÁNH
# ==============================================================================
def test_p0_dieu_phoi_loc_thuoc_khong_nhan_doi_can_xac_nhan_va_chot_4():
    ps = [
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng thuốc kháng sinh penicillin", bang_chung=[1], trich_dan=["dị ứng thuốc kháng sinh penicillin"]),
        PhatBieu(id=2, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="nghỉ ngơi tại nhà, uống nhiều nước ấm, tái khám sau 5 ngày", hanh_vi="kế hoạch", bang_chung=[2], trich_dan=["nghỉ ngơi tại nhà"]),
        PhatBieu(id=3, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="kê viên Losec 20mg trước ăn sáng", hanh_vi="kế hoạch", bang_chung=[2], trich_dan=["viên Losec 20mg"]),
        # Phát biểu giả định / sai trích dẫn để kích hoạt chặn ở Chốt 4
        PhatBieu(id=4, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="đau ngực dữ dội", bang_chung=[1], trich_dan=["câu này không tồn tại trong hội thoại"]),
    ]
    ds_thuoc = _trich_danh_sach_thuoc_hop_le(ps)
    assert not any("penicillin" in t.lower() for t in ds_thuoc)
    assert not any("nghỉ ngơi" in t.lower() for t in ds_thuoc)
    assert any("losec" in t.lower() for t in ds_thuoc)

    hoi_thoai = (
        "Bệnh nhân: Dạ tôi bị xốt nhẹ và dị ứng thuốc kháng sinh penicillin.\n"
        "Bác sĩ: Bác nghỉ ngơi tại nhà, tôi kê viên Losec 20mg trước ăn sáng."
    )
    kq = MediTracePipelineOrchestrator.xu_ly_ca_kham("ca_orch_p0", hoi_thoai, ps)
    cxn = kq.ban_nhap_3_phan_vung["CẦN XÁC NHẬN"]
    # Không nhân đôi lý do chặn của mệnh đề ID 4
    assert cxn.count("trích dẫn không có trong hội thoại") == 1
    # Triệu chứng biến âm 'xốt' tuyệt đối không bị gắn nhãn bôi đỏ tên thuốc!
    assert "[BÔI ĐỎ - CẦN BÁC SĨ XÁC NHẬN TÊN THUỐC]" not in cxn

    # Chốt 4 phản ánh đúng mệnh đề bị chặn (CANH_BAO thay vì DAT giả từ khóa co_loi không tồn tại)
    chot_4 = next(c for c in kq.audit_trail.cac_chot_kiem_soat if "Khóa căn cứ" in c.ten_chot)
    assert chot_4.trang_thai == "CANH_BAO"
    assert "1 mệnh đề bị chặn" in chot_4.chi_tiet


def test_p0_guardrails_tach_phuong_ngu_giu_ao_giac_lap_va_xung_ho_nhi():
    # Có cả biến âm 'xốt' (len(goi_y) > 0) VÀ vòng lặp ảo giác ASR -> hop_le bắt buộc phải False!
    res_lap = ASRQualityGuardrail.kiem_tra_phien_am("Bệnh nhân bị xốt cao đau đau đau đau")
    assert res_lap.goi_y_phuong_ngu.get("xốt") == "sốt"
    assert res_lap.goi_y_thuoc == {}
    assert res_lap.hop_le is False
    assert any("vòng lặp" in c for c in res_lap.canh_bao)

    # Chỉ có biến âm triệu chứng lành tính -> hop_le True, không lẫn vào goi_y_thuoc
    res_pn = ASRQualityGuardrail.kiem_tra_phien_am("Bệnh nhân bị xốt cao và lôn mửa từ sáng")
    assert res_pn.hop_le is True
    assert res_pn.goi_y_thuoc == {}
    assert res_pn.goi_y_phuong_ngu.get("xốt") == "sốt"

    # Nhi khoa: 'bé nhà em', 'con tôi', 'cháu nhà tôi' khi chu_the_id == 0 là hợp lệ
    for cau_nhi in ("Bé nhà em bị sốt 3 ngày nay", "Con tôi ho nhiều về đêm", "Cháu nhà tôi nôn 2 lần"):
        r_nhi = SpeakerConsistencyGuardrail.kiem_tra_xung_ho("người nhà", 0, cau_nhi)
        assert r_nhi.hop_le is True, cau_nhi


def test_p0_speaker_role_nurse_va_other_khong_mat_menh_de(tmp_path: Path):
    assert SpeakerRole.NURSE.value == "nurse"
    assert SpeakerRole.OTHER.value == "other"

    segs = [
        {"segment_id": "s1", "speaker_id": "spk_1", "speaker_role": SpeakerRole.NURSE.value, "text_original": "Huyết áp đo được 130/80 mmHg.", "start_time": 0.0, "end_time": 2.5},
        {"segment_id": "s2", "speaker_id": "spk_2", "speaker_role": SpeakerRole.OTHER.value, "text_original": "Bệnh nhân vừa nôn ở ngoài hành lang.", "start_time": 2.6, "end_time": 5.0},
    ]
    mt = to_meditrace(segs, strict=True)
    assert "Điều dưỡng: Huyết áp đo được 130/80 mmHg." in mt["input"]
    assert "Người khác: Bệnh nhân vừa nôn ở ngoài hành lang." in mt["input"]
    assert mt["turns"][0]["nguoi_noi"] == "dieu_duong"
    assert mt["turns"][1]["nguoi_noi"] == "nguoi_khac"

    # Kiểm tra AudioPipeline.map_speakers chấp nhận role 'nurse' và 'other'
    store = SessionStore(tmp_path / "audio_store")
    sess = store.create()
    sid = sess["session_id"]
    (store.path(sid, "transcript.json")).write_text(
        json.dumps([
            {"segment_id": "s1", "speaker_id": "spk_1", "speaker_role": "unknown", "text_original": "Mạch 80 lần/phút", "start_time": 0.0, "end_time": 1.0},
            {"segment_id": "s2", "speaker_id": "spk_2", "speaker_role": "unknown", "text_original": "Tôi đỡ mệt rồi", "start_time": 1.1, "end_time": 2.0},
        ], ensure_ascii=False),
        encoding="utf-8",
    )
    pipe = AudioPipeline(store)
    mapped = pipe.map_speakers(sid, {"spk_1": "nurse", "spk_2": "other"})
    assert [m["speaker_role"] for m in mapped] == ["nurse", "other"]

    # Kiểm tra PhatBieu.tu_json không vứt bỏ mệnh đề của 'điều dưỡng' hoặc 'người khác'
    luot_vai = {so: vai for so, vai, _ in thuc_the.tach_luot(mt["input"]) if vai}
    ps, loi = phat_bieu.tu_json(
        [
            {"chu_the": "bệnh nhân", "noi_dung": "huyết áp 130/80", "luot_thoai": [1], "hanh_vi": "quan sát"},
            {"chu_the": "bệnh nhân", "noi_dung": "vừa nôn ngoài hành lang", "luot_thoai": [2]},
        ],
        nguoi_noi_theo_luot=luot_vai,
    )
    assert loi == []
    assert len(ps) == 2
    assert ps[0].nguoi_noi == "điều dưỡng"
    assert ps[1].nguoi_noi == "người khác"


def test_p0_hoi_lai_khong_gay_value_error_khi_tai_tao_phat_bieu():
    # 1. Mâu thuẫn khi quan_he_voi=None hoặc có quan_he_voi
    p_mt_goc = PhatBieu(id=0, nguoi_noi="người nhà", chu_the_id=0, noi_dung="sốt", moc_thoi_gian="4 ngày", bang_chung=[1])
    p_mt_doi = PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="sốt", moc_thoi_gian="2 ngày", quan_he="mâu thuẫn", quan_he_voi=0, bang_chung=[2])
    ch_mt = hoi_lai.CauHoi(van="Thời điểm đúng?", ly_do="mau_thuan", muc_tieu={0: 1.0, 1: 1.0})
    hoi_lai.ap_dung_tra_loi(p_mt_goc, ch_mt, "2 ngày")
    hoi_lai.ap_dung_tra_loi(p_mt_doi, ch_mt, "2 ngày")
    # Khởi tạo lại PhatBieu từ to_dict() tuyệt đối không ném ValueError
    assert PhatBieu(**p_mt_goc.to_dict()).moc_thoi_gian == "2 ngày"
    assert PhatBieu(**p_mt_doi.to_dict()).quan_he == "bổ sung"

    # 2. Dị ứng chưa ghi nhận: trả lời 'Đã từng dùng an toàn' / 'Chưa bao giờ dùng'
    p_du = PhatBieu(id=2, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng penicillin", do_chac_chan="chưa ghi nhận", bang_chung=[3])
    ch_du = hoi_lai.CauHoi(van="Đã từng dùng chưa?", ly_do="di_ung_chua_ghi_nhan", muc_tieu={2: 1.0})
    hoi_lai.ap_dung_tra_loi(p_du, ch_du, "Đã từng dùng an toàn")
    rebuilt = PhatBieu(**p_du.to_dict())
    assert rebuilt.do_chac_chan == "chắc chắn" and rebuilt.phu_dinh is True

    hoi_lai.ap_dung_tra_loi(p_du, ch_du, "Chưa bao giờ dùng")
    rebuilt_2 = PhatBieu(**p_du.to_dict())
    assert rebuilt_2.do_chac_chan == "chưa ghi nhận" and rebuilt_2.phu_dinh is False


def test_p0_nhanh_dong_thuan_cheo_thong_tin_bn_va_c_khoa_v2():
    ht = (
        "1. Người nhà: Cháu sốt 4 ngày rồi bác sĩ ạ.\n"
        "2. Bệnh nhân: Mẹ nhớ nhầm rồi, con mới sốt 2 ngày thôi.\n"
        "3. Người nhà: À ừ nhỉ, mẹ nhầm, mới sốt 2 ngày."
    )
    kq_tho = [{
        "id": "ca_dt",
        "phat_bieu": [
            {"chu_the": "cháu", "noi_dung": "sốt", "moc_thoi_gian": "4 ngày", "luot_thoai": [1], "trich_dan": ["Cháu sốt 4 ngày rồi"]},
            {"chu_the": "cháu", "noi_dung": "sốt", "moc_thoi_gian": "2 ngày", "quan_he": "đính chính", "quan_he_voi": 0, "luot_thoai": [2], "trich_dan": ["mới sốt 2 ngày thôi"]},
        ],
    }]
    mau = [{"id": "ca_dt", "input": ht, "thong_tin_benh_nhan": {"mang_thai": True, "egfr": 20}}]

    # Nhánh C_khoa nhận hoi_thoai vào cap_nhat.ap_luat (đồng thuận chéo ở lượt 3) & thong_tin_benh_nhan vào cong_rui_ro.cham
    ra_ck = nhanh.chay_trung_gian(mau, None, None, None, "C_khoa", kq_tho=kq_tho)[0]
    assert ra_ck["phat_bieu"][0]["trang_thai"] == "bị thay thế"
    assert ra_ck["phat_bieu"][1]["trang_thai"] == "còn hiệu lực"
    assert all(r["he_so_bn"] > 1.0 for r in ra_ck["rui_ro"])

    # Nhánh C_khoa_v2 sử dụng MayTrangThaiHoiThoai độc lập, không làm thay đổi C_khoa cũ
    ra_v2 = nhanh.chay_trung_gian(mau, None, None, None, "C_khoa_v2", kq_tho=kq_tho)[0]
    assert "fsm_lich_su_chuyen" in ra_v2
    assert "fsm_mau_thuan" in ra_v2
    # Với MayTrangThaiHoiThoai chặt theo vai người nói: đính chính khác người nói chuyển thành mâu thuẫn nguồn
    assert ra_v2["phat_bieu"][0]["trang_thai"] == "chưa giải quyết"


# ==============================================================================
# 4. KHỞI ĐỘNG NHANH `/api/suc-khoe`, LOCK ĐA LUỒNG, TRIE 600 & DANH MỤC THUỐC
# ==============================================================================
def test_p1_cold_start_suc_khoe_duoi_100ms_khong_nap_scipy_torch_hay_quet_dia():
    code = r"""
import http.client, json, sys, threading, time
from http.server import ThreadingHTTPServer
from src.he_thong import dich_vu_http as dich_vu

dich_vu.May.loi = dich_vu.Loi(cho_nap_mo_hinh=False)
dich_vu.May.am = dich_vu.AmThanh()
class SilentMay(dich_vu.May):
    def log_message(self, *args):
        pass

srv = ThreadingHTTPServer(("127.0.0.1", 0), SilentMay)
port = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()

t0 = time.perf_counter()
conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
conn.request("GET", "/api/suc-khoe")
resp = conn.getresponse()
body = json.loads(resp.read().decode("utf-8"))
elapsed_ms = (time.perf_counter() - t0) * 1000.0
conn.close()
srv.shutdown()
srv.server_close()

print(json.dumps({
    "status": resp.status,
    "elapsed_ms": elapsed_ms,
    "scipy_loaded": "scipy" in sys.modules,
    "cham_he_thong_loaded": "src.do_luong.cham_he_thong" in sys.modules,
    "torch_loaded": "torch" in sys.modules,
    "dem_is_none": dich_vu.May.loi._dem is None,
    "pipe_is_none": dich_vu.May.am._pipe is None,
    "timeout": dich_vu.May.timeout,
    "body": body,
}))
"""
    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(Path(__file__).resolve().parents[1]),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    out = json.loads(proc.stdout.strip().splitlines()[-1])
    assert out["status"] == 200
    assert out["elapsed_ms"] < 100.0, f"/api/suc-khoe mất {out['elapsed_ms']:.2f}ms (>= 100ms)"
    assert out["scipy_loaded"] is False
    assert out["cham_he_thong_loaded"] is False
    assert out["torch_loaded"] is False
    assert out["dem_is_none"] is True
    assert out["pipe_is_none"] is True
    assert out["timeout"] == 60
    assert validate_contract_keys(out["body"], "PyHealthResponse") == []


def test_p1_locks_suy_luan_bo_dem_va_asr_cache(monkeypatch):
    loi = dich_vu.Loi(cho_nap_mo_hinh=True)
    loi._dem = {}
    loi._dem_theo_chu = {}
    assert hasattr(loi, "_khoa_suy_luan") and hasattr(loi, "_khoa_dem")
    assert hasattr(phowhisper_provider, "_CACHE_LOCK")
    assert hasattr(faster_whisper_provider, "_CACHE_LOCK")

    dang_chay = {"active": 0, "max_active": 0}
    guard = threading.Lock()

    monkeypatch.setattr(loi, "nap", lambda: ("tok", "model", "prefix"))

    def fake_chay_trung_gian(mau, tok, model, prefix_fn, nhanh_ten, max_token=3072, kq_tho=None):
        with guard:
            dang_chay["active"] += 1
            dang_chay["max_active"] = max(dang_chay["max_active"], dang_chay["active"])
        time.sleep(0.04)
        with guard:
            dang_chay["active"] -= 1
        return [{
            "id": mau[0]["id"],
            "input": mau[0]["input"],
            "du_doan": "CHẨN ĐOÁN\n\nViêm họng.",
            "phat_bieu": [],
            "ghi_chu": [],
        }]

    monkeypatch.setattr(nhanh, "chay_trung_gian", fake_chay_trung_gian)

    ket_qua = []
    threads = [
        threading.Thread(target=lambda idx=i: ket_qua.append(loi.ho_so(f"ca_{idx}", f"Bác sĩ: Lượt {idx}", "C_khoa")))
        for i in range(3)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(ket_qua) == 3
    assert dang_chay["max_active"] == 1, "Suy luận mô hình cục bộ phải được tuần tự hóa bằng _khoa_suy_luan!"


def test_p1_http_integration_full_endpoints_va_metadata_am_thanh(tmp_path: Path, monkeypatch):
    loi = dich_vu.Loi(cho_nap_mo_hinh=False)
    # Gắn sẵn 1 ca vào bộ đệm để kiểm thử /api/ho-so qua cả `input` lẫn `phien` âm thanh
    ht_mau = "Bác sĩ: Bác bị sao ạ?\nBệnh nhân: Dạ tôi đau thượng vị 3 ngày nay."
    loi._dem = {
        "ca_http_1": {
            "id": "ca_http_1",
            "input": ht_mau,
            "phat_bieu": [
                {
                    "chu_the": "tôi",
                    "noi_dung": "đau thượng vị",
                    "moc_thoi_gian": "3 ngày nay",
                    "luot_thoai": [2],
                    "trich_dan": ["đau thượng vị 3 ngày nay"],
                }
            ],
        }
    }
    loi._dem_theo_chu = {" ".join(ht_mau.split()): loi._dem["ca_http_1"]}

    am = dich_vu.AmThanh()
    store = SessionStore(tmp_path / "phien_http")
    sess = store.create()
    phien_id = sess["session_id"]
    store.path(phien_id, "transcript.json").write_text(
        json.dumps([
            {"segment_id": "seg_1", "speaker_id": "s1", "speaker_role": "doctor", "text_original": "Bác bị sao ạ?", "start_time": 0.0, "end_time": 1.8},
            {"segment_id": "seg_2", "speaker_id": "s2", "speaker_role": "patient", "text_original": "Dạ tôi đau thượng vị 3 ngày nay.", "start_time": 2.0, "end_time": 5.5},
        ], ensure_ascii=False),
        encoding="utf-8",
    )

    class _MayHttpTest(dich_vu.May):
        def log_message(self, *args):
            pass

    _MayHttpTest.loi = loi
    _MayHttpTest.am = am
    _MayHttpTest.khoa_noi_bo = "khoa-thu"  # dich vu doi khoa noi bo cho moi /api tru suc-khoe

    server = ThreadingHTTPServer(("127.0.0.1", 0), _MayHttpTest)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)

        # 1. GET /api/suc-khoe: không khởi tạo am._pipe
        t0 = time.perf_counter()
        conn.request("GET", "/api/suc-khoe")
        r_sk = conn.getresponse()
        d_sk = json.loads(r_sk.read().decode("utf-8"))
        assert r_sk.status == 200
        assert (time.perf_counter() - t0) * 1000.0 < 100.0
        assert am._pipe is None
        assert validate_contract_keys(d_sk, "PyHealthResponse") == []

        # Nạp store tạm cho bước test `phien`
        am._pipe = AudioPipeline(store)

        # 2. POST /api/ho-so (qua `phien` âm thanh -> bảo toàn vao.get("metadata") & audio_spans)
        conn.request(
            "POST",
            "/api/ho-so",
            body=json.dumps({"phien": phien_id, "nhanh": "C_khoa"}),
            headers={"Content-Type": "application/json", "X-MediTrace-Internal-Token": "khoa-thu"},
        )
        r_hs = conn.getresponse()
        d_hs = json.loads(r_hs.read().decode("utf-8"))
        assert r_hs.status == 200
        assert validate_contract_keys(d_hs, "PyNoteResponse") == []
        assert isinstance(d_hs.get("metadata"), list) and len(d_hs["metadata"]) == 2
        assert d_hs["phat_bieu"][0]["audio_spans"][0]["start_ms"] == 2000
        assert d_hs["phat_bieu"][0]["audio_spans"][0]["end_ms"] == 5500

        # 3. POST /api/bhyt/precheck
        conn.request(
            "POST",
            "/api/bhyt/precheck",
            body=json.dumps({
                "propositions": [
                    {"id": 1, "text": "Mẹ bị tiểu đường", "subject": "mẹ"},
                    {"id": 2, "text": "Tăng huyết áp vô căn", "subject": "bệnh nhân", "nguoi_noi": "bác sĩ"},
                ],
                "transcript": "Bác sĩ chẩn đoán tăng huyết áp, mẹ bị tiểu đường.",
            }),
            headers={"Content-Type": "application/json", "X-MediTrace-Internal-Token": "khoa-thu"},
        )
        r_bh = conn.getresponse()
        d_bh = json.loads(r_bh.read().decode("utf-8"))
        assert r_bh.status == 200
        assert validate_contract_keys(d_bh, "PyBhytPrecheckResponse") == []
        assert d_bh["ma_icd10_chinh"]["ma_icd10"] == "I10"

        # 4. POST /api/ocr/phieu-cu
        conn.request(
            "POST",
            "/api/ocr/phieu-cu",
            body=json.dumps({"text": "Creatinin: 210 umol/L, Glucophage 850mg ngày 2 viên", "tuoi": 72}),
            headers={"Content-Type": "application/json", "X-MediTrace-Internal-Token": "khoa-thu"},
        )
        r_ocr = conn.getresponse()
        d_ocr = json.loads(r_ocr.read().decode("utf-8"))
        assert r_ocr.status == 200
        assert validate_contract_keys(d_ocr, "PyOcrPhieuCuResponse") == []
        assert d_ocr["hieu_chinh_lieu"]["co_canh_bao_critical"] is True
        conn.close()
    finally:
        server.shutdown()
        server.server_close()


def test_p1_contextual_trie_600_anh_xa_hai_chieu_va_hotwords_chuyen_khoa():
    assert chuan_hoa_he_co_quan("tim mạch") == "tim_mach"
    assert chuan_hoa_he_co_quan("tiêu hoá") == "tieu_hoa"
    assert chuan_hoa_he_co_quan("tiêu hóa") == "tieu_hoa"
    assert chuan_hoa_he_co_quan("nội tiết - chuyển hoá") == "noi_tiet_chuyen_hoa"
    assert chuan_hoa_he_co_quan("thận - tiết niệu") == "than_tiet_nieu"
    assert chuan_hoa_he_co_quan("mắt") == "mat_nhan_khoa"
    assert ten_he_co_quan_tieng_viet("tim_mach") == "tim mạch"

    trie = tao_trie_600_mac_dinh()
    # Chỉ mục hệ cơ quan nạp từ `kho_khuon` phải có thực thể thật (trước đây rỗng 0 do lệch dấu tiếng Việt!)
    assert len(trie.chi_muc_he_co_quan["tim_mach"]) > 10
    assert len(trie.chi_muc_he_co_quan["ho_hap"]) > 10
    assert len(trie.chi_muc_he_co_quan["tieu_hoa"]) > 10

    # Hotwords tim mạch khác hẳn hotwords hô hấp, và nhãn có dấu / snake_case cho kết quả đồng nhất
    hw_tim_vi = trie.xuat_hotwords(he_co_quan="tim mạch", max_terms=40)
    hw_tim_ma = trie.xuat_hotwords(he_co_quan="tim_mach", max_terms=40)
    hw_hohap = trie.xuat_hotwords(he_co_quan="ho_hap", max_terms=40)
    assert hw_tim_vi == hw_tim_ma
    assert hw_tim_ma != hw_hohap

    # Kiểm tra buoc_trie ưu tiên đúng hệ cơ quan kể cả khi truyền nhãn tiếng Việt có dấu
    trie_nho = ContextualPrefixTrie600()
    trie_nho.nap_khuon_benh([
        {"ten": "suy tim", "he_co_quan": "tim mạch", "chinh": ["khó thở"], "phu": []},
    ])
    _, n1 = trie_nho.buoc_trie(trie_nho.root, "suy")
    diem_dung_khoa, _ = trie_nho.buoc_trie(n1, "tim", he_co_quan_uu_tien="tim mạch")
    diem_khac_khoa, _ = trie_nho.buoc_trie(n1, "tim", he_co_quan_uu_tien="hô hấp")
    assert diem_dung_khoa > diem_khac_khoa


def test_p1_thong_nhat_danh_muc_thuoc_sintrom_chu_e_cuoi_biet_duoc_va_khoa_co_dia():
    # 1. Aho-Corasick: Sintrom -> acenocoumarol (tách biệt với Coumadin -> warfarin)
    aho = BoTraCuuDuocThuAhoCorasick()
    kq_sintrom = aho.nhan_dien_thuoc_trong_van_ban("Bệnh nhân đang uống Sintrom 4mg và Coumadin 5mg")
    hc_map = {m["tu_khoa_khop"].lower(): m["hoat_chat"] for m in kq_sintrom}
    assert hc_map["sintrom"] == "acenocoumarol"
    assert hc_map["coumadin"] == "warfarin"

    # 2. DDI với biệt dược & biến thể chữ 'e' cuối trong duoc_ly_lam_sang
    assert ClinicalPharmacovigilanceEngine.kiem_tra_tuong_tac(["Losec 20mg", "Plavix 75mg"])
    assert ClinicalPharmacovigilanceEngine.kiem_tra_tuong_tac(["omeprazol 20mg", "clopidogrel 75mg"])
    assert ClinicalPharmacovigilanceEngine.kiem_tra_tuong_tac(["spironolacton 25mg", "enalapril 5mg"])
    assert ClinicalPharmacovigilanceEngine.kiem_tra_tuong_tac(["Sintrom 4mg", "Aspirin 81mg"])
    assert ClinicalPharmacovigilanceEngine.kiem_tra_tuong_tac(["Coumadin 5mg", "Aspirin 81mg"])
    assert ClinicalPharmacovigilanceEngine.kiem_tra_tuong_tac(["Cordarone 200mg", "Digoxin 0.125mg"])

    # 3. Hỗ trợ cả khóa `benh_nen` lẫn `tien_su_benh`
    cd_benh_nen = ClinicalPharmacovigilanceEngine.kiem_tra_co_dia_chong_chi_dinh(
        ["Propranolol 40mg"], {"benh_nen": ["hen phế quản"]}
    )
    cd_tien_su = ClinicalPharmacovigilanceEngine.kiem_tra_co_dia_chong_chi_dinh(
        ["Propranolol 40mg"], {"tien_su_benh": ["hen phế quản"]}
    )
    assert len(cd_benh_nen) == 1 and len(cd_tien_su) == 1

    # 4. Hiệu chỉnh liều: chữ 'e' cuối, biệt dược & hỗ trợ cả `can_nang` lẫn `can_nang_kg`
    hc_1 = kiem_tra_hieu_chinh_lieu(
        danh_sach_thuoc=["Spironolacton 25mg", "Amlodipin 5mg", "Sintrom 4mg", "Coumadin 5mg", "Lipitor 20mg"],
        ket_qua_xet_nghiem={"creatinine": 2.4},
        thong_tin_benh_nhan={"tuoi": 70, "can_nang": 55.0, "gioi_tinh": "nữ", "benh_nen": ["xơ gan"]},
    )
    assert hc_1["chuc_nang_than"]["crcl_cockcroft_gault"] is not None
    assert hc_1["co_canh_bao_critical"] is True
    assert any("Spironolacton" in c["thuoc"] for c in hc_1["canh_bao_hieu_chinh_than"])
    assert any("Statin" in c["thuoc"] for c in hc_1["canh_bao_hieu_chinh_gan"])
    tp_thuoc = [c["thuoc"] for c in hc_1["huong_dan_tuong_tac_thuc_pham"]]
    assert any("Amlodipine" in t for t in tp_thuoc)
    assert any("Sintrom" in t for t in tp_thuoc)
    assert any("Coumadin" in t for t in tp_thuoc)


# ==============================================================================
# 5. ADVERSARIAL EDGE-CASE REGRESSIONS (REVIEW HARDENING)
# ==============================================================================
def test_review_fhir_di_ung_hon_hop_va_phu_dinh_don_le():
    # Câu hỗn hợp vừa phủ định thức ăn vừa khẳng định dị ứng thuốc KHÔNG BAO GIỜ được bỏ sót AllergyIntolerance!
    mixed_cases = (
        "không dị ứng thức ăn hay hải sản gì cả chỉ nổi mề đay với ceftriaxone",
        "Không dị ứng thức ăn, có dị ứng Penicillin",
        "Không dị ứng thuốc, nổi mề đay khi ăn hải sản",
        "Không dị ứng gì trừ aspirin",
    )
    for cau in mixed_cases:
        b_mix = FHIRExporter.xuat_fhir_bundle("ca_mix", {"CHẨN ĐOÁN": "Viêm phổi", "DỊ ỨNG": cau})
        al_mix = [e["resource"] for e in b_mix["entry"] if e["resource"]["resourceType"] == "AllergyIntolerance"]
        assert len(al_mix) == 1, f"Bỏ sót dị ứng hỗn hợp: {cau}"
        assert al_mix[0]["criticality"] == "high"

    # Phủ định đơn lẻ hoặc liệt kê danh mục dưới cùng một từ phủ định -> KHÔNG tạo AllergyIntolerance
    neg_cases = ("Không", "Không có", "Âm tính", "Không dị ứng thuốc, thức ăn, hải sản", "Chưa từng thấy bị dị ứng thuốc")
    for cau_neg in neg_cases:
        b_neg = FHIRExporter.xuat_fhir_bundle("ca_neg", {"CHẨN ĐOÁN": "Viêm họng", "DỊ ỨNG": cau_neg})
        al_neg = [e["resource"] for e in b_neg["entry"] if e["resource"]["resourceType"] == "AllergyIntolerance"]
        assert al_neg == [], f"Tạo nhầm AllergyIntolerance cho phủ định: {cau_neg}"


def test_review_khu_dinh_danh_ten_don_khong_pha_tu_ghep_lam_sang_va_ten_1_ky_tu():
    # Tên đơn 'Bình', 'An', 'Tâm' không bao giờ được làm hỏng 'bình thường', 'Bình thường', 'thuốc an thần', 'An toàn', 'điện tâm đồ'
    vb_binh = "Bác sĩ: Chào bác Bình, tim phổi bình thường. Bình thường không đau ngực."
    kq_binh = ClinicalDeidentifier.an_danh_van_ban(vb_binh, ten_benh_nhan="Bình")
    assert "Chào bác [BENH_NHAN]," in kq_binh.van_ban_da_an_danh
    assert "tim phổi bình thường" in kq_binh.van_ban_da_an_danh
    assert "Bình thường không đau ngực" in kq_binh.van_ban_da_an_danh

    vb_an = "Tôi tên là An. Bệnh nhân dùng thuốc an thần, An toàn khi điều trị ngoại trú."
    kq_an = ClinicalDeidentifier.an_danh_van_ban(vb_an)
    assert "Tôi tên là [HO_TEN_1]." in kq_an.van_ban_da_an_danh
    assert "thuốc an thần" in kq_an.van_ban_da_an_danh
    assert "An toàn khi điều trị" in kq_an.van_ban_da_an_danh

    vb_tam = "Bệnh nhân Tâm cần đo điện tâm đồ, huyết áp tâm thu ổn định."
    kq_tam = ClinicalDeidentifier.an_danh_van_ban(vb_tam, ten_benh_nhan="Tâm")
    assert "Bệnh nhân [BENH_NHAN] cần" in kq_tam.van_ban_da_an_danh
    assert "điện tâm đồ" in kq_tam.van_ban_da_an_danh
    assert "huyết áp tâm thu" in kq_tam.van_ban_da_an_danh

    # Tên có chữ cái đơn 'Nguyễn Thị Ý' / 'TRẦN THỊ Ý' bắt trọn vẹn không rớt chữ 'Ý'
    kq_y = ClinicalDeidentifier.an_danh_van_ban("Tôi tên là Nguyễn Thị Ý năm nay ba mươi tuổi bị ho khan")
    assert "Nguyễn Thị Ý" not in kq_y.van_ban_da_an_danh
    assert "[HO_TEN_1] năm nay ba mươi tuổi bị ho khan" in kq_y.van_ban_da_an_danh
    kq_y_hoa = ClinicalDeidentifier.an_danh_van_ban("Họ tên: TRẦN THỊ Ý năm nay bốn mươi tuổi đau đầu")
    assert "[HO_TEN_1] năm nay bốn mươi tuổi đau đầu" in kq_y_hoa.van_ban_da_an_danh


def test_review_hoi_lai_phu_dinh_di_ung_va_khong_ghi_de_nguoi_nha():
    p_bn = PhatBieu(id=1, nguoi_noi="người nhà", chu_the_id=0, noi_dung="dị ứng penicillin", do_chac_chan="chưa ghi nhận", bang_chung=[1])
    p_me = PhatBieu(id=2, nguoi_noi="người nhà", chu_the_id=1, ten_chu_the="mẹ", noi_dung="dị ứng penicillin", bang_chung=[1])
    ch = hoi_lai.CauHoi(van="Đã từng dùng chưa?", ly_do="di_ung_chua_ghi_nhan", muc_tieu={1: 1.0, 2: 0.9})

    # 'Không bị dị ứng' tuyệt đối phải mang phu_dinh=True, không được rơi nhầm vào nhánh khẳng định dị ứng!
    hoi_lai.ap_dung_tra_loi(p_bn, ch, "Không bị dị ứng")
    assert p_bn.do_chac_chan == "chắc chắn" and p_bn.phu_dinh is True

    # 'Chưa từng bị dị ứng' phải giữ 'chưa ghi nhận', phu_dinh=False
    hoi_lai.ap_dung_tra_loi(p_bn, ch, "Chưa từng bị dị ứng")
    assert p_bn.do_chac_chan == "chưa ghi nhận" and p_bn.phu_dinh is False

    # Không bao giờ ghi đè dị ứng của người nhà (chu_the_id == 1)
    hoi_lai.ap_dung_tra_loi(p_me, ch, "Đã từng dùng an toàn")
    assert p_me.phu_dinh is False and p_me.do_chac_chan == "chắc chắn"


def test_review_bhyt_chu_the_nhi_esomeprazol_va_xml5_stt():
    # Chủ thể 'cháu' trong ca nhi phải được hiểu là bệnh nhân chính (chu_the_id == 0)
    kq_nhi = tien_kiem_bhyt_tu_du_lieu(
        [
            {"id": 1, "chu_the": "mẹ", "text": "Tăng huyết áp"},
            {"id": 2, "chu_the": "cháu", "nguoi_noi": "bác sĩ", "text": "Viêm phế quản cấp"},
        ],
        "Bác sĩ khám cháu bị viêm phế quản cấp, mẹ tăng huyết áp.",
    )
    assert kq_nhi["ma_icd10_chinh"]["ma_icd10"] == "J20.9"
    # STT trong XML5_DIEN_BIEN_LS liên tục từ 1 dù mệnh đề đầu tiên là của mẹ
    xml5_list = kq_nhi["bang_xml_130_4750"]["XML5_DIEN_BIEN_LS"]
    assert len(xml5_list) == 1 and xml5_list[0]["STT"] == 1

    # Esomeprazol không bị nhân đôi cảnh báo với Omeprazol
    ps_eso = [
        PhatBieu(id=1, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="viêm họng cấp", hanh_vi="nhận định", bang_chung=[1]),
        PhatBieu(id=2, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="Esomeprazole 40mg", hanh_vi="kế hoạch", bang_chung=[1]),
    ]
    bhyt_eso = BHYTXmlPreChecker.kiem_duyet_ho_so("ca_eso", ps_eso, "Viêm họng cấp, kê Esomeprazole 40mg")
    assert len(bhyt_eso.canh_bao_xuat_toan_bhyt) == 1
    assert "Esomeprazol" in bhyt_eso.canh_bao_xuat_toan_bhyt[0]


def test_review_trie_chi_muc_2_chieu_hotwords_sach_va_orchestrator_cls_gop():
    trie = tao_trie_600_mac_dinh()
    # Tra cứu trực tiếp trên chi_muc_he_co_quan bằng nhãn tiếng Việt có dấu hoạt động 100%
    assert trie.chi_muc_he_co_quan["tim mạch"] == trie.chi_muc_he_co_quan["tim_mach"]
    assert trie.chi_muc_he_co_quan.get("tiêu hoá") == trie.chi_muc_he_co_quan["tieu_hoa"]
    assert "hô hấp" in trie.chi_muc_he_co_quan
    assert len(trie.chi_muc_he_co_quan["ung_buou"]) >= 1

    # Hotwords gọn sạch, ưu tiên nhiều tên bệnh + thuốc đặc trưng tim mạch (losartan, atorvastatin, warfarin...)
    hw_tm = trie.xuat_hotwords("tim mạch", max_terms=40)
    items_tm = [x.strip() for x in hw_tm.split(",") if x.strip()]
    assert all("." not in it and ";" not in it for it in items_tm)
    assert any("suy tim" in it.lower() or "rung nhĩ" in it.lower() or "tăng huyết áp" in it.lower() for it in items_tm)
    assert any(d in hw_tm.lower() for d in ("amlodipin", "losartan", "atorvastatin", "warfarin"))

    # Biệt dược chính thống 'Hapacol'/'Panadol' không bị gắn nhầm lỗi ASR âm vị dân gian
    res_hapacol = ASRQualityGuardrail.kiem_tra_phien_am("Mẹ cho bé uống 1 gói Hapacol 250mg và viên Panadol")
    assert res_hapacol.hop_le is True
    assert res_hapacol.goi_y_thuoc == {}

    # _trich_danh_sach_thuoc_hop_le loại bỏ 'phát ban khi uống amoxicillin' và 'chưa ghi nhận'
    ps_allergy = [
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="phát ban khi uống amoxicillin", bang_chung=[1]),
        PhatBieu(id=2, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dùng warfarin", do_chac_chan="chưa ghi nhận", bang_chung=[1]),
    ]
    assert _trich_danh_sach_thuoc_hop_le(ps_allergy) == []

    # Orchestrator hợp nhất cả thong_tin_benh_nhan["xet_nghiem"] và du_lieu_xet_nghiem cho Chốt 6 & Chốt 7
    ps_met = [PhatBieu(id=1, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="Metformin 850mg", thuoc={"ten": "Metformin"}, bang_chung=[1], trich_dan=["Metformin 850mg"])]
    kq_orch = MediTracePipelineOrchestrator.xu_ly_ca_kham(
        "ca_gop_xn",
        "Bác sĩ: Duy trì Metformin 850mg.",
        ps_met,
        thong_tin_benh_nhan={"tuoi": 70, "xet_nghiem": {"egfr": 22.0}},
        du_lieu_xet_nghiem={"troponin": "0,0"},
    )
    assert kq_orch.hieu_chinh_lieu["co_canh_bao_critical"] is True
    assert any(c.ma_xet_nghiem == "TROPONIN" and c.gia_tri == 0.0 for c in kq_orch.doi_soat_can_lam_sang.danh_sach_chi_so)


def test_review_http_query_rong_khong_loi_500_va_asr_infer_lock():
    assert hasattr(phowhisper_provider, "_INFER_LOCK")
    assert hasattr(faster_whisper_provider, "_INFER_LOCK")
    am = dich_vu.AmThanh()
    assert hasattr(am, "_khoa_suy_luan")

    class _MayQueryTest(dich_vu.May):
        loi = dich_vu.Loi(cho_nap_mo_hinh=False)
        am = dich_vu.AmThanh()
        def log_message(self, *args):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), _MayQueryTest)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        for path in ("/api/suc-khoe?", "/api/suc-khoe?ping"):
            conn.request("GET", path)
            r = conn.getresponse()
            body = json.loads(r.read().decode("utf-8"))
            assert r.status == 200 and body["ok"] is True, path
        conn.close()
    finally:
        srv.shutdown()
        srv.server_close()
