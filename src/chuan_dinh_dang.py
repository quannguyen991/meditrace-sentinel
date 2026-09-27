# -*- coding: utf-8 -*-
"""Chuan hoa DINH DANG tieu de truoc khi cham, ap dung NHU NHAU cho moi nhanh.

VI SAO CAN — do duoc 11/09/2026, va no lam mot con so cu mat nghia.

`section_f1` cua nhanh `A nen` la **0,0000 dung bang khong** tren ca 60 ca. Khong
phai thap — KHONG. Khong mot ten muc nao khop, tren ca 60 ban nhap.

Nguyen nhan khong phai noi dung. Mo hinh sinh thang viet tieu de kieu Markdown:

    **Benh su:**                 <- A nen viet the nay
    BENH SU HIEN TAI             <- ban tham chieu viet the nay

`cham_diem.cac_muc` nhan mot dong la tieu de khi no VIET HOA TOAN BO. Dong
`**Benh su:**` co chu thuong nen khong duoc tinh, va the la mau so cua
`section_f1` trong rong.

HE QUA NANG HON MOT CON SO SAI: diem gop la `0,6 x ROUGE + 0,4 x SectionF1`, nen
nhanh A bi **chan tran o 0,6** chi vi cach viet tieu de. Mot phan ba thuoc do
khong bao gio mo cho no.

DAY LA LAN THU BA trong hai ngay mot thuoc do do thu khac voi thu no khai:

    ROUGE         mu truoc lo~i quy gan        (0,9799 so voi 0,9661)
    f1_quy_gan    bi tang de chi phoi          (xep regex tren duong ong)
    section_f1    do CACH VIET TIEU DE         (0 tuyet doi cho A)

PHEP THU CONG BANG — va day la cho quan trong nhat cua tep nay.

    Chuan hoa phai la PHEP DONG NHAT tren ban nhap da dung ten muc chuan.

Neu no doi ca nhanh `B`, `C`, `D` thi no khong con la "bo tat dinh dang" ma thanh
"dieu chinh de mot nhanh trong hon". Do duoc, va da do:

    A_nen   0,0000 -> 0,1477   (+0,1477)
    B       0,7339 -> 0,7339   ( 0,0000)
    C       0,7285 -> 0,7285   ( 0,0000)
    D       0,6366 -> 0,6366   ( 0,0000)

Chi mot nhanh doi, va do la nhanh duy nhat khong dung ten muc chuan.

VA PHAI NOI RO: sau khi bo tat dinh dang, A van kem xa B (0,15 so voi 0,73). Nen
ket luan "cau truc muc cua A kem hon nhieu" VAN DUNG — chi la do lon bi thoi, va
con so "dung bang khong" thi vo nghia.

GIOI HAN: bang dong nghia duoi day la mot phan doan cua toi, chua co bac si xem.
No chi anh xa cac cum RAT gan ten muc chuan. Moi lan them mot dong nghia la mot
lan noi long phep do, nen bang nay phai duoc doc cung so lieu chu khong am tham.
"""
import re
import unicodedata

from src import sinh_benh_an, sinh_hoi_thoai_viet

# HOP cua hai von tu, va cho nay da la mot lo~ that.
#
# `sinh_benh_an.THU_TU_MUC` (khau sinh cua duong ong) va
# `sinh_hoi_thoai_viet.MUC` (ban nhap tham chieu) KHONG trung nhau:
#
#     chi o duong ong : CAN XAC NHAN, KHAM HE THONG CAC CO QUAN, SINH HIEU,
#                       TIEM CHUNG, TIEN SU PHAU THUAT, TIEN SU XA HOI
#     chi o tham chieu: KHAM LAM SANG
#
# Ban tham chieu co `KHAM LAM SANG` o 60/60 ca; ban nhap cua nhanh B co 0.
# Duong ong KHONG THE sinh ra ten muc do vi ten do khong nam trong bang cua
# no. Day khong phai viec cua tep nay de chua, nhung tep nay phai biet CA HAI
# von tu, neu khong thi no se 'chuan hoa' mot ten dung thanh mot ten khac.
MUC_CHUAN = tuple(dict.fromkeys(
    tuple(sinh_benh_an.THU_TU_MUC) + tuple(sinh_hoi_thoai_viet.MUC)))

