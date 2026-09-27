# -*- coding: utf-8 -*-
"""Van tay bo du lieu — chan ho loi "mot ten tep, hai bo du lieu".

HO LOI NAY DA QUAY LAI BA LAN, va ca ba lan deu chi bi bat bang mot dau hieu
tinh co:

  lan 1  `train_baseline` chay tiep tu checkpoint bo 3.000 tren du lieu bo 5.000.
         Bi bat vi `eval_loss` o cac buoc dau trung tung chu so voi lan truoc —
         dau hieu chi thay duoc neu tinh co con nho so cu. Mat ~4 gio GPU.
  lan 2  `ra_C_viet_phat_trien.jsonl` mang ten bo 5.000 nhung la ket qua bo 3.000.
  lan 3  Bo sinh DUNG LAI khong gian id giua cac the he: `hv_0019` la "sot sieu
         vi" o bo 3.000 va "thieu mau do giun" o bo 5.000. Doi theo id thi bo SAI
         cung khop 60/60 — mot phep ghep thanh cong 100% voi toan bo nhan sai.

Nen BAM PHAI THEO NOI DUNG, khong theo id. Test dau tien o day canh dung cho do.
"""
import json

import pytest

from src import van_tay_bo as vt


def _ca(ma, van, benh="sốt siêu vi", dap_an=None):
    return {"id": ma, "input": van, "benh": benh, "dap_an": dap_an or []}


def _bo(tmp_path, ds, ten="bo.jsonl"):
    p = tmp_path / ten
    p.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in ds),
                 encoding="utf-8")
    return p


# ------------------------------------------- bam theo NOI DUNG, khong theo id

def test_CUNG_id_KHAC_noi_dung_thi_bam_KHAC():
    """Day la lan thu ba cua ho loi. Hai bo dung cung id cho hai ca khac nhau —
    doi theo id thi khop 100%, doi theo noi dung thi khong khop gi."""
    a = [_ca("hv_0019", "Bác sĩ: A\nBệnh nhân: sốt")]
    b = [_ca("hv_0019", "Bác sĩ: X\nBệnh nhân: đau bụng")]
    assert vt.bam_noi_dung(a) != vt.bam_noi_dung(b)


def test_KHAC_id_CUNG_noi_dung_thi_bam_GIONG():
    """Doi ten id khong lam bo du lieu thanh bo khac."""
    van = "Bác sĩ: A\nBệnh nhân: sốt"
    assert vt.bam_noi_dung([_ca("x1", van)]) == vt.bam_noi_dung([_ca("y9", van)])


def test_khoang_trang_khong_doi_bam():
    assert (vt.bam_noi_dung([_ca("a", "Bác sĩ: A\n\nBệnh nhân:  sốt ")])
            == vt.bam_noi_dung([_ca("a", "Bác sĩ: A\nBệnh nhân: sốt")]))


def test_thu_tu_ca_CO_doi_bam():
    """Hai bo cung noi dung nhung khac thu tu la hai lan chia khac nhau, va
    `--n 60` lay 60 dong DAU nen thu tu quyet dinh mau duoc do."""
    v1, v2 = "Bác sĩ: A", "Bác sĩ: B"
    assert (vt.bam_noi_dung([_ca("a", v1), _ca("b", v2)])
            != vt.bam_noi_dung([_ca("b", v2), _ca("a", v1)]))


# --------------------------------------------------------- ghi va doc lai

def test_ghi_roi_doc_lai_duoc(tmp_path):
    ds = [_ca("a", "Bác sĩ: A")]
    p = _bo(tmp_path, ds)
    vt.ghi(p, ds, "3", hat=42, ghi_chu="thu")
    v = vt.doc(p)
    assert v["the_he"] == "3" and v["hat"] == 42 and v["so_ca"] == 1
    assert v["ghi_chu"] == "thu"
    assert v["commit"]


def test_van_tay_nam_CANH_bo_khong_trong_bo(tmp_path):
    p = _bo(tmp_path, [_ca("a", "Bác sĩ: A")])
    assert vt.duong_dan_van_tay(p).name == "bo.van_tay.json"


