# -*- coding: utf-8 -*-
"""Test cho bo sinh hoi thoai kham benh Viet Nam.

Bo sinh du lieu co dap an thi BAN THAN no phai co test, va phai test ca hai
chieu. Bai hoc o `meditrace`: tung viet mot test KHANG DINH mot lo hong la
dung — test bao ve lo hong con te hon khong co test.

Bon cai bay cua meditrace deu co test rieng o day, cong voi mot nhom test ve
NGON NGU: mot bo du lieu tieng Viet sai vai giao tiep thi mo hinh se hoc dung
cai sai do, va no vo dung cho mot du an ve tieng Viet.
"""
import collections
import random
import re
import statistics

from src import phuong_ngu
from src import sinh_hoi_thoai_viet as sh
from src.phat_bieu import HANH_VI


def bo(n=160, seed=7):
    return sh.sinh_bo(n, seed=seed)


# --------------------------------------------------------- tai lap duoc

def test_cung_seed_ra_cung_ket_qua():
    assert sh.sinh_bo(25, seed=3) == sh.sinh_bo(25, seed=3)


def test_khac_seed_ra_khac_ket_qua():
    assert sh.sinh_bo(25, seed=3) != sh.sinh_bo(25, seed=4)


# ------------------------------------- benh an khong duoc chua thong tin la

def test_benh_an_chi_gom_thong_tin_da_noi_ra():
    """Rang buoc cot loi. Hoi thoai va benh an ra tu CUNG mot kich ban, nen
    khong duoc phep co menh de nao khong ai noi."""
    for m in bo(60):
        loi_thoai = m["input"].lower()
        for d in m["dap_an"]:
            assert d["luot"], f"{m['id']}: menh de khong co luot bang chung"
            assert max(d["luot"]) <= m["so_luot"], f"{m['id']}: luot vuot so luot"
        # Moi muc trong benh an phai co menh de tuong ung
        for dong in m["output"].split("\n"):
            d = dong.strip()
            if d and d == d.upper() and len(d) < 60:
                assert d in sh.MUC, f"{m['id']}: muc la {d!r}"


# --------------------------------------------- BAY: quy gan cho dung nguoi

def test_tien_su_nguoi_nha_KHONG_bi_gan_cho_benh_nhan():
    """Bay quan trong nhat cua ca bo du lieu. Nguoi nha ke benh CUA HO xen vao
    giua — dap an phai ghi ten nguoi do, khong duoc ghi la benh nhan."""
    thay = 0
    for m in bo(200):
        if "tien_su_gia_dinh" not in m["bay"]:
            continue
        gd = [d for d in m["dap_an"] if d["muc"] == "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI"]
        assert gd, f"{m['id']}: co bay ma khong co menh de tien su gia dinh"
        for d in gd:
            assert d["chu_the"] != "bệnh nhân", f"{m['id']}: gan cho benh nhan"
            thay += 1
    assert thay >= 5


def test_di_ung_cua_nguoi_nha_khong_thanh_di_ung_cua_benh_nhan():
    thay = 0
    for m in bo(300):
        if "di_ung_nguoi_nha" not in m["bay"]:
            continue
        # CHI xet hai muc ma bay nay sinh ra. Ban dau quet moi menh de co chu
        # "di ung" va no bat nham "di ung dam sua bo" — mot tien su THAT cua
        # em be, nam o muc TIEN SU BENH va gan cho benh nhan la dung.
        du = [d for d in m["dap_an"]
              if "dị ứng" in d["noi_dung"]
              and d["muc"] in ("DỊ ỨNG", "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI")]
        for d in du:
            if d["chu_the"] == "bệnh nhân":
                # "Chua thay bi bao gio" la `chua ghi nhan` tu 11/09/2026 (truoc
                # do la `phu_dinh=True`). Y cua test khong doi: benh nhan KHONG
                # duoc mang di ung cua nguoi nha.
                assert d["phu_dinh"] or d["do_chac_chan"] == "chưa ghi nhận", \
                    f"{m['id']}: gan di ung cho benh nhan"
        assert any(d["chu_the"] != "bệnh nhân" for d in du), m["id"]
        thay += 1
    assert thay >= 3


# ------------------------------------------------- BAY: dinh chinh, dien bien

