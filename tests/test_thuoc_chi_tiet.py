# -*- coding: utf-8 -*-
"""Chi tiet thuoc: lieu, so lan, duong dung, luc bat dau, luc ngung, trang thai dung.

Bat bien chinh — cung tinh than voi `test_lo_danh_tinh`: CHI TIET NAO GHI TRONG DAP
AN THI PHAI CO NGUYEN VAN TRONG HOI THOAI. Mot lieu thuoc khong ai noi ma nam trong
dap an thi ca hai nhanh deu bi day doan lieu.

Va ho loi "khai trong luoc do ma khong bao gio co gia tri" (sau lan truoc 15/09):
moi gia tri cua hai danh sach dong phai co it nhat mot vi du trong bo sinh, va
truong phai di het duong: bo sinh -> dap an -> nhan huan luyen -> luoc do cua mo
hinh -> doc JSON -> ban nhap -> khoa bang chung -> bo cham.
"""
import collections
import json

import pytest

from src import bakeoff, cham_he_thong as cht, du_lieu_trich, khoa_bang_chung as kbc
from src import ngu_lieu_viet as nl, phat_bieu as pb, sinh_benh_an
from src import sinh_hoi_thoai_viet as sh


@pytest.fixture(scope="module")
def bo():
    return sh.sinh_bo(1500, seed=7)


def _luot_cua(ca, so):
    return ca["input"].split("\n")[so - 1].lower()


def _menh_de_thuoc(bo):
    return [(c, d) for c in bo for d in c["dap_an"] if d.get("thuoc")]


# ------------------------------------------------------------------ luoc do

def test_luoc_do_tu_choi_duong_dung_la():
    with pytest.raises(ValueError):
        pb.PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="x",
                    bang_chung=[1], thuoc={"ten": "x", "duong_dung": "hít"})


def test_luoc_do_tu_choi_thuoc_khong_ten_va_khoa_la():
    for t in ({"lieu": "5 mg"}, {"ten": "x", "ham_luong": "5 mg"}):
        with pytest.raises(ValueError):
            pb.PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="x",
                        bang_chung=[1], thuoc=t)


def test_tu_json_giu_thuoc_va_bo_gia_tri_la_ma_khong_bo_ban_ghi():
    ps, loi = pb.tu_json([{"chu_the": "bệnh nhân", "noi_dung": "amlodipin",
                           "luot_thoai": [2],
                           "thuoc": {"ten": "amlodipin", "lieu": "5 mg",
                                     "duong_dung": "hít", "trang_thai_dung": "đang dùng"}}])
    assert not loi and len(ps) == 1
    assert ps[0].thuoc["lieu"] == "5 mg"
    assert ps[0].thuoc["duong_dung"] is None, "gia tri ngoai danh sach phai thanh None"
    assert ps[0].thuoc["trang_thai_dung"] == "đang dùng"


def test_luoc_do_mo_hinh_dung_chung_danh_sach_voi_phat_bieu():
    tp = bakeoff.LUOC_DO["properties"]["phat_bieu"]["items"]["properties"]["thuoc"]
    assert set(tp["properties"]) == set(pb.THUOC_KHOA)
    assert set(tp["properties"]["duong_dung"]["enum"]) - {None} == set(pb.DUONG_DUNG)
    assert set(tp["properties"]["trang_thai_dung"]["enum"]) - {None} == set(pb.TRANG_THAI_DUNG)


def test_loi_nhac_day_mo_hinh_khong_doan_lieu():
    assert "thuoc:" in bakeoff.HUONG_DAN
    assert "không đoán liều" in bakeoff.HUONG_DAN


# ------------------------------------------------------------------ bo sinh

def test_moi_duong_dung_deu_co_thuoc_trong_ngu_lieu():
    co = {v[0] for bang in (nl.THUOC_CHI_TIET_NGUOI_LON, nl.THUOC_CHI_TIET_TRE_EM)
          for v in bang.values()}
    assert co == set(pb.DUONG_DUNG)


def test_moi_gia_tri_dong_deu_co_vi_du_trong_bo_sinh(bo):
    md = _menh_de_thuoc(bo)
    assert len(md) > 100
    assert {d["thuoc"]["duong_dung"] for _c, d in md} == set(pb.DUONG_DUNG)
    assert {d["thuoc"]["trang_thai_dung"] for _c, d in md} == set(pb.TRANG_THAI_DUNG)
    for k in ("lieu", "so_lan", "bat_dau", "ngung"):
        assert any(d["thuoc"][k] for _c, d in md), f"khong menh de nao co {k}"
        assert any(d["thuoc"][k] is None for _c, d in md), \
            f"moi menh de deu co {k} — mo hinh se hoc luon dien, ke ca khi khong ai noi"


def test_moi_chi_tiet_ghi_trong_dap_an_deu_co_trong_luot_duoc_dan(bo):
    vi_pham = []
    for c, d in _menh_de_thuoc(bo):
        van = " ".join(_luot_cua(c, n) for n in d["luot"])
        t = d["thuoc"]
        for k in ("ten", "lieu", "so_lan", "bat_dau", "ngung", "duong_dung"):
            if t.get(k) and t[k].lower() not in van:
                vi_pham.append((c["id"], k, t[k]))
    assert not vi_pham, vi_pham[:5]


