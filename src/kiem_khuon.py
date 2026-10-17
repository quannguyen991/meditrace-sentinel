# -*- coding: utf-8 -*-
"""Bo kiem khuon benh (validator) cho `ngu_lieu_viet.BENH`.

Muc dich: truoc khi mot khuon vao bo sinh, kiem no bang luat xac dinh, khong dua
vao cam nhan. Ba muc do:

  LOI   — chan. Khuon sai cau truc, trung ten, sai gioi, chan doan khong co ten benh.
          Bo sinh khong duoc chay khi con LOI.
  CANH  — can nguoi xem. Co the sai ve tuoi hay trung trieu chung nhung chua chac.
  INFO  — thong tin. Vi du khuon chua co bac si duyet.

Bo kiem KHONG thay the bac si. Cot "da duyet" la cot rieng: khuon mac dinh
CHUA DUYET, va chi co bac si moi duoc them ten khuon vao `DA_DUYET_BAC_SI`.
Khop voi bat bien I3 cua MediTrace: AI khong tu chuyen sang trang thai da duyet.

Chay:  python -m src.kiem_khuon
"""
import re
import unicodedata
from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, Iterable, List, Set, Tuple

NHOM_HOP_LE = {"nhi", "người lớn", "cả hai"}
DIEN_TIEN_HOP_LE = {"cấp", "mạn"}
TRUONG_BAT_BUOC = {"ten", "nhom", "dien_tien", "chinh", "phu", "kham", "chan_doan", "ke_hoach"}

# Nguong trung lap: Jaccard tren tap tu cua trieu chung chinh + phu.
NGUONG_TRUNG = 0.5

# Tu khong mang nghia benh: bo khi so trung trieu chung.
TU_DUNG = {
    "và", "của", "là", "có", "đang", "một", "các", "những", "bị", "khi", "từ",
    "vì", "ở", "trong", "hay", "với", "cho", "thì", "đã", "rồi", "nên", "hơn",
    "cả", "sau", "trước", "nhiều", "ít", "ra", "vào", "lên", "xuống", "nhẹ", "mạnh",
}

# Tu chi dac thu cho mot nhom tuoi (khop nguyen tu, dung bieu thuc chinh quy).
# Gap trong khuon cua nhom khac la CANH, khong phai LOI: day la tin hieu de xem lai.
TU_TRE_EM = (r"\btrẻ\b", r"\bbú\b", r"\btã\b", r"quấy khóc", r"\bbé\b", r"nhũ nhi", r"sữa mẹ", r"cai sữa")
TU_NGUOI_LON = (r"thai kỳ", r"mãn kinh", r"rượu bia", r"hút thuốc", r"thoái hóa", r"tăng huyết áp")

# Tu chi mot gioi (noi dung khuon nhac den thi nhan gioi phai khop).
TU_CHI_NU = (r"kinh nguyệt", r"âm đạo", r"mãn kinh", r"thai kỳ", r"tử cung", r"buồng trứng", r"cổ tử cung", r"\bvú\b")
TU_CHI_NAM = (r"tuyến tiền liệt", r"tinh hoàn", r"dương vật", r"thừng tinh")

# Khuon da duoc bac si duyet. Rong = chua co ai duyet. Chi bac si moi duoc them ten vao day.
DA_DUYET_BAC_SI: Set[str] = set()


@dataclass
class VanDe:
    muc: str            # "LOI" | "CANH" | "INFO"
    khuon: str          # ten khuon, hoac "" neu la van de chung
    noi_dung: str


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


def _chuan(s: str) -> str:
    return unicodedata.normalize("NFC", s or "").strip()


