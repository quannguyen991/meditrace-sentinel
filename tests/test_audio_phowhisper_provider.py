# -*- coding: utf-8 -*-
"""PhoWhisperProvider: dung luoc do chung, ghi phien ban, khong bia moc thoi gian.

Phep thu don vi thay buoc giai ma bang ban gia — khong tai mo hinh.
Phep thu tich hop that chi chay khi dat ASR_INTEGRATION=1 (can mo hinh va GPU/CPU).
"""
import math
import os
import wave
from pathlib import Path

import numpy as np
import pytest

from src.audio.asr import phowhisper_provider as pw


def _wav(path, giay=2.0):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(b"\0\0" * int(16000 * giay))
    return path


def _gia(monkeypatch, cua_so_ra):
    """cua_so_ra: danh sach ket qua _decode_window lan luot cho tung cua so."""
    it = iter(cua_so_ra)
    monkeypatch.setattr(pw.PhoWhisperProvider, "_load", lambda self: (None, None, "cpu", "float32"))
    monkeypatch.setattr(pw.PhoWhisperProvider, "_decode_window", lambda self, a: next(it))


def _ra(tokens, dtw=True, end=None, ids=None):
    return {"tokens": tokens, "ids": ids or list(range(len(tokens))), "dtw": dtw, "end": end}


LP = math.log(0.9)


def test_luoc_do_chung_moc_tung_tu_va_do_tin_cay(monkeypatch, tmp_path):
    _gia(monkeypatch, [_ra([("t", 0.0, LP), ("ôi", 0.3, LP), (" uống", 0.5, LP), (" amoxicillin", 0.8, LP),
                            (" Bố", 3.2, LP), (" em", 3.4, LP)], end=3.7)])
    r = pw.PhoWhisperProvider("vinai/PhoWhisper-medium").transcribe(_wav(tmp_path / "a.wav", 4))
    assert r.provider == "phowhisper" and r.model == "vinai/PhoWhisper-medium"
    assert r.revision == pw.REVISIONS["vinai/PhoWhisper-medium"] and r.timestamp_level == "word"
    assert [s.text for s in r.segments] == ["tôi uống amoxicillin", "Bố em"]   # tach theo khoang lang
    assert r.segments[0].words[0].text == "tôi" and r.segments[0].words[0].start_time == 0.0
    assert r.segments[0].end_time == 2.0 and r.segments[1].end_time == 3.7                                      # tu cuoi ket thuc o eos
    assert r.segments[0].asr_confidence == 0.9
    assert r.inference_config["timestamp_tokens"] is False


def test_khong_co_dtw_thi_dung_moc_cua_so_va_ghi_lai(monkeypatch, tmp_path):
    _gia(monkeypatch, [_ra([(" Không", None, LP), (" dị", None, LP), (" ứng.", None, LP)], dtw=False)])
    r = pw.PhoWhisperProvider().transcribe(_wav(tmp_path / "a.wav"))
    assert r.timestamp_level == "window"
    assert (r.segments[0].start_time, r.segments[0].end_time) == (0.0, 2.0)
    assert r.segments[0].text == "Không dị ứng." and r.segments[0].words == []
    assert any("DTW" in n for n in r.notes)


def test_lap_lai_duoc_ghi_chu_nhung_khong_cat_chu(monkeypatch, tmp_path):
    toks = [(" ông", 0.0, LP)] + [(" a.", 0.5 + 0.1 * i, LP) for i in range(6)]
    _gia(monkeypatch, [_ra(toks, end=1.2, ids=[1] + [7] * 6)])
    r = pw.PhoWhisperProvider().transcribe(_wav(tmp_path / "a.wav"))
    assert any("lap_lai_nghi_ngo" in n for n in r.notes)
    assert r.segments[0].text.count("a.") == 6


def test_giu_nguyen_chu_mo_hinh_nghe_duoc(monkeypatch, tmp_path):
    _gia(monkeypatch, [_ra([(" Người", 0.0, LP), (" nóng", 0.3, LP), (" hầm", 0.5, LP), (" hập.", 0.7, LP)], end=1.0)])
    r = pw.PhoWhisperProvider(word_timestamps=False).transcribe(_wav(tmp_path / "a.wav"))
    assert r.segments[0].text == "Người nóng hầm hập." and r.timestamp_level == "segment"


def test_cat_cua_so_tai_cho_lang_va_khong_qua_30s():
    sr = 16000
    x = np.full(sr * 70, 0.3, dtype="float32")
    x[int(25 * sr):int(25.2 * sr)] = 0.0         # cho lang o giay 25
    cs = pw._cat_cua_so(x, sr)
    assert all((b - a) / sr <= 30 for a, b in cs) and cs[0][0] == 0 and cs[-1][1] == len(x)
    assert 25.0 <= cs[0][1] / sr <= 25.2


def test_mot_cua_so_khi_ngan_hon_30s():
    assert pw._cat_cua_so(np.zeros(16000 * 12, dtype="float32")) == [(0, 16000 * 12)]


def test_moc_cua_so_sau_duoc_cong_do_lech(monkeypatch, tmp_path):
    with wave.open(str(tmp_path / "dai.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes((np.full(16000 * 40, 3000, dtype="<i2")).tobytes())
    _gia(monkeypatch, [_ra([(" một", 0.5, LP)], end=1.0), _ra([(" hai", 0.5, LP)], end=1.0)])
    r = pw.PhoWhisperProvider().transcribe(tmp_path / "dai.wav")
    assert len(r.segments) == 2 and r.segments[1].start_time > 20


@pytest.mark.skipif(os.environ.get("ASR_INTEGRATION") != "1", reason="dat ASR_INTEGRATION=1 de chay mo hinh that")
def test_tich_hop_phowhisper_small_that():
    am = Path(os.environ.get("ASR_TEST_WAV", "data/audio-bench/wav/c05a__vais1000__sach.wav"))
    r = pw.PhoWhisperProvider("vinai/PhoWhisper-small").transcribe(am)
    assert r.segments and r.timestamp_level == "word" and r.segments[0].start_time is not None
    assert not r.notes


@pytest.mark.skipif(os.environ.get("ASR_INTEGRATION") != "1", reason="dat ASR_INTEGRATION=1 de chay mo hinh that")
def test_tich_hop_chu_co_dau_khong_bi_vo():
    """Loi 22/09: giai ma tung token byte rieng le lam 'đỡ' thanh 'đ��' va dinh 'trămmilygam'."""
    am = Path("data/audio-bench/wav/d04__vais1000__sach.wav")
    r = pw.PhoWhisperProvider("vinai/PhoWhisper-small").transcribe(am)
    chu = " ".join(s.text for s in r.segments)
    assert "�" not in chu and "đỡ" in chu
    assert all("�" not in w.text for s in r.segments for w in s.words)
    assert r.segments[0].asr_confidence is not None
