# -*- coding: utf-8 -*-
"""Nhieu ASR — lam ban ghi loi thoai giong dau ra may nhan dang tieng noi.

VI SAO CAN TRUC NAY. Bo du lieu tu sinh dang co la van ban SACH: du dau, du dau
cau, viet hoa dung cho. Hoi thoai kham that khong den duoi dang do — no den qua
mot may nhan dang tieng noi, va cai ra la van ban mat dau, mat dau cau, ngat cau
sai cho. Neu khong bao gio do tren dang do thi moi ket luan cua du an chi dung
cho mot dang dau vao khong ton tai.

RANG BUOC CUNG: NHIEU KHONG DUOC DOI DAP AN. Bo nay do "he thong con hieu dung
khong khi chu xau di", chu khong do "he thong doan duoc chu bi xoa". Nen phep
lam nhieu o day:

  1. GIU NGUYEN SO TU. Moi tu vao mot tu ra. Nho the, doan trich dan trong dap an
     anh xa lai duoc theo CHI SO TU, va `khoa_bang_chung` van kiem duoc K1.
  2. KHONG DUNG TOI TU CHI NGUOI, TU PHU DINH VA TU SO. Bo dau nhung tu nay la
     DOI SU THAT chu khong phai lam nhieu:
         "ba"  -> "ba"   ba bien thanh ba — dung loi quy gan cua du an
         "me"  -> "me"   me lan voi "me" trong "me con"
         "nam" -> "nam"  nam (so 5) lan voi nam (gioi tinh, mien Nam)
         "khong" -> "khong"  con doc ra duoc, nhung mot chu sai la mat phu dinh
     Bo qua ba nhom nay la cach duy nhat giu dap an con dung sau khi lam nhieu.

VI SAO KHONG DUNG BANG DONG AM. Cam do la doi "sot" -> "xot", "chuan" -> "chan".
Nhung khi do he thong PHAI doan nguoc lai, ma khong phai luc nao nguoi that cung
doan duoc — phep thu se do mot thu khong ai giai duoc, va so lieu thu ve khong
noi len dieu gi. Hai hien tuong o day (mat dau, mat dau cau) thi nguoi doc nao
cung khoi phuc duoc tu ngu canh, nen chung do dung cai can do.

CHI DUNG O TAP DANH GIA. Khong khau huan luyen nao goi tep nay — xem
`tests/test_nhieu_asr.py`. Cung mot le voi bang phuong ngu: neu bo sinh va he
thong cung biet mot bang, phep thu chi do "he thong co ap dung dung bang cua no".
"""
import re
import unicodedata

from src.thuoc_do_quy_gan import (
    TU_BENH_NHAN,
    TU_NGUOI_NHA,
    TU_NGUOI_NHA_KHONG_NHAN_DIEN,
)

# Tu so va tu chi thoi gian: bo dau la doi gia tri hoac lan nghia.
TU_SO = (
    "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín", "mười",
    "mươi", "trăm", "nghìn", "rưỡi", "nửa", "vài",
)
TU_PHU_DINH = ("không", "chưa", "chẳng", "đừng", "khỏi", "hết", "còn")
TU_THOI_GIAN = ("hôm", "ngày", "tuần", "tháng", "năm", "giờ", "sáng", "chiều",
                "tối", "đêm", "trưa", "nay", "qua", "kia", "mai", "mốt")

# MOT bang duy nhat cho ca tep. Gom tu ba bang da co trong du an thay vi go lai:
# hai bang cung nghia o hai tep la cach chung troi nhau (bai hoc da ghi trong
# `phat_bieu`).
TU_CAM = frozenset(
    t
    for nhom in (TU_BENH_NHAN, TU_NGUOI_NHA, TU_NGUOI_NHA_KHONG_NHAN_DIEN,
                 TU_SO, TU_PHU_DINH, TU_THOI_GIAN)
    for cum in nhom
    for t in cum.split()
)

DAU_CAU = ",.?!;:"
_CHU = re.compile(r"[^\W\d_]", re.UNICODE)


def bo_dau(tu: str) -> str:
    """Bo toan bo dau tieng Viet, ke ca `d` -> `d`. Giu nguyen dau cau di kem."""
    tach = unicodedata.normalize("NFD", tu)
    khong_dau = "".join(c for c in tach if not unicodedata.combining(c))
    return unicodedata.normalize("NFC", khong_dau).replace("đ", "d").replace("Đ", "D")


def bo_dau_cau(van: str) -> str:
    """Bo dau cau, NHUNG giu dau phay/cham nam giua hai chu so.

    "38,5 do" ma bo dau phay thi thanh "385 do" — do la DOI GIA TRI, dung cai ma
    tep nay cam. Bay nay xuat hien ngay lan chay thu dau tien, va no khong lo ra
    o cho nao khac: cau van van doc troi, chi co con so la sai.
    """
    ra = []
    for i, c in enumerate(van):
        if c in DAU_CAU:
            truoc = van[i - 1] if i else ""
            sau = van[i + 1] if i + 1 < len(van) else ""
            if c in ",." and truoc.isdigit() and sau.isdigit():
                ra.append(c)
            continue
        ra.append(c)
    return "".join(ra)


