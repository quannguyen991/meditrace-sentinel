# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Khuôn bệnh]
Làm gì   : Giữ một danh sách khuôn bệnh duy nhất để bộ sinh, bước chia tập và bộ lọc giới
           tính cùng nhìn, không lệch nhau.
Vào → Ra : cờ mo_rong → tuple khuôn bệnh đúng thứ tự; tập khuôn chỉ nữ / chỉ nam; bảng khuôn
           → đợt
Đọc từ   : ds_khuon() trả danh sách khuôn dùng chung (thứ tự quyết định tập);
           dot_cua_khuon() cho biết khuôn thuộc đợt nào
Mục lục (các hàm/lớp chính):
  ds_khuon()        Trả danh sách khuôn bệnh, có thể mở rộng
  chi_nu()          Lấy tập khuôn bệnh chỉ gặp ở nữ
  chi_nam()         Lấy tập khuôn bệnh chỉ gặp ở nam
  dot_cua_khuon()   Cho biết mỗi khuôn ngoài bản gốc thuộc đợt nào
  thanh_vien_dot()  Gom tên khuôn theo từng đợt
Gọi tới  : bo_du_lieu/khuon_mo_rong, bo_du_lieu/ngu_lieu_viet
Dùng bởi : audio/asr/contextual_trie_600, bo_du_lieu/chia_tap_theo_khuon,
           bo_du_lieu/sinh_hoi_thoai_viet
Tên cũ   : kho_khuon.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
KHO KHUÔN dùng chung: bộ sinh, bước chia tập và lọc giới tính phải nhìn CÙNG MỘT danh sách.

VÌ SAO CẦN (23/11/2026). Trước đó `mo_rong=True` có ba chỗ dùng ba danh sách khác nhau:
  - `sinh_ca` chọn khuôn từ `nl.BENH` (270 khuôn);
  - `bang_tap_khuon` dùng `BENH_GOC` + `khuon_mo_rong.BENH_MO_RONG` (600 khuôn);
  - `tach_tap_viet.phan_khuon` đánh chỉ số theo `nl.BENH`.
Khuôn ngoài `nl.BENH` không có chỉ số nên rơi vào nhóm của khuôn 101-200 và làm 12 khuôn
cũ đổi tập (rò rỉ), còn khuôn trong `nl.BENH` mà không có trong `BENH_MO_RONG` thì tra cứu
bảng tập thất bại. Kho này là nguồn duy nhất.

THỨ TỰ (quan trọng, vì `phan_khuon` chia đợt theo CHỈ SỐ):
  1. 200 khuôn gốc (`nl.BENH_GOC`), không đổi;
  2. 70 khuôn mới của `nl.BENH` (chỉ số 200-269), đã được bộ sinh dùng;
  3. các khuôn của `khuon_mo_rong.BENH_MO_RONG` chưa có ở bước 1, 2 (giữ thứ tự đó).
Khuôn có ở cả `nl.BENH` và `BENH_MO_RONG` (13 khuôn trùng tên) giữ NỘI DUNG của `nl.BENH` (đã
dùng trong bộ sinh) và lấy thêm các trường `bien_the_*` của bản mở rộng. Chỉ thêm, không
đổi mã chữ cũ.

