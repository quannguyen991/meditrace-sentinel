# -*- coding: utf-8 -*-
"""Sinh cap ung vien quan he — doi vai giua CHUONG TRINH va MO HINH.

PHAT HIEN BUOC NGOAT (06/09/2026, Cua 4).
Tren 35 hoi thoai that, mo hinh danh dau `quan_he` o **0/282** phat bieu. Bang
boc co che cho con so dut khoat: `C_khong_lien_ket` bang DUNG `B` toi tung chu
so — luat cap nhat trang thai khong he thay doi gi, vi no chay tren truong
`quan_he` ma truong do luon rong.

Va do KHONG phai vi hoi thoai khong co quan he: 21/35 hoi thoai co moc kieu
"hom qua… hom nay…" — dung dang `dien_bien` ma du an muon bat.

CHAN DOAN. Trich phat bieu la bai toan **liet ke**; danh dau quan he la bai
toan **khoi phat** (self-initiation): mo hinh phai tu nho rang minh vua ghi mot
ban ghi tuong tu o dau do phia truoc, tu quay lai doi chieu, roi tu quyet dinh
ghi them mot truong khong ai hoi. Tren hoi thoai 4 luot do chinh tay minh sinh
ra thi lam duoc (15/15). Tren hoi thoai 10–28 luot cua nguoi that thi khong,
vi luc do ban ghi tuong ung da troi qua tu lau.

CACH SUA. Doi vai:

    truoc:  mo hinh  vua liet ke phat bieu  VUA tu phat hien quan he
    nay:    CHUONG TRINH liet ke cap dang ngo (vet can 100% theo cau truc)
            MO HINH (hoac LUAT) chi tra loi mot cau bon lua chon tren mot cap

Day la cung mot nguyen tac da dung o `cap_nhat.py` — *mo hinh trich, chuong
trinh ap luat* — chi la day them mot buoc nua: **chuong trinh con sinh ca cau
hoi**. Mo hinh khong phai nho gi, khong phai tu khoi phat gi.

Do vet (recall) cua buoc liet ke la tinh chat CAU TRUC chu khong phai ket qua
do duoc: cap nao thoa dieu kien cung duoc liet ke, khong phu thuoc mo hinh dang
chu y cho nao. Cai phai do la do CHINH XAC cua buoc phan.
"""
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from src.phat_bieu import QUAN_HE, PhatBieu

# Ty le do dai toi thieu giua hai cum noi dung. Chan truong hop mot cum rat
# ngan lot vao mot cum rat dai ("ho" nam trong "ho ga nghi do virus").
NGUONG_DO_DAI = 0.5

# Vi sao la BAO HAM chu khong phai ty le giao.
#
# Ban dau dung "ty le giao >= 0,8". Test danh sach song song lam no hong that:
#
#     "nguy cơ hỏng dụng cụ"        {nguy, cơ, hỏng, dụng, cụ}        5 tu
#     "nguy cơ phải tháo dụng cụ"   {nguy, cơ, phải, tháo, dụng, cụ}  6 tu
#     giao = {nguy, cơ, dụng, cụ} = 4 tu  ->  4/5 = 0,80  ->  LOT
#
# Nang nguong len 0,85 chi la va tam. Cho khac nhau ve BAN CHAT nam o cho:
# quan he that gan nhu luon la CUNG mot cum, hoac mot cum la ban chi tiet hon
# cua cum kia ("dau bung" / "dau bung du doi") — tuc mot ben BAO HAM ben kia.
# Con muc liet ke song song thi CA HAI ben deu co tu rieng.
#
# Nen dieu kien la: tap tu cua ben nay phai nam gon trong ben kia.


def _lien_quan(a: Optional[str], b: Optional[str]) -> bool:
    ta, tb = _tu(a), _tu(b)
    if not ta or not tb:
        return False
    if not (ta <= tb or tb <= ta):
        return False
    return min(len(ta), len(tb)) / max(len(ta), len(tb)) >= NGUONG_DO_DAI

