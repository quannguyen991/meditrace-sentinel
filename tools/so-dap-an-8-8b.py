# -*- coding: utf-8 -*-
"""So ket qua cham bang dap an the he 8 va 8b (sua "nong ham hap", 24/09/2026).

Doc cap tep `cham-he-thong-<bo><hau to>.json` va `...<hau to>-8b.json` da co trong
`docs/ket-qua/`, KHONG cham lai gi. Ghi `docs/ket-qua/sua-dap-an-nong-ham-hap.md/.json`.

    python tools/so-dap-an-8-8b.py
"""
import json
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
KQ = GOC / "docs" / "ket-qua"
BO = [("thach_thuc_doi_chu_the_phat_trien", "Đổi chủ thể"),
      ("thach_thuc_dinh_chinh_phat_trien", "Đính chính"),
      ("thach_thuc_nhieu_asr_phat_trien", "Nhiễu ASR"),
      ("thach_thuc_phuong_ngu_phat_trien", "Phương ngữ")]
NGUON = [("-th8-v0922", "Mô hình nhà (Qwen3-4B tinh chỉnh)"),
         ("-th8-v0922-chinh-sach-C", "Mô hình nhà, chính sách C"),
         ("-doi-chung-luat-th8-v0922", "Luật đối chứng"),
         ("-nen-8b-v0922", "Qwen3-8B chưa dạy"),
         ("-data-gpt-v0922", "GPT (đối chứng thương mại)"),
         ("-data-may-v0922", "Mô hình nhà trên cùng tập con với GPT")]
TEN_NHANH = {"B": "B", "C": "C", "C_khoa": "C + cổng", "C_khoa_hoi": "C + cổng + hỏi",
             "tat_nguoi_noi": "chủ thể = người nói", "tat_benh_nhan": "chủ thể = bệnh nhân",
             "tat_day_du": "lấy cả lượt bác sĩ", "tat_context": "bảng từ ConText",
             "tat_context_vai": "ConText + vai"}
CHI_SO = [("f1", "F₁"), ("ser", "SER"), ("do_chinh_xac", "Độ chính xác"),
          ("do_phu", "Độ phủ"), ("khong_can_cu", "Không căn cứ"), ("bo_sot", "Bỏ sót"),
          ("sai_muc", "Sai mức"), ("loi_nghiem_trong", "Lỗi nghiêm trọng")]


