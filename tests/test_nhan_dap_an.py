# -*- coding: utf-8 -*-
"""Nhan trong dap an phai NHAT QUAN voi chinh cach bo sinh dat ra chung.

Ho loi "khai ma khong dien" da gap sau lan trong du an nay; mot dang cua no la
dien o duong chinh nhung SOT o duong phu. Ban va `thoi_gian_su_kien` sang
11/09/2026 di qua `_Soan.ghi` va bo sot ba cho dung `MenhDe` truc tiep (dinh
chinh, mau thuan, hai nguon) — nen menh de da sua mang "chua ro" trong khi ban
goc cua no mang "hien tai". Test o day quet MOI menh de, khong chi duong chinh.
"""
import collections

import pytest

from src import sai_so
from src import sinh_hoi_thoai_viet as sh


@pytest.fixture(scope="module")
def bo():
    return sh.sinh_bo(600, seed=11)


def test_thoi_gian_su_kien_KHOP_muc_o_MOI_menh_de(bo):
    for m in bo:
        for d in m["dap_an"]:
            assert d["thoi_gian_su_kien"] == sh.THOI_GIAN_THEO_MUC[d["muc"]], \
                (m["id"], d["muc"], d["thoi_gian_su_kien"], d["quan_he"])


def test_menh_de_tao_tay_mang_DU_nhan_nhu_ban_goc(bo):
    """Ba bay tao menh de bang tay: cung muc, cung thoi gian voi ban goc."""
    thay = 0
    for m in bo:
        for d in m["dap_an"]:
            if d["quan_he"] not in ("đính chính", "mâu thuẫn"):
                continue
            goc = m["dap_an"][d["quan_he_voi"]]
            assert (d["muc"], d["thoi_gian_su_kien"]) == \
                   (goc["muc"], goc["thoi_gian_su_kien"]), m["id"]
            assert d["hanh_vi"] == "tự kể", m["id"]
            thay += 1
    assert thay >= 20, thay


def test_hanh_vi_KHOP_vai_nguoi_noi(bo):
    for m in bo:
        vai = sai_so.nguoi_noi_tung_luot(m)
        for d in m["dap_an"]:
            nn = vai[max(d["luot"])]
            if nn in ("Bác sĩ", "Điều dưỡng"):
                assert d["hanh_vi"] in ("quan sát", "nhận định", "kế hoạch"), \
                    (m["id"], d)
            else:
                assert d["hanh_vi"] in ("trả lời", "tự kể"), (m["id"], d)


# ----------------------------------- muc chac chan cua CHAN DOAN (11/09/2026)

def test_theo_doi_DAU_cau_la_chan_doan_TAM():
    """"Theo doi X" la cach bac si ghi chan doan tam — nhan phai la nghi ngo, va
    noi dung bo tien to (ban tham chieu in "Nghi ngo X")."""
    assert sh._muc_chan_doan("Theo dõi suy giáp.") == ("suy giáp", "nghi ngờ")


def test_chu_NGHI_trong_chan_doan_la_nghi_ngo():
    assert sh._muc_chan_doan("Viêm họng nghi do liên cầu.")[1] == "nghi ngờ"


def test_theo_doi_CUOI_cau_la_chan_doan_CHAC_kem_ke_hoach():
    assert sh._muc_chan_doan("Viêm gan B mạn, theo dõi.") == \
        ("Viêm gan B mạn, theo dõi", "chắc chắn")


def test_tren_bo_sinh_chan_doan_mang_dau_rao_don_DEU_la_nghi_ngo(bo):
    """Tang khoa bang chung chan phat bieu "chac chan" ma doan dan rao don — nen
    moi chan doan nhu vay trong dap an phai la "nghi ngo", khong thi khoa chan
    oan dung tren dap an dung."""
    import re
    for m in bo:
        for d in m["dap_an"]:
            if d["muc"] != "CHẨN ĐOÁN":
                continue
            rao = [t for t in d["trich_dan"]
                   if re.match(r"(?i)\s*theo dõi", t)
                   or re.search(r"(?i)(?<!\w)(nghi|nghĩ nhiều đến)(?!\w)", t)]
            if rao:
                assert d["do_chac_chan"] == "nghi ngờ", (m["id"], d)


# ----------------------------------------- tang_cua: MOT dinh nghia tang

def _ca(input_, dap_an):
    return {"input": input_, "dap_an": dap_an}


def test_tang_lay_nguoi_noi_LUOT_CUOI():
    """Cau tra loi tat mang ca luot cau hoi — nguoi noi la nguoi TRA LOI."""
    ca = _ca("Bác sĩ: Cháu có dị ứng thuốc không?\nNgười nhà: Dạ, không ạ.",
             [{"chu_the": "bệnh nhân", "luot": [1, 2]}])
    assert sai_so.tang_cua(ca["dap_an"][0],
                           sai_so.nguoi_noi_tung_luot(ca)) == "ke_ho"


def test_dieu_duong_la_tang_BAC_SI():
    """Truoc 11/09/2026 dieu duong doc sinh hieu roi vao tang `ke_ho`."""
    ca = _ca("Điều dưỡng: Sinh hiệu em đo được: nhiệt độ 38 độ.",
             [{"chu_the": "bệnh nhân", "luot": [1]}])
    assert sai_so.tang_cua(ca["dap_an"][0],
                           sai_so.nguoi_noi_tung_luot(ca)) == "bac_si"


def test_tang_4_van_la_tang_4():
    ca = _ca("Bác sĩ: Gia đình có ai bệnh gì không?\n"
             "Người nhà: Tôi bị tăng huyết áp.",
             [{"chu_the": "mẹ", "luot": [2]}])
    assert sai_so.tang_cua(ca["dap_an"][0],
                           sai_so.nguoi_noi_tung_luot(ca)) == "ke_ve_minh"


def test_do_tang_quy_gan_DUNG_CHUNG_dinh_nghia(bo):
    """`menh_de_dap_an` chi bo them menh de khong co tu noi dung — tung tang
    khong duoc NHIEU hon `tang_menh_de`."""
    from src import do_tang_quy_gan
    for m in bo[:120]:
        a = collections.Counter(
            t for t, _c, _g in do_tang_quy_gan.menh_de_dap_an(m))
        b = sai_so.tang_menh_de(m)
        for k in a:
            assert a[k] <= b[k], (m["id"], k)
