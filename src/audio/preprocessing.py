"""[Âm thanh]
Làm gì   : Đưa âm thanh về WAV 16 kHz mono để bộ chép dùng, vẫn giữ nguyên tệp gốc.
Vào → Ra : tệp âm thanh bất kỳ (webm, mp3...) → tệp WAV 16 kHz mono và kết quả kiểm chất
           lượng
Đọc từ   : class AudioPreprocessor chuyển định dạng; kiem_chat_luong() kiểm tệp
Mục lục (các hàm/lớp chính):
  class AudioPreprocessor     Chuyển âm thanh gốc sang WAV 16 kHz mono bằng ffmpeg
  kiem_chat_luong()           Kiểm tra chất lượng WAV: quá nhỏ, méo, quá ngắn
  class AudioProcessingError  Lỗi khi chuyển đổi âm thanh
Dùng bởi : audio/pipeline
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chuyển đổi âm thanh nhưng vẫn giữ nguyên tệp nguồn thô.

raw_audio.<ext>  --ffmpeg-->  processed.wav (16 kHz, mono, PCM 16 bit)

Tệp thô không bao giờ bị ghi vào: đích phải là đường dẫn khác, và
phép chuyển đổi từ chối chạy nếu không. Kiểm tra chất lượng (quá nhỏ, bị méo, quá ngắn)
được gắn vào siêu dữ liệu dưới dạng cảnh báo; nó không chặn việc xử lý.
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

# Ngưỡng kiểm chất lượng (âm thanh 16 bit). Đặt bảo thủ: cảnh báo, không chặn.
RMS_QUA_NHO = 300          # trung bình bình phương dưới mức này: nói quá nhỏ / micro xa
TY_LE_MEO = 0.001          # hơn 0,1% mẫu chạm trần: bị méo
THOI_LUONG_TOI_THIEU = 1.0


# ═══ class AudioProcessingError — Lỗi khi chuyển đổi âm thanh ═════════════════════════
class AudioProcessingError(RuntimeError):
    pass


# ═══ kiem_chat_luong() — Kiểm tra chất lượng WAV: quá nhỏ, méo, quá ngắn ══════════════
# Trả rms, tỷ lệ chạm trần, thời lượng và danh sách cảnh báo; chỉ cảnh báo, không chặn
# xử lý.
def kiem_chat_luong(wav_path: str | Path) -> dict[str, Any]:
    """-> {rms, clipping_ratio, duration, warnings}. Đọc cả tệp; đủ cho một buổi khám."""
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


# ═══ class AudioPreprocessor — Chuyển âm thanh gốc sang WAV 16 kHz mono bằng ffmpeg ═══
# Không bao giờ ghi đè tệp gốc; lưu siêu dữ liệu và kết quả kiểm chất lượng.
class AudioPreprocessor:
    def __init__(self, ffmpeg: str | None = None):
        self.ffmpeg = ffmpeg or shutil.which("ffmpeg") or "ffmpeg"

    def convert(self, source: str | Path, target: str | Path) -> dict[str, Any]:
        source, target = Path(source), Path(target)
        if source.resolve() == target.resolve():
            raise AudioProcessingError("audio_conversion_failed")   # không bao giờ ghi đè bản gốc
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
