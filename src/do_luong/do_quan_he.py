# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Đo phát hiện quan hệ bằng bốn số đúng, thừa, sót, nhầm loại thay vì một số, so
           với đáp án cấu trúc.
Vào → Ra : kết quả mô hình trên tập (--tap) và đáp án → số đúng/thừa/sót/nhầm loại của quan
           hệ và tình huống, ghi JSON
Đọc từ   : do() đếm bốn số cho quan hệ; do_tinh_huong() đếm cho trường tình huống
Mục lục (các hàm/lớp chính):
  do()             Đếm đúng, thừa, sót, nhầm loại của quan hệ
  do_tinh_huong()  Đo đúng, thừa, sót cho trường tình huống
  main()           Chạy dòng lệnh đo quan hệ trên một tập rồi ghi kết quả
Gọi tới  : bo_du_lieu/nap_du_lieu, he_thong/duong_dan, huan_luyen/chon_mo_hinh_bakeoff
Tên cũ   : do_quan_he.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đo CHẤT LƯỢNG phát hiện quan hệ, đối chiếu với đáp án cấu trúc.

VÌ SAO CÓ TỆP NÀY (10/09/2026).

Con số `quan_he` = "khong" ở 282/282 trên bộ tham chiếu ngoài đã bị giải thích
SAI HAI LẦN, và lần nào cũng nghe hợp lý:

  lần 1  "khâu trích không nhận ra quan hệ trên hội thoại dài"
         -> bác bỏ bởi: bước phân từng cặp chỉ sinh 2 cặp ứng viên

  lần 2  "bỏ nhãn huấn luyện không có ví dụ dương nên mô hình học sai"
         -> bác bỏ bởi: chính MÔ HÌNH NỀN, không adapter, không học gì cả,
            vẫn đánh dấu 20 quan hệ trên bộ tự sinh

Cái chung của hai lần: đếm MỘT con số rồi rút một nguyên nhân. Tệp này đếm BỐN
con số — đúng, thừa, sót, và nhầm loại — để lần sau không làm thế nữa.

    python -m src.do_luong.do_quan_he --tap viet_phat_trien