def _goc(tu: str) -> str:
    """Phan chu cua mot tu, bo dau cau hai dau — de tra bang TU_CAM."""
    return tu.strip(DAU_CAU + '"“”‘’()').lower()


def cam_dung(tu: str) -> bool:
    """Tu nay co thuoc nhom KHONG duoc dung toi khong."""
    g = _goc(tu)
    return (not g) or (g in TU_CAM) or any(c.isdigit() for c in g)


def nhieu_tu(tu: str, rng, ti_le: float) -> str:
    """Mot tu -> mot tu. Bo dau theo xac suat, tru cac tu trong TU_CAM."""
    if cam_dung(tu) or not _CHU.search(tu):
        return tu
    return bo_dau(tu) if rng.random() < ti_le else tu


def nhieu_dong(dong: str, rng, ti_le: float = 0.5,
               xoa_dau_cau: bool = True) -> str:
    """Lam nhieu MOT luot thoai, giu nguyen nhan vai o dau dong.

    Nhan vai ("Bac si:", "Benh nhan:") la thu bo sinh dat ra de danh so luot,
    khong phai loi ai noi — may nhan dang khong sinh ra no, va `khoa_bang_chung`
    dua vao no de biet ai noi. Lam nhieu cho do la pha cong cu do, khong phai lam
    kho bai toan.
    """
    vai, ngan, than = dong.partition(": ")
    if not ngan:
        vai, than = "", dong

    tu = than.split(" ")
    ra = [nhieu_tu(t, rng, ti_le) for t in tu]
    assert len(ra) == len(tu), "phep lam nhieu phai giu nguyen so tu"

    van = " ".join(ra)
    if xoa_dau_cau:
        # Bo dau cau va viet thuong chu dau: dau ra ASV thuong khong co ca hai.
        van = bo_dau_cau(van)
        van = re.sub(r"\s{2,}", " ", van).strip()
        if van:
            van = van[0].lower() + van[1:]
    return f"{vai}{ngan}{van}" if ngan else van


def nhieu_trich(trich: str, dong_goc: str, dong_nhieu: str):
    """Doan trich dan trong dap an -> doan tuong ung trong ban da lam nhieu.

    Tra `None` khi doan khong nam trong dong nay — de ben goi con biet ma thu
    dong khac. Tra nguyen doan cu thi khong phan biet duoc "tim thay ma khong
    doi gi" voi "khong tim thay", va lan chay thu dau tien da sai dung cho do.

    Anh xa theo CHI SO TU, dung duoc vi phep lam nhieu giu nguyen so tu. So khop
    sau khi BOC DAU CAU hai dau moi tu: dap an trich "… rồi rồi" con loi thoai
    ghi "… rồi rồi." — dinh dau cham o tu cuoi la du de truot ca doan.
    """
    def than(d):
        _, ngan, t = d.partition(": ")
        return (t if ngan else d).split(" ")

    def boc(ds):
        return [t.strip(DAU_CAU) for t in ds]

    tu_goc, tu_nhieu = than(dong_goc), than(dong_nhieu)
    if len(tu_goc) != len(tu_nhieu):
        return None

    goc_boc, tu_trich = boc(tu_goc), boc(trich.split(" "))
    n = len(tu_trich)
    for i in range(len(goc_boc) - n + 1):
        if goc_boc[i:i + n] == tu_trich:
            return bo_dau_cau(" ".join(tu_nhieu[i:i + n])).strip()
    return None


def nhieu_ca(ca: dict, rng, ti_le: float = 0.5) -> dict:
    """Mot ca -> ban da lam nhieu. `dap_an` giu nguyen, tru `trich_dan` duoc anh
    xa sang chu da nhieu de van doi chieu duoc voi hoi thoai."""
    dong_goc = ca["input"].split("\n")
    dong_nhieu = [nhieu_dong(d, rng, ti_le) if d.strip() else d for d in dong_goc]

    dap_an = []
    for m in ca["dap_an"]:
        m = dict(m)
        if m.get("trich_dan"):
            moi = []
            for t in m["trich_dan"]:
                d = next(
                    (x for g, n in zip(dong_goc, dong_nhieu)
                     if (x := nhieu_trich(t, g, n)) is not None),
                    t,
                )
                moi.append(d)
            m["trich_dan"] = moi
        dap_an.append(m)

    moi_ca = dict(ca)
    moi_ca["input"] = "\n".join(dong_nhieu)
    moi_ca["dap_an"] = dap_an
    return moi_ca
