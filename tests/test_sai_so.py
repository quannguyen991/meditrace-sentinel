# -*- coding: utf-8 -*-
"""Khoang tin cay, so sanh theo cap, va hai hang rao.

VI SAO CAN TEST. Tep `src/sai_so.py` sinh ra tu mot cau hoi tuong don gian —
"them khoang tin cay vao bang so sanh" — va trong luc viet no lam lo ra hai
loi nang hon ban than khoang tin cay. Test o day canh dung hai loi do.

LOI MOT: doi theo ID khong nhan dang duoc bo du lieu. Bo sinh dung lai khong
gian id giua cac the he, nen `hv_0019` la "sot sieu vi" trong bo 3.000 va
"thieu mau do giun" trong bo 5.000. Ghep ket qua bo 3.000 voi bo 5.000 theo id
cho ra mot phep ghep THANH CONG 60/60 voi toan bo nhan sai.

LOI HAI: don vi doc lap la khuon benh, khong phai ca. Lay lai mau theo ca thi
khoang tin cay hep gia.
"""
import json

import pytest

from src import sai_so as ss


def _tep(tmp_path, ban_ghi, ten):
    p = tmp_path / ten
    p.write_text("\n".join(json.dumps(b, ensure_ascii=False) for b in ban_ghi),
                 encoding="utf-8")
    return p


def _ca(ma, van, benh="sốt siêu vi", dap_an=None):
    return {"id": ma, "input": van, "benh": benh, "dap_an": dap_an or []}


# ------------------------------------------- LOI MOT: doi id khong du

def test_DUNG_HAN_khi_id_khop_nhung_noi_dung_LECH(tmp_path):
    """Loi that. Bo 3.000 va bo 5.000 dung cung id cho hai ca khac nhau."""
    ket_qua = {"hv_0019": {"id": "hv_0019", "input": "Bác sĩ: A\nBệnh nhân: sốt"}}
    bo_sai = _tep(tmp_path, [_ca("hv_0019", "Bác sĩ: X\nBệnh nhân: đau bụng",
                                 "thiếu máu do giun")], "bo_sai.jsonl")
    with pytest.raises(SystemExit) as e:
        ss.doi_chieu_tap(ket_qua, bo_sai)
    assert "LECH noi dung" in str(e.value)


def test_qua_khi_noi_dung_khop(tmp_path):
    van = "Bác sĩ: A\nBệnh nhân: sốt"
    ket_qua = {"hv_0019": {"id": "hv_0019", "input": van}}
    bo_dung = _tep(tmp_path, [_ca("hv_0019", van, "sốt siêu vi")], "bo.jsonl")
    assert ss.doi_chieu_tap(ket_qua, bo_dung) == {"hv_0019": "sốt siêu vi"}


def test_khoang_trang_khong_lam_lech(tmp_path):
    """Xuong dong va khoang trang khac nhau khong phai la the he khac nhau."""
    ket_qua = {"a": {"id": "a", "input": "Bác sĩ: A\n\nBệnh nhân:  sốt  "}}
    bo = _tep(tmp_path, [_ca("a", "Bác sĩ: A\nBệnh nhân: sốt")], "bo.jsonl")
    assert ss.doi_chieu_tap(ket_qua, bo)


def test_tim_tap_khop_sap_theo_NOI_DUNG_khong_theo_id(tmp_path):
    """Thong bao loi phai chi ra tep dung. Sap theo id thi no chi sai."""
    van = "Bác sĩ: A\nBệnh nhân: sốt"
    _tep(tmp_path, [_ca("a", van), _ca("b", van)], "dung.jsonl")
    _tep(tmp_path, [_ca("a", "khác hẳn"), _ca("b", "khác hẳn"),
                    _ca("c", "x")], "sai_nhung_nhieu_id.jsonl")
    theo_id = {"a": {"id": "a", "input": van}, "b": {"id": "b", "input": van}}
    ra = ss.tim_tap_khop(theo_id, tmp_path)
    assert ra[0][0] == "dung.jsonl"
    assert ra[0][1] == 2                      # khop noi dung
    assert [r for r in ra if r[0] == "sai_nhung_nhieu_id.jsonl"][0][1] == 0


