from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

root = Path(r'D:\Claude\meditrace-ma-nguon')
source = root / 'tai_lieu_on_tap_meditrace.md'
out = root / 'Bo_cau_hoi_tra_loi_ky_thuat_MediTrace_chi_tiet.docx'
doc = Document()
section = doc.sections[0]
section.top_margin = Cm(2.1)
section.bottom_margin = Cm(2.0)
section.left_margin = Cm(2.5)
section.right_margin = Cm(2.2)
styles = doc.styles
normal = styles['Normal']
normal.font.name = 'Arial'
normal.font.size = Pt(10.5)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15
for name, size in [('Title', 21), ('Heading 1', 15), ('Heading 2', 11.5)]:
    style = styles[name]
    style.font.name = 'Arial'
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor(0, 0, 0)
    style.font.bold = True
    style.paragraph_format.space_before = Pt(12 if name == 'Heading 1' else 8)
    style.paragraph_format.space_after = Pt(5)
    style.paragraph_format.keep_with_next = True
header = section.header.paragraphs[0]
header.text = 'MEDITRACE SENTINEL  |  TÀI LIỆU ÔN TẬP KỸ THUẬT'
header.runs[0].font.size = Pt(8)
header.runs[0].font.color.rgb = RGBColor(90, 90, 90)
footer = section.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer.add_run('Trang ')
field = OxmlElement('w:fldSimple')
field.set(qn('w:instr'), 'PAGE')
footer._p.append(field)
for line in source.read_text(encoding='utf-8').splitlines():
    line = line.strip()
    if not line:
        continue
    if line.startswith('# '):
        doc.add_paragraph(line[2:], style='Title')
    elif line.startswith('## '):
        doc.add_paragraph(line[3:], style='Heading 1')
    elif line.startswith('### '):
        doc.add_paragraph(line[4:], style='Heading 2')
    elif line.startswith('• '):
        p = doc.add_paragraph(style='List Bullet')
        p.add_run(line[2:])
    else:
        p = doc.add_paragraph()
        if line.startswith('Trả lời gợi ý: '):
            p.add_run('Trả lời gợi ý: ').bold = True
            p.add_run(line[len('Trả lời gợi ý: '):])
        else:
            p.add_run(line)
doc.core_properties.title = 'Bộ câu hỏi và trả lời kỹ thuật MediTrace Sentinel'
doc.core_properties.subject = 'Tài liệu ôn tập bảo vệ dự án'
doc.save(out)
print(out)
