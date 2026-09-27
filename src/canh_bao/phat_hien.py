# -*- coding: utf-8 -*-
"""Bo phat hien canh bao THEO TUNG PHAT BIEU — toan bo la LUAT, khong mo hinh.

NGUYEN TAC (dac ta muc 40-41, 51):
  - doi chieu phat bieu voi CHINH CAC LUOT HOI THOAI no dan, khong voi bang phat
    bieu hay kien thuc y khoa
  - phat hien != sua: khong bo phat hien nao doi noi dung phat bieu
  - moi canh bao phai noi duoc CAU NAO trong hoi thoai lam no bao dong
  - khong co bang chung thi khong ket luan "khong co" (absence != negative)

Ma loi cua `khoa_bang_chung` KHONG duoc tinh lai o day: `tu_khoa` chi anh xa
chung sang phan loai moi. Bo phat hien moi chi lam viec khoa chua lam.
"""
import re
import unicodedata
from typing import Dict, List, Optional, Tuple

from src import chuan_hoa
from src.canh_bao import so_lieu
from src.canh_bao.loai import (CAN_XEM, CAO, LOI_PHAT_HIEN, NGHI_RUI_RO, THAP, TRUNG,
                               CanhBao, muc_do)
from src.khoa_bang_chung import DAU_DIEU_KIEN, DAU_NGHI
from src.phat_bieu import la_vai_nhan_vien
from src.thuc_the import TU_DIEN_THUOC, tach_luot
from src.thuoc_do_quy_gan import _tu_noi_dung


# ----------------------------------------------------------------- ngu canh
def _nfc(s):
    return unicodedata.normalize("NFC", str(s or ""))


def _thuong(s):
    return re.sub(r"\s+", " ", _nfc(s).lower()).strip()


def _tu(s):
    return set(_tu_noi_dung(chuan_hoa.chuan_hoa(s)))


def cac_cau(van: str) -> List[str]:
    """Tach menh de: dau cau, cham phay, va "nhung" (hai y trai nhau)."""
    ra = []
    for c in re.split(r"[.!?;…]+|,?\s+nhưng\s+", _nfc(van)):
        c = c.strip(" ,")
        if c:
            ra.append(c)
    return ra


class NguCanh:
    """Hoi thoai cua mot ca, doc mot lan, dung chung cho moi bo phat hien."""

    def __init__(self, hoi_thoai: str):
        self.hoi_thoai = hoi_thoai
        self.luot: Dict[int, Tuple[str, str]] = {
            so: (str(vai or "").lower(), _nfc(van)) for so, vai, van in tach_luot(hoi_thoai)}
        self.toan_van = _thuong(" ".join(v for _vai, v in self.luot.values()))

    def la_nv(self, so) -> bool:
        return la_vai_nhan_vien(self.luot[so][0]) if so in self.luot else False

    def dan(self, p) -> List[int]:
        return sorted({n for n in (getattr(p, "bang_chung", None) or []) if n in self.luot})

    def van_dan(self, p, kem_cau_hoi=True) -> str:
        """Van ban cac luot duoc dan, kem cau hoi cua bac si dung ngay truoc mot
        cau tra loi (giong K2 cua khoa: 'Da, khong a' chi co nghia khi doc kem cau hoi)."""
        so = self.dan(p)
        them = []
        if kem_cau_hoi:
            for s in so:
                if not self.la_nv(s) and (s - 1) in self.luot and self.la_nv(s - 1) and (s - 1) not in so:
                    them.append(s - 1)
        return " ".join(self.luot[s][1] for s in sorted(set(so) | set(them)))

    def cau_gan_nhat(self, p, chi_luot=None) -> Tuple[Optional[int], str]:
        """Menh de trong cac luot duoc dan trung nhieu tu noi dung nhat voi phat bieu."""
        tu_p = _tu(p.noi_dung)
        tot, ra = -1, (None, "")
        for s in (chi_luot or self.dan(p)):
            for c in cac_cau(self.luot[s][1]):
                k = len(tu_p & _tu(c))
                if k > tot:
                    tot, ra = k, (s, c)
        return ra

    def tim_luot(self, cum: str, bo_qua=()) -> List[int]:
        cum = _thuong(cum)
        return [s for s, (_v, van) in self.luot.items() if s not in bo_qua and _co(cum, _thuong(van))]


def _co(ten: str, van: str) -> bool:
    """Ten thuoc / chat co trong van ban: khop nguyen tu, hoac 6 ky tu dau cho ten
    dai ('amlodipin' ~ 'amlodipine', 'prednisolon' ~ 'prednisolone')."""
    ten = _thuong(ten)
    if not ten:
        return False
    if re.search(rf"(?<!\w){re.escape(ten)}(?!\w)", van):
        return True
    if len(ten) >= 7 and " " not in ten:
        return re.search(rf"(?<!\w){re.escape(ten[:6])}\w*", van) is not None
    return False


def tao(ctx, p, ma, luot, trich, ly_do, ket_luan, bat_dinh, bo, loai_tt) -> CanhBao:
    return CanhBao(ma=ma, phat_bieu_id=p.id if p is not None else None, luot=sorted(set(luot)),
                   trich=[t for t in trich if t], ly_do=ly_do, ket_luan=ket_luan,
                   bat_dinh=bat_dinh, bo_phat_hien=bo, muc_do=muc_do(ma, loai_tt), loai_tt=loai_tt)


def _la_bn(p):
    return getattr(p, "chu_the_id", 0) == 0


def _thuc_te(p):
    return getattr(p, "tinh_huong", "thực tế") == "thực tế"


def _chac(p):
    return getattr(p, "do_chac_chan", "chắc chắn") == "chắc chắn"


