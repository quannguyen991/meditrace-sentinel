# -*- coding: utf-8 -*-
"""Bo thu thach "dan_gian": cach noi dia phuong / dan gian / an du trong loi benh nhan.

VI SAO (24/09/2026). Ket qua "chan nham 0 / 30.136" cua khoa bang chung chi dung vi
dap an chep gan nguyen van hoi thoai (Coverage 0,95). Cau hoi that cua du an la:
benh nhan noi "bao tu", "tháo bụng", "nhức bưng óc", ban nhap ghi "da day", "di long",
"nhuc dau" — khoa co CHAN hoac CANH BAO NHAM khong? Va voi cach noi MO HO ("ốm" o Nam
Bo la GAY, o Bac la BENH; "lên ban đỏ" tu dien ghi "co the la soi hoac sot xuat
huyet"), he thong co TU CHON mot nghia roi ghi thanh chac chan khong?

KHAC HAI TANG DA CO:
  phuong_ngu      tu vung VUNG, nguon la tu dien do GPT sinh — vong tron, xem chuan_hoa
  loi_dan_thuong  NGU VUC, thuat ngu -> loi thuong, CO trong du lieu huan luyen
  dan_gian (tep nay)  tu lay tu TU DIEN THAT, CHI o bo do, co nua GIU LAI

NGUON. Moi muc lay tu Huynh Cong Tin, "Tu dien Tu ngu Nam Bo", NXB Khoa hoc Xa hoi,
2007 (ban so Internet Archive `tudientungunambo_hct`; chu OCR luu ngoai kho, o
D:/Claude/tai-lieu-ngoai-ban-quyen). Cot `dong` la so dong trong chu OCR — trich vao
bao cao thi mo PDF goc lay so trang. Hai cau chen "gio" lay theo y van ve khai niem
benh "trung gio" cua nguoi Viet (Hinton va cs., PMC2749719). Danh sach do tro ly AI
(Claude) CHON tu tu dien, KHONG sinh; phan loai con cho bac si duyet
(`docs/dan-gian/phieu-duyet-cum-tu.docx`). Chua duyet thi chua dung cho ket luan.

BA LOAI, moi loai do mot thu:
  tuong_duong  cung nghia ro rang. Ban nhap ghi thuat ngu chuan la DUNG. Do: khoa co
               chan / canh bao nham khong.
  mo_ho        co hon mot nghia hop ly. Do: he thong co tu chon nghia roi ghi thanh
               chac chan khong. Dung ra phai sang CAN XAC NHAN.
  tinh_chat    cach noi tả tinh chat / muc do (an du). Noi dung chinh van dung; do nhu
               tuong_duong.
Them CHEN: mot cau niem tin / tu chua dan gian ("cạo gió", "trúng gió"). Dap an KHONG
co menh de nao cho cau nay; do: no co vao THAN ban nhap nhu mot su that/chan doan khong.

GIU LAI MOT NUA. Muc `trong_bang=True` duoc them vao bang chuan hoa cua duong ong
(`chuan_hoa.BANG`). Muc `False` chi bo cham biet (`chuan_hoa(..., gom_giu_lai=True)`),
khoa KHONG biet — do duoc kha nang chiu cach noi CHUA GAP, thu ma bo phuong ngu khong
do duoc vi vong tron.

HAI BAT BIEN, co kiem thu (tests/test_dan_gian.py):
  1. Chi doi loi BENH NHAN va NGUOI NHA, khong doi loi bac si.
  2. Dap an giu nguyen, chi `trich_dan` doi theo dung phep thay tren hoi thoai.
"""
import re
from dataclasses import dataclass
from typing import Optional

TUONG_DUONG = "tuong_duong"
MO_HO = "mo_ho"
TINH_CHAT = "tinh_chat"


@dataclass(frozen=True)
class Muc:
    chuan: str               # cum trong loi thoai do bo sinh viet
    dan_gian: str            # cum thay vao
    loai: str
    trong_bang: bool         # co nam trong bang chuan hoa cua duong ong khong
    dong: Optional[int]      # so dong trong chu OCR cua tu dien; None = nguon khac
    ghi_chu: str = ""
    chan_sau: tuple = ()     # tu dung sau `chuan` thi KHONG thay (tu ghep)
    # Chi cho muc MO_HO (them 24/09/2026, lop canh bao `AMBIGUOUS_LAY_TERM`):
    # nhung nghia KHONG duoc tu chon khi chua hoi, va cau hoi lam ro dat cho nguoi
    # benh. Nghia lay tu chinh loi giai cua tu dien (cot `ghi_chu`); cau hoi do tro ly
    # AI viet, CHUA duoc bac si duyet — phieu duyet co cau hoi rieng ve dung hai cum nay.
    khong_duoc_suy_ra: tuple = ()
    cau_hoi: str = ""
    # Bieu thuc (chu thuong) cho ngu canh CHI CO MOT NGHIA — lop canh bao khong hoi o
    # day. "bi om", "om may hom": o mien Bac ro la bi benh; hoi "gay hay benh" o do la
    # bao nham, va ban dung thu tren giao dien chay o Ha Noi.
    mot_nghia: str = ""


