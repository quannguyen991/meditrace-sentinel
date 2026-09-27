# -*- coding: utf-8 -*-
"""Test nhanh A va A+ bang mo hinh gia.

Cai dang test khong phai chat luong sinh — cai do phai do bang bo cham diem.
Cai dang test la BA dieu de sai am tham va lam hong ca phep so sanh:

  1. A+ phai NHAN duoc ban nhap cua A (khong thi no chi la A chay lai)
  2. A+ phai cong don token cua ca hai luot (khong thi bao cao chi phi sai,
     va A+ trong nhu re bang A)
  3. loi nhac hau kiem KHONG duoc nhac toi khai niem cua nhanh C — nhac roi
     thi A+ khong con la doi chung doc lap nua
"""
import json
import pathlib
import tempfile

from src import nhanh


class MoHinhGia:
    """Ghi lai moi loi nhac nhan duoc, tra ve van ban co dinh."""

    def __init__(self, tra_ve="BỆNH ÁN đã sửa"):
        self.nhan = []
        self.tra_ve = tra_ve


def gan_sinh_gia(monkeypatch, mh, token_vao=100, token_ra=50):
    def _gia(tok, model, noi_dung, max_token=512):
        mh.nhan.append(noi_dung)
        return mh.tra_ve, token_vao, token_ra
    monkeypatch.setattr(nhanh, "_sinh", _gia)


MAU = [{"id": "m1", "input": "1. Bác sĩ: Cháu sao ạ?\n2. Mẹ: Cháu ho 2 ngày.",
        "output": "LÝ DO KHÁM BỆNH\n\nHo 2 ngày."}]


def test_A_ghi_du_bon_truong(monkeypatch):
    mh = MoHinhGia("LÝ DO KHÁM BỆNH\n\nHo.")
    gan_sinh_gia(monkeypatch, mh)
    kq = nhanh.chay_A(MAU, None, None)
    assert len(kq) == 1
    assert set(kq[0]) >= {"id", "input", "tham_chieu", "du_doan"}
    assert kq[0]["tham_chieu"] == MAU[0]["output"]
    assert kq[0]["so_luot_goi"] == 1


def test_A_cong_NHAN_duoc_ban_nhap_cua_A(monkeypatch):
    """Neu A+ khong thay ban nhap thi no chi la A chay lai — doi chung vo nghia."""
    mh = MoHinhGia()
    gan_sinh_gia(monkeypatch, mh)
    ra_A = [{"id": "m1", "input": MAU[0]["input"], "tham_chieu": MAU[0]["output"],
             "du_doan": "BẢN NHÁP CỦA A", "token_vao": 100, "token_ra": 50}]
    nhanh.chay_A_cong(ra_A, None, None)
    assert "BẢN NHÁP CỦA A" in mh.nhan[0], "A+ khong nhan duoc ban nhap"
    assert MAU[0]["input"] in mh.nhan[0], "A+ khong nhan duoc hoi thoai goc"


def test_A_cong_cong_don_token_cua_CA_HAI_luot(monkeypatch):
    """A+ ton gap doi A. Bao cao thieu la bao cao mot phuong phap re hon that."""
    mh = MoHinhGia()
    gan_sinh_gia(monkeypatch, mh, token_vao=300, token_ra=80)
    ra_A = [{"id": "m1", "input": "x", "tham_chieu": "y", "du_doan": "z",
             "token_vao": 100, "token_ra": 50}]
    kq = nhanh.chay_A_cong(ra_A, None, None)
    assert kq[0]["token_vao"] == 400 and kq[0]["token_ra"] == 130
    assert kq[0]["so_luot_goi"] == 2


def test_tom_tat_chi_phi_cong_dung():
    kq = [{"so_luot_goi": 2, "token_vao": 400, "token_ra": 130},
          {"so_luot_goi": 2, "token_vao": 350, "token_ra": 120}]
    ct = nhanh.tom_tat_chi_phi(kq)
    assert ct == {"so_mau": 2, "tong_luot_goi": 4,
                  "tong_token_vao": 750, "tong_token_ra": 250}


def test_loi_nhac_hau_kiem_KHONG_nhac_khai_niem_cua_nhanh_C():
    """A+ phai la doi chung DOC LAP. Neu loi nhac cua no day khai niem cua C
    (chu the, quan he, trang thai, bang chung) thi khi C thang A+, khong biet
    la thang nho bieu dien trung gian hay nho loi nhac cua A+ bi lam yeu."""
    s = nhanh.LOI_NHAC_HAU_KIEM.lower()
    for cam in ("chủ thể", "quan hệ", "trạng thái", "bằng chứng",
                "đính chính", "diễn biến", "mâu thuẫn", "phát biểu"):
        assert cam not in s, f"loi nhac A+ ro ri khai niem cua nhanh C: {cam!r}"


def test_loi_nhac_hau_kiem_van_yeu_cau_ra_soat_that():
    """Doi chung phai duoc lam TU TE. Loi nhac mo ho thi A+ yeu oan."""
    s = nhanh.LOI_NHAC_HAU_KIEM
    assert "{hoi_thoai}" in s and "{ban_nhap}" in s
    assert "sai" in s and "thiếu" in s, "phai bao tim CA ghi sai lan ghi thieu"
    assert "viết lại" in s, "phai yeu cau xuat ban da sua, khong chi liet ke loi"


def test_A_cong_doc_duoc_tep_A_da_ghi(monkeypatch):
    """Duong noi giua hai nhanh la mot tep jsonl — kiem no doc lai duoc."""
    mh = MoHinhGia()
    gan_sinh_gia(monkeypatch, mh)
    kq_A = nhanh.chay_A(MAU, None, None)
    with tempfile.TemporaryDirectory() as d:
        p = pathlib.Path(d) / "ra_A.jsonl"
        p.write_text("\n".join(json.dumps(k, ensure_ascii=False) for k in kq_A),
                     encoding="utf-8")
        doc_lai = [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()]
    kq_Ac = nhanh.chay_A_cong(doc_lai, None, None)
    assert kq_Ac[0]["id"] == "m1" and kq_Ac[0]["tham_chieu"] == MAU[0]["output"]
