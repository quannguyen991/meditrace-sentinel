# -*- coding: utf-8 -*-
"""Log tiến trình Python không được chứa định danh bệnh nhân (Đề cải tiến 1)."""
from src.he_thong.che_log import che_log, in_loi_an_toan


def test_in_loi_an_toan_khong_in_ten(capsys):
    try:
        raise ValueError("lỗi ở hội thoại: Bệnh nhân Nguyễn Văn An 0912345678")
    except ValueError as exc:
        in_loi_an_toan(exc)
    err = capsys.readouterr().err
    assert "ValueError" in err
    assert "Nguyễn Văn An" not in err
    assert "0912345678" not in err


def test_che_log_cat_ngan():
    assert len(che_log("x" * 5000)) <= 300


def test_che_log_che_ten_va_so():
    ra = che_log("Bệnh nhân Nguyễn Văn An, sđt 0912345678, đau ngực")
    assert "Nguyễn Văn An" not in ra and "0912345678" not in ra
