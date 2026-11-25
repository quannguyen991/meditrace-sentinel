# -*- coding: utf-8 -*-
"""Phep thu VANG: bo sinh cu va cach chia 200 khuon KHONG DUOC DOI.

Chup ngay 21/11/2026 truoc khi them khuon, tinh huong, kich ban moi (Luong F cua
`docs/superpowers/plans/2026-11-21-nang-cap-toan-dien-meditrace.md`). Moi tinh nang
moi nam sau co `mo_rong` mac dinh TAT; hai phep thu nay phai PASS truoc va sau moi
sua doi o Luong B va F.

  - `sinh_bo(200, seed=42)` phai cho ra DUNG chuoi byte nhu luc chup (bam SHA-256);
  - 200 khuon cu phai giu nguyen tap: 150 train, 26 phat trien, 24 kiem tra cuoi.
    Doi cach chia la lam doi tap kiem tra da dong bang va lam checkpoint ro ri.
"""
import hashlib
import json

from src import ngu_lieu_viet as nl
from src import sinh_hoi_thoai_viet as sh
from src import tach_tap_viet as tt

BAM_VANG = "2bedc64168fe45ddb73514d2cdb76537988fafbbf26f537afee4297b762af207"
PHAT_TRIEN_VANG = ["béo phì", "liệt mặt ngoại biên", "lạc nội mạc tử cung", "ngưng thở khi ngủ do tắc nghẽn", "nhiễm giun", "nhiễm khuẩn HP dạ dày kháng thuốc", "rối loạn cương dương", "rối loạn tiêu hóa do kháng sinh", "rối loạn ám ảnh cưỡng chế", "suy tim phân xuất tống máu giảm", "sỏi thận", "sốt mò", "sốt phát ban", "sốt siêu vi", "thiếu máu thiếu sắt", "trào ngược dạ dày thực quản", "táo bón chức năng", "viêm amidan hốc mủ", "viêm cơ tim do virus", "viêm da cơ địa", "viêm hạch mạc treo cấp", "viêm loét dạ dày do HP", "viêm màng não do virus", "viêm túi mật cấp", "viêm xoang", "áp xe phổi"]
KIEM_TRA_VANG = ["bệnh phổi tắc nghẽn mạn tính", "hen phế quản", "hẹp hở van hai lá", "hội chứng cushing do thuốc", "ngoại tâm thu", "phì đại tuyến tiền liệt", "rối loạn tiền đình", "suy tĩnh mạch chi dưới", "sỏi túi mật", "sởi ở trẻ em", "thoái hóa cột sống", "thoát vị đĩa đệm cột sống cổ", "viêm cầu thận cấp sau nhiễm liên cầu", "viêm gan C mạn", "viêm họng do liên cầu", "viêm khớp gối", "viêm loét đại trực tràng chảy máu", "viêm lộ tuyến cổ tử cung", "viêm mũi xoang mạn tính", "xơ cứng tai", "xơ phổi vô căn", "đau thắt lưng cơ năng", "đau đầu căng thẳng", "đau đầu cụm"]


def _bam(bo):
    return hashlib.sha256(json.dumps(bo, ensure_ascii=False, sort_keys=True)
                          .encode("utf-8")).hexdigest()


def test_sinh_bo_seed_42_khong_doi():
    assert _bam(sh.sinh_bo(200, seed=42)) == BAM_VANG


def test_chia_khuon_200_khong_doi():
    p = tt.phan_khuon([b["ten"] for b in getattr(nl, "BENH_GOC", nl.BENH[:200])])
    assert {k: len(v) for k, v in p.items()} == {
        "train": 150, "phat_trien": 26, "kiem_tra_cuoi": 24}
    assert sorted(p["phat_trien"]) == PHAT_TRIEN_VANG
    assert sorted(p["kiem_tra_cuoi"]) == KIEM_TRA_VANG
