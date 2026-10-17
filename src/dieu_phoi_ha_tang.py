# -*- coding: utf-8 -*-
"""Trụ cột 4: Hạ tầng Điều phối Luồng Toàn diện & Ghi vết Kiểm toán (End-to-End Orchestrator & Audit Trail).

Hạ tầng thống nhất kết nối toàn bộ các tầng:
  Đầu vào -> ASR Guardrail -> Speaker Guardrail -> Extraction -> Dialogue Act Guardrail ->
  Evidence Lock -> Pharmacovigilance DDI Gate -> Asymmetric Risk Gate -> Output (3 Partitions + HL7 FHIR Bundle).
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Tuple

from src.guardrails import (
    ASRQualityGuardrail,
    SpeakerConsistencyGuardrail,
    DialogueActGuardrail,
    EvidenceIntegrityGuardrail,
    ClinicalSafetyGuardrail
)
from src.duoc_ly_lam_sang import ClinicalPharmacovigilanceEngine
from src.fhir_exporter import FHIRExporter
from src import cong_rui_ro
from src import khoa_bang_chung
from src import sinh_benh_an
from src.phat_bieu import PhatBieu


from src.can_lam_sang import ParaclinicalCorrelator
from src.thang_diem_lam_sang import ClinicalRiskScoringEngine
from src.hieu_chinh_lieu import kiem_tra_hieu_chinh_lieu
from src.dan_do_benh_nhan import sinh_ban_dan_do_benh_nhan


@dataclass
class AuditCheckpoint:
    ten_chot: str
    thoi_gian_ms: float
    trang_thai: str               # "DAT" | "CANH_BAO" | "CHAN"
    chi_tiet: str
    canh_bao: List[str] = field(default_factory=list)


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


class MediTracePipelineOrchestrator:
    """Bộ điều phối hạ tầng trung tâm cho MediTrace Sentinel."""

    @classmethod
    def xu_ly_ca_kham(cls, ma_ca: str, hoi_thoai: str,
                      danh_sach_phat_bieu: List[PhatBieu],
                      thong_tin_benh_nhan: Optional[Dict[str, Any]] = None,
                      du_lieu_xet_nghiem: Optional[Dict[str, Any]] = None) -> KetQuaDieuPhoi:
        """Thực thi toàn bộ chu trình xử lý end-to-end với đầy đủ 5 lớp guardrails và audit logging."""
        t0 = time.perf_counter()
        now_str = datetime.now(timezone.utc).isoformat()
        chot_kiem_soat: List[AuditCheckpoint] = []
        tat_ca_canh_bao: List[str] = []

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
        xac_nhan_map = cong_rui_ro.dua_sang_xac_nhan(danh_gia_rr)

        # BỔ SUNG QUY TẮC AN TOÀN DƯỢC THƯ ASR (HUMAN-IN-THE-LOOP):
        # Mọi tên thuốc do ASR nhận diện từ âm vị dân gian hoặc có thể nghe sai ('a móc', 'ô mê'...)
        # BẮT BUỘC BÔI ĐỎ và ĐẨY SANG MỤC "CẦN BÁC SĨ XÁC NHẬN", cấm tự ý gán vào đơn thuốc.
        if res_asr.goi_y:
            for idx_g, (am_vi, chuan) in enumerate(res_asr.goi_y.items()):
                khoa_id = f"ASR_THUOC_{idx_g + 1}"
                xac_nhan_map[khoa_id] = (
                    f"[BÔI ĐỎ - CẦN BÁC SĨ XÁC NHẬN TÊN THUỐC]: Tín hiệu ASR ghi nhận âm vị '{am_vi}' "
                    f"-> Hệ thống gợi ý '{chuan.capitalize()}'. "
                    f"Do tạp âm phòng khám/phát âm không chuẩn, hệ thống CẤM tự ý đưa vào đơn. Bác sĩ cần xác nhận đúng hay không."
                )

        dur_c4 = round((time.perf_counter() - t_c4) * 1000, 2)
        chot_kiem_soat.append(AuditCheckpoint(
            ten_chot="Tầng Khóa căn cứ & Cổng Rủi ro lâm sàng",
            thoi_gian_ms=dur_c4,
            trang_thai="DAT" if not kq_khoa.get("co_loi") else "CANH_BAO",
            chi_tiet=f"{len(xac_nhan_map)} mục chuyển sang Cần xác nhận.",
            canh_bao=[f"Chuyển ID {i}: {ly}" for i, ly in xac_nhan_map.items()]
        ))

        # ----------------------------------------------------------------------
        # CHỐT 5: Tầng Kiểm duyệt Dược lý Lâm sàng Nâng cao (Trụ cột 1)
        # ----------------------------------------------------------------------
        t_c5 = time.perf_counter()
        danh_sach_thuoc = [
            p.noi_dung for p in danh_sach_phat_bieu
            if "thuốc" in p.noi_dung.lower() or getattr(p, "muc", "") == "THUỐC ĐANG DÙNG"
        ]
        duoc_ly = ClinicalPharmacovigilanceEngine.kiem_duyet_toan_dien(danh_sach_thuoc, thong_tin_benh_nhan)
        dur_c5 = round((time.perf_counter() - t_c5) * 1000, 2)
        chot_kiem_soat.append(AuditCheckpoint(
            ten_chot="Guardrail 5: Kiểm duyệt Dược lý & Tương tác DDI",
            thoi_gian_ms=dur_c5,
            trang_thai="DAT" if duoc_ly.hop_le else "CANH_BAO",
            chi_tiet=f"Phát hiện {len(duoc_ly.canh_bao_ddi)} tương tác, {len(duoc_ly.chong_chi_dinh_co_dia)} chống chỉ định.",
            canh_bao=duoc_ly.giai_trinh_duoc_ly
        ))
        tat_ca_canh_bao.extend(duoc_ly.giai_trinh_duoc_ly)

        # ----------------------------------------------------------------------
        # XUẤT BẢN: Bệnh án 3 phân vùng & HL7 FHIR Bundle (Trụ cột 2)
        # ----------------------------------------------------------------------
        vb_benh_an, _ = sinh_benh_an.sinh(danh_sach_phat_bieu, ly_do_chan=xac_nhan_map)
        
        # Bóc tách các phân vùng từ văn bản bệnh án
        ban_nhap_dict = {
            "CHẨN ĐOÁN": "",
            "TIỀN SỬ BỆNH": "",
            "DỊ ỨNG": "",
            "THUỐC ĐANG DÙNG": "",
            "BỆNH SỬ HIỆN TẠI": "",
            "KHÁM LÂM SÀNG": "",
            "KẾ HOẠCH ĐIỀU TRỊ": "",
            "CẦN XÁC NHẬN": "\n".join(f"- {ly}" for ly in xac_nhan_map.values())
        }
        parts = [p.strip() for p in vb_benh_an.split("\n\n") if p.strip()]
        curr_muc = None
        for p in parts:
            if p in ban_nhap_dict or p in sinh_benh_an.THU_TU_MUC:
                curr_muc = p
            elif curr_muc and curr_muc in ban_nhap_dict:
                if ban_nhap_dict[curr_muc]:
                    ban_nhap_dict[curr_muc] += "\n" + p
                else:
                    ban_nhap_dict[curr_muc] = p

        # Xuất HL7 FHIR Document Bundle
        fhir_bundle = FHIRExporter.xuat_fhir_bundle(
            ma_ca, ban_nhap_dict, thong_tin_benh_nhan, danh_sach_phat_bieu
        )

        # ----------------------------------------------------------------------
        # CHỐT 6: Đối soát Cận lâm sàng & Thang điểm Nguy cơ Quốc tế
        # ----------------------------------------------------------------------
        t_c6 = time.perf_counter()
        du_lieu_cls = du_lieu_xet_nghiem or (thong_tin_benh_nhan.get("xet_nghiem") if thong_tin_benh_nhan else None) or {}
        kq_cls = None
        thang_diem_dict = {}
        cb_cls = []

        if du_lieu_cls:
            kq_cls = ParaclinicalCorrelator.phan_tich_xet_nghiem(
                du_lieu_cls, hoi_thoai, ban_nhap_dict.get("CHẨN ĐOÁN", "")
            )
            if kq_cls.bao_dong_do_khan_cap:
                cb_cls.extend(kq_cls.bao_dong_do_khan_cap)
            if kq_cls.canh_bao_bat_tuong_dong:
                cb_cls.extend(kq_cls.canh_bao_bat_tuong_dong)

            tuoi = int(thong_tin_benh_nhan.get("tuoi", 0)) if thong_tin_benh_nhan else 0
            if "viêm phổi" in hoi_thoai.lower() or "sốt" in hoi_thoai.lower() or "wbc" in du_lieu_cls:
                curb = ClinicalRiskScoringEngine.tinh_curb65(
                    tuoi=tuoi,
                    urea_mmol_l=du_lieu_cls.get("urea") or du_lieu_cls.get("ure"),
                    van_ban_kham=hoi_thoai
                )
                thang_diem_dict["CURB-65"] = asdict(curb)

        dur_c6 = round((time.perf_counter() - t_c6) * 1000, 2)
        if du_lieu_cls:
            chot_kiem_soat.append(AuditCheckpoint(
                ten_chot="Chốt 6: Đối soát Cận lâm sàng & Thang điểm lâm sàng",
                thoi_gian_ms=dur_c6,
                trang_thai="CANH_BAO" if (kq_cls and kq_cls.co_gia_tri_nguy_kich) else "DAT",
                chi_tiet=f"Đã đối soát {len(kq_cls.danh_sach_chi_so) if kq_cls else 0} chỉ số xét nghiệm.",
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

        t_tong = round((time.perf_counter() - t0) * 1000, 2)

        # Tạo chữ ký băm bảo mật SHA256 cho toàn bộ kết quả để chống can thiệp (Tamper-evident)
        content_for_hash = f"{ma_ca}:{now_str}:{vb_benh_an}:{json.dumps(fhir_bundle, sort_keys=True)}"
        sha256_sig = hashlib.sha256(content_for_hash.encode("utf-8")).hexdigest()

        co_nguy_co_nghiem_trong = (
            len(duoc_ly.chong_chi_dinh_co_dia) > 0 or
            len(duoc_ly.canh_bao_ddi) > 0 or
            (kq_cls and kq_cls.co_gia_tri_nguy_kich) or
            kq_hieu_chinh.get("co_canh_bao_critical", False)
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
            ban_dan_do_benh_nhan=ban_dan_do
        )
