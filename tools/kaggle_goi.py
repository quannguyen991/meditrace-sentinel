# -*- coding: utf-8 -*-
"""Dong goi mot bo tai len Kaggle: ma nguon, du lieu can thiet, adapter, kich ban.

    python tools/kaggle_goi.py thach_thuc_phuong_ngu_phat_trien thach_thuc_nhieu_asr_phat_trien

Tao ra thu muc `goi-kaggle/` gom:
    src/            toan bo ma nguon
    tools/          kiem-the-he.py, don-dem-trich.py, kaggle_chay.py
    data/           cac tep bo du lieu can + van tay cua chung
    models/nen-qwen3-4b-trich/best_checkpoint/   adapter khau trich
    dataset-metadata.json                        de `kaggle datasets create/version`

VI SAO KHONG DUA CA THU MUC data/: no nang hang GB (bo hoi thoai goc, tep dem cu,
ket qua cac lan chay). Chi dua dung tep can, va van tay di kem — thieu van tay thi
`kiem-the-he.py` khong chay duoc, ma do la hang rao duy nhat chan viec chay nham bo.

MO HINH NEN khong nam trong goi: notebook tai thang tu Hugging Face (8 GB), nhanh
hon tai len roi tai xuong.
"""
import json
import shutil
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
RA = GOC / "goi-kaggle"
# The he bo du lieu: doi bang --the-he. Moi the he mot dataset rieng tren Kaggle,
# vi ID ca trung nhau giua cac the he — dung chung mot dataset la lan bo.
THE_HE_MAC_DINH = "8"


def main() -> None:
    doi = sys.argv[1:]
    the_he = THE_HE_MAC_DINH
    if "--the-he" in doi:
        i = doi.index("--the-he")
        the_he = doi[i + 1]
        doi = doi[:i] + doi[i + 2:]
    ten_bo = f"meditrace-the-he-{the_he}"
    cac_tap = doi
    if not cac_tap:
        raise SystemExit("dung: python tools/kaggle_goi.py <tap> [<tap> ...]")
    if RA.exists():
        shutil.rmtree(RA)
    (RA / "data").mkdir(parents=True)
    (RA / "tools").mkdir()

    shutil.copytree(GOC / "src", RA / "src",
                    ignore=shutil.ignore_patterns("__pycache__"))
    for t in ("kiem-the-he.py", "don-dem-trich.py", "kaggle_chay.py"):
        shutil.copy2(GOC / "tools" / t, RA / "tools" / t)
    # Kaggle chay kich ban o thu muc goc cua dataset, nen de mot ban o day nua.
    shutil.copy2(GOC / "tools" / "kaggle_chay.py", RA / "kaggle_chay.py")

    can = list(cac_tap) + ["viet_train"]        # viet_train cho van tay doi chieu
    for tap in can:
        for duoi in (".jsonl", ".van_tay.json"):
            tep = GOC / "data" / f"{tap}{duoi}"
            if not tep.exists():
                raise SystemExit(f"thieu {tep}")
            shutil.copy2(tep, RA / "data" / tep.name)

    nguon_adapter = GOC / "models" / "nen-qwen3-4b-trich" / "best_checkpoint"
    if not nguon_adapter.is_dir():
        raise SystemExit(
            f"khong thay {nguon_adapter} — keo ve tu HoaiDuc truoc:\n"
            "  scp -r nguoidung@100.64.0.7:'D:/meditrace-core/models/"
            "nen-qwen3-4b-trich/best_checkpoint' models/nen-qwen3-4b-trich/")
    shutil.copytree(nguon_adapter, RA / "models" / "nen-qwen3-4b-trich" / "best_checkpoint")

    (RA / "dataset-metadata.json").write_text(json.dumps(
        {"title": f"MediTrace the he {the_he}",
         "id": f"PLACEHOLDER/{ten_bo}",
         "licenses": [{"name": "CC0-1.0"}]}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    tong = sum(f.stat().st_size for f in RA.rglob("*") if f.is_file())
    print(f"goi o {RA}: {tong / 1024 / 1024:,.0f} MB")
    print("cac tap:", ", ".join(cac_tap))
    print("\nBuoc tiep:")
    print("  1. sua 'PLACEHOLDER' trong dataset-metadata.json thanh ten tai khoan Kaggle")
    print(f"  2. kaggle datasets create -p {RA} --dir-mode zip")
    print("  3. tao kernel tro toi dataset do, chay:")
    print("     python kaggle_chay.py " + " ".join(cac_tap))


if __name__ == "__main__":
    main()
