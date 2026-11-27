# -*- coding: utf-8 -*-
"""[Dịch vụ, an toàn và minh bạch › Dịch vụ]
Làm gì   : Nối các chốt an toàn lâm sàng thành một đường chạy và ghi vết từng chốt để kiểm
           toán được.
Vào → Ra : bản nháp, thông tin bệnh nhân, dữ liệu xét nghiệm → kết quả điều phối kèm bản ghi
           vết kiểm toán từng chốt
Đọc từ   : class MediTracePipelineOrchestrator chạy các chốt lần lượt; class KetQuaDieuPhoi
           là kết quả
Mục lục (các hàm/lớp chính):
  class MediTracePipelineOrchestrator  Bộ điều phối chạy các chốt an toàn cho một ca
  class KetQuaDieuPhoi                 Gói kết quả điều phối trọn một ca khám
  class AuditTrailRecord               Hồ sơ kiểm toán của một ca khám
  class AuditCheckpoint                Kết quả kiểm của một chốt an toàn
  tai_kiem_tra_nhanh()                 Tái kiểm tra nhanh khi bác sĩ sửa đơn hoặc bệnh án
  _tinh_thang_diem_lam_sang()          Tính 9 thang điểm lâm sàng khi đủ dữ kiện
Gọi tới  : cong_cu_lam_sang/canh_bao_tuong_tac_thuoc,
           cong_cu_lam_sang/chuan_hoa_don_vi_xet_nghiem, cong_cu_lam_sang/di_ung_cheo,
           cong_cu_lam_sang/doi_soat_can_lam_sang, cong_cu_lam_sang/goi_y_cau_hoi_socrates,
           cong_cu_lam_sang/hieu_chinh_lieu, cong_cu_lam_sang/quy_dao_nhieu_lan_kham,
           cong_cu_lam_sang/thang_diem_nguy_co … (tổng 18 tệp)
Dùng bởi : he_thong/dich_vu_http
Tên cũ   : dieu_phoi_ha_tang.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Trụ cột 4: Hạ tầng Điều phối Luồng Toàn diện & Ghi vết Kiểm toán (End-to-End Orchestrator & Audit Trail).

Hạ tầng thống nhất kết nối toàn bộ các tầng:
  Đầu vào -> ASR Guardrail -> Speaker Guardrail -> Extraction -> Dialogue Act Guardrail ->
  Evidence Lock -> Pharmacovigilance DDI Gate -> Asymmetric Risk Gate -> Output (3 Partitions + HL7 FHIR Bundle).
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import re
import time
from typing import Any, Dict, List, Optional, Tuple

from src.he_thong.rao_chan_an_toan import (
    ASRQualityGuardrail,
    SpeakerConsistencyGuardrail,
    DialogueActGuardrail,
    EvidenceIntegrityGuardrail,
    ClinicalSafetyGuardrail,
    DUOC_THU_QUOC_GIA,
)
from src.cong_cu_lam_sang.canh_bao_tuong_tac_thuoc import ClinicalPharmacovigilanceEngine
from src.cong_cu_lam_sang.xuat_fhir_r4 import FHIRExporter
from src.duong_ong import b5_xep_cho_cong_rui_ro as cong_rui_ro
from src.duong_ong import b4_kiem_can_cu as khoa_bang_chung
from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu


from src.cong_cu_lam_sang.doi_soat_can_lam_sang import ParaclinicalCorrelator
from src.canh_bao import gop as _canh_bao_gop
from src.cong_cu_lam_sang.chuan_hoa_don_vi_xet_nghiem import chuan_hoa_du_lieu_xet_nghiem
from src.cong_cu_lam_sang.di_ung_cheo import kiem_tra_di_ung_cheo
from src.he_thong.ep_kieu_dau_vao import chuan_hoa_thong_tin_benh_nhan, so_an_toan
from src.cong_cu_lam_sang.quy_dao_nhieu_lan_kham import phan_tich_quy_dao_lam_sang
from src.cong_cu_lam_sang.thang_diem_nguy_co import ClinicalRiskScoringEngine
from src.cong_cu_lam_sang.hieu_chinh_lieu import kiem_tra_hieu_chinh_lieu
from src.cong_cu_lam_sang.to_dan_do_benh_nhan import sinh_ban_dan_do_benh_nhan
from src.he_thong.khu_dinh_danh import ClinicalDeidentifier
from src.cong_cu_lam_sang.goi_y_cau_hoi_socrates import ActiveClinicalClarificationAgent, KetQuaTroLyLamSang


# ═══ class AuditCheckpoint — Kết quả kiểm của một chốt an toàn ════════════════════════
# Gồm tên chốt, thời gian, trạng thái DAT/CANH_BAO/CHAN và cảnh báo.
@dataclass
class AuditCheckpoint:
    ten_chot: str
    thoi_gian_ms: float
    trang_thai: str               # "DAT" | "CANH_BAO" | "CHAN"
    chi_tiet: str
    canh_bao: List[str] = field(default_factory=list)


# ═══ class AuditTrailRecord — Hồ sơ kiểm toán của một ca khám ═════════════════════════
# Chứa mã ca, chữ ký băm SHA-256 và danh sách các chốt đã chạy.
@dataclass
class AuditTrailRecord:
    ma_ca: str
    thoi_gian_khoi_tao: str
    tong_thoi_gian_ms: float
    chu_ky_bam_sha256: str
    cac_chot_kiem_soat: List[AuditCheckpoint] = field(default_factory=list)
    tong_so_canh_bao: int = 0
    an_toan_lam_sang: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ═══ class KetQuaDieuPhoi — Gói kết quả điều phối trọn một ca khám ════════════════════
# Gồm bản nháp 3 phân vùng, FHIR, rủi ro, dược lý, thang điểm và hồ sơ kiểm toán.
@dataclass
class KetQuaDieuPhoi:
    ma_ca: str
    ban_nhap_3_phan_vung: Dict[str, str]
    fhir_bundle: Dict[str, Any]
    danh_gia_rui_ro: List[Any]
    kiem_duyet_duoc_ly: Any
    audit_trail: AuditTrailRecord
    doi_soat_can_lam_sang: Optional[Any] = None
    thang_diem_nguy_co: Optional[Dict[str, Any]] = None
    hieu_chinh_lieu: Optional[Dict[str, Any]] = None
    ban_dan_do_benh_nhan: Optional[Dict[str, Any]] = None
    hoi_thoai_da_khu_dinh_danh: str = ""
    tro_ly_lam_sang: Optional[Any] = None
    quy_dao_lam_sang: Optional[Dict[str, Any]] = None


_RE_CAU_DI_UNG = re.compile(
    r"(?i)(?<!\w)(dị\s+ứng|mẫn\s+cảm|phản\s+vệ|sốc\s+phản\s+vệ|"
    r"nổi\s+mề\s+đay\s+(?:khi|với|do)|phát\s+ban\s+(?:khi|với|do)|mẩn\s+ngứa\s+(?:khi|với|do))(?!\w)"
)


# ─── _trich_danh_sach_thuoc_hop_le() — Lọc danh sách thuốc bệnh nhân thật sự đang dùng ───
# Bỏ phủ định, giả định, thuốc đã ngừng hoặc bị thay thế, câu dị ứng; chỉ chu_the_id
# bằng 0.
def _trich_danh_sach_thuoc_hop_le(danh_sach_phat_bieu: List[PhatBieu]) -> List[str]:
    """Lọc thuốc đang dùng hoặc được kê trong kế hoạch điều trị của chính bệnh nhân (chu_the_id == 0),
    loại bỏ phủ định, giả định, phát biểu bị thay thế, thuốc đã ngừng, câu dị ứng và lời dặn không phải thuốc."""
    from src.cong_cu_lam_sang import tri_thuc_thuoc as _ttt

    ket_qua: List[str] = []
    for p in danh_sach_phat_bieu:
        if getattr(p, "chu_the_id", 0) != 0:
            continue
        if getattr(p, "phu_dinh", False):
            continue
        if getattr(p, "trang_thai", "còn hiệu lực") != "còn hiệu lực":
            continue
        if getattr(p, "tinh_huong", "thực tế") == "giả định":
            continue
        if getattr(p, "do_chac_chan", "chắc chắn") == "chưa ghi nhận":
            continue

        thuoc_dict = getattr(p, "thuoc", None)
        muc = (getattr(p, "muc", "") or "").strip().upper()
        if not muc and hasattr(p, "to_dict"):
            muc, _ = sinh_benh_an._muc_cho(p.to_dict(), 0)
        noi_dung = (getattr(p, "noi_dung", "") or "").strip()
        nd_low = noi_dung.lower()

        # Loại trừ câu dị ứng / mẫn cảm để chất gây dị ứng không bao giờ bị coi là thuốc đang dùng/kê đơn
        if muc == "DỊ ỨNG" or _RE_CAU_DI_UNG.search(nd_low):
            continue

        if any(kw in nd_low for kw in ("đã ngừng", "ngừng dùng", "ngưng dùng", "đã ngưng")):
            continue

        if isinstance(thuoc_dict, dict):
            if thuoc_dict.get("trang_thai_dung") == "đã ngừng":
                continue
            ten = (thuoc_dict.get("ten") or "").strip()
            if ten:
                ket_qua.append(ten)
                continue

        if not noi_dung:
            continue

        # Khi không có PhatBieu.thuoc có cấu trúc: chỉ nhận tên thuốc thật khớp danh mục hoạt chất/biệt dược
        thuoc_khop: List[str] = []
        da_thay = set()
        for m_rx in _ttt.regex_ten_thuoc().finditer(noi_dung):
            ten_m = m_rx.group(1).strip()
            hc_m = _ttt.hoat_chat(ten_m) or ten_m.lower()
            if hc_m not in da_thay:
                da_thay.add(hc_m)
                thuoc_khop.append(ten_m)
        for m_aho in ClinicalPharmacovigilanceEngine.nhan_dien_thuoc_aho_corasick(noi_dung):
            hc_a = m_aho["hoat_chat"]
            if hc_a not in da_thay:
                da_thay.add(hc_a)
                thuoc_khop.append(m_aho["tu_khoa_khop"])
        for dt in DUOC_THU_QUOC_GIA:
            if re.search(rf"(?i)(?<!\w){re.escape(dt)}(?!\w)", nd_low):
                hc_dt = _ttt.hoat_chat(dt) or dt
                if hc_dt not in da_thay:
                    da_thay.add(hc_dt)
                    thuoc_khop.append(dt)

        ket_qua.extend(thuoc_khop)
    return ket_qua


# ─── _trich_danh_sach_di_ung_hop_le() — Lọc dị ứng khẳng định còn hiệu lực ────────────
# Lấy từ mệnh đề của chính bệnh nhân và dị ứng có sẵn trong thông tin bệnh nhân.
def _trich_danh_sach_di_ung_hop_le(
    danh_sach_phat_bieu: List[PhatBieu],
    thong_tin_benh_nhan: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """Chỉ trích xuất dị ứng khẳng định, còn hiệu lực của chính bệnh nhân (chu_the_id == 0)
    kèm dị ứng có sẵn trong thong_tin_benh_nhan."""
    ket_qua: List[str] = []
    da_co = set()

    def _them(s: str) -> None:
        t = re.sub(r"\s+", " ", (s or "").strip())
        if t and t.lower() not in da_co:
            da_co.add(t.lower())
            ket_qua.append(t)

    if isinstance(thong_tin_benh_nhan, dict):
        for khoa in ("di_ung", "danh_sach_di_ung", "tien_su_di_ung"):
            raw = thong_tin_benh_nhan.get(khoa)
            if not raw:
                continue
            if isinstance(raw, str):
                for phan in re.split(r"[,;\n]+", raw):
                    _them(phan)
            elif isinstance(raw, dict):
                ten = raw.get("ten") or raw.get("hoat_chat") or raw.get("chat_di_ung") or raw.get("noi_dung") or ""
                _them(str(ten))
            elif isinstance(raw, (list, tuple, set)):
                for x in raw:
                    if isinstance(x, dict):
                        ten = x.get("ten") or x.get("hoat_chat") or x.get("chat_di_ung") or x.get("noi_dung") or ""
                        _them(str(ten))
                    elif x is not None:
                        _them(str(x))

    for p in danh_sach_phat_bieu or []:
        if getattr(p, "chu_the_id", 0) != 0:
            continue
        if getattr(p, "phu_dinh", False):
            continue
        if getattr(p, "trang_thai", "còn hiệu lực") != "còn hiệu lực":
            continue
        if getattr(p, "tinh_huong", "thực tế") == "giả định":
            continue
        if getattr(p, "do_chac_chan", "chắc chắn") == "chưa ghi nhận":
            continue

        muc = (getattr(p, "muc", "") or "").strip().upper()
        if not muc and hasattr(p, "to_dict"):
            muc, _ = sinh_benh_an._muc_cho(p.to_dict(), 0)
        noi_dung = (getattr(p, "noi_dung", "") or "").strip()
        nd_low = noi_dung.lower()
        if muc != "DỊ ỨNG" and not _RE_CAU_DI_UNG.search(nd_low):
            continue

        sau = re.sub(
            r"^.*?(?:dị\s+ứng|mẫn\s+cảm|phản\s+vệ|sốc\s+phản\s+vệ|nổi\s+mề\s+đay|phát\s+ban|mẩn\s+ngứa)\s*(?:khi|với|do)?\s*",
            "",
            nd_low,
            count=1,
        )
        ve_dau = re.split(r"[,;.]|(?<!\w)(đang|nhưng|còn)(?!\w)", sau)[0].strip()
        if ve_dau:
            for sub in re.split(r"\s+(?:và|hoặc)\s+|/", ve_dau):
                sub_s = re.sub(r"^(?:kháng\s+sinh|thuốc)\s+", "", sub.strip())
                if sub_s and sub_s not in ("gì", "thuốc"):
                    _them(sub_s)
    return ket_qua


# ─── _gop_du_lieu_can_lam_sang() — Gộp xét nghiệm từ thông tin bệnh nhân và đầu vào ───
# Giá trị đầu vào riêng ghi đè; kết quả được chuẩn hoá số.
def _gop_du_lieu_can_lam_sang(
    thong_tin_benh_nhan: Optional[Dict[str, Any]],
    du_lieu_xet_nghiem: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    gop: Dict[str, Any] = {}
    if isinstance(thong_tin_benh_nhan, dict):
        for nested_xn in ("xet_nghiem", "du_lieu_xet_nghiem", "labs"):
            if isinstance(thong_tin_benh_nhan.get(nested_xn), dict):
                for k_xn, v_xn in thong_tin_benh_nhan[nested_xn].items():
                    if v_xn is not None:
                        gop[k_xn] = v_xn
    if isinstance(du_lieu_xet_nghiem, dict):
        for k_xn, v_xn in du_lieu_xet_nghiem.items():
            if v_xn is not None:
                gop[k_xn] = v_xn
    return chuan_hoa_du_lieu_xet_nghiem(gop) if gop else {}


# ─── _lay_so_tu_nguon() — Lấy số đầu tiên đọc được từ nhiều nguồn ─────────────────────
# Thử lần lượt từng khoá và từng nguồn; không có thì None.
def _lay_so_tu_nguon(nguon_list: Tuple[Optional[Dict[str, Any]], ...], *keys: str) -> Optional[float]:
    for d in nguon_list:
        if not isinstance(d, dict):
            continue
        for k in keys:
            if d.get(k) is not None:
                v = so_an_toan(d.get(k))
                if v is not None:
                    return v
    return None


# ─── _trich_sinh_hieu() — Trích sinh hiệu từ dữ liệu có cấu trúc hoặc lời thoại ───────
# Ưu tiên số có cấu trúc, thiếu thì tìm trong văn bản bằng biểu thức chính quy.
def _trich_sinh_hieu(
    thong_tin_benh_nhan: Optional[Dict[str, Any]],
    du_lieu_cls: Dict[str, Any],
    van_ban: str,
) -> Dict[str, Optional[float]]:
    nguon = (du_lieu_cls, thong_tin_benh_nhan)
    vb_low = (van_ban or "").lower()

    nhip_tho = _lay_so_tu_nguon(nguon, "nhip_tho", "rr", "respiratory_rate")
    if nhip_tho is None:
        m_rr = re.search(r"\bnhịp thở\s*(?:là|:)?\s*(\d{1,2})\b", vb_low)
        if m_rr:
            nhip_tho = so_an_toan(m_rr.group(1))

    hatt = _lay_so_tu_nguon(nguon, "huyet_ap_tam_thu", "hatt", "sbp")
    hattr = _lay_so_tu_nguon(nguon, "huyet_ap_tam_truong", "hattr", "dbp")
    if hatt is None or hattr is None:
        for d in nguon:
            if isinstance(d, dict):
                ha_raw = d.get("huyet_ap") or d.get("bp")
                if isinstance(ha_raw, str):
                    m_ha = re.search(r"(\d{2,3})\s*/\s*(\d{2,3})", ha_raw)
                    if m_ha:
                        hatt = hatt if hatt is not None else so_an_toan(m_ha.group(1))
                        hattr = hattr if hattr is not None else so_an_toan(m_ha.group(2))
                        break
        if hatt is None or hattr is None:
            m_ha_vb = re.search(r"\bhuyết áp\s*(?:là|:)?\s*(\d{2,3})\s*/\s*(\d{2,3})\b", vb_low)
            if m_ha_vb:
                hatt = hatt if hatt is not None else so_an_toan(m_ha_vb.group(1))
                hattr = hattr if hattr is not None else so_an_toan(m_ha_vb.group(2))

    nhip_tim = _lay_so_tu_nguon(nguon, "nhip_tim", "mach", "hr", "heart_rate")
    if nhip_tim is None:
        m_hr = re.search(r"\b(?:mạch|nhịp tim)\s*(?:là|:)?\s*(\d{2,3})\b", vb_low)
        if m_hr:
            nhip_tim = so_an_toan(m_hr.group(1))

    can_nang = _lay_so_tu_nguon((thong_tin_benh_nhan, du_lieu_cls), "can_nang_kg", "can_nang", "weight_kg")
    chieu_cao = _lay_so_tu_nguon((thong_tin_benh_nhan, du_lieu_cls), "chieu_cao_cm", "height_cm")
    if chieu_cao is None:
        cc_raw = _lay_so_tu_nguon((thong_tin_benh_nhan, du_lieu_cls), "chieu_cao", "height")
        if cc_raw is not None:
            chieu_cao = cc_raw * 100.0 if cc_raw < 3.0 else cc_raw

    return {
        "nhip_tho": nhip_tho,
        "hatt": hatt,
        "hattr": hattr,
        "nhip_tim": nhip_tim,
        "can_nang_kg": can_nang,
        "chieu_cao_cm": chieu_cao,
    }


# ─── _tinh_thang_diem_lam_sang() — Tính 9 thang điểm lâm sàng khi đủ dữ kiện ──────────
# Tự kích hoạt theo tiêu chí khách quan; không bịa dữ kiện thiếu.
def _tinh_thang_diem_lam_sang(
    hoi_thoai: str,
    chan_doan: str,
    thong_tin_benh_nhan: Optional[Dict[str, Any]],
    du_lieu_cls: Dict[str, Any],
) -> Dict[str, Any]:
    """Tính toàn bộ 9 thang điểm lâm sàng từ đầu vào có cấu trúc `thang_diem` và tự động kích hoạt
    khi có tiêu chí khách quan / sinh hiệu / xét nghiệm đầy đủ (không bịa dữ kiện thiếu)."""
    thang_diem_dict: Dict[str, Any] = {}
    tt_bn = thong_tin_benh_nhan if isinstance(thong_tin_benh_nhan, dict) else {}
    vb_day_du = f"{hoi_thoai or ''} {chan_doan or ''}".strip()
    vb_low = vb_day_du.lower()

    benh_nen_list: List[str] = []
    for k_bn in ("benh_nen", "tien_su_benh"):
        raw_bn = tt_bn.get(k_bn)
        if isinstance(raw_bn, str):
            benh_nen_list.extend([x.strip().lower() for x in re.split(r"[,;\n]+", raw_bn) if x.strip()])
        elif isinstance(raw_bn, (list, tuple, set)):
            benh_nen_list.extend([str(x).strip().lower() for x in raw_bn if x is not None and str(x).strip()])
    benh_nen_str = " ".join(benh_nen_list)
    ngu_canh_low = f"{vb_low} {benh_nen_str}"

    tuoi_so = so_an_toan(tt_bn.get("tuoi"))
    tuoi = int(tuoi_so) if tuoi_so is not None and tuoi_so > 0 else None
    gioi_tinh = str(tt_bn.get("gioi_tinh") or ("nữ" if tt_bn.get("la_nu") is True else "nam"))
    sinh_hieu = _trich_sinh_hieu(tt_bn, du_lieu_cls, vb_day_du)

    # 1. Đọc trước cấu trúc có sẵn `thong_tin_benh_nhan["thang_diem"]` cho đủ 9 thang điểm
    scores = tt_bn.get("thang_diem", {})
    if isinstance(scores, dict):
        strict_scores = {
            "cha2ds2_vasc": (
                "CHA2DS2-VASc", ClinicalRiskScoringEngine.tinh_cha2ds2_vasc,
                {"tuoi", "gioi_tinh", "tien_su_suy_tim", "tien_su_tang_huyet_ap",
                 "tien_su_dai_thao_duong", "tien_su_dot_quy_tia", "tien_su_benh_mach_mau"},
            ),
            "wells_pe": (
                "Wells PE", ClinicalRiskScoringEngine.tinh_wells_pe,
                {"dau_hieu_dvt", "pe_la_chan_doan_hang_dau", "nhip_tim_tren_100",
                 "bat_dong_hoac_phau_thuat_gan_day", "tien_su_dvt_pe", "ho_ra_mau", "ung_thu_dang_dieu_tri"},
            ),
            "glasgow_blatchford": (
                "Glasgow-Blatchford", ClinicalRiskScoringEngine.tinh_glasgow_blatchford,
                {"urea_mmol_l", "hb_g_dl", "gioi_tinh", "huyet_ap_tam_thu", "nhip_tim",
                 "di_ngoai_phan_den", "co_con_ngat", "tien_su_benh_gan", "tien_su_suy_tim"},
            ),
        }
        for key, (label, calculate, required) in strict_scores.items():
            values = scores.get(key)
            if isinstance(values, dict) and required.issubset(values.keys()):
                thang_diem_dict[label] = asdict(calculate(**values))

        flexible_scores = {
            "curb65": ("CURB-65", ClinicalRiskScoringEngine.tinh_curb65, {"tuoi", "y_thuc_lu_lan", "urea_mmol_l", "bun_mg_dl", "nhip_tho", "huyet_ap_tam_thu", "huyet_ap_tam_truong", "van_ban_kham"}),
            "gcs": ("GCS", ClinicalRiskScoringEngine.tinh_gcs, {"mat", "loi_noi", "van_dong", "van_ban_kham"}),
            "qsofa": ("qSOFA", ClinicalRiskScoringEngine.tinh_qsofa, {"nhip_tho", "huyet_ap_tam_thu", "y_thuc_thay_doi", "van_ban_kham"}),
            "nyha": ("NYHA", ClinicalRiskScoringEngine.tinh_nyha, {"van_ban_kham", "kho_tho_khi_nghi", "kho_tho_khi_gang_suc_nhe", "kho_tho_khi_gang_suc_nang"}),
            "child_pugh": ("Child-Pugh", ClinicalRiskScoringEngine.tinh_child_pugh, {"bilirubin_umol_l", "albumin_g_l", "inr", "co_truong", "benh_nao_gan"}),
            "bmi": ("BMI", ClinicalRiskScoringEngine.tinh_bmi, {"can_nang_kg", "chieu_cao_cm"}),
        }
        for key, (label, calculate, allowed) in flexible_scores.items():
            values = scores.get(key)
            if isinstance(values, dict) and any(k in allowed for k in values):
                kwargs = {k: v for k, v in values.items() if k in allowed}
                if key == "bmi" and not (so_an_toan(kwargs.get("can_nang_kg")) and so_an_toan(kwargs.get("chieu_cao_cm"))):
                    continue
                thang_diem_dict[label] = asdict(calculate(**kwargs))

    # 2. Tự động kích hoạt từ dữ kiện khách quan khi chưa có trong thang_diem_dict
    urea_val = _lay_so_tu_nguon((du_lieu_cls,), "urea_mmol_l", "urea", "ure")
    hb_val = _lay_so_tu_nguon((du_lieu_cls,), "hb_g_dl", "hb", "hemoglobin")
    nhip_tho_i = int(sinh_hieu["nhip_tho"]) if sinh_hieu["nhip_tho"] is not None else None
    hatt_i = int(sinh_hieu["hatt"]) if sinh_hieu["hatt"] is not None else None
    hattr_i = int(sinh_hieu["hattr"]) if sinh_hieu["hattr"] is not None else None
    nhip_tim_i = int(sinh_hieu["nhip_tim"]) if sinh_hieu["nhip_tim"] is not None else None

    # 2.1 BMI (thuần khách quan từ cân nặng + chiều cao)
    if "BMI" not in thang_diem_dict and sinh_hieu["can_nang_kg"] and sinh_hieu["chieu_cao_cm"]:
        if sinh_hieu["can_nang_kg"] > 0 and sinh_hieu["chieu_cao_cm"] > 0:
            thang_diem_dict["BMI"] = asdict(
                ClinicalRiskScoringEngine.tinh_bmi(
                    can_nang_kg=float(sinh_hieu["can_nang_kg"]),
                    chieu_cao_cm=float(sinh_hieu["chieu_cao_cm"]),
                )
            )

    # 2.2 CURB-65 (viêm phổi / sốt kèm xét nghiệm hoặc sinh hiệu hoặc tuổi >= 65)
    if "CURB-65" not in thang_diem_dict:
        co_viem_phoi = "viêm phổi" in ngu_canh_low
        co_sot_hoac_wbc = ("sốt" in vb_low or "wbc" in du_lieu_cls)
        co_can_cu_curb = bool(du_lieu_cls) or nhip_tho_i is not None or hatt_i is not None or (tuoi is not None and tuoi >= 65)
        if co_viem_phoi or (co_sot_hoac_wbc and co_can_cu_curb):
            thang_diem_dict["CURB-65"] = asdict(
                ClinicalRiskScoringEngine.tinh_curb65(
                    tuoi=tuoi or 0,
                    urea_mmol_l=urea_val,
                    nhip_tho=nhip_tho_i,
                    huyet_ap_tam_thu=hatt_i,
                    huyet_ap_tam_truong=hattr_i,
                    van_ban_kham=vb_day_du,
                )
            )

    # 2.3 CHA2DS2-VASc (rung nhĩ + có tuổi)
    if "CHA2DS2-VASc" not in thang_diem_dict and tuoi is not None:
        if any(w in ngu_canh_low for w in ("rung nhĩ", "afib", "rối loạn nhịp nhĩ")):
            thang_diem_dict["CHA2DS2-VASc"] = asdict(
                ClinicalRiskScoringEngine.tinh_cha2ds2_vasc(
                    tuoi=tuoi,
                    gioi_tinh=gioi_tinh,
                    tien_su_suy_tim="suy tim" in ngu_canh_low,
                    tien_su_tang_huyet_ap=any(w in ngu_canh_low for w in ("tăng huyết áp", "cao huyết áp")),
                    tien_su_dai_thao_duong=any(w in ngu_canh_low for w in ("đái tháo đường", "tiểu đường")),
                    tien_su_dot_quy_tia=any(w in ngu_canh_low for w in ("đột quỵ", "tai biến", "nhồi máu não", "tia")),
                    tien_su_benh_mach_mau=any(w in ngu_canh_low for w in ("nhồi máu cơ tim", "bệnh mạch vành", "mạch máu ngoại biên")),
                    van_ban_kham=vb_day_du,
                )
            )

    # 2.4 Wells PE (nghi thuyên tắc phổi / huyết khối tĩnh mạch sâu)
    if "Wells PE" not in thang_diem_dict:
        if any(w in ngu_canh_low for w in ("thuyên tắc phổi", "huyết khối tĩnh mạch sâu", "dvt")):
            thang_diem_dict["Wells PE"] = asdict(
                ClinicalRiskScoringEngine.tinh_wells_pe(
                    nhip_tim_tren_100=(nhip_tim_i is not None and nhip_tim_i > 100),
                    pe_la_chan_doan_hang_dau=("thuyên tắc phổi" in ngu_canh_low),
                    van_ban_kham=vb_day_du,
                )
            )

    # 2.5 Glasgow-Blatchford (xuất huyết tiêu hóa trên + có ít nhất 1 chỉ số khách quan)
    if "Glasgow-Blatchford" not in thang_diem_dict:
        co_xhth = any(w in ngu_canh_low for w in ("xuất huyết tiêu hóa", "nôn ra máu", "tiêu phân đen", "đi cầu phân đen", "phân đen"))
        if co_xhth and (urea_val is not None or hb_val is not None or hatt_i is not None or nhip_tim_i is not None):
            thang_diem_dict["Glasgow-Blatchford"] = asdict(
                ClinicalRiskScoringEngine.tinh_glasgow_blatchford(
                    urea_mmol_l=urea_val,
                    hb_g_dl=hb_val,
                    gioi_tinh=gioi_tinh,
                    huyet_ap_tam_thu=hatt_i,
                    nhip_tim=nhip_tim_i,
                    tien_su_benh_gan=any(w in ngu_canh_low for w in ("xơ gan", "viêm gan mạn", "bệnh gan")),
                    tien_su_suy_tim=("suy tim" in ngu_canh_low),
                    van_ban_kham=vb_day_du,
                )
            )

    # 2.6 GCS (khi có điểm E/V/M cấu trúc hoặc dấu hiệu thay đổi tri giác)
    if "GCS" not in thang_diem_dict:
        gcs_e = _lay_so_tu_nguon((tt_bn, du_lieu_cls), "gcs_mat", "gcs_e")
        gcs_v = _lay_so_tu_nguon((tt_bn, du_lieu_cls), "gcs_loi_noi", "gcs_v")
        gcs_m = _lay_so_tu_nguon((tt_bn, du_lieu_cls), "gcs_van_dong", "gcs_m")
        co_roi_loan_tri_giac = any(
            w in vb_low for w in (
                "hôn mê", "mê sâu", "gọi mở mắt", "gọi không mở mắt", "kích thích đau",
                "không nói được", "lú lẫn", "lơ mơ", "chấn thương sọ não", "đột quỵ",
            )
        )
        if gcs_e is not None or gcs_v is not None or gcs_m is not None or co_roi_loan_tri_giac:
            thang_diem_dict["GCS"] = asdict(
                ClinicalRiskScoringEngine.tinh_gcs(
                    mat=int(gcs_e) if gcs_e is not None else 4,
                    loi_noi=int(gcs_v) if gcs_v is not None else 5,
                    van_dong=int(gcs_m) if gcs_m is not None else 6,
                    van_ban_kham=vb_day_du,
                )
            )

    # 2.7 qSOFA (nhiễm trùng/sepsis + ít nhất 1 tiêu chí sinh hiệu/tri giác khách quan)
    if "qSOFA" not in thang_diem_dict:
        co_nhiem_trung = any(w in ngu_canh_low for w in ("nhiễm khuẩn", "nhiễm trùng", "sốc nhiễm khuẩn", "sepsis", "viêm phổi", "sốt"))
        co_y_thuc = any(w in vb_low for w in ("lú lẫn", "lơ mơ", "kém tiếp xúc", "mê sảng", "ngủ gà"))
        co_tieu_chi_qsofa = (
            (nhip_tho_i is not None and nhip_tho_i >= 22)
            or (hatt_i is not None and hatt_i <= 100)
            or co_y_thuc
        )
        if co_nhiem_trung and (co_tieu_chi_qsofa or (nhip_tho_i is not None and hatt_i is not None)):
            thang_diem_dict["qSOFA"] = asdict(
                ClinicalRiskScoringEngine.tinh_qsofa(
                    nhip_tho=nhip_tho_i,
                    huyet_ap_tam_thu=hatt_i,
                    y_thuc_thay_doi=co_y_thuc,
                    van_ban_kham=vb_day_du,
                )
            )

    # 2.8 NYHA (suy tim / khó thở khi gắng sức hoặc nằm)
    if "NYHA" not in thang_diem_dict:
        if any(w in ngu_canh_low for w in (
            "suy tim", "nyha", "khó thở khi nằm", "khó thở khi nghỉ ngơi",
            "khó thở kịch phát", "leo cầu thang", "đi bộ vài mét", "làm việc nhà nhẹ",
        )):
            thang_diem_dict["NYHA"] = asdict(
                ClinicalRiskScoringEngine.tinh_nyha(van_ban_kham=vb_day_du)
            )

    # 2.9 Child-Pugh (xơ gan / bệnh gan hoặc có >= 2 chỉ số chức năng gan)
    if "Child-Pugh" not in thang_diem_dict:
        bili_val = _lay_so_tu_nguon((du_lieu_cls,), "bilirubin_umol_l", "bilirubin")
        alb_val = _lay_so_tu_nguon((du_lieu_cls,), "albumin_g_l", "albumin")
        inr_val = _lay_so_tu_nguon((du_lieu_cls,), "inr")
        so_xn_gan = sum(1 for v in (bili_val, alb_val, inr_val) if v is not None)
        co_benh_gan = any(w in ngu_canh_low for w in ("xơ gan", "suy gan", "cổ trướng", "bệnh não gan"))
        if co_benh_gan or so_xn_gan >= 2:
            co_truong = "NHIEU" if any(w in vb_low for w in ("cổ trướng nhiều", "cổ trướng căng")) else (
                "IT" if any(w in vb_low for w in ("cổ trướng", "báng bụng")) else "KHONG"
            )
            nao_gan = "DO_3" if any(w in vb_low for w in ("hôn mê gan", "não gan độ 3", "não gan độ 4")) else (
                "DO_1" if any(w in vb_low for w in ("bệnh não gan", "run vỗ cánh")) else "KHONG"
            )
            thang_diem_dict["Child-Pugh"] = asdict(
                ClinicalRiskScoringEngine.tinh_child_pugh(
                    bilirubin_umol_l=bili_val,
                    albumin_g_l=alb_val,
                    inr=inr_val,
                    co_truong=co_truong,
                    benh_nao_gan=nao_gan,
                )
            )

    canh_bao_nguy_co_cao = [
        f"{ten}: {kq_td['diem_so']} điểm ({kq_td['phan_tang_nguy_co']}) — {kq_td['khuyen_cao_lam_sang']}"
        for ten, kq_td in thang_diem_dict.items()
        if isinstance(kq_td, dict) and kq_td.get("phan_tang_nguy_co") in ("CAO", "NGUY_KICH")
    ]
    if canh_bao_nguy_co_cao:
        thang_diem_dict["canh_bao_nguy_co_cao"] = canh_bao_nguy_co_cao

    return thang_diem_dict


# ═══ class MediTracePipelineOrchestrator — Bộ điều phối chạy các chốt an toàn cho một ca ═══
# xu_ly_ca_kham chạy từ khử định danh đến rào chắn, khoá bằng chứng, dược lý và ghi kiểm
# toán.
class MediTracePipelineOrchestrator:
    """Bộ điều phối hạ tầng trung tâm cho MediTrace Sentinel."""

    @classmethod
    def xu_ly_ca_kham(cls, ma_ca: str, hoi_thoai: str,
                      danh_sach_phat_bieu: List[PhatBieu],
                      thong_tin_benh_nhan: Optional[Dict[str, Any]] = None,
                      du_lieu_xet_nghiem: Optional[Dict[str, Any]] = None,
                      lich_su_lan_kham: Optional[List[Dict[str, Any]]] = None) -> KetQuaDieuPhoi:
        """Thực thi toàn bộ chu trình xử lý end-to-end với đầy đủ 5 lớp guardrails và audit logging."""
        t0 = time.perf_counter()
        now_str = datetime.now(timezone.utc).isoformat()
        thong_tin_benh_nhan = chuan_hoa_thong_tin_benh_nhan(thong_tin_benh_nhan) if thong_tin_benh_nhan is not None else None
        chot_kiem_soat: List[AuditCheckpoint] = []
        tat_ca_canh_bao: List[str] = []
        ten_bn = (thong_tin_benh_nhan.get("ten") or thong_tin_benh_nhan.get("ho_ten")) if thong_tin_benh_nhan else None
        ban_sao_an_danh = ClinicalDeidentifier.an_danh_van_ban(hoi_thoai, ten_benh_nhan=ten_bn)

        # ----------------------------------------------------------------------
        # CHỐT 1: ASR & Dược thư âm vị
        # ----------------------------------------------------------------------
        t_c1 = time.perf_counter()
        res_asr = ASRQualityGuardrail.kiem_tra_phien_am(hoi_thoai)
        dur_c1 = round((time.perf_counter() - t_c1) * 1000, 2)
        status_c1 = "DAT" if res_asr.hop_le else "CANH_BAO"
        chot_kiem_soat.append(AuditCheckpoint(
            ten_chot="Guardrail 1: ASR & Dược thư âm vị",
            thoi_gian_ms=dur_c1,
            trang_thai=status_c1,
            chi_tiet=res_asr.chi_tiet,
            canh_bao=res_asr.canh_bao
        ))
        tat_ca_canh_bao.extend(res_asr.canh_bao)

        # ----------------------------------------------------------------------
        # CHỐT 2: Nhất quán Chủ thể & Đại từ
        # ----------------------------------------------------------------------
        t_c2 = time.perf_counter()
        cb_chu_the = []
        for p in danh_sach_phat_bieu:
            res_sc = SpeakerConsistencyGuardrail.kiem_tra_xung_ho(
                nguoi_noi=p.nguoi_noi,
                chu_the_id=p.chu_the_id,
                cau_noi=p.noi_dung
            )
            if not res_sc.hop_le:
                cb_chu_the.extend(res_sc.canh_bao)
        dur_c2 = round((time.perf_counter() - t_c2) * 1000, 2)
        chot_kiem_soat.append(AuditCheckpoint(
            ten_chot="Guardrail 2: Nhất quán Chủ thể & Vai người nói",
            thoi_gian_ms=dur_c2,
            trang_thai="DAT" if not cb_chu_the else "CANH_BAO",
            chi_tiet=f"Đã đối soát {len(danh_sach_phat_bieu)} phát biểu.",
            canh_bao=cb_chu_the
        ))
        tat_ca_canh_bao.extend(cb_chu_the)

        # ----------------------------------------------------------------------
        # CHỐT 3: Dialogue Act & Đính chính
        # ----------------------------------------------------------------------
        t_c3 = time.perf_counter()
        cb_dialogue = []
        for p in danh_sach_phat_bieu:
            if DialogueActGuardrail.la_cau_gia_dinh_hoac_tuong_lai(p.noi_dung):
                cb_dialogue.append(f"Phát hiện câu giả định/kế hoạch tương lai: '{p.noi_dung}'")
        dur_c3 = round((time.perf_counter() - t_c3) * 1000, 2)
        chot_kiem_soat.append(AuditCheckpoint(
            ten_chot="Guardrail 3: Dialogue Act & Giả định tương lai",
            thoi_gian_ms=dur_c3,
            trang_thai="DAT" if not cb_dialogue else "CANH_BAO",
            chi_tiet="Rà soát phủ định và điều kiện lâm sàng.",
            canh_bao=cb_dialogue
        ))
        tat_ca_canh_bao.extend(cb_dialogue)

        # ----------------------------------------------------------------------
        # CHỐT 4: Khóa căn cứ & Cổng Rủi ro
        # ----------------------------------------------------------------------
        t_c4 = time.perf_counter()
        kq_khoa = khoa_bang_chung.khoa_ca(danh_sach_phat_bieu, hoi_thoai)
        danh_gia_rr = cong_rui_ro.cham(danh_sach_phat_bieu, kq_khoa["ket_qua"], thong_tin_benh_nhan)
        ly_do_khoa_map = khoa_bang_chung.ly_do_chan(kq_khoa["ket_qua"])
        xac_nhan_map = {**ly_do_khoa_map, **cong_rui_ro.dua_sang_xac_nhan(danh_gia_rr)}

        # BỔ SUNG QUY TẮC AN TOÀN DƯỢC THƯ ASR (HUMAN-IN-THE-LOOP):
        # CHỈ áp dụng cho gợi ý âm vị tên thuốc (`goi_y_thuoc`), tuyệt đối KHÔNG gắn nhãn thuốc cho biến âm triệu chứng/phương ngữ!
        goi_y_thuoc_asr = getattr(res_asr, "goi_y_thuoc", None)
        if goi_y_thuoc_asr:
            for idx_g, (am_vi, chuan) in enumerate(goi_y_thuoc_asr.items()):
                khoa_id = f"ASR_THUOC_{idx_g + 1}"
                xac_nhan_map[khoa_id] = (
                    f"[BÔI ĐỎ - CẦN BÁC SĨ XÁC NHẬN TÊN THUỐC]: Tín hiệu ASR ghi nhận âm vị '{am_vi}' "
                    f"-> Hệ thống gợi ý '{chuan.capitalize()}'. "
                    f"Do tạp âm phòng khám/phát âm không chuẩn, hệ thống CẤM tự ý đưa vào đơn. Bác sĩ cần xác nhận đúng hay không."
                )

        so_bi_chan = sum(1 for k in (kq_khoa.get("ket_qua") or []) if not k.qua)
        dur_c4 = round((time.perf_counter() - t_c4) * 1000, 2)
        chot_kiem_soat.append(AuditCheckpoint(
            ten_chot="Tầng Khóa căn cứ & Cổng Rủi ro lâm sàng",
            thoi_gian_ms=dur_c4,
            trang_thai="DAT" if so_bi_chan == 0 else "CANH_BAO",
            chi_tiet=f"{so_bi_chan} mệnh đề bị chặn, {len(xac_nhan_map)} mục chuyển sang Cần xác nhận.",
            canh_bao=[f"Chuyển ID {i}: {ly}" for i, ly in xac_nhan_map.items()]
        ))

        # ----------------------------------------------------------------------
        # CHỐT 5: Tầng Kiểm duyệt Dược lý Lâm sàng Nâng cao (Trụ cột 1)
        # ----------------------------------------------------------------------
        t_c5 = time.perf_counter()
        danh_sach_thuoc = _trich_danh_sach_thuoc_hop_le(danh_sach_phat_bieu)
        danh_sach_di_ung = _trich_danh_sach_di_ung_hop_le(danh_sach_phat_bieu, thong_tin_benh_nhan)
        co_dia_duoc_ly = dict(thong_tin_benh_nhan) if isinstance(thong_tin_benh_nhan, dict) else {}
        if danh_sach_di_ung:
            co_dia_duoc_ly["di_ung"] = danh_sach_di_ung
        duoc_ly = ClinicalPharmacovigilanceEngine.kiem_duyet_toan_dien(
            danh_sach_thuoc, co_dia_duoc_ly or None
        )
        dur_c5 = round((time.perf_counter() - t_c5) * 1000, 2)
        so_atc = len((duoc_ly.ganh_nang_da_thuoc or {}).get("trung_nhom_atc") or {})
        chot_kiem_soat.append(AuditCheckpoint(
            ten_chot="Guardrail 5: Kiểm duyệt Dược lý & Tương tác DDI",
            thoi_gian_ms=dur_c5,
            trang_thai="DAT" if duoc_ly.hop_le else "CANH_BAO",
            chi_tiet=(
                f"Phát hiện {len(duoc_ly.canh_bao_ddi)} tương tác, "
                f"{len(duoc_ly.chong_chi_dinh_co_dia)} chống chỉ định, "
                f"{len(getattr(duoc_ly, 'canh_bao_di_ung_cheo', []) or [])} dị ứng chéo, "
                f"{so_atc} trùng nhóm ATC."
            ),
            canh_bao=duoc_ly.giai_trinh_duoc_ly
        ))
        tat_ca_canh_bao.extend(duoc_ly.giai_trinh_duoc_ly)

        # ----------------------------------------------------------------------
        # XUẤT BẢN: Bệnh án 3 phân vùng & HL7 FHIR Bundle (Trụ cột 2)
        # ----------------------------------------------------------------------
        vb_benh_an, _ = sinh_benh_an.sinh(danh_sach_phat_bieu, ly_do_chan=xac_nhan_map)

        # Bóc tách các phân vùng từ văn bản bệnh án (không khởi tạo trùng lặp CẦN XÁC NHẬN trước khi tách)
        ban_nhap_dict = {
            "CHẨN ĐOÁN": "",
            "TIỀN SỬ BỆNH": "",
            "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI": "",
            "DỊ ỨNG": "",
            "THUỐC ĐANG DÙNG": "",
            "BỆNH SỬ HIỆN TẠI": "",
            "KHÁM LÂM SÀNG": "",
            "KẾ HOẠCH ĐIỀU TRỊ": "",
            "CẦN XÁC NHẬN": "",
        }
        parts = [p.strip() for p in vb_benh_an.split("\n\n") if p.strip()]
        curr_muc = None
        for p in parts:
            if p in ban_nhap_dict or p in sinh_benh_an.THU_TU_MUC:
                curr_muc = p
                if curr_muc not in ban_nhap_dict:
                    ban_nhap_dict[curr_muc] = ""
            elif curr_muc and curr_muc in ban_nhap_dict:
                if ban_nhap_dict[curr_muc]:
                    ban_nhap_dict[curr_muc] += "\n" + p
                else:
                    ban_nhap_dict[curr_muc] = p

        # Chỉ nối thêm các mục tổng hợp không gắn với ID mệnh đề (ví dụ: ASR_THUOC_*) để không nhân đôi CẦN XÁC NHẬN
        tap_id_pb = {getattr(pb_item, "id", None) for pb_item in danh_sach_phat_bieu}
        muc_xac_nhan_phu = [f"- {ly}" for k_id, ly in xac_nhan_map.items() if k_id not in tap_id_pb]
        if muc_xac_nhan_phu:
            phu_text = "\n".join(muc_xac_nhan_phu)
            if ban_nhap_dict["CẦN XÁC NHẬN"]:
                ban_nhap_dict["CẦN XÁC NHẬN"] += "\n" + phu_text
            else:
                ban_nhap_dict["CẦN XÁC NHẬN"] = phu_text

        # Xuất HL7 FHIR Document Bundle
        fhir_bundle = FHIRExporter.xuat_fhir_bundle(
            ma_ca,
            ban_nhap_dict,
            thong_tin_benh_nhan,
            danh_sach_phat_bieu,
            du_lieu_xet_nghiem=du_lieu_xet_nghiem,
        )

        # ----------------------------------------------------------------------
        # CHỐT 6: Đối soát Cận lâm sàng, Quỹ đạo Lâm sàng & 9 Thang điểm Nguy cơ Quốc tế
        # ----------------------------------------------------------------------
        t_c6 = time.perf_counter()
        du_lieu_cls = _gop_du_lieu_can_lam_sang(thong_tin_benh_nhan, du_lieu_xet_nghiem)
        kq_cls = None
        cb_cls: List[str] = []

        if du_lieu_cls:
            kq_cls = ParaclinicalCorrelator.phan_tich_xet_nghiem(
                du_lieu_cls, hoi_thoai, ban_nhap_dict.get("CHẨN ĐOÁN", "")
            )
            if kq_cls.bao_dong_do_khan_cap:
                cb_cls.extend(kq_cls.bao_dong_do_khan_cap)
            if kq_cls.canh_bao_bat_tuong_dong:
                cb_cls.extend(kq_cls.canh_bao_bat_tuong_dong)

        thang_diem_dict = _tinh_thang_diem_lam_sang(
            hoi_thoai=hoi_thoai,
            chan_doan=ban_nhap_dict.get("CHẨN ĐOÁN", ""),
            thong_tin_benh_nhan=thong_tin_benh_nhan,
            du_lieu_cls=du_lieu_cls,
        )

        ls_kham = lich_su_lan_kham
        if ls_kham is None and isinstance(thong_tin_benh_nhan, dict):
            ls_kham = thong_tin_benh_nhan.get("lich_su_lan_kham")
        kq_quy_dao: Optional[Dict[str, Any]] = None
        if isinstance(ls_kham, list) and len(ls_kham) > 0:
            lan_hien_tai_qd: Dict[str, Any] = {
                "ngay_kham": now_str,
                "xet_nghiem": du_lieu_cls,
                "danh_sach_thuoc": danh_sach_thuoc,
            }
            if isinstance(thong_tin_benh_nhan, dict):
                if thong_tin_benh_nhan.get("tuoi") is not None:
                    lan_hien_tai_qd["tuoi"] = thong_tin_benh_nhan.get("tuoi")
                if thong_tin_benh_nhan.get("gioi_tinh") is not None:
                    lan_hien_tai_qd["gioi_tinh"] = thong_tin_benh_nhan.get("gioi_tinh")
                if thong_tin_benh_nhan.get("la_nu") is not None:
                    lan_hien_tai_qd["la_nu"] = thong_tin_benh_nhan.get("la_nu")
                if thong_tin_benh_nhan.get("ngay_kham") is not None:
                    lan_hien_tai_qd["ngay_kham"] = thong_tin_benh_nhan.get("ngay_kham")
            kq_quy_dao = phan_tich_quy_dao_lam_sang(ls_kham, lan_hien_tai_qd)
            if kq_quy_dao.get("kdigo_aki"):
                aki = kq_quy_dao["kdigo_aki"]
                cb_cls.append(f"[{aki['muc_do']}] {aki['ten_giai_doan']}: {aki['khuyen_cao']}")
            for cb_td in kq_quy_dao.get("canh_bao_thuoc_doc") or []:
                cb_cls.append(f"[{cb_td['muc_do']}] {cb_td['loai_canh_bao']}: {cb_td['mo_ta']}")

        dur_c6 = round((time.perf_counter() - t_c6) * 1000, 2)
        co_aki_hoac_thuoc_doc = bool(
            kq_quy_dao and (
                kq_quy_dao.get("kdigo_aki")
                or any(c.get("muc_do") in ("CAO", "NGUY_KICH") for c in (kq_quy_dao.get("canh_bao_thuoc_doc") or []))
            )
        )
        if du_lieu_cls or kq_quy_dao is not None:
            chot_kiem_soat.append(AuditCheckpoint(
                ten_chot="Chốt 6: Đối soát Cận lâm sàng & Thang điểm lâm sàng",
                thoi_gian_ms=dur_c6,
                trang_thai="CANH_BAO" if ((kq_cls and kq_cls.co_gia_tri_nguy_kich) or co_aki_hoac_thuoc_doc) else "DAT",
                chi_tiet=(
                    f"Đã đối soát {len(kq_cls.danh_sach_chi_so) if kq_cls else 0} chỉ số xét nghiệm"
                    + (f", phân tích quỹ đạo {len(ls_kham)} lần khám trước." if kq_quy_dao is not None else ".")
                ),
                canh_bao=cb_cls
            ))
            tat_ca_canh_bao.extend(cb_cls)

        # ----------------------------------------------------------------------
        # CHỐT 7: Hiệu chỉnh Liều theo Thận/Gan & Bản Dặn dò Bệnh nhân
        # ----------------------------------------------------------------------
        t_c7 = time.perf_counter()
        kq_hieu_chinh = kiem_tra_hieu_chinh_lieu(
            danh_sach_thuoc=danh_sach_thuoc,
            ket_qua_xet_nghiem=du_lieu_cls,
            thong_tin_benh_nhan=thong_tin_benh_nhan
        )
        cb_hieu_chinh = [
            f"[{c['muc_do']}] {c['thuoc']}: {c['khuyen_cao']} - {c['lieu_de_xuat']}"
            for c in kq_hieu_chinh.get("canh_bao_hieu_chinh_than", []) + kq_hieu_chinh.get("canh_bao_hieu_chinh_gan", [])
        ]
        
        # Sinh bản dặn dò bệnh nhân
        ten_bn = (thong_tin_benh_nhan.get("ten") or thong_tin_benh_nhan.get("ho_ten") or "Người bệnh") if thong_tin_benh_nhan else "Người bệnh"
        chan_doan_chinh = ban_nhap_dict.get("CHẨN ĐOÁN", "") or "Khám và điều trị ngoại trú"
        ban_dan_do = sinh_ban_dan_do_benh_nhan(
            ten_benh_nhan=ten_bn,
            chan_doan=chan_doan_chinh,
            danh_sach_thuoc=danh_sach_thuoc,
            canh_bao_them=[c["huong_dan_dung"] for c in kq_hieu_chinh.get("huong_dan_tuong_tac_thuc_pham", [])]
        )
        
        dur_c7 = round((time.perf_counter() - t_c7) * 1000, 2)
        chot_kiem_soat.append(AuditCheckpoint(
            ten_chot="Chốt 7: Hiệu chỉnh Liều Dược lâm sàng & Dặn dò Người bệnh",
            thoi_gian_ms=dur_c7,
            trang_thai="CANH_BAO" if kq_hieu_chinh.get("co_canh_bao_critical") else "DAT",
            chi_tiet=f"Đã rà soát {len(danh_sach_thuoc)} thuốc, sinh bản dặn dò 6 mục.",
            canh_bao=cb_hieu_chinh
        ))
        tat_ca_canh_bao.extend(cb_hieu_chinh)

        # ----------------------------------------------------------------------
        # CHỐT 8: Trợ lý Phát hiện Khoảng trống & Gợi ý Lâm sàng SOCRATES
        # ----------------------------------------------------------------------
        t_c8 = time.perf_counter()
        kq_tro_ly = ActiveClinicalClarificationAgent.phan_tich_khoang_trong(
            hoi_thoai=hoi_thoai,
            danh_sach_phat_bieu=danh_sach_phat_bieu,
            thong_tin_benh_nhan=thong_tin_benh_nhan
        )
        dur_c8 = round((time.perf_counter() - t_c8) * 1000, 2)
        cb_tro_ly = [f"[{g.muc_do_uu_tien}] {g.chu_de}: {g.khoang_trong}" for g in kq_tro_ly.danh_sach_goi_y]
        chot_kiem_soat.append(AuditCheckpoint(
            ten_chot="Chốt 8: Trợ lý Gợi ý Câu hỏi Lâm sàng SOCRATES",
            thoi_gian_ms=dur_c8,
            trang_thai="CANH_BAO" if kq_tro_ly.tong_so_khoang_trong > 0 else "DAT",
            chi_tiet=f"Đã rà soát SOCRATES, phát hiện {kq_tro_ly.tong_so_khoang_trong} khoảng trống bệnh sử.",
            canh_bao=cb_tro_ly
        ))
        tat_ca_canh_bao.extend(cb_tro_ly)

        t_tong = round((time.perf_counter() - t0) * 1000, 2)

        # Tạo dấu vân tay SHA-256 để đối chiếu nội dung. Đây không phải chữ ký số;
        # cần lưu giá trị ở nơi tin cậy và xác minh riêng để phát hiện thay đổi.
        content_for_hash = f"{ma_ca}:{now_str}:{vb_benh_an}:{json.dumps(fhir_bundle, sort_keys=True)}"
        sha256_sig = hashlib.sha256(content_for_hash.encode("utf-8")).hexdigest()

        co_nguy_co_nghiem_trong = (
            not duoc_ly.hop_le or
            len(duoc_ly.chong_chi_dinh_co_dia) > 0 or
            len(duoc_ly.canh_bao_ddi) > 0 or
            (kq_cls and kq_cls.co_gia_tri_nguy_kich) or
            kq_hieu_chinh.get("co_canh_bao_critical", False) or
            co_aki_hoac_thuoc_doc
        )

        audit_record = AuditTrailRecord(
            ma_ca=ma_ca,
            thoi_gian_khoi_tao=now_str,
            tong_thoi_gian_ms=t_tong,
            chu_ky_bam_sha256=sha256_sig,
            cac_chot_kiem_soat=chot_kiem_soat,
            tong_so_canh_bao=len(tat_ca_canh_bao),
            an_toan_lam_sang=not co_nguy_co_nghiem_trong
        )

        return KetQuaDieuPhoi(
            ma_ca=ma_ca,
            ban_nhap_3_phan_vung=ban_nhap_dict,
            fhir_bundle=fhir_bundle,
            danh_gia_rui_ro=danh_gia_rr,
            kiem_duyet_duoc_ly=duoc_ly,
            audit_trail=audit_record,
            doi_soat_can_lam_sang=kq_cls,
            thang_diem_nguy_co=thang_diem_dict,
            hieu_chinh_lieu=kq_hieu_chinh,
            ban_dan_do_benh_nhan=ban_dan_do,
            hoi_thoai_da_khu_dinh_danh=ban_sao_an_danh.van_ban_da_an_danh,
            tro_ly_lam_sang=asdict(kq_tro_ly),
            quy_dao_lam_sang=kq_quy_dao,
        )


# ─── _ep_phat_bieu_nhanh() — Đổi danh sách dict từ web thành các mệnh đề hợp lệ ───────
# Nhận dict hoặc PhatBieu, ép kiểu và gán giá trị mặc định.
def _ep_phat_bieu_nhanh(raw_list: Any) -> List[PhatBieu]:
    """Chuyển danh sách dict/PhatBieu từ Web hoặc Python thành List[PhatBieu] hợp lệ."""
    from src.duong_ong.b1_cau_truc_menh_de import (
        DO_CHAC_CHAN,
        THOI_GIAN,
        TINH_HUONG,
        TRANG_THAI,
        _chuan_hoa_nguoi_noi,
        _doc_hanh_vi,
        _doc_thuoc,
    )
    if not isinstance(raw_list, list):
        return []
    ra: List[PhatBieu] = []
    for idx, item in enumerate(raw_list):
        if isinstance(item, PhatBieu):
            ra.append(item)
            continue
        if not isinstance(item, dict):
            continue
        pb_id = item.get("id")
        if pb_id is None:
            pb_id = idx
        thuoc_val = item.get("thuoc")
        if isinstance(thuoc_val, str) and thuoc_val.strip():
            thuoc_val = {"ten": thuoc_val.strip()}
        elif isinstance(thuoc_val, dict):
            thuoc_val = _doc_thuoc({"thuoc": thuoc_val})
        else:
            thuoc_val = None
        bang_chung = item.get("bang_chung")
        if bang_chung is None:
            bang_chung = item.get("luot_thoai") or []
        if not isinstance(bang_chung, list):
            bang_chung = [bang_chung]
        bc_ints = [int(x) for x in bang_chung if isinstance(x, (int, float)) or str(x).isdigit()]
        if not bc_ints:
            bc_ints = [1]
        trich_dan = item.get("trich_dan") or []
        if isinstance(trich_dan, str):
            trich_dan = [trich_dan]
        do_chac_chan = str(item.get("do_chac_chan") or "chắc chắn")
        if do_chac_chan not in DO_CHAC_CHAN:
            do_chac_chan = "chắc chắn"
        tinh_huong = str(item.get("tinh_huong") or "thực tế")
        if tinh_huong not in TINH_HUONG:
            tinh_huong = "thực tế"
        trang_thai = str(item.get("trang_thai") or "còn hiệu lực")
        if trang_thai not in TRANG_THAI:
            trang_thai = "còn hiệu lực"
        thoi_gian = str(item.get("thoi_gian_su_kien") or "chưa rõ")
        if thoi_gian not in THOI_GIAN:
            thoi_gian = "chưa rõ"
        quan_he = item.get("quan_he")
        quan_he_voi = item.get("quan_he_voi")
        if not quan_he or quan_he_voi is None:
            quan_he, quan_he_voi = None, None
        ra.append(PhatBieu(
            id=int(pb_id),
            nguoi_noi=_chuan_hoa_nguoi_noi(item.get("nguoi_noi") or item.get("ten_chu_the") or "bệnh nhân"),
            chu_the_id=int(item.get("chu_the_id") if item.get("chu_the_id") is not None else 0),
            noi_dung=str(item.get("noi_dung") or ""),
            do_chac_chan=do_chac_chan,
            phu_dinh=bool(item.get("phu_dinh", False)),
            tinh_huong=tinh_huong,
            moc_thoi_gian=item.get("moc_thoi_gian"),
            bang_chung=bc_ints,
            trich_dan=[str(x) for x in trich_dan if x is not None],
            thuoc=thuoc_val,
            trang_thai=trang_thai,
            ten_chu_the=str(item.get("ten_chu_the") or ""),
            hanh_vi=_doc_hanh_vi(item),
            quan_he=quan_he,
            quan_he_voi=quan_he_voi,
            thoi_gian_su_kien=thoi_gian,
        ))
    return ra


# ─── _gop_chuoi_khong_trung() — Gộp nhiều danh sách chuỗi, bỏ trùng ───────────────────
# Giữ thứ tự xuất hiện đầu tiên.
def _gop_chuoi_khong_trung(*nguon_lists: Any) -> List[str]:
    ra: List[str] = []
    da_co = set()
    for src in nguon_lists:
        if not src:
            continue
        if isinstance(src, str):
            items = [x.strip() for x in re.split(r"[,;\n]+", src) if x.strip()]
        elif isinstance(src, (list, tuple, set)):
            items = list(src)
        else:
            continue
        for x in items:
            if isinstance(x, dict):
                s = str(x.get("ten") or x.get("hoat_chat") or x.get("name") or x.get("noi_dung") or "").strip()
            else:
                s = str(x).strip() if x is not None else ""
            if s and s.lower() not in da_co:
                da_co.add(s.lower())
                ra.append(s)
    return ra


# ═══ tai_kiem_tra_nhanh() — Tái kiểm tra nhanh khi bác sĩ sửa đơn hoặc bệnh án ════════
# Xác định, không dùng mô hình AI, dưới 50 ms; chạy khoá bằng chứng, cổng rủi ro và các
# động cơ M1.
def tai_kiem_tra_nhanh(payload: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
    """Tái kiểm tra nhanh xác định 100% (không LLM, <50ms) khi bác sĩ chỉnh sửa đơn/bệnh án.

    Chạy Bước 4-5 (`khoa_bang_chung`, `cong_rui_ro`, `canh_bao.gop` phân tầng 3 mức) +
    toàn bộ động cơ M1 (`di_ung_cheo`, `duoc_ly_lam_sang`, `can_lam_sang`, 9 thang điểm,
    `hieu_chinh_lieu`, `quy_dao_lam_sang`).
    """
    t0 = time.perf_counter()
    if payload is None:
        data = kwargs
    elif kwargs:
        data = {**payload, **kwargs}
    else:
        data = payload if isinstance(payload, dict) else {}

    hoi_thoai = str(
        data.get("hoi_thoai")
        or data.get("transcript")
        or data.get("input")
        or ""
    )
    raw_ps = data.get("phat_bieu") if data.get("phat_bieu") is not None else data.get("propositions")
    ps = _ep_phat_bieu_nhanh(raw_ps)

    thong_tin_bn = chuan_hoa_thong_tin_benh_nhan(data.get("thong_tin_benh_nhan") or {}) or {}
    raw_xn = (
        data.get("du_lieu_xet_nghiem")
        if data.get("du_lieu_xet_nghiem") is not None
        else (data.get("xet_nghiem") if data.get("xet_nghiem") is not None else data.get("labs"))
    )
    du_lieu_cls = _gop_du_lieu_can_lam_sang(thong_tin_bn, raw_xn if isinstance(raw_xn, dict) else None)

    thuoc_tu_ps = _trich_danh_sach_thuoc_hop_le(ps) if ps else []
    di_ung_tu_ps = _trich_danh_sach_di_ung_hop_le(ps, thong_tin_bn)
    ds_thuoc = _gop_chuoi_khong_trung(data.get("danh_sach_thuoc"), thuoc_tu_ps)
    ds_di_ung = _gop_chuoi_khong_trung(data.get("danh_sach_di_ung"), di_ung_tu_ps)

    # Bước 4-5: Khóa bằng chứng, Cổng rủi ro & Lớp cảnh báo + Phân tầng 3 mức
    kk = None
    danh_gia_rr = []
    cb_dict = None
    if ps:
        kk = khoa_bang_chung.khoa_ca(ps, hoi_thoai)
        danh_gia_rr = cong_rui_ro.cham(ps, kk["ket_qua"], thong_tin_bn)
        cb_raw = _canh_bao_gop.chay(ps, hoi_thoai, kk=kk)
        cb_dict = _canh_bao_gop.to_dict(cb_raw)

    # Dị ứng chéo & Dược lý lâm sàng
    co_dia_duoc_ly = dict(thong_tin_bn)
    if ds_di_ung:
        co_dia_duoc_ly["di_ung"] = ds_di_ung
    kq_di_ung_cheo = kiem_tra_di_ung_cheo(ds_di_ung, ds_thuoc) if (ds_di_ung and ds_thuoc) else []
    kq_duoc_ly = ClinicalPharmacovigilanceEngine.kiem_duyet_toan_dien(ds_thuoc, co_dia_duoc_ly or None)

    # Cận lâm sàng, 9 thang điểm, Hiệu chỉnh liều, Quỹ đạo lâm sàng
    chan_doan = str(data.get("chan_doan") or "")
    if not chan_doan and ps:
        cd_items = []
        for p in ps:
            if getattr(p, "chu_the_id", 0) == 0 and not getattr(p, "phu_dinh", False):
                muc_p, _ = sinh_benh_an._muc_cho(p.to_dict(), 0)
                if muc_p == "CHẨN ĐOÁN":
                    cd_items.append(p.noi_dung)
        chan_doan = "; ".join(cd_items)

    kq_cls = (
        ParaclinicalCorrelator.phan_tich_xet_nghiem(du_lieu_cls, hoi_thoai, chan_doan)
        if du_lieu_cls else None
    )
    thang_diem = _tinh_thang_diem_lam_sang(
        hoi_thoai=hoi_thoai,
        chan_doan=chan_doan,
        thong_tin_benh_nhan=thong_tin_bn,
        du_lieu_cls=du_lieu_cls,
    )
    kq_hieu_chinh = (
        kiem_tra_hieu_chinh_lieu(ds_thuoc, du_lieu_cls, thong_tin_bn)
        if (ds_thuoc or du_lieu_cls) else None
    )

    ls_kham = data.get("lich_su_lan_kham")
    if ls_kham is None:
        ls_kham = thong_tin_bn.get("lich_su_lan_kham")
    kq_quy_dao = None
    if isinstance(ls_kham, list) and len(ls_kham) > 0:
        hien_tai_qd: Dict[str, Any] = {
            "xet_nghiem": du_lieu_cls,
            "danh_sach_thuoc": ds_thuoc,
        }
        for k_copy in ("tuoi", "gioi_tinh", "la_nu", "ngay_kham", "thoi_gian", "timestamp"):
            if thong_tin_bn.get(k_copy) is not None:
                hien_tai_qd[k_copy] = thong_tin_bn.get(k_copy)
        if data.get("ngay_kham") is not None:
            hien_tai_qd["ngay_kham"] = data.get("ngay_kham")
        kq_quy_dao = phan_tich_quy_dao_lam_sang(ls_kham, hien_tai_qd)

    co_chan_ngay_cb = bool(cb_dict and (cb_dict.get("phan_tang") or {}).get(_canh_bao_gop.TANG_CHAN_NGAY))
    co_chan_di_ung_cheo = any(x.get("muc_do") == "CHONG_CHI_DINH" for x in kq_di_ung_cheo)
    co_chan_quy_dao = bool(
        kq_quy_dao and (
            kq_quy_dao.get("kdigo_aki")
            or any(c.get("muc_do") in ("CAO", "NGUY_KICH") for c in (kq_quy_dao.get("canh_bao_thuoc_doc") or []))
        )
    )
    hop_le_lam_sang = (
        kq_duoc_ly.hop_le
        and not co_chan_di_ung_cheo
        and not co_chan_ngay_cb
        and not (kq_cls and kq_cls.co_gia_tri_nguy_kich)
        and not (kq_hieu_chinh and kq_hieu_chinh.get("co_canh_bao_critical", False))
        and not co_chan_quy_dao
    )

    thoi_gian_ms = round((time.perf_counter() - t0) * 1000, 2)
    return {
        "thoi_gian_ms": thoi_gian_ms,
        "hop_le_lam_sang": hop_le_lam_sang,
        "thong_tin_benh_nhan": thong_tin_bn,
        "danh_sach_thuoc": ds_thuoc,
        "danh_sach_di_ung": ds_di_ung,
        "khoa_bang_chung": [asdict(k) for k in kk["ket_qua"]] if kk else [],
        "cong_rui_ro": [d.to_dict() for d in danh_gia_rr],
        "canh_bao": cb_dict,
        "di_ung_cheo": kq_di_ung_cheo,
        "duoc_ly": asdict(kq_duoc_ly),
        "doi_soat_can_lam_sang": asdict(kq_cls) if kq_cls else None,
        "thang_diem_nguy_co": thang_diem,
        "hieu_chinh_lieu": kq_hieu_chinh,
        "quy_dao_lam_sang": kq_quy_dao,
    }
