# -*- coding: utf-8 -*-
"""Unit tests cho Bộ kiểm toán gói XML1–XML5 BHYT (QĐ 130/4210 & TT 20/2022) và FHIR Condition.code."""
import json
import subprocess
import sys

from src.fhir_exporter import FHIRExporter
from src.kiem_toan_xml_bhyt import kiem_toan_goi_xml_bhyt


def _xml1_hop_le(
    ma_benh: str = "I10",
    ma_the: str = "DN4790123456789",
    t_tongchi: float = 500000,
    t_bhtt: float = 400000,
    t_bntt: float = 100000,
    t_bncct: float = 0,
    t_nguonkhac: float = 0,
) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<TONG_HOP>
  <MA_LK>LK_001</MA_LK>
  <MA_BN>BN_001</MA_BN>
  <MA_THE>{ma_the}</MA_THE>
  <MA_DKBD>79001</MA_DKBD>
  <MA_LOAI_KCB>1</MA_LOAI_KCB>
  <MA_BENH>{ma_benh}</MA_BENH>
  <NGAY_VAO>202611260800</NGAY_VAO>
  <NGAY_RA>202611260930</NGAY_RA>
  <MA_BAC_SI>BS001</MA_BAC_SI>
  <T_TONGCHI>{t_tongchi}</T_TONGCHI>
  <T_BHTT>{t_bhtt}</T_BHTT>
  <T_BNTT>{t_bntt}</T_BNTT>
  <T_BNCCT>{t_bncct}</T_BNCCT>
  <T_NGUONKHAC>{t_nguonkhac}</T_NGUONKHAC>