# ----------------------------------------------------------------- 1. tu khoa
# Anh xa ma cua `khoa_bang_chung` -> (ma moi, ket luan, bat dinh). Khoa CHAN =
# co bang chung doi nghich -> LOI_PHAT_HIEN; khoa CANH BAO = thieu bang chung
# khang dinh -> NGHI_RUI_RO.
TU_KHOA = {
    "khong_trich_dan": ("EVIDENCE_MISSING", NGHI_RUI_RO, TRUNG),
    "luot_khong_ton_tai": ("WRONG_EVIDENCE", LOI_PHAT_HIEN, THAP),
    "trich_khong_co": ("FABRICATED_QUOTE", LOI_PHAT_HIEN, THAP),
    "trich_lech_luot": ("WRONG_EVIDENCE", CAN_XEM, THAP),
    "noi_dung_khong_khop": ("UNSUPPORTED_INFORMATION", NGHI_RUI_RO, TRUNG),
    "phuong_ngu_can_hoi": ("OVER_NORMALIZATION", NGHI_RUI_RO, TRUNG),
    "chu_the_nguoi_ke": ("WRONG_SUBJECT", LOI_PHAT_HIEN, THAP),
    "chu_the_benh_nhan": ("WRONG_SUBJECT", LOI_PHAT_HIEN, THAP),
    "chu_the_nguoi_khac": ("FAMILY_PATIENT_MIXUP", NGHI_RUI_RO, TRUNG),
    "chu_the_suy_tu_nguoi_noi": ("SPEAKER_SUBJECT_MISMATCH", NGHI_RUI_RO, CAO),
    "chu_the_chua_ro": ("SUBJECT_AMBIGUOUS", NGHI_RUI_RO, TRUNG),
    "dieu_kien": ("CONDITION_AS_FACT", LOI_PHAT_HIEN, THAP),
    "vuot_muc_nghi": ("CERTAINTY_INCREASED", LOI_PHAT_HIEN, THAP),
    "vuot_muc_chua_ghi_nhan": ("NEGATION_FLIP", LOI_PHAT_HIEN, THAP),
    "phu_dinh_vuot_muc": ("NOT_YET_AS_NEGATIVE", NGHI_RUI_RO, TRUNG),
    "co_tu_phu_dinh": ("POSSIBLE_NEGATION_ERROR", NGHI_RUI_RO, CAO),
    "moc_khong_thay": ("TEMPORAL_MISMATCH", NGHI_RUI_RO, TRUNG),
    "mau_thuan": ("CONTRADICTION_UNRESOLVED", LOI_PHAT_HIEN, THAP),
    "lieu_khong_thay": ("DOSE_MISMATCH", LOI_PHAT_HIEN, THAP),
    "chi_tiet_thuoc_khong_thay": ("FREQUENCY_MISMATCH", NGHI_RUI_RO, TRUNG),
    "duong_dung_khong_thay": ("ROUTE_MISMATCH", NGHI_RUI_RO, TRUNG),
}


def tu_khoa(ctx: NguCanh, p, kq, loai_tt) -> List[CanhBao]:
    if kq is None:
        return []
    from src.khoa_bang_chung import LY_DO
    ra = []
    for ma_khoa in list(kq.chan) + list(kq.canh_bao):
        if ma_khoa not in TU_KHOA:
            continue
        ma, kl, bd = TU_KHOA[ma_khoa]
        # Nguoi NHA noi "vo em", "bo toi" thuong la dang goi CHINH benh nhan (nguoi nha
        # dua benh nhan di kham). Do 24/09/2026 tren 4 bo thu thach: 0/50 lan khop dung
        # loi sai chu the. Chi con la canh bao can xem; benh nhan TU noi "bo toi…" thi
        # moi la dau hieu nghi ngo.
        if ma_khoa == "chu_the_nguoi_khac":
            dan_ = ctx.dan(p)
            if dan_ and ctx.luot[max(dan_)][0] != "bệnh nhân":
                kl, bd = CAN_XEM, CAO
        if ma_khoa == "chi_tiet_thuoc_khong_thay" and not (getattr(p, "thuoc", None) or {}).get("so_lan"):
            ma = "TEMPORAL_MISMATCH"     # luc bat dau / luc ngung, khong phai so lan
        luot = sorted({s for s, _a, _b in kq.doan}) or ctx.dan(p)
        trich = [ctx.luot[s][1][a:b] for s, a, b in kq.doan] or [ctx.luot[s][1] for s in ctx.dan(p)[:2]]
        ra.append(tao(ctx, p, ma, luot, trich, LY_DO.get(ma_khoa, ma_khoa), kl, bd,
                      f"khoa:{ma_khoa}", loai_tt))
    return ra


# ----------------------------------------------------------------- 2. con so
def _so_phat_bieu(p) -> List[so_lieu.SoLieu]:
    phan = [p.noi_dung, getattr(p, "moc_thoi_gian", None) or ""]
    t = getattr(p, "thuoc", None) or {}
    phan += [t.get(k) or "" for k in ("lieu", "so_lan", "bat_dau", "ngung")]
    ra, da = [], set()
    for s in so_lieu.tach(" ; ".join(phan)):
        k = (s.gia_tri, s.tren, s.don_vi)
        if k not in da:
            da.add(k)
            ra.append(s)
    return ra


_MA_THEO_HO = {"lieu": "DOSE_MISMATCH", "so_lan": "FREQUENCY_MISMATCH", "thoi_gian": "DURATION_MISMATCH"}


