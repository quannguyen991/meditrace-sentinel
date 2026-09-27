import json
import math
import wave
from pathlib import Path

from src.audio.adapter import to_meditrace
from src.audio.alignment import align
from src.audio.models import SpeakerRole
from src.audio.pipeline import AudioPipeline
from src.audio.storage import SessionStore


def test_alignment_keeps_text_timestamps_and_unknown_role():
    items = align("session_x", {"language": "vi", "segments": [{"start": 1.2, "end": 3.4, "text": "Bố em bị hen.", "confidence": 0.9}]}, [{"speaker_id": "speaker_2", "start": 1, "end": 4}])
    assert items[0].speaker_id == "speaker_2"
    assert items[0].speaker_role == SpeakerRole.UNKNOWN.value
    assert items[0].text_original == "Bố em bị hen."
    assert items[0].audio_reference["start_time"] == 1.2


def test_adapter_does_not_turn_family_member_subject_into_patient():
    result = to_meditrace([{"segment_id": "seg_1", "speaker_id": "speaker_2", "speaker_role": "family_member", "text_original": "Bố em bị hen.", "start_time": 0, "end_time": 2, "asr_confidence": 0.8}])
    assert result["turns"][0] == {"luot": 1, "nguoi_noi": "nguoi_nha", "noi_dung": "Bố em bị hen."}
    assert result["metadata"][0]["speaker_role"] == "family_member"


def test_pipeline_fixture_end_to_end(tmp_path):
    store = SessionStore(tmp_path)

    class FakePreprocessor:
        def convert(self, source, target):
            target.write_bytes(b"wav")
            target.with_suffix(".json").write_text(json.dumps({"sample_rate": 16000, "channels": 1, "duration": 4.0, "segments": [{"start": 0.2, "end": 2.1, "text": "một tuần… à không, mười ngày", "confidence": 0.91}]}), encoding="utf-8")
            return {"sample_rate": 16000, "channels": 1, "duration": 4.0}

    class FakeVAD:
        def detect(self, _): return [{"start": 0.2, "end": 2.1}]

    class FakeDiarization:
        def diarize(self, _, speech): return [{"speaker_id": "speaker_1", **speech[0]}]

    class FakeASR:
        def transcribe(self, _): return {"language": "vi", "segments": [{"start": 0.2, "end": 2.1, "text": "một tuần… à không, mười ngày", "confidence": 0.91}]}

    pipeline = AudioPipeline(store, asr=FakeASR(), preprocessor=FakePreprocessor(), vad=FakeVAD(), diarization=FakeDiarization())
    session = store.create(); raw = store.path(session["session_id"], "raw.webm"); raw.write_bytes(b"raw")
    pipeline.upload(session["session_id"], b"raw", "raw.webm")
    result = pipeline.process(session["session_id"])
    assert result["status"] == "transcript_ready"
    assert pipeline.transcript(session["session_id"])[0]["text_original"].endswith("mười ngày")
    pipeline.map_speakers(session["session_id"], {"speaker_1": "family_member"})
    assert pipeline.meditrace_input(session["session_id"])["turns"][0]["nguoi_noi"] == "nguoi_nha"
