# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Đo lớp cảnh báo báo đúng bao nhiêu và bắt được bao nhiêu lỗi so với bộ chấm tự
           động, so chính sách C với D trên tập phát triển.
Vào → Ra : đầu ra các nhánh trên bốn bộ thử thách (--thu-muc, --nhanh) → độ chính xác, độ
           phủ từng mã cảnh báo, JSON
Đọc từ   : chay() đo cảnh báo trên các bộ thử thách; main() ghi JSON và nhật ký
Mục lục (các hàm/lớp chính):
  cac_tap()  Liệt kê tập thử thách có đầu ra nhánh
  chay()     Đo lớp cảnh báo trên các bộ thử thách
  main()     Chạy dòng lệnh đo cảnh báo, ghi JSON và nhật ký
Gọi tới  : do_luong/cham_he_thong, bo_du_lieu/nap_du_lieu, duong_ong/b1_cau_truc_menh_de,
           duong_ong/b5_viet_ban_nhap, duong_ong/b5_xep_cho_cong_rui_ro, he_thong/duong_dan
Tên cũ   : do_canh_bao.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đo lớp cảnh báo trên bốn bộ thử thách (TẬP PHÁT TRIỂN), so với BỘ CHẤM TỰ ĐỘNG.

NHÃN DÙNG ĐỂ ĐO là mã lỗi của `cham_he_thong.loi_phat_bieu` — bộ chấm tự động,
KHÔNG phải nhãn người. Bộ chấm có giới hạn đã biết (xem memory/báo cáo): `khong_can_cu`
bị thổi phồng vì ngưỡng ghép 0,6 — một phát biểu diễn đạt khác đáp án bị tính là
"không căn cứ". Nên:
  - độ chính xác của bộ phát hiện nhóm UNSUPPORTED sẽ THẤP GIẢ
  - mỗi con số ở đây là "so với bộ chấm tự động", phải ghi đúng như vậy khi báo cáo

THĂM DÒ, KHÔNG PHẢI KIỂM ĐỊNH. Lớp cảnh báo viết SAU đăng ký trước (dang-ky-truoc.md);
chạy trên tập phát triển, không chấm tập kiểm tra cuối. Ngưỡng và luật của lớp này đã
được sửa khi nhìn các ca phát triển (vd dct_019_B), nên số ở đây là số trên dữ liệu
đã nhìn — cần một tập mới để đo không thiên lệch.

Hai câu hỏi:
  1. Từng mã cảnh báo: báo đúng bao nhiêu (precision), bắt được bao nhiêu lỗi cùng
     loại (recall), so với bộ chấm.
  2. Chính sách C (đang dùng) vs D (mới): LỌT = phát biểu có lỗi nguy hiểm mà vẫn
     vào thân; CHẶN THỪA = phát biểu không lỗi bị đưa sang cần xác nhận.

    python -m src.do_luong.do_canh_bao
