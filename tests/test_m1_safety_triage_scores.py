# -*- coding: utf-8 -*-
"""Kiểm thử M1.3 & M1.4: chuẩn hóa `co_thai`, tự kích hoạt 9 thang điểm lâm sàng,
`tai_kiem_tra_nhanh` (<50ms) và phân tầng cảnh báo 3 mức chống mệt mỏi cảnh báo."""
import time

from src import cong_rui_ro
from src.canh_bao import gop
from src.canh_bao.loai import CAN_XEM, CAO, LOI_PHAT_HIEN, NGHI_RUI_RO, THAP, CanhBao
from src.dieu_phoi_ha_tang import MediTracePipelineOrchestrator, tai_kiem_tra_nhanh
from src.duoc_ly_lam_sang import ClinicalPharmacovigilanceEngine
from src.ep_kieu_dau_vao import chuan_hoa_thong_tin_benh_nhan
from src.phat_bieu import PhatBieu


def test_co_thai_chuan_hoa_xuyen_cac_tang():
    for truthy in (True, "true", "có", "Có", "yes", "1"):
        bn = chuan_hoa_thong_tin_benh_nhan({"co_thai": truthy, "tuan_thai": "10"})
        assert bn["thai_ky"] is True and bn["mang_thai"] is True and bn["co_thai"] is True

        rr = cong_rui_ro.phan_tich_co_dia_benh_nhan({"co_thai": truthy, "tuan_thai": "10"})
        assert rr.he_so_tong > 1.0 and any("3 tháng đầu" in y for y in rr.cac_yeu_to)

        dl = ClinicalPharmacovigilanceEngine.kiem_duyet_toan_dien(["atorvastatin", "enalapril"], {"co_thai": truthy})
        assert dl.hop_le is False and len(dl.chong_chi_dinh_co_dia) >= 2

    for falsy in (False, "false", "không", "no", "0"):
        bn_f = chuan_hoa_thong_tin_benh_nhan({"co_thai": falsy})
        assert bn_f["co_thai"] is False and bn_f["thai_ky"] is False and bn_f["mang_thai"] is False
        dl_f = ClinicalPharmacovigilanceEngine.kiem_duyet_toan_dien(["atorvastatin"], {"co_thai": falsy})
        assert dl_f.hop_le is True

    # Kiểm tra end-to-end qua dieu_phoi_ha_tang với co_thai=True
    ht = "Bác sĩ: Kê atorvastatin 20 mg."
    ps = [PhatBieu(id=1, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="atorvastatin 20 mg", bang_chung=[1], thuoc={"ten": "atorvastatin"})]
    kq = MediTracePipelineOrchestrator.xu_ly_ca_kham("ca_co_thai", ht, ps, {"co_thai": "có", "tuoi": 29})
    assert kq.kiem_duyet_duoc_ly.hop_le is False
    assert any("Statin" in c for c in kq.kiem_duyet_duoc_ly.chong_chi_dinh_co_dia)


