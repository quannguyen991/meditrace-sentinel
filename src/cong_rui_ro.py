# -*- coding: utf-8 -*-
"""Tang 5 — CONG RUI RO: khong phai loi nao cung nguy hiem nhu nhau.

Ghi sai di ung la ke nham thuoc; thieu mot chi tiet it quan trong thi khong. Tang
nay cho moi phat bieu mot DIEM RUI RO:

    diem = muc nghiem trong cua LOAI thong tin  x  do thieu can cu

roi chia ba nhom cho bac si:

    bi chan         khoa bang chung da chan — KHONG vao than, kem ly do
    nguy co cao     vao than nhung diem >= NGUONG_CAO — bac si duyet TRUOC
    da kiem chung   con lai

MOT CHIEU, co chu dinh: tang nay chi DANH DAU va XEP THU TU. Quyet dinh cho vao
than hay khong la cua `khoa_bang_chung`, noi co bang chung phu dinh. Ly do: phep
"day xuong theo diem rui ro" da thu ngay 07/09/2026 (`duong_danh_doi`) va THUA
nhom chon bua cung ty le o 2/3 nguong. Mot cong loc nua dung diem rui ro dat tay
se lap lai dung loi do.

TRONG SO DAT TAY — gioi han phai vao bao cao. Hai bang duoi day chua co du lieu
de hieu chuan; can bac si duyet. Vi the moi con so cua tang nay phai co COT CHON
BUA cung ty le danh dau (`danh_gia_khoa`): neu diem rui ro khong bat loi nhieu
hon chon bua thi no chua mang thong tin, du trong ra sao.
"""
from dataclasses import asdict, dataclass, field
from typing import Dict, List

# Muc nghiem trong theo LOAI thong tin — DAT TAY, cho bac si duyet.
MUC_NGHIEM_TRONG = {
    "di_ung": 1.0,       # ghi sai di ung -> ke nham thuoc
    "thuoc": 1.0,        # "dang dung" <-> "da ngung"
    "chan_doan": 0.8,    # nghi ngo thanh chan doan xac dinh
    "thoi_gian": 0.6,    # sai moc dien bien
    "khac": 0.3,         # mot chi tiet it quan trong hon
}

# Do thieu can cu, theo tung CANH BAO cua khoa (0..1). Bi chan -> 1,0.
DO_THIEU = {
    "mau_thuan": 1.0,
    "chu_the_nguoi_khac": 0.7,
    "chu_the_chua_ro": 0.6,
    "phu_dinh_vuot_muc": 0.6,
    "chu_the_suy_tu_nguoi_noi": 0.5,
    "noi_dung_khong_khop": 0.5,
    "phuong_ngu_can_hoi": 0.5,
    "co_tu_phu_dinh": 0.5,
    "moc_khong_thay": 0.5,
    # Chi tiet thuoc (15/09/2026). Lieu khong thay thi khoa CHAN (do thieu 1,0 tu
    # dong); hai chi tiet duoi chi canh bao. Dat tay nhu moi dong khac trong bang.
    "chi_tiet_thuoc_khong_thay": 0.6,
    "duong_dung_khong_thay": 0.5,
    "khong_trich_dan": 0.4,
    "trich_lech_luot": 0.3,
}
NGUONG_CAO = 0.5

BI_CHAN = "bị chặn"
NGUY_CO_CAO = "nguy cơ cao"
DA_KIEM_CHUNG = "đã kiểm chứng"
# Them 22/09/2026. Truoc do phat bieu CO CANH BAO nhung diem thap van mang nhan
# "đã kiểm chứng" — hien nhan do len giao dien la noi sai. Nay: co canh bao ma diem
# duoi NGUONG_CAO la "rủi ro thấp"; "đã kiểm chứng" chi con cho phat bieu KHONG co
# canh bao nao. Voi `hoi_lai`, hai nhom nay duoc xu ly nhu nhau (khong doi hanh vi).
RUI_RO_THAP = "rủi ro thấp"

