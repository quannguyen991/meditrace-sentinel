# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Điều phối]
Làm gì   : Chạy nhánh E: lấy bản nháp của nhánh A, bổ sung chỗ sót và sửa cục bộ bằng bảng
           mệnh đề, không viết lại bản nháp.
Vào → Ra : tệp kết quả nhánh A + kết quả thô của đường ống → tệp kết quả nhánh E kèm tỉ lệ
           bản nháp A giữ nguyên
Đọc từ   : chay_E() bổ sung rồi sửa bản nháp A; ty_le_giu() đo phần bản nháp A còn nguyên
Mục lục (các hàm/lớp chính):
  chay_E()     Chạy nhánh E: bổ sung và sửa bản nháp của A
  ty_le_giu()  Tính tỉ lệ bản nháp A còn nguyên sau khi sửa
  main()       Điểm vào dòng lệnh chạy nhánh E
Gọi tới  : bo_du_lieu/nap_du_lieu, duong_ong/b1_cau_truc_menh_de,
           duong_ong/b2_gom_nguoi_thuc_the, duong_ong/b3_cap_nhat_trang_thai,
           duong_ong/b4_kiem_day_du, duong_ong/b5_viet_ban_nhap, duong_ong/b6_sua_cuc_bo,
           he_thong/duong_dan
Tên cũ   : nhanh_e.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Nhánh E — dùng bảng phát biểu để RA LẠI bản nháp của A, không thay thế nó.

VÌ SAO CÓ NHÁNH NÀY. Đo trên tập phát triển cho kết quả rõ ràng:

    A (sinh trực tiếp, đã huấn luyện)   0.6216
    C (sinh từ bảng phát biểu)          0.4089

Sinh bệnh án TỪ bảng phát biểu thua hẳn sinh trực tiếp, và thua chủ yếu ở
hình thức: A học văn phong bệnh án từ 1.357 bản mẫu, còn bộ sinh bằng luật
chỉ biết ghép cụm theo bảng tra.

Nhưng bảng phát biểu vẫn có thứ A không có: nó biết MỖI mệnh đề thuộc về AI
và dựa trên lượt thoại nào. Nên thay vì dùng bảng để VIẾT, dùng nó để KIỂM.

    E = bản nháp của A  +  bổ sung cho bộ sót (Task 16)  +  sửa cục bộ (Task 17)

Đối chứng đúng của E là A+ (A tự đọc lại bản của chính nó, không có bảng):
A+ chỉ sửa 3/35 bản và không đổi điểm. Nếu E hơn A+ thì cái làm nên chênh
lệch là BẢNG PHÁT BIỂU, không phải chuyện "gọi mô hình hai lần".

