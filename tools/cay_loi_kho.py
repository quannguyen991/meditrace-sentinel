# -*- coding: utf-8 -*-
"""Loi KHO cay thang vao DAP AN (dict) — tinh vi, gan dung, de lot qua mat va qua luat.

Hai cong dung:
  1. Do do kho: lop canh bao bat duoc bao nhieu loi kho (`src.do_cay_loi --kho`).
  2. Du lieu huan luyen sau nay: cap (ban dung, ban co loi kho) cung dinh dang `du_lieu_trich`
     — dung cho DPO (chosen/rejected) hoac day mot bo kiem tra tim loi.

CHI lay tu tap TRAIN (`data/viet_train_v2.jsonl`). Khong dung tap giu kin `thach_thuc_v2`
hay `viet_kiem_tra_cuoi*`.

    moi, cac_cay = cay_kho(ca, "doi_ben", random.Random(1))
    moi, cac_cay = cay_nhieu(ca, rng, so_loi=3)
    cap = xuat_cap(ca, rng, so_loi=2)   # {"id","chosen","rejected","loi"}
"""
import argparse
import copy
import hashlib
import json
import random
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from src import tri_thuc_thuoc

GOC = Path(__file__).resolve().parents[1]

LOAI_KHO = ("so_lech_nho", "doi_don_vi_thoi_gian", "doi_ben", "doi_muc_do", "doi_tan_suat",
            "nguoi_nha_thanh_benh_nhan", "bo_tu_nghi", "thuoc_gan_giong", "phu_dinh_trong_chuoi",
            "qua_khu_hien_tai", "bo_dieu_kien", "dinh_chinh_nguoc", "bia_phu_dinh", "gan_nham_luot")

NHOM_KHO = {
    "so_lech_nho": {"ENTITY_VALUE", "TEMPORAL"},
    "doi_don_vi_thoi_gian": {"TEMPORAL", "ENTITY_VALUE"},
    "doi_ben": {"ENTITY_VALUE"},
    "doi_muc_do": {"ENTITY_VALUE", "QUALITY"},
    "doi_tan_suat": {"ENTITY_VALUE"},
    "nguoi_nha_thanh_benh_nhan": {"SUBJECT_ATTRIBUTION"},
    "bo_tu_nghi": {"NEGATION_ASSERTION"},
    "thuoc_gan_giong": {"ENTITY_VALUE", "UNSUPPORTED"},
    "phu_dinh_trong_chuoi": {"NEGATION_ASSERTION"},
    "qua_khu_hien_tai": {"TEMPORAL"},
    "bo_dieu_kien": {"PLAN_FACT_CONDITIONAL"},
    "dinh_chinh_nguoc": {"STATE_UPDATE", "TEMPORAL"},
    "bia_phu_dinh": {"UNSUPPORTED", "EVIDENCE_PROVENANCE"},
    "gan_nham_luot": {"EVIDENCE_PROVENANCE", "UNSUPPORTED"},
}

_SO = re.compile(r"(?<![\w.,])(\d+)([.,]\d+)?(?!\w)")
_TG = re.compile(r"(?<!\w)(\d+|một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|vài|mấy)\s+(giờ|ngày|tuần|tháng)(?!\w)")
_DOI_TG = {"giờ": "ngày", "ngày": "tuần", "tuần": "tháng", "tháng": "tuần"}
_CAP = lambda *ps: [(re.compile(rf"(?<!\w){a}(?!\w)"), b) for a, b in ps]  # noqa: E731
_BEN = _CAP(("trái", "phải"), ("phải", "trái"), ("trên", "dưới"), ("dưới", "trên"))
_MUC_DO = _CAP(("âm ỉ", "dữ dội"), ("dữ dội", "âm ỉ"), ("nhẹ", "nặng"), ("nặng", "nhẹ"), ("tăng", "giảm"),
               ("giảm", "tăng"), ("ít", "nhiều"), ("nhiều", "ít"), ("hơi", "rất"), ("rất", "hơi"))
