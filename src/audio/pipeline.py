"""Orchestration for an audio session."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .adapter import to_meditrace
from .alignment import align, gop_lien_tiep
from .asr import registry
from .asr.disagreement import compare as compare_asr
from .asr.schemas import ASRError, ASRResult
from .asr.sidecar_provider import SidecarProvider
from .config import AudioSettings
from .models import SessionStatus, SpeakerRole, now_iso
from .preprocessing import AudioPreprocessor
from .providers import EnergyVADProvider, JsonDiarizationProvider, SingleSpeakerDiarizationProvider
from .storage import SessionStore


def _bo_tach_mac_dinh(settings: AudioSettings):
    """Bo tach nguoi noi theo cau hinh. Cau hinh pyannote sai thi van chay duoc (lui ve
    mot nguoi noi o buoc process, co ghi ly do), khong lam hong viec chep loi."""
    if settings.diarization_provider == "pyannote":
        from .pyannote_provider import LoiTachNguoiNoi, PyannoteDiarizationProvider
        try:
            return PyannoteDiarizationProvider.from_settings(settings)
        except LoiTachNguoiNoi as exc:
            return _TachLoiCauHinh(str(exc))
    return JsonDiarizationProvider()


class _TachLoiCauHinh:
    """Giu cho: cau hinh pyannote thieu. Moi lan goi deu bao loi de pipeline lui ve."""

    tach_that = True
    ten = "pyannote"

    def __init__(self, ma: str):
        self.ma = ma

    def diarize(self, audio_path, speech_segments):
        raise RuntimeError(self.ma)


def goi_y_vai_nguoi_noi(transcript: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Gợi ý vai người nói tự động ('doctor' / 'patient' / 'family_member') khi diarization lùi về 1 người nói.
    Không ghi đè `speaker_role` (giữ nguyên để bác sĩ xác nhận), chỉ gắn `suggested_role`.
    """
    import re
    re_bac_si = re.compile(
        r"(?i)\b(chào\s+(?:bác|anh|chị|cô|chú|ông|bà|em|cháu)|"
        r"(?:bác|anh|chị|em|cháu)\s+(?:đau|sốt|ho|khó\s+thở|uống|dùng|bị)\s+(?:ở\s+đâu|bao\s+lâu|mấy\s+ngày|gì|chưa|không)|"
        r"để\s+(?:tôi|em|bác\s+sĩ)\s+(?:khám|nghe|đo|kê)|"
        r"(?:tôi|bác\s+sĩ)\s+(?:kê\s+đơn|cho\s+thuốc|hẹn\s+tái\s+khám|chỉ\s+định)|"
        r"huyết\s+áp\s+(?:đo\s+được|của\s+(?:bác|anh|chị)))\b"
    )
    re_nguoi_nha = re.compile(
        r"(?i)\b("
        r"con\s+(?:tôi|em|mình)|"
        r"(?:cháu|bé)\s+nhà\s+(?:em|tôi|mình)|"
        r"(?:mẹ|bố|ba|má|ông|bà|cụ|chồng|vợ)\s+(?:tôi|em)|"
        r"(?:nhà\s+em|nhà\s+tôi|gia\s+đình|em|tôi)\s+đưa\s+(?:cụ|ông|bà|bố|mẹ|cháu|bé|con|chồng|vợ)\s+(?:đi\s+khám|vào\s+viện|tới\s+khám|đến\s+khám)"
        r")\b"
    )
    re_benh_nhan = re.compile(
        r"(?i)\b(bác\s+sĩ\s+ơi|dạ\s+(?:vâng|có|không|đúng|thưa)|"
        r"(?:tôi|em|cháu|nhà\s+tôi)\s+(?:bị|đau|sốt|ho|mệt|khó\s+thở|uống|dùng|có\s+tiền\s+sử|dị\s+ứng)|"
        r"(?:tôi|em|cháu)\s+đau\s+quá)\b"
    )
    for seg in transcript:
        txt = (seg.get("text_normalized") or seg.get("text_original") or "").strip()
        if not txt:
            continue
        m_bs = re_bac_si.search(txt)
        m_nn = re_nguoi_nha.search(txt)
        m_bn = re_benh_nhan.search(txt)
        if m_bs and not m_nn and not m_bn:
            seg["suggested_role"] = "doctor"
            seg["suggested_role_reason"] = f"Khớp mẫu câu hỏi/chỉ định bác sĩ: '{m_bs.group(0)}'"
        elif m_nn and not m_bs:
            seg["suggested_role"] = "family_member"
            seg["suggested_role_reason"] = f"Khớp mẫu lời kể người nhà/chăm sóc: '{m_nn.group(0)}'"
        elif m_bn and not m_bs:
            seg["suggested_role"] = "patient"
            seg["suggested_role_reason"] = f"Khớp mẫu lời kể bệnh nhân: '{m_bn.group(0)}'"
        elif txt.endswith("?"):
            seg["suggested_role"] = "doctor"
            seg["suggested_role_reason"] = "Câu hỏi lâm sàng kết thúc bằng dấu hỏi"
    return transcript


