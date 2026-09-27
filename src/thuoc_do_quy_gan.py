# -*- coding: utf-8 -*-
"""Diem quy gan — thuoc do NHIN THAY duoc loi doi chu the.

LY DO TON TAI.

Du an phat bieu rang ROUGE va Section F1 mu truoc loi quy gan, va da chung
minh dieu do bang so: hoan doi "me di ung penicillin" <-> "tre di ung
penicillin" cho Section F1 = 1,0000 o 271/271 cap, ROUGE-1 = 1,0000 khi hai
chu the xuat hien cung so lan.

Nhung roi Cua 4 lai dung chinh bo cham do de ket luan ve nhanh C. Ket qua:
nam nhanh nam trong khoang 0,3514–0,3643 — chenh nhau 0,006, tuc duoi muc
nhieu. Ket luan "C khong hon B" duoc rut ra tu mot cai thuoc ma chinh du an
da chung minh la khong do duoc dai luong dang xet.

Do la mot loi thiet ke danh gia, khong phai mot ket qua nghien cuu.

CAI NAY DO GI. Dung mot dai luong: **menh de co duoc gan cho dung nguoi khong**.

    menh de  =  (chu the, tap tu noi dung)

Hai ban duoc doi chieu theo NOI DUNG truoc; trong so cac cap da khop noi dung,
dem xem bao nhieu cap khop luon CHU THE. Nho tach hai buoc nay ma phan biet
duoc ba thu ma ROUGE tron lam mot:

    khop noi dung + khop chu the  ->  dung
    khop noi dung + LECH chu the  ->  SAI QUY GAN   (loi nguy hiem)
    khong khop noi dung           ->  thua / thieu  (bia / bo sot)

GIOI HAN, phai ghi vao bao cao.

  1. Chu the doc bang LUAT be mat (tu chi nguoi trong cau, roi den ten muc).
     No khong hieu cau; "ba chau" hay "con cua chi gai" se doc sai. Da do tren
     tap that truoc khi dung — xem `docs/ket-qua/`.
  2. Chi phan biet hai muc `bệnh nhân` / `người nhà`. Hai nguoi nha khac nhau
     (me va ba) bi gop. Do la lua chon co chu dinh: bo du lieu chi co 8,8% mau
     co luot nguoi nha, tach nho hon nua thi khong con co mau.
  3. Doi chieu voi BAN THAM CHIEU, nen ke thua moi thieu sot cua ban tham
     chieu. Cham voi hoi thoai la viec cua phep cham tay.

  4. NHAY VOI CACH DONG GOI CAU — gioi han nang nhat, phat hien 07/09/2026 khi
     so nhanh A voi nhanh B. Menh de tach theo RANH GIOI CAU. Ban tham chieu
     goi nhieu su kien vao mot cau van xuoi:

         "Benh nhan nam nho tuoi, trong tuan qua co bieu hien nghet mui nhieu,
          ho tang hon binh thuong, sot 101 do F vao ngay hom qua."  -> 1 menh de

     con nhanh B xuat tung manh mot:

         "nghet mui nhieu (may hom nay)."  "ho nhieu hon binh thuong."
         "sot (hom qua)."  "nhiet do 101 do F."                     -> 4 menh de

     Ghep tham lam noi MOT manh voi cau dai do, ba manh con lai thanh "thua".
     Tuc mot phan diem tru cua nhanh B den tu CACH DONG GOI CAU, khong phai tu
     noi dung sai.

     Hai he qua, phai noi ca hai:

       - `f1_quy_gan` KHONG duoc dung mot minh de so mot mo hinh viet van xuoi
         voi mot bo sinh theo luat. No thien vi ben nao giong ban tham chieu ve
         HINH THUC — va mo hinh fine-tune thi giong theo dinh nghia, vi no hoc
         tu chinh cac ban ay.
       - `dung_quy_gan` va `so_sai_chu_the` chiu anh huong it hon vi chi tinh
         tren cap DA KHOP noi dung, nhung khong mien nhiem: cap nao khop duoc
         van phu thuoc cach dong goi.

     CHUA SUA. Sua dung phai tach den don vi nho hon cau (menh de con), va do la
     bai toan phan tich cu phap tieng Viet, khong lam duoc bang bieu thuc chinh
     quy. Ghi o day de khong ai doc bang so ma quen mat.
"""
import re
import unicodedata
from dataclasses import dataclass
from typing import FrozenSet, List, Optional, Tuple

