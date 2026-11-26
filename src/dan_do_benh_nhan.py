# -*- coding: utf-8 -*-
"""Trình Tự động Sinh Bản Hướng dẫn & Dặn dò Người Bệnh Ngôn ngữ Đời thường (Patient Aftercare Guide).

Chuyển đổi hồ sơ bệnh án SOAP và đơn thuốc kỹ thuật sang bản dặn dò bình dị, dễ hiểu,
giúp bệnh nhân và thân nhân tuân thủ điều trị tối đa:
1. Giải thích tình trạng bệnh học bằng lời giải thích thân thiện, xua tan hoang mang.
2. Lập lịch uống thuốc phân tách theo 4 khung giờ: Sáng - Trưa - Chiều - Tối, ghi rõ trước/sau ăn.
3. Hướng dẫn chế độ dinh dưỡng, ăn kiêng và sinh hoạt phục hồi theo bệnh lý.
4. Danh mục Dấu hiệu Đỏ Nguy hiểm (Red Flags) hướng dẫn nhập viện cấp cứu khẩn cấp.
5. Hẹn lịch tái khám và các lưu ý an toàn dùng thuốc.
"""

from typing import Dict, List, Optional, Any
import re


GIAI_THICH_BENH_LY: Dict[str, str] = {
    "viêm phế quản": "Đường dẫn khí vào phổi của bác đang bị viêm nhiễm tạm thời, dẫn đến ho có đờm và mệt mỏi. Bệnh sẽ cải thiện tốt nếu uống đủ nước ấm và dùng thuốc đúng lịch.",
    "viêm họng": "Vùng hầu họng đang bị viêm sưng và kích ứng, gây cảm giác rát buốt khi nuốt. Bác nên giữ ấm cổ và hạn chế ăn đồ quá lạnh.",
    "viêm phổi": "Tổ chức nhu mô phổi đang có ổ viêm. Bác cần nghỉ ngơi tuyệt đối, uống thuốc kháng sinh đủ liều đúng giờ và theo dõi sát nhịp thở.",
    "tăng huyết áp": "Áp lực máu trong lòng mạch đang cao hơn mức an toàn. Việc uống thuốc đều đặn mỗi sáng và giảm muối là chìa khóa bảo vệ tim và não bộ.",
    "đái tháo đường": "Lượng đường trong máu đang tăng cao. Bác cần kiểm soát khẩu phần tinh bột, kiêng đường ngọt và uống thuốc hạ đường huyết đúng bữa ăn.",
    "loét dạ dày": "Niêm mạc dạ dày đang có vết trợt loét gây đau âm ỉ hoặc nóng rát. Thuốc sẽ giúp trung hòa axit và làm lành vết thương trong vài tuần.",
    "trào ngược": "Axit từ dạ dày bị trào ngược lên thực quản gây ợ chua, nóng rát cổ họng. Bác cần tránh nằm ngay sau khi ăn no.",
    "gout": "Lượng axit uric lắng đọng tạo thành các tinh thể gây sưng đau buốt tại khớp. Bác cần kiêng tuyệt đối rượu bia và các loại thịt đỏ.",
    "nhiễm khuẩn đường tiết niệu": "Đường tiết niệu đang bị vi khuẩn xâm nhập gây tiểu buốt, tiểu rắt. Bác cần uống nhiều nước lọc (2-2.5 lít/ngày) để bài xuất vi khuẩn ra ngoài.",
    "nhiễm trùng tiết niệu": "Đường tiết niệu đang bị vi khuẩn xâm nhập gây tiểu buốt, tiểu rắt. Bác cần uống nhiều nước lọc (2-2.5 lít/ngày) và uống hết đợt kháng sinh theo đơn để tránh tái phát.",
    "suy thận": "Khả năng lọc chất thải của thận đang bị suy giảm. Bác cần tuân thủ nghiêm ngặt đơn thuốc chỉnh liều, hạn chế ăn mặn và kiêng các thuốc giảm đau tự ý mua ngoài tiệm.",
    "bệnh thận mạn": "Chức năng lọc của thận đang giảm dần theo thời gian. Bác cần kiểm soát tốt huyết áp, đường huyết, ăn nhạt và không tự ý dùng thuốc giảm đau hay thảo dược không rõ nguồn gốc.",
    "hen phế quản": "Đường thở của bác đang nhạy cảm và dễ co thắt gây khò khè, khó thở. Bác cần dùng thuốc xịt dự phòng đều đặn, luôn mang theo thuốc cắt cơn và tránh khói bụi, phấn hoa, không khí lạnh.",
    "copd": "Bệnh phổi tắc nghẽn mạn tính làm đường thở hẹp lại và tiết đờm. Bác cần tuyệt đối bỏ thuốc lá, dùng bình xịt đúng kỹ thuật và tập thở chúm môi mỗi ngày.",
    "suy tim": "Tim đang bơm máu yếu hơn bình thường nên dễ gây mệt và phù chân. Bác cần uống thuốc đều đặn, ăn nhạt, theo dõi cân nặng mỗi sáng và báo bác sĩ nếu tăng cân nhanh hoặc khó thở tăng.",
    "rối loạn mỡ máu": "Lượng mỡ (cholesterol hoặc triglyceride) trong máu đang cao, dễ lắng đọng gây xơ vữa mạch máu. Bác cần hạn chế mỡ động vật, tăng cường rau xanh và vận động nhẹ nhàng 30 phút mỗi ngày.",
    "đau nửa đầu": "Cơn đau nửa đầu thường liên quan đến co giãn mạch máu não và nhạy cảm ánh sáng, tiếng ồn. Bác nên nghỉ nơi yên tĩnh tối, ngủ đủ giấc và tránh bỏ bữa hoặc căng thẳng kéo dài.",
    "thiếu máu": "Lượng hồng cầu hoặc huyết sắc tố đang thấp hơn bình thường, khiến cơ thể dễ mệt, chóng mặt. Bác cần uống bổ sung sắt/acid folic theo đơn (nếu có) và ăn thêm thực phẩm giàu sắt."
}

