# -*- coding: utf-8 -*-
"""[Dịch vụ, an toàn và minh bạch › An toàn]
Làm gì   : Che định danh trước khi ghi log tiến trình; in lỗi chỉ gồm tên lớp, tệp:dòng và thông
           điệp đã che (Đề cải tiến 1, 28/11/2026 — không đưa dữ liệu nhận dạng vào log).
Vào → Ra : giá trị bất kỳ → chuỗi đã cắt ngắn và che; ngoại lệ → vài dòng stderr an toàn
Mục lục:
  che_log()          Che định danh rồi cắt ngắn; còn sót thì chỉ trả độ dài
  in_loi_an_toan()   Thay cho traceback.print_exc(): không in giá trị biến, thông điệp đã che
Gọi tới  : he_thong/khu_dinh_danh
Dùng bởi : he_thong/dich_vu_http
"""
from __future__ import annotations

import sys
import traceback

from src.he_thong.khu_dinh_danh import ClinicalDeidentifier


def che_log(gia_tri, toi_da: int = 300) -> str:
    s = gia_tri if isinstance(gia_tri, str) else repr(gia_tri)
    # Che TRƯỚC rồi mới cắt (cắt trước có thể chặt đôi số điện thoại / tên); giới hạn 8.000 ký tự đầu vào.
    try:
        kq = ClinicalDeidentifier.an_danh_van_ban(s[:8000])
        da_che = kq.van_ban_da_an_danh
        if ClinicalDeidentifier.kiem_tra_con_sot(da_che):
            return f"[đã ẩn {len(s)} ký tự: còn định danh]"
    except Exception:  # bộ che hỏng thì không được làm lộ: chỉ ghi độ dài
        return f"[đã ẩn {len(s)} ký tự: bộ che lỗi]"
    return da_che[:toi_da]


def in_loi_an_toan(exc: BaseException, file=None) -> None:
    file = file or sys.stderr
    khung = traceback.extract_tb(exc.__traceback__)
    dong = [f"[loi] {type(exc).__name__}: {che_log(str(exc))}"]
    for k in khung[-8:]:
        dong.append(f"    tại {k.filename}:{k.lineno} trong {k.name}")
    print("\n".join(dong), file=file, flush=True)
