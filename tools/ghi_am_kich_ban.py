# -*- coding: utf-8 -*-
"""In kịch bản để nhóm ĐỌC TO và ghi âm (kịch bản v2, việc V6: số đo từ âm thanh đến bản nháp).

    python -m tools.ghi_am_kich_ban --vao data/viet_phat_trien_v2.jsonl --so-ca 20 --ra data/thu-giong
    # → kich_ban_01_<id>.md … + danh_sach.json (tên tệp ghi âm cần đặt ↔ mã ca)

Mỗi kịch bản ghi rõ vai (Bác sĩ / Bệnh nhân / Người nhà) và số lượt. Người đọc phải đồng ý bằng văn bản
cho dùng giọng; không nói tên thật hay thông tin cá nhân của mình. Không dùng tập kiểm tra niêm phong.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

LOI_DAN = (
    "> Trước khi ghi: mọi người đọc đã **đồng ý bằng văn bản** cho dùng giọng nói để đo phần mềm. "
    "Chỉ đọc đúng lời trong kịch bản, **không nói tên thật** hay thông tin cá nhân của mình. "
    "Mỗi người một vai, đọc tự nhiên như đang khám; được phép ngắt, nói chen như thật. "
    "Ghi bằng micro laptop trong phòng bình thường, lưu tệp `.wav` hoặc `.m4a` đúng tên ghi ở cuối."
)


def tao_kich_ban(ca: dict) -> dict:
    luot = [d.strip() for d in (ca.get("input") or "").split("\n") if d.strip()]
    vai: list[str] = []
    for d in luot:
        v = d.split(":", 1)[0].strip()
        if v and v not in vai:
            vai.append(v)
    than = "\n\n".join(f"[{i}] {d}" for i, d in enumerate(luot, 1))
    van = f"# Kịch bản ca {ca['id']}\n\n{LOI_DAN}\n\n**Vai cần người đọc:** {', '.join(vai)}\n\n{than}\n"
    return {"id": ca["id"], "vai": vai, "so_luot": len(luot), "van": van}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vao", required=True)
    ap.add_argument("--so-ca", type=int, default=20)
    ap.add_argument("--seed", type=int, default=2811)
    ap.add_argument("--ra", default="data/thu-giong")
    a = ap.parse_args(argv)
    if "viet_kiem_tra_cuoi" in a.vao:
        print("Không dùng tập kiểm tra niêm phong.", file=sys.stderr)
        return 2
    ca = [json.loads(d) for d in Path(a.vao).read_text(encoding="utf-8").splitlines() if d.strip()]
    nhieu_vai = [c for c in ca if len(tao_kich_ban(c)["vai"]) >= 3] or ca
    chon = random.Random(a.seed).sample(nhieu_vai, min(a.so_ca, len(nhieu_vai)))
    ra = Path(a.ra)
    ra.mkdir(parents=True, exist_ok=True)
    ds = []
    for i, c in enumerate(chon, 1):
        kb = tao_kich_ban(c)
        ten = f"kich_ban_{i:02d}_{c['id']}"
        (ra / f"{ten}.md").write_text(kb["van"] + f"\n---\nLưu ghi âm thành: `{ten}.wav`\n", encoding="utf-8")
        ds.append({"tep_ghi_am": f"{ten}.wav", "ma_ca": c["id"], "vai": kb["vai"], "so_luot": kb["so_luot"]})
    (ra / "danh_sach.json").write_text(json.dumps(ds, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đã ghi {len(ds)} kịch bản vào {ra}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
