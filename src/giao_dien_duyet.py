# -*- coding: utf-8 -*-
"""Tang 7 — BAN DUYET 3 cot: mot tep HTML tu chua, mo bang trinh duyet la chay.

    hoi thoai              ban nhap benh an             chi tiet + quyet dinh
    (to dam doan duoc dan)  (moi dong la mot phat bieu)  (khoa, rui ro, lich su)

Bam mot dong -> to dam DUNG doan hoi thoai ma dong do dua vao. Vi tri lay tu
chinh tang khoa (`khoa_bang_chung`, vi tri tren luot da chuan NFC), khong tim lai
bang chuoi o trinh duyet — hai noi tim hai kieu thi to dam lech ma khong ai biet.

Nguoi duyet Xac nhan / Sua / Loai tung dong. Quyet dinh luu trong localStorage cua
may do (moi may mot kho rieng) va xuat duoc thanh JSON — de thanh du lieu phan hoi.

THOI GIAN DUYET: trang do tren may dang mo, de thu giao dien. CHUA CO so lieu bac
si that; khong duoc bao cao con so do nhu ket qua.

    python -m src.giao_dien_duyet --tep data/ra_C_khoa_hoi_viet_phat_trien.jsonl --n 20
    python -m src.giao_dien_duyet --minh-hoa
"""
import argparse
import hashlib
import io
import json
import random
import sys
from pathlib import Path

from src import duong_dan, khoa_bang_chung, sinh_benh_an

MAU = Path(__file__).with_name("ban_duyet_mau.html")
DAU_THAN = "<!--THAN-->"
GHI_CHU_MINH_HOA = ("Đáp án bộ tự sinh qua đúng đường ống, có cấy lỗi có chủ đích. "
                    "Không phải đầu ra mô hình.")
TRUONG_GON = ("noi_dung", "chu_the_id", "ten_chu_the", "nguoi_noi", "do_chac_chan",
              "phu_dinh", "tinh_huong", "moc_thoi_gian", "thoi_gian_su_kien",
              "trang_thai", "quan_he", "quan_he_voi", "bang_chung", "trich_dan",
              "hanh_vi")


def _vi_tri_trich(p, cac_luot):
    """Nhanh KHONG chay khoa (B, C): tim vi tri trich dan bang CHINH ham cua khoa."""
    doan = []
    bc = [n for n in (p.get("bang_chung") or []) if n in cac_luot]
    for t in p.get("trich_dan") or []:
        for n in bc + [s for s in cac_luot if s not in bc]:
            vt = khoa_bang_chung.tim_trich(t, cac_luot[n][1])
            if vt:
                doan.append([n, vt[0], vt[1]])
                break
    return doan


def ca_cho_trang(r) -> dict:
    """Mot ban ghi cua nhanh (C_khoa_hoi, C_khoa, C...) -> du lieu gon cho trang."""
    cac_luot = khoa_bang_chung._luot(r["input"])     # CUNG ban voi vi tri cua khoa
    ps = {p["id"]: p for p in r.get("phat_bieu") or []}
    khoa = {}
    for k in r.get("khoa") or []:
        khoa[k["id"]] = {"chan": k.get("chan", []), "canh_bao": k.get("canh_bao", []),
                         "doan": [list(x) for x in k.get("doan", [])]}
    for pid, p in ps.items():
        if pid not in khoa:
            khoa[pid] = {"chan": [], "canh_bao": [], "doan": _vi_tri_trich(p, cac_luot),
                         "khong_co_khoa": True}
    dong = []
    for g in r.get("ghi_chu") or []:
        van = g.get("van")
        if not van:
            p = ps.get(g["id"])
            van = sinh_benh_an.dien_dat(p) if p else g.get("noi_dung", "")
        dong.append({"id": g["id"], "muc": g["muc"], "ly_do": g.get("ly_do"), "van": van})
    return {
        "id": r["id"],
        "luot": [[n, vai, van] for n, (vai, van) in sorted(cac_luot.items())],
        "dong": dong,
        "phat_bieu": {str(k): {t: v.get(t) for t in TRUONG_GON} for k, v in ps.items()},
        "khoa": {str(k): v for k, v in khoa.items()},
        "rui_ro": {str(d["id"]): d for d in r.get("rui_ro") or []},
        "chua_ghi": [{"luot": d["luot"], "a": d["bat_dau"], "b": d["ket_thuc"],
                      "doan": d["doan"]} for d in r.get("doan_chua_ghi") or []],
        "cau_hoi": [{"van": c["van"], "ly_do": c["ly_do"],
                     "muc_tieu": [int(x) for x in c.get("muc_tieu", {})]}
                    for c in r.get("cau_hoi") or []],
        "lich_su": r.get("lich_su") or [],
    }


def du_lieu_trang(ban_ghi, ten_bo, minh_hoa=False, ghi_chu_nguon=""):
    dl = {"ten_bo": ten_bo, "minh_hoa": minh_hoa, "ghi_chu_nguon": ghi_chu_nguon,
          "ly_do": khoa_bang_chung.LY_DO, "thu_tu_muc": sinh_benh_an.THU_TU_MUC,
          "ca": [ca_cho_trang(r) for r in ban_ghi]}
    # Ma cua BO DU LIEU: quyet dinh luu theo ma nay, nen trang sinh tu bo khac
    # khong doc nham quyet dinh cu.
    dl["ma"] = hashlib.sha256(json.dumps(dl, ensure_ascii=False, sort_keys=True)
                              .encode("utf-8")).hexdigest()[:12]
    return dl


