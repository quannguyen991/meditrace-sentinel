# -*- coding: utf-8 -*-
"""Nap bo hoi thoai nguoi that ghi tay.

VI SAO CAN TEST NANG O DAY. Tep ghi tay do NGUOI go, nen loi dinh dang la
chuyen binh thuong chu khong phai ngoai le. Va hai loai loi duoi day KHONG bao
loi o buoc sau, chung chi lam so lieu sai am tham:

  - dan luot khong ton tai   -> menh de mat bang chung, `sai_so` dem nhu binh
                                thuong
  - chu the khong khai       -> menh de tang 4 bi doc thanh tang 3

Nen bo nap phai KIEM chu khong tu sua: chi nguoi ghi moi biet y minh la gi, va
tu doan bu o day la bia thong tin lam sang.
"""
import pytest

from src import bo_nguoi_that as bnt

DU = """# HT-001

## Người
bệnh nhân: nam, 54 tuổi
vợ: người đi cùng

## Hội thoại
1 Bác sĩ: Anh thấy thế nào ạ?
2 Bệnh nhân: Tôi đau trên rốn mấy hôm rồi.
3 Vợ: Anh ấy còn bỏ cơm nữa. Tôi thì cao huyết áp từ lâu.
4 Bác sĩ: Bụng mềm, ấn đau vùng trên rốn.

## Đáp án
bệnh nhân | đau thượng vị | BỆNH SỬ HIỆN TẠI | 2
bệnh nhân | chán ăn | BỆNH SỬ HIỆN TẠI | 3
vợ | tăng huyết áp | TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI | 3
bệnh nhân | ấn đau thượng vị, bụng mềm | KHÁM LÂM SÀNG | 4
"""


def _tep(tmp_path, van, ten="ht.txt"):
    p = tmp_path / ten
    p.write_text(van, encoding="utf-8")
    return p


# ---------------------------------------------------------------- doc duoc

def test_doc_duoc_tep_du(tmp_path):
    tho = bnt.doc_mot_tep(_tep(tmp_path, DU))
    assert tho["id"] == "HT-001"
    assert len(tho["luot"]) == 4
    assert len(tho["dap_an_tho"]) == 4
    assert set(tho["nguoi"]) == {"bệnh nhân", "vợ"}


def test_tep_du_khong_co_loi(tmp_path):
    assert bnt.kiem(bnt.doc_mot_tep(_tep(tmp_path, DU))) == []


def test_thieu_ma_ca_thi_bao_loi(tmp_path):
    with pytest.raises(bnt.LoiDinhDang, match="thieu dong"):
        bnt.doc_mot_tep(_tep(tmp_path, DU.replace("# HT-001", "")))


def test_khoi_khong_biet_thi_bao_loi_KEM_SO_DONG(tmp_path):
    """Nguoi sua loi nay la nguoi go Notepad, nen phai chi ro dong nao."""
    van = DU.replace("## Người", "## Nhân vật")
    with pytest.raises(bnt.LoiDinhDang, match=r"dong \d+"):
        bnt.doc_mot_tep(_tep(tmp_path, van))


def test_dong_hoi_thoai_thieu_so_thi_bao_loi(tmp_path):
    van = DU.replace("2 Bệnh nhân:", "Bệnh nhân:")
    with pytest.raises(bnt.LoiDinhDang, match="hoi thoai"):
        bnt.doc_mot_tep(_tep(tmp_path, van))


# ------------------------------------------ hai loi lam so lieu sai am tham

def test_BAT_dan_luot_khong_ton_tai(tmp_path):
    """Menh de mat bang chung ma `sai_so` van dem nhu binh thuong."""
    van = DU.replace("| BỆNH SỬ HIỆN TẠI | 2", "| BỆNH SỬ HIỆN TẠI | 9")
    loi = bnt.kiem(bnt.doc_mot_tep(_tep(tmp_path, van)))
    assert any("luot 9 khong ton tai" in x for x in loi)


def test_BAT_chu_the_khong_khai(tmp_path):
    """Menh de tang 4 bi doc thanh tang 3 neu chu the khong nhan ra duoc."""
    van = DU.replace("vợ | tăng huyết áp", "chị gái | tăng huyết áp")
    loi = bnt.kiem(bnt.doc_mot_tep(_tep(tmp_path, van)))
    assert any("chu the" in x and "chị gái" in x for x in loi)


def test_BAT_vai_noi_trong_thoai_ma_khong_khai(tmp_path):
    van = DU.replace("3 Vợ:", "3 Con trai:")
    loi = bnt.kiem(bnt.doc_mot_tep(_tep(tmp_path, van)))
    assert any("khong khai" in x for x in loi)


def test_BAT_so_luot_khong_lien_tuc(tmp_path):
    van = DU.replace("4 Bác sĩ: Bụng mềm", "7 Bác sĩ: Bụng mềm")
    loi = bnt.kiem(bnt.doc_mot_tep(_tep(tmp_path, van)))
    assert any("lien tuc" in x for x in loi)


def test_BAT_muc_khong_hop_le(tmp_path):
    van = DU.replace("BỆNH SỬ HIỆN TẠI | 2", "TIỀN SỬ HIỆN TẠI | 2")
    loi = bnt.kiem(bnt.doc_mot_tep(_tep(tmp_path, van)))
    assert any("khong hop le" in x for x in loi)


