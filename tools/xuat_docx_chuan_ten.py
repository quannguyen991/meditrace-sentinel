# -*- coding: utf-8 -*-
"""
Script chuyen doi va dong bo file Word (.docx) chuan ten tieng Viet khong in hoa:
1. Lịch sử câu lệnh.docx (tu Lịch sử câu lệnh.md)
2. Kê khai mã nguồn.docx (tu Kê khai mã nguồn.md)
3. Nhật ký lời nhắc và khai mã nguồn.docx (tu NHAT_KY_LOI_NHAC_VA_KHAI_MA_NGUON.docx)
4. Nhật ký mã nguồn và rà soát lỗi.docx (tu NHAT_KY_MA_NGUON_VA_RA_SOAT_LOI.docx)

Dong bo vao:
- C:\\Users\\admin\\Downloads\\MediTrace\\
- C:\\Users\\admin\\Desktop\\
- docs\\tai-lieu\\
"""

import sys
import os
import shutil

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr:
    sys.stderr.reconfigure(encoding='utf-8')

import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_margins(cell, top=35, bottom=35, left=60, right=60):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, hex_color):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_table_styling(table):
    tblPr = table._tbl.tblPr
    sz = "4"
    color = "CBD5E1"
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def make_header_repeat(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

def make_row_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))

def safe_copy(src, dst):
    try:
        shutil.copy(src, dst)
        print(f"[OK] Da sao chep: {src} -> {dst}")
    except Exception as e:
        print(f"[WARN] Loi sao chep sang {dst}: {e}")

