# -*- coding: utf-8 -*-
"""Xuất báo cáo Word (.docx) cho Đề cải tiến 1 (28/11/2026):
'Chứng minh làm chủ và bảo vệ dữ liệu sức khỏe'.

Phong cách văn bản hành chính – kỹ thuật gọn, dễ đọc:
- Phông Times New Roman thống nhất, mã/commit dùng Consolas
- Câu văn ngắn gọn, rõ ý, tránh nhồi chữ vào ô bảng
- Bảng biểu nền trắng, tiêu đề xám nhạt, đường kẻ ngang mảnh
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
OUT_DOWNLOADS_V2 = Path.home() / "Downloads" / "Bao_Cao_De_Cai_Tien_1_Ban_Chuyen_Nghiep.docx"

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


def them_vach_trai(p, mau_hex="94A3B8"):
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


def dat_le_o(cell, top=65, bottom=65, left=85, right=85):
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
    them_vach_trai(p)
    return p


def them_tieu_de_phan(doc, text):
    p = them_doan(doc, text, dam=True, co=13.0, mau=MAU_NHAN, cach_tren=14, cach_duoi=6, gian_dong=1.15)
    p.paragraph_format.keep_with_next = True
    them_duong_ke_duoi(p, mau_hex="94A3B8", sz="6")
    return p


def them_tieu_de_muc(doc, text):
    p = them_doan(doc, text, dam=True, co=11.8, mau=MAU_NHAN, cach_tren=9, cach_duoi=3, gian_dong=1.15)
    p.paragraph_format.keep_with_next = True
    return p


def them_bang(doc, headers, rows, col_widths_in, first_col_bold=True, font_size=9.5):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    for ci, h in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.width = Inches(col_widths_in[ci])
        dat_nen_o(cell, "F1F5F9")
        dat_vien_o(cell, top="single", bottom="single", left="none", right="none", sz="8", mau="334155")
        dat_le_o(cell, top=75, bottom=75, left=80, right=80)
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
            dat_le_o(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.15
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
    for b in blocks:
        body = "\n".join(b.splitlines()[1:])
        m = re.search(r"Cong-cu-AI:\s*([A-Za-z0-9_]+)", body)
        if m:
            cnt[m.group(1)] += 1
        elif "Co-Authored-By: Claude" in body:
            cnt["claude_code"] += 1
        else:
            cnt["chua_xac_dinh"] += 1
    head_short = blocks[0].split("|", 3)[1] if blocks else "main"
    return len(blocks), dict(cnt), head_short


def tao_bao_cao():
    tong_commit, dem_cong_cu, head_short = thong_ke_git_hien_tai()

    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(0.8)
        s.bottom_margin = Inches(0.8)
        s.left_margin = Inches(0.85)
        s.right_margin = Inches(0.85)
        s.page_width = Inches(8.27)
        s.page_height = Inches(11.69)

    them_header_footer(doc)

    # TIEU DE TRANG TRONG, NGAN GON
    them_doan(
        doc,
        "DỰ ÁN MEDITRACE SENTINEL — BÁO CÁO ĐÁP ỨNG ĐỀ CẢI TIẾN 1",
        dam=True, co=10.5, mau=MAU_PHU, can_le=WD_ALIGN_PARAGRAPH.CENTER, cach_duoi=4,
    )
    them_doan(
        doc,
        "CHỨNG MINH LÀM CHỦ CÔNG NGHỆ VÀ BẢO VỆ DỮ LIỆU SỨC KHỎE",
        dam=True, co=15.0, mau=MAU_NHAN, can_le=WD_ALIGN_PARAGRAPH.CENTER, cach_duoi=4,
    )
    p_sub = them_doan(
        doc,
        f"Ngày nhận đề: 28/11/2026  |  Nhánh main (commit {head_short})  |  Đội thực hiện: MediTrace",
        nghieng=True, co=10.0, mau=MAU_PHU, can_le=WD_ALIGN_PARAGRAPH.CENTER, cach_duoi=10,
    )
    them_duong_ke_duoi(p_sub, mau_hex="1E293B", sz="10")

    them_trich_dan(
        doc,
        "**Yêu cầu của đề:** Minh bạch quá trình dùng AI khi phát triển sản phẩm và phạm vi xử lý thông tin bệnh nhân; "
        "trình bày quyết định thiết kế, phần AI hỗ trợ và phần đội tự đánh giá/sửa; không đưa dữ liệu nhận dạng vào dịch vụ hay log trái phép. "
        "Minh chứng gồm lịch sử sửa đổi, sơ đồ dữ liệu và quy trình bác sĩ phê duyệt trước khi dùng hồ sơ.",
    )

    them_doan(doc, "**Hai điểm nhóm tác giả xác nhận rõ (28/11/2026):**", cach_tren=4, cach_duoi=2)
    them_gach_dau_dong(
        doc,
        "**Chưa từng đưa hồ sơ bệnh nhân thật vào bất kỳ công cụ AI nào.** Trong quá trình phát triển và kiểm thử, nhóm chỉ dùng dữ liệu mô phỏng và các bộ dữ liệu công khai hợp lệ.",
    )
    them_gach_dau_dong(
        doc,
        "**Cổng AI bên ngoài (AIBOX) chỉ là tính năng phụ của bên thứ ba.** Tính năng này mặc định tắt ở cả quản trị lẫn màn hình bác sĩ, và chỉ gửi văn bản đã xóa thông tin cá nhân.",
    )

    # BANG DOI CHIEU NGAN GON
    them_tieu_de_phan(doc, "Tóm tắt đối chiếu với yêu cầu của Ban Giám khảo")
    them_bang(
        doc,
        ["Yêu cầu", "Cách MediTrace giải quyết", "Minh chứng kiểm tra được"],
        [
            ["1. Quyết định thiết kế", "Ghi rõ 13 quyết định cốt lõi: vì sao chọn cách này, ai quyết và tệp nào thực hiện.", "`so-quyet-dinh-thiet-ke.md`, `test_minh_chung_trich_commit.py`"],
            ["2. AI hỗ trợ & Đội tự sửa", "Ghi rõ AI viết phần nào, đội kiểm/bác bỏ/sửa lại lỗi gì qua từng đợt rà soát.", "`ai-ho-tro-va-doi-tu-sua.md`, `nhat-ky-hackathon.md`"],
            ["3. Lịch sử sửa đổi", f"Thống kê {tong_commit} commit theo công cụ AI; tự động chặn commit mới nếu thiếu ghi chú công cụ.", "`tools/truy_nguon_commit.py`, `.githooks/commit-msg`"],
            ["4. Không lộ dữ liệu ra ngoài", "Lõi AI chạy tại chỗ; mọi kết nối mạng phải khai báo vào một danh sách; che tên/SĐT/mã bệnh nhân trước khi ra cổng phụ.", "`loi-ra-mang.ts`, `an-danh-ngoai.ts`, `khu_dinh_danh.py`"],
            ["5. Không lộ dữ liệu vào log", "Che tên và số điện thoại trước khi cắt ngắn log lỗi; tự xóa tệp ghi âm sau 30/30/7 ngày; gỡ Google Fonts.", "`che-log.ts`, `che_log.py`, `storage.py`, `khongTaiNguonNgoai.test.ts`"],
            ["6. Sơ đồ & Phê duyệt hồ sơ", "Sơ đồ dữ liệu sinh từ mã; khóa 12 nút xuất và 6 API máy chủ cho tới khi bác sĩ duyệt hết mục nghi ngờ và bấm ký.", "`so-do-du-lieu.md`, `choPhepDungHoSo.ts`, `kiem-ky-may-chu.ts`, `worm.ts`"],
        ],
        [1.45, 3.05, 2.05],
        font_size=9.3,
    )

    # =========================================================================
    # MUC 1: QUYET DINH THIET KE
    # =========================================================================
    them_tieu_de_phan(doc, "1. Các quyết định thiết kế cốt lõi")
    them_doan(
        doc,
        "Bảng dưới tóm tắt 13 quyết định thiết kế chính của đội (`docs/minh-bach/so-quyet-dinh-thiet-ke.md`), "
        "trả lời rõ vì sao đội chọn phương án này thay vì cách làm phổ biến hơn.",
        co=11.0,
    )

    them_bang(
        doc,
        ["Nhóm quyết định", "Phương án chọn & Lý do", "Bằng chứng"],
        [
            ["1. Tách AI và Luật\n(QĐ 1)", "Chỉ để `Qwen3-4B` nhặt từng ý nhỏ kèm câu trích ở Bước 1; các bước ghép người, xử lý đính chính và kiểm căn cứ K1–K7 viết bằng luật cố định để dễ truy lỗi và tránh trộn bệnh của người nhà.", "`chay_duong_ong.py`, `b4_kiem_can_cu.py`"],
            ["2. Chạy tại chỗ & Khóa lối ra\n(QĐ 2–4)", "Chạy lõi ngay trên máy nội bộ; cổng AI ngoài (AIBOX) mặc định tắt ở 2 lớp; tự xóa ghi âm sau 30 ngày (đã duyệt/chờ duyệt) hoặc 7 ngày (bỏ dở); gỡ Google Fonts để không lộ IP.", "`loi-ra-mang.ts`, `8b752da`, `fb6ef97`, `storage.py`"],
            ["3. Phê duyệt 2 tầng\n(QĐ 5–6)", "Khóa toàn bộ nút xuất trên giao diện và 6 API trên máy chủ cho tới khi bác sĩ duyệt xong và ký; sửa 1 chữ sau ký tự khóa lại. Bảng thuốc tham khảo giữ nhãn chưa duyệt để bác sĩ tự đối chiếu.", "`f111b14`, `a555bdc`, `kiem-ky-may-chu.ts`, `tri_thuc_thuoc.json`"],
            ["4. Kỷ luật dữ liệu & Độ tin cậy\n(QĐ 7–10)", "Chưa đưa mô hình mới (`v3`, `DPO`) vào chạy chính vì `v3` bỏ sót nhiều hơn `v1` (14,1% so với 11,8%) và `DPO` làm tụt điểm câu đúng. Không train bằng dữ liệu do GPT tạo; chỉ thử nghiệm `PhoWhisper-small` trên `VNMed_Speech` (CC BY 4.0) và giữ các bộ ngoài làm bài thi độc lập.", "`dpo-v3.md`, `90687ad`, `asr-vnmed-lora.md`, `1553a4f`"],
            ["5. Chống học vẹt & Hứa suông\n(QĐ 11–13)", "Tập kiểm tra giữ kín 240 ca chỉ chạy đúng 1 lần; ghi rõ tỷ lệ 11,8% là đo trên tập phát triển; không hứa hẹn 'tiết kiệm X% thời gian' khi chưa bấm giờ trên bác sĩ thật.", "`cay-loi.md`, `2fc4eba`, `7acd457`"],
        ],
        [1.35, 3.65, 1.55],
        font_size=9.2,
    )

    # =========================================================================
    # MUC 2: AI HO TRO VA DOI TU SUA
    # =========================================================================
    them_tieu_de_phan(doc, "2. Phần AI hỗ trợ và phần đội tự kiểm tra, sửa lỗi")

    them_tieu_de_muc(doc, "2.1. Phân công giữa AI và đội phát triển")
    them_bang(
        doc,
        ["Hạng mục", "AI hỗ trợ viết mã", "Đội tự làm và kiểm chứng", "Công cụ chính"],
        [
            ["Sinh dữ liệu mẫu", "Viết code sinh hội thoại và biến thể câu", "Thiết kế 657 khuôn bệnh, tách tập theo khuôn để tránh rò rỉ dữ liệu", "Claude Code, Antigravity"],
            ["Huấn luyện mô hình", "Viết code huấn luyện QLoRA, DPO, LoRA ASR", "Chạy thực nghiệm, kiểm tra trùng lặp, loại bỏ bản DPO kém ổn định", "Claude Code"],
            ["Luật kiểm căn cứ & Cảnh báo", "Viết khung luật K1–K7 và bộ bắt lỗi", "Đặt quy tắc lâm sàng, khóa ngữ cảnh y khoa, chạy kiểm chứng độc lập", "Claude Code, Antigravity"],
            ["Giao diện & Máy chủ", "Viết màn hình React và API Express", "Tự bấm kiểm tra từng trạng thái, bỏ bớt nút thừa, chặn lỗ hổng phía máy chủ", "Claude Code, Antigravity"],
            ["Đo lường & Báo cáo", "Viết kịch bản chạy đo và tổng hợp bảng", "Đối chiếu từng số liệu với log thật, xóa các bảng cũ thiếu căn cứ", "Claude Code, Antigravity"],
        ],
        [1.3, 1.7, 2.25, 1.3],
        font_size=9.1,
    )

    them_tieu_de_muc(doc, "2.2. Các lần đội tự phát hiện sai sót và sửa lại đầu ra của AI")
    them_bang(
        doc,
        ["Đợt kiểm tra", "Lỗi phát hiện từ mã/tài liệu do AI sinh", "Cách đội sửa và xác nhận lại"],
        [
            ["Rà mã sau commit `8120ce4`", "Chữ *\"mi\"* (mí mắt) bị đổi nhầm thành *\"mày\"*; số ngày *\"ho 3 ngày\"* bị báo nhầm là sai liều thuốc.", "Sửa ngay tại `2fc4eba` và ghi rõ bối cảnh số liệu tập phát triển."],
            ["Rà soát độc lập 26/11", "Lỗi so liều (`5 mg` khớp nhầm `2.5 mg`); mặc định tuổi bằng 50 khi thiếu; gán nhầm thuốc `Sintrom` thành `warfarin`.", "Sửa dứt điểm từng lỗi và viết phép thử khóa hồi quy (`f14a490`, `d1a6cb6`, `e9a1866`)."],
            ["Rà soát lộ dữ liệu & khóa xuất", "4 nút BHYT/TT26/Cam đoan/Đi buồng vẫn xuất được khi chưa ký; log lỗi còn in thô hoặc cắt chuỗi trước khi che; từ khóa tìm tài liệu có thể chứa tên người.", "Viết phép thử tái hiện lỗi trước rồi mới sửa (`2f41851`, `b4b3633`, `a555bdc`); khóa đủ 6 API ở máy chủ."],
            ["Rà soát số liệu báo cáo", "Một số bảng cũ (so sánh GPT-4o/Claude/Gemini, con số *\"78,3% đa dạng\"*) không có tệp kết quả đối chứng.", "Rút bỏ hoàn toàn khỏi báo cáo, chỉ giữ số chạy lại được (`doi-chieu-so-lieu-bao-cao.md`)."],
        ],
        [1.45, 2.8, 2.3],
        font_size=9.1,
    )

    # =========================================================================
    # MUC 3: LICH SU GIT
    # =========================================================================
    them_tieu_de_phan(doc, "3. Lịch sử sửa đổi Git và truy nguồn công cụ AI")
    them_doan(
        doc,
        f"Nhánh `main` hiện có **{tong_commit} commit** (tính tới `{head_short}`): `claude_code` ({dem_cong_cu.get('claude_code', 0)}), "
        f"`antigravity` ({dem_cong_cu.get('antigravity', 0)}), `codex` ({dem_cong_cu.get('codex', 0)}) và {dem_cong_cu.get('chua_xac_dinh', 0)} commit cũ "
        "trước khi áp dụng quy ước ghi công cụ (để nguyên `chua_xac_dinh`, không đoán). "
        "Mọi commit mới đều bị hook `.githooks/commit-msg` chặn lại nếu thiếu dòng `Cong-cu-AI:` hợp lệ.",
        co=11.0,
    )

    them_bang(
        doc,
        ["Ngày", "Commit", "Nội dung chính của các mốc sửa đổi tiêu biểu", "Công cụ"],
        [
            ["2026-11-28", "`06a1caa` / `e06236c`", "Hiển thị rõ dữ liệu ca đang dùng cho trợ lý; đồng bộ tài liệu Đề cải tiến 1", "`antigravity` / `claude_code`"],
            ["2026-11-28", "`90687ad`", "Thử nghiệm LoRA `PhoWhisper-small` trên `VNMed_Speech` (WER giảm 0,3165 → 0,2610, kiểm rò rỉ 0/0)", "`claude_code`"],
            ["2026-11-28", "`b4b3633`", "Vá theo rà soát độc lập: che log trước khi cắt, che tên viết thường, lọc từ khóa tra cứu", "`claude_code`"],
            ["2026-11-28", "`a555bdc` / `2f41851`", "Khóa máy chủ cho 6 API xuất hồ sơ qua bản chụp lúc ký; che tên thủ thuật trong nhật ký", "`claude_code`"],
            ["2026-11-28", "`a4fb3d6`", "Nâng cấp bộ che định danh cho mã ca bệnh và tên viết tắt (Python + TypeScript)", "`claude_code`"],
            ["2026-11-28", "`8b752da` / `054c8b3`", "Tắt mặc định cổng AI bên thứ ba ở 2 lớp; che log lỗi và chặn tên người trong ô tìm PubMed", "`claude_code`"],
            ["2026-11-28", "`9f290d2` / `f111b14`", "Bật hook truy nguồn commit theo công cụ AI; khóa 12 nút xuất khi bác sĩ chưa ký", "`claude_code`"],
            ["2026-11-27", "`2fc4eba` / `1878711`", "Sửa lỗi phương ngữ/liều thuốc và quy hoạch mã nguồn `src/` thành 6 gói rõ ràng", "`claude_code` / `chua_xac_dinh`"],
        ],
        [0.85, 1.05, 3.6, 1.05],
        first_col_bold=False,
        font_size=8.8,
    )

    # =========================================================================
    # MUC 4: BAO VE DU LIEU SUC KHOE & LOG
    # =========================================================================
    them_tieu_de_phan(doc, "4. Bảo vệ dữ liệu bệnh nhân: Kết nối ngoài, Bộ che định danh và Log")

    them_tieu_de_muc(doc, "4.1. Kiểm soát toàn bộ 6 kết nối mạng của máy chủ")
    them_doan(
        doc,
        "Tất cả lệnh gọi mạng trong máy chủ đều phải khai báo tại `web/may-chu/loi-ra-mang.ts`. Nếu lập trình viên thêm lệnh gọi mới mà không khai báo, bộ test tự động sẽ báo lỗi ngay.",
        co=10.8,
    )
    them_bang(
        doc,
        ["Đích kết nối", "Mục đích", "Cách bảo vệ dữ liệu", "Mặc định"],
        [
            ["Dịch vụ Python tại chỗ (`127.0.0.1:8765`)", "Gỡ băng, rút ý và kiểm K1–K7", "Chạy ngay trên cùng máy bệnh viện, dùng khóa nội bộ", "Mở (nội bộ)"],
            ["Cổng AI ngoài AIBOX (`/chat/completions`)", "Hỏi đáp / sửa nháp phụ trợ", "Chỉ gửi văn bản đã che tên/SĐT/mã; sót danh tính từ chối ngay", "**Tắt**"],
            ["Cổng AI ngoài AIBOX (`/models`)", "Kiểm tra cổng còn hoạt động", "Chỉ gửi khóa kết nối, không có bất kỳ dữ liệu bệnh nhân nào", "Mở (chỉ ping)"],
            ["Kho tài liệu y khoa (`PubMed / IRIS / openFDA`)", "Tìm bài báo tham khảo", "Chỉ gửi từ khóa y khoa; chặn ngay nếu từ khóa chứa tên hoặc SĐT", "Mở (đã lọc)"],
            ["Trang y khoa chính thống (`WHO / CDC / BYT`)", "Đọc phác đồ đối chiếu", "Chỉ mở địa chỉ bài viết công khai", "Mở"],
            ["`www.aafp.org`", "Mở bài báo theo mã PubMed", "Chỉ gửi mã bài báo khoa học", "Mở"],
        ],
        [1.75, 1.55, 2.45, 0.8],
        font_size=8.9,
    )

    them_tieu_de_muc(doc, "4.2. Kết quả kiểm tra bộ che định danh trên PhoNER_COVID19 (Trước và sau khi vá)")
    them_bang(
        doc,
        ["Bộ che định danh", "Trước khi vá (dev / test)", "Sau khi vá (dev / test)", "Đo trên 1.000 câu đầu", "Che nhầm câu y khoa (`ViMedAQA`)"],
        [
            ["TypeScript (cổng web)", "7,3% / 7,5%", "**97,5%** / **94,0%**", "— (khớp 45/45 ca rò rỉ chung)", "4/300 (**1,3%**)"],
            ["Python (cổng dịch vụ)", "1,5% / 0,8%", "**97,3%** / **93,8%**", "**1,2% → 91,5%** (775/847)", "2→4/300 (**0,7–1,3%**)"],
        ],
        [1.45, 1.15, 1.35, 1.5, 1.1],
        font_size=8.9,
    )
    them_doan(
        doc,
        "Ghi chú: Bộ test `PhoNER_COVID19` hiện còn sót ~6% (chủ yếu là tên 1 tiếng đứng riêng như *\"Nhung\"*, *\"Oanh\"*, *\"Kim\"*). "
        "Đội không vá đuổi theo tập kiểm tra để tránh học vẹt, đồng thời giữ quy tắc không che nhầm chữ thông dụng như *\"sốt từ thứ 2\"*, *\"viêm gan B.\"*, *\"Vitamin B.\"*. ",
        nghieng=True, co=10.2, mau=MAU_PHU,
    )

    them_tieu_de_muc(doc, "4.3. Kiểm soát log lỗi và lưu trữ dữ liệu")
    them_gach_dau_dong(doc, "**Che log trước khi cắt ngắn:** Mọi thông báo lỗi đều được che tên, số điện thoại, CCCD trước rồi mới cắt tối đa 300 ký tự để tránh cắt đôi số điện thoại (`che-log.ts`, `che_log.py`).")
    them_gach_dau_dong(doc, "**Sổ ký duyệt không lưu lời thoại:** Các bảng nhật ký WORM chỉ ghi mã băm, số lượng mục và người ký; bảng `ca_kham` luôn lọc theo đúng bác sĩ sở hữu ca.")
    them_gach_dau_dong(doc, "**Tự dọn dữ liệu tạm:** Tệp ghi âm gốc tự xóa sau 30 ngày (ca đã duyệt/chờ duyệt) hoặc 7 ngày (phiên bỏ dở không lời thoại); bộ nhớ tạm trình duyệt (`localStorage`) tự xóa sạch khi bác sĩ đăng xuất hoặc đổi tài khoản.")

    # =========================================================================
    # MUC 5: SO DO DU LIEU & QUY TRINH PHE DUYET
    # =========================================================================
    them_tieu_de_phan(doc, "5. Sơ đồ dữ liệu và quy trình bác sĩ phê duyệt trước khi dùng hồ sơ")

    them_tieu_de_muc(doc, "5.1. Đường đi của dữ liệu trong hệ thống")
    them_gach_dau_dong(doc, "**Trong phòng khám (luồng chính):** Micro → Trình duyệt bác sĩ → Máy chủ Web → Dịch vụ AI Python tại chỗ (`127.0.0.1:8765`) → Lưu tại SQLite và thư mục âm thanh nội bộ.")
    them_gach_dau_dong(doc, "**Trên bản demo công khai:** Đi qua Cloudflare Worker chuyển tiếp; màn hình đăng nhập ghi rõ chỉ được nhập dữ liệu mô phỏng.")
    them_gach_dau_dong(doc, "**Khi ra ngoài mạng:** Chỉ cho phép gửi từ khóa y khoa đã lọc danh tính tới PubMed/WHO/openFDA, hoặc văn bản đã che tới AIBOX khi được bật chủ động.")

    them_tieu_de_muc(doc, "5.2. Quy trình bác sĩ phê duyệt 2 tầng (Giao diện + Máy chủ)")
    them_bang(
        doc,
        ["Giai đoạn", "Quy định hiển thị và chặn xuất hồ sơ", "Nơi kiểm soát"],
        [
            ["1. Bản nháp mới", "Chỉ cho xem; toàn bộ 12 nút chép, in, tải PDF, xuất BHYT/FHIR/HIS/SBAR đều bị khóa.", "`choPhepDungHoSo.ts`, `loiRaHoSo.test.ts`"],
            ["2. Còn mục nghi ngờ", "Nút ký báo `Cần xác nhận (n)` và không cho ký cho tới khi bác sĩ chọn Giữ, Sửa hoặc Bỏ hết các mục treo.", "`compileEffectiveNote.ts`, `quyTrinhPheDuyet.test.ts`"],
            ["3. Bác sĩ bấm Ký", "Máy chủ kiểm tra đủ điều kiện, tính mã băm SHA-256 + HMAC lưu vào sổ WORM và chụp lại bản đã ký (`ban_ky_duyet`).", "`worm.ts`, `sign-off.ts`, `kiem-ky-may-chu.ts`"],
            ["4. Mở khóa xuất hồ sơ", "Giao diện mở 12 nút; khi gọi 6 API xuất hồ sơ, máy chủ đối chiếu lại đúng bản chụp lúc ký và kiểm tra đúng chủ sở hữu.", "`kiem-ky-may-chu.test.ts`, `bhyt-ocr.test.ts`"],
            ["5. Sửa nội dung sau ký", "Chỉ cần sửa 1 chữ hoặc đổi quyết định duyệt, cả giao diện lẫn máy chủ lập tức khóa lại và yêu cầu ký lại.", "`isSignOffStale`, `kiem-ky-may-chu.test.ts`"],
        ],
        [1.35, 3.35, 1.85],
        font_size=9.2,
    )

    anh_list = [
        (ANH_DIR / "khoa-truoc-ky-1.jpg", "Hình 1. Chưa ký: các nút chép, in, xuất hồ sơ bị khóa."),
        (ANH_DIR / "khoa-truoc-ky-2.jpg", "Hình 2. Đã ký (#1): mở khóa sử dụng hồ sơ."),
        (ANH_DIR / "khoa-truoc-ky-3.jpg", "Hình 3. Sửa sau khi ký: tự khóa lại và đòi ký lại."),
        (ANH_DIR / "thong-bao-ban-demo.jpg", "Hình 4. Cảnh báo bản demo chỉ dùng dữ liệu mô phỏng."),
    ]
    if all(p.exists() for p, _ in anh_list):
        them_tieu_de_muc(doc, "5.3. Ảnh chụp kiểm chứng trên giao diện thật")
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
            p.add_run().add_picture(str(img_path), width=Inches(3.05))
            pc = cell.add_paragraph()
            pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
            pc.paragraph_format.space_before = Pt(2)
            pc.paragraph_format.space_after = Pt(0)
            rc = pc.add_run(caption)
            dat_font_run(rc, PHONG_CHU, 9.0, nghieng=True, mau=MAU_PHU)
        them_doan(doc, "", cach_duoi=4)

    # =========================================================================
    # MUC 6: GIOI HAN VA KIEM THU
    # =========================================================================
    them_tieu_de_phan(doc, "6. Giới hạn còn lại và kết quả kiểm thử")

    them_tieu_de_muc(doc, "6.1. Những điểm chưa làm được (nêu thẳng)")
    them_gach_dau_dong(doc, "**Bộ che định danh trên `PhoNER_COVID19` test:** Đạt 94,0% (web) và 93,8% (Python), chưa đạt 95% vì còn sót tên riêng 1 tiếng đứng trơ.")
    them_gach_dau_dong(doc, "**Bộ nhớ tạm trình duyệt:** `localStorage` xóa khi đăng xuất hoặc hết phiên, nhưng nếu người dùng đóng tab ngang mà chưa đăng xuất thì dữ liệu tạm trên máy đó chưa mã hóa.")
    them_gach_dau_dong(doc, "**Sao chép thủ công trên trình duyệt:** Chưa chặn được thao tác bôi đen Ctrl+C hoặc phím Ctrl+P, nên bản in khi chưa ký tự chèn dòng chữ *\"BẢN NHÁP — CHƯA KÝ DUYỆT\"*.")
    them_gach_dau_dong(doc, "**Lịch sử cũ & Âm thanh bản demo:** 34 commit cũ giữ trạng thái chưa xác định công cụ; riêng máy chủ demo tạm nâng hạn xóa âm thanh tới sau buổi thi để giữ 8 ca mẫu.")
    them_gach_dau_dong(doc, "**Thử nghiệm trên bác sĩ thật & ASR LoRA:** Chưa đo thực nghiệm bấm giờ trên bác sĩ lâm sàng; bản LoRA `PhoWhisper-small` trên `VNMed_Speech` mới là thử nghiệm (`asr-vnmed-lora.md`), chưa thay vào bản chạy chính.")

    them_tieu_de_muc(doc, "6.2. Kết quả kiểm thử xác minh")
    them_bang(
        doc,
        ["Nhóm kiểm thử", "Kết quả", "Nội dung kiểm tra"],
        [
            ["Nhóm test Đề 1 (Python, chạy 28/11)", "**69 passed, 0 failed** (1,75s)", "Trích dẫn commit, hook git, lối ra mạng, che định danh chung, che log"],
            ["Nhóm test Đề 1 (Web TS, chạy 28/11)", "**93 passed, 0 failed** (3,08s)", "Phê duyệt 2 tầng, khóa 6 API, WORM HMAC, che log, danh sách lối ra mạng, lọc PubMed"],
            ["Hồi quy toàn hệ thống (`TRA_LOI_DE_CAI_TIEN_1.md`)", "**2.106 Python passed** (28 skip) · **214/214 Web TS**", "Kiểm kiểu TypeScript (`npm run lint`) và đóng gói (`npm run build`) sạch lỗi"],
        ],
        [2.05, 1.8, 2.7],
        font_size=9.1,
    )

    for out_path in (OUT_ROOT, OUT_MINH_BACH, OUT_TAI_LIEU, OUT_DOWNLOADS_V2):
        try:
            doc.save(str(out_path))
        except Exception as e:
            print(f"Luu {out_path.name}: {e}")
    for folder in ("Downloads", "Desktop"):
        try:
            doc.save(str(Path.home() / folder / OUT_ROOT.name))
        except Exception as e:
            print(f"Luu {folder}: {e}")
    print(f"Da xuat xong ban Word gon, de hieu tai:\n-> {OUT_ROOT}\n-> {OUT_DOWNLOADS_V2}")


if __name__ == "__main__":
    tao_bao_cao()
