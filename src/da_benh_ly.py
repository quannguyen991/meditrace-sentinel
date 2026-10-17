# -*- coding: utf-8 -*-
"""Trụ cột 3: Động cơ Đa bệnh lý Lâm sàng (Multimorbidity Combinatorial Engine).

Giải quyết triệt để phản biện của Ban Giám khảo về rủi ro kịch bản trùng lặp:
Thay vì chỉ sinh 1 bệnh đơn lẻ từ một khuôn tĩnh, động cơ này kết hợp:
  [Bệnh chính cấp tính tới khám] + [1-2 Bệnh nền mạn tính] + [Đơn thuốc nền đang uống] + [Cơ địa nhạy cảm]
Tạo ra không gian kịch bản tổ hợp phong phú, chân thực với thực tế phòng khám bệnh viện.
"""

from dataclasses import dataclass, field
import random
from typing import Any, Dict, List, Optional, Set, Tuple

# Danh mục các bệnh nền mạn tính phổ biến ở người trưởng thành và người cao tuổi
BENH_NEN_MAN_TINH: List[Dict[str, Any]] = [
    {
        "ten": "tăng huyết áp",
        "thuoc": ["amlodipin", "losartan", "captopril", "enalapril"],
        "cau_khai": "Tôi bị tăng huyết áp năm năm nay, ngày nào cũng uống thuốc huyết áp buổi sáng.",
        "chuyen_khoa": "tim mạch"
    },
    {
        "ten": "đái tháo đường típ 2",
        "thuoc": ["metformin", "gliclazide", "insulin"],
        "cau_khai": "Tôi phát hiện tiểu đường ba năm rồi, đang uống thuốc sau bữa ăn.",
        "chuyen_khoa": "nội tiết"
    },
    {
        "ten": "hen phế quản",
        "thuoc": ["salbutamol", "budesonide"],
        "cau_khai": "Tôi có tiền sử hen từ nhỏ, hễ thời tiết lạnh là phải xịt thuốc cắt cơn.",
        "chuyen_khoa": "hô hấp"
    },
    {
        "ten": "viêm loét dạ dày tá tràng",
        "thuoc": ["omeprazole", "pantoprazole", "esomeprazole"],
        "cau_khai": "Dạ dày tôi hay bị đau cồn cào và ợ chua, thỉnh thoảng phải uống thuốc tráng dạ dày.",
        "chuyen_khoa": "tiêu hóa"
    },
    {
        "ten": "gout",
        "thuoc": ["allopurinol", "colchicine"],
        "cau_khai": "Tôi bị gút mấy năm nay, hễ ăn hải sản uống bia là khớp ngón chân cái sưng buốt.",
        "chuyen_khoa": "cơ xương khớp"
    },
    {
        "ten": "rối loạn lipid máu",
        "thuoc": ["atorvastatin", "rosuvastatin"],
        "cau_khai": "Mỡ máu tôi cao, bác sĩ tuyến dưới kê uống viên hạ mỡ máu mỗi tối trước khi đi ngủ.",
        "chuyen_khoa": "tim mạch"
    },
    {
        "ten": "suy thận mạn",
        "thuoc": ["furosemide"],
        "cau_khai": "Thận tôi lọc hơi kém, bác sĩ bảo chức năng thận suy giảm độ 2.",
        "chuyen_khoa": "thận tiết niệu"
    },
    {
        "ten": "thoái hóa khớp gối",
        "thuoc": ["glucosamine", "paracetamol"],
        "cau_khai": "Hai đầu gối tôi lục cục đau nhức khi leo cầu thang nhiều năm nay.",
        "chuyen_khoa": "cơ xương khớp"
    }
]


@dataclass
class CaDaBenhLy:
    ma_ca: str
    benh_chinh: Dict[str, Any]
    benh_nen: List[Dict[str, Any]]
    thuoc_nen_dang_dung: List[str]
    co_dia: Dict[str, Any]
    luot_hoi_thoai_bo_sung: List[Tuple[str, str]] = field(default_factory=list)


