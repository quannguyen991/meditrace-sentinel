# -*- coding: utf-8 -*-
"""Đo (CPU, không gọi mô hình) kiểm `noi_dung` so với câu trích của chính nó.

Nguyên mẫu, KHÔNG nối vào đường ống hay Chính sách D. Trên 4 bộ phát triển:
  (a) trong mệnh đề thân hồ sơ mà bộ chấm `cham_he_thong.loi_phat_bieu` đánh là sai/không ghép
      được với đáp án, kiểm cờ bao nhiêu;
  (b) trong mệnh đề ghép đúng (không lỗi nào), kiểm cờ bao nhiêu (cảnh báo giả).

  python tools/do_noi_dung_trich.py --ra docs/ket-qua/noi-dung-vs-cau-trich.md
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.do_luong.cham_he_thong import LOI, _than, loi_phat_bieu  # noqa: E402
from src.duong_ong.b4_kiem_noi_dung_trich import kiem_noi_dung_theo_trich  # noqa: E402
from tools.do_ve_chua_phu import BO, doc, pt  # noqa: E402

GOC = Path(__file__).resolve().parent.parent
MA = ("tu_khong_co_trong_trich", "chep_loi_asr", "bo_mat_bo_nghia", "nhan_khac_trich")


def do_bo(ten: str) -> dict:
    vang = doc(GOC / f"data/thach_thuc/thach_thuc_{ten}_phat_trien.jsonl")
    ra = doc(GOC / f"data/thach_thuc/ra_C_khoa_thach_thuc_{ten}_phat_trien.jsonl")
    k = {n: Counter() for n in ("khong_ghep", "ghep_loi", "dung")}
    mau = {"khong_ghep": [], "dung": []}
    bo_qua = 0
    for i in sorted(set(vang) & set(ra)):
        ca, r = vang[i], ra[i]
        ps = r.get("phat_bieu") or []
        than = {p["id"] for p in _than(r)}
        loi, _ = loi_phat_bieu(ca, ps, than)
        theo_id = {p["id"]: p for p in ps}
        for pid, (ds, _loai) in loi.items():
            p = theo_id[pid]
            if "trung_lap" in ds:
                continue
            if "khong_can_cu" in ds:
                nhom = "khong_ghep"
            elif set(ds) & set(LOI):
                nhom = "ghep_loi"
            else:
                nhom = "dung"
            trich = p.get("trich_dan") or []
            if not trich:
                bo_qua += 1
                continue
            ma = kiem_noi_dung_theo_trich(p.get("noi_dung") or "", trich)
            k[nhom]["n"] += 1
            k[nhom]["co_co"] += bool(ma)
            for m in ma:
                k[nhom][m] += 1
            if ma and nhom in mau and len(mau[nhom]) < 400:
                mau[nhom].append((p.get("noi_dung"), trich, ma))
    return {"k": k, "bo_qua": bo_qua, "mau": mau}


def in_bang(kq: dict) -> str:
    tong = {n: Counter() for n in ("khong_ghep", "ghep_loi", "dung")}
    for r in kq.values():
        for n in tong:
            tong[n].update(r["k"][n])
    hang = {**kq, "**Tổng**": {"k": tong, "bo_qua": sum(r["bo_qua"] for r in kq.values())}}
    d = ["# Kiểm nội dung mệnh đề với câu trích của nó (đo khô, CPU)", "",
         "Chạy: `python tools/do_noi_dung_trich.py --ra docs/ket-qua/noi-dung-vs-cau-trich.md`. Nguồn: "
         "`data/thach_thuc/ra_C_khoa_*_phat_trien.jsonl` + đáp án `thach_thuc_*_phat_trien.jsonl`, chấm bằng "
         "`cham_he_thong.loi_phat_bieu` (mệnh đề vào thân hồ sơ, bỏ bản lặp). Module: "
         "`src/duong_ong/b4_kiem_noi_dung_trich.py`, **chưa nối vào đường ống**, không đổi số đã báo.", "",
         "Ba nhóm mệnh đề (theo bộ chấm): **không ghép** = không ứng với đáp án nào (nội dung lệch, hay thông tin "
         "bịa); **ghép nhưng lỗi** = ghép được nhưng sai chủ thể/mức/thuốc/thời gian; **đúng** = ghép được, không lỗi.",
         "", "## (a)/(b) Tỉ lệ cờ theo nhóm", "",
         "| Bộ | Không ghép: n | cờ | Ghép nhưng lỗi: n | cờ | Đúng: n | cờ (báo giả) |",
         "|---|---:|---:|---:|---:|---:|---:|"]
    for ten, r in hang.items():
        k = r["k"]
        d.append(f"| {ten} | {k['khong_ghep']['n']} | {k['khong_ghep']['co_co']} "
                 f"({pt(k['khong_ghep']['co_co'], k['khong_ghep']['n'])}) | {k['ghep_loi']['n']} | "
                 f"{k['ghep_loi']['co_co']} ({pt(k['ghep_loi']['co_co'], k['ghep_loi']['n'])}) | "
                 f"{k['dung']['n']} | {k['dung']['co_co']} ({pt(k['dung']['co_co'], k['dung']['n'])}) |")
    d += ["", "## Theo mã lý do (số mệnh đề mang mã; một mệnh đề có thể mang nhiều mã)", "",
          "| Bộ | Mã | Không ghép | Ghép nhưng lỗi | Đúng (báo giả) |", "|---|---|---:|---:|---:|"]
    for ten, r in hang.items():
        k = r["k"]
        for m in MA:
            d.append(f"| {ten} | `{m}` | {k['khong_ghep'][m]} | {k['ghep_loi'][m]} | {k['dung'][m]} |")
    t = tong
    n_sai, c_sai = t["khong_ghep"]["n"], t["khong_ghep"]["co_co"]
    n_dung, c_dung = t["dung"]["n"], t["dung"]["co_co"]
    n_gl, c_gl = t["ghep_loi"]["n"], t["ghep_loi"]["co_co"]
    d += ["", f"Mệnh đề không có câu trích bị bỏ khỏi bảng: {hang['**Tổng**']['bo_qua']}.", "",
          "## Đọc số", "",
          f"Kiểm này cờ {c_sai}/{n_sai} mệnh đề bộ chấm không ghép được với đáp án ({pt(c_sai, n_sai)}), nhiều nhất "
          "ở bộ nhiễu ASR, nơi lỗi chủ yếu là chép chữ không dấu và đổi chữ. "
          f"Nó cũng cờ {c_gl}/{n_gl} mệnh đề ghép được nhưng sai ở trục khác ({pt(c_gl, n_gl)}), đó là lỗi nó không "
          "nhắm tới nên chỉ coi là trùng hợp. "
          f"Cái giá là {c_dung}/{n_dung} mệnh đề đúng cũng bị cờ ({pt(c_dung, n_dung)}), phần lớn do mô hình diễn đạt "
          "lại hợp lệ (\"chán ăn\" cho \"không chịu ăn\"), nội dung ngắn hơn câu trích có kèm liều thuốc, hoặc chữ "
          "không dấu vốn là từ đúng. "
          "Mức báo giả này quá cao để chặn hay sửa tự động, chỉ hợp để xếp thứ tự cho bác sĩ xem lại. "
          "Giới hạn: chỉ 4 bộ phát triển do máy sinh (đáp án và nhiễu ASR đều tổng hợp), ngưỡng 50% và danh sách chữ "
          "miễn trừ chọn tay, từ điển chữ không dấu lập từ ba bộ sạch của cùng bộ sinh nên số ở bộ nhiễu ASR có phần "
          "lạc quan, và chưa nối vào đường ống nên chưa đổi số nào đã báo."]
    return "\n".join(d) + "\n"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ra", default=None)
    ap.add_argument("--mau", type=int, default=0, help="in N mẫu báo giả / bắt được mỗi bộ")
    a = ap.parse_args()
    kq = {ten: do_bo(ten) for ten in BO}
    van = in_bang(kq)
    if a.ra:
        Path(a.ra).write_text(van, encoding="utf-8")
    print(van)
    if a.mau:
        for ten, r in kq.items():
            for nhom in ("dung", "khong_ghep"):
                print(f"--- {ten} / {nhom}")
                for nd, tr, ma in r["mau"][nhom][:a.mau]:
                    print(ma, "|", nd, "|", tr)


if __name__ == "__main__":
    main()
