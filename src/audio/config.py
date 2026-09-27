"""Environment configuration for audio processing.

    PROCESSING_MODE=local            local | external (external providers refused in local)
    ASR_PROVIDER=phowhisper          phowhisper | faster_whisper | sidecar | auto
    ASR_MODEL=vinai/PhoWhisper-small (or "small", "medium" for PhoWhisper)
    ASR_DEVICE=cuda                  cuda | cpu (empty = auto)
    ASR_REVISION=                    Hugging Face commit; empty = pinned default
    ALLOW_ASR_FALLBACK=false         only then may a failing provider be replaced
    ASR_FALLBACK_PROVIDER=           e.g. faster_whisper
    ASR_FALLBACK_MODEL=
    ASR_COMPARE_PROVIDER=            run a second provider and flag disagreements
    ASR_COMPARE_MODEL=

    DIARIZATION_PROVIDER=mot_nguoi   mot_nguoi (ca ban ghi mot nguoi noi) | pyannote
    PYANNOTE_PYTHON=                 python cua MOI TRUONG RIENG co pyannote.audio
    PYANNOTE_MODEL=pyannote/speaker-diarization-3.1
    PYANNOTE_TOKEN_FILE=             tep chua khoa Hugging Face (chi can khi tai mo hinh lan dau)
    PYANNOTE_DEVICE=cpu              cpu | cuda
    PYANNOTE_RAM_GB=3                tran RAM rieng cua tien trinh pyannote
    PYANNOTE_TONG_RAM_GB=9.5         tran RAM dich vu + pyannote (HoaiDuc: 10 GB cho ca du an)
    PYANNOTE_TIMEOUT_S=1200
    PYANNOTE_MIN_SPEAKERS= / PYANNOTE_MAX_SPEAKERS=   neu biet truoc so nguoi noi
    PYANNOTE_HF_HOME=                thu muc bo nho dem Hugging Face cua moi truong pyannote
    GOP_LUOT_CUNG_NGUOI_NOI=true     tach that roi thi gop cac doan lien tiep cung nguoi noi

Legacy names WHISPER_MODEL / WHISPER_DEVICE are still read for ``auto``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def _bool(v: Optional[str]) -> bool:
    return str(v or "").strip().lower() in {"1", "true", "yes", "on"}


def _opt(name: str) -> Optional[str]:
    v = os.getenv(name, "").strip()
    return v or None


def _so(name: str, mac_dinh=None, kieu=float):
    v = os.getenv(name, "").strip()
    return kieu(v) if v else mac_dinh


@dataclass(frozen=True)
class AudioSettings:
    processing_mode: str = "local"
    asr_provider: str = "auto"
    whisper_model: str = "small"
    whisper_device: str = "cpu"
    asr_model: Optional[str] = None
    asr_device: Optional[str] = None
    asr_revision: Optional[str] = None
    allow_asr_fallback: bool = False
    asr_fallback_provider: Optional[str] = None
    asr_fallback_model: Optional[str] = None
    asr_compare_provider: Optional[str] = None
    asr_compare_model: Optional[str] = None
    diarization_provider: str = "mot_nguoi"
    pyannote_python: Optional[str] = None
    pyannote_model: Optional[str] = None
    pyannote_token_file: Optional[str] = None
    pyannote_device: Optional[str] = None
    pyannote_ram_gb: float = 3.0
    pyannote_tong_ram_gb: float = 9.5
    pyannote_timeout_s: float = 1200.0
    pyannote_min_speakers: Optional[int] = None
    pyannote_max_speakers: Optional[int] = None
    pyannote_hf_home: Optional[str] = None
    gop_luot_cung_nguoi_noi: bool = True

    @classmethod
    def from_env(cls) -> "AudioSettings":
        mode = os.getenv("PROCESSING_MODE", "local").lower()
        if mode not in {"local", "external"}:
            raise ValueError("invalid_processing_mode")
        dia = os.getenv("DIARIZATION_PROVIDER", "mot_nguoi").strip().lower().replace("-", "_")
        if dia not in {"mot_nguoi", "pyannote"}:
            raise ValueError("invalid_diarization_provider")
        return cls(mode, os.getenv("ASR_PROVIDER", "auto").lower(),
                   os.getenv("WHISPER_MODEL", "small"), os.getenv("WHISPER_DEVICE", "cpu"),
                   _opt("ASR_MODEL"), _opt("ASR_DEVICE"), _opt("ASR_REVISION"),
                   _bool(os.getenv("ALLOW_ASR_FALLBACK")), _opt("ASR_FALLBACK_PROVIDER"),
                   _opt("ASR_FALLBACK_MODEL"), _opt("ASR_COMPARE_PROVIDER"),
                   _opt("ASR_COMPARE_MODEL"),
                   diarization_provider=dia,
                   pyannote_python=_opt("PYANNOTE_PYTHON"),
                   pyannote_model=_opt("PYANNOTE_MODEL"),
                   pyannote_token_file=_opt("PYANNOTE_TOKEN_FILE"),
                   pyannote_device=_opt("PYANNOTE_DEVICE"),
                   pyannote_ram_gb=_so("PYANNOTE_RAM_GB", 3.0),
                   pyannote_tong_ram_gb=_so("PYANNOTE_TONG_RAM_GB", 9.5),
                   pyannote_timeout_s=_so("PYANNOTE_TIMEOUT_S", 1200.0),
                   pyannote_min_speakers=_so("PYANNOTE_MIN_SPEAKERS", None, int),
                   pyannote_max_speakers=_so("PYANNOTE_MAX_SPEAKERS", None, int),
                   pyannote_hf_home=_opt("PYANNOTE_HF_HOME"),
                   gop_luot_cung_nguoi_noi=os.getenv("GOP_LUOT_CUNG_NGUOI_NOI", "true").strip().lower()
                   not in {"0", "false", "no", "off"})
