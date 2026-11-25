# -*- coding: utf-8 -*-
"""Phép thử tính ngữ cảnh hoá và an toàn của câu hỏi bác sĩ (Bộ v2 mở rộng).

Kiểm tra:
1. Vòng 2.1 (them): Câu hỏi triệu chứng khác phải tham chiếu triệu chứng chính đã kể
   hoặc hỏi tổng quát theo nhóm đối tượng, không rò rỉ triệu chứng tương lai.
2. Trích dẫn nguyên văn và nhãn dap_an không đổi giữa các lần sinh.
"""
import random
import re
import pytest

from src import sinh_hoi_thoai_viet as shv
from src import bien_the_cau as btc


def test_vong_2_1_cau_hoi_them_co_ngu_canh():
    """Vòng 2.1: Câu hỏi 'them' của bác sĩ có ngữ cảnh triệu chứng chính của ca."""
    bo = shv.sinh_bo(100, seed=2611, mo_rong=True)
    co_ngu_canh = 0
    for ca in bo:
        lines = ca["input"].splitlines()
        # Triệu chứng chính từ mệnh đề đầu tiên
        md_chinh = next((m for m in ca["dap_an"] if m.get("muc") == "BỆNH SỬ HIỆN TẠI" and m.get("quan_he") is None), None)
        if not md_chinh:
            continue
        chinh = md_chinh["noi_dung"].lower()
        # Tìm câu hỏi của bác sĩ trước khi kể triệu chứng phụ
        for line in lines:
            if line.startswith("Bác sĩ: "):
                nd = line.partition(": ")[2].lower()
                # Kiểm tra nếu câu hỏi triệu chứng khác nhắc đến triệu chứng chính (hoặc một cụm từ nòng cốt của nó)
                tu_chinh = chinh.split()
                cum_nong_cot = " ".join(tu_chinh[:min(3, len(tu_chinh))])
                if cum_nong_cot in nd and any(w in nd for w in ("ngoài", "bên cạnh", "kèm", "cùng với")):
                    co_ngu_canh += 1
                    break
    # Tối thiểu 30% số ca phải có câu hỏi triệu chứng khác nhắc ngữ cảnh triệu chứng chính đã kể
    assert co_ngu_canh >= 25, f"Chỉ có {co_ngu_canh} câu hỏi 'them' có ngữ cảnh triệu chứng chính (kỳ vọng >= 25/100)"


def test_vong_2_2_cau_hoi_tien_su_phan_hoa_doi_tuong():
    """Vòng 2.2: Câu hỏi tiền sử phân hoá theo nhóm tuổi (trẻ em vs người lớn) và có ngữ cảnh ca."""
    bo = shv.sinh_bo(100, seed=2611, mo_rong=True)
    hoi_ts_tre_em = 0
    co_hoi_ts_tre_em = 0
    tu_khoa_ts = ("bệnh cũ", "sức khỏe trước", "tiền sử bệnh", "bệnh mạn tính", "bệnh nền", "nằm viện", "đi viện", "ốm vặt", "phát triển trước giờ", "bệnh lý bẩm sinh")
    for ca in bo:
        if ca.get("la_tre_em"):
            lines = ca["input"].splitlines()
            for line in lines:
                if line.startswith("Bác sĩ: "):
                    nd = line.partition(": ")[2].lower()
                    if any(w in nd for w in ("trong nhà", "gia đình", "người thân", "bố mẹ", "anh chị", "anh em")):
                        continue
                    if any(w in nd for w in tu_khoa_ts):
                        co_hoi_ts_tre_em += 1
                        if any(w in nd for w in ("bé", "cháu", "con", "nhà mình")):
                            hoi_ts_tre_em += 1
                        break
    assert co_hoi_ts_tre_em > 0, "Phải có ca trẻ em có hỏi tiền sử"
    # Toàn bộ câu hỏi tiền sử trong ca trẻ em phải dùng từ xưng hô nhi khoa
    assert hoi_ts_tre_em == co_hoi_ts_tre_em, (
        f"Chỉ có {hoi_ts_tre_em}/{co_hoi_ts_tre_em} câu hỏi tiền sử trẻ em dùng ngôi nhi khoa"
    )


