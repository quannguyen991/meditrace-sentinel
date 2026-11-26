# -*- coding: utf-8 -*-
"""Kiểm toán gói hồ sơ BHYT XML1–XML5 trước khi gửi Cổng Giám định BHXH.

Áp dụng 100% quy tắc xác định (deterministic rules), không dùng LLM:
1. Kiểm tra cấu trúc bắt buộc & cân đối tài chính theo QĐ 130/QĐ-BYT & 4210/QĐ-BYT (XML1).
2. Kiểm tra điều kiện thanh toán thuốc/DVKT theo Thông tư 20/2022/TT-BYT (XML2, XML3, XML5):
   - Kháng sinh hạn chế / dự trữ (WHO Watch/Reserve)
   - Thuốc ức chế bơm proton đường tiêm (IV PPI)
   - Trùng lặp dịch vụ kỹ thuật cùng ngày y lệnh (XML3)
   - Thiếu biện luận diễn biến lâm sàng (XML5) cho MRI, CT, Nội soi, Troponin
3. Đối soát chứng cứ lâm sàng K1–K7 (mệnh đề đã xác nhận & lời thoại) với XML2/XML3.
"""
from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET


TRUONG_BAT_BUOC_XML1: Tuple[str, ...] = (
    "MA_LK",
    "MA_BN",
    "MA_THE",
    "MA_DKBD",
    "MA_LOAI_KCB",
    "MA_BENH",
    "NGAY_VAO",
    "NGAY_RA",
    "MA_BAC_SI",
)

MAU_ICD10 = re.compile(r"^[A-Z]\d{2}(?:\.\d{1,2})?$")
MAU_THE_BHYT_15 = re.compile(r"^[A-Z0-9]{15}$")

KHANG_SINH_HAN_CHE: Tuple[str, ...] = (
    "meropenem",
    "imipenem",
    "vancomycin",
    "colistin",
    "linezolid",
    "levofloxacin",
    "ciprofloxacin",
    "cefepime",
)

ICD10_NHIEM_KHUAN_TIEN_TO: Tuple[str, ...] = (
    "J15", "J18", "A41", "N39", "K81", "L03", "A09",
    "J20", "J21", "J44", "K80", "K83", "N10", "N12",
    "M00", "G00", "I33", "A15", "A16", "B95", "B96",
)

TU_KHOA_NHIEM_KHUAN_XML5: Tuple[str, ...] = (
    "kháng sinh đồ",
    "cấy máu",
    "cấy đờm",
    "cấy nước tiểu",
    "vi khuẩn",
    "nhiễm khuẩn",
    "nhiễm trùng",
    "sốc nhiễm khuẩn",
    "sepsis",
    "procalcitonin",
    "pct",
    "crp",
    "bạch cầu",
    "đa kháng",
)

PPI_HOAT_CHAT: Tuple[str, ...] = (
    "omeprazol",
    "omeprazole",
    "pantoprazol",
    "pantoprazole",
    "esomeprazol",
    "esomeprazole",
)

ICD10_XUAT_HUYET_LOET_TIEN_TO: Tuple[str, ...] = (
    "K25", "K26", "K27", "K28", "K92",
)

TU_KHOA_PPI_IV_XML5: Tuple[str, ...] = (
    "xuất huyết tiêu hóa",
    "nôn ra máu",
    "đi ngoài phân đen",
    "loét dạ dày",
    "loét tá tràng",
    "nhịn ăn",
    "npo",
    "không uống được",
    "hậu phẫu",
)

