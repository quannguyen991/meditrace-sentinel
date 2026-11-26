# -*- coding: utf-8 -*-
"""Kiểm thử toàn diện Phần A (6 lỗ hổng) & Phần B (các trục nâng cấp chuyên sâu)."""
from __future__ import annotations

import http.client
import json
import threading
import xml.etree.ElementTree as ET
from pathlib import Path

from src.audio.asr.contextual_trie_600 import ContextualPrefixTrie600
from src.audio.asr.faster_whisper_provider import FasterWhisperProvider
from src.audio.pipeline import goi_y_vai_nguoi_noi
from src.audio.sim2real_v2 import (
    danh_gia_sim2real_va_trie_600,
    do_duong_cong_do_ben_nhieu_asr,
    tinh_chi_so_alert_fatigue,
)
from src.can_lam_sang import ParaclinicalCorrelator
from src.chuan_hoa_don_vi_xet_nghiem import (
    chuan_hoa_creatinine,
    chuan_hoa_du_lieu_xet_nghiem,
    chuan_hoa_glucose,
    chuan_hoa_urea,
)
from src.dich_vu import AmThanh, Loi, May, _them_canh_bao
from src.dieu_phoi_ha_tang import MediTracePipelineOrchestrator, _trich_danh_sach_thuoc_hop_le
from src.duoc_ly_lam_sang import ClinicalPharmacovigilanceEngine
from src.fhir_exporter import FHIRExporter
from src.guardrails import ASRQualityGuardrail, tao_khoa_am_vi_vung_mien
from src.hieu_chinh_lieu import kiem_tra_hieu_chinh_lieu
from src.khu_dinh_danh import ClinicalDeidentifier
from src.kiem_duyet_bhyt_va_bo_sot import BHYTXmlPreChecker, xuat_goi_xml_1_5_qd130
from src.ocr_lam_sang import boc_tach_phieu_cu
from src.phat_bieu import PhatBieu
from src.worm_audit_log import WormAuditLogger


# ==============================================================================
# A1: Nối thong_tin_benh_nhan & du_lieu_xet_nghiem vào _them_canh_bao (Chốt 6 & 7)
# ==============================================================================
def test_a1_them_canh_bao_kich_hoat_chot_6_va_7():
    ban_ghi = {
        "id": "ca_a1",
        "input": "Bác sĩ: Bệnh nhân sốt cao, viêm phổi, đang dùng Metformin.\nBệnh nhân: Dạ tôi có tiền sử tiểu đường.",
        "phat_bieu": [
            {
                "id": 1,
                "nguoi_noi": "bác sĩ",
                "chu_the_id": 0,
                "noi_dung": "viêm phổi",
                "hanh_vi": "nhận định",
                "bang_chung": [1],
                "trich_dan": ["viêm phổi"],
            },
            {
                "id": 2,
                "nguoi_noi": "bác sĩ",
                "chu_the_id": 0,
                "noi_dung": "Metformin 850mg",
                "thuoc": {"ten": "Metformin", "lieu": "850 mg", "trang_thai_dung": "đang dùng"},
                "bang_chung": [1],
                "trich_dan": ["đang dùng Metformin"],
            },
        ],
    }
    kq = _them_canh_bao(
        ban_ghi,
        thong_tin_benh_nhan={"tuoi": 70, "la_nu": False},
        du_lieu_xet_nghiem={"creatinine": 220.0, "wbc": 16.5, "urea": 10.2},
    )
    ls = kq["lam_sang_nang_cao"]
    assert ls["doi_soat_can_lam_sang"] is not None
    assert "CURB-65" in ls["thang_diem_nguy_co"]
    assert ls["hieu_chinh_lieu"]["co_canh_bao_critical"] is True
    assert "goi_xml_1_5" in ls
    assert "<MA_LK>ca_a1</MA_LK>" in ls["goi_xml_1_5"]["XML1"]