def test_bo_chua_co_van_tay_thi_NOI_RO(tmp_path):
    """Im lang o cho nay la de nguoi doc tuong bo nao cung co nhan."""
    p = _bo(tmp_path, [_ca("a", "Bác sĩ: A")])
    assert vt.doc(p) is None
    assert "CHUA CO VAN TAY" in vt.mo_ta(p)


# --------------------------------------------------- bat tep bi ghi de

def test_BAT_tep_bi_ghi_de_boi_the_he_khac(tmp_path):
    ds = [_ca("a", "Bác sĩ: A"), _ca("b", "Bác sĩ: B")]
    p = _bo(tmp_path, ds)
    vt.ghi(p, ds, "2", hat=42)
    moi = [_ca("a", "Bác sĩ: HOÀN TOÀN KHÁC"), _ca("b", "Bác sĩ: KHÁC NỮA")]
    _bo(tmp_path, moi)                       # ghi de, KHONG cap nhat van tay
    khop, thong_diep = vt.khop(p, moi)
    assert khop is False
    assert "KHONG khop van tay cua chinh no" in thong_diep
    assert "the he 2" in thong_diep


def test_khop_khi_tep_con_nguyen(tmp_path):
    ds = [_ca("a", "Bác sĩ: A")]
    p = _bo(tmp_path, ds)
    vt.ghi(p, ds, "3", hat=42)
    khop, thong_diep = vt.khop(p, ds)
    assert khop is True and "thế hệ 3" in thong_diep


def test_BAT_ca_khi_SO_CA_doi_ma_bam_tinh_co_giong(tmp_path):
    ds = [_ca("a", "Bác sĩ: A")]
    p = _bo(tmp_path, ds)
    vt.ghi(p, ds, "3", hat=42)
    assert vt.khop(p, ds + ds)[0] is False


# ------------------------------------- nhan khai ra ma khong co vi du

def test_nhan_thieu_vi_du(tmp_path):
    """Lo~ "khai qua": luoc do khai bon quan he, du lieu co hai. Truoc
    11/09/2026 chuyen do chi bi phat hien bang cach tinh co di dem."""
    ds = [_ca("a", "Bác sĩ: A", dap_an=[
        {"quan_he": "đính chính", "trang_thai": "còn hiệu lực",
         "tinh_huong": "thực tế"},
        {"quan_he": None, "trang_thai": "bị thay thế",
         "tinh_huong": "thực tế"}])]
    p = _bo(tmp_path, ds)
    vt.ghi(p, ds, "2", hat=42)
    thieu = vt.nhan_thieu_vi_du(p, {
        "quan_he": ("bổ sung", "đính chính", "diễn biến", "mâu thuẫn"),
        "trang_thai": ("còn hiệu lực", "bị thay thế", "chưa giải quyết"),
        "tinh_huong": ("thực tế", "giả định", "kế hoạch")})
    assert set(thieu["quan_he"]) == {"bổ sung", "diễn biến", "mâu thuẫn"}
    assert thieu["trang_thai"] == ["chưa giải quyết"]
    assert set(thieu["tinh_huong"]) == {"giả định", "kế hoạch"}


def test_nhan_du_vi_du_thi_khong_bao_gi(tmp_path):
    ds = [_ca("a", "Bác sĩ: A", dap_an=[
        {"tinh_huong": t} for t in ("thực tế", "giả định", "kế hoạch")])]
    p = _bo(tmp_path, ds)
    vt.ghi(p, ds, "3", hat=42)
    assert vt.nhan_thieu_vi_du(
        p, {"tinh_huong": ("thực tế", "giả định", "kế hoạch")}) == {}


def test_bo_khong_co_van_tay_thi_khong_phan_doan_bua(tmp_path):
    """Khong co van tay thi tra ve rong, khong tu suy ra "thieu het"."""
    p = _bo(tmp_path, [_ca("a", "Bác sĩ: A")])
    assert vt.nhan_thieu_vi_du(p, {"quan_he": ("bổ sung",)}) == {}


# --------------------------------------------- the he la BAT BUOC khi chia tap