QUY_TAC_CLS_XML5: Tuple[Tuple[str, Tuple[str, ...], Tuple[str, ...], str], ...] = (
    (
        "MRI",
        ("mri", "cộng hưởng từ"),
        (
            "đau đầu", "yếu liệt", "đột quỵ", "chóng mặt", "thoát vị",
            "cột sống", "khớp", "khối u", "chấn thương", "co giật", "tê bì",
            "thiếu máu não", "thần kinh",
        ),
        "Chụp cộng hưởng từ (MRI) chưa có ghi nhận triệu chứng/chỉ định thần kinh, cột sống, khớp hoặc tổn thương khu trú trong XML5.",
    ),
    (
        "CT",
        ("cắt lớp vi tính", "chụp clvt", "ct scanner", "ct scan", "ct ngực", "ct sọ", "ct bụng"),
        (
            "đau đầu", "chấn thương", "đột quỵ", "đau bụng", "khó thở",
            "ho ra máu", "viêm phổi", "tắc ruột", "sỏi", "khối u", "nghi ngờ",
            "xuất huyết",
        ),
        "Chụp cắt lớp vi tính (CT) chưa có ghi nhận triệu chứng cấp cứu hoặc nghi ngờ tổn thương thực thể trong XML5.",
    ),
    (
        "NOI_SOI",
        ("nội soi",),
        (
            "đau thượng vị", "ợ hơi", "ợ chua", "trào ngược", "nôn",
            "xuất huyết", "nuốt nghẹn", "tiêu chảy", "đi ngoài", "viêm loét",
            "dạ dày", "đại tràng", "phân đen",
        ),
        "Thủ thuật nội soi chưa có triệu chứng tiêu hóa/tai mũi họng tương ứng được ghi nhận trong XML5.",
    ),
    (
        "TROPONIN",
        ("troponin",),
        (
            "đau ngực", "đau thắt ngực", "khó thở", "hồi hộp", "nhồi máu",
            "mạch vành", "hội chứng vành", "tăng huyết áp cấp cứu", "ngất",
        ),
        "Xét nghiệm Troponin chưa có ghi nhận đau ngực, khó thở hoặc nghi ngờ hội chứng mạch vành cấp trong XML5.",
    ),
)

TU_KHOA_LAP_LAI_XML5: Tuple[str, ...] = (
    "làm lại",
    "theo dõi lại",
    "kiểm tra lại",
    "diễn biến nặng",
    "tái khám",
    "sau can thiệp",
    "lần 2",
    "theo dõi sát",
)


def _strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _text_of(elem: ET.Element, tag_name: str) -> str:
    for child in elem.iter():
        if _strip_ns(child.tag).upper() == tag_name.upper():
            return (child.text or "").strip()
    return ""


def _float_of(elem: ET.Element, tag_name: str, default: float = 0.0) -> float:
    raw = _text_of(elem, tag_name)
    if not raw:
        return default
    cleaned = raw.replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return default


def _extract_embedded_xmls(xml_files: Dict[str, str]) -> Dict[str, str]:
    """Tách gói `<GIAMDINHHS>` đa phần tử thành dict XML1..XML5 nếu đầu vào là tệp gộp."""
    result: Dict[str, str] = {}
    for k, v in (xml_files or {}).items():
        if isinstance(v, str) and v.strip():
            result[str(k).upper()] = v

    if any(k in result for k in ("XML1", "XML2", "XML3", "XML4", "XML5")):
        return result

    for raw in result.values():
        if "<FILEHOSO" in raw.upper():
            try:
                root = ET.fromstring(raw.strip())
                for fhs in root.iter():
                    if _strip_ns(fhs.tag).upper() == "FILEHOSO":
                        loai = (fhs.attrib.get("loai") or fhs.attrib.get("LOAI") or "").strip().upper()
                        if loai in ("XML1", "XML2", "XML3", "XML4", "XML5"):
                            children = list(fhs)
                            if children:
                                result[loai] = ET.tostring(children[0], encoding="unicode")
            except ET.ParseError:
                pass
    return result


def _parse_xml_safe(loai: str, xml_str: str, loi_cau_truc: List[Dict[str, Any]]) -> Optional[ET.Element]:
    if not isinstance(xml_str, str) or not xml_str.strip():
        return None
    try:
        return ET.fromstring(xml_str.strip())
    except ET.ParseError as exc:
        loi_cau_truc.append({
            "loai": loai,
            "ma_loi": "xml_khong_hop_le",
            "truong": loai,
            "muc_do": "nghiem_trong",
            "ly_do": f"Tệp {loai} sai cú pháp XML: {exc}",
        })
        return None


