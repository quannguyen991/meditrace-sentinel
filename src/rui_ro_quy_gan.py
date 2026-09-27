# -*- coding: utf-8 -*-
"""Cham diem RUI RO QUY GAN cho tung phat bieu, va sang loc theo nguong.

VI SAO PHAN NAY TON TAI.

Hai co che loi cua du an deu khong khai hoa duoc tren du lieu that: quan he
chi ra 2 cap tren 282 phat bieu, va lien ket thuc the chi doi tien to cach goi.
Nhung co MOT hien tuong thi co that va do duoc:

    0,6 menh de gan nham nguoi tren moi ho so  (do bang `thuoc_do_quy_gan`)

Va hau het chung den tu cung mot duong tat, da thay o bake-off: mo hinh gan
trieu chung cho NGUOI VUA NOI. Duong tat do dung o phan lon luot — nen do
chinh xac cao khong chung minh duoc gi — va no sai dung vao nhom ca nguy hiem
nhat: nguoi nha ke ho benh nhan.

DOI CACH DAT VAN DE. Thay vi co sua cho mo hinh gan dung han — viec ma ba
nhanh da thu va khong an thua — hay **danh dau nhung phat bieu co nguy co gan
sai roi day chung xuong muc CAN XAC NHAN**.

Cai duoc: bac si van phai ky ban cuoi, nen thu ho thuc su can khong phai la
mot ban hoan hao ma la mot ban **kem danh sach cho phai soat**. Va vi nguong
la mot nut van duoc, no cho ra ca mot DUONG DANH DOI thay vi mot diem: gan co
nhieu thi it loi con lai trong than bai nhung bo sot nhieu hon, va nguoc lai.

Do la thu ma ke hoach da yeu cau o Cua 4 — *"chua co can cu chon nguong thi
trinh bay duong danh doi loi–bo sot thay vi ket luan mot chieu"* — nhung chua
bao gio dung.

BON DAU HIEU, va vi sao la bon dau hieu nay.

  chu_the_suy_tu_nguoi_noi   Trong cac luot bang chung KHONG co tu nao goi ten
                             chu the. Tuc chu the khong doc duoc tu noi dung,
                             no chi co the den tu nhan vai cua nguoi noi. Day
                             la dau hieu bat DUNG duong tat, va la dau hieu
                             manh nhat trong bon.
  nhieu_nguoi_ke             Hoi thoai co tu hai nguoi noi khong phai bac si.
                             Mot nguoi ke thi khong the lan; hai nguoi thi co.
  bang_chung_mot_luot        Chi mot luot lam bang chung. Cap hoi–dap can hai
                             luot moi du nghia, nen mot luot thuong la da mat
                             ve ngu canh.
  khong_chac_chan            `do_chac_chan` khac "chắc chắn".

TRONG SO DEU NHAU, va do la mot GIOI HAN phai ghi vao bao cao. Chua co du lieu
gan nhan tay de hieu chuan trong so; dat trong so bang tay roi bao "dau hieu
nay quan trong hon" la bia mot con so khong do duoc. Khi Task 9 va Task 13 co
nhan tay roi thi hieu chuan lai — va luc do phai do xem hieu chuan co that su
tot hon deu nhau khong, chu khong mac dinh la co.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

from src.phat_bieu import PhatBieu
from src.thuoc_do_quy_gan import TU_BENH_NHAN, TU_NGUOI_NHA

import re

DAU_HIEU = ("chủ thể suy từ người nói", "nhiều người kể",
            "bằng chứng một lượt", "không chắc chắn")

VAI_KHONG_PHAI_NGUOI_KE = ("bác sĩ", "điều dưỡng", "bs", "y tá")


@dataclass(frozen=True)
class NguCanh:
    """Thong tin cua CA hoi thoai, dung chung cho moi phat bieu trong do."""
    luot_thoai: Dict[int, str]
    so_nguoi_ke: int

    @classmethod
    def tu_hoi_thoai(cls, cac_luot):
        """`cac_luot`: [(so, vai, noi_dung)] — dau ra cua `thuc_the.tach_luot`."""
        luot = {so: nd for so, _, nd in cac_luot}
        nguoi_ke = {
            (vai or "").strip().lower() for _, vai, _ in cac_luot
            if (vai or "").strip().lower() not in VAI_KHONG_PHAI_NGUOI_KE
        }
        return cls(luot_thoai=luot, so_nguoi_ke=len(nguoi_ke))


def _co_tu(van_ban: str, cum_list) -> bool:
    thap = " " + (van_ban or "").lower() + " "
    return any(re.search(r"(?<![\w])" + re.escape(c) + r"(?![\w])", thap)
               for c in cum_list)


def dac_trung(p: PhatBieu, ngu_canh: NguCanh, id_benh_nhan: int = 0) -> Dict[str, bool]:
    van_ban = " ".join(ngu_canh.luot_thoai.get(l, "") for l in (p.bang_chung or []))
    cum = TU_BENH_NHAN if p.chu_the_id == id_benh_nhan else TU_NGUOI_NHA
    return {
        "chủ thể suy từ người nói": not _co_tu(van_ban, cum),
        "nhiều người kể": ngu_canh.so_nguoi_ke >= 2,
        "bằng chứng một lượt": len(p.bang_chung or []) <= 1,
        "không chắc chắn": p.do_chac_chan != "chắc chắn",
    }


def diem_rui_ro(p: PhatBieu, ngu_canh: NguCanh, id_benh_nhan: int = 0) -> float:
    """0,0 = khong co dau hieu nao; 1,0 = du ca bon. Trong so deu nhau."""
    d = dac_trung(p, ngu_canh, id_benh_nhan)
    return sum(1 for v in d.values() if v) / len(DAU_HIEU)


def sang_loc(danh_sach: List[PhatBieu], nguong: float, ngu_canh: NguCanh,
             id_benh_nhan: int = 0) -> List[PhatBieu]:
    """Tra ve ban SAO; phat bieu co diem >= `nguong` bi danh `chưa giải quyết`.

    Khong xoa phat bieu nao. `sinh_benh_an._muc_cho` da co san luat dua moi ban
    ghi `chưa giải quyết` xuong muc CAN XAC NHAN — nen sang loc chi la danh dau,
    khong phai mot duong sinh thu hai. Bot duoc mot cho co the lech nhau.

    `nguong > 1` nghia la khong danh dau gi ca — day la moc doi chung, phai co
    trong duong danh doi chu khong duoc bo.
    """
    ra = []
    for p in danh_sach:
        q = PhatBieu(**p.to_dict())
        if diem_rui_ro(p, ngu_canh, id_benh_nhan) >= nguong:
            q.trang_thai = "chưa giải quyết"
        ra.append(q)
    return ra


def sang_loc_ngau_nhien(danh_sach: List[PhatBieu], ty_le: float,
                        seed: int) -> List[PhatBieu]:
    """Doi chung: day xuong DUNG `ty_le` phat bieu, chon NGAU NHIEN.

    Bat buoc phai co. Day 60% phat bieu xuong muc can xac nhan thi loi gan nham
    con lai tat nhien giam — ke ca khi chon bua. Duong danh doi ve tu diem rui
    ro chi co y nghia neu no nam DUOI duong ngau nhien o cung ty le day xuong:
    tuc cung mot cong sang loc thi bat duoc nhieu loi hon.

    Khong co ve nay thi bang so chi chung minh duoc mot dieu ai cung biet —
    viet it di thi sai it di.
    """
    import random

    rng = random.Random(seed)
    n = len(danh_sach)
    so_chon = int(round(ty_le * n))
    chon = set(rng.sample(range(n), so_chon)) if so_chon else set()

    ra = []
    for i, p in enumerate(danh_sach):
        q = PhatBieu(**p.to_dict())
        if i in chon:
            q.trang_thai = "chưa giải quyết"
        ra.append(q)
    return ra


def thong_ke(danh_sach: List[PhatBieu], ngu_canh: NguCanh,
             id_benh_nhan: int = 0) -> dict:
    dem = {t: 0 for t in DAU_HIEU}
    diem = []
    for p in danh_sach:
        for ten, co in dac_trung(p, ngu_canh, id_benh_nhan).items():
            dem[ten] += int(co)
        diem.append(diem_rui_ro(p, ngu_canh, id_benh_nhan))
    return {
        "so_phat_bieu": len(danh_sach),
        "dem_dau_hieu": dem,
        "diem_trung_binh": round(sum(diem) / len(diem), 4) if diem else 0.0,
    }
