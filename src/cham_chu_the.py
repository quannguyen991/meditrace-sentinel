# -*- coding: utf-8 -*-
"""In phieu cham tay cho truong `chu_the`.

Vi sao khong dem tu dong: bo dem chi kiem `chu_the` co phai ten mot vai nguoi
noi khong. Nhung "nguoi nha mang theo bang ghi chep an uong" thi chu the DUNG
la nguoi nha. Bo dem se tinh nham do la loi.

Script nay in ra, voi moi phat bieu:
    - chu_the mo hinh gan
    - noi dung
    - NGUYEN VAN cac luot thoai duoc dan lam bang chung

Doc bang do roi tu cham. Ghi ket qua vao docs/ket-qua/cham-chu-the.json theo dang
    {"<ten mo hinh>": {"dung": <so>, "sai": <so>, "ghi_chu": "..."}}

    python -m src.cham_chu_the --tep bakeoff-Qwen3-4B.json
"""
import argparse
import io
import json
import sys

VAI = {"người nhà", "bác sĩ", "bệnh nhân", "điều dưỡng"}


def in_phieu(duong_dan_kq, mau_theo_id, gioi_han=None):
    kq = json.loads(open(duong_dan_kq, encoding="utf-8").read())
    stt = 0
    for k in kq:
        ps = k["phat_bieu"] or []
        if not ps:
            continue
        goc = mau_theo_id.get(k["id"])
        luot = [d for d in goc["input"].split("\n") if d.strip()] if goc else []
        print(f"\n{'='*76}\n[{k['id']}]")
        for p in ps:
            stt += 1
            if gioi_han and stt > gioi_han:
                return
            ct = str(p.get("chu_the", ""))
            co_the_sai = ct.strip().lower() in VAI
            dau = "  ?" if co_the_sai else "   "
            print(f"{dau} #{stt:<3} chu_the={ct:12} | {str(p.get('noi_dung'))[:52]}")
            for n in p.get("luot_thoai", []):
                if 1 <= n <= len(luot):
                    print(f"        luot {n:2d}: {luot[n-1][:90]}")
                else:
                    print(f"        luot {n:2d}: *** KHONG TON TAI ***")


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tep", required=True, help="ten tep trong docs/ket-qua/")
    ap.add_argument("--gioi-han", type=int, default=None)
    a = ap.parse_args()

    from src import du_lieu, duong_dan

    mau = {m["id"]: m for m in
           du_lieu.nap_mau(duong_dan.THU_MUC_DU_LIEU / "phat_trien.jsonl")}
    in_phieu(duong_dan.THU_MUC_KET_QUA / a.tep, mau, a.gioi_han)
    print(f"\n{'='*76}")
    print("Dau '?' = chu_the la ten mot vai nguoi noi. KHONG chac la sai —")
    print("nguoi nha ke benh CUA CHINH HO thi chu the dung la nguoi nha.")
    print("Doc bang chung roi tu cham.")


if __name__ == "__main__":
    main()
