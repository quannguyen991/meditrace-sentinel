# -*- coding: utf-8 -*-
"""Trợ lý Gợi ý Câu hỏi Lâm sàng Thông minh (Active Clinical Clarification Agent).

Chủ động phân tích cuộc hội thoại khám bệnh và danh sách phát biểu để phát hiện:
1. Khoảng trống bệnh sử cốt lõi (Clinical Information Gaps theo chuẩn SOCRATES cho triệu chứng đau).
2. Chi tiết triệu chứng sốt (nhiệt độ đỉnh, rét run, tính chất sốt).
3. Chi tiết triệu chứng hô hấp (ho khan/đờm, màu sắc đờm, máu, khó thở tư thế).
4. Thông tin dùng thuốc chưa đầy đủ (thiếu hàm lượng, liều dùng hàng ngày, tuân thủ điều trị).
5. Yếu tố nguy cơ & cơ địa nhạy cảm (thai kỳ/cho con bú ở phụ nữ tuổi sinh sản khi có thuốc/triệu chứng liên quan).

Sinh ra các câu hỏi gợi ý thông minh (Smart Clarification Prompts) hiển thị tức thời cho bác sĩ
để hỏi bổ sung trước khi kết thúc ca khám.
"""

from dataclasses import dataclass, field
import re
from typing import Any, Dict, List, Optional


@dataclass
class GoiYLamSang:
    ma_goi_y: str
    chu_de: str              # ĐAU, SỐT, HÔ_HẤP, THUỐC, THAI_KỲ, TIỀN_SỬ
    muc_do_uu_tien: str      # CAO, TRUNG_BINH, KHUYEN_NGHI
    khoang_trong: str        # Mô tả thông tin đang bị khuyết thiếu
    cau_hoi_goi_y: str       # Câu hỏi đề xuất cho bác sĩ
    cac_lua_chon: List[str]  # Quick chips cho UI
    ly_do_y_khoa: str        # Giải thích tại sao cần hỏi thông tin này


@dataclass
class KetQuaTroLyLamSang:
    danh_sach_goi_y: List[GoiYLamSang] = field(default_factory=list)
    tong_so_khoang_trong: int = 0
    muc_do_day_du_benh_an: float = 1.0  # Từ 0.0 đến 1.0


