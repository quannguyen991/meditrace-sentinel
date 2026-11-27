# -*- coding: utf-8 -*-
"""Kiểm thử Động cơ Dị ứng Chéo Thuốc theo Nhóm ATC & Chuỗi nhánh Hóa học (`src/cong_cu_lam_sang/di_ung_cheo.py`)
và tích hợp vào `duoc_ly_lam_sang`, `canh_bao.lam_sang`, `dieu_phoi_ha_tang`."""
import pytest

from src.canh_bao import gop, lam_sang
from src.canh_bao.loai import CAN_XEM, NGHI_RUI_RO
from src.canh_bao.phat_hien import NguCanh
from src.cong_cu_lam_sang.di_ung_cheo import CHONG_CHI_DINH, THAN_TRONG, kiem_tra_di_ung_cheo
from src.he_thong.dieu_phoi_cac_chot_an_toan import MediTracePipelineOrchestrator
from src.cong_cu_lam_sang.canh_bao_tuong_tac_thuoc import ClinicalPharmacovigilanceEngine
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu

KHOA_BAT_BUOC = {
    "thuoc",
    "di_ung_goc",
    "nhom_cheo",
    "muc_do",
    "co_che",
    "khuyen_cao_thay_the",
}


def test_khop_truc_tiep_va_biet_duoc_phoi_hop():
    kq = kiem_tra_di_ung_cheo(["amoxicillin"], ["Augmentin 625 mg"])
    assert len(kq) == 1
    assert set(kq[0].keys()) == KHOA_BAT_BUOC
    assert kq[0]["muc_do"] == CHONG_CHI_DINH

    kq_sulfa = kiem_tra_di_ung_cheo(["sulfamethoxazole"], ["Bactrim"])
    assert len(kq_sulfa) == 1 and kq_sulfa[0]["muc_do"] == CHONG_CHI_DINH

    kq_zyloric = kiem_tra_di_ung_cheo("allopurinol", [{"ten": "Zyloric 300 mg"}])
    assert len(kq_zyloric) == 1 and kq_zyloric[0]["muc_do"] == CHONG_CHI_DINH


def test_dinh_dang_dau_vao_linh_hoat():
    kq_str = kiem_tra_di_ung_cheo("penicillin, aspirin", "amoxicillin, paracetamol")
    assert len(kq_str) == 1 and kq_str[0]["thuoc"] == "amoxicillin"

    kq_set = kiem_tra_di_ung_cheo(("penicillin",), {"cephalexin", "paracetamol"})
    assert len(kq_set) == 1 and kq_set[0]["muc_do"] == CHONG_CHI_DINH

    kq_dict = kiem_tra_di_ung_cheo(
        [{"hoat_chat": "ibuprofen"}],
        [{"ten": "naproxen"}, {"hoat_chat": "celecoxib"}],
    )
    theo_thuoc = {x["thuoc"]: x["muc_do"] for x in kq_dict}
    assert theo_thuoc["naproxen"] == CHONG_CHI_DINH
    assert theo_thuoc["celecoxib"] == THAN_TRONG

    assert kiem_tra_di_ung_cheo([], ["amoxicillin"]) == []
    assert kiem_tra_di_ung_cheo(["penicillin"], []) == []


def test_beta_lactam_chuoi_nhanh_r1_va_phan_nhom():
    # Penicillin <-> Aminopenicillin / Gen-1 shared-R1 Cephalosporins -> CHONG_CHI_DINH
    for thuoc in ("amoxicillin", "ampicillin", "Augmentin", "cephalexin", "cefadroxil", "cefazolin"):
        kq = kiem_tra_di_ung_cheo(["penicillin"], [thuoc])
        assert kq and kq[0]["muc_do"] == CHONG_CHI_DINH, thuoc

    # Penicillin / Aminopenicillin <-> distinct-R1 2nd/3rd/4th-gen Cephalosporins -> THAN_TRONG
    for thuoc in ("cefuroxime", "cefixime", "cefdinir", "cefotaxime", "ceftriaxone", "ceftazidime", "cefepime"):
        kq = kiem_tra_di_ung_cheo(["amoxicillin"], [thuoc])
        assert kq and kq[0]["muc_do"] == THAN_TRONG, thuoc

    # Penicillin / Cephalosporin <-> Carbapenems -> THAN_TRONG
    for carb in ("meropenem", "imipenem", "ertapenem"):
        assert kiem_tra_di_ung_cheo(["penicillin"], [carb])[0]["muc_do"] == THAN_TRONG
        assert kiem_tra_di_ung_cheo(["ceftriaxone"], [carb])[0]["muc_do"] == THAN_TRONG

    # Ceftazidime <-> Aztreonam shared R1 -> CHONG_CHI_DINH, while Penicillin <-> Aztreonam -> safe
    assert kiem_tra_di_ung_cheo(["ceftazidime"], ["aztreonam"])[0]["muc_do"] == CHONG_CHI_DINH
    assert kiem_tra_di_ung_cheo(["aztreonam"], ["ceftazidime"])[0]["muc_do"] == CHONG_CHI_DINH
    assert kiem_tra_di_ung_cheo(["penicillin"], ["aztreonam"]) == []


