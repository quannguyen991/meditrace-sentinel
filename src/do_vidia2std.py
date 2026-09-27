# -*- coding: utf-8 -*-
"""Do bang chuan hoa phuong ngu (`chuan_hoa`) tren cau THAT: bo ViDia2Std.

VI SAO (24/09/2026). Bang thay cua bo sinh (`phuong_ngu.THAY_DUOC`) va bang chuan hoa
lay tu CUNG mot tu dien do GPT sinh, nen tren du lieu tu sinh bang chuan hoa biet truoc
moi tu phuong ngu — phep thu phuong ngu cua du an do "he thong ap dung dung bang cua
no", khong do "he thong chiu duoc phuong ngu that". Bo ViDia2Std pha vong tron do:

  Ta, Dinh, Nguyen. ViDia2Std: A Parallel Corpus and Methods for Low-Resource Vietnamese
  Dialect-to-Standard Translation. AAAI-26 (2026). 13.657 cap cau binh luan Facebook,
  63 tinh, nguoi ban ngu viet lai sang tieng Viet chuan (dong thuan 82-86 %).
  Giay phep CC-BY-NC-4.0. Tep luu NGOAI kho (bien VIDIA2STD_DIR), khong phat tan lai.

GIOI HAN PHAI GHI KEM. Day la binh luan mang xa hoi, KHONG phai hoi thoai kham benh. Con
so o day chi noi bang chuan hoa PHU duoc bao nhieu cho khac biet phuong ngu trong tieng
Viet viet tu nhien — khong noi he thong hieu loi benh nhan.

CACH DO, theo tung CHO KHAC BIET giua cau phuong ngu va cau chuan (can hang bang
difflib tren tu; cum thay CUNG DO DAI tach thanh tung cap mot tu — "chi mô" -> "gì đâu"
la hai cho, vi bang co the sua mot va bo mot):
  doi_dung     bang doi cho do thanh DUNG chu nguoi viet lai dung
  doi_khac_chu bang doi cho do nhung ra chu khac. PHAN LON la tu cung nghia ("rứa" ->
               "vậy" khi nguoi viet lai dung "thế"; "chừ" -> "bây giờ" / "giờ") hoac sua
               duoc mot phan cum; SO IT sai nghia that ("mệ" -> "bà" khi nguoi viet lai
               ghi "mẹ"). May khong tach duoc hai loai: bao cao in danh sach cap de doc tay.
  bo_qua       bang khong dong vao cho do
  doi_thua     bang doi mot cho ma nguoi viet lai GIU NGUYEN (chuan hoa qua tay)
Them/bot tu (vd tieu tu cuoi cau "nả") tach rieng: phep thay tu khong the lam.

TAP DEV DE DOC TAY, TAP TEST DE LAY SO. Danh sach cap in ra chi rut tu dev: neu sau nay
them tu vao bang thi phai lay tu tap train cua ViDia2Std, khong tu test.

    python -m src.do_vidia2std
"""
import argparse
import csv
import difflib
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from src import chuan_hoa, duong_dan

THU_MUC = Path(os.environ.get("VIDIA2STD_DIR", "D:/Claude/tai-lieu-ngoai-ban-quyen/vidia2std"))
_TU = re.compile(r"[\wÀ-ỹ]+")


def _tach(van):
    """-> [(tu thuong, bat dau, ket thuc)] tren chuoi goc."""
    return [(m.group(0).lower(), m.start(), m.end()) for m in _TU.finditer(van or "")]


def _so_loi(a, b):
    """So phep sua (thay + xoa + chen) de bien day tu `a` thanh `b`."""
    n, m = len(a), len(b)
    d = list(range(m + 1))
    for i in range(1, n + 1):
        truoc, d[0] = d[0], i
        for j in range(1, m + 1):
            tam = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, truoc + (a[i - 1] != b[j - 1]))
            truoc = tam
    return d[m]


def _don_vi(tp, tc):
    """Cac cho khac biet -> [(i1, i2, j1, j2)] va so cho them/bot tu."""
    sm = difflib.SequenceMatcher(None, [t for t, _, _ in tp], tc, autojunk=False)
    ra, them_bot = [], 0
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        if op in ("delete", "insert"):
            them_bot += 1
        elif i2 - i1 == j2 - j1:
            ra += [(k, k + 1, j1 + k - i1, j1 + k - i1 + 1) for k in range(i1, i2)]
        else:
            ra.append((i1, i2, j1, j2))
    return ra, them_bot


