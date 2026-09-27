# -*- coding: utf-8 -*-
"""Tu dien phuong ngu mien Trung / mien Nam, va phep thay tu trong loi thoai.

VI SAO CAN (10/09/2026).

Bo sinh cua du an truoc do CO ba vung (`bac`, `nam`, `trung`) nhung khac nhau
chi o TIEU TU: "a", "nghen", "hi", "nha". Tu vung thi giong het nhau — moi
vung deu noi "sot", "ho", "met".

Nguoi that khong noi vay. O mien Nam mot nguoi me se noi "chau nong ham hap"
chu it khi noi "chau sot"; o mien Trung se la "hom te" chu khong phai "hom kia".

Day la mot dang cua LOI QUY GAN ma du an di do, chi la o tang tu vung: he
thong phai hieu "nong ham hap" va "sot" la MOT THU. Neu khong thi:

  - buoc trich ghi "nong ham hap" nguyen van    -> benh an khong chuan hoa
  - buoc loc cap ung vien khong ghep duoc       -> mat quan he
  - phep cham theo chuoi khong khop             -> bao loi oan

NGUYEN TAC THAY TU. Chi thay trong loi cua BENH NHAN va NGUOI NHA, khong thay
trong loi BAC SI: bac si duoc dao tao noi chuan, va tron lai thi mat mot dau
hieu that trong hoi thoai kham benh.

DAP AN GIU NGHIA CHUAN. Hoi thoai viet "lu du", dap an van ghi "met".
Do chinh la phep thu: mo hinh co quy duoc ve khai niem chuan khong.

TRU cum KHONG dong nghia voi tu chuan (`GIU_NGUYEN`, sua 24/09/2026): "nong
ham hap" chua phai "sot" khi chua do nhiet do, nen dap an ghi dung loi nguoi noi.
Vi du cu o dong tren tung la "nong ham hap -> sot" — chinh vi du do sai.

NGUON. Tu dien 30 tu do nguoi dung cung cap (`data/ngoai/tu_dien_phuong_ngu.csv`),
ma nguoi dung xac nhan ngay 11/09/2026 la do GPT SINH. Tu ngay do bang thay KHONG
ap vao khuon train (`sinh_hoi_thoai_viet.PHUONG_NGU_TRONG_TRAIN`), chi o tap danh
gia. Moi muc phai doi chieu tu dien that (Huynh Cong Tin 2007) hoac nguoi dia
phuong truoc khi dung cho ket luan. Xem `docs/nguon-du-lieu.md`.
"""
import csv
import re
from pathlib import Path

from src import duong_dan

TEP_TU_DIEN = duong_dan.THU_MUC_DU_LIEU / "ngoai" / "tu_dien_phuong_ngu.csv"

# Vung trong tu dien -> khoa vung cua bo sinh.
VUNG = {"miền Trung": "trung", "miền Nam": "nam"}


def nap(tep=None):
    """-> {khoa_vung: [(tu_phuong_ngu, nghia_chuan), ...]}.

    Tra ve rong khi khong co tep, KHONG nem loi: bo sinh phai chay duoc ca khi
    chua co tu dien, va phai bao ra chu khong im lang thay bang tu chuan.
    """
    tep = Path(tep or TEP_TU_DIEN)
    ra = {v: [] for v in VUNG.values()}
    if not tep.exists():
        return ra
    with open(tep, encoding="utf-8", newline="") as f:
        for hang in csv.DictReader(f):
            vung = VUNG.get((hang.get("vùng") or "").strip())
            tu = (hang.get("từ/cụm từ") or "").strip()
            nghia = (hang.get("nghĩa chuẩn") or "").strip()
            if vung and tu and nghia:
                ra[vung].append((tu, nghia))
    return ra


