# -*- coding: utf-8 -*-
"""Tổng hợp Tờ điều trị Nội trú Đi buồng (Inpatient Ward-Round SOAP Evolution Diff).

Căn cứ biểu mẫu y tế:
- Thông tư 32/2023/TT-BYT của Bộ Y tế (Mẫu Tờ điều trị — BV-01/BV2):
  2 cột / 2 khối bắt buộc: DIỄN BIẾN BỆNH (SOAP) và Y LỆNH ĐIỀU TRỊ.

Bất biến an toàn lâm sàng MediTrace:
- 100% quy tắc tất định (deterministic), KHÔNG dùng mô hình ngôn ngữ tự suy diễn.
- Đối chiếu trực tiếp tập phát biểu còn hiệu lực của HÔM NAY với HÔM QUA:
  + `trieu_chung_giam_hoac_het`: dương tính hôm qua -> phủ định hôm nay, hoặc mang từ chỉ đỡ/giảm/hết/bớt
  + `trieu_chung_moi_phat_sinh`: dương tính hôm nay, chưa ghi nhận hôm qua
  + `trieu_chung_con_ton_tai`: dương tính cả hai ngày
  + `bien_thien_sinh_hieu`: đối chiếu Huyết áp, Mạch, Nhiệt độ, SpO2 (chỉ khi có số thực, không đoán bù)
  + `y_lenh_duy_tri` vs `y_lenh_thay_doi`: phân tách rõ "Thuốc duy trì như ngày trước" và thuốc mới/chỉnh liều/ngừng
- Mọi mệnh đề và y lệnh đều kèm truy vết `[T1..Tn]`.
"""
from __future__ import annotations

import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

from src import tri_thuc_thuoc as _ttt
from src.phat_bieu import la_vai_nhan_vien

RE_CAI_THIEN = re.compile(
    r"(?i)(?<!\w)(đỡ|giảm|hết|bớt|nhẹ\s+hơn|cải\s+thiện|êm\s+hơn|dễ\s+thở\s+hơn|hạ\s+sốt)(?!\w)"
)

RE_TU_LOAI_BO_GOC_TC = re.compile(
    r"(?i)\b("
    r"không\s+còn|không\s+thấy|không\s+bị|không|chưa|"
    r"đã\s+hết|hết\s+hẳn|hết|đỡ\s+nhiều|đỡ\s+hơn|đỡ|giảm\s+nhiều|giảm|bớt\s+nhiều|bớt|"
    r"vẫn\s+còn|vẫn\s+bị|vẫn|còn|đang\s+bị|đang|bị|"
    r"rất\s+nhiều|nhiều|nhẹ\s+hơn|nhẹ|nặng\s+hơn|nặng|dữ\s+dội|âm\s+ỉ|cao|râm\s+ran|"
    r"hôm\s+nay|hôm\s+qua|sáng\s+nay|tối\s+qua|đêm\s+qua|từ\s+sáng|mới\s+phát\s+sinh"
    r")\b"
)

RE_SINH_HIEU_NHAN_DIEN = re.compile(
    r"(?i)\b(huyết\s+áp|ha\s*\d|mạch\s*\d|nhịp\s+tim\s*\d|nhiệt\s+độ\s*\d|spo2\s*\d|nhịp\s+thở\s*\d|\d{2,3}/\d{2,3}\s*mmhg)\b"
)

RE_CHAN_DOAN_NHAN_DIEN = re.compile(
    r"(?i)\b(chẩn\s+đoán|theo\s+dõi\s+bệnh|nghĩ\s+nhiều\s+đến)\b"
)

RE_DUY_TRI_THUOC_CU = re.compile(
    r"(?i)\b("
    r"thuốc\s+duy\s+trì\s+như\s+(?:ngày\s+trước|hôm\s+qua|cũ)|"
    r"duy\s+trì\s+(?:thuốc|y\s+lệnh|phác\s+đồ)\s+(?:như\s+)?(?:ngày\s+trước|hôm\s+qua|cũ)|"
    r"giữ\s+nguyên\s+(?:thuốc|y\s+lệnh|liều)\s*(?:cũ|hôm\s+qua|như\s+cũ)?"
    r")\b"
)

RE_NGUNG_THUOC = re.compile(
    r"(?i)\b(ngừng|ngưng|cắt\s+thuốc|dừng\s+thuốc|bỏ\s+thuốc|tạm\s+ngừng)\b"
)