# ==============================================================================
# A2: Bộ lọc thuốc trong dieu_phoi_ha_tang.py
# ==============================================================================
def test_a2_loc_thuoc_hop_le():
    ps = [
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="đang uống thuốc Amlodipin 5mg",
                 thuoc={"ten": "Amlodipin", "trang_thai_dung": "đang dùng"}, bang_chung=[1]),
        PhatBieu(id=2, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="kê thêm Losartan 50mg",
                 hanh_vi="kế hoạch", thuoc={"ten": "Losartan", "trang_thai_dung": "được kê, chưa dùng"}, bang_chung=[2]),
        # Các trường hợp phải loại bỏ:
        PhatBieu(id=3, nguoi_noi="người nhà", chu_the_id=1, noi_dung="mẹ tôi uống Warfarin",
                 thuoc={"ten": "Warfarin", "trang_thai_dung": "đang dùng"}, bang_chung=[3]),
        PhatBieu(id=4, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="không dùng Aspirin",
                 phu_dinh=True, thuoc={"ten": "Aspirin", "trang_thai_dung": "đang dùng"}, bang_chung=[4]),
        PhatBieu(id=5, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="uống Ibuprofen",
                 trang_thai="bị thay thế", thuoc={"ten": "Ibuprofen", "trang_thai_dung": "đang dùng"}, bang_chung=[5]),
        PhatBieu(id=6, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="đã ngừng Simvastatin 2 tuần",
                 thuoc={"ten": "Simvastatin", "trang_thai_dung": "đã ngừng"}, bang_chung=[6]),
    ]
    thuoc = _trich_danh_sach_thuoc_hop_le(ps)
    assert thuoc == ["Amlodipin", "Losartan"]


