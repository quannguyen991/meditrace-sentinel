# -*- coding: utf-8 -*-
"""[Dịch vụ, an toàn và minh bạch › Minh bạch]
Làm gì   : Lập bảng khai tệp mã nguồn nào do AI viết, sửa mấy lần và theo lời nhắc nào, để
           minh bạch phần AI.
Vào → Ra : lịch sử git của mã nguồn + nhật ký lời nhắc → tệp Markdown bảng khai theo từng
           tệp
Đọc từ   : dung_bang() dựng bảng Markdown; lich_su_tep() gom lịch sử sửa từ git
Mục lục (các hàm/lớp chính):
  main()               Điểm vào: sinh tệp bảng khai mã nguồn
  lich_su_tep()        Gom lịch sử sửa từng tệp mã nguồn từ git
  loi_nhac_theo_tep()  Gom lời nhắc đã rút gọn theo từng tệp
  dung_bang()          Dựng nội dung bảng khai mã nguồn dạng Markdown
Gọi tới  : he_thong/nhat_ky_loi_nhac
Tên cũ   : khai_ma_nguon.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Bang khai mã nguồn: tệp nào do AI viết, theo lời nhắc nào, sửa bao nhiêu lần.

VÌ SAO CẦN. Phụ lục hướng dẫn sử dụng AI cho phép "AI viết mã nguồn ban đầu"
với hai điều kiện:

    1. ghi rõ MÃ NÀO do AI sinh
    2. có nhật ký lời nhắc

Điều 2 đã có (`src/he_thong/nhat_ky_loi_nhac.py`). Tệp này làm điều 1.

CÂU TRẢ LỜI NGẮN, và nó phải được nói thẳng: **toàn bộ `src/`, `tests/`,
`tools/` do AI viết**, dưới sự chỉ đạo của học sinh. Không có tệp nào viết tay
hoàn toàn. Bảng dưới đây không phải để chia đôi công trạng, mà để trả lời được
từng tệp một khi bị hỏi.

CÁI BẢNG NÀY THÊM VÀO so với một câu khai chung:

  - mỗi tệp sửa bao nhiêu lần, trong bao nhiêu ngày  -> thấy tệp nào là trung
    tâm, tệp nào viết một lần rồi thôi
  - lời nhắc nào dẫn tới tệp đó                       -> truy ngược được quyết
    định thiết kế là của ai

QUYẾT ĐỊNH THIẾT KẾ LÀ CỦA HỌC SINH, và chỗ đó cần phân biệt rõ với việc gõ
mã. Ví dụ đọc thẳng từ nhật ký lời nhắc:

    "3.000 ca từ 24 khuôn vẫn có nguy cơ mô hình học công thức viết"
    "không huấn luyện trên hội thoại do mô hình khác sinh"
    "dùng đúng vaic làm phần để đối chiếu"

Ba câu đó đổi hướng cả dự án, và không câu nào là một dòng mã.

    python -m src.he_thong.khai_ma_nguon --ra docs/khai-ma-nguon.md
"""
import argparse
import io
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

THU_MUC_MA = ("src", "tests", "tools", "web")
KHO_WEB = Path("D:/meditrace-sentinel")
THU_MUC_MA_WEB = ("src", "may-chu", "db", "server.ts")   # trong kho web; ghi là web/...


