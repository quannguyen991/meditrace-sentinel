# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 0 – Chuẩn hoá đầu vào]
Làm gì   : Hiểu từ địa phương và khẩu ngữ trong lời bệnh nhân nhưng vẫn giữ nguyên văn, để
           còn trích dẫn và đối chiếu.
Vào → Ra : lời thoại nguyên văn → danh sách chỗ phương ngữ (mức chắc / cần hỏi), bản đã
           chuẩn hoá, chỗ cần hỏi lại
Đọc từ   : phan_tich() tìm cụm phương ngữ; chuan_hoa() đổi sang nghĩa chuẩn; can_hoi() lấy
           chỗ mơ hồ
Mục lục (các hàm/lớp chính):
  phan_tich()   Tìm các cụm phương ngữ trên nguyên văn
  chuan_hoa()   Thay từ phương ngữ bằng nghĩa chuẩn
  can_hoi()     Liệt kê chỗ mơ hồ cần hỏi lại
  class ChoDoi  Một chỗ phương ngữ cần đổi hoặc gắn cờ
Gọi tới  : bo_du_lieu/dan_gian
Dùng bởi : canh_bao/phat_hien, do_luong/cham_he_thong, do_luong/do_vidia2std,
           do_luong/doi_chung_context_vi, bo_du_lieu/nap_bo_gpt500,
           duong_ong/b1_ep_dau_ra_json, duong_ong/b2_bu_chu_ngu_tinh_luoc,
           duong_ong/b4_kiem_can_cu … (tổng 10 tệp)
Tên cũ   : chuan_hoa.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Tầng 1 — HIỂU phương ngữ nhưng GIỮ NGUYÊN VĂN.

Mỗi đoạn hội thoại có HAI bản: nguyên văn (để trích dẫn, để bác sĩ đọc) và bản
chuẩn hoá (để đối chiếu nội dung). Mỗi chỗ đổi mang MỨC TIN:

  chắc     trong ngữ cảnh khám bệnh từ chỉ có MỘT nghĩa: "hôm rày", "xỉu", "ói"
  cần hỏi  từ có nghĩa thứ hai thường gặp, hoặc mục từ điển đáng ngờ. Bản chuẩn
           hoá VẪN ghi nghĩa hay gặp nhất để đối chiếu, nhưng gắn cờ — tầng khoá
           bằng chứng hạ nó xuống cảnh báo, tầng hỏi lại (`hoi_lai`) hỏi lại.

KHÔNG thay cả câu dân dã thành thuật ngữ y khoa. "Nóng hâm hấp" thành "nóng
nhiều có thể sốt", mức CẦN HỎI — chứ không thành "sốt": người nói chưa đo nhiệt.

BỐN TỪ NGUY HIỂM NHẤT, và vì sao không đổi chúng khi đứng một mình:

  "tê"    = kia (miền Trung), NHƯNG "tê chân", "tê bì" là triệu chứng. Chỉ đổi
            trong "hôm tê", "bên tê", "chỗ tê".
  "chi"   = gì, NHƯNG "chi dưới" là chi của cơ thể. Chỉ đổi trong "có chi",
            "làm chi", "bị chi", "cái chi".
  "răng"  = sao, NHƯNG "mọc răng", "đau răng" là cái răng.
  "bả"    = bà ấy (miền Nam), NHƯNG "bả vai" là một bộ phận cơ thể.

NGUỒN — phải đọc trước khi dùng. Bảng dưới đây lấy từ từ điển phương ngữ người
dùng cung cấp (40 mục), mà người dùng xác nhận ngày 11/09/2026 là do GPT SINH;
một số nguồn trích trong đó là bài blog thương mại. Mỗi mục phải được đối chiếu
với từ điển thật (Huỳnh Công Tín, "Từ điển từ ngữ Nam Bộ", 2007) hoặc người địa
phương trước khi dùng cho kết luận. Mục "mệ" đặc biệt: từ điển ghi "bà/mẹ", ở
Huế "mệ" thường là BÀ — nhầm hai người này là đúng lỗi quy gán của dự án, nên
để CẦN HỎI.

