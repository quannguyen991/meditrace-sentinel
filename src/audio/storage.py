"""[Âm thanh]
Làm gì   : Lưu phiên âm thanh vào đĩa tại chỗ, bền vững qua các lần chạy, kèm nhật ký sự
           kiện để kiểm toán.
Vào → Ra : mã phiên + trường cần lưu → tệp JSON của phiên và dòng nhật ký jsonl
Đọc từ   : class SessionStore lưu, nạp, cập nhật phiên và ghi nhật ký; class SessionNotFound
           khi thiếu phiên
Mục lục (các hàm/lớp chính):
  class SessionStore     Kho lưu phiên âm thanh cục bộ kèm nhật ký kiểm toán
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
from pathlib import Path
from typing import Any, Iterable

from .models import new_session, now_iso


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

    def _dir(self, session_id: str) -> Path:
        if not re.fullmatch(r"session_[A-Za-z0-9_-]+", session_id):
            raise ValueError("invalid session id")
        return self.sessions_dir / session_id

    def _json(self, session_id: str) -> Path:
        return self._dir(session_id) / "session.json"

    def create(self) -> dict[str, Any]:
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
