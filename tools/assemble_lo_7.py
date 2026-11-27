# -*- coding: utf-8 -*-
"""Lắp ráp và kiểm định toàn diện Lô 7 (50 khuôn bệnh, 501-550) cho MediTrace V2."""
import json
import re
import unicodedata
from itertools import combinations
import pprint

from tools.lo7_part1 import PART1_DATA
from tools.lo7_part2 import PART2_DATA
from tools.lo7_part3 import PART3_DATA
from tools.lo7_part4 import PART4_DATA
from tools.lo7_part5 import PART5_DATA

from src.bo_du_lieu.khuon_mo_rong import DANH_SACH_UNG_VIEN_CON_LAI, BENH_MO_RONG
from src.bo_du_lieu import ngu_lieu_viet as nl
from src.bo_du_lieu import kiem_khuon as kk

ALL_50 = PART1_DATA + PART2_DATA + PART3_DATA + PART4_DATA + PART5_DATA
assert len(ALL_50) == 50, f"Expected 50 templates, got {len(ALL_50)}"

# 1. Đối chiếu chính xác danh sách ứng viên
CANDIDATES = DANH_SACH_UNG_VIEN_CON_LAI[200:250]
assert len(CANDIDATES) == 50

for idx, (b, c) in enumerate(zip(ALL_50, CANDIDATES), 1):
    assert b["ten"] == c[0], f"Khuôn {idx}: tên '{b['ten']}' != ứng viên '{c[0]}'"
    assert b["nhom"] == c[1], f"Khuôn {idx}: nhóm '{b['nhom']}' != ứng viên '{c[1]}'"
    assert b["dien_tien"] == c[2], f"Khuôn {idx}: diễn tiến '{b['dien_tien']}' != ứng viên '{c[2]}'"
    assert b["he_co_quan"] == c[3], f"Khuôn {idx}: hệ cơ quan '{b['he_co_quan']}' != ứng viên '{c[3]}'"
    assert b["da_duyet"] is False, f"Khuôn {idx}: da_duyet phải là False"

print("✓ 100% đối chiếu khớp danh sách ứng viên DANH_SACH_UNG_VIEN_CON_LAI[200:250]!")

# 2. Kiểm tra bắt buộc không chứa chuỗi con 'ốm'
for idx, b in enumerate(ALL_50, 1):
    text_repr = unicodedata.normalize("NFC", json.dumps(b, ensure_ascii=False).lower())
    assert "ốm" not in text_repr, f"Phát hiện 'ốm' trong khuôn {idx}: {b['ten']}"

print("✓ 100% không chứa bất kỳ chuỗi con 'ốm' nào!")

# 3. Kiểm tra biến thể: đủ 6 biến thể, không trùng, biến thể 0 khớp chính
for idx, b in enumerate(ALL_50, 1):
    for f_var, f_main in [
        ("bien_the_kham", "kham"),
        ("bien_the_chan_doan", "chan_doan"),
        ("bien_the_ke_hoach", "ke_hoach")
    ]:
        vars_list = b.get(f_var, [])
        assert isinstance(vars_list, list) and len(vars_list) == 6, f"Khuôn {idx} ({b['ten']}): {f_var} len != 6"
        assert len(set(vars_list)) == 6, f"Khuôn {idx} ({b['ten']}): {f_var} có biến thể trùng lặp!"
        assert b[f_main] == vars_list[0], f"Khuôn {idx} ({b['ten']}): {f_main} != {f_var}[0]"
    
    assert len(b["chinh"]) >= 3, f"Khuôn {idx} ({b['ten']}): chinh < 3"
    assert len(b["phu"]) >= 3, f"Khuôn {idx} ({b['ten']}): phu < 3"

print("✓ 100% kiểm tra biến thể (6 biến thể, không trùng, khớp biến thể 0) ĐẠT!")

# 4. Định nghĩa nhãn giới tính đặc thù Lô 7
GIOI_TINH_LO_7 = {
    "lichen xơ teo âm hộ": "nữ",
    "rụng tóc nội tiết androgenic nam": "nam"
}

# 5. Chạy kiem_tat_ca trên BENH_LO_7
chi_nu = {k for k, v in GIOI_TINH_LO_7.items() if v == "nữ"}
chi_nam = {k for k, v in GIOI_TINH_LO_7.items() if v == "nam"}

ket_qua_lo7 = kk.kiem_tat_ca(
    ALL_50,
    chi_nu=chi_nu,
    chi_nam=chi_nam,
    nhan_gioi=GIOI_TINH_LO_7,
    nguong_trung=0.20
)

loi_lo7 = [v for v in ket_qua_lo7.van_de if v.muc == "LOI"]
assert not loi_lo7, f"Có lỗi trong kiem_tat_ca Lô 7: {loi_lo7}"
assert len(ket_qua_lo7.cap_trung) == 0, f"Có cặp trùng >= 20% trong nội bộ Lô 7: {ket_qua_lo7.cap_trung}"

print("✓ kiem_tat_ca trên nội bộ Lô 7: 0 LOI, 0 cặp trùng >= 20%!")

# 6. Kiểm tra trùng lặp triệu chứng chéo với 200 khuôn gốc và 100 khuôn Lo 1-2
benh_goc = getattr(nl, "BENH_GOC", nl.BENH[:200])
tat_ca_da_co = benh_goc + BENH_MO_RONG
tu_da_co = {kk._chuan(b["ten"]): kk._tu_khoa([*b.get("chinh", []), *b.get("phu", [])]) for b in tat_ca_da_co}
tu_lo_7 = {kk._chuan(b["ten"]): kk._tu_khoa([*b.get("chinh", []), *b.get("phu", [])]) for b in ALL_50}

cap_trung_cheo = []
for ten_7, tokens_7 in tu_lo_7.items():
    for ten_cu, tokens_cu in tu_da_co.items():
        j = kk._jaccard(tokens_7, tokens_cu)
        if j >= 0.20:
            cap_trung_cheo.append((ten_7, ten_cu, round(j, 3)))

assert not cap_trung_cheo, f"Có cặp trùng lặp chéo >= 20%: {cap_trung_cheo}"
print(f"✓ Kiểm tra chéo {len(tu_lo_7)} khuôn Lô 7 với {len(tu_da_co)} khuôn hiện có: 0 CẶP TRÙNG LẶP >= 20%!")

# 7. Xuất file src/bo_du_lieu/khuon_lo_7.py
content = f'''# -*- coding: utf-8 -*-
"""Lô 7 Khuôn Bệnh Lâm Sàng (Khuôn 501 - 550) cho MediTrace Sentinel V2.

Bộ 50 khuôn bệnh bổ sung:
- Nguồn: DANH_SACH_UNG_VIEN_CON_LAI[200:250]
- Hệ cơ quan: da liễu, miễn dịch - dị ứng, tim mạch, tiêu hoá, thần kinh, mắt, huyết học
- Đảm bảo 100% 6 biến thể khám, chẩn đoán, kế hoạch
- 0 cặp trùng lặp triệu chứng >= 20%
"""
from typing import Dict, List, Any

GIOI_TINH_LO_7: Dict[str, str] = {json.dumps(GIOI_TINH_LO_7, ensure_ascii=False, indent=4)}

BENH_LO_7: List[Dict[str, Any]] = {pprint.pformat(ALL_50, width=100, compact=False, sort_dicts=True)}
'''

with open("src/bo_du_lieu/khuon_lo_7.py", "w", encoding="utf-8") as f:
    f.write(content)

print(f"✓ Đã ghi thành công src/bo_du_lieu/khuon_lo_7.py ({len(ALL_50)} khuôn)!")
