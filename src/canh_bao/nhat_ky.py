# -*- coding: utf-8 -*-
"""[Lớp cảnh báo]
Làm gì   : Ghi các cảnh báo ra tệp nhật ký từng dòng để phục vụ nghiên cứu sau này.
Vào → Ra : mã ca + kết quả cảnh báo → các dòng nhật ký, ghi nối vào tệp jsonl
Đọc từ   : dong() dựng dòng nhật ký cho một ca; ghi() ghi ra tệp
Mục lục (các hàm/lớp chính):
  dong()  Chuyển kết quả cảnh báo thành các dòng nhật ký
  ghi()   Ghi nối các dòng nhật ký vào tệp JSON từng dòng
Gọi tới  : canh_bao/loai
Dùng bởi : do_luong/do_canh_bao
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Nhật ký cảnh báo cho nghiên cứu (đặc tả mục 49).

Mỗi dòng một cảnh báo: ca, phát biểu, mã, bằng chứng, bộ phát hiện, phiên bản,
mức độ, bất định, trạng thái cuối. Hai cột để trống (None) cho sau này điền:
    bac_si_xac_nhan    bác sĩ có đồng ý cảnh báo đúng không (từ giao diện duyệt)
    dung_theo_bo_cham  cảnh báo có trúng lỗi mà bộ chấm tự động tìm ra không
                       (`src.do_luong.do_canh_bao` điền khi chạy trên tập có đáp án)
"""
import json
from pathlib import Path
from typing import Iterable, List, Optional

from src.canh_bao.loai import PHIEN_BAN


# ═══ dong() — Chuyển kết quả cảnh báo thành các dòng nhật ký ══════════════════════════
# Mỗi cảnh báo một dòng; hai cột bác sĩ xác nhận và đúng theo bộ chấm để trống.
def dong(ca_id: str, kq: dict, nhan_bo_cham: Optional[dict] = None) -> List[dict]:
    """kq = `gop.chay(...)`. nhan_bo_cham = {phat_bieu_id: dung/sai} nếu có."""
    ra = []
    for pid, v in kq["theo_phat_bieu"].items():
        tt = kq["trang_thai_D"][pid]["trang_thai"]
        for c in v["tat_ca"]:
            ra.append(_dong(ca_id, c, tt, None if nhan_bo_cham is None else nhan_bo_cham.get((pid, c.ma))))
    for c in kq["toan_ca"]:
        ra.append(_dong(ca_id, c, None, None))
    return ra


# ─── _dong() — Dựng một dòng nhật ký cho một cảnh báo ─────────────────────────────────
def _dong(ca_id, c, trang_thai_cuoi, dung):
    return {"ca": ca_id, "phat_bieu": c.phat_bieu_id, "ma": c.ma, "nhom": c.nhom, "luot": c.luot,
            "trich": c.trich, "ly_do": c.ly_do, "bo_phat_hien": c.bo_phat_hien, "phien_ban": PHIEN_BAN,
            "tin_cay_bo_phat_hien": c.tin_cay, "ket_luan": c.ket_luan, "muc_do": c.muc_do,
            "bat_dinh": c.bat_dinh, "anh_huong_trang_thai": c.anh_huong_trang_thai,
            "trang_thai_cuoi": trang_thai_cuoi, "bac_si_xac_nhan": None, "dung_theo_bo_cham": dung}


# ═══ ghi() — Ghi nối các dòng nhật ký vào tệp JSON từng dòng ══════════════════════════
# Tự tạo thư mục nếu chưa có.
def ghi(duong: Path, cac_dong: Iterable[dict]):
    duong.parent.mkdir(parents=True, exist_ok=True)
    with open(duong, "a", encoding="utf-8") as f:
        for d in cac_dong:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
