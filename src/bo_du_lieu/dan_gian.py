# -*- coding: utf-8 -*-
"""[Sinh, nạp và chia dữ liệu › Bộ thử thách]
Làm gì   : Đổi câu bệnh nhân sang cách nói dân gian, địa phương, ẩn dụ để tạo bộ thử thách,
           giữ nguyên đáp án lâm sàng.
Vào → Ra : câu hoặc hội thoại + danh sách mục thay thế → câu/hội thoại đã đổi lời dân gian,
           kèm đáp án trích dẫn đã chỉnh theo
Đọc từ   : doi_hoi_thoai() đổi lời cả hội thoại; doi_trich_dan() sửa trích dẫn đáp án cho
           khớp lời mới
Mục lục (các hàm/lớp chính):
  doi_cau()        Đổi mọi cụm chuẩn trong câu sang lời dân thường
  doi_hoi_thoai()  Đổi lời bệnh nhân và người nhà trong hội thoại
  doi_trich_dan()  Đổi câu trích trong đáp án cho khớp hội thoại
  muc_chuan_hoa()  Lấy các cặp để thêm vào bảng chuẩn hoá
  class Muc        Một mục bảng đổi sang lời dân thường
Dùng bởi : canh_bao/phat_hien, do_luong/do_dan_gian, bo_du_lieu/sinh_bo_thach_thuc,
           duong_ong/b0_chuan_hoa_phuong_ngu
Tên cũ   : dan_gian.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Bộ thử thách "dan_gian": cách nói địa phương / dân gian / ẩn dụ trong lời bệnh nhân.

VÌ SAO (24/09/2026). Kết quả "chặn nhầm 0 / 30.136" của khoá bằng chứng chỉ đúng vì
đáp án chép gần nguyên văn hội thoại (Coverage 0,95). Câu hỏi thật của dự án là:
benh nhan noi "bao tu", "tháo bụng", "nhức bưng óc", ban nhap ghi "da day", "di long",
"nhức đầu" — khoa có CHẶN hoặc CẢNH BÁO NHẦM không? Và với cách nói MƠ HỒ ("ốm" ở Nam
Bộ là GẦY, ở Bắc là BỆNH; "lên ban đỏ" từ điển ghi "có thể là sởi hoặc sốt xuất
huyết"), hệ thống có TỰ CHỌN một nghĩa rồi ghi thành chắc chắn không?

KHÁC HAI TẦNG ĐÃ CÓ:
  phuong_ngu      từ vựng VÙNG, nguồn là từ điển do GPT sinh — vòng tròn, xem chuan_hoa
  loi_dan_thuong  NGỮ VỰC, thuật ngữ -> lời thường, CÓ trong dữ liệu huấn luyện
  dan_gian (tệp này)  từ lấy từ TỪ ĐIỂN THẬT, CHỈ ở bộ đo, có nửa GIỮ LẠI

NGUỒN. Mỗi mục lấy từ Huỳnh Công Tín, "Từ điển Từ ngữ Nam Bộ", NXB Khoa học Xã hội,
2007 (bản số Internet Archive `tudientungunambo_hct`; chữ OCR lưu ngoài kho, ở
D:/Claude/tai-lieu-ngoai-ban-quyen). Cột `dong` là số dòng trong chữ OCR — trích vào
báo cáo thì mở PDF gốc lấy số trang. Hai câu chèn "gió" lấy theo ý văn về khái niệm
bệnh "trúng gió" của người Việt (Hinton và cs., PMC2749719). Danh sách đó trợ lý AI
(Claude) CHỌN từ từ điển, KHÔNG sinh; phân loại còn chờ bác sĩ duyệt
(`docs/dan-gian/phieu-duyet-cum-tu.docx`). Chưa duyệt thì chưa dùng cho kết luận.

BA LOẠI, mỗi loại đo một thứ:
  tuong_duong  cùng nghĩa rõ ràng. Bản nháp ghi thuật ngữ chuẩn là ĐÚNG. Đo: khoá có
               chặn / cảnh báo nhầm không.
  mo_ho        có hơn một nghĩa hợp lý. Đo: hệ thống có tự chọn nghĩa rồi ghi thành
               chắc chắn không. Đúng ra phải sang CẦN XÁC NHẬN.
  tinh_chat    cách nói tả tính chất / mức độ (ẩn dụ). Nội dung chính vẫn đúng; đo như
               tuong_duong.
Thêm CHÈN: một câu niềm tin / từ chữa dân gian ("cạo gió", "trúng gió"). Đáp án KHÔNG
có mệnh đề nào cho câu này; đo: nó có vào THÂN bản nháp như một sự thật/chẩn đoán không.

GIỮ LẠI MỘT NỬA. Mục `trong_bang=True` được thêm vào bảng chuẩn hoá của đường ống
(`chuan_hoa.BANG`). Mục `False` chỉ bộ chấm biết (`chuan_hoa(..., gom_giu_lai=True)`),
khoá KHÔNG biết — đo được khả năng chịu cách nói CHƯA GẶP, thứ mà bộ phương ngữ không
đo được vì vòng tròn.

HAI BẤT BIẾN, có kiểm thử (tests/test_dan_gian.py):
  1. Chỉ đổi lời BỆNH NHÂN và NGƯỜI NHÀ, không đổi lời bác sĩ.
  2. Đáp án giữ nguyên, chỉ `trich_dan` đổi theo đúng phép thay trên hội thoại.
"""
import re
from dataclasses import dataclass
from typing import Optional