_TAN_SUAT = _CAP(("một lần", "hai lần"), ("hai lần", "ba lần"), ("ba lần", "hai lần"), ("1 lần", "2 lần"),
                 ("2 lần", "3 lần"), ("3 lần", "2 lần"), ("buổi sáng", "buổi tối"), ("buổi tối", "buổi sáng"),
                 ("mỗi sáng", "mỗi tối"), ("mỗi tối", "mỗi sáng"))
_NGHI = re.compile(r"(?<!\w)(có thể là|có thể|nghi ngờ|nghi|hình như|chắc là|có lẽ|nghĩ nhiều đến|nghĩ đến|"
                   r"theo dõi)(?!\w)\s*")
_NEU = re.compile(r"\s*(?<!\w)(nếu|khi|trong trường hợp)(?!\w).*$")
_PHU = re.compile(r"(?<!\w)(không|chưa|chẳng|chả)(?!\w)")
TRIEU_CHUNG_BIA = ("buồn nôn", "đau đầu", "tiêu chảy", "phát ban", "chóng mặt", "ho ra máu", "đau ngực",
                   "khó nuốt", "vàng da", "phù chân", "tiểu buốt", "co giật")


@dataclass(frozen=True)
class CayKho:
    loai: str
    chi_so: int
    mo_ta: str


def _luot(ca):
    return [d for d in str(ca.get("input") or "").split("\n") if d.strip()]


def _vai(ca, so):
    l = _luot(ca)
    return l[so - 1].split(":", 1)[0].strip().lower() if 1 <= so <= len(l) else ""


def _nv(v):
    return v.startswith(("bác sĩ", "điều dưỡng"))


def _hieu_luc(d):
    return d.get("trang_thai", "còn hiệu lực") != "bị thay thế" and d.get("luot")


def _doi_cap(van, cap, rng):
    """Thay MOT cum theo bang cap — chon ngau nhien trong cac cum co mat."""
    co = [(m, b) for p, b in cap for m in p.finditer(van)]
    if not co:
        return None
    m, b = rng.choice(sorted(co, key=lambda x: (x[0].start(), x[1])))
    return van[:m.start()] + b + van[m.end():]


def _ung(ca, loai, tranh):
    da = ca["dap_an"]
    ok = [i for i, d in enumerate(da) if i not in tranh and _hieu_luc(d)]
    if loai == "so_lech_nho":
        return [i for i in ok if _SO.search(da[i]["noi_dung"]) or _SO.search(da[i].get("moc_thoi_gian") or "")]
    if loai == "doi_don_vi_thoi_gian":
        return [i for i in ok if _TG.search(da[i]["noi_dung"]) or _TG.search(da[i].get("moc_thoi_gian") or "")]
    if loai in ("doi_ben", "doi_muc_do", "doi_tan_suat"):
        cap = {"doi_ben": _BEN, "doi_muc_do": _MUC_DO, "doi_tan_suat": _TAN_SUAT}[loai]
        return [i for i in ok if any(p.search(da[i]["noi_dung"]) for p, _ in cap)
                or (loai == "doi_tan_suat" and any(p.search((da[i].get("thuoc") or {}).get("so_lan") or "")
                                                   for p, _ in cap))]
    if loai == "nguoi_nha_thanh_benh_nhan":
        return [i for i in ok if da[i]["chu_the"] != "bệnh nhân"]
    if loai == "bo_tu_nghi":
        return [i for i in ok if (da[i].get("do_chac_chan") or "chắc chắn") != "chắc chắn"]
    if loai == "thuoc_gan_giong":
        return [i for i in ok if tri_thuc_thuoc.regex_ten_thuoc().search(da[i]["noi_dung"])]
    if loai == "phu_dinh_trong_chuoi":
        l = _luot(ca)
        ra = []
        for i in ok:
            ls = set(da[i]["luot"])
            van = " ".join(l[s - 1] for s in ls if 1 <= s <= len(l)).lower()
            khac = [j for j, e in enumerate(da) if j != i and _hieu_luc(e) and ls & set(e["luot"])
                    and bool(e.get("phu_dinh")) != bool(da[i].get("phu_dinh"))]
            if _PHU.search(van) and khac:
                ra.append(i)
        return ra
    if loai == "qua_khu_hien_tai":
        return [i for i in ok if da[i].get("thoi_gian_su_kien") in ("quá khứ", "hiện tại")]
    if loai == "bo_dieu_kien":
        return [i for i in ok if da[i].get("tinh_huong") == "giả định"]
    if loai == "dinh_chinh_nguoc":
        ra = []
        for i in ok:
            cu = [j for j, e in enumerate(da) if j not in tranh and e.get("trang_thai") == "bị thay thế"
                  and e["noi_dung"] == da[i]["noi_dung"]]
            if cu:
                ra.append(i)
        return ra
    if loai == "gan_nham_luot":
        n = len(_luot(ca))
        return [i for i in ok if any(1 <= s <= n and s not in da[i]["luot"] and not _nv(_vai(ca, s))
                                     for s in (min(da[i]["luot"]) - 2, min(da[i]["luot"]) - 1,
                                               max(da[i]["luot"]) + 1, max(da[i]["luot"]) + 2))]
    raise ValueError(loai)


