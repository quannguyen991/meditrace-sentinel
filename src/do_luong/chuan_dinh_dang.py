# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Bộ chấm]
Làm gì   : Đổi các kiểu viết tiêu đề mục khác nhau về tên mục chuẩn trước khi chấm, để cách
           trình bày không làm sai điểm Section F1.
Vào → Ra : văn bản bản nháp có tiêu đề biến thể (như **Bệnh sử:**) → văn bản với tiêu đề
           viết hoa chuẩn
Đọc từ   : chuan_hoa() đổi cả văn bản; la_tieu_de_bien_the() nhận biết dòng tiêu đề
Mục lục (các hàm/lớp chính):
  la_tieu_de_bien_the()  Nhận biết dòng là tiêu đề biến thể
  chuan_hoa()            Đổi tiêu đề biến thể về tên mục chuẩn
Gọi tới  : bo_du_lieu/sinh_hoi_thoai_viet, duong_ong/b5_viet_ban_nhap
Dùng bởi : do_luong/cham_muc_thach_thuc, do_luong/do_dac
Tên cũ   : chuan_dinh_dang.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chuẩn hoá ĐỊNH DẠNG tiêu đề trước khi chấm, áp dụng NHƯ NHAU cho mọi nhánh.

VÌ SAO CẦN — đo được 11/09/2026, và nó làm một con số cũ mất nghĩa.

`section_f1` của nhánh `A nen` là **0,0000 đúng bằng không** trên cả 60 ca. Không
phải thấp — KHÔNG. Không một tên mục nào khớp, trên cả 60 bản nháp.

Nguyên nhân không phải nội dung. Mô hình sinh thẳng viết tiêu đề kiểu Markdown:

    **Bệnh sử:**                 <- A nền viết thế này
    BỆNH SỬ HIỆN TẠI             <- bản tham chiếu viết thế này

`cham_diem.cac_muc` nhận một dòng là tiêu đề khi nó VIẾT HOA TOÀN BỘ. Dòng
`**Benh su:**` có chữ thường nên không được tính, và thế là mẫu số của
`section_f1` trống rỗng.

HỆ QUẢ NẶNG HƠN MỘT CON SỐ SAI: điểm gộp là `0,6 x ROUGE + 0,4 x SectionF1`, nên
nhánh A bị **chặn trần ở 0,6** chỉ vì cách viết tiêu đề. Một phần ba thước đo
không bao giờ mở cho nó.

ĐÂY LÀ LẦN THỨ BA trong hai ngày một thước đo đo thứ khác với thứ nó khai:

    ROUGE         mù trước lo~i quy gán        (0,9799 so với 0,9661)
    f1_quy_gan    bị tầng dễ chi phối          (xếp regex trên đường ống)
    section_f1    đo CÁCH VIẾT TIÊU ĐỀ         (0 tuyệt đối cho A)

PHÉP THỬ CÔNG BẰNG — và đây là chỗ quan trọng nhất của tệp này.

    Chuẩn hoá phải là PHÉP ĐỒNG NHẤT trên bản nháp đã đúng tên mục chuẩn.

Nếu nó đổi cả nhánh `B`, `C`, `D` thì nó không còn là "bỏ tật định dạng" mà thành
"điều chỉnh để một nhánh trông hơn". Đo được, và đã đo:

    A_nen   0,0000 -> 0,1477   (+0,1477)
    B       0,7339 -> 0,7339   ( 0,0000)
    C       0,7285 -> 0,7285   ( 0,0000)
    D       0,6366 -> 0,6366   ( 0,0000)

Chỉ một nhánh đổi, và đó là nhánh duy nhất không dùng tên mục chuẩn.

VÀ PHẢI NÓI RÕ: sau khi bỏ tật định dạng, A vẫn kém xa B (0,15 so với 0,73). Nên
kết luận "cấu trúc mục của A kém hơn nhiều" VẪN ĐÚNG — chỉ là độ lớn bị thổi, và
con số "đúng bằng không" thì vô nghĩa.

