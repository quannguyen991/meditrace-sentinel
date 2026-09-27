# -*- coding: utf-8 -*-
"""Tang ngu vuc: hoi thoai noi loi dan thuong, dap an giu thuat ngu lam sang.

VI SAO CAN TANG NAY. Do ngay 10/09/2026: ty le tu noi dung cua menh de dap an
xuat hien NGUYEN VAN trong hoi thoai la 99,7% (bo 3.000) va 99,6% (bo 5.000);
99,1% menh de phu 100%. Nghia la nhiem vu ma bo du lieu dat ra chi la "tim dung
doan va xep dung muc" — va mot doi chung regex khong mo hinh da hon ca duong
ong day du tren moi tang.

HAI BAT BIEN, ca hai deu duoc kiem o day:

  1. CHI thay trong loi benh nhan va nguoi nha, khong thay loi bac si.
  2. DAP AN GIU THUAT NGU CHUAN.

Bat bien 2 CHINH LA phep thu: neu dap an cung doi sang loi dan thuong thi khong
con gi de do, mo hinh chi viec chep lai nguyen van.

Them 11/09/2026 mot rang buoc thu ba, truoc do chi nam trong chu thich: BANG LAY
TU TU VUNG CUA TAP TRAIN (`test_MOI_khoa_thuoc_TU_VUNG_TRAIN`).
"""
import random
import re

import pytest

from src import loi_dan_thuong as ldt
from src import sinh_hoi_thoai_viet as sh


def _rng():
    return random.Random(7)


# ------------------------------------------------------ phep thay co ban

def test_doi_duoc_cum_ky_thuat():
    cau, da_doi = ldt.doi_sang_dan_thuong("cháu đau vùng thượng vị ba hôm",
                                          _rng(), ty_le=1.0)
    assert "đau vùng thượng vị" not in cau
    assert da_doi and da_doi[0][0] == "đau vùng thượng vị"


def test_ty_le_0_thi_khong_doi_gi():
    cau, da_doi = ldt.doi_sang_dan_thuong("cháu buồn nôn", _rng(), ty_le=0.0)
    assert cau == "cháu buồn nôn" and da_doi == []


def test_khong_khop_tu_nam_TRONG_tu_khac():
    """"da xanh" khong duoc khop trong "da xanh xao" — biên tu phai chat."""
    cau, _ = ldt.doi_sang_dan_thuong("trông da xanh xao", _rng(), ty_le=1.0)
    assert "da xanh xao" in cau


def test_doi_cum_DAI_truoc_cum_NGAN():
    """"dau lung lan xuong chan" phai duoc xet truoc "dau lung".

    Doi cum ngan truoc thi con lai mot cau chap va — dung ho loi pha tu ghep da
    mac o `phuong_ngu`. (Truoc 11/09/2026 test nay dung "ngua tang ve dem",
    mot cum da bo vi khong thuoc tu vung train.)
    """
    cau, da_doi = ldt.doi_sang_dan_thuong("cháu đau lưng lan xuống chân",
                                          _rng(), ty_le=1.0)
    assert "đau lưng lan xuống chân" not in cau
    assert [t for t, _c in da_doi] == ["đau lưng lan xuống chân"]


def test_bang_khong_rong_va_moi_cum_co_it_nhat_mot_cach_noi():
    assert len(ldt.DAN_THUONG) >= 15
    for thuat_ngu, cach in ldt.DAN_THUONG.items():
        assert cach, thuat_ngu
        for c in cach:
            assert c and c != thuat_ngu, thuat_ngu


def test_cum_da_bo_deu_co_LY_DO():
    """Ghi ra ly do thay vi xoa im lang, de nguoi doc sau biet la da can nhac."""
    assert ldt.DA_BO
    for cum, ly_do in ldt.DA_BO.items():
        assert len(ly_do) > 20, cum


def test_cum_bo_vi_khong_thuoc_train_KHONG_con_trong_bang():
    assert not set(ldt.BO_VI_KHONG_THUOC_TRAIN) & set(ldt.DAN_THUONG)
    assert not set(ldt.BO_VI_KHONG_THUOC_TRAIN) & set(ldt.CHAN_SAU), \
        "con mot dong CHAN_SAU cho khoa khong ton tai — ma chet"


