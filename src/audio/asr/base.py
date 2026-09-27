"""ASRProvider interface.

A provider turns a 16 kHz mono PCM WAV file into an ``ASRResult``. It must:

* keep the words it heard (no clinical normalisation, no diagnosis wording);
* return timestamps on the time axis of the WAV it was given, or ``None``;
* never infer speaker roles (that is diarization + human review);
* declare ``external = True`` if it sends audio off the machine.
"""

from __future__ import annotations

import wave
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .schemas import ASRError, ASRResult


class ASRProvider(ABC):
    name: str = "base"
    external: bool = False          # True = gui am thanh ra dich vu ngoai

    @abstractmethod
    def transcribe(self, audio_path: str | Path) -> ASRResult: ...

    def info(self) -> dict[str, Any]:
        return {"provider": self.name, "external": self.external}


def read_wav_16k_mono(audio_path: str | Path):
    """Doc WAV PCM 16 bit, 16 kHz, mono -> (numpy float32 trong [-1, 1], thoi luong).

    Dung module `wave` co san, khong can librosa/soundfile. Sai dinh dang thi bao
    `audio_invalid` — preprocessing phai da chuyen dung dinh dang truoc do.
    """
    import numpy as np
    try:
        with wave.open(str(audio_path), "rb") as w:
            if w.getnchannels() != 1 or w.getframerate() != 16000 or w.getsampwidth() != 2:
                raise ASRError("audio_invalid", "can WAV PCM 16 bit, 16 kHz, mono")
            frames = w.readframes(w.getnframes())
    except (wave.Error, OSError) as exc:
        raise ASRError("audio_invalid", str(exc)) from exc
    audio = np.frombuffer(frames, dtype="<i2").astype("float32") / 32768.0
    return audio, len(audio) / 16000.0
