# -*- coding: utf-8 -*-
"""Tang 4 — KHOA BANG CHUNG: moi phat bieu phai chung minh duoc bang CHINH hoi
thoai truoc khi duoc vao than ho so.

VI SAO CAN — va vi sao `sua_cuc_bo` khong du. Bon phep kiem cua `sua_cuc_bo`
doi chieu cau ban nhap voi BANG PHAT BIEU do chinh mo hinh trich ra. Mo hinh
bia mot phat bieu thi bang co phat bieu do, va phep kiem noi "co nguon". Tang
nay quay lai HOI THOAI: trich dan phai la chuoi nguyen van cua luot, va chinh
doan do phai noi dung nguoi, dung muc khang dinh.

BA CAU HOI:

  1. co doan hoi thoai nao THUC SU noi dieu nay khong   K1 nguon, K2 noi dung
  2. doan do noi ve DUNG NGUOI khong                     K3 chu the
  3. doan do ung ho DUNG MUC khang dinh khong            K4 muc, K5 thoi gian

HAI MUC DO, va vi sao phai tach:

  chan      co bang chung PHU DINH ro rang: trich dan khong co trong hoi thoai,
            doan dan noi ve nguoi KHAC bang mot tu khong mo ho ("toi"), cau goc
            chi nghi ma ban ghi chac, cau dieu kien ghi thanh su that. Phat bieu
            KHONG vao than ho so — xuong CAN XAC NHAN, kem ly do.
  canh bao  THIEU bang chung khang dinh: chu the chi suy tu nguoi noi, noi dung
            khong trung tu nao voi doan dan, moc thoi gian khong thay. Van vao
            than; `cong_rui_ro` dung de xep thu tu cho bac si duyet.

Chan qua tay la "giam loi bang cach viet it di" — bay lon nhat cua du an, da vap
mot lan o `duong_danh_doi` (07/09/2026): day xuong theo diem rui ro thua nhom chon
bua cung ty le o 2/3 nguong. Nen thieu bang chung KHANG DINH chi canh bao, va
yeu cau dat TRUOC khi do: tren dap an hoan hao, chan oan <= 1%.

KHONG DUNG BANG LOI DAN THUONG CUA BO SINH. `loi_dan_thuong.DAN_THUONG` la thu bo
sinh dung de lam kho du lieu; dung no o day la de he thong biet truoc dap an. Nen
K2 chi la canh bao: "tim dap thinh thich" -> "hoi hop" khong trung tu nao ma van
dung, va chan no la chan oan.

TU XUNG HO — CHO DE CHAN OAN NHAT. "Toi" luon la nguoi dang noi: du can cu de
chan. "Em" va "chau" thi KHONG: me tu xung "em" voi bac si ma bac si cung goi
benh nhan nguoi lon la "em"; con gai tu xung "chau" ma "chau" cung la cach goi
benh nhi. Hai tu nay chi du de canh bao. Gioi han nay phai vao bao cao: do tren
dap an lam hong co chu dinh (khuon train), doi chu the bi CHAN 14,7%, CANH BAO
82,4%, LOT 2,9%.

HIEU CHINH 11/09/2026, TREN DAP AN HOAN HAO CUA TAP TRAIN (khong nhin tap khac):
chan oan ban dau 2,04%, ba nguyen nhan, ca ba da sua:
  - "toi nho lai roi, 2 ngay chu khong phai 3 ngay": "toi" o day noi ve viec NHO,
    khong phai chu the cua thong tin -> `_TU_XUNG_KE` giu cho truoc
  - "lau roi chua thay moc rang" (cach noi dan thuong cua "cham moc rang") khop
    "chua thay" -> dau hieu chua ghi nhan doi phai co "bi"/"gi"/"bao gio"
  - "Theo doi suy giap": dung DAU cau la chan doan TAM, nhung "Viem gan B man,
    theo doi" la chan doan CHAC kem ke hoach -> "theo doi" chi tinh khi dung dau
Lan hai, cung tap: 0,15% (49 lan, deu "tro minh" — "minh" trong tu ghep chi co
the) roi 0,02% (7 lan, deu "con chi chua thay bi bao gio" — "anh", "chi" chua la
tu chi nguoi). K4 chi doc chuan hoa CHAC: nghia can hoi cua "nong ham hap" mang
chu "co the" vao. Bo ban sao ly do kham khoi dap an: 28.982 menh de vao than.
"""
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Tuple

