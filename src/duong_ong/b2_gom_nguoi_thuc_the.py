# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 2 – Gom người]
Làm gì   : Gom các cách gọi khác nhau (tôi, chồng tôi, thuốc đó) về cùng một chủ thể, phân
           biệt người nói với người được nói đến.
Vào → Ra : hội thoại (các lượt nói) → danh sách ThucThe (người, thuốc, khái niệm) kèm mã chủ
           thể và các cách gọi
Đọc từ   : lien_ket() gom người và thuốc từ hội thoại; lien_ket_mo_rong() gom đủ bốn loại
           chủ thể
Mục lục (các hàm/lớp chính):
  lien_ket()          Gom hội thoại thành danh sách chủ thể
  lien_ket_mo_rong()  Gom đủ bốn loại chủ thể
  class ThucThe       Một chủ thể được gom từ hội thoại
  tach_luot()         Tách hội thoại thành các lượt nói
  _lien_ket_nguoi()   Gom người: bệnh nhân một chủ thể, mỗi vai khác một
  _lien_ket_thuoc()   Gom thuốc: tên riêng, "thuốc đó" trỏ ngược
Gọi tới  : cong_cu_lam_sang/tri_thuc_thuoc
Dùng bởi : canh_bao/bo_sot, canh_bao/phat_hien, canh_bao/toan_ca, do_luong/do_tang_quan_he,
           do_luong/duong_danh_doi, duong_ong/b1_ep_dau_ra_json,
           duong_ong/b2_bu_chu_ngu_tinh_luoc, duong_ong/b3_cap_nhat_trang_thai … (tổng 12
           tệp)
Tên cũ   : thuc_the.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Bảng thực thể và liên kết cách gọi.

Hội thoại nhắc cùng một người bằng "tôi", "chồng tôi", "bệnh nhân"; cùng một
thuốc bằng tên đầy đủ rồi "thuốc đó". Nếu `chu_the` là chuỗi tự do thì một
người sẽ thành nhiều chủ thể, và bảng cập nhật trạng thái mất hết ý nghĩa:
không thể biết "đính chính" ai đính chính ai.

Hai chiều lỗi, cả hai đều phải đo:

  bỏ sót liên kết   "thuốc A" và "thuốc đó" thành HAI thực thể
  gộp nhầm          "thuốc A" và "thuốc B" thành MỘT thực thể

Chiều thứ hai nguy hiểm hơn: nó trộn thông tin của hai đối tượng khác nhau,
đúng cái lỗi dự án đang muốn chặn. Nên luật ở đây chỉ gộp khi có CĂN CỨ
(đại từ chỉ định trỏ ngược, hoặc cách gọi trùng tên chuẩn), không gộp theo
độ giống nhau.

