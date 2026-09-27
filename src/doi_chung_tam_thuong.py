# -*- coding: utf-8 -*-
"""Hai doi chung KHONG DUNG MO HINH. Chung chan hai cau hoi khac nhau.

VI SAO CAN. Tai lieu cua du an da viet, nhieu lan, rang "mot he thong chi lam
dung mot viec — gan trieu chung cho nguoi vua noi — van dat do chinh xac cao".
Cau do LAP LUAN chu khong DO: khong co cau hinh nao chay duong tat do. Nguoi
cham se tu hoi dung cau hoi day, va khong co so de tra loi.

    duong tat A   chu the = NGUOI NOI cua luot
    duong tat B   chu the = BENH NHAN, luon luon

Hai duong tat nay SAI O HAI CHO DOI NHAU, va do la ca y nghia cua chung:

    tang 3  nguoi nha ke HO benh nhan      -> A sai,  B dung
    tang 4  nguoi nha ke VE CHINH MINH     -> A dung, B sai

Nen mot he thong that phai hon CA HAI tren CA HAI tang. Hon mot duong tat o
mot tang thi chua noi len gi — no co the chi dang lam dung viec cua duong tat
kia.

CHUNG DUNG CHUNG MOI KHAU KHAC voi nhanh B: cung `sinh_benh_an.sinh`, cung
bang tra muc, cung cach dien dat. Chi khac DUNG MOT cho — buoc trich va buoc
gan chu the. Neu khac o nhung cho lat vat thi chenh lech do duoc se lan lon
nguyen nhan.

GIOI HAN, phai ghi vao bao cao. Buoc trich o day la tach cau bang luat, tho
hon mo hinh that nhieu. Nen con so cua chung la SAN DUOI cho ca duong ong, va
doc dung phai la "mo hinh dong gop bao nhieu so voi luat tho", khong phai
"luat lam duoc viec nay".

    python -m src.doi_chung_tam_thuong --tap viet_phat_trien --n 60
"""
import argparse
import io
import json
import re
import sys
from pathlib import Path

from src import sinh_benh_an

# Ba duong tat. Hai dau khac nhau o CACH GAN CHU THE; duong thu ba khac o
# PHAM VI — no lay ca luot bac si.
#
# VI SAO CAN DUONG THU BA. Hai duong dau bo han luot bac si, nen chung khong
# viet ket qua kham, chan doan hay ke hoach: bao phu tang bac si chi 4,17%. Mot
# san duoi bo mat mot phan ba ban nhap la san YEU GIA, va san yeu gia lam duong
# ong trong tot hon thuc te. `day_du` lay ca luot bac si voi chu the = benh
# nhan, va do la san duoi dung de doi chieu.
#
# DUONG THU TU (16/09/2026) — `context`. Giong `day_du` o moi khau, chi khac cach
# gan chu the: dung bang tu kieu ConText (`src/context_vi.py`) thay vi hai duong tat.
# VI SAO CAN: truc chu the cua du an co tien le truc tiep la truc `Experiencer` cua
# ConText (Harkema, Chapman va cong su, 2009), chay bang mot bang tu. Khong co duong
# nay thi khong tra loi duoc cau "mo hinh dong gop bao nhieu so voi mot bang tu".
DUONG = ("nguoi_noi", "benh_nhan", "day_du", "context", "context_vai")

# Tieu tu va cum mo dau khong mang thong tin lam sang. Bo truoc khi tach cau,
# neu khong thi moi menh de deu bat dau bang "da" hoac "vang".
RAC_DAU = re.compile(r"^(dạ|vâng|thưa|ừ|à|ạ|thì|vậy|thế)\b[\s,]*", re.I)
RAC_CUOI = re.compile(r"[\s,]*(ạ|nhé|nghen|nghe|đấy|cơ|mà|rồi)\s*$", re.I)

# Cau giao tiep, khong mang thong tin lam sang. Giu lai thi san duoi thap GIA
# — va san thap gia lam mo hinh trong tot hon thuc te, nen phai bo.
CAU_GIAO_TIEP = re.compile(
    r"^(cảm ơn|cám ơn|xin cảm ơn|vâng|dạ|được|ok|không có gì|tôi cảm ơn"
    r"|chào|tạm biệt|nhờ bác sĩ|bác sĩ xem)\b", re.I)

# Cum chuyen y: tach o day vi hai ben thuong la hai chu the khac nhau.
#   "Toi thi di ung aspirin, CON chau chua thay bi bao gio"
TACH_MENH_DE = re.compile(r"[.;?!]|,\s*(?=còn\b|mà\b|nhưng\b)", re.I)

