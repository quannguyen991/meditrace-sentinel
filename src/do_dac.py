# -*- coding: utf-8 -*-
"""Do va so sanh cac nhanh — mot cho duy nhat tinh so.

Nam mat chat luong, khong gop thanh mot con so:

    diem_cuoi     0,6 x ROUGE_avg + 0,4 x SectionF1, cong thuc cua cuoc thi
    section_f1    tach rieng vi no la nua khac cua diem, va de bi keo bang
                  hinh thuc chu khong bang noi dung
    bo_sot        phat bieu `con hieu luc` khong vao duoc ban nhap
    can_xac_nhan  phat bieu bi chuyen sang muc phu
    chi_phi       so luot goi mo hinh va token

DIEU KIEN CONG BANG (Task 18 buoc 4). Giam loi bang cach VIET IT DI la cai
thien gia. Nen truoc khi doc bat ky chenh lech nao, phai kiem: nhanh moi co
bo sot nhieu hon nhanh cu qua 20% khong. Vuot thi phep so sanh khong con
nghia, va `kiem_dieu_kien_cong_bang` bao thang.

KHONG dung ROUGE lam dieu kien. ROUGE thuong cho diem mot ban ghi sai chu
the gan bang mot ban ghi dung — do la ly do du an nay ton tai. Bao cao no
nhu chi so bo sung, khong lay lam cua.
"""
import io
import json
import sys

from src import cham_diem, chuan_dinh_dang, duong_dan


def nap_ket_qua(duong_dan_jsonl):
    return [json.loads(d) for d in
            open(duong_dan_jsonl, encoding="utf-8") if d.strip()]


def do_mot_nhanh(ket_qua, dung_muc_phu=True, bo_tat_dinh_dang=True):
    """-> dict cac so trung binh. `ket_qua` la mot tep ra_<nhanh>_<tap>.jsonl.

    `dung_muc_phu=False` cham tren ban da bo muc CAN XAC NHAN — xem
    `sinh_benh_an.tach_muc_phu` de biet vi sao can ca hai.

    `bo_tat_dinh_dang=True` chay `chuan_dinh_dang.chuan_hoa` tren CA ban nhap lan
    ban tham chieu truoc khi cham.

    VI SAO PHAI CO, va vi sao mac dinh la BAT. `chuan_dinh_dang` duoc viet va do
    ngay 11/09/2026 nhung KHONG tep nao goi no — mot bo bo tat dinh dang nam
    khong, dung ho lo~i "khai ma khong dien" da gap nam lan trong du an. Hau qua
    do duoc ngay tren chuoi the he 4: nhanh sinh thang viet tieu de kieu Markdown
    ("**LICH SU BENH:**") con duong ong sinh theo khuon nen viet dung ten muc cua
    ban tham chieu, va `section_f1` cua `A_nen` ra DUNG BANG KHONG. Diem gop la
    0,6 x ROUGE + 0,4 x SectionF1, nen mot nhanh bi chan tran chi vi cach viet
    tieu de — chenh lech doc ra duoc khi do se la chenh lech ve DINH DANG chu
    khong ve noi dung.

    Phep chuan hoa nay la phep DONG NHAT tren ban da dung ten muc chuan, nen bat
    no khong lam loi cho nhanh nao — xem phep thu cong bang o dau `chuan_dinh_dang`.
    """
    khoa = "du_doan" if dung_muc_phu else "du_doan_khong_muc_phu"
    diem, tong = [], {"so_luot_goi": 0, "token_vao": 0, "token_ra": 0,
                      "so_phat_bieu": 0, "so_can_xac_nhan": 0, "loi_ban_ghi": 0}
    for k in ket_qua:
        du_doan = k.get(khoa, k.get("du_doan", ""))
        tham_chieu = k.get("tham_chieu") or ""
        if bo_tat_dinh_dang:
            du_doan = chuan_dinh_dang.chuan_hoa(du_doan)
            tham_chieu = chuan_dinh_dang.chuan_hoa(tham_chieu)
        if tham_chieu:
            diem.append(cham_diem.diem_cuoi(du_doan, tham_chieu))
        for t in ("so_luot_goi", "token_vao", "token_ra",
                  "so_phat_bieu", "so_can_xac_nhan"):
            tong[t] += k.get(t, 0) or 0
        tong["loi_ban_ghi"] += len(k.get("loi_ban_ghi") or [])

    n = max(1, len(diem))
    ra = {"so_mau": len(ket_qua), "so_mau_co_tham_chieu": len(diem)}
    for t in ("rouge1", "rouge2", "rougel", "rouge_avg", "section_f1", "final"):
        ra[t] = sum(d[t] for d in diem) / n if diem else None
    ra.update(tong)
    return ra


