# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 1 – Rút mệnh đề]
Làm gì   : Định nghĩa bản ghi một mệnh đề (nội dung, chủ thể, người nói, câu trích, lượt căn
           cứ) và đổi kết quả JSON của mô hình thành bản ghi đó.
Vào → Ra : JSON mô hình rút ra + người nói theo lượt → danh sách PhatBieu (mệnh đề) đã kiểm
           giá trị hợp lệ
Đọc từ   : class PhatBieu là bản ghi mệnh đề; tu_json() đổi JSON của mô hình thành danh sách
           PhatBieu
Mục lục (các hàm/lớp chính):
  class PhatBieu          Bản ghi một mệnh đề lâm sàng rút từ hội thoại
  tu_json()               Đổi đầu ra JSON của mô hình thành danh sách PhatBieu
  bang_ten_tu_thuc_the()  Dựng bảng cách gọi sang mã chủ thể
  id_khac_an_toan()       Chọn mã chủ thể an toàn cho người không tra được
  la_vai_nhan_vien()      Kiểm tên có phải vai nhân viên y tế
  dem_vai_nhan_vien()     Đếm mệnh đề có chủ thể là nhân viên y tế
Dùng bởi : canh_bao/phat_hien, cong_cu_lam_sang/cam_doan_thu_thuat,
           cong_cu_lam_sang/di_buong_noi_tru,
           cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot, do_luong/danh_gia_khoa,
           do_luong/do_canh_bao, do_luong/do_tang_quan_he, do_luong/duong_danh_doi … (tổng
           27 tệp)
Tên cũ   : phat_bieu.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Bản ghi phát biểu — cấu trúc trung tâm của phương pháp.

Mỗi thông tin lâm sàng rút ra từ hội thoại được ghi thành một bản ghi 11 trường.
Bệnh án CHỈ được sinh từ tập bản ghi đang `con hieu luc`.

Ba trường quan trọng nhất, mỗi trường chặn một lỗi thật:

  tinh_huong    "Nếu mai cháu vẫn đau thì…" không được ghi thành triệu chứng
                đã xảy ra. Tách khỏi do_chac_chan vì giả định KHÔNG PHẢI là
                chưa chắc về một sự thật — nó là sự thật CHƯA XẢY RA.

  quan_he       Có `dien_bien` bên cạnh `dinh_chinh`. "Hôm qua đau, hôm nay hết
                đau" là diễn biến, GIỮ CẢ HAI. Nếu chỉ có `dinh_chinh` thì hệ
                thống sẽ vứt mất câu đầu.

  bang_chung    Là DANH SÁCH lượt thoại. Cặp "Anh có dị ứng thuốc không?" / "Có."
                cần cả hai lượt mới đủ nghĩa.
