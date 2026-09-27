"""Audio intake pipeline for MediTrace Sentinel.

The package deliberately stops at a reviewed transcript. It does not infer
clinical facts or replace the existing MediTrace core.
"""

from .models import SessionStatus, SpeakerRole, TranscriptSegment

__all__ = ["SessionStatus", "SpeakerRole", "TranscriptSegment"]
