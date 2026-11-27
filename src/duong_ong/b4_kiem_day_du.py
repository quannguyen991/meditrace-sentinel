# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 4 – Kiểm căn cứ]
Làm gì   : Kiểm bản nháp có bỏ sót mệnh đề còn hiệu lực nào không, và thêm lại chỗ sót khi
           có căn cứ trong bảng mệnh đề.
Vào → Ra : danh sách mệnh đề + văn bản bản nháp → mệnh đề được thể hiện / bị bỏ sót theo
           nhóm; bản nháp đã bổ sung; tỉ lệ
Đọc từ   : doi_chieu() so mệnh đề với bản nháp theo bốn nhóm; bo_sung() thêm lại mệnh đề bị
           sót
Mục lục (các hàm/lớp chính):
  doi_chieu()  Đối chiếu mệnh đề với bản nháp theo bốn nhóm
  bo_sung()    Thêm lại mệnh đề bị bỏ sót vào bản nháp
  ty_le()      Tính tỉ lệ thể hiện, bỏ sót giữa các nhánh
Gọi tới  : duong_ong/b5_viet_ban_nhap
Dùng bởi : duong_ong/chay_duong_ong, duong_ong/chay_nhanh_e
Tên cũ   : kiem_day_du.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đo độ ĐẦY ĐỦ: bản nháp có bỏ sót phát biểu nào không.

Giảm câu sai chưa đủ. Một hệ thống không bao giờ ghi sai vì nó không ghi gì
thì vô dụng. Nên phải đo thêm chiều ngược lại: mỗi phát biểu `con hieu luc`
có vào được bản nháp không.

GIỚI HẠN THẬT CỦA PHÉP ĐO NÀY — phải ghi vào báo cáo, không được giấu:

    Nó đối chiếu bản nháp với BẢNG PHÁT BIỂU, không với hội thoại. Nếu khâu
    trích xuất đã bỏ sót ngay từ đầu thì bảng phát biểu cũng thiếu, và phép
    đo này báo "đầy đủ" trong khi thông tin đã mất.

    Vì thế đánh giá cuối VẪN phải đối chiếu với hội thoại và nhãn chuyên gia.
    Phép đo này chỉ bắt được một loại lỗi: mất mát ở khâu SINH, sau khi đã
    trích được.

