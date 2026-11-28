# -*- coding: utf-8 -*-
"""Đổi ca_bay.py thành JSONL cùng định dạng data/thach_thuc_v2, kiểm trích dẫn có thật.

    python thi-nghiem/bo-bay-tay/sinh.py
Ra: thi-nghiem/bo-bay-tay/ra/ca_bay.jsonl
"""
import copy
import json
import sys
from pathlib import Path

DAY = Path(__file__).resolve().parent
sys.path.insert(0, str(DAY))
import ca_bay  # noqa: E402

RA = DAY / "ra"


def _giai(dap_an_tho, luot_so):
    """Đổi khoá mệnh đề và nhãn lượt thành chỉ số; bỏ trường 'k'."""
    chi_so = {d["k"]: i for i, d in enumerate(dap_an_tho)}
    ra = []
    for d in dap_an_tho:
        d = copy.deepcopy(d)
        d["luot"] = [luot_so[x] for x in d["luot"]]
        if d.get("quan_he_voi") is not None:
            d["quan_he_voi"] = chi_so[d["quan_he_voi"]]
        d.pop("k")
        ra.append(d)
    return ra, chi_so


def kiem_trich(ca_id, d, dong):
    for t in d["trich_dan"]:
        if not any(t in dong[l - 1] for l in d["luot"]):
            raise SystemExit(f"{ca_id}: trích dẫn không nằm trong lượt {d['luot']}: {t!r}")


def sinh():
    ds = []
    for c in ca_bay.CA:
        luot_so = {tag: i for i, (tag, _, _) in enumerate(c["luot"], 1)}
        dong = [f"{ca_bay.VAI[v]}: {t}" for _, v, t in c["luot"]]
        dap_an, chi_so = _giai(c["dap_an"], luot_so)
        for d in dap_an:
            kiem_trich(c["id"], d, dong)
        ban_sai = []
        for s in c["ban_sai"]:
            doi = dict(s["doi"])
            moi = doi.pop("moi", None)
            xoa = doi.pop("xoa", False)
            b = {"loai": s["loai"], "mo_ta": s["mo_ta"], "nhom_dung": sorted(ca_bay.NHOM[s["loai"]])}
            if moi is not None:  # thêm mệnh đề bịa
                (md,), _ = _giai([moi], luot_so)
                b.update(cach="them", menh_de=md)
            elif xoa:
                b.update(cach="xoa", chi_so=chi_so[s["k"]], luot=dap_an[chi_so[s["k"]]]["luot"])
            else:
                if "luot" in doi:
                    doi["luot"] = [luot_so[x] for x in doi["luot"]]
                b.update(cach="sua", chi_so=chi_so[s["k"]], doi=doi)
            ban_sai.append(b)
        ds.append({
            "id": c["id"], "ten": c["ten"], "input": "\n".join(dong), "bay": c["bay"],
            "so_luot": len(dong), "nguoi_ke": c["nguoi_ke"], "phuong_ngu": c.get("phuong_ngu", "bac"),
            "vai_theo_luot": [v for _, v, _ in c["luot"]],
            "nguon": "Claude viết tay theo yêu cầu tác giả 28/11/2026 — chỉ để đo, không huấn luyện, chưa có bác sĩ duyệt",
            "dap_an": dap_an, "ban_sai": ban_sai,
        })
    RA.mkdir(exist_ok=True)
    with open(RA / "ca_bay.jsonl", "w", encoding="utf-8") as f:
        for ca in ds:
            f.write(json.dumps(ca, ensure_ascii=False) + "\n")
    print(f"{len(ds)} ca, {sum(len(c['dap_an']) for c in ds)} mệnh đề, "
          f"{sum(len(c['ban_sai']) for c in ds)} bản sai -> {RA / 'ca_bay.jsonl'}")
    return ds


if __name__ == "__main__":
    sinh()
