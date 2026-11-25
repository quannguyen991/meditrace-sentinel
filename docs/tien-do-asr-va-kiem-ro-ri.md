# Tiến độ ASR và kiểm rò rỉ dữ liệu (theo KE_HOACH_NANG_CAP_TOAN_DIEN v1.3)

Cập nhật: 18/11/2026. Số liệu lấy từ các tệp trong `data-rieng-tu/ket-qua/` (không nằm trong repo).

## 1. Kết quả đo (PhoWhisper-medium)

| Tập | Mô hình | WER | Tỷ lệ thuật ngữ Anh nhận đúng | AUROC dự đoán câu sai (WER≥0,2) |
|---|---|---|---|---|
| VietMed-test (3.437 câu) | gốc | 0,2369 | — | 0,7527 |
| VietMed-test | LoRA trên VietMed-train | 0,2041 | — | 0,7839 |
| ViMedCSS-test-shard0 (323 câu) | gốc | 0,3336 | 0,1734 | 0,757 |
| ViMedCSS-test-shard0 | LoRA trên VietMed-train | 0,2606 | 0,2345 | 0,8213 |

Số liệu trên dùng giải mã greedy. Thử nghiệm beam search (beam=5) trên 500 câu VietMed và 323 câu ViMedCSS: đang chạy, chưa có kết quả khi viết báo cáo này.

Ghi chú về chỉ số: khi bỏ các từ đệm (à, ừ, ờ, ạ, thì, là, cái, mà, nó, đó, ấy, kiểu, thế) khỏi cả tham chiếu và giả thuyết, WER VietMed của mô hình LoRA chỉ đổi từ 0,2041 xuống 0,2016. Vì vậy số lượng lớn lỗi thêm/bớt từ đệm không phải nguyên nhân chính của WER. Lỗi nguy hiểm nhất là thuật ngữ bị phiên âm sai (ví dụ `implant→imlan`, `candida→canada`, `inulin→insulin`, `estrogen→gen`).

## 2. Kiểm rò rỉ giữa các tập

Chạy bằng [kiem_ro_ri_va_manifest.py](../thi-nghiem/asr/kiem_ro_ri_va_manifest.py). Báo cáo đầy đủ: `data-rieng-tu/ket-qua/kiem-ro-ri/bao-cao-ro-ri.json`.

| Kiểm tra | Kết quả |
|---|---|
| VietMed: người nói/phiên chung train–test | 0 |
| VietMed: người nói/phiên chung dev–test | 1 (trong 14 phiên của test) |
| VietMed: âm thanh trùng (SHA-256) train–test, dev–test | 0, 0 |
| VietMed: câu test trùng nội dung với train | 0 / 3.437 |
| ViMedCSS: video gốc chung train–test | 898 video; 93,8% dòng test có video nằm trong train |
| ViMedCSS: segment_id chung train–test | 2 |
| ViMedCSS: câu test trùng nội dung với train | 44 / 1.614 |

Kết luận:
- Kết quả trên ViMedCSS-test của mô hình huấn luyện trên VietMed **không bị rò rỉ**, vì VietMed và ViMedCSS không chung video hay câu.
- Không được huấn luyện thêm trên ViMedCSS-train rồi báo cáo trên ViMedCSS-test nếu chưa loại bỏ các video trùng.
- Dev và test VietMed có một phiên chung. Cần ghi chú khi báo cáo số dev.

## 3. Manifest

`data-rieng-tu/ket-qua/kiem-ro-ri/manifest.json` (không nằm trong repo) chứa cho từng mẫu VietMed: ID, người nói/phiên, tham chiếu và SHA-256 của âm thanh; cùng SHA-256 của `test_set.csv` và `train_set.csv` của ViMedCSS. Bản sao dữ liệu đã được chuyển sang `E:\MediTraceData\data-rieng-tu\` trên máy HoaiĐức và xác minh bằng SHA-256 khớp với bản gốc.

## 4. Trạng thái theo giai đoạn

| Giai đoạn | Trạng thái | Ghi chú |
|---|---|---|
| 0. Baseline | Một phần | Có số liệu ASR. Chưa đóng băng commit: kho còn nhiều thay đổi chưa commit. |
| 1. Đánh giá độc lập | Một phần | Có báo cáo rò rỉ và manifest ASR. Chưa có taxonomy lỗi có nhãn người thẩm định. |
| 1B. Mở rộng dữ liệu | Chưa làm | Chờ bác sĩ duyệt khuôn mới. |
| 2. Nghe lại đúng đoạn | Chưa xác minh | Không thuộc phạm vi phiên này. |
| 2B. Tra cứu có nguồn | Chưa thay đổi | |
| 3–4. Giảm bỏ sót, giao diện duyệt | Chưa làm | |
| 5. ASR và người nói | Đang làm | Có WER, thuật ngữ, AUROC, so sánh greedy/LoRA. Chưa có tỷ lệ lỗi lâm sàng chính thức, chưa so nhiều nhà cung cấp, chưa hiệu chuẩn độ tin cậy. |
| 6–7. Thư viện tài liệu, bảo mật, pilot | Chưa làm | |

## 5. Cổng P0

1. Baseline tái lập từ manifest: chưa đạt (cần đóng băng commit và cấu hình).
2. Tập kiểm thử khóa và báo cáo rò rỉ: đã có báo cáo ASR; chưa có cho các tập khác của dự án.
3. Dữ liệu demo nhận diện rõ: chưa kiểm tra trong phiên này.
4. Data-flow và provider ngoài: chưa rà soát trong phiên này.
5. Taxonomy lỗi nghiêm trọng và đường đưa về bác sĩ: chưa đạt.

## 5b. So sánh có khoảng tin cậy (paired bootstrap theo câu, 2.000 lần)

Chạy bằng [so_sanh_bootstrap.py](../thi-nghiem/asr/so_sanh_bootstrap.py). Hiệu WER = B − A (âm là B tốt hơn).

| So sánh | Tập | WER A → B | Hiệu [95% CI] |
|---|---|---|---|
| Gốc → LoRA | VietMed-test (3.437) | 0,2369 → 0,2041 | −0,033 [−0,041; −0,027] |
| Greedy → beam 5 | VietMed-test (500 đầu) | 0,2923 → 0,2758 | −0,016 [−0,022; −0,011] |
| Gốc → LoRA | ViMedCSS-shard0 (323) | 0,3336 → 0,2606 | −0,073 [−0,159; −0,012] |
| Greedy → beam 5 | ViMedCSS-shard0 (323) | 0,2606 → 0,2609 | +0,000 [−0,009; +0,010] |

Lưu ý: bootstrap theo câu bỏ qua việc các câu cùng video/phiên, nên khoảng tin cậy có thể hẹp hơn thực tế, đặc biệt với ViMedCSS.

Kết luận beam 5: cải thiện VietMed-500 nhưng không cải thiện ViMedCSS (khoảng tin cậy chứa 0). Thuật ngữ Anh giảm nhẹ (0,2345 → 0,2299). Chưa đủ bằng chứng để đổi mặc định; giữ greedy.

## 6. Giấy phép và phạm vi sử dụng

[nguon-va-giay-phep.md](nguon-va-giay-phep.md): dữ liệu huấn luyện từ bên ngoài chỉ dùng cho thí nghiệm nhận dạng, không dùng để sinh bệnh án. Mô hình LoRA chưa được triển khai lên bản demo.
