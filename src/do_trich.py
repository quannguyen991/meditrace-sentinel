# -*- coding: utf-8 -*-
"""Do CHAT LUONG KHAU TRICH truc tiep, doi chieu voi dap an cau truc.

VI SAO CAN RIENG TEP NAY. Cac phep do dang co deu do SAN PHAM CUOI (benh an),
nen chat luong khau trich bi tron voi chat luong khau sinh:

    do_bo_chan_doan   cham theo BAY cua tung tinh huong, khong cham tung menh de
    do_van_xuoi       cham ban benh an, khong cham bang phat bieu
    thuoc_do_quy_gan  doi chieu benh an voi benh an, nhay voi cach dong goi cau

Bo `hoi_thoai_viet.jsonl` co dap an o muc MENH DE, nen do thang duoc:
mo hinh trich ra bao nhieu menh de dung, va trong so do bao nhieu phan gan
dung nguoi.

BA CON SO, khong gop lam mot:

    tim_thay      bao nhieu menh de trong dap an duoc trich ra (nho lai)
    dung_chu_the  trong so menh de tim thay, bao nhieu phan gan DUNG nguoi
    khac_bn       ba con so tren, tinh RIENG cho cac menh de KHONG thuoc
                  benh nhan — chi 2,8% tong so nhung la toan bo phan do
                  quy gan. Gop chung thi 97% menh de de gan se che mat no.

CACH GHEP MENH DE. Dap an va ban trich khong bao gio trung tung chu, nen
ghep theo do chong lap tu (F1 tren tap tu), nguong 0,6. Ghep tham lam theo
diem giam dan, moi ben dung mot lan.

    python -m src.do_trich --tep trich_giu_lai_hl.jsonl --dap-an trich_giu_lai
"""
import io
import json
import re
import sys

NGUONG_GHEP = 0.6


def _tu(s):
    return [t for t in re.split(r"[^\wÀ-ỹ]+", str(s or "").lower()) if t]


def do_giong(a, b):
    """F1 tren tap tu. Khong dung khop nguyen van vi hai ben khong bao gio
    trung tung chu."""
    ta, tb = set(_tu(a)), set(_tu(b))
    if not ta or not tb:
        return 0.0
    chung = len(ta & tb)
    if not chung:
        return 0.0
    p, r = chung / len(tb), chung / len(ta)
    return 2 * p * r / (p + r)


def ghep(dap_an, trich, nguong=NGUONG_GHEP):
    """-> (cap_da_ghep, dap_an_khong_tim_thay, trich_thua).

    Ghep THAM LAM theo diem giam dan, moi ben dung mot lan. Khong ghep mot
    menh de dap an voi nhieu ban trich: lam the thi mot ban trich dung se
    che duoc nhieu ban sai.
    """
    diem = []
    for i, d in enumerate(dap_an):
        for j, t in enumerate(trich):
            s = do_giong(d.get("noi_dung"), t.get("noi_dung"))
            if s >= nguong:
                diem.append((s, i, j))
    diem.sort(reverse=True)
    da_d, da_t, cap = set(), set(), []
    for s, i, j in diem:
        if i in da_d or j in da_t:
            continue
        da_d.add(i)
        da_t.add(j)
        cap.append((dap_an[i], trich[j], s))
    thieu = [d for i, d in enumerate(dap_an) if i not in da_d]
    thua = [t for j, t in enumerate(trich) if j not in da_t]
    return cap, thieu, thua


# Cach goi benh nhan trong dap an va trong ban trich khong nhat thiet trung
# chu. Coi la CUNG mot nguoi neu ca hai deu nam trong ro nay.
RO_BENH_NHAN = {"bệnh nhân", "trẻ", "bé", "cháu", "con", "em bé", "bệnh nhi",
                "trẻ nhỏ", "bn"}


