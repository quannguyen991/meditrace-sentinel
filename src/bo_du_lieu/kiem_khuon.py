# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Khuôn bệnh]
Làm gì   : Kiểm khuôn bệnh có hợp lệ không (đủ trường, đúng giới, không trùng nhau quá)
           trước khi cho vào bộ sinh.
Vào → Ra : danh sách khuôn + tập khuôn chỉ nữ / chỉ nam → KetQuaKiem gồm các VanDe;
           bao_cao() in thành văn bản
Đọc từ   : kiem_tat_ca() chạy cho mọi khuôn; kiem_mot() là các phép kiểm cho một khuôn;
           bao_cao() in kết quả
Mục lục (các hàm/lớp chính):
  kiem_tat_ca()     Kiểm toàn bộ bộ khuôn, tên trùng và trùng lặp chéo
  kiem_mot()        Kiểm từng khuôn theo luật riêng
  bao_cao()         Viết báo cáo kiểm khuôn bằng tiếng Việt
  class KetQuaKiem  Kết quả kiểm cả bộ khuôn
  class VanDe       Một vấn đề phát hiện khi kiểm khuôn
Gọi tới  : bo_du_lieu/ngu_lieu_viet
Tên cũ   : kiem_khuon.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Bộ kiểm khuôn bệnh (validator) cho `ngu_lieu_viet.BENH`.

Mục đích: trước khi một khuôn vào bộ sinh, kiểm nó bằng luật xác định, không dựa
vào cảm nhận. Ba mức độ:

  LOI   — chặn. Khuôn sai cấu trúc, trùng tên, sai giới, chẩn đoán không có tên bệnh.
          Bộ sinh không được chạy khi còn LOI.
  CANH  — cần người xem. Có thể sai về tuổi hay trùng triệu chứng nhưng chưa chắc.
  INFO  — thông tin. Ví dụ khuôn chưa có bác sĩ duyệt.

Bộ kiểm KHÔNG thay thế bác sĩ. Cột "da duyet" là cột riêng: khuôn mặc định
CHƯA DUYỆT, và chỉ có bác sĩ mới được thêm tên khuôn vào `DA_DUYET_BAC_SI`.
Khớp với bất biến I3 của MediTrace: AI không tự chuyển sang trạng thái đã duyệt.

