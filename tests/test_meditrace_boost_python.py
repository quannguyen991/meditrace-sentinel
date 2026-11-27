# -*- coding: utf-8 -*-
"""Bộ kiểm thử toàn diện cho MediTrace Boost Python Core (Boost 1, 2, 5, 6, 8, 9, 10, 12)."""
from __future__ import annotations

import http.client
import json
import math
import struct
import subprocess
import sys
import threading
import types
import wave
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from src.huan_luyen import chon_mo_hinh_bakeoff as bakeoff
from src.he_thong import dich_vu_http as dich_vu
from src.duong_ong import chay_duong_ong as nhanh
from src.audio.asr import phowhisper_provider as pw
from src.audio.asr.contextual_trie_600 import ContextualPrefixTrie600, tao_trie_600_mac_dinh
from src.audio.pipeline import (
    goi_y_vai_nguoi_noi,
    khop_mau_giong_bac_si,
    trich_dac_trung_giong_nhe,
)
from src.cong_cu_lam_sang.cam_doan_thu_thuat import co_dau_hieu_thu_thuat, kiem_chung_cam_doan_thu_thuat
from src.cong_cu_lam_sang.di_buong_noi_tru import tong_hop_to_dieu_tri_noi_tru
from src.cong_cu_lam_sang.tien_kiem_bhyt_va_khoi_phuc_bo_sot import (
    BHYTXmlPreChecker,
    QUY_TAC_CHI_DINH_CLS_BHYT,
    doi_soat_da_don_va_don_quoc_gia,
    tien_kiem_bhyt_tu_du_lieu,
    xuat_goi_xml_1_5_qd130,
)
from src.cong_cu_lam_sang.doc_phieu_xet_nghiem import boc_tach_phieu_cu
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu


def _tao_wav_giong_gia(path: Path, f0_hz: float, duration_s: float = 2.0, amp: float = 0.4, sr: int = 16000) -> Path:
    """Sinh sóng hài tổng hợp mô phỏng giọng nói có tần số cơ bản `f0_hz`."""
    n = int(sr * duration_s)
    frames = bytearray()
    for i in range(n):
        t = i / sr
        if f0_hz < 170.0:
            # Âm sắc trầm (nhiều năng lượng dải dưới 450 Hz)
            val = amp * (
                0.70 * math.sin(2 * math.pi * f0_hz * t)
                + 0.25 * math.sin(2 * math.pi * (2 * f0_hz) * t)
                + 0.05 * math.sin(2 * math.pi * (3 * f0_hz) * t)
            )
        else:
            # Âm sắc cao / sáng (nhiều hài bậc cao > 800 Hz)
            val = amp * (
                0.25 * math.sin(2 * math.pi * f0_hz * t)
                + 0.45 * math.sin(2 * math.pi * (3 * f0_hz) * t)
                + 0.30 * math.sin(2 * math.pi * (6 * f0_hz) * t)
            )
        pcm = max(-32767, min(32767, int(val * 32767)))
        frames.extend(struct.pack("<h", pcm))
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(bytes(frames))
    return path


# ===========================================================================
# 1. BOOST 1: NHẬN DIỆN LỜI NGƯỜI NHÀ (`family_member`) & VOICEPRINT BÁC SĨ
# ===========================================================================

def test_boost1_goi_y_vai_nguoi_nha_va_khong_ghi_de_speaker_role():
    segs = [
        {"segment_id": "s1", "speaker_role": "unknown", "text_original": "Chào chị, cháu bị làm sao ạ?"},
        {"segment_id": "s2", "speaker_role": "unknown", "text_original": "Dạ thưa bác sĩ, cháu nhà em bị sốt cao 2 ngày nay."},
        {"segment_id": "s3", "speaker_role": "unknown", "text_original": "Hôm nay nhà em đưa cụ đi khám vì mẹ tôi mệt nhiều."},
        {"segment_id": "s4", "speaker_role": "unknown", "text_original": "Bác sĩ ơi, tôi bị đau ngực quá."},
        {"segment_id": "s5", "speaker_role": "unknown", "text_original": "Chồng em ở nhà uống thuốc huyết áp vẫn đều."},
    ]
    ra = goi_y_vai_nguoi_noi(segs)
    assert ra[0]["suggested_role"] == "doctor"
    assert ra[1]["suggested_role"] == "family_member"
    assert ra[2]["suggested_role"] == "family_member"
    assert ra[3]["suggested_role"] == "patient"
    assert ra[4]["suggested_role"] == "family_member"
    # Bất biến an toàn: không tự động sửa `speaker_role`
    assert all(s["speaker_role"] == "unknown" for s in ra)


