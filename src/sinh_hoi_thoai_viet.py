# -*- coding: utf-8 -*-
"""Bo sinh hoi thoai kham benh Viet Nam, kem benh an va DAP AN CO CAU TRUC.

    python -m src.sinh_hoi_thoai_viet --so-ca 1000

VI SAO TU DUNG BO NAY, VA VI SAO SINH BANG LUAT CHU KHONG BANG MO HINH.

Bo du lieu cua cuoc thi co dau vet ro la ban dich tu mot bo hoi thoai y khoa
tieng Anh (xem `docs/ket-qua/dau-vet-nguon.md`). Hai hien tuong lam viec quy gan
kho nhat trong tieng Viet — LUOC CHU NGU va DUNG TU CHI QUAN HE HO HANG LAM DAI
TU — deu bi duoi dai dien trong mot ban dich, vi tieng Anh gan nhu luon co chu
ngu. Bo nay sinh ra dung hai hien tuong do.

Va no sinh bang LUAT, khong bang mo hinh ngon ngu. Do la rang buoc so 1 cua ca
du an, va ly do khong phai hinh thuc:

  Du an do "mo hinh gan nham thong tin cho sai nguoi bao nhieu lan". Mo hinh
  ngon ngu viet hoi thoai SACH hon nguoi noi that — no gan nhu luon ghi ro chu
  ngu o moi luot. Nen dung ca kho nhat se hiem di, va duong tat "chu the chinh
  la nguoi vua noi" se TRUNG nhieu hon binh thuong. Do khong phai sai so ngau
  nhien: no lech mot chieu, luon ve phia lam van de trong nhe hon that.

CAI BO NAY CO MA BO CUA CUOC THI KHONG CO: **dap an co cau truc**. Moi menh de
trong benh an deu kem chu the that, moc thoi gian that, va tinh huong that. Nho
do do duoc do chinh xac quy gan CHINH XAC TUYET DOI, khong phai uoc luong qua
ban tham chieu dang van xuoi.

BON CAI BAY DA VAP O `meditrace`, deu da chan o day:

  1. Thay the lam bai toan khong giai duoc  -> chi CHEN them, giu nguyen luot goc
  2. Hai khang dinh khac nhau khong phai mau thuan
  3. Do dai lo dap an  -> so luot khong phu thuoc vao viec ca do co bay hay khong
  4. Vi tri lo dap an  -> vi tri bay rai deu, khong dinh o cuoi
"""
import argparse
import functools
import hashlib
import io
import json
import random
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from typing import List, Optional

from src import duong_dan, ngu_lieu_viet as nl, tach_tap_viet

# Ten bay. Moi ca ghi lai minh chua nhung bay nao, de do duoc ty le loi THEO
# TUNG BAY thay vi chi mot con so chung.
BAY = ("nguoi_nha_ke_ho", "tien_su_gia_dinh", "di_ung_nguoi_nha", "luoc_chu_ngu",
       "dai_tu_ho_hang", "dinh_chinh", "dien_bien", "gia_dinh", "hoi_khong_dap",
       "nguoi_ke_benh_minh", "mau_thuan", "bo_sung", "nguon_khac_nhau",
       "lieu_dinh_chinh")

# Bay duoc RUT NGAU NHIEN. `nguoi_ke_benh_minh` co y khong nam o day: no duoc
# bat rieng trong `sinh_bo`, vi rut no qua `rng.sample` se lam loang tat ca bay
# khac (`rng.sample(BAY, k=n)` chia deu cho moi phan tu — them mot bay la moi
# bay cu mat 1/9 ty le, va the la bo moi khong con so sanh duoc voi bo cu).
# `mau_thuan` va `bo_sung` CO nam trong bo rut: chung la bay noi dung binh
# thuong nhu `dinh_chinh`, khac `nguoi_ke_benh_minh` (bay nay phu thuoc vao viec
# ca do co nguoi nha ke hay khong nen phai bat rieng).
#
# Them hai bay vao bo rut lam moi bay cu mat 2/11 ty le. Do la gia phai tra va
# no co y: hai quan he `bo sung` va `mau thuan` duoc khai trong luoc do tu dau
# ma co 0 vi du tren ca 43.687 menh de, nen chung can cho trong bo rut hon la
# tam bay cu can giu nguyen ty le.
#
# `nguon_khac_nhau` (them 11/09/2026) cung bat RIENG, cung ly do: no chi co nghia
# khi CA benh nhan lan nguoi nha cung co mat va cung noi. Rut qua `rng.sample`
# thi phan lon lan rut roi vao ca khong du dieu kien va bi bo, con moi bay cu
# van mat mot phan ty le.
#
# `lieu_dinh_chinh` (them 15/09/2026) cung KHONG nam trong bo rut: no chi co nghia
# khi hoi thoai CO nhac mot thuoc kem lieu, va viec do tu rut ngau nhien trong luc
# sinh loi thoai. Nen bay nay duoc GHI VAO `ca.bay` ngay tai cho no xay ra (xem
# `_ke_thuoc`), khong duoc chon truoc.
BAY_BAT_RIENG = ("nguoi_ke_benh_minh", "nguon_khac_nhau", "lieu_dinh_chinh")
BAY_RUT = tuple(b for b in BAY if b not in BAY_BAT_RIENG)

# Bay nao SINH RA `quan_he` trong dap an. Khai ra de phep thu doi chung
# ("ca sach thi khong co quan he nao") khong phai go tay danh sach —
# go tay thi them bay moi la doi chung am tham bo sot, va test van xanh.
BAY_SINH_QUAN_HE = ("dinh_chinh", "dien_bien", "mau_thuan", "bo_sung",
                    "nguon_khac_nhau", "lieu_dinh_chinh")

# Ty le nguoi noi tu sua LIEU ("amlodipin 5 mg, a nham, 10 mg"), tren cac lan nhac
# thuoc DU DIEU KIEN: co noi lieu, thuoc co tu hai lieu trong ngu lieu, va thuoc con
# dang dung. Loi giu lai lieu da bi sua la ke nham lieu — nhom loi 9 cua so tay.
TY_LE_LIEU_DINH_CHINH = 0.35

# Ty le ca co Y LENH THUOC cua bac si ngay trong loi thoai: ngung mot thuoc dang
# dung, hoac ke mot thuoc moi.
#
# VI SAO CO (16/09/2026). Truoc do moi menh de thuoc deu la loi NGUOI BENH ke ve
# thuoc dang dung. Thieu han hai viec co that trong buoi kham: bac si bao ngung
# thuoc, va bac si ke thuoc moi. MEDIQA-OE 2025 va n2c2 CMED 2022 deu lay dung hai
# viec do lam tac vu chinh (`Action = Stop`), nen thieu chung la thieu cho so sanh.
# Y lenh la viec CHUA XAY RA: `tinh_huong = "kế hoạch"`, va thuoc moi mang trang
# thai "được kê, chưa dùng" chu khong phai "đang dùng".
TY_LE_Y_LENH_THUOC = 0.30

# Ty le bat `nguon_khac_nhau` tren cac ca DU DIEU KIEN: benh nhan nguoi lon, co
# nguoi nha ke, benh nhan co mat, va trieu chung chinh chua mang bay
# `dinh_chinh` hay `mau_thuan` (ca ba cung nham vao mot menh de).
#
# VI SAO CAN. `cap_nhat.ap_luat` coi moi `dinh chinh` la ban sau thang ban
# truoc, bat ke AI noi. Nhung nguoi nha noi "4 ngay" roi chinh benh nhan noi "2
# ngay thoi" thi khong co can cu nao de chon mot ben. Bo sinh truoc day chi co
# mau thuan cua MOT nguoi noi (luong lu), nen luat "hai NGUON khac nhau thi
# khong tu chon ben" chua co mot vi du nao de do.
TY_LE_NGUON_KHAC_NHAU = 0.40

# Ty le bat `nguoi_ke_benh_minh` tren cac ca CO nguoi nha ke.
#
# VI SAO CAN (do ngay 10/09/2026). Menh de "nguoi nha ke ve CHINH MINH" — cho
# ca hai duong tat deu sai, "chu the = nguoi noi" sai ma "chu the = benh nhan"
# cung sai — chiem:
#
#     bo 3.000   67/3.507 menh de = 1,91%
#     bo 5.000  137/5.896 menh de = 2,32%
#
# Di tu 24 len 60 khuon, tu 1 len 5 boi canh, con so do gan nhu khong doi. Va
# trong 60 ca dung de so sanh cac nhanh: 7 menh de tren 514.
#
# HE QUA: anh huong toi da ma co che quy gan co the tao ra tren mot thuoc do
# gop la 1,36%, trong khi khoang tin cay rong 4,16%. Phep so sanh khong du cong
# suat de thay dieu no duoc dung de thay (xem `src/sai_so.canh_cong_suat`).
#
# Cho nay khong phai "mo hinh kem" hay "co che vo dung" — la BO DU LIEU gan nhu
# khong chua hien tuong ma du an noi ve.
#
# NANG 0,45 -> 0,70 ngay 11/09/2026, theo dich 1.500 menh de tang 4 o tap train.
# O 0,45 voi bo 100 khuon, tap train chi co 1.165 menh de tang 4: bo khuon lon
# hon lam doi co cau ca, va ty le tang 4 tut xuong 2,98% — duoi nguong 3% ma
# `test_ty_le_tang_4_da_tang_so_voi_muc_do_duoc_truoc_day` canh.
TY_LE_NGUOI_KE_BENH_MINH = 0.70

# ---------------------------------------------------------------- boi canh
#
# VI SAO CO BOI CANH (them 10/09/2026).
#
# Do duoc: 3.000 ca truoc do chi co **32 MACH THONG TIN** khac nhau, va nam
# mach dau chiem 52,6%. Dau va cuoi giong het nhau o 100% so ca:
#
#     BENH SU -> LY DO KHAM -> BENH SU -> [tuy chon] -> KHAM -> CHAN DOAN
#     -> KE HOACH
#
# Do moi la cho `eval_loss` xuong 10^-4, khong phai so luong benh. Them benh
# ma giu nguyen mot mach thi mo hinh van hoc thuoc CONG THUC VIET.
#
# Boi canh doi DAU va CUOI cua mach, khong chi doi tu vung:
#
#   kham_lan_dau        mach cu — kham moi, co chan doan va ke hoach
#   tai_kham            mo dau bang thuoc da ke lan truoc; THUOC DANG DUNG
#                       len dau thay vi nam giua
#   cho_ket_qua         KHONG co CHAN DOAN. Bac si noi ro chua ket luan duoc.
#                       Day la boi canh phuc vu thang thach thuc 3.
#   nguoi_nha_thay_mat  benh nhan KHONG co mat. Moi thong tin deu qua nguoi
#                       thu ba — boi canh kho nhat cho quy gan chu the.
#   dieu_duong_ban_giao dieu duong noi truoc, roi bac si vao. Ba vai nguoi noi.
BOI_CANH = ("kham_lan_dau", "tai_kham", "cho_ket_qua",
            "nguoi_nha_thay_mat", "dieu_duong_ban_giao")

# Mach cu van chiem da so: no la boi canh thuong gap nhat that, va giu no lam
# phan lon giup so lieu con so sanh duoc voi cac lan chay truoc.
TRONG_SO_BOI_CANH = (48, 16, 14, 12, 10)

MUC = ("LÝ DO KHÁM BỆNH", "BỆNH SỬ HIỆN TẠI", "TIỀN SỬ BỆNH",
       "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", "THUỐC ĐANG DÙNG", "DỊ ỨNG",
       "KHÁM LÂM SÀNG", "CHẨN ĐOÁN", "KẾ HOẠCH ĐIỀU TRỊ")

# Muc -> `thoi_gian_su_kien`. Bo sinh TU DAT muc nen no biet chac gia tri nay;
# truoc 11/09/2026 dap an khong mang truong do va `sinh_benh_an` co mot luat doc
# no, nen luat do la ma chet (xem chu thich o `MenhDe.thoi_gian_su_kien`).
#
# "chua ro" la gia tri DUNG cho ba muc duoi cung, khong phai gia tri bo qua:
#   DỊ ỨNG               di ung la mot su that thuong truc, khong co thoi diem
#   TIỀN SỬ GIA ĐÌNH     benh cua nguoi khac, thoi diem khong thuoc benh nhan
#   KẾ HOẠCH ĐIỀU TRỊ    chua xay ra; `tinh_huong = "ke hoach"` da noi dieu do
THOI_GIAN_THEO_MUC = {
    "LÝ DO KHÁM BỆNH": "hiện tại",
    "BỆNH SỬ HIỆN TẠI": "hiện tại",
    "KHÁM LÂM SÀNG": "hiện tại",
    "CHẨN ĐOÁN": "hiện tại",
    "THUỐC ĐANG DÙNG": "hiện tại",
    "TIỀN SỬ BỆNH": "quá khứ",
    "DỊ ỨNG": "chưa rõ",
    "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI": "chưa rõ",
    "KẾ HOẠCH ĐIỀU TRỊ": "chưa rõ",
}


