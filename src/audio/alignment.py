"""[Âm thanh]
Làm gì   : Gán người nói cho từng đoạn chép lời bằng cách đối chiếu mốc thời gian, không đổi
           chữ đã chép.
Vào → Ra : đoạn chép lời + đoạn người nói → các lượt thoại có nhãn người nói, đã gộp đoạn
           liền nhau
Đọc từ   : align() ghép chữ với người nói theo độ chồng lấn; gop_lien_tiep() gộp lượt
Mục lục (các hàm/lớp chính):
  align()          Ghép chép lời với tách người nói thành các đoạn
  gop_lien_tiep()  Gộp các đoạn liền nhau cùng người nói thành một lượt
Gọi tới  : audio/models
Dùng bởi : audio/pipeline
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Căn chỉnh khoảng ASR với khoảng tách người nói mà không đổi văn bản bản chép lời.

Hai chế độ:

* có mốc thời gian theo từ: mỗi TỪ thuộc về người nói có khoảng trùng với nó
  nhiều nhất; đoạn bị cắt tại chỗ người nói đổi. Từ giữ nguyên chính tả.
* chỉ có mốc thời gian theo đoạn: cả đoạn thuộc về người nói có phần trùng
  lớn nhất (hành vi trước đây).

VAI của người nói không bao giờ được đặt ở đây: mọi đoạn đều ra là ``unknown``. Chỉ bước duyệt
của con người (``AudioPipeline.map_speakers``) mới đổi speaker_1 thành bác sĩ/bệnh nhân/…

Nhận dict cũ ``{"segments": [{"start", "end", "text", "confidence"}]}`` và
``ASRResult.as_legacy()`` (có thêm ``provider``, ``model`` và ``words``).
"""

from __future__ import annotations

from typing import Any, Optional

from .models import SpeakerRole, TranscriptSegment


# ─── _overlap() — Tính độ chồng lấn giữa hai khoảng thời gian ─────────────────────────
def _overlap(a0, a1, b0, b1) -> float:
    if None in (a0, a1, b0, b1):
        return 0.0
    return max(0.0, min(float(a1), float(b1)) - max(float(a0), float(b0)))


# Từ nằm lọt khe giữa hai đoạn của bộ tách người nói (không trùng đoạn nào) thì gán cho
# đoạn GẦN NHẤT, nếu cách không quá chừng này giây. Xa hơn thì để "unknown".
KHE_TOI_DA = 1.0

# PhoWhisper chỉ cho mốc BẮT ĐẦU của từ (DTW); mốc kết thúc là mốc bắt đầu của từ sau
# (tối đa +1,2 s), nên từ cuối một lượt kéo dài sang khoảng lặng, có khi sang cả lượt của
# người kế tiếp. Gán người nói theo chừng này giây ĐẦU của từ (một âm tiết ~0,15-0,35 s).
DO_DAI_GAN = 0.3

# Hai từ rơi vào hai khoảng có tiếng nói cách nhau >= chừng này giây thì cắt dòng, kể cả khi
# cùng người nói. Khi không tách người nói, đây là chỗ duy nhất cắt dòng theo khoảng lặng:
# quy tắc "khoảng lặng > 0,8 s" của bộ chép lời gần như không chạy vì mốc kết thúc là ước.
KHE_CAT_DOAN = 0.6


# ─── _span_for() — Tìm khoảng người nói trùng nhiều nhất với một mốc ──────────────────
# Không trùng thì lấy khoảng gần nhất trong KHE_TOI_DA giây; xa hơn trả None.
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


# ─── _speaker_for() — Lấy mã người nói cho một mốc thời gian ──────────────────────────
# Không tìm được khoảng nào thì trả unknown.
def _speaker_for(start, end, diarization: list[dict[str, Any]]) -> str:
    best = _span_for(start, end, diarization)
    return str(best.get("speaker_id", "unknown")) if best else "unknown"


# ─── _cach_lang() — Kiểm tra hai khoảng nói có đủ lặng để cắt dòng ────────────────────
def _cach_lang(truoc: Optional[dict], sau: Optional[dict]) -> bool:
    """Hai khoảng có tiếng nói khác nhau, cách nhau một khoảng lặng đủ dài để cắt dòng."""
    if truoc is None or sau is None or truoc is sau:
        return False
    try:
        return float(sau["start"]) - float(truoc["end"]) >= KHE_CAT_DOAN
    except (KeyError, TypeError, ValueError):
        return False


# ─── _get() — Lấy giá trị đầu tiên khác rỗng theo danh sách khoá ──────────────────────
def _get(raw: dict, *keys, default=None):
    for k in keys:
        if raw.get(k) is not None:
            return raw[k]
    return default


# ═══ align() — Ghép chép lời với tách người nói thành các đoạn ════════════════════════
# Có mốc từng từ thì mỗi từ về người nói trùng nhiều nhất; không thì cả đoạn. Vai luôn
# là unknown, chữ giữ nguyên.
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
        # Cắt theo người nói từng từ, và ở khoảng lặng dài giữa hai khoảng có tiếng nói.
        # Chữ ghép lại từ chính các từ của mô hình.
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


# ═══ gop_lien_tiep() — Gộp các đoạn liền nhau cùng người nói thành một lượt ═══════════
# Độ tin gộp lấy mức thấp nhất. Chỉ dùng khi đã tách thật từ hai người nói trở lên;
# unknown không gộp.
def gop_lien_tiep(doan: list[TranscriptSegment]) -> list[TranscriptSegment]:
    """Gộp các đoạn LIÊN TIẾP cùng người nói thành MỘT lượt.

    Một lượt thoại là một lần một người nói, từ lúc bắt đầu đến lúc người khác nói. `align`
    cắt dòng ở khoảng lặng dài (KHE_CAT_DOAN) và bộ tách có thể chia một người thành nhiều
    khoảng, nên một người ngưng giữa chừng bị chia thành nhiều dòng. CHỈ dùng khi đã tách
    thật ra từ hai người nói trở lên; nếu cả bản ghi là một người nói thì hàm này sẽ gộp hết
    thành một dòng.

    Độ tin gộp = độ tin THẤP NHẤT (cảnh báo dựa trên ngưỡng 0,6 không được mất vì gộp).
    Đoạn có speaker_id "unknown" không gộp với đoạn nào.
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
