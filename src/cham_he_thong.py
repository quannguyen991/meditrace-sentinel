# -*- coding: utf-8 -*-
"""Cham DAU RA THAT cua duong ong tren dap an cau truc: nhanh B, C, C_khoa, C_khoa_hoi.

Khac `danh_gia_khoa` (chay tang khoa tren DAP AN — do gia cua tang khoa), tep nay
doi chieu tung phat bieu ma duong ong da trich (truong `phat_bieu` cua tep
ra_<nhanh>_<tap>.jsonl, co tu 11/09/2026) voi dap an cua bo tu sinh.

BON LOI tren phat bieu VAO THAN ho so (khong xuong CAN XAC NHAN), va bo sot:

  sai_chu_the    ghep duoc dap an nhung sai nguoi (benh nhan <-> nguoi khac)
  sai_muc        sai MUC KHANG DINH: chac / nghi / chua ghi nhan / phu dinh /
                 gia dinh / ke hoach. Tach thanh ba ma con (22/09/2026), xem
                 MA_CON_MUC
  sai_thoi_gian  (22/09/2026) qua khu <-> hien tai, hoac hai moc thoi gian khong
                 khop. "chưa rõ" hay thieu moc o mot ben KHONG tinh
  ban_cu         dap an noi ban nay DA BI THAY hoac CON MAU THUAN, ma no vao than
  khong_can_cu   khong ghep duoc menh de dap an nao — bia, hoac noi qua loi
  sai_thuoc      (15/09/2026) ghep duoc, nhung chi tiet thuoc (lieu, so lan, duong
                 dung, luc bat dau, luc ngung, trang thai dung) KHAC dap an — ke ca
                 ghi mot chi tiet dap an de trong, tuc la bia
  bo_sot         menh de dap an le ra vao than ma khong phat bieu than nao ghep duoc

Moi loi con tinh rieng cho DI UNG, THUOC, CHAN DOAN — ba loai `cong_rui_ro` xep
nghiem trong nhat.

GHEP: noi dung da chuan hoa phuong ngu, F1 tren tap tu, nguong 0,6 — CUNG nguong
voi phep do khau trich (`do_trich`). Moc thoi gian chi de xep hang: hai ban "sot"
(4 ngay bi thay, 2 ngay con hieu luc) phai ghep dung ban. Ghep truot thi mot loi
thanh hai (khong_can_cu + bo_sot): so loi CAO hon that, va nhu nhau giua cac nhanh.

KHOANG TIN CAY: ty so TONG, bootstrap cum THEO KHUON. Tap phat trien co 13 khuon;
ca khong phai don vi doc lap (`sai_so`).

DOI CHUNG BAT BUOC — bai hoc cua `duong_danh_doi` (07/09/2026):
  - danh dau (khoa + rui ro): so voi DANH DAU NGAU NHIEN cung so luong trong cung
    ca. Ky vong cua doi chung tinh DONG: k*e/n moi ca, khong phai rut ngau nhien.
  - hoi lai: so voi hoi NGAU NHIEN cung so phat bieu. Nguoi tra loi mo phong la
    HOAN HAO — con so la TRAN TREN, phai ghi ro moi lan dung.

    python -m src.cham_he_thong --tap viet_phat_trien --nhanh C C_khoa C_khoa_hoi
"""
import argparse
import io
import json
import random
import re as _re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from src import chuan_hoa, cong_rui_ro, duong_dan, sai_so, sinh_benh_an
from src.do_trich import NGUONG_GHEP, do_giong

LOI = ("sai_chu_the", "sai_muc", "ban_cu", "khong_can_cu", "sai_thuoc",
       "sai_thoi_gian")

# Ba MA CON cua `sai_muc` (22/09/2026). `sai_muc` la "sai MUC KHANG DINH" — gop
# chung muc chac chan, phu dinh va tinh huong (thuc te / gia dinh / ke hoach).
# Ma con chi TACH `sai_muc` ra xem sai o truc nao; chung KHONG nam trong LOI, nen
# mot menh de khong bi dem loi hai lan.
MA_CON_MUC = ("sai_muc_chac_chan", "sai_muc_phu_dinh", "sai_muc_tinh_huong")

# Phien ban bo cham. Doi moi lan them hay doi dinh nghia mot ma loi — so lieu cua
# hai phien ban KHONG so thang duoc voi nhau. Ghi vao moi tep ket qua.
#   2026-09-20  them do_chinh_xac, do_phu, f1, ser, sai_chu_the_tren_gold
#   2026-09-22  them ma loi sai_thoi_gian (truoc do KHONG cham thoi gian); tach
#               sai_muc thanh ba ma con; `_muc` hieu tu phu dinh dau cau; them
#               phu dinh lam tieu chi pha the hoa khi ghep
PHIEN_BAN = "2026-09-22"

# Tu mo dau cau lam dao nghia. "không sốt" (phu_dinh=False) va "sốt"
# (phu_dinh=True) la CUNG mot y — so co phu dinh tran se dem loi oan.
_TU_PHU_DINH = _re.compile(r"^\s*(không|chưa|chẳng|ko)\b", _re.I)