def con_so(ctx: NguCanh, p, loai_tt) -> List[CanhBao]:
    """So trong ban ghi phai co trong LUOT DUOC DAN (cung don vi). Bat: sai so, sai
    don vi, lech thap phan, mat chu 'khoang', khoang bi rut thanh mot so.
    Mot so bi DINH CHINH ('7 ngay... a khong, 10 ngay') van co trong luot dan —
    bo phat hien `dinh_chinh` lo phan do, o day khong bao."""
    ps = _so_phat_bieu(p)
    if not ps:
        return []
    dan = ctx.dan(p)
    van = ctx.van_dan(p)
    ev = so_lieu.tach(van)
    ra = []
    for s in ps:
        cung_dv = [e for e in ev if e.don_vi == s.don_vi and e.ho == s.ho]
        khop = [e for e in cung_dv if e.chua(s.gia_tri) or (s.la_khoang and e.la_khoang
                                                             and e.gia_tri == s.gia_tri and e.tren == s.tren)]
        if khop:
            e = khop[0]
            if e.la_khoang and not s.la_khoang:
                ra.append(tao(ctx, p, "RANGE_COLLAPSED", dan, [e.chu],
                              f"Câu gốc nói “{e.chu}”, bản ghi chỉ còn “{s.chu}”.",
                              LOI_PHAT_HIEN, THAP, "con_so", loai_tt))
            elif e.uoc and not s.uoc and not re.search(r"khoảng|tầm|chừng|ước|hình như", _thuong(p.noi_dung)):
                ra.append(tao(ctx, p, "APPROXIMATION_LOST", dan, [e.chu],
                              f"Câu gốc nói con số ước chừng quanh “{e.chu}”.", CAN_XEM, TRUNG, "con_so", loai_tt))
            continue
        # cung gia tri, khac don vi trong cung ho: mg <-> g, ngay <-> tuan
        khac_dv = [e for e in ev if e.ho == s.ho and e.don_vi != s.don_vi and e.chua(s.gia_tri)]
        if khac_dv:
            ma = "DURATION_MISMATCH" if s.ho == "thoi_gian" else "UNIT_MISMATCH"
            ra.append(tao(ctx, p, ma, dan, [khac_dv[0].chu],
                          f"Bản ghi “{s.chu}”, câu gốc “{khac_dv[0].chu}” — cùng số, khác đơn vị.",
                          LOI_PHAT_HIEN, THAP, "con_so", loai_tt))
            continue
        lech10 = [e for e in cung_dv if not e.la_khoang and e.gia_tri and
                  (abs(s.gia_tri - e.gia_tri * 10) < 1e-9 or abs(s.gia_tri * 10 - e.gia_tri) < 1e-9)]
        if lech10:
            ra.append(tao(ctx, p, "DECIMAL_MISMATCH", dan, [lech10[0].chu],
                          f"Bản ghi “{s.chu}”, câu gốc “{lech10[0].chu}” — lệch 10 lần.",
                          LOI_PHAT_HIEN, THAP, "con_so", loai_tt))
            continue
        # so co o LUOT KHAC trong hoi thoai: dan sai luot, khong phai bia
        o_dau = [so for so, (_v, v) in ctx.luot.items() if so not in dan
                 and any(e.don_vi == s.don_vi and e.chua(s.gia_tri) for e in so_lieu.tach(v))]
        ma = _MA_THEO_HO.get(s.ho, "NUMERIC_MISMATCH")
        if o_dau:
            ra.append(tao(ctx, p, ma, dan + o_dau[:1], [ctx.luot[o_dau[0]][1]],
                          f"“{s.chu}” có ở lượt {o_dau[0]}, không có ở lượt được dẫn.",
                          NGHI_RUI_RO, TRUNG, "con_so", loai_tt))
        elif cung_dv:
            ra.append(tao(ctx, p, ma, dan, [e.chu for e in cung_dv[:2]],
                          f"Bản ghi “{s.chu}”, câu gốc nói “{', '.join(e.chu for e in cung_dv[:2])}”.",
                          LOI_PHAT_HIEN, THAP, "con_so", loai_tt))
        elif dan:
            ra.append(tao(ctx, p, ma, dan, [],
                          f"“{s.chu}” không có ở đâu trong hội thoại.", LOI_PHAT_HIEN, THAP, "con_so", loai_tt))
    return ra


# ----------------------------------------------------------------- 3. hoi - dap
LA_CAU_HOI = re.compile(r"\?|(?<!\w)(không|chưa|gì|nào|sao|à|hả|chứ)\s*(ạ|vậy|nhỉ|nhé)?\s*$")
TRA_LOI_KHONG = re.compile(r"^(dạ|vâng|thưa bác sĩ|ờ|à)?[ ,]*(không|chưa|chẳng|chả)(?!\s+(nhớ|rõ|biết|chắc))(\s|,|\.|$)")
TRA_LOI_CO = re.compile(r"^(dạ|vâng|ờ)?[ ,]*(có|bị|đúng rồi|vâng có|dạ có)(\s|,|\.|$)")


def hoi_dap(ctx: NguCanh, p, loai_tt) -> List[CanhBao]:
    """Cap hoi (bac si) - dap (nguoi benh/nguoi nha). Ba loi:
    NEGATION_FLIP: tra loi 'khong' ma ban ghi khang dinh, hoac nguoc lai.
    QUESTION_AS_FACT: chi dan cau hoi, khong dan cau tra loi.
    EVIDENCE_CONTEXT_MISSING: dan cau tra loi ngan ma khong dan cau hoi."""
    dan = ctx.dan(p)
    if not dan or not _thuc_te(p):
        return []
    ra = []
    tu_p = _tu(p.noi_dung)
    for q in dan:
        if not ctx.la_nv(q) or not LA_CAU_HOI.search(_thuong(ctx.luot[q][1])):
            continue
        a = q + 1
        if a not in ctx.luot or ctx.la_nv(a):
            continue
        cau_hoi, tra_loi = ctx.luot[q][1], _thuong(ctx.luot[a][1])
        if not (tu_p & _tu(cau_hoi)):
            continue
        # phan tra loi SAU tu co/khong: "Khong, nhung toi co ho" — phat bieu "ho"
        # noi ve phan con lai, khong phai ve dieu duoc hoi.
        con_lai = _tu(re.sub(r"^(dạ|vâng|ờ|à)?[ ,]*(không|chưa|có|bị)\b", "", tra_loi))
        noi_ve_con_lai = bool(tu_p & con_lai - _tu(cau_hoi))
        if TRA_LOI_KHONG.search(tra_loi) and not getattr(p, "phu_dinh", False) and _chac(p) \
                and not noi_ve_con_lai:
            ra.append(tao(ctx, p, "NEGATION_FLIP", [q, a], [cau_hoi, ctx.luot[a][1]],
                          f"Lượt {q} hỏi, lượt {a} trả lời “{ctx.luot[a][1]}”; bản ghi lại khẳng định.",
                          LOI_PHAT_HIEN, THAP, "hoi_dap", loai_tt))
        elif TRA_LOI_CO.search(tra_loi) and getattr(p, "phu_dinh", False) and not noi_ve_con_lai:
            ra.append(tao(ctx, p, "NEGATION_FLIP", [q, a], [cau_hoi, ctx.luot[a][1]],
                          f"Lượt {q} hỏi, lượt {a} trả lời “{ctx.luot[a][1]}”; bản ghi lại phủ định.",
                          LOI_PHAT_HIEN, THAP, "hoi_dap", loai_tt))
        if a not in dan and all(ctx.la_nv(s) for s in dan) and _la_bn(p) \
                and getattr(p, "hanh_vi", "") not in ("quan sát", "nhận định", "kế hoạch"):
            ra.append(tao(ctx, p, "QUESTION_AS_FACT", [q, a], [cau_hoi],
                          f"Căn cứ chỉ là câu hỏi ở lượt {q}; câu trả lời ở lượt {a} không được dẫn.",
                          LOI_PHAT_HIEN, THAP, "hoi_dap", loai_tt))
    for a in dan:
        q = a - 1
        if ctx.la_nv(a) or q in dan or q not in ctx.luot or not ctx.la_nv(q):
            continue
        if len(_tu(ctx.luot[a][1])) <= 2 and LA_CAU_HOI.search(_thuong(ctx.luot[q][1])):
            ra.append(tao(ctx, p, "EVIDENCE_CONTEXT_MISSING", [q, a], [ctx.luot[q][1], ctx.luot[a][1]],
                          f"Lượt {a} là câu trả lời ngắn; câu hỏi ở lượt {q} cần được dẫn cùng.",
                          CAN_XEM, THAP, "hoi_dap", loai_tt))
    return ra


