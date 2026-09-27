# -*- coding: utf-8 -*-
"""Van tay cua mot bo du lieu: the he nao, hat giong nao, ma nguon nao sinh ra.

VI SAO CAN — HO LOI NAY DA QUAY LAI BA LAN.

  lan 1 (09/09)  `train_baseline` chay tiep tu checkpoint cua bo 3.000 tren du
                 lieu bo 5.000. Chi bi bat vi `eval_loss` o cac buoc dau TRUNG
                 TUNG CHU SO voi lan chay truoc — mot dau hieu chi thay duoc neu
                 tinh co con nho so cu. Mat khoang 4 gio GPU.

  lan 2 (10/09)  `data/ra_C_viet_phat_trien.jsonl` mang ten `viet_phat_trien`
                 nhung la ket qua cua bo 3.000. Ghep no voi bo du lieu hien tai
                 mat 54/60 ca.

  lan 3 (10/09)  Va nang hon lan 2: bo sinh DUNG LAI khong gian id giua cac the
                 he. `hv_0019` la "sot sieu vi" trong bo 3.000 va "thieu mau do
                 giun" trong bo 5.000. Doi theo id thi bo SAI cung khop 60/60 —
                 mot phep ghep THANH CONG 100% voi toan bo nhan sai, khong ngoai
                 le, khong thieu dong, khong dau hieu gi tren bang so.

Ba lan deu cung mot hinh: **ten tep khong noi duoc no chua gi.** Va ca ba lan
deu chi bi bat bang mot dau hieu tinh co.

Chua bang cach dan nhan: moi bo du lieu sinh ra thi ghi kem mot tep van tay, va
moi cho DOC bo du lieu thi doi chieu van tay truoc khi tinh so.

    data/viet_train.jsonl
    data/viet_train.van_tay.json     <- sinh cung luc, khong bao gio sua tay

VAN TAY GHI GI, va vi sao tung muc:

    the_he      ten nguoi doc dung de goi bo nay ("3", "2b") — so lieu trong
                bao cao phai goi dung ten
    hat         hat giong; bo nay sinh lai duoc khong
    commit      ma nguon nao sinh ra. Doi bo sinh ma giu hat thi ra bo KHAC
    so_ca       de bat truong hop ghep thieu
    bam_noi_dung  bam cua NOI DUNG, khong cua id — vi id bi dung lai
    phan_bo     phan bo nhan: de thay ngay mot nhan co 0 vi du
"""
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

DUOI = ".van_tay.json"


def _commit():
    """-> ma commit, kem hau to `-ban-nhap` neu cay lam viec con thay doi.

    LO~ TRONG BAN DAU CUA CHINH TEP NAY: ghi `git rev-parse HEAD` la ghi commit
    CUOI CUNG DA COMMIT, khong phai ma nguon that su da sinh ra bo du lieu. Sinh
    bo khi dang co sua chua commit thi van tay ghi mot commit **khong chua doan
    ma do** — tuc la truong `commit` noi sai, va noi sai mot cach khong the phat
    hien tu chinh no.

    Da xay ra ngay trong lan dung dau tien: bo the he 3 duoc sinh khi
    `loi_dan_thuong.py` con dang sua, nen van tay ghi commit 2e57b3d trong khi
    bang tu dung de sinh khong nam trong commit do.
    """
    try:
        ma = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True, timeout=10
                            ).stdout.strip()
        ban_nhap = subprocess.run(["git", "status", "--porcelain", "--",
                                   "src", "tests"],
                                  capture_output=True, text=True, timeout=10
                                  ).stdout.strip()
        if not ma:
            return "khong-ro"
        return ma + ("-ban-nhap" if ban_nhap else "")
    except Exception:                                          # noqa: BLE001
        return "khong-ro"


def bam_noi_dung(cac_ban_ghi):
    """Bam theo NOI DUNG hoi thoai VA DAP AN, khong theo id.

    Bam theo id la vo nghia o day: id bi dung lai giua cac the he, nen hai bo
    khac nhau hoan toan se cho cung mot bam.

    VA PHAI GOM CA DAP AN — lo~ trong ban dau cua chinh ham nay.
    Ban dau no chi bam truong `input`. Ngay 11/09/2026 toi them truong
    `thoi_gian_su_kien` vao dap an roi sinh lai bo: hoi thoai khong doi mot chu,
    nen the he 3 va the he 4 cho **cung mot bam** — `9486115ed86f669a` cho ca
    hai. Hai bo co cung hoi thoai nhung KHAC NHAN se lan vao nhau ma van tay
    khong thay, tuc la dung loai hong ma ham nay duoc viet ra de chan.
    """
    h = hashlib.sha256()
    for b in cac_ban_ghi:
        h.update(" ".join(str(b.get("input") or "").split()).encode("utf-8"))
        h.update(b"\x01")
        # Dap an: bam cac truong MANG NHAN, theo thu tu co dinh. Khong bam ca
        # dict vi thu tu khoa co the doi ma noi dung khong doi.
        for m in (b.get("dap_an") or []):
            for khoa in ("chu_the", "noi_dung", "muc", "moc_thoi_gian",
                         "phu_dinh", "tinh_huong", "thoi_gian_su_kien",
                         "quan_he", "quan_he_voi", "trang_thai", "luot"):
                h.update(f"{khoa}={m.get(khoa)!r}".encode("utf-8"))
            h.update(b"\x02")
        h.update(b"\x00")
    return h.hexdigest()[:16]


