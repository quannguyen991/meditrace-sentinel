# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 4 – Kiểm nội dung theo câu trích] (NGUYÊN MẪU, chưa nối vào đường ống)
Làm gì   : So `noi_dung` của một mệnh đề với CHÍNH câu trích của nó, chặt hơn K2 của
           `b4_kiem_can_cu` (K2 chỉ cảnh báo khi KHÔNG trùng từ nào).
Vào → Ra : nội dung + danh sách câu trích → danh sách mã lý do (rỗng = sạch)
Mã lý do :
  tu_khong_co_trong_trich  có chữ nội dung không nằm trong câu trích nào ("ngột mũi" / "nghẹt mũi")
  chep_loi_asr             chữ nội dung không dấu, giống âm tiết tiếng Việt bỏ dấu, chép nguyên từ
                           câu trích ("the trang beo"); câu trích CÓ chữ đó nên báo riêng
  bo_mat_bo_nghia          câu trích có vế bổ nghĩa ("nặng hơn sau khi ăn", "về đêm") mà nội dung bỏ
  nhan_khac_trich          nội dung trùng dưới 50% chữ nội dung với câu trích ("đau bụng" / "đi ngoài toàn nước")
Dùng lại : do_luong/thuoc_do_quy_gan._tu_noi_dung (bỏ từ chỉ người/từ đệm, đổi số chữ),
           duong_ong/b4_kiem_can_cu._chuan_so_lieu_thuoc (số viết chữ -> số),
           duong_ong/b0_chuan_hoa_phuong_ngu.chuan_hoa, bo_du_lieu/nhieu_asr.bo_dau
