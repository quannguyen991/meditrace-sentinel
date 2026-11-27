# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Bộ sinh]
Làm gì   : Sinh hội thoại khám bệnh tiếng Việt mô phỏng từ khuôn bệnh, kèm bệnh án và đáp án
           có cấu trúc.
Vào → Ra : mã ca + rng (+ tên tập) → Ca gồm hội thoại, các MenhDe đáp án, bệnh án
Đọc từ   : sinh_ca() dựng một ca đầy đủ; class Ca là kết quả; class MenhDe là một mệnh đề
           đáp án
Mục lục (các hàm/lớp chính):
  sinh_bo()         Sinh một bộ nhiều ca với cùng hạt giống
  sinh_mot_ca()     Sinh một ca hoàn chỉnh kèm đáp án có cấu trúc
  sinh_hoi_thoai()  Dựng toàn bộ hội thoại và mệnh đề của một ca
  sinh_ca()         Chọn khuôn bệnh và dựng thông tin cố định cho một ca
  sinh_benh_an()    Viết bệnh án chỉ từ các mệnh đề đã nói
  class MenhDe      Một mệnh đề lâm sàng kèm chủ thể thật, chính là đáp án
  class Ca          Thông tin cố định của một ca khám
  class TuyChon     Tuỳ chọn cho một ca, dùng cho bộ thử thách
  main()            Điểm vào dòng lệnh để sinh bộ hội thoại tiếng Việt
Gọi tới  : do_luong/thuoc_do_quy_gan, bo_du_lieu/bien_the_cau,
           bo_du_lieu/chia_tap_theo_khuon, bo_du_lieu/kho_khuon, bo_du_lieu/loi_dan_thuong,
           bo_du_lieu/ngu_lieu_viet, bo_du_lieu/phuong_ngu, duong_ong/b0_cat_doan_van …
           (tổng 10 tệp)
Dùng bởi : do_luong/cham_muc_thach_thuc, do_luong/chuan_dinh_dang,
           bo_du_lieu/chia_tap_theo_khuon, bo_du_lieu/sinh_bo_thach_thuc,
           duong_ong/b7_ban_duyet_html
Tên cũ   : sinh_hoi_thoai_viet.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Bộ sinh hội thoại khám bệnh Việt Nam, kèm bệnh án và ĐÁP ÁN CÓ CẤU TRÚC.

    python -m src.bo_du_lieu.sinh_hoi_thoai_viet --so-ca 1000

VÌ SAO TỰ DỰNG BỘ NÀY, VÀ VÌ SAO SINH BẰNG LUẬT CHỨ KHÔNG BẰNG MÔ HÌNH.

Bộ dữ liệu của cuộc thi có dấu vết rõ là bản dịch từ một bộ hội thoại y khoa
tiếng Anh (xem `docs/ket-qua/dau-vet-nguon.md`). Hai hiện tượng làm việc quy gán
khó nhất trong tiếng Việt — LƯỢC CHỦ NGỮ và DÙNG TỪ CHỈ QUAN HỆ HỌ HÀNG LÀM ĐẠI
TỪ — đều bị đuổi đại diện trong một bản dịch, vì tiếng Anh gần như luôn có chủ
ngữ. Bộ này sinh ra đúng hai hiện tượng đó.

Và nó sinh bằng LUẬT, không bằng mô hình ngôn ngữ. Đó là ràng buộc số 1 của cả
dự án, và lý do không phải hình thức:

  Dự án đo "mô hình gán nhầm thông tin cho sai người bao nhiêu lần". Mô hình
  ngôn ngữ viết hội thoại SẠCH hơn người nói thật — nó gần như luôn ghi rõ chủ
  ngữ ở mọi lượt. Nên đúng ca khó nhất sẽ hiếm đi, và đường tắt "chủ thể chính
  là người vừa nói" sẽ TRÚNG nhiều hơn bình thường. Đó không phải sai số ngẫu
  nhiên: nó lệch một chiều, luôn về phía làm vấn đề trông nhẹ hơn thật.

CÁI BỘ NÀY CÓ MÀ BỘ CỦA CUỘC THI KHÔNG CÓ: **đáp án có cấu trúc**. Mỗi mệnh đề
trong bệnh án đều kèm chủ thể thật, mốc thời gian thật, và tình huống thật. Nhờ
đó đo được độ chính xác quy gán CHÍNH XÁC TUYỆT ĐỐI, không phải ước lượng qua
bản tham chiếu dạng văn xuôi.

BỐN CÁI BẪY ĐÃ VẤP Ở `meditrace`, đều đã chặn ở đây:

  1. Thay thế làm bài toán không giải được  -> chỉ CHÈN thêm, giữ nguyên lượt gốc
  2. Hai khẳng định khác nhau không phải mâu thuẫn
  3. Độ dài lộ đáp án  -> số lượt không phụ thuộc vào việc ca đó có bẫy hay không
  4. Vị trí lộ đáp án  -> vị trí bẫy rải đều, không dính ở cuối
