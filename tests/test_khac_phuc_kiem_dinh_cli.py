# -*- coding: utf-8 -*-
"""Kiểm thử hồi quy cho 4 điểm khắc phục sau kiểm định độc lập Claude CLI & OpenAI CLI."""
from src.quet_an_toan_duoc_ly_v2 import QuetAnToanDuocLyV2
from src.trich_xuat_thuc_the import HoiThoaiSubstringTrie
from src.audio.asr.contextual_trie_600 import ContextualPrefixTrie600
from src.audio.sim2real_v2 import danh_gia_sim2real_va_trie_600


def test_di_ung_nguoi_nha_cum_pho_tu_va_so_huu_gia_dinh():
    # Cụm nhiều phó từ tự xưng -> PHẢI bắt được
    assert QuetAnToanDuocLyV2.la_nguoi_nha_tu_xung_di_ung("tôi cũng từng bị dị ứng penicillin") is True
    assert QuetAnToanDuocLyV2.la_nguoi_nha_tu_xung_di_ung("tôi đã từng bị dị ứng aspirin") is True
    # Cụm sở hữu gia đình / người thân -> KHÔNG gắn cờ tự xưng cá nhân sai chiều
    assert QuetAnToanDuocLyV2.la_nguoi_nha_tu_xung_di_ung("gia đình tôi bị dị ứng hải sản") is False
    assert QuetAnToanDuocLyV2.la_nguoi_nha_tu_xung_di_ung("mẹ cháu bị dị ứng amoxicillin") is False

    # Kiểm tra end-to-end khi người nhà nói "tôi cũng từng bị dị ứng" mà hệ thống gán nhầm cho bệnh nhân
    engine = QuetAnToanDuocLyV2()
    ca_ro_ri = {
        "id": "test_leak_1",
        "benh": "viêm họng",
        "bay": ["di_ung_nguoi_nha"],
        "input": "Người nhà: tôi cũng từng bị dị ứng penicillin ạ",
        "output": "",
        "dap_an": [
            {
                "chu_the": "bệnh nhân",
                "muc": "DỊ ỨNG",
                "noi_dung": "dị ứng penicillin",
                "trich_dan": ["tôi cũng từng bị dị ứng penicillin ạ"],
            }
        ],
    }
    kq = engine.kiem_tra_ca(ca_ro_ri)
    assert kq.di_ung_nguoi_nha_an_toan is False


def test_substring_trie_khong_cat_cut_tren_350_ky_tu():
    doan_351 = "a" * 351
    doan_420 = "bệnh nhân khai " + ("triệu chứng đau âm ỉ vùng thượng vị lan ra sau lưng " * 8)
    assert len(doan_420) > 400

    trie = HoiThoaiSubstringTrie({1: doan_351, 2: f"Tiền sử: {doan_420}."})
    ok_351, luot_351 = trie.kiem_tra_chuoi_con(doan_351)
    assert ok_351 is True and 1 in luot_351

    ok_420, luot_420 = trie.kiem_tra_chuoi_con(doan_420)
    assert ok_420 is True and 2 in luot_420

    ok_sai, _ = trie.kiem_tra_chuoi_con(doan_420 + " không có trong văn bản")
    assert ok_sai is False


def test_sim2real_trie_rong_quay_ve_baseline():
    trie_rong = ContextualPrefixTrie600()
    mau_ca = [
        {"dap_an": [{"thuoc": {"ten": f"paracetamol_{i}"}} for i in range(40)]}
    ]
    kq = danh_gia_sim2real_va_trie_600(mau_ca, trie_rong, seed=42)
    # Trie rỗng không được phép nhảy vọt lên > 0.85, phải quanh baseline ~0.23
    assert kq.recall_co_prefix_trie < 0.40
