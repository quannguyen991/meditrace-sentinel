# -*- coding: utf-8 -*-
"""Test phan KHONG can mo hinh cua bake-off: danh so luot va phan tich JSON."""
from src import bakeoff


def test_danh_so_luot():
    ht = "Bác sĩ: Chào chị.\nMẹ: Dạ chào bác sĩ."
    ra, n = bakeoff.danh_so_luot(ht)
    assert n == 2
    assert ra.startswith("1. Bác sĩ:")
    assert "2. Mẹ:" in ra


def test_danh_so_bo_dong_trong():
    ra, n = bakeoff.danh_so_luot("Bác sĩ: A.\n\n\nMẹ: B.")
    assert n == 2


def test_json_hong_thi_bao_hong():
    hop_le, _, ly_do = bakeoff._phan_tich("khong phai json", 3)
    assert hop_le is False and "json hong" in ly_do


def test_thieu_truong_bat_buoc_thi_bao_hong():
    v = '{"phat_bieu": [{"chu_the": "trẻ", "noi_dung": "sốt"}]}'
    hop_le, _, ly_do = bakeoff._phan_tich(v, 3)
    assert hop_le is False and "thieu truong" in ly_do


def test_luot_thoai_khong_ton_tai_thi_bao_hong():
    """Bang chung phai tro toi luot CO THAT — kiem bang luat, khong chi cu phap."""
    v = ('{"phat_bieu": [{"chu_the": "trẻ", "noi_dung": "sốt", '
         '"do_chac_chan": "chắc chắn", "luot_thoai": [99]}]}')
    hop_le, _, ly_do = bakeoff._phan_tich(v, 3)
    assert hop_le is False and "khong ton tai" in ly_do


def test_ban_ghi_du_dieu_kien_thi_hop_le():
    v = ('{"phat_bieu": [{"chu_the": "mẹ", "noi_dung": "dị ứng penicillin", '
         '"do_chac_chan": "chắc chắn", "luot_thoai": [1, 2]}]}')
    hop_le, ds, ly_do = bakeoff._phan_tich(v, 3)
    assert hop_le is True and ly_do == "" and len(ds) == 1


def test_luoc_do_dung_enum_cho_ba_truong():
    """Enum khien mo hinh KHONG THE sinh gia tri ngoai tap hop le."""
    tp = bakeoff.LUOC_DO["properties"]["phat_bieu"]["items"]["properties"]
    assert set(tp["do_chac_chan"]["enum"]) == {"chắc chắn", "nghi ngờ", "chưa ghi nhận"}
    assert set(tp["tinh_huong"]["enum"]) == {"thực tế", "giả định", "kế hoạch"}


# ------------------------------------------------- loi nhac day dieu gi

def test_huong_dan_noi_ro_tuoi_la_cua_benh_nhan():
    """Phep kiem CHEO tim ra 17/289 ban ghi (6%) ghi "chau ba tuoi" ma chu_the
    la "nguoi nha". Dong nay va vi du 5 la ban sua cho loi do."""
    assert "Tuổi, cân nặng, giới tính của bệnh nhân là thông tin VỀ BỆNH NHÂN" \
        in bakeoff.HUONG_DAN


def test_vi_du_5_day_dung_ca_tuoi_do_nguoi_nha_noi():
    from src.vi_du_mau import VI_DU
    assert "Ví dụ 5" in VI_DU
    khoi = VI_DU.split("Ví dụ 5")[1]
    assert '"chu_the": "trẻ", "noi_dung": "ba tuổi"' in khoi
    assert '"chu_the": "người nhà"' not in khoi, "vi du lai day chinh cai loi"


def test_moi_vi_du_deu_co_JSON_hop_le():
    """Vi du sai cu phap thi mo hinh hoc theo cai sai do."""
    import json
    import re
    from src.vi_du_mau import VI_DU
    khoi = re.findall(r'\{"phat_bieu":.*?\n\]\}', VI_DU, re.S)
    assert len(khoi) == 5, f"tim thay {len(khoi)} khoi JSON, mong doi 5"
    for k in khoi:
        d = json.loads(k)
        for p in d["phat_bieu"]:
            assert p["luot_thoai"], "vi du co ban ghi khong co bang chung"
            assert p["do_chac_chan"] in ("chắc chắn", "nghi ngờ", "chưa ghi nhận")
            assert p["tinh_huong"] in ("thực tế", "giả định", "kế hoạch")


