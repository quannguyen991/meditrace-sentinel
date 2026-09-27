# -*- coding: utf-8 -*-
"""Bon bai kiem tra "dat" — sinh bang LUAT, tren khuon cua MOT tap.

  doi_chu_the  CAP ca giong het nhau, chi DAO nguoi mang di ung: nguoi nha <->
               benh nhan. Ho so phai doi theo, va phai dung o CA HAI ban.
  phuong_ngu   CAP ca giong het nhau, mot ban co tu phuong ngu, mot ban khong.
               Trang thai ho so phai GIONG NHAU. Noi dung cung vay, tru cum
               khong dong nghia ("nong ham hap" / "sot", tu 24/09/2026).
  dinh_chinh   ca mang mot bay cap nhat: dinh chinh, mau thuan, dien bien, bo
               sung, hai nguon khac nhau. Do trang thai CUOI CUNG.
  dan_gian     CAP: ban goc va CHINH ban do voi loi benh nhan doi sang cach noi dia
               phuong / dan gian / an du lay tu tu dien that (`dan_gian`). Dap an
               giong het tru `trich_dan`. Them 24/09/2026, chi sinh khi goi ro
               `--chi dan_gian`.
  nhieu_asr    CAP: ban sach va CHINH ban do da lam nhieu nhu dau ra may nhan
               dang tieng noi (mat dau, mat dau cau). Trang thai ho so phai
               GIONG NHAU — xem `nhieu_asr` de biet vi sao nhieu khong duoc
               dung toi tu chi nguoi, tu so va tu phu dinh.

VI SAO LA CAP. Mot con so tren tap thuong khong tach duoc "he thong hieu chu
the" voi "he thong doan trung": duong tat "chu the = nguoi noi" dung o phan lon
luot. Hai ban chi khac DUNG mot dieu thi moi duong tat deu lo ra — doan theo
nguoi noi thi dung mot ban va sai ban kia.

KHONG DUNG MO HINH NGON NGU. Ca ba bo sinh tu `sinh_hoi_thoai_viet` bang tuy
chon (`TuyChon`) — rang buoc so 1 cua du an ap cho ca bai kiem tra.

CHI SINH TREN KHUON CUA MOT TAP: bai kiem tra tren khuon da hoc la do "nho",
khong phai do "hieu". Tap kiem tra cuoi chi sinh luc khoa thiet ke — chot
`du_lieu.chan_tap_khoa` chan ca o day.

    python -m src.thach_thuc --khuon-tap phat_trien --the-he 5
"""
import argparse
import hashlib
import io
import json
import random
import sys

from src import dan_gian, du_lieu, duong_dan, nhieu_asr, van_tay_bo
from src import sinh_hoi_thoai_viet as sh

THACH_THUC = ("doi_chu_the", "phuong_ngu", "dinh_chinh", "nhieu_asr", "dan_gian")
BAY_CAP_NHAT = ("dinh_chinh", "mau_thuan", "dien_bien", "bo_sung",
                "nguon_khac_nhau")
# Moi cap / moi ca thu toi da bay nhieu hat. Qua so nay la tuy chon khong the
# dat duoc — bao loi thay vi lang le tra ve it ca hon.
SO_LAN_THU_TOI_DA = 60


def _hat(*phan):
    s = ":".join(str(x) for x in phan)
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:12], 16)


def _luot(ca):
    return [d for d in ca["input"].split("\n") if d.strip()]


def bo_trich_dan(dap_an):
    """Dap an bo `trich_dan`. Hai ban cua cap phuong ngu KHAC CHU nen trich dan
    phai khac; moi truong con lai phai giong het."""
    return [{k: v for k, v in d.items() if k != "trich_dan"} for d in dap_an]


