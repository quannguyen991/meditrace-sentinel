# -*- coding: utf-8 -*-
"""[Âm thanh]
Làm gì   : Chạy pyannote trên một tệp WAV trong môi trường riêng và ghi kết quả tách người
           nói ra tệp JSON.
Vào → Ra : đường dẫn WAV + đường dẫn JSON đầu ra → tệp JSON các đoạn kèm nhãn người nói
Đọc từ   : main() là toàn bộ luồng chạy; cho_phep_lop_trong_checkpoint() cho tải mô hình
Mục lục (các hàm/lớp chính):
  main()                           Chạy pyannote tách người nói trên một tệp WAV, ghi JSON
  cho_phep_lop_trong_checkpoint()  Cho phép đúng bốn lớp mà checkpoint pyannote cần
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chạy pyannote tách người nói trên MỘT tệp WAV, ghi kết quả ra JSON.

TỆP NÀY CHẠY TRONG MÔI TRƯỜNG PYTHON RIÊNG (vd D:/pyannote-venv), KHÔNG trong môi trường
của đường ống được đo. Lý do: pyannote.audio kéo theo torch, lightning, speechbrain... với
phiên bản riêng; cài chúng sẽ làm đổi môi trường đã khoá trong bản đăng ký trước
(transformers 4.57.6, peft 0.20.0, bitsandbytes 0.50.2). Vì vậy tệp này KHÔNG import gì
từ `src`, chỉ dùng thư viện chuẩn + pyannote + soundfile.

Được gọi bởi `src/audio/pyannote_provider.py` qua subprocess:

    <python của môi trường pyannote> pyannote_chay.py --vao processed.wav --ra pyannote.json
        [--mo-hinh pyannote/speaker-diarization-3.1] [--thiet-bi cpu|cuda]
        [--it-nhat N] [--nhieu-nhat N]

Khoá Hugging Face (mô hình bị khoá, phải đồng ý điều khoản) đọc từ biến môi trường HF_TOKEN,
KHÔNG nhận qua dòng lệnh (dòng lệnh hiện trong danh sách tiến trình). Khi đã tải mô hình về
bộ nhớ đệm, chạy với HF_HUB_OFFLINE=1 và không cần khoá.

Ra (JSON):
    {"segments": [{"speaker_id": "speaker_1", "start": 0.52, "end": 3.1}, ...],
     "so_nguoi_noi": 2, "mo_hinh": ..., "pyannote": "3.4.0", "torch": ..., "thiet_bi": "cpu",
     "giay": 12.3}
Nhãn người nói đánh lại theo thứ tự XUẤT HIỆN ĐẦU TIÊN: speaker_1 là người nói trước.
Không gán vai (bác sĩ, bệnh nhân...). Vai do người dùng gán.

Mã thoát: 0 xong; 2 không nạp được mô hình (chưa có khoá / chưa đồng ý điều khoản / không
có bản trong bộ nhớ đệm); 3 lỗi khác. Dòng cuối của stderr là JSON {"loi": ma, "chi_tiet": ...}.
"""
import argparse
import json
import os
import sys
import time
import warnings


# ─── _bao_loi() — In lỗi JSON ra stderr rồi thoát ─────────────────────────────────────
def _bao_loi(ma, chi_tiet, thoat):
    print(json.dumps({"loi": ma, "chi_tiet": str(chi_tiet)[:500]}, ensure_ascii=False), file=sys.stderr)
    sys.exit(thoat)


# ═══ cho_phep_lop_trong_checkpoint() — Cho phép đúng bốn lớp mà checkpoint pyannote cần ═══
# Không tắt weights_only để tránh chạy mã tuỳ ý khi nạp.
def cho_phep_lop_trong_checkpoint():
    """torch >= 2.6 nạp checkpoint với weights_only=True: chỉ dùng lại các lớp trong danh sách
    cho phép. Checkpoint của pyannote 3.x lưu kèm bốn lớp Python (đã liệt kê bằng pickletools
    trên pytorch_model.bin của wespeaker-voxceleb-resnet34-LM, 25/09/2026): TorchVersion và
    đặc tả tác vụ Specifications, Problem, Resolution. Thêm ĐÚNG bốn lớp đó; KHÔNG tắt
    weights_only, vì tắt thì một checkpoint bất kỳ có thể chạy mã tùy ý khi nạp."""
    import torch
    if not hasattr(torch.serialization, "add_safe_globals"):   # torch < 2.4: không cần
        return
    from torch.torch_version import TorchVersion
    from pyannote.audio.core.task import Problem, Resolution, Specifications
    torch.serialization.add_safe_globals([TorchVersion, Specifications, Problem, Resolution])


# ═══ main() — Chạy pyannote tách người nói trên một tệp WAV, ghi JSON ═════════════════
# Chạy trong môi trường Python riêng; nhãn đánh lại theo thứ tự xuất hiện, không gán
# vai.
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
    except Exception as exc:  # môi trường chưa cài đủ
        _bao_loi("pyannote_chua_cai", exc, 3)

    token = os.environ.get("HF_TOKEN") or None
    try:
        cho_phep_lop_trong_checkpoint()
        pipeline = Pipeline.from_pretrained(a.mo_hinh, use_auth_token=token)
    except Exception as exc:
        _bao_loi("mo_hinh_khong_nap_duoc", exc, 2)
    if pipeline is None:  # pyannote trả None khi mô hình bị khoá mà không có quyền
        _bao_loi("mo_hinh_khong_nap_duoc", "Pipeline.from_pretrained tra None (mo hinh bi khoa?)", 2)
    if a.thiet_bi == "cuda":
        pipeline.to(torch.device("cuda"))

    try:
        # Đọc vào bộ nhớ (soundfile), không để pyannote tự giải mã tệp.
        x, sr = sf.read(a.vao, dtype="float32", always_2d=True)
        waveform = torch.from_numpy(np.ascontiguousarray(x.T))  # (kênh, mẫu)
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
