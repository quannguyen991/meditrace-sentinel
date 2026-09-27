# -*- coding: utf-8 -*-
"""Adapter sang dau vao loi MediTrace (yeu cau XVI)."""
import pytest

from src.audio.adapter import to_meditrace

SEGS = [
    {"segment_id": "seg_1", "speaker_id": "speaker_1", "speaker_role": "doctor",
     "text_original": "Cô ho bao lâu rồi?", "start_time": 0.0, "end_time": 1.5,
     "asr_provider": "phowhisper", "asr_model": "vinai/PhoWhisper-medium"},
    {"segment_id": "seg_2", "speaker_id": "speaker_2", "speaker_role": "patient",
     "text_original": "Khoảng một tuần, à không, mười ngày.", "text_normalized": "10 ngày",
     "start_time": 11.2, "end_time": 15.9, "asr_provider": "phowhisper", "asr_model": "vinai/PhoWhisper-medium"},
]


def test_ra_dung_chuoi_input_cua_loi():
    r = to_meditrace(SEGS, strict=True)
    assert r["input"] == "Bác sĩ: Cô ho bao lâu rồi?\nBệnh nhân: Khoảng một tuần, à không, mười ngày."
    assert r["turns"][1] == {"luot": 2, "nguoi_noi": "benh_nhan", "noi_dung": "Khoảng một tuần, à không, mười ngày."}


def test_sieu_du_lieu_am_thanh_tach_rieng():
    m = to_meditrace(SEGS)["metadata"][1]
    assert (m["utterance_id"], m["audio_start"], m["audio_end"]) == (2, 11.2, 15.9)
    assert m["asr_provider"] == "phowhisper" and m["asr_model"] == "vinai/PhoWhisper-medium"


def test_khong_dung_ban_chuan_hoa():
    assert "10 ngày" not in to_meditrace(SEGS)["input"]


def test_vai_chua_ro_bi_chan_o_che_do_chat():
    with pytest.raises(ValueError, match="speaker_unknown"):
        to_meditrace([dict(SEGS[0], speaker_role="unknown")], strict=True)