def test_tach_tap_BAT_BUOC_co_the_he():
    """De mac dinh thi moi lan sinh lai deu mang cung mot nhan, va nhan do het
    phan biet duoc gi."""
    import subprocess
    import sys
    r = subprocess.run([sys.executable, "-m", "src.tach_tap_viet", "--help"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    assert "--the-he" in r.stdout
    r2 = subprocess.run([sys.executable, "-m", "src.tach_tap_viet",
                         "--nguon", "khong_co_tep_nay.jsonl"],
                        capture_output=True, text=True, encoding="utf-8",
                        errors="replace")
    assert r2.returncode != 0
    assert "the-he" in (r2.stderr + r2.stdout)


def test_commit_danh_dau_BAN_NHAP_khi_cay_lam_viec_con_sua():
    """Lo~ trong ban dau cua chinh tep nay.

    Ghi `git rev-parse HEAD` la ghi commit CUOI CUNG DA COMMIT, khong phai ma
    nguon that su da sinh ra bo du lieu. Sinh bo khi dang co sua chua commit thi
    van tay ghi mot commit KHONG chua doan ma do — truong `commit` noi sai, va
    noi sai theo cach khong the phat hien tu chinh no.

    Da xay ra ngay trong lan dung dau tien: bo the he 3 duoc sinh khi
    `loi_dan_thuong.py` con dang sua.

    Test nay khong the khang dinh cay dang sach hay dang ban, nen no kiem DANG
    cua gia tri: phai la ma commit, va phai mang hau to khi va chi khi co sua.
    """
    import subprocess
    ma = vt._commit()
    assert ma and ma != "khong-ro"
    ban_nhap = subprocess.run(
        ["git", "status", "--porcelain", "--", "src", "tests"],
        capture_output=True, text=True).stdout.strip()
    if ban_nhap:
        assert ma.endswith("-ban-nhap"), ma
    else:
        assert not ma.endswith("-ban-nhap"), ma


def test_CUNG_hoi_thoai_KHAC_dap_an_thi_bam_KHAC():
    """Lo~ trong ban dau cua `bam_noi_dung`: no chi bam truong `input`.

    Ngay 11/09/2026 toi them truong `thoi_gian_su_kien` vao dap an roi sinh lai
    bo. Hoi thoai khong doi mot chu, nen the he 3 va the he 4 cho CUNG MOT BAM
    (`9486115ed86f669a` cho ca hai). Hai bo cung hoi thoai nhung khac nhan se lan
    vao nhau ma van tay khong thay — dung loai hong ma ham nay duoc viet de chan.
    """
    van = "Bác sĩ: A\nBệnh nhân: sốt"
    a = [_ca("x", van, dap_an=[{"noi_dung": "sốt", "muc": "BỆNH SỬ HIỆN TẠI",
                               "thoi_gian_su_kien": "hiện tại"}])]
    b = [_ca("x", van, dap_an=[{"noi_dung": "sốt", "muc": "BỆNH SỬ HIỆN TẠI",
                               "thoi_gian_su_kien": "quá khứ"}])]
    assert vt.bam_noi_dung(a) != vt.bam_noi_dung(b)


def test_thu_tu_khoa_trong_dap_an_KHONG_doi_bam():
    """Doi chung: bam phai on dinh truoc thu tu khoa, neu khong thi moi lan doc
    lai tep la mot bam khac va hang rao bao oan."""
    van = "Bác sĩ: A"
    a = [_ca("x", van, dap_an=[{"noi_dung": "sốt", "muc": "M", "phu_dinh": False}])]
    b = [_ca("x", van, dap_an=[{"phu_dinh": False, "muc": "M", "noi_dung": "sốt"}])]
    assert vt.bam_noi_dung(a) == vt.bam_noi_dung(b)


def test_them_menh_de_vao_dap_an_thi_bam_KHAC():
    van = "Bác sĩ: A"
    a = [_ca("x", van, dap_an=[{"noi_dung": "sốt"}])]
    b = [_ca("x", van, dap_an=[{"noi_dung": "sốt"}, {"noi_dung": "ho"}])]
    assert vt.bam_noi_dung(a) != vt.bam_noi_dung(b)
