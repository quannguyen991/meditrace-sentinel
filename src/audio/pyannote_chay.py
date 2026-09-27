# -*- coding: utf-8 -*-
"""Chay pyannote tach nguoi noi tren MOT tep WAV, ghi ket qua ra JSON.

TEP NAY CHAY TRONG MOI TRUONG PYTHON RIENG (vd D:/pyannote-venv), KHONG trong moi truong
cua duong ong duoc do. Ly do: pyannote.audio keo theo torch, lightning, speechbrain... voi
phien ban rieng; cai chung se lam doi moi truong da khoa trong ban dang ky truoc
(transformers 4.57.6, peft 0.20.0, bitsandbytes 0.50.2). Vi vay tep nay KHONG import gi
tu `src`, chi dung thu vien chuan + pyannote + soundfile.

Duoc goi boi `src/audio/pyannote_provider.py` qua subprocess:

    <python cua moi truong pyannote> pyannote_chay.py --vao processed.wav --ra pyannote.json
        [--mo-hinh pyannote/speaker-diarization-3.1] [--thiet-bi cpu|cuda]
        [--it-nhat N] [--nhieu-nhat N]

Khoa Hugging Face (mo hinh bi khoa, phai dong y dieu khoan) doc tu bien moi truong HF_TOKEN,
KHONG nhan qua dong lenh (dong lenh hien trong danh sach tien trinh). Khi da tai mo hinh ve
bo nho dem, chay voi HF_HUB_OFFLINE=1 va khong can khoa.

Ra (JSON):
    {"segments": [{"speaker_id": "speaker_1", "start": 0.52, "end": 3.1}, ...],
     "so_nguoi_noi": 2, "mo_hinh": ..., "pyannote": "3.4.0", "torch": ..., "thiet_bi": "cpu",
     "giay": 12.3}
Nhan nguoi noi danh lai theo thu tu XUAT HIEN DAU TIEN: speaker_1 la nguoi noi truoc.
Khong gan vai (bac si, benh nhan...). Vai do nguoi dung gan.

Ma thoat: 0 xong; 2 khong nap duoc mo hinh (chua co khoa / chua dong y dieu khoan / khong
co ban trong bo nho dem); 3 loi khac. Dong cuoi cua stderr la JSON {"loi": ma, "chi_tiet": ...}.
"""
import argparse
import json
import os
import sys
import time
import warnings


def _bao_loi(ma, chi_tiet, thoat):
    print(json.dumps({"loi": ma, "chi_tiet": str(chi_tiet)[:500]}, ensure_ascii=False), file=sys.stderr)
    sys.exit(thoat)


def cho_phep_lop_trong_checkpoint():
    """torch >= 2.6 nap checkpoint voi weights_only=True: chi dung lai cac lop trong danh sach
    cho phep. Checkpoint cua pyannote 3.x luu kem bon lop Python (da liet ke bang pickletools
    tren pytorch_model.bin cua wespeaker-voxceleb-resnet34-LM, 25/09/2026): TorchVersion va
    dac ta tac vu Specifications, Problem, Resolution. Them DUNG bon lop do; KHONG tat
    weights_only, vi tat thi mot checkpoint bat ky co the chay ma tuy y khi nap."""
    import torch
    if not hasattr(torch.serialization, "add_safe_globals"):   # torch < 2.4: khong can
        return
    from torch.torch_version import TorchVersion
    from pyannote.audio.core.task import Problem, Resolution, Specifications
    torch.serialization.add_safe_globals([TorchVersion, Specifications, Problem, Resolution])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vao", required=True)
    ap.add_argument("--ra", required=True)
    ap.add_argument("--mo-hinh", default="pyannote/speaker-diarization-3.1")
    ap.add_argument("--thiet-bi", default="cpu", choices=["cpu", "cuda"])
    ap.add_argument("--it-nhat", type=int, default=None, help="so nguoi noi toi thieu (neu biet)")
    ap.add_argument("--nhieu-nhat", type=int, default=None, help="so nguoi noi toi da (neu biet)")
    a = ap.parse_args()

    warnings.filterwarnings("ignore")
    t0 = time.time()
    try:
        import numpy as np
        import soundfile as sf
        import torch
        import pyannote.audio
        from pyannote.audio import Pipeline
    except Exception as exc:  # moi truong chua cai du
        _bao_loi("pyannote_chua_cai", exc, 3)

    token = os.environ.get("HF_TOKEN") or None
    try:
        cho_phep_lop_trong_checkpoint()
        pipeline = Pipeline.from_pretrained(a.mo_hinh, use_auth_token=token)
    except Exception as exc:
        _bao_loi("mo_hinh_khong_nap_duoc", exc, 2)
    if pipeline is None:  # pyannote tra None khi mo hinh bi khoa ma khong co quyen
        _bao_loi("mo_hinh_khong_nap_duoc", "Pipeline.from_pretrained tra None (mo hinh bi khoa?)", 2)
    if a.thiet_bi == "cuda":
        pipeline.to(torch.device("cuda"))

    try:
        # Doc vao bo nho (soundfile), khong de pyannote tu giai ma tep.
        x, sr = sf.read(a.vao, dtype="float32", always_2d=True)
        waveform = torch.from_numpy(np.ascontiguousarray(x.T))  # (kenh, mau)
        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)
        tham_so = {}
        if a.it_nhat:
            tham_so["min_speakers"] = a.it_nhat
        if a.nhieu_nhat:
            tham_so["max_speakers"] = a.nhieu_nhat
        ket_qua = pipeline({"waveform": waveform, "sample_rate": sr}, **tham_so)
    except Exception as exc:
        _bao_loi("tach_nguoi_noi_loi", exc, 3)

    nhan_moi, doan = {}, []
    for luot, _, nhan in ket_qua.itertracks(yield_label=True):
        if nhan not in nhan_moi:
            nhan_moi[nhan] = f"speaker_{len(nhan_moi) + 1}"
        doan.append({"speaker_id": nhan_moi[nhan], "start": round(float(luot.start), 3),
                     "end": round(float(luot.end), 3)})
    doan.sort(key=lambda d: (d["start"], d["end"]))
    ra = {"segments": doan, "so_nguoi_noi": len(nhan_moi), "mo_hinh": a.mo_hinh,
          "pyannote": pyannote.audio.__version__, "torch": torch.__version__,
          "thiet_bi": a.thiet_bi, "giay": round(time.time() - t0, 2)}
    with open(a.ra, "w", encoding="utf-8") as f:
        json.dump(ra, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
