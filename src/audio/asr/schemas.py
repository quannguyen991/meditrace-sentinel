"""[Âm thanh › Chép lời]
Làm gì   : Định nghĩa kiểu dữ liệu đầu ra chung của mọi bộ chép lời và lỗi chuẩn khi chép
           thất bại.
Đọc từ   : class ASRResult kết quả chép gồm các ASRSegment; class ASRError lỗi chuẩn
Mục lục (các hàm/lớp chính):
  class ASRResult   Kết quả chép lời chung của mọi nhà cung cấp
  class ASRSegment  Một đoạn chép lời kèm độ tin và danh sách từ
  class ASRWord     Một từ đã chép lời kèm mốc bắt đầu và kết thúc
  class ASRError    Lỗi chép lời có mã ổn định và cờ thử lại được
Dùng bởi : audio/asr/__init__, audio/asr/base, audio/asr/disagreement,
           audio/asr/faster_whisper_provider, audio/asr/phowhisper_provider,
           audio/asr/registry, audio/asr/sidecar_provider, audio/pipeline
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Lược đồ đầu ra chung cho mọi nhà cung cấp ASR, và hợp đồng lỗi.

Mọi nhà cung cấp trả về một ``ASRResult``. Đường ống không bao giờ đọc các trường
riêng của nhà cung cấp, nên có thể hoán đổi nhà cung cấp bằng cấu hình.

Ba khái niệm được cố ý tách riêng (xem docs/tai-lieu/thiet-ke-dau-vao-am-thanh.md):

* ``asr_confidence``  bộ nhận dạng chắc đến đâu về các TỪ đã nghe.
* độ chắc lâm sàng  NGƯỜI NÓI chắc đến đâu về dữ kiện (trường lõi MediTrace
                      ``do_chac_chan``) — không bao giờ suy ra từ âm thanh.
* trạng thái căn cứ   MediTrace có cơ sở để công bố mệnh đề hay không (chốt chặn lõi).

``asr_confidence`` là ``None`` khi nhà cung cấp không cung cấp con số
có ý nghĩa. Nó không bao giờ bị bịa.
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

# Lỗi nào người dùng thử lại được (đổi mạng, đổi máy, ghi lại âm thanh)
_RECOVERABLE = {"audio_invalid": True, "audio_conversion_failed": True,
                "phowhisper_load_failed": True, "phowhisper_inference_failed": True,
                "asr_load_failed": True, "asr_inference_failed": True,
                "asr_provider_unknown": False, "asr_provider_external_blocked": False,
                "timestamp_alignment_failed": True, "diarization_failed": True,
                "asr_disagreement": True, "low_quality_audio": True}


# ═══ class ASRError — Lỗi chép lời có mã ổn định và cờ thử lại được ═══════════════════
# str(lỗi) là mã; to_dict trả mã, thông báo tiếng Việt và recoverable.
class ASRError(RuntimeError):
    """Lỗi có mã ổn định. ``str(err)`` là mã lỗi, nên đường ống hiện có
    (lưu ``str(exc)`` làm mã lỗi) vẫn chạy được."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(code)
        self.code = code
        self.detail = detail

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": ERROR_CODES.get(self.code, self.code),
                "recoverable": _RECOVERABLE.get(self.code, True)}


# ═══ class ASRWord — Một từ đã chép lời kèm mốc bắt đầu và kết thúc ═══════════════════
@dataclass
class ASRWord:
    text: str
    start_time: Optional[float]
    end_time: Optional[float]


# ═══ class ASRSegment — Một đoạn chép lời kèm độ tin và danh sách từ ══════════════════
# asr_confidence chỉ là độ chắc của bộ nhận dạng về chữ, không phải độ chắc lâm sàng.
@dataclass
class ASRSegment:
    segment_id: str
    start_time: Optional[float]
    end_time: Optional[float]
    text: str
    asr_confidence: Optional[float] = None
    words: list[ASRWord] = field(default_factory=list)


# ═══ class ASRResult — Kết quả chép lời chung của mọi nhà cung cấp ════════════════════
# Có as_legacy để đưa vào alignment.align; confidence là None nếu nhà cung cấp không có.
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
        """Dạng dữ liệu ``alignment.align`` hiểu được (và các bên gọi cũ dùng)."""
        return {
            "provider": self.provider, "model": self.model, "language": self.language,
            "timestamp_level": self.timestamp_level,
            "segments": [{
                "segment_id": s.segment_id, "start": s.start_time, "end": s.end_time,
                "text": s.text, "confidence": s.asr_confidence,
                "words": [asdict(w) for w in s.words],
            } for s in self.segments],
        }
