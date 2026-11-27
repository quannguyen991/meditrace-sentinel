# -*- coding: utf-8 -*-
"""[Lớp cảnh báo]
Làm gì   : Cảnh báo dòng bản nháp có thể sai vì lỗi chép giọng nói, tách riêng do xảy ra
           trước bước mô hình.
Vào → Ra : bản nháp + thông tin chép lời từng dòng → danh sách CanhBao về dòng nghi chép sai
Đọc từ   : canh_bao() sinh cảnh báo lỗi chép giọng nói cho từng dòng
Mục lục (các hàm/lớp chính):
  canh_bao()  Cảnh báo chép âm: người nói chưa chắc, độ tin cậy thấp
Gọi tới  : canh_bao/loai, canh_bao/phat_hien, canh_bao/so_lieu
Dùng bởi : canh_bao/gop
Bản đồ   : BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Cảnh báo CHÉP ÂM — lỗi TRƯỚC khâu mô hình, tách riêng (đặc tả mục 34).

Chỉ sinh khi lời thoại đến từ `src.audio` và có thông tin độ tin cậy theo lượt.
Bộ dữ liệu hiện tại là văn bản sạch: không có meta_asr thì không có cảnh báo nào
ở đây, và không bao giờ tính các cảnh báo này là lỗi của mô hình sinh.
Nhóm ASR_UPSTREAM không đổi trạng thái (xem `CanhBao.anh_huong_trang_thai`).
"""
import re
from typing import Dict, List

from src.canh_bao import so_lieu
from src.canh_bao.loai import CAO, NGHI_RUI_RO, TRUNG, CanhBao, muc_do

NGUONG_TIN_CAY = 0.6
_PHU_DINH = re.compile(r"(?<!\w)(không|chưa|chẳng|chả)(?!\w)")


# ═══ canh_bao() — Cảnh báo chép âm: người nói chưa chắc, độ tin cậy thấp ══════════════
# Chỉ chạy khi có siêu dữ liệu chép âm theo lượt; độ tin cậy dưới 0,6 thì phân loại
# thuốc, số, phủ định hoặc chung.
def canh_bao(ctx, ps, meta_asr: Dict[int, dict], loai_theo_id) -> List[CanhBao]:
    from src.canh_bao.phat_hien import _ten_thuoc, _thuong
    ra = []
    for p in ps:
        for s in ctx.dan(p):
            m = meta_asr.get(s) or {}
            van = _thuong(ctx.luot[s][1])
            loai = loai_theo_id.get(p.id, "khac")

            def them(ma, ly_do, bd=TRUNG):
                ra.append(CanhBao(ma=ma, phat_bieu_id=p.id, luot=[s], trich=[ctx.luot[s][1]], ly_do=ly_do,
                                  ket_luan=NGHI_RUI_RO, bat_dinh=bd, bo_phat_hien="asr",
                                  muc_do=muc_do(ma, loai), loai_tt=loai))
            if m.get("nguoi_noi_chua_chac"):
                them("SPEAKER_DIARIZATION_UNCERTAIN", f"Lượt {s}: máy chưa chắc ai nói.")
            tc = m.get("asr_confidence")
            if tc is None or tc >= NGUONG_TIN_CAY:
                continue
            if _ten_thuoc(p):
                them("POSSIBLE_MEDICATION_TRANSCRIPTION_ERROR",
                     f"Lượt {s} chép âm với độ tin cậy {tc:.2f}; tên thuốc có thể bị nghe sai.", CAO)
            elif so_lieu.tach(van):
                them("POSSIBLE_NUMERIC_TRANSCRIPTION_ERROR",
                     f"Lượt {s} chép âm với độ tin cậy {tc:.2f}; con số có thể bị nghe sai.", CAO)
            elif _PHU_DINH.search(van):
                them("POSSIBLE_NEGATION_TRANSCRIPTION_ERROR",
                     f"Lượt {s} chép âm với độ tin cậy {tc:.2f}; “không/chưa” có thể bị nghe sai.", CAO)
            else:
                them("ASR_LOW_CONFIDENCE", f"Lượt {s} chép âm với độ tin cậy {tc:.2f}.")
    return ra
