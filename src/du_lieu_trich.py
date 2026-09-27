# -*- coding: utf-8 -*-
"""Dung du lieu HUAN LUYEN cho khau trich, tu bo hoi thoai Viet tu sinh.

VI SAO. Ba phep do doc lap deu chi vao cung mot cho: khau TRICH XUAT la nut
that, khong phai luat.

    hoi thoai that, dung quy gan   A_nen 73,2%   C 57,4%
    bo chan doan tu sinh           A     92%     C 93%
    `quan_he` tren hoi thoai that  "khong" o ca 282 phat bieu

Nhanh A duoc huan luyen tren 1.357 benh an; khau trich cua C dung mo hinh nen
voi 5 vi du. Cho khong can do da duoc go mot phan bang nhanh A_nen (zero-shot,
cung mo hinh) — va A_nen VAN hon C ve quy gan. Nhung A_nen duoc huan luyen
truoc do cho tac vu VIET BENH AN, con khau trich thi chua bao gio duoc huan
luyen cho tac vu cua no.

Bo `hoi_thoai_viet.jsonl` (1.000 ca, 8.361 menh de) co dap an cau truc, nen
dung duoc lam du lieu huan luyen cho chinh khau trich.

GIOI HAN CUA BO NHAN NAY — phai ghi vao bao cao, khong duoc lo di:

  co       chu_the (238/8.361 khong phai benh nhan), noi_dung, moc_thoi_gian,
           phu_dinh, tinh_huong (thuc te / ke hoach), luot lam bang chung
  KHONG co `do_chac_chan` -> khong day duoc muc "chua ghi nhan".
  KHONG co `gia_dinh`     -> tinh_huong chi co "thuc te" va "ke hoach".

`quan_he` — SUA 09/09/2026. Truoc do dap an khong co truong nay, nen moi ban
ghi deu mang "khong": 2.231 ca vi du am, KHONG MOT vi du duong. Do la ly do
day du cua con so `quan_he` = "khong" o 282/282 tren hoi thoai that — mo hinh
hoc dung thu no duoc day. Bo sinh gio ghi lai quan he (461 dinh chinh + 442
dien bien tren 3.000 ca), nen bo nhan nay day duoc co che quan he.

Nen ket qua cua thi nghiem nay noi duoc ve QUY GAN CHU THE va (tu 09/09/2026)
ve QUAN HE. Van chua noi duoc ve muc chac chan va tinh huong gia dinh.

    python -m src.du_lieu_trich --giu-lai 100
"""
import io
import json
import sys

from src import bakeoff, duong_dan

# Truong nao trong dap an anh xa sang truong nao cua LUOC_DO.
# `muc` khong co trong luoc do — bo di chu khong nhet bua vao, vi mo hinh se
# hoc sinh ra mot truong ma bo ep JSON se chan.
MAC_DINH = {"do_chac_chan": "chắc chắn", "thoi_gian_su_kien": "chưa rõ",
            "quan_he": "không", "quan_he_voi": None}


def ban_lap_ly_do_kham(dap_an):
    """Chi so cac menh de LY DO KHAM la BAN SAO cua mot menh de khac (cung chu the,
    cung noi dung).

    Bo sinh ghi trieu chung chinh HAI lan: mot o benh su, mot o ly do kham. Luoc do
    trich khong co truong `muc`, nen ban sao chi day mo hinh viet TRUNG — va ban
    nhap ra hai dong "sot cao" lien nhau trong benh su (muc ly do kham do
    `sinh_benh_an.sinh` tu lay dong dau benh su). Tim ra 11/09/2026 khi cham trich
    HOAN HAO qua duong ong (`cham_he_thong`). Mot dinh nghia, dung chung cho nhan
    huan luyen, cho phep do khau trich va cho phep cham he thong.
    """
    thuong = {(m.get("chu_the"), m.get("noi_dung")) for m in dap_an
              if m.get("muc") != "LÝ DO KHÁM BỆNH"}
    return {i for i, m in enumerate(dap_an) if m.get("muc") == "LÝ DO KHÁM BỆNH"
            and (m.get("chu_the"), m.get("noi_dung")) in thuong}


