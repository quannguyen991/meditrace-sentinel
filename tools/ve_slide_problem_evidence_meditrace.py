# -*- coding: utf-8 -*-
"""Ve slide doan thuyet trinh: Problem -> Evidence -> MediTrace Sentinel.
Ti le chuan 16:9 (1920x1080), bo cuc 3 cot doi chieu truc quan cho Ban Giam Khao.

Chay:
    python tools/ve_slide_problem_evidence_meditrace.py
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

# Mau sac chu dao
C_BG = "#F8FAFC"
C_TEXT_MAIN = "#0F172A"
C_TEXT_MUTED = "#475569"

C_AI = "#0D5C54"          # Xanh mong ket (AI)
C_AI_BG = "#E6F4F1"
C_RULE = "#1E3A5F"        # Xanh Navy (Luat / Pipeline)
C_RULE_BG = "#F1F5F9"
C_SAFE = "#059669"        # Xanh la (An toan)
C_SAFE_BG = "#ECFDF5"
C_WARN = "#D97706"        # Vang ho phach (Canh bao)
C_WARN_BG = "#FFFBEB"
C_DANGER = "#DC2626"      # Do (Loi y khoa / Rui ro)
C_DANGER_BG = "#FEF2F2"
C_PURPLE = "#6366F1"      # Tim (Literature)
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

def mui_ten(ax, x1, y1, x2, y2, mau="#94A3B8", day=1.5):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=13, linewidth=day, color=mau))

def ve_slide_thuyet_trinh():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    # ========================== 1. HEADER (TIÊU ĐỀ SLIDE) ==========================
    ax.text(9.6, 10.35, "VÌ SAO CẦN MEDITRACE: TỪ BẰNG CHỨNG Y VĂN ĐẾN ĐƯỜNG ỐNG 5 TẦNG",
            ha="center", va="center", fontsize=17, fontweight="bold", color=C_TEXT_MAIN)
    ax.text(9.6, 9.95, "Clinical AI Documentation is Useful — But NOT Reliably Self-Verifying (Không thể phó mặc cho LLM tự do)",
            ha="center", va="center", fontsize=11, color=C_TEXT_MUTED)

    # ========================== 2. CỘT 1 (TRÁI): BẰNG CHỨNG Y VĂN (EVIDENCE) ==========================
    khung_c1 = FancyBboxPatch((0.5, 1.4), 5.7, 8.2, boxstyle="round,pad=0.03,rounding_size=0.1",
                              linewidth=1.4, edgecolor="#CBD5E1", facecolor="white")
    ax.add_patch(khung_c1)

    ax.text(0.75, 9.25, "I. BẰNG CHỨNG Y VĂN QUỐC TẾ", fontsize=12, fontweight="bold", color=C_DANGER)
    ax.text(0.75, 8.95, "Lỗi của AI trong thực tế lâm sàng không phải giả thuyết", fontsize=9, color=C_TEXT_MUTED)

    # 4 Stat Cards
    # Stat 1: 70%
    hop(ax, 0.75, 6.95, 5.2, 1.75, "70% BẢN NHÁP CÓ LỖI LÂM SÀNG",
        "Thử nghiệm kiểm soát trên 2 AI thương mại (JMIR 2025 / PMC11811668)\n"
        "• 31/44 bản nháp có >= 1 lỗi; trung bình 2.9 lỗi mỗi bản nháp.\n"
        "• Lỗi bỏ sót (Omission) chiếm đa số — Bác sĩ rất khó thấy khi review!",
        vien=C_DANGER, nen=C_DANGER_BG, co_td=11, co_nd=8.3, mau_td=C_DANGER)

    # Stat 2: 18% & 11.5%
    hop(ax, 0.75, 5.15, 5.2, 1.65, "18% BỎ SÓT  |  11.5% ẢO GIÁC",
        "Thử nghiệm thực tế tương lai trên 356 bệnh án (PubMed 41996389)\n"
        "• 9.3% thông tin tình cờ bị đưa nhầm (Accidental inclusion)\n"
        "• Chứng minh: Mô hình sinh tự do không thể tự kiểm soát tính đầy đủ.",
        vien=C_WARN, nen=C_WARN_BG, co_td=10.5, co_nd=8.3, mau_td=C_WARN)

    # Stat 3: 5.3%
    hop(ax, 0.75, 3.4, 5.2, 1.6, "5.3% NGUY CƠ GÂY HẠI NGHIÊM TRỌNG",
        "Thử nghiệm lâm sàng thực nghiệm (ScienceDirect 2026)\n"
        "• 5.3% bản nháp chứa lỗi có nguy cơ Serious / Imminent Harm\n"
        "• Nếu bác sĩ ký duyệt mà không sửa sẽ đe dọa an toàn người bệnh.",
        vien=C_DANGER, nen=C_DANGER_BG, co_td=10.5, co_nd=8.3, mau_td=C_DANGER)

    # Stat 4: 44%
    hop(ax, 0.75, 1.65, 5.2, 1.6, "44% ẢO GIÁC LÀ LỖI MAJOR (TRẦM TRỌNG)",
        "Đánh giá trên 12,999 câu do bác sĩ thẩm định (npj Digital Medicine / Nature)\n"
        "• Tần suất ảo giác có thể nhỏ (1.47%), nhưng gần 1 nửa là cực kỳ nguy hiểm!\n"
        "• Không thể coi các lỗi là như nhau (quên uống trà != quên dị ứng).",
        vien=C_PURPLE, nen=C_PURPLE_BG, co_td=10.5, co_nd=8.3, mau_td=C_PURPLE)

    # ========================== 3. CỘT 2 (GIỮA): VÌ SAO SINH TỰ DO BỊ MÙ KIỂM TOÁN ==========================
    khung_c2 = FancyBboxPatch((6.5, 1.4), 5.7, 8.2, boxstyle="round,pad=0.03,rounding_size=0.1",
                              linewidth=1.4, edgecolor="#CBD5E1", facecolor="white")
    ax.add_patch(khung_c2)

    ax.text(6.75, 9.25, "II. ĐIỂM YẾU CỦA MÔ HÌNH SINH TỰ DO", fontsize=12, fontweight="bold", color="#64748B")
    ax.text(6.75, 8.95, "Why Direct Generation is Difficult to Audit (Mù kiểm toán)", fontsize=9, color=C_TEXT_MUTED)

    # Luồng sinh thẳng
    hop(ax, 6.75, 7.85, 5.2, 0.85, "1. HỘI THOẠI KHÁM PHÒNG KHÁM", "Bác sĩ, bệnh nhân, người nhà nói chuyện đa thoại",
        vien=C_RULE, nen="white", co_td=9.5, co_nd=8.2, can="center")
    mui_ten(ax, 9.35, 7.85, 9.35, 7.55, mau="#64748B", day=1.5)

    hop(ax, 6.75, 6.7, 5.2, 0.85, "2. MÔ HÌNH LLM (GPT / Qwen...)", "Sinh văn bản tự do dựa trên xác suất từ tiếp theo",
        vien=C_AI, nen=C_AI_BG, co_td=9.5, co_nd=8.2, can="center")
    mui_ten(ax, 9.35, 6.7, 9.35, 6.4, mau="#64748B", day=1.5)

    hop(ax, 6.75, 5.55, 5.2, 0.85, "3. BẢN NHÁP VĂN XUÔI TRÔI CHẢY", "Fluent Clinical Note (Nghe rất mượt và chuẩn văn y)",
        vien="#64748B", nen="#F1F5F9", co_td=9.5, co_nd=8.2, can="center")

    # Hộp bóc mẽ cạm bẫy lâm sàng
    hop(ax, 6.75, 1.65, 5.2, 3.65, "CÁC CẠM BẪY LÂM SÀNG BỊ 'GIẤU' KÍN",
        "Mô hình viết cả bài văn dài khiến bác sĩ đọc lướt không thể nhận ra:\n\n"
        "• Tráo đổi chủ thể (12.4%): Tiền sử người nhà bị gán thành của bệnh nhân\n"
        "   ('Bố em bị hen' -> ghi thành 'Bệnh nhân có tiền sử hen phế quản')\n"
        "• Đảo ngược khẳng định/phủ định: 30% ảo giác thuộc nhóm phủ định\n"
        "• Biến câu điều kiện thành sự thật: 'Nếu sốt thì uống' -> ghi 'đang sốt'\n"
        "• Giữ lại thông tin đã đính chính: Giữ thuốc cũ dù lượt sau đã đổi\n"
        "• Mù câu hỏi tự soát: Thêm prompt 'Check your answer' vẫn lọt 9.8% lỗi\n"
        "• ROUGE cao giả tạo: Vẫn đạt ~1.0000 dù bệnh án sai chết người!",
        vien=C_DANGER, nen=C_DANGER_BG, co_td=10, co_nd=8.2, mau_td=C_DANGER)

    # ========================== 4. CỘT 3 (PHẢI): GIẢI PHÁP ĐƯỜNG ỐNG 5 TẦNG MEDITRACE ==========================
    khung_c3 = FancyBboxPatch((12.5, 1.4), 6.2, 8.2, boxstyle="round,pad=0.03,rounding_size=0.1",
                              linewidth=1.4, edgecolor=C_SAFE, facecolor="white")
    ax.add_patch(khung_c3)

    ax.text(12.75, 9.25, "III. GIẢI PHÁP 5 TẦNG MEDITRACE SENTINEL", fontsize=12, fontweight="bold", color=C_SAFE)
    ax.text(12.75, 8.95, "How MediTrace Provides Structural Auditability (Rào chắn cấu trúc)", fontsize=9, color=C_TEXT_MUTED)

    cac_tang = [
        ("TẦNG 1: Rút mệnh đề nguyên tử (AI)", "AI không viết văn xuôi; chỉ trích JSON + câu trích bằng chứng", C_AI, C_AI_BG),
        ("TẦNG 2: Gom & Gán chủ thể (Luật)", "Định danh Bệnh nhân vs Người nhà (chặn lỗi tráo tiền sử)", C_RULE, C_RULE_BG),
        ("TẦNG 3: Cập nhật & Quan hệ (Luật)", "Theo dõi đính chính, tự sửa (11.5% lỗi tự sửa giảm còn 0.8%)", C_RULE, C_RULE_BG),
        ("TẦNG 4: Khóa bằng chứng (7 cổng K1-K7)", "Chặn điều kiện & K7 chặn thông tin cũ bị đè (Superseded)", C_DANGER, C_DANGER_BG),
        ("TẦNG 5: Cổng rủi ro lâm sàng & Xếp chỗ", "Tách bạch: Thân bản nháp vs Mục Cần bác sĩ xác nhận", C_SAFE, C_SAFE_BG),
    ]

    y_t = 7.7
    for i, (t_td, t_nd, col, bg_col) in enumerate(cac_tang):
        hop(ax, 12.75, y_t, 5.7, 0.95, t_td, t_nd, vien=col, nen=bg_col, co_td=9.3, co_nd=8.0)
        if i < len(cac_tang) - 1:
            mui_ten(ax, 15.6, y_t, 15.6, y_t - 0.25, mau="#059669", day=1.4)
        y_t -= 1.2

    # Output Card
    hop(ax, 12.75, 1.65, 5.7, 1.05, "ĐẦU RA BỆNH ÁN MINH BẠCH & AUDIT TRAIL",
        "• Bác sĩ duyệt bệnh án trong 30 giây (mỏ neo câu trích đến từng lượt nói)\n"
        "• Khâu 6: Gợi ý tối đa 3 câu hỏi làm rõ nếu có mâu thuẫn cần xác nhận.",
        vien=C_SAFE, nen=C_SAFE_BG, co_td=9.5, co_nd=8.2, mau_td=C_SAFE)

    # ========================== 5. FOOTER: KẾT QUẢ THỰC NGHIỆM ĐỐI CHỨNG ==========================
    khung_bot = FancyBboxPatch((0.5, 0.2), 18.2, 1.05, boxstyle="round,pad=0.02,rounding_size=0.08",
                                linewidth=1.2, edgecolor="#94A3B8", facecolor="#0F172A")
    ax.add_patch(khung_bot)

    so_sanh_text = (
        "[*] ĐỐI CHỨNG THỰC NGHIỆM (KHI DÙNG CÙNG MÔ HÌNH VÀ CÙNG BỘ CA BỆNH):\n"
        "• Rò rỉ sai chủ thể (Wrong-subject): Sinh thẳng A (12.4%) -> Tự soát A+ (9.8%) -> MediTrace C_khoá (2.1% — Giảm 83% rủi ro!)\n"
        "• F1 đạt 70.8%, SER giảm từ 45.4% xuống 36.9% | Tỷ lệ chặn oan (False-block rate) cực thấp <= 1% (0/30.136 dòng kiểm thử)."
    )
    ax.text(0.75, 0.72, so_sanh_text, ha="left", va="center", fontsize=9.2, color="#F8FAFC", linespacing=1.35)

    p1 = RA_DOCS / "slide-problem-evidence-meditrace.png"
    p2 = RA_ARTIFACT / "slide-problem-evidence-meditrace.png"
    fig.savefig(p1)
    fig.savefig(p2)
    plt.close(fig)
    print(f"Da tao thanh cong slide thuyet trinh:\n-> {p1}\n-> {p2}")

if __name__ == "__main__":
    ve_slide_thuyet_trinh()
