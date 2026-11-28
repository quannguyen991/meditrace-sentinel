# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 4 – Kiểm căn cứ]
Làm gì   : Kiểm mỗi mệnh đề có thật sự được nói trong lời thoại không — đúng câu, đúng
           người, đúng mức — trước khi cho vào bản nháp.
Vào → Ra : danh sách mệnh đề + lời thoại → mỗi mệnh đề đạt / cảnh báo / chặn kèm mã lý do
Đọc từ   : khoa_ca() chạy cho cả ca; khoa_mot() là 7 phép kiểm K1–K7 cho một mệnh đề
Bảy phép kiểm (🔴 chặn = chuyển sang CẦN XÁC NHẬN, không xoá · 🟡 cảnh báo = vẫn vào thân):
  K1 Nguồn       Câu trích có NGUYÊN VĂN trong lượt được dẫn không.
                 🔴 không có câu trích / lượt không tồn tại / câu trích không có trong hội
                 thoại · 🟡 câu trích nằm ở lượt khác lượt được dẫn.
  K2 Nội dung    Nội dung mệnh đề có trùng từ với câu trích không (chỉ so từ, không hiểu ý).
                 🟡 không trùng từ nào / chỉ khớp qua một từ phương ngữ mơ hồ.
  K3 Người       Câu trích nói về ĐÚNG NGƯỜI không ("tôi" của người mẹ ≠ bệnh nhi).
                 🔴 ghi cho bệnh nhân mà câu gốc là người kể tự nói về mình; ghi cho người
                 nhà mà câu gốc nói về bệnh nhân · 🟡 có nhắc người nhà / chủ thể chỉ suy từ
                 người nói / chưa rõ chủ thể.
  K4 Mức         Không biến nghi ngờ, "nếu…", "chưa ghi nhận" thành điều chắc chắn đã xảy ra.
                 🔴 câu gốc chỉ nghi / là câu điều kiện hay dự phòng / là chưa ghi nhận / đã
                 bị đính chính ngầm hoặc xét nghiệm loại trừ · 🟡 đoạn dẫn có từ phủ định.
  K5 Thời gian   Mốc thời gian của mệnh đề có xuất hiện trong lượt dẫn không.
                 🟡 không thấy mốc thời gian.
  K6 Thuốc       Chi tiết thuốc có trong lời nói không. 🔴 liều không có trong lượt dẫn ·
                 🟡 số lần dùng, lúc bắt đầu/ngừng, đường dùng không thấy.
  K7 Thay thế    Thông tin đã bị đính chính hoặc diễn biến mới thay thế chưa (trạng thái từ
                 bước b3). 🔴 bị thay thế · 🟡 đang mâu thuẫn, chưa giải quyết.
  Giới hạn: K1 là so chuỗi nên chắc chắn; K2–K6 là luật theo từ nên chỉ bắt được một phần —
  câu trích có thật nhưng bị diễn giải sai có thể chỉ bị cảnh báo. Tên lý do: bảng LY_DO.
Mục lục (các hàm/lớp chính):
  khoa_ca()               Khoá căn cứ cho cả danh sách mệnh đề
  khoa_mot()              Khoá căn cứ một mệnh đề qua các phép kiểm K1 đến K7
  class KetQua            Kết quả kiểm căn cứ của một mệnh đề
  doan_chua_ghi()         Tìm đoạn hội thoại có nội dung mà không mệnh đề nào dẫn
  cap_hoi_dap_chua_ghi()  Tìm cặp hỏi–đáp ngắn chưa có mệnh đề
  ly_do_chan()            Gom lý do chặn thành chuỗi theo mã mệnh đề
  tim_trich()             Tìm câu trích trong lượt nói
  kiem_chu_the()          Kiểm chủ thể của mệnh đề khớp với người trong đoạn
Gọi tới  : cong_cu_lam_sang/tri_thuc_thuoc, do_luong/thuoc_do_quy_gan,
           duong_ong/b0_cat_doan_van, duong_ong/b0_chuan_hoa_phuong_ngu,
           duong_ong/b1_cau_truc_menh_de, duong_ong/b2_gom_nguoi_thuc_the
Dùng bởi : canh_bao/bo_sot, canh_bao/gop, canh_bao/phat_hien, canh_bao/toan_ca,
           cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot, do_luong/danh_gia_khoa,
           do_luong/do_dan_gian, do_luong/kiem_nghiem_ngoai_khuon … (tổng 14 tệp)
Tên cũ   : khoa_bang_chung.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Tầng 4 — KHOÁ BẰNG CHỨNG: mỗi phát biểu phải chứng minh được bằng CHÍNH hội
thoại trước khi được vào thân hồ sơ.

VÌ SAO CẦN — và vì sao `sua_cuc_bo` không đủ. Bốn phép kiểm của `sua_cuc_bo`
đối chiếu câu bản nháp với BẢNG PHÁT BIỂU do chính mô hình trích ra. Mô hình
bịa một phát biểu thì bảng có phát biểu đó, và phép kiểm nói "có nguồn". Tầng
này quay lại HỘI THOẠI: trích dẫn phải là chuỗi nguyên văn của lượt, và chính
đoạn đó phải nói đúng người, đúng mức khẳng định.

BA CÂU HỎI:

  1. có đoạn hội thoại nào THỰC SỰ nói điều này không   K1 nguồn, K2 nội dung
  2. đoạn đó nói về ĐÚNG NGƯỜI không                     K3 chủ thể
  3. đoạn đó ủng hộ ĐÚNG MỨC khẳng định không            K4 mức, K5 thời gian, K6 thuốc
  4. thông tin có bị THAY THẾ bởi diễn biến mới không    K7 thay thế/superseded