def _tu_khoa(cum: Iterable[str]) -> Set[str]:
    tu = set()
    for c in cum:
        for t in re.findall(r"[^\W\d_]+", _chuan(c).lower()):
            if len(t) > 1 and t not in TU_DUNG:
                tu.add(t)
    return tu


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def kiem_mot(b: dict, chi_nu: Set[str], chi_nam: Set[str], nhan_gioi: Dict[str, str]) -> List[VanDe]:
    """Kiem tung khuon theo luat rieng (khong so sanh giua cac khuon)."""
    out: List[VanDe] = []
    ten = _chuan(b.get("ten", ""))

    thieu = TRUONG_BAT_BUOC - set(b)
    if thieu:
        out.append(VanDe("LOI", ten, f"thieu truong {sorted(thieu)}"))
        return out
    extra = set(b) - TRUONG_BAT_BUOC
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

    # Gioi: luat dang chay la GIOI_THEO_KHUON (nhan nam/nu cho mot khuon). Tu khoa
    # chi mot gioi trong noi dung thi phai co nhan dung, neu khong la loi.
    nhan = nhan_gioi.get(ten)
    if nhan is not None and nhan not in ("nam", "nữ"):
        out.append(VanDe("LOI", ten, f"nhan gioi {nhan!r} khong hop le"))
    # Nhan mau thuan voi noi dung la LOI. Khong co nhan ma co tu chi mot gioi la CANH:
    # co the la bien chung that (vi du quai bi gay viem tinh hoan o tre trai), chi can xem lai.
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

    # Tuoi: tu khoa dac trung cua nhom tuoi khong duoc lac nhom (khop nguyen tu).
    if b.get("nhom") == "người lớn":
        gap = [t for t in TU_TRE_EM if re.search(t, van_ban)]
        if gap:
            out.append(VanDe("CANH", ten, f"nhom nguoi lon nhung co tu tre em: {gap}"))
    if b.get("nhom") == "nhi":
        gap = [t for t in TU_NGUOI_LON if re.search(t, van_ban)]
        if gap:
            out.append(VanDe("CANH", ten, f"nhom nhi nhung co tu nguoi lon: {gap}"))

    # Chan doan: phai nhac ten benh (it nhat mot tu khoa cua ten co trong chan doan).
    tu_ten = _tu_khoa([ten])
    tu_cd = _tu_khoa([b.get("chan_doan", "")])
    if tu_ten and not (tu_ten & tu_cd):
        out.append(VanDe("LOI", ten, f"chan doan {b.get('chan_doan')!r} khong nhac ten benh"))
    if b.get("dien_tien") == "cấp" and "mạn" in _chuan(b.get("chan_doan", "")).lower():
        out.append(VanDe("CANH", ten, "dien_tien cap nhung chan doan ghi 'man'"))
    if b.get("dien_tien") == "mạn" and re.search(r"\bcấp\b", _chuan(b.get("chan_doan", "")).lower()):
        out.append(VanDe("CANH", ten, "dien_tien man nhung chan doan ghi 'cap'"))

    if ten not in DA_DUYET_BAC_SI:
        out.append(VanDe("INFO", ten, "chua co bac si duyet"))
    return out


def kiem_tat_ca(
    benh: List[dict],
    chi_nu: Iterable[str],
    chi_nam: Iterable[str],
    nhan_gioi: Dict[str, str],
    nguong_trung: float = NGUONG_TRUNG,
) -> KetQuaKiem:
    """Kiem toan bo bo khuon: tung khuon, ten trung, va trung lap giua cac khuon."""
    chi_nu, chi_nam = set(chi_nu), set(chi_nam)
    ket = KetQuaKiem(so_khuon=len(benh))

    ten = [_chuan(b.get("ten", "")) for b in benh]
    for t, so in _dem(ten).items():
        if so > 1:
            ket.van_de.append(VanDe("LOI", t, f"ten trung {so} lan"))
    # Ten khac nhau nhung cung chu (khac hoa/thuong, khac dau cach).
    chuan_ten = _dem([re.sub(r"\s+", " ", t.lower()) for t in ten])
    for t, so in chuan_ten.items():
        if so > 1 and _dem(ten)[t] == 1:
            ket.van_de.append(VanDe("LOI", t, "ten trung sau khi bo hoa thuong"))

    # Ten trong danh sach gioi ma khong co khuon nao: quy tac do khong bao gio chay.
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

    # Trung lap trieu chung giua cac khuon.
    tu = {_chuan(b.get("ten", "")): _tu_khoa([*b.get("chinh", []), *b.get("phu", [])]) for b in benh}
    for a, b2 in combinations(sorted(tu), 2):
        j = _jaccard(tu[a], tu[b2])
        if j >= nguong_trung:
            ket.cap_trung.append((a, b2, round(j, 3)))
            ket.van_de.append(VanDe("CANH", a, f"trung trieu chung {j:.0%} voi '{b2}'"))
    return ket


def _dem(ds: Iterable[str]) -> Dict[str, int]:
    d: Dict[str, int] = {}
    for x in ds:
        d[x] = d.get(x, 0) + 1
    return d


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
    from src import ngu_lieu_viet as nl

    ket = kiem_tat_ca(nl.BENH, nl.CHI_NU, nl.CHI_NAM, nl.GIOI_THEO_KHUON)
    print(bao_cao(ket))
    sys.exit(0 if ket.dat else 1)