def _phu_dinh_that(x) -> bool:
    """Phu dinh co hieu luc = co `phu_dinh` XOR noi dung mo dau bang tu phu dinh."""
    return bool(x.get("phu_dinh")) != bool(_TU_PHU_DINH.match(x.get("noi_dung") or ""))


# Hai gia tri thoi gian "chac" — "chưa rõ" o mot ben thi KHONG tinh la loi: noi
# "chua ro" khi dap an co moc la bo sot chi tiet, khong phai noi sai.
_THOI_GIAN_CHAC = ("hiện tại", "quá khứ")


def sai_thoi_gian(d, p) -> bool:
    """Loi thoi gian: (1) ca hai ben noi chac ma khac nhau (qua khu <-> hien tai),
    hoac (2) ca hai ben co moc thoi gian ma hai moc khong khop.
    Thieu moc o mot ben KHONG tinh — do la bo sot chi tiet."""
    a, b = d.get("thoi_gian_su_kien"), p.get("thoi_gian_su_kien")
    if a in _THOI_GIAN_CHAC and b in _THOI_GIAN_CHAC and a != b:
        return True
    ma, mb = _nd(d.get("moc_thoi_gian")), _nd(p.get("moc_thoi_gian"))
    return bool(ma and mb and do_giong(ma, mb) < NGUONG_GHEP)


LOAI_NGHIEM_TRONG = ("di_ung", "thuoc", "chan_doan")
CO_DANH_DAU = (cong_rui_ro.BI_CHAN, cong_rui_ro.NGUY_CO_CAO)


def _nd(x):
    # Bo cham biet CA cac cum dan gian giu lai (24/09/2026); duong ong thi khong —
    # do moi do duoc duong ong chiu cach noi chua gap. Cac cum do khong co trong du
    # lieu the he 8 nen moi so da bao cao khong doi (tests/test_dan_gian.py).
    return chuan_hoa.chuan_hoa(str(x or ""), gom_giu_lai=True)


def _muc(d):
    """(do chac chan, phu dinh, tinh huong). Phu dinh chi co nghia khi chac chan:
    "chua ghi nhan" bo qua phu dinh, giong `sinh_benh_an.dien_dat`."""
    dcc = d.get("do_chac_chan") or "chắc chắn"
    return (dcc, _phu_dinh_that(d) and dcc == "chắc chắn",
            d.get("tinh_huong") or "thực tế")


def _con_hieu_luc(d):
    return (d.get("trang_thai") or "còn hiệu lực") == "còn hiệu lực"


def _gold_vao_than(d):
    return _con_hieu_luc(d) and (d.get("tinh_huong") or "thực tế") != "giả định"


def _la_bn_gold(d):
    return d.get("chu_the") == "bệnh nhân"


# Cach mo hinh goi CHINH nguoi dang ke ma khong neu quan he. Dung khi dap an ghi
# "nguoi nha" — tuc loi thoai KHONG lo nguoi do la ai.
TEN_NGUOI_NHA_CHUNG = frozenset({"người nhà", "người kể", "tôi", "em", "cháu", ""})


def dung_nguoi(d, p) -> bool:
    """Phat bieu co gan DUNG NGUOI voi menh de dap an khong.

    VI SAO KHONG CHI KIEM BENH NHAN HAY NGUOI KHAC (15/09/2026). Ban cu chi so
    `chu_the_id == 0`. Tren bo doi chu the the he 6, no cham C dung 28/40 cap trong
    khi 29/40 ca duong ong ghi di ung cua "bo" thanh cua "ba ngoai" — dung MUC tien
    su gia dinh, SAI NGUOI. Voi ho so, ghi nham bo thanh ba ngoai cung la mot lo~i
    quy gan: di ung cua mot nguoi da duoc gan cho mot nguoi khac.

    Dap an "nguoi nha" (loi thoai khong lo quan he): mo hinh phai goi chung chung.
    Neu no ghi dich danh "bo", do la BIA ra mot thong tin khong ai noi.
    """
    if _la_bn_gold(d) != (p.get("chu_the_id", 0) == 0):
        return False
    if _la_bn_gold(d):
        return True
    vang = _nd(d.get("chu_the", ""))
    ten = _nd(p.get("ten_chu_the", ""))
    if vang == "người nhà":
        return ten in TEN_NGUOI_NHA_CHUNG
    return ten == vang or ten.startswith(vang + " ")


CHI_TIET_THUOC_CHAM = ("lieu", "so_lan", "duong_dung", "bat_dau", "ngung",
                       "trang_thai_dung")


def dung_thuoc(d, p) -> bool:
    """Chi tiet thuoc cua phat bieu co KHOP dap an khong (15/09/2026).

    Moi chi tiet so sau chuan hoa, BANG NHAU MOI TINH LA DUNG. Ca hai chieu deu la
    loi: dap an co lieu ma phat bieu khong ghi (mat thong tin nguy hiem), va phat
    bieu ghi lieu ma dap an de trong (bia mot con so khong ai noi). Dap an khong co
    `thuoc` (menh de khong phai thuoc, hoac bo du lieu truoc 15/09) thi khong cham
    truc nay — cham thi moi phat bieu cua bo cu deu thanh loi.
    """
    vang = d.get("thuoc")
    if not vang:
        return True
    du = p.get("thuoc") or {}
    return all(_nd(vang.get(k)) == _nd(du.get(k)) for k in CHI_TIET_THUOC_CHAM)


