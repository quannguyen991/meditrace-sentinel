"""[Âm thanh › Chép lời]
Làm gì   : Chép lời tiếng Việt bằng PhoWhisper chạy tại chỗ, là bộ chép chính của hệ thống.
Vào → Ra : tệp WAV 16 kHz mono → ASRResult: các đoạn chữ kèm mốc thời gian và độ tin cậy
Đọc từ   : class PhoWhisperProvider chép lời; _group_words() gom từ thành đoạn
Mục lục (các hàm/lớp chính):
  class PhoWhisperProvider  Nhà cung cấp chép lời PhoWhisper chạy tại chỗ
Gọi tới  : audio/asr/base, audio/asr/contextual_trie_600, audio/asr/schemas
Dùng bởi : audio/asr/registry
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
PhoWhisper (VinAI) qua Hugging Face transformers.

Mô hình: vinai/PhoWhisper-{tiny,base,small,medium,large}. Giấy phép BSD-3-Clause.
Mặc định ở đây là ``small`` (kiểm tra đường ống); ``medium`` cho benchmark chất lượng.
``large`` không phải mặc định: 1,55 B tham số không vừa GPU 4 GB, và nạp
checkpoint fp32 cần hơn 10 GB RAM.

Giải mã KHÔNG dùng token mốc thời gian. Đo ngày 22/09/2026 (docs/ket-qua/asr-benchmark.md):
yêu cầu PhoWhisper trả token mốc thời gian của Whisper — mức từ hoặc mức đoạn, qua
đường ống transformers — khiến nó nối thêm các vòng lặp dài sau câu
("a. a. a. …", "chủ yếu là chủ yếu là …") ở khoảng một nửa số đoạn thử ngắn,
và chạy chậm hơn 10–20×. Giải mã với ``<|notimestamps|>`` cho câu sạch.
Vì vậy nhà cung cấp này:

1. cắt âm thanh thành các cửa sổ tối đa 30 s, tại khung 0,1 s yên tĩnh nhất giữa
   20 s và 30 s (không cắt trong cửa sổ, nên ta không chẻ đôi từ nào);
2. giải mã từng cửa sổ bằng ``<|notimestamps|>``, tham lam, ``max_new_tokens`` bị chặn theo
   độ dài cửa sổ;
3. lấy thời điểm token từ DTW chú ý chéo (``return_token_timestamps``, dùng
   ``alignment_heads`` đi kèm trong cấu hình sinh). Các mốc này là ƯỚC LƯỢNG
   (khoảng ±0,2 s trên các đoạn thử; token đầu của cửa sổ được ghim vào đầu
   cửa sổ). Cuối một từ là đầu từ kế tiếp, nhưng không quá TU_DAI_TOI_DA giây
   sau đầu của chính nó, để một quãng ngắt hiện ra như khoảng trống giữa các từ.

Nếu bước 3 lỗi, từ không có mốc và các đoạn lùi về biên cửa sổ với
``timestamp_level = "window"`` — mốc thời gian không bao giờ bị bịa.

Độ tin cậy. ``asr_confidence`` = exp(trung bình log-xác suất token) của đoạn, cùng
định nghĩa với nhà cung cấp faster-whisper. Nó đo mức độ bộ nhận dạng chắc
về các từ — không hơn.

Chốt chặn lặp. Nếu văn bản của một cửa sổ kết thúc bằng cùng một n-gram 1–6 token lặp lại 4+
lần, ghi chú ``lap_lai_nghi_ngo`` được ghi lại; văn bản KHÔNG bị cắt bớt.

Mô hình được nạp một lần cho mỗi (mô hình, bản sửa, thiết bị) và lưu đệm trong tiến trình.
"""

from __future__ import annotations

import math
import threading
import time
from pathlib import Path
from typing import Any, Optional

import numpy as np

from .base import ASRProvider, read_wav_16k_mono
from .contextual_trie_600 import (
    ContextualPrefixTrie600,
    tao_trie_600_mac_dinh,
    tao_trie_logits_processor,
)
from .schemas import ASRError, ASRResult, ASRSegment, ASRWord

# Mã commit trên Hugging Face, đọc ngày 22/09/2026 — ghim dự án lặp thí nghiệm.
REVISIONS = {
    "vinai/PhoWhisper-small": "a86b604c346caf7148c37512eafe783a16420adb",
    "vinai/PhoWhisper-medium": "55a7e3eb6c906de891f8f06a107754427dd3be79",
    "vinai/PhoWhisper-large": "b9136a44b5f2ca664bd0b8f74baecf1715f6eeeb",
}
_CACHE: dict[tuple, Any] = {}
_CACHE_LOCK = threading.Lock()
_INFER_LOCK = threading.Lock()