# ─── _git() — Chạy lệnh git và trả về đầu ra ──────────────────────────────────────────
# Có thể chỉ định kho khác.
def _git(*doi, repo=None):
    lenh = ["git"] + (["-C", str(repo)] if repo else []) + list(doi)
    return subprocess.run(lenh, capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


# ═══ lich_su_tep() — Gom lịch sử sửa từng tệp mã nguồn từ git ═════════════════════════
# Gồm số lần sửa, ngày đầu, ngày cuối và commit; quét cả kho xử lý và web.
def lich_su_tep():
    """-> {duong_dan: {so_lan_sua, ngay_dau, ngay_cuoi, commit: [...]}}.

    Gom CẢ HAI kho: phần xử lý (src, tests, tools) và giao diện web (ghi là web/...).
    """
    ra = defaultdict(lambda: {"so_lan_sua": 0, "ngay": [], "commit": []})

    def doc(repo, thu_muc, tien_to):
        ma = ngay = None
        for dong in _git("log", "--format=@@%h|%ad|%s", "--date=short",
                         "--name-only", "--", *thu_muc, repo=repo).splitlines():
            dong = dong.strip()
            if dong.startswith("@@"):
                ma, ngay, _tieu_de = dong[2:].split("|", 2)
            elif dong and ma and (repo or dong.split("/")[0] in THU_MUC_MA):
                if repo and dong.split("/")[0] not in THU_MUC_MA_WEB and dong not in THU_MUC_MA_WEB:
                    continue
                m = ra[tien_to + dong]
                m["so_lan_sua"] += 1
                m["ngay"].append(ngay)
                m["commit"].append(ma)

    doc(None, ("src", "tests", "tools"), "")
    if KHO_WEB.exists():
        doc(KHO_WEB, THU_MUC_MA_WEB, "web/")
    for m in ra.values():
        m["ngay_dau"], m["ngay_cuoi"] = min(m["ngay"]), max(m["ngay"])
    return dict(ra)


# ═══ loi_nhac_theo_tep() — Gom lời nhắc đã rút gọn theo từng tệp ══════════════════════
# Lấy từ nhật ký lời nhắc.
def loi_nhac_theo_tep(muc):
    """-> {duong_dan: [lời nhắc đã rút gọn]} từ nhật ký lời nhắc."""
    # Tệp ghi thẳng VÀ tệp qua commit (17/09): nhiều lần mã được sửa bằng lệnh
    # shell nên không có Write/Edit, chỉ còn dấu vết ở commit.
    from src.he_thong.nhat_ky_loi_nhac import che_nhay_cam, tep_cua
    ra = defaultdict(list)
    for m in muc:
        van = che_nhay_cam(m["loi_nhac"])[0]
        for t in tep_cua(m):
            if van not in ra[t]:
                ra[t].append(van)
    return ra


# ─── _dong() — Rút gọn văn bản thành một dòng ─────────────────────────────────────────
# Cắt khi dài hơn mức tối đa.
def _dong(van, toi_da=90):
    import re
    van = re.sub(r"\s+", " ", van).strip()
    return van if len(van) <= toi_da else van[:toi_da] + "…"


# ═══ dung_bang() — Dựng nội dung bảng khai mã nguồn dạng Markdown ═════════════════════
# Khai toàn bộ mã do AI viết, kèm số lần sửa và lời nhắc từng tệp.
def dung_bang(lich_su, theo_tep):
    d = ["# Bảng khai mã nguồn",
         "",
         "## Khai báo",
         "",
         "**Toàn bộ mã nguồn trong `src/`, `tests/`, `tools/` (phần xử lý) và `web/` (giao diện) do AI viết**, dưới",
         "sự chỉ đạo của học sinh. Không có tệp nào được viết tay hoàn toàn.",
         "",
         "Nhật ký lời nhắc kèm theo: `docs/nhat-ky-loi-nhac.md`.",
         "",
         "## Phân biệt: viết mã và quyết định thiết kế",
         "",
         "Bảng dưới nói về **việc gõ mã**. Các **quyết định thiết kế** đến từ học",
         "sinh, và đọc thẳng ra được trong nhật ký lời nhắc. Ba ví dụ đã đổi hướng",
         "cả dự án, không câu nào là một dòng mã:",
         "",
         "> *“3.000 ca từ 24 khuôn vẫn có nguy cơ mô hình học công thức viết”*",
         ">",
         "> *“không huấn luyện trên hội thoại do mô hình khác sinh”*",
         ">",
         "> *“đừng dùng VAIC làm phần đề bạn đối chiếu”*",
         "",
         "---",
         ""]

    tong_sua = sum(m["so_lan_sua"] for m in lich_su.values())
    d += [f"**Số tệp mã nguồn:** {len(lich_su)}  ·  "
          f"**Tổng số lần sửa:** {tong_sua}", ""]

    for tm in THU_MUC_MA:
        tep = sorted(t for t in lich_su if t.startswith(tm + "/"))
        if not tep:
            continue
        d += [f"## `{tm}/` — {len(tep)} tệp", "",
              "| Tệp | Lần sửa | Từ ngày | Đến ngày | Nguồn |",
              "|---|---|---|---|---|"]
        for t in tep:
            m = lich_su[t]
            d.append(f"| `{t.split('/', 1)[1]}` | {m['so_lan_sua']} | "
                     f"{m['ngay_dau']} | {m['ngay_cuoi']} | AI viết |")
        d.append("")

    # Chỉ liệt kê lời nhắc cho tệp CÓ trong nhật ký. Tệp không có nghĩa là nó
    # được sửa trong một lượt không có lời nhắc riêng — không phải là không rõ
    # nguồn gốc, mà là nằm trong một lượt làm nhiều việc.
    co = {t: v for t, v in theo_tep.items() if t in lich_su}
    thieu = sorted(t for t in lich_su if t not in co)
    d += ["---", "",
          "## Lời nhắc dẫn tới từng tệp", "",
          f"Truy được lời nhắc: **{len(co)}/{len(lich_su)}** tệp.",
          "",
          "Một lời nhắc có thể gắn với nhiều tệp — ví dụ *“làm hết tất cả các task",
          "k nghỉ”* dẫn tới 16 tệp cùng lúc — nên số lời nhắc ít hơn nhiều so với",
          "số tệp. Lời nhắc ở đây đã qua bước che nội dung nhạy cảm như trong",
          "`docs/nhat-ky-loi-nhac.md`.",
          ""]
    if thieu:
        d += [f"**{len(thieu)} tệp không truy được lời nhắc riêng.** Phải nói rõ "
              "thay vì bỏ qua:", ""]
        for t in thieu:
            d.append(f"  - `{t}` — {lich_su[t]['so_lan_sua']} lần sửa, "
                     f"{lich_su[t]['ngay_dau']}")
        d += ["",
              f"Cả {len(thieu)} tệp đều **do AI viết**, như mọi tệp khác — thiếu ở",
              "đây là thiếu *đường truy ngược tới lời nhắc*, không phải thiếu khai",
              "báo nguồn. Thường gặp: tệp `__init__.py` rỗng, hoặc tệp sửa trong một",
              "commit trước mọi lời nhắc đã ghi nhận.",
              ""]
    d += [""]
    for t in sorted(co):
        d.append(f"**`{t}`**")
        for ln in co[t]:
            d.append(f"  - {_dong(ln)}")
        d.append("")
    return "\n".join(d)


# ═══ main() — Điểm vào: sinh tệp bảng khai mã nguồn ═══════════════════════════════════
# Ghi docs/khai-ma-nguon.md và in thống kê.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ra", default="docs/khai-ma-nguon.md")
    a = ap.parse_args()

    from src.he_thong import nhat_ky_loi_nhac as nhat_ky_loi_nhac

    ls = lich_su_tep()
    theo_tep = loi_nhac_theo_tep(nhat_ky_loi_nhac.gom())
    Path(a.ra).write_text(dung_bang(ls, theo_tep), encoding="utf-8")
    print(f"{len(ls)} tep ma nguon, "
          f"{sum(m['so_lan_sua'] for m in ls.values())} lan sua")
    print(f"{len([t for t in theo_tep if t in ls])} tep co loi nhac rieng")
    print(f"-> {a.ra}")


if __name__ == "__main__":
    main()
