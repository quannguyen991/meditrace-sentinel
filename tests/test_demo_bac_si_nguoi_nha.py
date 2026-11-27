# -*- coding: utf-8 -*-
"""Kịch bản Demo Hoàn chỉnh: Trao đổi Bác sĩ - Người nhà - Bệnh nhân.

Minh chứng kiểm thử theo yêu cầu của Ban Giám Khảo (VẤN ĐỀ 1):
1. Người nhà kể hộ triệu chứng của người bệnh (bệnh nhi / người già).
2. Người nhà nói về tiền sử bệnh / dị ứng của CHÍNH NGƯỜI NHÀ (ví dụ: dị ứng Penicillin).
3. Bệnh nhân tự đính chính thông tin (ví dụ: số ngày sốt, liều thuốc hoặc tần suất quên thuốc).
4. Bản nháp bệnh án có cơ chế truy vết hai chiều (bidirectional citation) và cơ chế cảnh báo/cách ly (Quarantine / Cần xác nhận).
5. Chứng minh bệnh án KHÔNG BAO GIỜ gán dị ứng của người nhà sang cho bệnh nhân, ngay cả khi mô hình AI trích xuất nhầm chu_the_id.
"""

import json
import pytest

from src.duong_ong.b1_cau_truc_menh_de import PhatBieu
from src.duong_ong.b4_kiem_can_cu import khoa_ca, ly_do_chan
from src.duong_ong import b5_xep_cho_cong_rui_ro as cong_rui_ro
from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an
from src.cong_cu_lam_sang.canh_bao_tuong_tac_thuoc import ClinicalPharmacovigilanceEngine as CPE
from src.cong_cu_lam_sang.xuat_fhir_r4 import FHIRExporter
from src.he_thong.dieu_phoi_cac_chot_an_toan import MediTracePipelineOrchestrator