def _loai_gold(d):
    m = d.get("muc")
    if m == "DỊ ỨNG" or "dị ứng" in str(d.get("noi_dung", "")).lower():
        return "di_ung"
    return {"THUỐC ĐANG DÙNG": "thuoc", "CHẨN ĐOÁN": "chan_doan"}.get(m, "khac")


def dap_an(ca):
    """Menh de dap an de cham, kem chi so goc `_i`. Bo ban sao o LY DO KHAM
    (`du_lieu_trich.ban_lap_ly_do_kham`): no khong phai mot thong tin rieng."""
    from src.du_lieu_trich import ban_lap_ly_do_kham
    lap = ban_lap_ly_do_kham(ca["dap_an"])
    return [dict(d, _i=i) for i, d in enumerate(ca["dap_an"]) if i not in lap]


def ghep_menh_de(da, ps):
    """Ghep 1-1 tham lam -> {chi so trong `da`: chi so trong `ps`}.

    Noi dung phai dat NGUONG_GHEP. Khi nhieu menh de CUNG noi dung — hai ban "sot"
    cua mot lan dinh chinh; "di ngoai phan long" that va "neu con di ngoai phan
    long" gia dinh — xep hang bang moc thoi gian roi bang LUOT dan. Ghep sai ban thi
    mot phat bieu dung bi tinh la "ban cu" hay "sai muc": do 11/09/2026 tren trich
    HOAN HAO, 21/531 loi gia truoc khi co hai tieu chi nay.
    """
    diem = []
    for i, d in enumerate(da):
        a = _nd(d.get("noi_dung"))
        la = set(d.get("luot") or [])
        for j, p in enumerate(ps):
            s = do_giong(a, _nd(p.get("noi_dung")))
            if s < NGUONG_GHEP:
                continue
            t = do_giong(_nd(d.get("moc_thoi_gian")), _nd(p.get("moc_thoi_gian")))
            lb = set(p.get("bang_chung") or p.get("luot_thoai") or [])
            lu = len(la & lb) / len(la | lb) if (la and lb) else 0.0
            # Hai ban cua mot lan sua LIEU cung ten thuoc, cung luot, khong moc thoi
            # gian — chi lieu phan biet duoc. Them 15/09/2026 cung truong `thuoc`.
            lieu = 0.0
            if d.get("thuoc") and p.get("thuoc"):
                lieu = float(_nd(d["thuoc"].get("lieu")) == _nd(p["thuoc"].get("lieu")))
            # Pha the hoa khi hai ban GIONG HET nhau ca noi dung, moc thoi gian va luot,
            # chi khac phu dinh: ghep ban cung phu dinh voi nhau. Trong so nho nen KHONG
            # doi cap khi moc thoi gian khac. Luu y (22/09/2026): ca dct_030_A tung bi
            # nghi la ghep cheo, kiem lai thi KHONG — mo hinh dao phu dinh that o ca hai
            # moc cua mot dien bien, va ghep theo moc thoi gian la dung.
            pd = 0.05 * float(_phu_dinh_that(d) == _phu_dinh_that(p))
            diem.append((s + 0.5 * t + 0.25 * lu + 0.5 * lieu + pd, -i, -j, i, j))
    diem.sort(reverse=True)
    ra, da_p = {}, set()
    for *_x, i, j in diem:
        if i in ra or j in da_p:
            continue
        ra[i] = j
        da_p.add(j)
    return ra


def _khoa_trung(p):
    return (_nd(p.get("noi_dung")), p.get("chu_the_id", 0) == 0, _muc(p))