def test_boost1_voiceprint_8_chieu_va_khop_mau_giong_bac_si(tmp_path):
    wav_mau_bs = _tao_wav_giong_gia(tmp_path / "mau_bs.wav", f0_hz=120.0, duration_s=5.0, amp=0.5)
    mau_vec = trich_dac_trung_giong_nhe(wav_mau_bs, 0.0, 5.0)
    assert len(mau_vec) == 8
    assert any(abs(v) > 0.01 for v in mau_vec)

    # Tạo đoạn khám gồm 2 giây đầu là giọng bác sĩ (120 Hz, nhỏ tiếng hơn) và 2 giây sau là giọng bệnh nhân (250 Hz)
    sr = 16000
    p1 = tmp_path / "p1.wav"
    p2 = tmp_path / "p2.wav"
    _tao_wav_giong_gia(p1, f0_hz=121.0, duration_s=2.0, amp=0.2, sr=sr)
    _tao_wav_giong_gia(p2, f0_hz=255.0, duration_s=2.0, amp=0.45, sr=sr)
    with wave.open(str(p1), "rb") as r1, wave.open(str(p2), "rb") as r2:
        raw_mix = r1.readframes(r1.getnframes()) + r2.readframes(r2.getnframes())
    wav_phien = tmp_path / "phien.wav"
    with wave.open(str(wav_phien), "wb") as wm:
        wm.setnchannels(1)
        wm.setsampwidth(2)
        wm.setframerate(sr)
        wm.writeframes(raw_mix)

    transcript = [
        {"segment_id": "seg_1", "start_time": 0.1, "end_time": 1.9, "speaker_role": "unknown", "text_original": "Mời bác ngồi."},
        {"segment_id": "seg_2", "start_time": 2.1, "end_time": 3.9, "speaker_role": "unknown", "text_original": "Vâng ạ."},
    ]
    khop_mau_giong_bac_si(transcript, wav_phien, mau_vec, nguong_cosine=0.92)
    assert transcript[0].get("suggested_role") == "doctor"
    assert transcript[0]["doctor_voiceprint_similarity"] >= 0.92
    assert transcript[1].get("suggested_role") != "doctor"
    assert transcript[1]["doctor_voiceprint_similarity"] < 0.92
    assert transcript[0]["speaker_role"] == "unknown"


# ===========================================================================
# 2. BOOST 2: TĂNG TỐC SUY LUẬN (`device_map={"": 0}` + `prompt_lookup_num_tokens`)
# ===========================================================================

def test_boost2_nap_ghim_gpu0_khi_du_vram_va_fallback_auto_khi_oom(monkeypatch):
    goi_device_map = []

    class _FakeModel:
        def eval(self):
            return self

    class _FakeAutoModel:
        @staticmethod
        def from_pretrained(name, **kw):
            goi_device_map.append(kw.get("device_map"))
            if len(goi_device_map) == 2:
                # Lần kiểm thứ 2 giả lập OOM khi ép {"": 0}
                raise RuntimeError("CUDA out of memory")
            return _FakeModel()

    class _FakeAutoTok:
        @staticmethod
        def from_pretrained(name):
            return types.SimpleNamespace(eos_token_id=0)

    class _FakeBnB:
        def __init__(self, **kw):
            self.kw = kw

    fake_torch = types.SimpleNamespace(
        bfloat16="bf16",
        cuda=types.SimpleNamespace(
            is_available=lambda: True,
            mem_get_info=lambda: (int(5.0 * (1024 ** 3)), int(8.0 * (1024 ** 3))),
            OutOfMemoryError=RuntimeError,
            empty_cache=lambda: None,
        ),
    )
    fake_tf = types.SimpleNamespace(
        AutoModelForCausalLM=_FakeAutoModel,
        AutoTokenizer=_FakeAutoTok,
        BitsAndBytesConfig=_FakeBnB,
    )
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setitem(sys.modules, "transformers", fake_tf)
    monkeypatch.setattr(bakeoff, "_ep_json", lambda tok: None)

    # TH1: VRAM trống 5.0 GB >= 3.5 GB -> nạp thẳng lên {"": 0}
    bakeoff.nap("Qwen/Qwen3-4B", ep_json=False)
    assert goi_device_map == [{"": 0}]

    # TH2: Giả lập OOM ở lần gọi đầu của ca thứ 2 -> tự động fallback về "auto"
    bakeoff.nap("Qwen/Qwen3-4B", ep_json=False)
    assert goi_device_map == [{"": 0}, {"": 0}, "auto"]


