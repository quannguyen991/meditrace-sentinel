# -*- coding: utf-8 -*-
"""Ten tep ket qua phai phan biet duoc cac cau hinh khac nhau.

VI SAO CO TEP NAY (10/09/2026).

Chuoi dung lai chay hai buoc lien nhau:

    2b  nhanh A, CO adapter      -> ra_A_viet_phat_trien.jsonl
    2c  nhanh A, KHONG adapter   -> ra_A_viet_phat_trien.jsonl   <- DE LEN

Ket qua cua 2b bien mat, im lang, khong bao gi. Va no la mot trong hai cot
cua bang so sanh chinh — "huan luyen dong gop bao nhieu" khong tra loi duoc
neu mot trong hai cot bi mat.

Loi con kin hon o cho: `cham_lai_bang_quy_gan.NHANH` DA liet ke "A_nen" nhu
mot nhanh rieng. Ben DOC luon mong doi mot tep ma ben GHI chua bao gio tao
ra, va hai ben lech nhau suot ma khong ai bao.
"""
import pathlib

import pytest

from src import cham_lai_bang_quy_gan as cl
from src import nhanh


# ------------------------------------------------- ham dat ten, kiem truc tiep

def test_co_adapter_va_khong_adapter_ra_HAI_ten_khac_nhau():
    co = nhanh.ten_ket_qua("A", "models/nen-qwen3-4b/best_checkpoint")
    khong = nhanh.ten_ket_qua("A", None)
    assert co != khong, "hai cau hinh khac nhau ma cung mot ten tep"


def test_co_adapter_giu_nguyen_ten_nhanh():
    """Giu nguyen `ra_A_*` cho ban co adapter de cac tep ket qua cu con doc
    duoc, va de bo cham khong phai doi."""
    assert nhanh.ten_ket_qua("A", "duong/dan/nao/do") == "A"
    assert nhanh.ten_ket_qua("A_cong", "duong/dan/nao/do") == "A_cong"


def test_khong_adapter_thi_them_hau_to_nen():
    assert nhanh.ten_ket_qua("A", None) == "A_nen"
    assert nhanh.ten_ket_qua("A_cong", None) == "A_cong_nen"


@pytest.mark.parametrize("rong", ["", None])
def test_adapter_rong_cung_tinh_la_khong_co(rong):
    """Chuoi rong tu dong lenh phai duoc coi nhu khong co adapter, khong duoc
    lot qua thanh ban 'co adapter'."""
    assert nhanh.ten_ket_qua("A", rong) == "A_nen"


# --------------------------------------------- hai ben doc/ghi phai khop nhau

def test_moi_ten_ben_GHI_sinh_ra_deu_co_trong_danh_sach_ben_DOC():
    """Day la phep kiem that su bat duoc loi da xay ra: ben ghi tao ra mot ten
    ma ben doc khong biet (hoac nguoc lai) thi so lieu bien mat lang le."""
    ben_ghi = {nhanh.ten_ket_qua(n, ad)
               for n in ("A", "A_cong")
               for ad in ("co/adapter", None)}
    thieu = ben_ghi - set(cl.NHANH)
    assert not thieu, f"ben ghi tao ra ten ma bo cham khong biet: {sorted(thieu)}"


def test_A_nen_nam_trong_danh_sach_cua_bo_cham():
    assert "A_nen" in cl.NHANH


# ------------------------------------------------------- cung nguyen tac, cho khac

def test_tep_dem_trich_kem_max_token_va_adapter():
    """Ket qua trich o 1536 va o 3072 la hai thu khac nhau; cua mo hinh nen va
    mo hinh da huan luyen cung vay. Tron chung mot tep thi lan sau dung lai ban
    cu ma khong ai biet."""
    t = (pathlib.Path("src") / "nhanh.py").read_text(encoding="utf-8")
    assert 'hau = "_hl" if a.adapter_trich else ""' in t
    assert 'f"trich_{a.tap}_{a.max_token}{hau}.jsonl"' in t
