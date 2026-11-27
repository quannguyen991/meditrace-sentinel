# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Chất lượng dữ liệu]
Làm gì   : Đo độ lặp câu và độ đa dạng từ vựng của bộ hội thoại bằng một định nghĩa cố định,
           để so bộ cũ với bộ mới cùng một thước.
Vào → Ra : tệp jsonl hội thoại → tỉ lệ lặp câu, TTR, MTLD, distinct-2 in ra màn hình
Đọc từ   : do_lap_cau() tính các chỉ số cho cả bộ; tach_cau() tách lượt thành câu chuẩn hoá
Mục lục (các hàm/lớp chính):
  tach_cau()    Tách hội thoại thành câu, bỏ tên người nói
  mtld()        Tính độ đa dạng từ vựng MTLD hai chiều
  do_lap_cau()  Đo độ lặp câu và độ đa dạng từ của bộ ca
  doc_jsonl()   Đọc tệp jsonl, bỏ dòng trống hoặc hỏng
  main()        Chạy dòng lệnh đo độ lặp câu rồi in kết quả
Gọi tới  : he_thong/duong_dan
Dùng bởi : do_luong/nguon_lap_cau
Tên cũ   : do_lap_cau.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đo độ lặp câu và độ đa dạng từ vựng của một bộ hội thoại.

Bộ 5.000 ca hiện tại có tỉ lệ lặp câu rất cao (bản bàn giao 20/11/2026: 87.265 câu,
20.652 câu duy nhất, lặp 76,3%) và từ vựng nghèo (TTR 0,0020 so với 0,0181-0,0253
của dữ liệu thật). Công cụ này đo lại các con số đó bằng MỘT định nghĩa cố định, để
so bộ v1 với bộ v2 cùng một thước.

Định nghĩa:
  - một "câu" là một LƯỢT nói sau khi bỏ phần ghi người nói (`Bac si:`...), chuẩn hóa
    NFC, hạ chữ thường, gộp khoảng trắng;
  - ti_le_lap = 1 - so_cau_duy_nhat / so_cau;
  - TTR = số từ duy nhất / tổng số từ trên toàn bộ bộ;
  - MTLD (McCarthy & Jarvis 2010, ngưỡng 0,72) ít phụ thuộc độ dài văn bản hơn TTR;
  - distinct-2 = số cặp từ liên tiếp duy nhất / tổng số cặp (tính trong từng câu).

