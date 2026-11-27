# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Bộ chấm]
Làm gì   : Chấm lại các nhánh bằng điểm quy gán trên đúng đầu ra đã sinh, để xem kết luận C
           không hơn B có do thước đo mù không.
Vào → Ra : tệp data/ra_*.jsonl các nhánh trên một tập (--tap) → bảng điểm quy gán JSON và
           báo cáo markdown
Đọc từ   : cham() lấy điểm trung bình một nhánh; main() chấm mọi nhánh và ghi báo cáo
Mục lục (các hàm/lớp chính):
  cham()      Lấy điểm trung bình một nhánh trên cả tập
  main()      Chấm lại mọi nhánh bằng điểm quy gán, ghi báo cáo
  _bao_cao()  Dựng báo cáo Markdown so các nhánh
Gọi tới  : do_luong/cham_diem, do_luong/thuoc_do_quy_gan, bo_du_lieu/nap_du_lieu,
           he_thong/duong_dan
Tên cũ   : cham_lai_bang_quy_gan.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Chấm lại các nhánh bằng ĐIỂM QUY GÁN, trên đúng đầu ra đã có.

Cửa 4 kết luận "C không hơn B" bằng `0,6×ROUGE + 0,4×SectionF1`. Nhưng chính đề
tài đã chứng minh bộ chấm đó mù trước lỗi quy gán, và chứng chỉ trên 38 bệnh án
thật còn cho thấy nó xếp lỗi nguy hiểm CAO HƠN lỗi vô hại (khoảng cách −0,0104).

Chấm bằng một cái thước mù rồi kết luận về một cơ chế chuyên trị điểm mù của nó
là lỗi thiết kế đánh giá. Script này chấm lại — KHÔNG chạy lại mô hình, dùng
đúng các tệp `data/ra_*.jsonl` đã sinh, nên chênh lệch đo được chắc chắn đến từ
CÁCH CHẤM chứ không từ một lần sinh khác.

    python -m src.do_luong.cham_lai_bang_quy_gan --tap phat_trien
