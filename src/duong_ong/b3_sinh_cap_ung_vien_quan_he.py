# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 3 – Cập nhật trạng thái]
Làm gì   : Tìm các cặp mệnh đề có thể liên quan (tự sửa, mâu thuẫn, nối tiếp theo thời gian)
           để đem đi phân xử quan hệ.
Vào → Ra : danh sách mệnh đề (+ lời thoại theo lượt) → danh sách CapUngVien kèm gợi ý quan
           hệ từ dấu hiệu bề mặt
Đọc từ   : sinh_cap() liệt kê các cặp đáng ngờ; goi_y_bang_luat() đoán quan hệ;
           ap_phan_quyet() gán quan hệ vào bản sao
Mục lục (các hàm/lớp chính):
  sinh_cap()            Liệt kê các cặp đáng ngờ để phân xử
  goi_y_bang_luat()     Đoán quan hệ của cặp từ dấu hiệu bề mặt
  ap_phan_quyet()       Gán quan hệ vào bản sao danh sách mệnh đề
  sinh_cap_trung_lap()  Tìm cặp mệnh đề trùng lặp lúc rút
  thong_ke()            Tính số liệu thống kê cho báo cáo
  class CapUngVien      Một cặp mệnh đề đáng ngờ có thể có quan hệ
  da_bi_cat()           Báo có cặp nào bị cắt bớt không
Gọi tới  : duong_ong/b1_cau_truc_menh_de
Dùng bởi : do_luong/do_tang_quan_he, duong_ong/b3_phan_xu_quan_he
Tên cũ   : ung_vien_quan_he.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Sinh cặp ứng viên quan hệ — đổi vai giữa CHƯƠNG TRÌNH và MÔ HÌNH.

PHÁT HIỆN BƯỚC NGOẶT (06/09/2026, Cửa 4).
Trên 35 hội thoại thật, mô hình đánh dấu `quan_he` ở **0/282** phát biểu. Bảng
bóc cơ chế cho con số dứt khoát: `C_khong_lien_ket` bằng ĐÚNG `B` tới từng chữ
số — luật cập nhật trạng thái không hề thay đổi gì, vì nó chạy trên trường
`quan_he` mà trường đó luôn rỗng.

Và đó KHÔNG phải vì hội thoại không có quan hệ: 21/35 hội thoại có mốc kiểu
"hôm qua… hôm nay…" — đúng dạng `dien_bien` mà dự án muốn bắt.

CHẨN ĐOÁN. Trích phát biểu là bài toán **liệt kê**; đánh dấu quan hệ là bài
toán **khởi phát** (self-initiation): mô hình phải tự nhớ rằng mình vừa ghi một
bản ghi tương tự ở đâu đó phía trước, tự quay lại đối chiếu, rồi tự quyết định
ghi thêm một trường không ai hỏi. Trên hội thoại 4 lượt do chính tay mình sinh
ra thì làm được (15/15). Trên hội thoại 10–28 lượt của người thật thì không,
vì lúc đó bản ghi tương ứng đã trôi qua từ lâu.

CÁCH SỬA. Đổi vai:

    trước:  mô hình  vừa liệt kê phát biểu  VỪA tự phát hiện quan hệ
    nay:    CHƯƠNG TRÌNH liệt kê cặp đáng ngờ (vét cạn 100% theo cấu trúc)
            MÔ HÌNH (hoặc LUẬT) chỉ trả lời một câu bốn lựa chọn trên một cặp

Đây là cùng một nguyên tắc đã dùng ở `cap_nhat.py` — *mô hình trích, chương
trình áp luật* — chỉ là đẩy thêm một bước nữa: **chương trình còn sinh cả câu
hỏi**. Mô hình không phải nhớ gì, không phải tự khởi phát gì.

