# -*- coding: utf-8 -*-
"""Ve so do tong the: Cac tang xu ly, phan tich va phan biet trong MediTrace Sentinel.
Chuan hoa thuat ngu hoc thuat, bo sung cong K7 Supersession, toi uu bo cuc 16:9 cao cap.

Chay:
    python tools/ve_so_do_tong_the_cac_tang.py
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

# Mau sac chuan phong cach Y te - Khoa hoc du lieu cao cap
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
C_GRAY = "#64748B"
C_GRAY_BG = "#F8FAFC"

def hop(ax, x, y, w, h, tieu_de, noi_dung="", vien="#CBD5E1", nen="white",
        co_td=10.0, co_nd=8.6, mau_td=C_TEXT_MAIN, mau_nd=C_TEXT_MUTED, dam=True, can="left",
        dy_text=0.48):
    """Ve hop co bo goc voi tieu de va noi dung nam tu tren xuong (va='top') de tranh chong de chu."""
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                           linewidth=1.2, edgecolor=vien, facecolor=nen)
    ax.add_patch(patch)
    if noi_dung:
        ax.text(x + w/2 if can=="center" else x + 0.14, y + h - 0.18, tieu_de,
                ha=can, va="top", fontsize=co_td, fontweight="bold" if dam else "normal",
                color=mau_td)
        ax.text(x + w/2 if can=="center" else x + 0.14, y + h - dy_text, noi_dung,
                ha=can, va="top", fontsize=co_nd, color=mau_nd, linespacing=1.28)
    else:
        ax.text(x + w/2, y + h/2, tieu_de, ha="center", va="center",
                fontsize=co_td, fontweight="bold" if dam else "normal", color=mau_td, linespacing=1.25)

def mui_ten(ax, x1, y1, x2, y2, mau="#94A3B8", day=1.6):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=14, linewidth=day, color=mau))

def ve_tong_the():
    fig, ax = plt.subplots(figsize=(19.2, 12), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 12)
    ax.axis("off")

    # ========================== 1. TIEU DE CHINH ==========================
    ax.text(9.6, 11.52, "KIẾN TRÚC TOÀN CẢNH: CÁC TẦNG XỬ LÝ & BỘ PHÂN LOẠI TRONG MEDITRACE SENTINEL",
            ha="center", va="center", fontsize=16.5, fontweight="bold", color=C_TEXT_MAIN)
    ax.text(9.6, 11.14, "Quy trình chuyển đổi hội thoại lâm sàng đa thoại thành bệnh án có kiểm soát và truy vết nguồn gốc từng dòng",
            ha="center", va="center", fontsize=11, color=C_TEXT_MUTED)

    # ========================== 2. KHUNG TRUC CHINH (TOP PIPELINE) ==========================
    khung_top = FancyBboxPatch((0.4, 6.7), 18.4, 4.1, boxstyle="round,pad=0.03,rounding_size=0.10",
                               linewidth=1.3, edgecolor="#94A3B8", facecolor="white")
    ax.add_patch(khung_top)
    ax.text(0.7, 10.45, "I. QUY TRÌNH KIẾN TRÚC 5 TẦNG XỬ LÝ (CORE PIPELINE)",
            ha="left", va="center", fontsize=12, fontweight="bold", color=C_RULE)

    # 6 Khoi chinh tren truc Pipeline (Chuan hoa thuat ngu hoc thuat)
    khoi_pipeline = [
        (0.65, 7.05, 2.5, 2.9, "0. TIẾP NHẬN ĐẦU VÀO",
         "• PhoWhisper thu âm tiếng Việt\n• pyannote.audio tách người nói\n• Định danh vai: Bác sĩ / BN\n• Chia lượt nói [T1], [T2], [T3]...\n• Hoạt động 100% On-Premise",
         C_GRAY, C_GRAY_BG),
        (3.55, 7.05, 2.7, 2.9, "TẦNG 1: RÚT MỆNH ĐỀ",
         "• Mô hình Qwen3-4B QLoRA Local\n• Trích xuất mẩu dữ liệu nhỏ\n• Gắn mỏ neo bằng chứng [T_i]\n• TUYỆT ĐỐI không sinh tự do\n• Triệt tiêu bịa đặt (Hallucination)",
         C_AI, C_AI_BG),
        (6.65, 7.05, 2.7, 2.9, "TẦNG 2: GÁN CHỦ THỂ",
         "• Phân giải đại từ nhân xưng\n• Tách rõ Bệnh nhân vs Gia đình\n• Chống nhầm tiền sử bệnh\n• Lỗi giảm từ 12.4% -> 2.1%\n• Minh chứng bám sát JAMA 2026",
         C_RULE, C_RULE_BG),
        (9.75, 7.05, 2.7, 2.9, "TẦNG 3: TRẠNG THÁI",
         "• Theo dõi dòng thời gian thoại\n• Nhận diện tự sửa & đính chính\n• Đổi trạng thái 'Bị thay thế'\n• Lỗi giữ tin cũ: 11.5% -> 0.8%\n• Lưu trọn vẹn Audit Trail",
         C_RULE, C_RULE_BG),
        (12.85, 7.05, 2.8, 2.9, "TẦNG 4: KHÓA BẰNG CHỨNG",
         "• 7 Cổng kiểm định độc lập (K1-K7)\n• Chặn câu giả định / dặn dò (K4)\n• Cổng K7 chặn fact bị thay thế\n• Chặn oan (False-block) <= 1%\n• (0/30.136 dòng bị chặn oan)",
         C_DANGER, C_DANGER_BG),
        (16.05, 7.05, 2.55, 2.9, "TẦNG 5: CỔNG RỦI RO",
         "• Phân luồng xuất bản kép\n• Thân SOAP vs Mục Xác nhận\n• Bác sĩ duyệt trong 30 giây\n• Gợi ý tối đa 3 câu hỏi làm rõ\n• Lưu vết pháp lý EMR trọn vẹn",
         C_SAFE, C_SAFE_BG),
    ]

    for x, y, w, h, td, nd, vien, nen in khoi_pipeline:
        hop(ax, x, y, w, h, td, nd, vien=vien, nen=nen, co_td=9.6, co_nd=8.3, can="left", dam=True, dy_text=0.48)

    # Mui ten noi giua cac khoi pipeline
    for i in range(len(khoi_pipeline) - 1):
        x1 = khoi_pipeline[i][0] + khoi_pipeline[i][2]
        x2 = khoi_pipeline[i+1][0]
        y_mid = 7.05 + 1.45
        mui_ten(ax, x1 + 0.04, y_mid, x2 - 0.04, y_mid, mau="#64748B", day=2.0)

    # ========================== 3. BA PHAN HE PHAN TICH CHI TIET (BOTTOM) ==========================

    # --- KHUNG CON 1: TANG 2 (4 CAP DO PHAN GIAI CHU THE) ---
    khung_b1 = FancyBboxPatch((0.4, 0.45), 5.75, 5.85, boxstyle="round,pad=0.03,rounding_size=0.10",
                              linewidth=1.2, edgecolor="#94A3B8", facecolor="white")
    ax.add_patch(khung_b1)
    ax.text(0.7, 5.98, "II. TẦNG 2: 4 CẤP ĐỘ PHÂN GIẢI CHỦ THỂ LÂM SÀNG",
            ha="left", va="center", fontsize=11, fontweight="bold", color=C_RULE)
    ax.text(0.7, 5.68, "(Giải quyết điểm mù ROUGE / Tránh gán nhầm tiền sử người nhà)",
            ha="left", va="center", fontsize=8.6, color=C_TEXT_MUTED)

    cac_tang_do_kho = [
        (0.65, 4.4, 5.25, 1.05, "Cấp 1: Lời Bác sĩ nhận định",
         "Bác sĩ trao đổi về tình trạng bệnh nhân -> Gán chủ thể: BỆNH NHÂN", C_RULE),
        (0.65, 3.15, 5.25, 1.05, "Cấp 2: Bệnh nhân tự thuật",
         "Bệnh nhân trực tiếp kể triệu chứng bản thân -> Gán chủ thể: BỆNH NHÂN", C_RULE),
        (0.65, 1.90, 5.25, 1.05, "Cấp 3: Người nhà trình bày hộ",
         "Người nhà kể: 'Cháu sốt từ hôm qua...' -> Gán chủ thể: BỆNH NHÂN", C_WARN),
        (0.65, 0.62, 5.25, 1.08, "Cấp 4: Tiền sử gia đình (Tránh gán nhầm)",
         "Người nhà kể: 'Bố em bị hen...' -> Gán TIỀN SỬ GIA ĐÌNH (Không gán BN)", C_DANGER),
    ]
    for x, y, w, h, td, nd, col in cac_tang_do_kho:
        hop(ax, x, y, w, h, td, nd, vien=col, nen="white", co_td=9.3, co_nd=8.3, can="left", dy_text=0.46)

    # --- KHUNG CON 2: TANG 4 (7 CONG KIEM CHUNG K1-K7) ---
    khung_b2 = FancyBboxPatch((6.45, 0.45), 6.35, 5.85, boxstyle="round,pad=0.03,rounding_size=0.10",
                              linewidth=1.2, edgecolor="#94A3B8", facecolor="white")
    ax.add_patch(khung_b2)
    ax.text(6.7, 5.98, "III. TẦNG 4: 7 CỔNG KHÓA BẰNG CHỨNG ĐỘC LẬP (K1-K7)",
            ha="left", va="center", fontsize=11, fontweight="bold", color=C_DANGER)
    ax.text(6.7, 5.68, "(Kiểm định chéo đối soát nguyên văn với dữ liệu hội thoại gốc)",
            ha="left", va="center", fontsize=8.6, color=C_TEXT_MUTED)

    cac_cong = [
        (6.65, 4.80, 2.9, 0.74, "K1: Nguồn gốc nguyên văn", "Trích dẫn phải có thật trong thoại", C_RULE),
        (9.70, 4.80, 2.9, 0.74, "K2: Khớp thực thể y khoa", "Khớp đúng thuật ngữ lâm sàng", C_RULE),
        (6.65, 3.93, 2.9, 0.74, "K3: Khớp đại từ xưng hô", "Đúng chủ thể trong ngữ cảnh", C_RULE),
        (9.70, 3.93, 2.9, 0.74, "K4: Chặn giả định / Dặn dò", "Chặn câu điều kiện & dặn dò", C_DANGER),
        (6.65, 3.06, 2.9, 0.74, "K5: Mốc thời gian xuất hiện", "Khớp thời điểm thực tế diễn ra", C_RULE),
        (9.70, 3.06, 2.9, 0.74, "K6: Chi tiết thuốc & Liều", "Đúng tên, hàm lượng, cách dùng", C_RULE),
        (6.65, 1.95, 5.95, 0.95, "K7: Supersession / Đính chính thay thế (Độc quyền MediTrace)",
         "Chặn triệt để fact cũ đã bị đính chính ở lượt sau — Khắc phục điểm mù RAG thông thường", C_DANGER),
    ]
    for x, y, w, h, td, nd, col in cac_cong:
        hop(ax, x, y, w, h, td, nd, vien=col, nen=C_DANGER_BG if col==C_DANGER else "white",
            co_td=8.8, co_nd=7.8, can="center" if w < 4.0 else "left", dy_text=0.44)

    hop(ax, 6.65, 0.62, 5.95, 1.15, "NGUYÊN TẮC AN TOÀN LÂM SÀNG",
        "• Vi phạm rõ ràng -> CHẶN (Chuyển mục Cần xác nhận)\n"
        "• Thiếu khẳng định -> CẢNH BÁO (Ưu tiên bác sĩ duyệt)\n"
        "• False-block rate <= 1.0% (Thực nghiệm kiểm chứng 0/30.136 dòng bị chặn oan)",
        vien=C_DANGER, nen=C_DANGER_BG, co_td=9.2, co_nd=8.0, can="left", dy_text=0.46)

    # --- KHUNG CON 3: TANG 5 (PHAN LUONG XUAT BAN & XEP CHO) ---
    khung_b3 = FancyBboxPatch((13.1, 0.45), 5.7, 5.85, boxstyle="round,pad=0.03,rounding_size=0.10",
                              linewidth=1.2, edgecolor="#94A3B8", facecolor="white")
    ax.add_patch(khung_b3)
    ax.text(13.35, 5.98, "IV. TẦNG 5: PHÂN LUỒNG XUẤT BẢN THEO RỦI RO",
            ha="left", va="center", fontsize=11, fontweight="bold", color=C_SAFE)
    ax.text(13.35, 5.68, "(Định tuyến tự động vào bản nháp theo mức độ rủi ro lâm sàng)",
            ha="left", va="center", fontsize=8.6, color=C_TEXT_MUTED)

    cac_ket_qua = [
        (13.3, 4.4, 5.3, 1.05, "1. QUA (ĐÃ KIỂM CHỨNG)",
         "Đưa vào thân bản nháp SOAP, kèm số lượt thoại căn cứ", C_SAFE, C_SAFE_BG),
        (13.3, 3.15, 5.3, 1.05, "2. CẢNH BÁO (NGUY CƠ CAO)",
         "Đưa vào thân bệnh án, xếp lên ĐẦU để bác sĩ xem xét trước", C_WARN, C_WARN_BG),
        (13.3, 1.90, 5.3, 1.05, "3. BỊ CHẶN (CẦN XÁC NHẬN)",
         "Cách ly vào mục 'Cần bác sĩ xác nhận', ghi rõ lý do vi phạm", C_DANGER, C_DANGER_BG),
        (13.3, 0.62, 5.3, 1.08, "4. BỊ THAY THẾ (ĐÃ ĐÍNH CHÍNH)",
         "Loại khỏi bản nháp; lưu vết Audit Trail đối soát pháp lý", C_GRAY, C_GRAY_BG),
    ]
    for x, y, w, h, td, nd, col, nen in cac_ket_qua:
        hop(ax, x, y, w, h, td, nd, vien=col, nen=nen, co_td=9.3, co_nd=8.3, can="left", dy_text=0.46)

    # Mui ten lien ket tu Pipeline xuong cac module duoi
    mui_ten(ax, 8.0, 7.05, 3.3, 6.35, mau="#4F6D8A", day=1.6)
    mui_ten(ax, 14.25, 7.05, 9.6, 6.35, mau="#B91C1C", day=1.6)
    mui_ten(ax, 17.3, 7.05, 15.95, 6.35, mau="#059669", day=1.6)

    # Luu ra hai noi: docs va brain artifact
    ten_tep = "so-do-tong-the-cac-tang.png"
    p1 = RA_DOCS / ten_tep
    p2 = RA_ARTIFACT / ten_tep
    fig.savefig(p1)
    fig.savefig(p2)
    plt.close(fig)
    print(f"Da tao thanh cong anh:\n-> {p1}\n-> {p2}")

if __name__ == "__main__":
    ve_tong_the()
