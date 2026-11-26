# Mốc 0 — lớp cảnh báo trên 4 bộ thử thách (25/11/2026)

**So với bộ chấm tự động** (`cham_he_thong` phiên bản 2026-09-22), **không phải nhãn người**.
Tập: 4 bộ thử thách phát triển (`data/thach_thuc/`, đầu ra nhánh `C_khoa` của mô hình thế hệ 8, tháng 9).
Đây là tập đã nhìn khi viết luật, nên số ở đây thiên lạc quan.

Lệnh:

```
python -m src.do_canh_bao --ra-json docs/ket-qua/canh-bao-moc-0.json
```

Phiên bản lớp cảnh báo: `canh-bao-2026-09-24b`. Số phát biểu còn hiệu lực: 2.789.

## Chính sách C (đang dùng) và D

| | C | D |
|---|---|---|
| Phát biểu có lỗi | 765 | 765 |
| Lọt vào thân (mọi lỗi) | 485 (63,4%) | 477 (62,4%) |
| Lỗi nguy hiểm (dị ứng, thuốc, chẩn đoán) | 217 | 217 |
| **Lỗi nguy hiểm lọt** | **98 (45,2%)** | **94 (43,3%)** |
| **Chặn thừa** (không lỗi mà bị đưa sang cần xác nhận) | **161 (8,0%)** | **123 (6,1%)** |

So với số 24/09 (C 44,7% / 8,1%; D 43,3% / 6,2%): D khớp. C lệch đúng 1 phát biểu nguy hiểm
(97 → 98 trên 217). Trạng thái C lấy từ tệp đầu ra đã đóng băng, nên chênh lệch đến từ phần
phân loại `cong_rui_ro.loai_thong_tin` hoặc bộ chấm đã sửa sau 24/09; chưa truy tới phát biểu cụ thể.

## Bỏ sót

| | |
|---|---|
| Mệnh đề đáp án bị sót | 200 |
| Có cảnh báo toàn ca chạm đúng lượt | 25 (độ phủ 12,5%) |
| Cảnh báo toàn ca | 887 |
| Cảnh báo trúng lượt bị sót | 25 (precision 2,8%) |

Đây là chỗ yếu nhất: cứ 8 mệnh đề bị sót thì 7 không có cảnh báo nào, và 97% cảnh báo bỏ sót là báo nhầm.

## 10 mã có precision cùng loại thấp nhất (báo ≥ 5 lần)

| Mã | Báo | Precision cùng loại | Có lỗi bất kỳ | Tin cậy |
|---|---|---|---|---|
| IMPORTANT_MODIFIER_DROPPED | 84 | 0,000 | 0,179 | thu_nghiem |
| FAMILY_PATIENT_MIXUP | 50 | 0,000 | 0,280 | on_dinh |
| DOCTOR_STATEMENT_AS_PATIENT_FACT | 6 | 0,000 | 0,833 | thu_nghiem |
| DUPLICATE_INFORMATION | 108 | 0,056 | 0,704 | on_dinh |
| SPEAKER_SUBJECT_MISMATCH | 382 | 0,058 | 0,440 | on_dinh |
| EVIDENCE_CONTEXT_MISSING | 7 | 0,143 | 0,429 | on_dinh |
| FABRICATED_QUOTE | 17 | 0,176 | 0,412 | on_dinh |
| UNSUPPORTED_INFORMATION | 253 | 0,289 | 0,518 | on_dinh |
| POSSIBLE_NEGATION_ERROR | 69 | 0,319 | 0,406 | on_dinh |
| PAST_CURRENT_CONFUSION | 24 | 0,333 | 0,458 | on_dinh |

Hai mã `FAMILY_PATIENT_MIXUP` và `SPEAKER_SUBJECT_MISMATCH` đang gắn nhãn `on_dinh` mà precision cùng loại dưới 0,06.
`SPEAKER_SUBJECT_MISMATCH` vẫn đáng giữ vì bỏ nó làm lỗi nguy hiểm lọt tăng từ 44,7% lên 55,3% (đo 24/09):
nó bắt lỗi thật nhưng sai loại. Cần ghi đúng điều này khi báo cáo thay vì gọi là "ổn định".

## Lỗi bộ chấm thấy mà lớp cảnh báo bắt kém nhất