# Nguong trung tu de coi hai menh de la "cung noi dung".
NGUONG_NOI_DUNG = 0.6

# Tu chi BENH NHAN va tu chi NGUOI NHA. Doc trong cau, uu tien hon ten muc.
TU_BENH_NHAN = ("trẻ", "bé", "cháu", "bệnh nhân", "con", "em bé", "trẻ nhỏ",
                "trẻ sơ sinh", "bn")

# CHI nhung tu chi nguoi nha KHONG the hieu theo nghia khac.
#
# Da thu dung danh sach day du va no hong ngay o cau dau tien:
#
#     "Ho và sốt ba ngày."     -> "ba" khop tu chi BO      -> gan cho nguoi nha
#     "Bác sĩ khám thấy..."    -> "bác" khop tu chi BAC    -> gan cho nguoi nha
#     "Sưng má bên trái."      -> "má" khop tu chi ME      -> gan cho nguoi nha
#     "Cô bé quấy khóc."       -> "cô" khop tu chi CO      -> gan cho nguoi nha
#
# Dung mot ho lop lỗi da gap o Task 1 (nhan "nhi" chi dung 53% vi "hoi tre em
# co hut", "aspirin tre em"). Nguyen tac da chot cua du an: **chan gop nham
# quan trong hon chan bo sot**. Mot menh de bi bo sot chi lam giam do bao phu;
# mot menh de bi gan nham nguoi lam hong dung dai luong dang do.
#
# Cai gia phai tra duoc ghi lai bang test: cau chi noi "Ba cháu bị tiểu đường"
# se bi doc thanh chuyen cua benh nhan. Xem `TU_NGUOI_NHA_KHONG_NHAN_DIEN`.
TU_NGUOI_NHA = ("mẹ", "bố", "cha", "người nhà", "gia đình", "bố mẹ", "cha mẹ",
                "phụ huynh", "anh trai", "chị gái", "em trai", "em gái",
                "ông nội", "bà nội", "ông ngoại", "bà ngoại", "mẹ ruột",
                "bố ruột", "mẹ đẻ", "bố đẻ")

# Khong nhan dien, co chu dinh. Moi tu o day deu co nghia thu hai thuong gap
# trong benh an. Ghi ra day de bao cao neu duoc gioi han, khong giau.
TU_NGUOI_NHA_KHONG_NHAN_DIEN = ("ba", "má", "cô", "chú", "bác", "cậu", "dì",
                                "mợ", "thím", "ông", "bà", "anh", "chị", "em")

# Muc mac dinh thuoc ve nguoi nha khi cau khong neu ro ai.
MUC_NGUOI_NHA = ("GIA ĐÌNH",)

# Tu dem. CO Y KHONG CHUA tu phu dinh.
#
# Moi bang tu dem tieng Viet san co deu liet "khong" / "chua" vao tu dem. Neu
# bo chung o day thi "tre khong di ung penicillin" va "tre di ung penicillin"
# thanh cung mot menh de — dung cai loi chet nguoi ma thuoc do nay sinh ra de
# chan. Co mot test rieng giu dieu nay.
TU_DEM = frozenset("""
là và của với trong cho các những đã đang sẽ ở tại một này đó ạ rồi thì mà
nhưng vào ra lên xuống về từ đến do bởi được bị có khi nếu nên cũng còn rất
hơn nữa khoảng chừng trên dưới sau trước cùng theo qua vẫn lại mới
""".split())

TU_PHU_DINH = frozenset(["không", "chưa", "chẳng", "chả", "khỏi", "hết"])

