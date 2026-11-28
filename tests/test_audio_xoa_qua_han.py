"""Hạn giữ âm thanh: phiên đã duyệt quá hạn thì xoá tệp ghi âm, giữ lời thoại và nhật ký."""

from __future__ import annotations

import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.audio.pipeline import AudioPipeline
from src.audio.storage import SessionStore

BAY = time.time()


def _iso(ngay_truoc: float) -> str:
    t = datetime.fromtimestamp(BAY, timezone.utc) - timedelta(days=ngay_truoc)
    return t.isoformat().replace("+00:00", "Z")


def _phien(store: SessionStore, ngay_truoc: float, da_duyet: bool, raw_path: Path | None = None) -> str:
    s = store.create()
    sid = s["session_id"]
    raw = store.path(sid, "raw.webm")
    raw.write_bytes(b"giong-noi-goc")
    processed = store.path(sid, "processed.wav")
    processed.write_bytes(b"RIFF16k")
    transcript = [{"segment_id": "s1", "speaker_role": "doctor", "text_original": "chào bác"}]
    store.path(sid, "transcript.json").write_text(json.dumps(transcript, ensure_ascii=False), encoding="utf-8")
    store.update(
        sid,
        created_at=_iso(ngay_truoc),
        raw_audio_path=str(raw_path or raw),
        processed_audio_path=str(processed),
        status="ready_for_meditrace",
        meditrace_status="ready" if da_duyet else "not_sent",
    )
    if da_duyet:
        with store.path(sid, "audit.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"at": _iso(ngay_truoc), "event": "sent_to_meditrace", "turn_count": 1}) + "\n")
    return sid


@pytest.fixture()
def store(tmp_path):
    return SessionStore(tmp_path / "audio")


def test_phien_da_duyet_31_ngay_xoa_am_thanh_giu_loi_thoai(store):
    sid = _phien(store, 31, True)
    xoa = store.xoa_am_thanh_qua_han(30, bay=BAY)
    assert xoa == [sid]
    thu_muc = store.sessions_dir / sid
    assert not (thu_muc / "raw.webm").exists()
    assert not (thu_muc / "processed.wav").exists()
    # Lời thoại đã duyệt và nhật ký còn nguyên, vẫn nạp được.
    assert AudioPipeline(store).transcript(sid)[0]["text_original"] == "chào bác"
    phien = store.load(sid)
    assert phien["raw_audio_path"] is None and phien["processed_audio_path"] is None
    assert phien["audio_deleted_at"]
    su_kien = [r["event"] for r in store.read_jsonl(sid, "audit.jsonl")]
    assert "sent_to_meditrace" in su_kien and su_kien[-1] == "am_thanh_da_xoa"
    # Chạy lại không xoá/ghi nhật ký lần hai.
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == []


def test_phien_chua_duyet_31_ngay_giu_nguyen(store):
    sid = _phien(store, 31, False)
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == []
    assert (store.sessions_dir / sid / "raw.webm").exists()
    assert (store.sessions_dir / sid / "processed.wav").exists()


def test_phien_da_duyet_29_ngay_giu_nguyen(store):
    sid = _phien(store, 29, True)
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == []
    assert (store.sessions_dir / sid / "raw.webm").exists()


def test_khong_dung_toi_tep_ngoai_thu_muc_phien(store, tmp_path):
    ngoai = tmp_path / "ngoai" / "raw.webm"
    ngoai.parent.mkdir()
    ngoai.write_bytes(b"khong-duoc-xoa")
    sid = _phien(store, 31, True, raw_path=ngoai)
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == [sid]
    assert ngoai.read_bytes() == b"khong-duoc-xoa"
    # Tệp âm thanh nằm trong thư mục phiên vẫn bị xoá.
    assert not (store.sessions_dir / sid / "raw.webm").exists()


def test_mac_dinh_doc_bien_moi_truong(store, monkeypatch):
    sid = _phien(store, 10, True)
    monkeypatch.setenv("MEDITRACE_GIU_AM_THANH_NGAY", "7")
    assert store.xoa_am_thanh_qua_han(bay=BAY) == [sid]


def test_mac_dinh_30_ngay(store, monkeypatch):
    monkeypatch.delenv("MEDITRACE_GIU_AM_THANH_NGAY", raising=False)
    sid29 = _phien(store, 29, True)
    sid31 = _phien(store, 31, True)
    assert store.xoa_am_thanh_qua_han(bay=BAY) == [sid31]
    assert (store.sessions_dir / sid29 / "raw.webm").exists()


def test_tao_phien_tu_don_toi_da_mot_lan_moi_ngay(store, monkeypatch):
    monkeypatch.delenv("MEDITRACE_GIU_AM_THANH_NGAY", raising=False)
    sid = _phien(store, 31, True)  # lần create() này đã dọn trước khi phiên cũ có mặt
    store2 = SessionStore(store.root)  # dịch vụ khởi động lại
    store2.create()
    assert not (store.sessions_dir / sid / "raw.webm").exists()
    sid_b = _phien(store2, 31, True)
    store2.create()  # chưa đủ một ngày kể từ lần dọn trước → không dọn
    assert (store.sessions_dir / sid_b / "raw.webm").exists()
