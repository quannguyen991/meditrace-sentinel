# -*- coding: utf-8 -*-
"""Phep kiem lop canh bao (src/canh_bao).

Moi loai canh bao co it nhat: DUONG (co loi -> phai bao), AM (dung -> khong bao),
AM KHO (co tu khoa giong loi nhung ngu canh dung -> khong bao). Nhom CAP TUONG
PHAN cuoi tep: hai hoi thoai chi khac MOT bien (chu the, phu dinh, dieu kien,
thoi gian) — de biet bo phat hien hieu dung bien nao gay loi.
"""
import pytest

from src.canh_bao import gop, so_lieu
from src.canh_bao.loai import CAO, LOAI, LOI_PHAT_HIEN, THAP, TRUNG
from src.phat_bieu import PhatBieu


def ht(*luot):
    return "\n".join(luot)


def pb(i, nd, dan, **kw):
    kw.setdefault("nguoi_noi", "bệnh nhân")
    kw.setdefault("chu_the_id", 0)
    return PhatBieu(id=i, noi_dung=nd, bang_chung=list(dan), **kw)


def chay(hoi_thoai, *ps, **kw):
    return gop.chay(list(ps), hoi_thoai, **kw)


def ma(hoi_thoai, *ps, id_=None, **kw):
    kq = chay(hoi_thoai, *ps, **kw)
    ra = set()
    for i, v in kq["theo_phat_bieu"].items():
        if id_ is None or i == id_:
            ra |= {c.ma for c in v["tat_ca"]}
    return ra


# ============================================================ so lieu
@pytest.mark.parametrize("cau, ky_vong", [
    ("uống amoxicillin 500mg ngày 2 lần", [(500, None, "mg"), (2, None, "lần")]),
    ("sốt 38 độ 5", [(38.5, None, "độ")]),
    ("ba bốn ngày nay", [(3, 4, "ngày")]),
    ("3-5 ngày", [(3, 5, "ngày")]),
    ("hai mươi lăm tuổi", [(25, None, "tuổi")]),
    ("mười lăm ngày", [(15, None, "ngày")]),
    ("0,5 mg", [(0.5, None, "mg")]),
    ("một ngày rưỡi", [(1.5, None, "ngày")]),
    ("năm ngoái có mổ", []),                     # "nam" la tu chi thoi diem, khong phai so
    ("phòng 3 tầng 2", []),                      # so khong don vi: bo qua
])
def test_tach_so(cau, ky_vong):
    assert [(s.gia_tri, s.tren, s.don_vi) for s in so_lieu.tach(cau)] == ky_vong


def test_uoc_chung():
    assert so_lieu.tach("hình như giảm 5 kg")[0].uoc
    assert not so_lieu.tach("giảm 5 kg")[0].uoc


# ============================================================ con so
H_LIEU = ht("Bác sĩ: Anh đang uống thuốc gì?", "Bệnh nhân: Tôi uống amoxicillin 500 mg, ngày 1 lần.")


def test_lech_thap_phan():
    assert "DECIMAL_MISMATCH" in ma(H_LIEU, pb(1, "amoxicillin 50 mg", [2]))


def test_sai_don_vi():
    assert "UNIT_MISMATCH" in ma(H_LIEU, pb(1, "amoxicillin 500 g", [2]))


def test_sai_so_lan():
    assert "FREQUENCY_MISMATCH" in ma(H_LIEU, pb(1, "amoxicillin 500 mg, 2 lần/ngày", [2]))


def test_so_dung_khong_bao():
    m = ma(H_LIEU, pb(1, "amoxicillin 500 mg, ngày một lần", [2]))
    assert not m & {"DECIMAL_MISMATCH", "UNIT_MISMATCH", "FREQUENCY_MISMATCH", "DOSE_MISMATCH", "NUMERIC_MISMATCH"}


def test_sai_thoi_gian_don_vi():
    h = ht("Bệnh nhân: Tôi ho 10 ngày nay.")
    assert "DURATION_MISMATCH" in ma(h, pb(1, "ho 10 tuần", [1]))


def test_so_chu_va_so_viet_khop():         # am kho: "hai ngay" = "2 ngay"
    h = ht("Bệnh nhân: Tôi sốt hai ngày rồi, 38 độ 5.")
    m = ma(h, pb(1, "sốt 2 ngày, 38,5 độ", [1]))
    assert not m & {"DURATION_MISMATCH", "NUMERIC_MISMATCH", "UNIT_MISMATCH"}


