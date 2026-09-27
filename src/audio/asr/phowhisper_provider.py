"""PhoWhisper (VinAI) through Hugging Face transformers.

Models: vinai/PhoWhisper-{tiny,base,small,medium,large}. Licence BSD-3-Clause.
Default here is ``small`` (pipeline checks); ``medium`` for quality benchmarks.
``large`` is not the default: 1.55 B parameters do not fit a 4 GB GPU, and loading
the fp32 checkpoint needs more than 10 GB RAM.

Decoding WITHOUT timestamp tokens. Measured on 22/09/2026 (docs/ket-qua/asr-benchmark.md):
asking PhoWhisper for Whisper timestamp tokens — word or segment level, through the
transformers pipeline — makes it append long repetition loops after the sentence
("a. a. a. …", "chủ yếu là chủ yếu là …") on about half of the short test clips, and
runs 10–20× slower. Decoding with ``<|notimestamps|>`` gives the clean sentence.
So this provider:

1. cuts the audio into windows of at most 30 s, at the quietest 0.1 s frame between
   20 s and 30 s (no cut inside the window, so no word is split by us);
2. decodes each window with ``<|notimestamps|>``, greedy, ``max_new_tokens`` bounded by
   the window length;
3. takes token times from cross-attention DTW (``return_token_timestamps``, using the
   ``alignment_heads`` shipped in the generation config). These times are ESTIMATES
   (about ±0.2 s on the test clips; the first token of a window is pinned to the window
   start). A word's end is the start of the next word, capped at TU_DAI_TOI_DA seconds
   after its own start so that a pause shows up as a gap between words.

If step 3 fails, words get no times and segments fall back to the window bounds with
``timestamp_level = "window"`` — times are never invented.

Confidence. ``asr_confidence`` = exp(mean token log-probability) of the segment, the
same definition as the faster-whisper provider. It measures how sure the recogniser is
about the words — nothing more.

Repetition guard. If a window's text ends with the same 1–6 token n-gram repeated 4+
times, a note ``lap_lai_nghi_ngo`` is recorded; the text is NOT trimmed.

The model is loaded once per (model, revision, device) and cached in the process.
"""

from __future__ import annotations

import math
import time
from pathlib import Path
from typing import Any, Optional

import numpy as np

from .base import ASRProvider, read_wav_16k_mono
from .schemas import ASRError, ASRResult, ASRSegment, ASRWord

# Ma commit tren Hugging Face, doc ngay 22/09/2026 — ghim du an lap thi nghiem.
REVISIONS = {
    "vinai/PhoWhisper-small": "a86b604c346caf7148c37512eafe783a16420adb",
    "vinai/PhoWhisper-medium": "55a7e3eb6c906de891f8f06a107754427dd3be79",
    "vinai/PhoWhisper-large": "b9136a44b5f2ca664bd0b8f74baecf1715f6eeeb",
}
_CACHE: dict[tuple, Any] = {}

SR = 16000
GAP_SPLIT = 0.8            # khoang lang (giay) giua hai tu thi cat thanh doan moi
CUA_SO_TOI_DA = 30.0       # Whisper chi nghe duoc 30 s moi lan
CUA_SO_TOI_THIEU = 20.0
TOKEN_MOI_GIAY = 12        # tran so token sinh ra, chong lap vo han
TOKEN_TRAN = 440
TU_DAI_TOI_DA = 1.2      # mot tu (ke ca ten thuoc nhieu am tiet) hiem khi dai hon


def _group_words(chunks: list[dict], gap: float = GAP_SPLIT) -> list[ASRSegment]:
    """Gom tu thanh doan theo khoang lang. Giu nguyen chu cua mo hinh.

    chunks: [{"text", "timestamp": (a, b), "logprob"?: float, "n_tok"?: int}]
    """
    segs: list[ASRSegment] = []
    cur: list[dict] = []

    def flush():
        if not cur:
            return
        text = "".join(c["text"] for c in cur).strip()
        if text:
            n = sum(c.get("n_tok", 0) for c in cur)
            lp = sum(c.get("logprob", 0.0) for c in cur)
            conf = round(math.exp(lp / n), 4) if n else None
            words = [ASRWord(c["text"], *(c.get("timestamp") or (None, None))) for c in cur]
            segs.append(ASRSegment(f"seg_{len(segs) + 1:03d}", words[0].start_time,
                                   words[-1].end_time, text, conf, words))
        cur.clear()

    for c in chunks:
        a, _ = (c.get("timestamp") or (None, None))
        if cur and a is not None:
            prev_end = (cur[-1].get("timestamp") or (None, None))[1]
            if prev_end is not None and a - prev_end > gap:
                flush()
        cur.append(c)
    flush()
    return segs


