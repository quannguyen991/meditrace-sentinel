# -*- coding: utf-8 -*-
"""[Công cụ lâm sàng hỗ trợ bác sĩ › Tri thức]
Làm gì   : Đọc bảng tri thức thuốc dùng chung (tên, hoạt chất, liều tối đa) từ tệp dữ liệu;
           bảng này chưa được chuyên gia duyệt.
Vào → Ra : tên thuốc hoặc hoạt chất → hoạt chất, các tên gọi, liều tối đa người lớn và trẻ
           em
Đọc từ   : hoat_chat() đổi tên thuốc về hoạt chất; lieu_toi_da() tra liều tối đa theo đối
           tượng
Mục lục (các hàm/lớp chính):
  hoat_chat()        Đổi biệt dược hoặc tên khác về hoạt chất
  lieu_toi_da()      Tra liều tối đa của thuốc cho người lớn hoặc trẻ em
  la_nti()           Kiểm tra thuốc có khoảng điều trị hẹp (NTI)
  regex_ten_thuoc()  Mẫu regex nhận diện mọi tên thuốc trong văn bản
  tat_ca()           Trả toàn bộ mục thuốc trong tri thức
  ten_cua()          Liệt kê các tên gọi của một hoạt chất
  ten_nti()          Tập hoạt chất thuốc khoảng điều trị hẹp
Dùng bởi : audio/asr/contextual_trie_600, canh_bao/bo_sot, canh_bao/lam_sang,
           cong_cu_lam_sang/canh_bao_tuong_tac_thuoc, cong_cu_lam_sang/di_buong_noi_tru,
           cong_cu_lam_sang/di_ung_cheo, cong_cu_lam_sang/hieu_chinh_lieu,
           cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot … (tổng 14 tệp)
Tên cũ   : tri_thuc_thuoc.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Tri thức thuốc — MỘT nguồn cho cả hệ thống (25/11/2026).

Trước ngày này liều tối đa paracetamol 4000 mg nằm ở ít nhất 3 nơi (`guardrails`,
`duoc_ly_lam_sang`, `aho_corasick_duoc_thu`), liều trẻ em ở `kiem_duyet_bhyt_va_bo_sot`,
danh sách thuốc khoảng điều trị hẹp ở `cong_rui_ro`, từ điển tên thuốc ở `thuc_the` — mỗi
nơi một danh sách, có chỗ trái nhau (omeprazole 40 hay 80 mg/ngày), và hầu hết không ghi
nguồn. Giờ tất cả đọc từ `data/tri_thuc_thuoc.json`.

MỖI MỤC có `nguon` (chép từ đâu, có số trang hay không) và `da_duyet`. Mục `da_duyet=false`
chỉ được sinh cảnh báo mức "cần xem", không bao giờ chặn. KHÔNG ai tự đặt `da_duyet=true`
trừ người có chuyên môn đã tra lại nguồn — xem docs/tri-thuc-thuoc-can-duyet.md.
"""
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Literal, Optional, Tuple

TEP = Path(__file__).resolve().parents[2] / "data" / "tri_thuc_thuoc.json"


# ═══ class LieuToiDa — Liều tối đa kèm nguồn và cờ đã duyệt ═══════════════════════════
# Gồm giá trị, đơn vị, nguồn, da_duyet, liều mỗi lần và ghi chú.
@dataclass(frozen=True)
class LieuToiDa:
    gia_tri: float
    don_vi: str
    nguon: str
    da_duyet: bool
    moi_lan: Optional[float] = None
    ghi_chu: str = ""


# ─── _khoa() — Khoá so khớp tên thuốc: chữ thường, bỏ e cuối ──────────────────────────
def _khoa(ten: str) -> str:
    """Khoá so khớp: viết thường, bỏ 'e' cuối (omeprazol = omeprazole, cefixim = cefixime)."""
    t = re.sub(r"\s+", " ", (ten or "").strip().lower())
    return t[:-1] if len(t) > 5 and t.endswith("e") else t


# ─── _du_lieu() — Đọc tệp tri thức thuốc JSON ─────────────────────────────────────────
# Chưa chuyên gia duyệt.
@lru_cache(maxsize=1)
def _du_lieu() -> dict:
    return json.loads(TEP.read_text(encoding="utf-8"))


# ═══ tat_ca() — Trả toàn bộ mục thuốc trong tri thức ══════════════════════════════════
def tat_ca() -> List[dict]:
    return list(_du_lieu()["muc"])


# ─── _bang_ten() — Lập bảng từ mọi tên thuốc sang hoạt chất ───────────────────────────
# Gồm hoạt chất, tên khác và biệt dược.
@lru_cache(maxsize=1)
def _bang_ten() -> Dict[str, str]:
    """{khoá tên: hoạt chất} cho hoạt chất, tên khác và biệt dược."""
    ra = {}
    for m in tat_ca():
        for t in [m["hoat_chat"], *m.get("ten_khac", []), *m.get("biet_duoc", [])]:
            ra.setdefault(_khoa(t), m["hoat_chat"])
    return ra


# ─── _theo_hoat_chat() — Lập bảng tra mục thuốc theo hoạt chất ────────────────────────
@lru_cache(maxsize=1)
def _theo_hoat_chat() -> Dict[str, dict]:
    return {m["hoat_chat"]: m for m in tat_ca()}


# ═══ tat_ca_ten() — Liệt kê mọi tên thuốc, tên dài xếp trước ══════════════════════════
def tat_ca_ten() -> List[str]:
    """Mọi tên (hoạt chất, tên khác, biệt dược), viết thường, dài trước."""
    ten = {t.lower() for m in tat_ca() for t in [m["hoat_chat"], *m.get("ten_khac", []), *m.get("biet_duoc", [])]}
    return sorted(ten, key=lambda t: (-len(t), t))


