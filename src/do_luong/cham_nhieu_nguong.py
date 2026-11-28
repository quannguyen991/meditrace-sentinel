# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Chấm ghép mệnh đề ở nhiều ngưỡng giống từ.
Vào → Ra : mệnh đề dự đoán, đáp án, các ngưỡng → precision, recall và F1.
Đọc từ   : ghep_menh_de() của bộ chấm hệ thống, giữ cách chuẩn hóa và phân xử hòa.
"""
from src.do_luong.cham_he_thong import ghep_menh_de


def cham_o_cac_nguong(du_doan: list[dict], dap_an: list[dict],
                      cac_nguong=(0.4, 0.5, 0.6, 0.7)) -> dict:
    """Ghép một-một ở từng ngưỡng; tập rỗng có điểm bằng không."""
    ket_qua = {}
    for nguong in cac_nguong:
        dung = len(ghep_menh_de(dap_an, du_doan, nguong=nguong))
        p = dung / len(du_doan) if du_doan else 0.0
        r = dung / len(dap_an) if dap_an else 0.0
        ket_qua[nguong] = {"precision": p, "recall": r,
                           "f1": 2 * p * r / (p + r) if p + r else 0.0}
    return ket_qua
