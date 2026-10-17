# -*- coding: utf-8 -*-
"""Script tao file Word (.docx) sieu dep cho Bo Cau hoi & Tra loi Ban Giam khao.
Thiet ke theo tieu chuan an pham trinh bay chuyen nghiep:
- Font Segoe UI dong nhat, mau sac Navy & Teal trang nha
- Hop cau hoi co vien mau, nen sang kem huy hieu muc do (De, Trung binh, Kho, Stress-test)
- Bang bieu va hop chu y bo tri khoa hoc de gay an tuong manh voi Ban Giam khao
"""

from pathlib import Path
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

GOC = Path(__file__).resolve().parent.parent
FILE_OUT_GOC = GOC / "Bo_Cau_Hoi_Va_Tra_Loi_Ban_Giam_Khao_MediTrace.docx"
FILE_OUT_DOCS = GOC / "docs" / "tai-lieu" / "Bo_Cau_Hoi_Va_Tra_Loi_Ban_Giam_Khao_MediTrace.docx"

# Bang mau
HEX_NAVY = "1E3A5F"
HEX_TEAL = "0D5C54"
HEX_DARK = "0F172A"
HEX_MUTED = "475569"
HEX_LIGHT_BG = "F8FAFC"
HEX_DANGER = "DC2626"
HEX_SAFE = "059669"
HEX_WARN = "D97706"
HEX_PURPLE = "7C3AED"

COLOR_NAVY = RGBColor(0x1E, 0x3A, 0x5F)
COLOR_TEAL = RGBColor(0x0D, 0x5C, 0x54)
COLOR_DARK = RGBColor(0x0F, 0x17, 0x2A)
COLOR_MUTED = RGBColor(0x47, 0x55, 0x69)
COLOR_DANGER = RGBColor(0xDC, 0x26, 0x26)
COLOR_SAFE = RGBColor(0x05, 0x96, 0x69)
COLOR_WARN = RGBColor(0xD9, 0x77, 0x06)
COLOR_PURPLE = RGBColor(0x7C, 0x3A, 0xED)


def dat_vien_o(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1", sz="4"):
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
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)


def dat_le_o(cell, top=100, bottom=100, left=140, right=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def them_doan_van(doc, text="", dam=False, nghieng=False, co_chu=10,
                  mau=COLOR_DARK, can_le=WD_ALIGN_PARAGRAPH.LEFT,
                  cach_tren=0, cach_duoi=4, gian_dong=1.15):
    p = doc.add_paragraph()
    p.alignment = can_le
    p.paragraph_format.space_before = Pt(cach_tren)
    p.paragraph_format.space_after = Pt(cach_duoi)
    p.paragraph_format.line_spacing = gian_dong
    if text:
        r = p.add_run(text)
        r.bold = dam
        r.italic = nghieng
        r.font.name = "Segoe UI"
        r.font.size = Pt(co_chu)
        r.font.color.rgb = mau
    return p


def them_tieu_de_phan(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Segoe UI"
    r.font.size = Pt(14)
    r.font.color.rgb = COLOR_NAVY
    return p


def them_hop_cau_hoi(doc, ma_muc, tieu_de_cau_hoi, noi_dung_tra_loi, mau_vien=HEX_NAVY, mau_nen="F8FAFC", badge_text=""):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.8)
    dat_nen_o(cell, mau_nen)
    dat_vien_o(cell, top="CBD5E1", bottom="CBD5E1", left=mau_vien, right="CBD5E1", sz="16")
    dat_le_o(cell, top=100, bottom=100, left=150, right=140)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)

    # Badge muc do
    if badge_text:
        r_badge = p.add_run(f"[{badge_text.upper()}] ")
        r_badge.bold = True
        r_badge.font.size = Pt(9.5)
        r_badge.font.name = "Segoe UI"
        if badge_text.lower() in ("dễ", "easy"):
            r_badge.font.color.rgb = COLOR_SAFE
        elif badge_text.lower() in ("trung bình", "medium"):
            r_badge.font.color.rgb = COLOR_NAVY
        elif badge_text.lower() in ("khó", "hard"):
            r_badge.font.color.rgb = COLOR_PURPLE
        else:
            r_badge.font.color.rgb = COLOR_DANGER

    r_q = p.add_run(tieu_de_cau_hoi + "\n")
    r_q.bold = True
    r_q.font.size = Pt(11)
    r_q.font.name = "Segoe UI"
    r_q.font.color.rgb = COLOR_DARK

    # Noi dung tra loi
    for dong in noi_dung_tra_loi:
        p_ans = cell.add_paragraph()
        p_ans.paragraph_format.space_before = Pt(2)
        p_ans.paragraph_format.space_after = Pt(3)
        p_ans.paragraph_format.line_spacing = 1.15
        
        # Parse dinh dang co ban
        parts = dong.split("**")
        is_bold = False
        for part in parts:
            if part:
                r = p_ans.add_run(part)
                r.bold = is_bold
                r.font.name = "Segoe UI"
                r.font.size = Pt(9.5)
                r.font.color.rgb = COLOR_DARK
            is_bold = not is_bold

    them_doan_van(doc, "")


