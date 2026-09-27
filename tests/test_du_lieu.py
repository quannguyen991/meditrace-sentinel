# -*- coding: utf-8 -*-
import pytest

from src import du_lieu, duong_dan, tach_tap

pytestmark = pytest.mark.skipif(
    not duong_dan.GOC_VAIC.exists(),
    reason="can thu muc du lieu goc 'D:/VAIC DE @' — chi co tren laptop, khong co tren HoaiDuc")


def test_tach_luot_thoai():
    ht = "Bác sĩ: Cháu sao rồi?\nMẹ: Cháu sốt hai ngày."
    assert du_lieu.tach_luot_thoai(ht) == [
        ("Bác sĩ", "Cháu sao rồi?"),
        ("Mẹ", "Cháu sốt hai ngày."),
    ]


def test_co_nguoi_nha():
    assert du_lieu.co_nguoi_nha({"input": "Người nhà: Cháu sốt."}) is True
    assert du_lieu.co_nguoi_nha({"input": "Bệnh nhân: Tôi sốt."}) is False


def test_thong_ke_khop_so_da_khao_sat():
    """Chot cung so lieu do ngay 05/09/2026.

    Neu test nay hong, du lieu goc da bi thay doi va MOI ket luan trong
    de cuong lan ke hoach deu phai xem lai.

    So ca nhi da doi 109 -> 58 sau khi kiem tay 30 mau: cach nhan dien ban 1
    chi dat 53% do chinh xac. Xem docs/ket-qua/kiem-tay-nhan-nhi.md.
    """
    tk = du_lieu.thong_ke(du_lieu.nap_mau(duong_dan.TRAIN_JSONL))
    assert tk["tong"] == 1305
    assert tk["so_mau_nguoi_nha"] == 115
    assert tk["so_mau_nhi"] == 58
    assert tk["so_mau_ca_hai"] == 39
    assert tk["luot_theo_vai"]["Người nhà"] == 433


def test_nhan_nhi_loai_duoc_bon_kieu_sai_da_biet():
    """Bon kieu sai tim ra khi kiem tay ban 1."""
    for cau in (
        "Bệnh nhân: Dạ hồi trẻ em có hút, nhưng bây giờ thì không nữa ạ.",
        "Bệnh nhân: Em còn uống thêm một viên aspirin trẻ em vào buổi sáng.",
        "Bác sĩ: Ồ, chú có mấy cháu rồi?",
        "Bác sĩ: Ừ, cô còn trẻ mà, sao lại phải đến khám hôm nay?",
    ):
        assert du_lieu.co_dau_hieu_nhi({"input": cau}) is False, cau


def test_nhan_nhi_van_bat_duoc_ca_nhi_that():
    for cau in (
        "Bác sĩ: Em bé đang sốt rất cao, tôi nghĩ là em bé đang bị co giật do sốt.",
        "Người nhà: Chào bác sĩ, em là mẹ của bé ạ.",
        "Người nhà: Dạ, cháu năm nay 5 tuổi, cháu bị ngã xuống tay phải.",
        "Bác sĩ: Em bé sinh đủ tháng không? Người nhà: Dạ không, bé sinh non ạ.",
    ):
        assert du_lieu.co_dau_hieu_nhi({"input": cau}) is True, cau


# ---------------------------------------------------------------- chia tap

@pytest.fixture(scope="module")
def tap():
    return tach_tap.chia(du_lieu.nap_mau(duong_dan.TRAIN_JSONL))


def test_kich_thuoc_bon_tap(tap):
    assert len(tap["phat_trien"]) == 35
    assert len(tap["kiem_tra_cuoi"]) == 40
    assert len(tap["kiem_tra_chung"]) == 60
    assert sum(len(d) for d in tap.values()) == 1305


def test_khong_ro_ri_giua_cac_tap(tap):
    ids = {t: {m["id"] for m in ds} for t, ds in tap.items()}
    for a in ("phat_trien", "kiem_tra_cuoi", "kiem_tra_chung"):
        assert not (ids[a] & ids["train"]), f"RO RI: {a} nam trong train"
    assert not (ids["phat_trien"] & ids["kiem_tra_cuoi"]), \
        "RO RI: tap phat trien va tap kiem tra cuoi giao nhau"
    assert not (ids["phat_trien"] & ids["kiem_tra_chung"])
    assert not (ids["kiem_tra_cuoi"] & ids["kiem_tra_chung"])


def test_hai_tap_danh_gia_deu_co_nguoi_nha(tap):
    """Do la tap kiem tra CHUYEN BIET cho tinh huong nhieu nguoi noi."""
    for t in ("phat_trien", "kiem_tra_cuoi"):
        assert all(du_lieu.co_nguoi_nha(m) for m in tap[t])


def test_train_van_giu_mau_nguoi_nha(tap):
    """Bo het mau nguoi nha khoi train se lam baseline yeu gia."""
    so = len(du_lieu.loc_mau_co_nguoi_nha(tap["train"]))
    assert so >= 30, f"train chi con {so} mau nguoi nha, qua it"


def test_chia_lai_cung_seed_ra_cung_ket_qua():
    mau = du_lieu.nap_mau(duong_dan.TRAIN_JSONL)
    a = tach_tap.chia(mau, seed=7)
    b = tach_tap.chia(mau, seed=7)
    assert [m["id"] for m in a["phat_trien"]] == [m["id"] for m in b["phat_trien"]]


# ------------------------------------------------- chot bao ve Cua 5

def test_chan_tap_kiem_tra_cuoi():
    """Tap kiem tra cuoi mo som la hong toan bo phan danh gia, va hong theo
    kieu khong lay lai duoc. Mot dong `--tap kiem_tra_cuoi` go nham la du."""
    import pytest
    with pytest.raises(SystemExit):
        du_lieu.chan_tap_khoa("kiem_tra_cuoi")
    with pytest.raises(SystemExit):
        du_lieu.chan_tap_khoa(["phat_trien", "kiem_tra_cuoi"])


def test_chot_khong_chan_nham_tap_thuong():
    """Chieu bao DAT cua chinh phep chan — phai test ca hai chieu."""
    for t in ("phat_trien", "kiem_tra_chung", "train"):
        du_lieu.chan_tap_khoa(t)
    du_lieu.chan_tap_khoa(["phat_trien", "kiem_tra_chung"])