# Tu mo dau menh de bao hieu nguoi noi dang noi VE CHINH MINH.
#
# BANG NAY DO TU NGU LIEU, khong tu phong doan. Ban dau toi viet
#
#     ("tôi", "em", "mình", "cháu", "con", "bà", "ông", "mẹ", "bố")
#
# roi do tren 681 ca — dem tu mo dau cua menh de trong luot NGUOI NHA, doi chieu
# voi `chu_the` that trong dap an:
#
#     tu      ve BENH NHAN   ve chinh minh
#     cháu         438             5
#     con          235             0
#     bà            98             9
#     ông           78             9
#     tôi           28            58
#     em            18            13
#     mẹ             2             7
#     bố             3             7
#
# Bon tu dau la NGUOC HOAN TOAN voi gia dinh cua toi: trong hoi thoai kham benh
# Viet Nam, nguoi nha goi BENH NHAN la "chau"/"con", va benh nhan cao tuoi duoc
# goi la "ba"/"ong". Giu chung trong bang nay lam doi chung sai o dung tang 3 —
# tang dong nhat trong ba tang kho.
#
# "em" thi 18/13, gan nhu tung dong xu, nen bo: mot luat doi chung phai la luat
# RO RANG, khong phai luat doan bua.
#
# "minh" khong xuat hien lan nao nhung giu lai vi no khong bao gio mo ho.
TU_XUNG_MINH = ("tôi", "mình", "mẹ", "bố")

VAI_BENH_NHAN = ("bệnh nhân",)
VAI_BAC_SI = ("bác sĩ", "điều dưỡng")


def tach_luot(hoi_thoai):
    """-> [(so_luot_dem_tu_1, vai, noi_dung_luot)]."""
    ra = []
    for i, dong in enumerate(
            [d for d in str(hoi_thoai or "").split("\n") if d.strip()], 1):
        m = re.match(r"^([^:]{1,30}):\s*(.*)$", dong)
        ra.append((i, m.group(1).strip(), m.group(2).strip()) if m
                  else (i, "?", dong.strip()))
    return ra


def _gon(cau):
    """Bo tieu tu dau va cuoi. Lap o dau vi chung di thanh chum.

    "Vang a, toi sot ba hom roi" -> bo mot lan duoc "a, toi sot ba hom roi",
    con nguyen mot tieu tu o dau. Phai lap cho toi khi khong con.
    """
    cau = cau.strip()
    for _ in range(4):
        moi = RAC_DAU.sub("", cau).lstrip(" ,")
        if moi == cau:
            break
        cau = moi
    cau = RAC_CUOI.sub("", cau)
    return cau.strip(" ,.")


# Cau hoi cua bac si: khong mang thong tin lam sang. Nhan ra bang dau hoi hoac
# cum hoi o dau. Loi bac si con lai (ket qua kham, chan doan, ke hoach) thi CO
# mang thong tin va phai lay.
CAU_HOI = re.compile(r"\?|^(có|còn|đã|bao|mấy|nhà mình|cháu có|em có|anh có"
                     r"|chị có|cô có|ngoài ra|từ khi|bị từ)\b", re.I)


def menh_de_bang_luat(hoi_thoai, lay_bac_si=False):
    """-> [(so_luot, vai, noi_dung)].

    `lay_bac_si=False` bo han luot bac si — dung cho hai duong tat thuan, de
    chung chi do DUNG cach gan chu the.

    `lay_bac_si=True` lay them loi bac si KHONG phai cau hoi: ket qua kham,
    chan doan, ke hoach. Khong lay cau hoi, vi cau hoi khong la menh de lam
    sang va dua vao thi ban nhap day rac.
    """
    ra = []
    for so, vai, noi in tach_luot(hoi_thoai):
        if vai.lower() in VAI_BAC_SI:
            if not lay_bac_si or CAU_HOI.search(noi):
                continue
        for phan in TACH_MENH_DE.split(noi):
            if not phan:
                continue
            g = _gon(phan)
            # Duoi 2 tu thi khong phai menh de lam sang, chi la tieu tu.
            if g and len(g.split()) >= 2 and not CAU_GIAO_TIEP.match(g):
                ra.append((so, vai, g))
    return ra


def _noi_ve_chinh_minh(noi_dung):
    """Menh de co dau hieu noi ve CHINH nguoi dang noi khong.

    Chi dung cho duong tat `nguoi_noi`: no can biet luot nay la nguoi noi tu
    ke ve minh hay ke ho. Day van la mot luat tho — dung tu xung o dau menh de.
    """
    dau = (noi_dung or "").strip().lower().split()
    return bool(dau) and dau[0] in TU_XUNG_MINH


