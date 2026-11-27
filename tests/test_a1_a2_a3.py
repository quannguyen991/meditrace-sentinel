# -*- coding: utf-8 -*-
"""Kiểm thử hồi quy cho 3 hạng mục nâng cấp lõi (A1, A2, A3)."""
import json
from pathlib import Path

from src.duong_ong import b5_xep_cho_cong_rui_ro as cong_rui_ro
from src.he_thong import duong_dan as duong_dan
from src.bo_du_lieu.ca_mau_bgk import doc_ca_demo
from src.canh_bao.loai import LOAI, LOAI_NANG, muc_do, CAO
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu


def test_a1_demo_hai_benh_nhan_tach_nguoi_khac_khoi_tien_su_gia_dinh():
    """A1: Phát biểu của 'người khác' (bệnh nhân kế tiếp) không được lọt vào TIỀN SỬ GIA ĐÌNH hay gắn nhãn 'vợ'."""
    r = doc_ca_demo("demo_hai_benh_nhan")
    ghi_chu = r.get("ghi_chu", [])
    muc_tsgd = [g for g in ghi_chu if g.get("muc") == "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI"]
    assert muc_tsgd == [], f"Không được đẩy người khác vào TIỀN SỬ GIA ĐÌNH: {muc_tsgd}"

    # Mệnh đề đái tháo đường của người khác phải bị chặn sang CẦN XÁC NHẬN
    dm = [g for g in ghi_chu if "metformin" in str(g.get("noi_dung", "")).lower()]
    assert len(dm) == 1
    assert dm[0]["muc"] == "CẦN XÁC NHẬN"
    assert "vợ" not in str(dm[0].get("van", "")).lower()


def test_a2_cong_rui_ro_nhan_dien_thuoc_va_chan_doan_khi_khac_chu_the():
    """A2: cong_rui_ro.loai_thong_tin phải nhận diện đúng 'thuoc' và 'chan_doan' kể cả khi chu_the_id != 0."""
    p_thuoc = PhatBieu(
        id=6,
        nguoi_noi="người nhà",
        chu_the_id=3,
        noi_dung="augmentin",
        bang_chung=[15],
        thuoc={"ten": "augmentin", "lieu": "625 mg"},
    )
    assert cong_rui_ro.loai_thong_tin(p_thuoc) == "thuoc"

    p_cd = PhatBieu(
        id=9,
        nguoi_noi="bác sĩ",
        chu_the_id=3,
        noi_dung="Thiếu máu thiếu sắt",
        bang_chung=[18],
        hanh_vi="nhận định",
    )
    assert cong_rui_ro.loai_thong_tin(p_cd) == "chan_doan"
    assert "chan_doan" in LOAI_NANG
    assert muc_do("SUBJECT_AMBIGUOUS", "chan_doan") == CAO
    assert LOAI["ROUTE_MISMATCH"].muc_goc == CAO


def test_a3_khong_trung_cau_nguyen_van_train_dev_v2():
    """A3: Tập viet_train_v2.jsonl sau khử trùng phải có 0% câu trùng nguyên văn với viet_phat_trien_v2.jsonl."""
    goc = duong_dan.GOC_DU_AN / "data"
    tr_p = goc / "viet_train_v2.jsonl"
    dv_p = goc / "viet_phat_trien_v2.jsonl"
    if not tr_p.exists() or not dv_p.exists():
        return
    import re
    norm = lambda s: re.sub(r"\s+", " ", s.split(":", 1)[-1].strip().lower())
    tr_sents = {
        norm(ln)
        for line in tr_p.read_text(encoding="utf-8").splitlines()
        if line.strip()
        for ln in json.loads(line)["input"].splitlines()
        if ln.strip()
    }
    dv_lines = [
        norm(ln)
        for line in dv_p.read_text(encoding="utf-8").splitlines()
        if line.strip()
        for ln in json.loads(line)["input"].splitlines()
        if ln.strip()
    ]
    dup = sum(1 for s in dv_lines if s in tr_sents)
    assert dup == 0, f"Vẫn còn {dup} dòng dev trùng nguyên văn với train"
