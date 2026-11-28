# -*- coding: utf-8 -*-
"""Xuất báo cáo Word (.docx) hoàn chỉnh cho Đề cải tiến 1 (28/11/2026):
'Chứng minh làm chủ và bảo vệ dữ liệu sức khỏe'.

Thiết kế trình bày chuyên nghiệp:
- Banner Navy & Teal, 4 thẻ chỉ số định lượng đã kiểm chứng
- Bảng đối chiếu trực diện yêu cầu Đề cải tiến 1 -> minh chứng & test
- Đủ 13 Quyết định thiết kế, bảng AI hỗ trợ vs đội tự sửa/bác bỏ,
  thống kê git 129 commits theo công cụ AI, sơ đồ luồng dữ liệu & 11 nơi lưu,
  quy trình phê duyệt bác sĩ 2 tầng + nhúng ảnh chụp giao diện thật
"""

from pathlib import Path
import subprocess
import sys
import re
from collections import Counter

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
ANH_DIR = GOC / "docs" / "minh-bach" / "anh"

OUT_ROOT = GOC / "Bao_Cao_De_Cai_Tien_1_Lam_Chu_Va_Bao_Ve_Du_Lieu_Suc_Khoe.docx"
OUT_MINH_BACH = GOC / "docs" / "minh-bach" / "TRA_LOI_DE_CAI_TIEN_1.docx"
OUT_TAI_LIEU = GOC / "docs" / "tai-lieu" / "Bao_Cao_De_Cai_Tien_1_Lam_Chu_Va_Bao_Ve_Du_Lieu_Suc_Khoe.docx"

HEX_NAVY = "1E3A5F"
HEX_TEAL = "0D5C54"
HEX_SAFE = "059669"
HEX_DANGER = "DC2626"
HEX_WARN = "D97706"
HEX_PURPLE = "7C3AED"

COLOR_NAVY = RGBColor(0x1E, 0x3A, 0x5F)
COLOR_TEAL = RGBColor(0x0D, 0x5C, 0x54)
COLOR_DARK = RGBColor(0x0F, 0x17, 0x2A)
COLOR_MUTED = RGBColor(0x47, 0x55, 0x69)
COLOR_SAFE = RGBColor(0x05, 0x96, 0x69)
COLOR_DANGER = RGBColor(0xDC, 0x26, 0x26)


def dat_vien_o(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1", sz="4"):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for canh, mau in [("w:top", top), ("w:bottom", bottom), ("w:left", left), ("w:right", right)]:
        node = OxmlElement(canh)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), sz)
        node.set(qn("w:space"), "0")
        node.set(qn("w:color"), mau)
        tcBorders.append(node)
    tcPr.append(tcBorders)