from src import chuan_hoa, thuc_the
from src.doan_van import cac_doan, dau_ket
from src.phat_bieu import la_vai_nhan_vien
from src.thuoc_do_quy_gan import _tu_noi_dung

CHAN = "chặn"
CANH_BAO = "cảnh báo"

LY_DO = {
    "khong_trich_dan": "không có trích dẫn nguyên văn",
    "luot_khong_ton_tai": "lượt được dẫn không tồn tại",
    "trich_khong_co": "trích dẫn không có trong hội thoại",
    "trich_lech_luot": "trích dẫn nằm ở lượt khác lượt được dẫn",
    "noi_dung_khong_khop": "nội dung không trùng từ nào với đoạn dẫn",
    "phuong_ngu_can_hoi": "chỉ khớp qua một từ phương ngữ mơ hồ",
    "chu_the_nguoi_ke": "đoạn dẫn nói về chính người kể, không phải bệnh nhân",
    "chu_the_benh_nhan": "đoạn dẫn nói về bệnh nhân, không phải người nhà",
    "chu_the_nguoi_khac": "đoạn dẫn nhắc người nhà — có thể không phải của bệnh nhân",
    "chu_the_suy_tu_nguoi_noi": "chủ thể chỉ suy từ người nói — đoạn dẫn không có từ chỉ người",
    "chu_the_chua_ro": "chưa rõ chủ thể",
    "dieu_kien": "câu điều kiện ghi như sự thật",
    "vuot_muc_nghi": "câu gốc chỉ nghi ngờ, bản ghi khẳng định",
    "vuot_muc_chua_ghi_nhan": "câu gốc là chưa ghi nhận, bản ghi khẳng định",
    "phu_dinh_vuot_muc": "câu gốc là chưa ghi nhận, bản ghi phủ định chắc chắn",
    "co_tu_phu_dinh": "đoạn dẫn có từ phủ định",
    "moc_khong_thay": "mốc thời gian không thấy trong lượt dẫn",
    "mau_thuan": "nguồn mâu thuẫn, chưa xác nhận",
    "lieu_khong_thay": "liều thuốc không có trong lượt được dẫn",
    "chi_tiet_thuoc_khong_thay": "số lần dùng, lúc bắt đầu hoặc lúc ngừng thuốc không có trong lượt được dẫn",
    "duong_dung_khong_thay": "đường dùng thuốc không có trong lượt được dẫn",
}

# ----------------------------------------------------- tu chi nguoi
TU_TU_XUNG_RO = ("tôi", "tui", "mình", "tớ")
# Tu xung HOAC cach goi benh nhan. "anh", "chi" them 11/09/2026 (dap an train):
# 7/7 lan chan oan cuoi cung deu la nguoi nha noi "con chi chua thay bi bao gio"
# ve benh nhan — khoa khong biet "chi" la tu chi nguoi, nen lui ve dau cau, gap
# "toi thi di ung X" va chan. Lan do sau con 1/28.982, cung kieu: "con chu chua
# thay bi bao gio" — nen them ca lop tu xung ho tran "chu", "co", "ong". KHONG
# them "bac": "bac" trong "bac si" la mot tu rieng, khop vao la sai.
# Cum dai ("anh ay", "chi gai", "ong noi") van chiem cho truoc.
TU_MO = ("cháu", "con", "em", "anh", "chị", "chú", "cô", "ông")
# Them 11/09/2026 cung luc voi bang xung ho moi cua bo sinh: nguoi nha xung "toi"
# thi goi benh nhan "chau nha toi", "con toi" — khong co o day thi chu "toi" trong
# cum do bi doc thanh tu xung, va khoa chan oan.
TU_BENH_NHAN_RO = ("bé nhà em", "con nhà em", "cháu nó", "nhà em", "em bé", "bé",
                   "ông ấy", "bà ấy", "anh ấy", "chị ấy", "bệnh nhân", "trẻ",
                   "bé nhà tôi", "con nhà tôi", "cháu nhà em", "cháu nhà tôi",
                   "cháu tôi", "con tôi", "con em", "nhà tôi", "ông nhà tôi",
                   "bà nhà tôi", "cô ấy", "chú ấy", "bác ấy", "em ấy")
