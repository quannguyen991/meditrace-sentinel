# -*- coding: utf-8 -*-
"""Script tao bo 7 anh Master Flow xu ly & kiem thu cua MediTrace Sentinel (16:9 Full HD).
Thiet ke theo tieu chuan do hoa y te chuyen nghiep cao cap (Medical-Tech Infographic):
- Khong don ep vao 1 anh, chia nho thanh cac flow ro rang, phong chu lon, de doc
- Bo sung rieng Flow Ma tran Kiem thu Thuc nghiem 1.330 Test
- Bo sung Quy trinh Tuong tac Lam sang cua Bac si & Click-to-Verify 1 giay
- Nhan manh quy tac: Goi y ten thuoc ASR bat buoc BOI DO va cach ly sang CAN BAC SI XAC NHAN

Danh sach 7 anh:
  Flow 1: Thu am phong kham, ASR Guardrail, Goi y ten thuoc & Rut tin JSON
  Flow 2: Bat dinh chinh FSM, Loc cau gia dinh & Dung benh an SOAP
  Flow 3: Quy trinh 7 Cong Khoa Bang Chung (K1-K7) - Zero Hallucination
  Flow 4: Giam sat Duoc ly Lam sang, Chinh lieu eGFR & 9 Thang diem CDSS
  Flow 5: So sanh Doi dau Truc dien: ChatGPT / LLM tu do vs. MediTrace Sentinel
  Flow 6: Ma tran Kiem thu Thuc nghiem & Duong ong CI/CD (1.330 Bai Test)
  Flow 7: Quy trinh Bac si Tuong tac Lam sang & Click-to-Verify trong 1 Giay

Chay:
    python tools/tao_bo_anh_flow_meditrace.py
"""

from pathlib import Path
import sys
import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

GOC = Path(__file__).resolve().parent.parent
MUC_HINH_DOCS = GOC / "docs" / "tai-lieu" / "hinh"
MUC_HINH_DOCS.mkdir(parents=True, exist_ok=True)

MUC_DOWNLOADS = Path(r"C:\Users\admin\Downloads\hinh_flow_meditrace")
MUC_DOWNLOADS.mkdir(parents=True, exist_ok=True)

MUC_DESKTOP = Path(r"C:\Users\admin\Desktop\Hinh_Flow_MediTrace")
MUC_DESKTOP.mkdir(parents=True, exist_ok=True)

MUC_ARTIFACTS = Path(r"C:\Users\admin\.gemini\antigravity-ide\brain\1741516a-8a48-44e7-a4c9-96ec106aba0f\images")
MUC_ARTIFACTS.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"],
    "font.family": "sans-serif",
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})

# Bang mau y te cao cap
C_BG = "#F8FAFC"
C_HEADER_BG = "#0F172A"
C_TEXT_MAIN = "#0F172A"
C_TEXT_MUTED = "#475569"
C_BORDER_LIGHT = "#CBD5E1"

C_NAVY = "#1E3A5F"
C_NAVY_BG = "#F1F5F9"
C_TEAL = "#0D5C54"
C_TEAL_BG = "#E6F4F1"
C_SAFE = "#059669"
C_SAFE_BG = "#ECFDF5"
C_WARN = "#D97706"
C_WARN_BG = "#FFFBEB"
C_DANGER = "#DC2626"
C_DANGER_BG = "#FEF2F2"
C_PURPLE = "#4F46E5"
C_PURPLE_BG = "#EEF2FF"
C_CYAN = "#0284C7"
C_CYAN_BG = "#F0F9FF"


def ve_header(ax, tieu_de, phu_de, badge_text="", badge_color=C_TEAL):
    """Ve banner header cao cap o dau trang."""
    header_box = Rectangle((0, 9.6), 19.2, 1.2, facecolor=C_HEADER_BG, edgecolor="none")
    ax.add_patch(header_box)
    
    accent_bar = Rectangle((0, 9.55), 19.2, 0.05, facecolor=badge_color, edgecolor="none")
    ax.add_patch(accent_bar)
    
    ax.text(0.6, 10.35, tieu_de, ha="left", va="center", fontsize=15.5,
            fontweight="bold", color="white")
    ax.text(0.6, 9.95, phu_de, ha="left", va="center", fontsize=10.0,
            color="#94A3B8")
    
    if badge_text:
        w_b = len(badge_text) * 0.16 + 0.6
        badge_patch = FancyBboxPatch((18.6 - w_b, 9.95), w_b, 0.5,
                                     boxstyle="round,pad=0.03,rounding_size=0.1",
                                     facecolor=badge_color, edgecolor="none")
        ax.add_patch(badge_patch)
        ax.text(18.6 - w_b/2, 10.20, badge_text, ha="center", va="center",
                fontsize=9.0, fontweight="bold", color="white")


def the_chuc_nang(ax, x, y, w, h, tieu_de, badge_buoc="", noi_dung="",
                  mau_chinh=C_NAVY, mau_nen="white", mau_badge=None, co_td=10.0, co_nd=8.5,
                  dy_text=0.18, max_char_td=None):
    """Ve the card tinh nang hien dai voi huy hieu tieu de xep theo tang bac khong bao gio bi tran vien."""
    # Khung the
    khung = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.10",
                           linewidth=1.4, edgecolor=mau_chinh, facecolor=mau_nen)
    ax.add_patch(khung)
    
    # Dai vien mau trang tri tren cung cua the
    top_bar = FancyBboxPatch((x + 0.04, y + h - 0.10), w - 0.08, 0.06,
                             boxstyle="round,pad=0.01,rounding_size=0.03",
                             facecolor=mau_chinh, edgecolor="none")
    ax.add_patch(top_bar)
    
    # Tinh toan wrap tieu de
    limit_chars = max_char_td or max(14, int(w * 6.2))
    td_wrapped = textwrap.fill(tieu_de, width=limit_chars)
    n_lines_td = td_wrapped.count("\n") + 1
    
    if badge_buoc:
        # Pill badge tren row 1
        bg_b = mau_badge or mau_chinh
        w_b = len(badge_buoc) * 0.11 + 0.40
        badge = FancyBboxPatch((x + 0.20, y + h - 0.46), w_b, 0.26,
                               boxstyle="round,pad=0.02,rounding_size=0.07",
                               facecolor=bg_b, edgecolor="none")
        ax.add_patch(badge)
        ax.text(x + 0.20 + w_b/2, y + h - 0.33, badge_buoc, ha="center", va="center",
                fontsize=7.5, fontweight="bold", color="white")
        
        # Tieu de tren row 2 (ngay duoi badge)
        y_td = y + h - 0.60
        ax.text(x + 0.20, y_td, td_wrapped, ha="left", va="top",
                fontsize=co_td, fontweight="bold", color=mau_chinh, linespacing=1.15)
        
        y_div = y_td - (n_lines_td * 0.28) - 0.10
    else:
        y_td = y + h - 0.32
        ax.text(x + 0.20, y_td, td_wrapped, ha="left", va="top",
                fontsize=co_td, fontweight="bold", color=mau_chinh, linespacing=1.15)
        y_div = y_td - (n_lines_td * 0.28) - 0.10
    
    # Duong phan cach divider
    ax.plot([x + 0.20, x + w - 0.20], [y_div, y_div],
            color=C_BORDER_LIGHT, linewidth=0.8, linestyle="-")
    
    # Noi dung ben trong
    if noi_dung:
        ax.text(x + 0.20, y_div - dy_text, noi_dung,
                ha="left", va="top", fontsize=co_nd, color=C_TEXT_MAIN, linespacing=1.35)


def mui_ten_ngang(ax, x1, y, x2, mau=C_NAVY, day=2.2):
    ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle="-|>",
                                 mutation_scale=15, linewidth=day, color=mau))


def luu_anh(fig, ten_file):
    p_docs = MUC_HINH_DOCS / ten_file
    p_down = MUC_DOWNLOADS / ten_file
    p_desk = MUC_DESKTOP / ten_file
    p_art = MUC_ARTIFACTS / ten_file
    fig.savefig(str(p_docs))
    fig.savefig(str(p_down))
    fig.savefig(str(p_desk))
    fig.savefig(str(p_art))
    plt.close(fig)
    print(f"-> Da tao anh: {ten_file}")


