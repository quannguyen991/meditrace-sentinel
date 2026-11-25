# -*- coding: utf-8 -*-
"""Bộ kiểm thử cho Trục 2: Trích xuất nguyên tử, RLVR và Máy trạng thái hội thoại."""
import json
import pytest

from src.bo_kiem_tra import (
    tinh_thuong_rlvr_cho_ca,
    tinh_loi_the_grpo,
    tao_cap_du_lieu_dapo,
    TRONG_SO_RLVR,
)
from src.may_trang_thai_hoi_thoai import (
    BoGiaiQuyetProDrop,
    MayTrangThaiHoiThoai,
    QuanHeHoiThoai,
    TrangThaiFSM,
    ap_dung_may_trang_thai,
)
from src.phat_bieu import PhatBieu
from src.trich_xuat_thuc_the import (
    HoiThoaiSubstringTrie,
    SCHEMA_TRICH_XUAT_DANH_SACH,
    tao_gbnf_cho_trich_xuat,
    tach_suy_luan_va_json,
    xu_ly_dau_ra_mo_hinh,
)


# ==============================================================================
# 1. TEST SCHEMA VÀ GIẢI MÃ RÀNG BUỘC
# ==============================================================================

def test_gbnf_grammar_contains_core_rules():
    gbnf = tao_gbnf_cho_trich_xuat()
    assert "root ::=" in gbnf
    assert "danh_sach" in gbnf
    assert "trich_dan" in gbnf
    assert "nguoi_noi" in gbnf


def test_dynamic_substring_trie():
    cac_luot = {
        1: "Bác sĩ: Anh bị đau bụng thế nào?",
        2: "Bệnh nhân: Dạ, tôi đau quặn từng cơn quanh rốn từ chiều qua.",
    }
    trie = HoiThoaiSubstringTrie(cac_luot)

    # Khớp chính xác
    hop_le, luot = trie.kiem_tra_chuoi_con("đau quặn từng cơn")
    assert hop_le and 2 in luot

    # Trích dẫn bịa đặt (hallucination)
    hop_le, luot = trie.kiem_tra_chuoi_con("đau dữ dội kèm buồn nôn")
    assert not hop_le and len(luot) == 0


def test_tach_pha_suy_luan_va_json():
    dau_ra_mo_hinh = (
        "<think>\n"
        "Bệnh nhân kể đau bụng từ hôm qua. Người nhà nói thêm về dị ứng penicillin.\n"
        "Cần tách thành 2 bản ghi riêng biệt.\n"
        "</think>\n"
        "```json\n"
        "{\n"
        '  "danh_sach": [\n'
        "    {\n"
        '      "id": 0,\n'
        '      "nguoi_noi": "bệnh nhân",\n'
        '      "chu_the_id": 0,\n'
        '      "noi_dung": "đau bụng quanh rốn",\n'
        '      "bang_chung": [2],\n'
        '      "trich_dan": ["đau quặn từng cơn quanh rốn"]\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "```"
    )
    suy_luan, json_str = tach_suy_luan_va_json(dau_ra_mo_hinh)
    assert "Bệnh nhân kể đau bụng" in suy_luan
    parsed = json.loads(json_str)
    assert len(parsed["danh_sach"]) == 1


# ==============================================================================
# 2. TEST HÀM THƯỞNG XÁC MINH RLVR (K1-K7 & GUARDRAILS)
# ==============================================================================

def test_rlvr_reward_calculation():
    ht = (
        "Bác sĩ: Cháu có dị ứng thuốc gì không chị?\n"
        "Người nhà: Dạ, tôi thì dị ứng penicillin, còn cháu chưa thấy bị bao giờ ạ."
    )
    # Mẫu chuẩn: Đúng chủ thể (mẹ dị ứng, chu_the_id = 1) và đúng mức (cháu: chưa ghi nhận)
    pb1 = PhatBieu(
        id=0,
        nguoi_noi="người nhà",
        chu_the_id=1,
        noi_dung="dị ứng penicillin",
        bang_chung=[2],
        trich_dan=["tôi thì dị ứng penicillin"],
        do_chac_chan="chắc chắn",
    )
    pb2 = PhatBieu(
        id=1,
        nguoi_noi="người nhà",
        chu_the_id=0,
        noi_dung="dị ứng thuốc",
        bang_chung=[2],
        trich_dan=["còn cháu chưa thấy bị bao giờ ạ"],
        do_chac_chan="chưa ghi nhận",
    )

    ct_tot = tinh_thuong_rlvr_cho_ca(ht, [pb1, pb2])
    assert ct_tot.diem_tong > 0
    assert len(ct_tot.cac_loi_chan) == 0

    # Mẫu lỗi nguy hiểm: Gán nhầm dị ứng của mẹ cho con (chu_the_id = 0)
    pb_sai = PhatBieu(
        id=0,
        nguoi_noi="người nhà",
        chu_the_id=0,  # SAI: con không bị dị ứng penicillin!
        noi_dung="dị ứng penicillin",
        bang_chung=[2],
        trich_dan=["tôi thì dị ứng penicillin"],
        do_chac_chan="chắc chắn",
    )
    ct_sai = tinh_thuong_rlvr_cho_ca(ht, [pb_sai])
    assert ct_sai.p_nguy_hiem_lam_sang < 0
    assert "chu_the_nguoi_ke" in ct_sai.cac_loi_chan
    assert ct_tot.diem_tong > ct_sai.diem_tong


