# -*- coding: utf-8 -*-
"""Khoang tin cay va so sanh theo cap cho bang doi chieu cac nhanh.

VI SAO CAN. Moi con so trong bang so sanh hien tai la MOT diem, chay mot lan.
Khong co cho nao trong `src/` tinh sai so. Voi n = 60 ca, sai so chuan cua mot
ty le quanh 0,5 la khoang 6,5 diem phan tram, nen khoang tin cay 95% rong co
±13 diem — moi cau "nhanh X hon nhanh Y vai diem" deu khong doc duoc.

BA CHO DE LAM SAI, tep nay chan ca ba.

1. DON VI DOC LAP LA KHUON BENH, KHONG PHAI CA.

   `tach_tap_viet` da ghi ro: hai ca cung khuon dung chung dan y, chung kho
   trieu chung, chung mach hoi thoai — "chung gan nhu la mot bai". Lay lai mau
   theo CA thi 60 ca duoc dem la 60 don vi doc lap, trong khi thuc te chi co
   vai cum. Khoang tin cay ra hep gia.

   Nen bao CA HAI:

       theo ca     lay lai mau tung ca        -> khoang lac quan
       theo khuon  lay lai mau tung khuon     -> khoang that (bootstrap cum)

2. SO HAI KHOANG TIN CAY CHONG NHAU ROI KET LUAN "khong khac biet" LA SAI.

   Cac nhanh chay tren CUNG bo ca, nen phai lay khoang tin cay cua HIEU theo
   cap. Hieu theo cap hep hon nhieu so voi hai khoang roi, vi no triet tieu
   phan "ca nay de, ca kia kho".

3. TEN TEP KET QUA KHONG NOI DUOC NO CHAY TREN BO NAO.

   Loi that, tim ra dung luc viet tep nay: `data/ra_C_viet_phat_trien.jsonl`
   co ten noi la `viet_phat_trien`, nhung id trong no khop
   `viet3k_phat_trien.jsonl` dung 60/60, va khop `viet_phat_trien.jsonl`
   hien tai chi 6/60. Noi cach khac day la ket qua cua BO 3.000, mang ten cua
   bo 5.000.

   Ghep no voi bo du lieu hien tai thi mat 54/60 ca ma khong co ngoai le nao.
   Day la ho loi B12 lan thu bay: MOT TEN TEP, HAI BO DU LIEU.

   Nen `doi_chieu_tap` do khop id truoc khi tinh bat ky con so nao, va khi
   khong khop 100% thi DUNG HAN, kem ten tep that su khop.

GIOI HAN, phai ghi vao bao cao. Tap phat_trien co 8 khuon. Bootstrap cum tren
8 cum la xap xi tho: no noi duoc "khoang nay rong", khong noi duoc "p = 0,03".
Dung no de bac bo nhung chenh lech nho, khong dung no de khang dinh chenh lech
nho.

    python -m src.sai_so --tap viet_phat_trien --nhanh B C D
"""
import argparse
import io
import json
import random
import sys
from pathlib import Path

from src import cham_diem, thuoc_do_quy_gan

# Hai HO thuoc do, va chung khong thay nhau duoc.
#
#   cham_diem   ROUGE + SectionF1. Du an nay da chung minh no NGUOC DAU voi
#               loi doi chu the, nen no la chi so tham chieu.
#   quy_gan     F1 tren cap (chu the, noi dung). Day moi la thuoc do chinh.
#
# Mot bang chi co `final` thi khong tra loi duoc cau hoi cua du an.
HO_THUOC_DO = {
    "cham_diem": ("final", "rouge_avg", "section_f1",
                  "rouge1", "rouge2", "rougel"),
    "quy_gan": ("f1_quy_gan", "do_chinh_xac", "do_bao_phu"),
}


def _ho_cua(khoa):
    for ho, cac in HO_THUOC_DO.items():
        if khoa in cac:
            return ho
    raise SystemExit(f"khong biet thuoc do {khoa!r}; "
                     f"co: {sorted(k for v in HO_THUOC_DO.values() for k in v)}")

THU_MUC_DATA = Path("data")