`mo_rong=False` trả đúng 200 khuôn gốc: hành vi cũ giữ nguyên từng bit.
"""
from __future__ import annotations

from functools import lru_cache

from src.bo_du_lieu import ngu_lieu_viet as nl


# ─── _goc() — Lấy danh sách khuôn bệnh gốc ────────────────────────────────────────────
# Dùng BENH_GOC nếu có, không thì 200 khuôn đầu của kho.
def _goc() -> list:
    return list(getattr(nl, "BENH_GOC", nl.BENH[:200]))


# ═══ ds_khuon() — Trả danh sách khuôn bệnh, có thể mở rộng ════════════════════════════
# Mặc định chỉ khuôn gốc; mở rộng thì ghép thêm khuôn mở rộng. Không sửa dict trả về.
@lru_cache(maxsize=2)
def ds_khuon(mo_rong: bool = False) -> tuple:
    """-> tuple các dict khuôn. Không sửa các dict trả về."""
    goc = _goc()
    if not mo_rong:
        return tuple(goc)
    ten_goc = {b["ten"] for b in goc}
    try:
        from src.bo_du_lieu import khuon_mo_rong as kmr
    except ImportError:
        return tuple(nl.BENH)
    theo_ten = {b["ten"]: b for b in kmr.BENH_MO_RONG}
    ra, da = [], set()
    for b in nl.BENH:
        ten = b["ten"]
        if ten in da:
            continue
        da.add(ten)
        mr = theo_ten.get(ten)
        if mr is not None and ten not in ten_goc:
            b = {**b, **{k: v for k, v in mr.items() if k.startswith("bien_the_")}}
        ra.append(b)
    for b in kmr.BENH_MO_RONG:
        if b["ten"] not in da:
            da.add(b["ten"])
            ra.append(b)
    return tuple(ra)


# ═══ chi_nu() — Lấy tập khuôn bệnh chỉ gặp ở nữ ═══════════════════════════════════════
# Gồm khuôn gốc và khuôn mở rộng.
@lru_cache(maxsize=1)
def chi_nu() -> frozenset:
    """Khuôn chỉ ở nữ: tập gốc + tập của khuôn mở rộng (tên không trùng khuôn gốc)."""
    try:
        from src.bo_du_lieu import khuon_mo_rong as kmr
        return frozenset(nl.CHI_NU) | frozenset(kmr.CHI_NU_MO_RONG)
    except ImportError:
        return frozenset(nl.CHI_NU)


# ═══ chi_nam() — Lấy tập khuôn bệnh chỉ gặp ở nam ═════════════════════════════════════
# Gồm khuôn gốc và khuôn mở rộng.
@lru_cache(maxsize=1)
def chi_nam() -> frozenset:
    try:
        from src.bo_du_lieu import khuon_mo_rong as kmr
        return frozenset(nl.CHI_NAM) | frozenset(kmr.CHI_NAM_MO_RONG)
    except ImportError:
        return frozenset(nl.CHI_NAM)


# ═══ dot_cua_khuon() — Cho biết mỗi khuôn ngoài bản gốc thuộc đợt nào ═════════════════
# Đợt 1 và 2 theo bảng khuôn mở rộng; đợt 0 là phần còn lại.
@lru_cache(maxsize=1)
def dot_cua_khuon() -> dict:
    """{tên khuôn: số đợt} cho MỌI khuôn ngoài 200 khuôn gốc.

    Đợt 1 và 2 là hai đợt 200 khuôn của `khuon_mo_rong.TEN_THEO_DOT`; đợt 0 là phần còn lại
    (các khuôn của `nl.BENH` ở vị trí 200-269 chưa nằm trong đợt nào). Khuôn gốc không có
    trong bảng này.
    """
    ten_goc = {b["ten"] for b in _goc()}
    try:
        from src.bo_du_lieu import khuon_mo_rong as kmr
        theo_dot = dict(getattr(kmr, "TEN_THEO_DOT", {}))
    except ImportError:
        theo_dot = {}
    ra = {}
    for b in ds_khuon(True):
        t = b["ten"]
        if t in ten_goc:
            continue
        ra[t] = next((d for d, tap_ten in theo_dot.items() if t in tap_ten), 0)
    return ra


# ═══ thanh_vien_dot() — Gom tên khuôn theo từng đợt ═══════════════════════════════════
# Trả số đợt kèm tuple tên khuôn đã sắp xếp.
@lru_cache(maxsize=1)
def thanh_vien_dot() -> dict:
    """{số đợt: tuple tên khuôn đã sắp xếp} của kho đầy đủ."""
    nhom: dict = {}
    for t, d in dot_cua_khuon().items():
        nhom.setdefault(d, []).append(t)
    return {d: tuple(sorted(v)) for d, v in nhom.items()}