def test_dap_an_moi_khoa_thuoc_day_du(bo):
    for _c, d in _menh_de_thuoc(bo):
        assert set(d["thuoc"]) == set(pb.THUOC_KHOA)
        pb._kiem_thuoc(d["thuoc"])


def test_dinh_chinh_lieu_giu_ban_cu_va_ban_moi_khac_lieu(bo):
    thay = 0
    for c in bo:
        if "lieu_dinh_chinh" not in c["bay"]:
            continue
        moi = [d for d in c["dap_an"] if d.get("thuoc") and d["quan_he"] == "đính chính"]
        assert moi, c["id"]
        for d in moi:
            cu = c["dap_an"][d["quan_he_voi"]]
            assert cu["trang_thai"] == "bị thay thế"
            assert cu["thuoc"]["lieu"] and d["thuoc"]["lieu"]
            assert cu["thuoc"]["lieu"] != d["thuoc"]["lieu"]
            assert d["thuoc"]["ten"] == cu["thuoc"]["ten"]
            # Ban tham chieu chi in lieu da sua
            assert d["thuoc"]["lieu"] in c["output"]
            thay += 1
    assert thay >= 10


def test_ca_khong_mang_bay_dinh_chinh_lieu_thi_khong_co_ban_lieu_bi_thay(bo):
    for c in bo:
        if "lieu_dinh_chinh" in c["bay"]:
            continue
        assert not any(d.get("thuoc") and d["trang_thai"] == "bị thay thế"
                       for d in c["dap_an"]), c["id"]


# ------------------------------------------------- di het duong, sau bo sinh

def test_nhan_huan_luyen_mang_thuoc(bo):
    c, d = _menh_de_thuoc(bo)[0]
    _hoi, dap = du_lieu_trich.doi_mot_ca(c)
    ps = json.loads(dap)["phat_bieu"]
    assert any(p.get("thuoc") == d["thuoc"] for p in ps)
    assert not any("thuoc" in p for p in ps if p["noi_dung"] != d["noi_dung"]
                   and not p.get("thuoc")), "ban ghi khong phai thuoc khong mang truong"


def test_ban_nhap_in_lieu_va_cach_dung():
    p = {"id": 0, "chu_the_id": 0, "noi_dung": "amlodipin", "bang_chung": [2],
         "trich_dan": ["tôi có uống amlodipin 5 mg"],
         "thuoc": {"ten": "amlodipin", "lieu": "5 mg", "so_lan": "ngày một lần buổi sáng",
                   "duong_dung": "uống", "bat_dau": "ba tháng nay", "ngung": None,
                   "trang_thai_dung": "đang dùng"}}
    cum = sinh_benh_an.dien_dat(p)
    assert cum == "amlodipin 5 mg, uống ngày một lần buổi sáng (ba tháng nay)"


def test_ban_nhap_khong_viet_lap_moc_ngung_da_co_trong_noi_dung():
    p = {"noi_dung": "từng dùng omeprazole, đã ngừng 2 tuần",
         "thuoc": {"ten": "omeprazole", "lieu": "20 mg", "so_lan": None,
                   "duong_dung": "uống", "bat_dau": None, "ngung": "2 tuần",
                   "trang_thai_dung": "đã ngừng"}}
    assert sinh_benh_an.dien_dat(p) == "từng dùng omeprazole 20 mg, uống, đã ngừng 2 tuần"


def _khoa(lieu):
    luot = {1: ("bác sĩ", "Đang uống thuốc gì không ạ?"),
            2: ("bệnh nhân", "Dạ tôi có uống amlodipin 5 mg, ngày một lần buổi sáng ạ.")}
    p = pb.PhatBieu(id=0, nguoi_noi="bệnh nhân", chu_the_id=0, noi_dung="amlodipin",
                    bang_chung=[2], trich_dan=["tôi có uống amlodipin 5 mg"],
                    thuoc={"ten": "amlodipin", "lieu": lieu, "so_lan": "ngày một lần buổi sáng",
                           "duong_dung": "uống", "bat_dau": None, "ngung": None,
                           "trang_thai_dung": "đang dùng"})
    return kbc.khoa_mot(p, luot)


def test_khoa_chan_lieu_khong_ai_noi():
    kq = _khoa("50 mg")
    assert "lieu_khong_thay" in kq.chan, "50 mg chung tu 'mg' voi 5 mg — phai so nguyen chuoi"


def test_khoa_khong_chan_lieu_dung():
    kq = _khoa("5 mg")
    assert "lieu_khong_thay" not in kq.chan
    assert "chi_tiet_thuoc_khong_thay" not in kq.canh_bao


