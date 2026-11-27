# -*- coding: utf-8 -*-
"""[Lớp cảnh báo]
Làm gì   : Tìm những đoạn hội thoại có thông tin lâm sàng mà bản nháp chưa ghi, dùng chung
           cho cả hệ thống.
Vào → Ra : ngữ cảnh hội thoại + bản nháp → các đoạn bị bỏ sót kèm loại thông tin
Đọc từ   : quet() quét cả ca; phan_loai() xác định đoạn thuộc loại thông tin nào
Mục lục (các hàm/lớp chính):
  quet()             Bộ phát hiện bỏ sót duy nhất cho cả ca
  quet_chi_tiet()    Phân loại mọi đoạn chưa ghi, trả (đoạn, mã, cụm)
  phan_loai()        Phân loại bỏ sót cho một đoạn thoại chưa được ghi
  cap_hoi_dap()      Cảnh báo cặp hỏi đáp lâm sàng không dòng nào dẫn tới
  class _DaGhi       Tổng hợp những gì bản nháp đã ghi
  la_xa_giao()       Nhận biết đoạn chỉ là xã giao, xưng hô
  la_ve_nguoi_nha()  Nhận biết vế nói về người nhà
Gọi tới  : canh_bao/loai, canh_bao/phat_hien, canh_bao/so_lieu,
           cong_cu_lam_sang/tri_thuc_thuoc, duong_ong/b2_gom_nguoi_thuc_the,
           duong_ong/b4_kiem_can_cu
Dùng bởi : canh_bao/toan_ca, cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
MỘT bộ phát hiện bỏ sót cho cả hệ thống (25/11/2026).

Trước ngày này có HAI bộ chạy song song trên cùng `doan_chua_ghi`:
  - `canh_bao.toan_ca.bo_sot`: lớp cảnh báo, mỗi đoạn MỘT mã (mã đầu tiên khớp);
  - `kiem_duyet_bhyt_va_bo_sot.ActiveOmissionRecoveryEngine` (tầng 4.5): danh sách
    thuốc riêng, `continue` sau loại đầu tiên, và bỏ qua MỌI dị ứng bị sót nếu có một
    mệnh đề nào chứa chữ "dị ứng" — kể cả "không dị ứng thức ăn".
Hai bộ cho hai kết luận khác nhau trên cùng một ca. Tệp này thay cả hai; hai hàm cũ
thành lớp bọc gọi sang đây.

Khác bộ cũ:
  1. Đoạn được tách thành VẾ (dấu phẩy, "và", "rồi", "còn"); mỗi vế cho một mã, nên một
     đoạn cho được nhiều mã ("dị ứng penicillin, đang uống warfarin" -> dị ứng + thuốc).
  2. Dị ứng chỉ coi là ĐÃ GHI khi có mệnh đề dị ứng KHẲNG ĐỊNH cùng chất.
  3. Thuốc chỉ coi là đã ghi khi MỖI tên thuốc trong vế đã có trong một mệnh đề.
  4. Phủ định chỉ coi là đã ghi khi có mệnh đề phủ định mang cùng từ.
"""
import re
from typing import Iterable, List, Optional, Tuple

from src.canh_bao import so_lieu
from src.canh_bao.loai import CAN_XEM, CAO, NGHI_RUI_RO, TRUNG, CanhBao, muc_do
from src.canh_bao.phat_hien import DAU_SUA, DIEU_KIEN_THEM, KHONG_NHO, TUONG_LAI, NguCanh, _thuong, _tu
from src.duong_ong.b4_kiem_can_cu import DAU_NGHI
from src.duong_ong.b2_gom_nguoi_thuc_the import THUOC_TU_DIEN

