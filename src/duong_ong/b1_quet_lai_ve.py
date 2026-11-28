# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 1 – Rút mệnh đề › Quét lại]
Làm gì   : Tìm các VẾ của hội thoại có tín hiệu lâm sàng mà chưa câu trích nào phủ, dựng lời
           nhắc để hỏi lại mô hình đúng các vế đó, rồi gộp mệnh đề mới vào bảng.
Vào → Ra : hội thoại + bảng mệnh đề của lượt trích đầu → danh sách vế chưa phủ; lời nhắc quét
           lại; bảng mệnh đề đã gộp (mệnh đề mới gắn "nguon": "quet_lai")
Đọc từ   : ve_chua_phu() là lối vào; chay_duong_ong.chay_trung_gian(quet_lai=True) gọi cả ba hàm
Mục lục (các hàm/lớp chính):
  ve_chua_phu()           Vế có tín hiệu lâm sàng mà không câu trích nào phủ
  cac_ve()                Mọi vế của hội thoại kèm tín hiệu và cờ đã phủ (dùng để đo)
  loi_nhac_quet_lai()     Lời nhắc hỏi lại mô hình chỉ cho các vế chưa phủ
  loc_trong_van()         Giữ mệnh đề quét lại có câu trích nằm trong chính lượt nó dẫn
  gop_ket_qua_quet_lai()  Gộp mệnh đề mới, bỏ trùng câu trích, đổi lại quan_he_voi
Gọi tới  : duong_ong/b0_cat_doan_van, duong_ong/b4_kiem_can_cu, canh_bao/bo_sot,
           canh_bao/loi_noi, canh_bao/so_lieu, huan_luyen/chon_mo_hinh_bakeoff
Dùng bởi : duong_ong/chay_duong_ong
────────────────────────────────────────────────────────────────────────
Vì sao (Task 1, kế hoạch 27/11/2026): 172/200 mệnh đề bị sót (86%) nằm trong một lượt mà mô
hình ĐÃ dẫn cho một mệnh đề khác. Xét theo lượt thì lượt đó "đã có mệnh đề" và vế còn lại bị
che. Ở đây đơn vị là VẾ (đoạn theo dấu câu của `cac_doan`; lượt không dấu thì `tach_y`).

Vế coi là ĐÃ PHỦ khi giao với một câu trích của lượt đó VÀ mọi tên thuốc / chất dị ứng của vế
đều có trong các câu trích giao với nó. Chỉ giao thôi chưa đủ: "amlodipin 5mg với metformin
500mg" có câu trích "amlodipin 5mg" vẫn còn metformin chưa ai ghi.