def _collect_items(root: Optional[ET.Element], item_tag: str) -> List[ET.Element]:
    if root is None:
        return []
    items = [el for el in root.iter() if _strip_ns(el.tag).upper() == item_tag.upper()]
    return items


def _kiem_tra_xml1(
    root1: Optional[ET.Element],
    co_xml1: bool,
    loi_cau_truc: List[Dict[str, Any]],
) -> Tuple[List[str], float]:
    """Kiểm tra XML1 (QĐ 130/4210): trường bắt buộc, mã thẻ BHYT, mã ICD-10, cân đối tài chính."""
    if not co_xml1:
        loi_cau_truc.append({
            "loai": "XML1",
            "ma_loi": "thieu_xml1",
            "truong": "XML1",
            "muc_do": "nghiem_trong",
            "ly_do": "Thiếu bảng tổng hợp XML1 bắt buộc theo QĐ 130/4210.",
        })
        return [], 0.0

    if root1 is None:
        return [], 0.0

    tong_hop = root1
    if _strip_ns(root1.tag).upper() != "TONG_HOP":
        found = _collect_items(root1, "TONG_HOP")
        if found:
            tong_hop = found[0]

    for field_name in TRUONG_BAT_BUOC_XML1:
        val = _text_of(tong_hop, field_name)
        if not val:
            loi_cau_truc.append({
                "loai": "XML1",
                "ma_loi": "thieu_truong_bat_buoc",
                "truong": field_name,
                "muc_do": "nghiem_trong",
                "ly_do": f"XML1 thiếu trường bắt buộc `{field_name}` theo QĐ 130/4210.",
            })

    ma_the = _text_of(tong_hop, "MA_THE").upper()
    if ma_the and not MAU_THE_BHYT_15.match(ma_the):
        loi_cau_truc.append({
            "loai": "XML1",
            "ma_loi": "ma_the_khong_hop_le",
            "truong": "MA_THE",
            "gia_tri": ma_the,
            "muc_do": "nghiem_trong",
            "ly_do": f"Mã thẻ BHYT `{ma_the}` không đúng chuẩn 15 ký tự.",
        })

    ma_benh = _text_of(tong_hop, "MA_BENH").upper()
    if ma_benh and not MAU_ICD10.match(ma_benh):
        loi_cau_truc.append({
            "loai": "XML1",
            "ma_loi": "ma_benh_icd10_khong_hop_le",
            "truong": "MA_BENH",
            "gia_tri": ma_benh,
            "muc_do": "nghiem_trong",
            "ly_do": f"Mã bệnh chính `{ma_benh}` không đúng định dạng ICD-10 (VD: I10, J18.9).",
        })

    ma_benh_khac_raw = _text_of(tong_hop, "MA_BENHKHAC").upper()
    icd_codes: List[str] = []
    if ma_benh:
        icd_codes.append(ma_benh)
    if ma_benh_khac_raw:
        for part in re.split(r"[;,|\s]+", ma_benh_khac_raw):
            p = part.strip()
            if p:
                icd_codes.append(p)

    t_tongchi = _float_of(tong_hop, "T_TONGCHI", 0.0)
    t_bhtt = _float_of(tong_hop, "T_BHTT", 0.0)
    t_bntt = _float_of(tong_hop, "T_BNTT", 0.0)
    t_bncct = _float_of(tong_hop, "T_BNCCT", 0.0)
    t_nguonkhac = _float_of(tong_hop, "T_NGUONKHAC", 0.0)

    co_chi_tiet_tai_chinh = any(
        _text_of(tong_hop, f) != ""
        for f in ("T_TONGCHI", "T_BHTT", "T_BNTT", "T_BNCCT", "T_NGUONKHAC")
    )
    if co_chi_tiet_tai_chinh:
        tong_thanh_phan = t_bhtt + t_bntt + t_bncct + t_nguonkhac
        chenh_lech = round(t_tongchi - tong_thanh_phan, 2)
        if abs(chenh_lech) > 1.0:
            loi_cau_truc.append({
                "loai": "XML1",
                "ma_loi": "lech_tai_chinh_xml1",
                "truong": "T_TONGCHI",
                "t_tongchi": t_tongchi,
                "tong_thanh_phan": tong_thanh_phan,
                "chenh_lech": chenh_lech,
                "muc_do": "nghiem_trong",
                "ly_do": (
                    f"Lệch cân đối tài chính XML1: T_TONGCHI ({t_tongchi:,.0f} đ) != "
                    f"T_BHTT + T_BNTT + T_BNCCT + T_NGUONKHAC ({tong_thanh_phan:,.0f} đ), "
                    f"chênh lệch {chenh_lech:+,.0f} đ."
                ),
            })

    return icd_codes, t_tongchi


