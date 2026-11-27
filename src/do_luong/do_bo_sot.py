# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Đo tỉ lệ mệnh đề của đáp án mà bước rút không rút ra được, để trả lời câu giảm bỏ
           sót thông tin quan trọng bằng số.
Vào → Ra : danh sách (đáp án, bản rút) từng ca → tổng mệnh đề, số bỏ sót, tỉ lệ bỏ sót, theo
           nhóm lỗi
Đọc từ   : ti_le_bo_sot() ghép đáp án với bản rút rồi đếm mệnh đề không ghép được
Mục lục (các hàm/lớp chính):
  ti_le_bo_sot()  Tính tỉ lệ bỏ sót mệnh đề so với đáp án
Gọi tới  : do_luong/do_trich
Tên cũ   : do_bo_sot.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đo TỈ LỆ BỎ SÓT thông tin của khâu trích mệnh đề.

Một mệnh đề của đáp án là BỎ SÓT nếu không có bản trích nào ghép được với nó.
Dùng chính phép ghép của `src.do_luong.do_trich.ghep` (ghép tham lam theo độ giống từ,
ngưỡng 0,6), nên số liệu này cùng hệ với các số khác của dự án.

Câu 1 của giám khảo: "giảm bỏ sót thông tin quan trọng". Chỉ số này trả lời câu đó
bằng SỐ, thay cho câu chung chung.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Optional

from src.do_luong.do_trich import NGUONG_GHEP, ghep


# ═══ ti_le_bo_sot() — Tính tỉ lệ bỏ sót mệnh đề so với đáp án ═════════════════════════
# Ghép đáp án với bản rút theo ngưỡng; trả tổng, số bỏ sót, tỉ lệ và theo nhóm lỗi.
def ti_le_bo_sot(cac_ca: list[tuple[list[dict], Optional[list[dict]]]],
                 nguong: float = NGUONG_GHEP) -> dict:
    """`cac_ca`: mỗi phần tử là `(dap_an, trich)`; `trich` có thể là None (coi như rỗng).

    -> {"so_menh_de_dap_an", "so_bo_sot", "ti_le_bo_sot", "theo_nhom"}. Mệnh đề đáp án
    có khóa `nhom_loi` thì tính riêng theo nhóm; thiếu khóa thì vào nhóm "khác".
    """
    tong = bo_sot = 0
    nhom = defaultdict(lambda: [0, 0])
    for dap_an, trich in cac_ca:
        dap_an = dap_an or []
        _cap, thieu, _thua = ghep(dap_an, trich or [], nguong)
        ma_thieu = {id(d) for d in thieu}
        for d in dap_an:
            ten = d.get("nhom_loi") or "khac"
            nhom[ten][0] += 1
            tong += 1
            if id(d) in ma_thieu:
                nhom[ten][1] += 1
                bo_sot += 1
    return {
        "so_menh_de_dap_an": tong,
        "so_bo_sot": bo_sot,
        "ti_le_bo_sot": (bo_sot / tong) if tong else 0.0,
        "theo_nhom": {k: {"so_menh_de": v[0], "so_bo_sot": v[1],
                          "ti_le": (v[1] / v[0]) if v[0] else 0.0}
                      for k, v in sorted(nhom.items())},
    }