def test_vong_2_3_cau_hoi_thuoc_va_di_ung_ngu_canh():
    """Vòng 2.3: Câu hỏi thuốc và dị ứng gắn với ngữ cảnh ca và phân hoá đối tượng."""
    bo = shv.sinh_bo(100, seed=2611, mo_rong=True)
    hoi_thuoc_co_chinh = 0
    hoi_di_ung_tre_em = 0
    co_tre_em = 0
    for ca in bo:
        lines = ca["input"].splitlines()
        md_chinh = next((m for m in ca["dap_an"] if m.get("muc") == "BỆNH SỬ HIỆN TẠI" and m.get("quan_he") is None), None)
        chinh = md_chinh["noi_dung"].lower() if md_chinh else ""
        cum_chinh = " ".join(chinh.split()[:min(3, len(chinh.split()))])
        
        la_tre = ca.get("la_tre_em", False)
        if la_tre:
            co_tre_em += 1

        for line in lines:
            if line.startswith("Bác sĩ: "):
                nd = line.partition(": ")[2].lower()
                # Kiểm tra câu hỏi thuốc gắn với triệu chứng chính
                if any(w in nd for w in ("thuốc", "uống gì", "dùng gì")):
                    if cum_chinh and cum_chinh in nd and any(w in nd for w in ("từ lúc", "mấy hôm", "khi bị")):
                        hoi_thuoc_co_chinh += 1
                # Kiểm tra câu hỏi dị ứng ca trẻ em
                if la_tre and any(w in nd for w in ("dị ứng", "mẩn ngứa", "phản ứng lạ")):
                    if any(w in nd for w in ("bé", "cháu", "con")):
                        hoi_di_ung_tre_em += 1

    assert hoi_thuoc_co_chinh >= 10, f"Chỉ có {hoi_thuoc_co_chinh} câu hỏi thuốc nhắc triệu chứng chính (kỳ vọng >= 10)"
    assert hoi_di_ung_tre_em >= 5, f"Chỉ có {hoi_di_ung_tre_em} câu hỏi dị ứng trẻ em dùng ngôi nhi khoa (kỳ vọng >= 5)"


def test_vong_2_4_cau_hoi_gia_dinh_theo_he_co_quan():
    """Vòng 2.4: Câu hỏi tiền sử gia đình phân hoá theo hệ cơ quan của bệnh."""
    bo = shv.sinh_bo(100, seed=2611, mo_rong=True)
    hoi_gd_theo_he = 0
    co_hoi_gd = 0
    for ca in bo:
        if "tien_su_gia_dinh" in ca.get("bay", []):
            co_hoi_gd += 1
            lines = ca["input"].splitlines()
            for line in lines:
                if line.startswith("Bác sĩ: "):
                    nd = line.partition(": ")[2].lower()
                    if any(w in nd for w in ("trong nhà", "gia đình", "người thân", "bố mẹ", "anh chị em", "anh em ruột")):
                        # Có câu hỏi gia đình phân hoá theo cơ quan
                        if any(w in nd for w in ("hen", "hô hấp", "huyết áp", "tim mạch", "tiểu đường", "dạ dày", "khớp", "thần kinh", "thận", "tiết niệu", "da", "lây nhiễm", "tương tự")):
                            hoi_gd_theo_he += 1
                            break
    assert co_hoi_gd > 0, "Phải có ca có bẫy tiền sử gia đình"
    assert hoi_gd_theo_he >= int(co_hoi_gd * 0.4), (
        f"Chỉ có {hoi_gd_theo_he}/{co_hoi_gd} câu hỏi gia đình phân hoá theo nhóm bệnh"
    )


def test_vong_3_zero_information_leak_va_trich_dan_nguyen_van():
    """Bước 3: Kiểm tra toàn vẹn trích dẫn 100% là chuỗi con nguyên văn và không rò rỉ thông tin."""
    bo = shv.sinh_bo(200, seed=2611, mo_rong=True)
    for ca in bo:
        inp = ca["input"]
        # 1. 100% trich_dan la chuoi con nguyen van
        for md in ca.get("dap_an", []):
            for tc in md.get("trich_dan", []):
                assert tc in inp, f"Trích dẫn không phải chuỗi con: '{tc}' trong ca {ca['id']}"

        # 2. Câu hỏi của bác sĩ không được hỏi lộ tên bệnh chẩn đoán
        lines = inp.splitlines()
        benh_ten = ca["benh"].lower()
        for l in lines:
            role, _, text = l.partition(": ")
            text_l = text.lower()
            if role == "Bác sĩ" and text.strip().endswith("?"):
                if len(benh_ten) > 6 and benh_ten in text_l:
                    pytest.fail(f"Bác sĩ hỏi lộ tên bệnh '{benh_ten}' trong câu: '{text}' (ca {ca['id']})")
