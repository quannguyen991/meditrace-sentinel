# -*- coding: utf-8 -*-
"""Do lop canh bao tren bon bo thu thach (TAP PHAT TRIEN), so voi BO CHAM TU DONG.

NHAN DUNG DE DO la ma loi cua `cham_he_thong.loi_phat_bieu` — bo cham tu dong,
KHONG phai nhan nguoi. Bo cham co gioi han da biet (xem memory/bao cao): `khong_can_cu`
bi thoi phong vi nguong ghep 0,6 — mot phat bieu dien dat khac dap an bi tinh la
"khong can cu". Nen:
  - do chinh xac cua bo phat hien nhom UNSUPPORTED se THAP GIA
  - moi con so o day la "so voi bo cham tu dong", phai ghi dung nhu vay khi bao cao

THAM DO, KHONG PHAI KIEM DINH. Lop canh bao viet SAU dang ky truoc (dang-ky-truoc.md);
chay tren tap phat trien, khong cham tap kiem tra cuoi. Nguong va luat cua lop nay da
duoc sua khi nhin cac ca phat trien (vd dct_019_B), nen so o day la so tren du lieu
da nhin — can mot tap moi de do khong thien lech.

Hai cau hoi:
  1. Tung ma canh bao: bao dung bao nhieu (precision), bat duoc bao nhieu loi cung
     loai (recall), so voi bo cham.
  2. Chinh sach C (dang dung) vs D (moi): LOT = phat bieu co loi nguy hiem ma van
     vao than; CHAN THUA = phat bieu khong loi bi dua sang can xac nhan.

    python -m src.do_canh_bao
"""
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from src import cham_he_thong, cong_rui_ro, duong_dan, du_lieu, sinh_benh_an
from src.canh_bao import gop, nhat_ky
from src.canh_bao.loai import LOAI, PHIEN_BAN
from src.phat_bieu import PhatBieu

THU_MUC = duong_dan.GOC_DU_AN / "kaggle-ra" / "the-he-8-chinh-sach-C"
CAC_TAP = ("thach_thuc_dinh_chinh_phat_trien", "thach_thuc_doi_chu_the_phat_trien",
           "thach_thuc_nhieu_asr_phat_trien", "thach_thuc_phuong_ngu_phat_trien")
NHANH = "C_khoa"

# Nhom canh bao -> ma loi cua bo cham cung loai. Nhom khong co ma tuong ung (bo sot,
# chat luong, chep am, quan he) khong tinh recall theo loai.
NHOM_SANG_MA = {
    "SUBJECT_ATTRIBUTION": {"sai_chu_the"},
    "NEGATION_ASSERTION": {"sai_muc_phu_dinh", "sai_muc_chac_chan"},
    "PLAN_FACT_CONDITIONAL": {"sai_muc_tinh_huong"},
    "STATE_UPDATE": {"ban_cu", "sai_muc"},
    "UNSUPPORTED": {"khong_can_cu"},
    "EVIDENCE_PROVENANCE": {"khong_can_cu"},
    "ENTITY_VALUE": {"sai_thuoc", "sai_thoi_gian", "khong_can_cu"},
    "TEMPORAL": {"sai_thoi_gian", "sai_thuoc", "ban_cu"},
    "QUALITY": {"trung_lap"},
    "RELATION_CAUSALITY": set(cham_he_thong.LOI),
}
LOI_THAT = set(cham_he_thong.LOI)          # khong tinh trung_lap la loi
NGUY_HIEM = cham_he_thong.LOAI_NGHIEM_TRONG  # di_ung, thuoc, chan_doan


def _p(x):
    return round(x, 3) if x == x else None


