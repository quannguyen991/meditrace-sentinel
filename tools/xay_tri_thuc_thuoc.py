# -*- coding: utf-8 -*-
"""Chuyen tri thuc thuoc rai rac vao data/tri_thuc_thuoc.json — CHAY MOT LAN (25/11/2026).

Doc cac bang CU luc chung con viet cung trong ma:
  aho_corasick_duoc_thu.CO_SO_DU_LIEU_DUOC_THU_2022   32 hoat chat, biet duoc, lieu 24h
  duoc_ly_lam_sang.LIEU_TOI_DA_NGAY                   lieu toi da nguoi lon
  guardrails (LIEU_TRAN trong ham)                    trung voi bang tren — chep tay vao day
  kiem_duyet_bhyt_va_bo_sot.LIEU_TRAN_NHI_KHOA_MG_KG_NGAY, BIET_DUOC_CHUA_PARACETAMOL
  cong_rui_ro.THUOC_KHOANG_DIEU_TRI_HEP               thuoc khoang dieu tri hep
  thuc_the.TU_DIEN_THUOC                              tu dien ten
  ten hoat chat trong ke hoach dieu tri cua 657 khuon (kho_khuon, mo_rong=True)
KHONG them con so moi. Cho hai bang trai nhau: lay so THAP hon (than trong hon) va ghi
`mau_thuan`. Sau khi cac mo-dun cu doc tu JSON, chay lai tep nay se doc vong — vi vay
can `--ghi-de` moi chay khi JSON da co.

    python -m tools.xay_tri_thuc_thuoc --ghi-de
"""
import argparse
import json
import re
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
DICH = GOC / "data" / "tri_thuc_thuoc.json"

N_AHO = "src/aho_corasick_duoc_thu.py (bảng ghi “Dược thư Quốc gia Việt Nam 2022”, không ghi số trang)"
N_NGUOI_LON = "src/duoc_ly_lam_sang.py LIEU_TOI_DA_NGAY và src/guardrails.py LIEU_TRAN (không ghi nguồn)"
N_TRE_EM = "src/kiem_duyet_bhyt_va_bo_sot.py LIEU_TRAN_NHI_KHOA_MG_KG_NGAY (không ghi nguồn)"
N_NTI = "src/cong_rui_ro.py THUOC_KHOANG_DIEU_TRI_HEP (không ghi nguồn)"
N_KHUON = "tên hoạt chất trong kế hoạch điều trị của khuôn bệnh (src/khuon_*.py, ngu_lieu_viet.py); không kèm ngưỡng"
N_TEN = "src/thuc_the.py TU_DIEN_THUOC hoặc danh sách tên của tầng 4.5 cũ; không kèm ngưỡng"

# Tieng Viet bo 'e' cuoi; xu ly chung trong tri_thuc_thuoc._khoa. Day chi la ten THAT SU khac.
TEN_KHAC = {
    "paracetamol": ["acetaminophen"],
    "co-trimoxazole": ["cotrimoxazole", "trimethoprim-sulfamethoxazole", "sulfamethoxazole-trimethoprim"],
    "benzylpenicillin": ["penicillin g"],
    "valproat": ["valproate", "valproic acid", "natri valproat"],
    "amlodipin": ["amlodipine"],
}
# Biet duoc moi (khong co trong bang cu) — chi ten, khong so.
BIET_DUOC_THEM = {"salbutamol": ["ventolin"], "methylprednisolone": ["medrol"], "omeprazole": [],
                  "acenocoumarol": ["sintrom"]}
# Sua bang cu: sintrom la ACENOCOUMAROL, khong phai warfarin; aminophylline la mot hoat chat
# rieng (muoi theophylline-ethylenediamine), khong phai biet duoc cua theophylline.
BO_KHOI_BIET_DUOC = {"warfarin": {"sintrom"}, "theophylline": {"aminophylline"}}
NHOM_KHONG_PHAI_THUOC = {"statin", "cephalosporin", "fluoroquinolone", "thiazide", "triptan", "aminopenicillin",
                         "disease", "orabase", "ceramide", "bromide", "kinase", "methicillin"}
