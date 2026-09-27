# -*- coding: utf-8 -*-
"""Bo 500 hoi thoai phuong ngu DO GPT SINH -> dinh dang ca cua du an. CHI DE DO.

NGUON — doc truoc khi dung. Nguoi dung xac nhan ngay 11/09/2026: bo 500 hoi
thoai (`data/ngoai/phuong_ngu_500.jsonl`) va hai tu dien phuong ngu kem theo do
GPT sinh. Du an co rang buoc cung: KHONG dung mo hinh ngon ngu thuong mai o bat
ky khau nao, ke ca sinh du lieu huan luyen. Nen bo nay:

  - KHONG BAO GIO vao huan luyen hay chon checkpoint. Ten tep ra mang chu "gpt",
    va `du_lieu.chan_du_lieu_gpt` chan moi duong huan luyen doc tep co chu do.
  - KHONG gop vao tap kiem tra cuoi, khong tron voi bo tu sinh.
  - Moi con so tu bo nay phai kem `KHAI_NGUON`, va KHONG duoc goi la hoi thoai
    that.

DAP AN CUA BO NAY KHAC DAP AN CUA DE TAI:
  - khong co luot bang chung, khong co trich dan -> khong do duoc tang khoa
  - `status` gop BA truc ma luoc do du an co y tach (muc chac chan / tinh huong /
    trang thai) -> `ANH_XA` tra lai, va chinh viec anh xa la mot nguon sai
  - chu the ghi bang TU QUAN HE: khuon `daughter_elderly_dizzy` thi "me" la BENH
    NHAN, khuon `allergy_relative` thi "me" la NGUOI NHA. Ai la benh nhan phai tra
    THEO KHUON (`BENH_NHAN`) — mot bang toi DOC TAY tu `speaker_context` va cau hoi
    cua bac si trong tung khuon, khong phai dap an co san. Khuon nao doc khong ra
    thi de trong `BENH_NHAN_MO_HO` va khong cham chu the.
  - hoi thoai 4 luot, 2,2 menh de moi ca

DO DUOC: tim thay menh de khong, CHU THE (benh nhan hay nguoi khac), va LOP muc
khang dinh. Lop quan trong nhat la `KHONG_LA_SU_THAT` (cau hoi chua tra loi, gia
dinh, dang cho ket qua, ban bi thay the, mau thuan): ghi no vao than ho so nhu
mot su that la RO RI.

    python -m src.bo_gpt500 --chuyen          # -> data/gpt500_phuong_ngu.jsonl
    python -m src.bo_gpt500 --do-phuong-ngu   # bang chuan hoa nhan ra tu khong
    python -m src.bo_gpt500 --cham data/ra_C_gpt500_phuong_ngu.jsonl
"""
import argparse
import io
import json
import re
import sys
from collections import Counter, defaultdict

from src import chuan_hoa, duong_dan
from src.thuoc_do_quy_gan import _tu_noi_dung

NGUON = duong_dan.THU_MUC_DU_LIEU / "ngoai" / "phuong_ngu_500.jsonl"
TEN_TAP = "gpt500_phuong_ngu"
TEP_RA = duong_dan.THU_MUC_DU_LIEU / f"{TEN_TAP}.jsonl"
KHAI_NGUON = ("dữ liệu tổng hợp do GPT sinh (người dùng cung cấp 10/09/2026, "
              "xác nhận nguồn 11/09/2026) — chỉ để đo, không huấn luyện")

# Vai trong bo GPT -> vai trong hoi thoai cua du an. Nguoi nha nao cung thanh
# "Nguoi nha" nhu bo tu sinh (mo hinh chua tung thay nhan "Me:", "Vo:"); vai goc
# giu trong truong `vai_goc`. "Tre" la benh nhi TU NOI (khuon child_direct_speech).
VAI = {"Bác sĩ": "Bác sĩ", "Điều dưỡng": "Điều dưỡng", "Bệnh nhân": "Bệnh nhân",
       "Trẻ": "Bệnh nhân"}