@dataclass
class MenhDe:
    """Mot don vi thong tin, kem CHU THE THAT. Day la dap an.

    QUAN_HE VA TRANG_THAI — them 09/09/2026.

    Truoc do dap an KHONG co hai truong nay. Hau qua do duoc: `trich_train`
    day 2.231 ca cho mo hinh hoc, va trong ca 2.231 ca thi `quan_he` luon
    vang mat — tuc la 2.231 vi du am, KHONG MOT vi du duong. Mo hinh hoc dung
    thu no duoc day: khong bao gio danh dau quan he. Tren 35 hoi thoai that,
    `quan_he` bang "khong" o **282/282** phat bieu.

    Bay `dinh_chinh` va `dien_bien` VAN LUON co trong hoi thoai (337 va 339 ca
    trong tap train) — chi la dap an khong ghi lai chung. Nen day khong phai
    thieu du lieu, ma la thieu NHAN tren du lieu da co.
    """
    chu_the: str                 # "bệnh nhân" hoac ten quan he: "mẹ", "bà ngoại"...
    noi_dung: str
    muc: str
    moc_thoi_gian: Optional[str] = None
    phu_dinh: bool = False
    tinh_huong: str = "thực tế"  # thực tế | giả định | kế hoạch
    # hiện tại | quá khứ | chưa rõ — THEM 11/09/2026.
    #
    # HO LOI LAN THU TU, cung hinh voi `quan_he` (09/09). Luoc do 16 truong co
    # `thoi_gian_su_kien`, `sinh_benh_an` co luat
    #
    #     thoi_gian_su_kien == "qua khu"  ->  TIEN SU BENH
    #
    # nhung dap an KHONG CO truong nay, nen `du_lieu_trich` dong cung nhan thanh
    # "chua ro", mo hinh chi hoc duoc mot gia tri, va xuat "chua ro" o **ca 462**
    # phat bieu tren tap phat trien. Luat tren la MA CHET.
    #
    # Hau qua do duoc: muc TIEN SU BENH co 28/60 ca trong ban tham chieu va **0**
    # trong ban nhap cua moi nhanh.
    #
    # Bo sinh BIET gia tri nay — no tu dat `muc` cho tung menh de — nen day la
    # thieu nhan tren du lieu da co, khong phai thieu du lieu.
    thoi_gian_su_kien: str = "chưa rõ"
    luot: List[int] = field(default_factory=list)
    quan_he: Optional[str] = None       # bổ sung | đính chính | diễn biến | mâu thuẫn
    quan_he_voi: Optional["MenhDe"] = None   # tro thang toi ban ghi kia
    trang_thai: str = "còn hiệu lực"    # còn hiệu lực | bị thay thế | chưa giải quyết
    # chắc chắn | nghi ngờ | chưa ghi nhận — THEM 11/09/2026.
    #
    # Ho loi "khai trong luoc do ma khong bao gio co gia tri", lan thu sau (sau
    # `quan_he`, `tinh_huong`, hai quan he rong, `thoi_gian_su_kien`, va
    # `trich_dan` tim ra cung ngay). `bakeoff.LUOC_DO`, `phat_bieu.PhatBieu` va
    # `sinh_benh_an.dien_dat` deu phan biet ba muc; `du_lieu_trich` thi dong cung
    # "chac chan" vi dap an khong mang truong nay. Mo hinh CHUA BAO GIO duoc day
    # "nghi ngo" hay "chua ghi nhan" — dung truc "co / khong / chua xac dinh" ma
    # tang khoa bang chung can.
    #
    # Tach khoi `phu_dinh`: "chua thay bi bao gio" la mot cho TRONG (`chua ghi
    # nhan`), "khong" la mot khang dinh AM (`phu_dinh`). Truoc day ca hai deu la
    # `phu_dinh=True`, va ban tham chieu in ca hai thanh "Chua ghi nhan".
    do_chac_chan: str = "chắc chắn"
    # Loai phat bieu (`phat_bieu.HANH_VI`). `_Soan.ghi` tu suy tu vai nguoi noi,
    # muc va luot dung truoc; chi dat tay o nhung cho luat do khong du.
    hanh_vi: str = ""
    # Chi tiet thuoc (`phat_bieu.THUOC_KHOA`) — THEM 15/09/2026. None voi moi menh
    # de khong phai thuoc. Moi chi tiet khac None PHAI co nguyen van trong hoi thoai;
    # `tests/test_thuoc_chi_tiet.py` canh.
    thuoc: Optional[dict] = None
    # {so luot: chi so doan} — goi y DOAN nao trong luot la bang chung, cho nhung
    # menh de noi TAT ma so khop tu khong tim duoc: "con chau chua thay bi bao
    # gio" khong co chu "di ung". Khong xuat ra dap an. Xem `_trich_dan`.
    goi_y_doan: dict = field(default_factory=dict)


@dataclass
class Ca:
    ma: str
    benh: dict
    la_tre_em: bool
    goi_bn: str                  # bac si goi benh nhan la gi
    tu_xung_bn: str              # benh nhan tu xung la gi
    nguoi_ke: Optional[tuple]    # None = benh nhan tu ke; khac = (vai, goi, tu xung, quan he)
    mien: str = "bac"            # chon MOT vung cho ca cuoc, khong tron tung cau
    bay: List[str] = field(default_factory=list)
    boi_canh: str = "kham_lan_dau"   # xem BOI_CANH
    gioi_bn: Optional[str] = None    # "nam" | "nữ" — chi nguoi lon; tre em khong can
    # Loi thoai co NOI RO nguoi ke la ai cua benh nhan khong — xem `_lo_danh_tinh_nguoi_ke`.
    lo_danh_tinh: bool = False


def _hoa(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "")
    return s[:1].upper() + s[1:] if s else s


# ------------------------------------------------------------------- sinh ca

def sinh_ca(ma: str, rng: random.Random, chi_tap: Optional[str] = None,
            ep_mien: Optional[str] = None, ep_nguoi_ke: bool = False) -> Ca:
    """`chi_tap`, `ep_mien`, `ep_nguoi_ke`: chi bo thach thuc dung (xem
    `TuyChon`). Moi tuy chon van RUT dung so lan nhu khi khong dung no."""
    if chi_tap is None:
        benh = rng.choice(nl.BENH)
    else:
        bang = bang_tap_khuon()
        benh = rng.choice([b for b in nl.BENH if bang[b["ten"]] == chi_tap])
    if benh["nhom"] == "nhi":
        la_tre = True
    elif benh["nhom"] == "người lớn":
        la_tre = False
    else:
        la_tre = rng.random() < 0.35

    gioi = None
    if la_tre:
        goi_bn, tu_xung = rng.choice(nl.XUNG_HO_TRE_EM)
        # Tre em thi gan nhu luon co nguoi nha ke ho — do la thuc te phong kham.
        nguoi_ke = rng.choice(nl.NGUOI_NHA_TRE_EM) if rng.random() < 0.92 else None
    else:
        # Cach goi phai HOP khuon: co khuon chi mot gioi, mot lua tuoi.
        cho = nl.XUNG_HO_THEO_KHUON.get(benh["ten"])
        goi_bn, tu_xung = rng.choice([x for x in nl.XUNG_HO_NGUOI_LON
                                      if cho is None or x[0] in cho])
        gioi = (nl.GIOI_THEO_KHUON.get(benh["ten"]) or nl.GIOI_THEO_GOI.get(goi_bn)
                or rng.choice(["nam", "nữ"]))
        nguoi_ke = (_chon_nguoi_nha_nguoi_lon(goi_bn, gioi, rng)
                    if rng.random() < 0.22 else None)
    if ep_nguoi_ke and nguoi_ke is None:
        nguoi_ke = (rng.choice(nl.NGUOI_NHA_TRE_EM) if la_tre
                    else _chon_nguoi_nha_nguoi_lon(goi_bn, gioi, rng))

    bc = rng.choices(BOI_CANH, weights=TRONG_SO_BOI_CANH)[0]
    # `nguoi_nha_thay_mat` chi co nghia khi CO nguoi nha. Khong ep nguoc lai
    # bang cach tao nguoi nha gia: lam the thi ty le ca co nguoi nha bi lech
    # theo boi canh, va moi so lieu ve quy gan chu the deu bi nhiem.
    if bc == "nguoi_nha_thay_mat" and nguoi_ke is None:
        bc = "kham_lan_dau"

    mien = rng.choices(["bac", "nam", "trung"], weights=[45, 40, 15])[0]
    return Ca(ma=ma, benh=benh, la_tre_em=la_tre, goi_bn=goi_bn,
              tu_xung_bn=tu_xung, nguoi_ke=nguoi_ke,
              mien=ep_mien or mien, boi_canh=bc, gioi_bn=gioi)


# ------------------------------------------------------- sinh hoi thoai

class _Soan:
    """Gom luot thoai va menh de. Menh de CHI duoc ghi khi that su duoc noi ra —
    nho vay benh an khong bao gio chua thong tin khong co trong hoi thoai."""

    def __init__(self, ca: Ca, rng: random.Random, ap_phuong_ngu: bool = True,
                 ap_ngu_vuc: bool = True):
        self.ca, self.rng = ca, rng
        self.luot: List[tuple] = []
        # Loi thoai TRUOC tang ngu vuc va tang vung, cung chi so voi `luot`.
        self.luot_goc: List[str] = []
        self.menh_de: List[MenhDe] = []
        self.vung = nl.MIEN[ca.mien]
        # Cac tu phuong ngu thuc su da xuat hien trong ca nay. Ghi lai de do
        # duoc RIENG nhom co phuong ngu — khong ghi thi khong biet ca nao co.
        self.tu_phuong_ngu: List[str] = []
        self.cum_dan_thuong: List[str] = []
        # Hai bo so rieng cho hai tang ngon ngu — xem `ke`. Rut hat tu `rng` DUNG
        # MOT lan, bat ke hai tang co bat hay khong, de bat/tat mot tang khong
        # lam lech phan noi dung cua hoi thoai.
        hat = rng.getrandbits(48)
        self.rng_vung = random.Random(2 * hat + 1)
        self.rng_ngu_vuc = random.Random(2 * hat + 2)
        self.ap_phuong_ngu, self.ap_ngu_vuc = ap_phuong_ngu, ap_ngu_vuc

    def tt(self) -> str:
        """Tieu tu cho CAU HOI va CAU KE — chi "a" hoac de trong."""
        t = self.rng.choice(self.vung["ket"])
        return (" " + t) if t else ""

    def dn(self) -> str:
        """Tieu tu cho LOI DE NGHI cua bac si — "nhe", "nha", "nghen".

        Tach khoi `tt` vi gan chung vao cau hoi thi sai nga:
        "Gia dinh co ai bi benh gi khong nhe?" khong phai tieng Viet.
        """
        t = self.rng.choice(self.vung["de_nghi"])
        return (" " + t) if t else ""

    def da(self, phu_dinh: bool = False) -> str:
        """Tu dem mo dau cua BENH NHAN / NGUOI NHA, da kem dau phay.

        Khong bao gio la "Ừ" hay "Rồi" — do la loi nguoi tren noi voi nguoi
        duoi, benh nhan khong dung voi bac si.

        CHI khi TRA LOI nhan vien y te (sua 11/09/2026). Noi tiep luot cua chinh
        minh ma mo bang "Vang," thi nhu tu dap loi minh — ban minh hoa co "Vang,
        toi dang dieu tri loet ta trang" ngay sau mot luot cua chinh nguoi do.
        """
        if self.luot and self.luot[-1][0] not in self.VAI_NHAN_VIEN:
            return ""
        cac = self.vung["da_vang"]
        if phu_dinh:
            # "Vang, khong a" nghe nhu vua dong y vua phu nhan: cau tra loi PHU
            # DINH mo bang "Da".
            cac = [c for c in cac if not c.startswith("Vâng")] or ["Dạ"]
        return self.rng.choice(cac) + ", "

    # Nhan vien y te trong LOI THOAI cua bo sinh — viet hoa, dung nhu dau luot.
    VAI_NHAN_VIEN = ("Bác sĩ", "Điều dưỡng")

    def noi(self, vai: str, cau: str, cau_goc: Optional[str] = None) -> int:
        """`cau_goc`: loi thoai TRUOC tang ngu vuc va tang vung (chi `ke` truyen).
        Giu lai de tim doan bang chung bang THUAT NGU CHUAN — xem `_trich_dan`."""
        self.luot.append((vai, cau.strip()))
        self.luot_goc.append((cau if cau_goc is None else cau_goc).strip())
        return len(self.luot)

    def bs(self, cau: str) -> int:
        return self.noi("Bác sĩ", cau)

    def nguoi_ke_vai(self) -> str:
        return "Người nhà" if self.ca.nguoi_ke else "Bệnh nhân"

    def ke(self, cau: str, vai: Optional[str] = None) -> int:
        """Loi cua BENH NHAN hoac NGUOI NHA — co the mang tu phuong ngu.

        CHI thay o day, khong thay trong `bs()`: bac si duoc dao tao noi chuan,
        va tron lai thi mat mot dau hieu that trong hoi thoai kham benh.

        DAP AN KHONG DOI. Hoi thoai viet "lu du", `ghi()` van ghi "met".
        Do chinh la phep thu: mo hinh co quy duoc ve khai niem chuan khong.
        Tru cum khong dong nghia ("nong ham hap" — chua do nhiet do thi chua phai
        "sot"): `_giu_loi_nguoi_noi` doi noi dung ve loi nguoi noi sau khi ghi.

        `vai`: mac dinh la nguoi dang ke (`nguoi_ke_vai`). Bay `nguon_khac_nhau`
        can benh nhan chen vao trong mot ca do nguoi nha ke.

        HAI BO SO NGAU NHIEN RIENG, va TANG NGU VUC CHAY TRUOC — doi 11/09/2026.
        Truoc day hai tang dung chung `self.rng` voi phan NOI DUNG, nen moi lan
        tang vung quyet dinh doi hay khong la mot lan rut so cua ca hoi thoai: tat
        phuong ngu la doi luon benh, bay va moc thoi gian cua moi luot sau do.
        Phep thu "cung mot ca, co va khong co phuong ngu" (`thach_thuc`) can hai
        ban giong het nhau tru DUNG cac tu phuong ngu. Tang ngu vuc chay truoc,
        tren cau goc, nen quyet dinh cua no giong nhau o ca hai ban.
        """
        cau_goc = cau
        if self.ap_ngu_vuc:
            from src import loi_dan_thuong
            cau, da_doi_nv = loi_dan_thuong.doi_sang_dan_thuong(
                cau, self.rng_ngu_vuc)
            self.cum_dan_thuong.extend(t for t, _c in da_doi_nv)
        if self.ap_phuong_ngu and self.ca.mien in ("nam", "trung"):
            from src import phuong_ngu
            cau, da_doi = phuong_ngu.doi_sang_phuong_ngu(cau, self.ca.mien,
                                                         self.rng_vung)
            self.tu_phuong_ngu.extend(d for _c, d in da_doi)
        # Viet hoa chu dau SAU hai tang ngon ngu: `da()` co the tra ve rong, va cau
        # luoc chu ngu khi do bat dau bang chu thuong ("con ho nua a").
        return self.noi(vai or self.nguoi_ke_vai(), _hoa(cau), cau_goc=_hoa(cau_goc))

    def ghi(self, chu_the, noi_dung, muc, luot, doan=None, kem_cau_hoi=False,
            **kw):
        """Ghi mot menh de va TRA VE chinh no.

        Tra ve la can thiet, khong phai tien nghi: bay `dinh_chinh` truoc day
        lay muc tieu bang `menh_de[0]`, ngam gia dinh menh de dau tien luon la
        trieu chung chinh. Boi canh `tai_kham` ghi mot menh de THUOC len truoc,
        va the la bay dinh chinh sua nham vao thuoc — sinh ra
        "dang dung panadol (nam hom)" doi voi "dang dung panadol".
        Test `test_dinh_chinh_chi_giu_moc_da_sua` bat duoc.

        `doan`: goi y doan nao trong luot DAU cua `luot` la bang chung — chi dung
        o cho menh de noi TAT, so khop tu khong tu tim duoc. Xem `_trich_dan`.

        `kem_cau_hoi`: them luot ngay truoc (cau hoi cua nhan vien y te) vao bang
        chung. Dung cho cau tra loi TAT — "Da, khong a" tu no khong mang noi dung,
        cap hoi–dap moi du nghia. `bakeoff.HUONG_DAN` day dung dieu do tu dau
        ("Cap cau hoi–cau tra loi can ca hai luot"), nhung nhan thi chi ghi luot
        tra loi: hai cho cua cung mot du an noi hai dieu.
        """
        # `thoi_gian_su_kien` suy tu MUC, vi bo sinh tu dat muc nen no biet chac.
        # Cho phep ghi de qua `kw` — bay `dien_bien` can dat tay.
        kw.setdefault("thoi_gian_su_kien", THOI_GIAN_THEO_MUC.get(muc, "chưa rõ"))
        cac_luot = [luot] if isinstance(luot, int) else list(luot)
        dau = cac_luot[0]
        kw.setdefault("hanh_vi", self._hanh_vi(dau, muc,
                                               kw.get("tinh_huong", "thực tế")))
        if (kem_cau_hoi and dau >= 2
                and self.luot[dau - 2][0] in self.VAI_NHAN_VIEN):
            cac_luot = [dau - 1] + cac_luot
        md = MenhDe(chu_the=chu_the, noi_dung=noi_dung, muc=muc,
                    luot=cac_luot, **kw)
        if doan is not None:
            md.goi_y_doan[dau] = doan
        self.menh_de.append(md)
        return md

    def _hanh_vi(self, so_luot, muc, tinh_huong):
        """Loai phat bieu, suy tu VAI nguoi noi luot `so_luot` va luot DUNG TRUOC.

            nhan vien y te    KHAM LAM SANG -> quan sat; ke hoach, gia dinh ->
                              ke hoach; con lai -> nhan dinh
            benh nhan / nha   luot truoc cua nhan vien y te -> tra loi; con lai
                              -> tu ke
        """
        vai = self.luot[so_luot - 1][0]
        if vai in self.VAI_NHAN_VIEN:
            if muc == "KHÁM LÂM SÀNG":
                return "quan sát"
            if tinh_huong in ("kế hoạch", "giả định"):
                return "kế hoạch"
            return "nhận định"
        truoc = self.luot[so_luot - 2][0] if so_luot >= 2 else None
        return "trả lời" if truoc in self.VAI_NHAN_VIEN else "tự kể"


