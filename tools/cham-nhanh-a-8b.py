# -*- coding: utf-8 -*-
"""Cham nhanh A va A+ (chay tren HoaiDuc dem 22–23/09/2026) cung B, C, C + cong bang DIEM
QUY GAN tren van ban ho so — chi so chinh cua H1 trong `docs/dang-ky-truoc.md` — tren
bon bo thu thach, dap an the he 8b. Khong chay lai mo hinh nao.

VI SAO CAN TEP NAY (24/09/2026). Nhanh A va A+ da chay xong tren HoaiDuc tu dem 22/09
(`C:\\Users\\nguoidung\\meditrace\\chuoi_hoaiduc.log`), nhung ket qua chua duoc chep ve va chua cham;
bao cao mau van ghi "chua chay". Tep dau ra luu kem ban benh an tham chieu (`tham_chieu`)
luc chay — la ban the he 8. Cham o day THAY `tham_chieu` bang truong `output` cua bo 8b
cho MOI nhanh, de A va C + cong cung so voi mot ban tham chieu.

Khoang tin cay 95 %: bootstrap theo cum KHUON BENH (truong `benh`), hat 2026, 2000 lan —
dung quy uoc cua dang ky truoc. Chenh lech duong nghia la C + cong CAO hon A.

    python tools/cham-nhanh-a-8b.py
"""
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC))
from src import cham_diem, thuoc_do_quy_gan as tdq  # noqa: E402

TAP = ["thach_thuc_doi_chu_the_phat_trien", "thach_thuc_dinh_chinh_phat_trien",
       "thach_thuc_nhieu_asr_phat_trien", "thach_thuc_phuong_ngu_phat_trien"]
TEN_BO = {"thach_thuc_doi_chu_the_phat_trien": "Đổi chủ thể", "thach_thuc_dinh_chinh_phat_trien": "Đính chính",
          "thach_thuc_nhieu_asr_phat_trien": "Nhiễu ASR", "thach_thuc_phuong_ngu_phat_trien": "Phương ngữ"}
NGUON = {"A": "kaggle-ra/the-he-8-nhanh-a-hoaiduc", "A_cong": "kaggle-ra/the-he-8-nhanh-a-hoaiduc",
         "B": "kaggle-ra/the-he-8", "C": "kaggle-ra/the-he-8", "C_khoa": "kaggle-ra/the-he-8"}
TEN_NHANH = {"A": "A · viết thẳng", "A_cong": "A+ · viết thẳng rồi tự soát", "B": "B", "C": "C",
             "C_khoa": "C + cổng"}
CHI_SO = ("f1_quy_gan", "dung_quy_gan", "bo_sot", "them_moi", "so_sai_chu_the")
HAT, LAN = 2026, 2000


def _nap(p):
    return [json.loads(x) for x in Path(p).read_text(encoding="utf-8").split("\n") if x.strip()]


def diem_ca(r, tham_chieu):
    d = tdq.diem(r.get("du_doan") or "", tham_chieu)
    d["final_cuoc_thi"] = cham_diem.diem_cuoi(r.get("du_doan") or "", tham_chieu)["final"]
    return d


def ci(cap, ham, hat=HAT, lan=LAN):
    """cap: {khuon: [gia tri moi ca]} -> (trung binh, thap, cao) cua `ham` qua bootstrap cum."""
    khuon = sorted(cap)
    rng = random.Random(hat)
    mau = []
    for _ in range(lan):
        chon = [rng.choice(khuon) for _ in khuon]
        mau.append(ham([v for k in chon for v in cap[k]]))
    mau.sort()
    return ham([v for k in khuon for v in cap[k]]), mau[int(0.025 * lan)], mau[int(0.975 * lan) - 1]


