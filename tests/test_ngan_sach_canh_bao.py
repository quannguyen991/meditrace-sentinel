# -*- coding: utf-8 -*-
"""Ngân sách cảnh báo (Task 5 plan 27/11 + V11 plan 28/11).

- `gop.chon_hien_thi(ds, ngan_sach=2) -> (hien, gap)`: mỗi mệnh đề chỉ hiện tối đa `ngan_sach`
  cảnh báo; cảnh báo mức `cao`, kết luận `loi_phat_hien` hoặc mã `LUON_CAO` luôn hiện.
- Mã vô dụng (báo ≥ 20 lần, chính xác cùng loại < 0,10 trong docs/ket-qua/canh-bao.json) xuống
  mức `thap`, không vào hàng chặn của chính sách D, và luôn nằm trong phần gập.
"""
import json
import random
from pathlib import Path

from src.canh_bao import gop
from src.canh_bao.loai import (CAN_XEM, CAO, LOI_PHAT_HIEN, LUON_CAO, MA_GOI_Y_CHINH_XAC_THAP, NGHI_RUI_RO,
                               THAP, TRUNG, CanhBao)
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu

GOC = Path(__file__).resolve().parents[1]


def cb(ma, muc_do, ket_luan, pid=1, luot=(1,)):
    return CanhBao(ma=ma, phat_bieu_id=pid, luot=list(luot), trich=["x"], ly_do="thử", ket_luan=ket_luan,
                   bat_dinh=TRUNG, bo_phat_hien="test", muc_do=muc_do)


# ---------------------------------------------------------------- chon_hien_thi (plan Task 5)
def test_cao_luon_hien_du_vuot_ngan_sach():
    ds = [cb("NEGATION_FLIP", CAO, LOI_PHAT_HIEN) for _ in range(3)] + [cb("OMITTED_ANSWER", THAP, CAN_XEM)]
    hien, gap = gop.chon_hien_thi(ds, ngan_sach=2)
    assert len(hien) == 3 and len(gap) == 1


def test_ban_sach_chi_hien_toi_da_ngan_sach():
    ds = [cb("OMITTED_ANSWER", TRUNG, NGHI_RUI_RO) for _ in range(7)]
    hien, gap = gop.chon_hien_thi(ds, 2)
    assert len(hien) == 2 and len(gap) == 5


def test_ngan_sach_khong_an_canh_bao_cao():
    # Mọi cảnh báo cao (bất kể kết luận), mọi loi_phat_hien (bất kể mức) và mọi mã LUON_CAO
    # (kể cả khi mức bị hạ theo loại thông tin) đều phải hiện, dù ngân sách = 0.
    ds = ([cb("CONTRADICTION_UNRESOLVED", CAO, NGHI_RUI_RO, luot=(i,)) for i in range(1, 5)]
          + [cb("UNSUPPORTED_INFORMATION", TRUNG, LOI_PHAT_HIEN)]
          + [cb("DOSE_MISMATCH", TRUNG, NGHI_RUI_RO)]
          + [cb("PAST_CURRENT_CONFUSION", TRUNG, NGHI_RUI_RO) for _ in range(3)])
    for ngan_sach in (0, 1, 2):
        hien, gap = gop.chon_hien_thi(ds, ngan_sach=ngan_sach)
        assert sum(c.muc_do == CAO for c in hien) == 4
        assert any(c.ma == "UNSUPPORTED_INFORMATION" for c in hien)
        assert any(c.ma == "DOSE_MISMATCH" for c in hien)
        assert not any(c.muc_do == CAO or c.ket_luan == LOI_PHAT_HIEN or c.ma in LUON_CAO for c in gap)
        assert len(hien) + len(gap) == len(ds)


def test_thu_tu_xac_dinh():
    ds = [cb("PAST_CURRENT_CONFUSION", TRUNG, NGHI_RUI_RO), cb("SUBJECT_AMBIGUOUS", TRUNG, NGHI_RUI_RO),
          cb("APPROXIMATION_LOST", THAP, CAN_XEM), cb("TEMPORAL_MISMATCH", TRUNG, NGHI_RUI_RO),
          cb("CERTAINTY_INCREASED", CAO, NGHI_RUI_RO)]
    goc = gop.chon_hien_thi(ds, 2)
    for hat in range(5):
        tron = ds[:]
        random.Random(hat).shuffle(tron)
        ra = gop.chon_hien_thi(tron, 2)
        assert [c.ma for c in ra[0]] == [c.ma for c in goc[0]]
        assert [c.ma for c in ra[1]] == [c.ma for c in goc[1]]
    # mức trước, rồi độ chính xác cùng loại đã đo: SUBJECT_AMBIGUOUS 0,59 > PAST_CURRENT 0,344
    assert [c.ma for c in goc[0]] == ["CERTAINTY_INCREASED", "SUBJECT_AMBIGUOUS"]


