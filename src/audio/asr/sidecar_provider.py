"""Deterministic provider reading a JSON transcript next to the audio.

Used for demos, offline tests and fixtures. Wraps the legacy
``providers.JsonSidecarASRProvider`` into the common ``ASRResult`` schema.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .base import ASRProvider
from .schemas import ASRError, ASRResult, ASRSegment, ASRWord


class SidecarProvider(ASRProvider):
    name = "sidecar"
    external = False

    def __init__(self, sidecar_path: Optional[str | Path] = None):
        self.sidecar_path = Path(sidecar_path) if sidecar_path else None

    def transcribe(self, audio_path: str | Path) -> ASRResult:
        p = self.sidecar_path or Path(audio_path).with_suffix(".json")
        if not p.exists():
            raise ASRError("asr_inference_failed", "asr_sidecar_missing")
        data = json.loads(p.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("segments")
        if items is None:
            raise ASRError("asr_inference_failed", "asr_sidecar_invalid")
        segs = []
        for i, s in enumerate(items, 1):
            words = [ASRWord(w.get("text", ""), w.get("start_time", w.get("start")),
                             w.get("end_time", w.get("end"))) for w in s.get("words", [])]
            segs.append(ASRSegment(s.get("segment_id", f"seg_{i:03d}"),
                                   s.get("start_time", s.get("start")), s.get("end_time", s.get("end")),
                                   str(s.get("text", "")).strip(),
                                   s.get("asr_confidence", s.get("confidence")), words))
        lang = "vi" if isinstance(data, list) else data.get("language", "vi")
        return ASRResult(provider=self.name, model="sidecar-json", language=lang, segments=segs,
                         timestamp_level="word" if any(s.words for s in segs) else "segment")
