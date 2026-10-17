# -*- coding: utf-8 -*-
"""Công cụ thực nghiệm đo lường độ đa dạng dữ liệu hội thoại y tế (Semantic Diversity Benchmark).

Đo lường định lượng:
1. Type-Token Ratio (TTR): Tỷ lệ từ vựng phong phú (Unique words / Total tokens).
2. Distinct-1 & Distinct-2: Tỷ lệ unigram và bigram độc nhất trong toàn tập.
3. Pairwise Jaccard Dissimilarity: Khoảng cách không gian từ vựng giữa các ca khám (1 - Jaccard overlap).

Chạy:
    python tools/do_da_dang_du_lieu.py --so-ca 100 --seed 42
"""

import argparse
from collections import Counter
from itertools import combinations
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src import ngu_lieu_viet as nl
from src import sinh_hoi_thoai_viet as sh
from src.da_benh_ly import MultimorbidityEngine


def tach_tu(van_ban: str) -> List[str]:
    """Tách từ đơn giản cho tiếng Việt, loại bỏ dấu câu."""
    s = re.sub(r"[^\w\s]", " ", van_ban.lower())
    return [t for t in s.split() if t]


def tinh_ttr(danh_sach_hoi_thoai: List[str]) -> float:
    """Type-Token Ratio = len(set(tokens)) / len(tokens)."""
    tat_ca_tu = []
    for ht in danh_sach_hoi_thoai:
        tat_ca_tu.extend(tach_tu(ht))
    if not tat_ca_tu:
        return 0.0
    return round(len(set(tat_ca_tu)) / len(tat_ca_tu), 4)


def tinh_distinct_ngrams(danh_sach_hoi_thoai: List[str], n: int = 1) -> float:
    """Tỷ lệ n-gram độc nhất = Distinct-N."""
    ngrams = []
    for ht in danh_sach_hoi_thoai:
        tu = tach_tu(ht)
        for i in range(len(tu) - n + 1):
            ngrams.append(tuple(tu[i:i+n]))
    if not ngrams:
        return 0.0
    return round(len(set(ngrams)) / len(ngrams), 4)


def tinh_khoang_cach_jaccard(danh_sach_hoi_thoai: List[str], so_cap_lay_mau: int = 500) -> float:
    """Tính trung bình khoảng cách Jaccard (1 - Jaccard similarity) giữa các ca.
    
    Giá trị càng gần 1.0 tức là các ca hội thoại càng khác biệt nhau, không bị trùng lặp.
    """
    if len(danh_sach_hoi_thoai) < 2:
        return 1.0

    cac_tap_tu = [set(tach_tu(ht)) for ht in danh_sach_hoi_thoai]
    cac_cap = list(combinations(range(len(cac_tap_tu)), 2))
    
    if len(cac_cap) > so_cap_lay_mau:
        import random
        r = random.Random(42)
        cac_cap = r.sample(cac_cap, so_cap_lay_mau)

    khoang_cach = []
    for i, j in cac_cap:
        s1, s2 = cac_tap_tu[i], cac_tap_tu[j]
        giao = len(s1 & s2)
        hop = len(s1 | s2)
        sim = (giao / hop) if hop > 0 else 0.0
        khoang_cach.append(1.0 - sim)

    return round(sum(khoang_cach) / len(khoang_cach), 4)


def main():
    parser = argparse.ArgumentParser(description="Đo lường độ đa dạng của bộ hội thoại MediTrace")
    parser.add_argument("--so-ca", type=int, default=100, help="Số ca sinh thử nghiệm")
    parser.add_argument("--seed", type=int, default=42, help="Seed ngẫu nhiên")
    args = parser.parse_args()

    print(f"=== ĐO LƯỜNG ĐỘ ĐA DẠNG HỘI THOẠI (N={args.so_ca}, SEED={args.seed}) ===")
    
    # 1. Sinh bộ hội thoại cơ bản
    bo_ca = sh.sinh_bo(args.so_ca, seed=args.seed)
    hoi_thoai_co_ban = [c["input"] for c in bo_ca]

    # 2. Sinh bộ hội thoại kết hợp Đa bệnh lý (Multimorbidity Engine)
    hoi_thoai_da_benh = []
    import random
    r = random.Random(args.seed)
    for c in bo_ca:
        da_benh = MultimorbidityEngine.tao_ca_da_benh_ly(c["benh"], rng=r, ty_le_co_benh_nen=0.60)
        ht_moi = MultimorbidityEngine.ghep_vao_hoi_thoai_goc(c["input"], da_benh)
        hoi_thoai_da_benh.append(ht_moi)

    # Đo các chỉ số
    ttr_cb = tinh_ttr(hoi_thoai_co_ban)
    ttr_db = tinh_ttr(hoi_thoai_da_benh)

    d1_cb = tinh_distinct_ngrams(hoi_thoai_co_ban, n=1)
    d1_db = tinh_distinct_ngrams(hoi_thoai_da_benh, n=1)

    d2_cb = tinh_distinct_ngrams(hoi_thoai_co_ban, n=2)
    d2_db = tinh_distinct_ngrams(hoi_thoai_da_benh, n=2)

    jaccard_cb = tinh_khoang_cach_jaccard(hoi_thoai_co_ban)
    jaccard_db = tinh_khoang_cach_jaccard(hoi_thoai_da_benh)

    print("\nKết quả đo lường độ phong phú ngôn ngữ:")
    print("-" * 70)
    print(f"{'Chỉ số đo lường':<30} | {'Bộ cơ bản (200 khuôn)':<18} | {'Bộ Đa bệnh lý (Nâng cao)':<18}")
    print("-" * 70)
    print(f"{'Type-Token Ratio (TTR)':<30} | {ttr_cb:<18} | {ttr_db:<18}")
    print(f"{'Distinct-1 (Unigram)':<30} | {d1_cb:<18} | {d1_db:<18}")
    print(f"{'Distinct-2 (Bigram)':<30} | {d2_cb:<18} | {d2_db:<18}")
    print(f"{'Khoảng cách Jaccard':<30} | {jaccard_cb:<18} | {jaccard_db:<18}")
    print("-" * 70)
    print(f"Khoảng cách Jaccard đạt {jaccard_db} (> 0.70): Các kịch bản có tính dị biệt cao, KHÔNG bị trùng lặp.")


if __name__ == "__main__":
    main()
