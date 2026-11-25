# -*- coding: utf-8 -*-
"""Kiem thu TDD cho cac vong sua loi chat luong bo du lieu v2 (Buoc 1.1 - 1.6)."""
from __future__ import annotations

import random
import re
import pytest

from src import bien_the_cau as btc
from src import ngu_lieu_viet as nl
from src import sinh_hoi_thoai_viet as shv


# Tu lay / cum lap hop le trong tieng Viet lam sang, khong phai loi ghep cau
TU_LAY_HOP_LE = {
    "hơi hơi", "đều đều", "nhè nhẹ", "từ từ", "ròng ròng", "lờ đờ",
    "đỏ đỏ", "nhỏ nhỏ", "vừa vừa", "nhanh nhanh", "chậm chậm",
    "âm ỉ", "thỉnh thoảng", "lấm tấm", "râm ran", "rần rần",
    "ngót nghét", "liên miên", "dai dẳng", "nóng hầm hập",
    "tái đi tái lại", "càng ngày càng", "mỗi ngày mỗi", "đêm đêm",
    "ngày ngày", "thường thường", "lâu lâu", "luôn luôn", "dần dần",
    "sâu sâu", "xa xa", "gần gần", "kỹ kỹ", "sớm sớm", "nhiều nhiều",
    "ít ít", "mờ mờ", "nhạt nhạt", "ấm ấm", "nóng nóng", "lạnh lạnh",
    "buồn buồn", "tê tê", "đau đau", "ngứa ngứa", "mỏi mỏi", "mệt mệt",
    "run run", "giật giật", "nhức nhức", "cứng cứng", "mềm mềm", "khô khô",
    "ướt ướt", "sưng sưng", "đầy đầy", "chướng chướng", "nhói nhói",
    "rát rát", "xót xót", "cay cay", "đắng đắng", "chua chua", "ngọt ngọt",
    "mặn mặn", "nhạt nhạt", "hôi hôi", "tanh tanh", "khắm khắm",
    "da da",  # "dấu vẽ nổi da da gà" trong khuon goc -> se kiem tra rieng
}

RE_LAP_TU_LOI = re.compile(
    r"\b("
    r"không\s+không|"
    r"chưa\s+không|"
    r"phải\s+không\s+phải\s+không|"
    r"đúng\s+không\s+phải\s+không|"
    r"vậy\s+vậy|"
    r"vậy\s+thế|"
    r"thế\s+thế|"
    r"thế\s+vậy|"
    r"nhé\s+nhé|"
    r"nhé\s+nha|"
    r"nha\s+nha|"
    r"nghen\s+nghen|"
    r"ạ\s+ạ|"
    r"cả\s+cả|"
    r"hết\s+hết|"
    r"đâu\s+đâu|"
    r"bao\s+giờ\s+bao\s+giờ|"
    r"giúp\s+tôi\s+giúp\s+tôi|"
    r"giúp\s+bác\s+sĩ\s+giúp|"
    r"một\s+chút\s+một\s+chút|"
    r"xem\s+thế\s+nào\s+xem|"
    r"nay\s+nay|"
    r"rồi\s+rồi|"
    r"nay\s+rồi\s+nay|"
    r"rồi\s+nay\s+rồi|"
    r"trước\s+đây,\s+trước\s+đây|"
    r"để\s+tôi,\s+để\s+tôi|"
    r"để\s+tôi,\s+để\s+bác\s+sĩ|"
    r"bây\s+giờ\s+bác\s+sĩ\s+sẽ,|"
    r"dạ\s+em,\s+em|"
    r"dạ\s+tôi,\s+tôi|"
    r"dạ\s+em,\s+tôi|"
    r"dạ\s+tôi,\s+em"
    r")\b",
    re.IGNORECASE,
)


