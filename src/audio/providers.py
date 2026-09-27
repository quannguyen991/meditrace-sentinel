"""Provider interfaces and local MVP providers."""

from __future__ import annotations

import importlib
import json
import math
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


@dataclass
class ASRSegment:
    start: float
    end: float
    text: str
    confidence: float | None = None


class ASRProvider(Protocol):
    def transcribe(self, audio_path: str | Path) -> dict[str, Any]: ...


class DiarizationProvider(Protocol):
    def diarize(self, audio_path: str | Path, speech_segments: list[dict[str, float]]) -> list[dict[str, Any]]: ...


class JsonSidecarASRProvider:
    """Deterministic local provider for review, demos, and offline tests.

    A file named ``processed.json`` next to the WAV contains either a list of
    segments or ``{"language":"vi", "segments":[...]}``.
    """

    def __init__(self, sidecar_path: str | Path | None = None):
        self.sidecar_path = Path(sidecar_path) if sidecar_path else None

    def transcribe(self, audio_path: str | Path) -> dict[str, Any]:
        sidecar = self.sidecar_path or Path(audio_path).with_suffix(".json")
        if not sidecar.exists():
            raise RuntimeError("asr_sidecar_missing")
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
        if "segments" not in payload:
            raise RuntimeError("asr_sidecar_invalid")
        return {"language": payload.get("language", "vi"), "segments": payload["segments"]}


# Lop cu (Codex) da thay bang src/audio/asr/faster_whisper_provider.py (22/09/2026).
# Giu ten cu de ma goi cu khong gay.
from .asr.faster_whisper_provider import FasterWhisperProvider as FasterWhisperASRProvider  # noqa: E402


class EnergyVADProvider:
    def __init__(self, frame_ms: int = 30, threshold: int = 450):
        self.frame_ms, self.threshold = frame_ms, threshold

    def detect(self, audio_path: str | Path) -> list[dict[str, float]]:
        with wave.open(str(audio_path), "rb") as wav:
            if wav.getnchannels() != 1 or wav.getframerate() != 16000 or wav.getsampwidth() != 2:
                raise RuntimeError("vad_requires_16khz_mono_pcm")
            rate = wav.getframerate()
            frames = max(1, int(rate * self.frame_ms / 1000))
            active: list[tuple[float, float]] = []
            in_speech = None
            index = 0
            while True:
                data = wav.readframes(frames)
                if not data:
                    break
                samples = [int.from_bytes(data[i:i+2], "little", signed=True) for i in range(0, len(data) - 1, 2)]
                rms = math.sqrt(sum(s * s for s in samples) / max(1, len(samples)))
                start, end = index / rate, min(wav.getnframes() / rate, (index + len(samples)) / rate)
                if rms >= self.threshold and in_speech is None:
                    in_speech = start
                if rms < self.threshold and in_speech is not None:
                    active.append((in_speech, end)); in_speech = None
                index += len(samples)
            if in_speech is not None:
                active.append((in_speech, wav.getnframes() / rate))
        return [{"start": round(a, 3), "end": round(b, 3)} for a, b in active]


class SingleSpeakerDiarizationProvider:
    """Safe baseline: labels speech as speaker_1, never as doctor/patient."""

    def diarize(self, audio_path: str | Path, speech_segments: list[dict[str, float]]) -> list[dict[str, Any]]:
        return [{"speaker_id": "speaker_1", "start": s["start"], "end": s["end"]} for s in speech_segments]


class JsonDiarizationProvider:
    def __init__(self):
        self.last_info: dict[str, Any] = {}

    def diarize(self, audio_path: str | Path, speech_segments: list[dict[str, float]]) -> list[dict[str, Any]]:
        path = Path(audio_path).with_name("diarization.json")
        if not path.exists():
            self.last_info = {"phuong_phap": "mot_nguoi"}
            return SingleSpeakerDiarizationProvider().diarize(audio_path, speech_segments)
        self.last_info = {"phuong_phap": "tep_json"}
        value = json.loads(path.read_text(encoding="utf-8"))
        return value.get("segments", value) if isinstance(value, dict) else value