def _ve_chuan(cum):
    """Doi cac tu phuong ngu trong `cum` ve dang chuan cua ban tham chieu."""
    from src import phuong_ngu as _pn

    for _vung, cap in _pn.THAY_DUOC.items():
        for chuan, dia_phuong in cap:
            cum = cum.replace(dia_phuong, chuan)
    return cum


def test_dinh_chinh_chi_giu_moc_da_sua():
    """Benh an phai giu con so DUNG. Giu ca hai la sai — nguoi noi da tu nhan
    con so dau la nham.

    MOC LAY TU HOI THOAI PHAI QUY VE CHUAN TRUOC KHI DOI CHIEU. Hoi thoai co the
    da qua tang vung: ca hv_0042 noi "tu hom te" trong khi ban tham chieu ghi
    "tu hom kia". Doi chieu thang chuoi hoi thoai voi ban tham chieu la doi hoi
    dap an phai mang tu phuong ngu — dung nguoc voi bat bien cua du an ("hoi
    thoai dan da, dap an giu thuat ngu chuan"). Lo~i nay co san trong phep kiem tu
    truoc, chi khong lo ra vi cac hat giong cu khong roi vao ca phuong ngu nao."""
    thay = 0
    for m in bo(200):
        if "dinh_chinh" not in m["bay"]:
            continue
        # Tim luot dinh chinh bang khuon "X chu khong phai Y" — chung cho ca ba
        # cach noi tu 11/09/2026 ("A khong, ...", "Xin loi bac si, ...", "...
        # noi lai cho dung, ..."). Lay ve NGAY TRUOC "chu khong phai", tinh tu
        # dau phay gan nhat.
        dong = [l for l in m["input"].split("\n") if "chứ không phải" in l][0]
        moc = re.findall(r"([^,]+?) chứ không phải ([^,]+?)\s*\.?\s*$", dong)
        assert moc, f"{m['id']}: {dong}"
        dung = _ve_chuan(moc[0][0].strip())
        sai = _ve_chuan(re.sub(r"\s+(ạ|nhé|nha|nghen|nghe)$", "", moc[0][1].strip()))
        assert dung in m["output"], f"{m['id']}: thieu moc da sua {dung!r}"
        assert f"({sai})" not in m["output"], f"{m['id']}: con giu moc sai {sai!r}"
        thay += 1
    assert thay >= 5


def test_dien_bien_GIU_CA_HAI_moc():
    """Cho de sai nhat cua ca du an: coi dien bien la dinh chinh roi vut mat
    moc dau. Hai moc deu dung, phai giu ca hai."""
    thay = 0
    for m in bo(200):
        if "dien_bien" not in m["bay"]:
            continue
        moc = [d["moc_thoi_gian"] for d in m["dap_an"]
               if d["moc_thoi_gian"] and d["muc"] == "BỆNH SỬ HIỆN TẠI"]
        assert len(set(moc)) >= 2, f"{m['id']}: chi giu mot moc"
        thay += 1
    assert thay >= 5


def test_cau_gia_dinh_KHONG_thanh_trieu_chung_da_xay_ra():
    """Cau dieu kien phai duoc GHI LAI voi nhan "gia dinh", va KHONG duoc vao
    benh an nhu mot trieu chung da xay ra.

    SUA 09/09/2026. Ban truoc cua test nay khang dinh cau gia dinh khong sinh
    ra menh de NAO CA. Dieu do giu benh an dung, nhung lam dap an khong co mot
    vi du "gia dinh" nao tren ca 19.035 menh de — trong khi luoc do trich
    (`bakeoff.LUOC_DO`), loi nhac (`bakeoff.HUONG_DAN`: *"Neu mai van dau
    thi..." la "gia dinh"*) va `sinh_benh_an` (day menh de gia dinh xuong muc
    CAN XAC NHAN) deu MONG DOI co ban ghi nhu vay. Bo sinh la cho lech.

    Y dinh cua test khong doi: cau dieu kien khong duoc thanh trieu chung that.
    Chi cach kiem doi — tu "khong co ban ghi" thanh "co ban ghi, danh dau dung,
    va khong lot vao benh an".
    """
    thay = 0
    for m in bo(200):
        if "gia_dinh" not in m["bay"]:
            continue
        dk = [l for l in m["input"].split("\n") if l.startswith("Bác sĩ: Nếu mai")]
        assert dk, m["id"]
        gd = [d for d in m["dap_an"] if d["tinh_huong"] == "giả định"]
        assert gd, f"{m['id']}: cau dieu kien khong duoc ghi lai"
        for d in gd:
            # Khong duoc vao benh an — TRU khi chinh trieu chung do cung duoc
            # noi ra o cho khac nhu mot su that (bo sinh chon dieu kien tu
            # `benh["chinh"]`, nen trung la chuyen binh thuong).
            that = [x for x in m["dap_an"]
                    if x["tinh_huong"] == "thực tế"
                    and x["noi_dung"] == d["noi_dung"]]
            if not that:
                assert d["noi_dung"] not in m["output"], m["id"]
        thay += 1
    assert thay >= 5


