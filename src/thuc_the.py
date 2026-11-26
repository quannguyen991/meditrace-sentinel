# -*- coding: utf-8 -*-
"""Bang thuc the va lien ket cach goi.

Hoi thoai nhac cung mot nguoi bang "toi", "chong toi", "benh nhan"; cung mot
thuoc bang ten day du roi "thuoc do". Neu `chu_the` la chuoi tu do thi mot
nguoi se thanh nhieu chu the, va bang cap nhat trang thai mat het y nghia:
khong the biet "dinh chinh" ai dinh chinh ai.

Hai chieu loi, ca hai deu phai do:

  bo sot lien ket   "thuoc A" va "thuoc do" thanh HAI thuc the
  gop nham          "thuoc A" va "thuoc B" thanh MOT thuc the

Chieu thu hai nguy hiem hon: no tron thong tin cua hai doi tuong khac nhau,
dung cai loi du an dang muon chan. Nen luat o day chi gop khi co CAN CU
(dai tu chi dinh tro nguoc, hoac cach goi trung ten chuan), khong gop theo
do giong nhau.

CHUA lam: lien ket `xét nghiệm` va `bệnh`. Hai loai do can tu dien thuat ngu
ma du an chua co. Khai bao trong LOAI de kieu du lieu san sang, nhung
`lien_ket()` chua sinh ra chung — noi ro con hon gia vo lam duoc.
"""
import re
from dataclasses import dataclass, field
from typing import List

LOAI = ("người", "thuốc", "xét nghiệm", "bệnh")

VAI_NOI = ("bác sĩ", "bệnh nhân", "người nhà", "điều dưỡng", "người khác")

# Tu chi quan he. "<quan he> toi" tro toi mot nguoi KHAC nguoi noi.
QUAN_HE = ("chồng", "vợ", "con trai", "con gái", "con", "cháu", "mẹ", "bố",
           "ba", "má", "cha", "anh trai", "chị gái", "anh", "chị", "em",
           "ông", "bà", "bé")
_QH = "|".join(sorted(QUAN_HE, key=len, reverse=True))

# "<quan he> toi/tui/em/minh" — cum so huu, tro toi NGUOI KHAC.
#
# "tui" them 24/09/2026: cach tu xung Nam Bo. Truoc do "Me tui bi tieu duong" khong
# sinh thuc the "me tui", nen tien su gia dinh roi vao nguoi noi. `khoa_bang_chung`
# da coi "tui" la tu xung tu truoc (TU_TU_XUNG_RO, _SO_HUU_DUOI) — hai tep cua cung
# duong ong noi hai dieu. ViDia2Std (tap dev): "tui -> toi" xuat hien 68 lan. Du lieu
# the he 8/8b khong co chu "tui" nao, nen so da bao cao khong doi. Gioi han: ban chep
# am mat dau co the bien "tụi" (tui no) thanh "tui".
QH_SO_HUU = re.compile(rf"(?i)\b({_QH})\s+(tôi|tui|em|mình)\b")

# Dai tu ngoi thu nhat DUNG MOT MINH — tro toi chinh nguoi noi.
NGOI_MOT = re.compile(r"(?i)\b(tôi|tui|em|cháu|mình)\b")

# Dai tu chi dinh cho thuoc — tro NGUOC lai thuoc vua nhac.
THUOC_TRO_NGUOC = re.compile(r"(?i)\b(thuốc|loại)\s+(đó|này|ấy|kia|nớ)\b")