# So cap toi da moi hoi thoai. Hoi thoai dai co the sinh to hop lon; cat de
# chi phi khong no theo binh phuong. `da_bi_cat` bao lai khi da cat.
TOI_DA_MAC_DINH = 30

# Dau hieu dinh chinh — nam trong VAN BAN loi thoai, khong nam trong truong nao.
# Day la ly do `goi_y_bang_luat` can `luot_thoai` chu khong chi can ban ghi.
DAU_HIEU_DINH_CHINH = (
    "à không", "à quên", "à nhầm", "nhầm rồi", "nhầm ạ", "xin lỗi",
    "không phải", "à mà", "à sai", "nói lại", "đúng hơn là", "à mà không",
)

# Moc chi MOT THOI DIEM. Hai thoi diem khac nhau thi hai ban ghi cung dung —
# do la dien bien. Phan biet voi moc chi DO DAI ("5 ngay", "ba tuan"), noi ma
# hai gia tri khac nhau thuong la mot ben ghi sai.
MOC_THOI_DIEM = (
    "hôm nay", "hôm qua", "hôm kia", "hôm trước", "hôm nọ",
    "sáng nay", "trưa nay", "chiều nay", "tối nay", "đêm qua", "tối qua",
    "sáng qua", "chiều qua", "tuần trước", "tuần này", "tháng trước",
    "tháng này", "năm ngoái", "hiện tại", "bây giờ", "lúc nãy", "khi nãy",
)


@dataclass(frozen=True)
class CapUngVien:
    """Mot cap dang ngo. `a` luon truoc `b` theo thu tu xuat hien."""
    a: int
    b: int
    ly_do: Tuple[str, ...]
    diem: float

    def khoa(self):
        return (self.a, self.b)


# ----------------------------------------------------------------- tach tu

_KHONG_PHAI_CHU = re.compile(r"[^\w]+", re.UNICODE)


def _tu(s: Optional[str]) -> set:
    return {t for t in _KHONG_PHAI_CHU.split((s or "").lower()) if t}


def _chuan_moc(m: Optional[str]) -> str:
    return (m or "").strip().lower()


# ------------------------------------------------------------- sinh cap

def _tin_hieu_khac(a: PhatBieu, b: PhatBieu) -> Tuple[str, ...]:
    """Nhung truong ma hai ban ghi KHAC nhau. Rong = khong co gi de phan."""
    ly_do = []
    if _chuan_moc(a.moc_thoi_gian) != _chuan_moc(b.moc_thoi_gian):
        ly_do.append("khác mốc")
    if bool(a.phu_dinh) != bool(b.phu_dinh):
        ly_do.append("khác phủ định")
    if a.do_chac_chan != b.do_chac_chan:
        ly_do.append("khác chắc chắn")
    if a.thoi_gian_su_kien != b.thoi_gian_su_kien:
        ly_do.append("khác thời điểm")
    return tuple(ly_do)


def _cap_tho(danh_sach: List[PhatBieu],
             luot_thoai: Optional[Dict[int, str]] = None):
    """Moi cap thoa dieu kien cau truc, chua cat."""
    theo_id = {p.id: p for p in danh_sach}
    ra = []
    for i in range(len(danh_sach)):
        for j in range(i + 1, len(danh_sach)):
            a, b = danh_sach[i], danh_sach[j]
            # Khac chu the thi khong bao gio la quan he. Ghep hai chu the lai
            # chinh la loi nguy hiem nhat ma du an di chan — tang nay tuyet
            # doi khong duoc tu tao ra no.
            if a.chu_the_id != b.chu_the_id:
                continue
            if not _lien_quan(a.noi_dung, b.noi_dung):
                continue
            ly_do = _tin_hieu_khac(a, b)
            if not ly_do:
                continue        # trung lap hoan toan — xem `sinh_cap_trung_lap`
            khoang_cach = abs(b.id - a.id) or 1
            diem = len(ly_do) + 1.0 / (1 + khoang_cach)
            # Cap co dau hieu dinh chinh ngay trong loi thoai duoc uu tien giu
            # khi phai cat bot. Dinh chinh la tinh huong ma bo sot mot cap gay
            # hai nhat: bo qua no thi benh an giu lai con so nguoi noi DA TU
            # NHAN la sai. Khong co ve nay thi `luot_thoai` chi la mot tham so
            # nhan vao roi khong dung, va thu tu cat hoan toan theo khoang cach.
            if luot_thoai:
                tam = CapUngVien(a=a.id, b=b.id, ly_do=ly_do, diem=0.0)
                van = _van_ban_bang_chung(tam, theo_id, luot_thoai)
                if any(d in van for d in DAU_HIEU_DINH_CHINH):
                    diem += 10.0
                    ly_do = ly_do + ("có dấu hiệu đính chính",)
            ra.append(CapUngVien(a=a.id, b=b.id, ly_do=ly_do, diem=diem))
    return ra


