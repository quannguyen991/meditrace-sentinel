# -*- coding: utf-8 -*-
"""Test suite cho Trụ cột 1: Động cơ Dược lý Lâm sàng trong src/duoc_ly_lam_sang.py."""
import pytest
from src.duoc_ly_lam_sang import (
    ClinicalPharmacovigilanceEngine,
    ClinicalPharmacovigilanceEngine as CPE,
    DDI_CHONG_CHI_DINH,
    DDI_NGHIEM_TRONG
)
from src.aho_corasick_duoc_thu import (
    BoTraCuuDuocThuAhoCorasick,
    PurePythonAhoCorasick
)


def test_phat_hien_tuong_tac_nguy_hiem_warfarin_aspirin():
    thuoc = ["viên warfarin 2mg", "aspirin 81mg"]
    ddi = CPE.kiem_tra_tuong_tac(thuoc)
    assert len(ddi) >= 1
    assert any(d.thuoc_1 == "warfarin" and d.thuoc_2 == "aspirin" for d in ddi)
    assert ddi[0].muc_do == DDI_CHONG_CHI_DINH


def test_phat_hien_tuong_tac_clopidogrel_omeprazole():
    thuoc = ["clopidogrel 75mg", "omeprazole 20mg"]
    ddi = CPE.kiem_tra_tuong_tac(thuoc)
    assert any("clopidogrel" in d.thuoc_1 or "clopidogrel" in d.thuoc_2 for d in ddi)
    assert any("CYP2C19" in d.co_che for d in ddi)


def test_chong_chi_dinh_nsaid_khi_suy_than_nang():
    co_dia = {"egfr": 22, "tuoi": 72}
    thuoc = ["ibuprofen 400mg", "paracetamol 500mg"]
    cd = CPE.kiem_tra_co_dia_chong_chi_dinh(thuoc, co_dia)
    assert any("ibuprofen" in c and "suy thận" in c for c in cd)


def test_chong_chi_dinh_acei_trong_thai_ky():
    co_dia = {"mang_thai": True, "tuan_thai": 14}
    thuoc = ["captopril 25mg", "vitamin C"]
    cd = CPE.kiem_tra_co_dia_chong_chi_dinh(thuoc, co_dia)
    assert any("captopril" in c and "quái thai" in c for c in cd)


def test_chong_chi_dinh_propranolol_o_benh_nhan_hen():
    co_dia = {"tien_su_benh": ["hen phế quản", "viêm mũi dị ứng"]}
    thuoc = ["propranolol 40mg", "salbutamol xịt"]
    cd = CPE.kiem_tra_co_dia_chong_chi_dinh(thuoc, co_dia)
    assert any("propranolol" in c and "co thắt phế quản" in c for c in cd)


def test_phat_hien_vuot_lieu_tran_paracetamol():
    # Paracetamol liều trần là 4000mg/ngày
    err = CPE.kiem_tra_lieu_tran("panadol extra", 5000.0)
    assert err is not None
    assert "VƯỢT LIỀU TRẦN" in err

    # Liều an toàn 2000mg/ngày
    assert CPE.kiem_tra_lieu_tran("paracetamol", 2000.0) is None


def test_kiem_duyet_toan_dien_tong_hop():
    co_dia = {"mang_thai": True, "egfr": 50}
    thuoc = ["warfarin 5mg", "aspirin 81mg"]
    chi_tiet_lieu = {"paracetamol": 6000.0}

    ket_qua = CPE.kiem_duyet_toan_dien(thuoc, co_dia, chi_tiet_lieu)
    assert not ket_qua.hop_le
    assert len(ket_qua.canh_bao_ddi) > 0
    assert len(ket_qua.chong_chi_dinh_co_dia) > 0
    assert len(ket_qua.vuot_lieu_tran) > 0
    assert len(ket_qua.giai_trinh_duoc_ly) >= 3