TU_HO_HANG = ("con trai", "con gái", "anh trai", "chị gái", "em trai", "em gái",
              "ông nội", "bà nội", "ông ngoại", "bà ngoại", "mẹ", "bố", "cha",
              "chồng", "vợ", "bà")
_SO_HUU_GOC = TU_HO_HANG + ("ba", "má", "ông", "anh", "chị")
_SO_HUU_DUOI = ("tôi", "em", "mình", "cháu", "nó", "tui")
# Tu xung trong LOI KE VE VIEC NOI — khong phai chu the cua thong tin.
_VIEC_NOI = ("nhầm", "nhớ nhầm", "nói nhầm", "nhớ lại", "nói lại", "nhớ rồi",
             "nghĩ", "thấy là", "không chắc", "hay lo", "đi thay")
# "minh" trong tu ghep chi CO THE, khong phai tu xung: "tro minh ca dem khong ngu"
# la noi ve tre. Hieu chinh 11/09/2026 tren dap an TAP TRAIN: 49/49 lan chan oan
# con lai deu la "tro minh" — khoa doc "minh" thanh nguoi nha tu ke ve minh. Tren
# train chi co "tro minh"; cac tu ghep con lai la tu vung pho thong, them de khoi
# vap lai dung loi nay o tu khac.
_MINH_TU_GHEP = ("trở mình", "giật mình", "rùng mình", "cựa mình", "mình mẩy",
                 "nóng mình", "một mình", "khắp mình")
_TU_XUNG_KE = ([f"{a} {b}" for a in TU_TU_XUNG_RO + TU_MO for b in _VIEC_NOI]
               + [f"theo {a}" for a in TU_TU_XUNG_RO + TU_MO]
               + list(_MINH_TU_GHEP))

# ----------------------------------------------------- dau hieu muc khang dinh
DAU_NGHI = re.compile(r"(?<!\w)(nghi|nghĩ nhiều đến|nghĩ là|có thể|hình như|"
                      r"chắc là|không chắc|chưa rõ|chưa kết luận)(?!\w)")
# "Theo doi X" DAU doan: cach bac si ghi chan doan TAM. "X, theo doi": chan doan
# chac kem ke hoach — khong phai rao don.
DAU_THEO_DOI = re.compile(r"^\s*theo dõi(?!\w)")
# Doi phai co "bi"/"gi"/"bao gio": "chua thay moc rang" la mot trieu chung (cham
# moc rang), khong phai mot cho trong.
DAU_CHUA_GHI_NHAN = re.compile(r"(?<!\w)(chưa (thấy |từng )?bị( gì| bao giờ)?|"
                               r"chưa bao giờ|chưa thấy gì|chưa từng)(?!\w)")
DAU_DIEU_KIEN = re.compile(r"(?<!\w)(nếu|lỡ mà|hễ|trường hợp)(?!\w)")
# "chu khong phai" la doi lap, khong phai phu dinh noi dung.
DAU_PHU_DINH = re.compile(r"(?<!\w)(không(?! phải)|chẳng|chả|hết|đỡ hẳn|khỏi)(?!\w)")

# Doan THU TUC: khong co thong tin lam sang, khong phai bo sot khi khong ai dan.
# Danh sach lay tu dap an hoan hao cua TAP TRAIN (11/09/2026): 8.136 doan "chua
# ghi" tren 32.741 menh de, gan het la loi chao, loi ke ve viec noi, loi chuyen.
THU_TUC = re.compile(
    r"^(dạ|vâng|ừ|dạ vâng)( ạ)?$"
    r"|chào|cảm ơn|tạm biệt|thưa bác sĩ|^bác sĩ ạ|xin lỗi"
    r"|^(dạ |vâng |dạ vâng )?(không|chưa)( có gì| uống gì| bị gì| đâu)?"
    r"( ạ| nhé| nha| nghen| ha)?$"
    r"|^à không$|không đúng đâu|nhớ rồi|nhớ lại rồi|nói lại cho đúng"
    r"|nói thêm để bác sĩ biết|hay lo"
    r"|để tôi|tôi khám|khám cho|khám xem|xác nhận lại|kể tôi nghe|kể xem"
    r"|nằm lên bàn|mời \w+ ngồi|đi một mình|đi thay|không đến được"
    r"|mệt quá nên|đã đo sinh hiệu|vào từ sáng|mới đăng ký khám|chờ từ nãy"
    r"|chưa kết luận|phải có kết quả"
    # Bo sung lan 2, cung dap an TAP TRAIN: loi ke ve viec NOI NHAM va cau rao
    # "khong chac lam" DUNG MOT MINH — 184 trong 948 lan bao dong gia. Neo ca hai
    # dau: "toi khong chac lam la be da tiem chua" van la thong tin.
    r"|^(à |ờ )?(\w+ )?(nói |nhớ )?nhầm( rồi)?( ạ)?$"
    r"|^(\w+ )?không chắc( lắm)?( ạ)?$", re.I)


