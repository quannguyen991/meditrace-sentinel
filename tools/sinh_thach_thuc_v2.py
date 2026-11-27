# -*- coding: utf-8 -*-
"""Bo thu thach v2 cho lop canh bao: chi tren khuon CHUA NHIN.

VI SAO. Lop canh bao (`src/canh_bao/`) va khoa bang chung duoc viet khi nhin cac ca
cua 4 bo thu thach cu, sinh tu 200 khuon goc. So do tren bo cu vi the thien lac quan.
Bo nay chi rut khuon (a) NGOAI 200 khuon goc va (b) thuoc tap PHAT TRIEN cua kho mo
rong — khong bao gio khuon train, khong bao gio tap kiem tra cuoi.

Sau bo, moi bo `so_ca` ca (mac dinh 40):
  dinh_chinh     moi ca mang mot bay cap nhat (xoay vong BAY_CAP_NHAT)
  doi_chu_the    cap A/B dao nguoi mang di ung (nhu `thach_thuc.cap_doi_chu_the`)
  phuong_ngu     cap A/B co / khong tu phuong ngu
  nhieu_asr      cap A/B: ban sach / ban mat dau tieng Viet + mat dau cau
  tra_loi_ngan   MOI: >= 3 cap "Bac si hoi co/khong — benh nhan dap <= 3 chu", noi dung
                 nam trong cau hoi, menh de dap an dan toi CA HAI luot
  khong_dau_cau  MOI, cap A/B: ban B bo dau cau, viet thuong, chen "ờ"/"à" va lap tu dau
                 luot — nhu loi chep tu am thanh. Dap an giong het tru `trich_dan`.

Sinh bang LUAT tu `sinh_hoi_thoai_viet`, khong dung mo hinh ngon ngu.

    python -m tools.sinh_thach_thuc_v2 --the-he v2-luat-2026-11-25
"""
import argparse
import hashlib
import json
import random
import re
import sys
from functools import lru_cache
from pathlib import Path

from src.bo_du_lieu import nap_du_lieu as du_lieu
from src.bo_du_lieu import kho_khuon as kho_khuon
from src.bo_du_lieu import nhieu_asr as nhieu_asr
from src.bo_du_lieu import van_tay_bo as van_tay_bo
from src.bo_du_lieu import sinh_hoi_thoai_viet as sh
from src.bo_du_lieu.sinh_bo_thach_thuc import BAY_CAP_NHAT, _so_cap_phuong_ngu, bo_trich_dan

GOC = Path(__file__).resolve().parents[1]
THU_MUC_RA = GOC / "data" / "thach_thuc_v2"
TAP = "phat_trien"
CAC_BO = ("dinh_chinh", "doi_chu_the", "phuong_ngu", "nhieu_asr", "tra_loi_ngan", "khong_dau_cau")
SO_LAN_THU = 4000
SO_CAP_TOI_THIEU = 3
TRA_LOI_XAC_NHAN = ("Dạ phải ạ.", "Vâng ạ.", "Dạ đúng rồi.", "Có ạ.", "Dạ có.")
MUC_HOI_DUOC = {"TIỀN SỬ BỆNH", "BỆNH SỬ HIỆN TẠI", "THUỐC ĐANG DÙNG", "DỊ ỨNG", "LÝ DO KHÁM BỆNH"}
_LOI_DAU = re.compile(r"^(dạ|vâng|thưa|bác sĩ|bác sỹ|bác\s*,|đúng rồi|ạ|à|ờ|ừ|thêm vào đó|ngoài ra|với lại|đi kèm với đó là|kèm theo đó|chưa kể"
                      r"|,|\s)+", re.IGNORECASE)
# Nguoi benh tu xung -> bac si goi lai. "mình" la cach bac si goi nguoi benh trung tinh.
_TU_XUNG = {"Bệnh nhân": re.compile(r"(?<!\w)(tôi|em|con|cháu)(?!\w)"),
            "Người nhà": re.compile(r"(?<!\w)(tôi)(?!\w)")}