# ----------------------------------------------------------------- 4. khong nho
KHONG_NHO = re.compile(r"(?<!\w)((không|chả|chẳng) (nhớ|rõ|biết|chắc)|chưa (rõ|biết)|quên (mất|rồi)?)(?!\w)")
PHU_DINH_THAT = re.compile(r"(?<!\w)(không (có|bị)|chưa (từng|bao giờ)|chưa (thấy )?bị)(?!\w)")


def khong_nho(ctx: NguCanh, p, loai_tt) -> List[CanhBao]:
    """'Khong nho co di ung khong' KHONG phai 'khong di ung'. Va cung khong phai
    'co di ung' — ghi chac chan chieu nao cung sai."""
    ra = []
    tu_p = _tu(re.sub(r"(?<!\w)(không|chưa|chẳng|chả)(?!\w)", " ", _thuong(p.noi_dung)))
    for s in ctx.dan(p):
        if ctx.la_nv(s):
            continue
        for c in cac_cau(ctx.luot[s][1]):
            ct = _thuong(c)
            if not KHONG_NHO.search(ct):
                continue
            # "khong nho" phai noi ve CUNG noi dung voi ban ghi: "khong nho ten thuoc"
            # khong lien quan "khong di ung". Menh de chi con "toi khong nho" thi doc
            # noi dung o cau hoi cua bac si ngay truoc.
            tu_c = _tu(KHONG_NHO.sub(" ", ct))
            cau_hoi = ctx.luot[s - 1][1] if (s - 1) in ctx.luot and ctx.la_nv(s - 1) else ""
            if not (tu_p & tu_c) and not (not tu_c - {"tôi", "em", "cháu"} and tu_p & _tu(cau_hoi)):
                continue
            # "khong nho ngay nao nhung khong co di ung" — da tach o "nhung"; con
            # trong CUNG menh de ma co phu dinh that thi khong bao.
            if PHU_DINH_THAT.search(KHONG_NHO.sub(" ", ct)):
                continue
            if not _chac(p):
                continue
            ma = "UNKNOWN_AS_NEGATIVE" if getattr(p, "phu_dinh", False) else "CERTAINTY_INCREASED"
            ra.append(tao(ctx, p, ma, [s], [c],
                          f"Lượt {s}: “{c}” — người nói không chắc, bản ghi lại ghi chắc chắn.",
                          LOI_PHAT_HIEN, THAP, "khong_nho", loai_tt))
            return ra
    return ra


# Phu dinh CAI LOI NOI TRUOC, khong phai phu dinh noi dung: "Khong dung dau, em meo
# mieng hai hom roi" (ca dct_019_B, 24/09/2026 — ca khoa va bo phat hien cu deu bo qua).
PHU_DINH_LOI_NOI = re.compile(r"(?<!\w)(không (đúng|phải) (đâu|vậy|thế|ạ)|không phải vậy|sai rồi|không đúng)(?!\w)")
PHU_DINH_CON = re.compile(r"(?<!\w)(không|chưa|chẳng|chả|hết)(?!\w)")


def pham_vi_phu_dinh(ctx: NguCanh, p, loai_tt) -> List[CanhBao]:
    if not getattr(p, "phu_dinh", False):
        return []
    tu_p = _tu(re.sub(r"(?<!\w)(không|chưa|chẳng|chả|hết)(?!\w)", " ", _thuong(p.noi_dung)))
    for s in ctx.dan(p):
        if ctx.la_nv(s):
            continue
        for c in cac_cau(ctx.luot[s][1]):
            ct = _thuong(c)
            m = PHU_DINH_LOI_NOI.search(ct)
            if not m:
                continue
            con_lai = ct[m.end():]
            if PHU_DINH_CON.search(con_lai) or not (tu_p & _tu(con_lai)):
                continue
            return [tao(ctx, p, "NEGATION_SCOPE_ERROR", [s], [c],
                        f"Lượt {s}: “{c}” — “{m.group(0)}” là bác lời nói trước; phần sau vẫn khẳng định.",
                        LOI_PHAT_HIEN, THAP, "pham_vi_phu_dinh", loai_tt)]
    return []


# ----------------------------------------------------------------- 5. loi dan, ke hoach
LOI_KHUYEN = re.compile(r"(?<!\w)(nên|hãy|nhớ|đừng|không nên|cần phải|phải|cố gắng|tránh|chú ý)(?!\w)")
TUONG_LAI = re.compile(r"(?<!\w)(sẽ|tuần sau|tháng sau|ngày mai|sáng mai|chiều mai|lát nữa|chiều nay|tối nay|"
                       r"hẹn|tái khám|để (tôi|em|bác sĩ|chị|anh) (cho|kê|làm|chỉ định|gửi)|cho (đi|làm)|"
                       r"(đi|về) (chụp|xét nghiệm|siêu âm|làm|đo)|chỉ định|làm thêm)(?!\w)")
QUA_KHU_KE_HOACH = re.compile(r"(?<!\w)(đã|hôm trước|lần trước|tuần trước|hồi|trước đây)(?!\w)")
XET_NGHIEM = re.compile(r"(?<!\w)(xét nghiệm|chụp|siêu âm|x[- ]?quang|nội soi|điện tim|ct|mri|đo đường|"
                        r"công thức máu|nước tiểu)(?!\w)")
CO_KET_QUA = re.compile(r"(?<!\w)(kết quả|bình thường|âm tính|dương tính|không (thấy|phát hiện)|bất thường|"
                        r"tăng|giảm|cao|thấp)(?!\w)|\d")
CHUA_LAM = re.compile(r"(?<!\w)chưa (làm|có kết quả|chụp|xét nghiệm|đo|siêu âm)(?!\w)")
BAC_SI_BAO = re.compile(r"(?<!\w)(bác sĩ|bs) (bảo|dặn|kê|nói|cho|hẹn|chỉ định)(?!\w)")
DIEU_KIEN_THEM = re.compile(r"(?<!\w)(nếu|lỡ mà|hễ|trường hợp|khi nào|phòng khi)(?!\w)")