def test_9_thang_diem_lam_sang_tu_dong_va_co_cau_truc():
    # 1. Không tự bịa CURB-65 khi thiếu tuổi và không có viêm phổi / sinh hiệu / xét nghiệm
    ht_nhe = "Bệnh nhân: Tôi hơi đau đầu nhẹ."
    ps_nhe = [PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="đau đầu nhẹ", bang_chung=[1])]
    kq_nhe = MediTracePipelineOrchestrator.xu_ly_ca_kham("ca_thieu_curb", ht_nhe, ps_nhe, {"gioi_tinh": "nam"})
    assert "CURB-65" not in (kq_nhe.thang_diem_nguy_co or {})

    # 2. Kích hoạt tự động đầy đủ từ bối cảnh lâm sàng + sinh hiệu + xét nghiệm (không cần `thang_diem` thủ công)
    ht_nang = (
        "Bệnh nhân 76 tuổi, nữ, tiền sử rung nhĩ, suy tim NYHA khó thở khi nằm, xơ gan cổ trướng nhiều, "
        "bị viêm phổi sốt cao, lú lẫn, ho ra máu, nghi thuyên tắc phổi và xuất huyết tiêu hóa đi cầu phân đen, "
        "nhịp thở 32, huyết áp 85/55, mạch 115."
    )
    ps_nang = [
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="viêm phổi sốt cao lú lẫn", bang_chung=[1]),
    ]
    bn_nang = {
        "tuoi": 76,
        "gioi_tinh": "nữ",
        "can_nang_kg": 78,
        "chieu_cao_cm": 160,
        "benh_nen": ["rung nhĩ", "suy tim", "tăng huyết áp", "đái tháo đường", "xơ gan"],
    }
    xn_nang = {
        "wbc": 16.0,
        "urea_mmol_l": 11.0,
        "hb": 9.2,
        "bilirubin": 62.0,
        "albumin": 26.0,
        "inr": 2.4,
    }
    kq_full = MediTracePipelineOrchestrator.xu_ly_ca_kham("ca_9_scores", ht_nang, ps_nang, bn_nang, xn_nang)
    td = kq_full.thang_diem_nguy_co
    for ten in ("CURB-65", "CHA2DS2-VASc", "Wells PE", "Glasgow-Blatchford", "GCS", "qSOFA", "NYHA", "Child-Pugh", "BMI"):
        assert ten in td, f"Thiếu thang điểm {ten}"
    assert td["canh_bao_nguy_co_cao"]  # Có cảnh báo nguy cơ cao/nguy kịch

    # 3. Kiểm tra truyền tường minh toàn bộ 9 thang điểm qua `thang_diem`
    bn_cau_truc = {
        "thang_diem": {
            "curb65": {"tuoi": 70, "urea_mmol_l": 8.0, "nhip_tho": 32},
            "cha2ds2_vasc": {
                "tuoi": 75, "gioi_tinh": "nam", "tien_su_suy_tim": True, "tien_su_tang_huyet_ap": True,
                "tien_su_dai_thao_duong": False, "tien_su_dot_quy_tia": False, "tien_su_benh_mach_mau": False,
            },
            "wells_pe": {
                "dau_hieu_dvt": True, "pe_la_chan_doan_hang_dau": True, "nhip_tim_tren_100": True,
                "bat_dong_hoac_phau_thuat_gan_day": False, "tien_su_dvt_pe": False, "ho_ra_mau": False, "ung_thu_dang_dieu_tri": False,
            },
            "glasgow_blatchford": {
                "urea_mmol_l": 10.5, "hb_g_dl": 9.5, "gioi_tinh": "nam", "huyet_ap_tam_thu": 95,
                "nhip_tim": 110, "di_ngoai_phan_den": True, "co_con_ngat": False, "tien_su_benh_gan": False, "tien_su_suy_tim": False,
            },
            "gcs": {"mat": 2, "loi_noi": 2, "van_dong": 3},
            "qsofa": {"nhip_tho": 24, "huyet_ap_tam_thu": 90, "y_thuc_thay_doi": True},
            "nyha": {"kho_tho_khi_nghi": True},
            "child_pugh": {"bilirubin_umol_l": 55, "albumin_g_l": 27, "inr": 2.4, "co_truong": "NHIEU", "benh_nao_gan": "DO_3"},
            "bmi": {"can_nang_kg": 80, "chieu_cao_cm": 165},
        }
    }
    kq_struct = MediTracePipelineOrchestrator.xu_ly_ca_kham("ca_struct_9", "Khám tổng quát", ps_nhe, bn_cau_truc)
    for ten in ("CURB-65", "CHA2DS2-VASc", "Wells PE", "Glasgow-Blatchford", "GCS", "qSOFA", "NYHA", "Child-Pugh", "BMI"):
        assert ten in kq_struct.thang_diem_nguy_co
    assert len(kq_struct.thang_diem_nguy_co["canh_bao_nguy_co_cao"]) >= 5


def test_tai_kiem_tra_nhanh_do_tre_va_tuong_thich_web_python():
    payload = {
        "transcript": "Bệnh nhân: Tôi dị ứng penicillin.\nBác sĩ: Tôi kê augmentin 625 mg và warfarin.",
        "propositions": [
            {"id": 0, "nguoi_noi": "bệnh nhân", "chu_the_id": 0, "noi_dung": "dị ứng penicillin", "bang_chung": [1], "trich_dan": ["dị ứng penicillin"]},
            {"id": 1, "nguoi_noi": "bác sĩ", "chu_the_id": 0, "noi_dung": "augmentin 625 mg", "bang_chung": [2], "trich_dan": ["augmentin 625 mg"], "thuoc": {"ten": "augmentin"}},
            {"id": 2, "nguoi_noi": "bác sĩ", "chu_the_id": 0, "noi_dung": "warfarin 5 mg", "bang_chung": [2], "trich_dan": ["warfarin"], "thuoc": {"ten": "warfarin"}},
        ],
        "thong_tin_benh_nhan": {"tuoi": "72", "gioi_tinh": "nữ", "co_thai": "có", "can_nang_kg": 62, "chieu_cao_cm": 158},
        "xet_nghiem": {"creatinine_mg_dl": 2.0, "inr": 4.1},
        "lich_su_lan_kham": [{"gio_truoc": 24, "xet_nghiem": {"creatinine_mg_dl": 1.0}}],
    }
    # Làm ấm cache module lần 1 rồi đo độ trễ thực thi lặp lại
    _ = tai_kiem_tra_nhanh(payload)
    t0 = time.perf_counter()
    kq = tai_kiem_tra_nhanh(payload)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    assert elapsed_ms < 50.0, f"Độ trễ quá cao: {elapsed_ms:.2f} ms"
    assert kq["hop_le_lam_sang"] is False
    assert any(x["muc_do"] == "CHONG_CHI_DINH" for x in kq["di_ung_cheo"])
    assert kq["duoc_ly"]["hop_le"] is False
    assert kq["quy_dao_lam_sang"]["kdigo_aki"]["giai_doan"] == 2
    assert "BMI" in kq["thang_diem_nguy_co"]
    assert "phan_tang" in kq["canh_bao"]