# Chi nhung cap co the thay THANG trong cau ma khong pha ngu phap. Nhieu muc
# trong tu dien la dai tu hoac tu de hoi ("rang", "mo", "te") — thay bua vao
# mot cau bat ky se ra cau sai, nen phai liet ke tay chu khong quet ca tu dien.
#
# Chieu thay la CHUAN -> PHUONG NGU: bo sinh viet cau bang tu chuan truoc, roi
# doi sang phuong ngu de dua vao hoi thoai. Dap an giu ban chuan.
THAY_DUOC = {
    "trung": [
        ("hôm kia", "hôm tê"),
        ("dạo này", "bữa chừ"),
        ("bây giờ", "chừ"),
        ("trẻ em", "con nít"),
    ],
    "nam": [
        ("hôm trước", "bữa hổm"),
        ("dạo gần đây", "hổm rày"),
        ("ngất", "xỉu"),
        ("sốt", "nóng hầm hập"),
        ("mệt", "lừ đừ"),
        ("đại tiện", "đi cầu"),
    ],
}

# Tu DUNG SAU chan phep thay. Khong co bang nay thi bo sinh viet ra tieng Viet
# sai, va do la loi te hon khong co phuong ngu: du lieu hong ma nhin bang so
# khong thay.
#
# Da hong that, test bat duoc:
#     "mệt mỏi"  ->  "lừ đừ mỏi"    (khong phai tieng Viet)
#     "sốt cao"  ->  "nóng hầm hập cao"
#
# Nguyen nhan: ranh gioi TU khong phai ranh gioi TU GHEP. "met" trong "met
# moi" dung la mot tu tach bang dau cach, nhung thay rieng no thi vo nghia.
CHAN_SAU = {
    "sốt": {"cao", "nhẹ", "siêu", "xuất", "phát", "rét", "ruột", "li"},
    "mệt": {"mỏi"},
    "ngất": {"xỉu"},
}

# Hai tu bi BO HAN khoi bang thay, du co trong tu dien:
#
#   "không" -> "nỏ"   "nỏ" la phu dinh TRAN THUAT. Cau hoi "co sot khong?"
#                     doi thanh "co sot no?" la sai. Tach hai truong hop do
#                     can phan tich cu phap, chua lam.
#   "làm"   -> "mần"  xuat hien trong "lam xet nghiem", "lam sao" voi nghia
#                     rat khac nhau; thay dong loat ra cau khong tu nhien.
#
# Ghi ra day chu khong xoa im lang, de nguoi doc sau biet la da can nhac.
DA_BO = {"không": "nỏ", "làm": "mần"}

# Cum phuong ngu KHONG dong nghia voi tu chuan: dap an GIU NGUYEN loi nguoi noi.
#
# SUA 24/09/2026. Cap ("sot", "nong ham hap") o THAY_DUOC tu 10/09, theo quy uoc
# "dap an giu nghia chuan" o dau tep: hoi thoai viet "nong ham hap", dap an ghi
# "sot, chac chan". Nhung bang chuan hoa cua chinh du an (`chuan_hoa`, tu 11/09)
# ghi cum nay la CAN HOI: "nguoi noi chua do nhiet do — khong tu doi thanh sot".
# Hai cho cua cung mot du an noi hai dieu, va phep cham dung ve phia sai: dau ra
# chep nguyen van "nong ham hap" bi tinh la khong can cu + bo sot, con dau ra doi
# thang thanh "sot, chac chan" — dung dieu bang chuan hoa cam — duoc tinh la dung.
#
# Tu nay menh de nao ma KHONG trich dan nao con tu chuan, chi con cum o day, thi
# noi dung ghi dung cum nguoi noi dung. Do chac chan GIU NGUYEN: nguoi noi khong
# ra dau nghi ngo, cai chua chac la phep doi tu chu khong phai loi ke. Cac cap
# con lai cua THAY_DUOC deu la CHAC trong `chuan_hoa`, van giu nghia chuan. Test
# `test_giu_nguyen_khop_chuan_hoa` bat khi hai bang lech nhau.
GIU_NGUYEN = {"nóng hầm hập"}


def _mau(cum):
    return re.compile(rf"(?<![\wÀ-ỹ]){re.escape(cum)}(?![\wÀ-ỹ])", re.I)


