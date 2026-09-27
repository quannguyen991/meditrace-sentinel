# -*- coding: utf-8 -*-
"""Tang 1 — HIEU phuong ngu nhung GIU NGUYEN VAN.

Moi doan hoi thoai co HAI ban: nguyen van (de trich dan, de bac si doc) va ban
chuan hoa (de doi chieu noi dung). Moi cho doi mang MUC TIN:

  chac     trong ngu canh kham benh tu chi co MOT nghia: "hom ray", "xiu", "oi"
  can hoi  tu co nghia thu hai thuong gap, hoac muc tu dien dang ngo. Ban chuan
           hoa VAN ghi nghia hay gap nhat de doi chieu, nhung gan co — tang khoa
           bang chung ha no xuong canh bao, tang hoi lai (`hoi_lai`) hoi lai.

KHONG thay ca cau dan da thanh thuat ngu y khoa. "Nong ham hap" thanh "nong
nhieu co the sot", muc CAN HOI — chu khong thanh "sot": nguoi noi chua do nhiet.

BON TU NGUY HIEM NHAT, va vi sao khong doi chung khi dung mot minh:

  "te"    = kia (mien Trung), NHUNG "te chan", "te bi" la trieu chung. Chi doi
            trong "hom te", "ben te", "cho te".
  "chi"   = gi, NHUNG "chi duoi" la chi cua co the. Chi doi trong "co chi",
            "lam chi", "bi chi", "cai chi".
  "rang"  = sao, NHUNG "moc rang", "dau rang" la cai rang.
  "ba"    = ba ay (mien Nam), NHUNG "ba vai" la mot bo phan co the.

NGUON — phai doc truoc khi dung. Bang duoi day lay tu tu dien phuong ngu nguoi
dung cung cap (40 muc), ma nguoi dung xac nhan ngay 11/09/2026 la do GPT SINH;
mot so nguon trich trong do la bai blog thuong mai. Moi muc phai duoc doi chieu
voi tu dien that (Huynh Cong Tin, "Tu dien tu ngu Nam Bo", 2007) hoac nguoi dia
phuong truoc khi dung cho ket luan. Muc "me" dac biet: tu dien ghi "ba/me", o
Hue "me" thuong la BA — nham hai nguoi nay la dung loi quy gan cua du an, nen
de CAN HOI.

VONG TRON PHAI NOI RO. Bang thay cua bo sinh (`phuong_ngu.THAY_DUOC`) lay tu
cung nguon, nen tren du lieu tu sinh tang nay biet truoc MOI tu phuong ngu. Phep
thu cap phuong ngu (`thach_thuc`) vi the do "he thong co ap dung dung bang cua
no", khong do "he thong chiu duoc phuong ngu la". Phan do duoc that la MO HINH:
tu 11/09/2026 khuon train khong co tu nao tu bang GPT
(`sinh_hoi_thoai_viet.PHUONG_NGU_TRONG_TRAIN`), nen mo hinh gap chung lan dau o
tap danh gia.
"""
import re
from dataclasses import dataclass
from typing import List, Optional

from src import dan_gian

CHAC = "chắc"
CAN_HOI = "cần hỏi"


@dataclass(frozen=True)
class ChoDoi:
    bat_dau: int
    ket_thuc: int
    goc: str                  # chu nguyen van
    nghia: str                # "" = khong doi
    muc_tin: Optional[str]    # CHAC | CAN_HOI | None (giu cho, khong doi, khong bao)
    ly_do: str = ""


def _tu(cum):
    return rf"(?<!\w){cum}(?!\w)"


