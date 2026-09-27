# -*- coding: utf-8 -*-
"""Tach nguoi noi khi chep am (pyannote qua moi truong rieng) va gop luot.

Phan lon phep thu dung mot tep chay GIA (viet ra tmp_path) thay cho pyannote_chay.py, nen
khong can pyannote hay mo hinh. Phep thu chay pyannote that chi chay khi dat
PYANNOTE_INTEGRATION=1 (can moi truong rieng + mo hinh da tai ve bo nho dem).
"""
import json
import os
import sys
import time
from pathlib import Path

import pytest

from src.audio.alignment import align, gop_lien_tiep
from src.audio.config import AudioSettings
from src.audio.models import TranscriptSegment
from src.audio.pipeline import AudioPipeline
from src.audio.pyannote_provider import LoiTachNguoiNoi, PyannoteDiarizationProvider
from src.audio.storage import SessionStore
from src.dich_vu import ghi_chu_tach


def _doan(i, spk, a, b, chu, tin=0.9):
    return TranscriptSegment(segment_id=f"seg_{i:04d}", utterance_id=i, speaker_id=spk,
                             speaker_role="unknown", start_time=a, end_time=b, text_original=chu,
                             asr_confidence=tin,
                             audio_reference={"session_id": "s", "start_time": a, "end_time": b})


# ------------------------------------------------------------------ gop luot
def test_gop_cac_doan_lien_tiep_cung_nguoi_noi():
    ra = gop_lien_tiep([_doan(1, "speaker_1", 0.0, 1.0, "Chị ho", 0.9),
                        _doan(2, "speaker_1", 1.9, 2.5, "bao lâu rồi?", 0.5),
                        _doan(3, "speaker_2", 2.8, 3.5, "Mười ngày."),
                        _doan(4, "speaker_1", 3.9, 4.2, "Có sốt không?")])
    assert [(d.speaker_id, d.text_original) for d in ra] == [
        ("speaker_1", "Chị ho bao lâu rồi?"), ("speaker_2", "Mười ngày."), ("speaker_1", "Có sốt không?")]
    assert ra[0].start_time == 0.0 and ra[0].end_time == 2.5
    assert ra[0].audio_reference["end_time"] == 2.5
    assert ra[0].asr_confidence == 0.5          # lay do tin thap nhat, khong de mat canh bao
    assert [d.segment_id for d in ra] == ["seg_0001", "seg_0002", "seg_0003"]
    assert [d.utterance_id for d in ra] == [1, 2, 3]


def test_khong_gop_doan_chua_ro_nguoi_noi():
    ra = gop_lien_tiep([_doan(1, "unknown", 0, 1, "a"), _doan(2, "unknown", 1, 2, "b")])
    assert len(ra) == 2


# ------------------------------------------------------------ tu lot khe
DIA = [{"speaker_id": "speaker_1", "start": 0.0, "end": 2.0},
       {"speaker_id": "speaker_2", "start": 2.4, "end": 5.0}]


def _asr_tung_tu(words):
    return {"segments": [{"start": words[0][1], "end": words[-1][2], "confidence": 0.9,
                          "text": "".join(w[0] for w in words),
                          "words": [{"text": t, "start_time": a, "end_time": b} for t, a, b in words]}]}


def test_tu_lot_khe_gan_cho_doan_gan_nhat():
    # " rồi" 2.05-2.15 khong trung doan nao; gan speaker_1 (cach 0,05 s) chu khong phai speaker_2.
    out = align("s", _asr_tung_tu([(" Ho", 1.5, 1.9), (" rồi", 2.05, 2.15), (" Vâng", 2.5, 2.9)]), DIA)
    assert [(o.speaker_id, o.text_original) for o in out] == [("speaker_1", "Ho rồi"), ("speaker_2", "Vâng")]


def test_tu_xa_moi_doan_de_chua_ro():
    out = align("s", _asr_tung_tu([(" Alo", 7.0, 7.4)]), DIA)
    assert out[0].speaker_id == "unknown"


def test_tu_cuoi_luot_gan_theo_moc_bat_dau_khong_theo_moc_ket_thuc_uoc():
    # PhoWhisper uoc moc ket thuc = moc bat dau tu sau (toi da +1,2 s): " rồi." 1,5 -> 2,7 trung
    # speaker_2 0,6 s nhung chi trung speaker_1 0,4 s. Tu that bat dau trong luot speaker_1.
    dia = [{"speaker_id": "speaker_1", "start": 0.0, "end": 1.9},
           {"speaker_id": "speaker_2", "start": 2.1, "end": 5.0}]
    out = align("s", _asr_tung_tu([(" Ho", 1.0, 1.5), (" rồi.", 1.5, 2.7), (" Vâng.", 2.7, 3.2)]), dia)
    assert [(o.speaker_id, o.text_original) for o in out] == [("speaker_1", "Ho rồi."), ("speaker_2", "Vâng.")]