def test_bo_qua_tep_ket_qua_khi_do_khop(tmp_path):
    """`ra_*.jsonl` va `trich_*.jsonl` khong phai bo du lieu goc."""
    van = "Bác sĩ: A"
    _tep(tmp_path, [_ca("a", van)], "ra_C_gi_do.jsonl")
    _tep(tmp_path, [_ca("a", van)], "trich_gi_do.jsonl")
    ra = ss.tim_tap_khop({"a": {"id": "a", "input": van}}, tmp_path)
    assert [r[0] for r in ra] == []


# ------------------------------- LOI HAI: don vi doc lap la khuon benh

def test_bootstrap_cum_RONG_hon_bootstrap_theo_ca():
    """Day la toan bo ly do co bootstrap cum.

    Dung mot bo so trong do moi khuon la mot hang so khac nhau: bien thien
    NAM HET o muc khuon. Lay lai mau theo ca thi 40 ca duoc dem la 40 don vi
    doc lap va khoang ra hep; lay lai mau theo khuon thi chi co 4 don vi.
    """
    diem, khuon = {}, {}
    for k, gia_tri in enumerate([0.2, 0.4, 0.6, 0.8]):
        for j in range(10):
            ma = f"c{k}_{j}"
            diem[ma], khuon[ma] = gia_tri, f"khuon{k}"
    theo_ca = ss.khoang(diem, None, so_lan=2000)
    theo_khuon = ss.khoang(diem, khuon, so_lan=2000)
    rong_ca = theo_ca["cao"] - theo_ca["thap"]
    rong_khuon = theo_khuon["cao"] - theo_khuon["thap"]
    assert rong_khuon > rong_ca * 1.5, (rong_ca, rong_khuon)
    assert theo_khuon["so_khuon"] == 4
    assert theo_ca["don_vi"] == "ca" and theo_khuon["don_vi"] == "khuôn"


def test_trung_binh_khong_doi_theo_cach_lay_lai_mau():
    diem = {f"c{i}": i / 10 for i in range(10)}
    khuon = {f"c{i}": f"k{i % 2}" for i in range(10)}
    assert ss.khoang(diem, None, so_lan=500)["trung_binh"] == \
        pytest.approx(ss.khoang(diem, khuon, so_lan=500)["trung_binh"])


def test_cung_hat_cho_cung_ket_qua():
    diem = {f"c{i}": (i * 7 % 13) / 13 for i in range(20)}
    a = ss.khoang(diem, None, so_lan=500, hat=7)
    b = ss.khoang(diem, None, so_lan=500, hat=7)
    assert (a["thap"], a["cao"]) == (b["thap"], b["cao"])


# ------------------------------------------------------ so sanh theo cap

def test_so_sanh_CHI_lay_ca_co_o_CA_HAI_nhanh():
    a = {"x": 0.5, "y": 0.6, "z": 0.7}
    b = {"x": 0.4, "y": 0.5}
    assert ss.so_sanh(a, b, so_lan=200)["so_ca_chung"] == 2


def test_theo_cap_HEP_hon_hai_khoang_roi():
    """Cac nhanh chay tren cung bo ca. Hieu theo cap triet tieu phan "ca nay
    de, ca kia kho", nen no hep hon nhieu so voi hai khoang roi.

    Neu khong lam theo cap thi hai khoang chong nhau va ket luan thanh
    "khong khac biet" — trong khi moi ca deu lech dung mot chieu.
    """
    a = {f"c{i}": i / 20 for i in range(20)}
    b = {f"c{i}": i / 20 + 0.02 for i in range(20)}   # luon hon dung 0,02
    ka, kb = ss.khoang(a, so_lan=2000), ss.khoang(b, so_lan=2000)
    assert ka["cao"] > kb["thap"], "hai khoang roi phai chong nhau"
    s = ss.so_sanh(b, a, so_lan=2000)
    assert s["hieu"] == pytest.approx(0.02)
    assert s["thap"] > 0, "theo cap phai tach duoc khoi 0"
    assert s["ty_le_dau_nguoc"] == 0.0


def test_khong_co_ca_chung_thi_dung_han():
    with pytest.raises(SystemExit):
        ss.so_sanh({"a": 1.0}, {"b": 1.0})


# ---------------------------------------------------- phan tang quy gan