def create_lich_su_cau_lenh_docx():
    src_md = r"C:\Users\admin\Downloads\MediTrace\Lịch sử câu lệnh.md"
    with open(src_md, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.7)

    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t.paragraph_format.space_before = Pt(0)
    p_t.paragraph_format.space_after = Pt(2)
    r_t = p_t.add_run("Lịch sử câu lệnh (Prompt History)\nMediTrace Sentinel")
    r_t.bold = True
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(14)
    r_t.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run("Hồ sơ nhật ký lời nhắc của tác giả và tiến trình thực thi mã nguồn (05/09/2026 – 18/10/2026)")
    r_sub.italic = True
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(9.5)
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    lines = md_text.split("\n")
    for l in lines:
        l_str = l.strip()
        if not l_str:
            continue
            
        if l_str.startswith("# Lịch sử câu lệnh"):
            continue
        elif l_str.startswith("## "):
            date_val = l_str.replace("## ", "").strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(f"Ngày {date_val}")
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(12)
            r.font.color.rgb = RGBColor(3, 105, 161)
        elif l_str.startswith("**") and "—" in l_str:
            # Dòng prompt: **HH:MM** — prompt
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.1
            parts = l_str.split("—", 1)
            time_part = parts[0].replace("**", "").strip()
            prompt_part = parts[1].strip() if len(parts) > 1 else ""
            
            r_time = p.add_run(time_part + " — ")
            r_time.bold = True
            r_time.font.name = "Times New Roman"
            r_time.font.size = Pt(10)
            r_time.font.color.rgb = RGBColor(15, 23, 42)
            
            r_pr = p.add_run(prompt_part)
            r_pr.font.name = "Times New Roman"
            r_pr.font.size = Pt(10.5)
        elif l_str.startswith("Tệp đã ghi:"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(l_str)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            r.font.color.rgb = RGBColor(71, 85, 105)
        elif l_str.startswith("Qua commit"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(l_str)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            r.font.color.rgb = RGBColor(51, 65, 85)
        elif l_str.startswith("Câu lệnh thực thi:") or l_str.startswith("Kết quả:"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(l_str)
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            r.font.color.rgb = RGBColor(30, 41, 59)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(l_str)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)

    out_local = "docs/tai-lieu/Lịch sử câu lệnh.docx"
    doc.save(out_local)
    print(f"[OK] Da tao {out_local}")
    return out_local

def create_ke_khai_ma_nguon_docx():
    src_md = r"C:\Users\admin\Downloads\MediTrace\Kê khai mã nguồn.md"
    with open(src_md, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = Document()
    for s in doc.sections:
        s.top_margin = Inches(0.7)
        s.bottom_margin = Inches(0.7)
        s.left_margin = Inches(0.8)
        s.right_margin = Inches(0.7)

    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t.paragraph_format.space_before = Pt(0)
    p_t.paragraph_format.space_after = Pt(2)
    r_t = p_t.add_run("Bảng kê khai mã nguồn\nMediTrace Sentinel")
    r_t.bold = True
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(14)
    r_t.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(10)
    r_sub = p_sub.add_run("Bảng thống kê tệp mã nguồn và phân định trách nhiệm đóng góp (05/09/2026 – 18/10/2026)")
    r_sub.italic = True
    r_sub.font.name = "Times New Roman"
    r_sub.font.size = Pt(9.5)
    r_sub.font.color.rgb = RGBColor(100, 116, 139)

    lines = md_text.split("\n")
    in_table = False
    table_rows = []

    def flush_table(rows):
        if not rows:
            return
        t = doc.add_table(rows=len(rows), cols=len(rows[0]))
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_styling(t)
        make_header_repeat(t.rows[0])
        for r_i, row in enumerate(rows):
            make_row_cant_split(t.rows[r_i])
            cells = t.rows[r_i].cells
            for c_i, val in enumerate(row):
                c = cells[c_i]
                set_cell_margins(c, 25, 25, 45, 45)
                p = c.paragraphs[0]
                p.paragraph_format.space_after = Pt(0)
                r = p.add_run(val.strip().replace("`", ""))
                r.font.name = "Times New Roman"
                if r_i == 0:
                    set_cell_background(c, "0F172A")
                    r.bold = True
                    r.font.size = Pt(8.5)
                    r.font.color.rgb = RGBColor(255, 255, 255)
                else:
                    if r_i % 2 == 1:
                        set_cell_background(c, "F8FAFC")
                    r.font.size = Pt(8.5)

    for l in lines:
        l_str = l.strip()
        if not l_str:
            if in_table:
                flush_table(table_rows)
                table_rows = []
                in_table = False
            continue

        if l_str.startswith("|") and l_str.endswith("|"):
            parts = [c.strip() for c in l_str.split("|")[1:-1]]
            if len(parts) >= 2 and all(set(c) <= set("-: ") for c in parts):
                continue # Bo qua dong gach ngang |--|--|
            in_table = True
            table_rows.append(parts)
            continue
        elif in_table:
            flush_table(table_rows)
            table_rows = []
            in_table = False

        if l_str.startswith("# Bảng khai mã nguồn") or l_str.startswith("# Kê khai mã nguồn"):
            continue
        elif l_str.startswith("## "):
            sec_title = l_str.replace("## ", "").strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            r = p.add_run(sec_title)
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(11.5)
            r.font.color.rgb = RGBColor(3, 105, 161)
        elif l_str.startswith(">"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(l_str.replace(">", "").replace("*", "").strip())
            r.italic = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
            r.font.color.rgb = RGBColor(71, 85, 105)
        elif l_str.startswith("**`") and l_str.endswith("`**"):
            # File header ở phần phụ lục lời nhắc
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(l_str.replace("**`", "").replace("`**", "").strip())
            r.bold = True
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            r.font.color.rgb = RGBColor(15, 23, 42)
        elif l_str.startswith("- "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.2)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run("• " + l_str[2:])
            r.font.name = "Times New Roman"
            r.font.size = Pt(9.5)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            r = p.add_run(l_str.replace("**", ""))
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)

    if in_table and table_rows:
        flush_table(table_rows)

    out_local = "docs/tai-lieu/Kê khai mã nguồn.docx"
    doc.save(out_local)
    print(f"[OK] Da tao {out_local}")
    return out_local

def main():
    # 1. Tao Lich su cau lenh.docx
    f_lsc = create_lich_su_cau_lenh_docx()
    # 2. Tao Ke khai ma nguon.docx
    f_kkm = create_ke_khai_ma_nguon_docx()

    # 3. Dong bo vao cac thu muc
    destinations = [
        # MediTrace folder in Downloads
        (f_lsc, r"C:\Users\admin\Downloads\MediTrace\Lịch sử câu lệnh.docx"),
        (f_kkm, r"C:\Users\admin\Downloads\MediTrace\Kê khai mã nguồn.docx"),
        ("NHAT_KY_LOI_NHAC_VA_KHAI_MA_NGUON.docx", r"C:\Users\admin\Downloads\MediTrace\Nhật ký lời nhắc và khai mã nguồn.docx"),
        ("NHAT_KY_MA_NGUON_VA_RA_SOAT_LOI.docx", r"C:\Users\admin\Downloads\MediTrace\Nhật ký mã nguồn và rà soát lỗi.docx"),

        # Desktop
        (f_lsc, r"C:\Users\admin\Desktop\Lịch sử câu lệnh.docx"),
        (f_kkm, r"C:\Users\admin\Desktop\Kê khai mã nguồn.docx"),
        ("NHAT_KY_LOI_NHAC_VA_KHAI_MA_NGUON.docx", r"C:\Users\admin\Desktop\Nhật ký lời nhắc và khai mã nguồn.docx"),
        ("NHAT_KY_MA_NGUON_VA_RA_SOAT_LOI.docx", r"C:\Users\admin\Desktop\Nhật ký mã nguồn và rà soát lỗi.docx"),

        # docs/tai-lieu/
        ("NHAT_KY_LOI_NHAC_VA_KHAI_MA_NGUON.docx", r"docs\tai-lieu\Nhật ký lời nhắc và khai mã nguồn.docx"),
        ("NHAT_KY_MA_NGUON_VA_RA_SOAT_LOI.docx", r"docs\tai-lieu\Nhật ký mã nguồn và rà soát lỗi.docx"),
    ]

    for src, dst in destinations:
        safe_copy(src, dst)

    print("\nHOAN TAT DONG BO VA DOI TEN CAC FILE DOCX CHUAN TIENG VIET KHONG IN HOA!")

if __name__ == "__main__":
    main()
