"""ASR providers for the audio intake layer. See docs/tai-lieu/ke-hoach-phowhisper.md."""

from .base import ASRProvider
from .schemas import ASRError, ASRResult, ASRSegment, ASRWord

__all__ = ["ASRProvider", "ASRError", "ASRResult", "ASRSegment", "ASRWord"]
