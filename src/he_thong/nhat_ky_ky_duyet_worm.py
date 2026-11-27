# -*- coding: utf-8 -*-
"""[Dịch vụ, an toàn và minh bạch › An toàn]
Làm gì   : Ghi nhật ký ký duyệt chỉ thêm, không sửa xoá, nối các dòng bằng chuỗi băm SHA-256
           để phát hiện can thiệp.
Vào → Ra : sự kiện ký duyệt (người, nội dung) → dòng mới trong cơ sở dữ liệu có băm nối
           chuỗi; kiểm chuỗi trả đúng hoặc sai
Đọc từ   : class WormAuditLogger ghi và kiểm chuỗi; init_worm_db() tạo cơ sở dữ liệu
Mục lục (các hàm/lớp chính):
  class WormAuditLogger  Bộ ghi nhật ký chỉ-ghi-thêm (WORM) có chuỗi băm
  init_worm_db()         Khởi tạo cơ sở dữ liệu WORM kèm bẫy chặn sửa xoá
  _tinh_curr_hash()      Tính băm nối chuỗi của một bản ghi
Dùng bởi : he_thong/dich_vu_http
Tên cũ   : worm_audit_log.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Sổ nhật ký kiểm toán bất biến WORM (Write Once Read Many) với SHA-256 Hash Chaining.
Tuân thủ Thông tư 46/2018/TT-BYT (Quy định hồ sơ bệnh án điện tử) và Nghị định 13/2023/NĐ-CP (Bảo vệ dữ liệu cá nhân).
"""
import hashlib
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

GENESIS_HASH = hashlib.sha256("MEDITRACE_SENTINEL_GENESIS_CIRCULAR_46_2018_TT_BYT".encode("utf-8")).hexdigest()
DEFAULT_DB_PATH = Path("data/audit_log_worm.db")


# ═══ init_worm_db() — Khởi tạo cơ sở dữ liệu WORM kèm bẫy chặn sửa xoá ════════════════
# SQLite chế độ WAL; trigger cấm UPDATE và DELETE trên bảng nhật ký.
def init_worm_db(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Khởi tạo SQLite WAL database với bảng WORM và các triggers ngăn sửa/xóa tuyệt đối."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA busy_timeout = 5000;")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS audit_log_worm (
        seq INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user_id TEXT NOT NULL,
        action TEXT NOT NULL,
        case_id TEXT NOT NULL,
        payload_hash TEXT NOT NULL,
        prev_hash TEXT NOT NULL,
        curr_hash TEXT NOT NULL,
        details TEXT
    );
    """)

    # Triggers ngăn chặn sửa/xóa tuyệt đối (WORM Immutable Enforcement)
    conn.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_audit_worm_prevent_update
    BEFORE UPDATE ON audit_log_worm
    BEGIN
        SELECT RAISE(FAIL, 'WORM Violation: Audit log entries are strictly immutable under Circular 46/2018/TT-BYT.');
    END;
    """)

    conn.execute("""
    CREATE TRIGGER IF NOT EXISTS trg_audit_worm_prevent_delete
    BEFORE DELETE ON audit_log_worm
    BEGIN
        SELECT RAISE(FAIL, 'WORM Violation: Audit log entries cannot be deleted under Circular 46/2018/TT-BYT.');
    END;
    """)

    conn.commit()
    return conn


# ─── _tinh_payload_hash() — Băm SHA-256 nội dung sự kiện ──────────────────────────────
# Nội dung được chuẩn hoá JSON trước khi băm.
def _tinh_payload_hash(payload: Any) -> str:
    """Tính SHA-256 của payload dưới dạng JSON chuẩn hóa."""
    chuoi = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(chuoi.encode("utf-8")).hexdigest()


# ─── _tinh_curr_hash() — Tính băm nối chuỗi của một bản ghi ───────────────────────────
# Băm số thứ tự, thời gian, người, hành động, ca, nội dung và băm trước đó.
def _tinh_curr_hash(seq: int, timestamp: str, user_id: str, action: str,
                    case_id: str, payload_hash: str, prev_hash: str) -> str:
    """Tính chuỗi hàm băm liên hoàn: Hash_k = SHA-256(seq || timestamp || user || action || case || payload || Hash_{k-1})."""
    du_lieu = f"{seq}|{timestamp}|{user_id}|{action}|{case_id}|{payload_hash}|{prev_hash}"
    return hashlib.sha256(du_lieu.encode("utf-8")).hexdigest()