# Chu so viet bang chu -> chu so. De "ba ngay" va "3 ngay" la mot menh de.
SO_BANG_CHU = {"một": "1", "hai": "2", "ba": "3", "bốn": "4", "năm": "5",
               "sáu": "6", "bảy": "7", "tám": "8", "chín": "9", "mười": "10",
               "mốt": "1", "tư": "4", "rưỡi": "0.5"}

_TIEU_DE = re.compile(r"^[^a-zà-ỹ]{3,}$")
_KHONG_PHAI_CHU = re.compile(r"[^\w]+", re.UNICODE)


@dataclass(frozen=True)
class MenhDe:
    chu_the: str
    tu: FrozenSet[str]
    cau: str
    muc: str


# ------------------------------------------------------------------ tach

def _la_tieu_de(dong: str) -> bool:
    """Dong toan chu hoa, khong co dau cau ket — la ten muc chu khong phai menh de."""
    s = dong.strip()
    if not s or len(s) > 70:
        return False
    return s == s.upper() and not s.endswith(".")


def _chuan(s: str) -> str:
    return unicodedata.normalize("NFC", s or "").strip()


def _tu_noi_dung(cau: str) -> FrozenSet[str]:
    """Tap tu de doi chieu noi dung.

    Bo tu chi nguoi (chung da thanh truong `chu_the`, giu lai thi hai ban khac
    chu the se tu dong khac noi dung va phep do sup do). Bo tu dem. GIU tu phu
    dinh.
    """
    tho = [t for t in _KHONG_PHAI_CHU.split(_chuan(cau).lower()) if t]
    nguoi = set()
    for cum in TU_BENH_NHAN + TU_NGUOI_NHA:
        nguoi.update(cum.split())
    # GIU lai con so. "dau bung 3 ngay" va "dau bung 5 ngay" phai la hai menh
    # de khac nhau — sai mot con so trong benh an la loi that, khong phai bien
    # the cach dien dat.
    return frozenset(SO_BANG_CHU.get(t, t) for t in tho if t in TU_PHU_DINH
                     or (t not in TU_DEM and t not in nguoi))


def _con_so(tu: FrozenSet[str]) -> FrozenSet[str]:
    return frozenset(t for t in tu if any(c.isdigit() for c in t))


def _chu_the_cua_cau(cau: str, muc: str) -> str:
    """Tu trong cau thang ten muc — 'Be di hoc' duoi muc GIA DINH van la cua be."""
    thap = " " + _chuan(cau).lower() + " "

    def co(cum_list):
        return any(re.search(r"(?<![\w])" + re.escape(c) + r"(?![\w])", thap)
                   for c in cum_list)

    bn, nn = co(TU_BENH_NHAN), co(TU_NGUOI_NHA)
    if bn and not nn:
        return "bệnh nhân"
    if nn and not bn:
        return "người nhà"
    if bn and nn:
        # Ca hai cung xuat hien: lay tu dung DAU cau lam chu ngu.
        vi_bn = min((thap.find(" " + c + " ") for c in TU_BENH_NHAN
                     if " " + c + " " in thap), default=10**6)
        vi_nn = min((thap.find(" " + c + " ") for c in TU_NGUOI_NHA
                     if " " + c + " " in thap), default=10**6)
        return "bệnh nhân" if vi_bn <= vi_nn else "người nhà"
    return "người nhà" if any(k in muc.upper() for k in MUC_NGUOI_NHA) else "bệnh nhân"


def tach_menh_de(ban: str) -> List[MenhDe]:
    """Benh an -> danh sach menh de co chu the. Thuan tuy, khong goi mo hinh."""
    ra: List[MenhDe] = []
    muc = ""
    for dong in _chuan(ban).split("\n"):
        dong = dong.strip()
        if not dong:
            continue
        if _la_tieu_de(dong):
            muc = dong
            continue
        for cau in re.split(r"(?<=[.;!?])\s+", dong):
            cau = cau.strip(" -•\t")
            if not cau:
                continue
            tu = _tu_noi_dung(cau)
            if not tu:
                continue
            ra.append(MenhDe(chu_the=_chu_the_cua_cau(cau, muc),
                             tu=tu, cau=cau, muc=muc))
    return ra