def _chi_phi_muc(elem: ET.Element) -> float:
    thanh_tien = _float_of(elem, "THANH_TIEN", 0.0)
    if thanh_tien > 0:
        return round(thanh_tien, 2)
    so_luong = _float_of(elem, "SO_LUONG", 0.0)
    don_gia = _float_of(elem, "DON_GIA", 0.0)
    return round(so_luong * don_gia, 2)


def _la_ppi_duong_tiem(ten_thuoc: str, duong_dung: str, ham_luong: str) -> bool:
    ten_l = ten_thuoc.lower()
    duong_l = duong_dung.lower()
    ham_l = ham_luong.lower()
    if not any(hc in ten_l for hc in PPI_HOAT_CHAT):
        return False
    return (
        "tiêm" in ten_l
        or "truyền" in ten_l
        or "iv" in ten_l.split()
        or "tiêm" in duong_l
        or "truyền" in duong_l
        or duong_l.startswith("2.")
        or "tiêm" in ham_l
    )


def _chuan_hoa_ten_tim_kiem(ten: str) -> List[str]:
    """Tách từ khóa lõi của tên thuốc/dịch vụ để đối soát chứng cứ K1–K7."""
    s = re.sub(r"\b\d+(?:[.,]\d+)?\s*(?:mg|g|mcg|ml|ui|iu|lần|viên|ống|lọ)\b", " ", ten.lower())
    s = re.sub(r"[^\w\sàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]", " ", s)
    stop = {"thuốc", "viên", "ống", "tiêm", "uống", "dịch", "vụ", "xét", "nghiệm", "chụp", "siêu", "âm", "nội", "soi"}
    tokens = [t for t in s.split() if len(t) >= 3 and t not in stop]
    return tokens


def _trich_xuat_van_ban_bang_chung(bang_chung_kham: Dict[str, Any]) -> str:
    """Gộp toàn bộ chứng cứ lâm sàng đã xác nhận (K1–K7) thành chuỗi tra cứu."""
    parts: List[str] = []
    transcript = bang_chung_kham.get("transcript")
    if isinstance(transcript, str) and transcript.strip():
        parts.append(transcript)
    elif isinstance(transcript, list):
        for turn in transcript:
            if isinstance(turn, dict):
                parts.append(str(turn.get("text") or turn.get("noi_dung") or ""))
            elif isinstance(turn, str):
                parts.append(turn)

    propositions = bang_chung_kham.get("propositions") or bang_chung_kham.get("phat_bieu") or []
    if isinstance(propositions, list):
        for prop in propositions:
            if isinstance(prop, dict):
                if prop.get("chu_the_id", 0) != 0:
                    continue
                if prop.get("phu_dinh") is True:
                    continue
                trang_thai = str(prop.get("trang_thai") or "còn hiệu lực").lower()
                quyet_dinh = str(prop.get("quyet_dinh") or "").lower()
                if trang_thai in ("đã bỏ", "da_bo", "rejected") or quyet_dinh in ("bo", "reject"):
                    continue
                noi_dung = str(prop.get("noi_dung") or prop.get("text") or "")
                thuoc = prop.get("thuoc")
                if isinstance(thuoc, dict) and thuoc.get("ten"):
                    noi_dung += " " + str(thuoc.get("ten"))
                parts.append(noi_dung)
            elif isinstance(prop, str):
                parts.append(prop)

    return " ".join(parts).lower()