def _chon_nguoi_nha_nguoi_lon(goi_bn: str, gioi: str, rng: random.Random) -> tuple:
    """(vai, tu bac si goi ho, tu ho tu xung, quan he) KHOP lua tuoi va gioi cua
    benh nhan — xem `nl.LUA_TUOI_THEO_GOI`. Benh nhan tre: vo/chong hoac bo me;
    trung nien, cao tuoi: vo/chong hoac con. Khong con ong ba ke ho nguoi lon.

    Tu xung khop voi cach bac si goi ho: goi "chi"/"anh" thi xung "em" hoac "toi",
    goi "chau" thi xung "chau" — bang cu co con gai bac si goi "chi" ma xung "chau".
    """
    tuoi = nl.LUA_TUOI_THEO_GOI[goi_bn]
    loai = rng.choice(["vo_chong", "vo_chong", "bo_me"] if tuoi == "trẻ"
                      else ["vo_chong", "con"])
    if loai == "vo_chong":
        vai = "vợ" if gioi == "nam" else "chồng"
        goi = nl.VO_CHONG_GOI[goi_bn]
        tx = "em" if goi == "em" else (rng.choice(["em", "tôi"]) if goi in ("anh", "chị")
                                       else "tôi")
        return (vai, goi, tx, vai)
    if loai == "bo_me":
        vai = rng.choice(["mẹ", "bố"])
        goi = rng.choice(["cô", "bác"] if vai == "mẹ" else ["chú", "bác"])
        return (vai, goi, "tôi", vai)
    vai = rng.choice(["con gái", "con trai"])
    if tuoi == "trung niên" or goi_bn == "bác":
        goi, tx = rng.choice([("cháu", "cháu"), ("em", "em")])
    else:
        goi, tx = ("chị" if vai == "con gái" else "anh"), rng.choice(["em", "tôi"])
    return (vai, goi, tx, vai)


def _cach_goi_bn_trong_loi_nguoi_ke(ca: Ca, rng: random.Random) -> str:
    """Nguoi nha goi benh nhan la gi khi ke — THEO quan he, va THEO chinh tu ho tu
    xung: da xung "toi" thi la "chau nha toi", "con toi", khong phai "chau nha em".

    SUA 11/09/2026. Ban cu rut chung {"chau", "be", "con", "chau no", "be nha em"}
    cho moi nguoi ke benh nhi, va {goi bac si, "nha em", "ong ay", "ba ay"} cho moi
    nguoi ke benh nhan nguoi lon. Nen ba noi goi chau trai la "anh", bo xung "toi"
    ma goi con la "be nha em", va "nha em" — cach VO CHONG goi nhau — roi vao mieng
    ong ba, bo me, con cai. Nguoi dung doc ban minh hoa: "khong ai noi nhu nay ca".

    Bay `dai_tu_ho_hang` van con: "chau" vua la cach ong ba, bo me goi benh nhi,
    vua la cach con cai xung voi bac si (`nl.NGUOI_NHA`, `_chon_nguoi_nha_nguoi_lon`).
    """
    if not ca.nguoi_ke:
        return ca.tu_xung_bn                      # benh nhan tu ke — khong dung toi
    _vai, _goi, tx, qh = ca.nguoi_ke
    if ca.la_tre_em:
        if qh in ("mẹ", "bố"):
            return rng.choice(["cháu", "cháu nó", f"cháu nhà {tx}", f"bé nhà {tx}",
                               f"con {tx}"])
        return rng.choice(["cháu", "cháu nó", f"cháu {tx}"])          # ong ba
    gia = nl.LUA_TUOI_THEO_GOI[ca.goi_bn] == "cao tuổi"
    nam = ca.gioi_bn == "nam"
    if qh in ("vợ", "chồng"):
        if gia:
            return rng.choice([f"{'ông' if nam else 'bà'} nhà {tx}", f"nhà {tx}",
                               "ông ấy" if nam else "bà ấy"])
        if nam:                                   # vo ke ve chong
            return rng.choice([f"nhà {tx}", f"chồng {tx}", "anh ấy"])
        return rng.choice([f"nhà {tx}", f"vợ {tx}"])   # chong ke ve vo
    if qh in ("con gái", "con trai"):
        # Con goi cha me gia la "ong cu/ba cu nha em", KHONG "ba ay" — nghe xa cach.
        bo_me = "bố" if nam else "mẹ"
        return rng.choice([f"{bo_me} {tx}"] +
                          ([f"{'ông' if nam else 'bà'} cụ nhà {tx}"] if gia else []))
    return rng.choice(["cháu", "cháu nó", f"con {tx}", f"cháu nhà {tx}"])  # bo me


# Ty le ca co nguoi nha ma loi thoai NOI RO nguoi do la ai cua benh nhan.
#
# VI SAO CO (15/09/2026). Truoc do bo sinh ghi thang quan he that cua nguoi ke
# ("bo", "ba ngoai"...) vao `chu_the` cua dap an va vao ban tham chieu, BAT KE loi
# thoai co lo ra hay khong. Cau mo dau chi mang TU XUNG HO ("anh", "ba"), ma xung
# ho khong xac dinh duoc quan he: "ba" la ba noi hay ba ngoai, "anh" la chong hay
# con trai; va hai mau mo dau ("Hom nay be sao roi?", "Lan truoc toi ke...") khong
# lo gi ca. Do tren tap train the he 6: 256/1.416 menh de (18,1%) gan dich danh cho
# nguoi ke ma khong co manh moi nao. Ca nhanh A lan khau trich deu bi day DOAN mot
# thong tin khong ai noi — dung lo~i ma du an dung ra de chan.
#
# Bat bien tu nay: quan he GHI DICH DANH trong dap an  <=>  quan he CO trong loi
# thoai. Con lai ghi "nguoi nha". `tests/test_lo_danh_tinh.py` canh.
TY_LE_LO_DANH_TINH = 0.6


def _ten_nguoi_ke(ca: Ca) -> str:
    """Ten ghi vao `chu_the` cho thong tin CUA CHINH nguoi dang ke."""
    return ca.nguoi_ke[3] if (ca.nguoi_ke and ca.lo_danh_tinh) else "người nhà"


def _lo_danh_tinh_nguoi_ke(s, ca: Ca, rng: random.Random) -> None:
    """Voi xac suat TY_LE_LO_DANH_TINH, chen mot cap hoi - dap noi RO quan he.

    Rut so voi MOI ca, ke ca ca khong chen — de hai ban cua mot cap
    thach thuc di cung mot duong rut so. Cap nay KHONG sinh menh de: no chi lam cho
    ten ghi trong dap an co can cu trong loi thoai."""
    ca.lo_danh_tinh = False
    if rng.random() >= TY_LE_LO_DANH_TINH:
        return
    if not ca.nguoi_ke:
        # Ca KHONG co nguoi nha cung nhan mot cap cung do dai, cung xac suat.
        # Chen rieng cho ca co nguoi nha thi so luot lai lo bay: cac bay can nguoi
        # nha (`di_ung_nguoi_nha`, `nguon_khac_nhau`) don ve nhom dai hon —
        # `test_do_dai_KHONG_lo_ca_nao_co_bay` da bao do (0,755 > 0,72).
        s.bs(f"{_hoa(ca.goi_bn)} đi khám cho mình phải không ạ?")
        s.ke(f"{s.da()}{ca.tu_xung_bn} khám cho {ca.tu_xung_bn} ạ.")
        return
    ca.lo_danh_tinh = True
    bn3 = _bn_ngoi_ba(ca)
    s.bs(f"{_hoa(ca.nguoi_ke[1])} là gì của {bn3} ạ?")
    s.ke(f"{s.da()}{ca.nguoi_ke[2]} là {ca.nguoi_ke[3]} của {bn3} ạ.")


def _duong_dung_cua(ca: Ca, ten: str) -> str:
    """Duong dung cua mot thuoc theo ngu lieu; thuoc khong co trong bang chi tiet
    (ten thuong mai trong `nl.THUOC`) thi la thuoc uong."""
    bang = nl.THUOC_CHI_TIET_TRE_EM if ca.la_tre_em else nl.THUOC_CHI_TIET_NGUOI_LON
    return bang[ten][0] if ten in bang else "uống"


def _thuoc(ten, duong, trang, lieu=None, so_lan=None, bat_dau=None, ngung=None):
    """Tu dien `thuoc` DU MOI KHOA — chi tiet khong noi thi la None, khong bo khoa."""
    return {"ten": ten, "lieu": lieu, "so_lan": so_lan, "duong_dung": duong,
            "bat_dau": bat_dau, "ngung": ngung, "trang_thai_dung": trang}


def _ke_thuoc(s, ca: Ca, rng: random.Random, chu: str, tt) -> None:
    """Nguoi benh (hoac nguoi nha) ke MOT thuoc, kem mot phan chi tiet — them 15/09/2026.

    Moi chi tiet (lieu, so lan, luc bat dau) co mat HAY VANG MAT doc lap: vang mat
    thi dap an ghi None. Mo hinh phai hoc rang KHONG noi thi KHONG ghi — neu chi tiet
    luon co mat, no se hoc luon dien lieu, ke ca khi khong ai noi.

    Rut DU MOI SO truoc khi quyet dinh dung so nao, de hai ban cua mot cap thach thuc
    di cung mot duong rut so (cung le voi `_lo_danh_tinh_nguoi_ke`).

    Ba bien the:
      dang dung            "co uong amlodipin 5 mg, ngay mot lan buoi sang, dung duoc ba thang nay"
      da ngung             "truoc co uong omeprazole 20 mg, ngung 2 tuan roi" -> TIEN SU BENH
      tu sua lieu          "co uong amlodipin 5 mg, a nham, 10 mg moi dung" -> hai menh de,
                           ban 5 mg `bi thay the`, ban 10 mg `dinh chinh` ban kia
    """
    bang = nl.THUOC_CHI_TIET_TRE_EM if ca.la_tre_em else nl.THUOC_CHI_TIET_NGUOI_LON
    ten = rng.choice(sorted(bang))
    duong, cac_lieu, cac_lan = bang[ten]
    lieu, so_lan = rng.choice(cac_lieu), rng.choice(cac_lan)
    bat_dau = rng.choice(nl.BAT_DAU_THUOC)
    co_lieu, co_lan, co_bat_dau = rng.random() < 0.7, rng.random() < 0.7, rng.random() < 0.5
    da_ngung = rng.random() < 0.2
    sua = rng.random() < TY_LE_LIEU_DINH_CHINH
    tuan = rng.randint(1, 4)
    lieu_moi = rng.choice([x for x in cac_lieu if x != lieu] or [lieu])

    lieu = lieu if co_lieu else None
    so_lan = so_lan if co_lan else None
    # "dung duoc hai tuan nay" roi "ngung 2 tuan roi" la hai moc nghich nhau.
    bat_dau = bat_dau if (co_bat_dau and not da_ngung) else None
    sua = sua and lieu is not None and lieu_moi != lieu and not da_ngung

    dau = f"{ten} {lieu}" if lieu else ten
    if sua:
        # "a nham" chu khong "a khong": tu "khong" trong doan dan lam khoa bang chung
        # canh bao phu dinh cho mot cau khong he phu dinh.
        dau = f"{ten} {lieu}, à nhầm, {lieu_moi} mới đúng"
    phan = [dau] + ([so_lan] if so_lan else []) + (
        [f"dùng được {bat_dau}"] if bat_dau else [])

    if da_ngung:
        ngung = f"{tuan} tuần"
        l = s.ke(f"{s.da()}trước {chu}có {duong} {', '.join(phan)}, "
                 f"ngừng {ngung} rồi{tt()}.")
        s.ghi("bệnh nhân", f"từng dùng {ten}, đã ngừng {ngung}", "TIỀN SỬ BỆNH", l,
              thuoc=_thuoc(ten, duong, "đã ngừng", lieu=lieu, so_lan=so_lan,
                           ngung=ngung))
        return

    l = s.ke(f"{s.da()}{chu}có {duong} {', '.join(phan)}{tt()}.")
    thuoc = _thuoc(ten, duong, "đang dùng", lieu=lieu, so_lan=so_lan, bat_dau=bat_dau)
    md = s.ghi("bệnh nhân", ten, "THUỐC ĐANG DÙNG", l, thuoc=thuoc)
    if not sua:
        return
    # Cung cach voi bay `dinh_chinh`: GIU ban cu, danh dau bi thay the, chen ban moi
    # truoc no. Ban moi dung MenhDe truc tiep nen phai chep tay moi truong `ghi` dat.
    md.trang_thai = "bị thay thế"
    moi = MenhDe(chu_the=md.chu_the, noi_dung=md.noi_dung, muc=md.muc,
                 phu_dinh=md.phu_dinh, tinh_huong=md.tinh_huong, luot=list(md.luot),
                 # Moi ban dinh chinh la "tu ke" (`phat_bieu.HANH_VI`): khong ai hoi
                 # nguoi noi sua lai. `test_menh_de_tao_tay_mang_DU_nhan_nhu_ban_goc`.
                 quan_he="đính chính", quan_he_voi=md, hanh_vi="tự kể",
                 thoi_gian_su_kien=md.thoi_gian_su_kien,
                 do_chac_chan=md.do_chac_chan, thuoc=dict(thuoc, lieu=lieu_moi))
    s.menh_de.insert(s.menh_de.index(md), moi)
    ca.bay = sorted(set(ca.bay) | {"lieu_dinh_chinh"})


