# -*- coding: utf-8 -*-
"""Bo trich nhat ky loi nhac.

VI SAO CAN TEST. Ban dau bo trich chi tim duoc **3** loi nhac tren 74 phien,
trong khi kho co 105 commit trong 6 ngay. Con so 3 do la dau hieu DUY NHAT cho
thay co loi — tep sinh ra van dung dinh dang, van doc duoc, chi la gan trong.

Nguyen nhan: ban ghi KET QUA CONG CU cung mang `type: "user"`. Ban dau moi ban
ghi khong phai chu deu dat `hien = None`, nen ngay sau lenh dau tien la lien
ket giua loi nhac va phan viec sau no bi cat.

Day la ho loi im lang lan thu bay trong du an: dau ra hop le, khong ngoai le,
chi la thieu gan het du lieu.
"""
import json

import pytest

from src import nhat_ky_loi_nhac as nk


def _phien(tmp_path, ban_ghi, ten="phien.jsonl"):
    p = tmp_path / ten
    p.write_text("\n".join(json.dumps(b, ensure_ascii=False) for b in ban_ghi),
                 encoding="utf-8")
    return p


def _user(van, ts="2026-09-05T10:00:00Z", cwd=r"D:\Claude\meditrace-core"):
    return {"type": "user", "timestamp": ts, "cwd": cwd,
            "message": {"role": "user", "content": van}}


def _ket_qua_cong_cu(cwd=r"D:\Claude\meditrace-core"):
    """Ban ghi ket qua cong cu — cung mang type "user"."""
    return {"type": "user", "cwd": cwd, "message": {
        "role": "user",
        "content": [{"type": "tool_result", "content": "xong"}]}}


def _ghi(duong_dan, cwd=r"D:\Claude\meditrace-core"):
    return {"type": "assistant", "cwd": cwd, "message": {
        "role": "assistant",
        "content": [{"type": "tool_use", "name": "Write",
                     "input": {"file_path": duong_dan}}]}}


# ------------------------------------------------- loi da xay ra that

def test_ket_qua_cong_cu_KHONG_cat_lien_ket(tmp_path):
    """Loi that: sau lenh dau tien, moi tep ghi sau do deu bi mat."""
    p = _phien(tmp_path, [
        _user("viết bộ sinh dữ liệu"),
        _ghi(r"D:\Claude\meditrace-core\src\a.py"),
        _ket_qua_cong_cu(),
        _ghi(r"D:\Claude\meditrace-core\src\b.py"),      # sau ket qua cong cu
        _ket_qua_cong_cu(),
        _ghi(r"D:\Claude\meditrace-core\tests\test_a.py"),
    ])
    muc = nk.doc_phien(p)
    assert len(muc) == 1
    assert muc[0]["tep_da_ghi"] == ["src/a.py", "src/b.py", "tests/test_a.py"]


# ------------------------------------------------- pham vi loc

def test_chi_lay_loi_nhac_dan_toi_MA_NGUON(tmp_path):
    p = _phien(tmp_path, [
        _user("viết mã"),
        _ghi(r"D:\Claude\meditrace-core\src\a.py"),
        _user("xuất pdf báo cáo mẫu cho tôi học"),
        _ghi(r"D:\Claude\meditrace-core\docs\bao-cao-mau.md"),
    ])
    muc = [m for m in nk.doc_phien(p) if m["tep_da_ghi"]]
    assert len(muc) == 1
    assert muc[0]["loi_nhac"] == "viết mã"


def test_loi_nhac_chi_sinh_tai_lieu_thi_KHONG_vao(tmp_path):
    """Yeu cau ro cua nguoi dung: tai lieu de HOC khong duoc ghi vao nhat ky
    loi nhac, vi de bi hieu nham la AI viet bao cao."""
    p = _phien(tmp_path, [
        _user("làm cho tôi bản báo cáo mẫu để học"),
        _ghi(r"D:\Claude\meditrace-core\docs\mau.md"),
    ])
    assert [m for m in nk.doc_phien(p) if m["tep_da_ghi"]] == []


def test_bo_qua_viec_cua_du_an_KHAC(tmp_path):
    """Thu muc phien chua ban ghi cua moi du an tren may. Doc nham la doc vao
    viec rieng cua nguoi dung.

    SUA 10/09: ban dau loc THEO PHIEN, nay loc theo TUNG LOI NHAC — chinh xac
    hon, vi mot phien co the lam nhieu du an. `doc_phien` van tra ve ban ghi
    nhung `tep_da_ghi` rong, nen `gom` loai no.
    """
    khac = r"D:\Claude\ielts-writing-task1"
    p = _phien(tmp_path, [
        _user("viết mã", cwd=khac),
        _ghi(r"D:\Claude\ielts-writing-task1\src\a.py", cwd=khac),
    ])
    assert [m for m in nk.doc_phien(p) if m["tep_da_ghi"]] == []


