# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Phép đo]
Làm gì   : Đếm cặp quan hệ ứng viên mà chương trình liệt kê trên dữ liệu thật và bộ chẩn
           đoán, để xem cơ chế quan hệ có khai hoa không.
Vào → Ra : tệp trích (--trich) và tập hội thoại (--tap) → số cặp ứng viên theo ca, ghi JSON
           và báo cáo markdown
Đọc từ   : do() đếm cặp ứng viên trên từng ca; main() ghi JSON và báo cáo
Mục lục (các hàm/lớp chính):
  do()        Đếm cặp quan hệ ứng viên mà chương trình sinh ra
  main()      Chạy dòng lệnh đo tầng quan hệ rồi ghi JSON và báo cáo
  _bao_cao()  Dựng báo cáo markdown về tầng cặp ứng viên
Gọi tới  : bo_du_lieu/nap_du_lieu, duong_ong/b1_cau_truc_menh_de,
           duong_ong/b2_gom_nguoi_thuc_the, duong_ong/b3_sinh_cap_ung_vien_quan_he,
           he_thong/duong_dan
Tên cũ   : do_tang_quan_he.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đo tầng sinh cặp ứng viên trên dữ liệu THẬT, và trên bộ chẩn đoán.

Câu hỏi: đổi vai (chương trình liệt kê — mô hình/luật phân) có làm cơ chế lỗi
KHAI HOA trên hội thoại thật không, trong khi cách cũ được 0/282?

    python -m src.do_luong.do_tang_quan_he --trich data/trich_phat_trien_3072.jsonl \\
                                  --tap phat_trien
"""
import argparse
import io
import json
import sys
from collections import Counter

from src.bo_du_lieu import nap_du_lieu as du_lieu
from src.he_thong import duong_dan as duong_dan
from src.duong_ong import b1_cau_truc_menh_de as phat_bieu
from src.duong_ong import b2_gom_nguoi_thuc_the as thuc_the
from src.duong_ong import b3_sinh_cap_ung_vien_quan_he as uv


# ─── _luot() — Tách hội thoại thành lượt và người nói theo số lượt ────────────────────
def _luot(hoi_thoai):
    cac = thuc_the.tach_luot(hoi_thoai)
    return ({so: nd for so, _, nd in cac},
            {so: vai for so, vai, _ in cac if vai})


# ═══ do() — Đếm cặp quan hệ ứng viên mà chương trình sinh ra ══════════════════════════
# Cộng dồn thống kê từng hội thoại, kèm số quan hệ mà mô hình tự đánh dấu để so với cách
# cũ.
def do(ds_trich, mau_theo_id, toi_da=uv.TOI_DA_MAC_DINH):
    tong = Counter()
    theo_hoi_thoai = []
    for d in ds_trich:
        m = mau_theo_id.get(d["id"])
        if m is None:
            continue
        luot, nguoi_noi = _luot(m["input"])
        pbs, _ = phat_bieu.tu_json(d.get("phat_bieu") or [],
                                   nguoi_noi_theo_luot=nguoi_noi)
        tk = uv.thong_ke(pbs, luot, toi_da)

        # Số quan hệ mà MÔ HÌNH tự đánh dấu, để đối chiếu với cách cũ.
        mo_hinh_tu_danh = sum(
            1 for p in (d.get("phat_bieu") or [])
            if p.get("quan_he") not in (None, "không", ""))

        tk["mo_hinh_tu_danh"] = mo_hinh_tu_danh
        tk["id"] = d["id"]
        theo_hoi_thoai.append(tk)
        for k, v in tk.items():
            if isinstance(v, bool):
                tong[k] += int(v)
            elif isinstance(v, int):
                tong[k] += v
    return dict(tong), theo_hoi_thoai


# ═══ main() — Chạy dòng lệnh đo tầng quan hệ rồi ghi JSON và báo cáo ══════════════════
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--trich", default="data/trich_phat_trien_3072.jsonl")
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--toi-da", type=int, default=uv.TOI_DA_MAC_DINH)
    a = ap.parse_args()
    du_lieu.chan_tap_khoa(a.tap)
    du_lieu.chan_tap_ngoai(a.tap)

    ds = [json.loads(l) for l in open(a.trich, encoding="utf-8") if l.strip()]
    mau = {m["id"]: m for m in du_lieu.nap_mau(
        duong_dan.THU_MUC_DU_LIEU / f"{a.tap}.jsonl")}
    tong, tung = do(ds, mau, a.toi_da)

    tong["so_hoi_thoai"] = len(tung)
    tong["hoi_thoai_co_cap"] = sum(1 for t in tung if t["so_cap"])
    print(json.dumps(tong, ensure_ascii=False, indent=2))

    dp = duong_dan.THU_MUC_KET_QUA / f"tang-quan-he-{a.tap}.json"
    dp.write_text(json.dumps({"tong": tong, "tung_hoi_thoai": tung},
                             ensure_ascii=False, indent=2), encoding="utf-8")
    dp_md = duong_dan.THU_MUC_KET_QUA / f"tang-quan-he-{a.tap}.md"
    dp_md.write_text(_bao_cao(tong, a.tap), encoding="utf-8")
    print(f"da ghi {dp}\nda ghi {dp_md}")


# ─── _bao_cao() — Dựng báo cáo markdown về tầng cặp ứng viên ──────────────────────────
# Điền số đo vào văn bản mẫu, gồm cả phần nhận định quan hệ hiếm trong dữ liệu.
def _bao_cao(t, tap):
    return f"""# Tầng sinh cặp ứng viên quan hệ — đo trên tập `{tap}`