# ═══ ten_cua() — Liệt kê các tên gọi của một hoạt chất ════════════════════════════════
# Gồm hoạt chất, tên khác và biệt dược, viết thường.
def ten_cua(hc: str) -> List[str]:
    m = _theo_hoat_chat().get(hoat_chat(hc) or "")
    return [] if m is None else [t.lower() for t in [m["hoat_chat"], *m.get("ten_khac", []), *m.get("biet_duoc", [])]]


# ═══ regex_ten_thuoc() — Mẫu regex nhận diện mọi tên thuốc trong văn bản ══════════════
# Chịu được chữ có dấu và chữ e cuối tuỳ chọn; lưu bộ nhớ đệm.
@lru_cache(maxsize=1)
def regex_ten_thuoc() -> "re.Pattern":
    # Mẫu cho mỗi tên (có hoặc không 'e' cuối), ranh giới chữ chịu được chữ có dấu.
    phan = sorted({re.escape(t[:-1]) + "e?" if len(t) > 5 and t.endswith("e") else re.escape(t) + "e?"
                   for t in tat_ca_ten()}, key=lambda s: -len(s))
    return re.compile(r"(?i)(?<![\w-])(" + "|".join(phan) + r")(?![\w-])")


# ═══ hoat_chat() — Đổi biệt dược hoặc tên khác về hoạt chất ═══════════════════════════
# Chuỗi dài lấy tên dài nhất tìm thấy; không biết thì trả None.
def hoat_chat(ten: str) -> Optional[str]:
    """Biệt dược / tên khác / hoạt chất -> hoạt chất. Chuỗi dài ("panadol extra") -> tên dài
    nhất tìm thấy trong chuỗi. None khi không biết."""
    k = _khoa(ten)
    if k in _bang_ten():
        return _bang_ten()[k]
    tim = [m.group(1) for m in regex_ten_thuoc().finditer(ten or "")]
    if not tim:
        return None
    return _bang_ten().get(_khoa(max(tim, key=len)))


# ═══ la_nti() — Kiểm tra thuốc có khoảng điều trị hẹp (NTI) ═══════════════════════════
# Dựa vào cờ nti trong tri thức thuốc.
def la_nti(hc: str) -> bool:
    m = _theo_hoat_chat().get(hoat_chat(hc) or "")
    return bool(m and m.get("nti"))


# ═══ lieu_toi_da() — Tra liều tối đa của thuốc cho người lớn hoặc trẻ em ══════════════
# Trả LieuToiDa hoặc None; kèm cờ nguồn và da_duyet.
def lieu_toi_da(hc: str, doi_tuong: Literal["nguoi_lon", "tre_em"]) -> Optional[LieuToiDa]:
    m = _theo_hoat_chat().get(hoat_chat(hc) or "")
    l = ((m or {}).get("lieu_toi_da") or {}).get(doi_tuong)
    if not l:
        return None
    return LieuToiDa(gia_tri=float(l["gia_tri"]), don_vi=l["don_vi"], nguon=m["nguon"], da_duyet=m["da_duyet"],
                     moi_lan=l.get("moi_lan"), ghi_chu=l.get("ghi_chu", ""))


# ---- bảng dẫn xuất cho các mô-đun cũ (giữ giao diện cũ, đọc từ cùng một nguồn) ----

# ═══ bang_lieu_nguoi_lon() — Bảng liều tối đa người lớn (mg mỗi ngày) theo tên ════════
# Dẫn xuất từ tri thức thuốc cho các mô-đun cũ.
def bang_lieu_nguoi_lon() -> Dict[str, float]:
    """{mọi tên: mg/ngày} — thay `guardrails.LIEU_TRAN`, `duoc_ly_lam_sang.LIEU_TOI_DA_NGAY`."""
    ra = {}
    for m in tat_ca():
        l = (m.get("lieu_toi_da") or {}).get("nguoi_lon")
        if l:
            for t in ten_cua(m["hoat_chat"]):
                ra[t] = float(l["gia_tri"])
    return ra


# ═══ bang_lieu_tre_em() — Bảng liều tối đa trẻ em (mg mỗi kg) theo tên ════════════════
# Mỗi tên ứng với bộ ba: mỗi lần, mỗi ngày, ghi chú.
def bang_lieu_tre_em() -> Dict[str, Tuple[float, float, str]]:
    """{mọi tên: (mg/kg/lần, mg/kg/ngày, ghi chú)} — thay `LIEU_TRAN_NHI_KHOA_MG_KG_NGAY`."""
    ra = {}
    for m in tat_ca():
        l = (m.get("lieu_toi_da") or {}).get("tre_em")
        if l:
            for t in ten_cua(m["hoat_chat"]):
                ra[t] = (float(l.get("moi_lan") or l["gia_tri"]), float(l["gia_tri"]), l.get("ghi_chu", ""))
    return ra


# ═══ ten_nti() — Tập hoạt chất thuốc khoảng điều trị hẹp ══════════════════════════════
# Lấy từ cờ nti, cộng thêm sintrom.
def ten_nti() -> set:
    """Tên HOẠT CHẤT của thuốc khoảng điều trị hẹp — thay `cong_rui_ro.THUOC_KHOANG_DIEU_TRI_HEP`.
    Chỉ hoạt chất (cộng "sintrom", có sẵn trong bảng cũ): mở rộng sang biệt dược (coumadin,
    tegretol...) đổi mức nguy cơ của chính sách C từ dữ liệu chưa duyệt (rà soát 25/11)."""
    return {m["hoat_chat"] for m in tat_ca() if m.get("nti")} | {"sintrom"}
