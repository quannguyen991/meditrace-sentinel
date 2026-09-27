# -*- coding: utf-8 -*-
"""Do mo hinh tren bo kiem tra chan doan — cham TU DONG.

Day la ly do bo chan doan ton tai: dap an biet truoc chinh xac vi ca hoi thoai
lan benh an dung deu do cung mot doan ma sinh ra. Khong phai cham tay.

Moi tinh huong mot phep kiem. Phep kiem duoc viet de TRA LOI DUOC va de HONG —
neu no khong bao gio bao sai thi no vo dung.

    python -m src.do_bo_chan_doan --model Qwen/Qwen3-8B --n 15
"""
import argparse
import io
import json
import re
import sys

from src import bakeoff

TRE = re.compile(r"(?i)\b(trẻ|bé|cháu|em bé)\b")
ME = re.compile(r"(?i)\b(mẹ|người nhà|tôi)\b")


def _co(cum, van_ban):
    """So theo ranh gioi tu — chan CA HAI ben, khong chan ranh gioi CUM.

    Ban 1 chi chan ben PHAI. Hau qua: "ho" khop vao duoi chu "cho", nen
    "cho uong ha sot" bi tinh la da nhac toi trieu chung "ho" — 3/4 ca
    moi_bia bao hong deu la loi nay, khong phai loi mo hinh.

    Chan ben trai bang lookbehind. Van phai khop duoc tien to cua mot CUM
    ("ho" trong "ho khan", "2 ngay" trong "sot 2 ngay nay") vi phep kiem
    dinh_chinh dua vao do — nen chi chan ky tu chu, khong chan dau cach.
    """
    return re.search(rf"(?<![\wÀ-ỹ]){re.escape(cum)}(?![\wÀ-ỹ])",
                     van_ban or "", re.I) is not None


def _gop(p):
    """Gop cac truong van ban cua mot phat bieu de tim cum."""
    return " ".join(str(p.get(k, "")) for k in ("noi_dung", "thoi_gian_su_kien", "moc_thoi_gian"))


# --------------------------------------------------------------- phep kiem

def kiem_chu_the(mau, ps):
    """Di ung cua ME phai duoc gan cho ME.

    SUA 10/09/2026 — LO~ HONG: ban truoc kiem the PHU DINH, "chu the khong khop
    (tre|be|chau|em be)". Mot he thong ghi `chu_the = "benh nhan"` cho di ung
    cua me thi LOT QUA, vi "benh nhan" khong khop bang tu do. Doi chung tam
    thuong `benh_nhan` — gan MOI menh de cho benh nhan — dat 60/60 = 100% o
    nhom nay, trong khi no sai toan bo.
    """
    thuoc = mau["thuoc"]
    lien_quan = [p for p in ps if _co(thuoc, _gop(p))]
    if not lien_quan:
        return False, "khong trich duoc di ung nao"
    # Kiem the KHANG DINH: phai co mot phat bieu gan cho NGUOI NHA. Hang so
    # `ME` duoc khai tu dau nhung chua bao gio duoc dung — mot hang so khong ai
    # doc la dau hieu phep kiem chua lam dung viec no mo ta.
    dung = [p for p in lien_quan if ME.search(str(p.get("chu_the", "")))]
    if dung:
        return True, ""
    ai = ", ".join(sorted({str(p.get("chu_the") or "?") for p in lien_quan}))
    return False, f"gan di ung {thuoc} cho {ai} thay vi cho nguoi nha"


def kiem_chac_chan(mau, ps):
    """"Chua thay bi bao gio" phai giu la 'chua ghi nhan', khong thanh phu dinh chac chan."""
    tc = mau["trieu_chung"]
    lien_quan = [p for p in ps if _co(tc, _gop(p))]
    if not lien_quan:
        return False, f"khong trich duoc gi ve {tc}"
    for p in lien_quan:
        if p.get("do_chac_chan") == "chưa ghi nhận":
            return True, ""
    return False, "nang 'chua ghi nhan' thanh muc chac chan khac"


