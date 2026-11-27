# -*- coding: utf-8 -*-
"""Kiểm thử tự động cho Sổ nhật ký kiểm toán bất biến WORM (src/he_thong/nhat_ky_ky_duyet_worm.py)."""
import sqlite3
import tempfile
from pathlib import Path
import pytest

from src.he_thong.nhat_ky_ky_duyet_worm import WormAuditLogger, GENESIS_HASH


@pytest.fixture
def temp_logger(tmp_path):
    db_path = tmp_path / "test_worm.db"
    logger = WormAuditLogger(db_path)
    try:
        yield logger
    finally:
        logger.close()


def test_genesis_hash_khoi_tao(temp_logger):
    is_valid, count, _ = temp_logger.verify_chain()
    assert is_valid is True
    assert count == 0


def test_chuoi_bam_lien_hoan_hop_le(temp_logger):
    # Ghi 3 sự kiện
    ev1 = temp_logger.append_event("bs_nguyen", "TAO_BAN_NHAP", "ca_001", {"trieu_chung": "sốt 39 độ"})
    assert ev1["seq"] == 1
    assert ev1["prev_hash"] == GENESIS_HASH

    ev2 = temp_logger.append_event("bs_nguyen", "DUYET_MENH_DE", "ca_001", {"menh_de_id": 1, "trang_thai": "da_duyet"})
    assert ev2["seq"] == 2
    assert ev2["prev_hash"] == ev1["curr_hash"]

    ev3 = temp_logger.append_event("bs_tran", "XUAT_BENH_AN", "ca_001", {"dinh_dang": "FHIR_R4"})
    assert ev3["seq"] == 3
    assert ev3["prev_hash"] == ev2["curr_hash"]

    # Kiểm tra toàn vẹn
    is_valid, count, msg = temp_logger.verify_chain()
    assert is_valid is True
    assert count == 3
    assert "hợp lệ 100%" in msg


def test_trigger_ngan_sua_xoa_tuyet_doi(temp_logger):
    temp_logger.append_event("admin", "DONG_BANG_DATASET", "v2_5000", {"sha256": "abcdef"})

    # Cố tình UPDATE trực tiếp vào SQLite -> phải bị RAISE FAIL
    with pytest.raises(sqlite3.DatabaseError) as exc_info:
        temp_logger.conn.execute("UPDATE audit_log_worm SET action = 'SUA_LENH' WHERE seq = 1;")
    assert "WORM Violation" in str(exc_info.value)

    # Cố tình DELETE trực tiếp khỏi SQLite -> phải bị RAISE FAIL
    with pytest.raises(sqlite3.DatabaseError) as exc_info:
        temp_logger.conn.execute("DELETE FROM audit_log_worm WHERE seq = 1;")
    assert "WORM Violation" in str(exc_info.value)


def test_xuat_chung_chi_thanh_tra(temp_logger):
    temp_logger.append_event("bs_truong_khoa", "KHOA_HO_SO", "ca_100", {"chan_doan": "Sốt xuất huyết Dengue"})
    cert = temp_logger.export_inspection_certificate()

    assert cert["trang_thai_toan_ven"] is True
    assert cert["tong_so_su_kien"] == 1
    assert "Thong_tu_46_2018_TT_BYT" in cert["tieu_chuan"]
    assert cert["latest_hash"] != GENESIS_HASH


def test_neo_ngoai_phat_hien_cat_duoi_sau_drop_trigger(temp_logger):
    temp_logger.append_event("u1", "ACT_1", "c1", {"a": 1})
    temp_logger.append_event("u2", "ACT_2", "c2", {"b": 2})

    # Giả lập kẻ tấn công DROP TRIGGER rồi xóa bản ghi cuối (cắt đuôi chuỗi)
    temp_logger.conn.execute("DROP TRIGGER trg_audit_worm_prevent_delete;")
    temp_logger.conn.execute("DELETE FROM audit_log_worm WHERE seq = 2;")
    temp_logger.conn.commit()

    is_valid, count, msg = temp_logger.verify_chain()
    assert is_valid is False
    assert count == 1
    assert "neo ngoài" in msg.lower()