def sinh_cap(danh_sach: List[PhatBieu], luot_thoai: Optional[Dict[int, str]] = None,
             toi_da: int = TOI_DA_MAC_DINH) -> List[CapUngVien]:
    """Liet ke cap dang ngo. Thuan tuy, khong goi mo hinh.

    `luot_thoai` chi anh huong THU TU khi phai cat bot, khong anh huong cap nao
    duoc coi la ung vien. Do vet cua buoc liet ke van la tinh chat cau truc.
    """
    ra = _cap_tho(danh_sach, luot_thoai)
    ra.sort(key=lambda c: (-c.diem, c.a, c.b))
    return ra[:toi_da]


def da_bi_cat(danh_sach: List[PhatBieu], toi_da: int = TOI_DA_MAC_DINH) -> bool:
    """Co cap nao bi cat khong. Bao ra chu khong im lang — so cap bi bo la mot
    nguon bo sot, phai vao bao cao."""
    return len(_cap_tho(danh_sach)) > toi_da


def sinh_cap_trung_lap(danh_sach: List[PhatBieu]) -> List[CapUngVien]:
    """Hai ban ghi giong het VA khong truong nao khac.

    Day khong phai quan he — do la trung lap luc trich. Tra ve rieng vi cach
    xu ly khac han: quan he thi phan, trung lap thi gop.
    """
    ra = []
    for i in range(len(danh_sach)):
        for j in range(i + 1, len(danh_sach)):
            a, b = danh_sach[i], danh_sach[j]
            if a.chu_the_id != b.chu_the_id:
                continue
            if _tu(a.noi_dung) != _tu(b.noi_dung) or not _tu(a.noi_dung):
                continue
            if _tin_hieu_khac(a, b):
                continue
            ra.append(CapUngVien(a=a.id, b=b.id, ly_do=("trùng lặp",), diem=0.0))
    return ra


# ------------------------------------------------- goi y bang luat (khong mo hinh)

def _van_ban_bang_chung(cap: CapUngVien, theo_id: Dict[int, PhatBieu],
                        luot_thoai: Dict[int, str]) -> str:
    luot = set()
    for i in (cap.a, cap.b):
        p = theo_id.get(i)
        if p:
            luot.update(p.bang_chung)
    return " ".join(luot_thoai.get(l, "") for l in sorted(luot)).lower()


