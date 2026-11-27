# -*- coding: utf-8 -*-
"""Phan khong can GPU cua `src.huan_luyen.huan_luyen_dpo`: chon cap chia deu, mat na nhan, nap cap, loss."""
import json
import math

import pytest

from src.huan_luyen import huan_luyen_dpo as td
from tests.test_train_baseline import TokGia


def _cap(i, loai, bien_the=0):
    return {"id": f"c{i}", "bien_the": bien_the, "chosen": f"dung{i}", "rejected": f"sai{i}",
            "loi": [{"loai": loai}]}


def test_chon_cap_chia_deu_theo_loai():
    ds = [_cap(i, "nhieu") for i in range(100)] + [_cap(100 + i, "hiem") for i in range(5)]
    ra = td.chon_cap(ds, 10)
    dem = {}
    for c in ra:
        dem[td.loai_cap(c)] = dem.get(td.loai_cap(c), 0) + 1
    assert dem == {"nhieu": 5, "hiem": 5}


def test_chon_cap_het_loai_hiem_thi_lay_tiep_loai_con_lai():
    ds = [_cap(i, "nhieu") for i in range(100)] + [_cap(100 + i, "hiem") for i in range(2)]
    ra = td.chon_cap(ds, 10)
    assert len(ra) == 10
    assert sum(td.loai_cap(c) == "hiem" for c in ra) == 2


def test_chon_cap_tat_dinh_va_khong_trung():
    ds = [_cap(i, l) for i, l in enumerate(["a", "b", "c"] * 20)]
    a, b = td.chon_cap(ds, 30, seed=7), td.chon_cap(ds, 30, seed=7)
    assert [c["id"] for c in a] == [c["id"] for c in b]
    assert len({c["id"] for c in a}) == 30


def test_dung_mau_mat_na_che_phan_nhac():
    tok = TokGia()
    ids, nhan = td.dung_mau(tok, "hoi", "TRA LOI", 1000)
    phan = "".join(chr(t) for t in nhan if t != -100)
    assert phan == "TRA LOI<E>"
    assert len(ids) == len(nhan)


def test_dung_mau_qua_dai_tra_none():
    assert td.dung_mau(TokGia(), "hoi", "x" * 50, 20) is None


def test_nap_cap_bo_cap_khong_co_nhac_va_cap_qua_dai(tmp_path):
    cap = tmp_path / "cap.jsonl"
    nhac = tmp_path / "nhac.jsonl"
    ds = [_cap(1, "a"), _cap(2, "b"), _cap(3, "a")]
    ds[2]["chosen"] = "y" * 500
    cap.write_text("\n".join(json.dumps(c) for c in ds + [_cap(9, "a")]), encoding="utf-8")
    nhac.write_text("\n".join(json.dumps({"id": f"c{i}", "input": "h"}) for i in (1, 2, 3)),
                    encoding="utf-8")
    # loi nhac he thong trich ~240 ky tu: 400 du cho cap ngan, thieu cho cap 500 ky tu
    mau, bo = td.nap_cap(cap, nhac, TokGia(), 400, 10)
    assert sorted(m["khoa"] for m in mau) == ["c1#0", "c2#0"]
    assert bo == 1


def test_ghep_lo_dem_phai_nhan_dem_bi_bo_qua():
    ids, nhan, mat = td.ghep_lo([([1, 2, 3], [-100, 2, 3]), ([4, 5], [-100, 5])], ma_dem=0)
    assert ids == [[1, 2, 3], [4, 5, 0]]
    assert nhan == [[-100, 2, 3], [-100, 5, -100]]
    assert mat == [[1, 1, 1], [1, 1, 0]]


def test_ghep_lo_cung_do_dai_mat_na_toan_mot():
    _ids, _nhan, mat = td.ghep_lo([([1, 2], [-100, 2]), ([3, 4], [-100, 4])], ma_dem=0)
    assert all(all(x == 1 for x in r) for r in mat)


def _m(a, b):
    return {"tot": ([0] * a, [0] * a), "xau": ([0] * b, [0] * b)}


def test_nen_ghep_theo_nguong_va_tat():
    assert td.nen_ghep({"nguong": 100}, _m(90, 100))
    assert not td.nen_ghep({"nguong": 100}, _m(90, 101))
    assert not td.nen_ghep(None, _m(1, 1))


def test_ha_nguong_sau_khi_tran_chi_giam_khong_tang():
    g = {"nguong": 4096}
    td.ha_nguong(g, _m(3000, 3100))
    assert g["nguong"] == 3099
    assert not td.nen_ghep(g, _m(3100, 10))
    td.ha_nguong(g, _m(3500, 3500))  # cap dai hon khong lam nguong tang lai
    assert g["nguong"] == 3099


def test_bam_mau_doi_khi_token_doi():
    a, b = _m(3, 4), _m(3, 4)
    assert td.bam_mau(a) == td.bam_mau(b)
    b["xau"] = ([1, 0, 0, 0], [0] * 4)
    assert td.bam_mau(a) != td.bam_mau(b)


def test_gan_bang_chap_nhan_sai_so_bf16_nhung_khong_qua_lon():
    assert td.gan_bang(-23.769, -23.680)
    assert td.gan_bang(-0.051, -0.050)
    assert not td.gan_bang(-30.0, -23.0)


def _L(lt, lx, rt, rx, beta, alpha, n):
    z = beta * ((lt - rt) - (lx - rx))
    return -math.log(1 / (1 + math.exp(-z))) + alpha * (-lt / n)


@pytest.mark.parametrize("lt,lx", [(-10.0, -12.0), (-3.0, -1.0), (-0.05, -9.8)])
def test_he_so_dpo_bang_dao_ham_so(lt, lx):
    rt, rx, beta, alpha, n, h = -11.0, -11.5, 0.1, 1.0, 40, 1e-5
    z = beta * ((lt - rt) - (lx - rx))
    he_tot, he_xau = td.he_so_dpo(z, beta, alpha, n)
    so_tot = (_L(lt + h, lx, rt, rx, beta, alpha, n) - _L(lt - h, lx, rt, rx, beta, alpha, n)) / (2 * h)
    so_xau = (_L(lt, lx + h, rt, rx, beta, alpha, n) - _L(lt, lx - h, rt, rx, beta, alpha, n)) / (2 * h)
    assert math.isclose(he_tot, so_tot, rel_tol=1e-5)
    assert math.isclose(he_xau, so_xau, rel_tol=1e-5)


def test_loss_dpo_bang_cong_thuc():
    torch = pytest.importorskip("torch")
    lt, lx, rt, rx, nll = map(torch.tensor, (-10.0, -12.0, -11.0, -11.0, 0.5))
    loss, le = td.loss_dpo(lt, lx, rt, rx, nll, beta=0.1, alpha=1.0)
    z = 0.1 * ((-10 + 11) - (-12 + 11))
    assert math.isclose(le.item(), z, rel_tol=1e-6)
    assert math.isclose(loss.item(), -math.log(1 / (1 + math.exp(-z))) + 0.5, rel_tol=1e-6)
