# -*- coding: utf-8 -*-
"""Ve so do truc quan so sanh kien truc cac nhanh A, B, C, C_khoa, D (Ablation Study).

Chay:
    python tools/ve_so_do_so_sanh_nhanh.py
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

GOC = Path(__file__).resolve().parent.parent
RA_DOCS = GOC / "docs" / "tai-lieu" / "hinh"
RA_DOCS.mkdir(parents=True, exist_ok=True)
RA_ARTIFACT = Path(r"C:\Users\admin\.gemini\antigravity-ide\brain\7c585094-b290-4263-a215-a9f3a6adf27b\images")
RA_ARTIFACT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.family": "Segoe UI",
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})

# Mau sac chuan
C_BG = "#F8FAFC"
C_TEXT_MAIN = "#0F172A"
C_TEXT_MUTED = "#475569"

C_AI = "#0D5C54"          # Xanh mong ket (AI Model)
C_AI_BG = "#E6F4F1"
C_RULE = "#1E3A5F"        # Xanh Navy (Chuong trinh luat)
C_RULE_BG = "#F1F5F9"
C_SAFE = "#059669"        # Xanh la (Qua / Da kiem chung)
C_SAFE_BG = "#ECFDF5"
C_WARN = "#D97706"        # Vang ho phach (Canh bao / Nguy co cao)
C_WARN_BG = "#FFFBEB"
C_DANGER = "#DC2626"      # Do (Chan / Vi pham)
C_DANGER_BG = "#FEF2F2"
C_PURPLE = "#4F46E5"      # Tim (Interactive / Hoi lai)
C_PURPLE_BG = "#EEF2FF"

def hop(ax, x, y, w, h, tieu_de, noi_dung="", vien="#CBD5E1", nen="white",
        co_td=10, co_nd=8.5, mau_td=C_TEXT_MAIN, mau_nd=C_TEXT_MUTED, dam=True, can="left"):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.07",
                           linewidth=1.3, edgecolor=vien, facecolor=nen)
    ax.add_patch(patch)
    if noi_dung:
        ax.text(x + w/2 if can=="center" else x + 0.15, y + h - 0.22, tieu_de,
                ha=can, va="top", fontsize=co_td, fontweight="bold" if dam else "normal",
                color=mau_td)
        ax.text(x + w/2 if can=="center" else x + 0.15, y + 0.18, noi_dung,
                ha=can, va="bottom", fontsize=co_nd, color=mau_nd, linespacing=1.2)
    else:
        ax.text(x + w/2, y + h/2, tieu_de, ha="center", va="center",
                fontsize=co_td, fontweight="bold" if dam else "normal", color=mau_td, linespacing=1.2)

def mui_ten(ax, x1, y1, x2, y2, mau="#94A3B8", day=1.5):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=14, linewidth=day, color=mau))

def ve_so_sanh_nhanh():
    fig, ax = plt.subplots(figsize=(19, 14.5), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19)
    ax.set_ylim(0, 14.5)
    ax.axis("off")

    # ========================== 1. TIEU DE CHINH ==========================
    ax.text(9.5, 14.0, "SO SÁNH KIẾN TRÚC CÁC NHÁNH THỬ NGHIỆM & BÓC TÁCH (ABLATION STUDY)",
            ha="center", va="center", fontsize=15.5, fontweight="bold", color=C_TEXT_MAIN)
    ax.text(9.5, 13.62, "Chứng minh giá trị an toàn vượt trội của rào chắn cấu trúc so với mô hình sinh tự do và tự soát lỗi (Self-Review)",
            ha="center", va="center", fontsize=10.5, color=C_TEXT_MUTED)

    # ========================== 2. SÁU NHÁNH THỬ NGHIỆM ==========================
    cac_nhanh = [
        # (Y_start, Tên nhánh, Subtitle, Màu viền, Màu nền, Flow modules list)
        (11.8, "NHÁNH A (Baseline)", "Mô hình sinh thẳng văn xuôi\n(Cách làm thông thường)",
         "#64748B", "#F1F5F9",
         [("Hội thoại khám", "Âm thanh / Văn bản", C_RULE),
          ("Mô hình AI (Qwen3-4B)", "Viết thẳng cả đoạn văn xuôi", C_AI),
          ("Bản nháp bệnh án", "Câu trôi chảy, không truy vết (Wrong-subject 12.4%)", "#64748B")]),

        (9.9, "NHÁNH A+ (Self-Review)", "Sinh thẳng + Tự kiểm tra lại\n(\"Check your answer\" prompt)",
         "#D97706", "#FFFBEB",
         [("Hội thoại khám", "Âm thanh / Văn bản", C_RULE),
          ("Mô hình AI sinh nháp", "Tạo bản nháp ban đầu", C_AI),
          ("Prompt: Tự soát lỗi AI", "\"Check for hallucinations & errors\"", C_WARN),
          ("Bản nháp sau tự soát", "Vẫn bị mù cấu trúc (Wrong-subject 9.8%, lọt lỗi)", C_WARN)]),

        (8.0, "NHÁNH B", "Trích mệnh đề AI +\nGhép bệnh án bằng luật",
         C_RULE, C_RULE_BG,
         [("Hội thoại khám", "Âm thanh / Văn bản", C_RULE),
          ("Rút mệnh đề (Tầng 1)", "AI trích JSON + câu trích", C_AI),
          ("Ghép theo luật mẫu câu", "Xếp vào các mục cố định", C_RULE),
          ("Bản nháp có trích dẫn", "Bắt đầu truy vết được từng câu nói", C_RULE)]),

        (6.1, "NHÁNH C", "Nhánh B + Gom người (T2)\n+ Cập nhật trạng thái (T3)",
         C_RULE, C_RULE_BG,
         [("Hội thoại khám", "Âm thanh / Văn bản", C_RULE),
          ("Rút mệnh đề (Tầng 1)", "AI trích JSON + câu trích", C_AI),
          ("Gom người (Tầng 2)", "Bệnh nhân vs Người nhà", C_RULE),
          ("Cập nhật (Tầng 3)", "Bắt tự sửa & mâu thuẫn", C_RULE),
          ("Bản nháp đúng người", "Lỗi tự sửa giảm từ 11.5% -> 0.8%", C_RULE)]),

        (4.2, "NHÁNH C_KHOÁ (Chính)", "Nhánh C + Khóa bằng chứng (T4)\n+ Cổng rủi ro & Xếp chỗ (T5)",
         C_DANGER, C_DANGER_BG,
         [("Hội thoại khám", "Âm thanh / Văn bản", C_RULE),
          ("Rút mệnh đề (T1)", "AI trích JSON", C_AI),
          ("Gom người & Cập nhật (T2-T3)", "Đúng chủ thể, đúng diễn biến", C_RULE),
          ("Khóa bằng chứng (T4)", "7 cổng K1-K7 (chặn K7 superseded)", C_DANGER),
          ("Cổng rủi ro (T5)", "Wrong-subject giảm còn 2.1%, False-block <= 1%", C_SAFE)]),

        (2.3, "NHÁNH D (C_khoa_hoi)", "Nhánh C_khoá +\nHỏi lại bác sĩ (Khâu 6)",
         C_PURPLE, C_PURPLE_BG,
         [("Hội thoại khám", "Âm thanh / Văn bản", C_RULE),
          ("Pipeline 5 tầng", "Tầng 1 -> Tầng 2 -> Tầng 3 -> Tầng 4 -> Tầng 5", C_SAFE),
          ("Hỏi lại bác sĩ (Khâu 6)", "Gợi ý tối đa 3 câu hỏi làm rõ mâu thuẫn", C_PURPLE),
          ("Bệnh án hoàn chỉnh", "An toàn lâm sàng và độ chính xác cao nhất", C_PURPLE)]),
    ]

    for y, ten_nhanh, mo_ta, vien_nhanh, nen_nhanh, buoc_list in cac_nhanh:
        # Khung tên nhánh bên trái
        hop(ax, 0.5, y, 3.6, 1.45, ten_nhanh, mo_ta, vien=vien_nhanh, nen=nen_nhanh,
            co_td=10.0, co_nd=8.3, dam=True, can="left")

        # Các bước trong luồng của nhánh đó
        so_buoc = len(buoc_list)
        chieu_rong_buoc = (14.0 - (so_buoc - 1) * 0.45) / so_buoc
        x_buoc = 4.5

        for i, (b_td, b_nd, b_col) in enumerate(buoc_list):
            nen_buoc = (C_AI_BG if b_col==C_AI else
                        (C_DANGER_BG if b_col==C_DANGER else
                         (C_SAFE_BG if b_col==C_SAFE else
                          (C_WARN_BG if b_col==C_WARN else
                           (C_PURPLE_BG if b_col==C_PURPLE else "white")))))
            hop(ax, x_buoc, y + 0.08, chieu_rong_buoc, 1.3, b_td, b_nd,
                vien=b_col, nen=nen_buoc, co_td=9.3, co_nd=8.0, can="center")

            if i < so_buoc - 1:
                mui_ten(ax, x_buoc + chieu_rong_buoc + 0.04, y + 0.73,
                        x_buoc + chieu_rong_buoc + 0.41, y + 0.73, mau="#94A3B8")

            x_buoc += chieu_rong_buoc + 0.45

    # ========================== 3. BẢNG TỔNG KẾT ĐÁNH GIÁ (FOOTER) ==========================
    khung_bot = FancyBboxPatch((0.5, 0.25), 18.0, 1.6, boxstyle="round,pad=0.02,rounding_size=0.08",
                                linewidth=1.2, edgecolor="#CBD5E1", facecolor="white")
    ax.add_patch(khung_bot)

    so_sanh_text = (
        "[*] BẢN CHẤT THỰC NGHIỆM & PHẢN BIỆN HỌC THUẬT:\n"
        "• Tại sao Prompt \"Tự kiểm tra\" (Self-Review A+) không đủ: Mô hình tự soát chỉ giảm lỗi chủ thể nhẹ (12.4% -> 9.8%) vì LLM bị mù trước chính ảo giác của mình.\n"
        "• MediTrace Full (C_khoá): Giảm sai chủ thể xuống 2.1% (giảm 83% lỗi), F1 đạt 70.8%, tỷ lệ chặn oan (False-block rate) cực thấp <= 1% (0/30.136 dòng test thật).\n"
        "• Khẳng định khoa học: \"When the same model and same cases are used, structural safeguards reduced clinical risk leakage by over 80%.\""
    )
    ax.text(0.75, 1.05, so_sanh_text, ha="left", va="center", fontsize=9.2, color=C_TEXT_MAIN, linespacing=1.4)

    # Lưu ảnh ra cả 2 nơi
    p1 = RA_DOCS / "so-do-so-sanh-cac-nhanh.png"
    p2 = RA_ARTIFACT / "so-do-so-sanh-cac-nhanh.png"
    fig.savefig(p1)
    fig.savefig(p2)
    plt.close(fig)
    print(f"Da tao thanh cong anh so sanh cac nhanh:\n-> {p1}\n-> {p2}")

if __name__ == "__main__":
    ve_so_sanh_nhanh()