def cap_doi_chu_the(tap, so_cap, seed=42):
    """-> 2*so_cap ca. Ban A: nguoi nha di ung, benh nhan "chua thay bi bao
    gio". Ban B: cung cau do, DAO hai nguoi. Chi DUNG MOT luot khac nhau."""
    ra = []
    for i in range(so_cap):
        for thu in range(SO_LAN_THU_TOI_DA):
            h = _hat("doi_chu_the", seed, tap, i, thu)
            chung = dict(chi_tap=tap, ep_bay=("di_ung_nguoi_nha",),
                         ep_nguoi_ke=True, di_ung_cua_nguoi_ke=True)
            a = sh.sinh_mot_ca(f"dct_{i:03d}_A", random.Random(h),
                               sh.TuyChon(**chung))
            b = sh.sinh_mot_ca(f"dct_{i:03d}_B", random.Random(h),
                               sh.TuyChon(**chung, doi_chu_the=True))
            la, lb = _luot(a), _luot(b)
            khac = [j for j, (x, y) in enumerate(zip(la, lb)) if x != y]
            if len(la) == len(lb) and len(khac) == 1:
                break
        else:
            raise RuntimeError(f"khong sinh duoc cap doi chu the thu {i}")
        for x, bien_the in ((a, "A"), (b, "B")):
            x.update(thach_thuc="doi_chu_the", cap=i, bien_the=bien_the,
                     luot_khac=khac[0] + 1)
        ra += [a, b]
    return ra


# Cap phuong ngu can NHIEU lan thu hon: bang thay cua mien Trung chi co 4 cap tu
# ("hom kia", "dao nay", "bay gio", "tre em"), nen phan lon ca mien Trung KHONG
# mang tu phuong ngu nao. Lan chay dau ngay 11/09/2026: cap thu 9 (mien Trung)
# truot ca 60 lan thu.
SO_LAN_THU_PHUONG_NGU = 800


def _so_cap_phuong_ngu(dap_an):
    """`bo_trich_dan`, roi tra cum giu nguyen loi nguoi noi ve tu chuan.

    Tu 24/09/2026 ban A noi "nong ham hap" thi dap an A ghi dung cum do
    (`phuong_ngu.GIU_NGUYEN`), ban B noi "sot" thi ghi "sot": hai ban CO Y khac
    nhau o dung cho do. Moi truong con lai van phai giong het, va so bang ham nay
    thi cac cap cu van duoc nhan y nhu truoc — khong cap nao bi sinh lai."""
    from src import phuong_ngu
    ra = bo_trich_dan(dap_an)
    for d in ra:
        d["noi_dung"] = phuong_ngu.ve_tu_chuan(d["noi_dung"])
    return ra


def cap_phuong_ngu(tap, so_cap, seed=42):
    """-> 2*so_cap ca. Ban A co tu phuong ngu, ban B tat tang vung. Dap an phai
    giong het tru `trich_dan`, va tru noi dung mang cum giu nguyen loi nguoi noi
    (`_so_cap_phuong_ngu`)."""
    ra = []
    for i in range(so_cap):
        mien = ("nam", "trung")[i % 2]
        for thu in range(SO_LAN_THU_PHUONG_NGU):
            h = _hat("phuong_ngu", seed, tap, i, thu)
            chung = dict(chi_tap=tap, ep_mien=mien)
            a = sh.sinh_mot_ca(f"png_{i:03d}_A", random.Random(h),
                               sh.TuyChon(**chung))
            b = sh.sinh_mot_ca(f"png_{i:03d}_B", random.Random(h),
                               sh.TuyChon(**chung, ap_phuong_ngu=False))
            if (a["tu_phuong_ngu"] and not b["tu_phuong_ngu"]
                    and len(_luot(a)) == len(_luot(b))
                    and _so_cap_phuong_ngu(a["dap_an"]) == _so_cap_phuong_ngu(b["dap_an"])):
                break
        else:
            raise RuntimeError(f"khong sinh duoc cap phuong ngu thu {i}")
        for x, bien_the in ((a, "A"), (b, "B")):
            x.update(thach_thuc="phuong_ngu", cap=i, bien_the=bien_the)
        ra += [a, b]
    return ra