def ke_hoach(ctx: NguCanh, p, loai_tt) -> List[CanhBao]:
    ra = []
    dan = ctx.dan(p)
    if not dan:
        return ra
    s, c = ctx.cau_gan_nhat(p)
    if s is None:
        return ra
    ct, nd = _thuong(c), _thuong(p.noi_dung)
    hanh_vi = getattr(p, "hanh_vi", "")
    tinh_huong = getattr(p, "tinh_huong", "thực tế")
    # Loi dan cua bac si ghi thanh viec benh nhan da lam
    if all(ctx.la_nv(x) for x in dan) and LOI_KHUYEN.search(ct) and not LA_CAU_HOI.search(ct) \
            and tinh_huong == "thực tế" and hanh_vi not in ("kế hoạch", "quan sát", "nhận định") and _la_bn(p):
        ra.append(tao(ctx, p, "RECOMMENDATION_AS_FACT", [s], [c],
                      f"Lượt {s} là lời dặn của bác sĩ: “{c}”.", LOI_PHAT_HIEN, TRUNG, "ke_hoach", loai_tt))
    # Xet nghiem se lam / chua lam ghi thanh co ket qua
    if tinh_huong == "thực tế" and XET_NGHIEM.search(ct) and (TUONG_LAI.search(ct) or CHUA_LAM.search(ct)) \
            and XET_NGHIEM.search(nd) and CO_KET_QUA.search(nd) and not CO_KET_QUA.search(
                re.sub(XET_NGHIEM, "", ct)):
        ra.append(tao(ctx, p, "PLANNED_TEST_AS_RESULT", [s], [c],
                      f"Lượt {s} nói xét nghiệm sẽ làm hoặc chưa làm: “{c}”.",
                      LOI_PHAT_HIEN, THAP, "ke_hoach", loai_tt))
    # Viec se lam ghi thanh su viec
    elif tinh_huong == "thực tế" and TUONG_LAI.search(ct) and not DAU_DIEU_KIEN.search(ct) \
            and not QUA_KHU_KE_HOACH.search(ct) and ctx.la_nv(s) and not LA_CAU_HOI.search(ct):
        ra.append(tao(ctx, p, "PLAN_AS_FACT", [s], [c],
                      f"Lượt {s} nói việc sẽ làm: “{c}”; bản ghi ghi như đã xảy ra.",
                      LOI_PHAT_HIEN, TRUNG, "ke_hoach", loai_tt))
    # Ke hoach CO DIEU KIEN ghi thanh ke hoach chac chan
    if tinh_huong == "kế hoạch" and DIEU_KIEN_THEM.search(ct) and not DIEU_KIEN_THEM.search(nd):
        ra.append(tao(ctx, p, "CONDITION_AS_CONFIRMED_PLAN", [s], [c],
                      f"Lượt {s} là kế hoạch có điều kiện: “{c}”; bản ghi bỏ mất điều kiện.",
                      LOI_PHAT_HIEN, THAP, "ke_hoach", loai_tt))
    # Y cua nguoi benh/nguoi nha ghi thanh ke hoach cua bac si
    if (tinh_huong == "kế hoạch" or hanh_vi == "kế hoạch") and not any(ctx.la_nv(x) for x in dan) \
            and not any(BAC_SI_BAO.search(_thuong(ctx.luot[x][1])) for x in dan):
        ra.append(tao(ctx, p, "FAMILY_STATEMENT_AS_CLINICIAN_PLAN", dan, [ctx.luot[x][1] for x in dan[:2]],
                      "Kế hoạch này chỉ dựa trên lời người bệnh hoặc người nhà.",
                      NGHI_RUI_RO, TRUNG, "ke_hoach", loai_tt))
    return ra


# ----------------------------------------------------------------- 6. thoi diem, trang thai dung
NGUNG = re.compile(r"(?<!\w)(ngưng|ngừng|bỏ|thôi (uống|dùng)|không (uống|dùng|xịt) nữa|hết thuốc|dừng)(?!\w)")
DUNG_LAI = re.compile(r"(?<!\w)((uống|dùng) lại|vẫn (uống|dùng|đang)|đang (uống|dùng))(?!\w)")
QUA_KHU = re.compile(r"(?<!\w)(trước đây|hồi trước|lúc trước|ngày xưa|hồi nhỏ|năm ngoái|đã từng|từng|hồi đó|"
                     r"dạo trước|mấy năm trước)(?!\w)")
HIEN_TAI = re.compile(r"(?<!\w)(bây giờ|hiện (tại|giờ|nay)|vẫn|đang|dạo này|mấy (hôm|ngày|bữa) nay|nay|còn)(?!\w)")


def _dang_dung(p) -> bool:
    t = getattr(p, "thuoc", None) or {}
    if t.get("trang_thai_dung"):
        return t["trang_thai_dung"] == "đang dùng"
    return bool(t) and "đang" in _thuong(p.noi_dung)


def thoi_diem(ctx: NguCanh, p, loai_tt) -> List[CanhBao]:
    ra = []
    t = getattr(p, "thuoc", None) or {}
    ten = t.get("ten") or ""
    if t and _dang_dung(p):
        for s in ctx.dan(p):
            for c in cac_cau(ctx.luot[s][1]):
                ct = _thuong(c)
                if NGUNG.search(ct) and not DUNG_LAI.search(ct) and (not ten or _co(ten, ct) or
                                                                     "thuốc" in ct):
                    ra.append(tao(ctx, p, "DISCONTINUED_AS_CURRENT", [s], [c],
                                  f"Lượt {s}: “{c}” — thuốc đã ngừng, bản ghi ghi đang dùng.",
                                  LOI_PHAT_HIEN, THAP, "thoi_diem", loai_tt))
                    return ra
    s, c = ctx.cau_gan_nhat(p)
    if s is None:
        return ra
    ct = _thuong(c)
    thoi = getattr(p, "thoi_gian_su_kien", "chưa rõ")
    if (thoi == "hiện tại" or _dang_dung(p)) and QUA_KHU.search(ct) and not HIEN_TAI.search(ct):
        ra.append(tao(ctx, p, "PAST_CURRENT_CONFUSION", [s], [c],
                      f"Lượt {s}: “{c}” — nói chuyện trước đây; bản ghi ghi như hiện tại.",
                      NGHI_RUI_RO, TRUNG, "thoi_diem", loai_tt))
    elif (thoi == "quá khứ" or t.get("trang_thai_dung") == "đã ngừng") \
            and re.search(r"(?<!\w)(vẫn đang|hiện đang|vẫn còn|bây giờ vẫn|vẫn (uống|dùng))(?!\w)", ct) \
            and not QUA_KHU.search(ct) and not NGUNG.search(ct):
        ra.append(tao(ctx, p, "PAST_CURRENT_CONFUSION", [s], [c],
                      f"Lượt {s}: “{c}” — vẫn đang diễn ra; bản ghi ghi như đã qua.",
                      NGHI_RUI_RO, TRUNG, "thoi_diem", loai_tt))
    return ra