def trich_dac_trung_giong_nhe(
    wav_path: Path,
    start_s: float = 0.0,
    end_s: float | None = None,
) -> list[float]:
    """Trích xuất vector đặc trưng âm học 8 chiều tất định (thuần `numpy` + `wave`, không thư viện nặng).

    8 chiều đã quy chuẩn tâm không (zero-centered acoustic contrast) để cosine similarity phân tách
    chính xác các giọng nói khác cao độ / âm sắc mà bất biến với âm lượng micro:
      [0] Độ lệch tần số cơ bản f0 so với 175 Hz
      [1] Độ mạnh tương quan tuần hoàn (pitch harmonicity / voicing clarity)
      [2] Độ lệch trọng tâm phổ (spectral centroid contrast)
      [3] Độ rộng phổ (spectral spread contrast)
      [4] Điểm cuộn phổ 85% (spectral rolloff contrast)
      [5] Tỷ lệ qua điểm không (zero-crossing rate contrast)
      [6] Tương phản năng lượng dải trầm (80-450 Hz) vs dải trung (450-1800 Hz)
      [7] Tương phản năng lượng dải trung (450-1800 Hz) vs dải cao (1800-4000 Hz)
    """
    import wave
    import numpy as np

    p = Path(wav_path)
    if not p.exists():
        return [0.0] * 8
    try:
        with wave.open(str(p), "rb") as wf:
            sr = wf.getframerate()
            n_ch = wf.getnchannels()
            sw = wf.getsampwidth()
            n_total = wf.getnframes()
            if sr <= 0 or n_total <= 0:
                return [0.0] * 8
            f_start = max(0, min(n_total, int(round(max(0.0, float(start_s)) * sr))))
            f_end = n_total if end_s is None else max(f_start, min(n_total, int(round(float(end_s) * sr))))
            if f_end - f_start < 64:
                return [0.0] * 8
            wf.setpos(f_start)
            raw = wf.readframes(f_end - f_start)
    except Exception:
        return [0.0] * 8

    if sw == 2:
        x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    elif sw == 1:
        x = (np.frombuffer(raw, dtype=np.uint8).astype(np.float64) - 128.0) / 128.0
    elif sw == 4:
        x = np.frombuffer(raw, dtype="<i4").astype(np.float64) / 2147483648.0
    else:
        return [0.0] * 8

    if n_ch > 1:
        x = x.reshape(-1, n_ch).mean(axis=1)
    if len(x) < 64:
        return [0.0] * 8

    x = x - float(np.mean(x))
    rms = float(np.sqrt(np.mean(x * x)))
    if rms < 1e-6:
        return [0.0] * 8
    x_norm = x / rms

    # 1. Ước lượng f0 bằng tự tương quan trên cửa sổ giọng nói (75 Hz .. 400 Hz)
    win_len = min(len(x_norm), int(sr * 1.5))
    seg = x_norm[:win_len]
    n_fft_ac = 1 << int(np.ceil(np.log2(max(128, 2 * len(seg)))))
    spec_ac = np.fft.rfft(seg, n=n_fft_ac)
    acf = np.fft.irfft(spec_ac * np.conj(spec_ac), n=n_fft_ac)[:len(seg)]
    acf0 = float(acf[0]) if acf[0] > 1e-9 else 1.0
    lag_min = max(1, int(sr / 400.0))
    lag_max = min(len(acf) - 1, int(sr / 75.0))
    if lag_max > lag_min:
        sub_acf = acf[lag_min:lag_max + 1]
        best_idx = int(np.argmax(sub_acf))
        lag_peak = lag_min + best_idx
        f0_hz = float(sr) / float(lag_peak)
        voicing = float(sub_acf[best_idx]) / acf0
    else:
        f0_hz = 175.0
        voicing = 0.0

    # 2. Đặc trưng phổ trung bình qua cửa sổ Hann
    win = np.hanning(len(seg))
    mag = np.abs(np.fft.rfft(seg * win)) + 1e-12
    freqs = np.fft.rfftfreq(len(seg), d=1.0 / sr)
    power = mag * mag
    total_pow = float(np.sum(power))

    centroid = float(np.sum(freqs * power)) / total_pow
    spread = float(np.sqrt(np.sum(((freqs - centroid) ** 2) * power) / total_pow))
    cumsum_pow = np.cumsum(power)
    rolloff_idx = int(np.searchsorted(cumsum_pow, 0.85 * total_pow))
    rolloff = float(freqs[min(rolloff_idx, len(freqs) - 1)])

    zcr = float(np.mean(np.abs(np.diff(np.signbit(seg)))))

    e_low = float(np.sum(power[(freqs >= 70.0) & (freqs < 450.0)])) / total_pow
    e_mid = float(np.sum(power[(freqs >= 450.0) & (freqs < 1800.0)])) / total_pow
    e_high = float(np.sum(power[(freqs >= 1800.0) & (freqs <= min(4500.0, sr / 2.0))])) / total_pow

    vec = [
        (f0_hz - 175.0) / 85.0,
        (voicing - 0.45) * 2.0,
        (centroid - 900.0) / 700.0,
        (spread - 650.0) / 500.0,
        (rolloff - 1600.0) / 1100.0,
        (zcr - 0.12) / 0.08,
        float(np.log((e_low + 1e-4) / (e_mid + 1e-4))) / 3.0,
        float(np.log((e_mid + 1e-4) / (e_high + 1e-4))) / 3.0,
    ]
    return [round(float(v), 6) for v in vec]


