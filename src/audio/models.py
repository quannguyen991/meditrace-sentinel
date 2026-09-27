"""Data contracts for the audio intake pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class SessionStatus(str, Enum):
    CREATED = "created"
    RECORDING = "recording"
    RECORDED = "recorded"
    PROCESSING_AUDIO = "processing_audio"
    DIARIZING = "diarizing"
    TRANSCRIBING = "transcribing"
    TRANSCRIPT_READY = "transcript_ready"
    READY_FOR_MEDITRACE = "ready_for_meditrace"
    FAILED = "failed"


class SpeakerRole(str, Enum):
    DOCTOR = "doctor"
    PATIENT = "patient"
    FAMILY_MEMBER = "family_member"
    OTHER = "other"
    UNKNOWN = "unknown"


@dataclass
class TranscriptSegment:
    segment_id: str
    utterance_id: int
    speaker_id: str
    speaker_role: str
    start_time: float
    end_time: float
    text_original: str
    text_normalized: Optional[str] = None
    asr_confidence: Optional[float] = None
    audio_reference: dict[str, Any] = field(default_factory=dict)
    edited: bool = False
    original_asr_text: Optional[str] = None
    edited_at: Optional[str] = None
    edited_by: Optional[str] = None
    # Them 22/09/2026 — nguon goc ban chep va canh bao hai ASR bat dong.
    asr_provider: Optional[str] = None
    asr_model: Optional[str] = None
    asr_review_required: bool = False
    asr_review_reason: Optional[str] = None
    asr_candidates: list[dict[str, Any]] = field(default_factory=list)
    reviewed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "TranscriptSegment":
        return cls(**value)


def new_session(session_id: str) -> dict[str, Any]:
    stamp = now_iso()
    return {
        "session_id": session_id,
        "created_at": stamp,
        "recording_started_at": None,
        "recording_ended_at": None,
        "duration_seconds": 0.0,
        "status": SessionStatus.CREATED.value,
        "raw_audio_path": None,
        "processed_audio_path": None,
        "transcript_status": "not_started",
        "meditrace_status": "not_sent",
        "speaker_map": {},
        "error": None,
        "asr": None,
        "audio_quality": None,
    }