def test_bo_qua_viec_cua_tac_tu_con(tmp_path):
    p = _phien(tmp_path, [
        dict(_user("việc của tác tử con"), isSidechain=True),
        _ghi(r"D:\Claude\meditrace-core\src\a.py"),
    ])
    assert [m for m in nk.doc_phien(p) if m["tep_da_ghi"]] == []


def test_bo_qua_nhac_he_thong(tmp_path):
    p = _phien(tmp_path, [
        _user("<system-reminder>gì đó</system-reminder>"),
        _ghi(r"D:\Claude\meditrace-core\src\a.py"),
    ])
    assert [m for m in nk.doc_phien(p) if m["tep_da_ghi"]] == []


# ------------------------------------------------------------ dinh dang

def test_loi_nhac_dai_bi_cat_va_NOI_RO_la_da_cat():
    van = "a" * 500
    assert "đã cắt" in nk._gon(van)


def test_bang_khai_ro_pham_vi():
    """Nhat ky nay chi gom phan MA NGUON. Khong khai ro thi nguoi doc se tuong
    day la toan bo cuoc trao doi."""
    t = nk.dung_bang([{"thoi_gian": "2026-09-05T10:00:00Z",
                       "loi_nhac": "viết mã", "tep_da_ghi": ["src/a.py"]}])
    assert "Phạm vi" in t
    assert "không phải nhật ký cho" in t


def test_bang_rong_van_dung_dinh_dang():
    t = nk.dung_bang([])
    assert "Phạm vi" in t and "chưa có mục nào" in t


def test_dong_thoi_gian_khong_lam_mat_muc(tmp_path):
    """Hai loi nhac cung mot phut phai giu ca hai."""
    p = _phien(tmp_path, [
        _user("việc một", ts="2026-09-05T10:00:00Z"),
        _ghi(r"D:\Claude\meditrace-core\src\a.py"),
        _user("việc hai", ts="2026-09-05T10:00:00Z"),
        _ghi(r"D:\Claude\meditrace-core\src\b.py"),
    ])
    muc = [m for m in nk.doc_phien(p) if m["tep_da_ghi"]]
    assert len(muc) == 2


# ------------------------------- loc CHEO DU AN, va thong bao he thong

def test_bo_ghi_vao_du_an_KHAC_du_duong_dan_co_src(tmp_path):
    """Loi that: `_la_ma` chi kiem "src/" ma khong kiem thuoc kho nao.

    Mot lenh ghi vao D:/Claude/ielts-writing-task1/src/build.py cung khop
    "src/" va lot vao nhat ky. Cong voi viec loc THEO PHIEN, ket qua la nhat
    ky co ca loi nhac cua VeriSocrates, ReadUp, va mot du an lam logo.
    """
    p = _phien(tmp_path, [
        _user("sửa giao diện"),
        _ghi(r"D:\Claude\ielts-writing-task1\src\build.py"),
    ])
    assert [m for m in nk.doc_phien(p) if m["tep_da_ghi"]] == []


def test_giu_lai_khi_duong_dan_THUOC_de_tai(tmp_path):
    p = _phien(tmp_path, [
        _user("viết bộ sinh"),
        _ghi(r"D:\Claude\meditrace-core\src\a.py"),
    ])
    assert len([m for m in nk.doc_phien(p) if m["tep_da_ghi"]]) == 1


def test_mot_phien_lam_HAI_du_an_chi_lay_phan_dung(tmp_path):
    """Truong hop da xay ra: mot phien lam ca hai du an. Loc theo phien thi
    lay het; loc theo tung loi nhac thi chi lay dung phan cua du an."""
    p = _phien(tmp_path, [
        _user("xong front end verisocrates nhé"),
        _ghi(r"D:\verisocrates\src\app.js"),
        _user("viết bộ sinh dữ liệu"),
        _ghi(r"D:\Claude\meditrace-core\src\a.py"),
    ])
    muc = [m for m in nk.doc_phien(p) if m["tep_da_ghi"]]
    assert len(muc) == 1
    assert muc[0]["loi_nhac"] == "viết bộ sinh dữ liệu"


