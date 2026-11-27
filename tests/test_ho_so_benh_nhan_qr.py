# -*- coding: utf-8 -*-
"""Kiểm thử tự động cho Gói Chăm sóc Người bệnh QR (src/cong_cu_lam_sang/ho_so_benh_nhan_qr.py) và nâng cấp an toàn lịch uống thuốc."""

import json
import re
import subprocess
import sys

from src.cong_cu_lam_sang.to_dan_do_benh_nhan import (
    CHE_DO_AN_UONG_BENH,
    GIAI_THICH_BENH_LY,
    phan_loai_lich_uong_thuoc,
    sinh_ban_dan_do_benh_nhan,
)
from src.cong_cu_lam_sang.ho_so_benh_nhan_qr import (
    tao_goi_cham_soc_benh_nhan,
    xac_thuc_chu_ky_goi,
)


def test_khong_mac_dinh_gio_sang_khi_mo_ho_lich_uong():
    """Thuốc không có từ khóa giờ uống hoặc tần suất phải vào chua_ro_gio, tuyệt đối không đẩy sang sáng."""
    lich = phan_loai_lich_uong_thuoc([
        "Amoxicillin 500mg uống 1 viên",
        "Paracetamol 500mg khi đau",
        "Amlodipine 5mg uống buổi sáng 1 viên",
        "Atorvastatin 20mg 1 viên",
    ])
    assert "chua_ro_gio" in lich
    ten_mo_ho = [x["ten_thuoc"] for x in lich["chua_ro_gio"]]
    assert "Amoxicillin 500mg uống 1 viên" in ten_mo_ho
    assert "Paracetamol 500mg khi đau" in ten_mo_ho
    for item in lich["chua_ro_gio"]:
        assert item["cach_dung"] == "Cần bác sĩ/dược sĩ xác nhận giờ uống cụ thể"

    ten_sang = [x["ten_thuoc"] for x in lich["sang"]]
    assert "Amoxicillin 500mg uống 1 viên" not in ten_sang
    assert "Paracetamol 500mg khi đau" not in ten_sang
    assert any("Amlodipine" in t for t in ten_sang)
    assert any("Atorvastatin" in t for t in [x["ten_thuoc"] for x in lich["toi"]])


def test_che_do_an_mac_dinh_tong_quat_va_mo_rong_benh_ly():
    """Chẩn đoán lạ dùng chế độ ăn tong_quat, không rơi nhầm sang hô hấp; các bệnh lý mới có giải thích riêng."""
    for benh in [
        "hen phế quản",
        "copd",
        "suy tim",
        "rối loạn mỡ máu",
        "nhiễm trùng tiết niệu",
        "đau nửa đầu",
        "thiếu máu",
        "bệnh thận mạn",
    ]:
        assert benh in GIAI_THICH_BENH_LY

    for nhom in ["suy thận", "suy tim", "tim mạch", "nhiễm khuẩn tiết niệu", "tong_quat"]:
        assert nhom in CHE_DO_AN_UONG_BENH

    ban_la = sinh_ban_dan_do_benh_nhan("Trần Văn X", "Thoái hóa khớp gối", ["Glucosamine 1500mg uống sáng 1 viên"])
    assert ban_la["che_do_an_uong"] == CHE_DO_AN_UONG_BENH["tong_quat"]
    assert ban_la["che_do_an_uong"] != CHE_DO_AN_UONG_BENH["hô hấp"]


def test_tao_goi_cham_soc_benh_nhan_hmac_va_an_toan():
    """Tạo gói chăm sóc QR hợp lệ, xác thực HMAC, gắn cờ thuốc mơ hồ và trích tương tác thực phẩm."""
    du_lieu = {
        "ten_benh_nhan": "Nguyễn Thị Minh",
        "chan_doan": "Suy tim độ II / Rối loạn mỡ máu",
        "danh_sach_thuoc": [
            "Atorvastatin 20mg 1 viên",
            "Perindopril 5mg uống buổi sáng 1 viên",
            "Furosemide 40mg 1 viên",
        ],
        "hieu_chinh_lieu": [
            {"thuoc": "Perindopril", "canh_bao": "Theo dõi creatinin và kali máu sau 7 ngày do eGFR giảm nhẹ"}
        ],
        "duoc_ly": {
            "thai_ky": "Chống chỉ định nếu có thai (nhóm ƯCMC)"
        },
        "ghi_chu_noi_bo": "Bí mật nội bộ bác sĩ không được lộ ra QR",
        "raw_transcript": "BS: ...",
    }

    goi = tao_goi_cham_soc_benh_nhan(du_lieu, bi_mat_ky="khoa-bi-mat-test")
    assert re.match(r"^[A-Za-z0-9_-]{8,32}$", goi["ma_ho_so"])
    assert goi["url_truy_cap"] == f"?portal={goi['ma_ho_so']}"
    assert xac_thuc_chu_ky_goi(goi, bi_mat_ky="khoa-bi-mat-test") is True
    assert xac_thuc_chu_ky_goi(goi, bi_mat_ky="khoa-sai") is False

    # Kiểm tra sửa nội dung làm hỏng chữ ký
    goi_sua = dict(goi, nguoi_benh="Kẻ giả mạo")
    assert xac_thuc_chu_ky_goi(goi_sua, bi_mat_ky="khoa-bi-mat-test") is False

    # Furosemide không ghi giờ -> phải nằm ở thuoc_mo_ho_lich
    mo_ho_names = [m["ten_thuoc"] for m in goi["thuoc_mo_ho_lich"]]
    assert any("Furosemide" in n for n in mo_ho_names)

    # Tương tác thực phẩm + hiệu chỉnh liều + dược lý
    noi_dung_tt = " ".join(item["noi_dung"] for item in goi["tuong_tac_thuc_an"])
    assert "bưởi chùm" in noi_dung_tt
    assert "Kali" in noi_dung_tt or "kali" in noi_dung_tt
    assert "creatinin" in noi_dung_tt
    assert "thai" in noi_dung_tt

    # Dấu hiệu báo động phù hợp suy tim
    assert any("Tăng cân nhanh" in rf or "Đau thắt ngực" in rf for rf in goi["dau_hieu_bao_dong"])

    # Không rò rỉ ghi chú nội bộ
    serialized = json.dumps(goi, ensure_ascii=False)
    assert "Bí mật nội bộ" not in serialized
    assert "raw_transcript" not in serialized


def test_cli_build_tu_stdin():
    """CLI --build đọc JSON từ stdin và xuất gói QR hợp lệ."""
    payload = {
        "ten_benh_nhan": "Lê Văn Hùng",
        "chan_doan": "Nhiễm trùng tiết niệu",
        "danh_sach_thuoc": ["Ciprofloxacin 500mg ngày 2 lần sau ăn"],
    }
    proc = subprocess.run(
        [sys.executable, "-m", "src.cong_cu_lam_sang.ho_so_benh_nhan_qr", "--build", "--secret", "cli-key"],
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    out = json.loads(proc.stdout)
    assert out["nguoi_benh"] == "Lê Văn Hùng"
    assert xac_thuc_chu_ky_goi(out, bi_mat_ky="cli-key") is True
    assert any("sữa" in item["noi_dung"] for item in out["tuong_tac_thuc_an"])
