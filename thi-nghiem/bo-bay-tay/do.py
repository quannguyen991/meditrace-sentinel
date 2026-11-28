# -*- coding: utf-8 -*-
"""Chạy lớp cảnh báo MediTrace (src/canh_bao, toàn luật, không cần GPU) trên bộ ca bẫy.

Bản sạch = đáp án (khâu trích hoàn hảo). Mỗi bản sai = đáp án có đúng MỘT lỗi cố ý.
  - Báo nhầm: cảnh báo trên bản sạch.
  - Bắt đúng: có cảnh báo thuộc `nhom_dung` trên đúng dòng sai (lỗi xoá: cảnh báo bỏ sót
    toàn ca chạm lượt của dòng bị xoá).

    python thi-nghiem/bo-bay-tay/do.py [--loi-thoai ra/loi_thoai_asr.jsonl] [--ra ra/ket_qua.json]

`--loi-thoai`: thay `input` bằng bản chép âm (mỗi dòng {"id", "input"}) để xem lớp cảnh báo
chịu lỗi chép giọng nói ra sao. Mọi số chỉ trên 16 ca viết tay, KHÔNG phải độ chính xác thực tế.
"""
import argparse
import copy
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

DAY = Path(__file__).resolve().parent
GOC = DAY.parents[1]
sys.path.insert(0, str(GOC))

from src.canh_bao import gop  # noqa: E402
from src.do_luong.danh_gia_khoa import phat_bieu_tu_dap_an  # noqa: E402


def _canh_bao(kq):
    ra = [(int(i), c) for i, v in kq["theo_phat_bieu"].items() for c in v["tat_ca"]]
    return ra + [(None, c) for c in kq["toan_ca"]]


def ap_sai(ca, b):
    """-> (ca mới, id dòng bị sai hoặc None nếu xoá)."""
    moi = copy.deepcopy(ca)
    if b["cach"] == "them":
        moi["dap_an"].append(b["menh_de"])
        return moi, len(moi["dap_an"]) - 1
    if b["cach"] == "xoa":
        moi["dap_an"][b["chi_so"]]["luot"] = []  # phat_bieu_tu_dap_an bỏ dòng không lượt; giữ chỉ số
        return moi, None
    moi["dap_an"][b["chi_so"]].update(b["doi"])
    return moi, b["chi_so"]


def do_ca(ca):
    ps = phat_bieu_tu_dap_an(ca)
    kq = gop.chay(ps, ca["input"])
    sach = [{"dong": pid, "ma": c.ma, "nhom": c.nhom, "ly_do": c.ly_do} for pid, c in _canh_bao(kq)]
    ket = []
    for b in ca["ban_sai"]:
        moi, pid = ap_sai(ca, b)
        k2 = gop.chay(phat_bieu_tu_dap_an(moi), moi["input"])
        cbs = _canh_bao(k2)
        if pid is None:
            tren = [c for p, c in cbs if p is None and set(c.luot) & set(b["luot"])]
        else:
            tren = [c for p, c in cbs if p == pid]
        dung = [c for c in tren if c.nhom in b["nhom_dung"]]
        ket.append({
            "loai": b["loai"], "mo_ta": b["mo_ta"], "nhom_dung": b["nhom_dung"],
            "bat_dung": bool(dung), "bat_bat_ky": bool(tren),
            "can_xac_nhan_D": (pid is not None and k2["trang_thai_D"].get(pid, {}).get("trang_thai") == gop.CAN_XAC_NHAN),
            "canh_bao_tren_dong": [{"ma": c.ma, "nhom": c.nhom, "ly_do": c.ly_do} for c in tren],
        })
    return {"id": ca["id"], "ten": ca["ten"], "phuong_ngu": ca["phuong_ngu"], "bao_nham_sach": sach, "ban_sai": ket}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--vao", default=str(DAY / "ra" / "ca_bay.jsonl"))
    ap.add_argument("--loi-thoai", help="JSONL {id, input} thay lời thoại gốc (vd. bản chép âm)")
    ap.add_argument("--ra", default=str(DAY / "ra" / "ket_qua_luat.json"))
    a = ap.parse_args()
    ds = [json.loads(l) for l in open(a.vao, encoding="utf-8")]
    if a.loi_thoai:
        thay = {r["id"]: r["input"] for r in map(json.loads, open(a.loi_thoai, encoding="utf-8"))}
        ds = [dict(c, input=thay[c["id"]]) for c in ds if c["id"] in thay]

    theo_ca = [do_ca(c) for c in ds]
    tl = defaultdict(Counter)
    for c in theo_ca:
        for b in c["ban_sai"]:
            t = tl[b["loai"]]
            t["n"] += 1
            t["dung"] += b["bat_dung"]
            t["bat_ky"] += b["bat_bat_ky"]
    tong_n = sum(t["n"] for t in tl.values())
    tong_dung = sum(t["dung"] for t in tl.values())
    nham = sum(len(c["bao_nham_sach"]) for c in theo_ca)

    print(f"{len(theo_ca)} ca | bắt đúng {tong_dung}/{tong_n} ({tong_dung / max(tong_n, 1):.0%}) | "
          f"báo nhầm trên bản sạch {nham} ({nham / max(len(theo_ca), 1):.1f}/ca)\n")
    print(f"{'loại lỗi':<22}{'n':>4}{'đúng':>6}{'bất kỳ':>8}")
    for l, t in sorted(tl.items(), key=lambda x: x[1]["dung"] / x[1]["n"]):
        print(f"{l:<22}{t['n']:>4}{t['dung']:>6}{t['bat_ky']:>8}")
    print("\nLỌT (không có cảnh báo đúng nhóm):")
    for c in theo_ca:
        for b in c["ban_sai"]:
            if not b["bat_dung"]:
                co = ",".join(sorted({x["ma"] for x in b["canh_bao_tren_dong"]})) or "—"
                print(f"  {c['id']} [{c['phuong_ngu']}] {b['loai']}: {b['mo_ta']}  (trên dòng: {co})")

    Path(a.ra).write_text(json.dumps({
        "ghi_chu": "16 ca viết tay, bản sạch = đáp án. Không phải độ chính xác thực tế.",
        "loi_thoai": a.loi_thoai or "gốc",
        "tong": {"ban_sai": tong_n, "bat_dung": tong_dung, "bao_nham_sach": nham},
        "theo_loai": {l: dict(t) for l, t in tl.items()}, "theo_ca": theo_ca,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n-> {a.ra}")


if __name__ == "__main__":
    main()
