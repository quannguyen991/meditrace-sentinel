# Ước lượng số mệnh đề sót nằm trong vế được chọn (trên bảng sau xử lý; đo khô, CPU)

Chạy: `python tools/do_ve_chua_phu.py --ra docs/ket-qua/ve-chua-phu.md`. Nguồn: đầu ra đã lưu `data/thach_thuc/ra_C_khoa_*_phat_trien.jsonl` + đáp án `thach_thuc_*_phat_trien.jsonl` (4 bộ phát triển). **Chưa đo bằng mô hình**: đây là ước lượng số mệnh đề bị sót nằm trong vế mà quét lại sẽ chọn để hỏi lại, không phải số mô hình sẽ trích đúng, và **không phải cận trên**: (1) vế được chọn tính trên bảng mệnh đề SAU xử lý (thay cho đầu ra thô, không lưu trên máy này), nên vế chọn thật có thể khác; (2) bảng ghép đáp án theo `noi_dung`, nên mệnh đề quét lại có thể ghép được với đáp án ở chỗ khác. Từ 28/11 mệnh đề quét lại chỉ được giữ khi câu trích giao vế đã chọn (`loc_trong_van(..., ve=...)`).

Đáp án của bộ sinh ghi cùng một mệnh đề ở hai mục (cùng nội dung, cùng lượt): 367 bản trùng. Ghép một-một đếm bản trùng là bỏ sót dù mô hình đã ghi (chưa bỏ trùng: 517 sót), nên các bảng dưới tính trên đáp án ĐÃ bỏ trùng.

## Mệnh đề bị sót nằm ở đâu

| Bộ | Ca | Mệnh đề đáp án | Bị sót | Sót ở lượt đã dẫn | Trong vế được chọn (ước lượng) | Vế chưa phủ, không tín hiệu | Vế đã phủ | Ngoài vế | Không định vị |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| dinh_chinh | 60 | 551 | 14 | 13 (92.9%) | **1 (7.1%)** | 1 | 12 | 0 | 0 |
| doi_chu_the | 80 | 772 | 28 | 27 (96.4%) | **0 (0.0%)** | 9 | 19 | 0 | 0 |
| nhieu_asr | 80 | 684 | 141 | 136 (96.5%) | **2 (1.4%)** | 4 | 132 | 1 | 2 |
| phuong_ngu | 80 | 716 | 22 | 19 (86.4%) | **1 (4.5%)** | 6 | 15 | 0 | 0 |
| **Tổng** | 300 | 2723 | 205 | 195 (95.1%) | **4 (2.0%)** | 20 | 178 | 1 | 2 |

## Chi phí

| Bộ | Ca có ≥ 1 vế chưa phủ (= số lần sinh thêm) | Vế chưa phủ | Vế/ca | Vế chứa ≥ 1 mệnh đề sót |
|---|---:|---:|---:|---:|
| dinh_chinh | 26/60 (43.3%) | 29 | 0.48 | 1 (3.4%) |
| doi_chu_the | 27/80 (33.8%) | 33 | 0.41 | 0 (0.0%) |
| nhieu_asr | 29/80 (36.2%) | 33 | 0.41 | 2 (6.1%) |
| phuong_ngu | 22/80 (27.5%) | 22 | 0.28 | 1 (4.5%) |
| **Tổng** | 104/300 (34.7%) | 117 | 0.39 | 4 (3.4%) |

## Đọc số

- Ước lượng: 4/205 mệnh đề sót (2.0%) nằm trong một vế được chọn để hỏi lại (trên bảng sau xử lý). Nếu mô hình trích đúng hết chỗ đó, tỉ lệ sót trên bộ này giảm từ 7.5% xuống khoảng 7.4%.
- 178/205 mệnh đề sót (86.8%) nằm ở vế ĐÃ có câu trích phủ: mô hình dẫn đúng chỗ nhưng `noi_dung` không ghép được với đáp án. Đọc mẫu: chép theo chính tả sai của ASR ("the trang beo", "beo phi do một"), đổi chữ ("ngột mũi" thay "nghẹt mũi", "nóng trong" thay "nóng hầm hập"), gắn nhãn sai lên đúng câu trích ("đau bụng" cho "đi ngoài toàn nước"), hoặc bỏ nửa sau của ý ("đau cơ" thay "đau cơ nặng hơn sau khi ăn"). Nghĩa là con số "86% sót nằm ở lượt đã có mệnh đề" chủ yếu là **ghi sai nội dung trên đúng vế**, không phải vế bị bỏ qua. Quét lại vế chưa phủ không nhắm vào nhóm này; muốn thu hồi phải kiểm `noi_dung` so với câu trích của chính nó (vd. vế có câu trích mà nội dung mệnh đề ít trùng từ).
- Hệ quả cho MT1 (≤ 8,0% từ 11,5%, đo trên `viet_phat_trien_v2`): theo ước lượng trên bộ này quét lại chỉ bớt khoảng 0,1 điểm phần trăm sót, nên quét lại đơn thuần khó đạt MT1. Đây là dự báo từ bộ khác và từ bảng sau xử lý, cần đo thật để kết luận.
- 20 mệnh đề sót nằm ở vế chưa phủ nhưng không có tín hiệu lâm sàng theo bộ từ khoá của `canh_bao.bo_sot` — muốn thu hồi phải nới bộ lọc tín hiệu (đổi chi phí lấy độ phủ).
- Bảng mệnh đề dùng ở đây là bảng SAU áp luật của nhánh C_khoa cộng các bản ghi bị `tu_json` loại; lượt trích thô không được lưu riêng trên máy này. Hai bảng có cùng câu trích nên độ phủ vế gần như nhau, nhưng không trùng tuyệt đối.
- Số thật (MT1, 30 ca `viet_phat_trien_v2`) phải chạy `chay_trung_gian(..., quet_lai=True)` trên GPU HoaiĐức: **chưa đo bằng mô hình**.
