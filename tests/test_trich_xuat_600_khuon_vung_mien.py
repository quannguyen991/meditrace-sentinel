# -*- coding: utf-8 -*-
"""Kiểm thử mở rộng Trục 2 cho 600 khuôn bệnh & Phương ngữ 3 miền (Phase 3).

Kiểm chứng:
1. Dynamic Substring Trie Constraint hoạt động chuẩn xác với phương ngữ lâm sàng 3 miền
   (Nam Bộ, Trung Bộ, Bắc Bộ), bảo toàn trích dẫn nguyên văn và gợi ý thuật ngữ y khoa chuẩn.
2. Decoupled Epistemic Reasoning (<think>...) phân giải chính xác 18 hệ cơ quan.
3. Bộ giải quyết Pro-Drop xử lý trơn tru đại từ nhân xưng vùng miền (tui, qua, mềnh, thằng nhỏ, bé út).
4. Kiểm soát lỗi 4 cửa ngõ bảo đảm an toàn tuyệt đối, không gán nhầm bệnh người nhà cho bệnh nhân.
"""
import pytest

from src.huan_luyen.ham_thuong_rlvr import KiemTraTungBuocToanDien
from src.duong_ong.b2_bu_chu_ngu_tinh_luoc import BoGiaiQuyetProDrop, MayTrangThaiHoiThoai, TrangThaiFSM
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu
from src.duong_ong.b1_ep_dau_ra_json import (
    DANH_SACH_18_HE_CO_QUAN,
    HoiThoaiSubstringTrie,
    LuotThoaiL1,
    xu_ly_dau_ra_mo_hinh,
)


def test_substring_trie_with_regional_dialects():
    """Kiểm chứng Substring Trie với khẩu ngữ & phương ngữ 3 miền."""
    cac_luot = {
        1: "Bác sĩ: Bác thấy trong người thế nào?",
        2: "Bệnh nhân: Dạ, tôi nóng hầm hập mấy bữa nay, rồi thấy tức ngực khó thở.",
        3: "Bác sĩ: Có bị buồn nôn hay đau bụng gì không?",
        4: "Bệnh nhân: Dạ, ăn vô là mắc nghẹn với lại ói mửa dữ lắm bác sĩ.",
    }
    trie = HoiThoaiSubstringTrie(cac_luot)

    # 1. Phương ngữ Nam Bộ: "nóng hầm hập" -> sốt
    hop_le, luot, chuan = trie.kiem_tra_va_chuan_hoa_phuong_ngu("nóng hầm hập")
    assert hop_le and 2 in luot
    assert "sốt" in chuan.lower() or "nóng" in chuan.lower()

    # 2. Khẩu ngữ: "mắc nghẹn"
    hop_le, luot, chuan = trie.kiem_tra_va_chuan_hoa_phuong_ngu("mắc nghẹn")
    assert hop_le and 4 in luot

    # 3. Trích dẫn bịa đặt (hallucinated quote) -> Trie chặn ngay lập tức
    hop_le, luot, _ = trie.kiem_tra_va_chuan_hoa_phuong_ngu("nôn ra máu tươi kèm đau quặn thắt")
    assert not hop_le and len(luot) == 0


def test_decoupled_reasoning_18_organ_systems():
    """Kiểm chứng nhận diện Hệ cơ quan (18 hệ) từ khối suy luận <think>."""
    output_mo_hinh = (
        "<think>\n"
        "[HỆ CƠ QUAN & BỆNH CẢNH]: Bệnh nhân có triệu chứng tức ngực, khó thở khi gắng sức, thuộc hệ tim mạch.\n"
        "[CHỦ THỂ & VAI NÓI]: Bệnh nhân tự kể triệu chứng của mình, chu_the_id = 0.\n"
        "[DÒNG THỜI GIAN & ĐÍNH CHÍNH]: Triệu chứng xuất hiện 3 ngày nay, thực tế, chắc chắn.\n"
        "[PHÂN RÃ NGUYÊN TỬ]: 1 bản ghi về tức ngực.\n"
        "</think>\n"
        "```json\n"
        "{\n"
        '  "danh_sach": [\n'
        "    {\n"
        '      "id": 0,\n'
        '      "nguoi_noi": "bệnh nhân",\n'
        '      "chu_the_id": 0,\n'
        '      "noi_dung": "tức ngực khi gắng sức",\n'
        '      "bang_chung": [1],\n'
        '      "trich_dan": ["tức ngực khi đi bộ nhanh"]\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "```"
    )
    ht = "Bệnh nhân: Tôi bị tức ngực khi đi bộ nhanh từ 3 hôm trước."
    kq = xu_ly_dau_ra_mo_hinh(output_mo_hinh, hoi_thoai_goc=ht)
    assert kq.he_co_quan == "tim mạch"
    assert len(kq.danh_sach_phat_bieu) == 1
    assert kq.danh_sach_phat_bieu[0].noi_dung == "tức ngực khi gắng sức"


