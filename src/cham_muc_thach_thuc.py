# -*- coding: utf-8 -*-
"""Cham bon bo thach thuc TREN VAN BAN, ap NHU NHAU cho moi nhanh — ke ca nhanh A.

VI SAO CO TEP NAY (15/09/2026).

Moi ham cham thach thuc trong `cham_he_thong` doc `r["phat_bieu"]` — bang menh de
cua duong ong. Nhanh A sinh thang van xuoi, khong co bang do, nen A KHONG CHAM
DUOC tren chinh cac bo duoc dung ra de so A voi duong ong. Ma do lai la cau hoi
nghien cuu. Con thuoc do dau-cuoi (ROUGE, F1 muc) thi cham duoc A — va cho A
0,9935 tren tap phat trien, vi A hoc thuoc NGU PHAP viet cua bo sinh: 36/60 ban
nhap trung khit tung ky tu voi ban tham chieu. Mot thuoc do ma A dat 0,99 thi
khong con cho nao de phan biet ai hieu chu the voi ai chep khuon.

DIEU LAM PHEP CHAM NAY CONG BANG: ban tham chieu cua bo sinh ma hoa DUNG dieu
tung bo do.

  doi_chu_the  hai ban cua cap khac nhau DUNG o muc DI UNG va TIEN SU GIA DINH
  dinh_chinh   trang thai cuoi hien trong muc BENH SU: ban dung, "chua ro X hay
               Y" khi mau thuan, ca hai moc khi dien bien
  phuong_ngu   hai ban tham chieu cua cap GIONG HET nhau
  nhieu_asr    nhu tren

Nen doi chieu tung MUC VAN BAN cua ban nhap voi ban tham chieu, bang CUNG mot ham
cho moi nhanh, la phep so sanh can. Khong can bang menh de.

CHI SO CAC Y LIEN QUAN, KHONG SO CA MUC. Do tren ca `dch_001`: nhanh A xu ly mau
thuan DUNG ("sot (chua ro ba hom hay may hom nay)") nhung viet "met moi" thay vi
"met" o mot y khac trong cung muc. So ca muc thi ca do bi cham SAI OAN — va phep
do luc do do "viet giong khuon" chu khong do "giu dung trang thai". Nen:

  doi_chu_the  chi cac y co chu "di ung"
  dinh_chinh   chi cac y chua noi dung cua menh de dap an CO quan he

    python -m src.cham_muc_thach_thuc --tap thach_thuc_doi_chu_the_phat_trien \\
        --nhanh A B C C_khoa C_khoa_hoi
"""
import argparse
import io
import json
import re
import sys
import unicodedata
from collections import defaultdict

from src import chuan_dinh_dang, duong_dan, sinh_benh_an
from src import sinh_hoi_thoai_viet as sh

MUC_THAN = tuple(sh.MUC)
MUC_PHU = tuple(sinh_benh_an.MUC_PHU_TAT_CA)

# Ban nao cua cap la ban BI LAM KHO. Hai bo sinh dat nhan NGUOC nhau, va nham cho
# nay thi con so "phuong ngu lam giam do chinh xac" doi dau.
#   `thach_thuc.cap_phuong_ngu`: ban A CO tu phuong ngu, ban B tat tang vung
#   `thach_thuc.cap_nhieu_asr` : ban A SACH, ban B da lam nhieu
BAN_BI_LAM_KHO = {"phuong_ngu": "A", "nhieu_asr": "B"}


def _chuan(s):
    s = unicodedata.normalize("NFC", s or "").lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s.strip(" .;:,")


def _bo_cach_viet(y):
    """Bo nhung khac biet THUAN CACH VIET giua bo sinh va khau dung ban nhap.

    Do 15/09/2026 tren dau ra that, ban dau cua tep nay chua co ham nay va cham C
    0/40 cap doi chu the trong khi bo cham menh de cho 28/40:
      - tham chieu viet "benh nhan dau thuong vi (...)", duong ong viet "dau thuong
        vi (...)" — tien to chu ngu khong mang thong tin
      - tham chieu viet "bo di ung nong ong", duong ong viet "bo: di ung nong ong"
    Ca hai la dinh dang. Ten NGUOI thi giu nguyen: "ba ngoai: di ung…" doi thanh
    "ba ngoai di ung…" van khac "bo di ung…", va phai khac.
    """
    y = re.sub(r"^bệnh nhân\s+", "", y)
    y = re.sub(r"^([^:]{1,20}):\s*", r"\1 ", y)
    return y