def doi_mot_ca(k):
    """Mot ca -> (chuoi hoi thoai da danh so, chuoi JSON dap an).

    ANH XA LAI `quan_he_voi`. Trong dap an, `quan_he_voi` la chi so trong
    `dap_an`. Nhung vong lap duoi BO cac menh de khong co bang chung, nen chi
    so bi xe dich. Khong anh xa lai thi mot phan ba so quan he se tro sang mot
    ban ghi khac han — va do la loi im lang: JSON van hop le, mo hinh van hoc
    duoc, chi la hoc sai.
    """
    danh_so, so_luot = bakeoff.danh_so_luot(k["input"])
    dap_an = k["dap_an"]

    # Vong 1: quyet dinh giu menh de nao, va nho chi so moi cua no.
    giu, chi_so_moi = [], {}
    lap = ban_lap_ly_do_kham(dap_an)
    for i, m in enumerate(dap_an):
        if i in lap:
            continue                       # ban sao ly do kham — xem ham tren
        luot = [n for n in (m.get("luot") or []) if 1 <= n <= so_luot]
        if not luot:
            continue                       # khong co bang chung thi khong day
        chi_so_moi[i] = len(giu)
        giu.append((i, m, luot))

    # Vong 2: dung ban ghi, anh xa lai `quan_he_voi`.
    ps = []
    for i, m, luot in giu:
        quan_he = m.get("quan_he") or MAC_DINH["quan_he"]
        dich = m.get("quan_he_voi")
        dich_moi = chi_so_moi.get(dich) if dich is not None else None
        if dich_moi is None:
            # Ban ghi kia bi bo (khong co bang chung) -> khong con quan he de
            # day. Ha ve "khong" chu KHONG giu quan he tro vao khoang khong.
            quan_he, dich_moi = MAC_DINH["quan_he"], None
        ban_ghi = {
            "chu_the": m["chu_the"],
            "noi_dung": m["noi_dung"],
            # DOC TU DAP AN tu 11/09/2026. Truoc do la MAC_DINH o moi nhan — cung
            # hinh voi `thoi_gian_su_kien` ben duoi, lan thu sau cua ho loi. Bo
            # cu (dap an khong co truong nay) van lui ve mac dinh.
            "do_chac_chan": m.get("do_chac_chan") or MAC_DINH["do_chac_chan"],
            "phu_dinh": bool(m.get("phu_dinh", False)),
            "tinh_huong": m.get("tinh_huong", "thực tế"),
            # DOC TU DAP AN, khong dong cung mac dinh.
            #
            # Truoc 11/09/2026 dong nay la `MAC_DINH["thoi_gian_su_kien"]`, nen
            # MOI nhan huan luyen mang "chua ro" — mot truong hang so. Mo hinh
            # hoc dung thu no duoc day va xuat "chua ro" o **ca 462** phat bieu
            # tren tap phat trien, lam luat `thoi_gian_su_kien == "qua khu" ->
            # TIEN SU BENH` cua `sinh_benh_an` thanh ma chet.
            #
            # Cung hinh voi `quan_he` (09/09): mot truong khai trong luoc do,
            # duoc mot khau sau doc, va khong bao gio co gia tri thu hai trong
            # nhan. Lan thu tu cua ho loi nay.
            "thoi_gian_su_kien": (m.get("thoi_gian_su_kien")
                                  or MAC_DINH["thoi_gian_su_kien"]),
            "moc_thoi_gian": m.get("moc_thoi_gian"),
            "quan_he": quan_he,
            "quan_he_voi": dich_moi,
            "luot_thoai": luot,
        }
        # Trich dan di THEO luot: bo luot nao (ngoai khoang) thi bo trich dan cua
        # luot do, de hai danh sach van thang hang tung phan tu. Bo cu khong co
        # hai truong nay thi ban ghi khong mang chung — khong day mot gia tri rong.
        trich = [td for n, td in zip(m.get("luot") or [], m.get("trich_dan") or [])
                 if 1 <= n <= so_luot]
        if trich:
            ban_ghi["trich_dan"] = trich
        if m.get("hanh_vi"):
            ban_ghi["hanh_vi"] = m["hanh_vi"]
        # Chi tiet thuoc (15/09/2026). Chi phat bieu thuoc mang truong nay — cac
        # phat bieu khac khong mang, de mo hinh khong hoc sinh `"thuoc": null` o moi
        # ban ghi. Quen dong nay la ho loi "khai ma khong day" lan thu bay.
        if m.get("thuoc"):
            ban_ghi["thuoc"] = m["thuoc"]
        ps.append(ban_ghi)
    return danh_so, json.dumps({"phat_bieu": ps}, ensure_ascii=False)