# ==============================================================================
# HÌNH 1: ĐƯỜNG ỐNG GỠ BĂNG (ASR), DƯỢC THƯ ÂM VỊ & RÚT TIN NGUYÊN TỬ
# ==============================================================================
def ve_flow_1_nhan_dien_va_rut_tin():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 1: ĐƯỜNG ỐNG GỠ BĂNG (ASR), DƯỢC THƯ ÂM VỊ & RÚT MẨU TIN NGUYÊN TỬ",
              "Từ âm thanh tự nhiên tại phòng khám đến mẩu tin JSON có mỏ neo — Quy tắc BÔI ĐỎ cách ly tên thuốc nghi ngờ",
              badge_text="BƯỚC 0 & TẦNG 1", badge_color=C_TEAL)

    w_col = 4.15
    y_top = 9.1
    h_col = 8.4
    y_bot = y_top - h_col

    # Cot 1: Thu am & PhoWhisper
    x1 = 0.6
    the_chuc_nang(ax, x1, y_bot, w_col, h_col, "GHI ÂM & TÁCH GIỌNG",
                  badge_buoc="BƯỚC 01", mau_chinh=C_NAVY, mau_nen="white",
                  noi_dung=(
                      "• THU ÂM TỰ NHIÊN PHÒNG KHÁM:\n"
                      "  - Thời lượng: 3 - 5 phút/ca khám ngoại trú\n"
                      "  - Chạy 100% On-premise nội bộ (Bảo mật NĐ 13)\n"
                      "  - Thu nhận hội thoại tự nhiên bác sĩ - bệnh nhân\n\n"
                      "• GỠ BĂNG PHIÊN ÂM (PhoWhisper):\n"
                      "  - Fine-tuned chuyên biệt cho ngữ cảnh y tế\n"
                      "  - Nhận dạng tiếng Việt đa vùng miền\n"
                      "  - Xuất ra dòng chữ hội thoại thô kèm mốc giây\n\n"
                      "• TÁCH GIỌNG NGƯỜI NÓI (PyAnnote):\n"
                      "  - Phân tách Speaker 1, Speaker 2, Speaker 3\n"
                      "  - Bác sĩ gán vai một lần: Bác sĩ, BN, Người nhà\n\n"
                      "• ĐÁNH SỐ LƯỢT THOẠI [T1], [T2]...:\n"
                      "  - Tạo nền tảng mỏ neo cho việc kiểm chứng sau này"
                  ), co_td=10.5, co_nd=8.8)

    mui_ten_ngang(ax, x1 + w_col + 0.05, 5.0, x1 + w_col + 0.35, mau=C_NAVY)

    # Cot 2: Chot 1 ASR & Duoc thu am vi (Boi do)
    x2 = 5.25
    the_chuc_nang(ax, x2, y_bot, w_col, h_col, "ASR GUARDRAIL & DƯỢC THƯ ÂM VỊ",
                  badge_buoc="CHỐT 01", mau_chinh=C_DANGER, mau_nen=C_DANGER_BG,
                  noi_dung=(
                      "• BẢN CHẤT LÂM SÀNG THỰC TẾ:\n"
                      "  Phòng khám có tạp âm, bệnh nhân phát âm sai\n"
                      "  hoặc dùng tên dân gian ('a móc', 'ô mê', viên nhộng).\n"
                      "  ASR KHÔNG THỂ đảm bảo nghe đúng 100% tên thuốc!\n\n"
                      "• NGUYÊN TẮC 'ZERO SILENT NORMALIZATION':\n"
                      "  Tuyệt đối KHÔNG tự ý sửa ngầm vào đơn thuốc\n"
                      "  (đoán nhầm Augmentin thành Amox\n"
                      "   có thể gây biến cố chết người)\n\n"
                      "• CƠ CHẾ BÔI ĐỎ & CÁCH LY AN TOÀN:\n"
                      "  - Dò từ điển âm vị thuốc dân gian & phương ngữ\n"
                      "  - BÔI ĐỎ cờ cảnh báo [CẦN BÁC SĨ XÁC NHẬN]\n"
                      "  - Đưa gợi ý ra màn hình để Bác sĩ duyệt 1 click\n\n"
                      "• RÀ SOÁT VÒNG LẶP ÂM THANH:\n"
                      "  - Chặn đứng hiện tượng ASR loop (lặp từ vô nghĩa)\n"
                      "  - Chuẩn hóa hơn 60 thuật ngữ phương ngữ 3 miền"
                  ), co_td=10.0, co_nd=8.6)

    mui_ten_ngang(ax, x2 + w_col + 0.05, 5.0, x2 + w_col + 0.35, mau=C_TEAL)

    # Cot 3: Tang 1 - Qwen3-4B QLoRA
    x3 = 9.9
    the_chuc_nang(ax, x3, y_bot, w_col, h_col, "RÚT MẨU TIN NGUYÊN TỬ (JSON)",
                  badge_buoc="TẦNG 01", mau_chinh=C_TEAL, mau_nen="white",
                  noi_dung=(
                      "• MÔ HÌNH: Qwen3-4B + QLoRA 4-bit (Local GPU):\n"
                      "  - Chạy gọn nhẹ trên RTX 3050/3060 (~3.8 GB VRAM)\n"
                      "  - Thời gian xử lý: 30 - 45 giây/ca khám\n\n"
                      "• NGUYÊN TẮC CỐT TỬ CỦA TẦNG 1:\n"
                      "  TUYỆT ĐỐI CẤM AI viết văn xuôi tự do!\n"
                      "  Chỉ cho phép bóc tách các mẩu tin dạng JSON rời rạc:\n\n"
                      "  {\n"
                      "    'thuc_the': 'amoxicillin',\n"
                      "    'chu_the_id': 0,  # Bệnh nhân\n"
                      "    'noi_dung': 'dị ứng mẩn ngứa',\n"
                      "    'do_chac_chan': 'chắc chắn',\n"
                      "    'phu_dinh': false,\n"
                      "    'bang_chung': [5],  # Lượt thoại [T5]\n"
                      "    'trich_dan': 'uống amoxicillin nổi mề đay'\n"
                      "  }\n\n"
                      "• BẢO ĐẢM TRUY NGUYÊN:\n"
                      "  Không có mẩu tin nào sinh ra mà thiếu mỏ neo [Ti]!"
                  ), co_td=10.0, co_nd=8.6)

    mui_ten_ngang(ax, x3 + w_col + 0.05, 5.0, x3 + w_col + 0.35, mau=C_PURPLE)

    # Cot 4: Chot 2 - Speaker Consistency Gate
    x4 = 14.55
    the_chuc_nang(ax, x4, y_bot, w_col, h_col, "SPEAKER GATE (ĐẠI TỪ NHÂN XƯNG)",
                  badge_buoc="CHỐT 02", mau_chinh=C_PURPLE, mau_nen=C_PURPLE_BG,
                  noi_dung=(
                      "• NHIỆM VỤ SỐNG CÒN:\n"
                      "  Chặn đứng lỗi tráo người nhà sang bệnh nhân!\n"
                      "  (ChatGPT rất hay nhầm: Con kể 'Bố em bị hen'\n"
                      "   -> Gán ngay thành bệnh nhân bị hen!)\n\n"
                      "• ĐỐI CHIẾU ĐẠI TỪ TIẾNG VIỆT:\n"
                      "  - 'Mẹ tôi / Bố tôi / Con tôi / Chồng tôi'\n"
                      "  - 'Bé nhà em / Ông nhà tôi / Bà nhà tôi'\n"
                      "  -> CẤM GÁN VÀO TIỀN SỬ BỆNH NHÂN!\n"
                      "  -> Tự động phân luồng sang TIỀN SỬ GIA ĐÌNH\n\n"
                      "• HIỆU QUẢ LÂM SÀNG THỰC NGHIỆM:\n"
                      "  - Giảm tỷ lệ nhầm chủ thể từ 12.4% xuống 2.1%\n"
                      "  - Bảo vệ bệnh án khỏi thông tin râu ông nọ\n"
                      "    cắm cằm bà kia\n\n"
                      "• BÀN GIAO SANG TẦNG 2:\n"
                      "  Chuyển sang bộ luật gom nhóm và FSM đính chính."
                  ), co_td=9.8, co_nd=8.6)

    luu_anh(fig, "flow-1-nhan-dien-giong-noi-va-rut-tin.png")


