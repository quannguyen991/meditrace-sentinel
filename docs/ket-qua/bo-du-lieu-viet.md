# Bộ hội thoại khám bệnh Việt Nam — sinh bằng luật

Sinh tự động bằng `python -m src.sinh_hoi_thoai_viet --so-ca 5000`.
Đừng sửa tay: sửa tay rồi chạy lại là mất.

## Vì sao tự dựng bộ này

Bộ của cuộc thi có dấu vết rõ là **bản dịch từ một bộ hội thoại y khoa tiếng
Anh (Mỹ)** — xem `docs/ket-qua/dau-vet-nguon.md`. Hậu quả nằm đúng chỗ dự án
quan tâm: hai hiện tượng làm việc quy gán khó nhất trong tiếng Việt đều bị
**dưới đại diện** trong một bản dịch, vì tiếng Anh gần như luôn có chủ ngữ.

1. **Lược chủ ngữ.** *"Sốt hai hôm rồi"*, *"Nôn từ tối qua"* — người đọc phải
   suy chủ thể từ ngữ cảnh.
2. **Từ chỉ quan hệ họ hàng làm đại từ.** *cháu*, *em*, *con* vừa là cách người
   nói tự xưng, vừa là cách gọi người thứ ba.

Bộ này sinh ra đúng hai hiện tượng đó, ở mật độ thật.

## Sinh bằng LUẬT, không bằng mô hình ngôn ngữ

Đây là ràng buộc số 1 của dự án, và lý do không phải hình thức: mô hình ngôn ngữ
viết hội thoại **sạch hơn người nói thật** — nó gần như luôn ghi rõ chủ ngữ ở
mỗi lượt. Nên đúng những ca khó nhất sẽ hiếm đi, và đường tắt *"chủ thể chính là
người vừa nói"* sẽ trúng nhiều hơn bình thường. Sai lệch đó **một chiều**: luôn
về phía làm vấn đề trông nhẹ hơn thật.

## Quy mô

| | |
|---|---|
| Số ca | **5000** (hội thoại không trùng nhau: 5000) |
| Khuôn bệnh | 270 |
| Tổng lượt thoại | 87097 · trung bình 17.4 lượt/ca |
| Tổng từ | 1,525,126 |
| Mệnh đề trong đáp án | 47530 |
| **Mệnh đề KHÔNG thuộc bệnh nhân** | **2290** (4.8%) |
| Ca nhi | 1137 |
| Có người nhà kể hộ | 1944 |

## Thứ bộ của cuộc thi không có: đáp án có cấu trúc

Mỗi ca kèm trường `dap_an` — danh sách mệnh đề, mỗi mệnh đề ghi **chủ thể thật**,
mốc thời gian thật, tình huống thật, và số lượt thoại làm bằng chứng.

Nhờ đó đo được độ chính xác quy gán **chính xác tuyệt đối**, thay vì ước lượng
qua một bản tham chiếu dạng văn xuôi. Đó cũng là chỗ gỡ được hạn chế nặng nhất
của `thuoc_do_quy_gan` — nó nhạy với cách đóng gói câu khi phải đối chiếu văn
xuôi với văn xuôi.

## Bẫy quy gán

| Bẫy | Số ca | Tỷ lệ |
|---|---|---|
| `nguoi_nha_ke_ho` | 1944 | 38.9% |
| `nguoi_ke_benh_minh` | 1347 | 26.9% |
| `tien_su_gia_dinh` | 666 | 13.3% |
| `luoc_chu_ngu` | 636 | 12.7% |
| `dien_bien` | 631 | 12.6% |
| `hoi_khong_dap` | 630 | 12.6% |
| `bo_sung` | 608 | 12.2% |
| `dinh_chinh` | 600 | 12.0% |
| `gia_dinh` | 596 | 11.9% |
| `dai_tu_ho_hang` | 587 | 11.7% |
| `mau_thuan` | 524 | 10.5% |
| `di_ung_nguoi_nha` | 277 | 5.5% |
| `nguon_khac_nhau` | 238 | 4.8% |
| `lieu_dinh_chinh` | 137 | 2.7% |

Ý nghĩa từng bẫy:

- `nguoi_nha_ke_ho` — người nhà kể thay bệnh nhân. Người nói ≠ chủ thể.
- `tien_su_gia_dinh` — người nhà kể bệnh **của chính họ** xen vào giữa. Đây là
  bẫy quan trọng nhất: người nói và chủ thể là một, nhưng chủ thể **không phải**
  bệnh nhân.
- `di_ung_nguoi_nha` — dị ứng thuộc về người nhà, bệnh nhân thì *chưa ghi nhận*.
- `luoc_chu_ngu` — câu không có chủ ngữ.
- `dai_tu_ho_hang` — *cháu*/*con* vừa là người nói vừa là người được nói tới.
- `dinh_chinh` — người nói tự sửa lại con số vừa nêu. Đáp án giữ **bản đã sửa**.
- `dien_bien` — hai mốc thời gian, **cả hai đều đúng**, đáp án giữ cả hai.
- `gia_dinh` — câu điều kiện *"nếu mai còn…"*, **không** được thành triệu chứng.
- `hoi_khong_dap` — bác sĩ hỏi, không ai trả lời. Bệnh án **không** được nhắc tới.

## Bốn cái bẫy khi sinh dữ liệu có đáp án — đều đã chặn và có test

1. **Thay thế làm bài toán không giải được** → chỉ **chèn thêm**, giữ nguyên lượt gốc.
2. **Hai khẳng định khác nhau không phải mâu thuẫn** → `dien_bien` giữ cả hai.
3. **Độ dài lộ đáp án** → số lượt không phụ thuộc vào việc ca đó có bẫy hay không.
4. **Vị trí lộ đáp án** → vị trí bẫy rải đều, không dính ở cuối.

Thêm một nhóm test về **ngôn ngữ**, vì một bộ dữ liệu tiếng Việt sai vai giao
tiếp thì mô hình sẽ học đúng cái sai đó: bệnh nhân không dùng *"Ừ"* với bác sĩ ·
tiểu từ đề nghị (*nhé, nghen*) không gắn vào câu hỏi · không trộn giọng hai miền
trong một cuộc · bệnh phải hợp lứa tuổi · mốc thời gian phải hợp diễn tiến bệnh.

## Giới hạn, nói thẳng

1. **Đây là dữ liệu mô phỏng, không phải hội thoại người thật.** Mọi kết luận rút
   ra từ nó phải nói rõ điều đó. Nó dùng để đo **cơ chế** — quy gán đúng hay sai
   khi có bẫy — chứ không đo tần suất lỗi ngoài đời.
2. **5000 ca sinh từ 270 khuôn bệnh.** Đơn vị độc lập là
   số khuôn, không phải số dòng. Đừng viết *"5000 ca đủ để kết luận"*.
3. **Lời thoại do luật ghép**, nên đều đặn hơn lời nói thật: không có ngập ngừng,
   không nói chen, không câu bỏ dở. Bộ này **không** thay được dữ liệu thật.
4. Chưa có bác sĩ duyệt. Trước khi dùng cho phần kết luận, cần bác đọc một mẫu
   ngẫu nhiên và xác nhận các ca là hợp lý về lâm sàng.