def phat_bieu_bang_luat(hoi_thoai, duong="nguoi_noi"):
    """-> danh sach phat bieu tho cua mot duong doi chung. KHONG goi mo hinh.

    `duong`:
      nguoi_noi  chu the = nguoi noi cua luot (benh nhan -> 0, nguoi nha -> 1)
      benh_nhan  chu the = 0 cho moi menh de
      day_du     nhu `benh_nhan` nhung lay ca loi bac si
      context    chu the doc tu bang tu kieu ConText (`src/context_vi.py`)

    MOT BAN MA DUY NHAT (gop 16/09/2026). Truoc do `sinh_ban_nhap` va `_ps_cua`
    dung hai ban chep tay khac nhau: ban dung de CHAM thieu han `chu_the_id`, nen
    ban nhap va bang phat bieu cua cung mot duong noi hai dieu khac nhau — dung ho
    lo~i "hai khau cua mot du an dung hai dinh nghia" ma chinh tep nay canh bao.
    """
    if duong not in DUONG:
        raise SystemExit(f"duong phai la mot trong {DUONG}")
    ps = []
    for i, (so, vai, noi) in enumerate(
            menh_de_bang_luat(
            hoi_thoai,
            lay_bac_si=(duong in ("day_du", "context", "context_vai")))):
        la_bn_noi = vai.lower() in VAI_BENH_NHAN
        la_bs_noi = vai.lower() in VAI_BAC_SI
        if duong in ("context", "context_vai"):
            # Bang tu kieu ConText: chu the doc tu CHINH menh de, khong tu vai
            # nguoi noi. Loi bac si cung di qua cung mot bang — "bà ngoại có bị
            # tiểu đường không" thi chu the la ba ngoai, du bac si noi.
            from src import context_vi
            chu_the_id = context_vi.chu_the_cua(noi, vai)
            # `context_vai` = bang tu CONG vai nguoi noi. Vi sao tach lam hai duong:
            # bang tu kieu ConText khong nhin vai nguoi noi duoc, nen no khong the
            # dung o cau "Toi bi roi loan lo au" DO NGUOI NHA noi — do tren bo doi
            # chu the 16/09/2026, phan lon 70 loi cua duong `context` la dung cau nay.
            # Hai duong canh nhau tach duoc dong gop cua bang tu khoi dong gop cua vai.
            if (duong == "context_vai" and chu_the_id == 0
                    and not la_bn_noi and not la_bs_noi
                    and _noi_ve_chinh_minh(noi)):
                chu_the_id = 1
        elif duong == "benh_nhan" or la_bs_noi:
            # Loi bac si: chu the luon la benh nhan. Day khong phai duong tat,
            # day la dung — va chinh cho nay `sua_cuc_bo` da hieu sai 104 lan.
            chu_the_id = 0
        elif la_bn_noi:
            chu_the_id = 0
        else:
            # Nguoi nha dang noi. Duong tat nay gan cho NGUOI NOI, tuc la
            # nguoi nha — tru khi menh de khong co dau hieu tu xung, luc do
            # gan cho benh nhan moi dung voi chinh no ("gan cho nguoi vua
            # noi" chi co nghia khi cau noi VE nguoi do).
            chu_the_id = 1 if _noi_ve_chinh_minh(noi) else 0
        # `chu_the` la CHUOI ten nguoi, `chu_the_id` la so. Giu ca hai vi cac
        # bo cham doc truong khac nhau: `sinh_benh_an` doc `chu_the_id`, con
        # `do_bo_chan_doan.kiem_chu_the` doc `chu_the`. Thieu mot truong thi bo
        # cham kia doc chuoi rong va cho qua het — no khong bao loi.
        ten = "bệnh nhân" if chu_the_id == 0 else vai.lower()
        if chu_the_id == 1 and duong in ("context", "context_vai"):
            # Ten nguoi lay tu CHINH tu da kich hoat, khong lay vai nguoi noi: bo
            # cham doi chieu danh tinh, "người nhà" thay cho "anh trai" van tinh sai.
            from src import context_vi
            ten = context_vi.ten_chu_the_cua(noi) or vai.lower()
        ps.append({"id": i, "nguoi_noi": vai, "chu_the_id": chu_the_id,
                   "chu_the": ten, "ten_chu_the": ten,
                   "noi_dung": noi, "bang_chung": [so],
                   "do_chac_chan": "chắc chắn", "phu_dinh": False,
                   "tinh_huong": "thực tế", "thoi_gian_su_kien": "chưa rõ",
                   "moc_thoi_gian": None, "trang_thai": "còn hiệu lực",
                   "quan_he": None, "quan_he_voi": None})
    return ps


def sinh_ban_nhap(hoi_thoai, duong="nguoi_noi", ten_nguoi_nha="người nhà"):
    """-> (van_ban, ghi_chu, so_menh_de). KHONG goi mo hinh."""
    ps = phat_bieu_bang_luat(hoi_thoai, duong)
    van, ghi_chu = sinh_benh_an.sinh(ps, id_benh_nhan=0,
                                    ten_chu_the={1: ten_nguoi_nha})
    return van, ghi_chu, len(ps)