CHE_DO_AN_UONG_BENH: Dict[str, Dict[str, List[str]]] = {
    "tong_quat": {
        "nen_an": [
            "Ăn đủ 3 bữa điều độ, cân bằng đạm (cá, thịt nạc, trứng, đậu phụ) và rau xanh, trái cây tươi",
            "Uống đủ 1.5 - 2 lít nước lọc mỗi ngày (trừ khi bác sĩ có chỉ định hạn chế nước)",
            "Chọn thực phẩm tươi, chế biến hấp/luộc dễ tiêu hóa"
        ],
        "kieng_cu": [
            "Hạn chế rượu bia, thuốc lá, cà phê đặc và nước ngọt có ga",
            "Tránh thức ăn quá mặn, quá nhiều dầu mỡ chiên rán hoặc đồ ăn nhanh chế biến sẵn",
            "Không tự ý dùng thêm thực phẩm chức năng hay thuốc ngoài đơn khi chưa hỏi bác sĩ"
        ]
    },
    "tăng huyết áp": {
        "nen_an": ["Rau củ quả tươi giàu kali (chuối tiêu, cam, rau bina)", "Cá béo (cá hồi, cá thu) giàu Omega-3", "Ngũ cốc nguyên hạt, đậu đỗ"],
        "kieng_cu": ["Ăn mặn, mắm tôm, cà muối, dưa muối, đồ hộp đóng sẵn", "Thức uống có cồn (rượu, bia), cà phê đặc, thuốc lá", "Mỡ động vật, phủ tạng động vật"]
    },
    "tim mạch": {
        "nen_an": ["Rau xanh, trái cây tươi, ngũ cốc nguyên hạt và cá béo giàu Omega-3", "Chia nhỏ bữa ăn trong ngày để giảm gánh nặng cho tim", "Theo dõi lượng nước uống theo hướng dẫn của bác sĩ nếu có phù"],
        "kieng_cu": ["Ăn mặn (dưới 2g muối/ngày), dưa cà muối, đồ hộp, mì gói", "Rượu bia, thuốc lá, cà phê đặc và nước tăng lực", "Mỡ động vật, đồ chiên rán, phủ tạng động vật"]
    },
    "suy tim": {
        "nen_an": ["Thức ăn nhạt, mềm, dễ tiêu; tăng rau xanh và cá nạc", "Chia nhỏ 4-5 bữa nhẹ/ngày thay vì ăn quá no", "Cân nặng mỗi sáng và giữ lượng nước theo đúng lời dặn bác sĩ"],
        "kieng_cu": ["Tuyệt đối tránh ăn mặn, nước mắm chấm đậm, đồ hộp, thức ăn nhanh", "Uống quá nhiều nước một lúc gây quá tải tuần hoàn", "Rượu bia, thuốc lá, chất kích thích"]
    },
    "đái tháo đường": {
        "nen_an": ["Ăn rau xanh trước khi ăn cơm để làm chậm hấp thu đường", "Gạo lứt, yến mạch, các loại đậu hạt", "Thịt nạc, cá, đậu phụ"],
        "kieng_cu": ["Bánh kẹo ngọt, nước ngọt có ga, trà sữa, chè", "Hoa quả quá ngọt sấy khô (sầu riêng, nhãn, mít sấy)", "Bỏ bữa hoặc ăn dồn quá nhiều tinh bột vào một bữa"]
    },
    "loét dạ dày": {
        "nen_an": ["Thức ăn mềm, dễ tiêu (cháo, súp, canh hầm)", "Uống nước ấm rải rác trong ngày", "Bánh mì, khoai lang luộc giúp hút bớt dịch axit"],
        "kieng_cu": ["Đồ chua cay (chanh, ớt, tiêu, giấm, mù tạt)", "Cà phê, trà đặc, rượu bia, nước ngọt có ga", "Ăn quá no hoặc để bụng quá đói, không nằm ngay sau ăn"]
    },
    "gout": {
        "nen_an": ["Uống nhiều nước lọc (tối thiểu 2 - 2.5 lít mỗi ngày)", "Sữa ít béo, sữa chua, trứng gà", "Rau xanh, trái cây giàu vitamin C (cam, dâu tây)"],
        "kieng_cu": ["Tuyệt đối kiêng rượu, bia (kể cả bia không cồn)", "Thịt đỏ (thịt bò, thịt dê, thịt chó), nội tạng (gan, lòng, cật)", "Hải sản đậm đà đạm (cua, ghẹ, tôm biển, cá trích)"]
    },
    "suy thận": {
        "nen_an": ["Ăn nhạt, giảm muối và kiểm soát lượng đạm vừa phải theo hướng dẫn bác sĩ", "Chọn rau củ ít kali (bầu, bí, cải bắp) nếu bác sĩ dặn hạn chế kali", "Uống lượng nước phù hợp với lượng nước tiểu hàng ngày"],
        "kieng_cu": ["Thức ăn mặn, đồ muối chua, đồ hộp, mì ăn liền", "Thực phẩm quá giàu kali/phospho (chuối, cam, nước dừa, nội tạng, nước ngọt có ga) khi chưa có chỉ định", "Tuyệt đối kiêng thuốc giảm đau NSAID, thuốc nam/lá cây không rõ nguồn gốc"]
    },
    "nhiễm khuẩn tiết niệu": {
        "nen_an": ["Uống nhiều nước lọc (2 - 2.5 lít/ngày) để tăng thải vi khuẩn qua đường tiểu", "Trái cây giàu vitamin C (cam, bưởi, dâu tây) nếu không có chống chỉ định dạ dày", "Rau xanh, thức ăn thanh đạm dễ tiêu"],
        "kieng_cu": ["Nhịn tiểu hoặc uống ít nước trong ngày", "Rượu bia, cà phê đặc, nước ngọt có ga và đồ ăn quá cay nóng gây kích thích bàng quang", "Vệ sinh kém hoặc tự ý ngưng kháng sinh giữa chừng"]
    },
    "hô hấp": {
        "nen_an": ["Uống nhiều nước ấm (2 - 2.5 lít/ngày) để làm loãng đờm", "Nước cam, chanh ấm mật ong", "Súp gà, cháo thịt băm tía tô gừng ấm"],
        "kieng_cu": ["Uống nước đá lạnh, kem lạnh", "Hút thuốc lá, thuốc lào và tiếp xúc khói bụi", "Rượu bia và đồ ăn chiên rán nhiều dầu mỡ gây kích ứng họng"]
    }
}