</TONG_HOP>"""


def test_goi_xml_hop_le_khong_loi():
    xml2 = """<CHITIEU_CHITIET_THUOC><DSACH_CHI_TIET_THUOC>
      <CHI_TIET_THUOC>
        <STT>1</STT>
        <MA_THUOC>T001</MA_THUOC>
        <TEN_THUOC>Amlodipine 5mg</TEN_THUOC>
        <DUONG_DUNG>1.01</DUONG_DUNG>
        <SO_LUONG>30</SO_LUONG>
        <DON_GIA>5000</DON_GIA>
        <THANH_TIEN>150000</THANH_TIEN>
      </CHI_TIET_THUOC>
    </DSACH_CHI_TIET_THUOC></CHITIEU_CHITIET_THUOC>"""
    xml3 = """<CHITIEU_CHITIET_DVKT_VTYT><DSACH_CHI_TIET_DVKT>
      <CHI_TIET_DVKT>
        <STT>1</STT>
        <MA_DICH_VU>01.0001</MA_DICH_VU>
        <TEN_DICH_VU>Khám bệnh ngoại trú</TEN_DICH_VU>
        <SO_LUONG>1</SO_LUONG>
        <DON_GIA>350000</DON_GIA>
        <THANH_TIEN>350000</THANH_TIEN>
        <NGAY_YL>202611260810</NGAY_YL>
      </CHI_TIET_DVKT>
    </DSACH_CHI_TIET_DVKT></CHITIEU_CHITIET_DVKT_VTYT>"""
    xml5 = """<CHITIEU_CHITIET_DIEN_BIEN_BENH><DSACH_CHI_TIET_DIEN_BIEN_BENH>
      <CHI_TIET_DIEN_BIEN_BENH>
        <STT>1</STT>
        <DIEN_BIEN>Tăng huyết áp độ 2, tiếp tục Amlodipine 5mg mỗi sáng.</DIEN_BIEN>
      </CHI_TIET_DIEN_BIEN_BENH>
    </DSACH_CHI_TIET_DIEN_BIEN_BENH></CHITIEU_CHITIET_DIEN_BIEN_BENH>"""

    kq = kiem_toan_goi_xml_bhyt(
        {"XML1": _xml1_hop_le(), "XML2": xml2, "XML3": xml3, "XML5": xml5},
        bang_chung_kham={"transcript": "Bác sĩ kê Amlodipine 5mg uống mỗi sáng."},
    )
    assert kq["hop_le"] is True
    assert kq["tong_tien_de_nghi"] == 500000.0
    assert kq["tong_nguy_co_xuat_toan"] == 0.0
    assert kq["loi_cau_truc"] == []
    assert kq["vi_pham_tt20"] == []
    assert kq["thieu_bang_chung_k1_k7"] == []


def test_xml_hong_cu_phap_khong_crash():
    kq = kiem_toan_goi_xml_bhyt({"XML1": "<TONG_HOP><MA_LK>123", "XML2": "<broken"})
    assert kq["hop_le"] is False
    assert any(l["ma_loi"] == "xml_khong_hop_le" and l["loai"] == "XML1" for l in kq["loi_cau_truc"])
    assert any(l["ma_loi"] == "xml_khong_hop_le" and l["loai"] == "XML2" for l in kq["loi_cau_truc"])


def test_kiem_tra_xml1_truong_bat_buoc_va_lech_tai_chinh():
    xml1_sai = """<TONG_HOP>
      <MA_LK>LK_002</MA_LK>
      <MA_BN>BN_002</MA_BN>
      <MA_THE>INVALID_CARD</MA_THE>
      <MA_DKBD>79001</MA_DKBD>
      <MA_LOAI_KCB>1</MA_LOAI_KCB>
      <MA_BENH>999</MA_BENH>
      <NGAY_VAO>202611260800</NGAY_VAO>
      <NGAY_RA>202611260930</NGAY_RA>
      <T_TONGCHI>1000000</T_TONGCHI>
      <T_BHTT>700000</T_BHTT>
      <T_BNTT>200000</T_BNTT>
      <T_BNCCT>0</T_BNCCT>
      <T_NGUONKHAC>0</T_NGUONKHAC>
    </TONG_HOP>"""

    kq = kiem_toan_goi_xml_bhyt({"XML1": xml1_sai})
    assert kq["hop_le"] is False
    ma_lois = {l["ma_loi"] for l in kq["loi_cau_truc"]}
    assert "thieu_truong_bat_buoc" in ma_lois  # thiếu MA_BAC_SI
    assert "ma_the_khong_hop_le" in ma_lois
    assert "ma_benh_icd10_khong_hop_le" in ma_lois
    assert "lech_tai_chinh_xml1" in ma_lois
    loi_tc = [l for l in kq["loi_cau_truc"] if l["ma_loi"] == "lech_tai_chinh_xml1"][0]
    assert loi_tc["chenh_lech"] == 100000.0


def test_tt20_khang_sinh_han_che_va_ppi_duong_tiem():
    xml2 = """<CHITIEU_CHITIET_THUOC><DSACH_CHI_TIET_THUOC>
      <CHI_TIET_THUOC>
        <STT>1</STT>
        <TEN_THUOC>Meropenem 1g</TEN_THUOC>
        <SO_LUONG>3</SO_LUONG>
        <DON_GIA>450000</DON_GIA>
        <THANH_TIEN>1350000</THANH_TIEN>
      </CHI_TIET_THUOC>
      <CHI_TIET_THUOC>
        <STT>2</STT>
        <TEN_THUOC>Pantoprazole tiêm 40mg</TEN_THUOC>
        <DUONG_DUNG>2.01</DUONG_DUNG>
        <SO_LUONG>2</SO_LUONG>
        <DON_GIA>80000</DON_GIA>
        <THANH_TIEN>160000</THANH_TIEN>
      </CHI_TIET_THUOC>
    </DSACH_CHI_TIET_THUOC></CHITIEU_CHITIET_THUOC>"""
    xml5_mo_ho = """<CHITIEU_CHITIET_DIEN_BIEN_BENH><DSACH_CHI_TIET_DIEN_BIEN_BENH>
      <CHI_TIET_DIEN_BIEN_BENH><STT>1</STT><DIEN_BIEN>Bệnh nhân tỉnh, tiếp xúc tốt.</DIEN_BIEN></CHI_TIET_DIEN_BIEN_BENH>
    </DSACH_CHI_TIET_DIEN_BIEN_BENH></CHITIEU_CHITIET_DIEN_BIEN_BENH>"""

    kq_vi_pham = kiem_toan_goi_xml_bhyt({"XML1": _xml1_hop_le(ma_benh="I10", t_tongchi=1510000, t_bhtt=1510000, t_bntt=0), "XML2": xml2, "XML5": xml5_mo_ho})
    assert kq_vi_pham["hop_le"] is False
    nhoms = {v["nhom"] for v in kq_vi_pham["vi_pham_tt20"]}
    assert nhoms == {"khang_sinh_han_che", "ppi_duong_tiem"}
    assert kq_vi_pham["tong_nguy_co_xuat_toan"] == 1510000.0

    # Đủ căn cứ: J18.9 + xuất huyết tiêu hóa trong XML5
    xml5_du = """<CHITIEU_CHITIET_DIEN_BIEN_BENH><DSACH_CHI_TIET_DIEN_BIEN_BENH>
      <CHI_TIET_DIEN_BIEN_BENH><STT>1</STT><DIEN_BIEN>Viêm phổi nặng, có kháng sinh đồ, xuất huyết tiêu hóa đang nhịn ăn.</DIEN_BIEN></CHI_TIET_DIEN_BIEN_BENH>
    </DSACH_CHI_TIET_DIEN_BIEN_BENH></CHITIEU_CHITIET_DIEN_BIEN_BENH>"""
    kq_dat = kiem_toan_goi_xml_bhyt({"XML1": _xml1_hop_le(ma_benh="J18.9", t_tongchi=1510000, t_bhtt=1510000, t_bntt=0), "XML2": xml2, "XML5": xml5_du})
    assert kq_dat["hop_le"] is True
    assert kq_dat["vi_pham_tt20"] == []


def test_tt20_trung_lap_dvkt_va_thieu_bien_luan_cls():
    xml3 = """<CHITIEU_CHITIET_DVKT_VTYT><DSACH_CHI_TIET_DVKT>
      <CHI_TIET_DVKT>
        <STT>1</STT>
        <MA_DICH_VU>18.0010</MA_DICH_VU>
        <TEN_DICH_VU>Chụp MRI sọ não</TEN_DICH_VU>
        <SO_LUONG>1</SO_LUONG>
        <DON_GIA>1800000</DON_GIA>
        <THANH_TIEN>1800000</THANH_TIEN>
        <NGAY_YL>202611260815</NGAY_YL>
      </CHI_TIET_DVKT>
      <CHI_TIET_DVKT>
        <STT>2</STT>
        <MA_DICH_VU>03.0055</MA_DICH_VU>
        <TEN_DICH_VU>Định lượng Troponin T</TEN_DICH_VU>
        <SO_LUONG>1</SO_LUONG>
        <DON_GIA>250000</DON_GIA>
        <THANH_TIEN>250000</THANH_TIEN>
        <NGAY_YL>202611260820</NGAY_YL>
      </CHI_TIET_DVKT>
      <CHI_TIET_DVKT>
        <STT>3</STT>
        <MA_DICH_VU>03.0055</MA_DICH_VU>
        <TEN_DICH_VU>Định lượng Troponin T</TEN_DICH_VU>
        <SO_LUONG>1</SO_LUONG>
        <DON_GIA>250000</DON_GIA>
        <THANH_TIEN>250000</THANH_TIEN>
        <NGAY_YL>202611261020</NGAY_YL>
      </CHI_TIET_DVKT>
    </DSACH_CHI_TIET_DVKT></CHITIEU_CHITIET_DVKT_VTYT>"""
    xml5 = """<CHITIEU_CHITIET_DIEN_BIEN_BENH><DSACH_CHI_TIET_DIEN_BIEN_BENH>
      <CHI_TIET_DIEN_BIEN_BENH><STT>1</STT><DIEN_BIEN>Khám sức khỏe tổng quát.</DIEN_BIEN></CHI_TIET_DIEN_BIEN_BENH>
    </DSACH_CHI_TIET_DIEN_BIEN_BENH></CHITIEU_CHITIET_DIEN_BIEN_BENH>"""

    kq = kiem_toan_goi_xml_bhyt({"XML1": _xml1_hop_le(t_tongchi=2300000, t_bhtt=2300000, t_bntt=0), "XML3": xml3, "XML5": xml5})
    assert kq["hop_le"] is False
    nhoms = [v["nhom"] for v in kq["vi_pham_tt20"]]
    assert "thieu_bien_luan_cls" in nhoms
    assert "trung_lap_dvkt" in nhoms
    assert kq["tong_nguy_co_xuat_toan"] == 2300000.0


def test_doi_soat_bang_chung_k1_k7():
    xml2 = """<CHITIEU_CHITIET_THUOC><DSACH_CHI_TIET_THUOC>
      <CHI_TIET_THUOC>
        <STT>1</STT>
        <TEN_THUOC>Atorvastatin 20mg</TEN_THUOC>
        <THANH_TIEN>120000</THANH_TIEN>
      </CHI_TIET_THUOC>
    </DSACH_CHI_TIET_THUOC></CHITIEU_CHITIET_THUOC>"""
    kq = kiem_toan_goi_xml_bhyt(
        {"XML1": _xml1_hop_le(t_tongchi=120000, t_bhtt=120000, t_bntt=0), "XML2": xml2},
        bang_chung_kham={
            "propositions": [
                {"chu_the_id": 0, "phu_dinh": False, "noi_dung": "Bệnh nhân tăng huyết áp uống Amlodipine 5mg"},
            ],
            "transcript": "Huyết áp 140/90 mmHg, uống Amlodipine 5mg.",
        },
    )
    assert kq["hop_le"] is False
    assert len(kq["thieu_bang_chung_k1_k7"]) == 1
    assert kq["thieu_bang_chung_k1_k7"][0]["ten"] == "Atorvastatin 20mg"
    assert kq["tong_nguy_co_xuat_toan"] == 120000.0


def test_cli_audit_stdin_json():
    payload = json.dumps({"xml_files": {"XML1": _xml1_hop_le()}})
    proc = subprocess.run(
        [sys.executable, "-m", "src.kiem_toan_xml_bhyt", "--audit"],
        input=payload,
        text=True,
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    data = json.loads(proc.stdout)
    assert data["hop_le"] is True
    assert data["tong_tien_de_nghi"] == 500000.0


def test_fhir_condition_coding_luon_co_ma_icd10():
    bundle = FHIRExporter.xuat_fhir_bundle(
        "ca_fhir_icd",
        {
            "CHẨN ĐOÁN": "Tăng huyết áp vô căn [ICD-10: I10]",
            "TIỀN SỬ BỆNH": "Viêm phế quản mạn trước đây",
        },
    )
    conditions = [e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Condition"]
    assert len(conditions) == 2
    main_cond = [c for c in conditions if "Tăng huyết áp" in c["code"]["text"]][0]
    assert main_cond["code"]["coding"][0]["code"] == "I10"

    hist_cond = [c for c in conditions if "Viêm phế quản" in c["code"]["text"]][0]
    assert hist_cond["code"]["coding"][0]["code"] == "J20.9"

    # Trường hợp không khớp từ điển -> fallback R69, không bao giờ bỏ trống code
    bundle_fallback = FHIRExporter.xuat_fhir_bundle("ca_fhir_fb", {"CHẨN ĐOÁN": "Theo dõi triệu chứng chưa rõ"})
    fb_cond = [e["resource"] for e in bundle_fallback["entry"] if e["resource"]["resourceType"] == "Condition"][0]
    assert fb_cond["code"]["coding"][0]["code"] == "R69"