def giu_loi_nguoi_noi(noi_dung, trich_dan):
    """-> noi dung moi cua menh de (hoac chinh `noi_dung`). Xem GIU_NGUYEN.

    Chi doi khi ca ba dieu cung dung:
      1. noi dung co tu chuan (ca tu, khong phan biet hoa thuong);
      2. KHONG trich dan nao con tu chuan do — bac si hoi "co sot khong", hay
         "sot cao" bi CHAN_SAU giu lai, thi "sot" co can cu nguyen van;
      3. it nhat mot trich dan mang cum phuong ngu.
    """
    for cac in THAY_DUOC.values():
        for chuan, dia_phuong in cac:
            if dia_phuong not in GIU_NGUYEN:
                continue
            m_chuan = _mau(chuan)
            if (not m_chuan.search(noi_dung)
                    or any(m_chuan.search(t) for t in trich_dan)
                    or not any(_mau(dia_phuong).search(t) for t in trich_dan)):
                continue
            noi_dung = m_chuan.sub(
                lambda m: (dia_phuong[:1].upper() + dia_phuong[1:]
                           if m.group(0)[:1].isupper() else dia_phuong),
                noi_dung)
    return noi_dung


def ve_tu_chuan(noi_dung):
    """Nguoc cua `giu_loi_nguoi_noi`, CHI de so hai ban cua mot cap thu thach
    (`thach_thuc`): ban co phuong ngu ghi "nong ham hap", ban khong co ghi "sot",
    hai ban co y khac nhau dung o cho do."""
    for cac in THAY_DUOC.values():
        for chuan, dia_phuong in cac:
            if dia_phuong in GIU_NGUYEN:
                noi_dung = _mau(dia_phuong).sub(chuan, noi_dung)
    return noi_dung


def doi_sang_phuong_ngu(cau, vung, rng, ty_le=0.6):
    """Doi mot so tu chuan trong `cau` sang dang phuong ngu cua `vung`.

    -> (cau_moi, [cac cap da doi]). Tra ve ca danh sach da doi de bo sinh ghi
    lai duoc — khong ghi lai thi khong biet ca nao co phuong ngu, va khong do
    duoc rieng nhom do.

    `ty_le`: xac suat doi MOI cap tim thay. Khong doi het 100%: hoi thoai that
    tron ca hai cach noi, va neu doi het thi phep thu thanh "dich tu dien" chu
    khong con la "hieu cau co lan phuong ngu".
    """
    da_doi = []
    for chuan, dia_phuong in THAY_DUOC.get(vung, []):
        # Khong phan biet hoa thuong: "Hom kia" dau cau va "hom kia" giua cau
        # la mot tu. Ban dau khop phan biet hoa thuong, va hau qua la moi tu
        # dung o DAU CAU deu khong bao gio duoc doi — dung nhung cho de nhin
        # nhat, nen loi do rat de lot.
        mau = re.compile(rf"(?<![\wÀ-ỹ]){re.escape(chuan)}(?![\wÀ-ỹ])", re.I)
        m = mau.search(cau)
        if not m:
            continue
        # Ranh gioi TU khong phai ranh gioi TU GHEP — xem CHAN_SAU.
        sau = cau[m.end():].lstrip()
        tu_sau = re.split(r"[^\wÀ-ỹ]", sau, maxsplit=1)[0].lower()
        if tu_sau in CHAN_SAU.get(chuan, ()):
            continue
        if rng.random() > ty_le:
            continue
        # Giu chu hoa dau tu neu ban goc viet hoa.
        thay = dia_phuong
        if m.group(0)[:1].isupper():
            thay = dia_phuong[:1].upper() + dia_phuong[1:]
        cau = cau[:m.start()] + thay + cau[m.end():]
        da_doi.append((chuan, dia_phuong))
    return cau, da_doi


def bang_quy_chuan(tu_dien=None):
    """-> {tu phuong ngu (thuong): nghia chuan}. Dung cho phep cham va cho
    buoc loc cap ung vien, de "nong ham hap" ghep duoc voi "sot".

    GHI CHU 24/09/2026: khong noi nao trong `src` goi ham nay nua. Phep cham va
    duong ong dung `chuan_hoa`, noi do "nong ham hap" la CAN HOI (`GIU_NGUYEN`)."""
    tu_dien = tu_dien if tu_dien is not None else nap()
    ra = {}
    for cap in THAY_DUOC.values():
        for chuan, dia_phuong in cap:
            ra[dia_phuong.lower()] = chuan
    for cac in tu_dien.values():
        for tu, nghia in cac:
            ra.setdefault(tu.lower(), nghia)
    return ra
