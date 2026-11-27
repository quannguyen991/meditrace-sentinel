# -*- coding: utf-8 -*-
"""Đánh giá đa nguồn độc lập ngoài kho khuôn tự sinh (Yêu cầu 3 BGK).

Đo lường khả năng tổng quát hóa của các tầng xác định (chuẩn hóa phương ngữ,
khử định danh PII/PHI, trích thực thể dược lý Aho-Corasick, nhận diện số liệu/liều,
và tách vai/phủ định) trên **5 bộ dữ liệu tiếng Việt công khai độc lập hoàn toàn**:
1. ViDia2Std (AAAI-26, 1.603 câu test phương ngữ 63 tỉnh).
2. ViHealthQA (2.013 câu hỏi bệnh nhân thật trên hệ thống Vinmec/y tế).
3. ViMedAQA (500 mẫu test hỏi-đáp y khoa tiếng Việt).
4. ViMQ (câu hỏi bệnh nhân có nhãn thực thể triệu chứng/bệnh/thuốc).
5. PhoNER_COVID19 (văn bản y tế tiếng Việt có nhãn thực thể).
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from src.bo_du_lieu import nap_vimq
from src.canh_bao import so_lieu
from src.cong_cu_lam_sang.tra_duoc_thu_aho_corasick import BoTraCuuDuocThuAhoCorasick
from src.duong_ong import b0_chuan_hoa_phuong_ngu as chuan_hoa
from src.do_luong import do_vidia2std
from src.he_thong import duong_dan, khu_dinh_danh

_TRA_CUU_THUOC = BoTraCuuDuocThuAhoCorasick()


def danh_gia_vidia2std(base_dir: Path) -> Dict[str, Any]:
    test_csv = base_dir / "ViDia2Std" / "test.csv"
    if not test_csv.exists():
        return {"co_du_lieu": False}
    theo_vung, _ = do_vidia2std.do_tep(test_csv, gom_can_hoi=True)
    tong = theo_vung.get("tat_ca") or Counter()
    thay = tong["doi_dung"] + tong.get("doi_khac_chu", 0) + tong["bo_qua"]
    return {
        "co_du_lieu": True,
        "so_cau": tong["so_cau"],
        "cho_thay_tu": thay,
        "doi_dung": tong["doi_dung"],
        "ty_le_doi_dung_pct": round(tong["doi_dung"] / max(thay, 1) * 100, 1),
        "doi_khac_chu": tong.get("doi_khac_chu", 0),
        "tong_phu_pct": round((tong["doi_dung"] + tong.get("doi_khac_chu", 0)) / max(thay, 1) * 100, 1),
        "doi_thua": tong["doi_thua"],
        "loi_tu_goc_pct": round(tong.get("loi_goc", 0) / max(tong.get("so_tu", 1), 1) * 100, 1),
        "loi_tu_sau_pct": round(tong.get("loi_sau", 0) / max(tong.get("so_tu", 1), 1) * 100, 1),
    }


def _quet_van_ban_lam_sang(van_ban_list: List[str]) -> Dict[str, Any]:
    co_thuoc = 0
    co_so_lieu = 0
    co_phuong_ngu = 0
    co_pii = 0
    pii_con_sot = 0
    for vb in van_ban_list:
        sach = chuan_hoa.chuan_hoa(vb)
        if sach != vb.lower():
            co_phuong_ngu += 1
        if _TRA_CUU_THUOC.nhan_dien_thuoc_trong_van_ban(vb):
            co_thuoc += 1
        if so_lieu.tach(vb):
            co_so_lieu += 1
        an = khu_dinh_danh.ClinicalDeidentifier.an_danh_van_ban(vb)
        if an.tong_so_thuc_the > 0:
            co_pii += 1
            if an.con_sot:
                pii_con_sot += 1
    return {
        "so_mau": len(van_ban_list),
        "mau_chuan_hoa_phuong_ngu": co_phuong_ngu,
        "mau_phat_hien_thuoc_aho_corasick": co_thuoc,
        "mau_trich_so_lieu_lam_sang": co_so_lieu,
        "mau_che_pii": co_pii,
        "pii_con_sot": pii_con_sot,
    }


def danh_gia_vihealthqa(base_dir: Path) -> Dict[str, Any]:
    p = base_dir / "ViHealthQA" / "test.csv"
    if not p.exists():
        return {"co_du_lieu": False}
    rows = list(csv.DictReader(open(p, encoding="utf-8")))
    qs = [str(r.get("question") or "") for r in rows if r.get("question")]
    ans = [str(r.get("answer") or "") for r in rows if r.get("answer")]
    res = _quet_van_ban_lam_sang(qs)
    res["mau_phat_hien_thuoc_trong_cau_tra_loi"] = sum(
        1 for a in ans if _TRA_CUU_THUOC.nhan_dien_thuoc_trong_van_ban(a)
    )
    return {"co_du_lieu": True, **res}


def danh_gia_vimedaqa(base_dir: Path) -> Dict[str, Any]:
    p = base_dir / "ViMedAQA" / "test_sample_500.json"
    if not p.exists():
        return {"co_du_lieu": False}
    rows = json.loads(p.read_text(encoding="utf-8"))
    qs = [str(r.get("question") or "") for r in rows if r.get("question")]
    return {"co_du_lieu": True, **_quet_van_ban_lam_sang(qs)}


def danh_gia_vimq(base_dir: Path) -> Dict[str, Any]:
    p = base_dir / "ViMQ" / "data" / "test.json"
    if not p.exists():
        return {"co_du_lieu": False}
    mau = nap_vimq.doc_vimq(p, "test")
    caus = [m["cau"] for m in mau]
    tong_thuoc_nhan = 0
    thuoc_khop = 0
    for m in mau:
        for tt in m.get("thuc_the") or []:
            if "MED" in str(tt.get("loai", "")).upper() or "DRUG" in str(tt.get("loai", "")).upper():
                tong_thuoc_nhan += 1
                if _TRA_CUU_THUOC.nhan_dien_thuoc_trong_van_ban(tt["text"]):
                    thuoc_khop += 1
    return {
        "co_du_lieu": True,
        **_quet_van_ban_lam_sang(caus),
        "tong_thuc_the_thuoc_vimq": tong_thuoc_nhan,
        "khop_aho_corasick": thuoc_khop,
    }


def _trich_thuc_the_gold_phoner(words: List[str], tags: List[str], loai_target: set) -> List[str]:
    spans: List[str] = []
    cur: List[str] = []
    for w, t in zip(words, tags):
        if t.startswith("B-") and t[2:] in loai_target:
            if cur:
                spans.append(" ".join(cur))
            cur = [w]
        elif t.startswith("I-") and cur and t[2:] in loai_target:
            cur.append(w)
        else:
            if cur:
                spans.append(" ".join(cur))
                cur = []
    if cur:
        spans.append(" ".join(cur))
    return spans


def danh_gia_phoner(base_dir: Path) -> Dict[str, Any]:
    p = base_dir / "PhoNER_COVID19" / "data" / "syllable" / "test_syllable.json"
    if not p.exists():
        return {"co_du_lieu": False}
    caus: List[str] = []
    gold_tong = 0
    gold_che = 0
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        words = obj.get("words") or []
        tags = obj.get("tags") or []
        if not words:
            continue
        van = " ".join(words)
        caus.append(van)
        if len(caus) <= 1000 and tags:
            spans = _trich_thuc_the_gold_phoner(words, tags, {"NAME", "PATIENT_ID"})
            if spans:
                an = khu_dinh_danh.ClinicalDeidentifier.an_danh_van_ban(van)
                sau_che = an.van_ban_da_an_danh
                for sp in spans:
                    gold_tong += 1
                    if sp not in sau_che:
                        gold_che += 1
    return {
        "co_du_lieu": True,
        **_quet_van_ban_lam_sang(caus[:1000]),
        "gold_pii_name_id_tong": gold_tong,
        "gold_pii_name_id_che_duoc": gold_che,
        "gold_pii_name_id_recall_pct": round(gold_che / max(gold_tong, 1) * 100, 1),
    }


def chay_tat_ca() -> Dict[str, Any]:
    base = duong_dan.THU_MUC_DU_LIEU / "ngoai"
    kq = {
        "ViDia2Std_test_1603": danh_gia_vidia2std(base),
        "ViHealthQA_test": danh_gia_vihealthqa(base),
        "ViMedAQA_test_500": danh_gia_vimedaqa(base),
        "ViMQ_test": danh_gia_vimq(base),
        "PhoNER_COVID19_test_1000": danh_gia_phoner(base),
    }
    return kq


if __name__ == "__main__":
    res = chay_tat_ca()
    out_json = duong_dan.THU_MUC_KET_QUA / "da-nguon-doc-lap.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
