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
                 tra_loi_ngan: str, co_che_va_code: str, so_lieu_minh_chung: str,
                 minh_chung_giai_quyet: str = ""):
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

    cac_muc = [
        ("1. Trả lời trực diện:", tra_loi_ngan),
        ("2. Cơ chế & vị trí code:", co_che_va_code),
        ("3. Số liệu & minh chứng thật:", so_lieu_minh_chung),
    ]
    if minh_chung_giai_quyet:
        cac_muc.append(("4. Minh chứng thực tế (MediTrace giải quyết thế nào?):", minh_chung_giai_quyet))

    for nhan, noi_dung in cac_muc:
        pa = c.add_paragraph()
        pa.paragraph_format.space_before = Pt(2.5 if "Minh chứng" in nhan else 2)
        pa.paragraph_format.space_after = Pt(2.5)
        pa.paragraph_format.line_spacing = 1.15
        rn = pa.add_run(nhan + " ")
        rn.bold = True
        rn.font.name = "Segoe UI"
        rn.font.size = Pt(9.4)
        rn.font.color.rgb = (
            C_BLUE if "Minh chứng" in nhan
            else (C_TEAL if "Cơ chế" in nhan else (C_AMBER if "Số liệu" in nhan else C_NAVY))
        )
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
        "`src/audio/pipeline.py`\n`src/he_thong/dich_vu_http.py` (`_chep_am`)\n`web/src/services/realAudioService.ts`",
    ],
    [
        "Trạm 1\nRút mệnh đề AI",
        "Lời thoại đã gán vai theo từng lượt `1..N`",
        "Danh sách mệnh đề JSON nguyên tử `PhatBieu` (nói về ai, phủ định, độ chắc chắn, tình huống, lượt dẫn, `trich_dan`)",
        "**Chỉ bước này dùng AI** (`Qwen3-4B` + adapter QLoRA 4-bit chạy tại chỗ); cấm viết văn xuôi tự do; ép lược đồ JSON",
        "`src/huan_luyen/chon_mo_hinh_bakeoff.py`\n`src/duong_ong/b1_cau_truc_menh_de.py` (`tu_json`)\n`src/duong_ong/chay_duong_ong.py`",
    ],
    [
        "Trạm 2\nGom thực thể & Chủ thể",
        "Danh sách `PhatBieu` + văn bản lời thoại gốc",
        "Mỗi mệnh đề gắn `chu_the_id` (`0` = bệnh nhân, `1..k` = mẹ/bố/con/người đi cùng) và `ten_chu_the`",
        "Chuẩn hóa vai nhân viên y tế (`la_vai_nhan_vien`) về bệnh nhân; tách biệt người phát ngôn với người mang bệnh",
        "`src/duong_ong/b2_gom_nguoi_thuc_the.py` (`lien_ket`)\n`src/duong_ong/b1_cau_truc_menh_de.py` (`bang_ten_tu_thuc_the`)",
    ],
    [
        "Trạm 3\nCập nhật Đính chính (FSM)",
        "Chuỗi `PhatBieu` theo trật tự thời gian lượt nói",
        "Trạng thái từng mệnh đề: `còn hiệu lực`, `bị thay thế`, hoặc `chưa giải quyết` (mâu thuẫn)",
        "Tự sửa hoặc đồng thuận chéo -> bản cũ sang `bị thay thế` (**không xoá**); hai người nói ngược nhau -> hạ về `mâu thuẫn`",
        "`src/duong_ong/b3_cap_nhat_trang_thai.py` (`ap_luat`)\n`src/duong_ong/b2_bu_chu_ngu_tinh_luoc.py`",
    ],
    [
        "Trạm 4\nKhóa căn cứ K1–K6 & Cảnh báo",
        "Mệnh đề sau FSM + toàn bộ lượt thoại gốc + cơ địa bệnh nhân",
        "Kết quả khóa `KetQua`, điểm rủi ro `DanhGia`, và danh sách `CanhBao` (13 nhóm, 56 mã lỗi, 2 trục `muc_do` × `bat_dinh`)",
        "So khớp chuỗi con nguyên văn, từ nội dung, đại từ tự xưng người kể (`chu_the_nguoi_ke`), điều kiện, thời gian, tên/liều thuốc",
        "`src/duong_ong/b4_kiem_can_cu.py`\n`src/duong_ong/b5_xep_cho_cong_rui_ro.py`\n`src/canh_bao/` (`loai.py`, `gop.py`)",
    ],
    [
        "Trạm 5\nGhép bản nháp theo khuôn",
        "Mệnh đề + danh sách bị chặn/cảnh báo `ly_do_chan`",
        "Bản nháp 9–14 mục chuẩn khám bệnh + mục riêng `CẦN XÁC NHẬN` + tối đa 3 câu hỏi làm rõ",
        "100% ghép bằng mã luật, không dùng LLM viết lại; phân biệt *'chưa ghi nhận'* với *'không có'*; không xoá ngầm thông tin nghi ngờ",
        "`src/duong_ong/b5_viet_ban_nhap.py`\n`src/duong_ong/b6_goi_y_hoi_lai.py`",
    ],
    [
        "Trạm 6\nHỗ trợ Lâm sàng & BHYT",
        "Mệnh đề hiệu lực + ngữ cảnh tuổi/giới/xét nghiệm cũ",
        "Cảnh báo tương tác thuốc DDI, liều trần, CrCl/eGFR chỉnh liều thận, 9 thang điểm, mã ICD-10 4 ký tự, XML1–XML5, HL7 FHIR R4",
        "Loại trừ bệnh của người nhà và bệnh đã phủ định khỏi ICD-10/FHIR; gắn nhãn rõ bảng tri thức thuốc `da_duyet=false`",
        "`src/he_thong/dieu_phoi_cac_chot_an_toan.py`\n`src/cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot.py`\n`src/cong_cu_lam_sang/doc_phieu_xet_nghiem.py`\n`src/cong_cu_lam_sang/xuat_fhir_r4.py`",
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
        "`src/he_thong/dich_vu_http.py`\n`src/bo_du_lieu/ca_mau_bgk.py`\n`src/he_thong/hop_dong_api.py`",
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
        "`src/huan_luyen/chon_mo_hinh_bakeoff.py`\n`src/duong_ong/b1_cau_truc_menh_de.py`\n`src/huan_luyen/huan_luyen_sft.py`\n`src/huan_luyen/loss_theo_doan.py`\n`src/huan_luyen/huan_luyen_dpo.py`",
        "`PhatBieu`, `tu_json()`, `loss_theo_doan()`, `train_dpo`",
        "Định nghĩa cấu trúc mệnh đề nguyên tử; giải mã ép lược đồ JSON cho `Qwen3-4B`; tính hàm mất mát theo từng đoạn token giúp train ngữ cảnh dài `4.096` token chỉ tốn `6,42 GiB` VRAM; huấn luyện DPO trên 1.200 cặp lỗi khó.",
    ],
    [
        "3. Gom chủ thể & Đính chính FSM",
        "`src/duong_ong/b2_gom_nguoi_thuc_the.py`\n`src/duong_ong/b3_cap_nhat_trang_thai.py`\n`src/duong_ong/b3_phan_xu_quan_he.py`\n`src/duong_ong/b2_bu_chu_ngu_tinh_luoc.py`",
        "`lien_ket()`, `ap_luat()`, `_co_dong_thuan_cheo()`, `BoGiaiQuyetProDrop`, `MayTrangThaiHoiThoai`",
        "Gom các cách xưng hô tiếng Việt (*con, cháu, mẹ, ông nhà*) về thực thể số nguyên; xử lý 4 quan hệ hội thoại (*bổ sung, đính chính, diễn biến, mâu thuẫn*) mà không bao giờ xoá mất dấu vết giá trị cũ.",
    ],
    [
        "4. Khóa căn cứ K1–K6, Cổng rủi ro & Lớp cảnh báo",
        "`src/duong_ong/b4_kiem_can_cu.py`\n`src/duong_ong/b5_xep_cho_cong_rui_ro.py`\n`src/canh_bao/loai.py`\n`src/canh_bao/gop.py`\n`src/canh_bao/than_the.py`\n`src/canh_bao/thoi_diem.py`\n`src/canh_bao/toan_ca.py`",
        "`khoa_ca()`, `cham()`, `dua_sang_xac_nhan()`, `LOAI`, `muc_do()`, `gop.chay()`",
        "Đối chiếu trực tiếp từng mệnh đề với lượt dẫn; khuếch đại rủi ro theo cơ địa (thai kỳ, sơ sinh, lão khoa, suy thận/gan, đa thuốc); phân loại 56 mã lỗi thuộc 13 nhóm (gồm cả sai bên trái/phải, sai mức độ, nhầm quá khứ/hiện tại, đính chính ngược).",
    ],
    [
        "5. Sinh bệnh án, Dược lý, XN cũ, BHYT & FHIR",
        "`src/duong_ong/b5_viet_ban_nhap.py`\n`src/cong_cu_lam_sang/tra_duoc_thu_aho_corasick.py`\n`src/cong_cu_lam_sang/canh_bao_tuong_tac_thuoc.py`\n`src/cong_cu_lam_sang/hieu_chinh_lieu.py`\n`src/cong_cu_lam_sang/doc_phieu_xet_nghiem.py`\n`src/cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot.py`\n`src/cong_cu_lam_sang/xuat_fhir_r4.py`\n`src/cong_cu_lam_sang/thang_diem_nguy_co.py`",
        "`sinh()`, `PurePythonAhoCorasick`, `boc_tach_phieu_cu()`, `BHYTXmlPreChecker`, `FHIRExporter`",
        "Ghép bản nháp từ bảng mệnh đề; quét thuốc Aho-Corasick `O(N+M+Z)` thuần Python (`Sintrom -> acenocoumarol`); quy đổi Creatinin `µmol/L ↔ mg/dL` tính CrCl/eGFR; gợi ý ICD-10 4 ký tự, xuất XML1–XML5 QĐ 130/4750 và HL7 FHIR R4 Bundle.",
    ],
    [
        "6. Bộ dữ liệu 657 khuôn & Đo kiểm độc lập",
        "`src/bo_du_lieu/kho_khuon.py`\n`src/bo_du_lieu/ngu_lieu_viet.py`\n`src/bo_du_lieu/khuon_mo_rong.py`\n`src/bo_du_lieu/bien_the_cau.py`\n`src/bo_du_lieu/sinh_hoi_thoai_viet.py`\n`src/bo_du_lieu/chia_tap_theo_khuon.py`\n`src/do_luong/do_lap_cau.py`\n`src/do_luong/do_bo_sot.py`\n`src/do_luong/do_cay_loi.py`\n`src/do_luong/kiem_nghiem_ngoai_khuon.py`\n`tools/khu_trung_tap_du_lieu.py`\n`tools/do_truyen_lan_loi_tung_tang.py`",
        "`ds_khuon()`, `phan_khuon()`, `khu_trung_train_doi_chieu_dev_test()`, `do_tung_bo()`",
        "Hợp nhất 657 khuôn ca bệnh (21 hệ cơ quan), chia tập độc lập tuyệt đối `515 Train / 72 Dev / 70 Test` (`0` khuôn giao nhau), khử trùng câu nguyên văn Train–Dev về `0,00%`, và đo truyền lan/chặn lỗi từng tầng trên 4 bộ thử thách.",
    ],
    [
        "7. MediTrace Sentinel M1–M4 (An toàn sâu, KHTH BHYT, QR & LIS HL7)",
        "`src/cong_cu_lam_sang/di_ung_cheo.py`\n`src/cong_cu_lam_sang/quy_dao_nhieu_lan_kham.py`\n`src/he_thong/dieu_phoi_cac_chot_an_toan.py`\n`src/cong_cu_lam_sang/kiem_toan_xml_bhyt.py`\n`src/cong_cu_lam_sang/ho_so_benh_nhan_qr.py`\n`src/cong_cu_lam_sang/nap_ket_qua_lis_hl7.py`",
        "`kiem_tra_di_ung_cheo()`, `phan_tich_quy_dao_lam_sang()`, `tai_kiem_tra_nhanh()`, `kiem_toan_goi_xml_bhyt()`, `phan_tich_lis_dau_vao()`",
        "Đồ thị dị ứng chéo ATC/Beta-lactam/Sulfa/NSAID; quỹ đạo KDIGO AKI & độ dốc eGFR/HbA1c/INR; tái kiểm tra vòng lặp kín `<50ms`; kiểm toán XML1–5 BHYT + TT 20/2022; cổng QR bệnh nhân theo dõi 48h/7d; bộ đọc HL7 v2 ORU^R01 / LIS.",
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
        "Gợi ý tối đa 2 câu hỏi cờ đỏ tại chỗ (0 token); nhập tuổi/giới tường minh, đọc phiếu XN cũ & nhập tệp LIS/HL7; tiền kiểm ICD-10 4 ký tự; tạo phiếu bàn giao SBAR & chép từng ô sang HIS; in tờ dặn dò A4 kèm mã QR ISO-18004 & đọc giọng nói TTS; cảnh báo mâu thuẫn với lần khám trước.",
    ],
    [
        "Trung tâm KHTH/BHYT & Cổng Bệnh nhân QR (M2–M3)",
        "`web/may-chu/routes/quan-tri-bv.ts`\n`web/may-chu/routes/benh-nhan-portal.ts`\n`web/src/components/HospitalCommandCenterView.tsx`\n`web/src/components/PatientPortalView.tsx`\n`web/src/lib/qrEncoder.ts`",
        "`taoRouterQuanTriBv()`, `taoRouterBenhNhanPortal()`, `HospitalCommandCenterView`, `PatientPortalView`",
        "Dashboard KHTH/QLCL thống kê KPI toàn viện, phân tầng kháng sinh WHO AWaRe & kiểm toán gói XML1–5; cổng bệnh nhân công khai qua mã QR (`?portal=<token>`) cho phép báo cáo dấu hiệu đỏ 48h/7d đẩy thẳng vào `TasksView`.",
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
        "Định nghĩa 13 nhóm lỗi (56 mã) tại `src/canh_bao/loai.py` (hàm `muc_do()` tự nâng bậc cho `di_ung`, `thuoc_nti`, tập `LUON_CAO`). Định tuyến tại `src/duong_ong/b5_xep_cho_cong_rui_ro.py` (`dua_sang_xac_nhan`) và `src/duong_ong/b5_viet_ban_nhap.py` (`_muc_cho`).",
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
        "Bước 0: `dich_vu.py:660` trả `409 asr_review_pending` và `App.tsx:225` chặn nếu còn lượt thiếu vai. Bước 2: `src/duong_ong/b2_gom_nguoi_thuc_the.py` gán `chu_the_id != 0` cho người nhà/người đi cùng, `sinh_benh_an.py` cấm tuyệt đối `chu_the_id != 0` vào mục của bệnh nhân. Bước 4: `khoa_bang_chung.py` bắt mẫu người nhà tự xưng *'bản thân tôi / còn tôi bị dị ứng…'* (`chu_the_nguoi_ke`) đẩy thẳng xuống `CẦN XÁC NHẬN`.",
        "Trình diễn trực tiếp bằng **Ca mẫu 2 (`demo_hai_benh_nhan`)** và **Ca mẫu 1 (`demo_bs_nguoi_nha_nhi`)** trong `src/bo_du_lieu/ca_mau_bgk.py` (bấm *'Xem thử với ca mẫu'*, không cần GPU) và kiểm thử đối kháng `tests/test_demo_bac_si_nguoi_nha.py`. Trên tập giữ kín 240 ca `thach_thuc_v2`, độ nhạy bắt lỗi `doi_chu_the` đạt **0,946** (`[0,910–0,968]`). Trên 4 tập phát triển (300 ca, 2.789 phát biểu, đối chiếu bộ chấm tự động `docs/ket-qua/canh-bao.json` & `truyen-lan-loi-tung-tang.json`), Chính sách D chặn được **88,2% (`194/220`)** lỗi nguy hiểm: giảm lỗi nguy hiểm lọt thân từ `45,9%` (C) → **11,8% (`26/220`)** (đổi lại chặn thừa tăng từ `8,0%` lên `10,0%`); theo nhóm: *đổi chủ thể* `96,5% (109/113)`, *đính chính* `84,0% (21/25)`, *nhiễu ASR* `74,6% (50/67)`, *phương ngữ* `93,3% (14/15)`.",
    ),
    (
        4, "TRỌNG TÂM", "Yêu cầu 2 BGK · Trạng thái đính chính & Mâu thuẫn",
        "Khi người bệnh nói nhầm rồi tự sửa ('4 ngày... à không, chiều hôm qua'), hoặc con gái nói một đằng bố nói một nẻo thì hệ thống cập nhật trạng thái thế nào? Có xoá thông tin cũ không?",
        "Hệ thống **không bao giờ xoá mất thông tin cũ** mà cập nhật bằng máy trạng thái theo 4 quan hệ: tự sửa (hoặc người nói trước xác nhận đồng thuận ở lượt kế tiếp) thì bản cũ chuyển sang `bị thay thế` (đưa xuống `CẦN XÁC NHẬN` để lưu vết kiểm toán), bản mới giữ `còn hiệu lực`; còn hai người nói trái nhau chưa ai xác nhận thì cả hai hạ về `chưa giải quyết` (`mâu thuẫn`) để bác sĩ hỏi lại.",
        "Xử lý tại `src/duong_ong/b3_cap_nhat_trang_thai.py` (`ap_luat`, `_co_dong_thuan_cheo`), `src/duong_ong/b2_bu_chu_ngu_tinh_luoc.py` và luật bắt đính chính ngược `src/canh_bao/toan_ca.py` (`CORRECTION_NOT_APPLIED` khi mô hình lỡ giữ con số nằm trước chữ *'à nhầm / không phải'*).",
        "Trên bộ thử thách *tự sửa*, tỷ lệ thông tin cũ đã bị đính chính vẫn còn sót trong thân bản nháp giảm hơn 14 lần: từ **11,48%** xuống còn **0,80%**. Luật `dinh_chinh_nguoc` ở vòng 6 bắt đạt **1,000** (`[0,896–1,000]`) trên tập điều chỉnh.",
    ),
    (
        5, "XOÁY SÂU / BẮT BẺ", "Yêu cầu 3 BGK · Tính độc lập bộ dữ liệu",
        "Bộ 5.000 mẫu sinh từ khuôn có nguy cơ trùng lặp ngữ nghĩa giữa tập huấn luyện và kiểm thử. Nhóm chứng minh tính độc lập và công khai cách kiểm soát mẫu tổng hợp như thế nào?",
        "Dự án đã mở rộng kho khuôn từ 200 lên **657 khuôn ca bệnh trên 21 hệ cơ quan**, ngữ cảnh hóa câu hỏi bác sĩ, và **chia tách tập theo đơn vị KHUÔN BỆNH (`benh`) theo từng đợt** — tuyệt đối không chia ngẫu nhiên theo dòng hội thoại, nên **0 khuôn bệnh nào xuất hiện ở cả Train lẫn Dev/Test**.",
        "Hợp nhất kho khuôn tại `src/bo_du_lieu/kho_khuon.py`; chia tập tất định không rò rỉ tại `src/bo_du_lieu/chia_tap_theo_khuon.py` (kiểm chứng bằng `tests/test_chia_khuon_mo_rong_khong_doi.py` giữ nguyên mã băm vàng 200 khuôn gốc); kiểm chất lượng câu tại `tools/kiem_chat_luong_cau.py`; đo ma trận trùng lặp tại `src/do_luong/kiem_nghiem_ngoai_khuon.py`; công khai danh sách tên khuôn từng tập tại `data/manifest_v2_mo_rong_5000.json`.",
        "Chia `515` khuôn Train (`3.925` ca) / `72` khuôn Dev (`551` ca) / `70` khuôn Test (`524` ca), giao tên khuôn = **`0`**. Trên `36.050` cặp khuôn Train–Test, Jaccard từ khóa triệu chứng trung bình chỉ **0,0587** (`p95 = 0,1172`, cặp ≥ 0,20 chỉ **0,17%**), Trigram Jaccard **0,0287**. Câu duy nhất tăng **+127%** (`20.190 -> 45.835`), lặp mọi câu giảm từ `76,92%` xuống **47,37%** (câu ≥ 8 từ: **42,19%**), trích dẫn khớp chuỗi con `52.634/52.634 (100%)`.",
    ),
    (
        6, "CHUYÊN SÂU", "Yêu cầu 3 BGK · Thử ngoài khuôn & ngoài nguồn",
        "Khi đem hệ thống thử trên kịch bản bệnh mới hoàn toàn ngoài kho khuôn và văn bản thực tế từ nguồn bên ngoài, kết quả ra sao và phát hiện lỗi gì?",
        "Nhóm đã thử trên 3 mức kiểm nghiệm: (1) Tập giữ lại chưa từng học (`viet_phat_trien`, `thach_thuc_v2`); (2) 10 kịch bản bệnh hiếm ngoài kho 657 khuôn (`OOT_01..10`); và (3) 5 bộ dữ liệu tiếng Việt công khai từ bên ngoài (`ViDia2Std`, `ViHealthQA`, `ViMedAQA`, `ViMQ`, `PhoNER_COVID19`). Lưu ý rõ: bảng phương ngữ có mở rộng từ tập train `ViDia2Std` rồi đo trên `ViDia2Std/test.csv`, còn các phép đo PII/Aho-Corasick trên 4 bộ kia để phát hiện lỗ hổng thực tế.",
        "Bộ đo đa nguồn tại `tools/do_da_nguon_doc_lap.py` (lưu tại `docs/ket-qua/da-nguon-doc-lap.json`); kiểm nghiệm ngoài khuôn tại `src/do_luong/kiem_nghiem_ngoai_khuon.py`; nạp `ViMQ` tại `src/bo_du_lieu/nap_vimq.py`; đối chiếu phương ngữ `ViDia2Std` tại `src/do_luong/do_vidia2std.py` và chuẩn hóa ngữ cảnh tại `src/duong_ong/b0_chuan_hoa_phuong_ngu.py` (bảo vệ chặt thuật ngữ y khoa chuẩn như `tứ chi`, `mô mềm`, `cấy ghép`, `vô kinh`, `bờ mi`).",
        "• **`ViDia2Std/test.csv` (1.603 câu phương ngữ 63 tỉnh, 4.264 chỗ thay từ):** đổi đúng chữ đạt **28,0% (`1.192/4.264`)**, thêm `392` chỗ khác chữ thành tổng phủ **37,1%**, lỗi từ giảm từ `30,1%` xuống **21,9%** (`doi_thua` chỉ `44`), vẫn giữ nguyên các cụm y khoa chuẩn.\n• **`ViHealthQA` (2.013), `ViMedAQA` (500), `ViMQ` (1.000), `PhoNER_COVID19` (1.000):** nạp `158` hoạt chất `tri_thuc_thuoc` giúp Aho-Corasick bắt thuốc trên `14/42` câu hỏi/đáp `ViHealthQA` và `87` mẫu `ViMedAQA` (nhãn `MED` của `ViMQ` khớp `9/334` vì đa số là thủ thuật/xét nghiệm). **Giới hạn thực tế phát hiện được trên `PhoNER_COVID19`:** đối chiếu với `847` nhãn vàng `NAME`/`PATIENT_ID`, `ClinicalDeidentifier` mới che được **`10/847` (`1,2%`)** do `PhoNER` viết mã bệnh nhân/tên viết tắt (*'bệnh nhân 416', 'bà H.T.P'*) không có khung SĐT/CCCD.\n• **Ngoài khuôn 657 bệnh:** `OOT_01..10` đúng chủ thể **52/52**, tập giữ kín `thach_thuc_v2` giữ độ nhạy **0,871**.",
    ),

    # --- NHÓM B: KIẾN TRÚC KỸ THUẬT, MÔ HÌNH AI & MÃ NGUỒN ---
    (
        7, "XOÁY SÂU / BẮT BẺ", "Kiến trúc Neuro-Symbolic vs Viết thẳng",
        "Tại sao không để mô hình ngôn ngữ viết thẳng bản nháp bệnh án hoặc tự đọc lại để sửa (Nhánh A+), mà phải tách thành 5 bước trung gian? Có phải cách tách bước lúc nào cũng điểm cao hơn không?",
        "**Không — và nhóm ghi rất thẳng điều này trong README:** trên dữ liệu mô phỏng, cách để mô hình viết thẳng văn xuôi thậm chí đạt điểm quy gán tự động cao hơn MediTrace ở một số bộ thử thách. Lý do chọn kiến trúc 5 bước không phải để thắng điểm văn xuôi, mà vì **văn xuôi viết thẳng là hộp đen không thể kiểm chứng từng dòng**.",
        "Đối chứng các nhánh `A`, `A+`, `B`, `C`, `C_khoa`, `C_khoa_hoi` được viết chung trong `src/duong_ong/chay_duong_ong.py` để so sánh công bằng trên cùng một đầu ra trích xuất.",
        "Ở bộ *đổi người*, mô hình viết thẳng học vẹt khuôn văn mẫu và chép giống từng chữ ở `30–63%` số ca (đạt `0,939` so với `0,748`). Nhưng khi nó ghi sai 1 dòng dị ứng trong đoạn văn trôi chảy, bác sĩ phải dò lại cả cuộc khám; còn với MediTrace (`C_khoa` nâng F₁ từ `66,1%` lên **70,8%**, giảm SER `45,4% -> 36,9%` so với chỉ trích xuất), **mọi câu trong bản nháp đều có dây nối về đúng lượt nói và giây âm thanh gốc**, và khi sai biết chính xác sai ở bước nào để sửa luật ngay.",
    ),
    (
        8, "CƠ BẢN", "Lựa chọn mô hình Qwen3-4B + DPO",
        "Vì sao dự án chọn mô hình Qwen3-4B (kèm QLoRA & DPO) cho bước rút mệnh đề mà không dùng mô hình 8B/14B hoặc gọi API đám mây?",
        "Vì 3 ràng buộc thực tế của phòng khám Việt Nam: (1) **Bảo mật pháp lý** — không gửi lời thoại khám bệnh ra máy chủ ngoài; (2) **Phần cứng vừa túi tiền** — chạy gọn trên 1 card phổ thông 8–12GB VRAM; (3) **Bản quyền mở Apache-2.0** cho phép triển khai bệnh viện hợp pháp.",
        "Cấu hình mô hình mặc định tại `src/he_thong/duong_dan.py` (`MODEL_CHINH = 'Qwen/Qwen3-4B'`, ghim bằng `tests/test_model_chinh.py` và `tests/test_dich_vu.py`). Huấn luyện QLoRA ngữ cảnh 4.096 token với `src/huan_luyen/loss_theo_doan.py` và tinh chỉnh chống lỗi khó bằng DPO tại `src/huan_luyen/huan_luyen_dpo.py`.",
        "Nhờ tính loss theo đoạn và bỏ mặt nạ chú ý 4 chiều dư thừa, đỉnh VRAM khi train chuỗi dài `3.925` token trên RTX 3060 giảm từ tràn bộ nhớ (`> 11 GiB`) xuống chỉ còn **6,421 GiB**; suy luận 4-bit NF4 chỉ chiếm `~3,5–3,8 GiB` VRAM.",
    ),
    (
        9, "CHUYÊN SÂU", "Khóa căn cứ K1–K6 vs Lớp cảnh báo",
        "Trong code vừa có `khoa_bang_chung.py` (K1–K6) vừa có gói `src/canh_bao/` (56 mã lỗi). Hai tầng này khác nhau thế nào, có bị trùng lặp thừa thãi không?",
        "Hai tầng trả lời **hai câu hỏi khác hẳn nhau**: `khoa_bang_chung` là **cổng gác cửa nhị phân** (*mệnh đề này có đủ căn cứ tối thiểu để vào thân bản nháp không?*), còn `canh_bao` là **bộ chẩn đoán chi tiết cho bác sĩ** (*nếu mệnh đề này có rủi ro sai tinh vi vượt qua cổng gác, nó sai kiểu gì và bác sĩ cần nhìn vào lượt nào?*).",
        "`src/duong_ong/b4_kiem_can_cu.py` kiểm 6 điều kiện nền tảng. Còn `src/canh_bao/` (`than_the.py`, `thoi_diem.py`, `toan_ca.py`, `lam_sang.py`) bắt những lỗi tinh vi mà câu trích vẫn nguyên văn hợp lệ — ví dụ lượt dẫn nói *'hố chậu phải'* nhưng mệnh đề ghi *'trái'* (`LATERALITY_CHANGED`), nói *'từng hút thuốc'* ghi thành *'đang hút'* (`PAST_CURRENT_CONFUSION`), hoặc bỏ sót lượt có tên thuốc (`OMITTED_MEDICATION`).",
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
        "Triển khai tại `web/may-chu/worm.ts` (`damBaoBangWorm`, `ghiSignOff`, `xacMinhChuoi`) và đối xứng ở tầng Python `src/he_thong/nhat_ky_ky_duyet_worm.py`. Trên trình duyệt, `compileEffectiveNote.ts` tính `SHA-256` chuẩn FIPS 180-4 trên cả nội dung SOAP gốc lẫn mảng quyết định `quyetDuyet/banSuaDuyet` — hễ sửa 1 chữ sau khi ký, `isSignOffStale()` đổi nút sang **`Đã sửa · Ký lại`**.",
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
        "Xử lý tại `src/duong_ong/b2_gom_nguoi_thuc_the.py`, `src/duong_ong/b4_kiem_can_cu.py` (`TU_BENH_NHAN_RO`, `TU_HO_HANG`, `SPEAKER_SUBJECT_MISMATCH`, `SUBJECT_AMBIGUOUS`) và `src/duong_ong/b2_bu_chu_ngu_tinh_luoc.py` (`BoGiaiQuyetProDrop`).",
        "Minh chứng trực tiếp ở Ca mẫu 2 (`demo_hai_benh_nhan` lượt 6: *'đêm qua còn nôn hai lần nữa'* được giữ ở `CẦN XÁC NHẬN`). **Giới hạn đã biết ghi rõ trong README:** khi mô hình trích người được nhắc tới là cụm *'bố em'* ở một số ngữ cảnh phức tạp, bước gom người vẫn còn trường hợp gộp nhầm — nhóm công khai lỗi này để tiếp tục hoàn thiện.",
    ),
    (
        14, "XOÁY SÂU / BẮT BẺ", "Tên thuốc dân gian & Zero Silent Normalization",
        "Khi bệnh nhân đọc tên thuốc trại âm kiểu dân gian ('vỉ a móc', 'ô mê', 'la-xích / pla-vích') hoặc ASR nghe không chắc, phần mềm có tự động sửa thành tên thuốc chuẩn trong đơn không?",
        "**Tuyệt đối KHÔNG tự động sửa ngầm vào mục thuốc chính thức!** Ví dụ *'a móc'* có thể là Amoxicillin đơn chất hoặc Co-amoxiclav (Augmentin/Klamentin); đoán mò là nguy cơ lâm sàng nghiêm trọng. Hệ thống bắt buộc cách ly sang **`CẦN XÁC NHẬN`** kèm gợi ý để bác sĩ hỏi/xem vỉ thuốc thật.",
        "Khóa K6 tại `src/duong_ong/b4_kiem_can_cu.py` chặn mọi tên thuốc trong mệnh đề không xuất hiện ở lượt thoại được dẫn (`chi_tiet_thuoc_khong_thay` / `MEDICATION_ENTITY_MISMATCH`). Đồng thời `src/he_thong/dieu_phoi_cac_chot_an_toan.py` và `src/he_thong/rao_chan_an_toan.py` bôi đỏ cảnh báo âm vị thuốc dân gian, tách biệt hoàn toàn với phương ngữ triệu chứng thông thường (như *'xốt'*).",
        "Trình diễn trực tiếp trong **Ca mẫu 3 (`demo_lao_khoa_con_gai` lượt 6)**: câu *'tự ra hiệu thuốc mua vỉ a móc uống'* bị khóa K6 chặn không cho `amoxicillin` vào `THUỐC ĐANG DÙNG`, đẩy thẳng xuống `CẦN XÁC NHẬN` và khóa nút ký duyệt cho tới khi bác sĩ xác nhận.",
    ),
    (
        15, "TRỌNG TÂM", "Xét nghiệm cũ, Chỉnh liều thận & BHYT ICD-10",
        "Các tính năng đọc phiếu xét nghiệm cũ, gợi ý chỉnh liều suy thận và tiền kiểm BHYT hoạt động thế nào? Bảng tri thức thuốc và mã bệnh đã được bác sĩ/dược sĩ thẩm định chưa?",
        "Các mô-đun này là **công cụ tra cứu & nhắc kiểm xung quanh bản nháp** (không tự ý sửa bản nháp): bóc chỉ số từ văn bản phiếu cũ, tự quy đổi đơn vị (`Creatinin µmol/L ↔ mg/dL`), tính độ thanh thải thận Cockcroft-Gault/eGFR theo tuổi-giới-cân nặng thật (không tự điền tuổi 50 mặc định), và gợi ý mã ICD-10 4 ký tự kèm kiểm tra cấu trúc XML1–XML5.",
        "Mã nguồn tại `src/cong_cu_lam_sang/doc_phieu_xet_nghiem.py`, `src/cong_cu_lam_sang/chuan_hoa_don_vi_xet_nghiem.py`, `src/cong_cu_lam_sang/hieu_chinh_lieu.py`, `src/cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot.py`, giao diện tại `ContextView.tsx` và `BhytPrecheckModal.tsx` (đã loại trừ bệnh đã phủ định và bệnh nền của người nhà khỏi gợi ý mã ICD-10).",
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
        "• **Cấp độ 1 (Zero-Integration — dùng ngay hôm nay):** Popover `HisSmartCopyPopover.tsx` + `web/src/lib/sbar.ts` tự động gom các mệnh đề đã duyệt (bỏ sạch các dòng bác sĩ bấm `Bỏ`, áp dụng câu đã `Sửa`) thành đúng 5 ô chuẩn của màn hình khám bệnh HIS Việt Nam để bác sĩ bấm chép 1 chạm từng ô.\n• **Cấp độ 2 (Liên thông API chuẩn Bộ Y tế):** Xuất trực tiếp gói `HL7 FHIR R4 Bundle` (`src/cong_cu_lam_sang/xuat_fhir_r4.py`) và cấu trúc bảng `XML1–XML5` theo Quyết định 130/QĐ-BYT & 4750/QĐ-BYT (`src/cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot.py`).",
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
        "Kiến trúc tách rời giao diện web nhẹ (`Vite + Express + node:sqlite` tốn `< 150 MB` RAM) và dịch vụ AI Python (`src/he_thong/dich_vu_http.py` có cờ `--tran-ram-gb`, `--nghi-sau-phut` tự nhả VRAM khi nghỉ, và `--mo-hinh-xa` chia sẻ 1 GPU qua mạng nội bộ LAN).",
        "Một máy chủ nội bộ gắn 1 card RTX 3060 12GB (chi phí phần cứng một lần khoảng `8–10 triệu VNĐ`, điện năng tăng thêm vài nghìn đồng/ngày) phục vụ được cả cụm bàn khám mà không phát sinh chi phí thuê bao API tính theo ca.",
    ),

    # --- NHÓM E: LIÊM CHÍNH KHOA HỌC & SỬ DỤNG AI LẬP TRÌNH ---
    (
        21, "XOÁY SÂU / BẮT BẺ", "Thẳng thắn về điểm yếu lớn nhất",
        "Nếu tự phê bình nghiêm khắc nhất, đâu là 3 điểm yếu lớn nhất hiện tại của MediTrace Sentinel mà nhóm chưa giải quyết xong?",
        "Nhóm công khai thẳng 3 điểm yếu lớn nhất ngay trong `README.md` và `BAO_CAO_CAI_TIEN_CHANG_1.md`, không che giấu bất kỳ số liệu bất lợi nào:",
        "1. **Chưa có dữ liệu bệnh nhân thật & nghiên cứu bác sĩ thật:** Toàn bộ 5.000 ca là hội thoại mô phỏng đều đặn hơn đời thực; dự án không tuyên bố 'giảm X% thời gian làm bệnh án ngoài đời' khi chưa đo thực nghiệm với bác sĩ.\n2. **Phát hiện bỏ sót & Khử định danh tên ngắn:** Bộ cảnh báo bỏ sót toàn ca bằng luật từ khóa mới phủ được **12,5%** ở mốc 0 (`12,0% = 24/200` trong `canh-bao.json`, precision `2,8%` — `docs/ket-qua/canh-bao-moc-0.md`); ngoài ra trên văn xuôi báo chí `PhoNER_COVID19`, `ClinicalDeidentifier` mới che được `1,2%` nhãn `NAME`/`PATIENT_ID` viết tắt/mã số ngắn.\n3. **Nhận dạng tiếng nói (ASR) với tên biệt dược ngoại lai:** Khi nói xen tên thuốc tiếng Anh trong câu tiếng Việt có nhiễu, ASR thuần rất dễ chép trại âm, nên hiện tại hệ thống phải dựa vào cơ chế cách ly sang `CẦN XÁC NHẬN` thay vì nhận diện đúng ngay 100%.",
        "Chính việc đo lường và chỉ rõ từng điểm mù này (kèm sổ đăng ký trước `docs/dang-ky-truoc-bo-luat.md` và kiểm toán số liệu `docs/doi-chieu-so-lieu-bao-cao.md`) giúp dự án đi đúng hướng khoa học thay vì báo cáo các con số '100% hoàn hảo' ảo.",
    ),
    (
        22, "CƠ BẢN", "Khai báo sử dụng AI hỗ trợ lập trình & Kiểm chứng",
        "Nhóm đã sử dụng các công cụ AI hỗ trợ lập trình (Claude Code, Antigravity, Codex) như thế nào và làm sao đảm bảo mã nguồn do AI hỗ trợ không có lỗ hổng an toàn y khoa?",
        "Nhóm khai báo minh bạch trong `README.md`: phần lớn mã nguồn được viết với sự hỗ trợ của trợ lý lập trình AI **dưới sự chỉ đạo kiến trúc, đặt bất biến an toàn và kiểm tra chéo nghiêm ngặt của tác giả**.",
        "Quy trình kiểm soát gồm 3 vòng: (1) Mọi quy tắc lâm sàng đều phải có phép thử đơn vị trượt trước – qua sau (`pytest` và `tsx --test`); (2) Thực hiện các đợt **rà soát độc lập chéo** (như đợt rà soát 25/11 tìm và vá 9 lỗi che dị ứng/phủ định trong `tests/test_ra_soat_cuoi.py`, và đợt kiểm toán kiến trúc toàn diện sửa các lỗi khử định danh, FHIR, BHYT, đơn vị liều `kiem-dinh-so.ts`, khóa WORM `.anchor.json`); (3) Đối chiếu lại toàn bộ con số trong tài liệu với tệp JSON đầu ra thực tế (`docs/doi-chieu-so-lieu-bao-cao.md`).",
        "Toàn bộ kho mã hiện vượt qua **1.970 bài kiểm thử `pytest`** (`0` lỗi) và **96 bài kiểm thử TypeScript** (`0` lỗi kiểu `tsc --noEmit`), mọi thí nghiệm đều có lệnh chạy tái lập rõ ràng.",
    ),

    # --- NHÓM F: MEDITRACE BOOST — CHỐNG BURNOUT BÁC SĨ & BỆNH VIỆN VN (CÂU 23 - 28) ---
    (
        23, "TRỌNG TÂM", "Chống Burnout & Tối ưu tốc độ phòng khám 50–80 ca/ngày",
        "Ngoài việc nghe – chép bệnh án, các bác sĩ phòng khám đông còn mất rất nhiều thời gian cho việc gán vai người nói thủ công, chờ GPU, gõ khám thực thể khi đeo găng và duyệt từng dòng. MediTrace Boost giải quyết thế nào?",
        "MediTrace Boost giải phóng 4 nút thắt thao tác ngay tại bàn khám: **(1) Gán vai 1 chạm + Mẫu giọng Bác sĩ 5s** (`suggested_role` + phím `1/2/3`), **(2) Tăng tốc Qwen3-4B** bằng khóa VRAM GPU 0 + `prompt_lookup_num_tokens=5`, **(3) Đọc khám thực thể rảnh tay phím `F2`** bằng `PhoWhisper` nội bộ, và **(4) Triage bàn phím `J/K/Enter/E/Space`** kèm nút *Giữ nhanh N mệnh đề xanh*.",
        "Triển khai tại `src/audio/pipeline.py` (`goi_y_vai_nguoi_noi`, `trich_dac_trung_giong_nhe`), `src/huan_luyen/chon_mo_hinh_bakeoff.py` (`device_map={'': 0}`, `prompt_lookup_num_tokens`), `web/src/components/TranscriptView.tsx`, `DuyetBenCanh.tsx` và `NoteEditorView.tsx`.",
        "Nút *Giữ nhanh* vẫn **khóa cứng không cho duyệt hàng loạt** các mục `Cần xác nhận`, `Dị ứng` và `Thuốc`; đồng thời `taiBienDichHieuLuc.ts` tái biên dịch sạch mọi quyết định `Giữ / Sửa / Bỏ` sang HL7 FHIR R4 và BHYT XML1–XML5.",
    ),
    (
        24, "XOÁY SÂU / BẮT BẺ", "Lá chắn BHYT XML3/XML4 ↔ XML5 & Liều Nhi khoa TT 26/2025",
        "Ở bệnh viện Việt Nam, bác sĩ rất sợ bị BHXH xuất toán các chỉ định cận lâm sàng đắt tiền (MRI, CT, Nội soi, Troponin) vì thiếu câu biện luận trong diễn biến, hoặc kê đơn trẻ em thiếu cân nặng. Hệ thống xử lý ra sao?",
        "Hệ thống mở rộng từ kiểm tra `Thuốc ↔ ICD-10` sang **Lá chắn Biện luận Chỉ định CLS (`XML3/XML4 ↔ XML5`)** gồm 13 quy tắc đối chiếu chỉ định cận lâm sàng với triệu chứng còn hiệu lực của bệnh nhân, tự dựng câu biện luận có nguồn `[T_i]` hoặc cảnh báo đỏ nguy cơ xuất toán trước khi ký.",
        "Mã nguồn tại `src/cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot.py` (`QUY_TAC_CHI_DINH_CLS_BHYT`, `bien_luan_chi_dinh_cls`, kiểm tra cân nặng bắt buộc trẻ `< 72 tháng` theo **TT 26/2025/TT-BYT**), chuyển tiếp `thong_tin_benh_nhan` qua `web/may-chu/routes/bhyt-ocr.ts` và tải trọn bộ `.xml` tại `BhytPrecheckModal.tsx`.",
        "Giữ nguyên nguyên tắc không tự bịa triệu chứng: nếu thiếu căn cứ triệu chứng trong hội thoại, hệ thống báo đỏ và gợi ý bác sĩ bổ sung hoặc hỏi lại thay vì tự viết câu biện luận giả.",
    ),
    (
        25, "TRỌNG TÂM", "Đối soát đa đơn thuốc người cao tuổi & Đơn thuốc Quốc gia TT 26/2025",
        "Bệnh nhân cao tuổi thường mang túi thuốc từ 2–3 phòng khám khác nhau gây trùng hoạt chất khác biệt dược (như Panadol + Hapacol). MediTrace xử lý thế nào và có hỗ trợ chuẩn Đơn thuốc Điện tử Quốc gia không?",
        "MediTrace tách rạch ròi **Bảng 1 — Thuốc đang dùng ở nhà** (tự động bật sáng tương tác DDI, trùng nhóm ATC, trùng hoạt chất và gánh nặng kháng cholinergic ACB với 3 nút *Tiếp tục / Đổi liều / Tạm ngưng*) và **Bảng 2 — Nháp Đơn thuốc Mới chuẩn TT 26/2025/TT-BYT**.",
        "Logic tại `src/cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot.py` (`doi_soat_da_don_va_don_quoc_gia`), giao diện 2 bảng tại `web/src/components/BangDoiSoatThuocVaDonQuocGiaModal.tsx` và dải cảnh báo `BangDongCoLamSangThucTinh.tsx`.",
        "Số ngày dùng, tổng số lượng chỉ tự tính khi liều và số ngày đều tường minh trong hội thoại; mọi ô thiếu giữ nguyên `[cần bổ sung]` tô vàng nét đứt để bác sĩ tự điền.",
    ),
    (
        26, "TRỌNG TÂM", "8 biểu mẫu pháp lý chạy 100% Offline & Chuỗi dán HIS liên hoàn",
        "Khi bệnh viện tắt công tắc mô hình ngoài (100% offline), bác sĩ vẫn phải làm Giấy chuyển cơ sở KCB (TT 01/2025), Giấy nghỉ BHXH (TT 25/2025), Tóm tắt HSBA & Hội chẩn (TT 32/2023). Phần mềm có bị khóa sạch các mẫu đó không?",
        "**Không còn bị khóa!** Nhờ **Bộ biên dịch biểu mẫu pháp lý xác định 100% tại chỗ**, bác sĩ có thể tạo ngay **8 biểu mẫu pháp lý & bệnh án chuyên khoa (Nhi / Sản / Cấp cứu)** trong `< 10 ms` ngay cả khi tắt hoàn toàn internet và mô hình ngoài.",
        "Triển khai tại `web/src/lib/bieuMauPhapLyOffline.ts` (`bienDichBieuMauPhapLyTaiCho`), `mauVanBan.ts`, `TaoVanBanModal.tsx`, kèm **Chuỗi dán HIS liên hoàn (`Alt+N`)** trong `HisSmartCopyPopover.tsx` giúp dán tuần tự sang VNPT-HIS / Viettel HIS.",
        "Biểu mẫu tự động kiểm tra trần 30 ngày nghỉ BHXH ngoại trú (TT 25/2025), phân cấp 3 tuyến kỹ thuật (TT 01/2025), tách biệt tiền sử gia đình và giữ nguyên mỏ neo `[T_i]` + chỗ trống `[cần bổ sung]`.",
    ),
    (
        27, "CƠ BẢN", "Cam đoan Thủ thuật WORM (Luật KCB 2023) & Đi buồng Nội trú",
        "MediTrace có giúp bác sĩ tránh rủi ro pháp lý khi tư vấn thủ thuật xâm lấn, và có dùng được cho khoa điều trị nội trú đi buồng 20 giường mỗi sáng không?",
        "Có hai phân hệ chuyên biệt: **(1) Kiểm chứng 6 trụ cột Cam đoan Thủ thuật** theo Điều 10 & 63 Luật KCB 2023 (kèm mỏ neo âm thanh + băm SHA-256 WORM, chặn bác sĩ tự nói đồng ý thay người bệnh) và **(2) Chế độ Đi buồng Nội trú** tự so sánh diễn biến hôm nay với hôm qua dựng *Tờ điều trị TT 32/2023* + *Sổ bàn giao trực SBAR*.",
        "Backend Python tại `src/cong_cu_lam_sang/cam_doan_thu_thuat.py` và `src/cong_cu_lam_sang/di_buong_noi_tru.py`; BFF tại `web/may-chu/routes/boost-lam-sang.ts`; giao diện tại `CamDoanThuThuatModal.tsx` và `DiBuongNoiTruModal.tsx`.",
        "Mọi mục giải thích thiếu (như quên nói nguy cơ phản vệ hoặc phương án thay thế) đều bật cảnh báo vàng trước khi bác sĩ in *Phiếu cam đoan PTTT*.",
    ),
    (
        28, "TRỌNG TÂM", "Khép kín vòng lặp hậu khám SQLite & Từ điển thuốc viện cho PhoWhisper",
        "Dữ liệu bệnh nhân và đầu việc hẹn đọc lại xét nghiệm có lưu thật vào cơ sở dữ liệu không? Và bệnh viện có thể nạp danh mục thuốc trúng thầu BHYT riêng vào bộ nhận dạng giọng nói không?",
        "**Có.** Danh mục `benh-nhan` và `nhiem-vu` đã được migrate bảng `muc_kho` trong SQLite để lưu bền vững và tự trích đầu việc từ các ca khám; đồng thời cây `ContextualPrefixTrie600` đã gắn vào `PhoWhisperProvider` và cho phép nạp file `.csv` thuốc trúng thầu của từng bệnh viện.",
        "SQLite migration `damBaoKhoMoRong` tại `web/may-chu/csdl.ts` & `schema.sql`; tự gom bệnh nhân/nhiệm vụ tại `PatientsView.tsx` & `TasksView.tsx`; nạp CSV tại `src/audio/asr/contextual_trie_600.py` (`nap_danh_muc_trung_thau_csv`, `quet_goi_y_sua_am_vi`) và `phowhisper_provider.py`.",
        "Gợi ý âm vị thuốc trên `PhoWhisper` chỉ đính kèm thẻ gợi ý để bác sĩ đối chiếu chứ **tuyệt đối không tự sửa đè văn bản gỡ băng gốc**.",
    ),
]


