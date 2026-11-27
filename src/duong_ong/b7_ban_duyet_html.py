# -*- coding: utf-8 -*-
"""[Đường ống dựng bản nháp › Bước 7 – Bản duyệt]
Làm gì   : Dựng trang duyệt ba cột (lời thoại, mệnh đề, bản nháp) thành một tệp HTML tự
           chứa, bấm dòng nào tô đoạn lời thoại dẫn của dòng đó.
Vào → Ra : tệp kết quả jsonl của một nhánh (hoặc ca minh hoạ) → một tệp HTML duyệt bản nháp
Đọc từ   : dung_trang() dựng trang HTML từ dữ liệu; ca_cho_trang() gọn một bản ghi thành dữ
           liệu cho trang; main() là lối vào
Mục lục (các hàm/lớp chính):
  minh_hoa()       Tạo dữ liệu minh hoạ từ ca khuôn train
  du_lieu_trang()  Gom dữ liệu các ca thành gói cho trang duyệt
  dung_trang()     Dựng trang HTML duyệt bản nháp từ mẫu
  ca_cho_trang()   Gọn một bản ghi của nhánh thành dữ liệu cho trang
  main()           Điểm vào dòng lệnh dựng trang duyệt
Gọi tới  : bo_du_lieu/du_lieu_huan_luyen_trich, bo_du_lieu/nap_du_lieu,
           bo_du_lieu/sinh_hoi_thoai_viet, duong_ong/b4_kiem_can_cu,
           duong_ong/b5_viet_ban_nhap, duong_ong/chay_duong_ong, he_thong/duong_dan
Tên cũ   : giao_dien_duyet.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Tầng 7 — BẢN DUYỆT 3 cột: một tệp HTML tự chứa, mở bằng trình duyệt là chạy.

    hội thoại              bản nháp bệnh án             chi tiết + quyết định
    (tô đậm đoạn được dẫn)  (mỗi dòng là một phát biểu)  (khoá, rủi ro, lịch sử)

Bấm một dòng -> tô đậm ĐÚNG đoạn hội thoại mà dòng đó dựa vào. Vị trí lấy từ
chính tầng khoá (`khoa_bang_chung`, vị trí trên lượt đã chuẩn NFC), không tìm lại
bằng chuỗi ở trình duyệt — hai nơi tìm hai kiểu thì tô đậm lệch mà không ai biết.

Người duyệt Xác nhận / Sửa / Loại từng dòng. Quyết định lưu trong localStorage của
máy đó (mỗi máy một kho riêng) và xuất được thành JSON — để thành dữ liệu phản hồi.

THỜI GIAN DUYỆT: trang đo trên máy đang mở, để thử giao diện. CHƯA CÓ số liệu bác
sĩ thật; không được báo cáo con số đó như kết quả.

    python -m src.duong_ong.b7_ban_duyet_html --tep data/ra_C_khoa_hoi_viet_phat_trien.jsonl --n 20
    python -m src.duong_ong.b7_ban_duyet_html --minh-hoa
"""
import argparse
import hashlib
import io
import json
import random
import sys
from pathlib import Path

from src.he_thong import duong_dan as duong_dan
from src.duong_ong import b4_kiem_can_cu as khoa_bang_chung
from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an

MAU = Path(__file__).with_name("ban_duyet_mau.html")
DAU_THAN = "<!--THAN-->"
GHI_CHU_MINH_HOA = ("Đáp án bộ tự sinh qua đúng đường ống, có cấy lỗi có chủ đích. "
                    "Không phải đầu ra mô hình.")
TRUONG_GON = ("noi_dung", "chu_the_id", "ten_chu_the", "nguoi_noi", "do_chac_chan",
              "phu_dinh", "tinh_huong", "moc_thoi_gian", "thoi_gian_su_kien",
              "trang_thai", "quan_he", "quan_he_voi", "bang_chung", "trich_dan",
              "hanh_vi")


# ─── _vi_tri_trich() — Tìm vị trí câu trích cho nhánh không chạy khoá ─────────────────
# Dùng chính hàm của bước kiểm căn cứ; trả về các đoạn (lượt, đầu, cuối).
def _vi_tri_trich(p, cac_luot):
    """Nhánh KHÔNG chạy khoá (B, C): tìm vị trí trích dẫn bằng CHÍNH hàm của khoá."""
    doan = []
    bc = [n for n in (p.get("bang_chung") or []) if n in cac_luot]
    for t in p.get("trich_dan") or []:
        for n in bc + [s for s in cac_luot if s not in bc]:
            vt = khoa_bang_chung.tim_trich(t, cac_luot[n][1])
            if vt:
                doan.append([n, vt[0], vt[1]])
                break
    return doan