# ==============================================================================
# A3: Canonical Lab Unit Normalizer
# ==============================================================================
def test_a3_chuan_hoa_don_vi_xet_nghiem():
    c1 = chuan_hoa_creatinine(165, "µmol/L")
    c2 = chuan_hoa_creatinine(1.87, "mg/dL")
    assert c1 is not None and c2 is not None
    assert abs(c1["mg_dl"] - 1.87) <= 0.02
    assert abs(c2["umol_l"] - 165.3) <= 1.0

    g1 = chuan_hoa_glucose(10.0, "mmol/L")
    g2 = chuan_hoa_glucose(180.2, "mg/dL")
    assert g1 is not None and g2 is not None
    assert abs(g1["mg_dl"] - 180.2) <= 0.5
    assert abs(g2["mmol_l"] - 10.0) <= 0.1

    u1 = chuan_hoa_urea(12.0, "mmol/L")
    u2 = chuan_hoa_urea(72.07, "mg/dL", la_bun=False)
    u3 = chuan_hoa_urea(33.61, "mg/dL", la_bun=True)
    assert u1 and u2 and u3
    assert abs(u2["mmol_l"] - 12.0) <= 0.1
    assert abs(u3["mmol_l"] - 12.0) <= 0.1

    # Kiểm tra tích hợp ParaclinicalCorrelator nhận creatinine mg/dL vẫn bắt đúng TANG_CAO (>115 umol/L)
    cls_res = ParaclinicalCorrelator.phan_tich_xet_nghiem({"creatinine": 2.0, "glucose": 25.0, "glucose_unit": "mmol/L"})
    by_code = {c.ma_xet_nghiem: c for c in cls_res.danh_sach_chi_so}
    assert by_code["CREATININE"].trang_thai == "TANG_CAO"
    assert by_code["GLUCOSE"].trang_thai == "NGUY_KICH"

    # Kiểm tra OCR & FHIR Exporter thống nhất đơn vị
    ocr_res = boc_tach_phieu_cu("Creatinin 165 umol/L, Glucose 180 mg/dL, Ure 12 mmol/L", tuoi=65)
    assert abs(ocr_res["chi_so"]["creatinine"] - 1.87) <= 0.02
    assert abs(ocr_res["chi_so"]["glucose_mmol_l"] - 10.0) <= 0.1
    assert abs(ocr_res["chi_so"]["urea_mmol_l"] - 12.0) <= 0.1

    bundle = FHIRExporter.xuat_fhir_bundle(
        "ca_a3",
        {"CHẨN ĐOÁN": "Đái tháo đường"},
        thong_tin_benh_nhan={"id": "bn1", "creatinine": 165, "glucose": 10.0},
    )
    obs = [e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Observation"]
    creat_obs = next(o for o in obs if o["code"]["coding"][0]["code"] == "2160-0")
    glu_obs = next(o for o in obs if o["code"]["coding"][0]["code"] == "1558-6")
    assert abs(creat_obs["valueQuantity"]["value"] - 1.87) <= 0.02
    assert abs(glu_obs["valueQuantity"]["value"] - 180.2) <= 0.5


# ==============================================================================
# A4: De-identification (địa chỉ có dấu phẩy + Spoken-Number Normalizer + _ho_so_xa)
# ==============================================================================
def test_a4_khu_dinh_danh_va_so_noi():
    vb = (
        "Bệnh nhân địa chỉ: 123 Nguyễn Trãi, phường 5, quận 5, TP HCM. "
        "Số điện thoại không chín tám bảy sáu năm bốn ba hai một. "
        "Bệnh nhân uống hai viên thuốc mỗi ngày trong ba ngày."
    )
    kq = ClinicalDeidentifier.an_danh_van_ban(vb)
    assert "Nguyễn Trãi" not in kq.van_ban_da_an_danh
    assert "quận 5" not in kq.van_ban_da_an_danh
    assert "0987654321" not in kq.van_ban_da_an_danh
    assert "[SDT_1]" in kq.van_ban_da_an_danh
    assert "[DIA_CHI_1]" in kq.van_ban_da_an_danh
    # Không làm hỏng số đếm lâm sàng ngắn
    assert "hai viên" in kq.van_ban_da_an_danh
    assert "ba ngày" in kq.van_ban_da_an_danh


def test_a4_an_danh_truoc_khi_gui_ho_so_xa():
    loi = Loi(cho_nap_mo_hinh=False, mo_hinh_xa="http://127.0.0.1:9999")
    loi._dem = {}
    loi._dem_theo_chu = {}
    da_gui = {}

    def fake_ho_so_xa(ca_id, hoi_thoai, nhanh, metadata=None):
        da_gui["text"] = hoi_thoai
        return {"id": ca_id, "input": hoi_thoai, "phat_bieu": [], "du_doan": hoi_thoai}

    loi._ho_so_xa = fake_ho_so_xa
    res = loi.ho_so("ca_xa_1", "Bệnh nhân tên là Trần Văn Bình, SĐT 0912345678 bị đau đầu.", "C_khoa")
    assert "0912345678" not in da_gui["text"]
    assert "Trần Văn Bình" not in da_gui["text"]
    assert res["da_khu_dinh_danh_truoc_gui_xa"] is True
    assert res["so_pii_da_chan"] >= 1


# ==============================================================================
# A5: Nhãn mô phỏng + Đường cong WER/CHWER + Alert Fatigue
# ==============================================================================
def test_a5_sim2real_label_wer_chwer_va_alert_fatigue():
    trie = ContextualPrefixTrie600()
    trie.nap_duoc_thu_va_g2p({"metformin": ["mét pho min"]})
    sim = danh_gia_sim2real_va_trie_600([{"dap_an": [{"thuoc": {"ten": "metformin"}}]}], trie)
    assert sim.la_mo_phong is True
    assert sim.nguon_du_lieu == "MO_PHONG_MONTE_CARLO"

    mau = [
        {
            "transcript_chuan": "Bệnh nhân uống metformin 500mg mỗi ngày",
            "hyp_theo_snr": {
                25.0: "Bệnh nhân uống metformin 500mg mỗi ngày",
                5.0: "Bệnh nhân uống mét pho min 500mg mỗi ngày",
            },
        }
    ]
    curve = do_duong_cong_do_ben_nhieu_asr(mau, muc_snr_db_list=(25.0, 5.0))
    assert len(curve) == 2
    assert curve[0]["wer_trung_binh"] == 0.0
    assert curve[1]["wer_trung_binh"] > 0.0
    assert curve[0]["la_mo_phong"] is False

    af = tinh_chi_so_alert_fatigue([
        {"tong_menh_de": 10, "so_can_xac_nhan": 2, "so_giu": 3, "so_sua": 1, "so_bo": 1},
        {"tong_menh_de": 10, "so_can_xac_nhan": 3, "so_giu": 4, "so_sua": 0, "so_bo": 1},
    ])
    assert af["tong_menh_de"] == 20
    assert af["so_can_xac_nhan"] == 5
    assert af["ty_le_can_xac_nhan"] == 0.25
    assert af["override_rate"] == 0.2
    assert af["ppv"] == 0.8


# ==============================================================================
# A6: WormAuditLogger thread-safe
# ==============================================================================
def test_a6_worm_audit_logger_da_luong(tmp_path: Path):
    db_path = tmp_path / "worm_thread_test.db"
    logger = WormAuditLogger(db_path=db_path)
    errors = []

    def worker(tid: int):
        try:
            for i in range(10):
                logger.append_event(
                    user_id=f"bs_{tid}",
                    action="SIGN_OFF",
                    case_id=f"case_{tid}_{i}",
                    payload={"i": i},
                )
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors
    ok, count, _ = logger.verify_chain()
    assert ok is True
    assert count == 40
    logger.close()


# ==============================================================================
# B1: Trie600 -> FasterWhisperProvider, Biến âm 3 miền, Gợi ý vai người nói
# ==============================================================================
def test_b1_trie_hotwords_bien_am_va_goi_y_vai():
    prov = FasterWhisperProvider()
    assert prov.hotwords is not None and len(prov.hotwords) > 0
    prov_empty = FasterWhisperProvider(hotwords="")
    assert prov_empty.hotwords == ""

    res_g = ASRQualityGuardrail.kiem_tra_phien_am("Bệnh nhân bị xốt cao, lôn mửa, giãn tỉnh mạch")
    assert "xốt" in res_g.goi_y
    assert res_g.goi_y["xốt"] == "sốt"
    assert res_g.goi_y["lôn mửa"] == "nôn mửa"
    assert tao_khoa_am_vi_vung_mien("lặng tróng xốt ngã") == tao_khoa_am_vi_vung_mien("nặng chóng sốt ngả")

    segs = [
        {"segment_id": "s1", "text_original": "Chào bác, bác đau ở đâu?", "speaker_role": "unknown"},
        {"segment_id": "s2", "text_original": "Bác sĩ ơi tôi bị đau đầu quá", "speaker_role": "unknown"},
    ]
    goi_y_vai_nguoi_noi(segs)
    assert segs[0]["suggested_role"] == "doctor"
    assert segs[1]["suggested_role"] == "patient"
    assert segs[0]["speaker_role"] == "unknown"


# ==============================================================================
# B2: Polypharmacy Burden & ATC Duplication Engine
# ==============================================================================
def test_b2_trung_nhom_atc_va_cong_don_nguy_co():
    thuoc = ["Ibuprofen", "Meloxicam", "Omeprazol", "Esomeprazol", "Spironolacton", "Enalapril"]
    kq = ClinicalPharmacovigilanceEngine.kiem_duyet_toan_dien(thuoc)
    assert kq.hop_le is False
    atc = kq.ganh_nang_da_thuoc["trung_nhom_atc"]
    assert "NSAID (M01A)" in atc
    assert "PPI (A02BC)" in atc
    assert kq.ganh_nang_da_thuoc["polypharmacy"] is True
    assert len(kq.ganh_nang_da_thuoc["thuoc_tang_kali"]) >= 2


# ==============================================================================
# B3: XML1-XML5 (QĐ 130/4750/QĐ-BYT) & HTTP Persistent endpoints trên dich_vu.py
# ==============================================================================
def test_b3_xuat_xml_1_5_va_http_persistent():
    ps = [
        PhatBieu(id=1, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="Tăng huyết áp & đái tháo đường",
                 hanh_vi="nhận định", bang_chung=[1]),
        PhatBieu(id=2, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="Amlodipin 5mg",
                 hanh_vi="kế hoạch", thuoc={"ten": "Amlodipin", "lieu": "5mg"}, bang_chung=[1]),
    ]
    bhyt = BHYTXmlPreChecker.kiem_duyet_ho_so("ca_xml", ps, "Tăng huyết áp, kê Amlodipin 5mg")
    xml_pack = xuat_goi_xml_1_5_qd130("ca_xml", bhyt, ps, {"id": "BN1", "xet_nghiem": {"glucose": 7.8}})
    for key in ("XML1", "XML2", "XML3", "XML4", "XML5"):
        ET.fromstring(xml_pack[key])  # Parse XML hợp lệ

    # Kiểm tra endpoint HTTP persistent trên dich_vu.May
    from http.server import ThreadingHTTPServer

    class _MayTest(May):
        loi = Loi(cho_nap_mo_hinh=False)
        khoa_noi_bo = "khoa-thu"  # dich vu doi khoa noi bo cho moi /api tru suc-khoe
        am = AmThanh()
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), _MayTest)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    try:
        conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        conn.request(
            "POST",
            "/api/ocr/phieu-cu",
            body=json.dumps({"text": "Creatinin 165 umol/L, Metformin 850mg", "tuoi": 68}),
            headers={"Content-Type": "application/json", "X-MediTrace-Internal-Token": "khoa-thu"},
        )
        r1 = conn.getresponse()
        d1 = json.loads(r1.read().decode("utf-8"))
        assert r1.status == 200
        assert d1["chi_so"]["creatinine_umol_l"] == 165.0

        conn.request(
            "POST",
            "/api/bhyt/precheck",
            body=json.dumps({"propositions": [{"id": 1, "text": "Tăng huyết áp"}], "transcript": "Tăng huyết áp"}),
            headers={"Content-Type": "application/json", "X-MediTrace-Internal-Token": "khoa-thu"},
        )
        r2 = conn.getresponse()
        d2 = json.loads(r2.read().decode("utf-8"))
        assert r2.status == 200
        assert "goi_xml_1_5" in d2
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
