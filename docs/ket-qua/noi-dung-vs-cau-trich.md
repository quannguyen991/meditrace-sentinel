# Kiểm nội dung mệnh đề với câu trích của nó (đo khô, CPU)

Chạy: `python tools/do_noi_dung_trich.py --ra docs/ket-qua/noi-dung-vs-cau-trich.md`. Nguồn: `data/thach_thuc/ra_C_khoa_*_phat_trien.jsonl` + đáp án `thach_thuc_*_phat_trien.jsonl`, chấm bằng `cham_he_thong.loi_phat_bieu` (mệnh đề vào thân hồ sơ, bỏ bản lặp). Module: `src/duong_ong/b4_kiem_noi_dung_trich.py`, **chưa nối vào đường ống**, không đổi số đã báo.

Ba nhóm mệnh đề (theo bộ chấm): **không ghép** = không ứng với đáp án nào (nội dung lệch, hay thông tin bịa); **ghép nhưng lỗi** = ghép được nhưng sai chủ thể/mức/thuốc/thời gian; **đúng** = ghép được, không lỗi.

## (a)/(b) Tỉ lệ cờ theo nhóm

| Bộ | Không ghép: n | cờ | Ghép nhưng lỗi: n | cờ | Đúng: n | cờ (báo giả) |
|---|---:|---:|---:|---:|---:|---:|
| dinh_chinh | 11 | 3 (27.3%) | 39 | 18 (46.2%) | 410 | 84 (20.5%) |
| doi_chu_the | 23 | 4 (17.4%) | 134 | 40 (29.9%) | 466 | 66 (14.2%) |
| nhieu_asr | 136 | 113 (83.1%) | 72 | 45 (62.5%) | 390 | 136 (34.9%) |
| phuong_ngu | 20 | 8 (40.0%) | 50 | 28 (56.0%) | 578 | 113 (19.6%) |
| **Tổng** | 190 | 128 (67.4%) | 295 | 131 (44.4%) | 1844 | 399 (21.6%) |

## Theo mã lý do (số mệnh đề mang mã; một mệnh đề có thể mang nhiều mã)

| Bộ | Mã | Không ghép | Ghép nhưng lỗi | Đúng (báo giả) |
|---|---|---:|---:|---:|
| dinh_chinh | `tu_khong_co_trong_trich` | 3 | 16 | 51 |
| dinh_chinh | `chep_loi_asr` | 0 | 0 | 11 |
| dinh_chinh | `bo_mat_bo_nghia` | 0 | 2 | 24 |
| dinh_chinh | `nhan_khac_trich` | 2 | 5 | 24 |
| doi_chu_the | `tu_khong_co_trong_trich` | 4 | 24 | 44 |
| doi_chu_the | `chep_loi_asr` | 0 | 6 | 4 |
| doi_chu_the | `bo_mat_bo_nghia` | 0 | 11 | 23 |
| doi_chu_the | `nhan_khac_trich` | 2 | 12 | 14 |
| nhieu_asr | `tu_khong_co_trong_trich` | 53 | 27 | 67 |
| nhieu_asr | `chep_loi_asr` | 59 | 6 | 52 |
| nhieu_asr | `bo_mat_bo_nghia` | 4 | 12 | 20 |
| nhieu_asr | `nhan_khac_trich` | 33 | 7 | 25 |
| phuong_ngu | `tu_khong_co_trong_trich` | 8 | 25 | 74 |
| phuong_ngu | `chep_loi_asr` | 0 | 0 | 14 |
| phuong_ngu | `bo_mat_bo_nghia` | 0 | 3 | 31 |
| phuong_ngu | `nhan_khac_trich` | 4 | 12 | 26 |
| **Tổng** | `tu_khong_co_trong_trich` | 68 | 92 | 236 |
| **Tổng** | `chep_loi_asr` | 59 | 12 | 81 |
| **Tổng** | `bo_mat_bo_nghia` | 4 | 28 | 98 |
| **Tổng** | `nhan_khac_trich` | 41 | 36 | 89 |

Mệnh đề không có câu trích bị bỏ khỏi bảng: 0.

## Đọc số

Kiểm này cờ 128/190 mệnh đề bộ chấm không ghép được với đáp án (67.4%), nhiều nhất ở bộ nhiễu ASR, nơi lỗi chủ yếu là chép chữ không dấu và đổi chữ. Nó cũng cờ 131/295 mệnh đề ghép được nhưng sai ở trục khác (44.4%), đó là lỗi nó không nhắm tới nên chỉ coi là trùng hợp. Cái giá là 399/1844 mệnh đề đúng cũng bị cờ (21.6%), phần lớn do mô hình diễn đạt lại hợp lệ ("chán ăn" cho "không chịu ăn"), nội dung ngắn hơn câu trích có kèm liều thuốc, hoặc chữ không dấu vốn là từ đúng. Mức báo giả này quá cao để chặn hay sửa tự động, chỉ hợp để xếp thứ tự cho bác sĩ xem lại. Giới hạn: chỉ 4 bộ phát triển do máy sinh (đáp án và nhiễu ASR đều tổng hợp), ngưỡng 50% và danh sách chữ miễn trừ chọn tay, từ điển chữ không dấu lập từ ba bộ sạch của cùng bộ sinh nên số ở bộ nhiễu ASR có phần lạc quan, và chưa nối vào đường ống nên chưa đổi số nào đã báo.