CHƯA làm: liên kết `xét nghiệm` và `bệnh`. Hai loại đó cần từ điển thuật ngữ
mà dự án chưa có. Khai báo trong LOAI để kiểu dữ liệu sẵn sàng, nhưng
`lien_ket()` chưa sinh ra chúng — nói rõ còn hơn giả vờ làm được.
"""
import re
from dataclasses import dataclass, field
from typing import List

LOAI = ("người", "thuốc", "xét nghiệm", "bệnh")

VAI_NOI = ("bác sĩ", "bệnh nhân", "người nhà", "điều dưỡng", "người khác")

# Từ chỉ quan hệ. "<quan hệ> tôi" trỏ tới một người KHÁC người nói.
QUAN_HE = ("chồng", "vợ", "con trai", "con gái", "con", "cháu", "mẹ", "bố",
           "ba", "má", "cha", "anh trai", "chị gái", "anh", "chị", "em",
           "ông", "bà", "bé")
_QH = "|".join(sorted(QUAN_HE, key=len, reverse=True))

# "<quan hệ> tôi/tui/em/mình" — cụm sở hữu, trỏ tới NGƯỜI KHÁC.
#
# "tui" thêm 24/09/2026: cách tự xưng Nam Bộ. Trước đó "Mẹ tui bị tiểu đường" không
# sinh thực thể "mẹ tui", nên tiền sử gia đình rơi vào người nói. `khoa_bang_chung`
# đã coi "tui" là từ xưng từ trước (TU_TU_XUNG_RO, _SO_HUU_DUOI) — hai tệp của cùng
# đường ống nói hai điều. ViDia2Std (tập dev): "tui -> tôi" xuất hiện 68 lần. Dữ liệu
# thế hệ 8/8b không có chữ "tui" nào, nên số đã báo cáo không đổi. Giới hạn: bản chép
# am mat dau co the bien "tụi" (tui no) thanh "tui".
QH_SO_HUU = re.compile(rf"(?i)\b({_QH})\s+(tôi|tui|em|mình)\b")

# Đại từ ngôi thứ nhất ĐỨNG MỘT MÌNH — trỏ tới chính người nói.
NGOI_MOT = re.compile(r"(?i)\b(tôi|tui|em|cháu|mình)\b")

# Đại từ chỉ định cho thuốc — trỏ NGƯỢC lại thuốc vừa nhắc.
THUOC_TRO_NGUOC = re.compile(r"(?i)\b(thuốc|loại)\s+(đó|này|ấy|kia|nớ)\b")

# Tên thuốc: sau chữ "thuốc" là một từ viết hoa, hoặc một tên trong từ điển.
THUOC_CO_TEN = re.compile(r"(?:thuốc|uống)\s+([A-ZĐÀ-Ỹ][\wÀ-ỹ]*)")
TU_DIEN_THUOC = (
    "penicillin", "amoxicillin", "augmentin", "paracetamol", "ibuprofen",
    "cefixim", "cephalexin", "azithromycin", "erythromycin", "prednisolon",
    "salbutamol", "ventolin", "efferalgan", "hapacol", "aspirin", "insulin",
    "metformin", "amlodipin", "atorvastatin", "omeprazol",
)
# 25/11/2026: thêm mọi tên trong data/tri_thuc_thuoc.json (158 hoạt chất, gồm thuốc của 400 khuôn
# mới). Giữ tên cũ ở đầu tuple để thứ tự khớp cũ không đổi.
from src.cong_cu_lam_sang import tri_thuc_thuoc as _ttt  # noqa: E402
TU_DIEN_THUOC = TU_DIEN_THUOC + tuple(t for t in _ttt.tat_ca_ten() if t not in TU_DIEN_THUOC)
THUOC_TU_DIEN = re.compile(r"(?i)\b(" + "|".join(re.escape(t) for t in TU_DIEN_THUOC) + r")\b")

# Dấu hiệu câu nói của người nhà đang kể về TIỀN SỬ GIA ĐÌNH (người thứ ba ở nhà),
# KHÔNG phải kể về bệnh nhân đang khám (và lỗi "bố em" bị gộp nhầm vào bệnh nhân).
DAU_TIEN_SU_GIA_DINH = re.compile(
    r"(?i)\b(cũng bị|ở nhà|từ nhỏ|hồi nhỏ|ngày xưa|hồi xưa|đã mất|qua đời|"
    r"di truyền|có liên quan|tiền sử gia đình|bên nội|bên ngoại)\b"
)
_QH_NAM_LON = ("bố", "ba", "cha", "chồng", "ông", "anh trai", "anh")
_QH_NU_LON = ("mẹ", "má", "vợ", "bà", "chị gái", "chị")
_QH_BAC_TREN = ("bố", "ba", "cha", "mẹ", "má", "ông", "bà")
_GOI_BN_NU = re.compile(r"(?i)\b(cô|chị|bà)\b")
_GOI_BN_NAM = re.compile(r"(?i)\b(chú|ông|anh)\b")
_GOI_BN_TRE = re.compile(r"(?i)\b(cháu|bé|con|em bé)\b")

# Từ điển đồng nghĩa bệnh / triệu chứng và xét nghiệm khi bật `lien_ket_benh_xn=True`
NHOM_DONG_NGHIA_BENH = {
    "đau thượng vị": ("đau thượng vị", "đau dạ dày", "đau bao tử", "xót ruột", "đau vùng thượng vị"),
    "hen phế quản": ("hen phế quản", "hen suyễn", "bệnh hen", "suyễn"),
    "tăng huyết áp": ("tăng huyết áp", "cao huyết áp", "huyết áp cao"),
    "đái tháo đường": ("đái tháo đường", "tiểu đường", "đường huyết cao"),
    "viêm phổi": ("viêm phổi", "viêm phế quản phổi"),
    "viêm mũi dị ứng": ("viêm mũi dị ứng", "dị ứng thời tiết"),
}
NHOM_DONG_NGHIA_XN = {
    "xét nghiệm máu": ("xét nghiệm máu", "công thức máu", "lấy máu xét nghiệm"),
    "chụp x-quang": ("chụp x-quang", "chụp phim", "x-quang ngực", "chụp phổi"),
    "siêu âm bụng": ("siêu âm bụng", "siêu âm ổ bụng"),
    "điện tâm đồ": ("điện tâm đồ", "đo điện tim", "ecg"),
}


# ═══ class ThucThe — Một chủ thể được gom từ hội thoại ════════════════════════════════
# Có mã, loại (người, thuốc, bệnh, xét nghiệm), tên chuẩn, các cách gọi và lượt nói nhắc
# tới.
@dataclass
class ThucThe:
    id: int
    loai: str
    ten_chuan: str
    cach_goi: List[str] = field(default_factory=list)
    luot_thoai: List[int] = field(default_factory=list)

    def them(self, goi, luot):
        if goi not in self.cach_goi:
            self.cach_goi.append(goi)
        if luot not in self.luot_thoai:
            self.luot_thoai.append(luot)


# ═══ tach_luot() — Tách hội thoại thành các lượt nói ══════════════════════════════════
# Trả về danh sách (số lượt, vai người nói hoặc None, nội dung).
def tach_luot(hoi_thoai):
    """-> [(so_luot, vai_nguoi_noi_hoac_None, noi_dung)]"""
    ra = []
    for i, dong in enumerate(d for d in hoi_thoai.split("\n") if d.strip()):
        dong = re.sub(r"^\s*\d+\.\s*", "", dong.strip())
        m = re.match(r"^([^:]{1,20}):\s*(.*)$", dong)
        if m:
            vai = m.group(1).strip().lower()
            ra.append((i + 1, vai if vai in VAI_NOI else vai, m.group(2)))
        else:
            ra.append((i + 1, None, dong))
    return ra


# ─── _lien_ket_nguoi() — Gom người: bệnh nhân một chủ thể, mỗi vai khác một ───────────
# Đại từ ngôi một đứng một mình là chính người nói; "quan hệ + tôi" của người nhà là
# bệnh nhân; hai quan hệ khác nhau thì không gộp.
def _lien_ket_nguoi(luot):
    """Một thực thể cho bệnh nhân, một cho mỗi vai người nói khác.

    Hai luật:
      - đại từ ngôi thứ nhất ĐỨNG MỘT MÌNH -> chính người nói
      - "<quan hệ> tôi" từ NGƯỜI NHÀ -> bệnh nhân, vì người nhà đến khám là
        để nói về bệnh nhân. Nhưng nếu người nhà dùng HAI cụm quan hệ khác
        nhau ("chồng tôi" và "con tôi") thì không thể cả hai cùng là bệnh
        nhân — lúc đó KHÔNG gộp, để riêng, vì gộp nhầm nguy hiểm hơn bỏ sót.
    """
    benh_nhan = ThucThe(0, "người", "bệnh nhân")
    theo_vai, ket_qua = {}, [benh_nhan]

    def cua_vai(vai):
        if vai == "bệnh nhân":
            return benh_nhan
        if vai not in theo_vai:
            t = ThucThe(len(ket_qua), "người", vai or "không rõ")
            theo_vai[vai] = t
            ket_qua.append(t)
        return theo_vai[vai]

    # Vòng 1: đếm các cụm "<quan hệ> tôi" của người nhà
    cum_quan_he = {}
    cum_la_gia_dinh = set()
    loi_bac_si = " ".join(v for _, vai_n, v in luot if vai_n in ("bác sĩ", "điều dưỡng"))
    bn_la_nu = bool(_GOI_BN_NU.search(loi_bac_si)) and not bool(_GOI_BN_NAM.search(loi_bac_si))
    bn_la_nam = bool(_GOI_BN_NAM.search(loi_bac_si)) and not bool(_GOI_BN_NU.search(loi_bac_si))
    bn_la_tre = bool(_GOI_BN_TRE.search(loi_bac_si))

    for so, vai, van in luot:
        if vai != "người nhà":
            continue
        for m in QH_SO_HUU.finditer(van):
            cum_thap = m.group(0).lower()
            qh_goc = m.group(1).lower()
            cum_quan_he.setdefault(cum_thap, []).append(so)
            # Kiểm tra xem cụm "<quan hệ> tôi/em" có phải dạng kể TIỀN SỬ GIA ĐÌNH
            # (vd: "Bố em bị hen từ nhỏ, không biết có liên quan không") hoặc xung đột
            # giới tính / thế hệ với bệnh nhân đang khám hay không.
            if DAU_TIEN_SU_GIA_DINH.search(van):
                cum_la_gia_dinh.add(cum_thap)
            elif bn_la_nu and qh_goc in _QH_NAM_LON:
                cum_la_gia_dinh.add(cum_thap)
            elif bn_la_nam and qh_goc in _QH_NU_LON:
                cum_la_gia_dinh.add(cum_thap)
            elif bn_la_tre and qh_goc in _QH_BAC_TREN:
                cum_la_gia_dinh.add(cum_thap)
    gop_ve_benh_nhan = (len(cum_quan_he) == 1) and not cum_la_gia_dinh

    theo_ten_rieng = {}
    for so, vai, van in luot:
        if vai:
            cua_vai(vai).them(vai, so)

        con_lai = van
        for m in QH_SO_HUU.finditer(van):
            cum = m.group(0)
            cum_thap = cum.lower()
            # Bác sĩ nói "...của chị tôi mới ghi" -> "chị" là người bệnh, "tôi" là bác sĩ, không phải quan hệ "chị tôi"
            if vai in ("bác sĩ", "điều dưỡng"):
                continue
            if vai == "người nhà" and gop_ve_benh_nhan and cum_thap not in cum_la_gia_dinh:
                benh_nhan.them(cum_thap, so)
            else:
                if cum_thap in theo_ten_rieng:
                    t = theo_ten_rieng[cum_thap]
                else:
                    t = ThucThe(len(ket_qua), "người", cum_thap)
                    theo_ten_rieng[cum_thap] = t
                    ket_qua.append(t)
                t.them(cum_thap, so)
            # Bỏ cụm khỏi văn bản trước khi tìm đại từ đứng một mình, nếu
            # không thì chữ "tôi" trong "chồng tôi" sẽ bị tính là người nói.
            con_lai = con_lai.replace(cum, " ")

        if NGOI_MOT.search(con_lai):
            goi = NGOI_MOT.search(con_lai).group(1).lower()
            (benh_nhan if vai == "bệnh nhân" else cua_vai(vai)).them(goi, so)

    return ket_qua


# ─── _lien_ket_thuoc() — Gom thuốc: tên riêng, "thuốc đó" trỏ ngược ───────────────────
# Hai tên thuốc khác nhau không bao giờ bị gộp.
def _lien_ket_thuoc(luot, bat_dau_id):
    """Tên riêng tạo thực thể mới; "thuốc đó" trỏ ngược về thuốc gần nhất.

    Hai tên khác nhau KHÔNG bao giờ bị gộp — đó là chiều lỗi nguy hiểm.
    """
    ket_qua, theo_ten, gan_nhat = [], {}, None
    for so, _vai, van in luot:
        # Trỏ ngược phải xét TRƯỚC tên riêng: "Thuốc đó" có chữ T viết hoa.
        moc = []
        for m in THUOC_TRO_NGUOC.finditer(van):
            moc.append(("tro_nguoc", m.start(), m.group(0)))
        for m in THUOC_CO_TEN.finditer(van):
            if not any(b <= m.start() < b + len(g) for _k, b, g in moc):
                moc.append(("ten", m.start(), m.group(1)))
        for m in THUOC_TU_DIEN.finditer(van):
            moc.append(("ten", m.start(), m.group(1)))
        moc.sort(key=lambda x: x[1])

        for kieu, _vi_tri, chu in moc:
            if kieu == "tro_nguoc":
                if gan_nhat is not None:
                    gan_nhat.them(chu.lower(), so)
                continue
            khoa = chu.lower()
            if khoa in theo_ten:
                t = theo_ten[khoa]
            else:
                t = ThucThe(bat_dau_id + len(ket_qua), "thuốc", chu)
                theo_ten[khoa] = t
                ket_qua.append(t)
            t.them(chu, so)
            gan_nhat = t
    return ket_qua


# ─── _lien_ket_khai_niem() — Gom bệnh hoặc xét nghiệm cùng nhóm đồng nghĩa ────────────
# Các biến thể trong một nhóm về chung một chủ thể.
def _lien_ket_khai_niem(luot, bat_dau_id, loai_thuc_the, bang_dong_nghia):
    """Lien ket cac khai niem `bệnh` hoac `xét nghiệm` cung nhom dong nghia ve mot ThucThe."""
    ket_qua, theo_chuan = [], {}
    for so, _vai, van in luot:
        van_thap = van.lower()
        for ten_chuan, cac_bien_the in bang_dong_nghia.items():
            for bt in cac_bien_the:
                if re.search(rf"(?<!\w){re.escape(bt)}(?!\w)", van_thap):
                    if ten_chuan in theo_chuan:
                        t = theo_chuan[ten_chuan]
                    else:
                        t = ThucThe(bat_dau_id + len(ket_qua), loai_thuc_the, ten_chuan)
                        theo_chuan[ten_chuan] = t
                        ket_qua.append(t)
                    t.them(bt, so)
    return ket_qua


# ═══ lien_ket() — Gom hội thoại thành danh sách chủ thể ═══════════════════════════════
# Mặc định chỉ gom người và thuốc; bật cờ để gom thêm bệnh và xét nghiệm.
def lien_ket(hoi_thoai, lien_ket_benh_xn=False):
    """-> list[ThucThe]. Xem hai chiều lỗi ở docstring đầu tệp.
    Mặc định `lien_ket_benh_xn=False` để giữ tương thích 100% với bộ đo gốc;
    bật `lien_ket_benh_xn=True` (hoặc gọi `lien_ket_mo_rong`) để gom đồng nghĩa bệnh và xét nghiệm.
    """
    luot = tach_luot(hoi_thoai)
    nguoi = _lien_ket_nguoi(luot)
    thuoc = _lien_ket_thuoc(luot, bat_dau_id=len(nguoi))
    ra = nguoi + thuoc
    if lien_ket_benh_xn:
        benh = _lien_ket_khai_niem(luot, len(ra), "bệnh", NHOM_DONG_NGHIA_BENH)
        ra = ra + benh
        xn = _lien_ket_khai_niem(luot, len(ra), "xét nghiệm", NHOM_DONG_NGHIA_XN)
        ra = ra + xn
    return ra


# ═══ lien_ket_mo_rong() — Gom đủ bốn loại chủ thể ═════════════════════════════════════
# Người, thuốc, bệnh, xét nghiệm.
def lien_ket_mo_rong(hoi_thoai):
    """Lien ket day du ca 4 loai thuc the: người, thuốc, bệnh, xét nghiệm."""
    return lien_ket(hoi_thoai, lien_ket_benh_xn=True)