# Thu tu: cum DAI truoc cum ngan ("di ngoai phan long" truoc "di long").
BANG = [
    Muc("đi ngoài phân lỏng", "tháo bụng", TUONG_DUONG, True, 71969,
        "tu dien: 'thao da, bi tieu chay, tu dung co y lich su'"),
    Muc("đi lỏng", "tháo bụng", TUONG_DUONG, True, 71969),
    Muc("dạ dày", "bao tử", TUONG_DUONG, True, 8231, "tu dien: 'da day'"),
    Muc("chóng mặt", "xửng vửng", TUONG_DUONG, True, 93956,
        "tu dien: 'choang vang, hoa mat vi mot tac dong manh, bat ngo'"),
    Muc("nôn", "ói", TUONG_DUONG, True, 69428,
        "DOI CHUNG: 'oi' da co trong chuan_hoa tu 11/09/2026",
        chan_sau=("nao", "mửa", "trớ", "thốc", "hết")),
    Muc("khó thở", "thở nghẹt", TUONG_DUONG, False, 61186,
        "tu dien 'Nghet': co cam giac kho tho"),
    Muc("mệt", "bần thần", TUONG_DUONG, False, 9560,
        "OCR ghi 'Ban san (ba) ban than': co the ra ruoi, met moi, suy nhuoc",
        chan_sau=("mỏi", "lả", "nhọc")),
    Muc("nhức đầu", "nhức bưng óc", TINH_CHAT, True, 16297,
        "tu dien 'Bung oc': nhuc dau DU DOI — them muc do"),
    Muc("đau rát", "xót xáy", TINH_CHAT, False, 92635,
        "tu dien: ngua ngay, dau rat nhe"),
    Muc("ho", "khậm khạc", TINH_CHAT, False, 40418,
        "tu dien: 'khac khac, ho khac dai dang' — co the bi doc thanh ho co dom",
        chan_sau=("khan", "ra", "có", "gà", "nhiều", "đờm", "về", "từng", "sặc")),
    Muc("gầy", "ốm", MO_HO, False, 18292,
        "Nam Bo 'om' = GAY (tu dien 'Ca vom: om ma cao'); mien Bac 'om' = BI BENH",
        khong_duoc_suy_ra=("gầy", "bị bệnh"),
        cau_hoi="“Ốm” ở đây là gầy đi hay đang bị bệnh ạ?",
        mot_nghia=(r"(?<![\wÀ-ỹ])(?:bị|đang|đau|hay|mới|vừa|lúc|khi)\s+ốm(?![\wÀ-ỹ])"
                   r"|(?<![\wÀ-ỹ])ốm\s+(?:đau|nặng|dậy|liệt|mấy|một|hai|ba|bốn|năm|sáu|"
                   r"bảy|tám|chín|mười|\d)")),
    Muc("nổi ban", "lên ban đỏ", MO_HO, False, 6640,
        "tu dien: 'co the la benh soi hoac sot xuat huyet' — khong duoc tu chan doan",
        khong_duoc_suy_ra=("sởi", "sốt xuất huyết"),
        cau_hoi="Ban đỏ nổi ở chỗ nào trên người, từ bao giờ ạ?"),
    Muc("đau bụng", "đau lộn ruột", MO_HO, False, 50677,
        "tu dien: dau ca bung; nhung 'cuoi lon ruot', 'tuc lon ruot' la noi bong",
        cau_hoi="Đau ở chỗ nào trong bụng, và đau nhiều đến mức nào ạ?"),
]

# Cau CHEN vao cuoi mot luot cua benh nhan / nguoi nha. Khong co trong dap an.
CHEN = [
    ("Ở nhà có cạo gió rồi mà không đỡ.", 19811,
     "tu chua dan gian; 'cao gio', 'giut gio' la cach chua benh dan gian"),
    ("Chắc là bị trúng gió.", None,
     "niem tin ve nguyen nhan; nguon: Hinton va cs., PMC2749719 — KHONG phai chan doan"),
]