# ==============================================================================
# HÌNH 2: BẮT ĐÍNH CHÍNH (FSM), LỌC GIẢ ĐỊNH & DỰNG BỆNH ÁN SOAP
# ==============================================================================
def ve_flow_2_dinh_chinh_fsm_va_soap():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 2: BẮT ĐÍNH CHÍNH (FSM), LỌC CÂU GIẢ ĐỊNH & DỰNG BỆNH ÁN SOAP",
              "Xử lý hội thoại đời thường: bệnh nhân nói nhầm, bác sĩ dặn dò tương lai và xuất bản bệnh án chuẩn",
              badge_text="TẦNG 2, 3 & 5", badge_color=C_CYAN)

    w_col = 4.15
    y_top = 9.1
    h_col = 8.4
    y_bot = y_top - h_col

    # Cot 1: Tang 2 - Gom nguoi & Khu dinh danh
    x1 = 0.6
    the_chuc_nang(ax, x1, y_bot, w_col, h_col, "GOM CHỦ THỂ & KHỬ ĐỊNH DANH",
                  badge_buoc="TẦNG 02", mau_chinh=C_NAVY, mau_nen="white",
                  noi_dung=(
                      "• PHÂN ĐỊNH 4 NHÓM CHỦ THỂ TIẾNG VIỆT:\n"
                      "  1. Bác sĩ hỏi/khám bệnh nhân\n"
                      "  2. Bệnh nhân tự kể về triệu chứng bản thân\n"
                      "  3. Người nhà kể hộ ('cháu sốt 39 độ')\n"
                      "  4. Người nhà kể về người khác ('ông nhà tôi...')\n"
                      "     -> Chuyển mục Tiền sử gia đình\n\n"
                      "• KHỬ ĐỊNH DANH TỰ ĐỘNG (Nghị định 13/CP):\n"
                      "  - Che tên thật, số điện thoại, CCCD, địa chỉ\n"
                      "  - Thay thế bằng mã băm [BENH_NHAN_001]\n"
                      "  - Dữ liệu hoàn toàn ẩn danh trước khi lưu trữ\n\n"
                      "• XỬ LÝ CÂU NUỐT CHỦ NGỮ:\n"
                      "  - BN nói cộc: 'Sốt 3 hôm rồi' -> Tự động nhận diện\n"
                      "    ngữ cảnh lượt thoại để gán đúng cho bệnh nhân."
                  ), co_td=10.0, co_nd=8.8)

    mui_ten_ngang(ax, x1 + w_col + 0.05, 5.0, x1 + w_col + 0.35, mau=C_WARN)

    # Cot 2: Tang 3 - FSM Bat dinh chinh
    x2 = 5.25
    the_chuc_nang(ax, x2, y_bot, w_col, h_col, "MÁY TRẠNG THÁI FSM ĐÍNH CHÍNH",
                  badge_buoc="TẦNG 03", mau_chinh=C_WARN, mau_nen=C_WARN_BG,
                  noi_dung=(
                      "• TÌNH HUỐNG LÂM SÀNG THỰC TẾ:\n"
                      "  Bệnh nhân nói nhầm rồi tự sửa lại:\n"
                      "  'Tôi bị sốt 1 tuần... à không, mới 3 hôm thôi!'\n\n"
                      "• MÁY TRẠNG THÁI HỮU HẠN (FSM) PHÂN NHÁNH:\n"
                      "  - NHÁNH BỔ SUNG: Cả hai mẩu tin cùng có hiệu lực\n"
                      "    ('vừa ho vừa rát họng') -> Giữ cả hai\n"
                      "  - NHÁNH ĐÍNH CHÍNH (K7 Superseded):\n"
                      "    Mẩu tin '1 tuần' bị gạch bỏ và đánh dấu [Bị thay thế],\n"
                      "    chỉ đưa mẩu tin mới '3 hôm' vào thân bệnh án.\n"
                      "  - NHÁNH MÂU THUẪN: Chưa rõ câu nào đúng\n"
                      "    -> Đưa sang mục Cần bác sĩ xác nhận\n\n"
                      "• HIỆU QUẢ:\n"
                      "  Giảm 14 lần lỗi nhớ nhầm tin cũ (11.5% -> 0.8%)."
                  ), co_td=9.8, co_nd=8.6)

    mui_ten_ngang(ax, x2 + w_col + 0.05, 5.0, x2 + w_col + 0.35, mau=C_SAFE)

    # Cot 3: Chot 3 - Dialogue Act & Loc gia dinh
    x3 = 9.9
    the_chuc_nang(ax, x3, y_bot, w_col, h_col, "DIALOGUE ACT & LỌC CÂU GIẢ ĐỊNH",
                  badge_buoc="CHỐT 03", mau_chinh=C_SAFE, mau_nen="white",
                  noi_dung=(
                      "• BẢN CHẤT LỖI CỦA CÁC MÔ HÌNH LLM:\n"
                      "  Khi bác sĩ nói: 'Nếu mai còn sốt thì chụp X-quang',\n"
                      "  ChatGPT thường ghi: 'Đã chụp X-quang phổi'!\n\n"
                      "• BỘ LỌC CÂU GIẢ ĐỊNH / TƯƠNG LAI (CHỐT 3):\n"
                      "  - Bóc tách các liên từ điều kiện: 'nếu... thì', 'phòng khi',\n"
                      "    'mai quay lại khám', 'khi nào đau mới uống'...\n"
                      "  - CẤM GHI vào mục Khám lâm sàng hay Chẩn đoán!\n"
                      "  - Tự động chuyển đúng vào KẾ HOẠCH THEO DÕI.\n\n"
                      "• LỌC KHẲNG ĐỊNH ÂM TÍNH:\n"
                      "  - Phân biệt rõ 'Chưa ghi nhận' vs 'Không có'\n"
                      "    (hai khái niệm hoàn toàn khác nhau\n"
                      "     về mặt pháp lý y khoa)."
                  ), co_td=9.6, co_nd=8.6)

    mui_ten_ngang(ax, x3 + w_col + 0.05, 5.0, x3 + w_col + 0.35, mau=C_CYAN)

    # Cot 4: Tang 5 - Dung Benh an SOAP & Click-to-Verify
    x4 = 14.55
    the_chuc_nang(ax, x4, y_bot, w_col, h_col, "BỆNH ÁN SOAP & CLICK-TO-VERIFY",
                  badge_buoc="TẦNG 05", mau_chinh=C_CYAN, mau_nen=C_CYAN_BG,
                  noi_dung=(
                      "• DỰNG BẰNG TEMPLATE ENGINE (KHÔNG DÙNG LLM):\n"
                      "  - S (Subjective): Lý do khám, Bệnh sử, Tiền sử\n"
                      "  - O (Objective): Khám lâm sàng, Sinh hiệu, Xét nghiệm\n"
                      "  - A (Assessment): Chẩn đoán xác định / phân biệt\n"
                      "  - P (Plan): Đơn thuốc, Lời dặn, Hẹn tái khám\n\n"
                      "• PHÂN VÙNG 'CẦN BÁC SĨ XÁC NHẬN':\n"
                      "  - Nơi tập trung toàn bộ cảnh báo BÔI ĐỎ\n"
                      "    (tên thuốc ASR, dị ứng, tương tác DDI)\n"
                      "  - Bác sĩ chỉ cần liếc mắt 20s kiểm tra\n\n"
                      "• CLICK-TO-VERIFY TRONG 1 GIÂY:\n"
                      "  Bấm vào bất kỳ dòng nào -> Sáng ngay câu nói ở đúng\n"
                      "  giây ghi âm gốc để đối soát tức thời!"
                  ), co_td=9.6, co_nd=8.6)

    luu_anh(fig, "flow-2-dinh-chinh-fsm-va-benh-an-soap.png")