def test_khoang_bi_rut():
    h = ht("Bệnh nhân: Tôi ho ba bốn ngày nay.")
    assert "RANGE_COLLAPSED" in ma(h, pb(1, "ho 3 ngày", [1]))
    assert "RANGE_COLLAPSED" not in ma(h, pb(1, "ho 3-4 ngày", [1]))


def test_mat_uoc_chung():
    h = ht("Bệnh nhân: Hình như tôi giảm 5 kg.")
    assert "APPROXIMATION_LOST" in ma(h, pb(1, "giảm 5 kg", [1]))


def test_so_bia():
    h = ht("Bệnh nhân: Tôi ho mấy hôm nay.")
    assert "DURATION_MISMATCH" in ma(h, pb(1, "ho 5 ngày", [1]))


# ============================================================ hoi - dap
H_HOI = ("Bác sĩ: Anh có đau ngực không?",)


def test_tra_loi_khong_ma_ghi_co():
    assert "NEGATION_FLIP" in ma(ht(*H_HOI, "Bệnh nhân: Dạ không."), pb(1, "đau ngực", [1, 2]))


def test_tra_loi_co_ghi_co():
    assert "NEGATION_FLIP" not in ma(ht(*H_HOI, "Bệnh nhân: Dạ có."), pb(1, "đau ngực", [1, 2]))


def test_tra_loi_khong_nhung_noi_viec_khac():    # am kho
    h = ht(*H_HOI, "Bệnh nhân: Không, nhưng tôi hay ho về đêm.")
    assert "NEGATION_FLIP" not in ma(h, pb(1, "ho về đêm", [1, 2]))


def test_tra_loi_co_ma_ghi_khong():
    assert "NEGATION_FLIP" in ma(ht(*H_HOI, "Bệnh nhân: Dạ có."), pb(1, "không đau ngực", [1, 2], phu_dinh=True))


def test_chi_dan_cau_hoi():
    assert "QUESTION_AS_FACT" in ma(ht(*H_HOI, "Bệnh nhân: Dạ có."), pb(1, "đau ngực", [1]))
    assert "QUESTION_AS_FACT" not in ma(ht(*H_HOI, "Bệnh nhân: Dạ có."), pb(1, "đau ngực", [1, 2]))


# ============================================================ khong nho, pham vi phu dinh
def test_khong_nho_thanh_khong_co():
    h = ht("Bác sĩ: Anh có dị ứng thuốc gì không?", "Bệnh nhân: Tôi không nhớ có dị ứng thuốc không.")
    assert "UNKNOWN_AS_NEGATIVE" in ma(h, pb(1, "không dị ứng thuốc", [1, 2], phu_dinh=True))


def test_khong_co_that():
    h = ht("Bác sĩ: Anh có dị ứng thuốc gì không?", "Bệnh nhân: Tôi không có dị ứng thuốc.")
    assert "UNKNOWN_AS_NEGATIVE" not in ma(h, pb(1, "không dị ứng thuốc", [1, 2], phu_dinh=True))


def test_khong_nho_mot_viec_khac():           # am kho
    h = ht("Bệnh nhân: Tôi không nhớ tên thuốc nhưng không có dị ứng gì.")
    assert "UNKNOWN_AS_NEGATIVE" not in ma(h, pb(1, "không dị ứng", [1], phu_dinh=True))


def test_khong_dung_dau():
    h = ht("Người nhà: Chồng em méo miệng từ hôm kia.", "Bệnh nhân: Không đúng đâu, em méo miệng hai hôm rồi.")
    assert "NEGATION_SCOPE_ERROR" in ma(h, pb(1, "không méo miệng", [2], phu_dinh=True))
    assert "NEGATION_SCOPE_ERROR" not in ma(h, pb(1, "méo miệng", [2]))


def test_khong_dung_dau_roi_phu_dinh_that():    # am kho
    h = ht("Bệnh nhân: Không đúng đâu, tôi không sốt.")
    assert "NEGATION_SCOPE_ERROR" not in ma(h, pb(1, "không sốt", [1], phu_dinh=True))


