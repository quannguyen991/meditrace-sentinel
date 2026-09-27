# -*- coding: utf-8 -*-
"""Danh gia cac tang moi — khoa bang chung, rui ro, hoi lai — tren DAP AN CAU TRUC.

HAI LOAI DAU VAO, va vi sao can ca hai:

  dap an hoan hao   `phat_bieu_tu_dap_an`: khau trich KHONG sai gi. Moi lan tang
                    khoa CHAN o day la mot lan chan oan — do duoc gia cua tang
                    khoa ma khong lan voi loi cua mo hinh.
  dap an bi lam hong co chu dinh (`lam_hong`): doi chu the, nang muc khang dinh,
                    bia trich dan... — biet truoc loi nao o dau, nen do duoc tang
                    khoa BAT duoc bao nhieu, theo TUNG loai loi.

Dau ra cua mo hinh (sau khi huan luyen lai tren bo the he 5) di qua cung cac ham
nay, nhung phai kem COT CHON BUA cung ty le — bai hoc cua `duong_danh_doi`.

CHI HIEU CHINH TREN KHUON CUA TAP TRAIN. Tap phat trien de xem, tap kiem tra cuoi
chi mo mot lan.
"""
import random
from collections import Counter

from src import sai_so
from src.phat_bieu import PhatBieu

VAI_HOP_LE = ("bác sĩ", "bệnh nhân", "điều dưỡng")


def phat_bieu_tu_dap_an(ca) -> list:
    """Dap an -> PhatBieu, nhu mot khau trich HOAN HAO.

    `id` = chi so trong `dap_an`, nen `quan_he_voi` giu nguyen nghia. Chu the chi
    phan hai muc (0 = benh nhan, 1 = nguoi khac) — tang khoa chi can the.
    """
    from src.du_lieu_trich import ban_lap_ly_do_kham
    vai = sai_so.nguoi_noi_tung_luot(ca)
    lap = ban_lap_ly_do_kham(ca["dap_an"])
    ra = []
    for i, d in enumerate(ca["dap_an"]):
        luot = list(d.get("luot") or [])
        if not luot or i in lap:
            continue
        nn = str(vai.get(max(luot), "")).lower()
        qh = d.get("quan_he")
        ra.append(PhatBieu(
            id=i, nguoi_noi=nn if nn in VAI_HOP_LE else "người nhà",
            chu_the_id=0 if d["chu_the"] == "bệnh nhân" else 1,
            noi_dung=d["noi_dung"], bang_chung=luot,
            do_chac_chan=d.get("do_chac_chan") or "chắc chắn",
            phu_dinh=bool(d.get("phu_dinh")),
            tinh_huong=d.get("tinh_huong") or "thực tế",
            thoi_gian_su_kien=d.get("thoi_gian_su_kien") or "chưa rõ",
            moc_thoi_gian=d.get("moc_thoi_gian"),
            quan_he=qh, quan_he_voi=d.get("quan_he_voi") if qh else None,
            trang_thai=d.get("trang_thai") or "còn hiệu lực",
            trich_dan=list(d.get("trich_dan") or []),
            ten_chu_the=d["chu_the"], hanh_vi=d.get("hanh_vi") or "",
            # Chi tiet thuoc (15/09/2026): khong chep sang thi phep do chan oan tren
            # dap an hoan hao khong bao gio chay K6 cua khoa.
            thuoc=d.get("thuoc")))
    return ra


def vao_than(p) -> bool:
    """Phat bieu nay, neu khong bi khoa chan, co vao THAN ho so khong. Chan oan
    chi tinh tren nhung phat bieu nay — ban bi thay the hay cau gia dinh von da
    xuong CAN XAC NHAN, khoa them ly do cung khong lam mat gi."""
    return p.trang_thai == "còn hiệu lực" and p.tinh_huong != "giả định"


def thong_ke_khoa(ds, bat_buoc_trich_dan=True, so_vi_du=3):
    """Chay tang khoa tren DAP AN HOAN HAO cua `ds` -> ty le chan oan, canh bao,
    va doan chua ghi — theo tung ly do, kem vai vi du."""
    from src import khoa_bang_chung as kbc
    chan, canh, vi_du, doan = Counter(), Counter(), {}, Counter()
    tong_than = so_chan_oan = 0
    for ca in ds:
        ps = phat_bieu_tu_dap_an(ca)
        kq = kbc.khoa_ca(ps, ca["input"], bat_buoc_trich_dan)
        for p, k in zip(ps, kq["ket_qua"]):
            if not vao_than(p):
                continue
            tong_than += 1
            so_chan_oan += bool(k.chan)
            for m in k.chan:
                chan[m] += 1
                vi_du.setdefault(m, [])
                if len(vi_du[m]) < so_vi_du:
                    vi_du[m].append((ca["id"], p.noi_dung, p.trich_dan))
            for m in k.canh_bao:
                canh[m] += 1
        for d in kq["doan_chua_ghi"]:
            doan[d["doan"].lower()] += 1
    return {"tong_than": tong_than, "so_chan_oan": so_chan_oan,
            "chan": dict(chan), "canh_bao": dict(canh), "vi_du": vi_du,
            "doan_chua_ghi": doan}