def goi_y_bang_luat(cap: CapUngVien, danh_sach: List[PhatBieu],
                    luot_thoai: Dict[int, str]) -> Optional[str]:
    """Doan quan he tu dau hieu be mat. Tra `None` khi khong chac.

    Hai vai:
      1. Duong lui khi khong co GPU — ca co che loi van chay duoc.
      2. Doi chung cho buoc phan bang mo hinh. Mo hinh khong hon luat nay thi
         khong can mo hinh o buoc nay.

    KHONG duoc doan bua. Khong co dau hieu thi tra `None` de mo hinh phan —
    doan bua o day se sinh ra quan he gia, va quan he gia lam luat cap nhat
    vut mat thong tin dung.
    """
    theo_id = {p.id: p for p in danh_sach}
    van_ban = _van_ban_bang_chung(cap, theo_id, luot_thoai or {})
    a, b = theo_id.get(cap.a), theo_id.get(cap.b)
    if a is None or b is None:
        return None

    # 1. Dau hieu dinh chinh nam trong loi noi. Uu tien cao nhat: nguoi noi
    #    da tu tuyen bo la minh noi sai.
    if any(d in van_ban for d in DAU_HIEU_DINH_CHINH):
        return "đính chính"

    # 2. Hai MOC THOI DIEM khac nhau => ca hai cung dung => dien bien.
    #    Day la cho de sai nhat cua ca du an, nen no la mot nhanh rieng.
    ma, mb = _chuan_moc(a.moc_thoi_gian), _chuan_moc(b.moc_thoi_gian)
    if ma and mb and ma != mb:
        if _la_thoi_diem(ma) and _la_thoi_diem(mb):
            return "diễn biến"

    return None


def _la_thoi_diem(moc: str) -> bool:
    return any(t in moc for t in MOC_THOI_DIEM)


# ------------------------------------------------------------- ap phan quyet

def ap_phan_quyet(danh_sach: List[PhatBieu],
                  phan_quyet: Dict[Tuple[int, int], Optional[str]]) -> List[PhatBieu]:
    """Gan `quan_he`/`quan_he_voi` vao ban SAO. Khong sua ban goc.

    Ba rang buoc, moi rang buoc chan mot cach lam vo `cap_nhat.ap_luat`:
      - gia tri phai thuoc `QUAN_HE`, khong thi bo (mo hinh tra rac)
      - moi ban ghi nhan toi da MOT quan he (`quan_he_voi` la mot so)
      - khong tao vong: a->b roi b->a se lam luat cap nhat quanh mai
    """
    ra = [PhatBieu(**p.to_dict()) for p in danh_sach]
    theo_id = {p.id: p for p in ra}
    cha: Dict[int, int] = {}

    for (a, b) in sorted(k for k in phan_quyet if k is not None):
        quan_he = phan_quyet[(a, b)]
        if quan_he not in QUAN_HE:
            continue
        if a not in theo_id or b not in theo_id or a == b:
            continue
        if b in cha:
            continue                       # ban ghi da nhan mot quan he roi
        if _den_duoc(cha, a, b):
            continue                       # them canh nay se tao vong
        cha[b] = a
        theo_id[b].quan_he = quan_he
        theo_id[b].quan_he_voi = a
    return ra


def _den_duoc(cha: Dict[int, int], tu: int, den: int) -> bool:
    """Di nguoc theo `cha` tu `tu`, co gap `den` khong."""
    da_qua = set()
    hien = tu
    while hien is not None and hien not in da_qua:
        if hien == den:
            return True
        da_qua.add(hien)
        hien = cha.get(hien)
    return False


# ------------------------------------------------------------------ thong ke

def thong_ke(danh_sach: List[PhatBieu], luot_thoai: Optional[Dict[int, str]] = None,
             toi_da: int = TOI_DA_MAC_DINH) -> dict:
    """So lieu cho bao cao — moi con so trong bao cao phai sinh tu day."""
    cap = sinh_cap(danh_sach, luot_thoai, toi_da)
    goi_y = [goi_y_bang_luat(c, danh_sach, luot_thoai or {}) for c in cap]
    return {
        "so_phat_bieu": len(danh_sach),
        "so_cap": len(cap),
        "bi_cat": da_bi_cat(danh_sach, toi_da),
        "so_cap_truoc_khi_cat": len(_cap_tho(danh_sach)),
        "so_trung_lap": len(sinh_cap_trung_lap(danh_sach)),
        "luat_quyet_duoc": sum(1 for g in goi_y if g is not None),
        "luat_dinh_chinh": sum(1 for g in goi_y if g == "đính chính"),
        "luat_dien_bien": sum(1 for g in goi_y if g == "diễn biến"),
    }
