"""Kiểm thông điệp commit có trailer `Cong-cu-AI:` hợp lệ (dùng trong hook commit-msg)."""
from __future__ import annotations

import re
import sys

CONG_CU_HOP_LE = {"claude_code", "antigravity", "codex", "chatgpt", "khong"}

_TRAILER = re.compile(r"^Cong-cu-AI:\s*(\S+)\s*$")

HUONG_DAN = (
    "Commit bị chặn: thiếu trailer `Cong-cu-AI:` hợp lệ.\n"
    "Thêm một dòng ở cuối thông điệp commit, ví dụ:\n\n"
    "    Cong-cu-AI: claude_code\n\n"
    "Giá trị cho phép: " + ", ".join(sorted(CONG_CU_HOP_LE)) + ".\n"
    "Dùng `khong` khi commit không có công cụ AI nào hỗ trợ.\n"
)


def trailer_hop_le(thong_diep: str) -> bool:
    dong = thong_diep.splitlines()
    if dong and dong[0].startswith("Merge "):
        return True
    for d in dong:
        m = _TRAILER.match(d.strip())
        if m and m.group(1) in CONG_CU_HOP_LE:
            return True
    return False


def main(duong_dan: str) -> None:
    with open(duong_dan, encoding="utf-8", errors="replace") as f:
        dong = [d for d in f.read().splitlines() if not d.startswith("#")]
    if trailer_hop_le("\n".join(dong)):
        sys.exit(0)
    try:  # hook chạy không có PYTHONUTF8: tránh lỗi mã hoá khi in tiếng Việt
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    sys.stderr.write(HUONG_DAN)
    sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Cách dùng: python tools/kiem_trailer_commit.py <tệp thông điệp commit>\n")
        sys.exit(2)
    main(sys.argv[1])
