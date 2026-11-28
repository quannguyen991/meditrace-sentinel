# -*- coding: utf-8 -*-
"""Script tao file Word (.docx) cho Bo Cau hoi & Tra loi Ban Giam khao.
Thiet ke theo tieu chuan an pham trinh bay chuyen nghiep:
- Font Segoe UI dong nhat, mau sac Navy & Teal trang nha
- Co Phan 0 trinh bay ro cau truc du an (3 khoi, 6 goi Python, 5 tang, Full-stack Web)
- Hop cau hoi co vien mau, nen sang kem huy hieu muc do (De, Trung binh, Kho, Stress-test)
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
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Segoe UI"
    r.font.size = Pt(13.5)
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
        elif badge_text.lower() in ("kiến trúc", "cấu trúc"):
            r_badge.font.color.rgb = COLOR_TEAL
        else:
            r_badge.font.color.rgb = COLOR_DANGER

    r_q = p.add_run(tieu_de_cau_hoi + "\n")
    r_q.bold = True
    r_q.font.size = Pt(10.8)
    r_q.font.name = "Segoe UI"
    r_q.font.color.rgb = COLOR_DARK

    for dong in noi_dung_tra_loi:
        p_ans = cell.add_paragraph()
        p_ans.paragraph_format.space_before = Pt(2)
        p_ans.paragraph_format.space_after = Pt(3)
        p_ans.paragraph_format.line_spacing = 1.15

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

    them_doan_van(doc, "", cach_duoi=2)


def them_bang_cau_truc(doc, rows):
    tbl = doc.add_table(rows=len(rows) + 1, cols=3)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Thư mục / Gói", "Vai trò kiến trúc", "Mô-đun tiêu biểu & Quy mô thực tế"]
    widths = [Inches(1.5), Inches(2.2), Inches(3.1)]

    for col_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, col_idx)
        cell.width = widths[col_idx]
        dat_nen_o(cell, HEX_NAVY)
        dat_vien_o(cell, top=HEX_NAVY, bottom=HEX_NAVY, left=HEX_NAVY, right=HEX_NAVY, sz="4")
        dat_le_o(cell, top=70, bottom=70, left=90, right=90)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.bold = True
        r.font.name = "Segoe UI"
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for r_idx, (pkg, role, modules) in enumerate(rows, start=1):
        bg = "FFFFFF" if r_idx % 2 == 1 else "F8FAFC"
        for col_idx, text in enumerate((pkg, role, modules)):
            cell = tbl.cell(r_idx, col_idx)
            cell.width = widths[col_idx]
            dat_nen_o(cell, bg)
            dat_vien_o(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1", sz="4")
            dat_le_o(cell, top=60, bottom=60, left=90, right=90)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.12
            r = p.add_run(text)
            r.bold = (col_idx == 0)
            r.font.name = "Segoe UI"
            r.font.size = Pt(8.5)
            r.font.color.rgb = COLOR_TEAL if col_idx == 0 else COLOR_DARK

    them_doan_van(doc, "", cach_duoi=4)


def tao_word_qna():
    doc = docx.Document()

    # Thiet lap le trang A4
    for section in doc.sections:
        section.top_margin = Inches(0.65)
        section.bottom_margin = Inches(0.65)
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
    dat_le_o(cell_top, top=150, bottom=150, left=180, right=180)

    p_top = cell_top.paragraphs[0]
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_top1 = p_top.add_run("MEDITRACE SENTINEL — AMBIENT CLINICAL INTELLIGENCE\n")
    r_top1.bold = True
    r_top1.font.size = Pt(11)
    r_top1.font.name = "Segoe UI"
    r_top1.font.color.rgb = RGBColor(0x99, 0xF6, 0xE4)

    r_top_title = p_top.add_run("BỘ CÂU HỎI & TRẢ LỜI PHẢN BIỆN BAN GIÁM KHẢO\n")
    r_top_title.bold = True
    r_top_title.font.size = Pt(17.5)
    r_top_title.font.name = "Segoe UI"
    r_top_title.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    r_top2 = p_top.add_run("BẢN ĐỒ CẤU TRÚC DỰ ÁN · CÂU HỎI LÝ THUYẾT, KỸ THUẬT & STRESS-TEST (DỮ LIỆU ĐÃ KIỂM CHỨNG)")
    r_top2.italic = True
    r_top2.font.size = Pt(8.8)
    r_top2.font.name = "Segoe UI"
    r_top2.font.color.rgb = RGBColor(0xCC, 0xFB, 0xF1)

    them_doan_van(doc, "", cach_duoi=4)

    # 4 o chi so thuc nghiem trung thuc
    tbl_stats = doc.add_table(rows=1, cols=4)
    tbl_stats.alignment = WD_TABLE_ALIGNMENT.CENTER
    stats = [
        ("KIỂM THỬ TỰ ĐỘNG", "1.942 & 96 PASS", "Pytest (27 skip, 26/11) + Web TS", HEX_SAFE, "ECFDF5"),
        ("CHẶN LỖI NGUY HIỂM", "88,2% (CHÍNH SÁCH D)", "11,8% lọt dev (lạc quan) | Giữ kín 0,946", HEX_DANGER, "FEF2F2"),
        ("CHẶN ẢO GIÁC", "7 CỔNG K1–K7", "Chặn thừa 8,0–10,0% trên đầu ra mô hình", HEX_TEAL, "F0FDFA"),
        ("GIẢM SÓT ĐÍNH CHÍNH", "11,48% -> 0,80%", "Giảm > 14 lần tin cũ bị thay thế", HEX_WARN, "FFFBEB")
    ]
    for idx, (label, val, desc, border_c, bg_c) in enumerate(stats):
        cell = tbl_stats.cell(0, idx)
        cell.width = Inches(1.7)
        dat_nen_o(cell, bg_c)
        dat_vien_o(cell, top=border_c, bottom=border_c, left=border_c, right=border_c, sz="6")
        dat_le_o(cell, top=60, bottom=60, left=70, right=70)

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
        r_v.font.size = Pt(10)
        r_v.font.name = "Segoe UI"
        r_v.font.color.rgb = COLOR_NAVY

        r_d = p.add_run(desc)
        r_d.font.size = Pt(7.3)
        r_d.font.name = "Segoe UI"
        r_d.font.color.rgb = COLOR_MUTED

    them_doan_van(doc, "", cach_duoi=4)

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
        "Mọi câu hỏi phản biện của Ban Giám khảo đều tuân theo công thức trả lời 3 bước:\n"
        "1. Trực diện khẳng định: Trả lời thẳng trọng tâm câu hỏi, không vòng vo.\n"
        "2. Bản chất kỹ thuật/lâm sàng: Gắn đúng tên mô-đun thật trong mã nguồn (src/ và web/).\n"
        "3. Số liệu trung thực: Dùng đúng các con số đã đo (1.942 pytest + 96 TS tests, Chính sách D chặn 88,2% lỗi nguy hiểm / còn 11,8% trên 4 tập dev — số lạc quan vì luật chỉnh trên chính các tập này, giữ kín 0,946/0,871, giảm >14 lần lỗi đính chính) và chủ động nêu cả giới hạn còn lại."
    )
    r_g2.font.size = Pt(8.8)
    r_g2.font.name = "Segoe UI"
    r_g2.font.color.rgb = COLOR_DARK

    # =========================================================================
    # PHẦN 0: CẤU TRÚC DỰ ÁN & BẢN ĐỒ KIẾN TRÚC TỔNG THỂ
    # =========================================================================
    them_tieu_de_phan(doc, "PHẦN 0: CẤU TRÚC DỰ ÁN & BẢN ĐỒ KIẾN TRÚC TỔNG THỂ")
    them_doan_van(doc, "Tóm tắt tổ chức mã nguồn theo mô hình 3 khối – 6 gói Python lõi – 5 tầng Neuro-Symbolic và Web Full-Stack.",
                  nghieng=True, co_chu=9.2, mau=COLOR_MUTED)

    them_hop_cau_hoi(
        doc, "p0_flow",
        "Luồng xử lý đầu – cuối từ Âm thanh phòng khám đến Sổ ký duyệt WORM",
        [
            "1. **Tầng 0 (ASR & Âm thanh - src/audio/):** PhoWhisper + PyAnnote tách giọng người nói + Trie 65+ G2P tên thuốc (`contextual_trie_600.py`, chỉ gợi ý, không tự sửa ngầm).",
            "2. **B0 (Chuẩn hóa phương ngữ - src/duong_ong/b0_chuan_hoa_phuong_ngu.py):** Quy đổi phương ngữ 3 miền kèm khóa bảo vệ ngữ cảnh lâm sàng ('tứ chi', 'mô mềm', 'cấy ghép', 'vô kinh', 'bờ mi').",
            "3. **B1 (Rút mệnh đề bằng AI - src/duong_ong/b1_cau_truc_menh_de.py):** Khâu DUY NHẤT dùng LLM (`Qwen3-4B QLoRA 4-bit`) để bóc từng mệnh đề `PhatBieu` gắn `bang_chung [T_i]` và `trich_dan` nguyên văn.",
            "4. **B2 & B3 (Chủ thể & Trạng thái FSM - b2_*, b3_*):** Gom nhóm người nói/bù chủ ngữ tỉnh lược -> Máy trạng thái FSM đánh dấu đính chính `DA_THAY_THE`.",
            "5. **B4 (Khóa căn cứ K1–K7 - b4_kiem_can_cu.py):** 7 cổng xác định kiểm tra nguyên văn, từ khóa lâm sàng, chủ thể, phủ định/giả định, thời gian, liều lượng (`s.ho == 'lieu'`), đính chính.",
            "6. **B5, B6, Cảnh báo & Lâm sàng (b5_*, src/canh_bao/, src/cong_cu_lam_sang/):** Định tuyến rủi ro (Chính sách C/D), 13 nhóm/56 mã cảnh báo, 158 hoạt chất Dược thư, DDI, TT 26/2025.",
            "7. **BFF + WORM + React UI (web/may-chu/ + web/src/):** Hàng đợi nền `202 Accepted` trong SQLite -> Bác sĩ rà `Cần xác nhận` + Click-to-Verify -> Sổ WORM SHA-256 (`.anchor.json`)."
        ],
        mau_vien=HEX_TEAL, mau_nen="F0FDFA", badge_text="Kiến trúc"
    )

    cau_truc_rows = [
        ("src/audio/", "Thu nhận âm thanh, ASR & Diarization", "pipeline.py, phowhisper_provider.py, disagreement.py, contextual_trie_600.py (65+ G2P gợi ý)"),
        ("src/bo_du_lieu/", "Kho khuôn bệnh, chia tập chống rò rỉ & giả lập", "kho_khuon.py (657 khuôn, 21 hệ cơ quan), chia_tap_theo_khuon.py (515/72/70), ca_mau_bgk.py"),
        ("src/duong_ong/", "Lõi Neuro-Symbolic B0–B6", "chay_duong_ong.py, b0..b6 (PhatBieu, chủ thể, FSM đính chính, K1–K7, định tuyến rủi ro, SOAP)"),
        ("src/canh_bao/", "Phát hiện & gom nhóm cảnh báo 3 mức", "loai.py (13 nhóm, 56 mã gồm thuoc_nti), phat_hien.py, toan_ca.py, gop.py"),
        ("src/cong_cu_lam_sang/", "Dược lý, thang điểm, BHYT & chuẩn bệnh viện", "tra_duoc_thu_aho_corasick.py (158 hoạt chất), DDI, 9 thang điểm, TT 26/2025, FHIR R4, LIS/HL7, QR"),
        ("src/do_luong/", "Bộ chấm SER, F1, lặp câu & ngoài khuôn", "cham_he_thong.py, do_canh_bao.py, do_lap_cau.py, do_vidia2std.py, kiem_nghiem_ngoai_khuon.py"),
        ("src/he_thong/", "HTTP Service (:8765), PII, 5 chốt & WORM", "dich_vu_http.py, hop_dong_api.py, khu_dinh_danh.py, dieu_phoi_cac_chot_an_toan.py, nhat_ky_ky_duyet_worm.py"),
        ("src/huan_luyen/", "Huấn luyện SFT / DPO / RLVR cho Qwen3-4B", "chon_mo_hinh_bakeoff.py, huan_luyen_sft.py, huan_luyen_dpo.py, loss_theo_doan.py"),
        ("web/may-chu/", "Node/Express BFF + SQLite WAL + WORM", "csdl.ts, hang-doi.ts (202 Accepted), worm.ts (SHA-256 + .anchor.json), tro-ly/an-danh.ts"),
        ("web/src/", "Giao diện React 19 + TS + Tailwind", "TranscriptView, VerificationView (J/K/Enter/Space), DuyetBenCanh, HisSmartCopyPopover, BhytPrecheckModal, useTurnAudioPlayer"),
        ("tools/, tests/, docs/", "Đo đa nguồn, xuất báo cáo & kiểm thử", "do_da_nguon_doc_lap.py (5 nguồn ngoài), tao_word_qna_giam_khao.py, 1.942 pytest + 96 TS tests")
    ]
    them_bang_cau_truc(doc, cau_truc_rows)

    doc.add_page_break()

    # =========================================================================
    # PHẦN 1: CÂU HỎI LÝ THUYẾT, NGHIỆP VỤ & SẢN PHẨM
    # =========================================================================
    them_tieu_de_phan(doc, "PHẦN 1: CÂU HỎI LÝ THUYẾT, NGHIỆP VỤ LÂM SÀNG & GIÁ TRỊ SẢN PHẨM")
    them_doan_van(doc, "Tập trung vào tính cấp thiết, nghiệp vụ phòng khám, bảo mật, định tuyến rủi ro và bản địa hóa tiếng Việt.",
                  nghieng=True, co_chu=9.2, mau=COLOR_MUTED)

    # Cau 1
    them_hop_cau_hoi(
        doc, "q1",
        "Câu 1: MediTrace Sentinel giải quyết vấn đề gì lớn nhất trong bệnh viện?",
        [
            "• **Vấn đề giải quyết:** Bác sĩ ngoại trú tại bệnh viện đông bệnh nhân vừa khám hỏi vừa phải nhập bệnh án điện tử (EMR/HIS), dễ quá tải (burnout), giảm giao tiếp trực tiếp với người bệnh và có nguy cơ ghi sót tiền sử hoặc dị ứng.",
            "• **Giải pháp của MediTrace:** Đóng vai trò **trợ lý dựng bản nháp bệnh án theo nguồn thoại (Evidence-Linked Ambient Clinical Scribe)**: lắng nghe cuộc hội thoại, gỡ băng, bóc tách cấu trúc SOAP kèm câu trích nguyên văn và gom sẵn các điểm rủi ro vào hàng đợi 'Cần xác nhận'. Bác sĩ dùng phím tắt (`J/K/Enter/Space`, `Giữ nhanh`) và copy nhanh sang HIS qua `HisSmartCopyPopover`."
        ],
        mau_vien=HEX_SAFE, badge_text="Dễ"
    )

    # Cau 2
    them_hop_cau_hoi(
        doc, "q2",
        "Câu 2: Tại sao không dùng luôn ChatGPT, Claude hay Gemini cho nhanh và rẻ?",
        [
            "Trước hết, cần nói thẳng: dự án **chưa chạy so sánh đầy đủ** với mô hình thương mại. Phép đo duy nhất có thật (173/300 ca, dừng do hết số dư) cho thấy mô hình thương mại **ghi nhầm người ít hơn** mô hình nhỏ của dự án: 1,4% so với 7,6% ở bộ đính chính, 15,4% so với 22,9% ở bộ đổi chủ thể (`README.md`). Lý do dự án vẫn chọn cách làm riêng:",
            "1. **Dữ liệu người bệnh không cần rời phòng khám:** Lời thoại có họ tên, địa chỉ, số điện thoại, số CCCD là dữ liệu cá nhân nhạy cảm theo Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 và Nghị định 356/2025/NĐ-CP (hiệu lực 01/01/2026). Dự án không đánh giá việc dùng dịch vụ đám mây là đúng hay sai luật. MediTrace mặc định chạy **100% On-premise nội bộ** (`PhoWhisper` + `Qwen3-4B` + `SQLite`). Chế độ trợ lý bên ngoài mặc định **TẮT** (`MEDITRACE_TRO_LY_NGOAI=tat`); nếu bật vẫn phải đi qua bộ lọc allowlist khử định danh (`web/may-chu/tro-ly/an-danh.ts` & `src/he_thong/khu_dinh_danh.py`).",
            "2. **Rủi ro ảo giác AI (Hallucination):** Chatbot tổng quát có thể tự điền thông tin bệnh nhân không nói hoặc trộn bệnh của người nhà thành của bệnh nhân. MediTrace áp dụng 7 cổng khóa căn cứ **K1–K7** (`src/duong_ong/b4_kiem_can_cu.py`) để chặn và gắn cờ các mệnh đề sai nguồn.",
            "3. **Khả năng kiểm chứng tức thì:** Thay vì trả một đoạn văn xuôi dài khó dò, MediTrace gắn từng dòng với lượt thoại `[T_i]` và đoạn âm thanh gốc qua `useTurnAudioPlayer.ts` (Click-to-Verify)."
        ],
        mau_vien=HEX_SAFE, badge_text="Dễ"
    )

    # Cau 3
    them_hop_cau_hoi(
        doc, "q3",
        "Câu 3: Bác sĩ rất bận, liệu việc bắt bác sĩ ngồi duyệt từng dòng có làm mất thêm thời gian không?",
        [
            "• **Thiết kế giao diện hướng tới giảm thao tác đọc dư thừa, không bắt bác sĩ đọc lại toàn bộ từ đầu đến cuối** (đội ngũ chưa công bố con số 'tiết kiệm X phút/ca' ngoài đời thực khi chưa hoàn tất thử nghiệm đo thời gian trực tiếp trên bác sĩ lâm sàng).",
            "• Màn hình duyệt (`VerificationView.tsx` & `DuyetBenCanh.tsx`) chia thành 2 phần rõ ràng:",
            "  - **Phần thân bản nháp (đã qua K1–K7 và không vướng cờ rủi ro):** Gom các mệnh đề đạt căn cứ, hỗ trợ thao tác 'Giữ nhanh' thay vì sửa tay từng dòng.",
            "  - **Mục 'Cần bác sĩ xác nhận':** Chỉ gom những điểm nghi ngờ hoặc nguy cấp (đính chính, câu giả định, thuốc khoảng điều trị hẹp, tên thuốc G2P gợi ý, tương tác thuốc) để xử lý bằng phím tắt `J / K / Enter / Space`.",
            "• Ngoài ra, khâu suy luận nặng chạy qua hàng đợi nền `202 Accepted` (`web/may-chu/hang-doi.ts`), bác sĩ chuyển sang ca khám tiếp theo ngay mà không đứng chờ."
        ],
        mau_vien=HEX_NAVY, badge_text="Trung bình"
    )

    # Cau 4
    them_hop_cau_hoi(
        doc, "q4",
        "Câu 4: Nếu phần mềm ghi nhầm hoặc gợi ý sai dẫn đến tai biến y khoa thì ai chịu trách nhiệm?",
        [
            "• **Về mặt pháp lý:** Bác sĩ khám chữa bệnh luôn là người chịu trách nhiệm chuyên môn cuối cùng. MediTrace được định vị là **công cụ hỗ trợ soạn thảo bản nháp có căn cứ (Source-Grounded Drafting Copilot)**, không tự động ra y lệnh.",
            "• **Về mặt kỹ thuật bảo vệ thầy thuốc và kiểm toán nội bộ:**",
            "  1. **Truy vết hai chiều:** Mọi dòng bệnh án đều gắn `bang_chung [T_i]`, `trich_dan` nguyên văn và đoạn âm thanh gốc.",
            "  2. **Khóa ký duyệt + Sổ kiểm toán WORM:** Cổng `sign-off.ts` khóa ký duyệt nếu còn mục 'Cần xác nhận' chưa xử lý. Sau khi duyệt, `web/may-chu/worm.ts` & `nhat_ky_ky_duyet_worm.py` nối chuỗi băm **SHA-256** (`prev_hash` -> `entry_hash`) kèm tệp neo ngoại biên `.anchor.json` để phát hiện sửa/xoá lén dưới SQLite (là sổ kiểm toán kỹ thuật nội bộ, chưa thay thế chữ ký số CA).",
            "  3. **Cảnh báo dược lý:** Bộ tra **158 hoạt chất** Aho-Corasick và kiểm tra tương tác thuốc (DDI) / cân nặng trẻ em TT 26/2025 nhắc bác sĩ trước khi hoàn tất đơn."
        ],
        mau_vien=HEX_NAVY, badge_text="Trung bình"
    )

    # Cau 5
    them_hop_cau_hoi(
        doc, "q5",
        "Câu 5: Trong y tế có sự đánh đổi: Kiểm tra quá chặt thì bỏ sót thông tin (Low Recall), nới lỏng thì bị sai (Low Precision). MediTrace giải quyết sự đánh đổi này như thế nào?",
        [
            "• **Hệ thống áp dụng triết lý 'Định tuyến bất đối xứng theo độ rủi ro' (Fail-Safe Asymmetric Routing)** tại `b5_xep_cho_cong_rui_ro.py` và `src/canh_bao/`:",
            "  - Với thông tin nhẹ: Ưu tiên độ chính xác (Precision), trượt K1–K7 thì không đưa vào thân bệnh án sạch.",
            "  - Với nhóm nguy cấp (Dị ứng, Thuốc khoảng điều trị hẹp `thuoc_nti` như Digoxin/Warfarin, Đe dọa tính mạng, Lẫn người nhà, Bất đồng liều): Giữ lại trong mục 'CẦN BÁC SĨ XÁC NHẬN' kèm cờ đỏ/vàng, khóa ký duyệt cho tới khi bác sĩ quyết định.",
            "• **Kết quả thực nghiệm đã đo & minh bạch phạm vi:**",
            "  - Trên phép đo cấy lỗi có đăng ký trước (`docs/ket-qua/cay-loi.md`), độ nhạy bắt lỗi xoá dị ứng đạt **98,3%** (tập điều chỉnh 400 ca) và **97,2%** (tập giữ kín 240 ca). Chặn nhầm đáp án chuẩn ở K1–K7 là **0 / 30.136 dòng**, nhưng số này chỉ đúng vì đáp án mô phỏng chép gần nguyên văn hội thoại (độ phủ 0,95); trên đầu ra mô hình thật, chặn thừa là **8,0%** (C) / **10,0%** (D).",
            "  - Trên **4 bộ thử thách phát triển** (300 ca, 2.789 phát biểu dùng để tinh chỉnh luật), khi nâng cấp từ Chính sách C lên **Chính sách D**, tỷ lệ lọt lỗi nguy hiểm vào thân (`lot_nguy_hiem`) giảm từ **45,9% (101/220) xuống 11,8% (26/220)** — tức **chặn được 88,2% (194/220)** lỗi nguy hiểm bộ chấm gắn nhãn, với chặn thừa tăng từ 8,0% lên **10,0%**. Vì luật được chỉnh khi nhìn chính các tập này, 11,8% là số **lạc quan**. Trên tập giữ kín `thach_thuc_v2` (240 ca), độ nhạy phát hiện đạt **0,871**, đổi chủ thể đạt **0,946**."
        ],
        mau_vien=HEX_PURPLE, badge_text="Khó"
    )

    # Cau 6
    them_hop_cau_hoi(
        doc, "q6",
        "Câu 6: Người Việt Nam khi đi khám nói năng lộn xộn, hay nuốt chủ ngữ, xưng hô 'con/cháu/ông nhà', dùng từ địa phương ('trúng gió', 'xót ruột'). Làm sao hệ thống của bạn xử lý được?",
        [
            "Gồm 4 lớp bản địa hóa phối hợp:",
            "1. **Gom nhóm chủ thể xưng hô tiếng Việt (`b2_gom_nguoi_thuc_the.py`):** Tách rạch ròi `nguoi_noi` với `chu_the_id` (mẹ nói 'Cháu nhà em sốt' -> gán chủ thể là con/cháu, không lẫn sang mẹ).",
            "2. **Bù chủ ngữ tỉnh lược (`b2_bu_chu_ngu_tinh_luoc.py`):** Câu cụt không chủ ngữ được đối chiếu vai `nguoi_noi` và bối cảnh lượt thoại liền kề.",
            "3. **Chuẩn hóa phương ngữ 3 miền có khóa bảo vệ ngữ cảnh (`b0_chuan_hoa_phuong_ngu.py` & `tu_dien_phuong_ngu_lam_sang.py`):** Quy đổi từ Bắc–Trung–Nam kèm guard tránh sửa nhầm cụm y khoa ('tứ chi', 'mô mềm', 'cấy ghép', 'vô kinh', 'bờ mi'). Đo trên `ViDia2Std/test.csv` (1.603 câu): đúng chuẩn xác **27,8%** (1.185/4.264), tổng độ phủ **37,0%**, kéo WER giảm từ **30,1% xuống 22,0%** (43 đổi thừa).",
            "4. **Gợi ý âm vị G2P (`contextual_trie_600.py`) & Dược thư (`tra_duoc_thu_aho_corasick.py`):** **65+** ánh xạ phiên âm thuốc dân gian kèm khóa ngữ cảnh thuốc ('uống/viên/mg/đơn') và **158 hoạt chất** chuẩn, luôn ở dạng gợi ý chờ bác sĩ xác nhận."
        ],
        mau_vien=HEX_PURPLE, badge_text="Khó"
    )

    doc.add_page_break()

    # =========================================================================
    # PHẦN 2: CÂU HỎI KỸ THUẬT, THUẬT TOÁN & CÔNG NGHỆ CHUYÊN SÂU
    # =========================================================================
    them_tieu_de_phan(doc, "PHẦN 2: CÂU HỎI KỸ THUẬT, THUẬT TOÁN & CÔNG NGHỆ CHUYÊN SÂU")
    them_doan_van(doc, "Tập trung vào kiến trúc 5 tầng, Qwen3-4B QLoRA, chia mệnh đề PhatBieu, khóa bằng chứng K1–K7, SER và Guardrails.",
                  nghieng=True, co_chu=9.2, mau=COLOR_MUTED)

    # Cau 7
    them_hop_cau_hoi(
        doc, "q7",
        "Câu 7: Kiến trúc tổng thể của MediTrace gồm những thành phần công nghệ nào?",
        [
            "• **Tầng 0 — Âm thanh & Tiền xử lý (`src/audio/` + `B0`):** PhoWhisper + PyAnnote tách giọng, đo bất đồng ASR (`disagreement.py`), trie gợi ý 65+ G2P thuốc (`contextual_trie_600.py`) và chuẩn hóa phương ngữ 3 miền (`b0_chuan_hoa_phuong_ngu.py`).",
            "• **Tầng 1 — Rút mệnh đề bằng AI (`b1_cau_truc_menh_de.py`):** Mô hình **Qwen3-4B QLoRA 4-bit** là khâu DUY NHẤT dùng LLM, xuất danh sách `PhatBieu` kèm căn cứ nguyên văn.",
            "• **Tầng 2 đến Tầng 5 — Chuỗi thuật toán xác định (`src/duong_ong/`, `src/canh_bao/`, `src/cong_cu_lam_sang/`):** 100% Python xác định gồm gom chủ thể/bù tỉnh lược (`B2`), FSM đính chính (`B3`), 7 cổng K1–K7 (`B4`), định tuyến Chính sách C/D & SOAP (`B5`), gợi ý hỏi lại (`B6`), 13 nhóm/56 mã cảnh báo, Dược thư 158 hoạt chất, DDI, 9 thang điểm, TT 26/2025 và FHIR R4.",
            "• **Tầng Ứng dụng Web & Lưu trữ (`web/may-chu/` + `web/src/` + `src/he_thong/`):** Node/Express BFF + SQLite WAL + hàng đợi `202 Accepted` + WORM SHA-256 (`.anchor.json`), React 19 + TS + Tailwind và dịch vụ HTTP Python (`dich_vu_http.py` cổng `8765`)."
        ],
        mau_vien=HEX_SAFE, badge_text="Dễ"
    )

    # Cau 8
    them_hop_cau_hoi(
        doc, "q8",
        "Câu 8: Tại sao lại chọn mô hình Qwen3-4B mà không chọn Llama-3-8B hay mô hình lớn hơn?",
        [
            "1. **Khả năng triển khai phần cứng (Hardware Feasibility):** Máy trạm phòng khám phổ thông thường chỉ có **6GB–8GB VRAM** (như RTX 3050/3060). Mô hình 8B trở lên đòi hỏi VRAM và chi phí đầu tư cao hơn hẳn, trong khi **Qwen3-4B QLoRA 4-bit** chạy vừa trên GPU 8GB nội bộ.",
            "2. **Trung thực tốc độ & giải pháp bất đồng bộ:** Khi chạy PyTorch (`transformers`) mặc định chưa tối ưu trên RTX 3060 8GB, một ca đầy đủ mất khoảng **~3,5 phút/ca** (không phóng đại thành 30–45 giây). MediTrace giải quyết trực tiếp trên luồng khám bằng **hàng đợi nền `202 Accepted`** trong SQLite (`web/may-chu/hang-doi.ts`): bác sĩ chuyển sang bệnh nhân kế tiếp ngay với **0 giây đứng chờ giao diện**, bản nháp được xử lý ngầm; lộ trình tiếp theo là chuyển sang `vLLM / llama.cpp + XGrammar` để hướng tới **15–25 giây/ca**.",
            "3. **Hiệu quả QLoRA chuyên biệt:** Trên 30 ca phát triển độc lập (304 mệnh đề), adapter Qwen3-4B giảm tỷ lệ bỏ sót từ **43,1%** (trước huấn luyện) xuống **11,5%** (khoảng tin cậy 95%: 8,4%–15,6%) với **0 ca lỗi cấu trúc JSON**."
        ],
        mau_vien=HEX_SAFE, badge_text="Dễ"
    )

    # Cau 9
    them_hop_cau_hoi(
        doc, "q9",
        "Câu 9: Tại sao B1 phải chia câu nói ra thành từng mệnh đề (`PhatBieu`), và tại sao B2–B5 dùng thuật toán luật thay vì AI End-to-End?",
        [
            "• **Tại sao B1 phải tách câu nói thành từng mệnh đề nguyên tử (`PhatBieu`):**",
            "  1. Trong hội thoại tự nhiên, một lượt nói thường **trộn nhiều chủ thể, nhiều thời điểm và lời tự đính chính** (vd: 'Hôm qua tôi tưởng đau dạ dày, sáng nay siêu âm ra sỏi mật; còn mẹ tôi dị ứng penicillin').",
            "  2. Nếu gộp nguyên đoạn văn dài, không thể gán rạch ròi `chu_the_id`, `phu_dinh`, `tinh_huong` hay `moc_thoi_gian` cho từng sự kiện lâm sàng.",
            "  3. Tách thành từng `PhatBieu` cho phép B3 đánh dấu đúng ý 'đau dạ dày' thành `DA_THAY_THE`, B4 soi nguyên văn từng câu trích bằng K1–K7, và B5 chỉ đẩy riêng mệnh đề nghi ngờ sang 'Cần xác nhận' mà không bỏ phí phần thông tin sạch.",
            "• **Tại sao kiến trúc Lai Neuro-Symbolic (AI ở B1 + Rule ở B2–B5):** AI giỏi hiểu ngôn ngữ tự do nhưng dễ bịa và yếu logic nhất quán; còn B2–B5 viết bằng Python xác định nên **minh bạch 100%**, dễ truy lỗi đúng mô-đun và kiểm thử được bằng **1.942 unit/integration tests** mà không phải huấn luyện lại LLM."
        ],
        mau_vien=HEX_NAVY, badge_text="Trung bình"
    )

    # Cau 10
    them_hop_cau_hoi(
        doc, "q10",
        "Câu 10: Cơ chế Khóa bằng chứng K1–K7 ở Tầng 4 hoạt động cụ thể như thế nào để chặn Hallucination?",
        [
            "Mỗi `PhatBieu` từ B1 phải có `bang_chung [T_i]` và `trich_dan` nguyên văn. Cổng `src/duong_ong/b4_kiem_can_cu.py` kiểm tra 7 chốt:",
            "• **K1 (Nguồn gốc nguyên văn):** Dò trực tiếp xâu `trich_dan` vào lượt thoại `[T_i]`. Không có -> chặn ngay (`trich_khong_co`).",
            "• **K2 (Khớp nội dung):** Kiểm tra độ phủ từ khóa lâm sàng cốt lõi giữa `noi_dung` và `trich_dan`.",
            "• **K3 (Khớp chủ thể):** Đối chiếu từ chỉ người trong lượt thoại với `chu_the_id` được gán.",
            "• **K4 (Khớp mức khẳng định & điều kiện):** Chặn câu nghi ngờ hoặc câu điều kiện/phòng ngừa ('Nếu... thì...') bị biến thành sự thật (`dieu_kien`).",
            "• **K5 (Khớp mốc thời gian):** Mốc thời gian gắn cho sự kiện phải có căn cứ trong lượt thoại.",
            "• **K6 (Khớp liều lượng & thuốc):** Kiểm tra số lượng/đơn vị liều (`mg, g, ml, mcg, UI, viên...`) trên phát biểu thuộc họ liều (`s.ho == 'lieu'`).",
            "• **K7 (Kiểm tra đính chính — Superseded):** Các phát biểu đã bị câu sau phủ định hoặc xét nghiệm loại trừ (FSM ở B3 đánh dấu `DA_THAY_THE`) bị loại khỏi thân bệnh án."
        ],
        mau_vien=HEX_NAVY, badge_text="Trung bình"
    )

    # Cau 11
    them_hop_cau_hoi(
        doc, "q11",
        "Câu 11: Tại sao khẳng định điểm ROUGE là vô dụng trong đánh giá bệnh án? Dự án dùng thước đo nào thay thế?",
        [
            "• **Thực nghiệm chứng minh ROUGE không đo được an toàn lâm sàng:** Trên phép thử 400 ca bệnh, khi hoán đổi vị trí chữ **'bệnh nhân'** và **'người nhà'** (lỗi y khoa nghiêm trọng): **Điểm ROUGE-1 vẫn đạt 1.0000** vì tập hợp từ không đổi.",
            "• **Thước đo thay thế của dự án (`src/do_luong/cham_he_thong.py`):**",
            "  - **Entity Slot Error Rate (SER)** và **Attribution F1:** Chấm chính xác trên từng bộ giá trị `(Chủ thể, Bệnh/Thuốc, Trạng thái, Thời gian)`.",
            "  - **Tỷ lệ sót thông tin bị thay thế (Superseded Retention):** Cổng K7 và máy trạng thái B3 kéo tỷ lệ sót tin cũ đã đính chính giảm từ **11,48% xuống 0,80%** (giảm hơn **14 lần**)."
        ],
        mau_vien=HEX_PURPLE, badge_text="Khó"
    )

    # Cau 12
    them_hop_cau_hoi(
        doc, "q12",
        "Câu 12: Dữ liệu huấn luyện có phần mô phỏng (Synthetic Data). Làm sao chứng minh mô hình không 'học vẹt' và có tính tổng quát?",
        [
            "Dự án kiểm soát rò rỉ dữ liệu qua 4 lớp độc lập:",
            "1. **Chia tách không trùng khuôn (`chia_tap_theo_khuon.py`):** **657 khuôn ca bệnh** (21 hệ cơ quan) chia độc lập thành **515 Train / 72 Dev / 70 Test**. Độ tương đồng Jaccard từ khóa triệu chứng trung bình giữa Train và Test chỉ **5,87%**.",
            "2. **Đo đa dạng từ vựng (`src/do_luong/do_lap_cau.py`):** Bộ 5.000 hội thoại mô phỏng v2 đạt **45.835 câu duy nhất** (+127% so với v1), lặp câu giảm từ 76,92% xuống **47,37%** (câu >= 8 từ: **42,19%**), MTLD đạt **145,4**, Distinct-2 đạt **0,0468**, và **52.634/52.634 (100%)** trích dẫn đều là chuỗi con nguyên văn.",
            "3. **Tập thách thức đối lập (Adversarial Contrastive Pairs):** Trên các cặp ca bệnh đổi duy nhất một ranh giới, ở bộ đổi chủ thể 80 ca, các bước kiểm tra phía sau tăng F1 từ 66,1% lên **70,8%**, giảm SER từ 45,4% xuống **36,9%** và ghi nhầm người từ 22,0% xuống **17,9%**. Cần nói rõ: cách để mô hình viết thẳng bản nháp ghi đúng người **cao hơn** đường ống (0,939 so với 0,748).",
            "4. **Ngoài khuôn & dữ liệu công khai:** Bổ sung **10 kịch bản bệnh hiếm ngoài khuôn** (`kiem_nghiem_ngoai_khuon.py`) và đối chiếu **5 bộ dữ liệu tiếng Việt công khai bên ngoài** (xem Câu 18)."
        ],
        mau_vien=HEX_PURPLE, badge_text="Khó"
    )

    # Cau 13
    them_hop_cau_hoi(
        doc, "q13",
        "Câu 13: Hệ thống Guardrails 5 chốt chặn giải quyết hiện tượng Cascading Errors (Lỗi dây chuyền) như thế nào?",
        [
            "• **Cơ chế Cascading Error:** Nếu ASR nghe sai tên thuốc hoặc mất dấu tiếng Việt, lỗi ở tầng đầu có thể bị AI chép lại vào `trich_dan` ở B1 và đi qua phép khớp xâu B4 nếu thiếu kiểm soát từng tầng.",
            "• **5 chốt điều phối tại `src/he_thong/dieu_phoi_cac_chot_an_toan.py`:**",
            "  - **Chốt 1 (ASR & B0):** Gắn trie gợi ý 65+ G2P thuốc có khóa ngữ cảnh, phát hiện bất thường ASR/không dấu và chuẩn hóa phương ngữ có guard bảo vệ cụm từ y khoa.",
            "  - **Chốt 2 (Speaker Guardrail - B2):** Kiểm tra nhất quán vai `nguoi_noi` với `chu_the_id` và bù chủ ngữ tỉnh lược.",
            "  - **Chốt 3 (Dialogue Act & FSM - B3):** Tách câu nghi vấn/điều kiện và cập nhật trạng thái đính chính `DA_THAY_THE`.",
            "  - **Chốt 4 (Evidence Integrity K1–K7 - B4):** Soi nguyên văn trích dẫn, mức khẳng định, thời gian và hàm lượng/đơn vị liều.",
            "  - **Chốt 5 (Clinical Safety & WORM):** Soi 158 hoạt chất, tương tác DDI, liều trần, quy tắc BHYT/TT 26/2025, đẩy nhóm nguy cấp sang 'Cần xác nhận', khóa ký duyệt và ghi WORM SHA-256."
        ],
        mau_vien=HEX_PURPLE, badge_text="Khó"
    )

    doc.add_page_break()

    # =========================================================================
    # PHẦN 3: CÂU HỎI "BẮT BẺ CHÍ MẠNG" (STRESS-TEST) & MỞ RỘNG
    # =========================================================================
    them_tieu_de_phan(doc, "PHẦN 3: BỘ CÂU HỎI 'BẮT BẺ CHÍ MẠNG' (STRESS-TEST) & KIỂM CHỨNG ĐỘC LẬP")
    them_doan_van(doc, "Các câu hỏi hóc búa nhất về an toàn thuốc, tạp âm phòng khám, dữ liệu công khai và triển khai tại bệnh viện Việt Nam.",
                  nghieng=True, co_chu=9.2, mau=COLOR_MUTED)

    # Cau 14
    them_hop_cau_hoi(
        doc, "q14",
        "❓ Câu 14: 'Lúc ghi âm tên thuốc bệnh nhân đọc sai hoặc ASR nghe nhầm (a móc, ô mê). Phần mềm có tự sửa thẳng thành tên thuốc vào đơn không?'",
        [
            "🎯 **Phản biện tự tin:**",
            "1. **TUYỆT ĐỐI KHÔNG TỰ Ý SỬA NGẦM VÀO ĐƠN (Zero Silent Normalization):** Sai lệch giữa hai hoạt chất gần âm (vd: Amoxicillin đơn chất vs. Augmentin phối hợp Clavulanate) có thể gây dị ứng hoặc sai điều trị. Do đó `contextual_trie_600.py` chỉ trả về **gợi ý** khi xuất hiện trong ngữ cảnh thuốc (`uống/viên/mg/đơn`).",
            "2. **CÁCH LY SANG 'CẦN BÁC SĨ XÁC NHẬN':** Mọi trường hợp gợi ý từ âm vị dân gian, nghi ngờ nhầm họ thuốc hoặc thiếu liều (Chính sách D) đều gắn cờ cảnh báo để bác sĩ kiểm tra.",
            "3. **ĐỐI SOÁT CLICK-TO-VERIFY:** Bác sĩ bấm vào thẻ cảnh báo để `useTurnAudioPlayer.ts` phát lại đúng đoạn âm thanh gốc tại lượt thoại đó, tự tay bấm Xác nhận hoặc Sửa lại.",
            "4. **KHÓA KÝ DUYỆT & WORM:** Chỉ khi hết mục treo, đơn mới qua được `sign-off.ts` để kiểm DDI/TT 26/2025 và ghi sổ WORM nối chuỗi SHA-256 kèm `.anchor.json`."
        ],
        mau_vien=HEX_DANGER, mau_nen="FFF1F2", badge_text="Stress-Test"
    )

    # Cau 15
    them_hop_cau_hoi(
        doc, "q15",
        "❓ Câu 15: 'Nếu micrô thu nhiều tạp âm, bệnh nhân nói lí nhí, ASR nghe sai be bét thì phần mềm có tạo bệnh án rác không?'",
        [
            "🎯 **Phản biện tự tin:**",
            "Khác với chatbot tổng quát dễ 'sáng tác' phần bị mất cho mượt câu chữ, khi ASR vỡ chữ hoặc không rõ ngữ cảnh, bộ phát hiện bất thường ASR/không dấu trong `src/canh_bao/` kết hợp K1–K2 tại `b4_kiem_can_cu.py` sẽ chặn mệnh đề thiếu căn cứ và chuyển sang trạng thái chờ bác sĩ kiểm tra — không tự bịa thông số lâm sàng vào thân bệnh án sạch."
        ],
        mau_vien=HEX_DANGER, mau_nen="FFF1F2", badge_text="Stress-Test"
    )

    # Cau 16
    them_hop_cau_hoi(
        doc, "q16",
        "❓ Câu 16: 'Một ngày khám đông ca, nhỡ bác sĩ đang dở tay hoặc tắt máy đột ngột thì dữ liệu có mất không?'",
        [
            "🎯 **Phản biện tự tin:**",
            "Backend BFF (`web/may-chu/csdl.ts`) lưu phiên khám liên tục trên cơ sở dữ liệu **SQLite WAL cục bộ** kèm hàng đợi nền `hang-doi.ts`. Bản ghi âm, bản gỡ băng, danh sách mệnh đề và trạng thái từng mục xác nhận được lưu bền vững; khi mở lại phần mềm, bác sĩ tiếp tục đúng phiên ở trạng thái `Chờ duyệt` mà không mất dữ liệu."
        ],
        mau_vien=HEX_DANGER, mau_nen="FFF1F2", badge_text="Stress-Test"
    )

    # Cau 17
    them_hop_cau_hoi(
        doc, "q17",
        "❓ Câu 17: 'Dự án đã kiểm thử tự động trên quy mô bao nhiêu, kết quả thực tế thế nào?'",
        [
            "🎯 **Phản biện tự tin:**",
            "Toàn hệ thống được bảo vệ bởi bộ kiểm thử hồi quy hai tầng chạy sau các đợt tinh chỉnh cuối cùng:",
            "1. **Kiểm thử phần mềm tự động:** **1.942 bài test Python qua, 27 bỏ qua** (lần chạy 26/11/2026 ghi ở `README.md`; các bài skip phụ thuộc phần cứng/sidecar GPU ngoài môi trường CPU) và **96/96 bài kiểm thử TypeScript/BFF passed** (`web/`).",
            "2. **Kiểm thử dữ liệu & an toàn lâm sàng:** **657 khuôn ca bệnh** (21 hệ cơ quan, chia 515/72/70), **5.000 hội thoại mô phỏng v2** (100% trích dẫn trong dữ liệu huấn luyện tự sinh là chuỗi con nguyên văn), **4 bộ thử thách phát triển** (300 ca: Chính sách D giảm `lot_nguy_hiem` từ 45,9% xuống **11,8%**, chặn **88,2%** lỗi nguy hiểm, chặn thừa **10,0%**; số lạc quan), **240 ca giữ kín `thach_thuc_v2`** (nhạy **0,871**, đổi chủ thể **0,946**, bắt xoá dị ứng **97,2%**), và **10 ca bệnh hiếm ngoài khuôn**."
        ],
        mau_vien=HEX_DANGER, mau_nen="FFF1F2", badge_text="Stress-Test"
    )

    # Cau 18
    them_hop_cau_hoi(
        doc, "q18",
        "❓ Câu 18: 'Đã đo trên bộ dữ liệu tiếng Việt công khai độc lập nào chưa? Sau khi đo có bổ sung sửa phần còn sai không?'",
        [
            "🎯 **Phản biện tự tin (Chu trình Đo -> Vá luật -> Đo lại trên 5 nguồn ngoài tại `tools/do_da_nguon_doc_lap.py` & `tools/do_an_danh_phoner.py`):**",
            "1. **`ViDia2Std/test.csv`** (1.603 câu phương ngữ 63 tỉnh): Sau khi siết khóa bảo vệ từ y khoa ('bờ mi, tứ chi, mô mềm, vô kinh, cấy ghép'), đạt **27,8%** đúng chuẩn xác (1.185/4.264), tổng độ phủ **37,0%**, đổi thừa chỉ **43**, kéo WER giảm từ **30,1% xuống 22,0%**; đồng thời bổ sung đại từ Nam Bộ 'tui' từ tập `dev` vào `b2_gom_nguoi_thuc_the.py`.",
            "2. **`ViHealthQA`** (2.013 cặp hỏi đáp): Khớp Dược thư **158 hoạt chất** ở **14 câu hỏi** và **42 câu trả lời** trên 2.013 mẫu (cùng 459 mẫu trích số liệu lâm sàng).",
            "3. **`ViMedAQA`** (500 mẫu hỏi đáp y khoa): Bắt khớp **87** lượt nhắc hoạt chất chuẩn; 300 câu đầu dùng làm chuẩn chống che nhầm PII với tỷ lệ che nhầm chỉ **0,7%–1,3%**.",
            "4. **`ViMQ`** (1.000 câu hỏi ý định y khoa): Khớp 10 mẫu thuốc (9/334 thực thể `MED` có nhãn) do bệnh nhân ít gọi tên hoạt chất Tây y; đồng thời dùng làm nguồn tiền gán nhãn qua `gan_nhan_truoc.py`.",
            "5. **`PhoNER_COVID19` — Trước khi vá -> Sau khi vá:**",
            "   - **Trước khi vá (Mốc 0):** Bộ che Python chỉ đạt **10/847 (1,2%)** trên 1.000 câu đầu; đo đủ 3.000 câu test (`an-danh-phoner.md`) chỉ đạt **0,8% (19/2.323)** ở Python và **7,5% (174/2.323)** ở TypeScript.",
            "   - **Đã vá vào dự án:** Thêm luật `MA_CA_BENH`, `TEN_VIET_TAT`, họ tên viết thường và xưng hô + tên viết hoa (né 'thứ 2', '65 tuổi', 'Vitamin B.', tên thuốc) vào `khu_dinh_danh.py` và `an-danh-ngoai.ts`.",
            "   - **Sau khi vá:** Trên 1.000 câu đầu (`da-nguon-doc-lap.json`) tăng vọt lên **91,5% (775/847)**; trên toàn bộ 3.000 câu test (`an-danh-phoner.md`) đạt **93,8% (2.178/2.323)** ở Python và **94,0% (2.183/2.323)** ở TypeScript (tập `dev` đạt **97,3%–97,5%**). Phần ~6% tên 1 tiếng đứng trơ ('Nhung, Oanh, Kim') giữ nguyên không ép regex để tránh che nhầm thuật ngữ y khoa.",
            "*(Ngoài ra kho `data/ngoai/` còn có `VNMed_Speech` — 2.887 đoạn âm thanh CC BY 4.0 — và `VietMed-NER` phục vụ bóc mẫu chạy thử ASR; chưa đưa vào train Qwen3-4B hiện tại.)*"
        ],
        mau_vien=HEX_DANGER, mau_nen="FFF1F2", badge_text="Stress-Test"
    )

    # Cau 19
    them_hop_cau_hoi(
        doc, "q19",
        "❓ Câu 19: 'Ngoài bóc tách bệnh án SOAP, dự án có gì phục vụ vận hành thực tế tại bệnh viện Việt Nam (BHYT, HIS cũ, bệnh nhân)?'",
        [
            "🎯 **Phản biện tự tin (Bộ tiện ích `src/cong_cu_lam_sang/` & `web/`):**",
            "• **Tiền kiểm BHYT & TT 26/2025 (`tien_kiem_bhyt_va_khoi_phuc_bo_sot.py` + `BhytPrecheckModal.tsx`):** Rà **13 quy tắc cận lâm sàng (CLS)** dễ bị xuất toán BHYT và bắt buộc kiểm tra **cân nặng trẻ em** khi kê đơn nhi khoa.",
            "• **Sao chép thông minh sang HIS (`HisSmartCopyPopover.tsx`):** Copy theo từng khối (Lý do khám, Bệnh sử, Tiền sử/Dị ứng, Chẩn đoán, Điều trị) sang phần mềm HIS sẵn có của bệnh viện mà không phải chờ tích hợp sâu ngày đầu.",
            "• **Chuẩn liên thông & ngoại viện:** Xuất **FHIR R4** (`xuat_fhir_r4.py`), nạp **LIS/HL7** (`nap_ket_qua_lis_hl7.py`), **9 thang điểm nguy cơ** (`thang_diem_nguy_co.py`), đi buồng nội trú, **Cổng bệnh nhân & QR tóm tắt đơn/dặn dò** (`ho_so_benh_nhan_qr.py`, `PatientPortalView.tsx`) và **Trung tâm điều hành bệnh viện** (`HospitalCommandCenterView.tsx`)."
        ],
        mau_vien=HEX_NAVY, mau_nen="F8FAFC", badge_text="Trung bình"
    )

    # THONG DIEP CHOT
    them_hop_cau_hoi(
        doc, "conclusion",
        "🏆 THÔNG ĐIỆP CHỐT HẠ TRƯỚC BAN GIÁM KHẢO:",
        [
            "**'MediTrace Sentinel không trình diễn một chatbot viết văn y khoa trơn tru.**",
            "Đây là kiến trúc **Neuro-Symbolic đặt an toàn người bệnh lên trước**: dùng AI đúng một chỗ để tách từng mệnh đề có căn cứ nguyên văn, kiểm soát rủi ro ảo giác bằng **7 cổng khóa K1–K7** và **5 chốt an toàn xác định**, minh bạch cả kết quả đo được lẫn giới hạn còn lại để người thầy thuốc luôn giữ quyền quyết định cuối cùng.'**"
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
    print(f"Da xuat xong file Word tai:\n-> {FILE_OUT_GOC}\n-> {FILE_OUT_DOCS}")


if __name__ == "__main__":
    tao_word_qna()
