# -*- coding: utf-8 -*-
import sys
import glob
import docx

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

for f in glob.glob(r'C:\Users\admin\.gemini\antigravity\brain\79213359-464a-4d34-9459-cb3e0e45d19d\.user_uploaded\*.docx'):
    try:
        d = docx.Document(f)
        p0 = d.paragraphs[0].text.strip() if d.paragraphs else ''
        p1 = d.paragraphs[1].text.strip() if len(d.paragraphs) > 1 else ''
        print(f'{f} -> paras={len(d.paragraphs)}, tables={len(d.tables)} | p0="{p0[:50]}" | p1="{p1[:50]}"')
    except Exception as e:
        print(f'{f} -> error: {e}')