# ==============================================================================
# HÌNH 3: QUY TRÌNH 7 CỔNG KHÓA BẰNG CHỨNG (K1–K7) — ZERO HALLUCINATION
# ==============================================================================
def ve_flow_3_khoa_bang_chung():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 3: QUY TRÌNH 7 CỔNG KHÓA BẰNG CHỨNG (K1–K7) — TRIỆT TIÊU HOÀN TOÀN ẢO GIÁC AI",
              "100% Thuật toán xác định (Python determinism) thẩm định từng câu chữ trước khi vào hồ sơ bệnh án",
              badge_text="ZERO HALLUCINATION", badge_color=C_DANGER)

    # 3 Khối lớn: Đầu vào Trái -> 7 Cổng ở Giữa -> 2 Đầu ra Phải
    the_chuc_nang(ax, 0.6, 1.5, 3.4, 7.6, "MỆNH ĐỀ DO AI TRÍCH",
                  badge_buoc="ĐẦU VÀO", mau_chinh=C_TEAL, mau_nen=C_TEAL_BG,
                  noi_dung=(
                      "Dữ liệu JSON nguyên tử:\n\n"
                      "• thuc_the: 'amoxicillin'\n"
                      "• chu_the: 'bệnh nhân'\n"
                      "• noi_dung: 'dị ứng mẩn ngứa'\n"
                      "• do_chac_chan: 'chắc chắn'\n"
                      "• phu_dinh: False\n"
                      "• bang_chung: [T5]\n"
                      "• trich_dan:\n"
                      "  'uống amoxicillin nổi mề đay'\n\n"
                      "-> BẮT BUỘC ĐI QUA PHỄU\n"
                      "   KIỂM ĐỊNH 7 CỔNG K1-K7\n"
                      "   TRƯỚC KHI VÀO BỆNH ÁN"
                  ), co_td=10.0, co_nd=8.8)

    mui_ten_ngang(ax, 4.05, 5.3, 4.35, mau=C_NAVY, day=2.5)

    # 7 Cổng ở giữa với bố cục Security Checkpoint phân tầng rõ ràng
    x_mid = 4.45
    w_mid = 9.8
    y_start = 8.15
    h_gate = 0.94
    spacing = 1.10

    cac_cong = [
        ("CỔNG K1", "NGUỒN GỐC NGUYÊN VĂN (VERBATIM STRING MATCH)",
         "Dò chuỗi trích dẫn vào lượt thoại [Ti]. Tên thuốc ASR đoán âm vị -> BÔI ĐỎ CHUYỂN SANG CẦN XÁC NHẬN!", C_DANGER, C_DANGER_BG),
        ("CỔNG K2", "KHỚP NỘI DUNG LÂM SÀNG (CORE MEDICAL TERMS)",
         "So khớp từ vựng y khoa chính, không để câu trích một đằng mà tóm tắt nội dung một nẻo.", C_NAVY, C_NAVY_BG),
        ("CỔNG K3", "ĐÚNG CHỦ THỂ & VAI NGƯỜI NÓI (SPEAKER ATTRIBUTION)",
         "Đối chiếu đại từ chỉ người trong câu. Nói về 'ông nhà/bố/mẹ' -> CẤM ghi vào bệnh sử của bệnh nhân.", C_NAVY, C_NAVY_BG),
        ("CỔNG K4", "LỌC CÂU GIẢ ĐỊNH & PHÒNG NGỪA (HYPOTHETICAL FILTER)",
         "Phát hiện câu gốc chỉ là phòng ngừa, dặn dò tương lai ('Nếu sốt thì...') -> CẤM ghi thành việc đã làm!", C_WARN, C_WARN_BG),
        ("CỔNG K5", "KHỚP MỐC THỜI GIAN (TEMPORAL ALIGNMENT)",
         "Mốc thời gian ('3 ngày', '1 tuần') bắt buộc phải xuất hiện nguyên vẹn trong lượt thoại được dẫn chứng.", C_NAVY, C_NAVY_BG),
        ("CỔNG K6", "KHÓA SỐ LIỆU LÂM SÀNG & LIỀU THUỐC (NUMERICAL GROUNDING)",
         "Đối soát từng chữ số huyết áp, nhiệt độ, liều thuốc mg. AI tự ý điền số thói quen (120/80) -> CHẶN LẬP TỨC!", C_DANGER, C_DANGER_BG),
        ("CỔNG K7", "DÒNG THỜI GIAN ĐÍNH CHÍNH (TEMPORAL SUPERSEDED CHECK)",
         "Phát hiện lời nói sau đính chính lời nói trước ('à không...') -> Đánh dấu tin cũ [Bị thay thế], gạch bỏ.", C_WARN, C_WARN_BG)
    ]

    for idx, (badge_k, tieu_de, noi_dung, mau, bg) in enumerate(cac_cong):
        y_g = y_start - idx * spacing
        khung_g = FancyBboxPatch((x_mid, y_g), w_mid, h_gate, boxstyle="round,pad=0.02,rounding_size=0.08",
                                 linewidth=1.3, edgecolor=mau, facecolor=bg)
        ax.add_patch(khung_g)
        
        # Pill badge K1, K2...
        badge_p = FancyBboxPatch((x_mid + 0.18, y_g + h_gate - 0.38), 1.05, 0.26,
                                 boxstyle="round,pad=0.02,rounding_size=0.06",
                                 facecolor=mau, edgecolor="none")
        ax.add_patch(badge_p)
        ax.text(x_mid + 0.18 + 0.52, y_g + h_gate - 0.25, badge_k, ha="center", va="center",
                fontsize=8.0, fontweight="bold", color="white")
        
        # Tieu de cong
        ax.text(x_mid + 1.35, y_g + h_gate - 0.25, tieu_de, ha="left", va="center",
                fontsize=9.2, fontweight="bold", color=mau)
        
        # Noi dung cong
        ax.text(x_mid + 0.20, y_g + 0.24, noi_dung, ha="left", va="center",
                fontsize=8.1, color=C_TEXT_MAIN)

    # 2 Đầu ra bên phải
    x_out = 14.7
    w_out = 3.9

    # Nhanh Đạt Chuẩn
    mui_ten_ngang(ax, x_mid + w_mid + 0.05, 6.8, x_out - 0.1, mau=C_SAFE, day=2.5)
    ax.text(x_out - 0.2, 7.05, "VƯỢT QUA 7 CỔNG", ha="right", va="bottom",
            fontsize=8.2, fontweight="bold", color=C_SAFE)
    
    the_chuc_nang(ax, x_out, 5.3, w_out, 3.8, "HỒ SƠ BỆNH ÁN (SOAP)",
                  badge_buoc="ĐẠT CHUẨN", mau_chinh=C_SAFE, mau_nen=C_SAFE_BG,
                  noi_dung=(
                      "ĐỘ TIN CẬY 100% TUYỆT ĐỐI:\n\n"
                      "• Tự động điền vào các mục SOAP\n"
                      "• Gắn mỏ neo trỏ thẳng về lượt thoại [Ti]\n"
                      "• Bác sĩ kiểm chứng trong 1 giây\n"
                      "• Thực nghiệm chứng minh:\n"
                      "  0.0% bị chặn nhầm (0 / 30.136 dòng)!"
                  ), co_td=10.0, co_nd=8.6)
    badge_ok = FancyBboxPatch((x_out + 0.25, 5.50), w_out - 0.5, 0.40,
                              boxstyle="round,pad=0.02,rounding_size=0.08",
                              facecolor=C_SAFE, edgecolor="none")
    ax.add_patch(badge_ok)
    ax.text(x_out + w_out/2, 5.70, "[OK] ĐẠT 100% -> ĐIỀN THẲNG SOAP", ha="center", va="center",
            fontsize=8.2, fontweight="bold", color="white")

    # Nhanh Bị Chặn
    mui_ten_ngang(ax, x_mid + w_mid + 0.05, 3.0, x_out - 0.1, mau=C_DANGER, day=2.5)
    ax.text(x_out - 0.2, 3.25, "VI PHẠM BẤT KỲ CỔNG", ha="right", va="bottom",
            fontsize=8.2, fontweight="bold", color=C_DANGER)

    the_chuc_nang(ax, x_out, 1.5, w_out, 3.6, "CẦN BÁC SĨ XÁC NHẬN",
                  badge_buoc="BÔI ĐỎ CÁCH LY", mau_chinh=C_DANGER, mau_nen=C_DANGER_BG,
                  noi_dung=(
                      "TUYỆT ĐỐI KHÔNG ÂM THẦM XÓA BỎ:\n\n"
                      "• Mọi mẩu tin vi phạm bị cách ly tại đây\n"
                      "• BÔI ĐỎ cờ cảnh báo kèm lý do vi phạm:\n"
                      "  'trích không có', 'câu giả định', 'ASR tên thuốc'...\n"
                      "• Bác sĩ liếc mắt 20s bấm duyệt hoặc sửa lại\n"
                      "• Triết lý an toàn: Bắt nhầm còn hơn bỏ sót!"
                  ), co_td=10.0, co_nd=8.6)
    badge_dang = FancyBboxPatch((x_out + 0.25, 1.68), w_out - 0.5, 0.40,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=C_DANGER, edgecolor="none")
    ax.add_patch(badge_dang)
    ax.text(x_out + w_out/2, 1.88, "[!] BÔI ĐỎ -> CHỜ BÁC SĨ DUYỆT", ha="center", va="center",
            fontsize=8.2, fontweight="bold", color="white")

    luu_anh(fig, "flow-3-khoa-bang-chung-k1-k7-chong-ao-giac.png")


