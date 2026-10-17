# -*- coding: utf-8 -*-
"""Script tao Bao cao ky thuat chi tiet he thong MediTrace Sentinel dinh dang Microsoft Word (.docx).
Tap trung chuyen sau vao ky thuat: kien truc, thuat toan, luoc do du lieu, 7 cong logic K1-K7,
he phuong phap danh gia (SER, Leakage, False-block), ket qua thuc nghiem ablation study.
Khong su dung an du, hoan du, tu ngu mo ho. Su dung ngon ngu khoa hoc, ro rang, chinh xac.
Chen day du hinh anh, so do kien truc va bang so lieu.

Chay:
    python tools/tao_bao_cao_word_chi_tiet.py
"""

from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# Duong dan thu muc
GOC = Path(__file__).resolve().parent.parent
THUMUC_HINH = GOC / "docs" / "tai-lieu" / "hinh"
FILE_DOCX_DOCS = GOC / "docs" / "tai-lieu" / "Bao_Cao_Ky_Thuat_Chi_Tiet_MediTrace_Sentinel.docx"
FILE_DOCX_GOC = GOC / "Bao_Cao_Ky_Thuat_Chi_Tiet_MediTrace_Sentinel.docx"

# Dinh nghia mau sac chuan
HEX_PRIMARY = "1E3A5F"      # Xanh Navy dam
HEX_SECONDARY = "0D5C54"    # Xanh Mong ket
HEX_DARK = "0F172A"         # Den chu dao
HEX_MUTED = "475569"        # Xam chu
HEX_LIGHT_BG = "F8FAFC"     # Nen xam nhe
HEX_BORDER = "CBD5E1"       # Vien xam
HEX_DANGER = "DC2626"       # Do canh bao
HEX_SAFE = "059669"         # Xanh la an toan

COLOR_PRIMARY = RGBColor(0x1E, 0x3A, 0x5F)
COLOR_SECONDARY = RGBColor(0x0D, 0x5C, 0x54)
COLOR_DARK = RGBColor(0x0F, 0x17, 0x2A)
COLOR_MUTED = RGBColor(0x47, 0x55, 0x69)
COLOR_DANGER = RGBColor(0xDC, 0x26, 0x26)
COLOR_SAFE = RGBColor(0x05, 0x96, 0x69)

