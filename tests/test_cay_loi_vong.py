# -*- coding: utf-8 -*-
"""Phep thu cho cac vong sua luat tu do cay loi (plan 2026-11-25-cay-loi-do-canh-bao, Task 5).
Moi phep thu dung tu mot ca lot that trong tap dieu chinh (ghi id ca)."""
from src.canh_bao import gop
from src.phat_bieu import PhatBieu


def _p(id_, noi_dung, luot, trich, **kw):
    return PhatBieu(id=id_, nguoi_noi=kw.pop("nguoi_noi", "bác sĩ"), chu_the_id=kw.pop("chu_the_id", 0),
                    noi_dung=noi_dung, bang_chung=luot, trich_dan=trich, **kw)


def _ma(ps, hoi, pid):
    kq = gop.chay(ps, hoi)
    return {c.ma for c in kq["theo_phat_bieu"][pid]["tat_ca"]}


# ---- Vong 1: loi bac si "ke / ngung ... nhe" ghi thanh su viec (v2mr_0009 #12, v2mr_0030 #9, v2mr_0078 #8)
HOI_KE = "\n".join([
    "Bác sĩ: Anh thấy trong người thế nào?",
    "Bệnh nhân: Tôi hay khát nước, tiểu nhiều.",
    "Bác sĩ: Đơn thuốc hôm nay tôi kê metformin 500 mg, uống ngày hai lần sau ăn nhé.",
    "Bác sĩ: Thuốc omeprazole thì từ nay mình ngừng uống nha.",
    "Bệnh nhân: Dạ vâng.",
])


def test_ke_thuoc_ghi_thanh_su_viec_bi_bat():
    ps = [_p(0, "kê metformin", [3], ["Đơn thuốc hôm nay tôi kê metformin 500 mg"], tinh_huong="thực tế"),
          _p(1, "ngừng omeprazole", [4], ["Thuốc omeprazole thì từ nay mình ngừng uống nha"], tinh_huong="thực tế")]
    assert "PLAN_AS_FACT" in _ma(ps, HOI_KE, 0)
    assert "PLAN_AS_FACT" in _ma(ps, HOI_KE, 1)


def test_ke_thuoc_ghi_dung_ke_hoach_khong_bao():
    ps = [_p(0, "kê metformin", [3], ["Đơn thuốc hôm nay tôi kê metformin 500 mg"], tinh_huong="kế hoạch",
             hanh_vi="kế hoạch")]
    assert not {"PLAN_AS_FACT", "RECOMMENDATION_AS_FACT"} & _ma(ps, HOI_KE, 0)


def test_hoi_ve_thuoc_dang_dung_khong_bao():
    hoi = "Bác sĩ: Anh đang uống metformin mấy viên một ngày nhé?\nBệnh nhân: Dạ hai viên ạ."
    ps = [_p(0, "đang dùng metformin hai viên mỗi ngày", [1, 2], ["Anh đang uống metformin", "Dạ hai viên ạ"],
             nguoi_noi="bệnh nhân", tinh_huong="thực tế")]
    assert "PLAN_AS_FACT" not in _ma(ps, hoi, 0)


# ---- Vong 2: con so khong don vi bi doi (v2mr_0009 #10, v2mr_0270 #0, v2mr_0170 #2)
HOI_SO = "\n".join([
    "Bác sĩ: Cháu bị sao?",
    "Người nhà: Cháu nó phát hiện bị cả cụm 2 đến 4 răng liền kề lung lay hơn một tuần.",
    "Bác sĩ: Đụng dập phần mềm và tụ máu cơ tứ đầu đùi phải độ 2 sau chấn thương thể thao.",
    "Người nhà: Sinh thiết thấy teo nhung mao độ Marsh 3, có ba răng sâu.",
])


def test_so_khong_don_vi_bi_doi_bi_bat():
    ps = [_p(0, "cả cụm 4 đến 4 răng liền kề lung lay", [2], ["cả cụm 2 đến 4 răng liền kề lung lay"],
             nguoi_noi="người nhà"),
          _p(1, "tụ máu cơ tứ đầu đùi phải độ 4", [3], ["tụ máu cơ tứ đầu đùi phải độ 2"], hanh_vi="nhận định"),
          _p(2, "teo nhung mao độ Marsh 5", [4], ["teo nhung mao độ Marsh 3"], nguoi_noi="người nhà")]
    for i in range(3):
        assert "NUMERIC_MISMATCH" in _ma(ps, HOI_SO, i), i