VAI_NGUOI_NHA = "Người nhà"

# Ai la BENH NHAN trong tung khuon — doc tay, xem docstring.
BENH_NHAN = {
    "guardian_child_fever": "trẻ",
    "guardian_child_cough": "trẻ",
    "spouse_headache": "chồng",        # "Nguoi dau dau la anh nha chi hay chi?"
    "daughter_elderly_dizzy": "mẹ",    # con gai ke ho nguoi cao tuoi
    "nurse_breathing": "bệnh nhân",
    "allergy_relative": "trẻ",         # di ung la cua ME; benh nhan la tre
    "allergy_patient": "bệnh nhân",
    "medication_unknown": "bệnh nhân",
    "medication_stopped": "cha",       # "Ba anh da ngung tu bao lau?"
    "duration_correction": "trẻ",
    "vomiting_progress": "bệnh nhân",
    "diarrhea_progress": "trẻ",
    "unanswered_question": "bệnh nhân",
    "suspected_diagnosis": "bệnh nhân",
    "conditional_plan": "trẻ",
    "family_history": "mẹ",            # "Hom nay nguoi kham la ai?" "Da la ma toi"
    "surgery_history": "bệnh nhân",
    "vaccination_uncertain": "trẻ",
    "lab_pending": "bệnh nhân",
    "symptom_negation": "bệnh nhân",
    "multiple_relatives": "trẻ",       # ba ngoai la nguoi nha
    "pronoun_resolution": "chồng",     # KHONG CHAC — xem BENH_NHAN_MO_HO
    "child_direct_speech": "trẻ",
    "social_history": "bệnh nhân",
    "contradictory_sources": "trẻ",
}
# Loi chao goi ten mot nguoi ("dua Nam di kham") nhung ten rut ngau nhien, con
# vo chi noi thuoc cua "ong ay" — khong du de biet ong ay co phai benh nhan.
BENH_NHAN_MO_HO = frozenset({"pronoun_resolution"})

KHANG_DINH = "khẳng định"
PHU_DINH = "phủ định"
CHUA_GHI_NHAN = "chưa ghi nhận"
NGHI_NGO = "nghi ngờ"
KHONG_LA_SU_THAT = "không là sự thật"
LOP_SU_THAT = (KHANG_DINH, PHU_DINH, CHUA_GHI_NHAN, NGHI_NGO)

# `status` cua bo GPT -> lop. "chua xac dinh" ("toi khong nho be da dung lan nao")
# gop vao CHUA GHI NHAN: luoc do du an khong co muc rieng, va ca hai deu la mot
# cho TRONG, khong phai mot khang dinh am.
ANH_XA = {
    "khẳng định": KHANG_DINH,
    "bệnh nhân báo cáo": KHANG_DINH,
    "phủ định": PHU_DINH,
    "chưa ghi nhận": CHUA_GHI_NHAN,
    "chưa xác định": CHUA_GHI_NHAN,
    "nghi ngờ": NGHI_NGO,
    "không được kết luận": KHONG_LA_SU_THAT,
    "bị thay thế": KHONG_LA_SU_THAT,
    "mâu thuẫn/chưa giải quyết": KHONG_LA_SU_THAT,
    "giả định": KHONG_LA_SU_THAT,
    "kế hoạch": KHONG_LA_SU_THAT,
    "kế hoạch có điều kiện": KHONG_LA_SU_THAT,
    "đang chờ": KHONG_LA_SU_THAT,
}


