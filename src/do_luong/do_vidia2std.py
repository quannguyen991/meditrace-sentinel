# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Đo bảng chuẩn hoá phương ngữ đổi đúng bao nhiêu chỗ khác biệt trên câu thật
           ViDia2Std, không phải đo hiểu lời bệnh nhân.
Vào → Ra : tệp csv ViDia2Std test và dev (biến VIDIA2STD_DIR) → bảng đúng/khác chữ/bỏ qua
           theo vùng Bắc Trung Nam, ghi markdown
Đọc từ   : do_cau() đo một cặp câu; do_tep() đo cả tệp và tổng theo vùng
Mục lục (các hàm/lớp chính):
  do_cau()  Đo bảng chuẩn hoá trên một cặp câu phương ngữ và chuẩn
  do_tep()  Đo cả tệp csv ViDia2Std, tổng theo vùng miền
  bang()    Dựng bảng markdown kết quả theo vùng Bắc Trung Nam
  main()    Chạy dòng lệnh đo trên tập test và dev rồi ghi báo cáo
Gọi tới  : duong_ong/b0_chuan_hoa_phuong_ngu, he_thong/duong_dan
Tên cũ   : do_vidia2std.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đo bảng chuẩn hóa phương ngữ (`chuan_hoa`) trên câu THẬT: bộ ViDia2Std.

VÌ SAO (24/09/2026). Bảng thay của bộ sinh (`phuong_ngu.THAY_DUOC`) và bảng chuẩn hóa
lấy từ CÙNG một từ điển do GPT sinh, nên trên dữ liệu tự sinh bảng chuẩn hóa biết trước
mọi từ phương ngữ — phép thử phương ngữ của dự án đo "hệ thống áp dụng đúng bảng của
nó", không đo "hệ thống chịu được phương ngữ thật". Bộ ViDia2Std phá vòng tròn đó:

  Ta, Dinh, Nguyen. ViDia2Std: A Parallel Corpus and Methods for Low-Resource Vietnamese
  Dialect-to-Standard Translation. AAAI-26 (2026). 13.657 cặp câu bình luận Facebook,
  63 tỉnh, người bản ngữ viết lại sang tiếng Việt chuẩn (đồng thuận 82-86 %).
  Giấy phép CC-BY-NC-4.0. Tệp lưu NGOÀI kho (biến VIDIA2STD_DIR), không phát tán lại.

GIỚI HẠN PHẢI GHI KÈM. Đây là bình luận mạng xã hội, KHÔNG phải hội thoại khám bệnh. Con
số ở đây chỉ nói bảng chuẩn hóa PHỦ được bao nhiêu chỗ khác biệt phương ngữ trong tiếng
Việt viết tự nhiên — không nói hệ thống hiểu lời bệnh nhân.

CÁCH ĐO, theo từng CHỖ KHÁC BIỆT giữa câu phương ngữ và câu chuẩn (căn hàng bằng
difflib trên từ; cụm thay CÙNG ĐỘ DÀI tách thành từng cặp một từ — "chi mô" -> "gì đâu"
là hai chỗ, vì bảng có thể sửa một và bỏ một):
  doi_dung     bảng đổi chỗ đó thành ĐÚNG chữ người viết lại dùng
  doi_khac_chu bằng đổi chỗ đó nhưng ra chữ khác. PHẦN LỚN là từ cùng nghĩa ("rứa" ->
               "vậy" khi người viết lại dùng "thế"; "chừ" -> "bây giờ" / "giờ") hoặc sửa
               được một phần cụm; SỐ ÍT sai nghĩa thật ("mệ" -> "bà" khi người viết lại
               ghi "mẹ"). Máy không tách được hai loại: báo cáo in danh sách cặp để đọc tay.
  bo_qua       bảng không động vào chỗ đó
  doi_thua     bảng đổi một chỗ mà người viết lại GIỮ NGUYÊN (chuẩn hóa quá tay)
Thêm/bớt từ (vd tiểu từ cuối câu "nả") tách riêng: phép thay từ không thể làm.

TẬP DEV ĐỂ ĐỌC TAY, TẬP TEST ĐỂ LẤY SỐ. Danh sách cặp in ra chỉ rút từ dev: nếu sau này
thêm từ vào bảng thì phải lấy từ tập train của ViDia2Std, không từ test.

    python -m src.do_luong.do_vidia2std
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

from src.duong_ong import b0_chuan_hoa_phuong_ngu as chuan_hoa
from src.he_thong import duong_dan as duong_dan

