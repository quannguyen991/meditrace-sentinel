# -*- coding: utf-8 -*-
from tools.xuat_minh_bach_docx import chuyen


def test_chuyen_tieu_de_bang_va_dau_dong():
    doc = chuyen("# Tiêu đề\n\nĐoạn **đậm** có `mã`.\n\n| A | B |\n|---|---|\n| 1 | 2 |\n\n- ý một\n")
    chu = "\n".join(p.text for p in doc.paragraphs)
    assert "Tiêu đề" in chu and "Đoạn đậm có mã." in chu and "ý một" in chu
    assert len(doc.tables) == 1 and doc.tables[0].cell(1, 1).text == "2"