# ------------------------------------------------------------------ chuyen doi
def chuyen(ban_ghi) -> dict:
    kich = ban_ghi["scenario_id"]
    if kich not in BENH_NHAN:
        raise SystemExit(f"khuon moi chua co trong BENH_NHAN: {kich}")
    for g in ban_ghi["gold_claims"]:
        if g["status"] not in ANH_XA:
            raise SystemExit(f"status chua anh xa: {g['status']!r} ({ban_ghi['id']})")
    luot = sorted(ban_ghi["dialogue"], key=lambda t: t["turn_id"])
    return {"id": ban_ghi["id"],
            "input": "\n".join(f"{VAI.get(t['speaker'], VAI_NGUOI_NHA)}: {t['text']}"
                               for t in luot),
            "output": "",                   # bo nay khong co ban tham chieu
            "gpt_sinh": True, "khai_nguon": KHAI_NGUON,
            "scenario_id": kich, "region_style": ban_ghi.get("region_style"),
            "phenomena": list(ban_ghi.get("phenomena") or []),
            "dialect_terms_used": list(ban_ghi.get("dialect_terms_used") or []),
            "vai_goc": [t["speaker"] for t in luot],
            "benh_nhan": BENH_NHAN[kich],
            "gold_claims": ban_ghi["gold_claims"]}


def nap(tep):
    return [json.loads(x) for x in open(tep, encoding="utf-8") if x.strip()]


def ghi(nguon=NGUON, tep=TEP_RA):
    ds = [chuyen(b) for b in nap(nguon)]
    ids = [d["id"] for d in ds]
    if len(set(ids)) != len(ids):
        raise SystemExit("id trung trong bo GPT")
    with open(tep, "w", encoding="utf-8") as f:
        for d in ds:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    return ds


# ------------------------------------------------------ bang chuan hoa, tang 1
def do_phuong_ngu(ds):
    """Bang chuan hoa co NHAN RA tu phuong ngu bo nay khai khong.

    VONG TRON: bang chuan hoa lay tu tu dien mo rong, CUNG nguon GPT voi bo nay.
    Con so "nhan ra" chi noi bang phu tu cua chinh nguon cua no; cho TRUOT moi
    la thong tin — tu co trong hoi thoai ma bang khong biet.
    """
    ket, truot = Counter(), Counter()
    for d in ds:
        thap = d["input"].lower()
        cho = [c for c in chuan_hoa.phan_tich(d["input"]) if c.muc_tin]
        for tu in d["dialect_terms_used"]:
            t = tu.lower()
            vt = [m.start() for m in re.finditer(re.escape(t), thap)]
            if not vt:
                ket["khong_thay_trong_hoi_thoai"] += 1
                continue
            if any(c.bat_dau < a + len(t) and a < c.ket_thuc for a in vt for c in cho):
                ket["nhan_ra"] += 1
            else:
                ket["truot"] += 1
                truot[tu] += 1
    return ket, truot


# ------------------------------------------------------------------ cham diem
def _tu(s):
    return set(_tu_noi_dung(chuan_hoa.chuan_hoa(str(s or ""))))


def lop_phat_bieu(p) -> str:
    """Mot phat bieu (dict, luoc do du an) -> lop de so voi `ANH_XA`."""
    if (p.get("tinh_huong") or "thực tế") != "thực tế" or \
            (p.get("trang_thai") or "còn hiệu lực") != "còn hiệu lực":
        return KHONG_LA_SU_THAT
    muc = p.get("do_chac_chan") or "chắc chắn"
    if muc == CHUA_GHI_NHAN:
        return CHUA_GHI_NHAN
    if muc == NGHI_NGO:
        return NGHI_NGO
    return PHU_DINH if p.get("phu_dinh") else KHANG_DINH


def _diem(claim, p):
    """Trung it nhat mot tu noi dung moi tinh; moc thoi gian chi de phan xu hai
    ban cung khai niem ("sot bon ngay" bi thay the, "sot hai ngay" con hieu luc)."""
    a, b = _tu(claim.get("concept")), _tu(p.get("noi_dung"))
    chung = a & b
    if not chung:
        return 0.0
    d = len(chung) / len(a | b)
    t1, t2 = _tu(claim.get("time")), _tu(p.get("moc_thoi_gian"))
    if t1 and t2:
        d += 0.5 * len(t1 & t2) / len(t1 | t2)
    return d