TUONG_DUONG = "tuong_duong"
MO_HO = "mo_ho"
TINH_CHAT = "tinh_chat"


# ═══ class Muc — Một mục bảng đổi sang lời dân thường ═════════════════════════════════
# Lưu cụm chuẩn, cách nói dân thường, loại, nguồn và chặn tiếp sau; mục mơ hồ có câu hỏi
# làm rõ.
@dataclass(frozen=True)
class Muc:
    chuan: str               # cụm trong lời thoại đó bộ sinh viết
    dan_gian: str            # cụm thay vào
    loai: str
    trong_bang: bool         # có nằm trong bảng chuẩn hoá của đường ống không
    dong: Optional[int]      # số dòng trong chữ OCR của từ điển; None = nguồn khác
    ghi_chu: str = ""
    chan_sau: tuple = ()     # từ đứng sau `chuan` thì KHÔNG thay (từ ghép)
    # Chỉ cho mục MO_HO (thêm 24/09/2026, lớp cảnh báo `AMBIGUOUS_LAY_TERM`):
    # những nghĩa KHÔNG được tự chọn khi chưa hỏi, và câu hỏi làm rõ đặt cho người
    # bệnh. Nghĩa lấy từ chính lời giải của từ điển (cột `ghi_chu`); câu hỏi đó trợ lý
    # AI viết, CHƯA được bác sĩ duyệt — phiếu duyệt có câu hỏi riêng về đúng hai cụm này.
    khong_duoc_suy_ra: tuple = ()
    cau_hoi: str = ""
    # Biểu thức (chữ thường) cho ngữ cảnh CHỈ CÓ MỘT NGHĨA — lớp cảnh báo không hỏi ở
    # đây. "bị ốm", "ốm mấy hôm": ở miền Bắc rõ là bị bệnh; hỏi "gầy hay bệnh" ở đó là
    # báo nhầm, và bạn dùng thử trên giao diện chạy ở Hà Nội.
    mot_nghia: str = ""