"""
import argparse
import functools
import hashlib
import io
import json
import random
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from src.he_thong import duong_dan as duong_dan
from src.bo_du_lieu import ngu_lieu_viet as nl
from src.bo_du_lieu import chia_tap_theo_khuon as tach_tap_viet
from src.bo_du_lieu import kho_khuon as kho_khuon

# Tên bẫy. Mỗi ca ghi lại mình chứa những bẫy nào, để đo được tỷ lệ lỗi THEO
# TỪNG BẪY thay vì chỉ một con số chung.
BAY = ("nguoi_nha_ke_ho", "tien_su_gia_dinh", "di_ung_nguoi_nha", "luoc_chu_ngu",
       "dai_tu_ho_hang", "dinh_chinh", "dien_bien", "gia_dinh", "hoi_khong_dap",
       "nguoi_ke_benh_minh", "mau_thuan", "bo_sung", "nguon_khac_nhau",
       "lieu_dinh_chinh")

# Bẫy được RÚT NGẪU NHIÊN. `nguoi_ke_benh_minh` cố ý không nằm ở đây: nó được
# bật riêng trong `sinh_bo`, vì rút nó qua `rng.sample` sẽ làm loãng tất cả bẫy
# khác (`rng.sample(BAY, k=n)` chia đều cho mọi phần tử — thêm một bẫy là mỗi
# bẫy cũ mất 1/9 tỷ lệ, và thế là bộ mới không còn so sánh được với bộ cũ).
# `mau_thuan` và `bo_sung` CÓ nằm trong bộ rút: chúng là bẫy nội dung bình
# thường như `dinh_chinh`, khác `nguoi_ke_benh_minh` (bẫy này phụ thuộc vào việc
# ca đó có người nhà kể hay không nên phải bật riêng).
#
# Thêm hai bẫy vào bộ rút làm mỗi bẫy cũ mất 2/11 tỷ lệ. Đó là giá phải trả và
# nó cố ý: hai quan hệ `bo sung` và `mau thuan` được khai trong lược đồ từ đầu
# mà có 0 ví dụ trên cả 43.687 mệnh đề, nên chúng cần chỗ trong bộ rút hơn là
# tám bẫy cũ cần giữ nguyên tỷ lệ.
#
# `nguon_khac_nhau` (thêm 11/09/2026) cũng bật RIÊNG, cùng lý do: nó chỉ có nghĩa
# khi CẢ bệnh nhân lẫn người nhà cùng có mặt và cùng nói. Rút qua `rng.sample`
# thì phần lớn lần rút rơi vào ca không đủ điều kiện và bị bỏ, còn mỗi bẫy cũ
# vẫn mất một phần tỷ lệ.
#
# `lieu_dinh_chinh` (thêm 15/09/2026) cũng KHÔNG nằm trong bộ rút: nó chỉ có nghĩa
# khi hội thoại CÓ nhắc một thuốc kèm liều, và việc đó tự rút ngẫu nhiên trong lúc
# sinh lời thoại. Nên bẫy này được GHI VÀO `ca.bay` ngay tại chỗ nó xảy ra (xem
# `_ke_thuoc`), không được chọn trước.
BAY_BAT_RIENG = ("nguoi_ke_benh_minh", "nguon_khac_nhau", "lieu_dinh_chinh")
BAY_RUT = tuple(b for b in BAY if b not in BAY_BAT_RIENG)

# Bẫy nào SINH RA `quan_he` trong đáp án. Khai ra để phép thử đối chứng
# ("ca sạch thì không có quan hệ nào") không phải gõ tay danh sách —
# gõ tay thì thêm bẫy mới là đối chứng âm thầm bỏ sót, và test vẫn xanh.
BAY_SINH_QUAN_HE = ("dinh_chinh", "dien_bien", "mau_thuan", "bo_sung",
                    "nguon_khac_nhau", "lieu_dinh_chinh")

# Tỷ lệ người nói tự sửa LIỀU ("amlodipin 5 mg, à nhầm, 10 mg"), trên các lần nhắc
# thuốc ĐỦ ĐIỀU KIỆN: có nói liều, thuốc có từ hai liều trong ngữ liệu, và thuốc còn
# đang dùng. Lỗi giữ lại liều đã bị sửa là kê nhầm liều — nhóm lỗi 9 của sổ tay.
TY_LE_LIEU_DINH_CHINH = 0.35

# Tỷ lệ ca có Y LỆNH THUỐC của bác sĩ ngay trong lời thoại: ngừng một thuốc đang
# dùng, hoặc kê một thuốc mới.
#
# VÌ SAO CÓ (16/09/2026). Trước đó mọi mệnh đề thuốc đều là lời NGƯỜI BỆNH kể về
# thuốc đang dùng. Thiếu hẳn hai việc có thật trong buổi khám: bác sĩ bảo ngừng
# thuốc, và bác sĩ kê thuốc mới. MEDIQA-OE 2025 và n2c2 CMED 2022 đều lấy đúng hai
# việc đó làm tác vụ chính (`Action = Stop`), nên thiếu chúng là thiếu chỗ so sánh.
# Y lệnh là việc CHƯA XẢY RA: `tinh_huong = "kế hoạch"`, và thuốc mới mang trạng
# thái "được kê, chưa dùng" chứ không phải "đang dùng".
TY_LE_Y_LENH_THUOC = 0.30

# Tỷ lệ bật `nguon_khac_nhau` trên các ca ĐỦ ĐIỀU KIỆN: bệnh nhân người lớn, có
# người nhà kể, bệnh nhân có mặt, và triệu chứng chính chưa mang bẫy
# `dinh_chinh` hay `mau_thuan` (cả ba cùng nhắm vào một mệnh đề).
#
# VÌ SAO CẦN. `cap_nhat.ap_luat` coi mọi `dinh chinh` là bản sau thắng bản
# trước, bất kể AI nói. Nhưng người nhà nói "4 ngày" rồi chính bệnh nhân nói "2
# ngày thôi" thì không có căn cứ nào để chọn một bên. Bộ sinh trước đây chỉ có
# mâu thuẫn của MỘT người nói (lưỡng lự), nên luật "hai NGUỒN khác nhau thì
# không tự chọn bên" chưa có một ví dụ nào để đo.
TY_LE_NGUON_KHAC_NHAU = 0.40

# Tỷ lệ bật `nguoi_ke_benh_minh` trên các ca CÓ người nhà kể.
#
# VÌ SAO CẦN (đo ngày 10/09/2026). Mệnh đề "người nhà kể về CHÍNH MÌNH" — chỗ
# cả hai đường tắt đều sai, "chủ thể = người nói" sai mà "chủ thể = bệnh nhân"
# cũng sai — chiếm:
#
#     bộ 3.000   67/3.507 mệnh đề = 1,91%
#     bộ 5.000  137/5.896 mệnh đề = 2,32%
#
# Đi từ 24 lên 60 khuôn, từ 1 lên 5 bối cảnh, con số đó gần như không đổi. Và
# trong 60 ca dùng để so sánh các nhánh: 7 mệnh đề trên 514.
#
# HỆ QUẢ: ảnh hưởng tối đa mà cơ chế quy gán có thể tạo ra trên một thước đo
# gộp là 1,36%, trong khi khoảng tin cậy rộng 4,16%. Phép so sánh không đủ công
# suất để thấy điều nó được dùng để thấy (xem `src/sai_so.canh_cong_suat`).
#
# Chỗ này không phải "mô hình kém" hay "cơ chế vô dụng" — là BỘ DỮ LIỆU gần như
# không chứa hiện tượng mà dự án nói về.
#
# NÂNG 0,45 -> 0,70 ngày 11/09/2026, theo đích 1.500 mệnh đề tầng 4 ở tập train.
# Ở 0,45 với bộ 100 khuôn, tập train chỉ có 1.165 mệnh đề tầng 4: bộ khuôn lớn
# hơn làm đổi cơ cấu ca, và tỷ lệ tầng 4 tụt xuống 2,98% — dưới ngưỡng 3% mà
# `test_ty_le_tang_4_da_tang_so_voi_muc_do_duoc_truoc_day` canh.
TY_LE_NGUOI_KE_BENH_MINH = 0.70

# ---------------------------------------------------------------- bối cảnh
#
# VÌ SAO CÓ BỐI CẢNH (thêm 10/09/2026).
#
# Đo được: 3.000 ca trước đó chỉ có **32 MẠCH THÔNG TIN** khác nhau, và năm
# mạch đầu chiếm 52,6%. Đầu và cuối giống hệt nhau ở 100% số ca:
#
#     BỆNH SỬ -> LÝ DO KHÁM -> BỆNH SỬ -> [tùy chọn] -> KHÁM -> CHẨN ĐOÁN
#     -> KẾ HOẠCH
#
# Đó mới là chỗ `eval_loss` xuống 10^-4, không phải số lượng bệnh. Thêm bệnh
# mà giữ nguyên một mạch thì mô hình vẫn học thuộc CÔNG THỨC VIẾT.
#
# Bối cảnh đổi ĐẦU và CUỐI của mạch, không chỉ đổi từ vựng:
#
#   kham_lan_dau        mạch cũ — khám mới, có chẩn đoán và kế hoạch
#   tai_kham            mở đầu bằng thuốc đã kê lần trước; THUỐC ĐANG DÙNG
#                       lên đầu thay vì nằm giữa
#   cho_ket_qua         KHÔNG có CHẨN ĐOÁN. Bác sĩ nói rõ chưa kết luận được.
#                       Đây là bối cảnh phục vụ thang thách thức 3.
#   nguoi_nha_thay_mat  bệnh nhân KHÔNG có mặt. Mọi thông tin đều qua người
#                       thứ ba — bối cảnh khó nhất cho quy gán chủ thể.
#   dieu_duong_ban_giao điều dưỡng nói trước, rồi bác sĩ vào. Ba vai người nói.
BOI_CANH = ("kham_lan_dau", "tai_kham", "cho_ket_qua",
            "nguoi_nha_thay_mat", "dieu_duong_ban_giao")

# Mạch cũ vẫn chiếm đa số: nó là bối cảnh thường gặp nhất thật, và giữ nó làm
# phần lớn giúp số liệu còn so sánh được với các lần chạy trước.
TRONG_SO_BOI_CANH = (48, 16, 14, 12, 10)

MUC = ("LÝ DO KHÁM BỆNH", "BỆNH SỬ HIỆN TẠI", "TIỀN SỬ BỆNH",
       "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", "THUỐC ĐANG DÙNG", "DỊ ỨNG",
       "KHÁM LÂM SÀNG", "CHẨN ĐOÁN", "KẾ HOẠCH ĐIỀU TRỊ")

# Mục -> `thoi_gian_su_kien`. Bộ sinh TỰ ĐẶT mục nên nó biết chắc giá trị này;
# trước 11/09/2026 đáp án không mang trường đó và `sinh_benh_an` có một luật đọc
# nó, nên luật đó là mã chết (xem chú thích ở `MenhDe.thoi_gian_su_kien`).
#
# "chua ro" là giá trị ĐÚNG cho ba mục dưới cùng, không phải giá trị bỏ qua:
#   DỊ ỨNG               dị ứng là một sự thật thường trực, không có thời điểm
#   TIỀN SỬ GIA ĐÌNH     bệnh của người khác, thời điểm không thuộc bệnh nhân
#   KẾ HOẠCH ĐIỀU TRỊ    chưa xảy ra; `tinh_huong = "ke hoach"` đã nói điều đó
THOI_GIAN_THEO_MUC = {
    "LÝ DO KHÁM BỆNH": "hiện tại",
    "BỆNH SỬ HIỆN TẠI": "hiện tại",
    "KHÁM LÂM SÀNG": "hiện tại",
    "CHẨN ĐOÁN": "hiện tại",
    "THUỐC ĐANG DÙNG": "hiện tại",
    "TIỀN SỬ BỆNH": "quá khứ",
    "DỊ ỨNG": "chưa rõ",
    "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI": "chưa rõ",
    "KẾ HOẠCH ĐIỀU TRỊ": "chưa rõ",
}


# ═══ class MenhDe — Một mệnh đề lâm sàng kèm chủ thể thật, chính là đáp án ════════════
# Mang chủ thể, nội dung, mục, mốc thời gian, độ chắc chắn, quan hệ và trạng thái.
@dataclass
class MenhDe:
    """Một đơn vị thông tin, kèm CHỦ THỂ THẬT. Đây là đáp án.

    QUAN_HE VA TRANG_THAI — thêm 09/09/2026.

    Trước đó đáp án KHÔNG có hai trường này. Hậu quả đo được: `trich_train`
    đẩy 2.231 ca cho mô hình học, và trong cả 2.231 ca thì `quan_he` luôn
    vắng mặt — tức là 2.231 ví dụ âm, KHÔNG MỘT ví dụ dương. Mô hình học đúng
    thứ nó được dạy: không bao giờ đánh dấu quan hệ. Trên 35 hội thoại thật,
    `quan_he` bằng "khong" ở **282/282** phát biểu.

    Bẫy `dinh_chinh` và `dien_bien` VẪN LUÔN có trong hội thoại (337 và 339 ca
    trong tập train) — chỉ là đáp án không ghi lại chúng. Nên đây không phải
    thiếu dữ liệu, mà là thiếu NHÃN trên dữ liệu đã có.
    """
    chu_the: str                 # "bệnh nhân" hoac ten quan he: "mẹ", "bà ngoại"...
    noi_dung: str
    muc: str
    moc_thoi_gian: Optional[str] = None
    phu_dinh: bool = False
    tinh_huong: str = "thực tế"  # thực tế | giả định | kế hoạch
    # hiện tại | quá khứ | chưa rõ — THEM 11/09/2026.
    #
    # HỌ LỖI LẦN THỨ TƯ, cùng hình với `quan_he` (09/09). Lược đồ 16 trường có
    # `thoi_gian_su_kien`, `sinh_benh_an` có luật
    #
    #     thoi_gian_su_kien == "quá khứ"  ->  TIỀN SỬ BỆNH
    #
    # nhưng đáp án KHÔNG CÓ trường này, nên `du_lieu_trich` đóng cứng nhãn thành
    # "chua ro", mô hình chỉ học được một giá trị, và xuất "chua ro" ở **cả 462**
    # phát biểu trên tập phát triển. Luật trên là MÃ CHẾT.
    #
    # Hậu quả đo được: mục TIEN SU BENH có 28/60 ca trong bản tham chiếu và **0**
    # trong bản nháp của mỗi nhánh.
    #
    # Bộ sinh BIẾT giá trị này — nó tự đặt `muc` cho từng mệnh đề — nên đây là
    # thiếu nhãn trên dữ liệu đã có, không phải thiếu dữ liệu.
    thoi_gian_su_kien: str = "chưa rõ"
    luot: List[int] = field(default_factory=list)
    quan_he: Optional[str] = None       # bổ sung | đính chính | diễn biến | mâu thuẫn
    quan_he_voi: Optional["MenhDe"] = None   # trỏ thẳng tới bản ghi kia
    trang_thai: str = "còn hiệu lực"    # còn hiệu lực | bị thay thế | chưa giải quyết
    # chắc chắn | nghi ngờ | chưa ghi nhận — THEM 11/09/2026.
    #
    # Họ lỗi "khai trong lược đồ mà không bao giờ có giá trị", lần thứ sáu (sau
    # `quan_he`, `tinh_huong`, hai quan hệ rỗng, `thoi_gian_su_kien`, và
    # `trich_dan` tìm ra cùng ngày). `bakeoff.LUOC_DO`, `phat_bieu.PhatBieu` và
    # `sinh_benh_an.dien_dat` đều phân biệt ba mức; `du_lieu_trich` thì đóng cứng
    # "chắc chắn" vì đáp án không mang trường này. Mô hình CHƯA BAO GIỜ được dạy
    # "nghi ngờ" hay "chưa ghi nhận" — đúng trục "có / không / chưa xác định" mà
    # tầng khoá bằng chứng cần.
    #
    # Tách khỏi `phu_dinh`: "chưa thấy bị bao giờ" là một chỗ TRỐNG (`chua ghi
    # nhan`), "không" là một khẳng định ÂM (`phu_dinh`). Trước đây cả hai đều là
    # `phu_dinh=True`, và bản tham chiếu in cả hai thành "Chua ghi nhan".
    do_chac_chan: str = "chắc chắn"
    # Loại phát biểu (`phat_bieu.HANH_VI`). `_Soan.ghi` tự suy từ vai người nói,
    # mục và lượt đứng trước; chỉ đặt tay ở những chỗ luật đó không đủ.
    hanh_vi: str = ""
    # Chi tiết thuốc (`phat_bieu.THUOC_KHOA`) — THÊM 15/09/2026. None với mọi mệnh
    # đề không phải thuốc. Mỗi chi tiết khác None PHẢI có nguyên văn trong hội thoại;
    # `tests/test_thuoc_chi_tiet.py` canh.
    thuoc: Optional[dict] = None
    # {so luot: chi so doan} — gợi ý ĐOẠN nào trong lượt là bằng chứng, cho những
    # mệnh đề nói TẮT mà so khớp từ không tìm được: "con cháu chưa thấy bị báo
    # gio" không có chữ "di ung". Không xuất ra đáp án. Xem `_trich_dan`.
    goi_y_doan: dict = field(default_factory=dict)


# ═══ class Ca — Thông tin cố định của một ca khám ═════════════════════════════════════
# Gồm bệnh, cách gọi và tự xưng, người kể, miền phương ngữ và các bẫy.
@dataclass
class Ca:
    ma: str
    benh: dict
    la_tre_em: bool
    goi_bn: str                  # bác sĩ gọi bệnh nhân là gì
    tu_xung_bn: str              # bệnh nhân tự xưng là gì
    nguoi_ke: Optional[tuple]    # None = bệnh nhân tự kể; khác = (vai, gọi, tự xưng, quan hệ)
    mien: str = "bac"            # chọn MỘT vùng cho cả cuộc, không trộn từng câu
    bay: List[str] = field(default_factory=list)
    boi_canh: str = "kham_lan_dau"   # xem BOI_CANH
    gioi_bn: Optional[str] = None    # "nam" | "nữ" — chỉ người lớn; trẻ em không cần
    # Lời thoại có NÓI RÕ người kể là ai của bệnh nhân không — xem `_lo_danh_tinh_nguoi_ke`.
    lo_danh_tinh: bool = False


# ─── _hoa() — Chuẩn hoá NFC và viết hoa chữ đầu ───────────────────────────────────────
# Chuỗi rỗng giữ nguyên.
def _hoa(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "")
    return s[:1].upper() + s[1:] if s else s


# ------------------------------------------------------------------- sinh ca

# ═══ sinh_ca() — Chọn khuôn bệnh và dựng thông tin cố định cho một ca ═════════════════
# Có thể ép tập, miền hoặc người kể cho bộ thử thách.
def sinh_ca(ma: str, rng: random.Random, chi_tap: Optional[str] = None,
            ep_mien: Optional[str] = None, ep_nguoi_ke: bool = False,
            mo_rong: bool = False) -> Ca:
    """`chi_tap`, `ep_mien`, `ep_nguoi_ke`: chỉ bộ thách thức dùng (xem
    `TuyChon`). Mỗi tuỳ chọn vẫn RÚT đúng số lần như khi không dùng nó."""
    ds_benh = kho_khuon.ds_khuon(mo_rong)
    if chi_tap is None:
        benh = rng.choice(ds_benh)
    else:
        bang = bang_tap_khuon(mo_rong=mo_rong)
        benh = rng.choice([b for b in ds_benh if bang[b["ten"]] == chi_tap])
    if benh["nhom"] == "nhi":
        la_tre = True
    elif benh["nhom"] == "người lớn":
        la_tre = False
    else:
        la_tre = rng.random() < 0.35

    gioi = None
    if la_tre:
        goi_bn, tu_xung = rng.choice(nl.XUNG_HO_TRE_EM)
        # Trẻ em thì gần như luôn có người nhà kể hộ — đó là thực tế phòng khám.
        nguoi_ke = rng.choice(nl.NGUOI_NHA_TRE_EM) if rng.random() < 0.92 else None
    else:
        # Cách gọi phải HỢP khuôn: có khuôn chỉ một giới, một lứa tuổi.
        cho = nl.XUNG_HO_THEO_KHUON.get(benh["ten"])
        goi_bn, tu_xung = rng.choice([x for x in nl.XUNG_HO_NGUOI_LON
                                      if cho is None or x[0] in cho])
        gioi = (nl.GIOI_THEO_KHUON.get(benh["ten"]) or nl.GIOI_THEO_GOI.get(goi_bn)
                or rng.choice(["nam", "nữ"]))
        nguoi_ke = (_chon_nguoi_nha_nguoi_lon(goi_bn, gioi, rng)
                    if rng.random() < 0.22 else None)
    if ep_nguoi_ke and nguoi_ke is None:
        nguoi_ke = (rng.choice(nl.NGUOI_NHA_TRE_EM) if la_tre
                    else _chon_nguoi_nha_nguoi_lon(goi_bn, gioi, rng))

    bc = rng.choices(BOI_CANH, weights=TRONG_SO_BOI_CANH)[0]
    # `nguoi_nha_thay_mat` chỉ có nghĩa khi CÓ người nhà. Không ép ngược lại
    # bằng cách tạo người nhà giả: làm thế thì tỷ lệ ca có người nhà bị lệch
    # theo bối cảnh, và mọi số liệu về quy gán chủ thể đều bị nhiễm.
    if bc == "nguoi_nha_thay_mat" and nguoi_ke is None:
        bc = "kham_lan_dau"

    mien = rng.choices(["bac", "nam", "trung"], weights=[45, 40, 15])[0]
    return Ca(ma=ma, benh=benh, la_tre_em=la_tre, goi_bn=goi_bn,
              tu_xung_bn=tu_xung, nguoi_ke=nguoi_ke,
              mien=ep_mien or mien, boi_canh=bc, gioi_bn=gioi)


# ------------------------------------------------------- sinh hội thoại

# ─── class _Soan — Bộ soạn gom lượt nói và mệnh đề của một ca ─────────────────────────
# Mệnh đề chỉ ghi khi thật sự được nói ra nên bệnh án không có thông tin ngoài hội
# thoại.
class _Soan:
    """Gom lượt thoại và mệnh đề. Mệnh đề CHỈ được ghi khi thật sự được nói ra —
    nhờ vậy bệnh án không bao giờ chứa thông tin không có trong hội thoại."""

    def __init__(self, ca: Ca, rng: random.Random, ap_phuong_ngu: bool = True,
                 ap_ngu_vuc: bool = True, mo_rong: bool = False):
        self.ca, self.rng = ca, rng
        self.luot: List[tuple] = []
        # Lời thoại TRƯỚC tầng ngữ vực và tầng vùng, cùng chỉ số với `luot`.
        self.luot_goc: List[str] = []
        self.menh_de: List[MenhDe] = []
        self.vung = nl.MIEN[ca.mien]
        # Các từ phương ngữ thực sự đã xuất hiện trong ca này. Ghi lại để đo
        # được RIÊNG nhóm có phương ngữ — không ghi thì không biết ca nào có.
        self.tu_phuong_ngu: List[str] = []
        self.cum_dan_thuong: List[str] = []
        # Hai bộ số riêng cho hai tầng ngôn ngữ — xem `ke`. Rút hạt từ `rng` ĐÚNG
        # MỘT lần, bất kể hai tầng có bật hay không, để bật/tắt một tầng không
        # làm lệch phần nội dung của hội thoại.
        hat = rng.getrandbits(48)
        self.rng_vung = random.Random(2 * hat + 1)
        self.rng_ngu_vuc = random.Random(2 * hat + 2)
        self.rng_mo_rong = random.Random(2 * hat + 3)
        self.ap_phuong_ngu, self.ap_ngu_vuc = ap_phuong_ngu, ap_ngu_vuc
        self.mo_rong = mo_rong

    def tt(self) -> str:
        """Tiểu từ cho CÂU HỎI và CÂU KỂ — chỉ "a" hoặc để trống."""
        t = self.rng.choice(self.vung["ket"])
        return (" " + t) if t else ""

    def dn(self) -> str:
        """Tiểu từ cho LỜI ĐỀ NGHỊ của bác sĩ — "nhe", "nha", "nghen".

        Tách khỏi `tt` vì gắn chung vào câu hỏi thì sai ngã:
        "Gia dinh co ai bi benh gi khong nhe?" không phải tiếng Việt.
        """
        t = self.rng.choice(self.vung["de_nghi"])
        return (" " + t) if t else ""

    def da(self, phu_dinh: bool = False) -> str:
        """Từ đệm mở đầu của BỆNH NHÂN / NGƯỜI NHÀ, đã kèm dấu phẩy.

        Không bao giờ là "Ừ" hay "Rồi" — đó là lời người trên nói với người
        dưới, bệnh nhân không dùng với bác sĩ.

        CHỈ khi TRẢ LỜI nhân viên y tế (sửa 11/09/2026). Nối tiếp lượt của chính
        mình mà mở bằng "Vang," thì như tự đáp lời mình — bản minh hoạ có "Vang,
        toi dang dieu tri loet ta trang" ngay sau một lượt của chính người đó.
        """
        if self.luot and self.luot[-1][0] not in self.VAI_NHAN_VIEN:
            return ""
        if getattr(self, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            return btc.chon_da(self.ca.mien, phu_dinh, self.rng_mo_rong)
        cac = self.vung["da_vang"]
        if phu_dinh:
            # "Vang, khong a" nghe như vừa đồng ý vừa phủ nhận: câu trả lời PHỦ
            # ĐỊNH mở bằng "Da".
            cac = [c for c in cac if not c.startswith("Vâng")] or ["Dạ"]
        return self.rng.choice(cac) + ", "

    # Nhân viên y tế trong LỜI THOẠI của bộ sinh — viết hoa, đúng như đầu lượt.
    VAI_NHAN_VIEN = ("Bác sĩ", "Điều dưỡng")

    def noi(self, vai: str, cau: str, cau_goc: Optional[str] = None) -> int:
        """`cau_goc`: lời thoại TRƯỚC tầng ngữ vực và tầng vùng (chỉ `ke` truyền).
        Giữ lại để tìm đoạn bằng chứng bằng THUẬT NGỮ CHUẨN — xem `_trich_dan`."""
        self.luot.append((vai, cau.strip()))
        self.luot_goc.append((cau if cau_goc is None else cau_goc).strip())
        return len(self.luot)

    def bs(self, cau: str) -> int:
        return self.noi("Bác sĩ", cau)

    def nguoi_ke_vai(self) -> str:
        return "Người nhà" if self.ca.nguoi_ke else "Bệnh nhân"

    def ke(self, cau: str, vai: Optional[str] = None) -> int:
        """Lời của BỆNH NHÂN hoặc NGƯỜI NHÀ — có thể mang từ phương ngữ.

        CHỈ thay ở đây, không thay trong `bs()`: bác sĩ được đào tạo nói chuẩn,
        và trộn lại thì mất một dấu hiệu thật trong hội thoại khám bệnh.

        ĐÁP ÁN KHÔNG ĐỔI. Hội thoại viết "lu du", `ghi()` vẫn ghi "met".
        Đó chính là phép thử: mô hình có quy được về khái niệm chuẩn không.
        Trừ cụm không đồng nghĩa ("nong ham hap" — chưa đo nhiệt độ thì chưa phải
        "sot"): `_giu_loi_nguoi_noi` đổi nội dung về lời người nói sau khi ghi.

        `vai`: mặc định là người đang kể (`nguoi_ke_vai`). Bẫy `nguon_khac_nhau`
        cần bệnh nhân chen vào trong một ca do người nhà kể.

        HAI BỘ SỐ NGẪU NHIÊN RIÊNG, và TẦNG NGỮ VỰC CHẠY TRƯỚC — đổi 11/09/2026.
        Trước đây hai tầng dùng chung `self.rng` với phần NỘI DUNG, nên mỗi lần
        tầng vùng quyết định đổi hay không là một lần rút số của cả hội thoại: tắt
        phương ngữ là đổi luôn bệnh, bẫy và mốc thời gian của mỗi lượt sau đó.
        Phép thử "cùng một ca, có và không có phương ngữ" (`thach_thuc`) cần hai
        bản giống hệt nhau trừ ĐÚNG các từ phương ngữ. Tầng ngữ vực chạy trước,
        trên câu gốc, nên quyết định của nó giống nhau ở cả hai bản.
        """
        cau_goc = cau
        if self.ap_ngu_vuc:
            from src.bo_du_lieu import loi_dan_thuong as loi_dan_thuong
            cau, da_doi_nv = loi_dan_thuong.doi_sang_dan_thuong(
                cau, self.rng_ngu_vuc)
            self.cum_dan_thuong.extend(t for t, _c in da_doi_nv)
        if self.ap_phuong_ngu and self.ca.mien in ("nam", "trung"):
            from src.bo_du_lieu import phuong_ngu as phuong_ngu
            cau, da_doi = phuong_ngu.doi_sang_phuong_ngu(cau, self.ca.mien,
                                                         self.rng_vung)
            self.tu_phuong_ngu.extend(d for _c, d in da_doi)
        # Viết hoa chữ đầu SAU hai tầng ngôn ngữ: `da()` có thể trả về rỗng, và câu
        # lược chủ ngữ khi đó bắt đầu bằng chữ thường ("con ho nua a").
        return self.noi(vai or self.nguoi_ke_vai(), _hoa(cau), cau_goc=_hoa(cau_goc))

    def ghi(self, chu_the, noi_dung, muc, luot, doan=None, kem_cau_hoi=False,
            **kw):
        """Ghi một mệnh đề và TRẢ VỀ chính nó.

        Trả về là cần thiết, không phải tiện nghi: bẫy `dinh_chinh` trước đây
        lấy mục tiêu bằng `menh_de[0]`, ngầm giả định mệnh đề đầu tiên luôn là
        triệu chứng chính. Bối cảnh `tai_kham` ghi một mệnh đề THUỐC lên trước,
        và thế là bẫy đính chính sửa nhầm vào thuốc — sinh ra
        "dang dung panadol (nam hom)" đối với "dang dung panadol".
        Test `test_dinh_chinh_chi_giu_moc_da_sua` bắt được.

        `doan`: gợi ý đoạn nào trong lượt ĐẦU của `luot` là bằng chứng — chỉ dùng
        ở chỗ mệnh đề nói TẮT, so khớp từ không tự tìm được. Xem `_trich_dan`.

        `kem_cau_hoi`: thêm lượt ngay trước (câu hỏi của nhân viên y tế) vào bằng
        chứng. Dùng cho câu trả lời TẮT — "Da, khong a" tự nó không mang nội dung,
        cặp hỏi–đáp mới đủ nghĩa. `bakeoff.HUONG_DAN` dạy đúng điều đó từ đầu
        ("Cap cau hoi–cau tra loi can ca hai luot"), nhưng nhãn thì chỉ ghi lượt
        trả lời: hai chỗ của cùng một dự án nói hai điều.
        """
        # `thoi_gian_su_kien` suy từ MỤC, vì bộ sinh tự đặt mục nên nó biết chắc.
        # Cho phép ghi đè qua `kw` — bẫy `dien_bien` cần đặt tay.
        kw.setdefault("thoi_gian_su_kien", THOI_GIAN_THEO_MUC.get(muc, "chưa rõ"))
        cac_luot = [luot] if isinstance(luot, int) else list(luot)
        dau = cac_luot[0]
        kw.setdefault("hanh_vi", self._hanh_vi(dau, muc,
                                               kw.get("tinh_huong", "thực tế")))
        if (kem_cau_hoi and dau >= 2
                and self.luot[dau - 2][0] in self.VAI_NHAN_VIEN):
            cac_luot = [dau - 1] + cac_luot
        md = MenhDe(chu_the=chu_the, noi_dung=noi_dung, muc=muc,
                    luot=cac_luot, **kw)
        if doan is not None:
            md.goi_y_doan[dau] = doan
        self.menh_de.append(md)
        return md

    def _hanh_vi(self, so_luot, muc, tinh_huong):
        """Loại phát biểu, suy từ VAI người nói lượt `so_luot` và lượt ĐỨNG TRƯỚC.

            nhân viên y tế    KHÁM LÂM SÀNG -> quan sát; kế hoạch, gia đình ->
                              kế hoạch; còn lại -> nhận định
            bệnh nhân / nhà   lượt trước của nhân viên y tế -> trả lời; còn lại
                              -> tự kể
        """
        vai = self.luot[so_luot - 1][0]
        if vai in self.VAI_NHAN_VIEN:
            if muc == "KHÁM LÂM SÀNG":
                return "quan sát"
            if tinh_huong in ("kế hoạch", "giả định"):
                return "kế hoạch"
            return "nhận định"
        truoc = self.luot[so_luot - 2][0] if so_luot >= 2 else None
        return "trả lời" if truoc in self.VAI_NHAN_VIEN else "tự kể"


# ─── _chon_nguoi_nha_nguoi_lon() — Chọn người nhà hợp tuổi và giới của bệnh nhân người lớn ───
# Từ xưng khớp cách bác sĩ gọi; trả (vai, cách gọi, tự xưng, quan hệ).
def _chon_nguoi_nha_nguoi_lon(goi_bn: str, gioi: str, rng: random.Random) -> tuple:
    """(vai, từ bác sĩ gọi họ, từ họ tự xưng, quan hệ) KHỚP lứa tuổi và giới của
    bệnh nhân — xem `nl.LUA_TUOI_THEO_GOI`. Bệnh nhân trẻ: vợ/chồng hoặc bố mẹ;
    trung niên, cao tuổi: vợ/chồng hoặc con. Không còn ông bà kể hộ người lớn.

    Từ xưng khớp với cách bác sĩ gọi họ: gọi "chi"/"anh" thì xưng "em" hoặc "toi",
    gọi "chau" thì xưng "chau" — bảng cũ có con gái bác sĩ gọi "chi" mà xưng "chau".
    """
    tuoi = nl.LUA_TUOI_THEO_GOI[goi_bn]
    loai = rng.choice(["vo_chong", "vo_chong", "bo_me"] if tuoi == "trẻ"
                      else ["vo_chong", "con"])
    if loai == "vo_chong":
        vai = "vợ" if gioi == "nam" else "chồng"
        goi = nl.VO_CHONG_GOI[goi_bn]
        tx = "em" if goi == "em" else (rng.choice(["em", "tôi"]) if goi in ("anh", "chị")
                                       else "tôi")
        return (vai, goi, tx, vai)
    if loai == "bo_me":
        vai = rng.choice(["mẹ", "bố"])
        goi = rng.choice(["cô", "bác"] if vai == "mẹ" else ["chú", "bác"])
        return (vai, goi, "tôi", vai)
    vai = rng.choice(["con gái", "con trai"])
    if tuoi == "trung niên" or goi_bn == "bác":
        goi, tx = rng.choice([("cháu", "cháu"), ("em", "em")])
    else:
        goi, tx = ("chị" if vai == "con gái" else "anh"), rng.choice(["em", "tôi"])
    return (vai, goi, tx, vai)


# ─── _cach_goi_bn_trong_loi_nguoi_ke() — Chọn cách người kể gọi bệnh nhân theo quan hệ ───
# Theo quan hệ và theo từ họ tự xưng, tránh cách gọi vô lý.
def _cach_goi_bn_trong_loi_nguoi_ke(ca: Ca, rng: random.Random) -> str:
    """Người nhà gọi bệnh nhân là gì khi kể — THEO quan hệ, và THEO chính từ họ tự
    xưng: đã xưng "toi" thì là "chau nha toi", "con toi", không phải "chau nha em".

    SỬA 11/09/2026. Bản cũ rút chung {"chau", "be", "con", "chau no", "be nha em"}
    cho mọi người kể bệnh nhi, và {goi bac si, "nha em", "ong ay", "ba ay"} cho mọi
    người kể bệnh nhân người lớn. Nên bà nội gọi cháu trai là "anh", bố xưng "toi"
    mà gọi con là "be nha em", và "nha em" — cách VỢ CHỒNG gọi nhau — rơi vào miệng
    ông bà, bố mẹ, con cái. Người dùng đọc bản minh hoạ: "khong ai noi nhu nay ca".

    Bẫy `dai_tu_ho_hang` vẫn còn: "chau" vừa là cách ông bà, bố mẹ gọi bệnh nhi,
    vừa là cách con cái xưng với bác sĩ (`nl.NGUOI_NHA`, `_chon_nguoi_nha_nguoi_lon`).
    """
    if not ca.nguoi_ke:
        return ca.tu_xung_bn                      # bệnh nhân tự kể — không dùng tới
    _vai, _goi, tx, qh = ca.nguoi_ke
    if ca.la_tre_em:
        if qh in ("mẹ", "bố"):
            return rng.choice(["cháu", "cháu nó", f"cháu nhà {tx}", f"bé nhà {tx}",
                               f"con {tx}"])
        return rng.choice(["cháu", "cháu nó", f"cháu {tx}"])          # ông bà
    gia = nl.LUA_TUOI_THEO_GOI[ca.goi_bn] == "cao tuổi"
    nam = ca.gioi_bn == "nam"
    if qh in ("vợ", "chồng"):
        if gia:
            return rng.choice([f"{'ông' if nam else 'bà'} nhà {tx}", f"nhà {tx}",
                               "ông ấy" if nam else "bà ấy"])
        if nam:                                   # vợ kể về chồng
            return rng.choice([f"nhà {tx}", f"chồng {tx}", "anh ấy"])
        return rng.choice([f"nhà {tx}", f"vợ {tx}"])   # chồng kể về vợ
    if qh in ("con gái", "con trai"):
        # Còn gọi cha mẹ già là "ong cu/ba cu nha em", KHÔNG "ba ay" — nghe xa cách.
        bo_me = "bố" if nam else "mẹ"
        return rng.choice([f"{bo_me} {tx}"] +
                          ([f"{'ông' if nam else 'bà'} cụ nhà {tx}"] if gia else []))
    return rng.choice(["cháu", "cháu nó", f"con {tx}", f"cháu nhà {tx}"])  # bố mẹ


# Tỷ lệ ca có người nhà mà lời thoại NÓI RÕ người đó là ai của bệnh nhân.
#
# VÌ SAO CÓ (15/09/2026). Trước đó bộ sinh ghi thẳng quan hệ thật của người kể
# ("bo", "ba ngoai"...) vào `chu_the` của đáp án và vào bản tham chiếu, BẤT KỂ lời
# thoại có lộ ra hay không. Câu mở đầu chỉ mang TỪ XƯNG HÔ ("anh", "ba"), mà xưng
# hô không xác định được quan hệ: "ba" là ba nội hay ba ngoại, "anh" là chồng hay
# con trai; và hai mẫu mở đầu ("Hom nay be sao roi?", "Lan truoc toi ke...") không
# lộ gì cả. Đo trên tập train thế hệ 6: 256/1.416 mệnh đề (18,1%) gán đích danh cho
# người kể mà không có mảnh mồi nào. Cả nhánh A lẫn khẩu trích đều bị đẩy ĐOÁN một
# thông tin không ai nói — đúng lo~i mà dự án dựng ra để chặn.
#
# Bất biến từ nay: quan hệ GHI ĐÍCH DANH trong đáp án  <=>  quan hệ CÓ trong lời
# thoại. Còn lại ghi "nguoi nha". `tests/test_lo_danh_tinh.py` canh.
TY_LE_LO_DANH_TINH = 0.6


# ─── _ten_nguoi_ke() — Lấy tên chủ thể cho thông tin của chính người kể ───────────────
# Dùng quan hệ nếu đã lộ danh tính, không thì ghi người nhà.
def _ten_nguoi_ke(ca: Ca) -> str:
    """Tên ghi vào `chu_the` cho thông tin CỦA CHÍNH người đang kể."""
    return ca.nguoi_ke[3] if (ca.nguoi_ke and ca.lo_danh_tinh) else "người nhà"


# ─── _lo_danh_tinh_nguoi_ke() — Chèn cặp hỏi đáp nói rõ quan hệ của người kể ──────────
# Rút số cho mọi ca kể cả không chèn; không sinh mệnh đề.
def _lo_danh_tinh_nguoi_ke(s, ca: Ca, rng: random.Random) -> None:
    """Với xác suất TY_LE_LO_DANH_TINH, chèn một cặp hỏi - đáp nói RÕ quan hệ.

    Rút số với MỌI ca, kể cả ca không chèn — để hai bản của một cặp
    thách thức đi cùng một đường rút số. Cặp này KHÔNG sinh mệnh đề: nó chỉ làm cho
    tên ghi trong đáp án có căn cứ trong lời thoại."""
    ca.lo_danh_tinh = False
    if rng.random() >= TY_LE_LO_DANH_TINH:
        return
    if not ca.nguoi_ke:
        # Ca KHÔNG có người nhà cũng nhận một cặp cùng độ dài, cùng xác suất.
        # Chèn riêng cho ca có người nhà thì số lượt lại lộ bẫy: các bẫy cần người
        # nhà (`di_ung_nguoi_nha`, `nguon_khac_nhau`) dồn về nhóm dài hơn —
        # `test_do_dai_KHONG_lo_ca_nao_co_bay` đã báo đó (0,755 > 0,72).
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            cau_hoi, cau_ke = btc.sinh_danh_tinh_tu_kham(ca, s.rng_mo_rong)
            s.bs(cau_hoi)
            s.ke(cau_ke)
            return
        s.bs(f"{_hoa(ca.goi_bn)} đi khám cho mình phải không ạ?")
        cach = [f"{ca.tu_xung_bn} khám cho {ca.tu_xung_bn} ạ.",
                f"{ca.tu_xung_bn} tự đi khám ạ.",
                f"đúng rồi ạ, {ca.tu_xung_bn} tự đến khám.",
                f"{ca.tu_xung_bn} đi khám thật ạ."]
        s.ke(f"{s.da()}{rng.choice(cach)}")
        return
    ca.lo_danh_tinh = True
    bn3 = _bn_ngoi_ba(ca)
    if getattr(s, "mo_rong", False):
        from src.bo_du_lieu import bien_the_cau as btc
        cau_hoi, cau_ke = btc.sinh_danh_tinh_nguoi_nha(ca, bn3, s.rng_mo_rong)
        s.bs(cau_hoi)
        s.ke(cau_ke)
        return
    s.bs(f"{_hoa(ca.nguoi_ke[1])} là gì của {bn3} ạ?")
    s.ke(f"{s.da()}{ca.nguoi_ke[2]} là {ca.nguoi_ke[3]} của {bn3} ạ.")


# ─── _duong_dung_cua() — Lấy đường dùng của một thuốc theo ngữ liệu ───────────────────
# Thuốc không có trong bảng chi tiết coi là thuốc uống.
def _duong_dung_cua(ca: Ca, ten: str) -> str:
    """Đường dùng của một thuốc theo ngữ liệu; thuốc không có trong bảng chi tiết
    (tên thương mại trong `nl.THUOC`) thì là thuốc uống."""
    bang = nl.THUOC_CHI_TIET_TRE_EM if ca.la_tre_em else nl.THUOC_CHI_TIET_NGUOI_LON
    return bang[ten][0] if ten in bang else "uống"


# ─── _thuoc() — Dựng từ điển thuốc đủ mọi khoá ────────────────────────────────────────
# Chi tiết không nói thì là None, không bỏ khoá.
def _thuoc(ten, duong, trang, lieu=None, so_lan=None, bat_dau=None, ngung=None):
    """Từ điển `thuoc` ĐỦ MỌI KHOÁ — chi tiết không nói thì là None, không bỏ khoá."""
    return {"ten": ten, "lieu": lieu, "so_lan": so_lan, "duong_dung": duong,
            "bat_dau": bat_dau, "ngung": ngung, "trang_thai_dung": trang}


# ─── _ke_thuoc() — Người bệnh hoặc người nhà kể một thuốc kèm chi tiết ────────────────
# Mỗi chi tiết (liều, số lần, lúc bắt đầu) có hoặc vắng độc lập.
def _ke_thuoc(s, ca: Ca, rng: random.Random, chu: str, tt) -> None:
    """Người bệnh (hoặc người nhà) kể MỘT thuốc, kèm một phần chi tiết — thêm 15/09/2026.

    Mỗi chi tiết (liều, số lần, lúc bắt đầu) có mặt HAY VẮNG MẶT độc lập: vắng mặt
    thì đáp án ghi None. Mô hình phải học rằng KHÔNG nói thì KHÔNG ghi — nếu chi tiết
    luôn có mặt, nó sẽ học luôn điền liều, kể cả khi không ai nói.

    Rút ĐỦ MỌI SỐ trước khi quyết định dùng số nào, để hai bản của một cặp thách thức
    đi cùng một đường rút số (cùng lệ với `_lo_danh_tinh_nguoi_ke`).

    Ba biến thể:
      đang dùng          "có uống amlodipin 5 mg, ngày một lần buổi sáng, dùng được ba tháng nay"
      đã ngừng           "trước có uống omeprazole 20 mg, ngừng 2 tuần rồi" -> TIỀN SỬ BỆNH
      tự sửa liều        "có uống amlodipin 5 mg, à nhầm, 10 mg mới đúng" -> hai mệnh đề,
                           bản 5 mg `bi thay the`, bản 10 mg `dinh chinh` bản kia
    """
    bang = nl.THUOC_CHI_TIET_TRE_EM if ca.la_tre_em else nl.THUOC_CHI_TIET_NGUOI_LON
    ten = rng.choice(sorted(bang))
    duong, cac_lieu, cac_lan = bang[ten]
    lieu, so_lan = rng.choice(cac_lieu), rng.choice(cac_lan)
    bat_dau = rng.choice(nl.BAT_DAU_THUOC)
    co_lieu, co_lan, co_bat_dau = rng.random() < 0.7, rng.random() < 0.7, rng.random() < 0.5
    da_ngung = rng.random() < 0.2
    sua = rng.random() < TY_LE_LIEU_DINH_CHINH
    tuan = rng.randint(1, 4)
    lieu_moi = rng.choice([x for x in cac_lieu if x != lieu] or [lieu])

    lieu = lieu if co_lieu else None
    so_lan = so_lan if co_lan else None
    # "dung duoc hai tuan nay" rồi "ngung 2 tuan roi" là hai mốc nghịch nhau.
    bat_dau = bat_dau if (co_bat_dau and not da_ngung) else None
    sua = sua and lieu is not None and lieu_moi != lieu and not da_ngung

    dau = f"{ten} {lieu}" if lieu else ten
    if sua:
        # "a nham" chứ không "a khong": từ "khong" trong đoạn dẫn làm khoá bằng chứng
        # cảnh báo phủ định cho một câu không hề phủ định.
        dau = f"{ten} {lieu}, à nhầm, {lieu_moi} mới đúng"
    phan = [dau] + ([so_lan] if so_lan else []) + (
        [f"dùng được {bat_dau}"] if bat_dau else [])

    if da_ngung:
        ngung = f"{tuan} tuần"
        l = s.ke(f"{s.da()}trước {chu}có {duong} {', '.join(phan)}, "
                 f"ngừng {ngung} rồi{tt()}.")
        s.ghi("bệnh nhân", f"từng dùng {ten}, đã ngừng {ngung}", "TIỀN SỬ BỆNH", l,
              thuoc=_thuoc(ten, duong, "đã ngừng", lieu=lieu, so_lan=so_lan,
                           ngung=ngung))
        return

    l = s.ke(f"{s.da()}{chu}có {duong} {', '.join(phan)}{tt()}.")
    thuoc = _thuoc(ten, duong, "đang dùng", lieu=lieu, so_lan=so_lan, bat_dau=bat_dau)
    md = s.ghi("bệnh nhân", ten, "THUỐC ĐANG DÙNG", l, thuoc=thuoc)
    if not sua:
        return
    # Cùng cách với bẫy `dinh_chinh`: GIỮ bản cũ, đánh dấu bị thay thế, chèn bản mới
    # trước nó. Bản mới dùng MenhDe trực tiếp nên phải chép tay mọi trường `ghi` đặt.
    md.trang_thai = "bị thay thế"
    moi = MenhDe(chu_the=md.chu_the, noi_dung=md.noi_dung, muc=md.muc,
                 phu_dinh=md.phu_dinh, tinh_huong=md.tinh_huong, luot=list(md.luot),
                 # Mỗi bản đính chính là "tự kể" (`phat_bieu.HANH_VI`): không ai hỏi
                 # người nói sửa lại. `test_menh_de_tao_tay_mang_DU_nhan_nhu_ban_goc`.
                 quan_he="đính chính", quan_he_voi=md, hanh_vi="tự kể",
                 thoi_gian_su_kien=md.thoi_gian_su_kien,
                 do_chac_chan=md.do_chac_chan, thuoc=dict(thuoc, lieu=lieu_moi))
    s.menh_de.insert(s.menh_de.index(md), moi)
    ca.bay = sorted(set(ca.bay) | {"lieu_dinh_chinh"})


# ─── _y_lenh_thuoc() — Bác sĩ ra y lệnh thuốc ngay trong hội thoại ────────────────────
# Hai kiểu: ngừng thuốc đang dùng hoặc kê thuốc mới; đều là kế hoạch.
def _y_lenh_thuoc(s, ca: Ca, rng: random.Random, tt) -> None:
    """Bác sĩ ra y lệnh về thuốc ngay trong lời thoại — thêm 16/09/2026.

    Hai biến thể, đều là việc CHƯA XẢY RA nên `tinh_huong = "kế hoạch"`:
      ngung   "Từ hôm nay ngừng uống amlodipin nhé."   -> trang_thai_dung "đã ngừng"
      ke moi  "Tôi kê omeprazole 20 mg, uống ngày một lần trước ăn sáng nhé."
              -> trang_thai_dung "được kê, chưa dùng"

    Biến thể "ngung" chỉ chọn được khi trong ca ĐÃ có một thuốc đang dùng, nên nó
    tạo ra một cặp đối lập trong cùng một ca: cùng tên thuốc, một bản "đang dùng"
    (lời người bệnh) và một bản "đã ngừng" (y lệnh bác sĩ). Ghi nhầm hai bản này
    thành một là đúng lo~i "thuốc đã ngừng ghi thành đang dùng".

    Rút ĐỦ MỌI SỐ trước khi rẽ nhánh, để hai bản của một cặp thách thức đi cùng một
    đường rút số — cùng lệ với `_ke_thuoc`.
    """
    bang = nl.THUOC_CHI_TIET_TRE_EM if ca.la_tre_em else nl.THUOC_CHI_TIET_NGUOI_LON
    ten_moi = rng.choice(sorted(bang))
    duong_moi, cac_lieu, cac_lan = bang[ten_moi]
    lieu, so_lan = rng.choice(cac_lieu), rng.choice(cac_lan)
    co_y_lenh = rng.random() < TY_LE_Y_LENH_THUOC
    chon_ngung = rng.random() < 0.5
    if not co_y_lenh:
        return
    dang_dung = [m for m in s.menh_de
                 if m.thuoc and m.thuoc.get("trang_thai_dung") == "đang dùng"]
    if dang_dung and chon_ngung:
        md = dang_dung[-1]
        ten, duong = md.thuoc["ten"], md.thuoc["duong_dung"]
        # KHÔNG viết "khong ... nua": từ phủ định trong đoạn dẫn làm khoá bằng chứng
        # cảnh báo phủ định cho một câu không hề phủ định.
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            l = s.bs(btc.sinh_y_lenh_ngung(ten, duong, s.rng_mo_rong, tt()))
        else:
            l = s.bs(f"Từ hôm nay ngừng {duong} {ten} nhé{tt()}.")
        s.ghi("bệnh nhân", f"ngừng {ten}", "KẾ HOẠCH ĐIỀU TRỊ", l,
              tinh_huong="kế hoạch", thuoc=_thuoc(ten, duong, "đã ngừng"))
        return
    if getattr(s, "mo_rong", False):
        from src.bo_du_lieu import bien_the_cau as btc
        l = s.bs(btc.sinh_y_lenh_ke(ten_moi, lieu, duong_moi, so_lan, s.rng_mo_rong, tt()))
    else:
        l = s.bs(f"Tôi kê {ten_moi} {lieu}, {duong_moi} {so_lan} nhé{tt()}.")
    s.ghi("bệnh nhân", f"kê {ten_moi}", "KẾ HOẠCH ĐIỀU TRỊ", l,
          tinh_huong="kế hoạch",
          thuoc=_thuoc(ten_moi, duong_moi, "được kê, chưa dùng", lieu=lieu,
                       so_lan=so_lan))


# ─── _bn_ngoi_ba() — Cách bác sĩ nói về bệnh nhân với người nhà, ngôi thứ ba ──────────
# Không mượn cách gọi của người nhà.
def _bn_ngoi_ba(ca: Ca) -> str:
    """Bác sĩ nói VỀ bệnh nhân với người nhà — ngôi thứ ba. Không bao giờ mượn cách
    gọi của người nhà: trước 11/09/2026 bác sĩ nói "be nha em khong den duoc a?",
    "Neu mai be nha em con..." — 218 lượt bác sĩ ở tập train mang "nha em"."""
    if ca.la_tre_em:
        return "cháu" if ca.goi_bn == "con" else ca.goi_bn
    return f"{ca.goi_bn} ấy"


# ═══ class TuyChon — Tuỳ chọn cho một ca, dùng cho bộ thử thách ═══════════════════════
# Mặc định cho ra đúng bộ chính; không làm đổi đường rút số của rng.
@dataclass
class TuyChon:
    """Tuỳ chọn cho MỘT ca — chỉ dùng cho các bộ thách thức (`src.bo_du_lieu.sinh_bo_thach_thuc`).

    Mặc định cho ra ĐÚNG bộ dữ liệu chính. Mỗi tuỳ chọn phải giữ nguyên đường
    rút số của `rng` so với bản cặp của nó, để hai bản của một cặp chỉ khác
    nhau ở ĐÚNG điều đang đo — có test canh.
    """
    chi_tap: Optional[str] = None       # chỉ rút khuôn của tập này
    ep_mien: Optional[str] = None       # "bac" | "nam" | "trung"
    ep_bay: tuple = ()                  # bẫy BẮT BUỘC thêm vào ca
    ep_nguoi_ke: bool = False           # bắt buộc có người nhà kể
    ap_phuong_ngu: bool = True
    ap_ngu_vuc: bool = True
    di_ung_cua_nguoi_ke: bool = False   # bẫy dị ứng người nhà: luôn là người kể
    doi_chu_the: bool = False           # đảo người mang dị ứng — xem bẫy dị ứng
    mo_rong: bool = False               # True: dùng kho 270 khuôn; False: 200 khuôn gốc


# ─── _muc_chan_doan() — Đổi chẩn đoán của khuôn thành (nội dung, độ chắc chắn) ────────
# Theo dõi X đầu câu và có chữ nghi là nghi ngờ; còn lại chắc chắn.
def _muc_chan_doan(cd: str):
    """Chẩn đoán của khuôn -> (nội dung, độ chắc chắn).

    "Theo doi X" ĐẦU câu là cách bác sĩ ghi chẩn đoán TẠM (nghi X); "... nghi ..."
    là nghi ngờ ("Viem hong nghi do lien cau"). Trước 11/09/2026 cả hai mang nhãn
    "chắc chắn" — tầng khoá bằng chứng chỉ ra: 447 phát biểu chẩn đoán của tập
    train NÓI một đằng, NHÃN một neo. "X, theo doi" (chẩn đoán chắc kèm kế hoạch
    theo dõi) giữ "chắc chắn".
    """
    cd = cd.strip().rstrip(".")
    m = re.match(r"theo dõi\s+", cd, re.I)
    if m:
        return cd[m.end():], "nghi ngờ"
    if re.search(r"(?<!\w)nghi(?!\w)", cd, re.I):
        return cd, "nghi ngờ"
    return cd, "chắc chắn"


# ═══ sinh_hoi_thoai() — Dựng toàn bộ hội thoại và mệnh đề của một ca ══════════════════
# Trả bộ soạn chứa các lượt nói và mệnh đề; tuỳ chọn điều khiển phương ngữ.
def sinh_hoi_thoai(ca: Ca, rng: random.Random, tuy: Optional[TuyChon] = None):
    # Tên `tuy`, KHÔNG phải `tc`: thân hàm này dùng `tc` cho triệu chứng của bẫy
    # diễn biến, và một tên trùng sẽ đè lên tuỳ chọn ở giữa hàm.
    tuy = tuy or TuyChon()
    s = _Soan(ca, rng, ap_phuong_ngu=tuy.ap_phuong_ngu,
              ap_ngu_vuc=tuy.ap_ngu_vuc, mo_rong=tuy.mo_rong)
    tt = s.tt
    benh = ca.benh
    # Hai cách gọi KHÁC NHAU cho cùng một bệnh nhân:
    #   goi_bn_trong_loi — nguoi nha goi con minh ("bé nhà em", "cháu nó")
    #   ca.goi_bn        — bac si goi benh nhan ("bé", "cháu", "con")
    # Trộn hai cái này làm bác sĩ nói giọng người mẹ, nghe sai ngay.
    goi_bn_trong_loi = _cach_goi_bn_trong_loi_nguoi_ke(ca, rng)

    # --- mở đầu, khác nhau theo BỐI CẢNH
    if ca.boi_canh == "dieu_duong_ban_giao":
        # Vai thứ ba. `nguoi_noi` của lược đồ có sẵn "dieu duong", nhưng trước
        # 10/09/2026 không hội thoại nào dùng tới — nên mô hình chưa bao giờ
        # gặp một ca có ba người nói.
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            tt_dd, xong_dd = s.rng_mo_rong.choice(btc.DIEU_DUONG_MO_RONG_THEM)
            s.noi("Điều dưỡng", f"Em chào bác sĩ. {_hoa(ca.goi_bn)} này {tt_dd}, {xong_dd}")
        else:
            s.noi("Điều dưỡng", f"Em chào bác sĩ. {_hoa(ca.goi_bn)} này "
                                f"{rng.choice(['vào từ sáng', 'mới đăng ký khám', 'chờ từ nãy'])}"
                                f", em đã đo sinh hiệu rồi ạ.")
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            cau_bs = s.rng_mo_rong.choice(btc.BAC_SI_DIEU_DUONG_MO_RONG)
            # Định dạng bằng eval hoặc định dạng an toàn
            cau_bs_fmt = cau_bs.replace("{_hoa(ca.goi_bn)}", _hoa(ca.goi_bn)).replace("{tt()}", tt())
            s.bs(cau_bs_fmt)
        else:
            s.bs(f"Cảm ơn em. {_hoa(ca.goi_bn)} kể tôi nghe xem thế nào{tt()}.")
    elif ca.boi_canh == "tai_kham":
        thuoc_cu = rng.choice(nl.THUOC_TRE_EM if ca.la_tre_em else nl.THUOC)
        ai_tk = ca.goi_bn if not ca.nguoi_ke else _bn_ngoi_ba(ca)
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            s.bs(s.rng_mo_rong.choice(btc.TAI_KHAM_MO_RONG).format(thuoc=thuoc_cu, ai=ai_tk, tt=tt()))
        else:
            s.bs(f"Lần trước tôi kê {thuoc_cu} cho "
                 f"{ai_tk}, "
                 f"dùng thấy thế nào{tt()}?")
        # ĐỘNG TỪ theo đường dùng (15/09/2026): trước đó mọi thuốc đều "uong", kể cả
        # salbutamol là thuốc xịt.
        duong = _duong_dung_cua(ca, thuoc_cu)
        # Ghi lại thuốc đang dùng NGAY Ở ĐÂU. Ở mạch cũ, THUỐC ĐANG DÙNG luôn
        # nằm giữa; đây là một trong những chỗ làm mạch bị đều.
        if rng.random() < 0.55:
            l = s.ke(f"{s.da()}vẫn đang {duong} {thuoc_cu}{tt()}.")
            s.ghi("bệnh nhân", f"đang dùng {thuoc_cu}", "THUỐC ĐANG DÙNG", l,
                  thuoc=_thuoc(thuoc_cu, duong, "đang dùng"))
        else:
            tuan = rng.randint(1, 4)
            l = s.ke(f"{s.da()}{duong} được ít hôm rồi ngừng, "
                     f"ngừng {tuan} tuần rồi{tt()}.")
            # Câu trả lời KHÔNG nhắc tên thuốc — tên nằm ở câu hỏi của bác sĩ ngay
            # trước, nên bằng chứng phải gồm cả cặp hỏi–đáp (15/09/2026: 0 lượt dẫn
            # nào chứa tên thuốc trước khi thêm `kem_cau_hoi`).
            s.ghi("bệnh nhân", f"từng dùng {thuoc_cu}, đã ngừng {tuan} tuần",
                  "TIỀN SỬ BỆNH", l, kem_cau_hoi=True,
                  thuoc=_thuoc(thuoc_cu, duong, "đã ngừng", ngung=f"{tuan} tuần"))
    elif ca.boi_canh == "nguoi_nha_thay_mat":
        # Bệnh nhân KHÔNG có mặt. Mọi thông tin đều đi qua người thứ ba, nên
        # đường tắt "chủ thể chính là người vừa nói" luôn SAI ở bối cảnh này.
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            cau_bs = s.rng_mo_rong.choice(btc.NGUOI_NHA_THAY_MAT_BS).format(
                nn=ca.nguoi_ke[1], nn_hoa=_hoa(ca.nguoi_ke[1]), bn3=_bn_ngoi_ba(ca), tt=tt())
            cau_ke = s.rng_mo_rong.choice(btc.NGUOI_NHA_THAY_MAT_KE).format(
                da=s.da(), gbn=goi_bn_trong_loi, tx=ca.nguoi_ke[2], tt=tt())
            s.bs(cau_bs)
            s.ke(cau_ke)
        else:
            s.bs(f"Hôm nay {ca.nguoi_ke[1]} đi một mình à, "
                 f"{_bn_ngoi_ba(ca)} không đến được{tt()}?")
            s.ke(f"{s.da()}{goi_bn_trong_loi} mệt quá nên "
                 f"{ca.nguoi_ke[2]} đi thay{tt()}.")
    elif ca.nguoi_ke:
        mau = rng.choice(nl.MO_DAU_NGUOI_NHA)
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            mau = s.rng_mo_rong.choice(btc.MO_DAU_NGUOI_NHA_MO_RONG)
        s.bs(mau.format(goi_nn=ca.nguoi_ke[1], goi_nn_hoa=_hoa(ca.nguoi_ke[1]),
                        goi_bs=ca.goi_bn, goi_bs_hoa=_hoa(ca.goi_bn), tt=tt()))
    else:
        mau = rng.choice(nl.MO_DAU)
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            mau = s.rng_mo_rong.choice(btc.MO_DAU_MO_RONG)
        s.bs(mau.format(goi=ca.goi_bn, goi_hoa=_hoa(ca.goi_bn), tt=tt()))

    _lo_danh_tinh_nguoi_ke(s, ca, rng)
    _xa_giao(s, ca, rng)

    # --- triệu chứng chính
    chinh = benh["chinh"][0]
    # Mốc thời gian phải hợp DIỄN TIẾN của bệnh. "Sốt nửa tháng" rồi chẩn
    # đoán "cúm mùa" là một ca mà bác sĩ đọc qua là thấy sai.
    moc = rng.choice(nl.MOC_MAN if benh["dien_tien"] == "mạn" else nl.MOC_CAP)
    chu = "" if "luoc_chu_ngu" in ca.bay else (
        goi_bn_trong_loi + " " if ca.nguoi_ke else ca.tu_xung_bn + " ")
    cau = f"{s.da()}{chu}{chinh} {moc} rồi{tt()}."
    if getattr(s, "mo_rong", False):
        from src.bo_du_lieu import bien_the_cau as btc
        cau_mau = s.rng_mo_rong.choice(btc.CACH_KE_CHINH)
        cau = f"{s.da()}" + cau_mau.format(
            chu=chu, chinh=chinh, moc=moc, tt=tt())
    l = s.ke(cau)
    md_chinh = s.ghi("bệnh nhân", chinh, "BỆNH SỬ HIỆN TẠI", l, moc_thoi_gian=moc)
    s.ghi("bệnh nhân", chinh, "LÝ DO KHÁM BỆNH", l)

    # --- BẪY HAI NGUỒN NÓI KHÁC NHAU (thêm 11/09/2026)
    #
    # Người nhà vừa kể mốc, rồi CHÍNH bệnh nhân nói khác. Khác `mau_thuan` ở chỗ
    # hai bản đến từ HAI NGƯỜI: không ai tự sửa ai, nên không có căn cứ nào để
    # chọn một bên — cả hai `chua giai quyet`, bác sĩ ghi là chưa rõ. Đây là ví
    # dụ cho luật "hai nguồn khác nhau thì không tự chọn bên" của tầng đồ thị
    # trạng thái (`cap_nhat`). Điều kiện bật nằm ở `sinh_bo`.
    if "nguon_khac_nhau" in ca.bay:
        ro = nl.MOC_MAN if benh["dien_tien"] == "mạn" else nl.MOC_CAP
        moc_khac = rng.choice([m for m in ro if m != moc])
        tx_bn = ca.tu_xung_bn
        cau_nkn = rng.choice([
            f"Không đúng đâu, {tx_bn} {chinh} {moc_khac} rồi{tt()}.",
            f"Theo {tx_bn} thì {moc_khac} mới đúng{tt()}.",
        ])
        if getattr(s, "mo_rong", False):
            cau_nkn = cau_nkn.replace(" rồi rồi", " rồi")
        l2 = s.ke(cau_nkn, vai="Bệnh nhân")
        # Mỗi bản giữ LƯỢT CỦA CHÍNH NÓ, không gộp hai lượt như bẫy `mau_thuan`:
        # ở đây hai bản do HAI người nói, và phép đo chia tầng theo người nói
        # của lượt bằng chứng — gộp lại thì bản của người nhà mang lượt của
        # bệnh nhân và bị xếp sai tầng.
        cu = md_chinh
        cu.trang_thai = "chưa giải quyết"
        moi = MenhDe(chu_the="bệnh nhân", noi_dung=chinh, muc=cu.muc,
                     moc_thoi_gian=moc_khac, luot=[l2],
                     quan_he="mâu thuẫn", quan_he_voi=cu,
                     trang_thai="chưa giải quyết", hanh_vi="tự kể",
                     thoi_gian_su_kien=cu.thoi_gian_su_kien)
        s.menh_de.insert(s.menh_de.index(cu) + 1, moi)
        s.bs(f"Để tôi ghi là chưa rõ {moc} hay {moc_khac}, "
             f"mình xác nhận lại sau nhé{tt()}.")

    # --- đính chính (nếu có): sửa lại chính con số vừa nói
    if "dinh_chinh" in ca.bay:
        ro = nl.MOC_MAN if benh["dien_tien"] == "mạn" else nl.MOC_CAP
        moc_moi = rng.choice([m for m in ro if m != moc])
        # Người nói tự xưng BẰNG ĐÚNG từ họ dùng ở các lượt khác. Ban đầu bốc
        # ngẫu nhiên "em nham" / "toi nho nham" nên một ông bố lúc xưng "tôi"
        # lúc xưng "em" trong cùng một cuộc — đọc là thấy giả ngay.
        tx = ca.nguoi_ke[2] if ca.nguoi_ke else ca.tu_xung_bn
        # Ba cách nói, cùng một khuôn "X chứ không phải Y" — thêm hai cách sau
        # ngày 11/09/2026 để bài kiểm tra đính chính không chỉ bắt một cụm "a
        # không".
        l2 = s.ke(rng.choice([
            f"À không, {tx} {rng.choice(['nhầm', 'nhớ nhầm', 'nói nhầm'])}, "
            f"{moc_moi} chứ không phải {moc}{tt()}.",
            f"Xin lỗi bác sĩ, {tx} nhớ lại rồi, {moc_moi} chứ không phải "
            f"{moc}{tt()}.",
            f"{_hoa(tx)} nói lại cho đúng, {moc_moi} chứ không phải {moc}{tt()}.",
        ]))
        # GIỮ bản cũ, đánh dấu "bi thay the", và thêm một bản MỚI mang mốc đã
        # sửa. Trước đây chỗ này sửa thẳng `moc_thoi_gian` của bản cũ — bệnh án
        # ra đúng, nhưng đáp án mất sạch dấu vết của việc đính chính, nên không
        # có gì để mô hình học và không có gì để đo.
        #
        # Bản mới phải chèn vào ĐẦU danh sách, không được thêm vào cuối: thứ tự
        # mệnh đề quyết định thứ tự cụm trong mục BENH SU HIEN TAI của bệnh án
        # tham chiếu. Thêm vào cuối thì bệnh án đổi chữ, và mọi con số ROUGE đo
        # trước đây hết so sánh được.
        # Mục tiêu là mệnh đề TRIỆU CHỨNG CHÍNH, giữ bảng tham chiếu tương
        # minh. Không dùng `menh_de[0]` — bối cảnh `tai_kham` ghi một mệnh đề
        # thuốc lên trước nó.
        cu = md_chinh
        cu.luot.append(l2)
        cu.trang_thai = "bị thay thế"
        moi = MenhDe(chu_the=cu.chu_the, noi_dung=cu.noi_dung, muc=cu.muc,
                     moc_thoi_gian=moc_moi, phu_dinh=cu.phu_dinh,
                     tinh_huong=cu.tinh_huong, luot=list(cu.luot),
                     quan_he="đính chính", quan_he_voi=cu, hanh_vi="tự kể",
                     # Dùng MenhDe trực tiếp, không qua `ghi`, nên phải chép
                     # tay — bản và `thoi_gian_su_kien` sáng 11/09/2026 đi qua
                     # `ghi` và bỏ sót đúng ba chỗ này.
                     thoi_gian_su_kien=cu.thoi_gian_su_kien)
        s.menh_de.insert(s.menh_de.index(cu), moi)

    # --- BẪY MÂU THUẪN: hai mốc XUNG NHAU, KHÔNG ai đính chính
    #
    # Khác `dinh_chinh` ở ĐÚNG MỘT chỗ, và chỗ đó là cả ý nghĩa: không có câu
    # "a khong, toi nham". Nên không bản nào bị thay thế — cả hai ở trạng thái
    # `chua giai quyet`, và bác sĩ phải là người hỏi lại.
    #
    # VÌ SAO CẦN (đo 11/09/2026). Lược đồ khai BỐN quan hệ và BA trạng thái,
    # nhưng trên cả 43.687 mệnh đề của bộ 5.000:
    #
    #     bổ sung       0 ví dụ
    #     đính chính  784
    #     diễn biến   795
    #     mâu thuẫn     0 ví dụ
    #
    # và `trang_thai` chỉ có hai giá trị, không có `chua giai quyet`. Tài liệu
    # thì khai cả bốn quan hệ và cả ba trạng thái như nhau, kèm sơ đồ chuyển
    # trạng thái có mũi "mau thuan -> chua giai quyet". Đó là KHAI QUÁ.
    #
    # Nặng hơn: `phan_quan_he` cho mô hình chọn giữa 5 nhãn, trong đó HAI nhãn
    # không có một ví dụ dương nào. Chúng chỉ là nguồn nhiễu.
    #
    # Một bẫy này lấp cả hai lo~: quan hệ `mau thuan` VÀ trạng thái
    # `chua giai quyet`.
    if "mau_thuan" in ca.bay:
        ro = nl.MOC_MAN if benh["dien_tien"] == "mạn" else nl.MOC_CAP
        moc_khac = rng.choice([m for m in ro if m != moc])
        tx = ca.nguoi_ke[2] if ca.nguoi_ke else ca.tu_xung_bn
        l2 = s.ke(rng.choice([
            f"{tx} nghĩ là {moc_khac} thì đúng hơn{tt()}.",
            f"Mà cũng có thể {moc_khac}, {tx} không chắc lắm{tt()}.",
            f"Hình như {moc_khac} cơ{tt()}.",
        ]))
        cu = md_chinh
        cu.luot.append(l2)
        # KHÔNG đặt "bi thay the": không có đính chính thì không bản nào thắng.
        cu.trang_thai = "chưa giải quyết"
        moi = MenhDe(chu_the=cu.chu_the, noi_dung=cu.noi_dung, muc=cu.muc,
                     moc_thoi_gian=moc_khac, phu_dinh=cu.phu_dinh,
                     tinh_huong=cu.tinh_huong, luot=list(cu.luot),
                     quan_he="mâu thuẫn", quan_he_voi=cu,
                     trang_thai="chưa giải quyết",
                     # "nghi la...", "co the...", "hinh nhu..." — cả ba cách
                     # nói đều RÀO ĐÓN, nên bản này là `nghi ngo`.
                     do_chac_chan="nghi ngờ", hanh_vi="tự kể",
                     thoi_gian_su_kien=cu.thoi_gian_su_kien)
        s.menh_de.insert(s.menh_de.index(cu) + 1, moi)
        # Bác sĩ phải HỎI LẠI, không được im lặng chọn một bản. Im lặng là
        # hành vi sai trong hội thoại khám bệnh thật.
        s.bs(f"Để tôi ghi là chưa rõ {moc} hay {moc_khac}, "
             f"mình xác nhận lại sau nhé{tt()}.")

    # --- hỏi thêm triệu chứng
    cau_them = rng.choice(nl.HOI_THEM).format(tt=tt())
    if getattr(s, "mo_rong", False):
        from src.bo_du_lieu import bien_the_cau as btc
        cau_them = btc.sinh_cau_hoi_them_ngu_canh(chinh, ca, s.rng_mo_rong)
    s.bs(cau_them)
    phu = rng.sample(benh["phu"], k=rng.randint(1, min(2, len(benh["phu"]))))
    cum = ", ".join(phu)
    chu = "" if "luoc_chu_ngu" in ca.bay else (
        goi_bn_trong_loi + " " if ca.nguoi_ke else ca.tu_xung_bn + " ")
    cau_phu = f"{s.da()}{chu}còn {cum} nữa{tt()}."
    if getattr(s, "mo_rong", False):
        from src.bo_du_lieu import bien_the_cau as btc
        cau_mau = s.rng_mo_rong.choice(btc.CACH_KE_PHU)
        cau_phu = f"{s.da()}" + cau_mau.format(chu=chu, cum=cum, tt=tt())
    l = s.ke(cau_phu)
    md_phu = [s.ghi("bệnh nhân", p, "BỆNH SỬ HIỆN TẠI", l) for p in phu]

    # --- BẪY BỔ SUNG: thêm CHI TIẾT cho một mệnh đề đã nói, không đổi nó
    #
    # Quan hệ `bo sung` được khai trong lược đồ từ đầu nhưng có 0 ví dụ trên cả
    # bộ 5.000 — xem chú thích ở bẫy `mau_thuan`.
    #
    # Khác `dien_bien` ở chỗ: `dien_bien` là HAI mốc thời gian, triệu chứng đổi
    # theo thời gian. `bo sung` là CÙNG một sự việc, chỉ thêm chi tiết — mức độ,
    # thời điểm trong ngày, hoàn cảnh. Bản cũ VẪN còn hiệu lực.
    if "bo_sung" in ca.bay and md_phu:
        goc = rng.choice(md_phu)
        chi_tiet = rng.choice(["nhiều hơn về đêm", "nặng hơn sau khi ăn",
                               "chỉ bị lúc sáng sớm", "tăng lên khi vận động",
                               "đỡ hơn khi nằm nghỉ"])
        l2 = s.ke(f"{s.da()}{goc.noi_dung} thì {chi_tiet}{tt()}.")
        goc.luot.append(l2)
        s.ghi("bệnh nhân", f"{goc.noi_dung} {chi_tiet}", goc.muc, l2,
              quan_he="bổ sung", quan_he_voi=goc)

    # --- diễn biến: hai mốc, CẢ HAI đều đúng
    if "dien_bien" in ca.bay:
        tc = benh["chinh"][1] if len(benh["chinh"]) > 1 else benh["chinh"][0]
        m1, m2 = rng.sample(nl.MOC_THOI_DIEM, 2)
        l = s.ke(f"{m1.capitalize()} thì {tc}, {m2} thì đỡ hẳn rồi{tt()}.")
        # Hai mệnh đề CHUNG một lượt: đoạn 0 nói mốc đầu, đoạn 1 nói mốc sau.
        # Mệnh đề sau nói TẮT ("hom nay thi do han roi" — không có tên triệu
        # chứng), nên so khớp từ tự động sẽ chọn nhầm đoạn 0. Xem `_trich_dan`.
        s.ghi("bệnh nhân", tc, "BỆNH SỬ HIỆN TẠI", l, moc_thoi_gian=m1, doan=0)
        s.ghi("bệnh nhân", tc, "BỆNH SỬ HIỆN TẠI", l, moc_thoi_gian=m2,
              phu_dinh=True, doan=1)
        # CẢ HAI vẫn "còn hiệu lực" — đó là cả chỗ khác nhau giữa diễn biến và
        # đính chính. Chỉ đánh dấu quan hệ trên bản SAU, trỏ về bản TRƯỚC.
        s.menh_de[-1].quan_he = "diễn biến"
        s.menh_de[-1].quan_he_voi = s.menh_de[-2]

    # --- tiền sử bản thân
    if rng.random() < 0.55:
        cau_ts = rng.choice(nl.HOI_TIEN_SU).format(tt=tt())
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            cau_ts = btc.sinh_cau_hoi_tien_su_ngu_canh(chinh, ca, s.rng_mo_rong)
        s.bs(cau_ts)
        if rng.random() < 0.7:
            ts = rng.choice(nl.TIEN_SU_TRE_EM if ca.la_tre_em else nl.TIEN_SU_NGUOI_LON)
            chu = "" if "luoc_chu_ngu" in ca.bay else (
                goi_bn_trong_loi + " " if ca.nguoi_ke else ca.tu_xung_bn + " ")
            l = s.ke(f"{s.da()}{chu}có {ts}{tt()}.")
            s.ghi("bệnh nhân", ts, "TIỀN SỬ BỆNH", l)
        else:
            if getattr(s, "mo_rong", False):
                from src.bo_du_lieu import bien_the_cau as btc
                cau_dap = btc.sinh_dap_khong_tien_su(ca, s.rng_mo_rong, tt=tt())
            else:
                cau_dap = f"{s.da(phu_dinh=True)}không có gì{tt()}."
            s.ke(cau_dap)

    # --- BẪY QUAN TRỌNG NHẤT: tiền sử của NGƯỜI NHÀ, kể xen vào
    if "tien_su_gia_dinh" in ca.bay:
        cau_gd = rng.choice(nl.HOI_GIA_DINH).format(tt=tt())
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            cau_gd = btc.sinh_cau_hoi_gia_dinh_ngu_canh(benh.get("he_co_quan", ""), s.rng_mo_rong)
        s.bs(cau_gd)
        ai = _nguoi_nha_khac(ca, rng)
        benh_nha = _benh_hop_tuoi(ai, ca, rng, mo_rong=tuy.mo_rong)
        tu_xung = ca.nguoi_ke[2] if ca.nguoi_ke else ca.tu_xung_bn
        if ai == "người kể":
            # Chính người đang kể lại nói về bệnh CỦA HỌ. Đây là chỗ dễ gán nhầm
            # nhất: người nói và chủ thể là MỘT, nhưng chủ thể KHÔNG phải bệnh nhân.
            ten_that = _ten_nguoi_ke(ca) if ca.nguoi_ke else "bệnh nhân"
            l = s.ke(f"{s.da()}{tu_xung} thì bị {benh_nha}, "
                     f"còn {goi_bn_trong_loi} thì chưa thấy gì{tt()}.")
            s.ghi(ten_that, benh_nha, "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", l)
        else:
            l = s.ke(f"{s.da()}{ai} bị {benh_nha}{tt()}.")
            s.ghi(ai, benh_nha, "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", l)

    # --- BẪY TẦNG 4: người nhà TỰ NÓI RA bệnh của chính mình, không ai hỏi
    #
    # Khác `tien_su_gia_dinh` ở hai chỗ, và cả hai làm nó khó hơn:
    #
    #   1. KHÔNG có câu hỏi của bác sĩ dẫn vào. `tien_su_gia_dinh` luôn đi sau
    #      `HOI_GIA_DINH`, nên ngữ cảnh đã báo trước "sắp nói về người khác".
    #      Ở đây lời này xen vào giữa mạch kể về bệnh nhân.
    #   2. Câu không có mệnh đề đối lập "con chau thi chua thay gi". Một hệ
    #      thống có thể đang ăn điểm nhờ nửa sau đó chứ không nhớ quy gán.
    #
    # Đáp án ghi chủ thể là TÊN THẬT của người kể, nên nó vào mục tiền sử gia
    # đình chứ không vào mục của bệnh nhân.
    if "nguoi_ke_benh_minh" in ca.bay and ca.nguoi_ke:
        tu_xung = ca.nguoi_ke[2]
        ten_that = _ten_nguoi_ke(ca)
        benh_minh = _benh_hop_tuoi("người kể", ca, rng, mo_rong=tuy.mo_rong)
        mau_cau = rng.choice([
            "{tx} cũng đang {benh}, nên {tx} hay lo{tt}.",
            "{tx} bị {benh} mấy năm nay rồi{tt}.",
            # KHÔNG gắn {tt}: câu đã kết bằng "bac si a" — gắn thêm thành "a a".
            "{tx} đang điều trị {benh}, bác sĩ ạ.",
            "{tx} thì {benh}, nói thêm để bác sĩ biết{tt}.",
        ])
        l = s.ke(f"{s.da()}{mau_cau.format(tx=tu_xung, benh=benh_minh, tt=tt())}")
        s.ghi(ten_that, benh_minh, "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", l)

    # --- dị ứng
    if rng.random() < 0.6 or "di_ung_nguoi_nha" in ca.bay:
        cau_du = rng.choice(nl.HOI_DI_UNG).format(tt=tt())
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            cau_du = btc.sinh_cau_hoi_di_ung_ngu_canh(ca, s.rng_mo_rong)
        s.bs(cau_du)
        if "di_ung_nguoi_nha" in ca.bay:
            ai = _nguoi_nha_khac(ca, rng, cho_phep_nguoi_ke=True)
            if tuy.di_ung_cua_nguoi_ke and ca.nguoi_ke:
                # Vẫn RÚT số ở dòng trên rồi mới đặt đề: hai bản của một cặp
                # thách thức phải đi CÙNG một đường rút số.
                ai = "người kể"
            # Dị ứng của NGƯỜI NHÀ: bể riêng, chia theo tập. Dị ứng của bệnh
            # nhân (nhánh `elif` bên dưới) vẫn dùng THUOC_DI_UNG, không chia.
            thuoc = rng.choice(be_theo_tap(nl.DI_UNG_NGUOI_NHA, tap_cua_ca(ca, mo_rong=tuy.mo_rong)))
            tu_xung = ca.nguoi_ke[2] if ca.nguoi_ke else ca.tu_xung_bn
            ten_that = (_ten_nguoi_ke(ca) if (ai == "người kể" and ca.nguoi_ke) else ai)
            xung = tu_xung if ai == "người kể" else ai
            if tuy.doi_chu_the:
                # PHÉP THỬ ĐỔI CHỦ THỂ (`src.bo_du_lieu.sinh_bo_thach_thuc`): CÙNG câu, đảo hai
                # người — bệnh nhân mang dị ứng, người kia "chưa thấy bị báo
                # gio". Bản này chỉ ghi dị ứng của bệnh nhân: "chua thay bi bao
                # gio" của người nhà không phải thông tin của hồ sơ bệnh nhân.
                l = s.ke(f"{s.da()}{goi_bn_trong_loi} thì dị ứng {thuoc}, "
                         f"còn {xung} chưa thấy bị bao giờ{tt()}.")
                s.ghi("bệnh nhân", f"dị ứng {thuoc}", "DỊ ỨNG", l)
            else:
                l = s.ke(f"{s.da()}{xung} thì dị ứng {thuoc}, "
                         f"còn {goi_bn_trong_loi} chưa thấy bị bao giờ{tt()}.")
                s.ghi(ten_that, f"dị ứng {thuoc}", "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", l)
                # "Chua thay bi bao gio" là một chỗ TRỐNG, không phải phủ định —
                # `chua ghi nhan`, xem `MenhDe.do_chac_chan`. Mệnh đề nói TẮT
                # (đoạn cuối không có chữ "di ung"), nên gợi ý đoạn.
                s.ghi("bệnh nhân", "dị ứng thuốc", "DỊ ỨNG", l,
                      do_chac_chan="chưa ghi nhận", doan=-1)
        elif rng.random() < 0.35:
            thuoc = rng.choice(nl.THUOC_DI_UNG)
            cau_dap = f"{s.da()}có, dị ứng {thuoc}{tt()}."
            if getattr(s, "mo_rong", False):
                from src.bo_du_lieu import bien_the_cau as btc
                mau_dap = s.rng_mo_rong.choice(btc.DAP_CO_DI_UNG)
                if ca.nguoi_ke:
                    mau_dap = mau_dap.replace("tôi", goi_bn_trong_loi).replace("mình", goi_bn_trong_loi)
                cau_dap = f"{s.da()}" + mau_dap.format(thuoc=thuoc, tt=tt())
            l = s.ke(cau_dap)
            s.ghi("bệnh nhân", f"dị ứng {thuoc}", "DỊ ỨNG", l)
        else:
            if getattr(s, "mo_rong", False):
                from src.bo_du_lieu import bien_the_cau as btc
                cau_dap = btc.sinh_dap_khong_di_ung(ca, s.rng_mo_rong, tt=tt())
            else:
                cau_dap = f"{s.da(phu_dinh=True)}không{tt()}."
            l = s.ke(cau_dap)
            # Trả lời TẮT: "Da, khong a" không mang nội dung, cặp hỏi–đáp mới đủ
            # nghĩa — xem `_Soan.ghi(kem_cau_hoi)`.
            s.ghi("bệnh nhân", "dị ứng thuốc", "DỊ ỨNG", l, phu_dinh=True,
                  kem_cau_hoi=True)

    # --- thuốc đang dùng
    if rng.random() < 0.5:
        cau_thuoc = rng.choice(nl.HOI_THUOC).format(tt=tt())
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            cau_thuoc = btc.sinh_cau_hoi_thuoc_ngu_canh(chinh, ca, s.rng_mo_rong)
        s.bs(cau_thuoc)
        if rng.random() < 0.65:
            chu = "" if "luoc_chu_ngu" in ca.bay else (
                goi_bn_trong_loi + " " if ca.nguoi_ke else ca.tu_xung_bn + " ")
            _ke_thuoc(s, ca, rng, chu, tt)
        else:
            if getattr(s, "mo_rong", False):
                from src.bo_du_lieu import bien_the_cau as btc
                cau_dap = btc.sinh_dap_chua_uong_thuoc(ca, s.rng_mo_rong, tt=tt())
            else:
                cau_dap = f"{s.da(phu_dinh=True)}chưa uống gì{tt()}."
            s.ke(cau_dap)

    # Bệnh nhân VẮNG MẶT (người nhà đi thay): bác sĩ nói VỀ bệnh nhân ở ngôi thứ
    # ba, và KHÔNG khám được. Trước 11/09/2026 bối cảnh này vẫn "Toi kham qua mot
    # chut" rồi đọc kết quả khám — khám một người không có mặt (193 ca train).
    vang_mat = ca.boi_canh == "nguoi_nha_thay_mat"
    goi_hoi = _bn_ngoi_ba(ca) if vang_mat else ca.goi_bn

    # --- bác sĩ hỏi mà KHÔNG ai trả lời
    if "hoi_khong_dap" in ca.bay:
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            s.bs(s.rng_mo_rong.choice(btc.HOI_KHONG_DAP_MO_RONG).format(
                goi=goi_hoi, goi_hoa=_hoa(goi_hoi), tt=tt()))
        else:
            s.bs(rng.choice([
                f"Gần đây {goi_hoi} có đi đâu xa không{tt()}?",
                f"{_hoa(goi_hoi)} ngủ nghỉ thế nào{tt()}?",
                f"Ăn uống dạo này ra sao{tt()}?"]))
    if not vang_mat:
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            cau_ck = btc.sinh_chuyen_kham(ca.goi_bn, _hoa(ca.goi_bn), s.rng_mo_rong)
        else:
            cau_ck = rng.choice(nl.CHUYEN_KHAM).format(goi=ca.goi_bn, goi_hoa=_hoa(ca.goi_bn)) + s.dn() + "."
        s.bs(cau_ck)

    # --- khám
    if vang_mat:
        pass
    elif ca.boi_canh == "dieu_duong_ban_giao":
        # Sinh hiệu do ĐIỀU DƯỠNG đọc, không phải bác sĩ. Chủ thể vẫn là bệnh
        # nhân — đây là một bẫy quy gán thêm: người nói là vai thứ ba, hoàn
        # toàn không liên quan tới nội dung.
        if getattr(s, "mo_rong", False):
            loi_kham = benh['kham']
            l = s.noi("Điều dưỡng", loi_kham)
        else:
            l = s.noi("Điều dưỡng", f"Sinh hiệu em đo được: {benh['kham']}")
        s.ghi("bệnh nhân", benh["kham"].rstrip("."), "KHÁM LÂM SÀNG", l)
    else:
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            loi_kham = btc.sinh_kham(benh['kham'], s.rng_mo_rong)
            l = s.bs(loi_kham)
        else:
            l = s.bs(benh["kham"])
        s.ghi("bệnh nhân", benh["kham"].rstrip("."), "KHÁM LÂM SÀNG", l)

    # --- chẩn đoán và kế hoạch, khác nhau theo BỐI CẢNH
    if ca.boi_canh == "cho_ket_qua":
        # KHÔNG có chẩn đoán XÁC ĐỊNH. Bác sĩ nói rõ là CHƯA kết luận được.
        #
        # Đây là bối cảnh phục vụ thang thách thức 3: bộ dữ liệu trước đó không
        # có MỘT ca nào mà bệnh án dừng lại KHÔNG có chẩn đoán xác định, nên mô
        # hình chưa bao giờ thấy một ví dụ "chưa kết luận". Với nó, mỗi cuộc
        # khám đều kết thúc bằng một chẩn đoán — và đó là một thói quen nguy hiểm.
        xn = rng.choice(["xét nghiệm máu", "chụp X-quang", "siêu âm",
                         "xét nghiệm nước tiểu"])
        # Bỏ tiền tố "Theo dõi" của khuôn: trước đó câu này ra "toi nghi nhieu den
        # theo doi suy giap" — không phải tiếng Việt. Chỉ hạ chữ ĐẦU, giữ chữ viết
        # tắt ("HP"); bản cũ hạ hết cả câu.
        nghi, _muc = _muc_chan_doan(benh["chan_doan"])
        l_nghi = s.bs(f"Tôi nghĩ nhiều đến {nghi[:1].lower() + nghi[1:]}, nhưng "
                      f"chưa kết luận được. Phải có kết quả {xn} đã{s.dn()}.")
        # GHI nhận định đó với mục "nghi ngo" — thêm 11/09/2026. Trước đây bối
        # cảnh này không có mệnh đề chẩn đoán nào, nên `do_chac_chan = "nghi
        # ngo"` không có một ví dụ trong cả bộ dữ liệu. Bản tham chiếu in "Nghi
        # ngo X": đúng mức bác sĩ nói — không nâng thành chẩn đoán xác định,
        # cũng không bỏ mất nhận định.
        s.ghi("bệnh nhân", nghi, "CHẨN ĐOÁN", l_nghi, do_chac_chan="nghi ngờ")
        l = s.bs(f"{_hoa(ca.goi_bn)} đi làm {xn} rồi quay lại đây{s.dn()}.")
        s.ghi("bệnh nhân", f"làm {xn}", "KẾ HOẠCH ĐIỀU TRỊ", l,
              tinh_huong="kế hoạch")
    elif vang_mat:
        # Chưa khám thì chưa kết luận: nhận định ghi "nghi ngo", kế hoạch là đưa
        # bệnh nhân đến khám trực tiếp — không kê đơn cho người không có mặt.
        nghi, _muc = _muc_chan_doan(benh["chan_doan"])
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            cau_cd = s.rng_mo_rong.choice(btc.VANG_MAT_CHAN_DOAN).format(
                nn=ca.nguoi_ke[1], nghi=nghi[:1].lower() + nghi[1:], tt=tt())
            cau_kh = s.rng_mo_rong.choice(btc.VANG_MAT_KE_HOACH).format(
                nn=ca.nguoi_ke[1], nn_hoa=_hoa(ca.nguoi_ke[1]), goi_hoi=goi_hoi, dn=s.dn())
            l_nghi = s.bs(cau_cd)
            s.ghi("bệnh nhân", nghi, "CHẨN ĐOÁN", l_nghi, do_chac_chan="nghi ngờ")
            l = s.bs(cau_kh)
            s.ghi("bệnh nhân", "đưa bệnh nhân đến khám trực tiếp", "KẾ HOẠCH ĐIỀU TRỊ",
                  l, tinh_huong="kế hoạch")
        else:
            l_nghi = s.bs(f"Nghe {ca.nguoi_ke[1]} kể thì tôi nghĩ nhiều đến "
                          f"{nghi[:1].lower() + nghi[1:]}, nhưng chưa khám trực tiếp "
                          f"nên chưa kết luận được{tt()}.")
            s.ghi("bệnh nhân", nghi, "CHẨN ĐOÁN", l_nghi, do_chac_chan="nghi ngờ")
            l = s.bs(f"{_hoa(ca.nguoi_ke[1])} đưa {goi_hoi} đến để tôi khám trực "
                     f"tiếp{s.dn()}.")
            s.ghi("bệnh nhân", "đưa bệnh nhân đến khám trực tiếp", "KẾ HOẠCH ĐIỀU TRỊ",
                  l, tinh_huong="kế hoạch")
    else:
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            loi_cd = btc.sinh_chan_doan(benh['chan_doan'], s.rng_mo_rong)
            l = s.bs(loi_cd)
        else:
            l = s.bs(f"{benh['chan_doan']}")
        cd, muc_cd = _muc_chan_doan(benh["chan_doan"])
        s.ghi("bệnh nhân", cd, "CHẨN ĐOÁN", l, do_chac_chan=muc_cd)

        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            loi_kh = btc.sinh_ke_hoach(benh['ke_hoach'], s.rng_mo_rong)
            l = s.bs(loi_kh)
        else:
            l = s.bs(benh["ke_hoach"])
        s.ghi("bệnh nhân", benh["ke_hoach"].rstrip("."), "KẾ HOẠCH ĐIỀU TRỊ", l,
              tinh_huong="kế hoạch")

    # --- y lệnh thuốc của bác sĩ (ngừng thuốc, hoặc kê thuốc mới)
    _y_lenh_thuoc(s, ca, rng, tt)

    # --- câu giả định: KHÔNG được thành triệu chứng đã xảy ra
    if "gia_dinh" in ca.bay:
        dk = rng.choice(benh["chinh"])
        l = s.bs(f"Nếu mai {_bn_ngoi_ba(ca) if ca.nguoi_ke else ca.goi_bn} còn {dk} thì "
                 f"{rng.choice(nl.DAN_DO)} nhé.")
        # GHI mệnh đề này với tinh_huong="giả định" — cùng lý do với `quan_he`
        # (xem docstring MenhDe). Trước đây chỗ này không ghi gì cả, nên đáp án
        # có ĐÚNG HAI giá trị "thực tế" và "kế hoạch" trên cả 19.035 mệnh đề,
        # và mô hình trích chưa bao giờ nhìn thấy một ví dụ "giả định" nào.
        # Đó là lý do đầy đủ của việc nhánh C chỉ đạt 53% ở nhóm `gia_dinh`
        # trong khi nhánh A đạt 87%.
        #
        # Mệnh đề này KHÔNG vào bệnh án tham chiếu: `sinh_benh_an` bỏ qua
        # tinh_huong="giả định" (dòng đầu hàm). Nên bệnh án không đổi một ký tự,
        # đúng như bản sửa `dinh_chinh`.
        s.ghi("bệnh nhân", dk, "BỆNH SỬ HIỆN TẠI", l, tinh_huong="giả định")

    # --- kết: tự xưng trong lời chào phải là tự xưng của CHÍNH người nói. Trước
    # 11/09/2026 bốc ngẫu nhiên, nên người xưng "toi" cả cuộc kết bằng "Vang a, em
    # cảm ơn bác sĩ".
    tx = ca.nguoi_ke[2] if ca.nguoi_ke else ca.tu_xung_bn
    hop = [c for c in s.vung["chao_cuoi"]
           if set(re.findall(r"(?<!\w)(tôi|em|cháu|con)(?!\w)", c.lower())) <= {tx}]
    if getattr(s, "mo_rong", False):
        from src.bo_du_lieu import bien_the_cau as btc
        cau_chao = btc.sinh_chao_cuoi(ca, tx, s.rng_mo_rong)
    else:
        cau_chao = rng.choice(hop) if hop else f"{s.da()}{tx} cảm ơn bác sĩ{tt()}."
    s.ke(cau_chao)
    return s


# ------------------------------------- bề nội dung người nhà, CHIA THEO TẬP
#
# VÌ SAO. Trước 11/09/2026 cả ba tập rút nội dung người nhà từ CÙNG một bảng,
# và tập phát triển dùng lại đúng 25/25 chuỗi của train (284/284 mệnh đề tầng
# 4). Dự án chia tập theo khuôn để đo khả năng khái quát, nhưng từ vựng người
# nhà đi xuyên qua cả ba tập — nên tầng 4, chỗ quan trọng nhất, chưa bao giờ
# được thử trên nội dung CHƯA THẤY.
#
# Nay mỗi tập có bể riêng, KHÔNG chồng nhau: một nội dung rơi vào đúng một tập,
# theo băm của chính chuỗi đó. Tập của MỘT CA suy từ khuôn bệnh của nó, qua
# `tach_tap_viet.phan_khuon` — CÙNG hàm mà bước chia tập dùng, để hai chỗ không
# thể trôi nhau.
#
# Chia TỪNG BẢNG riêng (bệnh mọi tuổi, bệnh tuổi già, dị ứng) để mỗi tập có tỷ
# lệ của mỗi loại, thay vì một tập có thể rỗng hẳn một loại.
_DAI_TAP = {"train": (0.0, 0.70), "phat_trien": (0.70, 0.85),
            "kiem_tra_cuoi": (0.85, 1.0)}


# ═══ dai_cua() — Tính vị trí ổn định trong [0, 1) của một nội dung ════════════════════
# Dựa trên băm, không phụ thuộc thứ tự; dùng để chia bể theo tập.
def dai_cua(noi_dung):
    """Vị trí ổn định trong [0, 1) của một nội dung. Không phụ thuộc thứ tự."""
    h = hashlib.sha256(f"nguoi-nha:{noi_dung}".encode("utf-8")).hexdigest()
    return int(h[:12], 16) / float(16 ** 12)


# ─── _be_cache() — Lọc bể nội dung người nhà theo dải của tập ─────────────────────────
# Báo lỗi nếu bể rỗng để không lấy từ tập khác.
@functools.lru_cache(maxsize=None)
def _be_cache(cac_muc, tap):
    lo, hi = _DAI_TAP[tap]
    ra = tuple(x for x in cac_muc if lo <= dai_cua(x) < hi)
    if not ra:
        # Một tập có bể RỖNG là một lo~: bộ sinh sẽ phải lấy từ tập khác, và đó
        # đúng là rò rỉ mà bể theo tập được dựng ra để chặn. Báo lỗi thay vì lùi.
        raise ValueError(f"be noi dung nguoi nha cua tap {tap!r} rong")
    return ra


# ═══ be_theo_tap() — Lấy các nội dung người nhà thuộc một tập ═════════════════════════
# Mỗi nội dung thuộc đúng một tập.
def be_theo_tap(cac_muc, tap):
    """-> các nội dung thuộc `tap`. Mỗi nội dung thuộc ĐÚNG MỘT tập."""
    return list(_be_cache(tuple(cac_muc), tap))


# ─── _bang_tap_khuon() — Lập bảng tên khuôn sang tập ──────────────────────────────────
# Dựa trên hàm phân khuôn theo tên.
@functools.lru_cache(maxsize=1)
def _bang_tap_khuon(cac_khuon):
    p = tach_tap_viet.phan_khuon(list(cac_khuon))
    return {ten: tap for tap, cac in p.items() for ten in cac}


# ═══ bang_tap_khuon() — Bảng khuôn sang tập mà bộ sinh giả định ═══════════════════════
# Bước chia đối chiếu với bảng này để bắt lệch.
def bang_tap_khuon(mo_rong: bool = False):
    """-> {tên khuôn: tập} MÀ BỘ SINH GIẢ ĐỊNH khi chọn bể nội dung người nhà.

    `tach_tap_viet.kiem_khop_bo_sinh` đối chiếu bước chia với bảng này.
    """
    ds = kho_khuon.ds_khuon(mo_rong)
    return dict(_bang_tap_khuon(tuple(b["ten"] for b in ds)))


# ═══ tap_cua_ca() — Cho biết ca sẽ rơi vào tập nào sau khi chia ═══════════════════════
# Suy ra từ tên khuôn bệnh.
def tap_cua_ca(ca, mo_rong: bool = False):
    """-> tập mà ca này sẽ rơi vào sau bước chia. Suy từ TÊN KHUÔN."""
    ds = kho_khuon.ds_khuon(mo_rong)
    return _bang_tap_khuon(tuple(b["ten"] for b in ds))[ca.benh["ten"]]


# ─── _hop_gioi() — Kiểm tra bệnh hợp giới của người mang ──────────────────────────────
# Khuôn chỉ ở nữ hoặc chỉ ở nam không được gán sai giới.
def _hop_gioi(benh, vai):
    """"Bộ bị u xơ tử cung" thì bác sĩ đọc qua là thấy sai ngay."""
    if vai in nl.VAI_NAM and benh in kho_khuon.chi_nu():
        return False
    if vai in nl.VAI_NU and benh in kho_khuon.chi_nam():
        return False
    return True


# ─── _benh_hop_tuoi() — Chọn bệnh hợp tuổi, giới của người mang, thuộc bể tập ─────────
# Người nhà hợp lý nên bệnh án không có chi tiết vô lý.
def _benh_hop_tuoi(ai: str, ca: Ca, rng: random.Random, mo_rong: bool = False) -> str:
    """Bệnh phải hợp lứa tuổi VÀ GIỚI của người mang nó, và thuộc bể của TẬP.

    Một người mẹ trẻ đưa con đi khám mà "bi tai bien mach mau nao" thì bác sĩ
    đọc qua là thấy sai ngay — và tính hợp lý của ca bệnh cũng là một phần chất
    lượng dữ liệu, không phải chi tiết trang trí. Cùng lý do đó cho giới: từ
    11/09/2026 bể có bệnh chỉ có ở một giới (xem `nl.CHI_NU`, `nl.CHI_NAM`).
    """
    thuc = ai if ai != "người kể" else (_ten_nguoi_ke(ca) if ca.nguoi_ke else "bệnh nhân")
    tap = tap_cua_ca(ca, mo_rong=mo_rong)
    if thuc in nl.NGUOI_LON_TUOI and rng.random() < 0.55:
        ung = [b for b in be_theo_tap(nl.TIEN_SU_GIA_DINH_LON_TUOI, tap)
               if _hop_gioi(b, thuc)]
        if ung:
            return rng.choice(ung)
    ung = [b for b in be_theo_tap(nl.TIEN_SU_GIA_DINH_MOI_TUOI, tap)
           if _hop_gioi(b, thuc)]
    return rng.choice(ung)


# ─── _nguoi_nha_khac() — Chọn một người nhà khác để làm chủ thể ───────────────────────
# Có thể chọn chính người kể với xác suất 0,55.
def _nguoi_nha_khac(ca: Ca, rng, cho_phep_nguoi_ke=True) -> str:
    ung_vien = ["mẹ", "bố", "bà ngoại", "bà nội", "ông nội", "anh trai", "chị gái"]
    if ca.nguoi_ke and cho_phep_nguoi_ke and rng.random() < 0.55:
        return "người kể"
    return rng.choice(ung_vien)


# ------------------------------------------------------------- sinh bệnh án

# ═══ sinh_benh_an() — Viết bệnh án chỉ từ các mệnh đề đã nói ══════════════════════════
# Chủ thể khác bệnh nhân phải ghi tên và không vào mục của bệnh nhân; bỏ mệnh đề giả
# định.
def sinh_benh_an(menh_de: List[MenhDe]) -> str:
    """Bệnh án CHỈ gồm mệnh đề đã được nói ra. Chủ thể khác bệnh nhân thì phải
    ghi rõ tên người, và không được vào mục của bệnh nhân."""
    theo_muc = {}
    for m in menh_de:
        if m.tinh_huong == "giả định":
            continue
        # Bản đã bị đính chính không vào bệnh án tham chiếu. Nó vẫn nằm trong
        # ĐÁP ÁN để đo được bước phát hiện quan hệ — hai thứ đo khác nhau.
        if m.trang_thai == "bị thay thế":
            continue
        # MÂU THUẪN CHƯA GIẢI QUYẾT: hai bản cùng nội dung, khác mốc. In cả hai
        # thành hai dòng là viết một bệnh án nói bệnh nhân sốt "hơn một tuần" VÀ
        # "gần một tuần" — đọc là thấy sai ngay. Bệnh án thật ghi một dòng, nêu
        # rõ là chưa rõ, đúng như câu bác sĩ nói trong hội thoại.
        #
        # Gộp ở đây chứ không gộp trong `dap_an`: đáp án phải giữ CẢ HAI bản để
        # đo được bước phát hiện quan hệ. Hai việc khác nhau.
        if m.trang_thai == "chưa giải quyết" and m.quan_he == "mâu thuẫn":
            continue          # bản thứ hai — đã gộp vào bản thứ nhất bên dưới
        cum = m.noi_dung
        # Chi tiết thuốc (15/09/2026) — DÙNG hàm của đường ống, không viết lại: hai
        # khâu in chi tiết thuốc theo hai cách thì bản tham chiếu và bản nháp lệch
        # chữ, và mọi thước đo so văn bản phát lệch đó thành lỗi.
        if m.thuoc:
            from src.duong_ong.b5_viet_ban_nhap import _them_chi_tiet_thuoc
            cum = _them_chi_tiet_thuoc(cum, m.thuoc)
        if m.chu_the != "bệnh nhân":
            cum = f"{_hoa(m.chu_the)} {cum}"
        # Ba mức chắc chắn in thành ba cách KHÁC NHAU, giống `sinh_benh_an.
        # dien_dat` của đường ống. Trước 11/09/2026 mọi `phu_dinh` đều in thành
        # "Chua ghi nhan": một khẳng định ÂM ("khong di ung") và một chỗ TRỐNG
        # ("chua thay bi bao gio") ra cùng một chữ, trong khi bản nháp của
        # đường ống in "khong ..." cho cùng mệnh đề đó — hai khâu lệch nhau.
        elif m.do_chac_chan == "chưa ghi nhận":
            cum = f"Chưa ghi nhận {cum}"
        elif m.do_chac_chan == "nghi ngờ":
            # Nội dung đã tự mang dấu rào đón ("Viem hong nghi do lien cau") thì
            # không thêm "Nghi ngo" lần nữa.
            if not re.search(r"(?<!\w)nghi(?!\w)", cum, re.I):
                cum = f"Nghi ngờ {cum}"
        elif m.phu_dinh:
            cum = f"Không {cum}"
        if m.moc_thoi_gian and m.muc == "BỆNH SỬ HIỆN TẠI":
            xung = [k for k in menh_de
                    if k.quan_he == "mâu thuẫn" and k.quan_he_voi is m
                    and k.moc_thoi_gian]
            if xung:
                cum = (f"{cum} (chưa rõ {m.moc_thoi_gian} hay "
                       f"{xung[0].moc_thoi_gian})")
            else:
                cum = f"{cum} ({m.moc_thoi_gian})"
        theo_muc.setdefault(m.muc, [])
        if cum not in theo_muc[m.muc]:
            theo_muc[m.muc].append(cum)

    # Nêu rõ CHỦ NGỮ ở câu đầu BENH SU HIEN TAI. Bệnh án thật mở đầu kiểu
    # "Benh nhan nam 45 tuoi, dau bung..." chứ không lược chủ ngữ hoàn toàn.
    #
    # Ngoài chuyện giống thật hơn, chỗ này còn cần cho phép thử chứng chỉ
    # thước đo: phép thử đổi chỗ từ chỉ BỆNH NHÂN với từ chỉ NGƯỜI NHÀ ở hai
    # câu khác nhau. Khi bệnh án lược hết chủ ngữ thì không có gì để đổi —
    # đo 2.231 bản chỉ 21 bản có từ chỉ bệnh nhân, và chỉ 2 bản dùng được.
    if theo_muc.get("BỆNH SỬ HIỆN TẠI"):
        dau = theo_muc["BỆNH SỬ HIỆN TẠI"][0]
        if not dau.lower().startswith(("bệnh nhân", "chưa ghi nhận")):
            theo_muc["BỆNH SỬ HIỆN TẠI"][0] = f"bệnh nhân {dau}"

    khoi = []
    for muc in MUC:
        if muc not in theo_muc:
            continue
        noi_dung = "; ".join(theo_muc[muc])
        khoi.append(f"{muc}\n\n{_hoa(noi_dung)}.")
    return "\n\n".join(khoi)


# ------------------------------------------------------------------ sinh bộ

# ─── _chon_bay() — Chọn 0 đến 3 bẫy cho một ca ────────────────────────────────────────
# Phân bố độc lập với độ dài hội thoại.
def _chon_bay(rng: random.Random) -> List[str]:
    """Mỗi ca mang 0-3 bẫy. Phân bố độc lập với độ dài hội thoại."""
    n = rng.choices([0, 1, 2, 3], weights=[22, 34, 30, 14])[0]
    return sorted(rng.sample(BAY_RUT, k=n))


# ─── _du_dieu_kien_nguon_khac_nhau() — Kiểm tra ca đủ điều kiện có hai nguồn cùng nói ───
# Cần người lớn, có người kể và không có bẫy đính chính hay mâu thuẫn.
def _du_dieu_kien_nguon_khac_nhau(ca: Ca) -> bool:
    """Hai NGUỒN phải cùng có mặt và cùng nói: bệnh nhân người lớn, có người nhà
    kể, bệnh nhân không vắng mặt, và triệu chứng chính chưa mang bẫy khác."""
    return (ca.nguoi_ke is not None and not ca.la_tre_em
            and ca.boi_canh != "nguoi_nha_thay_mat"
            and not ({"dinh_chinh", "mau_thuan"} & set(ca.bay)))


# PHƯƠNG NGỮ CHỈ Ở TẬP ĐÁNH GIÁ — quyết định 11/09/2026.
#
# Bảng thay (`phuong_ngu.THAY_DUOC`) lấy từ từ điển người dùng cung cấp, mà người
# dùng xác nhận ngày 11/09/2026 là do GPT SINH. Dự án có ràng buộc cứng: không
# dùng mô hình ngôn ngữ thương mại ở bất kỳ khâu nào, KỂ CẢ sinh dữ liệu huấn
# luyện. Nên từ ngày đó khuôn TRAIN không nhận từ nào từ bảng đó; tập phát triển,
# tập kiểm tra cuối và bộ thách thức phương ngữ vẫn có.
#
# Cái giá và cái lời: mô hình không còn học 10 cặp từ đó trong lúc huấn luyện, nên
# trên tập phát triển nó gặp phương ngữ LẦN ĐẦU — đúng câu hỏi "chịu được phương
# ngữ chưa gặp không" mà bộ thách thức muốn hỏi. Tiểu từ vùng miền ("nghen", "ha")
# là của chính bộ sinh từ trước, không từ bảng GPT, vẫn giữ ở mọi tập.
#
# Thế hệ 4 (chuỗi chạy 11/09/2026) ĐÃ huấn luyện trên dữ liệu có 10 cặp thay này:
# phải ghi rõ khi dùng số của thế hệ 4.
PHUONG_NGU_TRONG_TRAIN = False


# ─── _xa_giao() — Chèn 0-2 trao đổi xã giao không có thông tin lâm sàng ───────────────
# Làm độ dài ca có bẫy không khác ca không bẫy.
def _xa_giao(s, ca, rng) -> None:
    """Chèn 0-2 trao đổi xã giao, KHÔNG mang thông tin lâm sàng.

    VÌ SAO CÓ. Ca MANG BẪY dài hơn ca không bẫy, đo được trên 400 ca: trung bình
    14,3 so với 12,8 lượt. Chênh 1,5 lượt đó là một đường tắt thật — đếm số lượt
    là đoán được ca này có bẫy hay không, và khi ấy mọi số đo trên bộ dữ liệu đều
    lẫn một phần "đoán theo độ dài". `test_do_dai_KHONG_lo_ca_nao_co_bay` canh
    đúng chỗ này và đã báo đó.

    VÌ SAO CHÈN CHO CẢ HAI NHÓM, KHÔNG CHỈ CHO NHÓM KHÔNG BẪY. Chèn riêng cho ca
    không bẫy thì vừa bịt được một mảnh mồi đã tạo ra một mảnh mồi khác: sự có
    mặt của đoạn xã giao TRỞ THÀNH dấu hiệu "ca này không có bẫy". Số lượng lấy
    ngẫu nhiên và ĐỘC LẬP với `ca.bay`, nên nó làm loãng cả hai phân bố chứ không
    đẩy một phân bố sang chỗ khác.

    KHÔNG gọi `s.ghi`: một cặp xã giao không sinh mệnh đề nào. Nếu một ngày nào đó
    nó sinh, đáp án sẽ dài thêm mà không ai có ý đó — nên `test_xa_giao_KHONG_sinh
    _menh_de` chốt điều đó lại.
    """
    for _ in range(rng.choice((0, 1, 1, 2))):
        hoi, dap = rng.choice(nl.XA_GIAO)
        if getattr(s, "mo_rong", False):
            from src.bo_du_lieu import bien_the_cau as btc
            hoi_mr, dap_mr = btc.sinh_xa_giao(ca, s.rng_mo_rong)
            s.bs(hoi_mr)
            s.ke(dap_mr)
        else:
            s.bs(hoi.format(goi=ca.goi_bn, goi_hoa=_hoa(ca.goi_bn)))
            s.ke(dap)


# ═══ sinh_mot_ca() — Sinh một ca hoàn chỉnh kèm đáp án có cấu trúc ════════════════════
# Bộ chính và bộ thử thách đi qua cùng một đường này.
def sinh_mot_ca(ma: str, rng: random.Random,
                tuy: Optional[TuyChon] = None) -> dict:
    """MỘT ca hoàn chỉnh. `sinh_bo` là chuỗi các lần gọi hàm này với CÙNG một
    `rng` — bộ chính và bộ thách thức (`src.bo_du_lieu.sinh_bo_thach_thuc`) đi qua cùng một đường,
    có test canh."""
    tuy = tuy or TuyChon()
    ca = sinh_ca(ma, rng, chi_tap=tuy.chi_tap, ep_mien=tuy.ep_mien,
                 ep_nguoi_ke=tuy.ep_nguoi_ke, mo_rong=tuy.mo_rong)
    # Tắt phương ngữ SAU khi rút khuôn: `_Soan` rút hạt giống cho lớp phương ngữ
    # trên một `rng` riêng, nên tắt hay bật không đổi gì khác trong ca.
    if tuy.ap_phuong_ngu and not PHUONG_NGU_TRONG_TRAIN and tap_cua_ca(ca, mo_rong=tuy.mo_rong) == "train":
        from dataclasses import replace
        tuy = replace(tuy, ap_phuong_ngu=False)
    ca.bay = _chon_bay(rng)
    # Bẫy ÉP thêm (chỉ bộ thách thức). Bẫy BẬT RIÊNG không thêm ở đây — chúng có
    # điều kiện riêng, xét bên dưới.
    ca.bay = sorted(set(ca.bay) | (set(tuy.ep_bay) - set(BAY_BAT_RIENG)))
    if ca.nguoi_ke:
        ca.bay = sorted(set(ca.bay) | {"nguoi_nha_ke_ho"})
    elif "nguoi_nha_ke_ho" in ca.bay:
        ca.bay.remove("nguoi_nha_ke_ho")
    # Hai bẫy này cần có người nhà trong hội thoại mới có nghĩa.
    if not ca.nguoi_ke:
        ca.bay = [b for b in ca.bay if b != "di_ung_nguoi_nha"]
    # `dinh_chinh` và `mau_thuan` cùng nhắm vào mệnh đề triệu chứng chính,
    # và một mốc thời gian KHÔNG THỂ vừa đã được đính chính vừa đang mâu
    # thuẫn: đính chính có nghĩa là đã có bản thắng, mâu thuẫn có nghĩa là
    # chưa có. Giữ `dinh_chinh` vì nó có trước, để số liệu cũ còn so sánh
    # được — trừ khi `mau_thuan` là bẫy bị ÉP (bộ thách thức).
    if "dinh_chinh" in ca.bay and "mau_thuan" in ca.bay:
        bo = "dinh_chinh" if "mau_thuan" in tuy.ep_bay else "mau_thuan"
        ca.bay = [b for b in ca.bay if b != bo]
    # Bẫy tầng 4, bật RIÊNG ngoài `_chon_bay` — xem TY_LE_NGUOI_KE_BENH_MINH.
    if ca.nguoi_ke and rng.random() < TY_LE_NGUOI_KE_BENH_MINH:
        ca.bay = sorted(set(ca.bay) | {"nguoi_ke_benh_minh"})
    # Bẫy hai nguồn, cũng bật RIÊNG — xem TY_LE_NGUON_KHAC_NHAU. Rút số TRƯỚC khi
    # xét bẫy ép, để ép hay không ép đều đi cùng một đường rút số.
    if _du_dieu_kien_nguon_khac_nhau(ca):
        rut = rng.random() < TY_LE_NGUON_KHAC_NHAU
        if rut or "nguon_khac_nhau" in tuy.ep_bay:
            ca.bay = sorted(set(ca.bay) | {"nguon_khac_nhau"})

    s = sinh_hoi_thoai(ca, rng, tuy)
    hoi_thoai = "\n".join(f"{vai}: {cau}" for vai, cau in s.luot)
    # Đáp án tính TRƯỚC bản bệnh án mẫu: trích dẫn phải tìm trên nội dung CHUẨN
    # (lời gốc còn chữ "sot"), rồi mới đổi nội dung sang lời người nói — xem
    # `_giu_loi_nguoi_noi`. Đổi trước thì trích dẫn lùi về cả lượt.
    dap_an = _dap_an(s.menh_de, s.luot, s.luot_goc)
    _giu_loi_nguoi_noi(s.menh_de, dap_an)
    ket_qua = {
        "id": ca.ma,
        "input": hoi_thoai,
        "output": sinh_benh_an(s.menh_de),
        "bay": ca.bay,
        "so_luot": len(s.luot),
        "benh": ca.benh["ten"],
        "la_tre_em": ca.la_tre_em,
        "nguoi_ke": ca.nguoi_ke[0] if ca.nguoi_ke else None,
        "lo_danh_tinh": ca.lo_danh_tinh,
        "boi_canh": ca.boi_canh,
        "tu_phuong_ngu": sorted(set(s.tu_phuong_ngu)),
        "cum_dan_thuong": sorted(set(s.cum_dan_thuong)),
        "dap_an": dap_an,
    }
    if tuy and tuy.mo_rong:
        ket_qua["khuon_da_duyet"] = ca.benh.get("da_duyet", False)
        ket_qua["he_co_quan"] = ca.benh.get("he_co_quan", "")
    return ket_qua


# ─── _giu_loi_nguoi_noi() — Đổi mệnh đề giữ cụm phương ngữ không đồng nghĩa ───────────
# Hiện chỉ có nóng hầm hập; sửa cả MenhDe và bản ghi đáp án.
def _giu_loi_nguoi_noi(menh_de: List[MenhDe], dap_an: List[dict]) -> None:
    """Cụm phương ngữ không đồng nghĩa (`phuong_ngu.GIU_NGUYEN`, hiện chỉ có "nong
    ham hap"): nội dung mệnh đề ghi đúng lời người nói thay vì từ chuẩn. Đổi CẢ
    `MenhDe` (cho `sinh_benh_an`) LẪN bản ghi đáp án. Sửa 24/09/2026."""
    from src.bo_du_lieu import phuong_ngu as phuong_ngu
    for m, d in zip(menh_de, dap_an):
        moi = phuong_ngu.giu_loi_nguoi_noi(m.noi_dung, d["trich_dan"])
        if moi != m.noi_dung:
            m.noi_dung = moi
            d["noi_dung"] = moi


# ═══ sinh_bo() — Sinh một bộ nhiều ca với cùng hạt giống ══════════════════════════════
# Mỗi ca có mã tăng dần; bật mở rộng thì dùng các biến thể câu đa tầng.
# Seed 42 là seed ĐÃ DÙNG để sinh `hoi_thoai_viet_3000.jsonl`. Mặc định
# trước đây là 2026, không khớp với tệp đang nằm trong kho — chạy lại lệnh
# mặc định sẽ ra một bộ KHÁC, và không ai biết chỗ tới khi số liệu lệch.
def sinh_bo(so_ca: int, seed: int = 42, mo_rong: bool = False) -> List[dict]:
    rng = random.Random(seed)
    tuy = TuyChon(mo_rong=mo_rong) if mo_rong else None
    prefix = "v2mr" if mo_rong else "hv"
    return [sinh_mot_ca(f"{prefix}_{i + 1:04d}", rng, tuy=tuy) for i in range(so_ca)]


# ─── _dap_an() — Đổi các mệnh đề thành danh sách đáp án JSON ──────────────────────────
# Đổi con trỏ quan hệ thành chỉ số trong danh sách và tính câu trích.
def _dap_an(menh_de: List[MenhDe], luot=None, luot_goc=None) -> List[dict]:
    """Đổi `quan_he_voi` từ con trỏ sang CHỈ SỐ trong chính danh sách này.

    Dùng chỉ số chứ không dùng tên: hai mệnh đề có thể trùng nội dung (đúng
    là trường hợp của `dinh_chinh` — cùng nội dung, khác mốc), nên tên không
    xác định duy nhất. Lược đồ trích của `bakeoff` cũng dùng chỉ số đếm từ 0.

    `trich_dan` tính Ở ĐÂY, khi hội thoại đã xong: mệnh đề còn được thêm lượt
    sau khi ghi (bẫy đính chính thêm lượt sửa vào bản cũ), nên tính lúc `ghi`
    là tính trên một danh sách lượt chưa đủ.
    """
    vi_tri = {id(m): i for i, m in enumerate(menh_de)}
    return [
        {"chu_the": m.chu_the, "noi_dung": m.noi_dung, "muc": m.muc,
         "moc_thoi_gian": m.moc_thoi_gian, "phu_dinh": m.phu_dinh,
         "tinh_huong": m.tinh_huong, "luot": m.luot,
         # Thêm 11/09/2026. Danh sách trường ở đây được gõ TAY, nên thêm trường
         # vào `MenhDe` mà quên dòng này thì đáp án không mang nó — và không có
         # gì báo lỗi: bộ sinh vẫn chạy, tệp vẫn đúng định dạng, chỉ là nhãn mới
         # không bao giờ ra tệp. Đã xảy ra đúng thế: lần đầu thêm trường này,
         # cả 4.533 mệnh đề đều có `thoi_gian_su_kien = None`.
         "thoi_gian_su_kien": m.thoi_gian_su_kien,
         "quan_he": m.quan_he,
         "quan_he_voi": (vi_tri.get(id(m.quan_he_voi))
                         if m.quan_he_voi is not None else None),
         "trang_thai": m.trang_thai,
         "do_chac_chan": m.do_chac_chan,
         "hanh_vi": m.hanh_vi,
         # Thêm 15/09/2026 — cùng họ lỗi ở chú thích ngay trên: quên dòng này thì
         # bộ sinh vẫn chạy và đáp án không bao giờ mang chi tiết thuốc.
         "thuoc": dict(m.thuoc) if m.thuoc else None,
         "trich_dan": (_trich_dan(m, luot, luot_goc)
                       if luot is not None else [])}
        for m in menh_de]


# ------------------------------------------------------- đoạn bằng chứng
#
# Cách cắt ĐOẠN dùng chung với tầng khoá bằng chứng — MỘT định nghĩa, ở
# `src.duong_ong.b0_cat_doan_van`. Hai chỗ cắt đoạn khác nhau thì trích dẫn của đáp án và đoạn mà
# khoá kiểm sẽ lệch nhau mà không báo lỗi.
from src.duong_ong.b0_cat_doan_van import cac_doan  # noqa: E402


# ─── _trich_mot_luot() — Tìm đoạn ngắn nhất trong một lượt nói ra mệnh đề ─────────────
# Tìm trên lời gốc rồi lấy đoạn cùng chỉ số trên lời thật, nguyên văn.
def _trich_mot_luot(md: MenhDe, so: int, luot, luot_goc) -> str:
    """Đoạn NGẮN NHẤT trong lượt `so` nói ra mệnh đề `md`, NGUYÊN VĂN.

    Tìm đoạn trên LỜI GỐC (trước tầng ngữ vực và tầng vùng), vì ở đó thuật ngữ
    chuẩn còn nguyên: "buon non" còn là "buon non", chưa thành "non nao". Rồi
    lấy ĐOẠN CÙNG CHỈ SỐ trên lời thật — hai tầng đó không thêm bớt dấu câu,
    nên số đoạn hai bên bằng nhau (có test canh; lệch thì lùi về cả lượt).

    Ba bước, theo thứ tự:
      1. gợi ý `md.goi_y_doan` — cho mệnh đề nói TẮT
      2. cửa sổ đoạn NGẮN NHẤT phủ hết các từ nội dung tìm thấy trong lượt
      3. không từ nào khớp (câu trả lời tắt "Da, khong a") -> cả lượt
    """
    from src.do_luong.thuoc_do_quy_gan import _tu_noi_dung
    van = luot[so - 1][1]
    goc = luot_goc[so - 1]
    d_van, d_goc = cac_doan(van), cac_doan(goc)
    if not d_van or len(d_van) != len(d_goc):
        return van.strip()
    if so in md.goi_y_doan:
        i = md.goi_y_doan[so]
        i = i if i >= 0 else len(d_van) + i
        if 0 <= i < len(d_van):
            return van[d_van[i][0]:d_van[i][1]]
    tu = set(_tu_noi_dung(md.noi_dung))
    if md.moc_thoi_gian:
        tu |= set(_tu_noi_dung(md.moc_thoi_gian))
    # Chi tiết thuốc thường nằm ở đoạn SAU dấu phẩy ("amlodipin 5 mg, ngay mot lan").
    # Không thêm từ của chúng thì trích dẫn chỉ phủ tên thuốc, và khoá bằng chứng
    # không còn đoạn nào chống lưng cho liều (15/09/2026).
    for k in ("lieu", "so_lan", "bat_dau", "ngung"):
        if md.thuoc and md.thuoc.get(k):
            tu |= set(_tu_noi_dung(md.thuoc[k]))
    phu = [tu & set(_tu_noi_dung(goc[a:b])) for a, b in d_goc]
    can = set().union(*phu)
    if not can:
        return van.strip()
    tot = None
    for a in range(len(phu)):
        gop = set()
        for b in range(a, len(phu)):
            gop |= phu[b]
            if gop >= can:
                if tot is None or b - a < tot[1] - tot[0]:
                    tot = (a, b)
                break
    a, b = tot
    return van[d_van[a][0]:d_van[b][1]]


# ─── _trich_dan() — Trích một đoạn cho mỗi lượt của mệnh đề ───────────────────────────
# Thẳng hàng từng phần tử với danh sách lượt.
def _trich_dan(md: MenhDe, luot, luot_goc) -> List[str]:
    """Mỗi lượt trong `md.luot` một đoạn — thẳng hàng từng phần tử."""
    return [_trich_mot_luot(md, so, luot, luot_goc) for so in md.luot]


# ─── _xuat_mau_duyet() — Xuất tệp Markdown để bác sĩ duyệt các ca đầu ─────────────────
# Để đọc độ tự nhiên, cách xưng hô và tính toàn vẹn câu trích.
def _xuat_mau_duyet(cac_ca: list[dict], duong_dan_md: Path, so_ca: int = 50) -> None:
    lines = [
        f"# MẪU DUYỆT LÂM SÀNG BỘ DỮ LIỆU V2 MỞ RỘNG ({so_ca} CA ĐẦU TIÊN)",
        "",
        "> **Mục đích:** Bác sĩ / Hội đồng chuyên môn đọc kiểm tra độ tự nhiên, tính hợp lý lâm sàng, "
        "đại từ xưng hô, và tính toàn vẹn của trích dẫn.",
        "",
        "---",
        ""
    ]
    for idx, ca in enumerate(cac_ca[:so_ca], 1):
        lines.append(f"## Ca {idx:02d} — Mã: `{ca['id']}`")
        lines.append(f"- **Khuôn bệnh:** `{ca.get('benh', 'N/A')}`")
        lines.append(f"- **Miền:** `{ca.get('mien', 'N/A')}` | **Bối cảnh:** `{ca.get('boi_canh', 'N/A')}`")
        lines.append(f"- **Bẫy quy gán:** `{', '.join(ca.get('bay', [])) or 'Không có'}`")
        lines.append("")
        lines.append("### Hội thoại Lâm sàng (Input):")
        lines.append("```text")
        lines.append(ca["input"].strip())
        lines.append("```")
        lines.append("")
        lines.append("### Đáp án Mệnh đề (Trích xuất):")
        lines.append("| Mục | Chủ thể | Nội dung | Tình huống | Độ chắc chắn | Trích dẫn |")
        lines.append("|---|---|---|---|---|---|")
        for md in ca.get("dap_an", []):
            muc = md.get("muc", "")
            ct = md.get("chu_the", "")
            nd = md.get("noi_dung", "")
            th = md.get("tinh_huong", "")
            dc = md.get("do_chac_chan", "")
            tc = "; ".join(md.get("trich_dan", []))
            lines.append(f"| {muc} | {ct} | {nd} | {th} | {dc} | {tc} |")
        lines.append("")
        lines.append("---")
        lines.append("")
    duong_dan_md.write_text("\n".join(lines), encoding="utf-8")


# ═══ main() — Điểm vào dòng lệnh để sinh bộ hội thoại tiếng Việt ══════════════════════
# Các tham số: số ca, hạt giống, tệp ra, mở rộng, xuất mẫu duyệt; ghi kèm báo cáo.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--so-ca", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--ra", "--dau-ra", default=None)
    ap.add_argument("--mo-rong", action="store_true", default=False,
                    help="Bat cac bien the cau da tang va khuon mo rong v2")
    ap.add_argument("--xuat-mau-duyet", default=None,
                    help="Xuat tep markdown doc mau N ca (mac dinh 50 ca)")
    a = ap.parse_args()

    bo = sinh_bo(a.so_ca, a.seed, mo_rong=a.mo_rong)
    # `--ra` là TÊN TỆP trong thư mục dữ liệu, không phải đường dẫn tương đối
    # theo chỗ đang đứng. Trước đây nó là đường dẫn thô, nên
    # `--ra hoi_thoai_viet_3000.jsonl` ghi vào gốc kho chứ không vào `data/`,
    # và lệnh chia tập ngay sau đó đọc phải bản CŨ mà không bao gi.
    # Đường dẫn tuyệt đối vẫn dùng được, cho ai có ý muốn ghi ra chỗ khác.
    from pathlib import Path
    dp = duong_dan.THU_MUC_DU_LIEU / "hoi_thoai_viet.jsonl"
    if a.ra:
        p = Path(a.ra)
        dp = p if p.is_absolute() else duong_dan.THU_MUC_DU_LIEU / p.name
    with open(dp, "w", encoding="utf-8") as f:
        for m in bo:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    if a.xuat_mau_duyet:
        p_md = Path(a.xuat_mau_duyet)
        dp_mau = p_md if p_md.is_absolute() else duong_dan.GOC_DU_AN / p_md
        dp_mau.parent.mkdir(parents=True, exist_ok=True)
        _xuat_mau_duyet(bo, dp_mau, so_ca=50)
        print(f"da xuat mau duyet: {dp_mau}")

    import collections
    dem_bay = collections.Counter(b for m in bo for b in m["bay"])
    tk = {
        "so_ca": len(bo),
        "so_khuon_benh": len(nl.BENH),
        "hoi_thoai_duy_nhat": len({m["input"] for m in bo}),
        "tong_luot": sum(m["so_luot"] for m in bo),
        "luot_moi_ca": round(sum(m["so_luot"] for m in bo) / len(bo), 1),
        "tong_tu": sum(len(m["input"].split()) for m in bo),
        "so_menh_de": sum(len(m["dap_an"]) for m in bo),
        "menh_de_khong_phai_benh_nhan": sum(
            1 for m in bo for d in m["dap_an"] if d["chu_the"] != "bệnh nhân"),
        "ca_nhi": sum(1 for m in bo if m["la_tre_em"]),
        "co_nguoi_nha_ke": sum(1 for m in bo if m["nguoi_ke"]),
        "bay": dict(dem_bay.most_common()),
    }
    print(f"{len(bo)} ca -> {dp}")
    for k, v in tk.items():
        if k != "bay":
            print(f"   {k}: {v}")
    print("bẫy:")
    for k, v in dem_bay.most_common():
        print(f"   {v:5d}  {k}")

    dp_md = duong_dan.THU_MUC_KET_QUA / "bo-du-lieu-viet.md"
    dp_md.write_text(_bao_cao(tk), encoding="utf-8")
    print(f"\nda ghi {dp_md}")


# ─── _bao_cao() — Viết báo cáo Markdown mô tả bộ vừa sinh ─────────────────────────────
# Có bảng bẫy, tỷ lệ mệnh đề khác bệnh nhân và các số thống kê khác.
def _bao_cao(t: dict) -> str:
    bay = "\n".join(f"| `{k}` | {v} | {v / t['so_ca']:.1%} |"
                    for k, v in t["bay"].items())
    ty_le_khac = t["menh_de_khong_phai_benh_nhan"] / t["so_menh_de"]
    return f"""# Bộ hội thoại khám bệnh Việt Nam — sinh bằng luật

Sinh tự động bằng `python -m src.bo_du_lieu.sinh_hoi_thoai_viet --so-ca {t['so_ca']}`.
Đừng sửa tay: sửa tay rồi chạy lại là mất.

## Vì sao tự dựng bộ này

Bộ của cuộc thi có dấu vết rõ là **bản dịch từ một bộ hội thoại y khoa tiếng
Anh (Mỹ)** — xem `docs/ket-qua/dau-vet-nguon.md`. Hậu quả nằm đúng chỗ dự án
quan tâm: hai hiện tượng làm việc quy gán khó nhất trong tiếng Việt đều bị
**dưới đại diện** trong một bản dịch, vì tiếng Anh gần như luôn có chủ ngữ.

1. **Lược chủ ngữ.** *"Sốt hai hôm rồi"*, *"Nôn từ tối qua"* — người đọc phải
   suy chủ thể từ ngữ cảnh.
2. **Từ chỉ quan hệ họ hàng làm đại từ.** *cháu*, *em*, *con* vừa là cách người
   nói tự xưng, vừa là cách gọi người thứ ba.

Bộ này sinh ra đúng hai hiện tượng đó, ở mật độ thật.

## Sinh bằng LUẬT, không bằng mô hình ngôn ngữ

Đây là ràng buộc số 1 của dự án, và lý do không phải hình thức: mô hình ngôn ngữ
viết hội thoại **sạch hơn người nói thật** — nó gần như luôn ghi rõ chủ ngữ ở
mỗi lượt. Nên đúng những ca khó nhất sẽ hiếm đi, và đường tắt *"chủ thể chính là
người vừa nói"* sẽ trúng nhiều hơn bình thường. Sai lệch đó **một chiều**: luôn
về phía làm vấn đề trông nhẹ hơn thật.

## Quy mô

| | |
|---|---|
| Số ca | **{t['so_ca']}** (hội thoại không trùng nhau: {t['hoi_thoai_duy_nhat']}) |
| Khuôn bệnh | {t['so_khuon_benh']} |
| Tổng lượt thoại | {t['tong_luot']} · trung bình {t['luot_moi_ca']} lượt/ca |
| Tổng từ | {t['tong_tu']:,} |
| Mệnh đề trong đáp án | {t['so_menh_de']} |
| **Mệnh đề KHÔNG thuộc bệnh nhân** | **{t['menh_de_khong_phai_benh_nhan']}** ({ty_le_khac:.1%}) |
| Ca nhi | {t['ca_nhi']} |
| Có người nhà kể hộ | {t['co_nguoi_nha_ke']} |

## Thứ bộ của cuộc thi không có: đáp án có cấu trúc

Mỗi ca kèm trường `dap_an` — danh sách mệnh đề, mỗi mệnh đề ghi **chủ thể thật**,
mốc thời gian thật, tình huống thật, và số lượt thoại làm bằng chứng.

Nhờ đó đo được độ chính xác quy gán **chính xác tuyệt đối**, thay vì ước lượng
qua một bản tham chiếu dạng văn xuôi. Đó cũng là chỗ gỡ được hạn chế nặng nhất
của `thuoc_do_quy_gan` — nó nhạy với cách đóng gói câu khi phải đối chiếu văn
xuôi với văn xuôi.

## Bẫy quy gán

| Bẫy | Số ca | Tỷ lệ |
|---|---|---|
{bay}

Ý nghĩa từng bẫy:

- `nguoi_nha_ke_ho` — người nhà kể thay bệnh nhân. Người nói ≠ chủ thể.
- `tien_su_gia_dinh` — người nhà kể bệnh **của chính họ** xen vào giữa. Đây là
  bẫy quan trọng nhất: người nói và chủ thể là một, nhưng chủ thể **không phải**
  bệnh nhân.
- `di_ung_nguoi_nha` — dị ứng thuộc về người nhà, bệnh nhân thì *chưa ghi nhận*.
- `luoc_chu_ngu` — câu không có chủ ngữ.
- `dai_tu_ho_hang` — *cháu*/*con* vừa là người nói vừa là người được nói tới.
- `dinh_chinh` — người nói tự sửa lại con số vừa nêu. Đáp án giữ **bản đã sửa**.
- `dien_bien` — hai mốc thời gian, **cả hai đều đúng**, đáp án giữ cả hai.
- `gia_dinh` — câu điều kiện *"nếu mai còn…"*, **không** được thành triệu chứng.
- `hoi_khong_dap` — bác sĩ hỏi, không ai trả lời. Bệnh án **không** được nhắc tới.

## Bốn cái bẫy khi sinh dữ liệu có đáp án — đều đã chặn và có test

1. **Thay thế làm bài toán không giải được** → chỉ **chèn thêm**, giữ nguyên lượt gốc.
2. **Hai khẳng định khác nhau không phải mâu thuẫn** → `dien_bien` giữ cả hai.
3. **Độ dài lộ đáp án** → số lượt không phụ thuộc vào việc ca đó có bẫy hay không.
4. **Vị trí lộ đáp án** → vị trí bẫy rải đều, không dính ở cuối.

Thêm một nhóm test về **ngôn ngữ**, vì một bộ dữ liệu tiếng Việt sai vai giao
tiếp thì mô hình sẽ học đúng cái sai đó: bệnh nhân không dùng *"Ừ"* với bác sĩ ·
tiểu từ đề nghị (*nhé, nghen*) không gắn vào câu hỏi · không trộn giọng hai miền
trong một cuộc · bệnh phải hợp lứa tuổi · mốc thời gian phải hợp diễn tiến bệnh.

## Giới hạn, nói thẳng

1. **Đây là dữ liệu mô phỏng, không phải hội thoại người thật.** Mọi kết luận rút
   ra từ nó phải nói rõ điều đó. Nó dùng để đo **cơ chế** — quy gán đúng hay sai
   khi có bẫy — chứ không đo tần suất lỗi ngoài đời.
2. **{t['so_ca']} ca sinh từ {t['so_khuon_benh']} khuôn bệnh.** Đơn vị độc lập là
   số khuôn, không phải số dòng. Đừng viết *"{t['so_ca']} ca đủ để kết luận"*.
3. **Lời thoại do luật ghép**, nên đều đặn hơn lời nói thật: không có ngập ngừng,
   không nói chen, không câu bỏ dở. Bộ này **không** thay được dữ liệu thật.
4. Chưa có bác sĩ duyệt. Trước khi dùng cho phần kết luận, cần bác đọc một mẫu
   ngẫu nhiên và xác nhận các ca là hợp lý về lâm sàng.
"""


if __name__ == "__main__":
    main()
