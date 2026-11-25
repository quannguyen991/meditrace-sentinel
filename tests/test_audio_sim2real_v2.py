# -*- coding: utf-8 -*-
"""Bộ kiểm thử Tầng 0 ASR cho Bộ V2: Sim2Real RIR & Contextual Prefix-Trie 600 Khuôn Bệnh."""
import numpy as np
import pytest


from src.audio.asr.contextual_trie_600 import (
    ContextualPrefixTrie600,
    HE_CO_QUAN_CHUAN,
)
from src.audio.sim2real_v2 import (
    CauHinhAmHocV2,
    Sim2RealV2Engine,
    danh_gia_sim2real_va_trie_600,
)


@pytest.fixture
def trie_600_mau():
    """Tạo Trie 600 mẫu với đại diện đầy đủ 18 hệ cơ quan và danh mục thuốc."""
    trie = ContextualPrefixTrie600()

    # Tạo mẫu các khuôn thuộc 18 hệ cơ quan
    danh_sach_khuon = []
    for i, he in enumerate(HE_CO_QUAN_CHUAN):
        danh_sach_khuon.append({
            "ten": f"bệnh mẫu {he}",
            "he_co_quan": he,
            "chinh": [f"triệu chứng chính {he}", f"đau tức {he}"],
            "phu": [f"triệu chứng phụ {he}", "mệt mỏi"],
            "kham": f"kết quả khám {he}"
        })
    trie.nap_khuon_benh(danh_sach_khuon)

    # Nạp danh mục thuốc mẫu và biến thể G2P
    duoc_thu = {
        "Augmentin": ["ooc men tin", "oc mang tin", "oóc măng tin"],
        "Amlodipine": ["am lo di pin", "am-lô-đi-pin"],
        "Metformin": ["met pho min", "méc-pho-min"],
        "Paracetamol": ["pa ra se ta mol", "pa-ra-xê-ta-môn"],
        "Levothyroxine": ["le vo thy ro xin", "lê vô ty rô xin"]
    }
    trie.nap_duoc_thu_va_g2p(duoc_thu)
    return trie


def test_contextual_prefix_trie_600_khoi_tao_va_tra_cuu(trie_600_mau):
    """Kiểm tra khởi tạo Trie, chỉ mục 18 hệ cơ quan và tra cứu O(1)."""
    assert trie_600_mau.so_thuc_the > 30

    # Kiểm tra chỉ mục 18 hệ cơ quan
    for he in HE_CO_QUAN_CHUAN:
        assert len(trie_600_mau.chi_muc_he_co_quan[he]) >= 1
        assert f"bệnh mẫu {he}" in trie_600_mau.chi_muc_he_co_quan[he]

    # Kiểm tra tra cứu bước Trie (bệnh mẫu tim mạch)
    curr = trie_600_mau.root
    bias, curr = trie_600_mau.buoc_trie(curr, "bệnh")
    assert bias > 0.0 and curr.token == "bệnh"

    bias, curr = trie_600_mau.buoc_trie(curr, "mẫu")
    assert bias > 0.0 and curr.token == "mẫu"

    bias, curr = trie_600_mau.buoc_trie(curr, "tim_mach")
    assert bias > 0.0 and curr.is_terminal is True


def test_organ_specific_priority_bias(trie_600_mau):
    """Kiểm tra cơ chế ưu tiên hệ cơ quan và Dialogue Act Masking."""
    curr = trie_600_mau.root
    curr = curr.children["bệnh"].children["mẫu"]

    # Bước vào lá terminal 'tim_mach' với hệ cơ quan chỉ định 'tim_mach'
    diem_uu_tien, _ = trie_600_mau.buoc_trie(
        curr, "tim_mach", he_co_quan_uu_tien="tim_mach", mu_dialogue_act=1.0
    )

    # Bước vào lá terminal 'tim_mach' nhưng hệ cơ quan chỉ định là 'ho_hap'
    diem_khong_uu_tien, _ = trie_600_mau.buoc_trie(
        curr, "tim_mach", he_co_quan_uu_tien="ho_hap", mu_dialogue_act=1.0
    )

    # Điểm khi đúng chuyên khoa phải cao hơn rõ rệt
    assert diem_uu_tien > diem_khong_uu_tien

    # Khi mu_dialogue_act = 0.0 (chào hỏi xã giao): Điểm bias bị triệt tiêu về 0
    diem_xa_giao, _ = trie_600_mau.buoc_trie(
        curr, "tim_mach", he_co_quan_uu_tien="tim_mach", mu_dialogue_act=0.0
    )
    assert diem_xa_giao == 0.0


def test_g2p_aliasing_recognition(trie_600_mau):
    """Kiểm tra biến thể ngữ âm tiếng Việt ánh xạ chính xác về tên chuẩn quốc tế."""
    curr = trie_600_mau.root
    for tok in ["ooc", "men", "tin"]:
        bias, curr = trie_600_mau.buoc_trie(curr, tok)

    assert curr.is_terminal is True
    assert curr.canonical_name == "Augmentin"
    assert curr.entity_type == "thuoc"


def test_sim2real_v2_acoustic_pipeline():
    """Kiểm tra chuỗi mô phỏng âm học phòng khám thực tế (RIR + Tạp âm + Opus packet loss)."""
    cfg = CauHinhAmHocV2(sample_rate=16000, rt60_giay=0.40, muc_snr_db=12.0)
    sim = Sim2RealV2Engine(cfg)

    # Tạo tín hiệu kiểm thử (tiếng nói giả định dài 1.0 giây)
    t = np.linspace(0, 1.0, 16000, endpoint=False)
    tin_hieu_sach = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)

    # Chạy qua chuỗi mô phỏng toàn diện
    tin_hieu_suy_hao = sim.xu_ly_chuoi_sim2real_toan_dien(
        tin_hieu_sach=tin_hieu_sach,
        vai_nguoi_noi="benh_nhan",
        loai_tap_am="dieu_hoa"
    )

    assert len(tin_hieu_suy_hao) == len(tin_hieu_sach)
    assert not np.array_equal(tin_hieu_sach, tin_hieu_suy_hao)
    # Tín hiệu đầu ra không bị tràn biên độ [-1.0, 1.0]
    assert np.max(np.abs(tin_hieu_suy_hao)) <= 1.0


def test_sim2real_danh_gia_thuc_nghiem(trie_600_mau):
    """Kiểm tra tỷ lệ Entity Recall nhảy vọt khi có Contextual Prefix-Trie."""
    # Tạo 20 ca mẫu giả lập
    ca_mau = []
    for _ in range(20):
        ca_mau.append({
            "dap_an": [
                {"thuoc": {"ten": "Augmentin", "lieu": "1g"}},
                {"thuoc": {"ten": "Amlodipine", "lieu": "5mg"}}
            ]
        })

    ket_qua = danh_gia_sim2real_va_trie_600(ca_mau, trie_600_mau, seed=42)

    assert ket_qua.tong_so_ca == 20
    assert ket_qua.tong_thuc_the_thuoc == 40
    # Baseline không bias: ~20-25%
    assert ket_qua.recall_khong_bias < 0.40
    # Có Contextual Prefix-Trie 600 trên CPU: > 85%
    assert ket_qua.recall_co_prefix_trie >= 0.85


def test_cpu_int8_ram_footprint(trie_600_mau):
    """Kiểm tra dung lượng bộ nhớ RAM CPU INT8 phải < 65 MB."""
    ram_mb = trie_600_mau.tinh_dung_luong_ram_uoc_tinh_kb() / 1024.0
    assert ram_mb < 65.0, f"Dung lượng RAM vượt trần: {ram_mb} MB"