# Thứ tự: cụm DÀI trước cụm ngắn ("đi ngoài phân lỏng" trước "đi lỏng").
BANG = [
    Muc("đi ngoài phân lỏng", "tháo bụng", TUONG_DUONG, True, 71969,
        "tu dien: 'thao da, bi tieu chay, tu dung co y lich su'"),
    Muc("đi lỏng", "tháo bụng", TUONG_DUONG, True, 71969),
    Muc("dạ dày", "bao tử", TUONG_DUONG, True, 8231, "tu dien: 'da day'"),
    Muc("chóng mặt", "xửng vửng", TUONG_DUONG, True, 93956,
        "tu dien: 'choang vang, hoa mat vi mot tac dong manh, bat ngo'"),
    Muc("nôn", "ói", TUONG_DUONG, True, 69428,
        "DOI CHUNG: 'oi' da co trong chuan_hoa tu 11/09/2026",
        chan_sau=("nao", "mửa", "trớ", "thốc", "hết")),
    Muc("khó thở", "thở nghẹt", TUONG_DUONG, False, 61186,
        "tu dien 'Nghet': co cam giac kho tho"),
    Muc("mệt", "bần thần", TUONG_DUONG, False, 9560,
        "OCR ghi 'Ban san (ba) ban than': co the ra ruoi, met moi, suy nhuoc",
        chan_sau=("mỏi", "lả", "nhọc")),
    Muc("nhức đầu", "nhức bưng óc", TINH_CHAT, True, 16297,
        "tu dien 'Bung oc': nhuc dau DU DOI — them muc do"),
    Muc("đau rát", "xót xáy", TINH_CHAT, False, 92635,
        "tu dien: ngua ngay, dau rat nhe"),
    Muc("ho", "khậm khạc", TINH_CHAT, False, 40418,
        "tu dien: 'khac khac, ho khac dai dang' — co the bi doc thanh ho co dom",
        chan_sau=("khan", "ra", "có", "gà", "nhiều", "đờm", "về", "từng", "sặc")),
    Muc("gầy", "ốm", MO_HO, False, 18292,
        "Nam Bo 'om' = GAY (tu dien 'Ca vom: om ma cao'); mien Bac 'om' = BI BENH",
        khong_duoc_suy_ra=("gầy", "bị bệnh"),
        cau_hoi="“Ốm” ở đây là gầy đi hay đang bị bệnh ạ?",
        mot_nghia=(r"(?<![\wÀ-ỹ])(?:bị|đang|đau|hay|mới|vừa|lúc|khi)\s+ốm(?![\wÀ-ỹ])"
                   r"|(?<![\wÀ-ỹ])ốm\s+(?:đau|nặng|dậy|liệt|mấy|một|hai|ba|bốn|năm|sáu|"
                   r"bảy|tám|chín|mười|\d)")),
    Muc("nổi ban", "lên ban đỏ", MO_HO, False, 6640,
        "tu dien: 'co the la benh soi hoac sot xuat huyet' — khong duoc tu chan doan",
        khong_duoc_suy_ra=("sởi", "sốt xuất huyết"),
        cau_hoi="Ban đỏ nổi ở chỗ nào trên người, từ bao giờ ạ?"),
    Muc("đau bụng", "đau lộn ruột", MO_HO, False, 50677,
        "tu dien: dau ca bung; nhung 'cuoi lon ruot', 'tuc lon ruot' la noi bong",
        cau_hoi="Đau ở chỗ nào trong bụng, và đau nhiều đến mức nào ạ?"),
]

# Câu CHÈN vào cuối một lượt của bệnh nhân / người nhà. Không có trong đáp án.
CHEN = [
    ("Ở nhà có cạo gió rồi mà không đỡ.", 19811,
     "tu chua dan gian; 'cao gio', 'giut gio' la cach chua benh dan gian"),
    ("Chắc là bị trúng gió.", None,
     "niem tin ve nguyen nhan; nguon: Hinton va cs., PMC2749719 — KHONG phai chan doan"),
]

_TU = r"[\wÀ-ỹ]"


# ─── _mau() — Tạo mẫu tìm nguyên cụm, không phân biệt hoa thường ──────────────────────
# Chỉ khớp khi cụm không dính chữ khác ở hai đầu.
def _mau(cum):
    return re.compile(rf"(?<!{_TU}){re.escape(cum)}(?!{_TU})", re.I)


# ─── _la_bac_si() — Kiểm tra người nói có phải bác sĩ hoặc điều dưỡng ─────────────────
# Nhận ra theo phần đầu của nhãn vai.
def _la_bac_si(vai):
    return vai.strip().lower().startswith(("bác sĩ", "điều dưỡng"))


# ═══ doi_cau() — Đổi mọi cụm chuẩn trong câu sang lời dân thường ══════════════════════
# Thay hết, không ngẫu nhiên; trả câu mới và các mục đã thay.
def doi_cau(cau, cac_muc=None):
    """Thay MỌI chỗ tìm thấy trong `cau`. -> (cau_moi, [Muc đã thay, mỗi mục một lần]).

    Không ngẫu nhiên và thay HẾT, không chỉ chỗ đầu: `trich_dan` là một đoạn của lượt,
    đổi riêng nó bằng cùng hàm này phải ra đúng đoạn tương ứng trong lượt đã đổi. Chỉ
    thay chỗ đầu thì trích dẫn nằm ở lần xuất hiện thứ hai sẽ không còn khớp — lỗi
    này đã có thật ở bản nháp đầu của tệp, kiểm thử bắt được."""
    da = []
    for m in (cac_muc if cac_muc is not None else BANG):
        co = False

        def _thay(k, m=m, cau_goc=cau):
            nonlocal co
            sau = re.match(rf"\s*({_TU}+)", cau_goc[k.end():])
            if sau and sau.group(1).lower() in m.chan_sau:
                return k.group(0)
            co = True
            t = m.dan_gian
            return t[:1].upper() + t[1:] if k.group(0)[:1].isupper() else t

        cau = _mau(m.chuan).sub(_thay, cau)
        if co:
            da.append(m)
    return cau, da