Chạy: python -m src.do_luong.do_lap_cau data/hoi_thoai_viet_5000.jsonl
"""
from __future__ import annotations

import collections
import json
import re
import sys
import unicodedata
from typing import Iterable

from src.he_thong import duong_dan as duong_dan

_TIEN_TO_NGUOI_NOI = re.compile(r"^\s*[^:\n]{1,30}:\s*")
_TU = re.compile(r"[^\W_]+", re.UNICODE)


# ─── _chuan_hoa() — Chuẩn hoá câu: NFC, chữ thường, gộp khoảng trắng ──────────────────
def _chuan_hoa(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "").lower()
    return re.sub(r"\s+", " ", s).strip()


# ═══ tach_cau() — Tách hội thoại thành câu, bỏ tên người nói ══════════════════════════
# Mỗi dòng là một lượt nói; bỏ phần ghi người nói rồi chuẩn hoá.
def tach_cau(input_hoi_thoai: str) -> list[str]:
    """Tách `input` của một ca (mỗi dòng một lượt) thành các câu, bỏ phần ghi người nói."""
    ra = []
    for dong in (input_hoi_thoai or "").split("\n"):
        dong = _TIEN_TO_NGUOI_NOI.sub("", dong, count=1)
        dong = _chuan_hoa(dong)
        if dong:
            ra.append(dong)
    return ra


# ─── _tu() — Tách một câu thành các từ ────────────────────────────────────────────────
def _tu(cau: str) -> list[str]:
    return _TU.findall(cau)


# ─── _mtld_mot_chieu() — Tính MTLD theo một chiều đọc ─────────────────────────────────
# Cắt chuỗi thành các đoạn khi tỉ lệ từ duy nhất rơi xuống ngưỡng, rồi lấy độ dài trung
# bình.
def _mtld_mot_chieu(tokens: list[str], nguong: float = 0.72) -> float:
    so_nhan_to, loai, tong = 0.0, set(), 0
    for t in tokens:
        tong += 1
        loai.add(t)
        if len(loai) / tong <= nguong:
            so_nhan_to += 1
            loai, tong = set(), 0
    if tong:
        ttr = len(loai) / tong
        so_nhan_to += (1 - ttr) / (1 - nguong)
    return len(tokens) / so_nhan_to if so_nhan_to else float(len(tokens))


# ═══ mtld() — Tính độ đa dạng từ vựng MTLD hai chiều ══════════════════════════════════
# Lấy trung bình MTLD xuôi và ngược; chuỗi rỗng trả 0,0.
def mtld(tokens: list[str], nguong: float = 0.72) -> float:
    """Trung bình MTLD xuôi và ngược. Chuỗi rỗng -> 0,0."""
    if not tokens:
        return 0.0
    return (_mtld_mot_chieu(tokens, nguong) + _mtld_mot_chieu(tokens[::-1], nguong)) / 2


# ═══ do_lap_cau() — Đo độ lặp câu và độ đa dạng từ của bộ ca ══════════════════════════
# Trả tỉ lệ lặp, TTR, MTLD, distinct-2 và các câu lặp nhiều nhất. Ca thiếu input bị bỏ.
def do_lap_cau(cac_ca: Iterable[dict], do_dai_tu_toi_thieu: int = 1) -> dict:
    """-> {"so_ca", "so_cau", "so_cau_duy_nhat", "ty_le_lap", "ttr", "mtld",
    "distinct2", "top_lap"}. Ca không có khóa `input` bị bỏ qua.
    Nếu `do_dai_tu_toi_thieu > 1`, chỉ tính các câu có ít nhất từng đó từ."""
    dem = collections.Counter()
    tu_tat_ca, loai_tu = [], set()
    cap_duy_nhat, tong_cap = set(), 0
    so_ca = 0
    for ca in cac_ca:
        if not isinstance(ca, dict) or "input" not in ca:
            continue
        so_ca += 1
        for cau in tach_cau(ca["input"]):
            tu = _tu(cau)
            if len(tu) < do_dai_tu_toi_thieu:
                continue
            dem[cau] += 1
            tu_tat_ca.extend(tu)
            loai_tu.update(tu)
            for i in range(len(tu) - 1):
                cap_duy_nhat.add((tu[i], tu[i + 1]))
                tong_cap += 1
    so_cau = sum(dem.values())
    duy_nhat = len(dem)
    return {
        "so_ca": so_ca,
        "so_cau": so_cau,
        "so_cau_duy_nhat": duy_nhat,
        "ty_le_lap": (1 - duy_nhat / so_cau) if so_cau else 0.0,
        "ttr": (len(loai_tu) / len(tu_tat_ca)) if tu_tat_ca else 0.0,
        "mtld": mtld(tu_tat_ca),
        "distinct2": (len(cap_duy_nhat) / tong_cap) if tong_cap else 0.0,
        "top_lap": [(c, n) for c, n in dem.most_common(20) if n > 1],
    }


# ═══ doc_jsonl() — Đọc tệp jsonl, bỏ dòng trống hoặc hỏng ═════════════════════════════
# Trả danh sách ca hợp lệ và số dòng bị bỏ.
def doc_jsonl(duong_dan_tep: str) -> tuple[list[dict], int]:
    """-> (cac_ca_hop_le, so_dong_bo). Dòng trống hoặc JSON hỏng được bỏ qua và đếm."""
    ca, bo = [], 0
    with open(duong_dan_tep, encoding="utf-8") as f:
        for dong in f:
            if not dong.strip():
                bo += 1
                continue
            try:
                x = json.loads(dong)
            except json.JSONDecodeError:
                bo += 1
                continue
            if isinstance(x, dict):
                ca.append(x)
            else:
                bo += 1
    return ca, bo


# ═══ main() — Chạy dòng lệnh đo độ lặp câu rồi in kết quả ═════════════════════════════
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser(description="Do do lap lai cau va chi so ngon ngu.")
    ap.add_argument("tep", help="duong dan tep jsonl")
    ap.add_argument("--do-dai-tu", type=int, default=1, help="do dai tu toi thieu cua cau (vi du: 8)")
    a = ap.parse_args()

    ca, bo = doc_jsonl(a.tep)
    r = do_lap_cau(ca, do_dai_tu_toi_thieu=a.do_dai_tu)
    print(f"tep: {a.tep}  (bo {bo} dong trong/hong)" + (f" (cau >= {a.do_dai_tu} tu)" if a.do_dai_tu > 1 else ""))
    for k in ("so_ca", "so_cau", "so_cau_duy_nhat"):
        print(f"{k:18s} {r[k]:,}")
    print(f"{'ty_le_lap':18s} {100 * r['ty_le_lap']:.2f}%")
    print(f"{'ttr':18s} {r['ttr']:.4f}")
    print(f"{'mtld':18s} {r['mtld']:.1f}")
    print(f"{'distinct2':18s} {r['distinct2']:.4f}")
    print("20 cau lap nhieu nhat:")
    for c, n in r["top_lap"]:
        print(f"  {n:6d}  {c[:90]}")


if __name__ == "__main__":
    main()
