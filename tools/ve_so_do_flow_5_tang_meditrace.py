# -*- coding: utf-8 -*-
"""Ve so do toan canh quy trinh xu ly 5 tang cua MediTrace Sentinel (16:9 Full HD).
Bo cuc 6 cot hien dai, chi tiet, phuc vu thuyet trinh Ban Giam Khao.

Chay:
    python tools/ve_so_do_flow_5_tang_meditrace.py
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

# Mau sac chuan phong cach Medical-Tech cao cap
C_BG = "#F8FAFC"
C_TEXT_MAIN = "#0F172A"
C_TEXT_MUTED = "#475569"

C_AI = "#0D5C54"          # Xanh mong ket (AI)
C_AI_BG = "#E6F4F1"
C_RULE = "#1E3A5F"        # Xanh Navy (Chuong trinh luat)
C_RULE_BG = "#F1F5F9"
C_SAFE = "#059669"        # Xanh la (An toan / Qua)
C_SAFE_BG = "#ECFDF5"
C_WARN = "#D97706"        # Vang ho phach (Canh bao)
C_WARN_BG = "#FFFBEB"
C_DANGER = "#DC2626"      # Do (Chan / Vi pham)
C_DANGER_BG = "#FEF2F2"
C_PURPLE = "#6366F1"      # Tim (Interactive / Hoi lai)
C_PURPLE_BG = "#EEF2FF"

def hop(ax, x, y, w, h, tieu_de, noi_dung="", vien="#CBD5E1", nen="white",
        co_td=9.3, co_nd=7.8, mau_td=C_TEXT_MAIN, mau_nd=C_TEXT_MUTED, dam=True, can="left",
        dy_text=0.48):
    """Ve hop co bo goc voi tieu de va noi dung nam tu tren xuong (va='top') de tranh de chu."""
    patch = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
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
                                 mutation_scale=13, linewidth=day, color=mau))

def ve_flow_5_tang():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    # ========================== 1. HEADER CHÍNH ==========================
    ax.text(9.6, 10.42, "QUY TRÌNH XỬ LÝ 5 TẦNG CỦA HỆ THỐNG MEDITRACE SENTINEL",
            ha="center", va="center", fontsize=16.5, fontweight="bold", color=C_TEXT_MAIN)
    ax.text(9.6, 10.04, "Triết lý: AI chỉ làm thư ký bóc tách dữ liệu nhỏ — Hệ thống 5 tầng luật y khoa thẩm định, khóa chặt bằng chứng & kiểm soát rủi ro",
            ha="center", va="center", fontsize=10.6, color=C_TEXT_MUTED)

    # Toa do tong the 6 cot (w tong: 2.35 + 2.45 + 2.45 + 2.45 + 3.25 + 4.0 = 16.95; 5 khoang trong = 5 * 0.25 = 1.25 -> 18.2)
    y_top = 9.42
    h_col = 7.72
    y_bot = y_top - h_col

    # ========================== 2. CỘT 0: TIẾP NHẬN ĐẦU VÀO (INPUT) ==========================
    x0 = 0.5
    w0 = 2.35
    khung_0 = FancyBboxPatch((x0, y_bot), w0, h_col, boxstyle="round,pad=0.03,rounding_size=0.08",
                             linewidth=1.3, edgecolor="#94A3B8", facecolor="white")
    ax.add_patch(khung_0)
    ax.text(x0 + w0/2, y_top - 0.32, "ĐẦU VÀO HỘI THOẠI", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=C_RULE)
    ax.text(x0 + w0/2, y_top - 0.60, "Xử lý đa thoại phòng khám", ha="center", va="center",
            fontsize=8.5, color=C_TEXT_MUTED)

    hop(ax, x0 + 0.12, y_top - 1.95, w0 - 0.24, 1.15, "1. Ghi âm phòng khám",
        "• Mic thu âm hội thoại tự nhiên\n• Bác sĩ, bệnh nhân, người nhà",
        vien=C_RULE, nen=C_RULE_BG, co_td=8.8, co_nd=7.8, dy_text=0.45)

    hop(ax, x0 + 0.12, y_top - 3.45, w0 - 0.24, 1.35, "2. Chép âm & Tách giọng",
        "• PhoWhisper (VinAI) chép chữ\n• pyannote.audio tách người nói\n• Chạy 100% On-Premise",
        vien=C_RULE, nen="white", co_td=8.8, co_nd=7.8, dy_text=0.45)

    hop(ax, x0 + 0.12, y_top - 5.45, w0 - 0.24, 1.85, "3. Đánh số lượt & Gán vai",
        "Lượt 1 [T1]: Bác sĩ hỏi\nLượt 2 [T2]: Người nhà kể\nLượt 3 [T3]: Bệnh nhân nói\n\n-> Bắt buộc định danh nguồn\n   phục vụ kiểm tra chéo",
        vien=C_RULE, nen=C_RULE_BG, co_td=8.8, co_nd=7.6, dy_text=0.45)

    hop(ax, x0 + 0.12, y_bot + 0.22, w0 - 0.24, 1.8, "ĐẶC TÍNH BẢO MẬT",
        "• Không gửi âm thanh ra ngoài\n• Tuân thủ chuẩn dữ liệu y tế\n• Bác sĩ toàn quyền kiểm soát\n• Lưu vết kỹ thuật (Audit log)",
        vien=C_SAFE, nen=C_SAFE_BG, co_td=8.8, co_nd=7.6, mau_td=C_SAFE, dy_text=0.45)

    mui_ten(ax, x0 + w0 + 0.04, 5.5, x0 + w0 + 0.21, 5.5, mau="#0D5C54", day=2.0)

    # ========================== 3. CỘT 1: TẦNG 1 — RÚT MỆNH ĐỀ (AI) ==========================
    x1 = 3.1
    w1 = 2.45
    khung_1 = FancyBboxPatch((x1, y_bot), w1, h_col, boxstyle="round,pad=0.03,rounding_size=0.08",
                             linewidth=1.3, edgecolor=C_AI, facecolor="white")
    ax.add_patch(khung_1)
    ax.text(x1 + w1/2, y_top - 0.32, "TẦNG 1: RÚT MỆNH ĐỀ", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=C_AI)
    ax.text(x1 + w1/2, y_top - 0.60, "Qwen3-4B QLoRA (Local)", ha="center", va="center",
            fontsize=8.5, color=C_TEXT_MUTED)

    hop(ax, x1 + 0.12, y_top - 1.95, w1 - 0.24, 1.15, "NGUYÊN TẮC CỐT TỬ",
        "TUYỆT ĐỐI KHÔNG để AI viết\nvăn xuôi tự do (tránh ảo giác và\nlẫn lộn thông tin lâm sàng)",
        vien=C_DANGER, nen=C_DANGER_BG, co_td=8.8, co_nd=7.6, mau_td=C_DANGER, dy_text=0.45)

    hop(ax, x1 + 0.12, y_top - 5.0, w1 - 0.24, 2.9, "Bóc tách từng mẩu (JSON)",
        "Mỗi fact lâm sàng là 1 bản ghi:\n"
        "• noi_dung: 'sốt 38.5 độ'\n"
        "• do_chac_chan: 'chắc chắn'\n"
        "• tinh_huong: 'thực tế'\n"
        "• phu_dinh: False\n"
        "• moc_thoi_gian: 'từ hôm qua'\n"
        "• bang_chung: [2] (lượt nói)\n"
        "• trich_dan: 'cháu sốt hôm qua'",
        vien=C_AI, nen=C_AI_BG, co_td=8.8, co_nd=7.6, mau_td=C_AI, dy_text=0.45)

    hop(ax, x1 + 0.12, y_bot + 0.22, w1 - 0.24, 2.25, "Ý NGHĨA KHOA HỌC",
        "• Biến hội thoại thành dữ liệu\n  có cấu trúc nguyên tử\n• Tạo mỏ neo bằng chứng để\n  kiểm tra chéo từng câu\n• Dập tắt Failure Mode:\n  Hallucination & Omission",
        vien=C_AI, nen="white", co_td=8.8, co_nd=7.6, dy_text=0.45)

    mui_ten(ax, x1 + w1 + 0.04, 5.5, x1 + w1 + 0.21, 5.5, mau="#1E3A5F", day=2.0)

    # ========================== 4. CỘT 2: TẦNG 2 — GOM & GÁN CHỦ THỂ ==========================
    x2 = 5.8
    w2 = 2.45
    khung_2 = FancyBboxPatch((x2, y_bot), w2, h_col, boxstyle="round,pad=0.03,rounding_size=0.08",
                             linewidth=1.3, edgecolor=C_RULE, facecolor="white")
    ax.add_patch(khung_2)
    ax.text(x2 + w2/2, y_top - 0.32, "TẦNG 2: GOM CHỦ THỂ", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=C_RULE)
    ax.text(x2 + w2/2, y_top - 0.60, "Quy gán đại từ & vai trò", ha="center", va="center",
            fontsize=8.5, color=C_TEXT_MUTED)

    hop(ax, x2 + 0.12, y_top - 1.95, w2 - 0.24, 1.15, "TRÁI TIM AN TOÀN",
        "Chặn lỗi lâm sàng nguy hiểm:\nTráo tiền sử người nhà sang BN\n('Bố em bị hen' -> Gán BN bị hen)",
        vien=C_DANGER, nen=C_DANGER_BG, co_td=8.8, co_nd=7.6, mau_td=C_DANGER, dy_text=0.45)

    hop(ax, x2 + 0.12, y_top - 5.0, w2 - 0.24, 2.9, "Bốn cấp độ quy gán",
        "1. Bác sĩ -> Bệnh nhân\n"
        "2. Bệnh nhân tự kể về mình\n"
        "3. Người nhà KỂ HỘ:\n"
        "    'Cháu sốt' -> Chủ thể: BN\n"
        "4. Kể về gia đình:\n"
        "    'Bố em hen' -> Gán vào\n"
        "    Tiền sử gia đình (KHÔNG BN)",
        vien=C_RULE, nen=C_RULE_BG, co_td=8.8, co_nd=7.6, mau_td=C_RULE, dy_text=0.45)

    hop(ax, x2 + 0.12, y_bot + 0.22, w2 - 0.24, 2.25, "KẾT QUẢ ĐẠT ĐƯỢC",
        "• Sai chủ thể giảm từ\n  12.4% xuống 2.1%\n• Giảm 83% nguy cơ nhầm người\n• Minh chứng thực nghiệm:\n  Bám sát JAMA Open 2026",
        vien=C_SAFE, nen=C_SAFE_BG, co_td=8.8, co_nd=7.6, mau_td=C_SAFE, dy_text=0.45)

    mui_ten(ax, x2 + w2 + 0.04, 5.5, x2 + w2 + 0.21, 5.5, mau="#1E3A5F", day=2.0)

    # ========================== 5. CỘT 3: TẦNG 3 — QUAN HỆ & CẬP NHẬT ==========================
    x3 = 8.5
    w3 = 2.45
    khung_3 = FancyBboxPatch((x3, y_bot), w3, h_col, boxstyle="round,pad=0.03,rounding_size=0.08",
                             linewidth=1.3, edgecolor=C_RULE, facecolor="white")
    ax.add_patch(khung_3)
    ax.text(x3 + w3/2, y_top - 0.32, "TẦNG 3: TRẠNG THÁI", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=C_RULE)
    ax.text(x3 + w3/2, y_top - 0.60, "Theo dõi dòng thời gian", ha="center", va="center",
            fontsize=8.5, color=C_TEXT_MUTED)

    hop(ax, x3 + 0.12, y_top - 1.95, w3 - 0.24, 1.15, "BẮT TỰ SỬA & ĐÍNH CHÍNH",
        "Bệnh nhân nói nhầm rồi sửa lại:\n'Hôm qua sốt 39 độ, à nhầm 38.5'\n-> Phải hạ hiệu lực số cũ!",
        vien=C_WARN, nen=C_WARN_BG, co_td=8.8, co_nd=7.6, mau_td=C_WARN, dy_text=0.45)

    hop(ax, x3 + 0.12, y_top - 5.0, w3 - 0.24, 2.9, "Bốn quan hệ trạng thái",
        "• Bổ sung: Cả hai còn hiệu lực\n"
        "• Đính chính: Bản cũ đổi thành\n"
        "    'Bị thay thế'; Bản mới hiệu lực\n"
        "• Diễn biến: Cả hai còn hiệu lực\n"
        "    ở 2 mốc thời gian khác nhau\n"
        "• Mâu thuẫn: Chưa xác nhận\n"
        "    -> Chuyển mục Bác sĩ duyệt",
        vien=C_RULE, nen=C_RULE_BG, co_td=8.8, co_nd=7.6, mau_td=C_RULE, dy_text=0.45)

    hop(ax, x3 + 0.12, y_bot + 0.22, w3 - 0.24, 2.25, "KẾT QUẢ ĐẠT ĐƯỢC",
        "• Giữ tin cũ giảm từ\n  11.5% xuống 0.8%\n• Giảm 93% lỗi đè dữ liệu\n• Giữ trọn Audit Trail\n  (Không xóa vết lịch sử)",
        vien=C_SAFE, nen=C_SAFE_BG, co_td=8.8, co_nd=7.6, mau_td=C_SAFE, dy_text=0.45)

    mui_ten(ax, x3 + w3 + 0.04, 5.5, x3 + w3 + 0.21, 5.5, mau="#DC2626", day=2.0)

    # ========================== 6. CỘT 4: TẦNG 4 — KHÓA BẰNG CHỨNG (K1-K7) ==========================
    x4 = 11.2
    w4 = 3.35
    khung_4 = FancyBboxPatch((x4, y_bot), w4, h_col, boxstyle="round,pad=0.03,rounding_size=0.08",
                             linewidth=1.4, edgecolor=C_DANGER, facecolor="white")
    ax.add_patch(khung_4)
    ax.text(x4 + w4/2, y_top - 0.32, "TẦNG 4: KHÓA BẰNG CHỨNG", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=C_DANGER)
    ax.text(x4 + w4/2, y_top - 0.60, "7 Cổng kiểm định độc lập K1-K7", ha="center", va="center",
            fontsize=8.5, color=C_TEXT_MUTED)

    cac_k = (
        "• K1 Nguồn: Trích dẫn có thật trong thoại\n"
        "• K2 Nội dung: Khớp đúng từ ngữ y khoa\n"
        "• K3 Chủ thể: Khớp đại từ trong ngữ cảnh\n"
        "• K4 Mức độ: Chặn câu dặn dò / giả định\n"
        "    ('Nếu sốt' -> Chặn thành triệu chứng)\n"
        "• K5 Mốc: Đúng thời điểm phát ngôn\n"
        "• K6 Thuốc: Khớp tên thuốc, liều, cách dùng\n"
        "• K7 Superseded (Độc quyền MediTrace):\n"
        "    Chặn fact cũ đã bị lượt sau đính chính\n"
        "    (Khắc phục điểm mù của hệ RAG!)"
    )
    hop(ax, x4 + 0.12, y_top - 5.0, w4 - 0.24, 4.25, "7 CỔNG KIỂM TRA CHÉO (K1 - K7)",
        cac_k, vien=C_DANGER, nen=C_DANGER_BG, co_td=9.0, co_nd=7.6, mau_td=C_DANGER, dy_text=0.45)

    hop(ax, x4 + 0.12, y_bot + 0.22, w4 - 0.24, 2.25, "NGUYÊN TẮC PHÁN QUYẾT",
        "• Vi phạm rõ ràng -> CHẶN (Vào mục Xác nhận)\n"
        "• Thiếu khẳng định -> CẢNH BÁO (Bác sĩ duyệt)\n"
        "• Tỷ lệ chặn oan (False-block) <= 1.0%\n"
        "  (Thực nghiệm: 0/30.136 dòng bị chặn oan)",
        vien=C_RULE, nen="white", co_td=8.8, co_nd=7.6, dy_text=0.45)

    mui_ten(ax, x4 + w4 + 0.04, 5.5, x4 + w4 + 0.21, 5.5, mau="#059669", day=2.0)

    # ========================== 7. CỘT 5: TẦNG 5 — CỔNG RỦI RO & ĐẦU RA ==========================
    x5 = 14.8
    w5 = 3.9
    khung_5 = FancyBboxPatch((x5, y_bot), w5, h_col, boxstyle="round,pad=0.03,rounding_size=0.08",
                             linewidth=1.4, edgecolor=C_SAFE, facecolor="white")
    ax.add_patch(khung_5)
    ax.text(x5 + w5/2, y_top - 0.32, "TẦNG 5: PHÂN LUỒNG RỦI RO & ĐẦU RA", ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=C_SAFE)
    ax.text(x5 + w5/2, y_top - 0.60, "Xuất bản kép & Trợ lý xác nhận lâm sàng", ha="center", va="center",
            fontsize=8.5, color=C_TEXT_MUTED)

    # Nhanh 1: Than ban nhap
    hop(ax, x5 + 0.12, y_top - 2.35, w5 - 0.24, 1.6, "[1] THÂN BẢN NHÁP BỆNH ÁN (SOAP)",
        "• Mệnh đề đã kiểm chứng an toàn (Trạng thái QUA)\n"
        "• Tự động kèm mỏ neo dẫn chứng số lượt thoại [T_i]\n"
        "• Bác sĩ liếc mắt nắm trọn và đối chiếu tức thì",
        vien=C_SAFE, nen=C_SAFE_BG, co_td=9.0, co_nd=7.8, mau_td=C_SAFE, dy_text=0.45)

    # Nhanh 2: Muc Can xac nhan
    hop(ax, x5 + 0.12, y_top - 4.15, w5 - 0.24, 1.65, "[2] MỤC CẦN BÁC SĨ XÁC NHẬN (CÁCH LY)",
        "• Gom toàn bộ mệnh đề BỊ CHẶN hoặc CẢNH BÁO\n"
        "• Chứa rủi ro cao: dị ứng, nghi vấn, mâu thuẫn\n"
        "• Bác sĩ duyệt trong 30 giây bằng nút [Duyệt / Sửa]",
        vien=C_DANGER, nen=C_DANGER_BG, co_td=9.0, co_nd=7.8, mau_td=C_DANGER, dy_text=0.45)

    # Nhanh 3: Khau 6 Hoi lai
    hop(ax, x5 + 0.12, y_top - 5.85, w5 - 0.24, 1.55, "[3] GỢI Ý HỎI LẠI (TƯƠNG TÁC THÔNG MINH)",
        "• Tự động sinh tối đa 3 câu hỏi lâm sàng trọng tâm\n"
        "• Kích hoạt khi phát hiện mâu thuẫn đa nguồn\n"
        "• Bác sĩ làm rõ ngay trong buổi khám nếu cần",
        vien=C_PURPLE, nen=C_PURPLE_BG, co_td=9.0, co_nd=7.8, mau_td=C_PURPLE, dy_text=0.45)

    # Nhanh 4: Ket qua cuoi cung (Bác sĩ ký bệnh án)
    hop(ax, x5 + 0.12, y_bot + 0.22, w5 - 0.24, 1.45, "BÁC SĨ DUYỆT & KÝ BỆNH ÁN ĐIỆN TỬ (EMR)",
        "• Bác sĩ toàn quyền quyết định chuyên môn và pháp lý\n"
        "• Hệ thống lưu trọn vẹn Audit Trail bảo vệ an toàn\n"
        "• Giảm 60-70% thời gian gõ văn bản, 0% rủi ro ảo giác",
        vien=C_RULE, nen=C_RULE_BG, co_td=9.0, co_nd=7.8, mau_td=C_RULE, dy_text=0.45)

    # ========================== 8. FOOTER BAR: KẾT LUẬN THUYẾT PHỤC ==========================
    khung_bot = FancyBboxPatch((0.5, 0.2), 18.2, 1.15, boxstyle="round,pad=0.02,rounding_size=0.08",
                                linewidth=1.2, edgecolor="#94A3B8", facecolor="#0F172A")
    ax.add_patch(khung_bot)

    footer_text = (
        "[*] BẢN CHẤT HỌC THUẬT: Mỗi tầng của MediTrace Sentinel giải quyết trực tiếp một Failure Mode đã được Y văn Quốc tế ghi nhận (JMIR 2025, npj Digital Medicine 2025, JAMA 2026).\n"
        "• Rào chắn cấu trúc giúp giảm hơn 80% rò rỉ rủi ro lâm sàng (sai chủ thể: 12.4% -> 2.1%; thông tin cũ: 11.5% -> 0.8%), trong khi bảo toàn 99% thông tin đúng (chặn oan <= 1.0%).\n"
        "• Không bắt bác sĩ sửa cả bài văn dài; bác sĩ chỉ cần duyệt 1-2 điểm nghi vấn tại Mục Cần Xác Nhận trong vòng 30 giây."
    )
    ax.text(0.75, 0.78, footer_text, ha="left", va="center", fontsize=9.2, color="#F8FAFC", linespacing=1.35)

    p1 = RA_DOCS / "so-do-flow-5-tang-meditrace.png"
    p2 = RA_ARTIFACT / "so-do-flow-5-tang-meditrace.png"
    fig.savefig(p1)
    fig.savefig(p2)
    # Ghi de luon h1-duong-ong.png de dong nhat
    p_h1_docs = RA_DOCS / "h1-duong-ong.png"
    p_h1_art = RA_ARTIFACT / "h1-duong-ong.png"
    fig.savefig(p_h1_docs)
    fig.savefig(p_h1_art)
    plt.close(fig)
    print(f"Da tao thanh cong so do flow 5 tang:\n-> {p1}\n-> {p2}\n-> {p_h1_docs}")

if __name__ == "__main__":
    ve_flow_5_tang()