# ----------------------------------------------------------------- 7. ben, muc do, tan suat
BEN = re.compile(r"(?<!\w)(bên|tay|chân|mắt|tai|phía|hố chậu|hông|sườn|hạ sườn|vú|gối|vai|phổi|thận|"
                 r"mông|đùi|cẳng chân|bàn chân|bàn tay|má|mặt|đầu|bụng|ngực|lưng|hạ vị|mạn sườn) (trái|phải)(?!\w)")
NHE = re.compile(r"(?<!\w)(nhẹ|hơi (sốt|đau|mệt|ho|khó|nhức|ê|tức|chóng)|âm ỉ|lâm râm|ít thôi|không nhiều)(?!\w)")
NANG = re.compile(r"(?<!\w)(dữ dội|rất (đau|nhiều|nặng)|nặng lắm|kinh khủng|quằn quại|chịu không nổi|"
                  r"đau nhiều|sốt cao|nặng)(?!\w)")
IT_KHI = re.compile(r"(?<!\w)(thỉnh thoảng|đôi khi|lâu lâu|ít khi|hiếm khi|đôi lúc)(?!\w)")
HAY_BI = re.compile(r"(?<!\w)(thường xuyên|liên tục|suốt ngày|lúc nào cũng|ngày nào cũng|luôn luôn|triền miên)(?!\w)")


def _ben(van):
    return {(m.group(1), m.group(2)) for m in BEN.finditer(_thuong(van))}


def than_the(ctx: NguCanh, p, loai_tt) -> List[CanhBao]:
    ra = []
    dan = ctx.dan(p)
    if not dan:
        return ra
    van = ctx.van_dan(p)
    b_p, b_e = _ben(p.noi_dung), _ben(van)
    for bo_phan, ben in b_p:
        cung_bo = {b for bp, b in b_e if bp == bo_phan}
        if cung_bo and ben not in cung_bo:
            ra.append(tao(ctx, p, "LATERALITY_CHANGED", dan, [f"{bo_phan} {b}" for b in cung_bo],
                          f"Bản ghi “{bo_phan} {ben}”, câu gốc “{bo_phan} {'/'.join(cung_bo)}”.",
                          LOI_PHAT_HIEN, THAP, "than_the", loai_tt))
    # muc do va tan suat: so voi MENH DE gan nhat, khong voi ca luot
    s, c = ctx.cau_gan_nhat(p)
    ct, nd = _thuong(c), _thuong(p.noi_dung)
    for a, b, ma, ten_a, ten_b in ((NANG, NHE, "SEVERITY_CHANGED", "nặng", "nhẹ"),
                                    (NHE, NANG, "SEVERITY_CHANGED", "nhẹ", "nặng"),
                                    (HAY_BI, IT_KHI, "FREQUENCY_WORD_CHANGED", "thường xuyên", "thỉnh thoảng"),
                                    (IT_KHI, HAY_BI, "FREQUENCY_WORD_CHANGED", "thỉnh thoảng", "thường xuyên")):
        if s is not None and a.search(nd) and b.search(ct) and not a.search(ct):
            ra.append(tao(ctx, p, ma, [s], [c],
                          f"Bản ghi ghi mức “{a.search(nd).group(0)}”, câu gốc “{b.search(ct).group(0)}”.",
                          LOI_PHAT_HIEN, TRUNG, "than_the", loai_tt))
            break
    return ra


# ----------------------------------------------------------------- 8. ten thuoc, chat gay di ung
TU_CHUNG = {"thuốc", "gì", "thức ăn", "đồ ăn", "một số", "nhiều", "các", "loại", "thuốc tây", "kháng sinh"}
_DI_UNG = re.compile(r"(?<!\w)(dị ứng|mẫn cảm)\s+(?:với\s+)?((?:[\wÀ-ỹ\-]+\s?){1,3})")


def _ten_thuoc(p) -> List[str]:
    t = getattr(p, "thuoc", None) or {}
    ra = []
    if t.get("ten") and not any(w in _thuong(t["ten"]).split() for w in ("thuốc", "loại")):
        ra.append(t["ten"])
    for m in re.finditer(r"(?i)(?<!\w)(" + "|".join(TU_DIEN_THUOC) + r")\w*", _nfc(p.noi_dung)):
        if not any(_co(m.group(0), _thuong(x)) or _co(x, _thuong(m.group(0))) for x in ra):
            ra.append(m.group(0))
    return ra


def _chat_di_ung(p) -> Optional[str]:
    if getattr(p, "phu_dinh", False):
        return None
    m = _DI_UNG.search(_thuong(p.noi_dung))
    if not m:
        return None
    chat = m.group(2).strip()
    chat = re.split(r"\s(khi|nên|thì|và|,|do|gây)\s", f" {chat} ")[0].strip()
    if not chat or any(chat == t or chat.startswith(t + " ") for t in TU_CHUNG) or chat.split()[0] in TU_CHUNG:
        return None
    return chat


def thuc_the(ctx: NguCanh, p, loai_tt) -> List[CanhBao]:
    ra = []
    dan = ctx.dan(p)
    if not dan:
        return ra
    van = _thuong(ctx.van_dan(p))
    doi = [(ten, "FABRICATED_MEDICATION", "MEDICATION_ENTITY_MISMATCH", "Tên thuốc") for ten in _ten_thuoc(p)]
    chat = _chat_di_ung(p)
    if chat:
        doi.append((chat, "FABRICATED_ALLERGY", "ALLERGEN_MISMATCH", "Chất gây dị ứng"))
    for ten, ma_bia, ma_lech, nhan in doi:
        if _co(ten, van):
            continue
        # chat gay di ung nhieu tu: du neu MOI tu noi dung co trong luot dan
        if " " in ten and _tu(ten) and _tu(ten) <= _tu(van):
            continue
        o_dau = ctx.tim_luot(ten, bo_qua=dan)
        if o_dau:
            ra.append(tao(ctx, p, ma_lech, dan + o_dau[:1], [ctx.luot[o_dau[0]][1]],
                          f"{nhan} “{ten}” có ở lượt {o_dau[0]}, không ở lượt được dẫn.",
                          NGHI_RUI_RO, TRUNG, "thuc_the", loai_tt))
        else:
            ra.append(tao(ctx, p, ma_bia, dan, [],
                          f"{nhan} “{ten}” không xuất hiện ở lượt nào trong hội thoại.",
                          LOI_PHAT_HIEN, THAP, "thuc_the", loai_tt))
    return ra


