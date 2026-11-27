# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 5 – Xếp chỗ]
Làm gì   : Viết bản nháp hồ sơ từ bảng mệnh đề bằng mẫu câu cố định, không dùng mô hình, mỗi
           mệnh đề vào đúng một mục.
Vào → Ra : danh sách mệnh đề + mã bệnh nhân → văn bản bản nháp chia mục; tách riêng phần cần
           xác nhận
Đọc từ   : sinh() dựng cả bản nháp; dien_dat() viết một mệnh đề thành cụm chữ;
           tach_muc_phu() tách mục phụ
Mục lục (các hàm/lớp chính):
  sinh()                  Dựng bản nháp từ danh sách mệnh đề
  dien_dat()              Diễn đạt một mệnh đề thành một cụm chữ
  _muc_cho()              Chọn mục bản nháp cho một mệnh đề
  tach_muc_phu()          Tách bản nháp thành bệnh án và phần cần xác nhận
  _them_chi_tiet_thuoc()  Chèn liều, đường dùng, số lần ngay sau tên thuốc
Gọi tới  : duong_ong/b1_cau_truc_menh_de
Dùng bởi : do_luong/cham_he_thong, do_luong/cham_muc_thach_thuc, do_luong/chuan_dinh_dang,
           do_luong/do_canh_bao, do_luong/do_neu_ten, do_luong/doi_chung_tam_thuong,
           do_luong/duong_danh_doi, bo_du_lieu/nap_bo_nguoi_that … (tổng 16 tệp)
Tên cũ   : sinh_benh_an.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Sinh bệnh án TỪ BẢNG PHÁT BIỂU bằng luật, không bằng mô hình.

Đây là chỗ dự án chặn lỗi quy gán. Nếu để mô hình tự do viết lại cả tập phát
biểu thành văn xuôi, nó sẽ gộp hai phát biểu KHÁC CHỦ THỂ thành một câu —
và đó đúng là lỗi mà dự án đang muốn chặn. Nên bước này là mã, không phải
mô hình: mỗi phát biểu đi vào đúng một mục, theo bảng tra cố định.

Hai luật không được phá:

  1. Phát biểu có chủ thể KHÔNG PHẢI bệnh nhân thì KHÔNG được vào các mục nói
     về bệnh nhân. Dị ứng của mẹ thuộc TIỀN SỬ GIA ĐÌNH, không thuộc DỊ ỨNG.

  2. "chưa ghi nhận" phải ra chữ "chưa ghi nhận". Biến nó thành "không có" là
     biến một chỗ TRỐNG thành một khẳng định ÂM — hai chuyện khác hẳn nhau
     về mặt lâm sàng.