def cap_nhieu_asr(tap, so_cap, seed=42, ti_le=0.5):
    """-> 2*so_cap ca. Ban A la ban SACH, ban B la chinh ban do da lam nhieu nhu
    dau ra may nhan dang tieng noi. Dap an giong het tru `trich_dan`.

    KHAC BA BO KIA MOT DIEM: hai bo tren sinh HAI ca roi doi mot dieu, con o day
    chi sinh MOT ca roi lam xau chu cua chinh no. Lam vay vi nhieu ASR la thu xay
    ra SAU khi nguoi ta noi — no khong doi noi dung buoi kham, chi doi ban ghi.
    Sinh hai ca roi lam nhieu mot ban thi hai ban da khac nhau tu truoc, va phep
    thu mat y nghia.
    """
    ra = []
    for i in range(so_cap):
        h = _hat("nhieu_asr", seed, tap, i)
        a = sh.sinh_mot_ca(f"asr_{i:03d}_A", random.Random(h),
                           sh.TuyChon(chi_tap=tap))
        b = nhieu_asr.nhieu_ca(a, random.Random(h ^ 0x5A5A), ti_le)
        b["id"] = f"asr_{i:03d}_B"
        if bo_trich_dan(a["dap_an"]) != bo_trich_dan(b["dap_an"]):
            raise RuntimeError(f"lam nhieu da doi dap an o cap {i}")
        for x, bien_the in ((a, "A"), (b, "B")):
            x.update(thach_thuc="nhieu_asr", cap=i, bien_the=bien_the,
                     ti_le_nhieu=ti_le)
        ra += [a, b]
    return ra


SO_LAN_THU_DAN_GIAN = 3000


def _luot_chen(input_):
    """-> so luot (dem tu 1) cua luot benh nhan / nguoi nha DAU TIEN sau luot 1, hoac
    None. Chen vao cuoi luot nen moi trich dan cu cua luot do van la chuoi con."""
    so = 0
    for d in input_.split("\n"):
        if not d.strip():
            continue
        so += 1
        m = dan_gian._DONG.match(d)
        if so > 1 and m and not dan_gian._la_bac_si(m.group(2)):
            return so
    return None