Mệnh đề quét lại KHÔNG được ưu tiên gì: chúng vào cùng bảng và đi qua khoá K1–K6 như mọi mệnh
đề khác; không qua thì xuống CẦN XÁC NHẬN.
"""
import unicodedata
from typing import Dict, List, Optional, Tuple

from src.canh_bao import so_lieu
from src.canh_bao.bo_sot import (DI_UNG, PHU_DINH, THUOC_CHUNG, THUOC_DONG_Y, _chat_di_ung,
                                 _ten_thuoc, la_xa_giao)
from src.canh_bao.loi_noi import co_dau_cau, nhan_cau_hoi, tach_y
from src.canh_bao.phat_hien import _thuong
from src.duong_ong import b2_gom_nguoi_thuc_the as thuc_the
from src.duong_ong.b0_cat_doan_van import cac_doan, dau_ket
from src.duong_ong.b1_cau_truc_menh_de import la_vai_nhan_vien
from src.duong_ong.b4_kiem_can_cu import CHU_DE_HOI, _chuan_trich, tim_trich

TIN_HIEU = ("thuoc", "di_ung", "so_lieu", "phu_dinh", "trieu_chung")
_TRIEU_CHUNG = dict(CHU_DE_HOI)["trieu_chung"]


def _nfc(s) -> str:
    return unicodedata.normalize("NFC", str(s or ""))


# ─── _luot() — {số lượt: (vai, lời)} theo đúng cách đánh số của bước trích ────────────
def _luot(hoi_thoai: str) -> Dict[int, Tuple[str, str]]:
    return {so: (str(vai or "").lower(), _nfc(van)) for so, vai, van in thuc_the.tach_luot(hoi_thoai)}


# ─── _trich() / _luot_dan() — đọc câu trích và lượt dẫn của một bản ghi mô hình ───────
# Chấp nhận cả hai dạng: đầu ra mô hình (`luot_thoai`, danh sách trích) và PhatBieu.to_dict
# (`bang_chung`); câu trích là một chuỗi hay một danh sách.
def _trich(p: dict) -> List[str]:
    td = p.get("trich_dan")
    if isinstance(td, str):
        td = [td]
    if not isinstance(td, (list, tuple)):
        return []
    return [str(x) for x in td if str(x or "").strip()]


def _luot_dan(p: dict) -> List[int]:
    ra = []
    for x in (p.get("luot_thoai") or p.get("bang_chung") or []):
        try:
            ra.append(int(x))
        except (TypeError, ValueError):
            continue
    return ra


# ─── _khoang_trich() — {số lượt: [(đầu, cuối, câu trích)]} ────────────────────────────
# Tìm câu trích trong các lượt bản ghi dẫn. Bản ghi không dẫn lượt nào thì tìm khắp hội
# thoại. Dẫn sai lượt thì KHÔNG tìm sang lượt khác: K1 sẽ chặn bản ghi đó, và quét lại vế
# ấy là đúng việc.
def _khoang_trich(luot: Dict[int, Tuple[str, str]], phat_bieu: List[dict]) -> Dict[int, list]:
    ra: Dict[int, list] = {}
    for p in phat_bieu or []:
        if not isinstance(p, dict):
            continue
        dan = [s for s in _luot_dan(p) if s in luot] or list(luot)
        for t in _trich(p):
            for s in dan:
                k = tim_trich(t, luot[s][1])
                if k:
                    ra.setdefault(s, []).append((k[0], k[1], t))
    return ra


# ─── _tin_hieu() — Tín hiệu lâm sàng của một vế (tái dùng từ khoá của canh_bao) ───────
def _tin_hieu(doan: str) -> List[str]:
    t = _thuong(doan)
    co = {
        "thuoc": bool(_ten_thuoc(t) or THUOC_DONG_Y.search(t) or THUOC_CHUNG.search(t)),
        "di_ung": bool(DI_UNG.search(t)),
        "so_lieu": bool(so_lieu.tach(doan)),
        "phu_dinh": bool(PHU_DINH.search(t)),
        "trieu_chung": bool(_TRIEU_CHUNG.search(t)),
    }
    return [k for k in TIN_HIEU if co[k]]


# ─── _con_thuc_the_moi() — Vế còn tên thuốc / chất dị ứng chưa nằm trong câu trích ────
def _con_thuc_the_moi(doan: str, cac_trich: List[str]) -> bool:
    t = _thuong(doan)
    can = set(_ten_thuoc(t)) | _chat_di_ung(t)
    if not can:
        return False
    chu = " ".join(_thuong(x) for x in cac_trich)
    co = set(_ten_thuoc(chu)) | _chat_di_ung(chu) | set(chu.split())
    return any(c not in co and c not in chu for c in can)


# ═══ cac_ve() — Mọi vế của hội thoại kèm tín hiệu và cờ đã phủ ════════════════════════
# Bỏ câu hỏi (dấu "?"; lượt không dấu của nhân viên thì theo tiểu từ hỏi) và vế xã giao.
def cac_ve(hoi_thoai: str, phat_bieu: List[dict]) -> List[dict]:
    luot = _luot(hoi_thoai)
    phu = _khoang_trich(luot, phat_bieu)
    ra = []
    for so, (vai, van) in sorted(luot.items()):
        co_dau = co_dau_cau(van)
        for a, b in (cac_doan(van) if co_dau else tach_y(van)):
            doan = van[a:b]
            if dau_ket(van, (a, b)) == "?" or (
                    not co_dau and la_vai_nhan_vien(vai) and nhan_cau_hoi(doan)):
                continue
            if la_xa_giao(doan):
                continue
            giao = [q for x, y, q in phu.get(so, ()) if x < b and a < y]
            ra.append({"luot": so, "dau": a, "cuoi": b, "van": doan,
                       "tin_hieu": _tin_hieu(doan),
                       "da_phu": bool(giao) and not _con_thuc_the_moi(doan, giao)})
    return ra


# ═══ ve_chua_phu() — Vế có tín hiệu lâm sàng mà không câu trích nào phủ ═══════════════
def ve_chua_phu(hoi_thoai: str, phat_bieu: List[dict]) -> List[dict]:
    """-> [{"luot", "dau", "cuoi", "van", "tin_hieu"}]; `dau`/`cuoi` là vị trí trên lời của
    lượt (sau khi bỏ "Vai:" và chuẩn NFC)."""
    return [{k: v[k] for k in ("luot", "dau", "cuoi", "van", "tin_hieu")}
            for v in cac_ve(hoi_thoai, phat_bieu) if v["tin_hieu"] and not v["da_phu"]]


# ═══ loi_nhac_quet_lai() — Lời nhắc hỏi lại mô hình chỉ cho các vế chưa phủ ═══════════
# Giữ nguyên hướng dẫn và cách đánh số lượt của lượt trích đầu, để đầu ra cùng lược đồ và
# đọc được bằng đúng bộ phân tích cũ.
def loi_nhac_quet_lai(hoi_thoai: str, ve: List[dict]) -> str:
    from src.huan_luyen.chon_mo_hinh_bakeoff import HUONG_DAN, danh_so_luot
    danh_so, _ = danh_so_luot(hoi_thoai)
    ds = "\n".join(f"- Lượt {v['luot']}: “{v['van']}”" for v in ve)
    return (f"{HUONG_DAN}\n\n"
            "Lần đọc trước đã ghi phần còn lại của hội thoại. Các vế dưới đây CHƯA có bản ghi nào. "
            "Chỉ ghi bản ghi cho thông tin lâm sàng nằm TRONG các vế này; vế nào không có thông tin "
            "lâm sàng thì bỏ qua. luot_thoai là số lượt của vế; trich_dan chép nguyên văn từ vế đó. "
            "quan_he_voi đếm trong danh sách bạn trả về lần này.\n\n"
            f"Các vế cần đọc lại:\n{ds}\n\nHội thoại:\n{danh_so}")


# ═══ loc_trong_van() — Giữ mệnh đề có câu trích nằm trong chính lượt nó dẫn ═══════════
# Lần sinh thứ hai được hỏi về những vế cụ thể; câu trích không có trong lượt dẫn (bịa, dẫn
# sai lượt, lượt không tồn tại, không trích) là không truy được về hội thoại -> bỏ, kèm đếm.
def loc_trong_van(hoi_thoai: str, moi: List[dict]) -> Tuple[List[dict], List[dict]]:
    luot = _luot(hoi_thoai)
    giu, bo = [], []
    for p in moi or []:
        if not isinstance(p, dict):
            bo.append(p)
            continue
        dan, td = _luot_dan(p), _trich(p)
        ok = bool(dan) and bool(td) and all(s in luot for s in dan) and all(
            any(tim_trich(t, luot[s][1]) for s in dan) for t in td)
        (giu if ok else bo).append(p)
    return giu, bo


# ═══ gop_ket_qua_quet_lai() — Gộp mệnh đề quét lại vào bảng ═══════════════════════════
def gop_ket_qua_quet_lai(phat_bieu: List[dict], moi: List[dict]) -> List[dict]:
    """Nối mệnh đề mới vào sau bảng cũ, gắn "nguon": "quet_lai". Bỏ mệnh đề mới có câu trích
    trùng (sau chuẩn hoá) câu trích của mệnh đề đã có hoặc của mệnh đề mới đứng trước.

    `quan_he_voi` của mệnh đề mới đếm trong danh sách của lần quét lại, nên được đổi sang vị
    trí trong bảng đã gộp; trỏ tới mệnh đề bị bỏ thì quan hệ thành "không"."""
    ra = [p for p in (phat_bieu or [])]
    da_co = {_chuan_trich(t) for p in ra if isinstance(p, dict) for t in _trich(p)}
    vi_tri: Dict[int, int] = {}
    them: List[Tuple[int, dict]] = []
    for i, p in enumerate(moi or []):
        if not isinstance(p, dict):
            continue
        tr = {_chuan_trich(t) for t in _trich(p)} - {""}
        if tr & da_co:
            continue
        da_co |= tr
        vi_tri[i] = len(ra) + len(them)
        them.append((i, dict(p, nguon="quet_lai")))
    for _i, p in them:
        qv: Optional[int] = p.get("quan_he_voi")
        if p.get("quan_he") not in (None, "", "không") or qv is not None:
            if isinstance(qv, int) and qv in vi_tri and p.get("quan_he") not in (None, "", "không"):
                p["quan_he_voi"] = vi_tri[qv]
            else:
                p["quan_he"], p["quan_he_voi"] = "không", None
        ra.append(p)
    return ra
