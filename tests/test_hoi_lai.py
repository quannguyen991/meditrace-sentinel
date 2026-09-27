# -*- coding: utf-8 -*-
"""Tang hoi lai: it cau hoi, dung cho nguy hiem, mot cau giai quyet nhieu cho."""
from src import cap_nhat
from src import cong_rui_ro as cr
from src import hoi_lai
from src import khoa_bang_chung as kbc
from src.phat_bieu import PhatBieu

HT = ("Bác sĩ: Anh sốt mấy hôm rồi?\n"
      "Người nhà: Dạ, ông ấy sốt bốn ngày rồi ạ.\n"
      "Bệnh nhân: Không đúng đâu, tôi sốt hai ngày rồi.\n"
      "Bác sĩ: Anh có dị ứng thuốc gì không?\n"
      "Người nhà: Dạ, tôi thì dị ứng penicillin, còn ông ấy chưa thấy bị bao giờ ạ.")


def _chuan_bi():
    ps = [
        PhatBieu(id=0, nguoi_noi="người nhà", chu_the_id=0, noi_dung="sốt",
                 bang_chung=[2], moc_thoi_gian="bốn ngày",
                 trich_dan=["ông ấy sốt bốn ngày rồi ạ"]),
        # mo hinh tuong la dinh chinh — nhung la HAI nguoi noi
        PhatBieu(id=1, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="sốt",
                 bang_chung=[3], moc_thoi_gian="hai ngày",
                 trich_dan=["tôi sốt hai ngày rồi"], quan_he="đính chính",
                 quan_he_voi=0),
        PhatBieu(id=2, nguoi_noi="người nhà", chu_the_id=1, ten_chu_the="vợ",
                 noi_dung="dị ứng penicillin", bang_chung=[5],
                 trich_dan=["tôi thì dị ứng penicillin"]),
        PhatBieu(id=3, nguoi_noi="người nhà", chu_the_id=0,
                 noi_dung="dị ứng thuốc", bang_chung=[5],
                 do_chac_chan="chưa ghi nhận",
                 trich_dan=["còn ông ấy chưa thấy bị bao giờ ạ"]),
    ]
    ps = cap_nhat.ap_luat(ps)
    dg = cr.cham(ps, kbc.khoa_ca(ps, HT)["ket_qua"])
    return ps, dg


def test_hai_nguon_khac_nhau_thanh_MOT_cau_hoi_cho_CA_CAP():
    ps, dg = _chuan_bi()
    cau = [c for c in hoi_lai.ung_vien(ps, dg) if c.ly_do == "mau_thuan"]
    assert len(cau) == 1 and set(cau[0].muc_tieu) == {0, 1}
    assert "bốn ngày" in cau[0].van and "hai ngày" in cau[0].van


def test_cho_trong_di_ung_hoi_DUNG_chat_cua_nguoi_nha():
    """Vi du cua ban de xuat: "di ung penicillin la cua me; con tre da tung dung
    penicillin lan nao chua?" — hoi dung cho trong, khong hoi lai tat ca."""
    ps, dg = _chuan_bi()
    cau = [c for c in hoi_lai.ung_vien(ps, dg)
           if c.ly_do == "di_ung_chua_ghi_nhan"]
    assert cau and "penicillin" in cau[0].van and 3 in cau[0].muc_tieu


def test_chon_KHONG_qua_ba_cau_va_uu_tien_LOI_ICH():
    ps, dg = _chuan_bi()
    chon = hoi_lai.chon(hoi_lai.ung_vien(ps, dg))
    assert 1 <= len(chon) <= hoi_lai.TOI_DA
    assert chon[0].ly_do == "mau_thuan"


def test_chon_tham_lam_theo_loi_ich_CON_LAI():
    """Cau B chi phu cho da duoc A phu — loi ich con lai bang 0, khong chon."""
    a = hoi_lai.CauHoi("A", "x", {1: 1.0, 2: 1.0})
    b = hoi_lai.CauHoi("B", "x", {2: 1.0})
    c = hoi_lai.CauHoi("C", "x", {3: 0.5})
    assert [q.van for q in hoi_lai.chon([b, a, c])] == ["A", "C"]


def test_KHONG_hoi_ve_phat_bieu_da_kiem_chung():
    """Tru cau hoi di ung: no chu dinh gom ca cho trong "chua ghi nhan", ke ca
    khi cho do da qua khoa — vi hoi mot cau la lap duoc cho trong."""
    ps, dg = _chuan_bi()
    sach = {d.id for d in dg if d.nhom == cr.DA_KIEM_CHUNG}
    for c in hoi_lai.ung_vien(ps, dg):
        if c.ly_do == "di_ung_chua_ghi_nhan":
            continue
        assert not (set(c.muc_tieu) & sach), c.to_dict()