# Bao nhieu khuon thi mot phep so sanh con doc duoc. Duoi muc nay thi con so
# khong sai, nhung no khong noi gi ve bo khuon day du.
KHUON_TOI_THIEU = 6

SO_LAN_MAC_DINH = 10000
HAT_MAC_DINH = 42


# --------------------------------------------------------------- nap du lieu

def _doc(duong_dan):
    return [json.loads(d) for d in
            open(duong_dan, encoding="utf-8") if d.strip()]


def diem_tung_ca(duong_dan, khoa="final", dung_muc_phu=True):
    """-> ({id: diem}, {id: ban_ghi}) cho MOT tep ket qua nhanh.

    Giu diem tung ca thay vi tra ve trung binh: `do_dac.do_mot_nhanh` trung
    binh ngay roi bo danh sach, nen khong con gi de lay lai mau.

    Tra ve ca ban ghi goc vi hang rao `doi_chieu_tap` phai so NOI DUNG, khong
    so id.
    """
    diem, ban_ghi = {}, {}
    for k in _doc(duong_dan):
        tham_chieu = k.get("tham_chieu") or ""
        if not tham_chieu:
            continue
        truong = "du_doan" if dung_muc_phu else "du_doan_khong_muc_phu"
        du_doan = k.get(truong, k.get("du_doan", ""))
        if _ho_cua(khoa) == "quy_gan":
            d = thuoc_do_quy_gan.diem(du_doan, tham_chieu)
        else:
            d = cham_diem.diem_cuoi(du_doan, tham_chieu)
        diem[k["id"]] = d[khoa]
        ban_ghi[k["id"]] = k
    return diem, ban_ghi


def _khoa_noi_dung(ban_ghi):
    """Dau vet NOI DUNG cua mot ca: chinh van ban hoi thoai, da chuan khoang."""
    return " ".join(str(ban_ghi.get("input") or "").split())


def tim_tap_khop(theo_id, thu_muc=None):
    """-> [(ten_tep, khop_noi_dung, khop_id, tong)] sap theo khop noi dung.

    `theo_id`: {id: ban_ghi_ket_qua} — can ca ban ghi, khong chi id, vi phai
    so NOI DUNG.

    DOI ID KHONG DU DE NHAN DANG BO DU LIEU. Bo sinh dung lai khong gian id:
    `hv_0019` la "sot sieu vi" trong bo 3.000 va "thieu mau do giun" trong bo
    5.000. Nen:

        doi theo id      bo 3.000 khop 60/60  VA  bo 5.000 khop 60/60
        doi theo noi dung bo 3.000 khop 60/60  VA  bo 5.000 khop  0/60

    Ghep theo id voi bo sai cho ra mot phep ghep THANH CONG 100% voi toan bo
    nhan sai. Khong ngoai le, khong thieu dong, khong dau hieu gi tren bang
    so. Day la ho loi B12 o dang nguy hiem nhat.
    """
    thu_muc = Path(thu_muc or THU_MUC_DATA)
    ra = []
    for tep in sorted(thu_muc.glob("*.jsonl")):
        if tep.name.startswith(("ra_", "trich_")):
            continue
        try:
            goc = {b.get("id"): b for b in _doc(tep)}
        except Exception:                                      # noqa: BLE001
            continue
        khop_id = sum(1 for i in theo_id if i in goc)
        khop_nd = sum(1 for i, b in theo_id.items()
                      if i in goc and _khoa_noi_dung(goc[i]) == _khoa_noi_dung(b))
        if khop_id:
            ra.append((tep.name, khop_nd, khop_id, len(theo_id)))
    ra.sort(key=lambda x: (-x[1], -x[2]))
    return ra


