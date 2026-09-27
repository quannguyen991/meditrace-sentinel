# -*- coding: utf-8 -*-
"""Do do DAY DU: ban nhap co bo sot phat bieu nao khong.

Giam cau sai chua du. Mot he thong khong bao gio ghi sai vi no khong ghi gi
thi vo dung. Nen phai do them chieu nguoc lai: moi phat bieu `con hieu luc`
co vao duoc ban nhap khong.

GIOI HAN THAT CUA PHEP DO NAY — phai ghi vao bao cao, khong duoc giau:

    No doi chieu ban nhap voi BANG PHAT BIEU, khong voi hoi thoai. Neu khau
    trich xuat da bo sot ngay tu dau thi bang phat bieu cung thieu, va phep
    do nay bao "day du" trong khi thong tin da mat.

    Vi the danh gia cuoi VAN phai doi chieu voi hoi thoai va nhan chuyen gia.
    Phep do nay chi bat duoc mot loai loi: mat mat o khau SINH, sau khi da
    trich duoc.

Nguyen tac bo sung: chi bo sung khi CO BANG CHUNG trong bang phat bieu.
Khong tu them muc kham hay ket qua ma hoi thoai chua cung cap.
"""
import re

from src import sinh_benh_an


def _chuan(s):
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def _co_trong(cum, van_ban):
    """So theo ranh gioi tu o CA HAI ben — giong `do_bo_chan_doan._co`.

    Chan mot ben thoi thi "ho" khop vao duoi chu "cho", va phep do bao
    "da the hien" cho mot noi dung chua he xuat hien.
    """
    cum = _chuan(cum)
    if not cum:
        return False
    return re.search(rf"(?<![\wÀ-ỹ]){re.escape(cum)}(?![\wÀ-ỹ])",
                     van_ban or "", re.I) is not None


def _bo_muc(van_ban, ten_muc):
    """Cat bo mot muc (tieu de + noi dung) khoi ban nhap."""
    khoi = (van_ban or "").split("\n\n")
    ra, i = [], 0
    while i < len(khoi):
        if khoi[i].strip() == ten_muc:
            i += 2                                   # bo ca tieu de lan noi dung
            continue
        ra.append(khoi[i])
        i += 1
    return "\n\n".join(ra)


def doi_chieu(phat_bieu, van_ban):
    """-> dict bon nhom, moi nhom la danh sach id phat bieu.

        da_the_hien     noi dung co trong ban nhap
        bo_sot          phat bieu con hieu luc ma noi dung KHONG co trong ban nhap
        lap             noi dung xuat hien nhieu hon mot lan
        can_xac_nhan    phat bieu da bi chuyen sang muc can xac nhan
    """
    than = (van_ban or "").split("CẦN XÁC NHẬN")[0]
    duoi = (van_ban or "").split("CẦN XÁC NHẬN")[1] if "CẦN XÁC NHẬN" in (van_ban or "") else ""
    # Dem lap thi PHAI bo muc LY DO KHAM BENH ra. Muc do nhac lai nguyen van
    # trieu chung chinh tu BENH SU HIEN TAI — do la dang benh an thong thuong,
    # khong phai loi lap. Khong bo thi trieu chung chinh luon bi bao lap.
    than_dem_lap = _bo_muc(than, "LÝ DO KHÁM BỆNH")

    ra = {"da_the_hien": [], "bo_sot": [], "lap": [], "can_xac_nhan": []}
    for p in phat_bieu:
        d = p.to_dict() if hasattr(p, "to_dict") else dict(p)
        nd = _chuan(d.get("noi_dung"))
        if d.get("trang_thai", "còn hiệu lực") != "còn hiệu lực":
            continue                                   # ban bi thay the: khong tinh
        # Xet THAN truoc roi moi den muc can xac nhan. Neu xet nguoc lai thi
        # hai ban ghi cung noi dung — mot con hieu luc, mot bi thay the — se
        # bi gop: ban con hieu luc khop vao muc can xac nhan cua ban kia va
        # bien mat khoi `da_the_hien`.
        if _co_trong(nd, than):
            ra["da_the_hien"].append(d.get("id"))
            so_lan = len(re.findall(
                rf"(?<![\wÀ-ỹ]){re.escape(nd)}(?![\wÀ-ỹ])", than_dem_lap, re.I))
            if so_lan > 1:
                ra["lap"].append(d.get("id"))
        elif _co_trong(nd, duoi):
            ra["can_xac_nhan"].append(d.get("id"))
        else:
            ra["bo_sot"].append(d.get("id"))
    return ra


def bo_sung(phat_bieu, van_ban, id_benh_nhan=0, ten_chu_the=None):
    """Them lai cac phat bieu bi bo sot — CHI nhung cai co trong bang.

    Tra ve (van_ban_moi, danh_sach_id_da_them).

    Khong sinh chu moi: dung dung `sinh_benh_an.dien_dat` nhu khau sinh, roi
    noi vao dung muc ma bang tra chi dinh. Neu de mo hinh viet phan bo sung
    thi chinh cho nay lai thanh nguon bia thong tin.
    """
    ket = doi_chieu(phat_bieu, van_ban)
    thieu = set(ket["bo_sot"])
    if not thieu:
        return van_ban, []

    ten_chu_the = ten_chu_the or {}
    theo_muc, da_them = {}, []
    for p in phat_bieu:
        d = p.to_dict() if hasattr(p, "to_dict") else dict(p)
        if d.get("id") not in thieu:
            continue
        muc, ly_do = sinh_benh_an._muc_cho(d, id_benh_nhan)
        ten = ten_chu_the.get(d.get("chu_the_id")) \
            if d.get("chu_the_id") != id_benh_nhan else None
        cum = sinh_benh_an.dien_dat(d, ten)
        if ly_do:
            cum = f"{cum} — {ly_do}"
        theo_muc.setdefault(muc, []).append(cum)
        da_them.append(d.get("id"))

    khoi = (van_ban or "").split("\n\n")
    ra = []
    i = 0
    while i < len(khoi):
        ra.append(khoi[i])
        ten_muc = khoi[i].strip()
        if ten_muc in theo_muc and i + 1 < len(khoi):
            ra.append(khoi[i + 1].rstrip(".") + ". " + ". ".join(theo_muc.pop(ten_muc)) + ".")
            i += 2
            continue
        i += 1
    for muc in sinh_benh_an.THU_TU_MUC:
        if muc in theo_muc:
            ra.append(muc)
            ra.append(". ".join(theo_muc.pop(muc)) + ".")
    return "\n\n".join(ra), da_them


def ty_le(phat_bieu, van_ban):
    """Mot so de theo doi giua cac nhanh. Mau so la so phat bieu con hieu luc."""
    k = doi_chieu(phat_bieu, van_ban)
    mau_so = len(k["da_the_hien"]) + len(k["bo_sot"]) + len(k["can_xac_nhan"])
    if mau_so == 0:
        return None
    return {"con_hieu_luc": mau_so,
            "da_the_hien": len(k["da_the_hien"]),
            "bo_sot": len(k["bo_sot"]),
            "can_xac_nhan": len(k["can_xac_nhan"]),
            "ty_le_day_du": len(k["da_the_hien"]) / mau_so}