Sinh tự động bằng `python -m src.do_luong.do_tang_quan_he`. Đừng sửa tay.

## Vì sao có tầng này

Ở Cửa 4, trong **{t.get('so_phat_bieu', 0)} phát biểu** trích được từ
{t.get('so_hoi_thoai', 0)} hội thoại thật, mô hình tự đánh dấu quan hệ ở
**{t.get('mo_hinh_tu_danh', 0)}** bản ghi. Luật cập nhật trạng thái chạy trên
trường `quan_he`, nên nó không có gì để làm — bảng bóc cơ chế cho thấy nhánh
`C_khong_lien_ket` bằng đúng nhánh `B` tới từng chữ số.

Chẩn đoán: trích phát biểu là bài toán **liệt kê**, còn đánh dấu quan hệ là bài
toán **tự khởi phát** — mô hình phải tự nhớ rằng nó vừa ghi một bản ghi tương
tự ở đâu đó phía trước, tự quay lại đối chiếu, rồi tự thêm một trường không ai
hỏi. Trên hội thoại bốn lượt tự sinh thì làm được (15/15); trên hội thoại
10–28 lượt của người thật thì không.

Cách sửa là đổi vai: **chương trình liệt kê cặp đáng ngờ, mô hình hoặc luật chỉ
phải trả lời một câu bốn lựa chọn trên một cặp ngắn.**

## Kết quả

| Chỉ tiêu | Số |
|---|---|
| Hội thoại | {t.get('so_hoi_thoai', 0)} |
| Phát biểu | {t.get('so_phat_bieu', 0)} |
| **Mô hình tự đánh dấu quan hệ** | **{t.get('mo_hinh_tu_danh', 0)}** |
| **Cặp ứng viên chương trình liệt kê** | **{t.get('so_cap', 0)}** |
| Hội thoại có ít nhất một cặp | {t.get('hoi_thoai_co_cap', 0)} |
| Luật tự quyết được (không cần mô hình) | {t.get('luat_quyet_duoc', 0)} |
| — trong đó đính chính | {t.get('luat_dinh_chinh', 0)} |
| — trong đó diễn biến | {t.get('luat_dien_bien', 0)} |
| Cặp trùng lặp (để gộp, không phải quan hệ) | {t.get('so_trung_lap', 0)} |
| Hội thoại bị cắt bớt cặp | {t.get('bi_cat', 0)} |

## Phát hiện phải nói thẳng

Số cặp ứng viên là **{t.get('so_cap', 0)}** — nhiều hơn 0 của cách cũ, nhưng
vẫn rất thấp so với {t.get('so_phat_bieu', 0)} phát biểu.

Điều đó nói lên một điều quan trọng hơn cả cơ chế: **quan hệ giữa các phát biểu
hiếm trong chính bộ dữ liệu này.** Hội thoại khám bệnh thật ít khi nhắc lại
cùng một triệu chứng hai lần với hai giá trị khác nhau. Bộ chẩn đoán sinh bằng
luật được xây trên giả định ngược lại, nên nó cho 15/15 còn dữ liệu thật cho
gần như không có gì.

Ba hệ quả, không được giấu:

1. **Cơ chế theo dõi trạng thái không thể là đóng góp chính đo trên bộ dữ liệu
   này.** Không đủ hiện tượng để đo.
2. Con số {t.get('so_trung_lap', 0)} cặp **trùng lặp** lại đáng chú ý: khâu
   trích xuất ghi cùng một thông tin nhiều lần. Đó là một lỗi thật, đo được,
   và tầng này bắt được nó.
3. Muốn đo cơ chế quan hệ cho tử tế thì phải có bộ dữ liệu **có đính chính và
   diễn biến ở mật độ thật** — hoặc thu thập, hoặc phát biểu lại phạm vi
   kết luận. Không được lấy 15/15 trên bộ tự sinh làm bằng chứng.
"""


if __name__ == "__main__":
    main()