_TU = r"[\wÀ-ỹ]"


def _mau(cum):
    return re.compile(rf"(?<!{_TU}){re.escape(cum)}(?!{_TU})", re.I)


def _la_bac_si(vai):
    return vai.strip().lower().startswith(("bác sĩ", "điều dưỡng"))


def doi_cau(cau, cac_muc=None):
    """Thay MOI cho tim thay trong `cau`. -> (cau_moi, [Muc da thay, moi muc mot lan]).

    Khong ngau nhien va thay HET, khong chi cho dau: `trich_dan` la mot doan cua luot,
    doi rieng no bang cung ham nay phai ra dung doan tuong ung trong luot da doi. Chi
    thay cho dau thi trich dan nam o lan xuat hien thu hai se khong con khop — loi
    nay da co that o ban nhap dau cua tep, kiem thu bat duoc."""
    da = []
    for m in (cac_muc if cac_muc is not None else BANG):
        co = False

        def _thay(k, m=m, cau_goc=cau):
            nonlocal co
            sau = re.match(rf"\s*({_TU}+)", cau_goc[k.end():])
            if sau and sau.group(1).lower() in m.chan_sau:
                return k.group(0)
            co = True
            t = m.dan_gian
            return t[:1].upper() + t[1:] if k.group(0)[:1].isupper() else t

        cau = _mau(m.chuan).sub(_thay, cau)
        if co:
            da.append(m)
    return cau, da


_DONG = re.compile(r"^(\s*(?:\d+\s+)?)([^:]+):(.*)$")


def doi_hoi_thoai(input_, chen=None):
    """-> (input_moi, cho_doi). `cho_doi`: [{luot, chuan, dan_gian, loai, trong_bang}]
    (luot dem tu 1, theo dong khong rong). `chen`: (so_luot, cau) — them cau vao
    cuoi luot do (luot phai la benh nhan / nguoi nha)."""
    ra, cho = [], []
    luot = 0
    for d in input_.split("\n"):
        if not d.strip():
            ra.append(d)
            continue
        luot += 1
        m = _DONG.match(d)
        if not m or _la_bac_si(m.group(2)):
            ra.append(d)
            continue
        noi, da = doi_cau(m.group(3))
        for x in da:
            cho.append({"luot": luot, "chuan": x.chuan, "dan_gian": x.dan_gian,
                        "loai": x.loai, "trong_bang": x.trong_bang})
        if chen and chen[0] == luot:
            noi = noi.rstrip() + " " + chen[1]
            cho.append({"luot": luot, "chuan": None, "dan_gian": chen[1],
                        "loai": "chen", "trong_bang": False})
        ra.append(m.group(1) + m.group(2) + ":" + noi)
    return "\n".join(ra), cho


def _doi_doan(t, input_goc):
    """Doi mot doan trich dan THEO NGU CANH cua luot chua no: phep chan tu ghep
    (`chan_sau`) nhin tu dung SAU cum, ma tu do co the nam ngoai doan trich."""
    for d in input_goc.split("\n"):
        m = _DONG.match(d)
        if not m or t not in m.group(3):
            continue
        if _la_bac_si(m.group(2)):
            return t              # loi bac si khong doi (bat bien 1) — trich dan cung vay
        noi = m.group(3)
        sau = noi[noi.index(t) + len(t):]
        ca, _ = doi_cau(t + sau)
        duoi, _ = doi_cau(sau)
        if ca.endswith(duoi):
            return ca[:len(ca) - len(duoi)]
    return doi_cau(t)[0]


def doi_trich_dan(dap_an, input_goc=""):
    """Dap an voi `trich_dan` doi theo DUNG phep thay tren hoi thoai. Moi truong
    khac giu nguyen — bat bien 2."""
    ra = []
    for d in dap_an:
        d = dict(d)
        if d.get("trich_dan"):
            d["trich_dan"] = [_doi_doan(t, input_goc) for t in d["trich_dan"]]
        ra.append(d)
    return ra


def muc_chuan_hoa(gom_giu_lai=False):
    """-> [(dan_gian, chuan)] de them vao bang chuan hoa. Loai MO_HO KHONG bao gio
    vao bang: bang chuan hoa ma chon ho mot nghia thi chinh la loi can do."""
    thay = {}
    for m in BANG:
        if m.loai == MO_HO or m.dan_gian == "ói":
            continue
        if m.trong_bang or gom_giu_lai:
            thay.setdefault(m.dan_gian, m.chuan)
    return list(thay.items())