# (bieu thuc tren chu THUONG, nhom duoc doi, nghia, muc tin, ly do).
# Xet theo THU TU; cho da bi mot muc truoc chiem thi muc sau bo qua — nen cum
# DAI va cac muc "giu cho" dung truoc tu don.
BANG = [
    # --- giu cho: nghia co the, KHONG phai phuong ngu
    (_tu("bả vai"), 0, "", None, ""),
    (_tu("chi (dưới|trên)"), 0, "", None, ""),
    (r"(?<!\w)(mọc|đau|sâu|nhổ|cái|chiếc|hàm|chải|đánh|niềng) răng(?!\w)", 0,
     "", None, ""),
    (r"(?<!\w)răng (sữa|hàm|khôn|miệng|cửa)(?!\w)", 0, "", None, ""),
    (r"(?<!\w)(chụp|tấm|bức|hình) ảnh(?!\w)", 0, "", None, ""),
    # --- cum nhieu tu, mot nghia
    (_tu("có chi mô"), 0, "không có gì", CHAC, ""),
    (_tu("mần răng"), 0, "làm sao", CHAC, ""),
    (_tu("làm răng"), 0, "làm sao", CHAC, ""),
    (_tu("hổm rày"), 0, "dạo gần đây", CHAC, ""),
    (_tu("bữa hổm"), 0, "hôm trước", CHAC, ""),
    (_tu("bữa giờ"), 0, "dạo này", CHAC, ""),
    (_tu("bữa chừ"), 0, "dạo này", CHAC, ""),
    (_tu("hôm tê"), 0, "hôm kia", CHAC, ""),
    (_tu("khi mô"), 0, "khi nào", CHAC, ""),
    (_tu("con nít"), 0, "trẻ em", CHAC, ""),
    (_tu("đi cầu"), 0, "đi đại tiện", CHAC, ""),
    (_tu("lừ đừ"), 0, "mệt mỏi", CHAC, ""),
    (_tu("dữ lắm"), 0, "rất nhiều", CHAC, ""),
    (_tu("nóng hầm hập"), 0, "nóng nhiều có thể sốt", CAN_HOI,
     "người nói chưa đo nhiệt độ — không tự đổi thành sốt"),
    (_tu("tới công chuyện"), 0, "trở nặng", CAN_HOI,
     "khẩu ngữ, phải hỏi triệu chứng cụ thể"),
    (_tu("quay quay"), 0, "chóng mặt", CAN_HOI, "mục từ điển đáng ngờ"),
    # --- tu don CHI doi trong ngu canh chan
    (r"(?<!\w)(?:bên|chỗ|cái|đằng) (tê)(?!\w)", 1, "kia", CHAC, ""),
    (r"(?<!\w)(?:có|làm|bị|cái) (chi)(?!\w)", 1, "gì", CHAC, ""),
    (r"(?<!\w)(?:cái|bữa|hôm|chỗ|bên|ngày) (ni)(?!\w)", 1, "này", CHAC, ""),
    (r"(?<!\w)(?:đi|ở|chỗ|bên|đằng) (mô)(?!\w)", 1, "đâu", CHAC, ""),
    (r"(?<!\w)(?:làm|mần|vì|tại) (răng)(?!\w)", 1, "sao", CHAC, ""),
    (r"(?<!\w)(răng)(?= (?:rứa|vậy|không|mà|hỉ)(?!\w))", 1, "sao", CHAC, ""),
    # "hong": het cau / dung truoc tieu tu -> khong. Sau tu chi bo phan co the
    # thi MO HO ("dau hong" = dau vung hong hay "dau khong?") — tu dien ghi dung
    # truong hop nay la cai bay khi ban ghi thieu dau cau.
    (r"(?<!\w)(hông)(?=\s*(?:[,.?!…]|$|có\b|biết\b|đó\b|nè\b|à\b|ha\b))", 1,
     "không", CHAC, ""),
    # MO HO THAT: khong ghi nghia nao vao ban chuan hoa — ghi "khong" thi "dau
    # hong ben phai" thanh "dau khong ben phai", tuc chon ho nguoi noi mot nghia.
    (r"(?<!\w)(?:đau|mỏi|nhức|bên|vùng|sưng|tê) (hông)(?!\w)", 1, "",
     CAN_HOI, "'hông' là vùng hông hay 'không'?"),
    (_tu("hông"), 0, "không", CHAC, ""),
    (_tu("mệ"), 0, "bà", CAN_HOI,
     "từ điển ghi 'bà/mẹ'; ở Huế 'mệ' thường là bà — cần người Huế xác nhận"),
    (_tu("ảnh"), 0, "anh ấy", CAN_HOI, "'ảnh' là anh ấy hay tấm ảnh?"),
    # --- tu don, mot nghia
    (_tu("xỉu"), 0, "ngất", CHAC, ""),
    (_tu("ói"), 0, "nôn", CHAC, ""),
    (_tu("mửa"), 0, "nôn", CHAC, ""),
    (_tu("chừ"), 0, "bây giờ", CHAC, ""),
    (_tu("rứa"), 0, "vậy", CHAC, ""),
    (_tu("hổng"), 0, "không", CHAC, ""),
    (_tu("nỏ"), 0, "không", CHAC, ""),
    (_tu("chớ"), 0, "chứ", CHAC, ""),
    (_tu("ổng"), 0, "ông ấy", CHAC, ""),
    (_tu("bả"), 0, "bà ấy", CHAC, ""),
    (_tu("eng"), 0, "anh", CHAC, ""),
    (_tu("hỉ"), 0, "nhỉ", CHAC, ""),
    (_tu("nớ"), 0, "đó", CHAC, ""),
    (_tu("mần"), 0, "làm", CHAC, ""),
]
_BANG = [(re.compile(bt), nhom, nghia, muc, ly) for bt, nhom, nghia, muc, ly in BANG]

