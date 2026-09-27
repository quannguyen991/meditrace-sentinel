# -*- coding: utf-8 -*-
"""Quet nguong ghep cua bo cham, de biet ket luan co phu thuoc nguong khong (20/09/2026).

VI SAO CAN. Bo cham ghep menh de khi do giong tu vung >= 0,6. Ngay 20/09/2026 do duoc:
voi doi chung gpt-6-astra, 258/428 (60%) menh de bi tinh loi co do giong 0,4–0,6 —
nam ngay DUOI nguong. Nghia la mot mo hinh dien dat khac se bi phat nang du noi dung
dung. Mo hinh chay tai cho duoc tinh chinh tren chinh loi dien dat cua bo sinh nen
khong bi.

=> Moi ket luan so sanh giua hai mo hinh phai kem phep quet nguong. Neu ket luan dao
chieu khi doi nguong thi do khong phai ket luan, do la tao tac cua bo cham.

Chi so quet la SAI CHU THE tren cac menh de GHEP DUOC — chi so trong tam cua du an.

    python tools/quet-nguong-ghep.py --nhanh B \
        --nguon kaggle-ra/the-he-8="Qwen3-4B tinh chinh" \
        --nguon kaggle-ra/nen-8b="Qwen3-8B nen" \
        --tap thach_thuc_doi_chu_the_phat_trien
"""
import argparse
import importlib
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import du_lieu  # noqa: E402

NGUONG = (0.4, 0.5, 0.6, 0.7, 0.8)


def do_mot(thu_muc: Path, tap: str, nhanh: str, nguong: float):
    """-> (so menh de sai chu the, so menh de ghep duoc) o nguong da cho."""
    from src import do_trich
    do_trich.NGUONG_GHEP = nguong
    import src.cham_he_thong as ch
    importlib.reload(ch)
    ch.NGUONG_GHEP = nguong

    goc = {c["id"]: c for c in du_lieu.nap_mau(thu_muc / f"{tap}.jsonl")}
    kq = {r["id"]: r for r in du_lieu.nap_mau(thu_muc / f"ra_{nhanh}_{tap}.jsonl")}
    sai = ghep = 0
    for i, r in kq.items():
        loi, _ = ch.loi_phat_bieu(goc[i], r["phat_bieu"])
        for p in r["phat_bieu"]:
            ma = loi.get(p["id"], ([], None))[0] or []
            if "khong_can_cu" in ma or "trung_lap" in ma:
                continue          # khong ghep duoc -> khong tinh vao mau so
            ghep += 1
            sai += "sai_chu_the" in ma
    return sai, ghep


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace", line_buffering=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--nguon", action="append", required=True,
                    metavar="THU_MUC=NHAN", help="lap lai co nay cho tung mo hinh")
    ap.add_argument("--tap", nargs="+", required=True)
    ap.add_argument("--nhanh", default="B")
    a = ap.parse_args()

    nguon = []
    for x in a.nguon:
        d, _, nhan = x.partition("=")
        nguon.append((Path(d), nhan or d))

    for tap in a.tap:
        print(f"\n### {tap} — nhánh {a.nhanh}\n")
        print("| Ngưỡng ghép | " + " | ".join(n for _, n in nguon) + " |")
        print("|---|" + "---|" * len(nguon))
        dao = []
        for ng in NGUONG:
            o, ty = [], []
            for d, _ in nguon:
                sai, ghep = do_mot(d, tap, a.nhanh, ng)
                o.append("%.1f %% (%d/%d)" % (sai / ghep * 100, sai, ghep) if ghep else "—")
                ty.append(sai / ghep if ghep else float("nan"))
            print(f"| {ng:.1f} | " + " | ".join(o) + " |")
            dao.append(ty)
        # Ket luan co dao chieu khong: thu tu xep hang co doi o nguong nao khong
        hang = [tuple(sorted(range(len(t)), key=lambda i: t[i])) for t in dao]
        print("\n**Thứ tự xếp hạng " +
              ("KHÔNG đổi" if len(set(hang)) == 1 else "CÓ ĐỔI") +
              " qua các ngưỡng.**" +
              ("" if len(set(hang)) == 1 else " Kết luận phụ thuộc ngưỡng — không dùng được."))


if __name__ == "__main__":
    main()
