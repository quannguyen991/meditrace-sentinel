# -*- coding: utf-8 -*-
"""Chay phep thu bit nhan nguoi noi tren GPU, roi doi chieu voi ban goc.

    python -m src.do_bit_nhan --model Qwen/Qwen3-4B --tap phat_trien \\
        --goc data/trich_phat_trien_3072.jsonl

Ban goc KHONG chay lai — dung dung tep trich da co, vi chay lai la mot lan sinh
khac va chenh lech do duoc se lan lon giua "do bit nhan" voi "do sinh lai".
"""
import argparse
import io
import json
import sys

from src import bakeoff, bit_nhan, du_lieu, duong_dan


def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tap", default="viet_phat_trien")
    ap.add_argument("--goc", default="data/trich_phat_trien_3072.jsonl")
    ap.add_argument("--max-token", type=int, default=3072)
    ap.add_argument("--so-mau", type=int, default=0, help="0 = het")
    ap.add_argument("--tu-json", action="store_true",
                    help="Sinh lai bao cao tu tep JSON da co, KHONG can GPU")
    a = ap.parse_args()

    from src import du_lieu as _dl
    _dl.chan_tap_ngoai(a.tap)
    _dl.chan_tap_khoa(a.tap)

    if a.tu_json:
        ten = a.model.replace("/", "-")
        dp = duong_dan.THU_MUC_KET_QUA / f"bit-nhan-{ten}.json"
        d = json.loads(dp.read_text(encoding="utf-8"))
        dp_md = duong_dan.THU_MUC_KET_QUA / f"bit-nhan-{ten}.md"
        dp_md.write_text(bao_cao(d.get("model", a.model), d["tong"]), encoding="utf-8")
        print(json.dumps(d["tong"], ensure_ascii=False, indent=2))
        print(f"da ghi {dp_md}")
        return

    goc = {}
    for dong in open(a.goc, encoding="utf-8"):
        if dong.strip():
            k = json.loads(dong)
            goc[k["id"]] = k
    print(f"ban goc: {len(goc)} mau tu {a.goc}")

    mau = du_lieu.nap_mau(duong_dan.THU_MUC_DU_LIEU / f"{a.tap}.jsonl")
    mau = [m for m in mau if m["id"] in goc]
    if a.so_mau:
        mau = mau[:a.so_mau]
    da_bit = [bit_nhan.bit_mau(m) for m in mau]
    print(f"se chay {len(da_bit)} mau da bit nhan tren {a.model}")

    luu = str(duong_dan.THU_MUC_DU_LIEU / f"trich_bit_nhan_{a.tap}.jsonl")
    tok, model, prefix_fn = bakeoff.nap(a.model, ep_json=False)
    kq = bakeoff.trich(tok, model, prefix_fn, da_bit,
                       max_token=a.max_token, luu_dan=luu)

    tong = {"so_hoi_thoai": 0, "so_phat_bieu_goc": 0, "so_phat_bieu_bit": 0,
            "so_khop_noi_dung": 0, "so_doi_y": 0, "so_chu_the_la_nhan": 0}
    tung = []
    for k in kq:
        g = goc.get(k["id"])
        if g is None:
            continue
        d = bit_nhan.doi_chieu(g.get("phat_bieu") or [], k.get("phat_bieu") or [])
        d["id"] = k["id"]
        tung.append(d)
        tong["so_hoi_thoai"] += 1
        for t in ("so_phat_bieu_goc", "so_phat_bieu_bit", "so_khop_noi_dung",
                  "so_doi_y", "so_chu_the_la_nhan"):
            tong[t] += d[t]

    kh = tong["so_khop_noi_dung"] or 1
    tong["ty_le_doi_y"] = round(tong["so_doi_y"] / kh, 4)
    tong["ty_le_chu_the_la_nhan"] = round(tong["so_chu_the_la_nhan"] / kh, 4)

    print(json.dumps(tong, ensure_ascii=False, indent=2))
    ten = a.model.replace("/", "-")
    dp = duong_dan.THU_MUC_KET_QUA / f"bit-nhan-{ten}.json"
    dp.write_text(json.dumps({"model": a.model, "tong": tong,
                              "tung_hoi_thoai": tung},
                             ensure_ascii=False, indent=2), encoding="utf-8")
    dp_md = duong_dan.THU_MUC_KET_QUA / f"bit-nhan-{ten}.md"
    dp_md.write_text(bao_cao(a.model, tong), encoding="utf-8")
    print(f"da ghi {dp}\nda ghi {dp_md}")


def _moi_lan_doi_deu_ve_nhan(t):
    """Ban goc luon co ten vai, nen moi ban ghi co `chu_the` la nhan trung tinh
    deu la mot lan DOI Y. Neu hai con so bang nhau thi suy ra: khong co lan doi
    nao la tu NGUOI NAY sang NGUOI KIA — tat ca deu la roi ve cai nhan.

    Phan biet nay quan trong hon ca ty le doi y, va no la ket luan manh nhat rut
    ra duoc tu phep thu.
    """
    doi = t.get("so_doi_y", 0)
    nhan = t.get("so_chu_the_la_nhan", 0)
    if doi == 0:
        return ""
    if doi != nhan:
        return (f"Trong {doi} lần đổi ý, có **{doi - nhan}** lần đổi từ người này "
                f"sang người khác — không phải chỉ rơi về nhãn. Đó là nhóm đáng đọc "
                f"tay trước tiên: mô hình vẫn nêu tên một người, chỉ là người khác.")
    return (
        f"**Cả {doi}/{doi} lần đổi ý đều rơi về chính cái nhãn trung tính.** Không "
        f"có lần nào đổi từ người này sang người khác.\n\n"
        f"Đây là kết luận mạnh nhất rút ra được: ở đúng những phát biểu ấy, chủ thể "
        f"**chưa bao giờ được đọc từ nội dung**. Bỏ tên vai đi thì mô hình không còn "
        f"gì để bám, nên nó chép lại cái nhãn. Trên bản gốc chúng vẫn được tính là "
        f"gán đúng — vì trong hội thoại khám bệnh, người nói thường đúng là chủ thể.\n\n"
        f"Đó chính là câu trả lời cho phản biện *\"mô hình to hơn là hết lỗi chứ gì\"*: "
        f"mô hình lớn hơn đi theo đường tắt ấy **trúng nhiều hơn**, chứ chưa có bằng "
        f"chứng nào cho thấy nó **thôi đi theo đường tắt**. Muốn biết thì phải chạy "
        f"lại phép thử này ở 8B và so tỷ lệ, chứ không so độ chính xác.")