def _y_lenh_thuoc(s, ca: Ca, rng: random.Random, tt) -> None:
    """Bac si ra y lenh ve thuoc ngay trong loi thoai — them 16/09/2026.

    Hai bien the, deu la viec CHUA XAY RA nen `tinh_huong = "kế hoạch"`:
      ngung   "Từ hôm nay ngừng uống amlodipin nhé."   -> trang_thai_dung "đã ngừng"
      ke moi  "Tôi kê omeprazole 20 mg, uống ngày một lần trước ăn sáng nhé."
              -> trang_thai_dung "được kê, chưa dùng"

    Bien the "ngung" chi chon duoc khi trong ca DA co mot thuoc dang dung, nen no
    tao ra mot cap doi lap trong cung mot ca: cung ten thuoc, mot ban "đang dùng"
    (loi nguoi benh) va mot ban "đã ngừng" (y lenh bac si). Ghi nham hai ban nay
    thanh mot la dung lo~i "thuoc da ngung ghi thanh dang dung".

    Rut DU MOI SO truoc khi re nhanh, de hai ban cua mot cap thach thuc di cung mot
    duong rut so — cung le voi `_ke_thuoc`.
    """
    bang = nl.THUOC_CHI_TIET_TRE_EM if ca.la_tre_em else nl.THUOC_CHI_TIET_NGUOI_LON
    ten_moi = rng.choice(sorted(bang))
    duong_moi, cac_lieu, cac_lan = bang[ten_moi]
    lieu, so_lan = rng.choice(cac_lieu), rng.choice(cac_lan)
    co_y_lenh = rng.random() < TY_LE_Y_LENH_THUOC
    chon_ngung = rng.random() < 0.5
    if not co_y_lenh:
        return
    dang_dung = [m for m in s.menh_de
                 if m.thuoc and m.thuoc.get("trang_thai_dung") == "đang dùng"]
    if dang_dung and chon_ngung:
        md = dang_dung[-1]
        ten, duong = md.thuoc["ten"], md.thuoc["duong_dung"]
        # KHONG viet "khong ... nua": tu phu dinh trong doan dan lam khoa bang chung
        # canh bao phu dinh cho mot cau khong he phu dinh.
        l = s.bs(f"Từ hôm nay ngừng {duong} {ten} nhé{tt()}.")
        s.ghi("bệnh nhân", f"ngừng {ten}", "KẾ HOẠCH ĐIỀU TRỊ", l,
              tinh_huong="kế hoạch", thuoc=_thuoc(ten, duong, "đã ngừng"))
        return
    l = s.bs(f"Tôi kê {ten_moi} {lieu}, {duong_moi} {so_lan} nhé{tt()}.")
    s.ghi("bệnh nhân", f"kê {ten_moi}", "KẾ HOẠCH ĐIỀU TRỊ", l,
          tinh_huong="kế hoạch",
          thuoc=_thuoc(ten_moi, duong_moi, "được kê, chưa dùng", lieu=lieu,
                       so_lan=so_lan))


def _bn_ngoi_ba(ca: Ca) -> str:
    """Bac si noi VE benh nhan voi nguoi nha — ngoi thu ba. Khong bao gio muon cach
    goi cua nguoi nha: truoc 11/09/2026 bac si noi "be nha em khong den duoc a?",
    "Neu mai be nha em con..." — 218 luot bac si o tap train mang "nha em"."""
    if ca.la_tre_em:
        return "cháu" if ca.goi_bn == "con" else ca.goi_bn
    return f"{ca.goi_bn} ấy"


@dataclass
class TuyChon:
    """Tuy chon cho MOT ca — chi dung cho cac bo thach thuc (`src.thach_thuc`).

    Mac dinh cho ra DUNG bo du lieu chinh. Moi tuy chon phai giu nguyen duong
    rut so cua `rng` so voi ban cap cua no, de hai ban cua mot cap chi khac
    nhau o DUNG dieu dang do — co test canh.
    """
    chi_tap: Optional[str] = None       # chi rut khuon cua tap nay
    ep_mien: Optional[str] = None       # "bac" | "nam" | "trung"
    ep_bay: tuple = ()                  # bay BAT BUOC them vao ca
    ep_nguoi_ke: bool = False           # bat buoc co nguoi nha ke
    ap_phuong_ngu: bool = True
    ap_ngu_vuc: bool = True
    di_ung_cua_nguoi_ke: bool = False   # bay di ung nguoi nha: luon la nguoi ke
    doi_chu_the: bool = False           # dao nguoi mang di ung — xem bay di ung


def _muc_chan_doan(cd: str):
    """Chan doan cua khuon -> (noi dung, do chac chan).

    "Theo doi X" DAU cau la cach bac si ghi chan doan TAM (nghi X); "... nghi ..."
    la nghi ngo ("Viem hong nghi do lien cau"). Truoc 11/09/2026 ca hai mang nhan
    "chac chan" — tang khoa bang chung chi ra: 447 phat bieu chan doan cua tap
    train NOI mot dang, NHAN mot neo. "X, theo doi" (chan doan chac kem ke hoach
    theo doi) giu "chac chan".
    """
    cd = cd.strip().rstrip(".")
    m = re.match(r"theo dõi\s+", cd, re.I)
    if m:
        return cd[m.end():], "nghi ngờ"
    if re.search(r"(?<!\w)nghi(?!\w)", cd, re.I):
        return cd, "nghi ngờ"
    return cd, "chắc chắn"