def loi_phat_bieu(ca, ps, xet=None):
    """Ghep TOAN BO `ps` voi dap an — de ban cu cua he thong ghep voi ban cu cua dap
    an, du ban cu khong nam trong phan dang xet — roi cham nhung phat bieu co id
    trong `xet` (mac dinh: tat ca).

    -> ({id: (danh sach loi, loai thong tin)}, [menh de dap an bo sot]).

    `trung_lap`: phat bieu khong ghep duoc nhung GIONG HET mot phat bieu dang xet
    khac — dong viet lap, khong phai thong tin bia. Tach khoi `khong_can_cu`.
    Bo sot: menh de dap an VAO THAN ma phat bieu ghep voi no khong nam trong `xet`.
    """
    da = dap_an(ca)
    xet = {p["id"] for p in ps} if xet is None else set(xet)
    g = ghep_menh_de(da, ps)
    theo_p = {ps[j]["id"]: da[i] for i, j in g.items()}
    co_ghep = {_khoa_trung(p) for p in ps if p["id"] in xet and p["id"] in theo_p}
    ra, da_gap = {}, set()
    for p in ps:
        if p["id"] not in xet:
            continue
        d = theo_p.get(p["id"])
        if d is None:
            k = _khoa_trung(p)
            loai = "trung_lap" if (k in co_ghep or k in da_gap) else "khong_can_cu"
            da_gap.add(k)
            ra[p["id"]] = ([loai], cong_rui_ro.loai_thong_tin(p))
            continue
        loi = []
        if not dung_nguoi(d, p):
            loi.append("sai_chu_the")
        if _muc(d) != _muc(p):
            loi.append("sai_muc")
        if not _con_hieu_luc(d):
            loi.append("ban_cu")
        if not dung_thuoc(d, p):
            loi.append("sai_thuoc")
        # Ma con cua sai_muc (22/09/2026): sai o truc nao trong ba truc.
        if "sai_muc" in loi:
            md, mp = _muc(d), _muc(p)
            for truc, ma in zip(range(3), MA_CON_MUC):
                if md[truc] != mp[truc]:
                    loi.append(ma)
        # Thoi gian (22/09/2026) — truoc do bo cham khong cham truc nay.
        if sai_thoi_gian(d, p):
            loi.append("sai_thoi_gian")
        ra[p["id"]] = (loi, _loai_gold(d))
    bo_sot = [d for i, d in enumerate(da) if _gold_vao_than(d)
              and (i not in g or ps[g[i]]["id"] not in xet)]
    return ra, bo_sot


def _co_loi(ds):
    return bool(set(ds) & set(LOI))


def _than(r):
    muc = {g["id"]: g["muc"] for g in r.get("ghi_chu", [])}
    return [p for p in r["phat_bieu"]
            if p["id"] in muc and muc[p["id"]] not in sinh_benh_an.MUC_PHU_TAT_CA]


def _truoc_khoa(r):
    """Phat bieu SE vao than neu KHONG co khoa — tap de do danh dau."""
    return [p for p in r["phat_bieu"]
            if sinh_benh_an._muc_cho(p, 0)[0] not in sinh_benh_an.MUC_PHU_TAT_CA]


def cham_ca(ca, r) -> dict:
    """-> so dem cho MOT ca. Moi truong la tu so hoac mau so cua mot ty so."""
    than = {p["id"] for p in _than(r)}
    loi, bo_sot = loi_phat_bieu(ca, r["phat_bieu"], than)
    da = dap_an(ca)
    k = Counter(so_than=len(than),
                so_dap_an_than=sum(1 for d in da if _gold_vao_than(d)),
                bo_sot=len(bo_sot))
    for ds, loai in loi.values():
        # So menh de GHEP DUOC voi dap an (16/09/2026). Vi sao can: `sai_chu_the`
        # chia cho MOI phat bieu vao than, ma mot phat bieu khong ghep duoc thi
        # khong bao gio bi tinh sai chu the. Nen mot nhanh trich tho, ghep truot
        # gan het, lai co ty le sai chu the DEP hon mot nhanh trich dung. Do duoc
        # 16/09 tren bo doi chu the: duong doi chung theo luat co 66-77% phat bieu
        # khong can cu, va nho the ty le sai chu the cua no tut xuong 4-8%.
        if not ({"khong_can_cu", "trung_lap"} & set(ds)):
            k["so_ghep"] += 1
            # Menh de ghep duoc VA khong dinh loi nao — tu so cua Precision/Recall.
            if not _co_loi(ds):
                k["so_dung"] += 1
        else:
            # Menh de khong ung voi thong tin nao trong dap an — loi CHEN cua SER.
            k["chen"] += 1
        for m in ds:
            k[m] += 1
        k["loi_bat_ky"] += _co_loi(ds)
        if loai in LOAI_NGHIEM_TRONG:
            k["so_than_nghiem_trong"] += 1
            k["loi_nghiem_trong"] += _co_loi(ds)
    k["bo_sot_nghiem_trong"] = sum(1 for d in bo_sot
                                   if _loai_gold(d) in LOAI_NGHIEM_TRONG)
    k["so_dap_an_nghiem_trong"] = sum(1 for d in da if _gold_vao_than(d)
                                      and _loai_gold(d) in LOAI_NGHIEM_TRONG)

    # --- Precision / Recall / F1 / Slot Error Rate (20/09/2026)
    #
    # VI SAO THEM. Moi ty le loi o tren deu chia cho mot mau so PHU THUOC HE THONG
    # (so menh de no viet ra, hoac so menh de no ghep duoc). Mot he thong viet it
    # co mau so nho nen ty le dep. Do duoc 19/09 tren bo doi chu the: duong tat
    # bang luat dat 13,1% sai chu the — THAP HON moi nhanh co mo hinh — nhung no
    # bo sot 51,3% thong tin va chi 350/1.156 menh de ghep duoc voi dap an.
    #
    # Chuan cua linh vuc trich xuat thong tin la bao cao Precision, Recall, F1 tren
    # MAU SO DAP AN, cong them Slot Error Rate (Makhoul, Kubala, Schwartz,
    # Weischedel 1999 — "Performance measures for information extraction").
    #
    # F1 viet duoi dang mot ty so DUY NHAT de bootstrap theo cum kich ban van dung:
    #     F1 = 2*dung / (so he thong viet ra + so dap an)
    #
    # SER dem ba loai loi tren tong so o dap an. SER CO THE VUOT 1 — do la binh
    # thuong, khi he thong chen them nhieu hon so o co that.
    #     SER = (thay the + xoa + chen) / so dap an
    #     thay the = menh de ghep duoc nhung dinh loi
    #     xoa      = bo sot
    #     chen     = menh de khong ung voi thong tin nao trong dap an
    k["f1_tu"] = 2 * k["so_dung"]
    k["f1_mau"] = k["so_than"] + k["so_dap_an_than"]
    k["ser_tu"] = (k["so_ghep"] - k["so_dung"]) + k["bo_sot"] + k["chen"]

    # --- danh dau: tren tap TRUOC khoa, so voi danh dau ngau nhien cung so luong
    if "rui_ro" in r:
        tk = {p["id"] for p in _truoc_khoa(r)}
        loi_tk, _ = loi_phat_bieu(ca, r["phat_bieu"], tk)
        sai = {i for i, (ds, _l) in loi_tk.items() if _co_loi(ds)}
        co = {d["id"] for d in r["rui_ro"] if d["nhom"] in CO_DANH_DAU} & tk
        n, e = len(tk), len(sai)
        k["dd_n"], k["dd_loi"], k["dd_co"] = n, e, len(co)
        k["dd_trung"] = len(co & sai)
        k["dd_ngau_nhien"] = len(co) * e / n if n else 0.0

        # --- hoi lai: nguoi tra loi HOAN HAO sua moi loi o phat bieu duoc hoi
        hoi = set()
        for c in r.get("cau_hoi") or []:
            hoi |= {int(x) for x in c.get("muc_tieu", {})}
        hoi &= tk
        k["hl_so_cau"] = len(r.get("cau_hoi") or [])
        k["hl_so_hoi"] = len(hoi)
        k["hl_sua"] = len(hoi & sai)
        k["hl_ngau_nhien"] = len(hoi) * e / n if n else 0.0
    return k