def doi_chieu_tap(theo_id, duong_dan_tap):
    """-> {id: khuon}. DUNG HAN neu bo du lieu khong khop NOI DUNG 100%.

    Ly do dung han chu khong canh bao: ghep sai o day khong bao loi o buoc
    sau. Ghep thieu thi lam n tut am tham; ghep lan the he thi giu nguyen n
    va doi het nhan khuon. Ca hai deu ra mot bang so doc duoc binh thuong.
    """
    goc = {b["id"]: b for b in _doc(duong_dan_tap)}
    thieu = [i for i in theo_id if i not in goc]
    lech = [i for i, b in theo_id.items()
            if i in goc and _khoa_noi_dung(goc[i]) != _khoa_noi_dung(b)]
    if thieu or lech:
        dong = [f"  {t:<40} noi dung {nd:>3}/{tong}   id {ki:>3}/{tong}"
                for t, nd, ki, tong in tim_tap_khop(theo_id)[:5]]
        raise SystemExit(
            f"Ket qua va bo du lieu KHONG cung mot the he.\n"
            f"  bo du lieu dua vao : {duong_dan_tap}\n"
            f"  thieu id           : {len(thieu)}/{len(theo_id)}"
            + (f" (vi du {', '.join(thieu[:4])})" if thieu else "") + "\n"
            f"  co id nhung LECH noi dung: {len(lech)}/{len(theo_id)}"
            + (f" (vi du {', '.join(lech[:4])})" if lech else "") + "\n"
            f"Do khop tung tep trong data/:\n" + "\n".join(dong) +
            "\n\nDoi theo id KHONG du: bo sinh dung lai khong gian id giua cac\n"
            "the he, nen mot bo sai van khop 60/60 theo id. Chon tep khop\n"
            "NOI DUNG, bang --tap-goc.")
    return {i: goc[i].get("benh") for i in theo_id}


# ----------------------------------------------------------------- lay lai mau

def _trung_binh(gia_tri):
    return sum(gia_tri) / len(gia_tri) if gia_tri else float("nan")


def _mau_theo_ca(gia_tri, rng):
    n = len(gia_tri)
    return _trung_binh([gia_tri[rng.randrange(n)] for _ in range(n)])


def _mau_theo_khuon(theo_khuon, rng):
    """Bootstrap cum: lay lai mau TEN KHUON, moi khuon lay ca cum ca cua no."""
    ten = list(theo_khuon)
    gop = []
    for _ in range(len(ten)):
        gop.extend(theo_khuon[ten[rng.randrange(len(ten))]])
    return _trung_binh(gop)


def _phan_vi(da_sap, p):
    if not da_sap:
        return float("nan")
    vi_tri = p * (len(da_sap) - 1)
    duoi = int(vi_tri)
    tren = min(duoi + 1, len(da_sap) - 1)
    le = vi_tri - duoi
    return da_sap[duoi] * (1 - le) + da_sap[tren] * le


def khoang(gia_tri_theo_id, khuon=None, so_lan=SO_LAN_MAC_DINH,
           hat=HAT_MAC_DINH, muc=0.95):
    """-> {trung_binh, thap, cao, so_ca, so_khuon, don_vi}.

    `khuon` co thi lay lai mau theo khuon (don vi doc lap dung). Khong co thi
    lay lai mau theo ca, va truong `don_vi` ghi ro la "ca" de doc bang biet
    day la khoang LAC QUAN.
    """
    rng = random.Random(hat)
    gia_tri = list(gia_tri_theo_id.values())
    if khuon:
        theo_khuon = {}
        for i, v in gia_tri_theo_id.items():
            theo_khuon.setdefault(khuon[i], []).append(v)
        mau = sorted(_mau_theo_khuon(theo_khuon, rng) for _ in range(so_lan))
        don_vi, so_khuon = "khuôn", len(theo_khuon)
    else:
        mau = sorted(_mau_theo_ca(gia_tri, rng) for _ in range(so_lan))
        don_vi, so_khuon = "ca", None
    le = (1 - muc) / 2
    return {"trung_binh": _trung_binh(gia_tri),
            "thap": _phan_vi(mau, le), "cao": _phan_vi(mau, 1 - le),
            "so_ca": len(gia_tri), "so_khuon": so_khuon, "don_vi": don_vi}


