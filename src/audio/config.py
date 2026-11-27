"""[Âm thanh]
Làm gì   : Đọc các tuỳ chọn xử lý âm thanh từ biến môi trường vào một đối tượng cấu hình.
Vào → Ra : biến môi trường → AudioSettings: bộ chép, thiết bị, thư mục lưu, các cờ bật tắt
Đọc từ   : class AudioSettings chứa toàn bộ tuỳ chọn và giá trị mặc định
Mục lục (các hàm/lớp chính):
  class AudioSettings  Cấu hình xử lý âm thanh lấy từ biến môi trường
Dùng bởi : audio/pipeline, he_thong/dich_vu_http
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Cấu hình môi trường cho xử lý âm thanh.

    PROCESSING_MODE=local            local | external (nhà cung cấp ngoài bị từ chối ở chế độ local)
    ASR_PROVIDER=phowhisper          phowhisper | faster_whisper | sidecar | auto
    ASR_MODEL=vinai/PhoWhisper-small (hoặc "small", "medium" cho PhoWhisper)
    ASR_DEVICE=cuda                  cuda | cpu (để trống = tự động)
    ASR_REVISION=                    commit Hugging Face; để trống = mặc định đã ghim
    ALLOW_ASR_FALLBACK=false         chỉ khi đó mới được thay nhà cung cấp bị lỗi
    ASR_FALLBACK_PROVIDER=           ví dụ faster_whisper
    ASR_FALLBACK_MODEL=
    ASR_COMPARE_PROVIDER=            chạy nhà cung cấp thứ hai và đánh dấu bất đồng
    ASR_COMPARE_MODEL=

    DIARIZATION_PROVIDER=mot_nguoi   mot_nguoi (cả bản ghi một người nói) | pyannote
    PYANNOTE_PYTHON=                 python của MÔI TRƯỜNG RIÊNG có pyannote.audio
    PYANNOTE_MODEL=pyannote/speaker-diarization-3.1
    PYANNOTE_TOKEN_FILE=             tệp chứa khoá Hugging Face (chỉ cần khi tải mô hình lần đầu)
    PYANNOTE_DEVICE=cpu              cpu | cuda
    PYANNOTE_RAM_GB=3                trần RAM riêng của tiến trình pyannote
    PYANNOTE_TONG_RAM_GB=9.5         trần RAM dịch vụ + pyannote (HoaiDuc: 10 GB cho cả dự án)
    PYANNOTE_TIMEOUT_S=1200
    PYANNOTE_MIN_SPEAKERS= / PYANNOTE_MAX_SPEAKERS=   nếu biết trước số người nói
    PYANNOTE_HF_HOME=                thư mục bộ nhớ đệm Hugging Face của môi trường pyannote
    GOP_LUOT_CUNG_NGUOI_NOI=true     tách thật rồi thì gộp các đoạn liên tiếp cùng người nói

Tên cũ WHISPER_MODEL / WHISPER_DEVICE vẫn được đọc cho chế độ ``auto``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


# ─── _bool() — Đọc chuỗi môi trường thành giá trị đúng sai ────────────────────────────
def _bool(v: Optional[str]) -> bool:
    return str(v or "").strip().lower() in {"1", "true", "yes", "on"}


# ─── _opt() — Đọc biến môi trường, rỗng thì trả None ──────────────────────────────────
def _opt(name: str) -> Optional[str]:
    v = os.getenv(name, "").strip()
    return v or None


# ─── _so() — Đọc biến môi trường thành số ─────────────────────────────────────────────
def _so(name: str, mac_dinh=None, kieu=float):
    v = os.getenv(name, "").strip()
    return kieu(v) if v else mac_dinh


# ═══ class AudioSettings — Cấu hình xử lý âm thanh lấy từ biến môi trường ═════════════
# from_env kiểm tra chế độ xử lý và nhà cung cấp tách người nói; sai thì báo lỗi.
@dataclass(frozen=True)
class AudioSettings:
    processing_mode: str = "local"
    asr_provider: str = "auto"
    whisper_model: str = "small"
    whisper_device: str = "cpu"
    asr_model: Optional[str] = None
    asr_device: Optional[str] = None
    asr_revision: Optional[str] = None
    allow_asr_fallback: bool = False
    asr_fallback_provider: Optional[str] = None
    asr_fallback_model: Optional[str] = None
    asr_compare_provider: Optional[str] = None
    asr_compare_model: Optional[str] = None
    diarization_provider: str = "mot_nguoi"
    pyannote_python: Optional[str] = None
    pyannote_model: Optional[str] = None
    pyannote_token_file: Optional[str] = None
    pyannote_device: Optional[str] = None
    pyannote_ram_gb: float = 3.0
    pyannote_tong_ram_gb: float = 9.5
    pyannote_timeout_s: float = 1200.0
    pyannote_min_speakers: Optional[int] = None
    pyannote_max_speakers: Optional[int] = None
    pyannote_hf_home: Optional[str] = None
    gop_luot_cung_nguoi_noi: bool = True

    @classmethod
    def from_env(cls) -> "AudioSettings":
        mode = os.getenv("PROCESSING_MODE", "local").lower()
        if mode not in {"local", "external"}:
            raise ValueError("invalid_processing_mode")
        dia = os.getenv("DIARIZATION_PROVIDER", "mot_nguoi").strip().lower().replace("-", "_")
        if dia not in {"mot_nguoi", "pyannote"}:
            raise ValueError("invalid_diarization_provider")
        return cls(mode, os.getenv("ASR_PROVIDER", "auto").lower(),
                   os.getenv("WHISPER_MODEL", "small"), os.getenv("WHISPER_DEVICE", "cpu"),
                   _opt("ASR_MODEL"), _opt("ASR_DEVICE"), _opt("ASR_REVISION"),
                   _bool(os.getenv("ALLOW_ASR_FALLBACK")), _opt("ASR_FALLBACK_PROVIDER"),
                   _opt("ASR_FALLBACK_MODEL"), _opt("ASR_COMPARE_PROVIDER"),
                   _opt("ASR_COMPARE_MODEL"),
                   diarization_provider=dia,
                   pyannote_python=_opt("PYANNOTE_PYTHON"),
                   pyannote_model=_opt("PYANNOTE_MODEL"),
                   pyannote_token_file=_opt("PYANNOTE_TOKEN_FILE"),
                   pyannote_device=_opt("PYANNOTE_DEVICE"),
                   pyannote_ram_gb=_so("PYANNOTE_RAM_GB", 3.0),
                   pyannote_tong_ram_gb=_so("PYANNOTE_TONG_RAM_GB", 9.5),
                   pyannote_timeout_s=_so("PYANNOTE_TIMEOUT_S", 1200.0),
                   pyannote_min_speakers=_so("PYANNOTE_MIN_SPEAKERS", None, int),
                   pyannote_max_speakers=_so("PYANNOTE_MAX_SPEAKERS", None, int),
                   pyannote_hf_home=_opt("PYANNOTE_HF_HOME"),
                   gop_luot_cung_nguoi_noi=os.getenv("GOP_LUOT_CUNG_NGUOI_NOI", "true").strip().lower()
                   not in {"0", "false", "no", "off"})