# ============================================================ ke hoach, dieu kien, loi dan
def test_dieu_kien_ghi_thanh_su_viec():
    h = ht("Bác sĩ: Nếu mai còn sốt thì quay lại để chụp phim.")
    assert "CONDITION_AS_FACT" in ma(h, pb(1, "chụp phim", [1], nguoi_noi="bác sĩ", trich_dan=["quay lại để chụp phim"]))


def test_ke_hoach_co_dieu_kien_mat_dieu_kien():
    h = ht("Bác sĩ: Nếu mai còn sốt thì quay lại để chụp phim.")
    assert "CONDITION_AS_CONFIRMED_PLAN" in ma(h, pb(1, "chụp phim", [1], nguoi_noi="bác sĩ", tinh_huong="kế hoạch"))
    assert "CONDITION_AS_CONFIRMED_PLAN" not in ma(
        h, pb(1, "nếu còn sốt thì chụp phim", [1], nguoi_noi="bác sĩ", tinh_huong="kế hoạch"))


def test_xet_nghiem_se_lam_ghi_co_ket_qua():
    h = ht("Bác sĩ: Tuần sau anh đi xét nghiệm máu nhé.")
    assert "PLANNED_TEST_AS_RESULT" in ma(h, pb(1, "xét nghiệm máu bình thường", [1], nguoi_noi="bác sĩ"))
    assert "PLAN_AS_FACT" in ma(h, pb(1, "đã xét nghiệm máu", [1], nguoi_noi="bác sĩ"))
    m = ma(h, pb(1, "xét nghiệm máu", [1], nguoi_noi="bác sĩ", tinh_huong="kế hoạch"))
    assert not m & {"PLAN_AS_FACT", "PLANNED_TEST_AS_RESULT"}


def test_ke_hoach_da_qua():                 # am kho: "lan truoc da hen" la su viec
    h = ht("Bệnh nhân: Lần trước bác sĩ đã hẹn tôi xét nghiệm, kết quả bình thường.")
    assert "PLAN_AS_FACT" not in ma(h, pb(1, "xét nghiệm bình thường", [1]))


def test_loi_dan_ghi_thanh_su_viec():
    h = ht("Bác sĩ: Anh nên uống nhiều nước.")
    assert "RECOMMENDATION_AS_FACT" in ma(h, pb(1, "uống nhiều nước", [1], nguoi_noi="bác sĩ"))
    assert "RECOMMENDATION_AS_FACT" not in ma(ht("Bệnh nhân: Tôi uống nhiều nước."), pb(1, "uống nhiều nước", [1]))


def test_nguoi_nha_noi_ke_hoach():
    h = ht("Người nhà: Chắc phải cho cháu đi chụp phim.")
    assert "FAMILY_STATEMENT_AS_CLINICIAN_PLAN" in ma(h, pb(1, "chụp phim", [1], nguoi_noi="người nhà",
                                                            tinh_huong="kế hoạch"))
    h2 = ht("Người nhà: Bác sĩ bảo cho cháu đi chụp phim.")
    assert "FAMILY_STATEMENT_AS_CLINICIAN_PLAN" not in ma(h2, pb(1, "chụp phim", [1], nguoi_noi="người nhà",
                                                                 tinh_huong="kế hoạch"))


# ============================================================ thoi diem, thuoc
def test_thuoc_da_ngung_ghi_dang_dung():
    h = ht("Bệnh nhân: Trước đây tôi dùng metformin, giờ bỏ rồi.")
    p = pb(1, "đang dùng metformin", [1], thuoc={"ten": "metformin", "trang_thai_dung": "đang dùng"})
    assert "DISCONTINUED_AS_CURRENT" in ma(h, p)


def test_thuoc_dang_dung_that():
    h = ht("Bệnh nhân: Hiện tôi đang dùng metformin.")
    p = pb(1, "đang dùng metformin", [1], thuoc={"ten": "metformin", "trang_thai_dung": "đang dùng"})
    assert "DISCONTINUED_AS_CURRENT" not in ma(h, p)


def test_ngung_roi_uong_lai():             # am kho
    h = ht("Bệnh nhân: Tôi ngưng metformin một tuần rồi uống lại.")
    p = pb(1, "đang dùng metformin", [1], thuoc={"ten": "metformin", "trang_thai_dung": "đang dùng"})
    assert "DISCONTINUED_AS_CURRENT" not in ma(h, p)


