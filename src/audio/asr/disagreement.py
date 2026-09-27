"""Run two ASR providers on the same audio and flag critical disagreements.

If the two transcripts differ on a drug name, a dose, a number, a negation, a time
expression, a medication state or who is being talked about, the segment gets
``asr_review_required = True`` with both candidates. The system NEVER picks one:
a human listens again and decides.
"""

from __future__ import annotations

from typing import Any

from . import critical_tokens as ct
from .schemas import ASRResult


def _overlap(a0, a1, b0, b1) -> float:
    if None in (a0, a1, b0, b1):
        return 0.0
    return max(0.0, min(a1, b1) - max(a0, b0))


def compare(primary: ASRResult, secondary: ASRResult) -> list[dict[str, Any]]:
    """-> one review item per primary segment whose critical tokens differ from the
    secondary transcript over the same time window."""
    items = []
    co_moc = all(s.start_time is not None for s in primary.segments + secondary.segments)
    for s in primary.segments:
        if co_moc:
            ben_kia = [x for x in secondary.segments
                       if _overlap(s.start_time, s.end_time, x.start_time, x.end_time) > 0]
        else:                                  # khong co moc: so ca ban chep
            ben_kia = secondary.segments if len(primary.segments) == 1 else []
        chu_kia = " ".join(x.text for x in ben_kia)
        loai = ct.khac_nhau(ct.trich(s.text), ct.trich(chu_kia))
        if loai:
            items.append({
                "segment_id": s.segment_id,
                "asr_review_required": True,
                "reason": ct.LY_DO[loai[0]],
                "reasons": sorted({ct.LY_DO[k] for k in loai}),
                "start_time": s.start_time, "end_time": s.end_time,
                "candidates": [
                    {"provider": primary.provider, "model": primary.model, "text": s.text},
                    {"provider": secondary.provider, "model": secondary.model, "text": chu_kia},
                ],
            })
    return items
