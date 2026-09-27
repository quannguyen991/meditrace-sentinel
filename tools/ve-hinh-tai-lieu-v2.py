# -*- coding: utf-8 -*-
"""Hinh cho bo tai lieu v2 (17/09/2026). Khong ghi de hinh cua ban v1.

Khac v1:
  - bo so "Hinh N." trong anh: hai tai lieu danh so hinh khac nhau, so nam o chu
    thich duoi anh trong tai lieu;
  - so do cac buoc ghi ro vai tro: mo hinh DE XUAT, chuong trinh AP DUNG CHINH SACH,
    bac si QUYET DINH CUOI;
  - so do chinh sach xuat ban BA TRANG THAI thay cho so do bon duong cua v1;
  - doi "khoa bang chung" thanh "kiem chung bang chung" trong tieu de.

Cac hinh con lai dung lai ham ve cua v1 (doc so lieu tu docs/ket-qua/).

    python tools/ve-hinh-tai-lieu-v2.py
"""
import re
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
nguon = (GOC / "tools" / "ve-hinh-tai-lieu.py").read_text(encoding="utf-8")
nguon = re.sub(r"Hình \d+\. ", "", nguon)
nguon = nguon.replace('"docs" / "tai-lieu" / "hinh"', '"docs" / "tai-lieu" / "hinh-v2"')
nguon = nguon.replace("Đánh đổi của khoá bằng chứng (thế hệ {the_he})", "Đánh đổi của bước kiểm chứng bằng chứng (thế hệ {the_he})")
nguon = nguon.replace("Chuỗi xử lý dùng mô hình (B, C, C_khoa) so với ba đối chứng chỉ dùng luật — bộ đổi chủ thể, thế hệ 7",
                      "Nhánh dùng mô hình so với đối chứng chỉ dùng luật (bộ đổi chủ thể, thế hệ 7)")
# 18/09/2026: hai bo phuong ngu va nhieu ASR da chay lai co rang buoc JSON — bo gach cheo.
nguon = nguon.replace('mo=lambda g: g in ("thach_thuc_phuong_ngu_phat_trien", "thach_thuc_nhieu_asr_phat_trien"))', 'mo=None)')
nguon = nguon.replace('"* cột gạch chéo: lần chạy chưa ép JSON, đang chạy lại, số sẽ còn đổi"', '"cùng điều kiện chạy có ràng buộc JSON"')
nguon = nguon.replace('ngữ*"', 'ngữ"').replace('ASR*"', 'ASR"')
g = {"__name__": "ve_hinh_v1", "__file__": str(GOC / "tools" / "ve-hinh-tai-lieu.py")}
exec(compile(nguon, "ve-hinh-tai-lieu.py", "exec"), g)

plt = g["plt"]
hop, mui_ten, luu = g["hop"], g["mui_ten"], g["luu"]
MO_HINH, CHUONG_TRINH, KIEM_SOAT, NGUOI, NEN = (g["MO_HINH"], g["CHUONG_TRINH"], g["KIEM_SOAT"],
                                                g["NGUOI"], g["NEN"])


