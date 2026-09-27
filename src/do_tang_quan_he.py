# -*- coding: utf-8 -*-
"""Do tang sinh cap ung vien tren du lieu THAT, va tren bo chan doan.

Cau hoi: doi vai (chuong trinh liet ke — mo hinh/luat phan) co lam co che loi
KHAI HOA tren hoi thoai that khong, trong khi cach cu duoc 0/282?

    python -m src.do_tang_quan_he --trich data/trich_phat_trien_3072.jsonl \\
                                  --tap phat_trien
"""
import argparse
import io
import json
import sys
from collections import Counter

from src import du_lieu, duong_dan, phat_bieu, thuc_the, ung_vien_quan_he as uv


def _luot(hoi_thoai):
    cac = thuc_the.tach_luot(hoi_thoai)
    return ({so: nd for so, _, nd in cac},
            {so: vai for so, vai, _ in cac if vai})


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

        # So quan he ma MO HINH tu danh dau, de doi chieu voi cach cu.
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


def _bao_cao(t, tap):
    return f"""# Tầng sinh cặp ứng viên quan hệ — đo trên tập `{tap}`

Sinh tự động bằng `python -m src.do_tang_quan_he`. Đừng sửa tay.

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
