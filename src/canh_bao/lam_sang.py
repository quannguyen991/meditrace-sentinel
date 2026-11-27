# -*- coding: utf-8 -*-
"""[Lớp cảnh báo]
Làm gì   : Cảnh báo theo kiến thức lâm sàng: liều vượt trần ngày, tương tác thuốc, kê thuốc
           cho người đang dị ứng.
Vào → Ra : ngữ cảnh hội thoại + các dòng bản nháp → danh sách CanhBao về thuốc
Đọc từ   : quet() chạy các luật; lieu_ngay_mg() tính liều ngày theo mg
Mục lục (các hàm/lớp chính):
  quet()  Quét kiến thức lâm sàng: quá liều, tương tác, dị ứng
Gọi tới  : canh_bao/loai, canh_bao/phat_hien, cong_cu_lam_sang/canh_bao_tuong_tac_thuoc,
           cong_cu_lam_sang/di_ung_cheo, cong_cu_lam_sang/tri_thuc_thuoc
Dùng bởi : canh_bao/gop, he_thong/dich_vu_http
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Cảnh báo KIẾN THỨC LÂM SÀNG trong lớp cảnh báo: liều vượt trần, tương tác thuốc, kê thuốc
người bệnh đang dị ứng (25/11/2026).

Trước ngày này các kiểm tra này chỉ nằm ở trường `lam_sang_nang_cao` của `dich_vu` — một hệ
song song không có mã, không có mức tin cậy, không đi qua cách gộp cảnh báo. Giờ chúng là mã
của lớp cảnh báo, nhóm CLINICAL_KNOWLEDGE, tin cậy THU_NGHIEM (chỉ hiện, không đổi trạng thái).

Số liệu (liều tối đa) đọc từ `tri_thuc_thuoc`. Mục `da_duyet=false` -> kết luận CAN_XEM, không
bao giờ cao hơn. Bảng tương tác (`duoc_ly_lam_sang.BANG_TUONG_TAC_THUOC`) chưa có nguồn nên
luôn CAN_XEM. Chống chỉ định ở đây chỉ là "kê đúng chất người bệnh đang dị ứng" — không cần
ngưỡng nào; dị ứng chéo theo nhóm (penicillin -> amoxicillin) cần tri thức có nguồn, chưa làm.
"""
import re
from typing import List, Optional

from src.cong_cu_lam_sang import tri_thuc_thuoc as tri_thuc_thuoc
from src.canh_bao.loai import CAN_XEM, CAO, NGHI_RUI_RO, THAP, TRUNG, CanhBao, muc_do
from src.canh_bao.phat_hien import NguCanh, _thuong

_SO_CHU = {"một": 1, "hai": 2, "ba": 3, "bốn": 4, "tư": 4, "năm": 5, "sáu": 6, "bảy": 7, "tám": 8}
_SO = r"(\d+(?:[.,]\d+)?|" + "|".join(_SO_CHU) + r")"
_LIEU = re.compile(_SO + r"\s*(mg|g|gam|mcg|µg)(?!\w)")
_LAN_NGAY = re.compile(r"(?:ngày|mỗi ngày)\s*" + _SO + r"\s*lần|" + _SO + r"\s*lần\s*(?:/|một|mỗi|trong)?\s*ngày")
_MOI_GIO = re.compile(r"mỗi\s*" + _SO + r"\s*(?:giờ|tiếng)|cách\s*" + _SO + r"\s*(?:giờ|tiếng)")
_MOT_LAN = re.compile(r"(?<!\w)(mỗi (sáng|tối|trưa|chiều)|một lần|ngày một lần|1 lần|uống một liều)(?!\w)")


# ─── _so() — Đọc số từ chữ số hoặc số viết bằng chữ ───────────────────────────────────
def _so(s: str) -> float:
    return float(_SO_CHU.get(s, None) or s.replace(",", "."))


# ═══ lieu_ngay_mg() — Tính tổng liều một ngày bằng mg ═════════════════════════════════
# Từ liều và số lần dùng; trả về None nếu không đọc được liều hoặc số lần.
def lieu_ngay_mg(thuoc: Optional[dict], noi_dung: str) -> Optional[float]:
    """Tổng liều một ngày (mg) từ `thuoc` {"lieu", "so_lan"} hoặc từ nội dung. None khi
    không đọc được cả liều lẫn số lần."""
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


# ─── _con() — Kiểm tra mệnh đề còn hiệu lực ───────────────────────────────────────────
def _con(p) -> bool:
    return getattr(p, "trang_thai", "còn hiệu lực") != "bị thay thế"


# ─── _la_di_ung() — Kiểm tra mệnh đề nói về dị ứng ────────────────────────────────────
def _la_di_ung(p) -> bool:
    return "dị ứng" in _thuong(p.noi_dung)


