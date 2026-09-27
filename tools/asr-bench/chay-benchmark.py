"""Benchmark ASR tren CUNG bo am thanh cua MediTrace.

    python tools/asr-bench/chay-benchmark.py tat-ca          # chay moi he, moi he mot tien trinh
    python tools/asr-bench/chay-benchmark.py chay <he>       # chay mot he
    python tools/asr-bench/chay-benchmark.py tong-hop        # tinh thuoc do, viet bao cao

He: xem HE ben duoi. Am thanh: tools/asr-bench/tao-am-thanh-thu.py (5 giong x 2 dieu kien).
Ket qua tho: data/audio-bench/ket-qua/<he>.json (khong vao git vi di kem am thanh co giay
phep phi thuong mai). Bao cao: docs/ket-qua/asr-benchmark.md + .json.

Do tai nguyen: VRAM dinh doc bang nvidia-smi moi 0,2 s (tru muc nen truoc khi nap),
RAM dinh = RSS lon nhat cua tien trinh. Lan chay dau tien (khoi dong) khong tinh gio.
"""
import json
import platform
import subprocess
import sys
import threading
import time
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC))
DL = GOC / "data" / "audio-bench"
KQ = DL / "ket-qua"

HE = {
    "phowhisper-small": ("phowhisper", "vinai/PhoWhisper-small", {}),
    "phowhisper-medium": ("phowhisper", "vinai/PhoWhisper-medium", {}),
    "faster-whisper-small": ("faster_whisper", "small", {}),
    "faster-whisper-large-v3-turbo": ("faster_whisper", "large-v3-turbo", {"compute_type": "int8_float16"}),
}
DIEU_KIEN = ("sach", "on")
# Nhom giong: VIVOS co the nam trong du lieu huan luyen PhoWhisper (can xac nhan) nen tach rieng
NHOM = {"chinh": ("mms", "vais1000", "25hours"), "vivos": ("vivos_a", "vivos_b")}


def _vram_mb():
    try:
        o = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                           capture_output=True, text=True, timeout=5).stdout
        return int(o.split()[0])
    except Exception:
        return None