# ═══ ca_cho_trang() — Gọn một bản ghi của nhánh thành dữ liệu cho trang ═══════════════
# Gồm mệnh đề, kết quả khoá và vị trí căn cứ của ca.
def ca_cho_trang(r) -> dict:
    """Một bản ghi của nhánh (C_khoa_hoi, C_khoa, C...) -> dữ liệu gọn cho trang."""
    cac_luot = khoa_bang_chung._luot(r["input"])     # CÙNG bản với vị trí của khoá
    ps = {p["id"]: p for p in r.get("phat_bieu") or []}
    khoa = {}
    for k in r.get("khoa") or []:
        khoa[k["id"]] = {"chan": k.get("chan", []), "canh_bao": k.get("canh_bao", []),
                         "doan": [list(x) for x in k.get("doan", [])]}
    for pid, p in ps.items():
        if pid not in khoa:
            khoa[pid] = {"chan": [], "canh_bao": [], "doan": _vi_tri_trich(p, cac_luot),
                         "khong_co_khoa": True}
    dong = []
    for g in r.get("ghi_chu") or []:
        van = g.get("van")
        if not van:
            p = ps.get(g["id"])
            van = sinh_benh_an.dien_dat(p) if p else g.get("noi_dung", "")
        dong.append({"id": g["id"], "muc": g["muc"], "ly_do": g.get("ly_do"), "van": van})
    return {
        "id": r["id"],
        "luot": [[n, vai, van] for n, (vai, van) in sorted(cac_luot.items())],
        "dong": dong,
        "phat_bieu": {str(k): {t: v.get(t) for t in TRUONG_GON} for k, v in ps.items()},
        "khoa": {str(k): v for k, v in khoa.items()},
        "rui_ro": {str(d["id"]): d for d in r.get("rui_ro") or []},
        "chua_ghi": [{"luot": d["luot"], "a": d["bat_dau"], "b": d["ket_thuc"],
                      "doan": d["doan"]} for d in r.get("doan_chua_ghi") or []],
        "cau_hoi": [{"van": c["van"], "ly_do": c["ly_do"],
                     "muc_tieu": [int(x) for x in c.get("muc_tieu", {})]}
                    for c in r.get("cau_hoi") or []],
        "lich_su": r.get("lich_su") or [],
    }


# ═══ du_lieu_trang() — Gom dữ liệu các ca thành gói cho trang duyệt ═══════════════════
# Gắn mã 12 ký tự sinh từ nội dung để quyết định cũ không bị đọc nhầm sang bộ khác.
def du_lieu_trang(ban_ghi, ten_bo, minh_hoa=False, ghi_chu_nguon=""):
    dl = {"ten_bo": ten_bo, "minh_hoa": minh_hoa, "ghi_chu_nguon": ghi_chu_nguon,
          "ly_do": khoa_bang_chung.LY_DO, "thu_tu_muc": sinh_benh_an.THU_TU_MUC,
          "ca": [ca_cho_trang(r) for r in ban_ghi]}
    # Mã của BỘ DỮ LIỆU: quyết định lưu theo mã này, nên trang sinh từ bộ khác
    # không đọc nhầm quyết định cũ.
    dl["ma"] = hashlib.sha256(json.dumps(dl, ensure_ascii=False, sort_keys=True)
                              .encode("utf-8")).hexdigest()[:12]
    return dl


