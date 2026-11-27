# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : So các nhánh trên năm mặt chất lượng (điểm cuối, Section F1, bỏ sót, cần xác
           nhận, chi phí) và kiểm nhánh mới không giảm lỗi nhờ viết ít.
Vào → Ra : kết quả các nhánh trên một tập (--tap, --nhanh) → bảng so sánh markdown, tùy chọn
           ghi báo cáo
Đọc từ   : do_mot_nhanh() tính điểm một nhánh; kiem_dieu_kien_cong_bang() chặn cải thiện giả
Mục lục (các hàm/lớp chính):
  do_mot_nhanh()              Tính điểm trung bình một nhánh trên một tập
  do_bo_sot()                 Tính tỉ lệ mệnh đề bị đẩy sang mục phụ
  kiem_dieu_kien_cong_bang()  Kiểm nhánh mới không giảm lỗi bằng cách viết ít
  bang_so_sanh()              Dựng bảng Markdown so các nhánh
  main()                      Chạy dòng lệnh so các nhánh và in bảng
Gọi tới  : do_luong/cham_diem, do_luong/chuan_dinh_dang, bo_du_lieu/nap_du_lieu,
           he_thong/duong_dan
Tên cũ   : do_dac.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đo và so sánh các nhánh — một chỗ duy nhất tính số.

Năm mặt chất lượng, không gộp thành một con số:

    diem_cuoi     0,6 x ROUGE_avg + 0,4 x SectionF1, công thức của cuộc thi
    section_f1    tách riêng vì nó là nửa khác của điểm, và dễ bị kéo bằng
                  hình thức chữ không bằng nội dung
    bo_sot        phát biểu `còn hiệu lực` không vào được bản nháp
    can_xac_nhan  phát biểu bị chuyển sang mục phụ
    chi_phi       số lượt gọi mô hình và token

ĐIỀU KIỆN CÔNG BẰNG (Task 18 bước 4). Giảm lỗi bằng cách VIẾT ÍT ĐI là cải
thiện giả. Nên trước khi đọc bất kỳ chênh lệch nào, phải kiểm: nhánh mới có
bỏ sót nhiều hơn nhánh cũ quá 20% không. Vượt thì phép so sánh không còn
nghĩa, và `kiem_dieu_kien_cong_bang` báo thẳng.

KHÔNG dùng ROUGE làm điều kiện. ROUGE thường cho điểm một bản ghi sai chủ
thể gần bằng một bản ghi đúng — đó là lý do dự án này tồn tại. Báo cáo nó
như chỉ số bổ sung, không lấy làm cửa.
"""
import io
import json
import sys

from src.do_luong import cham_diem as cham_diem
from src.do_luong import chuan_dinh_dang as chuan_dinh_dang
from src.he_thong import duong_dan as duong_dan


# ═══ nap_ket_qua() — Nạp tệp kết quả JSONL của một nhánh ══════════════════════════════
def nap_ket_qua(duong_dan_jsonl):
    return [json.loads(d) for d in
            open(duong_dan_jsonl, encoding="utf-8") if d.strip()]


# ═══ do_mot_nhanh() — Tính điểm trung bình một nhánh trên một tập ═════════════════════
# Chuẩn hoá tiêu đề trước khi chấm; có tuỳ chọn chấm bản bỏ mục phụ.
def do_mot_nhanh(ket_qua, dung_muc_phu=True, bo_tat_dinh_dang=True):
    """-> dict các số trung bình. `ket_qua` là một tệp ra_<nhanh>_<tap>.jsonl.

    `dung_muc_phu=False` chấm trên bản đã bỏ mục CẦN XÁC NHẬN — xem
    `sinh_benh_an.tach_muc_phu` để biết vì sao cần cả hai.

    `bo_tat_dinh_dang=True` chạy `chuan_dinh_dang.chuan_hoa` trên CẢ bản nháp lẫn
    bản tham chiếu trước khi chấm.

    VÌ SAO PHẢI CÓ, và vì sao mặc định là BẬT. `chuan_dinh_dang` được viết và đo
    ngày 11/09/2026 nhưng KHÔNG tệp nào gọi nó — một bộ bỏ tắt định dạng nằm
    không, đúng họ lo~i "khai mà không điền" đã gặp năm lần trong dự án. Hậu quả
    đo được ngay trên chuỗi thế hệ 4: nhánh sinh thẳng viết tiêu đề kiểu Markdown
    ("**LICH SU BENH:**") còn đường ống sinh theo khuôn nên viết đúng tên mục của
    bản tham chiếu, và `section_f1` của `A_nen` ra ĐÚNG BẰNG KHÔNG. Điểm gộp là
    0,6 x ROUGE + 0,4 x SectionF1, nên một nhánh bị chặn trần chỉ vì cách viết
    tiêu đề — chênh lệch đọc ra được khi đó sẽ là chênh lệch về ĐỊNH DẠNG chứ
    không về nội dung.

    Phép chuẩn hóa này là phép ĐỒNG NHẤT trên bản đã đúng tên mục chuẩn, nên bật
    nó không làm lỗi cho nhánh nào — xem phép thử công bằng ở đầu `chuan_dinh_dang`.
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