def do_cau(phuong_ngu, chuan, gom_can_hoi=True):
    """-> {"doi_dung", "doi_khac_chu", "bo_qua", "them_bot", "doi_thua", "loi_goc",
    "loi_sau", "so_tu", "cap": [(cum phuong ngu, cum chuan, ket qua)]} cho MOT cap cau."""
    tp = _tach(phuong_ngu)
    tc = [t for t, _, _ in _tach(chuan)]
    cho = [c for c in chuan_hoa.phan_tich(phuong_ngu)
           if c.nghia and c.muc_tin and (gom_can_hoi or c.muc_tin == chuan_hoa.CHAC)]
    kq = Counter()
    cap = []
    dung_cho = set()
    don_vi, kq["them_bot"] = _don_vi(tp, tc)
    for i1, i2, j1, j2 in don_vi:
        a, b = tp[i1][1], tp[i2 - 1][2]
        cum_pn = " ".join(t for t, _, _ in tp[i1:i2])
        cum_ch = " ".join(tc[j1:j2])
        trung = [c for c in cho if c.bat_dau < b and c.ket_thuc > a]
        if not trung:
            kq["bo_qua"] += 1
            cap.append((cum_pn, cum_ch, "bo_qua"))
            continue
        dung_cho.update(id(c) for c in trung)
        # Ap cac cho doi nam trong doan len chinh doan do, roi so voi chu nguoi viet lai.
        dau = min([a] + [c.bat_dau for c in trung])
        cuoi = max([b] + [c.ket_thuc for c in trung])
        doan = phuong_ngu[dau:cuoi]
        for c in sorted(trung, key=lambda c: c.bat_dau, reverse=True):
            doan = doan[:c.bat_dau - dau] + c.nghia + doan[c.ket_thuc - dau:]
        moi = " ".join(_TU.findall(doan.lower()))
        if moi == cum_ch:
            kq["doi_dung"] += 1
            cap.append((cum_pn, cum_ch, "doi_dung"))
        else:
            kq["doi_khac_chu"] += 1
            cap.append((cum_pn, cum_ch, f"doi_khac_chu:{moi}"))
    # Cho bang doi ma nguoi viet lai giu nguyen: nam tron trong mot doan "equal".
    thua = [c for c in cho if id(c) not in dung_cho]
    kq["doi_thua"] = len(thua)
    cap += [(c.goc.lower(), c.goc.lower(), f"doi_thua:{c.nghia.lower()}") for c in thua]
    sau = [t for t, _, _ in _tach(chuan_hoa.chuan_hoa(phuong_ngu, gom_can_hoi))]
    kq["loi_goc"] = _so_loi([t for t, _, _ in tp], tc)
    kq["loi_sau"] = _so_loi(sau, tc)
    kq["so_tu"] = len(tc)
    return {**kq, "cap": cap}


def do_tep(tep, gom_can_hoi=True):
    """-> (tong theo vung, {loai: Counter cap}) — loai: bo_qua / doi_khac_chu / doi_thua."""
    tong = defaultdict(Counter)
    cac = defaultdict(Counter)
    with open(tep, encoding="utf-8") as f:
        for h in csv.DictReader(f):
            r = do_cau(h["dialect"], h["standard"], gom_can_hoi)
            for vung in (h.get("region") or "?", "tat_ca"):
                tong[vung]["so_cau"] += 1
                for k, v in r.items():
                    if k != "cap":
                        tong[vung][k] += v
            for pn, ch, ket in r["cap"]:
                loai, _, may = ket.partition(":")
                if loai != "doi_dung":
                    nhan = f"{pn} → {ch}" if loai != "doi_thua" else pn
                    cac[loai][nhan + (f"  (bảng: {may})" if may else "")] += 1
    return tong, cac


def _ti(x, n):
    return f"{x}/{n} ({100 * x / n:.1f} %)" if n else "—"