def khop_mau_giong_bac_si(
    transcript: list[dict[str, Any]],
    wav_path: Path,
    mau_vector: list[float],
    nguong_cosine: float = 0.92,
) -> list[dict[str, Any]]:
    """So khớp từng đoạn âm thanh với mẫu giọng bác sĩ 5s cục bộ (cosine >= 0.92 -> `suggested_role = 'doctor'`).
    TUYỆT ĐỐI không ghi đè `speaker_role` (bác sĩ vẫn là người xác nhận cuối cùng).
    """
    import numpy as np

    if not mau_vector or len(mau_vector) != 8 or not Path(wav_path).exists():
        return transcript
    ref = np.asarray(mau_vector, dtype=np.float64)
    ref_norm = float(np.linalg.norm(ref))
    if ref_norm < 1e-8:
        return transcript

    for seg in transcript:
        st = float(seg.get("start_time") or 0.0)
        et_raw = seg.get("end_time")
        et = float(et_raw) if et_raw is not None else None
        vec = trich_dac_trung_giong_nhe(Path(wav_path), st, et)
        v = np.asarray(vec, dtype=np.float64)
        v_norm = float(np.linalg.norm(v))
        if v_norm < 1e-8:
            continue
        sim = float(np.dot(v, ref) / (v_norm * ref_norm))
        seg["doctor_voiceprint_similarity"] = round(sim, 4)
        if sim >= nguong_cosine:
            seg["suggested_role"] = "doctor"
            seg["suggested_role_reason"] = (
                f"Khớp mẫu giọng bác sĩ cục bộ (cosine={sim:.3f} >= {nguong_cosine:.2f})"
            )
    return transcript


