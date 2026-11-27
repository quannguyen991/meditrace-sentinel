# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Kiểm thử]
Làm gì   : Cấy 5 họ lỗi lâm sàng nguy hiểm vào ca hợp lệ rồi đếm các cổng chặn (khoá K1–K7,
           cổng rủi ro) bắt được bao nhiêu.
Vào → Ra : ca hợp lệ (danh sách PhatBieu) → tỉ lệ bắt giữ từng họ đột biến M1–M5 kèm mã chặn
           đã nổ
Đọc từ   : class ClinicalMutationTester chạy đột biến lên các cổng; class KetQuaDotBien giữ
           kết quả
Mục lục (các hàm/lớp chính):
  class ClinicalMutationTester  Chạy kiểm thử đột biến lâm sàng lên các cổng chặn
  class KetQuaDotBien           Kết quả một họ đột biến: số mẫu thử và số bắt được
Gọi tới  : duong_ong/b1_cau_truc_menh_de, duong_ong/b3_cap_nhat_trang_thai,
           duong_ong/b4_kiem_can_cu, duong_ong/b5_xep_cho_cong_rui_ro
Tên cũ   : kiem_thu_dot_bien.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Bộ Kiểm thử Đột biến Lâm sàng Tự động (Automated Clinical Mutation Testing Engine).

Mục đích khoa học (Trả lời Câu hỏi số 2 của Ban Giám khảo):
Đo lường định lượng "Tỷ lệ bắt giữ lỗi giữa các bước (Mutation Catch Rate)" của Tầng 3–4
(`cap_nhat`, `khoa_bang_chung` K1–K7, `cong_rui_ro`) bằng cách chủ động tiêm (inject)
5 họ đột biến lâm sàng nguy hiểm vào các ca khám hợp lệ và kiểm tra xem hệ thống
có chặn đứng / chuyển sang phân vùng 'CẦN BÁC SĨ XÁC NHẬN' 100% hay không:

  M1 (K1 - Bịa trích dẫn / Ảo giác nguồn): Thay chuỗi `trich_dan` bằng câu không có trong thoại.
  M2 (K3 - Đảo chủ thể Người nhà -> Bệnh nhân): Gán bệnh/dị ứng của người nhà (`tôi`) thành `chu_the_id=0`.
  M3 (K4 - Biến câu điều kiện/giả định thành sự thật): Đổi lời dặn `Nếu... thì...` thành `tinh_huong="thực tế"`.
  M4 (K6 - Sai lệch liều lượng thuốc 10x): Nhân 10 hàm lượng thuốc (`5mg -> 50mg`, `500mg -> 5000mg`).
  M5 (K7 - Giữ lại thông tin cũ đã bị đính chính): Bỏ qua trạng thái `bị thay thế` của mệnh đề cũ.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from src.duong_ong import b3_cap_nhat_trang_thai as cap_nhat
from src.duong_ong import b5_xep_cho_cong_rui_ro as cong_rui_ro
from src.duong_ong import b4_kiem_can_cu as khoa_bang_chung
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu


# ═══ class KetQuaDotBien — Kết quả một họ đột biến: số mẫu thử và số bắt được ═════════
# Gồm mã, cổng mục tiêu, tỉ lệ bắt giữ và các mã chặn đã nổ.
@dataclass
class KetQuaDotBien:
    ma_dot_bien: str
    ten_dot_bien: str
    cong_muc_tieu: str
    so_mau_thu: int
    so_mau_bat_duoc: int
    ty_le_bat_giu: float
    chi_tiet_ma_chan: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ═══ class ClinicalMutationTester — Chạy kiểm thử đột biến lâm sàng lên các cổng chặn ═══
