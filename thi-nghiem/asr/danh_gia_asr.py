# -*- coding: utf-8 -*-
"""Do PhoWhisper tren tap kiem thu (khong huan luyen) va do do tin cay ASR.

Dau vao (ngoai kho, khong commit):
  --vietmed-dir  thu muc co test_audio.zip va test_transcript.txt cua VietMed
  --vimedcss     tep parquet test cua ViMedCSS (co cot audio, segment_text, cs_terms_list)

Dau ra: JSON tong hop gom WER, ty le thuat ngu tieng Anh duoc nhan dung, va AUROC cua
do tin cay (exp(trung binh log-xac-suat token)) trong viec du doan cau bi sai.

Do tin cay o day la xac suat cua token duoc chon, khong phai entropy Shannon tren toan
bo tu vung. Phan entropy day du can sua ma de luu phan phoi, chua lam.
"""
import argparse
import ast
import io
import json
import math
import re
import zipfile
from pathlib import Path

import jiwer
import numpy as np
import pyarrow.parquet as pq
import soundfile as sf
import torch
from scipy.signal import resample_poly
from sklearn.metrics import roc_auc_score
from transformers import WhisperForConditionalGeneration, WhisperProcessor

MODEL = "vinai/PhoWhisper-medium"
REVISION = "55a7e3eb6c906de891f8f06a107754427dd3be79"  # ghim theo phowhisper_provider.py
TAN_SO = 16000


def chuan_hoa(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^\w\s]", " ", s, flags=re.UNICODE)
    return re.sub(r"\s+", " ", s).strip()


def doc_am_thanh(data: bytes) -> np.ndarray:
    x, sr = sf.read(io.BytesIO(data), dtype="float32", always_2d=False)
    if x.ndim > 1:
        x = x.mean(axis=1)
    if sr != TAN_SO:
        x = resample_poly(x, TAN_SO, sr).astype("float32")
    return x


def nap_mo_hinh(thiet_bi: str, mo_hinh_id: str = MODEL, revision=REVISION):
    proc = WhisperProcessor.from_pretrained(mo_hinh_id, revision=revision)
    mo_hinh = WhisperForConditionalGeneration.from_pretrained(
        mo_hinh_id, revision=revision, dtype=torch.float16 if thiet_bi == "cuda" else torch.float32
    ).to(thiet_bi).eval()
    return proc, mo_hinh


@torch.no_grad()
def nhan_dang(proc, mo_hinh, thiet_bi, mang_am: np.ndarray, beam: int = 1):
    """-> (van ban, do tin cay). Do tin cay = exp(trung binh log-xac-suat cua token duoc chon).

    beam > 1: lay diem sequences_scores cua chuoi tot nhat (da chuan hoa theo do dai, length_penalty=1.0),
    exp(diem) tuong duong exp(trung binh log-xac-suat) nhu nhanh greedy.
    """
    dau_vao = proc(mang_am, sampling_rate=TAN_SO, return_tensors="pt")
    feats = dau_vao.input_features.to(thiet_bi, dtype=mo_hinh.dtype)
    if beam > 1:
        sinh = mo_hinh.generate(
            feats, language="vi", task="transcribe", num_beams=beam, length_penalty=1.0,
            return_dict_in_generate=True, output_scores=True,
        )
        van_ban = proc.batch_decode(sinh.sequences, skip_special_tokens=True)[0].strip()
        return van_ban, float(math.exp(sinh.sequences_scores[0].item()))
    sinh = mo_hinh.generate(
        feats, language="vi", task="transcribe", return_dict_in_generate=True, output_scores=True
    )
    chuoi = sinh.sequences
    diem = torch.stack(sinh.scores, dim=1).float()          # (batch, buoc, vocab)
    log_xs = torch.log_softmax(diem, dim=-1)
    ids = chuoi[:, -diem.shape[1]:]
    lp = log_xs.gather(-1, ids.unsqueeze(-1)).squeeze(-1)  # (batch, buoc)
    ma_hop_le = ids != proc.tokenizer.pad_token_id
    trung_binh = (lp * ma_hop_le).sum(1) / ma_hop_le.sum(1).clamp(min=1)
    van_ban = proc.batch_decode(chuoi, skip_special_tokens=True)[0].strip()
    return van_ban, float(math.exp(trung_binh.item()))


def tap_vietmed(thu_muc: Path):
    # Khop theo duong dan day du (speaker/ten.ogg). Chi lay ten tep se ghi de nhau:
    # nhieu nguoi noi cung co ten kieu 17.0000_24.0000.ogg.
    with zipfile.ZipFile(thu_muc / "test_audio.zip") as z:
        goc = "test_audio/"
        ten_tep = {}
        for n in z.namelist():
            if n.lower().endswith((".ogg", ".wav", ".flac", ".mp3")):
                ten_tep[n[len(goc):] if n.startswith(goc) else n] = n
        dong = ast.literal_eval((thu_muc / "test_transcript.txt").read_text(encoding="utf-8"))
        for d in dong:
            if d["file"] not in ten_tep:
                continue
            yield {"id": d["file"], "ref": d["text"], "audio": z.read(ten_tep[d["file"]])}


def tap_vimedcss(duong_dan: Path):
    bang = pq.read_table(duong_dan, columns=["segment_id", "audio", "segment_text", "cs_terms_list"]).to_pylist()
    for r in bang:
        yield {
            "id": r["segment_id"],
            "ref": r["segment_text"],
            "audio": r["audio"]["bytes"],
            "cs_terms": [t.strip() for t in re.split(r"[;,|]", r["cs_terms_list"] or "") if t.strip()],
        }