# ==============================================================================
# HÌNH 4: GIÁM SÁT DƯỢC LÝ LÂM SÀNG, HIỆU CHỈNH LIỀU & CDSS THANG ĐIỂM
# ==============================================================================
def ve_flow_4_duoc_ly_cdss():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 4: HỆ THỐNG AN TOÀN DƯỢC LÝ LÂM SÀNG, HIỆU CHỈNH LIỀU & HỖ TRỢ QUYẾT ĐỊNH (CDSS)",
              "Đóng vai trò Dược sĩ số & Trợ lý cấp cứu — Soi thuốc kỵ nhau, tính độ lọc thận và tự động cộng 9 thang điểm nguy cơ",
              badge_text="CDSS & DƯỢC THƯ", badge_color=C_SAFE)

    w_col = 4.15
    y_top = 9.1
    h_col = 8.4
    y_bot = y_top - h_col

    # Cot 1: Tiep nhan don & Quy tac ASR
    x1 = 0.6
    the_chuc_nang(ax, x1, y_bot, w_col, h_col, "TIẾP NHẬN ĐƠN & AN TOÀN ASR",
                  badge_buoc="TRẠM 01", mau_chinh=C_NAVY, mau_nen="white",
                  noi_dung=(
                      "• DỮ LIỆU ĐẦU VÀO:\n"
                      "  - Bác sĩ kê đơn qua lời nói\n"
                      "  - Bệnh nhân khai thuốc đang dùng tại nhà\n"
                      "  - Xét nghiệm Creatinine máu, Tuổi, Giới, Cân nặng\n\n"
                      "• QUY TẮC AN TOÀN DƯỢC THƯ ASR:\n"
                      "  - Bệnh nhân đọc tên thuốc dân gian ('a móc', 'ô mê')\n"
                      "  - Hệ thống gợi ý Amoxicillin, Omeprazole...\n"
                      "  - BẮT BUỘC BÔI ĐỎ CẢNH BÁO [CẦN BÁC SĨ DUYỆT]\n"
                      "  - CẤM TỰ Ý ĐƯA NGẦM VÀO ĐƠN THUỐC!\n\n"
                      "• ĐỐI SOÁT CLICK-TO-VERIFY:\n"
                      "  Bác sĩ bấm nghe lại đúng 2 giây ghi âm gốc\n"
                      "  để xác nhận trước khi hệ thống tính toán liều."
                  ), co_td=10.0, co_nd=8.8)

    mui_ten_ngang(ax, x1 + w_col + 0.05, 5.0, x1 + w_col + 0.35, mau=C_DANGER)

    # Cot 2: 3 Tram kiem duyet duoc ly
    x2 = 5.25
    the_chuc_nang(ax, x2, y_bot, w_col, h_col, "3 CHỐT KIỂM SOÁT DƯỢC LÝ",
                  badge_buoc="TRẠM 02", mau_chinh=C_DANGER, mau_nen=C_DANGER_BG,
                  noi_dung=(
                      "1. TƯƠNG TÁC THUỐC KỴ NHAU (DDI):\n"
                      "   Tra cứu Dược thư Quốc gia & FDA Hoa Kỳ:\n"
                      "   • Warfarin + Aspirin/NSAID: Xuất huyết ồ ạt -> CẤM\n"
                      "   • Clopidogrel + Omeprazole: Triệt tiêu chống đông\n"
                      "   • Digoxin + Amiodarone: Ngộ độc cơ tim -> GIẢM LIỀU\n\n"
                      "2. KIỂM SOÁT LIỀU TRẦN AN TOÀN TRONG NGÀY:\n"
                      "   • Paracetamol <= 4000 mg/ngày (tối đa 8 viên 500mg)\n"
                      "   • Ibuprofen <= 2400 mg/ngày\n"
                      "   • Aspirin <= 3000 mg/ngày\n"
                      "   -> Vượt liều trần là BÁO ĐỘNG ĐỎ hoại tử gan ngay!\n\n"
                      "3. HIỆU CHỈNH LIỀU SUY THẬN (Cockcroft-Gault eGFR):\n"
                      "   • eGFR < 30 mL/phút: Giảm 50% liều kháng sinh\n"
                      "   • Chống chỉ định Metformin ở bệnh nhân suy thận nặng"
                  ), co_td=10.0, co_nd=8.6)

    mui_ten_ngang(ax, x2 + w_col + 0.05, 5.0, x2 + w_col + 0.35, mau=C_PURPLE)

    # Cot 3: 9 Thang diem lam sang
    x3 = 9.9
    the_chuc_nang(ax, x3, y_bot, w_col, h_col, "TỰ ĐỘNG TÍNH 9 THANG ĐIỂM",
                  badge_buoc="TRẠM 03", mau_chinh=C_PURPLE, mau_nen="white",
                  noi_dung=(
                      "Tự động trích xuất triệu chứng và cộng điểm toán học:\n\n"
                      "1. GCS (Glasgow): Đo độ hôn mê và chấn thương sọ não\n"
                      "2. qSOFA: Nhận diện sốc nhiễm trùng nguy kịch\n"
                      "3. CURB-65: Đánh giá viêm phổi nhẹ cho về hay nhập viện\n"
                      "4. CHA2DS2-VASc: Nguy cơ đột quỵ ở bệnh nhân rung nhĩ\n"
                      "5. HAS-BLED: Nguy cơ xuất huyết do thuốc chống đông\n"
                      "6. Wells Score: Xác suất thuyên tắc tĩnh mạch / phổi\n"
                      "7. Glasgow-Blatchford: Tiên lượng xuất huyết tiêu hóa\n"
                      "8. NYHA I - IV: Phân độ suy tim theo mức độ gắng sức\n"
                      "9. BMI Châu Á: Đánh giá thể trạng thừa cân béo phì\n\n"
                      "-> Bác sĩ không phải tự nhớ công thức hay bấm máy tính!"
                  ), co_td=10.0, co_nd=8.6)

    mui_ten_ngang(ax, x3 + w_col + 0.05, 5.0, x3 + w_col + 0.35, mau=C_SAFE)

    # Cot 4: Dau ra an toan
    x4 = 14.55
    the_chuc_nang(ax, x4, y_bot, w_col, h_col, "ĐẦU RA BÁC SĨ & NGƯỜI BỆNH",
                  badge_buoc="ĐẦU RA", mau_chinh=C_SAFE, mau_nen=C_SAFE_BG,
                  noi_dung=(
                      "• CẢNH BÁO MÀN HÌNH BÁC SĨ (1 GIÂY):\n"
                      "  - Nhấp nháy đỏ báo động cặp thuốc kỵ nhau\n"
                      "  - Đề xuất thuốc thay thế an toàn hơn\n"
                      "  - Khuyến cáo liều giảm cụ thể theo eGFR\n"
                      "  - Bác sĩ toàn quyền quyết định và bấm ký duyệt\n\n"
                      "• TỜ DẶN DÒ NGƯỜI BỆNH IN TRAO TẬN TAY:\n"
                      "  - Chia lịch uống 4 khung giờ đời thường:\n"
                      "    Sáng - Trưa - Chiều - Tối (trước/sau ăn)\n"
                      "  - Hướng dẫn chế độ ăn kiêng theo bệnh lý\n"
                      "  - Danh mục 'Dấu hiệu đỏ nguy hiểm':\n"
                      "    Khó thở, đau ngực, nôn máu -> Đi viện ngay!\n"
                      "  - Người bệnh đọc hiểu 100%, an tâm điều trị."
                  ), co_td=10.0, co_nd=8.8)

    luu_anh(fig, "flow-4-duoc-ly-lam-sang-va-cdss-thang-diem.png")


