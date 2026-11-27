"""[Âm thanh › Chép lời]
Làm gì   : Đo chất lượng chép lời bằng tỷ lệ sai từ và tỷ lệ sai từ khoá lâm sàng để so các
           bộ chép.
Vào → Ra : câu chuẩn + câu bộ chép đưa ra → WER, tỷ lệ sai từ khoá lâm sàng, bảng tổng hợp
Đọc từ   : wer() tính tỷ lệ sai từ; sai_tu_khoa() đếm lỗi ở từ lâm sàng
Mục lục (các hàm/lớp chính):
  wer()          Tính WER trên danh sách câu chuẩn và câu nhận dạng
  sai_tu_khoa()  So từ khoá lâm sàng quan trọng giữa hai câu
  tong_hop()     Tổng hợp WER và lỗi từ khoá cho cả bộ câu
Gọi tới  : audio/asr/critical_tokens
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Thước đo cho benchmark ASR: WER và tỷ lệ sai từ khoá lâm sàng.

Cả bản chép chuẩn và bản nhận dạng đều qua cùng một bước chuẩn hoá trước khi đo:
chữ thường, bỏ dấu câu, "mi li gam" -> "mg", số đọc bằng chữ -> chữ số. Bước này chỉ
dùng để ĐO; nó không bao giờ sửa bản chép đưa vào MediTrace.
"""
from __future__ import annotations

from typing import Any

from . import critical_tokens as ct

LOAI = ("thuoc", "lieu", "tan_suat", "thoi_gian", "phu_dinh", "trang_thai", "nguoi", "muc_do_dau")


# ═══ chuan_hoa_do() — Chuẩn hoá chữ trước khi đo lỗi chép lời ═════════════════════════
# Chữ thường, bỏ dấu câu, mi li gam thành mg, số đọc bằng chữ thành chữ số. Chỉ để đo,
# không sửa bản chép.
def chuan_hoa_do(text: str) -> list[str]:
    w = ct.chuan_hoa(text).split()
    ra, i = [], 0
    while i < len(w):
        s = ct._doc_so(w, i)
        if s and s[1] > i:
            ra.append(str(s[0]))
            i = s[1]
        else:
            ra.append(w[i])
            i += 1
    return ra


# ═══ khoang_cach_tu() — Tính khoảng cách chỉnh sửa giữa hai chuỗi từ ══════════════════
def khoang_cach_tu(a: list[str], b: list[str]) -> int:
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[len(b)]


# ═══ wer() — Tính WER trên danh sách câu chuẩn và câu nhận dạng ═══════════════════════
# Cộng số từ sai trên tổng số từ của câu chuẩn sau khi chuẩn hoá.
def wer(refs: list[str], hyps: list[str]) -> float:
    loi = tong = 0
    for r, h in zip(refs, hyps):
        rr = chuan_hoa_do(r)
        loi += khoang_cach_tu(rr, chuan_hoa_do(h))
        tong += len(rr)
    return loi / max(tong, 1)


# ═══ sai_tu_khoa() — So từ khoá lâm sàng quan trọng giữa hai câu ══════════════════════
# Mỗi loại trả dung, sai, them hoặc None (cả hai đều không có).
def sai_tu_khoa(ref: str, hyp: str) -> dict[str, Any]:
    """-> {loai: 'dung'|'sai'|'them'|None}. None = cả hai đều không có loại đó."""
    a, b = ct.trich(ref), ct.trich(hyp)
    ra = {}
    for k in LOAI:
        if not a[k] and not b[k]:
            ra[k] = None
        elif not a[k]:
            ra[k] = "them"
        else:
            ra[k] = "dung" if a[k] == b[k] else "sai"
    return ra


# ═══ tong_hop() — Tổng hợp WER và lỗi từ khoá cho cả bộ câu ═══════════════════════════
# Trả WER, tỷ lệ câu sai từ khoá, lỗi theo loại và kết quả các cặp câu tối thiểu.
def tong_hop(muc: list[dict], hyps: dict[str, str]) -> dict[str, Any]:
    """muc: [{id, van_ban, cap?}], hyps: {id: chữ nhận dạng}."""
    refs = [m["van_ban"] for m in muc]
    hs = [hyps.get(m["id"], "") for m in muc]
    theo_loai = {k: {"co": 0, "sai": 0, "them": 0} for k in LOAI}
    cau_sai = 0
    chi_tiet = {}
    for m, h in zip(muc, hs):
        s = sai_tu_khoa(m["van_ban"], h)
        chi_tiet[m["id"]] = s
        if any(v in ("sai", "them") for v in s.values()):
            cau_sai += 1
        for k, v in s.items():
            if v in ("dung", "sai"):
                theo_loai[k]["co"] += 1
            if v in ("sai", "them"):
                theo_loai[k][v] += 1
    cap: dict[str, list[str]] = {}
    for m in muc:
        if m.get("cap"):
            cap.setdefault(m["cap"], []).append(m["id"])
    # Một cặp đạt khi LOẠI THÔNG TIN PHÂN BIỆT hai câu (vd liều 5 mg / 50 mg) đúng ở cả hai
    # câu. Lỗi ở loại khác (vd tên thuốc) không làm trượt cặp; nó đã được đếm ở theo_loai.
    van = {m["id"]: m["van_ban"] for m in muc}
    cap_dat = []
    for c, ids in cap.items():
        phan_biet = ct.khac_nhau(ct.trich(van[ids[0]]), ct.trich(van[ids[1]]))
        if all(chi_tiet[i][k] in ("dung", None) for i in ids for k in phan_biet):
            cap_dat.append(c)
    return {
        "so_cau": len(muc),
        "wer": wer(refs, hs),
        "ty_le_cau_sai_tu_khoa": cau_sai / max(len(muc), 1),
        "theo_loai": {k: {**v, "ty_le_sai": (v["sai"] / v["co"]) if v["co"] else None}
                      for k, v in theo_loai.items()},
        "cap_toi_thieu": {"tong": len(cap), "phan_biet_dung": len(cap_dat),
                          "truot": sorted(set(cap) - set(cap_dat))},
        "chi_tiet": chi_tiet,
    }