def la_lap(van_ban: str, nguong: float = 2.4) -> bool:
    """Phat hien lap vo han: ti le nen gzip cao (van ban lap lai rat nhieu lan)."""
    import zlib
    b = van_ban.encode("utf-8")
    if len(b) < 40:
        return False
    return len(b) / max(1, len(zlib.compress(b))) > nguong


def danh_gia(ten_tap, mau, proc, mo_hinh, thiet_bi, gioi_han=None, beam=1):
    tham_chieu, gia_thuyet, tin_cay, sai = [], [], [], []
    kq_chi_tiet = []
    dem = 0
    for m in mau:
        if gioi_han and dem >= gioi_han:
            break
        try:
            x = doc_am_thanh(m["audio"])
        except Exception as e:  # tep am thanh loi: ghi lai, khong bo qua im lang
            kq_chi_tiet.append({"id": m["id"], "loi": str(e)})
            continue
        hyp, conf = nhan_dang(proc, mo_hinh, thiet_bi, x, beam)
        ref_n, hyp_n = chuan_hoa(m["ref"]), chuan_hoa(hyp)
        if not ref_n:
            continue
        wer_cau = jiwer.wer(ref_n, hyp_n) if hyp_n else 1.0
        tham_chieu.append(ref_n)
        gia_thuyet.append(hyp_n if hyp_n else "_")
        tin_cay.append(conf)
        sai.append(int(wer_cau > 0))
        rec = None
        if m.get("cs_terms"):
            terms = [chuan_hoa(t) for t in m["cs_terms"] if chuan_hoa(t)]
            if terms:
                rec = sum(1 for t in terms if f" {t} " in f" {hyp_n} ") / len(terms)
        kq_chi_tiet.append({"id": m["id"], "ref": ref_n, "hyp": hyp_n, "conf": round(conf, 4),
                            "wer": round(wer_cau, 4), "cs_recall": None if rec is None else round(rec, 4),
                            "lap": la_lap(hyp)})
        dem += 1
    tong = {"tap": ten_tap, "so_cau": len(tham_chieu)}
    if tham_chieu:
        tong["wer"] = round(jiwer.wer(tham_chieu, gia_thuyet), 4)
        recs = [k["cs_recall"] for k in kq_chi_tiet if k.get("cs_recall") is not None]
        tong["cs_recall_trung_binh"] = round(float(np.mean(recs)), 4) if recs else None
        # So cau bi lap vo han: loi nghiem trong vi ca cau bi mat noi dung that.
        tong["so_cau_lap_vo_han"] = int(sum(1 for k in kq_chi_tiet if k.get("lap")))
        # Nhan "cau sai dang ke" theo nguong WER. Ngưỡng 0 vô nghĩa vì gần như mọi câu nói tự nhiên đều có lỗi.
        tong["auroc_tin_cay_du_doan_cau_sai"] = {}
        wers = [k["wer"] for k in kq_chi_tiet if "wer" in k]
        for nguong in (0.2, 0.5):
            nhan = [int(w >= nguong) for w in wers]
            if 0 < sum(nhan) < len(nhan):
                tong["auroc_tin_cay_du_doan_cau_sai"][f"wer>={nguong}"] = round(
                    roc_auc_score(nhan, [-c for c in tin_cay]), 4)
                tong.setdefault("so_cau_sai", {})[f"wer>={nguong}"] = int(sum(nhan))
            else:
                tong["auroc_tin_cay_du_doan_cau_sai"][f"wer>={nguong}"] = None
    return tong, kq_chi_tiet


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vietmed-dir", type=Path, required=True)
    ap.add_argument("--vimedcss", type=Path, required=True)
    ap.add_argument("--ra", type=Path, required=True)
    ap.add_argument("--gioi-han", type=int, default=None, help="so cau toi da moi tap (de chay thu)")
    ap.add_argument("--mo-hinh", default=MODEL, help="ma Hugging Face hoac thu muc mo hinh da tinh chinh")
    ap.add_argument("--revision", default=REVISION, help="ghim phien ban; de rong voi thu muc cuc bo")
    ap.add_argument("--beam", type=int, default=1, help="so tia beam search; 1 = greedy")
    ap.add_argument("--chi-vimedcss", action="store_true", help="chi chay tap ViMedCSS")
    a = ap.parse_args()

    thiet_bi = "cuda" if torch.cuda.is_available() else "cpu"
    rev = None if (a.revision or "").strip().lower() in ("", "none") else a.revision
    proc, mo_hinh = nap_mo_hinh(thiet_bi, a.mo_hinh, rev)
    a.ra.mkdir(parents=True, exist_ok=True)

    ket = {"mo_hinh": a.mo_hinh, "revision": rev, "thiet_bi": thiet_bi, "beam": a.beam, "gioi_han": a.gioi_han, "ket_qua": []}
    cac_tap = [("VietMed-test", tap_vietmed(a.vietmed_dir)), ("ViMedCSS-test-shard0", tap_vimedcss(a.vimedcss))]
    if a.chi_vimedcss:
        cac_tap = cac_tap[1:]
    for ten, nguon in cac_tap:
        tong, chi_tiet = danh_gia(ten, nguon, proc, mo_hinh, thiet_bi, a.gioi_han, a.beam)
        ket["ket_qua"].append(tong)
        (a.ra / f"{ten}.chi-tiet.json").write_text(json.dumps(chi_tiet, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(tong, ensure_ascii=False))
    (a.ra / "tong-hop.json").write_text(json.dumps(ket, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
