# -*- coding: utf-8 -*-
"""xuat-pdf.py — dung ban de cuong (mot doan HTML roi) thanh tep in duoc, roi in ra PDF.

    python tools/xuat-pdf.py <de-cuong.html> [ra.pdf]

Tep de cuong la MOT DOAN HTML: chi co <title>, <link>, <style> roi <div class="wrap">.
No khong co <!DOCTYPE>, <html>, <head>, <body> vi he thong Artifact tu boc.
De in thi phai tu boc lai, dong thoi:
  - ep giao dien SANG bang data-theme="light" (khong thi may nao dat che do toi
    se in ra nen den, ton muc va kho doc)
  - them CSS cho trang giay: kho A4, le, va luat ngat trang
  - bo min-width cua bang, vi 520px vuot qua be ngang trang A4

Sau khi in thi DEM SO TRANG. Chrome tra ma 0 ca khi PDF ra trang trang.
"""
import subprocess
import sys
import unicodedata
from pathlib import Path

CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

CSS_IN = """
<style>
  @page { size: A4; margin: 17mm 15mm 15mm 15mm; }

  html, body { background: #fff !important; }
  body { font-size: 10.5pt; line-height: 1.55; padding: 0 !important; }
  .wrap { width: 100% !important; margin: 0 !important; }

  /* Bang: bo min-width de vua be ngang trang giay */
  .table-scroll { overflow: visible !important; }
  table { min-width: 0 !important; font-size: 8.6pt; }
  th, td { padding: .38rem .5rem; }

  /* Luat ngat trang */
  h1, h2, h3 { break-after: avoid; page-break-after: avoid; }
  tr, li { break-inside: avoid; page-break-inside: avoid; }
  caption { break-after: avoid; }
  .demo, .arch-row, .ask, .checks li, .scores { break-inside: avoid; page-break-inside: avoid; }
  section { break-inside: auto; }
  .masthead { break-after: avoid; }

  /* Ban ghi hoi thoai co the dai hon be ngang trang - cho xuong dong */
  .transcript { overflow: visible !important; }
  .transcript .line { white-space: normal !important; }

  h1 { font-size: 21pt; max-width: none; }
  h2 { font-size: 14pt; }
  .standfirst { font-size: 11pt; }
  section { margin-bottom: 2.1rem; }

  a { color: inherit; text-decoration: none; }
</style>
"""


def dung_tep_in(doan: Path, ra: Path) -> Path:
    s = doan.read_text(encoding="utf-8")
    moc = '<div class="wrap">'
    if moc not in s:
        sys.exit(f"Khong tim thay {moc} trong {doan.name} — tep khong dung dinh dang")
    dau, than = s.split(moc, 1)
    than = moc + than
    ra.write_text(
        "<!doctype html>\n"
        '<html lang="vi" data-theme="light">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        + dau
        + CSS_IN
        + "</head>\n<body>\n"
        + than
        + "\n</body>\n</html>\n",
        encoding="utf-8",
    )
    return ra


def in_pdf(html: Path, pdf: Path) -> Path:
    html = Path(unicodedata.normalize("NFC", str(html.resolve())))
    # Chrome doi duong dan TUYET DOI cho --print-to-pdf; duong dan tuong doi
    # lam no bao "cannot find the path specified" roi thoat voi ma 0.
    pdf = Path(unicodedata.normalize("NFC", str(pdf.resolve())))
    pdf.parent.mkdir(parents=True, exist_ok=True)
    if pdf.exists():
        pdf.unlink()
    cmd = [
        str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=45000",
        f"--print-to-pdf={pdf}", html.as_uri(),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if not pdf.exists():
        print(r.stdout[-1500:], r.stderr[-1500:], sep="\n")
        sys.exit("Chrome khong tao duoc PDF")
    return pdf


def dem_trang(pdf: Path) -> int:
    try:
        import pymupdf
        d = pymupdf.open(pdf)
        n = d.page_count
        d.close()
        return n
    except Exception:
        from pypdf import PdfReader
        return len(PdfReader(str(pdf)).pages)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Dung: python tools/xuat-pdf.py <de-cuong.html> [ra.pdf]")
    goc = Path(sys.argv[1])
    dich = Path(sys.argv[2]) if len(sys.argv) > 2 else goc.with_suffix(".pdf")
    tam = dich.with_name(dich.stem + "-in.html")
    dung_tep_in(goc, tam)
    pdf = in_pdf(tam, dich)
    print(f"{pdf}  ·  {dem_trang(pdf)} trang  ·  {pdf.stat().st_size / 1024:.0f} KB")
