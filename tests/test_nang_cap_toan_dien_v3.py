# -*- coding: utf-8 -*-
"""Bộ kiểm thử toàn diện cho Gói Nâng cấp v3 (Deep Research & Code-Level Fixes):
1. Vá lỗi gộp nhầm 'bố em' vào người bệnh & Liên kết mở rộng Bệnh/Xét nghiệm (`src/thuc_the.py`).
2. Vá lỗi lệch phân phối Train-Inference & Giải mã 2 tầng (`src/bakeoff.py`).
3. Đính chính có đồng thuận chéo giữa người nhà và bệnh nhân (`src/cap_nhat.py`).
4. Chuẩn hóa số viết bằng chữ & phân số tiếng Việt cho Khóa K6 (`src/khoa_bang_chung.py`).
5. Khử định danh tên riêng sau danh xưng tiếng Việt (`src/khu_dinh_danh.py`).
6. Tầng 4.5 Khôi phục bỏ sót chủ động, Cổng Tiền kiểm BHYT XML 130/4750 & ICD-10,
   Liều Nhi khoa mg/kg, Đa thuốc Đông-Tây y, Thước đo CHWER & Truy ngược lỗi đa vòng
   (`src/kiem_duyet_bhyt_va_bo_sot.py` & `src/dich_vu.py`).
"""
import pytest

from src import bakeoff, cap_nhat, dich_vu, khoa_bang_chung, thuc_the
from src.khu_dinh_danh import ClinicalDeidentifier
from src.kiem_duyet_bhyt_va_bo_sot import (
    ActiveOmissionRecoveryEngine,
    BHYTXmlPreChecker,
    ClinicalHarmWeightedEvaluator,
)
from src.phat_bieu import PhatBieu


# ---------------------------------------------------------------------------
# 1. TEST VÁ LỖI "BỐ EM" & LIÊN KẾT THỰC THỂ MỞ RỘNG (`src/thuc_the.py`)
# ---------------------------------------------------------------------------
def test_bo_em_tien_su_gia_dinh_KHONG_gop_nham_vao_benh_nhan():
    """Kịch bản thực tế nêu trong README.md (dòng 60-67 & 156):
    Bác sĩ gọi bệnh nhân là 'Cô' (nữ), người nhà nói 'Bố em bị hen, không biết có liên quan không'.
    'bố em' bắt buộc phải tách thành thực thể riêng, không được gộp vào bệnh nhân (id=0).
    """
    ht = (
        "Bác sĩ: Cô có dị ứng thuốc gì không ạ?\n"
        "Bệnh nhân: Tôi uống amoxicillin là nổi mẩn toàn thân.\n"
        "Người nhà: Bố em bị hen từ nhỏ, không biết có liên quan không bác sĩ.\n"
        "Bệnh nhân: Tôi ho mười ngày rồi."
    )
    ds = thuc_the.lien_ket(ht)
    bn = [t for t in ds if t.id == 0][0]
    assert "bố em" not in bn.cach_goi, "Lỗi gộp nhầm 'bố em' (tiền sử gia đình) vào bệnh nhân!"
    bo_em = [t for t in ds if t.ten_chuan == "bố em"]
    assert len(bo_em) == 1 and bo_em[0].id != 0


def test_lien_ket_mo_rong_gom_dong_nghia_benh_va_xet_nghiem():
    ht = (
        "Bệnh nhân: Tôi bị đau vùng thượng vị 3 hôm nay.\n"
        "Bệnh nhân: Chỗ đau bao tử đó rát lắm, tôi đã đi chụp phim phổi và xét nghiệm máu rồi."
    )
    # Mặc định giữ tương thích ngược
    ds_mac_dinh = thuc_the.lien_ket(ht)
    assert not any(t.loai in ("bệnh", "xét nghiệm") for t in ds_mac_dinh)

    # Bật liên kết mở rộng
    ds_mo_rong = thuc_the.lien_ket_mo_rong(ht)
    benh = [t for t in ds_mo_rong if t.loai == "bệnh" and t.ten_chuan == "đau thượng vị"]
    assert len(benh) == 1
    assert benh[0].luot_thoai == [1, 2]
    xn = [t for t in ds_mo_rong if t.loai == "xét nghiệm"]
    assert {t.ten_chuan for t in xn} >= {"chụp x-quang", "xét nghiệm máu"}


