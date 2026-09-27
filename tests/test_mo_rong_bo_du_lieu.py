# -*- coding: utf-8 -*-
"""Mo rong bo du lieu ngay 11/09/2026: 100 khuon, 200 noi dung nguoi nha, tang 4.

VI SAO CAN TEST RIENG. Truoc khi mo rong, do tren tap train bo 5.000:

    tang 4 (nguoi nha ke ve CHINH MINH)   1.101 menh de, chi 25 noi dung
    tap phat trien dung lai noi dung train 25/25 (284/284 menh de)

Nghia la du an chia tap theo khuon de do kha nang khai quat, nhung tu vung
nguoi nha di xuyen qua ca ba tap — nen tang 4, cho quan trong nhat, chua bao gio
duoc thu tren noi dung CHUA THAY. Va 25 chuoi lap trung binh 44 lan thi mot mo
hinh hoc thuoc chung la du.

Test o day canh ba dieu co the troi ma khong ai thay:

  1. be noi dung nguoi nha cua moi tap KHONG chong nhau
  2. tap ma bo sinh GIA DINH cho mot ca KHOP voi tap ma buoc chia THUC SU dat
     no vao — neu hai cho lech nhau thi be theo tap ro ri ma khong bao loi
  3. bang benh chi co o mot gioi TRO VAO chuoi co that trong be — neu khong thi
     phep loc gioi la ma chet, dung ho loi `ten_chu_the` / hang so `ME`
"""
import collections

import pytest

from src import do_tang_quy_gan
from src import ngu_lieu_viet as nl
from src import sinh_hoi_thoai_viet as sh
from src import tach_tap_viet as tt

TAP = ("train", "phat_trien", "kiem_tra_cuoi")
BANG = {"moi_tuoi": nl.TIEN_SU_GIA_DINH_MOI_TUOI,
        "lon_tuoi": nl.TIEN_SU_GIA_DINH_LON_TUOI,
        "di_ung": nl.DI_UNG_NGUOI_NHA}


@pytest.fixture(scope="module")
def toan_bo():
    """Bo DAY DU 5.000 ca. Mau nho khong du: voi 100 khuon, mau 40 ca se thieu
    khuon, va `chia` tinh tap tu cac khuon CO MAT — lech voi bo sinh."""
    bo = sh.sinh_bo(5000, seed=42)
    tr, pt, kt, _kh = tt.chia(bo)
    return bo, {"train": tr, "phat_trien": pt, "kiem_tra_cuoi": kt}


def _tang4(ds):
    """-> Counter noi dung cua menh de tang 4 (`ke_ve_minh`) trong `ds`.

    Dung CHINH dinh nghia tang cua thuoc do chu khong tu viet lai: mot khau thu
    hai tu dem "tang 4" la dung ho loi "hai khau dung hai bo ten muc".
    """
    c = collections.Counter()
    for x in ds:
        for tang, _ct, gia in do_tang_quy_gan.menh_de_dap_an(x):
            if tang == "ke_ve_minh":
                c[gia.cau.strip().lower()] += 1
    return c


# ------------------------------------------------------------- khuon benh

def test_du_100_khuon():
    assert len(nl.BENH) == 100


def test_khuon_khong_trung_ten_va_du_truong():
    ten = [b["ten"] for b in nl.BENH]
    assert len(set(ten)) == len(ten), "co ten khuon trung"
    for b in nl.BENH:
        for k in ("nhom", "dien_tien", "chinh", "phu", "kham", "chan_doan",
                  "ke_hoach"):
            assert b.get(k), (b["ten"], k)


def test_khuon_nhi_da_tang():
    """Truoc mo rong chi 13/60 khuon la nhi."""
    assert sum(1 for b in nl.BENH if b["nhom"] == "nhi") >= 20


# ------------------------------------------------- be noi dung nguoi nha

def test_du_200_noi_dung_nguoi_nha_KHAC_NHAU():
    """Dem noi dung SAU KHI hien ra (di ung thanh "di ung X"), vi do moi la
    chuoi mo hinh thay."""
    noi = (list(nl.TIEN_SU_GIA_DINH_MOI_TUOI) + list(nl.TIEN_SU_GIA_DINH_LON_TUOI)
           + [f"dị ứng {x}" for x in nl.DI_UNG_NGUOI_NHA])
    assert len(noi) == 200
    assert len(set(noi)) == 200, "co noi dung trung"


def test_moi_tuoi_va_lon_tuoi_KHONG_trung():
    assert not set(nl.TIEN_SU_GIA_DINH_MOI_TUOI) & set(nl.TIEN_SU_GIA_DINH_LON_TUOI)


@pytest.mark.parametrize("ten", list(BANG))
def test_moi_noi_dung_thuoc_DUNG_MOT_tap(ten):
    """Mot noi dung o hai tap la ro ri — dung cai ma be theo tap chan."""
    for x in BANG[ten]:
        o = [t for t in TAP if x in sh.be_theo_tap(BANG[ten], t)]
        assert len(o) == 1, (ten, x, o)


@pytest.mark.parametrize("ten", list(BANG))
@pytest.mark.parametrize("tap", TAP)
def test_be_moi_tap_KHONG_rong(ten, tap):
    assert sh.be_theo_tap(BANG[ten], tap)