@dataclass
class KetQua:
    id: int
    chan: List[str] = field(default_factory=list)          # ma ly do
    canh_bao: List[str] = field(default_factory=list)
    # (so luot, bat dau, ket thuc) cua moi trich dan TIM THAY, tren luot NFC
    doan: List[Tuple[int, int, int]] = field(default_factory=list)

    @property
    def qua(self) -> bool:
        return not self.chan

    def ly_do(self) -> str:
        return "; ".join(LY_DO[m] for m in self.chan + self.canh_bao)

    def to_dict(self):
        d = asdict(self)
        d["qua"] = self.qua
        return d


# ----------------------------------------------------- tim trich dan
def _nfc(s):
    return unicodedata.normalize("NFC", str(s or ""))


def _chuan_ban_do(van):
    """-> (chuoi chu thuong, gop khoang trang, ban do chi so ve `van`)."""
    ra, bd, trong = [], [], True
    for i, c in enumerate(van):
        if c.isspace():
            if trong:
                continue
            ra.append(" ")
            bd.append(i)
            trong = True
        else:
            ra.append(c.lower())
            bd.append(i)
            trong = False
    while ra and ra[-1] == " ":
        ra.pop()
        bd.pop()
    return "".join(ra), bd


def _chuan_trich(t):
    t = re.sub(r"\s+", " ", _nfc(t).lower()).strip()
    return t.strip(" .,;:!?…\"'“”‘’")


def tim_trich(trich, van) -> Optional[Tuple[int, int]]:
    """Trich dan co la chuoi con NGUYEN VAN cua `van` khong (bo qua hoa thuong,
    khoang trang, dau cau hai dau) -> vi tri tren `van` (NFC), hoac None."""
    t = _chuan_trich(trich)
    if not t:
        return None
    s, bd = _chuan_ban_do(_nfc(van))
    k = s.find(t)
    if k < 0:
        return None
    return bd[k], bd[k + len(t) - 1] + 1


def _luot(hoi_thoai) -> Dict[int, Tuple[str, str]]:
    return {so: (str(vai or "").lower(), _nfc(van))
            for so, vai, van in thuc_the.tach_luot(hoi_thoai)}


# ----------------------------------------------------- tu chi nguoi
def tim_nguoi(doan: str) -> Dict[str, bool]:
    """Tu chi NGUOI trong mot doan. Cum dai chiem cho truoc: "me toi" la mot nguoi
    nha, khong phai "me" + "toi"; "be nha em" la benh nhan, khong phai "em";
    "toi nho lai" la loi ke ve viec noi, khong phai chu the."""
    t = chuan_hoa.chuan_hoa(doan)
    da = [False] * len(t)

    def tim(cac):
        co = False
        for c in sorted(cac, key=len, reverse=True):
            for m in re.finditer(rf"(?<!\w){re.escape(c)}(?!\w)", t):
                if any(da[m.start():m.end()]):
                    continue
                for k in range(m.start(), m.end()):
                    da[k] = True
                co = True
        return co

    tim(_TU_XUNG_KE)                       # giu cho, KHONG tinh
    ra = {}
    ra["ho_hang_so_huu"] = tim([f"{a} {b}" for a in _SO_HUU_GOC for b in _SO_HUU_DUOI])
    ra["bn_ro"] = tim(TU_BENH_NHAN_RO)
    ra["ho_hang"] = tim(TU_HO_HANG)
    ra["tu_xung_ro"] = tim(TU_TU_XUNG_RO)
    ra["mo"] = tim(TU_MO)
    return ra