def chay(mau_list, duong):
    """-> danh sach ban ghi cung dinh dang `ra_<nhanh>_<tap>.jsonl`."""
    ra = []
    for m in mau_list:
        van, ghi_chu, n = sinh_ban_nhap(m["input"], duong)
        ra.append({"id": m["id"], "input": m["input"],
                   "tham_chieu": m.get("output") or m.get("tham_chieu") or "",
                   "du_doan": van, "du_doan_khong_muc_phu": van,
                   # `phat_bieu` de `cham_he_thong` cham duoc duong doi chung bang
                   # CUNG mot bo cham voi duong ong (16/09/2026). Thieu truong nay
                   # thi bo cham bo qua ca nhanh va in mot dong canh bao.
                   "phat_bieu": phat_bieu_bang_luat(m["input"], duong),
                   "ghi_chu": ghi_chu, "so_phat_bieu": n,
                   "so_can_xac_nhan": sum(1 for g in ghi_chu
                                          if g["muc"] == sinh_benh_an.MUC_PHU),
                   "so_luot_goi": 0, "token_vao": 0, "token_ra": 0,
                   "loi_ban_ghi": []})
    return ra


def chay_bo_chan_doan(so_moi_bay=60, duong_list=DUONG):
    """Chay cac duong tat tren BO CHAN DOAN va cham theo tung tinh huong.

    VI SAO O DAY. Tap phat trien chi co **7 menh de tang 4 tren 514** (1,36%),
    nen moi so do tren tang 4 co khoang tin cay vo dung. Bo chan doan thi CAN
    BANG: nhom `chu_the` — "Toi thi di ung X, con chau chua thay bi" — co dung
    60 ca, gap 8,5 lan.

    Day la cho duy nhat hien co de do tang 4 voi cong suat that, va no chay
    KHONG CAN GPU vi doi chung khong goi mo hinh.
    """
    from src import do_bo_chan_doan, sinh_bo_chan_doan

    bo = sinh_bo_chan_doan.sinh_bo(so_moi_bay, seed=42)
    ra = {}
    for duong in duong_list:
        theo_bay = {}
        for mau in bo:
            _van, _gc, _n = sinh_ban_nhap(mau["input"], duong)
            ps = [p for p in _ps_cua(mau["input"], duong)]
            dat, _ly_do = do_bo_chan_doan.cham(mau, ps)
            theo_bay.setdefault(mau["bay"], []).append(dat)
        ra[duong] = theo_bay
    return ra, bo


def _ps_cua(hoi_thoai, duong):
    """Phat bieu tho cua mot duong doi chung — mot ban ma duy nhat voi ban nhap."""
    return phat_bieu_bang_luat(hoi_thoai, duong)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--duong", nargs="+", default=list(DUONG), choices=DUONG)
    ap.add_argument("--bo-chan-doan", type=int, default=0, metavar="N",
                    help="chay tren bo chan doan, N ca MOI tinh huong")
    a = ap.parse_args()
    from src import du_lieu as _dl
    _dl.chan_tap_khoa(a.tap)

    if a.bo_chan_doan:
        ra, bo = chay_bo_chan_doan(a.bo_chan_doan, a.duong)
        from src import sinh_bo_chan_doan
        print(f"Doi chung khong mo hinh tren {len(bo)} ca bo chan doan "
              f"({len(sinh_bo_chan_doan.BAY)} tinh huong x {a.bo_chan_doan})\n")
        rong = max(len(b) for b in sinh_bo_chan_doan.BAY) + 2
        print(f"{'Tinh huong':{rong}}" +
              "".join(f"{d:>16}" for d in a.duong))
        for bay in sinh_bo_chan_doan.BAY:
            dong = f"{bay:{rong}}"
            for d in a.duong:
                ds = ra[d].get(bay, [])
                dong += (f"{sum(ds)}/{len(ds)} = {100 * sum(ds) / len(ds):.0f}%"
                         .rjust(16) if ds else "—".rjust(16))
            print(dong)
        print(f"\nNhom `chu_the` la tang 4: \"Toi thi di ung X, con chau chua "
              f"thay bi\".\nTap phat trien chi co 7 menh de tang 4 tren 514; "
              f"o day co {a.bo_chan_doan}.")
        return

    tep = Path("data") / f"{a.tap}.jsonl"
    mau = [json.loads(l) for l in open(tep, encoding="utf-8") if l.strip()]
    if a.n:
        mau = mau[:a.n]
    for duong in a.duong:
        kq = chay(mau, duong)
        ra = Path("data") / f"ra_tat_{duong}_{a.tap}.jsonl"
        ra.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in kq),
                      encoding="utf-8")
        print(f"{len(kq)} ca, {sum(r['so_phat_bieu'] for r in kq)} menh de "
              f"-> {ra}")


if __name__ == "__main__":
    main()