GIỚI HẠN: bảng đồng nghĩa dưới đây là một phán đoán của tôi, chưa có bác sĩ xem.
Nó chỉ ánh xạ các cụm RẤT gần tên mục chuẩn. Mỗi lần thêm một đồng nghĩa là một
lần nới lỏng phép đo, nên bảng này phải được đọc cùng số liệu chứ không âm thầm.
"""
import re
import unicodedata

from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an
from src.bo_du_lieu import sinh_hoi_thoai_viet as sinh_hoi_thoai_viet

# HỢP của hai vốn từ, và chỗ này đã là một lo~ thật.
#
# `sinh_benh_an.THU_TU_MUC` (khâu sinh của đường ống) và
# `sinh_hoi_thoai_viet.MUC` (bản nháp tham chiếu) KHÔNG trùng nhau:
#
#     chỉ ở đường ống : CẦN XÁC NHẬN, KHÁM HỆ THỐNG CÁC CƠ QUAN, SINH HIỆU,
#                       TIÊM CHỦNG, TIỀN SỬ PHẪU THUẬT, TIỀN SỬ XÃ HỘI
#     chỉ ở tham chiếu: KHÁM LÂM SÀNG
#
# Bản tham chiếu có `KHAM LAM SANG` ở 60/60 ca; bản nháp của nhánh B có 0.
# Đường ống KHÔNG THỂ sinh ra tên mục đó vì tên đó không nằm trong bảng của
# nó. Đây không phải việc của tệp này để chữa, nhưng tệp này phải biết CẢ HAI
# vốn từ, nếu không thì nó sẽ 'chuẩn hoá' một tên đúng thành một tên khác.
MUC_CHUAN = tuple(dict.fromkeys(
    tuple(sinh_benh_an.THU_TU_MUC) + tuple(sinh_hoi_thoai_viet.MUC)))

# Cụm -> tên mục chuẩn. Khoá đã bỏ dấu, hạ chữ thường, bỏ dấu câu.
#
# CHỈ những cụm gần tên chuẩn. Không thêm cụm chỉ "có nghĩa tương tự": mỗi dòng
# ở đây là một lần nới lỏng phép đo.
DONG_NGHIA = {
    "benh su": "BỆNH SỬ HIỆN TẠI",
    "benh su hien tai": "BỆNH SỬ HIỆN TẠI",
    "qua trinh benh": "BỆNH SỬ HIỆN TẠI",
    "ly do kham": "LÝ DO KHÁM BỆNH",
    "ly do kham benh": "LÝ DO KHÁM BỆNH",
    "ly do vao vien": "LÝ DO KHÁM BỆNH",
    "tien su": "TIỀN SỬ BỆNH",
    "tien su benh": "TIỀN SỬ BỆNH",
    "tien su ban than": "TIỀN SỬ BỆNH",
    "tien su gia dinh": "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI",
    "tien su gia dinh va xa hoi": "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI",
    "thuoc dang dung": "THUỐC ĐANG DÙNG",
    "thuoc da dung": "THUỐC ĐANG DÙNG",
    "di ung": "DỊ ỨNG",
    "tien su di ung": "DỊ ỨNG",
    "kham lam sang": "KHÁM LÂM SÀNG",
    "kham": "KHÁM LÂM SÀNG",
    # Tên CŨ của mục khám trong `sinh_benh_an`, đổi ngày 11/09/2026. Giữ ở đây
    # làm biến thể để các tệp kết quả sinh trước khi đổi tên vẫn đọc được.
    "kham he thong cac co quan": "KHÁM LÂM SÀNG",
    "chan doan": "CHẨN ĐOÁN",
    "chan doan so bo": "CHẨN ĐOÁN",
    "ke hoach": "KẾ HOẠCH ĐIỀU TRỊ",
    "ke hoach dieu tri": "KẾ HOẠCH ĐIỀU TRỊ",
    "huong xu tri": "KẾ HOẠCH ĐIỀU TRỊ",
    "can xac nhan": sinh_benh_an.MUC_PHU,
}

# Dài nhất của một tên mục chuẩn, cộng một khoảng. Dòng dài hơn thế không phải
# tiêu đề dù nó có khớp bảng đồng nghĩa — "Kế hoạch điều trị gồm ba việc sau"
# là một câu, không phải một tiêu đề.
DAI_TOI_DA = max(len(m) for m in MUC_CHUAN) + 8


# ─── _khoa() — Bỏ dấu, hạ chữ thường để so tiêu đề ────────────────────────────────────
# Xử lý riêng chữ đ vì chuẩn hoá Unicode không tách được.
def _khoa(s):
    """Bo dau, ha chu thuong. PHAI doi `đ`/`Đ` bang tay.

    `unicodedata.normalize("NFD")` tách dấu thành ký tự tổ hợp, nhưng `đ` KHÔNG
    phải `d` cộng dấu — nó là một ký tự riêng, không tách được. Nên
    "ke hoach dieu tri" ra "ke hoach đieu tri" với `đ` còn nguyên, và nó không
    khớp khoá "ke hoach dieu tri" trong bảng.

    Ba phép thử đó vì đúng chỗ này: `## Chan doan`, `Ke hoach dieu tri:`, và
    `tien su gia dinh` — cả ba đều có `đ`.
    """
    tho = "".join(c for c in unicodedata.normalize("NFD", s)
                  if unicodedata.category(c) != "Mn")
    tho = tho.replace("đ", "d").replace("Đ", "D")
    return tho.lower().strip(" :*#-.\t")


# ═══ la_tieu_de_bien_the() — Nhận biết dòng là tiêu đề biến thể ═══════════════════════
# Trả về tên mục chuẩn hoặc None; cần dấu hai chấm hoặc khớp từ đồng nghĩa.
def la_tieu_de_bien_the(dong):
    """-> tên mục chuẩn, hoặc None. Thuần tuý, để test được."""
    d = re.sub(r"[*_#`]+", "", str(dong or "")).strip()
    if not d or len(d) > DAI_TOI_DA:
        return None
    d = re.sub(r"^[-+•]\s*", "", d)
    if not d.rstrip().endswith(":") and _khoa(d) not in DONG_NGHIA:
        # Không có dấu hai chấm và không khớp đồng nghĩa -> không phải tiêu đề.
        return None
    return DONG_NGHIA.get(_khoa(d))


# ═══ chuan_hoa() — Đổi tiêu đề biến thể về tên mục chuẩn ══════════════════════════════
# Giữ nguyên dòng khác, chỉ bỏ ký hiệu Markdown và gạch đầu dòng.
def chuan_hoa(van_ban):
    """Đổi tiêu đề biến thể thành tên mục chuẩn. Giữ nguyên mọi dòng khác.

    PHẢI là phép đồng nhất trên bản nháp đã đúng tên mục chuẩn — xem phép thử
    công bằng ở đầu tệp.
    """
    ra = []
    for dong in str(van_ban or "").split("\n"):
        ten = la_tieu_de_bien_the(dong)
        if ten:
            ra.append(ten)
            continue
        # Bỏ đậm Markdown và dấu gạch đầu dòng ở các dòng nội dung, để phép tách
        # mệnh đề không coi "**" là một từ.
        d = re.sub(r"[*_`]+", "", dong)
        ra.append(re.sub(r"^(\s*)[-+•]\s+", r"\1", d))
    return "\n".join(ra)
