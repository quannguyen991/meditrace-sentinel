# -*- coding: utf-8 -*-
"""Doi nha cung cap ASR bang cau hinh; du phong chi khi cho phep (yeu cau II, XVIII, XIX)."""
import dataclasses
import json
import wave

import pytest

from src.audio.asr import registry
from src.audio.asr.base import ASRProvider
from src.audio.asr.faster_whisper_provider import FasterWhisperProvider
from src.audio.asr.phowhisper_provider import PhoWhisperProvider
from src.audio.asr.schemas import ASRError, ASRResult, ASRSegment
from src.audio.config import AudioSettings


def test_doi_nha_cung_cap_bang_cau_hinh(monkeypatch):
    monkeypatch.setenv("ASR_PROVIDER", "phowhisper")
    monkeypatch.setenv("ASR_MODEL", "medium")
    p = registry.from_settings(AudioSettings.from_env())
    assert isinstance(p, PhoWhisperProvider) and p.model == "vinai/PhoWhisper-medium"
    assert p.revision == "55a7e3eb6c906de891f8f06a107754427dd3be79"
    monkeypatch.setenv("ASR_PROVIDER", "faster_whisper")
    monkeypatch.setenv("ASR_MODEL", "small")
    assert isinstance(registry.from_settings(AudioSettings.from_env()), FasterWhisperProvider)


def test_mac_dinh_phowhisper_la_small_khong_phai_large():
    assert PhoWhisperProvider().model == "vinai/PhoWhisper-small"


def test_ten_la_bi_tu_choi():
    with pytest.raises(ASRError) as e:
        registry.create("khong_co")
    assert e.value.code == "asr_provider_unknown" and e.value.to_dict()["recoverable"] is False


class _GuiRaNgoai(ASRProvider):
    name = "dam_may"
    external = True

    def transcribe(self, audio_path):
        raise AssertionError("khong duoc goi")


def test_nha_cung_cap_gui_ra_ngoai_bi_chan_o_che_do_local():
    registry.register("dam_may", _GuiRaNgoai)
    with pytest.raises(ASRError) as e:
        registry.create("dam_may", processing_mode="local")
    assert e.value.code == "asr_provider_external_blocked"


class _Hong(ASRProvider):
    name = "hong"

    def transcribe(self, audio_path):
        raise ASRError("phowhisper_inference_failed")


class _Tot(ASRProvider):
    name = "tot"

    def transcribe(self, audio_path):
        return ASRResult("tot", "m", "vi", [ASRSegment("seg_001", 0, 1, "ạ")])


def test_khong_cho_du_phong_thi_dung_va_bao_loi():
    s = AudioSettings(asr_provider="hong", allow_asr_fallback=False, asr_fallback_provider="tot")
    with pytest.raises(ASRError) as e:
        registry.transcribe(s, "x.wav", _Hong())
    assert e.value.code == "phowhisper_inference_failed"


def test_cho_du_phong_thi_dung_dung_nha_cung_cap_duoc_chi_dinh():
    registry.register("tot", _Tot)
    s = AudioSettings(asr_provider="hong", allow_asr_fallback=True, asr_fallback_provider="tot")
    res, info = registry.transcribe(s, "x.wav", _Hong())
    assert res.provider == "tot" and info["fallback"] is True
    assert info["primary_error"]["code"] == "phowhisper_inference_failed"


def test_doc_wav_sai_dinh_dang_bao_audio_invalid(tmp_path):
    from src.audio.asr.base import read_wav_16k_mono
    f = tmp_path / "x.wav"
    with wave.open(str(f), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(44100); w.writeframes(b"\0\0" * 200)
    with pytest.raises(ASRError) as e:
        read_wav_16k_mono(f)
    assert e.value.code == "audio_invalid"