def test_truoc_day_ghi_hien_tai():
    h = ht("Bệnh nhân: Hồi trước tôi hay đau đầu.")
    assert "PAST_CURRENT_CONFUSION" in ma(h, pb(1, "đau đầu", [1], thoi_gian_su_kien="hiện tại"))
    h2 = ht("Bệnh nhân: Dạo này tôi hay đau đầu.")
    assert "PAST_CURRENT_CONFUSION" not in ma(h2, pb(1, "đau đầu", [1], thoi_gian_su_kien="hiện tại"))


def test_ten_thuoc_bia():
    h = ht("Bệnh nhân: Tôi uống amoxicillin.")
    p = pb(1, "uống ampicillin", [1], thuoc={"ten": "ampicillin"})
    assert "FABRICATED_MEDICATION" in ma(h, p)


def test_ten_thuoc_o_luot_khac():
    h = ht("Bệnh nhân: Tôi uống amoxicillin.", "Bệnh nhân: Vợ tôi uống ampicillin.")
    p = pb(1, "uống ampicillin", [1], thuoc={"ten": "ampicillin"})
    assert "MEDICATION_ENTITY_MISMATCH" in ma(h, p)


def test_ten_thuoc_bien_the_khong_bao():    # am kho: amlodipin ~ amlodipine
    h = ht("Bệnh nhân: Tôi uống amlodipine 5 mg.")
    p = pb(1, "amlodipin 5 mg", [1], thuoc={"ten": "amlodipin"})
    assert not ma(h, p) & {"FABRICATED_MEDICATION", "MEDICATION_ENTITY_MISMATCH"}


def test_chat_di_ung_bia():
    h = ht("Bệnh nhân: Tôi dị ứng penicillin.")
    assert "FABRICATED_ALLERGY" in ma(h, pb(1, "dị ứng aspirin", [1]))
    assert "FABRICATED_ALLERGY" not in ma(h, pb(1, "dị ứng penicillin", [1]))


# ============================================================ ben, muc do, tan suat
def test_ben_trai_phai():
    h = ht("Bệnh nhân: Tôi đau bụng bên trái.")
    assert "LATERALITY_CHANGED" in ma(h, pb(1, "đau bụng bên phải", [1]))
    assert "LATERALITY_CHANGED" not in ma(h, pb(1, "đau bụng bên trái", [1]))


def test_phai_la_tu_tinh_thai():            # am kho: "phai" = "must"
    h = ht("Bệnh nhân: Tôi đau bụng bên trái, phải nằm nghỉ.")
    assert "LATERALITY_CHANGED" not in ma(h, pb(1, "đau bụng bên trái", [1]))


def test_muc_do_nhe_thanh_nang():
    h = ht("Bệnh nhân: Tôi đau đầu nhẹ thôi.")
    assert "SEVERITY_CHANGED" in ma(h, pb(1, "đau đầu dữ dội", [1]))
    assert "SEVERITY_CHANGED" not in ma(h, pb(1, "đau đầu nhẹ", [1]))


def test_tan_suat():
    h = ht("Bệnh nhân: Thỉnh thoảng tôi đau đầu.")
    assert "FREQUENCY_WORD_CHANGED" in ma(h, pb(1, "thường xuyên đau đầu", [1]))


# ============================================================ dinh chinh
def test_dinh_chinh_giu_so_cu():
    h = ht("Bệnh nhân: Tôi ho khoảng 7 ngày... à không, 10 ngày rồi.")
    assert "CORRECTION_NOT_APPLIED" in ma(h, pb(1, "ho 7 ngày", [1]))
    assert "CORRECTION_NOT_APPLIED" not in ma(h, pb(1, "ho 10 ngày", [1]))


def test_dinh_chinh_giu_ca_hai():
    h = ht("Bệnh nhân: Tôi ho khoảng 7 ngày... à không, 10 ngày rồi.")
    assert "OLD_AND_NEW_VALUE_DUPLICATED" in ma(h, pb(1, "ho 7 ngày, 10 ngày", [1]))


def test_chu_khong_phai():
    h = ht("Bệnh nhân: Tôi ho 10 ngày chứ không phải 7 ngày.")
    assert "CORRECTION_NOT_APPLIED" in ma(h, pb(1, "ho 7 ngày", [1]))


