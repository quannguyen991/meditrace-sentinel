# Đăng ký trước — cải thiện bộ luật trên bộ thử thách v2 (25/11/2026)

Viết **trước** khi chạy bất kỳ luật hay mô hình nào trên `data/thach_thuc_v2/`. Không sửa các ngưỡng dưới đây
sau khi đã nhìn kết quả. Nếu buộc phải sửa, ghi lý do và ngày ở cuối tệp, và báo cả hai số (trước và sau khi sửa).

## Tập đo

Sinh bằng `python -m tools.sinh_thach_thuc_v2 --the-he v2-luat-2026-11-25` (hạt 42). Mỗi tệp 40 ca, chỉ từ khuôn
**ngoài 200 khuôn gốc** và thuộc **tập phát triển** của kho mở rộng (46 khuôn đủ điều kiện). Không có khuôn huấn
luyện, không có khuôn kiểm tra cuối.

| Tệp | SHA-256 |
|---|---|
| `thach_thuc_dinh_chinh_phat_trien.jsonl` | `726f016d9359a4adc55d8ab63573f0f55b80bd0f539a1d71482c2d8f1a5c2fb9` |
| `thach_thuc_doi_chu_the_phat_trien.jsonl` | `b644dd40948fede3b60fc7c7aea71ec3358428bb3d98de2ae9a7c13a0fc423b7` |
| `thach_thuc_khong_dau_cau_phat_trien.jsonl` | `179c36ddc144d220dde0d497ccd3f7834035de14f2a3e7647ee14cc406600a37` |
| `thach_thuc_nhieu_asr_phat_trien.jsonl` | `81b616cf8bcc0d82ed0c01845732348e46590a69a274403cae099e93cee4dad3` |
| `thach_thuc_phuong_ngu_phat_trien.jsonl` | `9fc6bca793ce7a38cc45d2d4ddfee201e4b119a546312c0e69ded3c790db5f85` |
| `thach_thuc_tra_loi_ngan_phat_trien.jsonl` | `238740f49263155e4901a5f998a3042e1283bd12d384fbcbbe9a0506d6dcd243` |

Hai bộ mới:

- `tra_loi_ngan`: mỗi ca có ít nhất 3 cặp "Bác sĩ: Có phải … không ạ?" / người bệnh đáp ≤ 3 chữ. Nội dung nằm
  trong câu hỏi; mệnh đề đáp án dẫn tới cả hai lượt. Cặp được **dựng** bằng cách viết lại một cặp hỏi–đáp có sẵn,
  vì bộ sinh gần như không tự tạo cặp kiểu này (≤ 1 cặp/ca ở 15/191 ca thử).
- `khong_dau_cau`: cặp A/B; B bỏ dấu câu, viết thường, chèn "ờ/à/ừm" và lặp từ đầu ở khoảng nửa số lượt.

## Chỉ số chính

Đo trên đầu ra của mô hình (Giai đoạn 5) bằng `python -m src.do_canh_bao --thu-muc data/thach_thuc_v2`.
Mọi số ghi "so với bộ chấm tự động", trừ chỉ số 4.

1. **Tỉ lệ lỗi nguy hiểm lọt vào thân** (dị ứng, thuốc, chẩn đoán), chính sách đang dùng.
2. **Tỉ lệ chặn thừa** (phát biểu không lỗi bị đưa sang cần xác nhận).
3. **Precision và độ phủ của cảnh báo bỏ sót** (khối `bo_sot` trong kết quả đo).
4. **Precision cảnh báo so với nhãn người** trên 40 ca của Task 1.2 — chỉ báo khi tập nhãn người đã có.

Chỉ số phụ: độ bất biến dấu câu (Task 3.2) = tỉ lệ mã cảnh báo trùng nhau giữa A và B của `khong_dau_cau`.

## Ngưỡng thành công (đổi chính sách mặc định chỉ khi đạt CẢ HAI)

- Lỗi nguy hiểm lọt giảm **≥ 10 điểm phần trăm** so với chính sách C chạy bằng luật cũ trên cùng đầu ra.
- Chặn thừa **≤ 10%**.

Thêm hai điều kiện cho từng luật mới:

- Một mã cảnh báo mới chỉ đổi từ `thu_nghiem` sang `on_dinh` khi precision cùng loại **≥ 0,5** trên tập này.
- Độ bất biến dấu câu **≥ 0,85**.

Không đạt thì giữ chính sách C và ghi kết quả âm vào báo cáo, không tìm ngưỡng khác cho tới khi đạt.

## Giới hạn đã biết

