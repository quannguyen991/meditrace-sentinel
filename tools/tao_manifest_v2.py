# -*- coding: utf-8 -*-
"""Tạo manifest chính thức và ghi sổ nhật ký kiểm toán bất biến WORM cho bộ dữ liệu V2.
Tuân thủ Thông tư 46/2018/TT-BYT và tiêu chuẩn đóng băng dữ liệu nghiên cứu khoa học.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

from src import ngu_lieu_viet as nl, tach_tap_viet as tv
from src.worm_audit_log import WormAuditLogger

DEFAULT_INPUT = Path("data/hoi_thoai_viet_v2_mo_rong.jsonl")
DEFAULT_OUTPUT = Path("data/manifest_v2_mo_rong_5000.json")


def tinh_sha256_tep(duong_dan: Path) -> str:
    """Tính mã băm SHA-256 của tệp tin theo từng khối 64KB."""
    h = hashlib.sha256()
    with open(duong_dan, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def tao_manifest(tep_vao: Path, tep_ra: Path, seed: int = tv.HAT_MAC_DINH) -> dict:
    """Đọc tệp JSONL v2, tính toán phân chia tập, mã băm và xuất manifest đóng băng."""
    if not tep_vao.exists():
        raise FileNotFoundError(f"Không tìm thấy tệp dữ liệu: {tep_vao}")

    # 1. Tính mã băm toàn tệp JSONL
    sha256_tep = tinh_sha256_tep(tep_vao)

    # 2. Đọc các ca hội thoại
    ca_list = []
    with open(tep_vao, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                ca_list.append(json.loads(line))

    so_ca = len(ca_list)
    khuon_xuat_hien = sorted({c["benh"] for c in ca_list})

    # 3. Phân chia tập độc lập
    phan_tap = tv.phan_khuon(khuon_xuat_hien, seed=seed)
    tap_cua = {}
    for tap, ds in phan_tap.items():
        for k in ds:
            tap_cua[k] = tap

    dong_danh_sach = []
    so_ca_theo_tap = {"train": 0, "phat_trien": 0, "kiem_tra_cuoi": 0}
    for c in ca_list:
        tap = tap_cua.get(c["benh"], "train")
        so_ca_theo_tap[tap] = so_ca_theo_tap.get(tap, 0) + 1
        dong_danh_sach.append(f"{c['id']}|{c['benh']}|{tap}")

    chuoi_danh_sach = "\n".join(dong_danh_sach).encode("utf-8")
    ma_bam_danh_sach_ca = hashlib.sha256(chuoi_danh_sach).hexdigest()

    manifest = {
        "ten_bo_du_lieu": "hoi_thoai_viet_v2_mo_rong",
        "phien_ban": "2.0.0",
        "tieu_chuan": "Thong_tu_46_2018_TT_BYT_Dieu_8",
        "tep_du_lieu": tep_vao.name,
        "sha256_tep": sha256_tep,
        "so_ca": so_ca,
        "seed": seed,
        "so_khuon_benh": len(khuon_xuat_hien),
        "so_ca_theo_tap": so_ca_theo_tap,
        "khuon_theo_tap": {t: sorted(v) for t, v in phan_tap.items()},
        "ma_bam_danh_sach_ca": ma_bam_danh_sach_ca,
        "trang_thai_dong_bang": True,
        "ghi_chu": "Manifest đóng băng bộ dữ liệu V2 mở rộng, độc lập theo khuôn bệnh (Zero Data Leakage).",
    }

    tep_ra.parent.mkdir(parents=True, exist_ok=True)
    tep_ra.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # 4. Ghi sổ kiểm toán bất biến WORM
    logger = WormAuditLogger()
    try:
        worm_ev = logger.append_event(
            user_id="infra_ui_worker",
            action="DONG_BANG_MANIFEST_DATASET_V2",
            case_id="v2_mo_rong_5000",
            payload={
                "tep_du_lieu": tep_vao.name,
                "sha256_tep": sha256_tep,
                "so_ca": so_ca,
                "seed": seed,
                "ma_bam_danh_sach_ca": ma_bam_danh_sach_ca,
                "so_ca_theo_tap": so_ca_theo_tap,
            },
            details=f"Đóng băng thành công 5.000 ca dữ liệu V2 với băm toàn vẹn {sha256_tep[:16]}..."
        )
        is_valid, count, msg = logger.verify_chain()
        cert = logger.export_inspection_certificate()
    finally:
        logger.close()

    manifest["worm_audit"] = {
        "seq": worm_ev["seq"],
        "timestamp": worm_ev["timestamp"],
        "curr_hash": worm_ev["curr_hash"],
        "prev_hash": worm_ev["prev_hash"],
        "xac_nhan_toan_ven": is_valid,
        "tong_su_kien_worm": count,
    }

    # Cập nhật lại manifest với thông tin WORM
    tep_ra.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main():
    ap = argparse.ArgumentParser(description="Tạo manifest đóng băng và ghi sổ WORM cho dataset V2.")
    ap.add_argument("--vao", type=Path, default=DEFAULT_INPUT, help="Đường dẫn tệp JSONL v2")
    ap.add_argument("--ra", type=Path, default=DEFAULT_OUTPUT, help="Đường dẫn tệp manifest JSON")
    ap.add_argument("--seed", type=int, default=tv.HAT_MAC_DINH, help="Seed ngẫu nhiên phân chia tập (mặc định 42 khớp với hệ thống)")
    a = ap.parse_args()

    manifest = tao_manifest(a.vao, a.ra, seed=a.seed)
    print(f"=== ĐÃ TẠO MANIFEST V2 THÀNH CÔNG ===")
    print(f"Tệp dữ liệu: {manifest['tep_du_lieu']}")
    print(f"Mã băm SHA-256 tệp: {manifest['sha256_tep']}")
    print(f"Tổng số ca: {manifest['so_ca']}")
    print(f"Số ca theo tập: {manifest['so_ca_theo_tap']}")
    print(f"Mã băm danh sách ca: {manifest['ma_bam_danh_sach_ca']}")
    print(f"WORM Audit Log seq: {manifest['worm_audit']['seq']}, hash: {manifest['worm_audit']['curr_hash']}")
    print(f"Đã lưu tại: {a.ra}")


if __name__ == "__main__":
    main()
