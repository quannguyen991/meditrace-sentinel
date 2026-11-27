# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Đo mô hình có sa vào từng bẫy của bộ chẩn đoán không (gán dị ứng sai người, nâng
           bệnh nghi thành chắc...), chấm tự động.
Vào → Ra : mô hình (--model) hoặc tệp kết quả đã lưu (--cham-lai) → bảng đạt/hỏng theo bẫy,
           ghi JSON
Đọc từ   : cham() chấm một mẫu theo phép kiểm của bẫy; main() chạy mô hình hoặc chấm lại
Mục lục (các hàm/lớp chính):
  cham()             Chấm một mẫu theo phép kiểm của bẫy tương ứng
  cham_lai()         Chấm lại từ tệp đã lưu, không chạy mô hình
  kiem_chu_the()     Kiểm dị ứng của mẹ có gán cho người nhà
  kiem_dinh_chinh()  Kiểm đính chính: giữ mốc mới, mốc cũ không ngang hàng
  kiem_nghi_ngo()    Kiểm bệnh nghi không bị nâng thành chẩn đoán chắc
  kiem_cheo()        Kiểm chéo đặc điểm của trẻ gán sai chủ thể
  main()             Chạy dòng lệnh đo mô hình trên bộ chẩn đoán
Gọi tới  : bo_du_lieu/nap_du_lieu, bo_du_lieu/sinh_bo_chan_doan, he_thong/duong_dan,
           huan_luyen/chon_mo_hinh_bakeoff
Dùng bởi : do_luong/doi_chung_tam_thuong
Tên cũ   : do_bo_chan_doan.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đo mô hình trên bộ kiểm tra chẩn đoán — chấm TỰ ĐỘNG.

Đây là lý do bộ chẩn đoán tồn tại: đáp án biết trước chính xác vì cả hội thoại
lẫn bệnh án đúng đều do cùng một đoạn mã sinh ra. Không phải chấm tay.

Mỗi tình huống một phép kiểm. Phép kiểm được viết để TRẢ LỜI ĐƯỢC và để HỎNG —
nếu nó không bao giờ báo sai thì nó vô dụng.

    python -m src.do_luong.do_bo_chan_doan --model Qwen/Qwen3-8B --n 15