# ------------------------------------------------------- lam hong co chu dinh
LOAI_HONG = ("doi_chu_the", "nang_muc", "gia_dinh_thanh_that", "bia_trich_dan")


def lam_hong(ps, loai, rng):
    """-> (danh sach MOI, id phat bieu da bi lam hong). Moi lan hong DUNG MOT
    phat bieu, chon ngau nhien trong nhung phat bieu hong duoc theo `loai`."""
    ung = []
    for p in ps:
        if not vao_than(p) and loai != "gia_dinh_thanh_that":
            continue
        if loai == "doi_chu_the":
            ung.append(p)
        elif loai == "nang_muc" and (p.do_chac_chan != "chắc chắn"):
            ung.append(p)
        elif loai == "gia_dinh_thanh_that" and p.tinh_huong == "giả định":
            ung.append(p)
        elif loai == "bia_trich_dan" and p.trich_dan:
            ung.append(p)
    if not ung:
        return None, None
    dich = rng.choice(ung)
    moi = []
    for p in ps:
        q = PhatBieu(**p.to_dict())
        if p.id == dich.id:
            if loai == "doi_chu_the":
                q.chu_the_id = 1 if p.chu_the_id == 0 else 0
            elif loai == "nang_muc":
                q.do_chac_chan, q.phu_dinh = "chắc chắn", False
            elif loai == "gia_dinh_thanh_that":
                q.tinh_huong = "thực tế"
            elif loai == "bia_trich_dan":
                q.trich_dan = [f"{p.noi_dung} từ tuần trước"] + p.trich_dan[1:]
        moi.append(q)
    return moi, dich.id


def do_bat_bo_sot(ds, seed=0):
    """BO mot phat bieu vao than (co trich dan) khoi moi ca, roi xem phep kiem
    day du co chi ra DOAN cua no khong -> Counter{"phat_hien", "lot"}.

    Day la phep do cho nua "kiem day du doi chieu voi HOI THOAI": bo sot la loi
    ma `kiem_day_du` cu khong the thay, vi no chi so ban nhap voi bang phat bieu.
    """
    from src import khoa_bang_chung as kbc
    rng = random.Random(seed)
    ket = Counter()
    for ca in ds:
        ps = phat_bieu_tu_dap_an(ca)
        ung = [p for p in ps if vao_than(p) and p.trich_dan]
        if not ung:
            continue
        bo = rng.choice(ung)
        con = [p for p in ps if p.id != bo.id]
        kq = kbc.khoa_ca(con, ca["input"])
        cac_luot = kbc._luot(ca["input"])
        vi_tri = []
        for so, t in zip(bo.bang_chung, bo.trich_dan):
            if so in cac_luot:
                vt = kbc.tim_trich(t, cac_luot[so][1])
                if vt:
                    vi_tri.append((so, vt))
        thay = any(d["luot"] == so and d["bat_dau"] < b and a < d["ket_thuc"]
                   for d in kq["doan_chua_ghi"] for so, (a, b) in vi_tri)
        ket["phat_hien" if thay else "lot"] += 1
    return ket


def do_bat_loi(ds, loai, seed=0, bat_buoc_trich_dan=True):
    """Tren moi ca, lam hong mot phat bieu theo `loai` roi xem khoa CHAN, CANH
    BAO, hay de lot -> Counter{"chan", "canh_bao", "lot"} va Counter ly do."""
    from src import khoa_bang_chung as kbc
    rng = random.Random(seed)
    ket, ly = Counter(), Counter()
    for ca in ds:
        ps = phat_bieu_tu_dap_an(ca)
        moi, dich = lam_hong(ps, loai, rng)
        if moi is None:
            continue
        kq = kbc.khoa_ca(moi, ca["input"], bat_buoc_trich_dan)["ket_qua"]
        k = next(x for x in kq if x.id == dich)
        if k.chan:
            ket["chan"] += 1
            ly.update(k.chan)
        elif k.canh_bao:
            ket["canh_bao"] += 1
            ly.update(k.canh_bao)
        else:
            ket["lot"] += 1
    return ket, ly