def test_grpo_and_dapo_generation():
    ht = "Bác sĩ: Anh uống thuốc gì chưa?\nBệnh nhân: Tôi đã uống paracetamol 500mg."
    pb_dung = [
        PhatBieu(
            id=0,
            nguoi_noi="bệnh nhân",
            chu_the_id=0,
            noi_dung="paracetamol",
            bang_chung=[2],
            trich_dan=["uống paracetamol 500mg"],
            thuoc={"ten": "paracetamol", "lieu": "500mg"},
        )
    ]
    pb_bia_trich = [
        PhatBieu(
            id=0,
            nguoi_noi="bệnh nhân",
            chu_the_id=0,
            noi_dung="paracetamol",
            bang_chung=[2],
            trich_dan=["uống amoxicillin 1000mg"],  # Bịa trích dẫn
            thuoc={"ten": "paracetamol", "lieu": "1000mg"},
        )
    ]

    kq_grpo = tinh_loi_the_grpo(ht, [pb_dung, pb_bia_trich])
    assert kq_grpo.chi_so_tot_nhat == 0
    assert kq_grpo.chi_so_kem_nhat == 1
    assert kq_grpo.danh_sach_loi_the[0] > kq_grpo.danh_sach_loi_the[1]

    cap_dapo = tao_cap_du_lieu_dapo(ht, [pb_dung, pb_bia_trich])
    assert cap_dapo is not None
    yw, yl, diff = cap_dapo
    assert yw == pb_dung
    assert diff > 2.0


# ==============================================================================
# 3. TEST TỈNH LƯỢC CHỦ NGỮ & FSM SỬA LỖI
# ==============================================================================

def test_bo_giai_quyet_pro_drop():
    bgq = BoGiaiQuyetProDrop()

    # Người nhà kể về bệnh nhân trước
    cid1, _ = bgq.phan_tich_luot("người nhà", "Dạ, bé nhà em bị sốt 2 hôm nay rồi ạ.")
    assert cid1 == 0

    # Câu khuyết chủ ngữ tiếp theo kế thừa bệnh nhân
    cid2, _ = bgq.phan_tich_luot("người nhà", "Uống hạ sốt thì đỡ một lúc, rồi lại nóng lại.")
    assert cid2 == 0

    # Câu người nhà tự kể về bản thân họ
    cid3, _ = bgq.phan_tich_luot("người nhà", "Tôi thì cũng đang bị cảm cúm lây từ bé.")
    assert cid3 == 1

    # Từ ghép có 'mình' nhưng không phải đại từ tự xưng
    cid4, _ = bgq.phan_tich_luot("người nhà", "Đêm cháu nó hay giật mình quấy khóc.")
    assert cid4 == 0


def test_fsm_self_repair_and_contradiction():
    fsm = MayTrangThaiHoiThoai()

    # 1. Phát biểu ban đầu
    p1 = PhatBieu(
        id=0,
        nguoi_noi="bệnh nhân",
        chu_the_id=0,
        noi_dung="sốt 39 độ",
        bang_chung=[1],
        trich_dan=["sốt 39 độ"],
    )
    fsm.them_phat_bieu(p1)
    assert fsm.danh_sach[0].trang_thai == TrangThaiFSM.CON_HIEU_LUC.value

    # 2. Đính chính bởi chính bệnh nhân (Tự sửa lỗi)
    p2 = PhatBieu(
        id=1,
        nguoi_noi="bệnh nhân",
        chu_the_id=0,
        noi_dung="sốt 38 độ",
        bang_chung=[3],
        trich_dan=["à nhầm chỉ 38 độ thôi"],
        quan_he="đính chính",
        quan_he_voi=0,
    )
    fsm.them_phat_bieu(p2)

    # Bản cũ phải bị thay thế, bản mới còn hiệu lực
    assert fsm.danh_sach[0].trang_thai == TrangThaiFSM.BI_THAY_THE.value
    assert fsm.danh_sach[1].trang_thai == TrangThaiFSM.CON_HIEU_LUC.value

    # 3. Mâu thuẫn khác người nói
    p3 = PhatBieu(
        id=2,
        nguoi_noi="người nhà",
        chu_the_id=0,
        noi_dung="đo nhiệt kế thủy ngân là 39 độ 5",
        bang_chung=[4],
        trich_dan=["đo nhiệt kế là 39 độ 5"],
        quan_he="đính chính",  # Người nhà đòi sửa lời bệnh nhân
        quan_he_voi=1,
    )
    fsm.them_phat_bieu(p3)

    # Khác người nói: Chuyển thành mâu thuẫn nguồn, cả hai hạ xuống 'chưa giải quyết'
    assert fsm.danh_sach[1].trang_thai == TrangThaiFSM.CHUA_GIAI_QUYET.value
    assert fsm.danh_sach[2].trang_thai == TrangThaiFSM.CHUA_GIAI_QUYET.value