def dung(danh_sach, vi_du=False):
    """-> danh sach {id, input, output} dung dinh dang `train_baseline` doc.

    `input` la LOI NHAC DAY DU giong het luc suy luan (`bakeoff.trich`), de
    mo hinh hoc dung dieu kien no se gap. Khac mot chu la lech phan phoi.
    `vi_du=False`: khi da huan luyen thi khong can 5 vi du mau nua, va bo di
    thi loi nhac ngan hon ba lan.
    """
    from src.vi_du_mau import VI_DU
    ra = []
    for k in danh_sach:
        danh_so, dap_an = doi_mot_ca(k)
        loi_nhac = bakeoff.HUONG_DAN + (
            f"\n\n{VI_DU}\n\nBây giờ đến lượt bạn." if vi_du else "")
        ra.append({"id": k["id"],
                   "input": f"{loi_nhac}\n\nHội thoại:\n{danh_so}",
                   "output": dap_an})
    return ra


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--nguon", default="hoi_thoai_viet_3000.jsonl")
    # Tap da duoc chia san boi `tach_tap_viet` (theo KHUON BENH). Dung no
    # thay vi tu chia lai, de khau trich va nhanh A hoc tren DUNG mot tap.
    ap.add_argument("--da-chia", action="store_true")
    ap.add_argument("--giu-khuon", type=int, default=4,
                    help="so KHUON BENH giu rieng — don vi doc lap la khuon, "
                         "khong phai dong")
    a = ap.parse_args()

    d = duong_dan.THU_MUC_DU_LIEU
    ca = [json.loads(x) for x in open(d / a.nguon, encoding="utf-8") if x.strip()]

    if a.da_chia:
        train = [json.loads(x) for x in
                 open(d / "viet_train.jsonl", encoding="utf-8") if x.strip()]
        giu = [json.loads(x) for x in
               open(d / "viet_phat_trien.jsonl", encoding="utf-8") if x.strip()]
    else:
        # Tach theo KHUON BENH, khong theo dong: hai dong cung khuon gan nhu
        # la mot bai, cat theo dong thi tap kiem chi do "gap lai khuon da hoc".
        khuon = sorted({k["benh"] for k in ca})
        giu_khuon = set(khuon[-a.giu_khuon:]) if a.giu_khuon else set()
        giu = [k for k in ca if k["benh"] in giu_khuon]
        train = [k for k in ca if k["benh"] not in giu_khuon]

    for ten, ds in (("trich_train", train), ("trich_giu_lai", giu)):
        if not ds:
            continue
        mau = dung(ds)
        dp = d / f"{ten}.jsonl"
        dp.write_text("\n".join(json.dumps(m, ensure_ascii=False) for m in mau),
                      encoding="utf-8")
        so_md = sum(len(json.loads(m["output"])["phat_bieu"]) for m in mau)
        khac = sum(1 for m in mau
                   for p in json.loads(m["output"])["phat_bieu"]
                   if p["chu_the"] != "bệnh nhân")
        print(f"{dp.name:22} {len(mau):5} ca  {so_md:6} menh de  "
              f"{khac:4} khong phai benh nhan ({100*khac/max(1,so_md):.1f}%)")

    khuon_train = {k["benh"] for k in train}
    khuon_giu = {k["benh"] for k in giu}
    print(f"\nKhuon benh: train {len(khuon_train)}, giu lai {len(khuon_giu)}, "
          f"chi co o tap giu lai: {sorted(khuon_giu - khuon_train)}")


if __name__ == "__main__":
    main()