def test_demo_tinh_huong_bac_si_nguoi_nha_benh_nhi():
    """KỊCH BẢN DEMO 1: Bác sĩ khám cho bệnh nhi đi cùng mẹ (Người nhà).
    
    Tình huống lâm sàng:
    - Mẹ kể hộ: Cháu bị sốt ho đờm từ 4 ngày nay.
    - Cháu bé đính chính: Không phải 4 ngày, mới sốt từ chiều hôm qua thôi.
    - Mẹ khai thuốc: Đã cho cháu uống 1 gói Hapacol 250mg.
    - Mẹ khai dị ứng: Bản thân tôi (mẹ) bị dị ứng Penicillin dữ dội, còn cháu thì chưa từng bị dị ứng gì.
    - Bác sĩ chẩn đoán: Viêm phế quản cấp, dự định kê đơn Amoxicillin 500mg.
    """
    hoi_thoai = """
1: Bác sĩ: Chào hai mẹ con, hôm nay bé bị làm sao thế mẹ?
2: Người nhà: Dạ thưa bác sĩ, cháu nó bị sốt cao với ho đờm từ 4 ngày nay, thở khò khè ăn vào là nôn trớ.
3: Bệnh nhân: Dạ không phải 4 ngày đâu ạ, con mới bị sốt nóng từ chiều hôm qua thôi mẹ, mấy hôm trước con chỉ hơi ngứa cổ thôi.
4: Bác sĩ: À vậy là mới sốt từ chiều hôm qua. Mẹ có cho cháu uống thuốc gì ở nhà chưa? Và bé hay mẹ có tiền sử dị ứng thuốc gì không?
5: Người nhà: Dạ em có cho cháu uống một gói Hapacol 250mg hạ sốt. Còn về dị ứng thì bản thân tôi bị dị ứng Penicillin nổi mề đay khó thở dữ dội, còn cháu từ nhỏ đến giờ chưa thấy bị dị ứng thuốc gì cả.
6: Bác sĩ: Con uống gói Hapacol xong có thấy đỡ sốt không? Có thấy nổi mẩn ngứa gì ở đâu không?
7: Bệnh nhân: Dạ con uống xong thì đỡ sốt, người không bị ngứa gì ạ.
8: Bác sĩ: Được rồi, bác khám phổi cháu có ran rít hai bên, họng đỏ. Bác chẩn đoán cháu bị viêm phế quản cấp. Bác sẽ kê đơn thuốc kháng sinh Amoxicillin 500mg cho cháu nhé.
""".strip()

    # Danh sách phát biểu trích xuất với mốc audio millisecond trỏ thẳng về bằng chứng gốc
    ps = [
        # PB 1: Triệu chứng kể hộ (Bệnh nhân)
        PhatBieu(
            id=1, nguoi_noi="người nhà", chu_the_id=0,
            noi_dung="sốt cao ho đờm thở khò khè nôn trớ",
            bang_chung=[2], trich_dan=["cháu nó bị sốt cao với ho đờm"],
            trang_thai="còn hiệu lực",
            audio_spans=[{"start_ms": 3200, "end_ms": 7800, "speaker_id": "CAREGIVER", "exact_quote": "cháu nó bị sốt cao với ho đờm từ 4 ngày nay"}]
        ),
        # PB 2: Thông tin cũ bị đính chính (Sốt 4 ngày) -> Bị thay thế bởi PB 3
        PhatBieu(
            id=2, nguoi_noi="người nhà", chu_the_id=0,
            noi_dung="sốt 4 ngày",
            bang_chung=[2], trich_dan=["sốt cao với ho đờm từ 4 ngày nay"],
            trang_thai="bị thay thế",  # K7 Superseded
            audio_spans=[{"start_ms": 5100, "end_ms": 7800, "speaker_id": "CAREGIVER", "exact_quote": "từ 4 ngày nay"}]
        ),
        # PB 3: Bệnh nhân tự đính chính (Mới sốt từ chiều hôm qua)
        PhatBieu(
            id=3, nguoi_noi="bệnh nhân", chu_the_id=0,
            noi_dung="sốt từ chiều hôm qua",
            bang_chung=[3], trich_dan=["con mới bị sốt nóng từ chiều hôm qua thôi"],
            trang_thai="còn hiệu lực", quan_he="đính chính", quan_he_voi=2,
            audio_spans=[{"start_ms": 8500, "end_ms": 12400, "speaker_id": "PATIENT", "exact_quote": "con mới bị sốt nóng từ chiều hôm qua thôi"}]
        ),
        # PB 4: Dị ứng của CHÍNH NGƯỜI NHÀ (Mẹ) -> chu_the_id = 1
        PhatBieu(
            id=4, nguoi_noi="người nhà", chu_the_id=1,
            noi_dung="dị ứng penicillin nổi mề đay khó thở",
            bang_chung=[5], trich_dan=["bản thân tôi bị dị ứng penicillin nổi mề đay khó thở dữ dội"],
            trang_thai="còn hiệu lực",
            audio_spans=[{"start_ms": 18200, "end_ms": 23500, "speaker_id": "CAREGIVER", "exact_quote": "bản thân tôi bị dị ứng Penicillin nổi mề đay khó thở dữ dội"}]
        ),
        # PB 5: Tình trạng dị ứng của bệnh nhân: Chưa từng bị dị ứng
        PhatBieu(
            id=5, nguoi_noi="người nhà", chu_the_id=0,
            noi_dung="chưa từng thấy bị dị ứng thuốc",
            bang_chung=[5], trich_dan=["cháu từ nhỏ đến giờ chưa thấy bị dị ứng thuốc gì cả"],
            do_chac_chan="chưa ghi nhận", trang_thai="còn hiệu lực",
            audio_spans=[{"start_ms": 23600, "end_ms": 27800, "speaker_id": "CAREGIVER", "exact_quote": "cháu từ nhỏ đến giờ chưa thấy bị dị ứng thuốc gì cả"}]
        ),
        # PB 6: Thuốc đã uống ở nhà: Hapacol 250mg
        PhatBieu(
            id=6, nguoi_noi="người nhà", chu_the_id=0,
            noi_dung="uống một gói Hapacol 250mg",
            bang_chung=[5], trich_dan=["cho cháu uống một gói hapacol 250mg"],
            trang_thai="còn hiệu lực",
            thuoc={"ten": "hapacol", "lieu": "250mg", "duong_dung": "uống", "trang_thai_dung": "đang dùng"},
            audio_spans=[{"start_ms": 15000, "end_ms": 18100, "speaker_id": "CAREGIVER", "exact_quote": "em có cho cháu uống một gói Hapacol 250mg hạ sốt"}]
        ),
        # PB 7: Chẩn đoán của Bác sĩ
        PhatBieu(
            id=7, nguoi_noi="bác sĩ", chu_the_id=0,
            noi_dung="viêm phế quản cấp",
            bang_chung=[8], trich_dan=["chẩn đoán cháu bị viêm phế quản cấp"],
            hanh_vi="nhận định", trang_thai="còn hiệu lực",
            audio_spans=[{"start_ms": 35000, "end_ms": 38500, "speaker_id": "DOCTOR", "exact_quote": "Bác chẩn đoán cháu bị viêm phế quản cấp"}]
        ),
        # PB 8: Kế hoạch điều trị: Bác sĩ kê Amoxicillin 500mg
        PhatBieu(
            id=8, nguoi_noi="bác sĩ", chu_the_id=0,
            noi_dung="amoxicillin 500mg",
            bang_chung=[8], trich_dan=["kê đơn thuốc kháng sinh amoxicillin 500mg"],
            tinh_huong="kế hoạch", hanh_vi="kế hoạch", trang_thai="còn hiệu lực",
            audio_spans=[{"start_ms": 38600, "end_ms": 42500, "speaker_id": "DOCTOR", "exact_quote": "Bác sẽ kê đơn thuốc kháng sinh Amoxicillin 500mg cho cháu nhé"}]
        ),
    ]

    thong_tin_bn = {"id": "BN_NHI_01", "ten": "Bé Nguyễn Văn An", "tuoi": 6, "gioi_tinh": "nam"}

    # 1. Thực thi điều phối toàn trình qua MediTracePipelineOrchestrator
    ket_qua_dieu_phoi = MediTracePipelineOrchestrator.xu_ly_ca_kham(
        ma_ca="ca_demo_nguoi_nha_01",
        hoi_thoai=hoi_thoai,
        danh_sach_phat_bieu=ps,
        thong_tin_benh_nhan=thong_tin_bn
    )

    ban_nhap = ket_qua_dieu_phoi.ban_nhap_3_phan_vung
    audit = ket_qua_dieu_phoi.audit_trail
    fhir = ket_qua_dieu_phoi.fhir_bundle

    # =========================================================================
    # MINH CHỨNG 1: BỆNH ÁN KHÔNG BAO GIỜ GÁN DỊ ỨNG CỦA NGƯỜI NHÀ CHO BỆNH NHÂN
    # =========================================================================
    # Mục DỊ ỨNG của bệnh nhân: Tuyệt đối KHÔNG chứa Penicillin
    assert "penicillin" not in ban_nhap.get("DỊ ỨNG", "").lower()
    
    # Mục TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI: Chứa đúng dị ứng của người nhà (Mẹ)
    assert "penicillin" in ban_nhap.get("TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", "").lower()
    assert "người nhà" in ban_nhap.get("TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", "").lower() or "dị ứng" in ban_nhap.get("TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", "").lower()

    # =========================================================================
    # MINH CHỨNG 2: BỆNH NHÂN TỰ ĐÍNH CHÍNH & CƠ CHẾ CÁCH LY QUARANTINE (K7)
    # =========================================================================
    # Thông tin đính chính (PB 3: sốt từ chiều hôm qua) nằm trong BỆNH SỬ HIỆN TẠI
    assert "hôm qua" in ban_nhap.get("BỆNH SỬ HIỆN TẠI", "").lower()
    # Thông tin cũ (PB 2: sốt 4 ngày) bị loại khỏi BỆNH SỬ HIỆN TẠI
    assert "4 ngày" not in ban_nhap.get("BỆNH SỬ HIỆN TẠI", "").lower()
    # Và bị chuyển xuống phân vùng CẦN XÁC NHẬN (Quarantine)
    assert "CẦN XÁC NHẬN" in ban_nhap
    can_xn = ban_nhap["CẦN XÁC NHẬN"]
    assert "thay thế" in can_xn.lower() or "đính chính" in can_xn.lower() or "bị thay thế" in can_xn.lower()

    # =========================================================================
    # MINH CHỨNG 3: TRUY VẾT HAI CHIỀU (BIDIRECTIONAL CITATIONS) TRONG FHIR R4
    # =========================================================================
    # Kiểm tra Resource FamilyMemberHistory (ghi nhận tiền sử dị ứng của mẹ)
    fmh_list = [e["resource"] for e in fhir["entry"] if e["resource"]["resourceType"] == "FamilyMemberHistory"]
    assert len(fmh_list) >= 1
    assert "penicillin" in fmh_list[0]["note"][0]["text"].lower()

    # Kiểm tra Resource AllergyIntolerance của Bệnh nhân: KHÔNG ĐƯỢC có Penicillin
    allergies = [e["resource"] for e in fhir["entry"] if e["resource"]["resourceType"] == "AllergyIntolerance"]
    for al in allergies:
        assert "penicillin" not in al["code"]["text"].lower()

    # Kiểm tra vết âm thanh audio-timestamp trên Condition / MedicationRequest
    conds = [e["resource"] for e in fhir["entry"] if e["resource"]["resourceType"] == "Condition"]
    assert len(conds) >= 1
    # Condition có extension trích dẫn
    assert "extension" in conds[0]
    ext_data = conds[0]["extension"][0]["extension"]
    sub_map = {item["url"]: item for item in ext_data}
    assert "audio-timestamp-start-ms" in sub_map
    assert "verbatim-quote" in sub_map


