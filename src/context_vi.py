# -*- coding: utf-8 -*-
"""Doi chung theo LUAT cho truc chu the, dung theo loi ConText — tieng Viet.

VI SAO CO (16/09/2026). ConText (Harkema, Chapman va cong su, 2009) co truc
`Experiencer` voi hai gia tri `patient` / `other`, chay bang mot danh sach tu kich
hoat cong pham vi anh huong tinh tu cho tu kich hoat den het cau. Do la tien le
truc tiep cua truc chu the trong du an nay, nen phai co mot ban tieng Viet de doi
chieu: mo hinh dong gop bao nhieu SO VOI mot bang tu.

ConText dung 26 tu kich hoat va 18 tu kich hoat GIA cho gia tri `other`. Ban nay
nho hon vi bo sinh chi dung mot so vai nguoi nha co dinh.

BA BO PHAN, dung nhu ConText:

  tu kich hoat   tu chi NGUOI NHA ("bố", "mẹ", "bà ngoại"...) -> thong tin la cua
                 nguoi do, khong phai cua benh nhan
  kich hoat GIA  cung tu do nhung trong vai NGUOI DUA DI KHAM hoac NGUOI KE, khong
                 phai nguoi mang benh: "mẹ đưa cháu đi khám", "bà kể là cháu ho".
                 Khong co bo phan nay thi moi cau nguoi nha ke ho deu bi gan sai.
  het pham vi    dau cau, va cac lien tu doi lap ("còn", "nhưng") — "bà ngoại thì dị
                 ứng penicillin, còn cháu chưa bị bao giờ" doi chu the giua chung cau

GIOI HAN PHAI GHI VAO BAO CAO. Bang tu nay chon tu VAI NGUOI NHA ma bo sinh dung
(`ngu_lieu_viet.NGUOI_NHA`, `VAI_NU`, `VAI_NAM`), KHONG chon bang cach nhin vao tap
danh gia. Mot bang tu chon tu chinh tap danh gia se cho mot con so cao gia.
"""
import re

from src import chuan_hoa

# Tu chi nguoi nha — tu kich hoat. Lay tu cac vai bo sinh that su dung.
TU_NGUOI_NHA = (
    "bà ngoại", "bà nội", "ông ngoại", "ông nội", "anh trai", "chị gái",
    "em trai", "em gái", "con trai", "con gái", "bố", "mẹ", "ba", "má",
    "vợ", "chồng",
)

# KHONG dua vao bang: "ba", "ong", "anh", "chi", "chau", "con" DUNG MOT AM. Trong
# hoi thoai kham tieng Viet do la cach goi CHINH BENH NHAN, khong phai nguoi nha —
# do tren 681 ca cua chinh kho nay (bang dem o `doi_chung_tam_thuong.TU_XUNG_MINH`):
# "chau" 438 lan chi benh nhan so voi 5 lan chi nguoi noi, "ba" 98 so voi 9, "ong"
# 78 so voi 9. Ban dau toi CO dua chung vao, va do duoc tren bo doi chu the ngay
# 16/09/2026: ty le sai chu the tren menh de ghep duoc la 20,00%, TE HON ca duong
# "luon gan cho benh nhan" (13,14%). Day dung la cho ConText khong chuyen thang sang
# tieng Viet duoc: tieng Anh khong goi benh nhan bang tu than toc.

# Dong tu lam cho tu chi nguoi nha thanh NGUOI DUA DI hoac NGUOI KE, khong phai
# nguoi mang benh. Xet trong mot cua so ngan ngay sau tu kich hoat.
DONG_TU_KICH_HOAT_GIA = (
    "đưa", "dẫn", "chở", "bế", "ẵm", "kể", "nói", "bảo", "trình bày", "hỏi",
    "thấy", "sờ", "đo", "nhắc",
    # "cho" mot minh: trong "bố cho cháu uống hạ sốt", nguoi nha la nguoi CHO, con
    # nguoi uong la benh nhan. Rong hon cac tu tren nhung van la vai tac nhan.
    "cho",
)

# Het pham vi anh huong: dau cau, hoac lien tu doi lap.
LIEN_TU_DOI_LAP = ("còn", "nhưng", "riêng")

_CUA_SO_TU = 4          # so tu sau tu kich hoat con xet la kich hoat gia


def _tach_pham_vi(cau: str):
    """Cat mot menh de thanh cac PHAM VI: dau phay, dau cham, va lien tu doi lap."""
    tho = re.split(r"[.;,?!]", cau)
    ra = []
    for phan in tho:
        con = [phan]
        for lt in LIEN_TU_DOI_LAP:
            moi = []
            for x in con:
                moi.extend(re.split(rf"(?<!\w){lt}(?!\w)", x))
            con = moi
        ra.extend(c.strip() for c in con if c.strip())
    return ra


def _kich_hoat(pham_vi: str):
    """-> (tu kich hoat, co phai kich hoat gia) hoac (None, False)."""
    t = chuan_hoa.chuan_hoa(pham_vi).lower()
    tim = None
    for tu in sorted(TU_NGUOI_NHA, key=len, reverse=True):
        m = re.search(rf"(?<!\w){re.escape(tu)}(?!\w)", t)
        if m and (tim is None or m.start() < tim[1]):
            tim = (tu, m.start(), m.end())
    if tim is None:
        return None, False
    tu, _a, b = tim
    sau = t[b:].split()[:_CUA_SO_TU]
    doan_sau = " ".join(sau)
    gia = any(re.search(rf"(?<!\w){re.escape(d)}(?!\w)", doan_sau)
              for d in DONG_TU_KICH_HOAT_GIA)
    return tu, gia


def chu_the_cua(cau: str, vai_nguoi_noi: str = "") -> int:
    """-> 0 neu menh de noi VE BENH NHAN, 1 neu noi ve mot nguoi khac.

    Luat, theo thu tu:
      1. Co tu chi nguoi nha va KHONG phai kich hoat gia -> nguoi khac.
      2. Con lai -> benh nhan. Ke ca khi nguoi nha dang noi: nguoi nha ke HO la
         truong hop thuong gap nhat, va ConText cung mac dinh `patient`.
    """
    for pv in _tach_pham_vi(cau):
        tu, gia = _kich_hoat(pv)
        if tu and not gia:
            return 1
    return 0


def ten_chu_the_cua(cau: str):
    """-> TU KICH HOAT da lam doi chu the ("bà ngoại"), hoac None neu la benh nhan.

    Can rieng ham nay vi bo cham doi chieu ca DANH TINH: ghi "người nhà" trong khi
    dap an ghi "anh trai" van la sai chu the (xem `cham_he_thong.dung_nguoi`). Truoc
    khi co ham nay, duong doi chung ghi ten theo VAI NGUOI NOI nen moi menh de ve
    nguoi nha deu mang ten "người nhà" — 22/68 loi chu the ngay 16/09/2026 la vi the.
    """
    for pv in _tach_pham_vi(cau):
        tu, gia = _kich_hoat(pv)
        if tu and not gia:
            return tu
    return None


def giai_thich(cau: str) -> list:
    """-> [(pham vi, tu kich hoat, la kich hoat gia)] — de doc lai khi cham tay."""
    return [(pv,) + _kich_hoat(pv) for pv in _tach_pham_vi(cau)]
