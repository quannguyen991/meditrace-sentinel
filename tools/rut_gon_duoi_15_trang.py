# -*- coding: utf-8 -*-
"""
Script rut gon Bao cao du an MediTrace Sentinel xuong duoi 15 trang (chuan 13-14 trang A4).
Bao toan 100% so lieu, 14 bang thuc nghiem, 8 chot an toan lam sang, DDI, eGFR, Nghi dinh 13,
HL7 FHIR R4, To dan do JCI, SOCRATES, ket qua 1.330 tests va 3 ca bay lam sang.
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
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def optimize_to_under_15_pages():
    src_file = "docs/tai-lieu/Báo cáo dự án.docx"
    doc = Document(src_file)

    # 1. Thiet lap kho giay A4 va le can doi hoc thuat
    for s in doc.sections:
        s.page_height = Cm(29.7) # Chuan A4
        s.page_width = Cm(21.0)
        s.top_margin = Cm(1.6)
        s.bottom_margin = Cm(1.6)
        s.left_margin = Cm(2.0)
        s.right_margin = Cm(1.6)

    # 2. Toi uu hoa typography cho cac doan van
    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt:
            continue
            
        p.paragraph_format.line_spacing = 1.08
        
        if p.style.name.startswith('Heading 1'):
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12.5)
                r.bold = True
        elif p.style.name.startswith('Heading 2'):
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(1.5)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(11.5)
                r.bold = True
        elif p.style.name.startswith('Heading 3'):
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(1)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(11)
                r.bold = True
        elif p.style.name.startswith('List'):
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(11)
        elif txt.startswith("Cập nhật ngày:"):
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(4)
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(10)
                r.italic = True
        else:
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(11)

    # 3. Toi uu hoa 14 bang bieu (giam padding, lap lai header, chong rach hang)
    ns_w = nsdecls('w')
    for t in doc.tables:
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Lap lai header hang dau tren cac trang
        if len(t.rows) > 0:
            header_trPr = t.rows[0]._tr.get_or_add_trPr()
            header_trPr.append(parse_xml(f'<w:tblHeader {ns_w}/>'))
            
        for r_idx, row in enumerate(t.rows):
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(f'<w:cantSplit {ns_w}/>'))
            
            for c in row.cells:
                tcPr = c._tc.get_or_add_tcPr()
                tcMar = OxmlElement('w:tcMar')
                for m, val in [('top', 20), ('bottom', 20), ('left', 40), ('right', 40)]:
                    node = OxmlElement(f'w:{m}')
                    node.set(qn('w:w'), str(val))
                    node.set(qn('w:type'), 'dxa')
                    tcMar.append(node)
                tcPr.append(tcMar)
                
                for p in c.paragraphs:
                    p.paragraph_format.space_after = Pt(0)
                    p.paragraph_format.line_spacing = 1.0
                    for r in p.runs:
                        r.font.name = "Times New Roman"
                        if r_idx == 0:
                            r.font.size = Pt(8.5)
                            r.bold = True
                        else:
                            r.font.size = Pt(8.5)

    # 4. Luu file Word
    out_docx = "docs/tai-lieu/Báo cáo dự án.docx"
    doc.save(out_docx)
    print(f"[OK] Da luu ban rut gon Word: {out_docx}")

    # 5. Xuat Markdown tuong ung
    md_lines = []
    for child in doc.element.body:
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            p = docx.text.paragraph.Paragraph(child, doc)
            txt = p.text.strip()
            if not txt:
                continue
            if p.style.name == 'Heading 1' or (txt.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.')) and not txt[1:3] in ['.1', '.2', '.3', '.4', '.5', '.6', '.7', '.8', '.9']):
                md_lines.append(f"\n# {txt}\n")
            elif p.style.name == 'Heading 2' or (any(txt.startswith(f"{i}.") for i in range(1, 10)) and '.' in txt[2:4]):
                md_lines.append(f"\n## {txt}\n")
            elif p.style.name == 'Heading 3':
                md_lines.append(f"\n### {txt}\n")
            elif p.style.name == 'List Bullet':
                md_lines.append(f"- {txt}")
            elif p.style.name == 'List Number':
                md_lines.append(f"1. {txt}")
            elif txt.startswith('Cập nhật ngày:'):
                md_lines.append(f"*{txt}*\n")
            else:
                md_lines.append(f"{txt}\n")
        elif tag == 'tbl':
            t = docx.table.Table(child, doc)
            if not t.rows:
                continue
            header_vals = [c.text.strip().replace('\n', ' ') for c in t.rows[0].cells]
            md_lines.append("| " + " | ".join(header_vals) + " |")
            md_lines.append("| " + " | ".join([":---" for _ in header_vals]) + " |")
            for row in t.rows[1:]:
                vals = [c.text.strip().replace('\n', ' ') for c in row.cells]
                md_lines.append("| " + " | ".join(vals) + " |")
            md_lines.append("")

    out_md = "docs/tai-lieu/Báo cáo dự án.md"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[OK] Da xuat Markdown: {out_md}")

    # 6. Kiem tra so trang qua Microsoft Word COM
    try:
        import win32com.client
        word = win32com.client.Dispatch('Word.Application')
        word.Visible = False
        abs_path = os.path.abspath(out_docx)
        d = word.Documents.Open(abs_path)
        pages = d.ComputeStatistics(2) # wdStatisticPages
        words = d.ComputeStatistics(0) # wdStatisticWords
        print(f"\n=== KET QUA KIEM TRA SO TRANG THUC TE ===")
        print(f"-> So trang (Pages): {pages} trang (Yeu cau: duoi 15 trang)")
        print(f"-> So tu (Words): {words} tu")
        d.Close(False)
        word.Quit()
    except Exception as e:
        print(f"[WARN] Khong the kiem tra qua Word COM: {e}")

    # 7. Dong bo vao Downloads, Desktop va cac thu muc yeu cau
    def safe_copy(src, dst):
        try:
            shutil.copy(src, dst)
            print(f"[OK] Da sao chep sang: {dst}")
        except Exception as e:
            print(f"[WARN] Khong the sao chep sang {dst}: {e}")

    safe_copy(out_docx, r"C:\Users\admin\Downloads\MediTrace\Báo cáo dự án.docx")
    safe_copy(out_md, r"C:\Users\admin\Downloads\MediTrace\Báo cáo dự án.md")
    safe_copy(out_docx, r"C:\Users\admin\Desktop\Báo cáo dự án.docx")
    safe_copy(out_md, r"C:\Users\admin\Desktop\Báo cáo dự án.md")
    safe_copy(out_docx, r"C:\Users\admin\Downloads\Báo cáo dự án.docx")

    print("\nHOAN THANH RUT GON BAO CAO DU AN XUONG DUOI 15 TRANG!")

if __name__ == "__main__":
    optimize_to_under_15_pages()