Nguyên tắc bổ sung: chỉ bổ sung khi CÓ BẰNG CHỨNG trong bảng phát biểu.
Không tự thêm mục khám hay kết quả mà hội thoại chưa cung cấp.
"""
import re

from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an


# ─── _chuan() — Chuẩn hoá khoảng trắng và chữ thường ──────────────────────────────────
def _chuan(s):
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


# ─── _co_trong() — Kiểm cụm có trong văn bản theo ranh giới từ ────────────────────────
# Xét ranh giới ở cả hai đầu để "ho" không khớp vào "cho".
def _co_trong(cum, van_ban):
    """So theo ranh giới từ ở CẢ HAI bên — giống `do_bo_chan_doan._co`.

    Chặn một bên thôi thì "ho" khớp vào đuôi chữ "cho", và phép đo báo
    "đã thể hiện" cho một nội dung chưa hề xuất hiện.
    """
    cum = _chuan(cum)
    if not cum:
        return False
    return re.search(rf"(?<![\wÀ-ỹ]){re.escape(cum)}(?![\wÀ-ỹ])",
                     van_ban or "", re.I) is not None


# ─── _bo_muc() — Cắt một mục (tiêu đề và nội dung) khỏi bản nháp ──────────────────────
def _bo_muc(van_ban, ten_muc):
    """Cắt bỏ một mục (tiêu đề + nội dung) khỏi bản nháp."""
    khoi = (van_ban or "").split("\n\n")
    ra, i = [], 0
    while i < len(khoi):
        if khoi[i].strip() == ten_muc:
            i += 2                                   # bỏ cả tiêu đề lẫn nội dung
            continue
        ra.append(khoi[i])
        i += 1
    return "\n\n".join(ra)


# ═══ doi_chieu() — Đối chiếu mệnh đề với bản nháp theo bốn nhóm ═══════════════════════
# Đã thể hiện, bỏ sót, lặp, cần xác nhận; mỗi nhóm là danh sách mã mệnh đề.
def doi_chieu(phat_bieu, van_ban):
    """-> dict bốn nhóm, mỗi nhóm là danh sách id phát biểu.

        da_the_hien     nội dung có trong bản nháp
        bo_sot          phát biểu còn hiệu lực mà nội dung KHÔNG có trong bản nháp
        lap             nội dung xuất hiện nhiều hơn một lần
        can_xac_nhan    phát biểu đã bị chuyển sang mục cần xác nhận
    """
    than = (van_ban or "").split("CẦN XÁC NHẬN")[0]
    duoi = (van_ban or "").split("CẦN XÁC NHẬN")[1] if "CẦN XÁC NHẬN" in (van_ban or "") else ""
    # Đếm lặp thì PHẢI bỏ mục LÝ DO KHÁM BỆNH ra. Mục đó nhắc lại nguyên văn
    # triệu chứng chính từ BỆNH SỬ HIỆN TẠI — đó là dạng bệnh án thông thường,
    # không phải lỗi lặp. Không bỏ thì triệu chứng chính luôn bị báo lặp.
    than_dem_lap = _bo_muc(than, "LÝ DO KHÁM BỆNH")

    ra = {"da_the_hien": [], "bo_sot": [], "lap": [], "can_xac_nhan": []}
    for p in phat_bieu:
        d = p.to_dict() if hasattr(p, "to_dict") else dict(p)
        nd = _chuan(d.get("noi_dung"))
        if d.get("trang_thai", "còn hiệu lực") != "còn hiệu lực":
            continue                                   # bản bị thay thế: không tính
        # Xét THÂN trước rồi mới đến mục cần xác nhận. Nếu xét ngược lại thì
        # hai bản ghi cùng nội dung — một còn hiệu lực, một bị thay thế — sẽ
        # bị gộp: bản còn hiệu lực khớp vào mục cần xác nhận của bản kia và
        # biến mất khỏi `da_the_hien`.
        if _co_trong(nd, than):
            ra["da_the_hien"].append(d.get("id"))
            so_lan = len(re.findall(
                rf"(?<![\wÀ-ỹ]){re.escape(nd)}(?![\wÀ-ỹ])", than_dem_lap, re.I))
            if so_lan > 1:
                ra["lap"].append(d.get("id"))
        elif _co_trong(nd, duoi):
            ra["can_xac_nhan"].append(d.get("id"))
        else:
            ra["bo_sot"].append(d.get("id"))
    return ra


# ═══ bo_sung() — Thêm lại mệnh đề bị bỏ sót vào bản nháp ══════════════════════════════
# Chỉ lấy từ bảng, không để mô hình viết thêm; trả về (văn bản mới, mã đã thêm).
def bo_sung(phat_bieu, van_ban, id_benh_nhan=0, ten_chu_the=None):
    """Thêm lại các phát biểu bị bỏ sót — CHỈ những cái có trong bảng.

    Trả về (van_ban_moi, danh_sach_id_da_them).

    Không sinh chữ mới: dùng đúng `sinh_benh_an.dien_dat` như khâu sinh, rồi
    nối vào đúng mục mà bảng tra chỉ định. Nếu để mô hình viết phần bổ sung
    thì chính chỗ này lại thành nguồn bịa thông tin.
    """
    ket = doi_chieu(phat_bieu, van_ban)
    thieu = set(ket["bo_sot"])
    if not thieu:
        return van_ban, []

    ten_chu_the = ten_chu_the or {}
    theo_muc, da_them = {}, []
    for p in phat_bieu:
        d = p.to_dict() if hasattr(p, "to_dict") else dict(p)
        if d.get("id") not in thieu:
            continue
        muc, ly_do = sinh_benh_an._muc_cho(d, id_benh_nhan)
        ten = ten_chu_the.get(d.get("chu_the_id")) \
            if d.get("chu_the_id") != id_benh_nhan else None
        cum = sinh_benh_an.dien_dat(d, ten)
        if ly_do:
            cum = f"{cum} — {ly_do}"
        theo_muc.setdefault(muc, []).append(cum)
        da_them.append(d.get("id"))

    khoi = (van_ban or "").split("\n\n")
    ra = []
    i = 0
    while i < len(khoi):
        ra.append(khoi[i])
        ten_muc = khoi[i].strip()
        if ten_muc in theo_muc and i + 1 < len(khoi):
            ra.append(khoi[i + 1].rstrip(".") + ". " + ". ".join(theo_muc.pop(ten_muc)) + ".")
            i += 2
            continue
        i += 1
    for muc in sinh_benh_an.THU_TU_MUC:
        if muc in theo_muc:
            ra.append(muc)
            ra.append(". ".join(theo_muc.pop(muc)) + ".")
    return "\n\n".join(ra), da_them


# ═══ ty_le() — Tính tỉ lệ thể hiện, bỏ sót giữa các nhánh ═════════════════════════════
# Mẫu số là số mệnh đề còn hiệu lực; None nếu mẫu số bằng 0.
def ty_le(phat_bieu, van_ban):
    """Một số để theo dõi giữa các nhánh. Mẫu số là số phát biểu còn hiệu lực."""
    k = doi_chieu(phat_bieu, van_ban)
    mau_so = len(k["da_the_hien"]) + len(k["bo_sot"]) + len(k["can_xac_nhan"])
    if mau_so == 0:
        return None
    return {"con_hieu_luc": mau_so,
            "da_the_hien": len(k["da_the_hien"]),
            "bo_sot": len(k["bo_sot"]),
            "can_xac_nhan": len(k["can_xac_nhan"]),
            "ty_le_day_du": len(k["da_the_hien"]) / mau_so}
