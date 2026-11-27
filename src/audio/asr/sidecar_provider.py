"""[Âm thanh › Chép lời]
Làm gì   : Cho ra bản chép lời cố định bằng cách đọc tệp JSON đặt cạnh âm thanh, dùng cho
           demo và phép thử lặp lại được.
Vào → Ra : tệp âm thanh có JSON cùng tên → ASRResult lấy nguyên từ JSON
Đọc từ   : class SidecarProvider đọc bản chép từ JSON cạnh âm thanh
Mục lục (các hàm/lớp chính):
  class SidecarProvider  Nhà cung cấp đọc lời chép sẵn từ tệp JSON cạnh âm thanh
Gọi tới  : audio/asr/base, audio/asr/schemas
Dùng bởi : audio/asr/registry, audio/pipeline
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Nhà cung cấp tất định đọc bản chép lời JSON nằm cạnh tệp âm thanh.

Dùng cho demo, kiểm thử ngoại tuyến và dữ liệu mẫu. Bọc lớp cũ
``providers.JsonSidecarASRProvider`` vào lược đồ ``ASRResult`` chung.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .base import ASRProvider
from .schemas import ASRError, ASRResult, ASRSegment, ASRWord


# ═══ class SidecarProvider — Nhà cung cấp đọc lời chép sẵn từ tệp JSON cạnh âm thanh ═══
# Dùng cho demo và kiểm thử ngoại tuyến; kết quả tất định.
class SidecarProvider(ASRProvider):
    name = "sidecar"
    external = False

    def __init__(self, sidecar_path: Optional[str | Path] = None):
        self.sidecar_path = Path(sidecar_path) if sidecar_path else None

    def transcribe(self, audio_path: str | Path) -> ASRResult:
        p = self.sidecar_path or Path(audio_path).with_suffix(".json")
        if not p.exists():
            raise ASRError("asr_inference_failed", "asr_sidecar_missing")
        data = json.loads(p.read_text(encoding="utf-8"))
        items = data if isinstance(data, list) else data.get("segments")
        if items is None:
            raise ASRError("asr_inference_failed", "asr_sidecar_invalid")
        segs = []
        for i, s in enumerate(items, 1):
            words = [ASRWord(w.get("text", ""), w.get("start_time", w.get("start")),
                             w.get("end_time", w.get("end"))) for w in s.get("words", [])]
            segs.append(ASRSegment(s.get("segment_id", f"seg_{i:03d}"),
                                   s.get("start_time", s.get("start")), s.get("end_time", s.get("end")),
                                   str(s.get("text", "")).strip(),
                                   s.get("asr_confidence", s.get("confidence")), words))
        lang = "vi" if isinstance(data, list) else data.get("language", "vi")
        return ASRResult(provider=self.name, model="sidecar-json", language=lang, segments=segs,
                         timestamp_level="word" if any(s.words for s in segs) else "segment")
