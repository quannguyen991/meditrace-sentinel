# -*- coding: utf-8 -*-
"""Tang khoa bang chung: chan khi co bang chung PHU DINH, canh bao khi THIEU.

Hai loai test:
  - tung loi mot, tren mot hoi thoai viet tay: khoa bat dung loi, dung ly do
  - tren DAP AN HOAN HAO cua bo sinh (khuon TRAIN): moi lan chan la chan oan
"""
import random

import pytest

from src import khoa_bang_chung as kbc
from src import sinh_hoi_thoai_viet as sh
from src.danh_gia_khoa import (do_bat_loi, phat_bieu_tu_dap_an, thong_ke_khoa,
                               vao_than)
from src.phat_bieu import PhatBieu

HT = ("Bác sĩ: Cháu có dị ứng thuốc gì không chị?\n"
      "Người nhà: Dạ, tôi thì dị ứng penicillin, còn cháu chưa thấy bị bao giờ ạ.\n"
      "Bác sĩ: Tôi nghĩ nhiều đến viêm phổi, nhưng chưa kết luận được.\n"
      "Người nhà: Nếu mai cháu còn sốt thì cho uống thuốc ạ.")


def pb(id_, noi_dung, luot, trich, chu_the_id=0, nguoi_noi="người nhà", **kw):
    return PhatBieu(id=id_, nguoi_noi=nguoi_noi, chu_the_id=chu_the_id,
                    noi_dung=noi_dung, bang_chung=luot, trich_dan=trich, **kw)


def _k(p, ht=HT, **kw):
    return kbc.khoa_ca([p], ht, **kw)["ket_qua"][0]


# ------------------------------------------------------------ tung loi mot

def test_trich_dan_DUNG_thi_qua_khong_canh_bao():
    k = _k(pb(0, "dị ứng penicillin", [2], ["tôi thì dị ứng penicillin"],
              chu_the_id=1, ten_chu_the="mẹ"))
    assert k.qua and not k.canh_bao, k.to_dict()


def test_trich_dan_BIA_thi_chan():
    k = _k(pb(0, "dị ứng aspirin", [2], ["tôi dị ứng aspirin"], chu_the_id=1))
    assert "trich_khong_co" in k.chan


def test_DOI_CHU_THE_bang_tu_TOI_thi_chan():
    """Loi nguy hiem nhat cua du an: di ung cua me thanh di ung cua tre."""
    k = _k(pb(0, "dị ứng penicillin", [2], ["tôi thì dị ứng penicillin"]))
    assert "chu_the_nguoi_ke" in k.chan


def test_chua_ghi_nhan_ghi_thanh_KHANG_DINH_thi_chan():
    k = _k(pb(0, "dị ứng thuốc", [2], ["còn cháu chưa thấy bị bao giờ"]))
    assert "vuot_muc_chua_ghi_nhan" in k.chan


def test_chua_ghi_nhan_ghi_dung_thi_qua():
    k = _k(pb(0, "dị ứng thuốc", [2], ["còn cháu chưa thấy bị bao giờ"],
              do_chac_chan="chưa ghi nhận"))
    assert k.qua, k.to_dict()


def test_NGHI_NGO_nang_thanh_chan_doan_thi_chan():
    k = _k(pb(0, "viêm phổi", [3], ["Tôi nghĩ nhiều đến viêm phổi"],
              nguoi_noi="bác sĩ"))
    assert "vuot_muc_nghi" in k.chan


def test_nghi_ngo_giu_dung_muc_thi_qua():
    k = _k(pb(0, "viêm phổi", [3], ["Tôi nghĩ nhiều đến viêm phổi"],
              nguoi_noi="bác sĩ", do_chac_chan="nghi ngờ"))
    assert k.qua, k.to_dict()


def test_cau_DIEU_KIEN_ghi_thanh_su_that_thi_chan():
    k = _k(pb(0, "sốt", [4], ["Nếu mai cháu còn sốt thì cho uống thuốc ạ"]))
    assert "dieu_kien" in k.chan


