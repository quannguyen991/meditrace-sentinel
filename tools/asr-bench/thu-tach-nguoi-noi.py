"""Do tach nguoi noi tren hoi thoai TONG HOP nhieu giong may doc.

AM THANH LA GIONG MAY (Piper), KHONG PHAI GIONG NGUOI. Moi vai trong mot hoi thoai do mot
giong may khac nhau doc, cac luot khong chen nhau. Ket qua o day chi cho biet may tach co
phan biet duoc nhung giong may nay khong; KHONG cho biet may tach lam duoc gi voi ban ghi
that trong phong kham (giong gan nhau, noi chen, on nen, micro xa).

Loi thoai lay tu TAP PHAT TRIEN (thach_thuc_doi_chu_the_phat_trien: nhieu nguoi nha noi thay;
thach_thuc_dinh_chinh_phat_trien: tu dinh chinh). KHONG mo tap kiem tra cuoi.

Ba dieu kien, cung loi thoai va cung giong:
  cach_quang   khoang lang giua hai luot 0,4-1,0 s, sach
  sat_nhau     khoang lang 0,05-0,3 s, sach  (may chep loi cat doan o khoang lang > 0,8 s,
               nen hai nguoi noi sat nhau thi lot vao cung mot doan)
  sat_nhau_on  nhu sat_nhau, them on trang SNR 15 dB

Buoc:
  dung   sinh WAV + nhan chuan (ai noi tu giay nao den giay nao) -> data/audio-bench/hoi-thoai/
  do     chay bo tach (mot_nguoi | pyannote) tren tung tep, tinh:
           - DER theo khung 10 ms, KHONG co vung dem quanh ranh gioi luot:
             (bo sot + bao nham + nham nguoi) / tong thoi luong co nguoi noi
           - ti le luot gan dung nguoi noi: nhan may duoc ghep voi vai chuan theo cach trung
             thoi luong nhieu nhat (moi nhan may mot vai); luot dung neu nhan chiem nhieu thoi
             luong nhat trong luot, sau khi ghep, dung vai chuan
           - so nguoi noi may dem ra co bang so vai that khong
         --co-asr: chay ca duong ong (PhoWhisper + ghep + gop luot) roi tinh tren cac DONG ma
           nguoi dung se thay:
           - so dong / so luot that (va / so luot that sau khi gop luot lien tiep cung vai)
           - ti le dong lan loi cua hai vai tro len (moi vai trung >= 0,3 s voi dong do)
           - ti le dong gan dung nguoi noi

Chay (moi truong cua dich vu):
  D:/meditrace-venv-lap/Scripts/python tools/asr-bench/thu-tach-nguoi-noi.py dung
  D:/meditrace-venv-lap/Scripts/python tools/asr-bench/thu-tach-nguoi-noi.py do --bo-tach mot_nguoi --co-asr
  D:/meditrace-venv-lap/Scripts/python tools/asr-bench/thu-tach-nguoi-noi.py do --bo-tach pyannote --co-asr \
      --pyannote-python D:/pyannote-venv/Scripts/python.exe [--pyannote-khoa D:/Claude/.secrets/huggingface.key]
Ra: docs/ket-qua/tach-nguoi-noi-<bo tach>[-asr].json va docs/ket-qua/tach-nguoi-noi.md (bang gop)
"""
import argparse
import importlib.util
import itertools
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC))

_spec = importlib.util.spec_from_file_location("tao_am", Path(__file__).with_name("tao-am-thanh-thu.py"))
tao_am = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tao_am)

SR = tao_am.SR
RA_AM = GOC / "data" / "audio-bench" / "hoi-thoai"
RA_KQ = GOC / "docs" / "ket-qua"
NGUON = ("thach_thuc_doi_chu_the_phat_trien", "thach_thuc_dinh_chinh_phat_trien")
SO_CA_MOI_BO = 12
GIONG = ("vais1000", "25hours", "vivos_a", "vivos_b")
DIEU_KIEN = {"cach_quang": (0.4, 1.0, None), "sat_nhau": (0.05, 0.3, None), "sat_nhau_on": (0.05, 0.3, 15.0)}
KHUNG = 0.01
VAI_RE = re.compile(r"^\s*([^:]{2,20}):\s*(.+)$")


