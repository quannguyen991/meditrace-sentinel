# DPO trên cặp lỗi khó — v3 so với v3 + DPO (26/11/2026)

Huấn luyện thêm adapter v3 bằng DPO (`src/huan_luyen/huan_luyen_dpo.py`, β = 0,1, cộng NLL câu đúng α = 1, lr 2e-5, 51 bước × 8 cặp) trên **407 cặp** lỗi khó sinh từ dữ liệu train. Mô hình tham chiếu là v3.

Đo trên **140 cặp kiểm tra** sinh từ `viet_phat_trien_v2` (tách khỏi dữ liệu train), cùng một tập cho cả hai bản.

| Chỉ số | v3 | v3 + DPO |
|---|---|---|
| Chọn đúng câu đúng | 140/140 | 140/140 |
| Chênh log-prob trung bình (câu đúng − câu sai) | 20,5 | **45,1** |
| Log-prob trung bình của câu đúng | −1,38 | −4,90 |

Theo loại lỗi (chênh log-prob trung bình, số cặp):

| Loại lỗi | Số cặp | v3 | v3 + DPO |
|---|---|---|---|
| Bịa phủ định | 9 | 50,1 | 149,0 |
| Thuốc gần giống tên | 11 | 36,9 | 60,0 |
| Bỏ điều kiện | 4 | 11,4 | 54,2 |
| Bỏ từ nghi ngờ | 12 | 10,5 | 41,7 |
| Nhầm quá khứ/hiện tại | 14 | 21,2 | 38,6 |
| Số lệch nhỏ | 10 | 19,2 | 37,7 |
| Đổi bên | 10 | 19,8 | 37,4 |
| Đổi mức độ | 11 | 21,0 | 34,6 |
| Phủ định trong chuỗi | 1 | 13,7 | 33,8 |
| Đổi đơn vị thời gian | 17 | 19,1 | 33,8 |
| Người nhà thành bệnh nhân | 17 | 11,5 | 33,6 |
| Gán nhầm lượt nói | 13 | 15,3 | 33,5 |
| Đổi tần suất | 11 | 17,0 | 27,9 |

## Đọc kết quả

- Tỉ lệ chọn đúng đã bão hòa ở v3 (100%), nên không phân biệt được hai bản. Chỉ số so sánh là độ chênh log-prob.
- DPO tách câu đúng khỏi câu sai xa hơn ở **cả 13 loại** (chênh trung bình gấp khoảng 2,2 lần).
- Nhưng log-prob của chính câu đúng **giảm** từ −1,38 xuống −4,90: mô hình đẩy câu sai xuống mạnh hơn, đồng thời cũng hạ xác suất câu đúng. Đây là hiện tượng đã biết của DPO và có thể làm chất lượng sinh văn bản kém đi.
- **Chưa đo bỏ sót** trên ca đầy đủ cho bản DPO (thiếu thời gian). Vì vậy chưa thay v3 bằng bản DPO trong hệ thống; bản DPO chỉ là kết quả thử nghiệm.

Tệp gốc: `models/nen-qwen3-4b-trich-v3-dpo/danh_gia_dpo.json` và `danh_gia_v3_chenh.json` trên máy huấn luyện.