# Cố ý đưa 5 lỗi vào mệnh đề (M1 đến M5) rồi đo cổng kiểm có chặn được không.
class ClinicalMutationTester:
    """Thực thi kiểm thử tiêm đột biến lâm sàng trên tập ca khám để đo tỷ lệ bắt lỗi K1–K7."""

    @classmethod
    def chay_kiem_thu_dot_bien(cls) -> Dict[str, Any]:
        hoi_thoai_mau = (
            "1. Bác sĩ: Chào chị, hôm nay cháu bé bị làm sao và có dị ứng thuốc gì không?\n"
            "2. Người nhà: Dạ bản thân tôi bị dị ứng Penicillin nổi mề đay, còn cháu sốt 38,5 độ.\n"
            "3. Bệnh nhân: Cháu ho 5 ngày... à nhầm, mới ho 2 ngày nay thôi ạ.\n"
            "4. Bệnh nhân: Ở nhà cháu đang uống Amlodipin 5mg buổi sáng.\n"
            "5. Bác sĩ: Nếu tối nay cháu còn sốt trên 38,5 độ thì mới uống thuốc hạ sốt nhé."
        )

        ket_qua_tung_ho: List[KetQuaDotBien] = []

        # --- M1: Đột biến Bịa đặt trích dẫn (Hallucinated Quote -> K1 chặn)
        pb_m1 = PhatBieu(
            id=1, nguoi_noi="bệnh nhân", chu_the_id=0,
            noi_dung="tiền sử suy thận mạn độ 4",
            bang_chung=[2],
            trich_dan=["cháu có tiền sử suy thận mạn độ 4 từ năm ngoái"],
        )
        kk_m1 = khoa_bang_chung.khoa_ca([pb_m1], hoi_thoai_mau)
        chan_m1 = kk_m1["ket_qua"][0].chan
        bat_m1 = "trich_khong_co" in chan_m1
        ket_qua_tung_ho.append(KetQuaDotBien(
            ma_dot_bien="M1_HALLUCINATED_QUOTE",
            ten_dot_bien="Đột biến bịa trích dẫn không có trong lời thoại",
            cong_muc_tieu="K1 (Nguồn trích dẫn nguyên văn)",
            so_mau_thu=1,
            so_mau_bat_duoc=1 if bat_m1 else 0,
            ty_le_bat_giu=1.0 if bat_m1 else 0.0,
            chi_tiet_ma_chan=chan_m1,
        ))

        # --- M2: Đột biến Đảo chủ thể Người nhà sang Bệnh nhân (Misattribution -> K3 chặn)
        pb_m2 = PhatBieu(
            id=2, nguoi_noi="người nhà", chu_the_id=0,  # Đột biến: gán dị ứng của mẹ cho bệnh nhân (0)
            noi_dung="dị ứng Penicillin nổi mề đay",
            bang_chung=[2],
            trich_dan=["bản thân tôi bị dị ứng Penicillin nổi mề đay"],
        )
        kk_m2 = khoa_bang_chung.khoa_ca([pb_m2], hoi_thoai_mau)
        chan_m2 = kk_m2["ket_qua"][0].chan
        bat_m2 = "chu_the_nguoi_ke" in chan_m2
        ket_qua_tung_ho.append(KetQuaDotBien(
            ma_dot_bien="M2_FAMILY_TO_PATIENT_SWAP",
            ten_dot_bien="Đột biến gán nhầm dị ứng của người nhà ('tôi') sang bệnh nhân",
            cong_muc_tieu="K3 (Đối soát đại từ & vai người nói)",
            so_mau_thu=1,
            so_mau_bat_duoc=1 if bat_m2 else 0,
            ty_le_bat_giu=1.0 if bat_m2 else 0.0,
            chi_tiet_ma_chan=chan_m2,
        ))

        # --- M3: Đột biến Biến câu giả định/điều kiện thành sự thật đã xảy ra (K4 chặn)
        pb_m3 = PhatBieu(
            id=3, nguoi_noi="bác sĩ", chu_the_id=0,
            noi_dung="đã uống thuốc hạ sốt",
            tinh_huong="thực tế",  # Đột biến: ghi câu "Nếu tối nay còn sốt..." thành sự thật
            bang_chung=[5],
            trich_dan=["Nếu tối nay cháu còn sốt trên 38,5 độ thì mới uống thuốc hạ sốt"],
        )
        kk_m3 = khoa_bang_chung.khoa_ca([pb_m3], hoi_thoai_mau)
        chan_m3 = kk_m3["ket_qua"][0].chan
        bat_m3 = "dieu_kien" in chan_m3
        ket_qua_tung_ho.append(KetQuaDotBien(
            ma_dot_bien="M3_CONDITIONAL_AS_FACT",
            ten_dot_bien="Đột biến biến lời dặn có điều kiện ('Nếu... thì...') thành sự thật",
            cong_muc_tieu="K4 (Phát hiện mệnh đề điều kiện/giả định)",
            so_mau_thu=1,
            so_mau_bat_duoc=1 if bat_m3 else 0,
            ty_le_bat_giu=1.0 if bat_m3 else 0.0,
            chi_tiet_ma_chan=chan_m3,
        ))

        # --- M4: Đột biến Sai lệch liều lượng thuốc gấp 10 lần (5mg -> 50mg -> K6 chặn)
        pb_m4 = PhatBieu(
            id=4, nguoi_noi="bệnh nhân", chu_the_id=0,
            noi_dung="uống Amlodipin 50mg",
            bang_chung=[4],
            trich_dan=["đang uống Amlodipin 5mg buổi sáng"],
            thuoc={"ten": "Amlodipin", "lieu": "50mg", "duong_dung": "uống"},
        )
        kk_m4 = khoa_bang_chung.khoa_ca([pb_m4], hoi_thoai_mau)
        chan_m4 = kk_m4["ket_qua"][0].chan
        bat_m4 = "lieu_khong_thay" in chan_m4
        ket_qua_tung_ho.append(KetQuaDotBien(
            ma_dot_bien="M4_DOSAGE_10X_DECIMATION",
            ten_dot_bien="Đột biến nhân 10 hàm lượng thuốc (5mg -> 50mg)",
            cong_muc_tieu="K6 (Đối soát số liệu hàm lượng & liều dùng)",
            so_mau_thu=1,
            so_mau_bat_duoc=1 if bat_m4 else 0,
            ty_le_bat_giu=1.0 if bat_m4 else 0.0,
            chi_tiet_ma_chan=chan_m4,
        ))

        # --- M5: Đột biến Giữ lại thông tin cũ đã bị người nói tự đính chính (FSM + K7 chặn)
        pb_cu = PhatBieu(
            id=5, nguoi_noi="bệnh nhân", chu_the_id=0,
            noi_dung="ho", moc_thoi_gian="5 ngày",
            bang_chung=[3], trich_dan=["Cháu ho 5 ngày"],
        )
        pb_moi = PhatBieu(
            id=6, nguoi_noi="bệnh nhân", chu_the_id=0,
            noi_dung="ho", moc_thoi_gian="2 ngày",
            bang_chung=[3], trich_dan=["mới ho 2 ngày nay thôi ạ"],
            quan_he="đính chính", quan_he_voi=5,
        )
        ps_sau_fsm = cap_nhat.ap_luat([pb_cu, pb_moi])
        kk_m5 = khoa_bang_chung.khoa_ca(ps_sau_fsm, hoi_thoai_mau)
        chan_m5 = kk_m5["ket_qua"][0].chan
        bat_m5 = "bi_thay_the" in chan_m5
        ket_qua_tung_ho.append(KetQuaDotBien(
            ma_dot_bien="M5_UNSUPERSEDED_REPAIR",
            ten_dot_bien="Đột biến giữ lại mốc thời gian cũ ('5 ngày') đã bị tự đính chính ('2 ngày')",
            cong_muc_tieu="Tầng 3 FSM + K7 (Supersession Gate)",
            so_mau_thu=1,
            so_mau_bat_duoc=1 if bat_m5 else 0,
            ty_le_bat_giu=1.0 if bat_m5 else 0.0,
            chi_tiet_ma_chan=chan_m5,
        ))

        tong_thu = sum(k.so_mau_thu for k in ket_qua_tung_ho)
        tong_bat = sum(k.so_mau_bat_duoc for k in ket_qua_tung_ho)
        return {
            "tong_so_ho_dot_bien": len(ket_qua_tung_ho),
            "tong_mau_thu": tong_thu,
            "tong_mau_bat_duoc": tong_bat,
            "ty_le_bat_giu_tong_the": round(tong_bat / max(1, tong_thu), 4),
            "chi_tiet_tung_ho": [k.to_dict() for k in ket_qua_tung_ho],
        }
