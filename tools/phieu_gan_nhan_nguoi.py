# -*- coding: utf-8 -*-
"""Xuất phiếu gán nhãn MÙ cho hai người gán độc lập (kế hoạch 27/11, Task 7).

Mỗi dòng là một mệnh đề máy đã trích: người gán đọc lượt hội thoại được dẫn rồi chọn một nhãn
trong NHAN_HOP_LE (src/do_luong/dong_thuan_nhan.py). Phiếu KHÔNG có kết quả của bộ chấm tự động.

    python -m tools.phieu_gan_nhan_nguoi --vao data/thach_thuc/ra_C_khoa_thach_thuc_doi_chu_the_phat_trien.jsonl \
        --so-ca 40 --ra data/nhan-nguoi
    # → phieu_A.csv, phieu_B.csv (giống hệt nhau, mỗi người một tệp), huong_dan.md
    python -m tools.phieu_gan_nhan_nguoi --so A.csv B.csv   # in κ sau khi hai người gán xong

Chỉ dùng tập phát triển. Máy không điền nhãn.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from pathlib import Path

from src.do_luong.dong_thuan_nhan import NHAN_HOP_LE, dong_thuan, nap_nhan
from src.duong_ong.b5_viet_ban_nhap import _muc_cho

COT = ["ma_muc", "ma_ca", "luot_dan", "loi_noi_duoc_dan", "menh_de_may_ghi", "chu_the_may_ghi", "muc_may_xep",
       "toan_bo_hoi_thoai", "nhan", "ghi_chu"]


def _luot(van: str) -> list[str]:
    return [d for d in (van or "").split("\n") if d.strip()]


def xuat_phieu(ca_list: list[dict], so_ca: int = 40, seed: int = 2711) -> list[dict]:
    co_menh_de = [c for c in ca_list if c.get("phat_bieu")]
    chon = random.Random(seed).sample(co_menh_de, min(so_ca, len(co_menh_de)))
    rows: list[dict] = []
    for ca in sorted(chon, key=lambda c: str(c["id"])):
        luot = _luot(ca.get("input", ""))
        toan_bo = "\n".join(f"[{i}] {d}" for i, d in enumerate(luot, 1))
        for p in ca["phat_bieu"]:
            dan = [i for i in (p.get("bang_chung") or []) if isinstance(i, int)]
            rows.append({
                "ma_muc": f"{ca['id']}#{p.get('id')}",
                "ma_ca": ca["id"],
                "luot_dan": ",".join(map(str, dan)),
                "loi_noi_duoc_dan": " | ".join(luot[i - 1] for i in dan if 0 < i <= len(luot)),
                "menh_de_may_ghi": p.get("noi_dung", ""),
                "chu_the_may_ghi": p.get("ten_chu_the") or ("bệnh nhân" if p.get("chu_the_id", 0) == 0 else "người khác"),
                # Mục bệnh án máy xếp (để gán được nhãn sai_muc) và toàn bộ hội thoại (để xét đổi người/đính chính)
                "muc_may_xep": _muc_cho(p, 0)[0],
                "toan_bo_hoi_thoai": toan_bo,
                "nhan": "",
                "ghi_chu": "",
            })
    return rows


def _ghi(rows: list[dict], duong: Path) -> None:
    with open(duong, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COT)
        w.writeheader()
        w.writerows(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vao")
    ap.add_argument("--so-ca", type=int, default=40)
    ap.add_argument("--seed", type=int, default=2711)
    ap.add_argument("--ra", default="data/nhan-nguoi")
    ap.add_argument("--so", nargs=2, metavar=("PHIEU_A", "PHIEU_B"))
    a = ap.parse_args(argv)
    if a.so:
        kq = dong_thuan(nap_nhan(a.so[0]), nap_nhan(a.so[1]))
        print(json.dumps(kq, ensure_ascii=False, indent=2))
        if kq["kappa"] is None:
            print("κ không xác định (không có mục chung, hoặc cả hai chỉ dùng một nhãn).")
        else:
            print("Hai người gán nhất quán (κ ≥ 0,6)." if kq["kappa"] >= 0.6
                  else "Hai người gán chưa nhất quán (κ < 0,6): thống nhất lại hướng dẫn trước khi dùng nhãn.")
        print("Lưu ý: κ chỉ đo hai NGƯỜI có đồng ý với nhau không; muốn đánh giá bộ chấm tự động phải phân xử nhãn rồi so.")
        return 0
    if "viet_kiem_tra_cuoi" in (a.vao or ""):
        print("Không dùng tập kiểm tra niêm phong.", file=sys.stderr)
        return 2
    ca = [json.loads(d) for d in Path(a.vao).read_text(encoding="utf-8").splitlines() if d.strip()]
    rows = xuat_phieu(ca, a.so_ca, a.seed)
    ra = Path(a.ra)
    ra.mkdir(parents=True, exist_ok=True)
    _ghi(rows, ra / "phieu_A.csv")
    _ghi(rows, ra / "phieu_B.csv")
    (ra / "huong_dan.md").write_text(
        "# Hướng dẫn gán nhãn\n\nHai người gán **độc lập**, không bàn nhau, không xem kết quả của máy chấm.\n"
        "Mỗi dòng: đọc *lời nói được dẫn*, so với *mệnh đề máy ghi* và *chủ thể máy ghi*, rồi điền cột `nhan` bằng một trong:\n\n"
        "- `dung`: đúng nội dung, đúng người, đúng mục\n- `sai_nguoi`: nội dung có thật nhưng gán nhầm người\n"
        "- `sai_noi_dung`: sai số liệu, phủ định, thời gian hoặc thông tin đã bị đính chính\n"
        "- `bia`: hội thoại không nói điều này\n- `sai_muc`: đúng nội dung nhưng xếp nhầm mục\n- `khong_ro`: không quyết được\n",
        encoding="utf-8",
    )
    print(f"Đã ghi {len(rows)} mục từ {len({r['ma_ca'] for r in rows})} ca vào {ra}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
