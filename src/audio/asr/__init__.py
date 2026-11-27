"""[Âm thanh › Chép lời]
Làm gì   : Gom các nhà cung cấp chép lời tiếng Việt để tầng âm thanh chọn dùng.
Gọi tới  : audio/asr/base, audio/asr/schemas
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Các nhà cung cấp ASR cho lớp tiếp nhận âm thanh. Xem docs/tai-lieu/ke-hoach-phowhisper.md."""

from .base import ASRProvider
from .schemas import ASRError, ASRResult, ASRSegment, ASRWord

__all__ = ["ASRProvider", "ASRError", "ASRResult", "ASRSegment", "ASRWord"]