def test_hoi_khong_dap_thi_benh_an_khong_nhac_toi():
    thay = 0
    for m in bo(200):
        if "hoi_khong_dap" not in m["bay"]:
            continue
        for tu in ("đi đâu xa", "ngủ nghỉ", "Ăn uống dạo này"):
            if tu.lower() in m["input"].lower():
                assert tu.lower() not in m["output"].lower(), m["id"]
        thay += 1
    assert thay >= 5


# ------------------------------ BAY CUA MEDITRACE: do dai va vi tri lo dap an

NGUONG_DOAN_BANG_DO_DAI = 0.72


def test_do_dai_KHONG_lo_ca_nao_co_bay():
    """Bay so 3 cua meditrace: neu ca co bay dai hon han thi dem so luot la doan
    duoc dap an, va moi ket qua do duoc deu lan mot phan "doan theo do dai".

    PHEP KIEM NAY DA DUOC VIET LAI 12/09/2026, va ly do phai ghi lai.

    Ban cu doi khoang [min, max] cua nhom KHONG bay nam gon trong khoang cua nhom
    CO bay. Doi hoi do gan nhu khong the dat duoc VE MAT CAU TRUC: mot bay bao gio
    cung them it nhat mot luot vao cai nen, nen `min(co)` co xu huong bang
    `min(khong) + 1`. Va vi min/max la cuc tri cua mau, chi MOT ca ngan trong nhom
    khong bay la do — phep kiem do doi theo hat giong chu khong theo chat luong bo
    du lieu. No da do va xanh xen ke nhau giua cac lan chay.

    Ban moi do THANG cai dang lo ngai: lay so luot lam dac trung duy nhat, tim
    nguong tot nhat, xem no doan "ca nay co bay khong" chinh xac den dau (can
    bang giua hai nhom). 0,50 la doan bua; 1,00 la do dai lo hoan toan.

    SO DO THAT, 500 ca moi lan, ba hat giong (12/09/2026):
        truoc khi chen xa giao : 0,673 · 0,647 · 0,709
        sau khi chen xa giao   : 0,642 · 0,642 · 0,678

    PHAI NOI RO TRONG BAO CAO: con 0,64-0,68 chu khong ve 0,50. Ca mang bay von
    mang nhieu noi dung hon, nen mot phan chenh lech la ban chat chu khong phai
    lo~i. Cach bit han la don do dai moi ca ve mot muc chung, nhung lam vay thi
    hoi thoai dai them khoang 25% — va do dai train da dat 3072 vi nhan the he 5,
    nen day them la co nguy co LOAI MAU AM THAM, dung lo~i da vap o 2048. Chon giu
    muc hien tai va ghi lai gioi han, thay vi doi mot rui ro da biet lay mot con so
    dep hon.
    """
    ds = bo(400)
    co = [m["so_luot"] for m in ds if m["bay"] not in ([], ["nguoi_nha_ke_ho"])]
    khong = [m["so_luot"] for m in ds if m["bay"] in ([], ["nguoi_nha_ke_ho"])]
    assert len(co) > 30 and len(khong) > 10

    # Hai khoang phai PHU LEN NHAU that su — khong doi cai nay chua cai kia.
    phu = min(max(co), max(khong)) - max(min(co), min(khong))
    rong = max(max(co), max(khong)) - min(min(co), min(khong))
    assert phu >= 0.6 * rong, (
        f"hai phan bo tach nhau: co bay {min(co)}-{max(co)}, "
        f"khong bay {min(khong)}-{max(khong)}")

    tot_nhat = 0.0
    for nguong in range(min(co + khong), max(co + khong) + 1):
        dung_co = sum(1 for x in co if x >= nguong) / len(co)
        dung_khong = sum(1 for x in khong if x < nguong) / len(khong)
        tot_nhat = max(tot_nhat, (dung_co + dung_khong) / 2)
    assert tot_nhat <= NGUONG_DOAN_BANG_DO_DAI, (
        f"doan bay bang do dai dat {tot_nhat:.3f} "
        f"(nguong {NGUONG_DOAN_BANG_DO_DAI}) — do dai dang lo dap an")