# ═══ do_bo_sot() — Tính tỉ lệ mệnh đề bị đẩy sang mục phụ ═════════════════════════════
# Chỉ có ở nhánh B/C/D; nhánh A và A+ không có bảng mệnh đề nên trả None.
def do_bo_sot(ket_qua):
    """Tỷ lệ bỏ sót trung bình, tính từ `ghi_chu` — chỉ có ở nhánh B/C/D.

    A và A+ sinh văn xuôi, không có bảng phát biểu để đối chiếu, nên hàm này
    trả None cho chúng. Không được lấy ROUGE recall thay thế rồi gọi là cùng
    một đại lượng — hai thứ đo hai thứ khác nhau.
    """
    co = [k for k in ket_qua if k.get("ghi_chu") is not None]
    if not co:
        return None
    tong_pb = sum(len(k["ghi_chu"]) for k in co)
    if tong_pb == 0:
        return None
    # `ghi_chu` ghi mỗi phát biểu đi vào mục nào. Bỏ sót theo nghĩa của
    # `kiem_day_du` phải đối chiếu với văn bản; ở đây đếm cái gần nhất có
    # được từ ghi chú: phát biểu bị đẩy sang mục phụ.
    phu = sum(1 for k in co for g in k["ghi_chu"] if g["muc"] == "CẦN XÁC NHẬN")
    return {"tong_phat_bieu": tong_pb, "sang_muc_phu": phu,
            "ty_le_muc_phu": phu / tong_pb}


# ═══ kiem_dieu_kien_cong_bang() — Kiểm nhánh mới không giảm lỗi bằng cách viết ít ═════
# Đạt khi bỏ sót tăng không quá ngưỡng; trả (đạt, thông điệp).
def kiem_dieu_kien_cong_bang(bo_sot_cu, bo_sot_moi, nguong=0.20):
    """-> (dat, thong_diep). Task 18 bước 4.

    Giảm lỗi bằng cách viết ít đi là cải thiện giả. Nếu nhánh mới bỏ sót
    nhiều hơn nhánh cũ quá `nguong` thì mọi chênh lệch khác đều không đọc
    được nữa.
    """
    if bo_sot_cu is None or bo_sot_moi is None:
        return None, "khong du du lieu (nhanh khong co bang phat bieu)"
    cu, moi = bo_sot_cu["ty_le_muc_phu"], bo_sot_moi["ty_le_muc_phu"]
    # Luôn nêu TRỊ TUYỆT ĐỐI. "Tăng inf%" khi mẫu cũ bằng 0 là một câu không
    # đọc được: nó không nói được 0% -> 1% khác 0% -> 40% chỗ nào.
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


# ═══ bang_so_sanh() — Dựng bảng Markdown so các nhánh ═════════════════════════════════
def bang_so_sanh(theo_nhanh):
    """theo_nhanh: {ten_nhanh: ket_qua_do}. -> chuỗi bảng Markdown."""
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

Sinh tự động bằng `python -m src.do_luong.do_dac --tap {tap} --viet-bao-cao`.
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


# ═══ bao_cao() — Điền số liệu vào khung báo cáo ═══════════════════════════════════════
def bao_cao(tap, bang, cong_bang, theo_nhanh, bo_sot):
    return KHUNG_BAO_CAO.format(tap=tap, bang=bang,
                                cong_bang=cong_bang or "")


# ═══ main() — Chạy dòng lệnh so các nhánh và in bảng ══════════════════════════════════
# In thêm mức định dạng làm đổi điểm bao nhiêu khi bật chuẩn hoá.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--nhanh", nargs="+",
                    default=["A", "A_cong", "B", "C", "C_ghi_de", "D"])
    ap.add_argument("--viet-bao-cao", action="store_true")
    a = ap.parse_args()

    from src.bo_du_lieu import nap_du_lieu as _dl
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
    # In luôn phần ĐỊNH DẠNG làm đổi điểm bao nhiêu. Bắt im lặng một phép chuẩn
    # hóa là cách dễ nhất để một chênh lệch về định dạng bị đọc thành chênh lệch
    # về nội dung — `chuan_dinh_dang` đòi hỏi bảng này được đọc cùng số liệu.
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