# ═══ class WormAuditLogger — Bộ ghi nhật ký chỉ-ghi-thêm (WORM) có chuỗi băm ══════════
# Ghi sự kiện, kiểm chuỗi, xuất chứng nhận; neo băm ra tệp ngoài chống cắt đuôi.
class WormAuditLogger:
    """Trình ghi nhật ký kiểm toán bất biến chuỗi băm WORM kèm neo hash ngoài (external anchor) chống cắt đuôi."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH, anchor_path: Optional[Path] = None):
        self.db_path = db_path
        self.anchor_path = anchor_path or db_path.with_suffix(".anchor.json")
        self._lock = threading.Lock()
        self.conn = init_worm_db(db_path)

    def _ghi_neo_ngoai(self, seq: int, curr_hash: str) -> None:
        """Ghi neo hash mới nhất ra tệp tách biệt để phát hiện hành vi DROP TRIGGER + cắt đuôi chuỗi."""
        self.anchor_path.parent.mkdir(parents=True, exist_ok=True)
        neo = {
            "genesis_hash": GENESIS_HASH,
            "latest_seq": seq,
            "latest_hash": curr_hash,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.anchor_path.write_text(json.dumps(neo, ensure_ascii=False, indent=2), encoding="utf-8")

    def append_event(self, user_id: str, action: str, case_id: str,
                     payload: Any, details: str = "") -> Dict[str, Any]:
        """Ghi một sự kiện kiểm toán mới vào chuỗi WORM với băm liên hoàn và cập nhật neo ngoài (thread-safe)."""
        with self._lock:
            self.conn.execute("BEGIN IMMEDIATE;")
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT seq, curr_hash FROM audit_log_worm ORDER BY seq DESC LIMIT 1;")
                row = cursor.fetchone()

                if row is None:
                    seq = 1
                    prev_hash = GENESIS_HASH
                else:
                    seq = row[0] + 1
                    prev_hash = row[1]

                timestamp = datetime.now(timezone.utc).isoformat()
                payload_hash = _tinh_payload_hash(payload)
                curr_hash = _tinh_curr_hash(seq, timestamp, user_id, action, case_id, payload_hash, prev_hash)

                cursor.execute("""
                INSERT INTO audit_log_worm (seq, timestamp, user_id, action, case_id, payload_hash, prev_hash, curr_hash, details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (seq, timestamp, user_id, action, case_id, payload_hash, prev_hash, curr_hash, details))
                self.conn.commit()
                self._ghi_neo_ngoai(seq, curr_hash)
            except Exception:
                try:
                    self.conn.rollback()
                except Exception:
                    pass
                raise

        return {
            "seq": seq,
            "timestamp": timestamp,
            "user_id": user_id,
            "action": action,
            "case_id": case_id,
            "payload_hash": payload_hash,
            "prev_hash": prev_hash,
            "curr_hash": curr_hash,
            "details": details,
        }

    def verify_chain(self) -> Tuple[bool, int, str]:
        """Thẩm tra toàn vẹn toàn bộ chuỗi băm WORM từ Genesis Hash đến bản ghi mới nhất và đối chiếu neo ngoài.
        -> (hợp_lệ: bool, tổng_số_bản_ghi: int, thông_điệp: str)
        """
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT seq, timestamp, user_id, action, case_id, payload_hash, prev_hash, curr_hash FROM audit_log_worm ORDER BY seq ASC;")
            rows = cursor.fetchall()

            if not rows:
                if self.anchor_path.exists():
                    neo = json.loads(self.anchor_path.read_text(encoding="utf-8"))
                    if neo.get("latest_seq", 0) > 0:
                        return False, 0, "Phát hiện xóa trắng bảng WORM so với neo kiểm toán ngoài (External Anchor mismatch)!"
                return True, 0, "Chuỗi rỗng, hợp lệ."

            expected_prev_hash = GENESIS_HASH
            for r in rows:
                seq, ts, user_id, action, case_id, payload_hash, prev_hash, curr_hash = r
                if prev_hash != expected_prev_hash:
                    return False, seq, f"Phát hiện đứt gãy chuỗi băm tại bản ghi seq={seq}! Prev_hash không khớp."

                recomputed_hash = _tinh_curr_hash(seq, ts, user_id, action, case_id, payload_hash, prev_hash)
                if curr_hash != recomputed_hash:
                    return False, seq, f"Phát hiện giả mạo dữ liệu tại seq={seq}! Curr_hash không khớp với phép tính băm."

                expected_prev_hash = curr_hash

            if self.anchor_path.exists():
                neo = json.loads(self.anchor_path.read_text(encoding="utf-8"))
                if rows[-1][0] != neo.get("latest_seq") or rows[-1][7] != neo.get("latest_hash"):
                    return (
                        False,
                        len(rows),
                        f"Phát hiện cắt đuôi hoặc giả mạo chuỗi WORM so với neo ngoài (DB seq={rows[-1][0]}, Anchor seq={neo.get('latest_seq')})!",
                    )

            return True, len(rows), f"Xác nhận chuỗi WORM gồm {len(rows)} bản ghi hợp lệ 100%, khớp neo ngoài, bảo đảm tính toàn vẹn pháp lý Thông tư 46/2018/TT-BYT."

    def close(self):
        """Đóng kết nối SQLite để giải phóng file lock."""
        with self._lock:
            if hasattr(self, "conn") and self.conn:
                self.conn.close()
                self.conn = None

    def export_inspection_certificate(self) -> Dict[str, Any]:
        """Xuất chứng chỉ kiểm định chuỗi kiểm toán phục vụ thanh kiểm tra Bộ Y tế."""
        is_valid, count, msg = self.verify_chain()
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT curr_hash, timestamp FROM audit_log_worm ORDER BY seq DESC LIMIT 1;")
            latest = cursor.fetchone()

        return {
            "tieu_chuan": "Thong_tu_46_2018_TT_BYT_Dieu_8_Ho_so_benh_an_dien_tu",
            "nghi_dinh": "Nghi_dinh_13_2023_ND_CP_Bao_ve_du_lieu_ca_nhan",
            "thoi_diem_kiem_dinh": datetime.now(timezone.utc).isoformat(),
            "trang_thai_toan_ven": is_valid,
            "tong_so_su_kien": count,
            "genesis_hash": GENESIS_HASH,
            "latest_hash": latest[0] if latest else GENESIS_HASH,
            "latest_timestamp": latest[1] if latest else None,
            "ket_luan_kiem_dinh": msg,
        }