def cay_kho(ca: dict, loai: str, rng: random.Random, tranh=frozenset()) -> Optional[Tuple[dict, List[CayKho]]]:
    """-> (ban sao `ca` da cay, [CayKho]) hoac None. `ca` khong doi. `tranh`: chi so khong duoc cham."""
    moi = copy.deepcopy(ca)
    da = moi["dap_an"]
    if loai == "bia_phu_dinh":
        hoi = str(ca["input"]).lower()
        tc = [t for t in TRIEU_CHUNG_BIA if t not in hoi]
        bn = [s for s in range(1, len(_luot(ca)) + 1) if not _nv(_vai(ca, s))]
        if not tc or not bn:
            return None
        t, s = rng.choice(tc), rng.choice(bn)
        da.append({"chu_the": "bệnh nhân", "noi_dung": t, "muc": "BỆNH SỬ HIỆN TẠI", "moc_thoi_gian": None,
                   "phu_dinh": True, "tinh_huong": "thực tế", "luot": [s], "thoi_gian_su_kien": "hiện tại",
                   "quan_he": None, "quan_he_voi": None, "trang_thai": "còn hiệu lực",
                   "do_chac_chan": "chắc chắn", "hanh_vi": "trả lời", "thuoc": None,
                   "trich_dan": [_luot(ca)[s - 1].split(":", 1)[-1].strip()]})
        return moi, [CayKho(loai, len(da) - 1, f"không {t} (bịa, lượt {s})")]
    ung = _ung(moi, loai, tranh)
    if not ung:
        return None
    i = rng.choice(ung)
    d = da[i]
    cu = d["noi_dung"]
    if loai == "so_lech_nho":
        truong = "noi_dung" if _SO.search(d["noi_dung"]) else "moc_thoi_gian"
        m = _SO.search(d[truong])
        moi_so = str(max(0, int(m.group(1)) + rng.choice((-1, 1))) or 2)
        d[truong] = d[truong][:m.start(1)] + moi_so + d[truong][m.end(1):]
        if d.get("thuoc") and d["thuoc"].get("lieu") and m.group(1) in d["thuoc"]["lieu"]:
            d["thuoc"] = dict(d["thuoc"], lieu=d["thuoc"]["lieu"].replace(m.group(1), moi_so, 1))
        mo_ta = f"{m.group(0)} -> {moi_so}{m.group(2) or ''}"
    elif loai == "doi_don_vi_thoi_gian":
        truong = "noi_dung" if _TG.search(d["noi_dung"]) else "moc_thoi_gian"
        m = _TG.search(d[truong])
        d[truong] = d[truong][:m.start(2)] + _DOI_TG[m.group(2)] + d[truong][m.end(2):]
        mo_ta = f"{m.group(0)} -> {m.group(1)} {_DOI_TG[m.group(2)]}"
    elif loai in ("doi_ben", "doi_muc_do", "doi_tan_suat"):
        cap = {"doi_ben": _BEN, "doi_muc_do": _MUC_DO, "doi_tan_suat": _TAN_SUAT}[loai]
        moi_nd = _doi_cap(d["noi_dung"], cap, rng)
        if moi_nd is not None:
            d["noi_dung"] = moi_nd
        if loai == "doi_tan_suat" and d.get("thuoc") and d["thuoc"].get("so_lan"):
            sl = _doi_cap(d["thuoc"]["so_lan"], cap, rng)
            if sl:
                d["thuoc"] = dict(d["thuoc"], so_lan=sl)
        mo_ta = f"{cu} -> {d['noi_dung']}"
    elif loai == "nguoi_nha_thanh_benh_nhan":
        mo_ta = f"{d['chu_the']} -> bệnh nhân: {cu}"
        d["chu_the"] = "bệnh nhân"
    elif loai == "bo_tu_nghi":
        d["do_chac_chan"] = "chắc chắn"
        d["noi_dung"] = _NGHI.sub("", d["noi_dung"]).strip() or d["noi_dung"]
        mo_ta = f"{cu} -> chắc chắn: {d['noi_dung']}"
    elif loai == "thuoc_gan_giong":
        m = tri_thuc_thuoc.regex_ten_thuoc().search(d["noi_dung"])
        ten = m.group(1).lower()
        hc = tri_thuc_thuoc.hoat_chat(ten)
        khac = sorted({t for t in tri_thuc_thuoc.tat_ca_ten() if " " not in t and tri_thuc_thuoc.hoat_chat(t) != hc})
        gan = [t for t in khac if t[:3] == ten[:3]] or [t for t in khac if t[:2] == ten[:2]] or \
              [t for t in khac if t[:1] == ten[:1]] or khac
        t = rng.choice(gan)
        d["noi_dung"] = d["noi_dung"][:m.start()] + t + d["noi_dung"][m.end():]
        if d.get("thuoc"):
            d["thuoc"] = dict(d["thuoc"], ten=t)
        mo_ta = f"{ten} -> {t}"
    elif loai == "phu_dinh_trong_chuoi":
        d["phu_dinh"] = not d.get("phu_dinh")
        mo_ta = f"đảo phủ định trong lượt có cả có/không: {cu}"
    elif loai == "qua_khu_hien_tai":
        d["thoi_gian_su_kien"] = "hiện tại" if d["thoi_gian_su_kien"] == "quá khứ" else "quá khứ"
        mo_ta = f"-> {d['thoi_gian_su_kien']}: {cu}"
    elif loai == "bo_dieu_kien":
        d["tinh_huong"] = "kế hoạch"
        d["noi_dung"] = _NEU.sub("", d["noi_dung"]).strip() or d["noi_dung"]
        mo_ta = f"{cu} -> {d['noi_dung']} (mất điều kiện)"
    elif loai == "dinh_chinh_nguoc":
        j = rng.choice([j for j, e in enumerate(da) if j not in tranh and e.get("trang_thai") == "bị thay thế"
                        and e["noi_dung"] == cu])
        d["trang_thai"], da[j]["trang_thai"] = "bị thay thế", "còn hiệu lực"
        mo_ta = f"giữ bản cũ #{j} ({da[j].get('moc_thoi_gian')}), bỏ bản mới ({d.get('moc_thoi_gian')})"
    elif loai == "gan_nham_luot":
        n = len(_luot(ca))
        ch = [s for s in (min(d["luot"]) - 2, min(d["luot"]) - 1, max(d["luot"]) + 1, max(d["luot"]) + 2)
              if 1 <= s <= n and s not in d["luot"] and not _nv(_vai(ca, s))]
        s = rng.choice(ch)
        mo_ta = f"lượt {d['luot']} -> [{s}]"
        d["luot"] = [s]
        d["trich_dan"] = list(d.get("trich_dan") or [])[:1]
    return moi, [CayKho(loai, i, mo_ta)]


