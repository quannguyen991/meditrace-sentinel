# -*- coding: utf-8 -*-
"""[Âm thanh]
Làm gì   : Tách người nói bằng pyannote bằng cách gọi tiến trình con trong môi trường Python
           riêng, có giới hạn bộ nhớ.
Vào → Ra : tệp WAV → danh sách đoạn (đầu, cuối, nhãn người nói); lỗi thì báo LoiTachNguoiNoi
Đọc từ   : class PyannoteDiarizationProvider tách người nói qua tiến trình con; class
           LoiTachNguoiNoi lỗi tách
Mục lục (các hàm/lớp chính):
  class PyannoteDiarizationProvider  Tách người nói bằng pyannote trong môi trường riêng
  class LoiTachNguoiNoi              Lỗi tách người nói có mã ngắn để pipeline lùi về
Dùng bởi : audio/pipeline
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Tách người nói bằng pyannote, chạy trong MÔI TRƯỜNG PYTHON RIÊNG qua subprocess.

VÌ SAO MÔI TRƯỜNG RIÊNG. pyannote.audio cần torch, lightning, speechbrain... theo phiên bản
của nó. Môi trường của dịch vụ là môi trường đã khoá trong bản đăng ký trước (transformers
4.57.6, peft 0.20.0, bitsandbytes 0.50.2); cài pyannote vào đó có thể đổi gói phụ thuộc và
làm đổi kết quả đã đo. Vì vậy dịch vụ gọi `pyannote_chay.py` bằng python của môi trường riêng
(biến PYANNOTE_PYTHON), đọc kết quả JSON.

VÌ SAO CÓ TRẦN RAM. Trên HoaiDuc, toàn bộ phần mềm của dự án chỉ được dùng 10 GB RAM. Tiến
trình con bị đo mỗi 0,5 s: vượt trần riêng (PYANNOTE_RAM_GB) hoặc tổng RAM của dịch vụ cộng
tiến trình con vượt PYANNOTE_TONG_RAM_GB thì bị giết.

KHÔNG ĐOÁN VAI. Kết quả chỉ có speaker_1, speaker_2... Vai bác sĩ / bệnh nhân / người nhà
vẫn do người dùng gán.

Khoá Hugging Face đọc từ tệp (PYANNOTE_TOKEN_FILE) và chuyển qua biến môi trường HF_TOKEN,
không qua dòng lệnh, không ghi vào nhật ký. Không có tệp khoá thì chạy với HF_HUB_OFFLINE=1:
chỉ dùng mô hình đã có trong bộ nhớ đệm.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

TEP_CHAY = Path(__file__).resolve().with_name("pyannote_chay.py")
MO_HINH_MAC_DINH = "pyannote/speaker-diarization-3.1"


# ═══ class LoiTachNguoiNoi — Lỗi tách người nói có mã ngắn để pipeline lùi về ═════════
class LoiTachNguoiNoi(RuntimeError):
    """Mã lỗi ngắn (str(exc)) để pipeline ghi nhật ký và lùi về một người nói."""


# ─── _rss() — Đo RAM vật lý của tiến trình và các tiến trình con ──────────────────────
def _rss(p) -> int:
    """RAM vật lý của tiến trình và mọi tiến trình con của nó (byte)."""
    import psutil
    tong = 0
    try:
        ds = [p] + p.children(recursive=True)
    except psutil.Error:
        return 0
    for q in ds:
        try:
            tong += q.memory_info().rss
        except psutil.Error:
            pass
    return tong


# ─── _giet_ca_cay() — Kết thúc tiến trình và toàn bộ tiến trình con ───────────────────
def _giet_ca_cay(p) -> None:
    import psutil
    try:
        con = p.children(recursive=True)
    except psutil.Error:
        con = []
    for q in con + [p]:
        try:
            q.kill()
        except psutil.Error:
            pass


# ═══ class PyannoteDiarizationProvider — Tách người nói bằng pyannote trong môi trường riêng ═══
# Chạy qua subprocess, giám sát RAM và thời gian, quá ngưỡng thì dừng; chỉ ra speaker_1,
# speaker_2, không đoán vai.
class PyannoteDiarizationProvider:
    """Nhà cung cấp tách người nói thật. `tach_that = True` báo pipeline gộp lượt liên tiếp."""

    tach_that = True
    ten = "pyannote"

    def __init__(self, python_exe: str, model: str = MO_HINH_MAC_DINH,
                 token_file: Optional[str] = None, device: str = "cpu",
                 ram_gb: float = 3.0, tong_ram_gb: float = 9.5, timeout_s: float = 1200.0,
                 min_speakers: Optional[int] = None, max_speakers: Optional[int] = None,
                 hf_home: Optional[str] = None, script: Optional[str] = None):
        self.python_exe = python_exe
        self.model = model
        self.token_file = token_file
        self.device = device
        self.ram_gb = ram_gb
        self.tong_ram_gb = tong_ram_gb
        self.timeout_s = timeout_s
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers
        self.hf_home = hf_home
        self.script = script or str(TEP_CHAY)
        self.last_info: dict[str, Any] = {}

    @classmethod
    def from_settings(cls, s) -> "PyannoteDiarizationProvider":
        if not s.pyannote_python:
            raise LoiTachNguoiNoi("pyannote_chua_cau_hinh")
        return cls(s.pyannote_python, s.pyannote_model or MO_HINH_MAC_DINH, s.pyannote_token_file,
                   s.pyannote_device or "cpu", s.pyannote_ram_gb, s.pyannote_tong_ram_gb,
                   s.pyannote_timeout_s, s.pyannote_min_speakers, s.pyannote_max_speakers,
                   s.pyannote_hf_home)

    # -- dựng lệnh (tách riêng để phép thử kiểm khoá KHÔNG nằm trong dòng lệnh) --------
    def lenh(self, wav: Path, ra: Path) -> list[str]:
        cmd = [self.python_exe, self.script, "--vao", str(wav), "--ra", str(ra),
               "--mo-hinh", self.model, "--thiet-bi", self.device]
        if self.min_speakers:
            cmd += ["--it-nhat", str(self.min_speakers)]
        if self.max_speakers:
            cmd += ["--nhieu-nhat", str(self.max_speakers)]
        return cmd

    def moi_truong(self) -> dict[str, str]:
        env = dict(os.environ)
        env.pop("HF_TOKEN", None)
        token = ""
        if self.token_file and Path(self.token_file).exists():
            token = Path(self.token_file).read_text(encoding="utf-8").strip()
        if token:
            env["HF_TOKEN"] = token
        else:
            env["HF_HUB_OFFLINE"] = "1"
        if self.hf_home:
            # pyannote 3.x KHÔNG lưu mô hình theo HF_HOME mà theo PYANNOTE_CACHE (mặc định
            # ~/.cache/torch/pyannote). Đặt cả hai vào cùng <hf_home>/hub để một thư mục chứa đủ
            # mô hình: chạy không mạng và chép sang máy khác chỉ cần chép thư mục này.
            env["HF_HOME"] = self.hf_home
            env["PYANNOTE_CACHE"] = str(Path(self.hf_home) / "hub")
        env["PYTHONUTF8"] = "1"
        return env

    # -----------------------------------------------------------------------------
    def diarize(self, audio_path, speech_segments) -> list[dict[str, Any]]:
        import psutil

        wav = Path(audio_path)
        ra = wav.with_name("pyannote.json")
        nhat_ky = wav.with_name("pyannote.log")
        if ra.exists():
            ra.unlink()
        if not Path(self.python_exe).exists():
            raise LoiTachNguoiNoi("pyannote_python_khong_co")
        t0 = time.time()
        dinh_ram = 0
        with open(nhat_ky, "w", encoding="utf-8", errors="replace") as log:
            proc = subprocess.Popen(self.lenh(wav, ra), env=self.moi_truong(),
                                    stdout=log, stderr=log)
            try:
                p = psutil.Process(proc.pid)
            except psutil.NoSuchProcess:  # thoát ngay (vd lỗi nạp), không cần đo RAM
                p = None
            cha = psutil.Process(os.getpid())
            while p is not None and proc.poll() is None:
                con = _rss(p)
                dinh_ram = max(dinh_ram, con)
                try:
                    tong = con + cha.memory_info().rss
                except psutil.Error:
                    tong = con
                if con > self.ram_gb * 2**30 or tong > self.tong_ram_gb * 2**30:
                    _giet_ca_cay(p)
                    proc.wait(timeout=30)
                    raise LoiTachNguoiNoi("pyannote_vuot_tran_ram")
                if time.time() - t0 > self.timeout_s:
                    _giet_ca_cay(p)
                    proc.wait(timeout=30)
                    raise LoiTachNguoiNoi("pyannote_qua_thoi_gian")
                time.sleep(0.5)
            proc.wait()
        if proc.returncode != 0:
            raise LoiTachNguoiNoi(self._ma_loi(nhat_ky, proc.returncode))
        if not ra.exists():
            raise LoiTachNguoiNoi("pyannote_khong_ra_ket_qua")
        du = json.loads(ra.read_text(encoding="utf-8"))
        doan = [d for d in du.get("segments", [])
                if d.get("speaker_id") and d.get("end", 0) > d.get("start", 0)]
        self.last_info = {"phuong_phap": "pyannote", "mo_hinh": du.get("mo_hinh"),
                          "pyannote": du.get("pyannote"), "thiet_bi": du.get("thiet_bi"),
                          "so_nguoi_noi": du.get("so_nguoi_noi"),
                          "giay": round(time.time() - t0, 2),
                          "ram_dinh_mb": round(dinh_ram / 2**20)}
        return doan

    @staticmethod
    def _ma_loi(nhat_ky: Path, ma_thoat: int) -> str:
        """Lấy mã lỗi từ dòng JSON cuối của nhật ký; không có thì dùng mã thoát."""
        try:
            dong = [d for d in nhat_ky.read_text(encoding="utf-8", errors="replace").splitlines()
                    if d.strip().startswith("{")]
            if dong:
                return str(json.loads(dong[-1]).get("loi") or f"pyannote_ma_thoat_{ma_thoat}")
        except (OSError, json.JSONDecodeError):
            pass
        return f"pyannote_ma_thoat_{ma_thoat}"
