# -*- coding: utf-8 -*-
"""Chung chi thuoc do MO RONG: thuoc do chu co nhin thay loi phu dinh, loi thoi gian,
loi ke hoach ghi thanh da lam khong (22/09/2026). Gia thuyet H3.

`src/chung_chi_thuoc_do.py` da chung minh cho loi DOI CHU THE: ROUGE-1 = 1,0000.
Tep nay lam ba kieu loi con lai cua dinh nghia "loi nguy hiem".

CACH LAM. Moi ca tap phat trien:
  1. Lay trich HOAN HAO (dap an), cho qua nhanh B -> van ban ho so GOC.
  2. Lam hong DUNG MOT menh de theo mot kieu:
       phu_dinh     dao phu dinh cua mot menh de "chắc chắn"        (doi 1 tu)
       thoi_gian    qua khu <-> hien tai                             (thuong doi muc)
       ke_hoach_thanh_da_lam  tinh_huong "kế hoạch"->"thực tế" VA hanh_vi "kế hoạch"->"quan sát"
       tinh_huong_mot_truong  chi doi tinh_huong. `sinh_benh_an` xep muc ke hoach theo
                    tinh_huong HOAC hanh_vi, nen van ban KHONG doi — kieu nay chi de chung
                    minh hai truong du phong nhau, khong phai phep thu H3
       vo_hai       DOI CHUNG: thay mot tu bang tu dong nghia 1-1     (doi 1 tu)
     roi cho qua dung nhanh B -> van ban ho so da lam hong.
  3. Cham ban lam hong bang HAI loai thuoc do:
       chu   ROUGE-1 va diem cuoi cuoc thi VAIC, so voi van ban GOC
       cau truc  bo cham menh de `cham_he_thong` (phien ban hien tai), so voi dap an

Doc: loi nguy hiem PHAI bi phat nang hon doi chung. Thuoc do nao cho ban nguy hiem
diem cao ngang hoac cao hon ban vo hai thi mu truoc loi do.

SO SANH CAP: moi kieu loi so voi doi chung TREN CUNG TAP CA (ca vua lam hong duoc
theo kieu do, vua co tu dong nghia de lam doi chung).

    python tools/chung-chi-mo-rong.py
"""
import io
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import cham_diem, cham_he_thong as ch, du_lieu, du_lieu_trich, nhanh  # noqa: E402

HAT = 2026
# Chi cap 1 am tiet <-> 1 am tiet, de so tu bi doi bang voi loi phu dinh (1 tu).
DONG_NGHIA_1 = (("nhiều", "lắm"), ("nôn", "ói"), ("uống", "dùng"), ("đau", "nhức"))
KIEU = ("phu_dinh", "thoi_gian", "ke_hoach_thanh_da_lam", "tinh_huong_mot_truong", "vo_hai")
MA_BAT = {"phu_dinh": "sai_muc_phu_dinh", "thoi_gian": "sai_thoi_gian",
          "ke_hoach_thanh_da_lam": "sai_muc_tinh_huong",
          "tinh_huong_mot_truong": "sai_muc_tinh_huong", "vo_hai": None}


def ung_vien(ps, kieu):
    """Chi so cac menh de lam hong duoc theo `kieu`."""
    ra = []
    for i, p in enumerate(ps):
        if kieu == "phu_dinh" and (p.get("do_chac_chan") or "chắc chắn") == "chắc chắn" \
                and (p.get("tinh_huong") or "thực tế") == "thực tế":
            ra.append(i)
        elif kieu == "thoi_gian" and p.get("thoi_gian_su_kien") in ("quá khứ", "hiện tại"):
            ra.append(i)
        elif kieu in ("ke_hoach_thanh_da_lam", "tinh_huong_mot_truong")                 and p.get("tinh_huong") == "kế hoạch":
            ra.append(i)
        elif kieu == "vo_hai" and any(re.search(rf"(?<!\w){a}(?!\w)", p.get("noi_dung") or "")
                                      for a, _b in DONG_NGHIA_1):
            ra.append(i)
    return ra


def lam_hong(ps, kieu, i):
    q = [dict(p) for p in ps]
    p = q[i]
    if kieu == "phu_dinh":
        p["phu_dinh"] = not p.get("phu_dinh")
    elif kieu == "thoi_gian":
        p["thoi_gian_su_kien"] = "hiện tại" if p["thoi_gian_su_kien"] == "quá khứ" else "quá khứ"
    elif kieu == "tinh_huong_mot_truong":
        # Chi doi mot truong. `sinh_benh_an` xep vao muc ke hoach neu tinh_huong HOAC
        # hanh_vi la "kế hoạch" — hai truong du phong nhau, nen van ban KHONG doi.
        p["tinh_huong"] = "thực tế"
    elif kieu == "ke_hoach_thanh_da_lam":
        # Loi that su den tay nguoi doc: ca hai truong deu noi "da lam, da thay".
        p["tinh_huong"] = "thực tế"
        p["hanh_vi"] = "quan sát"
    elif kieu == "vo_hai":
        for a, b in DONG_NGHIA_1:
            moi = re.sub(rf"(?<!\w){a}(?!\w)", b, p["noi_dung"], count=1)
            if moi != p["noi_dung"]:
                p["noi_dung"] = moi
                break
    return q