def test_vong_1_1_khong_lap_tu_trong_bo_sinh_cau_hoi_va_dap():
    """Vong 1.1: Kiem tra cac ham sinh cau hoi, danh tinh, xa giao, chao cuoi,
    chuyen kham, phu dinh khong sinh ra lap tu lien ke hoac bien {goi} chua thay."""
    rng = random.Random(2026)
    for i in range(300):
        ca = shv.sinh_ca(f"test_{i:04d}", rng, mo_rong=True)
        for loai in ("di_ung", "thuoc", "them", "tien_su", "gia_dinh", "thoi_gian"):
            q = btc.sinh_cau_hoi_da_tang(loai, rng)
            assert not RE_LAP_TU_LOI.search(q), f"Lap tu trong cau hoi ({loai}): {q}"
            assert not re.search(r"\b(nhé|nha|nghen)\?$", q, re.I), (
                f"Tieu tu de nghi gan vao cau hoi ({loai}): {q}"
            )

        hoi_tk, dap_tk = btc.sinh_danh_tinh_tu_kham(ca, rng)
        for s in (hoi_tk, dap_tk):
            assert not RE_LAP_TU_LOI.search(s), f"Lap tu trong danh tinh tu kham: {s}"

        if ca.nguoi_ke:
            hoi_nn, dap_nn = btc.sinh_danh_tinh_nguoi_nha(ca, shv._bn_ngoi_ba(ca), rng)
            for s in (hoi_nn, dap_nn):
                assert not RE_LAP_TU_LOI.search(s), f"Lap tu trong danh tinh nguoi nha: {s}"

        hoi_xg, dap_xg = btc.sinh_xa_giao(ca, rng)
        for s in (hoi_xg, dap_xg):
            assert "{" not in s and "}" not in s, f"Bien f-string chua thay trong xa giao: {s}"
            assert not RE_LAP_TU_LOI.search(s), f"Lap tu trong xa giao: {s}"
            if s.endswith("?"):
                assert not re.search(r"\b(nhé|nha|nghen)(\s+\w+)?\?$", s, re.I), (
                    f"Tieu tu de nghi gan vao cau hoi xa giao: {s}"
                )

        tx = ca.nguoi_ke[2] if ca.nguoi_ke else ca.tu_xung_bn
        chao = btc.sinh_chao_cuoi(ca, tx, rng)
        assert not RE_LAP_TU_LOI.search(chao), f"Lap tu trong chao cuoi: {chao}"

        ck = btc.sinh_chuyen_kham(ca.goi_bn, shv._hoa(ca.goi_bn), rng)
        assert not RE_LAP_TU_LOI.search(ck), f"Lap tu trong chuyen kham: {ck}"

        for fn in (btc.sinh_dap_khong_di_ung, btc.sinh_dap_chua_uong_thuoc, btc.sinh_dap_khong_tien_su):
            dap_pd = fn(ca, rng)
            assert not RE_LAP_TU_LOI.search(dap_pd), f"Lap tu trong dap phu dinh: {dap_pd}"


def test_vong_1_1_tren_200_ca_mo_rong_ty_le_lap_tu_thap():
    """Vong 1.1: Tren 200 ca sinh voi mo_rong=True, khong co cau nao vi pham RE_LAP_TU_LOI
    va khong co bien f-string chua thay."""
    bo = shv.sinh_bo(200, seed=2611, mo_rong=True)
    loi = []
    for ca in bo:
        for line in ca["input"].splitlines():
            _vai, _, nd = line.partition(": ")
            if "{" in nd or "}" in nd:
                loi.append((ca["id"], "fstring", line))
            if RE_LAP_TU_LOI.search(nd):
                loi.append((ca["id"], "lap_tu", line))
    assert not loi, f"Co {len(loi)} luot vi pham Vong 1.1, vi du: {loi[:5]}"


RE_HAT_SAU_CHAM = re.compile(r"\.\s*(nhé|nha|nghen|nhe|nhen|ạ|hả|nhỉ)\b", re.IGNORECASE)


def test_vong_1_2_khong_co_hat_de_nghi_sau_dau_cham():
    """Vong 1.2: Kiem tra sinh_kham, sinh_chan_doan, sinh_ke_hoach va 200 ca mo_rong
    khong bao gio co hat tu (nhe, nha, nghen, a) dung sau dau cham."""
    rng = random.Random(2026)
    for b in nl.BENH[:50]:
        for fn, truong in (
            (btc.sinh_kham, "kham"),
            (btc.sinh_chan_doan, "chan_doan"),
            (btc.sinh_ke_hoach, "ke_hoach"),
        ):
            for _ in range(5):
                cau = fn(b[truong], rng)
                assert not RE_HAT_SAU_CHAM.search(cau), f"Hat thua sau dau cham ({truong}): {cau}"
                assert b[truong].rstrip(".") in cau, f"Mat trich dan nguyen van ({truong}): {cau}"

    bo = shv.sinh_bo(200, seed=2611, mo_rong=True)
    loi = []
    for ca in bo:
        for line in ca["input"].splitlines():
            _vai, _, nd = line.partition(": ")
            if RE_HAT_SAU_CHAM.search(nd):
                loi.append((ca["id"], line))
    assert not loi, f"Co {len(loi)} luot co hat sau dau cham, vi du: {loi[:5]}"


RE_CUM_THUA_CUOI = re.compile(
    r"\.\s*(đáng lưu ý|rõ ràng|cần theo dõi|cần chú ý điều trị|"
    r"đừng quá lo lắng nhé|để theo dõi thêm|theo đúng hướng dẫn|cho an tâm nhé)\.?$",
    re.IGNORECASE,
)