def test_so_khong_don_vi_dung_khong_bao():
    ps = [_p(0, "cả cụm 2 đến 4 răng liền kề lung lay", [2], ["cả cụm 2 đến 4 răng liền kề lung lay"],
             nguoi_noi="người nhà"),
          _p(1, "tụ máu cơ tứ đầu đùi phải độ 2", [3], ["tụ máu cơ tứ đầu đùi phải độ 2"], hanh_vi="nhận định"),
          _p(2, "3 răng sâu", [4], ["có ba răng sâu"], nguoi_noi="người nhà")]
    for i in range(3):
        assert "NUMERIC_MISMATCH" not in _ma(ps, HOI_SO, i), i


# ---- Vong 3: dao phu dinh khong qua cap hoi-dap (v2mr_0003 #3, v2mr_0009 #7, v2mr_0014 #4)
HOI_PD = "\n".join([
    "Bác sĩ: Lúc sinh cháu thế nào?",
    "Người nhà: Thưa bác sĩ, có sinh non.",
    "Người nhà: Dạ thưa bác sĩ, em thì bị cường giáp, còn vợ em thì chưa thấy gì ạ.",
    "Bệnh nhân: Vâng, tôi ghi nhớ kỹ là mình bị dị ứng sulfamid.",
    "Bệnh nhân: Tôi không bị dị ứng penicillin, cũng không ho.",
    "Bác sĩ: Chị có sốt không?",
    "Bệnh nhân: Dạ không ạ.",
])


def test_ban_ghi_phu_dinh_ma_cau_goc_khang_dinh_bi_bat():
    ps = [_p(0, "sinh non", [2], ["có sinh non"], nguoi_noi="người nhà", phu_dinh=True),
          _p(1, "cường giáp", [3], ["em thì bị cường giáp"], nguoi_noi="người nhà", chu_the_id=1, phu_dinh=True),
          _p(2, "dị ứng sulfamid", [4], ["mình bị dị ứng sulfamid"], nguoi_noi="bệnh nhân", phu_dinh=True)]
    for i in range(3):
        assert "NEGATION_FLIP" in _ma(ps, HOI_PD, i), i


def test_ban_ghi_khang_dinh_ma_cau_goc_phu_dinh_bi_bat():
    ps = [_p(0, "dị ứng penicillin", [5], ["Tôi không bị dị ứng penicillin"], nguoi_noi="bệnh nhân"),
          _p(1, "ho", [5], ["cũng không ho"], nguoi_noi="bệnh nhân")]
    # chieu nay da co POSSIBLE_NEGATION_ERROR; chi can dung nhom NEGATION_ASSERTION
    nhom = {"NEGATION_FLIP", "POSSIBLE_NEGATION_ERROR", "NEGATION_SCOPE_ERROR"}
    assert nhom & _ma(ps, HOI_PD, 0)
    assert nhom & _ma(ps, HOI_PD, 1)


def test_phu_dinh_dung_khong_bao():
    ps = [_p(0, "dị ứng penicillin", [5], ["Tôi không bị dị ứng penicillin"], nguoi_noi="bệnh nhân", phu_dinh=True),
          _p(1, "sốt", [6, 7], ["Chị có sốt không?", "Dạ không ạ."], nguoi_noi="bệnh nhân", phu_dinh=True),
          _p(2, "sinh non", [2], ["có sinh non"], nguoi_noi="người nhà"),
          _p(3, "cường giáp", [3], ["em thì bị cường giáp"], nguoi_noi="người nhà", chu_the_id=1)]
    for i in range(4):
        assert "NEGATION_FLIP" not in _ma(ps, HOI_PD, i), i


# ---- Vong 4: bao nham bo sot chung chung tren loi xa giao (ban sach: 5,8 canh bao/ca; v2mr_0003, v2mr_0009)
import pytest  # noqa: E402

from src.canh_bao import bo_sot  # noqa: E402
from src.canh_bao.phat_hien import NguCanh  # noqa: E402