def hinh_cac_buoc():
    fig, ax = plt.subplots(figsize=(8.4, 9.0))
    ax.set_xlim(0, 12)
    ax.set_ylim(-0.2, 12.55)
    ax.axis("off")
    buoc = [
        ("Hội thoại khám bệnh, mỗi lượt nói được đánh số", "#777777", "ĐẦU VÀO", ""),
        ("Chuẩn hoá lời thoại: hiểu phương ngữ,\ngiữ nguyên văn lời gốc", CHUONG_TRINH, "CHƯƠNG TRÌNH", "theo luật"),
        ("Rút mệnh đề lâm sàng có cấu trúc\n(nội dung, chủ thể, mức chắc chắn, tình huống,\nlượt nói, trích dẫn)", MO_HINH,
         "MÔ HÌNH NGÔN NGỮ", "đề xuất"),
        ("Liên kết người, cập nhật trạng thái\n(đính chính, diễn biến, mâu thuẫn)", CHUONG_TRINH, "CHƯƠNG TRÌNH", "theo luật"),
        ("Kiểm chứng từng mệnh đề với lời thoại gốc", KIEM_SOAT, "CHƯƠNG TRÌNH", "theo luật"),
        ("Quyết định xuất bản: đã kiểm chứng /\ncần bác sĩ xác nhận / bị loại hoặc bị thay thế", KIEM_SOAT,
         "CHƯƠNG TRÌNH", "chính sách"),
        ("Tạo bản nháp có truy vết + thứ tự ưu tiên duyệt\n+ tối đa 3 câu hỏi làm rõ gợi ý", CHUONG_TRINH,
         "CHƯƠNG TRÌNH", "theo mẫu câu"),
        ("Xem, sửa, xác nhận và chịu trách nhiệm cuối cùng", NGUOI, "BÁC SĨ", "quyết định cuối"),
    ]
    h, khe = 1.12, 0.3
    y = 12.2 - h
    for i, (chu, mau, vai, phu) in enumerate(buoc):
        nen = "#E6F0EE" if mau == MO_HINH else ("#FBF0EE" if mau == KIEM_SOAT else "white")
        hop(ax, 3.3, y, 8.5, h, chu, mau, nen=nen, co=10.2)
        ax.text(3.05, y + h / 2 + 0.14, vai, ha="right", va="center", fontsize=10, color=mau, fontweight="bold")
        ax.text(3.05, y + h / 2 - 0.2, phu, ha="right", va="center", fontsize=9.3, color=mau)
        if i < len(buoc) - 1:
            mui_ten(ax, 7.55, y, 7.55, y - khe + 0.02)
        y -= h + khe
    ax.set_title("Các bước xử lý và vai trò của từng bên", fontsize=12.5, fontweight="bold")
    luu(fig, "cac-buoc-va-vai-tro.png")


def hinh_ba_trang_thai():
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.set_xlim(0, 12.6)
    ax.set_ylim(0, 8.2)
    ax.axis("off")
    hop(ax, 3.8, 6.6, 5, 1.2, "Mệnh đề do mô hình đề xuất\n(kèm lượt nói và trích dẫn)", MO_HINH, "#E6F0EE", dam=True)
    hop(ax, 3.8, 4.5, 5, 1.2, "Kiểm chứng với lời thoại gốc\n+ luật cập nhật trạng thái", KIEM_SOAT, dam=True)
    mui_ten(ax, 6.3, 6.6, 6.3, 5.72)
    o = [
        (0.2, "ĐÃ KIỂM CHỨNG\n(trong phạm vi luật hiện có)",
         "Vào thân bản nháp,\nkèm lượt nói làm căn cứ", MO_HINH),
        (4.4, "CẦN BÁC SĨ XÁC NHẬN\nthiếu căn cứ, chủ thể chưa rõ,\nmâu thuẫn, lời nói nhiều nghĩa",
         "Chỉ ở mục \"Cần bác sĩ xác nhận\",\nkèm câu gốc và lý do", NGUOI),
        (8.6, "BỊ LOẠI HOẶC BỊ THAY THẾ\ntrái hội thoại, giả định ghi thành\nsự thật, đã có thông tin mới",
         "Không vào bản nháp;\nchỉ lưu trong lịch sử truy vết", KIEM_SOAT),
    ]
    for x, dau, cuoi, mau in o:
        hop(ax, x, 2.1, 3.8, 1.6, dau, mau, co=9.8, dam=True)
        hop(ax, x, 0.15, 3.8, 1.4, cuoi, mau, nen=NEN, co=9.6)
        mui_ten(ax, 6.3, 4.5, x + 1.9, 3.72, mau=mau)
        mui_ten(ax, x + 1.9, 2.1, x + 1.9, 1.57, mau=mau)
    ax.set_title("Chính sách xuất bản ba trạng thái", fontsize=12.5, fontweight="bold")
    luu(fig, "ba-trang-thai.png")


if __name__ == "__main__":
    hinh_cac_buoc()
    hinh_ba_trang_thai()
    for ten in ("hinh_nhanh", "hinh_qlora", "hinh_sai_chu_the", "hinh_danh_doi", "hinh_nam_tap",
                "hinh_doi_chung_luat", "hinh_do_tre", "hinh_cat_token", "hinh_du_lieu", "hinh_may_chay"):
        g[ten]()
    g["hinh_danh_doi"]("8", "h13-danh-doi-th8.png", 56)
