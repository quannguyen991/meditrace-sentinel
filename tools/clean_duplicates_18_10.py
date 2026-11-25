# -*- coding: utf-8 -*-
"""
Script làm sạch trùng lặp và cố định mốc nghiệm thu chính xác đến ngày 18/10/2026
cho toàn bộ tài liệu Báo cáo dự án MediTrace Sentinel.
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

def clean_and_finalize_18_10():
    doc_path = r'C:\Users\admin\Downloads\MediTrace\Báo cáo dự án.docx'
    doc = Document(doc_path)
    
    # 1. Tìm và xóa các đoạn trùng lặp hoặc chứa mốc 28/10
    # Xóa paragraph trùng lặp
    seen_prefixes = set()
    paras_to_remove = []
    
    for p in doc.paragraphs:
        txt = p.text.strip()
        if not txt:
            paras_to_remove.append(p)
            continue
            
        # Xóa dòng 28/10
        if "28/10/2026" in txt or "27/10/2026" in txt:
            paras_to_remove.append(p)
            continue
            
        # Kiểm tra trùng lặp các heading bổ sung
        if txt.startswith("3.9.") or txt.startswith("3.10.") or txt.startswith("3.11.") or txt.startswith("4.8."):
            prefix = txt[:5]
            if prefix in seen_prefixes:
                paras_to_remove.append(p)
                continue
            seen_prefixes.add(prefix)
            
        # Kiểm tra trùng lặp đoạn tóm tắt bổ sung
        if "Đợt nâng cấp toàn diện tháng 10/2026: Để giải quyết" in txt:
            paras_to_remove.append(p)
            continue
            
        # Kiểm tra trùng lặp đoạn bàn luận / kết luận / hạn chế bổ sung
        if "Đợt nâng cấp tháng 10/2026 đã giải quyết căn cơ" in txt:
            paras_to_remove.append(p)
            continue
            
        if "Bước tiến tháng 10/2026 đưa MediTrace Sentinel" in txt:
            paras_to_remove.append(p)
            continue
            
        if "Ghi nhận đợt nâng cấp tháng 10/2026: Các hạn chế" in txt:
            paras_to_remove.append(p)
            continue

    for p in paras_to_remove:
        p._p.getparent().remove(p._p)
        
    print(f"[OK] Đã xóa {len(paras_to_remove)} đoạn trùng lặp / ngày cũ.")

    # 2. Xóa bảng trùng lặp (nếu có 2 bảng Chốt an toàn)
    guardrail_tables = []
    for t in doc.tables:
        first_cell = t.cell(0, 0).text.strip()
        if first_cell == "Chốt":
            guardrail_tables.append(t)
            
    if len(guardrail_tables) > 1:
        # Giữ bảng đầu tiên, xóa các bảng sau
        for t in guardrail_tables[1:]:
            t._tbl.getparent().remove(t._tbl)
        print(f"[OK] Đã xóa {len(guardrail_tables) - 1} bảng chốt an toàn trùng lặp.")

    # 3. Kiểm tra số lượng paragraphs và tables sau làm sạch
    print(f"Sau làm sạch: {len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables")

    # 4. Xuất Word & Markdown
    out_docx_local = "docs/tai-lieu/Báo cáo dự án.docx"
    doc.save(out_docx_local)
    print(f"[OK] Đã lưu file Word tại: {out_docx_local}")

    # Xuất Markdown
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

    out_md_local = "docs/tai-lieu/Báo cáo dự án.md"
    with open(out_md_local, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[OK] Đã lưu file Markdown tại: {out_md_local}")

    def safe_copy(src, dst):
        try:
            shutil.copy(src, dst)
            print(f"[OK] Đã sao chép sang: {dst}")
        except Exception as e:
            print(f"[WARN] Không thể sao chép sang {dst}: {e}")

    # Đồng bộ sang các thư mục
    safe_copy(out_docx_local, r"C:\Users\admin\Downloads\MediTrace\Báo cáo dự án.docx")
    safe_copy(out_md_local, r"C:\Users\admin\Downloads\MediTrace\Báo cáo dự án.md")
    safe_copy(out_docx_local, r"C:\Users\admin\Desktop\Báo cáo dự án.docx")
    safe_copy(out_md_local, r"C:\Users\admin\Desktop\Báo cáo dự án.md")
    safe_copy(out_docx_local, r"C:\Users\admin\Downloads\Báo cáo dự án.docx")

if __name__ == "__main__":
    clean_and_finalize_18_10()