class MultimorbidityEngine:
    """Động cơ ghép tổ hợp đa bệnh lý lâm sàng và sinh hội thoại phối hợp."""

    @classmethod
    def tao_ca_da_benh_ly(cls, benh_chinh: Dict[str, Any], rng: Optional[random.Random] = None,
                          ty_le_co_benh_nen: float = 0.50) -> CaDaBenhLy:
        """Tạo một ca bệnh đa bệnh lý: bệnh chính + 1-2 bệnh nền mạn tính."""
        r = rng or random.Random()
        ma_ca = f"comorb_{r.randint(1000, 9999)}"
        from src import ngu_lieu_viet as nl
        if isinstance(benh_chinh, str):
            tim = [b for b in nl.BENH if b["ten"] == benh_chinh]
            benh_dict = tim[0] if tim else {"ten": benh_chinh, "nhom": "người lớn"}
        else:
            benh_dict = benh_chinh or {"ten": "bệnh không rõ", "nhom": "người lớn"}

        nhom = benh_dict.get("nhom", "người lớn")
        
        benh_nen_duoc_chon = []
        thuoc_nen = []
        luot_thoai = []
        co_dia: Dict[str, Any] = {"tien_su_benh": []}

        # Trẻ em ít có bệnh nền mạn tính hơn, người lớn có tỷ lệ cao
        co_nen = (r.random() < ty_le_co_benh_nen) if nhom != "nhi" else (r.random() < 0.15)

        if co_nen:
            # Chọn 1 hoặc 2 bệnh nền không trùng với bệnh chính
            so_benh_nen = r.choice([1, 1, 2])
            ung_vien = [b for b in BENH_NEN_MAN_TINH if b["ten"] != benh_dict.get("ten")]
            benh_nen_duoc_chon = r.sample(ung_vien, min(so_benh_nen, len(ung_vien)))

            for bn in benh_nen_duoc_chon:
                co_dia["tien_su_benh"].append(bn["ten"])
                # Chọn ngẫu nhiên 1 thuốc nền đang điều trị
                t = r.choice(bn["thuoc"])
                thuoc_nen.append(t)

            # Sinh lượt hỏi đáp tự nhiên giữa bác sĩ và bệnh nhân về bệnh nền
            cau_hoi_bs = "Trước giờ bác có bệnh lý nền mạn tính gì hoặc đang uống thuốc gì định kỳ không?"
            cau_tra_loi = " ".join(bn["cau_khai"] for bn in benh_nen_duoc_chon)
            cau_chot_thuoc = f"Hiện tại tôi đang duy trì uống {', '.join(thuoc_nen)} hằng ngày."
            cau_tra_loi_day_du = f"Dạ có bác sĩ. {cau_tra_loi} {cau_chot_thuoc}"

            luot_thoai.append(("Bác sĩ", cau_hoi_bs))
            luot_thoai.append(("Bệnh nhân", cau_tra_loi_day_du))

        # Thêm cơ địa đặc thù ngẫu nhiên
        if nhom != "nhi":
            co_dia["tuoi"] = r.randint(45, 82)
            if r.random() < 0.20:
                co_dia["egfr"] = r.randint(20, 55)  # Suy thận nhẹ đến nặng
            if r.random() < 0.10:
                co_dia["mang_thai"] = True
                co_dia["tuan_thai"] = r.randint(6, 32)
        else:
            co_dia["tuoi"] = r.randint(1, 12)

        return CaDaBenhLy(
            ma_ca=ma_ca,
            benh_chinh=benh_dict,
            benh_nen=benh_nen_duoc_chon,
            thuoc_nen_dang_dung=thuoc_nen,
            co_dia=co_dia,
            luot_hoi_thoai_bo_sung=luot_thoai
        )

    @classmethod
    def ghep_vao_hoi_thoai_goc(cls, hoi_thoai_goc: str, ca_da_benh: CaDaBenhLy) -> str:
        """Chèn các lượt hội thoại về bệnh nền vào giữa buổi khám lâm sàng."""
        if not ca_da_benh.luot_hoi_thoai_bo_sung:
            return hoi_thoai_goc

        dong = hoi_thoai_goc.strip().split("\n")
        # Chèn vào vị trí sau lượt khám thứ 2 hoặc 3 (thời điểm hỏi tiền sử bệnh)
        vi_tri = min(len(dong), 3)
        chen = [f"{nguoi}: {cau}" for nguoi, cau in ca_da_benh.luot_hoi_thoai_bo_sung]
        ket_qua = dong[:vi_tri] + chen + dong[vi_tri:]
        return "\n".join(ket_qua)