"""
from dataclasses import asdict, dataclass, field
from typing import List, Optional

DO_CHAC_CHAN = ("chắc chắn", "nghi ngờ", "chưa ghi nhận")
TINH_HUONG = ("thực tế", "giả định", "kế hoạch")
QUAN_HE = ("bổ sung", "đính chính", "diễn biến", "mâu thuẫn")
TRANG_THAI = ("còn hiệu lực", "bị thay thế", "chưa giải quyết")
THOI_GIAN = ("hiện tại", "quá khứ", "chưa rõ")
NGUOI_NOI = ("bác sĩ", "bệnh nhân", "người nhà", "điều dưỡng", "người khác")

# Loại phát biểu — THÊM 11/09/2026 cho tầng "phát biểu nguyên tử".
#
#   trả lời    lời bệnh nhân / người nhà ngay SAU một lượt của nhân viên y tế
#   tự kể      lời bệnh nhân / người nhà KHÔNG có ai hỏi dẫn vào: đính chính,
#              bổ sung, diễn biến, và bẫy tầng 4 đều thuộc loại này
#   quan sát   ket qua kham, sinh hieu
#   nhận định  chan doan, ke ca muc "nghi ngo"
#   kế hoạch   chi dinh, dan do, ke ca dan do co dieu kien
#
# KHÔNG có "câu hỏi": câu hỏi không ai trả lời thì KHÔNG tạo bản ghi (xem
# `bakeoff.HUONG_DAN`), nên một giá trị "câu hỏi" sẽ không bao giờ có ví dụ —
# đúng họ lỗi "khai trong lược đồ mà không bao giờ có giá trị" đã gặp năm lần.
HANH_VI = ("trả lời", "tự kể", "quan sát", "nhận định", "kế hoạch")

# Thông tin CHI TIẾT VỀ THUỐC — THÊM 15/09/2026.
#
# Trước đó một phát biểu thuốc chỉ có `noi_dung` = tên thuốc ("amlodipin"). Nhóm
# lỗi nguy hiểm nhất về thuốc — sai liều, sai số lần, sai đường dùng, thuốc đã
# ngưng ghi thành đang dùng — không có chỗ nào để ghi, nên cũng không có cách nào
# để đo (sổ tay, Phần II, nhóm lỗi 9).
#
# `thuoc` là một từ điển hoặc None. Chỉ `ten` bắt buộc; chi tiết nào hội thoại KHÔNG
# nói thì để None — đoán liều là tự bịa ra thông tin lâm sàng.
#
# HAI DANH SÁCH ĐÓNG chỉ khai những giá trị BỘ SINH THẬT SỰ TẠO RA. Khai một giá
# trị mà không bao giờ có ví dụ ("tiêm", "đã kê chưa dùng") là họ lỗi "khai trong
# lược đồ mà không bao giờ có giá trị" đã gặp sáu lần. Muốn thêm giá trị thì thêm
# kịch bản vào bộ sinh cùng lúc.
# ĐỐI CHIẾU VỚI CHUẨN QUỐC TẾ (đọc 16/09/2026, xem docs/nguon/thuoc-va-tieng-viet.md):
#   `lieu`  GỘP hai trường của n2c2 2018: `Strength` ("500 mg") và `Dosage`
#           ("nửa gói", "hai nhát"). Không tách vì bộ sinh không sinh cả hai cùng
#           lúc; phải ghi rõ chỗ này khi so số liệu với n2c2.
#   `ngung` KHÔNG phải `Duration` của n2c2. `Duration` là độ dài đợt dùng ("trong
#           7 ngày"); `ngung` la DA NGUNG DUOC BAO LAU ("2 tuần"). Hai thu khac
#           nhau, dùng trả chéo.
#   MEDIQA-OE 2025 (y lệnh thuốc từ hội thoại khám) KHÔNG tách trường nào: mỗi y
#   lệnh chỉ có description / order_type / reason / provenance, liều và số lần
#   chìm trong văn xuôi. `provenance` của họ là số lượt thoại, giống `bang_chung`.
THUOC_KHOA = ("ten", "lieu", "so_lan", "duong_dung", "bat_dau", "ngung",
              "trang_thai_dung")
DUONG_DUNG = ("uống", "xịt", "bôi", "nhỏ")
# "được kê, chưa dùng" thêm 16/09/2026 cho y lệnh của bác sĩ ngay trong lời thoại:
# thuốc đã được kê nhưng chưa ai uống viên nào. Gộp nó vào "đang dùng" là ghi một
# việc CHƯA XẢY RA thành việc đang xảy ra — đúng nhóm lo~i số 4 của sổ tay.
TRANG_THAI_DUNG = ("đang dùng", "đã ngừng", "được kê, chưa dùng")


# ═══ class PhatBieu — Bản ghi một mệnh đề lâm sàng rút từ hội thoại ═══════════════════
# Gồm nội dung, chủ thể, người nói, phủ định, tình huống, thời gian, lượt căn cứ và câu
# trích; bản nháp chỉ sinh từ mệnh đề còn hiệu lực.
@dataclass
class PhatBieu:
    id: int
    nguoi_noi: str
    chu_the_id: int
    noi_dung: str
    bang_chung: List[int]                      # danh sách số lượt thoại
    do_chac_chan: str = "chắc chắn"
    phu_dinh: bool = False
    tinh_huong: str = "thực tế"
    thoi_gian_su_kien: str = "chưa rõ"
    moc_thoi_gian: Optional[str] = None
    doi_tuong_id: Optional[int] = None
    quan_he: Optional[str] = None
    quan_he_voi: Optional[int] = None
    trang_thai: str = "còn hiệu lực"
    # Đoạn NGUYÊN VĂN trong hội thoại làm bằng chứng, mỗi lượt một đoạn.
    #
    # Trường này nằm trong lược đồ từ ngày đầu nhưng không khâu nào điền: bộ
    # sinh không xuất, `du_lieu_trich` không đẩy, `tu_json` không đọc. Họ lỗi
    # "khai mà không điền" — và lần này là đúng cái trường mà tên dự án ("truy
    # vết bằng chứng") đưa vào. Điền từ 11/09/2026; `khoa_bang_chung` kiểm nó với
    # CHÍNH hội thoại, không với bảng phát biểu.
    trich_dan: List[str] = field(default_factory=list)
    ten_chu_the: str = ""          # chuỗi gốc mô hình viết, để trả vai người nói
    hanh_vi: str = ""              # xem HANH_VI; "" = không rõ (đầu ra cũ)
    thuoc: Optional[dict] = None   # xem THUOC_KHOA; None = không phải thông tin thuốc
    # Vết âm thanh căn cứ hai chiều (Bidirectional Audio Citation Spans)
    audio_spans: List[dict] = field(default_factory=list)  # [{ start_ms, end_ms, speaker_id, exact_quote }]

    def __post_init__(self):
        if self.thuoc is not None:
            _kiem_thuoc(self.thuoc)
        _kiem("do_chac_chan", self.do_chac_chan, DO_CHAC_CHAN)
        if self.hanh_vi:
            _kiem("hanh_vi", self.hanh_vi, HANH_VI)
        _kiem("tinh_huong", self.tinh_huong, TINH_HUONG)
        _kiem("trang_thai", self.trang_thai, TRANG_THAI)
        _kiem("thoi_gian_su_kien", self.thoi_gian_su_kien, THOI_GIAN)
        _kiem("nguoi_noi", self.nguoi_noi, NGUOI_NOI)
        if self.quan_he is not None:
            _kiem("quan_he", self.quan_he, QUAN_HE)
            if self.quan_he_voi is None:
                raise ValueError(f"quan_he={self.quan_he!r} phai kem quan_he_voi")
        if not self.bang_chung:
            raise ValueError("bang_chung khong duoc rong — moi phat bieu phai truy vet duoc")

    # ---- ba trường bắt buộc phải có giá trị: chu_the_id, do_chac_chan, bang_chung
    def du_dieu_kien_vao_benh_an(self):
        """Thiếu một trong ba trường bắt buộc thì chuyển sang mục cần xác nhận."""
        return (
            self.chu_the_id is not None
            and self.do_chac_chan in DO_CHAC_CHAN
            and bool(self.bang_chung)
            and self.trang_thai == "còn hiệu lực"
            and self.tinh_huong == "thực tế"
        )

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


# ─── _kiem() — Kiểm giá trị thuộc danh sách hợp lệ ────────────────────────────────────
# Báo lỗi ValueError nếu giá trị nằm ngoài danh sách cho phép.
def _kiem(ten, gia_tri, hop_le):
    if gia_tri not in hop_le:
        raise ValueError(f"{ten}={gia_tri!r} khong hop le; phai thuoc {hop_le}")


# ─── _kiem_thuoc() — Kiểm cấu trúc chi tiết thuốc ─────────────────────────────────────
# Phải là từ điển có tên, chỉ dùng khoá cho phép, đường dùng và trạng thái dùng nằm
# trong danh sách; hoặc None.
def _kiem_thuoc(t):
    """`thuoc` phải là từ điển, có `ten`, chỉ dùng khoá trong THUOC_KHOA, và hai
    trường đóng nằm trong danh sách — hoặc None khi hội thoại không nói."""
    if not isinstance(t, dict):
        raise ValueError(f"thuoc phai la tu dien, nhan {type(t).__name__}")
    thua = set(t) - set(THUOC_KHOA)
    if thua:
        raise ValueError(f"thuoc co khoa la: {sorted(thua)}")
    if not str(t.get("ten") or "").strip():
        raise ValueError("thuoc phai co ten")
    if t.get("duong_dung") is not None:
        _kiem("duong_dung", t["duong_dung"], DUONG_DUNG)
    if t.get("trang_thai_dung") is not None:
        _kiem("trang_thai_dung", t["trang_thai_dung"], TRANG_THAI_DUNG)


# ------------------------------------------------- câu nối từ đầu ra mô hình

# Cách gọi bệnh nhân trong hội thoại nhi khoa. Dùng cho nhánh B, là nhánh
# KHÔNG có liên kết thực thể — nó chỉ có chuỗi tự do để đối chiếu.
TEN_BENH_NHAN = ("trẻ", "bé", "cháu", "bệnh nhân", "con", "em bé", "trẻ nhỏ")

# Vai NHÂN VIÊN Y TẾ — MỘT định nghĩa duy nhất cho cả dự án.
#
# Chúng không bao giờ là `chu_the` hợp lệ của thông tin lâm sàng: câu bác sĩ
# nói là thông tin VỀ BỆNH NHÂN. `chu_the` là thông tin về ai, `nguoi_noi` là
# ai nói; gộp hai trường đó lại chính là lo~i quy gán.
#
# VÌ SAO ĐẶT Ở ĐÂY. Hàng rào này trước đó nằm ở ĐÚNG MỘT trong ba chỗ cần nó:
# `sinh_benh_an` có `NHAN_VIEN_Y_TE`, còn `phat_bieu.tu_json` và
# `sua_cuc_bo.kiem_mot_cau` thì không. Hai bảng cùng nghĩa ở hai tệp là cách
# chúng trôi nhau; đặt ở `phat_bieu` vì câu hỏi "cái gì được làm `chu_the`"
# thuộc về lược đồ, không thuộc về khâu sinh văn.
#
# GIÁ CỦA CHỖ THIẾU, đo được: khâu trích ghi `chu_the = "bac si"` cho 160/537
# phát biểu trên tập phát triển. `tu_json` cho chúng `id_khac`, rồi
# `sua_cuc_bo` kết luận "thông tin của người khác" và đổi câu sang mục TIỀN SỬ
# GIA ĐÌNH VÀ XÃ HỘI — 104 lần. Tầng bác sĩ tụt 98,6% -> 52,8%, điểm gộp tụt
# 13,7 điểm.
#
# VÌ SAO KHÔNG THƯỚC ĐO NÀO THẤY. Thước đo đầu-cuối suy chủ thể từ VĂN BẢN
# sinh ra và tên mục, không từ `chu_the_id`. Nhánh B và C giữ câu đúng mục nên
# thước đo đọc ra "bệnh nhân" và cho điểm đúng dù biểu diễn bên trong sai. Chỉ
# nhánh D phơi nó ra, vì D là nhánh duy nhất HÀNH ĐỘNG theo `chu_the_id`.
#
# Đây là luận điểm của dự án xảy ra bên trong dự án: một sai quy gán có thể
# nằm trong biểu diễn mà thước đo gộp không thấy, cho đến khi một khâu sau tin
# vào nó.
VAI_NHAN_VIEN = ("bác sĩ", "bác sỹ", "bs", "điều dưỡng", "y sĩ", "y tá")


# ═══ la_vai_nhan_vien() — Kiểm tên có phải vai nhân viên y tế ═════════════════════════
# Khớp theo chuỗi con, nên "bác sĩ Lan" hay "bs Nam" đều nhận.
def la_vai_nhan_vien(ten):
    """Tên này là vai nhân viên y tế không. Thuần tuý, để test được.

    Khớp theo CHUỖI CON có chủ ý: mô hình viết "bác sĩ Lan" hoặc "bs Nam" chứ
    không chỉ viết "bác sĩ". Đây cũng là ngữ nghĩa của `sinh_benh_an` trước
    khi gộp — đổi sang khớp chính xác sẽ làm mất những trường hợp đó.
    """
    thap = str(ten or "").strip().lower()
    return any(v in thap for v in VAI_NHAN_VIEN)


# ═══ dem_vai_nhan_vien() — Đếm mệnh đề có chủ thể là nhân viên y tế ═══════════════════
# Để đo tỉ lệ nhầm chủ thể và đưa vào báo cáo.
def dem_vai_nhan_vien(ps):
    """-> số bản ghi có `chu_the` là vai nhân viên y tế.

    Để đo TỶ LỆ chứ không để chứa: nếu chỉ chuẩn hoá âm thầm thì không ai biết
    khâu trích sai bao nhiêu. Con số này phải vào báo cáo.
    """
    return sum(1 for p in ps or [] if la_vai_nhan_vien(p.get("chu_the")))


# ═══ id_khac_an_toan() — Chọn mã chủ thể an toàn cho người không tra được ═════════════
# Tránh đè lên mã người đã có (từng làm sai mọi mệnh đề của người nhà); mã mới nằm ngoài
# bảng.
def id_khac_an_toan(id_theo_ten, mac_dinh=1):
    """Id dành cho chủ thể KHÔNG tra được trong bảng — phải không đâm vào id nào.

    LỖI ĐÃ XẢY RA, đo được 11/09/2026, và nó làm sai MỌI mệnh đề của người nhà.

    `tu_json` có `id_khac=1` trong chữ ký hàm, và KHÔNG MỘT chỗ gọi nào truyền
    giá trị khác. Trong khi `thuc_the.lien_ket` cấp id theo thứ tự xuất hiện, và
    trên hội thoại khám bệnh thì:

        0  bệnh nhân
        1  BÁC SĨ
        2  người nhà

    Nên mọi chủ thể không tra được — `chu_the = "me"` chẳng hạn — nhận id 1, tức
    là **trở thành bác sĩ**. Đo được trên ca đầu tiên của tập phát triển:

        chu_the 'me' -> id 1 -> ten_chu_the[1] = 'bac si'

    Và hậu quả ở đầu ra: mục TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI của nhánh B, C, D có
    50/50/53 câu, và **0 câu nêu tên người**. Bản tham chiếu có 22 câu, **22 câu
    nêu tên người**. Một bác sĩ đọc bản nháp đó không biết ai bị rối loạn mỡ máu.

    Tính từ bảng thay vì đặt hằng số: bảng do `thuc_the.lien_ket` sinh ra nên số
    thực thể đổi theo hội thoại, và một hằng số nào cũng sẽ đâm vào một lúc nào.
    """
    if not id_theo_ten:
        return mac_dinh
    so = [v for v in id_theo_ten.values() if isinstance(v, int)]
    return max(so) + 1 if so else mac_dinh


_ANH_XA_NGUOI_NOI = {
    "bác sĩ": "bác sĩ",
    "bác sỹ": "bác sĩ",
    "bs": "bác sĩ",
    "bac_si": "bác sĩ",
    "doctor": "bác sĩ",
    "y sĩ": "bác sĩ",
    "điều dưỡng": "điều dưỡng",
    "dieu_duong": "điều dưỡng",
    "nurse": "điều dưỡng",
    "y tá": "điều dưỡng",
    "bệnh nhân": "bệnh nhân",
    "người bệnh": "bệnh nhân",
    "benh_nhan": "bệnh nhân",
    "patient": "bệnh nhân",
    "người nhà": "người nhà",
    "nguoi_nha": "người nhà",
    "family_member": "người nhà",
    "mẹ": "người nhà",
    "bố": "người nhà",
    "ba": "người nhà",
    "má": "người nhà",
    "vợ": "người nhà",
    "chồng": "người nhà",
    "người khác": "người khác",
    "nguoi_khac": "người khác",
    "other": "người khác",
}


# ─── _chuan_hoa_nguoi_noi() — Chuẩn hoá vai người nói về 5 giá trị cho phép ───────────
# Rỗng thành bệnh nhân; vai nhân viên suy ra bác sĩ hoặc điều dưỡng; còn lại là người
# khác.
def _chuan_hoa_nguoi_noi(vai) -> str:
    raw = str(vai.value if hasattr(vai, "value") else (vai or "")).strip().lower()
    if not raw:
        return "bệnh nhân"
    if raw in NGUOI_NOI:
        return raw
    if raw in _ANH_XA_NGUOI_NOI:
        return _ANH_XA_NGUOI_NOI[raw]
    if la_vai_nhan_vien(raw):
        return "điều dưỡng" if ("điều dưỡng" in raw or "y tá" in raw) else "bác sĩ"
    return "người khác"


# ═══ tu_json() — Đổi đầu ra JSON của mô hình thành danh sách PhatBieu ═════════════════
# Người nói suy từ lượt căn cứ cuối; bản ghi sai lược đồ bị bỏ và ghi vào danh sách lỗi,
# không đoán bù.
def tu_json(ps, nguoi_noi_theo_luot=None, id_theo_ten=None, id_khac=None):
    """Đổi đầu ra JSON của mô hình thành danh sách PhatBieu đã kiểm hợp lệ.

    `nguoi_noi` không nằm trong lược đồ của mô hình — suy ra từ người nói của
    lượt bằng chứng CUỐI CÙNG. Với cặp hỏi–đáp [1, 2] thì lượt 2 là câu trả
    lời, và người trả lời mới là người phát ngôn thông tin đó.

    `id_theo_ten` ánh xạ chuỗi `chu_the` sang `chu_the_id`:
      nhánh B  bảng tra thô theo TEN_BENH_NHAN (không có liên kết thực thể)
      nhánh C  bảng đúng từ `thuc_the.lien_ket()`

    Bản ghi không đúng lược đồ bị BỎ và ghi vào `loi`, không được đoán bù —
    đoán bù là tự bịa ra thông tin lâm sàng.
    """
    nguoi_noi_theo_luot = nguoi_noi_theo_luot or {}
    if id_khac is None:
        id_khac = id_khac_an_toan(id_theo_ten)
    ra, loi = [], []
    for i, p in enumerate(ps):
        try:
            bang_chung = [int(x) for x in (p.get("luot_thoai") or p.get("bang_chung") or [])]
            if not bang_chung:
                raise ValueError("khong co luot thoai lam bang chung")
            nguoi_noi_tho = nguoi_noi_theo_luot.get(max(bang_chung), p.get("nguoi_noi", "bệnh nhân"))
            nguoi_noi = _chuan_hoa_nguoi_noi(nguoi_noi_tho)
            ten = str(p.get("chu_the", "")).strip().lower()
            # Vai nhân viên y tế không phải chủ thể của thông tin lâm sàng:
            # câu bác sĩ nói là thông tin VỀ BỆNH NHÂN. Quy về bệnh nhân thay
            # vì để nó thành "người khác" — xem chú thích ở VAI_NHAN_VIEN.
            if la_vai_nhan_vien(ten):
                chu_the_id = 0
            elif id_theo_ten is None:
                chu_the_id = 0 if ten in TEN_BENH_NHAN else id_khac
            else:
                chu_the_id = id_theo_ten.get(ten, id_khac)
            quan_he = p.get("quan_he")
            if quan_he in (None, "không", ""):
                quan_he, quan_he_voi = None, None
            else:
                quan_he_voi = p.get("quan_he_voi")
                if quan_he_voi is None:
                    raise ValueError(f"quan_he={quan_he!r} ma thieu quan_he_voi")
            ra.append(PhatBieu(
                id=i, nguoi_noi=nguoi_noi, chu_the_id=chu_the_id,
                # Gán NGAY TẠI CHỖ DỰNG BẢN GHI. Trước đây trường này được gán
                # ở `nhanh.chay_trung_gian`, sau khi `tu_json` trả về, bằng
                #
                #     zip(ps, [x for x in phat_bieu_tho if x.get("luot_thoai")])
                #
                # Phép zip đó LỆCH HÀNG khi có bản ghi vừa có `luot_thoai` vừa
                # không hợp lệ: nó bị loại khỏi `ps` nhưng vẫn còn ở danh sách
                # bên phải, nên từ đó trở đi mỗi phát biểu nhận tên chủ thể của
                # phát biểu KẾ TIẾP. Không ngoại lệ, không dấu hiệu.
                ten_chu_the=ten,
                noi_dung=str(p.get("noi_dung", "")).strip(),
                bang_chung=bang_chung,
                do_chac_chan=p.get("do_chac_chan", "chắc chắn"),
                phu_dinh=bool(p.get("phu_dinh", False)),
                tinh_huong=p.get("tinh_huong", "thực tế"),
                thoi_gian_su_kien=p.get("thoi_gian_su_kien", "chưa rõ"),
                moc_thoi_gian=p.get("moc_thoi_gian"),
                quan_he=quan_he, quan_he_voi=quan_he_voi,
                trich_dan=_doc_trich_dan(p), hanh_vi=_doc_hanh_vi(p),
                thuoc=_doc_thuoc(p)))
        except (ValueError, TypeError) as e:
            loi.append({"chi_so": i, "ly_do": str(e), "ban_ghi": p})
    return ra, loi


# ═══ bang_ten_tu_thuc_the() — Dựng bảng cách gọi sang mã chủ thể ══════════════════════
# Dùng cho nhánh C; thêm tên bệnh nhân vào chủ thể mã 0.
def bang_ten_tu_thuc_the(danh_sach_thuc_the):
    """{cach_goi_thuong: id} từ bảng thực thể — dùng cho nhánh C.

    Thêm cả TEN_BENH_NHAN vào thực thể có id 0: mô hình viết `chu_the` là
    "trẻ" hoặc "bé", còn bảng thực thể gọi nó là "bệnh nhân".
    """
    bang = {}
    for t in danh_sach_thuc_the:
        if t.loai != "người":
            continue
        for goi in [t.ten_chuan] + list(t.cach_goi):
            bang.setdefault(str(goi).strip().lower(), t.id)
    for ten in TEN_BENH_NHAN:
        bang.setdefault(ten, 0)
    return bang


# ─── _doc_trich_dan() — Đọc trường câu trích thành danh sách chuỗi ────────────────────
# Chấp nhận một chuỗi đơn, bỏ phần tử rỗng; việc kiểm câu trích có thật thuộc bước kiểm
# căn cứ.
def _doc_trich_dan(p):
    """`trich_dan` của một bản ghi mô hình -> danh sách chuỗi.

    Chấp nhận cả MỘT chuỗi (mô hình viết `"trich_dan": "..."` thay vì danh
    sách): nội dung không đổi, chỉ đổi vỏ bọc, nên đây không phải đoán bù. Phần
    tử rỗng bị bỏ. KHÔNG kiểm ở đây chuyện trích dẫn có thật trong hội thoại hay
    không — đó là việc của `khoa_bang_chung`, nơi có hội thoại.
    """
    td = p.get("trich_dan")
    if isinstance(td, str):
        td = [td]
    if not isinstance(td, (list, tuple)):
        return []
    return [str(x).strip() for x in td if str(x or "").strip()]


# ─── _doc_hanh_vi() — Đọc loại hành vi, giá trị lạ thành rỗng ─────────────────────────
# Chỉ bỏ giá trị sai chứ không bỏ cả mệnh đề.
def _doc_hanh_vi(p):
    """Giá trị ngoài `HANH_VI` -> "" (không rõ), KHÔNG bỏ cả bản ghi.

    Khác `quan_he`: một `hanh_vi` lạ không làm hỏng thông tin lâm sàng của bản
    ghi — chủ thể, nội dung, bằng chứng vẫn đúng — nên bỏ cả bản ghi vì nó là
    mất thông tin thật để đổi lấy sự gọn.
    """
    hv = str(p.get("hanh_vi") or "").strip()
    return hv if hv in HANH_VI else ""


# ─── _doc_thuoc() — Đọc chi tiết thuốc, bỏ riêng phần sai ─────────────────────────────
# Giá trị ngoài danh sách thì chi tiết đó thành None, không đoán bù; mệnh đề vẫn giữ.
def _doc_thuoc(p):
    """`thuoc` của một bản ghi mô hình -> từ điển đủ THUOC_KHOA, hoặc None.

    Cung nguyen tac voi `_doc_hanh_vi`: gia tri ngoai danh sach dong ("hít") hay
    khoá lạ thì BỎ RIÊNG chi tiết đó, KHÔNG bỏ cả bản ghi — tên thuốc, chủ thể và
    bằng chứng vẫn đúng. Nhưng KHÔNG ĐOÁN BÙ: chi tiết nào bỏ thì thành None, và
    khoá bằng chứng / bộ chấm sẽ thấy nó là thiếu.
    """
    t = p.get("thuoc")
    if not isinstance(t, dict):
        return None
    ten = str(t.get("ten") or "").strip()
    if not ten:
        return None

    def chuoi(k):
        v = t.get(k)
        return str(v).strip() or None if v is not None else None

    duong = chuoi("duong_dung")
    trang = chuoi("trang_thai_dung")
    return {"ten": ten, "lieu": chuoi("lieu"), "so_lan": chuoi("so_lan"),
            "duong_dung": duong if duong in DUONG_DUNG else None,
            "bat_dau": chuoi("bat_dau"), "ngung": chuoi("ngung"),
            "trang_thai_dung": trang if trang in TRANG_THAI_DUNG else None}
