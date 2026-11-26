# -*- coding: utf-8 -*-
"""Xuất ấn phẩm Word (.docx) & Markdown (.md) toàn diện cho MediTrace Sentinel (AI 2026):
1. Giải thích kiến trúc tổng thể & luồng chạy từng bước dễ hiểu.
2. Bản đồ mã nguồn chi tiết ("Chức năng này để code ở đâu, hàm nào xử lý?").
3. Phân tích tính khả thi thực tế (Phần cứng, Quy trình khám 50–80 ca/ngày, Pháp lý, Chi phí, Lộ trình).
4. Bộ 22 câu hỏi phản biện Ban Giám khảo (từ cơ bản đến xoáy sâu/stress-test) kèm câu trả lời chuẩn xác, trung thực.

Chạy bằng môi trường có python-docx:
    python tools/tao_cam_nang_giai_thich_va_qna_word.py
"""

from __future__ import annotations

from pathlib import Path
import re
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

GOC = Path(__file__).resolve().parent.parent
TEN_TEP_DOCX = "Cam_Nang_Kien_Truc_Ma_Nguon_Tinh_Kha_Thi_Va_Phan_Bien_BGK_MediTrace_2026.docx"
FILE_DOCX_GOC = GOC / TEN_TEP_DOCX
FILE_DOCX_DOCS = GOC / "docs" / "tai-lieu" / TEN_TEP_DOCX
FILE_DOCX_DESKTOP = Path("C:/Users/admin/Desktop") / TEN_TEP_DOCX
FILE_MD_DOCS = GOC / "docs" / "tai-lieu" / "CAM_NANG_KIEN_TRUC_MA_NGUON_VA_PHAN_BIEN_BGK_2026.md"
THUMUC_HINH = GOC / "docs" / "tai-lieu" / "hinh"

# Bảng màu biên tập chuyên nghiệp (Medical Executive Navy & Teal)
HEX_NAVY = "0F2942"
HEX_BLUE = "0284C7"
HEX_TEAL = "0D6E6E"
HEX_DARK = "0F172A"
HEX_MUTED = "475569"
HEX_BORDER = "CBD5E1"
HEX_BG_SOFT = "F8FAFC"
HEX_BG_BLUE = "F0F9FF"
HEX_BG_TEAL = "F0FDFA"
HEX_BG_AMBER = "FFFBEB"
HEX_BG_ROSE = "FFF1F2"
HEX_AMBER = "B45309"
HEX_DANGER = "BE123C"
HEX_SAFE = "047857"
HEX_PURPLE = "6D28D9"

C_NAVY = RGBColor(0x0F, 0x29, 0x42)
C_BLUE = RGBColor(0x02, 0x84, 0xC7)
C_TEAL = RGBColor(0x0D, 0x6E, 0x6E)
C_DARK = RGBColor(0x0F, 0x17, 0x2A)
C_MUTED = RGBColor(0x47, 0x55, 0x69)
C_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
C_AMBER = RGBColor(0xB4, 0x53, 0x09)
C_DANGER = RGBColor(0xBE, 0x12, 0x3C)
C_SAFE = RGBColor(0x04, 0x78, 0x57)
C_PURPLE = RGBColor(0x6D, 0x28, 0xD9)


# ==============================================================================
# TIỆN ÍCH ĐỊNH DẠNG WORD XML
# ==============================================================================

def dat_vien_o(cell, top=HEX_BORDER, bottom=HEX_BORDER, left=HEX_BORDER, right=HEX_BORDER, sz="4"):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn("w:tcBorders")):
        tcPr.remove(old)
    tcBorders = OxmlElement("w:tcBorders")
    for canh, mau in [("w:top", top), ("w:bottom", bottom), ("w:left", left), ("w:right", right)]:
        node = OxmlElement(canh)
        if mau is None:
            node.set(qn("w:val"), "none")
        else:
            node.set(qn("w:val"), "single")
            node.set(qn("w:sz"), str(sz))
            node.set(qn("w:space"), "0")
            node.set(qn("w:color"), mau)
        tcBorders.append(node)
    tcPr.append(tcBorders)


def dat_nen_o(cell, hex_color: str):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn("w:shd")):
        tcPr.remove(old)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def dat_le_o(cell, top=90, bottom=90, left=130, right=130):
    tcPr = cell._tc.get_or_add_tcPr()
    for old in tcPr.findall(qn("w:tcMar")):
        tcPr.remove(old)
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("w:top", top), ("w:bottom", bottom), ("w:left", left), ("w:right", right)]:
        node = OxmlElement(m)
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def lap_lai_hang_dau(row):
    trPr = row._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader")
    trPr.append(tblHeader)


def chong_cat_hang(row):
    trPr = row._tr.get_or_add_trPr()
    cantSplit = OxmlElement("w:cantSplit")
    trPr.append(cantSplit)


def them_so_trang_xml(run):
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "separate")
    fldChar3 = OxmlElement("w:fldChar")
    fldChar3.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    run._r.append(fldChar3)


_RE_TOKEN_DINH_DANG = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`|\*[^*\n]+\*)")


def ghi_chuoi_co_dinh_dang(p, text: str, co_chu=10.0, mau=C_DARK, mac_dinh_dam=False):
    """Hỗ trợ cú pháp **in đậm**, *in nghiêng* và `code/đường dẫn` (Consolas), kể cả lồng `code` trong **in đậm**."""
    vi_tri = 0
    for m in _RE_TOKEN_DINH_DANG.finditer(text):
        if m.start() > vi_tri:
            thuong = text[vi_tri:m.start()]
            r = p.add_run(thuong)
            r.bold = mac_dinh_dam
            r.font.name = "Segoe UI"
            r.font.size = Pt(co_chu)
            r.font.color.rgb = mau
        tok = m.group(0)
        if tok.startswith("**") and tok.endswith("**"):
            ruot = tok[2:-2]
            # Cho phép `code` lồng bên trong **...**
            for phan_c_idx, phan_c in enumerate(ruot.split("`")):
                if not phan_c:
                    continue
                r = p.add_run(phan_c)
                r.bold = True
                if phan_c_idx % 2 == 1:
                    r.font.name = "Consolas"
                    r.font.size = Pt(max(8.5, co_chu - 0.5))
                    r.font.color.rgb = C_NAVY
                else:
                    r.font.name = "Segoe UI"
                    r.font.size = Pt(co_chu)
                    r.font.color.rgb = C_NAVY if mau == C_DARK else mau
        elif tok.startswith("`") and tok.endswith("`"):
            r = p.add_run(tok[1:-1])
            r.bold = True
            r.font.name = "Consolas"
            r.font.size = Pt(max(8.5, co_chu - 0.5))
            r.font.color.rgb = C_TEAL if not mac_dinh_dam else C_NAVY
        elif tok.startswith("*") and tok.endswith("*"):
            r = p.add_run(tok[1:-1])
            r.bold = mac_dinh_dam
            r.italic = True
            r.font.name = "Segoe UI"
            r.font.size = Pt(co_chu)
            r.font.color.rgb = mau
        vi_tri = m.end()
    if vi_tri < len(text):
        r = p.add_run(text[vi_tri:])
        r.bold = mac_dinh_dam
        r.font.name = "Segoe UI"
        r.font.size = Pt(co_chu)
        r.font.color.rgb = mau


def them_doan(doc, text="", co_chu=10.0, mau=C_DARK, can_le=WD_ALIGN_PARAGRAPH.LEFT,
              cach_tren=0, cach_duoi=4, gian_dong=1.18):
    p = doc.add_paragraph()
    p.alignment = can_le
    p.paragraph_format.space_before = Pt(cach_tren)
    p.paragraph_format.space_after = Pt(cach_duoi)
    p.paragraph_format.line_spacing = gian_dong
    if text:
        ghi_chuoi_co_dinh_dang(p, text, co_chu=co_chu, mau=mau)
    return p


def them_gach_dau_dong(doc, text: str, co_chu=9.8):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.22)
    p.paragraph_format.first_line_indent = Inches(-0.14)
    p.paragraph_format.space_before = Pt(1.5)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.16
    r0 = p.add_run("•  ")
    r0.bold = True
    r0.font.name = "Segoe UI"
    r0.font.size = Pt(co_chu)
    r0.font.color.rgb = C_BLUE
    ghi_chuoi_co_dinh_dang(p, text, co_chu=co_chu, mau=C_DARK)
    return p


def them_phan_lon(doc, so_phan: str, tieu_de: str, mo_ta_ngan: str = ""):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    chong_cat_hang(tbl.rows[0])
    c = tbl.cell(0, 0)
    c.width = Inches(6.75)
    dat_nen_o(c, HEX_NAVY)
    dat_vien_o(c, top=HEX_NAVY, bottom="0284C7", left="38BDF8", right=HEX_NAVY, sz="14")
    dat_le_o(c, top=110, bottom=110, left=160, right=150)
    p = c.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2 if mo_ta_ngan else 0)
    p.paragraph_format.keep_with_next = True
    r1 = p.add_run(f"{so_phan.upper()}  ·  ")
    r1.bold = True
    r1.font.name = "Segoe UI"
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = RGBColor(0x7D, 0xD3, 0xFC)
    r2 = p.add_run(tieu_de.upper())
    r2.bold = True
    r2.font.name = "Segoe UI"
    r2.font.size = Pt(13)
    r2.font.color.rgb = C_WHITE
    if mo_ta_ngan:
        p2 = c.add_paragraph()
        p2.paragraph_format.space_before = Pt(2)
        p2.paragraph_format.space_after = Pt(0)
        rm = p2.add_run(mo_ta_ngan)
        rm.italic = True
        rm.font.name = "Segoe UI"
        rm.font.size = Pt(9.2)
        rm.font.color.rgb = RGBColor(0xE0, 0xF2, 0xFE)
    them_doan(doc, "", cach_tren=0, cach_duoi=4)