def test_mot_nguoi_noi_van_cat_dong_o_khoang_lang_dai():
    vad = [{"speaker_id": "speaker_1", "start": 0.0, "end": 1.0},
           {"speaker_id": "speaker_1", "start": 1.2, "end": 2.0},     # lang 0,2 s: khong cat
           {"speaker_id": "speaker_1", "start": 2.8, "end": 4.0}]     # lang 0,8 s: cat
    out = align("s", _asr_tung_tu([(" Ho", 0.1, 1.2), (" lâu", 1.2, 2.8), (" chưa?", 1.5, 2.8),
                                   (" Mười", 2.9, 3.3), (" ngày.", 3.3, 4.0)]), vad)
    assert [o.text_original for o in out] == ["Ho lâu chưa?", "Mười ngày."]
    assert {o.speaker_id for o in out} == {"speaker_1"}


# ------------------------------------------------------------ khoa & moi truong
def test_khoa_khong_nam_trong_dong_lenh(tmp_path):
    khoa = tmp_path / "hf.key"
    khoa.write_text("hf_GIATRIBIMAT123\n", encoding="utf-8")
    p = PyannoteDiarizationProvider(sys.executable, token_file=str(khoa), min_speakers=2, max_speakers=3)
    lenh = p.lenh(tmp_path / "a.wav", tmp_path / "ra.json")
    assert not any("hf_GIATRIBIMAT123" in x for x in lenh)
    assert lenh[-4:] == ["--it-nhat", "2", "--nhieu-nhat", "3"]
    env = p.moi_truong()
    assert env["HF_TOKEN"] == "hf_GIATRIBIMAT123" and "HF_HUB_OFFLINE" not in env


def test_khong_co_tep_khoa_thi_chay_ngoai_tuyen_va_bo_khoa_cua_tien_trinh_cha(monkeypatch, tmp_path):
    monkeypatch.setenv("HF_TOKEN", "khoa_cua_moi_truong_cha")
    env = PyannoteDiarizationProvider(sys.executable, token_file=str(tmp_path / "khong-co.key"),
                                      hf_home=str(tmp_path / "hf")).moi_truong()
    assert "HF_TOKEN" not in env
    assert env["HF_HUB_OFFLINE"] == "1" and env["HF_HOME"] == str(tmp_path / "hf")
    assert env["PYANNOTE_CACHE"] == str(tmp_path / "hf" / "hub")     # pyannote 3.x doc bien nay


# ------------------------------------------------------------ tep chay gia
GIA_XONG = r'''
import json, sys
a = sys.argv
ra = a[a.index("--ra") + 1]
json.dump({"segments": [{"speaker_id": "speaker_1", "start": 0.0, "end": 1.0},
                        {"speaker_id": "speaker_2", "start": 1.2, "end": 2.0},
                        {"speaker_id": "speaker_2", "start": 2.0, "end": 2.0}],
           "so_nguoi_noi": 2, "mo_hinh": "gia", "pyannote": "0.0", "thiet_bi": "cpu"},
          open(ra, "w", encoding="utf-8"))
'''
GIA_LOI_NAP = r'''
import json, sys
print("Traceback ... dong nhat ky bat ky", file=sys.stderr)
print(json.dumps({"loi": "mo_hinh_khong_nap_duoc", "chi_tiet": "gated"}), file=sys.stderr)
sys.exit(2)
'''
GIA_TREO = "import time\ntime.sleep(60)\n"
GIA_AN_RAM = "import time\nx = bytearray(400 * 2**20)\nfor i in range(0, len(x), 4096): x[i] = 1\ntime.sleep(60)\n"
GIA_KHONG_RA = "pass\n"


def _nha_cung_cap(tmp_path, noi_dung, **kw):
    tep = tmp_path / "gia_chay.py"
    tep.write_text(noi_dung, encoding="utf-8")
    wav = tmp_path / "processed.wav"
    wav.write_bytes(b"")
    return PyannoteDiarizationProvider(sys.executable, script=str(tep), **kw), wav


