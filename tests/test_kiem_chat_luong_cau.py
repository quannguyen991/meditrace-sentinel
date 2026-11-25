# -*- coding: utf-8 -*-
"""Kiểm thử đơn vị cho công cụ kiểm tra chất lượng câu thoại (tools/kiem_chat_luong_cau.py)."""
from __future__ import annotations

import io
from pathlib import Path
import pytest

from tools.kiem_chat_luong_cau import (
    DANH_SACH_QUY_TAC,
    MO_TA_QUY_TAC,
    VAI_NOI_CHUAN,
    kiem_tra_cau,
    tach_vai_va_cau,
    kiem_tra_tep_jsonl,
    in_bao_cao,
    main,
)


def test_danh_sach_6_quy_tac_va_vai_chuan():
    """Kiểm tra danh sách 6 quy tắc và 4 vai nói chuẩn."""
    assert len(DANH_SACH_QUY_TAC) == 6
    assert set(DANH_SACH_QUY_TAC) == {
        "lap_tu_lien_ke",
        "hat_sau_dau_cham",
        "cum_thua_cuoi",
        "ket_thuc_dau_phay_hai_cham",
        "hai_dau_cach",
        "qua_40_tu",
    }
    assert all(q in MO_TA_QUY_TAC for q in DANH_SACH_QUY_TAC)
    assert set(VAI_NOI_CHUAN) == {"Bác sĩ", "Bệnh nhân", "Người nhà", "Điều dưỡng"}


def test_tach_vai_va_cau():
    """Kiểm tra hàm tách vai nói và nội dung lượt thoại."""
    assert tach_vai_va_cau("Bác sĩ: Xin chào bác.") == ("Bác sĩ", "Xin chào bác.")
    assert tach_vai_va_cau("Bệnh nhân: Tôi bị đau bụng.") == ("Bệnh nhân", "Tôi bị đau bụng.")
    assert tach_vai_va_cau("Người nhà: Cháu bị sốt cao.") == ("Người nhà", "Cháu bị sốt cao.")
    assert tach_vai_va_cau("Điều dưỡng: Đã đo xong huyết áp.") == ("Điều dưỡng", "Đã đo xong huyết áp.")
    assert tach_vai_va_cau("Bác sĩ: Khám: Họng đỏ nhẹ.") == ("Bác sĩ", "Khám: Họng đỏ nhẹ.")
    assert tach_vai_va_cau("   ") == ("", "")
    assert tach_vai_va_cau("Không có tiền tố vai nói") == ("Không rõ", "Không có tiền tố vai nói")


def test_kiem_tra_cau_sach():
    """Câu chuẩn lâm sàng không được vi phạm bất kỳ quy tắc nào."""
    cau = "Bác sĩ cho tôi hỏi kết quả xét nghiệm máu đã có chưa ạ?"
    assert kiem_tra_cau(cau) == []


def test_quy_tac_lap_tu_lien_ke():
    """Kiểm tra phát hiện lặp từ/cụm từ liền kề vi phạm."""
    cau_loi = "Tôi cảm giác căng tức nặng bìu nửa năm rồi rồi."
    assert "lap_tu_lien_ke" in kiem_tra_cau(cau_loi)

    cau_loi_2 = "Bác sĩ xem giúp tôi giúp tôi với ạ."
    assert "lap_tu_lien_ke" in kiem_tra_cau(cau_loi_2)


def test_quy_tac_hat_sau_dau_cham():
    """Kiểm tra phát hiện hạt từ đề nghị đặt ngay sau dấu chấm."""
    cau_loi = "Bác uống thuốc đều đặn. nhé"
    assert "hat_sau_dau_cham" in kiem_tra_cau(cau_loi)

    cau_loi_2 = "Tái khám sau 1 tuần. nha bác."
    assert "hat_sau_dau_cham" in kiem_tra_cau(cau_loi_2)


def test_quy_tac_cum_thua_cuoi():
    """Kiểm tra phát hiện cụm từ nhận xét cụt ghép sau dấu chấm."""
    cau_loi = "Sờ thấy nốt xơ dày ở bao gân gấp. cần theo dõi."
    assert "cum_thua_cuoi" in kiem_tra_cau(cau_loi)

    cau_loi_2 = "Chẩn đoán xác định viêm xoang cấp. rõ ràng."
    assert "cum_thua_cuoi" in kiem_tra_cau(cau_loi_2)


def test_quy_tac_ket_thuc_dau_phay_hai_cham():
    """Kiểm tra phát hiện câu kết thúc bằng dấu phẩy hoặc hai chấm."""
    assert "ket_thuc_dau_phay_hai_cham" in kiem_tra_cau("Bác sĩ dặn dò,")
    assert "ket_thuc_dau_phay_hai_cham" in kiem_tra_cau("Kế hoạch điều trị:")
    assert "ket_thuc_dau_phay_hai_cham" not in kiem_tra_cau("Bác sĩ dặn dò.")


def test_quy_tac_hai_dau_cach():
    """Kiểm tra phát hiện hai dấu cách liên tiếp."""
    assert "hai_dau_cach" in kiem_tra_cau("Tôi bị  đau đầu nhiều ngày nay.")
    assert "hai_dau_cach" not in kiem_tra_cau("Tôi bị đau đầu nhiều ngày nay.")


def test_quy_tac_qua_40_tu():
    """Kiểm tra phát hiện lượt thoại quá 40 từ."""
    cau_ngan = " " .join(["từ"] * 40)
    assert "qua_40_tu" not in kiem_tra_cau(cau_ngan)

    cau_dai = " ".join(["từ"] * 41)
    assert "qua_40_tu" in kiem_tra_cau(cau_dai)


def test_kiem_tra_tep_jsonl_gioi_han_so_ca():
    """Kiểm tra phân tích tệp dữ liệu với giới hạn --so-ca."""
    tep_5000 = Path("data/hoi_thoai_viet_5000.jsonl")
    if not tep_5000.exists():
        pytest.skip("Tệp data/hoi_thoai_viet_5000.jsonl không tồn tại.")

    kq = kiem_tra_tep_jsonl(tep_5000, so_ca=20)
    assert kq.tong_so_ca == 20
    assert kq.tong_so_luot > 0
    assert "Bác sĩ" in kq.thong_ke_vai_noi
    assert "Bệnh nhân" in kq.thong_ke_vai_noi
    assert all(q in kq.thong_ke_quy_tac for q in DANH_SACH_QUY_TAC)

    # Kiểm tra in báo cáo không sinh ngoại lệ
    buf = io.StringIO()
    in_bao_cao(kq, chi_tiet=True, file=buf)
    output = buf.getvalue()
    assert "BÁO CÁO KIỂM TRA CHẤT LƯỢNG HỘI THOẠI" in output
    assert "lap_tu_lien_ke" in output


def test_cli_main_chay_thanh_cong():
    """Kiểm tra gọi CLI main() chạy thành công mã thoát 0."""
    tep_5000 = Path("data/hoi_thoai_viet_5000.jsonl")
    if not tep_5000.exists():
        pytest.skip("Tệp data/hoi_thoai_viet_5000.jsonl không tồn tại.")

    ret = main(["data/hoi_thoai_viet_5000.jsonl", "--so-ca", "5"])
    assert ret == 0