def kiem_dinh_chinh(mau, ps):
    """Giu moc MOI, va moc CU khong duoc dung nhu mot su that ngang hang.

    BAN 1 CUA PHEP KIEM NAY SAI: no bao hong neu moc cu xuat hien o BAT KY dau.
    Nhung thiet ke cua chinh du an noi phai GIU ban cu (trang_thai "bi thay the")
    de truy lai duoc rang da co dinh chinh. Phep kiem mau thuan voi thiet ke,
    va cho ket qua 0/15 trong khi mo hinh lam DUNG:

        {"noi_dung":"sốt", "moc_thoi_gian":"4 ngày", "quan_he":"không"}
        {"noi_dung":"sốt", "moc_thoi_gian":"2 ngày", "quan_he":"đính chính"}

    Ban 2: dat khi moc MOI co mat, VA (moc cu vang mat HOAC co ban ghi danh dau
    la dinh chinh). Hong khi ca hai moc cung ton tai ma khong danh dau gi —
    luc do hai moc trong ngang hang nhau va khong biet dung cai nao.
    """
    moi, cu = mau["moc_moi"], mau["moc_cu"]
    if not any(_co(moi, _gop(p)) for p in ps):
        return False, f"mat moc da dinh chinh ({moi})"
    co_moc_cu = any(_co(cu, _gop(p)) for p in ps)
    co_danh_dau = any(p.get("quan_he") == "đính chính" for p in ps)
    if co_moc_cu and not co_danh_dau:
        return False, f"giu ca hai moc ({cu} va {moi}) ma khong danh dau dinh chinh"
    return True, ""


def kiem_dien_bien(mau, ps):
    """GIU CA HAI moc — day khong phai dinh chinh."""
    van = " | ".join(_gop(p) for p in ps)
    co_cu = _co(mau["moc_cu"], van)      # "Hom qua"
    co_moi = _co(mau["moc_moi"], van)    # "hom nay"
    if co_cu and co_moi:
        return True, ""
    if co_moi and not co_cu:
        return False, "vut mat moc dau — coi dien bien la dinh chinh"
    if co_cu and not co_moi:
        return False, "vut mat moc sau"
    return False, "mat ca hai moc"


def kiem_gia_dinh(mau, ps):
    """Cau gia dinh KHONG duoc ghi thanh trieu chung da xay ra."""
    dk = mau["dieu_kien"]
    sai = [p for p in ps
           if _co(dk, _gop(p)) and p.get("tinh_huong", "thực tế") == "thực tế"]
    if sai:
        return False, f"ghi '{dk}' thanh trieu chung thuc te"
    return True, ""


def kiem_moi_bia(mau, ps):
    """Cau hoi khong ai tra loi thi KHONG duoc tao phat bieu."""
    moi = mau["moi_khong_duoc_tra_loi"]
    sai = [p for p in ps if _co(moi, _gop(p))]
    if sai:
        return False, f"tu dien '{moi}' du khong ai tra loi"
    return True, ""


def kiem_sach(mau, ps):
    """Nhom doi chung: khong duoc canh giac qua muc."""
    if not ps:
        return False, "khong trich duoc gi"
    bao_dong_gia = [p for p in ps
                    if p.get("do_chac_chan") == "chưa ghi nhận"
                    or p.get("tinh_huong", "thực tế") != "thực tế"]
    if bao_dong_gia:
        return False, f"{len(bao_dong_gia)} bao dong gia tren hoi thoai binh thuong"
    return True, ""


# --------------------------------------------------------- phep kiem CHEO
# Bay phep kiem tren chi kiem BAY RIENG cua tung tinh huong. Mot mo hinh co
# the tranh duoc ca bay bay ma van gan sai chu the o nhung ban ghi khac —
# va con so tong se khong he phan anh dieu do.
#
# Da xay ra that: o lan do 4B, bang tinh huong cho 103/105 = 98%, nhung 17
# ban ghi ghi TUOI CUA TRE lai gan chu the la "nguoi nha". Khong phep kiem
# nao trong bay cai do cham toi, vi no khong phai bay cua tinh huong nao.
#
# Nen phai co mot lop kiem chay tren MOI mau, va bao cao RIENG.

TRE_TRONG_NOI_DUNG = re.compile(
    r"(?i)(cháu|bé|trẻ|con)\s+\S+\s+tuổi|(cháu|bé|trẻ)\s+(nặng|cao)\s")


