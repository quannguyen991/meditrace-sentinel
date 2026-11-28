import pytest

from tools.kiem_trailer_commit import main, trailer_hop_le


def test_trailer_hop_le():
    assert trailer_hop_le("x\n\nCong-cu-AI: claude_code") is True


def test_trailer_gia_tri_la():
    assert trailer_hop_le("x\n\nCong-cu-AI: gpt5") is False


def test_khong_trailer():
    assert trailer_hop_le("x") is False


def test_merge_bo_qua():
    assert trailer_hop_le("Merge branch 'a'") is True


def test_main_thoat_1_khi_thieu_trailer(tmp_path, capsys):
    tep = tmp_path / "COMMIT_EDITMSG"
    tep.write_text("feat: x\n\n# Cong-cu-AI: claude_code\n", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        main(str(tep))
    assert e.value.code == 1
    assert "Cong-cu-AI" in capsys.readouterr().err


def test_main_thoat_0_khi_co_trailer(tmp_path):
    tep = tmp_path / "COMMIT_EDITMSG"
    tep.write_text("feat: x\n\nCong-cu-AI: khong\n", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        main(str(tep))
    assert e.value.code == 0
