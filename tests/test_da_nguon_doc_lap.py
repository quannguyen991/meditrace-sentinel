# -*- coding: utf-8 -*-
"""Kiểm thử nâng cấp toàn diện & hồi quy phản ví dụ (phương ngữ, G2P thuốc, Aho-Corasick, Chính sách D)."""
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
    assert chuan_hoa.chuan_hoa("bệnh nhân ăn không vô") == "bệnh nhân ăn không vào"
    assert chuan_hoa.chuan_hoa("lấy cấy ni uống") == "lấy cái này uống"

    # Bảo vệ tuyệt đối thuật ngữ & cụm y khoa chuẩn (hồi quy phản ví dụ kiểm toán)
    for cau in (
        "khám chi tiết phần chi dưới",
        "tê bì tứ chi và phù hai chi",
        "tổn thương mô mềm, sinh thiết mô vú và mô gan",
        "đã làm cấy máu trước cấy ghép thận và cấy que tránh thai",
        "vết thương vô khuẩn và vô kinh 3 tháng",
        "viêm bờ mi, sụp mi, mặt hầm hầm giời leo",
        "vết thương bờ nham nhở, mùa hè nóng bức",
        "ảnh chụp X-quang không thiệt mạng",
        "uống nước chơ vơ giữa hè",
    ):
        sach = chuan_hoa.chuan_hoa(cau)
        assert "gì" not in sach, (cau, sach)
        assert "đâu" not in sach, (cau, sach)
        assert "cái ghép" not in sach and "cái que" not in sach, (cau, sach)
        assert "vào kinh" not in sach, (cau, sach)
        assert "bờ mày" not in sach and "sụp mày" not in sach, (cau, sach)
        assert "trời leo" not in sach, (cau, sach)
        assert "anh ấy" not in sach, (cau, sach)
        assert "nóng nhiều có thể sốt" not in sach, (cau, sach)


def test_g2p_thuoc_trie_va_aho_corasick_tu_tri_thuc():
    trie = ContextualPrefixTrie600()
    assert "Amoxicillin" in trie._bang_g2p_thuoc.get("a móc", "")
    assert "Omeprazol" in trie._bang_g2p_thuoc.get("ô mê", "")
    assert "Paracetamol" in trie._bang_g2p_thuoc.get("pa ra", "")
    assert "Metformin" in trie._bang_g2p_thuoc.get("met pho min", "")
    assert "Ceftriaxon" in trie._bang_g2p_thuoc.get("xép tri a xôn", "")

    # Ngữ cảnh không phải thuốc: cụm 2 âm tiết ngắn không được gợi ý bừa
    assert trie.quet_goi_y_sua_am_vi("nấm a mốc trên tường") == []
    assert trie.quet_goi_y_sua_am_vi("trời ô mê quá") == []
    assert trie.quet_goi_y_sua_am_vi("tôi đi pa ra công viên") == []

    # Ngữ cảnh thuốc thật: gợi ý đúng hoạt chất, không tự sửa đè
    assert any(g["goi_y_chuan"] == "Amoxicillin" for g in trie.quet_goi_y_sua_am_vi("mua vỉ a móc uống"))
    assert any(g["goi_y_chuan"] == "Paracetamol" for g in trie.quet_goi_y_sua_am_vi("uống pa ra hạ sốt"))

    tc = BoTraCuuDuocThuAhoCorasick()
    assert len(tc.bang_hoat_chat) >= 150
    hits = {h["hoat_chat"] for h in tc.nhan_dien_thuoc_trong_van_ban("Đang dùng warfarin, allopurinol và mometasone")}
    assert any("warfarin" in x for x in hits)
    assert any("allopurinol" in x for x in hits)
    assert any("mometasone" in x for x in hits)


def test_thuoc_nti_trong_loai_nang():
    assert "thuoc_nti" in LOAI_NANG
    assert muc_do("MEDICATION_ENTITY_MISMATCH", "thuoc_nti") == CAO
    assert muc_do("DOSE_MISMATCH", "thuoc_nti") == CAO
    assert muc_do("FAMILY_PATIENT_MIXUP", "thuoc_nti") == CAO


def test_chinh_sach_d_chan_roi_lieu_va_nhieu_asr_khong_bat_nham_tu_sach():
    ht = (
        "Bác sĩ: Khám thấy viêm xoang cấp, anh uống paracetamol 500 mg ngày 2 lần nhé.\n"
        "Bệnh nhân: Tôi đang uống paracetamol 500 mg ngày 2 lần.\n"
        "Bệnh nhân: Tôi đang uống ibuprofen."
    )
    # Lượt dẫn có liều "500 mg" nhưng mệnh đề làm rơi sạch cả trường `thuoc` lẫn số liệu -> phải chặn
    p_roi_lieu = _pb(1, "đang dùng paracetamol", [2], thuoc=None, trich_dan=["Tôi đang uống paracetamol 500 mg ngày 2 lần"])
    # Lượt dẫn KHÔNG nói liều và mệnh đề khớp nguyên ý -> KHÔNG được chặn oan
    p_khong_lieu = _pb(2, "đang dùng ibuprofen", [3], thuoc=None, trich_dan=["Tôi đang uống ibuprofen"])
    # Nhiễu ASR mất dấu bắt buộc ("viem") -> chặn
    p_asr = _pb(3, "viem xoang cap", [1], nguoi_noi="bác sĩ", hanh_vi="nhận định",
                trich_dan=["Khám thấy viêm xoang cấp"])

    kq = gop.chay([p_roi_lieu, p_khong_lieu, p_asr], ht)

    assert kq["trang_thai_D"][1]["trang_thai"] == gop.CAN_XAC_NHAN
    assert "DOSE_MISMATCH" in {c.ma for c in kq["theo_phat_bieu"][1]["tat_ca"]}

    assert "DOSE_MISMATCH" not in {c.ma for c in kq["theo_phat_bieu"][2]["tat_ca"]}
    assert "MEDICATION_ENTITY_MISMATCH" not in {c.ma for c in kq["theo_phat_bieu"][2]["tat_ca"]}

    assert kq["trang_thai_D"][3]["trang_thai"] == gop.CAN_XAC_NHAN
    assert "UNSUPPORTED_INFORMATION" in {c.ma for c in kq["theo_phat_bieu"][3]["tat_ca"]}

    # Các chẩn đoán tiếng Việt có dấu hợp lệ ("ung thư phổi", "u nang", "dung dịch", "hoa mắt", "than đau") KHÔNG bị gắn nhiễu ASR
    ht_sach = "Bác sĩ: Theo dõi ung thư phổi, u nang gan, truyền dung dịch NaCl."
    p_sach = _pb(1, "theo dõi ung thư phổi, u nang gan", [1], nguoi_noi="bác sĩ", hanh_vi="nhận định",
                 trich_dan=["Theo dõi ung thư phổi, u nang gan"])
    kq_sach = gop.chay([p_sach], ht_sach)
    assert not any(c.bo_phat_hien == "thuc_the:nhieu_dau_asr" for c in kq_sach["theo_phat_bieu"][1]["tat_ca"])