def kiem_cheo(mau, ps):
    """-> danh sach loi tim thay tren MOT mau, khong phu thuoc tinh huong."""
    loi = []
    for i, p in enumerate(ps):
        nd = str(p.get("noi_dung", ""))
        ct = str(p.get("chu_the", "")).strip()
        if TRE_TRONG_NOI_DUNG.search(nd) and not TRE.match(ct):
            loi.append({"chi_so": i, "loai": "chu_the_cua_dac_diem_tre",
                        "chu_the": ct, "noi_dung": nd})
    return loi


def kiem_nghi_ngo(mau, ps):
    """Thach thuc 3 — "nghi" khong duoc nang thanh chan doan xac dinh.

    Bay nay co HAI ve, va chi bat mot ve thi phep do khong day du:

      nang muc   ghi benh nghi thanh `chac chan`  -> sai
      bo han     khong nhac gi toi benh nghi      -> cung sai, theo cach khac

    `_bay_nghi_ngo` ghi ro ca hai trong chu thich cua no, nhung truoc
    10/09/2026 `PHEP_KIEM` KHONG co muc nay: bo sinh co 9 tinh huong con bo
    cham chi co 7, va `cham()` nem `KeyError` khi gap `nghi_ngo` hoac
    `nhat_quan`. Nghia la hai nhom do chua bao gio duoc cham.
    """
    benh = mau["benh_nghi"]
    lien_quan = [p for p in ps if _co(benh, _gop(p))]
    if not lien_quan:
        return False, f"bo han thong tin nghi {benh}"
    nang = [p for p in lien_quan
            if p.get("do_chac_chan", "chắc chắn") == "chắc chắn"]
    if nang and not any(p.get("do_chac_chan") == "nghi ngờ"
                        for p in lien_quan):
        return False, f"nang 'nghi {benh}' thanh chan doan chac chan"
    return True, ""


def kiem_nhat_quan(mau, ps):
    """Thach thuc 5 — thuoc DA NGUNG khong duoc con o dang 'dang dung'.

    Loai loi nay khong phep do nao trong du an bat duoc truoc 09/09/2026:
    ROUGE dem tu nen hai cau deu khop, diem quy gan chi xet chu the, va sau
    nhom bay cu deu chi xet MOT cau mot.
    """
    thuoc = mau["thuoc_da_ngung"]
    lien_quan = [p for p in ps if _co(thuoc, _gop(p))]
    if not lien_quan:
        return False, f"bo han thuoc {thuoc}"
    # Da ngung thi phai co dau vet cua viec ngung: trang thai bi thay the,
    # hoac chinh noi dung noi ro la da ngung.
    co_dau_vet = any(
        p.get("trang_thai") not in (None, "còn hiệu lực")
        or re.search(r"(?i)(đã )?ngừng|ngưng|thôi không|dừng", _gop(p))
        for p in lien_quan)
    if not co_dau_vet:
        return False, f"ghi {thuoc} ma khong ghi la DA NGUNG"
    return True, ""


PHEP_KIEM = {
    "chu_the": kiem_chu_the, "chac_chan": kiem_chac_chan,
    "dinh_chinh": kiem_dinh_chinh, "dien_bien": kiem_dien_bien,
    "gia_dinh": kiem_gia_dinh, "moi_bia": kiem_moi_bia, "sach": kiem_sach,
    "nghi_ngo": kiem_nghi_ngo, "nhat_quan": kiem_nhat_quan,
}


def cham(mau, ps):
    if not ps:
        return False, "khong co phat bieu nao"
    return PHEP_KIEM[mau["bay"]](mau, ps)


def cham_lai(duong_dan_json):
    """Cham lai tu du lieu da luu, khong chay lai mo hinh."""
    chi_tiet = json.loads(open(duong_dan_json, encoding="utf-8").read())
    theo_bay = {}
    for c in chi_tiet:
        if "phat_bieu" not in c:
            raise SystemExit("Tep cu khong luu phat bieu tho — phai chay lai mo hinh")
        dat, ly_do = cham(c["dap_an"], c["phat_bieu"] or [])
        c["dat"], c["ly_do"] = dat, ly_do
        c["loi_cheo"] = kiem_cheo(c["dap_an"], c["phat_bieu"] or [])
        theo_bay.setdefault(c["bay"], []).append(dat)
    return chi_tiet, theo_bay