# Ten thuoc: sau chu "thuoc" la mot tu viet hoa, hoac mot ten trong tu dien.
THUOC_CO_TEN = re.compile(r"(?:thuốc|uống)\s+([A-ZĐÀ-Ỹ][\wÀ-ỹ]*)")
TU_DIEN_THUOC = (
    "penicillin", "amoxicillin", "augmentin", "paracetamol", "ibuprofen",
    "cefixim", "cephalexin", "azithromycin", "erythromycin", "prednisolon",
    "salbutamol", "ventolin", "efferalgan", "hapacol", "aspirin", "insulin",
    "metformin", "amlodipin", "atorvastatin", "omeprazol",
)
# 25/11/2026: them moi ten trong data/tri_thuc_thuoc.json (158 hoat chat, gom thuoc cua 400 khuon
# moi). Giu ten cu o dau tuple de thu tu khop cu khong doi.
from src import tri_thuc_thuoc as _ttt  # noqa: E402
TU_DIEN_THUOC = TU_DIEN_THUOC + tuple(t for t in _ttt.tat_ca_ten() if t not in TU_DIEN_THUOC)
THUOC_TU_DIEN = re.compile(r"(?i)\b(" + "|".join(re.escape(t) for t in TU_DIEN_THUOC) + r")\b")

# Dau hieu cau noi cua nguoi nha dang ke ve TIEN SU GIA DINH (nguoi thu ba o nha),
# KHONG phai ke ve benh nhan dang kham (va loi "bo em" bi gop nham vao benh nhan).
DAU_TIEN_SU_GIA_DINH = re.compile(
    r"(?i)\b(cũng bị|ở nhà|từ nhỏ|hồi nhỏ|ngày xưa|hồi xưa|đã mất|qua đời|"
    r"di truyền|có liên quan|tiền sử gia đình|bên nội|bên ngoại)\b"
)
_QH_NAM_LON = ("bố", "ba", "cha", "chồng", "ông", "anh trai", "anh")
_QH_NU_LON = ("mẹ", "má", "vợ", "bà", "chị gái", "chị")
_QH_BAC_TREN = ("bố", "ba", "cha", "mẹ", "má", "ông", "bà")
_GOI_BN_NU = re.compile(r"(?i)\b(cô|chị|bà)\b")
_GOI_BN_NAM = re.compile(r"(?i)\b(chú|ông|anh)\b")
_GOI_BN_TRE = re.compile(r"(?i)\b(cháu|bé|con|em bé)\b")

# Tu dien dong nghia benh / trieu chung va xet nghiem khi bat `lien_ket_benh_xn=True`
NHOM_DONG_NGHIA_BENH = {
    "đau thượng vị": ("đau thượng vị", "đau dạ dày", "đau bao tử", "xót ruột", "đau vùng thượng vị"),
    "hen phế quản": ("hen phế quản", "hen suyễn", "bệnh hen", "suyễn"),
    "tăng huyết áp": ("tăng huyết áp", "cao huyết áp", "huyết áp cao"),
    "đái tháo đường": ("đái tháo đường", "tiểu đường", "đường huyết cao"),
    "viêm phổi": ("viêm phổi", "viêm phế quản phổi"),
    "viêm mũi dị ứng": ("viêm mũi dị ứng", "dị ứng thời tiết"),
}
NHOM_DONG_NGHIA_XN = {
    "xét nghiệm máu": ("xét nghiệm máu", "công thức máu", "lấy máu xét nghiệm"),
    "chụp x-quang": ("chụp x-quang", "chụp phim", "x-quang ngực", "chụp phổi"),
    "siêu âm bụng": ("siêu âm bụng", "siêu âm ổ bụng"),
    "điện tâm đồ": ("điện tâm đồ", "đo điện tim", "ecg"),
}


@dataclass
class ThucThe:
    id: int
    loai: str
    ten_chuan: str
    cach_goi: List[str] = field(default_factory=list)
    luot_thoai: List[int] = field(default_factory=list)

    def them(self, goi, luot):
        if goi not in self.cach_goi:
            self.cach_goi.append(goi)
        if luot not in self.luot_thoai:
            self.luot_thoai.append(luot)


def tach_luot(hoi_thoai):
    """-> [(so_luot, vai_nguoi_noi_hoac_None, noi_dung)]"""
    ra = []
    for i, dong in enumerate(d for d in hoi_thoai.split("\n") if d.strip()):
        dong = re.sub(r"^\s*\d+\.\s*", "", dong.strip())
        m = re.match(r"^([^:]{1,20}):\s*(.*)$", dong)
        if m:
            vai = m.group(1).strip().lower()
            ra.append((i + 1, vai if vai in VAI_NOI else vai, m.group(2)))
        else:
            ra.append((i + 1, None, dong))
    return ra