def _bo_y_bi_bao_ham(tap_y):
    """Bo y tron "X" khi da co "X (moc)". Mot lan nhac lai khong moc la LAP (dem o
    loai `trung_lap` cua bo cham menh de), khong phai sai trang thai."""
    co_moc = {re.sub(r"\s*\(.*\)$", "", y) for y in tap_y if y.endswith(")")}
    return {y for y in tap_y if y.endswith(")") or y not in co_moc}


def tach_muc(van_ban):
    """Van ban -> {ten muc: [dong noi dung]}. Bo hai muc phu vi ban tham chieu
    khong co chung — de chung lai la phat duong ong vi mot muc no tu dat ra."""
    van = chuan_dinh_dang.chuan_hoa(van_ban)
    ra, dang = defaultdict(list), None
    for dong in van.split("\n"):
        t = dong.strip()
        if not t:
            continue
        if t in MUC_THAN or t in MUC_PHU:
            dang = t
            continue
        if dang and dang not in MUC_PHU:
            ra[dang].append(t)
    return dict(ra)


def dong_muc_phu(van_ban):
    """Cac dong duoi muc CAN XAC NHAN — noi duong ong dua thong tin chua giai quyet."""
    van = chuan_dinh_dang.chuan_hoa(van_ban)
    ra, dang = [], False
    for dong in van.split("\n"):
        s = dong.strip()
        if not s:
            continue
        if s in MUC_THAN or s in MUC_PHU:
            dang = s == sinh_benh_an.MUC_PHU
            continue
        if dang:
            ra.append(_chuan(s))
    return ra


def cac_y(dong_noi_dung):
    """Cac dong cua mot muc -> tap cac Y da chuan hoa (tach o ';' va het cau).

    Tap chu khong phai danh sach: thu tu cac y trong mot muc khong phai dieu bo
    thach thuc nao do.
    """
    ra = set()
    for dong in dong_noi_dung:
        for manh in re.split(r";|\.(?=\s|$)", dong):
            c = _bo_cach_viet(_chuan(manh))
            if c:
                ra.add(c)
    return ra


def _y_muc(van_ban, muc, loc=None):
    y = cac_y(tach_muc(van_ban).get(muc, []))
    return {x for x in y if loc(x)} if loc else y


# ------------------------------------------------------------ tung bo thach thuc
def dung_doi_chu_the(ca, du_doan):
    """Moi y "di ung" o muc DI UNG va o muc TIEN SU GIA DINH phai trung tham chieu."""
    co_di_ung = lambda y: "dị ứng" in y
    return all(
        _y_muc(du_doan, m, co_di_ung) == _y_muc(ca["output"], m, co_di_ung)
        for m in ("DỊ ỨNG", "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI"))


def _noi_dung_lien_quan(ca):
    da = ca["dap_an"]
    chi_so = {i for i, d in enumerate(da) if d.get("quan_he")} | \
             {d.get("quan_he_voi") for d in da if d.get("quan_he")}
    return {_chuan(da[i]["noi_dung"]) for i in chi_so
            if isinstance(i, int) and 0 <= i < len(da)}


def dung_dinh_chinh(ca, du_doan):
    """Cac y o muc BENH SU chua noi dung cua menh de CO quan he phai trung tham chieu.

    Loc bang noi dung dap an thay vi so ca muc — xem giai thich o dau tep.
    """
    nd = _noi_dung_lien_quan(ca)
    if not nd:
        return None
    m = "BỆNH SỬ HIỆN TẠI"

    # MAU THUAN va HAI NGUON: khong ai sua ai, nen khong co ban dung. Ban tham chieu
    # viet "(chua ro X hay Y)" trong than; duong ong theo chinh sach cua no dua ca hai
    # xuong CAN XAC NHAN. Ca hai deu dung ve lam sang. Cham theo DIEU CO HAI thay vi
    # theo cach viet cua bo sinh: SAI khi than ghi hai moc nhu hai su that, hoac khi
    # mau thuan bien mat khong de lai dau vet.
    if ca.get("bay_chinh") in ("mau_thuan", "nguon_khac_nhau"):
        moc = {_chuan(d["moc_thoi_gian"]) for d in ca["dap_an"]
               if d.get("trang_thai") == "chưa giải quyết" and d.get("moc_thoi_gian")}
        if len(moc) >= 2:
            than = cac_y(tach_muc(du_doan).get(m, []))
            hai_su_that = sum(any(f"({x})" in y for y in than) for x in moc) >= 2
            neu_trong_than = any("chưa rõ" in y and all(x in y for x in moc) for y in than)
            phu = dong_muc_phu(du_doan)
            neu_o_phu = all(any(x in y for y in phu) for x in moc)
            return (not hai_su_that) and (neu_trong_than or neu_o_phu)

    lien_quan = lambda y: any(n and n in y for n in nd)
    return (_bo_y_bi_bao_ham(_y_muc(du_doan, m, lien_quan))
            == _bo_y_bi_bao_ham(_y_muc(ca["output"], m, lien_quan)))