def test_dien_bien_khong_phai_dinh_chinh():   # am kho
    h = ht("Bệnh nhân: Hôm qua đau 7/10, hôm nay còn 3/10.")
    assert "CORRECTION_NOT_APPLIED" not in ma(h, pb(1, "đau 7/10", [1], moc_thoi_gian="hôm qua"))


def test_dinh_chinh_qua_luot():
    h = ht("Bệnh nhân: Tôi sốt 3 ngày.", "Bác sĩ: Vâng.", "Bệnh nhân: À không, 5 ngày rồi.")
    assert "CORRECTION_NOT_APPLIED" in ma(h, pb(1, "sốt 3 ngày", [1]))


# ============================================================ cau mau
def test_khong_di_ung_khong_can_cu():
    h = ht("Bác sĩ: Có dị ứng gì không?", "Bệnh nhân: Để tôi nghĩ đã.")
    assert "UNSUPPORTED_BOILERPLATE" in ma(h, pb(1, "không dị ứng", [1, 2], phu_dinh=True))
    h2 = ht("Bác sĩ: Có dị ứng gì không?", "Bệnh nhân: Dạ không ạ.")
    assert "UNSUPPORTED_BOILERPLATE" not in ma(h2, pb(1, "không dị ứng", [1, 2], phu_dinh=True))


# ============================================================ toan ca
def test_mau_thuan_di_ung():
    h = ht("Bệnh nhân: Tôi không dị ứng thuốc.", "Bệnh nhân: Uống amoxicillin lần trước nổi mẩn, dị ứng amoxicillin.")
    kq = chay(h, pb(1, "không dị ứng thuốc", [1], phu_dinh=True), pb(2, "dị ứng amoxicillin", [2]))
    for i in (1, 2):
        assert "INTERNAL_CONTRADICTION" in {c.ma for c in kq["theo_phat_bieu"][i]["tat_ca"]}


def test_dien_bien_khong_mau_thuan():       # am kho
    h = ht("Bệnh nhân: Hôm qua tôi đau đầu, hôm nay hết đau đầu rồi.")
    m = ma(h, pb(1, "đau đầu", [1], moc_thoi_gian="hôm qua"),
           pb(2, "hết đau đầu", [1], phu_dinh=True, moc_thoi_gian="hôm nay"))
    assert "CONTRADICTORY_INFORMATION" not in m


def test_ghi_lap():
    h = ht("Bệnh nhân: Tôi ho.")
    assert "DUPLICATE_INFORMATION" in ma(h, pb(1, "ho", [1]), pb(2, "ho", [1]))


def test_bo_sot_di_ung():
    h = ht("Bác sĩ: Anh bị sao?", "Bệnh nhân: Tôi đau họng, à tôi dị ứng penicillin nhé.")
    kq = chay(h, pb(1, "đau họng", [2], trich_dan=["Tôi đau họng"]))
    assert "OMITTED_ALLERGY" in {c.ma for c in kq["toan_ca"]}


# ============================================================ gop, muc do, chinh sach D
def test_gop_cung_ma_hai_bo_phat_hien():
    # K6 cua khoa (lieu khong thay) va bo so lieu cung ra DOSE_MISMATCH -> mot canh bao
    h = ht("Bệnh nhân: Tôi uống paracetamol 500 mg.")
    p = pb(1, "paracetamol 650 mg", [1], thuoc={"ten": "paracetamol", "lieu": "650 mg"})
    kq = chay(h, p)
    dose = [c for c in kq["theo_phat_bieu"][1]["tat_ca"] if c.ma == "DOSE_MISMATCH"]
    assert len(dose) == 1 and "+" in dose[0].bo_phat_hien


def test_mot_canh_bao_chinh_cho_mot_nguyen_nhan():
    h = ht("Bệnh nhân: Bố tôi bị hen.")
    kq = chay(h, pb(1, "hen", [1], trich_dan=["Bố tôi bị hen"]))
    v = kq["theo_phat_bieu"][1]
    assert v["chinh"].nhom == "SUBJECT_ATTRIBUTION"
    assert all(c.nhom != "SUBJECT_ATTRIBUTION" for c in v["khac"])


def test_muc_do_tach_bat_dinh():
    # cung ma, thong tin di ung -> muc do cao; thong tin khac -> thap hon; bat dinh khong doi
    from src.canh_bao.loai import muc_do
    assert muc_do("SUBJECT_AMBIGUOUS", "di_ung") == CAO
    assert muc_do("SUBJECT_AMBIGUOUS", "khac") == THAP
    assert muc_do("NEGATION_FLIP", "khac") == CAO          # luon cao


