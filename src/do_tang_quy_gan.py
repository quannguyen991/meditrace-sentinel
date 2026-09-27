# -*- coding: utf-8 -*-
"""Cham quy gan RIENG TUNG TANG do kho, thay vi gop thanh mot so.

VI SAO CAN. `thuoc_do_quy_gan.diem` cham F1 tren toan bo menh de cua mot ca.
Do duoc tren bo du lieu: menh de tang 4 — nguoi nha ke ve CHINH MINH, cho ca
hai duong tat deu sai — chiem 1,91% (bo 3.000) den 2,32% (bo 5.000). Trong 60
ca da dung de so sanh cac nhanh: 7 menh de tren 514.

    anh huong toi da tren thuoc do gop   1,36%
    be rong khoang tin cay do duoc       4,16%

Nen thuoc do gop KHONG THE thay duoc co che quy gan co tac dung hay khong. No
khong noi "co che vo dung", no khong noi gi ca. Tep nay cham rieng tung tang
de cau hoi do co cho tra loi.

BON TANG, xep theo do kho THAT:

    1 bac_si        luot bac si              chu the luon la benh nhan
    2 benh_nhan     luot benh nhan           chu the la chinh nguoi noi
    3 ke_ho         nguoi nha ke HO          "chu the = nguoi noi" SAI
    4 ke_ve_minh    nguoi nha ke VE MINH     ca hai duong tat deu SAI

Tang 3 va tang 4 doi nhau: o tang 3 phai gan cho BENH NHAN du nguoi noi la
nguoi nha; o tang 4 phai gan cho NGUOI NHA du phan lon luot khac deu ve benh
nhan. Mot he thong chi biet mot chieu se an mot tang va truot tang kia — nen
hai tang nay phai bao RIENG, khong duoc gop.

GOC DOI CHIEU LA `dap_an` TRONG BO DU LIEU, khong phai van ban tham chieu.
Van ban tham chieu sinh ra TU `dap_an`, nen doi chieu qua no la qua mot lan
bien doi nua — va lan bien doi do lam mat nhan tang.

    python -m src.do_tang_quy_gan --tap viet_phat_trien --nhanh B C D
"""
import argparse
import io
import sys
from pathlib import Path

from src import sai_so, thuoc_do_quy_gan

# Hai gia tri chu the ma `thuoc_do_quy_gan.tach_menh_de` phan biet duoc.
# `dap_an` ghi vai cu the ("me", "ba ngoai", "chong"...); gom het ve "nguoi
# nha" vi do la do phan giai ma ban nhap thuc su mang.
BENH_NHAN = "bệnh nhân"
NGUOI_NHA = "người nhà"


def _chu_the_chuan(chu_the):
    return BENH_NHAN if chu_the == BENH_NHAN else NGUOI_NHA


def menh_de_dap_an(ban_ghi_goc):
    """-> [(tang, chu_the_chuan, MenhDe gia)] cho moi menh de CO luot.

    `MenhDe` gia chi de goi `cung_noi_dung` — no can truong `tu` va `chu_the`.
    """
    vai = sai_so.nguoi_noi_tung_luot(ban_ghi_goc)
    ra = []
    for m in ban_ghi_goc.get("dap_an") or []:
        # MOT dinh nghia tang, dung chung voi `sai_so.tang_menh_de` — xem
        # `sai_so.tang_cua` (nguoi noi luot CUOI, dieu duong la nhan vien y te).
        tang = sai_so.tang_cua(m, vai)
        if tang is None:
            continue
        ct = _chu_the_chuan(m.get("chu_the"))
        noi_dung = str(m.get("noi_dung") or "")
        gia = thuoc_do_quy_gan.MenhDe(
            chu_the=ct, tu=thuoc_do_quy_gan._tu_noi_dung(noi_dung),
            cau=noi_dung, muc=str(m.get("muc") or ""))
        if gia.tu:
            ra.append((tang, ct, gia))
    return ra