Chạy:  python -m src.bo_du_lieu.kiem_khuon
"""
import re
import unicodedata
from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, Iterable, List, Set, Tuple

NHOM_HOP_LE = {"nhi", "người lớn", "cả hai"}
DIEN_TIEN_HOP_LE = {"cấp", "mạn"}
TRUONG_BAT_BUOC = {"ten", "nhom", "dien_tien", "chinh", "phu", "kham", "chan_doan", "ke_hoach"}
TRUONG_HOP_LE = TRUONG_BAT_BUOC | {"da_duyet", "he_co_quan"}

# Ngưỡng trùng lặp: Jaccard trên tập từ của triệu chứng chính + phụ.
NGUONG_TRUNG = 0.20

# Từ không mang nghĩa bệnh: bỏ khi so trùng triệu chứng.
TU_DUNG = {
    # 1. Hư từ, quan hệ từ, liên từ
    "và", "của", "là", "có", "đang", "một", "các", "những", "bị", "khi", "từ",
    "vì", "ở", "trong", "hay", "với", "cho", "thì", "đã", "rồi", "nên", "hơn",
    "cả", "sau", "trước", "nhiều", "ít", "ra", "vào", "lên", "xuống", "nhẹ", "mạnh",
    # 2. Từ chỉ định, phó từ, trạng từ, phương hướng, thời gian chung
    "đi", "lại", "về", "lúc", "kèm", "theo", "do", "bằng", "làm", "như", "thành",
    "tại", "này", "được", "rất", "thường", "xuyên", "liên", "tục", "không", "thấy",
    "cảm", "giác", "vừa", "từng", "cơn", "mỗi", "quá", "khắp", "hai", "bên", "vùng",
    "gần", "ngày", "đêm", "sáng", "chiều", "tối", "khác", "chung", "tự", "rõ",
    "nhất", "cực", "kỳ", "khoảng", "đều", "gặp", "tăng", "giảm", "mức", "độ",
    "gắng", "sức", "tầm", "phía", "chỗ", "phần", "qua", "nào", "gì", "sao",
    "nặng", "vừa", "kéo", "dài", "thoảng", "đôi", "chút", "dần", "nhanh", "chậm",
    # 3. Triệu chứng toàn thân chung không mang tính định danh bệnh lý
    "đau", "mệt", "khó", "sốt", "mỏi", "chán", "ăn", "ngủ", "buồn", "nôn",
}

# Từ chỉ đặc thù cho một nhóm tuổi (khớp nguyên từ, dùng biểu thức chính quy).
# Gặp trong khuôn của nhóm khác là CANH, không phải LOI: đây là tín hiệu để xem lại.
TU_TRE_EM = (r"\btrẻ\b", r"\bbú\b", r"\btã\b", r"quấy khóc", r"\bbé\b", r"nhũ nhi", r"sữa mẹ", r"cai sữa")
TU_NGUOI_LON = (r"thai kỳ", r"mãn kinh", r"rượu bia", r"hút thuốc", r"thoái hóa", r"tăng huyết áp")

# Từ chỉ một giới (nội dung khuôn nhắc đến thì nhãn giới phải khớp).
TU_CHI_NU = (r"kinh nguyệt", r"âm đạo", r"mãn kinh", r"thai kỳ", r"tử cung", r"buồng trứng", r"cổ tử cung", r"\bvú\b")
TU_CHI_NAM = (r"tuyến tiền liệt", r"tinh hoàn", r"dương vật", r"thừng tinh")

# Khuôn đã được bác sĩ duyệt. Rỗng = chưa có ai duyệt. Chỉ bác sĩ mới được thêm tên vào đây.
DA_DUYET_BAC_SI: Set[str] = set()


# ═══ class VanDe — Một vấn đề phát hiện khi kiểm khuôn ════════════════════════════════
# Có mức LOI, CANH hoặc INFO, tên khuôn và nội dung.
@dataclass
class VanDe:
    muc: str            # "LOI" | "CANH" | "INFO"
    khuon: str          # tên khuôn, hoặc "" nếu là vấn đề chung
    noi_dung: str


# ═══ class KetQuaKiem — Kết quả kiểm cả bộ khuôn ══════════════════════════════════════
# Gom vấn đề và các cặp khuôn trùng; đạt khi không có lỗi mức LOI.
@dataclass
class KetQuaKiem:
    so_khuon: int
    van_de: List[VanDe] = field(default_factory=list)
    cap_trung: List[Tuple[str, str, float]] = field(default_factory=list)

    def dem(self, muc: str) -> int:
        return sum(1 for v in self.van_de if v.muc == muc)

    @property
    def dat(self) -> bool:
        return self.dem("LOI") == 0


# ─── _chuan() — Chuẩn hoá chuỗi về NFC và bỏ khoảng trắng thừa ────────────────────────
# Chuỗi rỗng hoặc None trả chuỗi rỗng.
def _chuan(s: str) -> str:
    return unicodedata.normalize("NFC", s or "").strip()


# ─── _tu_khoa() — Rút tập từ khoá và cặp từ liền nhau từ các cụm ──────────────────────
# Bỏ từ dừng và từ một chữ; dùng để so độ trùng giữa các khuôn.
def _tu_khoa(cum: Iterable[str]) -> Set[str]:
    tokens = set()
    for c in cum:
        words = [w for w in re.findall(r"[^\W\d_]+", _chuan(c).lower()) if len(w) > 1 and w not in TU_DUNG]
        if not words:
            continue
        for i in range(len(words) - 1):
            tokens.add(f"{words[i]}_{words[i+1]}")
        for w in words:
            tokens.add(w)
    return tokens


# ─── _jaccard() — Tính độ giống Jaccard giữa hai tập từ khoá ──────────────────────────
# Bằng 0 khi một trong hai tập rỗng.
def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


# ═══ kiem_mot() — Kiểm từng khuôn theo luật riêng ═════════════════════════════════════
# Gặp thiếu trường bắt buộc thì báo LOI; trường lạ thì CANH.
def kiem_mot(b: dict, chi_nu: Set[str], chi_nam: Set[str], nhan_gioi: Dict[str, str]) -> List[VanDe]:
    """Kiểm từng khuôn theo luật riêng (không so sánh giữa các khuôn)."""
    out: List[VanDe] = []
    ten = _chuan(b.get("ten", ""))

    thieu = TRUONG_BAT_BUOC - set(b)
    if thieu:
        out.append(VanDe("LOI", ten, f"thieu truong {sorted(thieu)}"))
        return out
    extra = set(b) - TRUONG_HOP_LE
    if extra:
        out.append(VanDe("CANH", ten, f"truong la {sorted(extra)}, bo sinh co the khong dung"))

    if not ten:
        out.append(VanDe("LOI", "", "khuon khong co ten"))
        return out
    for truong in ("ten", "kham", "chan_doan", "ke_hoach", "nhom", "dien_tien"):
        v = _chuan(b.get(truong, ""))
        if not v:
            out.append(VanDe("LOI", ten, f"{truong} rong"))
        if v != b.get(truong, ""):
            out.append(VanDe("CANH", ten, f"{truong} chua chuan hoa Unicode NFC"))
    for truong in ("chinh", "phu"):
        ds = b.get(truong)
        if not isinstance(ds, list) or len(ds) < 2:
            out.append(VanDe("LOI", ten, f"{truong} can it nhat 2 muc"))
        elif any(not _chuan(x) for x in ds):
            out.append(VanDe("LOI", ten, f"{truong} co muc rong"))
        elif len({_chuan(x).lower() for x in ds}) != len(ds):
            out.append(VanDe("LOI", ten, f"{truong} co muc lap lai"))

    if b.get("nhom") not in NHOM_HOP_LE:
        out.append(VanDe("LOI", ten, f"nhom {b.get('nhom')!r} khong hop le"))
    if b.get("dien_tien") not in DIEN_TIEN_HOP_LE:
        out.append(VanDe("LOI", ten, f"dien_tien {b.get('dien_tien')!r} khong hop le"))

    van_ban = " ".join(
        [*b.get("chinh", []), *b.get("phu", []), b.get("kham", ""), b.get("ke_hoach", ""), b.get("chan_doan", ""), ten]
    ).lower()

    # Giới: luật đang chạy là GIOI_THEO_KHUON (nhãn nam/nữ cho một khuôn). Từ khoá
    # chỉ một giới trong nội dung thì phải có nhãn đúng, nếu không là lỗi.
    nhan = nhan_gioi.get(ten)
    if nhan is not None and nhan not in ("nam", "nữ"):
        out.append(VanDe("LOI", ten, f"nhan gioi {nhan!r} khong hop le"))
    # Nhãn mâu thuẫn với nội dung là LOI. Không có nhãn mà có từ chỉ một giới là CANH:
    # có thể là biến chứng thật (ví dụ quai bị gây viêm tinh hoàn ở trẻ trai), chỉ cần xem lại.
    co_nu = [t for t in TU_CHI_NU if re.search(t, van_ban)]
    co_nam = [t for t in TU_CHI_NAM if re.search(t, van_ban)]
    if co_nu and nhan == "nam":
        out.append(VanDe("LOI", ten, f"noi dung co tu chi nu {co_nu} nhung nhan gioi la nam"))
    if co_nam and nhan == "nữ":
        out.append(VanDe("LOI", ten, f"noi dung co tu chi nam {co_nam} nhung nhan gioi la nữ"))
    if nhan is None and (co_nu or co_nam):
        out.append(VanDe("CANH", ten, f"co tu chi mot gioi {co_nu or co_nam} nhung chua co nhan gioi: xem lai"))
    if ten in chi_nu and ten in chi_nam:
        out.append(VanDe("LOI", ten, "benh nam trong CA HAI danh sach gioi"))

    # Tuổi: từ khoá đặc trưng của nhóm tuổi không được lạc nhóm (khớp nguyên từ).
    if b.get("nhom") == "người lớn":
        gap = [t for t in TU_TRE_EM if re.search(t, van_ban)]
        if gap:
            out.append(VanDe("CANH", ten, f"nhom nguoi lon nhung co tu tre em: {gap}"))
    if b.get("nhom") == "nhi":
        gap = [t for t in TU_NGUOI_LON if re.search(t, van_ban)]
        if gap:
            out.append(VanDe("CANH", ten, f"nhom nhi nhung co tu nguoi lon: {gap}"))

    # Chẩn đoán: phải nhắc tên bệnh (ít nhất một từ khoá của tên có trong chẩn đoán).
    tu_ten = _tu_khoa([ten])
    tu_cd = _tu_khoa([b.get("chan_doan", "")])
    if tu_ten and not (tu_ten & tu_cd):
        out.append(VanDe("LOI", ten, f"chan doan {b.get('chan_doan')!r} khong nhac ten benh"))
    if b.get("dien_tien") == "cấp" and "mạn" in _chuan(b.get("chan_doan", "")).lower():
        out.append(VanDe("CANH", ten, "dien_tien cap nhung chan doan ghi 'man'"))
    if b.get("dien_tien") == "mạn" and re.search(r"\bcấp\b", _chuan(b.get("chan_doan", "")).lower()):
        out.append(VanDe("CANH", ten, "dien_tien man nhung chan doan ghi 'cap'"))

    if ten not in DA_DUYET_BAC_SI and not b.get("da_duyet", False):
        out.append(VanDe("INFO", ten, "chua co bac si duyet"))
    return out


# ═══ kiem_tat_ca() — Kiểm toàn bộ bộ khuôn, tên trùng và trùng lặp chéo ═══════════════
# Cặp khuôn trùng triệu chứng vượt ngưỡng được liệt kê.
def kiem_tat_ca(
    benh: List[dict],
    chi_nu: Iterable[str],
    chi_nam: Iterable[str],
    nhan_gioi: Dict[str, str],
    nguong_trung: float = NGUONG_TRUNG,
) -> KetQuaKiem:
    """Kiểm toàn bộ bộ khuôn: từng khuôn, tên trùng, và trùng lặp giữa các khuôn."""
    chi_nu, chi_nam = set(chi_nu), set(chi_nam)
    ket = KetQuaKiem(so_khuon=len(benh))

    ten = [_chuan(b.get("ten", "")) for b in benh]
    for t, so in _dem(ten).items():
        if so > 1:
            ket.van_de.append(VanDe("LOI", t, f"ten trung {so} lan"))
    # Tên khác nhau nhưng cùng chữ (khác hoa/thường, khác dấu cách).
    chuan_ten = _dem([re.sub(r"\s+", " ", t.lower()) for t in ten])
    for t, so in chuan_ten.items():
        if so > 1 and _dem(ten)[t] == 1:
            ket.van_de.append(VanDe("LOI", t, "ten trung sau khi bo hoa thuong"))

    # Tên trong danh sách giới mà không có khuôn nào: quy tắc đó không bao giờ chạy.
    for ten_khuon in sorted(chi_nu | chi_nam):
        if ten_khuon not in ten:
            ket.van_de.append(VanDe(
                "CANH", ten_khuon,
                "nam trong danh sach gioi (CHI_NU/CHI_NAM) nhung khong khop khuon nao: quy tac nay khong chay",
            ))
    for ten_khuon in sorted(nhan_gioi):
        if ten_khuon not in ten:
            ket.van_de.append(VanDe("LOI", ten_khuon, "co nhan gioi nhung khuon khong ton tai"))

    for b in benh:
        ket.van_de.extend(kiem_mot(b, chi_nu, chi_nam, nhan_gioi))

    # Trùng lặp triệu chứng giữa các khuôn.
    tu = {_chuan(b.get("ten", "")): _tu_khoa([*b.get("chinh", []), *b.get("phu", [])]) for b in benh}
    for a, b2 in combinations(sorted(tu), 2):
        j = _jaccard(tu[a], tu[b2])
        if j >= nguong_trung:
            ket.cap_trung.append((a, b2, round(j, 3)))
            ket.van_de.append(VanDe("CANH", a, f"trung trieu chung {j:.0%} voi '{b2}'"))
    return ket


# ─── _dem() — Đếm số lần xuất hiện của mỗi phần tử ────────────────────────────────────
# Trả từ điển phần tử sang số lần.
def _dem(ds: Iterable[str]) -> Dict[str, int]:
    d: Dict[str, int] = {}
    for x in ds:
        d[x] = d.get(x, 0) + 1
    return d


# ═══ bao_cao() — Viết báo cáo kiểm khuôn bằng tiếng Việt ══════════════════════════════
# Ghi số lỗi, cảnh báo, kết luận đạt hoặc không; bỏ mục INFO.
def bao_cao(ket: KetQuaKiem) -> str:
    dong = [
        f"Số khuôn: {ket.so_khuon}",
        f"LỖI (chặn): {ket.dem('LOI')}   CẢNH BÁO (xem lại): {ket.dem('CANH')}   "
        f"CHƯA DUYỆT BÁC SĨ: {ket.dem('INFO')}",
        f"Cặp khuôn trùng triệu chứng ≥ {NGUONG_TRUNG:.0%}: {len(ket.cap_trung)}",
        "Kết luận: " + ("ĐẠT cấu trúc, chưa đủ để dùng nội dung y khoa." if ket.dat else "KHÔNG ĐẠT, sửa LỖI trước."),
    ]
    for v in sorted(ket.van_de, key=lambda v: ({"LOI": 0, "CANH": 1, "INFO": 2}[v.muc], v.khuon)):
        if v.muc == "INFO":
            continue
        dong.append(f"  [{v.muc}] {v.khuon or '(chung)'}: {v.noi_dung}")
    return "\n".join(dong)


if __name__ == "__main__":
    import sys
    from src.bo_du_lieu import ngu_lieu_viet as nl

    ket = kiem_tat_ca(nl.BENH, nl.CHI_NU, nl.CHI_NAM, nl.GIOI_THEO_KHUON)
    print(bao_cao(ket))
    sys.exit(0 if ket.dat else 1)