def test_danh_sach_rong():
    assert gop.chon_hien_thi([], 2) == ([], [])


# ---------------------------------------------------------------- dọn mã vô dụng (V11)
def _ma_vo_dung_tu_bang_do():
    d = json.loads((GOC / "docs" / "ket-qua" / "canh-bao.json").read_text(encoding="utf-8"))
    return {r["ma"] for r in d["theo_ma"]
            if r["so_lan_bao"] >= 20 and r["chinh_xac_cung_loai"] < 0.10 and r["ma"] not in LUON_CAO}


def test_ma_vo_dung_xuong_goi_y():
    assert MA_GOI_Y_CHINH_XAC_THAP == _ma_vo_dung_tu_bang_do()
    assert MA_GOI_Y_CHINH_XAC_THAP == {"SPEAKER_SUBJECT_MISMATCH", "DUPLICATE_INFORMATION",
                                       "IMPORTANT_MODIFIER_DROPPED"}
    # Người nhà nói "ho ba ngày" (thông tin thường), mô hình gán cho bệnh nhân: mức thấp,
    # không chặn theo D, nằm trong phần gập.
    kq = _chay_nguoi_nha("ho ba ngày", "Ho ba ngày rồi")
    c = next(c for c in kq["theo_phat_bieu"][1]["tat_ca"] if c.ma == "SPEAKER_SUBJECT_MISMATCH")
    assert c.muc_do == THAP and not c.anh_huong_trang_thai
    assert kq["trang_thai_D"][1]["trang_thai"] == gop.DA_KIEM_CHUNG
    assert gop.phan_tang_canh_bao(c) == gop.TANG_TINH_LUOC
    hien, gap = gop.chon_hien_thi(kq["theo_phat_bieu"][1]["tat_ca"], 2)
    assert c in gap and c not in hien


def _chay_nguoi_nha(noi_dung, trich, thuoc=None, hoi_bs="Thế nào?"):
    hoi = f"1. Bác sĩ: {hoi_bs}\n2. Người nhà: {trich}."
    p = PhatBieu(id=1, noi_dung=noi_dung, bang_chung=[2], trich_dan=[trich], nguoi_noi="người nhà",
                 chu_the_id=0, thuoc=thuoc)
    return gop.chay([p], hoi)


def test_ma_goi_y_van_chan_D_tren_di_ung_va_thuoc():
    # Ngoại lệ an toàn (quyết định 28/11): trên dị ứng / thuốc, SPEAKER_SUBJECT_MISMATCH vẫn đưa
    # mệnh đề sang CẦN XÁC NHẬN (đo: bỏ đi thì D lọt nguy hiểm 11,8% -> 24,1%), và vẫn HIỆN
    # vì cảnh báo đổi trạng thái không bao giờ bị gập.
    for nd, trich, thuoc in [("dị ứng penicillin", "Dị ứng penicillin", None),
                             ("đang uống amlodipin 5mg", "Đang uống amlodipin 5mg",
                              {"ten": "amlodipin", "lieu": "5mg"})]:
        kq = _chay_nguoi_nha(nd, trich, thuoc)
        c = next(c for c in kq["theo_phat_bieu"][1]["tat_ca"] if c.ma == "SPEAKER_SUBJECT_MISMATCH")
        assert c.loai_tt in ("di_ung", "thuoc", "thuoc_nti")
        assert c.anh_huong_trang_thai
        assert kq["trang_thai_D"][1]["trang_thai"] == gop.CAN_XAC_NHAN
        hien, gap = gop.chon_hien_thi(kq["theo_phat_bieu"][1]["tat_ca"], 2)
        assert c in hien
    # Loại thông tin khác: không chặn.
    for nd, trich in [("ho ba ngày", "Ho ba ngày rồi"), ("sốt cao", "Sốt cao từ hôm qua")]:
        kq = _chay_nguoi_nha(nd, trich)
        assert kq["trang_thai_D"][1]["trang_thai"] == gop.DA_KIEM_CHUNG


def test_ma_goi_y_luon_gap_ke_ca_con_ngan_sach():
    ds = [cb("DUPLICATE_INFORMATION", THAP, CAN_XEM), cb("IMPORTANT_MODIFIER_DROPPED", THAP, CAN_XEM)]
    hien, gap = gop.chon_hien_thi(ds, 5)
    assert hien == [] and len(gap) == 2


