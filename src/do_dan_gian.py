# -*- coding: utf-8 -*-
"""Do bo thu thach dan gian THEO CAP — khong qua phep ghep menh de cua bo cham.

VI SAO KHONG DUNG CHI SO CUA BO CHAM. Bo cham ghep menh de voi dap an bang do giong tu
vung >= 0,6 (xem `cham_he_thong`). Ban B noi bang chu khac, nen moi chenh lech F1 giua
A va B lan lon hai thu: he thong sai, va bo cham truot nguong. Phep do o day chi so
CUNG MOT CHO (cung luot hoi thoai) giua hai ban cua mot cap:

  M1  tuong_duong / tinh_chat: trong cac menh de dan LUOT DA DOI, bao nhieu phan bi
      khoa CHAN hoac CANH BAO, va bao nhieu phan roi xuong CAN XAC NHAN — ban B so voi
      ban A. Chenh len o ban B la bao dong nham do cach noi, vi noi dung khong doi.
      Tach `trong_bang` (duong ong biet cum do) va `giu_lai` (chua gap).
  M2  mo_ho: o ban B, menh de dan luot da doi co vao THAN ban nhap o muc "chac chan"
      ma khong kem canh bao nao khong — tuc he thong tu chon mot nghia. Kem danh sach
      noi dung de doc tay (vd "om" ghi thanh "bi benh", "len ban do" ghi thanh "soi").
  M3  chen: menh de noi toi "gio" co vao THAN ban nhap khong.

    python -m src.do_dan_gian --nhanh B C C_khoa [--thu-muc kaggle-ra/the-he-8]
"""
import argparse
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

from src import dan_gian, duong_dan

TAP = "thach_thuc_dan_gian_phat_trien"
CAN_XAC_NHAN = "CẦN XÁC NHẬN"


def _doc(tep):
    return [json.loads(l) for l in Path(tep).read_text(encoding="utf-8").splitlines()
            if l.strip()]


def _cum_cua(c, ban):
    """Cum phai co trong trich dan de menh de duoc tinh cho cho doi `c`."""
    if c["loai"] == "chen":
        return None if ban == "A" else c["dan_gian"].split()[-2]
    return c["chuan"] if ban == "A" else c["dan_gian"]


def _thuoc_cho(luot, trich, bang_chung, cum):
    """Menh de dan `luot` VA trich dan chua `cum`. Mot luot co the mang nhieu cho doi
    (vd "oi" va "ban than" cung luot); khong loc theo trich dan thi canh bao cua cum
    nay bi ghi sang cum kia — loi da gap o ban dau cua phep do."""
    if luot not in (bang_chung or []):
        return False
    if cum is None:
        return False
    return any(cum.lower() in (t or "").lower() for t in (trich or []))


def _menh_de_dan(r, c, ban):
    """-> [(phat_bieu, khoa, muc)] cua cac menh de thuoc cho doi `c` o ban `ban`."""
    khoa = {k["id"]: k for k in r.get("khoa") or []}
    muc = {g["id"]: g.get("muc") for g in r.get("ghi_chu") or [] if "id" in g}
    cum = _cum_cua(c, ban)
    return [(p, khoa.get(p["id"], {}), muc.get(p["id"]))
            for p in r.get("phat_bieu") or []
            if _thuoc_cho(c["luot"], p.get("trich_dan"), p.get("bang_chung"), cum)]


def _dem(ds):
    n = len(ds)
    chan = sum(1 for _, k, _ in ds if k.get("chan"))
    canh = sum(1 for _, k, _ in ds if k.get("canh_bao") or k.get("chan"))
    cxn = sum(1 for _, _, m in ds if m == CAN_XAC_NHAN)
    return n, chan, canh, cxn