def test_chinh_sach_d_chan_nguoi_nha_ranh_gioi_tu_va_asr_ngoi_nhat():
    ht1 = "Bác sĩ: Ông uống thuốc gì?\nNgười nhà: Bố em thì dị ứng nhộng."
    p1 = _pb(1, "dị ứng nhộng", [2], nguoi_noi="người nhà", chu_the_id=3,
             ten_chu_the="bố", trich_dan=["bố em thì dị ứng nhộng"])
    kq1 = gop.chay([p1], ht1)
    assert kq1["trang_thai_D"][1]["trang_thai"] == gop.CAN_XAC_NHAN
    assert "FAMILY_PATIENT_MIXUP" in {c.ma for c in kq1["theo_phat_bieu"][1]["tat_ca"]}

    # Không khớp chuỗi con "ba" trong "ba ngày" hoặc "má" trong "mát gan"
    ht_sub = "Người nhà: Cháu uống thuốc ba ngày rồi, uống cho mát gan."
    p_sub = _pb(1, "dị ứng thuốc", [1], nguoi_noi="người nhà", chu_the_id=3,
                ten_chu_the="ba", trich_dan=["uống thuốc ba ngày rồi"])
    kq_sub = gop.chay([p_sub], ht_sub)
    assert not any(c.bo_phat_hien == "thuc_the:nguoi_nha_chinh" for c in kq_sub["theo_phat_bieu"][1]["tat_ca"])

    ht2 = "Người nhà: Dạ tôi thi dị ung ibuprofen."
    p2 = _pb(1, "dị ứng ibuprofen", [1], nguoi_noi="người nhà", chu_the_id=2,
             ten_chu_the="mẹ", trich_dan=["dạ tôi thi dị ung ibuprofen"])
    kq2 = gop.chay([p2], ht2)
    assert kq2["trang_thai_D"][1]["trang_thai"] == gop.CAN_XAC_NHAN
    assert "WRONG_SUBJECT" in {c.ma for c in kq2["theo_phat_bieu"][1]["tat_ca"]}


# ─── Hồi quy rà soát 27/11 tối: các luật mới không được đổi nghĩa / chặn oan ───

def test_mi_la_mi_mat_khong_doi_thanh_may():
    # "mi" là mí mắt: đổi thành đại từ "mày" làm sai nghĩa lâm sàng
    for cau in ("hai mi bị sưng đỏ", "mi đang sưng", "mi có mủ", "mi bị sụp", "mí mi không có gì"):
        assert "mày" not in chuan_hoa.chuan_hoa(cau), cau
    # Đại từ "mi" (miền Trung) trước động từ thường ngày vẫn được đổi
    assert chuan_hoa.chuan_hoa("mi đi mô rứa") .startswith("mày đi")


def test_dau_ngang_hong_khong_tu_doi_vi_tri():
    # Hông (mạn sườn/hông) và thắt lưng là hai vị trí khác nhau — không đổi chắc chắn
    assert "lưng dưới" not in chuan_hoa.chuan_hoa("đau ngang hông phải")


def test_dose_mismatch_bo_qua_so_lieu_khong_phai_lieu():
    ht = "Bệnh nhân: Tôi ho 3 ngày nay, có uống paracetamol."
    p = _pb(1, "đang dùng paracetamol", [1], thuoc=None, trich_dan=["có uống paracetamol"])
    kq = gop.chay([p], ht)
    assert "DOSE_MISMATCH" not in {c.ma for c in kq["theo_phat_bieu"][1]["tat_ca"]}


def test_viet_tat_dia_huyet_ap_khong_la_nhieu_asr():
    ht = "Bác sĩ: Huyết áp SYS 140 DIA 90, chẩn đoán tăng huyết áp."
    p = _pb(1, "tăng huyết áp, SYS 140 DIA 90", [1], nguoi_noi="bác sĩ", hanh_vi="nhận định",
            trich_dan=["Huyết áp SYS 140 DIA 90"])
    kq = gop.chay([p], ht)
    assert not any(c.bo_phat_hien == "thuc_the:nhieu_dau_asr" for c in kq["theo_phat_bieu"][1]["tat_ca"])
