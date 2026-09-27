# -*- coding: utf-8 -*-
"""Dap an phai GHI LAI quan he, va bo nhan huan luyen phai giu duoc no.

VI SAO CO TEP NAY. Truoc 09/09/2026, `dap_an` khong co truong `quan_he`. Bay
`dinh_chinh` va `dien_bien` van co trong hoi thoai (337 va 339 ca trong tap
train) nhung dap an khong danh dau. Hau qua: `trich_train` day 2.231 vi du
AM va khong mot vi du DUONG, nen mo hinh hoc "khong bao gio danh dau quan he"
— dung nhu do duoc tren hoi thoai that (282/282).

Loi do im lang hoan toan: JSON hop le, huan luyen chay, mat mat giam. Nen no
can mot test chu khong the trong vao mat nguoi doc.
"""
import json

from src import du_lieu_trich, sinh_hoi_thoai_viet as sh


def _ca_co_bay(bay, so_thu=400, seed=42):
    """Sinh cho toi khi gap mot ca mang bay can. Tra ca DAU TIEN gap."""
    for c in sh.sinh_bo(so_thu, seed=seed):
        if bay in c["bay"]:
            return c
    raise AssertionError(f"khong sinh duoc ca mang bay {bay} trong {so_thu} ca")


# --------------------------------------------------- dap an co ghi quan he

def test_dinh_chinh_ghi_lai_ca_hai_ban():
    """Ban cu phai con trong dap an va bi danh dau, khong duoc xoa.

    Xoa ban cu di thi benh an van dung, nhung mat sach dau vet — khong co gi
    de mo hinh hoc va khong co gi de do.
    """
    c = _ca_co_bay("dinh_chinh")
    cu = [m for m in c["dap_an"] if m["trang_thai"] == "bị thay thế"]
    moi = [m for m in c["dap_an"] if m["quan_he"] == "đính chính"]
    assert len(cu) == 1 and len(moi) == 1
    assert cu[0]["noi_dung"] == moi[0]["noi_dung"]
    assert cu[0]["moc_thoi_gian"] != moi[0]["moc_thoi_gian"]
    assert c["dap_an"][moi[0]["quan_he_voi"]] is cu[0] or \
        c["dap_an"][moi[0]["quan_he_voi"]] == cu[0]


def test_dien_bien_giu_ca_hai_con_hieu_luc():
    """Day la cho khac nhau CO BAN giua dien bien va dinh chinh."""
    c = _ca_co_bay("dien_bien")
    db = [m for m in c["dap_an"] if m["quan_he"] == "diễn biến"]
    assert len(db) >= 1
    for m in db:
        kia = c["dap_an"][m["quan_he_voi"]]
        assert m["trang_thai"] == "còn hiệu lực"
        assert kia["trang_thai"] == "còn hiệu lực"
        assert m["moc_thoi_gian"] != kia["moc_thoi_gian"]


def test_ban_bi_thay_the_khong_vao_benh_an_tham_chieu():
    """Benh an tham chieu phai giu NGUYEN nhu truoc khi them truong quan he.

    Neu ban bi thay the lot vao benh an thi moi con so ROUGE do truoc day het
    so sanh duoc — va do la mot thay doi im lang.
    """
    c = _ca_co_bay("dinh_chinh")
    cu = [m for m in c["dap_an"] if m["trang_thai"] == "bị thay thế"][0]
    moc_cu = cu["moc_thoi_gian"]
    moi = [m for m in c["dap_an"] if m["quan_he"] == "đính chính"][0]
    assert f"({moc_cu})" not in c["output"]
    assert f"({moi['moc_thoi_gian']})" in c["output"]


def test_quan_he_voi_luon_tro_toi_chi_so_hop_le():
    for c in sh.sinh_bo(200, seed=42):
        for i, m in enumerate(c["dap_an"]):
            if m["quan_he"]:
                j = m["quan_he_voi"]
                assert j is not None, f"{c['id']}: co quan he ma khong co dich"
                assert 0 <= j < len(c["dap_an"]), f"{c['id']}: dich ngoai bang"
                assert j != i, f"{c['id']}: tro vao chinh no"


def test_ca_khong_mang_bay_thi_khong_co_quan_he():
    """Doi chung. Mot bo sinh gan quan he cho moi ca se lam moi phep do sau do
    mat nghia — phai co ca SACH de biet nhan khong bi ram."""
    # Lay danh sach tu HANG SO, khong go tay: go tay thi them bay moi la doi
    # chung am tham bo sot va test van xanh. Da xay ra dung the khi them
    # `mau_thuan` va `bo_sung` ngay 11/09/2026.
    sach = [c for c in sh.sinh_bo(200, seed=42)
            if not set(c["bay"]) & set(sh.BAY_SINH_QUAN_HE)]
    assert sach, "khong sinh duoc ca sach nao de doi chung"
    for c in sach:
        assert all(m["quan_he"] is None for m in c["dap_an"]), c["id"]
        assert all(m["trang_thai"] == "còn hiệu lực" for m in c["dap_an"])


