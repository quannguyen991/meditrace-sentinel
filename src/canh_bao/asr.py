# -*- coding: utf-8 -*-
"""Canh bao CHEP AM — loi TRUOC khau mo hinh, tach rieng (dac ta muc 34).

Chi sinh khi loi thoai den tu `src.audio` va co thong tin do tin cay theo luot.
Bo du lieu hien tai la van ban sach: khong co meta_asr thi khong co canh bao nao
o day, va khong bao gio tinh cac canh bao nay la loi cua mo hinh sinh.
Nhom ASR_UPSTREAM khong doi trang thai (xem `CanhBao.anh_huong_trang_thai`).
"""
import re
from typing import Dict, List

from src.canh_bao import so_lieu
from src.canh_bao.loai import CAO, NGHI_RUI_RO, TRUNG, CanhBao, muc_do

NGUONG_TIN_CAY = 0.6
_PHU_DINH = re.compile(r"(?<!\w)(không|chưa|chẳng|chả)(?!\w)")


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