def so_sanh(a_theo_id, b_theo_id, khuon=None, so_lan=SO_LAN_MAC_DINH,
            hat=HAT_MAC_DINH, muc=0.95):
    """So sanh THEO CAP tren cac ca CO O CA HAI nhanh.

    -> {hieu, thap, cao, so_ca_chung, ty_le_dau_nguoc}

    `ty_le_dau_nguoc` la ty le lan lay lai mau cho hieu trai dau voi hieu do
    duoc. Nhan doi no duoc mot gia tri gan nghia voi p hai phia. Goi dung ten
    la ty le, khong goi la p: voi 8 khuon thi con so do khong du chinh xac de
    mang ten p.
    """
    chung = sorted(set(a_theo_id) & set(b_theo_id))
    if not chung:
        raise SystemExit("hai nhanh khong co ca nao chung — khong so sanh duoc")
    hieu = {i: a_theo_id[i] - b_theo_id[i] for i in chung}
    k = khoang(hieu, {i: khuon[i] for i in chung} if khuon else None,
               so_lan, hat, muc)
    rng = random.Random(hat + 1)
    if khuon:
        theo_khuon = {}
        for i, v in hieu.items():
            theo_khuon.setdefault(khuon[i], []).append(v)
        mau = [_mau_theo_khuon(theo_khuon, rng) for _ in range(so_lan)]
    else:
        gt = list(hieu.values())
        mau = [_mau_theo_ca(gt, rng) for _ in range(so_lan)]
    quan_sat = k["trung_binh"]
    nguoc = sum(1 for m in mau
                if ((m <= 0) if quan_sat > 0 else (m >= 0)))
    return {"hieu": quan_sat, "thap": k["thap"], "cao": k["cao"],
            "so_ca_chung": len(chung), "so_khuon": k["so_khuon"],
            "don_vi": k["don_vi"], "ty_le_dau_nguoc": nguoc / len(mau)}


# ------------------------------------------------------------------ bao cao

# ------------------------------------------------- do CONG SUAT cua phep do
#
# Bon tang quy gan, xep theo do kho THAT:
#
#   1 luot bac si                 chu the luon la benh nhan        khong kho
#   2 luot benh nhan              chu the la chinh nguoi noi       khong kho
#   3 nguoi nha ke HO benh nhan   "chu the = nguoi noi" SAI        kho
#   4 nguoi nha ke VE CHINH MINH  ca hai duong tat deu SAI         kho nhat
#
# Tang 4 la cho du an nay ton tai. Do duoc tren ba the he du lieu:
#
#   bo 3.000 (dev)   67/3.507 menh de = 1,91%
#   bo 5.000 (dev)  137/5.896 menh de = 2,32%
#
# Va trong 60 ca da dung de so sanh cac nhanh: 7 menh de tang 4 tren 514.
#
# HE QUA, va day la cho phai ghi vao bao cao: anh huong TOI DA ma co che quy
# gan co the tao ra tren mot thuoc do GOP la 1,4 diem. Be rong khoang tin cay
# do duoc la ±0,9 den ±1,4 diem. Phep do khong du cong suat de thay dieu no
# duoc dung de thay.
#
# Khong phai "co che khong hieu qua". La "phep do khong tra loi duoc cau hoi".
# Hai ket luan do khac nhau, va lan thu hai bat buoc phai sua PHEP DO, khong
# phai sua co che.

VAI_BAC_SI = ("bác sĩ",)
VAI_BENH_NHAN = ("bệnh nhân",)
TANG = ("bac_si", "benh_nhan", "ke_ho", "ke_ve_minh")


def nguoi_noi_tung_luot(ban_ghi):
    """-> {so thu tu luot (dem tu 1): vai nguoi noi}."""
    import re
    ra = {}
    dong = [d for d in str(ban_ghi.get("input") or "").split("\n") if d.strip()]
    for i, d in enumerate(dong, 1):
        m = re.match(r"^([^:]{1,30}):", d)
        ra[i] = m.group(1).strip() if m else "?"
    return ra


