# -*- coding: utf-8 -*-
"""Test bo cham diem — va chot cung mot quan sat cua du an.

Test `test_hoan_doi_chu_the_van_duoc_diem_cao` khong phai de kiem ma nguon
chay dung. No la mot QUAN SAT ve chinh chi so: hoan doi hai chu the cho nhau
gan nhu khong lam giam diem. Neu test nay hong, phan "phan tich them" cua
du an phai xem lai.
"""
from src import cham_diem

DUNG = "DỊ ỨNG\n\nMẹ dị ứng penicillin. Trẻ chưa ghi nhận dị ứng."
HOAN_DOI = "DỊ ỨNG\n\nTrẻ dị ứng penicillin. Mẹ chưa ghi nhận dị ứng."
VO_HAI = "DỊ ỨNG\n\nMẹ dị ứng penicillin. Trẻ chưa ghi nhận dị ứng thuốc."


def test_giong_het_thi_diem_tuyet_doi():
    assert cham_diem.diem_cuoi(DUNG, DUNG)["final"] == 1.0


def test_hoan_doi_chu_the_van_duoc_diem_cao():
    d = cham_diem.diem_cuoi(HOAN_DOI, DUNG)
    assert d["rouge1"] == 1.0, "tap unigram giong het nen ROUGE-1 phai bang 1"
    assert d["section_f1"] == 1.0, "cung mot section nen Section F1 phai bang 1"
    assert d["final"] > 0.8, f"diem cuoi do duoc {d['final']:.4f}"


def test_diem_van_cao_du_hoan_doi_chu_the():
    """Chi khang dinh dieu do duoc BANG CAU TRUC, khong khang dinh ket luan.

    Ban dau test nay khang dinh "chenh lech cua loi nguy hiem khong lon hon
    bon lan loi vo hai" — va HONG. So do duoc tren vi du nay:

        hoan doi chu the (nguy hiem)  -> chenh lech 0,1061
        them mot tu dong nghia (vo hai) -> chenh lech 0,0247

    Tuc la loi nguy hiem CO ton diem, khoang 4,3 lan loi vo hai. Khong dung
    rang chi so "gan nhu khong doi".

    Bai hoc: test don vi kiem HANH VI CUA MA, khong duoc dung de khang dinh
    truoc mot ket luan nghien cuu chua do. Ket luan that duoc do o Task 18
    tren toan bo tap phat trien va bo chan doan, khong phai tren mot vi du.

    Dieu van dung va dang noi: mot ban benh an co the gay hai van dat 0,89
    tren thang 1,00 — thu hang rat cao trong mot cuoc thi.
    """
    d = cham_diem.diem_cuoi(HOAN_DOI, DUNG)
    assert d["final"] > 0.85, f"diem cuoi = {d['final']:.4f}"

    d_nguy_hiem = 1.0 - d["final"]
    d_vo_hai = 1.0 - cham_diem.diem_cuoi(VO_HAI, DUNG)["final"]
    # Ghi lai de doi chieu ve sau; khong khang dinh quan he giua hai so.
    assert d_nguy_hiem > 0 and d_vo_hai > 0


def test_section_f1_bat_duoc_thieu_muc():
    thieu = "DỊ ỨNG\n\nMẹ dị ứng penicillin."
    day_du = "DỊ ỨNG\n\nMẹ dị ứng penicillin.\n\nTIỀN SỬ GIA ĐÌNH\n\nKhông có gì đặc biệt."
    assert cham_diem.section_f1(thieu, day_du) < 1.0