def _dinh_dang_tag_luot(bang_chung: List[int]) -> List[str]:
    return [f"[T{int(x)}]" for x in sorted({int(t) for t in (bang_chung or []) if int(t) > 0})]


def _chuan_hoa_item(m: Any, idx_mac_dinh: int = 1) -> Optional[Dict[str, Any]]:
    """Chuẩn hóa PhatBieu hoặc dict (cả chuẩn Python lẫn chuẩn API web) về dict thống nhất."""
    if hasattr(m, "to_dict"):
        d = m.to_dict()
    elif isinstance(m, dict):
        d = dict(m)
    else:
        return None

    noi_dung = str(d.get("noi_dung") or d.get("text") or "").strip()
    if not noi_dung and not isinstance(d.get("thuoc"), dict) and not d.get("drug"):
        return None

    # Chủ thể: chỉ giữ thông tin của bệnh nhân (chu_the_id == 0)
    chu_the_id = d.get("chu_the_id")
    if chu_the_id is None:
        subj = str(d.get("ten_chu_the") or d.get("chu_the") or d.get("subject") or "").strip().lower()
        if subj and not la_vai_nhan_vien(subj) and subj not in (
            "bệnh nhân", "người bệnh", "tôi", "em", "cháu", "bé", "trẻ", "patient", "self", "bác", "cụ", "ông", "bà",
        ):
            chu_the_id = 1
        else:
            chu_the_id = 0

    trang_thai_raw = str(d.get("trang_thai") or d.get("status") or "còn hiệu lực").strip().lower()
    if trang_thai_raw in ("bị thay thế", "bi_thay_the", "superseded", "replaced", "rejected"):
        trang_thai = "bị thay thế"
    elif trang_thai_raw in ("chưa giải quyết", "chua_giai_quyet", "unresolved", "quarantine", "can_xac_nhan"):
        trang_thai = "chưa giải quyết"
    else:
        trang_thai = "còn hiệu lực"

    tinh_huong_raw = str(d.get("tinh_huong") or d.get("situation") or "thực tế").strip().lower()
    if tinh_huong_raw in ("giả định", "gia_dinh", "hypothetical"):
        tinh_huong = "giả định"
    elif tinh_huong_raw in ("kế hoạch", "ke_hoach", "plan", "planned"):
        tinh_huong = "kế hoạch"
    else:
        tinh_huong = "thực tế"

    bc_raw = d.get("bang_chung") or d.get("luot_thoai") or d.get("evidenceTurns") or []
    bang_chung = [int(x) for x in bc_raw if str(x).lstrip("-").isdigit()]

    thuoc_obj = d.get("thuoc") if isinstance(d.get("thuoc"), dict) else None
    if thuoc_obj is None and d.get("drug"):
        thuoc_obj = {
            "ten": str(d["drug"]).strip(),
            "lieu": d.get("dosage") or d.get("lieu"),
            "so_lan": d.get("frequency") or d.get("so_lan"),
            "duong_dung": d.get("route") or d.get("duong_dung"),
            "trang_thai_dung": d.get("drugStatus") or d.get("trang_thai_dung"),
        }

    return {
        "id": int(d.get("id") or idx_mac_dinh),
        "nguoi_noi": str(d.get("nguoi_noi") or d.get("speaker") or "bệnh nhân").strip().lower(),
        "chu_the_id": int(chu_the_id),
        "noi_dung": noi_dung,
        "phu_dinh": bool(d.get("phu_dinh", d.get("negated", False))),
        "do_chac_chan": str(d.get("do_chac_chan") or "chắc chắn"),
        "tinh_huong": tinh_huong,
        "trang_thai": trang_thai,
        "hanh_vi": str(d.get("hanh_vi") or ""),
        "section": str(d.get("section") or d.get("muc") or "").upper(),
        "bang_chung": bang_chung,
        "trich_dan": list(d.get("trich_dan") or d.get("quotes") or []),
        "thuoc": thuoc_obj,
    }


