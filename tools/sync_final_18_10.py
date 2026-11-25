# -*- coding: utf-8 -*-
import sys
import os
import shutil
import docx

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr:
    sys.stderr.reconfigure(encoding='utf-8')

src_docx = "docs/tai-lieu/Báo cáo dự án.docx"
doc = docx.Document(src_docx)

# Tạo Markdown
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

src_md = "docs/tai-lieu/Báo cáo dự án.md"
with open(src_md, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))
print(f"[OK] Đã xuất file Markdown: {src_md}")

def safe_copy(src, dst):
    try:
        shutil.copy(src, dst)
        print(f"[OK] Đã sao chép sang: {dst}")
    except Exception as e:
        print(f"[WARN] Không thể sao chép sang {dst}: {e}")

safe_copy(src_docx, r"C:\Users\admin\Downloads\MediTrace\Báo cáo dự án.docx")
safe_copy(src_md, r"C:\Users\admin\Downloads\MediTrace\Báo cáo dự án.md")
safe_copy(src_docx, r"C:\Users\admin\Desktop\Báo cáo dự án.docx")
safe_copy(src_md, r"C:\Users\admin\Desktop\Báo cáo dự án.md")
safe_copy(src_docx, r"C:\Users\admin\Downloads\Báo cáo dự án.docx")

print("\nHOÀN THÀNH ĐỒNG BỘ MỐC CHUẨN 18/10/2026!")
