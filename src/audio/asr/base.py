"""[Âm thanh › Chép lời]
Làm gì   : Quy định giao diện chung mọi bộ chép lời phải theo và đọc WAV về dạng chuẩn để
           đưa vào bộ chép.
Vào → Ra : đường dẫn WAV → mảng mẫu 16 kHz mono; ASRProvider.transcribe(âm thanh) →
           ASRResult
Đọc từ   : class ASRProvider giao diện chung; read_wav_16k_mono() đọc WAV chuẩn
Mục lục (các hàm/lớp chính):
  class ASRProvider    Giao diện chung cho mọi nhà cung cấp chép lời
  read_wav_16k_mono()  Đọc tệp WAV 16 kHz mono ra mảng số
Gọi tới  : audio/asr/schemas
Dùng bởi : audio/asr/__init__, audio/asr/faster_whisper_provider,
           audio/asr/phowhisper_provider, audio/asr/registry, audio/asr/sidecar_provider
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Giao diện ASRProvider.

Nhà cung cấp biến tệp WAV PCM mono 16 kHz thành ``ASRResult``. Nó phải:

* giữ nguyên các từ đã nghe (không chuẩn hoá lâm sàng, không dùng từ chẩn đoán);
* trả mốc thời gian theo trục thời gian của tệp WAV được đưa vào, hoặc ``None``;
* không bao giờ suy ra vai người nói (đó là việc của tách người nói + con người duyệt);
* khai báo ``external = True`` nếu gửi âm thanh ra khỏi máy.
"""

from __future__ import annotations

import wave
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from .schemas import ASRError, ASRResult


# ═══ class ASRProvider — Giao diện chung cho mọi nhà cung cấp chép lời ════════════════
# Nhận WAV 16 kHz mono, trả ASRResult; giữ nguyên từ nghe được, không đoán vai;
# external=True nếu gửi âm thanh ra ngoài.
class ASRProvider(ABC):
    name: str = "base"
    external: bool = False          # True = gửi âm thanh ra dịch vụ ngoài

    @abstractmethod
    def transcribe(self, audio_path: str | Path) -> ASRResult: ...

    def info(self) -> dict[str, Any]:
        return {"provider": self.name, "external": self.external}


# ═══ read_wav_16k_mono() — Đọc tệp WAV 16 kHz mono ra mảng số ═════════════════════════
# Trả mảng float32 trong [-1, 1] và thời lượng; sai định dạng báo audio_invalid.
def read_wav_16k_mono(audio_path: str | Path):
    """Đọc WAV PCM 16 bit, 16 kHz, mono -> (numpy float32 trong [-1, 1], thời lượng).

    Dùng module `wave` có sẵn, không cần librosa/soundfile. Sai định dạng thì báo
    `audio_invalid` — preprocessing phải đã chuyển đúng định dạng trước đó.
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