def test_adversarial_trap_llm_gan_nham_di_ung_nguoi_nha_cho_benh_nhan():
    """KỊCH BẢN BẪY PHẢN DIỆN (ADVERSARIAL RED-TEAMING):
    
    Giả sử mô hình LLM tầng trích xuất bị ảo giác hoặc nhận diện sai:
    Gán `chu_the_id = 0` (Bệnh nhân) cho phát biểu: "Bản thân tôi bị dị ứng Penicillin nổi mề đay khó thở".
    
    Kiểm chứng Bất biến 2 & 5:
    Tầng 4 (Khóa căn cứ - khoa_bang_chung) BẮT BUỘC phải phát hiện từ xưng 'tôi' trong lời của 'người nhà',
    kích hoạt lệnh CHẶN `CHAN, "chu_the_nguoi_ke"`.
    Hệ thống đẩy phát biểu này sang CẦN XÁC NHẬN (Quarantine),
    TUYỆT ĐỐI KHÔNG cho phép lọt vào mục DỊ ỨNG của bệnh nhân!
    """
    hoi_thoai = """
1: Bác sĩ: Gia đình mình có ai bị dị ứng thuốc không chị?
2: Người nhà: Dạ bản thân tôi bị dị ứng Penicillin nổi mề đay khó thở dữ dội lắm bác sĩ.
""".strip()

    # BẪY: LLM trích xuất cẩu thả, đánh dấu chu_the_id = 0 (Bệnh nhân)
    pb_sai_chu_the = PhatBieu(
        id=99,
        nguoi_noi="người nhà",
        chu_the_id=0,  # <-- LỖI DO LLM GÁN NHẦM BỆNH NHÂN!
        noi_dung="dị ứng penicillin nổi mề đay khó thở",
        bang_chung=[2],
        trich_dan=["bản thân tôi bị dị ứng penicillin nổi mề đay khó thở"],
        trang_thai="còn hiệu lực",
        audio_spans=[{"start_ms": 2000, "end_ms": 5500, "speaker_id": "CAREGIVER", "exact_quote": "bản thân tôi bị dị ứng Penicillin"}]
    )

    # 1. Kiểm tra trực tiếp qua Tầng Khóa Căn Cứ (khoa_bang_chung)
    kq_khoa = khoa_ca([pb_sai_chu_the], hoi_thoai)
    kq_item = kq_khoa["ket_qua"][0]

    # BẮT BUỘC PHẢI BỊ CHẶN (qua = False)
    assert kq_item.qua is False
    assert "chu_the_nguoi_ke" in kq_item.chan
    ly_do = ly_do_chan(kq_khoa["ket_qua"])
    assert 99 in ly_do
    assert "người kể" in ly_do[99]

    # 2. Kiểm tra qua Tầng Cổng Rủi Ro (cong_rui_ro)
    danh_gia_rr = cong_rui_ro.cham([pb_sai_chu_the], kq_khoa["ket_qua"], {"tuoi": 5})
    # Khẳng định tầng cổng rủi ro xếp phát biểu bị vi phạm vào nhóm BI_CHAN
    assert any(d.nhom == cong_rui_ro.BI_CHAN for d in danh_gia_rr if d.id == 99)

    # Quy trình điều phối hạ tầng tổng hợp: gom cảnh báo từ cổng rủi ro và lý do chặn từ khóa căn cứ
    xac_nhan_map = cong_rui_ro.dua_sang_xac_nhan(danh_gia_rr)
    xac_nhan_map.update(ly_do)
    
    # Phát biểu ID 99 bắt buộc phải có trong danh sách CẦN XÁC NHẬN
    assert 99 in xac_nhan_map
    assert "chính người kể" in xac_nhan_map[99]

    # 3. Kiểm tra qua Tầng Sinh Bệnh Án (sinh_benh_an)
    vb_benh_an, _ = sinh_benh_an.sinh([pb_sai_chu_the], ly_do_chan=xac_nhan_map)

    # TUYỆT ĐỐI KHÔNG CÓ TRONG MỤC DỊ ỨNG CỦA BỆNH NHÂN
    # Nếu có mục DỊ ỨNG thì không được chứa Penicillin
    lines = vb_benh_an.split("\n\n")
    for i, line in enumerate(lines):
        if line.strip() == "DỊ ỨNG":
            noi_dung_di_ung = lines[i + 1] if i + 1 < len(lines) else ""
            assert "penicillin" not in noi_dung_di_ung.lower()

    # BẮT BUỘC PHẢI NẰM DƯỚI MỤC "CẦN XÁC NHẬN"
    assert "CẦN XÁC NHẬN" in vb_benh_an
    phan_can_xn = vb_benh_an.split("CẦN XÁC NHẬN")[1]
    assert "người kể" in phan_can_xn or "chính người kể" in phan_can_xn