def do_bo_sot(ket_qua):
    """Ty le bo sot trung binh, tinh tu `ghi_chu` — chi co o nhanh B/C/D.

    A va A+ sinh van xuoi, khong co bang phat bieu de doi chieu, nen ham nay
    tra None cho chung. Khong duoc lay ROUGE recall thay the roi goi la cung
    mot dai luong — hai thu do hai thu khac nhau.
    """
    co = [k for k in ket_qua if k.get("ghi_chu") is not None]
    if not co:
        return None
    tong_pb = sum(len(k["ghi_chu"]) for k in co)
    if tong_pb == 0:
        return None
    # `ghi_chu` ghi moi phat bieu di vao muc nao. Bo sot theo nghia cua
    # `kiem_day_du` phai doi chieu voi van ban; o day dem cai gan nhat co
    # duoc tu ghi chu: phat bieu bi day sang muc phu.
    phu = sum(1 for k in co for g in k["ghi_chu"] if g["muc"] == "CẦN XÁC NHẬN")
    return {"tong_phat_bieu": tong_pb, "sang_muc_phu": phu,
            "ty_le_muc_phu": phu / tong_pb}


def kiem_dieu_kien_cong_bang(bo_sot_cu, bo_sot_moi, nguong=0.20):
    """-> (dat, thong_diep). Task 18 buoc 4.

    Giam loi bang cach viet it di la cai thien gia. Neu nhanh moi bo sot
    nhieu hon nhanh cu qua `nguong` thi moi chenh lech khac deu khong doc
    duoc nua.
    """
    if bo_sot_cu is None or bo_sot_moi is None:
        return None, "khong du du lieu (nhanh khong co bang phat bieu)"
    cu, moi = bo_sot_cu["ty_le_muc_phu"], bo_sot_moi["ty_le_muc_phu"]
    # Luon neu TRI TUYET DOI. "Tang inf%" khi mau cu bang 0 la mot cau khong
    # doc duoc: no khong noi duoc 0% -> 1% khac 0% -> 40% cho nao.
    tri = f"{cu:.0%} -> {moi:.0%}"
    if cu == 0:
        tang = 0.0 if moi == 0 else float("inf")
    else:
        tang = (moi - cu) / cu
    tang_chu = "khong doi" if tang == 0 else (
        "tu khong len co" if tang == float("inf") else f"tang {tang:.0%}")
    if tang <= nguong:
        return True, f"bo sot {tri} ({tang_chu}, nguong {nguong:.0%}) — dat"
    return False, (f"bo sot {tri} ({tang_chu}) > nguong {nguong:.0%}. "
                   "Giam loi bang cach viet it di la cai thien gia.")


def bang_so_sanh(theo_nhanh):
    """theo_nhanh: {ten_nhanh: ket_qua_do}. -> chuoi bang Markdown."""
    cot = ["final", "rouge_avg", "section_f1", "so_phat_bieu",
           "so_can_xac_nhan", "so_luot_goi"]
    dong = ["| Nhánh | " + " | ".join(cot) + " |",
            "|" + "---|" * (len(cot) + 1)]
    for ten, d in theo_nhanh.items():
        o = []
        for c in cot:
            v = d.get(c)
            o.append("—" if v is None else
                     (f"{v:.4f}" if isinstance(v, float) else str(v)))
        dong.append(f"| {ten} | " + " | ".join(o) + " |")
    return "\n".join(dong)