def do(bo, ra):
    """`bo`: danh sach ca cua bo thu thach. `ra`: {id: ban ghi dau ra}. -> bao cao."""
    theo_id = {c["id"]: c for c in bo}
    m1 = defaultdict(lambda: {"A": [0, 0, 0, 0], "B": [0, 0, 0, 0], "cho": 0})
    m2, m3 = [], []
    thieu = 0
    for b in (c for c in bo if c["bien_the"] == "B"):
        a = theo_id[b["id"][:-1] + "A"]
        if a["id"] not in ra or b["id"] not in ra:
            thieu += 1
            continue
        for c in b["cho_dan_gian"]:
            ds_a = _menh_de_dan(ra[a["id"]], c, "A")
            ds_b = _menh_de_dan(ra[b["id"]], c, "B")
            if c["loai"] in (dan_gian.TUONG_DUONG, dan_gian.TINH_CHAT):
                k = ("trong_bang" if c["trong_bang"] else "giu_lai", c["dan_gian"])
                for ten, ds in (("A", ds_a), ("B", ds_b)):
                    for j, x in enumerate(_dem(ds)):
                        m1[k][ten][j] += x
                m1[k]["cho"] += 1
            elif c["loai"] == dan_gian.MO_HO:
                lop = (ra[b["id"]].get("canh_bao") or {}).get("theo_phat_bieu") or {}
                for p, kh, muc in ds_b:
                    cb = [x for x in (lop.get(str(p.get("id"))) or {}).get("tat_ca") or [] if x]
                    tu_chon = (muc not in (None, CAN_XAC_NHAN) and p.get("do_chac_chan") == "chắc chắn"
                               and not kh.get("canh_bao") and not kh.get("chan"))
                    m2.append({"ca": b["id"], "cum": c["dan_gian"], "noi_dung": p.get("noi_dung"),
                               "do_chac_chan": p.get("do_chac_chan"), "muc": muc,
                               "chan": kh.get("chan") or [], "canh_bao": kh.get("canh_bao") or [],
                               "lop_canh_bao": [x["ma"] for x in cb],
                               "cau_hoi": [x["ly_do"] for x in cb if x["ma"] == MA_MO_HO],
                               "tu_chon_nghia": tu_chon,
                               "tu_chon_nghia_ca_lop": tu_chon and not cb})
            else:
                for p, kh, muc in ds_b:
                    if "gió" in (p.get("noi_dung") or "").lower():
                        m3.append({"ca": b["id"], "noi_dung": p.get("noi_dung"), "muc": muc,
                                   "canh_bao": kh.get("canh_bao") or [], "chan": kh.get("chan") or []})
    return {"m1": {f"{k[0]}|{k[1]}": v for k, v in m1.items()}, "m2": m2, "m3": m3,
            "cap_thieu_dau_ra": thieu}


# Ma cua lop canh bao cho cach noi mo ho (them 24/09/2026, `canh_bao.phat_hien.cum_mo_ho`).
# M2 dem hai cach: chi canh bao cua KHOA (duong ong da dang ky), va KE CA lop canh bao
# (lop tham do, chi hien kem cau hoi, chinh sach C khong doi ban nhap).
MA_MO_HO = "AMBIGUOUS_LAY_TERM"

# Ma cua phep kiem noi dung K2 — ma DUY NHAT phan anh cach noi. Cac ma khac (vd
# "chu_the_suy_tu_nguoi_noi") da co tu truoc o ca hai ban, khong do cach noi.
MA_NOI_DUNG = "noi_dung_khong_khop"


