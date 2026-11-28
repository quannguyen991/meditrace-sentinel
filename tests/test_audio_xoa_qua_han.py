"""Hạn giữ âm thanh: phiên quá hạn (30 ngày sau duyệt, 7 ngày nếu chưa duyệt) thì xoá tệp ghi âm, giữ lời thoại và nhật ký.

Duyệt gắn với PHIÊN BẢN âm thanh (dấu vân tay tệp lúc duyệt): tải âm thanh mới, xử lý lại,
phiên đang bận hay đang bị khoá thì không xoá.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.audio.pipeline import AudioPipeline
from src.audio.storage import SessionStore

BAY = time.time()
NGAY = 86400.0


def _iso(ngay_truoc: float) -> str:
    t = datetime.fromtimestamp(BAY, timezone.utc) - timedelta(days=ngay_truoc)
    return t.isoformat().replace("+00:00", "Z")


def _lui_duyet(store: SessionStore, sid: str, ngay_truoc: float) -> None:
    phien = store.load(sid)
    phien["approved_audio"]["at"] = _iso(ngay_truoc)
    store.save(phien)


def _phien(
    store: SessionStore,
    ngay_truoc: float,
    da_duyet: bool,
    raw_path: Path | None = None,
    updated_at_ngay_truoc: float | None = None,
    co_loi_thoai: bool = True,
) -> str:
    """Phiên có raw.webm + processed.wav + transcript hợp lệ; da_duyet → duyệt qua pipeline thật."""
    sid = store.create()["session_id"]
    raw = store.path(sid, "raw.webm")
    raw.write_bytes(b"giong-noi-goc")
    processed = store.path(sid, "processed.wav")
    processed.write_bytes(b"RIFF16k")
    if co_loi_thoai:
        transcript = [{"segment_id": "s1", "speaker_id": "speaker_1", "speaker_role": "doctor", "text_original": "chào bác"}]
        store.path(sid, "transcript.json").write_text(json.dumps(transcript, ensure_ascii=False), encoding="utf-8")
    cap_nhat = {
        "created_at": _iso(ngay_truoc),
        "raw_audio_path": str(raw_path or raw),
        "processed_audio_path": str(processed),
        "status": "ready_for_meditrace",
    }
    if updated_at_ngay_truoc is not None:
        cap_nhat["updated_at"] = _iso(updated_at_ngay_truoc)
    store.update(sid, **cap_nhat)
    if da_duyet:
        AudioPipeline(store).meditrace_input(sid)
        _lui_duyet(store, sid, ngay_truoc)
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
    assert AudioPipeline(store).transcript(sid)[0]["text_original"] == "chào bác"
    phien = store.load(sid)
    assert phien["raw_audio_path"] is None and phien["processed_audio_path"] is None
    assert phien["audio_deleted_at"]
    su_kien = [r["event"] for r in store.read_jsonl(sid, "audit.jsonl")]
    assert "sent_to_meditrace" in su_kien and su_kien[-1] == "am_thanh_da_xoa"
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == []


def test_duyet_ghi_dau_van_tay_phien_ban_am_thanh(store):
    sid = _phien(store, 0, True)
    duyet = store.load(sid)["approved_audio"]
    assert duyet["at"] and set(duyet["files"]) == {"raw.webm", "processed.wav"}


def test_phien_chua_duyet_3_ngay_giu_nguyen(store):
    sid = _phien(store, 3, False, updated_at_ngay_truoc=3)
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == []
    assert (store.sessions_dir / sid / "raw.webm").exists()
    assert (store.sessions_dir / sid / "processed.wav").exists()


def test_phien_chua_duyet_co_loi_thoai_8_ngay_van_giu(store):
    # Chính sách 28/11: âm thanh chưa duyệt là căn cứ để bác sĩ nghe kiểm, giữ 30 ngày như bản đã duyệt
    sid = _phien(store, 8, False, updated_at_ngay_truoc=8)
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == []
    assert (store.sessions_dir / sid / "raw.webm").exists()


def test_phien_chua_duyet_co_loi_thoai_31_ngay_xoa_am_thanh_giu_nhat_ky(store):
    sid = _phien(store, 31, False, updated_at_ngay_truoc=31)
    xoa = store.xoa_am_thanh_qua_han(30, bay=BAY)
    assert xoa == [sid]
    thu_muc = store.sessions_dir / sid
    assert not (thu_muc / "raw.webm").exists()
    assert not (thu_muc / "processed.wav").exists()
    assert (thu_muc / "session.json").exists()
    assert (thu_muc / "audit.jsonl").exists()
    phien = store.load(sid)
    assert phien["raw_audio_path"] is None and phien["processed_audio_path"] is None
    assert phien["audio_deleted_at"]
    nhat_ky = store.read_jsonl(sid, "audit.jsonl")
    assert nhat_ky[-1]["event"] == "am_thanh_da_xoa"
    assert nhat_ky[-1]["status"] == "chua_duyet"
    assert nhat_ky[-1]["retention_days"] == 30
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == []


def test_phien_bo_do_khong_loi_thoai_8_ngay_xoa(store):
    sid = _phien(store, 8, False, updated_at_ngay_truoc=8, co_loi_thoai=False)
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == [sid]
    nhat_ky = store.read_jsonl(sid, "audit.jsonl")
    assert nhat_ky[-1]["status"] == "bo_do" and nhat_ky[-1]["retention_days"] == 7


def test_phien_bo_do_khong_loi_thoai_6_ngay_giu(store):
    sid = _phien(store, 6, False, updated_at_ngay_truoc=6, co_loi_thoai=False)
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == []
    assert (store.sessions_dir / sid / "raw.webm").exists()


def test_phien_chua_duyet_fallback_created_at_khi_khong_co_updated_at(store):
    sid = _phien(store, 31, False, updated_at_ngay_truoc=None)
    assert store.xoa_am_thanh_qua_han(bay=BAY) == [sid]
    nhat_ky = store.read_jsonl(sid, "audit.jsonl")
    assert nhat_ky[-1]["event"] == "am_thanh_da_xoa"
    assert nhat_ky[-1]["status"] == "chua_duyet"


def test_phien_da_duyet_29_ngay_giu_nguyen(store):
    sid = _phien(store, 29, True)
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == []
    assert (store.sessions_dir / sid / "raw.webm").exists()


def test_duyet_kieu_cu_khong_co_phien_ban_thi_giu(store):
    sid = _phien(store, 31, False)
    store.update(sid, meditrace_status="ready")
    store.log(sid, "sent_to_meditrace", turn_count=1)
    assert store.xoa_am_thanh_qua_han(30, bay=BAY + 31 * NGAY) == []
    assert (store.sessions_dir / sid / "raw.webm").exists()


def test_tai_am_thanh_moi_sau_duyet_thi_khong_xoa(store):
    sid = _phien(store, 31, True)
    AudioPipeline(store).upload(sid, b"ghi-am-moi-chua-duyet", "raw.webm")
    assert store.load(sid)["meditrace_status"] == "not_sent"
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == []
    assert (store.sessions_dir / sid / "raw.webm").read_bytes() == b"ghi-am-moi-chua-duyet"


def test_tep_doi_ma_van_con_co_duyet_thi_khong_xoa(store):
    sid = _phien(store, 31, True)
    (store.sessions_dir / sid / "processed.wav").write_bytes(b"RIFF-ban-xu-ly-lai")
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == []
    assert (store.sessions_dir / sid / "raw.webm").exists()


def test_phien_dang_xu_ly_thi_bo_qua(store):
    sid = _phien(store, 31, True)
    store.update(sid, status="transcribing")
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == []
    assert (store.sessions_dir / sid / "raw.webm").exists()


def test_phien_dang_bi_khoa_thi_bo_qua(store):
    sid = _phien(store, 31, True)
    with store.khoa_phien(sid):
        assert SessionStore(store.root).xoa_am_thanh_qua_han(30, bay=BAY) == []
    assert (store.sessions_dir / sid / "raw.webm").exists()
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == [sid]


def test_mot_phien_hong_khong_chan_ca_luot(store, capsys):
    hong = store.sessions_dir / "session_hong"
    hong.mkdir()
    (hong / "session.json").write_text("{khong phai json", encoding="utf-8")
    sid = _phien(store, 31, True)
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == [sid]
    assert "session_hong" in capsys.readouterr().err


def test_khong_dung_toi_tep_ngoai_thu_muc_phien(store, tmp_path):
    ngoai = tmp_path / "ngoai" / "raw.webm"
    ngoai.parent.mkdir()
    ngoai.write_bytes(b"khong-duoc-xoa")
    sid = _phien(store, 31, True, raw_path=ngoai)
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == [sid]
    assert ngoai.read_bytes() == b"khong-duoc-xoa"
    assert not (store.sessions_dir / sid / "raw.webm").exists()


def test_thu_muc_phien_la_lien_ket_tuong_trung_thi_bo_qua(store, tmp_path):
    that = _phien(SessionStore(tmp_path / "kho-khac"), 31, True)
    goc_that = tmp_path / "kho-khac" / "sessions" / that
    lien_ket = store.sessions_dir / that
    try:
        os.symlink(goc_that, lien_ket, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("hệ điều hành không cho tạo liên kết tượng trưng")
    assert store.xoa_am_thanh_qua_han(30, bay=BAY) == []
    assert (goc_that / "raw.webm").exists()


def test_mac_dinh_doc_bien_moi_truong(store, monkeypatch):
    sid = _phien(store, 10, True)
    sid_chua_duyet = _phien(store, 5, False, updated_at_ngay_truoc=5)
    monkeypatch.setenv("MEDITRACE_GIU_AM_THANH_NGAY", "7")
    monkeypatch.setenv("MEDITRACE_GIU_AM_THANH_CHUA_DUYET_NGAY", "4")
    assert sorted(store.xoa_am_thanh_qua_han(bay=BAY)) == sorted([sid, sid_chua_duyet])


def test_bien_moi_truong_chua_duyet_loi_thi_fallback_30_ngay(store, monkeypatch):
    monkeypatch.setenv("MEDITRACE_GIU_AM_THANH_CHUA_DUYET_NGAY", "khong-phai-so")
    sid_8 = _phien(store, 8, False, updated_at_ngay_truoc=8)
    sid_31 = _phien(store, 31, False, updated_at_ngay_truoc=31)
    assert store.xoa_am_thanh_qua_han(bay=BAY) == [sid_31]
    assert (store.sessions_dir / sid_8 / "raw.webm").exists()


def test_mac_dinh_30_ngay(store, monkeypatch):
    monkeypatch.delenv("MEDITRACE_GIU_AM_THANH_NGAY", raising=False)
    sid29 = _phien(store, 29, True)
    sid31 = _phien(store, 31, True)
    assert store.xoa_am_thanh_qua_han(bay=BAY) == [sid31]
    assert (store.sessions_dir / sid29 / "raw.webm").exists()


def test_tao_phien_tu_don_toi_da_mot_lan_moi_ngay(store, monkeypatch):
    monkeypatch.delenv("MEDITRACE_GIU_AM_THANH_NGAY", raising=False)
    sid = _phien(store, 31, True)
    store2 = SessionStore(store.root)
    store2.create()
    assert not (store.sessions_dir / sid / "raw.webm").exists()
    sid_b = _phien(store2, 31, True)
    store2.create()
    assert (store.sessions_dir / sid_b / "raw.webm").exists()


def test_don_nen_khi_khoi_dong_dich_vu(tmp_path, monkeypatch):
    from src.audio.storage import don_am_thanh_nen

    monkeypatch.delenv("MEDITRACE_GIU_AM_THANH_NGAY", raising=False)
    store = SessionStore(tmp_path / "audio")
    sid = _phien(store, 31, True)
    luong = don_am_thanh_nen(tmp_path / "audio", lap_lai=False)
    luong.join(10)
    assert not (store.sessions_dir / sid / "raw.webm").exists()


def test_am_thanh_pipeline_tu_don_am_thanh_qua_han(tmp_path, monkeypatch):
    from src.he_thong import dich_vu_http

    monkeypatch.delenv("MEDITRACE_GIU_AM_THANH_NGAY", raising=False)
    monkeypatch.delenv("MEDITRACE_GIU_AM_THANH_CHUA_DUYET_NGAY", raising=False)
    monkeypatch.delenv("MEDITRACE_GIU_AM_THANH_BO_DO_NGAY", raising=False)
    thu_muc_phien = tmp_path / "phien-dich-vu"
    store = SessionStore(thu_muc_phien)
    sid_da_duyet_cu = _phien(store, 31, True)
    sid_chua_duyet_cu = _phien(store, 31, False, updated_at_ngay_truoc=31)
    sid_bo_do_cu = _phien(store, 8, False, updated_at_ngay_truoc=8, co_loi_thoai=False)
    sid_cho_duyet_8 = _phien(store, 8, False, updated_at_ngay_truoc=8)
    sid_chua_duyet_moi = _phien(store, 2, False, updated_at_ngay_truoc=2)

    monkeypatch.setattr(dich_vu_http, "THU_MUC_PHIEN", thu_muc_phien)
    pipe = dich_vu_http.AmThanh().pipeline()
    assert pipe.store.root == thu_muc_phien
    assert not (store.sessions_dir / sid_da_duyet_cu / "raw.webm").exists()
    assert not (store.sessions_dir / sid_chua_duyet_cu / "raw.webm").exists()
    assert not (store.sessions_dir / sid_chua_duyet_cu / "processed.wav").exists()
    assert (store.sessions_dir / sid_chua_duyet_moi / "raw.webm").exists()
    assert not (store.sessions_dir / sid_bo_do_cu / "raw.webm").exists()
    assert (store.sessions_dir / sid_cho_duyet_8 / "raw.webm").exists()