def _hoi_lai(noi: str, vai: str) -> str:
    """Doan nguoi benh vua noi -> phan noi dung cau hoi cua bac si."""
    noi = _LOI_DAU.sub("", noi).rstrip(" .!ạ")
    noi = re.sub(r"\s*,?\s*(?<!\w)bác s[ĩỹ]( ơi)?(?!\w)", "", noi).strip(" ,")
    mau = _TU_XUNG.get(vai)
    return mau.sub("mình", noi) if mau else noi
TU_DEM = ("ờ", "à", "ừm")


def _hat(*phan):
    return int(hashlib.sha256(":".join(str(x) for x in phan).encode("utf-8")).hexdigest()[:12], 16)


@lru_cache(maxsize=1)
def khuon_moi():
    """Ten khuon thuoc tap phat trien cua kho mo rong va KHONG thuoc 200 khuon goc."""
    goc = {b["ten"] for b in kho_khuon._goc()}
    return frozenset(t for t, tap in sh.bang_tap_khuon(mo_rong=True).items()
                     if tap == TAP and t not in goc)


def _tuy(**kw):
    return sh.TuyChon(chi_tap=TAP, mo_rong=True, **kw)


def _luot(ca):
    return [d for d in ca["input"].split("\n") if d.strip()]


def _sinh(ma, h, **kw):
    return sh.sinh_mot_ca(ma, random.Random(h), _tuy(**kw))


def _het_lan_thu(bo, i):
    raise RuntimeError(f"khong sinh duoc ca {i} cua bo {bo} sau {SO_LAN_THU} lan thu")


# ---- bon bo cu, tren khuon moi -------------------------------------------------

def bo_dinh_chinh(so_ca, seed):
    ra = []
    for i in range(so_ca):
        bay = BAY_CAP_NHAT[i % len(BAY_CAP_NHAT)]
        for thu in range(SO_LAN_THU):
            ca = _sinh(f"v2dch_{i:03d}", _hat("v2_dinh_chinh", seed, i, thu),
                       ep_bay=(bay,), ep_nguoi_ke=(bay == "nguon_khac_nhau"))
            if ca["benh"] in khuon_moi() and bay in ca["bay"]:
                break
        else:
            _het_lan_thu("dinh_chinh", i)
        ca.update(thach_thuc="dinh_chinh", bay_chinh=bay)
        ra.append(ca)
    return ra


def cap_doi_chu_the(so_cap, seed):
    ra = []
    for i in range(so_cap):
        for thu in range(SO_LAN_THU):
            h = _hat("v2_doi_chu_the", seed, i, thu)
            chung = dict(ep_bay=("di_ung_nguoi_nha",), ep_nguoi_ke=True, di_ung_cua_nguoi_ke=True)
            a = _sinh(f"v2dct_{i:03d}_A", h, **chung)
            if a["benh"] not in khuon_moi():
                continue
            b = _sinh(f"v2dct_{i:03d}_B", h, **chung, doi_chu_the=True)
            la, lb = _luot(a), _luot(b)
            khac = [j for j, (x, y) in enumerate(zip(la, lb)) if x != y]
            if len(la) == len(lb) and len(khac) == 1:
                break
        else:
            _het_lan_thu("doi_chu_the", i)
        for x, bt in ((a, "A"), (b, "B")):
            x.update(thach_thuc="doi_chu_the", cap=i, bien_the=bt, luot_khac=khac[0] + 1)
        ra += [a, b]
    return ra


def cap_phuong_ngu(so_cap, seed):
    ra = []
    for i in range(so_cap):
        mien = ("nam", "trung")[i % 2]
        for thu in range(SO_LAN_THU):
            h = _hat("v2_phuong_ngu", seed, i, thu)
            a = _sinh(f"v2png_{i:03d}_A", h, ep_mien=mien)
            if a["benh"] not in khuon_moi() or not a["tu_phuong_ngu"]:
                continue
            b = _sinh(f"v2png_{i:03d}_B", h, ep_mien=mien, ap_phuong_ngu=False)
            if (not b["tu_phuong_ngu"] and len(_luot(a)) == len(_luot(b))
                    and _so_cap_phuong_ngu(a["dap_an"]) == _so_cap_phuong_ngu(b["dap_an"])):
                break
        else:
            _het_lan_thu("phuong_ngu", i)
        for x, bt in ((a, "A"), (b, "B")):
            x.update(thach_thuc="phuong_ngu", cap=i, bien_the=bt)
        ra += [a, b]
    return ra


