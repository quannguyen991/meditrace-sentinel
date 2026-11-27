# -*- coding: utf-8 -*-
"""Loss theo doan phai BANG loss tinh mot lan tren toan bo logits."""
from types import SimpleNamespace

import pytest

torch = pytest.importorskip("torch")
import torch.nn.functional as F  # noqa: E402

from src.huan_luyen.loss_theo_doan import (bo_mat_na_day_du,  # noqa: E402
                                cross_entropy_theo_doan,
                                tao_trainer_loss_theo_doan)


def _day_du(hidden, lm_head, nhan):
    v = lm_head.out_features
    return F.cross_entropy(lm_head(hidden).reshape(-1, v), nhan.reshape(-1),
                           ignore_index=-100)


def _du_lieu(T, V=50, H=16, bo=0, seed=0):
    torch.manual_seed(seed)
    hidden = torch.randn(1, T, H, requires_grad=True)
    lm_head = torch.nn.Linear(H, V, bias=False)
    nhan = torch.randint(0, V, (1, T))
    nhan[0, :bo] = -100
    return hidden, lm_head, nhan


def test_bang_loss_day_du():
    hidden, lm_head, nhan = _du_lieu(1000, bo=100)
    a = _day_du(hidden, lm_head, nhan)
    b = cross_entropy_theo_doan(hidden, lm_head, nhan, kich_thuoc_doan=512)
    assert torch.allclose(a, b, atol=1e-6)


def test_gradient_bang_nhau():
    hidden, lm_head, nhan = _du_lieu(1000, bo=100)
    _day_du(hidden, lm_head, nhan).backward()
    g_h, g_w = hidden.grad.clone(), lm_head.weight.grad.clone()
    hidden.grad = None
    lm_head.weight.grad = None
    cross_entropy_theo_doan(hidden, lm_head, nhan, kich_thuoc_doan=512).backward()
    assert torch.allclose(hidden.grad, g_h, atol=1e-6)
    assert torch.allclose(lm_head.weight.grad, g_w, atol=1e-6)


def test_toan_bo_nhan_bo_qua():
    hidden, lm_head, nhan = _du_lieu(700)
    nhan[:] = -100
    loss = cross_entropy_theo_doan(hidden, lm_head, nhan, 512)
    assert float(loss) == 0.0 and torch.isfinite(loss)
    loss.backward()


def test_mot_doan_toan_bo_qua_nhung_doan_khac_khong():
    # Doan dau (512 token) chi co loi bac si (nhan -100): khong duoc NaN.
    hidden, lm_head, nhan = _du_lieu(1100, bo=512)
    a = _day_du(hidden, lm_head, nhan)
    b = cross_entropy_theo_doan(hidden, lm_head, nhan, 512)
    assert torch.isfinite(b) and torch.allclose(a, b, atol=1e-6)


@pytest.mark.parametrize("T", [1, 2, 511, 512, 513, 1025])
def test_do_dai_khong_chia_het(T):
    hidden, lm_head, nhan = _du_lieu(T)
    a = _day_du(hidden, lm_head, nhan)
    b = cross_entropy_theo_doan(hidden, lm_head, nhan, 512)
    assert torch.allclose(a, b, atol=1e-6)


def test_kich_thuoc_doan_khong_hop_le():
    hidden, lm_head, nhan = _du_lieu(10)
    with pytest.raises(ValueError):
        cross_entropy_theo_doan(hidden, lm_head, nhan, 0)


def test_trainer_loss_theo_doan_bang_loss_goc():
    torch.manual_seed(1)
    V, H, T = 40, 8, 30
    lm_head = torch.nn.Linear(H, V, bias=False)
    nhung = torch.nn.Embedding(V, H)

    def than(input_ids, attention_mask=None):
        return SimpleNamespace(last_hidden_state=nhung(input_ids))

    than_fn = than
    goc = SimpleNamespace(model=than_fn, lm_head=lm_head)
    model = SimpleNamespace(base_model=SimpleNamespace(model=goc))

    class Trainer:  # lop cha gia
        pass

    lop = tao_trainer_loss_theo_doan(Trainer, kich_thuoc_doan=8)
    ids = torch.randint(0, V, (1, T))
    nhan = ids.clone()
    nhan[0, :5] = -100
    loss = lop().compute_loss(model, {"input_ids": ids, "labels": nhan,
                                      "attention_mask": torch.ones_like(ids)})
    mong_doi = F.cross_entropy(lm_head(nhung(ids))[:, :-1].reshape(-1, V),
                               nhan[:, 1:].reshape(-1), ignore_index=-100)
    assert torch.allclose(loss, mong_doi, atol=1e-6)
    # Buoc eval cua Trainer goi voi return_outputs=True va doc outputs nhu dict.
    loss2, outputs = lop().compute_loss(
        model, {"input_ids": ids, "labels": nhan,
                "attention_mask": torch.ones_like(ids)}, return_outputs=True)
    assert torch.allclose(loss2, mong_doi, atol=1e-6)
    assert isinstance(outputs, dict)


def test_bo_mat_na_day_du():
    assert bo_mat_na_day_du(None) is None
    assert bo_mat_na_day_du(torch.ones(1, 5, dtype=torch.long)) is None
    co_dem = torch.tensor([[1, 1, 0]])
    assert bo_mat_na_day_du(co_dem) is co_dem
