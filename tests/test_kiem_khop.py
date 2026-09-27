# -*- coding: utf-8 -*-
"""Tep dem trich phai KHOP voi bo du lieu dang cham.

VI SAO CO TEP NAY (10/09/2026).

Bo du lieu duoc sinh lai tu 3.000 ca len 5.000 ca. `viet_phat_trien.jsonl` bi
ghi de bang tap phat trien MOI, con tep dem trich van la cua bo cu. Ma ca la
`hv_xxxx` o CA HAI bo, nen id khop het.

Phep do chay tron tru va cho ra mot bang so hoan toan vo nghia:

    do tren bo cu    ca co quan he that: 16/60
    sau khi sinh lai ca co quan he that:  1/60    <- so cua mot bo khac

Khong JSON hong, khong ngoai le, khong dong canh bao. Neu khong tinh co doi
chieu voi lan do truoc thi con so do da vao bao cao.

Day la loi im lang thu BA cung ho trong du an nay:
  1. ra_A (co adapter) va ra_A (khong adapter) de len nhau
  2. ra_B/C/D (co adapter trich) de len ban khong adapter
  3. tep dem cua bo du lieu nay dung de cham bo du lieu khac
"""
import pytest

from src import bakeoff


def _ca(id, so_luot):
    return {"id": id, "input": "\n".join(f"Bác sĩ: câu {i}"
                                         for i in range(so_luot))}


def _tho(id, so_luot):
    return {"id": id, "so_luot": so_luot, "phat_bieu": []}


def test_khop_thi_khong_nem_loi():
    mau = {"hv_0001": _ca("hv_0001", 12), "hv_0002": _ca("hv_0002", 9)}
    tho = [_tho("hv_0001", 12), _tho("hv_0002", 9)]
    bakeoff.kiem_khop(mau, tho)          # khong duoc nem loi


def test_lech_so_luot_thi_nem_loi():
    """Hai bo du lieu khac nhau gan nhu khong bao gio cung so luot o moi ca."""
    mau = {"hv_0001": _ca("hv_0001", 12)}
    tho = [_tho("hv_0001", 15)]
    with pytest.raises(SystemExit) as e:
        bakeoff.kiem_khop(mau, tho)
    assert "hv_0001" in str(e.value)


def test_ca_khong_co_trong_dap_an_thi_nem_loi():
    mau = {"hv_0001": _ca("hv_0001", 12)}
    tho = [_tho("hv_0001", 12), _tho("hv_9999", 10)]
    with pytest.raises(SystemExit) as e:
        bakeoff.kiem_khop(mau, tho)
    assert "hv_9999" in str(e.value)


def test_thong_bao_neu_ten_tep_dem():
    """Nguoi gap loi phai biet NGAY tep nao sai, khong phai di do."""
    with pytest.raises(SystemExit) as e:
        bakeoff.kiem_khop({}, [_tho("hv_0001", 5)], "trich_abc_3072.jsonl")
    assert "trich_abc_3072.jsonl" in str(e.value)


def test_thong_bao_cat_bot_khi_lech_nhieu():
    """Lech ca tram cho thi in het ra la vo dung. Nhung phai noi ro con bao
    nhieu, khong duoc im lang cat."""
    mau = {f"hv_{i:04d}": _ca(f"hv_{i:04d}", 10) for i in range(20)}
    tho = [_tho(f"hv_{i:04d}", 11) for i in range(20)]
    with pytest.raises(SystemExit) as e:
        bakeoff.kiem_khop(mau, tho)
    tin = str(e.value)
    assert "va 15 cho nua" in tin


def test_tho_rong_thi_khong_nem_loi():
    """Chua trich mau nao thi khong co gi de doi chieu — khong phai loi."""
    bakeoff.kiem_khop({"hv_0001": _ca("hv_0001", 12)}, [])


def test_dong_trong_khong_tinh_la_luot():
    """`danh_so_luot` bo dong trong, nen phep dem o day phai bo giong het —
    khong thi chot bao dong gia tren moi tep."""
    mau = {"hv_0001": {"id": "hv_0001",
                       "input": "Bác sĩ: a\n\n\nBệnh nhân: b\n"}}
    bakeoff.kiem_khop(mau, [_tho("hv_0001", 2)])


# ------------------------------------- chay tiep khong duoc dung lai ban lech

def _viet_dem(tmp_path, ban_ghi):
    import json
    p = tmp_path / "dem.jsonl"
    p.write_text("\n".join(json.dumps(b, ensure_ascii=False) for b in ban_ghi),
                 encoding="utf-8")
    return p


def test_chay_tiep_bo_ban_ghi_lech_so_luot(tmp_path, capsys):
    """Tep dem cua bo du lieu KHAC phai bi bo, khong duoc dung lai.

    Id la `hv_xxxx` o moi bo tu sinh, nen khong kiem `so_luot` thi mot tep dem
    cua bo 3.000 se duoc dung nguyen cho bo 5.000.
    """
    mau = [{"id": "hv_0001", "input": "Bác sĩ: a\nBệnh nhân: b"}]
    dem = _viet_dem(tmp_path, [
        {"id": "hv_0001", "so_luot": 9, "phat_bieu": [], "json_hop_le": True},
    ])
    goi = {}

    def _gia(tok, model, prefix_fn, mau_list, max_token, vi_du, da_co, tep, kq):
        goi["da_co"] = dict(da_co)
        return kq

    import src.bakeoff as bk
    that = bk._vong_trich
    bk._vong_trich = _gia
    try:
        bk.trich(None, None, None, mau, luu_dan=str(dem))
    finally:
        bk._vong_trich = that

    assert goi["da_co"] == {}, "da dung lai ban ghi cua bo du lieu khac"
    assert "BO 1 mau" in capsys.readouterr().out


def test_chay_tiep_giu_ban_ghi_khop(tmp_path):
    mau = [{"id": "hv_0001", "input": "Bác sĩ: a\nBệnh nhân: b"}]
    dem = _viet_dem(tmp_path, [
        {"id": "hv_0001", "so_luot": 2, "phat_bieu": [], "json_hop_le": True},
    ])
    goi = {}

    def _gia(tok, model, prefix_fn, mau_list, max_token, vi_du, da_co, tep, kq):
        goi["da_co"] = dict(da_co)
        return kq

    import src.bakeoff as bk
    that = bk._vong_trich
    bk._vong_trich = _gia
    try:
        bk.trich(None, None, None, mau, luu_dan=str(dem))
    finally:
        bk._vong_trich = that
    assert "hv_0001" in goi["da_co"], "ban ghi khop ma van bi bo"