def test_phu_duoc_do_duoc_do_phu_cua_bang():
    """Bang khong khop ngu lieu thi khong bao loi, no chi khong chay. Da xay ra:
    9/18 cum dau tien khong xuat hien lan nao trong 681 ca."""
    assert ldt.phu_duoc("cháu chán ăn và mệt mỏi") == \
        [t for t in ("chán ăn", "mệt mỏi") if t in ldt.DAN_THUONG]
    assert ldt.phu_duoc("không có gì cả") == []


# ----------------------------------------- hai bat bien, tren bo sinh that

def _bo(n=220, seed=5):
    return sh.sinh_bo(n, seed=seed)


def test_BAT_BIEN_1_khong_thay_trong_loi_bac_si():
    """Bac si duoc dao tao noi thuat ngu. Doi loi bac si sang loi dan thuong la
    lam mat mot dau hieu that cua hoi thoai kham benh."""
    cach_noi = {c for ds in ldt.DAN_THUONG.values() for c in ds}
    for m in _bo():
        for dong in m["input"].split("\n"):
            if not dong.lower().startswith("bác sĩ:"):
                continue
            for c in cach_noi:
                assert c not in dong.lower(), f"{m['id']}: {dong}"


def test_BAT_BIEN_2_dap_an_giu_THUAT_NGU_CHUAN():
    """Day chinh la phep thu. Dap an doi theo thi khong con gi de do."""
    cach_noi = {c for ds in ldt.DAN_THUONG.values() for c in ds}
    for m in _bo():
        for d in m["dap_an"]:
            noi = str(d.get("noi_dung") or "").lower()
            for c in cach_noi:
                assert c not in noi, f"{m['id']}: dap an co loi dan thuong {c!r}"


def test_tang_nay_THAT_SU_chay_tren_bo_sinh():
    """Mot tang khong bao gio khai hoa thi khong bao loi, no chi vo nghia.

    Nguong 25% dat thap hon muc do duoc (~38%) co y: canh viec tut lai, khong
    khoa cung mot con so.
    """
    ds = _bo()
    co = sum(1 for m in ds if m.get("cum_dan_thuong"))
    assert co / len(ds) >= 0.25, f"chi {co}/{len(ds)} ca co loi dan thuong"


def test_ghi_lai_DUOC_cum_nao_da_doi():
    """Khong ghi lai thi khong do duoc rieng nhom nay — giong `tu_phuong_ngu`."""
    ds = _bo()
    co = [m for m in ds if m.get("cum_dan_thuong")]
    assert co
    for m in co:
        for t in m["cum_dan_thuong"]:
            assert t in ldt.DAN_THUONG, (m["id"], t)


def test_hai_tang_DOC_LAP_nhau():
    """Phuong ngu la bien the VUNG, loi dan thuong la bien the NGU VUC. Mot ca
    co the co cai nay ma khong co cai kia — neu luon di cung thi khong tach
    duoc tang nao dang lam mo hinh sai."""
    ds = _bo(400)
    chi_ngu_vuc = [m for m in ds if m.get("cum_dan_thuong")
                   and not m.get("tu_phuong_ngu")]
    assert chi_ngu_vuc, "khong co ca nao chi co loi dan thuong"


def test_CHAN_SAU_chan_dung_cho_pha_tu_ghep():
    """Cac cho lay tu ngu lieu, khong tu phong doan."""
    cau, da_doi = ldt.doi_sang_dan_thuong("nổi mụn nước nhỏ", _rng(), ty_le=1.0)
    assert cau == "nổi mụn nước nhỏ" and da_doi == []
    cau2, _ = ldt.doi_sang_dan_thuong("trông da xanh xao", _rng(), ty_le=1.0)
    assert cau2 == "trông da xanh xao"


def test_CHAN_SAU_khong_chan_cho_hop_le():
    """Doi chung: bang chan khong duoc lam tang nay ngung chay."""
    cau, da_doi = ldt.doi_sang_dan_thuong("nổi mụn nước hai hôm nay", _rng(),
                                          ty_le=1.0)
    assert "nổi mụn nước" not in cau and da_doi


def test_KHONG_cach_noi_nao_trung_voi_thuat_ngu_trong_dap_an():
    """Loi that: "kho vao giac" la cach noi dan thuong toi chon, nhung no cung la
    mot thuat ngu CO THAT trong dap an cua bo sinh.

    Trung nhu vay thi pha bat bien 2 — dap an chua mot cum cua bang nay — va
    phep thu het phan biet duoc dap an voi hoi thoai. Quet ca bang thay vi sua
    tung cho, vi mot cho trung la du de lam phep thu mat nghia.
    """
    noi_dung = set()
    for m in _bo(400):
        for d in m["dap_an"]:
            noi_dung.add(str(d.get("noi_dung") or "").strip().lower())
    kho = " ||| ".join(noi_dung)
    trung = [(t, c) for t, cac in ldt.DAN_THUONG.items() for c in cac
             if c.lower() in kho]
    assert not trung, f"cach noi trung voi thuat ngu trong dap an: {trung}"