def _lien_ket_nguoi(luot):
    """Mot thuc the cho benh nhan, mot cho moi vai nguoi noi khac.

    Hai luat:
      - dai tu ngoi thu nhat DUNG MOT MINH -> chinh nguoi noi
      - "<quan he> toi" tu NGUOI NHA -> benh nhan, vi nguoi nha den kham la
        de noi ve benh nhan. Nhung neu nguoi nha dung HAI cum quan he khac
        nhau ("chong toi" va "con toi") thi khong the ca hai cung la benh
        nhan — luc do KHONG gop, de rieng, vi gop nham nguy hiem hon bo sot.
    """
    benh_nhan = ThucThe(0, "người", "bệnh nhân")
    theo_vai, ket_qua = {}, [benh_nhan]

    def cua_vai(vai):
        if vai == "bệnh nhân":
            return benh_nhan
        if vai not in theo_vai:
            t = ThucThe(len(ket_qua), "người", vai or "không rõ")
            theo_vai[vai] = t
            ket_qua.append(t)
        return theo_vai[vai]

    # Vong 1: dem cac cum "<quan he> toi" cua nguoi nha
    cum_quan_he = {}
    cum_la_gia_dinh = set()
    loi_bac_si = " ".join(v for _, vai_n, v in luot if vai_n in ("bác sĩ", "điều dưỡng"))
    bn_la_nu = bool(_GOI_BN_NU.search(loi_bac_si)) and not bool(_GOI_BN_NAM.search(loi_bac_si))
    bn_la_nam = bool(_GOI_BN_NAM.search(loi_bac_si)) and not bool(_GOI_BN_NU.search(loi_bac_si))
    bn_la_tre = bool(_GOI_BN_TRE.search(loi_bac_si))

    for so, vai, van in luot:
        if vai != "người nhà":
            continue
        for m in QH_SO_HUU.finditer(van):
            cum_thap = m.group(0).lower()
            qh_goc = m.group(1).lower()
            cum_quan_he.setdefault(cum_thap, []).append(so)
            # Kiem tra xem cum "<quan he> toi/em" co phai dang ke TIEN SU GIA DINH
            # (vd: "Bo em bi hen tu nho, khong biet co lien quan khong") hoac xung dot
            # gioi tinh / the he voi benh nhan dang kham hay khong.
            if DAU_TIEN_SU_GIA_DINH.search(van):
                cum_la_gia_dinh.add(cum_thap)
            elif bn_la_nu and qh_goc in _QH_NAM_LON:
                cum_la_gia_dinh.add(cum_thap)
            elif bn_la_nam and qh_goc in _QH_NU_LON:
                cum_la_gia_dinh.add(cum_thap)
            elif bn_la_tre and qh_goc in _QH_BAC_TREN:
                cum_la_gia_dinh.add(cum_thap)
    gop_ve_benh_nhan = (len(cum_quan_he) == 1) and not cum_la_gia_dinh

    theo_ten_rieng = {}
    for so, vai, van in luot:
        if vai:
            cua_vai(vai).them(vai, so)

        con_lai = van
        for m in QH_SO_HUU.finditer(van):
            cum = m.group(0)
            cum_thap = cum.lower()
            # Bác sĩ nói "...của chị tôi mới ghi" -> "chị" là người bệnh, "tôi" là bác sĩ, không phải quan hệ "chị tôi"
            if vai in ("bác sĩ", "điều dưỡng"):
                continue
            if vai == "người nhà" and gop_ve_benh_nhan and cum_thap not in cum_la_gia_dinh:
                benh_nhan.them(cum_thap, so)
            else:
                if cum_thap in theo_ten_rieng:
                    t = theo_ten_rieng[cum_thap]
                else:
                    t = ThucThe(len(ket_qua), "người", cum_thap)
                    theo_ten_rieng[cum_thap] = t
                    ket_qua.append(t)
                t.them(cum_thap, so)
            # Bo cum khoi van ban truoc khi tim dai tu dung mot minh, neu
            # khong thi chu "toi" trong "chong toi" se bi tinh la nguoi noi.
            con_lai = con_lai.replace(cum, " ")

        if NGOI_MOT.search(con_lai):
            goi = NGOI_MOT.search(con_lai).group(1).lower()
            (benh_nhan if vai == "bệnh nhân" else cua_vai(vai)).them(goi, so)

    return ket_qua