def _so(x):
    return f"{100 * x:.2f}".replace(".", ",")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ra, dong = {}, []
    for tap, ten_bo in BO + [("viet_phat_trien_mau240", "Tập phát triển, mẫu 240 ca")]:
        cap = NGUON if tap != "viet_phat_trien_mau240" else [("", "Mô hình nhà (Qwen3-4B tinh chỉnh)")]
        for hau, ten_nguon in cap:
            cu_p = KQ / f"cham-he-thong-{tap}{hau or '-v0922'}.json"
            moi_p = KQ / f"cham-he-thong-{tap}{hau or '-v0922'}-8b.json"
            if not (cu_p.exists() and moi_p.exists()):
                continue
            cu = json.loads(cu_p.read_text(encoding="utf-8"))
            moi = json.loads(moi_p.read_text(encoding="utf-8"))
            for nhanh in cu:
                if nhanh not in moi:
                    continue
                a, b = cu[nhanh]["tong_hop"]["bang"], moi[nhanh]["tong_hop"]["bang"]
                hang = {k: (a[k]["gia_tri"], b[k]["gia_tri"]) for k, _ in CHI_SO
                        if k in a and k in b}
                ra.setdefault(tap, {}).setdefault(hau or "mau240", {})[nhanh] = {
                    "so_ca": moi[nhanh]["tong_hop"]["so_ca"],
                    "phien_ban_cu": cu[nhanh].get("phien_ban_bo_cham"),
                    "phien_ban_moi": moi[nhanh].get("phien_ban_bo_cham"),
                    "chi_so": {k: {"cu": x, "moi": y} for k, (x, y) in hang.items()},
                    "thach_thuc": {"cu": cu[nhanh].get("thach_thuc"),
                                   "moi": moi[nhanh].get("thach_thuc")}}
                dong.append((ten_bo, ten_nguon, TEN_NHANH.get(nhanh, nhanh),
                             moi[nhanh]["tong_hop"]["so_ca"], hang,
                             cu[nhanh].get("phien_ban_bo_cham")))

    md = ["# Sửa đáp án \"nóng hầm hập\" — số liệu trước và sau (24/09/2026)", "",
          "Sinh bằng `python tools/so-dap-an-8-8b.py`. Đừng sửa tay. Không chấm lại gì: "
          "chỉ đọc hai tệp chấm đã có của cùng một nguồn kết quả, một tệp chấm bằng đáp án "
          "thế hệ 8, một tệp bằng đáp án thế hệ 8b.", "",
          "**Đã đổi gì.** Người bệnh nói \"nóng hầm hập\" (chưa đo nhiệt độ). Đáp án thế hệ 8 "
          "ghi \"sốt, chắc chắn\"; bảng chuẩn hoá của chính dự án (`chuan_hoa`, từ 11/09) ghi "
          "cụm này là *cần hỏi*, không tự đổi thành sốt. Đáp án 8b ghi đúng lời người nói, độ chắc "
          "chắn giữ nguyên. Lời thoại không đổi, nên mọi kết quả đã chạy chỉ cần chấm lại. Xem "
          "`docs/dang-ky-truoc.md`, mục *Thay đổi sau đăng ký*.", "",
          "**Số mệnh đề đáp án bị đổi:** tập phát triển 42 (19 ca), phương ngữ 28 (13 ca), "
          "đổi chủ thể 14 (6 ca), đính chính 9 (3 ca), nhiễu ASR 4 (2 ca), dân gian 14 (6 ca). "
          "Tập kiểm tra cuối: 0 — tệp giống hệt từng byte, mã băm vẫn khớp đăng ký trước.", "",
          "Số là phần trăm. Cột \"8\" chấm bằng đáp án cũ, cột \"8b\" bằng đáp án mới; cả hai "
          "cùng bộ chấm phiên bản 2026-09-22. Mẫu 240 ca tập phát triển trước đây chỉ có tệp chấm "
          "bằng bộ chấm trước 22/09 (`the-he-8/`); ngày 24/09 đã chấm thêm bằng đáp án cũ với bộ "
          "chấm 22/09 (`...mau240-v0922.json`) để hai cột so được với nhau.", ""]
    ten_cs = [t for _k, t in CHI_SO[:6]]
    md.append("| Bộ | Nguồn | Nhánh | Ca | " + " | ".join(f"{t} 8 → 8b" for t in ten_cs) + " |")
    md.append("|---|---|---|---|" + "---|" * len(ten_cs))
    for ten_bo, ten_nguon, nhanh, so_ca, hang, pb in dong:
        o = []
        for k, _t in CHI_SO[:6]:
            if k not in hang:
                o.append("—")
                continue
            x, y = hang[k]
            o.append(f"{_so(x)} → {_so(y)}" if abs(x - y) > 1e-12 else f"{_so(x)} (không đổi)")
        md.append(f"| {ten_bo} | {ten_nguon} | {nhanh} | {so_ca} | " + " | ".join(o) + " |")
    tt = ra.get("thach_thuc_phuong_ngu_phat_trien", {}).get("-th8-v0922", {})
    if tt:
        md += ["", "**Chỉ số cặp của bộ phương ngữ (mô hình nhà):**", "",
               "| Nhánh | Lỗi ở bản có phương ngữ, 8 → 8b | Lỗi ở bản không phương ngữ | Số cặp đầu ra giống hệt |",
               "|---|---|---|---|"]
        for nhanh, v in tt.items():
            c, m = v["thach_thuc"]["cu"] or {}, v["thach_thuc"]["moi"] or {}
            md.append(f"| {TEN_NHANH.get(nhanh, nhanh)} | {c.get('loi_ban_co_phuong_ngu')} → "
                      f"{m.get('loi_ban_co_phuong_ngu')} | {m.get('loi_ban_khong_phuong_ngu')} | "
                      f"{m.get('giong_het')}/{m.get('so_cap')} |")
        md += ["", "\"Số cặp đầu ra giống hệt\" không còn là đích ở 13 cặp chứa \"nóng hầm hập\": "
               "ở đó đầu ra đúng của hai bản khác nhau (bản A ghi \"nóng hầm hập\", bản B ghi "
               "\"sốt\"). Báo cáo không dùng chỉ số này."]
    (KQ / "sua-dap-an-nong-ham-hap.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (KQ / "sua-dap-an-nong-ham-hap.json").write_text(
        json.dumps(ra, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
