# -*- coding: utf-8 -*-
"""Ghep ban chep ASR voi tach nguoi noi (yeu cau VII, VIII)."""
from src.audio.alignment import align
from src.audio.asr.schemas import ASRResult, ASRSegment, ASRWord


def _ket_qua(words):
    ws = [ASRWord(t, a, b) for t, a, b in words]
    seg = ASRSegment("seg_001", ws[0].start_time, ws[-1].end_time, "".join(w.text for w in ws).strip(), None, ws)
    return ASRResult("phowhisper", "vinai/PhoWhisper-small", "vi", [seg], timestamp_level="word").as_legacy()


DIA = [{"speaker_id": "speaker_1", "start": 0.0, "end": 2.0},
       {"speaker_id": "speaker_2", "start": 2.0, "end": 5.0}]


def test_cat_doan_tai_cho_doi_nguoi_noi_theo_moc_tung_tu():
    asr = _ket_qua([(" Ho", 0.1, 0.4), (" bao", 0.5, 0.8), (" lâu?", 0.9, 1.5),
                    (" Mười", 2.2, 2.6), (" ngày.", 2.7, 3.3)])
    out = align("s", asr, DIA)
    assert [(o.speaker_id, o.text_original) for o in out] == [("speaker_1", "Ho bao lâu?"),
                                                              ("speaker_2", "Mười ngày.")]
    assert out[1].start_time == 2.2 and out[1].end_time == 3.3


def test_vai_luon_la_unknown_sau_ghep():
    out = align("s", _ket_qua([(" Bố", 2.1, 2.3), (" em", 2.3, 2.5), (" bị", 2.5, 2.7), (" hen.", 2.7, 3.0)]), DIA)
    assert {o.speaker_role for o in out} == {"unknown"}
    assert out[0].text_original == "Bố em bị hen."        # giu nguyen van, khong doi thanh "bệnh nhân"


def test_giu_nguon_goc_va_moc_am_thanh():
    out = align("phien_1", _ket_qua([(" Có", 0.2, 0.4), (" ạ.", 0.4, 0.6)]), DIA)
    assert out[0].asr_provider == "phowhisper" and out[0].asr_model == "vinai/PhoWhisper-small"
    assert out[0].audio_reference == {"session_id": "phien_1", "start_time": 0.2, "end_time": 0.6}


def test_khong_co_moc_tung_tu_thi_gan_ca_doan():
    asr = {"segments": [{"start": 2.1, "end": 4.0, "text": "Mười ngày.", "confidence": None}]}
    out = align("s", asr, DIA)
    assert out[0].speaker_id == "speaker_2" and out[0].text_original == "Mười ngày."
