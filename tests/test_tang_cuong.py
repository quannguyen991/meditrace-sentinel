# -*- coding: utf-8 -*-
"""Bat bien quan trong nhat: benh an doi DUNG theo tung phep bien doi.

    doi_vai   -> benh an KHONG doi
    chen      -> benh an THEM muc TIEN SU GIA DINH

Cau "benh an luon giu nguyen" la sai, va test nay chan dung cho do.
"""
from src import sinh_bo_chan_doan, tang_cuong

MAU = {
    "id": "t1",
    "input": "Bác sĩ: Chị thấy trong người thế nào?\nBệnh nhân: Tôi đau đầu ba ngày nay.",
    "output": "LÝ DO KHÁM BỆNH\n\nĐau đầu ba ngày.",
}


def test_doi_vai_khong_doi_benh_an():
    ra = tang_cuong.doi_vai_thanh_nguoi_nha(MAU)
    assert ra is not None
    assert ra["output"] == MAU["output"], "trieu chung van cua benh nhan"
    assert "Người nhà:" in ra["input"]
    assert "Bệnh nhân:" not in ra["input"]


def test_doi_vai_chuyen_dai_tu():
    ra = tang_cuong.doi_vai_thanh_nguoi_nha(MAU)
    assert "Cháu đau đầu" in ra["input"], "'Toi dau dau' phai thanh 'Chau dau dau'"


def test_doi_vai_tu_choi_khi_dai_tu_long_nhau():
    """'Toi thay con toi met' -> 'Chau thay con chau met' la vo nghia."""
    kho = {**MAU, "input": "Bệnh nhân: Tôi thấy con tôi mệt lắm."}
    assert tang_cuong.doi_vai_thanh_nguoi_nha(kho) is None


def test_doi_vai_tu_choi_khi_khong_co_luot_benh_nhan():
    assert tang_cuong.doi_vai_thanh_nguoi_nha(
        {**MAU, "input": "Bác sĩ: Chào chị."}) is None


def test_chen_tien_su_THEM_muc_gia_dinh():
    """Benh an PHAI doi — tien su nguoi nha thuoc muc TIEN SU GIA DINH."""
    ra = tang_cuong.chen_tien_su_nguoi_nha(MAU, seed=1)
    assert tang_cuong.MUC_GIA_DINH in ra["output"]
    assert "Đau đầu ba ngày." in ra["output"], "phan cu phai con nguyen"
    assert "Người nhà:" in ra["input"]


def test_chen_them_dung_mot_luot():
    ra = tang_cuong.chen_tien_su_nguoi_nha(MAU, seed=1)
    assert len(ra["input"].split("\n")) == len(MAU["input"].split("\n")) + 1


def test_chen_dung_ngoi_thu_nhat_cho_nguoi_nha():
    """Nguoi nha ke benh CUA CHINH HO, khong phai cua benh nhan."""
    ra = tang_cuong.chen_tien_su_nguoi_nha(MAU, seed=1)
    luot = [d for d in ra["input"].split("\n") if d.startswith("Người nhà:")][0]
    assert "tôi" in luot.lower(), luot


def test_mau_cau_roi_han_voi_bo_chan_doan():
    """Chong ro ri lan hai: kiem tra tren dung thu da day."""
    assert not (set(tang_cuong.MAU_CAU) & set(sinh_bo_chan_doan.MAU_CAU))


def test_sinh_lai_cung_seed_ra_cung_ket_qua():
    a = tang_cuong.chen_tien_su_nguoi_nha(MAU, seed=7)
    b = tang_cuong.chen_tien_su_nguoi_nha(MAU, seed=7)
    assert a == b


def test_khong_dung_mo_hinh_ngon_ngu():
    """Toan bo module chi dung thu vien chuan — khong goi mo hinh nao."""
    import inspect
    ma = inspect.getsource(tang_cuong)
    for cam in ("openai", "transformers", "requests", "http", "anthropic"):
        assert cam not in ma, f"module khong duoc dung {cam}"


def test_doi_vai_tu_choi_khi_cau_da_co_chau():
    """Tim ra khi soat tay: doi "toi" -> "chau" lam tu nay qua tai.

    "Tôi có hai bé trai, các cháu ở với tôi"
        -> "Cháu có hai bé trai, các cháu ở với cháu"
    """
    for cau in (
        "Bệnh nhân: Tôi có hai bé trai, các cháu ở với tôi ạ.",
        "Bệnh nhân: Ba tôi với ông nội đều bị đái tháo đường.",
    ):
        assert tang_cuong.doi_vai_thanh_nguoi_nha({**MAU, "input": cau}) is None, cau
