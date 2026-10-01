# -*- coding: utf-8 -*-
"""Doi chung MO HINH THUONG MAI — moc so ngoai cho du an (19/09/2026).

MUC DICH. Tra loi cau hoi "sao khong dung luon mo hinh manh nhat cho xong".
Ket qua co hai kha nang, ca hai deu dung duoc:
  - Mo hinh thuong mai cung sai chu the nhieu  -> loai loi nay khong tu het khi
    mo hinh manh len, va viec do duoc no la dong gop that.
  - Mo hinh thuong mai tot hon han             -> phai ghi dung nhu vay, va phat
    bieu lai dong gop cho dung pham vi.

GIU CHO CONG BANG. Moi khau giong het nhanh B chay tai cho:
  - cung 4 bo thach thuc the he 8, cung 300 ca
  - cung loi nhac: HUONG_DAN + 5 vi du mau + hoi thoai da danh so luot
  - cung lo do JSON (`bakeoff.LUOC_DO`), ep bang `response_format=json_schema`
    thay cho `lm-format-enforcer`. Hai cach ep khac nhau ve ky thuat nhung cung
    rang buoc mot lo do.
  - cung ham phan tich ket qua (`bakeoff._phan_tich`), nen tieu chi "JSON hop le"
    la mot.
CHI KHAC: mo hinh, va no goi qua mang thay vi chay tren GPU.

KHONG NAM TRONG SAN PHAM. Mo hinh thuong mai o day chi dung DE DO. Giai phap cua
du an khong goi ra dich vu ngoai — hoi thoai kham benh that khong duoc gui ra
may chu ngoai. Hoi thoai dung o day la do may sinh, khong co benh nhan that.

GHI RA THU MUC RIENG. Ten tep `ra_<nhanh>_<tap>.jsonl` khong kem ten mo hinh, nen
phai chay voi MEDITRACE_DATA tro vao thu muc rieng, neu khong se de len ket qua cua mo
hinh da huan luyen.

    MEDITRACE_DATA=D:/Claude/meditrace-core/data-gpt \
        python tools/doi-chung-thuong-mai.py --model gpt-6-astra --tap <bo>
"""
import argparse
import io
import json
import os
import random
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import bakeoff, du_lieu, duong_dan  # noqa: E402

KHO_KHOA = Path("D:/Claude/.secrets")
MAX_TOKEN = 3072
CHO_TOI_DA = 300          # giay cho mot loi goi
SO_LAN_THU = 4


def khoa():
    nen = (KHO_KHOA / "openai.base").read_text(encoding="utf-8").strip()
    ma = (KHO_KHOA / "openai.key").read_text(encoding="utf-8").strip()
    return nen, ma


def goi_mot_lan(nen, ma, model, loi_nhac):
    """Mot loi goi. Tra ve van ban sinh ra, hoac nem loi."""
    body = {
        "model": model,
        "max_tokens": MAX_TOKEN,
        "temperature": 0,
        "response_format": {"type": "json_schema", "json_schema": {
            "name": "phat_bieu", "strict": False, "schema": bakeoff.LUOC_DO}},
        "messages": [{"role": "user", "content": loi_nhac}],
    }
    req = urllib.request.Request(
        f"{nen}/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {ma}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=CHO_TOI_DA) as r:
        d = json.loads(r.read())
    return d["choices"][0]["message"]["content"]


def goi(nen, ma, model, loi_nhac):
    """Goi co thu lai. Cong AI nay hay treo (ghi nhan tu cac du an truoc)."""
    cuoi = None
    for lan in range(SO_LAN_THU):
        try:
            return goi_mot_lan(nen, ma, model, loi_nhac), None
        except Exception as e:  # treo, 429, 5xx deu thu lai
            cuoi = f"{type(e).__name__}: {str(e)[:160]}"
            if lan < SO_LAN_THU - 1:
                time.sleep(min(60, 5 * 2 ** lan) + random.uniform(0, 3))
    return None, cuoi


def chay_tap(tap, model, so_luong, so_luong_song_song):
    thu_muc = duong_dan.THU_MUC_DU_LIEU
    nguon = thu_muc / f"{tap}.jsonl"
    if not nguon.is_file():
        raise SystemExit(f"khong thay {nguon} — chep bo du lieu vao thu muc nay truoc")
    mau = du_lieu.nap_mau(nguon)
    mau = mau[:so_luong] if so_luong else mau

    dem = thu_muc / f"trich_{tap}_{MAX_TOKEN}.jsonl"
    da_co = set()
    if dem.exists():
        for dong in dem.read_text(encoding="utf-8").splitlines():
            if dong.strip():
                da_co.add(json.loads(dong)["id"])
    con = [m for m in mau if m["id"] not in da_co]
    print(f"{tap}: {len(mau)} ca, da co {len(da_co)}, con {len(con)}", flush=True)
    if not con:
        return

    nen, ma = khoa()
    khoa_ghi = threading.Lock()
    tep = open(dem, "a", encoding="utf-8")
    dem_xong = [0]

    def mot_ca(m):
        danh_so, so_luot = bakeoff.danh_so_luot(m["input"])
        loi_nhac = (bakeoff.HUONG_DAN + "\n\n" + bakeoff.VI_DU
                    + "\n\nBây giờ đến lượt bạn."
                    + f"\n\nHội thoại:\n{danh_so}")
        sinh, loi = goi(nen, ma, model, loi_nhac)
        if sinh is None:
            hop_le, dl, ly_do = False, None, f"goi that bai — {loi}"
            sinh = ""
        else:
            hop_le, dl, ly_do = bakeoff._phan_tich(sinh, so_luot)
        ban_ghi = {"id": m["id"], "so_luot": so_luot, "json_hop_le": hop_le,
                   "ly_do": ly_do, "phat_bieu": dl, "tho": sinh[:400],
                   "mo_hinh": model}
        with khoa_ghi:
            tep.write(json.dumps(ban_ghi, ensure_ascii=False) + "\n")
            tep.flush()
            dem_xong[0] += 1
            print(f"  [{dem_xong[0]:3d}/{len(con)}] {m['id']:14} "
                  f"{'JSON OK ' if hop_le else 'JSON HONG'} "
                  f"{len(dl) if dl else 0} phat bieu"
                  + ("" if hop_le else f"  ({ly_do})"), flush=True)

    hang = list(con)
    khoa_hang = threading.Lock()

    def tho():
        while True:
            with khoa_hang:
                if not hang:
                    return
                m = hang.pop(0)
            try:
                mot_ca(m)
            except Exception as e:
                print(f"  !!! {m['id']}: {type(e).__name__}: {e}", flush=True)

    luong = [threading.Thread(target=tho, daemon=True)
             for _ in range(so_luong_song_song)]
    for t in luong:
        t.start()
    for t in luong:
        t.join()
    tep.close()


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace", line_buffering=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tap", nargs="+", required=True)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--song-song", type=int, default=6)
    a = ap.parse_args()

    if duong_dan.THU_MUC_DU_LIEU.name == "data":
        raise SystemExit(
            "dang ghi vao data/ — se de len ket qua cua mo hinh da huan luyen.\n"
            "Dat MEDITRACE_DATA tro vao mot thu muc rieng roi chay lai.")
    print("thu muc du lieu:", duong_dan.THU_MUC_DU_LIEU, flush=True)
    print("mo hinh        :", a.model, flush=True)
    for tap in a.tap:
        chay_tap(tap, a.model, a.n, a.song_song)


if __name__ == "__main__":
    main()