def test_thu_nghiem_khong_doi_trang_thai():
    h = ht("Bệnh nhân: Tôi uống thuốc A.", "Bệnh nhân: Sau đó tôi đau bụng.")
    kq = chay(h, pb(1, "đau bụng do uống thuốc A", [2], trich_dan=["Sau đó tôi đau bụng"]))
    v = kq["theo_phat_bieu"][1]
    assert "UNSUPPORTED_CAUSALITY" in {c.ma for c in v["tat_ca"]}
    tn = [c for c in v["tat_ca"] if c.ma == "UNSUPPORTED_CAUSALITY"][0]
    assert not tn.anh_huong_trang_thai


def test_ban_bi_thay_the():
    h = ht("Bệnh nhân: Tôi ho 7 ngày.")
    kq = chay(h, pb(1, "ho 7 ngày", [1], trang_thai="bị thay thế", trich_dan=["Tôi ho 7 ngày"]))
    assert kq["trang_thai_D"][1]["trang_thai"] == gop.BI_THAY_THE


def test_dung_het_la_da_kiem_chung():
    h = ht("Bác sĩ: Anh bị sao?", "Bệnh nhân: Tôi ho 3 ngày nay.")
    kq = chay(h, pb(1, "ho 3 ngày", [2], trich_dan=["Tôi ho 3 ngày nay"], moc_thoi_gian="3 ngày"))
    assert kq["trang_thai_D"][1]["trang_thai"] == gop.DA_KIEM_CHUNG


def test_moi_ma_co_trong_bang():
    kq = chay(ht("Bệnh nhân: Tôi uống amoxicillin 500 mg."), pb(1, "amoxicillin 50 g", [1]))
    for v in kq["theo_phat_bieu"].values():
        for c in v["tat_ca"]:
            assert c.ma in LOAI and c.ly_do


def test_chinh_sach_c_khong_doi():
    from src import cong_rui_ro
    assert cong_rui_ro.CHINH_SACH == "C-2026-09-22"


# ============================================================ chep am
def test_chep_am_chi_khi_co_meta():
    h = ht("Bệnh nhân: Tôi uống amoxicillin 500 mg.")
    p = pb(1, "amoxicillin 500 mg", [1], thuoc={"ten": "amoxicillin", "lieu": "500 mg"})
    assert not {c for c in ma(h, p) if c.startswith("POSSIBLE_") and "TRANSCRIPTION" in c}
    kq = chay(h, p, meta_asr={1: {"asr_confidence": 0.4}})
    c = [c for c in kq["theo_phat_bieu"][1]["tat_ca"] if c.ma == "POSSIBLE_MEDICATION_TRANSCRIPTION_ERROR"]
    assert c and not c[0].anh_huong_trang_thai


# ============================================================ cap tuong phan
@pytest.mark.parametrize("cau_sai, cau_dung, nd, ma_loi, kw", [
    # chi CHU THE thay doi
    ("Bệnh nhân: Bố tôi bị hen.", "Bệnh nhân: Tôi bị hen.", "hen", "SUBJECT_ATTRIBUTION", {}),
    # chi PHU DINH thay doi (qua cap hoi-dap)
    (("Bác sĩ: Anh có đau ngực không?", "Bệnh nhân: Dạ không."),
     ("Bác sĩ: Anh có đau ngực không?", "Bệnh nhân: Dạ có."), "đau ngực", "NEGATION_FLIP", {}),
    # chi DIEU KIEN thay doi
    ("Bác sĩ: Nếu mai còn sốt thì xét nghiệm máu.", "Bác sĩ: Tôi cho xét nghiệm máu, kết quả bình thường.",
     "xét nghiệm máu", "CONDITION_AS_FACT", {"nguoi_noi": "bác sĩ"}),
    # chi THOI GIAN thay doi
    ("Bệnh nhân: Trước đây dùng metformin, giờ bỏ rồi.", "Bệnh nhân: Hiện đang dùng metformin.",
     "đang dùng metformin", "DISCONTINUED_AS_CURRENT",
     {"thuoc": {"ten": "metformin", "trang_thai_dung": "đang dùng"}}),
])
def test_cap_tuong_phan(cau_sai, cau_dung, nd, ma_loi, kw):
    def lay(cau):
        luot = cau if isinstance(cau, tuple) else (cau,)
        dan = list(range(1, len(luot) + 1))
        kq = chay(ht(*luot), pb(1, nd, dan, **kw))
        return kq["theo_phat_bieu"][1]["tat_ca"]
    sai, dung = lay(cau_sai), lay(cau_dung)
    co = (lambda ds: any(c.nhom == ma_loi or c.ma == ma_loi for c in ds))
    assert co(sai), [c.ma for c in sai]
    assert not co(dung), [c.ma for c in dung]