def chay_b(cac_ca, cac_ps):
    kq_tho = [{"id": ca["id"], "phat_bieu": ps} for ca, ps in zip(cac_ca, cac_ps)]
    ra = nhanh.chay_trung_gian(cac_ca, None, None, None, "B", kq_tho=kq_tho)
    return {r["id"]: r for r in ra}


def f1_cau_truc(ca, r):
    k = ch.cham_ca(ca, r)
    return k["f1_tu"] / k["f1_mau"] if k["f1_mau"] else 1.0, k


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ds = du_lieu.nap_mau(Path("data/viet_phat_trien.jsonl"))
    goc_ps = {ca["id"]: json.loads(du_lieu_trich.doi_mot_ca(ca)[1])["phat_bieu"] for ca in ds}

    # Chon san menh de cho moi kieu, mot lan, hat co dinh.
    rng = random.Random(HAT)
    chon = {k: {} for k in KIEU}
    for ca in ds:
        for k in KIEU:
            u = ung_vien(goc_ps[ca["id"]], k)
            if u:
                chon[k][ca["id"]] = rng.choice(u)

    import contextlib
    im = io.StringIO()
    with contextlib.redirect_stdout(im):          # chay_trung_gian in tung ca
        goc = chay_b(ds, [goc_ps[ca["id"]] for ca in ds])
        hong = {}
        for k in KIEU:
            cac = [ca for ca in ds if ca["id"] in chon[k]]
            hong[k] = chay_b(cac, [lam_hong(goc_ps[ca["id"]], k, chon[k][ca["id"]]) for ca in cac])

    theo_ca = {k: {} for k in KIEU}
    for k in KIEU:
        for i, r in hong[k].items():
            ca = next(c for c in ds if c["id"] == i)
            vb_goc, vb_hong = goc[i]["du_doan"], r["du_doan"]
            d = cham_diem.diem_cuoi(vb_hong, vb_goc)
            f1, dem = f1_cau_truc(ca, r)
            f1_0, _ = f1_cau_truc(ca, goc[i])
            ma = MA_BAT[k]
            theo_ca[k][i] = {"rouge1": d["rouge1"], "vaic": d["final"] if "final" in d else d.get("diem_cuoi"),
                             "f1_cau_truc": f1, "f1_cau_truc_goc": f1_0,
                             "van_ban_doi": vb_goc != vb_hong,
                             "bat": bool(ma and dem.get(ma, 0) > 0),
                             "bat_bat_ky": dem.get("loi_bat_ky", 0) > ch.cham_ca(ca, goc[i]).get("loi_bat_ky", 0)}

    ra = {}
    print("| Kiểu làm hỏng | Cặp | Văn bản đổi | ROUGE-1 hỏng / đối chứng | Điểm VAIC hỏng / đối chứng | F₁ cấu trúc hỏng / đối chứng | Bộ chấm bắt đúng mã |")
    print("|---|---|---|---|---|---|---|")
    for k in ("phu_dinh", "thoi_gian", "ke_hoach_thanh_da_lam", "tinh_huong_mot_truong"):
        for nhom in ("tat_ca", "van_ban_doi"):
            cap = sorted(i for i in set(theo_ca[k]) & set(theo_ca["vo_hai"])
                         if nhom == "tat_ca" or theo_ca[k][i]["van_ban_doi"])
            if not cap:
                continue
            tb = lambda kk, f: sum(theo_ca[kk][i][f] for i in cap) / len(cap)
            doi = sum(theo_ca[k][i]["van_ban_doi"] for i in cap)
            bat = sum(theo_ca[k][i]["bat"] for i in cap)
            vh_bat = sum(theo_ca["vo_hai"][i]["bat_bat_ky"] for i in cap)
            x = {"so_cap": len(cap), "rouge1": [tb(k, "rouge1"), tb("vo_hai", "rouge1")],
                 "vaic": [tb(k, "vaic"), tb("vo_hai", "vaic")],
                 "f1_cau_truc": [tb(k, "f1_cau_truc"), tb("vo_hai", "f1_cau_truc")],
                 "f1_cau_truc_goc": tb(k, "f1_cau_truc_goc"),
                 "van_ban_doi": doi, "bo_cham_bat": bat, "doi_chung_bi_bat_oan": vh_bat}
            ra[f"{k}/{nhom}"] = x
            nhan = k if nhom == "tat_ca" else f"  └ chỉ ca văn bản đổi"
            print(f"| {nhan} | {len(cap)} | {doi}/{len(cap)} | {x['rouge1'][0]:.4f} / {x['rouge1'][1]:.4f} "
                  f"| {x['vaic'][0]:.4f} / {x['vaic'][1]:.4f} | {x['f1_cau_truc'][0]:.4f} / {x['f1_cau_truc'][1]:.4f} "
                  f"| {bat}/{len(cap)} (đối chứng bị tính lỗi {vh_bat}/{len(cap)}) |")
    ra["_ghi_chu"] = {"tap": "viet_phat_trien", "so_ca": len(ds), "hat": HAT, "nhanh": "B",
                      "phien_ban_bo_cham": ch.PHIEN_BAN, "doi_chung": [list(x) for x in DONG_NGHIA_1]}
    Path("docs/ket-qua/chung-chi-mo-rong.json").write_text(
        json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nghi docs/ket-qua/chung-chi-mo-rong.json")


if __name__ == "__main__":
    main()