def kiem_chu_the(la_bn: bool, vai: str, ng: Dict[str, bool]):
    """-> (muc, ma ly do) hoac (None, None). Xem docstring dau tep ve tu xung ho."""
    ho_hang = ng["ho_hang"] or ng["ho_hang_so_huu"]
    if la_vai_nhan_vien(vai):
        if la_bn or ho_hang:
            return None, None
        return CANH_BAO, "chu_the_chua_ro"
    if vai == "bệnh nhân":
        if la_bn:
            if ng["ho_hang_so_huu"] and not ng["tu_xung_ro"]:
                return CANH_BAO, "chu_the_nguoi_khac"
            return None, None
        return (None, None) if ho_hang else (CANH_BAO, "chu_the_chua_ro")
    # nguoi nha (hoac mot vai khong phai nhan vien y te, khong phai benh nhan)
    if la_bn:
        if ng["bn_ro"] or ng["mo"]:
            return None, None
        if ng["tu_xung_ro"]:
            return CHAN, "chu_the_nguoi_ke"
        if ho_hang:
            return CANH_BAO, "chu_the_nguoi_khac"
        return CANH_BAO, "chu_the_suy_tu_nguoi_noi"
    if ng["tu_xung_ro"] or ho_hang:
        return None, None
    if ng["bn_ro"]:
        return CHAN, "chu_the_benh_nhan"
    if ng["mo"]:
        return CANH_BAO, "chu_the_chua_ro"
    return CANH_BAO, "chu_the_suy_tu_nguoi_noi"


def _dau_cau(van, a):
    return max(van.rfind(c, 0, a) for c in ".?!…") + 1


def _nguoi_quanh(van, a, b):
    """Tu chi nguoi trong trich dan; khong co thi trong phan CUNG CAU dung truoc
    trich dan ("Da, chau con ho, so mui nua a" — trich "so mui nua a" khong co
    ai, nhung "chau" o dau cau)."""
    ng = tim_nguoi(van[a:b])
    if any(ng.values()):
        return ng
    return tim_nguoi(van[_dau_cau(van, a):a])


# ----------------------------------------------------- mot phat bieu
def _them(kq, muc, ma):
    if muc is None or ma is None:
        return
    ds = kq.chan if muc == CHAN else kq.canh_bao
    if ma not in ds:
        ds.append(ma)