def test_cau_dieu_kien_ghi_la_GIA_DINH_thi_khong_chan():
    k = _k(pb(0, "sốt", [4], ["Nếu mai cháu còn sốt thì cho uống thuốc ạ"],
              tinh_huong="giả định"))
    assert "dieu_kien" not in k.chan


def test_KHONG_trich_dan_thi_chan_hoac_canh_bao_theo_che_do():
    """Dau ra cu (truoc the he 5) khong co trich dan — van do duoc, nhung khoa
    chi canh bao chu khong chan."""
    p = pb(0, "dị ứng penicillin", [2], [], chu_the_id=1)
    assert "khong_trich_dan" in _k(p).chan
    assert "khong_trich_dan" in _k(p, bat_buoc_trich_dan=False).canh_bao


def test_luot_KHONG_ton_tai_thi_chan():
    assert "luot_khong_ton_tai" in _k(pb(0, "sốt", [99], ["sốt"])).chan


def test_tu_xung_MO_HO_chi_canh_bao_khong_chan():
    """'em' vua la me tu xung, vua la cach goi benh nhan nguoi lon — khong du de
    chan. Day la gioi han phai vao bao cao."""
    ht = ("Bác sĩ: Gia đình có ai bị gì không?\n"
          "Người nhà: Dạ, em cũng đang bị tăng huyết áp ạ.")
    for chu_the in (0, 1):
        k = _k(pb(0, "tăng huyết áp", [2], ["em cũng đang bị tăng huyết áp ạ"],
                  chu_the_id=chu_the), ht)
        assert k.qua, k.to_dict()


def test_trich_dan_bo_qua_hoa_thuong_khoang_trang_va_dau_cau_hai_dau():
    van = "Dạ, tôi thì  dị ứng penicillin, còn cháu chưa thấy bị bao giờ ạ."
    vt = kbc.tim_trich("TÔI THÌ DỊ ỨNG PENICILLIN.", van)
    assert vt and van[vt[0]:vt[1]] == "tôi thì  dị ứng penicillin"


def test_tra_loi_TAT_lay_noi_dung_tu_cau_hoi():
    ht = "Bác sĩ: Cháu có dị ứng thuốc gì không?\nNgười nhà: Dạ, không ạ."
    k = _k(pb(0, "dị ứng thuốc", [1, 2], ["Cháu có dị ứng thuốc gì không",
                                          "Dạ, không ạ"], phu_dinh=True), ht)
    assert "noi_dung_khong_khop" not in k.canh_bao, k.to_dict()


def test_nghia_CAN_HOI_khong_thanh_dau_rao_don():
    """"nong ham hap" -> nghia can hoi "nong nhieu co the sot". Chu "co the" la
    loi giai thich cua bang chuan hoa, khong phai loi nguoi noi — tung lam khoa
    chan oan "sot" vi "rao don" (hieu chinh 11/09/2026, tap train)."""
    ht = ("Bác sĩ: Anh bị làm sao?\n"
          "Bệnh nhân: Dạ, tôi nóng hầm hập gần một tuần rồi ạ.")
    k = _k(pb(0, "sốt", [2], ["tôi nóng hầm hập gần một tuần rồi ạ"],
              nguoi_noi="bệnh nhân"), ht)
    assert k.qua, k.to_dict()
    assert "phuong_ngu_can_hoi" in k.canh_bao, "chi khop qua tu can hoi"


def test_MINH_trong_tu_ghep_khong_phai_tu_xung():
    """"tro minh ca dem" noi ve tre — 49/49 lan chan oan con lai tren train."""
    ht = ("Bác sĩ: Cháu ngủ thế nào?\n"
          "Người nhà: Dạ, cháu trở mình cả đêm không ngủ nữa ạ.")
    k = _k(pb(0, "khó ngủ", [2], ["trở mình cả đêm không ngủ nữa ạ"]), ht)
    assert "chu_the_nguoi_ke" not in k.chan, k.to_dict()