- Bộ chấm tự động thổi phồng `khong_can_cu` (ngưỡng ghép 0,6), nên precision nhóm UNSUPPORTED thấp giả.
- Hai bộ mới là văn bản dựng bằng luật, không phải lời nói thật. Câu hỏi dựng đôi khi gượng (đổi "tôi" → "mình").
- Tập này nhỏ (240 ca, 46 khuôn); khoảng tin cậy rộng. Báo kèm khoảng Wilson 95%.

## Sửa đổi sau khi đăng ký

**25/11/2026 — bỏ chỉ số 4 (precision so với nhãn người).** Lý do: không có người gán nhãn kịp hạn. Sửa đổi này
viết **trước** khi chạy bất kỳ luật hay mô hình nào trên `data/thach_thuc_v2/`. Hệ quả:

- Mọi precision của cảnh báo chỉ báo "so với bộ chấm tự động". Không được viết "độ chính xác thực tế" hay
  "đã kiểm chứng" cho cảnh báo nào.
- Không dùng mô hình ngôn ngữ thương mại để gán nhãn thay người: đề tài cấm mô hình thương mại ở mọi khâu.
- Hạn chế phải ghi trong báo cáo: bộ chấm không gán nhãn câu âm tính chung ("Dạ, không có gì ạ" khi hỏi tiền
  sử, thuốc), nên precision các mã bỏ sót có tên bị thấp giả (đo 25/11 trên bộ cũ: 0).
- Ngưỡng thành công ở mục trên không đổi; chúng vốn đo so với bộ chấm.

**25/11/2026 — thêm phép đo cấy lỗi (thay phần đo của chỉ số 4).** Viết trước khi chạy phép đo này trên bất kỳ
tập nào. Plan: `docs/superpowers/plans/2026-11-25-cay-loi-do-canh-bao.md`.

- Cách đo: lấy đáp án làm bản ghi hoàn hảo, cấy **đúng một** lỗi đã biết loại và vị trí (16 loại: đổi chủ thể,
  đảo phủ định, nâng chắc chắn, giả định thành thật, bản cũ còn hiệu lực, đổi liều, đổi số, đổi thuốc, đổi thời
  gian, bịa mệnh đề, bịa trích dẫn, dời bằng chứng, xoá dị ứng/thuốc/phủ định/số liệu). Mọi số ghi "trên lỗi cấy
  nhân tạo".
- Tập điều chỉnh (được nhìn, được sửa luật): 400 ca rút từ `data/viet_train_v2.jsonl`
  (SHA-256 `7cf412c24e1feb29516a82ba93c6947ed745bcc6cdf0da9ca6aa59056ac3d7b0`), hạt 42; danh sách id ở
  `data/cay_loi/tap_dieu_chinh_ids.json` (SHA-256 `74fd58652b73b0743241d96d4312fa72e64958d2d04177ec7b8aa70bffa0648b`).
- Tập giữ kín: đáp án 240 ca của `data/thach_thuc_v2/` (SHA-256 ở bảng đầu tệp). Chạy **đúng một lần**, sau khi
  khoá luật. Chạy này chỉ đọc đáp án, không đọc đầu ra mô hình, nên không ảnh hưởng phép đo Giai đoạn 5.
- Chỉ số: độ nhạy theo loại lỗi (kèm Wilson 95%), báo nhầm/ca trên bản sạch theo mã, precision theo mã trong
  lượt cấy, tỉ lệ mệnh đề bị cấy rơi vào "cần xác nhận" theo chính sách D.
- Ngưỡng nâng một mã `thu_nghiem` lên `on_dinh` (đo trên tập giữ kín): độ nhạy loại đích ≥ 0,5 **và**
  precision trong lượt cấy ≥ 0,5 **và** báo nhầm ≤ 0,05 cảnh báo/ca sạch. Chỉ ghi khuyến nghị; đổi thật cần
  người dùng đồng ý.
- Tiêu chí giữ một vòng sửa luật (đo trên tập điều chỉnh): độ nhạy trung bình các loại tăng, báo nhầm/ca sạch
  tăng không quá 0,02, lọt nguy hiểm trên `data/thach_thuc` không tăng, Jaccard bất biến dấu câu ≥ 0,85.
  Tối đa 5 vòng; không đạt thì hoàn tác vòng đó.
- Giới hạn phải ghi trong báo cáo: lỗi cấy "sạch" hơn lỗi mô hình mắc thật; đáp án coi là đúng tuyệt đối nên
  cảnh báo trên bản sạch về câu âm tính chung bị tính báo nhầm dù có thể hợp lý.