def in_kiem_cheo(chi_tiet):
    """In RIENG khoi bang tinh huong. Gop vao mot con so la giau mat no."""
    tong_pb = sum(len(c["phat_bieu"] or []) for c in chi_tiet)
    tong_cheo = sum(len(c.get("loi_cheo") or []) for c in chi_tiet)
    print("")
    print("Kiem CHEO (chay tren moi mau, khong phu thuoc tinh huong):")
    print(f"  {tong_cheo}/{tong_pb} ban ghi gan sai chu the "
          f"= {100 * tong_cheo / max(1, tong_pb):.0f}%")
    print("  Bang tinh huong o tren chi do BAY RIENG cua tung tinh huong.")
    print("  Mot mo hinh tranh duoc ca bay bay van co the sai o cho khac.")


def in_bang(theo_bay):
    from src import sinh_bo_chan_doan
    print(f"\n{'Tinh huong':14}{'Dat':>8}{'Ty le':>9}")
    for bay in sinh_bo_chan_doan.BAY:
        ds = theo_bay.get(bay, [])
        if ds:
            print(f"{bay:14}{sum(ds):>4}/{len(ds):<3}{100*sum(ds)/len(ds):>8.0f}%")
    tong = [d for ds in theo_bay.values() for d in ds]
    print(f"{'TONG':14}{sum(tong):>4}/{len(tong):<3}{100*sum(tong)/len(tong):>8.0f}%")


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model")
    ap.add_argument("--cham-lai", help="cham lai tu tep ket qua da luu, khong chay mo hinh")
    ap.add_argument("--n", type=int, default=15, help="so mau MOI tinh huong")
    a = ap.parse_args()

    from src import du_lieu, duong_dan, sinh_bo_chan_doan

    if a.cham_lai:
        dp = duong_dan.THU_MUC_KET_QUA / a.cham_lai
        chi_tiet, theo_bay = cham_lai(dp)
        print(f"Cham lai {len(chi_tiet)} mau tu {dp.name} (khong chay mo hinh)")
        in_bang(theo_bay)
        in_kiem_cheo(chi_tiet)
        dp.write_text(json.dumps(chi_tiet, ensure_ascii=False, indent=2), encoding="utf-8")
        return

    if not a.model:
        ap.error("can --model hoac --cham-lai")

    bo = sinh_bo_chan_doan.sinh_bo(a.n, seed=42)
    print(f"Do {a.model} tren {len(bo)} mau ({len(sinh_bo_chan_doan.BAY)} tinh huong x {a.n})")

    kq_tho = bakeoff.chay(a.model, bo, ep_json=True)

    theo_bay = {}
    chi_tiet = []
    for mau, kq in zip(bo, kq_tho):
        ps = kq["phat_bieu"] or []
        dat, ly_do = cham(mau, ps)
        loi_cheo = kiem_cheo(mau, ps)
        theo_bay.setdefault(mau["bay"], []).append(dat)
        # Luu ca PHAT BIEU THO va DAP AN cua mau: neu phep cham sai va phai
        # sua, cham lai duoc offline ma khong phai chay lai mo hinh (mat 20 phut).
        chi_tiet.append({"id": mau["id"], "bay": mau["bay"], "dat": dat,
                         "ly_do": ly_do, "json_hop_le": kq["json_hop_le"],
                         "loi_cheo": loi_cheo,
                         "phat_bieu": ps,
                         "dap_an": {k: v for k, v in mau.items()
                                    if k not in ("input", "output")}})

    in_bang(theo_bay)

    in_kiem_cheo(chi_tiet)

    ten = a.model.split("/")[-1].replace(".", "_")
    dp = duong_dan.THU_MUC_KET_QUA / f"chan-doan-{ten}.json"
    dp.write_text(json.dumps(chi_tiet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nChi tiet: {dp}")


if __name__ == "__main__":
    main()
