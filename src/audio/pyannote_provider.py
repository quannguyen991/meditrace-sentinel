# -*- coding: utf-8 -*-
"""Tach nguoi noi bang pyannote, chay trong MOI TRUONG PYTHON RIENG qua subprocess.

VI SAO MOI TRUONG RIENG. pyannote.audio can torch, lightning, speechbrain... theo phien ban
cua no. Moi truong cua dich vu la moi truong da khoa trong ban dang ky truoc (transformers
4.57.6, peft 0.20.0, bitsandbytes 0.50.2); cai pyannote vao do co the doi goi phu thuoc va
lam doi ket qua da do. Vi vay dich vu goi `pyannote_chay.py` bang python cua moi truong rieng
(bien PYANNOTE_PYTHON), doc ket qua JSON.

VI SAO CO TRAN RAM. Tren HoaiDuc, toan bo phan mem cua du an chi duoc dung 10 GB RAM. Tien
trinh con bi do moi 0,5 s: vuot tran rieng (PYANNOTE_RAM_GB) hoac tong RAM cua dich vu cong
tien trinh con vuot PYANNOTE_TONG_RAM_GB thi bi giet.

KHONG DOAN VAI. Ket qua chi co speaker_1, speaker_2... Vai bac si / benh nhan / nguoi nha
van do nguoi dung gan.

Khoa Hugging Face doc tu tep (PYANNOTE_TOKEN_FILE) va chuyen qua bien moi truong HF_TOKEN,
khong qua dong lenh, khong ghi vao nhat ky. Khong co tep khoa thi chay voi HF_HUB_OFFLINE=1:
chi dung mo hinh da co trong bo nho dem.
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


class LoiTachNguoiNoi(RuntimeError):
    """Ma loi ngan (str(exc)) de pipeline ghi nhat ky va lui ve mot nguoi noi."""


def _rss(p) -> int:
    """RAM vat ly cua tien trinh va moi tien trinh con cua no (byte)."""
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


class PyannoteDiarizationProvider:
    """Nha cung cap tach nguoi noi that. `tach_that = True` bao pipeline gop luot lien tiep."""

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

    # -- dung lenh (tach rieng de phep thu kiem khoa KHONG nam trong dong lenh) --------
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
            # pyannote 3.x KHONG luu mo hinh theo HF_HOME ma theo PYANNOTE_CACHE (mac dinh
            # ~/.cache/torch/pyannote). Dat ca hai vao cung <hf_home>/hub de mot thu muc chua du
            # mo hinh: chay khong mang va chep sang may khac chi can chep thu muc nay.
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
            except psutil.NoSuchProcess:  # thoat ngay (vd loi nap), khong can do RAM
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
        """Lay ma loi tu dong JSON cuoi cua nhat ky; khong co thi dung ma thoat."""
        try:
            dong = [d for d in nhat_ky.read_text(encoding="utf-8", errors="replace").splitlines()
                    if d.strip().startswith("{")]
            if dong:
                return str(json.loads(dong[-1]).get("loi") or f"pyannote_ma_thoat_{ma_thoat}")
        except (OSError, json.JSONDecodeError):
            pass
        return f"pyannote_ma_thoat_{ma_thoat}"