DAU_HIEU_DO_CAP_CUU: List[str] = [
    "Sốt cao liên tục trên 39.0°C không hạ sau khi đã dùng thuốc hạ sốt 2 giờ.",
    "Khó thở, thở hụt hơi, thở rít, cảm giác tức nặng ngực dữ dội lan ra vai trái hoặc hàm dưới.",
    "Nôn ra máu tươi hoặc dịch nâu đen; đi ngoài phân đen quánh như bã cà phê có mùi tanh nồng.",
    "Yếu liệt hoặc tê bì đột ngột một bên tay chân, méo mặt, nói ngọng hoặc nhìn mờ đột ngột.",
    "Phát ban mẩn đỏ rầm rộ toàn thân, sưng phù môi, mí mắt, tức ngực hoặc khó nuốt sau khi uống thuốc.",
    "Đau bụng dữ dội liên tục không giảm, bụng gồng cứng như gỗ."
]


def phan_loai_lich_uong_thuoc(danh_sach_thuoc: List[str]) -> Dict[str, List[Dict[str, str]]]:
    """Phân tách danh sách thuốc vào các buổi uống trong ngày: Sáng, Trưa, Chiều/Tối, Trước ngủ.

    Thuốc không có từ khóa thời điểm hoặc tần suất rõ ràng sẽ được đưa vào ``chua_ro_gio``
    để bác sĩ/dược sĩ xác nhận, tuyệt đối không tự động gán vào buổi sáng.
    """
    lich: Dict[str, List[Dict[str, str]]] = {
        "sang": [],
        "trua": [],
        "toi": [],
        "truoc_ngu": [],
        "chua_ro_gio": []
    }
    
    for thuoc_raw in danh_sach_thuoc:
        thuoc_str = thuoc_raw.strip()
        if not thuoc_str:
            continue
        t_low = thuoc_str.lower()
        
        # Nhận diện thời điểm trước / sau ăn
        ghi_chu_an = "Uống sau khi ăn no"
        if any(w in t_low for w in ["trước ăn", "trước bữa", "khi đói", "trước khi ăn"]):
            ghi_chu_an = "Uống TRƯỚC khi ăn 30 phút"
        elif any(w in t_low for w in ["trong bữa", "cùng bữa"]):
            ghi_chu_an = "Uống trong bữa ăn"
        
        # Nhận diện phân bổ buổi uống
        da_gan = False
        
        if "sáng" in t_low:
            lich["sang"].append({"ten_thuoc": thuoc_str, "cach_dung": ghi_chu_an})
            da_gan = True
        if "trưa" in t_low:
            lich["trua"].append({"ten_thuoc": thuoc_str, "cach_dung": ghi_chu_an})
            da_gan = True
        if any(w in t_low for w in ["tối", "chiều"]):
            lich["toi"].append({"ten_thuoc": thuoc_str, "cach_dung": ghi_chu_an})
            da_gan = True
        if any(w in t_low for w in ["trước khi ngủ", "trước khi đi ngủ", "trước ngủ", "trước đi ngủ", "tối trước ngủ", "khi đi ngủ"]):
            lich["truoc_ngu"].append({"ten_thuoc": thuoc_str, "cach_dung": "Uống trước khi đi ngủ 30 phút"})
            da_gan = True
            
        # Nếu không có từ khóa buổi cụ thể, phân tích theo tần suất hoặc nhóm thuốc có giờ uống chuẩn
        if not da_gan:
            if "ngày 2 lần" in t_low or "ngày 2 viên" in t_low or "2 lần/ngày" in t_low or "2 lần / ngày" in t_low:
                lich["sang"].append({"ten_thuoc": thuoc_str, "cach_dung": f"{ghi_chu_an} (Liều 1)"})
                lich["toi"].append({"ten_thuoc": thuoc_str, "cach_dung": f"{ghi_chu_an} (Liều 2)"})
            elif "ngày 3 lần" in t_low or "3 lần/ngày" in t_low or "3 lần / ngày" in t_low:
                lich["sang"].append({"ten_thuoc": thuoc_str, "cach_dung": f"{ghi_chu_an} (Liều 1)"})
                lich["trua"].append({"ten_thuoc": thuoc_str, "cach_dung": f"{ghi_chu_an} (Liều 2)"})
                lich["toi"].append({"ten_thuoc": thuoc_str, "cach_dung": f"{ghi_chu_an} (Liều 3)"})
            elif any(s in t_low for s in ["statin", "atorvastatin", "rosuvastatin", "simvastatin", "pravastatin"]):
                # Statin uống buổi tối
                lich["toi"].append({"ten_thuoc": thuoc_str, "cach_dung": "Uống vào buổi tối sau ăn"})
            elif any(p in t_low for p in ["nexium", "omeprazol", "esomeprazol", "pantoprazol", "rabeprazol", "lansoprazol"]):
                # PPI uống buổi sáng trước ăn 30 phút
                lich["sang"].append({"ten_thuoc": thuoc_str, "cach_dung": ghi_chu_an if "TRƯỚC" in ghi_chu_an else "Uống TRƯỚC khi ăn sáng 30 phút"})
            else:
                # Không đoán mò buổi sáng — gắn cờ để bác sĩ/dược sĩ xác nhận
                lich["chua_ro_gio"].append({
                    "ten_thuoc": thuoc_str,
                    "cach_dung": "Cần bác sĩ/dược sĩ xác nhận giờ uống cụ thể"
                })
                
    return lich


