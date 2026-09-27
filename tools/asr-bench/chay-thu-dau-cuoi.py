"""Chay thu dau-cuoi: tep am thanh -> pipeline am thanh that -> dau vao loi MediTrace.

Dung PhoWhisper that (khong gia lap) va ffmpeg that. Ghep 3 cau giong may (hai giong khac
nhau, cach nhau 1,2 s lang) thanh mot tep 44,1 kHz stereo de buoc tien xu ly phai doi ve
16 kHz mono. Kiem:
  - am thanh goc con nguyen (so ma bam truoc va sau),
  - co ban chep tieng Viet, co moc thoi gian, co provider/model/revision,
  - vai nguoi noi van la unknown cho den khi nguoi duyet gan,
  - dau vao MediTrace bi chan khi con vai unknown, di qua khi da gan vai.

Chay: HF_HOME=D:/hf-cache D:/meditrace-venv-lap/Scripts/python tools/asr-bench/chay-thu-dau-cuoi.py
Ra:   docs/ket-qua/asr-chay-thu-dau-cuoi.json (khong chua am thanh).
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC))
os.environ.setdefault("ASR_PROVIDER", "phowhisper")
os.environ.setdefault("ASR_MODEL", "small")

from src.audio.config import AudioSettings  # noqa: E402
from src.audio.pipeline import AudioPipeline  # noqa: E402
from src.audio.storage import SessionStore  # noqa: E402

CAU = [("c02b", "vais1000"), ("d01", "25hours"), ("c03b", "vais1000")]


def main():
    wav = GOC / "data" / "audio-bench" / "wav"
    tam = Path(tempfile.mkdtemp(prefix="asr-dau-cuoi-"))
    danh_sach = tam / "ds.txt"
    lang = tam / "lang.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "anullsrc=r=16000:cl=mono", "-t", "1.2",
                    "-c:a", "pcm_s16le", str(lang)], check=True)
    dong = []
    for i, (cid, g) in enumerate(CAU):
        if i:
            dong.append(f"file '{lang.as_posix()}'")
        dong.append(f"file '{(wav / f'{cid}__{g}__sach.wav').as_posix()}'")
    danh_sach.write_text("\n".join(dong), encoding="utf-8")
    goc = tam / "ghi-am.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(danh_sach),
                    "-ar", "44100", "-ac", "2", str(goc)], check=True)
    data = goc.read_bytes()

    store = SessionStore(tam / "phien")
    s = AudioSettings.from_env()
    pipe = AudioPipeline(store, settings=s)
    sid = store.create()["session_id"]
    pipe.upload(sid, data, "ghi-am.wav")
    raw = Path(store.load(sid)["raw_audio_path"])
    bam_truoc = hashlib.sha256(raw.read_bytes()).hexdigest()
    ket = pipe.process(sid)
    bam_sau = hashlib.sha256(raw.read_bytes()).hexdigest()
    ban_chep = pipe.transcript(sid)
    phien = store.load(sid)

    chan = None
    try:
        pipe.meditrace_input(sid)
    except Exception as exc:  # phai bi chan vi vai con unknown
        chan = f"{type(exc).__name__}: {exc}"
    loa = sorted({t["speaker_id"] for t in ban_chep})
    pipe.map_speakers(sid, {loa[0]: "patient"})
    for t in pipe.transcript(sid):
        if t.get("asr_review_required"):
            pipe.confirm_segment(sid, t["segment_id"])
    vao = pipe.meditrace_input(sid)

    ra = {
        "cau_dua_vao": [f"{c}@{g}" for c, g in CAU],
        "trang_thai_xu_ly": ket.get("status") if isinstance(ket, dict) else None,
        "am_thanh_goc_con_nguyen": bam_truoc == bam_sau,
        "tien_xu_ly": phien.get("audio_quality"),
        "asr": phien.get("asr"),
        "ban_chep": [{k: t.get(k) for k in ("segment_id", "start_time", "end_time", "text_original",
                                             "asr_confidence", "asr_provider", "asr_model", "speaker_id",
                                             "speaker_role")} for t in ban_chep],
        "chan_khi_vai_unknown": chan,
        "dau_vao_meditrace": vao,
    }
    out = GOC / "docs" / "ket-qua" / "asr-chay-thu-dau-cuoi.json"
    out.write_text(json.dumps(ra, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps(ra, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
