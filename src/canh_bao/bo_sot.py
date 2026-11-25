# -*- coding: utf-8 -*-
"""MOT bo phat hien bo sot cho ca he thong (25/11/2026).

Truoc ngay nay co HAI bo chay song song tren cung `doan_chua_ghi`:
  - `canh_bao.toan_ca.bo_sot`: lop canh bao, moi doan MOT ma (ma dau tien khop);
  - `kiem_duyet_bhyt_va_bo_sot.ActiveOmissionRecoveryEngine` (tang 4.5): danh sach
    thuoc rieng, `continue` sau loai dau tien, va bo qua MOI di ung bi sot neu co mot
    menh de nao chua chu "dị ứng" — ke ca "không dị ứng thức ăn".
Hai bo cho hai ket luan khac nhau tren cung mot ca. Tep nay thay ca hai; hai ham cu
thanh lop boc goi sang day.

Khac bo cu:
  1. Doan duoc tach thanh VE (dau phay, "và", "rồi", "còn"); moi ve cho mot ma, nen mot
     doan cho duoc nhieu ma ("dị ứng penicillin, đang uống warfarin" -> di ung + thuoc).
  2. Di ung chi coi la DA GHI khi co menh de di ung KHANG DINH cung chat.
  3. Thuoc chi coi la da ghi khi MOI ten thuoc trong ve da co trong mot menh de.
  4. Phu dinh chi coi la da ghi khi co menh de phu dinh mang cung tu.
"""
import re
from typing import Iterable, List, Optional, Tuple

from src.canh_bao import so_lieu
from src.canh_bao.loai import CAN_XEM, CAO, NGHI_RUI_RO, TRUNG, CanhBao, muc_do
from src.canh_bao.phat_hien import DAU_SUA, DIEU_KIEN_THEM, KHONG_NHO, TUONG_LAI, NguCanh, _thuong, _tu
from src.khoa_bang_chung import DAU_NGHI
from src.thuc_the import THUOC_TU_DIEN

DI_UNG = re.compile(r"(?<!\w)(dị ứng|mẫn cảm|nổi mẩn (khi|sau)|nổi mề đay|sốc phản vệ|phát ban khi (uống|dùng))(?!\w)")
# Ten thuoc tu MOT nguon (data/tri_thuc_thuoc.json); thay danh sach rieng cua tang 4.5 cu.
from src import tri_thuc_thuoc as _ttt  # noqa: E402
THUOC_THEM = _ttt.regex_ten_thuoc()
THUOC_DONG_Y = re.compile(
    r"(?<!\w)(thuốc tễ|thuốc cam|thuốc hoàn|thuốc tán|thuốc nam|thuốc bắc|cao lá|gói bột (cam|giảm đau)|"
    r"thuốc tàu|viên hoàn trị khớp)(?!\w)")
THUOC_CHUNG = re.compile(r"(?<!\w)((uống|dùng|xịt|tiêm|bôi|kê) thuốc|thuốc \w+|\d+ ?(mg|viên))(?!\w)")
PHU_DINH = re.compile(r"(?<!\w)(không|chưa|chẳng)( từng)? (bị |có |thấy )?"
                      r"(sốt|ho|đau|nôn|khó thở|khó|phù|co giật|dị ứng)(?!\w)")
KHONG_CHAC = re.compile(DAU_NGHI.pattern + "|" + KHONG_NHO.pattern)
_TACH_VE = re.compile(r"\s*(?:[,;]|(?<!\w)(?:và|rồi|còn|nhưng|với lại|thêm nữa)(?!\w))\s*")
# Nguoi nha lam chu ngu trong ve ("mẹ em bị tiểu đường"). Khong gom cháu/bé/con: thuong la benh nhi.
_NGUOI_NHA = re.compile(r"(?<!\w)(mẹ|bố|ba|má|ông|bà|anh trai|chị gái|em trai|em gái|vợ|chồng|dì|chú|cô"
                        r"|nhà tôi|nhà em)(?!\w)")
_DONG_TU_THUOC = re.compile(r"(?<!\w)(uống|dùng|xịt|tiêm|bôi|kê|đang|vẫn|ngậm|nhỏ|truyền)(?!\w)")
_AM = re.compile(r"(?<!\w)(không|chưa|chẳng|chả)(?!\w)")
_KHONG_PHAI_CHAT = {"thuốc", "gì", "cả", "hết", "với", "nặng", "lắm", "lắm ạ", "ạ", "nha", "bị"}


def _ve(t: str) -> List[str]:
    return [v for v in _TACH_VE.split(t) if v and v.strip()]


def _ten_thuoc(t: str) -> List[str]:
    return sorted({m.group(1).lower() for bt in (THUOC_TU_DIEN, THUOC_THEM) for m in bt.finditer(t)})


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


def la_ve_nguoi_nha(ve: str) -> bool:
    return bool(_NGUOI_NHA.search(_thuong(ve)))