class ActiveClinicalClarificationAgent:
    """Động cơ phát hiện khoảng trống lâm sàng và gợi ý câu hỏi thời gian thực."""

    @classmethod
    def phan_tich_khoang_trong(
        cls,
        hoi_thoai: str,
        danh_sach_phat_bieu: Optional[List[Any]] = None,
        thong_tin_benh_nhan: Optional[Dict[str, Any]] = None
    ) -> KetQuaTroLyLamSang:
        """Rà soát toàn diện cuộc khám để tìm các thông tin y khoa còn thiếu."""
        hoi_thoai_lower = (hoi_thoai or "").lower()
        phat_bieu_texts = [
            str(getattr(p, "noi_dung", p)).lower()
            for p in (danh_sach_phat_bieu or [])
        ]
        toan_bo_van_ban = hoi_thoai_lower + " " + " ".join(phat_bieu_texts)

        goi_y_list: List[GoiYLamSang] = []

        # ----------------------------------------------------------------------
        # 1. RÀ SOÁT TRIỆU CHỨNG ĐAU (SOCRATES)
        # ----------------------------------------------------------------------
        co_dau = any(w in toan_bo_van_ban for w in ["đau bụng", "đau ngực", "đau đầu", "đau lưng", "đau khớp"])
        if co_dau:
            # Kiểm tra vị trí cụ thể của đau bụng
            if "đau bụng" in toan_bo_van_ban:
                vi_tri_bung = ["thượng vị", "hạ sườn", "quanh rốn", "hố chậu", "hạ vị", "mỏ ác"]
                if not any(vt in toan_bo_van_ban for vt in vi_tri_bung):
                    goi_y_list.append(GoiYLamSang(
                        ma_goi_y="GAP_DAU_VI_TRI_BUNG",
                        chu_de="ĐAU",
                        muc_do_uu_tien="CAO",
                        khoang_trong="Bệnh nhân khai đau bụng nhưng chưa xác định vị trí khu trú giải phẫu.",
                        cau_hoi_goi_y="Bác/cháu đau nhiều nhất ở vị trí nào trong bụng (trên rốn, dưới rốn, hay bên phải/trái)?",
                        cac_lua_chon=["Thượng vị (trên rốn)", "Hố chậu phải", "Quanh rốn", "Hạ vị (dưới rốn)", "Đau khắp bụng"],
                        ly_do_y_khoa="Khu trú vị trí đau bụng là yếu tố then chốt để phân biệt cấp cứu ngoại khoa (viêm ruột thừa, thủng tạng rỗng) với nội khoa."
                    ))

            # Kiểm tra tính chất đau
            tinh_chat_dau = ["quặn", "âm ỉ", "nhói", "như dao đâm", "từng cơn", "bỏng rát", "căng tức"]
            if not any(tc in toan_bo_van_ban for tc in tinh_chat_dau):
                goi_y_list.append(GoiYLamSang(
                    ma_goi_y="GAP_DAU_TINH_CHAT",
                    chu_de="ĐAU",
                    muc_do_uu_tien="TRUNG_BINH",
                    khoang_trong="Chưa rõ tính chất cơn đau (quặn từng cơn, âm ỉ liên tục, hay nhói buốt).",
                    cau_hoi_goi_y="Cơn đau có tính chất như thế nào: đau quặn thắt từng cơn hay đau âm ỉ liên tục cả ngày?",
                    cac_lua_chon=["Đau quặn từng cơn", "Đau âm ỉ liên tục", "Đau nhói như kim châm", "Đau rát bỏng"],
                    ly_do_y_khoa="Tính chất đau giúp định hướng cơ chế đau do co thắt tạng rỗng hay do viêm phúc mạc/thần kinh."
                ))

            # Kiểm tra hướng lan nếu là đau ngực
            if "đau ngực" in toan_bo_van_ban:
                huong_lan = ["lan lên", "lan ra sau lưng", "lan xuống tay", "lan sang vai", "không lan"]
                if not any(hl in toan_bo_van_ban for hl in huong_lan):
                    goi_y_list.append(GoiYLamSang(
                        ma_goi_y="GAP_DAU_NGUC_HUONG_LAN",
                        chu_de="ĐAU",
                        muc_do_uu_tien="CAO",
                        khoang_trong="Khai đau ngực nhưng chưa xác định hướng lan sang cánh tay trái, cằm hoặc sau lưng.",
                        cau_hoi_goi_y="Cơn đau ngực có lan lên cổ, cằm, xuống cánh tay trái hay ra sau lưng không?",
                        cac_lua_chon=["Lan xuống tay trái", "Lan ra sau lưng", "Lan lên cằm/cổ", "Chỉ đau tại chỗ, không lan"],
                        ly_do_y_khoa="Loại trừ hội chứng mạch vành cấp (nhồi máu cơ tim) và lóc tách động mạch chủ ngực."
                    ))

        # ----------------------------------------------------------------------
        # 2. RÀ SOÁT TRIỆU CHỨNG SỐT
        # ----------------------------------------------------------------------
        if "sốt" in toan_bo_van_ban:
            # Kiểm tra nhiệt độ đo được
            co_nhiet_do = bool(re.search(r"\b(?:3[6-9]|4[0-2])(?:\.[0-9])?\s*(?:độ|°c|°)\b", toan_bo_van_ban))
            if not co_nhiet_do:
                goi_y_list.append(GoiYLamSang(
                    ma_goi_y="GAP_SOT_NHIET_DO",
                    chu_de="SỐT",
                    muc_do_uu_tien="TRUNG_BINH",
                    khoang_trong="Bệnh nhân khai sốt nhưng chưa có chỉ số nhiệt độ đo bằng nhiệt kế tại nhà.",
                    cau_hoi_goi_y="Ở nhà bác/cháu có cặp nhiệt độ không, đo được bao nhiêu độ C lúc sốt cao nhất?",
                    cac_lua_chon=["37.5 - 38.0°C (Sốt nhẹ)", "38.5 - 39.0°C (Sốt vừa)", "Trên 39°C (Sốt cao)", "Chưa cặp nhiệt độ, chỉ cảm thấy nóng"],
                    ly_do_y_khoa="Định lượng mức độ sốt giúp phân tầng nguy cơ nhiễm trùng nặng và chỉ định thuốc hạ sốt phù hợp."
                ))

            # Kiểm tra rét run
            if not any(rr in toan_bo_van_ban for rr in ["rét run", "ớn lạnh", "lạnh run", "không rét"]):
                goi_y_list.append(GoiYLamSang(
                    ma_goi_y="GAP_SOT_RET_RUN",
                    chu_de="SỐT",
                    muc_do_uu_tien="TRUNG_BINH",
                    khoang_trong="Chưa khai thác cơn rét run đi kèm sốt.",
                    cau_hoi_goi_y="Khi sốt bác/cháu có kèm theo cơn rét run, phải đắp nhiều chăn không?",
                    cac_lua_chon=["Có rét run bần bật", "Chỉ ớn lạnh gai người", "Không rét run"],
                    ly_do_y_khoa="Cơn rét run là dấu hiệu chỉ điểm du khuẩn huyết (nhiễm trùng huyết) hoặc sốt rét/nhiễm khuẩn đường mật."
                ))

        # ----------------------------------------------------------------------
        # 3. RÀ SOÁT TRIỆU CHỨNG HÔ HẤP (HO & ĐỜM)
        # ----------------------------------------------------------------------
        if "ho" in toan_bo_van_ban:
            tinh_chat_ho = ["ho khan", "ho đờm", "có đờm", "đờm xanh", "đờm vàng", "đờm trắng", "ho ra máu"]
            if not any(th in toan_bo_van_ban for th in tinh_chat_ho):
                goi_y_list.append(GoiYLamSang(
                    ma_goi_y="GAP_HO_TINH_CHAT_DOM",
                    chu_de="HÔ_HẤP",
                    muc_do_uu_tien="TRUNG_BINH",
                    khoang_trong="Chưa rõ ho khan hay ho có đờm, màu sắc và tính chất đờm.",
                    cau_hoi_goi_y="Bác/cháu ho khan hay có khạc ra đờm? Đờm màu trắng trong hay vàng đục/xanh?",
                    cac_lua_chon=["Ho khan không có đờm", "Ho đờm trắng trong", "Ho đờm vàng/xanh đục", "Đờm có vệt máu"],
                    ly_do_y_khoa="Phân biệt nhiễm virus đường hô hấp trên với bội nhiễm vi khuẩn cần can thiệp kháng sinh."
                ))

        # ----------------------------------------------------------------------
        # 4. RÀ SOÁT THÔNG TIN DÙNG THUỐC (THIẾU LIỀU DÙNG / HÀM LƯỢNG)
        # ----------------------------------------------------------------------
        cac_thuoc_thuong_gap = ["amlodipin", "losartan", "metformin", "gliclazide", "atorvastatin", "paracetamol", "aspirin"]
        for thuoc in cac_thuoc_thuong_gap:
            if thuoc in toan_bo_van_ban:
                # Kiểm tra xem có hàm lượng (mg) đi kèm không
                pattern_lieu = rf"{thuoc}\s*(?:[a-zA-Z\s]*?)(\d+(?:\.\d+)?\s*(?:mg|g|viên))"
                if not re.search(pattern_lieu, toan_bo_van_ban):
                    goi_y_list.append(GoiYLamSang(
                        ma_goi_y=f"GAP_THUOC_HAM_LUONG_{thuoc.upper()}",
                        chu_de="THUỐC",
                        muc_do_uu_tien="CAO",
                        khoang_trong=f"Bệnh nhân có dùng {thuoc.capitalize()} nhưng chưa rõ hàm lượng cụ thể và liều lượng mỗi ngày.",
                        cau_hoi_goi_y=f"Thuốc {thuoc.capitalize()} bác đang uống là viên bao nhiêu miligram (mg), ngày uống mấy viên và vào lúc nào?",
                        cac_lua_chon=[f"{thuoc.capitalize()} liều thấp (1 viên/ngày)", f"{thuoc.capitalize()} liều chuẩn", "Không nhớ rõ hàm lượng, có mang theo vỏ thuốc"],
                        ly_do_y_khoa=f"Nắm chính xác liều {thuoc.capitalize()} là bắt buộc để đánh giá hiệu quả kiểm soát bệnh mạn tính và phòng ngừa quá liều/tác dụng phụ."
                    ))

        # ----------------------------------------------------------------------
        # 5. RÀ SOÁT NGUY CƠ THAI KỲ Ở PHỤ NỮ TUỔI SINH SẢN
        # ----------------------------------------------------------------------
        gioi_tinh = str(thong_tin_benh_nhan.get("gioi_tinh", "")).lower() if thong_tin_benh_nhan else ""
        tuoi = thong_tin_benh_nhan.get("tuoi", 0) if thong_tin_benh_nhan else 0

        la_nu_sinh_san = ("nữ" in gioi_tinh or "nu" in gioi_tinh) and (15 <= int(tuoi) <= 49 if tuoi else False)
        if la_nu_sinh_san:
            chua_hoi_thai = not any(tk in toan_bo_van_ban for tk in ["mang thai", "có bầu", "thai kỳ", "kinh nguyệt", "trễ kinh", "cho con bú"])
            if chua_hoi_thai:
                goi_y_list.append(GoiYLamSang(
                    ma_goi_y="GAP_NU_THAI_KY",
                    chu_de="THAI_KỲ",
                    muc_do_uu_tien="CAO",
                    khoang_trong="Bệnh nhân nữ trong độ tuổi sinh sản chưa được khai thác tình trạng thai kỳ hoặc cho con bú.",
                    cau_hoi_goi_y="Hiện tại chị/em có đang mang thai, nghi ngờ có thai (trễ kinh) hoặc đang cho con bú không?",
                    cac_lua_chon=["Không mang thai, không cho con bú", "Đang mang thai", "Đang cho con bú", "Đang trễ kinh chưa thử thai"],
                    ly_do_y_khoa="An toàn tuyệt đối trong chỉ định thuốc chống chỉ định cho thai kỳ và chụp X-quang/CT."
                ))

        # Tính điểm độ đầy đủ
        so_khoang_trong = len(goi_y_list)
        do_day_du = max(0.0, round(1.0 - (so_khoang_trong * 0.15), 2))

        return KetQuaTroLyLamSang(
            danh_sach_goi_y=goi_y_list,
            tong_so_khoang_trong=so_khoang_trong,
            muc_do_day_du_benh_an=do_day_du
        )