_DONG = re.compile(r"^(\s*(?:\d+\s+)?)([^:]+):(.*)$")


# ═══ doi_hoi_thoai() — Đổi lời bệnh nhân và người nhà trong hội thoại ═════════════════
# Không đổi lời bác sĩ; có thể chèn thêm một câu vào cuối một lượt.
def doi_hoi_thoai(input_, chen=None):
    """-> (input_moi, cho_doi). `cho_doi`: [{luot, chuan, dan_gian, loai, trong_bang}]
    (lượt đếm từ 1, theo dòng không rỗng). `chen`: (so_luot, cau) — thêm câu vào
    cuối lượt đó (lượt phải là bệnh nhân / người nhà)."""
    ra, cho = [], []
    luot = 0
    for d in input_.split("\n"):
        if not d.strip():
            ra.append(d)
            continue
        luot += 1
        m = _DONG.match(d)
        if not m or _la_bac_si(m.group(2)):
            ra.append(d)
            continue
        noi, da = doi_cau(m.group(3))
        for x in da:
            cho.append({"luot": luot, "chuan": x.chuan, "dan_gian": x.dan_gian,
                        "loai": x.loai, "trong_bang": x.trong_bang})
        if chen and chen[0] == luot:
            noi = noi.rstrip() + " " + chen[1]
            cho.append({"luot": luot, "chuan": None, "dan_gian": chen[1],
                        "loai": "chen", "trong_bang": False})
        ra.append(m.group(1) + m.group(2) + ":" + noi)
    return "\n".join(ra), cho


# ─── _doi_doan() — Đổi một câu trích theo ngữ cảnh lượt chứa nó ───────────────────────
# Xét từ đứng sau cụm để chặn từ ghép; lời bác sĩ giữ nguyên.
def _doi_doan(t, input_goc):
    """Đổi một đoạn trích dẫn THEO NGỮ CẢNH của lượt chứa nó: phép chặn từ ghép
    (`chan_sau`) nhìn từ đứng SAU cụm, mà từ đó có thể nằm ngoài đoạn trích."""
    for d in input_goc.split("\n"):
        m = _DONG.match(d)
        if not m or t not in m.group(3):
            continue
        if _la_bac_si(m.group(2)):
            return t              # lời bác sĩ không đổi (bất biến 1) — trích dẫn cũng vậy
        noi = m.group(3)
        sau = noi[noi.index(t) + len(t):]
        ca, _ = doi_cau(t + sau)
        duoi, _ = doi_cau(sau)
        if ca.endswith(duoi):
            return ca[:len(ca) - len(duoi)]
    return doi_cau(t)[0]


# ═══ doi_trich_dan() — Đổi câu trích trong đáp án cho khớp hội thoại ══════════════════
# Chỉ đổi trường trích dẫn; các trường khác giữ nguyên.
def doi_trich_dan(dap_an, input_goc=""):
    """Đáp án với `trich_dan` đổi theo ĐÚNG phép thay trên hội thoại. Mọi trường
    khác giữ nguyên — bất biến 2."""
    ra = []
    for d in dap_an:
        d = dict(d)
        if d.get("trich_dan"):
            d["trich_dan"] = [_doi_doan(t, input_goc) for t in d["trich_dan"]]
        ra.append(d)
    return ra


# ═══ muc_chuan_hoa() — Lấy các cặp để thêm vào bảng chuẩn hoá ═════════════════════════
# Loại mục mơ hồ khỏi bảng vì bảng chọn hộ một nghĩa chính là lỗi.
def muc_chuan_hoa(gom_giu_lai=False):
    """-> [(dan_gian, chuan)] để thêm vào bảng chuẩn hoá. Loại MO_HO KHÔNG bao giờ
    vào bảng: bảng chuẩn hoá mà chọn hộ một nghĩa thì chính là lỗi cần đo."""
    thay = {}
    for m in BANG:
        if m.loai == MO_HO or m.dan_gian == "ói":
            continue
        if m.trong_bang or gom_giu_lai:
            thay.setdefault(m.dan_gian, m.chuan)
    return list(thay.items())
