# -*- coding: utf-8 -*-
"""Hai ASR bat dong o thong tin quan trong -> bat duyet, KHONG tu chon (yeu cau XIV)."""
from src.audio.asr.disagreement import compare
from src.audio.asr.schemas import ASRResult, ASRSegment


def _r(provider, text, a=0.0, b=3.0):
    return ASRResult(provider, provider + "-m", "vi", [ASRSegment("seg_001", a, b, text)])


def test_lieu_bat_dong_thi_bat_duyet_va_giu_ca_hai():
    items = compare(_r("phowhisper", "metformin 500 mg"), _r("faster_whisper", "metformin 50 mg"))
    assert len(items) == 1
    it = items[0]
    assert it["asr_review_required"] is True and it["reason"] == "dosage_disagreement"
    texts = {c["provider"]: c["text"] for c in it["candidates"]}
    assert texts == {"phowhisper": "metformin 500 mg", "faster_whisper": "metformin 50 mg"}


def test_giong_nhau_thi_khong_bat_duyet():
    assert compare(_r("phowhisper", "không dị ứng thuốc"), _r("faster_whisper", "Không dị ứng thuốc.")) == []


def test_phu_dinh_bat_dong():
    items = compare(_r("phowhisper", "có dị ứng penicillin"), _r("faster_whisper", "không dị ứng penicillin"))
    assert items and items[0]["reason"] == "negation_disagreement"


def test_nguoi_bat_dong():
    items = compare(_r("phowhisper", "bố bệnh nhân bị hen"), _r("faster_whisper", "bệnh nhân bị hen"))
    assert items and "subject_disagreement" in items[0]["reasons"]


def test_so_khop_theo_moc_thoi_gian():
    """Chi so voi doan cua ben kia trung thoi gian — doan o cho khac khong tinh."""
    a = ASRResult("phowhisper", "m", "vi", [ASRSegment("seg_001", 0, 2, "uống 5 mg"),
                                           ASRSegment("seg_002", 5, 7, "ho mười ngày")])
    b = ASRResult("faster_whisper", "m", "vi", [ASRSegment("seg_001", 0, 2, "uống 5 mg"),
                                               ASRSegment("seg_002", 5, 7, "ho một ngày")])
    items = compare(a, b)
    assert [i["segment_id"] for i in items] == ["seg_002"]
    assert items[0]["reason"] == "time_disagreement"