class DoTaiNguyen(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        import psutil
        self.p = psutil.Process()
        self.nen = _vram_mb()
        self.vram = self.nen or 0
        self.ram = self.p.memory_info().rss
        self.dung = False

    def run(self):
        while not self.dung:
            v = _vram_mb()
            if v is not None:
                self.vram = max(self.vram, v)
            self.ram = max(self.ram, self.p.memory_info().rss)
            time.sleep(0.2)


def chay(he):
    from src.audio.asr import registry
    from src.audio.asr.faster_whisper_provider import FasterWhisperProvider
    loai, model, them = HE[he]
    bo = json.loads((DL / "muc-thu.json").read_text(encoding="utf-8"))
    do = DoTaiNguyen()
    do.start()
    p = registry.create("phowhisper", model=model) if loai == "phowhisper" else FasterWhisperProvider(model, **them)
    t0 = time.time()
    if loai == "phowhisper":
        p._load()
    else:
        p._model()
    nap = time.time() - t0
    p.transcribe(GOC / bo["muc"][0]["am"]["mms"]["sach"])          # khoi dong, khong tinh
    ra = {"he": he, "provider": loai, "model": model, "nap_giay": round(nap, 2), "ket_qua": {}, "ghi_chu": {}}
    for giong in bo["giong"]:
        for dk in DIEU_KIEN:
            hyps, xu_ly, am = {}, 0.0, 0.0
            for m in bo["muc"]:
                r = p.transcribe(GOC / m["am"][giong][dk])
                hyps[m["id"]] = " ".join(s.text for s in r.segments).strip()
                xu_ly += r.processing_seconds or 0
                am += r.audio_duration or 0
                if r.notes:
                    ra["ghi_chu"][f"{m['id']}@{giong}/{dk}"] = r.notes
            ra["ket_qua"][f"{giong}/{dk}"] = {"hyps": hyps, "giay_xu_ly": round(xu_ly, 2),
                                              "giay_am_thanh": round(am, 2)}
    ra.update(revision=r.revision, device=r.device, dtype=r.dtype, timestamp_level=r.timestamp_level,
              inference_config=r.inference_config)
    do.dung = True
    do.join()
    ra["vram_dinh_mb"] = (do.vram - do.nen) if do.nen is not None else None
    ra["ram_dinh_mb"] = round(do.ram / 2**20)
    tong_xl = sum(v["giay_xu_ly"] for v in ra["ket_qua"].values())
    tong_am = sum(v["giay_am_thanh"] for v in ra["ket_qua"].values())
    ra["rtf"] = round(tong_xl / tong_am, 4)
    KQ.mkdir(parents=True, exist_ok=True)
    (KQ / f"{he}.json").write_text(json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")
    print(he, "xong rtf", ra["rtf"], ra["vram_dinh_mb"], "MB VRAM", len(ra["ghi_chu"]), "ghi chu")


def moi_truong():
    import torch
    import transformers
    try:
        import ctranslate2
        import faster_whisper
        fw = (faster_whisper.__version__, ctranslate2.__version__)
    except ImportError:
        fw = (None, None)
    cuda = torch.cuda.is_available()
    return {"python": platform.python_version(), "torch": torch.__version__,
            "transformers": transformers.__version__, "faster_whisper": fw[0], "ctranslate2": fw[1],
            "gpu": torch.cuda.get_device_name(0) if cuda else None,
            "gpu_vram_mb": torch.cuda.get_device_properties(0).total_memory // 2**20 if cuda else None,
            "os": platform.platform()}


def _pct(x):
    return "—" if x is None else f"{100 * x:.1f}%"


def _gop(muc, r, giongs, dk):
    """Gop nhieu giong thanh mot bo: moi (cau, giong) la mot muc, cap tach theo giong."""
    mm, hy = [], {}
    for g in giongs:
        k = r["ket_qua"].get(f"{g}/{dk}")
        if not k:
            continue
        for m in muc:
            i = f"{m['id']}@{g}"
            mm.append({"id": i, "van_ban": m["van_ban"], "cap": f"{m['cap']}@{g}" if m.get("cap") else None})
            hy[i] = k["hyps"][m["id"]]
    return mm, hy


def tong_hop():
    from src.audio.asr.bench_metrics import LOAI, tong_hop as th
    bo = json.loads((DL / "muc-thu.json").read_text(encoding="utf-8"))
    muc = bo["muc"]
    so_cap = len({m["cap"] for m in muc if m.get("cap")})
    kq = {he: json.loads((KQ / f"{he}.json").read_text(encoding="utf-8")) for he in HE if (KQ / f"{he}.json").exists()}
    bang, theo_giong = [], []
    for he, r in kq.items():
        for nhom, giongs in NHOM.items():
            for dk in DIEU_KIEN:
                d = th(*_gop(muc, r, giongs, dk))
                d.pop("chi_tiet")
                bang.append({"he": he, "nhom": nhom, "dieu_kien": dk, "do": d})
        for g in bo["giong"]:
            d = th(muc, r["ket_qua"][f"{g}/sach"]["hyps"])
            theo_giong.append({"he": he, "giong": g, "wer": d["wer"], "cap": d["cap_toi_thieu"]["phan_biet_dung"],
                               "cau_sai": d["ty_le_cau_sai_tu_khoa"]})
    mt = moi_truong()
    ra = {"moi_truong": mt, "giong": bo["giong"], "snr_db": bo["snr_db"], "so_cau": len(muc),
          "muc": [{"id": m["id"], "van_ban": m["van_ban"], "doc": m["doc"], "cap": m.get("cap")} for m in muc],
          "he": {he: {x: r.get(x) for x in ("model", "revision", "device", "dtype", "timestamp_level",
                                            "inference_config", "nap_giay", "vram_dinh_mb", "ram_dinh_mb",
                                            "rtf", "ghi_chu")} for he, r in kq.items()},
          "bang": bang, "theo_giong": theo_giong,
          "ban_chep": {he: {k: v["hyps"] for k, v in r["ket_qua"].items()} for he, r in kq.items()}}
    (GOC / "docs" / "ket-qua" / "asr-benchmark.json").write_text(
        json.dumps(ra, ensure_ascii=False, indent=1), encoding="utf-8")

    L = ["# Benchmark ASR trên bộ câu thử của MediTrace", "",
         f"Chạy ngày {time.strftime('%d/%m/%Y')} trên {mt['gpu']} ({mt['gpu_vram_mb']} MB VRAM), {mt['os']}. "
         "Sinh bởi `tools/asr-bench/chay-benchmark.py tong-hop` — không sửa tay.", "",
         "## Giới hạn phải đọc trước", "",
         "- Âm thanh là **giọng máy đọc**, không phải người thật; không có tiếng phòng khám, không có nói chen. "
         "Kết quả dưới đây **không** thay được bản ghi thật và **không** đủ để kết luận mô hình nào phù hợp "
         "hơn cho MediTrace.",
         f"- {len(muc)} câu ngắn, trong đó {so_cap} cặp tối thiểu, mỗi câu đọc bằng {len(bo['giong'])} giọng máy.",
         "- Nhóm `chinh` = 3 giọng mms, vais1000, 25hours. Nhóm `vivos` = 2 người đọc của giọng Piper học từ "
         "VIVOS. PhoWhisper được đánh giá trên VIVOS và VinAI không công bố thành phần 844 giờ dữ liệu huấn luyện, "
         "nên tập huấn luyện VIVOS có thể nằm trong đó (cần xác nhận); nhóm này có thể có lợi cho PhoWhisper và "
         "được báo cáo riêng.",
         "- Máy đọc không đọc được chữ f, z, w nên tên thuốc được đưa vào dưới dạng phiên âm kiểu Việt "
         "(ví dụ “mét pho min”), còn bản chép chuẩn vẫn viết tên gốc. Cột `thuoc` vì thế đo việc mô hình có "
         "viết được tên gốc từ cách đọc kiểu Việt hay không — không phải đo nghe tên thuốc đọc chuẩn.",
         f"- Điều kiện `on` = thêm ồn trắng SNR {bo['snr_db']:.0f} dB. Ồn trắng không giống ồn phòng khám.",
         "- Trước khi đo, cả bản chuẩn và bản nhận dạng qua cùng một bước chuẩn hoá: chữ thường, bỏ dấu câu, "
         "“mi li gam”/“miligram” → “mg”, số đọc bằng chữ → chữ số. Bước này chỉ dùng để đo.",
         "- Một cặp tối thiểu được tính là phân biệt đúng khi loại thông tin làm hai câu khác nhau (ví dụ liều "
         "5 mg / 50 mg) được nghe đúng ở cả hai câu. Sai ở loại khác (ví dụ tên thuốc) không làm trượt cặp.", "",
         "## Bảng chính", "",
         "| Hệ | Nhóm giọng | Điều kiện | WER | Câu sai ≥1 từ khoá | Cặp phân biệt đúng |",
         "|---|---|---|---|---|---|"]
    for b in bang:
        d = b["do"]
        c = d["cap_toi_thieu"]
        L.append(f"| {b['he']} | {b['nhom']} | {b['dieu_kien']} | {_pct(d['wer'])} | "
                 f"{_pct(d['ty_le_cau_sai_tu_khoa'])} | {c['phan_biet_dung']}/{c['tong']} |")
    L += ["", "## Tài nguyên", "",
          "| Hệ | RTF | VRAM đỉnh | RAM đỉnh | Nạp mô hình | Đoạn có ghi chú lặp |", "|---|---|---|---|---|---|"]
    for he, r in kq.items():
        lap = sum(1 for v in r["ghi_chu"].values() if any("lap_lai" in n for n in v))
        L.append(f"| {he} | {r['rtf']:.3f} | {r['vram_dinh_mb']} MB | {r['ram_dinh_mb']} MB | {r['nap_giay']} s | "
                 f"{lap} |")
    L += ["", "RTF = giây xử lý / giây âm thanh, trên toàn bộ 10 lượt (5 giọng × 2 điều kiện). "
          "VRAM đỉnh = mức nvidia-smi cao nhất trừ mức nền trước khi nạp. RAM đỉnh = bộ nhớ lớn nhất của "
          "tiến trình Python. Nạp mô hình tính từ bộ nhớ đệm trên đĩa.", "",
          "## WER theo từng giọng (điều kiện sạch)", "",
          "| Hệ | " + " | ".join(bo["giong"]) + " |", "|---|" + "---|" * len(bo["giong"])]
    for he in kq:
        o = [f"{_pct(x['wer'])} ({x['cap']}/{so_cap})" for x in theo_giong if x["he"] == he]
        L.append(f"| {he} | " + " | ".join(o) + " |")
    L += ["", "Trong ngoặc: số cặp tối thiểu phân biệt đúng.", "",
          "## Tỷ lệ sai theo loại từ khoá (nhóm chinh)", "",
          "Mẫu số = số (câu, giọng) mà bản chuẩn có loại từ khoá đó. “thêm” = bản chuẩn không có nhưng mô hình "
          "nghe ra (ví dụ tự thêm chữ “không”).", "",
          "| Hệ | Điều kiện | " + " | ".join(LOAI) + " |", "|---|---|" + "---|" * len(LOAI)]
    for b in bang:
        if b["nhom"] != "chinh":
            continue
        o = []
        for k in LOAI:
            v = b["do"]["theo_loai"][k]
            o.append(f"{_pct(v['ty_le_sai'])} ({v['sai']}/{v['co']}, +{v['them']})")
        L.append(f"| {b['he']} | {b['dieu_kien']} | " + " | ".join(o) + " |")
    L += ["", "## Phiên bản", "", "| Hệ | Mô hình | Revision | Thiết bị | dtype | Mốc thời gian |",
          "|---|---|---|---|---|---|"]
    for he, r in kq.items():
        L.append(f"| {he} | {r['model']} | {r['revision'] or '—'} | {r['device']} | {r['dtype']} | "
                 f"{r['timestamp_level']} |")
    L += ["", f"Python {mt['python']}, torch {mt['torch']}, transformers {mt['transformers']}, "
          f"faster-whisper {mt['faster_whisper']}, ctranslate2 {mt['ctranslate2']}.", "",
          "Bản chép từng câu của từng hệ, từng giọng nằm trong `docs/ket-qua/asr-benchmark.json` (mục `ban_chep`)."]
    (GOC / "docs" / "ket-qua" / "asr-benchmark.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    lenh = sys.argv[1] if len(sys.argv) > 1 else "tat-ca"
    if lenh == "chay":
        chay(sys.argv[2])
    elif lenh == "tong-hop":
        tong_hop()
    else:
        for he in (sys.argv[2:] or HE):
            subprocess.run([sys.executable, __file__, "chay", he], check=False)
        tong_hop()
