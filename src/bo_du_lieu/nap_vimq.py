# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Dữ liệu ngoài]
Làm gì   : Đọc ViMQ (câu hỏi y tế có nhãn thực thể) và bỏ dấu gạch dưới để thành mẫu cho
           bước rút.
Vào → Ra : tệp JSON ViMQ + tên tập → danh sách dict mẫu (câu, thực thể gốc)
Đọc từ   : doc_vimq() đọc tập ViMQ thành danh sách mẫu; bo_gach_duoi() làm sạch từ ghép
Mục lục (các hàm/lớp chính):
  doc_vimq()      Đọc tệp ViMQ thành các mẫu câu kèm thực thể
  bo_gach_duoi()  Đổi gạch dưới thành khoảng trắng
Dùng bởi : bo_du_lieu/gan_nhan_truoc
Tên cũ   : nap_vimq.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Nạp ViMQ (câu hỏi y tế của bệnh nhân, có nhãn thực thể) thành mẫu cho khâu trích.

ViMQ (https://github.com/tadeephuy/ViMQ, phát hành học thuật, phi thương mại) là các câu
hỏi ĐƠN LẺ đã tách từ (nối từ bằng dấu gạch dưới: `dong_mach`), kèm `seq_label` là các đoạn
thực thể `[bat_dau, ket_thuc, loai]` theo CHỈ SỐ TỪ (ket_thuc tính cả). Không có hội thoại,
không có chủ thể, phủ định, thời gian.

Để cho khâu trích của dự án đọc được, mỗi câu được bỏ gạch dưới rồi bọc thành một lượt
`Benh nhan: <cau>` (giả định: người hỏi là bệnh nhân; ghi rõ trong báo cáo). Thực thể gốc
được giữ lại để ĐO phủ (không dùng để huấn luyện trực tiếp).
"""
from __future__ import annotations

import json
from pathlib import Path


# ═══ bo_gach_duoi() — Đổi gạch dưới thành khoảng trắng ════════════════════════════════
# Cũng gộp khoảng trắng thừa.
def bo_gach_duoi(s: str) -> str:
    return " ".join(str(s or "").replace("_", " ").split())


# ═══ doc_vimq() — Đọc tệp ViMQ thành các mẫu câu kèm thực thể ═════════════════════════
# Dòng có chỉ số thực thể ngoài câu bị bỏ riêng, không hỏng cả tệp.
def doc_vimq(duong_dan: str | Path, tap: str = "train") -> list[dict]:
    """-> [{"id", "input", "cau", "thuc_the": [{"text", "loai"}], "y_dinh"}].

    Dòng có chỉ số thực thể ngoài phạm vi câu bị bỏ qua riêng (không làm hỏng cả tệp).
    """
    du_lieu = json.loads(Path(duong_dan).read_text(encoding="utf-8"))
    if not isinstance(du_lieu, list):
        raise ValueError(f"{duong_dan}: can mot danh sach")
    ra = []
    for i, d in enumerate(du_lieu):
        cau = d.get("sentence")
        if not isinstance(cau, str) or not cau.strip():
            continue
        tu = cau.split()
        the = []
        for nhan in d.get("seq_label") or []:
            try:
                b, k, loai = int(nhan[0]), int(nhan[1]), str(nhan[2])
            except (TypeError, ValueError, IndexError):
                continue
            if 0 <= b <= k < len(tu):
                the.append({"text": bo_gach_duoi(" ".join(tu[b:k + 1])), "loai": loai})
        sach = bo_gach_duoi(cau)
        ra.append({"id": f"vimq_{tap}_{i:05d}", "input": f"Bệnh nhân: {sach}", "cau": sach,
                   "thuc_the": the, "y_dinh": d.get("sent_label")})
    return ra
