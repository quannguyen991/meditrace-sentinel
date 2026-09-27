# -*- coding: utf-8 -*-
"""Chia bo hoi thoai Viet tu sinh thanh ba tap, TACH THEO KHUON BENH.

VI SAO KHUON CHU KHONG PHAI DONG. 3.000 dong sinh ra tu 24 khuon benh; hai
dong cung khuon dung chung dan y, chung kho trieu chung, chung mach hoi
thoai — chung gan nhu la mot bai. Cat theo dong thi khuon nao cung co mat o
ca ba tap, va so tren tap kiem chi do "gap lai khuon da hoc" chu khong do
"gap khuon moi".

Da mac dung loi nay mot lan: lan chia dau tien cho khau trich cat theo dong,
va CA 24 khuon deu lot sang tap huan luyen.

    train         75 khuon
    phat_trien    13 khuon   - do, thu nghiem, chon thiet ke
    kiem_tra_cuoi 12 khuon   - MO MOT LAN, sau khi khoa thiet ke

Ty le 8/7 thay cho 3/3 (10/09/2026): voi 24 khuon thi 3 khuon giu lai la
12,5%, con chap nhan duoc. Voi 60 khuon thi 3 khuon chi con 5% — mot ket qua
tren ba khuon khong noi len duoc gi ve 60 khuon. 13/12 thay cho 8/7 (11/09/2026)
khi bo khuon len 100 — xem `SO_PHAT_TRIEN_MAC_DINH`.

DON VI DOC LAP VAN LA KHUON BENH, khong phai boi canh. Boi canh co mat o CA
BA tap la co y: no khong phai thu dang do kha nang khai quat, no la thu pha
do deu de con so `eval_loss` co nghia.

Chia bang cach xep ten khuon roi lay theo bam co dinh, khong xao ngau nhien
theo thoi gian chay — chay lai phai ra dung ba tap do.

    python -m src.tach_tap_viet --nguon hoi_thoai_viet_5000_th5.jsonl --the-he 5
"""
import hashlib
import io
import json
import sys

from src import duong_dan, van_tay_bo


def _thu_tu(ten_khuon, seed):
    """Thu tu on dinh, tai lap duoc, khong phu thuoc thu tu doc tep."""
    h = hashlib.sha256(f"{seed}:{ten_khuon}".encode()).hexdigest()
    return int(h[:12], 16)


# So khuon giu lai. Doi 11/09/2026 tu 8/7 len 13/12 khi bo khuon tang tu 60
# len 100: giu nguyen TY LE (13,3% dev, 11,7% test), khong giu nguyen SO. Voi 100
# khuon ma van giu 8/7 thi tap train phinh ra 85 khuon va tap do teo lai.
SO_PHAT_TRIEN_MAC_DINH = 13
SO_KIEM_TRA_MAC_DINH = 12
HAT_MAC_DINH = 42


def phan_khuon(cac_khuon, so_phat_trien=SO_PHAT_TRIEN_MAC_DINH,
               so_kiem_tra=SO_KIEM_TRA_MAC_DINH, seed=HAT_MAC_DINH):
    """-> {"train": set, "phat_trien": set, "kiem_tra_cuoi": set} — CHI tu ten.

    MOT dinh nghia duy nhat, dung chung cho `chia` VA cho bo sinh.

    VI SAO BO SINH CAN BIET TRUOC. Tu 11/09/2026 bo sinh rut noi dung ke ve
    nguoi nha tu BE RIENG cua tung tap, de tang 4 tren dev/test la noi dung CHUA
    THAY o train. Truoc do ca ba tap dung chung 25 chuoi, va tap phat trien dung
    lai dung 25/25 chuoi cua train (284/284 menh de) — nen tang 4, cho quan
    trong nhat cua du an, chua bao gio duoc thu tren noi dung chua thay.

    Muon vay bo sinh phai biet khuon nao se vao tap nao TRUOC khi chia. Tinh
    dieu do bang mot ban sao cua logic chia thi hai ban se troi nhau — dung ho
    loi "hai bang cung nghia o hai tep" da gap o NHAN_VIEN_Y_TE. Nen ca hai goi
    ham nay.
    """
    khuon = sorted(set(cac_khuon))
    khuon.sort(key=lambda t: _thu_tu(t, seed))
    kt = set(khuon[:so_kiem_tra])
    pt = set(khuon[so_kiem_tra:so_kiem_tra + so_phat_trien])
    tr = set(khuon) - kt - pt
    assert not (kt & pt) and not (kt & tr) and not (pt & tr)
    return {"train": tr, "phat_trien": pt, "kiem_tra_cuoi": kt}


def tap_cua_khuon(ten, cac_khuon, **kw):
    """-> "train" | "phat_trien" | "kiem_tra_cuoi" cho MOT khuon."""
    for tap, cac in phan_khuon(cac_khuon, **kw).items():
        if ten in cac:
            return tap
    raise KeyError(f"khuon {ten!r} khong nam trong danh sach")