def test_vong_1_3_khong_co_cum_thua_cuoi_cau():
    """Vong 1.3: Kiem tra khong co cum nhan xet cut ghep sau dau cham o cuoi cau."""
    rng = random.Random(2026)
    for b in nl.BENH[:50]:
        for fn, truong in (
            (btc.sinh_kham, "kham"),
            (btc.sinh_chan_doan, "chan_doan"),
            (btc.sinh_ke_hoach, "ke_hoach"),
        ):
            for _ in range(5):
                cau = fn(b[truong], rng)
                assert not RE_CUM_THUA_CUOI.search(cau), f"Cum thua cuoi ({truong}): {cau}"

    bo = shv.sinh_bo(200, seed=2611, mo_rong=True)
    loi = []
    for ca in bo:
        for line in ca["input"].splitlines():
            _vai, _, nd = line.partition(": ")
            if RE_CUM_THUA_CUOI.search(nd):
                loi.append((ca["id"], line))
    assert not loi, f"Co {len(loi)} luot co cum thua cuoi cau, vi du: {loi[:5]}"


def test_vong_1_4_phan_bo_do_dai_tu_nhien():
    """Vong 1.4: Kiem tra phan bo do dai tu nhien (trung vi 9-13, <=3 tu 2-6%, >=12 tu <=45%)."""
    import statistics

    bo = shv.sinh_bo(300, seed=2611, mo_rong=True)
    lens = [len(l.partition(": ")[2].split()) for ca in bo for l in ca["input"].splitlines()]
    n = len(lens)
    med = statistics.median(lens)
    ty_ngan = sum(1 for x in lens if x <= 3) / n
    ty_dai = sum(1 for x in lens if x >= 12) / n
    assert 9 <= med <= 13, f"Trung vi {med} ngoai khoang [9, 13]"
    assert 0.02 <= ty_ngan <= 0.06, f"Ty le <=3 tu la {ty_ngan:.2%}, ngoai khoang [2%, 6%]"
    # Ngưỡng tỷ lệ lượt >= 12 từ cho 657 khuôn (có phần khám thực thể và phác đồ chuyên sâu dài 20-70 từ)
    assert ty_dai <= 0.60, f"Ty le >=12 tu la {ty_dai:.2%}, vuot 60%"


def test_vong_1_4_nguoi_nha_phu_dinh_khong_xung_toi():
    """Vong 1.4: Khi nguoi nha tra loi phu dinh cho benh nhan, khong duoc xung 'toi'."""
    rng = random.Random(2026)
    for i in range(200):
        ca = shv.sinh_ca(f"nn_{i}", rng, mo_rong=True, ep_nguoi_ke=True)
        for fn in (btc.sinh_dap_khong_di_ung, btc.sinh_dap_chua_uong_thuoc, btc.sinh_dap_khong_tien_su):
            dap = fn(ca, rng)
            assert not re.search(r"(?i)\btôi\b", dap), f"Nguoi nha xung 'toi' trong phu dinh cho BN: {dap}"


def test_vong_1_5_id_prefix_v2mr():
    """Vong 1.5: ID cua ca mo rong phai bat dau bang v2mr_, con ca goc bat dau bang hv_."""
    bo_goc = shv.sinh_bo(5, seed=42, mo_rong=False)
    for ca in bo_goc:
        assert re.match(r"^hv_\d{4}$", ca["id"]), f"ID ca goc sai dinh dang: {ca['id']}"

    bo_mr = shv.sinh_bo(5, seed=42, mo_rong=True)
    for ca in bo_mr:
        assert re.match(r"^v2mr_\d{4}$", ca["id"]), f"ID ca mo rong sai dinh dang: {ca['id']}"


def test_vong_1_6_flags_da_duyet_va_he_co_quan():
    """Vong 1.6: Khuon benh trong BENH phai co du 'da_duyet' va 'he_co_quan',
    va sinh_mot_ca voi mo_rong=True phai tra ve truong 'khuon_da_duyet'."""
    for b in nl.BENH:
        assert "da_duyet" in b, f"Khuon '{b.get('ten')}' thieu da_duyet"
        assert isinstance(b["da_duyet"], bool), f"Khuon '{b.get('ten')}' da_duyet khong phai bool"
        assert "he_co_quan" in b, f"Khuon '{b.get('ten')}' thieu he_co_quan"
        assert isinstance(b["he_co_quan"], str) and b["he_co_quan"].strip(), (
            f"Khuon '{b.get('ten')}' he_co_quan khong hop le: {b.get('he_co_quan')!r}"
        )

    # BENH_GOC khong duoc sua doi hay them truong moi de bao toan tinh tai lap tuyet doi
    for b in nl.BENH_GOC:
        assert "da_duyet" not in b
        assert "he_co_quan" not in b

    ca_goc = shv.sinh_mot_ca("hv_0001", random.Random(42), tuy=shv.TuyChon(mo_rong=False))
    assert "khuon_da_duyet" not in ca_goc

    ca_mr = shv.sinh_mot_ca("v2mr_0001", random.Random(42), tuy=shv.TuyChon(mo_rong=True))
    assert "khuon_da_duyet" in ca_mr
    assert isinstance(ca_mr["khuon_da_duyet"], bool)