def _lien_ket_thuoc(luot, bat_dau_id):
    """Ten rieng tao thuc the moi; "thuoc do" tro nguoc ve thuoc gan nhat.

    Hai ten khac nhau KHONG bao gio bi gop — do la chieu loi nguy hiem.
    """
    ket_qua, theo_ten, gan_nhat = [], {}, None
    for so, _vai, van in luot:
        # Tro nguoc phai xet TRUOC ten rieng: "Thuoc do" co chu T viet hoa.
        moc = []
        for m in THUOC_TRO_NGUOC.finditer(van):
            moc.append(("tro_nguoc", m.start(), m.group(0)))
        for m in THUOC_CO_TEN.finditer(van):
            if not any(b <= m.start() < b + len(g) for _k, b, g in moc):
                moc.append(("ten", m.start(), m.group(1)))
        for m in THUOC_TU_DIEN.finditer(van):
            moc.append(("ten", m.start(), m.group(1)))
        moc.sort(key=lambda x: x[1])

        for kieu, _vi_tri, chu in moc:
            if kieu == "tro_nguoc":
                if gan_nhat is not None:
                    gan_nhat.them(chu.lower(), so)
                continue
            khoa = chu.lower()
            if khoa in theo_ten:
                t = theo_ten[khoa]
            else:
                t = ThucThe(bat_dau_id + len(ket_qua), "thuốc", chu)
                theo_ten[khoa] = t
                ket_qua.append(t)
            t.them(chu, so)
            gan_nhat = t
    return ket_qua


def _lien_ket_khai_niem(luot, bat_dau_id, loai_thuc_the, bang_dong_nghia):
    """Lien ket cac khai niem `bệnh` hoac `xét nghiệm` cung nhom dong nghia ve mot ThucThe."""
    ket_qua, theo_chuan = [], {}
    for so, _vai, van in luot:
        van_thap = van.lower()
        for ten_chuan, cac_bien_the in bang_dong_nghia.items():
            for bt in cac_bien_the:
                if re.search(rf"(?<!\w){re.escape(bt)}(?!\w)", van_thap):
                    if ten_chuan in theo_chuan:
                        t = theo_chuan[ten_chuan]
                    else:
                        t = ThucThe(bat_dau_id + len(ket_qua), loai_thuc_the, ten_chuan)
                        theo_chuan[ten_chuan] = t
                        ket_qua.append(t)
                    t.them(bt, so)
    return ket_qua


def lien_ket(hoi_thoai, lien_ket_benh_xn=False):
    """-> list[ThucThe]. Xem hai chieu loi o docstring dau tep.
    Mac dinh `lien_ket_benh_xn=False` de giu tuong thich 100% voi bo do goc;
    bat `lien_ket_benh_xn=True` (hoac goi `lien_ket_mo_rong`) de gom dong nghia benh va xet nghiem.
    """
    luot = tach_luot(hoi_thoai)
    nguoi = _lien_ket_nguoi(luot)
    thuoc = _lien_ket_thuoc(luot, bat_dau_id=len(nguoi))
    ra = nguoi + thuoc
    if lien_ket_benh_xn:
        benh = _lien_ket_khai_niem(luot, len(ra), "bệnh", NHOM_DONG_NGHIA_BENH)
        ra = ra + benh
        xn = _lien_ket_khai_niem(luot, len(ra), "xét nghiệm", NHOM_DONG_NGHIA_XN)
        ra = ra + xn
    return ra


def lien_ket_mo_rong(hoi_thoai):
    """Lien ket day du ca 4 loai thuc the: người, thuốc, bệnh, xét nghiệm."""
    return lien_ket(hoi_thoai, lien_ket_benh_xn=True)