def test_boost2_prompt_lookup_mac_dinh_5_khi_co_adapter_va_truyen_tu_dich_vu(monkeypatch):
    ghi_kw = []

    class _Tok:
        eos_token_id = 0

        def apply_chat_template(self, msgs, **kw):
            return "prompt"

        def __call__(self, s, return_tensors=None):
            class _D(dict):
                def to(self, _):
                    return self
            return _D(input_ids=types.SimpleNamespace(shape=(1, 1)))

        def decode(self, ids, skip_special_tokens=True):
            return '{"phat_bieu": [{"chu_the": "tôi", "noi_dung": "ho", "do_chac_chan": "chắc chắn", "luot_thoai": [1]}]}'

    class _Model:
        device = "cpu"
        _co_adapter_trich = True

        def generate(self, **kw):
            ghi_kw.append(dict(kw))
            return [[0, 1]]

    class _NoGrad:
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setitem(sys.modules, "torch", types.SimpleNamespace(no_grad=_NoGrad))
    monkeypatch.delenv("MEDITRACE_PROMPT_LOOKUP_TOKENS", raising=False)

    kq = bakeoff.trich(_Tok(), _Model(), prefix_fn=lambda *a: [0], mau_list=[{"id": "c1", "input": "Bệnh nhân: Tôi ho."}])
    assert kq[0]["json_hop_le"] is True
    assert ghi_kw[0].get("prompt_lookup_num_tokens") == 5
    assert ghi_kw[0].get("use_cache") is True


# ===========================================================================
# 3. BOOST 5: KHIÊN BIỆN LUẬN CHỈ ĐỊNH CLS (XML3/XML4 <-> XML5) & NHI KHOA TT26
# ===========================================================================

def test_boost5_du_13_quy_tac_cls_bien_luan_hop_le_va_canh_bao_xuat_toan():
    cac_khoa_bat_buoc = {
        "chụp mri", "cộng hưởng từ", "ct-scan", "cắt lớp vi tính",
        "nội soi dạ dày", "nội soi đại tràng", "troponin", "siêu âm doppler mạch",
        "hba1c", "x-quang ngực", "điện tâm đồ", "crp", "d-dimer",
    }
    assert cac_khoa_bat_buoc <= set(QUY_TAC_CHI_DINH_CLS_BHYT.keys())

    # Ca 1: Có triệu chứng đau thượng vị [T2] -> Nội soi dạ dày hợp lệ, XML3 có DVKT
    ps_hop_le = [
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="đau thượng vị và ợ chua 1 tuần", bang_chung=[2]),
        PhatBieu(id=2, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="viêm dạ dày cấp", hanh_vi="nhận định", bang_chung=[3]),
        PhatBieu(id=3, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="chỉ định nội soi dạ dày", tinh_huong="kế hoạch", hanh_vi="kế hoạch", bang_chung=[4]),
    ]
    kq_ok = BHYTXmlPreChecker.kiem_duyet_ho_so("ca_cls_ok", ps_hop_le, "")
    assert len(kq_ok.bien_luan_chi_dinh_cls) == 1
    bl = kq_ok.bien_luan_chi_dinh_cls[0]
    assert bl["hop_le"] is True
    assert "[T2]" in bl["cau_bien_luan"]
    assert bl["ma_xml"] == "XML3"
    assert not any("XUẤT TOÁN CLS" in c for c in kq_ok.canh_bao_xuat_toan_bhyt)

    goi_xml = xuat_goi_xml_1_5_qd130("ca_cls_ok", kq_ok, ps_hop_le)
    assert "Nội soi thực quản - dạ dày - tá tràng" in goi_xml["XML3"]
    assert "<MA_DICH_VU>03.0001</MA_DICH_VU>" in goi_xml["XML3"]

    # Ca 2: Chỉ viêm họng nhẹ nhưng chỉ định chụp MRI -> Cảnh báo xuất toán CLS XML3/XML5
    ps_thieu = [
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="đau rát họng 2 ngày", bang_chung=[1]),
        PhatBieu(id=2, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="viêm họng cấp", hanh_vi="nhận định", bang_chung=[2]),
        PhatBieu(id=3, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="cho chụp MRI sọ não kiểm tra", tinh_huong="kế hoạch", bang_chung=[3]),
    ]
    kq_loi = BHYTXmlPreChecker.kiem_duyet_ho_so("ca_cls_loi", ps_thieu, "")
    assert len(kq_loi.bien_luan_chi_dinh_cls) == 1
    assert kq_loi.bien_luan_chi_dinh_cls[0]["hop_le"] is False
    assert any("[CẢNH BÁO XUẤT TOÁN CLS - XML3/XML5]" in c for c in kq_loi.canh_bao_xuat_toan_bhyt)


