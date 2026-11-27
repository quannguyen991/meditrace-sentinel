# -*- coding: utf-8 -*-
"""[Lớp cảnh báo]
Làm gì   : Cảnh báo ở mức cả ca: thông tin bị bỏ sót, mâu thuẫn giữa các dòng, giá trị đã bị
           đính chính mà vẫn giữ, ghi lặp.
Vào → Ra : ngữ cảnh + các dòng bản nháp (+ đoạn chưa ghi) → danh sách CanhBao toàn ca
Đọc từ   : bo_sot() bắt thông tin bỏ sót; mau_thuan() bắt dòng mâu thuẫn nhau
Mục lục (các hàm/lớp chính):
  bo_sot()            Cảnh báo bỏ sót cho cả ca
  mau_thuan()         Phát hiện hai mệnh đề cùng chủ thể mâu thuẫn nhau
  dinh_chinh_nguoc()  Phát hiện bản đã đính chính lại bị đánh dấu thay thế
  ghi_lap()           Phát hiện mệnh đề ghi lặp
  bo_sot_cu()         Bộ bỏ sót cũ, mỗi đoạn một mã
Gọi tới  : canh_bao/bo_sot, canh_bao/loai, canh_bao/phat_hien, canh_bao/so_lieu,
           duong_ong/b2_gom_nguoi_thuc_the, duong_ong/b4_kiem_can_cu
Dùng bởi : canh_bao/gop
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Cảnh báo MỨC TOÀN CA: bỏ sót, mâu thuẫn trong bản ghi, ghi lặp.

BỎ SÓT KHÔNG TỰ LÀM LẠI. `khoa_bang_chung.doan_chua_ghi` đã tìm đoạn hội thoại có
nội dung lâm sàng mà không phát biểu nào dẫn tới. Ở đây chỉ PHÂN LOẠI đoạn đó
(dị ứng? thuốc? phủ định? con số?) để bác sĩ biết đoạn nào đáng lo nhất. Không tự
bổ sung vào bản nháp — thông tin đó chưa qua khoá.
"""
import re
from itertools import combinations
from typing import List

from src.canh_bao import so_lieu
from src.canh_bao.loai import CAN_XEM, CAO, LOI_PHAT_HIEN, NGHI_RUI_RO, THAP, TRUNG, CanhBao, muc_do
from src.canh_bao.phat_hien import (DAU_SUA, DIEU_KIEN_THEM, KHONG_NHO, TUONG_LAI, NguCanh, _co,
                                    _dang_dung, _thuong, _tu)
from src.duong_ong.b4_kiem_can_cu import DAU_NGHI
from src.duong_ong.b2_gom_nguoi_thuc_the import THUOC_TU_DIEN

BO_SOT = (
    ("OMITTED_ALLERGY", re.compile(r"(?<!\w)(dị ứng|mẫn cảm|nổi mẩn (khi|sau))(?!\w)")),
    ("OMITTED_MEDICATION", re.compile(r"(?<!\w)((uống|dùng|xịt|tiêm|bôi|kê) thuốc|thuốc \w+|\d+ ?(mg|viên))(?!\w)")),
    ("OMITTED_CORRECTION", DAU_SUA),
    ("OMITTED_NEGATION", re.compile(r"(?<!\w)(không|chưa|chẳng) (bị|có|sốt|ho|đau|thấy|nôn|khó)(?!\w)")),
    ("OMITTED_UNCERTAINTY", re.compile(DAU_NGHI.pattern + "|" + KHONG_NHO.pattern)),
)


# ═══ bo_sot() — Cảnh báo bỏ sót cho cả ca ═════════════════════════════════════════════
# Từ 25/11/2026 chuyển sang bo_sot.quet, một bộ duy nhất.
def bo_sot(ctx: NguCanh, doan_chua_ghi: List[dict], ps=(), cap=()) -> List[CanhBao]:
    """Từ 25/11/2026 gọi sang `canh_bao.bo_sot.quet` — một bộ duy nhất cho cả hệ thống.
    Hàm cũ (một mã mỗi đoạn, không biết bản ghi đã có gì) giữ ở `bo_sot_cu` để đối chiếu."""
    from src.canh_bao import bo_sot as _bs
    return _bs.quet(ctx, ps, doan_chua_ghi, cap)