def _con(p) -> bool:
    return getattr(p, "trang_thai", "còn hiệu lực") != "bị thay thế"


class _DaGhi:
    """Nhung gi ban ghi da co — dung de bo cac ve da duoc ghi o mot luot khac."""

    def __init__(self, ps: Iterable):
        ps = [p for p in ps if _con(p)]
        # Tach theo NGUOI: benh nhan (chu_the_id 0) va nguoi khac — di ung cua me khong che di
        # ung cua chau (ra soat 25/11).
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
        """Ve khang dinh chi duoc menh de khang dinh CUNG NGUOI phu; ve phu dinh chi duoc menh
        de phu dinh phu. Ve khong co chat chi duoc menh de cung chieu khong co chat phu. Menh
        de phu dinh khong chat ("không dị ứng gì") phu moi ve phu dinh."""
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


def phan_loai(ctx: NguCanh, so: int, doan: str, da: Optional[_DaGhi] = None) -> List[Tuple[str, str]]:
    """-> [(ma, cum khop)] theo thu tu, khong lap ma. Rong khi moi ve da duoc ghi."""
    da = da or _DaGhi([])
    t = _thuong(doan)
    ra, co_ma = [], set()

    def them(ma, cum):
        if ma not in co_ma:
            co_ma.add(ma)
            ra.append((ma, cum))

    bi_bo = False  # co ve khop mot loai nhung da duoc ghi
    nn = la_ve_nguoi_nha(t)
    trong_di_ung = False  # ve truoc la di ung: "dị ứng penicillin và aspirin" -> aspirin cung la chat
    for ve in _ve(t):
        ten = _ten_thuoc(ve)
        m = DI_UNG.search(ve)
        if m or (trong_di_ung and ten and not _DONG_TU_THUOC.search(ve)):
            # Ve di ung: ten thuoc trong ve la CHAT gay di ung, khong phai thuoc dang dung.
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


# Tu xa giao / dem / xung ho / thu tuc kham — khong mang thong tin lam sang (vong 4 cay loi 25/11/2026:
# ban sach 5,8 canh bao bo sot chung chung moi ca, phan lon la "Vâng em nghe", "Chúc bác sĩ…").
_XA_GIAO = re.compile(
    r"(?<!\w)(chào|xin chào|cảm ơn|cám ơn|chúc|xin phép|xin|phép|về|vâng|dạ|thưa|ạ|à|ờ|ừ|ừm|nhé|nhe|nha|ơi|"
    r"đúng rồi|đúng|rồi|vậy|thế|nghe|hiểu|biết rồi|ok|được|vẫn|ổn|bận|hơi|tốt|công tác|tiếp theo|tiếp|theo|"
    r"cho|hỏi|để|xem|khám|kể|nói|đưa|đi|đến|tới|là|thì|mà|và|với|nữa|lại|cũng|nhưng|còn|"
    r"bác sĩ|bác sỹ|bác|sĩ|điều dưỡng|tôi|em|anh|chị|cô|chú|cháu|con|mẹ|bố|ba|má|ông|bà|mình|ấy|nó|"
    r"này|kia|đây|đó|ở|có|không|chưa|gì|ạ)(?!\w)")


def la_xa_giao(t: str) -> bool:
    """Doan chi gom tu xa giao/xung ho/dem — khong con chu nao khac."""
    con = _XA_GIAO.sub(" ", _thuong(t))
    return not re.search(r"\w", con)


def quet_chi_tiet(ctx: NguCanh, ps, doan_chua_ghi: List[dict]) -> List[Tuple[dict, str, str]]:
    """-> [(doan, ma, cum)] cho moi ma cua moi doan chua ghi."""
    da = _DaGhi(ps)
    return [(d, ma, cum) for d in doan_chua_ghi for ma, cum in phan_loai(ctx, d["luot"], d["doan"], da)]


_TEN_CHU_DE = {"di_ung": "dị ứng", "thuoc": "thuốc", "tien_su": "tiền sử", "trieu_chung": "triệu chứng"}


def cap_hoi_dap(cap: Iterable[dict]) -> List[CanhBao]:
    """OMITTED_ANSWER cho cap hoi-dap chua ghi co chu de lam sang. Chu de "khac" (nha o
    dau, di voi ai) bo qua: do 24/09 cho thay canh bao chung chung chi dung 2,8%."""
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


def quet(ctx: NguCanh, ps, doan_chua_ghi: List[dict], cap: Iterable[dict] = ()) -> List[CanhBao]:
    ra = cap_hoi_dap(cap)
    for d, ma, cum in quet_chi_tiet(ctx, ps, doan_chua_ghi):
        doan, so = d["doan"], d["luot"]
        # Loai chung chung: 792/887 canh bao bo sot, 2,8% trung cho dap an bi sot (do
        # 24/09/2026). Giu o backend de do, KHONG hien cho bac si (can_xem).
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