# ------------------------------------------------------------- doi chieu

def _giao(a: FrozenSet[str], b: FrozenSet[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def cung_noi_dung(x: MenhDe, y: MenhDe) -> bool:
    """Hai menh de noi cung mot thu khong — CHUA xet chu the.

    Phu dinh lech nhau thi khong bao gio la cung noi dung, du tu con lai trung
    het. Kiem rieng vi phep do trung tu don thuan se cho "khong di ung" va
    "di ung" ty le 2/3 va lot qua nguong.
    """
    if (x.tu & TU_PHU_DINH) != (y.tu & TU_PHU_DINH):
        return False
    # Lech con so cung khong bao gio la cung menh de. "dau bung 3 ngay" va
    # "dau bung 5 ngay" trung 3/4 tu — dat nguong nao thi cung lot. Con so
    # sai trong benh an la loi that chu khong phai cach dien dat khac.
    if _con_so(x.tu) != _con_so(y.tu):
        return False
    return _giao(x.tu, y.tu) >= NGUONG_NOI_DUNG


def doi_chieu(du_doan: List[MenhDe], tham_chieu: List[MenhDe]):
    """Ghep tham lam theo do trung tu giam dan.

    Tra ve (trung, sai_chu_the, thua, thieu) — `trung` va `sai_chu_the` la cac
    cap da khop noi dung.
    """
    cap = []
    for i, p in enumerate(du_doan):
        for j, t in enumerate(tham_chieu):
            if cung_noi_dung(p, t):
                cap.append((_giao(p.tu, t.tu), i, j))
    cap.sort(key=lambda c: (-c[0], c[1], c[2]))

    da_p, da_t = set(), set()
    trung, sai = [], []
    for _, i, j in cap:
        if i in da_p or j in da_t:
            continue
        da_p.add(i)
        da_t.add(j)
        (trung if du_doan[i].chu_the == tham_chieu[j].chu_the else sai).append((i, j))

    thua = [i for i in range(len(du_doan)) if i not in da_p]
    thieu = [j for j in range(len(tham_chieu)) if j not in da_t]
    return trung, sai, thua, thieu


# ------------------------------------------------------------------ diem

def diem(du_doan: str, tham_chieu: str) -> dict:
    """Bo chi so quy gan cua mot cap (ban sinh, ban tham chieu).

    `f1_quy_gan` la chi so chinh: F1 tren cap (chu the, noi dung). No phat CA
    HAI chieu — ghi sai nguoi bi tru, ma viet it di cho an toan cung bi tru.
    """
    p = tach_menh_de(du_doan)
    t = tach_menh_de(tham_chieu)
    trung, sai, thua, thieu = doi_chieu(p, t)

    dung = len(trung)
    do_chinh_xac = dung / len(p) if p else 0.0
    do_bao_phu = dung / len(t) if t else 0.0
    f1 = (2 * do_chinh_xac * do_bao_phu / (do_chinh_xac + do_bao_phu)
          if (do_chinh_xac + do_bao_phu) else 0.0)
    khop_noi_dung = dung + len(sai)

    return {
        "f1_quy_gan": round(f1, 4),
        "do_chinh_xac": round(do_chinh_xac, 4),
        "do_bao_phu": round(do_bao_phu, 4),
        # Trong so menh de da noi DUNG NOI DUNG, bao nhieu phan gan DUNG NGUOI.
        # Tach rieng vi no khong bi anh huong boi bo sot — hai loi khac nhau.
        "dung_quy_gan": round(dung / khop_noi_dung, 4) if khop_noi_dung else 0.0,
        "bo_sot": round(len(thieu) / len(t), 4) if t else 0.0,
        "them_moi": round(len(thua) / len(p), 4) if p else 0.0,
        "so_sai_chu_the": len(sai),
        "so_thieu": len(thieu),
        "so_thua": len(thua),
        "so_menh_de_du_doan": len(p),
        "so_menh_de_tham_chieu": len(t),
    }