def cham_mot_ca(du_doan, ban_ghi_goc):
    """-> {tang: {dung, sai_chu_the, thieu}}.

    `dung`          tim duoc menh de cung noi dung VA cung chu the
    `sai_chu_the`   tim duoc cung noi dung nhung gan sai nguoi  <- loi cua du an
    `thieu`         khong tim duoc noi dung do trong ban nhap

    Tach `sai_chu_the` khoi `thieu` la chu y: bo sot va gan sai nguoi la hai
    loi khac nhau, va gop lai thi khong thay duoc cai nao dang giam.
    """
    pd = thuoc_do_quy_gan.tach_menh_de(du_doan or "")
    ra = {}
    for tang, ct, goc in menh_de_dap_an(ban_ghi_goc):
        o = ra.setdefault(tang, {"dung": 0, "sai_chu_the": 0, "thieu": 0})
        khop = [p for p in pd if thuoc_do_quy_gan.cung_noi_dung(p, goc)]
        if not khop:
            o["thieu"] += 1
        elif any(p.chu_the == ct for p in khop):
            o["dung"] += 1
        else:
            o["sai_chu_the"] += 1
    return ra


# Hai truc, va TRON CHUNG LAI LA LOI.
#
#   quy_gan   dung / (dung + sai_chu_the)        -- trong so noi dung DA ghi
#                                                   duoc, bao nhieu phan gan
#                                                   dung nguoi
#   bao_phu   (dung + sai) / (dung + sai + thieu) -- bao nhieu phan noi dung
#                                                   vao duoc ban nhap
#
# Ban dau tep nay tinh dung/(dung+sai+thieu) roi goi la "gan dung". Con so do
# tut xuong khi he thong BO SOT, khong phai khi no GAN SAI NGUOI — nen tang
# `bac_si` ra 56% trong khi loi quy gan o tang do gan nhu khong co. Hai loai
# loi khac nhau gop lai thi khong thay duoc cai nao dang giam.
CHE_DO = ("quy_gan", "bao_phu")


def ty_le_tung_ca(ket_qua_theo_id, goc_theo_id, tang, che_do="quy_gan"):
    """-> {id: ty le} cho MOT tang, chi tinh ca CO menh de tang do.

    Bo ca khong co menh de tang do thay vi cho diem 1.0: cho diem 1.0 lam
    loang het hieu ung — day dung la loi ma tep nay duoc viet ra de chan,
    khong duoc lap lai o muc trong tep.
    """
    if che_do not in CHE_DO:
        raise SystemExit(f"che do phai la mot trong {CHE_DO}")
    ra = {}
    for ma, k in ket_qua_theo_id.items():
        if ma not in goc_theo_id:
            continue
        d = cham_mot_ca(k.get("du_doan", ""), goc_theo_id[ma]).get(tang)
        if not d:
            continue
        if che_do == "quy_gan":
            mau = d["dung"] + d["sai_chu_the"]
            tu = d["dung"]
        else:
            mau = d["dung"] + d["sai_chu_the"] + d["thieu"]
            tu = d["dung"] + d["sai_chu_the"]
        if mau:
            ra[ma] = tu / mau
    return ra


