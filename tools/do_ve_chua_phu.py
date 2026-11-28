# -*- coding: utf-8 -*-
"""Đo khô (CPU, không gọi mô hình) TRẦN của quét lại vế (Task 1, kế hoạch 27/11/2026).

Trên đầu ra lượt trích đã lưu (`data/thach_thuc/ra_C_khoa_*_phat_trien.jsonl`, cùng bộ 300 ca
của chẩn đoán "172/200 sót nằm ở lượt đã có mệnh đề" trong `docs/ket-qua/canh-bao-moc-0.md`):

  1. ghép đáp án với bảng mệnh đề bằng `do_trich.ghep` (cùng phép đo bỏ sót của dự án);
  2. với mỗi mệnh đề đáp án bị sót, định vị câu trích của đáp án trong lượt của nó;
  3. xếp nó vào một nhóm theo các vế của `b1_quet_lai_ve.cac_ve`:
       trong_ve_chua_phu   giao một vế có tín hiệu lâm sàng mà chưa câu trích nào phủ
                           -> quét lại SẼ hỏi lại mô hình về chỗ này (ước lượng, không phải trần)
       ve_khong_tin_hieu   chỉ giao vế chưa phủ nhưng không có tín hiệu -> bị lọc, không hỏi
       ve_da_phu           chỉ giao vế đã có câu trích phủ (mô hình đã dẫn tới, nhưng nội dung
                           không ghép được với đáp án: ghi sai/khác chữ, hoặc giới hạn bộ chấm)
       ngoai_ve            nằm ở câu hỏi hoặc vế xã giao (không thành vế)
       khong_dinh_vi       câu trích của đáp án không tìm thấy trong lượt

Đây là TRẦN: vế được hỏi lại không có nghĩa mô hình sẽ trích đúng. Số thật cần chạy mô hình.

  python tools/do_ve_chua_phu.py --ra docs/ket-qua/ve-chua-phu.md
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.do_luong.do_trich import ghep  # noqa: E402
from src.duong_ong.b1_quet_lai_ve import _luot, cac_ve  # noqa: E402
from src.duong_ong.b4_kiem_can_cu import tim_trich  # noqa: E402

GOC = Path(__file__).resolve().parent.parent
BO = ("dinh_chinh", "doi_chu_the", "nhieu_asr", "phuong_ngu")
NHOM = ("trong_ve_chua_phu", "ve_khong_tin_hieu", "ve_da_phu", "ngoai_ve", "khong_dinh_vi")


def doc(tep):
    return {x["id"]: x for x in (json.loads(d) for d in Path(tep).read_text(encoding="utf-8").splitlines()
                                 if d.strip())}


def bang_tho(r: dict) -> list:
    """Bảng mệnh đề gần nhất với đầu ra thô của lượt trích: mệnh đề hợp lệ + bản ghi bị
    `tu_json` loại (chúng vẫn là thứ mô hình đã trích, quét lại thấy chúng)."""
    return list(r.get("phat_bieu") or []) + [x["ban_ghi"] for x in (r.get("loi_ban_ghi") or [])
                                             if isinstance(x.get("ban_ghi"), dict)]


def bo_trung_dap_an(da: list) -> list:
    """Đáp án ghi cùng một mệnh đề ở hai mục ("sốt" ở LÝ DO KHÁM và BỆNH SỬ, cùng lượt). Phép
    ghép một-một của `ghep` đếm bản thứ hai là bỏ sót dù mô hình đã ghi; bỏ bản trùng trước."""
    ra, da_thay = [], set()
    for d in da:
        k = (str(d.get("noi_dung") or "").strip().lower(), tuple(sorted(d.get("luot") or [])))
        if k not in da_thay:
            da_thay.add(k)
            ra.append(d)
    return ra


def xep_nhom(d: dict, luot: dict, ve: list) -> str:
    khoang = []
    for s in d.get("luot") or d.get("luot_thoai") or []:
        if s not in luot:
            continue
        for t in d.get("trich_dan") or []:
            k = tim_trich(t, luot[s][1])
            if k:
                khoang.append((s, k[0], k[1]))
    if not khoang:
        return "khong_dinh_vi"
    giao = [v for v in ve for s, a, b in khoang if v["luot"] == s and v["dau"] < b and a < v["cuoi"]]
    if any(v["tin_hieu"] and not v["da_phu"] for v in giao):
        return "trong_ve_chua_phu"
    if any(not v["da_phu"] for v in giao):
        return "ve_khong_tin_hieu"
    if giao:
        return "ve_da_phu"
    return "ngoai_ve"


def do_bo(ten: str) -> dict:
    vang = doc(GOC / f"data/thach_thuc/thach_thuc_{ten}_phat_trien.jsonl")
    ra = doc(GOC / f"data/thach_thuc/ra_C_khoa_thach_thuc_{ten}_phat_trien.jsonl")
    dem = Counter()
    tong_da = so_sot = sot_luot_da_dan = ca = ca_co_ve = so_ve = ve_trung = 0
    sot_goc = trung_da = 0
    for i in sorted(set(vang) & set(ra)):
        ca += 1
        ht, da_goc = vang[i]["input"], vang[i].get("dap_an") or []
        ps = ra[i].get("phat_bieu") or []
        sot_goc += len(ghep(da_goc, ps)[1])
        da = bo_trung_dap_an(da_goc)
        trung_da += len(da_goc) - len(da)
        _cap, thieu, _thua = ghep(da, ps)
        tong_da += len(da)
        so_sot += len(thieu)
        luot = _luot(ht)
        bang = bang_tho(ra[i])
        ve = cac_ve(ht, bang)
        chua_phu = [v for v in ve if v["tin_hieu"] and not v["da_phu"]]
        ca_co_ve += bool(chua_phu)
        so_ve += len(chua_phu)
        da_dan = {int(s) for p in bang for s in (p.get("bang_chung") or p.get("luot_thoai") or [])
                  if str(s).isdigit()}
        trung = set()
        for d in thieu:
            n = xep_nhom(d, luot, ve)
            dem[n] += 1
            sot_luot_da_dan += any(s in da_dan for s in (d.get("luot") or []))
            if n == "trong_ve_chua_phu":
                for v in chua_phu:
                    for s in d.get("luot") or []:
                        for t in d.get("trich_dan") or []:
                            k = tim_trich(t, luot[s][1]) if s in luot else None
                            if k and v["luot"] == s and v["dau"] < k[1] and k[0] < v["cuoi"]:
                                trung.add((v["luot"], v["dau"]))
        ve_trung += len(trung)
    return {"ca": ca, "menh_de": tong_da, "sot": so_sot, "sot_luot_da_dan": sot_luot_da_dan,
            "sot_goc": sot_goc, "trung_da": trung_da,
            "nhom": dict(dem), "ca_co_ve": ca_co_ve, "so_ve": so_ve, "ve_trung": ve_trung}


def pt(a, b):
    return f"{100 * a / b:.1f}%" if b else "—"


def in_bang(kq: dict) -> str:
    tong = {k: sum(r[k] for r in kq.values()) for k in
            ("ca", "menh_de", "sot", "sot_luot_da_dan", "ca_co_ve", "so_ve", "ve_trung",
             "sot_goc", "trung_da")}
    tong["nhom"] = Counter()
    for r in kq.values():
        tong["nhom"].update(r["nhom"])
    hang = {**kq, "**Tổng**": tong}
    d = ["# Trần của quét lại vế chưa phủ (đo khô, CPU)", "",
         "Chạy: `python tools/do_ve_chua_phu.py --ra docs/ket-qua/ve-chua-phu.md`. "
         "Nguồn: đầu ra đã lưu `data/thach_thuc/ra_C_khoa_*_phat_trien.jsonl` + đáp án "
         "`thach_thuc_*_phat_trien.jsonl` (4 bộ phát triển). **Chưa đo bằng mô hình**: đây là số mệnh "
         "đề bị sót mà quét lại SẼ hỏi lại, không phải số mô hình sẽ trích đúng.", "",
         f"Đáp án của bộ sinh ghi cùng một mệnh đề ở hai mục (cùng nội dung, cùng lượt): "
         f"{tong['trung_da']} bản trùng. Ghép một-một đếm bản trùng là bỏ sót dù mô hình đã ghi "
         f"(chưa bỏ trùng: {tong['sot_goc']} sót), nên các bảng dưới tính trên đáp án ĐÃ bỏ trùng.", "",
         "## Mệnh đề bị sót nằm ở đâu", "",
         "| Bộ | Ca | Mệnh đề đáp án | Bị sót | Sót ở lượt đã dẫn | Trong vế chưa phủ (ước lượng) | "
         "Vế chưa phủ, không tín hiệu | Vế đã phủ | Ngoài vế | Không định vị |",
         "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for ten, r in hang.items():
        n = r["nhom"]
        d.append(f"| {ten} | {r['ca']} | {r['menh_de']} | {r['sot']} | "
                 f"{r['sot_luot_da_dan']} ({pt(r['sot_luot_da_dan'], r['sot'])}) | "
                 f"**{n.get('trong_ve_chua_phu', 0)} ({pt(n.get('trong_ve_chua_phu', 0), r['sot'])})** | "
                 + " | ".join(f"{n.get(k, 0)}" for k in NHOM[1:]) + " |")
    n = tong["nhom"]
    tran = n.get("trong_ve_chua_phu", 0)
    d += ["", "## Chi phí", "",
          "| Bộ | Ca có ≥ 1 vế chưa phủ (= số lần sinh thêm) | Vế chưa phủ | Vế/ca | "
          "Vế chứa ≥ 1 mệnh đề sót |", "|---|---:|---:|---:|---:|"]
    for ten, r in hang.items():
        d.append(f"| {ten} | {r['ca_co_ve']}/{r['ca']} ({pt(r['ca_co_ve'], r['ca'])}) | {r['so_ve']} | "
                 f"{r['so_ve'] / r['ca']:.2f} | {r['ve_trung']} ({pt(r['ve_trung'], r['so_ve'])}) |")
    d += ["", "## Đọc số", "",
          f"- Trần thu hồi: {tran}/{tong['sot']} mệnh đề sót ({pt(tran, tong['sot'])}) nằm trong một vế mà "
          f"quét lại sẽ hỏi lại. Nếu mô hình trích đúng hết chỗ đó, tỉ lệ sót trên bộ này giảm từ "
          f"{pt(tong['sot'], tong['menh_de'])} xuống tối đa {pt(tong['sot'] - tran, tong['menh_de'])}.",
          f"- {n.get('ve_da_phu', 0)}/{tong['sot']} mệnh đề sót ({pt(n.get('ve_da_phu', 0), tong['sot'])}) nằm ở "
          "vế ĐÃ có câu trích phủ: mô hình dẫn đúng chỗ nhưng `noi_dung` không ghép được với đáp án. Đọc mẫu: "
          "chép theo chính tả sai của ASR (\"the trang beo\", \"beo phi do một\"), đổi chữ (\"ngột mũi\" thay "
          "\"nghẹt mũi\", \"nóng trong\" thay \"nóng hầm hập\"), gắn nhãn sai lên đúng câu trích (\"đau bụng\" cho "
          "\"đi ngoài toàn nước\"), hoặc bỏ nửa sau của ý (\"đau cơ\" thay \"đau cơ nặng hơn sau khi ăn\"). "
          "Nghĩa là con số \"86% sót nằm ở lượt đã có mệnh đề\" chủ yếu là **ghi sai nội dung trên đúng vế**, "
          "không phải vế bị bỏ qua. Quét lại vế chưa phủ không nhắm vào nhóm này; muốn thu hồi phải kiểm "
          "`noi_dung` so với câu trích của chính nó (vd. vế có câu trích mà nội dung mệnh đề ít trùng từ).",
          "- Hệ quả cho MT1 (≤ 8,0% từ 11,5%, đo trên `viet_phat_trien_v2`): trên bộ này ước lượng phần quét lại có thể cứu chỉ "
          f"bớt được {pt(tran, tong['menh_de'])} điểm sót, nên quét lại đơn thuần khó đạt MT1. Đây là dự báo "
          "trên bộ khác, cần đo thật để kết luận.",
          f"- {n.get('ve_khong_tin_hieu', 0)} mệnh đề sót nằm ở vế chưa phủ nhưng không có tín hiệu lâm sàng "
          "theo bộ từ khoá của `canh_bao.bo_sot` — muốn thu hồi phải nới bộ lọc tín hiệu (đổi chi phí lấy độ phủ).",
          "- Bảng mệnh đề dùng ở đây là bảng SAU áp luật của nhánh C_khoa cộng các bản ghi bị `tu_json` loại; "
          "lượt trích thô không được lưu riêng trên máy này. Hai bảng có cùng câu trích nên độ phủ vế gần như "
          "nhau, nhưng không trùng tuyệt đối.",
          "- Số thật (MT1, 30 ca `viet_phat_trien_v2`) phải chạy `chay_trung_gian(..., quet_lai=True)` trên GPU "
          "HoaiĐức: **chưa đo bằng mô hình**."]
    return "\n".join(d) + "\n"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--ra", default=None)
    a = ap.parse_args()
    kq = {ten: do_bo(ten) for ten in BO}
    van = in_bang(kq)
    if a.ra:
        Path(a.ra).write_text(van, encoding="utf-8")
    print(van)


if __name__ == "__main__":
    main()