def _phan_bo(cac_ban_ghi):
    """Phan bo nhan. Mot nhan co 0 vi du phai NHIN THAY NGAY o day."""
    ra = {}
    for truong in ("quan_he", "trang_thai", "tinh_huong"):
        c = Counter(str(m.get(truong)) for b in cac_ban_ghi
                    for m in (b.get("dap_an") or []))
        if c:
            ra[truong] = dict(sorted(c.items(), key=lambda x: -x[1]))
    for truong in ("benh", "boi_canh"):
        c = Counter(str(b.get(truong)) for b in cac_ban_ghi)
        ra[f"so_{truong}"] = len(c)
    return ra


def dung(cac_ban_ghi, the_he, hat=None, ghi_chu=""):
    """-> dict van tay."""
    return {"the_he": str(the_he), "hat": hat, "commit": _commit(),
            "so_ca": len(cac_ban_ghi),
            "so_menh_de": sum(len(b.get("dap_an") or []) for b in cac_ban_ghi),
            "bam_noi_dung": bam_noi_dung(cac_ban_ghi),
            "phan_bo": _phan_bo(cac_ban_ghi), "ghi_chu": ghi_chu}


def duong_dan_van_tay(duong_dan_bo):
    p = Path(duong_dan_bo)
    return p.with_name(p.name.rsplit(".", 1)[0] + DUOI)


def ghi(duong_dan_bo, cac_ban_ghi, the_he, hat=None, ghi_chu=""):
    vt = dung(cac_ban_ghi, the_he, hat, ghi_chu)
    duong_dan_van_tay(duong_dan_bo).write_text(
        json.dumps(vt, ensure_ascii=False, indent=2), encoding="utf-8")
    return vt


def doc(duong_dan_bo):
    """-> dict van tay, hoac None neu bo nay chua co van tay."""
    p = duong_dan_van_tay(duong_dan_bo)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def mo_ta(duong_dan_bo):
    """-> chuoi mot dong de in o dau moi bang so.

    Mot bang so khong noi no do tren bo nao thi khong doc duoc sau ba thang.
    """
    vt = doc(duong_dan_bo)
    if not vt:
        return (f"{Path(duong_dan_bo).name}: CHUA CO VAN TAY — khong biet day la "
                f"the he nao. Sinh lai bo nay, hoac ghi van tay bang "
                f"`src.van_tay_bo.ghi`.")
    return (f"{Path(duong_dan_bo).name}: thế hệ {vt['the_he']}, "
            f"{vt['so_ca']} ca, hạt {vt['hat']}, commit {vt['commit']}, "
            f"băm {vt['bam_noi_dung']}")


def khop(duong_dan_bo, cac_ban_ghi):
    """-> (khop, thong_diep). Doi chieu bo dang nam tren dia voi van tay cua no.

    Dung khi mot tep bi sua tay, hoac bi ghi de boi mot the he khac ma van tay
    khong duoc cap nhat theo.
    """
    vt = doc(duong_dan_bo)
    if not vt:
        return None, mo_ta(duong_dan_bo)
    bam = bam_noi_dung(cac_ban_ghi)
    if bam == vt["bam_noi_dung"] and len(cac_ban_ghi) == vt["so_ca"]:
        return True, f"khớp vân tay thế hệ {vt['the_he']}"
    return False, (
        f"{Path(duong_dan_bo).name} KHONG khop van tay cua chinh no.\n"
        f"  van tay ghi : the he {vt['the_he']}, {vt['so_ca']} ca, "
        f"bam {vt['bam_noi_dung']}\n"
        f"  tep hien co : {len(cac_ban_ghi)} ca, bam {bam}\n"
        f"Tep da bi ghi de hoac sua tay sau khi van tay duoc lap. Sinh lai bo, "
        f"dung tiep se cho mot bang so khong the truy nguoc.")


def nhan_thieu_vi_du(duong_dan_bo, khai_bao):
    """-> cac nhan duoc khai trong luoc do ma van tay cho thay co 0 vi du.

    `khai_bao`: {ten_truong: tuple cac gia tri hop le}.

    Day la cho de bat lo~ "khai qua": luoc do khai bon quan he, du lieu co hai.
    Truoc 11/09/2026 chuyen do chi bi phat hien bang cach tinh co di dem.
    """
    vt = doc(duong_dan_bo)
    if not vt:
        return {}
    ra = {}
    for truong, cac_gia_tri in khai_bao.items():
        co = vt.get("phan_bo", {}).get(truong, {})
        thieu = [v for v in cac_gia_tri if not co.get(v)]
        if thieu:
            ra[truong] = thieu
    return ra