def test_vai_bac_si_va_dieu_duong_KHONG_phai_khai(tmp_path):
    """Hai vai nay khong phai nguoi benh, khong can khai o khoi Nguoi."""
    van = DU.replace("4 Bác sĩ: Bụng mềm", "4 Điều dưỡng: Mạch 90, nhiệt 38 độ")
    assert bnt.kiem(bnt.doc_mot_tep(_tep(tmp_path, van))) == []


def test_BAT_dong_dap_an_thieu_cot(tmp_path):
    van = DU.replace("vợ | tăng huyết áp | TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI | 3",
                     "vợ | tăng huyết áp")
    with pytest.raises(bnt.LoiDinhDang, match="4 cot"):
        bnt.doc_mot_tep(_tep(tmp_path, van))


# ----------------------------------------------- doi sang dinh dang bo sinh

def test_doi_dinh_dang_KHOP_hinh_bo_sinh(tmp_path):
    """Day la ca y nghia cua tep nay: moi cong cu da co phai chay duoc ngay
    ma khong sua mot dong nao."""
    r = bnt.doi_dinh_dang(bnt.doc_mot_tep(_tep(tmp_path, DU)))
    for khoa in ("id", "input", "output", "dap_an", "so_luot", "benh"):
        assert khoa in r, khoa
    assert r["input"].startswith("Bác sĩ:")
    assert r["output"]
    assert all({"chu_the", "noi_dung", "muc", "luot"} <= set(m)
               for m in r["dap_an"])


def test_phan_tang_nhan_dung_TANG_4(tmp_path):
    """Cau "Toi thi cao huyet ap" o luot 3 do VO noi VE CHINH MINH — tang 4.

    Neu cho nay doc thanh tang 3 thi phieu tinh huong dung T4 thanh vo nghia.
    """
    r = bnt.doi_dinh_dang(bnt.doc_mot_tep(_tep(tmp_path, DU)))
    t = bnt._phan_tang(r)
    assert t["ke_ve_minh"] == 1, dict(t)
    assert t["ke_ho"] == 1, dict(t)
    assert t["benh_nhan"] == 1
    assert t["bac_si"] == 1


def test_gom_BO_ca_co_loi_va_GIU_ca_dung(tmp_path):
    _tep(tmp_path, DU, "a.txt")
    _tep(tmp_path, DU.replace("| BỆNH SỬ HIỆN TẠI | 2",
                              "| BỆNH SỬ HIỆN TẠI | 9"), "b.txt")
    ra, loi = bnt.gom(tmp_path)
    assert len(ra) == 1 and loi
    assert ra[0]["id"] == "HT-001"


# ------------------------------------ tai lieu khong duoc troi khoi ma

def test_KHOI_MAU_TRONG_TAI_LIEU_nap_duoc_that(tmp_path):
    """Tai lieu huong dan nguoi khac go tay theo mot dinh dang. Neu dinh dang
    trong tai lieu lech khoi bo nap thi NGUOI lam theo tai lieu se nhan mot
    trang loi, va ho khong co cach nao biet la tai lieu sai chu khong phai minh
    go sai.

    Test nay trich DUNG khoi mau trong `docs/bo-nguoi-that.md` va nap no.
    """
    import re
    from pathlib import Path
    if not Path("docs/bo-nguoi-that.md").exists():
        pytest.skip("can docs/bo-nguoi-that.md (khong co trong ban ma nguon day len GitHub)")
    van = Path("docs/bo-nguoi-that.md").read_text(encoding="utf-8")
    khoi = re.findall(r"```\n(# HT-001.*?)```", van, re.S)
    assert khoi, "khong tim thay khoi mau '# HT-001' trong tai lieu"
    tho = bnt.doc_mot_tep(_tep(tmp_path, khoi[0]))
    assert bnt.kiem(tho) == [], "khoi mau trong tai lieu khong nap duoc"
    # Va no phai la mot vi du CO tang 4 — neu khong thi tai lieu day nguoi ta
    # mot dinh dang ma khong day cho kho nhat.
    assert bnt._phan_tang(bnt.doi_dinh_dang(tho))["ke_ve_minh"] >= 1


def test_khoi_mau_trong_tai_lieu_KHONG_chep_nguyen_van():
    """Luat 2 cua tai lieu: dap an viet bang thuat ngu lam sang, khong chep loi
    benh nhan. Khoi mau phai lam dung luat no day."""
    import re
    from pathlib import Path
    from src import thuoc_do_quy_gan as t
    if not Path("docs/bo-nguoi-that.md").exists():
        pytest.skip("can docs/bo-nguoi-that.md (khong co trong ban ma nguon day len GitHub)")
    van = Path("docs/bo-nguoi-that.md").read_text(encoding="utf-8")
    khoi = re.findall(r"```\n(# HT-001.*?)```", van, re.S)[0]
    # "dau tren ron" trong hoi thoai, "dau thuong vi" trong dap an.
    assert "đau trên rốn" in khoi and "đau thượng vị" in khoi
    assert "đau thượng vị" not in khoi.split("## Đáp án")[0]