def test_boost5_nhi_khoa_duoi_72_thang_bat_buoc_can_nang_tt26():
    ps_nhi = [
        PhatBieu(id=1, nguoi_noi="người nhà", chu_the_id=0, noi_dung="cháu sốt và đau họng", bang_chung=[2]),
        PhatBieu(id=2, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="viêm họng cấp", hanh_vi="nhận định", bang_chung=[3]),
        PhatBieu(
            id=3, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="kê amoxicillin 250mg",
            tinh_huong="kế hoạch", thuoc={"ten": "amoxicillin", "lieu": "250mg"}, bang_chung=[4]
        ),
    ]
    # Trẻ 36 tháng tuổi, thiếu cân nặng -> Phải cảnh báo TT 26/2025/TT-BYT
    kq_thieu_cn = BHYTXmlPreChecker.kiem_duyet_ho_so(
        "nhi_thieu_cn", ps_nhi, "Người nhà: Cháu nhà em 36 tháng tuổi bị sốt.", thong_tin_benh_nhan={}
    )
    assert any("TT 26/2025/TT-BYT" in c and "72 tháng" in c for c in kq_thieu_cn.canh_bao_lieu_nhi_khoa)

    # Khi đã có cân nặng 14 kg -> Không còn cảnh báo thiếu cân nặng
    kq_du_cn = BHYTXmlPreChecker.kiem_duyet_ho_so(
        "nhi_du_cn", ps_nhi, "Người nhà: Cháu 36 tháng tuổi.", thong_tin_benh_nhan={"can_nang_kg": 14.0}
    )
    assert not any("bắt buộc ghi Cân nặng" in c for c in kq_du_cn.canh_bao_lieu_nhi_khoa)


# ===========================================================================
# 4. BOOST 6: ĐỐI SOÁT ĐA ĐƠN & CẤU TRÚC ĐƠN THUỐC QUỐC GIA TT 26/2025
# ===========================================================================

def test_boost6_doi_soat_trung_hoat_chat_va_tinh_tong_so_luong_tt26():
    ps = [
        # Thuốc đang dùng ở nhà: Glucophage (hoạt chất metformin)
        PhatBieu(
            id=1, nguoi_noi="bệnh nhân", chu_the_id=0,
            noi_dung="đang uống Glucophage 850mg ở nhà",
            tinh_huong="thực tế",
            thuoc={"ten": "Glucophage", "lieu": "850mg", "duong_dung": "uống", "trang_thai_dung": "đang dùng"},
            bang_chung=[2],
        ),
        # Bác sĩ kê mới Metformin (trùng hoạt chất với Glucophage!) kèm đầy đủ buổi + số ngày
        PhatBieu(
            id=2, nguoi_noi="bác sĩ", chu_the_id=0,
            noi_dung="uống Metformin 500mg sáng 1 viên tối 1 viên sau ăn trong 1 tuần",
            tinh_huong="kế hoạch", hanh_vi="kế hoạch",
            thuoc={"ten": "Metformin", "lieu": "500mg", "duong_dung": "uống", "trang_thai_dung": "được kê, chưa dùng"},
            bang_chung=[5],
        ),
        # Bác sĩ kê Paracetamol khi sốt (PRN, thiếu số ngày) -> KHÔNG tự đoán tổng số lượng!
        PhatBieu(
            id=3, nguoi_noi="bác sĩ", chu_the_id=0,
            noi_dung="uống Paracetamol khi sốt trên 38.5 độ",
            tinh_huong="kế hoạch", hanh_vi="kế hoạch",
            thuoc={"ten": "Paracetamol", "duong_dung": "uống"},
            bang_chung=[6],
        ),
    ]
    kq = doi_soat_da_don_va_don_quoc_gia(ps)
    assert len(kq["thuoc_dang_dung_o_nha"]) == 1
    assert kq["thuoc_dang_dung_o_nha"][0]["ten_thuoc"] == "Glucophage"

    assert len(kq["don_thuoc_moi_tt26"]) == 2
    d_met = kq["don_thuoc_moi_tt26"][0]
    assert d_met["hoat_chat"] == "metformin"
    assert d_met["ham_luong"] == "500mg"
    assert (d_met["sang"], d_met["trua"], d_met["chieu"], d_met["toi"]) == (1, 0, 0, 1)
    assert d_met["so_ngay"] == 7
    assert d_met["tong_so_luong"] == 14
    assert d_met["duong_dung"] == "uống"
    assert "sau ăn" in d_met["loi_dan_an_uong"]
    assert d_met["bang_chung"] == ["[T5]"]
    assert d_met["thieu_thong_tin"] == []

    # Dòng thiếu thông tin phải giữ None / [cần bổ sung], không tự đoán
    d_para = kq["don_thuoc_moi_tt26"][1]
    assert d_para["ham_luong"] == "[cần bổ sung]"
    assert d_para["so_ngay"] is None
    assert d_para["tong_so_luong"] is None
    assert "ham_luong" in d_para["thieu_thong_tin"]
    assert "tong_so_luong" in d_para["thieu_thong_tin"]

    # Cảnh báo trùng hoạt chất giữa Glucophage ở nhà và Metformin đơn mới
    assert kq["co_trung_hoat_chat"] is True
    trung = kq["canh_bao_trung_hoat_chat"][0]
    assert trung["hoat_chat"] == "metformin"
    assert trung["pham_vi"] == "giua_thuoc_nha_va_don_moi"