def test_demo_tinh_huong_nguoi_cao_tuoi_va_con_gai():
    """KỊCH BẢN DEMO 2: Bệnh nhân cao tuổi (Lão khoa) đi khám cùng con gái.
    
    Tình huống lâm sàng:
    - Con gái kể: Bố tôi bị tăng huyết áp, đợt này bố hay quên uống thuốc lắm, cả tuần nay quên suốt.
    - Ông cụ đính chính: Không phải cả tuần đâu con, bố vẫn nhớ uống đều đặn mỗi sáng một viên Amlodipin 5mg, chỉ có đúng hôm kia là bố quên thôi.
    - Con gái khai dị ứng của mình: Còn tôi thì bị dị ứng Aspirin nổi mề đay phù mi mắt.
    """
    hoi_thoai = """
1: Bác sĩ: Chào bác và chị, đợt này huyết áp của bác ở nhà thế nào?
2: Người nhà: Dạ thưa bác sĩ, bố tôi bị tăng huyết áp lâu năm rồi, đợt này bố hay quên uống thuốc lắm, cả tuần nay quên suốt.
3: Bệnh nhân: Không phải cả tuần đâu con, bố vẫn nhớ uống đều đặn mỗi sáng một viên Amlodipin 5mg, chỉ có đúng hôm kia là bố quên thôi.
4: Bác sĩ: Dạ vâng, vậy là bác vẫn duy trì uống Amlodipin 5mg mỗi sáng, chỉ mới quên một hôm thôi. Bác và chị có tiền sử dị ứng thuốc gì không?
5: Người nhà: Dạ bố tôi thì không thấy dị ứng thuốc gì, còn tôi thì bị dị ứng Aspirin nổi mề đay phù mi mắt dữ dội lắm.
6: Bác sĩ: Vâng, tôi ghi nhận bác không có dị ứng thuốc, huyết áp đo tại phòng khám là 135/85 mmHg, tiếp tục duy trì Amlodipin 5mg nhé.
""".strip()

    ps = [
        # PB 1: Bệnh nền Tăng huyết áp (Bệnh nhân)
        PhatBieu(
            id=1, nguoi_noi="người nhà", chu_the_id=0,
            noi_dung="tăng huyết áp lâu năm",
            bang_chung=[2], trich_dan=["bố tôi bị tăng huyết áp lâu năm rồi"],
            trang_thai="còn hiệu lực",
            audio_spans=[{"start_ms": 3000, "end_ms": 6500, "speaker_id": "CAREGIVER", "exact_quote": "bố tôi bị tăng huyết áp lâu năm rồi"}]
        ),
        # PB 2: Con gái khai quên cả tuần -> Bị thay thế bởi đính chính của ông cụ
        PhatBieu(
            id=2, nguoi_noi="người nhà", chu_the_id=0,
            noi_dung="quên uống thuốc cả tuần",
            bang_chung=[2], trich_dan=["cả tuần nay quên suốt"],
            trang_thai="bị thay thế",
            audio_spans=[{"start_ms": 6600, "end_ms": 9500, "speaker_id": "CAREGIVER", "exact_quote": "cả tuần nay quên suốt"}]
        ),
        # PB 3: Ông cụ đính chính: Chỉ quên hôm kia, uống đều mỗi sáng Amlodipin 5mg
        PhatBieu(
            id=3, nguoi_noi="bệnh nhân", chu_the_id=0,
            noi_dung="uống đều đặn mỗi sáng một viên amlodipin 5mg chỉ quên hôm kia",
            bang_chung=[3], trich_dan=["uống đều đặn mỗi sáng một viên amlodipin 5mg, chỉ có đúng hôm kia là bố quên thôi"],
            trang_thai="còn hiệu lực", quan_he="đính chính", quan_he_voi=2,
            thuoc={"ten": "amlodipin", "lieu": "5mg", "duong_dung": "uống", "trang_thai_dung": "đang dùng"},
            audio_spans=[{"start_ms": 10000, "end_ms": 16500, "speaker_id": "PATIENT", "exact_quote": "uống đều đặn mỗi sáng một viên Amlodipin 5mg"}]
        ),
        # PB 4: Dị ứng Aspirin của CON GÁI (Người nhà) -> chu_the_id = 1
        PhatBieu(
            id=4, nguoi_noi="người nhà", chu_the_id=1,
            noi_dung="dị ứng aspirin nổi mề đay phù mi mắt",
            bang_chung=[5], trich_dan=["còn tôi thì bị dị ứng aspirin nổi mề đay phù mi mắt"],
            trang_thai="còn hiệu lực",
            audio_spans=[{"start_ms": 25000, "end_ms": 30500, "speaker_id": "CAREGIVER", "exact_quote": "còn tôi thì bị dị ứng Aspirin nổi mề đay phù mi mắt"}]
        ),
        # PB 5: Bác sĩ đo huyết áp
        PhatBieu(
            id=5, nguoi_noi="bác sĩ", chu_the_id=0,
            noi_dung="huyết áp 135/85",
            bang_chung=[6], trich_dan=["huyết áp đo tại phòng khám là 135/85"],
            hanh_vi="quan sát", trang_thai="còn hiệu lực",
            audio_spans=[{"start_ms": 32000, "end_ms": 36000, "speaker_id": "DOCTOR", "exact_quote": "huyết áp đo tại phòng khám là 135/85 mmHg"}]
        )
    ]

    thong_tin_bn = {"id": "BN_LAO_KHOA_02", "ten": "Bác Trần Văn Bình", "tuoi": 74, "gioi_tinh": "nam"}

    ket_qua = MediTracePipelineOrchestrator.xu_ly_ca_kham(
        ma_ca="ca_demo_lao_khoa_02",
        hoi_thoai=hoi_thoai,
        danh_sach_phat_bieu=ps,
        thong_tin_benh_nhan=thong_tin_bn
    )

    ban_nhap = ket_qua.ban_nhap_3_phan_vung
    fhir = ket_qua.fhir_bundle

    # 1. Bệnh án của ông cụ: DỊ ỨNG không chứa Aspirin
    assert "aspirin" not in ban_nhap.get("DỊ ỨNG", "").lower()

    # 2. Tiền sử gia đình: Chứa dị ứng Aspirin của con gái
    assert "aspirin" in ban_nhap.get("TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI", "").lower()

    # 3. Đính chính: Thông tin "quên cả tuần" bị chuyển xuống CẦN XÁC NHẬN
    assert "CẦN XÁC NHẬN" in ban_nhap
    assert "thay thế" in ban_nhap["CẦN XÁC NHẬN"].lower()

    # 4. FHIR Bundle:
    # Không có AllergyIntolerance cho ông cụ
    allergies = [e["resource"] for e in fhir["entry"] if e["resource"]["resourceType"] == "AllergyIntolerance"]
    for al in allergies:
        assert "aspirin" not in al["code"]["text"].lower()

    # FamilyMemberHistory chứa dị ứng của con gái
    fmh_list = [e["resource"] for e in fhir["entry"] if e["resource"]["resourceType"] == "FamilyMemberHistory"]
    assert len(fmh_list) >= 1
    assert "aspirin" in fmh_list[0]["note"][0]["text"].lower()