# ═══ bo_sot_cu() — Bộ bỏ sót cũ, mỗi đoạn một mã ══════════════════════════════════════
# Giữ lại để đối chiếu.
def bo_sot_cu(ctx: NguCanh, doan_chua_ghi: List[dict]) -> List[CanhBao]:
    ra = []
    for d in doan_chua_ghi:
        doan, so = d["doan"], d["luot"]
        t = _thuong(doan)
        ma = None
        # dị ứng trước từ điển thuốc: "tôi dị ứng penicillin" là dị ứng, không phải thuốc
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
        # Loại chung chung: 792/887 cảnh báo bỏ sót, 2,8% trùng chỗ đáp án bị sót (đo
        # 24/09/2026). Giữ ở backend để đo, KHÔNG hiện cho bác sĩ (can_xem).
        chung = ma == "POSSIBLE_IMPORTANT_OMISSION"
        ra.append(CanhBao(ma=ma, phat_bieu_id=None, luot=[so], trich=[doan],
                          ly_do=f"Lượt {so} ({d.get('vai') or 'không rõ vai'}): “{doan}” — không dòng nào dẫn tới.",
                          ket_luan=CAN_XEM if chung else NGHI_RUI_RO, bat_dinh=CAO if chung else TRUNG, bo_phat_hien="toan_ca:bo_sot",
                          muc_do=muc_do(ma, "di_ung" if ma == "OMITTED_ALLERGY" else
                                        "thuoc" if ma == "OMITTED_MEDICATION" else "khac")))
    return ra


# ─── _con() — Kiểm tra mệnh đề còn hiệu lực ───────────────────────────────────────────
def _con(p):
    return getattr(p, "trang_thai", "còn hiệu lực") != "bị thay thế"


# ─── _nd_bo_phu_dinh() — Lấy tập từ nội dung sau khi bỏ chữ phủ định ──────────────────
def _nd_bo_phu_dinh(p):
    return _tu(re.sub(r"(?<!\w)(không|chưa|chẳng|chả|hết)(?!\w)", " ", _thuong(p.noi_dung)))


# ─── _dien_bien() — Nhận biết hai mệnh đề là diễn biến hoặc khác mốc ──────────────────
# Trường hợp đó không phải mâu thuẫn.
def _dien_bien(p, q):
    """Hai phát biểu liên hệ bằng diễn biến, hoặc mang mốc thời gian khác nhau:
    'hôm qua đau' / 'hôm nay hết đau' — không phải mâu thuẫn."""
    if (getattr(p, "quan_he", None) == "diễn biến" and getattr(p, "quan_he_voi", None) == q.id) or \
            (getattr(q, "quan_he", None) == "diễn biến" and getattr(q, "quan_he_voi", None) == p.id):
        return True
    mp, mq = getattr(p, "moc_thoi_gian", None), getattr(q, "moc_thoi_gian", None)
    return bool(mp and mq and _thuong(mp) != _thuong(mq))


# ─── _sau_di_ung() — Lấy phần chất nêu sau chữ dị ứng ─────────────────────────────────
def _sau_di_ung(p) -> str:
    m = re.search(r"dị ứng\s*(với\s*)?(.*)$", _thuong(p.noi_dung))
    return (m.group(2) if m else "").strip(" .,")


# ─── _trai_di_ung() — Kiểm tra phủ định dị ứng trái với dị ứng khẳng định ─────────────
# Không dị ứng gì trái mọi dị ứng; không dị ứng thuốc chỉ trái dị ứng thuốc.
def _trai_di_ung(am, duong) -> bool:
    """'không dị ứng (gì)' trái với MỌI dị ứng; 'không dị ứng thuốc' chỉ trái với dị
    ứng một THUỐC ('dị ứng đạm sữa bò' không trái — đo 24/09/2026, ca asr_010_A);
    còn lại chỉ trái khi cùng chất."""
    chat_am, chat_duong = _sau_di_ung(am), _sau_di_ung(duong)
    if chat_am in ("", "gì", "gì cả", "gì hết"):
        return True
    if chat_am.startswith("thuốc"):
        return bool(getattr(duong, "thuoc", None)) or bool(THUOC_TU_DIEN.search(chat_duong)) or             bool(re.search(r"(?<!\w)(thuốc|kháng sinh|\w+cillin|\w+micin)(?!\w)", chat_duong))
    return bool(chat_am) and (chat_am in chat_duong or chat_duong in chat_am)


# ═══ mau_thuan() — Phát hiện hai mệnh đề cùng chủ thể mâu thuẫn nhau ══════════════════
# Gồm dị ứng phủ định và khẳng định, trạng thái dùng thuốc, và cùng nội dung khác cờ phủ
# định.
def mau_thuan(ctx: NguCanh, ps, loai_theo_id) -> List[CanhBao]:
    ra = []
    con = [p for p in ps if _con(p)]
    for p, q in combinations(con, 2):
        if getattr(p, "chu_the_id", 0) != getattr(q, "chu_the_id", 0):
            continue
        luot = sorted(set(ctx.dan(p)) | set(ctx.dan(q)))
        np_, nq = _thuong(p.noi_dung), _thuong(q.noi_dung)
        ma, kl = None, LOI_PHAT_HIEN
        # "không dị ứng thuốc" và "dị ứng penicillin" cùng một người
        if "dị ứng" in np_ and "dị ứng" in nq and bool(getattr(p, "phu_dinh", False)) != bool(
                getattr(q, "phu_dinh", False)):
            am, duong = (p, q) if getattr(p, "phu_dinh", False) else (q, p)
            if _trai_di_ung(am, duong):
                ma = "INTERNAL_CONTRADICTION"
        tp, tq = getattr(p, "thuoc", None) or {}, getattr(q, "thuoc", None) or {}
        # Một bên là Y LỆNH của bác sĩ ("ngưng panadol" sau khi người bệnh kể đang uống)
        # thì là kế hoạch mới, không phải mâu thuẫn (đo 24/09/2026: 1/20 lần đúng).
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


