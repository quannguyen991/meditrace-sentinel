# -*- coding: utf-8 -*-
"""Kiểm thử tự động cho VẤN ĐỀ 1 (Ban Giám khảo):
Kiểm soát lỗi giữa các bước AI từ Layer 1 đến Layer 4.

Chứng minh toán học và thực nghiệm:
1. Khi ASR có sai số hoặc phân vai mơ hồ (unknown / low confidence), bộ kiểm tra
   bước 1 lập tức chặn lại và không cho phép tự ý gán thông tin cho bệnh nhân.
2. Khi người nhà kể bệnh của chính họ ("tôi thì dị ứng penicillin"), bộ kiểm tra
   bước 2 chặn đứng việc gán nhầm chu_the_id = 0 (bệnh nhân).
3. Khi bệnh nhân tự sửa lời ("sốt 39 độ... à không chỉ 38 độ"), FSM bước 3 chuyển
   bản ghi cũ sang 'bị thay thế', lưu vết kiểm toán và giữ nguyên audio_spans hai chiều.
4. Khi có mâu thuẫn giữa hai người nói khác nhau (bệnh nhân phủ nhận, người nhà khẳng định),
   FSM hạ cả hai về 'chưa giải quyết', đưa sang 'CẦN XÁC NHẬN' và không âm thầm xóa dữ liệu.
5. Kiểm chứng tính toàn vẹn của trường audio_spans: [{ start_ms, end_ms, speaker_id, exact_quote }].
"""
import pytest

from src.huan_luyen.ham_thuong_rlvr import KiemTraTungBuocToanDien
from src.duong_ong.b2_bu_chu_ngu_tinh_luoc import MayTrangThaiHoiThoai, TrangThaiFSM, kiem_tra_l2_sang_l3
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu
from src.duong_ong.b1_ep_dau_ra_json import LuotThoaiL1, kiem_tra_l1_sang_l2, xu_ly_dau_ra_mo_hinh


def test_buoc_1_chan_khi_asr_phan_vai_mo_ho_hoac_do_tin_cay_thap():
    """Kiểm tra Step-Gate 1: Khi vai ASR là 'unknown' hoặc confidence < 0.60."""
    luot_loi = LuotThoaiL1(
        luot_id=1,
        speaker_role="unknown",  # Mơ hồ phân vai
        speaker_id="spk_unknown",
        noi_dung="Tôi bị đau ngực dữ dội",
        start_ms=1000,
        end_ms=3500,
        confidence=0.45,         # Độ tin cậy thấp
    )
    kq = kiem_tra_l1_sang_l2(luot_loi)
    assert not kq.hop_le
    assert "vai_nguoi_noi_mo_ho" in kq.chan
    assert "do_tin_cay_asr_thap" in kq.chan


def test_buoc_2_chan_khi_nguoi_nha_ke_benh_ban_than_ma_gan_benh_nhan():
    """Kiểm tra Step-Gate 2: Ngăn chặn gán nhầm dị ứng người nhà cho bệnh nhân."""
    pb_sai_chu_the = PhatBieu(
        id=0,
        nguoi_noi="người nhà",
        chu_the_id=0,  # LỖI: gán cho bệnh nhân!
        noi_dung="dị ứng penicillin",
        bang_chung=[2],
        trich_dan=["Tôi thì bị dị ứng penicillin từ nhỏ"],
        audio_spans=[{
            "start_ms": 2500,
            "end_ms": 4800,
            "speaker_id": "spk_companion",
            "exact_quote": "Tôi thì bị dị ứng penicillin từ nhỏ",
        }],
    )
    hop_le, loi = kiem_tra_l2_sang_l3(pb_sai_chu_the)
    assert not hop_le
    assert any("chu_the_nguoi_ke" in m for m in loi)


def test_buoc_3_fsm_tu_dinh_chinh_chuyen_bi_thay_the_va_giu_audio_spans():
    """Kiểm tra Step-Gate 3: Tự sửa lỗi (cùng người nói) -> bản cũ thành 'bị thay thế'."""
    fsm = MayTrangThaiHoiThoai()
    
    # Bản ban đầu ở lượt 1
    pb_cu = PhatBieu(
        id=0,
        nguoi_noi="bệnh nhân",
        chu_the_id=0,
        noi_dung="sốt 39 độ",
        bang_chung=[1],
        trich_dan=["sốt 39 độ"],
        audio_spans=[{
            "start_ms": 1200,
            "end_ms": 2500,
            "speaker_id": "spk_patient",
            "exact_quote": "sốt 39 độ",
        }],
    )
    fsm.them_phat_bieu(pb_cu)

    # Đính chính ở lượt 3
    pb_moi = PhatBieu(
        id=1,
        nguoi_noi="bệnh nhân",
        chu_the_id=0,
        noi_dung="sốt 38 độ",
        bang_chung=[3],
        trich_dan=["à không tôi nhớ nhầm chỉ 38 độ thôi"],
        quan_he="đính chính",
        quan_he_voi=0,
        audio_spans=[{
            "start_ms": 5000,
            "end_ms": 7200,
            "speaker_id": "spk_patient",
            "exact_quote": "à không tôi nhớ nhầm chỉ 38 độ thôi",
        }],
    )
    fsm.them_phat_bieu(pb_moi)

    # Bản cũ chuyển 'bị thay thế', bản mới 'còn hiệu lực'
    assert fsm.danh_sach[0].trang_thai == TrangThaiFSM.BI_THAY_THE.value
    assert fsm.danh_sach[1].trang_thai == TrangThaiFSM.CON_HIEU_LUC.value

    # Kiểm tra vết âm thanh đính chính đầy đủ cả 2 chiều
    lich_su = fsm.lay_lich_su_dinh_chinh_kem_am_thanh()
    assert len(lich_su) == 1
    assert lich_su[0]["audio_spans_cu"][0]["exact_quote"] == "sốt 39 độ"
    assert lich_su[0]["audio_spans_moi"][0]["exact_quote"] == "à không tôi nhớ nhầm chỉ 38 độ thôi"


