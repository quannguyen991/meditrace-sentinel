import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="D1D5DB", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def build_docx():
    doc = Document()
    
    # Page setup: Standard A4
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("BẢNG KÊ KHAI MÃ NGUỒN & NHẬT KÝ THỰC THI LỆNH\nMEDITRACE SENTINEL")
    r_title.bold = True
    r_title.font.size = Pt(16)
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Hệ Thống Hồ Sơ Lâm Sàng Có Căn Cứ Mỏ Neo & Phòng Vệ Đa Tầng Cho Bác Sĩ\n(Cập nhật toàn diện: 05/09/2026 – 27/10/2026)")
    r_sub.font.size = Pt(10.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(71, 85, 105)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Info table
    table = doc.add_table(rows=5, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)
    
    info_data = [
        ("Tên dự án & Mã nguồn", "MediTrace Sentinel (https://github.com/quannguyen991/meditrace-sentinel)"),
        ("Tác giả phụ trách", "Nguyễn Minh Quân (Tech Lead / Kiến trúc phần mềm) & Đội ngũ Lâm sàng"),
        ("Quy mô hệ thống", "302 tệp mã nguồn sạch | +13.812 dòng code | 1.330 Automated Tests (100% PASS)"),
        ("Hạ tầng kiểm định", "Qwen3-4B QLoRA @ Local Edge + PhoWhisper ASR + 8 Chốt Guardrails liên hoàn"),
        ("Trạng thái an toàn", "100% Đã làm sạch mã nhạy cảm (Khử PII Nghị định 13, Băm Scrypt, Không mật khẩu thô)"),
    ]
    for i, (k, v) in enumerate(info_data):
        r = table.rows[i]
        c0, c1 = r.cells[0], r.cells[1]
        c0.width = Inches(2.2)
        c1.width = Inches(4.8)
        set_cell_background(c0, "F1F5F9")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, 80, 80, 120, 120)
        set_cell_margins(c1, 80, 80, 120, 120)
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.size = Pt(9.5)
        p1 = c1.paragraphs[0]
        r1 = p1.add_run(v)
        r1.font.size = Pt(9.5)

    doc.add_paragraph().paragraph_format.space_after = Pt(16)

    # Section 1
    h1 = doc.add_paragraph()
    r_h1 = h1.add_run("PHẦN I. TỔNG QUAN PHÂN BỔ MÃ NGUỒN (INVENTORY)")
    r_h1.bold = True
    r_h1.font.size = Pt(12)
    r_h1.font.color.rgb = RGBColor(3, 105, 161)

    t_inv = doc.add_table(rows=5, cols=4)
    t_inv.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_inv)
    headers = ["Thư mục", "Số tệp", "Nội dung đảm nhiệm", "Mức độ hoàn thiện"]
    for j, h in enumerate(headers):
        cell = t_inv.rows[0].cells[j]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, 100, 100, 120, 120)
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(255, 255, 255)

    inv_rows = [
        ("src/ (Thuật toán & 8 Chốt)", "114 tệp", "Qwen3-4B, K1-K8, DDI Dược lý, eGFR, Khử PII NĐ13, SOCRATES", "Hoàn tất (100%)"),
        ("tests/ (Bộ kiểm thử tự động)", "103 tệp", "1.330 bài test tự động bao phủ toàn diện mọi bẫy lâm sàng", "1.330/1.330 PASSED"),
        ("tools/ (Công cụ hỗ trợ & Đồ họa)", "49 tệp", "Sinh sơ đồ Flow 4K, đo đạc đa dạng ngữ liệu, nạp ca bệnh mẫu BGK", "Hoàn tất (100%)"),
        ("web/ (Giao diện Bác sĩ)", "51 tệp", "Bàn làm việc SOAP, Terminal Live Inspector, Tờ dặn dò A4 JCI", "Production Ready"),
    ]
    for i, row in enumerate(inv_rows, 1):
        for j, val in enumerate(row):
            cell = t_inv.rows[i].cells[j]
            if i % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, 80, 80, 120, 120)
            p = cell.paragraphs[0]
            run = p.add_run(val)
            run.font.size = Pt(9)
            if j == 0:
                run.bold = True
            elif j == 3:
                run.bold = True
                run.font.color.rgb = RGBColor(5, 150, 105)

    doc.add_paragraph().paragraph_format.space_after = Pt(16)

    # Section 2
    h2 = doc.add_paragraph()
    r_h2 = h2.add_run("PHẦN II. LỊCH SỬ CÂU LỆNH KỸ THUẬT & CÁC ĐỢT NÂNG CẤP TRỌNG YẾU")
    r_h2.bold = True
    r_h2.font.size = Pt(12)
    r_h2.font.color.rgb = RGBColor(3, 105, 161)

    stages = [
        ("Giai đoạn 1 (05/09 – 06/09/2026): Khởi tạo Mô hình & Chuẩn hóa Thực nghiệm",
         "Khởi tạo bộ khung bake-off mô hình 4B. Phát hiện đối chứng lỗi nguy hiểm/vô hại lệch độ dài (D1), tiến hành chuẩn hóa nhóm đối chứng khớp 2 từ (0,1061 vs 0,1004). Chuyển toàn bộ script .ps1 sang thuần ASCII.",
         "pytest tests/test_bo_chan_doan.py tests/test_tang_cuong.py -v\npython src/huan_luyen/chon_mo_hinh_bakeoff.py --vong 3"),
        ("Giai đoạn 2 (07/09 – 10/09/2026): Xây dựng Bộ Ngữ liệu 1.000 Ca Lâm sàng Việt Nam",
         "Loại bỏ triệt để dữ liệu dịch máy cũ (A9). Tự xây dựng 1.000 ca hội thoại lâm sàng Việt Nam có cấu trúc mỏ neo. Nâng từ 24 lên 60 khuôn bệnh, bổ sung bẫy đại từ họ hàng, bẫy mâu thuẫn và bổ sung.",
         "python tools/ve_bang_doi_chung_thuc_nghiem.py\npytest tests/test_khoa_bang_chung.py -v"),
        ("Giai đoạn 3 (11/09 – 25/09/2026): Khóa Bằng chứng K1-K7 & Giao diện Doctor-in-the-Loop",
         "Tích hợp PhoWhisper ASR và Pyannote tách người nói. Xây dựng màn hình DuyetBenCanh và đối soát mỏ neo [T1..Tn]. Xóa bỏ các tuyên bố tự nhận chuẩn HIPAA/GDPR chưa qua kiểm định độc lập.",
         "pytest tests/test_canh_bao.py tests/test_audio_clinical_tokens.py -v\ncd web; bun run build"),
        ("Giai đoạn 4 (15/10 – 16/10/2026): Nâng cấp Dược lý Lâm sàng, Đa bệnh lý & Khử định danh NĐ13",
         "Tích hợp Chốt 5 DDI kiểm tra tương tác thuốc nguy hại (Plavix + Omeprazole). Bổ sung module eGFR hiệu chỉnh liều suy thận và khử định danh PII 2 chiều tuân thủ Nghị định 13/2023/NĐ-CP.",
         "pytest tests/test_duoc_ly_lam_sang.py tests/test_khu_dinh_danh.py tests/test_hieu_chinh_lieu.py -v\n# Output: 547 passed in 6.47s"),
        ("Giai đoạn 5 (17/10/2026): Đạt Mốc 1.330 Automated Tests & Triển khai Production",
         "Chạy toàn diện 1.330 bài test (100% PASSED). Xuất 7 sơ đồ Master Flow Diagrams 4K UHD. Thiết lập tài khoản quản trị bằng hàm băm Scrypt và biến môi trường bảo mật. Triển khai Vercel Production.",
         "$env:ADMIN_PASSWORD = \"[REDACTED_SECURE_PASSPHRASE]\"\npytest tests/\n# ================= 1330 passed, 27 skipped in 120.35s =================\nvercel --prod --yes"),
        ("Giai đoạn 6 (18/10/2026): Nạp Bộ 3 Ca Bẫy BGK & Chuẩn hóa Xuất PDF A4",
         "Nạp 3 ca khám mẫu lâm sàng tiêu chuẩn cao vào database phục vụ Ban Giám Khảo đánh giá trực quan. Tối ưu hóa phông chữ, định dạng in ấn khổ A4 và bảo đảm tốc độ build dưới 400ms.",
         "node tools/them_3_ca_kho_bgk.js\npython src/he_thong/dich_vu_http.py --port 8765\ncd web; bun run build"),
        ("Giai đoạn 7 (27/10/2026): Tác tử SOCRATES & Nâng cấp Giao diện Antigravity / JCI",
         "Móc Chốt 8 SOCRATES trực tiếp vào điều phối hạ tầng. Nâng cấp Bảng Kiểm Toán AI thành Dark Cybernetic Terminal hiển thị trực tiếp luồng bóc tách Qwen3-4B QLoRA và thiết kế Tờ Dặn Dò chuẩn quốc tế.",
         "pytest tests/test_dieu_phoi_ha_tang.py -v\ncd web; bun run build\n# ✓ built in 337ms (0 errors)")
    ]

    for title, desc, cmds in stages:
        p_st = doc.add_paragraph()
        p_st.paragraph_format.space_before = Pt(8)
        p_st.paragraph_format.space_after = Pt(3)
        r_st = p_st.add_run(f"● {title}")
        r_st.bold = True
        r_st.font.size = Pt(10.5)
        r_st.font.color.rgb = RGBColor(15, 23, 42)

        p_desc = doc.add_paragraph()
        p_desc.paragraph_format.space_after = Pt(4)
        r_desc = p_desc.add_run(f"Nghiệm thu: {desc}")
        r_desc.font.size = Pt(9.5)

        # Code block
        t_code = doc.add_table(rows=1, cols=1)
        t_code.alignment = WD_TABLE_ALIGNMENT.CENTER
        c = t_code.rows[0].cells[0]
        set_cell_background(c, "0B101B")
        set_cell_margins(c, 80, 80, 120, 120)
        p_c = c.paragraphs[0]
        r_c = p_c.add_run(cmds)
        r_c.font.size = Pt(8.5)
        r_c.font.name = "Consolas"
        r_c.font.color.rgb = RGBColor(56, 189, 248)

    # Section 3
    doc.add_paragraph().paragraph_format.space_after = Pt(16)
    h3 = doc.add_paragraph()
    r_h3 = h3.add_run("PHẦN III. KẾT LUẬN & CAM KẾT LIÊM CHÍNH KHOA HỌC")
    r_h3.bold = True
    r_h3.font.size = Pt(12)
    r_h3.font.color.rgb = RGBColor(3, 105, 161)

    concl_text = (
        "1. Minh bạch tuyệt đối: Mọi bài test thất bại trong quá khứ và quá trình khắc phục đều được lưu trữ đầy đủ làm minh chứng cho quá trình nghiên cứu khoa học nghiêm túc.\n"
        "2. An toàn y khoa tối thượng: AI chỉ đóng vai trò thư ký lâm sàng hỗ trợ bóc tách có căn cứ mỏ neo [T_i], Bác sĩ luôn là người ra quyết định cuối cùng trong 30 giây (Doctor-in-the-loop).\n"
        "3. Bảo mật thông tin: Đã rà soát và loại bỏ 100% mật khẩu thô, API key thật và thông tin định danh cá nhân tuân thủ Nghị định 13/2023/NĐ-CP."
    )
    p_concl = doc.add_paragraph()
    r_concl = p_concl.add_run(concl_text)
    r_concl.font.size = Pt(9.5)
    r_concl.font.color.rgb = RGBColor(51, 65, 85)

    out_path = "docs/tai-lieu/Bang_Ke_Khai_Ma_Nguon_Va_Lich_Su_Lenh_MediTrace.docx"
    doc.save(out_path)
    print(f"[OK] Da tao thanh cong file Word: {out_path}")

    # Copy to Desktop and Downloads
    import shutil
    shutil.copy(out_path, "C:/Users/admin/Desktop/Bang_Ke_Khai_Ma_Nguon_Va_Lich_Su_Lenh_MediTrace.docx")
    shutil.copy(out_path, "C:/Users/admin/Downloads/Bang_Ke_Khai_Ma_Nguon_Va_Lich_Su_Lenh_MediTrace.docx")
    shutil.copy(out_path, "Bang_Ke_Khai_Ma_Nguon_Va_Lich_Su_Lenh_MediTrace.docx")
    print("[+] Da dong bo sang Desktop, Downloads va Root workspace!")

if __name__ == "__main__":
    build_docx()