class AudioPipeline:
    def __init__(self, store: SessionStore, asr=None, preprocessor=None, vad=None, diarization=None, settings=None):
        self.store = store
        self.settings = settings or AudioSettings.from_env()
        self.asr = asr
        self.preprocessor = preprocessor or AudioPreprocessor()
        self.vad = vad or EnergyVADProvider()
        self.diarization = diarization or _bo_tach_mac_dinh(self.settings)

    def _tach_nguoi_noi(self, session_id: str, processed: Path, speech: list[dict[str, Any]], bat: bool = True):
        """-> (cac doan nguoi noi, thong tin). Bo tach that loi thi lui ve MOT nguoi noi.

        Thong tin luu vao phien (`tach_nguoi_noi`) de giao dien noi ro may da tach hay chua,
        va vi sao chua. Khong bao gio doan vai; chi co speaker_1, speaker_2...
        `bat=False`: nguoi goi biet chi co mot nguoi noi (vd cau hoi ghi bang micro), bo qua
        bo tach that cho nhanh.
        """
        that = bool(getattr(self.diarization, "tach_that", False))
        if that and not bat:
            return (SingleSpeakerDiarizationProvider().diarize(processed, speech),
                    {"phuong_phap": "mot_nguoi", "tach_that": False, "so_nguoi_noi": 1, "bo_qua": True})
        try:
            doan = self.diarization.diarize(processed, speech)
            info = dict(getattr(self.diarization, "last_info", {}) or {})
            info.setdefault("phuong_phap", getattr(self.diarization, "ten", "mot_nguoi") if that else "mot_nguoi")
            if not that:
                info["so_nguoi_noi"] = len({d.get("speaker_id") for d in doan}) or 1
            elif not doan:
                raise RuntimeError("pyannote_khong_thay_ai_noi")
            info["tach_that"] = that
            return doan, info
        except Exception as exc:
            if not that:
                raise
            ma = str(exc) or type(exc).__name__
            self.store.log(session_id, "diarization_failed", provider=getattr(self.diarization, "ten", "?"), code=ma)
            doan = SingleSpeakerDiarizationProvider().diarize(processed, speech)
            return doan, {"phuong_phap": "mot_nguoi", "tach_that": False, "so_nguoi_noi": 1,
                          "loi": ma, "lui_ve": True}

    def upload(self, session_id: str, data: bytes, filename: str = "raw.webm") -> dict[str, Any]:
        if not data:
            raise ValueError("upload_failed")
        suffix = Path(filename).suffix.lower() or ".webm"
        if suffix not in {".webm", ".wav", ".mp3", ".m4a", ".ogg", ".flac"}:
            raise ValueError("upload_failed")
        target = self.store.path(session_id, "raw" + suffix)
        target.write_bytes(data)
        value = self.store.update(session_id, raw_audio_path=str(target), status=SessionStatus.RECORDED.value, recording_ended_at=now_iso(), transcript_status="not_started")
        self.store.log(session_id, "audio_uploaded", bytes=len(data), extension=suffix)
        return value

    def start_recording(self, session_id: str) -> dict[str, Any]:
        value = self.store.update(session_id, status=SessionStatus.RECORDING.value, recording_started_at=now_iso(), error=None)
        self.store.log(session_id, "recording_started")
        return value

    def stop_recording(self, session_id: str) -> dict[str, Any]:
        value = self.store.update(session_id, status=SessionStatus.RECORDED.value, recording_ended_at=now_iso())
        self.store.log(session_id, "recording_stopped")
        return value

    def process(self, session_id: str, tach_nguoi_noi: bool = True) -> dict[str, Any]:
        session = self.store.load(session_id)
        raw = Path(session.get("raw_audio_path") or "")
        if not raw.exists():
            raise ValueError("upload_failed")
        self.store.update(session_id, status=SessionStatus.PROCESSING_AUDIO.value, error=None)
        self.store.log(session_id, "processing_started")
        try:
            processed = self.store.path(session_id, "processed.wav")
            metadata = self.preprocessor.convert(raw, processed)
            self.store.update(session_id, processed_audio_path=str(processed), duration_seconds=metadata["duration"])
            self.store.log(session_id, "audio_converted", sample_rate=metadata["sample_rate"], channels=metadata["channels"])
            speech = self.vad.detect(processed)
            self.store.path(session_id, "vad.json").write_text(json.dumps(speech, ensure_ascii=False, indent=2), encoding="utf-8")
            self.store.log(session_id, "vad_completed", segment_count=len(speech))
            self.store.update(session_id, status=SessionStatus.DIARIZING.value)
            diarization, tach_info = self._tach_nguoi_noi(session_id, processed, speech, tach_nguoi_noi)
            self.store.path(session_id, "diarization.json").write_text(json.dumps(diarization, ensure_ascii=False, indent=2), encoding="utf-8")
            self.store.update(session_id, tach_nguoi_noi=tach_info)
            self.store.log(session_id, "diarization_completed", segment_count=len(diarization),
                           method=tach_info.get("phuong_phap"), speaker_count=tach_info.get("so_nguoi_noi"))
            quality = metadata.get("quality")
            if quality:
                self.store.update(session_id, audio_quality=quality)
                if quality.get("warnings"):
                    self.store.log(session_id, "low_quality_audio", warnings=quality["warnings"])
            self.store.update(session_id, status=SessionStatus.TRANSCRIBING.value)
            asr_result, asr_info = self._run_asr(session_id, processed, raw)
            doan = align(session_id, asr_result, diarization)
            # Chi gop luot khi da tach THAT ra tu hai nguoi noi tro len. Mot nguoi noi (hoac may
            # tach khong phan biet duoc hai giong) ma gop thi ca cuoc kham thanh mot dong, nguoi
            # dung khong gan vai tung dong duoc nua; giu cac dong cat theo khoang lang.
            if (tach_info.get("tach_that") and (tach_info.get("so_nguoi_noi") or 0) >= 2
                    and self.settings.gop_luot_cung_nguoi_noi):
                doan = gop_lien_tiep(doan)
            transcript = [s.to_dict() for s in doan]
            if not tach_info.get("tach_that") or (tach_info.get("so_nguoi_noi") or 1) <= 1:
                goi_y_vai_nguoi_noi(transcript)
                mau_giong = session.get("doctor_voiceprint")
                if isinstance(mau_giong, list) and len(mau_giong) == 8:
                    khop_mau_giong_bac_si(transcript, processed, mau_giong)
            self._flag_disagreements(session_id, processed, raw, transcript, asr_info)
            self.store.path(session_id, "transcript.json").write_text(json.dumps(transcript, ensure_ascii=False, indent=2), encoding="utf-8")
            value = self.store.update(session_id, status=SessionStatus.TRANSCRIPT_READY.value, transcript_status="ready")
            self.store.log(session_id, "transcript_created", segment_count=len(transcript))
            return {**value, "transcript": transcript}
        except ASRError as exc:
            value = self.store.update(session_id, status=SessionStatus.FAILED.value, error=exc.to_dict())
            self.store.log(session_id, "processing_failed", code=exc.code)
            raise
        except Exception as exc:
            code = str(exc) if str(exc) else "processing_failed"
            value = self.store.update(session_id, status=SessionStatus.FAILED.value, error={"code": code, "message": "Không thể xử lý audio ở bước hiện tại.", "recoverable": code not in {"asr_provider_unavailable", "vad_requires_16khz_mono_pcm"}})
            self.store.log(session_id, "processing_failed", code=code)
            raise

    # -- ASR ----------------------------------------------------------------
    def _run_asr(self, session_id: str, processed: Path, raw: Path):
        """Chay ASR. Nha cung cap tiem vao (phep thu) co the tra dict kieu cu.

        Log: provider, model, thiet bi, thoi gian xu ly, thoi luong am thanh, trang
        thai. KHONG log noi dung ban chep.
        """
        t0 = time.time()
        info: dict[str, Any] = {"fallback": False}
        if self.asr is not None:
            out = self.asr.transcribe(processed)
            info["used"] = getattr(self.asr, "name", type(self.asr).__name__)
        else:
            primary = self._default_asr(processed, raw)
            out, info = registry.transcribe(self.settings, processed, primary)
        if isinstance(out, ASRResult):
            meta = {k: v for k, v in out.to_dict().items() if k != "segments"}
            asr_dict = out.as_legacy()
        else:
            meta = {"provider": info.get("used"), "model": out.get("model"), "language": out.get("language", "vi")}
            asr_dict = out
        meta.update({"fallback": info.get("fallback", False), "primary_error": info.get("primary_error"),
                     "processing_seconds_total": round(time.time() - t0, 3)})
        self.store.path(session_id, "asr_raw.json").write_text(
            json.dumps(out.to_dict() if isinstance(out, ASRResult) else out, ensure_ascii=False, indent=2), encoding="utf-8")
        self.store.update(session_id, asr=meta)
        self.store.log(session_id, "asr_completed", provider=meta.get("provider"), model=meta.get("model"),
                       device=meta.get("device"), processing_seconds=meta.get("processing_seconds"),
                       audio_duration=meta.get("audio_duration"), fallback=meta.get("fallback"),
                       segment_count=len(asr_dict.get("segments", [])), status="ok")
        info["result"] = out
        return asr_dict, info

    def _flag_disagreements(self, session_id, processed, raw, transcript, asr_info) -> None:
        """Neu cau hinh ASR_COMPARE_PROVIDER: chay ASR thu hai, danh dau doan bat dong
        o tu khoa quan trong. Khong tu chon ben nao."""
        name = self.settings.asr_compare_provider
        primary = asr_info.get("result")
        if not name or not isinstance(primary, ASRResult):
            return
        second = registry.create(name, self.settings.asr_compare_model, self.settings.asr_device,
                                 None, self.settings.processing_mode).transcribe(processed)
        items = compare_asr(primary, second)
        for it in items:
            for seg in transcript:
                if (it["start_time"] is None or
                        (seg["start_time"] < (it["end_time"] or 0) and seg["end_time"] > it["start_time"])):
                    seg.update({"asr_review_required": True, "asr_review_reason": it["reason"],
                                "asr_candidates": it["candidates"]})
        self.store.path(session_id, "asr_disagreement.json").write_text(
            json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        self.store.log(session_id, "asr_compared", compare_provider=name, disagreement_count=len(items))

    def _default_asr(self, processed: Path, raw: Path):
        if self.settings.processing_mode == "external":
            raise RuntimeError("external_processing_requires_explicit_provider")
        if self.settings.asr_provider == "sidecar":
            return SidecarProvider(raw.with_suffix(".json"))
        if self.settings.asr_provider == "auto":
            try:
                sidecar = raw.with_suffix(".json")
                if sidecar.exists() and "segments" in json.loads(sidecar.read_text(encoding="utf-8")):
                    return SidecarProvider(sidecar)
            except (json.JSONDecodeError, OSError):
                pass
            return registry.create("phowhisper", self.settings.asr_model, self.settings.asr_device,
                                   self.settings.asr_revision, self.settings.processing_mode)
        return registry.from_settings(self.settings)

    def transcript(self, session_id: str) -> list[dict[str, Any]]:
        return self.store.read_jsonl(session_id, "transcript.json") if False else json.loads(self.store.path(session_id, "transcript.json").read_text(encoding="utf-8")) if self.store.path(session_id, "transcript.json").exists() else []

    def edit_segment(self, session_id: str, segment_id: str, text: str, edited_by: str = "user") -> list[dict[str, Any]]:
        items = self.transcript(session_id)
        for segment in items:
            if segment["segment_id"] == segment_id:
                if not text.strip():
                    raise ValueError("transcript_incomplete")
                # Nguoi duyet sua = nguoi duyet da quyet, ke ca khi hai ASR bat dong.
                segment.update({"edited": True, "original_asr_text": segment.get("original_asr_text") or segment["text_original"], "text_original": text, "edited_at": now_iso(), "edited_by": edited_by,
                                "reviewed": True, "asr_review_required": False})
                break
        else:
            raise KeyError(segment_id)
        self.store.path(session_id, "transcript.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        self.store.log(session_id, "transcript_edited", segment_id=segment_id)
        return items

    def map_speakers(self, session_id: str, mapping: dict[str, str]) -> list[dict[str, Any]]:
        allowed = {r.value for r in SpeakerRole}
        if any(role not in allowed for role in mapping.values()):
            raise ValueError("speaker_unknown")
        items = self.transcript(session_id)
        for segment in items:
            if segment["speaker_id"] in mapping:
                segment["speaker_role"] = mapping[segment["speaker_id"]]
        self.store.update(session_id, speaker_map=mapping, status=SessionStatus.READY_FOR_MEDITRACE.value)
        self.store.path(session_id, "transcript.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        self.store.log(session_id, "speaker_role_updated", speaker_count=len(mapping))
        return items

    def confirm_segment(self, session_id: str, segment_id: str, reviewed_by: str = "user") -> list[dict[str, Any]]:
        """Nguoi duyet nghe lai va giu nguyen ban chep hien tai."""
        items = self.transcript(session_id)
        for segment in items:
            if segment["segment_id"] == segment_id:
                segment.update({"reviewed": True, "asr_review_required": False,
                                "edited_at": now_iso(), "edited_by": reviewed_by})
                break
        else:
            raise KeyError(segment_id)
        self.store.path(session_id, "transcript.json").write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        self.store.log(session_id, "transcript_confirmed", segment_id=segment_id)
        return items

    def meditrace_input(self, session_id: str) -> dict[str, Any]:
        items = self.transcript(session_id)
        # Chan cung: khong gui sang loi khi con vai chua ro hoac hai ASR bat dong chua duyet.
        if any(s.get("speaker_role", "unknown") == SpeakerRole.UNKNOWN.value for s in items):
            raise ValueError("speaker_unknown")
        if any(s.get("asr_review_required") for s in items):
            raise ValueError("asr_review_pending")
        result = to_meditrace(items, strict=True)
        self.store.update(session_id, meditrace_status="ready")
        self.store.log(session_id, "sent_to_meditrace", turn_count=len(result["turns"]))
        return result