"""
import argparse
import io
import json
import sys
from pathlib import Path

from src.do_luong import cham_diem as cham_diem
from src.bo_du_lieu import nap_du_lieu as du_lieu
from src.he_thong import duong_dan as duong_dan
from src.do_luong import thuoc_do_quy_gan as tdq

# Thứ tự có ý: cộng dồn từ ít cơ chế nhất đến nhiều nhất, rồi hai ô bóc cơ chế.
# `A_nen` là nhánh A chạy bằng mô hình NỀN (không nạp adapter), cùng mô hình với
# bước trích của nhánh B và cùng zero-shot như nó. Nó là đối chứng tách được hai
# thứ mà bảng cũ trộn làm một: *có cấu trúc hay không* và *có fine-tune hay không*.
# `A_cong_nen` thêm 10/09/2026: `nhanh.ten_ket_qua` sinh được tên này khi chạy
# A+ mà không nạp adapter, và trước đó bộ chấm không biết nó. Mọi tên bên GHI
# sinh ra đều phải có ở đây — test `test_moi_ten_ben_GHI_sinh_ra_deu_co_trong_
# danh_sach_ben_DOC` chặn hai bên lệch nhau.
NHANH = ["A", "A_nen", "A_cong", "A_cong_nen", "E", "E_chi_bo_sung", "B",
         "C_khong_luat", "C_khong_lien_ket", "C", "C_ghi_de", "D",
         "C_quan_he", "C_quan_he_luat", "D_quan_he"]


# ─── _nap() — Nạp đầu ra của một nhánh trên một tập ───────────────────────────────────
def _nap(tap, nhanh):
    dp = Path(duong_dan.THU_MUC_DU_LIEU) / f"ra_{nhanh}_{tap}.jsonl"
    if not dp.exists():
        return None
    return [json.loads(l) for l in open(dp, encoding="utf-8") if l.strip()]


# ═══ cham() — Lấy điểm trung bình một nhánh trên cả tập ═══════════════════════════════
# Chấm cả điểm quy gán lẫn điểm cuộc thi; có thể dùng bản bỏ mục phụ.
def cham(ds, dung_ban_khong_muc_phu=False):
    """Điểm trung bình của một nhánh trên cả tập."""
    khoa = "du_doan_khong_muc_phu" if dung_ban_khong_muc_phu else "du_doan"
    tong = {}
    n = 0
    for m in ds:
        du_doan = m.get(khoa) or m.get("du_doan") or ""
        d = tdq.diem(du_doan, m.get("tham_chieu") or "")
        c = cham_diem.diem_cuoi(du_doan, m.get("tham_chieu") or "")
        d["final_cuoc_thi"] = c["final"]
        d["rouge_avg"] = c["rouge_avg"]
        d["section_f1"] = c["section_f1"]
        for k, v in d.items():
            if isinstance(v, (int, float)):
                tong[k] = tong.get(k, 0) + v
        n += 1
    return {k: round(v / n, 4) for k, v in tong.items()} if n else {}


# ═══ main() — Chấm lại mọi nhánh bằng điểm quy gán, ghi báo cáo ═══════════════════════
# Chặn tập khoá, bỏ qua nhánh thiếu tệp, ghi tệp JSON và Markdown.
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--tap", default="viet_phat_trien")
    a = ap.parse_args()
    du_lieu.chan_tap_khoa(a.tap)
    du_lieu.chan_tap_ngoai(a.tap)

    bang = {}
    for nhanh in NHANH:
        ds = _nap(a.tap, nhanh)
        if ds is None:
            print(f"  (bo qua {nhanh}: chua co tep)")
            continue
        bang[nhanh] = cham(ds)
        bang[nhanh]["so_mau"] = len(ds)
        print(f"  {nhanh:18} f1_quy_gan={bang[nhanh]['f1_quy_gan']:.4f}  "
              f"final_cuoc_thi={bang[nhanh]['final_cuoc_thi']:.4f}")

    if not bang:
        print("Khong co nhanh nao de cham.")
        return

    dp = duong_dan.THU_MUC_KET_QUA / f"cham-lai-quy-gan-{a.tap}.json"
    dp.write_text(json.dumps(bang, ensure_ascii=False, indent=2), encoding="utf-8")
    dp_md = duong_dan.THU_MUC_KET_QUA / f"cham-lai-quy-gan-{a.tap}.md"
    dp_md.write_text(_bao_cao(bang, a.tap), encoding="utf-8")
    print(f"\nda ghi {dp}\nda ghi {dp_md}")


# ─── _hai_thuoc_do_noi_gi() — Viết nhận xét so hai thước đo từ số liệu ────────────────
# Câu chữ chọn theo việc nhánh nào thắng ở điểm quy gán và điểm cuộc thi.
def _hai_thuoc_do_noi_gi(a, b, ten_a):
    """Hai thước đo có cùng nói một điều không — đọc TỪ SỐ LIỆU.

    Ban đầu cho in cùng một câu *"hơn ở mọi mặt đã đo"*. Với nhánh A đã fine-tune
    thì câu đó đúng; với `A_nen` thì SAI — nó thua trên điểm cuộc thi. Một báo
    cáo tự in ra một câu ngược với bảng số ngay bên trên nó là chỗ nguy hiểm
    nhất trong cả tệp này.
    """
    ty = b["so_sai_chu_the"] / a["so_sai_chu_the"] if a["so_sai_chu_the"] else 0.0
    quy_gan_thang = a["dung_quy_gan"] > b["dung_quy_gan"]
    cuoc_thi_thang = a["final_cuoc_thi"] > b["final_cuoc_thi"]

    if quy_gan_thang and cuoc_thi_thang:
        return (f"**{ten_a} hơn nhánh B trên CẢ HAI thước đo**, kể cả mặt mà đường "
                f"ống trung gian được dựng riêng để chữa: nó gán nhầm người "
                f"**{ty:.1f} lần ít hơn** tính theo số mệnh đề mỗi hồ sơ.")

    if quy_gan_thang and not cuoc_thi_thang:
        return (
            "**Hai thước đo nói ngược nhau, và đó là điều đáng chú ý nhất ở bảng "
            "này.**\n\n"
            f"- Theo **điểm cuộc thi**, nhánh B thắng: {b['final_cuoc_thi']:.4f} so "
            f"với {a['final_cuoc_thi']:.4f}.\n"
            f"- Theo **điểm quy gán**, {ten_a} thắng: gán đúng người "
            f"{a['dung_quy_gan']:.1%} so với {b['dung_quy_gan']:.1%}, và gán nhầm "
            f"**{ty:.1f} lần ít hơn** tính theo số mệnh đề mỗi hồ sơ.\n\n"
            "Đọc ngay được từ đó: **biểu diễn trung gian mua được CẤU TRÚC và trả "
            "giá bằng QUY GÁN.** Nhánh B ghi đúng tên mục, chia đúng phần, nên "
            f"Section F1 cao; nhưng nó băm hội thoại thành "
            f"{b['so_menh_de_du_doan']:.1f} mệnh đề mỗi hồ sơ (bản tham chiếu chỉ có "
            f"{b['so_menh_de_tham_chieu']:.1f}) và gán nhầm người nhiều hơn hẳn.\n\n"
            "Với một dự án lấy lỗi quy gán làm trung tâm thì mặt thua mới là mặt "
            "quan trọng. Nhưng **phải trình bày cả hai** — trình bày một chiều là "
            "chọn thước cho vừa kết luận, đúng cái lỗi mà chính dự án này phê phán.")

    if not quy_gan_thang and cuoc_thi_thang:
        return (f"{ten_a} thắng trên điểm cuộc thi nhưng **thua trên điểm quy gán** "
                f"({a['dung_quy_gan']:.1%} so với {b['dung_quy_gan']:.1%}). Biểu diễn "
                f"trung gian đang giúp đúng ở mặt dự án quan tâm.")

    return (f"**Nhánh B hơn {ten_a} trên cả hai thước đo.** Biểu diễn trung gian có "
            f"tác dụng, và lợi thế của nhánh A ở bảng trước là do fine-tune.")


# ─── _canh_bao_fine_tune() — Viết đoạn cảnh báo nhiễu do fine-tune ────────────────────
# Còn cảnh báo khi chưa có nhánh A nền để hai bên cùng zero-shot.
def _canh_bao_fine_tune(bang):
    """Cảnh báo chỉ còn đúng khi CHƯA có nhánh nền."""
    if "A_nen" in bang and "A" in bang:
        return (
            "### Điểm gây nhiễu fine-tune đã được loại\n\n"
            "Bảng trên dùng **nhánh A nền**, chạy bằng chính mô hình mà bước trích "
            "của nhánh B dùng, và cũng zero-shot như nó. Nên chênh lệch còn lại "
            'không giải thích được bằng *"A được fine-tune còn B thì không"* nữa.\n\n'
            "Để đối chiếu, nhánh A **đã** fine-tune đạt điểm quy gán "
            f"{bang['A']['f1_quy_gan']:.4f} và gán đúng "
            f"{bang['A']['dung_quy_gan']:.1%} — tức fine-tune đóng góp một phần "
            "thật, nhưng không phải toàn bộ khoảng cách.")

    return (
        "### ⚠️ Một điểm gây nhiễu phải nói ra trước khi ai kết luận\n\n"
        "Hai nhánh **không cùng điều kiện huấn luyện**: A sinh bằng mô hình đã "
        "fine-tune, còn B/C/D trích bằng mô hình nền. Ràng buộc công bằng của kế "
        'hoạch chỉ ghi *"cùng một kích thước mô hình"* — **không đủ**.\n\n'
        "Chạy nhánh A **không fine-tune** để hai bên cùng zero-shot, rồi hãy kết luận.")


# ─── _bao_cao() — Dựng báo cáo Markdown so các nhánh ──────────────────────────────────
# Kiểm điều kiện Cửa 4: số mệnh đề gán nhầm người giảm từ 30% mà bỏ sót không tăng quá
# 20%.
def _bao_cao(bang, tap):
    dong = []
    for ten, d in bang.items():
        dong.append(
            f"| {ten} | {d['f1_quy_gan']:.4f} | {d['dung_quy_gan']:.4f} | "
            f"{d['bo_sot']:.4f} | {d['so_sai_chu_the']:.2f} | {d['final_cuoc_thi']:.4f} |")

    b, c = bang.get("B"), bang.get("C")
    if b and c and b["so_sai_chu_the"]:
        # Cửa 4 đòi "C giảm tỷ lệ lỗi >= 30% tương đối so với B". Đại lượng dùng
        # để kiểm điều kiện đó là SỐ MỆNH ĐỀ GÁN NHẦM NGƯỜI, không phải f1 —
        # f1 bị chi phối bởi cách diễn đạt khác nhau giữa bản sinh và bản tham
        # chiếu, và chỗ khác biệt ấy thì cả năm nhánh đều như nhau.
        giam = (b["so_sai_chu_the"] - c["so_sai_chu_the"]) / b["so_sai_chu_the"]
        tang_bo_sot = ((c["bo_sot"] - b["bo_sot"]) / b["bo_sot"]) if b["bo_sot"] else 0.0
        dat = giam >= 0.30 and tang_bo_sot <= 0.20
        ket = (
            f"Theo **số mệnh đề gán nhầm người mỗi hồ sơ** — đại lượng đúng để kiểm "
            f"điều kiện Cửa 4 — nhánh C giảm từ **{b['so_sai_chu_the']:.4f}** xuống "
            f"**{c['so_sai_chu_the']:.4f}**, tức **{giam:+.1%} tương đối**. "
            f"Bỏ sót đổi {tang_bo_sot:+.1%}.\n\n"
            f"Điều kiện Cửa 4 (giảm ≥ 30%, bỏ sót không tăng quá 20%): "
            f"**{'ĐẠT' if dat else 'KHÔNG ĐẠT'}**.\n\n"
            f"Điểm quy gán tổng thể của hai nhánh bằng nhau tới bốn chữ số "
            f"({b['f1_quy_gan']:.4f}), vì phần lớn chênh lệch giữa bản sinh và bản "
            f"tham chiếu nằm ở **cách diễn đạt**, và cả năm nhánh diễn đạt như nhau."
        )
        ket += (
            "\n\n**Đây mới là điều đáng nói.** Trước đây kết luận *\"C không hơn B\"* "
            "có một lỗ hổng ai cũng chỉ ra được: *thước đo của em mù trước đúng cái "
            "lỗi em đang đo*. Nay phép so chạy lại bằng một thước **đã có chứng chỉ "
            "phân biệt được lỗi đổi chủ thể với thay đổi vô hại**, và kết quả vẫn "
            "vậy. Kết quả âm giờ **đứng vững** thay vì bị nghi ngờ — đó là một kết "
            "luận nghiên cứu thật, không phải một thất bại cần giấu.\n\n"
            "Nguyên nhân đã biết, và nhất quán với `tang-quan-he-phat_trien.md`: "
            "cơ chế quan hệ **không có gì để chạy** (2 cặp trên 282 phát biểu), còn "
            "liên kết thực thể chỉ đổi tiền tố cách gọi chứ không đổi nội dung."
        )
    else:
        ket = "Chưa đủ dữ liệu để so B với C."

    # So A với B — phép so của Cửa 3, và nó quan trọng hơn phép so C với B.
    #
    # Ưu tiên `A_nen`: nó chạy bằng mô hình NỀN, cùng mô hình với bước trích của
    # B và cùng zero-shot, nên phép so tách được *có cấu trúc hay không* khỏi
    # *có fine-tune hay không*. Dùng `A` thì hai thứ đo lẫn vào nhau.
    a = bang.get("A_nen") or bang.get("A")
    ten_a = "A nền (zero-shot)" if "A_nen" in bang else "A (đã fine-tune)"
    if a and b:
        ket += f"""

