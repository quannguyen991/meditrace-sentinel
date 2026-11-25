# -*- coding: utf-8 -*-
import sys
import docx

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\admin\Downloads\MediTrace\Báo cáo dự án.docx'
doc = docx.Document(path)
elements = list(doc.element.body)

print(f"Total body elements: {len(elements)}")
for idx, elem in enumerate(elements):
    tag = elem.tag.split('}')[-1]
    if tag == 'tbl':
        prev_p_text = ""
        for back in range(idx - 1, -1, -1):
            if elements[back].tag.split('}')[-1] == 'p':
                prev_p = docx.text.paragraph.Paragraph(elements[back], doc)
                if prev_p.text.strip():
                    prev_p_text = prev_p.text.strip()
                    break
        t = docx.table.Table(elem, doc)
        headers = [c.text.strip().replace('\n', ' ') for c in t.rows[0].cells[:3]]
        print(f"Table at elem[{idx}]: prev_text='{prev_p_text[:70]}' -> headers={headers}")