Giới hạn : chỉ đo, không đổi đường ống hay Chính sách D. Bảng `CHU_KHONG_DAU_HOP_LE` là danh sách tay.
"""
import re
import unicodedata
from typing import FrozenSet, List

from src.bo_du_lieu.nhieu_asr import bo_dau
from src.do_luong.thuoc_do_quy_gan import _tu_noi_dung
from src.duong_ong import b0_chuan_hoa_phuong_ngu as chuan_hoa
from src.duong_ong.b4_kiem_can_cu import _chuan_so_lieu_thuoc

NGUONG_NHAN = 0.5

# Âm tiết tiếng Việt viết không dấu (phụ âm đầu + nguyên âm + phụ âm cuối cho phép).
_AM_TIET = re.compile(r"^(ngh|ng|nh|ch|gh|gi|kh|ph|qu|th|tr|[bcdghklmnpqrstvx])?[aeiouy]+(ch|nh|ng|[cmnpt])?$")

# Chữ không dấu vốn đã là từ tiếng Việt đúng (hoặc nhập nhằng không phân xử được): không coi là chép lỗi ASR.
CHU_KHONG_DAU_HOP_LE = frozenset("""
khi sau hai da gan ban sinh theo cao do tay xanh men ho to thanh sung tai tra nghi quanh vi ong khu lo
an hay va ung lan mau sat nao cho quan rau vang con co di ba cam can ca chan hen kem mo ta la ve em anh
chi bo me cha ky ra vao no ta ai du tu tin nam nu gia vo xe
""".split())

_MOT = re.compile(r"[^\W\d_]+|\d+", re.UNICODE)

# Vế bổ nghĩa trong câu trích: mức nặng nhẹ, thời điểm, hoàn cảnh khởi phát.
_VE_BO_NGHIA = re.compile(
    r"(?<!\w)("
    r"(?:nặng|nhẹ|tệ|đỡ|nhiều|dữ|rõ)\s+hơn"
    r"|(?<!từ\s)(?:sau khi|trước khi|mỗi khi|khi)\s+\w+"
    r"|về\s+(?:đêm|chiều|sáng|tối|khuya)"
    r"|ban\s+(?:đêm|ngày)"
    r"|(?:buổi|lúc)\s+(?:sáng|chiều|tối|đêm|nằm|ngủ|ăn)"
    r"|(?:sau|trước)\s+(?:ăn|uống|bữa)"
    r"|mỗi\s+(?:sáng|tối|đêm|lần)"
    r")",
    re.I,
)


def _chuan(van: str) -> str:
    t = _chuan_so_lieu_thuoc(unicodedata.normalize("NFC", van or ""))
    return chuan_hoa.chuan_hoa(t, gom_can_hoi=False)


def _tu(van: str) -> FrozenSet[str]:
    return _tu_noi_dung(_chuan(van))


def _la_ascii_chu(t: str) -> bool:
    return t.isascii() and t.isalpha()


def _co_dau(t: str) -> bool:
    return bo_dau(t) != t


_TU_DIEN = None  # (số lần chữ ASCII, số lần các dạng có dấu cùng gốc) trong văn bản sạch


def _dung_tu_dien():
    """Từ điển tần số lập từ lời thoại của các bộ phát triển KHÔNG nhiễu ASR (chỉ dạng chữ). Thiếu tệp thì
    trả (rỗng, rỗng) và `_dang_chu_bo_dau` quay về danh sách tay."""
    global _TU_DIEN
    if _TU_DIEN is None:
        import json
        from collections import Counter
        from pathlib import Path
        a, c = Counter(), Counter()
        goc = Path(__file__).resolve().parent.parent.parent / "data" / "thach_thuc"
        for ten in ("dinh_chinh", "doi_chu_the", "phuong_ngu"):
            tep = goc / f"thach_thuc_{ten}_phat_trien.jsonl"
            if not tep.exists():
                continue
            for dong in tep.read_text(encoding="utf-8").splitlines():
                if not dong.strip():
                    continue
                for w in _MOT.findall(unicodedata.normalize("NFC", str(json.loads(dong).get("input", ""))).lower()):
                    if _co_dau(w):
                        c[bo_dau(w)] += 1
                    elif _la_ascii_chu(w):
                        a[w] += 1
        _TU_DIEN = (a, c)
    return _TU_DIEN


def _dang_chu_bo_dau(t: str) -> bool:
    """Chữ ASCII trông như âm tiết tiếng Việt bị bỏ dấu. Có từ điển: dạng có dấu cùng gốc phổ biến hơn dạng
    không dấu trong văn bản sạch. Danh sách chữ hợp lệ viết tay luôn được miễn."""
    if len(t) < 2 or not (_la_ascii_chu(t) and _AM_TIET.match(t)):
        return False
    if t in CHU_KHONG_DAU_HOP_LE:
        return False
    a, c = _dung_tu_dien()
    return c[t] > a[t] if c else True


def _co_trong_trich(t: str, tu_trich: FrozenSet[str], ascii_trich: FrozenSet[str]) -> bool:
    if t in tu_trich:
        return True
    # Trích là chữ ASR không dấu, nội dung đã khôi phục dấu: trích có hỗ trợ.
    return _co_dau(t) and bo_dau(t) in ascii_trich


def _vung_bo_nghia(trich: str):
    """(tập chữ phần trước vế bổ nghĩa, tập chữ của vế) cho từng vế bổ nghĩa trong câu trích."""
    t = unicodedata.normalize("NFC", trich or "").lower()
    ra = []
    for m in _VE_BO_NGHIA.finditer(t):
        cuoi = re.search(r"[,.;!?]", t[m.start():])
        ket = m.start() + cuoi.start() if cuoi else len(t)
        ve = _tu(t[m.start():ket])
        if ve:
            ra.append((_tu(t[:m.start()]), ve))
    return ra


def kiem_noi_dung_theo_trich(noi_dung: str, trich_dan: List[str]) -> List[str]:
    """Mã lý do cho thấy `noi_dung` không bám sát câu trích của chính nó; [] nếu ổn."""
    tu_nd = _tu(noi_dung)
    trich_dan = [t for t in (trich_dan or []) if t and t.strip()]
    if not tu_nd or not trich_dan:
        return []
    tu_trich = frozenset().union(*(_tu(t) for t in trich_dan))
    tho_trich = {w for t in trich_dan for w in _MOT.findall(unicodedata.normalize("NFC", t).lower())}
    ascii_trich = frozenset(w for w in tho_trich if _la_ascii_chu(w))

    ra: List[str] = []
    thieu = [t for t in tu_nd if not _co_trong_trich(t, tu_trich, ascii_trich)]
    if thieu:
        ra.append("tu_khong_co_trong_trich")
    if any(_dang_chu_bo_dau(t) and t in tu_trich for t in tu_nd):
        ra.append("chep_loi_asr")
    for truoc, ve in (v for t in trich_dan for v in _vung_bo_nghia(t)):
        if tu_nd & truoc and not (tu_nd & ve):
            ra.append("bo_mat_bo_nghia")
            break
    if (len(tu_nd) - len(thieu)) / len(tu_nd) < NGUONG_NHAN:
        ra.append("nhan_khac_trich")
    return ra
