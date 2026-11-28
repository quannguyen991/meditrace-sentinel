# -*- coding: utf-8 -*-
"""Xuất một tệp Markdown đơn giản (tiêu đề, đoạn, gạch đầu dòng, bảng, trích dẫn, khối mã) sang Word.

Dùng cho tài liệu minh chứng Đề cải tiến 1:
    python -m tools.xuat_minh_bach_docx docs/minh-bach/TRA_LOI_DE_CAI_TIEN_1.md
Ra tệp .docx cùng tên, cạnh tệp .md. Phông Times New Roman (không dùng Be Vietnam Pro).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor

PHONG = "Times New Roman"


def _chay(doan, chu: str, dam: bool = False, ma: bool = False) -> None:
    """Thêm chữ có **đậm** và `mã` vào một đoạn."""
    for phan in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", chu):
        if not phan:
            continue
        if phan.startswith("**") and phan.endswith("**"):
            r = doan.add_run(phan[2:-2])
            r.bold = True
        elif phan.startswith("`") and phan.endswith("`"):
            r = doan.add_run(phan[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(10)
            continue
        else:
            r = doan.add_run(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", phan).replace("*", ""))
            r.bold = dam
        r.font.name = PHONG


def chuyen(md: str) -> Document:
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name = PHONG
    st.font.size = Pt(12)
    dong = md.splitlines()
    i = 0
    while i < len(dong):
        d = dong[i].rstrip()
        if not d.strip() or d.strip() == "---":
            i += 1
            continue
        if d.startswith("```"):
            i += 1
            khoi = []
            while i < len(dong) and not dong[i].startswith("```"):
                khoi.append(dong[i])
                i += 1
            p = doc.add_paragraph()
            r = p.add_run("\n".join(khoi))
            r.font.name = "Consolas"
            r.font.size = Pt(9)
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", d)
        if m:
            h = doc.add_heading(level=min(len(m.group(1)), 3))
            _chay(h, m.group(2))
            for r in h.runs:
                r.font.color.rgb = RGBColor(12, 74, 110)
            i += 1
            continue
        if d.startswith("|"):
            hang = []
            while i < len(dong) and dong[i].startswith("|"):
                o = [x.strip() for x in dong[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", x) for x in o):
                    hang.append(o)
                i += 1
            so_cot = max(len(h) for h in hang)
            bang = doc.add_table(rows=len(hang), cols=so_cot)
            bang.style = "Table Grid"
            for ri, h in enumerate(hang):
                for ci in range(so_cot):
                    o = bang.cell(ri, ci)
                    o.text = ""
                    _chay(o.paragraphs[0], h[ci] if ci < len(h) else "", dam=(ri == 0))
            doc.add_paragraph()
            continue
        if re.match(r"^\s*[-*]\s+", d):
            p = doc.add_paragraph(style="List Bullet")
            _chay(p, re.sub(r"^\s*[-*]\s+", "", d))
            i += 1
            continue
        if d.startswith(">"):
            p = doc.add_paragraph()
            _chay(p, d.lstrip("> "))
            for r in p.runs:
                r.italic = True
            i += 1
            continue
        p = doc.add_paragraph()
        _chay(p, d)
        i += 1
    return doc


def main(duong: str) -> Path:
    vao = Path(duong)
    ra = vao.with_suffix(".docx")
    chuyen(vao.read_text(encoding="utf-8")).save(ra)
    print(f"Đã ghi {ra}")
    return ra


if __name__ == "__main__":
    main(sys.argv[1])
