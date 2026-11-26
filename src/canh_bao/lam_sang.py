# -*- coding: utf-8 -*-
"""Canh bao KIEN THUC LAM SANG trong lop canh bao: lieu vuot tran, tuong tac thuoc, ke thuoc
nguoi benh dang di ung (25/11/2026).

Truoc ngay nay cac kiem tra nay chi nam o truong `lam_sang_nang_cao` cua `dich_vu` — mot he
song song khong co ma, khong co muc tin cay, khong di qua cach gop canh bao. Gio chung la ma
cua lop canh bao, nhom CLINICAL_KNOWLEDGE, tin cay THU_NGHIEM (chi hien, khong doi trang thai).

So lieu (lieu toi da) doc tu `tri_thuc_thuoc`. Muc `da_duyet=false` -> ket luan CAN_XEM, khong
bao gio cao hon. Bang tuong tac (`duoc_ly_lam_sang.BANG_TUONG_TAC_THUOC`) chua co nguon nen
luon CAN_XEM. Chong chi dinh o day chi la "ke dung chat nguoi benh dang di ung" — khong can
nguong nao; di ung cheo theo nhom (penicillin -> amoxicillin) can tri thuc co nguon, chua lam.
"""
import re
from typing import List, Optional

from src import tri_thuc_thuoc
from src.canh_bao.loai import CAN_XEM, CAO, NGHI_RUI_RO, THAP, TRUNG, CanhBao, muc_do
from src.canh_bao.phat_hien import NguCanh, _thuong

_SO_CHU = {"một": 1, "hai": 2, "ba": 3, "bốn": 4, "tư": 4, "năm": 5, "sáu": 6, "bảy": 7, "tám": 8}
_SO = r"(\d+(?:[.,]\d+)?|" + "|".join(_SO_CHU) + r")"
_LIEU = re.compile(_SO + r"\s*(mg|g|gam|mcg|µg)(?!\w)")
_LAN_NGAY = re.compile(r"(?:ngày|mỗi ngày)\s*" + _SO + r"\s*lần|" + _SO + r"\s*lần\s*(?:/|một|mỗi|trong)?\s*ngày")
_MOI_GIO = re.compile(r"mỗi\s*" + _SO + r"\s*(?:giờ|tiếng)|cách\s*" + _SO + r"\s*(?:giờ|tiếng)")
_MOT_LAN = re.compile(r"(?<!\w)(mỗi (sáng|tối|trưa|chiều)|một lần|ngày một lần|1 lần|uống một liều)(?!\w)")


def _so(s: str) -> float:
    return float(_SO_CHU.get(s, None) or s.replace(",", "."))


def lieu_ngay_mg(thuoc: Optional[dict], noi_dung: str) -> Optional[float]:
    """Tong lieu mot ngay (mg) tu `thuoc` {"lieu", "so_lan"} hoac tu noi dung. None khi
    khong doc duoc ca lieu lan so lan."""
    thuoc = thuoc or {}
    t_lieu = _thuong(str(thuoc.get("lieu") or "")) or _thuong(noi_dung)
    t_lan = _thuong(str(thuoc.get("so_lan") or "")) or _thuong(noi_dung)
    m = _LIEU.search(t_lieu) or _LIEU.search(_thuong(noi_dung))
    if not m:
        return None
    mg = _so(m.group(1)) * {"g": 1000, "gam": 1000, "mcg": 0.001, "µg": 0.001}.get(m.group(2), 1)
    for van in (t_lan, _thuong(noi_dung)):
        n = _LAN_NGAY.search(van)
        if n:
            return mg * _so(n.group(1) or n.group(2))
        g = _MOI_GIO.search(van)
        if g:
            return mg * (24 / _so(g.group(1) or g.group(2)))
        if _MOT_LAN.search(van):
            return mg
    return None


def _con(p) -> bool:
    return getattr(p, "trang_thai", "còn hiệu lực") != "bị thay thế"


def _la_di_ung(p) -> bool:
    return "dị ứng" in _thuong(p.noi_dung)


def _hoat_chat(p) -> Optional[str]:
    ten = (getattr(p, "thuoc", None) or {}).get("ten") or ""
    return tri_thuc_thuoc.hoat_chat(ten) if ten else tri_thuc_thuoc.hoat_chat(p.noi_dung)


def _thuoc_dang_dung(ps) -> list:
    """(hoat chat, phat bieu) cua thuoc benh nhan dang dung hoac duoc ke — khong tinh dong di
    ung, dong phu dinh, dong bi thay the, dong cua nguoi khac."""
    ra = []
    for p in ps:
        if not _con(p) or getattr(p, "phu_dinh", False) or _la_di_ung(p) or getattr(p, "chu_the_id", 0) != 0:
            continue
        hc = _hoat_chat(p)
        if hc:
            ra.append((hc, p))
    return ra


def _cb(ma, p, ctx, ly_do, ket_luan, loai_tt="thuoc", trich=None):
    return CanhBao(ma=ma, phat_bieu_id=p.id, luot=ctx.dan(p), trich=trich or [p.noi_dung], ly_do=ly_do,
                   ket_luan=ket_luan, bat_dinh=TRUNG, bo_phat_hien=f"lam_sang:{ma.lower()}",
                   muc_do=muc_do(ma, loai_tt), loai_tt=loai_tt)