def ghep(claims, ps):
    """Ghep 1-1 tham lam theo diem giam dan -> {chi so claim: chi so phat bieu}."""
    cap = sorted(((_diem(c, p), i, j) for i, c in enumerate(claims)
                  for j, p in enumerate(ps)), key=lambda x: -x[0])
    ra, da = {}, set()
    for d, i, j in cap:
        if d <= 0:
            break
        if i in ra or j in da:
            continue
        ra[i] = j
        da.add(j)
    return ra


def cham_ca(ca, ps, bi_chan=frozenset()):
    """-> mot dong ket qua cho MOI menh de dap an cua ca.

    `ps`: phat bieu (dict) SAU ap luat. `bi_chan`: id phat bieu tang khoa da chan
    — khong vao than ho so, nen khong the ro ri.
    """
    ghep_ = ghep(ca["gold_claims"], ps)
    mo_ho = ca["scenario_id"] in BENH_NHAN_MO_HO
    ra = []
    for i, c in enumerate(ca["gold_claims"]):
        lop = ANH_XA[c["status"]]
        la_bn = c["subject"] == ca["benh_nhan"]
        p = ps[ghep_[i]] if i in ghep_ else None
        than = (p is not None and p.get("id") not in bi_chan
                and lop_phat_bieu(p) in LOP_SU_THAT)
        k = {"id": ca["id"], "scenario_id": ca["scenario_id"], "lop": lop,
             "la_benh_nhan": la_bn, "tim_thay": p is not None, "vao_than": than}
        if lop == KHONG_LA_SU_THAT:
            k["ro_ri"] = than
        elif p is not None:
            k["dung_lop"] = lop_phat_bieu(p) == lop
            if not mo_ho:
                bn_du_doan = p.get("chu_the_id", 0) == 0
                k["dung_chu_the"] = bn_du_doan == la_bn
                k["nguoi_khac_thanh_benh_nhan"] = (not la_bn) and bn_du_doan
        ra.append(k)
    return ra


def _ty_le(ket, loc, truong, khuon):
    """Ty le theo CA roi bootstrap cum THEO KHUON (scenario_id) — 25 cum, moi
    khuon 20 ca gan nhu giong nhau, nen don vi doc lap la khuon, khong phai ca."""
    from src import sai_so
    theo_ca = defaultdict(list)
    for k in ket:
        if loc(k) and k.get(truong) is not None:
            theo_ca[k["id"]].append(1.0 if k[truong] else 0.0)
    if not theo_ca:
        return None
    gt = {i: sum(v) / len(v) for i, v in theo_ca.items()}
    kq = sai_so.khoang(gt, {i: khuon[i] for i in gt})
    kq["so_menh_de"] = sum(len(v) for v in theo_ca.values())
    return kq


def tong_hop(cac_ca, du_doan):
    """`du_doan`: {id: (phat_bieu, bi_chan)}. Ca khong co du doan tinh la khong
    tim thay gi — khong duoc bo di cho dep so."""
    ket = []
    for ca in cac_ca:
        ps, chan = du_doan.get(ca["id"], ([], set()))
        ket.extend(cham_ca(ca, ps, chan))
    khuon = {ca["id"]: ca["scenario_id"] for ca in cac_ca}
    su_that = lambda k: k["lop"] in LOP_SU_THAT             # noqa: E731
    bang = {
        "tim_thay": _ty_le(ket, su_that, "tim_thay", khuon),
        "dung_chu_the": _ty_le(ket, su_that, "dung_chu_the", khuon),
        "dung_lop": _ty_le(ket, su_that, "dung_lop", khuon),
        "ro_ri": _ty_le(ket, lambda k: k["lop"] == KHONG_LA_SU_THAT, "ro_ri", khuon),
        "nguoi_khac_thanh_benh_nhan": _ty_le(
            ket, lambda k: su_that(k) and not k["la_benh_nhan"],
            "nguoi_khac_thanh_benh_nhan", khuon),
    }
    theo_khuon = {}
    for k in ket:
        t = theo_khuon.setdefault(k["scenario_id"], Counter())
        t["menh_de"] += 1
        for truong in ("tim_thay", "dung_chu_the", "dung_lop", "ro_ri",
                       "nguoi_khac_thanh_benh_nhan"):
            if k.get(truong) is not None:
                t[truong + "_n"] += 1
                t[truong] += bool(k[truong])
    return {"bang": bang, "theo_khuon": theo_khuon, "so_ca": len(cac_ca),
            "so_ca_co_du_doan": sum(1 for ca in cac_ca if ca["id"] in du_doan),
            "khai_nguon": KHAI_NGUON}


