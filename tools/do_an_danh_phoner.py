# -*- coding: utf-8 -*-
"""Đo bộ che định danh Python (ClinicalDeidentifier, cổng ra máy xa) trên PhoNER_COVID19.

Cùng định nghĩa với web/may-chu/do-an-danh-phoner.ts (bộ che TypeScript):
  - Nhãn vàng: NAME và PATIENT_ID (gộp B-/I-), văn bản nhãn = các âm tiết nối bằng dấu cách.
  - Câu = các âm tiết nối bằng dấu cách.
  - bao_ve(nhãn) = văn bản nhãn không còn trong văn bản đã che (so khớp có ranh giới: nhãn bắt đầu/kết
    thúc bằng chữ số thì không dính chữ số khác; bằng chữ cái thì không dính chữ cái/chữ số khác)
    HOẶC câu bị từ chối gửi (kiem_tra_con_sot khác rỗng).
  - Che nhầm: 300 câu hỏi đầu của ViMedAQA test_sample_500; một câu là "che nhầm" khi văn bản sau
    che khác văn bản gốc HOẶC câu bị từ chối.

Chạy: python -m tools.do_an_danh_phoner --tap dev|test [--toi-da N, 0 = cả tập] [--ra tep.json]
"""
import argparse
import json
import re
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
if str(GOC) not in sys.path:
    sys.path.insert(0, str(GOC))

from src.he_thong.khu_dinh_danh import ClinicalDeidentifier  # noqa: E402

NHAN = ("NAME", "PATIENT_ID")
SO_CAU_HOI_CHE_NHAM = 300


def doc_phoner(tap: str, toi_da: int):
    tep = GOC / "data" / "ngoai" / "PhoNER_COVID19" / "data" / "syllable" / f"{tap}_syllable.json"
    ra = []
    with open(tep, encoding="utf-8") as f:
        for dong in f:
            if not dong.strip():
                continue
            r = json.loads(dong)
            w, t = r["words"], r["tags"]
            nhan, i = [], 0
            while i < len(t):
                if t[i].startswith("B-") and t[i][2:] in NHAN:
                    loai, j = t[i][2:], i + 1
                    while j < len(t) and t[j] == "I-" + loai:
                        j += 1
                    nhan.append((loai, " ".join(w[i:j])))
                    i = j
                else:
                    i += 1
            ra.append((" ".join(w), nhan))
            if toi_da and len(ra) >= toi_da:
                break
    return ra


def con_trong(nhan: str, van: str) -> bool:
    trai = r"(?<![\d_])" if nhan[:1].isdigit() else (r"(?<!\w)" if nhan[:1].isalpha() else "")
    phai = r"(?![\d_])" if nhan[-1:].isdigit() else (r"(?!\w)" if nhan[-1:].isalpha() else "")
    return re.search(trai + re.escape(nhan) + phai, van) is not None


def che(van: str):
    da_che = ClinicalDeidentifier.an_danh_van_ban(van).van_ban_da_an_danh
    tu_choi = bool(ClinicalDeidentifier.kiem_tra_con_sot(da_che))
    return da_che, tu_choi


def do(tap: str, toi_da: int, chi_tiet: bool = False) -> dict:
    cau = doc_phoner(tap, toi_da)
    so_nhan = bao_ve = so_cau_tu_choi = 0
    theo_loai = {k: [0, 0] for k in NHAN}
    lot = []
    for van, nhan in cau:
        da_che, tu_choi = che(van)
        so_cau_tu_choi += tu_choi
        for loai, chu in nhan:
            so_nhan += 1
            theo_loai[loai][0] += 1
            ok = tu_choi or not con_trong(chu, da_che)
            bao_ve += ok
            theo_loai[loai][1] += ok
            if not ok and chi_tiet:
                lot.append({"loai": loai, "nhan": chu, "da_che": da_che})
    cau_hoi = json.loads((GOC / "data" / "ngoai" / "ViMedAQA" / "test_sample_500.json").read_text(encoding="utf-8"))
    cau_hoi = [c["question"] for c in cau_hoi[:SO_CAU_HOI_CHE_NHAM]]
    che_nham, vi_du_che_nham = 0, []
    for q in cau_hoi:
        da_che, tu_choi = che(q)
        if tu_choi or da_che != q:
            che_nham += 1
            if chi_tiet:
                vi_du_che_nham.append({"goc": q, "da_che": da_che, "tu_choi": tu_choi})
    kq = {
        "bo_che": "python_ClinicalDeidentifier",
        "tap": tap,
        "so_cau": len(cau),
        "so_nhan": so_nhan,
        "bao_ve": bao_ve,
        "ty_le_bao_ve": round(bao_ve / so_nhan, 4) if so_nhan else None,
        "theo_loai": {k: {"so_nhan": v[0], "bao_ve": v[1]} for k, v in theo_loai.items()},
        "so_cau_tu_choi": so_cau_tu_choi,
        "so_cau_hoi_vimedaqa": len(cau_hoi),
        "che_nham": che_nham,
        "ty_le_che_nham": round(che_nham / len(cau_hoi), 4) if cau_hoi else None,
    }
    if chi_tiet:
        kq["lot"] = lot
        kq["vi_du_che_nham"] = vi_du_che_nham
    return kq


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", choices=("dev", "test"), required=True)
    ap.add_argument("--toi-da", type=int, default=0, help="0 = cả tập")
    ap.add_argument("--ra", help="ghi JSON kết quả vào tệp này")
    ap.add_argument("--chi-tiet", action="store_true", help="kèm danh sách nhãn lọt và câu che nhầm")
    a = ap.parse_args()
    kq = do(a.tap, a.toi_da, a.chi_tiet)
    tom = {k: v for k, v in kq.items() if k not in ("lot", "vi_du_che_nham")}
    print(json.dumps(tom, ensure_ascii=False))
    if a.ra:
        Path(a.ra).write_text(json.dumps(kq, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
