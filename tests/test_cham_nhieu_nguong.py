from src.do_luong.cham_nhieu_nguong import cham_o_cac_nguong
from src.do_luong.cham_he_thong import ghep_menh_de
from src.do_luong.do_trich import ghep


def test_nhieu_nguong():
    du_doan = [{"noi_dung": "a b e f"}]
    dap_an = [{"noi_dung": "a b c d"}]
    kq = cham_o_cac_nguong(du_doan, dap_an)
    for nguong in (0.4, 0.5):
        assert kq[nguong] == {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    for nguong in (0.6, 0.7):
        assert kq[nguong] == {"precision": 0.0, "recall": 0.0, "f1": 0.0}


def test_nguong_mac_dinh_khong_doi():
    dap_an = [{"noi_dung": "a b c d"}, {"noi_dung": "đau ngực"}]
    du_doan = [{"noi_dung": "a b e f"}, {"noi_dung": "đau ngực"}]
    cap, thieu, thua = ghep(dap_an, du_doan)
    assert (len(cap), len(thieu), len(thua)) == (1, 1, 1)
    assert ghep(dap_an, du_doan) == ghep(dap_an, du_doan, nguong=0.6)
    assert ghep_menh_de(dap_an, du_doan) == {1: 1}
    assert ghep_menh_de(dap_an, du_doan) == ghep_menh_de(dap_an, du_doan, nguong=0.6)
    assert cham_o_cac_nguong(du_doan, dap_an)[0.6]["f1"] == 0.5
