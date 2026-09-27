# -*- coding: utf-8 -*-
"""Bo cham diem: ROUGE + Section F1, cai dat DOC LAP.

VI SAO VIET LAI. Ban truoc boc `evaluate.py` cua ban to chuc mot cuoc thi ma
tac gia tung du. Ban to chuc khuyen khong nen dung tai san cua cuoc thi do de
tranh cau hoi ve tinh chinh thong, va lo`i khuyen do dung: bo du lieu di kem
cung da bi do dau vet cho thay rat nhieu kha nang la ban dich tu tieng Anh.

Vi the du an nay cat het: du lieu, bo cham, va ca loi nhac he thong.

Cai dat hien tai dung `rouge-score` — ban tham chieu cua Google, trich dan
duoc — voi mot BO TACH TU rieng cho tieng Viet.

**Tach tu theo AM TIET, khong theo tu.** Tieng Viet viet roi tung am tiet;
bo tach tu mac dinh cua `rouge-score` la cho tieng Anh va se cat sai. Quy tac
o day: ha chu thuong, thay moi ky tu khong phai chu/so bang dau cach, roi cat
theo dau cach. Day cung la quy tac cac bo cham tieng Viet thuong dung, nen so
so sanh duoc voi cong trinh khac.

Cong thuc diem tong hop `0,6 x ROUGE_avg + 0,4 x SectionF1` la cach cham pho
bien cho tom tat lam sang. **Du an nay chung minh no NGUOC DAU voi loi doi
chu the** (xem `chung_chi_thuoc_do.py`), nen no duoc bao cao nhu mot chi so
tham chieu, khong phai lam trong tai.
"""
import re

from rouge_score import rouge_scorer, tokenizers

TRONG_SO_ROUGE = 0.6
TRONG_SO_SECTION = 0.4


class TachAmTiet(tokenizers.Tokenizer):
    """Ha chu thuong, bo dau cau, cat theo dau cach."""

    def tokenize(self, van_ban):
        van = re.sub(r"[^\w\s\d]", " ", str(van_ban or "").lower())
        return [t for t in van.split() if t]


_cham = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"],
                                 tokenizer=TachAmTiet())


def rouge(du_doan, tham_chieu):
    """-> {rouge1, rouge2, rougel, avg} theo F-measure."""
    r = _cham.score(tham_chieu or "", du_doan or "")
    r1, r2, rl = (r["rouge1"].fmeasure, r["rouge2"].fmeasure,
                  r["rougeL"].fmeasure)
    return {"rouge1": r1, "rouge2": r2, "rougel": rl,
            "avg": (r1 + r2 + rl) / 3}


def cac_muc(van_ban):
    """Rut ten cac muc cua benh an.

    Quy tac: mot dong duoc coi la tieu de muc khi no VIET HOA TOAN BO, dai
    hon 3 ky tu, va khong chua chu so. Do la quy tac thuong dung cho benh an
    tieng Viet, va cung la quy tac de bi danh lua — mot muc do he thong tu
    dat ra (vi du "CAN XAC NHAN") se bi dem la mot muc du doan thua du no
    khong phai loi noi dung. Diem nay duoc bao cao rieng.
    """
    ra = set()
    for dong in (van_ban or "").split("\n"):
        t = dong.strip()
        if len(t) > 3 and not any(c.islower() for c in t) \
                and not any(c.isdigit() for c in t):
            ra.add(t)
    return ra


def section_f1(du_doan, tham_chieu):
    p, r = cac_muc(du_doan), cac_muc(tham_chieu)
    if not p and not r:
        return 1.0
    tp = len(p & r)
    if tp == 0:
        return 0.0
    prec, rec = tp / len(p), tp / len(r)
    return 2 * prec * rec / (prec + rec)


def diem_cuoi(du_doan, tham_chieu):
    r = rouge(du_doan, tham_chieu)
    sf1 = section_f1(du_doan, tham_chieu)
    return {
        "rouge1": r["rouge1"],
        "rouge2": r["rouge2"],
        "rougel": r["rougel"],
        "rouge_avg": r["avg"],
        "section_f1": sf1,
        "final": TRONG_SO_ROUGE * r["avg"] + TRONG_SO_SECTION * sf1,
    }
