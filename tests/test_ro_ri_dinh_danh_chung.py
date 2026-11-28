# -*- coding: utf-8 -*-
"""Bộ ca rò rỉ định danh DÙNG CHUNG cho hai bộ che (Python ở đây, TypeScript ở
web/may-chu/an-danh-chung.test.ts). Fixture: tests/fixtures/ro_ri_dinh_danh.json,
mỗi ca {"van", "cam", "giu"}.

Đạt khi: câu bị từ chối (kiem_tra_con_sot khác rỗng) HOẶC mọi chuỗi `cam` vắng mặt trong văn bản
đã che; và khi không từ chối, mọi chuỗi `giu` còn nguyên.
"""
import json
from pathlib import Path

import pytest

from src.he_thong.khu_dinh_danh import ClinicalDeidentifier

FIXTURE = Path(__file__).parent / "fixtures" / "ro_ri_dinh_danh.json"
CA = json.loads(FIXTURE.read_text(encoding="utf-8"))

# Chỉ số các ca đang lọt (Task 2 ghi lại, Task 3 gỡ): rỗng = mọi ca phải đạt.
DANG_LOT: set = set()


def _tham_so():
    for i, ca in enumerate(CA):
        marks = [pytest.mark.xfail(strict=True, reason="đang lọt, chờ vá")] if i in DANG_LOT else []
        yield pytest.param(ca, id=f"ca{i:02d}", marks=marks)


@pytest.mark.parametrize("ca", list(_tham_so()))
def test_bo_che_python_theo_bo_ca_chung(ca):
    kq = ClinicalDeidentifier.an_danh_van_ban(ca["van"])
    da_che = kq.van_ban_da_an_danh
    tu_choi = bool(ClinicalDeidentifier.kiem_tra_con_sot(da_che))
    if not tu_choi:
        for c in ca["cam"]:
            assert c not in da_che, f"còn lộ {c!r} trong: {da_che!r}"
        for g in ca["giu"]:
            assert g in da_che, f"mất chuỗi lâm sàng {g!r}: {da_che!r}"


def test_fixture_du_ca_va_dung_dinh_dang():
    assert len(CA) >= 24
    for ca in CA:
        assert set(ca) == {"van", "cam", "giu"}
        assert isinstance(ca["van"], str) and isinstance(ca["cam"], list) and isinstance(ca["giu"], list)