def tang_cua(menh_de, vai_theo_luot):
    """Tang cua MOT menh de dap an -> "bac_si" | "benh_nhan" | "ke_ho" |
    "ke_ve_minh", hoac None neu menh de khong co luot.

    MOT DINH NGHIA, dung chung cho `tang_menh_de` va
    `do_tang_quy_gan.menh_de_dap_an`. Truoc 11/09/2026 moi tep giu mot ban sao
    cua cung logic nay — ho loi "hai bang cung nghia o hai tep".

    Hai quy uoc, ca hai sua ngay 11/09/2026:

      NGUOI NOI = nguoi noi LUOT CUOI trong bang chung, giong
      `phat_bieu.tu_json`. Cau tra loi tat mang ca luot CAU HOI dung truoc;
      lay luot dau thi moi cau "Da, khong a" cua nguoi nha thanh loi bac si.

      MOI vai nhan vien y te — ca DIEU DUONG — la tang `bac_si`. Truoc do chi
      "bac si": dieu duong doc sinh hieu la noi VE benh nhan, nhung roi vao
      tang `ke_ho` nhu mot nguoi nha ke thay.
    """
    from src.phat_bieu import la_vai_nhan_vien
    luot = menh_de.get("luot") or []
    if not luot:
        return None
    nn = str(vai_theo_luot.get(max(luot), "?")).lower()
    if la_vai_nhan_vien(nn):
        return "bac_si"
    if nn in VAI_BENH_NHAN:
        return "benh_nhan"
    if menh_de.get("chu_the") == "bệnh nhân":
        return "ke_ho"
    return "ke_ve_minh"


def tang_menh_de(ban_ghi_goc):
    """-> Counter tren bon tang, cho MOT ca (ban ghi cua bo du lieu)."""
    from collections import Counter
    vai = nguoi_noi_tung_luot(ban_ghi_goc)
    ra = Counter()
    for m in ban_ghi_goc.get("dap_an") or []:
        tang = tang_cua(m, vai)
        if tang:
            ra[tang] += 1
    return ra


def do_cong_suat(goc_theo_id):
    """-> {tong, theo_tang, ty_le_tang4, anh_huong_toi_da}.

    `anh_huong_toi_da` la chenh lech LON NHAT co the co tren mot thuoc do gop
    neu co che quy gan sua dung het tang 4 va doi chung sai het. No la tran
    tren, khong phai du doan.
    """
    from collections import Counter
    gop = Counter()
    for b in goc_theo_id.values():
        gop += tang_menh_de(b)
    tong = sum(gop.values()) or 1
    return {"tong": tong, "theo_tang": dict(gop),
            "ty_le_tang4": gop["ke_ve_minh"] / tong,
            "anh_huong_toi_da": gop["ke_ve_minh"] / tong}


def canh_cong_suat(cong_suat, rong_ktc):
    """-> chuoi canh bao, hoac None neu phep do du cong suat.

    So TRAN ANH HUONG voi BE RONG KHOANG TIN CAY. Tran nho hon be rong thi
    phep so sanh khong the thay duoc hieu ung, ke ca khi hieu ung co that.
    """
    tran = cong_suat["anh_huong_toi_da"]
    if rong_ktc != rong_ktc or tran >= rong_ktc:
        return None
    n4 = cong_suat["theo_tang"].get("ke_ve_minh", 0)
    return (f"**Phép đo không đủ công suất.** Mệnh đề tầng 4 — người nhà kể về "
            f"chính mình, nơi cả hai đường tắt đều sai — chỉ có **{n4}/"
            f"{cong_suat['tong']} = {_pt(tran)}** trong mẫu này. Ảnh hưởng tối "
            f"đa mà cơ chế quy gán có thể tạo ra trên thước đo gộp là "
            f"{_pt(tran)}, trong khi khoảng tin cậy rộng {_pt(rong_ktc)}. "
            f"Mọi kết luận "
            f"*“cơ chế không có tác dụng”* đọc từ bảng này là đọc sai: phép đo "
            f"không trả lời được câu hỏi đó. Phải chấm riêng trên tầng 4, và "
            f"phải tăng tỷ lệ tầng 4 trong bộ sinh.")