THU_MUC = Path(os.environ.get("VIDIA2STD_DIR", "D:/Claude/tai-lieu-ngoai-ban-quyen/vidia2std"))
_TU = re.compile(r"[\wÀ-ỹ]+")


# ─── _tach() — Tách câu thành từ kèm vị trí đầu cuối ──────────────────────────────────
def _tach(van):
    """-> [(từ thường, bắt đầu, kết thúc)] trên chuỗi gốc."""
    return [(m.group(0).lower(), m.start(), m.end()) for m in _TU.finditer(van or "")]


# ─── _so_loi() — Đếm số phép sửa từ để biến chuỗi này thành chuỗi kia ─────────────────
# Tính khoảng cách chỉnh sửa theo từ: thay, xoá, chèn.
def _so_loi(a, b):
    """Số phép sửa (thay + xóa + chèn) để biến dãy từ `a` thành `b`."""
    n, m = len(a), len(b)
    d = list(range(m + 1))
    for i in range(1, n + 1):
        truoc, d[0] = d[0], i
        for j in range(1, m + 1):
            tam = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, truoc + (a[i - 1] != b[j - 1]))
            truoc = tam
    return d[m]


# ─── _don_vi() — Tìm các chỗ khác biệt giữa câu phương ngữ và câu chuẩn ───────────────
# Chỗ cùng độ dài tách thành từng cặp một từ; trả thêm số chỗ chỉ thêm hoặc bớt từ.
def _don_vi(tp, tc):
    """Các chỗ khác biệt -> [(i1, i2, j1, j2)] và số chỗ thêm/bớt từ."""
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


# ═══ do_cau() — Đo bảng chuẩn hoá trên một cặp câu phương ngữ và chuẩn ════════════════
# Đếm chỗ đổi đúng chữ, khác chữ, bị bỏ qua, đổi thừa, và lỗi từ trước sau chuẩn hoá.
def do_cau(phuong_ngu, chuan, gom_can_hoi=True):
    """-> {"doi_dung", "doi_khac_chu", "bo_qua", "them_bot", "doi_thua", "loi_goc",
    "loi_sau", "so_tu", "cap": [(cụm phương ngữ, cụm chuẩn, kết quả)]} cho MỘT cặp câu."""
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
        # Áp các chỗ đổi nằm trong đoạn lên chính đoạn đó, rồi so với chữ người viết lại.
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
    # Chỗ bảng đổi mà người viết lại giữ nguyên: nằm trọn trong một đoạn "equal".
    thua = [c for c in cho if id(c) not in dung_cho]
    kq["doi_thua"] = len(thua)
    cap += [(c.goc.lower(), c.goc.lower(), f"doi_thua:{c.nghia.lower()}") for c in thua]
    sau = [t for t, _, _ in _tach(chuan_hoa.chuan_hoa(phuong_ngu, gom_can_hoi))]
    kq["loi_goc"] = _so_loi([t for t, _, _ in tp], tc)
    kq["loi_sau"] = _so_loi(sau, tc)
    kq["so_tu"] = len(tc)
    return {**kq, "cap": cap}


# ═══ do_tep() — Đo cả tệp csv ViDia2Std, tổng theo vùng miền ══════════════════════════
# Trả tổng theo vùng và danh sách cặp đổi chưa đúng theo từng loại.
def do_tep(tep, gom_can_hoi=True):
    """-> (tổng theo vùng, {loại: Counter cặp}) — loại: bo_qua / doi_khac_chu / doi_thua."""
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


# ─── _ti() — Định dạng tỉ lệ x trên n kèm phần trăm ───────────────────────────────────
def _ti(x, n):
    return f"{x}/{n} ({100 * x / n:.1f} %)" if n else "—"


# ═══ bang() — Dựng bảng markdown kết quả theo vùng Bắc Trung Nam ══════════════════════
# Cột gồm số câu, chỗ đổi đúng, khác chữ, bỏ qua, đổi thừa và lỗi từ.
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


# ═══ main() — Chạy dòng lệnh đo trên tập test và dev rồi ghi báo cáo ══════════════════
# Ghi bảng markdown và JSON; tập dev chỉ để đọc tay, không dùng để chỉnh rồi đo lại trên
# test.
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
        "Sinh bằng `python -m src.do_luong.do_vidia2std`. Đừng sửa tay. Nguồn: Ta, Dinh, Nguyen, *ViDia2Std*, "
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