def _luot_cua(x) -> int:
    """Luot thoai muon nhat lam bang chung — cho ca menh de dap an (`luot`) lan phat
    bieu cua duong ong (`bang_chung` hoac `luot_thoai`)."""
    return max(x.get("luot") or x.get("bang_chung") or x.get("luot_thoai") or [0])


def cham_theo_luot(ca, r) -> dict:
    """Hai chi so co don vi la LUOT, cho MOT ca (16/09/2026).

      luot_sai_dau_tien  luot dau tien ma ban nhap dung TOI luot do da mang mot loi
                         thuoc `LOI`, hoac da bo sot mot menh de dap an le ra co
                         trong ban nhap tinh toi luot do. None = khong luot nao sai.
      T_dung             luot dau tien ma MOI menh de dap an vao than (cua ca ca) da
                         duoc ghi dung, va khong con loi nao. None = khong bao gio du.

    VI SAO. Moi thuoc do khac cua du an cong don theo CA: mot ban nhap sai o luot 2
    roi duoc sua o luot 9 cham bang mot ban dung tu dau. Voi ho so lam sang thi hai
    thu do khac nhau — bac si doc ho so giua buoi kham. Pan, Liu, You (arXiv
    2603.17425) do `T_goal` (tuong ung `T_dung`) nhung khong do luot sai dau tien.

    Dung lai `loi_phat_bieu` va `ghep_menh_de` co san, chi doi tap `xet` theo tung
    luot — khong co luat cham thu hai de troi khoi luat chinh.
    """
    than = {p["id"] for p in _than(r)}
    ps = r["phat_bieu"]
    da = [d for d in dap_an(ca) if _gold_vao_than(d)]
    moc = sorted({_luot_cua(p) for p in ps if p["id"] in than}
                 | {_luot_cua(d) for d in da})
    dau_sai = t_dung = None
    for t in moc:
        xet = {p["id"] for p in ps if p["id"] in than and _luot_cua(p) <= t}
        loi, _ = loi_phat_bieu(ca, ps, xet)
        co_loi = any(_co_loi(ds) for ds, _l in loi.values())
        # Bo sot TINH TOI LUOT t: menh de dap an da du bang chung ma chua vao than.
        den_gio = [d for d in da if _luot_cua(d) <= t]
        thieu_gio = len(den_gio) - len(ghep_menh_de(
            den_gio, [p for p in ps if p["id"] in xet]))
        if dau_sai is None and (co_loi or thieu_gio):
            dau_sai = t
        # T_dung xet tren TOAN BO dap an cua ca, khong chi phan da den.
        if t_dung is None and not co_loi and da and len(ghep_menh_de(
                da, [p for p in ps if p["id"] in xet])) == len(da):
            t_dung = t
    return {"luot_sai_dau_tien": dau_sai, "T_dung": t_dung,
            "so_luot_co_menh_de": len(moc), "so_menh_de_than_dap_an": len(da)}