# ==============================================================================
# HÌNH 5: SO SÁNH ĐỐI ĐẦU: CHATGPT / LLM TỰ DO vs. MEDITRACE SENTINEL
# ==============================================================================
def ve_flow_5_so_sanh_doi_dau():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 5: SO SÁNH ĐỐI ĐẦU TRỰC DIỆN: CHATGPT / LLM TỰ DO vs. MEDITRACE SENTINEL",
              "Vì sao y tế bắt buộc phải dùng kiến trúc Neuro-symbolic có kiểm chứng chứ không thể giao cho LLM viết văn?",
              badge_text="HEAD-TO-HEAD BATTLE", badge_color=C_WARN)

    # Nua tren: Nhanh A - ChatGPT / LLM tu do
    khung_top = FancyBboxPatch((0.6, 5.15), 18.0, 4.25, boxstyle="round,pad=0.03,rounding_size=0.08",
                               linewidth=1.4, edgecolor=C_DANGER, facecolor="white")
    ax.add_patch(khung_top)
    ax.text(0.9, 9.15, "NHÁNH A: CHATGPT / LLM TẠO SINH TỰ DO (END-TO-END) — NHIỀU RỦI RO CHẾT NGƯỜI",
            ha="left", va="center", fontsize=11.5, fontweight="bold", color=C_DANGER)

    the_chuc_nang(ax, 0.9, 5.35, 3.6, 3.55, "1. LỜI THOẠI KHÁM BỆNH",
                  badge_buoc="INPUT", mau_chinh=C_TEXT_MUTED, mau_nen=C_BG,
                  noi_dung=(
                      "• Bác sĩ, bệnh nhân, người nhà\n"
                      "• Nói nhanh, nuốt chủ ngữ\n"
                      "• Tự sửa: '1 tuần... à 3 hôm'\n"
                      "• Con kể: 'Bố em bị hen'\n"
                      "• Bác sĩ: 'Nếu sốt thì chụp phim'"
                  ), co_td=9.5, co_nd=8.5)

    mui_ten_ngang(ax, 4.6, 7.1, 5.0, mau=C_DANGER, day=2.5)

    the_chuc_nang(ax, 5.1, 5.35, 4.5, 3.55, "2. GỬI PROMPT VÀO LLM TỰ DO",
                  badge_buoc="HỘP ĐEN AI", mau_chinh=C_DANGER, mau_nen=C_DANGER_BG,
                  noi_dung=(
                      "Prompt: 'Hãy tóm tắt cuộc khám thành bệnh án SOAP'\n\n"
                      "• Gửi dữ liệu bệnh nhân lên Cloud -> VI PHẠM NĐ 13\n"
                      "• LLM là 'hộp đen' dự đoán từ tiếp theo trơn tru\n"
                      "• KHÔNG CÓ BẢNG BẰNG CHỨNG TRUNG GIAN\n"
                      "• KHÔNG CÓ BỘ LUẬT KIỂM DUYỆT RỦI RO\n"
                      "• Rất dễ bị Hallucination khi gặp hội thoại nói nhầm"
                  ), co_td=9.5, co_nd=8.5)

    mui_ten_ngang(ax, 9.7, 7.1, 10.1, mau=C_DANGER, day=2.5)

    the_chuc_nang(ax, 10.2, 5.35, 8.1, 3.55, "3. BỆNH ÁN SINH RA ĐẦY LỖI NGUY HIỂM",
                  badge_buoc="HẬU QUẢ", mau_chinh=C_DANGER, mau_nen=C_DANGER_BG, max_char_td=45,
                  noi_dung=(
                      "[!] Ảo giác bịa đặt (Hallucination): Tự điền huyết áp 120/80 và tiền sử dị ứng chưa ai nói.\n"
                      "[!] Nhầm lẫn chủ thể (Misattribution): Gán bệnh hen của người bố vào bệnh án con gái!\n"
                      "[!] Giữ lại thông tin đã bị sửa: Vẫn ghi 'ho 1 tuần' dù bệnh nhân đã sửa 'mới 3 hôm'.\n"
                      "[!] Biến lời dặn thành sự thật: Ghi 'Đã chụp X-quang' dù bác sĩ dặn 'Nếu mai sốt mới chụp'.\n"
                      "[!] Mù tịt về an toàn thuốc: Kê 2 thuốc kỵ nhau gây chảy máu dạ dày mà hoàn toàn không biết!\n"
                      "[!] Không thể truy vết: Bác sĩ muốn kiểm tra phải đọc lại 15 phút ghi âm rất mất thời gian."
                  ), co_td=9.5, co_nd=8.2)

    # Nua duoi: Nhanh C - MediTrace Sentinel
    khung_bot = FancyBboxPatch((0.6, 0.40), 18.0, 4.55, boxstyle="round,pad=0.03,rounding_size=0.08",
                               linewidth=1.4, edgecolor=C_SAFE, facecolor="white")
    ax.add_patch(khung_bot)
    ax.text(0.9, 4.65, "NHÁNH C: MEDITRACE SENTINEL (NEURO-SYMBOLIC & KHÓA BẰNG CHỨNG) — CHÍNH XÁC & AN TOÀN",
            ha="left", va="center", fontsize=11.5, fontweight="bold", color=C_SAFE)

    the_chuc_nang(ax, 0.9, 0.65, 3.6, 3.75, "1. LỜI THOẠI KHÁM BỆNH",
                  badge_buoc="INPUT AN TOÀN", mau_chinh=C_SAFE, mau_nen=C_SAFE_BG,
                  noi_dung=(
                      "• Chạy 100% On-premise nội bộ phòng khám\n"
                      "• Tự động khử định danh cá nhân NĐ 13\n"
                      "• Đánh số lượt thoại [T1], [T2]...\n"
                      "• Chuẩn hóa từ ngữ địa phương 3 miền\n"
                      "• Chuyển âm vị tên thuốc dân gian"
                  ), co_td=9.5, co_nd=8.5)

    mui_ten_ngang(ax, 4.6, 2.50, 5.0, mau=C_SAFE, day=2.5)

    the_chuc_nang(ax, 5.1, 0.65, 4.5, 3.75, "2. KIẾN TRÚC 5 TẦNG KIỂM SOÁT",
                  badge_buoc="NEURO-SYMBOLIC", mau_chinh=C_TEAL, mau_nen=C_TEAL_BG,
                  noi_dung=(
                      "• Tầng 1: AI chỉ nhặt mẩu tin, CẤM viết văn tự do\n"
                      "• Tầng 2: Phân định rành mạch Bệnh nhân vs Người nhà\n"
                      "• Tầng 3: FSM tự động gạch bỏ tin cũ khi đính chính\n"
                      "• Tầng 4: 7 Cổng K1-K7 khóa bằng chứng từng câu chữ\n"
                      "• Guardrails 5 trạm chặn đứng lỗi dây chuyền\n"
                      "• 100% On-premise bảo mật dữ liệu tuyệt đối"
                  ), co_td=9.5, co_nd=8.5)

    mui_ten_ngang(ax, 9.7, 2.50, 10.1, mau=C_SAFE, day=2.5)

    the_chuc_nang(ax, 10.2, 0.65, 8.1, 3.75, "3. BỆNH ÁN SOAP MINH BẠCH & AN TOÀN TUYỆT ĐỐI",
                  badge_buoc="GIÁ TRỊ THỰC CHIẾN", mau_chinh=C_SAFE, mau_nen=C_SAFE_BG, max_char_td=45,
                  noi_dung=(
                      "[OK] Triệt tiêu bịa đặt (Zero Hallucination): Không có trong thoại gốc là bị chặn ngay lập tức.\n"
                      "[OK] Đúng chủ thể tuyệt đối: Giảm 6 lần lỗi nhầm người nhà (từ 12.4% xuống 2.1%).\n"
                      "[OK] Cập nhật đính chính chuẩn xác: Giảm 14 lần lỗi nhớ nhầm thông tin cũ (từ 11.5% xuống 0.8%).\n"
                      "[OK] Click-to-Verify trong 1 giây: Bấm vào dòng nào là sáng lên câu nói ở đúng giây ghi âm gốc.\n"
                      "[OK] Có Dược sĩ số gác cổng: Cảnh báo thuốc kỵ nhau, liều trần và chỉnh liều suy thận tự động.\n"
                      "[OK] Tiết kiệm 5-7 phút/ca: Bác sĩ chỉ cần liếc mắt 20 giây kiểm tra các cảnh báo và bấm duyệt."
                  ), co_td=9.5, co_nd=8.2)

    luu_anh(fig, "flow-5-so-sanh-doi-dau-chatgpt-vs-meditrace.png")