# Cach noi dan gian lay tu tu dien that (24/09/2026, xem `dan_gian`). Nua `trong_bang`
# duong ong biet; nua GIU LAI chi bo cham biet (`gom_giu_lai=True`) — de do kha nang
# chiu cach noi chua gap. Loai MO HO khong bao gio vao day. Dat SAU bang cu: cac cum
# nay khong xuat hien trong du lieu the he 8 (co kiem thu), nen khong doi so cu nao.
_DAN_GIAN_TRONG = [(re.compile(_tu(re.escape(dg))), 0, chuan, CHAC, "dan gian")
                   for dg, chuan in dan_gian.muc_chuan_hoa(False)]
_DAN_GIAN_GIU_LAI = [(re.compile(_tu(re.escape(dg))), 0, chuan, CHAC, "dan gian, giu lai")
                     for dg, chuan in dan_gian.muc_chuan_hoa(True)
                     if (dg, chuan) not in dan_gian.muc_chuan_hoa(False)]


def phan_tich(van: str, gom_giu_lai: bool = False) -> List[ChoDoi]:
    """-> cac cho doi / gan co tren NGUYEN VAN, xep theo vi tri. Khong chong nhau.

    `gom_giu_lai=True` CHI cho bo cham — duong ong (khoa bang chung, canh bao, hoi
    lai) luon goi mac dinh, nen khong biet cac cum dan gian giu lai."""
    van = van or ""
    thap = van.lower()
    if len(thap) != len(van):          # an toan: chuoi la khong doi duoc do dai
        return []
    da = [False] * len(van)
    ra = []
    bang = _BANG + _DAN_GIAN_TRONG + (_DAN_GIAN_GIU_LAI if gom_giu_lai else [])
    for mau, nhom, nghia, muc, ly in bang:
        for m in mau.finditer(thap):
            a, b = m.span(nhom)
            if a < 0 or any(da[a:b]):
                continue
            for k in range(a, b):
                da[k] = True
            ra.append(ChoDoi(a, b, van[a:b], nghia, muc, ly))
    return sorted(ra, key=lambda c: c.bat_dau)


def chuan_hoa(van: str, gom_can_hoi: bool = True, gom_giu_lai: bool = False) -> str:
    """-> ban CHU THUONG da thay tu phuong ngu bang nghia chuan.

    `gom_can_hoi=False`: chi thay cac cho CHAC — de biet mot phep doi chieu co
    dung duoc khong khi bo het cho mo ho.
    """
    thap = (van or "").lower()
    for c in sorted(phan_tich(van, gom_giu_lai), key=lambda c: c.bat_dau, reverse=True):
        if not c.nghia or c.muc_tin is None:
            continue
        if c.muc_tin == CAN_HOI and not gom_can_hoi:
            continue
        thap = thap[:c.bat_dau] + c.nghia + thap[c.ket_thuc:]
    return thap


def can_hoi(van: str) -> List[ChoDoi]:
    """Cac cho MO HO trong doan — ung vien cho tang hoi lai."""
    return [c for c in phan_tich(van) if c.muc_tin == CAN_HOI]