"""
import argparse
import io
import json
import re
import sys

from src.huan_luyen import chon_mo_hinh_bakeoff as bakeoff

TRE = re.compile(r"(?i)\b(trẻ|bé|cháu|em bé)\b")
ME = re.compile(r"(?i)\b(mẹ|người nhà|tôi)\b")


# ─── _co() — Tìm cụm theo ranh giới từ hai phía ───────────────────────────────────────
# Chặn cả bên trái nên "ho" không khớp vào "cho".
def _co(cum, van_ban):
    """So theo ranh giới từ — chặn CẢ HAI bên, không chặn ranh giới CỤM.

    Bản 1 chỉ chặn bên PHẢI. Hậu quả: "ho" khớp vào đuôi chữ "cho", nên
    "cho uống hạ sốt" bị tính là đã nhắc tới triệu chứng "ho" — 3/4 ca
    moi_bia báo hỏng đều là lỗi này, không phải lỗi mô hình.

    Chặn bên trái bằng lookbehind. Vẫn phải khớp được tiền tố của một CỤM
    ("ho" trong "ho khan", "2 ngày" trong "sốt 2 ngày nay") vì phép kiểm
    dinh_chinh dựa vào đó — nên chỉ chặn ký tự chữ, không chặn dấu cách.
    """
    return re.search(rf"(?<![\wÀ-ỹ]){re.escape(cum)}(?![\wÀ-ỹ])",
                     van_ban or "", re.I) is not None


# ─── _gop() — Gộp các trường văn bản của một mệnh đề để tìm cụm ───────────────────────
def _gop(p):
    """Gộp các trường văn bản của một phát biểu để tìm cụm."""
    return " ".join(str(p.get(k, "")) for k in ("noi_dung", "thoi_gian_su_kien", "moc_thoi_gian"))


# --------------------------------------------------------------- phép kiểm

# ═══ kiem_chu_the() — Kiểm dị ứng của mẹ có gán cho người nhà ═════════════════════════
# Phải có mệnh đề gán cho người nhà; gán cho bệnh nhân là hỏng.
def kiem_chu_the(mau, ps):
    """Dị ứng của ME phải được gán cho ME.

    SỬA 10/09/2026 — LO~ HỔNG: bản trước kiểm thể PHỦ ĐỊNH, "chủ thể không khớp
    (tre|be|chau|em be)". Một hệ thống ghi `chu_the = "benh nhan"` cho dị ứng
    của mẹ thì LỌT QUA, vì "bệnh nhân" không khớp bảng từ đó. Đối chứng tầm
    thường `benh_nhan` — gán MỌI mệnh đề cho bệnh nhân — đạt 60/60 = 100% ở
    nhóm này, trong khi nó sai toàn bộ.
    """
    thuoc = mau["thuoc"]
    lien_quan = [p for p in ps if _co(thuoc, _gop(p))]
    if not lien_quan:
        return False, "khong trich duoc di ung nao"
    # Kiểm thể KHẲNG ĐỊNH: phải có một phát biểu gán cho NGƯỜI NHÀ. Hằng số
    # `ME` được khai từ đầu nhưng chưa bao giờ được dùng — một hằng số không ai
    # đọc là dấu hiệu phép kiểm chưa làm đúng việc nó mô tả.
    dung = [p for p in lien_quan if ME.search(str(p.get("chu_the", "")))]
    if dung:
        return True, ""
    ai = ", ".join(sorted({str(p.get("chu_the") or "?") for p in lien_quan}))
    return False, f"gan di ung {thuoc} cho {ai} thay vi cho nguoi nha"


# ═══ kiem_chac_chan() — Kiểm chưa thấy bao giờ giữ là chưa ghi nhận ═══════════════════
# Hỏng nếu nâng thành mức chắc chắn khác.
def kiem_chac_chan(mau, ps):
    """"Chưa thấy bị bao giờ" phải giữ là 'chưa ghi nhận', không thành phủ định chắc chắn."""
    tc = mau["trieu_chung"]
    lien_quan = [p for p in ps if _co(tc, _gop(p))]
    if not lien_quan:
        return False, f"khong trich duoc gi ve {tc}"
    for p in lien_quan:
        if p.get("do_chac_chan") == "chưa ghi nhận":
            return True, ""
    return False, "nang 'chua ghi nhan' thanh muc chac chan khac"


# ═══ kiem_dinh_chinh() — Kiểm đính chính: giữ mốc mới, mốc cũ không ngang hàng ════════
# Hỏng khi cả hai mốc cùng có mà không đánh dấu đính chính.
def kiem_dinh_chinh(mau, ps):
    """Giữ mốc MỚI, và mốc CŨ không được dùng như một sự thật ngang hàng.

    BẢN 1 CỦA PHÉP KIỂM NÀY SAI: nó báo hỏng nếu mốc cũ xuất hiện ở BẤT KỲ đâu.
    Nhưng thiết kế của chính dự án nói phải GIỮ bản cũ (trang_thai "bị thay thế")
    để truy lại được rằng đã có đính chính. Phép kiểm mâu thuẫn với thiết kế,
    và cho kết quả 0/15 trong khi mô hình làm ĐÚNG:

        {"noi_dung":"sốt", "moc_thoi_gian":"4 ngày", "quan_he":"không"}
        {"noi_dung":"sốt", "moc_thoi_gian":"2 ngày", "quan_he":"đính chính"}

    Bản 2: đạt khi mốc MỚI có mặt, VÀ (mốc cũ vắng mặt HOẶC có bản ghi đánh dấu
    là đính chính). Hỏng khi cả hai mốc cùng tồn tại mà không đánh dấu gì —
    lúc đó hai mốc trông ngang hàng nhau và không biết dùng cái nào.
    """
    moi, cu = mau["moc_moi"], mau["moc_cu"]
    if not any(_co(moi, _gop(p)) for p in ps):
        return False, f"mat moc da dinh chinh ({moi})"
    co_moc_cu = any(_co(cu, _gop(p)) for p in ps)
    co_danh_dau = any(p.get("quan_he") == "đính chính" for p in ps)
    if co_moc_cu and not co_danh_dau:
        return False, f"giu ca hai moc ({cu} va {moi}) ma khong danh dau dinh chinh"
    return True, ""


# ═══ kiem_dien_bien() — Kiểm diễn biến: phải giữ cả hai mốc ═══════════════════════════
# Mất mốc nào, hoặc coi là đính chính, đều hỏng.
def kiem_dien_bien(mau, ps):
    """GIỮ CẢ HAI mốc — đây không phải đính chính."""
    van = " | ".join(_gop(p) for p in ps)
    co_cu = _co(mau["moc_cu"], van)      # "Hôm qua"
    co_moi = _co(mau["moc_moi"], van)    # "hôm nay"
    if co_cu and co_moi:
        return True, ""
    if co_moi and not co_cu:
        return False, "vut mat moc dau — coi dien bien la dinh chinh"
    if co_cu and not co_moi:
        return False, "vut mat moc sau"
    return False, "mat ca hai moc"


# ═══ kiem_gia_dinh() — Kiểm câu giả định không bị ghi thành triệu chứng thật ══════════
def kiem_gia_dinh(mau, ps):
    """Câu giả định KHÔNG được ghi thành triệu chứng đã xảy ra."""
    dk = mau["dieu_kien"]
    sai = [p for p in ps
           if _co(dk, _gop(p)) and p.get("tinh_huong", "thực tế") == "thực tế"]
    if sai:
        return False, f"ghi '{dk}' thanh trieu chung thuc te"
    return True, ""


# ═══ kiem_moi_bia() — Kiểm câu hỏi không ai trả lời không tạo mệnh đề ═════════════════
def kiem_moi_bia(mau, ps):
    """Câu hỏi không ai trả lời thì KHÔNG được tạo phát biểu."""
    moi = mau["moi_khong_duoc_tra_loi"]
    sai = [p for p in ps if _co(moi, _gop(p))]
    if sai:
        return False, f"tu dien '{moi}' du khong ai tra loi"
    return True, ""


# ═══ kiem_sach() — Kiểm nhóm đối chứng không bị cảnh giác quá mức ═════════════════════
# Hỏng khi chưa ghi nhận hoặc giả định xuất hiện ở hội thoại bình thường.
def kiem_sach(mau, ps):
    """Nhóm đối chứng: không được cảnh giác quá mức."""
    if not ps:
        return False, "khong trich duoc gi"
    bao_dong_gia = [p for p in ps
                    if p.get("do_chac_chan") == "chưa ghi nhận"
                    or p.get("tinh_huong", "thực tế") != "thực tế"]
    if bao_dong_gia:
        return False, f"{len(bao_dong_gia)} bao dong gia tren hoi thoai binh thuong"
    return True, ""


# --------------------------------------------------------- phép kiểm CHÉO
# Bảy phép kiểm trên chỉ kiểm BẪY RIÊNG của từng tình huống. Một mô hình có
# thể tránh được cả bảy bẫy mà vẫn gán sai chủ thể ở những bản ghi khác —
# và con số tổng sẽ không hề phản ánh điều đó.
#
# Đã xảy ra thật: ở lần đo 4B, bảng tình huống cho 103/105 = 98%, nhưng 17
# bản ghi ghi TUỔI CỦA TRẺ lại gán chủ thể là "người nhà". Không phép kiểm
# nào trong bảy cái đó chạm tới, vì nó không phải bẫy của tình huống nào.
#
# Nên phải có một lớp kiểm chạy trên MỌI mẫu, và báo cáo RIÊNG.

TRE_TRONG_NOI_DUNG = re.compile(
    r"(?i)(cháu|bé|trẻ|con)\s+\S+\s+tuổi|(cháu|bé|trẻ)\s+(nặng|cao)\s")


# ═══ kiem_cheo() — Kiểm chéo đặc điểm của trẻ gán sai chủ thể ═════════════════════════
# Chạy trên mọi mẫu, không phụ thuộc tình huống.
def kiem_cheo(mau, ps):
    """-> danh sách lỗi tìm thấy trên MỘT mẫu, không phụ thuộc tình huống."""
    loi = []
    for i, p in enumerate(ps):
        nd = str(p.get("noi_dung", ""))
        ct = str(p.get("chu_the", "")).strip()
        if TRE_TRONG_NOI_DUNG.search(nd) and not TRE.match(ct):
            loi.append({"chi_so": i, "loai": "chu_the_cua_dac_diem_tre",
                        "chu_the": ct, "noi_dung": nd})
    return loi


# ═══ kiem_nghi_ngo() — Kiểm bệnh nghi không bị nâng thành chẩn đoán chắc ══════════════
# Hỏng nếu nâng mức hoặc bỏ hẳn thông tin bệnh nghi.
def kiem_nghi_ngo(mau, ps):
    """Thách thức 3 — "nghi" không được nâng thành chẩn đoán xác định.

    Bẫy này có HAI vế, và chỉ bắt một vế thì phép đo không đầy đủ:

      nâng mức   ghi bệnh nghi thành `chac chan`  -> sai
      bỏ hẳn     không nhắc gì tới bệnh nghi      -> cũng sai, theo cách khác

    `_bay_nghi_ngo` ghi rõ cả hai trong chú thích của nó, nhưng trước
    10/09/2026 `PHEP_KIEM` KHÔNG có mục này: bộ sinh có 9 tình huống còn bộ
    chấm chỉ có 7, và `cham()` ném `KeyError` khi gặp `nghi_ngo` hoặc
    `nhat_quan`. Nghĩa là hai nhóm đó chưa bao giờ được chấm.
    """
    benh = mau["benh_nghi"]
    lien_quan = [p for p in ps if _co(benh, _gop(p))]
    if not lien_quan:
        return False, f"bo han thong tin nghi {benh}"
    nang = [p for p in lien_quan
            if p.get("do_chac_chan", "chắc chắn") == "chắc chắn"]
    if nang and not any(p.get("do_chac_chan") == "nghi ngờ"
                        for p in lien_quan):
        return False, f"nang 'nghi {benh}' thanh chan doan chac chan"
    return True, ""


# ═══ kiem_nhat_quan() — Kiểm thuốc đã ngưng không còn ở dạng đang dùng ════════════════
# Cần dấu vết ngưng: trạng thái bị thay thế hoặc nội dung nói ngừng.
def kiem_nhat_quan(mau, ps):
    """Thách thức 5 — thuốc ĐÃ NGƯNG không được còn ở dạng 'đang dùng'.

    Loại lỗi này không phép đo nào trong dự án bắt được trước 09/09/2026:
    ROUGE đếm từ nên hai câu đều khớp, điểm quy gán chỉ xét chủ thể, và sáu
    nhóm bẫy cũ đều chỉ xét MỘT câu một.
    """
    thuoc = mau["thuoc_da_ngung"]
    lien_quan = [p for p in ps if _co(thuoc, _gop(p))]
    if not lien_quan:
        return False, f"bo han thuoc {thuoc}"
    # Đã ngưng thì phải có dấu vết của việc ngưng: trạng thái bị thay thế,
    # hoặc chính nội dung nói rõ là đã ngưng.
    co_dau_vet = any(
        p.get("trang_thai") not in (None, "còn hiệu lực")
        or re.search(r"(?i)(đã )?ngừng|ngưng|thôi không|dừng", _gop(p))
        for p in lien_quan)
    if not co_dau_vet:
        return False, f"ghi {thuoc} ma khong ghi la DA NGUNG"
    return True, ""


PHEP_KIEM = {
    "chu_the": kiem_chu_the, "chac_chan": kiem_chac_chan,
    "dinh_chinh": kiem_dinh_chinh, "dien_bien": kiem_dien_bien,
    "gia_dinh": kiem_gia_dinh, "moi_bia": kiem_moi_bia, "sach": kiem_sach,
    "nghi_ngo": kiem_nghi_ngo, "nhat_quan": kiem_nhat_quan,
}


# ═══ cham() — Chấm một mẫu theo phép kiểm của bẫy tương ứng ═══════════════════════════
# Không có mệnh đề nào thì không đạt.
def cham(mau, ps):
    if not ps:
        return False, "khong co phat bieu nao"
    return PHEP_KIEM[mau["bay"]](mau, ps)


# ═══ cham_lai() — Chấm lại từ tệp đã lưu, không chạy mô hình ══════════════════════════
# Báo lỗi nếu tệp cũ thiếu mệnh đề thô.
def cham_lai(duong_dan_json):
    """Chấm lại từ dữ liệu đã lưu, không chạy lại mô hình."""
    chi_tiet = json.loads(open(duong_dan_json, encoding="utf-8").read())
    theo_bay = {}
    for c in chi_tiet:
        if "phat_bieu" not in c:
            raise SystemExit("Tep cu khong luu phat bieu tho — phai chay lai mo hinh")
        dat, ly_do = cham(c["dap_an"], c["phat_bieu"] or [])
        c["dat"], c["ly_do"] = dat, ly_do
        c["loi_cheo"] = kiem_cheo(c["dap_an"], c["phat_bieu"] or [])
        theo_bay.setdefault(c["bay"], []).append(dat)
    return chi_tiet, theo_bay


# ═══ in_kiem_cheo() — In riêng khối kiểm chéo ═════════════════════════════════════════
def in_kiem_cheo(chi_tiet):
    """In RIÊNG khối bảng tình huống. Gộp vào một con số là giấu mất nó."""
    tong_pb = sum(len(c["phat_bieu"] or []) for c in chi_tiet)
    tong_cheo = sum(len(c.get("loi_cheo") or []) for c in chi_tiet)
    print("")
    print("Kiem CHEO (chay tren moi mau, khong phu thuoc tinh huong):")
    print(f"  {tong_cheo}/{tong_pb} ban ghi gan sai chu the "
          f"= {100 * tong_cheo / max(1, tong_pb):.0f}%")
    print("  Bang tinh huong o tren chi do BAY RIENG cua tung tinh huong.")
    print("  Mot mo hinh tranh duoc ca bay bay van co the sai o cho khac.")


# ═══ in_bang() — In bảng đạt theo từng tình huống bẫy ═════════════════════════════════
def in_bang(theo_bay):
    from src.bo_du_lieu import sinh_bo_chan_doan as sinh_bo_chan_doan
    print(f"\n{'Tinh huong':14}{'Dat':>8}{'Ty le':>9}")
    for bay in sinh_bo_chan_doan.BAY:
        ds = theo_bay.get(bay, [])
        if ds:
            print(f"{bay:14}{sum(ds):>4}/{len(ds):<3}{100*sum(ds)/len(ds):>8.0f}%")
    tong = [d for ds in theo_bay.values() for d in ds]
    print(f"{'TONG':14}{sum(tong):>4}/{len(tong):<3}{100*sum(tong)/len(tong):>8.0f}%")


# ═══ main() — Chạy dòng lệnh đo mô hình trên bộ chẩn đoán ═════════════════════════════
# Chạy mô hình hoặc chấm lại từ tệp đã lưu.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model")
    ap.add_argument("--cham-lai", help="cham lai tu tep ket qua da luu, khong chay mo hinh")
    ap.add_argument("--n", type=int, default=15, help="so mau MOI tinh huong")
    a = ap.parse_args()

    from src.bo_du_lieu import nap_du_lieu as du_lieu
    from src.he_thong import duong_dan as duong_dan
    from src.bo_du_lieu import sinh_bo_chan_doan as sinh_bo_chan_doan

    if a.cham_lai:
        dp = duong_dan.THU_MUC_KET_QUA / a.cham_lai
        chi_tiet, theo_bay = cham_lai(dp)
        print(f"Cham lai {len(chi_tiet)} mau tu {dp.name} (khong chay mo hinh)")
        in_bang(theo_bay)
        in_kiem_cheo(chi_tiet)
        dp.write_text(json.dumps(chi_tiet, ensure_ascii=False, indent=2), encoding="utf-8")
        return

    if not a.model:
        ap.error("can --model hoac --cham-lai")

    bo = sinh_bo_chan_doan.sinh_bo(a.n, seed=42)
    print(f"Do {a.model} tren {len(bo)} mau ({len(sinh_bo_chan_doan.BAY)} tinh huong x {a.n})")

    kq_tho = bakeoff.chay(a.model, bo, ep_json=True)

    theo_bay = {}
    chi_tiet = []
    for mau, kq in zip(bo, kq_tho):
        ps = kq["phat_bieu"] or []
        dat, ly_do = cham(mau, ps)
        loi_cheo = kiem_cheo(mau, ps)
        theo_bay.setdefault(mau["bay"], []).append(dat)
        # Lưu cả PHÁT BIỂU THÔ và ĐÁP ÁN của mẫu: nếu phép chấm sai và phải
        # sửa, chấm lại được offline mà không phải chạy lại mô hình (mất 20 phút).
        chi_tiet.append({"id": mau["id"], "bay": mau["bay"], "dat": dat,
                         "ly_do": ly_do, "json_hop_le": kq["json_hop_le"],
                         "loi_cheo": loi_cheo,
                         "phat_bieu": ps,
                         "dap_an": {k: v for k, v in mau.items()
                                    if k not in ("input", "output")}})

    in_bang(theo_bay)

    in_kiem_cheo(chi_tiet)

    ten = a.model.split("/")[-1].replace(".", "_")
    dp = duong_dan.THU_MUC_KET_QUA / f"chan-doan-{ten}.json"
    dp.write_text(json.dumps(chi_tiet, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nChi tiet: {dp}")


if __name__ == "__main__":
    main()
