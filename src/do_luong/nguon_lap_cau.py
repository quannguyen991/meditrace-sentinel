# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Chất lượng dữ liệu]
Làm gì   : Truy mỗi câu lặp của bộ hội thoại về chỗ sinh ra nó trong bộ sinh: nhóm câu, mẫu
           f-string, câu cố định hay ghép.
Vào → Ra : tệp jsonl hội thoại + mã bộ sinh → bảng số câu lặp theo nguồn, tùy chọn ghi
           markdown (--ra)
Đọc từ   : phan_loai_nguon() gán một câu vào nguồn; bang_nguon_lap() thống kê toàn bộ
Mục lục (các hàm/lớp chính):
  phan_loai_nguon()  Phân loại một câu theo nguồn sinh ra nó
  bang_nguon_lap()   Thống kê câu lặp theo nguồn sinh
  main()             Chạy dòng lệnh phân tích nguồn câu lặp của một tệp
Gọi tới  : do_luong/do_lap_cau, bo_du_lieu/ngu_lieu_viet
Tên cũ   : nguon_lap_cau.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Câu lặp trong bộ hội thoại đến từ đâu? (Task B2 của kế hoạch nâng cấp)

Đếm mỗi câu lặp của bộ, rồi phân loại theo NGUỒN trong mã:
  - "nhom:<TEN>"   câu bằng đúng một phần tử của nhóm <TEN> trong `ngu_lieu_viet`
                   (kể cả nhóm lồng nhau, ví dụ `MIEN.bac.chao_cuoi`)
  - "mau-f-string:dongN"  câu khớp một f-string ở dòng N của `sinh_hoi_thoai_viet.py`
  - "cau-co-dinh"  câu bằng đúng một chuỗi văn bản cố định viết thẳng trong
                   `sinh_hoi_thoai_viet.py` (không thuộc nhóm nào)
  - "ghep"         còn lại: câu được ghép từ nhiều mảnh (f-string) hoặc dùng động từ
                   trung tính; muốn sửa phải sửa chỗ ghép, không thêm câu vào nhóm