| Mã lỗi bộ chấm | Số lỗi | Có cảnh báo cùng loại | Có cảnh báo bất kỳ |
|---|---|---|---|
| sai_thoi_gian | 19 | 5,3% | 36,8% |
| sai_thuoc | 109 | 11,0% | 58,7% |
| sai_muc_tinh_huong | 5 | 20,0% | 40,0% |
| sai_muc | 87 | 21,8% | 88,5% |
| khong_can_cu | 235 | 33,6% | 52,8% |
| sai_muc_phu_dinh | 52 | 50,0% | 86,5% |
| sai_chu_the | 218 | 64,2% | 72,5% |
| ban_cu | 160 | 81,9% | 99,4% |
| sai_muc_chac_chan | 33 | 87,9% | 97,0% |

Bộ chấm chỉ có 9 mã lỗi nên bảng có 9 dòng, không đủ 10.
`sai_thuoc` (109 lỗi, nhóm nguy hiểm) chỉ có 11% cảnh báo đúng loại; đây là mục tiêu của Giai đoạn 4.

## Sau các bước sửa

| Bước | Cảnh báo bỏ sót | Độ phủ | Precision | Lọt nguy hiểm C / D | Chặn thừa C / D |
|---|---|---|---|---|---|
| Mốc 0 | 887 | 12,5% | 2,8% | 45,2% / 43,3% | 8,0% / 6,1% |
| Sau 2.1 (một bộ bỏ sót, nhiều mã mỗi đoạn, sửa che dị ứng) | 864 | 12,5% | 2,9% | không đổi | không đổi |
| Sau 2.2 (+ `OMITTED_ANSWER`, thử nghiệm) | 958 | 12,5% | 2,6% | không đổi | không đổi |
| 2.3, `nguong_phu = 0,3` | 980 | 14,5% | 3,0% | không đổi | không đổi |
| 2.3, `nguong_phu = 0,5` | 985 | 15,5% | 3,1% | không đổi | không đổi |
| 2.3, `nguong_phu = 0,7` | 997 | 16,5% | 3,3% | không đổi | không đổi |
| Sau 3.1 (lượt không dấu đi qua `loi_noi`; mặc định `nguong_phu = None`) | 844 | 12,0% | 2,8% | không đổi | không đổi |
| Sau rà soát độc lập (9 lỗi nặng đã sửa, xem dưới) | 890 | 12,0% | 2,7% | 45,2% / 43,3% | 8,0% / 6,1% |
| Sau 5 vòng cấy lỗi (xem `cay-loi.md`) | 845 | 12,0% | 2,8% | 45,2% / 43,3% | 8,0% / 6,1% |
| Sau vòng 6 (4 điểm mù lỗi khó, 26/11) | — | — | — | 45,2% / 42,9% (C 98, D 93) | 8,0% / 6,1% |

Sau 2.1 gần như không đổi. Lý do: bộ phân loại chỉ chạy trên các đoạn mà `doan_chua_ghi` coi là chưa ghi,
và các đoạn đó chỉ chạm lượt của 25/200 mệnh đề bị sót. Nút thắt nằm ở khâu tìm đoạn (2.2, 2.3), không ở khâu
phân loại. Lỗi che dị ứng vẫn là lỗi thật (có phép thử ghim), nhưng trên bộ này không ca nào rơi vào.

### Vì sao bỏ sót gần như không nhúc nhích (chẩn đoán 25/11)

- **172/200 mệnh đề bị sót (86%) nằm trong lượt mà mô hình đã dẫn cho một mệnh đề khác.** Tiêu chí cũ
  "chung một từ nội dung là đã ghi" che chúng. Một phần không phải bỏ sót thật mà là giới hạn ghép của bộ chấm
  (đáp án "đau họng nhẹ", lời nói "rát cổ nhẹ", mô hình ghi "rát cổ").
- **Mọi mã bỏ sót có tên đều có precision 0 so với bộ chấm**; mọi lần trúng đến từ `POSSIBLE_IMPORTANT_OMISSION`
  (precision 3,0–3,8%). Với `OMITTED_ANSWER` (94 lần báo), nguyên nhân là **đáp án của bộ sinh không gán nhãn
  câu âm tính chung**: "Có đang điều trị bệnh gì không?" / "Dạ, không có gì ạ." không có mệnh đề đáp án nào.
  Về lâm sàng đó là thông tin âm tính đáng ghi, nên số 0 ở đây đo chỗ hổng nhãn, không đo chất lượng luật.
  Cần tập nhãn người (Task 1.2) và bộ `tra_loi_ngan` mới (có nhãn cho câu trả lời ngắn) để đo đúng.

