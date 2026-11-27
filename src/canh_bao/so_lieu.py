# -*- coding: utf-8 -*-
"""[Lớp cảnh báo]
Làm gì   : Tách con số kèm đơn vị trong câu tiếng Việt để so số ghi trong bản nháp với số
           được nói.
Vào → Ra : câu tiếng Việt → danh sách SoLieu (giá trị, đơn vị); đổi cơ sở đơn vị khi so
Đọc từ   : tach() rút các số kèm đơn vị; class SoLieu một số đo
Mục lục (các hàm/lớp chính):
  tach()        Tách các con số kèm đơn vị khỏi một câu
  class SoLieu  Một số kèm đơn vị tách từ câu
  doi_co_so()   Đổi giá trị về đơn vị cơ sở của cùng họ
Dùng bởi : canh_bao/asr, canh_bao/bo_sot, canh_bao/phat_hien, canh_bao/toan_ca
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Tách CON SỐ KÈM ĐƠN VỊ ra khỏi một câu tiếng Việt — để so bản ghi với lời nói.

Chỉ lấy số CÓ đơn vị đi kèm ("500 mg", "hai ngày", "38 độ 5", "ngày 2 lần"). Số
trần ("lần 2", "phòng 3") không mang nghĩa lâm sàng để đối chiếu, bỏ qua.

Nhưng chỗ dễ sai, đều có phép kiểm trong tests/test_canh_bao_so_lieu.py:
  - "năm" vừa là số 5 vừa là đơn vị năm: chỉ là SỐ khi đứng trước một đơn vị
  - "mười lăm" = 15, "hai mươi lăm" = 25, "một trăm" = 100, "nửa" = 0,5
  - "38 độ 5", "38 độ rưỡi" = 38,5; "0,5 mg" dấu phẩy là dấu thập phân
  - khoảng: "3-4 ngày", "3 đến 4 ngày", "ba bốn ngày" -> (3, 4)
  - ước chừng: "khoảng", "tầm", "chừng", "gần", "hơn", "có" đứng trước
"""
import re
import unicodedata
from dataclasses import dataclass
from typing import List, Optional

SO_CHU = {"một": 1, "mốt": 1, "hai": 2, "ba": 3, "bốn": 4, "tư": 4, "năm": 5, "lăm": 5,
          "sáu": 6, "bảy": 7, "bẩy": 7, "tám": 8, "chín": 9, "mười": 10, "nửa": 0.5}

# đơn vị -> (họ, đơn vị chuẩn, hệ số đổi về đơn vị cơ sở của họ)
DON_VI = {
    "mg": ("lieu", "mg", 1), "miligam": ("lieu", "mg", 1), "g": ("lieu", "g", 1000),
    "gam": ("lieu", "g", 1000), "gram": ("lieu", "g", 1000), "mcg": ("lieu", "mcg", 0.001),
    "µg": ("lieu", "mcg", 0.001), "ml": ("lieu", "ml", 1), "viên": ("lieu", "viên", 1),
    "gói": ("lieu", "gói", 1), "ống": ("lieu", "ống", 1), "nhát": ("lieu", "nhát", 1),
    "giọt": ("lieu", "giọt", 1), "đơn vị": ("lieu", "đơn vị", 1), "ui": ("lieu", "đơn vị", 1),
    "lần": ("so_lan", "lần", 1),
    "giây": ("thoi_gian", "giây", 1 / 86400), "phút": ("thoi_gian", "phút", 1 / 1440),
    "giờ": ("thoi_gian", "giờ", 1 / 24), "tiếng": ("thoi_gian", "giờ", 1 / 24),
    "ngày": ("thoi_gian", "ngày", 1), "hôm": ("thoi_gian", "ngày", 1), "đêm": ("thoi_gian", "ngày", 1),
    "tuần": ("thoi_gian", "tuần", 7), "tháng": ("thoi_gian", "tháng", 30), "năm": ("thoi_gian", "năm", 365),
    "độ": ("nhiet_do", "độ", 1), "°c": ("nhiet_do", "độ", 1), "°": ("nhiet_do", "độ", 1),
    "kg": ("can_nang", "kg", 1), "ký": ("can_nang", "kg", 1), "cân": ("can_nang", "kg", 1),
    "lạng": ("can_nang", "lạng", 0.1), "cm": ("chieu_cao", "cm", 1), "mét": ("chieu_cao", "m", 100),
    "tuổi": ("tuoi", "tuổi", 1), "%": ("phan_tram", "%", 1), "mmhg": ("huyet_ap", "mmhg", 1),
    "/10": ("thang_diem", "/10", 1),
}
_DV_SAP = sorted(DON_VI, key=len, reverse=True)
# Từ ước chừng trong 4 từ đứng trước số: "hình như giảm 5 kg" có động từ chen giữa.
UOC_CHUNG = re.compile(r"(?<!\w)(khoảng|tầm|chừng|gần|hơn|cỡ|ngót|xấp xỉ|độ chừng|áng chừng|hình như)(?!\w)")


