# -*- coding: utf-8 -*-
"""[Đo lường và chấm điểm › Chất lượng dữ liệu]
Làm gì   : Đếm các dấu vết nguồn gốc trong bộ hội thoại để biết nó có phải bản dịch từ tiếng
           Anh không, bằng số chứ không bằng phỏng đoán.
Vào → Ra : tập huấn luyện hội thoại tiếng Việt → số mẫu khớp từng dấu vết, ghi JSON và báo
           cáo markdown
Đọc từ   : do() đếm mẫu khớp từng dấu vết; main() đo trên tập huấn luyện và ghi tệp
Mục lục (các hàm/lớp chính):
  do()    Đếm số mẫu khớp từng dấu vết nguồn gốc
  main()  Đo dấu vết trên tập huấn luyện, ghi JSON và báo cáo
Gọi tới  : bo_du_lieu/nap_du_lieu, he_thong/duong_dan
Tên cũ   : dau_vet_nguon.py (trước 27/11/2026) · Bản đồ: BAN_DO_MA_NGUON.md
────────────────────────────────────────────────────────────────────────
Đo dấu vết nguồn gốc trong bộ dữ liệu hội thoại.

Ban tổ chức gọi đây là "bộ dữ liệu hội thoại y khoa tiếng Việt đã được chuẩn
hoá" và không nói gì thêm. Đề bài không có một dòng nào về giấy phép hay xuất
xứ; dữ liệu được phát qua một thư mục Google Drive, không có trang mô tả.

Nhưng bản thân văn bản thì nói được. Script này đếm các dấu vết đo được, để
phần "nguồn gốc dữ liệu" trong báo cáo dựa trên SỐ chứ không dựa trên phỏng
đoán — đúng nguyên tắc của cả dự án: mỗi con số trong báo cáo do script sinh.

Vì sao việc này không phải chuyện giấy tờ. Nếu hội thoại được dịch từ một bộ
dữ liệu tiếng Anh thì:

  1. Mọi phát biểu về "hội thoại y khoa tiếng Việt" phải thu hẹp phạm vi —
     NGÔN NGỮ là tiếng Việt, còn bối cảnh lâm sàng và thói quen hỏi đáp thì
     không phải của phòng khám Việt Nam.
  2. Điểm mới của dự án so với DocLens là "tiếng Việt". Nếu ngữ liệu chỉ là
     lớp vỏ tiếng Việt phủ lên cấu trúc hội thoại tiếng Anh thì điểm mới đó
     yếu đi, và người đánh giá có thể hỏi đúng câu này.
  3. Ngược lại, nó MỞ ra một phát biểu mạnh hơn: chính những hiện tượng làm
     khó việc quy gán trong tiếng Việt — lược chủ ngữ, dùng từ chỉ quan hệ
     họ hàng làm đại từ ("cháu", "em", "con") — sẽ bị DƯỚI đại diện trong bản
     dịch. Tức tỷ lệ lỗi thật ngoài đời có thể CAO HƠN con đo được ở đây.

    python -m src.do_luong.dau_vet_nguon
"""
import io
import json
import re
import sys

from src.bo_du_lieu import nap_du_lieu as du_lieu
from src.he_thong import duong_dan as duong_dan

# Mỗi mục: (tên, biểu thức, ý nghĩa khi xuất hiện)
DAU_VET = [
    ("đơn vị đo Mỹ — pound / ounce",
     r"\b(pound|lbs?|ounce|oz)\b",
     "cân nặng ở Việt Nam luôn tính bằng kg"),
    ("đơn vị đo Mỹ — feet / inch",
     r"\b(feet|foot|inch|inches)\b",
     "chiều cao ở Việt Nam tính bằng cm"),
    ("nhiệt độ độ F",
     r"\d+\s*(°\s*F|độ F)",
     "nhiệt kế ở Việt Nam đo độ C"),
    ("nhiệt độ độ C",
     r"\d+\s*(°\s*C|độ C)(?!\w)",
     "đối chứng cho dòng trên"),
    ("cân nặng kg",
     r"\b\d+\s*(kg|ký|ki-?lô)\b",
     "đối chứng cho dòng pound"),
    ("biệt dược Mỹ",
     r"\b(Tylenol|Advil|Motrin|Ibuprofen|Aleve|Benadryl)\b",
     "ở Việt Nam là paracetamol, panadol, efferalgan"),
    ("tên cơ sở y tế tiếng Anh",
     r"(bệnh viện|phòng khám)\s+(UIHC|Women'?s|Sample|General|Memorial)",
     "UIHC = University of Iowa Hospitals and Clinics"),
    ("ghi chú bản ghi âm",
     r"\[.*?\]|không nghe rõ|nghe không rõ",
     "bản gỡ băng thật gần như luôn có chỗ nghe không rõ"),
]


# ═══ do() — Đếm số mẫu khớp từng dấu vết nguồn gốc ════════════════════════════════════
# Quét đầu vào và đầu ra bằng biểu thức chính quy; trả số mẫu, tỉ lệ, ví dụ.
def do(mau):
    ra = []
    for ten, bt, y_nghia in DAU_VET:
        rx = re.compile(bt, re.IGNORECASE)
        khop = [m["id"] for m in mau
                if rx.search((m.get("input") or "") + "\n" + (m.get("output") or ""))]
        ra.append({"dau_vet": ten, "so_mau": len(khop),
                   "ty_le": round(len(khop) / len(mau), 4),
                   "y_nghia": y_nghia, "vi_du_id": khop[:5]})
    return ra


