# -*- coding: utf-8 -*-
"""Đọc lời thoại bộ ca bẫy thành âm thanh bằng VieNeu-TTS (lõi của Zoo Voice), chạy trên máy.

GIỌNG MÁY, KHÔNG PHẢI GIỌNG NGƯỜI. Chỉ để thử chuỗi chép âm của MediTrace. Không phát hành lại.
Giọng Trung của VieNeu (Quang Sơn, Ngọc Trân) không phải giọng Nghệ Tĩnh: ca bay_14 chỉ có
từ địa phương, không có ngữ điệu Nghệ.

    D:/venv-vieneu/Scripts/python -X utf8 thi-nghiem/bo-bay-tay/doc.py [--ca bay_01,bay_13]
Ra: ra/am_thanh/<id>.wav (16 kHz mono) + ra/am_thanh/<id>.json (mốc từng lượt, giọng).
"""
import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
import soundfile as sf

DAY = Path(__file__).resolve().parent
RA = DAY / "ra" / "am_thanh"
SR_RA = 16000
LANG = {"cung_nguoi": 0.35, "doi_nguoi": 0.8}

BS_THEO_VUNG = {"bac": "Hải Đăng", "bac_que": "Hải Đăng", "hue": "Quang Sơn", "nam_bo": "Adam", "nghe_tinh": "Ngọc Trân"}
# (bệnh nhân, người nhà) theo ca — chọn đúng giới và vùng
GIONG = {
    "bay_01": ("Quốc Tuấn", None), "bay_02": (None, "Trúc Ly"), "bay_03": ("Trúc Ly", None),
    "bay_04": (None, "Ngọc Trân"), "bay_05": ("Quốc Tuấn", None), "bay_06": ("Ngọc Huyền", None),
    "bay_07": ("Xuân Vĩnh", None), "bay_08": ("Phạm Tuyên", "Trúc Ly"), "bay_09": ("Quốc Tuấn", None),
    "bay_10": (None, "Đoan Trang"), "bay_11": ("Ngọc Huyền", None), "bay_12": ("Trúc Ly", None),
    "bay_13": (None, "Đức Trí"), "bay_14": ("Quang Sơn", None), "bay_15": (None, "Mỹ Duyên"),
    "bay_16": (None, "Ngọc Huyền"),
}


def ve_16k(x, sr):
    if sr == SR_RA:
        return x
    n = int(round(len(x) * SR_RA / sr))
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ca", default="")
    a = ap.parse_args()
    os.environ.setdefault("HF_HOME", "D:/hf-cache")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from vieneu import Vieneu
    tts = Vieneu(mode="v3turbo", backend="onnx", device="cpu", threads=os.cpu_count() or 4)
    sr = int(getattr(tts, "sample_rate", 48000))
    chon = set(filter(None, a.ca.split(",")))
    RA.mkdir(parents=True, exist_ok=True)
    for ca in map(json.loads, open(DAY / "ra" / "ca_bay.jsonl", encoding="utf-8")):
        if chon and ca["id"] not in chon:
            continue
        bn, nn = GIONG[ca["id"]]
        giong = {"BS": BS_THEO_VUNG[ca["phuong_ngu"]], "BN": bn, "NN": nn}
        dong = ca["input"].split("\n")
        t0, phan, moc, truoc = time.time(), [], [], None
        vi_tri = 0.0
        for i, (vai, d) in enumerate(zip(ca["vai_theo_luot"], dong), 1):
            loi = d.split(":", 1)[1].strip()
            if truoc is not None:
                lang = LANG["cung_nguoi"] if truoc == vai else LANG["doi_nguoi"]
                phan.append(np.zeros(int(lang * SR_RA), np.float32))
                vi_tri += lang
            w = np.asarray(tts.infer(loi, voice=giong[vai], apply_watermark=False), dtype=np.float32).reshape(-1)
            w = ve_16k(w, sr)
            phan.append(w)
            moc.append({"luot": i, "vai": vai, "giong": giong[vai], "bat_dau": round(vi_tri, 2),
                        "ket_thuc": round(vi_tri + len(w) / SR_RA, 2), "loi": loi})
            vi_tri += len(w) / SR_RA
            truoc = vai
        am = np.concatenate(phan)
        am = am / max(1e-6, float(np.abs(am).max())) * 0.9
        sf.write(RA / f"{ca['id']}.wav", am, SR_RA, subtype="PCM_16")
        (RA / f"{ca['id']}.json").write_text(json.dumps(
            {"id": ca["id"], "phuong_ngu": ca["phuong_ngu"], "may_doc": "VieNeu-TTS-v3-Turbo (ONNX/CPU)",
             "ghi_chu": "giọng máy, chỉ để thử", "do_dai_s": round(vi_tri, 1), "luot": moc},
            ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{ca['id']} [{ca['phuong_ngu']}] {vi_tri:.0f}s âm, mất {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