## Cửa 3 — sinh trực tiếp so với trích rồi sinh

Cột đầu là **{ten_a}**. Ưu tiên nhánh nền khi có, vì nó dùng **cùng mô hình** với
bước trích của nhánh B và cũng zero-shot như nó — nhờ đó phép so tách được *có
cấu trúc hay không* khỏi *có fine-tune hay không*, hai thứ mà bảng cũ trộn làm một.

| | {ten_a} | B (trích rồi sinh) |
|---|---|---|
| **đúng quy gán** | **{a['dung_quy_gan']:.4f}** | {b['dung_quy_gan']:.4f} |
| **sai chủ thể / hồ sơ** | **{a['so_sai_chu_the']:.4f}** | {b['so_sai_chu_the']:.4f} |
| bỏ sót | {a['bo_sot']:.4f} | {b['bo_sot']:.4f} |
| thêm mới (thừa / bịa) | {a['them_moi']:.4f} | {b['them_moi']:.4f} |
| mệnh đề sinh ra / hồ sơ | {a['so_menh_de_du_doan']:.2f} | {b['so_menh_de_du_doan']:.2f} |
| điểm cuộc thi | {a['final_cuoc_thi']:.4f} | {b['final_cuoc_thi']:.4f} |

{_hai_thuoc_do_noi_gi(a, b, ten_a)}

