"""Common output schema for every ASR provider, and the error contract.

Every provider returns an ``ASRResult``. The pipeline never reads provider
specific fields, so providers can be swapped by configuration.

Three notions are kept apart on purpose (see docs/tai-lieu/thiet-ke-dau-vao-am-thanh.md):

* ``asr_confidence``  how sure the recogniser is about the WORDS it heard.
* clinical certainty  how sure the SPEAKER is about the fact (core MediTrace field
                      ``do_chac_chan``) — never derived from audio.
* evidence status     whether MediTrace has grounds to publish the claim (core gate).

``asr_confidence`` is ``None`` when the provider does not expose a meaningful
number. It is never invented.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

ERROR_CODES = {
    "audio_invalid": "Tệp âm thanh không hợp lệ.",
    "audio_conversion_failed": "Không chuyển được âm thanh sang WAV 16 kHz mono.",
    "phowhisper_load_failed": "Không nạp được mô hình PhoWhisper.",
    "phowhisper_inference_failed": "PhoWhisper lỗi khi nhận dạng.",
    "asr_load_failed": "Không nạp được mô hình nhận dạng giọng nói.",
    "asr_inference_failed": "Mô hình nhận dạng giọng nói lỗi khi chạy.",
    "asr_provider_unknown": "Tên nhà cung cấp ASR không có trong sổ đăng ký.",
    "asr_provider_external_blocked": "Nhà cung cấp gửi âm thanh ra ngoài bị chặn ở chế độ local.",
    "timestamp_alignment_failed": "Không ghép được mốc thời gian với người nói.",
    "diarization_failed": "Tách người nói lỗi.",
    "asr_disagreement": "Hai bộ nhận dạng không thống nhất ở thông tin quan trọng.",
    "low_quality_audio": "Âm thanh quá nhỏ, bị méo hoặc quá ngắn.",
}

# Loi nao nguoi dung thu lai duoc (doi mang, doi may, ghi lai am thanh)
_RECOVERABLE = {"audio_invalid": True, "audio_conversion_failed": True,
                "phowhisper_load_failed": True, "phowhisper_inference_failed": True,
                "asr_load_failed": True, "asr_inference_failed": True,
                "asr_provider_unknown": False, "asr_provider_external_blocked": False,
                "timestamp_alignment_failed": True, "diarization_failed": True,
                "asr_disagreement": True, "low_quality_audio": True}


class ASRError(RuntimeError):
    """Error with a stable code. ``str(err)`` is the code, so the existing pipeline
    (which stores ``str(exc)`` as the error code) keeps working."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(code)
        self.code = code
        self.detail = detail

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": ERROR_CODES.get(self.code, self.code),
                "recoverable": _RECOVERABLE.get(self.code, True)}


@dataclass
class ASRWord:
    text: str
    start_time: Optional[float]
    end_time: Optional[float]


@dataclass
class ASRSegment:
    segment_id: str
    start_time: Optional[float]
    end_time: Optional[float]
    text: str
    asr_confidence: Optional[float] = None
    words: list[ASRWord] = field(default_factory=list)


@dataclass
class ASRResult:
    provider: str
    model: str
    language: str
    segments: list[ASRSegment]
    revision: Optional[str] = None
    device: Optional[str] = None
    dtype: Optional[str] = None
    timestamp_level: str = "segment"          # "word" | "segment" | "none"
    inference_config: dict[str, Any] = field(default_factory=dict)
    processing_seconds: Optional[float] = None
    audio_duration: Optional[float] = None
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def as_legacy(self) -> dict[str, Any]:
        """Shape understood by ``alignment.align`` (and by old callers)."""
        return {
            "provider": self.provider, "model": self.model, "language": self.language,
            "timestamp_level": self.timestamp_level,
            "segments": [{
                "segment_id": s.segment_id, "start": s.start_time, "end": s.end_time,
                "text": s.text, "confidence": s.asr_confidence,
                "words": [asdict(w) for w in s.words],
            } for s in self.segments],
        }
