"""[Âm thanh]
Làm gì   : Khai báo các kiểu dữ liệu của một phiên âm thanh: trạng thái, vai người nói, đoạn
           lời.
Đọc từ   : class TranscriptSegment một đoạn lời; new_session() tạo phiên mới
Mục lục (các hàm/lớp chính):
  class TranscriptSegment  Một lượt nói trong lời thoại kèm mốc và nguồn chép
  class SessionStatus      Các trạng thái của một phiên âm thanh
  class SpeakerRole        Các vai người nói được phép gán
  new_session()            Tạo bản ghi phiên âm thanh mới ở trạng thái created
Dùng bởi : audio/__init__, audio/alignment, audio/pipeline, audio/storage
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Hợp đồng dữ liệu cho đường ống tiếp nhận âm thanh."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


# ═══ now_iso() — Lấy thời điểm hiện tại theo UTC dạng ISO ═════════════════════════════
def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ═══ class SessionStatus — Các trạng thái của một phiên âm thanh ══════════════════════
# Từ created đến ready_for_meditrace hoặc failed.
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


# ═══ class SpeakerRole — Các vai người nói được phép gán ══════════════════════════════
# Bác sĩ, điều dưỡng, bệnh nhân, người nhà, khác, chưa rõ.
class SpeakerRole(str, Enum):
    DOCTOR = "doctor"
    NURSE = "nurse"
    PATIENT = "patient"
    FAMILY_MEMBER = "family_member"
    OTHER = "other"
    UNKNOWN = "unknown"


# ═══ class TranscriptSegment — Một lượt nói trong lời thoại kèm mốc và nguồn chép ═════
# Giữ chữ gốc, chữ đã sửa, độ tin, cờ cần nghe lại và các ứng viên chép lời.
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
    # Thêm 22/09/2026 — nguồn gốc bản chép và cảnh báo hai ASR bất đồng.
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


# ═══ new_session() — Tạo bản ghi phiên âm thanh mới ở trạng thái created ══════════════
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
