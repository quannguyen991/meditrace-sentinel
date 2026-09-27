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
