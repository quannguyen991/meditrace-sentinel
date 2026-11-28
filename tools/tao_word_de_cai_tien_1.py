# -*- coding: utf-8 -*-
"""Xuất báo cáo Word (.docx) hoàn chỉnh cho Đề cải tiến 1 (28/11/2026):
'Chứng minh làm chủ và bảo vệ dữ liệu sức khỏe'.

Phong cách văn bản chuyên nghiệp, trang trọng (chuẩn báo cáo kỹ thuật / y tế):
- Phông Times New Roman thống nhất, mã/commit dùng Consolas
- Không dùng thẻ KPI màu mè, không dùng khung hộp tô nền sặc sỡ
- Bảng biểu kiểu học thuật (nền trắng, tiêu đề xám nhạt, đường kẻ ngang mảnh)
- Đánh số trang tự động và tiêu đề đầu trang trang nhã
"""

from collections import Counter
from pathlib import Path
import re
import subprocess
import sys

import docx
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

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

PHONG_CHU = "Times New Roman"
MAU_CHU = RGBColor(0x11, 0x18, 0x27)
MAU_PHU = RGBColor(0x4B, 0x55, 0x63)
MAU_NHAN = RGBColor(0x1E, 0x29, 0x3B)


def dat_font_run(run, ten=PHONG_CHU, co=11.5, dam=False, nghieng=False, mau=MAU_CHU):
    run.font.name = ten
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.rFonts
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), ten)
    rFonts.set(qn("w:hAnsi"), ten)
    rFonts.set(qn("w:cs"), ten)
    run.font.size = Pt(co)
    run.bold = dam
    run.italic = nghieng
    run.font.color.rgb = mau


def viet_rich(p, text, dam=False, nghieng=False, co=11.5, mau=MAU_CHU):
    for part in re.split(r"(\*\*[^*]+\*\*|\*[^*\n]+\*|`[^`]+`)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            r = p.add_run(part[2:-2])
            dat_font_run(r, PHONG_CHU, co, dam=True, nghieng=nghieng, mau=mau)
        elif part.startswith("*") and part.endswith("*"):
            r = p.add_run(part[1:-1])
            dat_font_run(r, PHONG_CHU, co, dam=dam, nghieng=True, mau=mau)
        elif part.startswith("`") and part.endswith("`"):
            r = p.add_run(part[1:-1])
            dat_font_run(r, "Consolas", max(co - 1.5, 8.5), dam=dam, nghieng=nghieng, mau=MAU_NHAN)
        else:
            r = p.add_run(part)
            dat_font_run(r, PHONG_CHU, co, dam=dam, nghieng=nghieng, mau=mau)


def them_duong_ke_duoi(p, mau_hex="334155", sz="8"):
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), sz)
    bottom.set(qn("w:space"), "4")
    bottom.set(qn("w:color"), mau_hex)
    pBdr.append(bottom)
    pPr.append(pBdr)


def them_trinh_ky_trich_dan(p, mau_hex="94A3B8"):
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    left = OxmlElement("w:left")
    left.set(qn("w:val"), "single")
    left.set(qn("w:sz"), "12")
    left.set(qn("w:space"), "8")
    left.set(qn("w:color"), mau_hex)
    pBdr.append(left)
    pPr.append(pBdr)


def dat_vien_o(cell, top="none", bottom="none", left="none", right="none", sz="4", mau="CBD5E1"):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for canh, val in [("w:top", top), ("w:bottom", bottom), ("w:left", left), ("w:right", right)]:
        node = OxmlElement(canh)
        node.set(qn("w:val"), val)
        if val != "none":
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