def test_xa_giao_KHONG_sinh_menh_de():
    """Doan xa giao them vao chi de lam loang do dai — no KHONG duoc sinh menh de.

    Neu mot ngay nao do no sinh, dap an dai them ma khong ai co y do, va ban
    tham chieu se doi theo mot cach khong ai nhin thay."""
    from src import ngu_lieu_viet as nl

    cac_cau = {d.strip() for cap in nl.XA_GIAO for d in cap}
    for m in bo(120):
        for md in m["dap_an"]:
            for t in md.get("trich_dan") or []:
                assert t.strip() not in cac_cau, f"{m['id']}: {t!r} la cau xa giao"
            noi_dung = (md.get("noi_dung") or "").strip()
            assert noi_dung not in cac_cau, f"{m['id']}: {noi_dung!r} la cau xa giao"


def test_bay_khong_dinh_o_mot_vi_tri_co_dinh():
    """Bay so 4 cua meditrace. Neu bay luon o cuoi thi vi tri thanh manh moi."""
    vi_tri = []
    for m in bo(300):
        if "tien_su_gia_dinh" not in m["bay"]:
            continue
        luot = [d["luot"][0] for d in m["dap_an"]
                if d["muc"] == "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI"]
        if luot:
            vi_tri.append(luot[0] / m["so_luot"])
    assert len(vi_tri) >= 10
    assert statistics.pstdev(vi_tri) > 0.03, "vi tri bay qua co dinh"


# -------------------------------------------------- NGON NGU: vai giao tiep

def test_benh_nhan_khong_dung_tu_dem_cua_nguoi_tren():
    """"Ừ" / "Rồi" la loi nguoi tren noi voi nguoi duoi. Benh nhan va nguoi nha
    khong dung voi bac si. Sai cho nay la sai vai giao tiep, va mot bo du lieu
    tieng Viet sai vai thi vo dung cho mot du an ve tieng Viet."""
    for m in bo(200):
        for dong in m["input"].split("\n"):
            if dong.startswith(("Bệnh nhân:", "Người nhà:")):
                loi = dong.split(":", 1)[1].strip()
                assert not loi.startswith(("Ừ", "Rồi,", "Được rồi")), \
                    f"{m['id']}: {dong}"


def test_cau_hoi_khong_gan_tieu_tu_de_nghi():
    """"nhé", "nghen", "nha" la tieu tu DE NGHI. Gan vao cau hoi thi sai nga:
    "Gia dinh co ai bi benh gi khong nhe?" khong phai tieng Viet."""
    xau = []
    for m in bo(200):
        for dong in m["input"].split("\n"):
            if re.search(r"(nhé|nha|nghen|nghe|hen|đấy)\s*\?\s*$", dong):
                xau.append(dong)
    assert not xau, xau[:3]


def test_khong_tron_tieu_tu_hai_mien_trong_mot_cuoc():
    """"Vâng ... nghen" trong mot cau la tron giong Bac voi Nam. Chon mot vung
    cho ca cuoc hoi thoai, khong boc ngau nhien tung cau."""
    # Chi xet tieu tu o CUOI CAU. Ban dau tim "hen" o bat cu dau — va no bat
    # nham chu "hen" trong "hen phe quan", mot ten benh. Test bat nham thi
    # nguoi doc se di sua bo sinh dang dung.
    cuoi_cau = re.compile(r"(?<![\w])(nghen|hen|nha)\s*[.?!]?\s*$")
    for m in bo(200):
        co_bac = "Vâng" in m["input"]
        co_nam = any(cuoi_cau.search(d) for d in m["input"].split("\n"))
        assert not (co_bac and co_nam), f"{m['id']}: trộn miền"