# ─── _gia_tri_rieng() — Lấy giá trị riêng của mệnh đề này so với mệnh đề kia ──────────
# Mốc thời gian và các trường thuốc khác nhau.
def _gia_tri_rieng(a, b) -> List[str]:
    """Mốc thời gian / trường thuốc của `a` khác với `b`."""
    ra = []
    if getattr(a, "moc_thoi_gian", None) and getattr(a, "moc_thoi_gian", None) != getattr(b, "moc_thoi_gian", None):
        ra.append(a.moc_thoi_gian)
    ta, tb = getattr(a, "thuoc", None) or {}, getattr(b, "thuoc", None) or {}
    ra += [str(v) for k, v in ta.items() if v and v != tb.get(k)]
    return [_thuong(v) for v in ra if str(v).strip()]


# ─── _da_bi_sua() — Kiểm tra giá trị đã bị đính chính trong lời thoại ─────────────────
# Dạng chứ không phải X, hoặc X rồi à nhầm.
def _da_bi_sua(gia_tri: List[str], van: str) -> bool:
    for v in gia_tri:
        e = re.escape(v)
        if re.search(rf"(?<!\w)không phải\s+(là\s+)?{e}(?!\w)", van):
            return True
        m = DAU_SUA.search(van)
        if m and m.group(0) != "không phải" and re.search(rf"(?<!\w){e}(?!\w)", van[:m.start()]) \
                and not re.search(rf"(?<!\w){e}(?!\w)", van[m.end():]):
            return True
    return False


# ═══ dinh_chinh_nguoc() — Phát hiện bản đã đính chính lại bị đánh dấu thay thế ════════
# Mệnh đề còn hiệu lực lại giữ giá trị đã sửa (CORRECTION_NOT_APPLIED).
def dinh_chinh_nguoc(ctx: NguCanh, ps, loai_theo_id) -> List[CanhBao]:
    """Vòng 6 (26/11/2026): hai dòng cùng nội dung, `x` 'bị thay thế', `y` 'còn hiệu lực'.
    Chiều thay thế ngược khi (a) chính `x` khai là đính chính của `y`, hoặc (b) giá trị
    riêng của `y` (mốc thời gian, liều...) là giá trị ĐÃ BỊ SỬA trong lượt dẫn ('... chứ
    không phải <y>', '<y>, à nhầm, ...') còn giá trị của `x` thì không.
    Bản cũ và bản mới thường dẫn CÙNG lượt, nên không dùng thứ tự lượt."""
    ra = []
    for x in ps:
        if _con(x) or not ctx.dan(x):
            continue
        for y in ps:
            if not _con(y) or getattr(y, "chu_the_id", 0) != getattr(x, "chu_the_id", 0) \
                    or _thuong(y.noi_dung) != _thuong(x.noi_dung):
                continue
            khai = getattr(x, "quan_he", None) == "đính chính" and getattr(x, "quan_he_voi", None) == y.id
            van = _thuong(" ".join(ctx.luot[s][1] for s in sorted(set(ctx.dan(x)) | set(ctx.dan(y)))))
            if not khai and not (_da_bi_sua(_gia_tri_rieng(y, x), van) and not _da_bi_sua(_gia_tri_rieng(x, y), van)):
                continue
            luot = sorted(set(ctx.dan(x)) | set(ctx.dan(y)))
            for a, b in ((y, x), (x, y)):
                ra.append(CanhBao(ma="CORRECTION_NOT_APPLIED", phat_bieu_id=a.id, luot=luot, trich=[a.noi_dung],
                                  ly_do=f"Dòng #{y.id} còn hiệu lực nhưng giữ giá trị đã bị sửa; dòng #{x.id} "
                                        f"(bản đã đính chính) lại bị đánh dấu thay thế.",
                                  ket_luan=NGHI_RUI_RO, bat_dinh=TRUNG, bo_phat_hien="toan_ca:dinh_chinh_nguoc",
                                  muc_do=muc_do("CORRECTION_NOT_APPLIED", loai_theo_id.get(a.id, "khac")),
                                  loai_tt=loai_theo_id.get(a.id, "khac")))
    return ra


# ═══ ghi_lap() — Phát hiện mệnh đề ghi lặp ════════════════════════════════════════════
# Trùng nội dung, hoặc tương đồng từ từ 0,85 trở lên cùng chủ thể và cờ phủ định.
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