def test_khong_di_ung_thuoc_khong_trai_di_ung_thuc_an():     # am kho (ca asr_010_A)
    h = ht("Người nhà: Cháu dị ứng đạm sữa bò.", "Người nhà: Cháu không dị ứng thuốc.")
    m = ma(h, pb(1, "dị ứng đạm sữa bò", [1]), pb(2, "không dị ứng thuốc", [2], phu_dinh=True))
    assert "INTERNAL_CONTRADICTION" not in m


def test_khong_di_ung_gi_trai_moi_di_ung():
    h = ht("Bệnh nhân: Tôi không dị ứng gì.", "Bệnh nhân: À tôi dị ứng tôm.")
    m = ma(h, pb(1, "không dị ứng gì", [1], phu_dinh=True), pb(2, "dị ứng tôm", [2]))
    assert "INTERNAL_CONTRADICTION" in m


def test_chat_di_ung_chung_chung():                            # am kho
    h = ht("Bệnh nhân: Tôi dị ứng kháng sinh nhóm beta lactam.")
    assert "FABRICATED_ALLERGY" not in ma(h, pb(1, "dị ứng kháng sinh nhóm penicillin", [1]))


# ============================================================ khong doi so do (chinh sach C)
def _mot_ca_bo_dem():
    """Mot ca co trong bo dem khau trich, kem LOI THOAI GOC lay tu bo du lieu (tep dem
    chi co ma ca)."""
    import json
    from src import dich_vu
    loi = dich_vu.Loi(cho_nap_mo_hinh=False)
    if not loi.dem:
        pytest.skip("may nay khong co tep dem khau trich")
    for tep in sorted(dich_vu.THU_MUC_BO.glob("*.jsonl")):
        if tep.name.startswith("ra_"):
            continue
        for dong in open(tep, encoding="utf-8"):
            if dong.strip():
                c = json.loads(dong)
                if c.get("id") in loi.dem and c.get("input"):
                    return loi.dem[c["id"]], [{"id": c["id"], "input": c["input"]}]
    pytest.skip("khong tim thay loi thoai cho ca nao trong bo dem")


def test_chinh_sach_c_ban_nhap_khong_doi_khi_them_lop_canh_bao(monkeypatch):
    """Lop canh bao KHONG duoc doi ban nhap cua chinh sach C — moi con so da bao cao
    dua tren chinh sach C. Chay mot ca tu bo dem hai lan: co lop canh bao, va voi lop
    canh bao bi thay bang ham rong. Ban nhap phai giong het."""
    from src import nhanh
    dem, mau = _mot_ca_bo_dem()
    co = nhanh.chay_trung_gian(mau, None, None, None, "C_khoa", kq_tho=[dem])[0]
    rong = {"phien_ban": "", "chinh_sach": "", "theo_phat_bieu": {}, "toan_ca": [], "trang_thai_D": {},
            "cac_dinh_chinh": []}
    monkeypatch.setattr(gop, "chay", lambda *a, **k: rong)
    khong = nhanh.chay_trung_gian(mau, None, None, None, "C_khoa", kq_tho=[dem])[0]
    assert co["du_doan"] == khong["du_doan"]
    assert co["chinh_sach"] == "C-2026-09-22"
    assert co["canh_bao"]["theo_phat_bieu"]


def test_chinh_sach_d_chi_khi_goi_ro():
    from src import nhanh
    dem, mau = _mot_ca_bo_dem()
    d = nhanh.chay_trung_gian(mau, None, None, None, "C_khoa", kq_tho=[dem], chinh_sach="D")[0]
    assert d["chinh_sach"] == gop.CHINH_SACH_D