def them_muc_con(doc, tieu_de: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(11)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r_bar = p.add_run("▎ ")
    r_bar.bold = True
    r_bar.font.name = "Segoe UI"
    r_bar.font.size = Pt(11.5)
    r_bar.font.color.rgb = C_BLUE
    ghi_chuoi_co_dinh_dang(p, tieu_de, co_chu=11.5, mau=C_NAVY, mac_dinh_dam=True)
    return p


def them_hop_diem_nhan(doc, tieu_de: str, cac_dong: list[str], mau_vien=HEX_BLUE, mau_nen=HEX_BG_BLUE):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    chong_cat_hang(tbl.rows[0])
    c = tbl.cell(0, 0)
    c.width = Inches(6.75)
    dat_nen_o(c, mau_nen)
    dat_vien_o(c, top=HEX_BORDER, bottom=HEX_BORDER, left=mau_vien, right=HEX_BORDER, sz="16")
    dat_le_o(c, top=95, bottom=95, left=150, right=140)
    p0 = c.paragraphs[0]
    p0.paragraph_format.space_before = Pt(0)
    p0.paragraph_format.space_after = Pt(3)
    rt = p0.add_run(tieu_de)
    rt.bold = True
    rt.font.name = "Segoe UI"
    rt.font.size = Pt(10.2)
    rt.font.color.rgb = C_NAVY if mau_vien != HEX_DANGER else C_DANGER
    for d in cac_dong:
        pd = c.add_paragraph()
        pd.paragraph_format.space_before = Pt(1.5)
        pd.paragraph_format.space_after = Pt(2)
        pd.paragraph_format.line_spacing = 1.15
        ghi_chuoi_co_dinh_dang(pd, d, co_chu=9.5, mau=C_DARK)
    them_doan(doc, "", cach_tren=0, cach_duoi=3)


def them_bang(doc, tieu_de_cot: list[str], cac_hang: list[list[str]], do_rong: list[float], mau_header=HEX_NAVY):
    tbl = doc.add_table(rows=len(cac_hang) + 1, cols=len(tieu_de_cot))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False

    # Hàng tiêu đề
    hang_dau = tbl.rows[0]
    lap_lai_hang_dau(hang_dau)
    chong_cat_hang(hang_dau)
    for j, col_name in enumerate(tieu_de_cot):
        cell = hang_dau.cells[j]
        cell.width = Inches(do_rong[j])
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        dat_nen_o(cell, mau_header)
        dat_vien_o(cell, top=mau_header, bottom=mau_header, left="334155", right="334155", sz="4")
        dat_le_o(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(col_name)
        r.bold = True
        r.font.name = "Segoe UI"
        r.font.size = Pt(9.2)
        r.font.color.rgb = C_WHITE

    # Các hàng dữ liệu
    for i, hang in enumerate(cac_hang):
        row = tbl.rows[i + 1]
        chong_cat_hang(row)
        nen = "FFFFFF" if i % 2 == 0 else HEX_BG_SOFT
        for j, val in enumerate(hang):
            cell = row.cells[j]
            cell.width = Inches(do_rong[j])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            dat_nen_o(cell, nen)
            dat_vien_o(cell, top="E2E8F0", bottom="E2E8F0", left="E2E8F0", right="E2E8F0", sz="4")
            dat_le_o(cell, top=70, bottom=70, left=95, right=95)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.14
            ghi_chuoi_co_dinh_dang(p, val, co_chu=9.0, mau=C_DARK)

    them_doan(doc, "", cach_tren=0, cach_duoi=4)
    return tbl


def them_the_qna(doc, so_cau: int, muc_do: str, nhom: str, cau_hoi: str,
                 tra_loi_ngan: str, co_che_va_code: str, so_lieu_minh_chung: str):
    mau_vien = HEX_SAFE if muc_do == "CƠ BẢN" else HEX_BLUE if muc_do == "TRỌNG TÂM" else HEX_PURPLE if muc_do == "CHUYÊN SÂU" else HEX_DANGER
    mau_nen = HEX_BG_TEAL if muc_do == "CƠ BẢN" else HEX_BG_BLUE if muc_do == "TRỌNG TÂM" else "F5F3FF" if muc_do == "CHUYÊN SÂU" else HEX_BG_ROSE
    mau_chu_badge = C_SAFE if muc_do == "CƠ BẢN" else C_BLUE if muc_do == "TRỌNG TÂM" else C_PURPLE if muc_do == "CHUYÊN SÂU" else C_DANGER

    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    chong_cat_hang(tbl.rows[0])
    c = tbl.cell(0, 0)
    c.width = Inches(6.75)
    dat_nen_o(c, "FFFFFF")
    dat_vien_o(c, top="CBD5E1", bottom="CBD5E1", left=mau_vien, right="CBD5E1", sz="18")
    dat_le_o(c, top=95, bottom=95, left=145, right=135)

    # Dòng tiêu đề câu hỏi
    p_q = c.paragraphs[0]
    p_q.paragraph_format.space_before = Pt(0)
    p_q.paragraph_format.space_after = Pt(4)
    p_q.paragraph_format.line_spacing = 1.16
    rb = p_q.add_run(f"[CÂU {so_cau:02d} · {muc_do} · {nhom}] ")
    rb.bold = True
    rb.font.name = "Segoe UI"
    rb.font.size = Pt(8.8)
    rb.font.color.rgb = mau_chu_badge

    ghi_chuoi_co_dinh_dang(p_q, cau_hoi, co_chu=10.5, mau=C_NAVY, mac_dinh_dam=True)

    for nhan, noi_dung in [
        ("1. Trả lời trực diện:", tra_loi_ngan),
        ("2. Cơ chế & vị trí code:", co_che_va_code),
        ("3. Số liệu & minh chứng thật:", so_lieu_minh_chung),
    ]:
        pa = c.add_paragraph()
        pa.paragraph_format.space_before = Pt(2)
        pa.paragraph_format.space_after = Pt(2.5)
        pa.paragraph_format.line_spacing = 1.15
        rn = pa.add_run(nhan + " ")
        rn.bold = True
        rn.font.name = "Segoe UI"
        rn.font.size = Pt(9.4)
        rn.font.color.rgb = C_TEAL if "Cơ chế" in nhan else (C_AMBER if "Số liệu" in nhan else C_NAVY)
        ghi_chuoi_co_dinh_dang(pa, noi_dung, co_chu=9.4, mau=C_DARK)

    # Đệm nền nhẹ cho câu stress-test để dễ nhận biết khi ôn tập
    if muc_do == "XOÁY SÂU / BẮT BẺ":
        dat_nen_o(c, mau_nen)

    them_doan(doc, "", cach_tren=0, cach_duoi=4)


# ==============================================================================
# DỮ LIỆU NỘI DUNG CHUẨN XÁC 100% VỚI CODE ĐÃ TRIỂN KHAI (26/11/2026)
# ==============================================================================

BANG_LUONG_8_TRAM = [
    [
        "Trạm 0\nThu âm & Chép lời",
        "Âm thanh buổi khám (WebM/WAV) hoặc lời thoại gõ/nạp sẵn",
        "Chuỗi đoạn chép lời có mốc giây `start_time..end_time`, độ tự tin ASR và vai người nói (`doctor`, `patient`, `caregiver`, `nurse`, `other`)",
        "Mặc định `speaker_role='unknown'`; **chặn cứng HTTP 409** và chặn trên giao diện nếu còn lượt chưa gán vai",
        "`src/audio/pipeline.py`\n`src/dich_vu.py` (`_chep_am`)\n`web/src/services/realAudioService.ts`",
    ],
    [
        "Trạm 1\nRút mệnh đề AI",
        "Lời thoại đã gán vai theo từng lượt `1..N`",
        "Danh sách mệnh đề JSON nguyên tử `PhatBieu` (nói về ai, phủ định, độ chắc chắn, tình huống, lượt dẫn, `trich_dan`)",
        "**Chỉ bước này dùng AI** (`Qwen3-4B` + adapter QLoRA 4-bit chạy tại chỗ); cấm viết văn xuôi tự do; ép lược đồ JSON",
        "`src/bakeoff.py`\n`src/phat_bieu.py` (`tu_json`)\n`src/nhanh.py`",
    ],
    [
        "Trạm 2\nGom thực thể & Chủ thể",
        "Danh sách `PhatBieu` + văn bản lời thoại gốc",
        "Mỗi mệnh đề gắn `chu_the_id` (`0` = bệnh nhân, `1..k` = mẹ/bố/con/người đi cùng) và `ten_chu_the`",
        "Chuẩn hóa vai nhân viên y tế (`la_vai_nhan_vien`) về bệnh nhân; tách biệt người phát ngôn với người mang bệnh",
        "`src/thuc_the.py` (`lien_ket`)\n`src/phat_bieu.py` (`bang_ten_tu_thuc_the`)",
    ],
    [
        "Trạm 3\nCập nhật Đính chính (FSM)",
        "Chuỗi `PhatBieu` theo trật tự thời gian lượt nói",
        "Trạng thái từng mệnh đề: `còn hiệu lực`, `bị thay thế`, hoặc `chưa giải quyết` (mâu thuẫn)",
        "Tự sửa hoặc đồng thuận chéo -> bản cũ sang `bị thay thế` (**không xoá**); hai người nói ngược nhau -> hạ về `mâu thuẫn`",
        "`src/cap_nhat.py` (`ap_luat`)\n`src/may_trang_thai_hoi_thoai.py`",
    ],
    [
        "Trạm 4\nKhóa căn cứ K1–K6 & Cảnh báo",
        "Mệnh đề sau FSM + toàn bộ lượt thoại gốc + cơ địa bệnh nhân",
        "Kết quả khóa `KetQua`, điểm rủi ro `DanhGia`, và danh sách `CanhBao` (13 nhóm, 56 mã lỗi, 2 trục `muc_do` × `bat_dinh`)",
        "So khớp chuỗi con nguyên văn, từ nội dung, đại từ tự xưng người kể (`chu_the_nguoi_ke`), điều kiện, thời gian, tên/liều thuốc",
        "`src/khoa_bang_chung.py`\n`src/cong_rui_ro.py`\n`src/canh_bao/` (`loai.py`, `gop.py`)",
    ],
    [
        "Trạm 5\nGhép bản nháp theo khuôn",
        "Mệnh đề + danh sách bị chặn/cảnh báo `ly_do_chan`",
        "Bản nháp 9–14 mục chuẩn khám bệnh + mục riêng `CẦN XÁC NHẬN` + tối đa 3 câu hỏi làm rõ",
        "100% ghép bằng mã luật, không dùng LLM viết lại; phân biệt *'chưa ghi nhận'* với *'không có'*; không xoá ngầm thông tin nghi ngờ",
        "`src/sinh_benh_an.py`\n`src/hoi_lai.py`",
    ],
    [
        "Trạm 6\nHỗ trợ Lâm sàng & BHYT",
        "Mệnh đề hiệu lực + ngữ cảnh tuổi/giới/xét nghiệm cũ",
        "Cảnh báo tương tác thuốc DDI, liều trần, CrCl/eGFR chỉnh liều thận, 9 thang điểm, mã ICD-10 4 ký tự, XML1–XML5, HL7 FHIR R4",
        "Loại trừ bệnh của người nhà và bệnh đã phủ định khỏi ICD-10/FHIR; gắn nhãn rõ bảng tri thức thuốc `da_duyet=false`",
        "`src/dieu_phoi_ha_tang.py`\n`src/kiem_duyet_bhyt_va_bo_sot.py`\n`src/ocr_lam_sang.py`\n`src/fhir_exporter.py`",
    ],
    [
        "Trạm 7\nBác sĩ Duyệt & Ký WORM",
        "Bản nháp + dây nối căn cứ SVG + đoạn âm thanh gốc",
        "Văn bản hiệu lực (`Giữ / Sửa / Bỏ`), phiếu SBAR, ô chép HIS, tờ dặn dò TTS, bản ghi ký duyệt chuỗi băm SHA-256",
        "**Chốt cứng 2 tầng:** Chặn hoàn tất/ký duyệt khi `0` mệnh đề hoặc còn mục `Cần xác nhận` chưa xử lý; SQLite trigger cấm sửa/xoá + `.anchor.json`",
        "`web/src/components/VerificationView.tsx`\n`DuyetBenCanh.tsx`\n`compileEffectiveNote.ts`\n`web/may-chu/worm.ts`",
    ],
]


BAN_DO_MA_NGUON_PYTHON = [
    [
        "0. Dịch vụ HTTP & Ca mẫu BGK",
        "`src/dich_vu.py`\n`src/ca_mau_bgk.py`\n`src/api_contract.py`",
        "`May`, `Loi`, `AmThanh`, `ca_mau()`, `doc_ca()`, `danh_sach_ca_demo()`",
        "Cổng HTTP nội bộ `127.0.0.1:8765`. Nạp mô hình lười (lazy-load) giúp `/api/suc-khoe` phản hồi `< 1s`; khóa suy luận GPU `_khoa_suy_luan`; khử định danh trước khi gọi `--mo-hinh-xa`; tích hợp sẵn 3 ca mẫu đa người nói chạy ngay không cần GPU.",
    ],
    [
        "1. Âm thanh, PhoWhisper & Tách giọng",
        "`src/audio/pipeline.py`\n`src/audio/schemas.py`\n`src/audio/asr/disagreement.py`\n`src/trie_duoc_thu.py`",
        "`AudioPipeline`, `SpeakerRole`, `ContextualPrefixTrie600`",
        "Quản lý phiên ghi âm cục bộ, chép lời PhoWhisper, tách người nói (pyannote ở môi trường tách rời), kiểm tra bất đồng ASR trên thực thể thuốc/số/phủ định và xuất hotwords từ cây Trie dược thư 21 hệ cơ quan.",
    ],
    [
        "2. Trích xuất AI & Huấn luyện QLoRA / DPO",
        "`src/bakeoff.py`\n`src/phat_bieu.py`\n`src/train_baseline.py`\n`src/loss_theo_doan.py`\n`src/train_dpo.py`",
        "`PhatBieu`, `tu_json()`, `loss_theo_doan()`, `train_dpo`",
        "Định nghĩa cấu trúc mệnh đề nguyên tử; giải mã ép lược đồ JSON cho `Qwen3-4B`; tính hàm mất mát theo từng đoạn token giúp train ngữ cảnh dài `4.096` token chỉ tốn `6,42 GiB` VRAM; huấn luyện DPO trên 1.200 cặp lỗi khó.",
    ],
    [
        "3. Gom chủ thể & Đính chính FSM",
        "`src/thuc_the.py`\n`src/cap_nhat.py`\n`src/phan_quan_he.py`\n`src/may_trang_thai_hoi_thoai.py`",
        "`lien_ket()`, `ap_luat()`, `_co_dong_thuan_cheo()`, `BoGiaiQuyetProDrop`, `MayTrangThaiHoiThoai`",
        "Gom các cách xưng hô tiếng Việt (*con, cháu, mẹ, ông nhà*) về thực thể số nguyên; xử lý 4 quan hệ hội thoại (*bổ sung, đính chính, diễn biến, mâu thuẫn*) mà không bao giờ xoá mất dấu vết giá trị cũ.",
    ],
    [
        "4. Khóa căn cứ K1–K6, Cổng rủi ro & Lớp cảnh báo",
        "`src/khoa_bang_chung.py`\n`src/cong_rui_ro.py`\n`src/canh_bao/loai.py`\n`src/canh_bao/gop.py`\n`src/canh_bao/than_the.py`\n`src/canh_bao/thoi_diem.py`\n`src/canh_bao/toan_ca.py`",
        "`khoa_ca()`, `cham()`, `dua_sang_xac_nhan()`, `LOAI`, `muc_do()`, `gop.chay()`",
        "Đối chiếu trực tiếp từng mệnh đề với lượt dẫn; khuếch đại rủi ro theo cơ địa (thai kỳ, sơ sinh, lão khoa, suy thận/gan, đa thuốc); phân loại 56 mã lỗi thuộc 13 nhóm (gồm cả sai bên trái/phải, sai mức độ, nhầm quá khứ/hiện tại, đính chính ngược).",
    ],
    [
        "5. Sinh bệnh án, Dược lý, XN cũ, BHYT & FHIR",
        "`src/sinh_benh_an.py`\n`src/aho_corasick_duoc_thu.py`\n`src/duoc_ly_lam_sang.py`\n`src/hieu_chinh_lieu.py`\n`src/ocr_lam_sang.py`\n`src/kiem_duyet_bhyt_va_bo_sot.py`\n`src/fhir_exporter.py`\n`src/thang_diem_lam_sang.py`",
        "`sinh()`, `PurePythonAhoCorasick`, `boc_tach_phieu_cu()`, `BHYTXmlPreChecker`, `FHIRExporter`",
        "Ghép bản nháp từ bảng mệnh đề; quét thuốc Aho-Corasick `O(N+M+Z)` thuần Python (`Sintrom -> acenocoumarol`); quy đổi Creatinin `µmol/L ↔ mg/dL` tính CrCl/eGFR; gợi ý ICD-10 4 ký tự, xuất XML1–XML5 QĐ 130/4750 và HL7 FHIR R4 Bundle.",
    ],
    [
        "6. Bộ dữ liệu 657 khuôn & Đo kiểm độc lập",
        "`src/kho_khuon.py`\n`src/ngu_lieu_viet.py`\n`src/khuon_mo_rong.py`\n`src/bien_the_cau.py`\n`src/sinh_hoi_thoai_viet.py`\n`src/tach_tap_viet.py`\n`src/do_lap_cau.py`\n`src/do_bo_sot.py`\n`src/do_cay_loi.py`\n`src/kiem_nghiem_ngoai_khuon.py`",
        "`ds_khuon()`, `phan_khuon()`, `tinh_ma_tran_trung_lap_train_test()`, `chay_kiem_nghiem_ngoai_khuon()`",
        "Hợp nhất 657 khuôn ca bệnh (21 hệ cơ quan), chia tập độc lập tuyệt đối `515 Train / 72 Dev / 70 Test` (`0` khuôn giao nhau), đo lặp câu/MTLD/Distinct-2, đo tỷ lệ bỏ sót, cấy lỗi 16 cơ bản + 14 lỗi khó và kiểm nghiệm 10 kịch bản ngoài khuôn.",
    ],
]


BAN_DO_MA_NGUON_WEB = [
    [
        "BFF Khởi động, Tài khoản & An ninh CSRF",
        "`web/server.ts`\n`web/may-chu/env.ts`\n`web/may-chu/tai-khoan.ts`\n`web/may-chu/csdl.ts`",
        "`taoUngDung()`, `dangKyTaiKhoan()`, `ghiMotCaKham()`",
        "Nạp `.env` trước mọi mô-đun; băm mật khẩu `scrypt` có semaphore giới hạn đồng thời `<= 4`; đăng ký bằng mã mời 1 lần; chặn CSRF bằng danh sách nguồn HTTPS tường minh (đã gỡ bỏ hoàn toàn wildcard `.vercel.app`/`.trycloudflare.com`); lưu ca khám SQLite có khóa lạc quan `409 Conflict`.",
    ],
    [
        "Hàng đợi Bền bỉ & Nhật ký Pháp lý WORM",
        "`web/may-chu/hang-doi.ts`\n`web/may-chu/worm.ts`\n`web/may-chu/routes/asr.ts`\n`web/may-chu/routes/sign-off.ts`",
        "`taoHangDoi()`, `taoKhoWorm()`, `ghiSignOff()`, `xacMinhChuoi()`",
        "Hàng đợi SQLite tự khôi phục việc dở dang khi máy chủ khởi động lại, giữ kết quả theo TTL (chống lỗi mất kết quả khi F5). Bảng `worm_signoff` có SQLite trigger cấm `UPDATE/DELETE`, nối băm `SHA-256`, đối chiếu tệp neo `.anchor.json` và chặn cứng ký duyệt khi thiếu căn cứ.",
    ],
    [
        "Trợ lý Đa tác tử Ẩn danh & Kiểm định số",
        "`web/may-chu/tro-ly/dieu-phoi.ts`\n`web/may-chu/tro-ly/an-danh.ts`\n`web/may-chu/tro-ly/tac-tu-tai-cho.ts`\n`web/may-chu/tra-cuu/kiem-dinh-so.ts`",
        "`chayDieuPhoi()`, `xayDuLieuAnDanh()`, `soLech()`",
        "Lập kế hoạch tối đa 6 bước tra cứu y văn (Bộ Y tế, WHO, PubMed, openFDA, DailyMed). Chỉ gửi allowlist ẩn danh (giữ nhãn `[DỊ ỨNG]`, loại thuốc đã ngừng, chặn câu hỏi chứa tên/SĐT/CCCD); kiểm định chéo số liệu quy đổi đơn vị `g/mg/mcg` và `/phút ↔ /giờ`; đẩy tiến độ qua SSE stream.",
    ],
    [
        "Không gian Soạn thảo & Chốt Ký duyệt",
        "`web/src/App.tsx`\n`web/src/components/NoteEditorView.tsx`\n`web/src/lib/compileEffectiveNote.ts`\n`web/src/hooks/useSessionsStore.ts`",
        "`taoHoSo()`, `compileEffectiveNote()`, `kiemTraDieuKienKyDuyet()`, `computeNoteSignOffHash()`",
        "Quản lý đa ca khám không khóa trắng màn hình khi GPU đang chạy ca khác; biên dịch văn bản hiệu lực tức thì theo quyết định `Giữ / Sửa / Bỏ`; tính băm `SHA-256` chuẩn FIPS 180-4; khóa nút `Ký duyệt` khi còn mục `Cần xác nhận`; đồng bộ đa tab qua `BroadcastChannel`.",
    ],
    [
        "Đối chiếu Dây nối Căn cứ & Nghe lại Âm thanh",
        "`web/src/components/VerificationView.tsx`\n`web/src/components/DuyetBenCanh.tsx`\n`web/src/hooks/useTurnAudioPlayer.ts`\n`web/src/lib/asrHighlight.ts`",
        "`VerificationView`, `DuyetBenCanh`, `useTurnAudioPlayer`, `phanTichVungMoAsr()`",
        "Vẽ dây nối Bezier hai cột từ lượt lời thoại sang từng mệnh đề (dây đỏ = cần xác nhận, xanh = không cảnh báo); phím tắt duyệt nhanh `J/K/Enter/Backspace`; bấm nút **Nghe lại** phát đúng đoạn ghi âm gốc `[start - 0.5s, end + 0.5s]`; tô cam vùng số/phủ định/ASR mờ.",
    ],
    [
        "Công cụ Lâm sàng Quanh Bản nháp",
        "`TranscriptView.tsx` + `radarCoDo.ts`\n`ContextView.tsx`\n`BhytPrecheckModal.tsx`\n`SbarModal.tsx` + `HisSmartCopyPopover.tsx`\n`ToDanDoBenhNhanModal.tsx`\n`CrossVisitBanner.tsx`",
        "`quetCoDo()`, `taoPhieuSbar()`, `tachMucHis()`, `phatHienMauThuanXuyenLanKham()`",
        "Gợi ý tối đa 2 câu hỏi cờ đỏ tại chỗ (0 token); nhập tuổi/giới tường minh & đọc phiếu xét nghiệm cũ; tiền kiểm ICD-10 4 ký tự; tạo phiếu bàn giao SBAR & chép từng ô sang phần mềm HIS; in tờ dặn dò A4 kèm đọc giọng nói tiếng Việt TTS; cảnh báo mâu thuẫn với lần khám trước.",
    ],
]


BANG_KHA_THI = [
    [
        "1. Phần cứng & Hạ tầng\n(On-Premise / Edge)",
        "Rất khả thi ở 3 quy mô:\n• **Trạm đơn:** 1 PC gắn card phổ thông RTX 3060 12GB (`~8–10 triệu VNĐ`), mô hình `Qwen3-4B` 4-bit QLoRA chỉ chiếm `~3,5–3,8 GB` VRAM lúc chạy.\n• **Phòng khám nhiều bàn:** Dùng chung 1 máy chủ GPU nội bộ LAN qua cờ `--mo-hinh-xa` (có khử định danh trước khi qua LAN và xếp hàng SQLite).\n• **Máy yếu không GPU:** Chạy `--khong-mo-hinh` (`< 1s` khởi động) để mở ca chạy trước, tra cứu, tiền kiểm BHYT, SBAR.",
    ],
    [
        "2. Quy trình Khám Ngoại trú\n(50–80 ca/ngày, 3–5 phút/ca)",
        "Giải quyết bài toán độ trễ `~3,5 phút` bằng **xử lý nền bất đồng bộ theo từng ca (`202 Accepted` + `generatingSessionId`)**:\n• Kết thúc khám Ca A, bác sĩ bấm tạo nháp rồi gọi ngay bệnh nhân Ca B vào khám — màn hình Ca B hoàn toàn không bị khóa.\n• Khi khám xong Ca B, bản nháp Ca A đã dựng xong ở nền. Bác sĩ chỉ mất `15–30 giây` duyệt các dòng đỏ ở mục `Cần xác nhận` bằng phím tắt `J/K/Enter` rồi bấm `Chép HIS`.",
    ],
    [
        "3. Tích hợp Phần mềm Bệnh viện\n(VNPT-HIS, Viettel HIS, FPT.eHospital)",
        "Không đòi hỏi bệnh viện phải sửa mã HIS ngay từ ngày đầu nhờ **lộ trình 2 bước thực tế**:\n• **Bước 1 (Áp dụng ngay, 0 chi phí tích hợp):** Nút `Chép HIS` (`HisSmartCopyPopover.tsx`) tách sẵn đúng từng ô (*Lý do khám, Bệnh sử, Khám thực thể, Chẩn đoán, Hướng xử trí*) để dán 1 chạm vào cửa sổ HIS đang mở.\n• **Bước 2 (Liên thông chuẩn hóa):** Xuất gói JSON chuẩn quốc tế `HL7 FHIR R4` và bộ thẻ `XML1–XML5` theo Quyết định 130/QĐ-BYT & 4750/QĐ-BYT.",
    ],
    [
        "4. Pháp lý, Bảo mật & Đạo đức\n(NĐ 13/2023 & TT 46/2018)",
        "Thiết kế bám sát hành lang pháp lý y tế Việt Nam:\n• **Nghị định 13/2023/NĐ-CP:** Ghi âm và tạo bản nháp chạy 100% nội bộ tại chỗ, `0 byte` hội thoại gửi lên đám mây mặc định; công tắc mô hình ngoài mặc định **TẮT**; trợ lý tra cứu chỉ gửi allowlist ẩn danh và chặn câu hỏi chứa tên/SĐT/CCCD.\n• **Luật Khám bệnh, chữa bệnh 2023:** Phần mềm chỉ tạo **bản nháp**, khóa cứng không tự hoàn tất khi thiếu căn cứ, lưu vết quyết định bác sĩ bằng chuỗi băm WORM `SHA-256`.",
    ],
    [
        "5. Chi phí & Bản quyền\n(Tài chính bền vững)",
        "• **Chi phí API biến đổi:** `0 VNĐ / ca khám` cho luồng chính (không tốn $280–$420 / 1.000 ca như gọi API ngoại).\n• **Sạch bản quyền thương mại:** Trọng số `Qwen3-4B` (Apache-2.0), mã kiểm tra thuần Python/TypeScript tự chủ; chủ động loại trừ các tập dữ liệu/trọng số cấm thương mại (`CC-BY-NC`, PhysioNet DUA).",
    ],
    [
        "6. Rào cản Thực tế & Lộ trình\n(Nói thẳng giới hạn)",
        "• **Giới hạn hiện tại:** (1) Chưa thử trên ghi âm bệnh nhân thật (cần xin Hội đồng Đạo đức IRB); (2) ASR còn sai tên thuốc ngoại lai khi phòng khám ồn; (3) Bảng tri thức thuốc `data/tri_thuc_thuoc.json` mới là bản nháp kỹ thuật (`da_duyet=false`); (4) Tốc độ `3,5 phút/ca` trên PyTorch mặc định còn chậm.\n• **Lộ trình tiếp theo:** Chuyển suy luận sang `vLLM / llama.cpp + XGrammar` để rút thời gian tạo nháp xuống `< 25 giây/ca`; mời dược sĩ lâm sàng duyệt bảng thuốc; thử nghiệm chéo với 8–10 bác sĩ ngoại trú.",
    ],
]


BO_22_CAU_HOI_BGK = [
    # --- NHÓM A: 3 YÊU CẦU CẢI TIẾN CHẶNG 1 AI 2026 ---
    (
        1, "TRỌNG TÂM", "Yêu cầu 1 BGK · Bỏ sót vs Sai sót",
        "Nhận xét vòng trước chỉ ra sự đánh đổi giữa giảm lỗi nghiêm trọng và tỷ lệ bỏ sót thông tin. Nhóm đã định nghĩa lại lỗi và giải quyết sự đánh đổi này như thế nào?",
        "Thay vì dùng một ngưỡng cắt bỏ cứng (hoặc cho vào bệnh án, hoặc xoá mất), MediTrace tách đánh giá thành **2 trục độc lập** (mức nghiêm trọng lâm sàng × độ bất định căn cứ) và định tuyến vào **3 vùng**: thông tin chưa chắc được giữ nguyên trong mục **`CẦN XÁC NHẬN`** kèm lý do chứ tuyệt đối không âm thầm loại bỏ.",
        "Định nghĩa 13 nhóm lỗi (56 mã) tại `src/canh_bao/loai.py` (hàm `muc_do()` tự nâng bậc cho `di_ung`, `thuoc_nti`, tập `LUON_CAO`). Định tuyến tại `src/cong_rui_ro.py` (`dua_sang_xac_nhan`) và `src/sinh_benh_an.py` (`_muc_cho`).",
        "Tỷ lệ bỏ sót ở khâu trích xuất (30 ca phát triển độc lập, 304 mệnh đề) giảm từ **43,1%** (Qwen3-4B chưa train) xuống **11,5%** (Qwen3-4B + adapter QLoRA, khoảng tin cậy 95%: `8,4%–15,6%`, `0` ca lỗi JSON — `docs/ket-qua/bo-sot-qwen3-4b.md`). Ở khâu khóa căn cứ, tỷ lệ thông tin không vào thân tăng từ `4,5%` lên `7,7%` ở bộ đổi người, nhưng toàn bộ số bị chặn đều nằm ở mục `CẦN XÁC NHẬN` để bác sĩ thấy ngay.",
    ),
    (
        2, "XOÁY SÂU / BẮT BẺ", "Yêu cầu 1 BGK · Chốt chặn hoàn tất hồ sơ",
        "Nếu bác sĩ đang vội khám đông mà bấm thẳng nút 'Ký duyệt' hoàn tất hồ sơ khi bản nháp còn câu thiếu căn cứ hoặc còn mục 'Cần xác nhận' chưa xem thì hệ thống xử lý thế nào?",
        "Hệ thống **chặn cứng ở cả hai tầng (Giao diện + Máy chủ WORM)** — bác sĩ không thể ký duyệt hoàn tất hồ sơ khi chưa có mệnh đề có căn cứ hoặc khi còn bất kỳ dòng nào trong mục `Cần xác nhận` chưa được quyết định rõ (`Xác nhận / Sửa / Bỏ`).",
        "Ở giao diện: hàm `kiemTraDieuKienKyDuyet()` trong `web/src/lib/compileEffectiveNote.ts` đổi nút ký thành cảnh báo vàng `Cần xác nhận (N)` (hoặc `Chưa đủ căn cứ`); nếu bấm vào, `App.tsx` từ chối ký, hiện thông báo lỗi, tự bật ngăn `DuyetBenCanh.tsx` và cuộn thẳng tới mệnh đề chưa duyệt đầu tiên. Ở máy chủ: `kiemTraInputSignOff()` trong `web/may-chu/worm.ts` trả `HTTP 400` nếu `tongMenhDe < 1`, `soBo >= tongMenhDe`, `tyLeCoNguon <= 0` hoặc `soChuaXacNhan > 0`.",
        "Đã kiểm chứng tự động bằng các ca kiểm thử biên trong `web/src/lib/compileEffectiveNote.test.ts`, `web/may-chu/worm.test.ts` và `web/may-chu/routes/routes.test.ts` (`43/43` phép thử TypeScript vượt qua 100%).",
    ),
    (
        3, "TRỌNG TÂM", "Yêu cầu 2 BGK · Kiểm soát lỗi dây chuyền",
        "Lỗi ở bước chép lời (ASR), gán người nói hoặc gán chủ thể có thể lan truyền làm ghi nhầm bệnh cho người khác (ví dụ hai bệnh nhân cùng phòng hoặc mẹ kể bệnh của mẹ). Hệ thống chặn ở từng bước ra sao?",
        "MediTrace đặt chốt kiểm tra riêng ở từng giao điểm giữa các bước thay vì tin mù quáng đầu ra bước trước: (1) Chặn tạo bản nháp khi còn lượt chưa gán vai; (2) Tách `nguoi_noi` khỏi `chu_the_id`; (3) Khóa K3 đối chiếu ngược đại từ trong câu trích dẫn gốc để bắt lỗi ngay cả khi AI gán nhầm chủ thể.",
        "Bước 0: `dich_vu.py:660` trả `409 asr_review_pending` và `App.tsx:225` chặn nếu còn lượt thiếu vai. Bước 2: `src/thuc_the.py` gán `chu_the_id != 0` cho người nhà/người đi cùng, `sinh_benh_an.py` cấm tuyệt đối `chu_the_id != 0` vào mục của bệnh nhân. Bước 4: `khoa_bang_chung.py` bắt mẫu người nhà tự xưng *'bản thân tôi / còn tôi bị dị ứng…'* (`chu_the_nguoi_ke`) đẩy thẳng xuống `CẦN XÁC NHẬN`.",
        "Trình diễn trực tiếp bằng **Ca mẫu 2 (`demo_hai_benh_nhan`)** và **Ca mẫu 1 (`demo_bs_nguoi_nha_nhi`)** trong `src/ca_mau_bgk.py` (bấm *'Xem thử với ca mẫu'*, không cần GPU) và kiểm thử đối kháng `tests/test_demo_bac_si_nguoi_nha.py`. Trên tập giữ kín 240 ca, độ nhạy bắt lỗi `doi_chu_the` đạt **0,946** (`[0,910–0,968]`).",
    ),
    (
        4, "TRỌNG TÂM", "Yêu cầu 2 BGK · Trạng thái đính chính & Mâu thuẫn",
        "Khi người bệnh nói nhầm rồi tự sửa ('4 ngày... à không, chiều hôm qua'), hoặc con gái nói một đằng bố nói một nẻo thì hệ thống cập nhật trạng thái thế nào? Có xoá thông tin cũ không?",
        "Hệ thống **không bao giờ xoá mất thông tin cũ** mà cập nhật bằng máy trạng thái theo 4 quan hệ: tự sửa (hoặc người nói trước xác nhận đồng thuận ở lượt kế tiếp) thì bản cũ chuyển sang `bị thay thế` (đưa xuống `CẦN XÁC NHẬN` để lưu vết kiểm toán), bản mới giữ `còn hiệu lực`; còn hai người nói trái nhau chưa ai xác nhận thì cả hai hạ về `chưa giải quyết` (`mâu thuẫn`) để bác sĩ hỏi lại.",
        "Xử lý tại `src/cap_nhat.py` (`ap_luat`, `_co_dong_thuan_cheo`), `src/may_trang_thai_hoi_thoai.py` và luật bắt đính chính ngược `src/canh_bao/toan_ca.py` (`CORRECTION_NOT_APPLIED` khi mô hình lỡ giữ con số nằm trước chữ *'à nhầm / không phải'*).",
        "Trên bộ thử thách *tự sửa*, tỷ lệ thông tin cũ đã bị đính chính vẫn còn sót trong thân bản nháp giảm hơn 14 lần: từ **11,48%** xuống còn **0,80%**. Luật `dinh_chinh_nguoc` ở vòng 6 bắt đạt **1,000** (`[0,896–1,000]`) trên tập điều chỉnh.",
    ),
    (
        5, "XOÁY SÂU / BẮT BẺ", "Yêu cầu 3 BGK · Tính độc lập bộ dữ liệu",
        "Bộ 5.000 mẫu sinh từ khuôn có nguy cơ trùng lặp ngữ nghĩa giữa tập huấn luyện và kiểm thử. Nhóm chứng minh tính độc lập và công khai cách kiểm soát mẫu tổng hợp như thế nào?",
        "Dự án đã mở rộng kho khuôn từ 200 lên **657 khuôn ca bệnh trên 21 hệ cơ quan**, ngữ cảnh hóa câu hỏi bác sĩ, và **chia tách tập theo đơn vị KHUÔN BỆNH (`benh`) theo từng đợt** — tuyệt đối không chia ngẫu nhiên theo dòng hội thoại, nên **0 khuôn bệnh nào xuất hiện ở cả Train lẫn Dev/Test**.",
        "Hợp nhất kho khuôn tại `src/kho_khuon.py`; chia tập tất định không rò rỉ tại `src/tach_tap_viet.py` (kiểm chứng bằng `tests/test_chia_khuon_mo_rong_khong_doi.py` giữ nguyên mã băm vàng 200 khuôn gốc); kiểm chất lượng câu tại `tools/kiem_chat_luong_cau.py`; đo ma trận trùng lặp tại `src/kiem_nghiem_ngoai_khuon.py`; công khai danh sách tên khuôn từng tập tại `data/manifest_v2_mo_rong_5000.json`.",
        "Chia `515` khuôn Train (`3.925` ca) / `72` khuôn Dev (`551` ca) / `70` khuôn Test (`524` ca), giao tên khuôn = **`0`**. Trên `36.050` cặp khuôn Train–Test, Jaccard từ khóa triệu chứng trung bình chỉ **0,0587** (`p95 = 0,1172`, cặp ≥ 0,20 chỉ **0,17%**), Trigram Jaccard **0,0287**. Câu duy nhất tăng **+127%** (`20.190 -> 45.835`), lặp mọi câu giảm từ `76,92%` xuống **47,37%** (câu ≥ 8 từ: **42,19%**), trích dẫn khớp chuỗi con `52.634/52.634 (100%)`.",
    ),
    (
        6, "CHUYÊN SÂU", "Yêu cầu 3 BGK · Thử ngoài khuôn & ngoài nguồn",
        "Khi đem hệ thống thử trên kịch bản bệnh mới hoàn toàn ngoài kho khuôn và văn bản thực tế từ nguồn bên ngoài, kết quả ra sao và phát hiện lỗi gì?",
        "Nhóm đã thử trên cả 3 mức độc lập: (1) Khuôn giữ lại chưa từng học (`viet_phat_trien`, `thach_thuc_v2`); (2) 10 kịch bản bệnh hiếm ngoài kho 657 khuôn (`OOT_01..10`); và (3) 200 câu hỏi người bệnh thật từ bộ dữ liệu công khai `ViMQ`. Đặc biệt, phép thử `ViMQ` đã giúp phát hiện một lỗi lệch phân phối rất quan trọng.",
        "Mã kiểm nghiệm ngoài khuôn nằm ở `src/kiem_nghiem_ngoai_khuon.py`; đường ống thử nghiệm ngoài nguồn `ViMQ` nằm ở `src/nap_vimq.py`, `src/loc_nhan_may.py`, `src/gan_nhan_truoc.py`; nhật ký phân tích lỗi ghi tại `docs/tien-do-21-11-2026.md`.",
        "• Tập giữ kín `thach_thuc_v2` (240 ca): độ nhạy lớp cảnh báo giữ nguyên **0,871** (không suy giảm so với `0,871` trên tập điều chỉnh).\n• 10 kịch bản ngoài kho 657 khuôn (52 mệnh đề, đo tầng luật): đúng chủ thể **52/52**, chống gán nhầm người nhà **11/11**, bắt đính chính **10/10**.\n• 200 mẫu `ViMQ` ngoài nguồn: xuất JSON hợp lệ **96,0%**, phủ thực thể gốc **284/322 = 88,2%**; phát hiện lỗi mô hình biến câu hỏi chưa trả lời của người bệnh thành mệnh đề khẳng định -> quyết định **không dùng nhãn máy ViMQ để train** và dùng luật `QUESTION_AS_FACT` để chặn.",
    ),

    # --- NHÓM B: KIẾN TRÚC KỸ THUẬT, MÔ HÌNH AI & MÃ NGUỒN ---
    (
        7, "XOÁY SÂU / BẮT BẺ", "Kiến trúc Neuro-Symbolic vs Viết thẳng",
        "Tại sao không để mô hình ngôn ngữ viết thẳng bản nháp bệnh án hoặc tự đọc lại để sửa (Nhánh A+), mà phải tách thành 5 bước trung gian? Có phải cách tách bước lúc nào cũng điểm cao hơn không?",
        "**Không — và nhóm ghi rất thẳng điều này trong README:** trên dữ liệu mô phỏng, cách để mô hình viết thẳng văn xuôi thậm chí đạt điểm quy gán tự động cao hơn MediTrace ở một số bộ thử thách. Lý do chọn kiến trúc 5 bước không phải để thắng điểm văn xuôi, mà vì **văn xuôi viết thẳng là hộp đen không thể kiểm chứng từng dòng**.",
        "Đối chứng các nhánh `A`, `A+`, `B`, `C`, `C_khoa`, `C_khoa_hoi` được viết chung trong `src/nhanh.py` để so sánh công bằng trên cùng một đầu ra trích xuất.",
        "Ở bộ *đổi người*, mô hình viết thẳng học vẹt khuôn văn mẫu và chép giống từng chữ ở `30–63%` số ca (đạt `0,939` so với `0,748`). Nhưng khi nó ghi sai 1 dòng dị ứng trong đoạn văn trôi chảy, bác sĩ phải dò lại cả cuộc khám; còn với MediTrace (`C_khoa` nâng F₁ từ `66,1%` lên **70,8%**, giảm SER `45,4% -> 36,9%` so với chỉ trích xuất), **mọi câu trong bản nháp đều có dây nối về đúng lượt nói và giây âm thanh gốc**, và khi sai biết chính xác sai ở bước nào để sửa luật ngay.",
    ),
    (
        8, "CƠ BẢN", "Lựa chọn mô hình Qwen3-4B + DPO",
        "Vì sao dự án chọn mô hình Qwen3-4B (kèm QLoRA & DPO) cho bước rút mệnh đề mà không dùng mô hình 8B/14B hoặc gọi API đám mây?",
        "Vì 3 ràng buộc thực tế của phòng khám Việt Nam: (1) **Bảo mật pháp lý** — không gửi lời thoại khám bệnh ra máy chủ ngoài; (2) **Phần cứng vừa túi tiền** — chạy gọn trên 1 card phổ thông 8–12GB VRAM; (3) **Bản quyền mở Apache-2.0** cho phép triển khai bệnh viện hợp pháp.",
        "Cấu hình mô hình mặc định tại `src/duong_dan.py` (`MODEL_CHINH = 'Qwen/Qwen3-4B'`, ghim bằng `tests/test_model_chinh.py` và `tests/test_dich_vu.py`). Huấn luyện QLoRA ngữ cảnh 4.096 token với `src/loss_theo_doan.py` và tinh chỉnh chống lỗi khó bằng DPO tại `src/train_dpo.py`.",
        "Nhờ tính loss theo đoạn và bỏ mặt nạ chú ý 4 chiều dư thừa, đỉnh VRAM khi train chuỗi dài `3.925` token trên RTX 3060 giảm từ tràn bộ nhớ (`> 11 GiB`) xuống chỉ còn **6,421 GiB**; suy luận 4-bit NF4 chỉ chiếm `~3,5–3,8 GiB` VRAM.",
    ),
    (
        9, "CHUYÊN SÂU", "Khóa căn cứ K1–K6 vs Lớp cảnh báo",
        "Trong code vừa có `khoa_bang_chung.py` (K1–K6) vừa có gói `src/canh_bao/` (56 mã lỗi). Hai tầng này khác nhau thế nào, có bị trùng lặp thừa thãi không?",
        "Hai tầng trả lời **hai câu hỏi khác hẳn nhau**: `khoa_bang_chung` là **cổng gác cửa nhị phân** (*mệnh đề này có đủ căn cứ tối thiểu để vào thân bản nháp không?*), còn `canh_bao` là **bộ chẩn đoán chi tiết cho bác sĩ** (*nếu mệnh đề này có rủi ro sai tinh vi vượt qua cổng gác, nó sai kiểu gì và bác sĩ cần nhìn vào lượt nào?*).",
        "`src/khoa_bang_chung.py` kiểm 6 điều kiện nền tảng. Còn `src/canh_bao/` (`than_the.py`, `thoi_diem.py`, `toan_ca.py`, `lam_sang.py`) bắt những lỗi tinh vi mà câu trích vẫn nguyên văn hợp lệ — ví dụ lượt dẫn nói *'hố chậu phải'* nhưng mệnh đề ghi *'trái'* (`LATERALITY_CHANGED`), nói *'từng hút thuốc'* ghi thành *'đang hút'* (`PAST_CURRENT_CONFUSION`), hoặc bỏ sót lượt có tên thuốc (`OMITTED_MEDICATION`).",
        "Bổ sung 4 luật mới ở `src/canh_bao/` (vòng 6) giúp nâng độ nhạy bắt 14 loại lỗi khó (khi câu trích dẫn vẫn giữ nguyên văn!) từ **0,682** lên **0,889** (`doi_ben: 0,250 -> 0,950`, `doi_muc_do: 0,500 -> 0,970`, `qua_khu_hien_tai: 0,012 -> 0,730`, `dinh_chinh_nguoc: 0,000 -> 1,000`).",
    ),
    (
        10, "TRỌNG TÂM", "Phép chứng minh ROUGE-1 = 1,0000",
        "Trong báo cáo nhóm nêu khi tráo đổi chỗ 'bệnh nhân' và 'người nhà', điểm ROUGE-1 vẫn bằng 1,0000 tuyệt đối. Phép đo này thực hiện thế nào và chứng minh điều gì?",
        "Phép đo này chứng minh các thước đo đếm từ truyền thống của tóm tắt văn bản (như ROUGE) **mù hoàn toàn trước lỗi quy gán chủ thể trong y khoa**, từ đó lý giải vì sao dự án bắt buộc phải xây dựng đáp án có cấu trúc `dap_an` và thước đo quy gán theo ô (`SER`, `Attribution F1`).",
        "Bởi vì ROUGE-1 chỉ đếm tập hợp từ đơn (unigram overlap) giữa bản dự đoán và bản tham chiếu: khi hoán đổi vị trí chữ *'bệnh nhân'* và *'người nhà'* trong cùng một bản bệnh án (biến dị ứng/bệnh hen của người nhà thành của người bệnh), tổng số lần xuất hiện của từng từ không đổi nên điểm trùng từ vẫn đạt `1,0000`.",
        "Thử nghiệm trên **400 bản hồ sơ**: ROUGE-1 giữ nguyên **1,0000** (0% phát hiện), trong khi thước đo quy gán riêng của dự án lập tức tụt **0,1381 điểm**, chỉ đích danh lỗi sai chủ thể.",
    ),
    (
        11, "CHUYÊN SÂU", "Chuỗi băm WORM & Tệp neo .anchor.json",
        "Cơ chế ký duyệt WORM SHA-256 của hệ thống chống sửa lén hoạt động cụ thể ra sao? Nếu kẻ có quyền quản trị máy chủ mở trực tiếp file SQLite xoá dòng cuối hoặc xoá trắng bảng thì sao?",
        "Nhóm đã thiết kế **3 lớp khóa chéo độc lập**: (1) Trigger SQLite chặn trực tiếp lệnh `UPDATE/DELETE`; (2) Chuỗi băm nối tiếp `prev_hash -> curr_hash` từ `GENESIS_HASH_WORM`; và (3) **Tệp neo ngoài `.anchor.json` + nhật ký `.jsonl`** để bắt quả tang cả tấn công cắt đuôi (tail truncation), cắt đầu hoặc xoá trắng bảng.",
        "Triển khai tại `web/may-chu/worm.ts` (`damBaoBangWorm`, `ghiSignOff`, `xacMinhChuoi`) và đối xứng ở tầng Python `src/worm_audit_log.py`. Trên trình duyệt, `compileEffectiveNote.ts` tính `SHA-256` chuẩn FIPS 180-4 trên cả nội dung SOAP gốc lẫn mảng quyết định `quyetDuyet/banSuaDuyet` — hễ sửa 1 chữ sau khi ký, `isSignOffStale()` đổi nút sang **`Đã sửa · Ký lại`**.",
        "Kiểm thử tấn công giả lập trong `web/may-chu/worm.test.ts`: thử `DROP TRIGGER` rồi xoá dòng cuối `seq=3`, xoá dòng đầu `seq=1`, xoá trắng bảng hoặc ghi hỏng `.anchor.json` -> `xacMinhChuoi()` (`GET /api/worm/verify`) đều phát hiện chính xác 100% và chặn ghi đè làm sạch dấu vết (`HTTP 409 WORM Violation`).",
    ),
    (
        12, "CHUYÊN SÂU", "Trợ lý đa tác tử & Chống lộ PII",
        "Ở ngăn bên phải có Trợ lý nhiều tác tử gọi mô hình ngoài để tra cứu y văn. Làm sao đảm bảo không lộ danh tính bệnh nhân và không gửi nhầm dị ứng thành thuốc đang dùng?",
        "Trợ lý **không dùng cách tìm-và-xoá tên trên văn bản tự do** (vì dễ sót), mà dựng chuỗi gửi đi bằng **danh sách cho phép (Allowlist)** từ các trường cấu trúc, giữ nguyên nhãn **`[DỊ ỨNG]`**, loại bỏ thuốc `đã ngừng`, đồng thời quét câu hỏi của bác sĩ để chặn ngay nếu chứa danh tính.",
        "Triển khai tại `web/may-chu/tro-ly/an-danh.ts`, `tac-tu-tai-cho.ts` và `dieu-phoi.ts`. Mọi câu trả lời từ y văn ngoài đều đi qua bộ kiểm định số liệu tất định `web/may-chu/tra-cuu/kiem-dinh-so.ts` (quy đổi bậc đơn vị `g = 1.000 mg = 1.000.000 mcg`, tốc độ truyền `/phút = 60 × /giờ`, giữ chuẩn số thập phân `0.125 mg`). Ngoài ra, quản trị viên có công tắc khóa toàn hệ thống (`MEDITRACE_TRO_LY_NGOAI=tat`).",
        " Giao diện hiển thị công khai hộp thu gọn *'Dữ liệu gửi ra ngoài (đã ẩn danh)'* để bác sĩ kiểm tra từng chữ trước mắt; kiểm thử đơn vị và tích hợp tại `an-danh.test.ts`, `kiem-dinh-so.test.ts`, `tich-hop.test.ts`.",
    ),

    # --- NHÓM C: TIẾNG VIỆT LÂM SÀNG, ÂM THANH ASR & DƯỢC LÝ ---
    (
        13, "TRỌNG TÂM", "Tiếng Việt lược chủ ngữ & Đại từ họ hàng",
        "Bệnh nhân Việt Nam rất hay nói câu cụt chủ ngữ ('Đêm qua nôn hai lần') và dùng từ 'cháu', 'con', 'em' vừa để tự xưng vừa để chỉ người khác. Thuật toán giải quyết thế nào và còn giới hạn nào?",
        "Hệ thống kết hợp **vai người nói của lượt hiện tại + câu hỏi bác sĩ liền trước + từ chỉ quan hệ nhân thân**; nếu câu lược chủ ngữ nằm trong bối cảnh có từ hai người bệnh/người nhà trở lên làm mơ hồ chủ thể, hệ thống gắn cờ nghi ngờ để đẩy sang **`CẦN XÁC NHẬN`** thay vì đoán mò.",
        "Xử lý tại `src/thuc_the.py`, `src/khoa_bang_chung.py` (`TU_BENH_NHAN_RO`, `TU_HO_HANG`, `SPEAKER_SUBJECT_MISMATCH`, `SUBJECT_AMBIGUOUS`) và `src/may_trang_thai_hoi_thoai.py` (`BoGiaiQuyetProDrop`).",
        "Minh chứng trực tiếp ở Ca mẫu 2 (`demo_hai_benh_nhan` lượt 6: *'đêm qua còn nôn hai lần nữa'* được giữ ở `CẦN XÁC NHẬN`). **Giới hạn đã biết ghi rõ trong README:** khi mô hình trích người được nhắc tới là cụm *'bố em'* ở một số ngữ cảnh phức tạp, bước gom người vẫn còn trường hợp gộp nhầm — nhóm công khai lỗi này để tiếp tục hoàn thiện.",
    ),
    (
        14, "XOÁY SÂU / BẮT BẺ", "Tên thuốc dân gian & Zero Silent Normalization",
        "Khi bệnh nhân đọc tên thuốc trại âm kiểu dân gian ('vỉ a móc', 'ô mê', 'la-xích / pla-vích') hoặc ASR nghe không chắc, phần mềm có tự động sửa thành tên thuốc chuẩn trong đơn không?",
        "**Tuyệt đối KHÔNG tự động sửa ngầm vào mục thuốc chính thức!** Ví dụ *'a móc'* có thể là Amoxicillin đơn chất hoặc Co-amoxiclav (Augmentin/Klamentin); đoán mò là nguy cơ lâm sàng nghiêm trọng. Hệ thống bắt buộc cách ly sang **`CẦN XÁC NHẬN`** kèm gợi ý để bác sĩ hỏi/xem vỉ thuốc thật.",
        "Khóa K6 tại `src/khoa_bang_chung.py` chặn mọi tên thuốc trong mệnh đề không xuất hiện ở lượt thoại được dẫn (`chi_tiet_thuoc_khong_thay` / `MEDICATION_ENTITY_MISMATCH`). Đồng thời `src/dieu_phoi_ha_tang.py` và `src/guardrails.py` bôi đỏ cảnh báo âm vị thuốc dân gian, tách biệt hoàn toàn với phương ngữ triệu chứng thông thường (như *'xốt'*).",
        "Trình diễn trực tiếp trong **Ca mẫu 3 (`demo_lao_khoa_con_gai` lượt 6)**: câu *'tự ra hiệu thuốc mua vỉ a móc uống'* bị khóa K6 chặn không cho `amoxicillin` vào `THUỐC ĐANG DÙNG`, đẩy thẳng xuống `CẦN XÁC NHẬN` và khóa nút ký duyệt cho tới khi bác sĩ xác nhận.",
    ),
    (
        15, "TRỌNG TÂM", "Xét nghiệm cũ, Chỉnh liều thận & BHYT ICD-10",
        "Các tính năng đọc phiếu xét nghiệm cũ, gợi ý chỉnh liều suy thận và tiền kiểm BHYT hoạt động thế nào? Bảng tri thức thuốc và mã bệnh đã được bác sĩ/dược sĩ thẩm định chưa?",
        "Các mô-đun này là **công cụ tra cứu & nhắc kiểm xung quanh bản nháp** (không tự ý sửa bản nháp): bóc chỉ số từ văn bản phiếu cũ, tự quy đổi đơn vị (`Creatinin µmol/L ↔ mg/dL`), tính độ thanh thải thận Cockcroft-Gault/eGFR theo tuổi-giới-cân nặng thật (không tự điền tuổi 50 mặc định), và gợi ý mã ICD-10 4 ký tự kèm kiểm tra cấu trúc XML1–XML5.",
        "Mã nguồn tại `src/ocr_lam_sang.py`, `src/chuan_hoa_don_vi_xet_nghiem.py`, `src/hieu_chinh_lieu.py`, `src/kiem_duyet_bhyt_va_bo_sot.py`, giao diện tại `ContextView.tsx` và `BhytPrecheckModal.tsx` (đã loại trừ bệnh đã phủ định và bệnh nền của người nhà khỏi gợi ý mã ICD-10).",
        "**Minh bạch tuyệt đối:** Toàn bộ mục trong `data/tri_thuc_thuoc.json` hiện mang cờ `da_duyet = false` (chưa qua hội đồng dược lâm sàng duyệt), nên mọi cảnh báo từ bảng này trong `src/canh_bao/lam_sang.py` đều gắn nhãn `thu_nghiem` / `can_xem`, chỉ đóng vai trò gợi ý tham khảo cho bác sĩ.",
    ),
    (
        16, "CƠ BẢN", "Cơ chế Click-to-Play nghe lại đoạn ghi âm gốc",
        "Khi bác sĩ nghi ngờ một con số liều thuốc trên bản nháp và bấm nút 'Nghe lại', hệ thống làm sao phát đúng câu nói đó trong đoạn băng dài 10 phút?",
        "Mỗi lượt thoại sau khi gỡ băng đều lưu mốc thời gian `start_s` và `end_s`; mỗi mệnh đề lưu danh sách số thứ tự lượt `evidenceTurns` và `audio_spans` (`start_ms..end_ms`). Khi bấm **Nghe lại** ở lượt `k`, trình phát nhảy thẳng tới `max(0, start_s - 0.5)` và tự dừng ở `end_s + 0.5` giây.",
        "Triển khai tại `web/src/hooks/useTurnAudioPlayer.ts`, `web/src/lib/asrHighlight.ts` (`khoangPhatLaiLuot`, cộng đệm `0,5 giây` hai đầu để không mất âm đầu/cuối câu), hiển thị ngay trên từng thẻ mệnh đề ở `DuyetBenCanh.tsx` và `VerificationView.tsx`. Tệp âm thanh gốc được lưu bền bỉ trong IndexedDB trình duyệt theo từng `userId` (`realAudioService.ts`) nên F5 tải lại trang vẫn nghe lại được.",
        "Các mệnh đề chứa con số kèm đơn vị, từ phủ định tiếng Việt có dấu hoặc đoạn ASR độ tự tin `< 0,75` được tự động gắn nhãn cam nhắc bác sĩ ưu tiên bấm nghe lại (`asrHighlight.test.ts`).",
    ),

    # --- NHÓM D: TÍNH KHẢ THI, ĐỘ TRỄ, TÍCH HỢP HIS & PHÁP LÝ ---
    (
        17, "XOÁY SÂU / BẮT BẺ", "Bài toán độ trễ 3,5 phút trên RTX 3060",
        "README ghi tạo một bản nháp mất khoảng 3,5 phút trên card RTX 3060, trong khi một ca khám ngoại trú ở Việt Nam chỉ kéo dài 3–5 phút. Vậy bác sĩ có phải ngồi chờ 3,5 phút mới khám được ca tiếp theo không?",
        "**Bác sĩ chờ 0 giây để chuyển sang ca khám tiếp theo!** 3,5 phút là thời gian GPU chạy ngầm ở hậu trường, còn giao diện đã được kiến trúc bất đồng bộ theo từng mã ca (`generatingSessionId`), cho phép bác sĩ khám cuốn chiếu liên tục.",
        "Khi bác sĩ bấm tạo nháp cho Ca 1, `POST /api/generate-note` (`web/may-chu/routes/asr.ts`) đưa việc vào hàng đợi SQLite `hang-doi.ts` và trả mã `202 Accepted` kèm `jobId`. Ở `web/src/App.tsx`, tiến độ chỉ gắn với `generatingSessionId = Ca 1`; bác sĩ bấm tạo ngay Ca 2 để thu âm khám cho người tiếp theo bình thường, trên đầu trang chỉ hiện thanh báo nhỏ *'Đang tạo bản nháp nền cho một ca khám khác'*. Khi xong, kết quả tự gắn về đúng `targetId = Ca 1` (chống stale closure).",
        "Ngoài ra, về lộ trình tối ưu kỹ thuật: 3,5 phút hiện tại là chạy qua `transformers.generate` tuần tự trên Python; khi chuyển sang engine `vLLM` hoặc `llama.cpp` với giải mã bitmask `XGrammar` cho mô hình 4B, tốc độ sinh ~800 token JSON giảm xuống còn **15–25 giây/ca** trên cùng phần cứng.",
    ),
    (
        18, "TRỌNG TÂM", "Tích hợp HIS bệnh viện thực tế",
        "Các bệnh viện công tại Việt Nam đang dùng VNPT-HIS, Viettel HIS, FPT.eHospital rất chặt chẽ và khó mở cổng kết nối cho phần mềm bên ngoài. MediTrace triển khai thực tế bằng cách nào?",
        "Dự án thiết kế **cầu nối 2 cấp độ** để dùng được ngay lập tức tại phòng khám mà không cần chờ bệnh viện sửa phần mềm HIS, đồng thời sẵn sàng chuẩn liên thông quốc gia khi triển khai cấp viện.",
        "• **Cấp độ 1 (Zero-Integration — dùng ngay hôm nay):** Popover `HisSmartCopyPopover.tsx` + `web/src/lib/sbar.ts` tự động gom các mệnh đề đã duyệt (bỏ sạch các dòng bác sĩ bấm `Bỏ`, áp dụng câu đã `Sửa`) thành đúng 5 ô chuẩn của màn hình khám bệnh HIS Việt Nam để bác sĩ bấm chép 1 chạm từng ô.\n• **Cấp độ 2 (Liên thông API chuẩn Bộ Y tế):** Xuất trực tiếp gói `HL7 FHIR R4 Bundle` (`src/fhir_exporter.py`) và cấu trúc bảng `XML1–XML5` theo Quyết định 130/QĐ-BYT & 4750/QĐ-BYT (`src/kiem_duyet_bhyt_va_bo_sot.py`).",
        "Trong XML2/FHIR, hệ thống đã kiểm toán kỹ để **không đẩy thuốc đã ngừng hoặc dị ứng thuốc sang danh sách thuốc chỉ định**, và đánh lại số thứ tự `STT` liên tục trong XML5.",
    ),
    (
        19, "CƠ BẢN", "Trách nhiệm pháp lý khi xảy ra sai sót",
        "Nếu bản nháp có sai sót mà bác sĩ ký duyệt dẫn tới sự cố chuyên môn thì trách nhiệm pháp lý thuộc về ai? Phần mềm bảo vệ bác sĩ và người bệnh như thế nào?",
        "Theo Luật Khám bệnh, chữa bệnh 2023, **bác sĩ hành nghề luôn là chủ thể chịu trách nhiệm chuyên môn cuối cùng**. MediTrace được định vị nghiêm ngặt là **công cụ dựng bản nháp có truy vết**, không phải thiết bị tự động chẩn đoán hay tự động kê đơn.",
        "Phần mềm giảm thiểu rủi ro cho cả người bệnh lẫn thầy thuốc bằng 3 hàng rào kỹ thuật: (1) Mọi bản nháp mới tạo đều gắn nhãn rõ *'Chưa có bác sĩ duyệt'*; (2) Chốt chặn `kiemTraDieuKienKyDuyet` + `worm.ts` cấm ký hoàn tất khi còn dòng nghi ngờ chưa xem; (3) Mọi mệnh đề có mỏ neo `[T_i]` và đoạn ghi âm gốc để chứng minh minh bạch nội dung cuộc trao đổi.",
        "Khi bác sĩ sửa lại hồ sơ sau lần ký trước, hàm `isSignOffStale()` phát hiện lệch băm `SHA-256` ngay lập tức và yêu cầu ký lại lượt mới vào sổ cái WORM.",
    ),
    (
        20, "CƠ BẢN", "Chi phí đầu tư & Vận hành phòng khám",
        "Chi phí thực tế để một phòng khám đa khoa hoặc khoa khám bệnh triển khai MediTrace Sentinel là bao nhiêu?",
        "Chi phí phần mềm và phí gọi API đám mây cho luồng dựng bệnh án chính bằng **0 VNĐ**; chi phí phần cứng tận dụng máy tính sẵn có tại phòng khám hoặc đầu tư 1 máy trạm GPU phổ thông dùng chung cho nhiều bàn khám.",
        "Kiến trúc tách rời giao diện web nhẹ (`Vite + Express + node:sqlite` tốn `< 150 MB` RAM) và dịch vụ AI Python (`src/dich_vu.py` có cờ `--tran-ram-gb`, `--nghi-sau-phut` tự nhả VRAM khi nghỉ, và `--mo-hinh-xa` chia sẻ 1 GPU qua mạng nội bộ LAN).",
        "Một máy chủ nội bộ gắn 1 card RTX 3060 12GB (chi phí phần cứng một lần khoảng `8–10 triệu VNĐ`, điện năng tăng thêm vài nghìn đồng/ngày) phục vụ được cả cụm bàn khám mà không phát sinh chi phí thuê bao API tính theo ca.",
    ),

    # --- NHÓM E: LIÊM CHÍNH KHOA HỌC & SỬ DỤNG AI LẬP TRÌNH ---
    (
        21, "XOÁY SÂU / BẮT BẺ", "Thẳng thắn về điểm yếu lớn nhất",
        "Nếu tự phê bình nghiêm khắc nhất, đâu là 3 điểm yếu lớn nhất hiện tại của MediTrace Sentinel mà nhóm chưa giải quyết xong?",
        "Nhóm công khai thẳng 3 điểm yếu lớn nhất ngay trong `README.md` và `BAO_CAO_CAI_TIEN_CHANG_1.md`, không che giấu bất kỳ số liệu bất lợi nào:",
        "1. **Chưa có dữ liệu bệnh nhân thật & nghiên cứu bác sĩ thật:** Toàn bộ 5.000 ca là hội thoại mô phỏng đều đặn hơn đời thực; dự án không tuyên bố 'giảm X% thời gian làm bệnh án ngoài đời' khi chưa đo thực nghiệm với bác sĩ.\n2. **Phát hiện bỏ sót ở khâu trích xuất còn hạn chế:** Nếu ngay từ Bước 1 mô hình Qwen3-4B bỏ quên không rút một chi tiết nằm chung lượt với chi tiết khác, bộ cảnh báo bỏ sót toàn ca bằng luật từ khóa hiện mới phủ được **12,5%** số mệnh đề bị sót (precision `2,8%` — `docs/ket-qua/canh-bao-moc-0.md`).\n3. **Nhận dạng tiếng nói (ASR) với tên biệt dược ngoại lai:** Khi nói xen tên thuốc tiếng Anh trong câu tiếng Việt có nhiễu, ASR thuần rất dễ chép trại âm, nên hiện tại hệ thống phải dựa vào cơ chế cách ly sang `CẦN XÁC NHẬN` thay vì nhận diện đúng ngay 100%.",
        "Chính việc đo lường và chỉ rõ từng điểm mù này (kèm sổ đăng ký trước `docs/dang-ky-truoc-bo-luat.md` và kiểm toán số liệu `docs/doi-chieu-so-lieu-bao-cao.md`) giúp dự án đi đúng hướng khoa học thay vì báo cáo các con số '100% hoàn hảo' ảo.",
    ),
    (
        22, "CƠ BẢN", "Khai báo sử dụng AI hỗ trợ lập trình & Kiểm chứng",
        "Nhóm đã sử dụng các công cụ AI hỗ trợ lập trình (Claude Code, Antigravity, Codex) như thế nào và làm sao đảm bảo mã nguồn do AI hỗ trợ không có lỗ hổng an toàn y khoa?",
        "Nhóm khai báo minh bạch trong `README.md`: phần lớn mã nguồn được viết với sự hỗ trợ của trợ lý lập trình AI **dưới sự chỉ đạo kiến trúc, đặt bất biến an toàn và kiểm tra chéo nghiêm ngặt của tác giả**.",
        "Quy trình kiểm soát gồm 3 vòng: (1) Mọi quy tắc lâm sàng đều phải có phép thử đơn vị trượt trước – qua sau (`pytest` và `tsx --test`); (2) Thực hiện các đợt **rà soát độc lập chéo** (như đợt rà soát 25/11 tìm và vá 9 lỗi che dị ứng/phủ định trong `tests/test_ra_soat_cuoi.py`, và đợt kiểm toán kiến trúc toàn diện sửa các lỗi khử định danh, FHIR, BHYT, đơn vị liều `kiem-dinh-so.ts`, khóa WORM `.anchor.json`); (3) Đối chiếu lại toàn bộ con số trong tài liệu với tệp JSON đầu ra thực tế (`docs/doi-chieu-so-lieu-bao-cao.md`).",
        "Toàn bộ kho mã hiện vượt qua **1.779 bài kiểm thử `pytest`** (`0` lỗi) và **43 bài kiểm thử TypeScript** (`0` lỗi kiểu `tsc --noEmit`), mọi thí nghiệm đều có lệnh chạy tái lập rõ ràng.",
    ),
]


# ==============================================================================
# XÂY DỰNG TÀI LIỆU WORD (.DOCX)
# ==============================================================================

def xuat_word():
    doc = docx.Document()

    # Cấu hình trang A4 chuẩn in ấn
    for sec in doc.sections:
        sec.page_width = Inches(8.27)
        sec.page_height = Inches(11.69)
        sec.top_margin = Inches(0.72)
        sec.bottom_margin = Inches(0.72)
        sec.left_margin = Inches(0.76)
        sec.right_margin = Inches(0.76)
        sec.different_first_page_header_footer = True

        # Header các trang nội dung
        hdr = sec.header.paragraphs[0]
        hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        rh = hdr.add_run("MEDITRACE SENTINEL · CẨM NANG KIẾN TRÚC, MÃ NGUỒN, TÍNH KHẢ THI & PHẢN BIỆN BGK AI 2026")
        rh.font.name = "Segoe UI"
        rh.font.size = Pt(8.0)
        rh.font.color.rgb = C_MUTED

        # Footer kèm số trang tự động
        ftr = sec.footer.paragraphs[0]
        ftr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        rf1 = ftr.add_run("Tài liệu giải trình kỹ thuật & bảo vệ dự án (Cập nhật 26/11/2026)   |   Trang ")
        rf1.font.name = "Segoe UI"
        rf1.font.size = Pt(8.2)
        rf1.font.color.rgb = C_MUTED
        rf_pg = ftr.add_run()
        rf_pg.font.name = "Segoe UI"
        rf_pg.font.size = Pt(8.2)
        rf_pg.font.bold = True
        rf_pg.font.color.rgb = C_NAVY
        them_so_trang_xml(rf_pg)

    # ---------------- TRANG BÌA ----------------
    tbl_banner = doc.add_table(rows=1, cols=1)
    tbl_banner.alignment = WD_TABLE_ALIGNMENT.CENTER
    cb = tbl_banner.cell(0, 0)
    cb.width = Inches(6.75)
    dat_nen_o(cb, HEX_NAVY)
    dat_vien_o(cb, top=HEX_NAVY, bottom="F59E0B", left=HEX_NAVY, right=HEX_NAVY, sz="18")
    dat_le_o(cb, top=160, bottom=160, left=180, right=180)
    pb1 = cb.paragraphs[0]
    pb1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pb1.paragraph_format.space_after = Pt(4)
    r_b1 = pb1.add_run("CUỘC THI TRÍ TUỆ NHÂN TẠO AI 2026 (AI.TAINANGVIET.VN) · HỒ SƠ CHẶNG 1\n")
    r_b1.bold = True
    r_b1.font.name = "Segoe UI"
    r_b1.font.size = Pt(9.5)
    r_b1.font.color.rgb = RGBColor(0x7D, 0xD3, 0xFC)
    r_b2 = pb1.add_run("DỰ ÁN MEDITRACE SENTINEL")
    r_b2.bold = True
    r_b2.font.name = "Segoe UI"
    r_b2.font.size = Pt(16)
    r_b2.font.color.rgb = C_WHITE

    them_doan(
        doc,
        "CẨM NANG GIẢI THÍCH CẤU TRÚC HỆ THỐNG,\nBẢN ĐỒ MÃ NGUỒN, TÍNH KHẢ THI & PHẢN BIỆN BAN GIÁM KHẢO",
        co_chu=18.5, mau=C_NAVY, can_le=WD_ALIGN_PARAGRAPH.CENTER, cach_tren=16, cach_duoi=6, gian_dong=1.22,
    ).runs[0].bold = True

    p_sub = them_doan(
        doc,
        "Giải thích rõ từng tầng xử lý · Chỉ tận nơi tệp code & hàm thực thi · Phân tích khả thi triển khai phòng khám Việt Nam · 22 câu hỏi & trả lời bảo vệ trước Hội đồng Giám khảo",
        co_chu=10.2, mau=C_MUTED, can_le=WD_ALIGN_PARAGRAPH.CENTER, cach_tren=0, cach_duoi=14,
    )
    p_sub.runs[0].italic = True

    # Lưới 6 ô chỉ số thực nghiệm cốt lõi (3x2)
    kpis = [
        ("KIỂM THỬ TỰ ĐỘNG", "1.779 + 43 PASS", "1.779 bài pytest Python + 43 bài test TypeScript vượt qua 100% (0 lỗi)", HEX_SAFE, HEX_BG_TEAL),
        ("GIẢM TỶ LỆ BỎ SÓT", "43,1% → 11,5%", "Đo trên 30 ca phát triển ngoài khuôn (304 mệnh đề, 0 ca lỗi JSON)", HEX_BLUE, HEX_BG_BLUE),
        ("BỘ DỮ LIỆU ĐỘC LẬP V2", "657 KHUÔN BỆNH", "21 hệ cơ quan · 515 Train / 72 Dev / 70 Test · 0 khuôn giao nhau (Jaccard 5,87%)", HEX_TEAL, HEX_BG_TEAL),
        ("LỚP CẢNH BÁO LỖI", "13 NHÓM · 56 MÃ", "Độ nhạy cấy lỗi cơ bản giữ nguyên 0,871 trên 240 ca giữ kín; lỗi khó 0,889", HEX_AMBER, HEX_BG_AMBER),
        ("TRUY VẾT HAI CHIỀU", "LƯỢT NÓI & ÂM GỐC", "Mọi dòng nối về lượt [T_i] và phát lại đúng đoạn ghi âm gốc ±0,5 giây", HEX_NAVY, HEX_BG_SOFT),
        ("CHỐT KÝ DUYỆT PHÁP LÝ", "CHẶN THIẾU CĂN CỨ", "Khóa cứng khi còn mục Cần xác nhận + Chuỗi băm WORM SHA-256 & .anchor.json", HEX_DANGER, HEX_BG_ROSE),
    ]
    tbl_kpi = doc.add_table(rows=3, cols=2)
    tbl_kpi.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (lbl, val, desc, hex_b, hex_bg) in enumerate(kpis):
        cell = tbl_kpi.cell(idx // 2, idx % 2)
        cell.width = Inches(3.32)
        dat_nen_o(cell, hex_bg)
        dat_vien_o(cell, top="CBD5E1", bottom="CBD5E1", left=hex_b, right="CBD5E1", sz="16")
        dat_le_o(cell, top=80, bottom=80, left=120, right=110)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        rl = p.add_run(lbl + "\n")
        rl.bold = True
        rl.font.name = "Segoe UI"
        rl.font.size = Pt(8.2)
        rl.font.color.rgb = C_MUTED
        rv = p.add_run(val + "\n")
        rv.bold = True
        rv.font.name = "Segoe UI"
        rv.font.size = Pt(12.5)
        rv.font.color.rgb = C_NAVY if hex_b != HEX_DANGER else C_DANGER
        rd = p.add_run(desc)
        rd.font.name = "Segoe UI"
        rd.font.size = Pt(8.4)
        rd.font.color.rgb = C_DARK

    them_doan(doc, "", cach_tren=4, cach_duoi=4)

    # Bảng thông tin định danh dự án & 3 liên kết nộp bài Chặng 1
    them_bang(
        doc,
        ["Hạng mục hồ sơ", "Thông tin chi tiết & Đường dẫn đối chứng (Cập nhật 26/11/2026)"],
        [
            ["Định vị sản phẩm", "**Phần mềm dựng bản nháp hồ sơ khám bệnh từ lời nói buổi khám tiếng Việt**, mỗi dòng đều chỉ ra câu nói và đoạn ghi âm làm căn cứ (không tự chẩn đoán, không tự kê đơn)."],
            ["Liên kết 1 · Mã nguồn", "`https://github.com/quannguyen991/meditrace-sentinel`"],
            ["Liên kết 2 · Chạy thử", "`https://meditrace-sentinel.vercel.app` *(Bấm nút 'Xem thử với ca mẫu' để mở ngay 3 ca đa người nói không cần GPU)*"],
            ["Liên kết 3 · Báo cáo cải tiến", "`https://github.com/quannguyen991/meditrace-sentinel/blob/main/BAO_CAO_CAI_TIEN_CHANG_1.md`"],
            ["Cấu trúc tài liệu này", "**Phần 1:** Giải thích kiến trúc & luồng chạy · **Phần 2:** Bản đồ code nằm ở đâu · **Phần 3:** Tính khả thi thực tế · **Phần 4:** 22 câu hỏi & trả lời BGK."],
        ],
        [1.85, 4.90],
    )

    doc.add_page_break()

    # ---------------- PHẦN 1: GIẢI THÍCH TỔNG THỂ CẤU TRÚC & LUỒNG HỆ THỐNG ----------------
    them_phan_lon(
        doc,
        "PHẦN 1",
        "Giải thích cấu trúc tổng thể & luồng chạy hệ thống",
        "Cách trình bày ngắn gọn, rõ bản chất trong 2 phút đầu trước Ban Giám khảo",
    )

    them_muc_con(doc, "1.1. Bài toán cốt lõi: Vì sao văn bản AI viết trôi chảy lại nguy hiểm trong phòng khám?")
    them_doan(
        doc,
        "Nếu đưa bản ghi âm hoặc lời thoại khám bệnh cho một mô hình ngôn ngữ lớn (như ChatGPT, Gemini hay một LLM viết thẳng đầu-cuối), mô hình sẽ viết ra một bệnh án đọc rất mượt. Tuy nhiên, trong khám bệnh tiếng Việt thường xuyên xảy ra **4 bẫy ngôn ngữ thực tế** khiến bản văn trôi chảy bị sai nghiêm trọng về mặt y khoa:",
    )
    them_gach_dau_dong(doc, "**Bẫy 1 — Ghi nhầm người (Sai chủ thể):** Người con đi cùng nói *'Bố em bị hen từ nhỏ'* hoặc người mẹ nói *'Bản thân tôi dị ứng Penicillin'*, mô hình viết gộp thành *'Bệnh nhân có tiền sử hen / dị ứng Penicillin'*.")
    them_gach_dau_dong(doc, "**Bẫy 2 — Giữ thông tin đã bị sửa (Sai đính chính):** Người bệnh nói *'Tôi ho chừng một tuần… à không, mười ngày rồi'*, bản tóm tắt vẫn giữ nguyên *'ho một tuần'* hoặc giữ cả hai số mâu thuẫn.")
    them_gach_dau_dong(doc, "**Bẫy 3 — Biến lời dặn / câu hỏi thành việc đã xảy ra:** Bác sĩ dặn *'Nếu đêm nay sốt trên 39 độ thì vào viện'* hoặc hỏi *'Có dị ứng thuốc không?'* (chưa ai đáp), mô hình biến thành *'Đã nhập viện'* hoặc *'Không dị ứng thuốc'*.")
    them_gach_dau_dong(doc, "**Bẫy 4 — Tiếng Việt lược chủ ngữ & đại từ họ hàng đa nghĩa:** Câu *'Đêm qua nôn hai lần'* không có chủ ngữ; chữ *'cháu', 'con', 'em'* vừa để tự xưng vừa để gọi người thứ ba.")

    them_hop_diem_nhan(
        doc,
        "ĐIỂM ĐỘT PHÁ KIẾN TRÚC CẦN NHẤN MẠNH VỚI BAN GIÁM KHẢO",
        [
            "• **Chỉ duy nhất Bước 1 dùng mô hình AI (`Qwen3-4B` chạy ngay trên máy)** để đọc lời thoại và liệt kê từng mảnh thông tin nguyên tử (`PhatBieu`) kèm câu trích nguyên văn.",
            "• **Toàn bộ các bước còn lại (Gom người -> Cập nhật đính chính -> Khóa căn cứ K1–K6 -> Cảnh báo 56 mã -> Ghép bản nháp SOAP) đều là mã luật cố định mà con người đọc và kiểm thử được.**",
            "• **Không bao giờ xoá ngầm thông tin chưa chắc:** Mọi chi tiết nghi ngờ (dị ứng, thuốc, chủ thể mơ hồ) đều được giữ lại ở mục riêng **`CẦN XÁC NHẬN`** kèm lý do, và hệ thống **khóa cứng không cho ký duyệt hoàn tất hồ sơ** cho tới khi bác sĩ trực tiếp xử lý hết.",
        ],
        mau_vien=HEX_TEAL,
        mau_nen=HEX_BG_TEAL,
    )

    # Chèn ảnh sơ đồ luồng nếu tồn tại trên đĩa
    hinh_flow = THUMUC_HINH / "flow-1-tong-the-5-tang-guardrails.png"
    if hinh_flow.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        p_img.add_run().add_picture(str(hinh_flow), width=Inches(6.5))
        p_cap = them_doan(
            doc,
            "Hình 1. Sơ đồ tổng thể đường ống tách bước Neuro-Symbolic và các chốt kiểm soát của MediTrace Sentinel.",
            co_chu=8.8, mau=C_MUTED, can_le=WD_ALIGN_PARAGRAPH.CENTER, cach_tren=0, cach_duoi=8,
        )
        p_cap.runs[0].italic = True

    them_muc_con(doc, "1.2. Ba khối kiến trúc phần mềm khi triển khai thực tế")
    them_gach_dau_dong(doc, "**Khối 1 — Lõi xử lý Y khoa & AI bằng Python (`src/`, cổng nội bộ `127.0.0.1:8765`):** Chứa đường ống âm thanh `PhoWhisper`, mô hình trích xuất `Qwen3-4B` QLoRA, liên kết thực thể, máy trạng thái đính chính, khóa căn cứ K1–K6, lớp cảnh báo 13 nhóm, bộ ghép bản nháp SOAP, dược lý Aho-Corasick, tiền kiểm BHYT/ICD-10 và xuất HL7 FHIR R4.")
    them_gach_dau_dong(doc, "**Khối 2 — Máy chủ Trung gian BFF, Hàng đợi & Sổ cái WORM bằng Node.js/Express (`web/server.ts`, `web/may-chu/`):** Xác thực bác sĩ bằng `scrypt` + mã mời 1 lần, bảo vệ CSRF không wildcard, lưu trữ ca khám tách biệt từng bác sĩ trong `node:sqlite` (có khóa đồng bộ lạc quan `409`), xếp hàng tạo bản nháp nền bền bỉ (`hang-doi.ts`), điều phối Trợ lý đa tác tử ẩn danh (`tro-ly/`) và ghi sổ cái ký duyệt bất biến `worm_signoff` kèm tệp neo `.anchor.json`.")
    them_gach_dau_dong(doc, "**Khối 3 — Không gian làm việc Bác sĩ bằng React 19 + TypeScript (`web/src/`):** Giao diện *Tactile Doctor* tiếng Việt gồm ghi âm trực tiếp lưu IndexedDB, gán vai người nói, soạn bệnh án song song với ngăn duyệt mệnh đề cạnh bên (`DuyetBenCanh.tsx`), màn hình dây nối căn cứ toàn màn hình (`VerificationView.tsx`), nút nghe lại đoạn âm gốc `±0,5s`, SBAR, chép nhanh HIS, tiền kiểm BHYT và tờ dặn dò người bệnh có đọc giọng nói.")

    them_muc_con(doc, "1.3. Đường đi của một ca khám qua 8 trạm (Từ lúc thu âm đến lúc ký duyệt)")
    them_bang(
        doc,
        ["Trạm xử lý", "Đầu vào", "Đầu ra", "Chốt kiểm soát an toàn", "Tệp code chính"],
        BANG_LUONG_8_TRAM,
        [1.05, 1.15, 1.55, 1.65, 1.35],
    )

    doc.add_page_break()

    # ---------------- PHẦN 2: BẢN ĐỒ MÃ NGUỒN CHI TIẾT ("ĐỂ CODE Ở ĐÂU?") ----------------
    them_phan_lon(
        doc,
        "PHẦN 2",
        "Bản đồ mã nguồn chi tiết — Chức năng này để code ở đâu?",
        "Tra cứu nhanh tệp nguồn, hàm/lớp xử lý và cơ chế bên trong khi Ban Giám khảo hỏi sâu vào code",
    )

    them_muc_con(doc, "2.1. Tầng Lõi Python (`src/`, `tools/`, `tests/` — 1.779 bài kiểm thử pytest)")
    them_bang(
        doc,
        ["Phân hệ chức năng", "Đường dẫn tệp mã nguồn", "Lớp / Hàm cốt lõi", "Giải thích cơ chế hoạt động trong code"],
        BAN_DO_MA_NGUON_PYTHON,
        [1.25, 1.65, 1.45, 2.40],
        mau_header=HEX_TEAL,
    )

    them_muc_con(doc, "2.2. Tầng Máy chủ Node/Express BFF & Giao diện React (`web/` — 43 bài kiểm thử TS)")
    them_bang(
        doc,
        ["Phân hệ Web / BFF", "Đường dẫn tệp mã nguồn", "Hàm / Component chính", "Giải thích cơ chế hoạt động trong code"],
        BAN_DO_MA_NGUON_WEB,
        [1.25, 1.65, 1.45, 2.40],
        mau_header=HEX_NAVY,
    )

    them_muc_con(doc, "2.3. Hợp đồng dữ liệu xuyên suốt 2 đầu Python ↔ TypeScript (Tránh lệch trường ngầm)")
    them_doan(
        doc,
        "Để tránh lỗi phía Python đổi tên trường JSON làm giao diện React bị trắng trang hoặc rơi mất cảnh báo, hai đầu hệ thống dùng chung hợp đồng kiểu tường minh tại `src/api_contract.py` và `web/src/types/api-contract.ts`, được biên dịch qua hàm `menhDeChoGiaoDien()` trong `web/may-chu/routes/asr.ts` (truyền đầy đủ `id`, `text`, `section`, `status`, `gateReason`, `subject`, `chu_the_id`, `negated`, `certainty`, `evidenceTurns`, `quotes`, `warning`, `stateD`, `wormSeq`, `wormHash`) và bọc bởi 3 lớp `ErrorBoundary.tsx` trên giao diện.",
    )

    doc.add_page_break()

    # ---------------- PHẦN 3: PHÂN TÍCH TÍNH KHẢ THI THỰC TẾ ----------------
    them_phan_lon(
        doc,
        "PHẦN 3",
        "Phân tích tính khả thi thực tế khi triển khai tại Việt Nam",
        "Đánh giá toàn diện 6 chiều: Phần cứng · Quy trình khám đông · Liên thông HIS · Pháp lý · Chi phí · Lộ trình",
    )

    them_doan(
        doc,
        "Một câu hỏi chắc chắn Hội đồng Giám khảo sẽ đặt ra là: **'Hệ thống chạy tốt trong phòng thí nghiệm nhưng đem ra phòng khám ngoại trú Việt Nam khám 60–80 bệnh nhân/ngày, máy tính cấu hình vừa phải, mạng chập chờn và quy định bảo mật gắt gao thì có sống được không?'** Bảng dưới đây cung cấp câu trả lời định lượng cho từng khía cạnh:",
    )

    them_bang(
        doc,
        ["Khía cạnh khả thi", "Giải pháp thiết kế trong MediTrace Sentinel & Số liệu thực tế"],
        BANG_KHA_THI,
        [1.65, 5.10],
    )

    them_hop_diem_nhan(
        doc,
        "TÓM TẮT KỊCH BẢN VẬN HÀNH 'KHÔNG ĐỨNG CHỜ GPU' TẠI PHÒNG KHÁM NGOẠI TRÚ",
        [
            "1. **08:00 – 08:04 (Khám Ca 1):** Bác sĩ bật thu âm trên MediTrace và tập trung nhìn mắt, hỏi bệnh, khám thực thể cho Bệnh nhân 1.",
            "2. **08:04 (Chuyển ca trong 3 giây):** Bác sĩ dừng thu âm, gán vai 1 chạm, bấm **Tạo bản nháp** (chạy ngầm qua `hang-doi.ts`), rồi bấm **+ Ca mới** mời ngay Bệnh nhân 2 vào khám — **không phải ngồi đợi 3,5 phút**.",
            "3. **Cuối cụm khám / Trước khi in đơn:** Bản nháp Ca 1 đã dựng xong sẵn. Bác sĩ mở Ca 1, dùng phím `J/K/Enter` duyệt 1–2 mục đỏ ở `Cần xác nhận` trong **15–30 giây**, bấm **Ký duyệt WORM**, rồi bấm **Chép HIS** dán thẳng vào VNPT-HIS / Viettel HIS và in **Tờ dặn dò** trao tay người bệnh.",
        ],
        mau_vien=HEX_AMBER,
        mau_nen=HEX_BG_AMBER,
    )

    doc.add_page_break()

    # ---------------- PHẦN 4: 22 CÂU HỎI PHẢN BIỆN BGK & KỊCH BẢN TRẢ LỜI ----------------
    them_phan_lon(
        doc,
        "PHẦN 4",
        "Bộ 22 câu hỏi Ban Giám khảo sẽ hỏi & Kịch bản trả lời chuẩn xác",
        "Mỗi câu đều theo cấu trúc 3 nhịp: (1) Trả lời trực diện -> (2) Cơ chế & vị trí code -> (3) Số liệu thật đối chứng",
    )

    nhom_hien_tai = ""
    tieu_de_nhom_map = {
        1: "NHÓM A · CÂU HỎI XOÁY TRỰC DIỆN VÀO 3 YÊU CẦU CẢI TIẾN CHẶNG 1 AI 2026 (CÂU 01 – 06)",
        7: "NHÓM B · CÂU HỎI VỀ KIẾN TRÚC KỸ THUẬT, MÔ HÌNH AI & MÃ NGUỒN (CÂU 07 – 12)",
        13: "NHÓM C · CÂU HỎI VỀ NGÔN NGỮ TIẾNG VIỆT, ÂM THANH ASR, DƯỢC LÝ & BHYT (CÂU 13 – 16)",
        17: "NHÓM D · CÂU HỎI VỀ TÍNH KHẢ THI, ĐỘ TRỄ, TÍCH HỢP HIS & PHÁP LÝ (CÂU 17 – 20)",
        21: "NHÓM E · CÂU HỎI KIỂM TRA ĐỘ TRUNG THỰC KHOA HỌC & SỬ DỤNG AI (CÂU 21 – 22)",
    }

    for so, muc_do, nhom, q, a1, a2, a3 in BO_22_CAU_HOI_BGK:
        if so in tieu_de_nhom_map and tieu_de_nhom_map[so] != nhom_hien_tai:
            nhom_hien_tai = tieu_de_nhom_map[so]
            them_muc_con(doc, nhom_hien_tai)
        them_the_qna(doc, so, muc_do, nhom, q, a1, a2, a3)

    # Lưu ra cả 3 vị trí tiện dụng
    FILE_DOCX_DOCS.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(FILE_DOCX_DOCS))
    doc.save(str(FILE_DOCX_GOC))
    da_luu_desktop = False
    if FILE_DOCX_DESKTOP.parent.exists():
        try:
            doc.save(str(FILE_DOCX_DESKTOP))
            da_luu_desktop = True
        except Exception as exc:
            print(f"[canh-bao] Khong ghi duoc ban Desktop ({exc}), da giu ban tai kho va docs/tai-lieu/")
    return da_luu_desktop


# ==============================================================================
# XUẤT BẢN MARKDOWN ĐỒNG BỘ (.MD) ĐỂ ĐỌC / TÌM KIẾM NHANH TRÊN IDE
# ==============================================================================

def xuat_markdown():
    lines = [
        "# CẨM NANG GIẢI THÍCH CẤU TRÚC HỆ THỐNG, BẢN ĐỒ MÃ NGUỒN, TÍNH KHẢ THI & PHẢN BIỆN BGK (AI 2026)",
        "",
        "> **Bản Word (`.docx`) trình bày đẹp in ấn được sinh tự động cùng nội dung tại:**",
        f"> - `{FILE_DOCX_GOC.name}` (thư mục gốc dự án)",
        f"> - `docs/tai-lieu/{FILE_DOCX_DOCS.name}`",
        "",
        "---",
        "",
        "## PHẦN 1: TỔNG QUAN CẤU TRÚC & ĐƯỜNG ĐI CỦA MỘT CA KHÁM QUA 8 TRẠM",
        "",
        "- **Nguyên lý cốt lõi:** Chỉ **Bước 1** dùng mô hình AI (`Qwen3-4B` + QLoRA chạy ngay tại máy) để rút từng mệnh đề nguyên tử kèm câu trích nguyên văn. Toàn bộ **Bước 2 đến Bước 5** (gom người, cập nhật đính chính FSM, khóa căn cứ K1–K6, lớp cảnh báo 13 nhóm / 56 mã, ghép bản nháp SOAP) đều là mã luật xác định mà con người đọc và viết kiểm thử được.",
        "- **Bảo toàn thông tin chưa chắc & Chốt chặn hoàn tất hồ sơ:** Không xoá ngầm thông tin nghi ngờ (dị ứng, thuốc, chủ thể mơ hồ) mà chuyển xuống mục **`CẦN XÁC NHẬN`** kèm lý do; đồng thời khóa cứng không cho ký duyệt WORM khi `0` mệnh đề hoặc còn mục `Cần xác nhận` chưa được bác sĩ xử lý.",
        "",
        "| Trạm xử lý | Đầu vào | Đầu ra | Chốt kiểm soát an toàn | Tệp code chính |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for r in BANG_LUONG_8_TRAM:
        cells = [c.replace("\n", "<br>") for c in r]
        lines.append(f"| {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} | {cells[4]} |")

    lines.extend([
        "",
        "---",
        "",
        "## PHẦN 2: BẢN ĐỒ MÃ NGUỒN CHI TIẾT (\"CHỨC NĂNG NÀY ĐỂ CODE Ở ĐÂU?\")",
        "",
        "### 2.1. Tầng Lõi Python (`src/`, `tools/`, `tests/` — 1.779 bài kiểm thử `pytest`)",
        "",
        "| Phân hệ chức năng | Đường dẫn tệp mã nguồn | Lớp / Hàm cốt lõi | Giải thích cơ chế hoạt động trong code |",
        "| :--- | :--- | :--- | :--- |",
    ])
    for r in BAN_DO_MA_NGUON_PYTHON:
        cells = [c.replace("\n", "<br>") for c in r]
        lines.append(f"| {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")

    lines.extend([
        "",
        "### 2.2. Tầng Máy chủ Node/Express BFF & Giao diện React (`web/` — 43 bài kiểm thử TypeScript)",
        "",
        "| Phân hệ Web / BFF | Đường dẫn tệp mã nguồn | Hàm / Component chính | Giải thích cơ chế hoạt động trong code |",
        "| :--- | :--- | :--- | :--- |",
    ])
    for r in BAN_DO_MA_NGUON_WEB:
        cells = [c.replace("\n", "<br>") for c in r]
        lines.append(f"| {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")

    lines.extend([
        "",
        "---",
        "",
        "## PHẦN 3: PHÂN TÍCH TÍNH KHẢ THI THỰC TẾ TẠI PHÒNG KHÁM VIỆT NAM",
        "",
        "| Khía cạnh khả thi | Giải pháp thiết kế trong MediTrace Sentinel & Số liệu thực tế |",
        "| :--- | :--- |",
    ])
    for r in BANG_KHA_THI:
        cells = [c.replace("\n", "<br>") for c in r]
        lines.append(f"| **{cells[0]}** | {cells[1]} |")

    lines.extend([
        "",
        "---",
        "",
        "## PHẦN 4: BỘ 22 CÂU HỎI PHẢN BIỆN BAN GIÁM KHẢO & KỊCH BẢN TRẢ LỜI",
        "",
    ])
    for so, muc_do, nhom, q, a1, a2, a3 in BO_22_CAU_HOI_BGK:
        lines.extend([
            f"### Câu {so:02d} [{muc_do} · {nhom}]: {q}",
            f"- **1. Trả lời trực diện:** {a1}",
            f"- **2. Cơ chế & vị trí code:** {a2}",
            f"- **3. Số liệu & minh chứng thật:** {a3}",
            "",
        ])

    FILE_MD_DOCS.parent.mkdir(parents=True, exist_ok=True)
    FILE_MD_DOCS.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    ok_desk = xuat_word()
    xuat_markdown()
    print(f"[OK] Da xuat Word (goc): {FILE_DOCX_GOC} ({FILE_DOCX_GOC.stat().st_size:,} bytes)")
    print(f"[OK] Da xuat Word (docs): {FILE_DOCX_DOCS} ({FILE_DOCX_DOCS.stat().st_size:,} bytes)")
    if ok_desk:
        print(f"[OK] Da xuat Word (Desktop): {FILE_DOCX_DESKTOP}")
    print(f"[OK] Da xuat Markdown: {FILE_MD_DOCS} ({FILE_MD_DOCS.stat().st_size:,} bytes)")
