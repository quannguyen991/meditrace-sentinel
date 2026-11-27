# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Dữ liệu ngoài]
Làm gì   : Đọc bản chép lời VietMed và ghép các dòng liền nhau thành đoạn hội thoại đủ dài
           cho bước rút.
Vào → Ra : tệp chép lời VietMed → danh sách dòng; danh sách dòng → danh sách đoạn (tối đa số
           ký tự cho phép)
Đọc từ   : doc_chep_loi() đọc tệp; ghep_doan() ghép dòng thành đoạn theo mã ghi âm
Mục lục (các hàm/lớp chính):
  doc_chep_loi()  Đọc tệp chép lời VietMed thành danh sách dòng
  ma_ghi_am()     Lấy mã bản ghi từ một dòng chép lời
  ghep_doan()     Gom các dòng liền nhau cùng bản ghi thành đoạn
Tên cũ   : nap_vietmed.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đọc và ghép chép lời VietMed thành đoạn hội thoại (Task B5 của kế hoạch).

Tệp `labeled_medical_data/*_transcript.txt` của VietMed là một DANH SÁCH KIỂU TỪ ĐIỂN
PYTHON (nháy đơn), KHÔNG phải JSON, nên đọc bằng `ast.literal_eval` (không dùng `eval`).
Mỗi phần tử: {'text', 'speaker_name', 'file', 'duration'}. Mỗi phần tử là một lát cắt
khoảng 5 giây của ghi âm dài, nên phải ghép lại theo bản ghi (thư mục của `file`) mới
có đoạn hội thoại.

Chưa có nhãn mệnh đề: đoạn này dùng làm bộ đánh giá hoặc gán nhãn sau (Task E3, E4).
"""
from __future__ import annotations

import ast
import re
from pathlib import Path


# ═══ doc_chep_loi() — Đọc tệp chép lời VietMed thành danh sách dòng ═══════════════════
# Phải là danh sách từ điển Python hợp lệ; đọc an toàn, không chạy mã.
def doc_chep_loi(duong_dan: str | Path) -> list[dict]:
    """Đọc một tệp `*_transcript.txt`. Nội dung không phải danh sách từ điển hợp lệ
    -> `ValueError` rõ ràng, không thực thi mã."""
    van_ban = Path(duong_dan).read_text(encoding="utf-8")
    try:
        x = ast.literal_eval(van_ban)
    except (ValueError, SyntaxError) as e:
        raise ValueError(f"{duong_dan}: khong phai danh sach tu dien Python hop le ({e})") from e
    if not isinstance(x, list) or not all(isinstance(d, dict) for d in x):
        raise ValueError(f"{duong_dan}: can mot danh sach cac tu dien")
    return x


# ═══ ma_ghi_am() — Lấy mã bản ghi từ một dòng chép lời ════════════════════════════════
# Lấy thư mục đầu của file; thiếu thì bỏ hậu tố khỏi tên người nói.
def ma_ghi_am(dong: dict) -> str:
    """Mã bản ghi: thư mục đầu của `file` (ví dụ `VietMed_007/1465.0_1470.0.ogg` ->
    `VietMed_007`). Thiếu `file` thì lấy `speaker_name` bỏ hậu tố `_a`/`_b`."""
    f = str(dong.get("file") or "")
    if "/" in f:
        return f.split("/", 1)[0]
    ten = str(dong.get("speaker_name") or "")
    return re.sub(r"_[a-z]$", "", ten) or "khong-ro"


# ═══ ghep_doan() — Gom các dòng liền nhau cùng bản ghi thành đoạn ═════════════════════
# Cắt khi quá giới hạn ký tự; giữ người nói từng lượt, bỏ dòng rỗng.
def ghep_doan(dong: list[dict], toi_da_ky_tu: int = 6000) -> list[dict]:
    """Gom các dòng LIÊN TIẾP cùng bản ghi thành đoạn; cắt khi quá `toi_da_ky_tu`.

    -> [{"id", "luot": [{"nguoi_noi", "van_ban"}], "van_ban", "so_dong"}]. Người nói
    (`speaker_name`, ví dụ `VietMed_007_a`) được giữ nguyên từng lượt để bước sau gán vai.
    Dòng không có `text` hoặc rỗng bị bỏ qua. Một dòng đơn lẻ dài hơn giới hạn vẫn được
    giữ thành một đoạn riêng (không cắt giữa câu).
    """
    ra: list[dict] = []
    hien, ma_hien, dai = None, None, 0
    stt: dict[str, int] = {}

    def dong_doan():
        nonlocal hien, dai
        if hien and hien["luot"]:
            hien["van_ban"] = " ".join(x["van_ban"] for x in hien["luot"])
            hien["so_dong"] = len(hien["luot"])
            ra.append(hien)
        hien, dai = None, 0

    for d in dong:
        text = str(d.get("text") or "").strip()
        if not text:
            continue
        ma = ma_ghi_am(d)
        if hien is None or ma != ma_hien or (dai + len(text) + 1 > toi_da_ky_tu and hien["luot"]):
            dong_doan()
            stt[ma] = stt.get(ma, 0) + 1
            hien = {"id": f"{ma}#{stt[ma]}", "luot": []}
            ma_hien = ma
        hien["luot"].append({"nguoi_noi": str(d.get("speaker_name") or ""), "van_ban": text})
        dai += len(text) + 1
    dong_doan()
    return ra