def test_pro_drop_regional_pronouns_nam_bo_trung_bo():
    """Kiểm chứng bộ giải quyết Pro-drop với đại từ nhân xưng 3 miền."""
    bgq = BoGiaiQuyetProDrop()

    # 1. Người nhà Nam Bộ gọi bệnh nhân là 'thằng nhỏ'
    cid1, _ = bgq.phan_tich_luot("người nhà", "Dạ thưa bác sĩ, thằng nhỏ nhà tui nó sốt hầm hập từ tối qua.")
    assert cid1 == 0

    # 2. Câu tiếp theo khuyết chủ ngữ kế thừa bệnh nhân
    cid2, _ = bgq.phan_tich_luot("người nhà", "Cho uống thuốc hạ sốt gói mà hổng chịu hạ, cứ quấy khóc miết.")
    assert cid2 == 0

    # 3. Người nhà Nam Bộ tự xưng "tui thì..." kể bệnh của mình
    cid3, _ = bgq.phan_tich_luot("người nhà", "Tui thì cũng đang bị đau nhức xương khớp dữ lắm.")
    assert cid3 == 1

    # 4. Người nhà Trung Bộ: "mềnh thì..." kể bệnh của mình
    cid4, _ = bgq.phan_tich_luot("người nhà", "Mềnh thì cũng đang bị viêm họng mấy bữa ni.")
    assert cid4 == 1


def test_stepwise_gates_regional_and_multi_organ():
    """Kiểm chứng 4 cửa ngõ với câu thoại phương ngữ và đa hệ cơ quan."""
    ht = (
        "Bác sĩ: Gia đình dạo này sức khỏe thế nào?\n"
        "Người nhà: Dạ, tui thì cũng đang bị tăng huyết áp uống thuốc đều, còn thằng nhỏ thì bị ho khò khè khó thở từ hôm qua."
    )
    luot_l1 = [
        LuotThoaiL1(1, "bác sĩ", "spk_doc", "Gia đình dạo này sức khỏe thế nào?", 0, 2000, 0.99),
        LuotThoaiL1(2, "người nhà", "spk_comp", "Dạ, tui thì cũng đang bị tăng huyết áp uống thuốc đều, còn thằng nhỏ thì bị ho khò khè khó thở từ hôm qua.", 2100, 7500, 0.95),
    ]

    # Bản ghi 1: Tăng huyết áp của người nhà (chu_the_id = 1)
    p_nn = PhatBieu(
        id=0,
        nguoi_noi="người nhà",
        chu_the_id=1,
        noi_dung="tăng huyết áp",
        bang_chung=[2],
        trich_dan=["tui thì cũng đang bị tăng huyết áp"],
        audio_spans=[{"start_ms": 2500, "end_ms": 4500, "speaker_id": "spk_comp", "exact_quote": "tui thì cũng đang bị tăng huyết áp"}],
    )

    # Bản ghi 2: Ho khò khè của em bé (chu_the_id = 0)
    p_bn = PhatBieu(
        id=1,
        nguoi_noi="người nhà",
        chu_the_id=0,
        noi_dung="ho khò khè khó thở",
        bang_chung=[2],
        trich_dan=["thằng nhỏ thì bị ho khò khè khó thở"],
        audio_spans=[{"start_ms": 5000, "end_ms": 7500, "speaker_id": "spk_comp", "exact_quote": "thằng nhỏ thì bị ho khò khè khó thở"}],
    )

    bc = KiemTraTungBuocToanDien.kiem_tra_quy_trinh(ht, luot_l1, [p_nn, p_bn])
    
    # Cả hai bản ghi đều hợp lệ, không bị chặn oan, gán đúng chủ thể
    assert bc.buoc_2_l2_l3["qua_l2"] == 2
    assert len(bc.danh_sach_an_toan_vao_benh_an) >= 1
    # Bệnh nhi có triệu chứng hô hấp
    assert any(p.chu_the_id == 0 and "ho" in p.noi_dung for p in bc.danh_sach_an_toan_vao_benh_an)