# ----------------------------------------------------------------- 9. dinh chinh
DAU_SUA = re.compile(r"(?<!\w)(à không|à mà không|ờ không|à nhầm|nói nhầm|nhầm|xin lỗi|à quên|"
                     r"ý (tôi|em|cháu) là|đúng ra là|chính xác là|không phải)(?!\w)")


def tim_dinh_chinh(ctx: NguCanh) -> List[dict]:
    """Moi lan nguoi noi SUA MOT CON SO: {luot, cu, moi, cau}.
    Hai dang trong mot luot: 'X ... a khong, Y' va 'Y chu khong phai X' /
    'khong phai X ma la Y'. Mot dang qua luot: luot sau MO DAU bang dau hieu sua,
    cung nguoi noi, trong 4 luot. Tien trien ('hom qua 7/10, hom nay 3/10') khong
    co dau hieu sua nen khong bi coi la dinh chinh."""
    ra = []
    ds = sorted(ctx.luot.items())
    for so, (vai, van) in ds:
        t = _thuong(van)
        for m in re.finditer(r"(.{0,60}?)(chứ không phải|không phải)\s(.{0,40})", t):
            truoc, sau = so_lieu.tach(m.group(1)), so_lieu.tach(m.group(3))
            if m.group(2) == "chứ không phải" and truoc and sau and truoc[-1].ho == sau[0].ho:
                ra.append({"luot": so, "cu": sau[0], "moi": truoc[-1], "cau": van})
            elif m.group(2) == "không phải" and sau and len(sau) >= 2 and "mà" in m.group(3) \
                    and sau[0].ho == sau[1].ho:
                ra.append({"luot": so, "cu": sau[0], "moi": sau[1], "cau": van})
        for m in DAU_SUA.finditer(t):
            if m.group(0) == "không phải":
                continue
            truoc, sau = so_lieu.tach(t[:m.start()]), so_lieu.tach(t[m.end():])
            if truoc and sau and truoc[-1].ho == sau[0].ho and not truoc[-1].chua(sau[0].gia_tri):
                ra.append({"luot": so, "cu": truoc[-1], "moi": sau[0], "cau": van})
            elif not truoc and sau and m.start() < 12:
                # sua o luot sau: tim so cung ho o luot truoc cua CUNG nguoi noi
                for so2 in range(so - 1, max(0, so - 5), -1):
                    if so2 in ctx.luot and ctx.luot[so2][0] == vai:
                        cu = [e for e in so_lieu.tach(ctx.luot[so2][1]) if e.ho == sau[0].ho]
                        if cu and not cu[-1].chua(sau[0].gia_tri):
                            ra.append({"luot": so, "luot_cu": so2, "cu": cu[-1], "moi": sau[0], "cau": van})
                        break
    return ra


def dinh_chinh(ctx: NguCanh, p, loai_tt, cac_sua: List[dict]) -> List[CanhBao]:
    if not cac_sua or getattr(p, "trang_thai", "còn hiệu lực") != "còn hiệu lực":
        return []
    ps = _so_phat_bieu(p)
    ra = []
    for d in cac_sua:
        cu, moi = d["cu"], d["moi"]
        co_cu = any(s.don_vi == cu.don_vi and cu.chua(s.gia_tri) for s in ps)
        co_moi = any(s.don_vi == moi.don_vi and moi.chua(s.gia_tri) for s in ps)
        luot = [d["luot"]] + ([d["luot_cu"]] if "luot_cu" in d else [])
        if not set(luot) & set(ctx.dan(p)):
            continue
        if co_cu and co_moi:
            ra.append(tao(ctx, p, "OLD_AND_NEW_VALUE_DUPLICATED", luot, [d["cau"]],
                          f"Bản ghi có cả “{cu.chu}” (đã sửa) và “{moi.chu}”.",
                          LOI_PHAT_HIEN, THAP, "dinh_chinh", loai_tt))
        elif co_cu:
            ra.append(tao(ctx, p, "CORRECTION_NOT_APPLIED", luot, [d["cau"]],
                          f"Lượt {d['luot']}: “{d['cau']}” — người nói sửa “{cu.chu}” thành “{moi.chu}”, "
                          f"bản ghi còn giữ “{cu.chu}”.", LOI_PHAT_HIEN, THAP, "dinh_chinh", loai_tt))
    return ra


# ----------------------------------------------------------------- 10. cau mau
CAU_MAU = (
    (re.compile(r"(?<!\w)(không|chưa) (có |ghi nhận |phát hiện )?(tiền sử )?dị ứng"), "phu_dinh"),
    (re.compile(r"(?<!\w)(không có tiền sử (gì )?(đặc biệt|bệnh lý)|tiền sử (khỏe mạnh|không có gì đặc biệt))"), "phu_dinh"),
    (re.compile(r"(?<!\w)(khám (bình thường|không (thấy|phát hiện) (gì )?bất thường)|"
                r"(sinh hiệu|dấu hiệu sinh tồn) (ổn|ổn định|bình thường))"), "binh_thuong"),
)
_CO_PHU_DINH = re.compile(r"(?<!\w)(không|chưa|chẳng|chả|không có gì|khỏe)(?!\w)")
_CO_BINH_THUONG = re.compile(r"(?<!\w)(bình thường|ổn|không (có gì|thấy gì|thấy bất thường)|tốt)(?!\w)")


def cau_mau(ctx: NguCanh, p, loai_tt) -> List[CanhBao]:
    """'Khong di ung', 'kham binh thuong' la cau MAU hay duoc dien tu dong. Chi
    chap nhan khi luot duoc dan THUC SU co cau tra loi phu dinh / binh thuong."""
    nd = _thuong(p.noi_dung)
    dan = ctx.dan(p)
    for bt, can in CAU_MAU:
        if not bt.search(nd):
            continue
        if can == "phu_dinh":
            ok = any(not ctx.la_nv(s) and _CO_PHU_DINH.search(_thuong(ctx.luot[s][1])) for s in dan)
        else:
            ok = any(ctx.la_nv(s) and _CO_BINH_THUONG.search(_thuong(ctx.luot[s][1])) for s in dan)
        if not ok:
            return [tao(ctx, p, "UNSUPPORTED_BOILERPLATE", dan, [ctx.luot[s][1] for s in dan[:2]],
                        f"“{p.noi_dung}” là câu mẫu; lượt được dẫn không có câu trả lời "
                        f"{'phủ định' if can == 'phu_dinh' else 'bình thường'} nào.",
                        LOI_PHAT_HIEN, TRUNG, "cau_mau", loai_tt)]
    return []


