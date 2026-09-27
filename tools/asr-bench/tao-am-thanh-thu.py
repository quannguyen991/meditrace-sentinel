"""Sinh am thanh thu cho benchmark ASR bang may doc chay tren may (khong gui du lieu ra ngoai).

AM THANH NAY LA GIONG MAY, KHONG PHAI GIONG NGUOI. Ket qua benchmark tren no chi cho
biet mo hinh co nghe duoc cac tu khoa lam sang trong dieu kien de, KHONG thay duoc ban
ghi that trong phong kham. Khong phat hanh lai am thanh (xem giay phep tung giong).

Giong (GIONG ben duoi):
  mms          facebook/mms-tts-vie                    CC-BY-NC 4.0
  vais1000     Piper vi_VN-vais1000-medium (1 nu)      du lieu CC-BY 4.0
  25hours      Piper vi_VN-25hours_single-low (1)      du lieu InfoRe, giay phep khong ro
  vivos_a/_b   Piper vi_VN-vivos-x_low, 2 nguoi doc     du lieu VIVOS, CC-BY-NC-SA 4.0
               CANH BAO: PhoWhisper duoc danh gia tren VIVOS va VinAI khong cong bo thanh phan
               844 gio du lieu huan luyen, nen co the tap huan luyen VIVOS nam trong do (can xac
               nhan). Giong nay co the loi cho PhoWhisper. Bao cao phai tach rieng.

Moi giong hai dieu kien: sach, on (them on trang SNR 15 dB).
Ra: data/audio-bench/wav/<id>__<giong>__<dieu_kien>.wav va data/audio-bench/muc-thu.json.

Chay: D:/meditrace-venv-lap/Scripts/python tools/asr-bench/tao-am-thanh-thu.py
      (can file giong Piper trong PIPER_DIR, mac dinh D:/hf-cache/piper)
"""
import json
import os
import re
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC))
from src.audio.asr import critical_tokens as ct  # noqa: E402

SR = 16000
SNR_DB = 15.0
RA = GOC / "data" / "audio-bench"
PIPER_DIR = Path(os.environ.get("PIPER_DIR", "D:/hf-cache/piper"))
GIONG = {
    "mms": {"loai": "mms", "mo_hinh": "facebook/mms-tts-vie", "giay_phep": "CC-BY-NC 4.0"},
    "vais1000": {"loai": "piper", "mo_hinh": "vi_VN-vais1000-medium", "giay_phep": "du lieu CC-BY 4.0"},
    "25hours": {"loai": "piper", "mo_hinh": "vi_VN-25hours_single-low", "giay_phep": "khong ro"},
    "vivos_a": {"loai": "piper", "mo_hinh": "vi_VN-vivos-x_low", "speaker": 3, "giay_phep": "CC-BY-NC-SA 4.0",
                "canh_bao": "VIVOS co the nam trong du lieu huan luyen PhoWhisper (can xac nhan)"},
    "vivos_b": {"loai": "piper", "mo_hinh": "vi_VN-vivos-x_low", "speaker": 40, "giay_phep": "CC-BY-NC-SA 4.0",
                "canh_bao": "VIVOS co the nam trong du lieu huan luyen PhoWhisper (can xac nhan)"},
}
DIEU_KIEN = ("sach", "on")


def ghi_wav(path, x, sr=SR):
    x = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def ve_16k(x, sr):
    if sr == SR:
        return x.astype("float32")
    o = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-",
                        "-ar", str(SR), "-f", "f32le", "-"], input=x.astype("<f4").tobytes(),
                       capture_output=True, check=True).stdout
    return np.frombuffer(o, dtype="<f4").copy()


class May:
    def __init__(self):
        self._mms = None
        self._piper = {}

    def doc(self, giong, text):
        g = GIONG[giong]
        if g["loai"] == "mms":
            import torch
            from transformers import AutoTokenizer, VitsModel
            if self._mms is None:
                self._mms = (AutoTokenizer.from_pretrained(g["mo_hinh"]),
                             VitsModel.from_pretrained(g["mo_hinh"]).eval())
            tok, m = self._mms
            torch.manual_seed(0)
            with torch.no_grad():
                x = m(**tok(text.lower(), return_tensors="pt")).waveform[0].numpy()
            return ve_16k(x, m.config.sampling_rate)
        from piper import PiperVoice, SynthesisConfig
        if g["mo_hinh"] not in self._piper:
            self._piper[g["mo_hinh"]] = PiperVoice.load(str(PIPER_DIR / f"{g['mo_hinh']}.onnx"))
        v = self._piper[g["mo_hinh"]]
        cfg = SynthesisConfig(speaker_id=g.get("speaker"), noise_scale=0.0, noise_w_scale=0.0)
        parts = [c.audio_float_array for c in v.synthesize(text, syn_config=cfg)]
        return ve_16k(np.concatenate(parts), v.config.sample_rate)


def main():
    bo = json.loads((GOC / "docs" / "audio-bench" / "muc-thu.json").read_text(encoding="utf-8"))
    # moi cap toi thieu phai khac nhau o it nhat mot loai tu khoa, neu khong cau thu sai
    cap = {}
    for m in bo["muc"]:
        if m.get("cap"):
            cap.setdefault(m["cap"], []).append(m["van_ban"])
    for k, (a, b) in cap.items():
        assert ct.khac_nhau(ct.trich(a), ct.trich(b)), f"cap {k} khong khac o tu khoa nao"

    (RA / "wav").mkdir(parents=True, exist_ok=True)
    may = May()
    rng = np.random.default_rng(0)
    ra = []
    for m in bo["muc"]:
        doc = m["van_ban"]
        for ten, am in bo["phat_am_thuoc"].items():
            doc = re.sub(rf"\b{ten}\b", am, doc, flags=re.I)
        muc = {**m, "doc": doc, "am": {}}
        for giong in GIONG:
            x = may.doc(giong, doc)
            x = np.concatenate([np.zeros(int(0.3 * SR)), x, np.zeros(int(0.3 * SR))]).astype("float32")
            x = 0.7 * x / (np.abs(x).max() + 1e-9)
            on = rng.normal(0, 1, len(x)).astype("float32")
            on *= np.sqrt(np.mean(x ** 2) / (10 ** (SNR_DB / 10)) / np.mean(on ** 2))
            muc["am"][giong] = {}
            for dk, y in (("sach", x), ("on", x + on)):
                p = RA / "wav" / f"{m['id']}__{giong}__{dk}.wav"
                ghi_wav(p, y)
                muc["am"][giong][dk] = str(p.relative_to(GOC))
            muc["am"][giong]["giay"] = round(len(x) / SR, 2)
        ra.append(muc)
        print(m["id"], {g: muc["am"][g]["giay"] for g in GIONG})
    (RA / "muc-thu.json").write_text(json.dumps({"giong": GIONG, "snr_db": SNR_DB, "muc": ra},
                                                ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
