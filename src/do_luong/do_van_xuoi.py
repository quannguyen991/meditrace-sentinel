# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Đo một bệnh án văn xuôi trên bộ chẩn đoán có mắc đúng lỗi bẫy không, không dùng
           thước đo nào, để so nhánh A với nhánh C.
Vào → Ra : tệp bản nháp văn xuôi (--tep) + bộ chẩn đoán (--n) → bảng đạt/hỏng theo loại bẫy
Đọc từ   : cham() chọn phép kiểm đúng bẫy của ca; cham_tep() chấm cả bộ và gom theo bẫy
Mục lục (các hàm/lớp chính):
  cham()            Chấm một bản nháp bằng phép kiểm đúng bẫy của ca
  cham_tep()        Chấm cả bộ ca chẩn đoán và gom theo bẫy
  kiem_chu_the()    Kiểm tra dị ứng người nhà không bị gán cho trẻ
  kiem_dien_bien()  Kiểm tra bản nháp giữ cả hai mốc diễn biến
  kiem_nghi_ngo()   Kiểm tra nghi ngờ không bị viết thành chẩn đoán chắc
  kiem_nhat_quan()  Kiểm tra thuốc đã ngừng không hiện như đang dùng
  in_bang()         In bảng đạt, hỏng theo từng loại bẫy
  main()            Chạy dòng lệnh chấm văn xuôi các tệp bản nháp
Gọi tới  : bo_du_lieu/sinh_bo_chan_doan, he_thong/duong_dan
Tên cũ   : do_van_xuoi.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đo MỘT BẢN BỆNH ÁN VĂN XUÔI trên bộ chẩn đoán — không dùng thước đo nào.

VÌ SAO CẦN TỆP NÀY.

Mọi phép số từ trước tới giờ đều đi qua một thước đo: ROUGE, Section F1, hay
điểm quy gán. Mà chính dự án đã chứng minh thước đo đầu tiên MÙ trước lỗi
quy gán (chung-chi-thuoc-do.md: đổi chỗ hai chủ thể không đổi một từ nào,
ROUGE-1 = 1.0000), còn thước đo thứ hai thì do dự án tự dựng ra.

Trên bộ chẩn đoán thì không cần thước đo nào hết. Hội thoại do chính đoạn mã
sinh ra, nên **đáp án đúng được biết trước**: biết dị ứng là của MẸ, biết có
hai mốc thời gian đều thật, biết triệu chứng nào không ai trả lời. Chỉ việc
đọc bản bệnh án và xem nó có phạm đúng lỗi đó không.

Đó là phép so công bằng nhất có thể có giữa nhánh A (văn xuôi) và nhánh C
(sinh từ bảng) — hai dạng văn bản rất khác nhau nhưng cùng bị hỏi một câu.

ĐỘ CHẮC CỦA TỪNG PHÉP KIỂM, phải nói rõ chứ không được trộn làm một:

  chu_the    CHẮC. Xét câu chứa tên thuốc: có từ chỉ trẻ mà không có từ chỉ
             người nhà thì là gán sai. Không phụ thuộc định dạng.
  dien_bien  CHẮC. Chỉ hỏi cả hai mốc thời gian có còn trong bản không.
  moi_bia    CHẮC. Triệu chứng không ai trả lời thì không được xuất hiện như
             một khẳng định.
  gia_dinh   VUA. Cau gia dinh phai kem dau hieu dieu kien ("neu", "nếu")
             hoặc vắng mặt. Văn xuôi có thể diễn đạt kiểu khác.
  chac_chan  VỪA. Đòi cụm "chưa ghi nhận"/"chưa từng"/"không rõ" gần triệu
             chứng. Cách diễn đạt khác sẽ bị báo oan.
  dinh_chinh VỪA. Chỉ kiểm mốc MỚI còn và mốc CŨ không được dùng như sự thật
             hiện tại.
  sach       CHẮC. Nhóm đối chứng: không được cảnh giác quá mức.
