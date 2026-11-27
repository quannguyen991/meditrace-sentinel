# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Đo bộ thử thách dân gian theo cặp A và B: nói chữ khác mà nghĩa không đổi thì hệ
           thống có chặn, cảnh báo hay tự chọn nghĩa không.
Vào → Ra : đầu ra các nhánh trên bộ dân gian (--nhanh, --thu-muc) → báo cáo markdown M1
           tương đương, M2 mơ hồ, M3 chen giờ
Đọc từ   : do() đo một nhánh theo cặp; main() ghi báo cáo dan-gian.md
Mục lục (các hàm/lớp chính):
  do()                  Đo bộ thử thách dân gian theo cặp A và B
  do_dap_an_hoan_hao()  Chạy khoá bằng chứng trên đáp án hoàn hảo hai bản
  in_bao_cao()          Dựng báo cáo Markdown của một nhánh
  in_hoan_hao()         Dựng bảng Markdown cho phép đo đáp án hoàn hảo
  main()                Chạy dòng lệnh đo bộ dân gian và ghi báo cáo
Gọi tới  : do_luong/danh_gia_khoa, bo_du_lieu/dan_gian, duong_ong/b4_kiem_can_cu,
           he_thong/duong_dan
Tên cũ   : do_dan_gian.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đo bộ thử thách dân gian THEO CẶP — không qua phép ghép mệnh đề của bộ chấm.

VÌ SAO KHÔNG DÙNG CHỈ SỐ CỦA BỘ CHẤM. Bộ chấm ghép mệnh đề với đáp án bằng độ giống từ
vựng >= 0,6 (xem `cham_he_thong`). Bản B nói bằng chữ khác, nên mọi chênh lệch F1 giữa
A và B lẫn lộn hai thứ: hệ thống sai, và bộ chấm trượt ngưỡng. Phép đo ở đây chỉ so
CÙNG MỘT CHỖ (cùng lượt hội thoại) giữa hai bản của một cặp:

  M1  tuong_duong / tinh_chat: trong các mệnh đề dẫn LƯỢT ĐÃ ĐỔI, bao nhiêu phần bị
      khoá CHẶN hoặc CẢNH BÁO, và bao nhiêu phần rơi xuống CẦN XÁC NHẬN — bản B so với
      bản A. Chênh lên ở bản B là báo động nhầm do cách nói, vì nội dung không đổi.
      Tách `trong_bang` (đường ống biết cụm đó) và `giu_lai` (chưa gặp).
  M2  mo_ho: ở bản B, mệnh đề dẫn lượt đã đổi có vào THÂN bản nháp ở mức "chắc chắn"
      mà không kèm cảnh báo nào không — tức hệ thống tự chọn một nghĩa. Kèm danh sách
      nội dung để đọc tay (vd "ốm" ghi thành "bị bệnh", "lên ban đỏ" ghi thành "sởi").
  M3  chen: mệnh đề nói tới "giờ" có vào THÂN bản nháp không.

    python -m src.do_luong.do_dan_gian --nhanh B C C_khoa [--thu-muc kaggle-ra/the-he-8]
