"""[Âm thanh]
Làm gì   : Lưu phiên âm thanh vào đĩa tại chỗ, bền vững qua các lần chạy, kèm nhật ký sự
           kiện để kiểm toán.
Vào → Ra : mã phiên + trường cần lưu → tệp JSON của phiên và dòng nhật ký jsonl
Đọc từ   : class SessionStore lưu, nạp, cập nhật phiên và ghi nhật ký; class SessionNotFound
           khi thiếu phiên
Mục lục (các hàm/lớp chính):
  class SessionStore     Kho lưu phiên âm thanh cục bộ kèm nhật ký kiểm toán
    .xoa_am_thanh_qua_han  Xoá tệp ghi âm của phiên đã duyệt quá hạn giữ (mặc định 30 ngày)
  don_am_thanh_nen()     Luồng nền dọn hạn giữ âm thanh khi dịch vụ khởi động và mỗi 24 giờ
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
import hashlib
import secrets
import stat
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from .models import new_session, now_iso

# Hạn giữ tệp ghi âm (gốc + bản 16 kHz) sau khi lời thoại đã duyệt. Giọng nói là dữ liệu định danh.
BIEN_GIU_AM_THANH = "MEDITRACE_GIU_AM_THANH_NGAY"
GIU_AM_THANH_MAC_DINH = 30
BIEN_GIU_AM_THANH_CHUA_DUYET = "MEDITRACE_GIU_AM_THANH_CHUA_DUYET_NGAY"
GIU_AM_THANH_CHUA_DUYET_MAC_DINH = 30  # chính sách 28/11: bản chờ bác sĩ nghe kiểm giữ như bản đã duyệt
BIEN_GIU_AM_THANH_BO_DO = "MEDITRACE_GIU_AM_THANH_BO_DO_NGAY"
GIU_AM_THANH_BO_DO_MAC_DINH = 7  # phiên bỏ dở: chưa có lời thoại nào
_DUOI_AM_THANH = {".webm", ".wav", ".mp3", ".m4a", ".ogg", ".flac"}
_MOT_NGAY = 86400.0


def _doc_so_ngay_env(bien: str, mac_dinh: int) -> float:
    try:
        return float(os.environ.get(bien, mac_dinh))
    except ValueError:
        return float(mac_dinh)


def _so_ngay_giu() -> float:
    return _doc_so_ngay_env(BIEN_GIU_AM_THANH, GIU_AM_THANH_MAC_DINH)


def _so_ngay_giu_chua_duyet() -> float:
    return _doc_so_ngay_env(BIEN_GIU_AM_THANH_CHUA_DUYET, GIU_AM_THANH_CHUA_DUYET_MAC_DINH)


def _so_ngay_giu_bo_do() -> float:
    return _doc_so_ngay_env(BIEN_GIU_AM_THANH_BO_DO, GIU_AM_THANH_BO_DO_MAC_DINH)


# Phiên đang ghi/xử lý thì không bao giờ xoá âm thanh.
_TRANG_THAI_BAN = {"recording", "processing_audio", "diarizing", "transcribing"}

# Khoá theo thư mục phiên (đã resolve), dùng chung cho mọi SessionStore trong tiến trình:
# upload / process / duyệt giữ khoá; dọn hạn giữ chỉ thử lấy khoá, bận thì bỏ qua phiên.
_KHOA_CHUNG = threading.Lock()
_KHOA_PHIEN: dict[str, threading.Lock] = {}


def _khoa_cho(thu_muc: Path) -> threading.Lock:
    khoa = os.path.normcase(str(thu_muc.resolve()))
    with _KHOA_CHUNG:
        return _KHOA_PHIEN.setdefault(khoa, threading.Lock())


def _la_lien_ket(p: Path) -> bool:
    """Liên kết tượng trưng hoặc junction/điểm reparse của Windows."""
    if p.is_symlink():
        return True
    try:
        thuoc_tinh = getattr(os.lstat(p), "st_file_attributes", 0)
        return bool(thuoc_tinh & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))
    except OSError:
        return True


def _bao_loi_phien(session_id: str, exc: BaseException) -> None:
    """Ghi lỗi dọn một phiên ra stderr, đã che định danh (không in nội dung phiên)."""
    try:
        from src.he_thong.che_log import che_log
        chi_tiet = che_log(str(exc), 200)
    except Exception:
        chi_tiet = "[không ghi chi tiết]"
    print(f"[am-thanh] bo qua phien {session_id} khi don han giu: {type(exc).__name__}: {chi_tiet}",
          file=sys.stderr, flush=True)


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
    def khoa_phien(self, session_id: str) -> threading.Lock:
        """Khoá của phiên (dùng `with`); upload, process, duyệt và dọn hạn giữ dùng chung."""
        return _khoa_cho(self._dir(session_id))

    def dau_van_tay_am_thanh(self, session_id: str) -> dict[str, str]:
        """{tên tệp: sha256} của các tệp ghi âm trong thư mục phiên (raw.* và processed.wav)."""
        thu_muc = self._dir(session_id)
        ra: dict[str, str] = {}
        if not thu_muc.is_dir():
            return ra
        for tep in sorted(thu_muc.iterdir()):
            la_am_thanh = (tep.name.startswith("raw.") and tep.suffix.lower() in _DUOI_AM_THANH) \
                or tep.name == "processed.wav"
            if la_am_thanh and tep.is_file() and not tep.is_symlink():
                h = hashlib.sha256()
                with tep.open("rb") as fh:
                    for khoi in iter(lambda: fh.read(1 << 20), b""):
                        h.update(khoi)
                ra[tep.name] = h.hexdigest()
        return ra

    def ghi_duyet_am_thanh(self, session_id: str) -> dict[str, Any]:
        """Đánh dấu đã duyệt cho ĐÚNG phiên bản âm thanh hiện có. Người gọi giữ khoa_phien."""
        duyet = {"at": now_iso(), "files": self.dau_van_tay_am_thanh(session_id)}
        return self.update(session_id, meditrace_status="ready", approved_audio=duyet)

    def huy_duyet_am_thanh(self, session_id: str) -> dict[str, Any]:
        """Âm thanh hoặc lời thoại đổi (tải mới, xử lý lại) thì lần duyệt cũ hết hiệu lực."""
        return self.update(session_id, meditrace_status="not_sent", approved_audio=None, updated_at=now_iso())

    def don_dinh_ky(self) -> None:
        """Chạy xoa_am_thanh_qua_han tối đa một lần mỗi ngày cho mỗi kho; lỗi dọn không chặn việc tạo phiên."""
        bay = time.time()
        if self._lan_don_cuoi is not None and bay - self._lan_don_cuoi < _MOT_NGAY:
            return
        self._lan_don_cuoi = bay
        try:
            self.xoa_am_thanh_qua_han(bay=bay)
        except Exception as exc:
            _bao_loi_phien("*", exc)

    def xoa_am_thanh_qua_han(
        self,
        so_ngay: float | None = None,
        bay: float | None = None,
        so_ngay_chua_duyet: float | None = None,
        so_ngay_bo_do: float | None = None,
    ) -> list[str]:
        """Xoá tệp ghi âm gốc và bản WAV 16 kHz của phiên quá hạn:
        - Đã duyệt (meditrace_status == "ready"): quá ``so_ngay`` ngày (mặc định 30) kể từ lúc duyệt,
          chỉ xoá khi có ``approved_audio`` và dấu vân tay âm thanh hiện tại trùng bản đã duyệt.
        - Chưa duyệt, đã có lời thoại: quá ``so_ngay_chua_duyet`` ngày (mặc định 30) tính từ
          ``updated_at`` (fallback ``created_at``), ghi log với ``status="chua_duyet"``.
        - Bỏ dở (chưa duyệt, transcript.json thiếu hoặc rỗng): quá ``so_ngay_bo_do`` ngày
          (mặc định 7), ghi log với ``status="bo_do"``.

        Luôn bỏ qua liên kết/junction, phiên đang bận hoặc đang giữ khoá; chỉ xoá tệp nằm trong
        thư mục phiên; giữ session.json, transcript.json, audit.jsonl. Trả về mã phiên vừa xoá."""
        if so_ngay is None:
            so_ngay = _so_ngay_giu()
        if so_ngay_chua_duyet is None:
            so_ngay_chua_duyet = _so_ngay_giu_chua_duyet()
        if so_ngay_bo_do is None:
            so_ngay_bo_do = _so_ngay_giu_bo_do()
        bay = time.time() if bay is None else bay
        han_da_duyet = bay - float(so_ngay) * _MOT_NGAY
        han_chua_duyet = bay - float(so_ngay_chua_duyet) * _MOT_NGAY
        han_bo_do = bay - float(so_ngay_bo_do) * _MOT_NGAY
        goc_kho = self.sessions_dir.resolve()
        da_xoa: list[str] = []
        for thu_muc in sorted(self.sessions_dir.iterdir()):
            sid = thu_muc.name
            if not re.fullmatch(r"session_[A-Za-z0-9_-]+", sid):
                continue
            try:
                if _la_lien_ket(thu_muc) or not thu_muc.is_dir():
                    continue
                goc = thu_muc.resolve()
                if goc.parent != goc_kho:
                    continue
                khoa = _khoa_cho(thu_muc)
                if not khoa.acquire(blocking=False):
                    continue  # đang tải lên / xử lý / duyệt
                try:
                    if self._xoa_mot_phien(
                        sid, goc, han_da_duyet, so_ngay, han_chua_duyet, so_ngay_chua_duyet, han_bo_do, so_ngay_bo_do
                    ):
                        da_xoa.append(sid)
                finally:
                    khoa.release()
            except Exception as exc:
                _bao_loi_phien(sid, exc)
        return da_xoa

    def _xoa_mot_phien(
        self,
        sid: str,
        goc: Path,
        han_da_duyet: float,
        so_ngay: float,
        han_chua_duyet: float,
        so_ngay_chua_duyet: float,
        han_bo_do: float,
        so_ngay_bo_do: float,
    ) -> bool:
        phien = self.load(sid)
        if phien.get("status") in _TRANG_THAI_BAN:
            return False
        da_duyet = phien.get("meditrace_status") == "ready"
        if da_duyet:
            duyet = phien.get("approved_audio")
            if not isinstance(duyet, dict) or not duyet.get("files"):
                return False
            moc = _giay(duyet.get("at"))
            if moc is None or moc > han_da_duyet:
                return False
            if self.dau_van_tay_am_thanh(sid) != duyet["files"]:
                return False  # âm thanh hiện tại không phải bản đã duyệt
            ung_vien = {(goc / ten).resolve() for ten in duyet["files"]}
            han_ngay = so_ngay
        else:
            moc = _giay(phien.get("updated_at"))
            moc = moc if moc is not None else _giay(phien.get("created_at"))
            bo_do = not self._co_loi_thoai(goc)
            han, han_ngay = (han_bo_do, so_ngay_bo_do) if bo_do else (han_chua_duyet, so_ngay_chua_duyet)
            if moc is None or moc > han:
                return False
            ung_vien = set()
            for khoa in ("raw_audio_path", "processed_audio_path"):
                if phien.get(khoa):
                    ung_vien.add(Path(phien[khoa]).resolve())
            ung_vien.update(p.resolve() for p in goc.glob("raw.*") if p.suffix.lower() in _DUOI_AM_THANH)
            ung_vien.add((goc / "processed.wav").resolve())

        tep_xoa: list[str] = []
        for tep in sorted(ung_vien):
            if tep.parent != goc or not tep.is_file():
                continue  # không bao giờ đụng tệp ngoài thư mục phiên
            tep.unlink()
            tep_xoa.append(tep.name)
        if not tep_xoa:
            return False
        self.update(sid, raw_audio_path=None, processed_audio_path=None, audio_deleted_at=now_iso())
        if da_duyet:
            self.log(sid, "am_thanh_da_xoa", files=tep_xoa, retention_days=han_ngay)
        else:
            self.log(
                sid, "am_thanh_da_xoa", files=tep_xoa, retention_days=han_ngay,
                status="bo_do" if bo_do else "chua_duyet",
            )
        return True

    @staticmethod
    def _co_loi_thoai(goc: Path) -> bool:
        """Phiên có lời thoại khi transcript.json đọc được và không rỗng. Lỗi đọc → coi như CÓ
        (giữ lâu hơn là an toàn hơn so với xoá nhầm căn cứ bác sĩ cần nghe lại)."""
        tep = goc / "transcript.json"
        if not tep.is_file():
            return False
        try:
            return bool(json.loads(tep.read_text(encoding="utf-8")))
        except Exception:
            return True


# ═══ don_am_thanh_nen() — Dọn hạn giữ âm thanh ở luồng nền khi dịch vụ khởi động ══════
# Chạy ngay một lượt, rồi mỗi 24 giờ một lượt khi dịch vụ còn chạy. Không bao giờ ném lỗi.
def don_am_thanh_nen(root: str | Path, lap_lai: bool = True) -> threading.Thread:
    def _chay() -> None:
        while True:
            try:
                SessionStore(root).xoa_am_thanh_qua_han()
            except Exception as exc:
                _bao_loi_phien("*", exc)
            if not lap_lai:
                return
            time.sleep(_MOT_NGAY)

    luong = threading.Thread(target=_chay, name="don-am-thanh-qua-han", daemon=True)
    luong.start()
    return luong