# CHINH SACH XUAT BAN, cach C (chu du an chon 22/09/2026).
#   bi chan                              -> CẦN XÁC NHẬN (nhu truoc)
#   co canh bao VA la di ung hoac thuoc  -> CẦN XÁC NHẬN (MOI)
#   co canh bao, loai khac               -> o lai than ban nhap, mang nhan canh bao
# Ly do: do ngay 22/09 tren 4 bo thu thach, 699/813 phat bieu co canh bao nam trong
# than ban nhap ma khong co dau hieu gi; trong do 185 la di ung hoac thuoc. Ca that
# dct_002_B: "ông cụ nhà em thì dị ứng ibuprofen" ghi thanh "ông cụ: chưa ghi nhận
# dị ứng thuốc", co canh bao nhung van o than.
CHINH_SACH = "C-2026-09-22"
LOAI_XAC_NHAN_KHI_CANH_BAO = ("di_ung", "thuoc")


@dataclass
class DanhGia:
    id: int
    loai: str
    nghiem_trong: float
    thieu: float
    diem: float
    nhom: str
    ly_do: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def loai_thong_tin(p) -> str:
    """Loai thong tin, suy tu MUC ma `sinh_benh_an` xep phat bieu vao — MOT dinh
    nghia voi khau sinh ho so, khong mot bang tu khoa thu hai."""
    from src import sinh_benh_an
    d = p.to_dict() if hasattr(p, "to_dict") else dict(p)
    d = dict(d, trang_thai="còn hiệu lực")        # xep muc NHU THE no con hieu luc
    muc, _ = sinh_benh_an._muc_cho(d, 0)
    if muc == "DỊ ỨNG" or "dị ứng" in str(d.get("noi_dung", "")).lower():
        return "di_ung"
    if muc == "THUỐC ĐANG DÙNG":
        return "thuoc"
    if muc == "CHẨN ĐOÁN":
        return "chan_doan"
    if d.get("moc_thoi_gian") or d.get("quan_he") in ("đính chính", "diễn biến",
                                                      "mâu thuẫn"):
        return "thoi_gian"
    return "khac"


def cham(ps, ket_qua_khoa) -> List[DanhGia]:
    """-> mot DanhGia cho moi phat bieu, cung thu tu voi `ps`."""
    theo_id = {k.id: k for k in ket_qua_khoa}
    ra = []
    for p in ps:
        k = theo_id.get(p.id)
        loai = loai_thong_tin(p)
        nt = MUC_NGHIEM_TRONG[loai]
        if k is not None and k.chan:
            ra.append(DanhGia(p.id, loai, nt, 1.0, nt, BI_CHAN, list(k.chan)))
            continue
        canh = list(k.canh_bao) if k is not None else []
        thieu = max((DO_THIEU.get(m, 0.3) for m in canh), default=0.0)
        diem = round(nt * thieu, 4)
        nhom = (NGUY_CO_CAO if diem >= NGUONG_CAO
                else RUI_RO_THAP if canh else DA_KIEM_CHUNG)
        ra.append(DanhGia(p.id, loai, nt, thieu, diem, nhom, canh))
    return ra


def thu_tu_duyet(danh_gia: List[DanhGia]) -> List[DanhGia]:
    """Thu tu bac si nen doc: bi chan truoc (nghiem trong giam dan), roi nguy co
    cao (diem giam dan), roi phan con lai."""
    hang = {BI_CHAN: 0, NGUY_CO_CAO: 1, RUI_RO_THAP: 2, DA_KIEM_CHUNG: 3}
    return sorted(danh_gia, key=lambda d: (hang[d.nhom], -d.nghiem_trong,
                                           -d.diem, d.id))


def dem_nhom(danh_gia: List[DanhGia]) -> Dict[str, int]:
    ra = {BI_CHAN: 0, NGUY_CO_CAO: 0, RUI_RO_THAP: 0, DA_KIEM_CHUNG: 0}
    for d in danh_gia:
        ra[d.nhom] += 1
    return ra


_TEN_LOAI = {"di_ung": "dị ứng", "thuoc": "thuốc"}


def dua_sang_xac_nhan(danh_gia: List[DanhGia]) -> Dict[int, str]:
    """Cach C: phat bieu di ung hoac thuoc CO CANH BAO -> {id: ly do} de dua sang
    CẦN XÁC NHẬN. Phat bieu bi chan khong o day — khoa da dua chung di roi."""
    from src.khoa_bang_chung import LY_DO   # nap muon: tranh vong nap
    ra = {}
    for d in danh_gia:
        if d.nhom != BI_CHAN and d.ly_do and d.loai in LOAI_XAC_NHAN_KHI_CANH_BAO:
            ra[d.id] = (f"cảnh báo ở thông tin {_TEN_LOAI[d.loai]}: "
                        + "; ".join(LY_DO.get(m, m) for m in d.ly_do))
    return ra
