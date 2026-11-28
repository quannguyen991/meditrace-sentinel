# -*- coding: utf-8 -*-
"""
Công cụ xuất Tập Hồ sơ Thực nghiệm Khoa học & Các Bảng Đối chứng Chi tiết sang Word (.docx).
Thiết kế Executive Y khoa: Segoe UI, Bảng màu Navy/Ice-blue/Emerald, Callout chứng thực.
"""

import os
import shutil
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def set_table_borders(table, color="CBD5E1"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="6" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Segoe UI"
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = RGBColor(12, 74, 110) # Navy
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    run.font.name = "Segoe UI"
    run.font.size = Pt(11.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(2, 132, 199) # Sky Blue
    return p

def add_callout(doc, title, text, bg_hex="F0F9FF", border_hex="0284C7"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:left w:val="single" w:sz="20" w:color="{border_hex}"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r_title = p.add_run(f"[{title}] ")
    r_title.font.name = "Segoe UI"
    r_title.font.size = Pt(10)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(12, 74, 110)
    
    r_body = p.add_run(text)
    r_body.font.name = "Segoe UI"
    r_body.font.size = Pt(9.5)
    r_body.font.color.rgb = RGBColor(51, 65, 85)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(2)
    p_after.paragraph_format.space_after = Pt(4)

def build_table(doc, headers, data, highlight_col=None, highlight_row=None):
    tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    
    # Header
    for j, h in enumerate(headers):
        cell = tbl.rows[0].cells[j]
        set_cell_background(cell, "0C4A6E")
        set_cell_margins(cell, 100, 100, 120, 120)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.font.name = "Segoe UI"
        r.font.size = Pt(9)
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    for i, row_vals in enumerate(data):
        row = tbl.rows[i + 1]
        is_hl_row = (highlight_row is not None and i == highlight_row)
        for j, val in enumerate(row_vals):
            cell = row.cells[j]
            bg = "ECFDF5" if is_hl_row else ("F8FAFC" if i % 2 == 0 else "FFFFFF")
            set_cell_background(cell, bg)
            set_cell_margins(cell, 80, 80, 110, 110)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.name = "Segoe UI"
            r.font.size = Pt(8.5)
            if j == 0:
                r.font.bold = True
                r.font.color.rgb = RGBColor(12, 74, 110)
            elif is_hl_row or (highlight_col is not None and j == highlight_col):
                r.font.bold = True
                r.font.color.rgb = RGBColor(16, 185, 129) # Emerald
            else:
                r.font.color.rgb = RGBColor(51, 65, 85)
    
    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_after = Pt(6)

def tao_word_bang_thuc_nghiem():
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)
        section.different_first_page_header_footer = False
        
        header = section.header
        p_head = header.paragraphs[0]
        p_head.text = "MediTrace Sentinel | Tập Hồ sơ Thực nghiệm Khoa học & Các Bảng Đối chứng"
        p_head.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p_head.runs[0].font.name = "Segoe UI"
        p_head.runs[0].font.size = Pt(8.5)
        p_head.runs[0].font.color.rgb = RGBColor(148, 163, 184)
        
        footer = section.footer
        p_foot = footer.paragraphs[0]
        p_foot.text = "Tài liệu Nghiên cứu & Dữ liệu Thực nghiệm Lâm sàng | Bản quyền thuộc về Dự án MediTrace Sentinel"
        p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_foot.runs[0].font.name = "Segoe UI"
        p_foot.runs[0].font.size = Pt(8.5)
        p_foot.runs[0].font.color.rgb = RGBColor(148, 163, 184)

    # Tiêu đề chính
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    r1 = p_title.add_run("TẬP HỒ SƠ THỰC NGHIỆM KHOA HỌC\nVÀ CÁC BẢNG ĐỐI CHỨNG CHI TIẾT")
    r1.font.name = "Segoe UI"
    r1.font.size = Pt(18)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(12, 74, 110)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(12)
    r_sub = p_sub.add_run("Số đo có nguồn và các phần chưa đo, ghi rõ từng mục\nDự án: MediTrace Sentinel — Bản nháp Hồ sơ Lâm sàng Có căn cứ & Phòng vệ An toàn Y khoa")
    r_sub.font.name = "Segoe UI"
    r_sub.font.size = Pt(10.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    add_callout(
        doc,
        "CÁCH ĐỌC TÀI LIỆU NÀY",
        "Chỉ những con số có tệp kết quả đo mới được ghi. Nguồn: README.md mục \"Kết quả đo\", "
        "docs/final/Báo cáo dự án.md mục 4 và thư mục docs/ket-qua/. Mọi số đo là trên dữ liệu MÔ PHỎNG, "
        "so với bộ chấm tự động, chưa có nhãn của người và chưa có hội thoại thật. Phần nào chưa đo thì ghi \"chưa đo\".",
        "F0FDF4", "16A34A"
    )

    # BẢNG 1
    add_heading_1(doc, "BẢNG 1: So sánh ba phương án có cấu trúc (đã đo)")
    add_heading_2(doc, "F1 / SER / tỷ lệ ghi nhầm người trên 4 bộ thử thách — docs/final/Báo cáo dự án.md mục 4.1")
    h1 = ["Bộ thử thách (số ca)", "Chỉ tách thông tin", "+ Xử lý lời sửa", "+ Kiểm bằng chứng (C_khoá)"]
    d1 = [
        ["Đổi chủ thể (80)", "66,1 / 45,4 / 22,0%", "69,2 / 38,2 / 20,0%", "70,8 / 36,9 / 17,9%"],
        ["Đính chính (60)", "80,9 / 29,9 / 7,6%", "85,9 / 17,4 / 6,8%", "87,0 / 17,4 / 5,5%"],
        ["Nhiễu giọng nói (80)", "63,2 / 63,7 / 3,7%", "64,9 / 58,4 / 3,3%", "64,8 / 58,6 / 3,5%"],
        ["Vùng miền (80)", "85,8 / 21,5 / 1,7%", "87,8 / 16,9 / 1,5%", "88,0 / 16,3 / 1,5%"],
    ]
    build_table(doc, h1, d1, highlight_col=3)
    h1b = ["Phép đo khác", "Kết quả", "Nguồn"]
    d1b = [
        ["Thông tin đã bị sửa vẫn còn trong bản nháp (bộ tự sửa 60 ca)", "11,48% → 0,80%", "README.md, Báo cáo dự án mục 4.2"],
        ["Bỏ sót khi thêm kiểm bằng chứng (bộ đổi chủ thể)", "4,5% → 7,7% (tăng)", "Báo cáo dự án mục 4.3"],
        ["Nhánh A sinh thẳng: điểm ghi đúng người (bộ đổi chủ thể)", "0,939 so với 0,748 của pipeline — nhánh A CAO HƠN", "README.md"],
        ["Nhánh A+ (prompt tự soát lỗi)", "Chưa đo", "—"],
        ["Nhánh D (hỏi lại bác sĩ)", "Chưa đo, chưa từng chạy với bác sĩ thật", "—"],
    ]
    build_table(doc, h1b, d1b)
    add_callout(doc, "KẾT LUẬN BẢNG 1",
                "Ở bộ đổi chủ thể, các bước phía sau giảm ghi nhầm người từ 22,0% xuống 17,9% và tăng F1 từ 66,1 lên 70,8. "
                "Ở bộ nhiễu giọng nói gần như không cải thiện. Cách sinh thẳng ghi đúng người cao hơn pipeline, nên dự án không "
                "khẳng định MediTrace chính xác hơn; điểm mạnh là mỗi dòng kiểm tra được về lượt nói gốc. "
                "Chặn nhầm 0/30.136 chỉ đúng vì đáp án chép gần nguyên văn hội thoại (độ phủ 0,95); trên đầu ra mô hình thật, "
                "chặn thừa là 8,0% (C) / 10,0% (D) (docs/ket-qua/canh-bao.json).", "F0F9FF", "0284C7")

    # BẢNG 2
    add_heading_1(doc, "BẢNG 2: So sánh với mô hình thương mại")
    add_heading_2(doc, "Chưa chạy so sánh với mô hình thương mại")
    add_callout(doc, "TRẠNG THÁI",
                "Chưa chạy so sánh với mô hình thương mại. Phép đo duy nhất có thật: mô hình thương mại ghi nhầm người 1,4% "
                "so với 7,6% của mô hình dự án (bộ tự sửa) — mô hình thương mại tốt hơn. Kế hoạch đo: "
                "docs/superpowers/plans/2026-11-27-nang-cap-toan-dien-bgk.md, Task 6.", "FFFBEB", "D97706")
    add_callout(doc, "VỀ DỮ LIỆU CÁ NHÂN",
                "Từ 01/01/2026, dữ liệu cá nhân chịu điều chỉnh của Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 và "
                "Nghị định 356/2025/NĐ-CP. Dự án chạy tại chỗ nên dữ liệu người bệnh không cần rời phòng khám.", "F0F9FF", "0284C7")

    # BẢNG 3
    add_heading_1(doc, "BẢNG 3: Chống nhiễu âm thanh & tên thuốc dân gian")
    add_heading_2(doc, "Chưa đo trên âm thanh thu thực tế")
    add_callout(doc, "TRẠNG THÁI",
                "Chưa có bộ âm thanh phòng khám thật để đo WER. Số đo duy nhất liên quan: bộ thử thách \"nhiễu giọng nói\" 80 ca "
                "(lỗi do chép giọng nói được mô phỏng trên văn bản): F1 63,2 → 64,8, ghi nhầm người 3,7% → 3,5% (Bảng 1). "
                "Cơ chế bôi đỏ tên thuốc dân gian có trong mã và có kiểm thử đơn vị, chưa đo tỷ lệ trên dữ liệu thật.",
                "FFFBEB", "D97706")

    # BẢNG 4
    add_heading_1(doc, "BẢNG 4: Dữ liệu, chia tập và đo lớp cảnh báo")
    add_heading_2(doc, "Số đo từ README.md \"Kết quả đo\" và docs/ket-qua/cay-loi.md")
    h4 = ["Phép đo", "Kết quả", "Ghi chú"]
    d4 = [
        ["Bộ dữ liệu v2", "5.000 hội thoại, 657 khuôn, 21 hệ cơ quan", "Mô phỏng; chia theo khuôn bệnh"],
        ["Tỷ lệ lặp câu", "76,92% (v1) → 47,37% (v2)", "Câu khác nhau 45.835 (+127%)"],
        ["Trích dẫn nguyên văn", "52.634 / 52.634", "Kiểm dữ liệu huấn luyện tự sinh, không phải đầu ra mô hình"],
        ["Bỏ sót mệnh đề (30 ca phát triển, 304 mệnh đề)", "43,1% → 11,5%", "So với bộ chấm tự động, đáp án v1"],
        ["Cấy lỗi: 16 loại cơ bản (400 ca tập điều chỉnh)", "0,801 → 0,871", "Đo khả năng bắt lỗi cố ý cấy"],
        ["Cấy lỗi: tập giữ kín (240 ca, chạy 1 lần)", "0,871; báo nhầm 8,0 cảnh báo/ca sạch", "Lỗi cấy đều đặn hơn lỗi thật"],
        ["Cấy lỗi: 14 loại khó (400 ca)", "0,682 → 0,889", "Số lạc quan: luật vòng 6 chỉ đo trên tập điều chỉnh"],
        ["Lỗi nguy hiểm lọt vào thân, chính sách D", "11,8%", "Tập phát triển đã dùng để chỉnh luật (docs/ket-qua/canh-bao.json)"],
        ["Khái quát hoá theo vùng miền, đa bệnh lý trên 500 ca", "Chưa đo", "—"],
    ]
    build_table(doc, h4, d4)

    # BẢNG 5
    add_heading_1(doc, "BẢNG 5: An toàn dược lý & thang điểm lâm sàng")
    add_heading_2(doc, "Kiểm bằng phép thử đơn vị với ca tự viết, không phải tỷ lệ trên dữ liệu thật")
    h5 = ["Chức năng", "Cách kiểm", "Độ nhạy / độ đặc hiệu trên dữ liệu thật"]
    d5 = [
        ["Trần liều Paracetamol (> 4 g/ngày)", "Phép thử đơn vị (pytest)", "Chưa đo"],
        ["Tương tác thuốc nguy hiểm", "Phép thử đơn vị (pytest)", "Chưa đo"],
        ["Chống chỉ định theo eGFR", "Phép thử đơn vị (pytest)", "Chưa đo"],
        ["Thang điểm CURB-65, CHA2DS2-VASc, HAS-BLED, Child-Pugh...", "Phép thử đơn vị (pytest)", "Chưa đo"],
        ["Tờ dặn dò 4 khung giờ", "Phép thử đơn vị (pytest)", "Chưa đo"],
    ]
    build_table(doc, h5, d5)
    add_callout(doc, "GHI CHÚ BẢNG 5",
                "Toàn bộ kho mã có 1.942 bài pytest qua (README.md, chạy lại 26/11/2026). Bảng tri thức thuốc đi kèm chưa được "
                "chuyên gia duyệt.", "F0FDF4", "16A34A")

    # BẢNG 6
    add_heading_1(doc, "BẢNG 6: Đánh giá bởi bác sĩ (đề xuất, chưa thực hiện)")
    add_heading_2(doc, "Không có dữ liệu bác sĩ nào trong dự án")
    h6 = ["Tiêu chí dự kiến đo", "Kết quả"]
    d6 = [
        ["Thời gian hoàn thành bệnh án (phút/ca)", "Chưa đo"],
        ["Tỷ lệ bác sĩ phát hiện lỗi nguy cơ cao", "Chưa đo"],
        ["Điểm khả dụng SUS", "Chưa đo"],
    ]
    build_table(doc, h6, d6)
    out_name = "Bang_So_Lieu_Thuc_Nghiem_Va_Doi_Chung_Chi_Tiet.docx"
    doc.save(out_name)
    print(f"[OK] Da xuat bao cao Word: {out_name}")
    
    destinations = [
        f"docs/tai-lieu/{out_name}",
        f"C:\\Users\\admin\\Desktop\\Hinh_Flow_MediTrace\\{out_name}",
        f"C:\\Users\\admin\\Desktop\\{out_name}",
        f"C:\\Users\\admin\\Downloads\\hinh_flow_meditrace\\{out_name}",
        f"C:\\Users\\admin\\Downloads\\{out_name}",
    ]
    for d in destinations:
        try:
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(out_name, d)
            print(f"[+] Dong bo: {d}")
        except Exception as e:
            print(f"[-] Loi dong bo {d}: {e}")

if __name__ == "__main__":
    tao_word_bang_thuc_nghiem()