# ---------------------------------------------------------------------------
# 2. TEST KHỚP PHÂN PHỐI TRAIN-INFERENCE & GIẢI MÃ 2 TẦNG (`src/bakeoff.py`)
# ---------------------------------------------------------------------------
def test_bakeoff_khop_prompt_khi_co_adapter(monkeypatch):
    from tests.test_bakeoff import _cai_torch_gia, _InpGia

    _cai_torch_gia(monkeypatch)
    da_nhan_msgs = []

    class TokTest:
        eos_token_id = 0

        def apply_chat_template(self, msgs, **kw):
            da_nhan_msgs.append(msgs)
            return msgs[-1]["content"]

        def __call__(self, s, return_tensors=None):
            return _InpGia()

        def decode(self, ids, skip_special_tokens=True):
            return '{"phat_bieu": [{"chu_the": "bệnh nhân", "noi_dung": "ho", "do_chac_chan": "chắc chắn", "luot_thoai": [1]}]}'

    class ModelCoAdapter:
        device = "cpu"
        _co_adapter_trich = True
        so_lan_ep = 0

        def generate(self, **kw):
            if kw.get("prefix_allowed_tokens_fn") is not None:
                ModelCoAdapter.so_lan_ep += 1
            return [[0, 1]]

    mau = [{"id": "ca_1", "input": "1. Bệnh nhân: Tôi ho 3 ngày."}]
    kq = bakeoff.trich(TokTest(), ModelCoAdapter(), prefix_fn=lambda *a: [0], mau_list=mau)
    assert len(kq) == 1 and kq[0]["json_hop_le"] is True
    # Phải có system prompt LOI_NHAC_HE_THONG_TRICH và KHÔNG nhồi 5 ví dụ mẫu VI_DU
    assert da_nhan_msgs[0][0]["role"] == "system"
    assert "Ví dụ 1" not in da_nhan_msgs[0][1]["content"]
    # Giải mã 2 tầng: JSON đã hợp lệ ngay lần đầu nên không tốn CPU chạy prefix_fn
    assert ModelCoAdapter.so_lan_ep == 0


# ---------------------------------------------------------------------------
# 3. TEST ĐÍNH CHÍNH ĐỒNG THUẬN CHÉO (`src/cap_nhat.py`)
# ---------------------------------------------------------------------------
def test_dinh_chinh_cheo_duoc_chap_nhan_khi_benh_nhan_xac_nhan_ngay_luot_sau():
    ht = (
        "1. Bệnh nhân: Tôi uống thuốc huyết áp ngày 3 viên.\n"
        "2. Người nhà: Đâu có mẹ, mẹ uống ngày có 1 viên buổi sáng thôi.\n"
        "3. Bệnh nhân: À ừ nhỉ, đúng rồi, tôi nhớ nhầm, ngày 1 viên."
    )
    ps = [
        PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="uống thuốc huyết áp 3 viên", bang_chung=[1]),
        PhatBieu(id=1, nguoi_noi="người nhà", chu_the_id=0, noi_dung="uống thuốc huyết áp 1 viên",
                 bang_chung=[2], quan_he="đính chính", quan_he_voi=0),
    ]
    # Nếu có hội thoại xác nhận ở lượt 3 -> chấp nhận đính chính
    ra = cap_nhat.ap_luat(ps, hoi_thoai=ht)
    assert ra[0].trang_thai == "bị thay thế"
    assert ra[1].trang_thai == "còn hiệu lực"


# ---------------------------------------------------------------------------
# 4. TEST CHUẨN HÓA SỐ VIẾT BẰNG CHỮ & PHÂN SỐ Ở KHÓA K6 (`src/khoa_bang_chung.py`)
# ---------------------------------------------------------------------------
def test_khoa_k6_chap_nhan_so_viet_bang_chu_va_phan_so_nhung_chan_sai_so():
    ht = "1. Bệnh nhân: Sáng nào tôi cũng uống nửa viên Amlodipin năm mi li gam và một viên rưỡi Metformin 500mg."
    p_dung_1 = PhatBieu(
        id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="uống Amlodipin 0.5 viên",
        bang_chung=[1], trich_dan=["uống nửa viên Amlodipin"],
        thuoc={"ten": "Amlodipin", "lieu": "0.5 viên", "duong_dung": "uống"}
    )
    p_dung_2 = PhatBieu(
        id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="uống Metformin 500 mg",
        bang_chung=[1], trich_dan=["một viên rưỡi Metformin 500mg"],
        thuoc={"ten": "Metformin", "lieu": "500 mg", "duong_dung": "uống"}
    )
    p_sai_lieu_10x = PhatBieu(
        id=2, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="uống Metformin 50 mg",
        bang_chung=[1], trich_dan=["một viên rưỡi Metformin 500mg"],
        thuoc={"ten": "Metformin", "lieu": "50 mg", "duong_dung": "uống"}
    )

    kk = khoa_bang_chung.khoa_ca([p_dung_1, p_dung_2, p_sai_lieu_10x], ht)
    kq = {k.id: k for k in kk["ket_qua"]}
    assert "lieu_khong_thay" not in kq[0].chan, "Phải hiểu 'nửa viên' == '0.5 viên'"
    assert "lieu_khong_thay" not in kq[1].chan, "Phải hiểu '500mg' == '500 mg'"
    assert "lieu_khong_thay" in kq[2].chan, "Phải chặn nghiêm ngặt '50 mg' khi gốc là '500mg'!"