"""
import io
import json
import re
import sys

TRE = r"(?:trẻ|bé|cháu|con|em bé|bệnh nhân nhi)"
NHA = r"(?:mẹ|bố|ba|cha|má|người nhà|phụ huynh|gia đình|chị|anh)"
HEDGE = r"(?:chưa ghi nhận|chưa từng|không rõ|chưa rõ|chưa thấy|không ghi nhận)"
DIEU_KIEN = r"(?:nếu|trường hợp|khi nào|nếu như)"


# ─── _cau() — Tách văn bản thành câu, giữ cả dòng tiêu đề ─────────────────────────────
def _cau(van_ban):
    """Tách thành câu. Giữ cả dòng tiêu đề vì chúng mang thông tin mục."""
    return [c.strip() for c in re.split(r"[.\n;]", van_ban or "") if c.strip()]


# Cách diễn đạt TƯƠNG ĐƯƠNG. Phép đo này so sánh hai dạng văn bản rất khác
# nhau (văn xuôi của A và cụm ghép của C), nên nó phải phạt THÔNG TIN SAI chứ
# không phạt CÁCH DIỄN ĐẠT. Ban đầu không có bảng này, và hậu quả là:
#   - A viết "khởi phát hôm qua, HIỆN TẠI đã hết" -> bị báo vụt mất mốc sau,
#     dù nó giữ cả hai mốc. dien_bien tụt xuống 1/15.
#   - C ghi "đau bụng (4 ngày) - trạng thái BỊ THAY THẾ" -> bị báo không đánh
#     dấu đính chính, dù đó đúng là đánh dấu. dinh_chinh tụt xuống 0/15.
# Cả hai đều là lỗi của phép chấm, không phải của mô hình.
TUONG_DUONG = {
    "hôm nay": ("hôm nay", "hiện tại", "hiện nay", "nay"),
    "hôm qua": ("hôm qua", "ngày hôm qua", "hôm trước", "khởi phát hôm qua"),
}

# Mọi cách đánh dấu một thông tin đã bị thay thế đều được chấp nhận — điều
# cần là người đọc biết bản nào còn hiệu lực, không phải là dùng từ nào.
DANH_DAU_THAY_THE = r"(?:đính chính|sửa lại|thực tế là|ban đầu|bị thay thế|"                     r"đã sửa|cần xác nhận|thay bằng|không còn đúng)"


# ─── _cum_tuong_duong() — Lấy các cách diễn đạt tương đương của một cụm ───────────────
# Tra bảng tương đương, ví dụ hôm nay và hiện tại; không có thì giữ cụm gốc.
def _cum_tuong_duong(cum):
    khoa = (cum or "").strip().lower()
    return TUONG_DUONG.get(khoa, (cum,))


# ─── _co_y() — Kiểm tra văn bản có ý của cụm, không cần đúng chữ ──────────────────────
def _co_y(cum, van):
    """Có Ý NGHĨA của cụm, không đòi đúng chữ."""
    return any(_co(x, van) for x in _cum_tuong_duong(cum))


# ─── _co() — Kiểm tra cụm xuất hiện nguyên từ trong văn bản ───────────────────────────
def _co(cum, van):
    if not cum:
        return False
    return re.search(rf"(?<![\wÀ-ỹ]){re.escape(cum)}(?![\wÀ-ỹ])", van or "",
                     re.I) is not None


# ═══ kiem_chu_the() — Kiểm tra dị ứng người nhà không bị gán cho trẻ ══════════════════
# Câu có tên thuốc mà nhắc trẻ không nhắc người nhà là gán sai; không nhắc thuốc là sót.
def kiem_chu_the(mau, van):
    """Dị ứng của NGƯỜI NHÀ không được gán cho TRẺ.

    Xét từng câu chứa tên thuốc. Câu nhắc tới trẻ mà không nhắc người nhà
    thì là gán sai. Nếu tên thuốc không xuất hiện ở đâu thì tính là BỎ SÓT,
    khác với gán sai — báo cáo riêng.
    """
    thuoc = mau["thuoc"]
    lien_quan = [c for c in _cau(van) if _co(thuoc, c)]
    if not lien_quan:
        return None, f"khong nhac toi {thuoc}"
    for c in lien_quan:
        co_tre = re.search(TRE, c, re.I) is not None
        co_nha = re.search(NHA, c, re.I) is not None
        if co_tre and not co_nha:
            return False, f"gan {thuoc} cho tre: {c[:70]}"
    return True, ""


# ═══ kiem_dien_bien() — Kiểm tra bản nháp giữ cả hai mốc diễn biến ════════════════════
# Vứt mốc đầu hay mốc sau đều bị tính hỏng; không nhắc mốc nào thì không kết luận.
def kiem_dien_bien(mau, van):
    """Hai mốc đều thật. Vụt một mốc là mất thông tin."""
    cu, moi = mau["moc_cu"], mau["moc_moi"]
    co_cu, co_moi = _co_y(cu, van), _co_y(moi, van)
    if co_cu and co_moi:
        return True, ""
    if co_moi and not co_cu:
        return False, f"vut moc dau ({cu})"
    if co_cu and not co_moi:
        return False, f"vut moc sau ({moi})"
    return None, "khong nhac toi moc nao"


# ═══ kiem_moi_bia() — Kiểm tra triệu chứng bỏ ngỏ không bị khẳng định ═════════════════
# Câu nhắc triệu chứng phải có dấu hiệu chưa rõ hoặc phủ định mới được chấp nhận.
def kiem_moi_bia(mau, van):
    """Triệu chứng không ai trả lời thì không được khẳng định."""
    moi = mau["moi_khong_duoc_tra_loi"]
    lien_quan = [c for c in _cau(van) if _co(moi, c)]
    if not lien_quan:
        return True, ""
    for c in lien_quan:
        if re.search(HEDGE, c, re.I) or re.search(r"(?i)không có|phủ định", c):
            continue                       # có đánh dấu là chưa rõ thì chấp nhận
        return False, f"khang dinh '{moi}' du khong ai tra loi: {c[:70]}"
    return True, ""


# ═══ kiem_gia_dinh() — Kiểm tra câu giả định không thành triệu chứng đã xảy ra ════════
# Câu nhắc điều kiện phải có từ chỉ giả định như nếu, trường hợp.
def kiem_gia_dinh(mau, van):
    """Câu giả định không được thành triệu chứng đã xảy ra."""
    dk = mau["dieu_kien"]
    lien_quan = [c for c in _cau(van) if _co(dk, c)]
    if not lien_quan:
        return True, ""
    for c in lien_quan:
        if not re.search(DIEU_KIEN, c, re.I):
            return False, f"ghi '{dk}' nhu trieu chung that: {c[:70]}"
    return True, ""


# ═══ kiem_chac_chan() — Kiểm tra "chưa thấy" không thành phủ định chắc ════════════════
# Hỏng nếu có cụm sai hoặc không giữ được mức chưa ghi nhận.
def kiem_chac_chan(mau, van):
    """"Chưa thấy bị bao giờ" không được thành phủ định chắc chắn."""
    tc, sai = mau["trieu_chung"], mau["cum_sai"]
    if _co(sai, van):
        return False, f"nang thanh phu dinh chac chan: '{sai}'"
    lien_quan = [c for c in _cau(van) if _co(tc, c)]
    if not lien_quan:
        return None, f"khong nhac toi {tc}"
    if any(re.search(HEDGE, c, re.I) for c in lien_quan):
        return True, ""
    return False, "khong giu duoc muc 'chua ghi nhan'"


# ═══ kiem_dinh_chinh() — Kiểm tra mốc mới còn và mốc cũ được đánh dấu thay thế ════════
# Mất mốc mới là hỏng; giữ cả hai mốc mà không đánh dấu thay thế cũng hỏng.
def kiem_dinh_chinh(mau, van):
    """Mốc MỚI phải còn. Mốc CŨ không được dùng như sự thật hiện tại."""
    cu, moi = mau["moc_cu"], mau["moc_moi"]
    if not _co_y(moi, van):
        return False, f"mat moc da dinh chinh ({moi})"
    if _co_y(cu, van):
        # Đánh dấu có thể ở chính câu đó, hoặc ở tiêu đề mục ngay trên nó.
        khoi = re.split(r"\n\s*\n", van or "")
        co_danh_dau = any(re.search(DANH_DAU_THAY_THE, k, re.I)
                          for k in khoi if _co_y(cu, k))
        if not co_danh_dau:
            return False, f"giu ca hai moc ({cu} va {moi}) khong danh dau"
    return True, ""


DANG_DUNG = r"(?:đang dùng|đang uống|hiện dùng|hiện đang|vẫn dùng|vẫn uống|"             r"tiếp tục dùng|duy trì)"
DA_NGUNG = r"(?:đã ngừng|ngừng|đã dừng|dừng|đã bỏ|không còn dùng|thôi dùng)"
MUC_DANG_DUNG = "THUỐC ĐANG DÙNG"


NGHI = r"(?:nghi|nghi ngờ|theo dõi|chưa kết luận|chưa xác định|chờ kết quả|" \
       r"cần thêm|hướng tới|nghĩ nhiều đến)"


# ═══ kiem_nghi_ngo() — Kiểm tra nghi ngờ không bị viết thành chẩn đoán chắc ═══════════
# Tách ba lỗi: nâng mức, bỏ sót tên bệnh, bản rỗng. Chỉ xét câu có tên bệnh.
def kiem_nghi_ngo(mau, van):
    """Thách thức 3 — NGHI NGỜ không được thành CHẨN ĐOÁN XÁC ĐỊNH.

    Ba cách hỏng, bắt riêng vì cần ba cách sửa khác nhau:

      1. có tên bệnh nhưng KHÔNG có từ đánh dấu mục nghi   -> NÂNG MỨC
      2. không nhắc tên bệnh nào cả                         -> BỎ SÓT
      3. bản rỗng                                           -> bỏ sót hoàn toàn

    Cách 1 là cái bẫy chính. Cách 2 phải tách ra: gộp chung thì một bản im
    lặng hoàn toàn sẽ đạt điểm tuyệt đối ở phép kiểm này — đúng cái bẫy "giảm
    lỗi bằng cách viết ít đi" mà cả dự án đi chặn.

    Chú ý về phạm vi: chỉ xét CÂU có tên bệnh, không xét cả bản. Một bản có
    thể ghi đúng "nghi viêm phổi" ở mục CHẨN ĐOÁN và vẫn có chữ "viêm phổi"
    ở chỗ khác mà không sai.
    """
    benh = mau["benh_nghi"]
    if not (van or "").strip():
        return False, "ban rong"
    if not _co(benh, van):
        return False, f"bo sot: khong nhac toi {benh}"

    for c in _cau(van):
        if not _co(benh, c):
            continue
        if not re.search(NGHI, c, re.I):
            return False, f"ghi {benh} nhu chan doan xac dinh"
    return True, ""


# ═══ kiem_nhat_quan() — Kiểm tra thuốc đã ngừng không hiện như đang dùng ══════════════
# Bắt lỗi sai vị trí (mục thuốc đang dùng) và sai diễn đạt; bỏ sót thì báo riêng.
def kiem_nhat_quan(mau, van):
    """Thách thức 5. Thuốc ĐÃ NGƯNG không được xuất hiện như thuốc ĐANG DÙNG.

    Hai cách hỏng được bắt riêng, vì chúng cần hai cách sửa khác nhau:

      1. thuốc nằm trong mục THUỐC ĐANG DÙNG        -> sai VỊ TRÍ
      2. một khối nói "đang dùng" thuốc đó          -> sai DIỄN ĐẠT

    Và một cách hỏng thứ ba: bản KHÔNG NHẮC tới thuốc nào cả. Đó là bỏ sót,
    không phải mâu thuẫn — báo riêng chứ không gộp vào, nếu không thì một bản
    rỗng sẽ đạt điểm tuyệt đối ở phép kiểm này.
    """
    thuoc = mau["thuoc_da_ngung"]
    if not (van or "").strip():
        return False, "ban rong"
    if not _co(thuoc, van):
        return False, f"bo sot: khong nhac toi {thuoc}"

    khoi = re.split(r"\n\s*\n", van)
    # 1. Nằm dưới tiêu đề THUỐC ĐANG DÙNG?
    muc_hien = ""
    for k in khoi:
        dong_dau = k.strip().split("\n")[0].strip()
        if dong_dau and not any(c.islower() for c in dong_dau):
            muc_hien = dong_dau
        if _co(thuoc, k) and MUC_DANG_DUNG in muc_hien:
            return False, f"{thuoc} da ngung nhung nam o muc {MUC_DANG_DUNG}"

    # 2. Câu nào nói thuốc đó ĐANG dùng mà không nói đã ngưng?
    for c in _cau(van):
        if not _co(thuoc, c):
            continue
        if re.search(DANG_DUNG, c, re.I) and not re.search(DA_NGUNG, c, re.I):
            return False, f"ghi {thuoc} nhu thuoc dang dung"
    return True, ""


# ═══ kiem_sach() — Đối chứng sạch: không cảnh giác quá mức ════════════════════════════
# Hỏng nếu bản rỗng hoặc báo động giả trên hội thoại bình thường.
def kiem_sach(mau, van):
    """Đối chứng: không được cảnh giác quá mức trên hội thoại bình thường."""
    if not (van or "").strip():
        return False, "ban rong"
    if re.search(HEDGE, van, re.I):
        return False, "bao dong gia tren hoi thoai binh thuong"
    return True, ""


PHEP_KIEM = {
    "chu_the": kiem_chu_the, "chac_chan": kiem_chac_chan,
    "dinh_chinh": kiem_dinh_chinh, "dien_bien": kiem_dien_bien,
    "gia_dinh": kiem_gia_dinh, "moi_bia": kiem_moi_bia,
    "nghi_ngo": kiem_nghi_ngo,
    "nhat_quan": kiem_nhat_quan, "sach": kiem_sach,
}

# Phép kiểm nào chắc, phép kiểm nào chỉ là xấp xỉ trên văn xuôi.
DO_CHAC = {"chu_the": "chắc", "dien_bien": "chắc", "moi_bia": "chắc",
           "sach": "chắc", "nhat_quan": "chắc", "nghi_ngo": "chắc",
           "gia_dinh": "vừa",
           "chac_chan": "vừa", "dinh_chinh": "vừa"}


# ═══ cham() — Chấm một bản nháp bằng phép kiểm đúng bẫy của ca ════════════════════════
# Trả (đạt, lý do); đạt là None nếu không kết luận được.
def cham(mau, van):
    """-> (dat, ly_do). `dat` có thể là None = không kết luận được."""
    return PHEP_KIEM[mau["bay"]](mau, van)


# ═══ cham_tep() — Chấm cả bộ ca chẩn đoán và gom theo bẫy ═════════════════════════════
# Trả chi tiết từng ca và danh sách kết quả theo từng loại bẫy.
def cham_tep(bo, ban):
    """bo: danh sách mẫu chẩn đoán. ban: {id: van_ban}. -> (chi_tiet, theo_bay)."""
    chi_tiet, theo_bay = [], {}
    for m in bo:
        dat, ly_do = cham(m, ban.get(m["id"], ""))
        chi_tiet.append({"id": m["id"], "bay": m["bay"], "dat": dat,
                         "ly_do": ly_do})
        theo_bay.setdefault(m["bay"], []).append(dat)
    return chi_tiet, theo_bay


# ═══ in_bang() — In bảng đạt, hỏng theo từng loại bẫy ═════════════════════════════════
# Mỗi bẫy kèm độ chắc của phép kiểm và tỉ lệ đạt; có dòng tổng.
def in_bang(theo_bay, ten=""):
    from src.bo_du_lieu import sinh_bo_chan_doan as sinh_bo_chan_doan
    print(f"\n{ten}")
    print(f"{'Tinh huong':13}{'do chac':>9}{'dat':>8}{'hong':>6}{'?':>4}{'ty le':>8}")
    tong_dat = tong_hong = 0
    for bay in sinh_bo_chan_doan.BAY:
        ds = theo_bay.get(bay, [])
        if not ds:
            continue
        dat = sum(1 for x in ds if x is True)
        hong = sum(1 for x in ds if x is False)
        khong_ro = sum(1 for x in ds if x is None)
        tong_dat += dat
        tong_hong += hong
        ty = f"{100 * dat / (dat + hong):.0f}%" if dat + hong else "—"
        print(f"{bay:13}{DO_CHAC[bay]:>9}{dat:>8}{hong:>6}{khong_ro:>4}{ty:>8}")
    ty = f"{100 * tong_dat / (tong_dat + tong_hong):.0f}%" if tong_dat + tong_hong else "—"
    print(f"{'TONG':13}{'':>9}{tong_dat:>8}{tong_hong:>6}{'':>4}{ty:>8}")


# ═══ main() — Chạy dòng lệnh chấm văn xuôi các tệp bản nháp ═══════════════════════════
# Sinh bộ chẩn đoán cố định, chấm từng tệp, rồi ghi JSON chi tiết.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--tep", nargs="+", required=True,
                    help="ten tep trong data/, vd ra_A_bo_chan_doan.jsonl")
    ap.add_argument("--n", type=int, default=15)
    a = ap.parse_args()

    from src.he_thong import duong_dan as duong_dan
    from src.bo_du_lieu import sinh_bo_chan_doan as sinh_bo_chan_doan

    bo = sinh_bo_chan_doan.sinh_bo(a.n, seed=42)
    for t in a.tep:
        dp = duong_dan.THU_MUC_DU_LIEU / t
        if not dp.exists():
            print(f"(chua co {t})")
            continue
        ban = {json.loads(x)["id"]: json.loads(x)["du_doan"]
               for x in open(dp, encoding="utf-8") if x.strip()}
        chi_tiet, theo_bay = cham_tep(bo, ban)
        in_bang(theo_bay, ten=t)
        (duong_dan.THU_MUC_KET_QUA / f"van-xuoi-{t}.json").write_text(
            json.dumps(chi_tiet, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