def ti_so(tu, mau, khuon, so_lan=sai_so.SO_LAN_MAC_DINH, hat=sai_so.HAT_MAC_DINH):
    """Ty so TONG (sum tu / sum mau) + khoang 95% bootstrap cum theo khuon."""
    cum = defaultdict(lambda: [0.0, 0.0])
    for i in mau:
        cum[khuon[i]][0] += tu.get(i, 0)
        cum[khuon[i]][1] += mau[i]
    cum = list(cum.values())
    T, M = sum(c[0] for c in cum), sum(c[1] for c in cum)
    if not M:
        return None
    rng = random.Random(hat)
    bs = []
    for _ in range(so_lan):
        t = m = 0.0
        for _k in range(len(cum)):
            c = cum[rng.randrange(len(cum))]
            t += c[0]
            m += c[1]
        if m:
            bs.append(t / m)
    bs.sort()
    return {"gia_tri": T / M, "thap": sai_so._phan_vi(bs, 0.025),
            "cao": sai_so._phan_vi(bs, 0.975), "tu": T, "mau": M,
            "so_khuon": len(cum)}


BANG = (  # (ten, tu so, mau so)
    ("sai_chu_the", "sai_chu_the", "so_than"),
    ("sai_muc", "sai_muc", "so_than"),
    ("ban_cu", "ban_cu", "so_than"),
    ("khong_can_cu", "khong_can_cu", "so_than"),
    ("sai_thuoc", "sai_thuoc", "so_than"),
    # Cung tu so, mau so la so menh de GHEP DUOC — doc kem hai dong tren, vi mau so
    # "so_than" thuong cho diem dep cho nhanh ghep truot nhieu.
    ("sai_chu_the_tren_ghep", "sai_chu_the", "so_ghep"),
    ("sai_muc_tren_ghep", "sai_muc", "so_ghep"),
    # Phien ban 2026-09-22, tinh tren menh de GHEP DUOC — ly do nhu dong
    # `sai_chu_the_tren_ghep`. Ba ma con cong lai co the LON HON sai_muc: mot menh
    # de sai ca hai truc thi co hai ma con.
    ("sai_muc_chac_chan_tren_ghep", "sai_muc_chac_chan", "so_ghep"),
    ("sai_muc_phu_dinh_tren_ghep", "sai_muc_phu_dinh", "so_ghep"),
    ("sai_muc_tinh_huong_tren_ghep", "sai_muc_tinh_huong", "so_ghep"),
    ("sai_thoi_gian_tren_ghep", "sai_thoi_gian", "so_ghep"),
    ("loi_bat_ky", "loi_bat_ky", "so_than"),
    ("trung_lap", "trung_lap", "so_than"),
    ("loi_nghiem_trong", "loi_nghiem_trong", "so_than_nghiem_trong"),
    ("bo_sot", "bo_sot", "so_dap_an_than"),
    ("bo_sot_nghiem_trong", "bo_sot_nghiem_trong", "so_dap_an_nghiem_trong"),
    # Bon dong duoi day dung MAU SO KHONG PHU THUOC he thong, nen so sanh duoc
    # giua cac he thong viet ra so luong menh de khac nhau. Xem ghi chu trong
    # `cham_ca`. `sai_chu_the_tren_gold` la cung tu so voi `sai_chu_the`, chia
    # cho tong so o dap an thay vi cho so menh de he thong viet ra.
    ("do_chinh_xac", "so_dung", "so_than"),
    ("do_phu", "so_dung", "so_dap_an_than"),
    ("f1", "f1_tu", "f1_mau"),
    ("ser", "ser_tu", "so_dap_an_than"),
    ("sai_chu_the_tren_gold", "sai_chu_the", "so_dap_an_than"),
    ("danh_dau_do_chuan", "dd_trung", "dd_co"),
    ("danh_dau_do_chuan_NGAU_NHIEN", "dd_ngau_nhien", "dd_co"),
    ("danh_dau_do_phu", "dd_trung", "dd_loi"),
    ("danh_dau_do_phu_NGAU_NHIEN", "dd_ngau_nhien", "dd_loi"),
    ("hoi_lai_sua_moi_phat_bieu_hoi", "hl_sua", "hl_so_hoi"),
    ("hoi_lai_NGAU_NHIEN", "hl_ngau_nhien", "hl_so_hoi"),
)


def tong_hop(cac_ca, ket_qua):
    """`ket_qua`: {id: ban ghi cua nhanh}. Moi ca trong `cac_ca` PHAI co ban ghi —
    thieu la dung han: bo ca di la chon ca de cho so dep."""
    thieu = [ca["id"] for ca in cac_ca if ca["id"] not in ket_qua]
    if thieu:
        raise SystemExit(f"thieu ket qua cho {len(thieu)} ca: {thieu[:5]}")
    dem = {ca["id"]: cham_ca(ca, ket_qua[ca["id"]]) for ca in cac_ca}
    khuon = {ca["id"]: ca.get("benh") or "?" for ca in cac_ca}
    bang = {}
    for ten, tu, mau in BANG:
        m = {i: dem[i][mau] for i in dem if mau in dem[i]}
        if m:
            bang[ten] = ti_so({i: dem[i][tu] for i in m}, m, khuon)
    return {"bang": bang, "so_ca": len(cac_ca),
            "tong": dict(sum((Counter(d) for d in dem.values()), Counter()))}