def test_khong_co_dau_cau_lap():
    for m in bo(200):
        assert ".." not in m["input"], m["id"]
        assert " ," not in m["input"] and ",," not in m["input"], m["id"]


def test_benh_cua_tre_em_hop_lua_tuoi():
    """Mot em be "co roi loan mo mau" thi bac si doc qua la thay sai ngay."""
    cam = ("rối loạn mỡ máu", "tăng huyết áp", "đái tháo đường", "gout",
           "sỏi thận", "viêm gan B")
    for m in bo(300):
        if not m["la_tre_em"]:
            continue
        ts = [d["noi_dung"] for d in m["dap_an"] if d["muc"] == "TIỀN SỬ BỆNH"]
        for t in ts:
            assert t not in cam, f"{m['id']}: tre em co {t!r}"


# ------------------------------------------------------------- da dang

def test_du_da_dang_de_khong_phai_mot_khuon_lap_lai():
    ds = bo(300)
    assert len({m["benh"] for m in ds}) >= 18
    assert len({m["input"] for m in ds}) == len(ds), "co hoi thoai trung nhau"
    assert len({m["so_luot"] for m in ds}) >= 6


# ------------------------------------------------- bay tang 4 (10/09/2026)

def test_bay_tang_4_khong_nam_trong_bo_rut_ngau_nhien():
    """`rng.sample(BAY, k=n)` chia deu cho moi phan tu. Them mot bay vao bo rut
    la moi bay cu mat 1/9 ty le, va the la bo moi khong con so sanh duoc voi bo
    cu. Nen `nguoi_ke_benh_minh` phai bat RIENG — va tu 11/09/2026 ca
    `nguon_khac_nhau` cung vay."""
    assert "nguoi_ke_benh_minh" in sh.BAY
    assert "nguoi_ke_benh_minh" not in sh.BAY_RUT
    assert set(sh.BAY_RUT) == set(sh.BAY) - set(sh.BAY_BAT_RIENG)


def test_bay_tang_4_chi_bat_khi_CO_nguoi_nha_ke():
    """Khong co nguoi nha thi khong the co "nguoi nha ke ve chinh minh"."""
    for m in bo(400):
        if "nguoi_ke_benh_minh" in m["bay"]:
            assert m["nguoi_ke"], m["id"]


def test_bay_tang_4_sinh_menh_de_CHU_THE_KHONG_phai_benh_nhan():
    """Day la ca duy nhat ma ca hai duong tat deu sai, nen dap an phai ghi chu
    the la nguoi ke chu khong phai benh nhan."""
    thay = 0
    for m in bo(400):
        if "nguoi_ke_benh_minh" not in m["bay"]:
            continue
        khac = [d for d in m["dap_an"]
                if d["muc"] == "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI"
                and d["chu_the"] != "bệnh nhân"]
        assert khac, m["id"]
        thay += 1
    assert thay >= 20, f"bay tang 4 chi bat {thay} lan tren 400 ca"


def test_ty_le_tang_4_da_tang_so_voi_muc_do_duoc_truoc_day():
    """Do truoc khi sua: 1,91% (bo 3.000) va 2,32% (bo 5.000) so menh de.

    Nguong 3% dat THAP hon muc do duoc (3,66%) co y: test nay canh viec tut
    lai, khong phai khoa cung mot con so.

    Nguoi noi lay o luot CUOI cua bang chung — giong `phat_bieu.tu_json` va
    `do_tang_quy_gan` (xem do).
    """
    ds = bo(500)
    tong = tang4 = 0
    for m in ds:
        vai = {}
        for i, d in enumerate([x for x in m["input"].split("\n") if x.strip()], 1):
            mm = re.match(r"^([^:]{1,30}):", d)
            vai[i] = mm.group(1).strip().lower() if mm else "?"
        for md in m["dap_an"]:
            lt = md.get("luot") or []
            if not lt:
                continue
            tong += 1
            if (vai.get(max(lt)) not in ("bác sĩ", "bệnh nhân")
                    and md["chu_the"] != "bệnh nhân"):
                tang4 += 1
    assert tong
    assert tang4 / tong >= 0.03, f"ty le tang 4 chi {tang4 / tong:.2%}"


