# -*- coding: utf-8 -*-
"""Chép âm bộ ca bẫy bằng PhoWhisper của MediTrace (src/audio/asr), rồi xem từ then chốt còn không.

Cắt âm theo mốc từng lượt (ra/am_thanh/<id>.json), tức là GIẢ ĐỊNH tách người nói hoàn hảo:
chỉ đo lỗi chép chữ, không đo lỗi tách người nói.

    HF_HOME=... D:/khkt-venv-lap/Scripts/python -X utf8 thi-nghiem/bo-bay-tay/nghe.py [--mo-hinh medium]
Ra: ra/loi_thoai_asr.jsonl ({id, input}) để chạy `do.py --loi-thoai`, và ra/asr_tu_then_chot.json.
"""
import argparse
import json
import re
import sys
import tempfile
import unicodedata
from pathlib import Path

import wave

import numpy as np


class sf:  # đủ dùng cho WAV PCM16 mono, khỏi cần soundfile trong venv đo
    @staticmethod
    def read(p, dtype="float32"):
        with wave.open(str(p)) as w:
            x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32768
            return x, w.getframerate()

    @staticmethod
    def write(p, x, sr, subtype=None):
        with wave.open(str(p), "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes((np.clip(x, -1, 1) * 32767).astype("<i2").tobytes())

DAY = Path(__file__).resolve().parent
GOC = DAY.parents[1]
sys.path.insert(0, str(GOC))

VAI = {"BS": "Bác sĩ", "BN": "Bệnh nhân", "NN": "Người nhà"}
PHU_DINH = {"không", "chưa", "hổng", "nỏ", "chẳng", "hông"}
BEN = {"trái", "phải"}
THUOC = {"amlodipin", "losartan", "penicillin", "aspirin", "paracetamol", "metformin", "insulin", "furosemid",
         "bisoprolol", "omeprazol", "kali", "atorvastatin", "amoxicillin", "azithromycin", "cephalexin",
         "fosfomycin", "panadol", "ibuprofen", "diclofenac", "digoxin", "doxycycline"}
SO_CHU = {"một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười", "mươi", "trăm", "nghìn"}


def tu(s):
    s = unicodedata.normalize("NFC", s.lower())
    return re.findall(r"\w+", s)


def nhom(t):
    if t in PHU_DINH:
        return "phu_dinh"
    if t in BEN:
        return "ben"
    if t in THUOC:
        return "thuoc"
    if t.isdigit() or t in SO_CHU:
        return "so"
    return None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--mo-hinh", default="medium")
    a = ap.parse_args()
    from src.audio.asr.phowhisper_provider import PhoWhisperProvider
    asr = PhoWhisperProvider(model=f"vinai/PhoWhisper-{a.mo_hinh}")
    ra_jsonl, bao = [], {"mo_hinh": f"vinai/PhoWhisper-{a.mo_hinh}", "gia_dinh": "tách người nói hoàn hảo", "theo_ca": []}
    tam = Path(tempfile.mkdtemp(prefix="bay-asr-"))
    tong = {}
    for ca in map(json.loads, open(DAY / "ra" / "ca_bay.jsonl", encoding="utf-8")):
        wav = DAY / "ra" / "am_thanh" / f"{ca['id']}.wav"
        if not wav.exists():
            continue
        moc = json.loads((DAY / "ra" / "am_thanh" / f"{ca['id']}.json").read_text(encoding="utf-8"))
        am, sr = sf.read(wav, dtype="float32")
        dong, mat = [], []
        for m in moc["luot"]:
            doan = am[int(m["bat_dau"] * sr): int(m["ket_thuc"] * sr) + int(0.1 * sr)]
            p = tam / f"{ca['id']}_{m['luot']}.wav"
            sf.write(p, np.concatenate([np.zeros(int(0.2 * sr), np.float32), doan]), sr, subtype="PCM_16")
            kq = asr.transcribe(p)
            chu = " ".join(s.text for s in kq.segments).strip()
            dong.append(f"{VAI[m['vai']]}: {chu}")
            goc, nghe = tu(m["loi"]), tu(chu)
            for t in set(goc):
                g = nhom(t)
                if g is None:
                    continue
                c = tong.setdefault(ca["phuong_ngu"], {}).setdefault(g, [0, 0])
                n_goc, n_nghe = goc.count(t), nghe.count(t)
                c[0] += n_goc
                c[1] += min(n_goc, n_nghe)
                if n_nghe < n_goc:
                    mat.append({"luot": m["luot"], "tu": t, "nhom": g, "goc": m["loi"], "nghe": chu})
        ra_jsonl.append({"id": ca["id"], "input": "\n".join(dong)})
        bao["theo_ca"].append({"id": ca["id"], "phuong_ngu": ca["phuong_ngu"], "mat_tu_then_chot": mat})
        print(f"{ca['id']} [{ca['phuong_ngu']}] mất {len(mat)} từ then chốt", flush=True)
        for x in mat:
            print(f"   lượt {x['luot']} '{x['tu']}' ({x['nhom']}): {x['nghe']}")
    bao["giu_lai_theo_vung"] = {v: {g: f"{k[1]}/{k[0]}" for g, k in d.items()} for v, d in tong.items()}
    with open(DAY / "ra" / "loi_thoai_asr.jsonl", "w", encoding="utf-8") as f:
        for r in ra_jsonl:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (DAY / "ra" / "asr_tu_then_chot.json").write_text(json.dumps(bao, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nTừ then chốt còn giữ (theo vùng):")
    for v, d in bao["giu_lai_theo_vung"].items():
        print(f"  {v:<10} " + "  ".join(f"{g} {x}" for g, x in sorted(d.items())))


if __name__ == "__main__":
    main()