def canh_so_khuon(so_khuon, toi_thieu=KHUON_TOI_THIEU):
    """-> chuoi canh bao, hoac None. Dat o DAU bang, khong nhet xuong cuoi."""
    if so_khuon is None or so_khuon >= toi_thieu:
        return None
    return (f"**Mẫu chỉ nằm trên {so_khuon} khuôn bệnh.** Đơn vị độc lập của bộ "
            f"dữ liệu là khuôn, không phải ca (xem `tach_tap_viet`), nên phép so "
            f"sánh này có {so_khuon} đơn vị độc lập chứ không phải "
            f"{{so_ca}} — nó không nói được gì về bộ khuôn đầy đủ.")


def _so(x, chu_so=4):
    return "—" if x != x else f"{x:.{chu_so}f}".replace(".", ",")


def _pt(x, chu_so=2):
    """Phan tram voi dau phay thap phan — bang trong bao cao tieng Viet."""
    return "—" if x != x else f"{x * 100:.{chu_so}f}".replace(".", ",") + "%"


def bang(ten_goc, diem_theo_nhanh, khuon, khoa="final", goc_theo_id=None):
    """Bang khoang tin cay + so sanh theo cap voi nhanh goc.

    Hai canh bao dat o DAU bang, khong nhet xuong cuoi: so khuon, va cong
    suat. Mot canh bao o cuoi bang thi nguoi doc da doc xong so roi.
    """
    d = [f"### Thước đo `{khoa}`", ""]
    so_khuon = len(set(khuon.values())) if khuon else None
    canh = canh_so_khuon(so_khuon)
    if canh:
        mot = next(iter(diem_theo_nhanh.values()))
        d += ["> " + canh.replace("{so_ca}", str(len(mot))), ""]

    if goc_theo_id:
        cs = do_cong_suat(goc_theo_id)
        goc_diem = diem_theo_nhanh[ten_goc]
        k = khoang(goc_diem, khuon)
        cc = canh_cong_suat(cs, k["cao"] - k["thap"])
        if cc:
            d += ["> " + cc, ""]
        d += ["Phân tầng quy gán của mẫu: "
              + "  ·  ".join(f"{t} **{cs['theo_tang'].get(t, 0)}**"
                             for t in TANG), ""]

    d += ["| Nhánh | Trung bình | KTC 95% theo ca | KTC 95% theo khuôn |",
          "|---|---|---|---|"]
    for ten, diem in diem_theo_nhanh.items():
        kc = khoang(diem)
        kk = khoang(diem, khuon) if khuon else None
        d.append(f"| `{ten}` | {_so(kc['trung_binh'])} | "
                 f"[{_so(kc['thap'])}; {_so(kc['cao'])}] | "
                 f"{'[' + _so(kk['thap']) + '; ' + _so(kk['cao']) + ']' if kk else '—'} |")
    d += ["",
          f"So sánh **theo cặp** với `{ten_goc}` — khoảng tin cậy của HIỆU, "
          "không phải hai khoảng rời:", "",
          "| Nhánh | Hiệu | KTC 95% của hiệu (theo khuôn) | Tỷ lệ dấu ngược |",
          "|---|---|---|---|"]
    goc = diem_theo_nhanh[ten_goc]
    for ten, diem in diem_theo_nhanh.items():
        if ten == ten_goc:
            continue
        s = so_sanh(diem, goc, khuon)
        d.append(f"| `{ten}` | {_so(s['hieu'])} | "
                 f"[{_so(s['thap'])}; {_so(s['cao'])}] | "
                 f"{_pt(s['ty_le_dau_nguoc'], 1)} |")
    d += ["",
          "*Tỷ lệ dấu ngược* là tỷ lệ lần lấy lại mẫu cho hiệu trái dấu với "
          "hiệu đo được. Nhân đôi được một giá trị gần nghĩa với p hai phía. "
          "Không gọi là p: với số khuôn nhỏ thì con số đó không đủ chính xác "
          "để mang tên đó.", ""]
    return "\n".join(d)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--tap-goc", default=None,
                    help="tep bo du lieu de lay khuon benh; mac dinh data/<tap>.jsonl")
    ap.add_argument("--nhanh", nargs="+", default=["B", "C", "D"])
    # Quy uoc `ra_<nhanh>_<tap>.jsonl` da sinh ra mot loi that: ten tep noi
    # `viet_phat_trien` trong khi ket qua chay tren `viet3k_phat_trien`. Cho
    # nay de goi thang duong dan, khong phai vong qua quy uoc ten.
    ap.add_argument("--tep", nargs="+", default=None,
                    metavar="TEN=DUONG_DAN",
                    help="chi dinh thang tung nhanh, vi du B=data/ra_B.jsonl")
    ap.add_argument("--goc", default=None, help="nhanh lam moc so sanh")
    ap.add_argument("--khoa", default="f1_quy_gan",
                    choices=sorted(k for v in HO_THUOC_DO.values() for k in v),
                    help="mac dinh f1_quy_gan — thuoc do chinh cua du an")
    ap.add_argument("--so-lan", type=int, default=SO_LAN_MAC_DINH)
    ap.add_argument("--ra", default=None)
    a = ap.parse_args()
    from src import du_lieu as _dl
    _dl.chan_tap_khoa(a.tap)

    nguon = ({k: Path(v) for k, v in (x.split("=", 1) for x in a.tep)}
             if a.tep else
             {n: THU_MUC_DATA / f"ra_{n}_{a.tap}.jsonl" for n in a.nhanh})
    diem_theo_nhanh, ban_ghi = {}, {}
    for n, tep in nguon.items():
        if not tep.exists():
            print(f"bo qua {n}: khong co {tep}")
            continue
        diem_theo_nhanh[n], bg = diem_tung_ca(tep, a.khoa)
        ban_ghi.update(bg)
    if not diem_theo_nhanh:
        raise SystemExit("khong nap duoc nhanh nao")

    moi_id = sorted({i for d in diem_theo_nhanh.values() for i in d})
    tap_goc = Path(a.tap_goc) if a.tap_goc else THU_MUC_DATA / f"{a.tap}.jsonl"
    khuon = doi_chieu_tap({i: ban_ghi[i] for i in moi_id}, tap_goc)
    goc_theo_id = {b["id"]: b for b in _doc(tap_goc) if b["id"] in set(moi_id)}

    # Van tay in o DAU bang. Mot bang so khong noi no do tren bo nao thi ba
    # thang sau khong doc duoc — va ba lan ho loi "mot ten tep, hai bo du lieu"
    # deu bat dau tu mot bang nhu the.
    from src import phat_bieu, van_tay_bo
    dong_van_tay = [van_tay_bo.mo_ta(tap_goc)]
    # Doi chieu voi CA TEP, khong voi `goc_theo_id` — bien do chi chua cac ca
    # dang duoc do (60 ca), con van tay lap tren ca bo (408 ca). So hai thu do
    # voi nhau thi hang rao bao oan moi lan chay, va mot hang rao bao oan se bi
    # tat di — luc do no thanh vo dung dung vao lan no can len tieng.
    khop, thong_diep = van_tay_bo.khop(tap_goc, _doc(tap_goc))
    if khop is False:
        raise SystemExit(thong_diep)
    thieu = van_tay_bo.nhan_thieu_vi_du(
        tap_goc, {"quan_he": phat_bieu.QUAN_HE,
                  "trang_thai": phat_bieu.TRANG_THAI,
                  "tinh_huong": phat_bieu.TINH_HUONG})
    for truong, cac_nhan in thieu.items():
        dong_van_tay.append(
            f"**`{truong}`: {', '.join(cac_nhan)} không có ví dụ nào trong bộ "
            f"này** — mọi số về nhãn đó là số của một nhãn không có dữ liệu.")

    ten_goc = a.goc or list(diem_theo_nhanh)[0]
    van = bang(ten_goc, diem_theo_nhanh, khuon, a.khoa, goc_theo_id)
    van = "\n".join(f"> {x}" for x in dong_van_tay) + "\n\n" + van
    print(van)
    print(f"\n{len(moi_id)} ca, {len(set(khuon.values()))} khuon, "
          f"bo du lieu {tap_goc.name}")
    if a.ra:
        Path(a.ra).write_text(van + "\n", encoding="utf-8")
        print(f"-> {a.ra}")


if __name__ == "__main__":
    main()
