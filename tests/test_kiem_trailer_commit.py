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


def test_hook_chay_duoc_tren_macos_linux():
    """Git bỏ qua hook không có quyền chạy; macOS thường chỉ có python3."""
    import subprocess
    from pathlib import Path
    goc = Path(__file__).resolve().parents[1]
    mode = subprocess.run(["git", "ls-files", "-s", ".githooks/commit-msg"], cwd=goc,
                          capture_output=True, text=True).stdout.split()[0]
    assert mode == "100755"
    noi_dung = (goc / ".githooks" / "commit-msg").read_text(encoding="utf-8")
    assert "python3" in noi_dung
