# -*- coding: utf-8 -*-
"""Doi cac so do SVG viet thang trong tep Markdown thanh anh PNG.

VI SAO CAN (19/09/2026). Bo in ra PDF dung Chrome nen SVG viet thang trong Markdown
hien dung la so do. Bo xuat ra Word thi khong: no khong hieu the SVG, nen do NGUYEN
MA NGUON SVG ra giua trang van ban — nguoi doc thay mot khoi chu dai vo nghia.

Tep nay rut tung khoi SVG, dung Chrome ve thanh PNG, roi thay khoi do trong Markdown
bang mot dong anh thuong. Sau buoc nay ca hai bo — Word va PDF — deu ra so do.

    python tools/svg-sang-png.py docs/so-tay-meditrace-sentinel.md --thu-muc-anh hinh-so-do
    python tools/svg-sang-png.py <tep.md> --chi-xoa      # chi go bo, khong ve anh
"""
import argparse
import io
import re
import subprocess
import sys
import tempfile
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

# Khoi so do trong cac tep so tay co dang: <div style="margin:1rem ...> <svg ...> </svg> </div>
MAU = re.compile(r"<div[^>]*>\s*(<svg\b.*?</svg>)\s*</div>", re.S)
MAU_TRAN = re.compile(r"(<svg\b.*?</svg>)", re.S)

KHUON = """<!doctype html><html><head><meta charset="utf-8">
<style>html,body{{margin:0;padding:0;background:#fff}}
svg{{display:block;width:{rong}px;height:auto}}</style></head><body>{svg}</body></html>"""


def be_ngang(svg, mac_dinh=1400):
    """Rong anh theo ti le cua viewBox, de chu khong bi be."""
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not m:
        return mac_dinh, mac_dinh
    w, h = float(m.group(1)), float(m.group(2))
    return mac_dinh, max(1, round(mac_dinh * h / w))


def ve(svg, ra_png):
    rong, cao = be_ngang(svg)
    with tempfile.TemporaryDirectory() as tm:
        html = Path(tm) / "so-do.html"
        html.write_text(KHUON.format(svg=svg, rong=rong), encoding="utf-8")
        lenh = [str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
                "--hide-scrollbars", "--default-background-color=FFFFFFFF",
                f"--window-size={rong},{cao}",
                # Chrome doi duong dan TUYET DOI cho --screenshot.
                f"--screenshot={Path(ra_png).resolve()}", html.as_uri()]
        r = subprocess.run(lenh, capture_output=True, text=True)
    if not Path(ra_png).exists():
        raise SystemExit(f"Chrome khong ve duoc {ra_png}: {r.stderr[-400:]}")
    return rong, cao


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("tep")
    ap.add_argument("--thu-muc-anh", default="hinh-so-do",
                    help="thu muc anh, tinh tu thu muc cua tep .md")
    ap.add_argument("--ten", nargs="*", default=[], help="ten tep anh cho tung so do")
    ap.add_argument("--chu-thich", nargs="*", default=[], help="chu thich cho tung so do")
    ap.add_argument("--chi-xoa", action="store_true", help="go bo SVG, khong ve anh")
    a = ap.parse_args()

    tep = Path(a.tep)
    s = tep.read_text(encoding="utf-8")
    khoi = [m.group(1) for m in MAU.finditer(s)] or MAU_TRAN.findall(s)
    if not khoi:
        print("khong co so do SVG nao trong tep")
        return
    print(f"{tep.name}: {len(khoi)} so do SVG")

    thu_muc = tep.parent / a.thu_muc_anh
    if not a.chi_xoa:
        thu_muc.mkdir(parents=True, exist_ok=True)

    for i, svg in enumerate(khoi):
        ten = a.ten[i] if i < len(a.ten) else f"so-do-{i + 1}"
        chu = a.chu_thich[i] if i < len(a.chu_thich) else ""
        if a.chi_xoa:
            moi = ""
        else:
            png = thu_muc / f"{ten}.png"
            rong, cao = ve(svg, png)
            print(f"  {ten}.png  {rong}x{cao}")
            moi = f"![{chu}]({a.thu_muc_anh}/{ten}.png)"
        # Go ca lop <div> boc ngoai neu co
        m = re.search(re.escape(svg), s)
        i0, i1 = m.start(), m.end()
        truoc = s.rfind("<div", 0, i0)
        if truoc != -1 and s[truoc:i0].strip().endswith(">") and "<div" not in s[truoc + 4:i0]:
            i0 = truoc
        sau = s.find("</div>", i1)
        if sau != -1 and not s[i1:sau].strip():
            i1 = sau + len("</div>")
        s = s[:i0] + moi + s[i1:]

    tep.write_text(s, encoding="utf-8")
    print("da ghi", tep)


if __name__ == "__main__":
    main()