# ------------------------------- phat bieu nguyen tu: trich dan (11/09/2026)

def _cac_luot(m):
    return [x.split(":", 1)[1].strip() for x in m["input"].split("\n")
            if x.strip()]


def test_moi_menh_de_co_TRICH_DAN_thang_hang_voi_luot():
    for m in bo(200):
        for d in m["dap_an"]:
            assert len(d["trich_dan"]) == len(d["luot"]), (m["id"], d)


def test_trich_dan_la_CHUOI_CON_NGUYEN_VAN_cua_DUNG_luot():
    """Trich dan phai kiem duoc bang MAY: khong nam trong luot duoc dan thi
    khong phai bang chung. Tang khoa bang chung dua dung vao dieu nay."""
    for m in bo(200):
        luot = _cac_luot(m)
        for d in m["dap_an"]:
            for so, td in zip(d["luot"], d["trich_dan"]):
                assert td and td in luot[so - 1], (m["id"], so, td)


def test_hai_menh_de_KHAC_noi_dung_chung_mot_luot_trich_HAI_doan_khac_nhau():
    """Ly do ton tai cua `trich_dan`: 39,8% menh de nam chung luot voi menh de
    khac (do tren train the he 4), nen so luot khong chi ra duoc doan nao.

    Bo qua cap ma noi dung nay CHUA noi dung kia: bay `bo_sung` noi "X" roi "X
    nhieu hon ve dem" trong CUNG mot doan, va trich cung doan la dung.
    """
    cap = khac = 0
    for m in bo(300):
        theo_luot = collections.defaultdict(list)
        for d in m["dap_an"]:
            for so, td in zip(d["luot"], d["trich_dan"]):
                theo_luot[so].append((d["noi_dung"], td))
        for ds in theo_luot.values():
            for i in range(len(ds)):
                for j in range(i + 1, len(ds)):
                    a, b = ds[i][0], ds[j][0]
                    if a == b or a in b or b in a:
                        continue
                    cap += 1
                    khac += ds[i][1] != ds[j][1]
    assert cap >= 50, cap
    assert khac / cap >= 0.95, f"chi {khac}/{cap} cap trich hai doan khac nhau"


def test_menh_de_noi_TAT_lay_DUNG_doan():
    """Di ung nguoi nha: menh de cua benh nhan phai trich doan "con ... chua
    thay bi bao gio". So khop tu se chon nham doan cua nguoi nha, vi chi doan
    do co chu "di ung"."""
    thay = 0
    for m in bo(300):
        if "di_ung_nguoi_nha" not in m["bay"]:
            continue
        for d in m["dap_an"]:
            if d["chu_the"] == "bệnh nhân" and d["muc"] == "DỊ ỨNG":
                assert "chưa thấy bị bao giờ" in d["trich_dan"][-1], \
                    (m["id"], d["trich_dan"])
                thay += 1
    assert thay >= 3


def test_dien_bien_hai_menh_de_trich_HAI_doan_khac_nhau():
    thay = 0
    for m in bo(300):
        for d in m["dap_an"]:
            if d["quan_he"] != "diễn biến":
                continue
            goc = m["dap_an"][d["quan_he_voi"]]
            assert d["trich_dan"] != goc["trich_dan"], m["id"]
            # Lop phuong ngu doi moc trong LOI THOAI ("hôm kia" -> "hôm tê") con
            # dap an giu ban chuan — nen trich dan duoc mang mot bien the vung.
            moc = goc["moc_thoi_gian"].lower()
            bien_the = {moc} | {vung for ds in phuong_ngu.THAY_DUOC.values()
                                for chuan, vung in ds if chuan == moc}
            assert any(b in goc["trich_dan"][0].lower() for b in bien_the), m["id"]
            thay += 1
    assert thay >= 5


def test_cau_tra_loi_TAT_kem_luot_cau_hoi():
    """"Da, khong a" khong mang noi dung — bang chung phai gom ca cau hoi."""
    thay = 0
    for m in bo(300):
        for d in m["dap_an"]:
            if d["muc"] == "DỊ ỨNG" and d["phu_dinh"]:
                assert len(d["luot"]) == 2, (m["id"], d["luot"])
                assert d["luot"][1] == d["luot"][0] + 1, (m["id"], d["luot"])
                thay += 1
    assert thay >= 10