# ---------------------------------------------------------------------------
# 5. TEST KHỬ ĐỊNH DANH HỌ TÊN SAU DANH XƯNG (`src/khu_dinh_danh.py`)
# ---------------------------------------------------------------------------
def test_khu_dinh_danh_bat_ten_rieng_sau_danh_xung_khong_can_tien_to_ten_la():
    vb = "Bác sĩ: Chào bác Nguyễn Văn An, mời chị Trần Thị Bích ngồi chờ đo huyết áp."
    kq = ClinicalDeidentifier.an_danh_van_ban(vb)
    assert "Nguyễn Văn An" not in kq.van_ban_da_an_danh
    assert "Trần Thị Bích" not in kq.van_ban_da_an_danh
    assert "[HO_TEN_1]" in kq.van_ban_da_an_danh
    assert "[HO_TEN_2]" in kq.van_ban_da_an_danh
    phuc_hoi = ClinicalDeidentifier.giai_ma_van_ban(kq.van_ban_da_an_danh, kq.bang_anh_xa_giai_ma)
    assert phuc_hoi == vb


# ---------------------------------------------------------------------------
# 6. TEST TẦNG 4.5 KHÔI PHỤC BỎ SÓT, TIỀN KIỂM BHYT XML 130/4750 & CHWER
# ---------------------------------------------------------------------------
def test_tang_45_khoi_phuc_bo_sot_tu_doan_chua_ghi():
    ht = (
        "1. Bác sĩ: Bác đau ở đâu ạ?\n"
        "2. Bệnh nhân: Tôi đau thượng vị 3 ngày nay.\n"
        "3. Bệnh nhân: Tôi bị dị ứng Penicillin nặng lắm và ở nhà đang uống thêm thuốc tễ trị đau khớp.\n"
        "4. Bệnh nhân: Tôi không sốt, không khó thở gì cả."
    )
    # Giả sử LLM Tầng 1 chỉ trích được lượt 2 mà bỏ sót lượt 3 và lượt 4
    ps = [
        PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="đau thượng vị",
                 bang_chung=[2], trich_dan=["Tôi đau thượng vị 3 ngày nay"])
    ]
    khoi_phuc = ActiveOmissionRecoveryEngine.quet_khoi_phuc(ps, ht)
    loai = {x.loai_thong_tin for x in khoi_phuc}
    assert "di_ung" in loai, "Tầng 4.5 phải khôi phục được dị ứng bị bỏ sót ở lượt 3!"
    assert "trieu_chung_am_tinh" in loai, "Tầng 4.5 phải khôi phục được triệu chứng âm tính ở lượt 4!"


def test_tien_kiem_bhyt_icd10_canh_bao_xuat_toan_va_lieu_nhi_khoa():
    ht = (
        "1. Bác sĩ: Cháu bé nặng 10 kg, hôm nay khám vì đau họng, viêm họng cấp.\n"
        "2. Bác sĩ: Tôi kê Omeprazol 20mg và Hapacol 800mg kèm Tiffy và Panadol."
    )
    ps = [
        PhatBieu(id=0, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="viêm họng cấp",
                 bang_chung=[1], trich_dan=["viêm họng cấp"], hanh_vi="nhận định"),
        PhatBieu(id=1, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="kê Omeprazol 20mg",
                 bang_chung=[2], trich_dan=["kê Omeprazol 20mg"], tinh_huong="kế hoạch",
                 thuoc={"ten": "omeprazol", "lieu": "20mg", "duong_dung": "uống"}),
        PhatBieu(id=2, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="uống Hapacol 800mg",
                 bang_chung=[2], trich_dan=["Hapacol 800mg"], tinh_huong="kế hoạch",
                 thuoc={"ten": "hapacol", "lieu": "800mg", "duong_dung": "uống"}),
    ]
    kq = BHYTXmlPreChecker.kiem_duyet_ho_so("CA_BHYT_01", ps, ht)
    assert kq.ma_icd10_chinh and kq.ma_icd10_chinh["ma_icd10"] == "J02.9"
    # Kê Omeprazol nhưng chỉ có chẩn đoán J02.9 (Viêm họng) -> Cảnh báo xuất toán BHYT
    assert any("Omeprazol" in c and "4750/QĐ-BYT" in c for c in kq.canh_bao_xuat_toan_bhyt)
    # Trẻ 10kg uống 800mg Hapacol = 80 mg/kg (>60 mg/kg/ngày) -> Cảnh báo quá liều Nhi khoa
    assert any("80.0 mg/kg" in c or "80 mg/kg" in c for c in kq.canh_bao_lieu_nhi_khoa)
    # Trùng lặp Paracetamol (Hapacol + Tiffy + Panadol)
    assert any("PARACETAMOL" in c for c in kq.canh_bao_da_thuoc_dong_tay_y)


