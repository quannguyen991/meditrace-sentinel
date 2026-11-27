# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Bộ chấm]
Làm gì   : In ra từng phát biểu cùng nguyên văn lượt dẫn chứng để người chấm tay trường chủ
           thể, vì bộ đếm tự động sẽ chấm nhầm người nhà.
Vào → Ra : tệp kết quả bake-off trong docs/ket-qua (--tep) → phiếu chấm tay in ra màn hình
Đọc từ   : in_phieu() in từng phát biểu kèm lượt dẫn; main() đọc tệp kết quả
Mục lục (các hàm/lớp chính):
  in_phieu()  In phiếu chấm tay trường chủ thể
  main()      Chạy dòng lệnh in phiếu từ tệp kết quả
Gọi tới  : bo_du_lieu/nap_du_lieu, he_thong/duong_dan
Tên cũ   : cham_chu_the.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
In phiếu chấm tay cho trường `chu_the`.

Vì sao không đếm tự động: bộ đếm chỉ kiểm `chu_the` có phải tên một vai người
nói không. Nhưng "người nhà mang theo bảng ghi chép ăn uống" thì chủ thể ĐÚNG
là người nhà. Bộ đếm sẽ tính nhầm đó là lỗi.

Script này in ra, với mỗi phát biểu:
    - chu_the mô hình gán
    - nội dung
    - NGUYÊN VĂN các lượt thoại được dẫn làm bằng chứng

Đọc bảng đó rồi tự chấm. Ghi kết quả vào docs/ket-qua/cham-chu-the.json theo dạng
    {"<tên mô hình>": {"dung": <so>, "sai": <so>, "ghi_chu": "..."}}

    python -m src.do_luong.cham_chu_the --tep bakeoff-Qwen3-4B.json
"""
import argparse
import io
import json
import sys

VAI = {"người nhà", "bác sĩ", "bệnh nhân", "điều dưỡng"}


# ═══ in_phieu() — In phiếu chấm tay trường chủ thể ════════════════════════════════════
# Mỗi mệnh đề in kèm lượt nói dẫn chứng; dấu ? khi chủ thể là tên vai người nói, báo
# lượt không tồn tại.
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


# ═══ main() — Chạy dòng lệnh in phiếu từ tệp kết quả ══════════════════════════════════
# Đọc tệp kết quả cùng tập phát triển, in phiếu và nhắc dấu ? chưa chắc là sai.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tep", required=True, help="ten tep trong docs/ket-qua/")
    ap.add_argument("--gioi-han", type=int, default=None)
    a = ap.parse_args()

    from src.bo_du_lieu import nap_du_lieu as du_lieu
    from src.he_thong import duong_dan as duong_dan

    mau = {m["id"]: m for m in
           du_lieu.nap_mau(duong_dan.THU_MUC_DU_LIEU / "phat_trien.jsonl")}
    in_phieu(duong_dan.THU_MUC_KET_QUA / a.tep, mau, a.gioi_han)
    print(f"\n{'='*76}")
    print("Dau '?' = chu_the la ten mot vai nguoi noi. KHONG chac la sai —")
    print("nguoi nha ke benh CUA CHINH HO thi chu the dung la nguoi nha.")
    print("Doc bang chung roi tu cham.")


if __name__ == "__main__":
    main()