# ===========================================================================
# 5. BOOST 8: KIỂM CHỨNG CAM ĐOAN THỦ THUẬT (ĐIỀU 10 & 63 LUẬT KBCB 2023)
# ===========================================================================

def test_boost8_cam_doan_du_6_muc_va_chan_bac_si_tu_xac_nhan():
    ht_du = (
        "Bác sĩ: Chẩn đoán hiện tại anh đang bị viêm loét dạ dày nghi xuất huyết tiêu hóa.\n"
        "Bác sĩ: Chúng tôi chỉ định tiến hành nội soi dạ dày gây mê để cầm máu và kiểm tra ổ loét.\n"
        "Bác sĩ: Nguy cơ tai biến có thể gặp gồm phản vệ với thuốc mê, chảy máu hoặc thủng dạ dày rất hiếm.\n"
        "Bác sĩ: Phương án thay thế là nội soi tỉnh không gây mê hoặc điều trị nội khoa theo dõi nhưng khó cầm máu trực tiếp.\n"
        "Bác sĩ: Nếu từ chối hoặc chậm trễ, bệnh có thể tiến triển nặng gây xuất huyết ồ ạt nguy hiểm tính mạng.\n"
        "Bệnh nhân: Dạ tôi đã hiểu rõ và hoàn toàn đồng ý làm nội soi gây mê ạ."
    )
    meta = [{"luot": i, "audio_start": float(i), "audio_end": float(i) + 0.8, "speaker_role": "doctor" if i < 6 else "patient"} for i in range(1, 7)]
    kq_du = kiem_chung_cam_doan_thu_thuat(ht_du, [], metadata_am_thanh=meta)
    assert kq_du["du_6_muc_phap_ly"] is True
    assert kq_du["ty_le_hoan_thanh"] == 1.0
    assert kq_du["chi_tiet_theo_ma"]["xac_nhan_dong_y"]["luot_can_cu"] == [6]
    assert len(kq_du["chi_tiet_theo_ma"]["xac_nhan_dong_y"]["audio_spans"]) == 1
    assert "[Cần bác sĩ giải thích bổ sung]" not in kq_du["van_ban_phieu_cam_doan"]

    # Bác sĩ tự nói "đồng ý" mà bệnh nhân/người nhà chưa lên tiếng -> PHẢI CHẶN!
    ht_bs_tu_noi = (
        "Bác sĩ: Tình trạng bệnh là viêm dạ dày cần nội soi dạ dày.\n"
        "Bác sĩ: Tôi ghi nhận bệnh nhân đã đồng ý ký cam đoan làm thủ thuật."
    )
    kq_chan = kiem_chung_cam_doan_thu_thuat(ht_bs_tu_noi, [])
    assert kq_chan["du_6_muc_phap_ly"] is False
    assert kq_chan["chi_tiet_theo_ma"]["xac_nhan_dong_y"]["da_giai_thich"] is False
    assert kq_chan["chan_bac_si_tu_xac_nhan"] is True
    assert "[Cần bác sĩ giải thích bổ sung]" in kq_chan["van_ban_phieu_cam_doan"]


# ===========================================================================
# 6. BOOST 9: MỞ RỘNG BÓC TÁCH XÉT NGHIỆM CŨ & ĐỐI SOÁT CẬN LÂM SÀNG
# ===========================================================================