# ============================================================ cach noi mo ho (24/09/2026)
def test_cum_mo_ho_DUONG_kem_cau_hoi():
    """'om' o Nam Bo la gay, o Bac la bi benh: ban ghi chep nguyen van van phai bao,
    va ly do phai mang cau hoi lam ro."""
    h = ht("Bác sĩ: Cháu dạo này thế nào?", "Người nhà: Cháu ốm quá, ăn không vô.")
    kq = chay(h, pb(1, "ốm", [2], nguoi_noi="người nhà", trich_dan=["Cháu ốm quá"]))
    c = [x for x in kq["theo_phat_bieu"][1]["tat_ca"] if x.ma == "AMBIGUOUS_LAY_TERM"]
    assert c and "Hỏi lại:" in c[0].ly_do and "gầy" in c[0].ly_do


def test_cum_mo_ho_ghi_ro_nghia_da_tu_chon():
    h = ht("Người nhà: Cháu lên ban đỏ khắp người.")
    kq = chay(h, pb(1, "nghi sởi", [1], nguoi_noi="người nhà", trich_dan=["Cháu lên ban đỏ khắp người"]))
    c = [x for x in kq["theo_phat_bieu"][1]["tat_ca"] if x.ma == "AMBIGUOUS_LAY_TERM"]
    assert c and "đã chọn “sởi”" in c[0].ly_do


def test_cum_mo_ho_AM_loi_bac_si():
    """Bac si noi 'om' thi khong phai cach noi cua nguoi benh."""
    h = ht("Bác sĩ: Cháu có bị ốm lần nào gần đây không?", "Người nhà: Dạ không.")
    assert "AMBIGUOUS_LAY_TERM" not in ma(h, pb(1, "ốm", [1], trich_dan=["Cháu có bị ốm"]))


def test_cum_mo_ho_AM_KHO_trich_dan_noi_cho_khac():
    """Luot co cum mo ho, nhung phat bieu dan phan khac cua luot: khong bao."""
    h = ht("Người nhà: Cháu ốm quá, ho suốt đêm.")
    assert "AMBIGUOUS_LAY_TERM" not in ma(
        h, pb(1, "ho về đêm", [1], nguoi_noi="người nhà", trich_dan=["ho suốt đêm"]))


def test_cum_mo_ho_khong_doi_trang_thai_trieu_chung():
    """Chi hien kem cau hoi; voi trieu chung khong du nang de doi trang thai (chinh sach D)."""
    h = ht("Người nhà: Cháu ốm quá.")
    kq = chay(h, pb(1, "ốm", [1], nguoi_noi="người nhà", trich_dan=["Cháu ốm quá"]))
    c = [x for x in kq["theo_phat_bieu"][1]["tat_ca"] if x.ma == "AMBIGUOUS_LAY_TERM"][0]
    assert not c.anh_huong_trang_thai


def test_cum_mo_ho_khong_the_co_trong_du_lieu_the_he_8():
    """Bo phat hien moi khong duoc doi so lieu the he 8. Khong doc du lieu (tap kiem tra
    cuoi khong duoc mo): bo sinh chi lay chu tu ma nguon `src/`, nen chi can kiem ma
    nguon khong chua cum mo ho nao, tru chinh cac tep cua bo dan gian."""
    import re
    from pathlib import Path

    from src import dan_gian
    goc = Path(__file__).resolve().parents[1] / "src"
    mau = re.compile("|".join(re.escape(m.dan_gian) for m in dan_gian.BANG if m.loai == dan_gian.MO_HO),
                     re.I)
    bo_qua = {"dan_gian.py", "do_dan_gian.py", "phat_hien.py", "loai.py"}
    for p in goc.rglob("*.py"):
        if p.name in bo_qua:
            continue
        van = p.read_text(encoding="utf-8")
        assert not mau.search(van), (p.name, mau.search(van).group(0))


@pytest.mark.parametrize("cau", ["Cháu bị ốm mấy hôm nay rồi.", "Cháu ốm hai hôm rồi.",
                                 "Từ hôm cháu ốm dậy thì ăn kém."])
def test_cum_mo_ho_AM_KHO_om_ro_nghia_benh(cau):
    """'bi om', 'om hai hom', 'om day': o mien Bac chi co nghia bi benh — khong hoi."""
    h = ht(f"Người nhà: {cau}")
    assert "AMBIGUOUS_LAY_TERM" not in ma(h, pb(1, "ốm", [1], nguoi_noi="người nhà", trich_dan=[cau.rstrip(".")]))