@pytest.mark.parametrize("van", [
    "<task-notification><task-id>abc</task-id></task-notification>",
    "<system-reminder>gì đó</system-reminder>",
    r"Base directory for this skill: C:\gì đó",
    "This session is being continued from a previous conversation.",
    "[SYSTEM NOTIFICATION - NOT USER INPUT] gì đó",
])
def test_bo_van_ban_khong_phai_loi_nhac(tmp_path, van):
    """Nhung thu nay nam o ban ghi "user" nhung khong phai nguoi dung go."""
    p = _phien(tmp_path, [
        _user(van),
        _ghi(r"D:\Claude\meditrace-core\src\a.py"),
    ])
    assert [m for m in nk.doc_phien(p) if m["tep_da_ghi"]] == []


def test_loi_nhac_that_van_duoc_giu(tmp_path):
    """Doi chung: bo loc khong duoc bat nham loi nhac ngan cua nguoi dung."""
    p = _phien(tmp_path, [
        _user("ok làm tiếp đi"),
        _ghi(r"D:\Claude\meditrace-core\src\a.py"),
    ])
    assert len([m for m in nk.doc_phien(p) if m["tep_da_ghi"]]) == 1


# ------------------------------------------- che noi dung nhay cam (17/09)

def test_che_dia_chi_may_TRUOC_email():
    """Mau email chay truoc thi an mat phan dau va de lo dia chi IP."""
    van, so = nk.che_nhay_cam("ssh nguoidung@100.64.0.7 rồi chạy")
    assert "100.64" not in van and "nguoidung" not in van
    assert "[đã che: địa chỉ máy]" in van and so == 1


@pytest.mark.parametrize("van,lo", [
    ("gửi về ai.do@gmail.com nhé", "gmail"),
    ("số tôi 0912345678", "0912345678"),
    ("khoá sk-abcdefghijklmnopqrstu", "abcdefghij"),
    ("máy 192.168.1.20", "192.168"),
])
def test_che_thong_tin_rieng(van, lo):
    moi, so = nk.che_nhay_cam(van)
    assert lo not in moi and so >= 1


def test_tep_dinh_kem_giu_TEN_bo_duong_dan_may():
    goc = r'@"C:\Users\admin\.claude\uploads\abc\d6e89445-tu_dien.csv" đọc nhé'
    van, _so = nk.che_nhay_cam(goc)
    assert "tu_dien.csv" in van
    assert "Users" not in van and "d6e89445" not in van


def test_luoc_cum_ngoai_de_tai_GIU_phan_con_lai():
    van, so = nk.che_nhay_cam("cho readup làm sau, làm cái này trước")
    assert "readup" not in van.lower()
    assert "làm cái này trước" in van
    assert nk.DAU_LUOC in van and so == 1


def test_luoc_ca_loi_nhac_van_de_lai_dau():
    """Khong bao gio bien loi nhac thanh chuoi rong: nguoi doc phai thay la da luoc."""
    van, _so = nk.che_nhay_cam("ok cài ollama lên laptop đi")
    assert van == nk.DAU_LUOC


def test_gop_dau_luoc_lien_nhau():
    van, _so = nk.che_nhay_cam("bds chạy chưa, ollama thì sao, làm tiếp")
    assert van.count(nk.DAU_LUOC) == 1 and "làm tiếp" in van


def test_khong_luoc_nham_loi_nhac_de_tai():
    """Doi chung: tu du an khong duoc bi coi la ngoai du an."""
    goc = "thêm thuốc chi tiết vào lược đồ và bộ sinh đi, chạy gpt 500"
    van, so = nk.che_nhay_cam(goc)
    assert van == goc and so == 0


def test_khop_theo_TU_khong_khop_giua_tu():
    van, so = nk.che_nhay_cam("chạy bdsx đi")
    assert so == 0


# ---------------------------------------------- gan commit theo thoi gian

def _c(ma, luc):
    from datetime import datetime
    return {"ma": ma, "luc": datetime.fromisoformat(luc), "tieu_de": "t",
            "tep": ["src/a.py"]}


def test_commit_gan_cho_loi_nhac_GAN_NHAT_TRUOC_no():
    muc = [{"thoi_gian": "2026-09-05T01:00:00Z", "loi_nhac": "một",
            "tep_da_ghi": [], "dung_de_tai": True},
           {"thoi_gian": "2026-09-05T02:00:00Z", "loi_nhac": "hai",
            "tep_da_ghi": [], "dung_de_tai": True}]
    # 09:30 gio VN = 02:30 UTC -> sau "hai"
    khong = nk.gan_commit(muc, [_c("abc", "2026-09-05T09:30:00+07:00")])
    assert khong == []
    assert "commit" not in muc[0] and muc[1]["commit"][0]["ma"] == "abc"