def test_boost9_ocr_lam_sang_mo_rong_9_chi_so_va_doi_soat_can_lam_sang():
    van_ban = (
        "Phiếu XN: Đau ngực cấp. WBC: 15.4 G/L, Hb: 6.5 g/dL, Tiểu cầu: 190 G/L, "
        "Troponin T: 0.28 ng/mL, CRP: 45 mg/L, Natri: 136 mmol/L, Kali: 4.2 mmol/L, "
        "INR: 2.4, Bilirubin TP: 18 umol/L, Albumin: 34 g/L, HbA1c: 7.2%. Đơn cũ: Warfarin 5mg."
    )
    kq = boc_tach_phieu_cu(van_ban, tuoi=64, la_nu=False)
    cs = kq["chi_so"]
    assert cs["wbc"] == 15.4
    assert cs["hb"] == 6.5          # Không bị nhầm với HbA1c 7.2%
    assert cs["hba1c"] == 7.2
    assert cs["plt"] == 190.0
    assert cs["troponin"] == 0.28
    assert cs["crp"] == 45.0
    assert cs["na"] == 136.0
    assert cs["inr"] == 2.4
    assert cs["bilirubin"] == 18.0
    assert cs["albumin"] == 34.0

    cls = kq["doi_soat_can_lam_sang"]
    assert cls["co_gia_tri_nguy_kich"] is True
    assert any("Troponin" in b for b in cls["bao_dong_do_khan_cap"])
    assert any("Hemoglobin" in b for b in cls["bao_dong_do_khan_cap"])


# ===========================================================================
# 7. BOOST 10: TỜ ĐIỀU TRỊ NỘI TRÚ ĐI BUỒNG (SOAP EVOLUTION DIFF - TT 32/2023)
# ===========================================================================

def test_boost10_di_buong_noi_tru_diff_soap_sinh_hieu_va_y_lenh():
    pb_hom_qua = [
        {"id": 1, "noi_dung": "sốt cao", "phu_dinh": False, "bang_chung": [1]},
        {"id": 2, "noi_dung": "ho đờm đặc", "phu_dinh": False, "bang_chung": [2]},
        {"id": 3, "noi_dung": "Huyết áp 155/95 mmHg, mạch 98 lần/phút, nhiệt độ 38.8 độ, SpO2 94%", "phu_dinh": False, "bang_chung": [3]},
        {"id": 4, "noi_dung": "Amlodipin 5mg ngày 1 viên", "tinh_huong": "kế hoạch", "thuoc": {"ten": "Amlodipin", "lieu": "5mg", "so_lan": "ngày 1 lần"}, "bang_chung": [4]},
        {"id": 5, "noi_dung": "Amoxicillin 500mg ngày 2 lần", "tinh_huong": "kế hoạch", "thuoc": {"ten": "Amoxicillin", "lieu": "500mg", "so_lan": "ngày 2 lần"}, "bang_chung": [5]},
    ]
    pb_hom_nay = [
        {"id": 1, "noi_dung": "sốt", "phu_dinh": True, "bang_chung": [2]},
        {"id": 2, "noi_dung": "ho đờm", "phu_dinh": False, "bang_chung": [3]},
        {"id": 3, "noi_dung": "đau tức ngực phải", "phu_dinh": False, "bang_chung": [4]},
        {"id": 4, "noi_dung": "Huyết áp 130/80 mmHg, mạch 80 lần/phút, nhiệt độ 37.0 độ, SpO2 98%", "phu_dinh": False, "bang_chung": [5]},
        {"id": 5, "noi_dung": "Amlodipin 5mg ngày 1 viên", "tinh_huong": "kế hoạch", "thuoc": {"ten": "Amlodipin", "lieu": "5mg", "so_lan": "ngày 1 lần"}, "bang_chung": [6]},
        {"id": 6, "noi_dung": "Tăng liều Amoxicillin 1000mg ngày 2 lần", "tinh_huong": "kế hoạch", "thuoc": {"ten": "Amoxicillin", "lieu": "1000mg", "so_lan": "ngày 2 lần"}, "bang_chung": [7]},
        {"id": 7, "noi_dung": "Bổ sung Bromhexin 8mg", "tinh_huong": "kế hoạch", "thuoc": {"ten": "Paracetamol", "lieu": "500mg", "so_lan": "khi cần"}, "bang_chung": [8]},
    ]
    kq = tong_hop_to_dieu_tri_noi_tru(pb_hom_nay, pb_hom_qua, ngay_dieu_tri_thu=3)
    assert len(kq["trieu_chung_giam_hoac_het"]) == 1
    assert kq["trieu_chung_giam_hoac_het"][0]["bang_chung"] == ["[T2]"]

    assert len(kq["trieu_chung_con_ton_tai"]) == 1
    assert "ho đờm" in kq["trieu_chung_con_ton_tai"][0]["noi_dung"]

    assert len(kq["trieu_chung_moi_phat_sinh"]) == 1
    assert "đau tức ngực" in kq["trieu_chung_moi_phat_sinh"][0]["noi_dung"]

    sh_map = {x["ma"]: x for x in kq["bien_thien_sinh_hieu"]}
    assert sh_map["huyet_ap"]["xu_huong"] == "giảm"
    assert sh_map["spo2"]["xu_huong"] == "tăng"

    assert len(kq["y_lenh_duy_tri"]) == 1
    assert "Thuốc duy trì như ngày trước" in kq["y_lenh_duy_tri"][0]["mo_ta"]
    loai_td = {x["loai_thay_doi"] for x in kq["y_lenh_thay_doi"]}
    assert {"dieu_chinh_lieu", "them_moi"} <= loai_td
    assert "THÔNG TƯ 32/2023/TT-BYT" in kq["van_ban_to_dieu_tri_tt32"]
    assert "[T6]" in kq["van_ban_to_dieu_tri_tt32"]


