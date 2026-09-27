# -*- coding: utf-8 -*-
"""Chay moi bo phat hien, GOP canh bao trung, chon canh bao CHINH, ap chinh sach D.

CHONG BAO DONG TRAN LAN (dac ta muc 38-39). "Bo toi bi hen" ghi thanh "benh
nhan bi hen" co the kich ca WRONG_SUBJECT, FAMILY_PATIENT_MIXUP, UNSUPPORTED...
Giao dien chi hien MOT canh bao chinh cho moi nguyen nhan; phan con lai la ma phu:
  1. cung MA tu nhieu bo phat hien -> gop lam mot (hop luot, hop trich dan)
  2. cung NHOM -> ma uu tien cao nhat la chinh, ma khac thanh `phu`
  3. khac nhom va DU NANG de doi trang thai -> giu rieng (toi da 2), con lai -> `phu`

CHINH SACH D (moi, chua dung de do). Chinh sach C (`cong_rui_ro.CHINH_SACH`) van la
chinh sach cua moi con so da bao cao; D chi bat khi goi ro `chinh_sach="D"`.
    bị thay thế      trang_thai 'bị thay thế' — khong vao than, giu dau vet
    cần xác nhận     khoa chan, HOAC dang mau thuan, HOAC co canh bao du nang
    đã kiểm chứng    con lai (van co the mang canh bao nhe de bac si luu y)
"""
from typing import Dict, List, Optional

from src import cong_rui_ro
from src.canh_bao import asr, phat_hien, toan_ca
from src.canh_bao.loai import (CAN_XEM, LOAI, LOI_PHAT_HIEN, NGHI_RUI_RO, ON_DINH, PHIEN_BAN, CanhBao, _HANG)

CHINH_SACH_D = "D-2026-09-24"
DA_KIEM_CHUNG = "đã kiểm chứng"
CAN_XAC_NHAN = "cần xác nhận"
BI_THAY_THE = "bị thay thế"

_KL = {LOI_PHAT_HIEN: 2, NGHI_RUI_RO: 1, CAN_XEM: 0}


def _gop_cung_ma(ds: List[CanhBao]) -> List[CanhBao]:
    theo = {}
    for c in ds:
        k = (c.phat_bieu_id, c.ma)
        if k not in theo:
            theo[k] = c
            continue
        a = theo[k]
        a.luot = sorted(set(a.luot) | set(c.luot))
        a.trich = a.trich + [t for t in c.trich if t not in a.trich]
        if c.bo_phat_hien not in a.bo_phat_hien.split("+"):
            a.bo_phat_hien += "+" + c.bo_phat_hien
        if _KL[c.ket_luan] > _KL[a.ket_luan]:
            a.ket_luan, a.ly_do = c.ket_luan, c.ly_do
        if _HANG[c.bat_dinh] < _HANG[a.bat_dinh]:
            a.bat_dinh = c.bat_dinh
        if _HANG[c.muc_do] > _HANG[a.muc_do]:
            a.muc_do = c.muc_do
    return list(theo.values())


def _khoa_sap(c: CanhBao):
    return (not c.anh_huong_trang_thai, LOAI[c.ma].uu_tien, -_HANG[c.muc_do], _HANG[c.bat_dinh])


def chon_chinh(ds: List[CanhBao]) -> dict:
    """-> {chinh, khac: [..], phu: [ma..], tat_ca: [..]} cho MOT phat bieu."""
    if not ds:
        return {"chinh": None, "khac": [], "phu": [], "tat_ca": []}
    ds = sorted(ds, key=_khoa_sap)
    # Canh bao "can xem" cua bo phat hien THU NGHIEM khong bao gio la canh bao chinh:
    # IMPORTANT_MODIFIER_DROPPED bao 84 lan, 0 lan trung loi (do 24/09/2026) — hien no
    # la tao bao dong gia. Van giu trong `tat_ca` de ghi nhat ky va do tiep.
    hien = [c for c in ds if not (c.ket_luan == CAN_XEM and c.tin_cay != ON_DINH)]
    if not hien:
        return {"chinh": None, "khac": [], "phu": [], "tat_ca": ds}
    ds = hien + [c for c in ds if c not in hien]
    chinh, khac, phu = ds[0], [], []
    nhom_da = {chinh.nhom}
    for c in hien[1:]:
        if c.nhom not in nhom_da and c.anh_huong_trang_thai and len(khac) < 2:
            khac.append(c)
            nhom_da.add(c.nhom)
        else:
            phu.append(c.ma)
    chinh.phu = sorted(set(chinh.phu) | {m for m in phu if m != chinh.ma})
    return {"chinh": chinh, "khac": khac, "phu": chinh.phu, "tat_ca": ds}