def dung_trang(dl, tu_chua=True) -> str:
    """`tu_chua=True`: tep HTML day du de mo tu may. False: chi phan noi dung (cho
    noi nao tu boc khung html/head/body)."""
    mau = MAU.read_text(encoding="utf-8")
    dau, than = mau.split(DAU_THAN)
    # Ban khong tu chua duoc nhung vao noi khac, thuong cam tai tep: an nut tai.
    dl = dict(dl, cho_tai=tu_chua)
    # "</" trong JSON se dong the <script> som — JSON cho phep viet "<\/".
    js = json.dumps(dl, ensure_ascii=False).replace("</", "<\\/")
    than = than.replace("__DU_LIEU__", js)
    if not tu_chua:
        return dau + than
    return ('<!doctype html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            + dau + "</head>\n<body>\n" + than + "</body>\n</html>\n")


# ------------------------------------------------------------------ minh hoa
def _cay_loi(ps, loai, rng):
    """Ba loi co ten, cay vao DAP AN truoc khi qua duong ong; loai 3 va 4 de sach."""
    if loai == 0:                                  # doi chu the
        ung = [p for p in ps if p["chu_the"] != "bệnh nhân" and "dị ứng" in p["noi_dung"]]
        ung = ung or [p for p in ps if p["chu_the"] != "bệnh nhân"]
        if ung:
            rng.choice(ung)["chu_the"] = "bệnh nhân"
    elif loai == 1:                                # nang muc khang dinh
        ung = [p for p in ps if p.get("do_chac_chan") == "nghi ngờ"]
        if ung:
            rng.choice(ung)["do_chac_chan"] = "chắc chắn"
    elif loai == 2:                                # bia trich dan
        ung = [p for p in ps if p.get("trich_dan")]
        if ung:
            p = rng.choice(ung)
            p["trich_dan"] = [f"{p['noi_dung']} từ tuần trước"]


def minh_hoa(so_ca=10, hat=11):
    """MINH HOA, KHONG phai dau ra mo hinh: dap an cua `so_ca` ca KHUON TRAIN di qua
    DUNG duong ong C_khoa_hoi (`nhanh.chay_trung_gian`), co cay loi co chu dinh."""
    from src import du_lieu_trich, nhanh
    from src import sinh_hoi_thoai_viet as sh
    tuy = [sh.TuyChon(chi_tap="train", ep_bay=("di_ung_nguoi_nha",), ep_nguoi_ke=True,
                      di_ung_cua_nguoi_ke=True),
           sh.TuyChon(chi_tap="train"),
           sh.TuyChon(chi_tap="train"),
           sh.TuyChon(chi_tap="train", ep_bay=("nguon_khac_nhau",), ep_nguoi_ke=True),
           sh.TuyChon(chi_tap="train", ep_bay=("dinh_chinh",))]
    rng = random.Random(hat)
    cases, kq_tho = [], []
    for i in range(so_ca):
        ca = sh.sinh_mot_ca(f"minh_hoa_{i + 1:02d}", random.Random(hat * 1000 + i),
                            tuy[i % len(tuy)])
        _ds, js = du_lieu_trich.doi_mot_ca(ca)
        ps = json.loads(js)["phat_bieu"]
        _cay_loi(ps, i % len(tuy), rng)
        cases.append(ca)
        kq_tho.append({"id": ca["id"], "phat_bieu": ps})
    return nhanh.chay_trung_gian(cases, None, None, None, "C_khoa_hoi", kq_tho=kq_tho)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tep", help="data/ra_<nhanh>_<tap>.jsonl")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--minh-hoa", action="store_true")
    ap.add_argument("--chi-noi-dung", action="store_true",
                    help="bo khung html/head/body")
    ap.add_argument("--ra", default=None)
    a = ap.parse_args()
    if a.minh_hoa:
        dl = du_lieu_trang(minh_hoa(), "minh hoạ", minh_hoa=True,
                           ghi_chu_nguon=GHI_CHU_MINH_HOA)
        ra = Path(a.ra) if a.ra else duong_dan.THU_MUC_KET_QUA / "ban-duyet-minh-hoa.html"
    elif a.tep:
        from src import du_lieu
        tep = Path(a.tep)
        du_lieu.chan_tap_khoa(tep.name)
        dl = du_lieu_trang(du_lieu.nap_mau(tep)[:a.n], tep.stem,
                           ghi_chu_nguon=f"Đầu ra của đường ống — {tep.name}")
        ra = Path(a.ra) if a.ra else duong_dan.THU_MUC_KET_QUA / f"ban-duyet-{tep.stem}.html"
    else:
        raise SystemExit("can --tep <ra_...jsonl> hoac --minh-hoa")
    ra.write_text(dung_trang(dl, tu_chua=not a.chi_noi_dung), encoding="utf-8")
    print(f"Ghi {len(dl['ca'])} ca -> {ra}")


if __name__ == "__main__":
    main()