def sinh_hoi_thoai(ca: Ca, rng: random.Random, tuy: Optional[TuyChon] = None):
    # Ten `tuy`, KHONG phai `tc`: than ham nay dung `tc` cho trieu chung cua bay
    # dien bien, va mot ten trung se de len tuy chon o giua ham.
    tuy = tuy or TuyChon()
    s = _Soan(ca, rng, ap_phuong_ngu=tuy.ap_phuong_ngu,
              ap_ngu_vuc=tuy.ap_ngu_vuc)
    tt = s.tt
    benh = ca.benh
    # Hai cach goi KHAC NHAU cho cung mot benh nhan:
    #   goi_bn_trong_loi — nguoi nha goi con minh ("bé nhà em", "cháu nó")
    #   ca.goi_bn        — bac si goi benh nhan ("bé", "cháu", "con")
    # Tron hai cai nay lam bac si noi giong nguoi me, nghe sai ngay.
    goi_bn_trong_loi = _cach_goi_bn_trong_loi_nguoi_ke(ca, rng)

    # --- mo dau, khac nhau theo BOI CANH
    if ca.boi_canh == "dieu_duong_ban_giao":
        # Vai thu ba. `nguoi_noi` cua luoc do co san "dieu duong", nhung truoc
        # 10/09/2026 khong hoi thoai nao dung toi — nen mo hinh chua bao gio
        # gap mot ca co ba nguoi noi.
        s.noi("Điều dưỡng", f"Em chào bác sĩ. {_hoa(ca.goi_bn)} này "
                            f"{rng.choice(['vào từ sáng', 'mới đăng ký khám', 'chờ từ nãy'])}"
                            f", em đã đo sinh hiệu rồi ạ.")
        s.bs(f"Cảm ơn em. {_hoa(ca.goi_bn)} kể tôi nghe xem thế nào{tt()}.")
    elif ca.boi_canh == "tai_kham":
        thuoc_cu = rng.choice(nl.THUOC_TRE_EM if ca.la_tre_em else nl.THUOC)
        s.bs(f"Lần trước tôi kê {thuoc_cu} cho "
             f"{ca.goi_bn if not ca.nguoi_ke else _bn_ngoi_ba(ca)}, "
             f"dùng thấy thế nào{tt()}?")
        # DONG TU theo duong dung (15/09/2026): truoc do moi thuoc deu "uong", ke ca
        # salbutamol la thuoc xit.
        duong = _duong_dung_cua(ca, thuoc_cu)
        # Ghi lai thuoc dang dung NGAY O DAU. O mach cu, THUOC DANG DUNG luon
        # nam giua; day la mot trong nhung cho lam mach bi deu.
        if rng.random() < 0.55:
            l = s.ke(f"{s.da()}vẫn đang {duong} {thuoc_cu}{tt()}.")
            s.ghi("bệnh nhân", f"đang dùng {thuoc_cu}", "THUỐC ĐANG DÙNG", l,
                  thuoc=_thuoc(thuoc_cu, duong, "đang dùng"))
        else:
            tuan = rng.randint(1, 4)
            l = s.ke(f"{s.da()}{duong} được ít hôm rồi ngừng, "
                     f"ngừng {tuan} tuần rồi{tt()}.")
            # Cau tra loi KHONG nhac ten thuoc — ten nam o cau hoi cua bac si ngay
            # truoc, nen bang chung phai gom ca cap hoi–dap (15/09/2026: 0 luot dan
            # nao chua ten thuoc truoc khi them `kem_cau_hoi`).
            s.ghi("bệnh nhân", f"từng dùng {thuoc_cu}, đã ngừng {tuan} tuần",
                  "TIỀN SỬ BỆNH", l, kem_cau_hoi=True,
                  thuoc=_thuoc(thuoc_cu, duong, "đã ngừng", ngung=f"{tuan} tuần"))
    elif ca.boi_canh == "nguoi_nha_thay_mat":
        # Benh nhan KHONG co mat. Moi thong tin deu di qua nguoi thu ba, nen
        # duong tat "chu the chinh la nguoi vua noi" luon SAI o boi canh nay.
        s.bs(f"Hôm nay {ca.nguoi_ke[1]} đi một mình à, "
             f"{_bn_ngoi_ba(ca)} không đến được{tt()}?")
        s.ke(f"{s.da()}{goi_bn_trong_loi} mệt quá nên "
             f"{ca.nguoi_ke[2]} đi thay{tt()}.")
    elif ca.nguoi_ke:
        mau = rng.choice(nl.MO_DAU_NGUOI_NHA)
        s.bs(mau.format(goi_nn=ca.nguoi_ke[1], goi_nn_hoa=_hoa(ca.nguoi_ke[1]),
                        goi_bs=ca.goi_bn, goi_bs_hoa=_hoa(ca.goi_bn), tt=tt()))
    else:
        mau = rng.choice(nl.MO_DAU)
        s.bs(mau.format(goi=ca.goi_bn, goi_hoa=_hoa(ca.goi_bn), tt=tt()))

    _lo_danh_tinh_nguoi_ke(s, ca, rng)
    _xa_giao(s, ca, rng)

    # --- trieu chung chinh
    chinh = benh["chinh"][0]
    # Moc thoi gian phai hop DIEN TIEN cua benh. "Sot nua thang" roi chan
    # doan "cum mua" la mot ca ma bac si doc qua la thay sai.
    moc = rng.choice(nl.MOC_MAN if benh["dien_tien"] == "mạn" else nl.MOC_CAP)
    if "luoc_chu_ngu" in ca.bay:
        # Khong co chu ngu — nguoi doc phai suy ra tu ngu canh. Day la dang cau
        # RAT thuong gap trong tieng Viet noi va gan nhu vang mat trong ban dich.
        cau = f"{s.da()}{chinh} {moc} rồi{tt()}."
    elif ca.nguoi_ke:
        cau = f"{s.da()}{goi_bn_trong_loi} {chinh} {moc} rồi{tt()}."
    else:
        cau = f"{s.da()}{ca.tu_xung_bn} {chinh} {moc} rồi{tt()}."
    l = s.ke(cau)
    md_chinh = s.ghi("bệnh nhân", chinh, "BỆNH SỬ HIỆN TẠI", l, moc_thoi_gian=moc)
    s.ghi("bệnh nhân", chinh, "LÝ DO KHÁM BỆNH", l)

    # --- BAY HAI NGUON NOI KHAC NHAU (them 11/09/2026)
    #
    # Nguoi nha vua ke moc, roi CHINH benh nhan noi khac. Khac `mau_thuan` o cho
    # hai ban den tu HAI NGUOI: khong ai tu sua ai, nen khong co can cu nao de
    # chon mot ben — ca hai `chua giai quyet`, bac si ghi la chua ro. Day la vi
    # du cho luat "hai nguon khac nhau thi khong tu chon ben" cua tang do thi
    # trang thai (`cap_nhat`). Dieu kien bat nam o `sinh_bo`.
    if "nguon_khac_nhau" in ca.bay:
        ro = nl.MOC_MAN if benh["dien_tien"] == "mạn" else nl.MOC_CAP
        moc_khac = rng.choice([m for m in ro if m != moc])
        tx_bn = ca.tu_xung_bn
        l2 = s.ke(rng.choice([
            f"Không đúng đâu, {tx_bn} {chinh} {moc_khac} rồi{tt()}.",
            f"Theo {tx_bn} thì {moc_khac} mới đúng{tt()}.",
        ]), vai="Bệnh nhân")
        # Moi ban giu LUOT CUA CHINH NO, khong gop hai luot nhu bay `mau_thuan`:
        # o day hai ban do HAI nguoi noi, va phep do chia tang theo nguoi noi
        # cua luot bang chung — gop lai thi ban cua nguoi nha mang luot cua
        # benh nhan va bi xep sai tang.
        cu = md_chinh
        cu.trang_thai = "chưa giải quyết"
        moi = MenhDe(chu_the="bệnh nhân", noi_dung=chinh, muc=cu.muc,
                     moc_thoi_gian=moc_khac, luot=[l2],
                     quan_he="mâu thuẫn", quan_he_voi=cu,
                     trang_thai="chưa giải quyết", hanh_vi="tự kể",
                     thoi_gian_su_kien=cu.thoi_gian_su_kien)
        s.menh_de.insert(s.menh_de.index(cu) + 1, moi)
        s.bs(f"Để tôi ghi là chưa rõ {moc} hay {moc_khac}, "
             f"mình xác nhận lại sau nhé{tt()}.")

    # --- dinh chinh (neu co): sua lai chinh con so vua noi
    if "dinh_chinh" in ca.bay:
        ro = nl.MOC_MAN if benh["dien_tien"] == "mạn" else nl.MOC_CAP
        moc_moi = rng.choice([m for m in ro if m != moc])
        # Nguoi noi tu xung BANG DUNG tu ho dung o cac luot khac. Ban dau boc
        # ngau nhien "em nham" / "toi nho nham" nen mot ong bo luc xung "toi"
        # luc xung "em" trong cung mot cuoc — doc la thay gia ngay.
        tx = ca.nguoi_ke[2] if ca.nguoi_ke else ca.tu_xung_bn
        # Ba cach noi, cung mot khuon "X chu khong phai Y" — them hai cach sau
        # ngay 11/09/2026 de bai kiem tra dinh chinh khong chi bat mot cum "a
        # khong".
        l2 = s.ke(rng.choice([
            f"À không, {tx} {rng.choice(['nhầm', 'nhớ nhầm', 'nói nhầm'])}, "
            f"{moc_moi} chứ không phải {moc}{tt()}.",
            f"Xin lỗi bác sĩ, {tx} nhớ lại rồi, {moc_moi} chứ không phải "
            f"{moc}{tt()}.",
            f"{_hoa(tx)} nói lại cho đúng, {moc_moi} chứ không phải {moc}{tt()}.",
        ]))
        # GIU ban cu, danh dau "bi thay the", va them mot ban MOI mang moc da
        # sua. Truoc day cho nay sua thang `moc_thoi_gian` cua ban cu — benh an
        # ra dung, nhung dap an mat sach dau vet cua viec dinh chinh, nen khong
        # co gi de mo hinh hoc va khong co gi de do.
        #
        # Ban moi phai chen vao DAU danh sach, khong duoc them vao cuoi: thu tu
        # menh de quyet dinh thu tu cum trong muc BENH SU HIEN TAI cua benh an
        # tham chieu. Them vao cuoi thi benh an doi chu, va moi con so ROUGE do
        # truoc day het so sanh duoc.
        # Muc tieu la menh de TRIEU CHUNG CHINH, giu bang tham chieu tuong
        # minh. Khong dung `menh_de[0]` — boi canh `tai_kham` ghi mot menh de
        # thuoc len truoc no.
        cu = md_chinh
        cu.luot.append(l2)
        cu.trang_thai = "bị thay thế"
        moi = MenhDe(chu_the=cu.chu_the, noi_dung=cu.noi_dung, muc=cu.muc,
                     moc_thoi_gian=moc_moi, phu_dinh=cu.phu_dinh,
                     tinh_huong=cu.tinh_huong, luot=list(cu.luot),
                     quan_he="đính chính", quan_he_voi=cu, hanh_vi="tự kể",
                     # Dung MenhDe truc tiep, khong qua `ghi`, nen phai chep
                     # tay — ban va `thoi_gian_su_kien` sang 11/09/2026 di qua
                     # `ghi` va bo sot dung ba cho nay.
                     thoi_gian_su_kien=cu.thoi_gian_su_kien)
        s.menh_de.insert(s.menh_de.index(cu), moi)

    # --- BAY MAU THUAN: hai moc XUNG NHAU, KHONG ai dinh chinh
    #
    # Khac `dinh_chinh` o DUNG MOT cho, va cho do la ca y nghia: khong co cau
    # "a khong, toi nham". Nen khong ban nao bi thay the — ca hai o trang thai
    # `chua giai quyet`, va bac si phai la nguoi hoi lai.
    #
    # VI SAO CAN (do 11/09/2026). Luoc do khai BON quan he va BA trang thai,
    # nhung tren ca 43.687 menh de cua bo 5.000:
    #
    #     bo sung       0 vi du
    #     dinh chinh  784
    #     dien bien   795
    #     mau thuan     0 vi du
    #
    # va `trang_thai` chi co hai gia tri, khong co `chua giai quyet`. Tai lieu
    # thi khai ca bon quan he va ca ba trang thai nhu nhau, kem so do chuyen
    # trang thai co mui "mau thuan -> chua giai quyet". Do la KHAI QUA.
    #
    # Nang hon: `phan_quan_he` cho mo hinh chon giua 5 nhan, trong do HAI nhan
    # khong co mot vi du duong nao. Chung chi la nguon nhieu.
    #
    # Mot bay nay lap ca hai lo~: quan he `mau thuan` VA trang thai
    # `chua giai quyet`.
    if "mau_thuan" in ca.bay:
        ro = nl.MOC_MAN if benh["dien_tien"] == "mạn" else nl.MOC_CAP
        moc_khac = rng.choice([m for m in ro if m != moc])
        tx = ca.nguoi_ke[2] if ca.nguoi_ke else ca.tu_xung_bn
        l2 = s.ke(rng.choice([
            f"{tx} nghĩ là {moc_khac} thì đúng hơn{tt()}.",
            f"Mà cũng có thể {moc_khac}, {tx} không chắc lắm{tt()}.",
            f"Hình như {moc_khac} cơ{tt()}.",
        ]))
        cu = md_chinh
        cu.luot.append(l2)
        # KHONG dat "bi thay the": khong co dinh chinh thi khong ban nao thang.
        cu.trang_thai = "chưa giải quyết"
        moi = MenhDe(chu_the=cu.chu_the, noi_dung=cu.noi_dung, muc=cu.muc,
                     moc_thoi_gian=moc_khac, phu_dinh=cu.phu_dinh,
                     tinh_huong=cu.tinh_huong, luot=list(cu.luot),
                     quan_he="mâu thuẫn", quan_he_voi=cu,
                     trang_thai="chưa giải quyết",
                     # "nghi la...", "co the...", "hinh nhu..." — ca ba cach
                     # noi deu RAO DON, nen ban nay la `nghi ngo`.
                     do_chac_chan="nghi ngờ", hanh_vi="tự kể",
                     thoi_gian_su_kien=cu.thoi_gian_su_kien)
        s.menh_de.insert(s.menh_de.index(cu) + 1, moi)
        # Bac si phai HOI LAI, khong duoc im lang chon mot ban. Im lang la
        # hanh vi sai trong hoi thoai kham benh that.
        s.bs(f"Để tôi ghi là chưa rõ {moc} hay {moc_khac}, "
             f"mình xác nhận lại sau nhé{tt()}.")

    # --- hoi them trieu chung
    s.bs(rng.choice(nl.HOI_THEM).format(tt=tt()))
    phu = rng.sample(benh["phu"], k=rng.randint(1, min(2, len(benh["phu"]))))
    cum = ", ".join(phu)
    chu = "" if "luoc_chu_ngu" in ca.bay else (
        goi_bn_trong_loi + " " if ca.nguoi_ke else ca.tu_xung_bn + " ")
    l = s.ke(f"{s.da()}{chu}còn {cum} nữa{tt()}.")
    md_phu = [s.ghi("bệnh nhân", p, "BỆNH SỬ HIỆN TẠI", l) for p in phu]

    # --- BAY BO SUNG: them CHI TIET cho mot menh de da noi, khong doi no
    #
    # Quan he `bo sung` duoc khai trong luoc do tu dau nhung co 0 vi du tren ca
    # bo 5.000 — xem chu thich o bay `mau_thuan`.
    #
    # Khac `dien_bien` o cho: `dien_bien` la HAI moc thoi gian, trieu chung doi
    # theo thoi gian. `bo sung` la CUNG mot su viec, chi them chi tiet — muc do,
    # thoi diem trong ngay, hoan canh. Ban cu VAN con hieu luc.
    if "bo_sung" in ca.bay and md_phu:
        goc = rng.choice(md_phu)
        chi_tiet = rng.choice(["nhiều hơn về đêm", "nặng hơn sau khi ăn",
                               "chỉ bị lúc sáng sớm", "tăng lên khi vận động",
                               "đỡ hơn khi nằm nghỉ"])
        l2 = s.ke(f"{s.da()}{goc.noi_dung} thì {chi_tiet}{tt()}.")
        goc.luot.append(l2)
        s.ghi("bệnh nhân", f"{goc.noi_dung} {chi_tiet}", goc.muc, l2,
              quan_he="bổ sung", quan_he_voi=goc)

    # --- dien bien: hai moc, CA HAI deu dung
    if "dien_bien" in ca.bay:
        tc = benh["chinh"][1] if len(benh["chinh"]) > 1 else benh["chinh"][0]
        m1, m2 = rng.sample(nl.MOC_THOI_DIEM, 2)
        l = s.ke(f"{m1.capitalize()} thì {tc}, {m2} thì đỡ hẳn rồi{tt()}.")
        # Hai menh de CHUNG mot luot: doan 0 noi moc dau, doan 1 noi moc sau.
        # Menh de sau noi TAT ("hom nay thi do han roi" — khong co ten trieu
        # chung), nen so khop tu tu dong se chon nham doan 0. Xem `_trich_dan`.
        s.ghi("bệnh nhân", tc, "BỆNH SỬ HIỆN TẠI", l, moc_thoi_gian=m1, doan=0)
        s.ghi("bệnh nhân", tc, "BỆNH SỬ HIỆN TẠI", l, moc_thoi_gian=m2,
              phu_dinh=True, doan=1)
        # CA HAI van "con hieu luc" — do la ca cho khac nhau giua dien bien va
        # dinh chinh. Chi danh dau quan he tren ban SAU, tro ve ban TRUOC.
        s.menh_de[-1].quan_he = "diễn biến"
        s.menh_de[-1].quan_he_voi = s.menh_de[-2]

    # --- tien su ban than
    if rng.random() < 0.55:
        s.bs(rng.choice(nl.HOI_TIEN_SU).format(tt=tt()))
        if rng.random() < 0.7:
            ts = rng.choice(nl.TIEN_SU_TRE_EM if ca.la_tre_em else nl.TIEN_SU_NGUOI_LON)
            chu = "" if "luoc_chu_ngu" in ca.bay else (
                goi_bn_trong_loi + " " if ca.nguoi_ke else ca.tu_xung_bn + " ")
            l = s.ke(f"{s.da()}{chu}có {ts}{tt()}.")
            s.ghi("bệnh nhân", ts, "TIỀN SỬ BỆNH", l)
        else:
            s.ke(f"{s.da(phu_dinh=True)}không có gì{tt()}.")

    # --- BAY QUAN TRONG NHAT: tien su cua NGUOI NHA, ke xen vao
    if "tien_su_gia_dinh" in ca.bay:
        s.bs(rng.choice(nl.HOI_GIA_DINH).format(tt=tt()))
        ai = _nguoi_nha_khac(ca, rng)
        benh_nha = _benh_hop_tuoi(ai, ca, rng)
        tu_xung = ca.nguoi_ke[2] if ca.nguoi_ke else ca.tu_xung_bn
        if ai == "người kể":
            # Chinh nguoi dang ke lai noi ve benh CUA HO. Day la cho de gan nham
            # nhat: nguoi noi va chu the la MOT, nhung chu the KHONG phai benh nhan.
            ten_that = _ten_nguoi_ke(ca) if ca.nguoi_ke else "bệnh nhân"
            l = s.ke(f"{s.da()}{tu_xung} thì bị {benh_nha}, "
                     f"còn {goi_bn_trong_loi} thì chưa thấy gì{tt()}.")
            s.ghi(ten_that, benh_nha, "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", l)
        else:
            l = s.ke(f"{s.da()}{ai} bị {benh_nha}{tt()}.")
            s.ghi(ai, benh_nha, "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", l)

    # --- BAY TANG 4: nguoi nha TU NOI RA benh cua chinh minh, khong ai hoi
    #
    # Khac `tien_su_gia_dinh` o hai cho, va ca hai lam no kho hon:
    #
    #   1. KHONG co cau hoi cua bac si dan vao. `tien_su_gia_dinh` luon di sau
    #      `HOI_GIA_DINH`, nen ngu canh da bao truoc "sap noi ve nguoi khac".
    #      O day loi nay xen vao giua mach ke ve benh nhan.
    #   2. Cau khong co menh de doi lap "con chau thi chua thay gi". Mot he
    #      thong co the dang an diem nho nua sau do chu khong nho quy gan.
    #
    # Dap an ghi chu the la TEN THAT cua nguoi ke, nen no vao muc tien su gia
    # dinh chu khong vao muc cua benh nhan.
    if "nguoi_ke_benh_minh" in ca.bay and ca.nguoi_ke:
        tu_xung = ca.nguoi_ke[2]
        ten_that = _ten_nguoi_ke(ca)
        benh_minh = _benh_hop_tuoi("người kể", ca, rng)
        mau_cau = rng.choice([
            "{tx} cũng đang {benh}, nên {tx} hay lo{tt}.",
            "{tx} bị {benh} mấy năm nay rồi{tt}.",
            # KHONG gan {tt}: cau da ket bang "bac si a" — gan them thanh "a a".
            "{tx} đang điều trị {benh}, bác sĩ ạ.",
            "{tx} thì {benh}, nói thêm để bác sĩ biết{tt}.",
        ])
        l = s.ke(f"{s.da()}{mau_cau.format(tx=tu_xung, benh=benh_minh, tt=tt())}")
        s.ghi(ten_that, benh_minh, "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", l)

    # --- di ung
    if rng.random() < 0.6 or "di_ung_nguoi_nha" in ca.bay:
        s.bs(rng.choice(nl.HOI_DI_UNG).format(tt=tt()))
        if "di_ung_nguoi_nha" in ca.bay:
            ai = _nguoi_nha_khac(ca, rng, cho_phep_nguoi_ke=True)
            if tuy.di_ung_cua_nguoi_ke and ca.nguoi_ke:
                # Van RUT so o dong tren roi moi dat de: hai ban cua mot cap
                # thach thuc phai di CUNG mot duong rut so.
                ai = "người kể"
            # Di ung cua NGUOI NHA: be rieng, chia theo tap. Di ung cua benh
            # nhan (nhanh `elif` ben duoi) van dung THUOC_DI_UNG, khong chia.
            thuoc = rng.choice(be_theo_tap(nl.DI_UNG_NGUOI_NHA, tap_cua_ca(ca)))
            tu_xung = ca.nguoi_ke[2] if ca.nguoi_ke else ca.tu_xung_bn
            ten_that = (_ten_nguoi_ke(ca) if (ai == "người kể" and ca.nguoi_ke) else ai)
            xung = tu_xung if ai == "người kể" else ai
            if tuy.doi_chu_the:
                # PHEP THU DOI CHU THE (`src.thach_thuc`): CUNG cau, dao hai
                # nguoi — benh nhan mang di ung, nguoi kia "chua thay bi bao
                # gio". Ban nay chi ghi di ung cua benh nhan: "chua thay bi bao
                # gio" cua nguoi nha khong phai thong tin cua ho so benh nhan.
                l = s.ke(f"{s.da()}{goi_bn_trong_loi} thì dị ứng {thuoc}, "
                         f"còn {xung} chưa thấy bị bao giờ{tt()}.")
                s.ghi("bệnh nhân", f"dị ứng {thuoc}", "DỊ ỨNG", l)
            else:
                l = s.ke(f"{s.da()}{xung} thì dị ứng {thuoc}, "
                         f"còn {goi_bn_trong_loi} chưa thấy bị bao giờ{tt()}.")
                s.ghi(ten_that, f"dị ứng {thuoc}", "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", l)
                # "Chua thay bi bao gio" la mot cho TRONG, khong phai phu dinh —
                # `chua ghi nhan`, xem `MenhDe.do_chac_chan`. Menh de noi TAT
                # (doan cuoi khong co chu "di ung"), nen goi y doan.
                s.ghi("bệnh nhân", "dị ứng thuốc", "DỊ ỨNG", l,
                      do_chac_chan="chưa ghi nhận", doan=-1)
        elif rng.random() < 0.35:
            thuoc = rng.choice(nl.THUOC_DI_UNG)
            l = s.ke(f"{s.da()}có, dị ứng {thuoc}{tt()}.")
            s.ghi("bệnh nhân", f"dị ứng {thuoc}", "DỊ ỨNG", l)
        else:
            l = s.ke(f"{s.da(phu_dinh=True)}không{tt()}.")
            # Tra loi TAT: "Da, khong a" khong mang noi dung, cap hoi–dap moi du
            # nghia — xem `_Soan.ghi(kem_cau_hoi)`.
            s.ghi("bệnh nhân", "dị ứng thuốc", "DỊ ỨNG", l, phu_dinh=True,
                  kem_cau_hoi=True)

    # --- thuoc dang dung
    if rng.random() < 0.5:
        s.bs(rng.choice(nl.HOI_THUOC).format(tt=tt()))
        if rng.random() < 0.65:
            chu = "" if "luoc_chu_ngu" in ca.bay else (
                goi_bn_trong_loi + " " if ca.nguoi_ke else ca.tu_xung_bn + " ")
            _ke_thuoc(s, ca, rng, chu, tt)
        else:
            s.ke(f"{s.da(phu_dinh=True)}chưa uống gì{tt()}.")

    # Benh nhan VANG MAT (nguoi nha di thay): bac si noi VE benh nhan o ngoi thu
    # ba, va KHONG kham duoc. Truoc 11/09/2026 boi canh nay van "Toi kham qua mot
    # chut" roi doc ket qua kham — kham mot nguoi khong co mat (193 ca train).
    vang_mat = ca.boi_canh == "nguoi_nha_thay_mat"
    goi_hoi = _bn_ngoi_ba(ca) if vang_mat else ca.goi_bn

    # --- bac si hoi ma KHONG ai tra loi
    if "hoi_khong_dap" in ca.bay:
        s.bs(rng.choice([
            f"Gần đây {goi_hoi} có đi đâu xa không{tt()}?",
            f"{_hoa(goi_hoi)} ngủ nghỉ thế nào{tt()}?",
            f"Ăn uống dạo này ra sao{tt()}?"]))
    if not vang_mat:
        s.bs(rng.choice(nl.CHUYEN_KHAM).format(goi=ca.goi_bn, goi_hoa=_hoa(ca.goi_bn)) + s.dn() + ".")

    # --- kham
    if vang_mat:
        pass
    elif ca.boi_canh == "dieu_duong_ban_giao":
        # Sinh hieu do DIEU DUONG doc, khong phai bac si. Chu the van la benh
        # nhan — day la mot bay quy gan them: nguoi noi la vai thu ba, hoan
        # toan khong lien quan toi noi dung.
        l = s.noi("Điều dưỡng", f"Sinh hiệu em đo được: {benh['kham']}")
        s.ghi("bệnh nhân", benh["kham"].rstrip("."), "KHÁM LÂM SÀNG", l)
    else:
        l = s.bs(benh["kham"])
        s.ghi("bệnh nhân", benh["kham"].rstrip("."), "KHÁM LÂM SÀNG", l)

    # --- chan doan va ke hoach, khac nhau theo BOI CANH
    if ca.boi_canh == "cho_ket_qua":
        # KHONG co chan doan XAC DINH. Bac si noi ro la CHUA ket luan duoc.
        #
        # Day la boi canh phuc vu thang thach thuc 3: bo du lieu truoc do khong
        # co MOT ca nao ma benh an dung lai KHONG co chan doan xac dinh, nen mo
        # hinh chua bao gio thay mot vi du "chua ket luan". Voi no, moi cuoc
        # kham deu ket thuc bang mot chan doan — va do la mot thoi quen nguy hiem.
        xn = rng.choice(["xét nghiệm máu", "chụp X-quang", "siêu âm",
                         "xét nghiệm nước tiểu"])
        # Bo tien to "Theo doi" cua khuon: truoc do cau nay ra "toi nghi nhieu den
        # theo doi suy giap" — khong phai tieng Viet. Chi ha chu DAU, giu chu viet
        # tat ("HP"); ban cu ha het ca cau.
        nghi, _muc = _muc_chan_doan(benh["chan_doan"])
        l_nghi = s.bs(f"Tôi nghĩ nhiều đến {nghi[:1].lower() + nghi[1:]}, nhưng "
                      f"chưa kết luận được. Phải có kết quả {xn} đã{s.dn()}.")
        # GHI nhan dinh do voi muc "nghi ngo" — them 11/09/2026. Truoc day boi
        # canh nay khong co menh de chan doan nao, nen `do_chac_chan = "nghi
        # ngo"` khong co mot vi du trong ca bo du lieu. Ban tham chieu in "Nghi
        # ngo X": dung muc bac si noi — khong nang thanh chan doan xac dinh,
        # cung khong bo mat nhan dinh.
        s.ghi("bệnh nhân", nghi, "CHẨN ĐOÁN", l_nghi, do_chac_chan="nghi ngờ")
        l = s.bs(f"{_hoa(ca.goi_bn)} đi làm {xn} rồi quay lại đây{s.dn()}.")
        s.ghi("bệnh nhân", f"làm {xn}", "KẾ HOẠCH ĐIỀU TRỊ", l,
              tinh_huong="kế hoạch")
    elif vang_mat:
        # Chua kham thi chua ket luan: nhan dinh ghi "nghi ngo", ke hoach la dua
        # benh nhan den kham truc tiep — khong ke don cho nguoi khong co mat.
        nghi, _muc = _muc_chan_doan(benh["chan_doan"])
        l_nghi = s.bs(f"Nghe {ca.nguoi_ke[1]} kể thì tôi nghĩ nhiều đến "
                      f"{nghi[:1].lower() + nghi[1:]}, nhưng chưa khám trực tiếp "
                      f"nên chưa kết luận được{tt()}.")
        s.ghi("bệnh nhân", nghi, "CHẨN ĐOÁN", l_nghi, do_chac_chan="nghi ngờ")
        l = s.bs(f"{_hoa(ca.nguoi_ke[1])} đưa {goi_hoi} đến để tôi khám trực "
                 f"tiếp{s.dn()}.")
        s.ghi("bệnh nhân", "đưa bệnh nhân đến khám trực tiếp", "KẾ HOẠCH ĐIỀU TRỊ",
              l, tinh_huong="kế hoạch")
    else:
        l = s.bs(f"{benh['chan_doan']}")
        cd, muc_cd = _muc_chan_doan(benh["chan_doan"])
        s.ghi("bệnh nhân", cd, "CHẨN ĐOÁN", l, do_chac_chan=muc_cd)

        l = s.bs(benh["ke_hoach"])
        s.ghi("bệnh nhân", benh["ke_hoach"].rstrip("."), "KẾ HOẠCH ĐIỀU TRỊ", l,
              tinh_huong="kế hoạch")

    # --- y lenh thuoc cua bac si (ngung thuoc, hoac ke thuoc moi)
    _y_lenh_thuoc(s, ca, rng, tt)

    # --- cau gia dinh: KHONG duoc thanh trieu chung da xay ra
    if "gia_dinh" in ca.bay:
        dk = rng.choice(benh["chinh"])
        l = s.bs(f"Nếu mai {_bn_ngoi_ba(ca) if ca.nguoi_ke else ca.goi_bn} còn {dk} thì "
                 f"{rng.choice(nl.DAN_DO)} nhé.")
        # GHI menh de nay voi tinh_huong="giả định" — cung ly do voi `quan_he`
        # (xem docstring MenhDe). Truoc day cho nay khong ghi gi ca, nen dap an
        # co DUNG HAI gia tri "thực tế" va "kế hoạch" tren ca 19.035 menh de,
        # va mo hinh trich chua bao gio nhin thay mot vi du "giả định" nao.
        # Do la ly do day du cua viec nhanh C chi dat 53% o nhom `gia_dinh`
        # trong khi nhanh A dat 87%.
        #
        # Menh de nay KHONG vao benh an tham chieu: `sinh_benh_an` bo qua
        # tinh_huong="giả định" (dong dau ham). Nen benh an khong doi mot ky tu,
        # dung nhu ban sua `dinh_chinh`.
        s.ghi("bệnh nhân", dk, "BỆNH SỬ HIỆN TẠI", l, tinh_huong="giả định")

    # --- ket: tu xung trong loi chao phai la tu xung cua CHINH nguoi noi. Truoc
    # 11/09/2026 boc ngau nhien, nen nguoi xung "toi" ca cuoc ket bang "Vang a, em
    # cam on bac si".
    tx = ca.nguoi_ke[2] if ca.nguoi_ke else ca.tu_xung_bn
    hop = [c for c in s.vung["chao_cuoi"]
           if set(re.findall(r"(?<!\w)(tôi|em|cháu|con)(?!\w)", c.lower())) <= {tx}]
    s.ke(rng.choice(hop) if hop else f"{s.da()}{tx} cảm ơn bác sĩ{tt()}.")
    return s