# ------------------------------------------ do chac chan va loai phat bieu

def test_do_chac_chan_co_DU_BA_gia_tri():
    """Ho loi lan thu sau: truoc 11/09/2026 dap an khong co truong nay va nhan
    huan luyen dong cung "chac chan" — mo hinh chua bao gio thay hai gia tri
    kia."""
    gt = collections.Counter(d["do_chac_chan"] for m in bo(400)
                             for d in m["dap_an"])
    assert set(gt) == {"chắc chắn", "nghi ngờ", "chưa ghi nhận"}, gt


def test_hanh_vi_co_DU_nam_gia_tri_va_KHONG_co_gia_tri_la():
    gt = collections.Counter(d["hanh_vi"] for m in bo(300) for d in m["dap_an"])
    assert set(gt) == set(HANH_VI), gt


def test_bay_tang_4_la_TU_KE():
    """Bay tang 4 khong co cau hoi dan vao — do la dieu lam no kho hon bay
    tien su gia dinh."""
    thay = 0
    for m in bo(400):
        if "nguoi_ke_benh_minh" not in m["bay"]:
            continue
        gd = [d for d in m["dap_an"]
              if d["muc"] == "TIỀN SỬ GIA ĐÌNH VÀ XÃ HỘI"]
        assert any(d["hanh_vi"] == "tự kể" for d in gd), m["id"]
        thay += 1
    assert thay >= 20


def test_ket_qua_kham_la_QUAN_SAT_va_chan_doan_la_NHAN_DINH():
    for m in bo(200):
        for d in m["dap_an"]:
            if d["muc"] == "KHÁM LÂM SÀNG":
                assert d["hanh_vi"] == "quan sát", (m["id"], d)
            elif d["muc"] == "CHẨN ĐOÁN":
                assert d["hanh_vi"] == "nhận định", (m["id"], d)


def test_cho_ket_qua_ghi_NHAN_DINH_muc_nghi_ngo():
    """Nang muc nhan dinh ("nghi X" -> "X") la nua nguy hiem hon cua thach thuc
    3. Truoc 11/09/2026 boi canh nay KHONG ghi nhan dinh nao, nen muc "nghi
    ngo" khong co mot vi du."""
    thay = 0
    for m in bo(400):
        if m["boi_canh"] != "cho_ket_qua":
            continue
        cd = [d for d in m["dap_an"] if d["muc"] == "CHẨN ĐOÁN"]
        assert cd and all(d["do_chac_chan"] == "nghi ngờ" for d in cd), m["id"]
        # "Nghi ngo X", hoac chinh chan doan da mang chu "nghi" ("Viem hong nghi
        # do lien cau") — khong in "Nghi ngo" hai lan.
        khoi = m["output"].split("CHẨN ĐOÁN")[1].split("\n\n")[1]
        assert "nghi" in khoi.lower(), (m["id"], khoi)
        thay += 1
    assert thay >= 10


def test_ban_tham_chieu_in_theo_DO_CHAC_CHAN_giong_duong_ong():
    """"Chua thay bi bao gio" (cho TRONG) va "khong" (khang dinh AM) truoc day
    in cung mot chu "Chua ghi nhan", trong khi `sinh_benh_an.dien_dat` cua
    duong ong in "khong ..." — hai khau lech nhau o cung mot menh de."""
    co = collections.Counter()
    for m in bo(300):
        for d in m["dap_an"]:
            if d["muc"] != "DỊ ỨNG" or d["chu_the"] != "bệnh nhân":
                continue
            if d["do_chac_chan"] == "chưa ghi nhận":
                assert f"Chưa ghi nhận {d['noi_dung']}" in m["output"], m["id"]
                co["chua"] += 1
            elif d["phu_dinh"]:
                assert f"Không {d['noi_dung']}" in m["output"], m["id"]
                co["khong"] += 1
    assert co["chua"] >= 3 and co["khong"] >= 10, co


# ------------------------------------------ bay hai nguon khac nhau (11/09)

