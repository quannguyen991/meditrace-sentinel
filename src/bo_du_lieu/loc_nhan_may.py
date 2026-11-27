# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Dữ liệu ngoài]
Làm gì   : Giữ lại mệnh đề do máy gán trước chỉ khi qua các phép kiểm bằng luật, như có câu
           trích thật trong lời thoại.
Vào → Ra : danh sách mệnh đề máy gán + văn bản hội thoại → (mệnh đề giữ, mệnh đề loại kèm lý
           do); thêm tỷ lệ phủ thực thể
Đọc từ   : loc_menh_de_may() tách mệnh đề giữ và loại; phu_thuc_the() đo tỷ lệ thực thể gốc
           được phủ
Mục lục (các hàm/lớp chính):
  loc_menh_de_may()  Lọc mệnh đề do máy sinh, giữ cái có câu trích thật
  phu_thuc_the()     Đo tỷ lệ thực thể gốc được mệnh đề phủ
  chuan()            Chuẩn hoá chuỗi để so khớp
Gọi tới  : do_luong/do_trich
Dùng bởi : bo_du_lieu/gan_nhan_truoc
Tên cũ   : loc_nhan_may.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Lọc tự động các mệnh đề do MÁY gán trước (Task E4 của kế hoạch nâng cấp).

Nhãn do máy gán có thể sai và không ai kiểm lại, nên chỉ giữ mệnh đề qua các phép kiểm có
thể kiểm BẰNG LUẬT. Phép kiểm này chỉ bắt được nhãn sai rõ ràng; KHÔNG chứng minh được
chủ thể, phủ định hay thời gian đúng. Không thay được người đọc.
"""
from __future__ import annotations

import unicodedata

from src.do_luong.do_trich import do_giong

CAC_TRUONG_BAT_BUOC = ("chu_the", "noi_dung", "do_chac_chan", "luot_thoai")
DO_CHAC_CHAN = {"chắc chắn", "nghi ngờ", "chưa ghi nhận"}


# ═══ chuan() — Chuẩn hoá chuỗi để so khớp ═════════════════════════════════════════════
# NFC, chữ thường, gộp khoảng trắng.
def chuan(s) -> str:
    return " ".join(unicodedata.normalize("NFC", str(s or "")).lower().split())


# ═══ loc_menh_de_may() — Lọc mệnh đề do máy sinh, giữ cái có câu trích thật ═══════════
# Giữ khi đủ trường, câu trích là chuỗi con nguyên văn của văn bản và không trùng.
def loc_menh_de_may(menh_de: list[dict], van_ban: str) -> tuple[list[dict], list[dict]]:
    """-> (giu, bo); mỗi phần tử của `bo` có thêm khoá `ly_do`.

    Giữ khi: đủ trường bắt buộc, `chu_the` và `noi_dung` không rỗng, `do_chac_chan` hợp lệ,
    `trich_dan` KHÔNG rỗng và mỗi chuỗi là chuỗi con nguyên văn của `van_ban` (sau NFC), và
    không trùng (chu_the, noi_dung) với một mệnh đề đã giữ.
    """
    giu, bo, da_co = [], [], set()
    goc = chuan(van_ban)
    for m in menh_de or []:
        ly_do = None
        if not isinstance(m, dict):
            bo.append({"menh_de": m, "ly_do": "khong phai tu dien"})
            continue
        thieu = [k for k in CAC_TRUONG_BAT_BUOC if k not in m]
        if thieu:
            ly_do = f"thieu truong {thieu}"
        elif not chuan(m["chu_the"]) or not chuan(m["noi_dung"]):
            ly_do = "chu_the hoac noi_dung rong"
        elif m["do_chac_chan"] not in DO_CHAC_CHAN:
            ly_do = "do_chac_chan khong hop le"
        else:
            td = m.get("trich_dan")
            if not isinstance(td, list) or not td or not all(isinstance(x, str) and x.strip() for x in td):
                ly_do = "khong co trich_dan"
            elif any(chuan(x) not in goc for x in td):
                ly_do = "trich_dan khong phai chuoi con cua van ban"
            else:
                khoa = (chuan(m["chu_the"]), chuan(m["noi_dung"]))
                if khoa in da_co:
                    ly_do = "trung menh de"
                else:
                    da_co.add(khoa)
        if ly_do:
            bo.append({**m, "ly_do": ly_do})
        else:
            giu.append(m)
    return giu, bo


# ═══ phu_thuc_the() — Đo tỷ lệ thực thể gốc được mệnh đề phủ ══════════════════════════
# Thực thể phủ khi nằm trong nội dung hoặc độ giống từ ngưỡng 0,6.
def phu_thuc_the(menh_de: list[dict], thuc_the: list[dict], nguong: float = 0.6) -> dict:
    """Tỉ lệ thực thể gốc (của bộ NER) được một mệnh đề PHỦ: chuỗi thực thể nằm trong
    `noi_dung`, hoặc `do_giong` >= ngưỡng. -> {"so_thuc_the", "so_phu", "ti_le_phu"}."""
    noi = [chuan(m.get("noi_dung")) for m in menh_de or []]
    phu = 0
    for t in thuc_the or []:
        x = chuan(t.get("text"))
        if x and any(x in n or do_giong(x, n) >= nguong for n in noi):
            phu += 1
    tong = len(thuc_the or [])
    return {"so_thuc_the": tong, "so_phu": phu, "ti_le_phu": (phu / tong) if tong else 0.0}