# ------------------------------------------- bo nhan huan luyen giu quan he

def test_bo_nhan_huan_luyen_giu_quan_he():
    c = _ca_co_bay("dien_bien")
    _, dap_an = du_lieu_trich.doi_mot_ca(c)
    ps = json.loads(dap_an)["phat_bieu"]
    co = [p for p in ps if p["quan_he"] != "không"]
    assert co, "quan he bi mat khi dung bo nhan huan luyen"


def test_anh_xa_lai_chi_so_khi_bo_menh_de_khong_co_bang_chung():
    """Vong lap bo menh de khong co bang chung, nen chi so bi xe dich.

    Khong anh xa lai thi quan he tro sang mot ban ghi khac han — JSON van hop
    le, mo hinh van hoc duoc, chi la hoc sai. Day la loi im lang.
    """
    ca = {
        "id": "thu",
        "input": "Bác sĩ: Sao ạ?\nBệnh nhân: Sốt bốn ngày.\n"
                 "Bệnh nhân: À không, hai ngày.",
        "dap_an": [
            # menh de 0 KHONG co bang chung -> bi bo
            {"chu_the": "bệnh nhân", "noi_dung": "bỏ", "muc": "BỆNH SỬ HIỆN TẠI",
             "luot": [], "quan_he": None, "quan_he_voi": None,
             "trang_thai": "còn hiệu lực"},
            # menh de 1 -> chi so moi 0
            {"chu_the": "bệnh nhân", "noi_dung": "sốt", "muc": "BỆNH SỬ HIỆN TẠI",
             "moc_thoi_gian": "bốn ngày", "luot": [2],
             "quan_he": None, "quan_he_voi": None, "trang_thai": "bị thay thế"},
            # menh de 2 -> chi so moi 1, tro ve menh de 1
            {"chu_the": "bệnh nhân", "noi_dung": "sốt", "muc": "BỆNH SỬ HIỆN TẠI",
             "moc_thoi_gian": "hai ngày", "luot": [2, 3],
             "quan_he": "đính chính", "quan_he_voi": 1,
             "trang_thai": "còn hiệu lực"},
        ],
    }
    _, dap_an = du_lieu_trich.doi_mot_ca(ca)
    ps = json.loads(dap_an)["phat_bieu"]
    assert len(ps) == 2
    assert ps[1]["quan_he"] == "đính chính"
    assert ps[1]["quan_he_voi"] == 0, "chi so chua duoc anh xa lai"


def test_ha_ve_khong_khi_dich_bi_bo():
    """Quan he tro vao khoang khong nguy hiem hon la khong co quan he."""
    ca = {
        "id": "thu",
        "input": "Bác sĩ: Sao ạ?\nBệnh nhân: Sốt.",
        "dap_an": [
            {"chu_the": "bệnh nhân", "noi_dung": "cũ", "muc": "BỆNH SỬ HIỆN TẠI",
             "luot": [], "quan_he": None, "quan_he_voi": None,
             "trang_thai": "còn hiệu lực"},
            {"chu_the": "bệnh nhân", "noi_dung": "sốt", "muc": "BỆNH SỬ HIỆN TẠI",
             "luot": [2], "quan_he": "đính chính", "quan_he_voi": 0,
             "trang_thai": "còn hiệu lực"},
        ],
    }
    _, dap_an = du_lieu_trich.doi_mot_ca(ca)
    ps = json.loads(dap_an)["phat_bieu"]
    assert len(ps) == 1
    assert ps[0]["quan_he"] == "không"
    assert ps[0]["quan_he_voi"] is None


# ------------------------------------------- tinh huong "gia dinh" (thach thuc 3)

def test_bay_gia_dinh_ghi_menh_de_gia_dinh():
    """Cung ho loi voi `quan_he`: bay co trong hoi thoai nhung dap an khong ghi.

    Truoc 09/09/2026, `tinh_huong` chi co DUNG hai gia tri tren ca 19.035 menh
    de: "thuc te" va "ke hoach". Mo hinh trich chua bao gio nhin thay mot vi du
    "gia dinh" nao — do la ly do day du cua viec nhanh C chi dat 53% o nhom
    `gia_dinh` trong khi nhanh A dat 87%.
    """
    c = _ca_co_bay("gia_dinh")
    gd = [m for m in c["dap_an"] if m["tinh_huong"] == "giả định"]
    assert gd, f"{c['id']}: mang bay gia_dinh ma dap an khong co menh de gia dinh"