def test_nguon_khac_nhau_bat_RIENG_ngoai_bo_rut():
    assert "nguon_khac_nhau" in sh.BAY_BAT_RIENG
    assert "nguon_khac_nhau" not in sh.BAY_RUT
    assert "nguon_khac_nhau" in sh.BAY_SINH_QUAN_HE


def test_nguon_khac_nhau_HAI_ban_deu_chua_giai_quyet():
    """Hai nguoi noi khac nhau thi khong co can cu chon ben — ca hai ban phai
    `chua giai quyet`, va moi ban mang luot cua CHINH nguoi noi no."""
    thay = 0
    for m in bo(700):
        if "nguon_khac_nhau" not in m["bay"]:
            continue
        assert m["nguoi_ke"] and not m["la_tre_em"], m["id"]
        assert "\nBệnh nhân:" in m["input"] and "Người nhà:" in m["input"]
        vai = [x.split(":", 1)[0] for x in m["input"].split("\n") if x.strip()]
        mt = [d for d in m["dap_an"] if d["quan_he"] == "mâu thuẫn"]
        assert mt, m["id"]
        for d in mt:
            goc = m["dap_an"][d["quan_he_voi"]]
            assert d["trang_thai"] == goc["trang_thai"] == "chưa giải quyết"
            assert vai[max(d["luot"]) - 1] == "Bệnh nhân", m["id"]
            assert vai[max(goc["luot"]) - 1] == "Người nhà", m["id"]
        assert "chưa rõ" in m["output"], m["id"]
        thay += 1
    assert thay >= 5, thay


# ------------------------------ tang ngon ngu dung bo so RIENG (11/09/2026)

def _bo_trich(dap_an):
    return [{k: v for k, v in d.items() if k != "trich_dan"} for d in dap_an]


def test_TAT_phuong_ngu_KHONG_doi_phan_noi_dung():
    """Phep thu cap phuong ngu can hai ban chi khac o tu phuong ngu. Truoc day
    tang vung rut so tu CHUNG `rng` voi noi dung, nen tat no la doi ca benh.

    So qua `thach_thuc._so_cap_phuong_ngu`: tu 24/09/2026 ban co phuong ngu ghi
    "nong ham hap" dung loi nguoi noi (`phuong_ngu.GIU_NGUYEN`), ban kia ghi "sot"."""
    from src.thach_thuc import _so_cap_phuong_ngu as _bo_trich
    doi_it_nhat_mot = 0
    # Khuon PHAT TRIEN: tu 11/09/2026 khuon train khong nhan tu phuong ngu nao
    # (`PHUONG_NGU_TRONG_TRAIN`), nen rut khuon ngau nhien thi gan het cap giong.
    for i in range(40):
        a = sh.sinh_mot_ca("x", random.Random(i),
                           sh.TuyChon(chi_tap="phat_trien", ep_mien="nam"))
        b = sh.sinh_mot_ca("x", random.Random(i),
                           sh.TuyChon(chi_tap="phat_trien", ep_mien="nam",
                                      ap_phuong_ngu=False))
        assert (a["benh"], a["bay"], a["so_luot"]) == \
               (b["benh"], b["bay"], b["so_luot"]), i
        assert _bo_trich(a["dap_an"]) == _bo_trich(b["dap_an"]), i
        assert not b["tu_phuong_ngu"]
        doi_it_nhat_mot += bool(a["tu_phuong_ngu"])
    assert doi_it_nhat_mot >= 5


def test_sinh_bo_LA_chuoi_sinh_mot_ca():
    """`sinh_bo` khong duoc co nhanh rieng: bo chinh va bo thach thuc phai di
    qua CUNG mot duong sinh."""
    rng = random.Random(5)
    tay = [sh.sinh_mot_ca(f"hv_{i + 1:04d}", rng) for i in range(8)]
    assert tay == sh.sinh_bo(8, seed=5)


def test_chi_tap_chi_rut_khuon_cua_tap_do():
    bang = sh.bang_tap_khuon()
    for i in range(30):
        ca = sh.sinh_mot_ca("x", random.Random(i),
                            sh.TuyChon(chi_tap="phat_trien"))
        assert bang[ca["benh"]] == "phat_trien", ca["benh"]
