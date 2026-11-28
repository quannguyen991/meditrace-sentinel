"""[Âm thanh]
Làm gì   : Lưu phiên âm thanh vào đĩa tại chỗ, bền vững qua các lần chạy, kèm nhật ký sự
           kiện để kiểm toán.
Vào → Ra : mã phiên + trường cần lưu → tệp JSON của phiên và dòng nhật ký jsonl
Đọc từ   : class SessionStore lưu, nạp, cập nhật phiên và ghi nhật ký; class SessionNotFound
           khi thiếu phiên
Mục lục (các hàm/lớp chính):
  class SessionStore     Kho lưu phiên âm thanh cục bộ kèm nhật ký kiểm toán
    .xoa_am_thanh_qua_han  Xoá tệp ghi âm của phiên đã duyệt quá hạn giữ (mặc định 30 ngày)
  class SessionNotFound  Lỗi không tìm thấy phiên âm thanh
Gọi tới  : audio/models
Dùng bởi : audio/api, audio/pipeline, he_thong/dich_vu_http
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Lưu trữ phiên cục bộ, bền vững, kèm nhật ký kiểm toán."""

from __future__ import annotations

import json
import os
import re
import secrets
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from .models import new_session, now_iso

# Hạn giữ tệp ghi âm (gốc + bản 16 kHz) sau khi lời thoại đã duyệt. Giọng nói là dữ liệu định danh.
BIEN_GIU_AM_THANH = "MEDITRACE_GIU_AM_THANH_NGAY"
GIU_AM_THANH_MAC_DINH = 30
_DUOI_AM_THANH = {".webm", ".wav", ".mp3", ".m4a", ".ogg", ".flac"}
_MOT_NGAY = 86400.0


def _so_ngay_giu() -> float:
    try:
        return float(os.environ.get(BIEN_GIU_AM_THANH, GIU_AM_THANH_MAC_DINH))
    except ValueError:
        return float(GIU_AM_THANH_MAC_DINH)


def _giay(iso: Any) -> float | None:
    try:
        return datetime.fromisoformat(str(iso).replace("Z", "+00:00")).timestamp()
    except (TypeError, ValueError):
        return None


# ═══ class SessionNotFound — Lỗi không tìm thấy phiên âm thanh ════════════════════════
class SessionNotFound(KeyError):
    pass


# ═══ class SessionStore — Kho lưu phiên âm thanh cục bộ kèm nhật ký kiểm toán ═════════
# Mỗi phiên một thư mục với session.json và audit.jsonl; ghi tệp qua tệp tạm để tránh
# hỏng.
class SessionStore:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.sessions_dir = self.root / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self._lan_don_cuoi: float | None = None

    def _dir(self, session_id: str) -> Path:
        if not re.fullmatch(r"session_[A-Za-z0-9_-]+", session_id):
            raise ValueError("invalid session id")
        return self.sessions_dir / session_id

    def _json(self, session_id: str) -> Path:
        return self._dir(session_id) / "session.json"

    def create(self) -> dict[str, Any]:
        self.don_dinh_ky()
        stamp = re.sub(r"[^A-Za-z0-9]", "", now_iso())
        session_id = f"session_{stamp}_{secrets.token_hex(2)}"
        folder = self._dir(session_id)
        folder.mkdir(parents=True)
        value = new_session(session_id)
        self.save(value)
        self.log(session_id, "session_created")
        return value

    def load(self, session_id: str) -> dict[str, Any]:
        path = self._json(session_id)
        if not path.exists():
            raise SessionNotFound(session_id)
        return json.loads(path.read_text(encoding="utf-8"))

    def save(self, value: dict[str, Any]) -> None:
        path = self._json(value["session_id"])
        tmp = path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, path)

    def update(self, session_id: str, **changes: Any) -> dict[str, Any]:
        value = self.load(session_id)
        value.update(changes)
        self.save(value)
        return value

    def path(self, session_id: str, name: str) -> Path:
        folder = self._dir(session_id)
        folder.mkdir(parents=True, exist_ok=True)
        return folder / name

    def log(self, session_id: str, event: str, **metadata: Any) -> None:
        record = {"at": now_iso(), "event": event, **metadata}
        with self.path(session_id, "audit.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

    def read_jsonl(self, session_id: str, name: str) -> list[dict[str, Any]]:
        path = self.path(session_id, name)
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    # ─── Hạn giữ âm thanh ──────────────────────────────────────────────────────────────
    def don_dinh_ky(self) -> None:
        """Chạy xoa_am_thanh_qua_han tối đa một lần mỗi ngày cho mỗi kho; lỗi dọn không chặn việc tạo phiên."""
        bay = time.time()
        if self._lan_don_cuoi is not None and bay - self._lan_don_cuoi < _MOT_NGAY:
            return
        self._lan_don_cuoi = bay
        try:
            self.xoa_am_thanh_qua_han(bay=bay)
        except Exception:
            pass

    def xoa_am_thanh_qua_han(self, so_ngay: float | None = None, bay: float | None = None) -> list[str]:
        """Xoá tệp ghi âm gốc và bản WAV 16 kHz của các phiên đã duyệt (meditrace_status == "ready",
        tức đã qua chặn cứng và gửi sang lõi — sự kiện ``sent_to_meditrace``) cũ hơn ``so_ngay`` ngày,
        tính từ lần duyệt cuối (không có thì từ created_at). Giữ session.json, transcript.json và
        audit.jsonl; ghi sự kiện ``am_thanh_da_xoa``. Chỉ xoá tệp nằm trong thư mục của phiên.
        Trả về mã các phiên vừa xoá âm thanh."""
        if so_ngay is None:
            so_ngay = _so_ngay_giu()
        bay = time.time() if bay is None else bay
        han = bay - float(so_ngay) * _MOT_NGAY
        da_xoa: list[str] = []
        for thu_muc in sorted(self.sessions_dir.iterdir()):
            sid = thu_muc.name
            if not thu_muc.is_dir() or not re.fullmatch(r"session_[A-Za-z0-9_-]+", sid):
                continue
            try:
                phien = self.load(sid)
            except (SessionNotFound, ValueError):
                continue
            if phien.get("meditrace_status") != "ready":
                continue
            duyet = [r.get("at") for r in self.read_jsonl(sid, "audit.jsonl") if r.get("event") == "sent_to_meditrace"]
            moc = _giay(duyet[-1]) if duyet else None
            moc = moc if moc is not None else _giay(phien.get("created_at"))
            if moc is None or moc > han:
                continue
            goc = thu_muc.resolve()
            ung_vien: set[Path] = set()
            for khoa in ("raw_audio_path", "processed_audio_path"):
                if phien.get(khoa):
                    ung_vien.add(Path(phien[khoa]).resolve())
            ung_vien.update(p.resolve() for p in thu_muc.glob("raw.*") if p.suffix.lower() in _DUOI_AM_THANH)
            ung_vien.add((thu_muc / "processed.wav").resolve())
            tep_xoa: list[str] = []
            for tep in sorted(ung_vien):
                if tep.parent != goc or not tep.is_file():
                    continue  # không bao giờ đụng tệp ngoài thư mục phiên
                tep.unlink()
                tep_xoa.append(tep.name)
            if not tep_xoa:
                continue
            self.update(sid, raw_audio_path=None, processed_audio_path=None, audio_deleted_at=now_iso())
            self.log(sid, "am_thanh_da_xoa", files=tep_xoa, retention_days=so_ngay)
            da_xoa.append(sid)
        return da_xoa