DI_UNG = re.compile(r"(?<!\w)(dị ứng|mẫn cảm|nổi mẩn (khi|sau)|nổi mề đay|sốc phản vệ|phát ban khi (uống|dùng))(?!\w)")
# Tên thuốc từ MỘT nguồn (data/tri_thuc_thuoc.json); thay danh sách riêng của tầng 4.5 cũ.
from src.cong_cu_lam_sang import tri_thuc_thuoc as _ttt  # noqa: E402
THUOC_THEM = _ttt.regex_ten_thuoc()
THUOC_DONG_Y = re.compile(
    r"(?<!\w)(thuốc tễ|thuốc cam|thuốc hoàn|thuốc tán|thuốc nam|thuốc bắc|cao lá|gói bột (cam|giảm đau)|"
    r"thuốc tàu|viên hoàn trị khớp)(?!\w)")
THUOC_CHUNG = re.compile(r"(?<!\w)((uống|dùng|xịt|tiêm|bôi|kê) thuốc|thuốc \w+|\d+ ?(mg|viên))(?!\w)")
PHU_DINH = re.compile(r"(?<!\w)(không|chưa|chẳng)( từng)? (bị |có |thấy )?"
                      r"(sốt|ho|đau|nôn|khó thở|khó|phù|co giật|dị ứng)(?!\w)")
KHONG_CHAC = re.compile(DAU_NGHI.pattern + "|" + KHONG_NHO.pattern)
_TACH_VE = re.compile(r"\s*(?:[,;]|(?<!\w)(?:và|rồi|còn|nhưng|với lại|thêm nữa)(?!\w))\s*")
# Người nhà làm chủ ngữ trong vế ("mẹ em bị tiểu đường"). Không gồm cháu/bé/con: thường là bệnh nhi.
_NGUOI_NHA = re.compile(r"(?<!\w)(mẹ|bố|ba|má|ông|bà|anh trai|chị gái|em trai|em gái|vợ|chồng|dì|chú|cô"
                        r"|nhà tôi|nhà em)(?!\w)")
_DONG_TU_THUOC = re.compile(r"(?<!\w)(uống|dùng|xịt|tiêm|bôi|kê|đang|vẫn|ngậm|nhỏ|truyền)(?!\w)")
_AM = re.compile(r"(?<!\w)(không|chưa|chẳng|chả)(?!\w)")
_KHONG_PHAI_CHAT = {"thuốc", "gì", "cả", "hết", "với", "nặng", "lắm", "lắm ạ", "ạ", "nha", "bị"}


# ─── _ve() — Tách một đoạn thoại thành các vế nhỏ ─────────────────────────────────────
# Tách theo dấu phẩy, chấm phẩy và các từ nối như và, rồi, còn.
def _ve(t: str) -> List[str]:
    return [v for v in _TACH_VE.split(t) if v and v.strip()]


# ─── _ten_thuoc() — Liệt kê tên thuốc có trong một vế ─────────────────────────────────
# Tra theo từ điển thuốc và bảng tri thức thuốc.
def _ten_thuoc(t: str) -> List[str]:
    return sorted({m.group(1).lower() for bt in (THUOC_TU_DIEN, THUOC_THEM) for m in bt.finditer(t)})


# ─── _chat_di_ung() — Lấy các chất gây dị ứng nêu trong một vế ────────────────────────
# Gồm hoạt chất của thuốc trong vế và từ đứng sau dị ứng, mẫn cảm, sốc phản vệ.
def _chat_di_ung(t: str) -> set:
    """Chat gay di ung trong mot ve: hoat chat cua moi ten thuoc trong ve, cong tu sau "dị ứng /
    mẫn cảm / sốc phản vệ (với)". Truoc ra soat 25/11 chi doc sau "dị ứng", nen "sốc phản vệ
    với penicillin" khong co chat va bi che boi bat ky di ung nao da ghi."""
    chat = {_ttt.hoat_chat(x) or x for x in _ten_thuoc(t)}
    m = DI_UNG.search(t)
    if m:
        sau = re.sub(r"^\s*(với|khi (uống|dùng)|sau (khi )?(uống|dùng))\s*", "", t[m.end():])
        chat |= {_ttt.hoat_chat(x) or x for x in _tu(sau) - _KHONG_PHAI_CHAT}
    return chat