def khoa_mot(p, cac_luot, bat_buoc_trich_dan=True) -> KetQua:
    kq = KetQua(id=p.id)
    for n in (p.bang_chung or []):
        if n not in cac_luot:
            _them(kq, CHAN, "luot_khong_ton_tai")
    hop_le = [n for n in (p.bang_chung or []) if n in cac_luot]

    # --- K1 nguon
    trich = list(getattr(p, "trich_dan", None) or [])
    if not trich:
        _them(kq, CHAN if bat_buoc_trich_dan else CANH_BAO, "khong_trich_dan")
    for k, t in enumerate(trich):
        so_dan = hop_le[k] if k < len(hop_le) else (hop_le[-1] if hop_le else None)
        thu_tu = ([so_dan] if so_dan is not None else []) + \
                 [s for s in cac_luot if s != so_dan]
        tim_thay = None
        for s in thu_tu:
            vt = tim_trich(t, cac_luot[s][1])
            if vt:
                tim_thay = (s, vt)
                break
        if tim_thay is None:
            _them(kq, CHAN, "trich_khong_co")
            continue
        if tim_thay[0] != so_dan:
            _them(kq, CANH_BAO, "trich_lech_luot")
        kq.doan.append((tim_thay[0], tim_thay[1][0], tim_thay[1][1]))

    # Van ban lam CAN CU: cac doan tim thay; khong co doan nao thi ca cac luot
    # duoc dan (de van co tin hieu cho K2-K5, du phat bieu da bi chan o K1).
    if kq.doan:
        doan_van = [(s, cac_luot[s][1], a, b) for s, a, b in kq.doan]
    else:
        doan_van = [(s, cac_luot[s][1], 0, len(cac_luot[s][1])) for s in hop_le]
    if not doan_van:
        return kq
    nguon = hop_le or sorted({s for s, _v, _a, _b in doan_van})

    can_cu = []
    for s, van, a, b in doan_van:
        can_cu.append(van[a:b])
        # Cau tra loi TAT ("Da, khong a"): noi dung nam o cau hoi dung truoc.
        if not _tu_noi_dung(chuan_hoa.chuan_hoa(van[a:b])) and (s - 1) in cac_luot \
                and la_vai_nhan_vien(cac_luot[s - 1][0]):
            can_cu.append(cac_luot[s - 1][1])
    can_cu_van = " ".join(can_cu)

    # --- K2 noi dung
    nd_chuan = chuan_hoa.chuan_hoa(p.noi_dung)
    tu_nd = set(_tu_noi_dung(nd_chuan))
    if tu_nd:
        co = tu_nd & set(_tu_noi_dung(chuan_hoa.chuan_hoa(can_cu_van)))
        chac = tu_nd & set(_tu_noi_dung(chuan_hoa.chuan_hoa(can_cu_van,
                                                              gom_can_hoi=False)))
        if not co:
            _them(kq, CANH_BAO, "noi_dung_khong_khop")
        elif not chac:
            _them(kq, CANH_BAO, "phuong_ngu_can_hoi")

    # --- K3 chu the: theo nguoi noi LUOT CUOI (giong `phat_bieu.tu_json`)
    so_cuoi = max(nguon)
    vai = cac_luot[so_cuoi][0]
    ng = {"ho_hang_so_huu": False, "bn_ro": False, "ho_hang": False,
          "tu_xung_ro": False, "mo": False}
    for s, van, a, b in doan_van:
        if s != so_cuoi:
            continue
        for k, v in _nguoi_quanh(van, a, b).items():
            ng[k] = ng[k] or v
    _them(kq, *kiem_chu_the(getattr(p, "chu_the_id", 0) == 0, vai, ng))

    # --- K4 muc khang dinh — tren chinh doan dan, chuan hoa CHI cac cho CHAC.
    # Nghia cua mot cho "can hoi" la loi GIAI THICH cua bang, khong phai loi nguoi
    # noi: "nong ham hap" -> "nong nhieu co the sot" mang chu "co the" vao, va
    # tang nay tung chan oan "sot" vi "rao don" (hieu chinh 11/09/2026, tap train).
    # Chan can bang chung RO; mot cach doc con phai hoi thi chua phai bang chung.
    thuc_te = getattr(p, "tinh_huong", "thực tế") == "thực tế"
    chac_chan = getattr(p, "do_chac_chan", "chắc chắn") == "chắc chắn"
    phu_dinh = bool(getattr(p, "phu_dinh", False))
    tu_nd_tho = set(re.findall(r"\w+", nd_chuan))
    for s, van, a, b in doan_van:
        cau = chuan_hoa.chuan_hoa(van[_dau_cau(van, a):b], gom_can_hoi=False)
        doan = chuan_hoa.chuan_hoa(van[a:b], gom_can_hoi=False)
        if thuc_te and DAU_DIEU_KIEN.search(cau):
            _them(kq, CHAN, "dieu_kien")
        if thuc_te and chac_chan and not phu_dinh:
            if DAU_NGHI.search(doan) or DAU_THEO_DOI.search(doan):
                _them(kq, CHAN, "vuot_muc_nghi")
            elif DAU_CHUA_GHI_NHAN.search(doan):
                _them(kq, CHAN, "vuot_muc_chua_ghi_nhan")
            elif any(m.group(1).split()[0] not in tu_nd_tho
                     for m in DAU_PHU_DINH.finditer(doan)):
                # Tu phu dinh la MOT PHAN noi dung ("khong phu", "khong phat hien
                # bat thuong") thi khong phai dau hieu gi.
                _them(kq, CANH_BAO, "co_tu_phu_dinh")
        if phu_dinh and chac_chan and DAU_CHUA_GHI_NHAN.search(doan):
            _them(kq, CANH_BAO, "phu_dinh_vuot_muc")

    # --- K5 moc thoi gian: phai thay trong cac LUOT duoc dan
    moc = getattr(p, "moc_thoi_gian", None)
    if moc:
        tu_moc = set(_tu_noi_dung(chuan_hoa.chuan_hoa(moc)))
        luot_van = " ".join(cac_luot[s][1] for s in nguon)
        if tu_moc and not tu_moc <= set(_tu_noi_dung(chuan_hoa.chuan_hoa(luot_van))):
            _them(kq, CANH_BAO, "moc_khong_thay")

    # --- K6 chi tiet thuoc (15/09/2026): moi chi tiet phai CO trong cac luot duoc dan
    #
    # So NGUYEN CHUOI (chu thuong, gop khoang trang), khong so tap tu: "5 mg" va
    # "50 mg" chung tu "mg", so tu thi lieu sai van qua.
    #
    # LIEU KHONG THAY THI CHAN, khac voi moc thoi gian (K5 chi canh bao). Mot con so
    # lieu khong co trong chinh cac luot ma ban ghi dan toi la con so khong ai noi —
    # cung loai voi trich dan khong co trong hoi thoai, va ghi sai lieu la ke nham
    # thuoc. So lan dung, luc bat dau, luc ngung va duong dung chi canh bao: nguoi
    # noi hay dien dat chung bang nhieu cach ("sang mot vien" = "ngay mot lan").
    t = getattr(p, "thuoc", None)
    if t:
        van_dan = _chuan_trich(" ".join(cac_luot[s][1] for s in nguon))
        if t.get("lieu") and _chuan_trich(t["lieu"]) not in van_dan:
            _them(kq, CHAN, "lieu_khong_thay")
        for khoa in ("so_lan", "bat_dau", "ngung"):
            if t.get(khoa) and _chuan_trich(t[khoa]) not in van_dan:
                _them(kq, CANH_BAO, "chi_tiet_thuoc_khong_thay")
        duong = t.get("duong_dung")
        if duong and not re.search(rf"(?<!\w){re.escape(duong)}(?!\w)", van_dan):
            _them(kq, CANH_BAO, "duong_dung_khong_thay")

    if getattr(p, "trang_thai", "còn hiệu lực") == "chưa giải quyết":
        _them(kq, CANH_BAO, "mau_thuan")
    return kq