# ------------------------------------- be noi dung nguoi nha, CHIA THEO TAP
#
# VI SAO. Truoc 11/09/2026 ca ba tap rut noi dung nguoi nha tu CUNG mot bang,
# va tap phat trien dung lai dung 25/25 chuoi cua train (284/284 menh de tang
# 4). Du an chia tap theo khuon de do kha nang khai quat, nhung tu vung nguoi
# nha di xuyen qua ca ba tap — nen tang 4, cho quan trong nhat, chua bao gio
# duoc thu tren noi dung CHUA THAY.
#
# Nay moi tap co be rieng, KHONG chong nhau: mot noi dung roi vao dung mot tap,
# theo bam cua chinh chuoi do. Tap cua MOT CA suy tu khuon benh cua no, qua
# `tach_tap_viet.phan_khuon` — CUNG ham ma buoc chia tap dung, de hai cho khong
# the troi nhau.
#
# Chia TUNG BANG rieng (benh moi tuoi, benh tuoi gia, di ung) de moi tap co ty
# le cua moi loai, thay vi mot tap co the rong han mot loai.
_DAI_TAP = {"train": (0.0, 0.70), "phat_trien": (0.70, 0.85),
            "kiem_tra_cuoi": (0.85, 1.0)}


def dai_cua(noi_dung):
    """Vi tri on dinh trong [0, 1) cua mot noi dung. Khong phu thuoc thu tu."""
    h = hashlib.sha256(f"nguoi-nha:{noi_dung}".encode("utf-8")).hexdigest()
    return int(h[:12], 16) / float(16 ** 12)


@functools.lru_cache(maxsize=None)
def _be_cache(cac_muc, tap):
    lo, hi = _DAI_TAP[tap]
    ra = tuple(x for x in cac_muc if lo <= dai_cua(x) < hi)
    if not ra:
        # Mot tap co be RONG la mot lo~: bo sinh se phai lay tu tap khac, va do
        # dung la ro ri ma be theo tap duoc dung ra de chan. Bao loi thay vi lui.
        raise ValueError(f"be noi dung nguoi nha cua tap {tap!r} rong")
    return ra


def be_theo_tap(cac_muc, tap):
    """-> cac noi dung thuoc `tap`. Moi noi dung thuoc DUNG MOT tap."""
    return list(_be_cache(tuple(cac_muc), tap))


@functools.lru_cache(maxsize=1)
def _bang_tap_khuon(cac_khuon):
    p = tach_tap_viet.phan_khuon(list(cac_khuon))
    return {ten: tap for tap, cac in p.items() for ten in cac}


def bang_tap_khuon():
    """-> {ten khuon: tap} MA BO SINH GIA DINH khi chon be noi dung nguoi nha.

    `tach_tap_viet.kiem_khop_bo_sinh` doi chieu buoc chia voi bang nay.
    """
    return dict(_bang_tap_khuon(tuple(b["ten"] for b in nl.BENH)))


def tap_cua_ca(ca):
    """-> tap ma ca nay se roi vao sau buoc chia. Suy tu TEN KHUON."""
    return _bang_tap_khuon(tuple(b["ten"] for b in nl.BENH))[ca.benh["ten"]]


def _hop_gioi(benh, vai):
    """"Bo bi u xo tu cung" thi bac si doc qua la thay sai ngay."""
    if vai in nl.VAI_NAM and benh in nl.CHI_NU:
        return False
    if vai in nl.VAI_NU and benh in nl.CHI_NAM:
        return False
    return True


def _benh_hop_tuoi(ai: str, ca: Ca, rng: random.Random) -> str:
    """Benh phai hop lua tuoi VA GIOI cua nguoi mang no, va thuoc be cua TAP.

    Mot nguoi me tre dua con di kham ma "bi tai bien mach mau nao" thi bac si
    doc qua la thay sai ngay — va tinh hop ly cua ca benh cung la mot phan chat
    luong du lieu, khong phai chi tiet trang tri. Cung ly do do cho gioi: tu
    11/09/2026 be co benh chi co o mot gioi (xem `nl.CHI_NU`, `nl.CHI_NAM`).
    """
    thuc = ai if ai != "người kể" else (_ten_nguoi_ke(ca) if ca.nguoi_ke else "bệnh nhân")
    tap = tap_cua_ca(ca)
    if thuc in nl.NGUOI_LON_TUOI and rng.random() < 0.55:
        ung = [b for b in be_theo_tap(nl.TIEN_SU_GIA_DINH_LON_TUOI, tap)
               if _hop_gioi(b, thuc)]
        if ung:
            return rng.choice(ung)
    ung = [b for b in be_theo_tap(nl.TIEN_SU_GIA_DINH_MOI_TUOI, tap)
           if _hop_gioi(b, thuc)]
    return rng.choice(ung)