# ═══ la_ve_nguoi_nha() — Nhận biết vế nói về người nhà ════════════════════════════════
# Có từ chỉ người thân (mẹ, bố, vợ, chồng...) thì coi là của người nhà.
def la_ve_nguoi_nha(ve: str) -> bool:
    return bool(_NGUOI_NHA.search(_thuong(ve)))


# ─── _con() — Kiểm tra mệnh đề còn hiệu lực ───────────────────────────────────────────
# Trả về sai nếu mệnh đề đã bị thay thế.
def _con(p) -> bool:
    return getattr(p, "trang_thai", "còn hiệu lực") != "bị thay thế"


# ─── class _DaGhi — Tổng hợp những gì bản nháp đã ghi ─────────────────────────────────
# Có sẵn dị ứng, thuốc, phủ định đã ghi, tách theo người bệnh và người nhà; bỏ mệnh đề
# bị thay thế.
class _DaGhi:
    """Những gì bản ghi đã có — dùng để bỏ các vế đã được ghi ở một lượt khác."""

    def __init__(self, ps: Iterable):
        ps = [p for p in ps if _con(p)]
        # Tách theo NGƯỜI: bệnh nhân (chu_the_id 0) và người khác — dị ứng của mẹ không che dị
        # ứng của cháu (rà soát 25/11).
        self.di_ung = {nn: {am: [_chat_di_ung(_thuong(p.noi_dung)) for p in ps
                                 if DI_UNG.search(_thuong(p.noi_dung))
                                 and bool(getattr(p, "phu_dinh", False)) == am
                                 and (getattr(p, "chu_the_id", 0) != 0) == nn]
                            for am in (False, True)} for nn in (False, True)}
        self.chu = {nn: " ".join(_thuong(p.noi_dung) + " " +
                                 _thuong(((getattr(p, "thuoc", None) or {}).get("ten")) or "")
                                 for p in ps if (getattr(p, "chu_the_id", 0) != 0) == nn)
                    for nn in (False, True)}
        self.phu_dinh = " ".join(_thuong(p.noi_dung) for p in ps if getattr(p, "phu_dinh", False))

    def di_ung_da_ghi(self, ve: str, nguoi_nha: bool = False) -> bool:
        """Vế khẳng định chỉ được mệnh đề khẳng định CÙNG NGƯỜI phủ; vế phủ định chỉ được mệnh
        đề phủ định phủ. Vế không có chất chỉ được mệnh đề cùng chiều không có chất phủ. Mệnh
        để phủ định không chặt ("không dị ứng gì") phủ mọi vế phủ định."""
        am = bool(_AM.search(ve))
        ds = self.di_ung[nguoi_nha][am]
        chat = _chat_di_ung(ve)
        if not chat:
            return any(not d for d in ds)
        return any(chat & d or (am and not d) for d in ds)

    def thuoc(self, ten: List[str], nguoi_nha: bool = False) -> bool:
        chu = self.chu[nguoi_nha]
        return bool(ten) and all(re.search(rf"(?<!\w){re.escape(t)}(?!\w)", chu) for t in ten)

    def phu_dinh_co(self, tu: str) -> bool:
        return bool(tu) and re.search(rf"(?<!\w){re.escape(tu)}(?!\w)", self.phu_dinh) is not None