def _goc_trieu_chung(noi_dung: str) -> str:
    """Chuẩn hóa cụm triệu chứng về lõi khái niệm để so khớp giữa hôm qua và hôm nay."""
    s = (noi_dung or "").lower()
    # Bỏ thông số nhiệt độ đính kèm sau chữ sốt ("sốt 38.5 độ" -> "sốt")
    s = re.sub(r"\b\d{2}(?:[.,]\d)?\s*(?:độ\s*c?|°c?)\b", " ", s)
    s = RE_TU_LOAI_BO_GOC_TC.sub(" ", s)
    s = re.sub(r"[^\w\sàáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s or (noi_dung or "").strip().lower()


def _khop_trieu_chung(goc_a: str, goc_b: str) -> bool:
    if not goc_a or not goc_b:
        return False
    if goc_a == goc_b:
        return True
    # Cho phép bao hàm từ nguyên vẹn khi một bên có bổ ngữ vị trí/tính chất ("ho đờm" vs "ho")
    ngan, dai = (goc_a, goc_b) if len(goc_a) <= len(goc_b) else (goc_b, goc_a)
    if len(ngan) >= 2 and re.search(rf"(?<!\w){re.escape(ngan)}(?!\w)", dai):
        return True
    return False


def _la_menh_de_thuoc_hoac_y_lenh(p: Dict[str, Any]) -> bool:
    if isinstance(p.get("thuoc"), dict) and p["thuoc"].get("ten"):
        return True
    if p.get("tinh_huong") == "kế hoạch" or p.get("hanh_vi") == "kế hoạch":
        return True
    if p.get("section") in ("THUỐC ĐANG DÙNG", "KẾ HOẠCH ĐIỀU TRỊ"):
        return True
    nd = p.get("noi_dung", "")
    if _ttt.hoat_chat(nd) is not None and "dị ứng" not in nd.lower() and "mẫn cảm" not in nd.lower():
        return True
    if RE_DUY_TRI_THUOC_CU.search(nd):
        return True
    return False


def _la_sinh_hieu_thuan(noi_dung: str) -> bool:
    nd = (noi_dung or "").strip()
    if not RE_SINH_HIEU_NHAN_DIEN.search(nd):
        return False
    # Nếu câu chỉ nêu số đo sinh hiệu ("Huyết áp 140/90 mmHg", "Mạch 88 lần/phút", "SpO2 97%")
    # Lưu ý: "sốt 38.5 độ" vẫn là triệu chứng sốt kiêm nhiệt độ
    if "sốt" in nd.lower():
        return False
    return True


def _trich_sinh_hieu(ds_pb: List[Dict[str, Any]], hoi_thoai: str = "") -> Dict[str, Dict[str, Any]]:
    """Trích xuất BP, HR, Temp, SpO2 kèm lượt bằng chứng (không tự bịa số)."""
    ket_qua: Dict[str, Dict[str, Any]] = {}
    cac_nguon: List[Tuple[str, List[int]]] = []
    for p in ds_pb:
        if p["chu_the_id"] != 0 or p["trang_thai"] != "còn hiệu lực" or p["tinh_huong"] == "giả định" or p["phu_dinh"]:
            continue
        cac_nguon.append((p["noi_dung"], p["bang_chung"]))
    if hoi_thoai:
        for idx, dong in enumerate([x.strip() for x in hoi_thoai.splitlines() if x.strip()], start=1):
            cac_nguon.append((dong, [idx]))

    for vb, bc in cac_nguon:
        # 1. Huyết áp (VD: huyết áp 130/80, HA 150/95 mmHg)
        m_ha = re.search(r"(?i)\b(?:huyết\s+áp|ha)\s*[:=]?\s*(\d{2,3})\s*/\s*(\d{2,3})\b", vb)
        if m_ha and "huyet_ap" not in ket_qua:
            sys_v, dia_v = int(m_ha.group(1)), int(m_ha.group(2))
            ket_qua["huyet_ap"] = {
                "hien_thi": f"{sys_v}/{dia_v} mmHg",
                "gia_tri": sys_v,
                "tam_thu": sys_v,
                "tam_truong": dia_v,
                "bang_chung": bc,
            }

        # 2. Mạch / Nhịp tim
        m_mach = re.search(r"(?i)\b(?:mạch|nhịp\s+tim)\s*[:=]?\s*(\d{2,3})\b", vb)
        if m_mach and "mach" not in ket_qua:
            hr = int(m_mach.group(1))
            ket_qua["mach"] = {
                "hien_thi": f"{hr} lần/phút",
                "gia_tri": float(hr),
                "bang_chung": bc,
            }

        # 3. Nhiệt độ
        m_nd = re.search(r"(?i)\b(?:nhiệt\s+độ|thân\s+nhiệt|sốt)\s*[:=]?\s*(\d{2}(?:[.,]\d)?)\s*(?:độ|°c|c\b)?", vb)
        if m_nd and "nhiet_do" not in ket_qua:
            temp = float(m_nd.group(1).replace(",", "."))
            if 34.0 <= temp <= 43.0:
                ket_qua["nhiet_do"] = {
                    "hien_thi": f"{temp:g} °C",
                    "gia_tri": temp,
                    "bang_chung": bc,
                }

        # 4. SpO2
        m_spo2 = re.search(r"(?i)\bspo2\s*[:=]?\s*(\d{2,3})\s*%?", vb)
        if m_spo2 and "spo2" not in ket_qua:
            sp_val = int(m_spo2.group(1))
            if 50 <= sp_val <= 100:
                ket_qua["spo2"] = {
                    "hien_thi": f"{sp_val}%",
                    "gia_tri": float(sp_val),
                    "bang_chung": bc,
                }

    return ket_qua


def _trich_thong_tin_thuoc(p: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    t = p.get("thuoc") if isinstance(p.get("thuoc"), dict) else {}
    nd = p.get("noi_dung") or ""
    if "dị ứng" in nd.lower() or "mẫn cảm" in nd.lower():
        return None
    ten = str(t.get("ten") or "").strip()
    if not ten:
        m_rx = _ttt.regex_ten_thuoc().search(nd)
        if m_rx:
            ten = m_rx.group(1).strip()
        else:
            return None

    hc = _ttt.hoat_chat(ten) or ten.lower()
    lieu = str(t.get("lieu") or "").strip() or None
    if not lieu:
        m_l = re.search(r"(?i)\b(\d+(?:[.,]\d+)?\s*(?:mg|g|mcg|ml|iu|đơn\s+vị|viên|ống|lọ|gói))\b", nd)
        if m_l:
            lieu = m_l.group(1).strip()
    so_lan = str(t.get("so_lan") or "").strip() or None
    if not so_lan:
        m_sl = re.search(r"(?i)\b(ngày\s+\w+\s+lần|mỗi\s+\d+\s+giờ|\d+\s*lần\s*/\s*ngày|sáng\s+[^.,;]+)", nd)
        if m_sl:
            so_lan = m_sl.group(1).strip()
    duong_dung = str(t.get("duong_dung") or "").strip() or None
    tt_dung = str(t.get("trang_thai_dung") or "").strip()
    da_ngung = (
        tt_dung == "đã ngừng"
        or bool(RE_NGUNG_THUOC.search(nd))
    )

    return {
        "khoa_so_khop": hc.lower(),
        "ten_thuoc": ten,
        "hoat_chat": _ttt.hoat_chat(ten) or ten,
        "lieu": lieu,
        "so_lan": so_lan,
        "duong_dung": duong_dung,
        "da_ngung": da_ngung,
        "noi_dung_goc": nd,
        "bang_chung": p["bang_chung"],
    }


def tong_hop_to_dieu_tri_noi_tru(
    phat_bieu_hom_nay: list,
    phat_bieu_hom_qua: list,
    hoi_thoai_hom_nay: str = "",
    ngay_dieu_tri_thu: int | None = None,
) -> dict:
    """Đối chiếu diễn biến SOAP & y lệnh điều trị nội trú giữa Hôm nay và Hôm qua (Mẫu TT 32/2023/TT-BYT)."""
    ds_nay = [
        x for idx, raw in enumerate(phat_bieu_hom_nay or [], start=1)
        if (x := _chuan_hoa_item(raw, idx)) is not None
    ]
    ds_qua = [
        x for idx, raw in enumerate(phat_bieu_hom_qua or [], start=1)
        if (x := _chuan_hoa_item(raw, idx)) is not None
    ]

    # Lọc các mệnh đề còn hiệu lực, không giả định, thuộc bệnh nhân (chu_the_id == 0)
    hieu_luc_nay = [
        p for p in ds_nay
        if p["chu_the_id"] == 0 and p["trang_thai"] == "còn hiệu lực" and p["tinh_huong"] != "giả định"
    ]
    hieu_luc_qua = [
        p for p in ds_qua
        if p["chu_the_id"] == 0 and p["trang_thai"] == "còn hiệu lực" and p["tinh_huong"] != "giả định"
    ]

    # 1. TẬP TRIỆU CHỨNG DƯƠNG TÍNH HÔM QUA
    tc_duong_qua: List[Dict[str, Any]] = []
    for p in hieu_luc_qua:
        if p["phu_dinh"] or _la_menh_de_thuoc_hoac_y_lenh(p) or _la_sinh_hieu_thuan(p["noi_dung"]):
            continue
        if RE_CHAN_DOAN_NHAN_DIEN.search(p["noi_dung"]) or p["hanh_vi"] == "nhận định" or p["section"] == "CHẨN ĐOÁN":
            continue
        tc_duong_qua.append({
            "goc": _goc_trieu_chung(p["noi_dung"]),
            "noi_dung": p["noi_dung"],
            "bang_chung": p["bang_chung"],
        })

    # 2. PHÂN LOẠI TRIỆU CHỨNG HÔM NAY
    trieu_chung_giam_hoac_het: List[Dict[str, Any]] = []
    trieu_chung_moi_phat_sinh: List[Dict[str, Any]] = []
    trieu_chung_con_ton_tai: List[Dict[str, Any]] = []
    nhan_dinh_kham_hom_nay: List[Dict[str, Any]] = []

    for p in hieu_luc_nay:
        if _la_menh_de_thuoc_hoac_y_lenh(p) or _la_sinh_hieu_thuan(p["noi_dung"]):
            continue
        if RE_CHAN_DOAN_NHAN_DIEN.search(p["noi_dung"]) or p["hanh_vi"] == "nhận định" or p["section"] == "CHẨN ĐOÁN":
            if not p["phu_dinh"]:
                nhan_dinh_kham_hom_nay.append({
                    "noi_dung": p["noi_dung"],
                    "bang_chung": _dinh_dang_tag_luot(p["bang_chung"]),
                    "luot_thoai": p["bang_chung"],
                })
            continue

        goc_nay = _goc_trieu_chung(p["noi_dung"])
        khop_qua = next((q for q in tc_duong_qua if _khop_trieu_chung(goc_nay, q["goc"])), None)
        co_tu_cai_thien = bool(RE_CAI_THIEN.search(p["noi_dung"]))
        la_het = p["phu_dinh"] or bool(re.search(r"(?i)(?<!\w)(hết|không\s+còn|hạ\s+sốt)(?!\w)", p["noi_dung"]))

        if p["phu_dinh"]:
            if khop_qua is not None:
                trieu_chung_giam_hoac_het.append({
                    "noi_dung": f"Hết {goc_nay}" if not p["noi_dung"].lower().startswith(("không", "hết")) else p["noi_dung"],
                    "hom_qua": khop_qua["noi_dung"],
                    "trang_thai_dien_bien": "hết",
                    "bang_chung": _dinh_dang_tag_luot(p["bang_chung"]),
                    "luot_thoai": p["bang_chung"],
                })
            continue

        if co_tu_cai_thien:
            trieu_chung_giam_hoac_het.append({
                "noi_dung": p["noi_dung"],
                "hom_qua": khop_qua["noi_dung"] if khop_qua else None,
                "trang_thai_dien_bien": "hết" if la_het else "giảm/đỡ",
                "bang_chung": _dinh_dang_tag_luot(p["bang_chung"]),
                "luot_thoai": p["bang_chung"],
            })
        elif khop_qua is not None:
            trieu_chung_con_ton_tai.append({
                "noi_dung": p["noi_dung"],
                "hom_qua": khop_qua["noi_dung"],
                "bang_chung": _dinh_dang_tag_luot(p["bang_chung"]),
                "luot_thoai": p["bang_chung"],
            })
        else:
            trieu_chung_moi_phat_sinh.append({
                "noi_dung": p["noi_dung"],
                "bang_chung": _dinh_dang_tag_luot(p["bang_chung"]),
                "luot_thoai": p["bang_chung"],
            })

    # 3. ĐỐI CHIẾU BIẾN THIÊN SINH HIỆU
    sh_qua = _trich_sinh_hieu(hieu_luc_qua, "")
    sh_nay = _trich_sinh_hieu(hieu_luc_nay, hoi_thoai_hom_nay)
    ten_sh_map = {
        "huyet_ap": "Huyết áp",
        "mach": "Mạch",
        "nhiet_do": "Nhiệt độ",
        "spo2": "SpO2",
    }
    bien_thien_sinh_hieu: List[Dict[str, Any]] = []
    for ma_sh, ten_sh in ten_sh_map.items():
        q_item = sh_qua.get(ma_sh)
        n_item = sh_nay.get(ma_sh)
        if q_item is None and n_item is None:
            continue
        xu_huong = "chỉ có một mốc"
        if q_item is not None and n_item is not None:
            chenh = float(n_item["gia_tri"]) - float(q_item["gia_tri"])
            if abs(chenh) < 1e-6:
                xu_huong = "ổn định"
            elif chenh > 0:
                xu_huong = "tăng"
            else:
                xu_huong = "giảm"
        bien_thien_sinh_hieu.append({
            "ma": ma_sh,
            "chi_so": ten_sh,
            "hom_qua": q_item["hien_thi"] if q_item else None,
            "hom_nay": n_item["hien_thi"] if n_item else None,
            "xu_huong": xu_huong,
            "bang_chung": _dinh_dang_tag_luot(n_item["bang_chung"]) if n_item else [],
        })

    # 4. ĐỐI CHIẾU Y LỆNH THUỐC (DUY TRÌ vs THAY ĐỔI)
    thuoc_qua_map: Dict[str, Dict[str, Any]] = {}
    for p in hieu_luc_qua:
        if p["phu_dinh"]:
            continue
        info = _trich_thong_tin_thuoc(p)
        if info and not info["da_ngung"]:
            thuoc_qua_map[info["khoa_so_khop"]] = info

    y_lenh_duy_tri: List[Dict[str, Any]] = []
    y_lenh_thay_doi: List[Dict[str, Any]] = []
    da_xu_ly_khoa = set()

    # Kiểm tra câu bác sĩ nói "duy trì thuốc như ngày trước / giữ nguyên y lệnh cũ"
    luot_duy_tri_chung: List[int] = []
    for p in hieu_luc_nay:
        if RE_DUY_TRI_THUOC_CU.search(p["noi_dung"]):
            luot_duy_tri_chung.extend(p["bang_chung"])
    if not luot_duy_tri_chung and hoi_thoai_hom_nay:
        for idx_l, dong in enumerate([d.strip() for d in hoi_thoai_hom_nay.splitlines() if d.strip()], start=1):
            if RE_DUY_TRI_THUOC_CU.search(dong):
                luot_duy_tri_chung.append(idx_l)

    for p in hieu_luc_nay:
        if p["phu_dinh"] and not RE_NGUNG_THUOC.search(p["noi_dung"]):
            continue
        info = _trich_thong_tin_thuoc(p)
        if not info:
            continue
        khoa = info["khoa_so_khop"]
        da_xu_ly_khoa.add(khoa)
        cu = thuoc_qua_map.get(khoa)
        tags = _dinh_dang_tag_luot(info["bang_chung"])

        if info["da_ngung"]:
            y_lenh_thay_doi.append({
                "loai_thay_doi": "ngung_thuoc",
                "ten_thuoc": info["ten_thuoc"],
                "hoat_chat": info["hoat_chat"],
                "mo_ta": f"Ngừng thuốc {info['ten_thuoc']}" + (f" (hôm qua dùng {cu['lieu']})" if cu and cu.get("lieu") else ""),
                "bang_chung": tags,
                "luot_thoai": info["bang_chung"],
            })
        elif cu is None:
            chi_tiet = " ".join(x for x in (info["ten_thuoc"], info["lieu"], info["duong_dung"], info["so_lan"]) if x)
            y_lenh_thay_doi.append({
                "loai_thay_doi": "them_moi",
                "ten_thuoc": info["ten_thuoc"],
                "hoat_chat": info["hoat_chat"],
                "mo_ta": f"Bổ sung mới: {chi_tiet}",
                "bang_chung": tags,
                "luot_thoai": info["bang_chung"],
            })
        else:
            lieu_doi = bool(info["lieu"] and cu["lieu"] and info["lieu"].lower() != cu["lieu"].lower())
            lan_doi = bool(info["so_lan"] and cu["so_lan"] and info["so_lan"].lower() != cu["so_lan"].lower())
            co_tu_chinh = bool(re.search(r"(?i)\b(tăng\s+liều|giảm\s+liều|đổi\s+sang|chỉnh\s+liều)\b", info["noi_dung_goc"]))
            if lieu_doi or lan_doi or co_tu_chinh:
                truoc_str = " ".join(x for x in (cu.get("lieu"), cu.get("so_lan")) if x) or "liều cũ"
                sau_str = " ".join(x for x in (info.get("lieu"), info.get("so_lan")) if x) or info["noi_dung_goc"]
                y_lenh_thay_doi.append({
                    "loai_thay_doi": "dieu_chinh_lieu",
                    "ten_thuoc": info["ten_thuoc"],
                    "hoat_chat": info["hoat_chat"],
                    "mo_ta": f"Điều chỉnh {info['ten_thuoc']}: {truoc_str} -> {sau_str}",
                    "bang_chung": tags,
                    "luot_thoai": info["bang_chung"],
                })
            else:
                chi_tiet = " ".join(x for x in (info["ten_thuoc"], info["lieu"] or cu.get("lieu"), info["so_lan"] or cu.get("so_lan")) if x)
                y_lenh_duy_tri.append({
                    "ten_thuoc": info["ten_thuoc"],
                    "hoat_chat": info["hoat_chat"],
                    "mo_ta": f"Thuốc duy trì như ngày trước: {chi_tiet}",
                    "bang_chung": tags,
                    "luot_thoai": info["bang_chung"],
                })

    # Nếu bác sĩ nói "Thuốc duy trì như ngày trước" chung cho các thuốc cũ chưa bị ngừng/sửa
    if luot_duy_tri_chung:
        tags_chung = _dinh_dang_tag_luot(luot_duy_tri_chung)
        for khoa_cu, cu in thuoc_qua_map.items():
            if khoa_cu in da_xu_ly_khoa:
                continue
            chi_tiet_cu = " ".join(x for x in (cu["ten_thuoc"], cu.get("lieu"), cu.get("so_lan")) if x)
            y_lenh_duy_tri.append({
                "ten_thuoc": cu["ten_thuoc"],
                "hoat_chat": cu["hoat_chat"],
                "mo_ta": f"Thuốc duy trì như ngày trước: {chi_tiet_cu}",
                "bang_chung": tags_chung,
                "luot_thoai": sorted(set(luot_duy_tri_chung)),
            })

    # 5. ĐỊNH DẠNG TỜ ĐIỀU TRỊ CHUẨN MẪU BV-01/BV2 — THÔNG TƯ 32/2023/TT-BYT
    nhan_ngay = f"Ngày điều trị thứ {ngay_dieu_tri_thu}" if ngay_dieu_tri_thu is not None else "Ngày điều trị nội trú hiện tại"

    dong_dien_bien: List[str] = []
    if trieu_chung_giam_hoac_het:
        for tc in trieu_chung_giam_hoac_het:
            bc_s = " ".join(tc["bang_chung"])
            dong_dien_bien.append(f"- Đáp ứng tốt ({tc['trang_thai_dien_bien']}): {tc['noi_dung']} {bc_s}".strip())
    if trieu_chung_con_ton_tai:
        for tc in trieu_chung_con_ton_tai:
            bc_s = " ".join(tc["bang_chung"])
            dong_dien_bien.append(f"- Triệu chứng còn tồn tại: {tc['noi_dung']} {bc_s}".strip())
    if trieu_chung_moi_phat_sinh:
        for tc in trieu_chung_moi_phat_sinh:
            bc_s = " ".join(tc["bang_chung"])
            dong_dien_bien.append(f"- [LƯU Ý] Triệu chứng mới phát sinh: {tc['noi_dung']} {bc_s}".strip())
    if bien_thien_sinh_hieu:
        sh_parts = []
        for s in bien_thien_sinh_hieu:
            bc_s = " ".join(s["bang_chung"])
            if s["hom_qua"] and s["hom_nay"]:
                sh_parts.append(f"{s['chi_so']}: {s['hom_qua']} -> {s['hom_nay']} ({s['xu_huong']}) {bc_s}".strip())
            elif s["hom_nay"]:
                sh_parts.append(f"{s['chi_so']}: {s['hom_nay']} {bc_s}".strip())
            elif s["hom_qua"]:
                sh_parts.append(f"{s['chi_so']}: [cần bổ sung số đo hôm nay; hôm qua {s['hom_qua']}]")
        if sh_parts:
            dong_dien_bien.append("- Sinh hiệu: " + "; ".join(sh_parts))
    if nhan_dinh_kham_hom_nay:
        for nd_k in nhan_dinh_kham_hom_nay:
            bc_s = " ".join(nd_k["bang_chung"])
            dong_dien_bien.append(f"- Nhận định lâm sàng: {nd_k['noi_dung']} {bc_s}".strip())
    if not dong_dien_bien:
        dong_dien_bien.append("- [cần bổ sung diễn biến lâm sàng đi buồng hôm nay]")

    dong_y_lenh: List[str] = []
    if y_lenh_duy_tri:
        dong_y_lenh.append("* Thuốc duy trì như ngày trước:")
        for yl in y_lenh_duy_tri:
            bc_s = " ".join(yl["bang_chung"])
            ten_gon = yl["mo_ta"].replace("Thuốc duy trì như ngày trước: ", "")
            dong_y_lenh.append(f"  + {ten_gon} {bc_s}".strip())
    if y_lenh_thay_doi:
        dong_y_lenh.append("* Y lệnh điều chỉnh / bổ sung / ngừng hôm nay:")
        for yl in y_lenh_thay_doi:
            bc_s = " ".join(yl["bang_chung"])
            dong_y_lenh.append(f"  + {yl['mo_ta']} {bc_s}".strip())
    if not dong_y_lenh:
        dong_y_lenh.append("* [Cần bác sĩ xác nhận y lệnh điều trị & chế độ chăm sóc hôm nay]")

    van_ban_tt32 = (
        "TỜ ĐIỀU TRỊ NỘI TRÚ (MẪU BV-01/BV2 — THÔNG TƯ 32/2023/TT-BYT)\n"
        f"Thời điểm đi buồng: {nhan_ngay}\n"
        "========================================================================\n"
        "I. DIỄN BIẾN BỆNH (SOAP EVOLUTION)\n"
        + "\n".join(dong_dien_bien)
        + "\n\n"
        "II. Y LỆNH ĐIỀU TRỊ & CHĂM SÓC\n"
        + "\n".join(dong_y_lenh)
        + "\n\n"
        "Bác sĩ điều trị kiểm tra & ký xác nhận: [Cần bác sĩ xác nhận]"
    )

    return {
        "chuan_bieu_mau": "Mẫu BV-01/BV2 — Thông tư 32/2023/TT-BYT",
        "ngay_dieu_tri_thu": ngay_dieu_tri_thu,
        "trieu_chung_giam_hoac_het": trieu_chung_giam_hoac_het,
        "trieu_chung_moi_phat_sinh": trieu_chung_moi_phat_sinh,
        "trieu_chung_con_ton_tai": trieu_chung_con_ton_tai,
        "bien_thien_sinh_hieu": bien_thien_sinh_hieu,
        "y_lenh_duy_tri": y_lenh_duy_tri,
        "y_lenh_thay_doi": y_lenh_thay_doi,
        "van_ban_to_dieu_tri_tt32": van_ban_tt32,
    }


if __name__ == "__main__":
    if "--diff" in sys.argv:
        raw = sys.stdin.read().lstrip("\ufeff")
        payload = json.loads(raw) if raw.strip() else {}
        ngay_raw = payload.get("ngay_dieu_tri_thu") if payload.get("ngay_dieu_tri_thu") is not None else payload.get("treatmentDay")
        ngay_so = int(ngay_raw) if str(ngay_raw or "").strip().isdigit() else None
        kq = tong_hop_to_dieu_tri_noi_tru(
            phat_bieu_hom_nay=payload.get("phat_bieu_hom_nay") or payload.get("todayPropositions") or [],
            phat_bieu_hom_qua=payload.get("phat_bieu_hom_qua") or payload.get("yesterdayPropositions") or [],
            hoi_thoai_hom_nay=str(payload.get("hoi_thoai_hom_nay") or payload.get("transcriptToday") or ""),
            ngay_dieu_tri_thu=ngay_so,
        )
        print(json.dumps(kq, ensure_ascii=False))