def dat_nen_o(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def dat_le_o(cell, top=80, bottom=80, left=110, right=110):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("w:top", top), ("w:bottom", bottom), ("w:left", left), ("w:right", right)]:
        node = OxmlElement(m)
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def viet_rich(p, text, dam=False, co_chu=9.2, mau=COLOR_DARK):
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*\n]+\*|`[^`]+`)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = p.add_run(part[2:-2])
            r.bold = True
            r.font.name = "Segoe UI"
            r.font.size = Pt(co_chu)
            r.font.color.rgb = mau
        elif part.startswith("*") and part.endswith("*"):
            r = p.add_run(part[1:-1])
            r.bold = dam
            r.italic = True
            r.font.name = "Segoe UI"
            r.font.size = Pt(co_chu)
            r.font.color.rgb = mau
        elif part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1])
            r.bold = dam
            r.font.name = "Consolas"
            r.font.size = Pt(max(co_chu - 0.7, 7.5))
            r.font.color.rgb = COLOR_TEAL
        else:
            r = p.add_run(part)
            r.bold = dam
            r.font.name = "Segoe UI"
            r.font.size = Pt(co_chu)
            r.font.color.rgb = mau


def them_doan_van(doc, text="", dam=False, nghieng=False, co_chu=9.5,
                  mau=COLOR_DARK, can_le=WD_ALIGN_PARAGRAPH.LEFT,
                  cach_tren=0, cach_duoi=4, gian_dong=1.15):
    p = doc.add_paragraph()
    p.alignment = can_le
    p.paragraph_format.space_before = Pt(cach_tren)
    p.paragraph_format.space_after = Pt(cach_duoi)
    p.paragraph_format.line_spacing = gian_dong
    if text:
        viet_rich(p, text, dam=dam, co_chu=co_chu, mau=mau)
        if nghieng:
            for r in p.runs:
                r.italic = True
    return p


def them_tieu_de_phan(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Segoe UI"
    r.font.size = Pt(13)
    r.font.color.rgb = COLOR_NAVY
    return p


def them_tieu_de_muc(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Segoe UI"
    r.font.size = Pt(10.5)
    r.font.color.rgb = COLOR_TEAL
    return p


def them_hop_thong_tin(doc, tieu_de, cac_dong, mau_vien=HEX_NAVY, mau_nen="F8FAFC", badge=""):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.85)
    dat_nen_o(cell, mau_nen)
    dat_vien_o(cell, top="CBD5E1", bottom="CBD5E1", left=mau_vien, right="CBD5E1", sz="14")
    dat_le_o(cell, top=85, bottom=85, left=130, right=120)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    if badge:
        rb = p.add_run(f"[{badge.upper()}] ")
        rb.bold = True
        rb.font.name = "Segoe UI"
        rb.font.size = Pt(9)
        rb.font.color.rgb = COLOR_TEAL if mau_vien == HEX_TEAL else COLOR_NAVY

    rt = p.add_run(tieu_de)
    rt.bold = True
    rt.font.name = "Segoe UI"
    rt.font.size = Pt(10.2)
    rt.font.color.rgb = COLOR_DARK

    for dong in cac_dong:
        pa = cell.add_paragraph()
        pa.paragraph_format.space_before = Pt(1.5)
        pa.paragraph_format.space_after = Pt(2)
        pa.paragraph_format.line_spacing = 1.14
        viet_rich(pa, dong, co_chu=9.1, mau=COLOR_DARK)

    them_doan_van(doc, "", cach_duoi=2)


def them_bang(doc, headers, rows, col_widths_in, first_col_bold=True, font_size=8.3):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    for ci, h in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.width = Inches(col_widths_in[ci])
        dat_nen_o(cell, HEX_NAVY)
        dat_vien_o(cell, top=HEX_NAVY, bottom=HEX_NAVY, left=HEX_NAVY, right=HEX_NAVY, sz="4")
        dat_le_o(cell, top=65, bottom=65, left=80, right=80)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Segoe UI"
        r.font.size = Pt(font_size + 0.4)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for ri, row in enumerate(rows, start=1):
        bg = "FFFFFF" if ri % 2 == 1 else "F8FAFC"
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            cell.width = Inches(col_widths_in[ci])
            dat_nen_o(cell, bg)
            dat_vien_o(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1", sz="4")
            dat_le_o(cell, top=55, bottom=55, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.12
            viet_rich(
                p,
                str(val),
                dam=(first_col_bold and ci == 0),
                co_chu=font_size,
                mau=COLOR_NAVY if (first_col_bold and ci == 0) else COLOR_DARK,
            )

    them_doan_van(doc, "", cach_duoi=3)


def thong_ke_git_hien_tai():
    out = subprocess.check_output(
        ["git", "log", "--format=%H|%h|%ad|%s|%b===END===", "--date=short"],
        cwd=str(GOC),
        encoding="utf-8",
        errors="replace",
    )
    blocks = [b.strip() for b in out.split("===END===") if b.strip()]
    cnt = Counter()
    recent = []
    for idx, b in enumerate(blocks):
        lines = b.splitlines()
        head = lines[0].split("|", 3)
        short_h, date_s, subj = head[1], head[2], head[3]
        body = "\n".join(lines[1:])
        m = re.search(r"Cong-cu-AI:\s*([A-Za-z0-9_]+)", body)
        if m:
            tool = m.group(1)
        elif "Co-Authored-By: Claude" in body:
            tool = "claude_code"
        else:
            tool = "chua_xac_dinh"
        cnt[tool] += 1
        if idx < 18:
            recent.append((date_s, f"`{short_h}`", subj, f"`{tool}`"))
    head_short = blocks[0].split("|", 3)[1] if blocks else "main"
    return len(blocks), dict(cnt), recent, head_short


def tao_bao_cao():
    tong_commit, dem_cong_cu, commits_gan_nhat, head_short = thong_ke_git_hien_tai()

    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.6)
        s.bottom_margin = Inches(0.6)
        s.left_margin = Inches(0.65)
        s.right_margin = Inches(0.65)
        s.page_width = Inches(8.27)
        s.page_height = Inches(11.69)

    # BANNER
    tbl_top = doc.add_table(rows=1, cols=1)
    tbl_top.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_top = tbl_top.cell(0, 0)
    c_top.width = Inches(6.95)
    dat_nen_o(c_top, HEX_NAVY)
    dat_vien_o(c_top, top=HEX_NAVY, bottom=HEX_NAVY, left=HEX_NAVY, right=HEX_NAVY)
    dat_le_o(c_top, top=140, bottom=140, left=160, right=160)

    p_top = c_top.paragraphs[0]
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p_top.add_run("MEDITRACE SENTINEL — BÁO CÁO ĐÁP ỨNG ĐỀ CẢI TIẾN 1 (28/11/2026)\n")
    r1.bold = True
    r1.font.name = "Segoe UI"
    r1.font.size = Pt(10.5)
    r1.font.color.rgb = RGBColor(0x99, 0xF6, 0xE4)

    r2 = p_top.add_run("CHỨNG MINH LÀM CHỦ CÔNG NGHỆ & BẢO VỆ DỮ LIỆU SỨC KHỎE\n")
    r2.bold = True
    r2.font.name = "Segoe UI"
    r2.font.size = Pt(15.5)
    r2.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    r3 = p_top.add_run(
        f"Xác nhận nhận đề: 07:32:49 28/11/2026 · Nhánh main (HEAD {head_short}) · Mọi kết quả đều gắn bằng chứng và phép thử tái lập"
    )
    r3.italic = True
    r3.font.name = "Segoe UI"
    r3.font.size = Pt(8.6)
    r3.font.color.rgb = RGBColor(0xCC, 0xFB, 0xF1)

    them_doan_van(doc, "", cach_duoi=3)

    # 4 KPI CARDS
    tbl_kpi = doc.add_table(rows=1, cols=4)
    tbl_kpi.alignment = WD_TABLE_ALIGNMENT.CENTER
    kpis = [
        ("TRUY NGUỒN GIT", f"{tong_commit} COMMITS",
         f"Claude {dem_cong_cu.get('claude_code', 0)} · AGY {dem_cong_cu.get('antigravity', 0)} · Codex {dem_cong_cu.get('codex', 0)}",
         HEX_NAVY, "EFF6FF"),
        ("CHE ĐỊNH DANH (PHONER)", "94,0% TS / 93,8% PY",
         "Trước vá: 7,5%/0,8% | Che nhầm ≤ 1,3%",
         HEX_TEAL, "F0FDFA"),
        ("KHÓA PHÊ DUYỆT", "2 TẦNG UI + SERVER",
         "Khóa 12 nút xuất & 6 API + WORM HMAC",
         HEX_DANGER, "FEF2F2"),
        ("KIỂM THỬ XÁC MINH", "69 PY + 93 WEB PASS",
         "Toàn hệ thống: 2.106 Py + 214 Web TS",
         HEX_SAFE, "ECFDF5"),
    ]
    for i, (lbl, val, sub, bc, bg) in enumerate(kpis):
        cell = tbl_kpi.cell(0, i)
        cell.width = Inches(1.73)
        dat_nen_o(cell, bg)
        dat_vien_o(cell, top=bc, bottom=bc, left=bc, right=bc, sz="6")
        dat_le_o(cell, top=55, bottom=55, left=65, right=65)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        rl = p.add_run(lbl + "\n")
        rl.bold = True
        rl.font.name = "Segoe UI"
        rl.font.size = Pt(7.3)
        rl.font.color.rgb = COLOR_NAVY
        rv = p.add_run(val + "\n")
        rv.bold = True
        rv.font.name = "Segoe UI"
        rv.font.size = Pt(9.8)
        rv.font.color.rgb = COLOR_NAVY
        rs = p.add_run(sub)
        rs.font.name = "Segoe UI"
        rs.font.size = Pt(7.1)
        rs.font.color.rgb = COLOR_MUTED

    them_doan_van(doc, "", cach_duoi=3)

    # XAC NHAN CUA TAC GIA + DE BAI
    them_hop_thong_tin(
        doc,
        "Yêu cầu Đề cải tiến 1 & Hai xác nhận trung thực của tác giả (28/11/2026)",
        [
            "• **Đề bài:** Minh bạch quá trình sử dụng AI để phát triển sản phẩm và phạm vi xử lý thông tin bệnh nhân; trình bày quyết định thiết kế, nội dung AI hỗ trợ và đội tự đánh giá/sửa; không đưa dữ liệu bệnh nhân nhận dạng được vào dịch vụ/log trái phép. Minh chứng: lịch sử sửa đổi, sơ đồ dữ liệu, quy trình bác sĩ phê duyệt trước khi dùng hồ sơ.",
            "• **Xác nhận 1:** **Chưa từng đưa hồ sơ bệnh nhân thật vào công cụ AI nào.** Khi phát triển và kiểm thử chỉ dùng dữ liệu mô phỏng và các bộ dữ liệu công khai có giấy phép hợp lệ.",
            "• **Xác nhận 2:** **Cổng mô hình ngoài AIBOX là dịch vụ bên thứ ba.** Vì vậy cổng này là tính năng phụ, mặc định TẮT ở cả 2 lớp (quản trị + bác sĩ), và chỉ gửi văn bản đã che định danh (từ chối `422` nếu còn sót).",
        ],
        mau_vien=HEX_TEAL,
        mau_nen="F0FDFA",
        badge="Đề bài & Cam kết",
    )

    # BANG DOI CHIEU TONG QUAN
    them_tieu_de_phan(doc, "TÓM TẮT ĐỐI CHIẾU YÊU CẦU ĐỀ CẢI TIẾN 1 VỚI MINH CHỨNG ĐÃ TRIỂN KHAI")
    them_bang(
        doc,
        ["Hạng mục yêu cầu", "Giải pháp đã triển khai trong mã nguồn", "Minh chứng & Phép thử kiểm chứng"],
        [
            [
                "1. Quyết định thiết kế",
                "Sổ **13 quyết định thiết kế** theo cấu trúc Vấn đề → Phương án → Lý do chọn → Người quyết → Commit/Tệp bằng chứng.",
                "`docs/minh-bach/so-quyet-dinh-thiet-ke.md`; `tests/test_minh_chung_trich_commit.py` tự kiểm từng mã commit.",
            ],
            [
                "2. AI hỗ trợ & Đội tự sửa",
                "Bảng phân vai theo từng phần dự án + **14 lần đội tự rà/bác bỏ/sửa đầu ra AI** kèm nhật ký hackathon.",
                "`docs/minh-bach/ai-ho-tro-va-doi-tu-sua.md`, `nhat-ky-hackathon.md`; sửa `2fc4eba`, `e9a1866`, `2286ee0`, `b4b3633`.",
            ],
            [
                "3. Lịch sử sửa đổi",
                "Bắt buộc trailer `Cong-cu-AI:` trong mọi commit qua hook `.githooks/commit-msg`; sinh bảng truy nguồn tự động, commit cũ để `chua_xac_dinh` (không đoán).",
                "`tools/truy_nguon_commit.py`, `tools/kiem_trailer_commit.py`, `test_truy_nguon_commit.py`, `test_kiem_trailer_commit.py`.",
            ],
            [
                "4. Không gửi PII trái phép ra dịch vụ ngoài",
                "Lõi PhoWhisper + Qwen3-4B + K1–K7 + SQLite chạy **tại chỗ**; gom mọi `fetch` vào danh sách duy nhất có test quét; che PII 2 đầu TS/Python (`94,0%` / `93,8%` PhoNER test) + lọc từ khóa PubMed/NCBI.",
                "`web/may-chu/loi-ra-mang.ts`, `an-danh-ngoai.ts`, `khu_dinh_danh.py`, `loc-tu-khoa.test.ts`, `test_ro_ri_dinh_danh_chung.py`.",
            ],
            [
                "5. Không lộ PII vào log & Kiểm soát lưu trữ",
                "Che log **trước khi cắt ngắn** (`cheLog`/`che_log`), thay `traceback.print_exc()`, che `procedureName` trong `nhat_ky`; tự xóa audio `30/30/7` ngày; xóa `localStorage` khi đăng xuất; gỡ Google Fonts.",
                "`che-log.ts`, `che_log.py`, `log-da-che.test.ts`, `test_che_log.py`, `test_audio_xoa_qua_han.py`, `khongTaiNguonNgoai.test.ts`.",
            ],
            [
                "6. Sơ đồ dữ liệu & Phê duyệt 2 tầng",
                "Sơ đồ sinh tự động từ mã (`so-do-du-lieu.md`); khóa **12 nút xuất UI + 6 API máy chủ** (`409`/`422`) qua bản chụp `ban_ky_duyet` & WORM SHA-256 + HMAC; sửa sau ký tự khóa lại.",
                "`choPhepDungHoSo.ts`, `kiem-ky-may-chu.ts`, `worm.ts`, `loiRaHoSo.test.ts`, `quyTrinhPheDuyet.test.ts`, 4 ảnh giao diện thật.",
            ],
        ],
        [1.4, 2.95, 2.6],
    )

    # =========================================================================
    # PHẦN 1: 13 QUYẾT ĐỊNH THIẾT KẾ CỐT LÕI
    # =========================================================================
    them_tieu_de_phan(doc, "PHẦN 1: SỔ 13 QUYẾT ĐỊNH THIẾT KẾ CỐT LÕI (ĐỘI CHỦ ĐỘNG QUYẾT ĐỊNH)")
    them_doan_van(
        doc,
        "Trích từ `docs/minh-bach/so-quyet-dinh-thiet-ke.md`. Mọi mã commit và đường dẫn tệp đều được kiểm tự động bằng `tests/test_minh_chung_trich_commit.py`.",
        nghieng=True, co_chu=8.8, mau=COLOR_MUTED,
    )

    them_bang(
        doc,
        ["Nhóm", "Quyết định thiết kế đã chọn & Lý do cốt lõi", "Người quyết & Bằng chứng"],
        [
            [
                "1. AI & Dữ liệu\n(QĐ 1–4)",
                "**QĐ 1:** Chỉ Bước 1 dùng AI (`Qwen3-4B` rút mệnh đề kèm trích dẫn); B2–B6 dùng luật xác định K1–K7 để truy vết & chặn trộn người nhà.\n"
                "**QĐ 2:** Chạy lõi tại chỗ (offline mặc định); gom mọi lối ra mạng vào 1 danh sách duy nhất có test quét (`loi-ra-mang.ts`); máy xa fail-closed nếu còn PII.\n"
                "**QĐ 3:** Đường ra AIBOX bên thứ ba **mặc định TẮT** ở 2 lớp (quản trị tắt luôn thắng env); màn đăng nhập demo cảnh báo chỉ dùng dữ liệu mô phỏng.\n"
                "**QĐ 4:** Tự xóa tệp ghi âm theo hạn **30/30/7 ngày** (`fb6ef97`), gỡ Google Fonts khỏi `web/index.html` dùng font hệ thống.",
                "Tác giả (đội)\n`chay_duong_ong.py`, `b4_kiem_can_cu.py`, `7d00a2a`, `4c57e89`, `054c8b3`, `8b752da`, `22c61af`, `fb6ef97`",
            ],
            [
                "2. Phê duyệt\n(QĐ 5–6)",
                "**QĐ 5:** Khóa **2 tầng** (12 nút giao diện + 6 API máy chủ qua bản chụp `ban_ky_duyet`, trả `409/422` khi chưa ký hoặc sửa 1 chữ sau ký); bản in chưa ký đóng dấu `BẢN NHÁP — CHƯA KÝ DUYỆT`.\n"
                "**QĐ 6:** Dữ liệu tham khảo thuốc/ICD-10 giữ nguyên `da_duyet = false`, chỉ gợi ý đối chiếu chờ chuyên gia y tế thẩm định.",
                "Tác giả (đội); thuốc chờ hội đồng duyệt\n`f111b14`, `98bd5de`, `a555bdc`, `kiem-ky-may-chu.ts`, `tri_thuc_thuoc.json`",
            ],
            [
                "3. Huấn luyện & Trung thực\n(QĐ 7–13)",
                "**QĐ 7:** Giữ Chính sách C làm mặc định, Chính sách D bật tường minh tránh làm sai lệch số liệu cũ.\n"
                "**QĐ 8:** Chưa thay bản `v1` bằng `v3`/`DPO` vì đo thực tế `v3` bỏ sót `14,1%` (> `11,8%` của `v1`) và DPO làm tụt log-prob câu đúng (`-1,38 -> -4,90`).\n"
                "**QĐ 9–10:** Tuyệt đối **không train** bằng dữ liệu GPT sinh (`VietMed-Sum SYN`); chỉ dùng `VNMed_Speech` (`CC BY 4.0`) thử LoRA `PhoWhisper-small` (lọc 0/0 rò rỉ với tập kiểm thử), giữ nguyên `ViDia2Std`, `PhoNER`, `ViMQ`, `ViMedAQA`, `ViHealthQA` làm bài thi độc lập.\n"
                "**QĐ 11–13:** Tập giữ kín `240 ca` chỉ chạy **1 lần**; luôn ghi rõ `11,8%` là trên tập phát triển (`2fc4eba`); không hứa suông *'tiết kiệm X% thời gian'* khi chưa bấm giờ trên bác sĩ thật.",
                "Tác giả (đội)\n`3d8a91b`, `90687ad`, `1553a4f`, `2fc4eba`, `7acd457`, `docs/ket-qua/asr-vnmed-lora.md`, `docs/ket-qua/an-danh-phoner.md`",
            ],
        ],
        [1.1, 4.15, 1.7],
        font_size=8.2,
    )

    # =========================================================================
    # PHẦN 2: NỘI DUNG AI HỖ TRỢ & ĐỘI TỰ ĐÁNH GIÁ / SỬA
    # =========================================================================
    them_tieu_de_phan(doc, "PHẦN 2: MINH BẠCH AI HỖ TRỢ & NHỮNG LẦN ĐỘI TỰ ĐÁNH GIÁ / SỬA ĐẦU RA AI")

    them_tieu_de_muc(doc, "2.1. Bảng phân vai: AI hỗ trợ phần nào — Đội làm và tự kiểm phần nào")
    them_bang(
        doc,
        ["Thành phần", "AI hỗ trợ viết / gợi ý", "Đội tự thiết kế, chạy đo & kiểm chứng", "Công cụ & Bằng chứng"],
        [
            ["Dữ liệu mô phỏng", "Viết mã sinh hội thoại theo khuôn, biến thể câu, phương ngữ", "Chọn sinh bằng luật xác định thay vì để LLM viết văn; thiết kế 657 khuôn; chia tập không trùng khuôn", "Claude Code; Antigravity (`bffaa3c`, `chia_tap_theo_khuon.py`)"],
            ["Huấn luyện Qwen3 & ASR", "Viết mã QLoRA, DPO, LoRA `PhoWhisper-small` (`VNMed_Speech`)", "Chạy thực nghiệm, kiểm rò rỉ 0/0, bác bỏ DPO & giữ mô hình sản xuất cũ chưa thay đại trà", "Claude Code (`huan_luyen_dpo.py`, `90687ad`, `asr-vnmed-lora.md`)"],
            ["Luật K1–K7 & Cảnh báo", "Viết mã phát hiện theo quy cách & vá vòng 6", "Đăng ký trước tiêu chí, chạy giữ kín đúng 1 lần, rà chặn ngữ cảnh y khoa", "Claude Code; Antigravity (`b4_kiem_can_cu.py`, `397ddbb`, `8120ce4`)"],
            ["Đo lường & Tài liệu", "Viết công cụ chấm, soạn báo cáo & sổ tay", "Chạy lại số liệu thật (kể cả chưa đạt mục tiêu), rút các con số không có bằng chứng (`78,3%`, bảng GPT-4o cũ)", "Claude Code; Antigravity (`doi-chieu-so-lieu-bao-cao.md`, `13cd479`, `6e0a245`)"],
            ["Giao diện & Máy chủ Web", "Viết mã React/Express, kiểm thử tự động", "Thử tay từng trạng thái thật, chụp 4 ảnh minh chứng, bớt nút thừa, thêm khóa server 6 route xuất", "Claude Code; Antigravity; Codex (`src/audio/`, `f111b14`, `e06236c`)"],
        ],
        [1.15, 1.85, 2.25, 1.7],
        font_size=8.1,
    )

    them_tieu_de_muc(doc, "2.2. Những lần đội phát hiện lỗi, bác bỏ hoặc tự sửa đầu ra của AI")
    them_bang(
        doc,
        ["Mốc phát hiện / Rà soát", "Lỗi trong đầu ra hoặc đề xuất của AI", "Hành động sửa của đội & Bằng chứng commit"],
        [
            ["Sửa 3 lỗi ở `8120ce4`", "Antigravity đổi chữ *'mi'* (bờ mi mắt) thành *'mày'*; báo `DOSE_MISMATCH` cho số ngày *'ho 3 ngày'*; gán `'DIA'` là lỗi mất dấu ASR", "Rà mã trực tiếp và sửa ngay ở `2fc4eba`; gắn rõ `11,8%` là số trên tập phát triển"],
            ["Rà soát độc lập 26/11", "9 lỗi nặng: `5 mg` khớp nhầm `2.5 mg`, thiếu tuổi mặc định `50`, `Sintrom` gán nhầm là `warfarin`, lỗi `khong` đồng bộ khóa nội bộ", "Viết test hồi quy cho từng lỗi (`f14a490`, `d1a6cb6`, `7d00a2a`, `e9a1866`, `2286ee0`)"],
            ["Hackathon Task 4 & 5", "Test quét `loi-ra-mang.ts` tự bắt chú thích chứa chữ `fetch(`; luật mới cho phép `env` bật đè lên việc quản trị bấm tắt AIBOX", "Sửa chú thích giữ test nghiêm (`054c8b3`); đổi ưu tiên để quản trị tắt luôn thắng (`8b752da`)"],
            ["Rà soát độc lập vòng 1", "Phát hiện 4 nút BHYT/XML, TT26, cam đoan, đi buồng xuất được khi chưa ký; log thô ở 4 route; cắt chuỗi trước khi che; tên viết thường lọt; từ khóa tra cứu mang tên thật; hook không chạy trên macOS/Linux", "Viết test đỏ trước cho từng lỗi rồi vá sạch (`2f41851`, `b4b3633`: `loiRaHoSo.test.ts`, `log-da-che.test.ts`, `loc-tu-khoa.test.ts`)"],
            ["Rà soát vòng 2 (28/11)", "Cổng `cam doan PTTT` & `đi buồng` chưa khóa ở server; `procedureName` ghi thô vào `nhat_ky`; tab chưa sửa che tab đã ký; `index.html` còn tải Google Fonts", "Khóa `ban_ky_duyet` ở 6 API (`98bd5de`, `a555bdc`), che `procedureName`, xóa `localStorage` khi logout (`22c61af`), gỡ Google Fonts"],
            ["Thanh lọc tài liệu nói quá", "Bảng so sánh GPT-4o/Gemini/Claude/Llama & số *'78,3% đa dạng'* không có tệp đo kiểm chứng; câu chữ nói quá *'0% sót dị ứng'* / *'5–7 phút'*", "Rút bỏ/đánh dấu minh bạch (`docs/doi-chieu-so-lieu-bao-cao.md`, `13cd479`, `6e0a245`)"],
        ],
        [1.35, 3.15, 2.45],
        font_size=8.1,
    )

    # =========================================================================
    # PHẦN 3: LỊCH SỬ SỬA ĐỔI GIT & HOOK BẮT BUỘC TRUY NGUỒN
    # =========================================================================
    them_tieu_de_phan(doc, "PHẦN 3: LỊCH SỬ SỬA ĐỔI GIT & CƠ CHẾ TRUY NGUỒN CÔNG CỤ AI")
    them_hop_thong_tin(
        doc,
        f"Thống kê trực tiếp toàn lịch sử Git đến hiện tại ({tong_commit} commits trên nhánh main)",
        [
            f"• **Phân bổ công cụ:** `claude_code`: **{dem_cong_cu.get('claude_code', 0)}** commits · `antigravity`: **{dem_cong_cu.get('antigravity', 0)}** commits · `codex`: **{dem_cong_cu.get('codex', 0)}** commit · `chua_xac_dinh` (các commit trước khi bật trailer): **{dem_cong_cu.get('chua_xac_dinh', 0)}** commits (không đoán thủ công).",
            "• **Ràng buộc kỹ thuật tự động:** Mọi commit mới đều bắt buộc kết thúc bằng dòng `Cong-cu-AI: <claude_code|antigravity|codex|chatgpt|khong>`. Hook `.githooks/commit-msg` (hoạt động trên cả Windows, macOS, Linux) **chặn cứng (`exit 1`)** nếu thiếu trailer hợp lệ (`tests/test_kiem_trailer_commit.py`).",
        ],
        mau_vien=HEX_NAVY,
        mau_nen="EFF6FF",
        badge="Git Audit",
    )

    them_bang(
        doc,
        ["Ngày", "Commit", "Nội dung sửa đổi (18 commit gần nhất trên main)", "Công cụ AI"],
        commits_gan_nhat,
        [0.85, 0.75, 4.2, 1.15],
        first_col_bold=False,
        font_size=7.9,
    )

    # =========================================================================
    # PHẦN 4: KHÔNG ĐƯA DỮ LIỆU NHẬN DẠNG VÀO DỊCH VỤ / LOG TRÁI PHÉP
    # =========================================================================
    them_tieu_de_phan(doc, "PHẦN 4: BẢO VỆ DỮ LIỆU SỨC KHỎE — LỐI RA MẠNG, BỘ CHE PII & LOG SẠCH")

    them_tieu_de_muc(doc, "4.1. Kiểm soát toàn bộ 6 lối ra mạng & Che định danh 2 đầu (TS + Python)")
    them_bang(
        doc,
        ["Đích kết nối mạng", "Mục đích", "Dữ liệu đi ra & Chốt bảo vệ bắt buộc", "Mặc định"],
        [
            ["Python nội bộ (`127.0.0.1:8765`)", "Chép lời, rút mệnh đề, K1–K7, dựng nháp", "Chạy tại chỗ trong cùng máy, kèm header token nội bộ", "Mở (nội bộ)"],
            ["AIBOX bên thứ ba (`/chat/completions`)", "Tính năng phụ: sửa nháp / hỏi đáp", "Chỉ gửi văn bản **ĐÃ CHE PII**; sót danh tính từ chối `422`. Cần cả quản trị + bác sĩ bật.", "**TẮT**"],
            ["AIBOX `/models`", "Kiểm tra cổng dịch vụ còn sống", "Chỉ gửi API key máy chủ, **0 byte** dữ liệu bệnh nhân", "Mở (chỉ ping)"],
            ["API tài liệu (`PubMed / IRIS / openFDA`)", "Tra tài liệu y khoa theo từ khóa", "Từ khóa do bác sĩ nhập hoặc từ văn bản đã che; chặn `422` nếu chứa tên/mã/SĐT (`locTuKhoaCoDanhTinh`)", "Mở (lọc PII)"],
            ["Trang chính thống (`WHO/CDC/BYT/NICE/MSD`)", "Đọc toàn văn phác đồ đối chiếu", "Chỉ URL tài liệu y khoa công khai", "Mở"],
            ["`www.aafp.org`", "Mở bài báo theo mã PubMed", "Chỉ mã PMID bài báo khoa học", "Mở"],
        ],
        [1.7, 1.65, 2.75, 0.85],
        font_size=8.0,
    )

    them_tieu_de_muc(doc, "4.2. Số liệu kiểm định che định danh trên PhoNER_COVID19 (Trước khi vá → Sau khi vá)")
    them_bang(
        doc,
        ["Bộ che định danh", "Trước vá (dev / test)", "Sau vá (dev / test)", "Đo lại trên 1.000 câu (`da-nguon-doc-lap.json`)", "Che nhầm `ViMedAQA`"],
        [
            ["TypeScript (`an-danh-ngoai.ts`)", "7,3% / 7,5%", "**97,5%** / **94,0%** (2.183/2.323)", "— (kiểm qua bộ 45 ca rò rỉ chung `an-danh-chung.test.ts`)", "4/300 (**1,3%**)"],
            ["Python (`khu_dinh_danh.py`)", "1,5% / 0,8%", "**97,3%** / **93,8%** (2.178/2.323)", "Nhảy từ **10/847 (1,2%)** → **775/847 (91,5%)**", "2→4/300 (**0,7–1,3%**)"],
        ],
        [1.55, 1.15, 1.4, 1.85, 1.0],
        font_size=8.0,
    )
    them_doan_van(
        doc,
        "*Trung thực khoa học:* Phần ~6% còn lọt trên tập test là tên riêng 1 tiếng đứng trơ (*\"Nhung\", \"Oanh\", \"Kim\"*). Đội không nhìn tập test để vá đuổi tránh học tủ; đồng thời giữ quy tắc che `MA_CA_BENH` (`BN416`), `TEN_VIET_TAT` (`bà H.T.P`) và không che nhầm *\"sốt từ thứ 2\"*, *\"viêm gan B.\"*, *\"Vitamin B.\"*, *\"Alsiful S.R\"*.",
        nghieng=True, co_chu=8.6, mau=COLOR_MUTED,
    )

    them_tieu_de_muc(doc, "4.3. Không lộ dữ liệu nhận dạng vào Log & Kiểm soát 11 nơi lưu dữ liệu")
    them_hop_thong_tin(
        doc,
        "Bảo vệ Log, Vòng đời xóa Âm thanh & Trình duyệt (`che-log.ts`, `che_log.py`, `storage.py`, `xoaDuLieuTrinhDuyet.ts`)",
        [
            "• **Che log trước khi cắt ngắn (`che-log.ts`, `che_log.py`):** Mọi lỗi máy chủ (kể cả lỗi dội ngược từ AIBOX) đi qua bộ che tên/SĐT/CCCD trước rồi mới cắt tối đa 300 ký tự để không cắt đôi số điện thoại; `procedureName` trong `nhat_ky` cũng qua `cheLog`; thay `traceback.print_exc()` bằng tên lỗi + dòng; test quét `log-da-che.test.ts` báo đỏ nếu lọt `console.error/warn` thô.",
            "• **11 nơi lưu dữ liệu trong `docs/minh-bach/so-do-du-lieu.md` (sinh tự động từ mã):** Bảng `ca_kham` (lọc theo `nguoi_dung_id`), `ban_sao`, `muc_kho`, `ban_ky_duyet` (trigger chống sửa), `viec_nen` (tự dọn quá 30 phút), `worm_signoff` & `audit_log_worm.db` (chỉ lưu hash/đếm, **không có lời thoại**), `nhat_ky` (đã che).",
            "• **Tự xóa tệp ghi âm & dữ liệu trình duyệt:** `src/audio/storage.py` tự xóa file `.wav` gốc và bản 16kHz sau **30 ngày** (đã duyệt), **30 ngày** (chờ duyệt để bác sĩ kịp nghe lại), **7 ngày** (phiên bỏ dở không lời thoại) và kích hoạt khi khởi tạo `AudioPipeline` ở `dich_vu_http.py`. Trình duyệt xóa toàn bộ khóa `meditrace_*` trong `localStorage` khi đăng xuất, `401` hoặc đổi người dùng; `web/index.html` đã gỡ Google Fonts.",
        ],
        mau_vien=HEX_PURPLE,
        mau_nen="F5F3FF",
        badge="Log & Lưu trữ",
    )

    # =========================================================================
    # PHẦN 5: SƠ ĐỒ LUỒNG DỮ LIỆU & QUY TRÌNH PHÊ DUYỆT 2 TẦNG + ẢNH THẬT
    # =========================================================================
    them_tieu_de_phan(doc, "PHẦN 5: SƠ ĐỒ DỮ LIỆU & QUY TRÌNH BÁC SĨ PHÊ DUYỆT TRƯỚC KHI DÙNG HỒ SƠ")

    them_hop_thong_tin(
        doc,
        "Sơ đồ luồng dữ liệu đầu – cuối & Vùng ranh giới nội bộ",
        [
            "• **Luồng tại chỗ (Mặc định):** Micro phòng khám → Trình duyệt bác sĩ → Máy chủ Web MediTrace (Node/Express) → Dịch vụ Python nội bộ `127.0.0.1:8765` (PhoWhisper + Qwen3-4B + K1–K7) → SQLite tại chỗ (`ca_kham`, `ban_ky_duyet`, sổ WORM) + Thư mục âm thanh.",
            "• **Luồng bản demo công khai:** Người xem chỉ được nhập dữ liệu mô phỏng (cảnh báo ngay tại màn hình đăng nhập) đi qua Cloudflare Worker/Tunnel chuyển tiếp TLS.",
            "• **Luồng ra ngoài có kiểm soát:** Chỉ cho phép: (1) Từ khóa y khoa đã lọc PII ra PubMed/WHO/openFDA, (2) URL phác đồ chính thống, (3) Cổng AIBOX khi **cả quản trị và bác sĩ bật** kèm bộ che `422` fail-closed.",
        ],
        mau_vien=HEX_TEAL,
        mau_nen="F0FDFA",
        badge="Sơ đồ dữ liệu",
    )

    them_bang(
        doc,
        ["Bước trạng thái", "Hành vi giao diện & API máy chủ", "Cơ chế khóa & Phép thử xác minh"],
        [
            ["1. Bản nháp mới", "Chỉ được **xem**; toàn bộ **12 nút xuất** (Chép, In, PDF, `.txt`, `.md`, FHIR, SBAR, HIS, Dặn dò, BHYT/XML, TT26, Cam đoan, Đi buồng) đều **khóa**.", "`choPhepDungHoSo.ts`, `loiRaHoSo.test.ts` (đỏ nếu có hộp xuất nào không kiểm ký)."],
            ["2. Còn mục *Cần xác nhận*", "Nút ký hiển thị `Cần xác nhận (n)`, **không ký được**; bấm vào thì cuộn tới đúng mệnh đề treo hoặc mệnh đề thiếu lượt thoại căn cứ.", "`kiemTraDieuKienKyDuyet` (`compileEffectiveNote.ts`, `quyTrinhPheDuyet.test.ts`)."],
            ["3. Bác sĩ duyệt & Ký", "Bác sĩ chọn Giữ/Sửa/Bỏ từng mục rồi bấm Ký → Server tính SHA-256 nội dung + HMAC-SHA256 nối vào WORM, đồng thời chụp `ban_ky_duyet`.", "`worm.ts`, `sign-off.ts`, `kiem-ky-may-chu.ts`, `worm.test.ts`."],
            ["4. Được dùng hồ sơ", "Mở khóa 12 nút UI; khi gọi **6 API xuất** (`tao-ma`, `bhyt/precheck`, `bhyt/recompile`, `fhir/recompile`, `informed-consent`, `ward-round-diff`), server đối chiếu đúng bản chụp `ban_ky_duyet` + IDOR `403`.", "`kiem-ky-may-chu.test.ts`, `routes/bhyt-ocr.test.ts`, `routes/boost-lam-sang.test.ts`."],
            ["5. Sửa 1 chữ sau ký", "Băm nội dung hoặc quyết định duyệt thay đổi → **khóa lại lập tức** ở cả UI lẫn máy chủ (`409 chua_ky_duyet` / `422 noi_dung_khac_ban_ky`), bắt ký lại.", "`isSignOffStale`, `quyTrinhPheDuyet.test.ts` bước 5–6, `kiem-ky-may-chu.test.ts`."],
        ],
        [1.35, 3.35, 2.25],
        font_size=8.1,
    )

    # CHEN 4 ANH CHUP GIAO DIEN THAT (2x2)
    anh_list = [
        (ANH_DIR / "khoa-truoc-ky-1.jpg", "Hình 1: Chưa ký — toàn bộ nút Chép/In/Xuất bị khóa"),
        (ANH_DIR / "khoa-truoc-ky-2.jpg", "Hình 2: Đã ký WORM (#1) — mở khóa dùng hồ sơ"),
        (ANH_DIR / "khoa-truoc-ky-3.jpg", "Hình 3: Sửa nội dung sau khi ký — tự khóa lại, đòi ký lại"),
        (ANH_DIR / "thong-bao-ban-demo.jpg", "Hình 4: Cảnh báo bản demo công khai chỉ nhập dữ liệu mô phỏng"),
    ]
    if all(p.exists() for p, _ in anh_list):
        them_tieu_de_muc(doc, "Minh chứng ảnh chụp giao diện thực tế (không phải ảnh vẽ AI)")
        tbl_img = doc.add_table(rows=2, cols=2)
        tbl_img.alignment = WD_TABLE_ALIGNMENT.CENTER
        for idx, (img_path, caption) in enumerate(anh_list):
            cell = tbl_img.cell(idx // 2, idx % 2)
            cell.width = Inches(3.45)
            dat_vien_o(cell, top="CBD5E1", bottom="CBD5E1", left="CBD5E1", right="CBD5E1", sz="4")
            dat_nen_o(cell, "F8FAFC")
            dat_le_o(cell, top=60, bottom=60, left=60, right=60)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            run_img = p.add_run()
            run_img.add_picture(str(img_path), width=Inches(3.2))
            pc = cell.add_paragraph()
            pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pc.paragraph_format.space_before = Pt(2)
            pc.paragraph_format.space_after = Pt(0)
            rc = pc.add_run(caption)
            rc.italic = True
            rc.font.name = "Segoe UI"
            rc.font.size = Pt(8.0)
            rc.font.color.rgb = COLOR_MUTED
        them_doan_van(doc, "", cach_duoi=3)

    # =========================================================================
    # PHẦN 6: GIỚI HẠN NÓI THẲNG & KẾT QUẢ KIỂM THỬ XÁC MINH
    # =========================================================================
    them_tieu_de_phan(doc, "PHẦN 6: CÁC GIỚI HẠN CÒN LẠI (NÓI THẲNG) & KẾT QUẢ KIỂM THỬ XÁC MINH")

    them_hop_thong_tin(
        doc,
        "Những giới hạn nhóm chủ động công khai trung thực (không giấu hoặc nói quá)",
        [
            "• **Bộ che PII (`94,0%` TS / `93,8%` Py trên `PhoNER_COVID19` test):** Chưa chạm ngưỡng `95%` trên test (chủ yếu tên 1 tiếng đứng trơ); nhóm không vá đuổi trên tập test để tránh học tủ (vẫn giữ `97,5%` / `97,3%` trên dev).",
            "• **Bản sao tạm trên trình duyệt:** `localStorage` xóa sạch khi đăng xuất / `401` / đổi người dùng, nhưng nếu người dùng đóng tab không đăng xuất thì bản lưu tạm trên máy đó chưa mã hóa.",
            "• **Thao tác hệ điều hành trình duyệt:** Không chặn được bôi đen `Ctrl+C` khi đọc tại chỗ hay `Ctrl+P`, nên bản in khi chưa ký tự mang dòng **`BẢN NHÁP — CHƯA KÝ DUYỆT`** ở đầu trang.",
            "• **Lịch sử commit cũ & giữ audio demo:** `34` commit cũ chưa ghi công cụ giữ nguyên trạng thái `chua_xac_dinh` chờ tác giả xác nhận dần; chính sách tự xóa audio `30/30/7` ngày đã chốt trong mã nhưng tạm nâng hạn trên máy chủ demo tới sau buổi thi để giữ âm thanh mẫu.",
            "• **Đánh giá trên bác sĩ thật & thử nghiệm LoRA ASR:** Chưa thực nghiệm bấm giờ trên bác sĩ lâm sàng để kiểm chứng việc duyệt bừa hay thời gian tiết kiệm; adapter LoRA `PhoWhisper-small` trên `VNMed_Speech` (`WER ViMedCSS 0,3165 → 0,2610`) mới nằm ở mức báo cáo thực nghiệm (`docs/ket-qua/asr-vnmed-lora.md`), chưa triển khai thay thế mô hình sản xuất.",
        ],
        mau_vien=HEX_WARN,
        mau_nen="FFFBEB",
        badge="Giới hạn minh bạch",
    )

    them_bang(
        doc,
        ["Bộ kiểm thử đã chạy kiểm chứng", "Kết quả quan sát trực tiếp", "Phạm vi kiểm chứng"],
        [
            ["Nhóm test Đề 1 (Python, vừa chạy lại 28/11)", "**69 passed, 0 failed** (1,75s)", "`test_minh_chung_trich_commit`, `test_truy_nguon_commit`, `test_kiem_trailer_commit`, `test_loi_ra_mang_python`, `test_ro_ri_dinh_danh_chung`, `test_che_log`"],
            ["Nhóm test Đề 1 (Web TS, vừa chạy lại 28/11)", "**93 passed, 0 failed** (3,08s)", "`quyTrinhPheDuyet`, `choPhepDungHoSo`, `loiRaHoSo`, `kiem-ky-may-chu`, `worm`, `che-log`, `loi-ra-mang`, `an-danh-chung`, `llm-ngoai`, `tra-cuu`"],
            ["Toàn bộ hồi quy (sau vòng 2, `TRA_LOI_DE_CAI_TIEN_1.md`)", "**2.106 Python passed** (28 skip) · **214/214 Web TS passed**", "Đóng gói `npm run build` & kiểm kiểu `tsc --noEmit` (`npm run lint`) sạch không lỗi"],
        ],
        [2.05, 1.95, 2.95],
        font_size=8.1,
    )

    doc.save(str(OUT_ROOT))
    doc.save(str(OUT_MINH_BACH))
    doc.save(str(OUT_TAI_LIEU))
    for folder in ("Downloads", "Desktop"):
        try:
            target = Path.home() / folder / OUT_ROOT.name
            doc.save(str(target))
        except Exception as e:
            print(f"Luu {folder}: {e}")
    print(f"Da xuat xong file Word De cai tien 1 tai:\n-> {OUT_ROOT}\n-> {OUT_MINH_BACH}\n-> {OUT_TAI_LIEU}")


if __name__ == "__main__":
    tao_bao_cao()
