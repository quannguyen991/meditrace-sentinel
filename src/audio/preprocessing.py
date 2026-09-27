"""Audio conversion while preserving the raw source file.

raw_audio.<ext>  --ffmpeg-->  processed.wav (16 kHz, mono, PCM 16 bit)

The raw file is never written to: the target must be a different path, and the
conversion refuses to run otherwise. A quality check (too quiet, clipped, too short)
is attached to the metadata as warnings; it does not block processing.
"""

from __future__ import annotations

import array
import json
import math
import shutil
import subprocess
import wave
from pathlib import Path
from typing import Any

# Nguong kiem chat luong (am thanh 16 bit). Dat bao thu: canh bao, khong chan.
RMS_QUA_NHO = 300          # trung binh binh phuong duoi muc nay: noi qua nho / micro xa
TY_LE_MEO = 0.001          # hon 0,1% mau cham tran: bi meo
THOI_LUONG_TOI_THIEU = 1.0


class AudioProcessingError(RuntimeError):
    pass


def kiem_chat_luong(wav_path: str | Path) -> dict[str, Any]:
    """-> {rms, clipping_ratio, duration, warnings}. Doc ca tep; du cho mot buoi kham."""
    with wave.open(str(wav_path), "rb") as w:
        n = w.getnframes()
        data = array.array("h")
        data.frombytes(w.readframes(n))
        rate = w.getframerate()
    if not data:
        return {"rms": 0.0, "clipping_ratio": 0.0, "duration": 0.0, "warnings": ["qua_ngan"]}
    rms = math.sqrt(sum(x * x for x in data) / len(data))
    clip = sum(1 for x in data if x >= 32767 or x <= -32768) / len(data)
    dur = len(data) / rate
    canh = []
    if rms < RMS_QUA_NHO:
        canh.append("qua_nho")
    if clip > TY_LE_MEO:
        canh.append("bi_meo")
    if dur < THOI_LUONG_TOI_THIEU:
        canh.append("qua_ngan")
    return {"rms": round(rms, 1), "clipping_ratio": round(clip, 5), "duration": round(dur, 3),
            "warnings": canh}


class AudioPreprocessor:
    def __init__(self, ffmpeg: str | None = None):
        self.ffmpeg = ffmpeg or shutil.which("ffmpeg") or "ffmpeg"

    def convert(self, source: str | Path, target: str | Path) -> dict[str, Any]:
        source, target = Path(source), Path(target)
        if source.resolve() == target.resolve():
            raise AudioProcessingError("audio_conversion_failed")   # khong bao gio ghi de ban goc
        target.parent.mkdir(parents=True, exist_ok=True)
        command = [self.ffmpeg, "-y", "-i", str(source), "-ac", "1", "-ar", "16000", "-sample_fmt", "s16", str(target)]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode != 0 or not target.exists():
            raise AudioProcessingError("audio_conversion_failed")
        try:
            with wave.open(str(target), "rb") as wav:
                metadata = {"sample_rate": wav.getframerate(), "channels": wav.getnchannels(),
                            "duration": wav.getnframes() / wav.getframerate()}
        except (wave.Error, OSError) as exc:
            raise AudioProcessingError("audio_conversion_failed") from exc
        metadata.update({"raw_audio_path": str(source), "processed_audio_path": str(target),
                         "duration_seconds": metadata["duration"],
                         "quality": kiem_chat_luong(target)})
        target.with_suffix(".json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        return metadata