def bang(ket_qua_theo_nhanh, goc_theo_id, khuon=None, so_lan=2000):
    """Bang: moi tang mot khoi, moi nhanh mot dong."""
    d = ["# Chấm quy gán theo tầng độ khó", "",
         "Tầng 3 và tầng 4 **đối nhau**: tầng 3 phải gán cho bệnh nhân dù người",
         "nói là người nhà; tầng 4 phải gán cho người nhà dù phần lớn lượt khác",
         "đều về bệnh nhân. Một hệ thống chỉ biết một chiều sẽ ăn một tầng và",
         "trượt tầng kia, nên hai tầng này không được gộp.", ""]
    so_khuon = len(set(khuon.values())) if khuon else None
    canh = sai_so.canh_so_khuon(so_khuon)
    if canh:
        d += ["> " + canh.replace("{so_ca}", str(len(goc_theo_id))),
              ">",
              "> Cụ thể với số khuôn này, cận dưới của khoảng tin cậy tụt về 0%:",
              "> một lần lấy lại mẫu có thể rút đúng một khuôn ba lần. Khoảng đó",
              "> không hỏng — nó đang nói rằng nó không nói được gì.", ""]

    d += ["Hai trục, **không gộp**: *gán đúng* tính trong số nội dung đã ghi",
          "được (mẫu số không có phần bỏ sót), *bao phủ* tính phần nội dung vào",
          "được bản nháp. Trộn hai trục thì điểm tụt vì bỏ sót bị đọc thành lỗi",
          "quy gán.", ""]

    for tang in sai_so.TANG:
        dong = []
        for ten, kq in ket_qua_theo_nhanh.items():
            qg = ty_le_tung_ca(kq, goc_theo_id, tang, "quy_gan")
            bp = ty_le_tung_ca(kq, goc_theo_id, tang, "bao_phu")
            if not bp:
                continue
            kq_g = (sai_so.khoang(qg, {i: khuon[i] for i in qg} if khuon else None,
                                  so_lan=so_lan) if qg else None)
            kb = sai_so.khoang(bp, {i: khuon[i] for i in bp} if khuon else None,
                               so_lan=so_lan)
            dong.append((ten, kq_g, kb, len(qg), len(bp)))
        if not dong:
            continue
        d += [f"## Tầng `{tang}` — {dong[0][4]} ca có mệnh đề tầng này", "",
              "| Nhánh | Gán đúng | KTC 95% | Bao phủ | n ca chấm được quy gán |",
              "|---|---|---|---|---|"]
        for ten, kg, kb, n_qg, _ in dong:
            cot = (f"{sai_so._pt(kg['trung_binh'])} | "
                   f"[{sai_so._pt(kg['thap'])}; {sai_so._pt(kg['cao'])}]"
                   if kg else "— | —")
            d.append(f"| `{ten}` | {cot} | {sai_so._pt(kb['trung_binh'])} | "
                     f"{n_qg} |")
        d.append("")
    return "\n".join(d)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--tap-goc", default=None)
    ap.add_argument("--nhanh", nargs="+", default=["B", "C", "D"])
    # Xem chu thich cung ten o `sai_so`: quy uoc ten tep da sinh ra mot loi
    # that, nen phai goi thang duong dan duoc.
    ap.add_argument("--tep", nargs="+", default=None, metavar="TEN=DUONG_DAN")
    ap.add_argument("--so-lan", type=int, default=2000)
    ap.add_argument("--ra", default=None)
    a = ap.parse_args()
    from src import du_lieu as _dl
    _dl.chan_tap_khoa(a.tap)

    nguon = ({k: Path(v) for k, v in (x.split("=", 1) for x in a.tep)}
             if a.tep else
             {n: sai_so.THU_MUC_DATA / f"ra_{n}_{a.tap}.jsonl" for n in a.nhanh})
    ket_qua_theo_nhanh, moi = {}, {}
    for n, tep in nguon.items():
        if not tep.exists():
            print(f"bo qua {n}: khong co {tep}")
            continue
        kq = {b["id"]: b for b in sai_so._doc(tep)}
        ket_qua_theo_nhanh[n] = kq
        moi.update(kq)
    if not ket_qua_theo_nhanh:
        raise SystemExit("khong nap duoc nhanh nao")

    tap_goc = (Path(a.tap_goc) if a.tap_goc
               else sai_so.THU_MUC_DATA / f"{a.tap}.jsonl")
    khuon = sai_so.doi_chieu_tap(moi, tap_goc)
    goc = {b["id"]: b for b in sai_so._doc(tap_goc) if b["id"] in moi}

    van = bang(ket_qua_theo_nhanh, goc, khuon, a.so_lan)
    print(van)
    if a.ra:
        Path(a.ra).write_text(van + "\n", encoding="utf-8")
        print(f"-> {a.ra}")


if __name__ == "__main__":
    main()