"""
import argparse
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

from src.bo_du_lieu import dan_gian as dan_gian
from src.he_thong import duong_dan as duong_dan

TAP = "thach_thuc_dan_gian_phat_trien"
CAN_XAC_NHAN = "CẦN XÁC NHẬN"


# ─── _doc() — Đọc tệp JSONL thành danh sách ───────────────────────────────────────────
def _doc(tep):
    return [json.loads(l) for l in Path(tep).read_text(encoding="utf-8").splitlines()
            if l.strip()]


# ─── _cum_cua() — Lấy cụm phải có trong trích dẫn ở mỗi bản ───────────────────────────
# Bản A dùng cụm chuẩn, bản B dùng cụm dân gian.
def _cum_cua(c, ban):
    """Cụm phải có trong trích dẫn để mệnh đề được tính cho chỗ đổi `c`."""
    if c["loai"] == "chen":
        return None if ban == "A" else c["dan_gian"].split()[-2]
    return c["chuan"] if ban == "A" else c["dan_gian"]


# ─── _thuoc_cho() — Xét mệnh đề có dẫn đúng chỗ đổi ───────────────────────────────────
# Phải dẫn đúng lượt và trích dẫn chứa cụm.
def _thuoc_cho(luot, trich, bang_chung, cum):
    """Mệnh đề dẫn `luot` VÀ trích dẫn chứa `cum`. Một lượt có thể mang nhiều chỗ đổi
    (vd "ơi" và "bản thân" cùng lượt); không lọc theo trích dẫn thì cảnh báo của cụm
    này bị ghi sang cụm kia — lỗi đã gặp ở bản đầu của phép đo."""
    if luot not in (bang_chung or []):
        return False
    if cum is None:
        return False
    return any(cum.lower() in (t or "").lower() for t in (trich or []))


# ─── _menh_de_dan() — Lấy mệnh đề thuộc một chỗ đổi ở một bản ─────────────────────────
# Kèm kết quả khoá và mục của từng mệnh đề.
def _menh_de_dan(r, c, ban):
    """-> [(phat_bieu, khoa, muc)] của các mệnh đề thuộc chỗ đổi `c` ở bản `ban`."""
    khoa = {k["id"]: k for k in r.get("khoa") or []}
    muc = {g["id"]: g.get("muc") for g in r.get("ghi_chu") or [] if "id" in g}
    cum = _cum_cua(c, ban)
    return [(p, khoa.get(p["id"], {}), muc.get(p["id"]))
            for p in r.get("phat_bieu") or []
            if _thuoc_cho(c["luot"], p.get("trich_dan"), p.get("bang_chung"), cum)]


# ─── _dem() — Đếm mệnh đề, bị chặn, cảnh báo, xuống cần xác nhận ──────────────────────
def _dem(ds):
    n = len(ds)
    chan = sum(1 for _, k, _ in ds if k.get("chan"))
    canh = sum(1 for _, k, _ in ds if k.get("canh_bao") or k.get("chan"))
    cxn = sum(1 for _, _, m in ds if m == CAN_XAC_NHAN)
    return n, chan, canh, cxn


# ═══ do() — Đo bộ thử thách dân gian theo cặp A và B ══════════════════════════════════
# Gồm ba phép đo: tương đương hoặc tả tính chất, mơ hồ, chèn; cặp thiếu đầu ra bị bỏ.
def do(bo, ra):
    """`bo`: danh sách ca của bộ thử thách. `ra`: {id: bản ghi đầu ra}. -> báo cáo."""
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


# Mã của lớp cảnh báo cho cách nói mơ hồ (thêm 24/09/2026, `canh_bao.phat_hien.cum_mo_ho`).
# M2 đếm hai cách: chỉ cảnh báo của KHOÁ (đường ống đã đăng ký), và KỂ CẢ lớp cảnh báo
# (lớp thăm dò, chỉ hiện kèm câu hỏi, chính sách C không đổi bản nháp).
MA_MO_HO = "AMBIGUOUS_LAY_TERM"

# Mã của phép kiểm nội dung K2 — mã DUY NHẤT phản ánh cách nói. Các mã khác (vd
# "chu_the_suy_tu_nguoi_noi") đã có từ trước ở cả hai bản, không đo cách nói.
MA_NOI_DUNG = "noi_dung_khong_khop"


# ═══ do_dap_an_hoan_hao() — Chạy khoá bằng chứng trên đáp án hoàn hảo hai bản ═════════
# Thử thẳng phép kiểm nội dung và mục, không cần mô hình.
def do_dap_an_hoan_hao(bo):
    """Chạy khoá bằng chứng trên ĐÁP ÁN HOÀN HẢO của cả hai bản — cùng cách đo "chặn
    nhầm 0 / 30.136" (`danh_gia_khoa.thong_ke_khoa`). Đáp án giữ thuật ngữ chuẩn ("dạ
    dày") còn trích dẫn ở bản B nói cách dân gian ("bao tử"): đây là phép thử thẳng
    phép kiểm nội dung K2 và phép kiểm mức. Không cần mô hình.

    -> {nhom|cum: {"A": [số mệnh đề dẫn lượt, bị chặn, chặn hoặc cảnh báo], "B": [...],
                   "ma": {ma: số lần ở bản B}}}"""
    from collections import Counter

    from src.do_luong import danh_gia_khoa as danh_gia_khoa
    from src.duong_ong import b4_kiem_can_cu as kbc
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


# ═══ in_hoan_hao() — Dựng bảng Markdown cho phép đo đáp án hoàn hảo ═══════════════════
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


# ─── _ti() — Định dạng tỉ lệ dạng số lượng và phần trăm ───────────────────────────────
def _ti(x, n):
    return f"{x}/{n} ({100 * x / n:.0f} %)" if n else "—"


# ═══ in_bao_cao() — Dựng báo cáo Markdown của một nhánh ═══════════════════════════════
# Gồm ba phần đo của bộ dân gian theo cặp.
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


# ═══ main() — Chạy dòng lệnh đo bộ dân gian và ghi báo cáo ════════════════════════════
# Luôn đo đáp án hoàn hảo; thêm nhánh nếu có đầu ra mô hình.
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
            "Sinh bằng `python -m src.do_luong.do_dan_gian`. Đừng sửa tay. Cách đọc: đầu tệp `src/do_luong/do_dan_gian.py`.", ""]
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