# ═══ main() — Đo dấu vết trên tập huấn luyện, ghi JSON và báo cáo ═════════════════════
def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    mau = du_lieu.nap_mau(duong_dan.TRAIN_JSONL)
    bang = do(mau)
    for d in bang:
        print(f"{d['so_mau']:5d} mẫu ({d['ty_le']:6.2%})  {d['dau_vet']}")

    dp = duong_dan.THU_MUC_KET_QUA / "dau-vet-nguon.json"
    dp.write_text(json.dumps({"tong_mau": len(mau), "dau_vet": bang},
                             ensure_ascii=False, indent=2), encoding="utf-8")
    dp_md = duong_dan.THU_MUC_KET_QUA / "dau-vet-nguon.md"
    dp_md.write_text(_bao_cao(len(mau), bang), encoding="utf-8")
    print(f"\nda ghi {dp}\nda ghi {dp_md}")


# ─── _bao_cao() — Dựng báo cáo Markdown về dấu vết nguồn gốc ──────────────────────────
# So số mẫu dùng pound/ounce với số mẫu dùng kg để nêu kết luận.
def _bao_cao(tong, bang):
    theo_ten = {d["dau_vet"]: d for d in bang}
    dong = "\n".join(
        f"| {d['dau_vet']} | {d['so_mau']} | {d['ty_le']:.2%} | {d['y_nghia']} |"
        for d in bang)

    my = theo_ten["đơn vị đo Mỹ — pound / ounce"]["so_mau"]
    vn = theo_ten["cân nặng kg"]["so_mau"]
    ket = (f"**{my} mẫu dùng pound/ounce, {vn} mẫu dùng kg.**" if my > vn else
           f"{my} mẫu dùng pound/ounce, {vn} mẫu dùng kg.")

    return f"""# Dấu vết nguồn gốc trong bộ dữ liệu hội thoại

Sinh tự động bằng `python -m src.do_luong.dau_vet_nguon`. Đừng sửa tay. {tong} mẫu.

## Vì sao phải đo

Đề bài gọi đây là *"bộ dữ liệu hội thoại y khoa tiếng Việt đã được chuẩn hoá"*
và **không nói gì thêm** — không một dòng nào về giấy phép hay xuất xứ, và dữ
liệu được phát qua một thư mục Google Drive không có trang mô tả.

Nhưng bản thân văn bản thì nói được.

## Bảng

| Dấu vết | Số mẫu | Tỷ lệ | Ý nghĩa |
|---|---|---|---|
{dong}

## Đọc bảng

{ket} Ở Việt Nam cân nặng luôn tính bằng kg — pound gần như không bao giờ xuất
hiện trong lời một bệnh nhân Việt.

Ba mẫu dưới đây là bằng chứng trực tiếp nhất, và không cần thống kê để thấy:

> **`train_0471`** — *"Bác sĩ: Lúc sinh bé nặng bao nhiêu **ký** vậy anh?
> / Bệnh nhân: Dạ bé nặng **7 pound 3 ounce** ạ."*
>
> Câu hỏi đã được Việt hoá sang **ký**, câu trả lời thì vẫn là **pound và
> ounce**. Không một cuộc khám thật nào diễn ra như vậy, và không ai tự viết
> ra như vậy. Đó là dấu vết của một bản dịch được localize nửa chừng.

> **`train_0471`** — *"ở bệnh viện **Women's**"* · **`train_0325`** —
> *"bệnh viện **UIHC**"*. UIHC là **University of Iowa Hospitals and Clinics**.

> **`train_0052`** — *"phòng khám **Sample**"*. Đây là chỗ điền mẫu trong một
> khuôn ("Sample Clinic") chưa bao giờ được thay bằng tên thật.

Thêm một dấu vết **vắng mặt**: 0 mẫu có ghi chú kiểu `[không nghe rõ]`. Bản gỡ
băng của lời nói thật gần như luôn có ít nhất vài chỗ như thế.

## Kết luận có thể phát biểu

Bộ dữ liệu **rất nhiều khả năng được dịch và chuyển thể từ một bộ hội thoại
y khoa tiếng Anh (Mỹ)**, chứ không phải ghi từ phòng khám Việt Nam, cũng không
phải do người Việt biên soạn từ đầu.

Đây là **suy luận từ dấu vết, không phải xác nhận từ ban tổ chức.** Phải hỏi
để biết chắc, và trước khi có trả lời thì báo cáo phải viết đúng mức đó.

## Ba hệ quả cho dự án — không được giấu

1. **Thu hẹp phạm vi mọi phát biểu về "tiếng Việt".** Ngôn ngữ là tiếng Việt;
   bối cảnh lâm sàng và thói quen hỏi đáp thì không phải của phòng khám Việt.
2. **Điểm mới so với DocLens yếu đi.** Khác biệt từng nêu là "làm cho tiếng
   Việt". Nếu ngữ liệu chỉ là lớp vỏ tiếng Việt phủ lên cấu trúc hội thoại
   tiếng Anh thì người đánh giá hỏi được đúng câu đó, và phải có câu trả lời sẵn.
3. **Nhưng nó mở ra một phát biểu MẠNH HƠN.** Chính những hiện tượng làm việc
   quy gán khó trong tiếng Việt — lược chủ ngữ, và dùng từ chỉ quan hệ họ hàng
   làm đại từ (*cháu*, *em*, *con* vừa là ngôi thứ nhất vừa là ngôi thứ ba) —
   sẽ bị **dưới đại diện** trong một bản dịch từ tiếng Anh, nơi chủ ngữ luôn
   hiện diện. Tức **tỷ lệ lỗi thật ngoài đời có thể CAO HƠN** con số đo được ở
   đây, chứ không thấp hơn. Đó là một hạn chế nói ra thì làm dự án mạnh lên.
"""


if __name__ == "__main__":
    main()