def chay():
    thong_ke_ma = defaultdict(lambda: Counter())       # ma -> {ban, dung_loai, co_loi}
    recall = defaultdict(lambda: Counter())            # ma bo cham -> {tong, co_canh_bao_cung_loai, co_canh_bao}
    chinh_sach = {k: Counter() for k in ("C", "D")}
    so_hien, so_pb = [], 0
    nhat = []
    bo_sot = Counter()
    for tap in CAC_TAP:
        goc = {c["id"]: c for c in du_lieu.nap_mau(THU_MUC / f"{tap}.jsonl")}
        for r in du_lieu.nap_mau(THU_MUC / f"ra_{NHANH}_{tap}.jsonl"):
            ca = goc[r["id"]]
            ps = [PhatBieu(**d) for d in r["phat_bieu"]]
            loi, sot = cham_he_thong.loi_phat_bieu(ca, r["phat_bieu"])
            kq = gop.chay(ps, r["input"])
            muc_c = {g["id"]: g["muc"] for g in r.get("ghi_chu", [])}
            nhan_nhat = {}
            for p in ps:
                if p.trang_thai == "bị thay thế":
                    continue
                so_pb += 1
                ma_loi, loai = loi.get(p.id, ([], cong_rui_ro.loai_thong_tin(p)))
                co_loi = bool(set(ma_loi) & LOI_THAT)
                v = kq["theo_phat_bieu"][p.id]
                so_hien.append(int(v["chinh"] is not None) + len(v["khac"]))
                for c in v["tat_ca"]:
                    dung_loai = bool(set(ma_loi) & NHOM_SANG_MA.get(c.nhom, set()))
                    t = thong_ke_ma[c.ma]
                    t["ban"] += 1
                    t["dung_loai"] += dung_loai
                    t["co_loi"] += co_loi
                    t["doi_trang_thai"] += c.anh_huong_trang_thai
                    nhan_nhat[(p.id, c.ma)] = dung_loai
                nhom_bao = {c.nhom for c in v["tat_ca"]}
                for m in set(ma_loi) & (LOI_THAT | {"sai_muc_phu_dinh", "sai_muc_chac_chan", "sai_muc_tinh_huong"}):
                    recall[m]["tong"] += 1
                    recall[m]["co_canh_bao"] += bool(v["tat_ca"])
                    recall[m]["cung_loai"] += any(m in NHOM_SANG_MA.get(n, set()) for n in nhom_bao)
                # chinh sach: vao than hay can xac nhan
                vao_c = muc_c.get(p.id) not in sinh_benh_an.MUC_PHU_TAT_CA and p.id in muc_c
                vao_d = kq["trang_thai_D"][p.id]["trang_thai"] == gop.DA_KIEM_CHUNG
                for ten, vao in (("C", vao_c), ("D", vao_d)):
                    k = chinh_sach[ten]
                    k["tong"] += 1
                    k["co_loi"] += co_loi
                    k["vao_than"] += vao
                    if co_loi and vao:
                        k["lot"] += 1
                        if loai in NGUY_HIEM:
                            k["lot_nguy_hiem"] += 1
                    if co_loi and loai in NGUY_HIEM:
                        k["loi_nguy_hiem"] += 1
                    if not co_loi and not vao:
                        k["chan_thua"] += 1
                    if not co_loi:
                        k["khong_loi"] += 1
            # bo sot: canh bao toan ca co cham dung luot cua menh de dap an bi sot khong
            luot_sot = [set(d.get("luot") or []) for d in sot]
            luot_cb = [set(c.luot) for c in kq["toan_ca"]]
            bo_sot["dap_an_sot"] += len(luot_sot)
            bo_sot["sot_co_canh_bao"] += sum(any(a & b for b in luot_cb) for a in luot_sot)
            bo_sot["canh_bao"] += len(luot_cb)
            bo_sot["canh_bao_trung_sot"] += sum(any(a & b for b in luot_sot) for a in luot_cb)
            nhat += nhat_ky.dong(f"{tap}/{r['id']}", kq, nhan_nhat)

    bang_ma = []
    for ma, t in sorted(thong_ke_ma.items(), key=lambda x: -x[1]["ban"]):
        bang_ma.append({"ma": ma, "nhom": LOAI[ma].nhom, "tin_cay": LOAI[ma].tin_cay, "so_lan_bao": t["ban"],
                        "chinh_xac_cung_loai": _p(t["dung_loai"] / t["ban"]),
                        "chinh_xac_co_loi_bat_ky": _p(t["co_loi"] / t["ban"]),
                        "so_lan_doi_trang_thai": t["doi_trang_thai"]})
    bang_recall = {m: {"so_loi": t["tong"], "co_canh_bao_cung_loai": _p(t["cung_loai"] / t["tong"]),
                       "co_canh_bao_bat_ky": _p(t["co_canh_bao"] / t["tong"])} for m, t in sorted(recall.items())}

    def ty(k):
        return {"so_phat_bieu": k["tong"], "co_loi": k["co_loi"], "vao_than": k["vao_than"],
                "lot": k["lot"], "ty_le_lot": _p(k["lot"] / max(k["co_loi"], 1)),
                "lot_nguy_hiem": k["lot_nguy_hiem"], "loi_nguy_hiem": k["loi_nguy_hiem"],
                "ty_le_lot_nguy_hiem": _p(k["lot_nguy_hiem"] / max(k["loi_nguy_hiem"], 1)),
                "chan_thua": k["chan_thua"], "ty_le_chan_thua": _p(k["chan_thua"] / max(k["khong_loi"], 1))}
    ra = {
        "phien_ban_canh_bao": PHIEN_BAN, "phien_ban_bo_cham": cham_he_thong.PHIEN_BAN,
        "chinh_sach_C": cong_rui_ro.CHINH_SACH, "chinh_sach_D": gop.CHINH_SACH_D,
        "cac_tap": CAC_TAP, "nhanh": NHANH, "so_phat_bieu_con_hieu_luc": so_pb,
        "ghi_chu": "So voi BO CHAM TU DONG, khong phai nhan nguoi. Tham do tren tap phat trien da nhin.",
        "theo_ma": bang_ma, "do_phu_theo_loi_bo_cham": bang_recall,
        "chinh_sach": {k: ty(v) for k, v in chinh_sach.items()},
        "canh_bao_hien_moi_phat_bieu": _p(sum(so_hien) / max(len(so_hien), 1)),
        "bo_sot": {**bo_sot, "do_phu": _p(bo_sot["sot_co_canh_bao"] / max(bo_sot["dap_an_sot"], 1)),
                   "chinh_xac": _p(bo_sot["canh_bao_trung_sot"] / max(bo_sot["canh_bao"], 1))},
    }
    return ra, nhat


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ra, nhat = chay()
    dich = duong_dan.THU_MUC_KET_QUA
    (dich / "canh-bao.json").write_text(json.dumps(ra, ensure_ascii=False, indent=2), encoding="utf-8")
    tep_nk = dich / "canh-bao-nhat-ky.jsonl"
    tep_nk.unlink(missing_ok=True)
    nhat_ky.ghi(tep_nk, nhat)
    print(json.dumps({k: ra[k] for k in ("so_phat_bieu_con_hieu_luc", "chinh_sach", "canh_bao_hien_moi_phat_bieu",
                                         "bo_sot")}, ensure_ascii=False, indent=1))
    print(f"{'ma':38} {'bao':>5} {'cx_loai':>8} {'cx_loi':>7} {'doi_tt':>6}  tin_cay")
    for d in ra["theo_ma"]:
        print(f"{d['ma']:38} {d['so_lan_bao']:5d} {str(d['chinh_xac_cung_loai']):>8} "
              f"{str(d['chinh_xac_co_loi_bat_ky']):>7} {d['so_lan_doi_trang_thai']:6d}  {d['tin_cay']}")
    print("do phu:", json.dumps(ra["do_phu_theo_loi_bo_cham"], ensure_ascii=False))
    print(f"\nGhi {dich / 'canh-bao.json'} va {tep_nk}")


if __name__ == "__main__":
    main()
