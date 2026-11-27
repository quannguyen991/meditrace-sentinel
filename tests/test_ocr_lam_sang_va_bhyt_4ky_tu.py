# -*- coding: utf-8 -*-
import unittest
from src.cong_cu_lam_sang.doc_phieu_xet_nghiem import boc_tach_phieu_cu
from src.cong_cu_lam_sang.tien_kiem_bhyt_va_khoi_phuc_bo_sot import tien_kiem_bhyt_tu_du_lieu


class TestOcrLamSangVaBhyt4KyTu(unittest.TestCase):
    def test_boc_tach_creatinine_umol_va_canh_bao_metformin(self):
        van_ban = "Phiếu XN cũ: Creatinin 220 umol/L, HbA1c 8.1%. Đơn cũ: Glucophage 850mg, Allopurinol 300mg."
        kq = boc_tach_phieu_cu(van_ban, tuoi=68, la_nu=True)
        cs = kq["chi_so"]
        self.assertAlmostEqual(cs["creatinine"], round(220 / 88.4, 2), places=2)
        self.assertLess(cs["egfr"], 30.0)
        self.assertIn("Metformin", kq["thuoc_nhan_dien"])
        self.assertIn("Allopurinol", kq["thuoc_nhan_dien"])
        self.assertTrue(len(kq["hieu_chinh_lieu"]["canh_bao_hieu_chinh_than"]) >= 1)

    def test_creatinine_thieu_don_vi_va_tuoi_none(self):
        kq_mg = boc_tach_phieu_cu("Creatinin: 1.8", tuoi=None)
        self.assertAlmostEqual(kq_mg["chi_so"]["creatinine"], 1.8)
        # Thieu tuoi: khong con mac dinh 50 tuoi -> khong uoc tinh eGFR, danh dau thieu_tuoi
        self.assertNotIn("egfr", kq_mg["chi_so"])
        self.assertEqual(kq_mg["hieu_chinh_lieu"]["chuc_nang_than"]["phuong_phap_uoc_tinh"], "thieu_tuoi")

        kq_umol = boc_tach_phieu_cu("Creatinin: 180", tuoi=None)
        self.assertAlmostEqual(kq_umol["chi_so"]["creatinine"], round(180 / 88.4, 2), places=2)

    def test_nhi_khoa_tuoi_duoi_18_khong_bao_suy_than_g5_gia(self):
        kq = boc_tach_phieu_cu("Creatinin: 0.6 mg/dL, Metformin 500mg", tuoi=10)
        self.assertNotIn("egfr", kq["chi_so"])
        self.assertIsNone(kq["hieu_chinh_lieu"]["chuc_nang_than"]["egfr_ckd_epi"])
        self.assertEqual(kq["hieu_chinh_lieu"]["tong_so_canh_bao"], 0)

    def test_gioi_tinh_la_nu_he_so_0_85_trong_crcl(self):
        kq_nam = boc_tach_phieu_cu("Creatinin: 1.5 mg/dL", tuoi=60, la_nu=False, can_nang_kg=60.0)
        kq_nu = boc_tach_phieu_cu("Creatinin: 1.5 mg/dL", tuoi=60, la_nu=True, can_nang_kg=60.0)
        crcl_nam = kq_nam["hieu_chinh_lieu"]["chuc_nang_than"]["crcl_cockcroft_gault"]
        crcl_nu = kq_nu["hieu_chinh_lieu"]["chuc_nang_than"]["crcl_cockcroft_gault"]
        self.assertAlmostEqual(crcl_nu, round(crcl_nam * 0.85, 1), delta=0.2)

    def test_kali_cao_spironolacton_canh_bao_critical(self):
        kq = boc_tach_phieu_cu("Creatinin: 1.0 mg/dL, Kali: 6.2 mmol/L, Spironolacton 25mg", tuoi=65)
        self.assertTrue(kq["hieu_chinh_lieu"]["co_canh_bao_critical"])
        cbs = kq["hieu_chinh_lieu"]["canh_bao_hieu_chinh_than"]
        self.assertTrue(any("Spironolacton" in c["thuoc"] for c in cbs))

    def test_rosuvastatin_va_paracetamol_men_gan_tren_3x_uln(self):
        kq_statin = boc_tach_phieu_cu("AST: 135 U/L, ALT: 140 U/L, Crestor 10mg", tuoi=60)
        self.assertTrue(kq_statin["hieu_chinh_lieu"]["chuc_nang_gan"]["bat_thuong"])
        self.assertTrue(len(kq_statin["hieu_chinh_lieu"]["canh_bao_hieu_chinh_gan"]) >= 1)

        kq_para = boc_tach_phieu_cu("AST: 130 U/L, Panadol 500mg", tuoi=45)
        self.assertTrue(len(kq_para["hieu_chinh_lieu"]["canh_bao_hieu_chinh_gan"]) >= 1)

    def test_bhyt_icd10_4_ky_tu_va_canh_bao_xuat_toan(self):
        props = [
            {
                "text": "Đái tháo đường biến chứng thận, xét nghiệm albumin niệu dương tính",
                "section": "CHẨN ĐOÁN",
                "negated": False,
                "trich_dan": "bị đái tháo đường biến chứng thận",
            },
            {
                "text": "Kê đơn Omeprazol 20mg ngày 1 viên",
                "section": "KẾ HOẠCH ĐIỀU TRỊ",
                "negated": False,
                "drug": "omeprazol",
            },
        ]
        kq = tien_kiem_bhyt_tu_du_lieu(props, "bị đái tháo đường biến chứng thận")
        ma_goi_y = [x["ma"] for x in kq["icd10_chi_tiet"]]
        self.assertIn("E11.2", ma_goi_y)
        self.assertTrue(len(kq["canh_bao_xuat_toan"]) >= 1)
        self.assertTrue(any("omeprazol" in c["ly_do"].lower() for c in kq["canh_bao_xuat_toan"]))

    def test_bhyt_khong_goi_y_icd10_khi_bac_si_phu_dinh(self):
        props = [
            {
                "id": 1,
                "text": "Bệnh nhân không bị tiểu đường",
                "nguoi_noi": "bác sĩ",
                "negated": True,
            }
        ]
        kq = tien_kiem_bhyt_tu_du_lieu(props, "")
        self.assertEqual(kq["icd10_chi_tiet"], [])

        # Hỗ trợ key `phu_dinh` thay vì `negated`
        props2 = [{"id": 2, "text": "Không tăng huyết áp", "nguoi_noi": "bác sĩ", "phu_dinh": True}]
        kq2 = tien_kiem_bhyt_tu_du_lieu(props2, "")
        self.assertEqual(kq2["icd10_chi_tiet"], [])

    def test_bhyt_input_rong_va_biet_duoc(self):
        kq_rong = tien_kiem_bhyt_tu_du_lieu([], "")
        self.assertEqual(kq_rong["icd10_chi_tiet"], [])
        self.assertTrue(any("MA_BENH" in c["ly_do"] for c in kq_rong["canh_bao_xuat_toan"]))

        kq_bd = tien_kiem_bhyt_tu_du_lieu(
            [{"text": "Đang uống Glucophage 850mg", "section": "KẾ HOẠCH"}],
            "",
        )
        self.assertTrue(any("glucophage" in c["ly_do"].lower() for c in kq_bd["canh_bao_xuat_toan"]))


if __name__ == "__main__":
    unittest.main()