_HAU_TO = re.compile(r"(cillin|mycin|micin|cyclin|floxacin|pril|sartan|statin|olol|prazol|prazole|dipin|dipine|azol"
                     r"|azole|mab|tinib|parin|xaban|semide|lukast|setron|zepam|zolam|ofen|fenac|coxib|sone|solon"
                     r"|olone|formin|flozin|triptan|vir|cycline|nidazol|cef\w+|ceph\w+|plase|rnase|dornase)$")
CAN_TRA = {
    "omeprazole": "Hai bảng cũ trái nhau: 40 mg/ngày (duoc_ly_lam_sang, guardrails) và 80 mg/ngày (aho_corasick). "
                  "Đã lấy 40 (thận trọng hơn). Liều điều trị Zollinger-Ellison có thể cao hơn nhiều.",
    "clopidogrel": "Bảng cũ ghi 300 mg/ngày là liều TỐI ĐA; 300 mg là liều nạp, liều duy trì 75 mg/ngày. Cần tra.",
    "warfarin": "Bảng cũ ghi 10 mg/ngày là liều tối đa; warfarin chỉnh theo INR, không có trần cố định. "
                "Bảng cũ còn ghi sintrom là biệt dược của warfarin — sai (sintrom là acenocoumarol), đã tách.",
    "theophylline": "Bảng cũ ghi aminophylline là biệt dược của theophylline — đã tách thành hoạt chất riêng.",
    "co-amoxiclav": "Liều 3000 mg/ngày trong bảng cũ không rõ tính theo amoxicillin hay cả hai thành phần.",
    "digoxin": "0,25 mg/ngày là liều duy trì thường dùng, không phải trần tuyệt đối. Cần tra.",
}


def _khoa(t):
    t = t.strip().lower()
    return t[:-1] if len(t) > 5 and t.endswith("e") else t