def _nguoi_nha_khac(ca: Ca, rng, cho_phep_nguoi_ke=True) -> str:
    ung_vien = ["mẹ", "bố", "bà ngoại", "bà nội", "ông nội", "anh trai", "chị gái"]
    if ca.nguoi_ke and cho_phep_nguoi_ke and rng.random() < 0.55:
        return "người kể"
    return rng.choice(ung_vien)


# ------------------------------------------------------------- sinh benh an

def sinh_benh_an(menh_de: List[MenhDe]) -> str:
    """Benh an CHI gom menh de da duoc noi ra. Chu the khac benh nhan thi phai
    ghi ro ten nguoi, va khong duoc vao muc cua benh nhan."""
    theo_muc = {}
    for m in menh_de:
        if m.tinh_huong == "giả định":
            continue
        # Ban da bi dinh chinh khong vao benh an tham chieu. No van nam trong
        # DAP AN de do duoc buoc phat hien quan he — hai thu do khac nhau.
        if m.trang_thai == "bị thay thế":
            continue
        # MAU THUAN CHUA GIAI QUYET: hai ban cung noi dung, khac moc. In ca hai
        # thanh hai dong la viet mot benh an noi benh nhan sot "hon mot tuan" VA
        # "gan mot tuan" — doc la thay sai ngay. Benh an that ghi mot dong, neu
        # ro la chua ro, dung nhu cau bac si noi trong hoi thoai.
        #
        # Gop o day chu khong gop trong `dap_an`: dap an phai giu CA HAI ban de
        # do duoc buoc phat hien quan he. Hai viec khac nhau.
        if m.trang_thai == "chưa giải quyết" and m.quan_he == "mâu thuẫn":
            continue          # ban thu hai — da gop vao ban thu nhat ben duoi
        cum = m.noi_dung
        # Chi tiet thuoc (15/09/2026) — DUNG ham cua duong ong, khong viet lai: hai
        # khau in chi tiet thuoc theo hai cach thi ban tham chieu va ban nhap lech
        # chu, va moi thuoc do so van ban phat lech do thanh loi.
        if m.thuoc:
            from src.sinh_benh_an import _them_chi_tiet_thuoc
            cum = _them_chi_tiet_thuoc(cum, m.thuoc)
        if m.chu_the != "bệnh nhân":
            cum = f"{_hoa(m.chu_the)} {cum}"
        # Ba muc chac chan in thanh ba cach KHAC NHAU, giong `sinh_benh_an.
        # dien_dat` cua duong ong. Truoc 11/09/2026 moi `phu_dinh` deu in thanh
        # "Chua ghi nhan": mot khang dinh AM ("khong di ung") va mot cho TRONG
        # ("chua thay bi bao gio") ra cung mot chu, trong khi ban nhap cua
        # duong ong in "khong ..." cho cung menh de do — hai khau lech nhau.
        elif m.do_chac_chan == "chưa ghi nhận":
            cum = f"Chưa ghi nhận {cum}"
        elif m.do_chac_chan == "nghi ngờ":
            # Noi dung da tu mang dau rao don ("Viem hong nghi do lien cau") thi
            # khong them "Nghi ngo" lan nua.
            if not re.search(r"(?<!\w)nghi(?!\w)", cum, re.I):
                cum = f"Nghi ngờ {cum}"
        elif m.phu_dinh:
            cum = f"Không {cum}"
        if m.moc_thoi_gian and m.muc == "BỆNH SỬ HIỆN TẠI":
            xung = [k for k in menh_de
                    if k.quan_he == "mâu thuẫn" and k.quan_he_voi is m
                    and k.moc_thoi_gian]
            if xung:
                cum = (f"{cum} (chưa rõ {m.moc_thoi_gian} hay "
                       f"{xung[0].moc_thoi_gian})")
            else:
                cum = f"{cum} ({m.moc_thoi_gian})"
        theo_muc.setdefault(m.muc, [])
        if cum not in theo_muc[m.muc]:
            theo_muc[m.muc].append(cum)

    # Neu ro CHU NGU o cau dau BENH SU HIEN TAI. Benh an that mo dau kieu
    # "Benh nhan nam 45 tuoi, dau bung..." chu khong luoc chu ngu hoan toan.
    #
    # Ngoai chuyen giong that hon, cho nay con can cho phep thu chung chi
    # thuoc do: phep thu doi cho tu chi BENH NHAN voi tu chi NGUOI NHA o hai
    # cau khac nhau. Khi benh an luoc het chu ngu thi khong co gi de doi —
    # do 2.231 ban chi 21 ban co tu chi benh nhan, va chi 2 ban dung duoc.
    if theo_muc.get("BỆNH SỬ HIỆN TẠI"):
        dau = theo_muc["BỆNH SỬ HIỆN TẠI"][0]
        if not dau.lower().startswith(("bệnh nhân", "chưa ghi nhận")):
            theo_muc["BỆNH SỬ HIỆN TẠI"][0] = f"bệnh nhân {dau}"

    khoi = []
    for muc in MUC:
        if muc not in theo_muc:
            continue
        noi_dung = "; ".join(theo_muc[muc])
        khoi.append(f"{muc}\n\n{_hoa(noi_dung)}.")
    return "\n\n".join(khoi)


# ------------------------------------------------------------------ sinh bo

def _chon_bay(rng: random.Random) -> List[str]:
    """Moi ca mang 0-3 bay. Phan bo doc lap voi do dai hoi thoai."""
    n = rng.choices([0, 1, 2, 3], weights=[22, 34, 30, 14])[0]
    return sorted(rng.sample(BAY_RUT, k=n))


def _du_dieu_kien_nguon_khac_nhau(ca: Ca) -> bool:
    """Hai NGUON phai cung co mat va cung noi: benh nhan nguoi lon, co nguoi nha
    ke, benh nhan khong vang mat, va trieu chung chinh chua mang bay khac."""
    return (ca.nguoi_ke is not None and not ca.la_tre_em
            and ca.boi_canh != "nguoi_nha_thay_mat"
            and not ({"dinh_chinh", "mau_thuan"} & set(ca.bay)))


# PHUONG NGU CHI O TAP DANH GIA — quyet dinh 11/09/2026.
#
# Bang thay (`phuong_ngu.THAY_DUOC`) lay tu tu dien nguoi dung cung cap, ma nguoi
# dung xac nhan ngay 11/09/2026 la do GPT SINH. Du an co rang buoc cung: khong
# dung mo hinh ngon ngu thuong mai o bat ky khau nao, KE CA sinh du lieu huan
# luyen. Nen tu ngay do khuon TRAIN khong nhan tu nao tu bang do; tap phat trien,
# tap kiem tra cuoi va bo thach thuc phuong ngu van co.
#
# Cai gia va cai loi: mo hinh khong con hoc 10 cap tu do trong luc huan luyen, nen
# tren tap phat trien no gap phuong ngu LAN DAU — dung cau hoi "chiu duoc phuong
# ngu chua gap khong" ma bo thach thuc muon hoi. Tieu tu vung mien ("nghen", "ha")
# la cua chinh bo sinh tu truoc, khong tu bang GPT, van giu o moi tap.
#
# The he 4 (chuoi chay 11/09/2026) DA huan luyen tren du lieu co 10 cap thay nay:
# phai ghi ro khi dung so cua the he 4.
PHUONG_NGU_TRONG_TRAIN = False


def _xa_giao(s, ca, rng) -> None:
    """Chen 0-2 trao doi xa giao, KHONG mang thong tin lam sang.

    VI SAO CO. Ca MANG BAY dai hon ca khong bay, do duoc tren 400 ca: trung binh
    14,3 so voi 12,8 luot. Chenh 1,5 luot do la mot duong tat that — dem so luot
    la doan duoc ca nay co bay hay khong, va khi ay moi so do tren bo du lieu deu
    lan mot phan "doan theo do dai". `test_do_dai_KHONG_lo_ca_nao_co_bay` canh
    dung cho nay va da bao do.

    VI SAO CHEN CHO CA HAI NHOM, KHONG CHI CHO NHOM KHONG BAY. Chen rieng cho ca
    khong bay thi vua bit duoc mot manh moi da tao ra mot manh moi khac: su co
    mat cua doan xa giao TRO THANH dau hieu "ca nay khong co bay". So luong lay
    ngau nhien va DOC LAP voi `ca.bay`, nen no lam loang ca hai phan bo chu khong
    day mot phan bo sang cho khac.

    KHONG goi `s.ghi`: mot cap xa giao khong sinh menh de nao. Neu mot ngay nao do
    no sinh, dap an se dai them ma khong ai co y do — nen `test_xa_giao_KHONG_sinh
    _menh_de` chot dieu do lai.
    """
    for _ in range(rng.choice((0, 1, 1, 2))):
        hoi, dap = rng.choice(nl.XA_GIAO)
        s.bs(hoi.format(goi=ca.goi_bn, goi_hoa=_hoa(ca.goi_bn)))
        s.ke(dap)


def sinh_mot_ca(ma: str, rng: random.Random,
                tuy: Optional[TuyChon] = None) -> dict:
    """MOT ca hoan chinh. `sinh_bo` la chuoi cac lan goi ham nay voi CUNG mot
    `rng` — bo chinh va bo thach thuc (`src.thach_thuc`) di qua cung mot duong,
    co test canh."""
    tuy = tuy or TuyChon()
    ca = sinh_ca(ma, rng, chi_tap=tuy.chi_tap, ep_mien=tuy.ep_mien,
                 ep_nguoi_ke=tuy.ep_nguoi_ke)
    # Tat phuong ngu SAU khi rut khuon: `_Soan` rut hat giong cho lop phuong ngu
    # tren mot `rng` rieng, nen tat hay bat khong doi gi khac trong ca.
    if tuy.ap_phuong_ngu and not PHUONG_NGU_TRONG_TRAIN and tap_cua_ca(ca) == "train":
        from dataclasses import replace
        tuy = replace(tuy, ap_phuong_ngu=False)
    ca.bay = _chon_bay(rng)
    # Bay EP them (chi bo thach thuc). Bay BAT RIENG khong them o day — chung co
    # dieu kien rieng, xet ben duoi.
    ca.bay = sorted(set(ca.bay) | (set(tuy.ep_bay) - set(BAY_BAT_RIENG)))
    if ca.nguoi_ke:
        ca.bay = sorted(set(ca.bay) | {"nguoi_nha_ke_ho"})
    elif "nguoi_nha_ke_ho" in ca.bay:
        ca.bay.remove("nguoi_nha_ke_ho")
    # Hai bay nay can co nguoi nha trong hoi thoai moi co nghia.
    if not ca.nguoi_ke:
        ca.bay = [b for b in ca.bay if b != "di_ung_nguoi_nha"]
    # `dinh_chinh` va `mau_thuan` cung nham vao menh de trieu chung chinh,
    # va mot moc thoi gian KHONG THE vua da duoc dinh chinh vua dang mau
    # thuan: dinh chinh co nghia la da co ban thang, mau thuan co nghia la
    # chua co. Giu `dinh_chinh` vi no co truoc, de so lieu cu con so sanh
    # duoc — tru khi `mau_thuan` la bay bi EP (bo thach thuc).
    if "dinh_chinh" in ca.bay and "mau_thuan" in ca.bay:
        bo = "dinh_chinh" if "mau_thuan" in tuy.ep_bay else "mau_thuan"
        ca.bay = [b for b in ca.bay if b != bo]
    # Bay tang 4, bat RIENG ngoai `_chon_bay` — xem TY_LE_NGUOI_KE_BENH_MINH.
    if ca.nguoi_ke and rng.random() < TY_LE_NGUOI_KE_BENH_MINH:
        ca.bay = sorted(set(ca.bay) | {"nguoi_ke_benh_minh"})
    # Bay hai nguon, cung bat RIENG — xem TY_LE_NGUON_KHAC_NHAU. Rut so TRUOC khi
    # xet bay ep, de ep hay khong ep deu di cung mot duong rut so.
    if _du_dieu_kien_nguon_khac_nhau(ca):
        rut = rng.random() < TY_LE_NGUON_KHAC_NHAU
        if rut or "nguon_khac_nhau" in tuy.ep_bay:
            ca.bay = sorted(set(ca.bay) | {"nguon_khac_nhau"})

    s = sinh_hoi_thoai(ca, rng, tuy)
    hoi_thoai = "\n".join(f"{vai}: {cau}" for vai, cau in s.luot)
    # Dap an tinh TRUOC ban benh an mau: trich dan phai tim tren noi dung CHUAN
    # (loi goc con chu "sot"), roi moi doi noi dung sang loi nguoi noi — xem
    # `_giu_loi_nguoi_noi`. Doi truoc thi trich dan lui ve ca luot.
    dap_an = _dap_an(s.menh_de, s.luot, s.luot_goc)
    _giu_loi_nguoi_noi(s.menh_de, dap_an)
    return {
        "id": ca.ma,
        "input": hoi_thoai,
        "output": sinh_benh_an(s.menh_de),
        "bay": ca.bay,
        "so_luot": len(s.luot),
        "benh": ca.benh["ten"],
        "la_tre_em": ca.la_tre_em,
        "nguoi_ke": ca.nguoi_ke[0] if ca.nguoi_ke else None,
        "lo_danh_tinh": ca.lo_danh_tinh,
        "boi_canh": ca.boi_canh,
        "tu_phuong_ngu": sorted(set(s.tu_phuong_ngu)),
        "cum_dan_thuong": sorted(set(s.cum_dan_thuong)),
        "dap_an": dap_an,
    }


def _giu_loi_nguoi_noi(menh_de: List[MenhDe], dap_an: List[dict]) -> None:
    """Cum phuong ngu khong dong nghia (`phuong_ngu.GIU_NGUYEN`, hien chi co "nong
    ham hap"): noi dung menh de ghi dung loi nguoi noi thay vi tu chuan. Doi CA
    `MenhDe` (cho `sinh_benh_an`) LAN ban ghi dap an. Sua 24/09/2026."""
    from src import phuong_ngu
    for m, d in zip(menh_de, dap_an):
        moi = phuong_ngu.giu_loi_nguoi_noi(m.noi_dung, d["trich_dan"])
        if moi != m.noi_dung:
            m.noi_dung = moi
            d["noi_dung"] = moi


# Seed 42 la seed DA DUNG de sinh `hoi_thoai_viet_3000.jsonl`. Mac dinh
# truoc day la 2026, khong khop voi tep dang nam trong kho — chay lai lenh
# mac dinh se ra mot bo KHAC, va khong ai biet cho toi khi so lieu lech.
def sinh_bo(so_ca: int, seed: int = 42) -> List[dict]:
    rng = random.Random(seed)
    return [sinh_mot_ca(f"hv_{i + 1:04d}", rng) for i in range(so_ca)]


