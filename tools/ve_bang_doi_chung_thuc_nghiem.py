# -*- coding: utf-8 -*-
"""Ve slide bang so lieu thuc nghiem doi chung tra loi Cau hoi nghien cuu.
Ti le chuan 16:9 (1920x1080), thiet ke publication-grade cuc dep cho Hoi dong Giam khao.

Chay:
    python tools/ve_bang_doi_chung_thuc_nghiem.py
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

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

# Mau sac sang trong, hien dai
C_BG = "#F8FAFC"
C_TEXT_MAIN = "#0F172A"
C_TEXT_MUTED = "#475569"

C_AI = "#0D5C54"          # Xanh mong ket
C_AI_BG = "#E6F4F1"
C_RULE = "#1E3A5F"        # Xanh Navy
C_RULE_BG = "#F1F5F9"
C_SAFE = "#059669"        # Xanh la (Tot nhat)
C_SAFE_BG = "#ECFDF5"
C_WARN = "#D97706"        # Vang ho phach
C_WARN_BG = "#FFFBEB"
C_DANGER = "#DC2626"      # Do (Nguy co)
C_DANGER_BG = "#FEF2F2"
C_HIGHLIGHT = "#0284C7"   # Xanh duong nhan manh
C_HIGHLIGHT_BG = "#F0F9FF"
C_PURPLE = "#6366F1"      # Tim (Interactive / Hoi lai)
C_PURPLE_BG = "#EEF2FF"

def hop(ax, x, y, w, h, tieu_de, noi_dung="", vien="#CBD5E1", nen="white",
        co_td=10, co_nd=8.5, mau_td=C_TEXT_MAIN, mau_nd=C_TEXT_MUTED, dam=True, can="left"):
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                           linewidth=1.3, edgecolor=vien, facecolor=nen)
    ax.add_patch(patch)
    if noi_dung:
        ax.text(x + w/2 if can=="center" else x + 0.15, y + h - 0.22, tieu_de,
                ha=can, va="top", fontsize=co_td, fontweight="bold" if dam else "normal",
                color=mau_td)
        ax.text(x + w/2 if can=="center" else x + 0.15, y + 0.16, noi_dung,
                ha=can, va="bottom", fontsize=co_nd, color=mau_nd, linespacing=1.25)
    else:
        ax.text(x + w/2, y + h/2, tieu_de, ha="center", va="center",
                fontsize=co_td, fontweight="bold" if dam else "normal", color=mau_td, linespacing=1.2)

def ve_bang_doi_chung():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    # ========================== 1. HEADER & CÂU HỎI NGHIÊN CỨU ==========================
    ax.text(9.6, 10.38, "BẢNG KẾT QUẢ THỰC NGHIỆM ĐỐI CHỨNG TRẢ LỜI CÂU HỎI NGHIÊN CỨU",
            ha="center", va="center", fontsize=16.5, fontweight="bold", color=C_TEXT_MAIN)

    # Box Câu hỏi nghiên cứu (RQ Badge)
    rq_box = FancyBboxPatch((0.6, 9.35), 18.0, 0.75, boxstyle="round,pad=0.02,rounding_size=0.06",
                            linewidth=1.4, edgecolor=C_RULE, facecolor=C_HIGHLIGHT_BG)
    ax.add_patch(rq_box)
    rq_text = (
        "CÂU HỎI NGHIÊN CỨU (RQ): Với cùng mô hình nền (Qwen3-4B QLoRA) và dữ liệu lâm sàng tiếng Việt,\n"
        "quy trình xử lý qua mệnh đề, trạng thái và bằng chứng có giảm lỗi so với sinh bản nháp trực tiếp không?"
    )
    ax.text(9.6, 9.72, rq_text, ha="center", va="center", fontsize=10.2, fontweight="bold",
            color=C_RULE, linespacing=1.25)

    # ========================== 2. BẢNG SỐ LIỆU ĐỐI CHỨNG (MAIN MATRIX) ==========================
    # Toa do bang
    x_bang = 0.6
    y_dau = 8.65
    w_bang = 18.0
    h_cot_td = 0.55

    # Cac cot: (X_offset, Width, Title, Align)
    # So lieu lay tu docs/final/Bao cao du an.md muc 4.1-4.4 va README.md "Ket qua do".
    cac_cot = [
        (0.0, 3.2, "Bộ thử thách (số ca)", "left"),
        (3.2, 3.6, "Chỉ tách thông tin\nF1 / SER / nhầm người", "center"),
        (6.8, 3.6, "+ Xử lý lời sửa\nF1 / SER / nhầm người", "center"),
        (10.4, 3.8, "+ Kiểm bằng chứng (C_khoá)\nF1 / SER / nhầm người", "center"),
        (14.2, 3.8, "Đọc kết quả", "left"),
    ]

    box_th = FancyBboxPatch((x_bang, y_dau - h_cot_td), w_bang, h_cot_td,
                            boxstyle="round,pad=0.01,rounding_size=0.04",
                            linewidth=1.2, edgecolor="#94A3B8", facecolor="#1E293B")
    ax.add_patch(box_th)
    for x_off, w_c, c_td, can in cac_cot:
        x_chu = x_bang + x_off + (w_c / 2 if can == "center" else 0.2)
        ax.text(x_chu, y_dau - h_cot_td / 2, c_td, ha=can, va="center",
                fontsize=9.2, fontweight="bold", color="white", linespacing=1.15)

    hang_data = [
        ("Đổi chủ thể (80 ca)", "66,1 / 45,4 / 22,0%", "69,2 / 38,2 / 20,0%", "70,8 / 36,9 / 17,9%",
         "Cải thiện rõ nhất", C_SAFE),
        ("Đính chính / tự sửa (60 ca)", "80,9 / 29,9 / 7,6%", "85,9 / 17,4 / 6,8%", "87,0 / 17,4 / 5,5%",
         "Bản cũ còn giữ: 11,48% → 0,80%", C_SAFE),
        ("Nhiễu giọng nói (80 ca)", "63,2 / 63,7 / 3,7%", "64,9 / 58,4 / 3,3%", "64,8 / 58,6 / 3,5%",
         "Kiểm bằng chứng gần như\nkhông cải thiện", C_WARN),
        ("Vùng miền (80 ca)", "85,8 / 21,5 / 1,7%", "87,8 / 16,9 / 1,5%", "88,0 / 16,3 / 1,5%",
         "Cải thiện rất nhỏ", C_WARN),
    ]

    y_cur = y_dau - h_cot_td - 0.1
    h_hang = 0.78
    for ten, v1, v2, v3, doc, mau_doc in hang_data:
        box_tr = FancyBboxPatch((x_bang, y_cur - h_hang), w_bang, h_hang,
                                boxstyle="round,pad=0.01,rounding_size=0.04",
                                linewidth=1.1, edgecolor="#CBD5E1", facecolor="white")
        ax.add_patch(box_tr)
        cot_vals = [
            (ten, "left", C_TEXT_MAIN, True, 9.6),
            (v1, "center", C_TEXT_MUTED, False, 9.6),
            (v2, "center", C_TEXT_MUTED, False, 9.6),
            (v3, "center", C_RULE, True, 9.6),
            (doc, "left", mau_doc, True, 8.8),
        ]
        for idx, (val, can, mau, dam, sz) in enumerate(cot_vals):
            x_off, w_c, _, _ = cac_cot[idx]
            x_chu = x_bang + x_off + (w_c / 2 if can == "center" else 0.2)
            ax.text(x_chu, y_cur - h_hang / 2, val, ha=can, va="center",
                    fontsize=sz, fontweight="bold" if dam else "normal", color=mau, linespacing=1.2)
        y_cur -= h_hang + 0.08

    # Hang canh bao: nhanh A (sinh thang) va nhanh D (hoi lai bac si)
    for ten, noi_dung, vien, nen in [
        ("Nhánh A (sinh thẳng bản nháp)",
         "Ghi đúng người CAO HƠN pipeline: 0,939 so với 0,748 (bộ đổi chủ thể). Dự án không khẳng định MediTrace chính xác hơn cách sinh thẳng;\n"
         "điểm mạnh là mỗi dòng kiểm tra được về lượt nói gốc. Một phần điểm của nhánh A do chép giống văn mẫu ở 30–63% số ca.",
         C_DANGER, C_DANGER_BG),
        ("Nhánh D (hỏi lại bác sĩ)",
         "CHƯA ĐO. Chưa từng chạy với bác sĩ thật.",
         C_PURPLE, C_PURPLE_BG),
    ]:
        h_r = 0.78 if "\n" in noi_dung else 0.5
        box_tr = FancyBboxPatch((x_bang, y_cur - h_r), w_bang, h_r,
                                boxstyle="round,pad=0.01,rounding_size=0.04",
                                linewidth=1.4, edgecolor=vien, facecolor=nen)
        ax.add_patch(box_tr)
        ax.text(x_bang + 0.2, y_cur - h_r / 2, ten, ha="left", va="center",
                fontsize=9.6, fontweight="bold", color=vien)
        ax.text(x_bang + 3.4, y_cur - h_r / 2, noi_dung, ha="left", va="center",
                fontsize=8.8, color=C_TEXT_MAIN, linespacing=1.3)
        y_cur -= h_r + 0.08

    # ========================== 3. PANEL DƯỚI ==========================
    y_panel = 2.75
    h_panel = 2.45

    khung_p1 = FancyBboxPatch((0.6, y_panel - h_panel), 8.8, h_panel,
                              boxstyle="round,pad=0.02,rounding_size=0.06",
                              linewidth=1.3, edgecolor=C_WARN, facecolor="white")
    ax.add_patch(khung_p1)
    ax.text(0.85, y_panel - 0.22, "[1] KẾT QUẢ KHÔNG CÓ LỢI (GHI ĐÚNG NHƯ ĐO)",
            fontsize=10.2, fontweight="bold", color=C_WARN, va="top")
    ablation_text = (
        "• Kiểm bằng chứng làm tăng bỏ sót: 4,5% → 7,7% (bộ đổi chủ thể).\n"
        "• Lỗi nguy hiểm lọt vào thân bản nháp, chính sách D: 11,8% trên tập phát triển\n"
        "   đã dùng để chỉnh luật (docs/ket-qua/canh-bao.json), nên số này lạc quan.\n"
        "• Chặn thừa trên đầu ra mô hình thật: 8,0% (C) / 10,0% (D).\n"
        "• Chưa chạy so sánh với mô hình thương mại; phép đo duy nhất: mô hình thương mại\n"
        "   ghi nhầm người 1,4% so với 7,6% của mô hình dự án (bộ tự sửa) — thương mại tốt hơn."
    )
    ax.text(0.85, y_panel - 0.58, ablation_text, fontsize=8.6, color=C_TEXT_MAIN, linespacing=1.32, va="top")

    khung_p2 = FancyBboxPatch((9.7, y_panel - h_panel), 8.9, h_panel,
                              boxstyle="round,pad=0.02,rounding_size=0.06",
                              linewidth=1.3, edgecolor=C_SAFE, facecolor=C_SAFE_BG)
    ax.add_patch(khung_p2)
    ax.text(9.95, y_panel - 0.22, "[2] TRẢ LỜI CÂU HỎI NGHIÊN CỨU",
            fontsize=10.2, fontweight="bold", color=C_SAFE, va="top")
    conclusion_text = (
        "Có giảm lỗi so với chỉ tách thông tin, nhưng không đều giữa các bộ:\n"
        "• Đổi chủ thể: nhầm người 22,0% → 17,9%; F1 66,1 → 70,8; SER 45,4 → 36,9.\n"
        "• Tự sửa: thông tin cũ còn giữ 11,48% → 0,80%.\n"
        "• Chặn nhầm 0/30.136 chỉ đúng vì đáp án chép gần nguyên văn hội thoại\n"
        "   (độ phủ 0,95); trên đầu ra mô hình thật chặn thừa 8,0–10,0%.\n"
        "• Kết quả chỉ có hiệu lực trên dữ liệu mô phỏng, chưa đo trên hội thoại thật."
    )
    ax.text(9.95, y_panel - 0.58, conclusion_text, fontsize=8.6, color=C_TEXT_MAIN, linespacing=1.32, va="top")

    ax.text(9.6, 0.05, "Nguồn: docs/final/Báo cáo dự án.md mục 4.1–4.4; README.md \"Kết quả đo\"; docs/ket-qua/canh-bao.json. "
            "Số ca là bộ thử thách, không phải 5.000 ca dữ liệu.",
            ha="center", va="bottom", fontsize=8, color=C_TEXT_MUTED)

    p1 = RA_DOCS / "bang-doi-chung-thuc-nghiem.png"
    p2 = RA_ARTIFACT / "bang-doi-chung-thuc-nghiem.png"
    fig.savefig(p1)
    fig.savefig(p2)
    plt.close(fig)
    print(f"Da tao thanh cong bang doi chung thuc nghiem:\n-> {p1}\n-> {p2}")

if __name__ == "__main__":
    ve_bang_doi_chung()
