# -*- coding: utf-8 -*-
"""Ba ca mau da nguoi noi dung san cho nut 'Xem thu voi ca mau' khi khong co `kaggle-ra/`.

Muc dich (Yeu cau 2 - AI 2026 Chang 1):
  1. `demo_bs_nguoi_nha_nhi`: Bac si - Me (Nguoi nha) - Benh nhi (6 tuoi).
     Me ke ho trieu chung, be tu dinh chinh so ngay sot (4 ngay -> chieu hom qua),
     me khai chinh me di ung Penicillin (tach sang TIEN SU GIA DINH, khong lot vao DI UNG cua be),
     cau dieu kien cap cuu nam o CAN XAC NHAN.
  2. `demo_hai_benh_nhan`: Tinh huong HAI BENH NHAN cung trao doi trong phong kham
     (hai vo chong cung kham ngoai tru): tach chu the giua nguoi benh chinh va nguoi di cung,
     mot cau luoc chu ngu mo ho bi day sang CAN XAC NHAN de bac si xac nhan.
  3. `demo_lao_khoa_con_gai`: Bac si - Cu ong 74 tuoi - Con gai.
     Con gai khai bo quen thuoc ca tuan, bo dinh chinh chi quen hom kia (van uong Amlodipin 5mg),
     di ung Aspirin cua con gai tach khoi benh nhan, ten thuoc khau ngu can bac si xac nhan.

Moi ca deu chay that qua `src.nhanh.chay_trung_gian(..., kq_tho=[...])` (100% luat xac dinh,
khong can GPU, < 50ms) va gan nhan trung thuc `nguon = "chay_truoc"`, `bo = "demo_bgk"`.
"""
from __future__ import annotations

import copy
from functools import lru_cache
from typing import Dict, List

BO_DEMO_BGK = "demo_bgk"