def test_doc_ket_qua_json_va_bo_doan_do_dai_bang_khong(tmp_path):
    p, wav = _nha_cung_cap(tmp_path, GIA_XONG)
    doan = p.diarize(wav, [])
    assert [d["speaker_id"] for d in doan] == ["speaker_1", "speaker_2"]
    assert p.last_info["phuong_phap"] == "pyannote" and p.last_info["so_nguoi_noi"] == 2
    assert "ram_dinh_mb" in p.last_info and "giay" in p.last_info


def test_loi_nap_mo_hinh_lay_ma_tu_dong_json_cuoi(tmp_path):
    p, wav = _nha_cung_cap(tmp_path, GIA_LOI_NAP)
    with pytest.raises(LoiTachNguoiNoi, match="mo_hinh_khong_nap_duoc"):
        p.diarize(wav, [])


def test_qua_thoi_gian_thi_giet_tien_trinh(tmp_path):
    p, wav = _nha_cung_cap(tmp_path, GIA_TREO, timeout_s=1.0)
    t0 = time.time()
    with pytest.raises(LoiTachNguoiNoi, match="pyannote_qua_thoi_gian"):
        p.diarize(wav, [])
    assert time.time() - t0 < 20


def test_vuot_tran_ram_thi_giet_tien_trinh(tmp_path):
    p, wav = _nha_cung_cap(tmp_path, GIA_AN_RAM, ram_gb=0.2, timeout_s=60)
    t0 = time.time()
    with pytest.raises(LoiTachNguoiNoi, match="pyannote_vuot_tran_ram"):
        p.diarize(wav, [])
    assert time.time() - t0 < 30


def test_thoat_ma_0_ma_khong_ghi_ket_qua(tmp_path):
    p, wav = _nha_cung_cap(tmp_path, GIA_KHONG_RA)
    with pytest.raises(LoiTachNguoiNoi, match="pyannote_khong_ra_ket_qua"):
        p.diarize(wav, [])


def test_python_cua_moi_truong_rieng_khong_co(tmp_path):
    p = PyannoteDiarizationProvider(str(tmp_path / "khong-co" / "python.exe"))
    with pytest.raises(LoiTachNguoiNoi, match="pyannote_python_khong_co"):
        p.diarize(tmp_path / "processed.wav", [])


def test_tep_chay_that_bao_loi_dung_hop_dong_khi_thieu_pyannote_hoac_mo_hinh(tmp_path):
    """Chay pyannote_chay.py THAT bang python cua moi truong phep thu: hoac thieu pyannote
    (ma thoat 3), hoac co pyannote nhung khong co mo hinh ngoai tuyen (ma thoat 2)."""
    wav = tmp_path / "processed.wav"
    wav.write_bytes(b"")
    p = PyannoteDiarizationProvider(sys.executable, hf_home=str(tmp_path / "hf-rong"), timeout_s=300)
    with pytest.raises(LoiTachNguoiNoi) as e:
        p.diarize(wav, [])
    assert str(e.value) in {"pyannote_chua_cai", "mo_hinh_khong_nap_duoc"}


# ------------------------------------------------------------ duong ong
class _Pre:
    def convert(self, source, target):
        target.write_bytes(b"wav")
        return {"sample_rate": 16000, "channels": 1, "duration": 6.0}


class _VAD:
    def detect(self, _):
        return [{"start": 0.0, "end": 6.0}]


class _ASR:
    def transcribe(self, _):
        return {"language": "vi", "segments": [
            {"start": 0.0, "end": 1.0, "text": "Chị ho bao lâu rồi?", "confidence": 0.9},
            {"start": 1.2, "end": 2.0, "text": "Mười ngày.", "confidence": 0.8},
            {"start": 3.0, "end": 3.6, "text": "À không,", "confidence": 0.7},
            {"start": 4.6, "end": 5.4, "text": "hai tuần rồi ạ.", "confidence": 0.9}]}


class _TachThat:
    tach_that, ten = True, "pyannote"

    def __init__(self, doan=None, loi=None):
        self.doan, self.loi, self.last_info = doan, loi, {}

    def diarize(self, _, speech):
        if self.loi:
            raise LoiTachNguoiNoi(self.loi)
        self.last_info = {"phuong_phap": "pyannote", "so_nguoi_noi": 2}
        return self.doan


def _chay(tmp_path, tach, settings=None, bat=True):
    store = SessionStore(tmp_path)
    pipe = AudioPipeline(store, asr=_ASR(), preprocessor=_Pre(), vad=_VAD(), diarization=tach,
                         settings=settings or AudioSettings())
    phien = store.create()["session_id"]
    pipe.upload(phien, b"raw", "raw.webm")
    pipe.process(phien, tach_nguoi_noi=bat)
    return pipe, store, phien