def test_chwer_va_quy_ket_nguoc_tang_loi():
    dap_an = [
        PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng penicillin", bang_chung=[1]),
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="mệt mỏi nhẹ", bang_chung=[2]),
    ]
    # Mô hình bỏ sót dị ứng (w=1.0) nặng hơn bỏ sót triệu chứng nhẹ (w=0.3)
    du_doan_sot_di_ung = [dap_an[1]]
    du_doan_sot_met_moi = [dap_an[0]]

    diem_1 = ClinicalHarmWeightedEvaluator.tinh_chwer(du_doan_sot_di_ung, dap_an)
    diem_2 = ClinicalHarmWeightedEvaluator.tinh_chwer(du_doan_sot_met_moi, dap_an)
    assert diem_1["ser_khong_trong_so"] == diem_2["ser_khong_trong_so"] == 0.5
    assert diem_1["chwer"] > diem_2["chwer"], "CHWER phải phạt nặng lỗi bỏ sót dị ứng hơn lỗi bỏ sót triệu chứng phụ!"

    qk = ClinicalHarmWeightedEvaluator.quy_ket_nguoc_tang_loi(
        "doi_chu_the", {"subject": "bệnh nhân"}, {"subject": "bố bệnh nhân"}
    )
    assert qk["ma_tang"] == "STAGE_2_ENTITY_ATTRIBUTION"


def test_dich_vu_tich_hop_lam_sang_nang_cao_va_kiem_ma_phien():
    with pytest.raises(dich_vu.LoiDichVu) as e:
        dich_vu.May._kiem_ma_phien("../etc/passwd")
    assert e.value.code == 400

    ban_ghi = {
        "id": "ca_test_tich_hop",
        "input": "1. Bác sĩ: Bác bị tăng huyết áp, tôi kê Amlodipin 5mg.\n2. Bệnh nhân: Tôi dị ứng Penicillin.",
        "phat_bieu": [
            PhatBieu(id=0, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="tăng huyết áp",
                     bang_chung=[1], trich_dan=["tăng huyết áp"], hanh_vi="nhận định").to_dict(),
            PhatBieu(id=1, nguoi_noi="bác sĩ", chu_the_id=0, noi_dung="uống Amlodipin 5mg",
                     bang_chung=[1], trich_dan=["Amlodipin 5mg"],
                     thuoc={"ten": "amlodipin", "lieu": "5mg", "duong_dung": "uống"}).to_dict(),
        ],
    }
    ra = dich_vu._them_canh_bao(ban_ghi)
    assert "lam_sang_nang_cao" in ra
    ls = ra["lam_sang_nang_cao"]
    assert ls["bhyt_icd10"]["ma_icd10_chinh"]["ma_icd10"] == "I10"
    # Lượt 2 có 'dị ứng Penicillin' chưa nằm trong phat_bieu -> Tầng 4.5 phải khôi phục được!
    assert any(x["loai_thong_tin"] == "di_ung" for x in ls["khoi_phuc_bo_sot_tang_45"])
    assert ls["audit_trail_worm"]["chu_ky_bam_sha256"]
    assert ls["ban_dan_do_benh_nhan"] is not None
    assert ls["fhir_bundle"]["resourceType"] == "Bundle"


def test_kiem_thu_dot_bien_lam_sang_bat_giu_100_phan_tram():
    from src.kiem_thu_dot_bien import ClinicalMutationTester

    kq = ClinicalMutationTester.chay_kiem_thu_dot_bien()
    assert kq["tong_so_ho_dot_bien"] == 5
    assert kq["ty_le_bat_giu_tong_the"] == 1.0, f"Phải bắt giữ 100% cả 5 họ đột biến: {kq}"