def trang_thai_D(p, cb: dict, kq_khoa=None) -> tuple:
    """-> (trang thai, ly do) theo chinh sach D."""
    if getattr(p, "trang_thai", "còn hiệu lực") == "bị thay thế":
        return BI_THAY_THE, "đã được thông tin mới thay thế"
    if kq_khoa is not None and kq_khoa.chan:
        c = cb["chinh"]
        return CAN_XAC_NHAN, (c.ly_do if c else "khoá bằng chứng chặn")
    if getattr(p, "trang_thai", "còn hiệu lực") == "chưa giải quyết":
        return CAN_XAC_NHAN, "hai nguồn mâu thuẫn, chưa xác nhận"
    for c in [cb["chinh"]] + cb["khac"]:
        if c is not None and c.anh_huong_trang_thai:
            return CAN_XAC_NHAN, f"{LOAI[c.ma].tieu_de}: {c.ly_do}"
    return DA_KIEM_CHUNG, ""


def chay(ps, hoi_thoai: str, kk: Optional[dict] = None, meta_asr: Optional[dict] = None) -> dict:
    """Canh bao cho MOT ca. `kk` = ket qua `khoa_bang_chung.khoa_ca` (tinh lai neu
    khong truyen). `meta_asr` = {so luot: {asr_confidence, nguoi_noi_chua_chac}}
    khi loi thoai den tu chep am; khong co thi khong sinh canh bao chep am."""
    from src import khoa_bang_chung
    ctx = phat_hien.NguCanh(hoi_thoai)
    if kk is None:
        kk = khoa_bang_chung.khoa_ca(ps, hoi_thoai)
    kq_theo_id = {k.id: k for k in kk["ket_qua"]}
    loai = {p.id: cong_rui_ro.loai_thong_tin(p) for p in ps}
    cac_sua = phat_hien.tim_dinh_chinh(ctx)

    tho: List[CanhBao] = []
    for p in ps:
        if getattr(p, "trang_thai", "còn hiệu lực") == "bị thay thế":
            continue
        tho += phat_hien.tu_khoa(ctx, p, kq_theo_id.get(p.id), loai[p.id])
        for f in phat_hien.BO_PHAT_HIEN:
            tho += f(ctx, p, loai[p.id])
        tho += phat_hien.dinh_chinh(ctx, p, loai[p.id], cac_sua)
    tho += toan_ca.mau_thuan(ctx, ps, loai)
    tho += toan_ca.ghi_lap(ctx, ps, loai)
    if meta_asr:
        tho += asr.canh_bao(ctx, ps, meta_asr, loai)
    gop = _gop_cung_ma(tho)

    theo_p: Dict[int, dict] = {}
    trang_thai: Dict[int, dict] = {}
    for p in ps:
        cb = chon_chinh([c for c in gop if c.phat_bieu_id == p.id])
        theo_p[p.id] = cb
        tt, ly = trang_thai_D(p, cb, kq_theo_id.get(p.id))
        trang_thai[p.id] = {"trang_thai": tt, "ly_do": ly}
    toan = toan_ca.bo_sot(ctx, kk.get("doan_chua_ghi", []))
    return {
        "phien_ban": PHIEN_BAN,
        "chinh_sach": CHINH_SACH_D,
        "theo_phat_bieu": theo_p,
        "toan_ca": toan,
        "trang_thai_D": trang_thai,
        "cac_dinh_chinh": [{"luot": d["luot"], "cu": d["cu"].chu, "moi": d["moi"].chu} for d in cac_sua],
    }


def ly_do_chan_D(kq: dict) -> Dict[int, str]:
    """{id: ly do} de `sinh_benh_an.sinh` dua sang CAN XAC NHAN theo chinh sach D."""
    return {i: v["ly_do"] for i, v in kq["trang_thai_D"].items() if v["trang_thai"] == CAN_XAC_NHAN}


def to_dict(kq: dict) -> dict:
    """Ban JSON — cho ban ghi ket qua, dich vu va giao dien."""
    def cb(c):
        return c.to_dict() if c is not None else None
    return {
        "phien_ban": kq["phien_ban"], "chinh_sach": kq["chinh_sach"],
        "theo_phat_bieu": {str(i): {"chinh": cb(v["chinh"]), "khac": [cb(c) for c in v["khac"]],
                                    "phu": v["phu"], "tat_ca": [cb(c) for c in v["tat_ca"]]}
                           for i, v in kq["theo_phat_bieu"].items()},
        "toan_ca": [cb(c) for c in kq["toan_ca"]],
        "trang_thai_D": {str(i): v for i, v in kq["trang_thai_D"].items()},
        "cac_dinh_chinh": kq["cac_dinh_chinh"],
    }