def dat_le_o(cell, top=70, bottom=70, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for m, val in [("w:top", top), ("w:bottom", bottom), ("w:left", left), ("w:right", right)]:
        node = OxmlElement(m)
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def them_doan(doc, text="", dam=False, nghieng=False, co=11.5, mau=MAU_CHU,
              can_le=WD_ALIGN_PARAGRAPH.LEFT, cach_tren=0, cach_duoi=5, gian_dong=1.22,
              lui_trai=0.0):
    p = doc.add_paragraph()
    p.alignment = can_le
    p.paragraph_format.space_before = Pt(cach_tren)
    p.paragraph_format.space_after = Pt(cach_duoi)
    p.paragraph_format.line_spacing = gian_dong
    if lui_trai:
        p.paragraph_format.left_indent = Inches(lui_trai)
    if text:
        viet_rich(p, text, dam=dam, nghieng=nghieng, co=co, mau=mau)
    return p


def them_gach_dau_dong(doc, text, co=11.2):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(3.5)
    p.paragraph_format.line_spacing = 1.2
    viet_rich(p, text, co=co, mau=MAU_CHU)
    return p


def them_trich_dan(doc, text, co=11.0):
    p = them_doan(doc, text, nghieng=True, co=co, mau=MAU_CHU, cach_tren=4, cach_duoi=6, lui_trai=0.2)
    them_trinh_ky_trich_dan(p)
    return p


def them_tieu_de_phan(doc, text):
    p = them_doan(doc, text, dam=True, co=13.5, mau=MAU_NHAN, cach_tren=14, cach_duoi=6, gian_dong=1.15)
    p.paragraph_format.keep_with_next = True
    them_duong_ke_duoi(p, mau_hex="94A3B8", sz="6")
    return p


def them_tieu_de_muc(doc, text):
    p = them_doan(doc, text, dam=True, co=12.0, mau=MAU_NHAN, cach_tren=10, cach_duoi=4, gian_dong=1.15)
    p.paragraph_format.keep_with_next = True
    return p


def them_bang(doc, headers, rows, col_widths_in, first_col_bold=True, font_size=9.5):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Hang tieu de: nen xam rat nhat, ke duoi dam, chu den trang nha
    for ci, h in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.width = Inches(col_widths_in[ci])
        dat_nen_o(cell, "F1F5F9")
        dat_vien_o(cell, top="single", bottom="single", left="none", right="none", sz="8", mau="334155")
        dat_le_o(cell, top=80, bottom=80, left=85, right=85)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(h)
        dat_font_run(r, PHONG_CHU, font_size + 0.3, dam=True, mau=MAU_NHAN)

    for ri, row in enumerate(rows, start=1):
        is_last = (ri == len(rows))
        for ci, val in enumerate(row):
            cell = tbl.cell(ri, ci)
            cell.width = Inches(col_widths_in[ci])
            dat_vien_o(
                cell,
                top="none",
                bottom="single",
                left="none",
                right="none",
                sz="8" if is_last else "4",
                mau="334155" if is_last else "CBD5E1",
            )
            dat_le_o(cell, top=65, bottom=65, left=85, right=85)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.16
            viet_rich(p, str(val), dam=(first_col_bold and ci == 0), co=font_size, mau=MAU_CHU)

    them_doan(doc, "", cach_duoi=4)


def them_header_footer(doc):
    section = doc.sections[0]
    section.different_first_page_header_footer = True

    hp = section.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    hr = hp.add_run("MediTrace Sentinel — Báo cáo đáp ứng Đề cải tiến 1 (28/11/2026)")
    dat_font_run(hr, PHONG_CHU, 9.0, nghieng=True, mau=MAU_PHU)

    fp = section.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fr1 = fp.add_run("Trang ")
    dat_font_run(fr1, PHONG_CHU, 9.0, mau=MAU_PHU)

    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    fp._p.append(fld)


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
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.85)
        s.page_width = Inches(8.27)
        s.page_height = Inches(11.69)

    them_header_footer(doc)

    # PHAN MO DAU TRANG TRONG (KHONG TO MAU / KHONG HOP KPI)
    them_doan(
        doc,
        "DỰ ÁN MEDITRACE SENTINEL — HỒ SƠ ĐÁP ỨNG ĐỀ CẢI TIẾN 1",
        dam=True, co=10.5, mau=MAU_PHU, can_le=WD_ALIGN_PARAGRAPH.CENTER, cach_duoi=4,
    )
    them_doan(
        doc,
        "CHỨNG MINH LÀM CHỦ CÔNG NGHỆ VÀ BẢO VỆ DỮ LIỆU SỨC KHỎE",
        dam=True, co=15.5, mau=MAU_NHAN, can_le=WD_ALIGN_PARAGRAPH.CENTER, cach_duoi=4,
    )
    p_sub = them_doan(
        doc,
        f"Ngày xác nhận đề: 07:32:49, 28/11/2026  |  Nhánh mã nguồn: main (commit {head_short})  |  Đơn vị thực hiện: Đội MediTrace",
        nghieng=True, co=10.0, mau=MAU_PHU, can_le=WD_ALIGN_PARAGRAPH.CENTER, cach_duoi=10,
    )
    them_duong_ke_duoi(p_sub, mau_hex="1E293B", sz="10")

    them_trich_dan(
        doc,
        "**Đề bài cải tiến:** Quá trình sử dụng AI để phát triển sản phẩm và phạm vi xử lý thông tin bệnh nhân cần minh bạch hơn. "
        "Trình bày quyết định thiết kế, những nội dung AI hỗ trợ và đội tự đánh giá/sửa; không đưa dữ liệu bệnh nhân nhận dạng được vào dịch vụ hoặc log trái phép. "
        "Minh chứng: lịch sử sửa đổi, sơ đồ dữ liệu và quy trình bác sĩ phê duyệt trước khi dùng hồ sơ.",
    )

    them_doan(doc, "**Hai xác nhận chính thức của nhóm tác giả (28/11/2026):**", cach_tren=4, cach_duoi=2)
    them_gach_dau_dong(
        doc,
        "**Chưa từng đưa hồ sơ bệnh nhân thật vào công cụ AI nào.** Trong suốt quá trình phát triển và kiểm thử, đội chỉ sử dụng dữ liệu mô phỏng tự sinh và các bộ dữ liệu công khai có giấy phép hợp lệ.",
    )
    them_gach_dau_dong(
        doc,
        "**Cổng mô hình ngoài AIBOX là dịch vụ bên thứ ba.** Do đó tính năng trợ lý ngoài là tính năng phụ, mặc định tắt ở cả hai lớp (quản trị và bác sĩ), và chỉ gửi văn bản đã khử định danh (từ chối HTTP 422 nếu còn sót dấu hiệu danh tính).",
    )

    # BANG TOM TAT DOI CHIEU
    them_tieu_de_phan(doc, "Tóm tắt đối chiếu yêu cầu của đề bài với minh chứng thực tế")
    them_bang(
        doc,
        ["Nội dung yêu cầu", "Giải pháp đã triển khai trong mã nguồn", "Tệp minh chứng và phép thử kiểm chứng"],
        [
            [
                "1. Quyết định thiết kế",
                "Sổ 13 quyết định thiết kế ghi rõ vấn đề, các phương án cân nhắc, phương án chọn, lý do, người quyết và mã commit/tệp bằng chứng.",
                "`docs/minh-bach/so-quyet-dinh-thiet-ke.md`; `tests/test_minh_chung_trich_commit.py`",
            ],
            [
                "2. Nội dung AI hỗ trợ và đội tự đánh giá/sửa",
                "Bảng phân vai theo từng cấu phần dự án và danh sách 14 lần đội rà soát, phát hiện lỗi, bác bỏ hoặc tự sửa đầu ra của AI kèm nhật ký.",
                "`docs/minh-bach/ai-ho-tro-va-doi-tu-sua.md`, `nhat-ky-hackathon.md`",
            ],
            [
                "3. Lịch sử sửa đổi",
                f"Toàn bộ {tong_commit} commit trên nhánh `main` được thống kê theo công cụ AI; hook `.githooks/commit-msg` chặn mọi commit mới thiếu dòng `Cong-cu-AI:`.",
                "`tools/truy_nguon_commit.py`, `tools/kiem_trailer_commit.py`, `test_truy_nguon_commit.py`",
            ],
            [
                "4. Không gửi dữ liệu nhận dạng vào dịch vụ trái phép",
                "Lõi PhoWhisper, Qwen3-4B, luật K1–K7 và SQLite chạy tại chỗ; mọi lời gọi mạng khai báo tập trung có test quét; bộ che định danh đạt 94,0% (TS) / 93,8% (Python) trên PhoNER test; chặn từ khóa PubMed có danh tính.",
                "`web/may-chu/loi-ra-mang.ts`, `an-danh-ngoai.ts`, `khu_dinh_danh.py`, `test_loi_ra_mang_python.py`",
            ],
            [
                "5. Không đưa dữ liệu nhận dạng vào log trái phép",
                "Che định danh trước khi cắt ngắn chuỗi log lỗi (`cheLog`/`che_log`), thay `traceback.print_exc()`, che `procedureName` trong `nhat_ky`; tự xóa audio quá hạn 30/30/7 ngày; xóa `localStorage` khi đăng xuất; gỡ Google Fonts.",
                "`che-log.ts`, `che_log.py`, `log-da-che.test.ts`, `test_che_log.py`, `khongTaiNguonNgoai.test.ts`",
            ],
            [
                "6. Sơ đồ dữ liệu và quy trình phê duyệt trước khi dùng hồ sơ",
                "Sơ đồ dữ liệu sinh tự động từ mã nguồn; khóa 2 tầng (12 nút xuất trên giao diện + 6 API máy chủ) qua bản chụp `ban_ky_duyet` và sổ ký WORM SHA-256 + HMAC; sửa sau khi ký tự động khóa lại.",
                "`so-do-du-lieu.md`, `choPhepDungHoSo.ts`, `kiem-ky-may-chu.ts`, `worm.ts`, `loiRaHoSo.test.ts`",
            ],
        ],
        [1.45, 3.05, 2.05],
        font_size=9.2,
    )

    # =========================================================================
    # PHAN 1: QUYET DINH THIET KE
    # =========================================================================
    them_tieu_de_phan(doc, "1. Quyết định thiết kế cốt lõi")
    them_doan(
        doc,
        "Sổ quyết định thiết kế (`docs/minh-bach/so-quyet-dinh-thiet-ke.md`) ghi lại 13 quyết định kiến trúc quan trọng nhất của dự án. "
        "Phép thử tự động `tests/test_minh_chung_trich_commit.py` kiểm tra mọi mã commit (`git cat-file`) và đường dẫn tệp được trích dẫn.",
        co=11.0,
    )

    them_bang(
        doc,
        ["Nhóm", "Quyết định lựa chọn và lý do kỹ thuật", "Người quyết & Bằng chứng"],
        [
            [
                "Nhóm 1:\nKiến trúc AI & Bảo vệ dữ liệu\n(QĐ 1–4)",
                "**QĐ 1:** Chỉ dùng AI (`Qwen3-4B`) ở Bước 1 để tách từng mệnh đề kèm câu trích; các bước gom chủ thể, xử lý đính chính, khóa căn cứ `K1–K7` và dựng bản nháp đều dùng luật xác định để truy vết được lỗi và chặn trộn bệnh của người nhà.\n"
                "**QĐ 2:** Chạy toàn bộ lõi tại chỗ (offline mặc định); gom mọi lối ra mạng vào một danh sách duy nhất có test quét (`loi-ra-mang.ts`); máy xa fail-closed nếu kiểm tra còn sót định danh.\n"
                "**QĐ 3:** Đường gửi nội dung ca khám ra bên thứ ba (AIBOX) mặc định TẮT ở hai lớp (công tắc quản trị tắt luôn thắng biến môi trường); màn hình đăng nhập bản demo cảnh báo chỉ dùng dữ liệu mô phỏng.\n"
                "**QĐ 4:** Đặt hạn tự xóa tệp ghi âm sau 30 ngày (ca đã duyệt và ca chờ duyệt để bác sĩ kịp nghe lại căn cứ) và 7 ngày (phiên bỏ dở chưa có lời thoại, `fb6ef97`); gỡ hoàn toàn Google Fonts khỏi `web/index.html`.",
                "Tác giả (đội)\n`chay_duong_ong.py`, `b4_kiem_can_cu.py`, `7d00a2a`, `4c57e89`, `054c8b3`, `8b752da`, `22c61af`, `fb6ef97`",
            ],
            [
                "Nhóm 2:\nPhê duyệt trước khi dùng hồ sơ\n(QĐ 5–6)",
                "**QĐ 5:** Khóa hai tầng ở cả giao diện (12 nút chép/in/xuất) lẫn máy chủ (lưu bản chụp `ban_ky_duyet`, trả `409`/`422` cho cả 6 API xuất hồ sơ khi chưa ký hoặc sửa sau ký); bản in chưa ký tự đóng dấu *\"BẢN NHÁP — CHƯA KÝ DUYỆT\"*.\n"
                "**QĐ 6:** Danh mục thuốc và mã bệnh tham khảo giữ nguyên cờ `da_duyet = false`, chỉ hiển thị ở mức gợi ý đối chiếu chờ bác sĩ/dược sĩ thẩm định.",
                "Tác giả (đội); thuốc chờ hội đồng duyệt\n`f111b14`, `98bd5de`, `a555bdc`, `kiem-ky-may-chu.ts`, `tri_thuc_thuoc.json`",
            ],
            [
                "Nhóm 3:\nKỷ luật dữ liệu & Trung thực\n(QĐ 7–13)",
                "**QĐ 7:** Giữ Chính sách C làm mặc định, Chính sách D bật tường minh nhằm không làm lệch bảng số liệu đã công bố.\n"
                "**QĐ 8:** Chưa đưa bản `v3` hay `DPO` vào chạy chính do đo trên ca đầy đủ `v3` bỏ sót `14,1%` (cao hơn `11,8%` của `v1`) và `DPO` làm giảm xác suất câu đúng (log-prob tụt từ `-1,38` xuống `-4,90`).\n"
                "**QĐ 9–10:** Tuyệt đối không train bằng dữ liệu GPT sinh (`VietMed-Sum SYN`); chỉ dùng `VNMed_Speech` (`CC BY 4.0`) thử LoRA `PhoWhisper-small` (lọc 0/0 câu trùng với tập test, chưa thay mô hình sản xuất), giữ các bộ ngoài (`ViDia2Std`, `PhoNER`, `ViMQ`, `ViMedAQA`, `ViHealthQA`) làm bài thi độc lập.\n"
                "**QĐ 11–13:** Tập giữ kín `240 ca` chỉ chạy đúng 1 lần; luôn gắn rõ nhãn *\"tập phát triển\"* cạnh tỷ lệ `11,8%`; không công bố con số tiết kiệm thời gian khi chưa đo thực nghiệm trên bác sĩ thật.",
                "Tác giả (đội)\n`3d8a91b`, `90687ad`, `1553a4f`, `2fc4eba`, `7acd457`, `asr-vnmed-lora.md`, `an-danh-phoner.md`",
            ],
        ],
        [1.15, 3.85, 1.55],
        font_size=9.0,
    )

    # =========================================================================
    # PHAN 2: NOI DUNG AI HO TRO VA DOI TU DANH GIA / SUA
    # =========================================================================
    them_tieu_de_phan(doc, "2. Nội dung AI hỗ trợ và quá trình đội tự đánh giá, sửa lỗi")

    them_tieu_de_muc(doc, "2.1. Phân vai theo từng cấu phần của dự án")
    them_bang(
        doc,
        ["Thành phần", "Phần AI hỗ trợ viết mã", "Phần đội thiết kế, kiểm chứng và quyết định", "Công cụ & Bằng chứng"],
        [
            ["Dữ liệu mô phỏng", "Viết mã sinh hội thoại theo khuôn, biến thể câu, phương ngữ", "Chọn sinh bằng luật xác định thay vì để LLM viết văn; thiết kế 657 khuôn; chia tập không trùng khuôn", "Claude Code; Antigravity (`bffaa3c`, `chia_tap_theo_khuon.py`)"],
            ["Huấn luyện Qwen3 & ASR", "Viết mã QLoRA, DPO, LoRA `PhoWhisper-small` (`VNMed_Speech`)", "Chạy trên máy của đội, kiểm rò rỉ 0/0, bác bỏ DPO và giữ nguyên mô hình sản xuất", "Claude Code (`huan_luyen_dpo.py`, `90687ad`, `asr-vnmed-lora.md`)"],
            ["Luật K1–K7 & Cảnh báo", "Viết mã phát hiện theo quy cách và các vòng vá điểm mù", "Đặt luật, đăng ký trước tiêu chí, chỉ chạy tập giữ kín 1 lần, siết khóa ngữ cảnh y khoa", "Claude Code; Antigravity (`b4_kiem_can_cu.py`, `397ddbb`, `8120ce4`)"],
            ["Đo lường & Tài liệu", "Viết công cụ chấm điểm, soạn báo cáo và sổ tay", "Chạy lại phép đo, giữ nguyên số chưa đạt, rút các bảng/con số thiếu bằng chứng", "Claude Code; Antigravity (`doi-chieu-so-lieu-bao-cao.md`, `13cd479`, `6e0a245`)"],
            ["Giao diện & Máy chủ Web", "Viết mã React/Express và kiểm thử tự động", "Thử tay từng trạng thái thật, chụp 4 ảnh minh chứng, bớt nút thừa, thêm khóa server 6 API xuất", "Claude Code; Antigravity; Codex (`src/audio/`, `f111b14`, `e06236c`)"],
        ],
        [1.15, 1.75, 2.1, 1.55],
        font_size=8.9,
    )

    them_tieu_de_muc(doc, "2.2. Những lần đội phát hiện lỗi, bác bỏ hoặc tự sửa đầu ra của AI")
    them_bang(
        doc,
        ["Đợt rà soát", "Lỗi trong đầu ra hoặc đề xuất của AI", "Biện pháp sửa và kiểm chứng của đội"],
        [
            ["Sửa 3 lỗi ở `8120ce4`", "Mã do Antigravity viết đổi chữ *\"mi\"* (bờ mi mắt) thành *\"mày\"*; báo `DOSE_MISMATCH` cho số ngày *\"ho 3 ngày\"*; gán chữ viết tắt `\"DIA\"` là nhiễu mất dấu ASR.", "Đội rà lại mã trực tiếp, sửa tại `2fc4eba`, ghi rõ `11,8%` là số đo trên tập phát triển."],
            ["Rà soát độc lập 26/11", "9 lỗi nghiêm trọng: khóa K6 coi `5 mg` khớp `2.5 mg`; thiếu tuổi mặc định `50`; bảng thuốc cũ ghi `Sintrom` là biệt dược của `warfarin`; thiếu đồng bộ khóa nội bộ.", "Viết test hồi quy cho từng lỗi (`f14a490`, `d1a6cb6`, `7d00a2a`, `e9a1866`, `2286ee0`)."],
            ["Hackathon Task 4 & 5", "Test quét `loi-ra-mang.ts` tự bắt chú thích chứa chữ `fetch(`; luật mới để biến môi trường bật đè lên việc quản trị bấm tắt AIBOX.", "Sửa chú thích và giữ test nghiêm (`054c8b3`); đổi thứ tự ưu tiên để quản trị tắt luôn thắng (`8b752da`)."],
            ["Rà soát độc lập vòng 1", "Phát hiện 4 nút BHYT/XML, TT26, cam đoan, đi buồng xuất được khi chưa ký; log thô ở 4 route; cắt chuỗi trước khi che; tên viết thường lọt; từ khóa tra cứu mang tên thật; hook không chạy trên macOS/Linux.", "Viết test đỏ tái hiện từng lỗi trước khi vá (`2f41851`, `b4b3633`: `loiRaHoSo.test.ts`, `log-da-che.test.ts`, `loc-tu-khoa.test.ts`)."],
            ["Rà soát vòng 2 (28/11)", "Cổng cam đoan PTTT & đi buồng chưa khóa ở máy chủ; `procedureName` ghi thô vào `nhat_ky`; tab chưa sửa che tab đã ký; `web/index.html` còn tải Google Fonts.", "Khóa `ban_ky_duyet` ở 6 API (`98bd5de`, `a555bdc`), che `procedureName`, xóa `localStorage` khi đăng xuất (`22c61af`), gỡ Google Fonts."],
            ["Thanh lọc tài liệu nói quá", "Bảng so sánh GPT-4o/Gemini/Claude/Llama và con số *\"78,3% đa dạng\"* không có tệp đo; câu chữ nói quá *\"0% sót dị ứng\"* / *\"5–7 phút\"*.", "Rút bỏ hoặc đánh dấu chưa có bằng chứng (`doi-chieu-so-lieu-bao-cao.md`, `13cd479`, `6e0a245`)."],
        ],
        [1.3, 2.95, 2.3],
        font_size=8.9,
    )

    # =========================================================================
    # PHAN 3: LICH SU SUA DOI GIT
    # =========================================================================
    them_tieu_de_phan(doc, "3. Lịch sử sửa đổi Git và cơ chế truy nguồn công cụ AI")
    them_doan(
        doc,
        f"Tính đến thời điểm xuất báo cáo (commit `{head_short}`), nhánh `main` có tổng cộng **{tong_commit} commit**, phân bổ như sau: "
        f"`claude_code` (**{dem_cong_cu.get('claude_code', 0)}**), `antigravity` (**{dem_cong_cu.get('antigravity', 0)}**), "
        f"`codex` (**{dem_cong_cu.get('codex', 0)}**), và `chua_xac_dinh` (**{dem_cong_cu.get('chua_xac_dinh', 0)}** commit cũ trước khi áp dụng trailer — hệ thống giữ nguyên không đoán). "
        "Hook `.githooks/commit-msg` (tương thích Windows, macOS và Linux) chặn mọi commit mới nếu thiếu dòng trailer `Cong-cu-AI:` hợp lệ (`tests/test_kiem_trailer_commit.py`).",
        co=11.0,
    )

    them_bang(
        doc,
        ["Ngày", "Commit", "Tóm tắt thay đổi (18 commit gần nhất trên nhánh main)", "Công cụ AI"],
        commits_gan_nhat,
        [0.85, 0.75, 3.85, 1.1],
        first_col_bold=False,
        font_size=8.6,
    )

    # =========================================================================
    # PHAN 4: KHONG DUA DU LIEU NHAN DANG VAO DICH VU / LOG TRAI PHEP
    # =========================================================================
    them_tieu_de_phan(doc, "4. Bảo vệ dữ liệu sức khỏe: Dịch vụ ngoài, Bộ che định danh và Log")

    them_tieu_de_muc(doc, "4.1. Danh sách toàn bộ 6 lối ra mạng của máy chủ Web")
    them_doan(
        doc,
        "Mọi lời gọi mạng ra ngoài đều tập trung trong danh sách `web/may-chu/loi-ra-mang.ts`; phép thử `loi-ra-mang.test.ts` tự động quét toàn bộ mã máy chủ và báo lỗi ngay nếu phát hiện lệnh `fetch` chưa khai báo. Phía Python cũng chỉ có một lối ra máy xa mặc định tắt (`tests/test_loi_ra_mang_python.py`).",
        co=10.8,
    )
    them_bang(
        doc,
        ["Đích kết nối", "Mục đích", "Dữ liệu đi ra và chốt kiểm soát", "Mặc định"],
        [
            ["Dịch vụ Python tại chỗ (`127.0.0.1:8765`)", "Chép lời, rút mệnh đề, K1–K7, dựng nháp", "Âm thanh và lời thoại ca khám; chỉ chạy nội bộ trong máy kèm khóa nội bộ", "Mở (nội bộ)"],
            ["Cổng mô hình ngoài AIBOX (`/chat/completions`)", "Tính năng phụ: sửa nháp / hỏi đáp", "Chỉ gửi văn bản ĐÃ CHE định danh; còn sót danh tính từ chối gửi (HTTP 422); cần quản trị và bác sĩ cùng bật", "**Tắt**"],
            ["Cổng mô hình ngoài AIBOX (`/models`)", "Kiểm tra tình trạng cổng", "Không mang dữ liệu ca khám (chỉ gửi khóa truy cập máy chủ)", "Mở (chỉ ping)"],
            ["API tài liệu (`PubMed / IRIS / openFDA`)", "Tra cứu tài liệu y khoa", "Từ khóa y khoa; từ chối (HTTP 422) nếu chứa tên, mã hoặc số liên lạc (`locTuKhoaCoDanhTinh`)", "Mở (đã lọc)"],
            ["Trang chính thống (`WHO/CDC/BYT/NICE/MSD`)", "Đọc nội dung tài liệu đối chiếu", "Chỉ địa chỉ URL trang tài liệu công khai", "Mở"],
            ["`www.aafp.org`", "Mở bài AAFP theo mã PubMed", "Chỉ mã PMID bài báo; không có dữ liệu ca khám", "Mở"],
        ],
        [1.65, 1.5, 2.55, 0.85],
        font_size=8.8,
    )

    them_tieu_de_muc(doc, "4.2. Kiểm định hai bộ che định danh trên PhoNER_COVID19 (Trước vá → Sau vá)")
    them_bang(
        doc,
        ["Bộ che định danh", "Trước vá (dev / test)", "Sau vá (dev / test)", "Đo lại 1.000 câu đầu (`da-nguon-doc-lap.json`)", "Che nhầm `ViMedAQA`"],
        [
            ["TypeScript (`an-danh-ngoai.ts`)", "7,3% / 7,5%", "**97,5%** / **94,0%** (2.183/2.323)", "— (kiểm qua bộ 45 ca rò rỉ chung `an-danh-chung.test.ts`)", "4/300 (**1,3%**)"],
            ["Python (`khu_dinh_danh.py`)", "1,5% / 0,8%", "**97,3%** / **93,8%** (2.178/2.323)", "Tăng từ **10/847 (1,2%)** → **775/847 (91,5%)**", "2→4/300 (**0,7–1,3%**)"],
        ],
        [1.45, 1.1, 1.35, 1.7, 0.95],
        font_size=8.8,
    )
    them_doan(
        doc,
        "Lưu ý trung thực: Tập test `PhoNER_COVID19` mới đạt 94,0% / 93,8% (chưa chạm ngưỡng 95%) vì còn sót tên riêng một tiếng đứng trơ như *\"Nhung\"*, *\"Oanh\"*, *\"Kim\"*. Đội không xem ca lọt của tập test để vá đuổi tránh học tủ; đồng thời vẫn giữ bộ luật che `MA_CA_BENH` (`BN416`), `TEN_VIET_TAT` (`bà H.T.P`) và bảo vệ không che nhầm *\"sốt từ thứ 2\"*, *\"viêm gan B.\"*, *\"Vitamin B.\"*, *\"Alsiful S.R\"*.",
        nghieng=True, co=10.2, mau=MAU_PHU,
    )

    them_tieu_de_muc(doc, "4.3. Kiểm soát log lỗi và vòng đời 11 nơi lưu dữ liệu")
    them_gach_dau_dong(
        doc,
        "**Che log trước khi cắt ngắn (`web/may-chu/che-log.ts`, `src/he_thong/che_log.py`):** Toàn bộ log lỗi máy chủ (kể cả thông báo lỗi do cổng ngoài dội lại) đều đi qua bộ che tên/SĐT/CCCD trước rồi mới cắt tối đa 300 ký tự để không cắt đôi số điện thoại; tên thủ thuật (`procedureName`) khi ghi `nhat_ky` cũng qua `cheLog`; thay `traceback.print_exc()` bằng tên lỗi và vị trí; phép thử `log-da-che.test.ts` quét toàn bộ mã để chặn dòng `console.error/warn` in biến lỗi thô.",
    )
    them_gach_dau_dong(
        doc,
        "**Kiểm soát lưu trữ 11 nơi trong `docs/minh-bach/so-do-du-lieu.md`:** Toàn bộ dữ liệu ca khám nằm trong SQLite nội bộ (lọc truy vấn theo `nguoi_dung_id`); bảng `worm_signoff` và `audit_log_worm.db` chỉ lưu mã băm, số đếm và người ký, tuyệt đối không lưu lời thoại; hàng đợi `viec_nen` tự dọn việc quá 30 phút.",
    )
    them_gach_dau_dong(
        doc,
        "**Tự xóa tệp ghi âm & dữ liệu trình duyệt:** `src/audio/storage.py` tự xóa tệp ghi âm gốc và bản 16 kHz sau **30 ngày** (ca đã duyệt và ca chờ duyệt) và **7 ngày** (phiên bỏ dở không lời thoại), kích hoạt khi `AudioPipeline` khởi tạo; trình duyệt xóa toàn bộ khóa `meditrace_*` trong `localStorage` khi đăng xuất, hết phiên `401` hoặc đổi tài khoản (`xoaDuLieuTrinhDuyet.ts`), và đã gỡ Google Fonts khỏi `web/index.html`.",
    )

    # =========================================================================
    # PHAN 5: SO DO DU LIEU & QUY TRINH PHE DUYET + ANH CHUP THAT
    # =========================================================================
    them_tieu_de_phan(doc, "5. Sơ đồ dữ liệu và quy trình bác sĩ phê duyệt trước khi dùng hồ sơ")

    them_tieu_de_muc(doc, "5.1. Luồng dữ liệu đầu – cuối")
    them_gach_dau_dong(
        doc,
        "**Luồng nội bộ tại phòng khám (mặc định):** Micro phòng khám → Trình duyệt bác sĩ → Máy chủ Web MediTrace (Node/Express) → Dịch vụ Python tại chỗ `127.0.0.1:8765` (PhoWhisper + Qwen3-4B + K1–K7) → SQLite tại chỗ (`ca_kham`, `ban_ky_duyet`, sổ WORM) và thư mục âm thanh nội bộ.",
    )
    them_gach_dau_dong(
        doc,
        "**Luồng bản demo công khai:** Người xem qua Cloudflare Worker/Tunnel chuyển tiếp TLS chỉ được nhập dữ liệu mô phỏng (có hộp cảnh báo ngay tại màn hình đăng nhập).",
    )
    them_gach_dau_dong(
        doc,
        "**Luồng ra ngoài có điều kiện:** Từ khóa y khoa sạch đi ra PubMed/WHO/openFDA; hoặc văn bản đã che đi ra AIBOX chỉ khi cả quản trị và bác sĩ chủ động bật.",
    )

    them_tieu_de_muc(doc, "5.2. Quy trình bác sĩ phê duyệt 2 tầng (Giao diện + Máy chủ)")
    them_bang(
        doc,
        ["Trạng thái hồ sơ", "Quy tắc khóa/mở trên giao diện và máy chủ", "Tệp cài đặt và kiểm chứng"],
        [
            ["1. Bản nháp mới", "Chỉ được xem; toàn bộ 12 nút xuất (Chép, In, PDF, `.txt`, `.md`, FHIR, SBAR, Chép HIS, Dặn dò, BHYT/XML, TT26, Cam đoan, Đi buồng) đều khóa.", "`choPhepDungHoSo.ts`, `loiRaHoSo.test.ts`"],
            ["2. Còn mục *Cần xác nhận*", "Nút ký hiển thị `Cần xác nhận (n)`, không cho ký; bấm vào sẽ cuộn tới đúng mệnh đề treo hoặc mệnh đề thiếu căn cứ lượt thoại.", "`kiemTraDieuKienKyDuyet`, `compileEffectiveNote.ts`, `quyTrinhPheDuyet.test.ts`"],
            ["3. Bác sĩ duyệt và Ký", "Bác sĩ chọn Giữ/Sửa/Bỏ từng mục rồi bấm Ký → Máy chủ tính SHA-256 + HMAC-SHA256 nối vào WORM và lưu bản chụp `ban_ky_duyet`.", "`worm.ts`, `sign-off.ts`, `kiem-ky-may-chu.ts`, `worm.test.ts`"],
            ["4. Hồ sơ được phép dùng", "Mở khóa 12 nút giao diện; khi gọi 6 API xuất (`tao-ma`, `bhyt/precheck`, `bhyt/recompile`, `fhir/recompile`, `informed-consent`, `ward-round-diff`), máy chủ đối chiếu `ban_ky_duyet` và kiểm IDOR (`403`).", "`kiem-ky-may-chu.test.ts`, `bhyt-ocr.test.ts`, `boost-lam-sang.test.ts`"],
            ["5. Sửa nội dung sau ký", "Băm nội dung hoặc quyết định duyệt thay đổi → tự động khóa lại ở cả giao diện lẫn máy chủ (`409 chua_ky_duyet` / `422 noi_dung_khac_ban_ky`), bắt ký lại.", "`isSignOffStale`, `quyTrinhPheDuyet.test.ts`, `kiem-ky-may-chu.test.ts`"],
        ],
        [1.35, 3.3, 1.9],
        font_size=9.0,
    )

    # 4 ANH CHUP GIAO DIEN THAT (KHUNG TRANG NHA, NEN TRANG)
    anh_list = [
        (ANH_DIR / "khoa-truoc-ky-1.jpg", "Hình 1. Chưa ký duyệt: toàn bộ nút chép, in và xuất hồ sơ bị khóa."),
        (ANH_DIR / "khoa-truoc-ky-2.jpg", "Hình 2. Đã ký duyệt WORM (#1): mở khóa các chức năng sử dụng hồ sơ."),
        (ANH_DIR / "khoa-truoc-ky-3.jpg", "Hình 3. Sửa nội dung sau khi ký: hệ thống tự khóa lại và yêu cầu ký lại."),
        (ANH_DIR / "thong-bao-ban-demo.jpg", "Hình 4. Cảnh báo bản demo công khai: chỉ nhập dữ liệu mô phỏng."),
    ]
    if all(p.exists() for p, _ in anh_list):
        them_tieu_de_muc(doc, "5.3. Ảnh chụp kiểm chứng trên giao diện thực tế")
        tbl_img = doc.add_table(rows=2, cols=2)
        tbl_img.alignment = WD_TABLE_ALIGNMENT.CENTER
        for idx, (img_path, caption) in enumerate(anh_list):
            cell = tbl_img.cell(idx // 2, idx % 2)
            cell.width = Inches(3.25)
            dat_vien_o(cell, top="single", bottom="single", left="single", right="single", sz="4", mau="CBD5E1")
            dat_le_o(cell, top=55, bottom=55, left=55, right=55)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(2)
            run_img = p.add_run()
            run_img.add_picture(str(img_path), width=Inches(3.05))
            pc = cell.add_paragraph()
            pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pc.paragraph_format.space_before = Pt(2)
            pc.paragraph_format.space_after = Pt(0)
            rc = pc.add_run(caption)
            dat_font_run(rc, PHONG_CHU, 9.0, nghieng=True, mau=MAU_PHU)
        them_doan(doc, "", cach_duoi=4)

    # =========================================================================
    # PHAN 6: GIOI HAN NOI THANG & KET QUA KIEM THU
    # =========================================================================
    them_tieu_de_phan(doc, "6. Giới hạn còn lại và kết quả kiểm thử xác minh")

    them_tieu_de_muc(doc, "6.1. Các giới hạn còn lại (trình bày thẳng thắn)")
    them_gach_dau_dong(doc, "**Bộ che định danh trên `PhoNER_COVID19` test:** Đạt `94,0%` (TypeScript) và `93,8%` (Python), chưa chạm ngưỡng `95%` do còn tên riêng một tiếng đứng trơ; nhóm không vá theo tập test để tránh học tủ.")
    them_gach_dau_dong(doc, "**Bản sao tạm trên trình duyệt:** `localStorage` xóa sạch khi đăng xuất, hết phiên `401` hoặc đổi tài khoản, nhưng nếu đóng tab mà không đăng xuất thì bản sao cục bộ trên máy đó chưa mã hóa.")
    them_gach_dau_dong(doc, "**Thao tác hệ điều hành trình duyệt:** Chưa chặn được bôi đen `Ctrl+C` khi đọc tại chỗ hoặc `Ctrl+P`, nên bản in chưa ký tự động mang dòng *\"BẢN NHÁP — CHƯA KÝ DUYỆT\"*.")
    them_gach_dau_dong(doc, "**Lịch sử cũ và giữ âm thanh demo:** `34` commit cũ trước khi áp dụng trailer giữ nguyên trạng thái `chua_xac_dinh`; chính sách tự xóa audio `30/30/7` ngày tạm nâng hạn trên máy chủ demo tới sau buổi thi để giữ âm thanh mẫu.")
    them_gach_dau_dong(doc, "**Thử nghiệm người dùng thật & LoRA ASR:** Chưa thử bấm giờ trên bác sĩ thật; adapter LoRA `PhoWhisper-small` trên `VNMed_Speech` (`WER ViMedCSS 0,3165 → 0,2610`) mới ở mức báo cáo thực nghiệm (`docs/ket-qua/asr-vnmed-lora.md`), chưa triển khai thay thế mô hình chính.")

    them_tieu_de_muc(doc, "6.2. Kết quả kiểm thử tự động xác minh")
    them_bang(
        doc,
        ["Nhóm kiểm thử", "Kết quả quan sát trực tiếp", "Phạm vi kiểm chứng"],
        [
            ["Nhóm test Đề 1 (Python, chạy lại 28/11)", "**69 passed, 0 failed** (1,75 giây)", "`test_minh_chung_trich_commit`, `test_truy_nguon_commit`, `test_kiem_trailer_commit`, `test_loi_ra_mang_python`, `test_ro_ri_dinh_danh_chung`, `test_che_log`"],
            ["Nhóm test Đề 1 (Web TS, chạy lại 28/11)", "**93 passed, 0 failed** (3,08 giây)", "`quyTrinhPheDuyet`, `choPhepDungHoSo`, `loiRaHoSo`, `kiem-ky-may-chu`, `worm`, `che-log`, `loi-ra-mang`, `an-danh-chung`, `llm-ngoai`, `tra-cuu`"],
            ["Toàn bộ hồi quy (`TRA_LOI_DE_CAI_TIEN_1.md`)", "**2.106 Python passed** (28 skip) · **214/214 Web TS passed**", "Đóng gói `npm run build` và kiểm kiểu `tsc --noEmit` (`npm run lint`) không có lỗi"],
        ],
        [2.0, 1.85, 2.7],
        font_size=9.0,
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
    print(f"Da xuat xong ban Word chuyen nghiep tai:\n-> {OUT_ROOT}\n-> {OUT_MINH_BACH}\n-> {OUT_TAI_LIEU}")


if __name__ == "__main__":
    tao_bao_cao()
