# -*- coding: utf-8 -*-
"""Đo lường truyền lan và kiểm soát lỗi qua từng tầng (Yêu cầu 2).

Đo chính xác trên 4 bộ thử thách (đặc biệt là bộ nhiễu chép âm `thach_thuc_nhieu_asr_phat_trien`):
- Tầng 1 (Trích xuất): Bao nhiêu phát biểu có lỗi ở đầu ra mô hình.
- Tầng 2-3 (Gom người & Đính chính): Bao nhiêu lỗi được giữ ở trạng thái `bị thay thế` / `chưa giải quyết`.
- Tầng 4-5 (Khóa bằng chứng & Lớp cảnh báo Chính sách D): Bao nhiêu % lỗi Tầng 1 (và lỗi nguy hiểm)
  bị chặn lại ở `CẦN XÁC NHẬN` thay vì lọt vào thân bản nháp.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Dict

from src import cham_he_thong, cong_rui_ro, do_canh_bao, du_lieu, duong_dan
from src.canh_bao import gop
from src.phat_bieu import PhatBieu


def do_tung_bo(thu_muc: Path | None = None, nhanh: str = "C_khoa") -> Dict[str, object]:
    tm = Path(thu_muc or do_canh_bao.THU_MUC)
    ket_qua_theo_tap = {}
    tong_hop = Counter()

    for tap in do_canh_bao.cac_tap(tm, nhanh):
        goc = {c["id"]: c for c in du_lieu.nap_mau(tm / f"{tap}.jsonl")}
        tk = Counter()
        for r in du_lieu.nap_mau(tm / f"ra_{nhanh}_{tap}.jsonl"):
            ca = goc[r["id"]]
            ps = [PhatBieu(**d) for d in r["phat_bieu"]]
            loi, sot = cham_he_thong.loi_phat_bieu(ca, r["phat_bieu"])
            kq = gop.chay(ps, r["input"])

            tk["so_ca"] += 1
            tk["menh_de_bo_sot"] += len(sot)

            for p in ps:
                tk["tong_phat_bieu"] += 1
                ma_loi, loai = loi.get(p.id, ([], cong_rui_ro.loai_thong_tin(p)))
                co_loi = bool(set(ma_loi) & do_canh_bao.LOI_THAT)
                la_nguy_hiem = co_loi and (loai in do_canh_bao.NGUY_HIEM)

                if p.trang_thai == "bị thay thế":
                    tk["tang_2_3_thay_the"] += 1
                    if co_loi:
                        tk["loi_bi_loai_tang_2_3"] += 1
                    continue

                tk["con_hieu_luc"] += 1
                if co_loi:
                    tk["loi_tang_1_con_hieu_luc"] += 1
                if la_nguy_hiem:
                    tk["loi_nguy_hiem_tang_1"] += 1

                bi_chan_D = kq["trang_thai_D"][p.id]["trang_thai"] != gop.DA_KIEM_CHUNG
                if co_loi and bi_chan_D:
                    tk["loi_bi_chan_tang_4_5"] += 1
                if la_nguy_hiem and bi_chan_D:
                    tk["loi_nguy_hiem_bi_chan_tang_4_5"] += 1
                if la_nguy_hiem and not bi_chan_D:
                    tk["loi_nguy_hiem_lot_vao_than"] += 1

        ty_le_chan_loi = round(
            tk["loi_bi_chan_tang_4_5"] / max(tk["loi_tang_1_con_hieu_luc"], 1) * 100, 1
        )
        ty_le_chan_nh = round(
            tk["loi_nguy_hiem_bi_chan_tang_4_5"] / max(tk["loi_nguy_hiem_tang_1"], 1) * 100, 1
        )
        ket_qua_theo_tap[tap] = {
            **tk,
            "ty_le_chan_loi_tang_4_5_pct": ty_le_chan_loi,
            "ty_le_chan_loi_nguy_hiem_pct": ty_le_chan_nh,
        }
        tong_hop.update(tk)

    return {
        "nhanh": nhanh,
        "theo_tap": ket_qua_theo_tap,
        "tong_hop": {
            **tong_hop,
            "ty_le_chan_loi_tang_4_5_pct": round(
                tong_hop["loi_bi_chan_tang_4_5"] / max(tong_hop["loi_tang_1_con_hieu_luc"], 1) * 100, 1
            ),
            "ty_le_chan_loi_nguy_hiem_pct": round(
                tong_hop["loi_nguy_hiem_bi_chan_tang_4_5"] / max(tong_hop["loi_nguy_hiem_tang_1"], 1) * 100, 1
            ),
        },
    }


if __name__ == "__main__":
    res = do_tung_bo()
    dich = duong_dan.THU_MUC_KET_QUA / "truyen-lan-loi-tung-tang.json"
    dich.parent.mkdir(parents=True, exist_ok=True)
    dich.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res["tong_hop"], ensure_ascii=False, indent=2))
    print("\n--- THEO TAP ---")
    for tap, d in res["theo_tap"].items():
        print(
            f"{tap}: loi_tang_1={d['loi_tang_1_con_hieu_luc']}, "
            f"chan_4_5={d['loi_bi_chan_tang_4_5']} ({d['ty_le_chan_loi_tang_4_5_pct']}%), "
            f"loi_nh={d['loi_nguy_hiem_tang_1']}, "
            f"chan_nh={d['loi_nguy_hiem_bi_chan_tang_4_5']} ({d['ty_le_chan_loi_nguy_hiem_pct']}%)"
        )