def test_luon_cao_khong_bi_ha():
    assert not (MA_GOI_Y_CHINH_XAC_THAP & LUON_CAO)
    # Hạ mức chỉ áp cho mã gợi ý; mã LUON_CAO giữ nguyên mức và vẫn đổi trạng thái được.
    for ma in sorted(LUON_CAO):
        c = cb(ma, CAO, LOI_PHAT_HIEN)
        gop._ha_ma_goi_y([c])
        assert c.muc_do == CAO
        hien, gap = gop.chon_hien_thi([c] + [cb("SUBJECT_AMBIGUOUS", TRUNG, NGHI_RUI_RO)] * 3, 0)
        assert c in hien
    # Mã gợi ý mà có kết luận loi_phat_hien (bằng chứng đối nghịch rõ) cũng không bị hạ.
    c = cb("SPEAKER_SUBJECT_MISMATCH", CAO, LOI_PHAT_HIEN)
    gop._ha_ma_goi_y([c])
    assert c.muc_do == CAO


# ---------------------------------------------------------------- JSON cho dịch vụ / giao diện
def test_to_dict_co_hien_va_gap():
    hoi = "1. Bác sĩ: Thế nào?\n2. Người nhà: Ho ba ngày rồi."
    p = PhatBieu(id=1, noi_dung="ho ba ngày", bang_chung=[2], trich_dan=["Ho ba ngày rồi"],
                 nguoi_noi="người nhà", chu_the_id=0)
    d = gop.to_dict(gop.chay([p], hoi))
    v = d["theo_phat_bieu"]["1"]
    assert "chinh" in v and "khac" in v and "tat_ca" in v          # trường cũ giữ nguyên
    assert [c["ma"] for c in v["canh_bao_gap"]] == ["SPEAKER_SUBJECT_MISMATCH"]
    assert v["canh_bao_hien"] == []
    assert set(d["toan_ca_ngan_sach"]) == {"canh_bao_hien", "canh_bao_gap"}
    assert d["ngan_sach"] == gop.NGAN_SACH_MAC_DINH == 2


def test_bo_sung_ngan_sach_cho_ban_ghi_cu():
    # Bản ghi đã lưu trước Task 5 (dict, không có canh_bao_hien): bổ sung từ `tat_ca`.
    cu = {"theo_phat_bieu": {"3": {"chinh": None, "khac": [], "phu": [],
                                   "tat_ca": [cb("PAST_CURRENT_CONFUSION", TRUNG, NGHI_RUI_RO, pid=3).to_dict()
                                              for _ in range(3)]
                                   + [cb("SPEAKER_SUBJECT_MISMATCH", CAO, NGHI_RUI_RO, pid=3).to_dict()]}},
          "toan_ca": [cb("OMITTED_MEDICATION", CAO, NGHI_RUI_RO, pid=None).to_dict()]}
    ra = gop.bo_sung_ngan_sach(cu)
    v = ra["theo_phat_bieu"]["3"]
    assert len(v["canh_bao_hien"]) == 2 and len(v["canh_bao_gap"]) == 2
    assert any(c["ma"] == "SPEAKER_SUBJECT_MISMATCH" for c in v["canh_bao_gap"])
    assert [c["ma"] for c in ra["toan_ca_ngan_sach"]["canh_bao_hien"]] == ["OMITTED_MEDICATION"]
    # đã có thì không tính lại
    assert gop.bo_sung_ngan_sach(ra) is ra


def test_dich_vu_tra_canh_bao_hien_va_gap():
    from src.he_thong import dich_vu_http as dich_vu
    hoi = "1. Bác sĩ: Thế nào?\n2. Người nhà: Ho ba ngày rồi."
    p = PhatBieu(id=1, noi_dung="ho ba ngày", bang_chung=[2], trich_dan=["Ho ba ngày rồi"],
                 nguoi_noi="người nhà", chu_the_id=0)
    cu = gop.to_dict(gop.chay([p], hoi))          # giả lập bản ghi lưu trước Task 5
    for v in cu["theo_phat_bieu"].values():
        v.pop("canh_bao_hien"), v.pop("canh_bao_gap")
    cu.pop("toan_ca_ngan_sach"), cu.pop("ngan_sach")
    r = {"input": hoi, "phat_bieu": [p.to_dict()], "canh_bao": cu, "lam_sang_nang_cao": {"da_co": True}}
    ra = dich_vu._them_canh_bao(r)
    v = ra["canh_bao"]["theo_phat_bieu"]["1"]
    assert "chinh" in v and "tat_ca" in v
    assert [c["ma"] for c in v["canh_bao_gap"]] == ["SPEAKER_SUBJECT_MISMATCH"]
    assert "toan_ca_ngan_sach" in ra["canh_bao"]
    # bản ghi mới: tính tại chỗ, có sẵn hai trường
    moi = dich_vu._them_canh_bao({"input": hoi, "phat_bieu": [p.to_dict()], "lam_sang_nang_cao": {"da_co": True}})
    assert "canh_bao_hien" in moi["canh_bao"]["theo_phat_bieu"]["1"]
