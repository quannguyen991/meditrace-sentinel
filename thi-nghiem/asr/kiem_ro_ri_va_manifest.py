# -*- coding: utf-8 -*-
"""Kiem tra ro ri giua cac tap ASR va xuat manifest co bam SHA-256.

Chay doc lap, khong can GPU. Dau vao (ngoai kho, khong commit):
  --vietmed-dir  thu muc co train/dev/test _audio.zip va _transcript.txt cua VietMed
  --vimedcss-dir thu muc co ViMedCSS-Metadata/train_set.csv va test_set.csv
  --vimedcss-test-parquet  tep parquet test (tuy chon, de bam am thanh)

Dau ra (ghi vao --ra):
  bao-cao-ro-ri.json   : cac chi so trung/ro ri giua train-dev-test
  manifest.json        : danh sach moi mau kiem thu voi ID, tap, nguon, SHA-256 am thanh va tham chieu

Khong doc tap test de chon mo hinh; script chi do thong ke.
"""
import argparse
import ast
import hashlib
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path

import pandas as pd


def chuan_hoa(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    return re.sub(r"\s+", " ", s).strip()


def doc_vietmed(thu_muc: Path):
    """-> {ten_tap: [ {id, nguoi_noi, ref, sha256} ]}"""
    out = {}
    for ten in ("train", "dev", "test"):
        dong = ast.literal_eval((thu_muc / f"{ten}_transcript.txt").read_text(encoding="utf-8"))
        ds = []
        with zipfile.ZipFile(thu_muc / f"{ten}_audio.zip") as z:
            goc = f"{ten}_audio/"
            ten_tep = {n[len(goc):] if n.startswith(goc) else n: n for n in z.namelist()}
            for d in dong:
                if d["file"] not in ten_tep:
                    continue
                am = z.read(ten_tep[d["file"]])
                ds.append({
                    "id": d["file"],
                    "nguoi_noi": d["file"].split("/")[0],  # thu muc = phien/nguoi noi (VietMed_###)
                    "ref": d["text"],
                    "sha256": hashlib.sha256(am).hexdigest(),
                })
        out[ten] = ds
    return out


def doc_vimedcss(thu_muc: Path):
    tr = pd.read_csv(thu_muc / "ViMedCSS-Metadata" / "train_set.csv")
    te = pd.read_csv(thu_muc / "test_set.csv")
    return tr, te


def bao_cao(vm, vc_tr, vc_te):
    rep = {}
    # 1) VietMed: trung nguoi noi/phien giua cac tap
    nguoi = {t: set(x["nguoi_noi"] for x in vm[t]) for t in vm}
    rep["vietmed_nguoi_noi_chung"] = {
        "train_va_test": len(nguoi["train"] & nguoi["test"]),
        "dev_va_test": len(nguoi["dev"] & nguoi["test"]),
        "train_va_dev": len(nguoi["train"] & nguoi["dev"]),
        "so_nguoi_noi_test": len(nguoi["test"]),
    }
    # 2) VietMed: trung SHA-256 am thanh va trung noi dung chuan hoa
    sha = {t: set(x["sha256"] for x in vm[t]) for t in vm}
    txt = {t: set(chuan_hoa(x["ref"]) for x in vm[t]) for t in vm}
    rep["vietmed_trung_am_thanh"] = {
        "train_va_test": len(sha["train"] & sha["test"]),
        "dev_va_test": len(sha["dev"] & sha["test"]),
    }
    rep["vietmed_trung_noi_dung"] = {
        "train_va_test": len(txt["train"] & txt["test"]),
        "dev_va_test": len(txt["dev"] & txt["test"]),
        "so_cau_test_trung_train": sum(1 for x in vm["test"] if chuan_hoa(x["ref"]) in txt["train"]),
        "so_cau_test": len(vm["test"]),
    }
    # 3) ViMedCSS: trung video goc giua train va test (ro ri cap video)
    v_tr, v_te = set(vc_tr["original_video_link"]), set(vc_te["original_video_link"])
    rep["vimedcss_trung_video"] = {
        "so_video_train": len(v_tr),
        "so_video_test": len(v_te),
        "so_video_chung": len(v_tr & v_te),
        "ty_le_dong_test_co_video_trong_train": round(float(vc_te["original_video_link"].isin(v_tr).mean()), 4),
    }
    rep["vimedcss_trung_segment_id"] = int(len(set(vc_tr["segment_id"]) & set(vc_te["segment_id"])))
    # 4) Chéo nguon: ViMedCSS va VietMed khong co chung video/cau (khong dung ViMedCSS-train de huan luyen roi bao cao tren ViMedCSS-test)
    txt_vc_tr = set(chuan_hoa(s) for s in vc_tr["segment_text"].astype(str))
    rep["vimedcss_test_trung_train_noi_dung"] = int(sum(1 for s in vc_te["segment_text"].astype(str) if chuan_hoa(s) in txt_vc_tr))
    rep["ket_luan_tap_huan_luyen_ViMedCSS"] = (
        "Khong dung ViMedCSS-train de huan luyen roi bao cao tren ViMedCSS-test: ro ri cap video."
        if rep["vimedcss_trung_video"]["ty_le_dong_test_co_video_trong_train"] > 0.05
        else "Ro ri cap video thap."
    )
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vietmed-dir", type=Path, required=True)
    ap.add_argument("--vimedcss-dir", type=Path, required=True)
    ap.add_argument("--ra", type=Path, required=True)
    a = ap.parse_args()
    a.ra.mkdir(parents=True, exist_ok=True)

    vm = doc_vietmed(a.vietmed_dir)
    vc_tr, vc_te = doc_vimedcss(a.vimedcss_dir)
    rep = bao_cao(vm, vc_tr, vc_te)
    (a.ra / "bao-cao-ro-ri.json").write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = {
        "vietmed": {t: {"so_mau": len(vm[t]), "mau": vm[t]} for t in vm},
        "vimedcss_test_so_dong": int(len(vc_te)),
        "vimedcss_train_so_dong": int(len(vc_tr)),
        "vimedcss_test_csv_sha256": hashlib.sha256((a.vimedcss_dir / "test_set.csv").read_bytes()).hexdigest(),
        "vimedcss_train_csv_sha256": hashlib.sha256((a.vimedcss_dir / "ViMedCSS-Metadata" / "train_set.csv").read_bytes()).hexdigest(),
    }
    (a.ra / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False, indent=2).encode("ascii", "backslashreplace").decode("ascii"))


if __name__ == "__main__":
    main()
