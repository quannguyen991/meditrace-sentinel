# -*- coding: utf-8 -*-
"""Mot cho duy nhat khai bao duong dan. Khong hardcode o noi khac.

Thu muc goc cua du lieu ke thua co dau cach va ky tu '@' trong ten
("D:/VAIC DE @"), nen moi noi dung Path chu khong noi chuoi.
Thu muc do la CHI DOC — khong ghi gi vao day.
"""
import os
from pathlib import Path

GOC_DU_AN = Path(__file__).resolve().parent.parent
GOC_VAIC = Path("D:/VAIC DE @")

# Thu muc du lieu cua cuoc thi cu. CHI CON de cac script cu chay lai duoc va
# de test doi chieu loi nhac; KHONG con tep nao cua du an dung du lieu tu day.
# Ban to chuc khuyen khong dung tai san cua ho de tranh cau hoi ve tinh chinh
# thong, va do dau vet cho thay bo du lieu do rat nhieu kha nang la ban dich
# tu tieng Anh. Du an chuyen han sang bo tu sinh `hoi_thoai_viet_3000.jsonl`.
TRAIN_JSONL = GOC_VAIC / "train (2).jsonl"




THU_MUC_KET_QUA = GOC_DU_AN / "docs" / "ket-qua"

# Thu muc du lieu doi duoc bang bien moi truong MEDITRACE_DATA.
#
# VI SAO CAN (19/09/2026). Ten tep ket qua `ra_<nhanh>_<tap>.jsonl` KHONG kem
# ten mo hinh. Chay cung mot nhanh voi mot mo hinh khac — mo hinh nen chua huan
# luyen, hay mot mo hinh thuong mai lam moc so — se DE LEN ket qua cu ma khong
# ai biet. Do dung nhom loi da xay ra ngay 19/09: cham nham the he du lieu vi
# hai bo trung ten tep.
#
# Cach dung: MEDITRACE_DATA=.../data-gpt python -m src.nhanh ...
# Thu muc do phai co san cac tep bo du lieu; `cham_he_thong --thu-muc` tro vao
# cung cho.
THU_MUC_DU_LIEU = Path(os.environ.get("MEDITRACE_DATA") or (GOC_DU_AN / "data"))
THU_MUC_MO_HINH = GOC_DU_AN / "models"

MODEL_NHO = "Qwen/Qwen3-1.7B"
MODEL_GO_LOI = "Qwen/Qwen3-4B"
MODEL_CHINH = "Qwen/Qwen3-8B"

for _d in (THU_MUC_KET_QUA, THU_MUC_DU_LIEU, THU_MUC_MO_HINH):
    _d.mkdir(parents=True, exist_ok=True)