def tao_word_qna():
    doc = docx.Document()

    # Thiet lap le trang A4
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)

    # BANNER COVER
    tbl_top = doc.add_table(rows=1, cols=1)
    tbl_top.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_top = tbl_top.cell(0, 0)
    cell_top.width = Inches(6.8)
    dat_nen_o(cell_top, HEX_NAVY)
    dat_vien_o(cell_top, top=HEX_NAVY, bottom=HEX_NAVY, left=HEX_NAVY, right=HEX_NAVY)
    dat_le_o(cell_top, top=160, bottom=160, left=180, right=180)

    p_top = cell_top.paragraphs[0]
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_top1 = p_top.add_run("MEDITRACE SENTINEL — AMBIENT CLINICAL INTELLIGENCE\n")
    r_top1.bold = True
    r_top1.font.size = Pt(11)
    r_top1.font.name = "Segoe UI"
    r_top1.font.color.rgb = RGBColor(0x99, 0xF6, 0xE4)

    r_top_title = p_top.add_run("BỘ CÂU HỎI & TRẢ LỜI PHẢN BIỆN BAN GIÁM KHẢO\n")
    r_top_title.bold = True
    r_top_title.font.size = Pt(18)
    r_top_title.font.name = "Segoe UI"
    r_top_title.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    r_top2 = p_top.add_run("TỔNG HỢP CÂU HỎI TỪ DỄ ĐẾN KHÓ · PHÂN LOẠI LÝ THUYẾT VÀ KỸ THUẬT CHUYÊN SÂU")
    r_top2.italic = True
    r_top2.font.size = Pt(9.0)
    r_top2.font.name = "Segoe UI"
    r_top2.font.color.rgb = RGBColor(0xCC, 0xFB, 0xF1)

    them_doan_van(doc, "")

    # 4 o chi so thuc nghiem
    tbl_stats = doc.add_table(rows=1, cols=4)
    tbl_stats.alignment = WD_TABLE_ALIGNMENT.CENTER
    stats = [
        ("KIỂM THỬ TỰ ĐỘNG", "1.320 / 1.320", "100% test vượt qua", HEX_SAFE, "ECFDF5"),
        ("SÓT DỊ ỨNG", "0.0%", "Tuyệt đối không bỏ sót", HEX_DANGER, "FEF2F2"),
        ("CHẶN BỊA ĐẶT", "7 CỔNG K1-K7", "Khóa bằng chứng 2 chiều", HEX_TEAL, "F0FDFA"),
        ("GIẢM LỖI NHỚ SAI", "GIẢM 14 LẦN", "Từ 11.5% xuống 0.8%", HEX_WARN, "FFFBEB")
    ]
    for idx, (label, val, desc, border_c, bg_c) in enumerate(stats):
        cell = tbl_stats.cell(0, idx)
        cell.width = Inches(1.7)
        dat_nen_o(cell, bg_c)
        dat_vien_o(cell, top=border_c, bottom=border_c, left=border_c, right=border_c, sz="6")
        dat_le_o(cell, top=60, bottom=60, left=80, right=80)

        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(1)

        r_l = p.add_run(f"{label}\n")
        r_l.bold = True
        r_l.font.size = Pt(7.5)
        r_l.font.name = "Segoe UI"
        r_l.font.color.rgb = COLOR_NAVY

        r_v = p.add_run(f"{val}\n")
        r_v.bold = True
        r_v.font.size = Pt(11)
        r_v.font.name = "Segoe UI"
        r_v.font.color.rgb = COLOR_NAVY

        r_d = p.add_run(desc)
        r_d.font.size = Pt(7.5)
        r_d.font.name = "Segoe UI"
        r_d.font.color.rgb = COLOR_MUTED

    them_doan_van(doc, "")

    # HUONG DAN SU DUNG
    tbl_guide = doc.add_table(rows=1, cols=1)
    tbl_guide.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_g = tbl_guide.cell(0, 0)
    c_g.width = Inches(6.8)
    dat_nen_o(c_g, "F1F5F9")
    dat_vien_o(c_g, top="CBD5E1", bottom="CBD5E1", left=HEX_TEAL, right="CBD5E1", sz="12")
    dat_le_o(c_g, top=80, bottom=80, left=120, right=120)
    p_g = c_g.paragraphs[0]
    p_g.paragraph_format.space_before = Pt(0)
    p_g.paragraph_format.space_after = Pt(2)
    r_g1 = p_g.add_run("💡 HƯỚNG DẪN DÀNH CHO THÍ SINH KHI ĐỨNG TRƯỚC HỘI ĐỒNG GIÁM KHẢO:\n")
    r_g1.bold = True
    r_g1.font.size = Pt(9.5)
    r_g1.font.name = "Segoe UI"
    r_g1.font.color.rgb = COLOR_TEAL

    r_g2 = p_g.add_run(
        "Mọi câu hỏi phản biện của Ban Giám khảo (dù là Bác sĩ hay Chuyên gia AI) đều tuân theo công thức trả lời 3 bước:\n"
        "1. Trực diện khẳng định: Trả lời 'Có/Không' hoặc nêu thẳng quan điểm, không vòng vo.\n"
        "2. Bản chất kỹ thuật/lâm sàng: Giải thích nguyên nhân cốt lõi và cơ chế hoạt động của hệ thống.\n"
        "3. Số liệu thực nghiệm: Bắn trúng đích bằng con số đo lường khoa học (1.320 tests, 0% sót dị ứng, giảm 14 lần lỗi nhớ nhầm)."
    )
    r_g2.font.size = Pt(9.0)
    r_g2.font.name = "Segoe UI"
    r_g2.font.color.rgb = COLOR_DARK

    doc.add_page_break()

    # =========================================================================
    # PHẦN 1: CÂU HỎI LÝ THUYẾT, NGHIỆP VỤ & SẢN PHẨM
    # =========================================================================
    them_tieu_de_phan(doc, "PHẦN 1: CÂU HỎI LÝ THUYẾT, NGHIỆP VỤ LÂM SÀNG & GIÁ TRỊ SẢN PHẨM")
    them_doan_van(doc, "Tập trung vào tính cấp thiết, nghiệp vụ phòng khám, giá trị bảo vệ người bệnh và trách nhiệm pháp lý.",
                  nghieng=True, co_chu=9.5, mau=COLOR_MUTED)

    # Cau 1
    them_hop_cau_hoi(
        doc, "q1",
        "Câu 1: MediTrace Sentinel giải quyết vấn đề gì lớn nhất trong bệnh viện?",
        [
            "• **Vấn đề giải quyết:** Bác sĩ ngoại trú tại Việt Nam đang bị quá tải khốc liệt (khám 50–80 ca/ngày, mỗi ca chỉ có 3–5 phút). Bác sĩ phải dành hơn 50% thời gian cắm cúi gõ bàn phím nhập bệnh án điện tử (EMR), dẫn đến kiệt sức (burnout), mất kết nối mắt với người bệnh và rất dễ ghi sót tiền sử dị ứng hoặc bệnh mạn tính.",
            "• **Giải pháp của MediTrace:** Đóng vai trò người trợ lý vô hình (Ambient Medical Scribe) ngồi cạnh lắng nghe cuộc trò chuyện tự nhiên giữa bác sĩ và người bệnh, tự động gỡ băng và dựng bản nháp bệnh án chuẩn cấu trúc SOAP. Bác sĩ chỉ mất 15–30 giây liếc mắt kiểm tra và bấm nút duyệt."
        ],
        mau_vien=HEX_SAFE, badge_text="Dễ"
    )

    # Cau 2
    them_hop_cau_hoi(
        doc, "q2",
        "Câu 2: Tại sao không dùng luôn ChatGPT, Claude hay Gemini cho nhanh và rẻ?",
        [
            "Có 3 lý do sống còn khiến việc dùng ChatGPT ở bệnh viện là **vi phạm pháp luật và nguy hiểm tính mạng**:",
            "1. **Vi phạm bảo mật (Nghị định 13/2023/NĐ-CP):** Dùng ChatGPT là gửi tên tuổi, bệnh tật của công dân Việt Nam lên máy chủ nước ngoài. MediTrace chạy 100% On-premise nội bộ, có bộ khử định danh giấu tên tự động, dữ liệu không bao giờ ra internet.",
            "2. **Ảo giác AI (Hallucination):** ChatGPT có xu hướng 'nói dối trơn tru', sẵn sàng tự điền con số huyết áp hoặc tiền sử bệnh mà bệnh nhân không hề nói. MediTrace có 7 cổng khóa K1–K7 dò từng chữ với thoại gốc, phát hiện bịa đặt là chặn ngay.",
            "3. **Không thể kiểm chứng:** ChatGPT trả ra một đoạn văn xuôi dài, bác sĩ muốn kiểm tra phải đọc lại cả băng ghi âm 15 phút. MediTrace có tính năng Click-to-Verify: bấm vào dòng nào trên bệnh án là sáng lên câu nói ở đúng giây ghi âm gốc."
        ],
        mau_vien=HEX_SAFE, badge_text="Dễ"
    )

    # Cau 3
    them_hop_cau_hoi(
        doc, "q3",
        "Câu 3: Bác sĩ rất bận, liệu việc bắt bác sĩ ngồi duyệt từng dòng có làm mất thêm thời gian không?",
        [
            "• **Không làm mất thời gian, mà tiết kiệm từ 5 đến 7 phút mỗi ca khám.**",
            "• Bác sĩ **không phải đọc lại toàn bộ từ đầu đến cuối**. Màn hình của MediTrace chia làm 2 phần trực quan:",
            "  - *Phần thân bệnh án:* Chứa những thông tin đã vượt qua toàn bộ 7 cổng kiểm tra (K1–K7) với độ tin cậy tuyệt đối.",
            "  - *Mục 'Cần bác sĩ xác nhận':* Chỉ gom đúng những điểm nghi ngờ (ví dụ: bệnh nhân nói nhầm, thuốc có tương tác kỵ nhau, câu giả định chưa rõ ràng) kèm cờ cảnh báo đỏ/vàng.",
            "• Bác sĩ chỉ cần liếc mắt đúng 15–30 giây vào các điểm cảnh báo, thấy đúng bấm nút duyệt là xong."
        ],
        mau_vien=HEX_NAVY, badge_text="Trung bình"
    )

    # Cau 4
    them_hop_cau_hoi(
        doc, "q4",
        "Câu 4: Nếu phần mềm ghi nhầm hoặc gợi ý sai dẫn đến tai biến y khoa thì ai chịu trách nhiệm?",
        [
            "• **Về mặt pháp lý:** Bác sĩ luôn là người chịu trách nhiệm chuyên môn cuối cùng. MediTrace được định vị chính xác là **Công cụ hỗ trợ soạn thảo bản nháp (Drafting Copilot)**, không phải bác sĩ điều trị và không tự động ra quyết định thay con người.",
            "• **Về mặt bảo vệ thầy thuốc:** MediTrace bảo vệ bác sĩ tốt hơn việc ghi chép tay:",
            "  1. Mọi dòng trong bệnh án đều có liên kết căn cứ trỏ về đúng câu nói của bệnh nhân -> Minh bạch nguồn gốc, tránh tranh chấp 'bệnh nhân bảo có nói mà bác sĩ không ghi'.",
            "  2. Sau khi bác sĩ bấm duyệt, bệnh án được niêm phong bằng chữ ký số băm SHA-256 chống sửa lén -> Bảo đảm tính pháp lý trước tòa án.",
            "  3. Tích hợp sẵn Dược thư Quốc gia để 'nhắc nhở' bác sĩ khi vô tình kê 2 thuốc kỵ nhau."
        ],
        mau_vien=HEX_NAVY, badge_text="Trung bình"
    )

    # Cau 5
    them_hop_cau_hoi(
        doc, "q5",
        "Câu 5: Trong y tế có sự đánh đổi: Kiểm tra quá chặt thì bỏ sót thông tin (Low Recall), nới lỏng thì bị sai (Low Precision). MediTrace giải quyết sự đánh đổi này như thế nào?",
        [
            "• **Hệ thống áp dụng triết lý 'Định tuyến bất đối xứng theo độ rủi ro' (Fail-Safe Asymmetric Routing):**",
            "  - Với thông tin thông thường (ví dụ: đau bụng âm ỉ, mệt mỏi): Ưu tiên độ chính xác (Precision). Nếu trượt bài kiểm tra K1–K7 thì loại khỏi thân bệnh án.",
            "  - Với thông tin nguy cấp (Dị ứng thuốc, Thuốc có khoảng điều trị hẹp như Digoxin/Warfarin, Bệnh tim mạch): **Tuyệt đối không bao giờ âm thầm xóa bỏ (Zero Information Loss)**.",
            "• **Giải pháp kỹ thuật:** Dù mẩu tin dị ứng có bị nghi ngờ (ví dụ người nhà nói lấp lửng), hệ thống vẫn giữ lại 100% và chuyển sang mục *'CẦN BÁC SĨ XÁC NHẬN'* kèm cờ đỏ.",
            "• **Kết quả thực nghiệm:** Tỷ lệ bỏ sót dị ứng giảm về **0.0%**, trong khi tỷ lệ thông tin đúng bị chặn nhầm đạt **0 / 30.136 dòng**."
        ],
        mau_vien=HEX_PURPLE, badge_text="Khó"
    )

    # Cau 6
    them_hop_cau_hoi(
        doc, "q6",
        "Câu 6: Người Việt Nam khi đi khám nói năng lộn xộn, hay nuốt chủ ngữ, xưng hô 'con/cháu/ông nhà', dùng từ địa phương ('trúng gió', 'xót ruột'). Làm sao hệ thống của bạn xử lý được?",
        [
            "Đây chính là 'vũ khí bản địa hóa' của MediTrace mà các mô hình nước ngoài không thể có:",
            "1. **Tầng 2 (Gom nhóm chủ thể - src/thuc_the.py):** Bộ luật ngữ pháp xử lý đại từ xưng hô Việt Nam. Phân biệt rõ: người mẹ nói *'Cháu nhà em bị sốt'* thì chủ thể bệnh là 'con' (id=1), không phải người mẹ (id=0).",
            "2. **Xử lý câu nuốt chủ ngữ:** Khi bệnh nhân nói *'Sốt 2 hôm nay rồi'*, ngữ cảnh lượt thoại được đối chiếu với vai người nói (Speaker Role). Nếu là bệnh nhân nói về bản thân thì tự động gán chủ thể 0.",
            "3. **Động cơ phương ngữ 3 miền (src/phuong_ngu_lam_sang.py):** Bộ từ điển hơn 60 thuật ngữ dân gian (Bắc - Trung - Nam) quy đổi về chuẩn y khoa: *'trúng gió'* -> liệt dây VII ngoại biên / cảm mạo; *'xót ruột/cồn cào'* -> viêm loét dạ dày; *'nấc cục'* -> nấc cụt.",
            "4. **Từ điển âm vị thuốc Tây:** Bệnh nhân đọc tên thuốc dân gian: *'a móc'* -> *Amoxicillin*; *'ô mê'* -> *Omeprazole*."
        ],
        mau_vien=HEX_PURPLE, badge_text="Khó"
    )

    doc.add_page_break()

    # =========================================================================
    # PHẦN 2: CÂU HỎI KỸ THUẬT, THUẬT TOÁN & CÔNG NGHỆ CHUYÊN SÂU
    # =========================================================================
    them_tieu_de_phan(doc, "PHẦN 2: CÂU HỎI KỸ THUẬT, THUẬT TOÁN & CÔNG NGHỆ CHUYÊN SÂU")
    them_doan_van(doc, "Tập trung vào kiến trúc Neuro-symbolic, tối ưu QLoRA, cơ chế khóa bằng chứng K1–K7, thước đo SER và Guardrails.",
                  nghieng=True, co_chu=9.5, mau=COLOR_MUTED)

    # Cau 7
    them_hop_cau_hoi(
        doc, "q7",
        "Câu 7: Kiến trúc tổng thể của MediTrace gồm những thành phần công nghệ nào?",
        [
            "• **Tầng 0 (ASR):** PhoWhisper (fine-tuned nhận dạng tiếng nói tiếng Việt) + PyAnnote Diarization (tách giọng người nói).",
            "• **Tầng 1 (Bóc tách thông tin):** Mô hình nguồn mở Qwen3-4B chạy kèm adapter huấn luyện QLoRA 4-bit (chạy ngay trên GPU máy trạm phòng khám).",
            "• **Tầng 2 đến Tầng 5 (Xử lý & Kiểm chứng):** 100% viết bằng Python thuật toán xác định (Deterministic Rule-Based, Máy trạng thái hữu hạn FSM, Bảng tra Dược thư Quốc gia, Template Engine).",
            "• **Giao diện Web:** React 19 + TypeScript + TailwindCSS, giao tiếp với backend qua REST API nội bộ (src/dich_vu.py)."
        ],
        mau_vien=HEX_SAFE, badge_text="Dễ"
    )

    # Cau 8
    them_hop_cau_hoi(
        doc, "q8",
        "Câu 8: Tại sao lại chọn mô hình Qwen3-4B mà không chọn Llama-3-8B hay mô hình lớn hơn?",
        [
            "1. **Khả năng triển khai tại phòng khám (Hardware Feasibility):** Các phòng khám Việt Nam chỉ trang bị máy tính phổ thông hoặc máy trạm có card đồ họa vừa phải (4GB – 8GB VRAM). Mô hình 8B cần tối thiểu 12GB–16GB VRAM, chi phí phần cứng quá đắt. Qwen3-4B QLoRA chỉ tốn ~3.8GB VRAM, chạy mượt trên card đồ họa phổ thông (như RTX 3050/3060).",
            "2. **Thời gian phản hồi:** Mô hình 4B xử lý bóc tách một ca khám chỉ mất ~30–45 giây trên GPU phổ thông, trong khi mô hình lớn mất từ 5–10 phút (không kịp cho ca khám tiếp theo).",
            "3. **Độ chính xác chuyên biệt:** Nhờ kỹ thuật huấn luyện QLoRA trên tập dữ liệu hội thoại y tế tiếng Việt chuẩn, Qwen3-4B đạt độ chính xác trích xuất tương đương mô hình 8B nhưng nhẹ hơn gấp đôi."
        ],
        mau_vien=HEX_SAFE, badge_text="Dễ"
    )

    # Cau 9
    them_hop_cau_hoi(
        doc, "q9",
        "Câu 9: Tại sao dự án chỉ dùng AI ở Tầng 1, còn Tầng 2–5 lại dùng thuật toán luật (Rule-based)? Sao không dùng AI làm hết (End-to-End)?",
        [
            "• **Đây là quyết định kiến trúc quan trọng nhất của dự án (Neuro-symbolic Architecture):**",
            "  - Điểm mạnh của AI (LLM) là: Đọc hiểu ngôn ngữ tự nhiên lộn xộn, nhận diện từ đồng nghĩa và nhặt mẩu tin.",
            "  - Điểm yếu chết người của AI là: Hay bịa đặt (hallucination), không làm toán chuẩn, không kiểm soát được ranh giới logic chặt chẽ.",
            "• **Nếu để AI làm từ đầu đến cuối (End-to-End):** Mô hình sẽ tự tiện gộp các câu khác chủ thể lại với nhau, biến câu dặn dò tương lai thành bệnh đã có, và khi sai thì không ai biết nó sai ở bước nào ('hộp đen').",
            "• **Khi tách thành luật ở Tầng 2–5:** Mọi quy tắc (đối soát chữ, tra thuốc kỵ nhau, cộng điểm thang điểm) đều minh bạch 100%, có thể viết Unit Test kiểm thử độc lập và sửa lỗi ngay lập tức mà không cần phải train lại AI."
        ],
        mau_vien=HEX_NAVY, badge_text="Trung bình"
    )

    # Cau 10
    them_hop_cau_hoi(
        doc, "q10",
        "Câu 10: Cơ chế Khóa bằng chứng K1–K7 ở Tầng 4 hoạt động cụ thể như thế nào để chặn Hallucination?",
        [
            "Mỗi mệnh đề được AI trích ra ở Tầng 1 bắt buộc phải có trường `trich_dan` (chuỗi trích dẫn nguyên văn) và `bang_chung` (lượt thoại [Ti]). Cổng khóa tại `src/khoa_bang_chung.py` thực thi 7 chốt chặn:",
            "• **K1 (Nguồn gốc nguyên văn):** Dò trực tiếp xâu ký tự `trich_dan` vào lượt thoại [Ti]. Nếu không có trong lượt thoại -> Bị CHẶN lập tức (`trich_khong_co`), đánh dấu Hallucination.",
            "• **K2 (Khớp nội dung):** Quét tỷ lệ trùng lặp từ ngữ lâm sàng cốt lõi.",
            "• **K3 (Khớp chủ thể):** Đối chiếu từ chỉ người trong lượt thoại với vai người được gán.",
            "• **K4 (Khớp mức khẳng định):** Phát hiện câu nghi ngờ hoặc câu điều kiện/phòng ngừa ('Nếu... thì...') mà bị ghi thành sự thật -> Bị CHẶN (`dieu_kien`).",
            "• **K5 (Khớp mốc thời gian):** Mốc thời gian phải có thật trong lượt thoại.",
            "• **K6 (Khớp liều lượng & thuốc):** Số lượng viên, hàm lượng mg phải trùng khớp với con số người nói nhắc đến.",
            "• **K7 (Kiểm tra đính chính - Superseded):** Nếu thông tin đã bị câu nói sau đính chính hoặc xét nghiệm loại trừ -> Đánh dấu bị thay thế, không cho vào thân bệnh án."
        ],
        mau_vien=HEX_NAVY, badge_text="Trung bình"
    )

    # Cau 11
    them_hop_cau_hoi(
        doc, "q11",
        "Câu 11: Tại sao trong báo cáo bạn khẳng định điểm ROUGE (thước đo AI văn bản phổ biến) là vô dụng trong đánh giá bệnh án? Bạn dùng thước đo nào thay thế?",
        [
            "• **Thực nghiệm chứng minh ROUGE vô dụng trong y tế:**",
            "  Trong thử nghiệm trên 400 ca bệnh của dự án, khi cố ý đổi chỗ chữ **'bệnh nhân'** và **'người nhà'** (ví dụ: biến bệnh hen của người nhà thành bệnh của bệnh nhân — một lỗi y khoa cực kỳ nghiêm trọng):",
            "  **Điểm ROUGE-1 vẫn đạt đúng 1.0000 (điểm tuyệt đối!)**",
            "  Lý do: ROUGE chỉ đếm số từ trùng lặp mà không hiểu ngữ nghĩa. Hoán đổi hai người thì tập hợp từ không hề thay đổi, nên ROUGE không phát hiện được lỗi!",
            "• **Thước đo thay thế của dự án:**",
            "  Dự án xây dựng bộ đo chuyên biệt **Entity Slot Error Rate (SER)** và **Attribution F1**:",
            "  - Đo đạc chính xác trên từng ô thuộc tính: (Chủ thể, Bệnh/Thuốc, Trạng thái, Thời gian).",
            "  - Đo tỷ lệ thông tin bị thay thế nhưng vẫn còn sót lại trong bản nháp (nhờ đó chứng minh Cổng K7 giảm tỷ lệ sót tin cũ từ 11.48% xuống **0.80%**)."
        ],
        mau_vien=HEX_PURPLE, badge_text="Khó"
    )

    # Cau 12
    them_hop_cau_hoi(
        doc, "q12",
        "Câu 12: Dữ liệu huấn luyện của bạn là dữ liệu mô phỏng (Synthetic Data). Làm sao chứng minh mô hình không bị 'học vẹt' (overfitting) và có tính tổng quát ngoài đời thực?",
        [
            "Dự án giải quyết triệt để vấn đề này qua 3 kỹ thuật khoa học:",
            "1. **Chia tách theo khuôn bệnh độc lập (Template-Disjoint Split):** 200 khuôn ca bệnh được chia thành tập Train, Dev, Test riêng biệt. Tập Test gồm những khuôn bệnh mà mô hình **chưa bao giờ nhìn thấy trong lúc huấn luyện**.",
            "2. **Đo đạc độ đa dạng từ vựng bằng toán học:** Đo khoảng cách Jaccard và n-gram diversity giữa 5.000 ca bệnh, chứng minh độ khác biệt giữa các ca đạt **78.3%** (không bị trùng lặp câu chữ).",
            "3. **Bộ dữ liệu Thử thách Cặp đôi (Adversarial Contrastive Pairs):** Tạo 300 ca thử thách theo cặp chỉ khác nhau đúng một yếu tố ranh giới (đổi người mang dị ứng, người nói tự đính chính sau 5 câu, chèn tiếng ồn ASR, phương ngữ 3 miền). Kết quả nhánh C của MediTrace vượt trội hoàn toàn so với nhánh A (AI thông thường) với F1 tăng từ 66.1% lên **70.8%** và SER giảm từ 45.4% xuống **36.9%**."
        ],
        mau_vien=HEX_PURPLE, badge_text="Khó"
    )

    # Cau 13
    them_hop_cau_hoi(
        doc, "q13",
        "Câu 13: Hệ thống Guardrails 5 chốt chặn vừa nâng cấp giải quyết hiện tượng Cascading Errors (Lỗi dây chuyền) như thế nào?",
        [
            "• **Cơ chế Cascading Error:** Nếu Tầng 0 (ASR) nghe sai từ *'Aspirin'* thành *'Amlodipin'*, Tầng 1 sẽ nhặt mẩu tin *'Amlodipin'*, Tầng 2 gán cho bệnh nhân, Tầng 3 lưu trạng thái. Đến Tầng 4 kiểm tra thì thấy câu trích vẫn khớp với đoạn gỡ băng (vì chính đoạn gỡ băng đã bị chép sai từ đầu!), dẫn đến bệnh án sai hoàn toàn.",
            "• **Cách Guardrails 5 tầng chặn đứng:**",
            "  - **Chốt 1 (ASR Guardrail):** Chạy ngay sau gỡ băng. Dò âm vị dược thư và từ điển phương ngữ, phát hiện từ lặp bất thường và tự động quy đổi cách đọc dân gian (*'a móc'* -> *Amoxicillin*) ngay tại nguồn.",
            "  - **Chốt 2 (Speaker Guardrail):** Rà soát mâu thuẫn đại từ nhân xưng ngay khi Tầng 1 vừa nhặt mẩu tin.",
            "  - **Chốt 3 (Dialogue Act Gate):** Bóc tách các câu đính chính (*'à không'*) và câu giả định (*'nếu mai sốt'*) trước khi đưa vào máy trạng thái.",
            "  - **Chốt 4 (Evidence Integrity Gate):** Soi xâu ký tự và đối soát từng con số sinh hiệu/liều thuốc.",
            "  - **Chốt 5 (Clinical Safety Gate):** Soi tương tác thuốc kỵ nhau DDI và liều trần trước khi xuất bệnh án.",
            "• **Kết quả:** Sai ở khâu nào bị chặn đứng và cô lập ngay ở khâu đó, không bao giờ lan truyền sang khâu tiếp theo."
        ],
        mau_vien=HEX_PURPLE, badge_text="Khó"
    )

    doc.add_page_break()

    # =========================================================================
    # PHẦN 3: CÂU HỎI "BẮT BẺ CHÍ MẠNG" (STRESS-TEST)
    # =========================================================================
    them_tieu_de_phan(doc, "PHẦN 3: BỘ CÂU HỎI 'BẮT BẺ CHÍ MẠNG' (STRESS-TEST) & CÁCH PHẢN BIỆN ĐOẠT ĐIỂM")
    them_doan_van(doc, "Các câu hỏi tình huống thực tế hóc búa nhất mà Giám khảo thường dùng để 'thử lửa' thí sinh.",
                  nghieng=True, co_chu=9.5, mau=COLOR_MUTED)

    # Cau 14: ASR Drug name mishearing
    them_hop_cau_hoi(
        doc, "q14",
        "❓ Giám khảo hỏi: 'Lúc ghi âm thực tế không thể đảm bảo thu nhận đúng 100% tín hiệu và câu từ, ví dụ tên thuốc bệnh nhân đọc hay bị sai hoặc ASR nghe nhầm ('a móc', 'ô mê', 'viên con nhộng đỏ'). Phần mềm có tự động sửa thành tên thuốc chính xác vào đơn không? Nhỡ AI đoán sai loại thuốc thì sao?'",
        [
            "🎯 **Phản biện tự tin:**",
            "'Thưa Ban Giám khảo, đây là câu hỏi chạm đúng vào **nguyên tắc an toàn y tế sống còn (Zero Silent Normalization)** của MediTrace Sentinel:",
            "1. **TUYỆT ĐỐI CẤM TỰ Ý SỬA NGẦM VÀO ĐƠN THUỐC:** Trong điều trị, chỉ một sai khác nhỏ về hoạt chất (ví dụ Amoxicillin đơn chất vs. Augmentin phối hợp Clavulanate) có thể gây kháng kháng sinh hoặc sốc phản vệ nguy hiểm tính mạng. Do đó, hệ thống cấm chỉ việc AI tự động 'đoán mò' rồi âm thầm điền tên thuốc vào đơn chính thức.",
            "2. **CƠ CHẾ BÔI ĐỎ & PHÂN VÙNG CÁCH LY AN TOÀN:** Mọi tên thuốc được gợi ý từ âm vị dân gian hoặc nhận diện trong điều kiện âm thanh không chắc chắn **bắt buộc phải BÔI ĐỎ (Red Badge cảnh báo cao nhất)** và chuyển thẳng sang mục **'CẦN BÁC SĨ XÁC NHẬN'**.",
            "3. **ĐỐI SOÁT CLICK-TO-VERIFY TRONG 1 GIÂY:** Trên giao diện, bác sĩ sẽ nhìn thấy ngay dòng cảnh báo nổi bật: `[BÔI ĐỎ - CẦN BÁC SĨ XÁC NHẬN TÊN THUỐC]: Tín hiệu ASR nghe là 'a móc' -> Gợi ý: 'Amoxicillin 500mg'`. Bác sĩ chỉ cần bấm vào mỏ neo âm thanh là nghe lại đúng 2 giây bệnh nhân nói trong băng ghi âm gốc để xác nhận hoặc gõ sửa lại.",
            "4. **QUY TRÌNH KÉP BẢO VỆ PHÁP LÝ:** Chỉ khi Bác sĩ bấm [Xác nhận đúng], tên thuốc mới được chuyển vào đơn chính thức và tiếp tục chạy qua Chốt Guardrail 5 để rà soát tương tác kỵ nhau (DDI) và liều trần. Quyết định chuyên môn 100% thuộc về Bác sĩ (Human-in-the-Loop), và hành động duyệt được ghi vết vào Audit Trail niêm phong chữ ký số SHA-256.'"
        ],
        mau_vien=HEX_DANGER, mau_nen="FFF1F2", badge_text="Stress-Test"
    )

    # Cau 15
    them_hop_cau_hoi(
        doc, "q15",
        "❓ Giám khảo hỏi: 'Nếu micrô phòng khám thu nhiều tạp âm, bệnh nhân nói lí nhí, ASR nghe sai be bét thì phần mềm của bạn có thành đống rác không?'",
        [
            "🎯 **Phản biện tự tin:**",
            "'Thưa Ban Giám khảo, đây chính là lý do MediTrace vượt trội hơn ChatGPT.",
            "Nếu là ChatGPT, khi gặp đoạn gỡ băng sai be bét, nó vẫn cố tình 'sáng tác' ra một bệnh án đọc rất mượt nhưng sai sự thật -> cực kỳ nguy hiểm.",
            "Còn với MediTrace, nhờ Chốt Guardrail 1 và Cổng K1: Khi âm thanh bị nhiễu hoặc không rõ ràng, hệ thống sẽ phát hiện độ tin cậy thấp (Low Confidence) và câu trích không đủ căn cứ. Mẩu tin đó **lập tức bị chặn lại và chuyển sang mục 'Cần bác sĩ xác nhận'** chứ tuyệt đối không bao giờ được ghi vào bệnh án chính thức. Thà để bác sĩ tự điền bằng tay còn hơn để phần mềm tự bịa thông tin sai!'"
        ],
        mau_vien=HEX_DANGER, mau_nen="FFF1F2", badge_text="Stress-Test"
    )

    # Cau 16
    them_hop_cau_hoi(
        doc, "q16",
        "❓ Giám khảo hỏi: 'Một ngày khám 80 ca, nhỡ bác sĩ bận quá quên bấm duyệt mà tắt máy về thì dữ liệu có bị mất không?'",
        [
            "🎯 **Phản biện tự tin:**",
            "'Hệ thống thiết kế cơ chế tự động lưu trữ tức thời (Auto-Save Persistence) vào cơ sở dữ liệu SQLite cục bộ tại phòng khám sau mỗi lượt thoại. Toàn bộ phiên âm thanh, các mẩu tin trích xuất và bản nháp đều được lưu vết. Nếu bác sĩ bị ngắt quãng ca khám để đi cấp cứu hoặc tắt máy đột ngột, khi mở lại phần mềm, ca khám vẫn hiển thị nguyên vẹn ở trạng thái 'Chờ duyệt' để bác sĩ kiểm tra tiếp mà không bị mất một chữ nào.'"
        ],
        mau_vien=HEX_DANGER, mau_nen="FFF1F2", badge_text="Stress-Test"
    )

    # Cau 17
    them_hop_cau_hoi(
        doc, "q17",
        "❓ Giám khảo hỏi: 'Dự án của bạn đã kiểm thử trên bao nhiêu ca bệnh và độ ổn định thực tế ra sao?'",
        [
            "🎯 **Phản biện tự tin:**",
            "'Hệ thống đã trải qua bộ kiểm thử tự động toàn diện với **1.330 bài test tự động (Unit & Integration Tests)** bao phủ toàn bộ 14 module lâm sàng, 7 cổng khóa bằng chứng và các tình huống kiểm thử nghịch đảo. Hiện tại, toàn bộ 1.330 bài test đều vượt qua 100% không có lỗi.",
            "Ngoài ra, cơ sở dữ liệu khuôn bệnh đã được nâng cấp lên **200 khuôn ca bệnh thuộc 10 chuyên khoa lâm sàng**, với hơn 5.000 hội thoại mô phỏng và 300 ca thử thách đối đầu ranh giới, bảo đảm hệ thống sẵn sàng hoạt động ổn định trong môi trường thực tế.'"
        ],
        mau_vien=HEX_DANGER, mau_nen="FFF1F2", badge_text="Stress-Test"
    )

    # THONG DIEP CHOT
    them_hop_cau_hoi(
        doc, "conclusion",
        "🏆 THÔNG ĐIỆP CHỐT HẠ ĐOẠT ĐIỂM TUYỆT ĐỐI:",
        [
            "**'MediTrace Sentinel không phải là một công cụ AI biểu diễn công nghệ viết văn.**",
            "Đây là một giải pháp y tế số an toàn được xây dựng bằng tư duy lâm sàng thực chiến: **Đặt an toàn tính mạng người bệnh lên hàng đầu, triệt tiêu ảo giác bằng luật toán học xác định, và giải phóng đôi tay người thầy thuốc.'**"
        ],
        mau_vien=HEX_NAVY, mau_nen="F1F5F9", badge_text="Kết luận"
    )

    # Luu file
    doc.save(str(FILE_OUT_GOC))
    doc.save(str(FILE_OUT_DOCS))
    try:
        doc.save(r"C:\Users\admin\Downloads\Bo_Cau_Hoi_Va_Tra_Loi_Ban_Giam_Khao_MediTrace.docx")
        doc.save(r"C:\Users\admin\Desktop\Bo_Cau_Hoi_Va_Tra_Loi_Ban_Giam_Khao_MediTrace.docx")
    except Exception as e:
        print(f"Luu Desktop/Downloads: {e}")
    print(f"Da xuat xong file Word dep tai:\n-> {FILE_OUT_GOC}\n-> {FILE_OUT_DOCS}")


if __name__ == "__main__":
    tao_word_qna()