def test_sulfonamide_nsaid_macrolide_fq_acei():
    # Sulfonamides: antimicrobial <-> antimicrobial (CHONG_CHI_DINH) vs non-antibiotic (THAN_TRONG)
    assert kiem_tra_di_ung_cheo(["bactrim"], ["sulfadiazine"])[0]["muc_do"] == CHONG_CHI_DINH
    for non_abx in ("furosemide", "hydrochlorothiazide", "indapamide", "celecoxib", "glimepiride", "gliclazide", "acetazolamide"):
        kq = kiem_tra_di_ung_cheo(["sulfamethoxazole"], [non_abx])
        assert kq and kq[0]["muc_do"] == THAN_TRONG, non_abx

    # NSAIDs: COX-1 <-> COX-1 (CHONG_CHI_DINH) vs selective COX-2 (THAN_TRONG)
    for cox1 in ("aspirin", "diclofenac", "naproxen", "meloxicam", "piroxicam", "ketoprofen", "indomethacin", "ketorolac"):
        assert kiem_tra_di_ung_cheo(["ibuprofen"], [cox1])[0]["muc_do"] == CHONG_CHI_DINH
    for cox2 in ("celecoxib", "etoricoxib"):
        assert kiem_tra_di_ung_cheo(["ibuprofen"], [cox2])[0]["muc_do"] == THAN_TRONG

    # Macrolides & Fluoroquinolones: intra-class THAN_TRONG, exact match CHONG_CHI_DINH
    assert kiem_tra_di_ung_cheo(["clarithromycin"], ["azithromycin"])[0]["muc_do"] == THAN_TRONG
    assert kiem_tra_di_ung_cheo(["clarithromycin"], ["clarithromycin"])[0]["muc_do"] == CHONG_CHI_DINH
    assert kiem_tra_di_ung_cheo(["ciprofloxacin"], ["levofloxacin"])[0]["muc_do"] == THAN_TRONG
    assert kiem_tra_di_ung_cheo(["ciprofloxacin"], ["ciprofloxacin"])[0]["muc_do"] == CHONG_CHI_DINH

    # ACEi angioedema class effect -> CHONG_CHI_DINH
    assert kiem_tra_di_ung_cheo(["enalapril"], ["perindopril"])[0]["muc_do"] == CHONG_CHI_DINH
    assert kiem_tra_di_ung_cheo(["captopril"], ["lisinopril"])[0]["muc_do"] == CHONG_CHI_DINH

    # Unrelated safe drug
    assert kiem_tra_di_ung_cheo(["penicillin"], ["paracetamol"]) == []


def test_tich_hop_duoc_ly_lam_sang_di_ung_cheo():
    kq_cam = ClinicalPharmacovigilanceEngine.kiem_duyet_toan_dien(
        ["Augmentin 625 mg"],
        co_dia={"di_ung": ["penicillin"]},
    )
    assert kq_cam.hop_le is False
    assert len(kq_cam.canh_bao_di_ung_cheo) == 1
    assert kq_cam.canh_bao_di_ung_cheo[0]["muc_do"] == CHONG_CHI_DINH
    assert any("DỊ ỨNG CHÉO" in x for x in kq_cam.chong_chi_dinh_co_dia)
    assert any("CHỐNG CHỈ ĐỊNH" in x for x in kq_cam.giai_trinh_duoc_ly)

    kq_than_trong = ClinicalPharmacovigilanceEngine.kiem_duyet_toan_dien(
        ["ceftriaxone"],
        co_dia={"tien_su_di_ung": ["penicillin"]},
    )
    assert kq_than_trong.hop_le is True
    assert len(kq_than_trong.canh_bao_di_ung_cheo) == 1
    assert kq_than_trong.canh_bao_di_ung_cheo[0]["muc_do"] == THAN_TRONG
    assert any("THẬN TRỌNG DỊ ỨNG CHÉO" in x for x in kq_than_trong.giai_trinh_duoc_ly)


