# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 0 – Chuẩn hoá đầu vào]
Làm gì   : Cắt một lời nói thành các đoạn ngắn theo dấu câu, để nơi sinh dữ liệu và nơi kiểm
           căn cứ cùng dùng một cách cắt.
Vào → Ra : một lời thoại (chuỗi chữ) → danh sách vị trí (đầu, cuối) của từng đoạn; dấu kết
           của đoạn
Đọc từ   : cac_doan() cắt lời thành đoạn; dau_ket() lấy dấu câu ngay sau một đoạn
Mục lục (các hàm/lớp chính):
  cac_doan()  Cắt lời nói thành các đoạn ngắn theo dấu câu
  dau_ket()   Lấy dấu câu ngay sau một đoạn
  _them()     Thêm đoạn đã cắt khoảng trắng vào danh sách
Dùng bởi : bo_du_lieu/sinh_hoi_thoai_viet, duong_ong/b4_kiem_can_cu
Tên cũ   : doan_van.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Cắt một lời thoại thành ĐOẠN theo dấu câu — MỘT định nghĩa dùng chung.

Dùng ở hai nơi, và hai nơi PHẢI cắt giống nhau:

  sinh_hoi_thoai_viet  tìm đoạn bằng chứng cho `trich_dan` của đáp án
  khoa_bang_chung      tìm đoạn hội thoại CHƯA được phát biểu nào dẫn tới

Hai cách cắt khác nhau thì "đoạn" của đáp án và "đoạn" mà khoá kiểm không khớp
nhau, và không có gì báo lỗi — họ lỗi "hai khâu dùng hai đơn vị văn bản" đã gặp
ở `sua_cuc_bo._co`.

Dấu phẩy và dấu chấm GIỮA HAI CHỮ SỐ không tách: "38,5 độ", "37.8". Dấu hai chấm
không tách: "Sinh hiệu em đo được: ..." là một ý.
"""
from typing import List, Tuple

DAU_DOAN = ";!?…"


# ═══ cac_doan() — Cắt lời nói thành các đoạn ngắn theo dấu câu ════════════════════════
# Trả về danh sách (đầu, cuối) trên chính chuỗi gốc, đã bỏ khoảng trắng hai đầu; không
# cắt dấu thập phân giữa hai chữ số.
def cac_doan(van: str) -> List[Tuple[int, int]]:
    """-> [(bat_dau, ket_thuc)] trên chính chuỗi `van`, đã bỏ khoảng trắng hai
    đầu mỗi đoạn. Đoạn rỗng bị bỏ."""
    ra, dau, n = [], 0, len(van)
    for i, c in enumerate(van):
        tach = c in DAU_DOAN or (
            c in ",." and not (0 < i < n - 1 and van[i - 1].isdigit()
                               and van[i + 1].isdigit()))
        if tach:
            _them(ra, van, dau, i)
            dau = i + 1
    _them(ra, van, dau, n)
    return ra


# ═══ dau_ket() — Lấy dấu câu ngay sau một đoạn ════════════════════════════════════════
# Dùng để biết đoạn đó có phải câu hỏi không; trả về chuỗi rỗng nếu hết chuỗi.
def dau_ket(van: str, doan: Tuple[int, int]) -> str:
    """Dấu câu NGAY SAU đoạn ("" nếu hết chuỗi) — để biết đoạn có là câu hỏi."""
    j = doan[1]
    while j < len(van) and van[j].isspace():
        j += 1
    return van[j] if j < len(van) else ""


# ─── _them() — Thêm đoạn đã cắt khoảng trắng vào danh sách ────────────────────────────
# Bỏ qua đoạn rỗng.
def _them(ra, van, a, b):
    while a < b and van[a].isspace():
        a += 1
    while b > a and van[b - 1].isspace():
        b -= 1
    if b > a:
        ra.append((a, b))