# ----------------------------------------------------------------- 11. thu nghiem
NHAN_QUA_P = re.compile(r"(?<!\w)(do (uống|dùng|ăn|thuốc|tác dụng)|vì (uống|dùng|ăn)|gây ra|tác dụng phụ)(?!\w)")
NHAN_QUA_E = re.compile(r"(?<!\w)(do|vì|tại|gây|nên bị|từ khi (uống|dùng)|sau khi (uống|dùng|ăn)|thì bị)(?!\w)")
BO_NGHIA = re.compile(r"(?<!\w)(thỉnh thoảng|đôi khi|về đêm|ban đêm|buổi sáng|sau (khi )?ăn|khi (gắng sức|nằm|đi lại)|"
                      r"đồ cay|lúc đói|nhẹ)(?!\w)")
NGOAI_LE = re.compile(r"(?<!\w)(tắc đường|đến muộn|gửi xe|chờ lâu|xếp hàng|bận việc|đông quá|đi thay)(?!\w)")


def thu_nghiem(ctx: NguCanh, p, loai_tt) -> List[CanhBao]:
    """Bo phat hien THU NGHIEM: chi hien, khong bao gio doi trang thai. Chua do
    do chinh xac tren nhan that — xem docs/tai-lieu/he-thong-canh-bao.md."""
    ra = []
    dan = ctx.dan(p)
    if not dan:
        return ra
    nd = _thuong(p.noi_dung)
    van = _thuong(ctx.van_dan(p))
    if NHAN_QUA_P.search(nd) and not NHAN_QUA_E.search(van):
        ra.append(tao(ctx, p, "UNSUPPORTED_CAUSALITY", dan, [], "Bản ghi nói nguyên nhân; lượt được dẫn không nói.",
                      NGHI_RUI_RO, CAO, "thu_nghiem", loai_tt))
    vai = {ctx.luot[s][0] for s in dan if not ctx.la_nv(s)}
    if len(vai) >= 2 and _la_bn(p):
        ra.append(tao(ctx, p, "UNSUPPORTED_FACT_COMBINATION", dan, [ctx.luot[s][1] for s in dan[:2]],
                      f"Căn cứ lấy từ lời của {', '.join(sorted(vai))}.", NGHI_RUI_RO, CAO, "thu_nghiem", loai_tt))
    s, c = ctx.cau_gan_nhat(p)
    if s is not None:
        mat = [m.group(0) for m in BO_NGHIA.finditer(_thuong(c)) if m.group(0) not in nd]
        if mat:
            ra.append(tao(ctx, p, "IMPORTANT_MODIFIER_DROPPED", [s], [c],
                          f"Câu gốc có “{', '.join(mat)}”, bản ghi không có.", CAN_XEM, CAO, "thu_nghiem", loai_tt))
    if getattr(p, "hanh_vi", "") in ("trả lời", "tự kể") and all(ctx.la_nv(x) for x in dan) \
            and not any(LA_CAU_HOI.search(_thuong(ctx.luot[x][1])) for x in dan):
        ra.append(tao(ctx, p, "DOCTOR_STATEMENT_AS_PATIENT_FACT", dan, [ctx.luot[dan[0]][1]],
                      "Bản ghi là lời kể của người bệnh nhưng chỉ dẫn lời bác sĩ.", NGHI_RUI_RO, CAO, "thu_nghiem",
                      loai_tt))
    if NGOAI_LE.search(nd):
        ra.append(tao(ctx, p, "CLINICALLY_IRRELEVANT", dan, [], "Nội dung có vẻ là chuyện ngoài lề.",
                      CAN_XEM, CAO, "thu_nghiem", loai_tt))
    return ra


# ----------------------------------------------------------------- 12. cach noi mo ho
def _mo_ho():
    from src import dan_gian
    return [(dan_gian._mau(m.dan_gian), m) for m in dan_gian.BANG if m.loai == dan_gian.MO_HO]


_MO_HO = _mo_ho()


def cum_mo_ho(ctx: NguCanh, p, loai_tt) -> List[CanhBao]:
    """Cach noi dan gian co hon mot nghia hop ly (`dan_gian.BANG`, muc MO_HO): "om" o
    Nam Bo la gay, o Bac la bi benh; "len ban do" tu dien ghi co the la soi hoac sot
    xuat huyet. Them 24/09/2026.

    Bao khi luot NGUOI BENH / NGUOI NHA duoc dan chua cum do VA trich dan cua phat bieu
    chua cum do (phat bieu noi ve dung cho nay — cung cach ghep voi `do_dan_gian`).
    Bao CA KHI ban ghi chep nguyen van: chep "om" thi nguoi doc mien Bac van hieu la
    "bi benh". Ly do kem cau hoi lam ro, va ghi ro neu ban ghi da tu chon mot nghia
    trong `khong_duoc_suy_ra`."""
    ra, da = [], set()
    trich_p = [t for t in (getattr(p, "trich_dan", None) or []) if t]
    nd = _thuong(p.noi_dung)
    for s in ctx.dan(p):
        if ctx.la_nv(s):
            continue
        van = ctx.luot[s][1]
        for mau, m in _MO_HO:
            mot = ([x.span() for x in re.finditer(m.mot_nghia, van.lower())]
                   if m.mot_nghia else [])
            k = next((x for x in mau.finditer(van)
                      if not any(a < x.end() and x.start() < b for a, b in mot)), None)
            trich = [t for t in trich_p if mau.search(t)]
            if not k or not trich or m.dan_gian in da:
                continue
            da.add(m.dan_gian)
            ly = f"“{k.group(0)}” có hơn một nghĩa hợp lý"
            chon = [x for x in m.khong_duoc_suy_ra if _co(x, nd)]
            if chon:
                ly += f"; bản ghi đã chọn “{chon[0]}” khi chưa hỏi lại"
            ly += f". Hỏi lại: {m.cau_hoi}"
            ra.append(tao(ctx, p, "AMBIGUOUS_LAY_TERM", [s], trich[:1], ly,
                          NGHI_RUI_RO, THAP, "cum_mo_ho", loai_tt))
    return ra


BO_PHAT_HIEN = (con_so, hoi_dap, khong_nho, pham_vi_phu_dinh, ke_hoach, thoi_diem, than_the, thuc_the, cau_mau,
                thu_nghiem, cum_mo_ho)
