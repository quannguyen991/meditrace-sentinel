# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 5 – Xếp chỗ]
Làm gì   : Chấm rủi ro lâm sàng từng mệnh đề và quyết định đưa vào thân bản nháp, mục CẦN
           XÁC NHẬN kèm lý do, hay loại (vẫn lưu vết).
Vào → Ra : danh sách mệnh đề + kết quả kiểm căn cứ + thông tin bệnh nhân → danh sách DanhGia
           (điểm, nhóm, lý do) và chỗ xếp
Đọc từ   : cham() chấm từng mệnh đề; dua_sang_xac_nhan() chuyển mệnh đề có cảnh báo sang CẦN
           XÁC NHẬN
Mục lục (các hàm/lớp chính):
  cham()                        Chấm điểm rủi ro lâm sàng cho từng mệnh đề
  thu_tu_duyet()                Xếp thứ tự ưu tiên để bác sĩ duyệt
  dua_sang_xac_nhan()           Chuyển mệnh đề có cảnh báo sang mục CẦN XÁC NHẬN
  dem_nhom()                    Đếm số mệnh đề theo từng nhóm rủi ro
  loai_thong_tin()              Xác định loại thông tin của mệnh đề
  phan_tich_co_dia_benh_nhan()  Tính hệ số rủi ro theo cơ địa bệnh nhân
  class DanhGia                 Kết quả chấm rủi ro một mệnh đề
Gọi tới  : cong_cu_lam_sang/tri_thuc_thuoc, duong_ong/b1_cau_truc_menh_de,
           duong_ong/b4_kiem_can_cu, duong_ong/b5_viet_ban_nhap, he_thong/ep_kieu_dau_vao
Dùng bởi : canh_bao/gop, cong_cu_lam_sang/tien_kiem_bhyt_va_khoi_phuc_bo_sot,
           do_luong/cham_he_thong, do_luong/do_canh_bao, do_luong/kiem_thu_dot_bien,
           do_luong/quet_an_toan_duoc_ly_v2, duong_ong/b6_goi_y_hoi_lai,
           duong_ong/chay_duong_ong … (tổng 9 tệp)
Tên cũ   : cong_rui_ro.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Tầng 5 — CỔNG RỦI RO (Nâng cấp chuyên sâu lâm sàng).