_DU_LIEU_CA_DEMO: List[Dict] = [
    {
        "id": "demo_bs_nguoi_nha_nhi",
        "ten_hien_thi": "Ca mẫu 1 · Bác sĩ – Mẹ – Bệnh nhi (Đính chính & Dị ứng người nhà)",
        "input": "\n".join([
            "Bác sĩ: Chào hai mẹ con, hôm nay bé bị làm sao thế chị?",
            "Người nhà: Dạ thưa bác sĩ, cháu nó bị sốt cao với ho đờm từ 4 ngày nay, thở khò khè.",
            "Bệnh nhân: Dạ không phải 4 ngày đâu ạ, con mới bị sốt nóng từ chiều hôm qua thôi mẹ.",
            "Người nhà: À đúng rồi bác sĩ, mẹ nhớ nhầm sang đợt húng hắng ho, chứ sốt nóng thì mới từ chiều hôm qua thôi.",
            "Bác sĩ: Ở nhà chị có cho cháu uống thuốc gì chưa, và bé hay chị có dị ứng thuốc gì không?",
            "Người nhà: Dạ em có cho cháu uống một gói hapacol 250mg hạ sốt. Bản thân tôi thì bị dị ứng penicillin nổi mề đay khó thở, còn cháu từ nhỏ đến giờ chưa thấy bị dị ứng thuốc gì cả.",
            "Bác sĩ: Bác khám phổi cháu có ran ẩm rải rác hai bên, họng đỏ xung huyết. Chẩn đoán cháu bị viêm phế quản cấp.",
            "Bác sĩ: Tôi kê siro ho thảo dược và hạ sốt khi cần. Nếu đêm nay cháu sốt cao trên 39 độ hoặc thở rút lõm lồng ngực thì chị đưa cháu vào viện ngay nhé.",
        ]),
        "metadata": [
            {"luot": 1, "speaker_id": "doctor", "speaker_role": "doctor", "audio_start": 0.0, "audio_end": 3.4},
            {"luot": 2, "speaker_id": "caregiver", "speaker_role": "caregiver", "audio_start": 3.6, "audio_end": 8.9},
            {"luot": 3, "speaker_id": "patient", "speaker_role": "patient", "audio_start": 9.2, "audio_end": 13.8},
            {"luot": 4, "speaker_id": "caregiver", "speaker_role": "caregiver", "audio_start": 14.0, "audio_end": 18.8},
            {"luot": 5, "speaker_id": "doctor", "speaker_role": "doctor", "audio_start": 19.1, "audio_end": 24.5},
            {"luot": 6, "speaker_id": "caregiver", "speaker_role": "caregiver", "audio_start": 24.8, "audio_end": 34.2},
            {"luot": 7, "speaker_id": "doctor", "speaker_role": "doctor", "audio_start": 34.6, "audio_end": 40.4},
            {"luot": 8, "speaker_id": "doctor", "speaker_role": "doctor", "audio_start": 40.8, "audio_end": 48.5},
        ],
        "phat_bieu": [
            {
                "id": 0,
                "nguoi_noi": "người nhà",
                "chu_the": "bệnh nhân",
                "noi_dung": "ho đờm, thở khò khè",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "tự kể",
                "thoi_gian_su_kien": "hiện tại",
                "luot_thoai": [2],
                "trich_dan": ["cháu nó bị sốt cao với ho đờm từ 4 ngày nay, thở khò khè"],
            },
            {
                "id": 1,
                "nguoi_noi": "người nhà",
                "chu_the": "bệnh nhân",
                "noi_dung": "sốt cao 4 ngày nay",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "tự kể",
                "moc_thoi_gian": "4 ngày nay",
                "thoi_gian_su_kien": "hiện tại",
                "luot_thoai": [2],
                "trich_dan": ["sốt cao với ho đờm từ 4 ngày nay"],
            },
            {
                "id": 2,
                "nguoi_noi": "bệnh nhân",
                "chu_the": "bệnh nhân",
                "noi_dung": "sốt nóng từ chiều hôm qua",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "tự kể",
                "moc_thoi_gian": "chiều hôm qua",
                "thoi_gian_su_kien": "hiện tại",
                "quan_he": "đính chính",
                "quan_he_voi": 1,
                "luot_thoai": [3],
                "trich_dan": ["không phải 4 ngày đâu ạ, con mới bị sốt nóng từ chiều hôm qua thôi"],
            },
            {
                "id": 3,
                "nguoi_noi": "người nhà",
                "chu_the": "bệnh nhân",
                "noi_dung": "đang dùng hapacol",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "trả lời",
                "thoi_gian_su_kien": "hiện tại",
                "thuoc": {"ten": "hapacol", "lieu": "250mg", "duong_dung": "uống", "trang_thai_dung": "đang dùng"},
                "luot_thoai": [6],
                "trich_dan": ["cho cháu uống một gói hapacol 250mg hạ sốt"],
            },
            {
                "id": 4,
                "nguoi_noi": "người nhà",
                "chu_the": "mẹ",
                "noi_dung": "dị ứng penicillin nổi mề đay khó thở",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "trả lời",
                "thoi_gian_su_kien": "quá khứ",
                "luot_thoai": [6],
                "trich_dan": ["bản thân tôi thì bị dị ứng penicillin nổi mề đay khó thở"],
            },
            {
                "id": 5,
                "nguoi_noi": "người nhà",
                "chu_the": "bệnh nhân",
                "noi_dung": "dị ứng thuốc",
                "do_chac_chan": "chưa ghi nhận",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "trả lời",
                "thoi_gian_su_kien": "quá khứ",
                "luot_thoai": [6],
                "trich_dan": ["cháu từ nhỏ đến giờ chưa thấy bị dị ứng thuốc gì cả"],
            },
            {
                "id": 6,
                "nguoi_noi": "bác sĩ",
                "chu_the": "bệnh nhân",
                "noi_dung": "phổi có ran ẩm rải rác hai bên, họng đỏ xung huyết",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "quan sát",
                "thoi_gian_su_kien": "hiện tại",
                "luot_thoai": [7],
                "trich_dan": ["phổi cháu có ran ẩm rải rác hai bên, họng đỏ xung huyết"],
            },
            {
                "id": 7,
                "nguoi_noi": "bác sĩ",
                "chu_the": "bệnh nhân",
                "noi_dung": "viêm phế quản cấp",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "nhận định",
                "thoi_gian_su_kien": "hiện tại",
                "luot_thoai": [7],
                "trich_dan": ["chẩn đoán cháu bị viêm phế quản cấp"],
            },
            {
                "id": 8,
                "nguoi_noi": "bác sĩ",
                "chu_the": "bệnh nhân",
                "noi_dung": "đưa cháu vào viện ngay nếu sốt cao trên 39 độ hoặc thở rút lõm lồng ngực",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "giả định",
                "hanh_vi": "kế hoạch",
                "thoi_gian_su_kien": "hiện tại",
                "luot_thoai": [8],
                "trich_dan": ["nếu đêm nay cháu sốt cao trên 39 độ hoặc thở rút lõm lồng ngực thì chị đưa cháu vào viện ngay"],
            },
        ],
    },
    {
        "id": "demo_hai_benh_nhan",
        "ten_hien_thi": "Ca mẫu 2 · Hai người bệnh cùng phòng trao đổi (Chống ghi nhầm người)",
        "input": "\n".join([
            "Bác sĩ: Mời anh Minh vào khám trước, còn chị ngồi cạnh chờ tới lượt sổ khám sau nhé.",
            "Bệnh nhân: Dạ chào bác sĩ, tôi đau tức vùng thượng vị âm ỉ 5 hôm nay, hay ợ chua nóng rát sau ăn.",
            "Người nhà: Bác sĩ ơi tiện thể cho tôi hỏi luôn, tôi là bệnh nhân sổ kế tiếp, tôi bị đái tháo đường đang uống metformin 500mg mà dạo này hay tê đầu ngón chân lắm.",
            "Bác sĩ: Chị ngồi chờ chút tôi khám xong hồ sơ của anh Minh trước đã nhé. Anh Minh trước giờ có tiền sử bệnh dạ dày hay dị ứng thuốc gì không?",
            "Bệnh nhân: Dạ tôi không dị ứng thuốc gì cả, chỉ có thói quen uống cà phê đặc buổi sáng.",
            "Người nhà: Còn tôi thì bị dị ứng cefuroxim phát ban đỏ khắp người đấy bác sĩ nhớ ghi vào sổ của tôi nhé, với lại đêm qua còn nôn hai lần nữa.",
            "Bác sĩ: Tôi nghe rõ rồi, phần của chị lát mở đúng mã bệnh nhân của chị tôi mới ghi, còn câu nôn hai lần đêm qua là của chị hay của anh Minh để bác sĩ xác nhận lại nhé. Khám anh Minh thấy ấn đau nhẹ thượng vị, bụng mềm, theo dõi viêm dạ dày trào ngược.",
        ]),
        "metadata": [
            {"luot": 1, "speaker_id": "doctor", "speaker_role": "doctor", "audio_start": 0.0, "audio_end": 4.2},
            {"luot": 2, "speaker_id": "patient", "speaker_role": "patient", "audio_start": 4.5, "audio_end": 10.1},
            {"luot": 3, "speaker_id": "caregiver", "speaker_role": "caregiver", "audio_start": 10.4, "audio_end": 18.6},
            {"luot": 4, "speaker_id": "doctor", "speaker_role": "doctor", "audio_start": 18.9, "audio_end": 25.0},
            {"luot": 5, "speaker_id": "patient", "speaker_role": "patient", "audio_start": 25.3, "audio_end": 30.1},
            {"luot": 6, "speaker_id": "caregiver", "speaker_role": "caregiver", "audio_start": 30.5, "audio_end": 38.4},
            {"luot": 7, "speaker_id": "doctor", "speaker_role": "doctor", "audio_start": 38.8, "audio_end": 49.0},
        ],
        "phat_bieu": [
            {
                "id": 1,
                "nguoi_noi": "bệnh nhân",
                "chu_the": "bệnh nhân",
                "noi_dung": "đau tức vùng thượng vị âm ỉ, ợ chua nóng rát sau ăn",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "tự kể",
                "moc_thoi_gian": "5 hôm nay",
                "thoi_gian_su_kien": "hiện tại",
                "luot_thoai": [2],
                "trich_dan": ["đau tức vùng thượng vị âm ỉ 5 hôm nay, hay ợ chua nóng rát sau ăn"],
            },
            {
                "id": 2,
                "nguoi_noi": "người nhà",
                "chu_the": "vợ",
                "noi_dung": "đái tháo đường đang uống metformin 500mg, tê đầu ngón chân",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "tự kể",
                "thoi_gian_su_kien": "hiện tại",
                "luot_thoai": [3],
                "trich_dan": ["tôi bị đái tháo đường đang uống metformin 500mg mà dạo này hay tê đầu ngón chân"],
            },
            {
                "id": 3,
                "nguoi_noi": "bệnh nhân",
                "chu_the": "bệnh nhân",
                "noi_dung": "dị ứng thuốc",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": True,
                "tinh_huong": "thực tế",
                "hanh_vi": "trả lời",
                "thoi_gian_su_kien": "quá khứ",
                "luot_thoai": [5],
                "trich_dan": ["tôi không dị ứng thuốc gì cả"],
            },
            {
                "id": 4,
                "nguoi_noi": "người nhà",
                "chu_the": "bệnh nhân",  # Co y de khoa K3 chan: nguoi di cung noi "Con toi thi bi di ung cefuroxim"!
                "noi_dung": "dị ứng cefuroxim phát ban đỏ",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "tự kể",
                "thoi_gian_su_kien": "quá khứ",
                "luot_thoai": [6],
                "trich_dan": ["còn tôi thì bị dị ứng cefuroxim phát ban đỏ khắp người"],
            },
            {
                "id": 5,
                "nguoi_noi": "người nhà",
                "chu_the": "bệnh nhân",  # Cau luoc chu ngu "dem qua con non hai lan nua" chua ro cua ai -> can xac nhan
                "noi_dung": "đêm qua nôn hai lần",
                "do_chac_chan": "nghi ngờ",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "tự kể",
                "moc_thoi_gian": "đêm qua",
                "thoi_gian_su_kien": "hiện tại",
                "luot_thoai": [6],
                "trich_dan": ["đêm qua còn nôn hai lần nữa"],
            },
            {
                "id": 6,
                "nguoi_noi": "bác sĩ",
                "chu_the": "bệnh nhân",
                "noi_dung": "ấn đau nhẹ thượng vị, bụng mềm",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "quan sát",
                "thoi_gian_su_kien": "hiện tại",
                "luot_thoai": [7],
                "trich_dan": ["ấn đau nhẹ thượng vị, bụng mềm"],
            },
            {
                "id": 7,
                "nguoi_noi": "bác sĩ",
                "chu_the": "bệnh nhân",
                "noi_dung": "theo dõi viêm dạ dày trào ngược",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "nhận định",
                "thoi_gian_su_kien": "hiện tại",
                "luot_thoai": [7],
                "trich_dan": ["theo dõi viêm dạ dày trào ngược"],
            },
        ],
    },
    {
        "id": "demo_lao_khoa_con_gai",
        "ten_hien_thi": "Ca mẫu 3 · Bác sĩ – Cụ ông 74 tuổi – Con gái (Đính chính thuốc & Biệt dược dân gian)",
        "input": "\n".join([
            "Bác sĩ: Chào bác và chị, đợt này huyết áp của bác ở nhà thế nào?",
            "Người nhà: Dạ thưa bác sĩ, bố tôi bị tăng huyết áp lâu năm rồi, đợt này bố hay quên uống thuốc lắm, cả tuần nay quên suốt.",
            "Bệnh nhân: Không phải cả tuần đâu con, bố vẫn nhớ uống đều đặn mỗi sáng một viên amlodipin 5mg, chỉ có đúng hôm kia là bố quên thôi.",
            "Người nhà: À ừ nhỉ, em nhớ nhầm sang thuốc bổ mắt, chứ viên huyết áp thì đúng là chỉ mới quên hôm kia.",
            "Bác sĩ: Vâng, vậy là bác vẫn uống amlodipin 5mg mỗi sáng. Bác và chị có tiền sử dị ứng thuốc hay tự mua thêm thuốc gì không?",
            "Người nhà: Dạ bố tôi thì không thấy dị ứng thuốc gì, còn tôi thì bị dị ứng aspirin nổi mề đay phù mi mắt. Hôm qua bố hơi đau họng nên tự ra hiệu thuốc mua vỉ a móc uống.",
            "Bác sĩ: Huyết áp đo tại phòng khám hôm nay là 135/85 mmHg, tim đều, phổi trong. Bác duy trì amlodipin 5mg buổi sáng và mang vỉ kháng sinh tự mua đó bác sĩ kiểm tra lại tên hoạt chất chính xác nhé.",
        ]),
        "metadata": [
            {"luot": 1, "speaker_id": "doctor", "speaker_role": "doctor", "audio_start": 0.0, "audio_end": 3.8},
            {"luot": 2, "speaker_id": "caregiver", "speaker_role": "caregiver", "audio_start": 4.0, "audio_end": 10.2},
            {"luot": 3, "speaker_id": "patient", "speaker_role": "patient", "audio_start": 10.5, "audio_end": 17.6},
            {"luot": 4, "speaker_id": "caregiver", "speaker_role": "caregiver", "audio_start": 17.8, "audio_end": 22.4},
            {"luot": 5, "speaker_id": "doctor", "speaker_role": "doctor", "audio_start": 22.8, "audio_end": 29.5},
            {"luot": 6, "speaker_id": "caregiver", "speaker_role": "caregiver", "audio_start": 29.8, "audio_end": 39.6},
            {"luot": 7, "speaker_id": "doctor", "speaker_role": "doctor", "audio_start": 40.0, "audio_end": 48.8},
        ],
        "phat_bieu": [
            {
                "id": 0,
                "nguoi_noi": "người nhà",
                "chu_the": "bệnh nhân",
                "noi_dung": "tăng huyết áp lâu năm",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "tự kể",
                "thoi_gian_su_kien": "quá khứ",
                "luot_thoai": [2],
                "trich_dan": ["bố tôi bị tăng huyết áp lâu năm rồi"],
            },
            {
                "id": 1,
                "nguoi_noi": "người nhà",
                "chu_the": "bệnh nhân",
                "noi_dung": "quên uống thuốc huyết áp cả tuần nay",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "tự kể",
                "moc_thoi_gian": "cả tuần nay",
                "thoi_gian_su_kien": "hiện tại",
                "luot_thoai": [2],
                "trich_dan": ["cả tuần nay quên suốt"],
            },
            {
                "id": 2,
                "nguoi_noi": "bệnh nhân",
                "chu_the": "bệnh nhân",
                "noi_dung": "đang uống amlodipin, chỉ quên hôm kia",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "tự kể",
                "thoi_gian_su_kien": "hiện tại",
                "quan_he": "đính chính",
                "quan_he_voi": 1,
                "thuoc": {"ten": "amlodipin", "lieu": "5mg", "duong_dung": "uống", "so_lan": "mỗi sáng một viên", "trang_thai_dung": "đang dùng"},
                "luot_thoai": [3],
                "trich_dan": ["vẫn nhớ uống đều đặn mỗi sáng một viên amlodipin 5mg, chỉ có đúng hôm kia là bố quên thôi"],
            },
            {
                "id": 3,
                "nguoi_noi": "người nhà",
                "chu_the": "con gái",
                "noi_dung": "dị ứng aspirin nổi mề đay phù mi mắt",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "trả lời",
                "thoi_gian_su_kien": "quá khứ",
                "luot_thoai": [6],
                "trich_dan": ["còn tôi thì bị dị ứng aspirin nổi mề đay phù mi mắt"],
            },
            {
                "id": 4,
                "nguoi_noi": "người nhà",
                "chu_the": "bệnh nhân",
                "noi_dung": "tự mua thuốc kháng sinh amoxicillin uống khi đau họng",
                "do_chac_chan": "nghi ngờ",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "tự kể",
                "thoi_gian_su_kien": "hiện tại",
                "thuoc": {"ten": "amoxicillin", "duong_dung": "uống", "trang_thai_dung": "đang dùng"},
                "luot_thoai": [6],
                "trich_dan": ["hôm qua bố hơi đau họng nên tự ra hiệu thuốc mua vỉ a móc uống"],
            },
            {
                "id": 5,
                "nguoi_noi": "bác sĩ",
                "chu_the": "bệnh nhân",
                "noi_dung": "huyết áp 135/85 mmHg, tim đều, phổi trong",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "thực tế",
                "hanh_vi": "quan sát",
                "thoi_gian_su_kien": "hiện tại",
                "luot_thoai": [7],
                "trich_dan": ["huyết áp đo tại phòng khám hôm nay là 135/85 mmHg, tim đều, phổi trong"],
            },
            {
                "id": 6,
                "nguoi_noi": "bác sĩ",
                "chu_the": "bệnh nhân",
                "noi_dung": "duy trì amlodipin 5mg buổi sáng và kiểm tra lại vỉ kháng sinh tự mua",
                "do_chac_chan": "chắc chắn",
                "phu_dinh": False,
                "tinh_huong": "kế hoạch",
                "hanh_vi": "kế hoạch",
                "thoi_gian_su_kien": "hiện tại",
                "luot_thoai": [7],
                "trich_dan": ["duy trì amlodipin 5mg buổi sáng và mang vỉ kháng sinh tự mua đó bác sĩ kiểm tra lại"],
            },
        ],
    },
]


