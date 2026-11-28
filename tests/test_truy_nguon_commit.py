from tools.truy_nguon_commit import cham_test, phan_loai_commit, tach_log


def test_trailer_cong_cu_ai():
    assert phan_loai_commit("fix: x\n\nCong-cu-AI: antigravity", {}, "a1") == "antigravity"


def test_co_authored_by_claude():
    assert (
        phan_loai_commit(
            "fix\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>", {}, "a2"
        )
        == "claude_code"
    )


def test_khong_ghi_cong_cu():
    assert phan_loai_commit("fix", {}, "a3") == "chua_xac_dinh"


def test_ghi_de_uu_tien_nhat():
    assert phan_loai_commit("fix", {"a4": "khong"}, "a4") == "khong"


def test_ghi_de_thang_trailer():
    assert phan_loai_commit("fix\n\nCong-cu-AI: codex", {"a5": "khong"}, "a5") == "khong"


def test_cham_test():
    assert cham_test(["tests/test_x.py"]) is True
    assert cham_test(["web/src/lib/a.test.ts"]) is True
    assert cham_test(["src/a.py", "README.md"]) is False


def test_tach_log_tieng_viet():
    tho = (
        "\x1eabc1234567\x1f2026-11-28\x1ffeat: thêm bộ che\x1ffeat: thêm bộ che\n\n"
        "Thân có dấu: bệnh nhân.\nCong-cu-AI: claude_code\n\x1e\n"
        "3\t1\ttests/test_a.py\n1\t0\tsrc/b.py\n"
    )
    ds = tach_log(tho)
    assert len(ds) == 1
    c = ds[0]
    assert c["ma"] == "abc1234567"
    assert c["ngay"] == "2026-11-28"
    assert c["tom_tat"] == "feat: thêm bộ che"
    assert "Cong-cu-AI: claude_code" in c["thong_diep"]
    assert c["tep"] == ["tests/test_a.py", "src/b.py"]