Tích hợp:
1. Danh mục thuốc khoảng điều trị hẹp (Narrow Therapeutic Index - NTI).
2. Mô hình tích lũy đa yếu tố nhạy cảm (Synergistic Clinical Model).
3. Phân tầng độ nặng suy thận (theo eGFR/CKD stage) và giai đoạn thai kỳ.
4. Giải trình lâm sàng (Clinical Explainability / XAI) phục vụ duyệt hồ sơ.
"""
from dataclasses import asdict, dataclass, field
import math
from typing import Any, Dict, List, Optional, Tuple

# Mức nghiêm trọng theo LOẠI thông tin (0.0 -> 1.0)
MUC_NGHIEM_TRONG = {
    "di_ung": 1.0,        # Sốc phản vệ, hội chứng Stevens-Johnson
    "thuoc_nti": 1.0,     # Thuốc khoảng điều trị hẹp (Narrow Therapeutic Index)
    "thuoc": 0.9,         # Thuốc điều trị thông thường
    "chan_doan": 0.8,     # Chẩn đoán bệnh lý
    "thoi_gian": 0.6,     # Mốc khởi phát, quan hệ trước/sau
    "khac": 0.3,          # Triệu chứng phụ, thông tin hành chính
}

# Danh mục hoạt chất khoảng điều trị hẹp & thuốc cảnh báo cao (High-Alert Medications)
# 25/11/2026: đọc từ MỘT nguồn (data/tri_thuc_thuoc.json, chưa duyệt).
from src.cong_cu_lam_sang import tri_thuc_thuoc as _ttt
THUOC_KHOANG_DIEU_TRI_HEP = _ttt.ten_nti()

# Độ thiếu căn cứ từ khóa bằng chứng (0.0 -> 1.0)
DO_THIEU = {
    "mau_thuan": 1.0,
    "chu_the_nguoi_khac": 0.75,
    "chu_the_chua_ro": 0.65,
    "phu_dinh_vuot_muc": 0.6,
    "chi_tiet_thuoc_khong_thay": 0.65,
    "duong_dung_khong_thay": 0.55,
    "chu_the_suy_tu_nguoi_noi": 0.5,
    "noi_dung_khong_khop": 0.5,
    "phuong_ngu_can_hoi": 0.5,
    "co_tu_phu_dinh": 0.5,
    "moc_khong_thay": 0.5,
    "khong_trich_dan": 0.4,
    "trich_lech_luot": 0.3,
}

NGUONG_CAO = 0.5
BI_CHAN = "bị chặn"
NGUY_CO_CAO = "nguy cơ cao"
RUI_RO_THAP = "rủi ro thấp"
DA_KIEM_CHUNG = "đã kiểm chứng"

CHINH_SACH = "C-2026-09-22"
LOAI_XAC_NHAN_KHI_CANH_BAO = ("di_ung", "thuoc", "thuoc_nti")


# ═══ class ChiTietRuiRoBenhNhan — Kết quả phân tích rủi ro nền của bệnh nhân ══════════
# Gồm hệ số tổng, các yếu tố rủi ro và cảnh báo được lý giải.
@dataclass
class ChiTietRuiRoBenhNhan:
    he_so_tong: float
    cac_yeu_to: List[str]
    canh_bao_duoc_ly: List[str]


# ═══ class DanhGia — Kết quả chấm rủi ro một mệnh đề ══════════════════════════════════
# Có loại thông tin, độ nghiêm trọng, độ thiếu, điểm, nhóm và lý do.
@dataclass
class DanhGia:
    id: int
    loai: str
    nghiem_trong: float
    thieu: float
    diem_goc: float
    diem: float
    nhom: str
    ly_do: List[str] = field(default_factory=list)
    he_so_bn: float = 1.0
    yeu_to_bn: List[str] = field(default_factory=list)
    canh_bao_duoc_ly: List[str] = field(default_factory=list)
    giai_trinh: str = ""

    def to_dict(self):
        return asdict(self)


# ═══ loai_thong_tin() — Xác định loại thông tin của mệnh đề ═══════════════════════════
# Ví dụ dị ứng, thuốc; phát hiện sớm thuốc có khoảng điều trị hẹp.
def loai_thong_tin(p) -> str:
    """Xác định loại thông tin và phát hiện sớm thuốc khoảng điều trị hẹp."""
    from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an
    d = p.to_dict() if hasattr(p, "to_dict") else dict(p)
    d = dict(d, trang_thai="còn hiệu lực")
    noi_dung = str(d.get("noi_dung", "")).lower()

    if "dị ứng" in noi_dung:
        return "di_ung"

    muc, _ = sinh_benh_an._muc_cho(d, 0)
    if muc == "DỊ ỨNG":
        return "di_ung"

    # Kiểm tra thuốc khoảng điều trị hẹp (kể cả khi chu_the_id != 0 nhưng có trường `thuoc`)
    if muc == "THUỐC ĐANG DÙNG" or d.get("thuoc") or "thuốc" in noi_dung:
        ten_thuoc = str((d.get("thuoc") or {}).get("ten", "") if isinstance(d.get("thuoc"), dict) else "").lower()
        for t in THUOC_KHOANG_DIEU_TRI_HEP:
            if t in noi_dung or (ten_thuoc and t in ten_thuoc):
                return "thuoc_nti"
        return "thuoc"

    from src.duong_ong import b1_cau_truc_menh_de as _pb
    if muc == "CHẨN ĐOÁN" or (
        d.get("hanh_vi") == "nhận định" and _pb.la_vai_nhan_vien(str(d.get("nguoi_noi") or ""))
    ):
        return "chan_doan"

    if d.get("moc_thoi_gian") or d.get("quan_he") in ("đính chính", "diễn biến", "mâu thuẫn"):
        return "thoi_gian"

    return "khac"


# ═══ phan_tich_co_dia_benh_nhan() — Tính hệ số rủi ro theo cơ địa bệnh nhân ═══════════
# Nhiều yếu tố cộng dồn phi tuyến; giá trị rác coi như thiếu, không gây lỗi.
def phan_tich_co_dia_benh_nhan(bn: Optional[Dict[str, Any]]) -> ChiTietRuiRoBenhNhan:
    """Mô hình tích lũy đa yếu tố (Synergistic Saturation Model).
    
    Nếu bệnh nhân đồng thời có nhiều yếu tố rủi ro, hệ số không cộng dồn tuyến tính
    mà tích lũy theo công thức phi tuyến: H = 1.0 + Sum(h_i) * giam_tru_bien_thien.
    """
    if not bn or not isinstance(bn, dict):
        return ChiTietRuiRoBenhNhan(1.0, [], [])
    # Giá trị JSON có thể là chuỗi ("25") hoặc rác: ép kiểu an toàn, rác = thiếu (không TypeError)
    from src.he_thong.ep_kieu_dau_vao import chuan_hoa_thong_tin_benh_nhan
    bn = chuan_hoa_thong_tin_benh_nhan(bn) or {}

    yeu_to = []
    canh_bao_duoc_ly = []
    delta_he_so = []

    # 1. Thai kỳ & Cho con bú (Phân hóa theo tam cá nguyệt nếu có)
    if bn.get("thai_ky") or bn.get("mang_thai"):
        tuan_thai = bn.get("tuan_thai")
        if tuan_thai and tuan_thai <= 12:
            delta_he_so.append(0.6)
            yeu_to.append(f"Thai kỳ 3 tháng đầu ({tuan_thai} tuần) — Nguy cơ quái thai tối đa")
        else:
            delta_he_so.append(0.5)
            yeu_to.append("Phụ nữ mang thai")
        canh_bao_duoc_ly.append("Chống chỉ định tuyệt đối nhóm thuốc Category X/D")

    if bn.get("cho_con_bu"):
        delta_he_so.append(0.3)
        yeu_to.append("Phụ nữ đang cho con bú")
        canh_bao_duoc_ly.append("Cần rà soát bài tiết qua sữa mẹ")

    # 2. Lứa tuổi: Trẻ sơ sinh (<6 tháng), nhi khoa, cao tuổi (>=65, >=80)
    thang_tuoi = bn.get("thang_tuoi")
    tuoi = bn.get("tuoi")
    if thang_tuoi is not None and thang_tuoi <= 6:
        delta_he_so.append(0.6)
        yeu_to.append(f"Trẻ sơ sinh ({thang_tuoi} tháng) — Suy giảm gắn kết protein huyết tương & lọc cầu thận")
    elif tuoi is not None:
        if tuoi >= 80:
            delta_he_so.append(0.4)
            yeu_to.append(f"Người rất cao tuổi ({tuoi} tuổi) — Suy giảm chức năng đa cơ quan")
        elif tuoi >= 65:
            delta_he_so.append(0.25)
            yeu_to.append(f"Người cao tuổi ({tuoi} tuổi)")

    # 3. Chức năng thận (eGFR hoặc phân độ CKD)
    egfr = bn.get("egfr")
    benh_nen: List[str] = []
    for k_bn in ("benh_nen", "tien_su_benh"):
        raw_bn = bn.get(k_bn)
        if isinstance(raw_bn, str):
            benh_nen.append(raw_bn.lower())
        elif isinstance(raw_bn, (list, tuple, set)):
            benh_nen.extend(str(b).lower() for b in raw_bn if b is not None)
    if egfr is not None:
        if egfr < 15:
            delta_he_so.append(0.6)
            yeu_to.append(f"Suy thận giai đoạn cuối (eGFR={egfr} ml/phút)")
            canh_bao_duoc_ly.append("Giảm độ thanh thải thận nghiêm trọng; bắt buộc hiệu chỉnh liều")
        elif egfr < 30:
            delta_he_so.append(0.5)
            yeu_to.append(f"Suy thận nặng độ 4 (eGFR={egfr} ml/phút)")
        elif egfr < 60:
            delta_he_so.append(0.3)
            yeu_to.append(f"Suy thận vừa độ 3 (eGFR={egfr} ml/phút)")
    elif any("suy thận" in b or "ckd" in b for b in benh_nen):
        delta_he_so.append(0.4)
        yeu_to.append("Bệnh thận mạn tính (chưa rõ eGFR)")

    # 4. Chức năng gan
    if any("suy gan" in b or "xơ gan" in b for b in benh_nen):
        delta_he_so.append(0.35)
        yeu_to.append("Bệnh lý xơ gan/suy giảm chức năng gan")
        canh_bao_duoc_ly.append("Giảm độ thanh thải chuyển hóa qua gan pha 1 và enzym CYP450")

    # 5. Đa thuốc (Polypharmacy: dùng từ 5 thuốc trở lên)
    so_thuoc = bn.get("so_thuoc_dang_dung") or 0
    if so_thuoc >= 5:
        delta_he_so.append(0.2)
        yeu_to.append(f"Hội chứng đa thuốc ({so_thuoc} thuốc đồng thời)")

    if not delta_he_so:
        return ChiTietRuiRoBenhNhan(1.0, [], [])

    # Cộng dồn phi tuyến: he_so = 1.0 + tong_delta / (1 + 0.3 * tong_delta)
    tong_delta = sum(delta_he_so)
    he_so_cuoi = round(1.0 + (tong_delta / (1.0 + 0.25 * tong_delta)), 2)

    return ChiTietRuiRoBenhNhan(he_so_cuoi, yeu_to, canh_bao_duoc_ly)


# ═══ cham() — Chấm điểm rủi ro lâm sàng cho từng mệnh đề ══════════════════════════════
# Kết hợp kết quả khoá căn cứ và cơ địa bệnh nhân; trả về danh sách DanhGia.
def cham(ps, ket_qua_khoa, thong_tin_benh_nhan: Optional[Dict[str, Any]] = None) -> List[DanhGia]:
    """Chấm điểm rủi ro lâm sàng tích hợp cơ địa nhạy cảm và phân tích audit trail."""
    theo_id = {k.id: k for k in ket_qua_khoa}
    tt_bn = phan_tich_co_dia_benh_nhan(thong_tin_benh_nhan)
    ra = []

    for p in ps:
        k = theo_id.get(p.id)
        loai = loai_thong_tin(p)
        nt = MUC_NGHIEM_TRONG[loai]

        if k is not None and k.chan:
            giai_trinh = f"BỊ CHẶN: Dính vi phạm nghiêm trọng ({', '.join(k.chan)})."
            if tt_bn.he_so_tong > 1.0:
                giai_trinh += f" Cơ địa nguy cơ cao: {'; '.join(tt_bn.cac_yeu_to)}."
            ra.append(DanhGia(
                id=p.id,
                loai=loai,
                nghiem_trong=nt,
                thieu=1.0,
                diem_goc=nt,
                diem=nt,
                nhom=BI_CHAN,
                ly_do=list(k.chan),
                he_so_bn=tt_bn.he_so_tong,
                yeu_to_bn=tt_bn.cac_yeu_to,
                canh_bao_duoc_ly=tt_bn.canh_bao_duoc_ly,
                giai_trinh=giai_trinh
            ))
            continue

        canh = list(k.canh_bao) if k is not None else []
        thieu = max((DO_THIEU.get(m, 0.3) for m in canh), default=0.0)

        diem_goc = round(nt * thieu, 4)
        diem_khuech_dai = min(1.0, round(diem_goc * tt_bn.he_so_tong, 4))

        nhom = (NGUY_CO_CAO if diem_khuech_dai >= NGUONG_CAO
                else RUI_RO_THAP if canh else DA_KIEM_CHUNG)

        # Xây dựng giải trình lâm sàng tự động
        giai_trinh_parts = [f"Phân loại '{loai}' (nt={nt}), độ thiếu căn cứ {thieu}."]
        if tt_bn.he_so_tong > 1.0:
            giai_trinh_parts.append(f"Khuếch đại x{tt_bn.he_so_tong} do cơ địa: {'; '.join(tt_bn.cac_yeu_to)}.")
        if diem_khuech_dai >= NGUONG_CAO and diem_goc < NGUONG_CAO:
            giai_trinh_parts.append("LƯU Ý: Vượt ngưỡng nguy cơ cao do tác động từ cơ địa bệnh nhân.")

        ra.append(DanhGia(
            id=p.id,
            loai=loai,
            nghiem_trong=nt,
            thieu=thieu,
            diem_goc=diem_goc,
            diem=diem_khuech_dai,
            nhom=nhom,
            ly_do=canh,
            he_so_bn=tt_bn.he_so_tong,
            yeu_to_bn=tt_bn.cac_yeu_to,
            canh_bao_duoc_ly=tt_bn.canh_bao_duoc_ly,
            giai_trinh=" ".join(giai_trinh_parts)
        ))
    return ra


# ═══ thu_tu_duyet() — Xếp thứ tự ưu tiên để bác sĩ duyệt ══════════════════════════════
# Nhóm bị chặn, nguy cơ cao, rủi ro thấp, đã kiểm chứng; trong nhóm theo độ nghiêm
# trọng.
def thu_tu_duyet(danh_gia: List[DanhGia]) -> List[DanhGia]:
    """Xếp thứ tự ưu tiên bác sĩ cần duyệt."""
    hang = {BI_CHAN: 0, NGUY_CO_CAO: 1, RUI_RO_THAP: 2, DA_KIEM_CHUNG: 3}
    return sorted(danh_gia, key=lambda d: (hang[d.nhom], -d.nghiem_trong, -d.diem, d.id))


# ═══ dem_nhom() — Đếm số mệnh đề theo từng nhóm rủi ro ════════════════════════════════
def dem_nhom(danh_gia: List[DanhGia]) -> Dict[str, int]:
    ra = {BI_CHAN: 0, NGUY_CO_CAO: 0, RUI_RO_THAP: 0, DA_KIEM_CHUNG: 0}
    for d in danh_gia:
        ra[d.nhom] += 1
    return ra


_TEN_LOAI = {
    "di_ung": "dị ứng",
    "thuoc_nti": "thuốc khoảng điều trị hẹp",
    "thuoc": "thuốc",
    "chan_doan": "chẩn đoán",
    "thoi_gian": "mốc thời gian"
}


# ═══ dua_sang_xac_nhan() — Chuyển mệnh đề có cảnh báo sang mục CẦN XÁC NHẬN ═══════════
# Trả về mã mệnh đề kèm ghi chú lý do cảnh báo.
def dua_sang_xac_nhan(danh_gia: List[DanhGia]) -> Dict[int, str]:
    """Chuyen phat bieu sang tab 'CẦN XÁC NHẬN' theo chinh sach lam sang mo rong."""
    from src.duong_ong.b4_kiem_can_cu import LY_DO
    ra = {}
    for d in danh_gia:
        if d.nhom != BI_CHAN and d.ly_do and d.loai in LOAI_XAC_NHAN_KHI_CANH_BAO:
            ly_do_khoa = "; ".join(LY_DO.get(m, m) for m in d.ly_do)
            ghi_chu = f"cảnh báo ở thông tin {_TEN_LOAI.get(d.loai, d.loai)}: {ly_do_khoa}"
            if d.yeu_to_bn:
                ghi_chu += f" | Nhóm nguy cơ cao: {', '.join(d.yeu_to_bn)}"
            ra[d.id] = ghi_chu
    return ra   