HAI MỨC ĐỘ, và vì sao phải tách:

  chặn      có bằng chứng PHỦ ĐỊNH rõ ràng: trích dẫn không có trong hội thoại,
            đoạn dẫn nói về người KHÁC bằng một từ không mơ hồ ("tôi"), câu gốc
            chỉ nghi mà bản ghi chắc, câu điều kiện ghi thành sự thật, thông tin
            đã bị đính chính/loại trừ, hoặc đã bị thay thế (K7 superseded).
            Phát biểu KHÔNG vào thân hồ sơ — xuống CẦN XÁC NHẬN, kèm lý do.
  cảnh báo  THIẾU bằng chứng khẳng định: chủ thể chỉ suy từ người nói, nội dung
            không trùng từ nào với đoạn dẫn, mốc thời gian không thấy. Vẫn vào
            thân; `cong_rui_ro` dùng để xếp thứ tự cho bác sĩ duyệt.
"""
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Tuple

from src.duong_ong import b0_chuan_hoa_phuong_ngu as chuan_hoa
from src.duong_ong import b2_gom_nguoi_thuc_the as thuc_the
from src.duong_ong.b0_cat_doan_van import cac_doan, dau_ket
from src.duong_ong.b1_cau_truc_menh_de import la_vai_nhan_vien
from src.do_luong.thuoc_do_quy_gan import _tu_noi_dung

CHAN = "chặn"
CANH_BAO = "cảnh báo"

LY_DO = {
    "khong_trich_dan": "không có trích dẫn nguyên văn",
    "luot_khong_ton_tai": "lượt được dẫn không tồn tại",
    "trich_khong_co": "trích dẫn không có trong hội thoại",
    "trich_lech_luot": "trích dẫn nằm ở lượt khác lượt được dẫn",
    "noi_dung_khong_khop": "nội dung không trùng từ nào với đoạn dẫn",
    "phuong_ngu_can_hoi": "chỉ khớp qua một từ phương ngữ mơ hồ",
    "chu_the_nguoi_ke": "đoạn dẫn nói về chính người kể, không phải bệnh nhân",
    "chu_the_benh_nhan": "đoạn dẫn nói về bệnh nhân, không phải người nhà",
    "chu_the_nguoi_khac": "đoạn dẫn nhắc người nhà — có thể không phải của bệnh nhân",
    "chu_the_suy_tu_nguoi_noi": "chủ thể chỉ suy từ người nói — đoạn dẫn không có từ chỉ người",
    "chu_the_chua_ro": "chưa rõ chủ thể",
    "dieu_kien": "câu điều kiện hoặc giả định/phòng ngừa ghi như sự thật",
    "dinh_chinh_ngam": "thông tin ban đầu tưởng đúng nhưng đã bị đính chính hoặc xét nghiệm loại trừ",
    "vuot_muc_nghi": "câu gốc chỉ nghi ngờ, bản ghi khẳng định",
    "vuot_muc_chua_ghi_nhan": "câu gốc là chưa ghi nhận, bản ghi khẳng định",
    "phu_dinh_vuot_muc": "câu gốc là chưa ghi nhận, bản ghi phủ định chắc chắn",
    "co_tu_phu_dinh": "đoạn dẫn có từ phủ định",
    "moc_khong_thay": "mốc thời gian không thấy trong lượt dẫn",
    "mau_thuan": "nguồn mâu thuẫn, chưa xác nhận",
    "lieu_khong_thay": "liều thuốc không có trong lượt được dẫn",
    "chi_tiet_thuoc_khong_thay": "số lần dùng, lúc bắt đầu hoặc lúc ngừng thuốc không có trong lượt được dẫn",
    "duong_dung_khong_thay": "đường dùng thuốc không có trong lượt được dẫn",
    "bi_thay_the": "thông tin đã bị thay thế hoặc đính chính bởi diễn biến mới hơn (K7 Superseded)",
}

# ----------------------------------------------------- từ chỉ người
TU_TU_XUNG_RO = ("tôi", "tui", "mình", "tớ")
TU_MO = ("cháu", "con", "em", "anh", "chị", "chú", "cô", "ông")
TU_BENH_NHAN_RO = (
    "bé nhà em", "con nhà em", "cháu nó", "nhà em", "em bé", "bé",
    "ông ấy", "bà ấy", "anh ấy", "chị ấy", "bệnh nhân", "trẻ",
    "bé nhà tôi", "con nhà tôi", "cháu nhà em", "cháu nhà tôi",
    "cháu tôi", "con tôi", "con em", "nhà tôi", "ông nhà tôi",
    "bà nhà tôi", "cô ấy", "chú ấy", "bác ấy", "em ấy",
    "thằng nhỏ", "con bé", "bé út", "mấy nhỏ", "thằng bé"
)
TU_HO_HANG = (
    "con trai", "con gái", "anh trai", "chị gái", "em trai", "em gái",
    "ông nội", "bà nội", "ông ngoại", "bà ngoại", "mẹ", "bố", "cha",
    "chồng", "vợ", "bà"
)
_SO_HUU_GOC = TU_HO_HANG + ("ba", "má", "ông", "anh", "chị")
_SO_HUU_DUOI = ("tôi", "em", "mình", "cháu", "nó", "tui")
_VIEC_NOI = (
    "nhầm", "nhớ nhầm", "nói nhầm", "nhớ lại", "nói lại", "nhớ rồi",
    "nghĩ", "thấy là", "không chắc", "hay lo", "đi thay"
)
_MINH_TU_GHEP = (
    "trở mình", "giật mình", "rùng mình", "cựa mình", "mình mẩy",
    "nóng mình", "một mình", "khắp mình"
)
_TU_XUNG_KE = (
    [f"{a} {b}" for a in TU_TU_XUNG_RO + TU_MO for b in _VIEC_NOI]
    + [f"theo {a}" for a in TU_TU_XUNG_RO + TU_MO]
    + list(_MINH_TU_GHEP)
)

# ----------------------------------------------------- dấu hiệu mức khẳng định
DAU_NGHI = re.compile(
    r"(?<!\w)(nghi|nghĩ nhiều đến|nghĩ là|có thể|hình như|"
    r"chắc là|không chắc|chưa rõ|chưa kết luận)(?!\w)"
)
DAU_THEO_DOI = re.compile(r"^\s*theo dõi(?!\w)")
DAU_CHUA_GHI_NHAN = re.compile(
    r"(?<!\w)(chưa (thấy |từng )?bị( gì| bao giờ)?|"
    r"chưa bao giờ|chưa thấy gì|chưa từng)(?!\w)"
)

# [NÂNG CẤP 1]: Bắt câu điều kiện, giả định, phòng ngừa hướng dẫn tương lai
DAU_DIEU_KIEN = re.compile(
    r"(?<!\w)("
    r"nếu(\s+như|\s+mà)?"
    r"|lỡ(\s+như|\s+mà)?"
    r"|hễ(\s+mà)?"
    r"|giả\s+sử"
    r"|phòng\s+(khi|hờ|trường\s+hợp)"
    r"|đề\s+phòng(\s+(khi|lỡ))?"
    r"|trong\s+trường\s+hợp(\s+mà)?"
    r"|trường\s+hợp\s+(bị|sốt|đau|có|nếu|lỡ|xảy\s+ra)"
    r"|chừng\s+nào\s+.*?\s+thì(\s+mới)?"
    r"|khi\s+nào\s+.*?\s+thì(\s+mới)?"
    r"|trừ\s+khi"
    r")(?!\w)",
    re.I
)

# [NÂNG CẤP 2]: Bắt đính chính ngầm / loại trừ hồi cứu sau kiểm chứng
# Mẫu 1: Tưởng là / nghĩ là [X] ... nhưng đi khám / test / xét nghiệm ... thì âm tính / không phải
_TIEN_DE_NGHI = r"(tưởng(\s+là)?|ngỡ(\s+là)?|đoán(\s+là)?|nghĩ(\s+là)?|trước\s+nghi|ban\s+đầu\s+bảo|nghi ngờ)"
_KIEM_CHUNG = r"(nhưng|mà|về\s+sau|đi\s+khám|xét\s+nghiệm|test|kết\s+quả|bác\s+sĩ\s+bảo|nội\s+soi|chụp)"
_PHU_DINH_KET_LUAN = r"(không\s+phải|không\s+bị|bình\s+thường|âm\s+tính|nhầm|loại\s+trừ|không\s+việc\s+gì)"

DAU_DINH_CHINH_NGAM = re.compile(
    rf"(?<!\w){_TIEN_DE_NGHI}.*?{_KIEM_CHUNG}.*?{_PHU_DINH_KET_LUAN}(?!\w)",
    re.I
)

# Mẫu 2: Khám / test thì bình thường chứ không phải / không phải [X]
DAU_BAC_BO_TRUC_TIEP = re.compile(
    r"(?<!\w)(khám|test|xét\s+nghiệm|nội\s+soi|chụp).*?(bình\s+thường|âm\s+tính|không\s+việc\s+gì).*?"
    r"(chứ\s+không\s+phải|không\s+phải|chả\s+phải)(?!\w)",
    re.I
)

# "chứ không phải" là đối lập, không phải phủ định nội dung.
DAU_PHU_DINH = re.compile(r"(?<!\w)(không(?! phải)|chẳng|chả|hết|đỡ hẳn|khỏi)(?!\w)")

THU_TUC = re.compile(
    r"^(dạ|vâng|ừ|dạ vâng)( ạ)?$"
    r"|chào|cảm ơn|tạm biệt|thưa bác sĩ|^bác sĩ ạ|xin lỗi"
    r"|^(dạ |vâng |dạ vâng )?(không|chưa)( có gì| uống gì| bị gì| đâu)?"
    r"( ạ| nhé| nha| nghen| ha)?$"
    r"|^à không$|không đúng đâu|nhớ rồi|nhớ lại rồi|nói lại cho đúng"
    r"|nói thêm để bác sĩ biết|hay lo"
    r"|để tôi|tôi khám|khám cho|khám xem|xác nhận lại|kể tôi nghe|kể xem"
    r"|nằm lên bàn|mời \w+ ngồi|đi một mình|đi thay|không đến được"
    r"|mệt quá nên|đã đo sinh hiệu|vào từ sáng|mới đăng ký khám|chờ từ nãy"
    r"|chưa kết luận|phải có kết quả"
    r"|^(à |ờ )?(\w+ )?(nói |nhớ )?nhầm( rồi)?( ạ)?$"
    r"|^(\w+ )?không chắc( lắm)?( ạ)?$",
    re.I
)


# ═══ class KetQua — Kết quả kiểm căn cứ của một mệnh đề ═══════════════════════════════
# Gồm mã lý do chặn, cảnh báo và các đoạn căn cứ tìm được; qua khi không có lý do chặn.
@dataclass
class KetQua:
    id: int
    chan: List[str] = field(default_factory=list)          # mã lý do
    canh_bao: List[str] = field(default_factory=list)
    doan: List[Tuple[int, int, int]] = field(default_factory=list)

    @property
    def qua(self) -> bool:
        return not self.chan

    def ly_do(self) -> str:
        return "; ".join(LY_DO[m] for m in self.chan + self.canh_bao)

    def to_dict(self):
        d = asdict(self)
        d["qua"] = self.qua
        return d


# ─── _nfc() — Chuẩn hoá Unicode NFC cho chuỗi ─────────────────────────────────────────
# ----------------------------------------------------- tìm trích dẫn
def _nfc(s):
    return unicodedata.normalize("NFC", str(s or ""))


# ─── _chuan_ban_do() — Gộp khoảng trắng và lập bản đồ vị trí về chuỗi gốc ─────────────
# Để tìm câu trích rồi quy ngược vị trí trên văn bản nguyên.
def _chuan_ban_do(van):
    ra, bd, trong = [], [], True
    for i, c in enumerate(van):
        if c.isspace():
            if trong:
                continue
            ra.append(" ")
            bd.append(i)
            trong = True
        else:
            ra.append(c.lower())
            bd.append(i)
            trong = False
    while ra and ra[-1] == " ":
        ra.pop()
        bd.pop()
    return "".join(ra), bd


# ─── _chuan_trich() — Chuẩn hoá câu trích: chữ thường, bỏ dấu câu hai đầu ─────────────
def _chuan_trich(t):
    t = re.sub(r"\s+", " ", _nfc(t).lower()).strip()
    return t.strip(" .,;:!?…\"'“”‘’")


_SO_CHU_VIET = [
    (r"\bmột\s+(viên|gói|ống|vỉ|nhát|giọt|muỗng|thìa)\s+rưỡi\b", r"1.5 \1"),
    (r"\bhai\s+(viên|gói|ống|vỉ|nhát|giọt|muỗng|thìa)\s+rưỡi\b", r"2.5 \1"),
    (r"\b(1|2|3)\s+(viên|gói|ống|vỉ|nhát|giọt|muỗng|thìa)\s+rưỡi\b", r"\1.5 \2"),
    (r"\bnửa\s+(viên|gói|ống|vỉ|muỗng|thìa)\b", r"0.5 \1"),
    (r"\b1/2\s*(viên|gói|ống|vỉ|muỗng|thìa)\b", r"0.5 \1"),
    (r"\b0,5\b", "0.5"),
    (r"\b1,5\b", "1.5"),
    (r"\b2,5\b", "2.5"),
    (r"\bnăm\s+trăm\b", "500"),
    (r"\bhai\s+trăm\s+năm\s+mươi\b", "250"),
    (r"\bmột\s+trăm\b", "100"),
    (r"\bnăm\s+mươi\b", "50"),
    (r"\bhai\s+mươi\b", "20"),
    (r"\bmười\s+lăm\b", "15"),
    (r"\bmười\s+bốn\b", "14"),
    (r"\bmười\b", "10"),
    (r"\bmột\s+chục\b", "10"),
    (r"\bchín\b", "9"),
    (r"\btám\b", "8"),
    (r"\bbảy\b", "7"),
    (r"\bsáu\b", "6"),
    (r"\bnăm\b", "5"),
    (r"\bbốn\b", "4"),
    (r"\bba\b", "3"),
    (r"\bhai\b", "2"),
    (r"\bmột\b", "1"),
    (r"(\d+(?:\.\d+)?)\s*(mg|g|ml|mcg|iu|%)\b", r"\1 \2"),
]


# ─── _chuan_so_lieu_thuoc() — Chuẩn hoá liều thuốc để so khớp ─────────────────────────
# Đổi dấu phẩy thập phân kiểu Việt thành dấu chấm và đổi số viết bằng chữ.
def _chuan_so_lieu_thuoc(s: str) -> str:
    t = _chuan_trich(s)
    # dấu phẩy thập phân kiểu Việt ("2,5") -> dấu chấm
    t = re.sub(r"(?<=\d),(?=\d)", ".", t)
    for pat, rep in _SO_CHU_VIET:
        t = re.sub(pat, rep, t)
    return re.sub(r"\s+", " ", t).strip()


# ─── _mau_ranh_gioi() — Dựng mẫu regex khớp có ranh giới số hoặc từ ───────────────────
# Để "5" không khớp vào "25" hay "2.5".
def _mau_ranh_gioi(ct_chuan: str) -> str:
    """Mẫu regex khớp ct_chuan với ranh giới ở hai đầu.

    Đầu là số: không được đứng sau chữ số, '.' hay ',' (tránh "5" trong
    "25", "2.5"). Cuối là số: không được theo sau bởi chữ số hay phần
    thập phân (tránh "5" trong "5.5"). Đầu/cuối là chữ: ranh giới từ.
    """
    mau = re.escape(ct_chuan)
    dau = r"(?<![\d.,])" if ct_chuan[0].isdigit() else r"(?<!\w)"
    cuoi = r"(?!\d|[.,]\d)" if ct_chuan[-1].isdigit() else r"(?!\w)"
    return dau + mau + cuoi


# ─── _khop_chi_tiet_thuoc() — Kiểm chi tiết thuốc có nằm trong văn dẫn ────────────────
# So theo ranh giới số/từ: "5 mg" không khớp "25 mg".
def _khop_chi_tiet_thuoc(chi_tiet: str, van_dan: str) -> bool:
    ct_chuan = _chuan_so_lieu_thuoc(chi_tiet)
    vd_chuan = _chuan_so_lieu_thuoc(van_dan)
    if not ct_chuan:
        return True
    # Chỉ khớp theo ranh giới số/từ: "5 mg" không bao giờ khớp vào
    # "25 mg" / "2.5 mg", "1 viên" không khớp vào "11 viên"
    return bool(re.search(_mau_ranh_gioi(ct_chuan), vd_chuan))


# ═══ tim_trich() — Tìm câu trích trong lượt nói ═══════════════════════════════════════
# Trả về vị trí (đầu, cuối) trên văn bản gốc hoặc None nếu không có.
def tim_trich(trich, van) -> Optional[Tuple[int, int]]:
    t = _chuan_trich(trich)
    if not t:
        return None
    s, bd = _chuan_ban_do(_nfc(van))
    k = s.find(t)
    if k < 0:
        return None
    return bd[k], bd[k + len(t) - 1] + 1


# ─── _luot() — Lập bảng lượt nói từ hội thoại ─────────────────────────────────────────
# Số lượt cho ra (vai, nội dung).
def _luot(hoi_thoai) -> Dict[int, Tuple[str, str]]:
    return {so: (str(vai or "").lower(), _nfc(van))
            for so, vai, van in thuc_the.tach_luot(hoi_thoai)}


# ═══ tim_nguoi() — Nhận diện người được nhắc trong một đoạn ═══════════════════════════
# Trả về các cờ như bản thân, họ hàng, sở hữu họ hàng.
# ----------------------------------------------------- từ chỉ người
def tim_nguoi(doan: str) -> Dict[str, bool]:
    t = chuan_hoa.chuan_hoa(doan)
    da = [False] * len(t)

    def tim(cac):
        co = False
        for c in sorted(cac, key=len, reverse=True):
            for m in re.finditer(rf"(?<!\w){re.escape(c)}(?!\w)", t):
                if any(da[m.start():m.end()]):
                    continue
                for k in range(m.start(), m.end()):
                    da[k] = True
                co = True
        return co

    tim(_TU_XUNG_KE)
    ra = {}
    ra["ho_hang_so_huu"] = tim([f"{a} {b}" for a in _SO_HUU_GOC for b in _SO_HUU_DUOI])
    ra["bn_ro"] = tim(TU_BENH_NHAN_RO)
    ra["ho_hang"] = tim(TU_HO_HANG)
    ra["tu_xung_ro"] = tim(TU_TU_XUNG_RO)
    ra["mo"] = tim(TU_MO)
    return ra


# ═══ kiem_chu_the() — Kiểm chủ thể của mệnh đề khớp với người trong đoạn ══════════════
# Lệch thì trả (CẢNH BÁO hoặc CHẶN, mã lý do như chu_the_nguoi_khac); khớp thì trả
# (None, None).
def kiem_chu_the(la_bn: bool, vai: str, ng: Dict[str, bool]):
    ho_hang = ng["ho_hang"] or ng["ho_hang_so_huu"]
    if la_vai_nhan_vien(vai):
        if la_bn or ho_hang:
            return None, None
        return CANH_BAO, "chu_the_chua_ro"
    if vai == "bệnh nhân":
        if la_bn:
            if ng["ho_hang_so_huu"] and not ng["tu_xung_ro"]:
                return CANH_BAO, "chu_the_nguoi_khac"
            return None, None
        return (None, None) if ho_hang else (CANH_BAO, "chu_the_chua_ro")
    if la_bn:
        if ng["bn_ro"] or ng["mo"]:
            return None, None
        if ng["tu_xung_ro"]:
            return CHAN, "chu_the_nguoi_ke"
        if ho_hang:
            return CANH_BAO, "chu_the_nguoi_khac"
        return CANH_BAO, "chu_the_suy_tu_nguoi_noi"
    if ng["tu_xung_ro"] or ho_hang:
        return None, None
    if ng["bn_ro"]:
        return CHAN, "chu_the_benh_nhan"
    if ng["mo"]:
        return CANH_BAO, "chu_the_chua_ro"
    return CANH_BAO, "chu_the_suy_tu_nguoi_noi"


# ─── _dau_cau() — Tìm vị trí đầu câu chứa một vị trí ──────────────────────────────────
def _dau_cau(van, a):
    return max(van.rfind(c, 0, a) for c in ".?!…\n") + 1


# ─── _cuoi_cau() — Tìm vị trí cuối câu từ một vị trí ──────────────────────────────────
def _cuoi_cau(van, b):
    idx = [van.find(c, b) for c in ".?!…\n" if van.find(c, b) != -1]
    return min(idx) if idx else len(van)


# ─── _dau_menh_de() — Lùi về đầu vế câu gần nhất ──────────────────────────────────────
# Để xác định phạm vi điều kiện hay phòng ngừa.
def _dau_menh_de(van, a):
    """Lùi về đầu mệnh đề gần nhất để xác định phạm vi điều kiện/phòng ngừa."""
    return max(van.rfind(c, 0, a) for c in ",;:.?!…\n") + 1


# ─── _cuoi_menh_de() — Tiến tới cuối vế câu gần nhất ──────────────────────────────────
def _cuoi_menh_de(van, b):
    idx = [van.find(c, b) for c in ",;:.?!…\n" if van.find(c, b) != -1]
    return min(idx) if idx else len(van)


# ─── _nguoi_quanh() — Tìm người nhắc quanh vị trí câu trích ───────────────────────────
# Không thấy trong đoạn thì tìm ở phần đầu câu.
def _nguoi_quanh(van, a, b):
    ng = tim_nguoi(van[a:b])
    if any(ng.values()):
        return ng
    return tim_nguoi(van[_dau_cau(van, a):a])


# ─── _them() — Thêm mã lý do vào danh sách chặn hoặc cảnh báo ─────────────────────────
# Bỏ qua nếu mức hoặc mã là None, không thêm trùng.
# ----------------------------------------------------- một phát biểu
def _them(kq, muc, ma):
    if muc is None or ma is None:
        return
    ds = kq.chan if muc == CHAN else kq.canh_bao
    if ma not in ds:
        ds.append(ma)


# ═══ khoa_mot() — Khoá căn cứ một mệnh đề qua các phép kiểm K1 đến K7 ═════════════════
# Kiểm nguồn, nội dung, chủ thể, mức khẳng định, mốc thời gian, chi tiết thuốc, bị thay
# thế.
def khoa_mot(p, cac_luot, bat_buoc_trich_dan=True) -> KetQua:
    kq = KetQua(id=p.id)
    for n in (p.bang_chung or []):
        if n not in cac_luot:
            _them(kq, CHAN, "luot_khong_ton_tai")
    hop_le = [n for n in (p.bang_chung or []) if n in cac_luot]

    # --- K1 nguồn
    trich = list(getattr(p, "trich_dan", None) or [])
    if not trich:
        _them(kq, CHAN if bat_buoc_trich_dan else CANH_BAO, "khong_trich_dan")
    for k, t in enumerate(trich):
        so_dan = hop_le[k] if k < len(hop_le) else (hop_le[-1] if hop_le else None)
        thu_tu = ([so_dan] if so_dan is not None else []) + \
                 [s for s in cac_luot if s != so_dan]
        tim_thay = None
        for s in thu_tu:
            vt = tim_trich(t, cac_luot[s][1])
            if vt:
                tim_thay = (s, vt)
                break
        if tim_thay is None:
            _them(kq, CHAN, "trich_khong_co")
            continue
        if tim_thay[0] != so_dan:
            _them(kq, CANH_BAO, "trich_lech_luot")
        kq.doan.append((tim_thay[0], tim_thay[1][0], tim_thay[1][1]))

    if kq.doan:
        doan_van = [(s, cac_luot[s][1], a, b) for s, a, b in kq.doan]
    else:
        doan_van = [(s, cac_luot[s][1], 0, len(cac_luot[s][1])) for s in hop_le]
    if not doan_van:
        return kq
    nguon = hop_le or sorted({s for s, _v, _a, _b in doan_van})

    can_cu = []
    for s, van, a, b in doan_van:
        can_cu.append(van[a:b])
        if not _tu_noi_dung(chuan_hoa.chuan_hoa(van[a:b])) and (s - 1) in cac_luot \
                and la_vai_nhan_vien(cac_luot[s - 1][0]):
            can_cu.append(cac_luot[s - 1][1])
    can_cu_van = " ".join(can_cu)

    # --- K2 nội dung
    nd_chuan = chuan_hoa.chuan_hoa(p.noi_dung)
    tu_nd = set(_tu_noi_dung(nd_chuan))
    if tu_nd:
        co = tu_nd & set(_tu_noi_dung(chuan_hoa.chuan_hoa(can_cu_van)))
        chac = tu_nd & set(_tu_noi_dung(chuan_hoa.chuan_hoa(can_cu_van, gom_can_hoi=False)))
        if not co:
            _them(kq, CANH_BAO, "noi_dung_khong_khop")
        elif not chac:
            _them(kq, CANH_BAO, "phuong_ngu_can_hoi")

    # --- K3 chủ thể
    so_cuoi = max(nguon)
    vai = cac_luot[so_cuoi][0]
    ng = {"ho_hang_so_huu": False, "bn_ro": False, "ho_hang": False,
          "tu_xung_ro": False, "mo": False}
    for s, van, a, b in doan_van:
        if s != so_cuoi:
            continue
        for k, v in _nguoi_quanh(van, a, b).items():
            ng[k] = ng[k] or v
    _them(kq, *kiem_chu_the(getattr(p, "chu_the_id", 0) == 0, vai, ng))

    # --- K4 mức khẳng định & tính hợp lệ của thông tin
    thuc_te = getattr(p, "tinh_huong", "thực tế") == "thực tế"
    chac_chan = getattr(p, "do_chac_chan", "chắc chắn") == "chắc chắn"
    phu_dinh = bool(getattr(p, "phu_dinh", False))
    tu_nd_tho = set(re.findall(r"\w+", nd_chuan))

    for s, van, a, b in doan_van:
        cau_toan_bo = chuan_hoa.chuan_hoa(van[_dau_cau(van, a):_cuoi_cau(van, b)], gom_can_hoi=False)
        cau_truoc_trich = chuan_hoa.chuan_hoa(van[_dau_cau(van, a):b], gom_can_hoi=False)
        menh_de = chuan_hoa.chuan_hoa(van[_dau_menh_de(van, a):_cuoi_menh_de(van, b)], gom_can_hoi=False)
        doan = chuan_hoa.chuan_hoa(van[a:b], gom_can_hoi=False)

        # 1. Kiểm tra đính chính ngầm / bác bỏ sau kiểm chứng
        if thuc_te and not phu_dinh:
            if DAU_DINH_CHINH_NGAM.search(cau_toan_bo) or DAU_BAC_BO_TRUC_TIEP.search(cau_toan_bo):
                _them(kq, CHAN, "dinh_chinh_ngam")

        # 2. Kiểm tra câu điều kiện / phòng ngừa tương lai
        # Nếu mệnh đề nằm sau liên từ chuyển ý đối lập (còn, nhưng...) thì không kế thừa tiền đề điều kiện phía trước
        la_ve_chuyen_y = bool(re.search(r"(,\s*(còn|nhưng|tuy nhiên|song|hiện tại|hôm nay))\b", cau_truoc_trich, re.I))
        dieu_kien_tim_thay = DAU_DIEU_KIEN.search(menh_de) or (not la_ve_chuyen_y and DAU_DIEU_KIEN.search(cau_truoc_trich))

        if thuc_te and dieu_kien_tim_thay:
            _them(kq, CHAN, "dieu_kien")

        # 3. Kiểm tra độ chắc chắn
        if thuc_te and chac_chan and not phu_dinh:
            if DAU_NGHI.search(doan) or DAU_THEO_DOI.search(doan):
                _them(kq, CHAN, "vuot_muc_nghi")
            elif DAU_CHUA_GHI_NHAN.search(doan):
                _them(kq, CHAN, "vuot_muc_chua_ghi_nhan")
            elif any(m.group(1).split()[0] not in tu_nd_tho
                     for m in DAU_PHU_DINH.finditer(doan)):
                _them(kq, CANH_BAO, "co_tu_phu_dinh")

        if phu_dinh and chac_chan and DAU_CHUA_GHI_NHAN.search(doan):
            _them(kq, CANH_BAO, "phu_dinh_vuot_muc")

    # --- K5 mốc thời gian
    moc = getattr(p, "moc_thoi_gian", None)
    if moc:
        tu_moc = set(_tu_noi_dung(chuan_hoa.chuan_hoa(moc)))
        luot_van = " ".join(cac_luot[s][1] for s in nguon)
        if tu_moc and not tu_moc <= set(_tu_noi_dung(chuan_hoa.chuan_hoa(luot_van))):
            _them(kq, CANH_BAO, "moc_khong_thay")

    # --- K6 chi tiết thuốc
    t = getattr(p, "thuoc", None)
    if t:
        van_dan = _chuan_trich(" ".join(cac_luot[s][1] for s in nguon))
        if t.get("lieu") and not _khop_chi_tiet_thuoc(t["lieu"], van_dan):
            _them(kq, CHAN, "lieu_khong_thay")
        for khoa in ("so_lan", "bat_dau", "ngung"):
            if t.get(khoa) and not _khop_chi_tiet_thuoc(t[khoa], van_dan):
                _them(kq, CANH_BAO, "chi_tiet_thuoc_khong_thay")
        duong = t.get("duong_dung")
        if duong and not re.search(rf"(?<!\w){re.escape(duong)}(?!\w)", van_dan):
            _them(kq, CANH_BAO, "duong_dung_khong_thay")

    # --- K7: Supersession / Contradiction (thông tin bị thay thế hoặc mâu thuẫn)
    if getattr(p, "trang_thai", "còn hiệu lực") == "bị thay thế":
        _them(kq, CHAN, "bi_thay_the")
    elif getattr(p, "trang_thai", "còn hiệu lực") == "chưa giải quyết":
        _them(kq, CANH_BAO, "mau_thuan")
    return kq


# ----------------------------------------------------- kiểm đầy đủ
# None = tiêu chí cũ (chung MỘT từ nội dung với mệnh đề dẫn tới lượt là đã ghi). Đổi ở đây
# để đo (Task 2.3); mặc định giữ None để không đổi số của chính sách C.
NGUONG_PHU_MAC_DINH: Optional[float] = None
_THUC_THE_SO = re.compile(r"\d+(?:[.,]\d+)?")


# ─── _thuoc_moi() — Kiểm đoạn có hoạt chất chưa nằm trong mệnh đề ─────────────────────
# Hoạt chất xuất hiện trong đoạn mà các mệnh đề dẫn tới lượt đó chưa có.
def _thuoc_moi(doan: str, chu_menh_de: str) -> bool:
    """Đoạn có hoạt chất nào không xuất hiện trong các mệnh đề dẫn tới lượt đó."""
    from src.cong_cu_lam_sang import tri_thuc_thuoc as tri_thuc_thuoc

    def hc(t):
        return {tri_thuc_thuoc.hoat_chat(m.group(0)) or m.group(0).lower()
                for m in thuc_the.THUOC_TU_DIEN.finditer(t)}
    trong_doan = hc(doan)
    return bool(trong_doan) and not trong_doan <= hc(chu_menh_de)


_DI_UNG_CHAT = re.compile(r"(?<!\w)(dị ứng|mẫn cảm)(?!\w)\s*(?:với\s+)?([^,;.?!]*)")
_NGAT_CHAT = re.compile(r"(?<!\w)(còn|nhưng|và|mà|thì|nên|khi|lúc|từ|hồi)(?!\w)")
_KHONG_PHAI_CHAT = {"gì", "cả", "đâu", "ạ", "nào", "bao", "giờ", "hết", "nữa", "luôn", "rồi", "thôi", "nhé", "à",
                    "không", "chưa", "có", "bị", "thì", "lắm", "đó", "này", "ấy"}


# ─── _di_ung_moi() — Kiểm đoạn nói dị ứng chất chưa có trong mệnh đề ──────────────────
# Tránh "bé chưa dị ứng thuốc" che nhầm "anh trai dị ứng trứng".
def _di_ung_moi(doan: str, chu_menh_de: str) -> bool:
    """Doan noi "dị ứng X" ma chat X chua co trong menh de nao dan toi luot do: "anh trai dị ứng trứng"
    không được che bởi "bé chưa dị ứng thuốc" chỉ vì chứng chữ "dị ứng" (vòng 5 cây lỗi 25/11/2026)."""
    m = _DI_UNG_CHAT.search(doan.lower())
    if not m:
        return False
    chat = [w for w in _NGAT_CHAT.split(m.group(2))[0].split() if w not in _KHONG_PHAI_CHAT]
    co = set(chu_menh_de.split())
    return bool(chat) and any(w not in co for w in chat)


# ─── _thuc_the() — Lấy tên thuốc và con số trong một đoạn ─────────────────────────────
# Những thứ không được mất khi ghi.
def _thuc_the(t: str) -> set:
    """Tên thuốc và con số trong đoạn — thứ không được mất khi ghi."""
    return {m.group(0).lower() for m in thuc_the.THUOC_TU_DIEN.finditer(t)} | set(_THUC_THE_SO.findall(t))


# ═══ doan_chua_ghi() — Tìm đoạn hội thoại có nội dung mà không mệnh đề nào dẫn ════════
# Đoạn coi là đã ghi nếu nằm trong câu trích, hoặc đủ tỉ lệ từ nội dung, hoặc đủ thực
# thể.
def doan_chua_ghi(ket_qua: List[KetQua], ps, cac_luot, nguong_phu: Optional[float] = "mac_dinh") -> List[dict]:
    """Đoạn hội thoại có nội dung mà không phát biểu nào dẫn tới.

    `nguong_phu=None`: tiêu chí cũ — đoạn đã ghi nếu giao với một khoảng trích dẫn HOẶC
    chung một từ nội dung với mệnh đề dẫn tới lượt đó. Trên lượt dài, một từ chung là đủ
    che cả ý khác (đo 25/11/2026: 172/200 mệnh đề bị sót nằm ở lượt đã được dẫn).
    `nguong_phu=x`: đã ghi khi nằm TRỌN trong khoảng trích dẫn, HOẶC tỉ lệ từ nội dung của
    đoạn có trong mệnh đề >= x, HOẶC mọi thực thể (thuốc, con số) của đoạn có trong mệnh đề."""
    if nguong_phu == "mac_dinh":
        nguong_phu = NGUONG_PHU_MAC_DINH
    phu, tu_theo_luot, chu_theo_luot = {}, {}, {}
    for kq, p in zip(ket_qua, ps):
        luot_cua = {s for s, _a, _b in kq.doan} | \
                   {n for n in (p.bang_chung or []) if n in cac_luot}
        tu = set(_tu_noi_dung(chuan_hoa.chuan_hoa(p.noi_dung)))
        # Bản BỊ THAY THẾ không che thực thể: "amoxicillin 250 mg, à nhầm, 500 mg" chỉ còn bản cũ thì bản
        # mới vẫn là chưa ghi (vòng 5 cây lỗi 25/11/2026).
        thay_the = getattr(p, "trang_thai", "còn hiệu lực") == "bị thay thế"
        for s in luot_cua:
            tu_theo_luot.setdefault(s, set()).update(tu)
            if thay_the:
                continue
            ten_thuoc = ((getattr(p, "thuoc", None) or {}).get("ten")) or ""
            chu_theo_luot[s] = f"{chu_theo_luot.get(s, '')} {str(p.noi_dung or '').lower()} {ten_thuoc.lower()}"
        for s, a, b in kq.doan:
            phu.setdefault(s, []).append((a, b))
    from src.canh_bao.loi_noi import co_dau_cau, nhan_cau_hoi, tach_y
    ra = []
    for so, (vai, van) in sorted(cac_luot.items()):
        # Lượt không dấu câu (chép từ âm thanh): tách theo từ nối, nhãn câu hỏi theo tiểu
        # từ. Lượt có dấu giữ nguyên cách cũ. Thêm 25/11/2026 (Task 3.1).
        co_dau = co_dau_cau(van)
        for a, b in (cac_doan(van) if co_dau else tach_y(van)):
            # Chỉ bó câu hỏi của NHÂN VIÊN: lời người bệnh không dấu mà đoán nhầm là câu hỏi sẽ
            # mất hết cảnh báo bỏ sót (rà soát 25/11).
            if dau_ket(van, (a, b)) == "?" or (not co_dau and la_vai_nhan_vien(vai) and nhan_cau_hoi(van[a:b])):
                continue
            doan = van[a:b]
            if THU_TUC.search(doan.lower()):
                continue
            tu = set(_tu_noi_dung(chuan_hoa.chuan_hoa(doan)))
            if not tu:
                continue
            # Tên thuốc chưa có trong mệnh đề nào của lượt: LUÔN là chưa ghi, dù chứng chữ "dị ứng"
            # với một mệnh đề khác ("không dị ứng thức ăn, dị ứng penicillin") — rà soát 25/11.
            if _thuoc_moi(doan, chu_theo_luot.get(so, "")) or _di_ung_moi(doan, chu_theo_luot.get(so, "")):
                ra.append({"luot": so, "vai": vai, "doan": doan, "bat_dau": a, "ket_thuc": b})
                continue
            if nguong_phu is None:
                if any(x < b and a < y for x, y in phu.get(so, ())):
                    continue
                if tu & tu_theo_luot.get(so, set()):
                    continue
            else:
                if any(x <= a and b <= y for x, y in phu.get(so, ())):
                    continue
                if len(tu & tu_theo_luot.get(so, set())) / len(tu) >= nguong_phu:
                    continue
                tt = _thuc_the(doan.lower())
                if tt and tt <= _thuc_the(chu_theo_luot.get(so, "")):
                    continue
            ra.append({"luot": so, "vai": vai, "doan": doan,
                       "bat_dau": a, "ket_thuc": b})
    return ra


CHU_DE_HOI = (
    ("di_ung", re.compile(r"(?<!\w)(dị ứng|mẫn cảm|phản vệ)(?!\w)")),
    ("thuoc", re.compile(r"(?<!\w)(thuốc|uống|tiêm|xịt|bôi|đơn thuốc|kháng sinh)(?!\w)")),
    ("tien_su", re.compile(r"(?<!\w)(trước (giờ|đây|nay)|tiền sử|mạn tính|từng|mổ|phẫu thuật|trong nhà|gia đình"
                           r"|ai bị|bệnh gì|nằm viện)(?!\w)")),
    ("trieu_chung", re.compile(r"(?<!\w)(sốt|ho|đau|nôn|buồn nôn|khó thở|tiêu chảy|mệt|chóng mặt|ngứa|sưng|phù"
                               r"|chảy máu|ra máu|đi ngoài|táo bón|tức ngực|khò khè|co giật|nổi|ăn uống|ngủ)(?!\w)")),
)
SO_TU_TRA_LOI_TOI_DA = 6


# ═══ cap_hoi_dap_chua_ghi() — Tìm cặp hỏi–đáp ngắn chưa có mệnh đề ════════════════════
# Câu hỏi của nhân viên rồi lượt đáp ≤ 6 chữ của người bệnh hoặc người nhà.
def cap_hoi_dap_chua_ghi(ket_qua: List[KetQua], ps, cac_luot) -> List[dict]:
    """Cặp (lượt nhân viên là câu hỏi, lượt ngay sau của người bệnh / người nhà, <= 6 chữ)
    mà KHÔNG phát biểu nào dẫn tới lượt trả lời. Thêm 25/11/2026 (L4 trong
    docs/superpowers/plans/2026-11-25-cai-thien-bo-luat.md).

    Nhãn câu hỏi bằng `canh_bao.loi_noi.nhan_cau_hoi`, chịu được văn không dấu câu.
    `chu_de` suy từ câu hỏi; "khác" khi không khớp chủ đề lâm sàng nào."""
    from src.canh_bao.loi_noi import nhan_cau_hoi
    da_dan = set()
    for kq, p in zip(ket_qua, ps):
        da_dan |= {s for s, _a, _b in kq.doan}
    for p in ps:
        da_dan |= {n for n in (getattr(p, "bang_chung", None) or []) if n in cac_luot}
    ra = []
    so = sorted(cac_luot)
    for hoi, dap in zip(so, so[1:]):
        if dap != hoi + 1:
            continue
        (vai_h, van_h), (vai_d, van_d) = cac_luot[hoi], cac_luot[dap]
        if not la_vai_nhan_vien(vai_h) or la_vai_nhan_vien(vai_d) or dap in da_dan:
            continue
        if not nhan_cau_hoi(van_h) or len(van_d.split()) > SO_TU_TRA_LOI_TOI_DA or not van_d.strip():
            continue
        t = unicodedata.normalize("NFC", van_h).lower()
        chu_de = next((ten for ten, bt in CHU_DE_HOI if bt.search(t)), "khac")
        ra.append({"luot_hoi": hoi, "luot_dap": dap, "cau_hoi": van_h, "tra_loi": van_d,
                   "chu_de": chu_de, "vai": vai_d})
    return ra


# ═══ khoa_ca() — Khoá căn cứ cho cả danh sách mệnh đề ═════════════════════════════════
# Trả về kết quả từng mệnh đề, đoạn chưa ghi và cặp hỏi–đáp chưa ghi.
def khoa_ca(ps, hoi_thoai, bat_buoc_trich_dan=True) -> dict:
    cac_luot = _luot(hoi_thoai)
    kq = [khoa_mot(p, cac_luot, bat_buoc_trich_dan) for p in ps]
    return {"ket_qua": kq, "doan_chua_ghi": doan_chua_ghi(kq, ps, cac_luot),
            "cap_hoi_dap_chua_ghi": cap_hoi_dap_chua_ghi(kq, ps, cac_luot)}


# ═══ ly_do_chan() — Gom lý do chặn thành chuỗi theo mã mệnh đề ════════════════════════
# Chỉ gồm mệnh đề có bị chặn.
def ly_do_chan(ket_qua: List[KetQua]) -> Dict[int, str]:
    return {k.id: "; ".join(LY_DO[m] for m in k.chan)
            for k in ket_qua if k.chan}