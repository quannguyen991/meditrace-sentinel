# -*- coding: utf-8 -*-
"""Kiểm thử nâng cấp toàn diện: phương ngữ 3 miền, G2P thuốc, Aho-Corasick, và cảnh báo Chính sách D."""
from src.audio.asr.contextual_trie_600 import ContextualPrefixTrie600
from src.canh_bao import gop
from src.canh_bao.loai import CAO, LOAI_NANG, muc_do
from src.cong_cu_lam_sang.tra_duoc_thu_aho_corasick import BoTraCuuDuocThuAhoCorasick
from src.duong_ong import b0_chuan_hoa_phuong_ngu as chuan_hoa
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu


def _pb(i, nd, dan, **kw):
    kw.setdefault("nguoi_noi", "bệnh nhân")
    kw.setdefault("chu_the_id", 0)
    return PhatBieu(id=i, noi_dung=nd, bang_chung=list(dan), **kw)


def test_phuong_ngu_mo_rong_va_bao_ve_tu_y_khoa():
    assert chuan_hoa.chuan_hoa("tau chộ hấn nác quá chơ") == "tao thấy nó nước quá chứ"
    assert chuan_hoa.chuan_hoa("dìa nhà dừ mệt hầy") == "về nhà giờ mệt nhỉ"
    assert chuan_hoa.chuan_hoa("bệnh nhân ói mửa mau lẹ") == "bệnh nhân nôn nhanh"
    # Giữ nguyên ngữ cảnh y khoa chuẩn để tránh thay nhầm
    assert "chi tiết" in chuan_hoa.chuan_hoa("khám chi tiết phần chi dưới")
    assert "mô mềm" in chuan_hoa.chuan_hoa("tổn thương mô mềm")
    assert "cấy máu" in chuan_hoa.chuan_hoa("đã làm cấy máu")
    assert "vô khuẩn" in chuan_hoa.chuan_hoa("vết thương vô khuẩn")
    assert "vào mạch" in chuan_hoa.chuan_hoa("tiêm thuốc vô mạch")


def test_g2p_thuoc_trie_va_aho_corasick_tu_tri_thuc():
    trie = ContextualPrefixTrie600()
    assert "Amoxicillin" in trie._bang_g2p_thuoc.get("a móc", "")
    assert "Omeprazol" in trie._bang_g2p_thuoc.get("ô mê", "")
    assert "Paracetamol" in trie._bang_g2p_thuoc.get("pa ra", "")
    assert "Metformin" in trie._bang_g2p_thuoc.get("met pho min", "")
    assert "Ceftriaxon" in trie._bang_g2p_thuoc.get("xép tri a xôn", "")

    tc = BoTraCuuDuocThuAhoCorasick()
    hits = {h["hoat_chat"] for h in tc.nhan_dien_thuoc_trong_van_ban("Đang dùng warfarin và allopurinol")}
    assert any("warfarin" in x for x in hits)
    assert any("allopurinol" in x for x in hits)


def test_thuoc_nti_trong_loai_nang():
    assert "thuoc_nti" in LOAI_NANG
    assert muc_do("MEDICATION_ENTITY_MISMATCH", "thuoc_nti") == CAO
    assert muc_do("FAMILY_PATIENT_MIXUP", "thuoc_nti") == CAO


def test_chinh_sach_d_chan_thuoc_thieu_chi_tiet_va_nhieu_asr():
    ht = "Bác sĩ: Khám thấy viêm xoang cấp, anh uống paracetamol nhé.\nBệnh nhân: Tôi đang uống paracetamol."
    p_thuoc = _pb(1, "đang dùng paracetamol", [2], thuoc=None, trich_dan=["Tôi đang uống paracetamol"])
    p_asr = _pb(2, "viem xoang cap", [1], nguoi_noi="bác sĩ", hanh_vi="nhận định",
                trich_dan=["Khám thấy viêm xoang cấp"])
    kq = gop.chay([p_thuoc, p_asr], ht)

    assert kq["trang_thai_D"][1]["trang_thai"] == gop.CAN_XAC_NHAN
    assert "MEDICATION_ENTITY_MISMATCH" in {c.ma for c in kq["theo_phat_bieu"][1]["tat_ca"]}

    assert kq["trang_thai_D"][2]["trang_thai"] == gop.CAN_XAC_NHAN
    assert "UNSUPPORTED_INFORMATION" in {c.ma for c in kq["theo_phat_bieu"][2]["tat_ca"]}


def test_chinh_sach_d_chan_nguoi_nha_tach_chu_the_va_asr_ngoi_nhat():
    ht1 = "Bác sĩ: Ông uống thuốc gì?\nNgười nhà: Bố em thì dị ứng nhộng."
    p1 = _pb(1, "dị ứng nhộng", [2], nguoi_noi="người nhà", chu_the_id=3,
             ten_chu_the="bố", trich_dan=["bố em thì dị ứng nhộng"])
    kq1 = gop.chay([p1], ht1)
    assert kq1["trang_thai_D"][1]["trang_thai"] == gop.CAN_XAC_NHAN
    assert "FAMILY_PATIENT_MIXUP" in {c.ma for c in kq1["theo_phat_bieu"][1]["tat_ca"]}

    ht2 = "Người nhà: Dạ tôi thi dị ung ibuprofen."
    p2 = _pb(1, "dị ứng ibuprofen", [1], nguoi_noi="người nhà", chu_the_id=2,
             ten_chu_the="mẹ", trich_dan=["dạ tôi thi dị ung ibuprofen"])
    kq2 = gop.chay([p2], ht2)
    assert kq2["trang_thai_D"][1]["trang_thai"] == gop.CAN_XAC_NHAN
    assert "WRONG_SUBJECT" in {c.ma for c in kq2["theo_phat_bieu"][1]["tat_ca"]}