# ------------------------------------------------------------------ dung
def _chon_ca():
    ra = []
    for bo in NGUON:
        ds = [json.loads(x) for x in open(GOC / "data" / f"{bo}.jsonl", encoding="utf-8") if x.strip()]
        # lay deu tren ca bo (khong lay 12 ca dau) de co nhieu khuon khac nhau
        buoc = max(1, len(ds) // SO_CA_MOI_BO)
        ra += [(bo, d) for d in ds[::buoc][:SO_CA_MOI_BO]]
    return ra


def dung():
    muc = json.loads((GOC / "docs" / "audio-bench" / "muc-thu.json").read_text(encoding="utf-8"))
    phat_am = muc["phat_am_thuoc"]
    RA_AM.mkdir(parents=True, exist_ok=True)
    may = tao_am.May()
    danh_sach = []
    for i, (bo, ca) in enumerate(_chon_ca()):
        luot = []
        for dong in ca["input"].split("\n"):
            m = VAI_RE.match(dong)
            if m:
                luot.append((m.group(1).strip(), m.group(2).strip()))
        vai_thu_tu = list(dict.fromkeys(v for v, _ in luot))
        # xoay vong giong theo so thu tu ca: khong de mot giong luon la bac si
        giong_cua = {v: GIONG[(i + k) % len(GIONG)] for k, v in enumerate(vai_thu_tu)}
        if len(vai_thu_tu) > len(GIONG):
            print(f"bo qua {ca['id']}: {len(vai_thu_tu)} vai, chi co {len(GIONG)} giong")
            continue
        am_luot = []
        for vai, chu in luot:
            doc = chu
            for ten, am in phat_am.items():
                doc = re.sub(rf"\b{ten}\b", am, doc, flags=re.I)
            x = may.doc(giong_cua[vai], doc)
            am_luot.append(0.7 * x / (np.abs(x).max() + 1e-9))
        for dk, (k0, k1, snr) in DIEU_KIEN.items():
            # sat_nhau va sat_nhau_on cung hat giong -> cung khoang lang, chi khac on
            rng = np.random.default_rng(1000 * i + int(k0 * 100))
            phan, nhan, t = [np.zeros(int(0.5 * SR), dtype="float32")], [], 0.5
            for (vai, chu), x in zip(luot, am_luot):
                nhan.append({"vai": vai, "giong": giong_cua[vai], "bat_dau": round(t, 3),
                             "ket_thuc": round(t + len(x) / SR, 3), "chu": chu})
                t += len(x) / SR
                khe = float(rng.uniform(k0, k1))
                phan += [x.astype("float32"), np.zeros(int(khe * SR), dtype="float32")]
                t += int(khe * SR) / SR
            y = np.concatenate(phan)
            if snr is not None:
                on = rng.normal(0, 1, len(y)).astype("float32")
                noi = np.concatenate([np.asarray(a) for a in am_luot])
                on *= np.sqrt(np.mean(noi ** 2) / (10 ** (snr / 10)) / np.mean(on ** 2))
                y = y + on
            ten = f"{ca['id']}__{dk}"
            tao_am.ghi_wav(RA_AM / f"{ten}.wav", y)
            ref = {"id": ten, "ca": ca["id"], "bo": bo, "dieu_kien": dk, "giay": round(len(y) / SR, 2),
                   "so_vai": len(vai_thu_tu), "giong_cua": giong_cua, "luot": nhan}
            (RA_AM / f"{ten}.json").write_text(json.dumps(ref, ensure_ascii=False, indent=1), encoding="utf-8")
            danh_sach.append(ten)
        print(ca["id"], len(luot), "luot", giong_cua, flush=True)
    (RA_AM / "danh-sach.json").write_text(json.dumps({"giong": {g: tao_am.GIONG[g] for g in GIONG},
                                                      "dieu_kien": DIEU_KIEN, "tep": danh_sach},
                                                     ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"xong: {len(danh_sach)} tep trong {RA_AM}")


# ------------------------------------------------------------------ do
def _khung(t):
    return int(round(t / KHUNG))


def _ghep_nhan(ref, hyp):
    """-> {nhan may: vai} cho tong thoi luong trung lon nhat (moi nhan may mot vai, moi vai mot nhan)."""
    vai = sorted({l["vai"] for l in ref["luot"]})
    nhan = sorted({d["speaker_id"] for d in hyp})
    trung = {}
    for d in hyp:
        for l in ref["luot"]:
            ov = min(d["end"], l["ket_thuc"]) - max(d["start"], l["bat_dau"])
            if ov > 0:
                trung[(d["speaker_id"], l["vai"])] = trung.get((d["speaker_id"], l["vai"]), 0.0) + ov
    tot, tot_diem = {}, -1.0
    if len(nhan) <= 7:
        for chon in itertools.permutations(vai + [None] * max(0, len(nhan) - len(vai)), len(nhan)):
            diem = sum(trung.get((n, v), 0.0) for n, v in zip(nhan, chon) if v)
            if diem > tot_diem:
                tot, tot_diem = dict(zip(nhan, chon)), diem
    else:  # qua nhieu nhan: ghep tham lam
        con = set(vai)
        for (n, v), _ in sorted(trung.items(), key=lambda x: -x[1]):
            if n not in tot and v in con:
                tot[n] = v
                con.discard(v)
    return {n: v for n, v in tot.items() if v}


def do_tach(ref, hyp):
    ghep = _ghep_nhan(ref, hyp)
    n = _khung(ref["giay"]) + 1
    chuan = np.full(n, -1, dtype=int)
    vai = sorted({l["vai"] for l in ref["luot"]})
    for l in ref["luot"]:
        chuan[_khung(l["bat_dau"]):_khung(l["ket_thuc"])] = vai.index(l["vai"])
    may = [set() for _ in range(n)]
    for d in hyp:
        v = ghep.get(d["speaker_id"])
        ma = vai.index(v) if v else 100 + sorted({x["speaker_id"] for x in hyp}).index(d["speaker_id"])
        for k in range(max(0, _khung(d["start"])), min(n, _khung(d["end"]))):
            may[k].add(ma)
    sot = bao_nham = nham = 0
    for k in range(n):
        r, h = chuan[k], may[k]
        if r < 0:
            bao_nham += len(h)
        elif not h:
            sot += 1
        else:
            nham += 0 if r in h else 1
            bao_nham += len(h) - 1
    co_noi = int((chuan >= 0).sum())
    luot_dung = 0
    for l in ref["luot"]:
        dem = {}
        for k in range(_khung(l["bat_dau"]), _khung(l["ket_thuc"])):
            for h in may[k]:
                dem[h] = dem.get(h, 0) + 1
        if dem and max(dem, key=dem.get) == vai.index(l["vai"]):
            luot_dung += 1
    so_nhan = len({d["speaker_id"] for d in hyp})
    return {"der": (sot + bao_nham + nham) / co_noi, "bo_sot": sot / co_noi, "bao_nham": bao_nham / co_noi,
            "nham_nguoi": nham / co_noi, "luot": len(ref["luot"]), "luot_dung": luot_dung,
            "so_nguoi_may": so_nhan, "so_vai": ref["so_vai"], "ghep": ghep}


def do_dong(ref, doan, ghep):
    """Tren cac dong nguoi dung se thay (sau ghep + gop luot).

    giay_dung_nguoi: tong thoi luong loi noi (theo nhan chuan) nam trong mot dong mang dung nguoi
    noi (sau khi ghep nhan may voi vai). Chia cho giay_noi ra ti le. Mot dong duy nhat cho ca
    cuoc kham thi chi phan cua nguoi noi nhieu nhat duoc tinh la dung.
    """
    lan = dung = 0
    giay_dung = 0.0
    for s in doan:
        trung = {}
        for l in ref["luot"]:
            ov = min(s["end_time"], l["ket_thuc"]) - max(s["start_time"], l["bat_dau"])
            if ov > 0:
                trung[l["vai"]] = trung.get(l["vai"], 0.0) + ov
        if sum(1 for v in trung.values() if v >= 0.3) >= 2:
            lan += 1
        if trung and ghep.get(s["speaker_id"]) == max(trung, key=trung.get):
            dung += 1
        giay_dung += trung.get(ghep.get(s["speaker_id"]), 0.0)
    gop = sum(1 for i, l in enumerate(ref["luot"]) if i == 0 or l["vai"] != ref["luot"][i - 1]["vai"])
    return {"so_dong": len(doan), "luot_that": len(ref["luot"]), "luot_that_sau_gop": gop,
            "dong_lan": lan, "dong_dung_nguoi": dung, "giay_dung_nguoi": round(giay_dung, 3),
            "giay_noi": round(sum(l["ket_thuc"] - l["bat_dau"] for l in ref["luot"]), 3),
            "dong": [{"bat_dau": round(s["start_time"], 2), "ket_thuc": round(s["end_time"], 2),
                      "nguoi_noi": s["speaker_id"]} for s in doan]}


def _bo_tach(a):
    from src.audio.providers import EnergyVADProvider, SingleSpeakerDiarizationProvider
    if a.bo_tach == "mot_nguoi":
        return SingleSpeakerDiarizationProvider()
    from src.audio.pyannote_provider import PyannoteDiarizationProvider
    return PyannoteDiarizationProvider(a.pyannote_python, token_file=a.pyannote_khoa,
                                       device=a.pyannote_thiet_bi, hf_home=a.pyannote_hf_home,
                                       timeout_s=1800)


def do(a):
    from src.audio.config import AudioSettings
    from src.audio.pipeline import AudioPipeline
    from src.audio.providers import EnergyVADProvider
    from src.audio.storage import SessionStore

    ds = json.loads((RA_AM / "danh-sach.json").read_text(encoding="utf-8"))["tep"]
    if a.gioi_han:
        ds = ds[: a.gioi_han]
    if a.cach_ghep == "cu":
        # Tai tao dung cach ghep truoc 25/09: gan nguoi noi theo ca khoang thoi gian uoc luong
        # cua tu (khong gioi han 0,3 s dau), khong bao gio cat dong theo khoang lang.
        from src.audio import alignment
        alignment.DO_DAI_GAN = 1e9
        alignment.KHE_CAT_DOAN = 1e9
    tach = _bo_tach(a)
    vad = EnergyVADProvider()
    ket_qua = []
    with tempfile.TemporaryDirectory() as tmp:
        store = SessionStore(Path(tmp))
        pipe = AudioPipeline(store, diarization=tach, settings=AudioSettings()) if a.co_asr else None
        for ten in ds:
            ref = json.loads((RA_AM / f"{ten}.json").read_text(encoding="utf-8"))
            wav = RA_AM / f"{ten}.wav"
            t0 = time.time()
            if pipe:
                phien = store.create()["session_id"]
                pipe.upload(phien, wav.read_bytes(), "raw.wav")
                pipe.process(phien)
                hyp = json.loads(store.path(phien, "diarization.json").read_text(encoding="utf-8"))
                doan = pipe.transcript(phien)
                info = store.load(phien).get("tach_nguoi_noi") or {}
            else:
                tam = Path(tmp) / ten
                tam.mkdir()
                (tam / "processed.wav").write_bytes(wav.read_bytes())
                hyp = tach.diarize(tam / "processed.wav", vad.detect(tam / "processed.wav"))
                doan, info = None, dict(getattr(tach, "last_info", {}) or {})
            if info.get("loi"):
                raise SystemExit(f"{ten}: bo tach loi {info['loi']} — dung lai, khong ghi ket qua lui ve")
            r = {"tep": ten, "dieu_kien": ref["dieu_kien"], "bo": ref["bo"], "giay_am": ref["giay"],
                 "giay_xu_ly": round(time.time() - t0, 2), "ram_dinh_mb": info.get("ram_dinh_mb"),
                 **do_tach(ref, hyp)}
            if doan is not None:
                r.update(do_dong(ref, doan, r["ghep"]))
            ket_qua.append(r)
            print(f"{ten}: DER {r['der']:.3f} luot dung {r['luot_dung']}/{r['luot']} "
                  f"nguoi {r['so_nguoi_may']}/{r['so_vai']}"
                  + (f" dong {r['so_dong']} lan {r['dong_lan']}" if doan is not None else "")
                  + f" ({r['giay_xu_ly']}s)", flush=True)
    tong = tong_hop(ket_qua)
    duoi = f"{a.bo_tach}{'-asr' if a.co_asr else ''}{'-' + a.nhan if a.nhan else ''}"
    ra = {"bo_tach": a.bo_tach, "co_asr": a.co_asr, "cach_ghep": a.cach_ghep,
          "nhan": a.nhan, "tieu_de": a.tieu_de, "mo_ta": a.mo_ta,
          "thiet_bi": getattr(tach, "device", None),
          "ghi_chu": "Giong may doc (Piper), khong phai giong nguoi; loi thoai tap phat trien.",
          "tong_hop": tong, "tung_tep": ket_qua}
    RA_KQ.mkdir(parents=True, exist_ok=True)
    (RA_KQ / f"tach-nguoi-noi-{duoi}.json").write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(tong, ensure_ascii=False, indent=1))
    viet_bang()


def tong_hop(kq):
    ra = {}
    for dk in ["tat_ca"] + list(DIEU_KIEN):
        xs = [r for r in kq if dk == "tat_ca" or r["dieu_kien"] == dk]
        if not xs:
            continue
        am = sum(r["giay_am"] for r in xs)
        d = {"so_tep": len(xs), "giay_am": round(am, 1),
             "der_tb_theo_thoi_luong": round(sum(r["der"] * r["giay_am"] for r in xs) / am, 4),
             "luot_dung": sum(r["luot_dung"] for r in xs), "luot": sum(r["luot"] for r in xs),
             "dem_dung_so_nguoi": sum(r["so_nguoi_may"] == r["so_vai"] for r in xs),
             "giay_xu_ly": round(sum(r["giay_xu_ly"] for r in xs), 1)}
        d["ti_le_luot_dung"] = round(d["luot_dung"] / d["luot"], 4)
        rams = [r["ram_dinh_mb"] for r in xs if r.get("ram_dinh_mb")]
        if rams:
            d["ram_dinh_mb_lon_nhat"] = max(rams)
        if "so_dong" in xs[0]:
            for k in ("so_dong", "luot_that", "luot_that_sau_gop", "dong_lan", "dong_dung_nguoi",
                      "giay_dung_nguoi", "giay_noi"):
                d[k] = round(sum(r[k] for r in xs), 3)
            d["ti_le_dong_lan"] = round(d["dong_lan"] / d["so_dong"], 4)
            d["ti_le_dong_dung_nguoi"] = round(d["dong_dung_nguoi"] / d["so_dong"], 4)
            d["ti_le_thoi_luong_dung_nguoi"] = round(d["giay_dung_nguoi"] / d["giay_noi"], 4)
        ra[dk] = d
    return ra


def _pt(x):
    return f"{100 * x:.1f} %".replace(".", ",")


def viet_bang():
    """Gop moi tep ket qua da co thanh mot bang Markdown."""
    tep = sorted(RA_KQ.glob("tach-nguoi-noi-*.json"))
    if not tep:
        return
    dong = ["# Đo tách người nói trên hội thoại tổng hợp", "",
            "Âm thanh do máy đọc (Piper), mỗi vai một giọng máy khác nhau, các lượt không nói chen "
            "nhau. Lời thoại lấy từ tập phát triển (bộ đổi chủ thể và bộ tự đính chính). Kết quả "
            "chỉ cho biết máy tách có phân biệt được các giọng máy này không; **không** cho biết "
            "máy tách làm được gì với bản ghi thật trong phòng khám.", "",
            "Cách tính: DER tính theo khung 10 ms, không có vùng đệm quanh ranh giới lượt. "
            "Lượt đúng người nói: nhãn máy được ghép với vai chuẩn theo cách trùng thời lượng nhiều "
            "nhất, rồi xem nhãn chiếm nhiều thời lượng nhất trong lượt có đúng vai không. Dòng lẫn "
            "hai người: dòng mà hai vai trở lên mỗi vai trùng ít nhất 0,3 s.", "",
            "Tạo lại: `python tools/asr-bench/thu-tach-nguoi-noi.py dung`, rồi `do` (xem đầu tệp).", ""]
    for p in tep:
        d = json.loads(p.read_text(encoding="utf-8"))
        dong += [f"## {d['bo_tach']}{' + chép lời (PhoWhisper)' if d['co_asr'] else ''}"
                 f"{' — ' + d['tieu_de'] if d.get('tieu_de') else ''}", ""]
        if d.get("mo_ta"):
            dong += [d["mo_ta"], ""]
        dong += [
                 "| Điều kiện | Tệp | Giây âm | DER | Lượt đúng người nói | Đếm đúng số người | Giây xử lý |"
                 + (" Số dòng / lượt thật (sau gộp) | Dòng lẫn hai người | Thời lượng nằm đúng dòng |"
                    if d["co_asr"] else ""),
                 "|---|---:|---:|---:|---:|---:|---:|" + ("---:|---:|---:|" if d["co_asr"] else "")]
        for dk, t in d["tong_hop"].items():
            o = (f"| {dk} | {t['so_tep']} | {t['giay_am']:.0f} | {_pt(t['der_tb_theo_thoi_luong'])} | "
                 f"{t['luot_dung']}/{t['luot']} ({_pt(t['ti_le_luot_dung'])}) | "
                 f"{t['dem_dung_so_nguoi']}/{t['so_tep']} | {t['giay_xu_ly']:.0f} |")
            if d["co_asr"]:
                tl = t.get("ti_le_thoi_luong_dung_nguoi")
                o += (f" {t['so_dong']:.0f} / {t['luot_that']:.0f} ({t['luot_that_sau_gop']:.0f}) | "
                      f"{t['dong_lan']:.0f} ({_pt(t['ti_le_dong_lan'])}) | "
                      f"{_pt(tl) if tl is not None else '—'} |")
            dong.append(o)
        if any(t.get("ram_dinh_mb_lon_nhat") for t in d["tong_hop"].values()):
            dong += ["", f"RAM đỉnh của tiến trình tách: {d['tong_hop']['tat_ca'].get('ram_dinh_mb_lon_nhat')} MB."]
        dong.append("")
    (RA_KQ / "tach-nguoi-noi.md").write_text("\n".join(dong), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="viec", required=True)
    sub.add_parser("dung")
    p = sub.add_parser("do")
    p.add_argument("--bo-tach", choices=["mot_nguoi", "pyannote"], required=True)
    p.add_argument("--co-asr", action="store_true")
    p.add_argument("--cach-ghep", choices=["moi", "cu"], default="moi",
                   help="cu: tai tao cach ghep tu-nguoi noi truoc 25/09 de do truoc-sau")
    p.add_argument("--gioi-han", type=int, default=None)
    p.add_argument("--nhan", default=None, help="nhan ngan cho lan do (vao ten tep ket qua)")
    p.add_argument("--tieu-de", default=None, help="tieu de ngan cua lan do (vao bang Markdown)")
    p.add_argument("--mo-ta", default=None, help="mot cau mo ta lan do (vao bang Markdown)")
    p.add_argument("--pyannote-python", default=os.environ.get("PYANNOTE_PYTHON", "D:/pyannote-venv/Scripts/python.exe"))
    p.add_argument("--pyannote-khoa", default=None, help="TEP chua khoa Hugging Face")
    p.add_argument("--pyannote-thiet-bi", default="cpu", choices=["cpu", "cuda"])
    p.add_argument("--pyannote-hf-home", default=os.environ.get("PYANNOTE_HF_HOME"))
    a = ap.parse_args()
    if a.viec == "dung":
        dung()
    else:
        do(a)


if __name__ == "__main__":
    main()
