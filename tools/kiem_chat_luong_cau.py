# -*- coding: utf-8 -*-
"""Công cụ kiểm tra 6 quy tắc chất lượng câu thoại tiếng Việt y khoa (MediTrace).

Kiểm tra từng lượt thoại sau khi tách bỏ tiền tố vai nói (Bác sĩ, Bệnh nhân,
Người nhà, Điều dưỡng) dựa trên 6 quy tắc chất lượng:
1. lap_tu_lien_ke: Lặp từ/cụm từ liền kề (trùng khớp RE_LAP_TU_LOI).
2. hat_sau_dau_cham: Hạt từ đề nghị đặt sau dấu chấm (. nhé, . nha, . nghen...).
3. cum_thua_cuoi: Cụm thừa/nhận xét cụt ghép sau dấu chấm (. đáng lưu ý, . rõ ràng...).
4. ket_thuc_dau_phay_hai_cham: Lượt thoại kết thúc bằng dấu phẩy ',' hoặc hai chấm ':'.
5. hai_dau_cach: Lượt thoại chứa hai dấu cách liên tiếp '  '.
6. qua_40_tu: Lượt thoại có độ dài vượt quá 40 từ.

Sử dụng:
    python -m tools.kiem_chat_luong_cau <duong_dan_tep_jsonl> [--so-ca N] [--xuat-json PATH] [--chi-tiet]
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import sys

# Thiết lập mã hóa UTF-8 cho stdout trên console Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==============================================================================
# ĐỊNH NGHĨA 6 QUY TẮC CHẤT LƯỢNG
# ==============================================================================

# Danh sách 6 quy tắc chuẩn
DANH_SACH_QUY_TAC = [
    "lap_tu_lien_ke",
    "hat_sau_dau_cham",
    "cum_thua_cuoi",
    "ket_thuc_dau_phay_hai_cham",
    "hai_dau_cach",
    "qua_40_tu",
]

MO_TA_QUY_TAC = {
    "lap_tu_lien_ke": "Lặp từ/cụm từ liền kề vi phạm ngữ pháp/khẩu ngữ",
    "hat_sau_dau_cham": "Hạt từ đề nghị gắn sau dấu chấm (. nhé, . nha...)",
    "cum_thua_cuoi": "Cụm thừa/nhận xét cụt ghép sau dấu chấm (. đáng lưu ý...)",
    "ket_thuc_dau_phay_hai_cham": "Lượt thoại kết thúc dở dang bằng dấu phẩy hoặc hai chấm",
    "hai_dau_cach": "Lượt thoại chứa hai dấu cách liên tiếp trong câu",
    "qua_40_tu": "Lượt thoại quá dài (> 40 từ)",
}

# Vai nói chuẩn trong hội thoại lâm sàng MediTrace
VAI_NOI_CHUAN = ["Bác sĩ", "Bệnh nhân", "Người nhà", "Điều dưỡng"]

# 1. Regex lặp từ lỗi (đồng bộ với tests/test_sua_loi_chat_luong_v2.py)
RE_LAP_TU_LOI = re.compile(
    r"\b("
    r"không\s+không|"
    r"chưa\s+không|"
    r"phải\s+không\s+phải\s+không|"
    r"đúng\s+không\s+phải\s+không|"
    r"vậy\s+vậy|"
    r"vậy\s+thế|"
    r"thế\s+thế|"
    r"thế\s+vậy|"
    r"nhé\s+nhé|"
    r"nhé\s+nha|"
    r"nha\s+nha|"
    r"nghen\s+nghen|"
    r"ạ\s+ạ|"
    r"cả\s+cả|"
    r"hết\s+hết|"
    r"đâu\s+đâu|"
    r"bao\s+giờ\s+bao\s+giờ|"
    r"giúp\s+tôi\s+giúp\s+tôi|"
    r"giúp\s+bác\s+sĩ\s+giúp|"
    r"một\s+chút\s+một\s+chút|"
    r"xem\s+thế\s+nào\s+xem|"
    r"nay\s+nay|"
    r"rồi\s+rồi|"
    r"nay\s+rồi\s+nay|"
    r"rồi\s+nay\s+rồi|"
    r"trước\s+đây,\s+trước\s+đây|"
    r"để\s+tôi,\s+để\s+tôi|"
    r"để\s+tôi,\s+để\s+bác\s+sĩ|"
    r"bây\s+giờ\s+bác\s+sĩ\s+sẽ,|"
    r"dạ\s+em,\s+em|"
    r"dạ\s+tôi,\s+tôi|"
    r"dạ\s+em,\s+tôi|"
    r"dạ\s+tôi,\s+em"
    r")\b",
    re.IGNORECASE,
)

# 2. Hạt từ đề nghị sau dấu chấm
RE_HAT_SAU_DAU_CHAM = re.compile(
    r"\.\s*(nhé|nha|nghen|nhe|nhen|ạ|hả|nhỉ)\b",
    re.IGNORECASE,
)

# 3. Cụm nhận xét thừa sau dấu chấm
RE_CUM_THUA_CUOI = re.compile(
    r"\.\s*(?:đáng lưu ý|rõ ràng|cần theo dõi|đáng kể|quan trọng|cần chú ý điều trị|"
    r"đừng quá lo lắng nhé|để theo dõi thêm|theo đúng hướng dẫn|cho an tâm nhé)(?:\.|\s*$)",
    re.IGNORECASE,
)

# 4. Kết thúc bằng dấu phẩy hoặc hai chấm
RE_KET_THUC_DAU_PHAY_HAI_CHAM = re.compile(r"[,:]\s*$")


# ==============================================================================
# HÀM KIỂM TRA TỪNG CÂU VÀ TÁCH LƯỢT THOẠI
# ==============================================================================

def tach_vai_va_cau(dong: str) -> tuple[str, str]:
    """Tách vai người nói và nội dung lượt thoại từ một dòng thoại.

    Ví dụ:
        'Bác sĩ: Chị kể tôi nghe anh bị sao ạ.' -> ('Bác sĩ', 'Chị kể tôi nghe anh bị sao ạ.')
        'Bệnh nhân: Tôi bị ho kéo dài.' -> ('Bệnh nhân', 'Tôi bị ho kéo dài.')
    """
    dong = dong.strip()
    if not dong:
        return "", ""
    if ": " in dong:
        vai, _, cau = dong.partition(": ")
        return vai.strip(), cau.strip()
    if ":" in dong:
        vai, _, cau = dong.partition(":")
        return vai.strip(), cau.strip()
    return "Không rõ", dong


def kiem_tra_cau(cau: str) -> list[str]:
    """Kiểm tra một lượt thoại (đã lược bỏ tiền tố người nói) với 6 quy tắc chất lượng.

    Trả về:
        Danh sách các mã quy tắc bị vi phạm (rỗng nếu câu đạt chuẩn).
    """
    loi: list[str] = []
    cau_strip = cau.strip()
    if not cau_strip:
        return loi

    # 1. lap_tu_lien_ke
    if RE_LAP_TU_LOI.search(cau_strip):
        loi.append("lap_tu_lien_ke")

    # 2. hat_sau_dau_cham
    if RE_HAT_SAU_DAU_CHAM.search(cau_strip):
        loi.append("hat_sau_dau_cham")

    # 3. cum_thua_cuoi
    if RE_CUM_THUA_CUOI.search(cau_strip):
        loi.append("cum_thua_cuoi")

    # 4. ket_thuc_dau_phay_hai_cham
    if RE_KET_THUC_DAU_PHAY_HAI_CHAM.search(cau_strip):
        loi.append("ket_thuc_dau_phay_hai_cham")

    # 5. hai_dau_cach
    if "  " in cau:
        loi.append("hai_dau_cach")

    # 6. qua_40_tu
    if len(cau_strip.split()) > 40:
        loi.append("qua_40_tu")

    return loi


# ==============================================================================
# CẤU TRÚC KẾT QUẢ KIỂM TRA
# ==============================================================================

@dataclass
class ThongKeVaiNoi:
    """Thống kê chi tiết cho từng vai nói."""
    vai: str
    tong_luot: int = 0
    luot_co_loi: int = 0
    tong_so_loi: int = 0
    loi_theo_quy_tac: dict[str, int] = field(default_factory=lambda: {q: 0 for q in DANH_SACH_QUY_TAC})

    @property
    def ty_le_luot_loi(self) -> float:
        """Tỷ lệ phần trăm số lượt có lỗi trên tổng số lượt của vai."""
        return (self.luot_co_loi / self.tong_luot * 100.0) if self.tong_luot > 0 else 0.0

    def ty_le_quy_tac(self, quy_tac: str) -> float:
        """Tỷ lệ phần trăm vi phạm quy tắc trên tổng số lượt của vai."""
        so_loi = self.loi_theo_quy_tac.get(quy_tac, 0)
        return (so_loi / self.tong_luot * 100.0) if self.tong_luot > 0 else 0.0


@dataclass
class MauViPham:
    """Mẫu một lượt thoại vi phạm quy tắc chất lượng."""
    ca_id: str
    vai: str
    quy_tac: str
    cau: str


@dataclass
class KetQuaKiemTra:
    """Kết quả kiểm tra toàn bộ tệp dữ liệu."""
    duong_dan_tep: str
    tong_so_ca: int = 0
    tong_so_luot: int = 0
    tong_so_luot_co_loi: int = 0
    tong_so_vi_pham: int = 0
    thong_ke_quy_tac: dict[str, int] = field(default_factory=lambda: {q: 0 for q in DANH_SACH_QUY_TAC})
    thong_ke_vai_noi: dict[str, ThongKeVaiNoi] = field(default_factory=dict)
    mau_vi_pham: dict[str, list[MauViPham]] = field(default_factory=lambda: {q: [] for q in DANH_SACH_QUY_TAC})

    @property
    def ty_le_luot_loi(self) -> float:
        """Tỷ lệ phần trăm số lượt có lỗi trên tổng số lượt thoại toàn bộ."""
        return (self.tong_so_luot_co_loi / self.tong_so_luot * 100.0) if self.tong_so_luot > 0 else 0.0

    def ty_le_quy_tac(self, quy_tac: str) -> float:
        """Tỷ lệ phần trăm vi phạm quy tắc trên tổng số lượt thoại toàn bộ."""
        so_loi = self.thong_ke_quy_tac.get(quy_tac, 0)
        return (so_loi / self.tong_so_luot * 100.0) if self.tong_so_luot > 0 else 0.0

    def to_dict(self) -> dict:
        """Chuyển đổi kết quả thành dictionary để xuất JSON."""
        return {
            "duong_dan_tep": self.duong_dan_tep,
            "tong_so_ca": self.tong_so_ca,
            "tong_so_luot": self.tong_so_luot,
            "tong_so_luot_co_loi": self.tong_so_luot_co_loi,
            "ty_le_luot_co_loi_pct": round(self.ty_le_luot_loi, 4),
            "tong_so_vi_pham": self.tong_so_vi_pham,
            "thong_ke_quy_tac": {
                q: {
                    "so_vi_pham": self.thong_ke_quy_tac[q],
                    "ty_le_pct": round(self.ty_le_quy_tac(q), 4),
                    "mo_ta": MO_TA_QUY_TAC.get(q, ""),
                }
                for q in DANH_SACH_QUY_TAC
            },
            "thong_ke_vai_noi": {
                v: {
                    "tong_luot": tk.tong_luot,
                    "luot_co_loi": tk.luot_co_loi,
                    "ty_le_luot_loi_pct": round(tk.ty_le_luot_loi, 4),
                    "tong_so_loi": tk.tong_so_loi,
                    "loi_theo_quy_tac": {
                        q: {
                            "so_vi_pham": tk.loi_theo_quy_tac[q],
                            "ty_le_pct": round(tk.ty_le_quy_tac(q), 4),
                        }
                        for q in DANH_SACH_QUY_TAC
                    },
                }
                for v, tk in self.thong_ke_vai_noi.items()
            },
        }


# ==============================================================================
# HÀM THỰC THI KIỂM TRA TỆP JSONL
# ==============================================================================

def kiem_tra_tep_jsonl(
    duong_dan_tep: str | Path,
    so_ca: int | None = None,
    so_mau_toi_da: int = 5,
) -> KetQuaKiemTra:
    """Đọc và kiểm tra chất lượng câu trong tệp JSONL hội thoại lâm sàng.

    Tham số:
        duong_dan_tep: Đường dẫn tới tệp JSONL.
        so_ca: Giới hạn số ca cần kiểm tra (None để kiểm tra toàn bộ).
        so_mau_toi_da: Số lượng câu vi phạm mẫu lưu lại cho mỗi quy tắc.

    Trả về:
        Đối tượng KetQuaKiemTra chứa đầy đủ các số liệu thống kê.
    """
    duong_dan = Path(duong_dan_tep)
    if not duong_dan.is_file():
        raise FileNotFoundError(f"Không tìm thấy tệp JSONL tại: {duong_dan}")

    ket_qua = KetQuaKiemTra(duong_dan_tep=str(duong_dan))

    # Khởi tạo thống kê vai nói chuẩn
    for v in VAI_NOI_CHUAN:
        ket_qua.thong_ke_vai_noi[v] = ThongKeVaiNoi(vai=v)

    with open(duong_dan, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if so_ca is not None and idx >= so_ca:
                break

            line_str = line.strip()
            if not line_str:
                continue

            try:
                item = json.loads(line_str)
            except Exception as e:
                print(f"[Cảnh báo] Lỗi phân tích JSON ở dòng {idx + 1}: {e}", file=sys.stderr)
                continue

            ket_qua.tong_so_ca += 1
            ca_id = str(item.get("id", f"line_{idx + 1}"))
            hoi_thoai_text = item.get("input", "")

            # Duyệt từng lượt thoại trong ca
            for dong in hoi_thoai_text.splitlines():
                if not dong.strip():
                    continue

                vai, cau = tach_vai_va_cau(dong)
                if not vai and not cau:
                    continue

                # Đảm bảo vai có trong thống kê
                if vai not in ket_qua.thong_ke_vai_noi:
                    ket_qua.thong_ke_vai_noi[vai] = ThongKeVaiNoi(vai=vai)

                tk_vai = ket_qua.thong_ke_vai_noi[vai]
                tk_vai.tong_luot += 1
                ket_qua.tong_so_luot += 1

                # Kiểm tra 6 quy tắc
                cac_loi = kiem_tra_cau(cau)
                if cac_loi:
                    ket_qua.tong_so_luot_co_loi += 1
                    tk_vai.luot_co_loi += 1

                    for quy_tac in cac_loi:
                        ket_qua.tong_so_vi_pham += 1
                        ket_qua.thong_ke_quy_tac[quy_tac] += 1
                        tk_vai.tong_so_loi += 1
                        tk_vai.loi_theo_quy_tac[quy_tac] += 1

                        # Lưu mẫu vi phạm
                        ds_mau = ket_qua.mau_vi_pham[quy_tac]
                        if len(ds_mau) < so_mau_toi_da:
                            ds_mau.append(MauViPham(ca_id=ca_id, vai=vai, quy_tac=quy_tac, cau=cau))

    return ket_qua


# ==============================================================================
# HÀM ĐỊNH DẠNG VÀ IN BÁO CÁO
# ==============================================================================

def in_bao_cao(ket_qua: KetQuaKiemTra, chi_tiet: bool = False, file=sys.stdout) -> None:
    """In báo cáo định dạng chuẩn ra luồng văn bản (console hoặc tệp)."""
    sep_rong = "=" * 80
    sep_hep = "-" * 80

    print(sep_rong, file=file)
    print("                BÁO CÁO KIỂM TRA CHẤT LƯỢNG HỘI THOẠI (6 QUY TẮC)", file=file)
    print(sep_rong, file=file)
    print(f"Tệp kiểm tra          : {ket_qua.duong_dan_tep}", file=file)
    print(f"Tổng số ca kiểm tra   : {ket_qua.tong_so_ca:,}", file=file)
    print(f"Tổng số lượt thoại    : {ket_qua.tong_so_luot:,}", file=file)
    print(
        f"Số lượt có lỗi        : {ket_qua.tong_so_luot_co_loi:,} "
        f"({ket_qua.ty_le_luot_loi:.3f}% tổng lượt thoại)",
        file=file,
    )
    print(f"Tổng số lần vi phạm   : {ket_qua.tong_so_vi_pham:,}", file=file)
    print("", file=file)

    # 1. Bảng thống kê theo từng quy tắc
    print(sep_hep, file=file)
    print("1. THỐNG KÊ THEO QUY TẮC CHẤT LƯỢNG", file=file)
    print(sep_hep, file=file)
    print(
        f"{'Tên quy tắc':<28} | {'Số vi phạm':>10} | {'Tỷ lệ (%)':>10} | {'Mô tả vắn tắt'}",
        file=file,
    )
    print("-" * 28 + "-+-" + "-" * 10 + "-+-" + "-" * 10 + "-+-" + "-" * 26, file=file)

    for q in DANH_SACH_QUY_TAC:
        cnt = ket_qua.thong_ke_quy_tac[q]
        pct = ket_qua.ty_le_quy_tac(q)
        mota = MO_TA_QUY_TAC.get(q, "")
        print(f"{q:<28} | {cnt:>10,} | {pct:>9.3f}% | {mota}", file=file)
    print("", file=file)

    # 2. Bảng phân bố ma trận: Quy tắc x Vai nói
    print(sep_hep, file=file)
    print("2. MA TRẬN PHÂN BỐ LỖI: QUY TẮC x VAI NÓI", file=file)
    print(sep_hep, file=file)

    # Danh sách vai nói cần hiển thị (các vai chuẩn trước, các vai khác nếu có)
    cac_vai = list(VAI_NOI_CHUAN)
    for v in ket_qua.thong_ke_vai_noi:
        if v not in cac_vai and ket_qua.thong_ke_vai_noi[v].tong_luot > 0:
            cac_vai.append(v)

    # Header ma trận
    header_vai = " | ".join(f"{v:>10}" for v in cac_vai)
    print(f"{'Quy tắc':<28} | {header_vai} | {'Tổng':>8}", file=file)
    line_sub = " | ".join("-" * 10 for _ in cac_vai)
    print("-" * 28 + "-+-" + line_sub + "-+-" + "-" * 8, file=file)

    for q in DANH_SACH_QUY_TAC:
        vals = " | ".join(
            f"{ket_qua.thong_ke_vai_noi[v].loi_theo_quy_tac.get(q, 0):>10,}"
            for v in cac_vai
        )
        tong_q = ket_qua.thong_ke_quy_tac[q]
        print(f"{q:<28} | {vals} | {tong_q:>8,}", file=file)

    print("-" * 28 + "-+-" + line_sub + "-+-" + "-" * 8, file=file)
    tong_vai_str = " | ".join(
        f"{ket_qua.thong_ke_vai_noi[v].tong_so_loi:>10,}"
        for v in cac_vai
    )
    print(f"{'Tổng số vi phạm':<28} | {tong_vai_str} | {ket_qua.tong_so_vi_pham:>8,}", file=file)
    print("", file=file)

    # 3. Thống kê chi tiết theo từng vai nói
    print(sep_hep, file=file)
    print("3. CHI TIẾT THEO TỪNG VAI NÓI (SPEAKER ROLE)", file=file)
    print(sep_hep, file=file)

    for v in cac_vai:
        tk = ket_qua.thong_ke_vai_noi.get(v)
        if not tk or tk.tong_luot == 0:
            continue

        pct_tong = (tk.tong_luot / ket_qua.tong_so_luot * 100.0) if ket_qua.tong_so_luot > 0 else 0.0
        print(
            f"● [{v}] - Tổng lượt: {tk.tong_luot:,} ({pct_tong:.2f}% tổng lượt thoại) "
            f"| Lượt có lỗi: {tk.luot_co_loi:,} ({tk.ty_le_luot_loi:.3f}%)",
            file=file,
        )
        for q in DANH_SACH_QUY_TAC:
            cnt_q = tk.loi_theo_quy_tac.get(q, 0)
            pct_q = tk.ty_le_quy_tac(q)
            if cnt_q > 0:
                print(f"    * {q:<26}: {cnt_q:>6,} lượt ({pct_q:.3f}%)", file=file)
            else:
                print(f"    * {q:<26}:      0 lượt (0.000%)", file=file)
        print("", file=file)

    # 4. Chi tiết mẫu vi phạm nếu có yêu cầu
    if chi_tiet:
        print(sep_hep, file=file)
        print("4. CÁC MẪU CÂU VI PHẠM ĐIỂN HÌNH (TỐI ĐA 5 MẪU / QUY TẮC)", file=file)
        print(sep_hep, file=file)
        co_mau = False
        for q in DANH_SACH_QUY_TAC:
            ds = ket_qua.mau_vi_pham.get(q, [])
            if not ds:
                continue
            co_mau = True
            print(f"▶ [{q}] ({len(ds)} mẫu):", file=file)
            for m in ds:
                print(f"   - Ca {m.ca_id} [{m.vai}]: \"{m.cau}\"", file=file)
            print("", file=file)
        if not co_mau:
            print("   (Không có vi phạm nào trong bộ dữ liệu kiểm tra)", file=file)
            print("", file=file)

    print(sep_rong, file=file)


# ==============================================================================
# HÀM MAIN VÀ XỬ LÝ DÒNG LỆNH (CLI)
# ==============================================================================

def main(argv: list[str] | None = None) -> int:
    """Điểm vào xử lý CLI cho công cụ kiểm tra chất lượng."""
    parser = argparse.ArgumentParser(
        prog="python -m tools.kiem_chat_luong_cau",
        description="Kiểm tra 6 quy tắc chất lượng câu thoại tiếng Việt y khoa (MediTrace).",
    )
    parser.add_argument(
        "duong_dan_tep_jsonl",
        type=Path,
        help="Đường dẫn tới tệp dữ liệu JSONL cần kiểm tra (ví dụ: data/hoi_thoai_viet_5000.jsonl).",
    )
    parser.add_argument(
        "--so-ca",
        type=int,
        default=None,
        metavar="N",
        help="Số ca cần kiểm tra (mặc định: kiểm tra toàn bộ tệp).",
    )
    parser.add_argument(
        "--xuat-json",
        type=Path,
        default=None,
        metavar="PATH",
        help="Xuất toàn bộ kết quả thống kê ra tệp JSON theo đường dẫn chỉ định.",
    )
    parser.add_argument(
        "--chi-tiet",
        action="store_true",
        help="In chi tiết các mẫu câu vi phạm cho từng quy tắc.",
    )

    args = parser.parse_args(argv)

    try:
        ket_qua = kiem_tra_tep_jsonl(
            duong_dan_tep=args.duong_dan_tep_jsonl,
            so_ca=args.so_ca,
        )
    except FileNotFoundError as err:
        print(f"Lỗi: {err}", file=sys.stderr)
        return 1
    except Exception as err:
        print(f"Lỗi không xác định khi kiểm tra: {err}", file=sys.stderr)
        return 2

    # In báo cáo ra màn hình
    in_bao_cao(ket_qua, chi_tiet=args.chi_tiet)

    # Xuất JSON nếu được yêu cầu
    if args.xuat_json:
        try:
            args.xuat_json.parent.mkdir(parents=True, exist_ok=True)
            with open(args.xuat_json, "w", encoding="utf-8") as f:
                json.dump(ket_qua.to_dict(), f, ensure_ascii=False, indent=2)
            print(f"\nĐã xuất kết quả kiểm tra ra tệp JSON: {args.xuat_json}")
        except Exception as err:
            print(f"Lỗi khi ghi tệp JSON: {err}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