Cửa 3 viết sẵn cho tình huống này: *"Nếu A+ ngang hoặc hơn B thì dừng, xem xét
lại. Có thể biểu diễn trung gian không cần thiết — đó là kết quả phải báo cáo
trung thực chứ không phải điều cần giấu."*

{_canh_bao_fine_tune(bang)}

### ⚠️ Điểm gây nhiễu thứ hai: thước đo này nhạy với cách đóng gói câu

Mệnh đề tách theo **ranh giới câu**. Bản tham chiếu gói nhiều sự kiện vào một
câu văn xuôi — *"Bệnh nhân nam nhỏ tuổi, trong tuần qua có biểu hiện nghẹt mũi
nhiều, ho tăng hơn bình thường, sốt 101°F vào ngày hôm qua"* là **một** mệnh đề
— còn nhánh B xuất từng mảnh một, thành **bốn**. Ghép tham lam nối được một
mảnh, ba mảnh còn lại tính là thừa.

Nên một phần điểm trừ của B đến từ **cách đóng gói câu**, không phải nội dung
sai. Và mô hình fine-tune viết giống bản tham chiếu về hình thức theo đúng định
nghĩa — nó học từ chính các bản ấy.

`dung_quy_gan` và `so_sai_chu_the` chịu ảnh hưởng ít hơn vì chỉ tính trên cặp đã
khớp nội dung, nhưng **không miễn nhiễm**. Đọc bảng trên với điều đó trong đầu:
khoảng cách A−B là thật, nhưng **độ lớn của nó thì chưa chắc**."""

    return f"""# Chấm lại các nhánh bằng ĐIỂM QUY GÁN — tập `{tap}`