# ═══ class SoLieu — Một số kèm đơn vị tách từ câu ═════════════════════════════════════
# Có giá trị, họ đơn vị, cận trên nếu là khoảng, cờ ước chừng và đoạn gốc.
@dataclass
class SoLieu:
    gia_tri: float
    ho: str                 # liều | so_lan | thoi_gian | nhiet_do | ...
    don_vi: str             # đơn vị chuẩn
    tren: Optional[float] = None    # dấu trên của khoảng, nếu là khoảng
    uoc: bool = False
    chu: str = ""           # đoạn gốc, để hiện cho bác sĩ

    @property
    def la_khoang(self):
        return self.tren is not None

    def chua(self, v):
        return self.gia_tri <= v <= self.tren if self.la_khoang else abs(self.gia_tri - v) < 1e-9


# ─── _nfc() — Chuẩn hoá Unicode NFC và chữ thường ─────────────────────────────────────
def _nfc(s):
    return unicodedata.normalize("NFC", str(s or "")).lower()


# ─── _chuan_bi() — Chuẩn bị chuỗi trước khi tách số ───────────────────────────────────
# Tách số khỏi đơn vị, đổi dấu phẩy thập phân thành chấm.
def _chuan_bi(van):
    t = _nfc(van)
    t = re.sub(r"(\d)([a-zµ%°])", r"\1 \2", t)            # 500mg -> 500 mg
    t = re.sub(r"(\d)\s*/\s*10(?!\d)", r"\1 /10", t)        # 7/10 -> 7 /10
    t = re.sub(r"(\d+)\s*,\s*(\d+)(?=\s*[a-zµ%°đ])", r"\1.\2", t)   # 0,5 mg -> 0.5
    return t


# ─── _doc_so() — Đọc một số bằng chữ số hoặc chữ tiếng Việt ───────────────────────────
# Hiểu mười lăm, hai mươi lăm, một trăm; trả về (giá trị, số từ đã đọc).
def _doc_so(tu: List[str], i: int):
    """Đọc một số bắt đầu ở tu[i] -> (giá trị, số từ đã đọc) hoặc (None, 0)."""
    if i >= len(tu):
        return None, 0
    w = tu[i]
    if re.fullmatch(r"\d+(\.\d+)?", w):
        return float(w), 1
    if w not in SO_CHU:
        return None, 0
    # mười | X mười | X trăm — ghép tối đa 4 từ
    gia, j = 0.0, i
    if w == "nửa":
        return 0.5, 1
    if w == "mười":
        gia, j = 10, i + 1
    else:
        gia, j = SO_CHU[w], i + 1
        if j < len(tu) and tu[j] in ("mươi", "chục"):
            gia, j = gia * 10, j + 1
        elif j < len(tu) and tu[j] == "trăm":
            gia, j = gia * 100, j + 1
            if j < len(tu) and tu[j] == "linh":
                j += 1
    if gia >= 10 and j < len(tu) and tu[j] in SO_CHU and tu[j] not in ("mười", "nửa") \
            and SO_CHU[tu[j]] < 10:
        # "mười lăm", "hai mươi mốt" — nhưng chỉ khi từ sau KHÔNG là số tiếp theo
        # của một khoảng ("mười hai mươi ngày" không có trong lời nói)
        gia, j = gia + SO_CHU[tu[j]], j + 1
    return gia, j - i