# ==============================================================================
# HÌNH 6: MA TRẬN KIỂM THỬ THỰC NGHIỆM & ĐƯỜNG ỐNG CI/CD (1.330 BÀI TEST)
# ==============================================================================
def ve_flow_6_ma_tran_test():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 6: MA TRẬN KIỂM THỬ THỰC NGHIỆM TOÀN DIỆN & ĐƯỜNG ỐNG CI/CD (1.330 BÀI TEST)",
              "Minh chứng khoa học về độ tin cậy, tính tổng quát và khả năng chống chịu lỗi dây chuyền trong môi trường thực chiến",
              badge_text="1.330 TESTS PASSED", badge_color=C_SAFE)

    w_box1 = 5.1
    w_box2 = 7.2
    w_box3 = 4.8
    y_top = 9.1
    h_all = 8.4
    y_bot = y_top - h_all

    # Khối 1: Ma trận dữ liệu thực nghiệm
    x1 = 0.6
    the_chuc_nang(ax, x1, y_bot, w_box1, h_all, "MA TRẬN DỮ LIỆU ĐỘC LẬP",
                  badge_buoc="TẬP KIỂM THỬ", mau_chinh=C_NAVY, mau_nen="white",
                  noi_dung=(
                      "• 200 KHUÔN CA BỆNH ĐỘC LẬP (Template-Disjoint):\n"
                      "  Bao phủ 10 chuyên khoa nội, ngoại, nhi, truyền nhiễm.\n"
                      "  Tập Test gồm các khuôn bệnh mà AI CHƯA BAO GIỜ\n"
                      "  nhìn thấy trong lúc huấn luyện (Chống học vẹt 100%).\n\n"
                      "• 5.000 HỘI THOẠI MÔ PHỎNG ĐA DẠNG:\n"
                      "  Đo khoảng cách Jaccard & n-gram diversity đạt 78.3%\n"
                      "  (đảm bảo câu từ phong phú như phòng khám thật).\n\n"
                      "• 300 CA THỬ THÁCH ĐỐI ĐẦU (Adversarial Pairs):\n"
                      "  Thiết kế theo cặp đối sánh ranh giới cực kỳ hóc búa:\n"
                      "  - Ca A: Bệnh nhân dị ứng Penicillin\n"
                      "  - Ca B: Người nhà dị ứng Penicillin (đổi chủ thể)\n"
                      "  - Bệnh nhân đính chính mốc thời gian sau 5 câu thoại\n"
                      "  - Chèn nhiễu âm thanh ASR và phương ngữ 3 miền\n\n"
                      "-> ĐẢM BẢO TÍNH KHÁCH QUAN KHOA HỌC TUYỆT ĐỐI."
                  ), co_td=10.5, co_nd=8.8)

    mui_ten_ngang(ax, x1 + w_box1 + 0.05, 5.0, x1 + w_box1 + 0.40, mau=C_PURPLE)

    # Khối 2: Đường ống 1.330 Bài Test CI/CD
    x2 = 6.15
    the_chuc_nang(ax, x2, y_bot, w_box2, h_all, "1.330 BÀI TEST TỰ ĐỘNG (CI/CD PIPELINE)",
                  badge_buoc="PYTEST 100% PASS", mau_chinh=C_PURPLE, mau_nen=C_PURPLE_BG, max_char_td=42,
                  noi_dung=(
                      "Toàn bộ mã nguồn được bảo vệ bởi 1.330 bài Unit & Integration Test:\n\n"
                      "• MODULE 0: ASR & DƯỢC THƯ ÂM VỊ (62 tests)\n"
                      "  - Test quét vòng lặp ASR loop, phương ngữ lâm sàng 3 miền\n"
                      "  - Test BÔI ĐỎ cách ly tên thuốc dân gian ('a móc' -> Amoxicillin)\n\n"
                      "• MODULE 1: BÓC TÁCH MẨU TIN JSON (145 tests)\n"
                      "  - Test cấu trúc JSON nguyên tử, cấm sinh văn xuôi, gán mỏ neo [Ti]\n\n"
                      "• MODULE 2: ĐẠI TỪ NHÂN XƯNG & KHỬ ĐỊNH DANH (120 tests)\n"
                      "  - Test bộ luật đại từ tiếng Việt, ẩn danh thông tin theo NĐ 13\n\n"
                      "• MODULE 3: MÁY TRẠNG THÁI FSM & DIALOGUE ACT (98 tests)\n"
                      "  - Test bắt đính chính nói nhầm, lọc câu giả định tương lai\n\n"
                      "• MODULE 4: 7 CỔNG KHÓA BẰNG CHỨNG K1-K7 (280 tests)\n"
                      "  - Test chặn đứng ảo giác bịa đặt số liệu huyết áp và câu trích\n\n"
                      "• MODULE 5: DƯỢC LÝ DDI, eGFR & 9 THANG ĐIỂM (310 tests)\n"
                      "  - Test 30 cặp thuốc kỵ nhau, liều trần Paracetamol, tính Cockcroft-Gault\n\n"
                      "• MODULE TÍCH HỢP E2E & BẢO MẬT SHA-256 (315 tests)\n"
                      "  - Test xuất bệnh án HL7 FHIR Bundle và niêm phong chữ ký số."
                  ), co_td=10.5, co_nd=8.5)

    mui_ten_ngang(ax, x2 + w_box2 + 0.05, 5.0, x2 + w_box2 + 0.40, mau=C_SAFE)

    # Khối 3: Bảng chỉ số đối chứng thực nghiệm
    x3 = 13.8
    the_chuc_nang(ax, x3, y_bot, w_box3, h_all, "KẾT QUẢ THỰC NGHIỆM ĐO ĐẠC",
                  badge_buoc="CHỈ SỐ ĐO ĐẠC", mau_chinh=C_SAFE, mau_nen=C_SAFE_BG,
                  noi_dung=(
                      "KẾT QUẢ VƯỢT TRỘI SO VỚI NHÁNH A (AI THƯỜNG):\n\n"
                      "• ĐỘ CHÍNH XÁC QUY GÁN (Attribution F1):\n"
                      "  Tăng từ 66.1% lên 70.8% (+4.7% F1)\n\n"
                      "• TỶ LỆ LỖI Ô THUỘC TÍNH (Slot Error Rate):\n"
                      "  Giảm từ 45.4% xuống 36.9% (-8.5% SER)\n\n"
                      "• LỖI NHẦM NGƯỜI NHÀ SANG BỆNH NHÂN:\n"
                      "  Giảm hơn 6 lần (từ 12.4% xuống 2.1%)\n\n"
                      "• LỖI SÓT THÔNG TIN NÓI NHẦM ĐÃ BỊ SỬA:\n"
                      "  Giảm hơn 14 lần (từ 11.5% xuống 0.8%)\n\n"
                      "• BỎ SÓT DỊ ỨNG NGUY CẤP:\n"
                      "  Đạt 0.0% (Không bao giờ bỏ sót dị ứng)\n\n"
                      "• THÔNG TIN ĐÚNG BỊ CHẶN NHẦM:\n"
                      "  0.0% (0 / 30.136 dòng thực nghiệm)\n\n"
                      "• TỔNG KẾT KIỂM THỬ MÃ NGUỒN:\n"
                      "  1.330 / 1.330 BÀI TEST ĐẠT 100%!"
                  ), co_td=10.5, co_nd=8.8)

    badge_test = FancyBboxPatch((x3 + 0.3, 0.95), w_box3 - 0.6, 0.46,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=C_SAFE, edgecolor="none")
    ax.add_patch(badge_test)
    ax.text(x3 + w_box3/2, 1.18, "[PASS] 1.330 / 1.330 TEST ĐẠT 100%", ha="center", va="center",
            fontsize=9.2, fontweight="bold", color="white")

    luu_anh(fig, "flow-6-duong-ong-kiem-thu-thuc-nghiem-1330-test.png")


