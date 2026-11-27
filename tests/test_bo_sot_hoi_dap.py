# -*- coding: utf-8 -*-
"""Bo sot trong cap hoi-dap: "BS: Chị có dị ứng thuốc gì không?" / "BN: Dạ có ạ." ma khong
menh de nao dan toi cau tra loi. `doan_chua_ghi` khong thay cap nay (bo cau hoi, va cau
tra loi khong co tu noi dung)."""
from src.duong_ong import b4_kiem_can_cu as kbc
from src.canh_bao import bo_sot
from src.canh_bao.loai import LOAI, THU_NGHIEM
from src.canh_bao.phat_hien import NguCanh
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu

HT = "Bác sĩ: Chị có dị ứng thuốc gì không?\nBệnh nhân: Dạ có ạ."


def test_da_co_khong_ghi():
    ra = kbc.cap_hoi_dap_chua_ghi([], [], kbc._luot(HT))
    assert len(ra) == 1
    assert ra[0]["chu_de"] == "di_ung" and ra[0]["tra_loi"] == "Dạ có ạ."
    assert ra[0]["luot_hoi"] == 1 and ra[0]["luot_dap"] == 2


def test_da_ghi_thi_im():
    ps = [PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="dị ứng thuốc", bang_chung=[2])]
    kq = [kbc.KetQua(id=0)]
    assert kbc.cap_hoi_dap_chua_ghi(kq, ps, kbc._luot(HT)) == []


def test_cau_hoi_khong_dau():
    cac_luot = {1: ("bác sĩ", "chị có dị ứng thuốc gì không"), 2: ("bệnh nhân", "dạ không")}
    ra = kbc.cap_hoi_dap_chua_ghi([], [], cac_luot)
    assert len(ra) == 1 and ra[0]["chu_de"] == "di_ung"


def test_cau_ke_cua_bac_si_khong_phai_cap():
    cac_luot = {1: ("bác sĩ", "Để tôi khám bụng nhé."), 2: ("bệnh nhân", "Dạ vâng.")}
    assert kbc.cap_hoi_dap_chua_ghi([], [], cac_luot) == []


def test_chu_de():
    def cd(hoi):
        return kbc.cap_hoi_dap_chua_ghi([], [], {1: ("bác sĩ", hoi), 2: ("bệnh nhân", "Dạ có.")})[0]["chu_de"]
    assert cd("Anh có đang uống thuốc gì không?") == "thuoc"
    assert cd("Trước giờ có bệnh mạn tính gì không?") == "tien_su"
    assert cd("Có sốt không?") == "trieu_chung"
    assert cd("Nhà mình ở gần đây không?") == "khac"


def test_khoa_ca_tra_ve_cap():
    assert len(kbc.khoa_ca([], HT, bat_buoc_trich_dan=False)["cap_hoi_dap_chua_ghi"]) == 1


def test_bo_sot_sinh_omitted_answer_thu_nghiem():
    cap = kbc.cap_hoi_dap_chua_ghi([], [], kbc._luot(HT))
    cbs = bo_sot.quet(NguCanh(HT), [], [], cap)
    assert [c.ma for c in cbs] == ["OMITTED_ANSWER"]
    assert cbs[0].luot == [1, 2]
    assert LOAI["OMITTED_ANSWER"].tin_cay == THU_NGHIEM


def test_bo_sot_bo_qua_chu_de_khac():
    cap = kbc.cap_hoi_dap_chua_ghi([], [], {1: ("bác sĩ", "Nhà mình ở gần đây không?"),
                                            2: ("bệnh nhân", "Dạ gần ạ.")})
    assert bo_sot.quet(NguCanh(""), [], [], cap) == []
