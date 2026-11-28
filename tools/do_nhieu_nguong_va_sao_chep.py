# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Báo cáo]
Làm gì   : Đo độ nhạy ngưỡng ghép và mức sao chép bản thảo trên tập phát triển.
Vào → Ra : tệp ra hệ thống + đáp án cùng thư mục → bảng JSON và Markdown.
Đọc từ   : bộ nạp dữ liệu, bộ chấm mệnh đề và phép đo mảnh trích.
"""
import json
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC))

from src.bo_du_lieu import nap_du_lieu as du_lieu
from src.do_luong.cham_he_thong import dap_an
from src.do_luong.cham_nhieu_nguong import cham_o_cac_nguong
from src.do_luong.do_sao_chep import do_phu_va_mat_do

NGUONG = (0.4, 0.5, 0.6, 0.7)


def tinh(tep, tep_dap_an):
    """Gộp số mệnh đề theo ca; lấy trung bình hai chỉ số sao chép theo ca."""
    gold = {x["id"]: x for x in du_lieu.nap_mau(tep_dap_an)}
    du_doan = du_lieu.nap_mau(tep)
    ids = [x["id"] for x in du_doan]
    if len(ids) != len(set(ids)) or not set(ids) <= set(gold) or not ids:
        raise ValueError(f"ID trùng, thiếu đáp án hoặc tệp rỗng: {tep}")
    so_ghep = dict.fromkeys(NGUONG, 0)
    tong_du = tong_da = 0
    do_phu = mat_do = 0.0
    for dong in du_doan:
        ca = gold[dong["id"]]
        ps = dong["phat_bieu"]
        da = dap_an(ca)
        diem = cham_o_cac_nguong(ps, da, NGUONG)
        for n in NGUONG:
            so_ghep[n] += round(diem[n]["recall"] * len(da))
        tong_du += len(ps)
        tong_da += len(da)
        sao = do_phu_va_mat_do(dong["du_doan"], ca["input"])
        do_phu += sao["coverage"]
        mat_do += sao["density"]
    scores = {}
    for n in NGUONG:
        p = so_ghep[n] / tong_du if tong_du else 0.0
        r = so_ghep[n] / tong_da if tong_da else 0.0
        scores[str(n)] = {"precision": p, "recall": r,
                          "f1": 2 * p * r / (p + r) if p + r else 0.0,
                          "so_ghep": so_ghep[n]}
    return {"he_thong": tep.name.split("_thach_thuc_", 1)[0][3:],
            "tap": tep_dap_an.stem, "tep_he_thong": tep.name,
            "so_ca": len(ids), "so_ca_dap_an": len(gold),
            "so_du_doan": tong_du, "so_dap_an": tong_da,
            "nguong": scores, "coverage_trung_binh": do_phu / len(ids),
            "density_trung_binh": mat_do / len(ids)}


def main():
    thu_muc = GOC / "data" / "thach_thuc"
    ket_qua = []
    for tep in sorted(thu_muc.glob("ra_*_thach_thuc_*_phat_trien.jsonl")):
        ten_tap = "thach_thuc_" + tep.name.split("_thach_thuc_", 1)[1]
        tep_da = thu_muc / ten_tap
        if not tep_da.is_file():
            raise FileNotFoundError(f"Không tìm thấy đáp án cho {tep.name}: {tep_da}")
        ket_qua.append(tinh(tep, tep_da))
    if not ket_qua:
        raise RuntimeError("Không tìm thấy tệp kết quả tập thử thách phát triển")
    dong = ["# Nhiều ngưỡng và mức sao chép", "",
            "F1 ghép mệnh đề cho biết mức khớp từ giữa mệnh đề trích và đáp án; ngưỡng càng thấp càng dễ ghép. "
            "Độ phủ là tỷ lệ từ trong bản thảo nằm trong các mảnh liên tiếp có ở hội thoại, còn mật độ tăng khi các mảnh đó dài hơn. "
            "F1 được gộp theo số mệnh đề, còn độ phủ và mật độ là trung bình theo ca; hai chỉ số sao chép tính trên toàn bộ bản thảo, kể cả tiêu đề. "
            "Đây là các tập phát triển từ dữ liệu tổng hợp, nên kết quả không chứng minh chất lượng hay mức sao chép trên hội thoại thực tế.", "",
            "| Hệ thống | Tập | Số ca | F1 0.4 | F1 0.5 | F1 0.6 | F1 0.7 | Độ phủ | Mật độ |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for k in ket_qua:
        f = " | ".join(f"{k['nguong'][str(n)]['f1']:.3f}" for n in NGUONG)
        dong.append(f"| {k['he_thong']} | {k['tap']} | {k['so_ca']}/{k['so_ca_dap_an']} | {f} | {k['coverage_trung_binh']:.3f} | {k['density_trung_binh']:.3f} |")
    bao_cao = "\n".join(dong) + "\n"
    dich = GOC / "docs" / "ket-qua" / "nhieu-nguong-va-sao-chep"
    dich.with_suffix(".json").write_text(json.dumps(ket_qua, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    dich.with_suffix(".md").write_text(bao_cao, encoding="utf-8")
    print(bao_cao)


if __name__ == "__main__":
    main()