# ═══ phan_loai() — Phân loại bỏ sót cho một đoạn thoại chưa được ghi ══════════════════
# Trả về danh sách (mã, cụm khớp): dị ứng, thuốc, phủ định, đính chính, số, kế hoạch...;
# rỗng nếu các vế đã được ghi.
def phan_loai(ctx: NguCanh, so: int, doan: str, da: Optional[_DaGhi] = None) -> List[Tuple[str, str]]:
    """-> [(ma, cụm khớp)] theo thứ tự, không lặp mã. Rỗng khi mọi vế đã được ghi."""
    da = da or _DaGhi([])
    t = _thuong(doan)
    ra, co_ma = [], set()

    def them(ma, cum):
        if ma not in co_ma:
            co_ma.add(ma)
            ra.append((ma, cum))

    bi_bo = False  # có vẻ khớp một loại nhưng đã được ghi
    nn = la_ve_nguoi_nha(t)
    trong_di_ung = False  # vế trước là dị ứng: "dị ứng penicillin và aspirin" -> aspirin cũng là chất
    for ve in _ve(t):
        ten = _ten_thuoc(ve)
        m = DI_UNG.search(ve)
        if m or (trong_di_ung and ten and not _DONG_TU_THUOC.search(ve)):
            # Về dị ứng: tên thuốc trong vế là CHẤT gây dị ứng, không phải thuốc đang dùng.
            trong_di_ung = True
            if da.di_ung_da_ghi(ve, nn):
                bi_bo = True
            else:
                them("OMITTED_ALLERGY", ve)
            continue
        trong_di_ung = False
        m_dy = THUOC_DONG_Y.search(ve)
        if ten or m_dy or THUOC_CHUNG.search(ve):
            if ten and not m_dy and da.thuoc(ten, nn):
                bi_bo = True
            else:
                them("OMITTED_MEDICATION", ve)
            continue
        m = PHU_DINH.search(ve)
        if m:
            if da.phu_dinh_co(m.group(4)):
                bi_bo = True
            else:
                them("OMITTED_NEGATION", ve)
            continue
        if DAU_SUA.search(ve):
            them("OMITTED_CORRECTION", ve)
        elif KHONG_CHAC.search(ve):
            them("OMITTED_UNCERTAINTY", ve)
    so_ = so_lieu.tach(doan)
    if so_ and any(s.ho != "thoi_gian" for s in so_):
        them("OMITTED_NUMERIC_VALUE", doan)
    if not ra and so_:
        them("OMITTED_DURATION" if all(s.ho == "thoi_gian" for s in so_) else "OMITTED_NUMERIC_VALUE", doan)
    if not ra and ctx.la_nv(so) and (DIEU_KIEN_THEM.search(t) or TUONG_LAI.search(t)):
        them("OMITTED_PLAN", doan)
    if not ra and not bi_bo and not la_xa_giao(t):
        them("POSSIBLE_IMPORTANT_OMISSION", doan)
    return ra


# Từ xã giao / đếm / xưng hô / thủ tục khám — không mang thông tin lâm sàng (vòng 4 cây lỗi 25/11/2026:
# bản sạch 5,8 cảnh báo bỏ sót chung chung mỗi ca, phần lớn là "Vâng em nghe", "Chúc bác sĩ…").
_XA_GIAO = re.compile(
    r"(?<!\w)(chào|xin chào|cảm ơn|cám ơn|chúc|xin phép|xin|phép|về|vâng|dạ|thưa|ạ|à|ờ|ừ|ừm|nhé|nhe|nha|ơi|"
    r"đúng rồi|đúng|rồi|vậy|thế|nghe|hiểu|biết rồi|ok|được|vẫn|ổn|bận|hơi|tốt|công tác|tiếp theo|tiếp|theo|"
    r"cho|hỏi|để|xem|khám|kể|nói|đưa|đi|đến|tới|là|thì|mà|và|với|nữa|lại|cũng|nhưng|còn|"
    r"bác sĩ|bác sỹ|bác|sĩ|điều dưỡng|tôi|em|anh|chị|cô|chú|cháu|con|mẹ|bố|ba|má|ông|bà|mình|ấy|nó|"
    r"này|kia|đây|đó|ở|có|không|chưa|gì|ạ)(?!\w)")


# ═══ la_xa_giao() — Nhận biết đoạn chỉ là xã giao, xưng hô ════════════════════════════
# Bỏ hết từ xã giao mà không còn chữ nào thì không đáng báo bỏ sót.
def la_xa_giao(t: str) -> bool:
    """Đoạn chỉ gồm từ xã giao/xưng hô/đếm — không còn chữ nào khác."""
    con = _XA_GIAO.sub(" ", _thuong(t))
    return not re.search(r"\w", con)