SR = 16000
GAP_SPLIT = 0.8            # khoảng lặng (giây) giữa hai từ thì cắt thành đoạn mới
CUA_SO_TOI_DA = 30.0       # Whisper chỉ nghe được 30 s mỗi lần
CUA_SO_TOI_THIEU = 20.0
TOKEN_MOI_GIAY = 12        # trần số token sinh ra, chống lặp vô hạn
TOKEN_TRAN = 440
TU_DAI_TOI_DA = 1.2      # một từ (kể cả tên thuốc nhiều âm tiết) hiếm khi dài hơn


# ─── _group_words() — Gom các từ thành đoạn theo khoảng lặng ──────────────────────────
# Hai từ cách nhau quá 0,8 giây thì tách đoạn mới; giữ nguyên chữ của mô hình.
def _group_words(chunks: list[dict], gap: float = GAP_SPLIT) -> list[ASRSegment]:
    """Gom từ thành đoạn theo khoảng lặng. Giữ nguyên chữ của mô hình.

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


# ─── _cat_cua_so() — Cắt âm thanh thành cửa sổ tối đa 30 giây ─────────────────────────
# Cắt tại khung 0,1 giây ít năng lượng nhất trong khoảng 20 đến 30 giây.
def _cat_cua_so(audio: np.ndarray, sr: int = SR, toi_da: float = CUA_SO_TOI_DA,
                toi_thieu: float = CUA_SO_TOI_THIEU) -> list[tuple[int, int]]:
    """Cắt âm thanh thành các cửa sổ <= toi_da giây, tại khung 0,1 s ít năng lượng nhất."""
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


# ─── _lap_lai() — Phát hiện đoạn cuối lặp lại một cụm token nhiều lần ─────────────────
def _lap_lai(tokens: list[int], toi_thieu: int = 4) -> bool:
    for k in range(1, 7):
        if len(tokens) < k * toi_thieu:
            continue
        duoi = tokens[-k:]
        if all(tokens[-(j + 1) * k: len(tokens) - j * k] == duoi for j in range(toi_thieu)):
            return True
    return False


# ═══ class PhoWhisperProvider — Nhà cung cấp chép lời PhoWhisper chạy tại chỗ ═════════
# Giải mã không dùng token thời gian, mốc từ ước lượng bằng DTW; có hotwords từ cây tiền
# tố, gợi ý sửa âm vị và ghi chú nghi lặp.
class PhoWhisperProvider(ASRProvider):
    name = "phowhisper"
    external = False

    def __init__(self, model: str = "vinai/PhoWhisper-small", device: Optional[str] = None,
                 revision: Optional[str] = None, word_timestamps: bool = True,
                 trie_600: Optional[ContextualPrefixTrie600] = None,
                 he_co_quan: Optional[str] = None,
                 prompt_hotwords: Optional[str] = None):
        self.model = model
        self.revision = revision or REVISIONS.get(model)
        self.device_req = device
        self.word_timestamps = word_timestamps
        self.trie_600 = trie_600 if trie_600 is not None else tao_trie_600_mac_dinh()
        self.he_co_quan = he_co_quan
        self.prompt_hotwords = prompt_hotwords

    # -- nạp mô hình -------------------------------------------------------
    def _load(self):
        try:
            import torch
            from transformers import WhisperForConditionalGeneration, WhisperProcessor
        except ImportError as exc:
            raise ASRError("phowhisper_load_failed", f"thieu thu vien: {exc}") from exc
        dev = self.device_req or ("cuda" if torch.cuda.is_available() else "cpu")
        dtype = torch.float16 if dev.startswith("cuda") else torch.float32
        key = (self.model, self.revision, dev)
        with _CACHE_LOCK:
            if key not in _CACHE:
                try:
                    proc = WhisperProcessor.from_pretrained(self.model, revision=self.revision)
                    m = WhisperForConditionalGeneration.from_pretrained(
                        self.model, revision=self.revision, torch_dtype=dtype).to(dev).eval()
                except Exception as exc:  # mạng, đĩa, bộ nhớ, sai tên
                    raise ASRError("phowhisper_load_failed", f"{type(exc).__name__}: {exc}") from exc
                _CACHE[key] = (m, proc)
            m, proc = _CACHE[key]
        return m, proc, dev, str(dtype).replace("torch.", "")

    def _decode_window(self, audio: np.ndarray) -> dict[str, Any]:
        """Giải mã một cửa sổ <= 30 s.

        -> {"tokens": [(text, start_s | None, logprob)], "ids": [int], "dtw": bool}
        Thời gian tính từ đầu cửa sổ. Chỉ gồm token văn bản (bỏ token đặc biệt).
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
        if self.trie_600 is not None:
            try:
                from transformers import LogitsProcessorList
                lp = tao_trie_logits_processor(self.trie_600, proc.tokenizer, he_co_quan=self.he_co_quan)
                if lp is not None:
                    kw["logits_processor"] = LogitsProcessorList([lp])
            except Exception:
                pass
        dtw = self.word_timestamps
        with _INFER_LOCK, torch.no_grad():
            try:
                out = m.generate(feats, attention_mask=mask, return_token_timestamps=dtw, **kw)
            except Exception:
                if not dtw:
                    raise
                dtw = False
                out = m.generate(feats, attention_mask=mask, **kw)
        seq = out["sequences"][0].tolist()
        scores = out["scores"]
        # scores[i] ứng với token sinh thứ i = seq[len(seq) - len(scores) + i]
        dau_sinh = len(seq) - len(scores)
        times = out["token_timestamps"][0].tolist() if dtw and "token_timestamps" in out else None
        dac_biet = set(proc.tokenizer.all_special_ids)
        # Gom token thành TỪ trước khi giải mã. Tokenizer byte-level cắt một chữ có dấu
        # (vd "ỡ") thành nhiều token byte; giải mã từng token riêng sẽ ra ký tự hỏng
        # ("đ��"). Từ mới bắt đầu ở token có dấu cách "Ġ" của tokenizer.
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
        # thời điểm kết thúc = mốc của token kết thúc (eos) nếu có
        het = times[-1] if times else None
        return {"tokens": toks, "ids": ids, "dtw": bool(times), "end": het}

    # -- nhận dạng ---------------------------------------------------------
    def transcribe(self, audio_path: str | Path) -> ASRResult:
        audio, duration = read_wav_16k_mono(audio_path)
        _, _, dev, dtype = self._load()
        hotwords_str = (
            self.prompt_hotwords
            if self.prompt_hotwords is not None
            else (self.trie_600.xuat_hotwords(he_co_quan=self.he_co_quan, max_terms=60) if self.trie_600 is not None else "")
        )
        cfg = {"language": "vi", "task": "transcribe", "num_beams": 1, "do_sample": False,
               "timestamp_tokens": False, "word_times": "cross_attention_dtw" if self.word_timestamps else None,
               "max_new_tokens_per_s": TOKEN_MOI_GIAY, "window_s": CUA_SO_TOI_DA,
               "trie_hotwords_active": bool(hotwords_str), "he_co_quan": self.he_co_quan}
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
            # gom token thành từ: token bắt đầu bằng dấu cách mở từ mới
            words: list[dict] = []
            # mỗi mục: (chữ, mốc bắt đầu, log-xác suất[, số token]); không có số token
            # nghĩa là mục đó là một token
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
        van_ban_gop = " ".join(s.text for s in segments if s.text)
        goi_y_am_vi = (
            self.trie_600.quet_goi_y_sua_am_vi(van_ban_gop)
            if (self.trie_600 is not None and van_ban_gop)
            else []
        )
        cfg["phonetic_candidates"] = goi_y_am_vi
        for gy in goi_y_am_vi:
            notes.append(f"goi_y_sua_am_vi: '{gy['tu_goc']}' -> '{gy['goi_y_chuan']}' ({gy['loai']})")
        return ASRResult(provider=self.name, model=self.model, language="vi", segments=segments,
                         revision=self.revision, device=dev, dtype=dtype, timestamp_level=level,
                         inference_config=cfg, processing_seconds=round(time.time() - t0, 3),
                         audio_duration=round(duration, 3), notes=notes)

    def info(self) -> dict[str, Any]:
        return {"provider": self.name, "model": self.model, "revision": self.revision,
                "external": self.external, "word_timestamps": self.word_timestamps,
                "trie_hotwords_active": self.trie_600 is not None,
                "he_co_quan": self.he_co_quan}