def test_commit_KHONG_gan_cho_loi_nhac_khong_dung_de_tai():
    """Loi nhac cua du an khac ngay truoc commit khong duoc nhan commit."""
    muc = [{"thoi_gian": "2026-09-05T01:00:00Z", "loi_nhac": "dự án",
            "tep_da_ghi": [], "dung_de_tai": True},
           {"thoi_gian": "2026-09-05T02:00:00Z", "loi_nhac": "dự án khác",
            "tep_da_ghi": [], "dung_de_tai": False}]
    nk.gan_commit(muc, [_c("abc", "2026-09-05T09:30:00+07:00")])
    assert muc[0]["commit"][0]["ma"] == "abc" and "commit" not in muc[1]


def test_commit_truoc_moi_loi_nhac_duoc_BAO_RA():
    muc = [{"thoi_gian": "2026-09-05T05:00:00Z", "loi_nhac": "x",
            "tep_da_ghi": [], "dung_de_tai": True}]
    khong = nk.gan_commit(muc, [_c("sớm", "2026-09-05T08:00:00+07:00")])
    assert [c["ma"] for c in khong] == ["sớm"]


def test_lenh_shell_cham_de_tai_danh_dau_dung_de_tai(tmp_path):
    """Lo hong ban 10/09: sua ma bang lenh shell thi khong co Write/Edit."""
    p = _phien(tmp_path, [
        _user("sửa bộ chấm"),
        {"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "name": "Bash",
             "input": {"command": "cd D:/Claude/meditrace-core && python - <<EOF"}}]}},
    ])
    muc = nk.doc_phien(p)
    assert muc[0]["dung_de_tai"] is True and muc[0]["tep_da_ghi"] == []


def test_bang_ghi_gio_viet_nam_va_commit():
    t = nk.dung_bang([{"thoi_gian": "2026-09-05T15:15:00Z", "loi_nhac": "viết mã",
                       "tep_da_ghi": [], "commit": [_c("abc", "2026-09-05T22:20:00+07:00")]}])
    assert "**22:15**" in t and "2026-09-06" not in t
    assert "Qua commit `abc`" in t and "UTC+7" in t


def test_bang_da_che_noi_dung_nhay_cam():
    t = nk.dung_bang([{"thoi_gian": "2026-09-05T15:15:00Z",
                       "loi_nhac": "ssh nguoidung@100.64.0.7 rồi sửa src",
                       "tep_da_ghi": ["src/a.py"]}])
    assert "100.64" not in t and "Số chỗ đã che:** 1" in t


# ------------------------------------------------------ kho giao diện web (29/09/2026)

def test_kho_web_tinh_la_ma_nguon_chi_o_thu_muc_ma():
    assert nk._la_ma("D:/meditrace-sentinel/src/App.tsx")
    assert nk._la_ma("D:/meditrace-sentinel/may-chu/tai-khoan.ts".replace("/", chr(92)))  # dấu gạch ngược kiểu Windows
    assert nk._la_ma("D:/meditrace-sentinel/server.ts")
    assert not nk._la_ma("D:/meditrace-sentinel/dist/server.cjs")
    assert not nk._la_ma("D:/meditrace-sentinel/README.md")
    assert not nk._la_ma("D:/Claude/ielts-writing-task1/src/build.py")


def test_che_cum_rieng_tu_tep_ngoai_ma_nguon(tmp_path, monkeypatch):
    """Tên tài khoản, tên người nằm trong tệp riêng (không nằm trong mã đưa công khai)."""
    tep = tmp_path / "che-them.txt"
    tep.write_text("# ghi chú" + chr(10) + "TaiKhoanThu" + chr(10), encoding="utf-8")
    monkeypatch.setattr(nk, "TEP_CHE_THEM", tep)
    van, so = nk.che_nhay_cam("vào TaiKhoanThu rồi thử; taikhoanthuX thì không che")
    assert "TaiKhoanThu" not in van and "taikhoanthuX" in van and so >= 1
    monkeypatch.setattr(nk, "TEP_CHE_THEM", tmp_path / "khong-co.txt")
    assert nk.che_nhay_cam("TaiKhoanThu")[0] == "TaiKhoanThu"        # không có tệp: không che thêm, không lỗi


def test_che_dia_chi_tam_va_tep_khoa_cham_mu():
    van, so = nk.che_nhay_cam("link https://abc-def-ghi.trycloudflare.com, mở " + "khoa" + "-phieu.json")
    assert "trycloudflare" not in van and ("khoa" + "-phieu") not in van and so >= 2


def test_ban_ghi_chi_co_anh_khong_thanh_loi_nhac():
    assert nk._van_ban([{"type": "text", "text": "[Image: source: C:\a\b.png]"}]) == ""
    con_chu = nk._van_ban([{"type": "text", "text": "[Image: source: x.png]\nlàm giúp tôi"}])
    assert con_chu == "làm giúp tôi"