# ----------------------------------------------------- kiem day du
def doan_chua_ghi(ket_qua: List[KetQua], ps, cac_luot) -> List[dict]:
    """Doan hoi thoai co noi dung lam sang ma KHONG phat bieu nao dan toi.

    Nua con lai cua ban de xuat: `kiem_day_du` doi chieu ban nhap voi bang phat
    bieu, nen mo hinh bo sot tu dau thi no van bao "day du". O day doi chieu voi
    HOI THOAI. Bo qua cau hoi (khong phai thong tin) va doan thu tuc.

    Mot doan duoc coi la DA GHI neu chong len mot trich dan tim thay, hoac chung
    it nhat mot tu noi dung voi mot phat bieu dan toi CUNG luot — "uong duoc it
    hom roi ngung, ngung hai tuan roi" la mot thong tin tach hai doan.
    """
    phu, tu_theo_luot = {}, {}
    for kq, p in zip(ket_qua, ps):
        luot_cua = {s for s, _a, _b in kq.doan} | \
                   {n for n in (p.bang_chung or []) if n in cac_luot}
        tu = set(_tu_noi_dung(chuan_hoa.chuan_hoa(p.noi_dung)))
        for s in luot_cua:
            tu_theo_luot.setdefault(s, set()).update(tu)
        for s, a, b in kq.doan:
            phu.setdefault(s, []).append((a, b))
    ra = []
    for so, (vai, van) in sorted(cac_luot.items()):
        for a, b in cac_doan(van):
            if dau_ket(van, (a, b)) == "?":
                continue
            doan = van[a:b]
            if THU_TUC.search(doan.lower()):
                continue
            tu = set(_tu_noi_dung(chuan_hoa.chuan_hoa(doan)))
            if not tu:
                continue
            if any(x < b and a < y for x, y in phu.get(so, ())):
                continue
            if tu & tu_theo_luot.get(so, set()):
                continue
            ra.append({"luot": so, "vai": vai, "doan": doan,
                       "bat_dau": a, "ket_thuc": b})
    return ra


def khoa_ca(ps, hoi_thoai, bat_buoc_trich_dan=True) -> dict:
    """-> {"ket_qua": [KetQua], "doan_chua_ghi": [...]} cho MOT ca."""
    cac_luot = _luot(hoi_thoai)
    kq = [khoa_mot(p, cac_luot, bat_buoc_trich_dan) for p in ps]
    return {"ket_qua": kq, "doan_chua_ghi": doan_chua_ghi(kq, ps, cac_luot)}


def ly_do_chan(ket_qua: List[KetQua]) -> Dict[int, str]:
    """{id phat bieu bi chan: ly do} — de `sinh_benh_an.sinh` dua xuong CAN XAC
    NHAN kem dung ly do cua khoa."""
    return {k.id: "; ".join(LY_DO[m] for m in k.chan)
            for k in ket_qua if k.chan}