# ------------------------------------------------------------- ba thach thuc
def _than_khang_dinh_di_ung_bn(r):
    return [p for p in _than(r) if p.get("chu_the_id", 0) == 0
            and "dị ứng" in str(p.get("noi_dung", "")).lower()
            and _muc(p) == ("chắc chắn", False, "thực tế")]


def dung_di_ung(ca, r) -> bool:
    """Ban A: di ung cua NGUOI NHA. Ban B: cua BENH NHAN. Dung khi menh de di ung
    khang dinh ghep duoc va dung nguoi, va o ban A khong co phat bieu than nao ghi
    benh nhan di ung chat do."""
    if r is None:
        return False
    gold = [d for d in dap_an(ca) if "dị ứng" in d["noi_dung"].lower()
            and _muc(d) == ("chắc chắn", False, "thực tế") and _con_hieu_luc(d)]
    if not gold:
        return False
    g = ghep_menh_de(gold, r["phat_bieu"])
    for i, d in enumerate(gold):
        if i not in g:
            return False
        if not dung_nguoi(d, r["phat_bieu"][g[i]]):
            return False
    if not any(_la_bn_gold(d) for d in gold):
        chat = {_nd(d["noi_dung"]) for d in gold}
        if any(do_giong(_nd(p["noi_dung"]), c) >= NGUONG_GHEP
               for p in _than_khang_dinh_di_ung_bn(r) for c in chat):
            return False
    return True


def chu_ky(r):
    """Cai phai GIONG NHAU giua hai ban cua cap phuong ngu: moi phat bieu la (noi
    dung chuan hoa, benh nhan?, muc khang dinh, vao than?)."""
    muc = {g["id"]: g["muc"] for g in r.get("ghi_chu", [])}
    return frozenset((_nd(p["noi_dung"]), p.get("chu_the_id", 0) == 0, _muc(p),
                      muc.get(p["id"]) not in sinh_benh_an.MUC_PHU_TAT_CA)
                     for p in r["phat_bieu"])


def dung_trang_thai_cuoi(ca, r) -> bool:
    """Moi menh de dap an CO quan he, va menh de no tro toi, phai o dung cho:
    con hieu luc -> than; bi thay / chua giai quyet -> KHONG o than."""
    if r is None:
        return False
    da = dap_an(ca)
    lq_i = {d["_i"] for d in da if d.get("quan_he")} | \
           {d.get("quan_he_voi") for d in da if d.get("quan_he")}
    if not lq_i:
        return False
    than_id = {p["id"] for p in _than(r)}
    g = ghep_menh_de(da, r["phat_bieu"])       # ghep TOAN BO, xet phan lien quan
    for i, d in enumerate(da):
        if d["_i"] not in lq_i:
            continue
        o_than = i in g and r["phat_bieu"][g[i]]["id"] in than_id
        if o_than != _gold_vao_than(d):
            return False
    return True


def cham_thach_thuc(cac_ca, ket_qua):
    loai = {ca.get("thach_thuc") for ca in cac_ca} - {None}
    if len(loai) != 1:
        return None
    loai = loai.pop()
    if loai == "doi_chu_the":
        cap = defaultdict(dict)
        for ca in cac_ca:
            cap[ca["cap"]][ca["bien_the"]] = dung_di_ung(ca, ket_qua.get(ca["id"]))
        du = [v for v in cap.values() if len(v) == 2]
        return {"thach_thuc": loai, "so_cap": len(du),
                "dung_ca_cap": sum(all(v.values()) for v in du),
                "dung_ban_A": sum(v["A"] for v in du),
                "dung_ban_B": sum(v["B"] for v in du)}
    if loai == "phuong_ngu":
        cap = defaultdict(dict)
        for ca in cac_ca:
            r = ket_qua.get(ca["id"])
            cap[ca["cap"]][ca["bien_the"]] = (ca, r)
        du = [v for v in cap.values() if len(v) == 2]
        giong = sum(1 for v in du if v["A"][1] and v["B"][1]
                    and chu_ky(v["A"][1]) == chu_ky(v["B"][1]))
        loi = {b: sum(cham_ca(ca, r)["loi_bat_ky"] for v in du
                      for ca, r in [v[b]] if r) for b in ("A", "B")}
        than = {b: sum(cham_ca(ca, r)["so_than"] for v in du
                       for ca, r in [v[b]] if r) for b in ("A", "B")}
        return {"thach_thuc": loai, "so_cap": len(du), "giong_het": giong,
                "loi_ban_co_phuong_ngu": f"{loi['A']}/{than['A']}",
                "loi_ban_khong_phuong_ngu": f"{loi['B']}/{than['B']}"}
    if loai == "dinh_chinh":
        theo_bay = defaultdict(lambda: [0, 0])
        for ca in cac_ca:
            t = theo_bay[ca.get("bay_chinh")]
            t[1] += 1
            t[0] += dung_trang_thai_cuoi(ca, ket_qua.get(ca["id"]))
        return {"thach_thuc": loai,
                "dung_theo_bay": {b: f"{d}/{n}" for b, (d, n) in theo_bay.items()},
                "dung": sum(d for d, _n in theo_bay.values()),
                "so_ca": sum(n for _d, n in theo_bay.values())}
    return None


