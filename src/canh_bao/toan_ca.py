# -*- coding: utf-8 -*-
"""Canh bao MUC TOAN CA: bo sot, mau thuan trong ban ghi, ghi lap.

BO SOT KHONG TU LAM LAI. `khoa_bang_chung.doan_chua_ghi` da tim doan hoi thoai co
noi dung lam sang ma khong phat bieu nao dan toi. O day chi PHAN LOAI doan do
(di ung? thuoc? phu dinh? con so?) de bac si biet doan nao dang lo nhat. Khong tu
bo sung vao ban nhap — thong tin do chua qua khoa.
"""
import re
from itertools import combinations
from typing import List

from src.canh_bao import so_lieu
from src.canh_bao.loai import CAN_XEM, CAO, LOI_PHAT_HIEN, NGHI_RUI_RO, THAP, TRUNG, CanhBao, muc_do
from src.canh_bao.phat_hien import (DAU_SUA, DIEU_KIEN_THEM, KHONG_NHO, TUONG_LAI, NguCanh, _co,
                                    _dang_dung, _thuong, _tu)
from src.khoa_bang_chung import DAU_NGHI
from src.thuc_the import THUOC_TU_DIEN

BO_SOT = (
    ("OMITTED_ALLERGY", re.compile(r"(?<!\w)(dị ứng|mẫn cảm|nổi mẩn (khi|sau))(?!\w)")),
    ("OMITTED_MEDICATION", re.compile(r"(?<!\w)((uống|dùng|xịt|tiêm|bôi|kê) thuốc|thuốc \w+|\d+ ?(mg|viên))(?!\w)")),
    ("OMITTED_CORRECTION", DAU_SUA),
    ("OMITTED_NEGATION", re.compile(r"(?<!\w)(không|chưa|chẳng) (bị|có|sốt|ho|đau|thấy|nôn|khó)(?!\w)")),
    ("OMITTED_UNCERTAINTY", re.compile(DAU_NGHI.pattern + "|" + KHONG_NHO.pattern)),
)


def bo_sot(ctx: NguCanh, doan_chua_ghi: List[dict]) -> List[CanhBao]:
    ra = []
    for d in doan_chua_ghi:
        doan, so = d["doan"], d["luot"]
        t = _thuong(doan)
        ma = None
        # di ung truoc tu dien thuoc: "toi di ung penicillin" la di ung, khong phai thuoc
        for m, bt in BO_SOT:
            if ma is None and bt.search(t):
                ma = m
        if (ma is None or ma != "OMITTED_ALLERGY") and THUOC_TU_DIEN.search(t):
            ma = "OMITTED_MEDICATION"
        if ma is None:
            so_ = so_lieu.tach(doan)
            if so_:
                ma = "OMITTED_DURATION" if all(s.ho == "thoi_gian" for s in so_) else "OMITTED_NUMERIC_VALUE"
        if ma is None and ctx.la_nv(so) and (DIEU_KIEN_THEM.search(t) or TUONG_LAI.search(t)):
            ma = "OMITTED_PLAN"
        ma = ma or "POSSIBLE_IMPORTANT_OMISSION"
        # Loai chung chung: 792/887 canh bao bo sot, 2,8% trung cho dap an bi sot (do
        # 24/09/2026). Giu o backend de do, KHONG hien cho bac si (can_xem).
        chung = ma == "POSSIBLE_IMPORTANT_OMISSION"
        ra.append(CanhBao(ma=ma, phat_bieu_id=None, luot=[so], trich=[doan],
                          ly_do=f"Lượt {so} ({d.get('vai') or 'không rõ vai'}): “{doan}” — không dòng nào dẫn tới.",
                          ket_luan=CAN_XEM if chung else NGHI_RUI_RO, bat_dinh=CAO if chung else TRUNG, bo_phat_hien="toan_ca:bo_sot",
                          muc_do=muc_do(ma, "di_ung" if ma == "OMITTED_ALLERGY" else
                                        "thuoc" if ma == "OMITTED_MEDICATION" else "khac")))
    return ra


def _con(p):
    return getattr(p, "trang_thai", "còn hiệu lực") != "bị thay thế"


def _nd_bo_phu_dinh(p):
    return _tu(re.sub(r"(?<!\w)(không|chưa|chẳng|chả|hết)(?!\w)", " ", _thuong(p.noi_dung)))


def _dien_bien(p, q):
    """Hai phat bieu lien he bang dien bien, hoac mang moc thoi gian khac nhau:
    'hom qua dau' / 'hom nay het dau' — khong phai mau thuan."""
    if (getattr(p, "quan_he", None) == "diễn biến" and getattr(p, "quan_he_voi", None) == q.id) or \
            (getattr(q, "quan_he", None) == "diễn biến" and getattr(q, "quan_he_voi", None) == p.id):
        return True
    mp, mq = getattr(p, "moc_thoi_gian", None), getattr(q, "moc_thoi_gian", None)
    return bool(mp and mq and _thuong(mp) != _thuong(mq))


def _sau_di_ung(p) -> str:
    m = re.search(r"dị ứng\s*(với\s*)?(.*)$", _thuong(p.noi_dung))
    return (m.group(2) if m else "").strip(" .,")