def _dap_an(menh_de: List[MenhDe], luot=None, luot_goc=None) -> List[dict]:
    """Doi `quan_he_voi` tu con tro sang CHI SO trong chinh danh sach nay.

    Dung chi so chu khong dung ten: hai menh de co the trung noi dung (dung
    la truong hop cua `dinh_chinh` — cung noi dung, khac moc), nen ten khong
    xac dinh duy nhat. Luoc do trich cua `bakeoff` cung dung chi so dem tu 0.

    `trich_dan` tinh O DAY, khi hoi thoai da xong: menh de con duoc them luot
    sau khi ghi (bay dinh chinh them luot sua vao ban cu), nen tinh luc `ghi`
    la tinh tren mot danh sach luot chua du.
    """
    vi_tri = {id(m): i for i, m in enumerate(menh_de)}
    return [
        {"chu_the": m.chu_the, "noi_dung": m.noi_dung, "muc": m.muc,
         "moc_thoi_gian": m.moc_thoi_gian, "phu_dinh": m.phu_dinh,
         "tinh_huong": m.tinh_huong, "luot": m.luot,
         # Them 11/09/2026. Danh sach truong o day duoc go TAY, nen them truong
         # vao `MenhDe` ma quen dong nay thi dap an khong mang no — va khong co
         # gi bao loi: bo sinh van chay, tep van dung dinh dang, chi la nhan moi
         # khong bao gio ra tep. Da xay ra dung the: lan dau them truong nay,
         # ca 4.533 menh de deu co `thoi_gian_su_kien = None`.
         "thoi_gian_su_kien": m.thoi_gian_su_kien,
         "quan_he": m.quan_he,
         "quan_he_voi": (vi_tri.get(id(m.quan_he_voi))
                         if m.quan_he_voi is not None else None),
         "trang_thai": m.trang_thai,
         "do_chac_chan": m.do_chac_chan,
         "hanh_vi": m.hanh_vi,
         # Them 15/09/2026 — cung ho loi o chu thich ngay tren: quen dong nay thi
         # bo sinh van chay va dap an khong bao gio mang chi tiet thuoc.
         "thuoc": dict(m.thuoc) if m.thuoc else None,
         "trich_dan": (_trich_dan(m, luot, luot_goc)
                       if luot is not None else [])}
        for m in menh_de]


# ------------------------------------------------------- doan bang chung
#
# Cach cat DOAN dung chung voi tang khoa bang chung — MOT dinh nghia, o
# `src.doan_van`. Hai cho cat doan khac nhau thi trich dan cua dap an va doan ma
# khoa kiem se lech nhau ma khong bao loi.
from src.doan_van import cac_doan  # noqa: E402


def _trich_mot_luot(md: MenhDe, so: int, luot, luot_goc) -> str:
    """Doan NGAN NHAT trong luot `so` noi ra menh de `md`, NGUYEN VAN.

    Tim doan tren LOI GOC (truoc tang ngu vuc va tang vung), vi o do thuat ngu
    chuan con nguyen: "buon non" con la "buon non", chua thanh "non nao". Roi
    lay DOAN CUNG CHI SO tren loi that — hai tang do khong them bot dau cau,
    nen so doan hai ben bang nhau (co test canh; lech thi lui ve ca luot).

    Ba buoc, theo thu tu:
      1. goi y `md.goi_y_doan` — cho menh de noi TAT
      2. cua so doan NGAN NHAT phu het cac tu noi dung tim thay trong luot
      3. khong tu nao khop (cau tra loi tat "Da, khong a") -> ca luot
    """
    from src.thuoc_do_quy_gan import _tu_noi_dung
    van = luot[so - 1][1]
    goc = luot_goc[so - 1]
    d_van, d_goc = cac_doan(van), cac_doan(goc)
    if not d_van or len(d_van) != len(d_goc):
        return van.strip()
    if so in md.goi_y_doan:
        i = md.goi_y_doan[so]
        i = i if i >= 0 else len(d_van) + i
        if 0 <= i < len(d_van):
            return van[d_van[i][0]:d_van[i][1]]
    tu = set(_tu_noi_dung(md.noi_dung))
    if md.moc_thoi_gian:
        tu |= set(_tu_noi_dung(md.moc_thoi_gian))
    # Chi tiet thuoc thuong nam o doan SAU dau phay ("amlodipin 5 mg, ngay mot lan").
    # Khong them tu cua chung thi trich dan chi phu ten thuoc, va khoa bang chung
    # khong con doan nao chong lung cho lieu (15/09/2026).
    for k in ("lieu", "so_lan", "bat_dau", "ngung"):
        if md.thuoc and md.thuoc.get(k):
            tu |= set(_tu_noi_dung(md.thuoc[k]))
    phu = [tu & set(_tu_noi_dung(goc[a:b])) for a, b in d_goc]
    can = set().union(*phu)
    if not can:
        return van.strip()
    tot = None
    for a in range(len(phu)):
        gop = set()
        for b in range(a, len(phu)):
            gop |= phu[b]
            if gop >= can:
                if tot is None or b - a < tot[1] - tot[0]:
                    tot = (a, b)
                break
    a, b = tot
    return van[d_van[a][0]:d_van[b][1]]


def _trich_dan(md: MenhDe, luot, luot_goc) -> List[str]:
    """Moi luot trong `md.luot` mot doan — thang hang tung phan tu."""
    return [_trich_mot_luot(md, so, luot, luot_goc) for so in md.luot]


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--so-ca", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--ra", default=None)
    a = ap.parse_args()

    bo = sinh_bo(a.so_ca, a.seed)
    # `--ra` la TEN TEP trong thu muc du lieu, khong phai duong dan tuong doi
    # theo cho dang dung. Truoc day no la duong dan tho, nen
    # `--ra hoi_thoai_viet_3000.jsonl` ghi vao goc kho chu khong vao `data/`,
    # va lenh chia tap ngay sau do doc phai ban CU ma khong bao gi.
    # Duong dan tuyet doi van dung duoc, cho ai co y muon ghi ra cho khac.
    from pathlib import Path
    dp = duong_dan.THU_MUC_DU_LIEU / "hoi_thoai_viet.jsonl"
    if a.ra:
        p = Path(a.ra)
        dp = p if p.is_absolute() else duong_dan.THU_MUC_DU_LIEU / p.name
    with open(dp, "w", encoding="utf-8") as f:
        for m in bo:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    import collections
    dem_bay = collections.Counter(b for m in bo for b in m["bay"])
    tk = {
        "so_ca": len(bo),
        "so_khuon_benh": len(nl.BENH),
        "hoi_thoai_duy_nhat": len({m["input"] for m in bo}),
        "tong_luot": sum(m["so_luot"] for m in bo),
        "luot_moi_ca": round(sum(m["so_luot"] for m in bo) / len(bo), 1),
        "tong_tu": sum(len(m["input"].split()) for m in bo),
        "so_menh_de": sum(len(m["dap_an"]) for m in bo),
        "menh_de_khong_phai_benh_nhan": sum(
            1 for m in bo for d in m["dap_an"] if d["chu_the"] != "bệnh nhân"),
        "ca_nhi": sum(1 for m in bo if m["la_tre_em"]),
        "co_nguoi_nha_ke": sum(1 for m in bo if m["nguoi_ke"]),
        "bay": dict(dem_bay.most_common()),
    }
    print(f"{len(bo)} ca -> {dp}")
    for k, v in tk.items():
        if k != "bay":
            print(f"   {k}: {v}")
    print("bẫy:")
    for k, v in dem_bay.most_common():
        print(f"   {v:5d}  {k}")

    dp_md = duong_dan.THU_MUC_KET_QUA / "bo-du-lieu-viet.md"
    dp_md.write_text(_bao_cao(tk), encoding="utf-8")
    print(f"\nda ghi {dp_md}")


def _bao_cao(t: dict) -> str:
    bay = "\n".join(f"| `{k}` | {v} | {v / t['so_ca']:.1%} |"
                    for k, v in t["bay"].items())
    ty_le_khac = t["menh_de_khong_phai_benh_nhan"] / t["so_menh_de"]
    return f"""# Bộ hội thoại khám bệnh Việt Nam — sinh bằng luật

Sinh tự động bằng `python -m src.sinh_hoi_thoai_viet --so-ca {t['so_ca']}`.
Đừng sửa tay: sửa tay rồi chạy lại là mất.

## Vì sao tự dựng bộ này

Bộ của cuộc thi có dấu vết rõ là **bản dịch từ một bộ hội thoại y khoa tiếng
Anh (Mỹ)** — xem `docs/ket-qua/dau-vet-nguon.md`. Hậu quả nằm đúng chỗ dự án
quan tâm: hai hiện tượng làm việc quy gán khó nhất trong tiếng Việt đều bị
**dưới đại diện** trong một bản dịch, vì tiếng Anh gần như luôn có chủ ngữ.

1. **Lược chủ ngữ.** *"Sốt hai hôm rồi"*, *"Nôn từ tối qua"* — người đọc phải
   suy chủ thể từ ngữ cảnh.
2. **Từ chỉ quan hệ họ hàng làm đại từ.** *cháu*, *em*, *con* vừa là cách người
   nói tự xưng, vừa là cách gọi người thứ ba.

Bộ này sinh ra đúng hai hiện tượng đó, ở mật độ thật.

## Sinh bằng LUẬT, không bằng mô hình ngôn ngữ

Đây là ràng buộc số 1 của dự án, và lý do không phải hình thức: mô hình ngôn ngữ
viết hội thoại **sạch hơn người nói thật** — nó gần như luôn ghi rõ chủ ngữ ở
mỗi lượt. Nên đúng những ca khó nhất sẽ hiếm đi, và đường tắt *"chủ thể chính là
người vừa nói"* sẽ trúng nhiều hơn bình thường. Sai lệch đó **một chiều**: luôn
về phía làm vấn đề trông nhẹ hơn thật.

## Quy mô

| | |
|---|---|
| Số ca | **{t['so_ca']}** (hội thoại không trùng nhau: {t['hoi_thoai_duy_nhat']}) |
| Khuôn bệnh | {t['so_khuon_benh']} |
| Tổng lượt thoại | {t['tong_luot']} · trung bình {t['luot_moi_ca']} lượt/ca |
| Tổng từ | {t['tong_tu']:,} |
| Mệnh đề trong đáp án | {t['so_menh_de']} |
| **Mệnh đề KHÔNG thuộc bệnh nhân** | **{t['menh_de_khong_phai_benh_nhan']}** ({ty_le_khac:.1%}) |
| Ca nhi | {t['ca_nhi']} |
| Có người nhà kể hộ | {t['co_nguoi_nha_ke']} |

## Thứ bộ của cuộc thi không có: đáp án có cấu trúc

Mỗi ca kèm trường `dap_an` — danh sách mệnh đề, mỗi mệnh đề ghi **chủ thể thật**,
mốc thời gian thật, tình huống thật, và số lượt thoại làm bằng chứng.

Nhờ đó đo được độ chính xác quy gán **chính xác tuyệt đối**, thay vì ước lượng
qua một bản tham chiếu dạng văn xuôi. Đó cũng là chỗ gỡ được hạn chế nặng nhất
của `thuoc_do_quy_gan` — nó nhạy với cách đóng gói câu khi phải đối chiếu văn
xuôi với văn xuôi.

## Bẫy quy gán

| Bẫy | Số ca | Tỷ lệ |
|---|---|---|
{bay}

Ý nghĩa từng bẫy:

- `nguoi_nha_ke_ho` — người nhà kể thay bệnh nhân. Người nói ≠ chủ thể.
- `tien_su_gia_dinh` — người nhà kể bệnh **của chính họ** xen vào giữa. Đây là
  bẫy quan trọng nhất: người nói và chủ thể là một, nhưng chủ thể **không phải**
  bệnh nhân.
- `di_ung_nguoi_nha` — dị ứng thuộc về người nhà, bệnh nhân thì *chưa ghi nhận*.
- `luoc_chu_ngu` — câu không có chủ ngữ.
- `dai_tu_ho_hang` — *cháu*/*con* vừa là người nói vừa là người được nói tới.
- `dinh_chinh` — người nói tự sửa lại con số vừa nêu. Đáp án giữ **bản đã sửa**.
- `dien_bien` — hai mốc thời gian, **cả hai đều đúng**, đáp án giữ cả hai.
- `gia_dinh` — câu điều kiện *"nếu mai còn…"*, **không** được thành triệu chứng.
- `hoi_khong_dap` — bác sĩ hỏi, không ai trả lời. Bệnh án **không** được nhắc tới.

## Bốn cái bẫy khi sinh dữ liệu có đáp án — đều đã chặn và có test

1. **Thay thế làm bài toán không giải được** → chỉ **chèn thêm**, giữ nguyên lượt gốc.
2. **Hai khẳng định khác nhau không phải mâu thuẫn** → `dien_bien` giữ cả hai.
3. **Độ dài lộ đáp án** → số lượt không phụ thuộc vào việc ca đó có bẫy hay không.
4. **Vị trí lộ đáp án** → vị trí bẫy rải đều, không dính ở cuối.

Thêm một nhóm test về **ngôn ngữ**, vì một bộ dữ liệu tiếng Việt sai vai giao
tiếp thì mô hình sẽ học đúng cái sai đó: bệnh nhân không dùng *"Ừ"* với bác sĩ ·
tiểu từ đề nghị (*nhé, nghen*) không gắn vào câu hỏi · không trộn giọng hai miền
trong một cuộc · bệnh phải hợp lứa tuổi · mốc thời gian phải hợp diễn tiến bệnh.

## Giới hạn, nói thẳng

1. **Đây là dữ liệu mô phỏng, không phải hội thoại người thật.** Mọi kết luận rút
   ra từ nó phải nói rõ điều đó. Nó dùng để đo **cơ chế** — quy gán đúng hay sai
   khi có bẫy — chứ không đo tần suất lỗi ngoài đời.
2. **{t['so_ca']} ca sinh từ {t['so_khuon_benh']} khuôn bệnh.** Đơn vị độc lập là
   số khuôn, không phải số dòng. Đừng viết *"{t['so_ca']} ca đủ để kết luận"*.
3. **Lời thoại do luật ghép**, nên đều đặn hơn lời nói thật: không có ngập ngừng,
   không nói chen, không câu bỏ dở. Bộ này **không** thay được dữ liệu thật.
4. Chưa có bác sĩ duyệt. Trước khi dùng cho phần kết luận, cần bác đọc một mẫu
   ngẫu nhiên và xác nhận các ca là hợp lý về lâm sàng.
"""


if __name__ == "__main__":
    main()