@lru_cache(maxsize=16)
def _dung_ca_demo(ca_id: str, nhanh: str) -> Dict:
    goc = next((c for c in _DU_LIEU_CA_DEMO if c["id"] == ca_id), None)
    if goc is None:
        raise KeyError(ca_id)
    from src import nhanh as _nhanh
    nhanh_chay = nhanh if nhanh in ("C_khoa", "C_khoa_hoi", "C_khoa_v2", "C", "B") else "C_khoa"
    mau = [{"id": goc["id"], "input": goc["input"]}]
    kq_tho = [{"id": goc["id"], "phat_bieu": copy.deepcopy(goc["phat_bieu"])}]
    r = _nhanh.chay_trung_gian(mau, None, None, None, nhanh_chay, kq_tho=kq_tho)[0]
    r["nhanh"] = nhanh_chay
    r["bo"] = BO_DEMO_BGK
    r["ten_hien_thi"] = goc["ten_hien_thi"]
    r["metadata"] = copy.deepcopy(goc["metadata"])
    return r


def danh_sach_ca_demo(bo: str | None = None) -> List[Dict]:
    if bo and bo != BO_DEMO_BGK:
        return []
    ra = []
    for goc in _DU_LIEU_CA_DEMO:
        r = _dung_ca_demo(goc["id"], "C_khoa")
        ra.append({
            "id": r["id"],
            "bo": BO_DEMO_BGK,
            "ten": goc["ten_hien_thi"],
            "so_luot": len([x for x in r["input"].split("\n") if x.strip()]),
            "so_menh_de": len(r.get("phat_bieu") or []),
            "so_can_xac_nhan": r.get("so_can_xac_nhan", 0),
        })
    return ra


def doc_ca_demo(ca_id: str, nhanh: str = "C_khoa") -> Dict | None:
    if not any(c["id"] == ca_id for c in _DU_LIEU_CA_DEMO):
        return None
    return copy.deepcopy(_dung_ca_demo(ca_id, nhanh))