# ===========================================================================
# 8. BOOST 12: CONTEXTUAL TRIE 600 + CSV TRÚNG THẦU BỆNH VIỆN + PHOWHISPER
# ===========================================================================

def test_boost12_trie_nap_csv_goi_y_sua_am_vi_va_phowhisper_provider(monkeypatch, tmp_path):
    trie = ContextualPrefixTrie600()
    csv_bv = (
        "hoat_chat,biet_duoc,ham_luong,he_co_quan\n"
        "Cefoperazon,Cefobid,1g,ho_hap\n"
        "Perindopril,Coversyl,5mg,tim_mach\n"
    )
    so_nap = trie.nap_danh_muc_trung_thau_csv(csv_bv)
    assert so_nap == 4
    hw_tm = trie.xuat_hotwords(he_co_quan="tim_mach", max_terms=20)
    assert "Perindopril" in hw_tm or "Coversyl" in hw_tm

    # Quét gợi ý âm vị: bắt G2P ("méc pho min") và lỗi chính tả 1 ký tự ("cefoperazon" đúng thì bỏ qua, "cefoperazol" sai thì gợi ý)
    van_ban_asr = "Bệnh nhân đang uống méc pho min và tiêm cefoperazol tại khoa."
    goi_y = trie.quet_goi_y_sua_am_vi(van_ban_asr)
    tu_goc_set = {g["tu_goc"].lower(): g["goi_y_chuan"] for g in goi_y}
    assert tu_goc_set.get("méc pho min") == "Metformin"
    assert tu_goc_set.get("cefoperazol") == "Cefoperazon"

    # Kiểm tra tích hợp vào PhoWhisperProvider mà KHÔNG tự ý sửa chữ gốc
    wav_test = _tao_wav_giong_gia(tmp_path / "asr.wav", f0_hz=150.0, duration_s=1.5)
    lp = math.log(0.92)
    monkeypatch.setattr(pw.PhoWhisperProvider, "_load", lambda self: (None, None, "cpu", "float32"))
    monkeypatch.setattr(
        pw.PhoWhisperProvider,
        "_decode_window",
        lambda self, a: {
            "tokens": [(" Tôi", 0.0, lp), (" uống", 0.3, lp), (" méc", 0.6, lp), (" pho", 0.8, lp), (" min", 1.0, lp)],
            "ids": [1, 2, 3, 4, 5],
            "dtw": True,
            "end": 1.3,
        },
    )
    provider = pw.PhoWhisperProvider(trie_600=trie, he_co_quan="noi_tiet_chuyen_hoa")
    res = provider.transcribe(wav_test)
    assert res.inference_config["trie_hotwords_active"] is True
    assert res.segments[0].text == "Tôi uống méc pho min"   # Giữ nguyên tuyệt đối chữ ASR
    assert len(res.inference_config["phonetic_candidates"]) == 1
    assert any("goi_y_sua_am_vi" in n and "Metformin" in n for n in res.notes)


# ===========================================================================
# 9. KIỂM THỬ TÍCH HỢP CÁC ĐƯỜNG DẪN HTTP API MỚI & CLI FALLBACK
# ===========================================================================

class _MayBoost(dich_vu.May):
    def log_message(self, *a):
        pass