VÒNG TRÒN PHẢI NÓI RÕ. Bảng thay của bộ sinh (`phuong_ngu.THAY_DUOC`) lấy từ
cùng nguồn, nên trên dữ liệu tự sinh tầng này biết trước MỌI từ phương ngữ. Phép
thử cặp phương ngữ (`thach_thuc`) vì thế đo "hệ thống có áp dụng đúng bảng của
nó", không đo "hệ thống chịu được phương ngữ lạ". Phần đo được thật là MÔ HÌNH:
từ 11/09/2026 khuôn train không có từ nào từ bảng GPT
(`sinh_hoi_thoai_viet.PHUONG_NGU_TRONG_TRAIN`), nên mô hình gặp chúng lần đầu ở
tập đánh giá.
"""
import re
from dataclasses import dataclass
from typing import List, Optional

from src.bo_du_lieu import dan_gian as dan_gian

CHAC = "chắc"
CAN_HOI = "cần hỏi"


# ═══ class ChoDoi — Một chỗ phương ngữ cần đổi hoặc gắn cờ ════════════════════════════
# Lưu vị trí, chữ gốc, nghĩa chuẩn, mức tin (chắc hoặc cần hỏi) và lý do.
@dataclass(frozen=True)
class ChoDoi:
    bat_dau: int
    ket_thuc: int
    goc: str                  # chữ nguyên văn
    nghia: str                # "" = không đổi
    muc_tin: Optional[str]    # CHAC | CAN_HOI | None (giữ chỗ, không đổi, không báo)
    ly_do: str = ""


# ─── _tu() — Dựng mẫu regex khớp nguyên từ ────────────────────────────────────────────
def _tu(cum):
    return rf"(?<!\w){cum}(?!\w)"


# (biểu thức trên chữ THƯỜNG, nhóm được đổi, nghĩa, mức tin, lý do).
# Xét theo THỨ TỰ; chỗ đã bị một mục trước chiếm thì mục sau bỏ qua — nên cụm
# DÀI và các mục "giữ chỗ" đứng trước từ đơn.
BANG = [
    # --- giữ chỗ: nghĩa có thể, KHÔNG phải phương ngữ
    (_tu("bả vai"), 0, "", None, ""),
    (_tu("chi (dưới|trên|phí|tiết|trả|tiêu|nhánh)"), 0, "", None, ""),
    (_tu("(mô|giải phẫu) (mềm|học|bệnh|xơ|sẹo|cơ|mỡ|hình|tả|phỏng|liên kết)"), 0, "", None, ""),
    (_tu("mô (mềm|học|bệnh học|xơ|sẹo|cơ|mỡ|hình|tả|phỏng|liên kết|tế bào)"), 0, "", None, ""),
    (_tu("(nuôi )?cấy (máu|đờm|đàm|phân|nước tiểu|dịch|vi khuẩn|nấm)"), 0, "", None, ""),
    (_tu("vô (căn|khuẩn|sinh|niệu|cảm|trùng|ý|tình|tư|hình|cùng|địch|tội|thường)"), 0, "", None, ""),
    (_tu("(mùa|nghỉ|trưa|nắng|nóng|ngày|tháng|năm) hè"), 0, "", None, ""),
    (_tu("trằn trọc"), 0, "", None, ""),
    (r"(?<!\w)(?:đầu|móng) giò(?!\w)", 0, "", None, ""),
    (r"(?<!\w)(?:hung|độc) ác(?!\w)", 0, "", None, ""),
    (r"(?<!\w)(mọc|đau|sâu|nhổ|cái|chiếc|hàm|chải|đánh|niềng) răng(?!\w)", 0,
     "", None, ""),
    (r"(?<!\w)răng (sữa|hàm|khôn|miệng|cửa)(?!\w)", 0, "", None, ""),
    (r"(?<!\w)(chụp|tấm|bức|hình) ảnh(?!\w)", 0, "", None, ""),
    (_tu("bẹ (cải|chuối|ngô|bắp|dừa)"), 0, "", None, ""),
    # --- cụm nhiều từ, một nghĩa
    (_tu("cái bụng dưới nó cứ trằn xuống"), 0, "vùng bụng dưới cứ nặng tức", CHAC, ""),
    (_tu("bọng đái bị trằn"), 0, "bàng quang bị nặng tức", CHAC, ""),
    (_tu("sáng dậy sưng hai cái giò"), 0, "sáng dậy sưng hai chân", CHAC, ""),
    (_tu("trặc giò"), 0, "trật chân", CHAC, ""),
    (_tu("uống rượu vô đau thắt"), 0, "uống rượu vào đau thắt", CHAC, ""),
    (r"(?<!\w)(?:uống rượu vào đau thắt|uống rượu vô đau thắt)\s+(mỏ ác)(?!\w)", 1, "vùng thượng vị", CHAC, ""),
    (r"(?<!\w)(?:cháu|bé|trẻ|tháng).*?\b(mỏ ác)\b", 1, "thóp trước", CHAC, ""),
    (_tu("trong mình cứ rười rượi mấy bữa rày"), 0, "trong người cứ uể oải mấy ngày nay", CHAC, ""),
    (_tu("sau cơn sốt người rười rượi"), 0, "sau cơn sốt người kiệt sức", CHAC, ""),
    (r"(?<!\w)(?:tiểu|đái|thấy)\s+(thốn)(?=\s+dữ dội(?!\w))", 1, "buốt", CHAC, ""),
    (_tu("thốn gót"), 0, "đau nhói gót", CHAC, ""),
    (_tu("cái bẹ"), 0, "bả vai", CHAC, ""),
    (_tu("có chi mô"), 0, "không có gì", CHAC, ""),
    (_tu("mần răng"), 0, "làm sao", CHAC, ""),
    (_tu("làm răng"), 0, "làm sao", CHAC, ""),
    (_tu("hổm rày"), 0, "dạo gần đây", CHAC, ""),
    (_tu("bữa hổm"), 0, "hôm trước", CHAC, ""),
    (_tu("bữa giờ"), 0, "dạo này", CHAC, ""),
    (_tu("bữa chừ"), 0, "dạo này", CHAC, ""),
    (_tu("hôm tê"), 0, "hôm kia", CHAC, ""),
    (_tu("khi mô"), 0, "khi nào", CHAC, ""),
    (_tu("con nít"), 0, "trẻ em", CHAC, ""),
    (_tu("đi cầu"), 0, "đi đại tiện", CHAC, ""),
    (_tu("lừ đừ"), 0, "mệt mỏi", CHAC, ""),
    (_tu("dữ lắm"), 0, "rất nhiều", CHAC, ""),
    (_tu("mỏ ác"), 0, "mũi ức", CAN_HOI, "người lớn: thượng vị, trẻ em: thóp trước"),
    (_tu("chấn thủy"), 0, "vùng thượng vị", CHAC, ""),
    (_tu("màng tang"), 0, "thái dương", CHAC, ""),
    (_tu("lóng tay"), 0, "khớp liên đốt ngón tay", CHAC, ""),
    (_tu("cù chỏ"), 0, "khớp khuỷu tay", CHAC, ""),
    (_tu("ống điếu"), 0, "xương cẳng chân", CHAC, ""),
    (_tu("trái khế"), 0, "yết hầu", CHAC, ""),
    (_tu("trái cấm"), 0, "yết hầu", CHAC, ""),
    (_tu("rần rần"), 0, "dị cảm thần kinh", CHAC, ""),
    (_tu("nê bụng"), 0, "chướng bụng", CHAC, ""),
    (_tu("dằm xóc"), 0, "đau rát bỏng", CHAC, ""),
    (_tu("bữa ni"), 0, "hôm nay", CHAC, ""),
    (_tu("bữa nớ"), 0, "hôm đó", CHAC, ""),
    (_tu("bữa qua"), 0, "hôm qua", CHAC, ""),
    (_tu("khi nớ"), 0, "khi đó", CHAC, ""),
    (_tu("khi dừ"), 0, "lúc nãy", CHAC, ""),
    (_tu("từ dừ"), 0, "từ giờ", CHAC, ""),
    # --- mở rộng phương ngữ 3 miền & khẩu ngữ y tế (27/11/2026) ---
    (_tu("nhức trốc"), 0, "đau đầu", CHAC, ""),
    (_tu("đau trốc"), 0, "đau đầu", CHAC, ""),
    (_tu("hầm hầm"), 0, "nóng nhiều có thể sốt", CAN_HOI,
     "người nói chưa đo nhiệt độ — không tự đổi thành sốt"),
    (_tu("nóng hầm hập"), 0, "nóng nhiều có thể sốt", CAN_HOI,
     "người nói chưa đo nhiệt độ — không tự đổi thành sốt"),
    (_tu("đi tháo"), 0, "tiêu chảy", CHAC, ""),
    (_tu("tào tháo rượt"), 0, "tiêu chảy nhiều lần", CHAC, ""),
    (_tu("phù giò"), 0, "phù chân", CHAC, ""),
    (_tu("xốn mắt"), 0, "cộm ngứa mắt", CHAC, ""),
    (_tu("đau ngang hông"), 0, "đau vùng lưng dưới", CHAC, ""),
    (_tu("ói mửa"), 0, "nôn", CHAC, ""),
    (_tu("mau lẹ"), 0, "nhanh", CHAC, ""),
    (_tu("mệ ngoại"), 0, "bà ngoại", CHAC, ""),
    (_tu("mệ nội"), 0, "bà nội", CHAC, ""),
    (_tu("nhức mình nhức mẩy"), 0, "đau mỏi toàn thân", CHAC, ""),
    (_tu("sổ mũi ròng ròng"), 0, "chảy nước mũi nhiều", CHAC, ""),
    (_tu("nổi sảy"), 0, "phát ban rôm sảy", CHAC, ""),
    (_tu("uống a móc"), 0, "uống amoxicillin (cần xác nhận)", CAN_HOI,
     "khẩu ngữ 'a móc' cần bác sĩ xác nhận đúng hoạt chất"),
    (_tu("uống ô mê"), 0, "uống omeprazol (cần xác nhận)", CAN_HOI,
     "khẩu ngữ 'ô mê' cần bác sĩ xác nhận đúng hoạt chất"),
    (_tu("uống pa ra"), 0, "uống paracetamol (cần xác nhận)", CAN_HOI,
     "khẩu ngữ 'pa ra' cần bác sĩ xác nhận đúng hoạt chất"),
    (_tu("tới công chuyện"), 0, "trở nặng", CAN_HOI,
     "khẩu ngữ, phải hỏi triệu chứng cụ thể"),
    (_tu("quay quay"), 0, "chóng mặt", CAN_HOI, "mục từ điển đáng ngờ"),
    # --- từ đơn CHỈ đổi trong ngữ cảnh chặn
    (r"(?<!\w)(?:bên|chỗ|cái|đằng) (tê)(?!\w)", 1, "kia", CHAC, ""),
    (r"(?<!\w)(?:có|làm|bị|cái) (chi)(?!\w)", 1, "gì", CHAC, ""),
    (r"(?<!\w)(?:cái|bữa|hôm|chỗ|bên|ngày) (ni)(?!\w)", 1, "này", CHAC, ""),
    (r"(?<!\w)(?:đi|ở|chỗ|bên|đằng) (mô)(?!\w)", 1, "đâu", CHAC, ""),
    (r"(?<!\w)(?:làm|mần|vì|tại) (răng)(?!\w)", 1, "sao", CHAC, ""),
    (r"(?<!\w)(răng)(?= (?:rứa|vậy|không|mà|hỉ)(?!\w))", 1, "sao", CHAC, ""),
    # "hong": hết câu / đứng trước tiểu từ -> không. Sau từ chỉ bộ phận cơ thể
    # thì MƠ HỒ ("đau hong" = đau vùng họng hay "đau không?") — từ điển ghi đúng
    # trường hợp này là cái bẫy khi bản ghi thiếu dấu câu.
    (r"(?<!\w)(hông)(?=\s*(?:[,.?!…]|$|có\b|biết\b|đó\b|nè\b|à\b|ha\b))", 1,
     "không", CHAC, ""),
    # MƠ HỒ THẬT: không ghi nghĩa nào vào bản chuẩn hoá — ghi "không" thì "đau
    # hong bên phải" thành "đau không bên phải", tức chọn hộ người nói một nghĩa.
    (r"(?<!\w)(?:đau|mỏi|nhức|bên|vùng|sưng|tê) (hông)(?!\w)", 1, "",
     CAN_HOI, "'hông' là vùng hông hay 'không'?"),
    (_tu("hông"), 0, "không", CHAC, ""),
    (_tu("mệ"), 0, "bà", CAN_HOI,
     "từ điển ghi 'bà/mẹ'; ở Huế 'mệ' thường là bà — cần người Huế xác nhận"),
    (_tu("ảnh"), 0, "anh ấy", CAN_HOI, "'ảnh' là anh ấy hay tấm ảnh?"),
    # --- từ đơn, một nghĩa
    (_tu("xỉu"), 0, "ngất", CHAC, ""),
    (_tu("ói"), 0, "nôn", CHAC, ""),
    (_tu("mửa"), 0, "nôn", CHAC, ""),
    (_tu("chừ"), 0, "bây giờ", CHAC, ""),
    (_tu("rứa"), 0, "vậy", CHAC, ""),
    (_tu("hổng"), 0, "không", CHAC, ""),
    (_tu("nỏ"), 0, "không", CHAC, ""),
    (_tu("chớ"), 0, "chứ", CHAC, ""),
    (_tu("ổng"), 0, "ông ấy", CHAC, ""),
    (_tu("bả"), 0, "bà ấy", CHAC, ""),
    (_tu("eng"), 0, "anh", CHAC, ""),
    (_tu("hỉ"), 0, "nhỉ", CHAC, ""),
    (_tu("nớ"), 0, "đó", CHAC, ""),
    (_tu("mần"), 0, "làm", CHAC, ""),
    (_tu("bẹ"), 0, "bả vai", CHAC, ""),
    (_tu("giò"), 0, "chân", CHAC, ""),
    (_tu("xốn"), 0, "cảm giác dị vật", CHAC, ""),
    (_tu("tui"), 0, "tôi", CHAC, ""),
    # --- mở rộng phương ngữ 3 miền xác thực từ tập train ViDia2Std (27/11/2026) ---
    (_tu("chơ"), 0, "chứ", CHAC, ""),
    (_tu("nựa"), 0, "nữa", CHAC, ""),
    (_tu("chộ"), 0, "thấy", CHAC, ""),
    (_tu("dìa"), 0, "về", CHAC, ""),
    (_tu("dừ"), 0, "giờ", CHAC, ""),
    (_tu("cụng"), 0, "cũng", CHAC, ""),
    (_tu("cấy"), 0, "cái", CHAC, ""),
    (_tu("thiệt"), 0, "thật", CHAC, ""),
    (_tu("mi"), 0, "mày", CHAC, ""),
    (_tu("tau"), 0, "tao", CHAC, ""),
    (_tu("hắn"), 0, "nó", CHAC, ""),
    (_tu("hấn"), 0, "nó", CHAC, ""),
    (_tu("tề"), 0, "kìa", CHAC, ""),
    (_tu("choa"), 0, "tôi", CHAC, ""),
    (_tu("miềng"), 0, "mình", CHAC, ""),
    (_tu("nì"), 0, "này", CHAC, ""),
    (_tu("nác"), 0, "nước", CHAC, ""),
    (_tu("vô"), 0, "vào", CHAC, ""),
    (_tu("hầy"), 0, "nhỉ", CHAC, ""),
    (_tu("hè"), 0, "nhỉ", CHAC, ""),
    (_tu("nè"), 0, "này", CHAC, ""),
    (_tu("ri"), 0, "thế", CHAC, ""),
    (_tu("gấy"), 0, "gái", CHAC, ""),
    (_tu("giời"), 0, "trời", CHAC, ""),
    (_tu("quẹo"), 0, "rẽ", CHAC, ""),
    (_tu("mạ"), 0, "mẹ", CHAC, ""),
    (_tu("nhể"), 0, "nhỉ", CHAC, ""),
    (_tu("nhở"), 0, "nhỉ", CHAC, ""),
    (_tu("ni"), 0, "này", CHAC, ""),
    (_tu("chi"), 0, "gì", CHAC, ""),
    (r"(?<!\w)(?:gì|cái|người|ai|việc|điều|khi|lúc|ngày|bữa|nơi|chỗ) (mô)(?!\w)", 1, "nào", CHAC, ""),
    (_tu("mô"), 0, "đâu", CHAC, ""),
]
_BANG = [(re.compile(bt), nhom, nghia, muc, ly) for bt, nhom, nghia, muc, ly in BANG]

# Cách nói dân gian lấy từ từ điển thật (24/09/2026, xem `dan_gian`). Nửa `trong_bang`
# đường ống biết; nửa GIỮ LẠI chỉ bộ chấm biết (`gom_giu_lai=True`) — để đo khả năng
# chịu cách nói chưa gặp. Loại MƠ HỒ không bao giờ vào đây. Đặt SAU bảng cũ: các cụm
# này không xuất hiện trong dữ liệu thế hệ 8 (có kiểm thử), nên không đổi số cũ nào.
_DAN_GIAN_TRONG = [(re.compile(_tu(re.escape(dg))), 0, chuan, CHAC, "dan gian")
                   for dg, chuan in dan_gian.muc_chuan_hoa(False)]
_DAN_GIAN_GIU_LAI = [(re.compile(_tu(re.escape(dg))), 0, chuan, CHAC, "dan gian, giu lai")
                     for dg, chuan in dan_gian.muc_chuan_hoa(True)
                     if (dg, chuan) not in dan_gian.muc_chuan_hoa(False)]


# ═══ phan_tich() — Tìm các cụm phương ngữ trên nguyên văn ═════════════════════════════
# Trả về các chỗ đổi xếp theo vị trí, không chồng nhau; bảng đơn giản giữ lại chỉ dùng
# khi chấm điểm.
def phan_tich(van: str, gom_giu_lai: bool = False) -> List[ChoDoi]:
    """-> các chỗ đổi / gắn cờ trên NGUYÊN VĂN, xếp theo vị trí. Không chồng nhau.

    `gom_giu_lai=True` CHỈ cho bộ chấm — đường ống (khoá bằng chứng, cảnh báo, hỏi
    lại) luôn gọi mặc định, nên không biết các cụm dân gian giữ lại."""
    van = van or ""
    thap = van.lower()
    if len(thap) != len(van):          # an toàn: chuỗi lạ không đổi được độ dài
        return []
    da = [False] * len(van)
    ra = []
    bang = _BANG + _DAN_GIAN_TRONG + (_DAN_GIAN_GIU_LAI if gom_giu_lai else [])
    for mau, nhom, nghia, muc, ly in bang:
        for m in mau.finditer(thap):
            a, b = m.span(nhom)
            if a < 0 or any(da[a:b]):
                continue
            for k in range(a, b):
                da[k] = True
            ra.append(ChoDoi(a, b, van[a:b], nghia, muc, ly))
    return sorted(ra, key=lambda c: c.bat_dau)


# ═══ chuan_hoa() — Thay từ phương ngữ bằng nghĩa chuẩn ════════════════════════════════
# Trả về bản chữ thường; có thể bỏ qua các chỗ mơ hồ để chỉ thay chỗ chắc chắn.
def chuan_hoa(van: str, gom_can_hoi: bool = True, gom_giu_lai: bool = False) -> str:
    """-> bản CHỮ THƯỜNG đã thay từ phương ngữ bằng nghĩa chuẩn.

    `gom_can_hoi=False`: chỉ thay các chỗ CHẮC — để biết một phép đối chiếu có
    dùng được không khi bỏ hết chỗ mơ hồ.
    """
    thap = (van or "").lower()
    for c in sorted(phan_tich(van, gom_giu_lai), key=lambda c: c.bat_dau, reverse=True):
        if not c.nghia or c.muc_tin is None:
            continue
        if c.muc_tin == CAN_HOI and not gom_can_hoi:
            continue
        thap = thap[:c.bat_dau] + c.nghia + thap[c.ket_thuc:]
    return thap


# ═══ can_hoi() — Liệt kê chỗ mơ hồ cần hỏi lại ════════════════════════════════════════
# Ứng viên cho tầng hỏi lại (b6).
def can_hoi(van: str) -> List[ChoDoi]:
    """Các chỗ MƠ HỒ trong đoạn — ứng viên cho tầng hỏi lại."""
    return [c for c in phan_tich(van) if c.muc_tin == CAN_HOI]

if __name__ == "__main__":
    CAU_VI_DU = [
        "Bữa ni tui đi khám.",
        "Bữa nớ tui bị ói.",
        "Khi nớ tui đang ở nhà.",
        "Tui bị tê chân.",
        "Mệ bị đau đầu.",
    ]

    for cau in CAU_VI_DU:
        print("Nguyên văn:", cau)
        print("Chuẩn hóa:", chuan_hoa(cau))

        for muc in can_hoi(cau):
            print("Cần hỏi:", muc.goc, "-", muc.ly_do)

        print()