# ═══ quet_chi_tiet() — Phân loại mọi đoạn chưa ghi, trả (đoạn, mã, cụm) ═══════════════
def quet_chi_tiet(ctx: NguCanh, ps, doan_chua_ghi: List[dict]) -> List[Tuple[dict, str, str]]:
    """-> [(doan, ma, cum)] cho mỗi mã của mỗi đoạn chưa ghi."""
    da = _DaGhi(ps)
    return [(d, ma, cum) for d in doan_chua_ghi for ma, cum in phan_loai(ctx, d["luot"], d["doan"], da)]


_TEN_CHU_DE = {"di_ung": "dị ứng", "thuoc": "thuốc", "tien_su": "tiền sử", "trieu_chung": "triệu chứng"}


# ═══ cap_hoi_dap() — Cảnh báo cặp hỏi đáp lâm sàng không dòng nào dẫn tới ═════════════
# Chỉ xét chủ đề dị ứng, thuốc, tiền sử, triệu chứng; chủ đề khác bỏ qua.
def cap_hoi_dap(cap: Iterable[dict]) -> List[CanhBao]:
    """OMITTED_ANSWER cho cặp hỏi-đáp chưa ghi có chủ đề lâm sàng. Chủ đề "khác" (nhà ở
    đâu, đi với ai) bỏ qua: đo 24/09 cho thấy cảnh báo chung chung chỉ đúng 2,8%."""
    ra = []
    for c in cap:
        if c["chu_de"] not in _TEN_CHU_DE:
            continue
        ra.append(CanhBao(ma="OMITTED_ANSWER", phat_bieu_id=None, luot=[c["luot_hoi"], c["luot_dap"]],
                          trich=[c["cau_hoi"], c["tra_loi"]],
                          ly_do=f"Lượt {c['luot_hoi']} hỏi về {_TEN_CHU_DE[c['chu_de']]}: “{c['cau_hoi']}”; "
                                f"lượt {c['luot_dap']} trả lời “{c['tra_loi']}” — không dòng nào dẫn tới.",
                          ket_luan=NGHI_RUI_RO, bat_dinh=TRUNG, bo_phat_hien="toan_ca:cap_hoi_dap",
                          muc_do=muc_do("OMITTED_ANSWER", "di_ung" if c["chu_de"] == "di_ung" else
                                        "thuoc" if c["chu_de"] == "thuoc" else "khac")))
    return ra


# ═══ quet() — Bộ phát hiện bỏ sót duy nhất cho cả ca ══════════════════════════════════
# Gộp cảnh báo cặp hỏi đáp và từng đoạn chưa ghi; mã chung chung chỉ ở mức cần xem,
# không hiện cho bác sĩ.
def quet(ctx: NguCanh, ps, doan_chua_ghi: List[dict], cap: Iterable[dict] = ()) -> List[CanhBao]:
    ra = cap_hoi_dap(cap)
    for d, ma, cum in quet_chi_tiet(ctx, ps, doan_chua_ghi):
        doan, so = d["doan"], d["luot"]
        # Loại chung chung: 792/887 cảnh báo bỏ sót, 2,8% trùng chỗ đáp án bị sót (đo
        # 24/09/2026). Giữ ở backend để đo, KHÔNG hiện cho bác sĩ (can_xem).
        chung = ma == "POSSIBLE_IMPORTANT_OMISSION"
        ra.append(CanhBao(ma=ma, phat_bieu_id=None, luot=[so], trich=[doan],
                          ly_do=f"Lượt {so} ({d.get('vai') or 'không rõ vai'}): “{doan}” — không dòng nào dẫn tới"
                                + ("" if chung or cum == _thuong(doan) else f" (“{cum}”)")
                                + (" — có thể là của người nhà, không phải người bệnh" if la_ve_nguoi_nha(doan) else "")
                                + ".",
                          ket_luan=CAN_XEM if chung else NGHI_RUI_RO, bat_dinh=CAO if chung else TRUNG,
                          bo_phat_hien="toan_ca:bo_sot",
                          muc_do=muc_do(ma, "di_ung" if ma == "OMITTED_ALLERGY" else
                                        "thuoc" if ma == "OMITTED_MEDICATION" else "khac")))
    return ra
