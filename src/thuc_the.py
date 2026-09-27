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

VAI_NOI = ("bác sĩ", "bệnh nhân", "người nhà", "điều dưỡng")

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
THUOC_TU_DIEN = re.compile(r"(?i)\b(" + "|".join(TU_DIEN_THUOC) + r")\b")


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
    for so, vai, van in luot:
        if vai != "người nhà":
            continue
        for m in QH_SO_HUU.finditer(van):
            cum_quan_he.setdefault(m.group(0).lower(), []).append(so)
    gop_ve_benh_nhan = len(cum_quan_he) == 1

    for so, vai, van in luot:
        if vai:
            cua_vai(vai).them(vai, so)

        con_lai = van
        for m in QH_SO_HUU.finditer(van):
            cum = m.group(0)
            if vai == "người nhà" and gop_ve_benh_nhan:
                benh_nhan.them(cum.lower(), so)
            else:
                t = ThucThe(len(ket_qua), "người", cum.lower())
                t.them(cum.lower(), so)
                ket_qua.append(t)
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


def lien_ket(hoi_thoai):
    """-> list[ThucThe]. Xem hai chieu loi o docstring dau tep."""
    luot = tach_luot(hoi_thoai)
    nguoi = _lien_ket_nguoi(luot)
    thuoc = _lien_ket_thuoc(luot, bat_dau_id=len(nguoi))
    return nguoi + thuoc