def quet(ctx: NguCanh, ps) -> List[CanhBao]:
    ra: List[CanhBao] = []
    dang_dung = _thuoc_dang_dung(ps)
    # 1. lieu vuot tran (nguoi lon; tre em can can nang — o kiem_duyet_bhyt)
    for hc, p in dang_dung:
        l = tri_thuc_thuoc.lieu_toi_da(hc, "nguoi_lon")
        ngay = lieu_ngay_mg(getattr(p, "thuoc", None), p.noi_dung)
        if l is None or ngay is None or ngay <= l.gia_tri:
            continue
        ra.append(_cb("DOSE_OVER_MAX", p, ctx,
                      f"“{p.noi_dung}” = {ngay:g} mg/ngày, vượt mức tối đa người lớn {l.gia_tri:g} {l.don_vi} của "
                      f"{hc}" + ("" if l.da_duyet else " (số chưa được duyệt — chỉ để bác sĩ xem lại)") + ".",
                      NGHI_RUI_RO if l.da_duyet else CAN_XEM))
    # 2. tuong tac thuoc (bang chua co nguon -> luon CAN_XEM)
    if len(dang_dung) >= 2:
        from src.duoc_ly_lam_sang import ClinicalPharmacovigilanceEngine as Dl
        theo_hc = {}
        for hc, p in dang_dung:
            theo_hc.setdefault(hc, p)
        for tt in Dl.kiem_tra_tuong_tac(list(theo_hc)):
            cap = [(hc, p) for hc, p in theo_hc.items() if tt.thuoc_1 in hc or tt.thuoc_2 in hc]
            if len(cap) < 2:
                continue
            (h1, p1), (h2, p2) = cap[0], cap[-1]
            ra.append(_cb("DRUG_INTERACTION", p2, ctx,
                          f"{h1} (dòng #{p1.id}) và {h2} (dòng #{p2.id}): {tt.muc_do} — {tt.hau_qua}. "
                          "Bảng tương tác chưa được duyệt nguồn.", CAN_XEM, trich=[p1.noi_dung, p2.noi_dung]))
    # 3. ke / dung dung chat nguoi benh dang di ung (khang dinh)
    di_ung = []
    di_ung_tho = []
    for p in ps:
        if _con(p) and _la_di_ung(p) and not getattr(p, "phu_dinh", False) and getattr(p, "chu_the_id", 0) == 0:
            # Chi ve ngay sau "dị ứng": "dị ứng penicillin, đang dùng augmentin" -> penicillin.
            sau = re.sub(r".*?dị ứng\s*(với\s*)?", "", _thuong(p.noi_dung), count=1)
            ve_dau = re.split(r"[,;.]|(?<!\w)(đang|nhưng|còn|và)(?!\w)", sau)[0].strip()
            hc = tri_thuc_thuoc.hoat_chat(ve_dau)
            if hc:
                di_ung.append((hc, p))
            if ve_dau:
                di_ung_tho.append((ve_dau, p))
    cap_da_bao_truc_tiep = set()
    for hc_du, p_du in di_ung:
        for hc, p in dang_dung:
            if hc == hc_du or any(hc_du in t for t in tri_thuc_thuoc.ten_cua(hc)):
                # Anh xa biet duoc -> hoat chat cung la tri thuc chua duyet: CAN_XEM cho toi khi ca
                # hai muc da_duyet (ra soat 25/11).
                duyet = all((tri_thuc_thuoc._theo_hoat_chat().get(x) or {}).get("da_duyet") for x in (hc, hc_du))
                cap_da_bao_truc_tiep.add((p.id, p_du.id))
                ra.append(_cb("CONTRAINDICATION", p, ctx,
                              f"“{p.noi_dung}” chứa {hc_du}, nhưng dòng #{p_du.id} ghi người bệnh dị ứng {hc_du}.",
                              NGHI_RUI_RO if duyet else CAN_XEM, loai_tt="di_ung", trich=[p.noi_dung, p_du.noi_dung]))

    # 4. di ung cheo theo nhom ATC / chuoi nhanh hoa hoc (CROSS_ALLERGY, khong phat CONTRAINDICATION)
    if di_ung_tho:
        from src.di_ung_cheo import CHONG_CHI_DINH as _DU_CAM, kiem_tra_di_ung_cheo
        thuoc_theo_pb = []
        for p in ps:
            if not _con(p) or getattr(p, "phu_dinh", False) or _la_di_ung(p) or getattr(p, "chu_the_id", 0) != 0:
                continue
            ten_t = ((getattr(p, "thuoc", None) or {}).get("ten") or "").strip() or _hoat_chat(p) or ""
            if ten_t:
                thuoc_theo_pb.append((ten_t, p))
        for chat_du, p_du in di_ung_tho:
            for ten_t, p in thuoc_theo_pb:
                if (p.id, p_du.id) in cap_da_bao_truc_tiep:
                    continue
                ket_qua_cheo = kiem_tra_di_ung_cheo([chat_du], [ten_t])
                if not ket_qua_cheo:
                    continue
                muc_cao_nhat = ket_qua_cheo[0]
                kl = NGHI_RUI_RO if muc_cao_nhat["muc_do"] == _DU_CAM else CAN_XEM
                ra.append(_cb(
                    "CROSS_ALLERGY", p, ctx,
                    f"“{p.noi_dung}” ({muc_cao_nhat['thuoc']}) có nguy cơ dị ứng chéo [{muc_cao_nhat['nhom_cheo']}] "
                    f"với tiền sử dị ứng {muc_cao_nhat['di_ung_goc']} ở dòng #{p_du.id}. {muc_cao_nhat['khuyen_cao_thay_the']}",
                    kl, loai_tt="di_ung", trich=[p.noi_dung, p_du.noi_dung],
                ))
    return ra