def sinh_ban_dan_do_benh_nhan(
    ten_benh_nhan: str,
    chan_doan: str,
    danh_sach_thuoc: List[str],
    ngay_tai_kham: Optional[str] = "Sau 5 - 7 ngày hoặc khi hết thuốc",
    canh_bao_them: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Sinh toàn bộ tài liệu hướng dẫn và dặn dò người bệnh hoàn chỉnh."""
    ten_bn = ten_benh_nhan if ten_benh_nhan else "Bác / Cô / Chú"
    cd_low = chan_doan.lower()
    
    # 1. Tìm lời giải thích bệnh lý phù hợp nhất
    loi_giai_thich = "Bác đang có tình trạng viêm nhiễm hoặc rối loạn cần được điều trị và theo dõi sát. Hãy tuân thủ hướng dẫn dùng thuốc dưới đây để sức khỏe phục hồi tốt nhất."
    for tu_khoa, gt in GIAI_THICH_BENH_LY.items():
        if tu_khoa in cd_low:
            loi_giai_thich = gt
            break
            
    # 2. Tìm chế độ ăn uống phù hợp (mặc định trung tính tong_quat, không fallback sang hô hấp)
    che_do_an = CHE_DO_AN_UONG_BENH["tong_quat"]
    for nhom, cd in CHE_DO_AN_UONG_BENH.items():
        if nhom == "tong_quat":
            continue
        if (
            nhom in cd_low
            or (nhom == "hô hấp" and any(h in cd_low for h in ["phế quản", "phổi", "họng", "cảm", "hen", "copd"]))
            or (nhom == "suy thận" and "bệnh thận mạn" in cd_low)
            or (nhom == "nhiễm khuẩn tiết niệu" and "tiết niệu" in cd_low)
        ):
            che_do_an = cd
            break
            
    # 3. Phân bổ lịch uống thuốc
    lich_uong = phan_loai_lich_uong_thuoc(danh_sach_thuoc)
    
    # 4. Tập hợp lời dặn đặc biệt
    loi_dan_thuoc = [
        "Uống thuốc với nước lọc đun sôi để nguội. Tuyệt đối không dùng nước trà đặc, nước ngọt có ga hay rượu bia để uống thuốc.",
        "Nếu là viên nang hoặc viên nén bao phim kéo dài: hãy nuốt nguyên viên, không bẻ vụn hay nhai nát.",
        "Uống đủ thời gian theo chỉ định của bác sĩ, không tự ý ngừng thuốc ngay cả khi cảm thấy triệu chứng đã thuyên giảm."
    ]
    if canh_bao_them:
        loi_dan_thuoc.extend(canh_bao_them)
        
    return {
        "tieu_de": f"BẢN HƯỚNG DẪN ĐIỀU TRỊ & DẶN DÒ NGƯỜI BỆNH",
        "nguoi_benh": ten_bn,
        "chan_doan_xac_dinh": chan_doan,
        "giai_thich_benh_don_gian": loi_giai_thich,
        "lich_uong_thuoc": lich_uong,
        "che_do_an_uong": che_do_an,
        "loi_dan_uong_thuoc_an_toan": loi_dan_thuoc,
        "dau_hieu_do_can_cap_cuu": DAU_HIEU_DO_CAP_CUU,
        "hen_tai_kham": ngay_tai_kham
    }


def dinh_dang_van_ban_dan_do(ban_dan_do: Dict[str, Any]) -> str:
    """Định dạng bản dặn dò thành văn bản có cấu trúc rõ ràng để in ấn hoặc hiển thị."""
    lines: List[str] = []
    lines.append("=" * 60)
    lines.append(f"   {ban_dan_do['tieu_de']}")
    lines.append("=" * 60)
    lines.append(f"Kính gửi: {ban_dan_do['nguoi_benh']}")
    lines.append(f"Chẩn đoán: {ban_dan_do['chan_doan_xac_dinh']}")
    lines.append("")
    lines.append("1. HIỂU VỀ TÌNH TRẠNG SỨC KHỎE CỦA BÁC:")
    lines.append(f"   {ban_dan_do['giai_thich_benh_don_gian']}")
    lines.append("")
    lines.append("2. LỊCH UỐNG THUỐC HÀNG NGÀY:")
    
    lich = ban_dan_do["lich_uong_thuoc"]
    khung_gio = [
        ("sang", "☀️ BUỔI SÁNG (7h00 - 8h00):"),
        ("trua", "🌤️ BUỔI TRƯA (11h30 - 12h30):"),
        ("toi", "🌙 BUỔI CHIỀU / TỐI (18h00 - 19h00):"),
        ("truoc_ngu", "🛏️ TRƯỚC KHI ĐI NGỦ (21h00 - 21h30):"),
        ("chua_ro_gio", "⏳ CHƯA RÕ GIỜ UỐNG (Cần hỏi lại bác sĩ/dược sĩ):")
    ]
    
    co_thuoc = False
    for key, label in khung_gio:
        ds = lich.get(key, [])
        if ds:
            co_thuoc = True
            lines.append(f"   {label}")
            for t in ds:
                lines.append(f"      • {t['ten_thuoc']} — {t['cach_dung']}")
                
    if not co_thuoc:
        lines.append("   (Hiện chưa có thuốc kê đơn hoặc theo dõi không dùng thuốc)")
        
    lines.append("")
    lines.append("3. CHẾ ĐỘ ĂN UỐNG & SINH HOẠT HỢP LÝ:")
    an = ban_dan_do["che_do_an_uong"]
    lines.append("   ✓ Những món NÊN ĂN:")
    for na in an.get("nen_an", []):
        lines.append(f"      + {na}")
    lines.append("   ✗ Những thứ CẦN KIÊNG:")
    for kc in an.get("kieng_cu", []):
        lines.append(f"      - {kc}")
        
    lines.append("")
    lines.append("4. NGUYÊN TẮC DÙNG THUỐC AN TOÀN:")
    for ld in ban_dan_do["loi_dan_uong_thuoc_an_toan"]:
        lines.append(f"   • {ld}")
        
    lines.append("")
    lines.append("5. 🚨 DẤU HIỆU CẦN ĐẾN BỆNH VIỆN CẤP CỨU NGAY LẬP TỨC:")
    for rf in ban_dan_do["dau_hieu_do_can_cap_cuu"]:
        lines.append(f"   [!] {rf}")
        
    lines.append("")
    lines.append(f"6. LỊCH TÁI KHÁM: {ban_dan_do['hen_tai_kham']}")
    lines.append("=" * 60)
    
    return "\n".join(lines)