"""
import argparse
import io
import json
import sys
from collections import Counter

from src.he_thong import duong_dan as duong_dan


# ─── _khoa() — Tạo khoá ghép mệnh đề từ chủ thể và nội dung ───────────────────────────
def _khoa(m):
    """Khoá ghép một mệnh đề: chủ thể + nội dung đã chuẩn hoá thô."""
    return (str(m.get("chu_the", "")).strip().lower(),
            " ".join(str(m.get("noi_dung", "")).lower().split()))


# ─── _cap_dung() — Lấy các cặp quan hệ đúng từ đáp án một ca ──────────────────────────
# Trả {(nguồn, đích): loại quan hệ}; bỏ qua chỉ số đích không hợp lệ.
def _cap_dung(ca):
    """Tập cặp quan hệ ĐÚNG của một ca -> {(khoa_nguon, khoa_dich): loai}."""
    dap_an = ca["dap_an"]
    ra = {}
    for m in dap_an:
        if not m.get("quan_he"):
            continue
        j = m.get("quan_he_voi")
        if j is None or not (0 <= j < len(dap_an)):
            continue
        ra[(_khoa(m), _khoa(dap_an[j]))] = m["quan_he"]
    return ra


# ─── _cap_du_doan() — Lấy các cặp quan hệ dự đoán từ đầu ra trích ─────────────────────
# Bỏ quan hệ "không", chỉ số sai và quan hệ trỏ về chính nó.
def _cap_du_doan(k):
    """Tập cặp quan hệ DỰ ĐOÁN từ đầu ra trích -> {(khoa_nguon, khoa_dich): loai}."""
    ps = k.get("phat_bieu") or []
    ra = {}
    for i, p in enumerate(ps):
        qh = p.get("quan_he")
        if not qh or qh == "không":
            continue
        j = p.get("quan_he_voi")
        if j is None or not isinstance(j, int) or not (0 <= j < len(ps)) or j == i:
            continue
        ra[(_khoa(p), _khoa(ps[j]))] = qh
    return ra


# ═══ do() — Đếm đúng, thừa, sót, nhầm loại của quan hệ ════════════════════════════════
# Đếm bốn nhóm riêng, không gộp thành một tỉ lệ; tính độ phủ và độ chuẩn.
def do(mau_theo_id, tho):
    """-> thống kê. Đếm BỐN nhóm, không gộp lại thành một tỷ lệ."""
    dung = thua = sot = nham_loai = 0
    theo_loai_dung = Counter()
    theo_loai_du_doan = Counter()
    theo_loai_that = Counter()
    ca_co_quan_he_that = ca_co_du_doan = 0

    for k in tho:
        ca = mau_theo_id.get(k["id"])
        if ca is None:
            continue
        that = _cap_dung(ca)
        du = _cap_du_doan(k)
        ca_co_quan_he_that += bool(that)
        ca_co_du_doan += bool(du)
        for loai in that.values():
            theo_loai_that[loai] += 1
        for loai in du.values():
            theo_loai_du_doan[loai] += 1

        for cap, loai_that in that.items():
            if cap not in du:
                sot += 1
            elif du[cap] == loai_that:
                dung += 1
                theo_loai_dung[loai_that] += 1
            else:
                nham_loai += 1
        for cap in du:
            if cap not in that:
                thua += 1

    tong_that = dung + sot + nham_loai
    tong_du = dung + thua + nham_loai
    return {
        "so_ca": len(tho),
        "ca_co_quan_he_that": ca_co_quan_he_that,
        "ca_co_du_doan": ca_co_du_doan,
        "dung": dung, "thua": thua, "sot": sot, "nham_loai": nham_loai,
        "do_phu": dung / tong_that if tong_that else None,
        "do_chuan": dung / tong_du if tong_du else None,
        "theo_loai_that": dict(theo_loai_that),
        "theo_loai_du_doan": dict(theo_loai_du_doan),
        "theo_loai_dung": dict(theo_loai_dung),
    }


# ═══ do_tinh_huong() — Đo đúng, thừa, sót cho trường tình huống ═══════════════════════
# Cùng cách đếm nhưng trên mệnh đề có tình huống giả định, không xét theo cặp.
def do_tinh_huong(mau_theo_id, tho, gia_tri="giả định"):
    """Cùng cách đếm, cho trường `tinh_huong`. Một trường đơn, không phải cặp."""
    dung = thua = sot = 0
    for k in tho:
        ca = mau_theo_id.get(k["id"])
        if ca is None:
            continue
        that = {_khoa(m) for m in ca["dap_an"] if m.get("tinh_huong") == gia_tri}
        du = {_khoa(p) for p in (k.get("phat_bieu") or [])
              if p.get("tinh_huong") == gia_tri}
        dung += len(that & du)
        sot += len(that - du)
        thua += len(du - that)
    return {"gia_tri": gia_tri, "dung": dung, "thua": thua, "sot": sot,
            "do_phu": dung / (dung + sot) if (dung + sot) else None,
            "do_chuan": dung / (dung + thua) if (dung + thua) else None}


# ─── _in() — In kết quả đo quan hệ ra màn hình ────────────────────────────────────────
def _in(tk, ten):
    print(f"\n=== {ten} ===")
    print(f"  ca co quan he that : {tk['ca_co_quan_he_that']}/{tk['so_ca']}")
    print(f"  ca co du doan      : {tk['ca_co_du_doan']}/{tk['so_ca']}")
    print(f"  dung      {tk['dung']:4d}")
    print(f"  thieu     {tk['sot']:4d}   (co that ma khong bat duoc)")
    print(f"  thua      {tk['thua']:4d}   (bat ra ma khong co that)")
    print(f"  nham loai {tk['nham_loai']:4d}   (dung cap, sai loai quan he)")
    dp, dc = tk["do_phu"], tk["do_chuan"]
    print(f"  do phu    {dp:.3f}" if dp is not None else "  do phu    —")
    print(f"  do chuan  {dc:.3f}" if dc is not None else "  do chuan  —")
    print(f"  that     : {tk['theo_loai_that']}")
    print(f"  du doan  : {tk['theo_loai_du_doan']}")
    print(f"  dung theo loai: {tk['theo_loai_dung']}")


# ═══ main() — Chạy dòng lệnh đo quan hệ trên một tập rồi ghi kết quả ══════════════════
# Đọc tệp đệm kết quả trích, kiểm khớp với bộ dữ liệu, rồi ghi JSON kết quả.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--max-token", type=int, default=3072)
    ap.add_argument("--adapter-trich", action="store_true",
                    help="doc tep dem cua ban da huan luyen (hau to _hl)")
    a = ap.parse_args()

    from src.bo_du_lieu import nap_du_lieu as _dl
    _dl.chan_tap_ngoai(a.tap)
    _dl.chan_tap_khoa(a.tap)

    d = duong_dan.THU_MUC_DU_LIEU
    mau = {json.loads(x)["id"]: json.loads(x)
           for x in open(d / f"{a.tap}.jsonl", encoding="utf-8") if x.strip()}
    hau = "_hl" if a.adapter_trich else ""
    dem = d / f"trich_{a.tap}_{a.max_token}{hau}.jsonl"
    if not dem.exists():
        raise SystemExit(f"chua co {dem}")
    tho = [json.loads(x) for x in open(dem, encoding="utf-8") if x.strip()]

    # Tệp đếm có đúng là của bộ dữ liệu này không. Xem bakeoff.kiem_khop —
    # không có phép kiểm này thì một lần sinh lại dữ liệu là đủ để mọi con số
    # sau đó vô nghĩa mà không có gì báo.
    from src.huan_luyen import chon_mo_hinh_bakeoff as _bk
    _bk.kiem_khop(mau, tho, dem.name)

    tk = do(mau, tho)
    _in(tk, f"QUAN HE — {a.tap}{hau}")
    tk_gd = do_tinh_huong(mau, tho)
    print(f"\n=== TINH HUONG 'gia dinh' — {a.tap}{hau} ===")
    print(f"  dung {tk_gd['dung']}   thieu {tk_gd['sot']}   thua {tk_gd['thua']}")
    dp, dc = tk_gd["do_phu"], tk_gd["do_chuan"]
    print(f"  do phu {dp:.3f}" if dp is not None else "  do phu —",
          f"  do chuan {dc:.3f}" if dc is not None else "  do chuan —")

    ra = {"tap": a.tap, "adapter_trich": a.adapter_trich,
          "quan_he": tk, "tinh_huong_gia_dinh": tk_gd}
    dp2 = duong_dan.THU_MUC_KET_QUA / f"quan-he-{a.tap}{hau}.json"
    dp2.write_text(json.dumps(ra, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nda ghi {dp2}")


if __name__ == "__main__":
    main()