### Quyết định 2.3

Đăng ký trong plan: chọn mức `nguong_phu` có precision `POSSIBLE_IMPORTANT_OMISSION` ≥ 0,15. **Không mức nào đạt**
(cao nhất 0,038 ở 0,7). Theo đăng ký: giữ mã này ẩn với bác sĩ, giữ mặc định `NGUONG_PHU_MAC_DINH = None` (tiêu chí
cũ). Ngưỡng 0,7 tăng độ phủ từ 12,5% lên 16,5% nhưng chỉ bằng thêm cảnh báo ẩn; sẽ đo lại trên bộ v2 ở Giai đoạn 5.

## Bất biến dấu câu (Task 3.2)

`python -m tools.do_bat_bien_dau_cau` — chạy lớp cảnh báo trên hội thoại gốc và trên bản bỏ dấu câu, viết thường
(mệnh đề và trích dẫn chuẩn hoá cùng cách), so tập (mã, phát biểu) và (mã, lượt). 300 ca.

| | Giữ nguyên (một chiều) | Jaccard (tính cả cảnh báo sinh thêm) | Cảnh báo sinh thêm khi bỏ dấu |
|---|---|---|---|
| Trước 3.1 | 0,973 | **0,675** | 1.042 (761 bỏ sót chung, 141 thuốc, 140 dị ứng) |
| Sau 3.1 | 0,931 | **0,882** | 124 (122 bỏ sót chung) |
| Sau rà soát | 0,976 | **0,888** | 228 (226 bỏ sót chung, ẩn với bác sĩ) |

Chỉ số một chiều trong plan (giữ nguyên ≥ 0,85) che mất vấn đề chính: khi bỏ dấu, câu hỏi "chị có dị ứng thuốc gì
không" bị coi là đoạn chưa ghi và sinh cảnh báo bỏ sót dị ứng giả. Vì vậy dùng Jaccard làm chỉ số chính; mục tiêu
≥ 0,85 đạt sau 3.1. Phần còn lệch gần hết là `POSSIBLE_IMPORTANT_OMISSION` (mã ẩn với bác sĩ), do cách tách đoạn khác nhau.

## Rà soát độc lập (25/11, sau Giai đoạn 4)

Một người rà soát mới (không tham gia viết mã) tìm ra 14 điểm. 9 điểm nặng đã sửa, mỗi điểm có một phép thử trượt
trước khi sửa (`tests/test_ra_soat_cuoi.py`):

1. Dị ứng dạng "sốc phản vệ / mẫn cảm / nổi mề đay" bị che bởi bất kỳ dị ứng nào đã ghi.
2. "không dị ứng penicillin **nhưng** dị ứng aspirin" bị che hoàn toàn.
3. Văn bản **có** dấu câu mất `PLAN_AS_FACT` (kiểm câu hỏi trên vế đã bị bóc dấu) — chính sách D đổi. Đã trả về hành vi cũ.
4. Lời kể không dấu của người bệnh ("mấy hôm nay cháu ho", "ăn gì cũng nôn") bị coi là câu hỏi và bỏ qua.
5. Dị ứng của mẹ che dị ứng của cháu; đoạn nói về người nhà không ghi rõ.
6. "dị ứng penicillin **và** aspirin" báo aspirin là thuốc bị sót.
7. Trọng tâm 3 (“không dị ứng thức ăn, dị ứng penicillin”) hỏng khi đi qua `doan_chua_ghi`: tên thuốc mới giờ luôn làm đoạn là chưa ghi.
8. Tra liều bằng chuỗi con trên 114 tên: "kháng sinh" khớp "inh" (isoniazid). NTI mở rộng sang biệt dược làm đổi mức nguy cơ của chính sách C trên dữ liệu mới — đã thu về đúng danh sách cũ + acenocoumarol.
9. Chống chỉ định dựa trên ánh xạ chưa duyệt từng ở mức "nghi rủi ro"; giờ là "cần xem".

Năm điểm nhẹ để sau: liều theo số viên / dạng siro / thuốc dùng theo tuần; "amlodipin" và "amlodipine" so theo tên chứ
không theo hoạt chất trong `bo_sot`; `OMITTED_ANSWER` báo cả khi mệnh đề dẫn lượt hỏi; "không sốt không ho" chỉ bắt phủ
định đầu; bảng trẻ em gán thuốc phối hợp vào một hoạt chất, `aho_corasick` vẫn liệt kê sintrom dưới warfarin.