def test_menh_de_gia_dinh_khong_vao_benh_an_tham_chieu():
    """Cau dieu kien KHONG duoc thanh trieu chung trong benh an."""
    c = _ca_co_bay("gia_dinh")
    for m in c["dap_an"]:
        if m["tinh_huong"] != "giả định":
            continue
        # Noi dung co the trung voi mot trieu chung THAT cua ca do, nen chi
        # kiem duoc khi no KHONG xuat hien duoi dang menh de thuc te nao khac.
        that = [x for x in c["dap_an"]
                if x["tinh_huong"] == "thực tế" and x["noi_dung"] == m["noi_dung"]]
        if not that:
            assert m["noi_dung"] not in c["output"], c["id"]


def test_ca_khong_mang_bay_gia_dinh_thi_khong_co_menh_de_gia_dinh():
    sach = [c for c in sh.sinh_bo(200, seed=42) if "gia_dinh" not in c["bay"]]
    assert sach
    for c in sach:
        assert all(m["tinh_huong"] != "giả định" for m in c["dap_an"]), c["id"]


# ----------------------- hai quan he khai tu dau ma khong co vi du nao
#
# Do ngay 11/09/2026 tren CA 43.687 menh de cua bo 5.000:
#
#     bo sung       0 vi du      <-- khai trong luoc do, khong co du lieu
#     dinh chinh  784  (1,79%)
#     dien bien   795  (1,82%)
#     mau thuan     0 vi du      <-- khai trong luoc do, khong co du lieu
#
# va `trang_thai` chi co hai gia tri, khong co `chua giai quyet`. Tai lieu thi
# khai ca bon quan he va ca ba trang thai nhu nhau, kem so do chuyen trang thai
# co mui "mau thuan -> chua giai quyet". Do la KHAI QUA.
#
# Nang hon: `phan_quan_he` cho mo hinh chon giua 5 nhan, trong do hai nhan khong
# co mot vi du duong nao — chung chi la nguon nhieu.

def test_MOI_quan_he_khai_trong_luoc_do_deu_co_vi_du():
    """Mot nhan khai ra ma khong co du lieu thi khong hoc duoc, khong do duoc,
    va bao cao noi ve no la noi qua."""
    from collections import Counter
    from src import phat_bieu
    c = Counter(m["quan_he"] for x in sh.sinh_bo(600, seed=77)
                for m in x["dap_an"])
    thieu = [q for q in phat_bieu.QUAN_HE if not c.get(q)]
    assert not thieu, f"quan he khong co vi du nao: {thieu}"


def test_MOI_trang_thai_khai_trong_luoc_do_deu_co_vi_du():
    from collections import Counter
    from src import phat_bieu
    c = Counter(m["trang_thai"] for x in sh.sinh_bo(600, seed=77)
                for m in x["dap_an"])
    thieu = [t for t in phat_bieu.TRANG_THAI if not c.get(t)]
    assert not thieu, f"trang thai khong co vi du nao: {thieu}"


def test_mau_thuan_KHONG_dat_bi_thay_the():
    """Mau thuan chua giai quyet thi KHONG ban nao thang. Dat "bi thay the" la
    noi rang da co ban dung — chinh la thu bay nay KHONG chua."""
    thay = 0
    for c in sh.sinh_bo(300, seed=11):
        if "mau_thuan" not in c["bay"]:
            continue
        mt = [m for m in c["dap_an"] if m["quan_he"] == "mâu thuẫn"]
        assert mt, c["id"]
        for m in mt:
            assert m["trang_thai"] == "chưa giải quyết", c["id"]
            goc = m["quan_he_voi"]
            if isinstance(goc, dict):
                assert goc["trang_thai"] == "chưa giải quyết", c["id"]
        thay += 1
    assert thay >= 10


def test_dinh_chinh_va_mau_thuan_LOAI_TRU_nhau():
    """Mot moc khong the vua da duoc dinh chinh vua dang mau thuan: dinh chinh
    nghia la da co ban thang, mau thuan nghia la chua co.

    Ca hai bay cung nham vao menh de trieu chung chinh, nen de ca hai cung chay
    thi `trang_thai` bi ghi de va dap an thanh vo nghia."""
    for c in sh.sinh_bo(400, seed=13):
        assert not ("dinh_chinh" in c["bay"] and "mau_thuan" in c["bay"]), c["id"]


