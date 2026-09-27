# -*- coding: utf-8 -*-
"""Bang khai mã nguồn: tệp nào do AI viết, theo lời nhắc nào, sửa bao nhiêu lần.

VI SAO CAN. Phu luc huong dan su dung AI cho phep "AI viet ma nguon ban dau"
voi hai dieu kien:

    1. ghi ro MA NAO do AI sinh
    2. co nhat ky loi nhac

Dieu 2 da co (`src/nhat_ky_loi_nhac.py`). Tep nay lam dieu 1.

CAU TRA LOI NGAN, va no phai duoc noi thang: **toan bo `src/`, `tests/`,
`tools/` do AI viet**, duoi su chi dao cua hoc sinh. Khong co tep nao viet tay
hoan toan. Bang duoi day khong phai de chia doi cong trang, ma de tra loi duoc
tung tep mot khi bi hoi.

CAI BANG NAY THEM VAO so voi mot cau khai chung:

  - moi tep sua bao nhieu lan, trong bao nhieu ngay  -> thay tep nao la trung
    tam, tep nao viet mot lan roi thoi
  - loi nhac nao dan toi tep do                       -> truy nguoc duoc quyet
    dinh thiet ke la cua ai

QUYET DINH THIET KE LA CUA HOC SINH, va cho do can phan biet ro voi viec go
ma. Vi du doc thang tu nhat ky loi nhac:

    "3.000 ca tu 24 khuon van co nguy co mo hinh hoc cong thuc viet"
    "khong huan luyen tren hoi thoai do mo hinh khac sinh"
    "dung dung vaic lam phan de doi chieu"

Ba cau do doi huong ca du an, va khong cau nao la mot dong ma.

    python -m src.khai_ma_nguon --ra docs/khai-ma-nguon.md
"""
import argparse
import io
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

THU_MUC_MA = ("src", "tests", "tools")


def _git(*doi):
    return subprocess.run(["git", *doi], capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


def lich_su_tep():
    """-> {duong_dan: {so_lan_sua, ngay_dau, ngay_cuoi, commit: [...]}}."""
    ra = defaultdict(lambda: {"so_lan_sua": 0, "ngay": [], "commit": []})
    ma = ngay = None
    for dong in _git("log", "--format=@@%h|%ad|%s", "--date=short",
                     "--name-only", "--", *THU_MUC_MA).splitlines():
        dong = dong.strip()
        if dong.startswith("@@"):
            ma, ngay, _tieu_de = dong[2:].split("|", 2)
        elif dong and ma and dong.split("/")[0] in THU_MUC_MA:
            m = ra[dong]
            m["so_lan_sua"] += 1
            m["ngay"].append(ngay)
            m["commit"].append(ma)
    for m in ra.values():
        m["ngay_dau"], m["ngay_cuoi"] = min(m["ngay"]), max(m["ngay"])
    return dict(ra)


def loi_nhac_theo_tep(muc):
    """-> {duong_dan: [loi nhac da rut gon]} tu nhat ky loi nhac."""
    # Tep ghi thang VA tep qua commit (17/09): nhieu lan ma duoc sua bang lenh
    # shell nen khong co Write/Edit, chi con dau vet o commit.
    from src.nhat_ky_loi_nhac import che_nhay_cam, tep_cua
    ra = defaultdict(list)
    for m in muc:
        van = che_nhay_cam(m["loi_nhac"])[0]
        for t in tep_cua(m):
            if van not in ra[t]:
                ra[t].append(van)
    return ra


def _dong(van, toi_da=90):
    import re
    van = re.sub(r"\s+", " ", van).strip()
    return van if len(van) <= toi_da else van[:toi_da] + "…"


def dung_bang(lich_su, theo_tep):
    d = ["# Bảng khai mã nguồn",
         "",
         "## Khai báo",
         "",
         "**Toàn bộ mã nguồn trong `src/`, `tests/`, `tools/` do AI viết**, dưới",
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

    # Chi liet ke loi nhac cho tep CO trong nhat ky. Tep khong co nghia la no
    # duoc sua trong mot luot khong co loi nhac rieng — khong phai la khong ro
    # nguon goc, ma la nam trong mot luot lam nhieu viec.
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


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ra", default="docs/khai-ma-nguon.md")
    a = ap.parse_args()

    from src import nhat_ky_loi_nhac

    ls = lich_su_tep()
    theo_tep = loi_nhac_theo_tep(nhat_ky_loi_nhac.gom())
    Path(a.ra).write_text(dung_bang(ls, theo_tep), encoding="utf-8")
    print(f"{len(ls)} tep ma nguon, "
          f"{sum(m['so_lan_sua'] for m in ls.values())} lan sua")
    print(f"{len([t for t in theo_tep if t in ls])} tep co loi nhac rieng")
    print(f"-> {a.ra}")


if __name__ == "__main__":
    main()