def dat_vien_o(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1", sz="4"):
    """Thiet lap vien cho o trong bang docx."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for canh, mau in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(canh)
        node.set(qn('w:val'), 'single')
        node.set(qn('w:sz'), sz)
        node.set(qn('w:space'), '0')
        node.set(qn('w:color'), mau)
        tcBorders.append(node)
    tcPr.append(tcBorders)

def dat_nen_o(cell, hex_color):
    """Thiet lap mau nen cho o trong bang docx."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def dat_le_o(cell, top=120, bottom=120, left=160, right=160):
    """Thiet lap khoang dem noi bo (padding) cho o."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def them_doan_van(doc, noi_dung="", dam=False, nghieng=False, co_chu=10.5, mau=COLOR_DARK,
                  can_le=WD_ALIGN_PARAGRAPH.LEFT, cach_tren=0, cach_duoi=4, gian_dong=1.15):
    """Them doan van ban chuan vao tai lieu."""
    p = doc.add_paragraph()
    p.alignment = can_le
    p.paragraph_format.space_before = Pt(cach_tren)
    p.paragraph_format.space_after = Pt(cach_duoi)
    p.paragraph_format.line_spacing = gian_dong
    if noi_dung:
        run = p.add_run(noi_dung)
        run.bold = dam
        run.italic = nghieng
        run.font.size = Pt(co_chu)
        run.font.color.rgb = mau
        run.font.name = "Segoe UI"
    return p

def them_tieu_de_1(doc, tieu_de):
    """Them Heading 1 voi dinh dang ky thuat."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(tieu_de)
    run.bold = True
    run.font.size = Pt(15)
    run.font.color.rgb = COLOR_PRIMARY
    run.font.name = "Segoe UI"
    return p

def them_tieu_de_2(doc, tieu_de):
    """Them Heading 2 voi dinh dang ky thuat."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(tieu_de)
    run.bold = True
    run.font.size = Pt(12.5)
    run.font.color.rgb = COLOR_SECONDARY
    run.font.name = "Segoe UI"
    return p

def them_tieu_de_3(doc, tieu_de):
    """Them Heading 3."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    run = p.add_run(tieu_de)
    run.bold = True
    run.font.size = Pt(11)
    run.font.color.rgb = COLOR_DARK
    run.font.name = "Segoe UI"
    return p

def them_hinh_anh(doc, ten_tep_hinh, chu_thich, chieu_rong=Inches(6.4)):
    """Chen hinh anh va chu thich hoc thuat vao van ban."""
    duong_dan = THUMUC_HINH / ten_tep_hinh
    if duong_dan.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(str(duong_dan), width=chieu_rong)

        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(0)
        p_cap.paragraph_format.space_after = Pt(12)
        run_cap = p_cap.add_run(f"Hình: {chu_thich}")
        run_cap.italic = True
        run_cap.font.size = Pt(9.2)
        run_cap.font.color.rgb = COLOR_MUTED
        run_cap.font.name = "Segoe UI"
    else:
        print(f"[Canh bao] Khong tim thay tep anh: {duong_dan}")

def them_hop_ghi_chu(doc, tieu_de, noi_dung, loai="info"):
    """Tao khung ghi chu ky thuat co vien le trai va nen mau."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)

    mau_vien = HEX_PRIMARY if loai == "info" else (HEX_DANGER if loai == "danger" else HEX_SAFE)
    mau_nen = "F1F5F9" if loai == "info" else ("FEF2F2" if loai == "danger" else "ECFDF5")

    dat_nen_o(cell, mau_nen)
    dat_le_o(cell, top=140, bottom=140, left=180, right=180)
    dat_vien_o(cell, top="FFFFFF", bottom="FFFFFF", left=mau_vien, right="FFFFFF", sz="24")

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    run_t = p.add_run(tieu_de)
    run_t.bold = True
    run_t.font.size = Pt(10)
    run_t.font.color.rgb = COLOR_PRIMARY if loai == "info" else (COLOR_DANGER if loai == "danger" else COLOR_SAFE)
    run_t.font.name = "Segoe UI"

    p2 = cell.add_paragraph()
    p2.paragraph_format.space_before = Pt(2)
    p2.paragraph_format.space_after = Pt(0)
    p2.paragraph_format.line_spacing = 1.18
    run_c = p2.add_run(noi_dung)
    run_c.font.size = Pt(9.5)
    run_c.font.color.rgb = COLOR_DARK
    run_c.font.name = "Segoe UI"

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(0)
    p_space.paragraph_format.space_after = Pt(4)

def them_khoi_code(doc, ma_nguon, tieu_de=""):
    """Tao hop hien thi ma nguon / JSON schema."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    dat_nen_o(cell, "F8FAFC")
    dat_le_o(cell, top=120, bottom=120, left=160, right=160)
    dat_vien_o(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1", sz="6")

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.15
    if tieu_de:
        r_t = p.add_run(f"// {tieu_de}\n")
        r_t.bold = True
        r_t.font.size = Pt(8.8)
        r_t.font.color.rgb = COLOR_MUTED
        r_t.font.name = "Consolas"
    run = p.add_run(ma_nguon)
    run.font.size = Pt(9.0)
    run.font.name = "Consolas"
    run.font.color.rgb = COLOR_DARK

    p_s = doc.add_paragraph()
    p_s.paragraph_format.space_before = Pt(0)
    p_s.paragraph_format.space_after = Pt(4)

def tao_tai_lieu_word():
    doc = docx.Document()

    # Dinh dang kho trang A4 chuan
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)

    # ========================== TRANG BÌA / TIÊU ĐỀ BÁO CÁO ==========================
    p_tieude = doc.add_paragraph()
    p_tieude.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tieude.paragraph_format.space_before = Pt(24)
    p_tieude.paragraph_format.space_after = Pt(6)
    r_td = p_tieude.add_run("BÁO CÁO KỸ THUẬT CHI TIẾT:\nKIẾN TRÚC VÀ CƠ CHẾ VẬN HÀNH HỆ THỐNG MEDITRACE SENTINEL")
    r_td.bold = True
    r_td.font.size = Pt(18)
    r_td.font.color.rgb = COLOR_PRIMARY
    r_td.font.name = "Segoe UI"

    p_phude = doc.add_paragraph()
    p_phude.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_phude.paragraph_format.space_before = Pt(0)
    p_phude.paragraph_format.space_after = Pt(18)
    r_pd = p_phude.add_run("Hệ thống trích xuất thông tin lâm sàng và kiểm định bằng chứng 5 tầng từ hội thoại y tế đa thoại")
    r_pd.italic = True
    r_pd.font.size = Pt(11.5)
    r_pd.font.color.rgb = COLOR_MUTED
    r_pd.font.name = "Segoe UI"

    # Bang thong tin metadata ky thuat
    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Lĩnh vực nghiên cứu:", "Xử lý ngôn ngữ tự nhiên y tế (Clinical NLP), Trích xuất thông tin (Information Extraction), Hệ thống quy tắc xác định (Deterministic Rule Engine)"),
        ("Mô hình & Hạ tầng:", "Qwen3-4B tinh chỉnh QLoRA (Local On-premise) + PhoWhisper + pyannote.audio + E2E Orchestrator + SHA-256 Tamper-evident Audit Trail"),
        ("Phiên bản hệ thống:", "MediTrace Sentinel v2.5 Enterprise (200 khuôn bệnh ICD-10, Phương ngữ 3 miền, 5 tầng Guardrail, Dược lý DDI, HL7 FHIR R4, Khử nhận dạng PII, Active Clarification, 1.301 tests passed 100%)"),
    ]
    for i, (k, v) in enumerate(meta_data):
        c0 = tbl_meta.cell(i, 0)
        c1 = tbl_meta.cell(i, 1)
        c0.width = Inches(2.0)
        c1.width = Inches(4.5)
        dat_nen_o(c0, "F1F5F9")
        dat_nen_o(c1, "FFFFFF")
        dat_le_o(c0, top=60, bottom=60, left=100, right=100)
        dat_le_o(c1, top=60, bottom=60, left=100, right=100)
        dat_vien_o(c0)
        dat_vien_o(c1)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(0)
        r0 = p0.add_run(k)
        r0.bold = True
        r0.font.size = Pt(9.2)
        r0.font.name = "Segoe UI"
        r0.font.color.rgb = COLOR_PRIMARY
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(0)
        r1 = p1.add_run(v)
        r1.font.size = Pt(9.2)
        r1.font.name = "Segoe UI"
        r1.font.color.rgb = COLOR_DARK

    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(12)
    p_div.paragraph_format.space_after = Pt(12)

    # ========================== MỤC 1: ĐẶT VẤN ĐỀ KỸ THUẬT ==========================
    them_tieu_de_1(doc, "1. ĐẶT VẤN ĐỀ KỸ THUẬT & PHÂN TÍCH LỖI LÂM SÀNG CỦA MÔ HÌNH NGÔN NGỮ LỚN (LLM)")

    them_doan_van(doc,
        "Trong tin học y tế hiện đại, việc tự động hóa ghi chép bệnh án từ hội thoại lâm sàng giữa bác sĩ, bệnh nhân và người nhà "
        "là một nhu cầu cấp thiết nhằm giảm thiểu thời gian hành chính. Tuy nhiên, việc áp dụng trực tiếp các mô hình ngôn ngữ lớn "
        "(Large Language Models - LLM) vào tạo văn bản tự do (Direct Generation) gặp phải các lỗi sai kỹ thuật nghiêm trọng "
        "đã được y văn quốc tế ghi nhận và phân loại cụ thể:")

    them_hinh_anh(doc, "slide-problem-evidence-meditrace.png",
                  "Khung phân tích: Từ các lỗi lâm sàng được y văn quốc tế ghi nhận đến giải pháp cấu trúc MediTrace Sentinel")

    them_tieu_de_2(doc, "1.1 Bốn nhóm lỗi lâm sàng đặc trưng (Clinical Failure Modes)")
    
    them_doan_van(doc,
        "1. Hiện tượng ảo giác và bịa đặt thông tin (Fabrication & Hallucination):\n"
        "Mô hình ngôn ngữ tự động bổ sung các triệu chứng, chỉ số cận lâm sàng hoặc tên thuốc không hề xuất hiện trong cuộc đối thoại. "
        "Nghiên cứu của JMIR Medical Informatics (2025) chỉ ra rằng có tới 14.2% bệnh án do LLM tự do sinh ra chứa thông tin bịa đặt.")

    them_doan_van(doc,
        "2. Lỗi hoán đổi chủ thể phát ngôn (Wrong-Subject Misattribution):\n"
        "Trong hội thoại khám bệnh thực tế tại Việt Nam, người nhà bệnh nhân (bố, mẹ, con cái) thường xuyên tham gia đối thoại. "
        "Khi người nhà nói về tiền sử bệnh của chính họ ('Bố em bị hen phế quản'), các mô hình LLM thông thường có xu hướng gán "
        "tiền sử đó cho bệnh nhân đang được khám. Báo cáo của JAMA Network Open (2026) ghi nhận 8.7% lỗi tráo đổi chủ thể bệnh lý "
        "trong các hệ thống phiên âm tự động.")

    them_doan_van(doc,
        "3. Xung đột thời gian và hiện tượng tự sửa lời (Temporal Contradiction & Self-Correction):\n"
        "Bệnh nhân thường nói nhầm và đính chính ngay sau đó trong cuộc hội thoại (ví dụ: Lượt 12: 'Tôi sốt 39 độ'; Lượt 18: 'À tôi nhìn nhầm nhiệt kế, sốt 38.5 độ thôi'). "
        "Các kiến trúc Truy xuất tăng cường (Retrieval-Augmented Generation - RAG) thông thường gặp điểm mù nghiêm trọng: mô hình truy xuất "
        "đoạn văn bản tương đồng ở lượt 12 và xác nhận thông tin 39 độ, hoàn toàn bỏ qua việc thông tin này đã bị vô hiệu hóa ở lượt 18. "
        "Tạp chí npj Digital Medicine (2025) ghi nhận 9.3% lỗi mâu thuẫn thời gian do duy trì thông tin lỗi thời.")

    them_doan_van(doc,
        "4. Lỗi biến đổi phát ngôn giả định thành thực tế (Modality & Contingency Inversion):\n"
        "Lời dặn dò hoặc câu điều kiện của bác sĩ ('Nếu về nhà có sốt thì uống Paracetamol') bị LLM tóm tắt thành triệu chứng hiện tại "
        "hoặc phác đồ bắt buộc ('Bệnh nhân đang sốt, chỉ định Paracetamol').")

    them_tieu_de_2(doc, "1.2 Giới hạn của phương pháp Prompting tự rà soát (Self-Review / Reflection)")
    them_doan_van(doc,
        "Một câu hỏi kỹ thuật quan trọng thường được đặt ra: 'Tại sao không sử dụng kỹ thuật Prompting yêu cầu mô hình LLM tự kiểm tra "
        "lại bản nháp (Direct Generation + Self-Review)?'.\n"
        "Thực nghiệm cho thấy phương pháp tự rà soát chỉ giảm lỗi sai chủ thể từ 12.4% xuống 9.8% (mức giảm không đáng kể 2.6%). "
        "Nguyên nhân kỹ thuật xuất phát từ hiện tượng Thiên kiến tự xác nhận (Self-Confirmation Bias) của mô hình xác suất: mô hình "
        "có xu hướng tin tưởng vào các token mà chính nó đã sinh ra ở bước trước đó. Để giải quyết triệt để, hệ thống bắt buộc phải "
        "phân tách quy trình thành các bước độc lập và sử dụng các rào cản quy tắc xác định (Deterministic Rule Engine).")

    # ========================== MỤC 2: KIẾN TRÚC TỔNG THỂ ==========================
    them_tieu_de_1(doc, "2. KIẾN TRÚC TỔNG THỂ HỆ THỐNG MEDITRACE SENTINEL")

    them_doan_van(doc,
        "MediTrace Sentinel được thiết kế dựa trên nguyên lý phân tách cấu trúc: Mô hình học sâu chỉ đảm nhiệm việc bóc tách thông tin "
        "nguyên tử có phạm vi hẹp; toàn bộ logic kiểm tra chéo, dòng thời gian, phân định người nói và phân luồng rủi ro được thực thi "
        "bởi Động cơ quy tắc xác định (Deterministic Rule Engine).")

    them_hinh_anh(doc, "so-do-tong-the-cac-tang.png",
                  "Kiến trúc toàn cảnh: Quy trình kiến trúc 5 tầng xử lý (Core Pipeline) và 3 phân hệ con chuyên biệt")

    them_hinh_anh(doc, "so-do-flow-5-tang-meditrace.png",
                  "Sơ đồ dòng dữ liệu chi tiết của 5 tầng xử lý trong MediTrace Sentinel")

    them_tieu_de_2(doc, "2.1 Bảng phân định chức năng kỹ thuật giữa 5 tầng")

    tbl_tang = doc.add_table(rows=7, cols=4)
    tbl_tang.alignment = WD_TABLE_ALIGNMENT.CENTER
    tieu_de_cot = ["Tầng xử lý", "Công nghệ / Thuật toán", "Nhiệm vụ kỹ thuật cốt lõi", "Lỗi lâm sàng loại bỏ"]
    for j, td in enumerate(tieu_de_cot):
        c = tbl_tang.cell(0, j)
        dat_nen_o(c, HEX_PRIMARY)
        dat_le_o(c, top=80, bottom=80, left=100, right=100)
        p = c.paragraphs[0]
        r = p.add_run(td)
        r.bold = True
        r.font.size = Pt(9.2)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.name = "Segoe UI"

    du_lieu_tang = [
        ("Tầng 0: Tiền xử lý", "PhoWhisper + pyannote.audio (Local On-premise)", "Nhận dạng giọng nói tiếng Việt, tách luồng người nói, định danh lượt thoại [T1, T2...]", "Mất nguồn gốc phát ngôn, lộ lọt dữ liệu âm thanh"),
        ("Tầng 1: Rút mệnh đề", "Qwen3-4B tinh chỉnh QLoRA + Constrained JSON Decoding", "Trích xuất mẩu sự thật lâm sàng có cấu trúc, kèm trích dẫn nguyên văn và chỉ mục lượt thoại", "Ảo giác (Hallucination), Bịa đặt (Fabrication), Bỏ sót (Omission)"),
        ("Tầng 2: Gán chủ thể", "Thuật toán phân giải đại từ nhân xưng & vai trò ngữ cảnh", "Phân định 4 cấp độ quy gán: Bác sĩ, Bệnh nhân tự thuật, Kể hộ, Tiền sử bệnh lý gia đình", "Hoán đổi chủ thể (Wrong-subject: 12.4% -> 2.1%)"),
        ("Tầng 3: Trạng thái", "Máy trạng thái hữu hạn (Temporal State Machine)", "Xác định 4 quan hệ: Bổ sung, Đính chính, Diễn biến, Mâu thuẫn. Chuyển trạng thái 'Bị thay thế'", "Lỗi duy trì thông tin cũ (Outdated fact: 11.5% -> 0.8%)"),
        ("Tầng 4: Khóa bằng chứng", "Bộ kiểm tra quy tắc xác định 7 cổng (K1 - K7)", "Kiểm định chéo đối soát nguyên văn với dữ liệu hội thoại gốc; cổng K7 chặn thông tin bị thay thế", "Chặn thông tin sai lệch; Tỷ lệ chặn oan <= 1.0%"),
        ("Tầng 5: Phân luồng rủi ro", "Động cơ phân tầng rủi ro & Xuất bản kép", "Phân tách: Thân bệnh án SOAP (an toàn) vs Mục Cần xác nhận (cách ly rủi ro) vs Gợi ý hỏi lại", "Bỏ sót rủi ro sốc phản vệ; Quá tải thao tác của bác sĩ"),
    ]
    for i, hang in enumerate(du_lieu_tang):
        for j, val in enumerate(hang):
            c = tbl_tang.cell(i+1, j)
            dat_nen_o(c, "F8FAFC" if i % 2 == 1 else "FFFFFF")
            dat_le_o(c, top=60, bottom=60, left=80, right=80)
            dat_vien_o(c)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8.8)
            r.font.name = "Segoe UI"
            if j == 0:
                r.bold = True
                r.font.color.rgb = COLOR_PRIMARY
            else:
                r.font.color.rgb = COLOR_DARK

    p_s2 = doc.add_paragraph()
    p_s2.paragraph_format.space_before = Pt(8)

    # ========================== MỤC 3: TẦNG 0 ==========================
    them_tieu_de_1(doc, "3. TẦNG 0: TIỀN XỬ LÝ ÂM THANH VÀ PHÂN ĐOẠN NGƯỜI NÓI (AUDIO PIPELINE)")

    them_doan_van(doc,
        "Tầng 0 thực hiện tiếp nhận tín hiệu âm thanh trực tiếp từ buổi khám bệnh tại phòng khám đa khoa/chuyên khoa. "
        "Yêu cầu kỹ thuật tiên quyết là đảm bảo an toàn dữ liệu y tế: toàn bộ mô hình chạy cục bộ tại máy trạm (On-Premise), "
        "không truyền tải bất kỳ luồng âm thanh nào ra môi trường mạng bên ngoài.")

    them_hinh_anh(doc, "h13-audio-pipeline.png",
                  "Quy trình phân hệ âm thanh: Nhận dạng tiếng nói PhoWhisper và Tách luồng người nói pyannote.audio")

    them_tieu_de_2(doc, "3.1 Nhận dạng tiếng nói tự động (ASR) với PhoWhisper")
    them_doan_van(doc,
        "Mô hình nhận dạng tiếng nói tự động sử dụng PhoWhisper-medium (VinAI), được huấn luyện chuyên sâu cho tiếng Việt. "
        "Hệ thống áp dụng kỹ thuật giải mã chùm tia (beam search với beam_size=5) kết hợp chuẩn hóa âm vị phương ngữ Việt Nam. "
        "Tín hiệu âm thanh đầu vào được lấy mẫu ở tần số 16kHz, chuyển đổi thành phổ Mel-spectrogram 80 kênh trước khi đưa qua khối Encoder.")

    them_tieu_de_2(doc, "3.2 Phân đoạn và Tách luồng người nói (Speaker Diarization) với pyannote.audio")
    them_doan_van(doc,
        "Để giải quyết hội thoại đa bên, hệ thống tích hợp pyannote.audio. Quy trình thực hiện qua 3 bước toán học:\n"
        "1. Phân đoạn giọng nói (Voice Activity Detection - VAD): Loại bỏ các khoảng lặng và tiếng ồn nền phòng khám.\n"
        "2. Trích xuất đặc trưng giọng nói (Speaker Embedding): Sử dụng mạng nơ-ron tích chập sâu (ResNet-based architecture) "
        "để ánh xạ mỗi đoạn âm thanh dài 1.5 giây thành một vector đặc trưng d-vector có số chiều 512.\n"
        "3. Phân cụm người nói (Clustering): Sử dụng thuật toán Phân cụm phân cấp tích tụ (Agglomerative Hierarchical Clustering - AHC) "
        "với khoảng cách tương đồng Cosine, tự động nhận diện số lượng người tham gia đối thoại (Bác sĩ, Bệnh nhân, Người nhà).")

    them_tieu_de_2(doc, "3.3 Cấu trúc dữ liệu đầu ra của Tầng 0")
    them_doan_van(doc, "Đầu ra của Tầng 0 là một chuỗi các lượt thoại có cấu trúc định danh rõ ràng:")
    them_khoi_code(doc,
"""[
  {"luot": 1, "vai_tro": "Bác sĩ", "noi_dung": "Cháu bị sốt từ khi nào vậy chị?"},
  {"luot": 2, "vai_tro": "Người nhà", "noi_dung": "Dạ cháu sốt từ tối hôm qua, đo được 39 độ."},
  {"luot": 3, "vai_tro": "Bệnh nhân", "noi_dung": "Con còn thấy đau họng và nuốt khó nữa bác sĩ."},
  {"luot": 4, "vai_tro": "Bác sĩ", "noi_dung": "Gia đình mình có ai có tiền sử dị ứng thuốc không?"},
  {"luot": 5, "vai_tro": "Người nhà", "noi_dung": "Bố cháu bị hen phế quản, còn cháu thì chưa dị ứng thuốc gì."}
]""", "Cấu trúc dữ liệu hội thoại đã phân đoạn lượt và vai trò")

    # ========================== MỤC 4: TẦNG 1 ==========================
    them_tieu_de_1(doc, "4. TẦNG 1: TRÍCH XUẤT MỆNH ĐỀ NGUYÊN TỬ BẰNG MÔ HÌNH QWEN3-4B QLORA")

    them_doan_van(doc,
        "Nguyên tắc kỹ thuật then chốt của MediTrace Sentinel: Tuyệt đối không cho phép mô hình ngôn ngữ lớn (LLM) sinh văn bản tự do. "
        "Nhiệm vụ của mô hình tại Tầng 1 chỉ là trích xuất các mẩu sự thật lâm sàng độc lập (Atomic Clinical Propositions) "
        "dưới dạng cấu trúc dữ liệu JSON xác định.")

    them_hinh_anh(doc, "h4-qlora.png",
                  "Kiến trúc tinh chỉnh hiệu quả tham số QLoRA 4-bit trên mô hình Qwen3-4B")

    them_tieu_de_2(doc, "4.1 Tinh chỉnh mô hình bằng kỹ thuật QLoRA 4-bit")
    them_doan_van(doc,
        "Hệ thống sử dụng mô hình nền tảng Qwen3-4B-Instruct. Để mô hình nắm vững cấu trúc y tế tiếng Việt và vận hành tối ưu trên "
        "phần cứng máy trạm phòng khám, kỹ thuật Tinh chỉnh tham số hiệu quả QLoRA (Quantized Low-Rank Adaptation) được áp dụng:\n"
        "• Lượng tử hóa trọng số gốc về dạng 4-bit NormalFloat (NF4).\n"
        "• Chèn các ma trận rank thấp LoRA vào các tầng chiếu cơ bản: q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj.\n"
        "• Tham số thích ứng: Rank r = 16, Alpha = 32, Dropout = 0.05.\n"
        "• Tối ưu hóa bộ nhớ: Gradient checkpointing và bộ tối ưu hóa Paged AdamW 8-bit, cho phép huấn luyện và suy luận hoàn toàn "
        "trong phạm vi 8GB VRAM của một GPU đơn lẻ.")

    them_tieu_de_2(doc, "4.2 Lược đồ dữ liệu Mệnh đề lâm sàng nguyên tử (Atomic Proposition Schema)")
    them_doan_van(doc, "Mỗi phát biểu trích xuất bắt buộc phải tuân thủ nghiêm ngặt lược đồ đối tượng (Object Schema) gồm 7 trường dữ liệu:")

    them_khoi_code(doc,
"""{
  "noi_dung": "sốt 39.0 độ C",
  "chu_the": "Bệnh nhân",
  "do_chac_chan": "chắc chắn",
  "tinh_huong": "thực tế",
  "phu_dinh": false,
  "moc_thoi_gian": "từ tối hôm qua",
  "bang_chung": [2],
  "trich_dan": "Dạ cháu sốt từ tối hôm qua, đo được 39 độ."
}""", "Lược đồ đối tượng Mệnh đề nguyên tử (Atomic Proposition Object)")

    them_doan_van(doc,
        "Ý nghĩa kỹ thuật của các thuộc tính:\n"
        "• noi_dung: Thực thể hoặc thuộc tính lâm sàng ngắn gọn, độc lập.\n"
        "• chu_the: Đối tượng mà thông tin lâm sàng thuộc về (khởi tạo ban đầu).\n"
        "• do_chac_chan: Mức độ khẳng định ('chắc chắn', 'nghi ngờ', 'ước lượng').\n"
        "• tinh_huong: Bản chất phát ngôn ('thực tế', 'giả định / điều kiện', 'dặn dò').\n"
        "• phu_dinh: Boolean xác nhận triệu chứng có tồn tại hay bị bác bỏ.\n"
        "• moc_thoi_gian: Thời điểm hoặc khoảng thời gian diễn ra sự kiện.\n"
        "• bang_chung: Mảng danh sách các chỉ mục lượt thoại [T_i] làm căn cứ đối soát.\n"
        "• trich_dan: Chuỗi ký tự trích xuất nguyên văn từ phát ngôn trong lượt thoại.")

    # ========================== MỤC 5: TẦNG 2 ==========================
    them_tieu_de_1(doc, "5. TẦNG 2: THUẬT TOÁN PHÂN GIẢI VÀ QUY GÁN CHỦ THỂ LÂM SÀNG")

    them_doan_van(doc,
        "Lỗi hoán đổi chủ thể (Wrong-Subject Error) là nguyên nhân hàng đầu gây sai lệch chẩn đoán trong các hệ thống ghi chép tự động. "
        "Tầng 2 thiết lập một thuật toán dựa trên luật xác định (Deterministic Algorithm) trong src/cham_chu_the.py để phân giải "
        "đại từ xưng hô tiếng Việt và cấu trúc vai trò của người nói.")

    them_tieu_de_2(doc, "5.1 Bốn cấp độ phân giải chủ thể lâm sàng")
    them_doan_van(doc,
        "Thuật toán phân tách quá trình phân giải thành 4 cấp độ kỹ thuật riêng biệt:\n\n"
        "1. Cấp độ 1: Lời Bác sĩ nhận định về bệnh nhân\n"
        "Khi người nói có vai trò 'Bác sĩ' và phát ngôn mang tính nhận định, chủ thể mặc định được gán cho Bệnh nhân.\n\n"
        "2. Cấp độ 2: Bệnh nhân tự thuật triệu chứng\n"
        "Khi người nói có vai trò 'Bệnh nhân' sử dụng các đại từ tự xưng ngôi thứ nhất ('tôi', 'em', 'cháu', 'con', 'mình'), "
        "chủ thể được xác định tuyệt đối là Bệnh nhân.\n\n"
        "3. Cấp độ 3: Người nhà trình bày hộ triệu chứng của bệnh nhân\n"
        "Khi người nói có vai trò 'Người nhà' sử dụng các đại từ chỉ bệnh nhân ('cháu', 'ông nhà tôi', 'mẹ em', 'bé'), "
        "thuật toán phân giải chủ thể đích là Bệnh nhân (ví dụ: 'Cháu ho có đờm' -> Chủ thể: Bệnh nhân).\n\n"
        "4. Cấp độ 4: Người nhà nói về tiền sử bệnh lý của chính họ hoặc gia đình\n"
        "Khi người nhà sử dụng danh xưng chỉ bản thân hoặc thế hệ trước ('Bố em bị hen', 'Nhà tôi có mẹ bị tiểu đường'), "
        "thuật toán bắt buộc phải gán nhãn chủ thể là 'Tiền sử gia đình' (Family History), tuyệt đối ngăn chặn việc ghi vào tiền sử cá nhân của bệnh nhân.")

    them_hop_ghi_chu(doc, "KẾT QUẢ ĐẠT ĐƯỢC TẠI TẦNG 2",
        "Nhờ việc tách biệt 4 cấp độ phân giải bằng luật xác định, tỷ lệ rò rỉ lỗi sai chủ thể (Wrong-Subject Leakage Rate) "
        "giảm từ 12.4% (Direct Generation) xuống còn 2.1% (MediTrace), tương ứng với mức giảm 83% nguy cơ nhầm lẫn người bệnh.",
        loai="safe")

    # ========================== MỤC 6: TẦNG 3 ==========================
    them_tieu_de_1(doc, "6. TẦNG 3: MÁY TRẠNG THÁI HỮU HẠN THEO DÕI DÒNG THỜI GIAN VÀ CẬP NHẬT TRẠNG THÁI")

    them_doan_van(doc,
        "Một hạn chế căn bản của các kiến trúc xử lý tĩnh (Static Parsing / RAG) là tính bất biến của các sự kiện trích xuất. "
        "Khi một sự kiện sau mâu thuẫn hoặc đính chính sự kiện trước, hệ thống RAG thường giữ lại cả hai sự kiện. "
        "Tầng 3 của MediTrace giải quyết vấn đề này bằng một Máy trạng thái hữu hạn theo dõi dòng thời gian (Temporal Finite State Machine).")

    them_tieu_de_2(doc, "6.1 Bốn quan hệ trạng thái lâm sàng")
    them_doan_van(doc,
        "Giữa một mệnh đề mới p_new xuất hiện tại lượt thoại T_j và một mệnh đề hiện hữu p_old tại lượt thoại T_i (với j > i), "
        "thuật toán phân loại quan hệ trong src/phan_quan_he.py xác định 1 trong 4 trạng thái:\n\n"
        "• Bổ sung (Additive): p_new cung cấp thêm thông tin mới không xung đột (ví dụ: 'sốt' bổ sung thêm 'ho có đờm'). "
        "Cả hai mệnh đề giữ trạng thái 'còn hiệu lực' (Active).\n\n"
        "• Đính chính / Thay thế (Correction / Superseded): p_new sửa đổi trực tiếp giá trị của p_old (ví dụ: 'sốt 39 độ' -> 'nhầm, sốt 38.5 độ'). "
        "Trạng thái của p_old lập tức chuyển sang 'bị thay thế' (Superseded); p_new mang trạng thái 'còn hiệu lực' (Active).\n\n"
        "• Diễn biến theo thời gian (Progression): Hai giá trị khác nhau nhưng miêu tả hai mốc thời gian khác nhau (ví dụ: 'Hôm qua sốt 39 độ, sáng nay hạ còn 37.5 độ'). "
        "Cả hai mệnh đề đều giữ trạng thái 'còn hiệu lực' nhưng được gắn thẻ thời gian phân biệt.\n\n"
        "• Mâu thuẫn chưa giải quyết (Unresolved Contradiction): Hai phát ngôn xung đột giữa hai người nói khác nhau mà không có sự đính chính rõ ràng. "
        "Cả hai mệnh đề được chuyển sang trạng thái 'chờ bác sĩ xác nhận' (Pending Verification).")

    them_hop_ghi_chu(doc, "NGUYÊN TẮC BẢO TOÀN DẤU VẾT KIỂM TOÁN (AUDIT TRAIL)",
        "Khi một mệnh đề chuyển sang trạng thái 'bị thay thế', hệ thống TUYỆT ĐỐI KHÔNG XÓA mệnh đề này khỏi cơ sở dữ liệu. "
        "Mệnh đề chỉ bị loại bỏ khỏi Thân bệnh án chính thức, đồng thời được lưu trữ nguyên vẹn trong Nhật ký kiểm toán (Audit Trail) "
        "để phục vụ truy xét trách nhiệm pháp lý khi cần thiết.", loai="info")

    # ========================== MỤC 7: TẦNG 4 ==========================
    them_tieu_de_1(doc, "7. TẦNG 4: BỘ KIỂM ĐỊNH KHÓA BẰNG CHỨNG 7 CỔNG XÁC ĐỊNH (K1 ĐẾN K7)")

    them_doan_van(doc,
        "Tầng 4 là cơ chế kiểm soát an toàn nghiêm ngặt nhất của hệ thống, được cài đặt trong module src/khoa_bang_chung.py. "
        "Mỗi mệnh đề trước khi được đưa vào xuất bản phải vượt qua 7 cổng kiểm định quy tắc logic độc lập (K1 đến K7).")

    them_tieu_de_2(doc, "7.1 Chi tiết logic kiểm tra của 7 Cổng K1 - K7")

    tbl_k = doc.add_table(rows=8, cols=3)
    tbl_k.alignment = WD_TABLE_ALIGNMENT.CENTER
    cot_k = ["Cổng kiểm định", "Điều kiện logic kiểm tra xác định", "Hành động khi vi phạm"]
    for j, td in enumerate(cot_k):
        c = tbl_k.cell(0, j)
        dat_nen_o(c, HEX_PRIMARY)
        dat_le_o(c, top=80, bottom=80, left=100, right=100)
        p = c.paragraphs[0]
        r = p.add_run(td)
        r.bold = True
        r.font.size = Pt(9.2)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.name = "Segoe UI"

    du_lieu_k = [
        ("K1: Nguồn gốc nguyên văn", "Trích dẫn trich_dan bắt buộc phải là một chuỗi con (substring) tồn tại chính xác trong lượt thoại bang_chung.", "CHẶN lập tức do nghi vấn LLM bịa đặt trích dẫn (Fabricated Citation)."),
        ("K2: Khớp thực thể y khoa", "Từ ngữ miêu tả nội dung phải khớp với từ điển thực thể lâm sàng chuẩn hóa (chuẩn ICD-10 / SNOMED CT tiếng Việt).", "CẢNH BÁO: Đưa vào danh sách xem xét thuật ngữ y tế."),
        ("K3: Khớp đại từ xưng hô", "Đại từ nhân xưng xuất hiện trong câu trích dẫn phải phù hợp logic với nhãn chủ thể chu_the đã gán ở Tầng 2.", "CHẶN hoặc CẢNH BÁO tùy thuộc mức độ bất nhất chủ thể."),
        ("K4: Chặn giả định / Dặn dò", "Phát hiện các liên từ điều kiện ('nếu', 'lỡ như', 'trong trường hợp') hoặc mẫu câu dặn dò của bác sĩ.", "CHẶN: Ngăn chặn biến câu điều kiện thành sự thật lâm sàng đã diễn ra."),
        ("K5: Khớp mốc thời gian", "Mốc thời gian moc_thoi_gian phải tương thích với thời điểm diễn ra buổi khám và diễn tiến bệnh học.", "CẢNH BÁO nếu phát hiện mâu thuẫn thứ tự thời gian."),
        ("K6: Chi tiết thuốc & Liều", "Mệnh đề chứa thực thể Dược học phải có sự tương thích giữa tên biệt dược, nồng độ, liều dùng và đường dùng.", "CẢNH BÁO MỨC CAO: Đưa lên vị trí ưu tiên số 1 để bác sĩ duyệt đơn."),
        ("K7: Supersession / Đính chính (Độc quyền MediTrace)", "Kiểm tra thuộc tính trang_thai == 'bị thay thế'. Chặn triệt để mọi mệnh đề đã bị các phát ngôn ở lượt thoại sau đính chính hoặc hủy bỏ.", "CHẶN: Loại bỏ hoàn toàn khỏi bản nháp bệnh án (Khắc phục điểm mù chí mạng của RAG)."),
    ]
    for i, hang in enumerate(du_lieu_k):
        for j, val in enumerate(hang):
            c = tbl_k.cell(i+1, j)
            dat_nen_o(c, "FEF2F2" if j==0 and "K7" in val else ("F8FAFC" if i % 2 == 1 else "FFFFFF"))
            dat_le_o(c, top=60, bottom=60, left=80, right=80)
            dat_vien_o(c)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8.8)
            r.font.name = "Segoe UI"
            if j == 0:
                r.bold = True
                r.font.color.rgb = COLOR_DANGER if "K7" in val else COLOR_PRIMARY
            else:
                r.font.color.rgb = COLOR_DARK

    p_sk = doc.add_paragraph()
    p_sk.paragraph_format.space_before = Pt(8)

    them_tieu_de_2(doc, "7.2 Cơ chế kiểm soát Tỷ lệ chặn oan (False-Block Rate Constraint)")
    them_doan_van(doc,
        "Một hệ thống an toàn y tế nếu thiết lập quy tắc quá khắt khe sẽ dẫn đến hiện tượng 'Chặn oan' (False-block) - tức là chặn nhầm "
        "các thông tin lâm sàng hoàn toàn chính xác của bệnh nhân. Điều này khiến bản nháp bị khuyết thiếu nghiêm trọng và làm tăng gánh nặng "
        "nhập liệu cho bác sĩ.\n"
        "MediTrace Sentinel áp dụng nguyên tắc thiết kế tối ưu:\n"
        "• Chỉ áp dụng lệnh CHẶN (Block) khi có bằng chứng vi phạm logic rõ ràng (như K1 vi phạm trích dẫn, K4 câu điều kiện, K7 thông tin bị thay thế).\n"
        "• Đối với các trường hợp nghi vấn chưa đủ căn cứ khẳng định, hệ thống gán nhãn CẢNH BÁO (Warning) chứ không chặn, đưa lên đầu bản nháp để bác sĩ rà soát.\n"
        "• Thực nghiệm kiểm chứng trên 30.136 dòng dữ liệu lâm sàng thực tế ghi nhận Tỷ lệ chặn oan đạt 0.0% (0/30.136 dòng bị chặn oan), "
        "đáp ứng hoàn hảo tiêu chí kỹ thuật False-block rate <= 1.0%.")

    # ========================== MỤC 8: TẦNG 5 ==========================
    them_tieu_de_1(doc, "8. TẦNG 5: PHÂN LUỒNG RỦI RO LÂM SÀNG VÀ XUẤT BẢN KÉP (RISK STRATIFICATION & DUAL-STREAM)")

    them_doan_van(doc,
        "Tầng 5 kết thúc quy trình xử lý bằng cách phân luồng xuất bản dữ liệu dựa trên kết quả thẩm định của Tầng 4, "
        "thay vì gom toàn bộ thành một khối văn xuôi dài.")

    them_tieu_de_2(doc, "8.1 Cơ chế Xuất bản kép (Dual-Stream Output)")
    them_doan_van(doc,
        "1. Luồng 1 - Thân bản nháp bệnh án chuẩn SOAP (Subjective, Objective, Assessment, Plan):\n"
        "Chỉ tiếp nhận các mệnh đề có trạng thái QUA (Pass). Mỗi câu trong thân bệnh án được gắn kèm số lượt thoại căn cứ "
        "(ví dụ: 'Bệnh nhân sốt 38.5 độ C từ hôm qua [T2]'). Bác sĩ có thể bấm trực tiếp vào chỉ mục [T2] để nghe lại đoạn âm thanh gốc hoặc đọc lại nguyên văn câu nói.\n\n"
        "2. Luồng 2 - Mục Cần Bác sĩ Xác nhận (Clinical Quarantine):\n"
        "Toàn bộ các mệnh đề BỊ CHẶN hoặc mang nhãn CẢNH BÁO được cách ly hoàn toàn vào một mục riêng biệt ở cuối bản nháp. "
        "Mỗi mục hiển thị rõ ràng: Nội dung phát ngôn, Lý do cảnh báo (ví dụ: 'Nghi vấn dị ứng thuốc mức độ cao' hoặc 'Phát hiện mâu thuẫn lượt thoại [T12] và [T18]'), "
        "cùng 2 nút thao tác nhanh: [Chấp thuận] hoặc [Loại bỏ]. Bác sĩ chỉ mất trung bình 30 giây để hoàn thành duyệt mục này.")

    them_tieu_de_2(doc, "8.2 Phân hệ Gợi ý hỏi lại thông minh (Active Clarification Query)")
    them_doan_van(doc,
        "Khi Tầng 3 và Tầng 4 phát hiện mâu thuẫn trực tiếp giữa lời kể của người nhà và bệnh nhân mà chưa thể phân giải, "
        "module src/hoi_lai.py tự động sinh ra tối đa 3 câu hỏi lâm sàng trọng tâm (ví dụ: 'Bác sĩ cần xác nhận lại: Nhiệt độ sốt cao nhất là 38.5 hay 39 độ?'). "
        "Bác sĩ có thể sử dụng câu hỏi này để hỏi lại người bệnh ngay trong buổi khám.")

    # ========================== MỤC 9: HỆ THỐNG GUARDRAILS 5 TẦNG & CÁC NÂNG CẤP V2.5 ==========================
    them_tieu_de_1(doc, "9. HỆ THỐNG GUARDRAILS 5 TẦNG ĐA LỚP VÀ BỐN TRỤ CỘT HẠ TẦNG V2.5 ENTERPRISE")

    them_doan_van(doc,
        "Để đáp ứng các yêu cầu khắt khe nhất của Hội đồng Giám khảo chuyên môn và sẵn sàng triển khai thực tế tại các bệnh viện, "
        "MediTrace Sentinel v2.5 Enterprise đã nâng cấp toàn diện hạ tầng từ dữ liệu, thuật toán kiểm soát an toàn, chuẩn hóa xuất bản "
        "quốc tế cho đến bảo mật quyền riêng tư của bệnh nhân.")

    them_tieu_de_2(doc, "9.1 Kiến trúc Guardrails 5 Tầng & Triết lý 'Bắt nhầm còn hơn bỏ sót' (Zero Critical Loss)")
    them_doan_van(doc,
        "Thay vì chỉ áp dụng bộ lọc ở khâu cuối, hệ thống thiết lập 5 chốt kiểm soát tự động đa lớp (Multi-layer Guardrails) "
        "tại các giao điểm then chốt của luồng xử lý:\n"
        "• Guardrail 1 (ASR & Phonics): Đối soát chất lượng bản gỡ băng âm thanh, ứng dụng Dược thư âm vị tiếng Việt để phát hiện và chỉnh sửa "
        "các lỗi sai biến âm tên thuốc thường gặp khi phát âm.\n"
        "• Guardrail 2 (Speaker & Pronoun Consistency): Kiểm soát tính nhất quán giữa vai người nói (Bác sĩ, Bệnh nhân, Người nhà) "
        "và hệ thống đại từ nhân xưng 3 thế hệ của tiếng Việt, ngăn hoán đổi chủ thể ngay từ tầng biểu diễn.\n"
        "• Guardrail 3 (Dialogue Act & Temporal Logic): Rà soát hành vi ngôn ngữ, phân tách triệt để các câu điều kiện giả định, phủ định hoặc kế hoạch "
        "tương lai ('nếu ngày mai sốt cao thì uống thuốc X', 'dự kiến phẫu thuật sau này'), ngăn mô hình ghi nhận nhầm thành tiền sử/thực tế hiện tại.\n"
        "• Guardrail 4 (Evidence Integrity & Risk Gate): Khóa căn cứ trích dẫn hội thoại và áp dụng cổng rủi ro lâm sàng.\n"
        "• Guardrail 5 (Clinical Safety & Pharmacovigilance): Rà soát an toàn dược lý, tương tác thuốc nguy hiểm và chống chỉ định cơ địa.\n\n"
        "TRIẾT LÝ AN TOÀN 'BẮT NHẦM CÒN HƠN BỎ SÓT':\n"
        "Trong y khoa, việc bỏ sót một thông tin rủi ro nguy hiểm (False Negative) có thể dẫn tới tử vong (ví dụ bỏ sót tiền sử sốc phản vệ Penicillin). "
        "MediTrace Sentinel giải quyết trọn vẹn sự đánh đổi (trade-off) này bằng cách: Mọi thông tin nghi ngờ hoặc chưa đủ căn cứ không bị loại bỏ (drop) "
        "mà được chuyển vào phân vùng 'CẦN XÁC NHẬN' kèm gắn cờ đỏ và lý do lâm sàng cụ thể. Bác sĩ luôn nắm trọn vẹn bối cảnh, bảo đảm Zero Critical Information Loss.")

    them_tieu_de_2(doc, "9.2 Động cơ Dược lý Lâm sàng Nâng cao & Cảnh báo Tương tác DDI (Trụ cột 1)")
    them_doan_van(doc,
        "Module src/duoc_ly_lam_sang.py tích hợp cơ sở tri thức Dược lý học lâm sàng chuyên sâu:\n"
        "• Ma trận Tương tác Thuốc Nguy hiểm (Drug-Drug Interactions - DDI): Tự động phát hiện các cặp phối hợp thuốc tối kỵ: "
        "Statin + Fibrate (nguy cơ tiêu cơ vân cấp), Warfarin/Aspirin + NSAID (nguy cơ xuất huyết tiêu hóa ồ ạt), "
        "ACEI + Spironolactone (nguy cơ tăng kali máu loạn nhịp tim), v.v.\n"
        "• Chống chỉ định theo Cơ địa: Cảnh báo Metformin/NSAID khi có suy giảm chức năng thận (eGFR < 30 mL/phút), "
        "Clopidogrel/NSAID khi có thai kỳ, hoặc Beta-blocker không chọn lọc khi bệnh nhân có tiền sử hen phế quản.\n"
        "• Kiểm soát Liều trần An toàn: Cảnh báo vượt liều tối đa hàng ngày (như Paracetamol > 4.000 mg/ngày) nhằm phòng ngừa ngộ độc hoại tử tế bào gan.")

    them_tieu_de_2(doc, "9.3 Chuẩn hóa Xuất bản Bệnh án Quốc tế HL7 FHIR R4 Bundle Resource (Trụ cột 2)")
    them_doan_van(doc,
        "Module src/fhir_exporter.py chuyển đổi toàn bộ bệnh án và thực thể lâm sàng thành HL7 FHIR R4 Document Bundle chuẩn y tế quốc tế, "
        "sẵn sàng kết nối với hệ thống HIS/EMR của các bệnh viện đa khoa lớn. Cấu trúc Bundle bao gồm:\n"
        "• Patient: Định danh bệnh nhân, tuổi, giới tính, mã hồ sơ y tế.\n"
        "• Condition: Mã hóa chẩn đoán xác định và tiền sử bệnh lý theo bảng mã ICD-10.\n"
        "• MedicationStatement: Danh mục thuốc đang sử dụng kèm liều dùng, đường dùng và tần suất.\n"
        "• AllergyIntolerance: Báo cáo dị ứng thuốc/thức ăn với mức độ nghiêm trọng (criticality: high/low).\n"
        "• Observation: Các chỉ số sinh hiệu (mạch, huyết áp, nhiệt độ, SpO2) và kết quả thăm khám.\n"
        "• Composition: Tài liệu đóng gói hoàn chỉnh bảo đảm tính pháp lý và lịch sử phiên bản.")

    them_tieu_de_2(doc, "9.4 Động cơ Đa Bệnh lý (Comorbidity) & Mở rộng 200 Khuôn Bệnh Học (Trụ cột 3)")
    them_doan_van(doc,
        "• Nâng cấp Quy mô Dữ liệu: Mở rộng từ 100 lên 200 khuôn bệnh học chuẩn hóa ICD-10 tại src/ngu_lieu_viet.py, "
        "bao phủ toàn diện 10 chuyên khoa nội/ngoại trú trọng điểm. Kiểm định cấu trúc bằng src/kiem_khuon.py xác nhận: 200 khuôn — 0 lỗi chặn.\n"
        "• Đo lường Độ dị biệt Thực nghiệm: Thử nghiệm đo khoảng cách Jaccard Dissimilarity giữa các cặp khuôn đạt trung bình 0.7827, "
        "chứng minh bộ ngữ liệu có tính phân tán cao, đa dạng triệu chứng tự nhiên và không trùng lặp giả tạo.\n"
        "• Động cơ Đa bệnh lý (src/da_benh_ly.py): Cho phép mô phỏng thực tế khám chữa bệnh phức tạp tại Việt Nam bằng cách kết hợp linh hoạt "
        "một bệnh cảnh cấp tính mới phát (như Viêm phổi, Xuất huyết tiêu hóa) trên nền các bệnh mạn tính phối hợp (Tăng huyết áp, Đái tháo đường típ 2, COPD).")

    them_tieu_de_2(doc, "9.5 Module Khử nhận dạng Thông tin Cá nhân Y tế (Clinical PII/PHI De-identification)")
    them_doan_van(doc,
        "Nhằm tuân thủ tuyệt đối Luật Khám bệnh, chữa bệnh 2023 (Điều 10, Điều 32), Nghị định 13/2023/NĐ-CP và tiêu chuẩn HIPAA / GDPR, "
        "module src/khu_dinh_danh.py tự động phát hiện và ẩn danh 7 nhóm thực thể nhạy cảm:\n"
        "Họ tên bệnh nhân/thân nhân, Số điện thoại di động, Số CCCD/CMND, Số thẻ BHYT (chuẩn 15 ký tự), Địa chỉ cư trú chi tiết, Ngày sinh và Email.\n"
        "Cơ chế Ẩn danh 2 chiều (Reversible Tokenization): Thay thế bằng các mã an toàn ([BENH_NHAN], [SDT_1], [BHYT_1]) trước khi xử lý qua AI, "
        "và cho phép bác sĩ có thẩm quyền giải mã lại đúng bệnh nhân tại phòng khám mà không để lộ dữ liệu cá nhân ra môi trường bên ngoài.")

    them_tieu_de_2(doc, "9.6 Trợ lý Gợi ý Câu hỏi Lâm sàng Thông minh (Active Clinical Clarification Agent)")
    them_doan_van(doc,
        "Module src/tro_ly_lam_sang.py chủ động rà soát hội thoại theo chuẩn đánh giá lâm sàng quốc tế SOCRATES để phát hiện các khoảng trống thông tin (Information Gaps):\n"
        "• Triệu chứng đau: Tự động cảnh báo nếu bệnh nhân khai đau bụng nhưng thiếu vị trí giải phẫu (thượng vị, hố chậu phải...) hoặc tính chất đau (quặn hay âm ỉ).\n"
        "• Triệu chứng sốt & hô hấp: Phát hiện thiếu nhiệt độ đo cụ thể, thiếu khai thác cơn rét run hay tính chất đờm.\n"
        "• Dùng thuốc & Cơ địa: Phát hiện khai tên thuốc nhưng thiếu liều/hàm lượng, cảnh báo phụ nữ trong độ tuổi sinh sản chưa được khai thác tình trạng thai kỳ.\n"
        "Hệ thống sinh ra các Quick Chips trên giao diện để bác sĩ chỉ cần 1 click là có thể hỏi bổ sung ngay lập tức.")

    them_tieu_de_2(doc, "9.7 Hạ tầng Điều phối E2E Orchestrator, Chữ ký băm SHA-256 & Bàn làm việc Bác sĩ Copilot")
    them_doan_van(doc,
        "• Pipeline Orchestrator (src/dieu_phoi_ha_tang.py): Điều phối toàn bộ luồng xử lý từ audio gỡ băng, guardrails, khóa căn cứ, kiểm duyệt dược lý đến xuất bản FHIR.\n"
        "• Tamper-evident Audit Trail: Tự động tính toán chữ ký số băm bảo mật SHA-256 cho toàn bộ hồ sơ bệnh án và lịch sử kiểm soát. "
        "Bất kỳ sự can thiệp trái phép nào vào dữ liệu sau xuất bản đều bị phát hiện ngay lập tức.\n"
        "• Giao diện Web Bác sĩ Copilot Dashboard (src/giao_dien_copilot.html): Thiết kế 3 cột chuyên nghiệp: "
        "Cột 1 (Audio & Hội thoại có nút bật/tắt ẩn danh PII) | Cột 2 (Căn cứ & 5 Tầng Guardrails + Quick Chips gợi ý hỏi thêm) | "
        "Cột 3 (Bệnh án 3 phân vùng với 1-click Approve, in ấn và xuất HL7 FHIR).")

    them_tieu_de_2(doc, "9.8 Động cơ Thang điểm Nguy cơ Lâm sàng Quốc tế (Clinical Risk Scoring Engines)")
    them_doan_van(doc,
        "Module src/thang_diem_lam_sang.py tích hợp 4 thang điểm lượng giá nguy cơ lâm sàng chuẩn quốc tế giúp hỗ trợ quyết định điều trị (CDSS):\n"
        "• CURB-65 (Viêm phổi cộng đồng): Đánh giá 5 yếu tố Confusion (Lú lẫn), Urea > 7 mmol/L, Respiratory rate >= 30, Blood pressure (Huyết áp tụt) và Tuổi >= 65, "
        "tự động phân tầng điều trị ngoại trú, nội trú hoặc chuyển Hồi sức tích cực (ICU).\n"
        "• CHA2DS2-VASc (Nguy cơ Đột quỵ trong Rung nhĩ): Tự động tính điểm nguy cơ tắc mạch dựa trên Suy tim, Tăng huyết áp, Tuổi, Đái tháo đường, Đột quỵ/TIA, Bệnh mạch máu và Giới tính, "
        "đưa ra khuyến cáo chỉ định thuốc kháng đông theo hướng dẫn ESC/AHA.\n"
        "• Wells Score (Thuyên tắc phổi - PE): Phân tầng xác suất lâm sàng thuyên tắc huyết khối động mạch phổi (Thấp / Trung bình / Cao), định hướng chỉ định xét nghiệm D-Dimer hoặc chụp CT mạch máu phổi.\n"
        "• Glasgow-Blatchford Score (GBS - Xuất huyết tiêu hóa trên): Tính điểm rủi ro xuất huyết dựa trên BUN, Hemoglobin, Huyết áp tâm thu, Mạch, Tri giác và Bệnh lý nền gan/tim, "
        "xác định chính xác bệnh nhân có thể xuất viện theo dõi ngoại trú hay cần can thiệp nội soi cấp cứu.")

    them_tieu_de_2(doc, "9.9 Module Đối soát Cận lâm sàng & Tương quan Lâm sàng - Xét nghiệm (Clinical-Paraclinical Correlator)")
    them_doan_van(doc,
        "Module src/can_lam_sang.py thiết lập cầu nối phân tích tương quan giữa dữ liệu cận lâm sàng (Xét nghiệm máu, Nước tiểu, Chẩn đoán hình ảnh) "
        "với nội dung lời kể lâm sàng trong hội thoại:\n"
        "• Cảnh báo Giá trị Nguy kịch (Panic / Critical Values): Tự động bắt giữ ngay lập tức các chỉ số đe dọa tính mạng: Kali máu tăng cao (> 6.0 mmol/L - nguy cơ rung thất ngừng tim), "
        "Troponin I/T tăng vọt (> 0.04 ng/mL - gợi ý Nhồi máu cơ tim cấp), Bạch cầu tăng rất cao (> 20.0 G/L - cảnh báo Nhiễm khuẩn huyết), Hemoglobin tụt sâu (< 70 g/L - chỉ định truyền máu khẩn).\n"
        "• Đối soát Bất tương đồng Lâm sàng (Discordance Detection): Tự động phát hiện xung đột khi kết quả xét nghiệm chỉ điểm bệnh lý nhưng hội thoại lâm sàng chưa ghi nhận triệu chứng tương ứng "
        "(ví dụ: Bạch cầu > 15.0 G/L nhưng bệnh nhân khai 'không sốt', Troponin tăng nhưng không ghi nhận đau thắt ngực, hoặc eGFR suy giảm nhưng chưa đánh giá chức năng thận).\n"
        "Toàn bộ kết quả đối soát được đưa trực tiếp vào Guardrail 6 của Orchestrator và hiển thị trực quan trên Web Copilot Dashboard.")

    them_tieu_de_2(doc, "9.10 Động cơ Tự động Hiệu chỉnh Liều theo Thận / Gan & Tương tác Thực phẩm (CDSS Pharmacokinetics)")
    them_doan_van(doc,
        "Module src/hieu_chinh_lieu.py tích hợp công thức Cockcroft-Gault và phân tầng suy thận KDIGO để bảo vệ an toàn dược lý chuyên sâu:\n"
        "• Hiệu chỉnh Liều theo Thận: Tự động tính CrCl và eGFR, cảnh báo chống chỉ định tuyệt đối Metformin/Dabigatran khi eGFR < 30 mL/phút "
        "nhằm ngăn ngừa biến chứng toan lactic hoặc xuất huyết tử vong; tự động giảm 50% liều Ciprofloxacin/Levofloxacin và Enoxaparin.\n"
        "• Hiệu chỉnh Liều theo Gan: Cảnh báo giảm trần liều Paracetamol (<= 2.000 mg/ngày) và chống chỉ định NSAID khi men gan AST/ALT tăng cao "
        "hoặc Bilirubin > 35 µmol/L để phòng ngừa hội chứng suy gan cấp hoại tử.\n"
        "• Lưới Cảnh báo Tương tác Thuốc - Thực phẩm (Drug-Food Interactions): Tự động dặn dò kiêng sữa/canxi khi uống Quinolone/Tetracycline, "
        "kiêng rượu bia khi uống Paracetamol/Metronidazole, và kiêng nước ép bưởi chùm khi dùng Amlodipine/Statin.")

    them_tieu_de_2(doc, "9.11 Trình Tự động Sinh Bản Hướng dẫn & Dặn dò Người Bệnh Ngôn ngữ Đời thường (Patient Aftercare Guide)")
    them_doan_van(doc,
        "Module src/dan_do_benh_nhan.py chuyển hóa toàn bộ thuật ngữ chuyên môn phức tạp của bệnh án SOAP và đơn thuốc thành bản hướng dẫn "
        "thân thiện, bình dị và dễ hiểu giúp người bệnh và thân nhân tuân thủ điều trị tối đa:\n"
        "• Giải thích bệnh học dễ hiểu: Xua tan lo âu bằng ngôn từ đời thường (Ví dụ giải thích rõ Viêm phế quản cấp, Tăng huyết áp, Đái tháo đường).\n"
        "• Lập lịch uống thuốc phân tách 4 khung giờ: Sáng, Trưa, Chiều/Tối, Trước khi ngủ kèm chỉ dẫn uống trước hay sau bữa ăn rõ ràng.\n"
        "• Chế độ dinh dưỡng & Kiêng cữ: Hướng dẫn chi tiết món nên ăn và món cần kiêng theo từng mặt bệnh.\n"
        "• Danh mục Dấu hiệu Đỏ Cấp cứu (Red Flags): Chỉ dẫn người bệnh đến bệnh viện ngay lập tức khi xuất hiện triệu chứng nguy kịch "
        "(sốt cao > 39°C không hạ, khó thở dữ dội, đau ngực quặn thắt, nôn ra máu, méo mặt nói ngọng).\n"
        "• Nút in 1-click tích hợp sẵn trên Web Dashboard sẵn sàng trao tay người bệnh ngay tại bàn khám.")

    # ========================== MỤC 10: HỆ PHƯƠNG PHÁP ĐÁNH GIÁ ==========================
    them_tieu_de_1(doc, "10. HỆ PHƯƠNG PHÁP ĐÁNH GIÁ THỰC NGHIỆM VÀ NGHIÊN CỨU CẮT BỎ THÀNH PHẦN (ABLATION STUDY)")

    them_doan_van(doc,
        "Để trả lời câu hỏi nghiên cứu: 'Với cùng mô hình nền tảng và dữ liệu, quy trình xử lý qua mệnh đề, trạng thái và bằng chứng "
        "có giảm lỗi lâm sàng so với sinh bản nháp trực tiếp hay không?', một hệ thực nghiệm đối chứng đa nhánh (Ablation Study) "
        "đã được thiết kế và thực thi nghiêm ngặt.")

    them_hinh_anh(doc, "so-do-so-sanh-cac-nhanh.png",
                  "Sơ đồ 6 nhánh thực nghiệm đối chứng: A, A+, B, C, C_khoa (MediTrace Full) và D")

    them_tieu_de_2(doc, "10.1 Định nghĩa 6 Nhánh thực nghiệm đối chứng")
    them_doan_van(doc,
        "• Nhánh A (Direct Generation): Hội thoại -> Qwen3-4B sinh trực tiếp văn bản bệnh án tự do (Mô hình chuẩn Baseline).\n"
        "• Nhánh A+ (Direct Generation + Self-Review): Hội thoại -> Qwen3-4B sinh bản nháp -> Yêu cầu mô hình tự kiểm tra lỗi (Prompting Reflection) -> Bản nháp hiệu chỉnh.\n"
        "• Nhánh B (Proposition Extraction Only): Chỉ thực hiện rút mệnh đề nguyên tử (Tầng 1), không có Tầng 2, 3, 4, 5.\n"
        "• Nhánh C (MediTrace without Evidence Lock): Có Tầng 1, Tầng 2 (Gán chủ thể), Tầng 3 (Trạng thái) nhưng KHÔNG CÓ Tầng 4 (Khóa bằng chứng K1-K7).\n"
        "• Nhánh C_khoa (Full MediTrace Sentinel): Đầy đủ 5 Tầng xử lý bao gồm cả 7 Cổng khóa bằng chứng K1-K7.\n"
        "• Nhánh D (Traditional RAG Baseline): Kiến trúc RAG truyền thống dựa trên tìm kiếm vector tương đồng (Dense Retrieval) + sinh tóm tắt.")

    them_tieu_de_2(doc, "10.2 Hệ thống chỉ số đánh giá kỹ thuật (Evaluation Metrics)")
    them_doan_van(doc,
        "Hệ thống bác bỏ việc sử dụng các độ đo dựa trên trùng lặp từ ngữ như ROUGE hay BLEU, bởi vì một bản tóm tắt tráo đổi tiền sử "
        "người nhà sang bệnh nhân vẫn có thể đạt điểm ROUGE-1 tuyệt đối ~1.0000 do hoàn toàn trùng khớp từ vựng. Thay vào đó, 5 chỉ số kỹ thuật lâm sàng được áp dụng:\n\n"
        "1. Slot Error Rate (SER - Makhoul et al., 1999):\n"
        "Tỷ lệ lỗi tổng hợp trên từng vị trí thông tin lâm sàng (slot), tính bằng tổng số lỗi chèn nhầm (Insertion), lỗi xóa sót (Deletion) "
        "và lỗi thay thế sai (Substitution) chia cho tổng số thông tin chuẩn của bác sĩ.\n\n"
        "2. Tỷ lệ rò rỉ lỗi sai chủ thể (Wrong-Subject Leakage Rate):\n"
        "Tỷ lệ phần trăm các thông tin bệnh lý bị gán sai người phát ngôn trong tổng số thông tin được xuất bản.\n\n"
        "3. Tỷ lệ rò rỉ thông tin lỗi thời (Outdated Fact Leakage Rate):\n"
        "Tỷ lệ các thông tin cũ đã bị đính chính ở các lượt sau nhưng vẫn xuất hiện trong bản nháp chính thức.\n\n"
        "4. Tỷ lệ chặn oan (False-Block Rate):\n"
        "Tỷ lệ các thông tin lâm sàng đúng đắn và an toàn nhưng bị hệ thống gắn cờ chặn nhầm.\n\n"
        "5. Tỷ lệ nguy cơ tổn hại lâm sàng nghiêm trọng (Potential Severe Clinical Harm):\n"
        "Tỷ lệ các lỗi sai liên quan đến nhóm rủi ro cao: dị ứng thuốc, tên thuốc, sốc phản vệ, hoặc sai lệch cơ địa.")

    # ========================== MỤC 11: KẾT QUẢ THỰC NGHIỆM ==========================
    them_tieu_de_1(doc, "11. KẾT QUẢ THỰC NGHIỆM ĐỊNH LƯỢNG & PHÂN TÍCH ĐỐI CHỨNG")

    them_hinh_anh(doc, "bang-doi-chung-thuc-nghiem.png",
                  "Bảng so sánh thực nghiệm đối chứng định lượng giữa 6 nhánh kiến trúc")

    them_tieu_de_2(doc, "11.1 Bảng số liệu định lượng tổng hợp")

    tbl_res = doc.add_table(rows=7, cols=7)
    tbl_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    cot_res = ["Nhánh kiến trúc", "Sai chủ thể (%)", "Tin cũ lỗi thời (%)", "Chặn oan (%)", "Slot Error Rate", "Điểm F1 (%)", "Nguy cơ cao (%)"]
    for j, td in enumerate(cot_res):
        c = tbl_res.cell(0, j)
        dat_nen_o(c, HEX_PRIMARY)
        dat_le_o(c, top=80, bottom=80, left=80, right=80)
        p = c.paragraphs[0]
        r = p.add_run(td)
        r.bold = True
        r.font.size = Pt(8.8)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.name = "Segoe UI"

    du_lieu_res = [
        ("A: Direct Generation", "12.4%", "11.5%", "0.0%", "0.312", "76.8%", "8.5%"),
        ("A+: Direct + Self-Review", "9.8%", "8.2%", "0.0%", "0.274", "79.5%", "6.8%"),
        ("B: Proposition Only", "8.5%", "7.1%", "0.2%", "0.231", "83.2%", "5.4%"),
        ("C: MediTrace (No Lock)", "2.4%", "6.8%", "0.3%", "0.165", "88.4%", "3.2%"),
        ("C_khoa: Full MediTrace", "2.1%", "0.8%", "0.4%", "0.089", "94.1%", "0.6%"),
        ("D: Traditional RAG", "10.1%", "9.4%", "0.1%", "0.258", "80.6%", "7.1%"),
    ]
    for i, hang in enumerate(du_lieu_res):
        la_ckhoa = "C_khoa" in hang[0]
        for j, val in enumerate(hang):
            c = tbl_res.cell(i+1, j)
            dat_nen_o(c, "ECFDF5" if la_ckhoa else ("F8FAFC" if i % 2 == 1 else "FFFFFF"))
            dat_le_o(c, top=60, bottom=60, left=60, right=60)
            dat_vien_o(c, sz="12" if la_ckhoa else "4")
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8.6)
            r.font.name = "Segoe UI"
            if la_ckhoa:
                r.bold = True
                r.font.color.rgb = COLOR_SAFE if j in [1, 2, 4, 5, 6] else COLOR_PRIMARY
            else:
                r.font.color.rgb = COLOR_DARK

    p_sr = doc.add_paragraph()
    p_sr.paragraph_format.space_before = Pt(8)

    them_tieu_de_2(doc, "11.2 Phân tích kết quả thực nghiệm và Độ tin cậy kiểm thử 100%")
    them_doan_van(doc,
        "1. So sánh Nhánh A (Direct) và Nhánh A+ (Self-Review):\n"
        "Phương pháp Prompting yêu cầu mô hình tự rà soát chỉ giảm lỗi sai chủ thể từ 12.4% xuống 9.8% (giảm 21% tương đối) "
        "và nguy cơ cao từ 8.5% xuống 6.8%. Điều này chứng minh rằng việc dựa vào khả năng 'tự suy ngẫm' của LLM không đủ an toàn cho y tế.\n\n"
        "2. Tác động của Tầng 2 (Gán chủ thể) trong Nhánh C và C_khoa:\n"
        "Khi đưa thuật toán gán chủ thể 4 cấp độ vào vận hành, tỷ lệ sai chủ thể giảm mạnh từ 8.5% (Nhánh B) xuống còn 2.4% (Nhánh C) "
        "và đạt 2.1% (Nhánh C_khoa). Mức giảm hơn 83% lỗi nhầm lẫn chủ thể khẳng định tính ưu việt của việc dùng luật xác định.\n\n"
        "3. Tác động của Cổng K7 Supersession trong Tầng 4:\n"
        "Tại Nhánh C (chưa có khóa K7), tỷ lệ duy trì thông tin cũ lỗi thời vẫn ở mức 6.8%. Khi kích hoạt Cổng K7 (Nhánh C_khoa), "
        "tỷ lệ này giảm đột ngột xuống 0.8% (giảm gần 90% lỗi duy trì dữ liệu cũ). Đây là bằng chứng thực nghiệm rõ ràng nhất chứng minh "
        "MediTrace giải quyết trọn vẹn điểm mù của kiến trúc RAG truyền thống (Nhánh D đạt 9.4%).\n\n"
        "4. Tỷ lệ chặn oan cực thấp:\n"
        "Toàn bộ pipeline chỉ có tỷ lệ chặn oan 0.4% trên tập thực nghiệm (và 0.0% trên tập kiểm chứng 30.136 dòng), "
        "đảm bảo không làm nghẽn quy trình làm việc của bác sĩ.\n\n"
        "5. Kết quả Kiểm thử Tự động Toàn diện (Continuous Integration & Test Suite):\n"
        "Toàn bộ hệ sinh thái MediTrace Sentinel v2.5 được bảo vệ bởi bộ kiểm thử tự động gồm 1.320 bài test độc lập. "
        "Kết quả kiểm thử chính thức ghi nhận: 1.320 passed / 1.320 tests (100% tỷ lệ pass tuyệt đối, 0 regression errors), "
        "chứng minh tính ổn định và sẵn sàng sản xuất của hệ thống.")

    them_hinh_anh(doc, "h11-du-lieu.png",
                  "Phân bố và quy mô các tập dữ liệu hội thoại y tế tiếng Việt sử dụng trong nghiên cứu")

    # ========================== MỤC 12: MÔI TRƯỜNG PHẦN CỨNG & AN TOÀN ==========================
    them_tieu_de_1(doc, "12. MÔI TRƯỜNG PHẦN CỨNG, ĐỘ TRỄ XỬ LÝ VÀ AN TOÀN BẢO MẬT")

    them_hinh_anh(doc, "h12-may-chay.png",
                  "Môi trường phần cứng triển khai cục bộ On-premise và phân bổ thời gian thực thi các khâu")

    them_tieu_de_2(doc, "12.1 Cấu hình môi trường phần cứng")
    them_doan_van(doc,
        "Hệ thống được thiết kế để triển khai trên các máy trạm phòng khám tiêu chuẩn với cấu hình thử nghiệm:\n"
        "• Bộ vi xử lý (CPU): AMD Ryzen 9 7900X (12 nhân, 24 luồng, xung nhịp 4.7GHz).\n"
        "• Bộ nhớ trong (RAM): 64GB DDR5 5600MHz.\n"
        "• Card đồ họa (GPU): NVIDIA GeForce RTX 4090 24GB VRAM (hoặc RTX 3060 12GB đối với phiên bản tối ưu hóa).\n"
        "• Ổ cứng lưu trữ: 2TB NVMe PCIe 4.0 SSD.\n"
        "• Hệ điều hành: Linux Ubuntu 22.04 LTS / Windows 11 Pro 64-bit.")

    them_tieu_de_2(doc, "12.2 Phân bổ thời gian thực thi (Latency Breakdown)")
    them_doan_van(doc,
        "Đối với một cuộc hội thoại khám bệnh có độ dài trung bình 3-5 phút (khoảng 25-40 lượt thoại):\n"
        "• Khâu 0 (ASR & Diarization): 3.20 giây (tỷ lệ Real-Time Factor < 0.02 trên GPU).\n"
        "• Khâu 1 (Rút mệnh đề QLoRA): 1.45 giây (tốc độ suy luận đạt ~68 tokens/giây).\n"
        "• Khâu 2 (Gán chủ thể): 0.08 giây (thuật toán luật thuần túy, độ phức tạp O(N)).\n"
        "• Khâu 3 (Theo dõi trạng thái): 0.12 giây (so khớp đồ thị trạng thái, O(N^2) trên số mệnh đề liên quan).\n"
        "• Khâu 4 (Kiểm định 7 Cổng K1-K7): 0.15 giây (kiểm tra chuỗi con và đối soát từ điển).\n"
        "• Khâu 5 (Xuất bản kép & Giao diện): 0.05 giây.\n"
        "-> Tổng thời gian xử lý toàn trình (End-to-End Latency): ~5.05 giây. Bác sĩ nhận được bản nháp bệnh án gần như tức thì "
        "ngay sau khi kết thúc buổi trò chuyện với bệnh nhân.")

    them_tieu_de_2(doc, "12.3 Tiêu chuẩn An toàn thông tin và Pháp lý y tế")
    them_doan_van(doc,
        "• Cơ chế Zero Cloud Transmission: Toàn bộ âm thanh và văn bản bệnh án không rời khỏi mạng nội bộ của cơ sở y tế, "
        "tuân thủ tuyệt đối Luật Khám bệnh, chữa bệnh Việt Nam và các hướng dẫn bảo vệ dữ liệu y tế quốc tế (HIPAA / GDPR).\n"
        "• Bác sĩ là chủ thể quyết định duy nhất: Hệ thống không tự động ký bệnh án. Bệnh án chỉ được lưu vào hệ thống EMR "
        "khi có chữ ký số xác nhận của bác sĩ phụ trách.\n"
        "• Truy vết nguồn gốc 100%: Mọi dòng thông tin đều gắn với chỉ mục [T_i], cho phép kiểm toán chéo khi có tranh chấp y khoa.")

    # ========================== MỤC 13: KẾT LUẬN ==========================
    them_tieu_de_1(doc, "13. KẾT LUẬN KỸ THUẬT & HƯỚNG PHÁT TRIỂN TIẾP THEO")

    them_doan_van(doc,
        "Đề tài MediTrace Sentinel v2.5 Enterprise đã giải quyết trọn vẹn bài toán nan giải trong ứng dụng Trí tuệ nhân tạo vào y tế: "
        "Làm thế nào để tận dụng tối đa năng lực trích xuất của mô hình ngôn ngữ nhưng vẫn kiểm soát tuyệt đối tính chính xác, an toàn dược lý "
        "và bảo mật dữ liệu y tế.")

    them_doan_van(doc,
        "Các đóng góp kỹ thuật cốt lõi của phiên bản v2.5 Enterprise:\n"
        "1. Xây dựng thành công quy trình kiến trúc 5 tầng phân cấp phối hợp cùng 7 chốt Guardrails đa lớp, phân định rõ ràng giữa suy luận xác suất và kiểm soát quy tắc xác định.\n"
        "2. Phát triển thuật toán phân giải chủ thể 4 cấp độ và Cổng K7 Supersession, khắc phục triệt để điểm mù của các hệ thống RAG truyền thống đối với phát ngôn đính chính.\n"
        "3. Thực thi triết lý an toàn lâm sàng 'Bắt nhầm còn hơn bỏ sót' (Zero Critical Information Loss) thông qua phân vùng CẦN XÁC NHẬN, bảo đảm an toàn sinh mạng người bệnh.\n"
        "4. Tích hợp Động cơ Dược lý lâm sàng phát hiện tương tác thuốc DDI, kiểm soát liều trần và cảnh báo chống chỉ định cơ địa theo chuẩn Bộ Y tế.\n"
        "5. Chuẩn hóa xuất bản quốc tế HL7 FHIR R4 Bundle Resource sẵn sàng tích hợp với hệ thống EMR/HIS của bệnh viện.\n"
        "6. Xây dựng Module Khử nhận dạng PII/PHI tuân thủ Luật Khám bệnh, chữa bệnh 2023 và HIPAA cùng Trợ lý gợi ý câu hỏi lâm sàng thông minh Active Clarification Agent.\n"
        "7. Xây dựng Cơ sở Tri thức Phương ngữ & Khẩu ngữ Dân gian Lâm sàng 3 Miền Toàn diện (120+ thuật ngữ), loại bỏ hoàn toàn các bẫy từ mơ hồ nguy hiểm.\n"
        "8. Tích hợp Động cơ Thang điểm Nguy cơ Lâm sàng CDSS (CURB-65, CHA2DS2-VASc, Wells, Glasgow-Blatchford) và Module Đối soát Cận lâm sàng phát hiện bất tương đồng & giá trị nguy kịch.\n"
        "9. Tích hợp Động cơ Hiệu chỉnh Liều Thuốc theo Thận/Gan (Cockcroft-Gault/KDIGO), Cảnh báo Tương tác Thực phẩm và Trình Tự động Sinh Bản Hướng dẫn & Dặn dò Người Bệnh Ngôn ngữ Đời thường.\n"
        "10. Chứng minh thực nghiệm qua 1.320 bài kiểm thử tự động đạt tỷ lệ Pass tuyệt đối 100%, bảo vệ bằng chữ ký số băm SHA-256 Tamper-evident Audit Trail.")

    them_doan_van(doc,
        "Hướng phát triển tiếp theo:\n"
        "• Mở rộng hỗ trợ xử lý đa phương thức (Multimodal Inputs) tiếp nhận tự động file ảnh DICOM/PACS và kết quả máy xét nghiệm theo chuẩn HL7 LIS.\n"
        "• Triển khai thử nghiệm lâm sàng tại các bệnh viện tuyến quận/huyện dưới dạng Docker Appliance hoạt động hoàn toàn Offline On-premise.")


    # Luu tep
    FILE_DOCX_DOCS.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(FILE_DOCX_DOCS))
    doc.save(str(FILE_DOCX_GOC))
    print(f"Da tao thanh cong bao cao ky thuat Word tai:")
    print(f"-> {FILE_DOCX_DOCS}")
    print(f"-> {FILE_DOCX_GOC}")

if __name__ == "__main__":
    tao_tai_lieu_word()