def test_moi_vi_du_deu_dung_luoc_do_dang_dung():
    """Vi du chua truong khong co trong LUOC_DO thi mo hinh se sinh ra truong
    do va bo ep JSON se chan — mat mot ban ghi ma khong ro vi sao."""
    import json
    import re
    from src.vi_du_mau import VI_DU
    cho_phep = set(bakeoff.LUOC_DO["properties"]["phat_bieu"]["items"]["properties"])
    for k in re.findall(r'\{"phat_bieu":.*?\n\]\}', VI_DU, re.S):
        for p in json.loads(k)["phat_bieu"]:
            thua = set(p) - cho_phep
            assert not thua, f"vi du dung truong khong co trong luoc do: {thua}"


# --------------------------------------------------- luu dan va chay tiep

class _TokGia:
    eos_token_id = 0

    def apply_chat_template(self, msgs, **kw):
        return msgs[0]["content"]

    def __call__(self, s, return_tensors=None):
        return _InpGia()

    def decode(self, ids, skip_special_tokens=True):
        return '{"phat_bieu": [{"chu_the": "trẻ", "noi_dung": "ho", ' \
               '"do_chac_chan": "chắc chắn", "luot_thoai": [1]}]}'


class _InpGia(dict):
    def __init__(self):
        super().__init__(input_ids=_Shape())

    def to(self, _dev):
        return self


class _Shape(list):
    shape = (1, 1)


class _ModelGia:
    device = "cpu"
    da_sinh = 0

    def generate(self, **kw):
        _ModelGia.da_sinh += 1
        return [[0, 1]]


class _TorchGia:
    """Chi can `no_grad` lam context manager. Cho phep test chay tren may
    khong cai torch — laptop khong co GPU van phai bat duoc loi logic."""

    class no_grad:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False


def _cai_torch_gia(monkeypatch):
    import sys
    if "torch" not in sys.modules:
        monkeypatch.setitem(sys.modules, "torch", _TorchGia())


def test_luu_dan_ghi_tung_mau_va_chay_tiep_duoc(tmp_path, monkeypatch):
    """Lan chay dau bi CUDA loi o mau 15 va mat sach 14 mau da lam."""
    _cai_torch_gia(monkeypatch)
    dem = tmp_path / "trich.jsonl"
    mau = [{"id": f"m{i}", "input": "1. Bác sĩ: sao ạ?"} for i in range(3)]

    _ModelGia.da_sinh = 0
    kq = bakeoff.trich(_TokGia(), _ModelGia(), None, mau, luu_dan=dem)
    assert len(kq) == 3 and _ModelGia.da_sinh == 3
    assert len(dem.read_text(encoding="utf-8").strip().splitlines()) == 3

    # chay lai: khong duoc goi mo hinh lan nao nua
    _ModelGia.da_sinh = 0
    kq2 = bakeoff.trich(_TokGia(), _ModelGia(), None, mau, luu_dan=dem)
    assert _ModelGia.da_sinh == 0, "chay lai ma van sinh lai tu dau"
    assert [k["id"] for k in kq2] == [k["id"] for k in kq]


def test_chay_tiep_chi_lam_nhung_mau_con_THIEU(tmp_path, monkeypatch):
    _cai_torch_gia(monkeypatch)
    dem = tmp_path / "trich.jsonl"
    mau = [{"id": f"m{i}", "input": "1. Bác sĩ: sao ạ?"} for i in range(3)]
    bakeoff.trich(_TokGia(), _ModelGia(), None, mau[:2], luu_dan=dem)
    _ModelGia.da_sinh = 0
    kq = bakeoff.trich(_TokGia(), _ModelGia(), None, mau, luu_dan=dem)
    assert _ModelGia.da_sinh == 1, "phai chi lam mau con thieu"
    assert len(kq) == 3


def test_khong_luu_dan_thi_khong_tao_tep(tmp_path, monkeypatch):
    _cai_torch_gia(monkeypatch)
    mau = [{"id": "m0", "input": "1. Bác sĩ: sao ạ?"}]
    bakeoff.trich(_TokGia(), _ModelGia(), None, mau)
    assert list(tmp_path.iterdir()) == []