def cay_nhieu(ca: dict, rng: random.Random, so_loi: int = 2, loai=LOAI_KHO):
    """Cay `so_loi` loi KHAC LOAI vao KHAC DONG. -> (ca moi, [CayKho]) hoac None khi khong du."""
    thu = list(loai)
    rng.shuffle(thu)
    cur, ra, tranh = ca, [], set()
    for l in thu:
        r = cay_kho(cur, l, rng, frozenset(tranh))
        if r is None:
            continue
        cur, cs = r
        ra += cs
        tranh |= {c.chi_so for c in cs}
        if len(ra) == so_loi:
            return cur, ra
    return (cur, ra) if ra else None


def _chi_so_ra(ca, i):
    """Chi so dap an -> chi so trong `phat_bieu` cua dau ra huan luyen (du_lieu_trich bo dong khong luot)."""
    from src import bakeoff
    from src.du_lieu_trich import ban_lap_ly_do_kham
    _ds, so_luot = bakeoff.danh_so_luot(ca["input"])
    lap = ban_lap_ly_do_kham(ca["dap_an"])
    giu = [j for j, m in enumerate(ca["dap_an"]) if j not in lap and any(1 <= n <= so_luot for n in m.get("luot") or [])]
    return giu.index(i) if i in giu else None


def xuat_cap(ca: dict, rng: random.Random, so_loi: int = 1) -> Optional[dict]:
    """-> {"id", "chosen", "rejected", "loi": [...]} — chosen/rejected la chuoi JSON dau ra huan luyen
    (`du_lieu_trich.doi_mot_ca`). Loi nhac (prompt) lay tu `data/trich_train_v2.jsonl` theo `id`."""
    from src.du_lieu_trich import doi_mot_ca
    r = cay_nhieu(ca, rng, so_loi) if so_loi > 1 else None
    if r is None:
        for l in rng.sample(LOAI_KHO, len(LOAI_KHO)):
            r = cay_kho(ca, l, rng)
            if r:
                break
    if r is None:
        return None
    moi, cs = r
    _a, tot = doi_mot_ca(ca)
    _b, xau = doi_mot_ca(moi)
    if tot == xau:
        return None
    loi = [dict(asdict(c), chi_so_ra=_chi_so_ra(moi, c.chi_so)) for c in cs]
    if any(x["chi_so_ra"] is None for x in loi):
        # Dong bi cay khong con trong dau ra huan luyen (du_lieu_trich bo dong lap / khong luot):
        # nhan loi se tro vao khoang khong — bo ca cap (7% o lan sinh dau 25/11).
        return None
    return {"id": ca["id"], "chosen": tot, "rejected": xau, "loi": loi}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Sinh cap loi kho tu tap TRAIN")
    ap.add_argument("--nguon", default="data/viet_train_v2.jsonl")
    ap.add_argument("--ra", default="data/cay_loi/cap_loi_kho_train.jsonl")
    ap.add_argument("--moi-ca", type=int, default=3, help="so cap moi ca (1, 2, 3 loi luan phien)")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args(argv)
    assert "kiem_tra" not in a.nguon and "thach_thuc" not in a.nguon, "chi sinh tu tap train"
    sys.stdout.reconfigure(encoding="utf-8")
    ds = [json.loads(l) for l in (GOC / a.nguon).read_text(encoding="utf-8").splitlines() if l.strip()]
    from collections import Counter
    dem, n = Counter(), 0
    with open(GOC / a.ra, "w", encoding="utf-8") as f:
        for ca in ds:
            for k in range(a.moi_ca):
                h = int(hashlib.sha256(f"{a.seed}:{ca['id']}:{k}".encode()).hexdigest()[:12], 16)
                cap = xuat_cap(ca, random.Random(h), so_loi=k % 3 + 1)
                if cap:
                    cap["bien_the"] = k
                    f.write(json.dumps(cap, ensure_ascii=False) + "\n")
                    n += 1
                    dem.update(x["loai"] for x in cap["loi"])
    print(f"{n} cap tu {len(ds)} ca -> {a.ra}")
    for l, c in dem.most_common():
        print(f"  {l:28} {c}")


if __name__ == "__main__":
    main()