def test_tich_hop_canh_bao_lam_sang_cross_allergy_khong_pha_contraindication():
    ht = "Bệnh nhân: Dị ứng penicillin.\nBác sĩ: Tôi kê augmentin 625 mg ngày 2 lần."
    ps = [
        PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng penicillin", bang_chung=[1]),
        PhatBieu(
            id=1, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="augmentin 625 mg ngày 2 lần",
            bang_chung=[2], tinh_huong="kế hoạch",
            thuoc={"ten": "augmentin", "lieu": "625 mg", "so_lan": "ngày 2 lần"},
        ),
    ]
    cbs = lam_sang.quet(NguCanh(ht), ps)
    assert not [c for c in cbs if c.ma == "CONTRAINDICATION"]
    cross = [c for c in cbs if c.ma == "CROSS_ALLERGY"]
    assert len(cross) == 1
    assert cross[0].phat_bieu_id == 1
    assert cross[0].ket_luan == NGHI_RUI_RO

    # Ceftriaxone trên nền dị ứng penicillin -> CROSS_ALLERGY mức CAN_XEM
    ps2 = [
        PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng penicillin", bang_chung=[1]),
        PhatBieu(id=1, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="ceftriaxone 1 g", bang_chung=[2], thuoc={"ten": "ceftriaxone"}),
    ]
    cross2 = [c for c in lam_sang.quet(NguCanh(ht), ps2) if c.ma == "CROSS_ALLERGY"]
    assert len(cross2) == 1 and cross2[0].ket_luan == CAN_XEM

    # Nếu đã khớp trực tiếp CONTRAINDICATION (amoxicillin -> augmentin) thì không phát trùng CROSS_ALLERGY
    ps3 = [
        PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng amoxicillin", bang_chung=[1]),
        PhatBieu(id=1, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="augmentin", bang_chung=[2], thuoc={"ten": "augmentin"}),
    ]
    cbs3 = lam_sang.quet(NguCanh("Bệnh nhân: Dị ứng amoxicillin.\nBác sĩ: kê augmentin."), ps3)
    assert any(c.ma == "CONTRAINDICATION" for c in cbs3)
    assert not any(c.ma == "CROSS_ALLERGY" for c in cbs3)


def test_dieu_phoi_ha_tang_tach_di_ung_nguoi_benh_va_co_lap_nguoi_nha():
    ht = (
        "Bệnh nhân: Tôi bị dị ứng penicillin.\n"
        "Người nhà: Mẹ tôi thì dị ứng aspirin.\n"
        "Bác sĩ: Tôi kê augmentin 625 mg và paracetamol 500 mg."
    )
    ps_benh_nhan = [
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng penicillin", bang_chung=[1], trich_dan=["dị ứng penicillin"]),
        PhatBieu(id=2, nguoi_noi="người nhà", chu_the_id=1, noi_dung="mẹ dị ứng aspirin", bang_chung=[2], trich_dan=["mẹ tôi thì dị ứng aspirin"]),
        PhatBieu(id=3, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="augmentin 625 mg", bang_chung=[3], thuoc={"ten": "augmentin"}),
        PhatBieu(id=4, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="paracetamol 500 mg", bang_chung=[3], thuoc={"ten": "paracetamol"}),
    ]
    kq = MediTracePipelineOrchestrator.xu_ly_ca_kham("ca_du_cheo_1", ht, ps_benh_nhan, {"tuoi": 40})
    assert kq.kiem_duyet_duoc_ly.hop_le is False
    assert any(x["thuoc"] == "augmentin" and x["muc_do"] == CHONG_CHI_DINH for x in kq.kiem_duyet_duoc_ly.canh_bao_di_ung_cheo)

    # Dị ứng chỉ ở người nhà (chu_the_id=1), phủ định, giả định hoặc chưa ghi nhận -> KHÔNG chặn ibuprofen của bệnh nhân
    ps_co_lap = [
        PhatBieu(id=1, nguoi_noi="người nhà", chu_the_id=1, noi_dung="dị ứng aspirin", bang_chung=[2]),
        PhatBieu(id=2, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng aspirin", phu_dinh=True, bang_chung=[1]),
        PhatBieu(id=3, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng aspirin", tinh_huong="giả định", bang_chung=[1]),
        PhatBieu(id=4, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng aspirin", do_chac_chan="chưa ghi nhận", bang_chung=[1]),
        PhatBieu(id=5, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="ibuprofen 400 mg", bang_chung=[3], thuoc={"ten": "ibuprofen"}),
    ]
    kq_safe = MediTracePipelineOrchestrator.xu_ly_ca_kham("ca_du_cheo_2", ht, ps_co_lap, {"tuoi": 40})
    assert kq_safe.kiem_duyet_duoc_ly.canh_bao_di_ung_cheo == []
    assert kq_safe.kiem_duyet_duoc_ly.hop_le is True