# ─── _hoat_chat() — Lấy hoạt chất của thuốc trong mệnh đề ─────────────────────────────
# Tra bảng tri thức thuốc.
def _hoat_chat(p) -> Optional[str]:
    ten = (getattr(p, "thuoc", None) or {}).get("ten") or ""
    return tri_thuc_thuoc.hoat_chat(ten) if ten else tri_thuc_thuoc.hoat_chat(p.noi_dung)


# ─── _thuoc_dang_dung() — Liệt kê thuốc người bệnh đang dùng hoặc được kê ─────────────
# Bỏ dòng dị ứng, phủ định, bị thay thế và của người khác.
def _thuoc_dang_dung(ps) -> list:
    """(hoạt chất, phát biểu) của thuốc bệnh nhân đang dùng hoặc được kê — không tính dòng dị
    ứng, dòng phủ định, dòng bị thay thế, dòng của người khác."""
    ra = []
    for p in ps:
        if not _con(p) or getattr(p, "phu_dinh", False) or _la_di_ung(p) or getattr(p, "chu_the_id", 0) != 0:
            continue
        hc = _hoat_chat(p)
        if hc:
            ra.append((hc, p))
    return ra


# ─── _cb() — Dựng một cảnh báo kiến thức lâm sàng ─────────────────────────────────────
def _cb(ma, p, ctx, ly_do, ket_luan, loai_tt="thuoc", trich=None):
    return CanhBao(ma=ma, phat_bieu_id=p.id, luot=ctx.dan(p), trich=trich or [p.noi_dung], ly_do=ly_do,
                   ket_luan=ket_luan, bat_dinh=TRUNG, bo_phat_hien=f"lam_sang:{ma.lower()}",
                   muc_do=muc_do(ma, loai_tt), loai_tt=loai_tt)


# ═══ quet() — Quét kiến thức lâm sàng: quá liều, tương tác, dị ứng ════════════════════
# Sinh DOSE_OVER_MAX, DRUG_INTERACTION, CONTRAINDICATION, CROSS_ALLERGY; số chưa duyệt
# chỉ ở mức cần xem.
def quet(ctx: NguCanh, ps) -> List[CanhBao]:
    ra: List[CanhBao] = []
    dang_dung = _thuoc_dang_dung(ps)
    # 1. liều vượt trần (người lớn; trẻ em cần cân nặng — ở kiem_duyet_bhyt)
    for hc, p in dang_dung:
        l = tri_thuc_thuoc.lieu_toi_da(hc, "nguoi_lon")
        ngay = lieu_ngay_mg(getattr(p, "thuoc", None), p.noi_dung)
        if l is None or ngay is None or ngay <= l.gia_tri:
            continue
        ra.append(_cb("DOSE_OVER_MAX", p, ctx,
                      f"“{p.noi_dung}” = {ngay:g} mg/ngày, vượt mức tối đa người lớn {l.gia_tri:g} {l.don_vi} của "
                      f"{hc}" + ("" if l.da_duyet else " (số chưa được duyệt — chỉ để bác sĩ xem lại)") + ".",
                      NGHI_RUI_RO if l.da_duyet else CAN_XEM))
    # 2. tương tác thuốc (bảng chưa có nguồn -> luôn CAN_XEM)
    if len(dang_dung) >= 2:
        from src.cong_cu_lam_sang.canh_bao_tuong_tac_thuoc import ClinicalPharmacovigilanceEngine as Dl
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
    # 3. kê / dùng đúng chất người bệnh đang dị ứng (khẳng định)
    di_ung = []
    di_ung_tho = []
    for p in ps:
        if _con(p) and _la_di_ung(p) and not getattr(p, "phu_dinh", False) and getattr(p, "chu_the_id", 0) == 0:
            # Chỉ vế ngay sau "dị ứng": "dị ứng penicillin, đang dùng augmentin" -> penicillin.
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
                # Ánh xạ biết được -> hoạt chất cũng là tri thức chưa duyệt: CAN_XEM cho tới khi cả
                # hai mục da_duyet (rà soát 25/11).
                duyet = all((tri_thuc_thuoc._theo_hoat_chat().get(x) or {}).get("da_duyet") for x in (hc, hc_du))
                cap_da_bao_truc_tiep.add((p.id, p_du.id))
                ra.append(_cb("CONTRAINDICATION", p, ctx,
                              f"“{p.noi_dung}” chứa {hc_du}, nhưng dòng #{p_du.id} ghi người bệnh dị ứng {hc_du}.",
                              NGHI_RUI_RO if duyet else CAN_XEM, loai_tt="di_ung", trich=[p.noi_dung, p_du.noi_dung]))

    # 4. dị ứng chéo theo nhóm ATC / chuỗi nhánh hoá học (CROSS_ALLERGY, không phát CONTRAINDICATION)
    if di_ung_tho:
        from src.cong_cu_lam_sang.di_ung_cheo import CHONG_CHI_DINH as _DU_CAM, kiem_tra_di_ung_cheo
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