def bao_cao(model, t):
    """Tach rieng de sinh lai bao cao tu tep JSON ma khong can GPU."""
    doi = t.get("ty_le_doi_y", 0.0)
    nhan = t.get("ty_le_chu_the_la_nhan", 0.0)

    if nhan > 0.10:
        ket = (f"**{nhan:.1%} số phát biểu có `chu_the` chính là cái nhãn được chép "
               f"lại** (`Người 2`). Đó là bằng chứng trực tiếp nhất: ở những phát "
               f"biểu ấy mô hình không rút được chủ thể từ nội dung, nó chỉ chép "
               f"lại vai của lượt thoại.")
    else:
        ket = (f"Chỉ {nhan:.1%} số phát biểu có `chu_the` là cái nhãn chép lại. "
               f"Mô hình phần lớn vẫn gọi tên chủ thể theo nội dung "
               f"(`trẻ`, `mẹ`), chứ không bám vào nhãn vai.")

    if doi >= 0.20:
        ket2 = (f"**Tỷ lệ đổi ý {doi:.1%}** — bịt tên vai đi thì hơn một phần năm số "
                f"phát biểu đổi chủ thể, dù nội dung không đổi một chữ. Mô hình có "
                f"dựa đáng kể vào nhãn vai.")
    elif doi >= 0.05:
        ket2 = (f"**Tỷ lệ đổi ý {doi:.1%}** — có phụ thuộc vào nhãn vai nhưng không "
                f"lớn. Cần cỡ mẫu lớn hơn mới nói được nó tập trung ở nhóm ca nào.")
    else:
        ket2 = (f"**Tỷ lệ đổi ý chỉ {doi:.1%}** — bịt nhãn gần như không đổi kết quả. "
                f"Trên cỡ mẫu này, mô hình đọc chủ thể từ NỘI DUNG chứ không đi theo "
                f"nhãn vai. Đó là kết quả âm cho giả thuyết đường tắt, và phải báo "
                f"cáo đúng như thế.")

    return f"""# Phép thử bịt nhãn người nói — `{model}`

Sinh tự động bằng `python -m src.do_bit_nhan`. Đừng sửa tay.

## Câu hỏi

Độ chính xác `chu_the` không trả lời được câu phản biện *"mô hình to hơn là hết
lỗi chứ gì"*, vì trong hội thoại khám bệnh **chủ thể chính là người nói ở phần
lớn lượt**. Một mô hình chỉ làm đúng một việc — gán triệu chứng cho người vừa
nói — vẫn đạt độ chính xác rất cao. Đường tắt đúng hầu hết thời gian, và nó sai
đúng vào nhóm ca nguy hiểm nhất: người nhà kể hộ bệnh nhân.

Nên phải tách **biết** khỏi **đoán trúng**: chạy trích xuất hai lần trên cùng
hội thoại, một lần giữ tên vai (`Bác sĩ:` / `Người nhà:`), một lần thay bằng
nhãn trung tính (`Người 1:` / `Người 2:`). Nội dung không đổi một chữ, đáp án
đúng cũng không đổi.

## Kết quả

| Chỉ tiêu | Số |
|---|---|
| Hội thoại | {t.get('so_hoi_thoai', 0)} |
| Phát biểu — bản gốc | {t.get('so_phat_bieu_goc', 0)} |
| Phát biểu — bản bịt nhãn | {t.get('so_phat_bieu_bit', 0)} |
| Ghép được theo nội dung | {t.get('so_khop_noi_dung', 0)} |
| **Đổi chủ thể sau khi bịt** | **{t.get('so_doi_y', 0)}** ({doi:.1%}) |
| **`chu_the` chính là cái nhãn** | **{t.get('so_chu_the_la_nhan', 0)}** ({nhan:.1%}) |

## Đọc kết quả

{ket}

{ket2}

{_moi_lan_doi_deu_ve_nhan(t)}

## Giới hạn, nói thẳng

1. **Bịt nhãn không xoá được THỨ TỰ LƯỢT.** Bác sĩ gần như luôn nói trước, nên
   `Người 1` vẫn đoán được là bác sĩ. Phép thử đo phần phụ thuộc vào **tên vai**,
   không đo phần phụ thuộc vào **vị trí**.
2. Chỉ ghép được những phát biểu **trùng nội dung** giữa hai lần chạy. Phát biểu
   chỉ xuất hiện ở một bên thì không đếm — và số đó tự nó cũng là một tín hiệu
   (bịt nhãn làm mô hình trích ra tập phát biểu khác), nhưng chưa phân tích.
3. Cỡ mẫu ở đây nhỏ. Chưa tách được kết quả theo nhóm ca (có người nhà kể hộ
   hay không) — mà đó mới là chỗ giả thuyết đường tắt dự đoán sẽ khác nhau nhất.
"""


if __name__ == "__main__":
    main()