# ----------------------------------------------------------------------- CLI
def _in(ten, k):
    if k is None:
        return
    print(f"  {ten:34} {k['gia_tri']:7.2%}  [{k['thap']:.2%}; {k['cao']:.2%}]"
          f"  ({k['tu']:.1f}/{k['mau']:.0f}, {k['so_khuon']} khuon)")


def canh_bo_lech_the_he(tep, goc, kq):
    """Dung neu hoi thoai trong tep ket qua khac hoi thoai trong bo du lieu.

    LOI DA XAY RA (phat hien 19/09/2026). Ngay 15/09 luc 13:04 cac nhanh chay tren
    bo doi chu the THE HE 6. Luc 13:40 cung ngay, bo the he 7 duoc sinh ra va GHI DE
    len cung ten tep trong `data/`. Ngay 16/09 bo cham chay lai: no nap ket qua the
    he 6 va dap an the he 7. Phep kiem id o tren KHONG bat duoc, vi hai the he sinh
    tu cung danh sach kich ban nen id trung nhau — chi noi dung loi thoai la khac.

    Ket qua sai di ro: bo sot cua nhanh B tu 15,60% thanh 29,39%.

    Phep kiem: `input` cua tung ca trong tep ket qua phai giong het `input` cua ca
    cung id trong bo du lieu. Ban ghi khong co `input` thi bo qua (tep cu).
    """
    lech = [i for i, r in kq.items()
            if "input" in r and r["input"] != goc[i].get("input")]
    if not lech:
        return
    raise SystemExit(
        f"{Path(tep).name}: {len(lech)}/{len(kq)} ca co hoi thoai KHAC bo du lieu hien tai "
        f"(vd {lech[:3]}).\nTep ket qua nay chay tren mot the he du lieu khac. Cham "
        f"no voi dap an nay ra so SAI. Dua dung cap tep ve cung thu muc roi chay lai.")


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", required=True)
    ap.add_argument("--nhanh", nargs="+", required=True)
    # Cham mot the he cu hoac mot ban tai ve tu Kaggle: dua ca tep ket qua LAN bo du
    # lieu sinh ra chung vao mot thu muc roi tro `--thu-muc` vao do. Dung `data/` de
    # cham mot the he cu la cach da lam ra so sai ngay 16/09/2026.
    ap.add_argument("--thu-muc", default=None,
                    help="thu muc chua ra_*.jsonl VA <tap>.jsonl (mac dinh: data/)")
    ap.add_argument("--hau-to", default="", help="hau to them vao ten tep ket qua")
    a = ap.parse_args()
    from src import du_lieu
    du_lieu.chan_tap_ngoai(a.tap)
    du_lieu.chan_tap_khoa(a.tap)
    d = Path(a.thu_muc) if a.thu_muc else duong_dan.THU_MUC_DU_LIEU
    goc = {c["id"]: c for c in du_lieu.nap_mau(d / f"{a.tap}.jsonl")}
    ra = {}
    for nhanh in a.nhanh:
        tep = d / f"ra_{nhanh}_{a.tap}.jsonl"
        kq = {r["id"]: r for r in du_lieu.nap_mau(tep)}
        la = [i for i in kq if i not in goc]
        if la:
            raise SystemExit(f"{tep.name}: {len(la)} id KHONG co trong {a.tap} "
                             f"(vd {la[:3]}) — mot ten tep, hai bo du lieu?")
        canh_bo_lech_the_he(tep, goc, kq)
        if not all("phat_bieu" in r for r in kq.values()):
            print(f"\n=== {nhanh}: khong co truong phat_bieu — sinh lai bang "
                  f"`--tu-dem` voi ma tu 11/09/2026")
            continue
        cac_ca = [goc[i] for i in kq]
        tk = tong_hop(cac_ca, kq)
        print(f"\n=== {nhanh} tren {a.tap}: {tk['so_ca']} ca")
        for ten, k in tk["bang"].items():
            _in(ten, k)
        tt = cham_thach_thuc(cac_ca, kq)
        if tt:
            print(f"  thach thuc: {tt}")
        ra[nhanh] = {"tong_hop": tk, "thach_thuc": tt, "phien_ban_bo_cham": PHIEN_BAN}
    if any(n.startswith("C_khoa_hoi") for n in ra):
        print("\nHOI LAI: nguoi tra loi MO PHONG la HOAN HAO — so tren la TRAN TREN.")
    dp = duong_dan.THU_MUC_KET_QUA / f"cham-he-thong-{a.tap}{a.hau_to}.json"
    dp.write_text(json.dumps(ra, ensure_ascii=False, indent=2, default=str),
                  encoding="utf-8")
    print(f"\nGhi {dp}")


if __name__ == "__main__":
    main()