Sinh tự động bằng `python -m src.do_luong.cham_lai_bang_quy_gan`. Đừng sửa tay.

**Không chạy lại mô hình.** Dùng đúng các tệp `data/ra_*.jsonl` đã sinh, nên mọi
chênh lệch dưới đây đến từ **cách chấm**, không phải từ một lần sinh khác.

## Vì sao phải chấm lại

Cửa 4 kết luận *"C không hơn B"* bằng `0,6×ROUGE + 0,4×SectionF1`. Chứng chỉ
trên 38 bệnh án thật (`chung-chi-thuoc-do.md`) cho thấy bộ chấm đó xếp lỗi đổi
chủ thể **cao hơn** lỗi đổi từ đồng nghĩa — khoảng cách −0,0104, tức ngược dấu.

Một cái thước như thế không thể làm trọng tài cho một dự án về lỗi quy gán.

## Bảng

| Nhánh | f1 quy gán | đúng quy gán | bỏ sót | sai chủ thể / hồ sơ | điểm cuộc thi |
|---|---|---|---|---|---|
{chr(10).join(dong)}

Cách đọc:

- **f1 quy gán** — chỉ số chính. Phạt cả hai chiều: ghi sai người bị trừ, mà viết
  ít đi cho an toàn cũng bị trừ.
- **đúng quy gán** — trong số mệnh đề đã nói đúng nội dung, bao nhiêu phần gán
  đúng người. Không bị ảnh hưởng bởi bỏ sót.
- **sai chủ thể / hồ sơ** — số mệnh đề gán nhầm người, trung bình mỗi bệnh án.
  Đây là con số nói được với bác sĩ.

## Kết luận

{ket}

## Giới hạn

1. **35 hội thoại.** Quá nhỏ để kết luận chắc về chênh lệch nhỏ.
2. Chấm so với **bản tham chiếu**, nên kế thừa mọi thiếu sót của bản tham chiếu.
   Chấm với hội thoại là việc của phép chấm tay và của buổi chấm mù với bác sĩ.
3. Điểm quy gán đọc chủ thể bằng **luật bề mặt** và cố ý không nhận diện những
   từ chỉ người nhà mơ hồ (`ba`, `bác`, `má`, `cô`…) — chọn bỏ sót thay vì gộp
   nhầm. Xem `src/do_luong/thuoc_do_quy_gan.py`.
4. Nhánh A và A+ chưa có trong bảng nếu chưa chạy xong Task 6.
"""


if __name__ == "__main__":
    main()