def test_nguoi_goi_tat_tach_thi_khong_goi_bo_tach_that(tmp_path):
    tach = _TachThat(loi="khong_duoc_goi")
    pipe, store, phien = _chay(tmp_path, tach, bat=False)
    info = store.load(phien)["tach_nguoi_noi"]
    assert info["bo_qua"] is True and "loi" not in info
    assert len(pipe.transcript(phien)) == 4


def test_tach_that_hai_nguoi_noi_thi_gop_luot_lien_tiep(tmp_path):
    tach = _TachThat([{"speaker_id": "speaker_1", "start": 0.0, "end": 1.1},
                      {"speaker_id": "speaker_2", "start": 1.1, "end": 6.0}])
    pipe, store, phien = _chay(tmp_path, tach)
    ds = pipe.transcript(phien)
    assert [(d["speaker_id"], d["text_original"]) for d in ds] == [
        ("speaker_1", "Chị ho bao lâu rồi?"), ("speaker_2", "Mười ngày. À không, hai tuần rồi ạ.")]
    assert {d["speaker_role"] for d in ds} == {"unknown"}        # khong doan vai
    info = store.load(phien)["tach_nguoi_noi"]
    assert info["tach_that"] is True and info["so_nguoi_noi"] == 2
    # Gan vai theo NGUOI NOI: mot lan cho moi nguoi, ap cho moi dong cua nguoi do.
    pipe.map_speakers(phien, {"speaker_1": "doctor", "speaker_2": "patient"})
    turns = pipe.meditrace_input(phien)["turns"]
    assert [t["nguoi_noi"] for t in turns] == ["bac_si", "benh_nhan"]


def test_may_tach_chi_nghe_ra_mot_nguoi_thi_khong_gop(tmp_path):
    class _MotGiong(_TachThat):
        def diarize(self, _, speech):
            self.last_info = {"phuong_phap": "pyannote", "so_nguoi_noi": 1}
            return [{"speaker_id": "speaker_1", "start": 0.0, "end": 6.0}]

    pipe, store, _phien = _chay(tmp_path, _MotGiong())
    assert len(pipe.transcript(_phien)) == 4        # van gan vai tung dong duoc
    assert store.load(_phien)["tach_nguoi_noi"]["tach_that"] is True


def test_tat_gop_luot_thi_giu_tung_doan(tmp_path):
    tach = _TachThat([{"speaker_id": "speaker_1", "start": 0.0, "end": 1.1},
                      {"speaker_id": "speaker_2", "start": 1.1, "end": 6.0}])
    pipe, _, phien = _chay(tmp_path, tach, AudioSettings(gop_luot_cung_nguoi_noi=False))
    assert len(pipe.transcript(phien)) == 4


def test_tach_loi_thi_lui_ve_mot_nguoi_noi_va_ghi_ly_do(tmp_path):
    pipe, store, phien = _chay(tmp_path, _TachThat(loi="mo_hinh_khong_nap_duoc"))
    ds = pipe.transcript(phien)
    assert len(ds) == 4 and {d["speaker_id"] for d in ds} == {"speaker_1"}    # khong gop
    info = store.load(phien)["tach_nguoi_noi"]
    assert info == {"phuong_phap": "mot_nguoi", "tach_that": False, "so_nguoi_noi": 1,
                    "loi": "mo_hinh_khong_nap_duoc", "lui_ve": True}
    su_kien = [json.loads(x) for x in store.path(phien, "audit.jsonl").read_text(encoding="utf-8").splitlines()]
    assert any(e["event"] == "diarization_failed" and e["code"] == "mo_hinh_khong_nap_duoc" for e in su_kien)
    assert store.load(phien)["status"] == "transcript_ready"


def test_tach_that_khong_ra_doan_nao_cung_lui_ve(tmp_path):
    _, store, phien = _chay(tmp_path, _TachThat(doan=[]))
    assert store.load(phien)["tach_nguoi_noi"]["loi"] == "pyannote_khong_thay_ai_noi"


def test_cau_hinh_pyannote_thieu_python_van_chep_duoc(tmp_path):
    pipe, store, phien = _chay(tmp_path, None, AudioSettings(diarization_provider="pyannote"))
    assert store.load(phien)["tach_nguoi_noi"]["loi"] == "pyannote_chua_cau_hinh"
    assert len(pipe.transcript(phien)) == 4


def test_mac_dinh_mot_nguoi_noi_khong_gop(tmp_path):
    pipe, store, phien = _chay(tmp_path, None)
    assert len(pipe.transcript(phien)) == 4
    info = store.load(phien)["tach_nguoi_noi"]
    assert info["phuong_phap"] == "mot_nguoi" and info["tach_that"] is False and "loi" not in info