KHUNG_BAO_CAO = """# So sánh các nhánh — tập `{tap}`

Sinh tự động bằng `python -m src.do_dac --tap {tap} --viet-bao-cao`.
Đừng sửa tay: sửa tay rồi chạy lại là mất.

## Cách đọc bảng

| Cột | Nghĩa |
|---|---|
| `final` | `0,6 × ROUGE_avg + 0,4 × SectionF1` — công thức của cuộc thi |
| `rouge_avg` | **Chỉ số bổ sung, không phải điều kiện.** ROUGE cho một bản ghi sai chủ thể điểm gần bằng một bản ghi đúng — đó chính là lý do dự án này tồn tại |
| `section_f1` | Nửa còn lại của điểm. Dễ bị kéo bằng hình thức chứ không bằng nội dung |
| `so_phat_bieu` | Số bản ghi trích được. Nhánh A và A+ không có bảng nên bằng 0 |
| `so_can_xac_nhan` | Số phát biểu bị đẩy xuống mục phụ. **Đẩy nhiều là cách làm đẹp điểm** — phải đọc kèm |
| `so_luot_goi` | Chi phí. A+ tốn gấp đôi A |

Mỗi nhánh B/C/D có thêm một dòng *(bỏ mục phụ)*: mục `CẦN XÁC NHẬN` không có
trong bản tham chiếu, nên bộ chấm tính nó là một mục dự đoán thừa và trừ điểm
Section F1. Hai dòng là hai cách đọc, không phải hai kết quả.

## Bảng

{bang}

{cong_bang}

## Giới hạn phải nói rõ

1. **Nhánh D gần như trùng nhánh C** trên đầu ra do luật sinh ra. Task 16 và
   Task 17 đi tìm đúng những luật mà khâu sinh đã áp dụng. Chênh lệch D − C
   nếu có thì phải chỉ ra đến từ đâu.
2. **Độ đầy đủ đo bằng bảng phát biểu, không bằng hội thoại.** Khâu trích xuất
   bỏ sót từ đầu thì phép đo này vẫn báo "đầy đủ".
3. **`bo_sot` không tính được cho A và A+** vì hai nhánh đó không có bảng trung
   gian. Không được lấy ROUGE recall thay thế rồi gọi là cùng một đại lượng.
"""


def bao_cao(tap, bang, cong_bang, theo_nhanh, bo_sot):
    return KHUNG_BAO_CAO.format(tap=tap, bang=bang,
                                cong_bang=cong_bang or "")


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--nhanh", nargs="+",
                    default=["A", "A_cong", "B", "C", "C_ghi_de", "D"])
    ap.add_argument("--viet-bao-cao", action="store_true")
    a = ap.parse_args()

    from src import du_lieu as _dl
    _dl.chan_tap_ngoai(a.tap)
    _dl.chan_tap_khoa(a.tap)

    theo_nhanh, bo_sot, tho = {}, {}, {}
    for ten in a.nhanh:
        dp = duong_dan.THU_MUC_DU_LIEU / f"ra_{ten}_{a.tap}.jsonl"
        if not dp.exists():
            print(f"(chua co {dp.name})")
            continue
        kq = nap_ket_qua(dp)
        theo_nhanh[ten] = do_mot_nhanh(kq)
        tho[ten] = do_mot_nhanh(kq, bo_tat_dinh_dang=False)
        if ten in ("B", "C", "C_ghi_de", "D"):
            theo_nhanh[ten + " (bỏ mục phụ)"] = do_mot_nhanh(kq, dung_muc_phu=False)
        bo_sot[ten] = do_bo_sot(kq)

    if not theo_nhanh:
        print("Chua co nhanh nao chay xong.")
        return
    bang = bang_so_sanh(theo_nhanh)
    print(bang)
    print("")
    # In luon phan DINH DANG lam doi diem bao nhieu. Bat im lang mot phep chuan
    # hoa la cach de nhat de mot chenh lech ve dinh dang bi doc thanh chenh lech
    # ve noi dung — `chuan_dinh_dang` doi hoi bang nay duoc doc cung so lieu.
    print("Định dạng làm đổi điểm bao nhiêu (bỏ tắt định dạng so với để nguyên):")
    for ten in sorted(tho):
        a1, a0 = theo_nhanh[ten], tho[ten]
        if a1.get("final") is None or a0.get("final") is None:
            continue
        d_final = a1["final"] - a0["final"]
        d_muc = a1["section_f1"] - a0["section_f1"]
        dau = "khong doi" if abs(d_final) < 1e-9 else f"{d_final:+.4f}"
        print(f"  {ten:22} final {a0['final']:.4f} -> {a1['final']:.4f}  ({dau})"
              f"   F1 mục {a0['section_f1']:.4f} -> {a1['section_f1']:.4f} ({d_muc:+.4f})")
    print("")
    dong_cong_bang = ""
    if bo_sot.get("B") and bo_sot.get("C"):
        dat, tin = kiem_dieu_kien_cong_bang(bo_sot["B"], bo_sot["C"])
        dong_cong_bang = f"Điều kiện công bằng B → C: {tin}"
        print(dong_cong_bang)

    if a.viet_bao_cao:
        dp = duong_dan.THU_MUC_KET_QUA / f"so-sanh-nhanh-{a.tap}.md"
        dp.write_text(bao_cao(a.tap, bang, dong_cong_bang, theo_nhanh, bo_sot),
                      encoding="utf-8")
        print(f"\nDa ghi {dp}")


if __name__ == "__main__":
    main()