def test_phan_tang_canh_bao_3_muc_giam_nhieu():
    # Kiểm tra trực tiếp từng tầng
    cb_chan = CanhBao(
        ma="CROSS_ALLERGY", phat_bieu_id=1, luot=[1], trich=["augmentin"],
        ly_do="Dị ứng chéo penicillin", ket_luan=NGHI_RUI_RO, bat_dinh="trung",
        bo_phat_hien="lam_sang:cross_allergy", muc_do=CAO, loai_tt="di_ung",
    )
    cb_xem = CanhBao(
        ma="DOSE_OVER_MAX", phat_bieu_id=2, luot=[1], trich=["paracetamol 6000mg"],
        ly_do="Vượt liều chưa duyệt", ket_luan=CAN_XEM, bat_dinh="trung",
        bo_phat_hien="lam_sang:dose_over_max", muc_do=CAO, loai_tt="thuoc",
    )
    cb_omitted = CanhBao(
        ma="OMITTED_ALLERGY", phat_bieu_id=None, luot=[1], trich=["dị ứng tôm"],
        ly_do="Bỏ sót dị ứng", ket_luan=NGHI_RUI_RO, bat_dinh="trung",
        bo_phat_hien="toan_ca:bo_sot", muc_do=CAO, loai_tt="di_ung",
    )
    cb_nhieu = CanhBao(
        ma="IMPORTANT_MODIFIER_DROPPED", phat_bieu_id=3, luot=[1], trich=["ho về đêm"],
        ly_do="Mất chi tiết", ket_luan=CAN_XEM, bat_dinh=CAO,
        bo_phat_hien="phat_hien:modifier", muc_do=THAP, loai_tt="khac",
    )
    cb_bo_sot_nhe = CanhBao(
        ma="POSSIBLE_IMPORTANT_OMISSION", phat_bieu_id=None, luot=[2], trich=["chào bác sĩ"],
        ly_do="Đoạn chưa ghi", ket_luan=CAN_XEM, bat_dinh=CAO,
        bo_phat_hien="toan_ca:bo_sot", muc_do=THAP, loai_tt="khac",
    )

    assert gop.phan_tang_canh_bao(cb_chan) == gop.TANG_CHAN_NGAY
    assert gop.phan_tang_canh_bao(cb_xem) == gop.TANG_CAN_XEM_XET
    assert gop.phan_tang_canh_bao(cb_omitted) == gop.TANG_CAN_XEM_XET
    assert gop.phan_tang_canh_bao(cb_nhieu) == gop.TANG_TINH_LUOC
    assert gop.phan_tang_canh_bao(cb_bo_sot_nhe) == gop.TANG_TINH_LUOC

    # Hồ sơ sạch có các cảnh báo nhiễu/chất lượng -> bị tinh lược, không làm phiền bác sĩ
    ht_sach = (
        "Bệnh nhân: Chào bác sĩ, hôm nay trời mát nên tôi đi bộ từ sáng, tôi ho về đêm 3 hôm nay.\n"
        "Bệnh nhân: Tôi ho về đêm 3 hôm nay."
    )
    ps_sach = [
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="ho", bang_chung=[1], trich_dan=["tôi ho về đêm 3 hôm nay"]),
        PhatBieu(id=2, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="ho", bang_chung=[2], trich_dan=["Tôi ho về đêm 3 hôm nay"]),
    ]
    kq_gop = gop.chay(ps_sach, ht_sach)
    kq_json = gop.to_dict(kq_gop)
    assert {"phien_ban", "chinh_sach", "theo_phat_bieu", "toan_ca", "trang_thai_D", "cac_dinh_chinh", "phan_tang"} <= set(kq_json.keys())
    pt = kq_json["phan_tang"]
    assert pt["thong_ke"]["tinh_luoc"] >= 1
    assert len(pt["CHAN_NGAY"]) == 0