# ------------------------------------------------------------ cau hinh & loi nhan
def test_doc_cau_hinh_tu_bien_moi_truong(monkeypatch):
    monkeypatch.setenv("DIARIZATION_PROVIDER", "pyannote")
    monkeypatch.setenv("PYANNOTE_PYTHON", "D:/pyannote-venv/Scripts/python.exe")
    monkeypatch.setenv("PYANNOTE_MAX_SPEAKERS", "3")
    monkeypatch.setenv("PYANNOTE_RAM_GB", "2.5")
    monkeypatch.setenv("GOP_LUOT_CUNG_NGUOI_NOI", "false")
    s = AudioSettings.from_env()
    assert s.diarization_provider == "pyannote" and s.pyannote_max_speakers == 3
    assert s.pyannote_ram_gb == 2.5 and s.gop_luot_cung_nguoi_noi is False
    p = PyannoteDiarizationProvider.from_settings(s)
    assert p.model == "pyannote/speaker-diarization-3.1" and p.device == "cpu"


def test_ten_bo_tach_sai_thi_bao_loi(monkeypatch):
    monkeypatch.setenv("DIARIZATION_PROVIDER", "doan-vai")
    with pytest.raises(ValueError, match="invalid_diarization_provider"):
        AudioSettings.from_env()


def _co(**kw):
    import argparse
    mac_dinh = dict(tach_nguoi_noi=None, pyannote_python=None, pyannote_khoa=None,
                    pyannote_thiet_bi=None, tran_ram_gb=None)
    return argparse.Namespace(**{**mac_dinh, **kw})


def test_co_dong_lenh_cua_hoaiduc_dat_duoc_bien_moi_truong(monkeypatch):
    # 25/09: dong nay lam dich vu tren HoaiDuc hong khi khoi dong (thieu `import os`), vi HoaiDuc
    # chay voi --tran-ram-gb 8.5. Goi dung duong mac dinh (os.environ) de bat lai loi do.
    from src.dich_vu import dat_bien_tach_nguoi_noi
    monkeypatch.delenv("PYANNOTE_TONG_RAM_GB", raising=False)
    monkeypatch.delenv("DIARIZATION_PROVIDER", raising=False)
    dat_bien_tach_nguoi_noi(_co(tran_ram_gb=8.5, tach_nguoi_noi="pyannote"))
    assert os.environ["PYANNOTE_TONG_RAM_GB"] == "8.5"
    assert os.environ["DIARIZATION_PROVIDER"] == "pyannote"


def test_co_dong_lenh_khong_de_len_tran_ram_da_dat_tay():
    from src.dich_vu import dat_bien_tach_nguoi_noi
    env = {"PYANNOTE_TONG_RAM_GB": "7"}
    dat_bien_tach_nguoi_noi(_co(tran_ram_gb=8.5, pyannote_khoa="D:/khoa.key"), env)
    assert env == {"PYANNOTE_TONG_RAM_GB": "7", "PYANNOTE_TOKEN_FILE": "D:/khoa.key"}


def test_loi_nhan_cho_nguoi_dung():
    assert "2 người nói" in ghi_chu_tach({"tach_that": True, "so_nguoi_noi": 2, "phuong_phap": "pyannote"})
    assert "không biết ai là bác sĩ" in ghi_chu_tach({"tach_that": True, "so_nguoi_noi": 2})
    assert "mo_hinh_khong_nap_duoc" in ghi_chu_tach({"lui_ve": True, "loi": "mo_hinh_khong_nap_duoc"})
    assert ghi_chu_tach(None).startswith("Chưa bật tách người nói")


# ------------------------------------------------------------ pyannote that (tuy chon)
@pytest.mark.skipif(os.environ.get("PYANNOTE_INTEGRATION") != "1",
                    reason="dat PYANNOTE_INTEGRATION=1 va PYANNOTE_PYTHON de chay pyannote that")
def test_pyannote_that_tach_hai_giong(tmp_path):
    import math
    import struct
    import wave
    wav = tmp_path / "processed.wav"
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        khung = []
        for i in range(16000 * 4):
            f = 140 if i < 16000 * 2 else 260
            khung.append(struct.pack("<h", int(8000 * math.sin(2 * math.pi * f * i / 16000))))
        w.writeframes(b"".join(khung))
    p = PyannoteDiarizationProvider.from_settings(AudioSettings.from_env())
    doan = p.diarize(wav, [])
    assert isinstance(doan, list) and p.last_info["phuong_phap"] == "pyannote"
