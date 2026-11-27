# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Dữ liệu ngoài]
Làm gì   : Cho mô hình của dự án gán trước mệnh đề lên câu ViMQ, rồi lọc bằng luật, ra nhãn
           máy chưa kiểm.
Vào → Ra : tệp ViMQ + checkpoint adapter → kết quả lọc nhãn máy (giữ / loại) và bảng tổng
           hợp; tệp đệm đọc lại được không cần GPU
Đọc từ   : main() lấy mẫu, chạy rút, lọc nhãn; tong_hop() gom kết quả lọc; doc_dem() đọc tệp
           đệm
Mục lục (các hàm/lớp chính):
  tong_hop()  Tổng hợp kết quả lọc nhãn máy trên câu ViMQ
  doc_dem()   Đọc tệp đệm kết quả trích thành từ điển theo id
  main()      Lấy mẫu ViMQ, chạy trích rồi lọc nhãn máy
Gọi tới  : bo_du_lieu/loc_nhan_may, bo_du_lieu/nap_vimq, he_thong/duong_dan,
           huan_luyen/chon_mo_hinh_bakeoff
Tên cũ   : gan_nhan_truoc.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Gán nhãn mệnh đề TRƯỚC bằng mô hình của dự án cho dữ liệu ngoài (Task E4, thu nhỏ).

Dùng đúng đường ép đầu ra theo lược đồ của dự án (`bakeoff.LUOC_DO`), nên kết quả luôn
ĐÚNG KHUÔN; khuôn đúng không có nghĩa giá trị đúng (nhất là `chu_the`). Vì vậy kết quả
phải qua `loc_nhan_may.loc_menh_de_may` và chỉ là "nhãn máy chưa kiểm".

Chạy trên máy có GPU (HoaiDuc), qua tràn VRAM:
  python tools/run_capped.py --phan-vram 0.74 --mo-dun src.bo_du_lieu.gan_nhan_truoc -- \\
      --tep data-ngoai/ViMQ/data/train.json --n 200 \\
      --adapter models/nen-qwen3-4b-trich-v2/best_checkpoint
Chỉ lọc và tổng hợp từ tệp đệm đã có (không cần GPU): thêm `--chi-loc`.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

from src.he_thong import duong_dan as duong_dan
from src.bo_du_lieu.loc_nhan_may import loc_menh_de_may, phu_thuc_the
from src.bo_du_lieu.nap_vimq import doc_vimq


# ═══ tong_hop() — Tổng hợp kết quả lọc nhãn máy trên câu ViMQ ═════════════════════════
# Trả thống kê và danh sách bản ghi huấn luyện tiềm năng có mệnh đề qua lọc.
def tong_hop(mau: list[dict], ket_qua: dict) -> dict:
    """`ket_qua`: {id: bản ghi tệp đệm}. -> {"thong_ke", "giu"}.

    `giu` là danh sách bản ghi huấn luyện tiềm năng (chưa dùng để huấn luyện):
    {"id", "input", "dap_an", "nguon", "nhan"}. Chỉ gồm câu có ít nhất một mệnh đề qua lọc.
    """
    tk = {"so_mau": 0, "so_co_ket_qua": 0, "so_json_loi": 0, "so_menh_de_may": 0,
          "so_menh_de_giu": 0, "ly_do_bo": {}, "so_cau_giu": 0,
          "phu_truoc_loc": {"so_thuc_the": 0, "so_phu": 0},
          "phu_sau_loc": {"so_thuc_the": 0, "so_phu": 0}}
    giu_ra = []
    for m in mau:
        tk["so_mau"] += 1
        k = ket_qua.get(m["id"])
        if k is None:
            continue
        tk["so_co_ket_qua"] += 1
        if not k.get("json_hop_le", False):
            tk["so_json_loi"] += 1
        menh_de = k.get("phat_bieu") or []
        tk["so_menh_de_may"] += len(menh_de)
        giu, bo = loc_menh_de_may(menh_de, m["input"])
        tk["so_menh_de_giu"] += len(giu)
        for b in bo:
            tk["ly_do_bo"][b["ly_do"]] = tk["ly_do_bo"].get(b["ly_do"], 0) + 1
        for ten, ds in (("phu_truoc_loc", menh_de), ("phu_sau_loc", giu)):
            r = phu_thuc_the(ds, m.get("thuc_the") or [])
            tk[ten]["so_thuc_the"] += r["so_thuc_the"]
            tk[ten]["so_phu"] += r["so_phu"]
        if giu:
            tk["so_cau_giu"] += 1
            giu_ra.append({"id": m["id"], "input": m["input"], "dap_an": giu,
                           "nguon": m.get("nguon", "vimq"), "nhan": "may-chua-kiem"})
    for ten in ("phu_truoc_loc", "phu_sau_loc"):
        t = tk[ten]
        t["ti_le"] = (t["so_phu"] / t["so_thuc_the"]) if t["so_thuc_the"] else 0.0
    return {"thong_ke": tk, "giu": giu_ra}


# ═══ doc_dem() — Đọc tệp đệm kết quả trích thành từ điển theo id ══════════════════════
# Mỗi dòng là một bản ghi JSON; tệp không có thì trả rỗng.
def doc_dem(duong_dan_dem: Path) -> dict:
    ra = {}
    if Path(duong_dan_dem).exists():
        for dong in Path(duong_dan_dem).read_text(encoding="utf-8").splitlines():
            if dong.strip():
                x = json.loads(dong)
                ra[x["id"]] = x
    return ra


# ═══ main() — Lấy mẫu ViMQ, chạy trích rồi lọc nhãn máy ═══════════════════════════════
# Có thể chỉ lọc (--chi-loc); in thống kê và ghi các câu giữ lại.
def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tep", required=True, help="tep ViMQ train/dev/test.json")
    ap.add_argument("--phan-tap", default="train", dest="tap")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--hat", type=int, default=2611)
    ap.add_argument("--model", default=duong_dan.MODEL_CHINH)
    ap.add_argument("--adapter", default=None)
    ap.add_argument("--max-token", type=int, default=1024)
    ap.add_argument("--chi-loc", action="store_true")
    ap.add_argument("--ra", default=None, help="tep jsonl cho cac menh de da loc")
    a = ap.parse_args()

    toan = doc_vimq(a.tep, a.tap)
    mau = random.Random(a.hat).sample(toan, min(a.n, len(toan)))
    mau.sort(key=lambda m: m["id"])
    dem = duong_dan.THU_MUC_DU_LIEU / f"trich_ngoai_vimq_{a.tap}_{a.n}_{a.hat}.jsonl"
    if not a.chi_loc:
        from src.huan_luyen import chon_mo_hinh_bakeoff as bakeoff
        tok, model, prefix_fn = bakeoff.nap(a.model, ep_json=True, adapter=a.adapter)
        bakeoff.trich(tok, model, prefix_fn, mau, max_token=a.max_token, luu_dan=dem)
    kq = tong_hop(mau, doc_dem(dem))
    print(json.dumps(kq["thong_ke"], ensure_ascii=False, indent=2))
    if a.ra:
        Path(a.ra).write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in kq["giu"]),
                              encoding="utf-8")
        print(f"Ghi {len(kq['giu'])} cau -> {a.ra}")


if __name__ == "__main__":
    main()