def test_pure_python_aho_corasick_co_ban():
    """Kiểm tra hoạt động máy trạng thái hữu hạn Aho-Corasick thuần Python."""
    from src.aho_corasick_duoc_thu import PurePythonAhoCorasick

    ac = PurePythonAhoCorasick()
    ac.them_tu_khoa("paracetamol", {"id": 1})
    ac.them_tu_khoa("aspirin", {"id": 2})
    ac.them_tu_khoa("ibuprofen", {"id": 3})
    ac.xay_dung()

    van_ban = "Bác sĩ kê đơn paracetamol và aspirin hạ sốt."
    ket_qua = ac.tim_kiem(van_ban)
    
    assert len(ket_qua) == 2
    tu_khoa_tim = [k["tu_khoa"] for k in ket_qua]
    assert "paracetamol" in tu_khoa_tim
    assert "aspirin" in tu_khoa_tim


def test_aho_corasick_word_boundary_guard():
    """Kiểm tra Word Boundary Guard: không bắt nhầm chuỗi con vô nghĩa bên trong từ."""
    from src.aho_corasick_duoc_thu import PurePythonAhoCorasick

    ac = PurePythonAhoCorasick()
    ac.them_tu_khoa("tin", {"id": "statin_hoac_khac"})
    ac.them_tu_khoa("am", {"id": "khac"})
    ac.xay_dung()

    # 'tin' nằm bên trong 'vitamin', 'am' nằm bên trong 'khám' (không có dấu cách phân tách)
    van_ban = "Bệnh nhân đến phòng khám để uống vitamin tăng lực."
    ket_qua = ac.tim_kiem(van_ban, kiem_tra_bien_tu=True)
    # Không được bắt nhầm 'tin' trong 'vitamin' hay 'am' trong 'khám'
    assert len(ket_qua) == 0

    # Nếu xuất hiện từ độc lập
    van_ban_dung = "Thuốc có dạng viên uống tin."
    ket_qua_dung = ac.tim_kiem(van_ban_dung, kiem_tra_bien_tu=True)
    assert len(ket_qua_dung) == 1


def test_nhan_dien_biet_duoc_duoc_thu_2022():
    """Aho-Corasick tự động ánh xạ từ biệt dược sang hoạt chất chuẩn Dược thư Quốc gia Việt Nam 2022."""
    cpe = CPE.lay_bo_tra_cuu_aho()
    van_ban = "Kê cho bệnh nhân Panadol 500mg và Plavix 75mg."
    
    thuoc = cpe.nhan_dien_thuoc_trong_van_ban(van_ban)
    hoat_chat = [t["hoat_chat"] for t in thuoc]
    
    assert "paracetamol" in hoat_chat  # Panadol -> Paracetamol
    assert "clopidogrel" in hoat_chat  # Plavix -> Clopidogrel


def test_aho_corasick_tuong_tac_biet_duoc():
    """Kiểm tra phát hiện tương tác nguy cơ cao khi đầu vào là tên biệt dược."""
    cpe = CPE.lay_bo_tra_cuu_aho()
    
    # Plavix (Clopidogrel) + Losec (Omeprazole) -> Tương tác ức chế men CYP2C19
    canh_bao = cpe.kiem_tra_tuong_tac(["viên Plavix 75mg uống sáng", "Losec 20mg trước ăn"])
    assert len(canh_bao) >= 1
    assert any(c["thuoc_1"] == "clopidogrel" or c["thuoc_2"] == "clopidogrel" for c in canh_bao)


def test_chuan_hoa_thuoc_hop_chat_gach_noi():
    """Kiểm tra nhận diện thuốc hợp chất chứa dấu gạch nối (-) như co-amoxiclav, co-trimoxazole."""
    cpe = CPE.lay_bo_tra_cuu_aho()

    # Dạng gạch nối chuẩn và có khoảng trắng
    van_ban = "Bác sĩ cho uống co-amoxiclav 1g ngày 2 lần và co - trimoxazole khi sốt."
    thuoc = cpe.nhan_dien_thuoc_trong_van_ban(van_ban)
    hoat_chat = [t["hoat_chat"] for t in thuoc]

    assert "co-amoxiclav" in hoat_chat
    assert "co-trimoxazole" in hoat_chat