def cung_nguoi(a, b):
    a, b = str(a or "").strip().lower(), str(b or "").strip().lower()
    if a == b:
        return True
    return a in RO_BENH_NHAN and b in RO_BENH_NHAN


def _luot(m, *khoa):
    """Tap so luot cua mot menh de. Dap an dung khoa `luot`, ban trich dung
    `luot_thoai` — nen phai nhan ca hai ten."""
    for k in khoa:
        v = m.get(k)
        if v:
            return {int(x) for x in v if isinstance(x, (int, float))}
    return set()


def cham_can_cu(cap):
    """Do nua THU HAI cua thach thuc 4: co DAN DUNG luot thoai nguon khong.

    VI SAO TACH RIENG (them 10/09/2026). Thach thuc 4 goi la "lien ket chu the
    va can cu bang chung", va no gom HAI viec:

        gan dung nguoi   thong tin nay thuoc ve ai
        dan dung nguon   thong tin nay dua vao cau nao

    Truoc do chi do duoc viec dau. Mot he thong co the gan DUNG nguoi ma DAN
    SAI luot thoai, va khong phep do nao cua du an bat duoc — trong khi truy
    vet bang chung la chinh dieu du an dat ten.

    Dem theo TUNG MENH DE roi lay trung binh, khong gop tat ca luot lai:
    mot menh de dan dung 2/2 luot va mot menh de dan sai ca 2/2 phai ra 50%,
    khong phai mot ty le gop lam mo mat ca hai.
    """
    du = sot = thua = 0
    khop_hoan_toan = 0
    xet = 0
    for d, t, _s in cap:
        that = _luot(d, "luot", "luot_thoai")
        doan = _luot(t, "luot_thoai", "luot")
        if not that:
            continue                  # dap an khong co luot thi khong do duoc
        xet += 1
        du += len(that & doan)
        sot += len(that - doan)
        thua += len(doan - that)
        khop_hoan_toan += (that == doan)
    return {
        "so_menh_de_xet": xet,
        "luot_dung": du,
        "luot_sot": sot,
        "luot_thua": thua,
        "do_phu": du / max(1, du + sot),
        "do_chuan": du / max(1, du + thua),
        "khop_hoan_toan": khop_hoan_toan,
        "ty_le_khop_hoan_toan": khop_hoan_toan / max(1, xet),
    }


def cham(danh_sach):
    """danh_sach: [(dap_an_menh_de_list, trich_menh_de_list)] cho tung ca."""
    tong_da = tong_tim = tong_dung = 0
    kb_da = kb_tim = kb_dung = 0
    tong_thua = 0
    loi = []
    moi_cap = []
    for dap_an, trich in danh_sach:
        cap, thieu, thua = ghep(dap_an, trich)
        moi_cap.extend(cap)
        tong_da += len(dap_an)
        tong_tim += len(cap)
        tong_thua += len(thua)
        kb_da += sum(1 for d in dap_an if d.get("chu_the") not in RO_BENH_NHAN)
        for d, t, _s in cap:
            khac_bn = d.get("chu_the") not in RO_BENH_NHAN
            dung = cung_nguoi(d.get("chu_the"), t.get("chu_the"))
            tong_dung += dung
            if khac_bn:
                kb_tim += 1
                kb_dung += dung
            if not dung:
                loi.append({"noi_dung": d.get("noi_dung"),
                            "dap_an": d.get("chu_the"),
                            "trich": t.get("chu_the"),
                            "khac_benh_nhan": khac_bn})
    return {
        "can_cu": cham_can_cu(moi_cap),
        "menh_de_dap_an": tong_da,
        "tim_thay": tong_tim,
        "ty_le_tim_thay": tong_tim / max(1, tong_da),
        "dung_chu_the": tong_dung,
        "ty_le_dung_chu_the": tong_dung / max(1, tong_tim),
        "trich_thua": tong_thua,
        "khac_bn_dap_an": kb_da,
        "khac_bn_tim_thay": kb_tim,
        "khac_bn_ty_le_tim_thay": kb_tim / max(1, kb_da),
        "khac_bn_dung": kb_dung,
        "khac_bn_ty_le_dung": kb_dung / max(1, kb_tim),
        "loi": loi,
    }