@pytest.mark.parametrize("doan", ["Chúc bác sĩ công tác tốt ạ", "Vâng em nghe", "hơi bận nhưng vẫn ổn ạ",
                                  "Cho bác sĩ hỏi", "Dạ thưa bác", "Tiếp theo", "xin phép về",
                                  "tôi là mẹ đưa cháu đi khám bác sĩ ạ", "Dạ đúng rồi bác"])
def test_loi_xa_giao_khong_bao_bo_sot(doan):
    ctx = NguCanh("Bác sĩ: Chào chị.\nNgười nhà: " + doan)
    assert bo_sot.phan_loai(ctx, 2, doan) == []


@pytest.mark.parametrize("doan", ["cháu bị đau bụng quặn từng cơn", "đi ngoài phân đen", "mẹ em bị tiểu đường",
                                  "em hay chóng mặt khi đứng dậy"])
def test_noi_dung_lam_sang_van_bao(doan):
    ctx = NguCanh("Bác sĩ: Chào chị.\nNgười nhà: " + doan)
    assert bo_sot.phan_loai(ctx, 2, doan) != []


def test_phu_dinh_kieu_da_do_hoac_thuoc_em_khong_bao():
    # v2mr_0157, v2mr_2788: dap an ghi phu dinh cho "đỡ hẳn rồi" va "uống thuốc đều êm"
    hoi = ("Bệnh nhân: Sáng nay thì bờ mi đỏ rực cương tụ, từ hôm chủ nhật thì đỡ hẳn rồi.\n"
           "Bác sĩ: Chị có dị ứng thuốc gì không?\nBệnh nhân: Chị uống thuốc đều êm ạ.")
    ps = [_p(0, "bờ mi đỏ rực cương tụ", [1], ["bờ mi đỏ rực cương tụ"], nguoi_noi="bệnh nhân", phu_dinh=True),
          _p(1, "dị ứng thuốc", [2, 3], ["Chị có dị ứng thuốc gì không?", "Chị uống thuốc đều êm ạ"],
             nguoi_noi="bệnh nhân", phu_dinh=True)]
    for i in range(2):
        assert "NEGATION_FLIP" not in _ma(ps, hoi, i), i


# ---- Vong 5: doan chua ghi bi che (v2mr_1014, v2mr_0244: di ung nguoi nha; v2mr_0581: thuoc dinh chinh)
from src import khoa_bang_chung as kbc  # noqa: E402


def _chua_ghi(ps, hoi):
    return [d["doan"] for d in kbc.khoa_ca(ps, hoi)["doan_chua_ghi"]]


def test_chat_di_ung_khac_khong_bi_che_boi_dong_di_ung_khac():
    hoi = ("Bác sĩ: Nhà mình có ai dị ứng gì không?\n"
           "Người nhà: Vâng em nghe, anh trai thì dị ứng trứng, còn bé nhà tôi chưa thấy bị bao giờ.")
    ps = [_p(0, "dị ứng thuốc", [2], ["còn bé nhà tôi chưa thấy bị bao giờ"], nguoi_noi="người nhà", phu_dinh=True)]
    assert any("trứng" in d for d in _chua_ghi(ps, hoi))


def test_ban_bi_thay_the_khong_che_ten_thuoc():
    hoi = "Bác sĩ: Anh đang uống thuốc gì?\nBệnh nhân: Tôi có uống amoxicillin 250 mg, à nhầm, 500 mg mới đúng."
    ps = [_p(0, "amoxicillin 250 mg", [2], ["Tôi có uống amoxicillin 250 mg"], nguoi_noi="bệnh nhân",
             trang_thai="bị thay thế")]
    assert any("amoxicillin" in d for d in _chua_ghi(ps, hoi))


def test_di_ung_da_ghi_va_phu_dinh_chung_khong_bao():
    hoi = ("Bác sĩ: Có dị ứng gì không?\n"
           "Người nhà: Anh trai thì dị ứng trứng, còn bé không dị ứng gì cả.")
    ps = [_p(0, "anh trai dị ứng trứng", [2], ["Anh trai thì dị ứng trứng"], nguoi_noi="người nhà", chu_the_id=1),
          _p(1, "dị ứng", [2], ["còn bé không dị ứng gì cả"], nguoi_noi="người nhà", phu_dinh=True)]
    assert not any("dị ứng" in d for d in _chua_ghi(ps, hoi))