Chạy: python -m src.do_luong.nguon_lap_cau data/hoi_thoai_viet_5000.jsonl [--ra docs/do-lap-cau-nguon.md]
"""
from __future__ import annotations

import ast
import collections
import re
import sys
from pathlib import Path

from src.do_luong import do_lap_cau as dl
from src.bo_du_lieu import ngu_lieu_viet as nl

_GOC = Path(__file__).resolve().parents[1] / "bo_du_lieu"  # nơi đặt bộ sinh hội thoại


# ─── _lam_phang() — Duyệt hằng ngữ liệu lồng nhau, gom chuỗi theo đường dẫn ───────────
def _lam_phang(v, duong: str, ra: dict[str, set[str]]) -> None:
    """Duyệt đệ quy hàng của `nl` (list/tuple/dict lồng nhau), gom chuỗi theo ĐƯỜNG DẪN
    (ví dụ `MIEN.bac.chao_cuoi`, `XA_GIAO`)."""
    if isinstance(v, str):
        ra.setdefault(duong, set()).add(dl._chuan_hoa(v))
    elif isinstance(v, dict):
        for k, x in v.items():
            _lam_phang(x, f"{duong}.{k}", ra)
    elif isinstance(v, (list, tuple)):
        for x in v:
            _lam_phang(x, duong, ra)


# ─── _cac_nhom_cau() — Gom câu của mọi hằng kho ngữ liệu theo nhóm ────────────────────
# Bỏ chuỗi dưới 6 ký tự vì không phải câu hội thoại.
def _cac_nhom_cau() -> dict[str, set[str]]:
    """{DUONG_DAN_NHOM: tập câu đã chuẩn hoá} cho mỗi hằng HOA của `nl` (kể cả lồng nhau)."""
    ra: dict[str, set[str]] = {}
    for ten in dir(nl):
        if ten.isupper():
            _lam_phang(getattr(nl, ten), ten, ra)
    # Chuỗi quá ngắn hoặc chỉ là một từ (tên bệnh, thuốc...) không phải câu hội thoại.
    return {k: {c for c in v if len(c) >= 6} for k, v in ra.items()}


# ─── _mau_f_string() — Dựng mẫu regex từ các f-string của bộ sinh hội thoại ───────────
# Phần văn bản giữ nguyên, phần trong ngoặc nhọn thành ký tự bất kỳ.
def _mau_f_string() -> list[tuple[str, "re.Pattern[str]"]]:
    """[(ten, regex)] cho mỗi f-string trong sinh_hoi_thoai_viet.py: phần văn bản giữ
    nguyên, phần {..} thành `.+?`. Câu lặp như "<goi> đi khám cho mình phải không ạ?"
    không nằm trong nhóm nào mà đến từ một f-string."""
    nguon = (_GOC / "sinh_hoi_thoai_viet.py").read_text(encoding="utf-8")
    ra = []
    for n in ast.walk(ast.parse(nguon)):
        if isinstance(n, ast.JoinedStr):
            manh = []
            for x in n.values:
                if isinstance(x, ast.Constant):
                    manh.append(re.escape(dl._chuan_hoa(str(x.value))))
                else:
                    manh.append(".+?")
            mau = "".join(manh)
            if len(re.sub(r"\.|\.\+\?", "", mau)) >= 6:
                ra.append((f"mau-f-string:dong{n.lineno}", re.compile(mau)))
    return ra


# ─── _cau_co_dinh() — Lấy các chuỗi hằng viết thẳng trong bộ sinh hội thoại ───────────
# Chỉ lấy chuỗi từ 6 ký tự trở lên, không tính f-string.
def _cau_co_dinh() -> set[str]:
    """Mỗi hằng chuỗi >= 6 ký tự viết thẳng trong sinh_hoi_thoai_viet.py (không phải f-string)."""
    cay = ast.parse((_GOC / "sinh_hoi_thoai_viet.py").read_text(encoding="utf-8"))
    ra = set()
    for n in ast.walk(cay):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and len(n.value) >= 6:
            ra.add(dl._chuan_hoa(n.value))
    return ra


# ═══ phan_loai_nguon() — Phân loại một câu theo nguồn sinh ra nó ══════════════════════
# Thứ tự: nhóm ngữ liệu, câu cố định, mẫu f-string, rồi ghép (còn lại).
def phan_loai_nguon(cau: str, nhom: dict[str, set[str]] | None = None,
                    co_dinh: set[str] | None = None,
                    mau: list | None = None) -> str:
    """-> "nhom:<DUONG_DAN>" | "cau-co-dinh" | "mau-f-string:dong<N>" | "ghep".

    `cau` đã qua `do_lap_cau.tach_cau`. Thứ tự: nhóm của `ngu_lieu_viet`, chuỗi cố định
    trong `sinh_hoi_thoai_viet.py`, f-string, rồi "ghep" (còn lại).
    """
    nhom = _cac_nhom_cau() if nhom is None else nhom
    co_dinh = _cau_co_dinh() if co_dinh is None else co_dinh
    mau = _mau_f_string() if mau is None else mau
    c = dl._chuan_hoa(cau)
    for ten, tap in nhom.items():
        if c in tap:
            return f"nhom:{ten}"
    if c in co_dinh:
        return "cau-co-dinh"
    for ten, rx in mau:
        if rx.fullmatch(c):
            return ten
    return "ghep"


# ═══ bang_nguon_lap() — Thống kê câu lặp theo nguồn sinh ══════════════════════════════
# Số lặp tính bằng số lần xuất hiện trừ lần đầu; kèm 40 câu lặp nhiều nhất.
def bang_nguon_lap(cac_ca: list[dict]) -> dict:
    """-> {"tong_cau_lap": int, "theo_nguon": {nguon: so_cau_lap}, "top": [(cau, n, nguon)]}.

    "Số câu lặp" = số lần xuất hiện TRỪ lần đầu của mỗi câu (tổng = so_cau - so_cau_duy_nhat).
    """
    dem = collections.Counter()
    for ca in cac_ca:
        if isinstance(ca, dict) and "input" in ca:
            dem.update(dl.tach_cau(ca["input"]))
    nhom, co_dinh, mau = _cac_nhom_cau(), _cau_co_dinh(), _mau_f_string()
    theo = collections.Counter()
    for cau, n in dem.items():
        if n > 1:
            theo[phan_loai_nguon(cau, nhom, co_dinh, mau)] += n - 1
    top = [(c, n, phan_loai_nguon(c, nhom, co_dinh, mau))
           for c, n in dem.most_common(40) if n > 1]
    return {"tong_cau_lap": sum(theo.values()), "theo_nguon": dict(theo.most_common()),
            "top": top}


# ─── _in_bang() — Dựng bảng markdown nguồn của câu lặp ────────────────────────────────
def _in_bang(r: dict, tep: str) -> str:
    tong = r["tong_cau_lap"] or 1
    d = [f"# Nguon cua cau lap — {tep}", "",
         f"Tong so lan lap (tru lan dau cua tung cau): {r['tong_cau_lap']:,}", "",
         "| Nguon | So lan lap | Ty trong |", "|---|---:|---:|"]
    for nguon, n in r["theo_nguon"].items():
        d.append(f"| {nguon} | {n:,} | {100 * n / tong:.1f}% |")
    d += ["", "## 40 cau lap nhieu nhat", "", "| So lan | Nguon | Cau |", "|---:|---|---|"]
    for c, n, nguon in r["top"]:
        d.append(f"| {n:,} | {nguon} | {c[:100]} |")
    return "\n".join(d) + "\n"


# ═══ main() — Chạy dòng lệnh phân tích nguồn câu lặp của một tệp ══════════════════════
# Có thể ghi ra tệp markdown bằng tuỳ chọn --ra.
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        raise SystemExit("dung: python -m src.do_luong.nguon_lap_cau <tep.jsonl> [--ra tep.md]")
    tep = sys.argv[1]
    ca, _ = dl.doc_jsonl(tep)
    van_ban = _in_bang(bang_nguon_lap(ca), tep)
    if "--ra" in sys.argv:
        Path(sys.argv[sys.argv.index("--ra") + 1]).write_text(van_ban, encoding="utf-8")
    print(van_ban)


if __name__ == "__main__":
    main()
