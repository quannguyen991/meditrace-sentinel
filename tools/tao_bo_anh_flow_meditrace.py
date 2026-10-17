# -*- coding: utf-8 -*-
"""Script tạo bộ 7 ảnh Master Flow xử lý & kiểm thử của MediTrace Sentinel (16:9 Full HD).
Thiết kế theo tiêu chuẩn đồ họa y tế công nghệ cao (Medical-Tech Infographic):
- Bố cục thoáng đãng, phông chữ lớn, canh lề chuẩn xác, tuyệt đối không tràn viền
- Sử dụng thuật ngữ khoa học, kỹ thuật và y tế chuẩn xác, diễn đạt trực tiếp, dễ hiểu
- Tuyệt đối không dùng từ ngữ ẩn dụ, hoán dụ, giật gân hay mơ hồ
- Nhấn mạnh quy tắc: Gợi ý tên thuốc khi nhận diện âm thanh chưa chắc chắn bắt buộc BÔI ĐỎ và cần bác sĩ xác nhận

Danh sách 7 ảnh:
  Flow 1: Thu âm, phiên âm tiếng nói (ASR) & Trích xuất thông tin cấu trúc (JSON)
  Flow 2: Xử lý đính chính lời nói, lọc câu giả định & Dựng bệnh án SOAP
  Flow 3: Quy trình kiểm tra tự động 7 bước (K1-K7) — Loại bỏ thông tin sai lệch
  Flow 4: Kiểm soát an toàn đơn thuốc, hiệu chỉnh liều và tính điểm lâm sàng (CDSS)
  Flow 5: So sánh phương pháp: Mô hình ngôn ngữ tự do (ChatGPT) vs. MediTrace Sentinel
  Flow 6: Dữ liệu thực nghiệm và quy trình kiểm thử tự động (1.330 trường hợp kiểm thử)
  Flow 7: Quy trình bác sĩ sử dụng hệ thống trong ca khám bệnh (< 60 giây thao tác)

Chạy:
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

# Bảng màu y tế công nghệ cao
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


def ve_header(ax, tieu_de, phu_de, badge_text="", badge_color=C_TEAL, co_td=14.2):
    """Vẽ banner header ở đầu trang."""
    header_box = Rectangle((0, 9.6), 19.2, 1.2, facecolor=C_HEADER_BG, edgecolor="none")
    ax.add_patch(header_box)
    
    accent_bar = Rectangle((0, 9.55), 19.2, 0.05, facecolor=badge_color, edgecolor="none")
    ax.add_patch(accent_bar)
    
    ax.text(0.6, 10.35, tieu_de, ha="left", va="center", fontsize=co_td,
            fontweight="bold", color="white")
    ax.text(0.6, 9.95, phu_de, ha="left", va="center", fontsize=9.6,
            color="#94A3B8")
    
    if badge_text:
        w_b = len(badge_text) * 0.16 + 0.6
        badge_patch = FancyBboxPatch((18.6 - w_b, 9.95), w_b, 0.5,
                                     boxstyle="round,pad=0.03,rounding_size=0.1",
                                     facecolor=badge_color, edgecolor="none")
        ax.add_patch(badge_patch)
        ax.text(18.6 - w_b/2, 10.20, badge_text, ha="center", va="center",
                fontsize=8.8, fontweight="bold", color="white")


def the_chuc_nang(ax, x, y, w, h, tieu_de, badge_buoc="", noi_dung="",
                  mau_chinh=C_NAVY, mau_nen="white", mau_badge=None, co_td=9.8, co_nd=8.3,
                  dy_text=0.16, max_char_td=None):
    """Vẽ thẻ hiển thị nội dung theo từng khối chức năng."""
    khung = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.10",
                           linewidth=1.4, edgecolor=mau_chinh, facecolor=mau_nen)
    ax.add_patch(khung)
    
    top_bar = FancyBboxPatch((x + 0.04, y + h - 0.10), w - 0.08, 0.06,
                             boxstyle="round,pad=0.01,rounding_size=0.03",
                             facecolor=mau_chinh, edgecolor="none")
    ax.add_patch(top_bar)
    
    limit_chars = max_char_td or max(14, int(w * 6.0))
    td_wrapped = textwrap.fill(tieu_de, width=limit_chars)
    n_lines_td = td_wrapped.count("\n") + 1
    
    if badge_buoc:
        bg_b = mau_badge or mau_chinh
        w_b = len(badge_buoc) * 0.11 + 0.40
        badge = FancyBboxPatch((x + 0.20, y + h - 0.46), w_b, 0.26,
                               boxstyle="round,pad=0.02,rounding_size=0.07",
                               facecolor=bg_b, edgecolor="none")
        ax.add_patch(badge)
        ax.text(x + 0.20 + w_b/2, y + h - 0.33, badge_buoc, ha="center", va="center",
                fontsize=7.5, fontweight="bold", color="white")
        
        y_td = y + h - 0.60
        ax.text(x + 0.20, y_td, td_wrapped, ha="left", va="top",
                fontsize=co_td, fontweight="bold", color=mau_chinh, linespacing=1.15)
        
        y_div = y_td - (n_lines_td * 0.28) - 0.10
    else:
        y_td = y + h - 0.32
        ax.text(x + 0.20, y_td, td_wrapped, ha="left", va="top",
                fontsize=co_td, fontweight="bold", color=mau_chinh, linespacing=1.15)
        y_div = y_td - (n_lines_td * 0.28) - 0.10
    
    ax.plot([x + 0.20, x + w - 0.20], [y_div, y_div],
            color=C_BORDER_LIGHT, linewidth=0.8, linestyle="-")
    
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
# HÌNH 1: THU ÂM, PHIÊN ÂM TIẾNG NÓI & TRÍCH XUẤT THÔNG TIN CẤU TRÚC (JSON)
# ==============================================================================
def ve_flow_1_nhan_dien_va_rut_tin():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 1: THU ÂM, PHIÊN ÂM TIẾNG NÓI (ASR) & TRÍCH XUẤT THÔNG TIN CẤU TRÚC (JSON)",
              "Từ âm thanh hội thoại khám bệnh đến dữ liệu có cấu trúc — Tự động bôi đỏ cảnh báo tên thuốc cần bác sĩ xác nhận",
              badge_text="BƯỚC 0 & TẦNG 1", badge_color=C_TEAL)

    w_col = 4.15
    y_top = 9.1
    h_col = 8.4
    y_bot = y_top - h_col

    # Cột 1: Thu âm & PhoWhisper
    x1 = 0.6
    the_chuc_nang(ax, x1, y_bot, w_col, h_col, "THU ÂM & PHIÊN ÂM TIẾNG NÓI",
                  badge_buoc="BƯỚC 01", mau_chinh=C_NAVY, mau_nen="white",
                  noi_dung=(
                      "• THU ÂM TẠI PHÒNG KHÁM:\n"
                      "  - Thời lượng trung bình: 3 - 5 phút/ca khám\n"
                      "  - Xử lý 100% nội bộ trên máy trạm (On-premise)\n"
                      "  - Tuân thủ bảo mật dữ liệu y tế (Nghị định 13/CP)\n\n"
                      "• PHIÊN ÂM TIẾNG NÓI (PhoWhisper):\n"
                      "  - Mô hình tinh chỉnh cho ngữ cảnh y tế tiếng Việt\n"
                      "  - Nhận diện giọng nói đa dạng các vùng miền\n"
                      "  - Tạo văn bản hội thoại kèm mốc thời gian chính xác\n\n"
                      "• PHÂN BIỆT NGƯỜI NÓI (PyAnnote):\n"
                      "  - Tự động tách giọng người nói 1, 2, 3\n"
                      "  - Phân loại rõ: Bác sĩ, Bệnh nhân, Người nhà\n\n"
                      "• ĐÁNH SỐ THỨ TỰ LƯỢT THOẠI [T1], [T2]...:\n"
                      "  - Lưu vết số thứ tự câu thoại làm căn cứ\n"
                      "    đối chiếu sau này."
                  ), co_td=10.0, co_nd=8.5)

    mui_ten_ngang(ax, x1 + w_col + 0.05, 5.0, x1 + w_col + 0.35, mau=C_NAVY)

    # Cột 2: Nhận diện tên thuốc & Cảnh báo đỏ
    x2 = 5.25
    the_chuc_nang(ax, x2, y_bot, w_col, h_col, "NHẬN DIỆN TÊN THUỐC & CẢNH BÁO ĐỎ",
                  badge_buoc="BƯỚC 02", mau_chinh=C_DANGER, mau_nen=C_DANGER_BG,
                  noi_dung=(
                      "• THỰC TẾ GIAO TIẾP TẠI PHÒNG KHÁM:\n"
                      "  Phòng khám có tiếng ồn; người bệnh có thể phát âm\n"
                      "  chưa chuẩn hoặc dùng tên gọi dân gian\n"
                      "  (ví dụ: 'a móc', 'ô mê', viên nhộng đỏ vàng...).\n"
                      "  Hệ thống ASR không thể cam đoan đúng 100%!\n\n"
                      "• QUY TẮC KHÔNG TỰ Ý SỬA TÊN THUỐC:\n"
                      "  Tuyệt đối KHÔNG tự ý suy đoán rồi điền ngầm vào đơn\n"
                      "  (đoán sai hoạt chất có thể dẫn đến rủi ro nguy hiểm).\n\n"
                      "• CƠ CHẾ BÔI ĐỎ & YÊU CẦU BÁC SĨ XÁC NHẬN:\n"
                      "  - Dò từ điển tên thuốc và từ phát âm tương đồng\n"
                      "  - BÔI ĐỎ cảnh báo: [CẦN BÁC SĨ XÁC NHẬN]\n"
                      "  - Hiển thị gợi ý trên màn hình để bác sĩ duyệt\n\n"
                      "• XỬ LÝ LỖI LẶP TỪ & PHƯƠNG NGỮ:\n"
                      "  - Ngăn chặn lỗi lặp từ vô nghĩa của mô hình âm thanh\n"
                      "  - Chuẩn hóa hơn 60 từ ngữ địa phương thông dụng."
                  ), co_td=9.8, co_nd=8.4)

    mui_ten_ngang(ax, x2 + w_col + 0.05, 5.0, x2 + w_col + 0.35, mau=C_TEAL)

    # Cột 3: Tầng 1 - Trích xuất JSON
    x3 = 9.9
    the_chuc_nang(ax, x3, y_bot, w_col, h_col, "TRÍCH XUẤT THÔNG TIN Y TẾ (JSON)",
                  badge_buoc="TẦNG 01", mau_chinh=C_TEAL, mau_nen="white",
                  noi_dung=(
                      "• MÔ HÌNH XỬ LÝ: Qwen3-4B QLoRA (Local GPU):\n"
                      "  - Vận hành trên máy tính phòng khám (RTX 3050/3060)\n"
                      "  - Tốc độ xử lý: 30 - 45 giây cho mỗi ca khám\n\n"
                      "• QUY ĐỊNH TRÍCH XUẤT CÓ CẤU TRÚC:\n"
                      "  Không để AI tự do viết đoạn văn (tránh sai lệch).\n"
                      "  Chỉ trích xuất các trường thông tin có cấu trúc JSON:\n\n"
                      "  {\n"
                      "    'thuc_the': 'amoxicillin',\n"
                      "    'chu_the_id': 0,  // Bệnh nhân\n"
                      "    'noi_dung': 'dị ứng mẩn ngứa',\n"
                      "    'do_chac_chan': 'chắc chắn',\n"
                      "    'phu_dinh': false,\n"
                      "    'bang_chung': [5],  // Câu thoại số [T5]\n"
                      "    'trich_dan': 'uống amoxicillin nổi mề đay'\n"
                      "  }\n\n"
                      "• YÊU CẦU NGUỒN DẪN CHỨNG:\n"
                      "  Mỗi thông tin trích xuất đều phải\n"
                      "  gắn với câu thoại gốc."
                  ), co_td=9.8, co_nd=8.4)

    mui_ten_ngang(ax, x3 + w_col + 0.05, 5.0, x3 + w_col + 0.35, mau=C_PURPLE)

    # Cột 4: Phân biệt người nói
    x4 = 14.55
    the_chuc_nang(ax, x4, y_bot, w_col, h_col, "PHÂN BIỆT BỆNH NHÂN & NGƯỜI NHÀ",
                  badge_buoc="BƯỚC 03", mau_chinh=C_PURPLE, mau_nen=C_PURPLE_BG,
                  noi_dung=(
                      "• MỤC TIÊU AN TOÀN:\n"
                      "  Tránh ghi nhầm triệu chứng của người nhà\n"
                      "  vào hồ sơ của bệnh nhân chính!\n"
                      "  (Ví dụ: Người nhà nói 'Bố cháu bị hen'\n"
                      "   thì không được kết luận là bệnh nhân bị hen).\n\n"
                      "• NHẬN BIẾT ĐẠI TỪ NHÂN XƯNG TIẾNG VIỆT:\n"
                      "  - Nhận biết các từ: 'mẹ tôi', 'bố tôi', 'con tôi',\n"
                      "    'ông nhà tôi', 'bé nhà em'...\n"
                      "  - Tự động phân loại chính xác:\n"
                      "    Không đưa vào bệnh sử của bệnh nhân,\n"
                      "    chuyển sang mục TIỀN SỬ GIA ĐÌNH.\n\n"
                      "• KẾT QUẢ ĐO ĐẠC THỰC TẾ:\n"
                      "  - Giảm tỷ lệ nhầm chủ thể từ 12.4% xuống còn 2.1%\n"
                      "  - Đảm bảo hồ sơ phản ánh đúng người bệnh\n\n"
                      "• CHUYỂN GIAO DỮ LIỆU:\n"
                      "  Dữ liệu hợp lệ được chuyển sang bước đính chính."
                  ), co_td=9.8, co_nd=8.4)

    luu_anh(fig, "flow-1-nhan-dien-giong-noi-va-rut-tin.png")


# ==============================================================================
# HÌNH 2: XỬ LÝ ĐÍNH CHÍNH LỜI NÓI, LỌC CÂU GIẢ ĐỊNH & DỰNG BỆNH ÁN SOAP
# ==============================================================================
def ve_flow_2_dinh_chinh_fsm_va_soap():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 2: XỬ LÝ ĐÍNH CHÍNH LỜI NÓI, LỌC CÂU GIẢ ĐỊNH & DỰNG BỆNH ÁN SOAP",
              "Xử lý tình huống nói nhầm, lọc bỏ câu dặn dò tương lai và tự động lập hồ sơ bệnh án chuẩn y khoa",
              badge_text="TẦNG 2, 3 & 5", badge_color=C_CYAN)

    w_col = 4.15
    y_top = 9.1
    h_col = 8.4
    y_bot = y_top - h_col

    # Cột 1: Phân nhóm chủ thể & Ẩn danh hóa
    x1 = 0.6
    the_chuc_nang(ax, x1, y_bot, w_col, h_col, "PHÂN NHÓM CHỦ THỂ & ẨN DANH HÓA",
                  badge_buoc="TẦNG 02", mau_chinh=C_NAVY, mau_nen="white",
                  noi_dung=(
                      "• PHÂN ĐỊNH 4 NHÓM NGƯỜI NÓI:\n"
                      "  1. Bác sĩ hỏi bệnh và thăm khám\n"
                      "  2. Bệnh nhân tự trình bày triệu chứng\n"
                      "  3. Người nhà mô tả hộ bệnh nhân ('cháu bị sốt')\n"
                      "  4. Người nhà kể về người khác ('ông nhà tôi...')\n"
                      "     -> Tự động phân vào Tiền sử gia đình\n\n"
                      "• BẢO MẬT DỮ LIỆU CÁ NHÂN (Nghị định 13/CP):\n"
                      "  - Tự động che họ tên, SĐT, số CCCD, địa chỉ\n"
                      "  - Thay thế bằng mã ẩn danh [BENH_NHAN_001]\n"
                      "  - Dữ liệu hoàn toàn ẩn danh trước khi lưu trữ\n\n"
                      "• XỬ LÝ CÂU NÓI THIẾU CHỦ NGỮ:\n"
                      "  - Khi bệnh nhân nói ngắn: 'Sốt 3 hôm rồi'\n"
                      "  -> Tự động nhận diện ngữ cảnh để gán\n"
                      "     chính xác cho bệnh nhân."
                  ), co_td=9.8, co_nd=8.4)

    mui_ten_ngang(ax, x1 + w_col + 0.05, 5.0, x1 + w_col + 0.35, mau=C_WARN)

    # Cột 2: Xử lý đính chính khi người nói sửa lời
    x2 = 5.25
    the_chuc_nang(ax, x2, y_bot, w_col, h_col, "XỬ LÝ ĐÍNH CHÍNH LỜI NÓI",
                  badge_buoc="TẦNG 03", mau_chinh=C_WARN, mau_nen=C_WARN_BG,
                  noi_dung=(
                      "• TÌNH HUỐNG THỰC TẾ PHÒNG KHÁM:\n"
                      "  Bệnh nhân nói nhầm rồi tự sửa lại ngay sau đó:\n"
                      "  'Tôi bị sốt 1 tuần... à không, mới 3 hôm thôi!'\n\n"
                      "• QUY TẮC XỬ LÝ PHÂN NHÁNH RÕ RÀNG:\n"
                      "  - NHÁNH BỔ SUNG: Cả hai ý cùng đúng\n"
                      "    ('vừa ho vừa rát họng') -> Lưu giữ cả hai\n"
                      "  - NHÁNH ĐÍNH CHÍNH (Thay thế thông tin):\n"
                      "    Thông tin cũ ('1 tuần') bị đánh dấu [Bị thay thế],\n"
                      "    chỉ đưa thông tin mới ('3 hôm') vào bệnh án.\n"
                      "  - NHÁNH MÂU THUẪN: Chưa rõ ý nào đúng\n"
                      "    -> Đưa sang mục [Cần bác sĩ xác nhận]\n\n"
                      "• HIỆU QUẢ THỰC NGHIỆM:\n"
                      "  Giảm 14 lần sai sót do giữ nhầm thông tin cũ\n"
                      "  (từ 11.5% xuống còn 0.8%)."
                  ), co_td=9.8, co_nd=8.4)

    mui_ten_ngang(ax, x2 + w_col + 0.05, 5.0, x2 + w_col + 0.35, mau=C_SAFE)

    # Cột 3: Lọc câu giả định
    x3 = 9.9
    the_chuc_nang(ax, x3, y_bot, w_col, h_col, "LỌC CÂU DẶN DÒ & GIẢ ĐỊNH",
                  badge_buoc="BƯỚC 04", mau_chinh=C_SAFE, mau_nen="white",
                  noi_dung=(
                      "• VẤN ĐỀ THƯỜNG GẶP CỦA CÁC MÔ HÌNH AI:\n"
                      "  Khi bác sĩ dặn: 'Nếu ngày mai sốt thì chụp X-quang',\n"
                      "  các mô hình AI thông thường hay ghi nhầm là:\n"
                      "  'Bệnh nhân đã chụp X-quang phổi'!\n\n"
                      "• BỘ LỌC CÂU ĐIỀU KIỆN / TƯƠNG LAI:\n"
                      "  - Nhận diện các liên từ: 'nếu... thì', 'phòng khi',\n"
                      "    'khi nào đau mới uống', 'hẹn tuần sau tái khám'...\n"
                      "  - KHÔNG GHI vào phần Khám hay Chẩn đoán!\n"
                      "  - Tự động chuyển vào mục KẾ HOẠCH THEO DÕI.\n\n"
                      "• PHÂN BIỆT RÕ KẾT QUẢ GHI NHẬN:\n"
                      "  - Phân biệt 'Chưa ghi nhận' và 'Không có triệu chứng'\n"
                      "    để đảm bảo tính chính xác về mặt y khoa."
                  ), co_td=9.8, co_nd=8.4)

    mui_ten_ngang(ax, x3 + w_col + 0.05, 5.0, x3 + w_col + 0.35, mau=C_CYAN)

    # Cột 4: Dựng bệnh án SOAP
    x4 = 14.55
    the_chuc_nang(ax, x4, y_bot, w_col, h_col, "THIẾT LẬP BỆNH ÁN SOAP",
                  badge_buoc="TẦNG 05", mau_chinh=C_CYAN, mau_nen=C_CYAN_BG,
                  noi_dung=(
                      "• XÂY DỰNG THEO MẪU BỆNH ÁN CHUẨN (SOAP):\n"
                      "  - S (Subjective): Lý do khám, Bệnh sử, Tiền sử\n"
                      "  - O (Objective): Triệu chứng thực thể, Sinh hiệu\n"
                      "  - A (Assessment): Chẩn đoán xác định / Phân biệt\n"
                      "  - P (Plan): Kế hoạch điều trị, Đơn thuốc, Lời dặn\n\n"
                      "• MỤC RIÊNG 'CẦN BÁC SĨ XÁC NHẬN':\n"
                      "  - Tập trung toàn bộ các cảnh báo BÔI ĐỎ\n"
                      "    (tên thuốc nghi ngờ, tương tác thuốc...)\n"
                      "  - Bác sĩ rà soát nhanh trong khoảng 20 giây\n\n"
                      "• BẤM XEM VÀ ĐỐI CHIẾU NGUỒN GỐC THÔNG TIN:\n"
                      "  Bấm vào từng câu trên bệnh án để xem ngay\n"
                      "  câu thoại tương ứng trong cuộc khám."
                  ), co_td=9.8, co_nd=8.4)

    luu_anh(fig, "flow-2-dinh-chinh-fsm-va-benh-an-soap.png")


# ==============================================================================
# HÌNH 3: QUY TRÌNH KIỂM TRA TỰ ĐỘNG 7 BƯỚC (K1–K7) — LOẠI BỎ THÔNG TIN SAI LỆCH
# ==============================================================================
def ve_flow_3_khoa_bang_chung():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 3: QUY TRÌNH KIỂM TRA TỰ ĐỘNG 7 BƯỚC (K1–K7) — LOẠI BỎ THÔNG TIN SAI LỆCH",
              "Áp dụng thuật toán kiểm tra logic độc lập để thẩm định từng nội dung trích xuất trước khi đưa vào hồ sơ bệnh án",
              badge_text="KIỂM ĐỊNH LOGIC 7 BƯỚC", badge_color=C_DANGER)

    # Khối Đầu vào Trái
    the_chuc_nang(ax, 0.6, 1.5, 3.4, 7.6, "THÔNG TIN ĐẦU VÀO TỪ MÔ HÌNH AI",
                  badge_buoc="DỮ LIỆU JSON", mau_chinh=C_TEAL, mau_nen=C_TEAL_BG,
                  noi_dung=(
                      "Dữ liệu có cấu trúc:\n\n"
                      "• Tên thực thể: 'amoxicillin'\n"
                      "• Đối tượng: 'bệnh nhân'\n"
                      "• Nội dung: 'dị ứng mẩn ngứa'\n"
                      "• Độ chắc chắn: 'chắc chắn'\n"
                      "• Phủ định: Sai (không phủ định)\n"
                      "• Lượt thoại nguồn: [T5]\n"
                      "• Đoạn trích dẫn:\n"
                      "  'uống amoxicillin nổi mề đay'\n\n"
                      "-> BẮT BUỘC ĐI QUA\n"
                      "   QUY TRÌNH KIỂM TRA 7 BƯỚC\n"
                      "   TRƯỚC KHI VÀO BỆNH ÁN"
                  ), co_td=9.8, co_nd=8.6)

    mui_ten_ngang(ax, 4.05, 5.3, 4.30, mau=C_NAVY, day=2.5)

    # 7 Bước kiểm tra ở giữa (thu hẹp w_mid = 8.85 để tạo khoảng trống thoáng cho mũi tên và chữ)
    x_mid = 4.25
    w_mid = 8.85
    y_start = 8.15
    h_gate = 0.94
    spacing = 1.10

    cac_cong = [
        ("BƯỚC K1", "KIỂM TRA SỰ TỒN TẠI TRONG LỜI THOẠI (VERBATIM STRING MATCH)",
         "Dò chuỗi trích dẫn trong câu thoại nguồn [Ti]. Nếu là tên thuốc nhận diện chưa chắc chắn -> BÔI ĐỎ CHỜ XÁC NHẬN!", C_DANGER, C_DANGER_BG),
        ("BƯỚC K2", "KIỂM TRA TÍNH PHÙ HỢP CỦA THUẬT NGỮ Y KHOA (CORE TERMS)",
         "So khớp từ ngữ y tế chính giữa đoạn trích dẫn và nội dung tóm tắt, tránh tóm tắt sai lệch nghĩa gốc.", C_NAVY, C_NAVY_BG),
        ("BƯỚC K3", "XÁC MINH NGƯỜI NÓI VÀ ĐỐI TƯỢNG ĐƯỢC NÓI TỚI (SPEAKER ATTRIBUTION)",
         "Kiểm tra đại từ chỉ người. Triệu chứng của người nhà (bố, mẹ, con...) không được ghi vào bệnh sử của bệnh nhân.", C_NAVY, C_NAVY_BG),
        ("BƯỚC K4", "LỌC NỘI DUNG GIẢ ĐỊNH HOẶC DẶN DÒ TƯƠNG LAI (HYPOTHETICAL FILTER)",
         "Xác định câu dặn dò hoặc tình huống dự kiến ('Nếu sốt thì...') để không ghi nhầm thành việc đã thực hiện.", C_WARN, C_WARN_BG),
        ("BƯỚC K5", "ĐỐI CHIẾU MỐC THỜI GIAN (TEMPORAL ALIGNMENT)",
         "Mốc thời gian (ví dụ: '3 ngày', '1 tuần') phải xuất hiện chính xác trong lượt thoại được dẫn chứng.", C_NAVY, C_NAVY_BG),
        ("BƯỚC K6", "KIỂM TRA CHỮ SỐ LÂM SÀNG VÀ LIỀU LƯỢNG (NUMERICAL GROUNDING)",
         "Đối chiếu từng con số huyết áp, nhiệt độ, liều thuốc mg. Chặn ngay trường hợp mô hình AI tự điền con số mặc định.", C_DANGER, C_DANGER_BG),
        ("BƯỚC K7", "CẬP NHẬT THÔNG TIN ĐÍNH CHÍNH (TEMPORAL SUPERSEDED CHECK)",
         "Phát hiện câu nói sau sửa lại câu nói trước để loại bỏ thông tin cũ đã bị thay thế.", C_WARN, C_WARN_BG)
    ]

    for idx, (badge_k, tieu_de, noi_dung, mau, bg) in enumerate(cac_cong):
        y_g = y_start - idx * spacing
        khung_g = FancyBboxPatch((x_mid, y_g), w_mid, h_gate, boxstyle="round,pad=0.02,rounding_size=0.08",
                                 linewidth=1.3, edgecolor=mau, facecolor=bg)
        ax.add_patch(khung_g)
        
        badge_p = FancyBboxPatch((x_mid + 0.18, y_g + h_gate - 0.38), 1.10, 0.26,
                                 boxstyle="round,pad=0.02,rounding_size=0.06",
                                 facecolor=mau, edgecolor="none")
        ax.add_patch(badge_p)
        ax.text(x_mid + 0.18 + 0.55, y_g + h_gate - 0.25, badge_k, ha="center", va="center",
                fontsize=7.8, fontweight="bold", color="white")
        
        ax.text(x_mid + 1.40, y_g + h_gate - 0.25, tieu_de, ha="left", va="center",
                fontsize=8.8, fontweight="bold", color=mau)
        
        ax.text(x_mid + 0.20, y_g + 0.24, noi_dung, ha="left", va="center",
                fontsize=7.9, color=C_TEXT_MAIN)

    # 2 Đầu ra bên phải
    x_out = 14.75
    w_out = 3.85

    # Nhánh Đạt Chuẩn
    x_arr_start = x_mid + w_mid + 0.05
    mui_ten_ngang(ax, x_arr_start, 6.8, x_out - 0.1, mau=C_SAFE, day=2.5)
    ax.text((x_arr_start + x_out) / 2, 7.15, "VƯỢT QUA\n7 BƯỚC", ha="center", va="bottom",
            fontsize=7.5, fontweight="bold", color=C_SAFE, linespacing=1.1)
    
    the_chuc_nang(ax, x_out, 5.3, w_out, 3.8, "HỒ SƠ BỆNH ÁN (SOAP)",
                  badge_buoc="ĐẠT CHUẨN", mau_chinh=C_SAFE, mau_nen=C_SAFE_BG,
                  noi_dung=(
                      "ĐỘ CHÍNH XÁC VÀ ĐẦY ĐỦ CĂN CỨ:\n\n"
                      "• Điền trực tiếp vào các mục SOAP\n"
                      "• Lưu kèm mã số câu thoại [Ti] để tra cứu\n"
                      "• Bác sĩ dễ dàng kiểm tra đối chiếu nhanh\n"
                      "• Kết quả thực nghiệm đo đạc:\n"
                      "  0.0% bị chặn nhầm (0 / 30.136 dòng dữ liệu)!"
                  ), co_td=9.8, co_nd=8.4)
    badge_ok = FancyBboxPatch((x_out + 0.25, 5.50), w_out - 0.5, 0.40,
                              boxstyle="round,pad=0.02,rounding_size=0.08",
                              facecolor=C_SAFE, edgecolor="none")
    ax.add_patch(badge_ok)
    ax.text(x_out + w_out/2, 5.70, "[OK] HỢP LỆ -> ĐIỀN VÀO BỆNH ÁN SOAP", ha="center", va="center",
            fontsize=7.8, fontweight="bold", color="white")

    # Nhánh Bị Chặn / Cần xác nhận
    mui_ten_ngang(ax, x_arr_start, 3.0, x_out - 0.1, mau=C_DANGER, day=2.5)
    ax.text((x_arr_start + x_out) / 2, 3.35, "CÓ ĐIỂM\nNGHI NGỜ", ha="center", va="bottom",
            fontsize=7.5, fontweight="bold", color=C_DANGER, linespacing=1.1)

    the_chuc_nang(ax, x_out, 1.5, w_out, 3.6, "CẦN BÁC SĨ XÁC NHẬN",
                  badge_buoc="BÔI ĐỎ CẢNH BÁO", mau_chinh=C_DANGER, mau_nen=C_DANGER_BG,
                  noi_dung=(
                      "KHÔNG TỰ Ý XÓA DỮ LIỆU NGHI NGỜ:\n\n"
                      "• Mọi thông tin chưa qua kiểm tra tập hợp tại đây\n"
                      "• BÔI ĐỎ cảnh báo kèm lý do cụ thể:\n"
                      "  'trích dẫn chưa khớp', 'câu giả định',\n"
                      "  'tên thuốc nhận diện chưa rõ'...\n"
                      "• Bác sĩ kiểm tra nhanh và bấm duyệt hoặc sửa lại\n"
                      "• Đảm bảo không bỏ sót thông tin quan trọng."
                  ), co_td=9.8, co_nd=8.3)
    badge_dang = FancyBboxPatch((x_out + 0.25, 1.68), w_out - 0.5, 0.40,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=C_DANGER, edgecolor="none")
    ax.add_patch(badge_dang)
    ax.text(x_out + w_out/2, 1.88, "[!] BÔI ĐỎ -> CHỜ BÁC SĨ DUYỆT", ha="center", va="center",
            fontsize=7.8, fontweight="bold", color="white")

    luu_anh(fig, "flow-3-khoa-bang-chung-k1-k7-chong-ao-giac.png")


# ==============================================================================
# HÌNH 4: KIỂM SOÁT AN TOÀN ĐƠN THUỐC, HIỆU CHỈNH LIỀU VÀ TÍNH ĐIỂM LÂM SÀNG (CDSS)
# ==============================================================================
def ve_flow_4_duoc_ly_cdss():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 4: KIỂM SOÁT AN TOÀN ĐƠN THUỐC, HIỆU CHỈNH LIỀU VÀ TÍNH ĐIỂM LÂM SÀNG (CDSS)",
              "Tự động kiểm tra tương tác thuốc, giới hạn liều tối đa, tính độ lọc cầu thận và hỗ trợ tính 9 thang điểm lâm sàng",
              badge_text="HỖ TRỢ QUYẾT ĐỊNH (CDSS)", badge_color=C_SAFE)

    w_col = 4.15
    y_top = 9.1
    h_col = 8.4
    y_bot = y_top - h_col

    # Cột 1: Tiếp nhận đơn
    x1 = 0.6
    the_chuc_nang(ax, x1, y_bot, w_col, h_col, "TIẾP NHẬN ĐƠN & DỮ LIỆU ĐẦU VÀO",
                  badge_buoc="BƯỚC 01", mau_chinh=C_NAVY, mau_nen="white",
                  noi_dung=(
                      "• NGUỒN DỮ LIỆU ĐẦU VÀO:\n"
                      "  - Bác sĩ kê đơn qua lời nói\n"
                      "  - Bệnh nhân thông báo thuốc đang dùng\n"
                      "  - Kết quả xét nghiệm (Creatinine máu, Tuổi)\n\n"
                      "• QUY TẮC AN TOÀN KHI NHẬN DIỆN THUỐC:\n"
                      "  - Khi người bệnh gọi tên dân gian ('a móc', 'ô mê')\n"
                      "  - Hệ thống gợi ý Amoxicillin, Omeprazole...\n"
                      "  - BẮT BUỘC BÔI ĐỎ CẢNH BÁO\n"
                      "    [CẦN BÁC SĨ DUYỆT]\n"
                      "  - Không tự ý thêm ngầm vào đơn thuốc.\n\n"
                      "• ĐỐI SOÁT NHANH VỚI GHI ÂM GỐC:\n"
                      "  Bác sĩ bấm nghe lại đoạn âm thanh bệnh nhân nói\n"
                      "  để xác nhận trước khi hệ thống tính toán liều."
                  ), co_td=9.8, co_nd=8.4)

    mui_ten_ngang(ax, x1 + w_col + 0.05, 5.0, x1 + w_col + 0.35, mau=C_DANGER)

    # Cột 2: 3 Bước kiểm tra dược lý
    x2 = 5.25
    the_chuc_nang(ax, x2, y_bot, w_col, h_col, "3 BƯỚC KIỂM TRA AN TOÀN ĐƠN THUỐC",
                  badge_buoc="BƯỚC 02", mau_chinh=C_DANGER, mau_nen=C_DANGER_BG,
                  noi_dung=(
                      "1. KIỂM TRA TƯƠNG TÁC THUỐC BẤT LỢI (DDI):\n"
                      "   Tra cứu Dược thư Quốc gia & hướng dẫn y khoa:\n"
                      "   • Warfarin + Aspirin/NSAID:\n"
                      "     Tăng nguy cơ xuất huyết -> Cảnh báo\n"
                      "   • Clopidogrel + Omeprazole: Giảm hiệu quả\n"
                      "   • Digoxin + Amiodarone: Tăng nguy cơ ngộ độc\n\n"
                      "2. KIỂM SOÁT LIỀU TỐI ĐA TRONG NGÀY:\n"
                      "   • Paracetamol <= 4000 mg/ngày (tối đa 8 viên 500mg)\n"
                      "   • Ibuprofen <= 2400 mg/ngày\n"
                      "   • Aspirin <= 3000 mg/ngày\n"
                      "   -> Tự động cộng dồn các nguồn\n"
                      "      và cảnh báo nếu vượt ngưỡng an toàn.\n\n"
                      "3. HIỆU CHỈNH LIỀU THEO CHỨC NĂNG THẬN (eGFR):\n"
                      "   • Tính mức lọc cầu thận Cockcroft-Gault từ Creatinine\n"
                      "   • eGFR < 30 mL/phút: Khuyến cáo giảm 50% liều\n"
                      "     kháng sinh và cảnh báo thận trọng."
                  ), co_td=9.6, co_nd=8.2)

    mui_ten_ngang(ax, x2 + w_col + 0.05, 5.0, x2 + w_col + 0.35, mau=C_PURPLE)

    # Cột 3: 9 Thang điểm lâm sàng
    x3 = 9.9
    the_chuc_nang(ax, x3, y_bot, w_col, h_col, "TỰ ĐỘNG TÍNH 9 THANG ĐIỂM",
                  badge_buoc="BƯỚC 03", mau_chinh=C_PURPLE, mau_nen="white",
                  noi_dung=(
                      "Tự động tổng hợp triệu chứng và tính toán điểm số:\n\n"
                      "1. GCS (Glasgow): Đánh giá tri giác và độ hôn mê\n"
                      "2. qSOFA: Đánh giá nguy cơ nhiễm khuẩn nặng\n"
                      "3. CURB-65: Đánh giá độ nặng của viêm phổi\n"
                      "4. CHA2DS2-VASc: Nguy cơ đột quỵ ở rung nhĩ\n"
                      "5. HAS-BLED: Đánh giá nguy cơ chảy máu\n"
                      "6. Wells Score: Đánh giá thuyên tắc mạch\n"
                      "7. Glasgow-Blatchford: Tiên lượng xuất huyết tiêu hóa\n"
                      "8. NYHA I - IV: Phân loại suy tim theo gắng sức\n"
                      "9. BMI Châu Á: Phân loại thể trạng dinh dưỡng\n\n"
                      "-> Cung cấp số liệu hỗ trợ bác sĩ tham khảo nhanh."
                  ), co_td=9.8, co_nd=8.3)

    mui_ten_ngang(ax, x3 + w_col + 0.05, 5.0, x3 + w_col + 0.35, mau=C_SAFE)

    # Cột 4: Đầu ra
    x4 = 14.55
    the_chuc_nang(ax, x4, y_bot, w_col, h_col, "KẾT QUẢ HIỂN THỊ & HƯỚNG DẪN",
                  badge_buoc="KẾT QUẢ", mau_chinh=C_SAFE, mau_nen=C_SAFE_BG,
                  noi_dung=(
                      "• BẢNG CẢNH BÁO TRÊN MÀN HÌNH BÁC SĨ:\n"
                      "  - Hiển thị rõ các cặp thuốc tương tác cần lưu ý\n"
                      "  - Đề xuất hoạt chất thay thế an toàn hơn nếu có\n"
                      "  - Khuyến cáo điều chỉnh liều theo chức năng thận\n"
                      "  - Bác sĩ luôn xem xét và ra quyết định cuối cùng.\n\n"
                      "• PHIẾU HƯỚNG DẪN ĐIỀU TRỊ CHO BỆNH NHÂN:\n"
                      "  - Phân chia lịch uống theo 4 khung giờ rõ ràng:\n"
                      "    Sáng - Trưa - Chiều - Tối (kèm lưu ý trước/sau ăn)\n"
                      "  - Hướng dẫn chế độ ăn uống và sinh hoạt phù hợp\n"
                      "  - Liệt kê dấu hiệu cảnh báo cần quay lại viện ngay:\n"
                      "    (Khó thở, đau tức ngực, sốt cao liên tục...)\n"
                      "  - Giúp người bệnh dễ hiểu và an tâm điều trị."
                  ), co_td=9.8, co_nd=8.3)

    luu_anh(fig, "flow-4-duoc-ly-lam-sang-va-cdss-thang-diem.png")


# ==============================================================================
# HÌNH 5: SO SÁNH PHƯƠNG PHÁP: MÔ HÌNH TỰ DO vs. MEDITRACE SENTINEL
# ==============================================================================
def ve_flow_5_so_sanh_doi_dau():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 5: SO SÁNH PHƯƠNG PHÁP: MÔ HÌNH NGÔN NGỮ TỰ DO (CHATGPT) vs. MEDITRACE SENTINEL",
              "Phân tích sự khác biệt giữa mô hình AI tạo sinh tự do và hệ thống AI kết hợp kiểm định logic xác định trong y tế",
              badge_text="SO SÁNH PHƯƠNG PHÁP", badge_color=C_WARN, co_td=13.8)

    # Nửa trên: Nhánh A - Mô hình đám mây tự do
    khung_top = FancyBboxPatch((0.6, 5.15), 18.0, 4.25, boxstyle="round,pad=0.03,rounding_size=0.08",
                               linewidth=1.4, edgecolor=C_DANGER, facecolor="white")
    ax.add_patch(khung_top)
    ax.text(0.9, 9.15, "PHƯƠNG PHÁP A: DÙNG MÔ HÌNH AI ĐÁM MÂY TỰ DO (END-TO-END) — NHIỀU RỦI RO SAI LỆCH",
            ha="left", va="center", fontsize=11.2, fontweight="bold", color=C_DANGER)

    the_chuc_nang(ax, 0.9, 5.35, 3.6, 3.55, "1. HỘI THOẠI KHÁM BỆNH",
                  badge_buoc="ĐẦU VÀO", mau_chinh=C_TEXT_MUTED, mau_nen=C_BG,
                  noi_dung=(
                      "• Bác sĩ, bệnh nhân, người nhà nói nhanh\n"
                      "• Người bệnh tự sửa lời: '1 tuần... à 3 hôm'\n"
                      "• Người nhà kể bệnh của người khác:\n"
                      "  'Bố em bị hen phế quản'\n"
                      "• Bác sĩ dặn: 'Nếu sốt thì chụp X-quang'"
                  ), co_td=9.5, co_nd=8.3)

    mui_ten_ngang(ax, 4.6, 7.1, 5.0, mau=C_DANGER, day=2.5)

    the_chuc_nang(ax, 5.1, 5.35, 4.5, 3.55, "2. GỬI YÊU CẦU LÊN MÔ HÌNH ĐÁM MÂY",
                  badge_buoc="XỬ LÝ ĐÁM MÂY", mau_chinh=C_DANGER, mau_nen=C_DANGER_BG,
                  noi_dung=(
                      "Yêu cầu: 'Hãy tóm tắt cuộc khám thành bệnh án SOAP'\n\n"
                      "• Gửi dữ liệu bệnh nhân lên máy chủ đám mây bên ngoài\n"
                      "• Mô hình tự do dự đoán từ ngữ theo xác suất thống kê\n"
                      "• Không có bước trung gian kiểm tra nguồn gốc câu trích dẫn\n"
                      "• Không có bộ quy tắc kiểm tra tương tác thuốc và liều lượng\n"
                      "• Dễ sinh thông tin không có trong thực tế khi gặp câu phức tạp."
                  ), co_td=9.5, co_nd=8.2)

    mui_ten_ngang(ax, 9.7, 7.1, 10.1, mau=C_DANGER, day=2.5)

    the_chuc_nang(ax, 10.2, 5.35, 8.1, 3.55, "3. RỦI RO VÀ HẠN CHẾ TRONG BỆNH ÁN ĐẦU RA",
                  badge_buoc="HẠN CHẾ", mau_chinh=C_DANGER, mau_nen=C_DANGER_BG, max_char_td=45,
                  noi_dung=(
                      "[!] Sinh thông tin không có trong lời thoại: Tự điền huyết áp 120/80 hoặc tiền sử dị ứng chưa ai nói.\n"
                      "[!] Nhầm lẫn đối tượng người nói: Ghi bệnh hen của người bố vào bệnh án của người con gái!\n"
                      "[!] Lưu giữ thông tin đã bị sửa: Vẫn ghi 'ho 1 tuần' dù bệnh nhân đã đính chính 'mới 3 hôm'.\n"
                      "[!] Nhầm lẫn câu dặn dò tương lai: Ghi 'Đã chụp X-quang' dù bác sĩ dặn 'Nếu mai sốt mới chụp'.\n"
                      "[!] Không kiểm tra an toàn thuốc: Không tự phát hiện đơn thuốc có 2 hoạt chất tương tác bất lợi.\n"
                      "[!] Khó kiểm tra lại nguồn: Bác sĩ muốn xác minh phải nghe lại toàn bộ đoạn ghi âm rất mất thời gian."
                  ), co_td=9.5, co_nd=8.2)

    # Nửa dưới: Nhánh B - MediTrace Sentinel
    khung_bot = FancyBboxPatch((0.6, 0.40), 18.0, 4.55, boxstyle="round,pad=0.03,rounding_size=0.08",
                               linewidth=1.4, edgecolor=C_SAFE, facecolor="white")
    ax.add_patch(khung_bot)
    ax.text(0.9, 4.65, "PHƯƠNG PHÁP B: HỆ THỐNG MEDITRACE SENTINEL (KẾT HỢP AI VÀ KIỂM TRA LOGIC ĐA TẦNG)",
            ha="left", va="center", fontsize=11.2, fontweight="bold", color=C_SAFE)

    the_chuc_nang(ax, 0.9, 0.65, 3.6, 3.75, "1. TIẾP NHẬN & XỬ LÝ AN TOÀN",
                  badge_buoc="XỬ LÝ TẠI CHỖ", mau_chinh=C_SAFE, mau_nen=C_SAFE_BG,
                  noi_dung=(
                      "• Vận hành tại máy tính phòng khám\n"
                      "• Tự động ẩn danh hóa theo Nghị định 13\n"
                      "• Đánh số từng câu thoại [T1], [T2]...\n"
                      "• Chuẩn hóa từ ngữ địa phương 3 miền\n"
                      "• Nhận diện tên thuốc gọi dân gian."
                  ), co_td=9.5, co_nd=8.3)

    mui_ten_ngang(ax, 4.6, 2.50, 5.0, mau=C_SAFE, day=2.5)

    the_chuc_nang(ax, 5.1, 0.65, 4.5, 3.75, "2. QUY TRÌNH KIỂM SOÁT ĐA TẦNG",
                  badge_buoc="KIỂM TRA LOGIC", mau_chinh=C_TEAL, mau_nen=C_TEAL_BG,
                  noi_dung=(
                      "• Tầng 1: AI chỉ trích xuất JSON, không viết tự do\n"
                      "• Tầng 2: Phân loại rõ Bệnh nhân vs Người nhà\n"
                      "• Tầng 3: Tự động loại bỏ tin cũ khi người nói sửa lời\n"
                      "• Tầng 4: Quy trình 7 bước (K1-K7) kiểm tra câu trích dẫn\n"
                      "• Tầng 5: Kiểm tra tương tác thuốc, liều lượng và thận\n"
                      "• Bảo mật thông tin nội bộ, không gửi dữ liệu ra ngoài."
                  ), co_td=9.5, co_nd=8.3)

    mui_ten_ngang(ax, 9.7, 2.50, 10.1, mau=C_SAFE, day=2.5)

    the_chuc_nang(ax, 10.2, 0.65, 8.1, 3.75, "3. BỆNH ÁN SOAP MINH BẠCH, CHUẨN XÁC & DỄ KIỂM TRA",
                  badge_buoc="KẾT QUẢ ĐẠT ĐƯỢC", mau_chinh=C_SAFE, mau_nen=C_SAFE_BG, max_char_td=45,
                  noi_dung=(
                      "[OK] Loại bỏ thông tin suy diễn: Không có trong lời thoại gốc thì không được đưa vào bệnh án.\n"
                      "[OK] Phân định đúng đối tượng: Giảm 6 lần tỷ lệ nhầm triệu chứng của người nhà (từ 12.4% xuống 2.1%).\n"
                      "[OK] Cập nhật đúng nội dung đính chính: Giảm 14 lần lỗi nhớ nhầm thông tin cũ (từ 11.5% xuống 0.8%).\n"
                      "[OK] Bấm xem lại nguồn tức thì: Bấm vào từng câu để nghe lại đúng đoạn âm thanh tương ứng trong cuộc khám.\n"
                      "[OK] Hỗ trợ an toàn đơn thuốc: Tự động cảnh báo tương tác thuốc và liều dùng theo chức năng thận.\n"
                      "[OK] Tối ưu hóa thời gian: Bác sĩ chỉ cần kiểm tra các mục được bôi đỏ cảnh báo trước khi duyệt."
                  ), co_td=9.5, co_nd=8.2)

    luu_anh(fig, "flow-5-so-sanh-doi-dau-chatgpt-vs-meditrace.png")


# ==============================================================================
# HÌNH 6: DỮ LIỆU THỰC NGHIỆM VÀ QUY TRÌNH KIỂM THỬ TỰ ĐỘNG (1.330 TEST)
# ==============================================================================
def ve_flow_6_ma_tran_test():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 6: DỮ LIỆU THỰC NGHIỆM VÀ QUY TRÌNH KIỂM THỬ TỰ ĐỘNG (1.330 TRƯỜNG HỢP KIỂM THỬ)",
              "Phương pháp đánh giá độc lập, bộ dữ liệu kiểm nghiệm đa dạng và kết quả kiểm thử tự động toàn diện hệ thống",
              badge_text="1.330 BÀI KIỂM THỬ ĐẠT 100%", badge_color=C_SAFE)

    w_box1 = 5.1
    w_box2 = 7.2
    w_box3 = 4.8
    y_top = 9.1
    h_all = 8.4
    y_bot = y_top - h_all

    # Khối 1: Ma trận dữ liệu thực nghiệm
    x1 = 0.6
    the_chuc_nang(ax, x1, y_bot, w_box1, h_all, "TẬP DỮ LIỆU ĐÁNH GIÁ ĐỘC LẬP",
                  badge_buoc="DỮ LIỆU TEST", mau_chinh=C_NAVY, mau_nen="white",
                  noi_dung=(
                      "• 200 KHUÔN CA BỆNH ĐỘC LẬP (Template-Disjoint):\n"
                      "  Bao phủ 10 chuyên khoa nội, ngoại, nhi, truyền nhiễm...\n"
                      "  Tập kiểm thử gồm các ca bệnh độc lập mà mô hình AI\n"
                      "  chưa từng gặp trong quá trình huấn luyện (đảm bảo khách quan).\n\n"
                      "• 5.000 ĐOẠN HỘI THOẠI MÔ PHỎNG ĐA DẠNG:\n"
                      "  Đo độ phong phú từ vựng đạt 78.3%\n"
                      "  (đảm bảo câu từ tự nhiên và phong phú như giao tiếp thực tế).\n\n"
                      "• 300 CA THỬ NGHIỆM BẪY SAI SÓT (Adversarial Testing):\n"
                      "  Thiết kế các cặp tình huống so sánh ranh giới dễ nhầm:\n"
                      "  - Ca A: Bệnh nhân có tiền sử dị ứng Penicillin\n"
                      "  - Ca B: Người nhà có tiền sử dị ứng Penicillin (đổi đối tượng)\n"
                      "  - Người bệnh đính chính mốc thời gian sau một vài câu thoại\n"
                      "  - Chèn thêm tiếng ồn môi trường và cách phát âm 3 miền\n\n"
                      "-> ĐẢM BẢO TÍNH ĐỘC LẬP VÀ ĐÁNH GIÁ TOÀN DIỆN."
                  ), co_td=10.0, co_nd=8.5)

    mui_ten_ngang(ax, x1 + w_box1 + 0.05, 5.0, x1 + w_box1 + 0.40, mau=C_PURPLE)

    # Khối 2: Đường ống 1.330 Bài Test CI/CD
    x2 = 6.15
    the_chuc_nang(ax, x2, y_bot, w_box2, h_all, "1.330 TRƯỜNG HỢP KIỂM THỬ TỰ ĐỘNG (CI/CD PIPELINE)",
                  badge_buoc="PYTEST 100% PASS", mau_chinh=C_PURPLE, mau_nen=C_PURPLE_BG, max_char_td=42,
                  noi_dung=(
                      "Toàn bộ mã nguồn hệ thống được kiểm định tự động qua 1.330 bài test:\n\n"
                      "• NHÓM 0: NHẬN DẠNG TIẾNG NÓI & TÊN THUỐC (62 tests)\n"
                      "  - Kiểm tra quét lặp từ ASR, từ vựng phương ngữ 3 miền\n"
                      "  - Kiểm tra cơ chế BÔI ĐỎ cảnh báo tên thuốc gọi dân gian\n\n"
                      "• NHÓM 1: TRÍCH XUẤT THÔNG TIN JSON (145 tests)\n"
                      "  - Kiểm tra tính hợp lệ của JSON, không sinh văn tự do, lưu câu thoại gốc [Ti]\n\n"
                      "• NHÓM 2: PHÂN BIỆT ĐẠI TỪ & BẢO MẬT DỮ LIỆU (120 tests)\n"
                      "  - Kiểm tra đại từ tiếng Việt, chức năng ẩn danh hóa theo Nghị định 13/CP\n\n"
                      "• NHÓM 3: XỬ LÝ ĐÍNH CHÍNH & LỌC CÂU GIẢ ĐỊNH (98 tests)\n"
                      "  - Kiểm tra loại bỏ thông tin cũ khi người nói sửa lời, phân loại câu dặn dò\n\n"
                      "• NHÓM 4: QUY TRÌNH KIỂM TRA LOGIC 7 BƯỚC K1-K7 (280 tests)\n"
                      "  - Kiểm tra việc ngăn chặn số liệu huyết áp hoặc trích dẫn tự suy diễn\n\n"
                      "• NHÓM 5: AN TOÀN ĐƠN THUỐC & 9 THANG ĐIỂM LÂM SÀNG (310 tests)\n"
                      "  - Kiểm tra 30 cặp thuốc tương tác, liều tối đa Paracetamol, tính độ lọc thận\n\n"
                      "• NHÓM TÍCH HỢP HỆ THỐNG VÀ BẢO MẬT (315 tests)\n"
                      "  - Kiểm tra xuất hồ sơ theo chuẩn HL7 FHIR và xác thực toàn vẹn dữ liệu."
                  ), co_td=10.0, co_nd=8.5)

    mui_ten_ngang(ax, x2 + w_box2 + 0.05, 5.0, x2 + w_box2 + 0.40, mau=C_SAFE)

    # Khối 3: Bảng chỉ số đối chứng thực nghiệm
    x3 = 13.8
    the_chuc_nang(ax, x3, y_bot, w_box3, h_all, "KẾT QUẢ THỰC NGHIỆM ĐO ĐẠC",
                  badge_buoc="KẾT QUẢ ĐO ĐẠC", mau_chinh=C_SAFE, mau_nen=C_SAFE_BG,
                  noi_dung=(
                      "KẾT QUẢ VƯỢT TRỘI SO VỚI MÔ HÌNH AI THÔNG THƯỜNG:\n\n"
                      "• ĐỘ CHÍNH XÁC TRÍCH XUẤT ĐÚNG NGUỒN (Attribution F1):\n"
                      "  Tăng từ 66.1% lên 70.8% (+4.7% F1)\n\n"
                      "• TỶ LỆ LỖI GÁN THUỘC TÍNH (Slot Error Rate):\n"
                      "  Giảm từ 45.4% xuống 36.9% (-8.5% SER)\n\n"
                      "• LỖI NHẦM NGƯỜI NHÀ SANG BỆNH NHÂN:\n"
                      "  Giảm hơn 6 lần (từ 12.4% xuống còn 2.1%)\n\n"
                      "• LỖI GIỮ LẠI THÔNG TIN NÓI NHẦM ĐÃ BỊ SỬA:\n"
                      "  Giảm hơn 14 lần (từ 11.5% xuống còn 0.8%)\n\n"
                      "• TỶ LỆ BỎ SÓT DỊ ỨNG THUỐC:\n"
                      "  0.0% (Toàn bộ cảnh báo dị ứng đều được ghi nhận)\n\n"
                      "• THÔNG TIN ĐÚNG BỊ CHẶN NHẦM:\n"
                      "  0.0% (0 / 30.136 dòng dữ liệu kiểm thử)\n\n"
                      "• TỔNG KẾT KIỂM THỬ MÃ NGUỒN:\n"
                      "  1.330 / 1.330 BÀI TEST ĐẠT KẾT QUẢ 100%!"
                  ), co_td=10.0, co_nd=8.6)

    badge_test = FancyBboxPatch((x3 + 0.3, 0.95), w_box3 - 0.6, 0.46,
                                boxstyle="round,pad=0.02,rounding_size=0.08",
                                facecolor=C_SAFE, edgecolor="none")
    ax.add_patch(badge_test)
    ax.text(x3 + w_box3/2, 1.18, "[PASS] 1.330 / 1.330 TEST ĐẠT 100%", ha="center", va="center",
            fontsize=9.2, fontweight="bold", color="white")

    luu_anh(fig, "flow-6-duong-ong-kiem-thu-thuc-nghiem-1330-test.png")


# ==============================================================================
# HÌNH 7: QUY TRÌNH BÁC SĨ SỬ DỤNG HỆ THỐNG TRONG CA KHÁM BỆNH (< 60 GIÂY THAO TÁC)
# ==============================================================================
def ve_flow_7_quy_trinh_bac_si():
    fig, ax = plt.subplots(figsize=(19.2, 10.8), facecolor=C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 19.2)
    ax.set_ylim(0, 10.8)
    ax.axis("off")

    ve_header(ax,
              "FLOW 7: QUY TRÌNH BÁC SĨ SỬ DỤNG HỆ THỐNG TRONG CA KHÁM BỆNH (< 60 GIÂY THAO TÁC)",
              "Bác sĩ làm chủ toàn bộ quy trình, giảm thao tác gõ phím thủ công và tiết kiệm 5–7 phút cho mỗi lượt khám",
              badge_text="BÁC SĨ KIỂM SOÁT", badge_color=C_CYAN)

    cac_buoc = [
        ("BƯỚC 01", "BẤM NÚT 'BẮT ĐẦU KHÁM'", C_NAVY, C_NAVY_BG,
         "• Bác sĩ bấm 1 nút trên màn hình\n"
         "• Hệ thống bắt đầu tiếp nhận âm thanh\n"
         "• Bác sĩ tập trung hoàn toàn vào việc:\n"
         "  Lắng nghe, giao tiếp và thăm khám\n"
         "  trực tiếp cho người bệnh\n"
         "• Không cần vừa khám vừa gõ phím!",
         "[ 0 GIÂY THAO TÁC ]"),

        ("BƯỚC 02", "TỰ ĐỘNG LẬP HỒ SƠ BỆNH ÁN", C_TEAL, C_TEAL_BG,
         "• Khi kết thúc lượt khám bệnh\n"
         "• Sau khoảng 30-45 giây xử lý:\n"
         "  Bản nháp bệnh án chuẩn SOAP đã\n"
         "  chuẩn bị sẵn trên màn hình\n"
         "• Mỗi thông tin đều lưu kèm số thứ tự\n"
         "  câu thoại [Ti] trong đoạn ghi âm.",
         "[ 30s CÓ BẢN NHÁP ]"),

        ("BƯỚC 03", "RÀ SOÁT CÁC CẢNH BÁO BÔI ĐỎ", C_DANGER, C_DANGER_BG,
         "• Bác sĩ xem nhanh mục\n"
         "  'CẦN BÁC SĨ XÁC NHẬN':\n"
         "  - Tên thuốc nhận diện chưa chắc chắn\n"
         "  - Cảnh báo tương tác thuốc cần lưu ý\n"
         "  - Thông tin bệnh nhân đã tự sửa lại\n"
         "• Thời gian rà soát khoảng 20 giây.",
         "[ 20s RÀ SOÁT CẢNH BÁO ]"),

        ("BƯỚC 04", "KIỂM TRA LẠI ÂM THANH GỐC", C_WARN, C_WARN_BG,
         "• Với thông tin cần nghe lại đối chứng:\n"
         "  Bác sĩ bấm vào số thứ tự câu thoại\n"
         "• Hệ thống phát lại ngay đoạn âm thanh 2s\n"
         "  đúng giọng người bệnh nói\n"
         "• Bác sĩ bấm xác nhận hoặc chỉnh sửa\n"
         "  trực tiếp trên màn hình trong 1 giây!",
         "[ 1s NGHE ĐỐI SOÁT ]"),

        ("BƯỚC 05", "KÝ DUYỆT & IN HƯỚNG DẪN", C_SAFE, C_SAFE_BG,
         "• Bác sĩ bấm nút 'Ký duyệt':\n"
         "  - Niêm phong hồ sơ (mã hóa SHA-256)\n"
         "  - Chuyển vào phần mềm viện (EMR)\n"
         "• Tự động in Phiếu hướng dẫn dùng thuốc\n"
         "  (chia 4 khung giờ Sáng - Trưa - Chiều - Tối)\n"
         "• TIẾT KIỆM 5-7 PHÚT\n"
         "  CHO MỖI LƯỢT KHÁM!",
         "[ TIẾT KIỆM 5-7 PHÚT ]")
    ]

    w_card = 3.35
    h_card = 8.1
    y_card = 0.95

    for idx, (badge, tieu_de, mau, bg, noi_dung, badge_bot) in enumerate(cac_buoc):
        x_c = 0.6 + idx * 3.65
        the_chuc_nang(ax, x_c, y_card, w_card, h_card, tieu_de,
                      badge_buoc=badge, mau_chinh=mau, mau_nen=bg,
                      noi_dung=noi_dung, co_td=9.5, co_nd=8.5, max_char_td=22)
        
        w_pill = w_card - 0.5
        pill_bot = FancyBboxPatch((x_c + 0.25, y_card + 0.35), w_pill, 0.42,
                                  boxstyle="round,pad=0.02,rounding_size=0.08",
                                  facecolor=mau, edgecolor="none")
        ax.add_patch(pill_bot)
        ax.text(x_c + 0.25 + w_pill/2, y_card + 0.56, badge_bot, ha="center", va="center",
                fontsize=8.2, fontweight="bold", color="white")
        
        if idx < len(cac_buoc) - 1:
            mui_ten_ngang(ax, x_c + w_card + 0.05, 5.0, x_c + w_card + 0.25, mau=mau, day=2.2)

    # Dải tổng kết toàn trang ở dưới cùng
    summary_bar = FancyBboxPatch((0.6, 0.18), 18.0, 0.55,
                                  boxstyle="round,pad=0.02,rounding_size=0.08",
                                  facecolor=C_HEADER_BG, edgecolor=C_SAFE, linewidth=1.2)
    ax.add_patch(summary_bar)
    ax.text(9.6, 0.45,
            "TỔNG KẾT: BÁC SĨ CHỈ MẤT DƯỚI 60 GIÂY THAO TÁC TRÊN MÀN HÌNH — TẬP TRUNG THỜI GIAN VÀO VIỆC THĂM KHÁM VÀ CHĂM SÓC NGƯỜI BỆNH!",
            ha="center", va="center", fontsize=9.6, fontweight="bold", color="white")

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