def test_khoa_khong_chan_oan_chi_tiet_thuoc_tren_dap_an_hoan_hao(bo):
    from src.danh_gia_khoa import phat_bieu_tu_dap_an
    dem = collections.Counter()
    for c in bo[:600]:
        ps = [p for p in phat_bieu_tu_dap_an(c) if p.thuoc]
        for k in kbc.khoa_ca(ps, c["input"])["ket_qua"]:
            dem["tong"] += 1
            for m in ("lieu_khong_thay",):
                dem[m] += m in k.chan
            for m in ("chi_tiet_thuoc_khong_thay", "duong_dung_khong_thay"):
                dem[m] += m in k.canh_bao
    assert dem["tong"] > 50
    assert dem["lieu_khong_thay"] == 0, dem
    assert dem["chi_tiet_thuoc_khong_thay"] == 0 and dem["duong_dung_khong_thay"] == 0, dem


def test_bo_cham_bat_sai_lieu_va_lieu_bia_nhung_khong_phat_bo_cu():
    vang = {"thuoc": {"ten": "amlodipin", "lieu": "5 mg", "so_lan": None, "duong_dung": "uống",
                      "bat_dau": None, "ngung": None, "trang_thai_dung": "đang dùng"}}
    dung = {"thuoc": dict(vang["thuoc"])}
    sai = {"thuoc": dict(vang["thuoc"], lieu="10 mg")}
    bia = {"thuoc": dict(vang["thuoc"], so_lan="ngày ba lần")}
    thieu = {"thuoc": dict(vang["thuoc"], lieu=None)}
    assert cht.dung_thuoc(vang, dung)
    assert not cht.dung_thuoc(vang, sai)
    assert not cht.dung_thuoc(vang, bia)
    assert not cht.dung_thuoc(vang, thieu)
    assert cht.dung_thuoc({"noi_dung": "sốt"}, {"noi_dung": "sốt"}), "bo cu khong co thuoc"
    assert "sai_thuoc" in cht.LOI


# ------------------------------------------------- y lenh thuoc cua bac si (16/09)

def _y_lenh(bo):
    return [(c, d) for c in bo for d in c["dap_an"]
            if d.get("thuoc") and d["muc"] == "KẾ HOẠCH ĐIỀU TRỊ"]


def test_y_lenh_thuoc_la_ke_hoach_chu_khong_phai_viec_da_xay_ra(bo):
    ds = _y_lenh(bo)
    assert len(ds) > 30, len(ds)
    for c, d in ds:
        assert d["tinh_huong"] == "kế hoạch", (c["id"], d)
        assert d["hanh_vi"] == "kế hoạch", (c["id"], d)
        assert d["thuoc"]["trang_thai_dung"] in ("đã ngừng", "được kê, chưa dùng")


def test_thuoc_moi_duoc_ke_khong_bao_gio_la_dang_dung(bo):
    ke = [d for _c, d in _y_lenh(bo) if d["noi_dung"].startswith("kê ")]
    assert ke, "khong co y lenh ke thuoc moi nao"
    for d in ke:
        assert d["thuoc"]["trang_thai_dung"] == "được kê, chưa dùng", d
        assert d["thuoc"]["lieu"] and d["thuoc"]["so_lan"], "y lenh phai co lieu va so lan"


def test_co_ca_vua_dang_dung_vua_bi_bac_si_bao_ngung_cung_mot_thuoc(bo):
    """Cap doi lap trong CUNG mot ca: ghi nham hai ban nay thanh mot la dung lo~i
    'thuoc da ngung ghi thanh dang dung'."""
    thay = 0
    for c in bo:
        dang = {d["thuoc"]["ten"] for d in c["dap_an"]
                if d.get("thuoc") and d["thuoc"]["trang_thai_dung"] == "đang dùng"}
        ngung = {d["thuoc"]["ten"] for d in c["dap_an"]
                 if d.get("thuoc") and d["muc"] == "KẾ HOẠCH ĐIỀU TRỊ"
                 and d["thuoc"]["trang_thai_dung"] == "đã ngừng"}
        thay += bool(dang & ngung)
    assert thay >= 5, thay


def test_ban_nhap_khong_gop_y_lenh_vao_muc_thuoc_dang_dung(bo):
    """Y lenh phai nam o muc KE HOACH DIEU TRI cua ban tham chieu, khong o THUOC
    DANG DUNG — day la nhom lo~i 14 (sai muc) cong nhom 4 (ke hoach thanh su that)."""
    for c, d in _y_lenh(bo)[:20]:
        khoi = [k for k in c["output"].split("\n\n") if k.startswith("THUỐC ĐANG DÙNG")]
        if khoi:
            assert d["noi_dung"] not in khoi[0], (c["id"], d["noi_dung"])


def test_loi_nhac_liet_ke_DU_moi_gia_tri_dong():
    """Luoc do JSON ep gia tri, nhung mo hinh doc LOI NHAC BANG CHU. Thieu mot gia
    tri trong loi nhac thi mo hinh co the khong bao gio sinh ra no — va the la mot
    gia tri khai trong luoc do ma khong bao gio xuat hien. Da vap dung the ngay
    16/09/2026 voi "được kê, chưa dùng"."""
    for v in pb.TRANG_THAI_DUNG:
        assert v in bakeoff.HUONG_DAN, v
    for v in pb.DUONG_DUNG:
        assert v in bakeoff.HUONG_DAN, v