def bang(tong):
    ten = {"central": "Trung", "southern": "Nam", "northern": "Bắc", "tat_ca": "Tất cả"}
    dong = ["| Vùng | Câu | Chỗ thay từ (người viết lại) | Bảng đổi đúng chữ | Bảng đổi, khác chữ | "
            "Bảng bỏ qua | Bảng đổi thừa | Chỗ thêm/bớt từ | Lỗi từ so với câu chuẩn: gốc → sau chuẩn hoá |",
            "|---|---|---|---|---|---|---|---|---|"]
    for v in ("northern", "central", "southern", "tat_ca"):
        t = tong.get(v)
        if not t:
            continue
        thay = t["doi_dung"] + t["doi_khac_chu"] + t["bo_qua"]
        dong.append(f"| {ten[v]} | {t['so_cau']} | {thay} | {_ti(t['doi_dung'], thay)} | "
                    f"{_ti(t['doi_khac_chu'], thay)} | {_ti(t['bo_qua'], thay)} | {t['doi_thua']} | "
                    f"{t['them_bot']} | {_ti(t['loi_goc'], t['so_tu'])} → {_ti(t['loi_sau'], t['so_tu'])} |")
    return "\n".join(dong)


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ra", default=str(duong_dan.GOC_DU_AN / "docs" / "ket-qua" / "vidia2std-chuan-hoa.md"))
    a = ap.parse_args()
    test, _ = do_tep(THU_MUC / "test.csv")
    test_chac, _ = do_tep(THU_MUC / "test.csv", gom_can_hoi=False)
    _, cac_dev = do_tep(THU_MUC / "dev.csv")
    phan = [
        "# Bảng chuẩn hoá phương ngữ trên câu thật — ViDia2Std", "",
        "Sinh bằng `python -m src.do_vidia2std`. Đừng sửa tay. Nguồn: Ta, Dinh, Nguyen, *ViDia2Std*, "
        "AAAI-26 (2026), CC-BY-NC-4.0; bình luận Facebook do người bản ngữ viết lại sang tiếng Việt chuẩn. "
        "**Không phải hội thoại khám bệnh** — số dưới đây chỉ nói bảng chuẩn hoá phủ được bao nhiêu chỗ "
        "khác biệt phương ngữ trong tiếng Việt viết tự nhiên.", "",
        "## Tập test (1.603 câu) — bảng đầy đủ (cả mục \"cần hỏi\")", "", bang(test), "",
        "## Tập test — chỉ các mục \"chắc\"", "", bang(test_chac), "",
        "Cách đọc: *chỗ thay từ* là chỗ người viết lại đổi một hay vài từ thành từ khác (cụm cùng độ dài "
        "tách thành từng cặp một từ); *đổi, khác chữ* là bảng có đổi nhưng ra chữ khác chữ người viết lại "
        "dùng — phần lớn là từ cùng nghĩa hoặc sửa được một phần cụm, xem danh sách tập dev bên dưới; "
        "*đổi thừa* là chỗ bảng đổi nhưng người viết lại giữ nguyên; *thêm/bớt từ* (ví dụ bỏ tiểu từ cuối "
        "câu) thì phép thay từ không làm được, tính riêng. Lỗi từ = số phép sửa (thay, xoá, chèn) để thành "
        "câu chuẩn, chia cho số từ câu chuẩn.", "",
        "## Tập DEV — đọc tay (không lấy từ test)", "",
        "### Bảng có đổi nhưng khác chữ người viết lại dùng", "",
        "| Số lần | Phương ngữ → chữ người viết lại (bảng ghi) |", "|---|---|"]
    phan += [f"| {n} | {k} |" for k, n in cac_dev["doi_khac_chu"].most_common(25)]
    phan += ["", "### Bảng đổi thừa (người viết lại giữ nguyên)", "",
             "| Số lần | Chữ gốc (bảng đổi thành) |", "|---|---|"]
    phan += [f"| {n} | {k} |" for k, n in cac_dev["doi_thua"].most_common(15)]
    phan += ["", "### Cụm bảng còn bỏ qua nhiều nhất", "", "| Số lần | Phương ngữ → chuẩn |", "|---|---|"]
    phan += [f"| {n} | {k} |" for k, n in cac_dev["bo_qua"].most_common(30)]
    phan += ["", "Muốn thêm từ vào bảng thì lấy từ tập *train* của ViDia2Std và đo lại trên test; "
             "không thêm từ danh sách trên rồi đo lại trên chính tập đã nhìn."]
    Path(a.ra).write_text("\n".join(phan) + "\n", encoding="utf-8")
    Path(a.ra).with_suffix(".json").write_text(json.dumps(
        {"test": {k: dict(v) for k, v in test.items()},
         "test_chi_chac": {k: dict(v) for k, v in test_chac.items()},
         "dev": {k: v.most_common(40) for k, v in cac_dev.items()}}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print("\n".join(phan))


if __name__ == "__main__":
    main()