def test_do_phu_tren_TAP_TRAIN_du_cao():
    """Bang phai duoc chon theo tu vung cua TAP TRAIN.

    Ban dau toi chon 20 cum theo tan so do tren TAP PHAT TRIEN. Hai hau qua:
    bang phu 8 khuon cua dev tot va 45 khuon cua train kem (83,3% so voi 93,8%
    ty le sao chep nguyen van), va chon tu vung theo tan so cua tap DO la mot
    dang nhin vao du lieu danh gia.

    Nguong 50% dat duoi muc do duoc (~66%) de canh viec tut lai.
    """
    from pathlib import Path
    import json
    p = Path("data/viet_train.jsonl")
    if not p.exists():
        pytest.skip("chua sinh tap train")
    d = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    co = sum(1 for x in d if x.get("cum_dan_thuong"))
    assert co / len(d) >= 0.50, f"chi {co}/{len(d)} ca train co loi dan thuong"


# ------------------- bang lay tu TAP TRAIN, va do lech giua hai tap (11/09)

@pytest.fixture(scope="module")
def chia_5000():
    from src import tach_tap_viet as tt
    tr, pt, _kt, _ = tt.chia(sh.sinh_bo(5000, seed=42))
    return tr, pt


def _khoa_trong(ds):
    from src import sai_so
    co = set()
    for x in ds:
        vai = sai_so.nguoi_noi_tung_luot(x)
        for d in x["dap_an"]:
            if vai[max(d["luot"])] in ("Bác sĩ", "Điều dưỡng"):
                continue
            nd = str(d["noi_dung"]).lower()
            for k in ldt.DAN_THUONG:
                if re.search(rf"(?<![\wÀ-ỹ]){re.escape(k)}(?![\wÀ-ỹ])", nd):
                    co.add(k)
    return co


def test_MOI_khoa_thuoc_TU_VUNG_TRAIN(chia_5000):
    """Rang buoc truoc day chi nam trong chu thich ("bang gio mo rong theo tu
    vung cua TAP TRAIN"), nen khi bo khuon doi, tam cum chon tu tap phat trien
    lang le thanh tu vung CHI co o tap do. Kiem bang ma thay vi tin chu thich."""
    tr, _pt = chia_5000
    thieu = set(ldt.DAN_THUONG) - _khoa_trong(tr)
    assert not thieu, f"khoa khong thuoc tu vung train: {sorted(thieu)}"


def _phu100(ds):
    from src import thuoc_do_quy_gan as t
    p = []
    for r in ds:
        thoai = t._tu_noi_dung(r["input"])
        for m in r["dap_an"]:
            w = t._tu_noi_dung(str(m.get("noi_dung") or ""))
            if w:
                p.append(w <= thoai)
    return sum(p) / len(p)


def test_do_phu_KHONG_lech_giua_train_va_dev(chia_5000):
    """Tap PHAT TRIEN khong duoc KHO HON train vi mot ly do khong lien quan toi
    kha nang khai quat — dung lo~i "LOI THU HAI" trong `loi_dan_thuong`: bang
    chon theo tu vung cua tap do lam tap do kho hon 10 diem.

    Hang so `CHENH_PHU_TOI_DA` duoc khai kem loi hua "co test canh" tu truoc,
    nhung test do CHUA BAO GIO duoc viet va hang so khong ai dung — viet ngay
    11/09/2026.

    MOT CHIEU, co chu dinh, va phai noi ro: chieu nguoc lai — tap phat trien DE
    CHEP HON train — la he qua TAT YEU cua rang buoc "bang chi lay tu vung
    train" (khuon cua tap phat trien khong duoc co cach noi dan thuong rieng).
    Kiem ca hai chieu la doi hai dieu mau thuan nhau. Do lech chieu do duoc bao
    cao trong nhat ky, khong giau.
    """
    tr, pt = chia_5000
    a, b = _phu100(tr), _phu100(pt)
    assert b >= a - ldt.CHENH_PHU_TOI_DA, \
        f"tap phat trien kho hon train: {b:.1%} so voi {a:.1%}"
