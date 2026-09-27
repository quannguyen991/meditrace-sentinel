# -*- coding: utf-8 -*-
"""Ban nhap co NEU TEN NGUOI khong — truc ma `f1_quy_gan` khong do.

VI SAO CAN. Do duoc 11/09/2026 tren tap phat trien the he 2: muc TIEN SU GIA DINH
VA XA HOI cua ban tham chieu co 22 cau va 22 cau neu ten nguoi; cua nhanh B, C, D
co 50, 50, 53 cau va **0 cau neu ten nguoi**.

Va khi sua de chung neu ten (0% -> 100%), `f1_quy_gan` doi **0,0000** voi khoang
tin cay [0,0000; 0,0000]. Ly do: `thuoc_do_quy_gan._chu_the_cua_cau` suy chu the tu
TEN MUC khi cau khong co tu chi nguoi, nen mot cau khong ten nam trong muc gia dinh
van duoc cham la "nguoi nha".

Nen con so 100% o tang 4 la diem cua viec XEP DUNG MUC, khong phai diem cua viec
GAN DUNG NGUOI. Tep nay do dung cai thu hai.
"""
import json

import pytest

from src import do_neu_ten as dnt
from src import sinh_benh_an

MUC = sinh_benh_an.MUC_NGUOI_KHAC


def _ban(noi_dung_muc, muc=MUC):
    return (f"BỆNH SỬ HIỆN TẠI\n\nsốt hai hôm.\n\n{muc}\n\n{noi_dung_muc}\n\n"
            f"KẾ HOẠCH ĐIỀU TRỊ\n\nhạ sốt.")


# ------------------------------------------------- tach cau trong muc

def test_lay_dung_cau_trong_muc():
    cau = dnt.cau_trong_muc(_ban("Mẹ rối loạn mỡ máu."))
    assert cau == ["Mẹ rối loạn mỡ máu."]


def test_tach_NHIEU_menh_de_tren_MOT_dong():
    """`sinh_benh_an` noi nhieu menh de vao mot dong bang dau cham. Tach theo
    dong thi dem 1 thay vi 2, va ty le ra sai."""
    cau = dnt.cau_trong_muc(_ban("Mẹ rối loạn mỡ máu. Bố tăng huyết áp."))
    assert len(cau) == 2


def test_tieu_de_moi_ket_thuc_muc():
    """Khong dung o tieu de tiep theo thi dem ca muc sau vao."""
    cau = dnt.cau_trong_muc(_ban("Mẹ rối loạn mỡ máu."))
    assert all("hạ sốt" not in c for c in cau)


def test_muc_khong_co_thi_tra_ve_rong():
    assert dnt.cau_trong_muc("BỆNH SỬ HIỆN TẠI\n\nsốt.") == []


# ------------------------------------------------- nhan dang neu ten

@pytest.mark.parametrize("cau", [
    "Mẹ rối loạn mỡ máu.",
    "mẹ: dị ứng penicillin",
    "Bà ngoại tăng huyết áp.",
    "người nhà: dị ứng aspirin",
    "- Bố đái tháo đường típ 2",
])
def test_co_neu_ten(cau):
    assert dnt.co_neu_ten(cau)


@pytest.mark.parametrize("cau", [
    "rối loạn mỡ máu.",
    "dị ứng penicillin",
    "tăng huyết áp",
    "",
])
def test_KHONG_neu_ten(cau):
    """Day dung la dang ma nhanh B, C, D sinh ra 50/50/53 lan."""
    assert not dnt.co_neu_ten(cau)


def test_tu_chi_nguoi_GIUA_cau_khong_tinh():
    """"di ung thuoc cua me cho" la noi dung, khong phai nhan chu the."""
    assert not dnt.co_neu_ten("dị ứng thuốc của mẹ cho")


# ------------------------------------------------------------- cham

def test_cham_tra_ve_ty_le():
    kq = [{"du_doan": _ban("Mẹ rối loạn mỡ máu.")},
          {"du_doan": _ban("tăng huyết áp.")}]
    d = dnt.cham(kq)
    assert d["so_cau"] == 2 and d["so_neu_ten"] == 1 and d["ty_le"] == 0.5


def test_cham_muc_rong_thi_ty_le_la_nan():
    d = dnt.cham([{"du_doan": "BỆNH SỬ HIỆN TẠI\n\nsốt."}])
    assert d["so_cau"] == 0
    assert d["ty_le"] != d["ty_le"]        # nan, khong phai 0 — khong co gi de do


def test_cham_doc_duoc_khoa_tham_chieu():
    kq = [{"du_doan": _ban("tăng huyết áp."),
           "tham_chieu": _ban("Mẹ tăng huyết áp.")}]
    assert dnt.cham(kq, "du_doan")["ty_le"] == 0.0
    assert dnt.cham(kq, "tham_chieu")["ty_le"] == 1.0


# ---------------------------------------- do tren du lieu THAT neu co

def test_tham_chieu_the_he_2_neu_ten_100_phan_tram():
    """Ban tham chieu luon neu ten. Do la moc ma ban nhap phai dat."""
    from pathlib import Path
    p = Path("data/ra_B_viet_phat_trien_th2.jsonl")
    if not p.exists():
        pytest.skip("chua co du lieu the he 2")
    kq = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    d = dnt.cham(kq, "tham_chieu")
    assert d["so_cau"] >= 10
    assert d["ty_le"] == 1.0, f"tham chieu chi neu ten {d['ty_le']:.0%}"