"""
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from src.do_luong import cham_he_thong as cham_he_thong
from src.duong_ong import b5_xep_cho_cong_rui_ro as cong_rui_ro
from src.he_thong import duong_dan as duong_dan
from src.bo_du_lieu import nap_du_lieu as du_lieu
from src.duong_ong import b5_viet_ban_nhap as sinh_benh_an
from src.canh_bao import gop, nhat_ky
from src.canh_bao.loai import LOAI, PHIEN_BAN
from src.duong_ong.b1_cau_truc_menh_de import PhatBieu

THU_MUC = duong_dan.GOC_DU_AN / "data" / "thach_thuc"
NHANH = "C_khoa"


# ═══ cac_tap() — Liệt kê tập thử thách có đầu ra nhánh ════════════════════════════════
# Bỏ tập kiểm tra cuối; báo lỗi nếu không có tập nào.
def cac_tap(thu_muc, nhanh=NHANH):
    """Tên các tập trong thư mục có cả tệp gốc `<tap>.jsonl` lần đầu ra `ra_<nhanh>_<tap>.jsonl`.
    Tập kiểm tra cuối (`*_kiem_tra*`) bị bỏ qua: không được mở trước Giai đoạn 5."""
    thu_muc = Path(thu_muc)
    ra = sorted(p.stem for p in thu_muc.glob("thach_thuc_*.jsonl")
                if "kiem_tra" not in p.stem and (thu_muc / f"ra_{nhanh}_{p.stem}.jsonl").exists())
    if not ra:
        raise FileNotFoundError(f"khong co tap nao kem dau ra ra_{nhanh}_* trong {thu_muc}")
    return ra

# Nhóm cảnh báo -> mã lỗi của bộ chấm cùng loại. Nhóm không có mã tương ứng (bỏ sót,
# chất lượng, chép âm, quan hệ) không tính recall theo loại.
NHOM_SANG_MA = {
    "SUBJECT_ATTRIBUTION": {"sai_chu_the"},
    "NEGATION_ASSERTION": {"sai_muc_phu_dinh", "sai_muc_chac_chan"},
    "PLAN_FACT_CONDITIONAL": {"sai_muc_tinh_huong"},
    "STATE_UPDATE": {"ban_cu", "sai_muc"},
    "UNSUPPORTED": {"khong_can_cu"},
    "EVIDENCE_PROVENANCE": {"khong_can_cu"},
    "ENTITY_VALUE": {"sai_thuoc", "sai_thoi_gian", "khong_can_cu"},
    "TEMPORAL": {"sai_thoi_gian", "sai_thuoc", "ban_cu"},
    "QUALITY": {"trung_lap"},
    "RELATION_CAUSALITY": set(cham_he_thong.LOI),
}
LOI_THAT = set(cham_he_thong.LOI)          # không tính trung_lap là lỗi
NGUY_HIEM = cham_he_thong.LOAI_NGHIEM_TRONG  # di_ung, thuoc, chan_doan


# ─── _p() — Làm tròn 3 chữ số, NaN thành None ─────────────────────────────────────────
def _p(x):
    return round(x, 3) if x == x else None


# ═══ chay() — Đo lớp cảnh báo trên các bộ thử thách ═══════════════════════════════════
# Thống kê theo mã cảnh báo: độ chính xác, độ phủ lỗi, bỏ sót, hai chính sách C và D.
def chay(thu_muc=THU_MUC, nhanh=NHANH):
    thu_muc = Path(thu_muc)
    tap_list = cac_tap(thu_muc, nhanh)
    thong_ke_ma = defaultdict(lambda: Counter())       # mã -> {ban, dung_loai, co_loi}
    recall = defaultdict(lambda: Counter())            # mã bộ chấm -> {tong, co_canh_bao_cung_loai, co_canh_bao}
    chinh_sach = {k: Counter() for k in ("C", "D")}
    so_hien, so_pb = [], 0
    nhat = []
    bo_sot = Counter()
    for tap in tap_list:
        goc = {c["id"]: c for c in du_lieu.nap_mau(thu_muc / f"{tap}.jsonl")}
        for r in du_lieu.nap_mau(thu_muc / f"ra_{nhanh}_{tap}.jsonl"):
            ca = goc[r["id"]]
            ps = [PhatBieu(**d) for d in r["phat_bieu"]]
            loi, sot = cham_he_thong.loi_phat_bieu(ca, r["phat_bieu"])
            kq = gop.chay(ps, r["input"])
            muc_c = {g["id"]: g["muc"] for g in r.get("ghi_chu", [])}
            nhan_nhat = {}
            for p in ps:
                if p.trang_thai == "bị thay thế":
                    continue
                so_pb += 1
                ma_loi, loai = loi.get(p.id, ([], cong_rui_ro.loai_thong_tin(p)))
                co_loi = bool(set(ma_loi) & LOI_THAT)
                v = kq["theo_phat_bieu"][p.id]
                so_hien.append(int(v["chinh"] is not None) + len(v["khac"]))
                for c in v["tat_ca"]:
                    dung_loai = bool(set(ma_loi) & NHOM_SANG_MA.get(c.nhom, set()))
                    t = thong_ke_ma[c.ma]
                    t["ban"] += 1
                    t["dung_loai"] += dung_loai
                    t["co_loi"] += co_loi
                    t["doi_trang_thai"] += c.anh_huong_trang_thai
                    nhan_nhat[(p.id, c.ma)] = dung_loai
                nhom_bao = {c.nhom for c in v["tat_ca"]}
                for m in set(ma_loi) & (LOI_THAT | {"sai_muc_phu_dinh", "sai_muc_chac_chan", "sai_muc_tinh_huong"}):
                    recall[m]["tong"] += 1
                    recall[m]["co_canh_bao"] += bool(v["tat_ca"])
                    recall[m]["cung_loai"] += any(m in NHOM_SANG_MA.get(n, set()) for n in nhom_bao)
                # chính sách: vào thân hay cần xác nhận
                vao_c = muc_c.get(p.id) not in sinh_benh_an.MUC_PHU_TAT_CA and p.id in muc_c
                vao_d = kq["trang_thai_D"][p.id]["trang_thai"] == gop.DA_KIEM_CHUNG
                for ten, vao in (("C", vao_c), ("D", vao_d)):
                    k = chinh_sach[ten]
                    k["tong"] += 1
                    k["co_loi"] += co_loi
                    k["vao_than"] += vao
                    if co_loi and vao:
                        k["lot"] += 1
                        if loai in NGUY_HIEM:
                            k["lot_nguy_hiem"] += 1
                    if co_loi and loai in NGUY_HIEM:
                        k["loi_nguy_hiem"] += 1
                    if not co_loi and not vao:
                        k["chan_thua"] += 1
                    if not co_loi:
                        k["khong_loi"] += 1
            # bỏ sót: cảnh báo toàn ca có chấm đúng lượt của mệnh đề đáp án bị sót không
            luot_sot = [set(d.get("luot") or []) for d in sot]
            luot_cb = [set(c.luot) for c in kq["toan_ca"]]
            bo_sot["dap_an_sot"] += len(luot_sot)
            bo_sot["sot_co_canh_bao"] += sum(any(a & b for b in luot_cb) for a in luot_sot)
            bo_sot["canh_bao"] += len(luot_cb)
            bo_sot["canh_bao_trung_sot"] += sum(any(a & b for b in luot_sot) for a in luot_cb)
            nhat += nhat_ky.dong(f"{tap}/{r['id']}", kq, nhan_nhat)

    bang_ma = []
    for ma, t in sorted(thong_ke_ma.items(), key=lambda x: -x[1]["ban"]):
        bang_ma.append({"ma": ma, "nhom": LOAI[ma].nhom, "tin_cay": LOAI[ma].tin_cay, "so_lan_bao": t["ban"],
                        "chinh_xac_cung_loai": _p(t["dung_loai"] / t["ban"]),
                        "chinh_xac_co_loi_bat_ky": _p(t["co_loi"] / t["ban"]),
                        "so_lan_doi_trang_thai": t["doi_trang_thai"]})
    bang_recall = {m: {"so_loi": t["tong"], "co_canh_bao_cung_loai": _p(t["cung_loai"] / t["tong"]),
                       "co_canh_bao_bat_ky": _p(t["co_canh_bao"] / t["tong"])} for m, t in sorted(recall.items())}

    def ty(k):
        return {"so_phat_bieu": k["tong"], "co_loi": k["co_loi"], "vao_than": k["vao_than"],
                "lot": k["lot"], "ty_le_lot": _p(k["lot"] / max(k["co_loi"], 1)),
                "lot_nguy_hiem": k["lot_nguy_hiem"], "loi_nguy_hiem": k["loi_nguy_hiem"],
                "ty_le_lot_nguy_hiem": _p(k["lot_nguy_hiem"] / max(k["loi_nguy_hiem"], 1)),
                "chan_thua": k["chan_thua"], "ty_le_chan_thua": _p(k["chan_thua"] / max(k["khong_loi"], 1))}
    ra = {
        "phien_ban_canh_bao": PHIEN_BAN, "phien_ban_bo_cham": cham_he_thong.PHIEN_BAN,
        "chinh_sach_C": cong_rui_ro.CHINH_SACH, "chinh_sach_D": gop.CHINH_SACH_D,
        "thu_muc": str(thu_muc), "cac_tap": tap_list, "nhanh": nhanh,
        "so_phat_bieu_con_hieu_luc": so_pb, "so_menh_de": so_pb,
        "ghi_chu": "So voi BO CHAM TU DONG, khong phai nhan nguoi. Tham do tren tap phat trien da nhin.",
        "theo_ma": bang_ma, "do_phu_theo_loi_bo_cham": bang_recall,
        "chinh_sach": {k: ty(v) for k, v in chinh_sach.items()},
        "canh_bao_hien_moi_phat_bieu": _p(sum(so_hien) / max(len(so_hien), 1)),
        "bo_sot": {**bo_sot, "do_phu": _p(bo_sot["sot_co_canh_bao"] / max(bo_sot["dap_an_sot"], 1)),
                   "chinh_xac": _p(bo_sot["canh_bao_trung_sot"] / max(bo_sot["canh_bao"], 1))},
    }
    return ra, nhat


# ═══ main() — Chạy dòng lệnh đo cảnh báo, ghi JSON và nhật ký ═════════════════════════
# In bảng theo mã cảnh báo và độ phủ theo lỗi bộ chấm.
def main(argv=None):
    import argparse
    if hasattr(sys.stdout, "reconfigure"):  # cửa sổ lệnh cp1252 không in được chữ có dấu
        sys.stdout.reconfigure(errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.split("─" * 72)[-1].strip().splitlines()[0])  # bỏ khung ghi chú cấu trúc ở đầu
    ap.add_argument("--thu-muc", default=str(THU_MUC))
    ap.add_argument("--nhanh", default=NHANH)
    ap.add_argument("--ra-json", default=None, help="mac dinh <THU_MUC_KET_QUA>/canh-bao.json")
    a = ap.parse_args(argv)
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    ra, nhat = chay(a.thu_muc, a.nhanh)
    dich = duong_dan.THU_MUC_KET_QUA
    tep_json = Path(a.ra_json) if a.ra_json else dich / "canh-bao.json"
    tep_json.parent.mkdir(parents=True, exist_ok=True)
    tep_json.write_text(json.dumps(ra, ensure_ascii=False, indent=2), encoding="utf-8")
    tep_nk = tep_json.with_name(tep_json.stem + "-nhat-ky.jsonl")
    tep_nk.unlink(missing_ok=True)
    nhat_ky.ghi(tep_nk, nhat)
    print(json.dumps({k: ra[k] for k in ("so_phat_bieu_con_hieu_luc", "chinh_sach", "canh_bao_hien_moi_phat_bieu",
                                         "bo_sot")}, ensure_ascii=False, indent=1))
    print(f"{'ma':38} {'bao':>5} {'cx_loai':>8} {'cx_loi':>7} {'doi_tt':>6}  tin_cay")
    for d in ra["theo_ma"]:
        print(f"{d['ma']:38} {d['so_lan_bao']:5d} {str(d['chinh_xac_cung_loai']):>8} "
              f"{str(d['chinh_xac_co_loi_bat_ky']):>7} {d['so_lan_doi_trang_thai']:6d}  {d['tin_cay']}")
    print("do phu:", json.dumps(ra["do_phu_theo_loi_bo_cham"], ensure_ascii=False))
    print(f"\nGhi {tep_json} va {tep_nk}")


if __name__ == "__main__":
    main()