def test_ANH_CHI_goi_benh_nhan_khong_lui_ve_TOI_o_dau_cau():
    """"toi thi di ung X, con chi chua thay bi bao gio" — trich dan cho trong cua
    benh nhan co "chi"; truoc 11/09/2026 khoa lui ve dau cau, gap "toi", chan oan."""
    for goi in ("chị", "anh", "chú", "cô", "ông"):
        ht = ("Bác sĩ: Có dị ứng thuốc gì không?\n"
              f"Người nhà: Dạ, tôi thì dị ứng penicillin, còn {goi} chưa thấy bị bao giờ ạ.")
        k = _k(pb(0, "dị ứng thuốc", [2], [f"còn {goi} chưa thấy bị bao giờ ạ"],
                  do_chac_chan="chưa ghi nhận"), ht)
        assert k.qua, (goi, k.to_dict())


def test_loi_ke_ve_viec_NOI_NHAM_la_thu_tuc_nhung_cau_co_thong_tin_thi_khong():
    for doan in ("tôi nói nhầm", "em nhầm", "à tôi nhớ nhầm", "tôi không chắc lắm ạ"):
        assert kbc.THU_TUC.search(doan), doan
    assert not kbc.THU_TUC.search("tôi không chắc lắm là bé đã tiêm chưa")


def test_doan_chua_ghi_bat_duoc_thong_tin_BI_BO_SOT():
    ht = ("Bác sĩ: Cháu bị làm sao?\n"
          "Người nhà: Dạ, cháu sốt ba ngày, còn đau bụng nữa ạ.")
    p = pb(0, "sốt", [2], ["cháu sốt ba ngày"])
    dcg = kbc.khoa_ca([p], ht)["doan_chua_ghi"]
    assert any("đau bụng" in d["doan"] for d in dcg), dcg
    assert not any("sốt" in d["doan"] for d in dcg)
    assert not any(d["luot"] == 1 for d in dcg), "cau hoi khong phai thong tin"


# --------------------------------------- tren dap an hoan hao, khuon TRAIN

@pytest.fixture(scope="module")
def bo_train():
    return [sh.sinh_mot_ca(f"t{i:03d}", random.Random(9000 + i),
                           sh.TuyChon(chi_tap="train")) for i in range(400)]


def test_tren_dap_an_HOAN_HAO_chan_oan_KHONG_qua_1_phan_tram(bo_train):
    """Yeu cau dat TRUOC khi do: tren dau vao hoan hao, moi lan chan la chan oan,
    va chan oan la "viet it di" — bay lon nhat cua du an."""
    tk = thong_ke_khoa(bo_train)
    ty_le = tk["so_chan_oan"] / tk["tong_than"]
    assert ty_le <= 0.01, (f"chan oan {tk['so_chan_oan']}/{tk['tong_than']}",
                           tk["chan"], tk["vi_du"])


def test_doi_chu_the_bang_TOI_luon_bi_chan(bo_train):
    """Moi lan doi chu the ma doan dan co "toi" (tu xung khong mo ho) phai bi
    chan — con lai chi co the canh bao, va ty le do phai BAO CAO."""
    ket, _ly = do_bat_loi(bo_train, "doi_chu_the", seed=1)
    assert ket["chan"] > 0


def test_bia_trich_dan_LUON_bi_chan(bo_train):
    ket, ly = do_bat_loi(bo_train, "bia_trich_dan", seed=2)
    assert ket["lot"] == 0 and ket["canh_bao"] == 0, (ket, ly)


def test_gia_dinh_thanh_that_LUON_bi_chan(bo_train):
    ket, ly = do_bat_loi(bo_train, "gia_dinh_thanh_that", seed=3)
    assert ket["chan"] > 0 and ket["lot"] == 0, (ket, ly)