def _ca_sach(ten, i, seed):
    for thu in range(SO_LAN_THU):
        h = _hat(f"v2_{ten}", seed, i, thu)
        a = _sinh(f"x", h)
        if a["benh"] in khuon_moi():
            return a, h
    _het_lan_thu(ten, i)


def cap_nhieu_asr(so_cap, seed, ti_le=0.5):
    ra = []
    for i in range(so_cap):
        a, h = _ca_sach("nhieu_asr", i, seed)
        a["id"] = f"v2asr_{i:03d}_A"
        b = nhieu_asr.nhieu_ca(a, random.Random(h ^ 0x5A5A), ti_le)
        b["id"] = f"v2asr_{i:03d}_B"
        if bo_trich_dan(a["dap_an"]) != bo_trich_dan(b["dap_an"]):
            raise RuntimeError(f"lam nhieu da doi dap an o cap {i}")
        for x, bt in ((a, "A"), (b, "B")):
            x.update(thach_thuc="nhieu_asr", cap=i, bien_the=bt, ti_le_nhieu=ti_le)
        ra += [a, b]
    return ra


# ---- tra_loi_ngan ---------------------------------------------------------------

def doi_tra_loi_ngan(ca, rng):
    """Viet lai TAI CHO cac cap (bac si hoi, nguoi benh tra loi) thanh: bac si hoi
    "Có phải <noi dung nguoi benh vua noi> không ạ?", nguoi benh dap mot cau xac nhan
    <= 3 chu. Khong chen luot nen khong phai danh so lai.

    Chi viet lai luot T khi: luot T-1 la bac si va KHONG menh de nao dan toi T-1; moi
    menh de dan toi T la cua benh nhan, khang dinh (phu_dinh=False), muc hoi duoc, va
    tat ca co CUNG MOT trich dan. Noi dung cau hoi lay tu trich dan do (khong lay ca
    luot, de khong keo theo "Dạ thưa bác sĩ,"), bo tu noi dau cau, doi tu xung "tôi" ->
    "mình". Menh de sau do dan toi CA HAI luot, trich dan = [noi dung hoi, cau dap].
    -> (ca moi, so cap da viet lai)."""
    L = _luot(ca)
    dan = {}
    for k, m in enumerate(ca["dap_an"]):
        for j in m.get("luot") or []:
            dan.setdefault(j, []).append(k)
    dap_an = [dict(m) for m in ca["dap_an"]]
    so = 0
    for t in range(2, len(L) + 1):  # t dem tu 1
        v0, _, _ = L[t - 2].partition(": ")
        v1, _, than = L[t - 1].partition(": ")
        if v0 != "Bác sĩ" or v1 == "Bác sĩ" or (t - 1) in dan or t not in dan:
            continue
        cac = [dap_an[k] for k in dan[t]]
        if not all(m["chu_the"] == "bệnh nhân" and not m["phu_dinh"] and m["muc"] in MUC_HOI_DUOC
                   and m.get("luot") == [t] for m in cac):
            continue
        trich = {tuple(m.get("trich_dan") or []) for m in cac}
        if len(trich) != 1 or len(next(iter(trich))) != 1:
            continue
        noi = _hoi_lai(next(iter(trich))[0], v1)
        if len(noi.split()) < 2:
            continue
        dap = rng.choice(TRA_LOI_XAC_NHAN)
        L[t - 2] = f"Bác sĩ: Có phải {noi} không ạ?"
        L[t - 1] = f"{v1}: {dap}"
        for m in cac:
            m["luot"] = [t - 1, t]
            m["trich_dan"] = [noi, dap.rstrip(".")]
        so += 1
    return dict(ca, input="\n".join(L), dap_an=dap_an), so