# Cum -> ten muc chuan. Khoa da bo dau, ha chu thuong, bo dau cau.
#
# CHI nhung cum gan ten chuan. Khong them cum chi "co nghia tuong tu": moi dong
# o day la mot lan noi long phep do.
DONG_NGHIA = {
    "benh su": "BỆNH SỬ HIỆN TẠI",
    "benh su hien tai": "BỆNH SỬ HIỆN TẠI",
    "qua trinh benh": "BỆNH SỬ HIỆN TẠI",
    "ly do kham": "LÝ DO KHÁM BỆNH",
    "ly do kham benh": "LÝ DO KHÁM BỆNH",
    "ly do vao vien": "LÝ DO KHÁM BỆNH",
    "tien su": "TIỀN SỬ BỆNH",
    "tien su benh": "TIỀN SỬ BỆNH",
    "tien su ban than": "TIỀN SỬ BỆNH",
    "tien su gia dinh": "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI",
    "tien su gia dinh va xa hoi": "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI",
    "thuoc dang dung": "THUỐC ĐANG DÙNG",
    "thuoc da dung": "THUỐC ĐANG DÙNG",
    "di ung": "DỊ ỨNG",
    "tien su di ung": "DỊ ỨNG",
    "kham lam sang": "KHÁM LÂM SÀNG",
    "kham": "KHÁM LÂM SÀNG",
    # Ten CU cua muc kham trong `sinh_benh_an`, doi ngay 11/09/2026. Giu o day
    # lam bien the de cac tep ket qua sinh truoc khi doi ten van doc duoc.
    "kham he thong cac co quan": "KHÁM LÂM SÀNG",
    "chan doan": "CHẨN ĐOÁN",
    "chan doan so bo": "CHẨN ĐOÁN",
    "ke hoach": "KẾ HOẠCH ĐIỀU TRỊ",
    "ke hoach dieu tri": "KẾ HOẠCH ĐIỀU TRỊ",
    "huong xu tri": "KẾ HOẠCH ĐIỀU TRỊ",
    "can xac nhan": sinh_benh_an.MUC_PHU,
}

# Dai nhat cua mot ten muc chuan, cong mot khoang. Dong dai hon the khong phai
# tieu de du no co khop bang dong nghia — "Ke hoach dieu tri gom ba viec sau"
# la mot cau, khong phai mot tieu de.
DAI_TOI_DA = max(len(m) for m in MUC_CHUAN) + 8


def _khoa(s):
    """Bo dau, ha chu thuong. PHAI doi `đ`/`Đ` bang tay.

    `unicodedata.normalize("NFD")` tach dau thanh ky tu to hop, nhung `đ` KHONG
    phai `d` cong dau — no la mot ky tu rieng, khong tach duoc. Nen
    "ke hoach dieu tri" ra "ke hoach đieu tri" voi `đ` con nguyen, va no khong
    khop khoa "ke hoach dieu tri" trong bang.

    Ba phep thu do vi dung cho nay: `## Chan doan`, `Ke hoach dieu tri:`, va
    `tien su gia dinh` — ca ba deu co `đ`.
    """
    tho = "".join(c for c in unicodedata.normalize("NFD", s)
                  if unicodedata.category(c) != "Mn")
    tho = tho.replace("đ", "d").replace("Đ", "D")
    return tho.lower().strip(" :*#-.\t")


def la_tieu_de_bien_the(dong):
    """-> ten muc chuan, hoac None. Thuan tuy, de test duoc."""
    d = re.sub(r"[*_#`]+", "", str(dong or "")).strip()
    if not d or len(d) > DAI_TOI_DA:
        return None
    d = re.sub(r"^[-+•]\s*", "", d)
    if not d.rstrip().endswith(":") and _khoa(d) not in DONG_NGHIA:
        # Khong co dau hai cham va khong khop dong nghia -> khong phai tieu de.
        return None
    return DONG_NGHIA.get(_khoa(d))


def chuan_hoa(van_ban):
    """Doi tieu de bien the thanh ten muc chuan. Giu nguyen moi dong khac.

    PHAI la phep dong nhat tren ban nhap da dung ten muc chuan — xem phep thu
    cong bang o dau tep.
    """
    ra = []
    for dong in str(van_ban or "").split("\n"):
        ten = la_tieu_de_bien_the(dong)
        if ten:
            ra.append(ten)
            continue
        # Bo dam Markdown va dau gach dau dong o cac dong noi dung, de phep tach
        # menh de khong coi "**" la mot tu.
        d = re.sub(r"[*_`]+", "", dong)
        ra.append(re.sub(r"^(\s*)[-+•]\s+", r"\1", d))
    return "\n".join(ra)