# ═══ dung_trang() — Dựng trang HTML duyệt bản nháp từ mẫu ═════════════════════════════
# Nhúng dữ liệu JSON vào mẫu; có thể ra tệp đầy đủ hoặc chỉ phần nội dung.
def dung_trang(dl, tu_chua=True) -> str:
    """`tu_chua=True`: tệp HTML đầy đủ để mở từ máy. False: chỉ phần nội dung (cho
    nơi nào tự bọc khung html/head/body)."""
    mau = MAU.read_text(encoding="utf-8")
    dau, than = mau.split(DAU_THAN)
    # Bản không tự chứa được nhúng vào nơi khác, thường cắm tại tệp: ẩn nút tải.
    dl = dict(dl, cho_tai=tu_chua)
    # "</" trong JSON sẽ đóng thẻ <script> sớm — JSON cho phép viết "<\/".
    js = json.dumps(dl, ensure_ascii=False).replace("</", "<\\/")
    than = than.replace("__DU_LIEU__", js)
    if not tu_chua:
        return dau + than
    return ('<!doctype html>\n<html lang="vi">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            + dau + "</head>\n<body>\n" + than + "</body>\n</html>\n")


# ─── _cay_loi() — Cấy lỗi có tên vào đáp án để minh hoạ ───────────────────────────────
# Ba loại lỗi cấy trước khi qua đường ống; loại 3 và 4 để sạch.
# ------------------------------------------------------------------ minh họa
def _cay_loi(ps, loai, rng):
    """Ba lỗi có tên, cấy vào ĐÁP ÁN trước khi qua đường ống; loại 3 và 4 để sạch."""
    if loai == 0:                                  # đổi chủ thể
        ung = [p for p in ps if p["chu_the"] != "bệnh nhân" and "dị ứng" in p["noi_dung"]]
        ung = ung or [p for p in ps if p["chu_the"] != "bệnh nhân"]
        if ung:
            rng.choice(ung)["chu_the"] = "bệnh nhân"
    elif loai == 1:                                # nâng mức khẳng định
        ung = [p for p in ps if p.get("do_chac_chan") == "nghi ngờ"]
        if ung:
            rng.choice(ung)["do_chac_chan"] = "chắc chắn"
    elif loai == 2:                                # bịa trích dẫn
        ung = [p for p in ps if p.get("trich_dan")]
        if ung:
            p = rng.choice(ung)
            p["trich_dan"] = [f"{p['noi_dung']} từ tuần trước"]


# ═══ minh_hoa() — Tạo dữ liệu minh hoạ từ ca khuôn train ══════════════════════════════
# Đáp án đã cấy lỗi chạy qua đúng đường ống C_khoa_hoi; không phải đầu ra mô hình.
def minh_hoa(so_ca=10, hat=11):
    """MINH HỌA, KHÔNG phải đầu ra mô hình: đáp án của `so_ca` ca KHUÔN TRAIN đi qua
    ĐÚNG đường ống C_khoa_hoi (`nhanh.chay_trung_gian`), có cấy lỗi có chủ định."""
    from src.bo_du_lieu import du_lieu_huan_luyen_trich as du_lieu_trich
    from src.duong_ong import chay_duong_ong as nhanh
    from src.bo_du_lieu import sinh_hoi_thoai_viet as sh
    tuy = [sh.TuyChon(chi_tap="train", ep_bay=("di_ung_nguoi_nha",), ep_nguoi_ke=True,
                      di_ung_cua_nguoi_ke=True),
           sh.TuyChon(chi_tap="train"),
           sh.TuyChon(chi_tap="train"),
           sh.TuyChon(chi_tap="train", ep_bay=("nguon_khac_nhau",), ep_nguoi_ke=True),
           sh.TuyChon(chi_tap="train", ep_bay=("dinh_chinh",))]
    rng = random.Random(hat)
    cases, kq_tho = [], []
    for i in range(so_ca):
        ca = sh.sinh_mot_ca(f"minh_hoa_{i + 1:02d}", random.Random(hat * 1000 + i),
                            tuy[i % len(tuy)])
        _ds, js = du_lieu_trich.doi_mot_ca(ca)
        ps = json.loads(js)["phat_bieu"]
        _cay_loi(ps, i % len(tuy), rng)
        cases.append(ca)
        kq_tho.append({"id": ca["id"], "phat_bieu": ps})
    return nhanh.chay_trung_gian(cases, None, None, None, "C_khoa_hoi", kq_tho=kq_tho)


# ═══ main() — Điểm vào dòng lệnh dựng trang duyệt ═════════════════════════════════════
# Đọc tệp kết quả hoặc dùng chế độ minh hoạ, rồi ghi ra tệp HTML.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tep", help="data/ra_<nhanh>_<tap>.jsonl")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--minh-hoa", action="store_true")
    ap.add_argument("--chi-noi-dung", action="store_true",
                    help="bo khung html/head/body")
    ap.add_argument("--ra", default=None)
    a = ap.parse_args()
    if a.minh_hoa:
        dl = du_lieu_trang(minh_hoa(), "minh hoạ", minh_hoa=True,
                           ghi_chu_nguon=GHI_CHU_MINH_HOA)
        ra = Path(a.ra) if a.ra else duong_dan.THU_MUC_KET_QUA / "ban-duyet-minh-hoa.html"
    elif a.tep:
        from src.bo_du_lieu import nap_du_lieu as du_lieu
        tep = Path(a.tep)
        du_lieu.chan_tap_khoa(tep.name)
        dl = du_lieu_trang(du_lieu.nap_mau(tep)[:a.n], tep.stem,
                           ghi_chu_nguon=f"Đầu ra của đường ống — {tep.name}")
        ra = Path(a.ra) if a.ra else duong_dan.THU_MUC_KET_QUA / f"ban-duyet-{tep.stem}.html"
    else:
        raise SystemExit("can --tep <ra_...jsonl> hoac --minh-hoa")
    ra.write_text(dung_trang(dl, tu_chua=not a.chi_noi_dung), encoding="utf-8")
    print(f"Ghi {len(dl['ca'])} ca -> {ra}")


if __name__ == "__main__":
    main()