# ─── _doc_don_vi() — Nhận biết đơn vị đo bắt đầu tại một vị trí ───────────────────────
# Thử đơn vị dài trước.
def _doc_don_vi(tu: List[str], j: int):
    for dv in _DV_SAP:
        phan = dv.split()
        if tu[j:j + len(phan)] == phan:
            return dv, len(phan)
    return None, 0


# ═══ tach() — Tách các con số kèm đơn vị khỏi một câu ═════════════════════════════════
# Hiểu khoảng, ước chừng, 38 độ 5, rưỡi; số trần không đơn vị bị bỏ qua.
def tach(van: str) -> List[SoLieu]:
    t = _chuan_bi(van)
    tu = re.findall(r"\d+(?:\.\d+)?|/10|°c|°|[\wµ%]+", t)
    ra, i = [], 0
    while i < len(tu):
        v, n = _doc_so(tu, i)
        if v is None:
            i += 1
            continue
        j = i + n
        tren = None
        # khoảng: "3 - 4", "3 đến 4", "ba bốn", "2 hay 3"
        if j < len(tu) and tu[j] in ("đến", "tới", "hay", "hoặc"):
            v2, n2 = _doc_so(tu, j + 1)
            if v2 is not None and v2 > v:
                tren, j = v2, j + 1 + n2
        elif j < len(tu):
            v2, n2 = _doc_so(tu, j)
            if v2 is not None and v2 == v + 1 and v < 10:
                tren, j = v2, j + n2
        dv, m = _doc_don_vi(tu, j) if j < len(tu) else (None, 0)
        if dv is None:
            # "3-4 ngày": dấu gạch bị bỏ khi tách từ — số tiếp theo liền sau
            i += n
            continue
        ho, chuan, _he = DON_VI[dv]
        k = j + m
        # "38 độ 5", "38 độ rưỡi"
        if ho == "nhiet_do" and k < len(tu):
            if tu[k] == "rưỡi":
                v, k = v + 0.5, k + 1
            elif re.fullmatch(r"\d", tu[k]) or (tu[k] in SO_CHU and SO_CHU[tu[k]] < 10 and tu[k] != "nửa"):
                v, k = v + (float(tu[k]) if tu[k].isdigit() else SO_CHU[tu[k]]) / 10, k + 1
        # "một ngày rưỡi"
        if k < len(tu) and tu[k] == "rưỡi":
            v, k = v + 0.5, k + 1
        truoc = " ".join(tu[max(0, i - 4):i])
        ra.append(SoLieu(v, ho, chuan, tren, bool(UOC_CHUNG.search(truoc)),
                         " ".join(tu[i:k])))
        i = k
    # "3-4 ngày" viết bằng số: gộp cặp (số không đơn vị, số có đơn vị) cách nhau dấu gạch
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)\s*([a-zđôơưăâêà-ỹ°%/]+)", t):
        a, b = float(m.group(1)), float(m.group(2))
        for s in ra:
            if abs(s.gia_tri - b) < 1e-9 and s.tren is None and a < b:
                s.gia_tri, s.tren = a, b
                break
    return ra


# ═══ doi_co_so() — Đổi giá trị về đơn vị cơ sở của cùng họ ════════════════════════════
def doi_co_so(s: SoLieu, v: float) -> float:
    for dv, (ho, chuan, he) in DON_VI.items():
        if chuan == s.don_vi and ho == s.ho:
            return v * he
    return v