MINH_CHUNG_GIAI_QUYET = {
    1: "Ví dụ thực tế: khi người nhà nói *'Hình như hồi nhỏ cháu có nổi mẩn khi uống Penicillin nhưng em không chắc'* → K4/Cổng rủi ro bắt thông tin có độ bất định cao + nhóm `di_ung` (trọng số `1.0`), KHÔNG xoá bỏ mà giữ nguyên sang mục **`CẦN XÁC NHẬN`** kèm lý do. Bác sĩ mở ngăn `DuyetBenCanh.tsx` bấm `Space` nghe lại đoạn ghi âm gốc để quyết định `Xác nhận` hay `Bỏ`.",
    2: "Thử ngay trên giao diện hoặc qua `pytest`/`tsx`: nếu Ca có 1 mục đỏ `Cần xác nhận` chưa bấm `Giữ/Sửa/Bỏ`, nút `Ký duyệt` hiện màu vàng `Cần xác nhận (1)`. Bấm vào sẽ chặn ký, mở ngăn duyệt và cuộn đúng tới thẻ đó; nếu gửi request giả trực tiếp lên `POST /api/sessions/:id/sign-off`, máy chủ trả `HTTP 400` (`worm.ts:233`).",
    3: "Mở **Ca mẫu 1 (`demo_bs_nguoi_nha_nhi`)**: người mẹ nói *'bản thân tôi bị dị ứng Penicillin'* (lượt 4) và *'bé bị sốt 39 độ'* (lượt 2) → MediTrace tách rõ `Sốt 39°C` vào thân bệnh án của bé (`chu_the_id=0`), còn `Dị ứng Penicillin` của mẹ sang `TIỀN SỬ GIA ĐÌNH` / `CẦN XÁC NHẬN` (`chu_the_id=1`). Mở **Ca mẫu 2 (`demo_hai_benh_nhan`)**: câu *'ông bị tăng huyết áp'* và *'tôi bị loét dạ dày'* được tách rạch ròi 2 chủ thể.",
    4: "Ví dụ Ca đối chứng tự sửa: lượt 2 bệnh nhân nói *'tôi ho khoảng 4 ngày nay'*, lượt 5 tự sửa *'à không, tính ra mới từ chiều hôm qua thôi'* → `cap_nhat.ap_luat()` giữ mệnh đề *'ho từ chiều hôm qua [T5]'* ở thân bệnh án, đồng thời chuyển mệnh đề cũ *'ho 4 ngày [T2]'* sang trạng thái `bị thay thế` ở `CẦN XÁC NHẬN` (vết kiểm toán nguyên vẹn).",
    5: "Chạy lệnh `python -m src.do_luong.kiem_nghiem_ngoai_khuon` và đọc `data/manifest_v2_mo_rong_5000.json`: toàn bộ 515 tên khuôn Train, 72 tên khuôn Dev và 70 tên khuôn Test được liệt kê tường minh, giao tập = `∅`. Kiểm thử `tests/test_chia_khuon_mo_rong_khong_doi.py` bảo đảm không rò rỉ giữa Train và Test.",
    6: "Chạy `python -m src.do_luong.kiem_nghiem_ngoai_khuon` trên 10 kịch bản bệnh hiếm ngoài kho (`OOT_01..OOT_10`) → đúng chủ thể `52/52`; chạy `python -m tools.do_da_nguon_doc_lap` (`docs/ket-qua/da-nguon-doc-lap.json`) → trên `ViDia2Std/test.csv` đổi đúng `28,0%` (`1.192/4.264`, phủ `37,1%`), WER giảm `30,1% -> 21,9%`; Aho-Corasick nhận `87` mẫu `ViMedAQA`; đồng thời chỉ rõ giới hạn `10/847` (`1,2%`) nhãn vàng `NAME`/`PATIENT_ID` trên `PhoNER` để tiếp tục cải thiện.",
    7: "Trong `NoteEditorView.tsx`, bấm vào bất kỳ câu nào trên bản nháp hoặc thẻ `[T3]` → khung thoại gốc sáng lên đúng câu nói của bệnh nhân và nút `Nghe lại` phát đúng giây ghi âm gốc. Ngược lại, một bản văn xuôi do LLM viết thẳng không thể làm được dây nối 2 chiều từng mệnh đề như vậy.",
    8: "Chạy thực tế `python -m src.he_thong.dich_vu_http --khong-mo-hinh` trên laptop không GPU hoặc chạy `Qwen3-4B` QLoRA 4-bit trên 1 card RTX 3060 12GB (chỉ tốn `~3,6 GB` VRAM). Kết hợp `prompt_lookup_num_tokens=5` (`bakeoff.py`) giúp sinh chuỗi JSON trích xuất nhanh gấp 2–3× mà không đổi phân phối mô hình.",
    9: "Ví dụ thực tế: câu *'Bệnh nhân đau hố chậu phải [T3]'* nhưng AI Tầng 1 gõ nhầm thành *'đau hố chậu trái [T3]'*. Cổng `khoa_bang_chung` thấy lượt 3 có nói 'đau hố chậu' nên cho qua, nhưng `canh_bao/than_the.py` (`LATERALITY_CHANGED`) bắt ngay sự đảo chiều `phải ↔ trái` và bôi vàng cảnh báo cho bác sĩ.",
    10: "Chạy `python -m src.do_luong.do_bo_chan_doan` hoặc `tests/test_do_quy_gan.py`: hoán đổi 2 từ `'bệnh nhân'` ↔ `'người nhà'` trên 400 hồ sơ → `ROUGE-1 = 1.0000`, trong khi `Attribution F1` của dự án tụt `0.1381`, chứng minh thước đo mới bắt được lỗi lâm sàng mà ROUGE bỏ lọt.",
    11: "Chạy `cd web && npx tsx --test may-chu/worm.test.ts`: kịch bản kiểm thử tự động thực hiện `DROP TRIGGER` rồi sửa/xoá lén bản ghi SQLite → hàm `xacMinhChuoi()` đối chiếu với `.anchor.json` phát hiện ngay `HTTP 409 WORM Violation` và từ chối ký tiếp.",
    12: "Mở ngăn **Trợ lý & Chứng cứ** bên phải trên giao diện, nhập câu hỏi có kèm tên/SĐT (VD: *'Bệnh nhân Nguyễn Văn A, 0912345678 uống thuốc gì?'*) → hệ thống chặn ngay từ phía máy chủ (`cau_hoi_co_danh_tinh`) và chỉ gửi đi các thông số ẩn danh (`tuổi, giới, mệnh đề đã lọc`), kiểm chứng qua `web/may-chu/tro-ly/an-danh.test.ts`.",
    13: "Mở **Ca mẫu 2 (`demo_hai_benh_nhan`)**: ở lượt 6 khi người vợ và người chồng cùng có triệu chứng trước đó, câu lược chủ ngữ *'đêm qua còn nôn hai lần nữa'* được `SPEAKER_SUBJECT_MISMATCH` / `SUBJECT_AMBIGUOUS` giữ ở `CẦN XÁC NHẬN` thay vì tự gán bừa cho chồng hoặc vợ.",
    14: "Mở **Ca mẫu 3 (`demo_lao_khoa_con_gai`)**: người nhà nói *'tự ra hiệu thuốc mua vỉ a móc uống'* (lượt 6). Khoá K6 phát hiện mệnh đề ghi `amoxicillin` không khớp nguyên văn chữ `'a móc'` trong thoại gốc → chặn không cho vào `THUỐC ĐANG DÙNG`, bôi đỏ ở `CẦN XÁC NHẬN` và khóa nút Ký duyệt cho tới khi bác sĩ xác nhận.",
    15: "Trong `ContextView.tsx`, dán phiếu cũ `Creatinine 180 umol/L, Kali 5.8 mmol/L`, nhập `72 tuổi, Nữ` → `ocr_lam_sang.py` tự quy đổi `180 umol/L -> 2.04 mg/dL`, tính `eGFR (CKD-EPI 2021)`, cảnh báo giảm liều `Metformin/Allopurinol` theo KDIGO và bật cảnh báo đỏ `Tăng Kali máu` nếu phối hợp `Spironolacton`.",
    16: "Trong `DuyetBenCanh.tsx` hoặc `VerificationView.tsx`, bấm nút `Nghe lại` trên thẻ mệnh đề có mỏ neo `[T4]` (hoặc nhấn phím `Space`) → `useTurnAudioPlayer` tua đúng tới `[start_s - 0.5s, end_s + 0.5s]` của đoạn âm thanh trong IndexedDB và tự dừng cuối câu.",
    17: "Chứng minh trực tiếp trong `App.tsx`: bấm `Tạo bản nháp` cho Ca A (trả về `202 Accepted` từ `hang-doi.ts`), chuyển ngay sang Ca B để thu âm và gõ tiếp — tiến độ Ca A chỉ chạy nền ở banner nhỏ; đồng thời ở `bakeoff.py` đã bật `device_map={'': 0}` + `prompt_lookup_num_tokens=5` để giảm tối đa độ trễ GPU.",
    18: "Trong `NoteEditorView.tsx`, bấm nút **`Chép HIS`** → `HisSmartCopyPopover.tsx` hiện 5 ô chuẩn HIS kèm nút **`[Chép & Chuyển ô kế →]`** (`Alt+N`) để dán liên hoàn sang VNPT-HIS/Viettel HIS; đồng thời bấm **`Tải HL7 FHIR & BHYT (.json)`** hoặc **`BHYT / ICD-10`** để tải gói chuẩn `HL7 FHIR R4` & `XML1–XML5` đã lọc bỏ mệnh đề `Bỏ`.",
    19: "Thử ngay kịch bản kiểm chứng trong `NoteEditorView.tsx`: ký duyệt WORM xong (hiện `Đã ký #1`), sau đó vào sửa 1 chữ trong bệnh án hoặc đổi 1 quyết định `Giữ -> Bỏ` → `isSignOffStale()` đổi nút ngay thành **`Đã sửa · Ký lại`** vì mã băm `SHA-256` đã lệch so với bản đã ký.",
    20: "Toàn bộ hệ thống chạy cục bộ qua `python -m src.he_thong.dich_vu_http --nghi-sau-phut 10 --tran-ram-gb 10` (tự giải phóng VRAM khi nghỉ) kết hợp `node dist/server.cjs` (`< 150 MB` RAM). Không cần thuê bao GPU đám mây hay gọi API trả phí theo ca cho luồng bệnh án chính.",
    21: "Đọc trực tiếp mục *Giới hạn & Thành thật khoa học* trong `README.md` và `docs/ket-qua/canh-bao-moc-0.md`: dự án công khai cả tỷ lệ sót (`11,5%` ở bước trích) và độ phủ từ khóa thô (`12,5%`) thay vì giấu lỗi, đồng thời bổ sung Tầng 4.5 (`ActiveOmissionRecoveryEngine`) để bác sĩ khôi phục 1 chạm ngay trên ngăn duyệt.",
    22: "Chạy trực tiếp 2 lệnh kiểm chứng độc lập trên toàn kho mã: `pytest --basetemp=D:\\temp\\pytest -q` (**1.970 passed, 25 skipped**) và `cd web; npm run lint; npm test; npm run build` (**96/96 passed, 0 lỗi TypeScript**).",
    23: "Chứng minh ở `TranscriptView.tsx` & `DuyetBenCanh.tsx`: tải băng 15 lượt không `pyannote` → bấm **`Áp dụng vai gợi ý`** 1 lần thay vì 15 lần bấm tay; nhấn `F2` đọc *'Bụng mềm, ấn đau nhẹ hố chậu phải'* → `PhoWhisper` nội bộ chép thẳng vào `KHÁM LÂM SÀNG`; nhấn `Giữ nhanh` + `J/K/Enter` duyệt xong cả ca trong 20 giây.",
    24: "Ví dụ thực tế: bác sĩ chỉ định *'Chụp MRI sọ não'* nhưng trong thoại chưa ghi triệu chứng thần kinh khu trú hay đau đầu → bấm **`BHYT / ICD-10`** (`BhytPrecheckModal.tsx`), hệ thống bật cảnh báo đỏ `[CẢNH BÁO XUẤT TOÁN CLS - XML3/XML5]` trước khi ký; nếu có triệu chứng `[T3]`, hệ thống tự dựng sẵn câu biện luận gắn `[T3]` để đưa vào XML5.",
    25: "Ví dụ bệnh nhân cao tuổi mang 2 vỏ thuốc `Panadol 500mg` và `Hapacol 500mg` cùng toa mới `Clopidogrel + Omeprazol`: mở **`Đơn thuốc TT26 / DDI`** → Bảng 1 báo đỏ trùng hoạt chất `Paracetamol` + tương tác `Clopidogrel ↔ Omeprazol` + điểm gánh nặng `ACB`; Bảng 2 tách riêng đơn mới chuẩn TT 26/2025 và chừa vàng `[cần bổ sung]` cho ô thiếu.",
    26: "Tắt hoàn toàn công tắc *'Mô hình ngoài'* rồi bấm nút **Tạo** (`TaoVanBanModal.tsx`) → cả 8 mẫu (*Phiếu chuyển cơ sở KCB TT 01/2025, Giấy nghỉ BHXH TT 25/2025, Tóm tắt HSBA TT 32/2023, Nhi/Sản/Cấp cứu*) đều mở sáng nhãn **`100% tại chỗ · Luật BYT`** và sinh văn bản trong `< 10 ms` (kiểm chứng tại `meditraceBoostLib.test.ts`).",
    27: "Mở **`Cam đoan PTTT`** trên ca có từ khoá thủ thuật: hệ thống quét băng ghi âm qua `src/cong_cu_lam_sang/cam_doan_thu_thuat.py`, tô xanh 4 mục đã giải thích kèm `[T_i]` và báo vàng 2 mục bác sĩ quên nói (*Nguy cơ phản vệ, Phương án thay thế*), chỉ cho đóng dấu WORM `consentHash` sau khi kiểm đủ. Ở **`Đi buồng / Trực`**, `di_buong_noi_tru.py` tự đối chiếu triệu chứng hôm nay với hôm qua dựng *Tờ điều trị TT 32/2023*.",
    28: "Kiểm chứng ở `boost-lam-sang.test.ts` và `test_meditrace_boost_python.py`: (1) Bảng `muc_kho` cũ được tự động migrate an toàn sang `benh-nhan` và `nhiem-vu` trong SQLite; (2) Nạp CSV danh mục thuốc trúng thầu viện qua `POST /api/formulary/upload-csv` vào `ContextualPrefixTrie600` gắn trên `PhoWhisperProvider` giúp gợi ý đúng tên thuốc viện mà không sửa đè chữ gốc.",
}


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
        rf1 = ftr.add_run("Tài liệu giải trình kỹ thuật & bảo vệ dự án (Cập nhật 27/11/2026)   |   Trang ")
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
        "Giải thích rõ từng tầng xử lý · Chỉ tận nơi tệp code & hàm thực thi · Phân tích khả thi triển khai phòng khám Việt Nam · 28 câu hỏi & trả lời bảo vệ trước Hội đồng Giám khảo (kèm 12 tính năng MediTrace Boost)",
        co_chu=10.2, mau=C_MUTED, can_le=WD_ALIGN_PARAGRAPH.CENTER, cach_tren=0, cach_duoi=14,
    )
    p_sub.runs[0].italic = True

    # Lưới 6 ô chỉ số thực nghiệm cốt lõi (3x2)
    kpis = [
        ("KIỂM THỬ TỰ ĐỘNG", "1.970 & 96 PASS", "1.970 bài pytest Python (25 skip tự chọn) + 96 bài test TypeScript & BFF (0 lỗi)", HEX_SAFE, HEX_BG_TEAL),
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
        ["Hạng mục hồ sơ", "Thông tin chi tiết & Đường dẫn đối chứng (Cập nhật 27/11/2026)"],
        [
            ["Định vị sản phẩm", "**Phần mềm dựng bản nháp hồ sơ khám bệnh từ lời nói buổi khám tiếng Việt**, mỗi dòng đều chỉ ra câu nói và đoạn ghi âm làm căn cứ (không tự chẩn đoán, không tự kê đơn)."],
            ["Liên kết 1 · Mã nguồn", "`https://github.com/quannguyen991/meditrace-sentinel`"],
            ["Liên kết 2 · Chạy thử", "`https://meditrace-sentinel.vercel.app` *(Bấm nút 'Xem thử với ca mẫu' để mở ngay 3 ca đa người nói không cần GPU)*"],
            ["Liên kết 3 · Báo cáo cải tiến", "`https://github.com/quannguyen991/meditrace-sentinel/blob/main/BAO_CAO_CAI_TIEN_CHANG_1.md`"],
            ["Cấu trúc tài liệu này", "**Phần 1:** Giải thích kiến trúc & luồng chạy · **Phần 2:** Bản đồ code nằm ở đâu · **Phần 3:** Tính khả thi thực tế · **Phần 4:** 28 câu hỏi & trả lời BGK (gồm MediTrace Boost)."],
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

    # Chèn bộ ảnh sơ đồ kiến trúc & minh họa giao diện nếu tồn tại trên đĩa
    cac_hinh = [
        ("flow-1-tong-the-5-tang-guardrails.png", "Hình 1. Sơ đồ tổng thể đường ống tách bước Neuro-Symbolic và các chốt kiểm soát của MediTrace Sentinel."),
        ("h13-audio-pipeline.png", "Hình 2. Đường ống xử lý âm thanh tại chỗ (VAD, PyAnnote, PhoWhisper & Trie 600 dược thư)."),
        ("flow-2-khoa-bang-chung-k1-k7.png", "Hình 3. Cơ chế Khóa bằng chứng K1–K7 chống ảo giác và đẩy câu nghi ngờ sang CẦN XÁC NHẬN."),
        ("flow-3-an-toan-duoc-ly-cdss.png", "Hình 4. Tầng an toàn dược lý, dị ứng chéo ATC, hiệu chỉnh liều thận CrCl/eGFR và 9 thang điểm CDSS."),
        ("flow-7-quy-trinh-bac-si-kham-va-click-to-verify.png", "Hình 5. Quy trình bác sĩ khám, kiểm chứng Click-to-Verify và ký duyệt bất biến WORM (< 60 giây)."),
        ("giao-dien-ban-lam-viec-bac-si-nut-moi.png", "Hình 6. Minh họa giao diện làm việc của bác sĩ với các công cụ hỗ trợ lâm sàng & kiểm chứng."),
    ]
    for ten_hinh, chu_thich in cac_hinh:
        p_hinh = THUMUC_HINH / ten_hinh
        if p_hinh.exists():
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(4)
            p_img.paragraph_format.space_after = Pt(2)
            p_img.add_run().add_picture(str(p_hinh), width=Inches(6.5))
            p_cap = them_doan(
                doc,
                chu_thich,
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

    them_muc_con(doc, "2.1. Tầng Lõi Python (`src/`, `tools/`, `tests/` — 1.970 bài kiểm thử pytest)")
    them_bang(
        doc,
        ["Phân hệ chức năng", "Đường dẫn tệp mã nguồn", "Lớp / Hàm cốt lõi", "Giải thích cơ chế hoạt động trong code"],
        BAN_DO_MA_NGUON_PYTHON,
        [1.25, 1.65, 1.45, 2.40],
        mau_header=HEX_TEAL,
    )

    them_muc_con(doc, "2.2. Tầng Máy chủ Node/Express BFF & Giao diện React (`web/` — 96 bài kiểm thử TS)")
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
        "Để tránh lỗi phía Python đổi tên trường JSON làm giao diện React bị trắng trang hoặc rơi mất cảnh báo, hai đầu hệ thống dùng chung hợp đồng kiểu tường minh tại `src/he_thong/hop_dong_api.py` và `web/src/types/api-contract.ts`, được biên dịch qua hàm `menhDeChoGiaoDien()` trong `web/may-chu/routes/asr.ts` (truyền đầy đủ `id`, `text`, `section`, `status`, `gateReason`, `subject`, `chu_the_id`, `negated`, `certainty`, `evidenceTurns`, `quotes`, `warning`, `stateD`, `wormSeq`, `wormHash`) và bọc bởi 3 lớp `ErrorBoundary.tsx` trên giao diện.",
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

    them_muc_con(doc, "3.1. Số liệu thực tế toàn cầu đối chứng (AMA · JAMA Network Open · WHO)")
    them_bang(
        doc,
        ["Chỉ số / Vấn đề toàn cầu", "Số liệu thực nghiệm & Tỷ lệ", "Nguồn trích dẫn & Ý nghĩa cho MediTrace"],
        [
            [
                "Tỷ lệ kiệt sức bác sĩ (Physician Burnout)",
                "**48,2%** (2023) → **43,2%** (2024) → **41,9%** (2025); Cấp cứu **49,8%**",
                "**AMA Organizational Biopsy:** Cứ 5 bác sĩ có hơn 2 người kiệt sức; áp lực giấy tờ/EHR là nguyên nhân hàng đầu.",
            ],
            [
                "Gánh nặng nhập liệu EHR & \"Pajama Time\"",
                "**~50%** ngày làm việc cho EHR (tỷ lệ **1:1–2 giờ** giấy tờ / 1 giờ khám); **21–22,5%** bác sĩ làm EHR **> 8 giờ/tuần** ngoài giờ tại nhà; nội trú **> 32%** làm ≥ 3 giờ/đêm (**OR 1,61**)",
                "**AMA Time-Motion (Sinsky et al., *Annals of Internal Medicine*) & ABFM:** Trực tiếp lý giải nhu cầu gán vai 1 chạm, `F2` đọc rảnh tay và 8 biểu mẫu Offline.",
            ],
            [
                "Hiệu quả Ambient AI Scribe thực tế",
                "Burnout giảm từ **51,9% → 38,8%** sau 30 ngày (**-13,1 điểm %**, giảm **74%** tỷ suất burnout); tiết kiệm **10–16 phút/8h** (nhóm dùng ≥ 50% ca tiết kiệm **27 phút/ca trực**)",
                "**JAMA Network Open đa trung tâm & JAMIA (Stanford / Kaiser Permanente):** Chứng minh mô hình Ambient AI Scribe giảm tải nhận thức rõ rệt khi chạy thật.",
            ],
            [
                "Chi phí & Tỷ lệ sai sót thuốc toàn cầu",
                "**42 tỷ USD/năm** (~**1%** chi tiêu y tế toàn cầu); xảy ra ở **~5%** ca nhập viện; **~50%** tổn hại y khoa liên quan thuốc có thể phòng ngừa",
                "**WHO (*Medication Without Harm*):** Khẳng định giá trị của Khóa K6, Dược lý Aho-Corasick DDI và Bảng TT 26/2025.",
            ],
            [
                "Đa thuốc ở người cao tuổi & Nước đang phát triển",
                "Sai sót/biến cố phòng ngừa được ở lão khoa lên tới **17%**; gánh nặng tàn tật (**DALYs**) ở nước thu nhập thấp/trung bình **cao gấp 2×** nước giàu",
                "**WHO Polypharmacy Technical Report:** Chứng minh tầm quan trọng của Bảng đối soát thuốc tại nhà (`duoc_ly_ddi` + ACB) khi chuyển tuyến/tái khám.",
            ],
        ],
        [1.55, 2.35, 2.85],
        mau_header=HEX_TEAL,
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

    # ---------------- PHẦN 4: 28 CÂU HỎI PHẢN BIỆN BGK & KỊCH BẢN TRẢ LỜI ----------------
    them_phan_lon(
        doc,
        "PHẦN 4",
        "Bộ 28 câu hỏi Ban Giám khảo sẽ hỏi & Kịch bản trả lời chuẩn xác",
        "Mỗi câu đều theo cấu trúc 3 nhịp: (1) Trả lời trực diện -> (2) Cơ chế & vị trí code -> (3) Số liệu thật đối chứng",
    )

    nhom_hien_tai = ""
    tieu_de_nhom_map = {
        1: "NHÓM A · CÂU HỎI XOÁY TRỰC DIỆN VÀO 3 YÊU CẦU CẢI TIẾN CHẶNG 1 AI 2026 (CÂU 01 – 06)",
        7: "NHÓM B · CÂU HỎI VỀ KIẾN TRÚC KỸ THUẬT, MÔ HÌNH AI & MÃ NGUỒN (CÂU 07 – 12)",
        13: "NHÓM C · CÂU HỎI VỀ NGÔN NGỮ TIẾNG VIỆT, ÂM THANH ASR, DƯỢC LÝ & BHYT (CÂU 13 – 16)",
        17: "NHÓM D · CÂU HỎI VỀ TÍNH KHẢ THI, ĐỘ TRỄ, TÍCH HỢP HIS & PHÁP LÝ (CÂU 17 – 20)",
        21: "NHÓM E · CÂU HỎI KIỂM TRA ĐỘ TRUNG THỰC KHOA HỌC & SỬ DỤNG AI (CÂU 21 – 22)",
        23: "NHÓM F · MEDITRACE BOOST — CHỐNG BURNOUT BÁC SĨ & TRIỂN KHAI BỆNH VIỆN VN (CÂU 23 – 28)",
    }

    for so, muc_do, nhom, q, a1, a2, a3 in BO_22_CAU_HOI_BGK:
        if so in tieu_de_nhom_map and tieu_de_nhom_map[so] != nhom_hien_tai:
            nhom_hien_tai = tieu_de_nhom_map[so]
            them_muc_con(doc, nhom_hien_tai)
        them_the_qna(doc, so, muc_do, nhom, q, a1, a2, a3, MINH_CHUNG_GIAI_QUYET.get(so, ""))

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
        "### 1.1. Sơ đồ kiến trúc & Ảnh minh họa giao diện",
        "",
        "![Hình 1. Sơ đồ tổng thể đường ống tách bước Neuro-Symbolic](hinh/flow-1-tong-the-5-tang-guardrails.png)",
        "",
        "![Hình 2. Đường ống xử lý âm thanh tại chỗ](hinh/h13-audio-pipeline.png)",
        "",
        "![Hình 3. Cơ chế Khóa bằng chứng K1–K7](hinh/flow-2-khoa-bang-chung-k1-k7.png)",
        "",
        "![Hình 4. Tầng an toàn dược lý & CDSS](hinh/flow-3-an-toan-duoc-ly-cdss.png)",
        "",
        "![Hình 5. Quy trình bác sĩ khám & Click-to-Verify](hinh/flow-7-quy-trinh-bac-si-kham-va-click-to-verify.png)",
        "",
        "![Hình 6. Giao diện làm việc của bác sĩ](hinh/giao-dien-ban-lam-viec-bac-si-nut-moi.png)",
    ])

    lines.extend([
        "",
        "---",
        "",
        "## PHẦN 2: BẢN ĐỒ MÃ NGUỒN CHI TIẾT (\"CHỨC NĂNG NÀY ĐỂ CODE Ở ĐÂU?\")",
        "",
        "### 2.1. Tầng Lõi Python (`src/`, `tools/`, `tests/` — 1.970 bài kiểm thử `pytest`)",
        "",
        "| Phân hệ chức năng | Đường dẫn tệp mã nguồn | Lớp / Hàm cốt lõi | Giải thích cơ chế hoạt động trong code |",
        "| :--- | :--- | :--- | :--- |",
    ])
    for r in BAN_DO_MA_NGUON_PYTHON:
        cells = [c.replace("\n", "<br>") for c in r]
        lines.append(f"| {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")

    lines.extend([
        "",
        "### 2.2. Tầng Máy chủ Node/Express BFF & Giao diện React (`web/` — 96 bài kiểm thử TypeScript)",
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
        "### 3.1. Số liệu thực tế toàn cầu đối chứng (AMA · JAMA Network Open · WHO)",
        "",
        "| Chỉ số / Vấn đề toàn cầu | Số liệu thực nghiệm & Tỷ lệ | Nguồn trích dẫn |",
        "| :--- | :--- | :--- |",
        "| Tỷ lệ kiệt sức bác sĩ (Burnout) | **48,2%** (2023) → **43,2%** (2024) → **41,9%** (2025); Cấp cứu **49,8%** | AMA Organizational Biopsy |",
        "| Gánh nặng EHR & Pajama Time | **~50%** ngày làm việc cho EHR (**1–2h** giấy tờ / 1h khám); **21–22,5%** làm **> 8h/tuần** tại nhà; nội trú **> 32%** (OR **1,61**) | AMA Time-Motion (Sinsky et al.) & ABFM |",
        "| Hiệu quả Ambient AI Scribe | Burnout giảm **51,9% → 38,8%** sau 30 ngày (**-13,1 điểm %**); tiết kiệm **10–16 phút/8h** (dùng ≥ 50% ca tiết kiệm **27 phút/ca trực**) | *JAMA Network Open* & *JAMIA* (Stanford / Kaiser Permanente) |",
        "| Sai sót thuốc toàn cầu | **42 tỷ USD/năm** (~**1%** chi y tế toàn cầu); **~5%** ca nhập viện; **~50%** tổn hại có thể phòng ngừa | WHO *Medication Without Harm* |",
        "| Đa thuốc lão khoa & LMIC | Sai sót lão khoa tới **17%**; gánh nặng **DALYs** tại LMIC **cao gấp 2×** nước giàu | WHO Polypharmacy Report |",
        "",
        "---",
        "",
        "## PHẦN 4: BỘ 28 CÂU HỎI PHẢN BIỆN BAN GIÁM KHẢO & KỊCH BẢN TRẢ LỜI",
        "",
    ])
    for so, muc_do, nhom, q, a1, a2, a3 in BO_22_CAU_HOI_BGK:
        mc4 = MINH_CHUNG_GIAI_QUYET.get(so, "")
        lines.extend([
            f"### Câu {so:02d} [{muc_do} · {nhom}]: {q}",
            f"- **1. Trả lời trực diện:** {a1}",
            f"- **2. Cơ chế & vị trí code:** {a2}",
            f"- **3. Số liệu & minh chứng thật:** {a3}",
            *( [f"- **4. Minh chứng thực tế (MediTrace giải quyết thế nào?):** {mc4}"] if mc4 else [] ),
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