def test_nhan_dien_thuoc_18_he_co_quan_aho_corasick():
    """Kiểm tra máy tra cứu Aho-Corasick nhận diện đầy đủ các thuốc thuộc 18 hệ cơ quan."""
    bo_tra_cuu = BoTraCuuDuocThuAhoCorasick()
    
    # Đoạn văn bản lâm sàng đa chuyên khoa
    van_ban = (
        "Bệnh nhân dùng zyloric 300mg điều trị gout mạn, uống thêm depakine 500mg ngừa động kinh. "
        "Ngoài ra đang duy trì lanoxin 0.125mg do rung nhĩ và imuran 50mg cho bệnh viêm ruột Crohn. "
        "Kê thêm thuốc hạ áp aldomet và thuốc mỡ lipitor."
    )
    ket_qua = bo_tra_cuu.nhan_dien_thuoc_trong_van_ban(van_ban)
    hoat_chat = {m["hoat_chat"] for m in ket_qua}

    assert "allopurinol" in hoat_chat    # từ zyloric
    assert "valproat" in hoat_chat       # từ depakine
    assert "digoxin" in hoat_chat        # từ lanoxin
    assert "azathioprine" in hoat_chat   # từ imuran
    assert "methyldopa" in hoat_chat     # từ aldomet
    assert "atorvastatin" in hoat_chat   # từ lipitor


def test_tuong_tac_chong_chi_dinh_moi_allopurinol_azathioprine():
    """Kiểm tra chống chỉ định chết người: Allopurinol + Azathioprine (độc tủy xương)."""
    ddi = ClinicalPharmacovigilanceEngine.kiem_tra_tuong_tac(["allopurinol", "azathioprine"])
    assert len(ddi) == 1
    assert ddi[0].muc_do == DDI_CHONG_CHI_DINH
    assert "tủy xương" in ddi[0].hau_qua.lower() or "tử vong" in ddi[0].hau_qua.lower()


def test_tuong_tac_chong_chi_dinh_colchicine_clarithromycin():
    """Kiểm tra chống chỉ định tử vong: Colchicine + Clarithromycin (ngộ độc tích lũy)."""
    ddi = ClinicalPharmacovigilanceEngine.kiem_tra_tuong_tac(["colchicine", "clarithromycin"])
    assert len(ddi) == 1
    assert ddi[0].muc_do == DDI_CHONG_CHI_DINH
    assert "colchicine" in ddi[0].hau_qua.lower()


def test_tuong_tac_chong_chi_dinh_methotrexate_nsaid():
    """Kiểm tra tương tác nghiêm trọng: Methotrexate + NSAID (Ibuprofen/Aspirin)."""
    ddi = ClinicalPharmacovigilanceEngine.kiem_tra_tuong_tac(["methotrexate", "ibuprofen"])
    assert len(ddi) == 1
    assert ddi[0].muc_do == DDI_CHONG_CHI_DINH

    ddi_asp = ClinicalPharmacovigilanceEngine.kiem_tra_tuong_tac(["methotrexate", "aspirin"])
    assert len(ddi_asp) == 1
    assert ddi_asp[0].muc_do == DDI_CHONG_CHI_DINH


def test_kiem_soat_lieu_tran_thuoc_moi():
    """Kiểm tra phát hiện vượt liều trần Colchicine và Allopurinol."""
    assert ClinicalPharmacovigilanceEngine.kiem_tra_lieu_tran("colchicine", 4.0) is not None  # trần 3mg -> cảnh báo
    assert ClinicalPharmacovigilanceEngine.kiem_tra_lieu_tran("colchicine", 1.0) is None      # hợp lệ

    assert ClinicalPharmacovigilanceEngine.kiem_tra_lieu_tran("allopurinol", 900.0) is not None  # trần 800mg -> cảnh báo
    assert ClinicalPharmacovigilanceEngine.kiem_tra_lieu_tran("allopurinol", 300.0) is None      # hợp lệ

    assert ClinicalPharmacovigilanceEngine.kiem_tra_lieu_tran("digoxin", 0.5) is not None      # trần 0.25mg -> cảnh báo
    assert ClinicalPharmacovigilanceEngine.kiem_tra_lieu_tran("digoxin", 0.125) is None        # hợp lệ



