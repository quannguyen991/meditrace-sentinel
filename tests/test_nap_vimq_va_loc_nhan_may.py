# -*- coding: utf-8 -*-
import json
import unicodedata

from src.bo_du_lieu import loc_nhan_may as ln
from src.bo_du_lieu import nap_vimq as nv


def _ghi(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False), encoding="utf-8")


def test_doc_vimq_bo_gach_duoi_va_cat_thuc_the_theo_chi_so_tu(tmp_path):
    p = tmp_path / "t.json"
    _ghi(p, [{"sentence": "Hẹp động_mạch thận phải có tiến_hành hiến thận được không ?",
              "seq_label": [[0, 2, "SYMPTOM_AND_DISEASE"], [6, 7, "medical_procedure"]],
              "sent_label": "method_diagnosis"}])
    r = nv.doc_vimq(p, "train")
    assert r[0]["input"] == "Bệnh nhân: Hẹp động mạch thận phải có tiến hành hiến thận được không ?"
    assert r[0]["thuc_the"][0] == {"text": "Hẹp động mạch thận", "loai": "SYMPTOM_AND_DISEASE"}
    assert r[0]["thuc_the"][1]["text"] == "hiến thận"
    assert r[0]["id"] == "vimq_train_00000"


def test_doc_vimq_bo_thuc_the_ngoai_pham_vi_va_cau_rong(tmp_path):
    p = tmp_path / "t.json"
    _ghi(p, [{"sentence": "đau đầu", "seq_label": [[0, 9, "X"], [0, 1, "Y"], ["a", 1, "Z"]]},
             {"sentence": "  "}, {"khong_co_cau": 1}])
    r = nv.doc_vimq(p)
    assert len(r) == 1 and [t["loai"] for t in r[0]["thuc_the"]] == ["Y"]


def test_doc_vimq_khong_phai_danh_sach(tmp_path):
    import pytest
    p = tmp_path / "t.json"
    _ghi(p, {"a": 1})
    with pytest.raises(ValueError):
        nv.doc_vimq(p)


def _md(**kw):
    m = {"chu_the": "bệnh nhân", "noi_dung": "đau đầu", "do_chac_chan": "chắc chắn",
         "luot_thoai": [1], "trich_dan": ["đau đầu"]}
    m.update(kw)
    return m


def test_giu_menh_de_co_trich_dan_that():
    giu, bo = ln.loc_menh_de_may([_md()], "Bệnh nhân: tôi đau đầu ba ngày")
    assert len(giu) == 1 and not bo


def test_bo_trich_dan_khong_co_trong_van_ban_va_ghi_ly_do():
    giu, bo = ln.loc_menh_de_may([_md(trich_dan=["sốt cao"])], "Bệnh nhân: tôi đau đầu")
    assert not giu and "chuoi con" in bo[0]["ly_do"]


def test_bo_khong_co_trich_dan():
    _, bo = ln.loc_menh_de_may([_md(trich_dan=[])], "đau đầu")
    assert bo[0]["ly_do"] == "khong co trich_dan"
    m = _md()
    del m["trich_dan"]
    _, bo = ln.loc_menh_de_may([m], "đau đầu")
    assert bo[0]["ly_do"] == "khong co trich_dan"


def test_nfc_nfd_trich_dan_van_khop():
    nfd = unicodedata.normalize("NFD", "đau đầu")
    giu, _ = ln.loc_menh_de_may([_md(trich_dan=[nfd])], "Bệnh nhân: tôi đau đầu")
    assert len(giu) == 1


def test_bo_thieu_truong_chu_the_rong_va_do_chac_chan_la():
    m1 = _md()
    del m1["luot_thoai"]
    _, bo = ln.loc_menh_de_may([m1, _md(chu_the=" "), _md(do_chac_chan="chắc chắn lắm")], "đau đầu")
    assert [b["ly_do"][:8] for b in bo] == ["thieu tr", "chu_the ", "do_chac_"]


def test_bo_trung_menh_de():
    giu, bo = ln.loc_menh_de_may([_md(), _md(noi_dung="Đau đầu")], "đau đầu")
    assert len(giu) == 1 and bo[0]["ly_do"] == "trung menh de"


def test_phu_thuc_the():
    md = [_md(noi_dung="đau đầu kéo dài ba ngày")]
    r = ln.phu_thuc_the(md, [{"text": "đau đầu"}, {"text": "sốt cao"}])
    assert r == {"so_thuc_the": 2, "so_phu": 1, "ti_le_phu": 0.5}
    assert ln.phu_thuc_the([], [{"text": "x"}])["so_phu"] == 0
    assert ln.phu_thuc_the(md, [])["ti_le_phu"] == 0.0


def test_tong_hop_dem_giu_bo_va_phu():
    from src.bo_du_lieu.gan_nhan_truoc import tong_hop
    mau = [{"id": "a", "input": "Bệnh nhân: tôi đau đầu", "thuc_the": [{"text": "đau đầu"}]},
           {"id": "b", "input": "Bệnh nhân: sốt", "thuc_the": [{"text": "sốt"}]},
           {"id": "c", "input": "Bệnh nhân: ho", "thuc_the": []}]
    kq = {"a": {"json_hop_le": True, "phat_bieu": [_md()]},
          "b": {"json_hop_le": False, "phat_bieu": [_md(noi_dung="sốt", trich_dan=["sốt cao"])]}}
    r = tong_hop(mau, kq)
    tk = r["thong_ke"]
    assert tk["so_mau"] == 3 and tk["so_co_ket_qua"] == 2 and tk["so_json_loi"] == 1
    assert tk["so_menh_de_may"] == 2 and tk["so_menh_de_giu"] == 1
    assert tk["ly_do_bo"] == {"trich_dan khong phai chuoi con cua van ban": 1}
    assert tk["phu_truoc_loc"]["ti_le"] == 1.0 and tk["phu_sau_loc"]["ti_le"] == 0.5
    assert [x["id"] for x in r["giu"]] == ["a"]
    assert r["giu"][0]["nhan"] == "may-chua-kiem" and r["giu"][0]["nguon"] == "vimq"
