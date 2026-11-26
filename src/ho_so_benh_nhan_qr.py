# -*- coding: utf-8 -*-
"""Trình đóng gói Hồ sơ Chăm sóc Người bệnh Kèm Chữ ký HMAC & Cổng QR.

Chuyển đổi dữ liệu ca khám (đã lọc bỏ ghi chú nội bộ bác sĩ) thành gói JSON an toàn,
xác thực toàn vẹn bằng HMAC-SHA256 để nhúng vào mã QR ISO-18004 và phục vụ Cổng theo dõi 48h/7 ngày.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import secrets
import sys
import time
from typing import Any, Dict, List, Optional

from src.dan_do_benh_nhan import (
    DAU_HIEU_DO_CAP_CUU,
    phan_loai_lich_uong_thuoc,
    sinh_ban_dan_do_benh_nhan,
)

_BI_MAT_MAC_DINH = "meditrace-patient-portal-default-key"

_QUY_TAC_TUONG_TAC_THUC_AN: List[Dict[str, Any]] = [
    {
        "tu_khoa": ["warfarin", "sintrom", "acenocoumarol"],
        "muc_do": "canh_bao",
        "noi_dung": "Thuốc chống đông máu: Giữ lượng rau xanh đậm (cải bó xôi, súp lơ xanh) ổn định hàng ngày, không ăn tăng giảm đột ngột và tránh rượu bia.",
    },
    {
        "tu_khoa": ["metformin", "glucophage"],
        "muc_do": "luu_y",
        "noi_dung": "Metformin: Uống trong hoặc ngay sau bữa ăn để giảm kích ứng dạ dày; kiêng rượu bia vì tăng nguy cơ nhiễm toan lactic.",
    },
    {
        "tu_khoa": ["atorvastatin", "simvastatin", "lovastatin", "statin"],
        "muc_do": "canh_bao",
        "noi_dung": "Nhóm Statin: Tránh uống cùng nước ép bưởi chùm vì làm tăng nồng độ thuốc trong máu; ưu tiên uống buổi tối.",
    },
    {
        "tu_khoa": ["ciprofloxacin", "levofloxacin", "moxifloxacin", "tetracycline", "doxycycline"],
        "muc_do": "canh_bao",
        "noi_dung": "Kháng sinh nhóm Quinolon/Tetracyclin: Uống cách sữa, sữa chua, viên canxi, sắt hoặc thuốc dạ dày chứa nhôm/magie ít nhất 2 giờ.",
    },
    {
        "tu_khoa": ["ibuprofen", "diclofenac", "naproxen", "meloxicam", "celecoxib", "ketoprofen", "aspirin"],
        "muc_do": "canh_bao",
        "noi_dung": "Thuốc giảm đau chống viêm (NSAID/Aspirin): Luôn uống sau ăn no; thận trọng nếu có tiền sử loét dạ dày hoặc bệnh thận.",
    },
    {
        "tu_khoa": ["perindopril", "enalapril", "lisinopril", "captopril", "losartan", "valsartan", "telmisartan", "spironolactone"],
        "muc_do": "luu_y",
        "noi_dung": "Thuốc tim mạch/huyết áp (ƯCMC/ARB): Tránh tự ý dùng muối ăn kiêng giàu Kali hoặc thực phẩm chức năng bổ sung Kali.",
    },
    {
        "tu_khoa": ["furosemide", "lasix", "hydrochlorothiazide"],
        "muc_do": "luu_y",
        "noi_dung": "Thuốc lợi tiểu: Nên uống vào buổi sáng để tránh đi tiểu đêm; theo dõi chóng mặt khi đứng lên đột ngột.",
    },
    {
        "tu_khoa": ["levothyroxine", "berlthyrox"],
        "muc_do": "canh_bao",
        "noi_dung": "Hormone tuyến giáp: Uống lúc bụng đói hoàn toàn vào sáng sớm (trước ăn 30-60 phút), cách viên sắt/canxi ít nhất 4 giờ.",
    },
]

_DAU_HIEU_DO_THEO_BENH: Dict[str, List[str]] = {
    "tim": [
        "Đau thắt ngực hoặc nặng ngực kéo dài > 15 phút, vã mồ hôi lạnh, khó thở khi nằm.",
        "Tăng cân nhanh bất thường (> 2 kg trong 2-3 ngày) hoặc phù hai chân tăng rõ.",
    ],
    "huyết áp": [
        "Huyết áp đo tại nhà >= 180/120 mmHg kèm đau đầu dữ dội, nhìn mờ hoặc đau ngực.",
    ],
    "hô hấp": [
        "Thở nhanh, khó thở tăng dần, tím môi hoặc đầu ngón tay, nói không hết câu.",
        "Ho ra máu tươi hoặc sốt cao trở lại sau khi đã hạ sốt.",
    ],
    "đái tháo đường": [
        "Run tay chân, vã mồ hôi lạnh, đói cồn cào, lú lẫn (nghi hạ đường huyết < 3.9 mmol/L).",
        "Khát nước dữ dội, tiểu nhiều, buồn nôn, thở mùi trái cây chín hoặc lơ mơ.",
    ],
    "dạ dày": [
        "Nôn ra máu hoặc dịch nâu đen như bã cà phê; đi ngoài phân đen sệt mùi khắm.",
    ],
    "thận": [
        "Tiểu rất ít hoặc vô niệu trong 24 giờ, phù mặt/chân tăng nhanh, mệt lả hoặc khó thở.",
    ],
}


def _lay_bi_mat(bi_mat_ky: str = "") -> str:
    return (bi_mat_ky or os.environ.get("MEDITRACE_PORTAL_SECRET") or _BI_MAT_MAC_DINH).strip()


def _tao_ma_ho_so(du_lieu_ca: Dict[str, Any]) -> str:
    raw = str(du_lieu_ca.get("ma_ho_so") or "").strip()
    if raw:
        clean = re.sub(r"[^A-Za-z0-9_-]", "", raw)
        if 8 <= len(clean) <= 32:
            return clean
    return secrets.token_urlsafe(12)


def _chuan_hoa_danh_sach_thuoc(du_lieu_ca: Dict[str, Any]) -> List[str]:
    nguon = (
        du_lieu_ca.get("danh_sach_thuoc")
        or du_lieu_ca.get("thuoc")
        or du_lieu_ca.get("medications")
        or []
    )
    ket_qua: List[str] = []
    if isinstance(nguon, list):
        for item in nguon:
            if isinstance(item, str) and item.strip():
                ket_qua.append(item.strip())
            elif isinstance(item, dict):
                ten = str(item.get("ten") or item.get("ten_thuoc") or item.get("name") or "").strip()
                if not ten:
                    continue
                parts = [ten]
                lieu = str(item.get("lieu") or item.get("dosage") or "").strip()
                tan_suat = str(item.get("tan_suat") or item.get("frequency") or "").strip()
                loi_dan = str(item.get("loiDan") or item.get("loi_dan") or item.get("cach_dung") or "").strip()
                for p in (lieu, tan_suat, loi_dan):
                    if p:
                        parts.append(p)
                ket_qua.append(" ".join(parts))
    return ket_qua


def _trich_tuong_tac_va_an_toan(
    danh_sach_thuoc: List[str],
    du_lieu_ca: Dict[str, Any],
) -> List[Dict[str, str]]:
    ket_qua: List[Dict[str, str]] = []
    da_them: set[str] = set()
    thuoc_ghep = " | ".join(danh_sach_thuoc).lower()

    for rule in _QUY_TAC_TUONG_TAC_THUC_AN:
        if any(kw in thuoc_ghep for kw in rule["tu_khoa"]):
            noi_dung = rule["noi_dung"]
            if noi_dung not in da_them:
                da_them.add(noi_dung)
                ket_qua.append({
                    "nguon": "tuong_tac_thuc_an",
                    "muc_do": rule["muc_do"],
                    "noi_dung": noi_dung,
                })

    # Cảnh báo hiệu chỉnh liều (suy thận / suy gan / người cao tuổi)
    hieu_chinh = du_lieu_ca.get("hieu_chinh_lieu")
    if isinstance(hieu_chinh, list):
        for hc in hieu_chinh:
            msg = ""
            if isinstance(hc, str):
                msg = hc.strip()
            elif isinstance(hc, dict):
                thuoc = str(hc.get("thuoc") or hc.get("ten_thuoc") or "").strip()
                canh_bao = str(hc.get("canh_bao") or hc.get("ly_do") or hc.get("khuyen_cao") or "").strip()
                msg = f"{thuoc}: {canh_bao}".strip(": ")
            if msg and msg not in da_them:
                da_them.add(msg)
                ket_qua.append({"nguon": "hieu_chinh_lieu", "muc_do": "canh_bao", "noi_dung": msg})
    elif isinstance(hieu_chinh, dict):
        canh_bao = str(hieu_chinh.get("canh_bao") or hieu_chinh.get("tom_tat") or "").strip()
        if canh_bao and canh_bao not in da_them:
            da_them.add(canh_bao)
            ket_qua.append({"nguon": "hieu_chinh_lieu", "muc_do": "canh_bao", "noi_dung": canh_bao})

    # Cảnh báo dược lý / thai kỳ / dị ứng / tương tác thuốc
    duoc_ly = du_lieu_ca.get("duoc_ly")
    if isinstance(duoc_ly, list):
        for dl in duoc_ly:
            msg = dl.strip() if isinstance(dl, str) else str((dl or {}).get("canh_bao") or (dl or {}).get("noi_dung") or "").strip()
            if msg and msg not in da_them:
                da_them.add(msg)
                ket_qua.append({"nguon": "duoc_ly", "muc_do": "canh_bao", "noi_dung": msg})
    elif isinstance(duoc_ly, dict):
        for key in ("canh_bao", "tuong_tac", "thai_ky", "suy_than", "di_ung"):
            val = duoc_ly.get(key)
            items = val if isinstance(val, list) else ([val] if val else [])
            for item in items:
                msg = item.strip() if isinstance(item, str) else str((item or {}).get("noi_dung") or (item or {}).get("mo_ta") or "").strip()
                if msg and msg not in da_them:
                    da_them.add(msg)
                    ket_qua.append({"nguon": f"duoc_ly:{key}", "muc_do": "canh_bao", "noi_dung": msg})

    return ket_qua


def _xay_dau_hieu_bao_dong(chan_doan: str) -> List[str]:
    cd_low = chan_doan.lower()
    ket_qua: List[str] = []
    da_co: set[str] = set()

    nhom_map = {
        "tim": ["tim", "mạch vành", "suy tim", "nhồi máu"],
        "huyết áp": ["huyết áp"],
        "hô hấp": ["phế quản", "phổi", "hen", "copd", "hô hấp"],
        "đái tháo đường": ["đái tháo đường", "tiểu đường"],
        "dạ dày": ["dạ dày", "tá tràng", "xuất huyết tiêu hóa"],
        "thận": ["thận", "tiết niệu"],
    }
    for nhom, kws in nhom_map.items():
        if any(k in cd_low for k in kws):
            for item in _DAU_HIEU_DO_THEO_BENH.get(nhom, []):
                if item not in da_co:
                    da_co.add(item)
                    ket_qua.append(item)

    for item in DAU_HIEU_DO_CAP_CUU:
        if item not in da_co:
            da_co.add(item)
            ket_qua.append(item)

    return ket_qua


def _canonical_payload_bytes(goi: Dict[str, Any]) -> bytes:
    ban_ky = {
        k: v
        for k, v in goi.items()
        if k not in ("chu_ky_hmac", "url_truy_cap")
    }
    return json.dumps(ban_ky, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def tao_goi_cham_soc_benh_nhan(du_lieu_ca: Dict[str, Any], bi_mat_ky: str = "") -> Dict[str, Any]:
    """Đóng gói hồ sơ chăm sóc người bệnh an toàn từ dữ liệu ca khám và ký HMAC-SHA256."""
    if not isinstance(du_lieu_ca, dict):
        raise ValueError("du_lieu_ca phải là dict")

    ten_bn = str(
        du_lieu_ca.get("ten_benh_nhan")
        or du_lieu_ca.get("nguoi_benh")
        or du_lieu_ca.get("patientIdentifier")
        or "Quý khách / Người bệnh"
    ).strip()
    chan_doan = str(
        du_lieu_ca.get("chan_doan")
        or du_lieu_ca.get("chan_doan_xac_dinh")
        or du_lieu_ca.get("diagnosis")
        or ""
    ).strip()
    ngay_tai_kham = str(du_lieu_ca.get("ngay_tai_kham") or "Sau 5 - 7 ngày hoặc khi hết thuốc").strip()
    canh_bao_them = du_lieu_ca.get("canh_bao_them")
    if not isinstance(canh_bao_them, list):
        canh_bao_them = None

    danh_sach_thuoc = _chuan_hoa_danh_sach_thuoc(du_lieu_ca)
    ban_dan_do = sinh_ban_dan_do_benh_nhan(
        ten_benh_nhan=ten_bn,
        chan_doan=chan_doan,
        danh_sach_thuoc=danh_sach_thuoc,
        ngay_tai_kham=ngay_tai_kham,
        canh_bao_them=canh_bao_them,
    )
    lich_phan_loai = phan_loai_lich_uong_thuoc(danh_sach_thuoc)

    # Tách riêng "chiều" nếu thuốc ghi rõ buổi chiều để hiển thị đủ 4 khung Sáng/Trưa/Chiều/Tối
    chieu_items: List[Dict[str, str]] = []
    toi_items: List[Dict[str, str]] = []
    for item in lich_phan_loai.get("toi", []):
        ten_low = item["ten_thuoc"].lower()
        if "chiều" in ten_low and "tối" not in ten_low:
            chieu_items.append(item)
        else:
            toi_items.append(item)

    lich_uong_thuoc = {
        "sang": lich_phan_loai.get("sang", []),
        "trua": lich_phan_loai.get("trua", []),
        "chieu": chieu_items,
        "toi": toi_items,
        "truoc_ngu": lich_phan_loai.get("truoc_ngu", []),
    }

    thuoc_mo_ho_lich = [
        {
            "ten_thuoc": item["ten_thuoc"],
            "cach_dung": item["cach_dung"],
            "ly_do": "Chưa ghi rõ khung giờ hoặc tần suất uống trong ngày",
        }
        for item in lich_phan_loai.get("chua_ro_gio", [])
    ]

    tuong_tac_thuc_an = _trich_tuong_tac_va_an_toan(danh_sach_thuoc, du_lieu_ca)
    dau_hieu_bao_dong = _xay_dau_hieu_bao_dong(chan_doan)
    che_do_sinh_hoat = {
        "nen_an": ban_dan_do["che_do_an_uong"]["nen_an"],
        "kieng_cu": ban_dan_do["che_do_an_uong"]["kieng_cu"],
        "loi_dan_an_toan": ban_dan_do["loi_dan_uong_thuoc_an_toan"],
        "hen_tai_kham": ban_dan_do["hen_tai_kham"],
    }

    ma_ho_so = _tao_ma_ho_so(du_lieu_ca)
    goi: Dict[str, Any] = {
        "phien_ban": "1.0",
        "ma_ho_so": ma_ho_so,
        "tao_luc": int(du_lieu_ca.get("tao_luc") or int(time.time())),
        "nguoi_benh": ban_dan_do["nguoi_benh"],
        "chan_doan": ban_dan_do["chan_doan_xac_dinh"],
        "giai_thich_benh_don_gian": ban_dan_do["giai_thich_benh_don_gian"],
        "lich_uong_thuoc": lich_uong_thuoc,
        "thuoc_mo_ho_lich": thuoc_mo_ho_lich,
        "tuong_tac_thuc_an": tuong_tac_thuc_an,
        "dau_hieu_bao_dong": dau_hieu_bao_dong,
        "che_do_sinh_hoat": che_do_sinh_hoat,
        "url_truy_cap": f"?portal={ma_ho_so}",
    }

    key = _lay_bi_mat(bi_mat_ky).encode("utf-8")
    goi["chu_ky_hmac"] = hmac.new(key, _canonical_payload_bytes(goi), hashlib.sha256).hexdigest()
    return goi


def xac_thuc_chu_ky_goi(goi: Dict[str, Any], bi_mat_ky: str = "") -> bool:
    """Kiểm tra chữ ký HMAC-SHA256 của gói chăm sóc người bệnh."""
    if not isinstance(goi, dict) or not isinstance(goi.get("chu_ky_hmac"), str):
        return False
    key = _lay_bi_mat(bi_mat_ky).encode("utf-8")
    ky_vong = hmac.new(key, _canonical_payload_bytes(goi), hashlib.sha256).hexdigest()
    return hmac.compare_digest(goi["chu_ky_hmac"], ky_vong)


def _main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Đóng gói Hồ sơ Chăm sóc Người bệnh QR MediTrace")
    parser.add_argument("--build", action="store_true", help="Đọc JSON ca khám từ stdin và xuất gói QR JSON ra stdout")
    parser.add_argument("--secret", default="", help="Khóa bí mật HMAC (tùy chọn)")
    args = parser.parse_args(argv)

    if not args.build:
        parser.print_help()
        return 1

    raw = sys.stdin.read()
    data = json.loads(raw) if raw.strip() else {}
    goi = tao_goi_cham_soc_benh_nhan(data, bi_mat_ky=args.secret)
    sys.stdout.write(json.dumps(goi, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