def kiem_toan_goi_xml_bhyt(
    xml_files: Dict[str, str],
    bang_chung_kham: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Kiểm toán gói XML1–XML5 trước khi gửi BHXH theo QĐ 130/4210 & TT 20/2022/TT-BYT."""
    goi = _extract_embedded_xmls(xml_files or {})
    loi_cau_truc: List[Dict[str, Any]] = []
    vi_pham_tt20: List[Dict[str, Any]] = []
    thieu_bang_chung_k1_k7: List[Dict[str, Any]] = []

    root1 = _parse_xml_safe("XML1", goi.get("XML1", ""), loi_cau_truc) if "XML1" in goi else None
    root2 = _parse_xml_safe("XML2", goi.get("XML2", ""), loi_cau_truc) if "XML2" in goi else None
    root3 = _parse_xml_safe("XML3", goi.get("XML3", ""), loi_cau_truc) if "XML3" in goi else None
    if "XML4" in goi:
        _parse_xml_safe("XML4", goi.get("XML4", ""), loi_cau_truc)
    root5 = _parse_xml_safe("XML5", goi.get("XML5", ""), loi_cau_truc) if "XML5" in goi else None

    icd_codes, t_tongchi_xml1 = _kiem_tra_xml1(root1, "XML1" in goi, loi_cau_truc)

    dien_bien_list: List[str] = []
    for db_el in _collect_items(root5, "CHI_TIET_DIEN_BIEN_BENH"):
        txt = _text_of(db_el, "DIEN_BIEN") or _text_of(db_el, "DIEN_BIEN_LS")
        if txt:
            dien_bien_list.append(txt)
    dien_bien_lower = " ".join(dien_bien_list).lower()

    thuoc_items = _collect_items(root2, "CHI_TIET_THUOC")
    dvkt_items = _collect_items(root3, "CHI_TIET_DVKT")

    tong_chi_tiet = 0.0
    xuat_toan_keys: Dict[str, float] = {}

    def _dang_ky_xuat_toan(key: str, so_tien: float) -> None:
        if so_tien > xuat_toan_keys.get(key, 0.0):
            xuat_toan_keys[key] = so_tien

    # Check 2A & 2B: Thuốc XML2 theo TT 20/2022
    co_icd_nhiem_khuan = any(
        icd.startswith(prefix) for icd in icd_codes for prefix in ICD10_NHIEM_KHUAN_TIEN_TO
    )
    co_chung_cu_nk_xml5 = any(kw in dien_bien_lower for kw in TU_KHOA_NHIEM_KHUAN_XML5)

    co_icd_xhth_loet = any(
        icd.startswith(prefix) for icd in icd_codes for prefix in ICD10_XUAT_HUYET_LOET_TIEN_TO
    )
    co_chung_cu_ppi_xml5 = any(kw in dien_bien_lower for kw in TU_KHOA_PPI_IV_XML5)

    for idx, t_el in enumerate(thuoc_items, start=1):
        stt = _text_of(t_el, "STT") or str(idx)
        ma_thuoc = _text_of(t_el, "MA_THUOC")
        ten_thuoc = _text_of(t_el, "TEN_THUOC")
        ham_luong = _text_of(t_el, "HAM_LUONG")
        duong_dung = _text_of(t_el, "DUONG_DUNG")
        chi_phi = _chi_phi_muc(t_el)
        tong_chi_tiet += chi_phi

        ten_lower = ten_thuoc.lower()
        item_key = f"XML2:{stt}:{ten_thuoc}"

        if any(ks in ten_lower for ks in KHANG_SINH_HAN_CHE):
            if not (co_icd_nhiem_khuan or co_chung_cu_nk_xml5):
                vi_pham_tt20.append({
                    "loai": "XML2",
                    "nhom": "khang_sinh_han_che",
                    "stt": stt,
                    "ma": ma_thuoc,
                    "ten": ten_thuoc,
                    "nguy_co_xuat_toan": chi_phi,
                    "ly_do": (
                        f"Kháng sinh hạn chế/dự trữ `{ten_thuoc}` (TT 20/2022) thiếu chẩn đoán nhiễm khuẩn "
                        "ICD-10 (J15/J18/A41/N39/K81/L03...) hoặc kháng sinh đồ/mức độ nặng trong XML5."
                    ),
                })
                _dang_ky_xuat_toan(item_key, chi_phi)

        if _la_ppi_duong_tiem(ten_thuoc, duong_dung, ham_luong):
            if not (co_icd_xhth_loet or co_chung_cu_ppi_xml5):
                vi_pham_tt20.append({
                    "loai": "XML2",
                    "nhom": "ppi_duong_tiem",
                    "stt": stt,
                    "ma": ma_thuoc,
                    "ten": ten_thuoc,
                    "nguy_co_xuat_toan": chi_phi,
                    "ly_do": (
                        f"PPI đường tiêm `{ten_thuoc}` (TT 20/2022) thiếu chỉ định xuất huyết tiêu hóa, "
                        "loét dạ dày-tá tràng (K25/K26/K92) hoặc tình trạng nhịn ăn/không uống được trong XML5."
                    ),
                })
                _dang_ky_xuat_toan(item_key, chi_phi)

    # Check 2C: Trùng lặp DVKT & thiếu biện luận CLS trong XML3 <-> XML5
    seen_dvkt: Dict[Tuple[str, str], int] = {}
    co_ly_do_lap_lai = any(kw in dien_bien_lower for kw in TU_KHOA_LAP_LAI_XML5)

    for idx, dv_el in enumerate(dvkt_items, start=1):
        stt = _text_of(dv_el, "STT") or str(idx)
        ma_dv = _text_of(dv_el, "MA_DICH_VU")
        ten_dv = _text_of(dv_el, "TEN_DICH_VU")
        ngay_yl = _text_of(dv_el, "NGAY_YL")
        ngay_ngan = ngay_yl[:8] if len(ngay_yl) >= 8 else ngay_yl
        chi_phi = _chi_phi_muc(dv_el)
        tong_chi_tiet += chi_phi

        item_key = f"XML3:{stt}:{ten_dv}"
        if ma_dv:
            dup_key = (ma_dv, ngay_ngan)
            seen_dvkt[dup_key] = seen_dvkt.get(dup_key, 0) + 1
            if seen_dvkt[dup_key] > 1 and not co_ly_do_lap_lai:
                vi_pham_tt20.append({
                    "loai": "XML3",
                    "nhom": "trung_lap_dvkt",
                    "stt": stt,
                    "ma": ma_dv,
                    "ten": ten_dv,
                    "ngay_yl": ngay_yl,
                    "nguy_co_xuat_toan": chi_phi,
                    "ly_do": (
                        f"Trùng lặp dịch vụ `{ten_dv}` ({ma_dv}) cùng ngày y lệnh `{ngay_ngan}` "
                        "mà không có giải trình chỉ định lại trong XML5."
                    ),
                })
                _dang_ky_xuat_toan(item_key, chi_phi)

        ten_dv_lower = ten_dv.lower()
        for nhom_cls, tu_khoa_dv, tu_khoa_xml5, thong_diep in QUY_TAC_CLS_XML5:
            if any(kw in ten_dv_lower for kw in tu_khoa_dv):
                if not any(kw in dien_bien_lower for kw in tu_khoa_xml5):
                    vi_pham_tt20.append({
                        "loai": "XML3",
                        "nhom": "thieu_bien_luan_cls",
                        "loai_cls": nhom_cls,
                        "stt": stt,
                        "ma": ma_dv,
                        "ten": ten_dv,
                        "nguy_co_xuat_toan": chi_phi,
                        "ly_do": f"{ten_dv}: {thong_diep}",
                    })
                    _dang_ky_xuat_toan(item_key, chi_phi)
                break

    # Check 3: Đối soát chứng cứ K1–K7
    if isinstance(bang_chung_kham, dict):
        van_ban_bc = _trich_xuat_van_ban_bang_chung(bang_chung_kham)
        for idx, t_el in enumerate(thuoc_items, start=1):
            stt = _text_of(t_el, "STT") or str(idx)
            ma_thuoc = _text_of(t_el, "MA_THUOC")
            ten_thuoc = _text_of(t_el, "TEN_THUOC")
            chi_phi = _chi_phi_muc(t_el)
            tokens = _chuan_hoa_ten_tim_kiem(ten_thuoc)
            if tokens and not any(tok in van_ban_bc for tok in tokens):
                thieu_bang_chung_k1_k7.append({
                    "loai": "XML2",
                    "stt": stt,
                    "ma": ma_thuoc,
                    "ten": ten_thuoc,
                    "nguy_co_xuat_toan": chi_phi,
                    "ly_do": f"Thuốc `{ten_thuoc}` chưa có chứng cứ xác nhận trong hội thoại/mệnh đề K1–K7.",
                })
                _dang_ky_xuat_toan(f"XML2:{stt}:{ten_thuoc}", chi_phi)

        for idx, dv_el in enumerate(dvkt_items, start=1):
            stt = _text_of(dv_el, "STT") or str(idx)
            ma_dv = _text_of(dv_el, "MA_DICH_VU")
            ten_dv = _text_of(dv_el, "TEN_DICH_VU")
            if ma_dv == "01.0001" or "khám bệnh" in ten_dv.lower():
                continue
            chi_phi = _chi_phi_muc(dv_el)
            tokens = _chuan_hoa_ten_tim_kiem(ten_dv)
            if tokens and not any(tok in van_ban_bc for tok in tokens):
                thieu_bang_chung_k1_k7.append({
                    "loai": "XML3",
                    "stt": stt,
                    "ma": ma_dv,
                    "ten": ten_dv,
                    "nguy_co_xuat_toan": chi_phi,
                    "ly_do": f"Dịch vụ `{ten_dv}` chưa có chứng cứ xác nhận trong hội thoại/mệnh đề K1–K7.",
                })
                _dang_ky_xuat_toan(f"XML3:{stt}:{ten_dv}", chi_phi)

    tong_tien_de_nghi = round(t_tongchi_xml1 if t_tongchi_xml1 > 0 else tong_chi_tiet, 2)
    tong_nguy_co_xuat_toan = round(sum(xuat_toan_keys.values()), 2)

    tom_tat_theo_nhom: Dict[str, Any] = {
        "so_loi_cau_truc": len(loi_cau_truc),
        "so_vi_pham_tt20": len(vi_pham_tt20),
        "so_thieu_bang_chung_k1_k7": len(thieu_bang_chung_k1_k7),
        "khang_sinh_han_che": sum(1 for x in vi_pham_tt20 if x.get("nhom") == "khang_sinh_han_che"),
        "ppi_duong_tiem": sum(1 for x in vi_pham_tt20 if x.get("nhom") == "ppi_duong_tiem"),
        "trung_lap_dvkt": sum(1 for x in vi_pham_tt20 if x.get("nhom") == "trung_lap_dvkt"),
        "thieu_bien_luan_cls": sum(1 for x in vi_pham_tt20 if x.get("nhom") == "thieu_bien_luan_cls"),
    }

    hop_le = (
        len(loi_cau_truc) == 0
        and len(vi_pham_tt20) == 0
        and len(thieu_bang_chung_k1_k7) == 0
    )

    return {
        "hop_le": hop_le,
        "tong_tien_de_nghi": tong_tien_de_nghi,
        "tong_nguy_co_xuat_toan": tong_nguy_co_xuat_toan,
        "loi_cau_truc": loi_cau_truc,
        "vi_pham_tt20": vi_pham_tt20,
        "thieu_bang_chung_k1_k7": thieu_bang_chung_k1_k7,
        "tom_tat_theo_nhom": tom_tat_theo_nhom,
    }


def _main() -> None:
    if hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if "--audit" not in sys.argv:
        print(json.dumps({"error": "Thiếu cờ --audit"}, ensure_ascii=False))
        sys.exit(1)

    raw_stdin = sys.stdin.read().strip()
    payload = json.loads(raw_stdin) if raw_stdin else {}
    xml_files = payload.get("xml_files") or payload.get("xmlFiles") or {}
    bang_chung_kham = payload.get("bang_chung_kham") or payload.get("clinicalEvidence")
    result = kiem_toan_goi_xml_bhyt(xml_files, bang_chung_kham)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    _main()
