"""Adapter from reviewed audio transcript to the existing MediTrace input.

The MediTrace core reads one string ``input`` with one turn per line, e.g.
``Bác sĩ: Cô ho bao lâu rồi?``. This adapter produces that string plus the turn
list, and keeps the audio metadata SEPARATE so the core schema is untouched.

Text used: ``text_original`` — what the recogniser heard, or what the reviewer typed
when editing. ``text_normalized`` is never sent to the core.
"""

from __future__ import annotations

from typing import Any

ROLE_TO_CORE = {"doctor": "bac_si", "patient": "benh_nhan", "family_member": "nguoi_nha",
                "other": "nguoi_khac", "unknown": "unknown"}
# Nhan vai trong chuoi `input` cua bo du lieu MediTrace
ROLE_LABEL = {"doctor": "Bác sĩ", "patient": "Bệnh nhân", "family_member": "Người nhà",
              "other": "Người khác"}


def to_meditrace(segments: list[dict[str, Any]], strict: bool = False) -> dict[str, Any]:
    """-> {"input": str, "turns": [...], "metadata": [...]}.

    ``strict=True`` refuses any segment whose role is still ``unknown``: the core
    must never guess who spoke.
    """
    turns, metadata, lines = [], [], []
    for index, segment in enumerate(segments, 1):
        text = (segment.get("text_original") or "").strip()
        role = segment.get("speaker_role", "unknown")
        if strict and role not in ROLE_LABEL:
            raise ValueError("speaker_unknown")
        turns.append({"luot": index, "nguoi_noi": ROLE_TO_CORE.get(role, "unknown"), "noi_dung": text})
        lines.append(f"{ROLE_LABEL.get(role, 'Chưa rõ')}: {text}")
        metadata.append({"luot": index, "utterance_id": index,
                         "segment_id": segment.get("segment_id"), "speaker_id": segment.get("speaker_id"),
                         "speaker_role": role, "audio_start": segment.get("start_time"),
                         "audio_end": segment.get("end_time"), "asr_confidence": segment.get("asr_confidence"),
                         "asr_provider": segment.get("asr_provider"), "asr_model": segment.get("asr_model"),
                         "edited": segment.get("edited", False)})
    return {"input": "\n".join(lines), "turns": turns, "metadata": metadata}
