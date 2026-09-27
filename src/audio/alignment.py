"""Align ASR spans and diarization spans without changing transcript text.

Two modes:

* word timestamps available: each WORD goes to the speaker whose span overlaps it
  most; a segment is cut where the speaker changes. Words keep their spelling.
* segment timestamps only: the whole segment goes to the speaker with the largest
  overlap (previous behaviour).

Speaker ROLES are never set here: every segment leaves as ``unknown``. Only the human
review step (``AudioPipeline.map_speakers``) turns speaker_1 into doctor/patient/…

Accepts the legacy dict ``{"segments": [{"start", "end", "text", "confidence"}]}`` and
``ASRResult.as_legacy()`` (which adds ``provider``, ``model`` and ``words``).
"""

from __future__ import annotations

from typing import Any, Optional

from .models import SpeakerRole, TranscriptSegment


def _overlap(a0, a1, b0, b1) -> float:
    if None in (a0, a1, b0, b1):
        return 0.0
    return max(0.0, min(float(a1), float(b1)) - max(float(a0), float(b0)))


# Tu nam lot khe giua hai doan cua bo tach nguoi noi (khong trung doan nao) thi gan cho
# doan GAN NHAT, neu cach khong qua chung nay giay. Xa hon thi de "unknown".
KHE_TOI_DA = 1.0

# PhoWhisper chi cho moc BAT DAU cua tu (DTW); moc ket thuc la moc bat dau cua tu sau
# (toi da +1,2 s), nen tu cuoi mot luot keo dai sang khoang lang, co khi sang ca luot cua
# nguoi ke tiep. Gan nguoi noi theo chung nay giay DAU cua tu (mot am tiet ~0,15-0,35 s).
DO_DAI_GAN = 0.3

# Hai tu roi vao hai khoang co tieng noi cach nhau >= chung nay giay thi cat dong, ke ca khi
# cung nguoi noi. Khi khong tach nguoi noi, day la cho duy nhat cat dong theo khoang lang:
# quy tac "khoang lang > 0,8 s" cua bo chep loi gan nhu khong chay vi moc ket thuc la uoc.
KHE_CAT_DOAN = 0.6


def _span_for(start, end, diarization: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    best, best_ov = None, 0.0
    for d in diarization:
        ov = _overlap(start, end, d.get("start"), d.get("end"))
        if ov > best_ov:
            best, best_ov = d, ov
    if best is None and start is not None and end is not None:
        gan, khe_min = None, KHE_TOI_DA
        for d in diarization:
            if d.get("start") is None or d.get("end") is None:
                continue
            khe = max(float(d["start"]) - float(end), float(start) - float(d["end"]), 0.0)
            if khe <= khe_min:
                gan, khe_min = d, khe
        best = gan
    return best


def _speaker_for(start, end, diarization: list[dict[str, Any]]) -> str:
    best = _span_for(start, end, diarization)
    return str(best.get("speaker_id", "unknown")) if best else "unknown"


def _cach_lang(truoc: Optional[dict], sau: Optional[dict]) -> bool:
    """Hai khoang co tieng noi khac nhau, cach nhau mot khoang lang du dai de cat dong."""
    if truoc is None or sau is None or truoc is sau:
        return False
    try:
        return float(sau["start"]) - float(truoc["end"]) >= KHE_CAT_DOAN
    except (KeyError, TypeError, ValueError):
        return False


def _get(raw: dict, *keys, default=None):
    for k in keys:
        if raw.get(k) is not None:
            return raw[k]
    return default


def align(session_id: str, asr: dict[str, Any], diarization: list[dict[str, Any]]) -> list[TranscriptSegment]:
    provider: Optional[str] = asr.get("provider")
    model: Optional[str] = asr.get("model")
    pieces: list[tuple[str, Optional[float], Optional[float], str, Any]] = []
    for raw in asr.get("segments", []):
        text = str(raw.get("text", "")).strip()
        if not text:
            continue
        start, end = _get(raw, "start", "start_time"), _get(raw, "end", "end_time")
        conf = _get(raw, "confidence", "asr_confidence")
        words = [w for w in raw.get("words") or [] if w.get("text", "").strip()]
        timed = words and all(_get(w, "start_time", "start") is not None for w in words)
        if not timed:
            pieces.append((_speaker_for(start, end, diarization), start, end, text, conf))
            continue
        # Cat theo nguoi noi tung tu, va o khoang lang dai giua hai khoang co tieng noi.
        # Chu ghep lai tu chinh cac tu cua mo hinh.
        cur_spk, cur_span, cur = None, None, []
        for w in words:
            ws, we = _get(w, "start_time", "start"), _get(w, "end_time", "end")
            gan_den = min(float(we), float(ws) + DO_DAI_GAN) if we is not None else float(ws) + DO_DAI_GAN
            span = _span_for(ws, max(gan_den, float(ws)), diarization)
            spk = str(span.get("speaker_id", "unknown")) if span else "unknown"
            if cur and (spk != cur_spk or _cach_lang(cur_span, span)):
                pieces.append((cur_spk, cur[0][1], cur[-1][2], "".join(x[0] for x in cur).strip(), conf))
                cur = []
            cur_spk = spk
            if span is not None:
                cur_span = span
            cur.append((w["text"], ws, we))
        if cur:
            pieces.append((cur_spk, cur[0][1], cur[-1][2], "".join(x[0] for x in cur).strip(), conf))

    result: list[TranscriptSegment] = []
    for index, (spk, start, end, text, conf) in enumerate(pieces, 1):
        if not text:
            continue
        s0 = float(start) if start is not None else 0.0
        s1 = float(end) if end is not None else s0
        result.append(TranscriptSegment(
            segment_id=f"seg_{index:04d}", utterance_id=index, speaker_id=spk,
            speaker_role=SpeakerRole.UNKNOWN.value, start_time=s0, end_time=s1,
            text_original=text, asr_confidence=conf,
            audio_reference={"session_id": session_id, "start_time": s0, "end_time": s1},
            asr_provider=provider, asr_model=model,
        ))
    return result


def gop_lien_tiep(doan: list[TranscriptSegment]) -> list[TranscriptSegment]:
    """Gop cac doan LIEN TIEP cung nguoi noi thanh MOT luot.

    Mot luot thoai la mot lan mot nguoi noi, tu luc bat dau den luc nguoi khac noi. `align`
    cat dong o khoang lang dai (KHE_CAT_DOAN) va bo tach co the chia mot nguoi thanh nhieu
    khoang, nen mot nguoi ngung giua chung bi chia thanh nhieu dong. CHI dung khi da tach
    that ra tu hai nguoi noi tro len; neu ca ban ghi la mot nguoi noi thi ham nay se gop het
    thanh mot dong.

    Do tin gop = do tin THAP NHAT (canh bao dua tren nguong 0,6 khong duoc mat vi gop).
    Doan co speaker_id "unknown" khong gop voi doan nao.
    """
    ra: list[TranscriptSegment] = []
    for d in doan:
        truoc = ra[-1] if ra else None
        if (truoc is not None and d.speaker_id == truoc.speaker_id and d.speaker_id != "unknown"):
            truoc.text_original = f"{truoc.text_original} {d.text_original}".strip()
            truoc.end_time = d.end_time
            cs = [c for c in (truoc.asr_confidence, d.asr_confidence) if c is not None]
            truoc.asr_confidence = min(cs) if cs else None
            truoc.audio_reference = {**truoc.audio_reference, "end_time": d.end_time}
            continue
        ra.append(d)
    for i, d in enumerate(ra, 1):
        d.segment_id, d.utterance_id = f"seg_{i:04d}", i
    return ra