Độ vét (recall) của bước liệt kê là tính chất CẤU TRÚC chứ không phải kết quả
đo được: cặp nào thỏa điều kiện cũng được liệt kê, không phụ thuộc mô hình đang
chú ý chỗ nào. Cái phải đo là độ CHÍNH XÁC của bước phân.
"""
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from src.duong_ong.b1_cau_truc_menh_de import QUAN_HE, PhatBieu

# Tỷ lệ độ dài tối thiểu giữa hai cụm nội dung. Chặn trường hợp một cụm rất
# ngắn lọt vào một cụm rất dài ("ho" nằm trong "ho gà nghi do virus").
NGUONG_DO_DAI = 0.5

# Vì sao là BAO HÀM chứ không phải tỷ lệ giao.
#
# Ban đầu dùng "tỷ lệ giao >= 0,8". Test danh sách song song làm nó hỏng thật:
#
#     "nguy cơ hỏng dụng cụ"        {nguy, cơ, hỏng, dụng, cụ}        5 tu
#     "nguy cơ phải tháo dụng cụ"   {nguy, cơ, phải, tháo, dụng, cụ}  6 tu
#     giao = {nguy, cơ, dụng, cụ} = 4 tu  ->  4/5 = 0,80  ->  LOT
#
# Nâng ngưỡng lên 0,85 chỉ là vá tạm. Chỗ khác nhau về BẢN CHẤT nằm ở chỗ:
# quan hệ thật gần như luôn là CÙNG một cụm, hoặc một cụm là bản chi tiết hơn
# của cụm kia ("đau bụng" / "đau bụng dữ dội") — tức một bên BAO HÀM bên kia.
# Còn mục liệt kê song song thì CẢ HAI bên đều có từ riêng.
#
# Nên điều kiện là: tập từ của bên này phải nằm gọn trong bên kia.


# ─── _lien_quan() — Kiểm hai mốc thời gian có liên quan nhau ──────────────────────────
# Tập từ của mốc này phải chứa mốc kia và độ dài đủ gần.
def _lien_quan(a: Optional[str], b: Optional[str]) -> bool:
    ta, tb = _tu(a), _tu(b)
    if not ta or not tb:
        return False
    if not (ta <= tb or tb <= ta):
        return False
    return min(len(ta), len(tb)) / max(len(ta), len(tb)) >= NGUONG_DO_DAI

# Số cặp tối đa mỗi hội thoại. Hội thoại dài có thể sinh tổ hợp lớn; cắt để
# chi phí không nổ theo bình phương. `da_bi_cat` báo lại khi đã cắt.
TOI_DA_MAC_DINH = 30

# Dấu hiệu đính chính — nằm trong VĂN BẢN lời thoại, không nằm trong trường nào.
# Đây là lý do `goi_y_bang_luat` cần `luot_thoai` chứ không chỉ cần bản ghi.
DAU_HIEU_DINH_CHINH = (
    "à không", "à quên", "à nhầm", "nhầm rồi", "nhầm ạ", "xin lỗi",
    "không phải", "à mà", "à sai", "nói lại", "đúng hơn là", "à mà không",
)

# Mốc chỉ MỘT THỜI ĐIỂM. Hai thời điểm khác nhau thì hai bản ghi cùng đúng —
# đó là diễn biến. Phân biệt với mốc chỉ ĐỘ DÀI ("5 ngày", "ba tuần"), nơi mà
# hai giá trị khác nhau thường là một bên ghi sai.
MOC_THOI_DIEM = (
    "hôm nay", "hôm qua", "hôm kia", "hôm trước", "hôm nọ",
    "sáng nay", "trưa nay", "chiều nay", "tối nay", "đêm qua", "tối qua",
    "sáng qua", "chiều qua", "tuần trước", "tuần này", "tháng trước",
    "tháng này", "năm ngoái", "hiện tại", "bây giờ", "lúc nãy", "khi nãy",
)


# ═══ class CapUngVien — Một cặp mệnh đề đáng ngờ có thể có quan hệ ════════════════════
# Mệnh đề a luôn xuất hiện trước b; kèm lý do và điểm.
@dataclass(frozen=True)
class CapUngVien:
    """Một cặp đáng ngờ. `a` luôn trước `b` theo thứ tự xuất hiện."""
    a: int
    b: int
    ly_do: Tuple[str, ...]
    diem: float

    def khoa(self):
        return (self.a, self.b)


# ----------------------------------------------------------------- tách từ

_KHONG_PHAI_CHU = re.compile(r"[^\w]+", re.UNICODE)


# ─── _tu() — Tách chuỗi thành tập từ chữ thường ───────────────────────────────────────
def _tu(s: Optional[str]) -> set:
    return {t for t in _KHONG_PHAI_CHU.split((s or "").lower()) if t}


# ─── _chuan_moc() — Chuẩn hoá mốc thời gian về chữ thường ─────────────────────────────
def _chuan_moc(m: Optional[str]) -> str:
    return (m or "").strip().lower()


# ------------------------------------------------------------- sinh cặp

# ─── _tin_hieu_khac() — Liệt kê trường mà hai mệnh đề khác nhau ───────────────────────
# Khác mốc, phủ định, độ chắc chắn...; rỗng nghĩa là không có gì để phân xử.
def _tin_hieu_khac(a: PhatBieu, b: PhatBieu) -> Tuple[str, ...]:
    """Những trường mà hai bản ghi KHÁC nhau. Rỗng = không có gì để phân."""
    ly_do = []
    if _chuan_moc(a.moc_thoi_gian) != _chuan_moc(b.moc_thoi_gian):
        ly_do.append("khác mốc")
    if bool(a.phu_dinh) != bool(b.phu_dinh):
        ly_do.append("khác phủ định")
    if a.do_chac_chan != b.do_chac_chan:
        ly_do.append("khác chắc chắn")
    if a.thoi_gian_su_kien != b.thoi_gian_su_kien:
        ly_do.append("khác thời điểm")
    return tuple(ly_do)


# ─── _cap_tho() — Liệt kê mọi cặp đạt điều kiện cấu trúc, chưa cắt ────────────────────
# Khác chủ thể thì không bao giờ ghép.
def _cap_tho(danh_sach: List[PhatBieu],
             luot_thoai: Optional[Dict[int, str]] = None):
    """Mọi cặp thỏa điều kiện cấu trúc, chưa cắt."""
    theo_id = {p.id: p for p in danh_sach}
    ra = []
    for i in range(len(danh_sach)):
        for j in range(i + 1, len(danh_sach)):
            a, b = danh_sach[i], danh_sach[j]
            # Khác chủ thể thì không bao giờ là quan hệ. Ghép hai chủ thể lại
            # chính là lỗi nguy hiểm nhất mà dự án đi chặn — tầng này tuyệt
            # đối không được tự tạo ra nó.
            if a.chu_the_id != b.chu_the_id:
                continue
            if not _lien_quan(a.noi_dung, b.noi_dung):
                continue
            ly_do = _tin_hieu_khac(a, b)
            if not ly_do:
                continue        # trùng lặp hoàn toàn — xem `sinh_cap_trung_lap`
            khoang_cach = abs(b.id - a.id) or 1
            diem = len(ly_do) + 1.0 / (1 + khoang_cach)
            # Cặp có dấu hiệu đính chính ngay trong lời thoại được ưu tiên giữ
            # khi phải cắt bớt. Đính chính là tình huống mà bỏ sót một cặp gây
            # hại nhất: bỏ qua nó thì bệnh án giữ lại con số người nói ĐÃ TỰ
            # NHẬN là sai. Không có vế này thì `luot_thoai` chỉ là một tham số
            # nhận vào rồi không dùng, và thứ tự cắt hoàn toàn theo khoảng cách.
            if luot_thoai:
                tam = CapUngVien(a=a.id, b=b.id, ly_do=ly_do, diem=0.0)
                van = _van_ban_bang_chung(tam, theo_id, luot_thoai)
                if any(d in van for d in DAU_HIEU_DINH_CHINH):
                    diem += 10.0
                    ly_do = ly_do + ("có dấu hiệu đính chính",)
            ra.append(CapUngVien(a=a.id, b=b.id, ly_do=ly_do, diem=diem))
    return ra


# ═══ sinh_cap() — Liệt kê các cặp đáng ngờ để phân xử ═════════════════════════════════
# Thuần cấu trúc, không gọi mô hình; xếp theo điểm và cắt ở mức tối đa.
def sinh_cap(danh_sach: List[PhatBieu], luot_thoai: Optional[Dict[int, str]] = None,
             toi_da: int = TOI_DA_MAC_DINH) -> List[CapUngVien]:
    """Liệt kê cặp đáng ngờ. Thuần túy, không gọi mô hình.

    `luot_thoai` chỉ ảnh hưởng THỨ TỰ khi phải cắt bớt, không ảnh hưởng cặp nào
    được coi là ứng viên. Độ vét của bước liệt kê vẫn là tính chất cấu trúc.
    """
    ra = _cap_tho(danh_sach, luot_thoai)
    ra.sort(key=lambda c: (-c.diem, c.a, c.b))
    return ra[:toi_da]


# ═══ da_bi_cat() — Báo có cặp nào bị cắt bớt không ════════════════════════════════════
# Số cặp bị bỏ là nguồn bỏ sót nên phải vào báo cáo.
def da_bi_cat(danh_sach: List[PhatBieu], toi_da: int = TOI_DA_MAC_DINH) -> bool:
    """Có cặp nào bị cắt không. Báo ra chứ không im lặng — số cặp bị bỏ là một
    nguồn bỏ sót, phải vào báo cáo."""
    return len(_cap_tho(danh_sach)) > toi_da


# ═══ sinh_cap_trung_lap() — Tìm cặp mệnh đề trùng lặp lúc rút ═════════════════════════
# Giống hệt và không khác trường nào; xử lý bằng gộp, không coi là quan hệ.
def sinh_cap_trung_lap(danh_sach: List[PhatBieu]) -> List[CapUngVien]:
    """Hai bản ghi giống hệt VÀ không trường nào khác.

    Đây không phải quan hệ — đó là trùng lặp lúc trích. Trả về riêng vì cách
    xử lý khác hẳn: quan hệ thì phân, trùng lặp thì gộp.
    """
    ra = []
    for i in range(len(danh_sach)):
        for j in range(i + 1, len(danh_sach)):
            a, b = danh_sach[i], danh_sach[j]
            if a.chu_the_id != b.chu_the_id:
                continue
            if _tu(a.noi_dung) != _tu(b.noi_dung) or not _tu(a.noi_dung):
                continue
            if _tin_hieu_khac(a, b):
                continue
            ra.append(CapUngVien(a=a.id, b=b.id, ly_do=("trùng lặp",), diem=0.0))
    return ra


# ------------------------------------------------- gợi ý bằng luật (không mô hình)

# ─── _van_ban_bang_chung() — Ghép lời thoại căn cứ của cả cặp ─────────────────────────
# Hợp các lượt căn cứ của hai mệnh đề, đưa về chữ thường.
def _van_ban_bang_chung(cap: CapUngVien, theo_id: Dict[int, PhatBieu],
                        luot_thoai: Dict[int, str]) -> str:
    luot = set()
    for i in (cap.a, cap.b):
        p = theo_id.get(i)
        if p:
            luot.update(p.bang_chung)
    return " ".join(luot_thoai.get(l, "") for l in sorted(luot)).lower()


# ═══ goi_y_bang_luat() — Đoán quan hệ của cặp từ dấu hiệu bề mặt ══════════════════════
# Trả None khi không chắc; dùng làm đường lùi không GPU và đối chứng cho mô hình.
def goi_y_bang_luat(cap: CapUngVien, danh_sach: List[PhatBieu],
                    luot_thoai: Dict[int, str]) -> Optional[str]:
    """Đoán quan hệ từ dấu hiệu bề mặt. Trả `None` khi không chắc.

    Hai vai:
      1. Đường lui khi không có GPU — cả cơ chế lõi vẫn chạy được.
      2. Đối chứng cho bước phân bằng mô hình. Mô hình không hơn luật này thì
         không cần mô hình ở bước này.

    KHÔNG được đoán bừa. Không có dấu hiệu thì trả `None` để mô hình phân —
    đoán bừa ở đây sẽ sinh ra quan hệ giả, và quan hệ giả làm luật cập nhật
    vụt mất thông tin đúng.
    """
    theo_id = {p.id: p for p in danh_sach}
    van_ban = _van_ban_bang_chung(cap, theo_id, luot_thoai or {})
    a, b = theo_id.get(cap.a), theo_id.get(cap.b)
    if a is None or b is None:
        return None

    # 1. Dấu hiệu đính chính nằm trong lời nói. Ưu tiên cao nhất: người nói
    #    đã tự tuyên bố là mình nói sai.
    if any(d in van_ban for d in DAU_HIEU_DINH_CHINH):
        return "đính chính"

    # 2. Hai MỐC THỜI ĐIỂM khác nhau => cả hai cùng đúng => diễn biến.
    #    Đây là chỗ dễ sai nhất của cả dự án, nên nó là một nhánh riêng.
    ma, mb = _chuan_moc(a.moc_thoi_gian), _chuan_moc(b.moc_thoi_gian)
    if ma and mb and ma != mb:
        if _la_thoi_diem(ma) and _la_thoi_diem(mb):
            return "diễn biến"

    return None


# ─── _la_thoi_diem() — Kiểm mốc có chứa từ chỉ thời điểm ──────────────────────────────
def _la_thoi_diem(moc: str) -> bool:
    return any(t in moc for t in MOC_THOI_DIEM)


# ------------------------------------------------------------- áp phán quyết

# ═══ ap_phan_quyet() — Gán quan hệ vào bản sao danh sách mệnh đề ══════════════════════
# Giá trị phải hợp lệ, mỗi mệnh đề nhận tối đa một quan hệ, không tạo vòng; không sửa
# bản gốc.
def ap_phan_quyet(danh_sach: List[PhatBieu],
                  phan_quyet: Dict[Tuple[int, int], Optional[str]]) -> List[PhatBieu]:
    """Gán `quan_he`/`quan_he_voi` vào bản SAO. Không sửa bản gốc.

    Ba ràng buộc, mỗi ràng buộc chặn một cách làm vỡ `cap_nhat.ap_luat`:
      - giá trị phải thuộc `QUAN_HE`, không thì bỏ (mô hình trả rác)
      - mỗi bản ghi nhận tối đa MỘT quan hệ (`quan_he_voi` là một số)
      - không tạo vòng: a->b rồi b->a sẽ làm luật cập nhật quanh mãi
    """
    ra = [PhatBieu(**p.to_dict()) for p in danh_sach]
    theo_id = {p.id: p for p in ra}
    cha: Dict[int, int] = {}

    for (a, b) in sorted(k for k in phan_quyet if k is not None):
        quan_he = phan_quyet[(a, b)]
        if quan_he not in QUAN_HE:
            continue
        if a not in theo_id or b not in theo_id or a == b:
            continue
        if b in cha:
            continue                       # bản ghi đã nhận một quan hệ rồi
        if _den_duoc(cha, a, b):
            continue                       # thêm cạnh này sẽ tạo vòng
        cha[b] = a
        theo_id[b].quan_he = quan_he
        theo_id[b].quan_he_voi = a
    return ra


# ─── _den_duoc() — Kiểm đi ngược theo cha có tới được một nút không ───────────────────
# Dùng để chặn vòng quan hệ.
def _den_duoc(cha: Dict[int, int], tu: int, den: int) -> bool:
    """Đi ngược theo `cha` từ `tu`, có gặp `den` không."""
    da_qua = set()
    hien = tu
    while hien is not None and hien not in da_qua:
        if hien == den:
            return True
        da_qua.add(hien)
        hien = cha.get(hien)
    return False


# ------------------------------------------------------------------ thống kê

# ═══ thong_ke() — Tính số liệu thống kê cho báo cáo ═══════════════════════════════════
# Số mệnh đề, số cặp, có bị cắt không và gợi ý của luật.
def thong_ke(danh_sach: List[PhatBieu], luot_thoai: Optional[Dict[int, str]] = None,
             toi_da: int = TOI_DA_MAC_DINH) -> dict:
    """Số liệu cho báo cáo — mỗi con số trong báo cáo phải sinh từ đây."""
    cap = sinh_cap(danh_sach, luot_thoai, toi_da)
    goi_y = [goi_y_bang_luat(c, danh_sach, luot_thoai or {}) for c in cap]
    return {
        "so_phat_bieu": len(danh_sach),
        "so_cap": len(cap),
        "bi_cat": da_bi_cat(danh_sach, toi_da),
        "so_cap_truoc_khi_cat": len(_cap_tho(danh_sach)),
        "so_trung_lap": len(sinh_cap_trung_lap(danh_sach)),
        "luat_quyet_duoc": sum(1 for g in goi_y if g is not None),
        "luat_dinh_chinh": sum(1 for g in goi_y if g == "đính chính"),
        "luat_dien_bien": sum(1 for g in goi_y if g == "diễn biến"),
    }