def than_ban_nhap(du_doan):
    """Moi y o moi muc than, gan ten muc — de so hai ban cua mot cap voi nhau."""
    return frozenset((m, y) for m, dong in tach_muc(du_doan).items()
                     if m in MUC_THAN for y in cac_y(dong))


# ------------------------------------------------------------------ tong hop tap
def cham_tap(cac_ca, ket_qua):
    loai = {ca.get("thach_thuc") for ca in cac_ca} - {None}
    if len(loai) != 1:
        raise ValueError(f"tap phai la MOT bo thach thuc, gap: {loai}")
    loai = loai.pop()

    if loai == "dinh_chinh":
        theo_bay = defaultdict(lambda: [0, 0])
        for ca in cac_ca:
            r = ket_qua.get(ca["id"])
            d = dung_dinh_chinh(ca, r["du_doan"]) if r else False
            if d is None:
                continue
            t = theo_bay[ca.get("bay_chinh")]
            t[0] += bool(d)
            t[1] += 1
        return {"thach_thuc": loai,
                "dung": sum(v[0] for v in theo_bay.values()),
                "so_ca": sum(v[1] for v in theo_bay.values()),
                "theo_bay": {b: f"{d}/{n}" for b, (d, n) in sorted(theo_bay.items())}}

    cap = defaultdict(dict)
    for ca in cac_ca:
        r = ket_qua.get(ca["id"])
        cap[ca["cap"]][ca["bien_the"]] = (ca, r)
    du = [v for v in cap.values() if len(v) == 2]

    if loai == "doi_chu_the":
        dung = [{b: bool(v[b][1]) and dung_doi_chu_the(v[b][0], v[b][1]["du_doan"])
                 for b in ("A", "B")} for v in du]
        return {"thach_thuc": loai, "so_cap": len(du),
                "dung_ca_cap": sum(d["A"] and d["B"] for d in dung),
                "dung_ban_A": sum(d["A"] for d in dung),
                "dung_ban_B": sum(d["B"] for d in dung)}

    if loai in BAN_BI_LAM_KHO:
        kho = BAN_BI_LAM_KHO[loai]
        sach = "B" if kho == "A" else "A"
        # CHI do BAT BIEN: ban nhap cua ban sach va ban bi lam kho co giong nhau
        # khong. Khong so voi ban tham chieu — so ca than ho so voi cach viet cua bo
        # sinh cho duong ong 0/40 va A 32/40 chi vi A chep khuon (do 15/09/2026).
        giong = 0
        for v in du:
            (_ca_s, r_s), (_ca_k, r_k) = v[sach], v[kho]
            if r_s and r_k:
                giong += than_ban_nhap(r_s["du_doan"]) == than_ban_nhap(r_k["du_doan"])
        return {"thach_thuc": loai, "so_cap": len(du), "hai_ban_giong_het": giong}

    raise ValueError(f"chua co phep cham van ban cho bo {loai!r}")


def _nap(p):
    with open(p, encoding="utf-8") as f:
        return [json.loads(d) for d in f if d.strip()]


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", required=True)
    ap.add_argument("--nhanh", nargs="+", required=True)
    a = ap.parse_args()
    from src import du_lieu as _dl
    _dl.chan_tap_ngoai(a.tap)
    _dl.chan_tap_khoa(a.tap)

    d = duong_dan.THU_MUC_DU_LIEU
    cac_ca = _nap(d / f"{a.tap}.jsonl")
    ra = {}
    for nhanh in a.nhanh:
        tep = d / f"ra_{nhanh}_{a.tap}.jsonl"
        if not tep.exists():
            print(f"(chua co {tep.name})")
            continue
        kq = {k["id"]: k for k in _nap(tep)}
        ra[nhanh] = cham_tap(cac_ca, kq)
        print(f"{nhanh:12} {json.dumps(ra[nhanh], ensure_ascii=False)}")

    dp = duong_dan.THU_MUC_KET_QUA / f"cham-muc-{a.tap}.json"
    dp.write_text(json.dumps(ra, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Ghi {dp}")


if __name__ == "__main__":
    main()