@pytest.mark.parametrize("tap", TAP)
def test_loc_gioi_KHONG_lam_rong_be(tap):
    """Be benh MOI TUOI la duong lui cuoi cua `_benh_hop_tuoi`: rong sau khi loc
    gioi thi `rng.choice([])` no. Be tuoi gia duoc phep rong — co duong lui."""
    for vai in nl.VAI_NU | nl.VAI_NAM:
        ung = [b for b in sh.be_theo_tap(nl.TIEN_SU_GIA_DINH_MOI_TUOI, tap)
               if sh._hop_gioi(b, vai)]
        assert ung, (tap, vai)


def test_benh_mot_gioi_TRO_VAO_chuoi_co_that():
    """Neu CHI_NU / CHI_NAM chua mot chuoi khong co trong be thi phep loc gioi
    khong loc gi ca — ma chet, khong bao loi. Da gap dung ho loi nay voi
    `ten_chu_the` va hang so `ME` trong cung ngay."""
    be = set(nl.TIEN_SU_GIA_DINH_MOI_TUOI) | set(nl.TIEN_SU_GIA_DINH_LON_TUOI)
    assert not (nl.CHI_NU - be), f"khong co trong be: {nl.CHI_NU - be}"
    assert not (nl.CHI_NAM - be), f"khong co trong be: {nl.CHI_NAM - be}"


def test_hop_gioi():
    assert not sh._hop_gioi("u xơ tử cung", "bố")
    assert not sh._hop_gioi("phì đại tuyến tiền liệt", "mẹ")
    assert sh._hop_gioi("u xơ tử cung", "mẹ")
    assert sh._hop_gioi("tăng huyết áp", "bố")


# ------------------------------------ tren bo DAY DU: chia khop voi bo sinh

def test_tap_bo_sinh_GIA_DINH_KHOP_tap_buoc_chia_DAT(toan_bo):
    """Neu hai cho lech nhau, be theo tap ro ri ma KHONG co gi bao loi: bo sinh
    rut noi dung tu be cua tap A cho mot ca ma buoc chia dat vao tap B."""
    _bo, theo_tap = toan_bo
    bang = sh.bang_tap_khuon()
    for tap, ds in theo_tap.items():
        for x in ds:
            assert bang[x["benh"]] == tap, (x["id"], x["benh"], tap)


def test_buoc_chia_KHOP_thi_cho_qua(toan_bo):
    bo, _ = toan_bo
    *_, khuon = tt.chia(bo)
    tt.kiem_khop_bo_sinh(khuon)


def test_chia_voi_so_KHAC_mac_dinh_thi_DUNG_LAI(toan_bo):
    """`--so-phat-trien 8 --so-kiem-tra 7` (so cu) tren bo moi."""
    bo, _ = toan_bo
    *_, khuon = tt.chia(bo, so_phat_trien=8, so_kiem_tra=7)
    with pytest.raises(SystemExit):
        tt.kiem_khop_bo_sinh(khuon)


def test_tep_THIEU_mot_khuon_dev_thi_DUNG_LAI(toan_bo):
    """Thieu mot khuon TRAIN thi khong khuon nao doi tap — khong co gi de bat.
    Thieu mot khuon DEV thi khuon train dau tien truot len dev."""
    bo, _ = toan_bo
    bo_di = next(t for t, tap in sorted(sh.bang_tap_khuon().items())
                 if tap == "phat_trien")
    *_, khuon = tt.chia([x for x in bo if x["benh"] != bo_di])
    with pytest.raises(SystemExit):
        tt.kiem_khop_bo_sinh(khuon)


def test_tang4_dev_test_KHONG_dung_lai_noi_dung_train(toan_bo):
    """Truoc mo rong: tap phat trien dung lai 25/25 chuoi cua train."""
    _bo, theo_tap = toan_bo
    tr = set(_tang4(theo_tap["train"]))
    for tap in ("phat_trien", "kiem_tra_cuoi"):
        chung = tr & set(_tang4(theo_tap[tap]))
        assert not chung, f"{tap} dung lai noi dung train: {sorted(chung)[:5]}"


def test_tang4_train_DU_1500_menh_de(toan_bo):
    """Dich dat ngay 11/09/2026. Truoc do: 1.101."""
    _bo, theo_tap = toan_bo
    assert sum(_tang4(theo_tap["train"]).values()) >= 1500


def test_tang4_train_DA_DANG_noi_dung(toan_bo):
    """Truoc do 25 noi dung, moi chuoi lap trung binh 44 lan."""
    _bo, theo_tap = toan_bo
    assert len(_tang4(theo_tap["train"])) >= 100


def test_KHONG_co_benh_sai_gioi_trong_dap_an(toan_bo):
    bo, _ = toan_bo
    nu = {s.lower() for s in nl.CHI_NU}
    nam = {s.lower() for s in nl.CHI_NAM}
    for x in bo:
        for m in x["dap_an"]:
            nd = str(m.get("noi_dung") or "").strip().lower()
            ct = m["chu_the"]
            assert not (ct in nl.VAI_NAM and nd in nu), (x["id"], ct, nd)
            assert not (ct in nl.VAI_NU and nd in nam), (x["id"], ct, nd)