def tb(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def so(x, cs=4):
    return f"{x:.{cs}f}".replace(".", ",").replace("-", "−")


def pt(x):
    return f"{100 * x:.1f}".replace(".", ",") + " %"


def _chuan(s):
    return " ".join((s or "").split())


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ra, dong = {}, []
    tong_hieu = defaultdict(list)
    for tap in TAP:
        goc = {c["id"]: c for c in _nap(GOC / "data" / f"{tap}.jsonl")}
        theo = {}
        for n, tm in NGUON.items():
            ds = _nap(GOC / tm / f"ra_{n}_{tap}.jsonl")
            lech = [r["id"] for r in ds if "input" in r and r["input"] != goc[r["id"]]["input"]]
            assert not lech, (tap, n, lech[:3])
            theo[n] = {r["id"]: diem_ca(r, goc[r["id"]]["output"]) for r in ds}
        chung = sorted(set.intersection(*(set(v) for v in theo.values())))
        # A co CHEP KHIT ban mau cua bo sinh khong; va C + cong chi tinh than ban nhap.
        ra_a = {r["id"]: r for r in _nap(GOC / NGUON["A"] / f"ra_A_{tap}.jsonl")}
        khit = sum(_chuan(ra_a[i]["du_doan"]) == _chuan(goc[i]["output"]) for i in chung)
        ra_k = {r["id"]: r for r in _nap(GOC / NGUON["C_khoa"] / f"ra_C_khoa_{tap}.jsonl")}
        than = tb([tdq.diem(ra_k[i].get("du_doan_khong_muc_phu") or ra_k[i]["du_doan"],
                            goc[i]["output"])["f1_quy_gan"] for i in chung])
        bang = {}
        for n, v in theo.items():
            bang[n] = {k: round(tb([v[i][k] for i in chung]), 4) for k in CHI_SO + ("final_cuoc_thi",)}
        cap = defaultdict(list)
        for i in chung:
            hieu = theo["C_khoa"][i]["f1_quy_gan"] - theo["A"][i]["f1_quy_gan"]
            cap[goc[i]["benh"]].append(hieu)
            tong_hieu[goc[i]["benh"] + "|" + tap].append(hieu)
        g, lo, hi = ci(cap, tb)
        ra[tap] = {"so_ca": len(chung), "so_khuon": len(cap), "bang": bang,
                   "A_trung_khit_ban_mau": khit, "C_khoa_f1_quy_gan_chi_than": round(than, 4),
                   "hieu_C_khoa_tru_A_f1_quy_gan": {"gia_tri": round(g, 4), "thap": round(lo, 4),
                                                   "cao": round(hi, 4)}}
        dong.append((tap, len(chung), len(cap), bang, (g, lo, hi), khit, than))

    md = ["# Nhánh A và A+ so với B, C, C + cổng — điểm quy gán, đáp án 8b", "",
          "Sinh bằng `python tools/cham-nhanh-a-8b.py`. Đừng sửa tay. Nhánh A, A+ chạy trên HoaiĐức "
          "(RTX 3060, nf4, tính bf16) đêm 22–23/09/2026 bằng adapter nhánh A thế hệ 8 (huấn luyện fp16 "
          "trên Kaggle T4); B, C, C + cổng là bản chạy Kaggle thế hệ 8. Mọi nhánh cùng lời thoại và "
          "được so với **cùng một bản tham chiếu** (bản bệnh án mẫu của bộ 8b). Tập kiểm tra cuối "
          "không dùng.", "",
          "`f1_quy_gan` là chỉ số chính của H1 trong đăng ký trước. Đây là số trên **tập phát triển** "
          "(bốn bộ thử thách), chỉ để mô tả, không phải kết quả của H1.", ""]
    for tap, n, k, bang, (g, lo, hi), khit, than in dong:
        md += [f"## {TEN_BO[tap]} — {n} ca, {k} khuôn bệnh", "",
               "| Nhánh | F₁ quy gán | Đúng người trên mệnh đề khớp nội dung | Bỏ sót | Thêm mới | "
               "Số mệnh đề sai người mỗi hồ sơ | Điểm cuộc thi |", "|---|---|---|---|---|---|---|"]
        for nh, t in TEN_NHANH.items():
            b = bang[nh]
            md.append(f"| {t} | {so(b['f1_quy_gan'])} | {pt(b['dung_quy_gan'])} | {pt(b['bo_sot'])} | "
                      f"{pt(b['them_moi'])} | {so(b['so_sai_chu_the'], 2)} | {so(b['final_cuoc_thi'])} |")
        md += ["", f"Chênh lệch F₁ quy gán, C + cổng − A: **{so(g)}** (khoảng tin cậy 95 %: "
                   f"{so(lo)} đến {so(hi)}; bootstrap theo khuôn bệnh, hạt {HAT}).", "",
               f"Bản nháp của A **trùng khít từng ký tự** bản bệnh án mẫu của bộ sinh ở **{khit}/{n} ca**. "
               f"Chỉ tính thân bản nháp (bỏ mục “Cần xác nhận”), F₁ quy gán của C + cổng là {so(than)}.", ""]
    (GOC / "docs" / "ket-qua" / "nhanh-a-quy-gan-8b.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (GOC / "docs" / "ket-qua" / "nhanh-a-quy-gan-8b.json").write_text(
        json.dumps(ra, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