def nap_du_doan(tep):
    """ra_<nhanh>_gpt500_phuong_ngu.jsonl -> {id: (phat_bieu, id bi chan)}."""
    ra = {}
    for r in nap(tep):
        if "phat_bieu" not in r:
            raise SystemExit(
                f"{tep}: ban ghi khong co truong `phat_bieu` — sinh lai bang "
                f"`python -m src.nhanh --nhanh C C_khoa --tu-dem --tap {TEN_TAP} "
                f"--adapter-trich <adapter>`")
        chan = {k["id"] for k in r.get("khoa", []) if k.get("chan")}
        ra[r["id"]] = (r["phat_bieu"], chan)
    return ra


def _in_bang(tk):
    print(f"NGUON: {tk['khai_nguon']}")
    print(f"ca: {tk['so_ca']} (co du doan: {tk['so_ca_co_du_doan']})")
    for ten, k in tk["bang"].items():
        if k is None:
            print(f"  {ten:28} (khong co menh de)")
            continue
        print(f"  {ten:28} {k['trung_binh']:6.1%}  [{k['thap']:.1%}; {k['cao']:.1%}]"
              f"  n={k['so_menh_de']} menh de / {k['so_ca']} ca / "
              f"{k['so_khuon']} {k['don_vi']}")
    print("  theo khuon (ty le tren menh de):")
    for kich, t in sorted(tk["theo_khuon"].items()):
        o = [f"{ten}={t[ten]}/{t[ten + '_n']}" for ten in
             ("tim_thay", "dung_chu_the", "dung_lop", "ro_ri") if t[ten + "_n"]]
        print(f"    {kich:26} " + "  ".join(o))


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--chuyen", action="store_true")
    ap.add_argument("--do-phuong-ngu", action="store_true")
    ap.add_argument("--cham", nargs="+", default=None,
                    help="tep ra_<nhanh>_gpt500_phuong_ngu.jsonl")
    a = ap.parse_args()
    if a.chuyen:
        ds = ghi()
        print(f"Ghi {len(ds)} ca -> {TEP_RA}\nNGUON: {KHAI_NGUON}")
    if a.do_phuong_ngu or a.cham:
        ds = nap(TEP_RA)
    if a.do_phuong_ngu:
        ket, truot = do_phuong_ngu(ds)
        tong = ket["nhan_ra"] + ket["truot"]
        print(f"bang chuan hoa nhan ra {ket['nhan_ra']}/{tong} lan xuat hien tu "
              f"phuong ngu duoc khai; khong thay trong hoi thoai: "
              f"{ket['khong_thay_trong_hoi_thoai']}")
        print("  (VONG TRON: bang va bo nay cung nguon GPT)")
        for tu, n in truot.most_common():
            print(f"  truot: {tu!r} x{n}")
    for tep in a.cham or []:
        print(f"\n=== {tep}")
        _in_bang(tong_hop(ds, nap_du_doan(tep)))


if __name__ == "__main__":
    main()
