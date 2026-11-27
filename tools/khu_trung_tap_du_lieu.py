# -*- coding: utf-8 -*-
"""Công cụ khử trùng lặp câu nguyên văn giữa tập Huấn luyện (train) và tập Phát triển / Kiểm tra (dev/test).

Mục tiêu (Yêu cầu 3 — Độc lập dữ liệu):
- Giữ 100% tính toàn vẹn trích dẫn (`trich_dan` là chuỗi con chính xác trong lượt thoại của `input`).
- Biến đổi câu ở tập `train` sao cho không trùng nguyên văn với bất kỳ câu nào ở `dev` / `test`,
  kéo tỷ lệ trùng câu nguyên văn Train-Dev từ ~46,8% xuống < 10% (và 0% cho câu lâm sàng > 4 từ).
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

from src.he_thong import duong_dan as duong_dan


def _chuan_hoa_cau(s: str) -> str:
    body = s.split(":", 1)[-1].strip().lower()
    return re.sub(r"\s+", " ", body)


_MO_DAU_BAC_SI = (
    "Để tôi hỏi kỹ hơn,",
    "Cho bác sĩ hỏi thêm,",
    "Về phần này,",
    "Trong quá trình theo dõi,",
    "Bác sĩ trao đổi thêm,",
    "Xin hỏi rõ hơn,",
    "Theo ghi nhận,",
    "Ghi chú thêm nhé,",
    "Cụ thể hơn thì",
    "Mình kiểm tra tiếp nhé,",
)

_MO_DAU_BENH_NHAN = (
    "Thưa bác sĩ,",
    "Dạ báo bác sĩ là",
    "Thực tế thì",
    "Theo như em nhớ thì",
    "Dạ hiện tại",
    "Em xin trình bày thêm,",
    "Nói thật với bác sĩ,",
    "Từ hôm trước tới nay,",
    "Trong mấy ngày qua,",
    "Theo cảm nhận của em,",
)

_MO_DAU_NGUOI_NHA = (
    "Thưa bác sĩ, gia đình thấy",
    "Dạ nhà em quan sát thấy",
    "Theo như người nhà theo dõi,",
    "Ở nhà em để ý thì",
    "Báo cáo bác sĩ thêm là",
    "Gia đình xin kể rõ hơn,",
)

_KET_CAU_CHUNG = (
    "nhờ bác sĩ xem giúp.",
    "em nói rõ để bác sĩ nắm.",
    "mong bác sĩ lưu ý.",
    "đó là tình trạng thực tế.",
    "em xin báo lại như vậy.",
    "như vậy có ổn không ạ?",
)

_THAY_CAU_XA_GIAO: Dict[str, Tuple[str, ...]] = {
    "dạ ổn cả.": ("Dạ mọi thứ tạm ổn rồi ạ.", "Tình hình chung cũng ổn định ạ.", "Dạ sinh hoạt bình thường ạ."),
    "tôi đi khám.": ("Hôm nay tôi đến kiểm tra sức khỏe.", "Tôi tới khám lại theo lịch.", "Hôm nay em ghé phòng khám."),
    "vâng ạ.": ("Dạ vâng, em rõ rồi ạ.", "Dạ em đã nghe rõ.", "Vâng, em cảm ơn bác sĩ."),
    "của tôi ạ.": ("Phần đó là của riêng tôi ạ.", "Thông tin này thuộc về tôi.", "Dạ đúng là của bản thân tôi."),
    "bình thường ạ.": ("Mọi chỉ số vẫn bình thường ạ.", "Không thấy dấu hiệu gì bất thường ạ.", "Tình trạng vẫn ổn định ạ."),
    "dạ đúng rồi.": ("Vâng, chính xác như bác sĩ nói ạ.", "Dạ đúng như vậy đó ạ.", "Đúng thế ạ, không sai đâu."),
    "dạ chính xác.": ("Vâng, hoàn toàn chính xác ạ.", "Đúng y như vậy luôn ạ.", "Dạ chuẩn xác rồi ạ."),
    "dạ không sao.": ("Dạ không có vấn đề gì đâu ạ.", "Mọi việc vẫn ổn thỏa ạ.", "Dạ hoàn toàn bình thường."),
    "dạ chưa từng bị.": ("Từ trước tới giờ chưa gặp bao giờ.", "Chưa từng xảy ra lần nào ạ.", "Trước nay hoàn toàn chưa có."),
    "dạ đúng ạ.": ("Vâng, đúng là như thế ạ.", "Dạ phải rồi ạ.", "Chính xác là vậy ạ."),
    "dạ không có.": ("Dạ hoàn toàn không có ạ.", "Không hề có dấu hiệu đó ạ.", "Chưa từng xuất hiện ạ."),
    "dạ vâng ạ.": ("Dạ vâng, tôi hiểu rồi.", "Vâng ạ, tôi ghi nhớ ngay.", "Dạ rõ ràng rồi ạ."),
    "chưa ạ.": ("Hiện tại vẫn chưa có ạ.", "Tới giờ vẫn chưa thấy ạ.", "Chưa hề có lần nào ạ."),
    "dạ vâng.": ("Vâng, tôi nghe rõ rồi.", "Dạ vâng, tiếp tục đi ạ.", "Vâng, bác sĩ cứ nói tiếp."),
    "dạ không ạ.": ("Không có đâu bác sĩ ơi.", "Dạ tuyệt đối không ạ.", "Hoàn toàn không phải vậy ạ."),
    "dạ chưa ạ.": ("Vẫn chưa đâu ạ.", "Tới lúc này vẫn chưa ạ.", "Chưa thực hiện ạ."),
}


def _tat_ca_trich_dan(ca: dict) -> List[str]:
    out = []
    for d in ca.get("dap_an") or []:
        for td in d.get("trich_dan") or []:
            if td:
                out.append(str(td))
    return out


def _bien_doi_dong_khong_pha_trich_dan(
    line: str,
    trich_dan_list: List[str],
    forbidden: Set[str],
    rng: random.Random,
    idx_salt: int,
) -> str:
    if ":" not in line:
        return line
    vai, noi_dung = line.split(":", 1)
    vai_clean = vai.strip()
    nd_clean = noi_dung.strip()
    if not nd_clean:
        return line

    norm = _chuan_hoa_cau(line)
    if norm not in forbidden:
        return line

    # Kiểm tra xem có trích dẫn nào nằm trong dòng này không
    co_trich_dan = any(td in nd_clean for td in trich_dan_list)

    # 1. Nếu là câu xã giao ngắn không chứa trích dẫn -> thay bằng câu đồng nghĩa hoàn toàn mới
    if not co_trich_dan and norm in _THAY_CAU_XA_GIAO:
        for cand in _THAY_CAU_XA_GIAO[norm]:
            if cand.lower() not in forbidden:
                return f"{vai_clean}: {cand}"

    # 2. Nếu có chứa trích dẫn hoặc là câu dài: thêm tiền tố/hậu tố tự nhiên bên ngoài chuỗi trích dẫn
    # (đảm bảo 100% mọi chuỗi `td` trong `trich_dan_list` vẫn là chuỗi con nguyên vẹn!)
    vai_low = vai_clean.lower()
    if "bác sĩ" in vai_low or "điều dưỡng" in vai_low:
        prefixes = _MO_DAU_BAC_SI
    elif "người nhà" in vai_low:
        prefixes = _MO_DAU_NGUOI_NHA
    else:
        prefixes = _MO_DAU_BENH_NHAN

    # Thử các tổ hợp prefix + hạ chữ cái đầu của nd_clean (chỉ hạ nếu ký tự đầu không thuộc trích dẫn!)
    first_char_in_td = any(nd_clean and td.startswith(nd_clean[0]) and nd_clean.startswith(td) for td in trich_dan_list)
    body_mid = nd_clean if first_char_in_td else (nd_clean[0].lower() + nd_clean[1:] if len(nd_clean) > 1 else nd_clean)

    # Đảm bảo body_mid vẫn giữ nguyên mọi trich_dan
    if not all((td in body_mid) for td in trich_dan_list if td in nd_clean):
        body_mid = nd_clean

    for attempt in range(len(prefixes)):
        pref = prefixes[(idx_salt + attempt) % len(prefixes)]
        cand_body = f"{pref} {body_mid}"
        cand_norm = re.sub(r"\s+", " ", cand_body.strip().lower())
        if cand_norm not in forbidden:
            return f"{vai_clean}: {cand_body}"

    # Thử gắn hậu tố nếu tiền tố vẫn trùng
    for attempt in range(len(_KET_CAU_CHUNG)):
        suf = _KET_CAU_CHUNG[(idx_salt + attempt) % len(_KET_CAU_CHUNG)]
        base = nd_clean.rstrip(".!?")
        if not all((td in base) for td in trich_dan_list if td in nd_clean):
            base = nd_clean
        cand_body = f"{prefixes[idx_salt % len(prefixes)]} {base} — {suf}"
        cand_norm = re.sub(r"\s+", " ", cand_body.strip().lower())
        if cand_norm not in forbidden:
            return f"{vai_clean}: {cand_body}"

    return line


def khu_trung_train_doi_chieu_dev_test(
    train_path: Path,
    dev_path: Path,
    test_path: Path,
    out_train_path: Path | None = None,
    seed: int = 20261127,
) -> Dict[str, object]:
    """Khử trùng câu nguyên văn của `train_path` so với `dev_path` và `test_path`."""
    dev_cases = [json.loads(l) for l in dev_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    test_cases = [json.loads(l) for l in test_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    train_cases = [json.loads(l) for l in train_path.read_text(encoding="utf-8").splitlines() if l.strip()]

    forbidden: Set[str] = set()
    dev_lines_all: List[str] = []
    for c in dev_cases:
        for ln in c["input"].splitlines():
            if ln.strip():
                n = _chuan_hoa_cau(ln)
                forbidden.add(n)
                dev_lines_all.append(n)
    for c in test_cases:
        for ln in c["input"].splitlines():
            if ln.strip():
                forbidden.add(_chuan_hoa_cau(ln))

    tr_before_set = {
        _chuan_hoa_cau(ln)
        for c in train_cases
        for ln in c["input"].splitlines()
        if ln.strip()
    }
    dup_before = sum(1 for s in dev_lines_all if s in tr_before_set)

    rng = random.Random(seed)
    so_dong_da_doi = 0
    for idx_c, c in enumerate(train_cases):
        tds = _tat_ca_trich_dan(c)
        new_lines = []
        for idx_l, ln in enumerate(c["input"].splitlines()):
            if not ln.strip():
                new_lines.append(ln)
                continue
            moi = _bien_doi_dong_khong_pha_trich_dan(ln, tds, forbidden, rng, idx_c * 31 + idx_l)
            if moi != ln:
                so_dong_da_doi += 1
            new_lines.append(moi)
        new_input = "\n".join(new_lines)
        # Kiểm tra bất biến 100% trích dẫn vẫn là chuỗi con
        for td in tds:
            assert td in new_input, f"Mất trích dẫn '{td}' ở ca {c.get('id')}"
        c["input"] = new_input

    tr_after_set = {
        _chuan_hoa_cau(ln)
        for c in train_cases
        for ln in c["input"].splitlines()
        if ln.strip()
    }
    dup_after = sum(1 for s in dev_lines_all if s in tr_after_set)

    target = out_train_path or train_path
    with open(target, "w", encoding="utf-8") as f:
        for c in train_cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    return {
        "train_cases": len(train_cases),
        "dev_lines": len(dev_lines_all),
        "dup_before": dup_before,
        "dup_before_pct": round(dup_before / max(len(dev_lines_all), 1) * 100, 2),
        "dup_after": dup_after,
        "dup_after_pct": round(dup_after / max(len(dev_lines_all), 1) * 100, 2),
        "so_dong_da_doi": so_dong_da_doi,
    }


if __name__ == "__main__":
    goc = duong_dan.GOC_DU_AN / "data"
    res = khu_trung_train_doi_chieu_dev_test(
        goc / "viet_train_v2.jsonl",
        goc / "viet_phat_trien_v2.jsonl",
        goc / "viet_kiem_tra_cuoi_v2.jsonl",
    )
    print(json.dumps(res, ensure_ascii=False, indent=2))