def _cat_cua_so(audio: np.ndarray, sr: int = SR, toi_da: float = CUA_SO_TOI_DA,
                toi_thieu: float = CUA_SO_TOI_THIEU) -> list[tuple[int, int]]:
    """Cat am thanh thanh cac cua so <= toi_da giay, tai khung 0,1 s it nang luong nhat."""
    n, khung = len(audio), int(0.1 * sr)
    ra, dau = [], 0
    while n - dau > toi_da * sr:
        a, b = dau + int(toi_thieu * sr), dau + int(toi_da * sr) - khung
        rms = [float(np.sqrt(np.mean(audio[i:i + khung] ** 2))) for i in range(a, b, khung)]
        cat = a + int(np.argmin(rms)) * khung + khung // 2
        ra.append((dau, cat))
        dau = cat
    ra.append((dau, n))
    return ra


def _lap_lai(tokens: list[int], toi_thieu: int = 4) -> bool:
    for k in range(1, 7):
        if len(tokens) < k * toi_thieu:
            continue
        duoi = tokens[-k:]
        if all(tokens[-(j + 1) * k: len(tokens) - j * k] == duoi for j in range(toi_thieu)):
            return True
    return False


class PhoWhisperProvider(ASRProvider):
    name = "phowhisper"
    external = False

    def __init__(self, model: str = "vinai/PhoWhisper-small", device: Optional[str] = None,
                 revision: Optional[str] = None, word_timestamps: bool = True):
        self.model = model
        self.revision = revision or REVISIONS.get(model)
        self.device_req = device
        self.word_timestamps = word_timestamps

    # -- nap mo hinh -------------------------------------------------------
    def _load(self):
        try:
            import torch
            from transformers import WhisperForConditionalGeneration, WhisperProcessor
        except ImportError as exc:
            raise ASRError("phowhisper_load_failed", f"thieu thu vien: {exc}") from exc
        dev = self.device_req or ("cuda" if torch.cuda.is_available() else "cpu")
        dtype = torch.float16 if dev.startswith("cuda") else torch.float32
        key = (self.model, self.revision, dev)
        if key not in _CACHE:
            try:
                proc = WhisperProcessor.from_pretrained(self.model, revision=self.revision)
                m = WhisperForConditionalGeneration.from_pretrained(
                    self.model, revision=self.revision, torch_dtype=dtype).to(dev).eval()
            except Exception as exc:  # mang, dia, bo nho, sai ten
                raise ASRError("phowhisper_load_failed", f"{type(exc).__name__}: {exc}") from exc
            _CACHE[key] = (m, proc)
        m, proc = _CACHE[key]
        return m, proc, dev, str(dtype).replace("torch.", "")

    def _decode_window(self, audio: np.ndarray) -> dict[str, Any]:
        """Giai ma mot cua so <= 30 s.

        -> {"tokens": [(text, start_s | None, logprob)], "ids": [int], "dtw": bool}
        Thoi gian tinh tu dau cua so. Chi gom token van ban (bo token dac biet).
        """
        import torch
        m, proc, dev, _ = self._load()
        x = proc(audio, sampling_rate=SR, return_tensors="pt", return_attention_mask=True)
        feats = x.input_features.to(dev, dtype=m.dtype)
        mask = x.attention_mask.to(dev)
        dur = len(audio) / SR
        kw = dict(language="vi", task="transcribe", num_beams=1, do_sample=False,
                  return_timestamps=False, max_new_tokens=min(TOKEN_TRAN, int(TOKEN_MOI_GIAY * dur) + 16),
                  return_dict_in_generate=True, output_scores=True)
        dtw = self.word_timestamps
        with torch.no_grad():
            try:
                out = m.generate(feats, attention_mask=mask, return_token_timestamps=dtw, **kw)
            except Exception:
                if not dtw:
                    raise
                dtw = False
                out = m.generate(feats, attention_mask=mask, **kw)
        seq = out["sequences"][0].tolist()
        scores = out["scores"]
        # scores[i] ung voi token sinh thu i = seq[len(seq) - len(scores) + i]
        dau_sinh = len(seq) - len(scores)
        times = out["token_timestamps"][0].tolist() if dtw and "token_timestamps" in out else None
        dac_biet = set(proc.tokenizer.all_special_ids)
        # Gom token thanh TU truoc khi giai ma. Tokenizer byte-level cat mot chu co dau
        # (vd "ỡ") thanh nhieu token byte; giai ma tung token rieng se ra ky tu hong
        # ("đ��"). Tu moi bat dau o token co dau cach "Ġ" cua tokenizer.
        nhom: list[dict] = []
        ids = []
        for i, t in enumerate(seq):
            if t in dac_biet:
                continue
            lp = None
            if i >= dau_sinh:
                lp = float(torch.log_softmax(scores[i - dau_sinh][0].float(), -1)[t])
            if not nhom or proc.tokenizer.convert_ids_to_tokens(t).startswith("Ġ"):
                nhom.append({"ids": [], "start": times[i] if times else None, "lp": 0.0, "n": 0})
            g = nhom[-1]
            g["ids"].append(t)
            if lp is not None:
                g["lp"] += lp
                g["n"] += 1
            ids.append(t)
        toks = [(proc.tokenizer.decode(g["ids"]), g["start"], g["lp"], g["n"]) for g in nhom]
        # thoi diem ket thuc = moc cua token ket thuc (eos) neu co
        het = times[-1] if times else None
        return {"tokens": toks, "ids": ids, "dtw": bool(times), "end": het}

    # -- nhan dang ---------------------------------------------------------
    def transcribe(self, audio_path: str | Path) -> ASRResult:
        audio, duration = read_wav_16k_mono(audio_path)
        _, _, dev, dtype = self._load()
        cfg = {"language": "vi", "task": "transcribe", "num_beams": 1, "do_sample": False,
               "timestamp_tokens": False, "word_times": "cross_attention_dtw" if self.word_timestamps else None,
               "max_new_tokens_per_s": TOKEN_MOI_GIAY, "window_s": CUA_SO_TOI_DA}
        t0 = time.time()
        notes: list[str] = []
        chunks: list[dict] = []
        co_dtw = True
        cua_so = _cat_cua_so(audio)
        for k, (a, b) in enumerate(cua_so):
            off = a / SR
            try:
                r = self._decode_window(audio[a:b])
            except ASRError:
                raise
            except Exception as exc:
                raise ASRError("phowhisper_inference_failed", f"{type(exc).__name__}: {exc}") from exc
            if _lap_lai(r["ids"]):
                notes.append(f"lap_lai_nghi_ngo o cua so {k} ({off:.1f}-{b / SR:.1f} s)")
            co_dtw = co_dtw and r["dtw"]
            # gom token thanh tu: token bat dau bang dau cach mo tu moi
            words: list[dict] = []
            # moi muc: (chu, moc bat dau, log-xac suat[, so token]); khong co so token
            # nghia la muc do la mot token
            for text, st, lp, *n in r["tokens"]:
                if not words or text.startswith(" "):
                    words.append({"text": text, "start": st, "logprob": 0.0, "n_tok": 0})
                else:
                    words[-1]["text"] += text
                w = words[-1]
                if lp is not None:
                    w["logprob"] += lp
                    w["n_tok"] += n[0] if n else 1
            for i, w in enumerate(words):
                if r["dtw"]:
                    s = w["start"]
                    e = words[i + 1]["start"] if i + 1 < len(words) else (r["end"] or s)
                    e = min(max(e, s), s + TU_DAI_TOI_DA)
                    ts = (round(off + s, 2), round(off + e, 2))
                else:
                    ts = (round(off, 2), round(b / SR, 2)) if i == 0 else (None, None)
                chunks.append({"text": w["text"], "timestamp": ts, "logprob": w["logprob"], "n_tok": w["n_tok"],
                               "_cua_so": k})
        if co_dtw:
            level = "word" if self.word_timestamps else "segment"
            segments = _group_words(chunks)
            if not self.word_timestamps:
                for s in segments:
                    s.words = []
        else:
            level = "window"
            if self.word_timestamps:
                notes.append("khong lay duoc moc tung tu bang DTW; dung moc cua so")
            segments = []
            for k, (a, b) in enumerate(cua_so):
                cs = [c for c in chunks if c["_cua_so"] == k]
                text = "".join(c["text"] for c in cs).strip()
                if text:
                    n = sum(c["n_tok"] for c in cs)
                    conf = round(math.exp(sum(c["logprob"] for c in cs) / n), 4) if n else None
                    segments.append(ASRSegment(f"seg_{len(segments) + 1:03d}", round(a / SR, 2),
                                               round(b / SR, 2), text, conf))
        cfg["timestamps"] = level
        return ASRResult(provider=self.name, model=self.model, language="vi", segments=segments,
                         revision=self.revision, device=dev, dtype=dtype, timestamp_level=level,
                         inference_config=cfg, processing_seconds=round(time.time() - t0, 3),
                         audio_duration=round(duration, 3), notes=notes)

    def info(self) -> dict[str, Any]:
        return {"provider": self.name, "model": self.model, "revision": self.revision,
                "external": self.external, "word_timestamps": self.word_timestamps}