def in_bang(k, ten=""):
    print("")
    print(f"{ten}")
    print(f"  Menh de trong dap an        {k['menh_de_dap_an']:6}")
    print(f"  Trich ra va ghep duoc       {k['tim_thay']:6}"
          f"   ({100 * k['ty_le_tim_thay']:.1f}%)")
    print(f"  Trong so do, gan DUNG nguoi {k['dung_chu_the']:6}"
          f"   ({100 * k['ty_le_dung_chu_the']:.1f}%)")
    print(f"  Ban trich thua (khong ghep) {k['trich_thua']:6}")
    print(f"  --- rieng menh de KHONG thuoc benh nhan ---")
    print(f"  Trong dap an                {k['khac_bn_dap_an']:6}")
    print(f"  Ghep duoc                   {k['khac_bn_tim_thay']:6}"
          f"   ({100 * k['khac_bn_ty_le_tim_thay']:.1f}%)")
    print(f"  Gan DUNG nguoi              {k['khac_bn_dung']:6}"
          f"   ({100 * k['khac_bn_ty_le_dung']:.1f}%)")
    cc = k.get("can_cu")
    if cc:
        print(f"  --- nua thu hai cua thach thuc 4: DAN DUNG NGUON ---")
        print(f"  Menh de do duoc             {cc['so_menh_de_xet']:6}")
        print(f"  Luot dan dung               {cc['luot_dung']:6}")
        print(f"  Luot bo sot                 {cc['luot_sot']:6}")
        print(f"  Luot dan thua               {cc['luot_thua']:6}")
        print(f"  Do phu / do chuan           "
              f"{100 * cc['do_phu']:.1f}% / {100 * cc['do_chuan']:.1f}%")
        print(f"  Dan DUNG HET, khong thua    {cc['khop_hoan_toan']:6}"
              f"   ({100 * cc['ty_le_khop_hoan_toan']:.1f}%)")


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tep", nargs="+", required=True,
                    help="tep trich_*.jsonl trong data/")
    ap.add_argument("--dap-an", default="hoi_thoai_viet",
                    help="ten tep nguon chua dap an (khong duoi)")
    a = ap.parse_args()

    from src import duong_dan
    d = duong_dan.THU_MUC_DU_LIEU

    # Bo ban sao ly do kham khoi dap an: tu 11/09/2026 nhan huan luyen khong con
    # chung (`du_lieu_trich.ban_lap_ly_do_kham`), giu lai thi moi ca mat oan mot
    # menh de "khong tim thay". So do truoc ngay do tinh CA ban sao o hai phia.
    from src.du_lieu_trich import ban_lap_ly_do_kham
    goc = {}
    for x in open(d / f"{a.dap_an}.jsonl", encoding="utf-8"):
        if x.strip():
            k = json.loads(x)
            da = k.get("dap_an") or []
            lap = ban_lap_ly_do_kham(da)
            goc[k["id"]] = [m for i, m in enumerate(da) if i not in lap]

    for t in a.tep:
        dp = d / t
        if not dp.exists():
            print(f"(chua co {t})")
            continue
        cap = []
        for x in open(dp, encoding="utf-8"):
            if not x.strip():
                continue
            k = json.loads(x)
            if k["id"] not in goc:
                continue
            cap.append((goc[k["id"]], k.get("phat_bieu") or []))
        if not cap:
            print(f"({t}: khong ca nao khop id voi dap an)")
            continue
        kq = cham(cap)
        in_bang(kq, ten=f"{t}  ({len(cap)} ca)")
        (duong_dan.THU_MUC_KET_QUA / f"do-trich-{t}.json").write_text(
            json.dumps(kq, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