def do_dap_an_hoan_hao(bo):
    """Chay khoa bang chung tren DAP AN HOAN HAO cua ca hai ban — cung cach do "chan
    nham 0 / 30.136" (`danh_gia_khoa.thong_ke_khoa`). Dap an giu thuat ngu chuan ("da
    day") con trich dan o ban B noi cach dan gian ("bao tu"): day la phep thu thang
    phep kiem noi dung K2 va phep kiem muc. Khong can mo hinh.

    -> {nhom|cum: {"A": [so menh de dan luot, bi chan, chan hoac canh bao], "B": [...],
                   "ma": {ma: so lan o ban B}}}"""
    from collections import Counter

    from src import danh_gia_khoa, khoa_bang_chung as kbc
    theo_id = {c["id"]: c for c in bo}
    ra = defaultdict(lambda: {"A": [0, 0, 0, 0], "B": [0, 0, 0, 0], "ma": Counter()})
    for b in (c for c in bo if c["bien_the"] == "B"):
        a = theo_id[b["id"][:-1] + "A"]
        kq = {}
        for ten, ca in (("A", a), ("B", b)):
            ps = danh_gia_khoa.phat_bieu_tu_dap_an(ca)
            kq[ten] = list(zip(ps, kbc.khoa_ca(ps, ca["input"], True)["ket_qua"]))
        for c in b["cho_dan_gian"]:
            nhom = c["loai"] if c["loai"] in (dan_gian.MO_HO, "chen") else \
                ("trong_bang" if c["trong_bang"] else "giu_lai")
            k = f"{nhom}|{c['dan_gian']}"
            for ten in ("A", "B"):
                for p, kk in kq[ten]:
                    if not danh_gia_khoa.vao_than(p) or not _thuoc_cho(
                            c["luot"], p.trich_dan, p.bang_chung, _cum_cua(c, ten)):
                        continue
                    ra[k][ten][0] += 1
                    ra[k][ten][1] += bool(kk.chan)
                    ra[k][ten][2] += bool(kk.chan or kk.canh_bao)
                    ra[k][ten][3] += MA_NOI_DUNG in (list(kk.chan) + list(kk.canh_bao))
                    if ten == "B" and (kk.chan or kk.canh_bao):
                        ra[k]["ma"].update(list(kk.chan) + list(kk.canh_bao))
    return dict(ra)


def in_hoan_hao(kq):
    dong = ["## Đáp án hoàn hảo — bước kiểm tra căn cứ trên cách nói dân gian", "",
            "Khâu tách mệnh đề coi như không sai gì; đáp án giữ thuật ngữ chuẩn, trích dẫn "
            "ở bản B là lời dân gian. Chỉ tính mệnh đề vào thân và dẫn đúng lượt đã đổi.", "",
            "| Nhóm | Cụm | Mệnh đề (A / B) | Bị chặn (A → B) | Cảnh báo \"nội dung không khớp\" (A → B) | Mọi chặn hoặc cảnh báo (A → B) | Mã ở bản B |",
            "|---|---|---|---|---|---|---|"]
    for k, v in sorted(kq.items()):
        nhom, cum = k.split("|")
        a, b = v["A"], v["B"]
        ma = ", ".join(f"{m} ×{n}" for m, n in v["ma"].most_common()) or "—"
        dong.append(f"| {nhom} | {cum} | {a[0]} / {b[0]} | {_ti(a[1], a[0])} → {_ti(b[1], b[0])} | "
                    f"{_ti(a[3], a[0])} → {_ti(b[3], b[0])} | "
                    f"{_ti(a[2], a[0])} → {_ti(b[2], b[0])} | {ma} |")
    return "\n".join(dong) + "\n"


def _ti(x, n):
    return f"{x}/{n} ({100 * x / n:.0f} %)" if n else "—"