def cap_dan_gian(tap, so_cap, seed=42):
    """-> 2*so_cap ca. Ban A la ca goc, ban B la CHINH ca do voi loi benh nhan va
    nguoi nha doi sang cach noi dan gian (`dan_gian.BANG`). Dap an giong het tru
    `trich_dan`.

    Giong `cap_nhieu_asr`: sinh MOT ca roi doi chu, khong sinh hai ca — hai ban chi
    khac nhau o cach noi, khong khac noi dung buoi kham.

    Ep phan bo theo vong 3 cap, vi cum mo ho hiem (duoi 6% ca cua khuon phat trien):
      i % 3 == 0  co it nhat mot cho MO_HO
      i % 3 == 1  co it nhat mot cho KHONG nam trong bang chuan hoa (giu lai)
      i % 3 == 2  co CHEN mot cau "gio" (`dan_gian.CHEN`, xen ke hai cau)
    Moi cap co it nhat HAI cho doi (tinh ca cau chen).
    """
    ra = []
    for i in range(so_cap):
        for thu in range(SO_LAN_THU_DAN_GIAN):
            h = _hat("dan_gian", seed, tap, i, thu)
            a = sh.sinh_mot_ca(f"dgn_{i:03d}_A", random.Random(h),
                               sh.TuyChon(chi_tap=tap))
            chen = None
            if i % 3 == 2:
                so = _luot_chen(a["input"])
                if so is None:
                    continue
                chen = (so, dan_gian.CHEN[(i // 3) % len(dan_gian.CHEN)][0])
            vao, cho = dan_gian.doi_hoi_thoai(a["input"], chen)
            loai = {c["loai"] for c in cho}
            if len(cho) < 2:
                continue
            if i % 3 == 0 and dan_gian.MO_HO not in loai:
                continue
            if i % 3 == 1 and not any(not c["trong_bang"] and c["loai"] != "chen"
                                      for c in cho):
                continue
            break
        else:
            raise RuntimeError(f"khong sinh duoc cap dan gian thu {i}")
        b = dict(a, id=f"dgn_{i:03d}_B", input=vao,
                 dap_an=dan_gian.doi_trich_dan(a["dap_an"], a["input"]))
        if bo_trich_dan(a["dap_an"]) != bo_trich_dan(b["dap_an"]):
            raise RuntimeError(f"doi chu da doi dap an o cap {i}")
        a.update(thach_thuc="dan_gian", cap=i, bien_the="A", cho_dan_gian=[])
        b.update(thach_thuc="dan_gian", cap=i, bien_the="B", cho_dan_gian=cho)
        ra += [a, b]
    return ra


def bo_dinh_chinh(tap, so_ca, seed=42):
    """-> so_ca ca, lan luot mang tung bay trong BAY_CAP_NHAT."""
    ra = []
    for i in range(so_ca):
        bay = BAY_CAP_NHAT[i % len(BAY_CAP_NHAT)]
        for thu in range(SO_LAN_THU_TOI_DA):
            h = _hat("dinh_chinh", seed, tap, i, thu)
            ca = sh.sinh_mot_ca(
                f"dch_{i:03d}", random.Random(h),
                sh.TuyChon(chi_tap=tap, ep_bay=(bay,),
                           ep_nguoi_ke=(bay == "nguon_khac_nhau")))
            if bay in ca["bay"]:
                break
        else:
            raise RuntimeError(f"khong sinh duoc ca mang bay {bay}")
        ca.update(thach_thuc="dinh_chinh", bay_chinh=bay)
        ra.append(ca)
    return ra


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    # `--khuon-tap`, KHONG phai `--tap`: day la TAP KHUON de rut benh, khong
    # phai ten tep du lieu. Dat ten `--tap` voi mac dinh "phat_trien" thi trung
    # ten mot tap cua cuoc thi cu, va `test_chan_tap_ngoai` bat dung dieu do.
    ap.add_argument("--khuon-tap", default="phat_trien",
                    choices=("phat_trien", "kiem_tra_cuoi"))
    ap.add_argument("--so-cap", type=int, default=40)
    ap.add_argument("--so-ca-dinh-chinh", type=int, default=60)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--ti-le-nhieu", type=float, default=0.5,
                    help="ti le tu bi bo dau trong bo nhieu ASR")
    ap.add_argument("--the-he", required=True)
    ap.add_argument("--chi", nargs="+", choices=THACH_THUC,
                    help="chi sinh cac bo nay; mac dinh bon bo cu (khong gom dan_gian), "
                         "de lenh cu chay lai ra dung tep cu")
    a = ap.parse_args()
    du_lieu.chan_tap_khoa(a.khuon_tap)

    tap = a.khuon_tap
    sinh = {"doi_chu_the": lambda: cap_doi_chu_the(tap, a.so_cap, a.seed),
            "phuong_ngu": lambda: cap_phuong_ngu(tap, a.so_cap, a.seed),
            "dinh_chinh": lambda: bo_dinh_chinh(tap, a.so_ca_dinh_chinh, a.seed),
            "nhieu_asr": lambda: cap_nhieu_asr(tap, a.so_cap, a.seed, a.ti_le_nhieu),
            "dan_gian": lambda: cap_dan_gian(tap, a.so_cap, a.seed)}
    chon = a.chi or [t for t in THACH_THUC if t != "dan_gian"]
    bo = {ten: sinh[ten]() for ten in chon}
    d = duong_dan.THU_MUC_DU_LIEU
    for ten, ds in bo.items():
        dp = d / f"thach_thuc_{ten}_{tap}.jsonl"
        dp.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in ds),
                      encoding="utf-8")
        van_tay_bo.ghi(dp, ds, a.the_he, hat=a.seed,
                       ghi_chu=f"thach thuc {ten}, khuon cua tap {tap}")
        print(f"{dp.name:48} {len(ds):4d} ca")


if __name__ == "__main__":
    main()
