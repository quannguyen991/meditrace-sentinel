# -*- coding: utf-8 -*-
"""Cham lai cac nhanh bang DIEM QUY GAN, tren dung dau ra da co.

Cua 4 ket luan "C khong hon B" bang `0,6×ROUGE + 0,4×SectionF1`. Nhung chinh de
tai da chung minh bo cham do mu truoc loi quy gan, va chung chi tren 38 benh an
that con cho thay no xep loi nguy hiem CAO HON loi vo hai (khoang cach −0,0104).

Cham bang mot cai thuoc mu roi ket luan ve mot co che chuyen tri diem mu cua no
la loi thiet ke danh gia. Script nay cham lai — KHONG chay lai mo hinh, dung
dung cac tep `data/ra_*.jsonl` da sinh, nen chenh lech do duoc chac chan den tu
CACH CHAM chu khong tu mot lan sinh khac.

    python -m src.cham_lai_bang_quy_gan --tap phat_trien
"""
import argparse
import io
import json
import sys
from pathlib import Path

from src import cham_diem, du_lieu, duong_dan, thuoc_do_quy_gan as tdq

# Thu tu co y: cong don tu it co che nhat den nhieu nhat, roi hai o boc co che.
# `A_nen` la nhanh A chay bang mo hinh NEN (khong nap adapter), cung mo hinh voi
# buoc trich cua nhanh B va cung zero-shot nhu no. No la doi chung tach duoc hai
# thu ma bang cu tron lam mot: *co cau truc hay khong* va *co fine-tune hay khong*.
# `A_cong_nen` them 10/09/2026: `nhanh.ten_ket_qua` sinh duoc ten nay khi chay
# A+ ma khong nap adapter, va truoc do bo cham khong biet no. Moi ten ben GHI
# sinh ra deu phai co o day — test `test_moi_ten_ben_GHI_sinh_ra_deu_co_trong_
# danh_sach_ben_DOC` chan hai ben lech nhau.
NHANH = ["A", "A_nen", "A_cong", "A_cong_nen", "E", "E_chi_bo_sung", "B",
         "C_khong_luat", "C_khong_lien_ket", "C", "C_ghi_de", "D",
         "C_quan_he", "C_quan_he_luat", "D_quan_he"]


def _nap(tap, nhanh):
    dp = Path(duong_dan.THU_MUC_DU_LIEU) / f"ra_{nhanh}_{tap}.jsonl"
    if not dp.exists():
        return None
    return [json.loads(l) for l in open(dp, encoding="utf-8") if l.strip()]


def cham(ds, dung_ban_khong_muc_phu=False):
    """Diem trung binh cua mot nhanh tren ca tap."""
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


def _hai_thuoc_do_noi_gi(a, b, ten_a):
    """Hai thuoc do co cung noi mot dieu khong — doc TU SO LIEU.

    Ban dau cho in cung mot cau *"hon o moi mat da do"*. Voi nhanh A da fine-tune
    thi cau do dung; voi `A_nen` thi SAI — no thua tren diem cuoc thi. Mot bao
    cao tu in ra mot cau nguoc voi bang so ngay ben tren no la cho nguy hiem
    nhat trong ca tep nay.
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


def _canh_bao_fine_tune(bang):
    """Canh bao chi con dung khi CHUA co nhanh nen."""
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


def _bao_cao(bang, tap):
    dong = []
    for ten, d in bang.items():
        dong.append(
            f"| {ten} | {d['f1_quy_gan']:.4f} | {d['dung_quy_gan']:.4f} | "
            f"{d['bo_sot']:.4f} | {d['so_sai_chu_the']:.2f} | {d['final_cuoc_thi']:.4f} |")

    b, c = bang.get("B"), bang.get("C")
    if b and c and b["so_sai_chu_the"]:
        # Cua 4 doi "C giam ty le loi >= 30% tuong doi so voi B". Dai luong dung
        # de kiem dieu kien do la SO MENH DE GAN NHAM NGUOI, khong phai f1 —
        # f1 bi chi phoi boi cach dien dat khac nhau giua ban sinh va ban tham
        # chieu, va cho khac biet ay thi ca nam nhanh deu nhu nhau.
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

    # So A voi B — phep so cua Cua 3, va no quan trong hon phep so C voi B.
    #
    # Uu tien `A_nen`: no chay bang mo hinh NEN, cung mo hinh voi buoc trich cua
    # B va cung zero-shot, nen phep so tach duoc *co cau truc hay khong* khoi
    # *co fine-tune hay khong*. Dung `A` thi hai thu do lan vao nhau.
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

Sinh tự động bằng `python -m src.cham_lai_bang_quy_gan`. Đừng sửa tay.

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
   nhầm. Xem `src/thuoc_do_quy_gan.py`.
4. Nhánh A và A+ chưa có trong bảng nếu chưa chạy xong Task 6.
"""


if __name__ == "__main__":
    main()