def in_bao_cao(nhanh, kq):
    dong = [f"## Nhánh {nhanh}", ""]
    if kq["cap_thieu_dau_ra"]:
        dong.append(f"*{kq['cap_thieu_dau_ra']} cặp thiếu đầu ra, không tính.*\n")
    dong += ["### M1 — cách nói tương đương / tả tính chất", "",
             "| Nhóm | Cụm | Số chỗ | Mệnh đề dẫn lượt (A → B) | Bị chặn (A → B) | Chặn hoặc cảnh báo (A → B) | Xuống cần xác nhận (A → B) |",
             "|---|---|---|---|---|---|---|"]
    for k, v in sorted(kq["m1"].items()):
        nhom, cum = k.split("|")
        a, b = v["A"], v["B"]
        dong.append(f"| {nhom} | {cum} | {v['cho']} | {a[0]} → {b[0]} | {_ti(a[1], a[0])} → {_ti(b[1], b[0])}"
                    f" | {_ti(a[2], a[0])} → {_ti(b[2], b[0])} | {_ti(a[3], a[0])} → {_ti(b[3], b[0])} |")
    m2 = kq["m2"]
    dong += ["", "### M2 — cách nói mơ hồ (bản B)", "",
             f"Mệnh đề dẫn lượt có cụm mơ hồ: {len(m2)}. Vào thân ở mức chắc chắn, cổng không cảnh "
             f"báo (tự chọn một nghĩa): {_ti(sum(x['tu_chon_nghia'] for x in m2), len(m2))}. Tính cả lớp "
             f"cảnh báo: {_ti(sum(x.get('tu_chon_nghia_ca_lop', x['tu_chon_nghia']) for x in m2), len(m2))}; "
             f"có câu hỏi làm rõ: {_ti(sum(bool(x.get('cau_hoi')) for x in m2), len(m2))}.", "",
             "| Ca | Cụm | Nội dung máy ghi | Chắc chắn | Mục | Cổng | Lớp cảnh báo |",
             "|---|---|---|---|---|---|---|"]
    for x in m2:
        dong.append(f"| {x['ca']} | {x['cum']} | {x['noi_dung']} | {x['do_chac_chan']} | {x['muc']} | "
                    f"{', '.join(x['chan'] + x['canh_bao']) or '—'} | "
                    f"{', '.join(x.get('lop_canh_bao') or []) or '—'} |")
    dong += ["", "### M3 — câu chèn về \"gió\" (bản B)", ""]
    if not kq["m3"]:
        dong.append("Không mệnh đề nào nói tới \"gió\".")
    for x in kq["m3"]:
        dong.append(f"- {x['ca']}: \"{x['noi_dung']}\" → mục {x['muc']}; "
                    f"{', '.join(x['chan'] + x['canh_bao']) or 'không cảnh báo'}")
    return "\n".join(dong) + "\n"


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--nhanh", nargs="*", default=[],
                    help="nhanh co dau ra mo hinh; bo trong thi chi do dap an hoan hao")
    ap.add_argument("--thu-muc", default=None, help="noi co ra_<nhanh>_<tap>.jsonl")
    ap.add_argument("--ra", default=str(duong_dan.GOC_DU_AN / "docs" / "ket-qua" / "dan-gian.md"))
    a = ap.parse_args()
    thu = Path(a.thu_muc) if a.thu_muc else duong_dan.THU_MUC_DU_LIEU
    bo = _doc(duong_dan.THU_MUC_DU_LIEU / f"{TAP}.jsonl")
    phan = ["# Bộ thử thách cách nói dân gian — đo theo cặp", "",
            "Sinh bằng `python -m src.do_dan_gian`. Đừng sửa tay. Cách đọc: đầu tệp `src/do_dan_gian.py`.", ""]
    hh = do_dap_an_hoan_hao(bo)
    phan.append(in_hoan_hao(hh))
    tho = {"dap_an_hoan_hao": {k: {**v, "ma": dict(v["ma"])} for k, v in hh.items()}}
    for n in a.nhanh:
        tep = thu / f"ra_{n}_{TAP}.jsonl"
        if not tep.exists():
            print(f"thieu {tep}")
            continue
        kq = do(bo, {r["id"]: r for r in _doc(tep)})
        tho[n] = kq
        phan.append(in_bao_cao(n, kq))
    Path(a.ra).write_text("\n".join(phan), encoding="utf-8")
    Path(a.ra).with_suffix(".json").write_text(json.dumps(tho, ensure_ascii=False, indent=1),
                                                encoding="utf-8")
    print("\n".join(phan))


if __name__ == "__main__":
    main()