def thu_thap():
    from src import cong_rui_ro, kho_khuon, kiem_duyet_bhyt_va_bo_sot as kd, thuc_the
    from src.aho_corasick_duoc_thu import CO_SO_DU_LIEU_DUOC_THU_2022
    from src.duoc_ly_lam_sang import LIEU_TOI_DA_NGAY

    muc = {}  # khoa hoat chat -> dict

    def lay(hc):
        k = _khoa(hc)
        if k not in muc:
            muc[k] = {"hoat_chat": hc.lower(), "ten_khac": [], "biet_duoc": [], "ma_atc": None, "nti": False,
                      "lieu_toi_da": {"nguoi_lon": None, "tre_em": None}, "mau_thuan": [], "can_tra": [],
                      "_nguon": []}
        return muc[k]

    def ten_ve(ten):
        """Ten bat ky -> muc dang co (theo hoat chat, ten khac hoac biet duoc)."""
        k = _khoa(ten)
        for m in muc.values():
            if k in {_khoa(x) for x in [m["hoat_chat"], *m["ten_khac"], *m["biet_duoc"]]}:
                return m
        return None

    for x in CO_SO_DU_LIEU_DUOC_THU_2022:
        m = lay(x.ten_hoat_chat)
        m["ma_atc"] = x.ma_atc
        bo = BO_KHOI_BIET_DUOC.get(x.ten_hoat_chat, set())
        m["biet_duoc"] += [b for b in x.ten_biet_duoc if b not in bo and _khoa(b) != _khoa(x.ten_hoat_chat)]
        if x.lieu_toi_da_24h_mg is not None:
            m["lieu_toi_da"]["nguoi_lon"] = {"gia_tri": x.lieu_toi_da_24h_mg, "don_vi": "mg/ngày"}
            m["_nguon"].append(N_AHO)
    for hc, ten in {**TEN_KHAC, **BIET_DUOC_THEM}.items():
        m = ten_ve(hc) or lay(hc)
        dich = "ten_khac" if hc in TEN_KHAC else "biet_duoc"
        m[dich] += [t for t in ten if t not in m[dich]]
    for ten, (gt, _dv) in LIEU_TOI_DA_NGAY.items():
        m = ten_ve(ten) or lay(ten)
        cu = m["lieu_toi_da"]["nguoi_lon"]
        if cu and cu["gia_tri"] != gt:
            m["mau_thuan"].append(f"liều tối đa người lớn: {cu['gia_tri']} (bảng aho_corasick) vs {gt} ({N_NGUOI_LON})")
            cu["gia_tri"] = min(cu["gia_tri"], gt)
        elif not cu:
            m["lieu_toi_da"]["nguoi_lon"] = {"gia_tri": gt, "don_vi": "mg/ngày"}
        if N_NGUOI_LON not in m["_nguon"]:
            m["_nguon"].append(N_NGUOI_LON)
    # guardrails.LIEU_TRAN: cung so voi bang tren tru "aspirin 3000", "salbutamol 16" (da co) — kiem tay 25/11.
    for ten, (lan, ngay, gc) in kd.LIEU_TRAN_NHI_KHOA_MG_KG_NGAY.items():
        hc = {"augmentin": "co-amoxiclav"}.get(ten, ten)
        m = ten_ve(hc) or lay(hc)
        m["lieu_toi_da"]["tre_em"] = {"gia_tri": ngay, "moi_lan": lan, "don_vi": "mg/kg/ngày", "ghi_chu": gc}
        if N_TRE_EM not in m["_nguon"]:
            m["_nguon"].append(N_TRE_EM)
    para = ten_ve("paracetamol")
    para["biet_duoc"] += [b for b in kd.BIET_DUOC_CHUA_PARACETAMOL if b != "paracetamol" and b not in para["biet_duoc"]]
    for ten in cong_rui_ro.THUOC_KHOANG_DIEU_TRI_HEP:
        m = ten_ve(ten)
        if m is None or (ten == "sintrom"):
            m = ten_ve("acenocoumarol") if ten == "sintrom" else lay(ten)
        m["nti"] = True
        if N_NTI not in m["_nguon"]:
            m["_nguon"].append(N_NTI)
    ten_cu = set(thuc_the.TU_DIEN_THUOC) | {"penicillin", "augmentin", "warfarin", "digoxin", "clopidogrel", "losartan",
                                            "allopurinol", "colchicin", "esomeprazol", "rosuvastatin", "medrol"}
    for ten in sorted(ten_cu):
        if ten_ve(ten) is None:
            lay(ten)["_nguon"].append(N_TEN)
    for b in kho_khuon.ds_khuon(True):
        van = " ".join([b.get("ke_hoach", "")] + list(b.get("bien_the_ke_hoach") or []))
        for w in re.findall(r"[A-Za-z][\w\-]+", van):
            w = w.lower()
            if len(w) >= 5 and w.isascii() and _HAU_TO.search(w) and w not in NHOM_KHONG_PHAI_THUOC \
                    and ten_ve(w) is None:
                lay(w)["_nguon"].append(N_KHUON)
    ra = []
    for m in sorted(muc.values(), key=lambda m: m["hoat_chat"]):
        if m["hoat_chat"] in CAN_TRA:
            m["can_tra"].append(CAN_TRA[m["hoat_chat"]])
        m["nguon"] = "Chép từ: " + "; ".join(dict.fromkeys(m.pop("_nguon"))) + ". CHƯA tra lại tài liệu gốc."
        m["da_duyet"] = False
        ra.append(m)
    return ra


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ghi-de", action="store_true")
    a = ap.parse_args(argv)
    if DICH.exists() and not a.ghi_de:
        sys.exit(f"{DICH} da co; cac mo-dun cu co the da doc tu no. Dung --ghi-de neu chac chan.")
    ra = thu_thap()
    DICH.write_text(json.dumps({"phien_ban": "2026-11-25", "ghi_chu": __doc__.splitlines()[0], "muc": ra},
                               ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Ghi {DICH}: {len(ra)} hoat chat, {sum(bool(m['lieu_toi_da']['nguoi_lon']) for m in ra)} co lieu nguoi lon, "
          f"{sum(bool(m['lieu_toi_da']['tre_em']) for m in ra)} co lieu tre em, {sum(m['nti'] for m in ra)} NTI, "
          f"{sum(bool(m['mau_thuan']) for m in ra)} mau thuan")


if __name__ == "__main__":
    main()