def chia(ca, so_phat_trien=SO_PHAT_TRIEN_MAC_DINH,
         so_kiem_tra=SO_KIEM_TRA_MAC_DINH, seed=HAT_MAC_DINH):
    """-> (train, phat_trien, kiem_tra_cuoi) va danh sach khuon moi tap."""
    p = phan_khuon({k["benh"] for k in ca}, so_phat_trien, so_kiem_tra, seed)
    tr, pt, kt = p["train"], p["phat_trien"], p["kiem_tra_cuoi"]
    return (
        [k for k in ca if k["benh"] in tr],
        [k for k in ca if k["benh"] in pt],
        [k for k in ca if k["benh"] in kt],
        {"train": sorted(tr), "phat_trien": sorted(pt), "kiem_tra_cuoi": sorted(kt)},
    )


def kiem_khop_bo_sinh(khuon):
    """Dung lai neu mot khuon bi chia vao tap KHAC tap ma bo sinh da gia dinh.

    Bo sinh chon be noi dung nguoi nha theo tap cua ca (xem `phan_khuon`). Hai
    duong lam lech, va ca hai deu KHONG bao loi — be theo tap cu the ro ri:

      - truyen `--so-phat-trien` / `--so-kiem-tra` / `--seed` khac mac dinh
      - tep THIEU mot khuon dev/test: `chia` xep tu cac khuon CO MAT, bo sinh
        xep tu CA bang khuon, nen moi khuon xep sau cho trong do truot sang tap
        ben canh

    Muon chia lai mot bo cu thi dung ma nguon o commit ghi trong van tay cua bo
    do, khong dung ma hien tai.
    """
    from src import sinh_hoi_thoai_viet   # nhap o day: tep do nhap nguoc tep nay
    bo_sinh = sinh_hoi_thoai_viet.bang_tap_khuon()
    lech = sorted(t for tap, cac in khuon.items() for t in cac
                  if bo_sinh.get(t) != tap)
    if lech:
        raise SystemExit(
            f"{len(lech)} khuon bi chia vao tap khac tap ma bo sinh da gia dinh "
            f"(vi du {lech[:3]}): be noi dung nguoi nha se ro ri giua cac tap. "
            "Xem tach_tap_viet.kiem_khop_bo_sinh.")


def _thong_ke(ds):
    md = [m for k in ds for m in k["dap_an"]]
    kb = [m for m in md if m["chu_the"] != "bệnh nhân"]
    return len(ds), len(md), len(kb), (100 * len(kb) / max(1, len(md)))


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--nguon", default="hoi_thoai_viet_3000.jsonl")
    # Mac dinh doc tu HANG SO dung chung voi bo sinh. Truyen so khac thi tap cua
    # khuon khong con khop voi be noi dung nguoi nha ma bo sinh da chon — va
    # `kiem_khop_bo_sinh` se dung lai truoc khi ghi tep nao.
    ap.add_argument("--so-phat-trien", type=int, default=SO_PHAT_TRIEN_MAC_DINH)
    ap.add_argument("--so-kiem-tra", type=int, default=SO_KIEM_TRA_MAC_DINH)
    ap.add_argument("--seed", type=int, default=HAT_MAC_DINH)
    # BAT BUOC, khong co mac dinh: the he la thu duy nhat phan biet hai bo cung
    # ten, va de mac dinh thi moi lan sinh lai deu mang cung mot nhan.
    ap.add_argument("--the-he", required=True,
                    help="ten nguoi doc dung de goi bo nay, vi du 3 hoac 2b")
    a = ap.parse_args()

    d = duong_dan.THU_MUC_DU_LIEU
    ca = [json.loads(x) for x in open(d / a.nguon, encoding="utf-8") if x.strip()]
    tr, pt, kt, khuon = chia(ca, a.so_phat_trien, a.so_kiem_tra, a.seed)

    print(f"{'Tap':16}{'ca':>6}{'menh de':>10}{'khac BN':>9}{'ty le':>8}   khuon")
    for ten, ds in (("viet_train", tr), ("viet_phat_trien", pt),
                    ("viet_kiem_tra_cuoi", kt)):
        dp = d / f"{ten}.jsonl"
        dp.write_text("\n".join(json.dumps(k, ensure_ascii=False) for k in ds),
                      encoding="utf-8")
        # Van tay ghi CUNG LUC voi bo. Ghi bo roi dan nhan sau thi co mot khoang
        # thoi gian bo du lieu khong ai biet no la the he nao — va ba lan ho loi
        # "mot ten tep, hai bo du lieu" deu xay ra trong dung khoang do.
        van_tay_bo.ghi(dp, ds, a.the_he, hat=a.seed,
                       ghi_chu=f"chia tu {a.nguon}, tach theo khuon benh")
        n, md, kb, ty = _thong_ke(ds)
        khoa = ten.replace("viet_", "")
        print(f"{ten:16}{n:>6}{md:>10}{kb:>9}{ty:>7.1f}%   "
              + ", ".join(khuon[khoa]))

    # Khong khuon nao duoc nam o hai tap. Kiem lai ngay day chu khong tin.
    tap_khuon = [set(khuon[t]) for t in ("train", "phat_trien", "kiem_tra_cuoi")]
    for i in range(3):
        for j in range(i + 1, 3):
            chung = tap_khuon[i] & tap_khuon[j]
            assert not chung, f"khuon lot hai tap: {chung}"
    print("\nKhong khuon nao lot hai tap.")


if __name__ == "__main__":
    main()
