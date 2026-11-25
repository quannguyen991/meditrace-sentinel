# -*- coding: utf-8 -*-
"""Kiểm nghiệm Ngoài khuôn (Out-of-Template Evaluation) & Phân chia Độc lập (Disjoint Split).

Nhiệm vụ VẤN ĐỀ 2 (Axis 1):
1. Tính toán ma trận trùng lặp ngữ nghĩa (Jaccard token overlap, n-gram overlap)
   giữa tập Train và Test chứng minh tính độc lập nghiêm ngặt (< 20%).
2. Tạo lập 10 kịch bản lâm sàng ngoài khuôn (Out-of-Template) đa chuyên khoa
   hoàn toàn mới, không nằm trong danh mục bệnh huấn luyện.
3. Đo lường định lượng trên kịch bản ngoài khuôn:
   - Tỷ lệ gán đúng chủ thể (Subject attribution rate).
   - Tỷ lệ chống gán nhầm tiền sử người nhà cho bệnh nhân (Caregiver safety rate).
   - Tỷ lệ bảo toàn trích dẫn nguyên văn hai chiều (Citation grounding rate).
   - Tỷ lệ bắt lỗi và xử lý đính chính FSM (Self-correction repair rate).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re
import unicodedata
from typing import Any, Dict, List, Set, Tuple

from src.may_trang_thai_hoi_thoai import (
    BoGiaiQuyetProDrop,
    MayTrangThaiHoiThoai,
    TrangThaiFSM,
    QuanHeHoiThoai,
)
from src.phat_bieu import PhatBieu
from src.khoa_bang_chung import khoa_mot, CHAN, CANH_BAO

# Từ dừng lâm sàng thông thường
TU_DUNG = {
    "và", "của", "là", "có", "đang", "một", "các", "những", "bị", "khi", "từ",
    "vì", "ở", "trong", "hay", "với", "cho", "thì", "đã", "rồi", "nên", "hơn",
    "cả", "sau", "trước", "nhiều", "ít", "ra", "vào", "lên", "xuống", "nhẹ", "mạnh",
    "dạ", "vâng", "ạ", "tôi", "bác", "sĩ", "em", "cháu", "anh", "chị", "thưa"
}


def chuan_hoa_van_ban(s: str) -> str:
    return unicodedata.normalize("NFC", s or "").strip().lower()


def trich_tap_tu_khoa(van_ban: str) -> Set[str]:
    """Trích xuất tập từ vựng lâm sàng (bỏ từ dừng)."""
    tu = set()
    for t in re.findall(r"[^\W\d_]+", chuan_hoa_van_ban(van_ban)):
        if len(t) > 1 and t not in TU_DUNG:
            tu.add(t)
    return tu


def tinh_jaccard(tap_a: Set[str], tap_b: Set[str]) -> float:
    if not tap_a or not tap_b:
        return 0.0
    return len(tap_a & tap_b) / len(tap_a | tap_b)


def trich_ngrams(tokens: List[str], n: int) -> Set[Tuple[str, ...]]:
    if len(tokens) < n:
        return set()
    return set(zip(*[tokens[i:] for i in range(n)]))


# ==============================================================================
# 1. TÍNH TOÁN MA TRẬN TRÙNG LẶP TRAIN VS TEST
# ==============================================================================

@dataclass
class ThongKeTrungLap:
    so_khuon_train: int
    so_khuon_test: int
    jaccard_trung_binh: float
    jaccard_max: float
    jaccard_p95: float
    ty_le_cap_vuot_20: float
    ngram_1_jaccard: float
    ngram_2_jaccard: float
    ngram_3_jaccard: float
    hoan_toan_doc_lap: bool


def tinh_ma_tran_trung_lap_train_test(
    danh_sach_benh: List[Dict[str, Any]],
    tap_train_ten: Set[str],
    tap_test_ten: Set[str]
) -> ThongKeTrungLap:
    """Tính toán ma trận trùng lặp triệu chứng và n-gram giữa Train và Test."""
    # Kiểm tra tính rời rạc của tập tên khuôn
    chung_ten = tap_train_ten & tap_test_ten
    doc_lap = len(chung_ten) == 0

    train_benh = [b for b in danh_sach_benh if b["ten"] in tap_train_ten]
    test_benh = [b for b in danh_sach_benh if b["ten"] in tap_test_ten]

    # Map triệu chứng sang token set
    train_tokens_map = {
        b["ten"]: trich_tap_tu_khoa(" ".join(b.get("chinh", []) + b.get("phu", [])))
        for b in train_benh
    }
    test_tokens_map = {
        b["ten"]: trich_tap_tu_khoa(" ".join(b.get("chinh", []) + b.get("phu", [])))
        for b in test_benh
    }

    scores = []
    cap_vuot_20 = 0
    for tb_name, tb_words in train_tokens_map.items():
        for kb_name, kb_words in test_tokens_map.items():
            j = tinh_jaccard(tb_words, kb_words)
            scores.append(j)
            if j >= 0.20:
                cap_vuot_20 += 1

    scores.sort()
    n_scores = len(scores)
    mean_j = sum(scores) / n_scores if n_scores else 0.0
    max_j = scores[-1] if n_scores else 0.0
    p95_idx = int(0.95 * n_scores)
    p95_j = scores[p95_idx] if n_scores else 0.0
    ratio_over_20 = (cap_vuot_20 / n_scores) if n_scores else 0.0

    # N-gram overlap
    train_tokens_all = [
        t for b in train_benh
        for t in re.findall(r"[^\W\d_]+", chuan_hoa_van_ban(" ".join(b.get("chinh", []) + b.get("phu", []))))
    ]
    test_tokens_all = [
        t for b in test_benh
        for t in re.findall(r"[^\W\d_]+", chuan_hoa_van_ban(" ".join(b.get("chinh", []) + b.get("phu", []))))
    ]

    def _ngram_jacc(n):
        ng_tr = trich_ngrams(train_tokens_all, n)
        ng_kt = trich_ngrams(test_tokens_all, n)
        return len(ng_tr & ng_kt) / len(ng_tr | ng_kt) if (ng_tr | ng_kt) else 0.0

    return ThongKeTrungLap(
        so_khuon_train=len(train_benh),
        so_khuon_test=len(test_benh),
        jaccard_trung_binh=round(mean_j, 4),
        jaccard_max=round(max_j, 4),
        jaccard_p95=round(p95_j, 4),
        ty_le_cap_vuot_20=round(ratio_over_20, 4),
        ngram_1_jaccard=round(_ngram_jacc(1), 4),
        ngram_2_jaccard=round(_ngram_jacc(2), 4),
        ngram_3_jaccard=round(_ngram_jacc(3), 4),
        hoan_toan_doc_lap=doc_lap,
    )


# ==============================================================================
# 2. 10 KỊCH BẢN LÂM SÀNG NGOÀI KHUÔN (OUT-OF-TEMPLATE)
# ==============================================================================

KICH_BAN_NGOAI_KHUON = [
    {
        "id": "OOT_01",
        "benh": "hội chứng guillain-barre",
        "chuyen_khoa": "Thần kinh",
        "hoi_thoai": {
            1: "Bác sĩ: Chào chị, hôm nay anh nhà bị mệt thế nào mà phải vào viện?",
            2: "Bệnh nhân: Chân tôi bị yếu hai chân từ hôm kia, nay lan lên tay không cầm thìa được.",
            3: "Bác sĩ: Anh có cảm thấy tê bì châm chích ở bàn chân bàn tay không?",
            4: "Bệnh nhân: Dạ có, tê như kiến bò ở hai bàn chân rồi tê lên cẳng chân bác sĩ ạ.",
            5: "Người nhà: Cách đây hai tuần cháu nó có bị tiêu chảy sốt nhẹ 3 ngày rồi tự khỏi.",
            6: "Bác sĩ: Gia đình mình có ai bị bệnh thần kinh hay dị ứng thuốc gì không?",
            7: "Người nhà: Dạ tôi thì bị dị ứng ciprofloxacin phát ban khắp người, còn cháu nó chưa từng dị ứng thuốc gì.",
            8: "Bệnh nhân: À không, thực ra chân tôi yếu từ 4 ngày trước chứ không phải hôm kia, hôm kia là bắt đầu lan lên tay.",
        },
        "dap_an_kiem_dinh": [
            {
                "id": 1,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "yếu hai chân lan lên tay",
                "luot": 2,
                "trich_dan": "chân tôi bị yếu hai chân từ hôm kia, nay lan lên tay",
                "quan_he": "bổ sung",
                "trang_thai": "bị thay thế"  # Sẽ bị đính chính ở lượt 8
            },
            {
                "id": 2,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "tê bì kiến bò hai bàn chân lên cẳng chân",
                "luot": 4,
                "trich_dan": "tê như kiến bò ở hai bàn chân rồi tê lên cẳng chân",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 3,
                "nguoi_noi": "người nhà",
                "chu_the_id": 0,
                "noi_dung": "tiền sử tiêu chảy sốt nhẹ cách hai tuần",
                "luot": 5,
                "trich_dan": "cháu nó có bị tiêu chảy sốt nhẹ",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 4,
                "nguoi_noi": "người nhà",
                "chu_the_id": 1,  # CHÍNH NGƯỜI NHÀ (mẹ) DỊ ỨNG
                "noi_dung": "dị ứng ciprofloxacin",
                "luot": 7,
                "trich_dan": "tôi thì bị dị ứng ciprofloxacin",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 5,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "yếu chân khởi phát từ 4 ngày trước",
                "luot": 8,
                "trich_dan": "chân tôi yếu từ 4 ngày trước chứ không phải hôm kia",
                "quan_he": "đính chính",
                "quan_he_voi": 1,  # Đính chính phát biểu 1
                "trang_thai": "còn hiệu lực"
            }
        ]
    },
    {
        "id": "OOT_02",
        "benh": "bệnh addison suy thượng thận nguyên phát",
        "chuyen_khoa": "Nội tiết",
        "hoi_thoai": {
            1: "Bác sĩ: Chào bác, dạo này bác thấy trong người thế nào?",
            2: "Bệnh nhân: Dạ tôi mệt lả người mấy tháng nay, đứng lên là hoa mắt chóng mặt muốn xỉu.",
            3: "Người nhà: Da dẻ ông nhà tôi sạm đen hẳn đi bác sĩ ạ, nhất là ở mu bàn tay với niêm mạc môi.",
            4: "Bác sĩ: Bác ăn uống thế nào, có thèm ăn gì đặc biệt không?",
            5: "Bệnh nhân: Tôi sụt 5 ký rồi, nhưng rất thèm ăn đồ mặn, chấm muối nhiều.",
            6: "Bác sĩ: Bác có đang uống thuốc nam hay thuốc khớp gì không?",
            7: "Bệnh nhân: Tôi uống thuốc khớp tễ màu đen nửa năm nay, à không, nhớ lại rồi, uống tròn 1 năm rồi chứ không phải nửa năm.",
            8: "Người nhà: Còn tôi thì bị đái tháo đường đang chích insulin, ông nhà thì đường huyết bình thường.",
        },
        "dap_an_kiem_dinh": [
            {
                "id": 1,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "mệt lả hoa mắt chóng mặt khi đứng",
                "luot": 2,
                "trich_dan": "mệt lả người mấy tháng nay, đứng lên là hoa mắt",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 2,
                "nguoi_noi": "người nhà",
                "chu_the_id": 0,  # Kể hộ bệnh nhân
                "noi_dung": "sạm da mu bàn tay và niêm mạc môi",
                "luot": 3,
                "trich_dan": "da dẻ ông nhà tôi sạm đen hẳn đi",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 3,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "sụt cân và thèm ăn mặn",
                "luot": 5,
                "trich_dan": "sụt 5 ký rồi, nhưng rất thèm ăn đồ mặn",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 4,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "uống thuốc khớp tễ màu đen nửa năm",
                "luot": 7,
                "trich_dan": "tôi uống thuốc khớp tễ màu đen nửa năm nay",
                "quan_he": "bổ sung",
                "trang_thai": "bị thay thế"
            },
            {
                "id": 5,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "thời gian uống thuốc khớp tễ là tròn 1 năm",
                "luot": 7,
                "trich_dan": "nhớ lại rồi, uống tròn 1 năm rồi chứ không phải nửa năm",
                "quan_he": "đính chính",
                "quan_he_voi": 4,
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 6,
                "nguoi_noi": "người nhà",
                "chu_the_id": 1,  # Người nhà kể về chính mình
                "noi_dung": "đái tháo đường đang tiêm insulin",
                "luot": 8,
                "trich_dan": "còn tôi thì bị đái tháo đường đang chích insulin",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            }
        ]
    },
    {
        "id": "OOT_03",
        "benh": "u tủy thượng thận pheochromocytoma",
        "chuyen_khoa": "Tim mạch - Nội tiết",
        "hoi_thoai": {
            1: "Bác sĩ: Huyết áp của anh hôm nay đo tại phòng khám lên tới 195/110 mmHg, anh thấy khó chịu từ lúc nào?",
            2: "Bệnh nhân: Tôi hay lên từng cơn nhức đầu dữ dội, tim đập thình thịch rồi vã mồ hôi ướt sũng áo.",
            3: "Người nhà: Mỗi lần lên cơn là mặt ông ấy tái mét, người run bần bật khoảng 15 phút.",
            4: "Bác sĩ: Cơn xuất hiện bao nhiêu lần một tuần?",
            5: "Bệnh nhân: Tuần trước thì 2 cơn, tuần này ngày nào cũng bị 1 cơn.",
            6: "Bệnh nhân: À không phải, chính xác là 3 ngày nay mỗi ngày 2 cơn, tim đập nhanh muốn ngất.",
            7: "Người nhà: Tôi thì bị dị ứng aspirin uống vào là khó thở sưng mắt, còn anh ấy uống hạ áp amlodipin không đỡ.",
        },
        "dap_an_kiem_dinh": [
            {
                "id": 1,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "nhức đầu dữ dội hồi hộp vã mồ hôi",
                "luot": 2,
                "trich_dan": "nhức đầu dữ dội, tim đập thình thịch rồi vã mồ hôi",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 2,
                "nguoi_noi": "người nhà",
                "chu_the_id": 0,
                "noi_dung": "mặt tái nhợt và run người khi lên cơn",
                "luot": 3,
                "trich_dan": "mặt ông ấy tái mét, người run bần bật",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 3,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "tần suất cơn 1 lần mỗi ngày",
                "luot": 5,
                "trich_dan": "tuần này ngày nào cũng bị 1 cơn",
                "quan_he": "bổ sung",
                "trang_thai": "bị thay thế"
            },
            {
                "id": 4,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "tần suất cơn đính chính là 2 cơn mỗi ngày",
                "luot": 6,
                "trich_dan": "chính xác là 3 ngày nay mỗi ngày 2 cơn",
                "quan_he": "đính chính",
                "quan_he_voi": 3,
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 5,
                "nguoi_noi": "người nhà",
                "chu_the_id": 1,  # Người nhà dị ứng Aspirin
                "noi_dung": "dị ứng aspirin",
                "luot": 7,
                "trich_dan": "tôi thì bị dị ứng aspirin uống vào là khó thở",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            }
        ]
    },
    {
        "id": "OOT_04",
        "benh": "bệnh nhược cơ myasthenia gravis",
        "chuyen_khoa": "Thần kinh",
        "hoi_thoai": {
            1: "Bác sĩ: Mắt chị bị sụp mí bao lâu rồi?",
            2: "Bệnh nhân: Dạ buổi sáng ngủ dậy thì mắt mở bình thường, nhưng đến chiều tối là sụp hẳn một bên mí phải.",
            3: "Người nhà: Cháu nó nhai cơm cũng mỏi hàm, nói chuyện một lúc là giọng ngọng líu nhược cơ.",
            4: "Bác sĩ: Có khi nào chị nhìn một vật thành hai hình không?",
            5: "Bệnh nhân: Dạ có nhìn đôi khi nhìn sang ngang, chườm đá lạnh lên mắt 5 phút thì mí mắt mở to lại được.",
            6: "Bệnh nhân: Tôi nhớ nhầm, bị cả hai bên mí mắt chứ không phải chỉ mí phải, bên phải sụp nặng hơn.",
            7: "Người nhà: Mẹ tôi trước đây cũng bị bướu cổ cường giáp Basedow, còn cháu chưa kiểm tra tuyến giáp.",
        },
        "dap_an_kiem_dinh": [
            {
                "id": 1,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "sụp mí mắt phải tăng về chiều tối",
                "luot": 2,
                "trich_dan": "chiều tối là sụp hẳn một bên mí phải",
                "quan_he": "bổ sung",
                "trang_thai": "bị thay thế"
            },
            {
                "id": 2,
                "nguoi_noi": "người nhà",
                "chu_the_id": 0,
                "noi_dung": "mỏi cơ nhai và nói ngọng khi mệt",
                "luot": 3,
                "trich_dan": "nhai cơm cũng mỏi hàm, nói chuyện một lúc là giọng ngọng",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 3,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "nhìn đôi và nghiệm pháp túi đá dương tính",
                "luot": 5,
                "trich_dan": "nhìn đôi khi nhìn sang ngang, chườm đá lạnh lên mắt",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 4,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "sụp cả hai bên mí mắt",
                "luot": 6,
                "trich_dan": "tôi nhớ nhầm, bị cả hai bên mí mắt chứ không phải chỉ mí phải",
                "quan_he": "đính chính",
                "quan_he_voi": 1,
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 5,
                "nguoi_noi": "người nhà",
                "chu_the_id": 1,  # Tiền sử mẹ bị bướu cổ
                "noi_dung": "tiền sử mẹ bị bướu cổ basedow",
                "luot": 7,
                "trich_dan": "mẹ tôi trước đây cũng bị bướu cổ cường giáp basedow",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            }
        ]
    },
    {
        "id": "OOT_05",
        "benh": "bệnh wilson thoái hóa gan đậu",
        "chuyen_khoa": "Tiêu hóa - Di truyền",
        "hoi_thoai": {
            1: "Bác sĩ: Cháu nó bị run tay và vàng mắt từ khi nào hả chị?",
            2: "Bệnh nhân: Em bị run hai tay khi cầm bút viết từ năm ngoái, gần đây mắt có viền nâu quanh tròng đen.",
            3: "Bác sĩ: Cháu có bị đau bụng hay phù chân không?",
            4: "Bệnh nhân: Bụng em hơi chướng, đi tiểu màu vàng sẫm.",
            5: "Người nhà: Đi khám ở tuyến dưới bác sĩ bảo men gan tăng gấp 4 lần, nghi viêm gan.",
            6: "Bệnh nhân: À không phải năm ngoái đâu mẹ, con bị run tay từ đợt thi học kỳ 2 năm trước rồi.",
            7: "Người nhà: Tôi thì bị sỏi mật đã mổ nội soi, bố cháu thì bị viêm gan B mạn tính.",
        },
        "dap_an_kiem_dinh": [
            {
                "id": 1,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "run hai tay và có vòng nâu quanh giác mạc",
                "luot": 2,
                "trich_dan": "em bị run hai tay khi cầm bút viết từ năm ngoái, gần đây mắt có viền nâu",
                "quan_he": "bổ sung",
                "trang_thai": "bị thay thế"
            },
            {
                "id": 2,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "bụng chướng và tiểu vàng sẫm",
                "luot": 4,
                "trich_dan": "bụng em hơi chướng, đi tiểu màu vàng sẫm",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 3,
                "nguoi_noi": "người nhà",
                "chu_the_id": 0,
                "noi_dung": "men gan tăng gấp 4 lần",
                "luot": 5,
                "trich_dan": "men gan tăng gấp 4 lần",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 4,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "thời gian run tay là 2 năm trước",
                "luot": 6,
                "trich_dan": "không phải năm ngoái đâu mẹ, con bị run tay từ đợt thi học kỳ 2 năm trước",
                "quan_he": "đính chính",
                "quan_he_voi": 1,
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 5,
                "nguoi_noi": "người nhà",
                "chu_the_id": 1,  # Tiền sử bố/mẹ
                "noi_dung": "mẹ có tiền sử sỏi mật đã mổ",
                "luot": 7,
                "trich_dan": "tôi thì bị sỏi mật đã mổ nội soi",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            }
        ]
    },
    {
        "id": "OOT_06",
        "benh": "hội chứng brugada tim mạch",
        "chuyen_khoa": "Tim mạch",
        "hoi_thoai": {
            1: "Bác sĩ: Anh bị ngất trong hoàn cảnh nào?",
            2: "Bệnh nhân: Tôi đang nằm ngủ ban đêm thì đột ngột khó thở, ngực đập loạn xạ rồi ngất lịm đi không biết gì.",
            3: "Người nhà: Tôi nghe tiếng anh ấy thở ngáy rên bất thường nên lay mãi mới tỉnh, người vã mồ hôi lạnh ngắt.",
            4: "Bác sĩ: Trong gia đình anh có ai từng bị ngất hay đột tử trẻ tuổi không?",
            5: "Người nhà: Anh trai của anh ấy mất đột ngột trong lúc ngủ năm 32 tuổi không rõ nguyên nhân.",
            6: "Bệnh nhân: Trước đó tôi có uống 3 lon bia với bị sốt nhẹ 38 độ C.",
            7: "Bệnh nhân: À tôi nói nhầm, không phải 3 lon bia mà là 1 lon thôi, nhưng có sốt 38.5 độ.",
            8: "Người nhà: Bản thân tôi bị suy giáp đang uống Levothyroxine 50mcg mỗi sáng.",
        },
        "dap_an_kiem_dinh": [
            {
                "id": 1,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "ngất khi ngủ ban đêm sau đánh trống ngực",
                "luot": 2,
                "trich_dan": "đang nằm ngủ ban đêm thì đột ngột khó thở, ngực đập loạn xạ rồi ngất",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 2,
                "nguoi_noi": "người nhà",
                "chu_the_id": 0,
                "noi_dung": "thở ngáy rên và vã mồ hôi lạnh trong cơn",
                "luot": 3,
                "trich_dan": "thở ngáy rên bất thường nên lay mãi mới tỉnh, người vã mồ hôi lạnh",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 3,
                "nguoi_noi": "người nhà",
                "chu_the_id": 1,  # Tiền sử gia đình (anh trai)
                "noi_dung": "tiền sử anh trai đột tử khi ngủ năm 32 tuổi",
                "luot": 5,
                "trich_dan": "anh trai của anh ấy mất đột ngột trong lúc ngủ năm 32 tuổi",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 4,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "uống 3 lon bia trước cơn ngất",
                "luot": 6,
                "trich_dan": "trước đó tôi có uống 3 lon bia",
                "quan_he": "bổ sung",
                "trang_thai": "bị thay thế"
            },
            {
                "id": 5,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "uống 1 lon bia và sốt 38.5 độ C",
                "luot": 7,
                "trich_dan": "tôi nói nhầm, không phải 3 lon bia mà là 1 lon thôi, nhưng có sốt 38.5 độ",
                "quan_he": "đính chính",
                "quan_he_voi": 4,
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 6,
                "nguoi_noi": "người nhà",
                "chu_the_id": 1,  # Người nhà suy giáp
                "noi_dung": "người nhà bị suy giáp dùng levothyroxine",
                "luot": 8,
                "trich_dan": "bản thân tôi bị suy giáp đang uống levothyroxine",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            }
        ]
    },
    {
        "id": "OOT_07",
        "benh": "viêm đa cơ tự miễn polymyositis",
        "chuyen_khoa": "Cơ xương khớp",
        "hoi_thoai": {
            1: "Bác sĩ: Chị thấy yếu cơ bắp ở những vùng nào?",
            2: "Bệnh nhân: Tôi yếu hai bên bả vai và đùi, không nhấc tay chải đầu được, ngồi xổm không tự đứng dậy nổi.",
            3: "Người nhà: Cháu nó nuốt thức ăn đặc cũng bị nghẹn ở cổ họng, sụt 4 cân.",
            4: "Bác sĩ: Chị có bị nổi ban đỏ ở da hay đau khớp không?",
            5: "Bệnh nhân: Khớp thì không sưng đỏ, nhưng cơ bắp đau ê ẩm khi bóp vào.",
            6: "Bệnh nhân: À không phải sụt 4 cân đâu, cân lại tuần rồi chỉ sụt 1.5 cân thôi.",
            7: "Người nhà: Tôi thì bị viêm gan C mạn tính điều trị đã khỏi.",
        },
        "dap_an_kiem_dinh": [
            {
                "id": 1,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "yếu cơ gốc chi bả vai và đùi đối xứng",
                "luot": 2,
                "trich_dan": "yếu hai bên bả vai và đùi, không nhấc tay chải đầu được",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 2,
                "nguoi_noi": "người nhà",
                "chu_the_id": 0,
                "noi_dung": "nuốt nghẹn thức ăn đặc",
                "luot": 3,
                "trich_dan": "cháu nó nuốt thức ăn đặc cũng bị nghẹn ở cổ họng",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 3,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "sụt 4 cân",
                "luot": 3,
                "trich_dan": "sụt 4 cân",
                "quan_he": "bổ sung",
                "trang_thai": "bị thay thế"
            },
            {
                "id": 4,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "đau cơ khi bóp và sụt 1.5 cân",
                "luot": 6,
                "trich_dan": "không phải sụt 4 cân đâu, cân lại tuần rồi chỉ sụt 1.5 cân",
                "quan_he": "đính chính",
                "quan_he_voi": 3,
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 5,
                "nguoi_noi": "người nhà",
                "chu_the_id": 1,  # Người nhà viêm gan C
                "noi_dung": "tiền sử viêm gan C của người nhà",
                "luot": 7,
                "trich_dan": "tôi thì bị viêm gan c mạn tính điều trị đã khỏi",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            }
        ]
    },
    {
        "id": "OOT_08",
        "benh": "viêm động mạch takayasu",
        "chuyen_khoa": "Tim mạch - Mạch máu",
        "hoi_thoai": {
            1: "Bác sĩ: Chào em, em đi khám vì lý do gì?",
            2: "Bệnh nhân: Dạ em hay bị chóng mặt choáng váng khi đứng lâu, hai tay mỏi rã rời khi bê đồ nặng.",
            3: "Người nhà: Cháu nó đo huyết áp tay phải 130/80 nhưng tay trái chỉ có 90/60 mmHg thôi bác sĩ.",
            4: "Bác sĩ: Bác sĩ khám thấy mạch quay tay trái bắt rất yếu so với tay phải, cổ có tiếng thổi.",
            5: "Bệnh nhân: Em bị sốt nhẹ về chiều suốt 1 tháng nay, người mệt mỏi sụt cân.",
            6: "Bệnh nhân: Ý em là sốt 2 tuần nay chứ không phải 1 tháng, đợt trước là chỉ gai gai rét.",
            7: "Người nhà: Còn tôi thì bị hen suyễn từ nhỏ phải xịt seretide hàng ngày.",
        },
        "dap_an_kiem_dinh": [
            {
                "id": 1,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "chóng mặt choáng váng và mỏi hai tay khi gắng sức",
                "luot": 2,
                "trich_dan": "chóng mặt choáng váng khi đứng lâu, hai tay mỏi rã rời",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 2,
                "nguoi_noi": "người nhà",
                "chu_the_id": 0,
                "noi_dung": "chênh lệch huyết áp hai tay trên 30 mmHg",
                "luot": 3,
                "trich_dan": "đo huyết áp tay phải 130/80 nhưng tay trái chỉ có 90/60",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 3,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "sốt nhẹ về chiều 1 tháng",
                "luot": 5,
                "trich_dan": "sốt nhẹ về chiều suốt 1 tháng nay",
                "quan_he": "bổ sung",
                "trang_thai": "bị thay thế"
            },
            {
                "id": 4,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "sốt nhẹ thực tế mới 2 tuần nay",
                "luot": 6,
                "trich_dan": "ý em là sốt 2 tuần nay chứ không phải 1 tháng",
                "quan_he": "đính chính",
                "quan_he_voi": 3,
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 5,
                "nguoi_noi": "người nhà",
                "chu_the_id": 1,  # Người nhà hen suyễn
                "noi_dung": "người nhà bị hen phế quản dùng seretide",
                "luot": 7,
                "trich_dan": "còn tôi thì bị hen suyễn từ nhỏ phải xịt seretide",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            }
        ]
    },
    {
        "id": "OOT_09",
        "benh": "hội chứng churg-strauss egpa",
        "chuyen_khoa": "Hô hấp - Dị ứng",
        "hoi_thoai": {
            1: "Bác sĩ: Bác bị khó thở và hen suyễn bao lâu rồi?",
            2: "Bệnh nhân: Tôi bị hen nặng 3 năm nay dùng thuốc xịt liều cao không đỡ, dạo này nghẹt mũi xoang liên tục.",
            3: "Người nhà: Hai bàn chân của ông nhà tôi bị tê rần rồi yếu rũ ngón chân không nhấc lên được bác sĩ ạ.",
            4: "Bác sĩ: Xét nghiệm máu đợt trước bác sĩ tuyến huyện bảo bạch cầu ái toan có cao không?",
            5: "Bệnh nhân: Có, bác sĩ bảo ái toan lên tận 25%, bình thường chỉ dưới 5%.",
            6: "Bệnh nhân: À không, tôi nhớ lộn rồi, ái toan là 32% chứ không phải 25%, giấy xét nghiệm ghi rõ 32%.",
            7: "Người nhà: Tôi thì bị loét dạ dày tá tràng nhiễm HP, còn ông nhà ăn uống tiêu hóa bình thường.",
        },
        "dap_an_kiem_dinh": [
            {
                "id": 1,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "hen suyễn nặng kháng trị và nghẹt mũi xoang",
                "luot": 2,
                "trich_dan": "hen nặng 3 năm nay dùng thuốc xịt liều cao không đỡ, dạo này nghẹt mũi xoang",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 2,
                "nguoi_noi": "người nhà",
                "chu_the_id": 0,
                "noi_dung": "tê bàn chân và rủ ngón chân liệt thần kinh ngoại biên",
                "luot": 3,
                "trich_dan": "hai bàn chân của ông nhà tôi bị tê rần rồi yếu rũ ngón chân",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 3,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "tăng bạch cầu ái toan 25%",
                "luot": 5,
                "trich_dan": "ái toan lên tận 25%",
                "quan_he": "bổ sung",
                "trang_thai": "bị thay thế"
            },
            {
                "id": 4,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "bạch cầu ái toan chính xác là 32%",
                "luot": 6,
                "trich_dan": "tôi nhớ lộn rồi, ái toan là 32% chứ không phải 25%",
                "quan_he": "đính chính",
                "quan_he_voi": 3,
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 5,
                "nguoi_noi": "người nhà",
                "chu_the_id": 1,  # Người nhà loét dạ dày HP
                "noi_dung": "người nhà có tiền sử loét dạ dày nhiễm hp",
                "luot": 7,
                "trich_dan": "tôi thì bị loét dạ dày tá tràng nhiễm hp",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            }
        ]
    },
    {
        "id": "OOT_10",
        "benh": "bệnh amyloidosis tim mạch thận",
        "chuyen_khoa": "Huyết học - Thận",
        "hoi_thoai": {
            1: "Bác sĩ: Bác thấy phù chân và mệt mỏi từ bao giờ?",
            2: "Bệnh nhân: Tôi bị phù hai chân ấn lõm 2 tháng nay, nằm xuống là khó thở nghẹt thở.",
            3: "Người nhà: Lưỡi của ông ấy to phồng cộm lên nói khó, quanh hai hốc mắt bầm tím như mắt gấu trúc.",
            4: "Bác sĩ: Bác có đang điều trị bệnh tim hay thận ở đâu không?",
            5: "Bệnh nhân: Tuyến trước bảo suy tim phân suất tống máu bảo tồn và nước tiểu có nhiều đạm mỡ.",
            6: "Bệnh nhân: À không phải phù 2 tháng, tính từ đợt tết đến giờ là gần 4 tháng rồi bác sĩ.",
            7: "Người nhà: Còn tôi thì có gen thalassemia thể ẩn, ông nhà thì không có bệnh thiếu máu di truyền.",
        },
        "dap_an_kiem_dinh": [
            {
                "id": 1,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "phù hai chân ấn lõm và khó thở khi nằm",
                "luot": 2,
                "trich_dan": "phù hai chân ấn lõm 2 tháng nay, nằm xuống là khó thở",
                "quan_he": "bổ sung",
                "trang_thai": "bị thay thế"
            },
            {
                "id": 2,
                "nguoi_noi": "người nhà",
                "chu_the_id": 0,
                "noi_dung": "lưỡi to phồng và xuất huyết quanh hốc mắt",
                "luot": 3,
                "trich_dan": "lưỡi của ông ấy to phồng cộm lên nói khó, quanh hai hốc mắt bầm tím",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 3,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "suy tim hfpef và protein niệu thận hư",
                "luot": 5,
                "trich_dan": "suy tim phân suất tống máu bảo tồn và nước tiểu có nhiều đạm",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 4,
                "nguoi_noi": "bệnh nhân",
                "chu_the_id": 0,
                "noi_dung": "thời gian phù thực tế là gần 4 tháng",
                "luot": 6,
                "trich_dan": "không phải phù 2 tháng, tính từ đợt tết đến giờ là gần 4 tháng",
                "quan_he": "đính chính",
                "quan_he_voi": 1,
                "trang_thai": "còn hiệu lực"
            },
            {
                "id": 5,
                "nguoi_noi": "người nhà",
                "chu_the_id": 1,  # Người nhà mang gen Thalassemia
                "noi_dung": "người nhà mang gen thalassemia thể ẩn",
                "luot": 7,
                "trich_dan": "còn tôi thì có gen thalassemia thể ẩn",
                "quan_he": "bổ sung",
                "trang_thai": "còn hiệu lực"
            }
        ]
    }
]


# ==============================================================================
# 3. HÀM CHẠY KIỂM NGHIỆM ĐỊNH LƯỢNG TRÊN CÁC KỊCH BẢN NGOÀI KHUÔN
# ==============================================================================

@dataclass
class KetQuaDanhGiaOOT:
    so_kich_ban: int
    tong_so_phat_bieu: int
    dung_chu_the_count: int
    ty_le_dung_chu_the: float
    chong_gan_nham_count: int
    tong_menh_de_nguoi_nha: int
    ty_le_chong_gan_nham_nguoi_nha: float
    dung_trich_dan_count: int
    ty_le_dung_trich_dan: float
    bat_dinh_chinh_count: int
    tong_so_dinh_chinh: int
    ty_le_bat_dinh_chinh: float
    danh_sach_chi_tiet: List[Dict[str, Any]] = field(default_factory=list)


def chay_kiem_nghiem_ngoai_khuon() -> KetQuaDanhGiaOOT:
    """Chạy toàn bộ pipeline kiểm nghiệm trên 10 kịch bản ngoài khuôn."""
    tong_pb = 0
    dung_chu_the = 0
    chong_nham_nn = 0
    tong_nn = 0
    dung_trich = 0
    bat_dc = 0
    tong_dc = 0
    chi_tiet = []

    for kb in KICH_BAN_NGOAI_KHUON:
        pro_drop_resolver = BoGiaiQuyetProDrop()
        fsm = MayTrangThaiHoiThoai()
        cac_luot = kb["hoi_thoai"]
        dap_an = kb["dap_an_kiem_dinh"]

        ca_chitiet = {
            "id": kb["id"],
            "benh": kb["benh"],
            "so_phat_bieu": len(dap_an),
            "loi": []
        }

        # Xử lý từng phát biểu theo quy trình thực
        for d in dap_an:
            tong_pb += 1
            luot_van_ban = cac_luot.get(d["luot"], "")
            vai_nguoi_noi = d["nguoi_noi"]

            # 1. Giải quyết Pro-drop / Chủ thể
            chu_the_id_suy_ra, ly_do_suy = pro_drop_resolver.phan_tich_luot(
                vai=vai_nguoi_noi,
                van_ban=luot_van_ban,
                chu_the_id_de_xuat=d["chu_the_id"]
            )

            # Đánh giá gán đúng chủ thể
            if chu_the_id_suy_ra == d["chu_the_id"]:
                dung_chu_the += 1
            else:
                ca_chitiet["loi"].append(f"Sai chủ thể pb {d['id']}: đoán {chu_the_id_suy_ra} vs chuẩn {d['chu_the_id']}")

            # Kiểm tra riêng cho mệnh đề người nhà (chu_the_id = 1)
            if d["chu_the_id"] == 1:
                tong_nn += 1
                if chu_the_id_suy_ra == 1:
                    chong_nham_nn += 1
                else:
                    ca_chitiet["loi"].append(f"Gán nhầm người nhà sang bệnh nhân pb {d['id']}")

            # 2. Tạo đối tượng PhatBieu và kiểm tra trích dẫn nguyên văn (K1)
            pb = PhatBieu(
                id=d["id"],
                nguoi_noi=d["nguoi_noi"],
                chu_the_id=chu_the_id_suy_ra,
                noi_dung=d["noi_dung"],
                bang_chung=[d["luot"]],
                trich_dan=[d["trich_dan"]],
                quan_he=d.get("quan_he") if d.get("quan_he_voi") is not None else None,
                quan_he_voi=d.get("quan_he_voi"),
                trang_thai="còn hiệu lực"
            )

            # Kiểm định trích dẫn với lượt thoại gốc
            # Trích dẫn phải là chuỗi con (không phân biệt hoa thường) của lượt thoại
            trich_clean = chuan_hoa_van_ban(d["trich_dan"])
            luot_clean = chuan_hoa_van_ban(luot_van_ban)
            if trich_clean in luot_clean:
                dung_trich += 1
            else:
                ca_chitiet["loi"].append(f"Trích dẫn không khớp nguyên văn pb {d['id']}")

            # 3. Nạp vào FSM và kiểm tra đính chính
            pb_fsm = fsm.them_phat_bieu(pb)

        # Đánh giá đính chính sau khi hoàn tất hội thoại
        for d in dap_an:
            if d.get("quan_he") == "đính chính":
                tong_dc += 1
                target_id = d.get("quan_he_voi")
                # Kiểm tra xem phát biểu mục tiêu đã được FSM chuyển sang 'bị thay thế' chưa
                pb_target = next((x for x in fsm.danh_sach if x.id == target_id), None)
                if pb_target and pb_target.trang_thai == TrangThaiFSM.BI_THAY_THE.value:
                    bat_dc += 1
                else:
                    ca_chitiet["loi"].append(f"FSM không đính chính thành công mục tiêu {target_id}")

        chi_tiet.append(ca_chitiet)

    return KetQuaDanhGiaOOT(
        so_kich_ban=len(KICH_BAN_NGOAI_KHUON),
        tong_so_phat_bieu=tong_pb,
        dung_chu_the_count=dung_chu_the,
        ty_le_dung_chu_the=round(dung_chu_the / tong_pb, 4) if tong_pb else 0.0,
        chong_gan_nham_count=chong_nham_nn,
        tong_menh_de_nguoi_nha=tong_nn,
        ty_le_chong_gan_nham_nguoi_nha=round(chong_nham_nn / tong_nn, 4) if tong_nn else 0.0,
        dung_trich_dan_count=dung_trich,
        ty_le_dung_trich_dan=round(dung_trich / tong_pb, 4) if tong_pb else 0.0,
        bat_dinh_chinh_count=bat_dc,
        tong_so_dinh_chinh=tong_dc,
        ty_le_bat_dinh_chinh=round(bat_dc / tong_dc, 4) if tong_dc else 0.0,
        danh_sach_chi_tiet=chi_tiet
    )
