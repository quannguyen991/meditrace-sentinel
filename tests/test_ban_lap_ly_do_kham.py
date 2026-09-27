# -*- coding: utf-8 -*-
"""Ban sao LY DO KHAM khong vao nhan huan luyen — no chi day mo hinh viet trung."""
import json
import random

from src import du_lieu_trich
from src import sinh_hoi_thoai_viet as sh


def test_chi_bo_ban_SAO_giu_ly_do_kham_khong_co_ban_sinh_doi():
    da = [{"chu_the": "bệnh nhân", "noi_dung": "sốt", "muc": "BỆNH SỬ HIỆN TẠI"},
          {"chu_the": "bệnh nhân", "noi_dung": "sốt", "muc": "LÝ DO KHÁM BỆNH"},
          {"chu_the": "bệnh nhân", "noi_dung": "ho", "muc": "LÝ DO KHÁM BỆNH"}]
    assert du_lieu_trich.ban_lap_ly_do_kham(da) == {1}


def test_nhan_huan_luyen_bo_DUNG_ban_sao_ly_do_kham_va_giu_quan_he():
    """Khong kiem bang "khong co hai phat bieu trung chu the, noi dung, luot": hai
    ban cua mot lan dinh chinh / mau thuan / dien bien CUNG dan mot cap luot va
    chi khac moc thoi gian — do la cap THAT (do 11/09/2026: 19/40 ca co cap nhu the)."""
    for i in range(40):
        ca = sh.sinh_mot_ca(f"t{i}", random.Random(300 + i), sh.TuyChon(chi_tap="train"))
        lap = du_lieu_trich.ban_lap_ly_do_kham(ca["dap_an"])
        assert len(lap) == 1, "moi ca bo sinh co dung mot ban sao ly do kham"
        _ds, js = du_lieu_trich.doi_mot_ca(ca)
        ps = json.loads(js)["phat_bieu"]
        giu = [j for j, m in enumerate(ca["dap_an"]) if j not in lap and m.get("luot")]
        assert [p["noi_dung"] for p in ps] == \
               [ca["dap_an"][j]["noi_dung"] for j in giu], ca["id"]
        # Quan he tro DUNG ban ghi sau khi bo ban sao (khong so noi dung: "bo sung"
        # noi hai noi dung khac nhau — "ngay" va "ngay tang len khi van dong").
        moi = {j: k for k, j in enumerate(giu)}
        for p, j in zip(ps, giu):
            dich = ca["dap_an"][j].get("quan_he_voi")
            if ca["dap_an"][j].get("quan_he") and dich in moi:
                assert p["quan_he_voi"] == moi[dich], ca["id"]