def _ca_bon_tang():
    van = ("Bác sĩ: Cháu bị sao ạ?\n"
           "Mẹ: Cháu sốt hai hôm rồi\n"
           "Mẹ: Tôi thì dị ứng penicillin\n"
           "Bệnh nhân: Con đau họng\n"
           "Bác sĩ: Họng hơi đỏ")
    return _ca("a", van, dap_an=[
        {"chu_the": "bệnh nhân", "noi_dung": "sốt", "luot": [2]},
        {"chu_the": "mẹ", "noi_dung": "dị ứng penicillin", "luot": [3]},
        {"chu_the": "bệnh nhân", "noi_dung": "đau họng", "luot": [4]},
        {"chu_the": "bệnh nhân", "noi_dung": "họng đỏ", "luot": [5]},
    ])


def test_phan_dung_bon_tang():
    t = ss.tang_menh_de(_ca_bon_tang())
    assert t["ke_ho"] == 1          # me ke ho benh nhan
    assert t["ke_ve_minh"] == 1     # me ke ve chinh minh  <- tang 4
    assert t["benh_nhan"] == 1
    assert t["bac_si"] == 1


def test_menh_de_khong_co_luot_thi_khong_dem():
    ca = _ca("a", "Bác sĩ: A", dap_an=[{"chu_the": "bệnh nhân",
                                        "noi_dung": "x", "luot": []}])
    assert sum(ss.tang_menh_de(ca).values()) == 0


def test_do_cong_suat_gop_het_cac_ca():
    cs = ss.do_cong_suat({"a": _ca_bon_tang(), "b": _ca_bon_tang()})
    assert cs["tong"] == 8
    assert cs["theo_tang"]["ke_ve_minh"] == 2
    assert cs["ty_le_tang4"] == pytest.approx(0.25)


# ------------------------------------------------------- hang rao cong suat

def test_canh_cong_suat_BAO_khi_tran_nho_hon_be_rong():
    """Truong hop that: tang 4 chiem 1,36% trong mau, khoang tin cay rong
    4,16%. Tran anh huong nho hon nhieu nen bang khong the thay hieu ung."""
    cs = {"tong": 514, "theo_tang": {"ke_ve_minh": 7},
          "ty_le_tang4": 7 / 514, "anh_huong_toi_da": 7 / 514}
    canh = ss.canh_cong_suat(cs, 0.0416)
    assert canh and "không đủ công suất" in canh
    assert "7/514" in canh


def test_canh_cong_suat_IM_khi_du_cong_suat():
    cs = {"tong": 100, "theo_tang": {"ke_ve_minh": 30},
          "ty_le_tang4": 0.30, "anh_huong_toi_da": 0.30}
    assert ss.canh_cong_suat(cs, 0.04) is None


def test_canh_so_khuon_bao_khi_qua_it():
    assert "3 khuôn" in ss.canh_so_khuon(3)
    assert ss.canh_so_khuon(ss.KHUON_TOI_THIEU) is None
    assert ss.canh_so_khuon(None) is None


# ----------------------------------------------------------- bang va ho do

def test_bang_dat_canh_bao_o_DAU_khong_o_cuoi():
    """Canh bao o cuoi bang thi nguoi doc da doc xong so roi."""
    diem = {"B": {"a": 0.6, "b": 0.7}, "C": {"a": 0.5, "b": 0.8}}
    khuon = {"a": "k1", "b": "k2"}
    van = ss.bang("B", diem, khuon, "f1_quy_gan",
                  {"a": _ca_bon_tang(), "b": _ca_bon_tang()})
    vi_tri_canh = van.index("Mẫu chỉ nằm trên")
    assert vi_tri_canh < van.index("| Nhánh |")


def test_ho_thuoc_do_tach_dung():
    assert ss._ho_cua("f1_quy_gan") == "quy_gan"
    assert ss._ho_cua("final") == "cham_diem"
    with pytest.raises(SystemExit):
        ss._ho_cua("khong_ton_tai")


def test_phan_vi_bien():
    assert ss._phan_vi([1.0], 0.5) == 1.0
    assert ss._phan_vi([0.0, 1.0], 0.0) == 0.0
    assert ss._phan_vi([0.0, 1.0], 1.0) == 1.0
    assert ss._phan_vi([], 0.5) != ss._phan_vi([], 0.5)      # nan