def test_ban_nhap_tham_chieu_in_mau_thuan_thanh_MOT_dong_chua_ro():
    """Hai dong "sot (hon mot tuan)" va "sot (gan mot tuan)" la mot benh an doc
    qua la thay sai. Benh an that ghi mot dong, neu ro la chua ro — dung nhu cau
    bac si noi trong hoi thoai."""
    thay = 0
    for c in sh.sinh_bo(300, seed=11):
        if "mau_thuan" not in c["bay"]:
            continue
        assert "chưa rõ" in c["output"], c["id"]
        thay += 1
    assert thay >= 10


def test_bo_sung_GIU_ban_cu_con_hieu_luc():
    """`bo sung` them chi tiet, KHONG thay the. Khac `dinh_chinh` o dung cho do."""
    thay = 0
    for c in sh.sinh_bo(400, seed=13):
        bs = [m for m in c["dap_an"] if m["quan_he"] == "bổ sung"]
        if not bs:
            continue
        for m in bs:
            goc = m["quan_he_voi"]
            if isinstance(goc, dict):
                assert goc["trang_thai"] == "còn hiệu lực", c["id"]
        thay += 1
    assert thay >= 10


# ------------------- `thoi_gian_su_kien`: ho loi lan thu tu (11/09/2026)
#
# Luoc do 16 truong co `thoi_gian_su_kien`; `sinh_benh_an` co luat
# `thoi_gian_su_kien == "qua khu" -> TIEN SU BENH`; nhung dap an KHONG CO truong
# do, nen `du_lieu_trich` dong cung nhan thanh "chua ro", mo hinh hoc mot gia tri
# duy nhat va xuat "chua ro" o ca 462 phat bieu. Luat tren la MA CHET.
#
# Hau qua do duoc: muc TIEN SU BENH co 28/60 ca trong ban tham chieu va 0 trong
# ban nhap cua moi nhanh.

def test_dap_an_CO_truong_thoi_gian_su_kien():
    """Them truong vao `MenhDe` ma quen danh sach truong trong `_dap_an` thi dap
    an khong mang no, va khong co gi bao loi. Da xay ra dung the: lan dau, ca
    4.533 menh de deu co `thoi_gian_su_kien = None`."""
    for m in sh.sinh_bo(40, seed=3):
        for d in m["dap_an"]:
            assert "thoi_gian_su_kien" in d, m["id"]
            assert d["thoi_gian_su_kien"] is not None, m["id"]


def test_MOI_gia_tri_thoi_gian_su_kien_deu_co_vi_du():
    """Mot nhan chi co mot gia tri thi khong day duoc gi — dung chuyen da xay ra
    voi `quan_he` hom 09/09."""
    from collections import Counter
    c = Counter(d["thoi_gian_su_kien"] for m in sh.sinh_bo(300, seed=77)
                for d in m["dap_an"])
    for v in ("hiện tại", "quá khứ", "chưa rõ"):
        assert c.get(v), f"{v} khong co vi du nao"


def test_muc_TIEN_SU_BENH_luon_la_qua_khu():
    """Day la nhan ma luat cua `sinh_benh_an` doc. Lech mot ca la luat doc sai."""
    for m in sh.sinh_bo(200, seed=5):
        for d in m["dap_an"]:
            if d["muc"] == "TIỀN SỬ BỆNH":
                assert d["thoi_gian_su_kien"] == "quá khứ", (m["id"], d["noi_dung"])


def test_muc_KHAM_va_CHAN_DOAN_la_hien_tai():
    for m in sh.sinh_bo(200, seed=5):
        for d in m["dap_an"]:
            if d["muc"] in ("KHÁM LÂM SÀNG", "CHẨN ĐOÁN"):
                assert d["thoi_gian_su_kien"] == "hiện tại", (m["id"], d["muc"])


def test_nhan_huan_luyen_DOC_tu_dap_an_khong_dong_cung():
    """`du_lieu_trich` tung dong cung truong nay thanh mac dinh."""
    import json
    from src import du_lieu_trich
    ca = sh.sinh_bo(6, seed=9)
    co_qua_khu = False
    for k in ca:
        _, nhan = du_lieu_trich.doi_mot_ca(k)
        for p in json.loads(nhan)["phat_bieu"]:
            assert "thoi_gian_su_kien" in p
            co_qua_khu = co_qua_khu or p["thoi_gian_su_kien"] == "quá khứ"
    assert co_qua_khu, "nhan huan luyen khong mang mot gia tri nao khac mac dinh"
