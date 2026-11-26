"""faster-whisper (CTranslate2) — baseline provider.

Default model ``small`` (OpenAI Whisper small, MIT licence) for a like-for-like size
comparison with PhoWhisper-small.

Settings chosen against known Whisper failure modes:
* ``vad_filter=True``          Whisper invents sentences on silence.
* ``condition_on_previous_text=False``  avoids repetition loops.
* ``temperature=0``            deterministic decoding.

``asr_confidence`` = exp(avg_logprob) of the segment, i.e. the geometric mean token
probability. It measures how sure the recogniser is about the words — nothing more.
"""

from __future__ import annotations

import math
import threading
import time
from pathlib import Path
from typing import Any, Optional

from .base import ASRProvider, read_wav_16k_mono
from .contextual_trie_600 import ContextualPrefixTrie600, tao_trie_600_mac_dinh
from .schemas import ASRError, ASRResult, ASRSegment, ASRWord

_CACHE: dict[tuple, Any] = {}
_CACHE_LOCK = threading.Lock()
_INFER_LOCK = threading.Lock()


class FasterWhisperProvider(ASRProvider):
    name = "faster_whisper"
    external = False

    def __init__(self, model: str = "small", device: Optional[str] = None,
                 compute_type: Optional[str] = None, word_timestamps: bool = True,
                 vad_filter: bool = True, hotwords: Optional[str] = None,
                 trie_600: Optional[ContextualPrefixTrie600] = None,
                 he_co_quan: Optional[str] = None):
        self.model = model
        self.device_req = device
        self.compute_type = compute_type
        self.word_timestamps = word_timestamps
        self.vad_filter = vad_filter
        self.he_co_quan = he_co_quan
        if hotwords is not None:
            self.hotwords = hotwords
        else:
            trie = trie_600 or tao_trie_600_mac_dinh()
            hw = trie.xuat_hotwords(he_co_quan=he_co_quan)
            self.hotwords = hw or None

    def _model(self):
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise ASRError("asr_load_failed", "chua cai faster-whisper") from exc
        dev = self.device_req
        if dev is None:
            try:
                import torch
                dev = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                dev = "cpu"
        ct = self.compute_type or ("float16" if dev == "cuda" else "int8")
        key = (self.model, dev, ct)
        with _CACHE_LOCK:
            if key not in _CACHE:
                try:
                    _CACHE[key] = WhisperModel(self.model, device=dev, compute_type=ct)
                except Exception as exc:
                    raise ASRError("asr_load_failed", f"{type(exc).__name__}: {exc}") from exc
            model_inst = _CACHE[key]
        return model_inst, dev, ct

    def transcribe(self, audio_path: str | Path) -> ASRResult:
        audio, duration = read_wav_16k_mono(audio_path)
        model, dev, ct = self._model()
        cfg = {"language": "vi", "beam_size": 1, "temperature": 0.0, "vad_filter": self.vad_filter,
               "condition_on_previous_text": False, "word_timestamps": self.word_timestamps,
               "hotwords": self.hotwords}
        t0 = time.time()
        try:
            with _INFER_LOCK:
                it, _info = model.transcribe(audio, language="vi", beam_size=1, temperature=0.0,
                                             vad_filter=self.vad_filter,
                                             condition_on_previous_text=False,
                                             word_timestamps=self.word_timestamps,
                                             hotwords=self.hotwords)
                raw = list(it)
        except Exception as exc:
            raise ASRError("asr_inference_failed", f"{type(exc).__name__}: {exc}") from exc
        segs = []
        for i, s in enumerate(raw, 1):
            conf = math.exp(s.avg_logprob) if s.avg_logprob is not None else None
            words = [ASRWord(w.word, w.start, w.end) for w in (s.words or [])]
            segs.append(ASRSegment(f"seg_{i:03d}", s.start, s.end, s.text.strip(),
                                   round(conf, 4) if conf is not None else None, words))
        return ASRResult(provider=self.name, model=self.model, language="vi", segments=segs,
                         revision=None, device=dev, dtype=ct,
                         timestamp_level="word" if self.word_timestamps else "segment",
                         inference_config=cfg, processing_seconds=round(time.time() - t0, 3),
                         audio_duration=round(duration, 3),
                         notes=["asr_confidence = exp(avg_logprob) cua doan"])

    def info(self) -> dict[str, Any]:
        return {"provider": self.name, "model": self.model, "external": self.external}
