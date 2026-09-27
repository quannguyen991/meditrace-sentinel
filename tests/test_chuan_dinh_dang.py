# -*- coding: utf-8 -*-
"""Chuan hoa dinh dang tieu de — va phep thu cong bang cua no.

VI SAO CAN. `section_f1` cua nhanh `A nen` la 0,0000 dung bang khong tren ca 60
ca, vi mo hinh sinh thang viet tieu de kieu Markdown (`**Benh su:**`) con ban
tham chieu viet chu hoa (`BENH SU HIEN TAI`). `cham_diem.cac_muc` chi nhan dong
VIET HOA TOAN BO, nen mau so trong rong.

Diem gop la 0,6 x ROUGE + 0,4 x SectionF1, nen nhanh A bi chan tran o 0,6 chi vi
cach viet tieu de.

PHEP THU QUAN TRONG NHAT O DAY la phep thu CONG BANG: chuan hoa phai la phep dong
nhat tren ban nhap da dung ten muc chuan. Neu no doi nhanh B/C/D thi no khong con
la "bo tat dinh dang" ma thanh "dieu chinh de mot nhanh trong hon".
"""
import json
from pathlib import Path

import pytest

from src import chuan_dinh_dang as cd
from src import sinh_benh_an


# -------------------------------------------- PHEP THU CONG BANG

def test_CONG_BANG_dong_nhat_tren_ten_muc_chuan():
    """Moi ten muc chuan phai di qua chuan hoa ma khong doi mot ky tu."""
    for m in cd.MUC_CHUAN:
        assert cd.chuan_hoa(m) == m, m
    van = "\n\n".join(f"{m}\n\nMot cau nao do." for m in sinh_benh_an.THU_TU_MUC)
    assert cd.chuan_hoa(van) == van


@pytest.mark.parametrize("nhanh", ["B", "C", "D"])
def test_CONG_BANG_khong_doi_ban_nhap_cua_duong_ong(nhanh):
    """Do tren du lieu THAT. Mot phep chuan hoa lam doi ban nhap cua duong ong
    la mot phep chuan hoa dang dieu chinh ket qua, khong phai dang bo tat."""
    p = Path(f"data/ra_{nhanh}_viet_phat_trien_th2.jsonl")
    if not p.exists():
        pytest.skip(f"chua co {p}")
    doi = 0
    r = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    for x in r:
        if cd.chuan_hoa(x["du_doan"]) != x["du_doan"]:
            doi += 1
    assert doi == 0, f"{nhanh}: chuan hoa doi {doi}/{len(r)} ban nhap"


def test_CONG_BANG_khong_doi_ban_tham_chieu():
    p = Path("data/ra_B_viet_phat_trien_th2.jsonl")
    if not p.exists():
        pytest.skip("chua co du lieu")
    for x in (json.loads(l) for l in open(p, encoding="utf-8") if l.strip()):
        assert cd.chuan_hoa(x["tham_chieu"]) == x["tham_chieu"]


# -------------------------------------------- nhan dang bien the

@pytest.mark.parametrize("dong,mong", [
    ("**Bệnh sử:**", "BỆNH SỬ HIỆN TẠI"),
    ("Bệnh sử:", "BỆNH SỬ HIỆN TẠI"),
    ("- **Khám lâm sàng:**", "KHÁM LÂM SÀNG"),
    ("## Chẩn đoán", "CHẨN ĐOÁN"),
    ("Kế hoạch điều trị:", "KẾ HOẠCH ĐIỀU TRỊ"),
    ("tiền sử gia đình", "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI"),
])
def test_nhan_ra_bien_the_tieu_de(dong, mong):
    assert cd.la_tieu_de_bien_the(dong) == mong


@pytest.mark.parametrize("dong", [
    "Bệnh nhân đau bụng quanh rốn trong khoảng 3 tháng.",
    "Kế hoạch điều trị gồm ba việc sau đây, mong anh thực hiện đầy đủ cho cháu",
    "",
    "- Bệnh nhân ngủ không yên, da xanh.",
])
def test_KHONG_bat_nham_cau_thanh_tieu_de(dong):
    """Mot cau dai co chua ten muc khong phai la mot tieu de. Bat nham thi ban
    nhap bi chat mat mot cau va phep do cho diem sai theo."""
    assert cd.la_tieu_de_bien_the(dong) is None


def test_dong_qua_dai_khong_phai_tieu_de():
    dai = "Kế hoạch " + "x" * cd.DAI_TOI_DA
    assert cd.la_tieu_de_bien_the(dai) is None


# -------------------------------------------- bo dam va gach dau dong

def test_bo_dam_Markdown_o_dong_noi_dung():
    """Khong bo thi phep tach menh de coi "**" la mot tu."""
    assert "**" not in cd.chuan_hoa("- **Bệnh nhân** sốt hai hôm")


def test_bo_gach_dau_dong_giu_noi_dung():
    assert cd.chuan_hoa("- Bệnh nhân sốt") == "Bệnh nhân sốt"


def test_giu_nguyen_so_dong():
    """Chuan hoa khong duoc them hay bot dong: thu tu dong quyet dinh thu tu cum
    trong ban nhap, va phep cham doc theo muc."""
    van = "**Bệnh sử:**\n\n- A\n- B\n\n**Chẩn đoán:**\n\n- C"
    assert len(cd.chuan_hoa(van).split("\n")) == len(van.split("\n"))


# -------------------------------------------- bang dong nghia phai lanh manh

def test_moi_dong_nghia_tro_ve_MOT_ten_muc_chuan():
    hop_le = set(cd.MUC_CHUAN) | {sinh_benh_an.MUC_PHU}
    for khoa, ten in cd.DONG_NGHIA.items():
        assert ten in hop_le, (khoa, ten)


def test_khong_dong_nghia_nao_trung_voi_ten_chuan_da_bo_dau():
    """Doi chung: neu mot khoa dong nghia lai chinh la ten chuan thi bang nay
    dang lam mot viec ma `cham_diem` da lam, va no se che mat loi that."""
    for m in cd.MUC_CHUAN:
        assert cd.chuan_hoa(m) == m