def _trai_di_ung(am, duong) -> bool:
    """'khong di ung (gi)' trai voi MOI di ung; 'khong di ung thuoc' chi trai voi di
    ung mot THUOC ('di ung dam sua bo' khong trai — do 24/09/2026, ca asr_010_A);
    con lai chi trai khi cung chat."""
    chat_am, chat_duong = _sau_di_ung(am), _sau_di_ung(duong)
    if chat_am in ("", "gì", "gì cả", "gì hết"):
        return True
    if chat_am.startswith("thuốc"):
        return bool(getattr(duong, "thuoc", None)) or bool(THUOC_TU_DIEN.search(chat_duong)) or             bool(re.search(r"(?<!\w)(thuốc|kháng sinh|\w+cillin|\w+micin)(?!\w)", chat_duong))
    return bool(chat_am) and (chat_am in chat_duong or chat_duong in chat_am)


def mau_thuan(ctx: NguCanh, ps, loai_theo_id) -> List[CanhBao]:
    ra = []
    con = [p for p in ps if _con(p)]
    for p, q in combinations(con, 2):
        if getattr(p, "chu_the_id", 0) != getattr(q, "chu_the_id", 0):
            continue
        luot = sorted(set(ctx.dan(p)) | set(ctx.dan(q)))
        np_, nq = _thuong(p.noi_dung), _thuong(q.noi_dung)
        ma, kl = None, LOI_PHAT_HIEN
        # "khong di ung thuoc" va "di ung penicillin" cung mot nguoi
        if "dị ứng" in np_ and "dị ứng" in nq and bool(getattr(p, "phu_dinh", False)) != bool(
                getattr(q, "phu_dinh", False)):
            am, duong = (p, q) if getattr(p, "phu_dinh", False) else (q, p)
            if _trai_di_ung(am, duong):
                ma = "INTERNAL_CONTRADICTION"
        tp, tq = getattr(p, "thuoc", None) or {}, getattr(q, "thuoc", None) or {}
        # Mot ben la Y LENH cua bac si ("ngung panadol" sau khi nguoi benh ke dang uong)
        # thi la ke hoach moi, khong phai mau thuan (do 24/09/2026: 1/20 lan dung).
        y_lenh = any(getattr(x, "tinh_huong", "") == "kế hoạch" or getattr(x, "hanh_vi", "") == "kế hoạch"
                     or (ctx.dan(x) and all(ctx.la_nv(s) for s in ctx.dan(x))) for x in (p, q))
        if ma is None and not y_lenh and tp.get("ten") and tq.get("ten") and _co(tp["ten"], _thuong(tq["ten"])) \
                and {tp.get("trang_thai_dung"), tq.get("trang_thai_dung")} == {"đang dùng", "đã ngừng"}:
            ma = "CONTRADICTORY_MEDICATION_STATUS"
        if ma is None and bool(getattr(p, "phu_dinh", False)) != bool(getattr(q, "phu_dinh", False)) \
                and _nd_bo_phu_dinh(p) and _nd_bo_phu_dinh(p) == _nd_bo_phu_dinh(q) and not _dien_bien(p, q):
            ma, kl = "CONTRADICTORY_INFORMATION", NGHI_RUI_RO
        if ma is None:
            continue
        for x, y in ((p, q), (q, p)):
            ra.append(CanhBao(ma=ma, phat_bieu_id=x.id, luot=luot, trich=[x.noi_dung, y.noi_dung],
                              ly_do=f"“{x.noi_dung}” trái với dòng #{y.id} “{y.noi_dung}”.",
                              ket_luan=kl, bat_dinh=THAP if kl == LOI_PHAT_HIEN else TRUNG,
                              bo_phat_hien="toan_ca:mau_thuan", muc_do=muc_do(ma, loai_theo_id.get(x.id, "khac")), loai_tt=loai_theo_id.get(x.id, "khac")))
    return ra


def ghi_lap(ctx: NguCanh, ps, loai_theo_id) -> List[CanhBao]:
    ra, da = [], {}
    for p in ps:
        if not _con(p):
            continue
        k = (getattr(p, "chu_the_id", 0), bool(getattr(p, "phu_dinh", False)))
        nd = _thuong(p.noi_dung)
        tu = _tu(p.noi_dung)
        for q_nd, q_tu, q in da.get(k, []):
            if nd == q_nd:
                ma = "DUPLICATE_INFORMATION"
            elif tu and q_tu and len(tu & q_tu) / len(tu | q_tu) >= 0.85:
                ma = "SEMANTIC_DUPLICATE"
            else:
                continue
            ra.append(CanhBao(ma=ma, phat_bieu_id=p.id, luot=ctx.dan(p), trich=[q.noi_dung],
                              ly_do=f"Giống dòng #{q.id} “{q.noi_dung}”.", ket_luan=CAN_XEM, bat_dinh=THAP,
                              bo_phat_hien="toan_ca:ghi_lap", muc_do=muc_do(ma, loai_theo_id.get(p.id, "khac")), loai_tt=loai_theo_id.get(p.id, "khac")))
            break
        da.setdefault(k, []).append((nd, tu, p))
    return ra