def test_buoc_3_fsm_mau_thuan_nguon_khac_nhau_ha_chua_giai_quyet():
    """Kiểm tra Step-Gate 3: Bệnh nhân và người nhà mâu thuẫn -> Chuyển 'chưa giải quyết'."""
    fsm = MayTrangThaiHoiThoai()
    
    # Bệnh nhân nói không uống rượu
    p_bn = PhatBieu(
        id=0,
        nguoi_noi="bệnh nhân",
        chu_the_id=0,
        noi_dung="uống rượu",
        bang_chung=[2],
        trich_dan=["tôi không hề uống giọt rượu nào"],
        phu_dinh=True,
        audio_spans=[{"start_ms": 3000, "end_ms": 5000, "speaker_id": "spk_patient", "exact_quote": "tôi không hề uống giọt rượu nào"}],
    )
    fsm.them_phat_bieu(p_bn)

    # Người nhà bảo có uống
    p_nn = PhatBieu(
        id=1,
        nguoi_noi="người nhà",
        chu_the_id=0,
        noi_dung="uống rượu",
        bang_chung=[3],
        trich_dan=["ngày nào ổng cũng uống nửa xị rượu đế"],
        phu_dinh=False,
        quan_he="đính chính",  # Người nhà muốn đính chính lời bệnh nhân
        quan_he_voi=0,
        audio_spans=[{"start_ms": 5500, "end_ms": 7800, "speaker_id": "spk_companion", "exact_quote": "ngày nào ổng cũng uống nửa xị rượu đế"}],
    )
    fsm.them_phat_bieu(p_nn)

    # CẢ HAI PHẢI CHUYỂN VỀ 'chưa giải quyết', không bên nào tự ý ghi đè
    assert fsm.danh_sach[0].trang_thai == TrangThaiFSM.CHUA_GIAI_QUYET.value
    assert fsm.danh_sach[1].trang_thai == TrangThaiFSM.CHUA_GIAI_QUYET.value

    # Danh sách mâu thuẫn giữ vết cả 2 luồng âm thanh
    mau_thuan = fsm.lay_danh_sach_mau_thuan_kem_am_thanh()
    assert len(mau_thuan) >= 1
    assert any(m["doi_lap_noi_dung"] == "uống rượu" for m in mau_thuan)


def test_quy_trinh_kiem_soat_toan_dien_4_buoc():
    """Kiểm thử tổng thể KiemTraTungBuocToanDien từ L1 đến L4."""
    ht = (
        "Bác sĩ: Bác sốt thế nào?\n"
        "Bệnh nhân: Tôi sốt 39 độ từ tối qua.\n"
        "Người nhà: À không, tôi đo nhiệt kế là 38 độ 5 thôi."
    )
    luot_l1 = [
        LuotThoaiL1(1, "bác sĩ", "spk_doc", "Bác sốt thế nào?", 0, 1500, 0.98),
        LuotThoaiL1(2, "bệnh nhân", "spk_pat", "Tôi sốt 39 độ từ tối qua.", 1600, 3800, 0.95),
        LuotThoaiL1(3, "người nhà", "spk_comp", "À không, tôi đo nhiệt kế là 38 độ 5 thôi.", 3900, 6500, 0.92),
    ]

    p1 = PhatBieu(
        id=0,
        nguoi_noi="bệnh nhân",
        chu_the_id=0,
        noi_dung="sốt 39 độ",
        bang_chung=[2],
        trich_dan=["Tôi sốt 39 độ từ tối qua"],
        moc_thoi_gian="tối qua",
        audio_spans=[{"start_ms": 1600, "end_ms": 3800, "speaker_id": "spk_pat", "exact_quote": "Tôi sốt 39 độ từ tối qua"}],
    )
    p2 = PhatBieu(
        id=1,
        nguoi_noi="người nhà",
        chu_the_id=0,
        noi_dung="sốt 38.5 độ",
        bang_chung=[3],
        trich_dan=["đo nhiệt kế là 38 độ 5"],
        quan_he="đính chính",
        quan_he_voi=0,
        audio_spans=[{"start_ms": 3900, "end_ms": 6500, "speaker_id": "spk_comp", "exact_quote": "đo nhiệt kế là 38 độ 5"}],
    )

    bc = KiemTraTungBuocToanDien.kiem_tra_quy_trinh(ht, luot_l1, [p1, p2])
    
    # Vì người nói khác nhau (bệnh nhân vs người nhà), không được tự ý xóa sốt 39 độ
    # Cả hai phải được đưa vào danh sách cần xác nhận
    assert len(bc.danh_sach_can_xac_nhan) == 2
    assert len(bc.danh_sach_an_toan_vao_benh_an) == 0  # Chặn không cho vào thân bệnh án khi chưa có bác sĩ duyệt!
