# -*- coding: utf-8 -*-
"""Tron cap ban nhap de bac si cham MU.

Bac si doc hai ban nhap cua cung mot hoi thoai va chon. Neu biet ban nao la
cua du an thi phep cham do khong con gia tri — nen o day:

  - moi cap duoc gan nhan "A" / "B" theo mot dong xu co seed co dinh
  - khoa giai ma luu RIENG, khong nam trong phieu cham
  - phieu cham khong chua ten nhanh, khong chua thu tu on dinh

Chi tiet de bo sot nhung lam hong ca phep do: neu nhanh nao cung luon o ben
trai thi bac si hoc duoc quy luat sau vai cap. `xao` dung mot dong xu rieng
cho TUNG cap.

Mot chi tiet nua: hai ban giong het nhau thi cap do khong do duoc gi, va no
lam loang ket qua. `tron` danh dau nhung cap do de bao cao rieng, khong am
tham bo di.

    python -m src.tron_cap --nhanh A C --tap kiem_tra_cuoi
"""
import argparse
import hashlib
import io
import json
import random
import sys

from src import duong_dan


def _khoa_on_dinh(ma_mau, seed):
    """Dong xu rieng cho tung cap, tai lap duoc tu (ma_mau, seed).

    Dung bam thay vi mot `random.Random(seed)` chay tuan tu: nhu vay thu tu
    mau trong tep khong anh huong den nhan, va them bot mau khong lam doi
    nhan cua cac mau con lai.
    """
    h = hashlib.sha256(f"{seed}:{ma_mau}".encode()).hexdigest()
    return int(h[:8], 16) % 2


def tron(ket_qua_1, ket_qua_2, ten_1, ten_2, seed=42):
    """-> (phieu, khoa_giai_ma, trung_nhau).

    phieu:  [{ma, hoi_thoai, ban_A, ban_B}] — khong co ten nhanh
    khoa:   [{ma, ban_A, ban_B}] voi gia tri la TEN NHANH
    trung:  [ma, ...] cac cap hai ban giong het nhau
    """
    theo_id = {k["id"]: k for k in ket_qua_2}
    phieu, khoa, trung = [], [], []
    for k1 in ket_qua_1:
        k2 = theo_id.get(k1["id"])
        if k2 is None:
            continue
        v1 = (k1.get("du_doan") or "").strip()
        v2 = (k2.get("du_doan") or "").strip()
        if v1 == v2:
            trung.append(k1["id"])
            continue
        doi = _khoa_on_dinh(k1["id"], seed)
        ban_A, ban_B = (v1, v2) if doi == 0 else (v2, v1)
        nhan_A, nhan_B = (ten_1, ten_2) if doi == 0 else (ten_2, ten_1)
        phieu.append({"ma": k1["id"], "hoi_thoai": k1.get("input", ""),
                      "ban_A": ban_A, "ban_B": ban_B})
        khoa.append({"ma": k1["id"], "ban_A": nhan_A, "ban_B": nhan_B})
    return phieu, khoa, trung


CAU_HOI = [
    "Bản nào ghi đúng hơn về việc AI có triệu chứng gì?",
    "Bản nào có lỗi đáng ngại hơn trên thực hành lâm sàng?",
    "Nếu phải ký vào một bản, bác chọn bản nào?",
]


def in_phieu(phieu):
    """Phieu cham. Khong co ten nhanh, khong co goi y nao ve nguon goc."""
    ra = ["# Phiếu chấm mù",
          "",
          "Với mỗi cặp: đọc hội thoại, đọc hai bản, trả lời ba câu hỏi.",
          "Hai bản do hai cách làm khác nhau sinh ra. **Không có thông tin nào",
          "cho biết bản nào của cách nào** — đó là chủ ý.",
          "",
          "Nếu cả hai bản đều sai ở cùng một chỗ, ghi rõ vào phần ghi chú thay",
          "vì chọn bừa một bản.",
          ""]
    for i, p in enumerate(phieu, 1):
        ra += [f"---", "", f"## Cặp {i} — mã `{p['ma']}`", "",
               "### Hội thoại", "", "```", p["hoi_thoai"], "```", "",
               "### Bản A", "", "```", p["ban_A"], "```", "",
               "### Bản B", "", "```", p["ban_B"], "```", "",
               "### Trả lời", ""]
        for c in CAU_HOI:
            ra += [f"- {c}  ☐ A  ☐ B  ☐ như nhau", ""]
        ra += ["- Ghi chú:", ""]
    return "\n".join(ra)


def giai_ma(khoa, tra_loi):
    """tra_loi: [{ma, cau, chon}] voi chon thuoc {"A","B","nhu nhau"}.

    -> {ten_nhanh: so_lan_duoc_chon} theo tung cau hoi.
    """
    theo_ma = {k["ma"]: k for k in khoa}
    dem = {}
    for t in tra_loi:
        k = theo_ma.get(t["ma"])
        if k is None:
            continue
        cau = dem.setdefault(t["cau"], {"nhu nhau": 0})
        if t["chon"] == "nhu nhau":
            cau["nhu nhau"] += 1
            continue
        ten = k["ban_A"] if t["chon"] == "A" else k["ban_B"]
        cau[ten] = cau.get(ten, 0) + 1
    return dem


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhanh", nargs=2, required=True)
    # Mac dinh cu la "kiem_tra_cuoi" — vua la du lieu cua cuoc thi cu, VUA la
    # tap khoa chi duoc mo sau Cua 5. Mot lenh go thieu `--tap` la pham ca hai
    # dieu cam cung luc, va khong co gi bao lai.
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    from src import du_lieu as _dl
    _dl.chan_tap_khoa(a.tap)
    _dl.chan_tap_ngoai(a.tap)

    d = duong_dan.THU_MUC_DU_LIEU
    kq = []
    for ten in a.nhanh:
        dp = d / f"ra_{ten}_{a.tap}.jsonl"
        if not dp.exists():
            raise SystemExit(f"chua co {dp}")
        kq.append([json.loads(x) for x in open(dp, encoding="utf-8") if x.strip()])

    phieu, khoa, trung = tron(kq[0], kq[1], a.nhanh[0], a.nhanh[1], a.seed)

    tm = duong_dan.THU_MUC_KET_QUA
    (tm / f"phieu-cham-mu-{a.tap}.md").write_text(in_phieu(phieu), encoding="utf-8")
    # Khoa giai ma de RIENG. Neu no nam canh phieu thi phep cham mu chi la
    # mot cach goi, khong phai mot rang buoc.
    (duong_dan.GOC_DU_AN / "khoa-giai-ma.json").write_text(
        json.dumps({"seed": a.seed, "khoa": khoa}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"{len(phieu)} cap vao phieu, {len(trung)} cap bi loai vi hai ban "
          f"giong het nhau: {trung}")
    print(f"Phieu:  {tm / f'phieu-cham-mu-{a.tap}.md'}")
    print(f"Khoa:   {duong_dan.GOC_DU_AN / 'khoa-giai-ma.json'}  (de RIENG)")


if __name__ == "__main__":
    main()