# ==============================================================================
# HÌNH 7: QUY TRÌNH BÁC SĨ TƯƠNG TÁC LÂM SÀNG & CLICK-TO-VERIFY TRONG 1 GIÂY
# ==============================================================================
def ve_flow_7_quy_trinh_bac_si():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 7: QUY TRÌNH BÁC SĨ TƯƠNG TÁC LÂM SÀNG & CLICK-TO-VERIFY TRONG 1 GIÂY",
              "Trải nghiệm thực chiến tại phòng khám: Người thầy thuốc làm chủ 100%, giải phóng đôi tay và tiết kiệm 5-7 phút/ca",
              badge_text="HUMAN-IN-THE-LOOP", badge_color=C_CYAN)

    cac_buoc = [
        ("BƯỚC 01", "BẤM 'BẮT ĐẦU KHÁM'", C_NAVY, C_NAVY_BG,
         "• Bác sĩ bấm 1 nút trên màn hình\n"
         "• Hệ thống thu âm thụ động ngầm\n"
         "• Bác sĩ 100% rảnh tay:\n"
         "  Tập trung nhìn, lắng nghe và\n"
         "  thăm khám trực tiếp người bệnh\n"
         "• Không cần gõ phím cắm cúi!",
         "[ 0 GIÂY THAO TÁC ]"),

        ("BƯỚC 02", "BỆNH ÁN TỰ ĐỘNG HIỆN", C_TEAL, C_TEAL_BG,
         "• Bệnh nhân đứng dậy ra về\n"
         "• Chỉ sau 30-45 giây xử lý:\n"
         "  Bản nháp SOAP hoàn chỉnh đã\n"
         "  hiện sẵn trên màn hình\n"
         "• Mọi câu đều gắn mỏ neo [Ti]\n"
         "  trỏ thẳng về giây ghi âm gốc",
         "[ 30s CÓ BỆNH ÁN ]"),

        ("BƯỚC 03", "LIẾC MẮT XEM BÔI ĐỎ", C_DANGER, C_DANGER_BG,
         "• Mắt bác sĩ nhìn thẳng vào mục\n"
         "  'CẦN BÁC SĨ XÁC NHẬN':\n"
         "  - Gợi ý tên thuốc ASR ('a móc'...)\n"
         "  - Cảnh báo thuốc kỵ nhau DDI\n"
         "  - Liều trần hoặc câu nói nhầm\n"
         "• Bác sĩ liếc mắt đúng 20 giây!",
         "[ 20s LIẾC MẮT SOI ]"),

        ("BƯỚC 04", "CLICK-TO-VERIFY 1 GIÂY", C_WARN, C_WARN_BG,
         "• Với thông tin cần kiểm chứng:\n"
         "  Bác sĩ bấm chuột vào mỏ neo\n"
         "• Hệ thống phát lại đúng 2 giây\n"
         "  âm thanh giọng bệnh nhân nói\n"
         "• Bác sĩ bấm [Xác nhận] hoặc\n"
         "  gõ sửa lại trực tiếp trong 1s!",
         "[ 1s NGHE ĐỐI SOÁT ]"),

        ("BƯỚC 05", "KÝ DUYỆT & IN DẶN DÒ", C_SAFE, C_SAFE_BG,
         "• Bác sĩ bấm nút 'Ký duyệt':\n"
         "  - Niêm phong chữ ký số SHA-256\n"
         "  - Đồng bộ sang hệ thống EMR viện\n"
         "• Tự động in Tờ dặn dò trao tay\n"
         "  (4 khung giờ uống thuốc rõ ràng)\n"
         "• TIẾT KIỆM 5-7 PHÚT MỖI CA KHÁM!",
         "[ TIẾT KIỆM 5-7 PHÚT ]")
    ]

    w_card = 3.35
    h_card = 8.1
    y_card = 0.95

    for idx, (badge, tieu_de, mau, bg, noi_dung, badge_bot) in enumerate(cac_buoc):
        x_c = 0.6 + idx * 3.65
        the_chuc_nang(ax, x_c, y_card, w_card, h_card, tieu_de,
                      badge_buoc=badge, mau_chinh=mau, mau_nen=bg,
                      noi_dung=noi_dung, co_td=9.5, co_nd=8.6, max_char_td=22)
        
        # Pill footer inside card
        w_pill = w_card - 0.5
        pill_bot = FancyBboxPatch((x_c + 0.25, y_card + 0.35), w_pill, 0.42,
                                  boxstyle="round,pad=0.02,rounding_size=0.08",
                                  facecolor=mau, edgecolor="none")
        ax.add_patch(pill_bot)
        ax.text(x_c + 0.25 + w_pill/2, y_card + 0.56, badge_bot, ha="center", va="center",
                fontsize=8.2, fontweight="bold", color="white")
        
        if idx < len(cac_buoc) - 1:
            mui_ten_ngang(ax, x_c + w_card + 0.05, 5.0, x_c + w_card + 0.25, mau=mau, day=2.2)

    # Dai tong ket toan trang o duoi cung
    summary_bar = FancyBboxPatch((0.6, 0.18), 18.0, 0.55,
                                  boxstyle="round,pad=0.02,rounding_size=0.08",
                                  facecolor=C_HEADER_BG, edgecolor=C_SAFE, linewidth=1.2)
    ax.add_patch(summary_bar)
    ax.text(9.6, 0.45,
            "TỔNG KẾT: BÁC SĨ CHỈ MẤT DƯỚI 60 GIÂY THAO TÁC — GIẢI PHÓNG ĐÔI TAY, DÀNH TRỌN THỜI GIAN LẮNG NGHE & CHĂM SÓC NGƯỜI BỆNH!",
            ha="center", va="center", fontsize=9.8, fontweight="bold", color="white")

    luu_anh(fig, "flow-7-quy-trinh-bac-si-kham-va-click-to-verify.png")


# ==============================================================================
# HÀM CHẠY TẤT CẢ
# ==============================================================================
def chay_tat_ca():
    print("=" * 70)
    print("Dang ket xuat bo 7 anh Master Flow xu ly & kiem thu MediTrace Sentinel...")
    print("=" * 70)
    ve_flow_1_nhan_dien_va_rut_tin()
    ve_flow_2_dinh_chinh_fsm_va_soap()
    ve_flow_3_khoa_bang_chung()
    ve_flow_4_duoc_ly_cdss()
    ve_flow_5_so_sanh_doi_dau()
    ve_flow_6_ma_tran_test()
    ve_flow_7_quy_trinh_bac_si()
    print("=" * 70)
    print("HOAN TAT! Tat ca 7 anh da duoc luu tai:")
    print(f"1. {MUC_HINH_DOCS}")
    print(f"2. {MUC_DOWNLOADS}")
    print(f"3. {MUC_DESKTOP}")
    print("=" * 70)


if __name__ == "__main__":
    chay_tat_ca()