RỦI RO ĐÃ BIẾT, phải đo chứ không được giả định: `sua_cuc_bo` đổi mệnh đề
trong bảng phải xuất hiện NGUYÊN VĂN trong câu thì mới coi là có nguồn. A
viết văn xuôi dài, nên nhiều câu sẽ không khớp và bị đẩy xuống mức cần xác
nhận — tức cơ chế này có thể PHÁ bản nháp tốt. `ty_le_giu` đo đúng điều đó.
"""
import io
import json
import sys

from src.duong_ong import b3_cap_nhat_trang_thai as cap_nhat
from src.he_thong import duong_dan as duong_dan
from src.duong_ong import b4_kiem_day_du as kiem_day_du
from src.duong_ong import b1_cau_truc_menh_de as phat_bieu
from src.duong_ong import b6_sua_cuc_bo as sua_cuc_bo
from src.duong_ong import b2_gom_nguoi_thuc_the as thuc_the


# ─── _bang_cho_mau() — Dựng bảng mệnh đề đã liên kết và áp luật cho một ca ────────────
# Trả về mệnh đề và tên chủ thể để dùng cho bổ sung và sửa.
def _bang_cho_mau(hoi_thoai, ps_json):
    """Dùng bảng phát biểu đã liên kết + đã áp luật cho một hội thoại."""
    tt = thuc_the.lien_ket(hoi_thoai)
    bang = phat_bieu.bang_ten_tu_thuc_the(tt)
    nguoi_noi = {so: vai for so, vai, _ in thuc_the.tach_luot(hoi_thoai) if vai}
    ps, loi = phat_bieu.tu_json(ps_json or [], nguoi_noi_theo_luot=nguoi_noi,
                                id_theo_ten=bang)
    for p_moi, p_goc in zip(ps, [x for x in (ps_json or []) if x.get("luot_thoai")]):
        p_moi.ten_chu_the = str(p_goc.get("chu_the", ""))
    ten_chu_the = {t.id: t.ten_chuan for t in tt
                   if t.loai == "người" and t.id != 0}
    return cap_nhat.ap_luat(ps), ten_chu_the, loi


# ═══ chay_E() — Chạy nhánh E: bổ sung và sửa bản nháp của A ═══════════════════════════
# Không gọi mô hình; đọc kết quả A và kết quả rút thô đã sinh sẵn.
def chay_E(ra_A, kq_tho, bo_sung=True, sua=True):
    """ra_A: đọc từ ra_A_<tap>.jsonl. kq_tho: đọc từ trich_<tap>_<n>.jsonl.

    Không gọi mô hình. Cả hai đầu vào đều là tệp đã sinh sẵn.
    """
    theo_id = {k["id"]: k for k in kq_tho}
    ra = []
    for a in ra_A:
        tho = theo_id.get(a["id"])
        ps, ten_chu_the, loi = _bang_cho_mau(a["input"],
                                             (tho or {}).get("phat_bieu"))
        van = a["du_doan"]
        da_bo_sung, da_sua = [], []
        if bo_sung:
            van, da_bo_sung = kiem_day_du.bo_sung(ps, van, ten_chu_the=ten_chu_the)
        if sua:
            ket = sua_cuc_bo.sua(van, ps, ten_chu_the=ten_chu_the)
            van, da_sua = ket.van_ban, ket.da_sua

        from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an
        than, _phu = sinh_benh_an.tach_muc_phu(van)
        ra.append({"id": a["id"], "input": a["input"],
                   "tham_chieu": a["tham_chieu"], "du_doan": van,
                   "du_doan_khong_muc_phu": than,
                   "ban_nhap_A": a["du_doan"],
                   "so_luot_goi": a.get("so_luot_goi", 1),
                   "token_vao": a.get("token_vao", 0),
                   "token_ra": a.get("token_ra", 0),
                   "so_phat_bieu": len(ps), "loi_ban_ghi": loi,
                   "so_can_xac_nhan": len(da_sua),
                   "da_bo_sung": da_bo_sung, "da_sua": da_sua,
                   "ghi_chu": None})
    return ra


# ═══ ty_le_giu() — Tính tỉ lệ bản nháp A còn nguyên sau khi sửa ═══════════════════════
# Cơ chế sửa xoá mất nửa bản nháp thì điểm cao cũng không dùng được.
def ty_le_giu(ra_E):
    """Bao nhiêu phần của bản nháp A còn nguyên sau khi ra lại.

    Con số này quan trọng ngang điểm: một cơ chế "sửa" xóa mất nửa bản nháp
    thì điểm có cao cũng không dùng được.
    """
    giu = sum(len(k["du_doan_khong_muc_phu"]) for k in ra_E)
    goc = sum(len(k["ban_nhap_A"]) for k in ra_E)
    doi = sum(1 for k in ra_E if k["du_doan"].strip() != k["ban_nhap_A"].strip())
    return {"ky_tu_goc": goc, "ky_tu_con": giu,
            "ty_le_giu": giu / max(1, goc), "so_ban_bi_doi": doi,
            "so_ban": len(ra_E)}


# ═══ main() — Điểm vào dòng lệnh chạy nhánh E ═════════════════════════════════════════
# Đọc tệp kết quả A và rút thô rồi ghi kết quả nhánh E.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--max-token", type=int, default=3072)
    ap.add_argument("--khong-bo-sung", action="store_true")
    ap.add_argument("--khong-sua", action="store_true")
    ap.add_argument("--ten", default="E")
    a = ap.parse_args()

    from src.bo_du_lieu import nap_du_lieu as _dl
    _dl.chan_tap_ngoai(a.tap)
    _dl.chan_tap_khoa(a.tap)

    d = duong_dan.THU_MUC_DU_LIEU
    ra_A = [json.loads(x) for x in open(d / f"ra_A_{a.tap}.jsonl",
                                        encoding="utf-8") if x.strip()]
    kq_tho = [json.loads(x) for x in
              open(d / f"trich_{a.tap}_{a.max_token}.jsonl",
                   encoding="utf-8") if x.strip()]

    ra = chay_E(ra_A, kq_tho, bo_sung=not a.khong_bo_sung, sua=not a.khong_sua)
    dp = d / f"ra_{a.ten}_{a.tap}.jsonl"
    dp.write_text("\n".join(json.dumps(k, ensure_ascii=False) for k in ra),
                  encoding="utf-8")

    t = ty_le_giu(ra)
    print(f"Ghi {len(ra)} dong -> {dp}")
    print(f"Ban bi sua doi: {t['so_ban_bi_doi']}/{t['so_ban']}")
    print(f"Giu lai {t['ty_le_giu']:.0%} do dai ban nhap cua A "
          f"({t['ky_tu_con']}/{t['ky_tu_goc']} ky tu)")
    print(f"Tong cho da sua: {sum(len(k['da_sua']) for k in ra)}, "
          f"da bo sung: {sum(len(k['da_bo_sung']) for k in ra)}")


if __name__ == "__main__":
    main()