def bo_tra_loi_ngan(so_ca, seed):
    ra = []
    for i in range(so_ca):
        for thu in range(SO_LAN_THU):
            h = _hat("v2_tra_loi_ngan", seed, i, thu)
            a = _sinh(f"v2tln_{i:03d}", h)
            if a["benh"] not in khuon_moi():
                continue
            b, so = doi_tra_loi_ngan(a, random.Random(h ^ 0x7A7A))
            if so >= SO_CAP_TOI_THIEU:
                break
        else:
            _het_lan_thu("tra_loi_ngan", i)
        b.update(thach_thuc="tra_loi_ngan", so_cap_tra_loi_ngan=so)
        ra.append(b)
    return ra


# ---- khong_dau_cau --------------------------------------------------------------

def doi_khong_dau_cau(ca, rng):
    """Ban sach -> ban chep tu am thanh: bo dau cau (giu 38,5), viet thuong toan bo,
    va o khoang nua so luot: chen mot tu dem ("ờ", "à", "ừm") va lap tu dau. Chi THEM
    o DAU luot nen moi trich dan van la chuoi con sau khi ap cung phep viet thuong."""
    dong = []
    for d in ca["input"].split("\n"):
        if not d.strip():
            dong.append(d)
            continue
        vai, ngan, than = d.partition(": ")
        than = re.sub(r"\s{2,}", " ", nhieu_asr.bo_dau_cau(than)).strip().lower()
        if than and rng.random() < 0.5:
            tu = than.split(" ")
            than = " ".join([rng.choice(TU_DEM), tu[0]] + tu)
        dong.append(f"{vai}{ngan}{than}")
    dap_an = []
    for m in ca["dap_an"]:
        m = dict(m)
        if m.get("trich_dan"):
            m["trich_dan"] = [re.sub(r"\s{2,}", " ", nhieu_asr.bo_dau_cau(t)).strip().lower()
                              for t in m["trich_dan"]]
        dap_an.append(m)
    return dict(ca, input="\n".join(dong), dap_an=dap_an)


def cap_khong_dau_cau(so_cap, seed):
    ra = []
    for i in range(so_cap):
        a, h = _ca_sach("khong_dau_cau", i, seed)
        a["id"] = f"v2kdc_{i:03d}_A"
        b = doi_khong_dau_cau(a, random.Random(h ^ 0x3C3C))
        b["id"] = f"v2kdc_{i:03d}_B"
        for x, bt in ((a, "A"), (b, "B")):
            x.update(thach_thuc="khong_dau_cau", cap=i, bien_the=bt)
        ra += [a, b]
    return ra


# ---------------------------------------------------------------------------------

def sinh_tat_ca(so_ca=40, seed=42):
    """-> {ten bo: danh sach ca}. Bo cap dung so_ca // 2 cap."""
    du_lieu.chan_tap_khoa(TAP)
    cap = max(so_ca // 2, 1)
    return {
        "dinh_chinh": bo_dinh_chinh(so_ca, seed),
        "doi_chu_the": cap_doi_chu_the(cap, seed),
        "phuong_ngu": cap_phuong_ngu(cap, seed),
        "nhieu_asr": cap_nhieu_asr(cap, seed),
        "tra_loi_ngan": bo_tra_loi_ngan(so_ca, seed),
        "khong_dau_cau": cap_khong_dau_cau(cap, seed),
    }


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--so-ca", type=int, default=40)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--the-he", required=True)
    a = ap.parse_args(argv)
    THU_MUC_RA.mkdir(parents=True, exist_ok=True)
    for ten, ds in sinh_tat_ca(a.so_ca, a.seed).items():
        dp = THU_MUC_RA / f"thach_thuc_{ten}_{TAP}.jsonl"
        dp.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in ds) + "\n", encoding="utf-8")
        van_tay_bo.ghi(dp, ds, a.the_he, hat=a.seed, ghi_chu=f"thach thuc v2 {ten}, khuon moi cua tap {TAP}")
        print(f"{dp.name:48} {len(ds):4d} ca  {len({c['benh'] for c in ds})} khuon")


if __name__ == "__main__":
    main()