Phát biểu không đủ điều kiện (bị thay thế, giả định, kế hoạch, thiếu bằng
chứng) không bị vứt đi — nó xuống mục CẦN XÁC NHẬN, kèm lý do.
"""
import re

from src.duong_ong import b1_cau_truc_menh_de as phat_bieu

MUC_BENH_NHAN = "__benh_nhan__"      # đánh dấu mục chỉ dành cho bệnh nhân

# Tên mục phải lấy từ VỐN TỪ CỦA CHÍNH BỘ DỮ LIỆU, không được tự đặt.
# Ban đầu tôi đặt là "TIỀN SỬ GIA ĐÌNH". Tên đó xuất hiện 0 lần trong 35 bản
# tham chiếu của tập phát triển, nên 22 lần sinh ra đều là dương tính giả,
# và 8 mục thật bị tính là bỏ sót. Chọn lại theo tần suất trong TẬP TRAIN
# (không nhìn tập phát triển): 376 lần "VÀ XÃ HỘI" so với 178 lần không.
MUC_NGUOI_KHAC = "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI"

# Nhân viên y tế KHÔNG phải chủ thể lâm sàng. "Bác sĩ: khó khai thác thêm
# thông tin bệnh sử" không phải tiền sử của bác sĩ. Ban đầu mọi phát biểu có
# chủ thể khác bệnh nhân đều bị đẩy vào mục tiền sử gia đình, kể cả 16 phát
# biểu có chủ thể là bác sĩ — vừa sai về ý nghĩa vừa sinh ra mục thừa.
# MỘT định nghĩa duy nhất, đặt ở `phat_bieu` — xem chú thích ở đó. Trước
# 10/09/2026 bảng này chỉ có ở tệp này, còn `tu_json` và `sua_cuc_bo`
# không biết gì, gia là 104 câu bác sĩ bị đổi sang mục gia đình.
NHAN_VIEN_Y_TE = phat_bieu.VAI_NHAN_VIEN

# Chuỗi KHÔNG dùng làm tên người trong bản nháp: chúng là cách gọi bệnh nhân,
# nên đặt chúng trước một mệnh đề ở mục tiền sử gia đình sẽ nói sai người.
TEN_KHONG_DAT_TEN = frozenset(phat_bieu.TEN_BENH_NHAN) | {""}

# Thứ tự in ra. Theo thứ tự bệnh án thông thường, không theo thứ tự phát biểu.
THU_TU_MUC = [
    "LÝ DO KHÁM BỆNH",
    "BỆNH SỬ HIỆN TẠI",
    # Đổi tên 11/09/2026: trước đây tệp này gọi mục này là
    # "KHÁM HỆ THỐNG CÁC CƠ QUAN" trong khi bản nháp tham chiếu gọi là
    # "KHÁM LÂM SÀNG". Hai khâu dùng hai bộ tên mục khác nhau, nên đường ống
    # không thể sinh ra tên mục mà phép chấm đối chiếu: tham chiếu có nó ở 60/60
    # ca, bản nháp của nhánh B có 0. Hai chỗ khác trong dự án
    # (`sinh_hoi_thoai_viet.MUC` và `bo_nguoi_that.MUC_HOP_LE`) đều dùng
    # "KHÁM LÂM SÀNG", nên tệp này là chỗ lệch.
    "KHÁM LÂM SÀNG",
    "SINH HIỆU",
    "TIỀN SỬ BỆNH",
    "TIỀN SỬ PHẪU THUẬT",
    "DỊ ỨNG",
    "THUỐC ĐANG DÙNG",
    "TIÊM CHỦNG",
    "TIỀN SỬ XÃ HỘI",
    MUC_NGUOI_KHAC,
    "CHẨN ĐOÁN",
    "KẾ HOẠCH ĐIỀU TRỊ",
    "CẦN XÁC NHẬN",
]

# Bảng tra: (biểu thức, mục). Xét theo thứ tự, cái đầu tiên khớp thì lấy.
# Chỉ áp dụng khi chủ thể LÀ bệnh nhân — xem `_muc_cho`.
BANG_TRA = [
    # `dị ứng` phải có CÁI GÌ ĐÚNG SAU nó.
    #
    # Ban đầu là `dị ứng` trần. "Viêm mũi dị ứng" và "Viêm kết mạc dị ứng" là
    # TÊN BỆNH — tiền sử bệnh — nhưng chúng khớp và bị đẩy sang mục DỊ ỨNG. Đã
    # thấy đúng thế trên bản nháp của nhánh B: mục TIỀN SỬ BỆNH có 28/60 ca trong
    # bản tham chiếu và 0 trong bản nháp.
    #
    # Trong tên bệnh, "dị ứng" đứng ở CUỐI ("viêm mũi dị ứng"); trong một lời kể
    # dị ứng thật, nó đi kèm chất gây dị ứng ("dị ứng penicillin", "dị ứng thuốc
    # cản quang"). Nên đòi hỏi có từ đứng sau.
    (r"dị ứng\s+\S|mẫn cảm|phát ban khi (uống|dùng)", "DỊ ỨNG"),
    (r"tiêm (chủng|phòng)|vắc[- ]?xin|vaccine", "TIÊM CHỦNG"),
    (r"mổ|phẫu thuật|cắt (ruột thừa|amidan|túi mật)", "TIỀN SỬ PHẪU THUẬT"),
    (r"đang (uống|dùng|điều trị bằng)|thuốc (đang|hiện)", "THUỐC ĐANG DÙNG"),
    # Bốn mục dưới đây thêm sau khi đo: bản tham chiếu có chúng mà bộ sinh
    # không bao giờ tạo ra, nên mỗi lần xuất hiện đều bị tính là bỏ sót.
    (r"hút thuốc|thuốc lá|rượu|bia|nghề|làm việc|sống (một mình|cùng)|"
     r"học lớp|đi học|nhà trẻ", "TIỀN SỬ XÃ HỘI"),
    # `mạch`, `huyết áp` PHẢI kèm số. Trần thì "tăng huyết áp" (một BỆNH) rơi vào
    # SINH HIỆU: đo trên đáp án TẬP TRAIN 11/09/2026, 80 phát biểu tiền sử bệnh
    # bị đẩy nhầm, trong khi đáp án không có phát biểu nào ở SINH HIỆU.
    (r"nhiệt độ|mạch \d|huyết áp \d|nhịp thở|spo2|cân nặng \d|\d+ *°|\d+ *độ|"
     r"°f|°c", "SINH HIỆU"),
    (r"chẩn đoán|nghĩ nhiều đến|theo dõi (viêm|sốt|bệnh)", "CHẨN ĐOÁN"),
]

# Dấu hiệu DÙNG THUỐC trong TRÍCH DẪN — xét sau `BANG_TRA`, trên lời nói chứ
# không trên nội dung. Đo trên đáp án TẬP TRAIN 11/09/2026: 1.538 phát biểu THUỐC
# ĐANG DÙNG có nội dung chỉ là TÊN THUỐC ("salbutamol", "berberin"), và bảng tra
# trên nội dung chỉ bắt được 343. Học thuộc tên thuốc của train là lặp lại bẫy của
# bảng tên bệnh (100% train, 40% tập phát triển); cái khái quát được là ĐỘNG TỪ
# dùng thuốc trong câu nói: "tôi có uống salbutamol". Trên train mẫu này bắn
# 1.588 lần: 1.538 đúng mục, 50 là kế hoạch — đã xử lý ở `tinh_huong` trước đó.
# Trừ đồ ăn uống: "có uống sữa" là chuyện ăn, không phải thuốc.
DUNG_THUOC = re.compile(
    r"(?<!\w)(có|đang|vẫn|hay|thường|mới) (uống|dùng|xịt|bôi|nhỏ|tiêm|ngậm)"
    r"(?!\w)(?! (nước|sữa|cháo|bia|rượu|cà phê|trà)(?!\w))", re.I)

# NGÔN NGỮ KHÁM: việc người khám LÀM hoặc QUAN SÁT được.
#
# VÌ SAO CẦN, và vì sao bảng cũ không đủ — đo ngày 11/09/2026.
#
# Bản tham chiếu có `KHAM LAM SANG` ở **60/60** ca; bản nháp của nhánh B có
# **0**. Hai lý do, cả hai đều là lo~:
#
#   1. `THU_TU_MUC` của tệp này gọi mục đó là `KHAM HE THONG CAC CO QUAN`, còn
#      bản tham chiếu (`sinh_hoi_thoai_viet.MUC`) gọi là `KHAM LAM SANG`. Hai
#      khâu dùng hai BỘ TÊN MỤC khác nhau, nên đường ống KHÔNG THỂ sinh ra tên
#      mục mà phép chấm đối chiếu. Cùng với `CHAN DOAN` (40 ca tham chiếu, B có
#      0) và `TIEN SU BENH` (28 ca, B có 0).
#
#   2. Bảng cũ khớp từ khoá kiểu `khám (thấy|phổi|...)`, nhưng câu khám thật
#      không chứa từ "khám": "Bụng mềm, ấn đau nhẹ quanh rốn". Nên luật gần như
#      không bao giờ bắn, và câu khám rơi xuống `BENH SU HIEN TAI`.
#
# BẢNG NÀY CHỌN TỪ TẬP TRAIN, không từ tập đo. Đã thử cả một bảng TÊN BỆNH và
# bỏ nó: tên bệnh đạt 100% trên train nhưng chỉ 40,4% trên tập phát triển — nó
# học thuộc 45 tên bệnh của train. Ngôn ngữ khám thì khái quát được, vì nó là
# một ngữ vực đóng: 95,5% trên train, 87,6% trên tập phát triển.
#
# Luật: có dấu hiệu khám -> KHÁM LÂM SÀNG; còn lại (câu bác sĩ nói, thực tế) ->
# CHẨN ĐOÁN. Đo được 93,6% trên train và 93,4% trên tập phát triển.
# KHÔNG dùng TÊN BỘ PHẬN đơn lẻ làm dấu hiệu. Ban đầu tôi có `niêm mạc`,
# `kết mạc`, `bờ mi`, `màng nhĩ`, `amidan` trong bang, va do tren train thi
# **85 chẩn đoán bị đẩy sang mục khám**: "Viêm kết mạc cấp", "Viêm bờ mi",
# "Viêm kết mạc dị ứng" — chẩn đoán cũng được gọi theo TÊN BỘ PHẬN.
#
# Nên chỉ giữ dấu hiệu là VIỆC NGƯỜI KHÁM LÀM hoặc DẤU HIỆU QUAN SÁT ĐƯỢC. Tên
# bộ phận chỉ được dùng khi đi kèm một dấu hiệu ("niêm mạc ... nhợt").
# MỖI DẤU HIỆU Ở ĐÂY ĐỀU BẮN TRÊN TẬP TRAIN. Đã kiểm bằng cách tách từng nhánh
# của biểu thức rồi đo riêng, và đã BỎ sau dấu hiệu:
#
#   `sờ thấy`, `gan lách`, `lách to`   chi ban o TAP PHAT TRIEN — toi chon chung
#                                      từ 8 chuỗi của dev trước khi đổi sang
#                                      train, tức là nhìn vào dữ liệu đánh giá
#   `gõ (đục|vang)`, `âm tính`,        không bắn ở cả hai tập — tôi tự bịa
#   `mạch \d`
#
# Cùng lo~i đã mắc với bảng từ dẫn thường sáng hôm trước, nên lần này kiểm trước
# khi ghi số.
#
# BỔ SUNG 11/09/2026 khi bộ khuôn tăng từ 60 lên 100. Kiểm lại trên TẬP TRAIN MỚI
# (75 khuôn): 145/150 — 5 chuỗi khám của các khuôn mới không khớp. Cả 5 đều nằm ở
# TẬP TRAIN, nên bổ sung từ chúng là hợp lệ; tập phát triển đạt 26/26 và KHÔNG
# được dùng để chọn dấu hiệu:
#
#   "Da vung mong do, khong co mun mu"               -> `mụn mủ`
#   "Mang hong ban gioi han ro, phu vay trang day"    -> `hồng ban`, `phủ vảy`,
#                                                        `giới hạn rõ`
#   "Ong tai ngoai sung ne, keo vanh tai dau tang"    -> `sưng nề`
#   "Bui tri noi do hai, khong chay mau luc kham"     -> `(lúc|khi) khám`
#   "Nhan mun va san viem vung tran, ma"              -> `sẩn viêm`, `nhân mụn`
NGON_NGU_KHAM = re.compile(
    r"ấn đau|nghe (có|thấy)|\bran\b|phản ứng thành bụng"
    r"|bụng (mềm|chướng)|cương tụ|dương tính|rải rác|có vảy|vảy tiết"
    r"|mụn nước|bọng nước|sẩn (phù|viêm)|phù nề|không phù|tim đều|tiếng thổi"
    r"|nhịp thở \d|huyết áp \d|mạch nhanh|thóp|gan (không )?to"
    r"|thị lực|dấu véo da|nhợt|mụn mủ|nhân mụn|hồng ban|phủ vảy|giới hạn rõ"
    r"|(lúc|khi) khám"
    r"|không (phát hiện|dấu hiệu|dấu) (bất thường|thần kinh)"
    r"|sưng (nóng|đỏ|nhẹ|tuyến|nề)|rút lõm|thể trạng|da (ẩm|khô)"
    r"|chấm mủ|tiết dịch|vết loét|điểm đau|khu trú|ban đỏ|nổi ban"
    r"|(niêm mạc|kết mạc|giác mạc|màng nhĩ|bờ mi|amidan|họng|phổi|khớp)"
    r"[^.;]{0,30}?(đỏ|sưng|nhợt|trong|phồng|to|nề|loét|dịch|mủ|ran|không)",
    re.I)


# ─── _chuan() — Gộp khoảng trắng của chuỗi ────────────────────────────────────────────
def _chuan(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()


# ─── _la_nguoi_khac() — Kiểm người nói hoặc chủ thể là "người khác" ───────────────────
# Không phải bệnh nhân, người nhà hay nhân viên.
def _la_nguoi_khac(p):
    """Người nói hoặc chủ thể là "người khác" (không phải bệnh nhân, người nhà, nhân viên)."""
    return "người khác" in (_chuan(p.get("nguoi_noi")).lower(),
                            _chuan(p.get("ten_chu_the") or p.get("chu_the")).lower())


# ─── _la_nhan_vien() — Kiểm chủ thể của mệnh đề là nhân viên y tế ─────────────────────
def _la_nhan_vien(p):
    return phat_bieu.la_vai_nhan_vien(
        _chuan(p.get("ten_chu_the") or p.get("chu_the") or ""))


# ─── _muc_cho() — Chọn mục bản nháp cho một mệnh đề ───────────────────────────────────
# Trả về (tên mục, lý do chuyển hướng); thiếu căn cứ hoặc không còn hiệu lực thì vào CẦN
# XÁC NHẬN.
def _muc_cho(p, id_benh_nhan):
    """Chọn mục cho một phát biểu. Trả về (ten_muc, ly_do_neu_chuyen_huong)."""
    if not p.get("bang_chung"):
        return "CẦN XÁC NHẬN", "không có bằng chứng lượt thoại"
    if p.get("trang_thai", "còn hiệu lực") != "còn hiệu lực":
        return "CẦN XÁC NHẬN", f"trạng thái {p.get('trang_thai')}"

    tinh_huong = p.get("tinh_huong", "thực tế")
    hanh_vi = p.get("hanh_vi") or ""
    if tinh_huong == "giả định":
        return "CẦN XÁC NHẬN", "câu giả định, chưa xảy ra"
    if tinh_huong == "kế hoạch" or hanh_vi == "kế hoạch":
        return "KẾ HOẠCH ĐIỀU TRỊ", None

    # LUẬT 1 — chủ thể không phải bệnh nhân thì KHÔNG được vào mục của bệnh nhân.
    if p.get("chu_the_id") != id_benh_nhan:
        if _la_nhan_vien(p):
            return "CẦN XÁC NHẬN", "chủ thể là nhân viên y tế, không phải người bệnh"
        # 26/11/2026: người KHÔNG phải người nhà (vd bệnh nhân khác cùng phòng) thì
        # thông tin của họ không phải tiền sử gia đình của bệnh nhân này.
        if _la_nguoi_khac(p):
            return "CẦN XÁC NHẬN", "thông tin của người khác, không phải bệnh nhân hay người nhà"
        return MUC_NGUOI_KHAC, None

    # HÀNH VI (thế hệ 5) — LOẠI LỜI NÓI quyết định nhóm mục, trước khi xét AI nói.
    #
    # Vì sao: bác sĩ NHẮC LẠI bệnh sử ("Vậy là cháu sốt ba ngày") là câu bác sĩ
    # nói nhưng là BỆNH SỬ; luật theo người nói bên dưới đẩy nó sang CHẨN ĐOÁN.
    # Chiều ngược lại thì không tin: người nhà không khám, nên "quan sát" và
    # "nhận định" chỉ tính khi người nói là nhân viên y tế — mô hình gán nhầm
    # "quan sát" cho lời mẹ kể "cháu nói ban" thì vẫn xuống bệnh sử.
    #
    # Không có hanh_vi (đầu ra thế hệ 4, dữ liệu cũ) -> luật cũ, không đổi gì.
    # Trên đáp án tự sinh, hanh_vi và mục đó cùng một bộ sinh gắn, nên đo đúng
    # 100% ở đây là THEO THIẾT KẾ; phép đo thật là trên hanh_vi mô hình trích.
    la_nv = phat_bieu.la_vai_nhan_vien(_chuan(p.get("nguoi_noi") or ""))
    if la_nv and hanh_vi == "quan sát":
        return "KHÁM LÂM SÀNG", None
    if la_nv and hanh_vi == "nhận định":
        return "CHẨN ĐOÁN", None
    if la_nv and hanh_vi in ("trả lời", "tự kể"):
        la_nv = False               # bệnh sử do nhân viên nhắc lại

    # CÂU DO BÁC SĨ NÓI là kết quả khám hoặc chẩn đoán, không phải bệnh sử.
    #
    # Đo trên tập phát triển thế hệ 2: trong 168 phát biểu có `nguoi_noi` là bác
    # sĩ, đáp án xếp 60 vào KẾ HOẠCH ĐIỀU TRỊ (đã xử lý ở `tinh_huong` trên), 56
    # vào KHÁM LÂM SÀNG, 40 vào CHẨN ĐOÁN. Trước 11/09/2026 cả 96 câu khám và
    # chẩn đoán đều rơi xuống BỆNH SỬ HIỆN TẠI, vì bảng tra khớp từ khoá trong
    # NỘI DUNG trong khi dấu hiệu thật là AI NÓI.
    #
    # Phải xét TRƯỚC `BANG_TRA`: "Viêm mũi dị ứng" là một CHẨN ĐOÁN, nhưng bảng
    # trả khớp `dị ứng` và đẩy nó sang mục DỊ ỨNG. Đã thấy đúng thế trên bản nháp
    # của nhánh B.
    if la_nv:
        if NGON_NGU_KHAM.search(_chuan(p.get("noi_dung"))):
            return "KHÁM LÂM SÀNG", None
        return "CHẨN ĐOÁN", None

    noi_dung = _chuan(p.get("noi_dung")).lower()
    for bieu_thuc, muc in BANG_TRA:
        if re.search(bieu_thuc, noi_dung):
            return muc, None
    if any(DUNG_THUOC.search(_chuan(t)) for t in (p.get("trich_dan") or [])):
        return "THUỐC ĐANG DÙNG", None

    if p.get("thoi_gian_su_kien") == "quá khứ":
        return "TIỀN SỬ BỆNH", None
    return "BỆNH SỬ HIỆN TẠI", None


# ─── _them_chi_tiet_thuoc() — Chèn liều, đường dùng, số lần ngay sau tên thuốc ────────
# Thêm mốc bắt đầu hoặc ngừng ở cuối; chi tiết đã có sẵn thì không viết lại.
def _them_chi_tiet_thuoc(cum, t):
    """Chèn liều, đường dùng, số lần NGAY SAU TÊN THUỐC; thêm mốc bắt đầu hoặc mốc
    ngừng ở cuối. Chi tiết nào đã có trong cụm (ví dụ "đã ngừng 2 tuần" nằm sẵn
    trong nội dung) thì không viết lần hai.

        amlodipin                   ->  amlodipin 5 mg, uống ngày một lần buổi sáng (ba tháng nay)
        từng dùng omeprazole, đã ngừng 2 tuần
                                    ->  từng dùng omeprazole 20 mg, uống, đã ngừng 2 tuần

    Thêm 15/09/2026. Trước đó bản nháp chỉ in tên thuốc, nên bác sĩ đọc hồ sơ không
    biết liều nào, dùng thế nào — và lỗi sai liều không có chỗ nào để hiện ra.
    """
    thap = cum.lower()
    cach_dung = " ".join(v for v in (t.get("duong_dung"), t.get("so_lan")) if v)
    phan = [v for v in (t.get("lieu"), cach_dung) if v and v.lower() not in thap]
    ten = _chuan(t.get("ten"))
    if phan:
        chen = ", ".join(phan)
        k = thap.find(ten.lower()) if ten else -1
        if k >= 0:
            cuoi = k + len(ten)
            cum = f"{cum[:cuoi]} {chen}{cum[cuoi:]}"
        else:
            cum = f"{cum}, {chen}"
    if t.get("bat_dau") and t["bat_dau"].lower() not in thap:
        cum += f" ({_chuan(t['bat_dau'])})"
    if t.get("ngung") and t["ngung"].lower() not in thap:
        cum += f" (đã ngừng {_chuan(t['ngung'])})"
    return cum


# ═══ dien_dat() — Diễn đạt một mệnh đề thành một cụm chữ ══════════════════════════════
# Không gộp với mệnh đề khác; "chưa ghi nhận" khác với "không có", nghi ngờ và phủ định
# có cách viết riêng.
def dien_dat(p, ten_chu_the=None):
    """Một phát biểu -> một cụm chữ. KHÔNG gộp với phát biểu khác.

    LUẬT 2: "chưa ghi nhận" ra chữ "chưa ghi nhận", không ra "không có".
    Ba mức độ chắc chắn là ba cách diễn đạt khác nhau, không quy về nhau được:

        chắc chắn  + phủ định False  ->  "sốt"
        chac chan  + phu dinh True   ->  "không sốt"
        nghi ngo                     ->  "nghi ngờ sốt"
        chua ghi nhan                ->  "chưa ghi nhận sốt"

    `chua ghi nhan` bỏ qua phu_dinh: "chưa thấy bị bao giờ" đã là một chỗ trống,
    không phải một phủ định.
    """
    nd = _chuan(p.get("noi_dung"))
    muc_do = p.get("do_chac_chan", "chắc chắn")
    if muc_do == "chưa ghi nhận":
        cum = f"chưa ghi nhận {nd}"
    elif muc_do == "nghi ngờ":
        # Nội dung đã mang dấu rào đón ("viêm họng nghi do liên cầu") thì không
        # thêm lần nữa — giống bản tham chiếu của bộ sinh.
        cum = nd if re.search(r"(?<!\w)nghi(?!\w)", nd, re.I) else f"nghi ngờ {nd}"
    elif p.get("phu_dinh"):
        cum = f"không {nd}"
    else:
        cum = nd
    if p.get("thuoc"):
        cum = _them_chi_tiet_thuoc(cum, p["thuoc"])
    if p.get("moc_thoi_gian"):
        cum += f" ({_chuan(p['moc_thoi_gian'])})"
    if ten_chu_the:
        cum = f"{ten_chu_the}: {cum}"
    return cum


# ═══ sinh() — Dựng bản nháp từ danh sách mệnh đề ══════════════════════════════════════
# Trả về (văn bản, ghi chú); ghi chú nói từng mệnh đề đi vào mục nào và vì sao.
def sinh(phat_bieu, id_benh_nhan=0, ten_chu_the=None, ly_do_kham=None,
         ly_do_chan=None):
    """Trả về (van_ban, ghi_chu).

    ghi_chu ghi lại TỪNG phát biểu đi đâu và vì sao — để đối chiếu ngược lại
    được, và để Task 16 đo độ đầy đủ.

    ten_chu_the: {chu_the_id: "mẹ"} — đặt tên cho người không phải bệnh nhân,
    để mục TIỀN SỬ GIA ĐÌNH nói rõ là của ai.

    ly_do_chan: {id phát biểu: lý do} từ `khoa_bang_chung` — phát biểu bị khoá
    chặn KHÔNG vào thân, xuống CẦN XÁC NHẬN kèm ĐÚNG lý do của khoá.
    """
    ten_chu_the = ten_chu_the or {}
    ly_do_chan = ly_do_chan or {}
    theo_muc, ghi_chu = {}, []

    for p in phat_bieu:
        d = p.to_dict() if hasattr(p, "to_dict") else dict(p)
        if d.get("id") in ly_do_chan:
            muc, ly_do = "CẦN XÁC NHẬN", ly_do_chan[d.get("id")]
        else:
            muc, ly_do = _muc_cho(d, id_benh_nhan)
        ten = None
        if muc == MUC_NGUOI_KHAC or d.get("chu_the_id") != id_benh_nhan:
            # Tra bảng trước; không tra được thì dùng CHÍNH CHUỖI khâu trích đã
            # viết. Không có bước lùi này thì câu ra KHÔNG CÓ TÊN NGƯỜI.
            #
            # LỖI ĐÃ XẢY RA, đo được 11/09/2026: mục TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI
            # của nhánh B, C, D có 50/50/53 câu và **0 câu nêu tên người**, trong
            # khi bản tham chiếu có 22 câu và 22 câu nêu tên. Một bác sĩ đọc
            # "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI / rối loạn mỡ máu" không biết AI bị.
            #
            # Và phép đo không thấy: `thuoc_do_quy_gan._chu_the_cua_cau` suy chủ
            # thể từ TÊN MỤC khi câu không có từ chỉ người, nên một câu không tên
            # nằm trong mục gia đình vẫn được chấm là "người nhà" — đúng 100% ở
            # tầng 4. Con số 100% đó là điểm của việc XẾP ĐÚNG MỤC, không phải
            # điểm của việc GÁN ĐÚNG NGƯỜI.
            ten = ten_chu_the.get(d.get("chu_the_id"))
            if not ten and not _la_nhan_vien(d):
                tho = _chuan(d.get("ten_chu_the") or "")
                if tho and tho.lower() not in TEN_KHONG_DAT_TEN:
                    ten = tho
        cum = dien_dat(d, ten)
        if ly_do:
            cum = f"{cum} — {ly_do}"
        theo_muc.setdefault(muc, []).append(cum)
        ghi_chu.append({"id": d.get("id"), "muc": muc, "ly_do": ly_do,
                        "noi_dung": _chuan(d.get("noi_dung")),
                        "bang_chung": d.get("bang_chung"),
                        # ĐÚNG dòng chữ trong bản nháp — giao diện duyệt nối từng
                        # dòng với phát biểu của nó qua trường này
                        "van": cum})

    # LÝ DO KHÁM BỆNH: lấy phát biểu hiện tại đầu tiên, KHÔNG viết lại nội dung.
    if ly_do_kham is None and "BỆNH SỬ HIỆN TẠI" in theo_muc:
        ly_do_kham = theo_muc["BỆNH SỬ HIỆN TẠI"][0]
    if ly_do_kham:
        theo_muc["LÝ DO KHÁM BỆNH"] = [ly_do_kham]

    khoi = []
    for muc in THU_TU_MUC:
        cum_list = theo_muc.get(muc)
        if not cum_list:
            continue                          # không sinh mục rỗng
        khoi.append(f"{muc}\n\n" + ". ".join(cum_list) + ".")
    return "\n\n".join(khoi), ghi_chu


MUC_PHU = "CẦN XÁC NHẬN"
# Câu hỏi làm rõ (`hoi_lai`) cũng là PHẦN PHỤ: nó là việc bác sĩ cần làm, không
# phải thông tin về bệnh nhân. Đứng sau CẦN XÁC NHẬN, nhưng phải tách được cả khi
# hồ sơ không có mục CẦN XÁC NHẬN nào.
MUC_HOI_LAI = "CÂU HỎI LÀM RÕ"
MUC_PHU_TAT_CA = (MUC_PHU, MUC_HOI_LAI)


# ═══ tach_muc_phu() — Tách bản nháp thành bệnh án và phần cần xác nhận ════════════════
# Để bộ chấm không đếm mục CẦN XÁC NHẬN như một mục dự đoán.
def tach_muc_phu(van_ban):
    """-> (benh_an, phan_can_xac_nhan).

    VÌ SAO CẦN HÀM NÀY. `CẦN XÁC NHẬN` là mục do dự án này đặt ra, không có
    trong bất kỳ bản tham chiếu nào. Bộ chấm của cuộc thi nhận diện mục bằng
    quy tắc "dòng viết hoa toàn bộ", nên nó đếm `CẦN XÁC NHẬN` là một mục
    dự đoán — và vì bản tham chiếu không có mục đó, đẩy thành một DƯƠNG TÍNH
    GIẢ, kéo Section F1 xuống.

    Nghĩa là cơ chế an toàn của dự án bị chính phép chấm phạt. Cách xử lý
    trung thực không phải là bỏ mục đó đi, mà là BÁO CÁO CẢ HAI SỐ:

        có mục phụ    đúng đầu ra thật của hệ thống
        không mục phụ bệnh án thuần, so sánh công bằng với các nhánh khác

    Và báo cáo luôn số phát biểu nằm trong mục phụ — nếu không thì "chuyển
    sang cần xác nhận" sẽ thành chỗ giấu mọi thứ khó.
    """
    if not any(m in (van_ban or "") for m in MUC_PHU_TAT_CA):
        return van_ban or "", ""
    khoi = (van_ban or "").split("\n\n")
    than, phu, dang_phu = [], [], False
    i = 0
    while i < len(khoi):
        if khoi[i].strip() in MUC_PHU_TAT_CA:
            dang_phu = True
            phu.append(khoi[i])
            i += 1
            continue
        (phu if dang_phu else than).append(khoi[i])
        i += 1
    return "\n\n".join(than).strip(), "\n\n".join(phu).strip()