def test_http_endpoints_va_cli_boost_8_10_12(monkeypatch):
    khoa = "khoa-test-boost-999"
    monkeypatch.setenv("MEDITRACE_INTERNAL_TOKEN", khoa)
    _MayBoost.loi = dich_vu.Loi(cho_nap_mo_hinh=False)
    _MayBoost.am = types.SimpleNamespace(
        cau_hinh_nhe=lambda: types.SimpleNamespace(
            asr_provider="phowhisper", asr_model="small", whisper_model="small", diarization_provider="mot-nguoi"
        )
    )
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _MayBoost)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    cong = srv.server_address[1]

    def _post(duong: str, body: dict):
        conn = http.client.HTTPConnection("127.0.0.1", cong, timeout=10)
        raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
        conn.request(
            "POST",
            duong,
            body=raw,
            headers={"Content-Type": "application/json", "X-MediTrace-Internal-Token": khoa},
        )
        r = conn.getresponse()
        data = json.loads(r.read().decode("utf-8"))
        conn.close()
        return r.status, data

    try:
        # 1. POST /api/cam-doan-thu-thuat
        st1, d1 = _post("/api/cam-doan-thu-thuat", {
            "hoi_thoai": "Bác sĩ: Cần nội soi dạ dày vì viêm loét.\nBệnh nhân: Dạ tôi đồng ý nội soi.",
        })
        assert st1 == 200 and d1["so_muc_dat"] >= 3 and d1["du_6_muc_phap_ly"] is False

        # 2. POST /api/noi-tru/to-dieu-tri
        st2, d2 = _post("/api/noi-tru/to-dieu-tri", {
            "phat_bieu_hom_qua": [{"id": 1, "noi_dung": "sốt", "phu_dinh": False, "bang_chung": [1]}],
            "phat_bieu_hom_nay": [{"id": 1, "noi_dung": "hết sốt", "phu_dinh": False, "bang_chung": [2]}],
            "ngay_dieu_tri_thu": 2,
        })
        assert st2 == 200 and len(d2["trieu_chung_giam_hoac_het"]) == 1

        # 3. POST /api/duoc-thu/nap-csv
        st3, d3 = _post("/api/duoc-thu/nap-csv", {
            "csv": "hoat_chat,biet_duoc\nMeropenem,Meronem\n",
        })
        assert st3 == 200 and d3["ok"] is True and d3["so_muc_da_nap"] == 2
        assert "Meropenem" in tao_trie_600_mac_dinh()._tat_ca_thuoc

        # 4. Kiểm tra tự động đính kèm `cam_doan_thu_thuat` và `doi_soat_thuoc_tt26` trong `_them_canh_bao`
        ban_ghi = {
            "id": "ca_tt",
            "input": "Bác sĩ: Chẩn đoán viêm dạ dày, chỉ định nội soi dạ dày.\nBệnh nhân: Dạ vâng tôi đồng ý nội soi.",
            "phat_bieu": [
                {"id": 1, "nguoi_noi": "bác sĩ", "chu_the_id": 0, "noi_dung": "viêm dạ dày", "hanh_vi": "nhận định", "bang_chung": [1]},
                {"id": 2, "nguoi_noi": "bác sĩ", "chu_the_id": 0, "noi_dung": "Omeprazol 20mg sáng 1 viên trước ăn 30 phút trong 14 ngày", "tinh_huong": "kế hoạch", "thuoc": {"ten": "Omeprazol", "lieu": "20mg", "duong_dung": "uống"}, "bang_chung": [1]},
            ],
        }
        assert co_dau_hieu_thu_thuat(ban_ghi["input"], ban_ghi["phat_bieu"]) is True
        da_gan = dich_vu._them_canh_bao(ban_ghi)
        ls = da_gan["lam_sang_nang_cao"]
        assert "doi_soat_thuoc_tt26" in ls
        assert ls["doi_soat_thuoc_tt26"]["don_thuoc_moi_tt26"][0]["tong_so_luong"] == 14
        assert "cam_doan_thu_thuat" in ls
    finally:
        srv.shutdown()
        srv.server_close()

    # 5. CLI `--check` và `--diff`
    p_check = subprocess.run(
        [sys.executable, "-m", "src.cong_cu_lam_sang.cam_doan_thu_thuat", "--check"],
        input=json.dumps({"hoi_thoai": "Bác sĩ: Cần sinh thiết hạch.\nBệnh nhân: Tôi chưa đồng ý."}).encode("utf-8"),
        capture_output=True,
        check=True,
    )
    out_check = json.loads(p_check.stdout.decode("utf-8"))
    assert out_check["nguoi_benh_tu_choi_hoac_hoan"] is True

    p_diff = subprocess.run(
        [sys.executable, "-m", "src.cong_cu_lam_sang.di_buong_noi_tru", "--diff"],
        input=json.dumps({
            "phat_bieu_hom_qua": [{"noi_dung": "khó thở", "bang_chung": [1]}],
            "phat_bieu_hom_nay": [{"noi_dung": "đỡ khó thở", "bang_chung": [2]}],
        }).encode("utf-8"),
        capture_output=True,
        check=True,
    )
    out_diff = json.loads(p_diff.stdout.decode("utf-8"))
    assert len(out_diff["trieu_chung_giam_hoac_het"]) == 1
