# -*- coding: utf-8 -*-
"""Tang 5 — CONG RUI RO (Nang cap chuyen sau lam sang).

Tich hop:
1. Danh muc thuoc khoang dieu tri hep (Narrow Therapeutic Index - NTI).
2. Mo hinh tich luy da yeu to nhay cam (Synergistic Clinical Model).
3. Phan tang do nang suy than (theo eGFR/CKD stage) va giai doan thai ky.
4. Giai trinh lam sang (Clinical Explainability / XAI) phuc vu duyet ho so.
"""
from dataclasses import asdict, dataclass, field
import math
from typing import Any, Dict, List, Optional, Tuple

# Muc nghiem trong theo LOAI thong tin (0.0 -> 1.0)
MUC_NGHIEM_TRONG = {
    "di_ung": 1.0,        # Soc phan ve, hoi chung Stevens-Johnson
    "thuoc_nti": 1.0,     # Thuoc khoang dieu tri hep (Narrow Therapeutic Index)
    "thuoc": 0.9,         # Thuoc dieu tri thong thuong
    "chan_doan": 0.8,     # Chan doan benh ly
    "thoi_gian": 0.6,     # Moc khoi phat, quan he truoc/sau
    "khac": 0.3,          # Trieu chung phu, thong tin hanh chinh
}

# Danh muc hoat chat khoang dieu tri hep & thuoc canh bao cao (High-Alert Medications)
THUOC_KHOANG_DIEU_TRI_HEP = {
    "warfarin", "sintrom", "heparin", "enoxaparin",
    "digoxin", "theophylline", "aminophylline",
    "phenytoin", "carbamazepine", "valproat", "lithium",
    "insulin", "methotrexate", "cyclosporine", "tacrolimus",
    "amiodarone", "gentamicin", "vancomycin"
}

# Do thieu can cu tu khoa bang chung (0.0 -> 1.0)
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


@dataclass
class ChiTietRuiRoBenhNhan:
    he_so_tong: float
    cac_yeu_to: List[str]
    canh_bao_duoc_ly: List[str]


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


def loai_thong_tin(p) -> str:
    """Xac dinh loai thong tin va phat hien som thuoc khoang dieu tri hep."""
    from src import sinh_benh_an
    d = p.to_dict() if hasattr(p, "to_dict") else dict(p)
    d = dict(d, trang_thai="còn hiệu lực")
    noi_dung = str(d.get("noi_dung", "")).lower()

    if "dị ứng" in noi_dung:
        return "di_ung"

    muc, _ = sinh_benh_an._muc_cho(d, 0)
    if muc == "DỊ ỨNG":
        return "di_ung"

    # Kiem tra thuoc khoang dieu tri hep
    if muc == "THUỐC ĐANG DÙNG" or "thuốc" in noi_dung:
        for t in THUOC_KHOANG_DIEU_TRI_HEP:
            if t in noi_dung:
                return "thuoc_nti"
        return "thuoc"

    if muc == "CHẨN ĐOÁN":
        return "chan_doan"

    if d.get("moc_thoi_gian") or d.get("quan_he") in ("đính chính", "diễn biến", "mâu thuẫn"):
        return "thoi_gian"

    return "khac"


def phan_tich_co_dia_benh_nhan(bn: Optional[Dict[str, Any]]) -> ChiTietRuiRoBenhNhan:
    """Mo hinh tich luy da yeu to (Synergistic Saturation Model).
    
    Neu benh nhan dong thoi co nhieu yeu to rui ro, he so khong cong don tuyen tinh
    ma tich luy theo cong thuc phi tuyen: H = 1.0 + Sum(h_i) * giam_tru_bien_thien.
    """
    if not bn:
        return ChiTietRuiRoBenhNhan(1.0, [], [])

    yeu_to = []
    canh_bao_duoc_ly = []
    delta_he_so = []

    # 1. Thai ky & Cho con bu (Phan hoa theo tam ca nguyet neu co)
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

    # 2. Lua tuoi: Tre so sinh (<6 thang), nhi khoa, cao tuoi (>=65, >=80)
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

    # 3. Chuc nang than (eGFR hoac phan do CKD)
    egfr = bn.get("egfr")
    benh_nen = [str(b).lower() for b in bn.get("benh_nen", [])]
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

    # 4. Chuc nang gan
    if any("suy gan" in b or "xơ gan" in b for b in benh_nen):
        delta_he_so.append(0.35)
        yeu_to.append("Bệnh lý xơ gan/suy giảm chức năng gan")
        canh_bao_duoc_ly.append("Giảm độ thanh thải chuyển hóa qua gan pha 1 và enzym CYP450")

    # 5. Da thuoc (Polypharmacy: dung tu 5 thuoc tro len)
    so_thuoc = bn.get("so_thuoc_dang_dung", 0)
    if so_thuoc >= 5:
        delta_he_so.append(0.2)
        yeu_to.append(f"Hội chứng đa thuốc ({so_thuoc} thuốc đồng thời)")

    if not delta_he_so:
        return ChiTietRuiRoBenhNhan(1.0, [], [])

    # Cong don phi tuyen: he_so = 1.0 + tong_delta / (1 + 0.3 * tong_delta)
    tong_delta = sum(delta_he_so)
    he_so_cuoi = round(1.0 + (tong_delta / (1.0 + 0.25 * tong_delta)), 2)

    return ChiTietRuiRoBenhNhan(he_so_cuoi, yeu_to, canh_bao_duoc_ly)


def cham(ps, ket_qua_khoa, thong_tin_benh_nhan: Optional[Dict[str, Any]] = None) -> List[DanhGia]:
    """Cham diem rui ro lam sang tich hop co dia nhay cam va phan tich audit trail."""
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

        # Xay dung giai trinh lam sang tu dong
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


def thu_tu_duyet(danh_gia: List[DanhGia]) -> List[DanhGia]:
    """Xep thu tu uu tien bac si can duyet."""
    hang = {BI_CHAN: 0, NGUY_CO_CAO: 1, RUI_RO_THAP: 2, DA_KIEM_CHUNG: 3}
    return sorted(danh_gia, key=lambda d: (hang[d.nhom], -d.nghiem_trong, -d.diem, d.id))


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


def dua_sang_xac_nhan(danh_gia: List[DanhGia]) -> Dict[int, str]:
    """Chuyen phat bieu sang tab 'CẦN XÁC NHẬN' theo chinh sach lam sang mo rong."""
    from src.khoa_bang_chung import LY_DO
    ra = {}
    for d in danh_gia:
        if d.nhom != BI_CHAN and d.ly_do and d.loai in LOAI_XAC_NHAN_KHI_CANH_BAO:
            ly_do_khoa = "; ".join(LY_DO.get(m, m) for m in d.ly_do)
            ghi_chu = f"cảnh báo ở thông tin {_TEN_LOAI.get(d.loai, d.loai)}: {ly_do_khoa}"
            if d.yeu_to_bn:
                ghi_chu += f" | Nhóm nguy cơ cao: {', '.join(d.yeu_to_bn)}"
            ra[d.id] = ghi_chu
    return ra   